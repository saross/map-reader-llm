"""The 3.7 GS and tier E K-ladders under D50 and D51, and a gate survey.

D50/D51 impact measurement, 2026-10-08 (Session 163). Read-only.

For each ladder rung's reported point(s) this script records, at the 20 m
headline buffer on the board frame (``era2_b_intersection_bounds``):

* ``committed`` — the cell's committed ``evaluation.json`` F1;
* ``d50`` — the NEW scorer on the cell's own detections (detections scoped per
  sheet on their origin sheet; for tier E this restores the 6-7 detections
  its re-key moved across a sheet edge);
* ``d51_clipped`` — the same with the detections clipped to the area common
  to every rung of the ladder, the frame's reference set kept (option 1 of
  ruling D51), at the rung's own committed operating point;
* ``d51_matched_sweep`` — the rung's whole candidate universe clipped to that
  common area and swept again (vote_t x prob_t, 20 m, the K-ladder tie-break),
  to show whether the operating point itself moves under matched areas.

The common area comes from the library's own gate
(``lib_assessed_area.compare_assessed_areas`` with ``clip_to_common``), so the
numbers are exactly what ``build_k_ladder_phase2_tables.py
--clip-to-common-area`` and the sweep drivers would produce.

Finally it runs the D51 gate, unclipped and allowing undetermined pools, over
every Phase 2 ladder (``build_k_ladder_phase2_tables.build``) and tier E, and
records each verdict.

Usage::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python ladders_new.py \
        --code WORKTREE --out out/ladders_new.json
"""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meas_lib as ml  # noqa: E402

BOARD = "inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson"
GT = "inputs/vectors/references/mounds-reference.geojson"
VR = "outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37"
GRID = "outputs/grid-2026-08-18/verifier/g384_ov192"
TIER_E = "results/k-ladder-2026-09-12/tier-e"

#: Candidate universes swept per rung: (crops dir, verify dir). The 3.7 pairs are
#: the blast radius's sweep jobs and derive_g37_gs_opmax_rungs.STAGES; tier E's
#: are its operating points and COMMITTED_K10's verify tree.
UNIVERSES = {
    ("g37", 1): (f"{VR}/crops_k1", f"{VR}/verify_k1"),
    ("g37", 3): (f"{VR}/crops_k3_recovery-fixed", f"{VR}/verify_k3_recovery-fixed"),
    ("g37", 5): (f"{VR}/crops", f"{VR}/verify"),
    ("g37", 10): (f"{VR}/crops_k10", f"{VR}/verify_k10"),
    ("tierE", 1): (f"{GRID}/k-ladder/k1/crops", f"{GRID}/k-ladder/k1"),
    ("tierE", 3): (f"{GRID}/k-ladder/k3/crops", f"{GRID}/k-ladder/k3"),
    ("tierE", 5): (f"{GRID}/k-ladder/k5/crops", f"{GRID}/k-ladder/k5"),
    ("tierE", 10): (f"{GRID}/crops", f"{GRID}/verify"),
}


def f1_at_20(eval_path: Path) -> float | None:
    """The committed F1 at 20 m of an evaluation."""
    summary = json.loads(eval_path.read_text()).get("summary") or {}
    for row in summary.get("buffers") or []:
        if row.get("buffer_metres") == 20:
            return row.get("f1")
    return None


def detections_of(eval_path: Path) -> list[str]:
    """The detection files an evaluation recorded."""
    meta = json.loads(eval_path.read_text()).get("_metadata") or {}
    dets = (meta.get("input_files") or {}).get("detections") or \
        (meta.get("cli_args") or {}).get("detections")
    return dets if isinstance(dets, list) else [dets]


def score(paths: list[str], code: Path, bounds: Any, ref: Any,
          clip: Any = None) -> dict[str, Any]:
    """NEW F1/P/R at 20 m (mean over files), optionally clipped to an area."""
    from scripts.lib_assessed_area import clip_points_to_area  # noqa: PLC0415

    vals, removed, n = [], 0, 0
    for p in paths:
        det = ml.load_detections(ml.resolve(code, p), bounds)
        if clip is not None:
            det, k = clip_points_to_area(det, clip)
            removed += k
        n += len(det)
        vals.append(ml.LIB.calculate_f1_internal(det, ref, bounds, buffer_metres=20))
    m = len(vals)
    return {"precision": sum(v[0] for v in vals) / m, "recall": sum(v[1] for v in vals) / m,
            "f1": sum(v[2] for v in vals) / m, "n_detections": n, "n_removed": removed}


def matched_sweep(code: Path, crops: str, verify: str, bounds: Any, clip: Any) -> dict:
    """Sweep a rung's universe clipped to the common area; argmax at 20 m."""
    import scripts.sweep_f1_greedy_pv as sweep_mod  # noqa: PLC0415
    import scripts.sweep_f1_wbf as wbf_mod  # noqa: PLC0415
    from scripts.lib_assessed_area import clip_points_to_area  # noqa: PLC0415

    cands = wbf_mod.load_candidates_as_gdf(code / crops / "candidate_manifest.json",
                                           code / verify / "probabilities.json")
    gt = wbf_mod.load_ground_truth()
    clipped, removed = clip_points_to_area(cands, clip)
    votes = list(range(1, int(cands["vote_count"].max()) + 1))
    rows = sweep_mod.run_sweep("matched", clipped, gt, bounds, buffer_m=20,
                               vote_thresholds=votes)
    full = sweep_mod.run_sweep("unclipped", cands, gt, bounds, buffer_m=20,
                               vote_thresholds=votes)
    best = max(rows, key=lambda r: (r["f1"], -r["vote_t"], -r["prob_t"]))
    best_full = max(full, key=lambda r: (r["f1"], -r["vote_t"], -r["prob_t"]))
    return {"universe": len(cands), "clipped_out": removed,
            "argmax": {k: best[k] for k in ("vote_t", "prob_t", "f1", "n")},
            "unclipped_argmax_d50": {k: best_full[k] for k in ("vote_t", "prob_t", "f1",
                                                               "n")}}


