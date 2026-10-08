#!/usr/bin/env python3
"""
Re-send a few unparseable batch verifier rows as ONE batch job, and book them.

Why this exists
---------------
The batch verifier path books a response that plain ``json.loads`` rejects
as ``mound_probability`` 0.0 with reasoning ``PARSE_ERROR: …``
(``lib_verifier.parse_verifier_results``). The original legs' real-time path
either repaired such a response (``lib_batch_api.parse_response_with_repair``)
or retried it. ``scripts/modality_bridge_stage2_checks.py repair`` closes the
first half after landing: it re-parses the leg's ``PARSE_ERROR`` rows into a
sibling ``<leg>_repaired/`` and REMOVES every row no repair can parse, so
scoring refuses until that row is re-verified (Stage 2 card § 7 item 11,
``planning/modality-bridge-2026-10-07-stage2.md``).

This script is the second half for a handful of rows spread over several
legs: the retry the real-time path would have made. PI decision D55 (Q4),
``planning/pi-decisions-2026-09-20.md``, approved re-sending the seven
unparseable rows of the 55-map Gemini 3 image arm 2 legs on the Batch API as
seven ``gemini-3.7-flash`` calls in one job. The established clean-up
(``run_pv.py cleanup``) runs real-time (flex), which would be a mode
deviation, and ``run_pv.py verify --mode batch`` lodges one job per crops
directory, which would be three jobs. Hence this script.

**What is sent is the original request, byte for byte.** ``build`` copies
each row's line out of the leg's own ``verifier_requests*.jsonl`` (the file
the leg was lodged from), audits it against the leg's ``run.meta.json``
(temperature, output ceiling, thinking level, system-instruction hash, and
one model across every leg), and rebuilds it with today's
``lib_verifier.build_verifier_jsonl`` from the leg's crop as a cross-check.
Keys are not rewritten, so they must be unique across the legs. Only the
rows change; nothing else.

Subcommands
-----------
``build``    Select the rows (``PARSE_ERROR`` and unrepairable), copy their
             request lines, audit them, estimate the cost on the rate card,
             write ``requests.jsonl`` and ``build.json`` into the run
             directory. Refuses unless the row count equals ``--expect`` and
             the estimate is within ``--max-cost-usd``. Zero API.
``lodge``    Upload ``requests.jsonl``, submit ONE batch job, poll it to a
             terminal state, write ``batch_jobs.json`` and
             ``batch_results.jsonl``. Refuses if the run directory already
             records a job: a second batch is a new approval. Prints
             ``REVERIFY LODGE COMPLETE`` or ``REVERIFY LODGE PARTIAL`` at the
             start of a line, the markers ``wait_for_run.py`` keys on.
``book``     Parse each new response (plain ``json.loads`` as the leg did,
             then the real-time path's repair), price its usage on the rate
             card at the batch tier, and merge it into ``<leg>_repaired/``
             (which ``repair`` must have written first). A response that is
             again unparseable is NOT booked and is not re-sent: exit 1.
             Writes ``record.json`` (every row: original and new response,
             old and new probability, usage, cost) into the run directory
             and ``reverify-<date>.json`` into each repaired copy. Zero API.
``release``  After the outputs are committed: delete this job's own input and
             output files from the Files API. Never deletes any file the
             run directory's ``batch_jobs.json`` does not name.

Usage::

    # on sapphire, in a scratch clone; the request files are the main
    # checkout's untracked verifier_requests*.jsonl
    S=outputs/gemini3-image-55map-2026-09-16/verifier/g384_ov192_55map_g3img
    RUN=$S/reverify-parse-errors-2026-10-08
    .venv/bin/python scripts/reverify_unparseable_rows.py build --out $RUN \\
        --expect 7 --max-cost-usd 0.05 --requests-root ~/Code/map-reader-llm \\
        --crops-root ~/Code/map-reader-llm \\
        --leg $S/verify_k1_arm2=$S/crops_k1 --leg $S/verify_k3_arm2=$S/crops_k3 \\
        --leg $S/verify_k5_arm2=$S/crops_k5
    .venv/bin/python scripts/reverify_unparseable_rows.py lodge --run-dir $RUN \\
        --max-cost-usd 0.05
    .venv/bin/python scripts/reverify_unparseable_rows.py book --run-dir $RUN
    # commit the run directory and the repaired copies, then:
    .venv/bin/python scripts/reverify_unparseable_rows.py release --run-dir $RUN

``lodge`` spends (about US$0.01 for seven 3.7 Flash calls). Every other
subcommand except ``release`` (a Files API delete) is zero API.

Created: 2026-10-08
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import math
import sys
import tempfile
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.modality_bridge_stage2_checks import (  # noqa: E402
    _response_text,
    diff_paths,
    repair_text,
)

logger = logging.getLogger(__name__)

#: Markers printed at the start of a line for ``wait_for_run.py --marker``.
MARKER_COMPLETE = "REVERIFY LODGE COMPLETE"
MARKER_PARTIAL = "REVERIFY LODGE PARTIAL"

#: The tier this script lodges at; the rate card prices it.
TIER = "batch"

#: The verdict fields a leg's ``probabilities.json`` row carries.
VERDICT_FIELDS = ("mound_probability", "reasoning", "best_alternative",
                  "alternative_evidence")


class Refused(RuntimeError):
    """A gate refused; nothing was sent or written beyond what is reported."""


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def sha256_bytes(data: bytes) -> str:
    """SHA-256 hex digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    """SHA-256 hex digest of a file's bytes."""
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    """*path* relative to the project root when it lies inside it."""
    try:
        return str(path.resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def is_parse_error(row: dict[str, Any]) -> bool:
    """Whether a booked row is the batch parser's PARSE_ERROR 0.0."""
    return str(row.get("reasoning", "")).startswith("PARSE_ERROR")


def read_raw_rows(path: Path, keys: set[str]) -> dict[str, dict]:
    """The rows of a batch results file whose ``key`` is in *keys*.

    A cheap substring test runs before the JSON parse, so a 90 MB results
    file is not parsed line by line for a handful of keys.

    Args:
        path: ``batch_results.jsonl``.
        keys: The keys wanted.

    Returns:
        ``key -> row``; a key with no row is absent.
    """
    out: dict[str, dict] = {}
    with open(path) as fh:
        for line in fh:
            if not any(f'"{k}"' in line for k in keys):
                continue
            row = json.loads(line)
            if row.get("key") in keys:
                out[row["key"]] = row
    return out


def find_request_lines(files: list[Path], keys: set[str]) -> dict[str, list[tuple[Path, bytes]]]:
    """Every request line, as raw bytes, whose ``key`` is in *keys*.

    Args:
        files: The leg's ``verifier_requests*.jsonl`` files.
        keys: The keys wanted.

    Returns:
        ``key -> [(file, line bytes without the newline), ...]``. More than
        one entry means the key was lodged more than once.
    """
    found: dict[str, list[tuple[Path, bytes]]] = {k: [] for k in keys}
    needles = {k: f'"{k}"'.encode() for k in keys}
    for path in files:
        with open(path, "rb") as fh:
            for line in fh:
                hit = [k for k, n in needles.items() if n in line]
                if not hit:
                    continue
                body = line.rstrip(b"\n")
                key = json.loads(body).get("key")
                if key in found:
                    found[key].append((path, body))
    return found


def request_files(leg_dir: Path) -> list[Path]:
    """A leg's request files, ``verifier_requests.jsonl`` or its chunks."""
    single = leg_dir / "verifier_requests.jsonl"
    if single.exists():
        return [single]
    return sorted(leg_dir.glob("verifier_requests_chunk*.jsonl"),
                  key=lambda p: int(p.stem.rsplit("chunk", 1)[1]))


def valid_probability(value: Any) -> bool:
    """A number in [0, 1] that is not a bool, NaN or infinite."""
    return (not isinstance(value, bool) and isinstance(value, (int, float))
            and math.isfinite(value) and 0.0 <= value <= 1.0)


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------


def audit_line(line: dict[str, Any], configuration: dict[str, Any]) -> list[str]:
    """Compare one request line with the configuration its leg recorded.

    Args:
        line: The parsed request line.
        configuration: The leg's ``run.meta.json`` ``configuration`` block.

    Returns:
        A list of mismatches, empty when the line matches.
    """
    problems: list[str] = []
    req = line.get("request", {})
    gen = req.get("generation_config", {})
    if gen.get("temperature") != configuration.get("temperature"):
        problems.append(f"temperature {gen.get('temperature')!r} != "
                        f"{configuration.get('temperature')!r}")
    if gen.get("max_output_tokens") != configuration.get("max_output_tokens"):
        problems.append(f"max_output_tokens {gen.get('max_output_tokens')!r} != "
                        f"{configuration.get('max_output_tokens')!r}")
    sent_level = str((gen.get("thinking_config") or {}).get("thinking_level", "")).lower()
    if sent_level != str(configuration.get("thinking_level", "")).lower():
        problems.append(f"thinking_level {sent_level!r} != "
                        f"{configuration.get('thinking_level')!r}")
    parts = (req.get("system_instruction") or {}).get("parts") or [{}]
    text = parts[0].get("text", "")
    if sha256_bytes(text.encode("utf-8")) != configuration.get("system_instruction_hash"):
        problems.append("system instruction hash differs from the leg's")
    return problems


def rebuild_line(candidate: dict[str, Any], configuration: dict[str, Any],
                 crops_dir: Path) -> dict[str, Any]:
    """Rebuild one request line with today's builder, for the cross-check.

    Uses the leg's recorded ``full_config_snapshot`` (which carries the
    thinking-level override the leg ran with) and its recorded temperature.

    Args:
        candidate: The candidate's entry in the crops manifest.
        configuration: The leg's ``configuration`` block.
        crops_dir: The leg's crops directory.

    Returns:
        The parsed line ``lib_verifier.build_verifier_jsonl`` writes.
    """
    from scripts.lib_verifier import build_verifier_jsonl

    config = dict(configuration["full_config_snapshot"])
    config["thinking_level"] = configuration.get("thinking_level")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "rebuilt.jsonl"
        build_verifier_jsonl(manifest={"candidates": [candidate]}, config=config,
                             output_path=out, crops_base_dir=crops_dir,
                             temperature_override=configuration.get("temperature"))
        return json.loads(out.read_text().splitlines()[0])


def estimate_cost(legs: list[dict[str, Any]], model: str, at: str) -> dict[str, Any]:
    """Price the rows to be sent at each leg's own mean usage per call.

    Args:
        legs: Per-leg ``{"n_rows", "usage_stats", "n_results"}``.
        model: The model to price.
        at: The date to price at (ISO).

    Returns:
        The rate card's cost block for the estimated usage.
    """
    from scripts.lib_cost import price_usage

    total = {"total_input_tokens": 0, "total_cached_tokens": 0,
             "total_output_tokens": 0, "total_thoughts_tokens": 0}
    n_rows = 0
    for leg in legs:
        n = leg["n_rows"]
        if not n:
            continue
        n_rows += n
        per = max(1, int(leg["n_results"]))
        for field in total:
            total[field] += round(int(leg["usage_stats"].get(field) or 0) * n / per)
    total["n_responses_with_usage"] = n_rows
    return price_usage(total, model=model, tier=TIER, at=at,
                       tier_source="estimate: each leg's mean usage per call")


def parse_leg_spec(spec: str) -> tuple[Path, Path | None]:
    """``LEG_DIR[=CROPS_DIR]`` to paths."""
    leg, _, crops = spec.partition("=")
    return Path(leg), (Path(crops) if crops else None)


def build(legs: list[tuple[Path, Path | None]], out_dir: Path, expect: int,
          max_cost_usd: float, requests_root: Path | None = None,
          crops_root: Path | None = None, at: str | None = None) -> dict[str, Any]:
    """Select, copy and audit the request lines of the unparseable rows.

    Args:
        legs: ``(leg_dir, crops_dir or None)`` per leg, paths relative to the
            project root (or absolute).
        out_dir: The run directory; ``requests.jsonl`` and ``build.json``
            are written there.
        expect: The number of rows to send; any other count is refused.
        max_cost_usd: The estimate's ceiling.
        requests_root: Where ``<leg_dir>/verifier_requests*.jsonl`` are found
            (default: the leg directory as given).
        crops_root: Where ``<crops_dir>`` is found for the cross-check
            (default: as given).
        at: Pricing date (default: today, UTC).

    Returns:
        The build record (also written as ``build.json``).

    Raises:
        Refused: On any failed gate; nothing is written.
    """
    at = at or datetime.now(timezone.utc).date().isoformat()
    if out_dir.exists() and any(out_dir.iterdir()):
        raise Refused(f"{out_dir} is not empty; a build is never overwritten")
    rows: list[dict[str, Any]] = []
    repairable: list[dict[str, Any]] = []
    lines: list[bytes] = []
    leg_records: list[dict[str, Any]] = []
    models: set[str] = set()
    seen_keys: dict[str, str] = {}
    for leg_dir, crops_dir in legs:
        probs = json.loads((leg_dir / "probabilities.json").read_text())
        meta = json.loads((leg_dir / "run.meta.json").read_text())
        configuration = meta["configuration"]
        targets = {k for k, v in probs["results"].items() if is_parse_error(v)}
        raw = read_raw_rows(leg_dir / "batch_results.jsonl", targets)
        resend: list[str] = []
        for key in sorted(targets):
            text = _response_text(raw.get(key, {}))
            try:
                if text is None:
                    raise ValueError("no response text in batch_results.jsonl")
                prob = repair_text(text)["mound_probability"]
            except (ValueError, TypeError) as exc:
                resend.append(key)
                rows.append({"leg": rel(leg_dir), "key": key,
                             "booked": probs["results"][key],
                             "original_response_text": text,
                             "original_usage": (raw.get(key, {}).get("response") or {})
                             .get("usageMetadata"),
                             "repair_error": str(exc)})
            else:
                repairable.append({"leg": rel(leg_dir), "key": key, "repairs_to": prob})
        if resend:
            models.add(configuration["model"])
        req_root = (requests_root / leg_dir) if requests_root else leg_dir
        files = request_files(req_root)
        if resend and not files:
            raise Refused(f"no verifier_requests*.jsonl under {req_root}")
        found = find_request_lines(files, set(resend))
        manifest_by_id: dict[int, dict] = {}
        crops_path = None
        if crops_dir is not None:
            crops_path = (crops_root / crops_dir) if crops_root else crops_dir
            manifest = json.loads((crops_path / "candidate_manifest.json").read_text())
            manifest_by_id = {c["candidate_id"]: c for c in manifest["candidates"]}
        for row in [r for r in rows if r["leg"] == rel(leg_dir)]:
            key = row["key"]
            if key in seen_keys:
                raise Refused(f"{key} is in {seen_keys[key]} and {row['leg']}: keys "
                              "must be unique across the legs, and are not rewritten")
            seen_keys[key] = row["leg"]
            hits = found.get(key, [])
            bodies = {b for _, b in hits}
            if len(bodies) != 1:
                raise Refused(f"{row['leg']} {key}: {len(bodies)} distinct request lines "
                              f"in {len(files)} request file(s); need exactly one")
            src, body = hits[0]
            line = json.loads(body)
            problems = audit_line(line, configuration)
            if problems:
                raise Refused(f"{row['leg']} {key}: request line does not match the leg's "
                              f"run.meta.json: {problems}")
            row["request_file"] = str(src)
            row["request_line_sha256"] = sha256_bytes(body)
            row["request_line_bytes"] = len(body)
            cross: dict[str, Any] = {"checked": False}
            cid = int(key.rsplit("_", 1)[1])
            if crops_path is not None and cid in manifest_by_id:
                rebuilt = rebuild_line(manifest_by_id[cid], configuration, crops_path)
                diffs = diff_paths(line, rebuilt)
                cross = {"checked": True, "identical_parsed": not diffs,
                         "identical_bytes": json.dumps(rebuilt).encode() == body,
                         "differing_paths": diffs}
            row["rebuild_cross_check"] = cross
            lines.append(body)
        leg_records.append({
            "leg": rel(leg_dir), "model": configuration["model"],
            "thinking_level": configuration.get("thinking_level"),
            "temperature": configuration.get("temperature"),
            "max_output_tokens": configuration.get("max_output_tokens"),
            "system_instruction_hash": configuration.get("system_instruction_hash"),
            "n_results": len(probs["results"]), "n_parse_error_rows": len(targets),
            "n_rows": len(resend), "keys": resend,
            "usage_stats": meta.get("usage_stats", {}),
            "request_files": [str(f) for f in files],
        })
    if len(rows) != expect:
        raise Refused(f"{len(rows)} unparseable row(s) found, --expect {expect}; "
                      "nothing written")
    if len(models) != 1:
        raise Refused(f"the rows' legs ran {sorted(models)}; one batch job takes one model")
    model = models.pop()
    estimate = estimate_cost(leg_records, model, at)
    if estimate["total_cost_usd"] is None or estimate["total_cost_usd"] > max_cost_usd:
        raise Refused(f"estimate US${estimate['total_cost_usd']} exceeds the "
                      f"US${max_cost_usd} ceiling")
    out_dir.mkdir(parents=True, exist_ok=True)
    req_path = out_dir / "requests.jsonl"
    req_path.write_bytes(b"".join(b + b"\n" for b in lines))
    record = {
        "script": "scripts/reverify_unparseable_rows.py build",
        "built_at": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "tier": TIER,
        "n_rows": len(rows),
        "requests": {"path": req_path.name, "sha256": sha256_file(req_path),
                     "bytes": req_path.stat().st_size,
                     "note": "each line is the leg's original request line, byte for "
                             "byte (key included)"},
        "estimate": estimate,
        "max_cost_usd": max_cost_usd,
        "legs": [{k: v for k, v in leg.items() if k != "usage_stats"}
                 for leg in leg_records],
        "rows": rows,
        "repairable_not_sent": repairable,
    }
    (out_dir / "build.json").write_text(json.dumps(record, indent=1) + "\n")
    return record


# ---------------------------------------------------------------------------
# lodge
# ---------------------------------------------------------------------------


def lodge(run_dir: Path, client: Any, max_cost_usd: float, *,
          resolve_model: Callable[[Any, str], str | None],
          preflight: Callable[..., Any], upload: Callable[..., str],
          submit: Callable[..., Any], poll: Callable[..., Any],
          retrieve: Callable[[Any, Any], list[dict]],
          state_name: Callable[[Any], str]) -> int:
    """Lodge the run's requests as ONE batch job and wait for it.

    The lifecycle functions are injected so the gates are testable without
    an API; :func:`main` passes ``lib_batch_api``'s.

    Args:
        run_dir: The run directory ``build`` wrote.
        client: A ``google.genai.Client``.
        max_cost_usd: The estimate's ceiling, re-checked here.
        resolve_model, preflight, upload, submit, poll, retrieve, state_name:
            The lifecycle functions.

    Returns:
        0 when the job SUCCEEDED and every key came back, 2 otherwise.

    Raises:
        Refused: Before any upload, when a gate fails.
    """
    jobs_path = run_dir / "batch_jobs.json"
    if jobs_path.exists():
        raise Refused(f"{jobs_path} exists: this run has lodged already, and a "
                      "second batch is a new approval")
    build_rec = json.loads((run_dir / "build.json").read_text())
    req_path = run_dir / build_rec["requests"]["path"]
    if sha256_file(req_path) != build_rec["requests"]["sha256"]:
        raise Refused(f"{req_path} has changed since build")
    keys = [json.loads(line)["key"] for line in req_path.read_text().splitlines()]
    if len(keys) != build_rec["n_rows"] or len(set(keys)) != len(keys):
        raise Refused(f"{req_path} holds {len(keys)} line(s) ({len(set(keys))} keys); "
                      f"build recorded {build_rec['n_rows']}")
    estimate = build_rec["estimate"]["total_cost_usd"]
    if estimate is None or estimate > max_cost_usd:
        raise Refused(f"estimate US${estimate} exceeds the US${max_cost_usd} ceiling")
    model = build_rec["model"]
    resolved = resolve_model(client, model)
    if resolved != model:
        raise Refused(f"model {model!r} resolves to {resolved!r}; the legs ran {model!r}")
    # No sweep: a sweep deletes other jobs' stale uploads, and this run may
    # delete only its own. Over budget is a refusal, not a clean-up.
    try:
        preflight(client, [req_path], log=logger, sweep=None)
    except Exception as exc:  # noqa: BLE001 - any preflight failure stops the lodge
        raise Refused(f"File API storage preflight: {exc}") from exc

    stamp = datetime.now(timezone.utc)
    record: dict[str, Any] = {
        "display_name": f"pv-verifier-reverify-{stamp:%Y%m%d-%H%M}",
        "model": model, "tier": TIER, "requests": req_path.name,
        "requests_sha256": build_rec["requests"]["sha256"], "n_requests": len(keys),
        "file": None, "job": None, "state": "not lodged",
    }

    def save() -> None:
        jobs_path.write_text(json.dumps(record, indent=1) + "\n")

    save()
    record["file"] = upload(client, req_path, record["display_name"])
    record["state"] = "uploaded"
    save()
    job = submit(client, model, record["file"], record["display_name"])
    record["job"] = getattr(job, "name", str(job))
    record["state"] = "lodged"
    record["lodged_at"] = datetime.now(timezone.utc).isoformat()
    save()
    print(f"Lodged {record['job']} ({len(keys)} requests, model {model})", flush=True)
    done = poll(client, record["job"])
    state = state_name(getattr(done, "state", ""))
    record["state"] = state
    record["terminal_at"] = datetime.now(timezone.utc).isoformat()
    dest = getattr(done, "dest", None)
    record["output_file"] = getattr(dest, "file_name", None) if dest else None
    save()
    rows: list[dict] = []
    if record["output_file"]:
        rows = retrieve(client, done)
        with open(run_dir / "batch_results.jsonl", "w") as fh:
            for row in rows:
                fh.write(json.dumps(row) + "\n")
    returned = {r.get("key") for r in rows if "error" not in r}
    missing = sorted(set(keys) - returned)
    record["n_results"] = len(rows)
    record["missing_or_errored"] = missing
    save()
    if state == "JOB_STATE_SUCCEEDED" and not missing:
        print(f"{MARKER_COMPLETE}: {len(rows)}/{len(keys)} rows, job {record['job']}",
              flush=True)
        return 0
    print(f"{MARKER_PARTIAL}: job {record['job']} ended {state}; {len(rows)} row(s) "
          f"returned, missing or errored: {missing}. Not re-sent: a resend needs a "
          "new approval.", flush=True)
    return 2


# ---------------------------------------------------------------------------
# book
# ---------------------------------------------------------------------------


def parse_new_response(text: str | None) -> tuple[dict[str, Any], str]:
    """Parse a new response as the leg's batch parser, then as the repair.

    Args:
        text: ``parts[0].text`` of the response.

    Returns:
        ``(verdict, method)``: the four verdict fields, and
        ``"json.loads"`` (the leg's batch parser) or
        ``"parse_response_with_repair"`` (the Stage 2 after-landing repair).

    Raises:
        ValueError: When neither parses, or the payload has no
            ``mound_probability`` in [0, 1]; the row is then not booked.
    """
    from scripts.lib_verifier import parse_verifier_results

    if text is None:
        raise ValueError("no response text")
    fake = {"k": {"response": {"candidates": [{"content": {"parts": [{"text": text}]}}]}}}
    parsed = parse_verifier_results(fake).get("k")
    if parsed and not is_parse_error(parsed):
        # parse_verifier_results defaults a missing probability to 0.0, so
        # confirm the payload really carried one (Stage 2 re-check, R2).
        raw = json.loads(text.replace("```json", "").replace("```", "").strip())
        from scripts.lib_verifier import _unwrap_verdict_payload

        if valid_probability(_unwrap_verdict_payload(raw).get("mound_probability")):
            return {f: parsed[f] for f in VERDICT_FIELDS}, "json.loads"
        raise ValueError("payload parses but has no mound_probability in [0, 1]")
    verdict = repair_text(text)  # raises ValueError when unrepairable
    return {f: verdict[f] for f in VERDICT_FIELDS}, "parse_response_with_repair"


def book(run_dir: Path, date_tag: str | None = None) -> int:
    """Merge the new responses into each leg's repaired copy.

    Args:
        run_dir: The run directory, holding ``build.json``,
            ``batch_jobs.json`` and ``batch_results.jsonl``.
        date_tag: Suffix of the per-leg record name (default: the job's
            terminal date).

    Returns:
        0 when every row was booked; 1 when any new response is again
        unparseable (those rows are not booked and not re-sent).

    Raises:
        Refused: When a repaired copy is missing, does not lack exactly
            this leg's rows, or already holds a re-verification record.
    """
    from scripts.lib_batch_api import aggregate_batch_usage
    from scripts.lib_cost import price_usage

    build_rec = json.loads((run_dir / "build.json").read_text())
    jobs = json.loads((run_dir / "batch_jobs.json").read_text())
    raw_path = run_dir / "batch_results.jsonl"
    raw = {json.loads(line)["key"]: json.loads(line)
           for line in raw_path.read_text().splitlines() if line.strip()}
    priced_at = (jobs.get("terminal_at") or datetime.now(timezone.utc).isoformat())[:10]
    tag = date_tag or priced_at
    rows_out: list[dict[str, Any]] = []
    unparseable: list[dict[str, Any]] = []
    by_leg: dict[str, list[dict[str, Any]]] = {}
    for row in build_rec["rows"]:
        key = row["key"]
        result = raw.get(key)
        text = _response_text(result or {})
        usage = aggregate_batch_usage([result] if result else [])
        cost = price_usage(usage, model=build_rec["model"], tier=TIER, at=priced_at,
                           tier_source="batch-api (reverify_unparseable_rows.py lodge)")
        out = {"leg": row["leg"], "key": key,
               "old_probability": row["booked"].get("mound_probability"),
               "old_reasoning": row["booked"].get("reasoning"),
               "original_response_text": row["original_response_text"],
               "new_response_text": text,
               "new_finish_reason": (((result or {}).get("response") or {})
                                     .get("candidates") or [{}])[0].get("finishReason"),
               "usage_metadata": ((result or {}).get("response") or {}).get("usageMetadata"),
               "cost_usd": cost["total_cost_usd"], "cost": cost}
        try:
            verdict, method = parse_new_response(text)
        except (ValueError, TypeError) as exc:
            out.update(new_probability=None, booked=False, parse_error=str(exc))
            unparseable.append(out)
        else:
            out.update(new_probability=verdict["mound_probability"], parse_method=method,
                       booked=True, verdict=verdict)
            by_leg.setdefault(row["leg"], []).append(out)
        rows_out.append(out)

    leg_records: list[dict[str, Any]] = []
    for leg in build_rec["legs"]:
        if not leg["keys"]:
            continue  # nothing was sent for this leg, so nothing to book
        leg_dir = Path(leg["leg"])
        if not leg_dir.is_absolute():
            leg_dir = PROJECT_ROOT / leg_dir
        rep_dir = leg_dir.with_name(leg_dir.name + "_repaired")
        rec_name = f"reverify-{tag}.json"
        probs_path = rep_dir / "probabilities.json"
        if not probs_path.exists():
            raise Refused(f"{rep_dir} has no probabilities.json: run "
                          "modality_bridge_stage2_checks.py repair on the leg first")
        if (rep_dir / rec_name).exists():
            raise Refused(f"{rep_dir / rec_name} exists: already booked")
        probs = json.loads(probs_path.read_text())
        leg_probs = json.loads((leg_dir / "probabilities.json").read_text())
        absent = sorted(set(leg_probs["results"]) - set(probs["results"]))
        if absent != sorted(leg["keys"]):
            raise Refused(f"{rep_dir} lacks {absent}, not this leg's re-sent rows "
                          f"{sorted(leg['keys'])}")
        before = sha256_file(probs_path)
        merged = by_leg.get(leg["leg"], [])
        for r in merged:
            probs["results"][r["key"]] = dict(r["verdict"])
        if "total_results" in probs:
            probs["total_results"] = len(probs["results"])
        probs["reverify"] = {
            "record": rec_name, "n_merged": len(merged),
            "keys": [r["key"] for r in merged],
            "not_booked": [u["key"] for u in unparseable if u["leg"] == leg["leg"]],
            "source": rel(run_dir),
        }
        probs_path.write_text(json.dumps(probs, indent=2) + "\n")
        leg_rec = {
            "script": "scripts/reverify_unparseable_rows.py book",
            "decision": "D55 (Q4), planning/pi-decisions-2026-09-20.md",
            "leg_dir": leg["leg"], "run_dir": rel(run_dir),
            "batch_job": jobs.get("job"), "model": build_rec["model"], "tier": TIER,
            "probabilities_sha256_before": before,
            "probabilities_sha256_after": sha256_file(probs_path),
            "complete": len(probs["results"]) == len(leg_probs["results"]),
            "rows": [{k: r[k] for k in ("key", "old_probability", "new_probability",
                                         "parse_method", "cost_usd")} for r in merged],
            "not_booked": [u["key"] for u in unparseable if u["leg"] == leg["leg"]],
            "note": "run.meta.json here is still the leg's byte copy; the calls' "
                    "usage and cost are in the run directory's record.json",
        }
        (rep_dir / rec_name).write_text(json.dumps(leg_rec, indent=1) + "\n")
        leg_records.append(leg_rec)

    total = sum(r["cost_usd"] or 0.0 for r in rows_out)
    record = {
        "script": "scripts/reverify_unparseable_rows.py book",
        "decision": "D55 (Q4), planning/pi-decisions-2026-09-20.md",
        "booked_at": datetime.now(timezone.utc).isoformat(),
        "batch_job": jobs.get("job"), "job_state": jobs.get("state"),
        "model": build_rec["model"], "tier": TIER, "priced_at": priced_at,
        "batch_results_sha256": sha256_file(raw_path),
        "n_rows": len(rows_out), "n_booked": len(rows_out) - len(unparseable),
        "n_unparseable_again": len(unparseable),
        "total_cost_usd": round(total, 6),
        "estimate_usd": build_rec["estimate"]["total_cost_usd"],
        "rows": rows_out, "legs": leg_records,
    }
    (run_dir / "record.json").write_text(json.dumps(record, indent=1) + "\n")
    for r in rows_out:
        new = "NOT BOOKED (unparseable again)" if not r["booked"] else r["new_probability"]
        print(f"  {r['leg'].rsplit('/', 1)[-1]} {r['key']}: {r['old_probability']} -> {new}"
              f"  (US${r['cost_usd']})")
    print(f"Total cost US${record['total_cost_usd']} (estimate "
          f"US${record['estimate_usd']})")
    if unparseable:
        print(f"{len(unparseable)} new response(s) unparseable again; not booked and "
              "NOT re-sent", file=sys.stderr)
        return 1
    return 0


# ---------------------------------------------------------------------------
# release
# ---------------------------------------------------------------------------


def release(run_dir: Path, client: Any, *, state_name: Callable[[Any], str],
            terminal: frozenset[str], delete: Callable[..., tuple[int, int]]) -> int:
    """Delete this job's own input and output files from the Files API.

    Args:
        run_dir: The run directory, whose ``batch_jobs.json`` names the files.
        client: A ``google.genai.Client``.
        state_name: ``lib_batch_api._get_state_name``.
        terminal: ``lib_batch_api._TERMINAL_STATES``.
        delete: ``lib_batch_api.cleanup_batch_files``.

    Returns:
        0 when both deletes went through, 1 otherwise.

    Raises:
        Refused: When the job is not terminal.
    """
    jobs_path = run_dir / "batch_jobs.json"
    rec = json.loads(jobs_path.read_text())
    job = client.batches.get(name=rec["job"])
    state = state_name(getattr(job, "state", ""))
    if state not in terminal:
        # A non-terminal job is still reading its input file.
        raise Refused(f"job {rec['job']} is {state}; its files are not released")
    names = [n for n in (rec.get("file"), rec.get("output_file")) if n]
    deleted, errors = delete(client, names, "reverify")
    rec["released"] = {"at": datetime.now(timezone.utc).isoformat(), "files": names,
                       "deleted": deleted, "errors": errors}
    jobs_path.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"Released {deleted} of {len(names)} file(s) ({errors} error(s))")
    return 0 if errors == 0 and deleted == len(names) else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _client() -> Any:
    """The API client, configured as ``run_pv.py``'s batch path configures it."""
    from google import genai

    from scripts.run_pv import _get_api_key

    return genai.Client(api_key=_get_api_key(), http_options={"api_version": "v1alpha"})


