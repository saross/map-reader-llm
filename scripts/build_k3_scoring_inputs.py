#!/usr/bin/env python3
"""
Build the k3 fixed-union scoring inputs for the 55-map deployment oracle.
=========================================================================

For each text run, the deployment-oracle threshold analysis compares the
carried operating point ``k4`` (consensus vote >= 4) against the looser ``k3``
(vote >= 3) in **corrected F1 @ 50 m**, under a **fixed-union** extended ground
truth: both operating points are scored against ``reviewed student GT + ALL
reviewer-confirmed phantom mounds`` (the carried-k4 review ∪ the new vote=3
shell review). k4 thus takes false negatives for the real mounds only k3 found.

This script produces the two per-run inputs the existing scorers consume:

1. ``k3_verified.geojson`` — the k3 detection set = carried-k4 verified
   detections ∪ vote=3-shell verified detections (prob >= 0.15). Kept columns:
   ``source_tile`` + geometry, with a fresh sequential ``candidate_id``.
2. ``k3-new-review.csv`` — the new vote=3-shell human review (pass-1 ∪ pass-2),
   re-indexed so candidate_ids don't collide. Passed as ``--review-today`` to
   the scorers; the carried-k4 ``human-review-multi-buffer.csv`` is
   ``--review-yesterday``. Both k4 and k3 are then scored with the *same*
   yesterday+today pair, giving the identical (fixed-union) extended GT.

Pure deterministic transform; NO API, NO compute beyond a spatial concat.

Usage::

    python scripts/build_k3_scoring_inputs.py \
        --run 55maps-text-high-generalisation \
        --k4-verified outputs/55maps-text-high-generalisation/verified/verified_detections.geojson \
        --vote3-verified results/deployment-oracle-2026-06-06/vote3-verify/55maps-text-high-generalisation/vote3_verified_p015.geojson \
        --pass1-review results/deployment-oracle-2026-06-06/k3-review/55maps-text-high-generalisation/pass1-new/human-review.csv \
        --pass2-review results/deployment-oracle-2026-06-06/k3-review/55maps-text-high-generalisation/pass2-review/human-review.csv \
        --output-dir results/deployment-oracle-2026-06-06/k3-scoring

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd
import pandas as pd


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True)
    ap.add_argument("--k4-verified", type=Path, required=True)
    ap.add_argument("--vote3-verified", type=Path, required=True)
    ap.add_argument("--pass1-review", type=Path, required=True)
    ap.add_argument("--pass2-review", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    out = args.output_dir / args.run
    out.mkdir(parents=True, exist_ok=True)

    # 1) k3 detection union = k4 verified ∪ vote=3 verified, keep source_tile.
    k4 = gpd.read_file(args.k4_verified)[["source_tile", "geometry"]].copy()
    v3 = gpd.read_file(args.vote3_verified)[["source_tile", "geometry"]].copy()
    k3 = pd.concat([k4, v3], ignore_index=True)
    k3 = gpd.GeoDataFrame(k3, geometry="geometry", crs=k4.crs)
    k3.insert(0, "candidate_id", range(len(k3)))
    k3.to_file(out / "k3_verified.geojson", driver="GeoJSON")

    # 2) combined new review = pass-1 ∪ pass-2, re-indexed candidate_ids.
    r1 = pd.read_csv(args.pass1_review)
    r2 = pd.read_csv(args.pass2_review)
    combined = pd.concat([r1, r2], ignore_index=True)
    combined["candidate_id"] = range(len(combined))
    combined.to_csv(out / "k3-new-review.csv", index=False)

    n_k4 = len(k4)
    n_v3 = len(v3)
    n_mound = int((combined["human_label"] == "mound").sum())
    print(f"{args.run}: k3_verified = {len(k3)} ({n_k4} k4 + {n_v3} vote3); "
          f"k3-new-review = {len(combined)} rows ({n_mound} mounds)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
