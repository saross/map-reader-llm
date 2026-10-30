#!/usr/bin/env python3
"""
Diagnostic: where the published ``id`` join's tile errors sit on the overlapping frame.

Part of the S166 MCC robustness job, part (b)
(``reports/s166-agent-records/mcc-join-tiering.md``). A DIAGNOSTIC, not a
result the record rests on: it asks whether a cell's tile errors under the
published ``id`` join are tiles the cell's detections geometrically occupy.

The ``id`` join books a reference to every frame tile it intersects but a
detection only to the one tile its ``source_tile`` names. On the board frame
(384 px tiles on a 336 px stride) neighbouring tiles overlap, so a detected
mound in an overlap makes two tiles reference-positive while its detection
names one of them. The other tile is then a false negative under ``id`` even
though a detection lies inside it. A detection set that keeps one point per
mound (a consensus or verified merge) can be exposed to this more than one
that keeps a point per tile the mound was seen on. This script counts, per
cell, under ``id``:

* ``fn``: false-negative tiles;
* ``fn_with_detection_inside``: those that geometrically contain one of the
  cell's detections (booked by name to a neighbour);
* ``fp``: false-positive tiles;
* ``n_det_outside_named_tile``: detections whose geometry does not intersect
  the tile their ``source_tile`` names;

and the cell's tile-MCC under each join, read from the chain's tiering runs.

Usage: python id_join_mechanism.py <clone_root> <chain_out_dir> <out_json>

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import geopandas as gpd

BOARD_ID = "gs-era2-verified-board-2026-09-10"
JOINS = ("id", "geometric-primary", "geometric-contains")


def main() -> int:
    """Count each cell's id-join tile errors against the detections' geometry."""
    clone, out, target = (Path(p) for p in sys.argv[1:4])
    sys.path.insert(0, str(clone / "scripts"))
    import era1_leaderboard_tiering as t  # noqa: PLC0415
    from lib_advanced_metrics import (  # noqa: PLC0415
        assign_points_to_tiles,
        calculate_tile_classification,
    )

    runs = {}
    for join in JOINS:
        stem = "tiering_20m" if join == "id" else f"tiering_20m_{join}"
        runs[join] = json.loads((out / "tiering" / join / f"{stem}.json").read_text())
    mcc = {j: {r["ref"]: r["mcc"] for r in runs[j]["mcc_permutation"]["ranking"]}
           for j in JOINS}
    rc = json.loads((clone / "results/run-conditions.json").read_text())["decomposition"]
    bounds = gpd.read_file(
        clone / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
    ).to_crs(t.TARGET_CRS)
    refs = gpd.read_file(
        clone / "inputs/vectors/references/mounds-reference.geojson").to_crs(t.TARGET_CRS)
    polygon = dict(zip(bounds["tile_name"], bounds.geometry, strict=True))

    rows = []
    for ref in mcc["id"]:
        run, label = ref.split("::", 1)
        cond = next(c for c in rc[run]["conditions"] if c["label"] == label)
        meta = json.loads((clone / cond["eval_path"]).read_text())["_metadata"]
        det = t.cell_detections(dict(meta.get("cli_args") or {}), bounds)
        res = calculate_tile_classification(det, refs, bounds, tile_join="id")
        occupied = assign_points_to_tiles(det, bounds, "geometric-contains")["tiles_with_point"]
        classes = {d["tile_name"]: d["classification"] for d in res["tile_details"]}
        fn = [name for name, c in classes.items() if c == "FN"]
        outside = sum(
            1 for name, geom in zip(det["source_tile"], det.geometry, strict=True)
            if name in polygon and not geom.intersects(polygon[name])
        )
        rows.append({
            "ref": ref,
            "architecture": cond.get("architecture"),
            "n_passes": cond.get("n_passes"),
            "n_detections": int(len(det)),
            "confusion_id": {k: int(res[k]) for k in ("tp", "tn", "fp", "fn")},
            "fn": len(fn),
            "fn_with_detection_inside": sum(1 for name in fn if name in occupied),
            "fp": sum(1 for c in classes.values() if c == "FP"),
            "n_det_outside_named_tile": outside,
            "mcc": {j: mcc[j][ref] for j in JOINS},
        })
        print(f"{label:55s} fn={rows[-1]['fn']:3d} "
              f"fn_inside={rows[-1]['fn_with_detection_inside']:3d} "
              f"outside_named={outside}", flush=True)
    target.write_text(json.dumps({"board": BOARD_ID, "cells": rows}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
