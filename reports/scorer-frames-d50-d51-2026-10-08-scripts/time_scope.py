"""Time calculate_f1_internal per call, old (main) vs new (branch), on a real universe.

D50/D51 impact measurement, 2026-10-08 (Session 163). Read-only.

Imports ``lib_advanced_metrics`` twice under distinct module names, from the
``main`` checkout (OLD) and from the branch worktree (NEW), and times 20 calls of
each on two Gemini 3.7 candidate universes, plus the D50 scope on its own. The
paths are sapphire's (``~/Code/map-reader-llm`` and the disposable worktree).

Usage::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python time_scope.py
"""
import importlib.util
import sys
import time
from pathlib import Path

import geopandas as gpd

MAIN = Path.home() / "Code/map-reader-llm"
WT = Path.home() / "worktrees/map-reader-llm/claude-scorer-d50"


def load(name: str, root: Path):
    """Import lib_advanced_metrics from a given checkout under a unique name."""
    spec = importlib.util.spec_from_file_location(name, root / "scripts/lib_advanced_metrics.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


old, new = load("lam_old", MAIN), load("lam_new", WT)
sys.path.insert(0, str(WT))
import scripts.sweep_f1_wbf as wbf  # noqa: E402

VR = WT / "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37"
for crops, verify in (("crops_k3_recovery-fixed", "verify_k3_recovery-fixed"),
                      ("crops_k10", "verify_k10")):
    cands = wbf.load_candidates_as_gdf(VR / crops / "candidate_manifest.json",
                                       VR / verify / "probabilities.json")
    gt = wbf.load_ground_truth()
    bounds = gpd.read_file(WT / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson")
    for label, mod in (("old", old), ("new", new)):
        t0 = time.perf_counter()
        for _ in range(20):
            res = mod.calculate_f1_internal(cands, gt, bounds, buffer_metres=20)
        print(crops, len(cands), label, f"{(time.perf_counter() - t0) / 20 * 1000:.1f} ms/call",
              tuple(round(x, 4) for x in res))
    t0 = time.perf_counter()
    for _ in range(20):
        new.scope_detections_to_frame(cands, bounds)
    print("  scope alone", f"{(time.perf_counter() - t0) / 20 * 1000:.1f} ms/call")
