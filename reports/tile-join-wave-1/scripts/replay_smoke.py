#!/usr/bin/env python3
"""
Legacy determinism replays of the Wave 1 smoke cells (W1.0, steps 6–8).

For each smoke cell this script:

1. **Recovers the recipe** through the D22 fallback chain, using the
   existing ``scripts.rescore_tile_mcc_e81.recover_recipe`` (read-only), and
   resolves the detection files exactly as the scorer does
   (``evaluate_detections.find_detection_files``);
2. **Pins input identity**: the SHA-256 and git blob hash of every input
   file, compared with the blob hashes the evaluation recorded where it
   recorded any; the run order of replicated passes; the seed, iteration
   count, buffers, and join; and the environment;
3. **Replays** the existing scorer (``scripts/evaluate_detections.py`` at
   the data root's checkout, unchanged) under the cell's **recorded** rules
   (classification join as recorded, ``id`` where none is recorded, the
   only join that existed then), writing only to a scratch directory, and
   times it (wall clock, and child CPU time from ``resource``);
4. **Compares** the replay with the committed file: every interval, the
   tile block, coverage flags, and the whole ``summary`` and ``per_run``
   apart from fields that change on every run.

Nothing here computes a corrected (sheet-specific) score. A cell whose
replay differs is reported and left alone (spec W1.0, "Determinism").

Usage (zbook; cells run in parallel, at most 14 at once)::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python \\
        reports/tile-join-wave-1/scripts/replay_smoke.py \\
        --data-root ~/Code/map-reader-llm --scratch ~/scratch/wave1/w10/replay \\
        --workers 8 --out ~/scratch/wave1/w10/replay/replay.json

Created: 2026-11-18 (tile-join Wave 1, W1.0)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import resource
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

#: The eight smoke cells (spec § 6; cells 3–5 pinned in W1.0).
_KL = "results/k-ladder-2026-09-12/phase2/cells/"
_G37 = _KL + "gemini37-screen-2026-08-28__g37-text-"
SMOKE_CELLS: dict[str, str] = {
    "1": _KL + "pv-diag-384__pv-high-image-t0_3-n1-opmax/evaluation.json",
    "2": "results/55map-final-board-r2-2026-09-06/cells/A-N1-oracle/evaluation.json",
    "3": "results/paper-eval/phase2/512px-14buf-mcc/p2c-image-canonical/evaluation.json",
    "4": "results/grid-2026-08-18/conditions/g512_ov064/eval/evaluation.json",
    "5": "results/paper-eval/n1/384px-14buf-mcc/pro-rerun/pro-image-high-t-0-0/evaluation.json",
    "6": _G37 + "k1-verified-carried-p0_10-k1/evaluation.json",
    "7": _G37 + "k1-verified-opmax/evaluation.json",
    "8": _G37 + "k3-verified-opmax/evaluation.json",
}
#: Fields that differ on every run and are excluded from the comparison.
VOLATILE_TOP = {"timestamp", "_metadata"}


def blob_hash(data: bytes) -> str:
    """Git blob hash of file content (``git hash-object``)."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def resolve_inputs(root: Path, meta: dict[str, Any]) -> tuple[dict, list[Path]]:
    """Recover the recipe and the ordered detection files, with existing code.

    Args:
        root: Data root (the checkout the recorded paths are relative to).
        meta: The evaluation's ``_metadata``.

    Returns:
        ``(cli_args, detection_files)``.
    """
    sys.path.insert(0, str(root))
    from scripts.evaluate_detections import find_detection_files  # noqa: PLC0415
    from scripts.rescore_tile_mcc_e81 import recover_recipe  # noqa: PLC0415

    cli = recover_recipe(meta)
    declared = meta.get("cli_args") or {}
    recovered_source = not (declared.get("detections") or declared.get("detections_dir"))
    if cli.get("detections_dir"):
        glob_pattern = None if recovered_source else cli.get("glob")
        files = find_detection_files(root / cli["detections_dir"], glob_pattern)
    else:
        listed = cli["detections"] if isinstance(cli["detections"], list) else [cli["detections"]]
        files = [root / p for p in listed]
    return cli, files


def command(root: Path, cli: dict[str, Any], out_dir: Path) -> list[str]:
    """The scorer invocation that replays the recorded recipe.

    Args:
        root: Data root.
        cli: Recovered recipe.
        out_dir: Scratch output directory.

    Returns:
        argv.
    """
    argv = [str(root / ".venv/bin/python"), "scripts/evaluate_detections.py"]
    if cli.get("detections_dir"):
        argv += ["--detections-dir", cli["detections_dir"]]
        declared_glob = cli.get("glob")
        if declared_glob:
            argv += ["--glob", declared_glob]
    else:
        listed = cli["detections"] if isinstance(cli["detections"], list) else [cli["detections"]]
        argv += ["--detections", *listed]
    argv += ["--buffers", *[str(b) for b in cli["buffers"]],
             "--ground-truth", cli["ground_truth"], "--bounds", cli["bounds"],
             "--bootstrap", str(cli.get("bootstrap") or 1000),
             "--seed", str(cli.get("seed")),
             "--output-dir", str(out_dir),
             "--tile-join", cli.get("tile_join") or "id",
             "--workers", str(cli.get("workers") or 1)]
    if cli.get("label"):
        argv += ["--label", cli["label"]]
    if cli.get("mcc"):
        argv.append("--mcc")
    if cli.get("require_clean_inputs"):
        argv.append("--require-clean-inputs")
    return argv


