#!/usr/bin/env python3
"""
Generate 14-buffer + MCC re-score worklists for the Era-1 phase3 runs.
=====================================================================

Emits two ``scripts/rescore_conditions.py`` worklists by globbing the consensus
GeoJSONs on disk (so it must run *after* the consensus has been built /
materialised — see ``build_phase3_subpool_consensus.py`` and
``materialise_phase3c_consensus.py``):

1. **phase3-consensus** (file-mode) — every threshold GeoJSON of every
   (cell × N) sub-pool for ``retest-phase3a`` / ``-high`` / ``-replication``:
   the existing full N=30 ``consensus/`` plus the regenerated ``consensus-n5/``
   and ``consensus-n10/``. One worklist entry per single consensus file.

2. **phase3c-diversity** (dir-mode replicate-mean) — one entry per
   (track × H9 condition × threshold), globbing the 5 per-replication GeoJSONs
   so ``evaluate_detections.py`` scores each and averages (the phase2 replicate
   pattern). H9's condition-level metric is the mean over its 5 replications.

All entries score against the standard Era-1 scope: 340-tile
``full_evaluation_bounds.geojson`` + the ``mounds-reference.geojson`` curator
GT, at the 14 uniform buffers + MCC (the project standard since 2026-05-31).

Usage
-----
    # Preview counts only
    python scripts/build_phase3_rescore_worklists.py --dry-run

    # Write both worklists
    python scripts/build_phase3_rescore_worklists.py

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-06-07
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

BOUNDS = "inputs/vectors/bounds/full_evaluation_bounds.geojson"
GROUND_TRUTH = "inputs/vectors/references/mounds-reference.geojson"

RESCORE_ROOT = "results/rescore-2026-06-07"
WORKLIST_DIR = REPO_ROOT / "planning" / "rescore-worklists"

# Cells for the file-mode (phase3a-family) sub-pools — must match
# build_phase3_subpool_consensus.CELLS. Each cell has consensus/ (N=30) plus,
# after the sub-pool build, consensus-n5/ and consensus-n10/.
PHASE3A_CELLS: dict[str, list[str]] = {
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

# N -> consensus subdir name.
N_SUBDIR = {5: "consensus-n5", 10: "consensus-n10", 30: "consensus"}

# phase3c diversity-pool root (materialise_phase3c_consensus output) and the
# per-track H9 conditions.
PHASE3C_ROOT = "outputs/retest/phase3c/diversity-consensus"
PHASE3C_CONDITIONS = {
    "track1-image": ["A", "B", "C", "D", "E"],
    "track2-text": ["A", "B", "D", "E"],
}


def _cell_slug(cell: str) -> str:
    """Turn an output cell path into a flat, filesystem-safe slug.

    e.g. ``outputs/retest/phase3a/track2-text/T0.3`` ->
    ``phase3a__track2-text__T0.3``.
    """
    rel = cell.replace("outputs/retest/", "")
    return rel.replace("/", "__")


def _threshold_of(geojson: Path) -> int:
    """Extract the integer vote threshold from a consensus_t<t>.geojson name."""
    m = re.search(r"consensus_t(\d+)\.geojson$", geojson.name)
    return int(m.group(1)) if m else -1


def build_phase3a_entries() -> list[dict]:
    """File-mode entries: every threshold GeoJSON of every (cell × N) sub-pool."""
    entries: list[dict] = []
    for cells in PHASE3A_CELLS.values():
        for cell in cells:
            slug = _cell_slug(cell)
            for n, subdir in sorted(N_SUBDIR.items()):
                cons_dir = REPO_ROOT / cell / subdir
                geojsons = sorted(
                    cons_dir.glob("consensus_t*.geojson"),
                    key=_threshold_of,
                )
                for gj in geojsons:
                    t = _threshold_of(gj)
                    label = f"{slug}__n{n}__t{t}"
                    entries.append({
                        "label": label,
                        "detections": str(gj.relative_to(REPO_ROOT)),
                        "bounds": BOUNDS,
                        "ground_truth": GROUND_TRUTH,
                        "output_dir": f"{RESCORE_ROOT}/phase3/{label}",
                    })
    return entries


def build_phase3c_entries() -> list[dict]:
    """Dir-mode replicate-mean entries: one per (track × condition × threshold)."""
    entries: list[dict] = []
    for track, conditions in PHASE3C_CONDITIONS.items():
        for cond in conditions:
            cond_dir = REPO_ROOT / PHASE3C_ROOT / track / cond
            # Discover thresholds present (replication_1 is representative).
            rep1 = cond_dir / "replication_1"
            thresholds = sorted(
                _threshold_of(p) for p in rep1.glob("consensus_t*.geojson")
            )
            n_reps = len(list(cond_dir.glob("replication_*")))
            for t in thresholds:
                label = f"phase3c__{track}__{cond}__t{t}"
                entries.append({
                    "label": label,
                    "detections_dir": f"{PHASE3C_ROOT}/{track}/{cond}",
                    "glob": f"replication_*/consensus_t{t}.geojson",
                    "replicates": n_reps,
                    "bounds": BOUNDS,
                    "ground_truth": GROUND_TRUTH,
                    "output_dir": f"{RESCORE_ROOT}/phase3c/{label}",
                })
    return entries


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate phase3 14-buf+MCC re-score worklists."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report counts only; write nothing.",
    )
    args = parser.parse_args(argv)

    p3a = build_phase3a_entries()
    p3c = build_phase3c_entries()

    print(f"phase3-consensus (file-mode): {len(p3a)} entries")
    print(f"phase3c-diversity (dir-mode): {len(p3c)} entries "
          f"({sum(e['replicates'] for e in p3c)} replicate scorings)")

    if args.dry_run:
        print("\nDRY-RUN — no worklists written.")
        return 0

    WORKLIST_DIR.mkdir(parents=True, exist_ok=True)
    p3a_path = WORKLIST_DIR / "phase3-consensus-14buf-mcc-2026-06-07.json"
    p3c_path = WORKLIST_DIR / "phase3c-diversity-14buf-mcc-2026-06-07.json"
    p3a_path.write_text(json.dumps({
        "_comment": "phase3a / -high / -replication consensus sweep, all "
        "N (5/10/30) x all vote thresholds, 14-buffer + MCC, Era-1 340-tile "
        "bounds + curator GT. Generated by build_phase3_rescore_worklists.py.",
        "entries": p3a,
    }, indent=2))
    p3c_path.write_text(json.dumps({
        "_comment": "phase3c H9 diversity-pool consensus, per (track x "
        "condition x threshold) replicate-mean over 5 replications, 14-buffer "
        "+ MCC, Era-1 340-tile bounds + curator GT. Generated by "
        "build_phase3_rescore_worklists.py.",
        "entries": p3c,
    }, indent=2))
    print(f"\nWrote {p3a_path.relative_to(REPO_ROOT)}")
    print(f"Wrote {p3c_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
