#!/usr/bin/env python3
"""
Build N=5 / N=10 sub-pool consensus GeoJSONs for the Era-1 phase3 runs.
======================================================================

The Era-1 phase3 consensus sweeps (``retest-phase3a``, ``retest-phase3a-high``,
``retest-phase3a-replication``) materialised only the **full N=30** consensus
GeoJSONs on disk (``<cell>/consensus/consensus_t1..t30.geojson``). The N=5 and
N=10 rows in the published F1-only sweep CSVs
(``results/retest/phase3a-consensus/**/consensus-sweep-results.csv``) were
computed in-memory by ``analyse_consensus_sweep.py`` and never written out.

To decompose these runs into the manifest at the comprehensive (per-N) grain we
need the N=5 / N=10 consensus GeoJSONs on disk so they can be re-scored at the
14-buffer + MCC (Matthews Correlation Coefficient) standard, exactly as the
pv-diag-384 consensus sweep was (Session 102).

Faithfulness
------------
This driver is a thin orchestrator over ``scripts/merge_passes.py --sweep``,
the *same* canonical consensus builder that produced the on-disk N=30 GeoJSONs
(via ``build_all_consensus.py``). The N sub-pool is selected with
``--passes 1,..,N`` which restricts to ``run_1..run_N`` *by parsed run number*
(``merge_passes.load_pass_detections``) — i.e. the **first N passes**, the
first-N sub-pool rule (registered in §3.8 for N=5/N=10 within K=10; sub-pooling K=30 is an unregistered extension, D17 audit U2) also used by
``analyse_consensus_sweep.py`` (its ``rn <= pool_size`` filter). Using the one
clustering implementation across all N keeps every minted condition internally
comparable; the 14-buffer re-score is the authoritative measurement and
supersedes the older F1-only sweep numbers (the pv-diag-384 precedent).

Outputs
-------
For each cell ``<input_dir>`` and each N in {5, 10}::

    <input_dir>/consensus-n5/consensus_t1..t5.geojson   + voting_summary.json
    <input_dir>/consensus-n10/consensus_t1..t10.geojson + voting_summary.json

(The existing full pool stays at ``<input_dir>/consensus/``; mirrors the
``consensus`` / ``consensus-n5`` / ``consensus-n10`` naming pv-diag-384 used.)

Usage
-----
    # Dry run — preview the merge_passes invocations, build nothing
    python scripts/build_phase3_subpool_consensus.py

    # Build everything (run on zbook / sapphire, not amd-tower)
    python scripts/build_phase3_subpool_consensus.py --execute

    # Restrict to one run
    python scripts/build_phase3_subpool_consensus.py --execute \\
        --run retest-phase3a-replication

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-06-07
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ── Cell inventory ────────────────────────────────────────────────────
# run_id -> list of cell input directories (each holding run_1..run_30/).
# Era-1, 340-tile, 512 px. phase3a-high image track never ran (text only).
CELLS: dict[str, list[str]] = {
    "retest-phase3a": [
        "outputs/retest/phase3a/track1-image/T0.3",
        "outputs/retest/phase3a/track1-image/T0.7",
        "outputs/retest/phase3a/track1-image/T1.0",
        "outputs/retest/phase3a/track2-text/T0.3",
        "outputs/retest/phase3a/track2-text/T0.7",
        "outputs/retest/phase3a/track2-text/T1.0",
    ],
    "retest-phase3a-high": [
        "outputs/retest/phase3a-high/track2-text/T0.3",
        "outputs/retest/phase3a-high/track2-text/T0.7",
        "outputs/retest/phase3a-high/track2-text/T1.0",
    ],
    "retest-phase3a-replication": [
        "outputs/retest/phase3a-replication/high",
        "outputs/retest/phase3a-replication/minimal",
    ],
}

N_VALUES = (5, 10)


def build_cell(input_dir: Path, n: int, execute: bool) -> tuple[bool, str]:
    """Shell out to merge_passes.py --sweep for one cell at sub-pool size N.

    Args:
        input_dir: Cell directory containing run_1..run_30/ subdirectories.
        n: Sub-pool size (first N passes, i.e. run_1..run_N).
        execute: When False, print the command without running it.

    Returns:
        (ok, message) — ok is True on success (or dry-run), message describes
        the outcome.
    """
    output_dir = input_dir / f"consensus-n{n}"
    passes = ",".join(str(i) for i in range(1, n + 1))
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "merge_passes.py"),
        "--input-dir",
        str(input_dir),
        "--passes",
        passes,
        "--output-dir",
        str(output_dir),
        "--sweep",
    ]
    if not execute:
        return True, "DRY-RUN  " + " ".join(cmd)

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return False, f"FAILED   {output_dir}\n{result.stderr.strip()[-500:]}"
    n_built = len(list(output_dir.glob("consensus_t*.geojson")))
    if n_built != n:
        # A sub-pool of N passes must yield exactly consensus_t1..tN. A mismatch
        # means either stale files from an earlier run survive (merge_passes
        # writes with exist_ok=True and does NOT purge the dir) or fewer than N
        # passes loaded — both contaminate the downstream re-score worklist.
        # Flag it rather than silently accepting a wrong file count.
        return False, (
            f"FAILED   {output_dir}  (expected {n} threshold GeoJSONs, found "
            f"{n_built} — stale files or short pool; clean the dir and re-run)"
        )
    return True, f"OK       {output_dir}  ({n_built} threshold GeoJSONs)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build N=5/N=10 sub-pool consensus GeoJSONs for the "
        "Era-1 phase3 runs (dry-run by default)."
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually build (default is dry-run). Run on zbook/sapphire.",
    )
    parser.add_argument(
        "--run",
        choices=sorted(CELLS),
        help="Restrict to a single run_id (default: all three).",
    )
    args = parser.parse_args(argv)

    runs = [args.run] if args.run else sorted(CELLS)
    n_ok = n_fail = 0
    for run_id in runs:
        print(f"\n=== {run_id} ===")
        for cell in CELLS[run_id]:
            input_dir = REPO_ROOT / cell
            if not input_dir.is_dir():
                print(f"  MISSING input dir: {cell}")
                n_fail += 1
                continue
            for n in N_VALUES:
                ok, msg = build_cell(input_dir, n, args.execute)
                print(f"  {msg}")
                n_ok += int(ok)
                n_fail += int(not ok)

    print(f"\nDone: {n_ok} ok, {n_fail} failed.")
    if not args.execute:
        print("DRY-RUN — nothing built. Re-run with --execute "
              "(on zbook/sapphire, never amd-tower).")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