def ladder(code: Path, name: str, rungs: list[dict[str, Any]], bounds: Any, ref: Any,
           lib_area: Any) -> dict[str, Any]:
    """Gate a ladder's pools, then score every point committed / D50 / D51."""
    areas = [lib_area.determine_assessed_area(r["pool"], label=f"K = {r['K']}")
             for r in rungs]
    comparison = lib_area.compare_assessed_areas(areas, frame=BOARD, clip_to_common=True)
    common = comparison.common
    out_rungs = []
    for r in rungs:
        points = {}
        for label, pt in r["points"].items():
            points[label] = {
                "vote_t": pt["vote_t"], "prob_t": pt["prob_t"],
                "committed_f1_20": pt.get("committed"),
                "d50": score(pt["detections"], code, bounds, ref),
                "d51_clipped": score(pt["detections"], code, bounds, ref, clip=common),
            }
        crops, verify = UNIVERSES[(name, r["K"])]
        out_rungs.append({"K": r["K"], "pool": r["pool"], "points": points,
                          "d51_matched_sweep": matched_sweep(code, crops, verify, bounds,
                                                             common)})
        print(name, r["K"], json.dumps({k: (v["committed_f1_20"], round(v["d50"]["f1"], 4),
                                            round(v["d51_clipped"]["f1"], 4))
                                        for k, v in points.items()}),
              out_rungs[-1]["d51_matched_sweep"]["argmax"], flush=True)
    return {"ladder": name, "assessed_area": comparison.record, "rungs": out_rungs}


def main() -> int:
    """Measure both ladders and run the gate survey."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    code = args.code.expanduser().resolve()
    ml.setup(code)
    import scripts.build_k_ladder_phase2_tables as tables  # noqa: PLC0415
    import scripts.lib_assessed_area as lib_area  # noqa: PLC0415

    bounds = ml.load_geojson(code / BOARD)
    ref = ml.load_geojson(code / GT)
    result: dict[str, Any] = {}

    # --- The 3.7 GS ladder: its committed opmax points (ladders.json) --------
    lad = next(x for x in json.loads((code / "results/k-ladder-2026-09-12/phase2/"
                                              "ladders.json").read_text())["ladders"]
               if x["proposer_pool"] == "g384_ov192_g37")
    pools = {**tables.new_rung_pools("g384_ov192_g37"),
             **tables.committed_sibling_pools("g384_ov192_g37")}
    rungs = []
    for rung in lad["rungs"]:
        pts = {}
        for label, pt in (("opmax", rung["opmax"]),
                          ("carried", rung["carried"]["stride-shell"])):
            ev = code / pt["eval_path"]
            pts[label] = {"vote_t": pt["vote_t"], "prob_t": pt["prob_t"],
                          "committed": f1_at_20(ev), "detections": detections_of(ev)}
        rungs.append({"K": rung["K"], "pool": pools[rung["K"]], "points": pts})
    result["g37_gs"] = ladder(code, "g37", rungs, bounds, ref, lib_area)

    # --- Tier E: its operating points and the committed K = 10 rung ----------
    ops = json.loads((code / TIER_E / "operating-points.json").read_text())
    rungs = []
    for rung in ops["rungs"]:
        pts = {}
        for label in ("opmax", "carried"):
            pt = rung[label]
            ev = code / TIER_E / "cells" / pt["cell"] / "evaluation.json"
            pts[label] = {"vote_t": pt["vote_t"], "prob_t": pt["prob_t"],
                          "committed": f1_at_20(ev), "detections": [pt["detections"]]}
        rungs.append({"K": rung["K"], "pool": f"{rung['verify_dir']}/crops", "points": pts})
    k10_eval = code / TIER_E / "cells" / \
        "grid-2026-08-18__g384-ov192-k10-verified-p0_15-k10-boardframe" / "evaluation.json"
    rungs.append({"K": 10, "pool": f"{GRID}/union_k10.geojson", "points": {
        "carried": {"vote_t": 10, "prob_t": 0.15, "committed": f1_at_20(k10_eval),
                    "detections": detections_of(k10_eval)}}})
    result["tier_e"] = ladder(code, "tierE", rungs, bounds, ref, lib_area)

    # --- The gate over every Phase 2 ladder, unclipped -------------------------
    payload = tables.build()
    survey = []
    for lad in payload["ladders"]:
        one = {"ladders": [copy.deepcopy(lad)]}
        messages = tables.apply_area_gate(one, allow_undetermined=True)
        record = one["ladders"][0].get("assessed_area") or {}
        survey.append({
            "family": lad["family"], "pool": lad["proposer_pool"],
            "status": record.get("status"), "common_area_km2": record.get("common_area_km2"),
            "max_excess_km2": record.get("max_excess_km2"),
            "undetermined": record.get("undetermined"),
            "pools": [{k: p.get(k) for k in ("label", "method", "effective_area_km2",
                                             "excess_over_common_km2", "reason", "warnings")}
                      for p in record.get("pools", [])],
            "messages": messages,
        })
        print("survey", lad["proposer_pool"], record.get("status"),
              record.get("max_excess_km2"), record.get("undetermined"), flush=True)
    result["phase2_gate_survey"] = survey
    args.out.write_text(json.dumps(result, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
