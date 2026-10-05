"""W2.4: re-test the 70 rows of results/retest/pairwise-bootstrap-comparisons.json.

Read-only. For each row, rebuilds the exact inputs the March session used
(first file of sorted(rglob('detections_*.geojson')) per condition; the two
consensus sets of rows 68-69 from the Era-1 Stage B board cells, whose deltas
match the committed rows), scores them on the board path (validated identical
to the historical scorer on all 319 Era-1 passes), then runs:
  - the retest bootstrap exactly as coded (B=1000, seed 42) as a reproduction
    check against the committed delta and p;
  - the paired tile-swap permutation test (permutation_test_float, 10k, seed
    42) for F1, plus the same swap masks for precision and recall;
  - a look-up of the board's own p for the pair (Stage A tiering_20m.json for
    pass-mean single-pass cells; Stage B results/era1-leaderboard for 68-69).
"""
import json
import os
import sys
from datetime import datetime, timezone
from multiprocessing import Pool
from pathlib import Path

import numpy as np

REPO = Path.home() / "Code/map-reader-llm"
os.chdir(REPO)
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, "/tmp/w2")

from w23_tests import retest_bootstrap, prf  # noqa: E402
from n1_baseline_leaderboard_tiering import permutation_test_float  # noqa: E402

RUN_T = datetime(2026, 3, 18, 6, 30, tzinfo=timezone.utc).timestamp()
PHASES = {
    "Phase 2a: H1 Modality": ("phase2a", "retest-phase2a::{c}"),
    "Phase 2b T1: H7 Temperature (Image)": ("phase2b/track1-image", "retest-phase2b::image-{cl}"),
    "Phase 2b T2: H7 Temperature (Text)": ("phase2b/track2-text", "retest-phase2b::text-{cl}"),
    "Phase 2c T1: H8 Library (Image)": ("phase2c/track1-image", "retest-phase2c::image-{c}"),
    "Phase 2c T2: H8 Library (Text)": ("phase2c/track2-text", "retest-phase2c::text-{c}"),
    "Phase 2c Exp: HP Scaling": ("phase2c/track1-image-exploratory", "retest-phase2c::image-exploratory-{c}"),
    "Phase 2d T1: H5 Negtext (Image)": ("phase2d/track1-image", "retest-phase2d::image-{c}"),
    "Phase 2d T2: H5 Negtext (Text)": ("phase2d/track2-text", "retest-phase2d::text-{c}"),
    "Phase 2e: H4 Ordering": ("phase2e", "retest-phase2e::{c}"),
    "Phase 3a T1: Voting (Image)": ("phase3a/track1-image", None),
    "Phase 3a T2: Voting (Text)": ("phase3a/track2-text", None),
    "Phase 3a Replication": ("phase3a-replication", None),
}
CELL68 = {"consensus_T0.7_18of30_image": "retest-phase3a::image-t0.7-n30-18of30",
          "single_pass_canonical_last": "retest-phase2e::canonical-last",
          "high_consensus_21of30": "retest-phase3a-replication::text-high-t0.7-n30-21of30",
          "minimal_consensus_25of30": "retest-phase3a-replication::text-minimal-t0.7-n30-25of30"}


def first_file(subdir, cond):
    files = sorted((REPO / "outputs/retest" / subdir / cond).rglob("detections_*.geojson"))
    return files[0]


def perm_prf(a, b, n=10_000, seed=42):
    """Same swap masks as permutation_test_float; returns p for P, R, F1."""
    rng = np.random.default_rng(seed)
    swap = rng.random((n, a.shape[0])) < 0.5
    sa = np.stack([np.where(swap, b[:, j], a[:, j]).sum(1) for j in range(3)], axis=1)
    sb = np.stack([np.where(swap, a[:, j], b[:, j]).sum(1) for j in range(3)], axis=1)
    pa, ra, fa = prf(sa.astype(float))
    pb, rb, fb = prf(sb.astype(float))
    p0a, r0a, f0a = prf(a.sum(0)[None, :].astype(float))
    p0b, r0b, f0b = prf(b.sum(0)[None, :].astype(float))
    out = {}
    for name, null, obs in (("prec", pa - pb, p0a - p0b), ("rec", ra - rb, r0a - r0b),
                            ("f1", fa - fb, f0a - f0b)):
        out[name] = float(np.mean(np.abs(null) >= abs(obs[0])))
    return out


def board_cell_arrays(ref, gdf_ref, gdf_bounds, order):
    from era1_leaderboard_tiering import cell_per_tile, resolve_condition
    cond = resolve_condition(REPO / "results/run-conditions.json", ref)
    meta = json.loads((REPO / cond["eval_path"]).read_text())["_metadata"]
    cli = dict(meta.get("cli_args") or {})
    if not (cli.get("detections") or cli.get("detections_dir")):
        fb = (meta.get("input_files") or {}).get("detections")
        if isinstance(fb, str):
            cli["detections_dir"] = fb
        elif isinstance(fb, list):
            cli["detections"] = fb
    tp, fp, fn, k = cell_per_tile(cli, gdf_ref, gdf_bounds, order, 20)
    return np.stack([tp, fp, fn], 1), k, cli


