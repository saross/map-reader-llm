"""Re-run the 55-map stride sweeps with the D50 corrected-F1 engine.

D50/D51 impact measurement, 2026-10-08 (Session 163). Read-only.

``scripts/stride55_sweep_oracle.py`` sweeps (prob_t x min_votes) over each
stride run's full candidate universe at 50 m against the extended ground truth,
through the corrected-F1 engine's ``compute_counts_at_r``. Under D50 that
function routes through the library's per-sheet scope, so out-of-frame
candidates (all of them inside a NEIGHBOURING sheet's tiles here) are dropped
by the engine itself. This script imports the worktree's loaders and engine
(no wrapper), scores every row, and compares each with the blast radius's ON
row (``out/stride55_sweep.json``) and the committed row
(``results/stride55-2026-08-27/<run>/sweep_50m.csv``).

Usage::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python rerun_stride55_new.py \
        --code WORKTREE --blast BLAST/out/stride55_sweep.json \
        --out out/stride55_new.json --workers 16
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
import meas_lib as ml  # noqa: E402

STATE: dict[str, Any] = {}


def init(code: str) -> None:
    """Worker initialiser: the extended reference, the frame and both universes."""
    import geopandas as gpd  # noqa: PLC0415
    import pandas as pd  # noqa: PLC0415

    ml.setup(Path(code))
    import scripts.compute_corrected_f1_multi_buffer as eng  # noqa: PLC0415
    import scripts.stride55_sweep_oracle as so  # noqa: PLC0415

    student = gpd.read_file(so.STUDENT_GT).to_crs(eng.DEFAULT_CRS)
    bounds = gpd.read_file(so.BOUNDS).to_crs(eng.DEFAULT_CRS)
    empty_y = pd.DataFrame(columns=[
        "candidate_id", "human_label", "buffer_metres", "x", "y", "map_name"])
    review_t = pd.read_csv(so.CANONICAL_REVIEW)
    phantoms = eng.build_phantom_gdf(empty_y, review_t, so.BUFFER_R)
    ext_gt = eng.build_extended_gt(student, phantoms)
    universes = {cell: so.load_candidates(cell, spec, bounds).reset_index(drop=True)
                 for cell, spec in so.RUNS.items()}
    STATE.update({"eng": eng, "so": so, "bounds": bounds, "ext_gt": ext_gt,
                  "universes": universes})


def score_row(cell: str, prob_t: float, k: int) -> dict[str, Any]:
    """Corrected F1 at 50 m for one sweep row with the NEW engine."""
    eng, so = STATE["eng"], STATE["so"]
    gdf = STATE["universes"][cell]
    sub = gdf[(gdf["mound_probability"] >= prob_t) & (gdf["vote_count"] >= k)]
    tp, fp, fn, _ = eng.compute_counts_at_r(sub, STATE["ext_gt"], STATE["bounds"],
                                            so.BUFFER_R)
    p, r, f1 = eng.compute_point_estimate(tp, fp, fn)
    return {"cell": cell, "prob_t": prob_t, "min_votes": k, "n": int(len(sub)),
            "tp": tp, "fp": fp, "fn": fn, "corrected_f1": f1}


def main() -> int:
    """Score every row NEW and compare with blast ON and committed."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--blast", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args()
    code = str(args.code.expanduser().resolve())
    init(code)
    so = STATE["so"]
    blast = json.loads(args.blast.read_text())
    on_rows = {(x["cell"], x["prob_t"], x["min_votes"]): x
               for x in blast["rows"] if x["mode"] == "on"}
    committed = {cell: list(csv.DictReader((so.OUT_BASE / cell / "sweep_50m.csv").open()))
                 for cell in so.RUNS}
    jobs = [(cell, float(r["prob_t"]), int(r["min_votes"]))
            for cell, rows in committed.items() for r in rows]
    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=args.workers, initializer=init,
                             initargs=(code,)) as pool:
        futs = [pool.submit(score_row, *j) for j in jobs]
        for fut in as_completed(futs):
            results.append(fut.result())
    out: dict[str, Any] = {"runs": {}}
    for cell, rows in committed.items():
        cmap = {(float(r["prob_t"]), int(r["min_votes"])): r for r in rows}
        new = [x for x in results if x["cell"] == cell]
        same_as_on = sum(
            1 for x in new
            if abs(x["corrected_f1"]
                   - on_rows[(cell, x["prob_t"], x["min_votes"])]["corrected_f1"]) <= 1e-12)
        best_off = max(rows, key=lambda r: float(r["corrected_f1"]))
        best_new = max(new, key=lambda x: x["corrected_f1"])
        new_map = {(x["prob_t"], x["min_votes"]): x for x in new}
        at_off = new_map[(float(best_off["prob_t"]), int(best_off["min_votes"]))]
        moved = [x for x in new if abs(x["corrected_f1"] - float(
            cmap[(x["prob_t"], x["min_votes"])]["corrected_f1"])) >= 0.001]
        out["runs"][cell] = {
            "n_rows": len(rows), "n_rows_equal_to_blast_on": same_as_on,
            "committed_oracle": {k: best_off[k] for k in ("prob_t", "min_votes",
                                                           "corrected_f1")},
            "new_oracle": {k: best_new[k] for k in ("prob_t", "min_votes", "corrected_f1")},
            "new_f1_at_committed_oracle": at_off["corrected_f1"],
            "oracle_moved": (float(best_off["prob_t"]), int(best_off["min_votes"]))
            != (best_new["prob_t"], best_new["min_votes"]),
            "n_rows_moved_ge_0.001": len(moved),
        }
        print(cell, json.dumps(out["runs"][cell], default=str), flush=True)
    out["rows"] = results
    args.out.write_text(json.dumps(out, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
