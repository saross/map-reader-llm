#!/usr/bin/env python3
"""
Materialise the Era-2 board's moved members at their REGISTERED operating points.

Part of the S164 re-score. Nine of the ten Era-2 board members downstream of
the wrong-sheet legs are registered conditions named by their operating point
(e.g. ``g37-image-k5-verified-carried-p0.10-k5``) whose detection file is the
``verified_best_20m.geojson`` that ``image_b_analysis.py`` writes at its sweep
argmax. When the argmax moves (four cells under ORIGIN, the 3.7 image carried
arm under REPAIRED), that file is no longer the registered condition. This
writes ``verified_reg_20m.geojson`` beside it: the set at the registered point,
built through ``image_b_analysis``'s own path (``load_image_union`` under the
leg rule in force, ``reassign_gate``, the PR #42 origin step, then
``verified_subset``), in the writer's own format. The tenth member (the grid
384/50 cell) is written by ``grid_verifier_analysis.py`` at (0.15, k10), its
registered point in both readings, and is checked rather than rewritten.

Usage: python regsets.py <copy_dir>

Author: Shawn Ross, Claude Code (S164). Licence: Apache 2.0
"""
import json
import sys
from pathlib import Path

COPY = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(COPY))

import geopandas as gpd  # noqa: E402

from scripts import image_b_analysis as iba  # noqa: E402
from scripts.grid_analysis import load_cell_passes  # noqa: E402
from scripts.grid_verifier_analysis import verified_subset  # noqa: E402
from scripts.lib_cluster_origins import union_on_origin  # noqa: E402
from scripts.stride_verifier_analysis import COMMON_BOUNDS, reassign_gate  # noqa: E402

#: (outputs root, cell, union, verify leg, K, registered point, results dir)
MEMBERS = [
    ("outputs/gemini37-screen-2026-08-28", "g384_ov192_g37", "union_k5.geojson", "verify", 5,
     (0.10, 5), "results/gemini37-screen-2026-08-28"),
    ("outputs/gemini37-screen-2026-08-28", "g384_ov192_g37", "union_k10.geojson", "verify_k10",
     10, (0.10, 10), "results/gemini37-screen-2026-08-28/k10"),
    ("outputs/gemini37-screen-2026-08-28", "g384_ov192_g37", "union_k5.geojson", "verify_swap37",
     5, (0.80, 5), "results/gemini37-screen-2026-08-28/swap37"),
    ("outputs/gemini37-screen-2026-08-28", "g384_ov192_g37", "union_k5.geojson", "verify_swap38",
     5, (0.88, 5), "results/gemini38-screen-2026-09-04/armV"),
    ("outputs/grid-2026-08-18", "g384_ov192", "union_k10.geojson", "verify_37", 10, (0.98, 10),
     "results/gemini37-fourth-cell/gs-leg"),
    ("outputs/gemini37-image-gs-2026-09-01", "g384_ov192_g37img", "union_k5.geojson",
     "verify_arm1", 5, (0.10, 5), "results/gemini37-image-gs-2026-09-01/arm1"),
    ("outputs/gemini37-image-gs-2026-09-01", "g384_ov192_g37img", "union_k5.geojson",
     "verify_arm2", 5, (0.90, 5), "results/gemini37-image-gs-2026-09-01/arm2"),
    ("outputs/image-b-gs-2026-08-28", "g384_ov192_image", "union_k10.geojson", "verify", 10,
     (0.15, 9), "results/image-b-gs-2026-08-28"),
    ("outputs/image-b-gs-2026-08-28", "g384_ov192_image_high", "union_k10.geojson", "verify", 10,
     (0.20, 8), "results/image-b-gs-2026-08-28/high"),
]

assert iba.PROJECT_ROOT == COPY, (iba.PROJECT_ROOT, COPY)  # scripts imported from the copy
bounds = gpd.read_file(COMMON_BOUNDS)
record = {}
for root, cell, union_name, leg, k, (pt, kk), rdir in MEMBERS:
    vroot = COPY / root / "verifier" / cell
    union = iba.load_image_union(vroot, union_name, leg)
    prov = union.attrs["verifier_probabilities"]
    union = reassign_gate(union, bounds, cell)
    passes = load_cell_passes(COPY / root / "scoring", cell, n_passes=k)
    union = union_on_origin(union, passes, bounds, label=cell, n_passes=k)
    sub = verified_subset(union, pt, kk)
    out = COPY / rdir / "verified_reg_20m.geojson"
    sub.to_crs("EPSG:4326").to_file(out, driver="GeoJSON")
    best = json.loads((COPY / rdir / "analysis.json").read_text())["image_best"]
    record[rdir] = {"registered_point": [pt, kk], "n": int(len(sub)),
                    "argmax_point": [best["prob_t"], best["min_votes"]],
                    "argmax_n": best["n_detections"], "read": prov["dir"]}
    print(rdir, record[rdir])
g = json.loads((COPY / "results/grid-2026-08-18/conditions-verified/grid_verified_conditions.json")
               .read_text())
cell = next(c for c in g["cells"] if c["cell"] == "g384_ov192")
assert (cell["prob_t"], cell["min_votes"]) == (0.15, 10), cell
record["grid g384_ov192"] = {"registered_point": [0.15, 10], "argmax_point": [0.15, 10]}
(COPY / "rescore-regsets.json").write_text(json.dumps(record, indent=1) + "\n")
