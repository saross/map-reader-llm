#!/usr/bin/env python3
"""Re-scoring harness for the 3b standardisation campaign.

Re-scores a worklist of conditions through the project-standard scorer
(``scripts/evaluate_detections.py``) at the **14 uniform buffers** decided
2026-05-31, with ``--mcc`` and the standard BCa bootstrap (10 000, seed 42), so
every condition gets a uniform, current, MCC-bearing ``evaluation.json``. This is
the "prefer re-scoring to standardise" half of the methodology audit (memory
``2026-05-31-e45dad98a906``, Obs 330). It is **evaluation-only — NO detection API
calls**.

The worklist is a JSON file ``{"entries": [{label, <input>, bounds,
ground_truth, output_dir}, ...]}`` — populated from the per-run decomposition
(the conditions), NOT from every materialised geojson (most of which are sweep /
pass intermediates, not conditions).

Each entry selects its detections with **exactly one** of two input grains,
mirroring ``evaluate_detections.py``'s own mutually-exclusive input group:

* ``detections`` — a single geojson path, *or a list of paths* forwarded to
  ``--detections`` (multiple files are treated as independent replicate runs of
  one condition, producing a replicate-mean summary).
* ``detections_dir`` (+ optional ``glob``; with no glob, ``evaluate_detections.py``
  resolves the pool through ``scripts/lib_detection_paths.py``, which expands BOTH
  per-pass naming conventions — the old batch-only default silently under-read any
  pool holding real-time passes, defect D6)
  — a condition directory whose ``run_*`` subdirs are each a replicate. This is
  the grain the Era-1 phase2 retests need (one condition = K passes under
  ``<condition>/run_K/``); an optional ``replicates`` hint (default 1) keeps the
  dry-run cost estimate honest without a filesystem walk.

Compute note (heavy-compute policy): run on sapphire/zbook, never amd-tower. The
55-map conditions (8 541 tiles) cost ~7 min and ~2 GB RAM EACH — RAM caps their
concurrency; the 4-map conditions are ~26 s / ~0.3 GB and parallelise freely.

Usage:
    # default: DRY-RUN — print the plan + the time/RAM estimate, run nothing
    python scripts/rescore_conditions.py --worklist worklist.json --workers 8

    # actually run (on zbook), 8 workers
    python scripts/rescore_conditions.py --worklist worklist.json --workers 8 --execute
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Pin every worker to ONE thread. Each evaluate_detections.py is CPU-bound (scipy
#: BCa bootstrap); without this, 16 concurrent processes each spawn BLAS threads and
#: oversubscribe the cores, inflating per-condition time. One thread per process →
#: clean N-way scaling across the 16 cores.
THREAD_ENV = {
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "VECLIB_MAXIMUM_THREADS": "1",
}

#: The 14 uniform buffers (metres), standard for ALL runs as of 2026-05-31:
#: a fine 5-50 m core (5 m steps) plus an extended 75-150 m tail (saturation /
#: cross-corpus comparison). One-to-one Hungarian matching makes the extended
#: buffers safe (they relax tolerance and F1 saturates; no cross-matching).
BUFFERS_STANDARD: list[int] = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 125, 150]

#: Standard bootstrap parameters (match every existing standard eval).
BOOTSTRAP_ITERS = 10000
BOOTSTRAP_SEED = 42

#: Empirical per-condition cost model (measured 2026-05-31, amd-tower; zbook may
#: differ). Cost ≈ fixed + per_buffer × n_buffers, linear in buffers (the BCa
#: bootstrap runs inside the per-buffer loop). Two regimes by tile count.
#:   4-map (327/487 tiles): 1 buf 5.7 s, 2 buf 7.2 s → per_buffer 1.55 s, fixed 4.1 s.
#:   55-map (8 541 tiles):  1 buf 60.7 s; per_buffer scales ~17× with tiles → ~27 s,
#:                          fixed ~34 s (extrapolated from one probe — refine on zbook).
COST = {
    "4map": {"fixed_s": 4.1, "per_buffer_s": 1.55, "ram_gb": 0.3},
    "55map": {"fixed_s": 34.0, "per_buffer_s": 27.0, "ram_gb": 2.1},
}


def _regime(bounds: str) -> str:
    """Classify a condition's cost regime from its bounds path (tile-count proxy)."""
    return "55map" if "55maps" in bounds else "4map"