def work(i_row):
    import geopandas as gpd
    from era1_leaderboard_tiering import _per_tile_one_set, _read_detections_gdf
    from n1_baseline_leaderboard_tiering import TARGET_CRS
    from pairwise_permutation_test import assign_source_tiles
    i, row = i_row
    gdf_ref = gpd.read_file("inputs/vectors/references/mounds-reference.geojson").to_crs(TARGET_CRS)
    gdf_bounds = gpd.read_file("inputs/vectors/bounds/full_evaluation_bounds.geojson").to_crs(TARGET_CRS)
    order = list(gdf_bounds["tile_name"].unique())
    out = {"i": i, "phase": row["phase"], "a": row["condition_a"], "b": row["condition_b"],
           "committed_f1_delta": row["f1_delta"], "committed_f1_p": row["f1_p_value"],
           "committed_prec_p": row["precision_p"], "committed_rec_p": row["recall_p"]}
    arrs, srcs = [], []
    for side in ("condition_a", "condition_b"):
        c = row[side]
        if row["phase"] in PHASES:
            sub = PHASES[row["phase"]][0]
            f = first_file(sub, c)
            g = assign_source_tiles(_read_detections_gdf(f), gdf_bounds)
            tp, fp, fn = _per_tile_one_set(g, gdf_ref, gdf_bounds, order, 20)
            arrs.append(np.stack([tp, fp, fn], 1))
            srcs.append({"file": str(f.relative_to(REPO)),
                         "modified_after_run": os.path.getmtime(f) > RUN_T,
                         "mtime": datetime.fromtimestamp(os.path.getmtime(f), timezone.utc).isoformat()})
        else:
            if c == "single_pass_canonical_last":
                f = REPO / "outputs/retest/phase2e/canonical-last/run_1/detections_canonical-last_run01.geojson"
                g = assign_source_tiles(_read_detections_gdf(f), gdf_bounds)
                tp, fp, fn = _per_tile_one_set(g, gdf_ref, gdf_bounds, order, 20)
                arrs.append(np.stack([tp, fp, fn], 1))
                srcs.append({"file": str(f.relative_to(REPO)),
                             "modified_after_run": os.path.getmtime(f) > RUN_T})
            else:
                arr, k, cli = board_cell_arrays(CELL68[c], gdf_ref, gdf_bounds, order)
                arrs.append(arr)
                srcs.append({"board_cell": CELL68[c], "detections": cli.get("detections")})
    a, b = arrs
    out["sources"] = srcs
    out["k_discordant"] = int((a != b).any(1).sum())
    bt = retest_bootstrap(a, b)
    out["repro_boot_mean"] = bt["boot_mean"]
    out["repro_boot_p_f1"] = bt["boot_p_f1"]
    out["repro_boot_p_prec"] = bt["boot_p_prec"]
    out["repro_boot_p_rec"] = bt["boot_p_rec"]
    out["repro_boot_ci"] = [bt["boot_ci_lo"], bt["boot_ci_hi"]]
    pt = permutation_test_float(a[:, 0], a[:, 1], a[:, 2], b[:, 0], b[:, 1], b[:, 2], 10_000, 42)
    out["obs_f1_a"], out["obs_f1_b"], out["obs_diff"] = pt["f1_a"], pt["f1_b"], pt["observed_diff"]
    out["perm_p_f1"] = pt["p_value"]
    pp = perm_prf(a, b)
    out["perm_p_prec"], out["perm_p_rec"], out["perm_p_f1_check"] = pp["prec"], pp["rec"], pp["f1"]
    return out


if __name__ == "__main__":
    rows = json.loads((REPO / "results/retest/pairwise-bootstrap-comparisons.json").read_text())["comparisons"]
    with Pool(20) as pool:
        res = pool.map(work, list(enumerate(rows)), chunksize=1)
    # Board look-ups.
    sa = json.loads((REPO / "results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.json").read_text())
    sb = json.loads((REPO / "results/era1-leaderboard/tiering_20m.json").read_text())
    def lut(board):
        return {frozenset((r["ref_a"], r["ref_b"])): r for r in board["pairwise"]}
    la, lb = lut(sa), lut(sb)
    for r in res:
        ph = PHASES.get(r["phase"])
        refs = None
        if ph and ph[1]:
            tmpl = ph[1]
            refs = [tmpl.format(c=c, cl=c.lower()) for c in (r["a"], r["b"])]
        elif r["a"] in CELL68:
            refs = [CELL68[r["a"]], CELL68[r["b"]]]
        r["board_refs"] = refs
        hit = None
        if refs:
            k = frozenset(refs)
            hit = la.get(k) or lb.get(k)
            r["board"] = "stageA" if k in la else ("stageB" if k in lb else None)
        if hit:
            r["board_p"] = hit["p_value"]
            r["board_bh_p"] = hit.get("bh_adjusted_p")
            r["board_diff_a_minus_b"] = hit["observed_diff"] if hit["ref_a"] == refs[0] else -hit["observed_diff"]
    Path("/tmp/w2/retest70.json").write_text(json.dumps(res, indent=1, default=str))
    for r in res:
        print(r["i"], r["phase"][:20], r["a"][:18], r["b"][:18], "dF1 %.4f/%.4f" % (r["committed_f1_delta"], r["obs_diff"]),
              "bootP %.3f->%.3f" % (r["committed_f1_p"], r["repro_boot_p_f1"]), "perm %.4f" % r["perm_p_f1"],
              "board", r.get("board_p"), "k", r["k_discordant"],
              "MOD" if any(s.get("modified_after_run") for s in r["sources"]) else "")
