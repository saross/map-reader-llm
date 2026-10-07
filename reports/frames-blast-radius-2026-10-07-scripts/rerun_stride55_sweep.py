"""Re-run the 55-map stride sweep (``stride55-sweep-oracle-2026-08-27``) with the geometric scope.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only.

``scripts/stride55_sweep_oracle.py`` sweeps (prob_t x min_votes) over each stride run's full
candidate universe at 50 m against the extended ground truth (student plus canonical
reviewer-promoted phantoms), with the corrected-F1 engine's ``compute_counts_at_r``, which
scopes detections by sheet name only. The two universes hold 1,018 and 2,192 candidates
outside the 55-map frame's tiles (``scan_universes.py``), almost all single-vote.

This script imports the project's own loaders (``stride55_sweep_oracle.load_candidates``,
``build_phantom_gdf``, ``build_extended_gt``) and engine (``compute_counts_at_r``), and:

* re-scores every sweep row ON (candidates geometrically scoped first; scoping is per
  candidate, so scoping the universe then thresholding equals thresholding then scoping);
* re-scores OFF a gate sample (each run's primary and oracle rows plus every 25th row) and
  checks it against the committed ``results/stride55-2026-08-27/<run>/sweep_50m.csv``;
* reports the F1 argmax OFF (committed) and ON.

A row whose subset holds no out-of-frame candidate is identical ON and OFF by construction;
it is still recomputed ON here, which doubles as a check against the committed row.

Usage::

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python rerun_stride55_sweep.py \
        --repo ~/Code/map-reader-llm --out out/stride55_sweep.json --workers 20
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blast_lib as bl  # noqa: E402

STATE: dict[str, Any] = {}


def init(repo_s: str) -> None:
    """Worker initialiser: load the extended GT, the frame and both universes once."""
    import geopandas as gpd  # noqa: PLC0415
    import pandas as pd  # noqa: PLC0415

    repo = Path(repo_s)
    bl.add_repo_to_path(repo)
    import scripts.compute_corrected_f1_multi_buffer as eng  # noqa: PLC0415
    import scripts.stride55_sweep_oracle as so  # noqa: PLC0415

    student = gpd.read_file(so.STUDENT_GT).to_crs(eng.DEFAULT_CRS)
    bounds = gpd.read_file(so.BOUNDS).to_crs(eng.DEFAULT_CRS)
    empty_y = pd.DataFrame(columns=[
        "candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"])
    review_t = pd.read_csv(so.CANONICAL_REVIEW)
    phantoms = eng.build_phantom_gdf(empty_y, review_t, so.BUFFER_R)
    ext_gt = eng.build_extended_gt(student, phantoms)
    universes = {}
    for cell, spec in so.RUNS.items():
        gdf = so.load_candidates(cell, spec, bounds).reset_index(drop=True)
        scoped, diag = bl.geometric_detection_scope(gdf, bounds)
        gdf["out_of_frame"] = ~gdf.index.isin(scoped.index)
        universes[cell] = (gdf, diag)
    STATE.update({"eng": eng, "so": so, "bounds": bounds, "ext_gt": ext_gt,
                  "universes": universes})


def score_row(cell: str, prob_t: float, k: int, mode: str) -> dict[str, Any]:
    """Corrected F1 at 50 m for one sweep row, OFF or ON."""
    eng, so = STATE["eng"], STATE["so"]
    gdf, _ = STATE["universes"][cell]
    sub = gdf[(gdf["mound_probability"] >= prob_t) & (gdf["vote_count"] >= k)]
    n_oof = int(sub["out_of_frame"].sum())
    if mode == "on":
        sub = sub[~sub["out_of_frame"]]
    tp, fp, fn, _ = eng.compute_counts_at_r(sub.drop(columns=["out_of_frame"]),
                                            STATE["ext_gt"], STATE["bounds"], so.BUFFER_R)
    p, r, f1 = eng.compute_point_estimate(tp, fp, fn)
    return {"cell": cell, "prob_t": prob_t, "min_votes": k, "mode": mode,
            "n": int(len(sub)), "n_out_of_frame_in_row": n_oof,
            "tp": tp, "fp": fp, "fn": fn, "corrected_f1": f1}


def main() -> int:
    """Run the ON sweep and the OFF gate sample, and compare argmaxes."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=20)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    init(str(repo))
    so = STATE["so"]
    committed: dict[str, list[dict[str, Any]]] = {}
    jobs: list[tuple[str, float, int, str]] = []
    for cell in so.RUNS:
        rows = list(csv.DictReader((so.OUT_BASE / cell / "sweep_50m.csv").open()))
        committed[cell] = rows
        best = max(rows, key=lambda r: float(r["corrected_f1"]))
        pt, pk = so.RUNS[cell]["primary"]
        for i, r in enumerate(rows):
            key = (cell, float(r["prob_t"]), int(r["min_votes"]))
            jobs.append((*key, "on"))
            is_gate = (i % 25 == 0 or r is best
                       or (float(r["prob_t"]) == pt and int(r["min_votes"]) == pk))
            if is_gate:
                jobs.append((*key, "off"))
    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=init,
                             initargs=(str(repo),)) as pool:
        futs = [pool.submit(score_row, *j) for j in jobs]
        for i, fut in enumerate(as_completed(futs), 1):
            results.append(fut.result())
            if i % 50 == 0:
                print(f"{i}/{len(futs)} rows", flush=True)
    out: dict[str, Any] = {"runs": {}}
    for cell, rows in committed.items():
        cmap = {(float(r["prob_t"]), int(r["min_votes"])): r for r in rows}
        off = [x for x in results if x["cell"] == cell and x["mode"] == "off"]
        on = [x for x in results if x["cell"] == cell and x["mode"] == "on"]
        gate = [abs(x["corrected_f1"] - float(cmap[(x["prob_t"], x["min_votes"])]
                                              ["corrected_f1"])) <= 1e-9 for x in off]
        best_off = max(rows, key=lambda r: float(r["corrected_f1"]))
        best_on = max(on, key=lambda x: x["corrected_f1"])
        on_map = {(x["prob_t"], x["min_votes"]): x for x in on}
        at_off = on_map[(float(best_off["prob_t"]), int(best_off["min_votes"]))]
        moved = [x for x in on if abs(x["corrected_f1"] - float(
            cmap[(x["prob_t"], x["min_votes"])]["corrected_f1"])) >= 0.001]
        out["runs"][cell] = {
            "universe_diag": STATE["universes"][cell][1],
            "n_rows": len(rows), "gate_rows": len(gate), "gate_reproduced": sum(gate),
            "committed_oracle": {k: best_off[k] for k in ("prob_t", "min_votes",
                                                           "corrected_f1")},
            "on_oracle": {k: best_on[k] for k in ("prob_t", "min_votes", "corrected_f1")},
            "on_f1_at_committed_oracle": at_off["corrected_f1"],
            "oracle_moved": (float(best_off["prob_t"]), int(best_off["min_votes"]))
            != (best_on["prob_t"], best_on["min_votes"]),
            "n_rows_with_out_of_frame": sum(1 for x in on if x["n_out_of_frame_in_row"]),
            "n_rows_moved_ge_0.001": len(moved),
            "max_row_shift": max((x["corrected_f1"] - float(
                cmap[(x["prob_t"], x["min_votes"])]["corrected_f1"]) for x in on),
                default=0.0),
        }
        print(cell, json.dumps(out["runs"][cell], default=str), flush=True)
    out["rows"] = results
    args.out.write_text(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
