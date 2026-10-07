#!/usr/bin/env python3
"""
API-free rehearsal of a proposer launch: stub client, sockets blocked.

Why this exists
---------------
``4_detect_mounds_batch.py --mode batch --dry-run`` is not API-free: it
creates a ``genai.Client`` and lists the served models before it reaches its
dry-run branch, and the real-time ``--dry-run`` with ``--use-cache`` creates a
billable context cache. A gate that forbids every API call (the modality
bridge's Stage 1 gate, ``planning/modality-bridge-2026-10-07.md`` § 6) needs
a rehearsal that runs the detector's own code with the exact launch
arguments and provably reaches no server. This harness provides it by:

1. blocking every socket connection and name lookup in the process, so any
   network attempt raises :class:`NetworkBlocked`;
2. replacing ``google.genai.Client`` with :class:`StubClient`, whose only
   capability is ``models.list()`` returning the pinned model name (so the
   detector's model resolution runs) — every other attribute raises; and
3. setting ``GOOGLE_API_KEY`` to a placeholder that is not a key (the
   detector refuses to start without one; the stub never sends it).

Batch mode (the default) runs the detector's ``__main__`` with the given
arguments plus ``--dry-run`` and wraps ``lib_batch_api.run_batch_unit`` to
record each chunk's plan (offset, tile count, model, cache use). With
``--full-build DIR`` it also builds every chunk's COMPLETE request file with
the real ``prepare_batch_unit`` and summarises it — line count, keys against
the manifest, the request with each tile image elided (one signature per
arm), system-instruction hash, generation config, example parts, tile-set
digest and file size — then deletes the file.

``--capture-realtime N`` instead runs the detector's REAL-TIME path (the
path every original leg ran) on the first N manifest tiles with a stub that
records each ``generate_content`` and ``caches.create`` request and raises,
so the real-time request can be compared field by field with the batch
request for the same tile (``--compare A.json B.json``).

Usage::

    python scripts/bridge_dryrun_harness.py --summary-json s.json \\
        [--full-build /scratch/dir] -- <4_detect_mounds_batch.py args>
    python scripts/bridge_dryrun_harness.py --summary-json r.json \\
        --capture-realtime 3 -- <args with --mode realtime --workers 1>
    python scripts/bridge_dryrun_harness.py --compare s.json r.json

Run from the repository root. Zero API calls by construction.

Created: 2026-10-07
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import runpy
import socket
import sys
import time
import types as pytypes
from pathlib import Path
from typing import Any

#: The placeholder the detector sees as its key. It is not a key.
PLACEHOLDER_KEY = "DRY-RUN-HARNESS-NOT-A-KEY"

#: The detector script, relative to the repository root.
DETECTOR = "scripts/4_detect_mounds_batch.py"

#: Placeholder cache name the real batch dry run uses (lib_batch_api).
DRY_RUN_CACHE = "cachedContents/DRY-RUN-PLACEHOLDER"


#: Every refused network operation or forbidden stub call, in order. The
#: detector catches some exceptions itself, so a breach is recorded here as
#: well as raised; a clean rehearsal leaves this empty.
BREACHES: list[str] = []


class NetworkBlocked(RuntimeError):
    """Raised by every socket entry point while the harness is installed."""

    def __init__(self, msg: str) -> None:
        """Record the breach, then build the exception.

        Args:
            msg: What was attempted.
        """
        BREACHES.append(f"network: {msg}")
        super().__init__(msg)


class StubCalled(RuntimeError):
    """Raised by a stub method that a rehearsal must never reach."""

    def __init__(self, msg: str) -> None:
        """Record the breach (except a capture's deliberate stop), then raise.

        Args:
            msg: What was called.
        """
        if msg != "captured":
            BREACHES.append(f"stub: {msg}")
        super().__init__(msg)


def _blocked(*_args: Any, **_kwargs: Any) -> None:
    """Refuse a network operation.

    Raises:
        NetworkBlocked: Always.
    """
    raise NetworkBlocked("network access attempted inside the API-free harness")


def block_network() -> None:
    """Make every outbound connection and DNS lookup in this process raise.

    Patches the socket module's connection and resolution entry points; the
    HTTP stacks the SDK uses (httpx, urllib3, aiohttp) all reach the network
    through these.
    """
    socket.socket.connect = _blocked  # type: ignore[method-assign]
    socket.socket.connect_ex = _blocked  # type: ignore[method-assign]
    socket.create_connection = _blocked  # type: ignore[assignment]
    socket.getaddrinfo = _blocked  # type: ignore[assignment]


class _Forbidden:
    """An attribute bag whose every attribute access raises."""

    def __init__(self, label: str) -> None:
        """Remember what this stands for, for the error message.

        Args:
            label: The client attribute this object replaces.
        """
        self._label = label

    def __getattr__(self, name: str) -> Any:
        """Refuse any capability.

        Raises:
            StubCalled: Always.
        """
        raise StubCalled(f"stub client: {self._label}.{name} is forbidden")


class StubModels:
    """``client.models`` for the rehearsal: ``list()`` only, unless capturing."""

    def __init__(self, names: list[str], capture: list | None) -> None:
        """Set the served names and the capture sink.

        Args:
            names: Model names ``list()`` reports as served.
            capture: When a list, ``generate_content`` appends its request
                here and raises; when None, it raises without recording.
        """
        self._names = names
        self._capture = capture

    def list(self) -> list[pytypes.SimpleNamespace]:
        """Report the pinned models as served (no network).

        Returns:
            Objects with a ``name`` attribute, as the SDK's listing has.
        """
        return [pytypes.SimpleNamespace(name=f"models/{n}") for n in self._names]

    def generate_content(self, model: str, contents: Any, config: Any) -> None:
        """Record a real-time request (capture mode) and stop it.

        Raises:
            StubCalled: Always — no response is fabricated.
        """
        if self._capture is None:
            raise StubCalled("stub client: models.generate_content is forbidden")
        self._capture.append({"kind": "generate_content", "model": model,
                              "contents": contents, "config": config})
        raise StubCalled("captured")

    def count_tokens(self, model: str, contents: Any) -> pytypes.SimpleNamespace:
        """Answer the batch cache's size check with the measured prefix size.

        Returns:
            An object whose ``total_tokens`` is 18,909 — the image prefix the
            original legs recorded (only used in capture mode).

        Raises:
            StubCalled: Outside capture mode.
        """
        if self._capture is None:
            raise StubCalled("stub client: models.count_tokens is forbidden")
        return pytypes.SimpleNamespace(total_tokens=18909)


class StubCaches:
    """``client.caches`` for capture mode: records the cache it is asked for."""

    def __init__(self, capture: list | None) -> None:
        """Set the capture sink.

        Args:
            capture: List to append requests to, or None to forbid.
        """
        self._capture = capture

    def create(self, model: str, config: Any) -> pytypes.SimpleNamespace:
        """Record a cache request and return a fake handle.

        Returns:
            An object with ``name`` and ``usage_metadata.total_token_count``.

        Raises:
            StubCalled: Outside capture mode.
        """
        if self._capture is None:
            raise StubCalled("stub client: caches.create is forbidden")
        self._capture.append({"kind": "caches.create", "model": model,
                              "config": config})
        return pytypes.SimpleNamespace(
            name="cachedContents/STUB",
            usage_metadata=pytypes.SimpleNamespace(total_token_count=18909))

    def delete(self, name: str) -> None:
        """Accept the detector's cache clean-up (capture mode only).

        Raises:
            StubCalled: Outside capture mode.
        """
        if self._capture is None:
            raise StubCalled("stub client: caches.delete is forbidden")


def make_stub_client(served: list[str], capture: list | None = None) -> type:
    """Build a ``genai.Client`` replacement class.

    Args:
        served: Model names ``models.list()`` reports.
        capture: Capture sink for real-time requests and caches, or None.

    Returns:
        A class whose instances expose ``models`` (and, when capturing,
        ``caches``); any other attribute raises :class:`StubCalled`.
    """

    class StubClient:
        """Stand-in for ``google.genai.Client``; never opens a connection."""

        instances = 0

        def __init__(self, *_args: Any, **_kwargs: Any) -> None:
            """Count the instance and attach the permitted surfaces."""
            StubClient.instances += 1
            self.models = StubModels(served, capture)
            self.caches = StubCaches(capture) if capture is not None else _Forbidden("caches")

        def __getattr__(self, name: str) -> Any:
            """Refuse every other capability (files, batches, ...).

            Raises:
                StubCalled: Always.
            """
            raise StubCalled(f"stub client: {name} is forbidden")

    return StubClient


def _sha(data: bytes) -> str:
    """Return the SHA-256 hex digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def _norm_part(part: Any) -> list:
    """Normalise one request part (SDK object or JSONL dict) for comparison.

    Args:
        part: A ``types.Part`` or a JSONL part dict.

    Returns:
        ``["text", sha256, first 60 chars]`` or ``["image", mime, sha256]``.
    """
    if isinstance(part, dict):
        if "text" in part:
            t = part["text"]
            return ["text", _sha(t.encode()), t[:60]]
        blob = part["inline_data"]
        return ["image", blob["mime_type"], _sha(base64.b64decode(blob["data"]))]
    if getattr(part, "text", None) is not None:
        return ["text", _sha(part.text.encode()), part.text[:60]]
    blob = part.inline_data
    return ["image", blob.mime_type, _sha(blob.data)]


def summarise_jsonl_line(line: dict) -> dict:
    """Normalise one batch JSONL request line.

    Args:
        line: A parsed JSONL line (``{"key": ..., "request": {...}}``).

    Returns:
        The canonical request summary (see :func:`summarise_sdk_request`).
    """
    req = line["request"]
    contents = req["contents"]
    gen = req.get("generation_config", {})
    si = req.get("system_instruction")
    return {
        "key": line["key"],
        "n_contents": len(contents),
        "roles": [c.get("role") for c in contents],
        "parts": [_norm_part(p) for c in contents for p in c["parts"]],
        "system_instruction_sha256": _sha(si["parts"][0]["text"].encode()) if si else None,
        "cached_content": req.get("cached_content"),
        "temperature": gen.get("temperature"),
        "max_output_tokens": gen.get("max_output_tokens"),
        "response_mime_type": gen.get("response_mime_type"),
        "thinking_level": (gen.get("thinking_config") or {}).get("thinking_level"),
        "safety_settings": req.get("safety_settings"),
        "service_tier": None,
        "request_keys": sorted(req.keys()),
    }


def summarise_sdk_request(rec: dict, key: str) -> dict:
    """Normalise one captured real-time ``generate_content`` call.

    Args:
        rec: The capture record (``contents`` and ``config`` SDK objects).
        key: The tile name the call was for.

    Returns:
        The canonical request summary, same fields as the batch one.
    """
    cfg = rec["config"]
    content = rec["contents"]
    contents = content if isinstance(content, list) else [content]
    tl = getattr(cfg.thinking_config, "thinking_level", None) if cfg.thinking_config else None
    tl = getattr(tl, "value", tl)
    si = cfg.system_instruction
    return {
        "key": key,
        "n_contents": len(contents),
        "roles": [getattr(c, "role", None) for c in contents],
        "parts": [_norm_part(p) for c in contents for p in c.parts],
        "system_instruction_sha256": _sha(si.encode()) if isinstance(si, str) else None,
        "cached_content": cfg.cached_content,
        "temperature": cfg.temperature,
        "max_output_tokens": cfg.max_output_tokens,
        "response_mime_type": cfg.response_mime_type,
        "thinking_level": str(tl).upper() if tl else None,
        "safety_settings": [[getattr(s.category, "value", s.category),
                             getattr(s.threshold, "value", s.threshold)]
                            for s in (cfg.safety_settings or [])] or None,
        "service_tier": getattr(cfg.service_tier, "value", cfg.service_tier),
        "request_keys": None,
    }


def summarise_cache(config: Any) -> dict:
    """Normalise a context-cache creation config (SDK object).

    Args:
        config: ``types.CreateCachedContentConfig`` as sent to ``caches.create``.

    Returns:
        System-instruction hash, roles and normalised parts of the cache.
    """
    si = config.system_instruction
    si_text = si if isinstance(si, str) else None
    parts = []
    roles = []
    for c in config.contents:
        roles.append(getattr(c, "role", None))
        for p in c.parts:
            parts.append(_norm_part(p if not isinstance(p, dict) else p))
    return {"system_instruction_sha256": _sha(si_text.encode()) if si_text else None,
            "roles": roles, "parts": parts}


def elide_tile(summary: dict) -> str:
    """Hash a request summary with its key and tile image removed.

    Every line of one arm should give the same value: the request is the
    same apart from the tile.

    Args:
        summary: A canonical request summary.

    Returns:
        SHA-256 of the canonical JSON with the last part (the tile) and the
        key dropped.
    """
    s = dict(summary)
    s.pop("key", None)
    s["parts"] = s["parts"][:-1]
    return _sha(json.dumps(s, sort_keys=True).encode())


def summarise_build(jsonl: Path, expected_keys: list[str]) -> dict:
    """Summarise a complete request file built by ``prepare_batch_unit``.

    Args:
        jsonl: The request file.
        expected_keys: The manifest slice the file should cover, in order.

    Returns:
        Line count, key check, the distinct elided signatures, generation
        and instruction fields, tile digest rows, first-line summary and
        file size.
    """
    rows: list[tuple[str, str]] = []
    sigs: dict[str, int] = {}
    keys: list[str] = []
    first: dict | None = None
    with open(jsonl) as fh:
        for raw in fh:
            line = json.loads(raw)
            s = summarise_jsonl_line(line)
            if first is None:
                first = s
            keys.append(s["key"])
            sig = elide_tile(s)
            sigs[sig] = sigs.get(sig, 0) + 1
            rows.append((s["key"], s["parts"][-1][2]))
    return {
        "jsonl_bytes": jsonl.stat().st_size,
        "n_lines": len(keys),
        "keys_match_manifest_slice": keys == expected_keys,
        "elided_signatures": sigs,
        "first_line": first,
        "tile_rows": rows,
    }


def tile_set_digest(rows: list[tuple[str, str]]) -> str:
    """Digest of (tile name, tile sha256) pairs, order-independent.

    Matches ``tile_set_sha256`` in the card's tile fingerprint.

    Args:
        rows: ``(name, sha256)`` pairs.

    Returns:
        SHA-256 of the canonical JSON of the sorted rows.
    """
    return _sha(json.dumps(sorted([list(r) for r in rows])).encode())


def _pinned_model(argv: list[str]) -> list[str]:
    """Return the model(s) the launch arguments pin with ``--model``.

    Args:
        argv: The detector arguments.

    Returns:
        The pinned name in a list. Unpinned, the ``-preview`` form of the
        config's model, which is what the original legs resolved
        ``gemini-3-flash`` to (``configuration.model`` in their metas).
    """
    if "--model" in argv:
        return [argv[argv.index("--model") + 1]]
    cfg = json.loads(Path(argv[argv.index("--config") + 1]).read_text())
    name = cfg["model"]
    return [name if name.endswith("-preview") else f"{name}-preview"]


def run_detector(argv: list[str]) -> int:
    """Run the detector's ``__main__`` with *argv*, as ``python DETECTOR`` would.

    Args:
        argv: The detector arguments.

    Returns:
        The detector's exit status.
    """
    root = Path.cwd()
    sys.path[:0] = [str(root / "scripts"), str(root)]
    sys.argv = [DETECTOR] + argv
    try:
        runpy.run_path(DETECTOR, run_name="__main__")
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


def main() -> int:
    """Parse arguments, install the guards, run one rehearsal, write a summary.

    Returns:
        0 when the rehearsal ran with no network attempt and no stub breach,
        1 otherwise (the summary lists each breach).
    """
    if "--" in sys.argv:
        cut = sys.argv.index("--")
        own, det = sys.argv[1:cut], sys.argv[cut + 1:]
    else:
        own, det = sys.argv[1:], []
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--summary-json", type=Path)
    ap.add_argument("--full-build", type=Path, default=None)
    ap.add_argument("--capture-realtime", type=int, default=None)
    ap.add_argument("--compare", nargs=2, type=Path, default=None)
    args = ap.parse_args(own)

    if args.compare:
        return compare(*args.compare)

    block_network()
    os.environ["GOOGLE_API_KEY"] = PLACEHOLDER_KEY
    os.environ.pop("GEMINI_API_KEY", None)
    import google.genai as genai  # after the socket guard

    capture: list | None = [] if args.capture_realtime else None
    stub = make_stub_client(_pinned_model(det), capture)
    genai.Client = stub  # type: ignore[misc]

    sys.path[:0] = [str(Path.cwd() / "scripts"), str(Path.cwd())]
    import scripts.lib_batch_api as lba  # noqa: E402

    summary: dict[str, Any] = {"argv": det, "chunks": [], "builds": [],
                               "lib_batch_api_file": lba.__file__}

    if args.capture_realtime:
        # The real-time path backs off 20-30 s after the stub's refusal; the
        # wait buys nothing here.
        time.sleep = lambda *_a, **_k: None  # type: ignore[assignment]
        det = det + ["--limit", str(args.capture_realtime), "--max-retries", "1"]
        status = run_detector(det)
        manifest = json.loads(Path(det[det.index("--manifest") + 1]).read_text())
        tiles_dir = Path(det[det.index("--tiles-dir") + 1])
        lookup = {p.name: p for p in tiles_dir.rglob("*.png")}
        # Name each captured call by its tile image, not by call order.
        by_sha = {_sha(lookup[n].read_bytes()): n
                  for n in manifest[:args.capture_realtime] if n in lookup}
        calls = [c for c in capture if c["kind"] == "generate_content"]
        caches = [c for c in capture if c["kind"] == "caches.create"]
        reqs = []
        for c in calls:
            s = summarise_sdk_request(c, "?")
            s["key"] = by_sha.get(s["parts"][-1][2], "?")
            reqs.append(s)
        summary["realtime_requests"] = reqs
        summary["realtime_caches"] = [summarise_cache(c["config"]) for c in caches]
    else:
        orig = lba.run_batch_unit

        def wrapped(**kw: Any) -> tuple[bool, str, float]:
            """Record the chunk plan, run the real dry run, optionally build in full."""
            plan = {"offset": kw["offset"], "limit": kw["limit"],
                    "model_name": kw["model_name"],
                    "use_context_cache": kw["use_context_cache"],
                    "cache_ttl_seconds": kw["cache_ttl_seconds"],
                    "dry_run": kw["dry_run"], "tile_size": kw["tile_size"],
                    "retry_service_tier": kw["retry_service_tier"],
                    "unit": kw["unit"]}
            result = orig(**kw)
            plan["dry_run_result"] = list(result)
            summary["chunks"].append(plan)
            if args.full_build is not None:
                ctx = lba.prepare_batch_unit(
                    unit=kw["unit"], config=kw["config"], output_dir=args.full_build,
                    model_name=kw["model_name"],
                    system_instruction=kw["system_instruction"],
                    examples=kw["examples"], config_version=kw["config_version"],
                    limit=kw["limit"], offset=kw["offset"], tile_size=kw["tile_size"],
                    tiles_dir=kw["tiles_dir"],
                    output_name_suffix=kw["output_name_suffix"],
                    cached_content=DRY_RUN_CACHE if kw["use_context_cache"] else None,
                    retry_service_tier=kw["retry_service_tier"])
                keys = [p.name for p in ctx.tile_paths]
                built = summarise_build(ctx.jsonl_path, keys)
                built["chunk_offset"] = kw["offset"]
                summary["builds"].append(built)
                ctx.jsonl_path.unlink()
                # Keep the cache-content check honest: what the real run's
                # create_shared_context_cache would send, captured by a stub.
                if kw["use_context_cache"] and "batch_cache" not in summary:
                    sink: list = []
                    cap = make_stub_client(_pinned_model(det), sink)()
                    # The same arguments run_batch_unit passes (its include
                    # flag is read from the STUDY config, so it is True here).
                    lba.create_shared_context_cache(
                        client=cap, model_name=kw["model_name"],
                        system_instruction=kw["system_instruction"],
                        examples=kw["examples"],
                        include_images=kw["config"].get("include_example_images", True),
                        ttl_seconds=kw["cache_ttl_seconds"])
                    summary["batch_cache"] = [summarise_cache(c["config"]) for c in sink
                                              if c["kind"] == "caches.create"]
            return result

        lba.run_batch_unit = wrapped
        status = run_detector(det + ["--dry-run"])

    summary["exit_status"] = status
    summary["stub_client_instances"] = stub.instances
    summary["breaches"] = list(BREACHES)
    if summary.get("builds"):
        rows = [r for b in summary["builds"] for r in b.pop("tile_rows")]
        summary["tile_set_sha256"] = tile_set_digest(rows)
        summary["n_requests"] = len(rows)
    if args.summary_json:
        args.summary_json.write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps({k: v for k, v in summary.items() if k != "builds"},
                     indent=1, default=str)[:4000])
    return 1 if BREACHES else 0


