"""Compare the two 487-tile frames' geometry, tile names, and reference scoping.

Read-only. Usage: python frames_geometry.py <repo_root>
"""

import sys
from pathlib import Path

import geopandas as gpd

sys.path.insert(0, sys.argv[1])
from scripts.lib_advanced_metrics import get_map_name, scope_references_to_tiles  # noqa: E402

root = Path(sys.argv[1])
crs = "EPSG:32635"
board = gpd.read_file(root / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson").to_crs(
    crs
)
era2 = gpd.read_file(root / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson").to_crs(crs)
ref = gpd.read_file(root / "inputs/vectors/references/mounds-reference.geojson").to_crs(crs)

print("tiles", len(board), len(era2))
print("tile-name sets equal:", set(board.tile_name) == set(era2.tile_name))
print("maps board", sorted({get_map_name(t) for t in board.tile_name}))
print("maps era2 ", sorted({get_map_name(t) for t in era2.tile_name}))
ub, ue = board.geometry.union_all(), era2.geometry.union_all()
print(
    f"area board {ub.area / 1e6:.3f} km2; era2 {ue.area / 1e6:.3f} km2; "
    f"diff {(ue.area - ub.area) / 1e6:.3f}"
)
strip = ue.symmetric_difference(ub)
print(
    f"symmetric difference {strip.area / 1e6:.3f} km2; "
    f"board-minus-era2 {ub.difference(ue).area / 1e6:.6f}"
)
m = era2.merge(board[["tile_name", "geometry"]].rename(columns={"geometry": "gb"}), on="tile_name")
m["lost_km2"] = (m.geometry.area - gpd.GeoSeries(m.gb, crs=crs).area) / 1e6
clipped = m[m.lost_km2 > 1e-6]
print(
    "clipped tiles",
    len(clipped),
    "by map:",
    clipped.tile_name.map(get_map_name).value_counts().to_dict(),
)
print(f"clipped-tile loss range {clipped.lost_km2.min():.4f}-{clipped.lost_km2.max():.4f} km2")
# Reference points in the strip, and under the scorer's per-map scoping
print("reference points within/intersecting strip:", int(ref.intersects(strip).sum()))
print("nearest reference to strip (m):", round(float(ref.distance(strip).min()), 1))
for name, frame in (("board", board), ("era2", era2)):
    tot = 0
    ids = set()
    for mp in sorted({get_map_name(t) for t in frame.tile_name}):
        mb = frame[frame.tile_name.str.startswith(mp)]
        rs = scope_references_to_tiles(ref[ref["Map"] == mp], mb)
        tot += len(rs)
        ids |= set(rs.index)
    print(f"{name}: references in scope under calculate_f1_internal = {tot}")
    if name == "board":
        bids = ids
    else:
        print("same reference index set:", bids == ids)
strip_gdf = gpd.GeoDataFrame(geometry=[strip], crs=crs)
strip_gdf.to_file(
    "/tmp/claude-1000/-home-shawn-Code-map-reader-llm/efba6aeb-0fcf-4126-91f1-0e10ca25f39d/scratchpad/w27/strip.geojson",
    driver="GeoJSON",
)