def _entry_cost_s(bounds: str, n_buffers: int) -> float:
    """Estimated wall-clock seconds for one *single-replicate* condition."""
    c = COST[_regime(bounds)]
    return c["fixed_s"] + c["per_buffer_s"] * n_buffers


def _replicate_count(entry: dict) -> int:
    """Replicate (run) count for cost estimation.

    ``evaluate_detections.py`` scores each replicate before averaging, so a
    K-replicate condition costs ~K× a single file. The true count for a
    ``detections_dir`` entry needs a directory walk; the optional ``replicates``
    hint (default 1) keeps the dry-run estimate honest without filesystem I/O.

    Args:
        entry: A worklist entry dict.

    Returns:
        The replicate count: the explicit list length for a multi-file
        ``detections`` entry, the ``replicates`` hint for a ``detections_dir``
        entry, else 1.
    """
    if "detections_dir" in entry:
        return max(1, int(entry.get("replicates", 1)))
    det = entry.get("detections")
    return len(det) if isinstance(det, list) else 1


def _input_args(entry: dict) -> list[str]:
    """Resolve the mutually-exclusive input selector for one worklist entry.

    Returns the ``--detections`` / ``--detections-dir`` (+ ``--glob``) argv
    fragment for ``evaluate_detections.py``. Exactly one of ``detections`` /
    ``detections_dir`` must be present; raising here (rather than letting the
    subprocess fail) gives a worklist-level error naming the offending entry.

    Args:
        entry: A worklist entry dict.

    Returns:
        The input-selector portion of the evaluate_detections.py command.

    Raises:
        ValueError: If neither or both input keys are present.
    """
    has_files = "detections" in entry
    has_dir = "detections_dir" in entry
    if has_files == has_dir:
        which = "both" if has_files else "neither"
        raise ValueError(
            f"worklist entry {entry.get('label', '?')!r} must set exactly one of "
            f"'detections' or 'detections_dir' (got {which})"
        )
    if has_dir:
        selector = ["--detections-dir", str(entry["detections_dir"])]
        glob = entry.get("glob")
        if glob:
            selector += ["--glob", str(glob)]
        return selector
    det = entry["detections"]
    paths = det if isinstance(det, list) else [det]
    return ["--detections", *(str(p) for p in paths)]


def _eval_command(entry: dict) -> list[str]:
    """Build the evaluate_detections.py command for one worklist entry."""
    return [
        sys.executable, str(REPO_ROOT / "scripts" / "evaluate_detections.py"),
        *_input_args(entry),
        "--bounds", str(entry["bounds"]),
        "--ground-truth", str(entry["ground_truth"]),
        "--buffers", *[str(b) for b in BUFFERS_STANDARD],
        "--bootstrap", str(BOOTSTRAP_ITERS),
        "--seed", str(BOOTSTRAP_SEED),
        "--mcc",
        "--output-dir", str(entry["output_dir"]),
    ]