def main(argv: list[str] | None = None) -> int:
    """Run one subcommand.

    Returns:
        0 on success; 1 on a refusal, or (``book``) an unparseable new
        response; 2 when (``lodge``) the job did not fully succeed.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--leg", action="append", required=True,
                   help="LEG_DIR[=CROPS_DIR]; repeatable")
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--expect", type=int, required=True)
    b.add_argument("--max-cost-usd", type=float, required=True)
    b.add_argument("--requests-root", type=Path, default=None)
    b.add_argument("--crops-root", type=Path, default=None)
    lo = sub.add_parser("lodge")
    lo.add_argument("--run-dir", type=Path, required=True)
    lo.add_argument("--max-cost-usd", type=float, required=True)
    bk = sub.add_parser("book")
    bk.add_argument("--run-dir", type=Path, required=True)
    rl = sub.add_parser("release")
    rl.add_argument("--run-dir", type=Path, required=True)
    args = ap.parse_args(argv)

    try:
        if args.cmd == "build":
            rec = build([parse_leg_spec(s) for s in args.leg], args.out, args.expect,
                        args.max_cost_usd, args.requests_root, args.crops_root)
            for r in rec["rows"]:
                cc = r["rebuild_cross_check"]
                print(f"  {r['leg'].rsplit('/', 1)[-1]} {r['key']}: line "
                      f"{r['request_line_sha256'][:12]} from "
                      f"{Path(r['request_file']).name}; rebuild "
                      + ("identical" if cc.get("identical_parsed")
                         else f"DIFFERS {cc.get('differing_paths')}"
                         if cc.get("checked") else "not checked"))
            for r in rec["repairable_not_sent"]:
                print(f"  repairable, not sent: {r['leg'].rsplit('/', 1)[-1]} {r['key']} "
                      f"-> {r['repairs_to']}")
            print(f"BUILD OK: {rec['n_rows']} rows, model {rec['model']}, estimate "
                  f"US${rec['estimate']['total_cost_usd']} (list "
                  f"US${rec['estimate']['list_total_cost_usd']})")
            return 0
        if args.cmd == "lodge":
            from scripts import lib_batch_api as lba
            from scripts.run_pv import _resolve_model_name

            return lodge(args.run_dir, _client(), args.max_cost_usd,
                         resolve_model=_resolve_model_name,
                         preflight=lba.preflight_file_storage, upload=lba.upload_jsonl,
                         submit=lba.submit_batch_job, poll=lba.poll_batch_job,
                         retrieve=lba.retrieve_batch_results,
                         state_name=lba._get_state_name)
        if args.cmd == "book":
            return book(args.run_dir)
        from scripts import lib_batch_api as lba

        return release(args.run_dir, _client(), state_name=lba._get_state_name,
                       terminal=lba._TERMINAL_STATES, delete=lba.cleanup_batch_files)
    except Refused as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