def diff(a: Any, b: Any, path: str = "") -> list[str]:
    """Paths at which two JSON values differ (exact equality).

    Args:
        a: Committed value.
        b: Replayed value.
        path: Path prefix.

    Returns:
        Differing paths with both values, abbreviated.
    """
    if isinstance(a, dict) and isinstance(b, dict):
        out = []
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                where = "missing in committed" if k not in a else "missing in replay"
                out.append(f"{path}/{k}: {where}")
            else:
                out += diff(a[k], b[k], f"{path}/{k}")
        return out
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return [f"{path}: length {len(a)} vs {len(b)}"]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, f"{path}[{i}]")
        return out
    return [] if a == b else [f"{path}: {json.dumps(a)[:80]} vs {json.dumps(b)[:80]}"]


def replay(cell: str, rel: str, root: Path, scratch: Path) -> dict[str, Any]:
    """Recover, pin, replay, time, and compare one smoke cell.

    Args:
        cell: Smoke-cell number.
        rel: Committed evaluation path.
        root: Data root.
        scratch: Scratch root.

    Returns:
        The cell's record.
    """
    committed = json.loads((root / rel).read_text())
    meta = committed.get("_metadata") or {}
    cli, files = resolve_inputs(root, meta)
    recorded_blobs = ((meta.get("input_git_state") or {}).get("blob_hashes") or {})
    inputs = []
    for p in [*files, root / cli["ground_truth"], root / cli["bounds"]]:
        data = p.read_bytes()
        relp = str(p.relative_to(root))
        bh = blob_hash(data)
        inputs.append({"path": relp, "sha256": hashlib.sha256(data).hexdigest(),
                       "git_blob": bh, "recorded_git_blob": recorded_blobs.get(relp),
                       "matches_recorded": (None if relp not in recorded_blobs
                                            else recorded_blobs[relp] == bh)})
    out_dir = scratch / f"cell{cell}"
    out_dir.mkdir(parents=True, exist_ok=True)
    argv = command(root, cli, out_dir)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    start = time.perf_counter()
    log_path = out_dir / "replay.log"
    with log_path.open("w") as log:
        child = subprocess.Popen(argv, cwd=root, env=env, stdout=log,
                                 stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
        _, status, usage = os.wait4(child.pid, 0)
    wall = time.perf_counter() - start
    returncode = os.waitstatus_to_exitcode(status)
    log_text = log_path.read_text()
    record: dict[str, Any] = {
        "cell": cell, "committed": rel, "argv": argv[1:], "returncode": returncode,
        "wall_s": round(wall, 2), "cpu_s": round(usage.ru_utime + usage.ru_stime, 2),
        "max_rss_mb": round(usage.ru_maxrss / 1024, 1), "recipe": cli,
        "n_detection_files": len(files),
        "run_order": [str(f.relative_to(root)) for f in files], "inputs": inputs,
        "recorded_join": (committed.get("summary", {}).get("tile_classification") or {}).get(
            "tile_join") or (meta.get("cli_args") or {}).get("tile_join"),
        "seed": cli.get("seed"), "n_iterations": cli.get("bootstrap"),
        "buffers": cli.get("buffers"),
        "committed_generated_at": meta.get("generated_at_utc"),
        "committed_script_commit": meta.get("script_git_commit"),
    }
    produced = out_dir / "evaluation.json"
    if returncode != 0 or not produced.exists():
        record["outcome"] = "replay-failed"
        record["log_tail"] = log_text[-2000:]
        return record
    replayed = json.loads(produced.read_text())
    a = {k: v for k, v in committed.items() if k not in VOLATILE_TOP}
    b = {k: v for k, v in replayed.items() if k not in VOLATILE_TOP}
    differences = diff(a, b)
    boot_a = (committed.get("_metadata") or {}).get("bootstrap")
    boot_b = (replayed.get("_metadata") or {}).get("bootstrap")
    record["differences"] = differences[:200]
    record["n_differences"] = len(differences)
    record["bootstrap_block_equal"] = boot_a == boot_b
    record["interval_differences"] = [d for d in differences if "_ci_" in d or "/ci_" in d]
    record["outcome"] = "reproduces" if not differences else "differs"
    withheld = (replayed.get("summary") or {}).get("tile_join_withheld")
    record["replay_withheld_reason"] = withheld.get("reason") if withheld else None
    return record


def main() -> None:
    """Replay every smoke cell in parallel and write the records."""
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cells", nargs="*", default=sorted(SMOKE_CELLS))
    args = parser.parse_args()
    start = time.perf_counter()
    cpu0 = resource.getrusage(resource.RUSAGE_CHILDREN)
    with ThreadPoolExecutor(max_workers=min(args.workers, 14)) as pool:
        records = list(pool.map(
            lambda c: replay(c, SMOKE_CELLS[c], args.data_root, args.scratch), args.cells))
    cpu1 = resource.getrusage(resource.RUSAGE_CHILDREN)
    env = {"python": platform.python_version(), "platform": platform.platform(),
           "data_root_head": subprocess.run(["git", "rev-parse", "HEAD"], cwd=args.data_root,
                                            capture_output=True, text=True).stdout.strip()}
    try:
        import numpy  # noqa: PLC0415
        import scipy  # noqa: PLC0415
        env.update(numpy=numpy.__version__, scipy=scipy.__version__)
    except ImportError:
        pass
    out = {"environment": env, "total_wall_s": round(time.perf_counter() - start, 2),
           "total_child_cpu_s": round((cpu1.ru_utime + cpu1.ru_stime)
                                      - (cpu0.ru_utime + cpu0.ru_stime), 2),
           "cells": records}
    args.out.write_text(json.dumps(out, indent=1, default=str) + "\n")
    for r in records:
        print(r["cell"], r["outcome"], r.get("n_differences"), r["wall_s"],
              r.get("cpu_s"), r.get("replay_withheld_reason"))


if __name__ == "__main__":
    main()
