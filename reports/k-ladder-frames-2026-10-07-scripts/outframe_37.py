"""Characterise the Gemini 3.7 rungs' detections outside the 487-tile frames.

Read-only. Usage: python outframe_37.py <repo_root>
"""

import json
import sys
from pathlib import Path

import geopandas as gpd

root = Path(sys.argv[1])
sys.path.insert(0, str(root))
from scripts.lib_advanced_metrics import get_map_name  # noqa: E402

crs = "EPSG:32635"
board = gpd.read_file(root / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson").to_crs(
    crs
)
ub = board.geometry.union_all()
ref = gpd.read_file(root / "inputs/vectors/references/mounds-reference.geojson").to_crs(crs)
ref_out = ref[~ref.intersects(ub)]
ops = json.load(open(root / "results/k-ladder-2026-09-12/phase2/operating-points.json"))["rungs"]
for r in ops:
    if r["run_id"] != "gemini37-screen-2026-08-28":
        continue
    det = gpd.read_file(root / r["opmax"]["detections"]).to_crs(crs)
    out = det[~det.intersects(ub)]
    maps = (
        out.source_tile.map(get_map_name).value_counts().to_dict() if "source_tile" in out else {}
    )
    near = out.geometry.apply(lambda g: ref_out.distance(g).min())
    print(f"row {r['row']} opmax n={len(det)}; outside board frame {len(out)}; by map {maps}")
    print(
        f"   within 20 m of an out-of-frame reference: {int((near <= 20).sum())}; "
        f"within 50 m: {int((near <= 50).sum())}; median distance {near.median():.0f} m"
    )
    print(
        "   distance to board frame (m): min %.0f, median %.0f, max %.0f"
        % tuple(out.distance(ub).quantile([0, 0.5, 1]).round())
    )
print(
    "reference mounds outside board frame:",
    len(ref_out),
    "on maps",
    ref_out["Map"].value_counts().to_dict(),
)
