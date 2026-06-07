#!/usr/bin/env python3
"""
Build a review kit of cross-config-corroborated vote=2 candidates for GT
enrichment (55-map deployment oracle).
=========================================================================

To push the 55-map ground truth toward GS completeness, we look one consensus
notch below the reviewed floor (vote>=3) at the **vote=2 shell** — real mounds
that even 3-of-5 missed. The full new vote=2 set is ~19k (mostly single-config
2-pass noise), so we keep only features that **>= --min-configs of the four
proposer configs independently surfaced at vote=2** (cross-config agreement =
a strong real-mound signal, no verifier needed), AND that are genuinely new:
not within ``--rev-exclude-m`` of any already-reviewed detection and not within
``--gt-exclude-m`` of the student GT (so: no re-checks, no conflicts).

Emits a review_candidates.py kit (manifest + probabilities + info CSV) — one
centroid per corroborated feature — for Shawn to label mound/not_mound. The
confirmed mounds are then added to the canonical GT and the cross-run analyses
re-scored against the enriched (more GS-like) reference.

Pure deterministic transform; NO API.

Usage::

    python scripts/build_vote2_enrichment_kit.py --min-configs 3 \
        --output-dir results/deployment-oracle-2026-06-06/vote2-enrichment

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import geopandas as gpd
import numpy as np
from scipy.spatial import cKDTree

UTM = 32635
SWEEP = "results/deployment-oracle-2026-06-06/consensus-sweep"
CONFIGS = {
    "text-high": "55maps-text-high-generalisation",
    "t0.3": "55maps-text-high-t0.3-generalisation",
    "text-min": "55maps-text-min-generalisation",
    "image": "55maps-image-generalisation",
}
GT = "inputs/vectors/references/student-mounds-55maps-reviewed.geojson"
K3_RUNS = ["55maps-text-high-generalisation",
           "55maps-text-high-t0.3-generalisation",
           "55maps-text-min-generalisation"]
K3_SUBS = ["pass1-new", "pass2-review", "pass2-mounds-confirm"]


def _first_tile(st: object) -> str:
    """Coerce a consensus feature's ``source_tiles`` (str / list / ndarray /
    None) to a single tile-name string; '' on anything unparseable."""
    if st is None:
        return ""
    if isinstance(st, str):
        return st.strip("[]'\" ").split(",")[0].strip("'\" ")
    try:
        return str(st[0]) if len(st) else ""
    except (TypeError, IndexError, KeyError):
        return ""


def reviewed_points(kit_root: Path) -> np.ndarray:
    """Every already-reviewed detection (x, y) in UTM 35N."""
    pts: list[tuple[float, float]] = []
    paths = [f"results/{run}/human-review-multi-buffer.csv" for run in CONFIGS.values()]
    for run in K3_RUNS:
        for sub in K3_SUBS:
            p = f"{kit_root}/{run}/{sub}/human-review.csv"
            if os.path.exists(p):
                paths.append(p)
    for p in paths:
        with open(p) as f:
            for r in csv.DictReader(f):
                try:
                    pts.append((float(r["x"]), float(r["y"])))
                except (KeyError, TypeError, ValueError):
                    continue
    return np.array(pts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--min-configs", type=int, default=3,
                    help="Keep features found by >= this many configs (default 3).")
    ap.add_argument("--cluster-m", type=float, default=20.0)
    ap.add_argument("--rev-exclude-m", type=float, default=20.0)
    ap.add_argument("--gt-exclude-m", type=float, default=50.0)
    ap.add_argument("--kit-root", type=Path,
                    default=Path("results/deployment-oracle-2026-06-06/k3-review"))
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()

    # vote=2 shell (exactly 2 votes) pooled across the four configs.
    cfgs: list[str] = []
    coords: list[tuple[float, float]] = []
    tiles: list[str] = []
    for name, run in CONFIGS.items():
        d = gpd.read_file(f"{SWEEP}/{run}/consensus_t2.geojson").to_crs(UTM)
        for _, f in d.iterrows():
            if (f.get("vote_count") or 0) != 2:
                continue
            c = f.geometry.centroid
            cfgs.append(name)
            coords.append((c.x, c.y))
            tiles.append(_first_tile(f.get("source_tiles")))
    coords_a = np.array(coords)

    # genuinely-new filter: not near a reviewed detection, not near student GT
    rev_tree = cKDTree(reviewed_points(args.kit_root))
    gt_pts = np.array([(g.x, g.y) for g in gpd.read_file(GT).to_crs(UTM).geometry])
    gt_tree = cKDTree(gt_pts)
    near_rev = rev_tree.query(coords_a, distance_upper_bound=args.rev_exclude_m)[0] < args.rev_exclude_m
    near_gt = gt_tree.query(coords_a, distance_upper_bound=args.gt_exclude_m)[0] < args.gt_exclude_m
    keep = ~near_rev & ~near_gt
    idx = np.where(keep)[0]

    # cluster the new detections; keep clusters with >= min-configs distinct configs
    sub = coords_a[idx]
    parent = list(range(len(sub)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, j in cKDTree(sub).query_pairs(args.cluster_m):
        parent[find(i)] = find(j)
    members: dict[int, list[int]] = defaultdict(list)
    for k in range(len(sub)):
        members[find(k)].append(k)

    kept = []
    for root, ks in members.items():
        cfg_set = {cfgs[idx[k]] for k in ks}
        if len(cfg_set) >= args.min_configs:
            pts = sub[ks]
            kept.append({
                "x": float(pts[:, 0].mean()), "y": float(pts[:, 1].mean()),
                "n_configs": len(cfg_set), "configs": ",".join(sorted(cfg_set)),
                "source_tile": next((tiles[idx[k]] for k in ks if tiles[idx[k]]), ""),
            })
    kept.sort(key=lambda d: -d["n_configs"])

    out = args.output_dir
    (out / "crops").mkdir(parents=True, exist_ok=True)
    manifest = {"candidates": [
        {"candidate_id": i, "centroid_x": d["x"], "centroid_y": d["y"],
         "source_tile": d["source_tile"], "cropped_from": "raster",
         "crop_file": f"crops/candidate_{i:05d}.png",
         "properties": {"n_configs": d["n_configs"], "configs": d["configs"]}}
        for i, d in enumerate(kept)
    ]}
    json.dump(manifest, open(out / "crops" / "candidate_manifest.json", "w"))
    json.dump({"version": "1.0", "results": {
        f"candidate_{i:05d}": {"mound_probability": 1.0} for i in range(len(kept))
    }}, open(out / "probabilities.json", "w"))
    with open(out / "candidate-info.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate_id", "n_configs", "configs", "x", "y", "source_tile"])
        for i, d in enumerate(kept):
            w.writerow([i, d["n_configs"], d["configs"], round(d["x"], 1),
                        round(d["y"], 1), d["source_tile"]])

    summary = {
        "min_configs": args.min_configs,
        "n_vote2_new_features_kept": len(kept),
        "by_n_configs": dict(sorted(Counter(d["n_configs"] for d in kept).items())),
    }
    json.dump(summary, open(out / "summary.json", "w"), indent=2)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
