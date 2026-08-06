#!/usr/bin/env python3
"""Verify the student ground truth differs from the original only as sanctioned.

Ruling 19 treats ``student-mounds-55maps.geojson`` (4,770 features) as
immutable and ``-reviewed.geojson`` (4,746) as its corrected descendant,
recording the derivation arithmetically as ``4770 - 52 + 28 = 4746``. W7-R2
showed that correct arithmetic is not the same as correct provenance: 2 of
those 28 additions turned out to be model detections, which the arithmetic
could never have revealed.

This audit asks the questions counting cannot:

1. **Is the original itself unchanged?** One commit in its history, and the
   working copy matching that commit, is the whole basis for calling it
   immutable.
2. **Is every REMOVED point accounted for?** Each should be one half of a
   merged pair, not a silent deletion.
3. **Is every ADDED point accounted for?** Each should be a merged centroid
   sitting between its two superseded originals — anything else is an
   incursion.
4. **Did any SURVIVING point move?** A point present in both layers should be
   byte-identical in position. Silent repositioning would be invisible to any
   count-based check.
5. **Did any SURVIVING point change classification?** ``MapSymbol``,
   ``FeatureType`` and ``source_map`` should be untouched. Reclassification at
   import is legitimate curation; reclassification afterwards is drift.

Exit status is non-zero if anything is unaccounted for, so this can gate.

Usage::

    .venv/bin/python scripts/audit_student_gt_integrity.py
    .venv/bin/python scripts/audit_student_gt_integrity.py --layer gs

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_TARGET_CRS = "EPSG:32635"

# Below this, two positions are the same point. Far under the ~5 m pixel and
# far above floating-point noise from a CRS round-trip.
_IDENTITY_TOL_M = 0.01

# A merged centroid should sit between the two originals it replaced.
_MERGE_SEARCH_M = 60.0

_LAYERS = {
    "55map": (
        "inputs/vectors/references/student-mounds-55maps.geojson",
        "inputs/vectors/references/student-mounds-55maps-reviewed.geojson",
    ),
    "gs": (
        "inputs/vectors/references/student-mounds-gs-4maps.geojson",
        "inputs/vectors/references/student-mounds-gs-4maps-reviewed.geojson",
    ),
}

# Attributes that must survive unchanged on a point present in both layers.
_STABLE_ATTRIBUTES = ["MapSymbol", "FeatureType", "source_map"]


def load(path: Path) -> tuple[np.ndarray, gpd.GeoDataFrame]:
    """Load a layer as projected coordinates plus its attribute table."""
    frame = gpd.read_file(path)
    if frame.crs is None:
        raise ValueError(f"{path} has no CRS")
    if frame.crs.to_string() != _TARGET_CRS:
        frame = frame.to_crs(_TARGET_CRS)
    centroids = frame.geometry.centroid
    return np.column_stack([centroids.x, centroids.y]), frame


def check_immutability(path: Path) -> list[str]:
    """Check the original has one commit and a clean working copy.

    Args:
        path: Repository-relative path to the immutable layer.

    Returns:
        A list of problems; empty means the file is what git says it is.
    """
    problems: list[str] = []
    rel = str(path.relative_to(_PROJECT_ROOT))
    log = subprocess.run(
        ["git", "log", "--format=%h", "--", rel],
        cwd=_PROJECT_ROOT, capture_output=True, text=True, check=False,
    ).stdout.split()
    print(f"  commits touching the original: {len(log)} ({', '.join(log)})")
    if len(log) != 1:
        problems.append(
            f"original has {len(log)} commits, expected exactly 1 — it has "
            "been modified since import",
        )
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", rel],
        cwd=_PROJECT_ROOT, capture_output=True, text=True, check=False,
    ).stdout.strip()
    if dirty:
        problems.append(f"original has uncommitted changes: {dirty}")
    return problems


def audit(original_path: Path, reviewed_path: Path) -> list[str]:
    """Run the full integrity audit.

    Args:
        original_path: The immutable layer.
        reviewed_path: Its corrected descendant.

    Returns:
        A list of problems; empty means every difference is accounted for.
    """
    problems = check_immutability(original_path)
    original, original_frame = load(original_path)
    reviewed, reviewed_frame = load(reviewed_path)
    print(f"  original {len(original)} -> reviewed {len(reviewed)}")

    to_original, nearest_original = cKDTree(original).query(reviewed, k=1)
    to_reviewed, _ = cKDTree(reviewed).query(original, k=1)
    added = np.where(to_original > _IDENTITY_TOL_M)[0]
    removed = np.where(to_reviewed > _IDENTITY_TOL_M)[0]
    survivors = np.where(to_original <= _IDENTITY_TOL_M)[0]
    print(f"  added {len(added)} · removed {len(removed)} · "
          f"unchanged position {len(survivors)}")

    # 4. Survivors must not have moved at all.
    worst = float(to_original[survivors].max()) if len(survivors) else 0.0
    print(f"  largest survivor displacement: {worst:.6f} m")
    if worst > _IDENTITY_TOL_M:
        problems.append(f"a surviving point moved by {worst:.3f} m")

    # 5. Survivors must not have been reclassified.
    for column in _STABLE_ATTRIBUTES:
        if column not in reviewed_frame.columns:
            continue
        changed = 0
        for reviewed_index in survivors:
            original_index = nearest_original[reviewed_index]
            before = original_frame.iloc[original_index].get(column)
            after = reviewed_frame.iloc[reviewed_index].get(column)
            if pd.isna(before) and pd.isna(after):
                continue
            if str(before) != str(after):
                changed += 1
        print(f"  survivors with changed {column}: {changed}")
        if changed:
            problems.append(
                f"{changed} surviving point(s) had {column} changed after "
                "import",
            )

    # 2 and 3. Every addition should be a merge centroid, and every removal
    # should be one half of such a merge.
    merge_sites, incursions = [], []
    claimed_removals: set[int] = set()
    if len(removed):
        removed_tree = cKDTree(original[removed])
        for index in added:
            nearby = removed_tree.query_ball_point(
                reviewed[index], r=_MERGE_SEARCH_M,
            )
            if len(nearby) == 2:
                merge_sites.append(int(index))
                claimed_removals.update(int(removed[n]) for n in nearby)
            else:
                incursions.append(int(index))
    else:
        incursions = [int(i) for i in added]
    orphan_removals = sorted(set(int(i) for i in removed) - claimed_removals)
    print(f"  additions explained as merge centroids: {len(merge_sites)}")
    print(f"  additions NOT explained: {len(incursions)}")
    print(f"  removals not claimed by any merge: {len(orphan_removals)}")

    for index in incursions:
        note = ""
        for column in reviewed_frame.columns:
            if column.startswith("_added"):
                value = reviewed_frame.iloc[index].get(column)
                if not pd.isna(value):
                    note = str(value)[:110]
        problems.append(f"unexplained addition at reviewed #{index}: {note}")
    for index in orphan_removals:
        problems.append(
            f"unexplained removal of original #{index} "
            f"({original_frame.iloc[index].get('MapSymbol')})",
        )
    return problems


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Audit student-GT integrity against the immutable original.",
    )
    parser.add_argument(
        "--layer", choices=sorted(_LAYERS) + ["all"], default="all",
    )
    return parser.parse_args(argv)


def main() -> None:
    """Run the audit and exit non-zero on any unaccounted difference."""
    args = parse_args()
    names = sorted(_LAYERS) if args.layer == "all" else [args.layer]
    all_problems: dict[str, list[str]] = {}
    for name in names:
        original, reviewed = _LAYERS[name]
        print(f"\n=== {name} ===")
        all_problems[name] = audit(
            _PROJECT_ROOT / original, _PROJECT_ROOT / reviewed,
        )

    print("\n=== VERDICT ===")
    total = 0
    for name, problems in all_problems.items():
        if problems:
            total += len(problems)
            print(f"  {name}: {len(problems)} UNACCOUNTED")
            for problem in problems:
                print(f"     - {problem}")
        else:
            print(f"  {name}: CLEAN — every difference accounted for")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