def compare(batch_path: Path, realtime_path: Path) -> int:
    """Compare a batch build's first lines with captured real-time requests.

    Args:
        batch_path: Summary JSON from a ``--full-build`` batch rehearsal.
        realtime_path: Summary JSON from a ``--capture-realtime`` rehearsal.

    Returns:
        0 always; differences are printed field by field.
    """
    b = json.loads(batch_path.read_text())
    r = json.loads(realtime_path.read_text())
    first = b["builds"][0]["first_line"]
    rt = {x["key"]: x for x in r.get("realtime_requests", [])}
    other = rt.get(first["key"])
    if other is None:
        print(f"no real-time capture for {first['key']}")
        return 0
    for field in sorted(set(first) | set(other)):
        same = first.get(field) == other.get(field)
        print(f"{'SAME' if same else 'DIFF'}  {field}")
        if not same:
            print(f"      batch:     {json.dumps(first.get(field))[:300]}")
            print(f"      real-time: {json.dumps(other.get(field))[:300]}")
    if b.get("batch_cache") or r.get("realtime_caches"):
        same = b.get("batch_cache", [None])[0] == r.get("realtime_caches", [None])[0]
        print(f"{'SAME' if same else 'DIFF'}  context-cache contents")
        if not same:
            print(f"      batch:     {json.dumps(b.get('batch_cache'))[:400]}")
            print(f"      real-time: {json.dumps(r.get('realtime_caches'))[:400]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
