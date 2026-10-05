# ruff: noqa  (kept verbatim as provenance of reports/retest-bootstrap-check-2026-10-05.md)
"""W2.4: re-test fair-384-vs-512.json (class B) with the permutation test.

Read-only harness: loads scripts/compare-384-vs-512.py, wraps its
bootstrap_effect_size_ci to also run permutation_test_float on the same
per-tile arrays (computed by the same compute_per_tile_tp_fp_fn on the common
tiles), and redirects the script's single write to /tmp/w2/c2/fair384/.
"""
import builtins
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path.home() / "Code/map-reader-llm"
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
from lib_advanced_metrics import bootstrap_effect_size_ci as orig, compute_per_tile_tp_fp_fn  # noqa: E402
from n1_baseline_leaderboard_tiering import permutation_test_float  # noqa: E402

OUT = Path("/tmp/w2/c2/fair384")
OUT.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location("cmp384", REPO / "scripts/compare-384-vs-512.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
captured = []


def wrapped(gdf_det_a, gdf_bounds_a, gdf_det_b, gdf_bounds_b, gdf_ref, **kw):
    eff = orig(gdf_det_a, gdf_bounds_a, gdf_det_b, gdf_bounds_b, gdf_ref, **kw)
    order = list(gdf_bounds_a["tile_name"].unique())
    ta = compute_per_tile_tp_fp_fn(gdf_det_a, gdf_ref, gdf_bounds_a, 20).set_index("tile_name").loc[order, ["tp", "fp", "fn"]].to_numpy(float)
    tb = compute_per_tile_tp_fp_fn(gdf_det_b, gdf_ref, gdf_bounds_b, 20).set_index("tile_name").loc[order, ["tp", "fp", "fn"]].to_numpy(float)
    pt = permutation_test_float(ta[:, 0], ta[:, 1], ta[:, 2], tb[:, 0], tb[:, 1], tb[:, 2], 10_000, 42)
    captured.append({"boot_mean": eff["f1_difference"]["mean"], "boot_p": eff["f1_difference"]["p_value"],
                     "perm_p": pt["p_value"], "obs": pt["observed_diff"],
                     "k_discordant": int((ta != tb).any(1).sum()), "n_tiles": len(order)})
    return eff


def redirected_open(path, mode="r", *a, **k):
    p = Path(path)
    if "w" in mode and str(p).startswith(str(REPO)):
        p = OUT / p.name
    return builtins.open(p, mode, *a, **k)


mod.bootstrap_effect_size_ci = wrapped
mod.open = redirected_open
# The script's March data layout (outputs/references) is gone; the same
# reference files live in inputs/vectors/references (unchanged since March).
_lsd = mod.load_shared_data
mod.load_shared_data = lambda _d: _lsd(REPO / "inputs" / "vectors")
mod.main()
(OUT / "permutation_capture.json").write_text(json.dumps(captured, indent=1, default=float))
for c in captured:
    print(c)
