"""Re-run the frames report's ten gold-standard sweeps with the D50 scorer.

D50/D51 impact measurement, 2026-10-08 (Session 163). Read-only.

The jobs are the blast radius's own (``frames-blast-radius-2026-10-07-scripts/
sweep_jobs.json``: the 3.7 K = 1 and K = 3 rungs, their recovery-fixed twins,
the 3.7 K = 5 control, and tier E's K = 1, 3, 5 and K = 5 recovery-fixed, on
the board and Era-2 frames). Each is swept with the project's own
``sweep_f1_greedy_pv.run_sweep`` imported from the branch worktree, so the
scorer is the NEW one with no wrapper, and compared with:

* the committed sweep rows (OFF): how many rows move, and by how much;
* the blast radius's wrapper sweep (ON, ``out/sweeps.json``): the argmax and
  the F1 at the committed argmax must agree exactly.

Usage::

    PYTHONDONTWRITEBYTECODE=1 ~/Code/map-reader-llm/.venv/bin/python rerun_sweeps_new.py \
        --code WORKTREE --data ~/Code/map-reader-llm --jobs BLAST/sweep_jobs.json \
        --blast BLAST/out/sweeps.json --out out/sweeps_new.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import meas_lib as ml  # noqa: E402


def argmax(rows: list[dict[str, Any]], buffer_m: int = 20) -> dict[str, Any]:
    """F1 argmax at one buffer with the K-ladder tie-break (low vote_t, low prob_t)."""
    sel = [r for r in rows if r.get("buffer_m", buffer_m) == buffer_m]
    return max(sel, key=lambda r: (r["f1"], -r["vote_t"], -r["prob_t"]))


def key(r: dict[str, Any]) -> tuple[Any, ...]:
    """Row identity within a sweep."""
    return (r.get("buffer_m"), r["vote_t"], round(r["prob_t"], 4))


def main() -> int:
    """Sweep every job with the NEW scorer and compare."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--code", type=Path, required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--jobs", type=Path, required=True)
    ap.add_argument("--blast", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    ml.setup(args.code)
    import geopandas as gpd  # noqa: PLC0415

    import scripts.sweep_f1_greedy_pv as sweep_mod  # noqa: PLC0415
    import scripts.sweep_f1_wbf as wbf_mod  # noqa: PLC0415

    data = args.data.expanduser().resolve()
    blast = {(j["name"], j["bounds"]): j for j in json.loads(args.blast.read_text())}
    results = []
    for job in json.loads(args.jobs.read_text()):
        crops, verify = data / job["crops_dir"], data / job["verify_dir"]
        cands = wbf_mod.load_candidates_as_gdf(crops / "candidate_manifest.json",
                                               verify / "probabilities.json")
        gt = wbf_mod.load_ground_truth()
        bounds = gpd.read_file(data / job["bounds"]).to_crs("EPSG:32635")
        manifest = json.loads((crops / "candidate_manifest.json").read_text())
        max_votes = max((c.get("properties", {}).get("vote_count", 1)
                         for c in manifest.get("candidates", [])), default=5)
        votes = list(range(1, max_votes + 1))
        rows: list[dict[str, Any]] = []
        for b in job.get("buffers") or [20]:
            part = sweep_mod.run_sweep(job["name"], cands, gt, bounds, buffer_m=b,
                                       vote_thresholds=votes)
            for r in part:
                r["buffer_m"] = b
            rows.extend(part)
        committed = json.loads((data / job["committed_sweep"]).read_text())
        cmap = {key(r): r for r in committed}
        new_map = {key(r): r for r in rows}
        moved = [r for r in rows if key(r) in cmap
                 and abs(r["f1"] - cmap[key(r)]["f1"]) >= 0.001]
        a_off = argmax(committed)
        a_new = argmax(rows)
        b = blast.get((job["name"], job["bounds"]), {})
        a_on = b.get("argmax_on") or {}
        rec = {
            "name": job["name"], "bounds": job["bounds"], "anchor": job.get("anchor"),
            "n_candidates": len(cands),
            "universe_scope": ml.LIB.scope_detections_to_frame(cands, bounds).diagnostics,
            "n_rows": len(rows), "n_rows_moved_ge_0.001_vs_committed": len(moved),
            "argmax_committed": {k: a_off[k] for k in ("vote_t", "prob_t", "f1", "n")},
            "argmax_new": {k: a_new[k] for k in ("vote_t", "prob_t", "f1", "n")},
            "argmax_moved_vs_committed": (a_off["vote_t"], a_off["prob_t"])
            != (a_new["vote_t"], a_new["prob_t"]),
            "new_f1_at_committed_argmax": new_map[key(a_off)]["f1"],
            "blast_on_argmax": {k: a_on.get(k) for k in ("vote_t", "prob_t", "f1")},
            "blast_on_f1_at_committed_argmax": b.get("on_f1_at_off_argmax"),
            "blast_n_rows_moved": b.get("n_rows_moved_ge_0.001"),
            "agrees_with_blast_on": (
                a_on.get("vote_t") == a_new["vote_t"]
                and a_on.get("prob_t") == a_new["prob_t"]
                and a_on.get("f1") is not None and abs(a_on["f1"] - a_new["f1"]) < 1e-9
                and b.get("on_f1_at_off_argmax") is not None
                and abs(b["on_f1_at_off_argmax"] - new_map[key(a_off)]["f1"]) < 1e-9
                and b.get("n_rows_moved_ge_0.001") == len(moved)
            ),
        }
        results.append(rec)
        print(f"{job['name']} [{Path(job['bounds']).stem}]: argmax committed "
              f"({a_off['vote_t']}, {a_off['prob_t']}) {a_off['f1']:.4f} -> NEW "
              f"({a_new['vote_t']}, {a_new['prob_t']}) {a_new['f1']:.4f}; rows moved "
              f"{len(moved)}/{len(rows)}; agrees with blast ON: {rec['agrees_with_blast_on']}",
              flush=True)
    args.out.write_text(json.dumps(results, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
