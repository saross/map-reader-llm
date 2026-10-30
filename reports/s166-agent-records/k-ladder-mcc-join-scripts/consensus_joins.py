#!/usr/bin/env python3
"""
§ 8.6's consensus-only side under the three tile joins: the grid sweep of cell g384_ov192, replayed.

Part of the S166 K-ladder tile-join job
(``reports/s166-agent-records/k-ladder-mcc-join.md``). K-ladder findings
§ 8.6 sets the consensus-only K = 1 -> 10 tile-MCC change on the grid study's
384 px / 50 % cell (+0.0444, ``tension/grid-overlap.json``, cell
``g384_ov192``) against the verified tier E change. That number comes from
``scripts/grid_analysis.py``'s sweep: for each K (the first K of ten passes),
each corroboration level ``c`` and each vote threshold ``k``, the cluster
centroids are booked to a carrier tile on their own sheet and scored by
``lib_advanced_metrics.score_detection_set`` on the grid-common carrier frame
at 20 m. ``k_ladder_tension_analyses.cmd_grid_overlap`` then takes, per K, the
row with the best F1.

This replays exactly that sweep for ``g384_ov192`` with the module's own
functions (``load_cell_passes``, ``cluster_votes_with_members``, ``as_gdf``),
scoring every detection set three times, once per tile join (the scorer's
``tile_join`` argument). F1 does not depend on the join, so the selected
operating point per K is the same under all three, and that is checked.

**Gate.** Under ``id`` every one of the cell's 57 sweep rows must equal the
committed ``results/grid-2026-08-18/sweep.csv`` row exactly (detection count,
and precision, recall, F1 and MCC as the CSV's float text), and the
selected rungs must equal ``tension/grid-overlap.json`` at its six decimals.
The script exits 3 if not, and reports nothing on that join.

Usage: python consensus_joins.py <clone_root> <out_json>

Author: Shawn Ross, Claude Code (S166). Licence: Apache 2.0
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

CELL = "g384_ov192"
JOINS = ("id", "geometric-primary", "geometric-contains")


def main() -> int:
    """Replay the cell's sweep under each join, gate the id reading, write it."""
    root, target = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    sys.path.insert(0, str(root))
    import geopandas as gpd  # noqa: PLC0415
    import numpy as np  # noqa: PLC0415

    import scripts.grid_analysis as ga  # noqa: PLC0415
    from scripts.lib_advanced_metrics import score_detection_set  # noqa: PLC0415

    scoring_dir = root / "outputs/grid-2026-08-18/scoring"
    bounds = gpd.read_file(scoring_dir / "bounds" / "grid_common_bounds.geojson")
    gdf_ref = gpd.read_file(ga.GROUND_TRUTH)
    passes = ga.load_cell_passes(scoring_dir, CELL)
    print(f"{CELL}: {len(passes)} passes, {len(bounds)} carrier tiles", flush=True)

    rows: list[dict] = []
    for k_total in ga.K_LADDER:
        subset = passes[:k_total]
        for c in ga.CORROBORATION:
            centroids, votes, members = ga.cluster_votes_with_members(subset, c)
            for k in range(1, k_total + 1):
                sel = votes >= k
                gdf = ga.as_gdf(centroids[sel], bounds,
                                origins=[members[i] for i in np.flatnonzero(sel)])
                row = {"K": k_total, "min_corroboration": c, "min_votes": k}
                for join in JOINS:
                    res = score_detection_set(gdf, gdf_ref, bounds,
                                              buffer_metres=ga.BUFFER_M,
                                              tile_join=join)
                    row[join] = {key: res[key] for key in
                                 ("precision", "recall", "f1", "n_detections",
                                  "mcc", "mcc_refused_reason")}
                    if row[join]["mcc"] is not None:
                        row[join]["mcc"] = float(row[join]["mcc"])
                rows.append(row)
        print(f"  K={k_total:2d}: {len(rows)} rows so far", flush=True)

    # Gate 1: the id rows against the committed sweep, exactly.
    committed: dict[tuple[int, int, int], dict] = {}
    with open(root / "results/grid-2026-08-18/sweep.csv", newline="") as handle:
        for rec in csv.DictReader(handle):
            if rec["cell"] == CELL:
                key = (int(rec["K"]), int(rec["min_corroboration"]),
                       int(rec["min_votes"]))
                committed[key] = rec
    mismatches = []
    for row in rows:
        key = (row["K"], row["min_corroboration"], row["min_votes"])
        rec, got = committed.get(key), row["id"]
        if rec is None:
            mismatches.append({"key": key, "why": "absent from sweep.csv"})
            continue
        for field in ("precision", "recall", "f1", "mcc"):
            want = None if rec[field] == "" else float(rec[field])
            if want != got[field]:
                mismatches.append({"key": key, "field": field,
                                   "committed": rec[field], "replayed": got[field]})
        if int(rec["n_detections"]) != got["n_detections"]:
            mismatches.append({"key": key, "field": "n_detections",
                               "committed": rec["n_detections"],
                               "replayed": got["n_detections"]})
    n_rows_committed = len(committed)

    # The selected operating point per K: best F1, first maximum in sweep
    # order (cmd_grid_overlap's rule). F1 is join-independent; check it.
    f1_join_invariant = all(
        row[j]["f1"] == row["id"]["f1"] and
        row[j]["n_detections"] == row["id"]["n_detections"]
        for row in rows for j in JOINS)
    selected: dict[int, dict] = {}
    for row in rows:
        best = selected.get(row["K"])
        if best is None or row["id"]["f1"] > best["id"]["f1"]:
            selected[row["K"]] = row

    # Gate 2: the selected id rungs against tension/grid-overlap.json.
    overlap = json.loads(
        (root / "results/k-ladder-2026-09-12/tension/grid-overlap.json").read_text())
    cell = next(c for c in overlap["cells"] if c["cell"] == CELL)
    rung_mismatch = []
    for k, row in selected.items():
        want = cell["rungs"][str(k)]
        got = {"f1_20": round(row["id"]["f1"], 6), "mcc": round(row["id"]["mcc"], 6),
               "operating_point": (f"c>={row['min_corroboration']}, "
                                   f"k>={row['min_votes']}"),
               "n_detections": row["id"]["n_detections"]}
        if got != want:
            rung_mismatch.append({"K": k, "committed": want, "replayed": got})
    gate_passed = (not mismatches and not rung_mismatch
                   and len(rows) == n_rows_committed and f1_join_invariant)

    per_join = {}
    for join in JOINS:
        rungs = {str(k): {"mcc": row[join]["mcc"], "f1_20": row[join]["f1"],
                          "operating_point": (f"c>={row['min_corroboration']}, "
                                              f"k>={row['min_votes']}"),
                          "n_detections": row[join]["n_detections"],
                          "mcc_refused_reason": row[join]["mcc_refused_reason"]}
                 for k, row in sorted(selected.items())}
        mcc1, mcc10 = rungs["1"]["mcc"], rungs["10"]["mcc"]
        per_join[join] = {
            "rungs": rungs,
            "delta_f1_k1_to_k10": round(rungs["10"]["f1_20"] - rungs["1"]["f1_20"], 6),
            "delta_mcc_k1_to_k10": (None if None in (mcc1, mcc10)
                                    else round(mcc10 - mcc1, 6)),
            "n_mcc_refused": sum(1 for r in rows if r[join]["mcc_refused_reason"]),
        }
    payload = {
        "cell": CELL,
        "scope": ("consensus-only grid sweep, 384 px / 50 %, MINIMAL text T 0.7, "
                  "grid-common carrier frame, 20 m, best F1@20 over (c, k) per K"),
        "source_rule": "scripts/grid_analysis.py sweep; "
                       "scripts/k_ladder_tension_analyses.py cmd_grid_overlap",
        "gate": {
            "passed": bool(gate_passed),
            "n_rows_replayed": len(rows),
            "n_rows_committed": n_rows_committed,
            "row_mismatches": mismatches,
            "rung_mismatches": rung_mismatch,
            "f1_and_count_join_invariant": bool(f1_join_invariant),
            "reference": ["results/grid-2026-08-18/sweep.csv",
                          "results/k-ladder-2026-09-12/tension/grid-overlap.json"],
        },
        "per_join": per_join if gate_passed else None,
        "rows": rows,
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"gate {'PASSED' if gate_passed else 'FAILED'}: {len(mismatches)} row "
          f"mismatch(es), {len(rung_mismatch)} rung mismatch(es)", flush=True)
    if gate_passed:
        for join in JOINS:
            p = per_join[join]
            print(f"  {join:20s} MCC K1 {p['rungs']['1']['mcc']:.6f} K10 "
                  f"{p['rungs']['10']['mcc']:.6f} delta {p['delta_mcc_k1_to_k10']:+.6f}",
                  flush=True)
    return 0 if gate_passed else 3


if __name__ == "__main__":
    raise SystemExit(main())
