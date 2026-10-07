#!/usr/bin/env python3
"""Incidental check: does the committed matcher's integer cost matrix (int buffer) change
totals or only per-tile allocation? Compares the gated scorer (int buffer, = committed)
with a float-buffer variant on 24 subset cells. Zero API.

Author: Shawn Ross & Claude (Anthropic) | Created: 2026-10-07 | Apache 2.0
"""

import os
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np

REPO = Path(os.environ.get("REPO", str(Path.home() / "Code/map-reader-llm")))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "reports/w27-replicate-floors-2026-10-06-scripts"))
import w27_55map_subset_replicates as w27  # noqa: E402

import floors2_lib as L  # noqa: E402
from scripts.build_55map_leaderboard import BOUNDS, reference_gt  # noqa: E402

w27.cluster_votes = L.cluster_votes_fast
fam = w27.build_families(gate_only=True)
index = next(iter(fam.values()))["index"]
ref = reference_gt("r2")
b = gpd.read_file(BOUNDS)
b = (b.set_crs("EPSG:4326") if b.crs is None else b).to_crs("EPSG:32635")
si, sf = L.FastScorer(ref, b, 50), L.FastScorer(ref, b, 50.0)
n_tot_diff = n_tile_diff = n = 0
for f, s in (
    ("A", (0,)),
    ("A", (1, 2, 3)),
    ("B", (0, 1, 2, 3, 4)),
    ("FOURTH", (4, 5, 6)),
    ("ARM1", (0, 1)),
    ("ARM2", (2, 3, 4)),
):
    cell = w27.inherit(w27.cluster_subset(fam[f]["passes"], s, index), fam[f]["union"])
    xy = np.c_[cell.geometry.x, cell.geometry.y]
    tiles = cell["source_tile"].to_numpy(dtype=object)
    for p in sorted(set(cell["mound_probability"].quantile([0.3, 0.5, 0.7, 0.9]).round(3))):
        m = cell["mound_probability"].to_numpy() >= p
        a, c = si.per_tile(xy[m], tiles[m]), sf.per_tile(xy[m], tiles[m])
        n += 1
        n_tot_diff += int(not np.array_equal(a.sum(0), c.sum(0)))
        n_tile_diff += int((a != c).any(axis=1).sum())
print(
    f"cells {n}: totals differ in {n_tot_diff}; "
    f"tiles with a different TP/FP/FN split: {n_tile_diff}"
)
