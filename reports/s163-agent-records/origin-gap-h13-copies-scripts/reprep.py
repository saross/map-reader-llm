#!/usr/bin/env python3
"""
Rewrite the H13 prepared sets on today's code, with the committed bounds.

D62 (1) workstream ``origin-gap-h13-copies`` (2026-10-13). The committed
per-pass sets under ``outputs/h13/scoring/{common,native}/`` were written on
2026-08-18 by ``scripts/prepare_h13_scoring.py`` under the legacy tiling
rule. They record each detection's origin (``origin_tiles``), so the D50
scorer restores the sheet at scoring time; but the per-tile tables that feed
the H13 bootstrap and permutation test book a true or false positive to the
recorded ``source_tile`` string, which for a re-keyed row is the
neighbouring sheet's tile. This driver re-runs the preparation's
deduplicate-and-write stage on today's code, reading the committed bounds
instead of regenerating them (the arm B and C tile metadata that
``build_native_bounds`` needs is not in the repository), so the main
analysis can be re-scored on sets tiled on their own sheets.

It mirrors ``prepare_h13_scoring.main()`` step for step except for the
bounds: the committed native and common bounds files are copied byte for
byte, and the common footprint is the intersection of the committed native
bounds' unions, as ``build_common_bounds`` computes it.

Usage::

    python reprep.py --repo <tree> --out <dir>

Author: Claude Code (Opus 5.5) for Shawn Ross
Licence: Apache 2.0
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import geopandas as gpd


def main() -> int:
    """Rewrite the 18 prepared sets into ``--out`` and compare them.

    Returns:
        Process exit status (0 on success).
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    repo = args.repo.resolve()
    sys.path.insert(0, str(repo))
    import scripts.prepare_h13_scoring as prep  # noqa: E402

    assert Path(prep.__file__).resolve().is_relative_to(repo), prep.__file__
    committed = repo / "outputs" / "h13" / "scoring"
    out = args.out
    (out / "bounds").mkdir(parents=True, exist_ok=True)
    for f in sorted((committed / "bounds").glob("*.geojson")):
        shutil.copyfile(f, out / "bounds" / f.name)

    native = {
        arm: gpd.read_file(out / "bounds" / f"h13_{arm}_bounds.geojson")
        for arm in prep.ARMS
    }
    unions = {arm: g.geometry.union_all() for arm, g in native.items()}
    common_geom = unions["armA"].intersection(unions["armB"]).intersection(unions["armC"])
    common_gdf = gpd.read_file(out / "bounds" / "h13_common_bounds.geojson")
    common_tiles = sorted(common_gdf["tile_name"].tolist())

    report: dict = {"passes": []}
    for arm, spec in prep.ARMS.items():
        for run, paths in spec["runs"].items():
            raw, processed = prep.load_pass(paths)
            deduped = prep.deduplicate_within_pass(
                raw, distance_thresh=prep.DISTANCE_THRESHOLD_METRES)
            entry = {"arm": arm, "run": run}
            for scope, bounds, tiles, clip in (
                ("native", native[arm], sorted(processed), None),
                ("common", common_gdf, common_tiles, common_geom),
            ):
                target = out / scope / arm / run / "detections_dedup.geojson"
                stats = prep.write_dedup_geojson(deduped, bounds, tiles, target, clip)
                # Compare with the committed set, feature by feature.
                new = json.loads(target.read_text())["features"]
                old = json.loads(
                    (committed / scope / arm / run / "detections_dedup.geojson")
                    .read_text())["features"]
                same_geom = len(new) == len(old) and all(
                    a["geometry"] == b["geometry"] for a, b in zip(new, old))
                diff_props = []
                for i, (a, b) in enumerate(zip(new, old)):
                    pa = {k: v for k, v in a["properties"].items() if k != "source_tile"}
                    pb = {k: v for k, v in b["properties"].items() if k != "source_tile"}
                    if pa != pb:
                        diff_props.append(i)
                tile_changed = [
                    (a["properties"]["source_tile"], b["properties"]["source_tile"])
                    for a, b in zip(new, old)
                    if a["properties"]["source_tile"] != b["properties"]["source_tile"]
                ]
                sheet_changed = [
                    t for t in tile_changed
                    if (t[0] or "").split("_x")[0] != (t[1] or "").split("_x")[0]
                ]
                entry[scope] = {
                    **stats,
                    "n_committed": len(old),
                    "same_geometry_and_order": same_geom,
                    "n_other_property_diffs": len(diff_props),
                    "n_source_tile_changed": len(tile_changed),
                    "n_sheet_changed": len(sheet_changed),
                    "n_now_null": sum(1 for t in tile_changed if t[0] is None),
                }
            report["passes"].append(entry)
            print(arm, run, json.dumps({k: entry[k] for k in ("native", "common")}))

    (out / "reprep_report.json").write_text(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
