#!/usr/bin/env python3
"""
API-free rehearsal of a verifier leg: batch dry run and real-time capture.

Why this exists
---------------
Run B's Stage 2 (``planning/modality-bridge-2026-10-07-stage2.md``) verifies
its unions on the Batch API, where every original leg ran the real-time
path. Before any spend, the batch request Stage 2 will send must be compared
field by field with the request each original leg sent. This harness does
both halves without reaching a server, using the Stage 1 harness's guards
(``scripts/bridge_dryrun_harness.py``: every socket connection and name
lookup refused, ``google.genai.Client`` replaced by a stub, a placeholder
key):

``batch``
    Runs ``run_pv.py verify --mode batch --dry-run`` with a stub client
    that has NO capability (constructing it is recorded). The dry run
    builds the request file(s) and returns before any client exists
    (``run_pv._verify_batch``: the ``dry_run`` return precedes the
    ``genai.Client`` construction), so a clean run records zero stub
    instances and zero breaches — the evidence that it is API-free. The
    request file is summarised (line count, keys against the manifest,
    one tile-elided signature per leg, the first N requests) and deleted.

``realtime``
    Runs ``run_pv.py verify --mode realtime`` from ANY checkout
    (``--repo-root``: the original leg's commit, in a disposable
    worktree) with a stub whose ``models.list()`` reports the served
    names and whose ``generate_content`` records the request and raises,
    so the request the original code sends is captured without a call.

``compare``
    Field by field, the batch requests against the captured real-time
    requests of the same candidates.

The harness never imports this repository's ``scripts`` package before
running the target, so an original checkout's ``run_pv.py`` runs with its
own ``lib_verifier``.

Usage::

    python scripts/verifier_dryrun_harness.py batch --summary-json b.json \\
        --first 3 -- --crops-dir C --verifier-config V --output-dir O \\
        --mode batch --dry-run --temperature 0.0 --model gemini-3-flash-preview
    python scripts/verifier_dryrun_harness.py realtime --repo-root WT \\
        --served gemini-3-flash-preview --summary-json r.json \\
        -- --crops-dir C --verifier-config V --output-dir O --mode realtime --workers 1
    python scripts/verifier_dryrun_harness.py compare b.json r.json

Run from the repository root. Zero API calls by construction.

Created: 2026-10-07
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import runpy
import sys
import time
from pathlib import Path
from typing import Any

#: This harness's own repository (the Stage 1 harness is loaded from here).
HERE = Path(__file__).resolve().parent.parent

#: Fields that legitimately differ between a batch line and a real-time call
#: by representation only (not request content).
REPRESENTATION_ONLY = ("key", "request_keys", "roles")

#: Exceptions the target raised (other than SystemExit), in order.
TARGET_ERRORS: list[str] = []


def load_stage1_harness() -> Any:
    """Load ``bridge_dryrun_harness.py`` by path, outside the ``scripts`` package.

    Returns:
        The module (guards, stub client and request summarisers).
    """
    path = HERE / "scripts" / "bridge_dryrun_harness.py"
    spec = importlib.util.spec_from_file_location("_bridge_dryrun_harness", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _sha(data: bytes) -> str:
    """Return the SHA-256 hex digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def _arg(argv: list[str], flag: str) -> str | None:
    """Return the value after *flag* in *argv*, or None."""
    return argv[argv.index(flag) + 1] if flag in argv else None


def run_target(repo_root: Path, argv: list[str]) -> int:
    """Run ``<repo_root>/scripts/run_pv.py verify`` in-process.

    The harness's own ``scripts`` directory is taken off ``sys.path`` and no
    ``scripts`` package may be imported yet, so the target resolves every
    ``scripts.*`` import inside its own checkout.

    Args:
        repo_root: The checkout whose ``run_pv.py`` runs.
        argv: Arguments after ``verify``.

    Returns:
        The target's exit status.

    Raises:
        RuntimeError: If a ``scripts`` package is already imported.
    """
    if any(m == "scripts" or m.startswith("scripts.") for m in sys.modules):
        raise RuntimeError("a scripts package is already imported; refusing to "
                           "run a target that would reuse it")
    own = str(HERE / "scripts")
    sys.path[:] = [p for p in sys.path if p != own]
    sys.path[:0] = [str(repo_root), str(repo_root / "scripts")]
    target = repo_root / "scripts" / "run_pv.py"
    sys.argv = [str(target), "verify"] + argv
    os.chdir(repo_root)
    try:
        runpy.run_path(str(target), run_name="__main__")
    except SystemExit as exc:
        return int(exc.code or 0)
    except Exception as exc:  # noqa: BLE001 — a crash after capture is still evidence
        # An old checkout may fail after the requests were captured (e.g.
        # writing outputs it was never meant to write under a stub); the
        # capture is what the rehearsal needs, and the error is recorded.
        TARGET_ERRORS.append(f"{type(exc).__name__}: {exc}")
        return -1
    return 0


