#!/usr/bin/env python3
"""
Build the k3-shell manual-review kit for the 55-map deployment-oracle analysis.
=============================================================================

Context
-------
The 55-map deployment-oracle analysis (Session 104) curtain-pulls the
post-verifier vote-threshold oracle. For the text runs the carried operating
point is vote >= 4 (``k4``); resolving the looser ``k3`` operating point added
the *vote = 3 shell* candidates, which were verified afresh (``run_pv.py
verify`` at prob_t = 0.15). To score ``k3`` in the project's **corrected-F1 @
50 m** frame, the new VLM-only detections (those not matching the reviewed
student ground truth at 50 m) need human review to mint reviewer-promoted
phantom mounds — exactly as the original per-run reviews did. They cannot be
carried over: the k3 clusters are disjoint from the carried k4 set.

Per the operator's two-pass plan, this script splits the VLM-only k3 verified
candidates into:

* **NEW** — not within ``--coincide-m`` of any previously-reviewed candidate
  (across all runs' ``human-review*.csv``). These need fresh judgement and form
  *pass 1* (a filtered ``review_candidates.py`` kit: manifest + probabilities
  subset, rendered live from the local rasters).
* **AUTO-FILL** — within ``--coincide-m`` of a prior-reviewed candidate. Their
  label is inherited from the nearest prior review and written to a confirm CSV
  for *pass 2* (a fast confirmation pass).

Outputs (under ``--output-dir/<run>/``)
---------------------------------------
* ``pass1-new/crops/candidate_manifest.json`` — manifest of NEW candidates only
* ``pass1-new/probabilities.json``            — probabilities of NEW candidates
* ``pass2-autofill.csv``                      — AUTO-FILL inherited labels
* ``kit_summary.json``                        — counts and provenance

This is a pure deterministic transform: NO API calls, NO new crops (the review
app re-renders context crops live from the rasters via ``--rasters-dir``).

Usage
-----
    python scripts/build_k3_review_kit.py \
        --run 55maps-text-high-generalisation \
        --vote3-dir results/deployment-oracle-2026-06-06/vote3-verify \
        --ground-truth inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
        --prior-reviews "results/55maps-*generalisation/human-review*.csv" \
        --prob-threshold 0.15 --match-m 50 --coincide-m 50 \
        --output-dir results/deployment-oracle-2026-06-06/k3-review

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import csv
import glob
import json
from pathlib import Path

import geopandas as gpd
from shapely.geometry import Point

UTM = 32635  # EPSG:32635 (UTM Zone 35N) — the study's projected CRS


def load_prior_reviews(patterns: list[str]) -> gpd.GeoDataFrame:
    """Collect every previously-reviewed candidate (any run) as points.

    Each ``human-review*.csv`` row carries projected ``x``/``y`` (UTM 35N),
    a ``human_label`` and a ``symbol_type``. Returns a GeoDataFrame in
    EPSG:32635 with ``human_label`` and ``symbol_type`` columns.
    """
    rows: list[dict] = []
    geoms: list[Point] = []
    seen_files: list[str] = []
    for pattern in patterns:
        for fp in glob.glob(pattern):
            seen_files.append(fp)
            for r in csv.DictReader(open(fp)):
                try:
                    x, y = float(r["x"]), float(r["y"])
                except (KeyError, TypeError, ValueError):
                    continue
                rows.append({
                    "human_label": r.get("human_label", ""),
                    "symbol_type": r.get("symbol_type", ""),
                })
                geoms.append(Point(x, y))
    gdf = gpd.GeoDataFrame(rows, geometry=geoms, crs=UTM)
    return gdf, sorted(set(seen_files))


def candidate_points(manifest_candidates: list[dict]) -> gpd.GeoDataFrame:
    """Build a GeoDataFrame of candidate centroids in EPSG:32635."""
    recs, geoms = [], []
    for c in manifest_candidates:
        recs.append({"candidate_id": int(c["candidate_id"])})
        geoms.append(Point(float(c["centroid_x"]), float(c["centroid_y"])))
    return gpd.GeoDataFrame(recs, geometry=geoms, crs=UTM)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run", required=True, help="Run id (directory name).")
    ap.add_argument("--vote3-dir", type=Path, required=True,
                    help="Base dir holding <run>/{crops,verified} from the "
                         "vote=3 verify pass.")
    ap.add_argument("--ground-truth", type=Path, required=True)
    ap.add_argument("--prior-reviews", nargs="+", required=True,
                    help="Glob pattern(s) for prior human-review CSVs.")
    ap.add_argument("--prob-threshold", type=float, default=0.15)
    ap.add_argument("--match-m", type=float, default=50.0,
                    help="GT-match tolerance defining VLM-only (default 50 m).")
    ap.add_argument("--coincide-m", type=float, default=50.0,
                    help="Distance for inheriting a prior review (default 50).")
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    run_dir = args.vote3_dir / args.run
    manifest = json.load(open(run_dir / "crops" / "candidate_manifest.json"))
    cands = manifest["candidates"]
    probs = json.load(open(run_dir / "verified" / "probabilities.json"))
    results = probs["results"]

    def prob_of(cid: int) -> float:
        entry = results.get(f"candidate_{cid:05d}")
        return float(entry["mound_probability"]) if entry else 0.0

    # Verifier-passed candidates only (prob >= threshold).
    passed = [c for c in cands if prob_of(int(c["candidate_id"])) >= args.prob_threshold]

    # VLM-only = not matching the reviewed GT within match-m.
    gt = gpd.read_file(args.ground_truth).to_crs(UTM)
    gt_buf = gt.buffer(args.match_m).union_all()
    cpts = candidate_points(passed)
    cpts["vlm_only"] = ~cpts.within(gt_buf)
    vlm_only_ids = set(cpts.loc[cpts["vlm_only"], "candidate_id"])
    vlm_only = cpts[cpts["vlm_only"]].copy()

    # Inherit nearest prior-review label within coincide-m -> AUTO-FILL.
    prior, prior_files = load_prior_reviews(args.prior_reviews)
    joined = gpd.sjoin_nearest(
        vlm_only, prior[["human_label", "symbol_type", "geometry"]],
        how="left", max_distance=args.coincide_m, distance_col="dist_m",
    )
    # sjoin_nearest can emit >1 row per candidate on ties; keep the closest.
    joined = joined.sort_values("dist_m").drop_duplicates("candidate_id")
    autofill = joined[joined["human_label"].notna()].copy()
    autofill_ids = set(autofill["candidate_id"])
    new_ids = vlm_only_ids - autofill_ids

    out = args.output_dir / args.run
    (out / "pass1-new" / "crops").mkdir(parents=True, exist_ok=True)

    # --- pass 1: NEW candidates -> filtered manifest + probabilities ---
    new_cands = [c for c in passed if int(c["candidate_id"]) in new_ids]
    new_manifest = dict(manifest)
    new_manifest["candidates"] = new_cands
    json.dump(new_manifest,
              open(out / "pass1-new" / "crops" / "candidate_manifest.json", "w"))
    new_results = {f"candidate_{int(c['candidate_id']):05d}":
                   results[f"candidate_{int(c['candidate_id']):05d}"]
                   for c in new_cands}
    new_probs = dict(probs)
    new_probs["results"] = new_results
    new_probs["total_results"] = len(new_results)
    json.dump(new_probs, open(out / "pass1-new" / "probabilities.json", "w"))

    # --- pass 2: AUTO-FILL inherited labels ---
    by_id = {int(c["candidate_id"]): c for c in passed}
    with open(out / "pass2-autofill.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate_id", "inherited_human_label", "inherited_symbol_type",
                    "dist_m", "verifier_probability", "source_tile",
                    "centroid_x", "centroid_y"])
        for _, r in autofill.iterrows():
            cid = int(r["candidate_id"])
            c = by_id[cid]
            st = c.get("source_tile") or (c.get("properties", {}) or {}).get("source_tile", "")
            w.writerow([cid, r["human_label"], r["symbol_type"],
                        round(float(r["dist_m"]), 2), round(prob_of(cid), 4),
                        st, c["centroid_x"], c["centroid_y"]])

    summary = {
        "run": args.run,
        "prob_threshold": args.prob_threshold,
        "match_m": args.match_m,
        "coincide_m": args.coincide_m,
        "n_vote3_candidates": len(cands),
        "n_verifier_passed": len(passed),
        "n_vlm_only": len(vlm_only_ids),
        "n_pass1_new": len(new_ids),
        "n_pass2_autofill": len(autofill_ids),
        "autofill_label_breakdown":
            autofill["human_label"].value_counts().to_dict(),
        "prior_review_files": prior_files,
        "ground_truth": str(args.ground_truth),
    }
    json.dump(summary, open(out / "kit_summary.json", "w"), indent=2)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
