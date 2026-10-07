"""Re-run committed (vote_t, prob_t) sweeps with and without the geometric detection scope.

Frames blast-radius measurement, Session 163 (2026-10-07). Read-only.

Each job names a candidate universe (``crops_dir/candidate_manifest.json``), its verifier
probabilities (``verify_dir/probabilities.json``), the frame it was swept on, and the
committed sweep JSON. The script imports the project's own ``sweep_f1_greedy_pv.run_sweep``
and ``sweep_f1_wbf`` loaders and runs the sweep twice in-process:

* OFF — unmodified; every row must reproduce the committed sweep (gate (i) for sweeps);
* ON — inside ``blast_lib.patched_scorers()``, which monkeypatches
  ``calculate_f1_internal`` in the sweep module's namespace so each row's detections are
  scoped geometrically before scoring.

It reports the F1@20 argmax under the K-ladder tie-break (highest F1, then lowest
``vote_t``, then lowest ``prob_t``; ``scripts/score_k_ladder_phase2_rungs.py``) for OFF and
ON, and the ON F1 at the committed (OFF) operating point.

Usage::

    PYTHONDONTWRITEBYTECODE=1 .venv/bin/python rerun_sweeps.py --repo ~/Code/map-reader-llm \
        --jobs sweep_jobs.json --out out/sweeps.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blast_lib as bl  # noqa: E402


def argmax(rows: list[dict[str, Any]], buffer_m: int = 20) -> dict[str, Any]:
    """F1 argmax at one buffer with the K-ladder tie-break."""
    sel = [r for r in rows if r.get("buffer_m", buffer_m) == buffer_m]
    return max(sel, key=lambda r: (r["f1"], -r["vote_t"], -r["prob_t"]))


def key(r: dict[str, Any]) -> tuple[Any, ...]:
    """Row identity within a sweep."""
    return (r.get("buffer_m"), r["vote_t"], round(r["prob_t"], 4))


def run_job(repo: Path, job: dict[str, Any], sweep_mod: Any, wbf_mod: Any) -> dict[str, Any]:
    """Run one sweep OFF and ON and compare with the committed rows."""
    import geopandas as gpd  # noqa: PLC0415

    crops = repo / job["crops_dir"]
    verify = repo / job["verify_dir"]
    manifest = crops / "candidate_manifest.json"
    cands = wbf_mod.load_candidates_as_gdf(manifest, verify / "probabilities.json")
    gt = wbf_mod.load_ground_truth()
    bounds = gpd.read_file(repo / job["bounds"]).to_crs("EPSG:32635")
    mf = json.loads(manifest.read_text())
    max_votes = max((c.get("properties", {}).get("vote_count", 1)
                     for c in mf.get("candidates", [])), default=5)
    votes = job.get("vote_thresholds") or list(range(1, max_votes + 1))
    buffers = job.get("buffers") or [20]
    _, diag = bl.geometric_detection_scope(cands.reset_index(drop=True), bounds)

    def sweep() -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for b in buffers:
            part = sweep_mod.run_sweep(job["name"], cands, gt, bounds, buffer_m=b,
                                       vote_thresholds=votes)
            for r in part:
                r["buffer_m"] = b
            rows.extend(part)
        return rows

    off = sweep()
    with bl.patched_scorers("geometric") as counter:
        on = sweep()
    committed = json.loads((repo / job["committed_sweep"]).read_text())
    cmap = {key(r): r for r in committed}
    n_cmp = n_ok = 0
    mismatches = []
    for r in off:
        c = cmap.get(key(r))
        if c is None:
            continue
        n_cmp += 1
        same = all(abs(r[m] - c[m]) <= 1e-4 for m in ("p", "r", "f1")) and r["n"] == c["n"]
        n_ok += same
        if not same and len(mismatches) < 5:
            mismatches.append({"key": key(r), "off": r, "committed": c})
    a_off, a_on = argmax(off), argmax(on)
    on_map = {key(r): r for r in on}
    on_at_off = on_map[key(a_off)]
    moved_rows = sum(1 for r in off if abs(on_map[key(r)]["f1"] - r["f1"]) >= 0.001)
    return {
        **job,
        "n_candidates_with_probability": len(cands),
        "universe_diag": diag,
        "n_rows": len(off), "n_rows_compared": n_cmp, "n_rows_reproduced": n_ok,
        "rows_reproduced": n_cmp > 0 and n_ok == n_cmp, "mismatch_examples": mismatches,
        "argmax_off": a_off, "argmax_on": a_on,
        "argmax_moved": (a_off["vote_t"], a_off["prob_t"]) != (a_on["vote_t"], a_on["prob_t"]),
        "on_f1_at_off_argmax": on_at_off["f1"], "on_n_at_off_argmax": on_at_off["n"],
        "n_rows_moved_ge_0.001": moved_rows,
        "patched_calls": counter["calls"], "patched_dropped": counter["dropped"],
    }


def main() -> int:
    """Run every job in the jobs file and write a JSON record."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--jobs", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.expanduser().resolve()
    bl.add_repo_to_path(repo)
    import scripts.sweep_f1_greedy_pv as sweep_mod  # noqa: PLC0415
    import scripts.sweep_f1_wbf as wbf_mod  # noqa: PLC0415

    jobs = json.loads(args.jobs.read_text())
    results = []
    for job in jobs:
        try:
            res = run_job(repo, job, sweep_mod, wbf_mod)
        except Exception as exc:  # noqa: BLE001
            res = {**job, "error": f"{type(exc).__name__}: {exc}"}
        results.append(res)
        if "error" in res:
            print(f"{job['name']}: ERROR {res['error']}", flush=True)
        else:
            print(f"{job['name']} [{Path(job['bounds']).stem}]: rows {res['n_rows_reproduced']}"
                  f"/{res['n_rows_compared']} reproduced; out-of-frame "
                  f"{res['universe_diag']['n_out_of_frame']}; argmax OFF "
                  f"({res['argmax_off']['vote_t']}, {res['argmax_off']['prob_t']}) "
                  f"F1 {res['argmax_off']['f1']:.4f} -> ON ({res['argmax_on']['vote_t']}, "
                  f"{res['argmax_on']['prob_t']}) F1 {res['argmax_on']['f1']:.4f}; ON at OFF "
                  f"point {res['on_f1_at_off_argmax']:.4f}", flush=True)
    args.out.write_text(json.dumps(results, indent=1, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