def _install_guards(h: Any, served: list[str], capture: list | None) -> type:
    """Block the network, set a placeholder key, stub the client.

    Args:
        h: The Stage 1 harness module.
        served: Model names the stub's ``models.list()`` reports.
        capture: Capture sink for ``generate_content``, or None to forbid it.

    Returns:
        The stub client class (its ``instances`` counts constructions).
    """
    h.block_network()
    os.environ["GOOGLE_API_KEY"] = h.PLACEHOLDER_KEY
    os.environ.pop("GEMINI_API_KEY", None)
    import google.genai as genai  # after the socket guard

    stub = h.make_stub_client(served, capture)
    genai.Client = stub  # type: ignore[misc]
    return stub


def full_elided_signature(line: dict) -> str:
    """SHA-256 of a whole batch request line with only its key and crop bytes removed.

    The Stage 1 signature (``bridge_dryrun_harness.elide_tile`` over
    ``summarise_jsonl_line``) hashes five named generation-config fields, so a
    field added to the request builder would not move it (Stage 2 audit,
    nit). This one hashes everything else in the request (every
    ``generation_config`` key and value, the system instruction, roles,
    request keys, every text part, the crop's MIME type), so any change to
    the request moves it, while every candidate of one leg still shares it.

    Args:
        line: A parsed JSONL line (``{"key": ..., "request": {...}}``).

    Returns:
        Hex digest of the canonical JSON of the request with the last
        part's ``inline_data.data`` replaced by a placeholder.
    """
    req = json.loads(json.dumps(line["request"]))
    last = req["contents"][-1]["parts"][-1]
    if "inline_data" in last:
        last["inline_data"]["data"] = "<crop>"
    return _sha(json.dumps(req, sort_keys=True).encode())


def summarise_batch_dir(h: Any, out_dir: Path, manifest: dict, first: int,
                        keep: bool = False) -> dict[str, Any]:
    """Summarise a dry run's request file(s), then delete them.

    Args:
        h: The Stage 1 harness module.
        out_dir: The dry run's ``--output-dir``.
        manifest: The crop manifest the requests were built from.
        first: How many leading requests to keep in full summary.
        keep: Keep the request files (default: delete after summary).

    Returns:
        Line count, key check, tile-elided signatures, the first requests'
        summaries and the files' sizes.
    """
    def order(p: Path) -> int:
        """The unchunked file first, then chunks in numeric order."""
        tail = p.stem.removeprefix("verifier_requests").removeprefix("_chunk")
        return int(tail) if tail.isdigit() else -1

    files = sorted(out_dir.glob("verifier_requests*.jsonl"), key=order)
    keys: list[str] = []
    sigs: dict[str, int] = {}
    full: dict[str, int] = {}
    gen_keys: dict[str, int] = {}
    head: list[dict] = []
    for f in files:
        with open(f) as fh:
            for raw in fh:
                line = json.loads(raw)
                s = h.summarise_jsonl_line(line)
                keys.append(s["key"])
                sig = h.elide_tile(s)
                sigs[sig] = sigs.get(sig, 0) + 1
                fsig = full_elided_signature(line)
                full[fsig] = full.get(fsig, 0) + 1
                gk = ",".join(sorted(line["request"].get("generation_config", {})))
                gen_keys[gk] = gen_keys.get(gk, 0) + 1
                if len(head) < first:
                    head.append(s)
    expected = [f"candidate_{c['candidate_id']:05d}" for c in manifest["candidates"]]
    out = {
        "request_files": [f.name for f in files],
        "request_bytes": [f.stat().st_size for f in files],
        "n_lines": len(keys),
        "n_candidates": len(expected),
        "keys_match_manifest": keys == expected,
        "elided_signatures": sigs,
        "full_elided_signatures": full,
        "generation_config_keys": gen_keys,
        "first_requests": head,
    }
    if not keep:
        for f in files:
            f.unlink()
    return out


def crop_key_lookup(crops_dir: Path, manifest: dict) -> dict[str, str]:
    """Map each crop image's SHA-256 to its candidate key.

    Args:
        crops_dir: The crops directory (``crop_file`` paths are relative to it).
        manifest: The crop manifest.

    Returns:
        ``{sha256: "candidate_NNNNN"}``.
    """
    return {_sha((crops_dir / c["crop_file"]).read_bytes()):
            f"candidate_{c['candidate_id']:05d}" for c in manifest["candidates"]}


