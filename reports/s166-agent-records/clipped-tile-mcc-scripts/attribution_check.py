#!/usr/bin/env python3
"""
attribution_check.py -- is the clip the only cause of the moved tile confusions?
================================================================================
S166 clipped tile-MCC job (reports/s166-agent-records/clipped-tile-mcc.md § 2.5).
The six Phase 2 cells the D51 clip moves (HIGH text T 1.0 and MINIMAL image
T 0.7, K = 3, 5, 10) were evaluated in September 2026, before the D50 scorer;
their clipped twins were evaluated with today's. This scores BOTH files of each
pair with today's ``calculate_tile_classification`` (no bootstrap) and compares
each with its committed evaluation's confusion: if today's scorer reproduces
the unclipped confusion, the clipped-minus-as-evaluated difference is the clip
alone. Run once on sapphire in the job's whole-tree copy (output beside this
file as attribution_check.out); a few seconds of CPU. No API calls.
"""
import json
import sys

import geopandas as gpd

sys.path.insert(0, ".")
from scripts.lib_advanced_metrics import calculate_tile_classification  # noqa: E402
from scripts.pairwise_permutation_test import assign_source_tiles  # noqa: E402

OUT = "results/k-ladder-2026-09-12/clipped-mcc-2026-10-30"
prepared = json.load(open(f"{OUT}/prepare.json"))
bounds = gpd.read_file("inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson")
bounds = bounds.to_crs(32635)
refs = gpd.read_file("inputs/vectors/references/mounds-reference.geojson").to_crs(32635)
for ladder in prepared["ladders"]:
    for rung in ladder["rungs"]:
        if rung["clip"]["n_removed"] == 0 or ladder["slug"] == "d51clip-tier-e":
            continue
        for which in ("source", "target"):
            det = gpd.read_file(rung["clip"][which])
            det = (det.set_crs(4326) if det.crs is None else det).to_crs(32635)
            if "source_tile" not in det.columns:
                det = assign_source_tiles(det, bounds)
            tc = calculate_tile_classification(det, refs, bounds)
            conf = {k: int(tc[k]) for k in ("tp", "tn", "fp", "fn")}
            path = rung["as_evaluated_eval_path"] if which == "source" else \
                rung["clipped_eval_path"]
            ref = json.load(open(path))["summary"]["tile_classification"]["confusion"]
            print(rung["condition_id"].split("::")[1], which, conf,
                  "== committed" if conf == ref else f"!= {ref}", round(tc["mcc"], 4))
