# ruff: noqa  (kept verbatim as provenance of reports/retest-bootstrap-check-2026-10-05.md)
"""W2.1: reproduce comparisons[45] of results/retest/pairwise-bootstrap-comparisons.json.

Read-only. Loads the HISTORICAL lib_advanced_metrics (git show fc832dfa9:...),
replays the session code verbatim (archived session 6bbac468, 2026-03-18),
then dissects the per-tile difference that drives the p-value.
"""
import importlib.util
import json
import os
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np

REPO = Path.home() / "Code/map-reader-llm"
os.chdir(REPO)
sys.path.insert(0, str(REPO / "scripts"))
spec = importlib.util.spec_from_file_location("oldlib", "/tmp/w2/lib_advanced_metrics_fc832dfa9.py")
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)

_, bounds, ref = old.load_data(
    "inputs/vectors/references/mounds-reference.geojson",
    "inputs/vectors/bounds/full_evaluation_bounds.geojson",
)


def load_det(path):
    gdf = gpd.read_file(path)
    if not gdf.empty:
        gdf.set_crs(old.DEFAULT_CRS, allow_override=True, inplace=True)
        if "source_tile" not in gdf.columns and "source_tiles" in gdf.columns:
            gdf["source_tile"] = gdf["source_tiles"].apply(
                lambda x: x[0] if hasattr(x, "__getitem__") and len(x) > 0 else str(x))
    return gdf


base = Path("outputs/retest/phase2c/track2-text")
a = load_det(sorted((base / "plus-hp").rglob("detections_*.geojson"))[0])
b = load_det(sorted((base / "scale-4").rglob("detections_*.geojson"))[0])
out = {"pythonhashseed": os.environ.get("PYTHONHASHSEED")}
eff = old.bootstrap_effect_size_ci(a, bounds, b, bounds, ref, n_iterations=1000,
                                   random_seed=42, return_p_values=True)
out["bootstrap"] = {k: eff[k] for k in ("f1_difference", "precision_difference", "recall_difference")}

if os.environ.get("W21_DISSECT"):
    tiles = list(bounds["tile_name"].unique())
    ta = old.compute_per_tile_tp_fp_fn(a, ref, bounds, buffer_metres=20).set_index("tile_name").loc[tiles]
    tb = old.compute_per_tile_tp_fp_fn(b, ref, bounds, buffer_metres=20).set_index("tile_name").loc[tiles]
    d = (ta[["tp", "fp", "fn"]] - tb[["tp", "fp", "fn"]])
    nz = d[(d != 0).any(axis=1)]
    out["n_tiles"] = len(tiles)
    out["totals_a"] = ta[["tp", "fp", "fn"]].sum().astype(int).to_dict()
    out["totals_b"] = tb[["tp", "fp", "fn"]].sum().astype(int).to_dict()
    out["n_discordant_tiles"] = int(len(nz))
    out["discordant_tiles"] = {t: {k: int(v) for k, v in r.items()} for t, r in nz.iterrows()}
    out["n_tiles_tp_a_gt_b"] = int((d["tp"] > 0).sum())
    out["n_tiles_tp_a_lt_b"] = int((d["tp"] < 0).sum())
    out["n_tiles_fp_a_gt_b"] = int((d["fp"] > 0).sum())
    out["n_tiles_fp_a_lt_b"] = int((d["fp"] < 0).sum())
    # Exact paired sign-flip (tile-swap) distribution over ONLY the discordant
    # tiles: swapping a concordant tile changes nothing, so the full tile-swap
    # null is the 2^k enumeration over the k discordant tiles.
    from n1_baseline_leaderboard_tiering import micro_f1
    A = ta[["tp", "fp", "fn"]].to_numpy(float); B = tb[["tp", "fp", "fn"]].to_numpy(float)
    obs = micro_f1(*A.sum(0)) - micro_f1(*B.sum(0))
    idx = np.flatnonzero((A != B).any(1))
    k = len(idx)
    out["observed_f1_diff"] = obs
    if k <= 22:
        import itertools
        cnt = 0; tot = 0
        for mask in itertools.product([0, 1], repeat=k):
            Aa = A.copy(); Bb = B.copy()
            for j, m in zip(idx, mask):
                if m:
                    Aa[j], Bb[j] = B[j].copy(), A[j].copy()
            dd = micro_f1(*Aa.sum(0)) - micro_f1(*Bb.sum(0))
            tot += 1; cnt += abs(dd) >= abs(obs) - 1e-12
        out["exact_tile_swap_p"] = cnt / tot
        out["exact_enumerations"] = tot
    # The bootstrap distribution of the difference, on the same arrays,
    # vectorised with the original rng call (tile order = list(set)).
    from n1_baseline_leaderboard_tiering import permutation_test_float
    pt = permutation_test_float(A[:, 0], A[:, 1], A[:, 2], B[:, 0], B[:, 1], B[:, 2], 10000, 42)
    out["permutation_on_old_arrays"] = pt
print(json.dumps(out, indent=1, default=float))
