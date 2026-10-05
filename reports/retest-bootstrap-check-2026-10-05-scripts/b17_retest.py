# ruff: noqa  (kept verbatim as provenance of reports/retest-bootstrap-check-2026-10-05.md)
"""W2.4: re-test B-17/B-18 (PV verifier-thinking comparisons) read-only.

Rebuilds each variant's accepted set with evaluate_pv_results._load_variant_gdf
(the producer's own loader), tries the plausible bounds files until the
library bootstrap reproduces the committed bootstrap mean, then runs the
permutation test on the same per-tile arrays.
"""
import json
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np

REPO = Path.home() / "Code/map-reader-llm"
sys.path.insert(0, str(REPO / "scripts"))
import evaluate_pv_results as ev  # noqa: E402
from lib_advanced_metrics import bootstrap_effect_size_ci, compute_per_tile_tp_fp_fn  # noqa: E402
from n1_baseline_leaderboard_tiering import permutation_test_float  # noqa: E402

out = {}
for track in ("text", "image"):
    comp = json.loads((REPO / f"results/h11-384-pv-diagnostic/pairwise/pro-proposer-verifier-thinking-{track}/comparison.json").read_text())
    va, vb = comp["variants"]
    # Recorded paths were renamed after March: map by the run.meta thinking
    # level (minimal vs medium; both Flash) and confirm by reproduction.
    root = REPO / "outputs/h11/pv-diag-384"
    va = dict(va, probabilities_file=str(root / f"verified/pro-{track}-minimal-verifier/probabilities.json"),
              manifest_file=str(root / f"crops/pro-medium-{track}-baseline/candidate_manifest.json"))
    vb = dict(vb, probabilities_file=str(root / f"verified/pro-{track}-medium-verifier/probabilities.json"),
              manifest_file=str(root / f"crops/pro-medium-{track}-baseline/candidate_manifest.json"))
    committed = comp["pairwise"][0]["f1_difference"]
    ref = gpd.read_file(REPO / "inputs/vectors/references/mounds-reference.geojson")
    for bpath in ("inputs/vectors/bounds/384/full_evaluation_bounds.geojson",
                  "inputs/vectors/bounds/full_evaluation_bounds.geojson",
                  "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"):
        bounds = gpd.read_file(REPO / bpath)
        ga, gb = ev._load_variant_gdf(va, bounds), ev._load_variant_gdf(vb, bounds)
        eff = bootstrap_effect_size_ci(ga, bounds, gb, bounds, ref, n_iterations=1000,
                                       random_seed=42, return_p_values=True)
        f = eff["f1_difference"]
        rec = {"bounds": bpath, "repro_mean": f["mean"], "repro_p": f["p_value"],
               "committed_mean": committed["mean"], "committed_p": committed["p_value"]}
        if abs(f["mean"] - committed["mean"]) < 0.002:
            order = list(bounds["tile_name"].unique())
            ta = compute_per_tile_tp_fp_fn(ga, ref, bounds, 20).set_index("tile_name").loc[order, ["tp", "fp", "fn"]].to_numpy(float)
            tb = compute_per_tile_tp_fp_fn(gb, ref, bounds, 20).set_index("tile_name").loc[order, ["tp", "fp", "fn"]].to_numpy(float)
            pt = permutation_test_float(ta[:, 0], ta[:, 1], ta[:, 2], tb[:, 0], tb[:, 1], tb[:, 2], 10_000, 42)
            rec.update({"perm_p": pt["p_value"], "obs_diff": pt["observed_diff"], "f1_a": pt["f1_a"],
                        "f1_b": pt["f1_b"], "k_discordant": int((ta != tb).any(1).sum()),
                        "n_tiles": len(order)})
            out[track] = rec
            break
        out.setdefault(track + "_tries", []).append(rec)
print(json.dumps(out, indent=1, default=float))
Path("/tmp/w2/b17_retest.json").write_text(json.dumps(out, indent=1, default=float))
