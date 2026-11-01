"""Does each tile join give a PERFECT detector a perfect tile-MCC?

Evidence for ``planning/tile-join-resolution-2026-11-01.md`` (S167,
2026-11-01). Detections are the reference mounds themselves, so any
tile-level false negative or false positive is manufactured by the scoring
rule, not by the pipeline. Run from the repository root with the project
venv: ``.venv/bin/python planning/tile-join-resolution-2026-11-01-scripts/
perfect_detector.py``. Output: ``perfect_detector.txt`` beside this file.

Two perfect pipelines:
  merged   one point per mound, ``source_tile`` = alphabetically first frame
           tile containing it (the rule ``lib_consensus`` applies to every
           consensus and verified point);
  per-tile one point per (mound, containing tile), each named for its tile
           (an unmerged pass that reported the mound on every tile it saw).
"""
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
from scripts.lib_advanced_metrics import TILE_JOINS, calculate_tile_classification  # noqa: E402

REPO = str(REPO_ROOT) + "/"
FRAMES = {
    "GS Era-2 (384 px / 336 stride)": (
        "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson",
        "inputs/vectors/references/mounds-reference.geojson",
    ),
}

for frame_name, (bounds_path, ref_path) in FRAMES.items():
    bounds = gpd.read_file(REPO + bounds_path).to_crs(32635)
    refs = gpd.read_file(REPO + ref_path).to_crs(32635)
    # Keep only references inside the frame union (the frame's own scope).
    hits = gpd.sjoin(refs[["geometry"]].reset_index(), bounds[["tile_name", "geometry"]],
                     predicate="intersects")
    containing = hits.groupby("index")["tile_name"].apply(sorted)
    refs_in = refs.loc[containing.index].copy()
    n_multi = int((containing.map(len) > 1).sum())
    print(f"{frame_name}: {len(refs_in)} reference mounds in frame, "
          f"{n_multi} ({n_multi / len(refs_in):.1%}) lie in 2+ tiles")

    merged = refs_in.copy()
    merged["source_tile"] = containing.map(lambda names: names[0])
    rows = []
    for idx, names in containing.items():
        for name in names:
            rows.append({"geometry": refs_in.loc[idx, "geometry"], "source_tile": name,
                         **{c: refs_in.loc[idx, c] for c in refs_in.columns if c != "geometry"}})
    per_tile = gpd.GeoDataFrame(pd.DataFrame(rows), geometry="geometry", crs=32635)

    for label, dets in (("merged", merged), ("per-tile", per_tile)):
        for join in TILE_JOINS:
            r = calculate_tile_classification(dets, refs_in, bounds, tile_join=join)
            if "error" in r:
                print(f"  {label:8s} {join:18s} REFUSED: {r.get('reason')}")
                continue
            print(f"  {label:8s} {join:18s} MCC {r['mcc']:.4f}  "
                  f"TP {r['tp']} FP {r['fp']} FN {r['fn']} TN {r['tn']}")