def estimate(entries: list[dict], workers: int, ram_gb: float = 16.0) -> dict:
    """Serial + parallel wall-clock estimate, RAM-aware (55-map caps concurrency).

    55-map conditions take ~2 GB each, so their concurrency is capped by ``ram_gb``,
    not by ``workers``. The parallel figure sums the 4-map and 55-map phase estimates
    (conservative — in the shared pool they partly overlap).
    """
    n_buf = len(BUFFERS_STANDARD)
    by_regime: dict[str, list[float]] = {"4map": [], "55map": []}
    for e in entries:
        cost = _entry_cost_s(e["bounds"], n_buf) * _replicate_count(e)
        by_regime[_regime(e["bounds"])].append(cost)
    serial_s = sum(sum(v) for v in by_regime.values())
    workers_55 = min(workers, max(1, int(ram_gb // COST["55map"]["ram_gb"])))
    par_4 = sum(by_regime["4map"]) / max(1, workers)
    par_55 = sum(by_regime["55map"]) / workers_55
    return {
        "n_entries": len(entries),
        "n_4map": len(by_regime["4map"]),
        "n_55map": len(by_regime["55map"]),
        "serial_minutes": round(serial_s / 60, 1),
        "parallel_minutes": round((par_4 + par_55) / 60, 1),
        "workers": workers,
        "workers_55": workers_55,
    }


def run_entry(entry: dict) -> tuple[str, int]:
    """Execute one re-score (single-threaded); return ``(label, returncode)``."""
    env = {**os.environ, **THREAD_ENV}
    proc = subprocess.run(_eval_command(entry), cwd=REPO_ROOT,
                          capture_output=True, text=True, env=env)
    fallback = entry.get("detections") or entry.get("detections_dir") or "?"
    label = entry.get("label") or (
        str(fallback[0]) if isinstance(fallback, list) else str(fallback)
    )
    return label, proc.returncode


def main(argv: list[str] | None = None) -> int:
    """Entry point. Dry-run by default (prints the plan + estimate); --execute to run."""
    parser = argparse.ArgumentParser(description="Re-score conditions at 14 uniform buffers (3b).")
    parser.add_argument("--worklist", type=Path, required=True,
                        help="JSON: {entries:[{label, detections|detections_dir, "
                             "bounds, ground_truth, output_dir}]} (see module docstring)")
    parser.add_argument("--workers", type=int, default=8, help="Concurrent conditions (default 8).")
    parser.add_argument("--ram-gb", type=float, default=16.0,
                        help="Available RAM (GB) — caps 55-map concurrency (~2 GB each).")
    parser.add_argument("--execute", action="store_true",
                        help="Actually run (omit for a dry-run plan + estimate). zbook only.")
    args = parser.parse_args(argv)

    entries = json.loads(args.worklist.read_text(encoding="utf-8")).get("entries", [])
    if not entries:
        print(f"No entries in {args.worklist}.", file=sys.stderr)
        return 2

    est = estimate(entries, args.workers, args.ram_gb)
    print(f"Buffers: {BUFFERS_STANDARD}  ({len(BUFFERS_STANDARD)} buffers, "
          f"bootstrap {BOOTSTRAP_ITERS} seed {BOOTSTRAP_SEED}, +MCC)")
    print(f"Worklist: {est['n_entries']} conditions "
          f"({est['n_4map']} 4-map, {est['n_55map']} 55-map)")
    print(f"Estimated wall-clock: serial ~{est['serial_minutes']} min · "
          f"parallel ~{est['parallel_minutes']} min "
          f"(4-map @{args.workers}, 55-map @{est['workers_55']} workers, {args.ram_gb:.0f} GB RAM)")

    if not args.execute:
        print("\nDRY-RUN — no scoring performed. Re-run with --execute (on zbook) to score.")
        for e in entries[:3]:
            print("  e.g. " + " ".join(_eval_command(e)))
        if len(entries) > 3:
            print(f"  … and {len(entries) - 3} more")
        return 0

    print(f"\nEXECUTING {len(entries)} re-scores at {args.workers} workers …")
    failures = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for label, rc in pool.map(run_entry, entries):
            status = "ok" if rc == 0 else f"FAILED (rc={rc})"
            print(f"  [{status}] {label}")
            failures += rc != 0
    print(f"\nDone: {len(entries) - failures} ok, {failures} failed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
