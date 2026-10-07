"""Count each K-ladder rung's candidates in the frame-difference strip, and
recompute sweep points under both frames with the project's own scorer.

Read-only. Usage: python strip_detections.py <repo_root>
"""

import json
import sys
from pathlib import Path

import geopandas as gpd

root = Path(sys.argv[1])
sys.path.insert(0, str(root))
from scripts.lib_advanced_metrics import calculate_f1_internal  # noqa: E402
from scripts.run_k_ladder_phase2_verifier import UNIONS_JSON, resolve_paths  # noqa: E402
from scripts.sweep_f1_wbf import load_candidates_as_gdf, load_ground_truth  # noqa: E402

crs = "EPSG:32635"
board = gpd.read_file(root / "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson").to_crs(
    crs
)
era2 = gpd.read_file(root / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson").to_crs(crs)
ub, ue = board.geometry.union_all(), era2.geometry.union_all()
strip = ue.difference(ub)
gt = load_ground_truth()
ops = {
    r["row"]: r
    for r in json.load(open(root / "results/k-ladder-2026-09-12/phase2/operating-points.json"))[
        "rungs"
    ]
}
rungs = json.load(open(UNIONS_JSON))["rungs"]

print("row run K cands in_strip outside_era2 | at-opmax: n in_strip outside_era2")
tot_strip = tot_strip_op = 0
for r in rungs:
    p = resolve_paths(r)
    c = load_candidates_as_gdf(
        root / p["crops_dir"] / "candidate_manifest.json",
        root / p["verify_dir"] / "probabilities.json",
    )
    op = ops[r["row"]]["opmax"]
    sel = c[(c.vote_count >= op["vote_t"]) & (c.mound_probability >= op["prob_t"])]
    s_all, o_all = int(c.within(strip).sum()), int((~c.intersects(ue)).sum())
    s_op, o_op = int(sel.within(strip).sum()), int((~sel.intersects(ue)).sum())
    tot_strip += s_all
    tot_strip_op += s_op
    print(
        r["row"], r["run_id"][:14], r["n_passes"], len(c), s_all, o_all, "|", len(sel), s_op, o_op
    )
    if r["row"] in (1, 27):
        # Direct recompute at the opmax point and at the loosest point, both frames,
        # plus a counterfactual that clips detections to each frame's geometry.
        for vt, pt in ((op["vote_t"], op["prob_t"]), (1, 0.0)):
            sub = c[(c.vote_count >= vt) & (c.mound_probability >= pt)]
            for name, fr, u in (("board", board, ub), ("era2", era2, ue)):
                prf = calculate_f1_internal(sub, gt, fr, buffer_metres=20)
                prf_c = calculate_f1_internal(sub[sub.intersects(u)], gt, fr, buffer_metres=20)
                print(
                    f"   recompute row {r['row']} ({vt},{pt}) {name}: n={len(sub)} "
                    f"P/R/F1={tuple(round(x, 4) for x in prf)}  "
                    f"[clipped-to-geometry n={int(sub.intersects(u).sum())} "
                    f"F1={round(prf_c[2], 4)}]"
                )
        sweep = json.load(open(root / ops[r["row"]]["sweep_board_frame"]))
        for vt, pt in ((op["vote_t"], op["prob_t"]), (1, 0.0)):
            row = [
                x for x in sweep if x["buffer_m"] == 20 and x["vote_t"] == vt and x["prob_t"] == pt
            ][0]
            print(f"   committed sweep row ({vt},{pt}) @20: {row}")
print("total candidates in strip, all rungs:", tot_strip, "; at opmax:", tot_strip_op)
