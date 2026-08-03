#!/usr/bin/env python3
"""
Build a canonical, adjudicated phantom-mound ground truth from all of Shawn's
per-run review passes (55-map deployment oracle).
=============================================================================

The cross-run "fixed-union" comparisons (config-axis, joint-oracle) naively
concatenated every run's reviewer-confirmed mound into the extended GT. That
double-counts a real mound detected by several runs (each run's detection is a
separate phantom point → spurious false negatives) and silently lets a `mound`
label in one run override a `not_mound` in another. This script builds the
canonical GT Shawn intended — one adjudicated point per real feature — by:

1. Pooling every review row (carried + k3-shell passes) across all runs.
2. Clustering at ``--cluster-m`` (default 20 m, the consensus dedup radius) so
   one cluster == one real feature.
3. Classifying each cluster:
   - **agreed not_mound** (no mound rows) → not a phantom.
   - **agreed mound, ring spread <= --auto-collapse-m** (default 25 m, one ring
     step) → AUTO-canonical mound at the cluster centroid, ``buffer_metres`` =
     the *min* (tightest) ring any run achieved.
   - **single-row mound** → AUTO-canonical at its own point/ring.
   - **label conflict** (mound AND not_mound rows) → RE-REVIEW.
   - **ring conflict** (agreed mound, spread > auto-collapse) → RE-REVIEW.
4. Emitting (a) ``auto-canonical-mounds.csv`` (review-CSV schema, ready for
   build_phantom_gdf) and (b) a ``re-review/`` kit (manifest + probabilities +
   conflict-info) for review_candidates.py so Shawn adjudicates the conflicts.

After Shawn reviews, merge auto-canonical + the adjudicated re-review calls →
the canonical mound set → re-score config-axis + joint-oracle against it.

Pure deterministic transform; NO API.

Usage::

    python scripts/build_canonical_gt.py \
        --output-dir results/deployment-oracle-2026-06-06/canonical-gt

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

UTM = 32635
SENTINEL_BUFFER = 200  # ">150 m visible-but-out-of-range" — never a phantom

# All of Shawn's review passes: carried (multi-buffer) + k3-shell (pass1/2).
CARRIED_RUNS = [
    "55maps-text-high-generalisation",
    "55maps-text-high-t0.3-generalisation",
    "55maps-text-min-generalisation",
    "55maps-image-generalisation",
]
K3_RUNS = [
    "55maps-text-high-generalisation",
    "55maps-text-high-t0.3-generalisation",
    "55maps-text-min-generalisation",
]
K3_SUBS = ["pass1-new", "pass2-review", "pass2-mounds-confirm"]


def gather_reviews(kit_root: Path) -> list[dict]:
    """Pool every review row across all runs and passes."""
    paths: list[tuple[str, str]] = []
    for run in CARRIED_RUNS:
        paths.append((run, f"results/{run}/human-review-multi-buffer.csv"))
    for run in K3_RUNS:
        for sub in K3_SUBS:
            p = f"{kit_root}/{run}/{sub}/human-review.csv"
            if os.path.exists(p):
                paths.append((f"{run}:{sub}", p))
    rows: list[dict] = []
    for src, p in paths:
        with open(p) as f:
            for r in csv.DictReader(f):
                try:
                    rows.append({
                        "src": src,
                        "x": float(r["x"]), "y": float(r["y"]),
                        "label": r["human_label"],
                        "buf": float(r.get("buffer_metres") or 50),
                        "map_name": r.get("map_name", ""),
                        "source_tile": r.get("source_tile", ""),
                    })
                except (KeyError, TypeError, ValueError):
                    continue
    return rows


def drop_student_layer_twins(
    rows: list[dict],
    student_gt_path: Path,
    tolerance_m: float,
) -> tuple[list[dict], list[tuple[dict, float]]]:
    """Drop mound rows that duplicate a same-map student-layer point.

    Session-126 escalation W6-E9: a rescue can enter through two
    channels — a review-CSV ``mound`` row AND a curator point later
    added to the student layer at (nearly) the same coordinates. This
    build previously pooled review rows WITHOUT consulting the student
    layer, so its 20 m union-find de-dup (phantom-vs-phantom only)
    laundered such twins into authoritative-looking canonical phantoms,
    and every consumer scoring student-layer + canonical phantoms
    together carried spurious FNs. The guard runs BEFORE clustering,
    where raw per-run rows sit 0–3.8 m from their curator twins
    (post-merge centroids drift further, which is why it cannot run
    after). Only ``mound`` rows are dropped — ``not_mound`` rows near
    a student point are conflict signal, not duplication. The 5 m
    default catches the observed cross-run duplicate spread (≤3.78 m)
    and stays well below distinct-mound spacing (touching mounds sit
    ≳15–20 m apart; student jitter is ~20–25 m).

    Args:
        rows: Pooled review rows from :func:`gather_reviews`.
        student_gt_path: The student GT GeoJSON (EPSG:32635 points).
        tolerance_m: Drop radius in metres; 0 disables the guard.

    Returns:
        ``(kept_rows, dropped)`` where ``dropped`` pairs each removed
        row with its distance to the nearest same-map student point.
    """
    if tolerance_m <= 0:
        return rows, []
    with open(student_gt_path) as f:
        gt = json.load(f)
    by_map: dict[str, list[list[float]]] = defaultdict(list)
    for feat in gt.get("features", []):
        props = feat.get("properties") or {}
        geom = feat.get("geometry") or {}
        if geom.get("type") == "Point":
            by_map[props.get("source_map", "")].append(
                list(geom["coordinates"][:2]))
    trees = {m: cKDTree(np.asarray(c)) for m, c in by_map.items() if c}
    kept: list[dict] = []
    dropped: list[tuple[dict, float]] = []
    for r in rows:
        tree = trees.get(r["map_name"])
        if tree is not None and r["label"] == "mound":
            dist, _ = tree.query([r["x"], r["y"]])
            if dist <= tolerance_m:
                dropped.append((r, float(dist)))
                continue
        kept.append(r)
    return kept, dropped


def cluster(rows: list[dict], radius: float) -> dict[int, list[dict]]:
    """Union-find clustering of review points at ``radius`` metres."""
    coords = np.array([[d["x"], d["y"]] for d in rows])
    parent = list(range(len(coords)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, j in cKDTree(coords).query_pairs(radius):
        parent[find(i)] = find(j)
    clusters: dict[int, list[dict]] = defaultdict(list)
    for i, d in enumerate(rows):
        clusters[find(i)].append(d)
    return clusters


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kit-root", type=Path,
                    default=Path("results/deployment-oracle-2026-06-06/k3-review"))
    ap.add_argument("--cluster-m", type=float, default=20.0)
    ap.add_argument("--auto-collapse-m", type=float, default=25.0,
                    help="Ring spread <= this is auto-collapsed by min-ring.")
    ap.add_argument("--review-mixed-sentinel", action="store_true",
                    help="Send clusters with BOTH a creditable mound and a 200 m "
                         "out-of-range sentinel to re-review (default: auto-resolve "
                         "to the creditable ring).")
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--student-gt", type=Path,
                    default=Path("inputs/vectors/references/"
                                 "student-mounds-55maps-reviewed.geojson"),
                    help="Student GT layer for the W6-E9 channel-twin "
                         "guard (see drop_student_layer_twins).")
    ap.add_argument("--dedup-tolerance-m", type=float, default=5.0,
                    help="Drop mound review rows within this distance of "
                         "a same-map student-GT point BEFORE clustering "
                         "(channel-duplicated rescues; 0 disables).")
    args = ap.parse_args()

    rows = gather_reviews(args.kit_root)
    rows, twin_dropped = drop_student_layer_twins(
        rows, args.student_gt, args.dedup_tolerance_m)
    for r, dist in twin_dropped:
        print(f"student-layer twin dropped: {r['src']} "
              f"({r['x']:.1f}, {r['y']:.1f}) buf {int(r['buf'])} — "
              f"{dist:.3f} m from a {r['map_name']} student point")
    clusters = cluster(rows, args.cluster_m)

    auto_mounds: list[dict] = []      # review-schema rows for build_phantom_gdf
    re_review: list[dict] = []        # conflict clusters for Shawn
    n_auto_notmound = 0

    for items in clusters.values():
        # Creditable mound rows = label 'mound' AND within the 5 tolerance rings.
        # The 200 m "visible-but-out-of-range" sentinel is excluded — exactly as
        # build_phantom_gdf drops it — so sentinel-only clusters are not phantoms.
        mound_rows = [d for d in items
                      if d["label"] == "mound" and d["buf"] != SENTINEL_BUFFER]
        has_notmound = any(d["label"] == "not_mound" for d in items)
        cx = float(np.mean([d["x"] for d in items]))
        cy = float(np.mean([d["y"] for d in items]))
        tile = next((d["source_tile"] for d in items if d["source_tile"]), "")
        mapn = next((d["map_name"] for d in items if d["map_name"]), "")

        if not mound_rows:
            # no creditable mound here (all not_mound and/or all sentinel)
            n_auto_notmound += 1
            continue

        has_sentinel_mound = any(
            d["label"] == "mound" and d["buf"] == SENTINEL_BUFFER for d in items)
        bufs = [d["buf"] for d in mound_rows]
        if has_notmound:
            kind = "label_conflict"
        elif (max(bufs) - min(bufs)) > args.auto_collapse_m:
            kind = "ring_conflict"
        elif has_sentinel_mound and args.review_mixed_sentinel:
            kind = "mixed_sentinel"
        else:
            kind = "auto"

        if kind == "auto":
            auto_mounds.append({
                "candidate_id": len(auto_mounds),
                "human_label": "mound",
                "buffer_metres": int(min(bufs)),
                "x": cx, "y": cy, "map_name": mapn,
            })
        else:
            re_review.append({
                "cluster_id": len(re_review),
                "kind": kind,
                "x": cx, "y": cy, "source_tile": tile, "map_name": mapn,
                "ring_spread": (max(bufs) - min(bufs)),
                "calls": "; ".join(f"{d['src']}={d['label']}@{int(d['buf'])}"
                                   for d in items),
            })

    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    # (a) auto-canonical mounds (review-CSV schema)
    with open(out / "auto-canonical-mounds.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["candidate_id", "human_label",
                                          "buffer_metres", "x", "y", "map_name"])
        w.writeheader()
        w.writerows(auto_mounds)

    # (b) re-review kit for review_candidates.py
    rr = out / "re-review"
    (rr / "crops").mkdir(parents=True, exist_ok=True)
    manifest = {"candidates": [
        {"candidate_id": d["cluster_id"], "centroid_x": d["x"], "centroid_y": d["y"],
         "source_tile": d["source_tile"], "cropped_from": "raster",
         # crop_file is required by review_candidates.py's manifest schema; the
         # PNG need not exist (the app re-crops live from --rasters-dir).
         "crop_file": f"crops/candidate_{d['cluster_id']:05d}.png",
         "properties": {"kind": d["kind"]}}
        for d in re_review
    ]}
    json.dump(manifest, open(rr / "crops" / "candidate_manifest.json", "w"))
    json.dump({"version": "1.0", "results": {
        f"candidate_{d['cluster_id']:05d}": {"mound_probability": 1.0}
        for d in re_review
    }}, open(rr / "probabilities.json", "w"))
    with open(rr / "conflict-info.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["cluster_id", "kind", "ring_spread",
                                          "x", "y", "source_tile", "calls"])
        w.writeheader()
        for d in re_review:
            w.writerow({k: d[k] for k in
                        ["cluster_id", "kind", "ring_spread", "x", "y",
                         "source_tile", "calls"]})

    summary = {
        "n_review_rows": len(rows),
        "n_student_layer_twins_dropped": len(twin_dropped),
        "dedup_tolerance_m": args.dedup_tolerance_m,
        "n_clusters": len(clusters),
        "n_auto_canonical_mounds": len(auto_mounds),
        "n_auto_not_mound_clusters": n_auto_notmound,
        "n_re_review": len(re_review),
        "re_review_by_kind": dict(__import__("collections").Counter(
            d["kind"] for d in re_review)),
        "cluster_m": args.cluster_m, "auto_collapse_m": args.auto_collapse_m,
    }
    json.dump(summary, open(out / "summary.json", "w"), indent=2)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
