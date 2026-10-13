#!/usr/bin/env python3
"""
Cheap measurements for the scorer-restatement inventory (2026-10-12/13).

Scratch tool, run in a disposable tree on sapphire; writes one JSON to the
path given and nothing else.

1. ``measure_miss_correlation_gs.py`` matches the GS curator mounds against
   the system set and the students with ONE global Hungarian across all four
   sheets, the system set unscoped. Here the same 2x2 found/miss table is
   recomputed both ways: (a) the committed global rule, as a reproduction
   gate, and (b) per sheet, with the system side scoped by the shared rule
   (``scope_detections_to_frame``) and the student side split by its sheet
   column, so each mound is matched only against its own sheet's points.

2. ``stride_plateau_analyses.py`` rebuilds its four incumbents from bare
   coordinates through ``grid_analysis.as_gdf`` (legacy nearest-centroid
   tile, no origin). Here each incumbent's as_gdf sheet is compared with the
   sheet of its own recorded ``source_tile``, and F1 at 20 m is computed both
   ways with the shared scorer on the same carrier.

Usage::

    python measure_misc.py <tree> <out.json>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    """Run both measurements and write the JSON."""
    tree = Path(sys.argv[1]).resolve()
    out_path = Path(sys.argv[2])
    sys.path.insert(0, str(tree))
    sys.path.insert(0, str(tree / "scripts"))

    import geopandas as gpd
    import numpy as np

    from scripts import lib_advanced_metrics as lam
    from scripts import measure_miss_correlation_gs as mmc

    out: dict = {}

    # ── 1. miss correlation: global (committed) versus per sheet ─────────
    bounds = mmc.to_32635(mmc.BOUNDS)
    area = bounds.union_all()
    curator = mmc.to_32635(mmc.CURATOR)
    curator = curator[curator.geometry.within(area)].reset_index(drop=True)
    students = mmc.to_32635(mmc.STUDENTS)
    system = mmc.to_32635(mmc.SYSTEM)
    scope = lam.scope_detections_to_frame(system, bounds)
    sheets = lam.frame_sheets(bounds)

    def per_sheet_flags(points: gpd.GeoDataFrame, sheet_of_point: np.ndarray,
                        radius: float) -> list[bool]:
        """Curator found-flags, matching each sheet only against its own points."""
        found = [False] * len(curator)
        for sheet in sheets:
            ref_idx = np.flatnonzero(curator["Map"].to_numpy() == sheet)
            pts = points[sheet_of_point == sheet]
            if len(ref_idx) == 0 or len(pts) == 0:
                continue
            _, mref, _, _ = lam.match_detections_to_references(
                list(pts.geometry), list(curator.geometry.iloc[ref_idx]), radius)
            for j in mref:
                found[int(ref_idx[j])] = True
        return found

    def table(s_found: list[bool], y_found: list[bool]) -> dict:
        a = sum(s and y for s, y in zip(s_found, y_found))
        b = sum(s and not y for s, y in zip(s_found, y_found))
        c = sum((not s) and y for s, y in zip(s_found, y_found))
        d = sum((not s) and (not y) for s, y in zip(s_found, y_found))
        n = len(curator)
        ms = 1 - sum(s_found) / n
        mm = (b + d) / n
        ratio = (d / n) / (ms * mm) if ms * mm else None
        return {"both_found": a, "students_only": b, "system_only": c,
                "both_miss": d, "student_miss_rate": round(ms, 4),
                "system_miss_rate": round(mm, 4),
                "correlation_ratio": None if ratio is None else round(ratio, 2)}

    s_global = mmc.matched_flags(curator, students, mmc.STUDENT_RADIUS)
    student_sheet = students["source_map"].to_numpy()
    s_sheet = per_sheet_flags(students, student_sheet, mmc.STUDENT_RADIUS)
    rows = []
    for r in mmc.SYSTEM_RADII:
        y_global = mmc.matched_flags(curator, system, r)
        y_sheet = per_sheet_flags(scope.detections, np.asarray(scope.sheets), r)
        rows.append({
            "radius_m": r,
            "global_committed_rule": table(s_global, y_global),
            "per_sheet_shared_scope": table(s_sheet, y_sheet),
            "mounds_whose_system_flag_changes": int(sum(
                g != s for g, s in zip(y_global, y_sheet))),
        })
    out["miss_correlation"] = {
        "n_curator_in_bounds": len(curator),
        "n_system": len(system),
        "system_scope": {k: v for k, v in scope.diagnostics.items()
                         if k.startswith("n_")},
        "students_flags_changed_by_per_sheet": int(sum(
            g != s for g, s in zip(s_global, s_sheet))),
        "by_radius": rows,
    }

    # ── 2. plateau incumbents: as_gdf sheet versus recorded sheet ────────
    from scripts import stride_plateau_analyses as spa
    from scripts.grid_analysis import as_gdf

    carrier = gpd.read_file(spa.COMMON_BOUNDS)
    gt = gpd.read_file(spa.GROUND_TRUTH)
    longest = sorted(lam.frame_sheets(carrier), key=len, reverse=True)
    inc_out = {}
    for name, rel in spa.INCUMBENTS.items():
        inc = gpd.read_file(tree / rel).to_crs(spa.CRS)
        rebuilt = as_gdf(np.asarray([[g.x, g.y] for g in inc.geometry]), carrier)
        kept = rebuilt.index.to_numpy()
        rec_sheet = [lam._sheet_of_tile_name(str(t), longest)
                     for t in inc["source_tile"].iloc[kept]]
        new_sheet = [lam._sheet_of_tile_name(str(t), longest)
                     for t in rebuilt["source_tile"]]
        changed = int(sum(a != b for a, b in zip(rec_sheet, new_sheet)))
        f1_asgdf = lam.calculate_f1_internal(rebuilt, gt, carrier, 20)[2]
        f1_recorded = lam.calculate_f1_internal(inc, gt, carrier, 20)[2]
        inc_out[name] = {
            "n_file": len(inc), "n_on_carrier": len(rebuilt),
            "sheet_changed_vs_recorded": changed,
            "f1_20m_as_gdf_rule": f1_asgdf,
            "f1_20m_recorded_source_tile": f1_recorded,
            "recorded_scope": {k: v for k, v in lam.scope_detections_to_frame(
                inc, carrier).diagnostics.items() if k.startswith("n_")},
        }
    out["plateau_incumbents"] = inc_out
    out_path.write_text(json.dumps(out, indent=1, default=str) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
