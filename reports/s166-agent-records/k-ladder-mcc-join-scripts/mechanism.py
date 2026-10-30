#!/usr/bin/env python3
"""
Diagnostic: per K-ladder rung, how many of its id-join false-negative tiles hold its own detections.

Part of the S166 K-ladder tile-join job
(``reports/s166-agent-records/k-ladder-mcc-join.md``). DESCRIPTIVE ONLY. It
extends the Era-2 board diagnostic of the same night
(``reports/s166-agent-records/mcc-join-tiering-scripts/id_join_mechanism.py``)
to every rung of the 29 ladders this job tests, to ask whether the share
changes with K.

Under the published ``id`` join a reference is booked to every frame tile it
intersects, but a detection only to the one tile its ``source_tile`` names. On
an overlapping frame a detected mound in an overlap then makes two tiles
reference-positive while its detection names one, and the other tile is a
false negative under ``id`` although a detection lies inside it. For each
rung, under ``id``, this counts:

* ``fn``: false-negative tiles;
* ``fn_with_detection_inside``: those that geometrically contain one of the
  rung's own detections (``assign_points_to_tiles`` under
  ``geometric-contains``);
* ``fp``, ``tp``, ``tn`` and the rung's ``id`` tile-MCC, which the summary
  cross-checks against the committed tiering.

Ground truth and bounds are resolved as ``era1_leaderboard_tiering.load_cells``
resolves them: from the rungs' own evaluations, unless the ladder's tiering
overrides the bounds (the gold-standard, Phase 2, tier E and clipped ladders
are tiered on the board frame by override).

Usage: python mechanism.py <clone_root> <phase2_compat_json> <out_json>

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    """Count each rung's id-join FN tiles that hold its own detections."""
    root, compat, target = (Path(sys.argv[1]).resolve(), Path(sys.argv[2]),
                            Path(sys.argv[3]))
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / "scripts"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import geopandas as gpd  # noqa: PLC0415

    import era1_leaderboard_tiering as t  # noqa: PLC0415
    from ladder_files import cli_of, ladder_specs, resolve  # noqa: PLC0415
    from lib_advanced_metrics import (  # noqa: PLC0415
        assign_points_to_tiles,
        calculate_tile_classification,
    )

    cache: dict[str, gpd.GeoDataFrame] = {}

    def frame(path: str) -> gpd.GeoDataFrame:
        if path not in cache:
            cache[path] = gpd.read_file(root / path).to_crs(t.TARGET_CRS)
        return cache[path]

    ladders = []
    for spec in ladder_specs(root, compat):
        clis = []
        for rung in spec["rungs"]:
            cond = resolve(root, spec["conditions"], rung["ref"])
            clis.append(cli_of(root, cond["eval_path"]))
        gts = {c["ground_truth"] for c in clis}
        boundss = {c["bounds"] for c in clis}
        if len(gts) != 1 or (spec["bounds_override"] is None and len(boundss) != 1):
            raise ValueError(f"{spec['slug']}: rungs disagree on reference or frame")
        gt_path = next(iter(gts))
        bounds_path = spec["bounds_override"] or next(iter(boundss))
        refs, bounds = frame(gt_path), frame(bounds_path)
        rows = []
        for rung, cli in zip(spec["rungs"], clis, strict=True):
            det = t.cell_detections(cli, bounds)
            res = calculate_tile_classification(det, refs, bounds, tile_join="id")
            if "error" in res:
                rows.append({"K": rung["K"], "ref": rung["ref"],
                             "withheld": res.get("reason")})
                continue
            occupied = assign_points_to_tiles(
                det, bounds, "geometric-contains")["tiles_with_point"]
            classes = {d["tile_name"]: d["classification"]
                       for d in res["tile_details"]}
            fn = [name for name, c in classes.items() if c == "FN"]
            inside = sum(1 for name in fn if name in occupied)
            rows.append({
                "K": rung["K"], "ref": rung["ref"],
                "n_detections": int(len(det)),
                "confusion_id": {k: int(res[k]) for k in ("tp", "tn", "fp", "fn")},
                "mcc_id": None if res.get("mcc") is None else float(res["mcc"]),
                "fn": len(fn),
                "fn_with_detection_inside": inside,
                "share": round(inside / len(fn), 6) if fn else None,
            })
            print(f"{spec['slug']:48s} K={rung['K']:2d} fn={len(fn):4d} "
                  f"inside={inside:4d} mcc_id={rows[-1]['mcc_id']}", flush=True)
        ladders.append({"slug": spec["slug"], "group": spec["group"],
                        "ground_truth": gt_path, "bounds": bounds_path,
                        "n_tiles": int(len(bounds)), "rungs": rows})
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "what": ("per rung, under the published id join, the false-negative "
                 "tiles that geometrically contain one of the rung's own "
                 "detections; descriptive, not a decomposition of any MCC change"),
        "ladders": ladders}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