def compare_requests(batch: dict, realtime: dict) -> dict[str, Any]:
    """Compare batch request summaries with captured real-time ones, per field.

    Args:
        batch: A ``batch`` summary JSON.
        realtime: A ``realtime`` summary JSON.

    Returns:
        Per candidate the fields that are SAME and those that DIFF (with
        both values), and the union of differing fields over all
        candidates, split into content and representation-only.
    """
    rt = {r["key"]: r for r in realtime.get("realtime_requests", [])}
    rows = []
    diff_fields: set[str] = set()
    for b in batch["batch"]["first_requests"]:
        r = rt.get(b["key"])
        if r is None:
            rows.append({"key": b["key"], "captured": False})
            continue
        same, diff = [], {}
        for field in sorted(set(b) | set(r)):
            if b.get(field) == r.get(field):
                same.append(field)
            else:
                diff[field] = {"batch": b.get(field), "realtime": r.get(field)}
                diff_fields.add(field)
        rows.append({"key": b["key"], "captured": True, "same": same, "diff": diff})
    return {
        "rows": rows,
        "content_diff_fields": sorted(diff_fields - set(REPRESENTATION_ONLY)),
        "representation_diff_fields": sorted(diff_fields & set(REPRESENTATION_ONLY)),
        "realtime_model": realtime.get("realtime_model"),
    }


def main() -> int:
    """Run one rehearsal mode.

    Returns:
        0 when the rehearsal reached no server (no breach, and for ``batch``
        no stub client constructed) and its checks held; 1 otherwise.
    """
    if "--" in sys.argv:
        cut = sys.argv.index("--")
        own, target = sys.argv[1:cut], sys.argv[cut + 1:]
    else:
        own, target = sys.argv[1:], []
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["batch", "realtime", "compare"])
    ap.add_argument("paths", nargs="*", type=Path,
                    help="compare: BATCH.json REALTIME.json")
    ap.add_argument("--repo-root", type=Path, default=HERE,
                    help="Checkout whose run_pv.py runs (default: this one).")
    ap.add_argument("--served", nargs="*", default=[],
                    help="realtime: model names models.list() reports.")
    ap.add_argument("--summary-json", type=Path, default=None)
    ap.add_argument("--first", type=int, default=3,
                    help="batch: leading requests kept in full summary.")
    ap.add_argument("--keep-requests", action="store_true",
                    help="batch: keep the request files (default: delete).")
    args = ap.parse_args(own)

    if args.mode == "compare":
        batch, realtime = (json.loads(p.read_text()) for p in args.paths)
        result = compare_requests(batch, realtime)
        print(json.dumps({k: v for k, v in result.items() if k != "rows"}, indent=1))
        for row in result["rows"]:
            print(row["key"], "DIFF:", sorted(row.get("diff", {})) or "none")
        if args.summary_json:
            args.summary_json.write_text(json.dumps(result, indent=1, default=str))
        return 0

    h = load_stage1_harness()
    repo = args.repo_root.resolve()
    # The target runs from its repository root, so relative paths in its
    # arguments are relative to that root.
    crops_dir = repo / _arg(target, "--crops-dir")
    out_dir = repo / _arg(target, "--output-dir")
    manifest = json.loads((crops_dir / "candidate_manifest.json").read_text())
    summary: dict[str, Any] = {"mode": args.mode, "argv": target,
                               "repo_root": str(repo)}

    if args.mode == "batch":
        if "--dry-run" not in target or _arg(target, "--mode") != "batch":
            ap.error("batch mode rehearses `--mode batch --dry-run` only")
        stub = _install_guards(h, served=[], capture=None)
        status = run_target(repo, target)
        summary["batch"] = summarise_batch_dir(h, out_dir, manifest, args.first,
                                               args.keep_requests)
        ok = (status == 0 and stub.instances == 0 and not h.BREACHES
              and summary["batch"]["keys_match_manifest"]
              and len(summary["batch"]["elided_signatures"]) == 1
              and len(summary["batch"]["full_elided_signatures"]) == 1)
    else:
        capture: list = []
        stub = _install_guards(h, served=args.served, capture=capture)
        # The real-time retry loop backs off after the stub's refusal; the
        # wait buys nothing here.
        time.sleep = lambda *_a, **_k: None  # type: ignore[assignment]
        status = run_target(repo, target)
        lookup = crop_key_lookup(crops_dir, manifest)
        reqs, attempts = [], {}
        for c in capture:
            if c["kind"] != "generate_content":
                continue
            s = h.summarise_sdk_request(c, "?")
            s["key"] = lookup.get(s["parts"][-1][2], "?")
            attempts[s["key"]] = attempts.get(s["key"], 0) + 1
            if attempts[s["key"]] == 1:
                reqs.append(s)
        summary["realtime_requests"] = reqs
        summary["realtime_attempts_per_candidate"] = attempts
        summary["realtime_model"] = sorted({c["model"] for c in capture
                                            if c["kind"] == "generate_content"})
        ok = not h.BREACHES and len(reqs) == len(manifest["candidates"])

    summary["exit_status"] = status
    summary["target_errors"] = list(TARGET_ERRORS)
    if args.mode == "batch" and TARGET_ERRORS:
        ok = False
    summary["stub_client_instances"] = stub.instances
    summary["breaches"] = list(h.BREACHES)
    summary["ok"] = bool(ok)
    if args.summary_json:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("realtime_requests", "batch")}, indent=1,
                     default=str))
    if "batch" in summary:
        print(json.dumps({k: v for k, v in summary["batch"].items()
                          if k != "first_requests"}, indent=1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
