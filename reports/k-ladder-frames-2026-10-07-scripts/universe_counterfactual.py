"""Score GS-ladder rung detections on the board frame under three candidate
universes: as committed; clipped to the board frame's geometry; clipped to the
grid-common footprint (the universe the committed K = 5 / K = 10 rungs carry).

Read-only; the project's own point scorer. Usage: python universe_counterfactual.py <repo_root>
"""

import json
import sys
from pathlib import Path

import geopandas as gpd

root = Path(sys.argv[1])
sys.path.insert(0, str(root))
from scripts.lib_advanced_metrics import calculate_f1_internal  # noqa: E402
from scripts.sweep_f1_wbf import load_ground_truth  # noqa: E402

crs = "EPSG:32635"
board = gpd.read_file(root / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson").to_crs(
    crs
)
ub = board.geometry.union_all()
ug = (
    gpd.read_file(root / "outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson")
    .to_crs(crs)
    .geometry.union_all()
)
gt = load_ground_truth()


def score(path: str, label: str) -> None:
    """Print n and P/R/F1@20 for one detections file under the three universes."""
    det = gpd.read_file(root / path).to_crs(crs)
    if "source_tile" not in det.columns:
        print(label, "no source_tile column; skipped")
        return
    out = []
    for name, mask in (("committed", None), ("clip-board", ub), ("clip-gridcommon", ug)):
        sub = det if mask is None else det[det.intersects(mask)]
        p, r, f = calculate_f1_internal(sub, gt, board, buffer_metres=20)
        out.append(f"{name}: n={len(sub)} P={p:.4f} R={r:.4f} F1={f:.4f}")
    print(f"{label:34s} | " + " | ".join(out))


L = json.load(open(root / "results/k-ladder-2026-09-12/phase2/ladders.json"))
for lad in L["ladders"]:
    if lad["run_id"] != "gemini37-screen-2026-08-28":
        continue
    for rg in lad["rungs"]:
        det = rg["opmax"].get("detections")
        if not det:
            det = (
                "results/k-ladder-2026-09-12/phase2/g37-opmax/materialised/"
                f"g37-text-k{rg['K']}-verified-opmax.geojson"
            )
        score(det, f"3.7 K={rg['K']} opmax")
T = json.load(open(root / "results/k-ladder-2026-09-12/tier-e/operating-points.json"))
for rg in T["rungs"]:
    score(rg["opmax"]["detections"], f"tier E K={rg['K']} opmax")
