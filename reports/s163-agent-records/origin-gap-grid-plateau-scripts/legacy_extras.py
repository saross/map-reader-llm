"""Legacy replay of the two outputs the branch now generates, before any re-score.

``stride_plateau_analyses.winner_ladder_exact`` and image_b_analysis's
``saturation_N3_vs_N10`` were folded into the committed artefacts by hand on
2026-08-25 and 2026-08-28; no script produced them. This replay runs the
branch's new code with the D62 origin step taken out (the stored, legacy
``source_tile``) and asserts the committed values come back exactly, so the
fixed run's numbers for these two outputs differ from the committed ones by
the origin route alone. Run from a fresh branch copy, BEFORE the chain
rewrites ``results/``.

Usage: python legacy_extras.py <copy_root> <out_json>
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree
from shapely.geometry import Point

root = Path(sys.argv[1]).resolve()
out_path = Path(sys.argv[2])
sys.path[:0] = [str(root), str(root / "scripts")]

import stride_plateau_analyses as sp  # noqa: E402
from scripts import image_b_analysis as iba  # noqa: E402
from scripts import stride_verifier_analysis as svs  # noqa: E402
from scripts.grid_analysis import CRS, load_cell_passes  # noqa: E402
from scripts.grid_verifier_analysis import per_tile_counts, verified_subset  # noqa: E402
from scripts.h13_k_sensitivity import cluster_votes  # noqa: E402
from scripts.n1_baseline_leaderboard_tiering import permutation_test_float  # noqa: E402
from scripts.prepare_h13_scoring import assign_primary_tiles  # noqa: E402

bounds = gpd.read_file(svs.COMMON_BOUNDS)
ref = gpd.read_file(svs.GROUND_TRUTH).to_crs(CRS)
result: dict = {"copy": str(root)}

# --- 1. The exact winner ladder, origin step removed. ---
plateau = json.loads((root / "results/stride-2026-08-25/plateau_analyses.json").read_text())


def legacy_loader(label, bounds, *, union_name="union_k10.geojson",
                  verify_dir="verify", n_passes=10):
    """The pre-D62 loader: join and round-trip gates, stored source_tile."""
    return svs.reassign_gate(
        svs.load_stride_union(label, union_name=union_name, verify_dir=verify_dir),
        bounds, label)


sp.load_stride_union_on_origin = legacy_loader
exact = json.loads(json.dumps(sp.winner_ladder_exact(
    bounds, ref, plateau["first_n_ladder"][sp.WINNER_CELL]["prop10_flex_usd"])))
result["winner_ladder_exact_legacy"] = exact
result["winner_ladder_exact_reproduces_committed"] = exact == plateau["winner_ladder_exact"]

# --- 2. Image-B N3 against N10, exactly as the pre-D62 script built rung 3. ---
committed = json.loads((root / "results/image-b-gs-2026-08-28/analysis.json").read_text())
cell = "g384_ov192_image"
vroot = root / "outputs/image-b-gs-2026-08-28/verifier" / cell
union = svs.reassign_gate(iba.load_image_union(vroot, "union_k10.geojson", "verify"),
                          bounds, cell)
best = committed["image_best"]
best_set = verified_subset(union, best["prob_t"], best["min_votes"])
passes = load_cell_passes(root / "outputs/image-b-gs-2026-08-28/scoring", cell)
tree = cKDTree(np.c_[union.geometry.x, union.geometry.y])
probs10 = union["mound_probability"].to_numpy()
centroids, votes = cluster_votes(passes[:3], 1)
gdf = gpd.GeoDataFrame({"vote_count": np.asarray(votes)},
                       geometry=[Point(xy) for xy in centroids], crs=CRS)
gdf["source_tile"] = assign_primary_tiles(gdf, bounds)
d, idx = tree.query(np.c_[gdf.geometry.x, gdf.geometry.y], k=1)
gdf["mound_probability"] = probs10[idx]
gdf = gdf[d <= iba.INHERIT_TOL_M].copy()
rows = iba.sweep(gdf, ref, bounds, range(1, 4))
rbest = max(rows, key=lambda r: r["f1"])
rung3 = verified_subset(gdf, rbest["prob_t"], rbest["min_votes"])
t3 = per_tile_counts(rung3, bounds, ref)
ti = per_tile_counts(best_set, bounds, ref)
sat3 = permutation_test_float(t3["tp"], t3["fp"], t3["fn"], ti["tp"], ti["fp"], ti["fn"],
                              n_permutations=iba.N_PERMS, seed=iba.SEED)
sat3 = json.loads(json.dumps(sat3, default=float))
result["image_sat3_legacy"] = sat3
result["image_rung3_best_legacy"] = json.loads(json.dumps(rbest, default=float))
result["image_sat3_reproduces_committed"] = sat3 == committed["saturation_N3_vs_N10"]
result["image_rung3_reproduces_committed"] = (
    json.loads(json.dumps(rbest, default=float)) == committed["ladder"]["3"]["best"])

out_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
print(json.dumps({k: v for k, v in result.items() if k.endswith("committed")}, indent=2))
ok = all(v for k, v in result.items() if k.endswith("committed"))
sys.exit(0 if ok else 3)
