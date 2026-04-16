#!/usr/bin/env python3
"""
F1 sweep over (greedy consensus_t, verifier prob_t) for a greedy-clustered
proposer candidate set that has been verified end-to-end.

Companion to ``sweep_f1_wbf.py`` — same output JSON schema so the two
pipelines can be compared directly. The only differences:

- Vote thresholds are 1..5 (K=5 greedy consensus) instead of the WBF
  2..10 range.
- Probability thresholds span 0.00 → 0.95 in fine steps so the sweep
  output is comparable to ``evaluate_pv_results.py sweep``.

Inputs (one ``--crops-dir`` / ``--verified-dir`` pair, matching
``run_pv.py`` layout):

    <crops-dir>/candidate_manifest.json   — must have vote_count in
                                             per-candidate properties
                                             (written by run_pv.py extract
                                             from consensus_t1 GeoJSON)
    <verified-dir>/probabilities.json      — mound_probability per candidate

Ground truth (defaults):

    inputs/vectors/references/mounds-reference.geojson       — 569 GT mounds
    inputs/vectors/bounds/384/h10_test_bounds.geojson        — 327 test tiles

Usage::

    python scripts/sweep_f1_greedy_pv.py \\
        --config scale-4 \\
        --crops-dir outputs/h8-v2/scale-4/crops \\
        --verified-dir outputs/h8-v2/scale-4/verified \\
        --output results/h8-v2/verifier-sweep/scale-4/sweep_2d_greedy_pv.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from scripts.sweep_f1_wbf import (
    load_candidates_as_gdf,
    load_ground_truth,
)
import geopandas as gpd
from scripts.lib_advanced_metrics import calculate_f1_internal

DEFAULT_BOUNDS = (
    BASE_DIR / "inputs" / "vectors" / "bounds" / "384" / "h10_test_bounds.geojson"
)

#: Default K=5 greedy consensus → valid vote thresholds are 1..5.
#: Override with --vote-thresholds or auto-detect from manifest total_passes.
DEFAULT_VOTE_THRESHOLDS = [1, 2, 3, 4, 5]

#: Fine-grained probability grid that matches the step=0.05 convention
#: used by ``evaluate_pv_results.py sweep``. Extends to 0.95 so the
#: high-precision tail of the sweep is visible.
PROB_THRESHOLDS = [
    0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40,
    0.45, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95,
]


def run_sweep(
    config_name: str,
    cands: gpd.GeoDataFrame,
    gt: gpd.GeoDataFrame,
    bounds: gpd.GeoDataFrame,
    buffer_m: int = 20,
    vote_thresholds: list[int] | None = None,
) -> list[dict]:
    if vote_thresholds is None:
        vote_thresholds = DEFAULT_VOTE_THRESHOLDS
    rows: list[dict] = []
    for vt in vote_thresholds:
        for pt in PROB_THRESHOLDS:
            sub = cands[
                (cands["vote_count"] >= vt)
                & (cands["mound_probability"] >= pt)
            ]
            n = len(sub)
            if n == 0:
                rows.append({
                    "config": config_name,
                    "vote_t": vt, "prob_t": pt,
                    "n": 0, "p": 0.0, "r": 0.0, "f1": 0.0,
                })
                continue
            p, r, f1 = calculate_f1_internal(
                sub, gt, bounds, buffer_metres=buffer_m,
            )
            rows.append({
                "config": config_name,
                "vote_t": vt, "prob_t": pt,
                "n": n,
                "p": round(p, 4),
                "r": round(r, 4),
                "f1": round(f1, 4),
            })
    return rows


def print_top(rows: list[dict], k: int = 10) -> None:
    best = max(rows, key=lambda r: r["f1"])
    print(
        f"\nOptimal: vote_t={best['vote_t']}  prob_t={best['prob_t']:.2f}  "
        f"n={best['n']}  P={best['p']:.4f}  R={best['r']:.4f}  "
        f"F1={best['f1']:.4f}"
    )
    top = sorted(rows, key=lambda r: -r["f1"])[:k]
    print(f"\nTop-{k} rows by F1:")
    print(f"  {'vote_t':<8}{'prob_t':<8}{'n':<8}{'P':<8}{'R':<8}{'F1':<8}")
    for r in top:
        print(
            f"  {r['vote_t']:<8}{r['prob_t']:<8.2f}{r['n']:<8}"
            f"{r['p']:<8.4f}{r['r']:<8.4f}{r['f1']:<8.4f}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="Config label")
    parser.add_argument("--crops-dir", type=Path, required=True)
    parser.add_argument("--verified-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bounds", type=Path, default=DEFAULT_BOUNDS)
    parser.add_argument("--buffer-m", type=int, nargs="+", default=[20],
                        help="Buffer distance(s) in metres (default: 20)")
    parser.add_argument("--vote-thresholds", type=int, nargs="+", default=None,
                        help="Vote thresholds to sweep (default: auto-detect from manifest)")
    args = parser.parse_args()

    manifest = args.crops_dir / "candidate_manifest.json"
    probs = args.verified_dir / "probabilities.json"
    if not manifest.exists() or not probs.exists():
        print(f"Error: missing inputs ({manifest} or {probs})", file=sys.stderr)
        return 1

    print(f"Loading candidates + probabilities from {manifest.parent}...")
    cands = load_candidates_as_gdf(manifest, probs)
    print(f"  {len(cands)} candidates")

    print(f"Loading GT + bounds ({args.bounds.name})...")
    gt = load_ground_truth()
    bounds = gpd.read_file(args.bounds).to_crs("EPSG:32635")
    print(f"  {len(gt)} GT mounds, {len(bounds)} bounds tiles")

    # Auto-detect vote thresholds from manifest if not specified
    vote_thresholds = args.vote_thresholds
    if vote_thresholds is None:
        with open(manifest, encoding="utf-8") as f:
            mf = json.load(f)
        # Find max vote_count across all candidates
        max_votes = max(
            (c.get("properties", {}).get("vote_count", 1)
             for c in mf.get("candidates", [])),
            default=5,
        )
        vote_thresholds = list(range(1, max_votes + 1))
        print(f"  Auto-detected vote thresholds: 1..{max_votes}")

    buffers = args.buffer_m if isinstance(args.buffer_m, list) else [args.buffer_m]
    all_rows: list[dict] = []

    for buffer_m in buffers:
        print(f"\nRunning 2D sweep: {len(vote_thresholds)} vote × {len(PROB_THRESHOLDS)} prob @ {buffer_m}m")
        rows = run_sweep(
            args.config, cands, gt, bounds,
            buffer_m=buffer_m, vote_thresholds=vote_thresholds,
        )
        # Tag rows with buffer
        for r in rows:
            r["buffer_m"] = buffer_m
        all_rows.extend(rows)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(all_rows, f, indent=2)
    print(f"\nWrote {len(all_rows)} rows to {args.output}")

    # Print top results per buffer
    for buffer_m in buffers:
        buf_rows = [r for r in all_rows if r.get("buffer_m") == buffer_m]
        if buf_rows:
            print(f"\n--- {buffer_m}m buffer ---")
            print_top(buf_rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
