#!/usr/bin/env python3
"""
Independent verification of the H13 overlap-arm headline numbers.

Re-derives every load-bearing figure in
``results/h13-overlap-2026-08-18/`` from the committed raw artefacts
along a deliberately separate code path. Nothing in this file imports
``lib_advanced_metrics``, ``merge_passes``, ``evaluate_detections`` or
``h13_overlap_analysis``: the deduplication, the footprint intersection,
the ground-truth scoping and the Hungarian matching are all
reimplemented here from primitives, so a shared bug cannot cancel itself
out across the proposer and the check.

Checks performed (each PASS/FAIL against a tolerance):

1. **Raw and deduplicated detection counts** per pass, including arm B
   run_1's additive recovery merge.
2. **Common footprint** area and the ground-truth count inside it.
3. **Per-arm micro precision, recall and F1** at 20 m on the common
   scope, against ``h13_overlap_analysis.json``.
4. **Audited cost** totals against the per-pass metadata.
5. **Edge-analysis low-margin subgroup** recall for all three arms.

Usage::

    python scripts/verify_h13_overlap.py

Exit status is 0 when every check passes and 1 otherwise, so the script
can gate a commit.

Created: 2026-08-18 (Session 136)
Author: Shawn Ross, Claude Code
Licence: Apache 2.0
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment
from shapely.geometry import Point, shape
from shapely.ops import unary_union

PROJECT_ROOT = Path(__file__).parent.parent
ANALYSIS = PROJECT_ROOT / "results/h13-overlap-2026-08-18/h13_overlap_analysis.json"
SCORING = PROJECT_ROOT / "outputs/h13/scoring"
GT_PATH = PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"

DEDUP_M = 20.0
BUFFER_M = 20.0
RUNS = ("run_1", "run_2", "run_3")

H13 = "detections-detect_brief-text-3-flash-2026-08-17.geojson"
PASS_FILES: dict[str, dict[str, list[Path]]] = {
    "armA": {
        f"run_{i}": [PROJECT_ROOT / f"outputs/retest/phase2a/brief-text/run_{i}/"
                     f"detections_brief-text_run0{i}.geojson"]
        for i in (1, 2, 3)
    },
    "armB": {
        "run_1": [PROJECT_ROOT / f"outputs/h13/armB/run_1/{H13}",
                  PROJECT_ROOT / f"outputs/h13/armB/run_1_recovery/{H13}"],
        "run_2": [PROJECT_ROOT / f"outputs/h13/armB/run_2/{H13}"],
        "run_3": [PROJECT_ROOT / f"outputs/h13/armB/run_3/{H13}"],
    },
    "armC": {
        f"run_{i}": [PROJECT_ROOT / f"outputs/h13/armC/run_{i}/{H13}"]
        for i in (1, 2, 3)
    },
}

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str) -> None:
    """Record one check outcome.

    Args:
        name: Short check label.
        ok: Whether the check passed.
        detail: Human-readable comparison detail.
    """
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def close(a: float, b: float, tol: float = 1e-4) -> bool:
    """Return whether two floats agree within ``tol``.

    Args:
        a: First value. b: Second value. tol: Absolute tolerance.

    Returns:
        True when ``|a - b| <= tol``.
    """
    return math.isclose(a, b, abs_tol=tol)


def centroid_xy(geom: dict) -> tuple[float, float]:
    """Return a geometry's centroid as an (x, y) tuple.

    Implemented via shapely directly rather than through the project's
    geometry helpers, keeping this verifier off the shared code path.

    Args:
        geom: GeoJSON geometry mapping.

    Returns:
        Centroid coordinates in the layer CRS.
    """
    c = shape(geom).centroid
    return (c.x, c.y)


def greedy_dedup(points: list[tuple[float, float]], radius: float) -> list[tuple[float, float]]:
    """Greedily cluster points within ``radius`` and return cluster means.

    A from-scratch restatement of the preregistered within-pass rule: walk
    the points in order, and let each unclaimed point absorb every later
    unclaimed point within the radius.

    Args:
        points: Detection centroids.
        radius: Clustering radius in metres.

    Returns:
        One mean centroid per cluster.
    """
    n = len(points)
    taken = [False] * n
    out: list[tuple[float, float]] = []
    arr = np.asarray(points, dtype=float) if n else np.zeros((0, 2))
    for i in range(n):
        if taken[i]:
            continue
        taken[i] = True
        members = [i]
        d = np.hypot(arr[:, 0] - arr[i, 0], arr[:, 1] - arr[i, 1])
        for j in range(n):
            if not taken[j] and d[j] <= radius:
                taken[j] = True
                members.append(j)
        out.append((float(arr[members, 0].mean()), float(arr[members, 1].mean())))
    return out


def hungarian_counts(
    dets: list[tuple[float, float]], refs: list[tuple[float, float]], tol: float,
) -> tuple[int, int, int]:
    """One-to-one match detections to references and return (TP, FP, FN).

    Args:
        dets: Detection centroids. refs: Reference points. tol: Match radius (m).

    Returns:
        Tuple of true positives, false positives and false negatives.
    """
    if not dets or not refs:
        return 0, len(dets), len(refs)
    d = np.asarray(dets, dtype=float)
    r = np.asarray(refs, dtype=float)
    dist = np.hypot(d[:, None, 0] - r[None, :, 0], d[:, None, 1] - r[None, :, 1])
    cost = np.where(dist <= tol, dist, tol * 1000.0)
    di, ri = linear_sum_assignment(cost)
    tp = int(sum(1 for a, b in zip(di, ri) if dist[a, b] <= tol))
    return tp, len(dets) - tp, len(refs) - tp


def map_of(tile_name: str) -> str:
    """Extract the map-sheet name from a tile filename.

    Args:
        tile_name: Tile filename such as ``K-35-052-4_32635_x0_y0.png``.

    Returns:
        The map name preceding the ``_x`` pixel-coordinate separator.
    """
    return tile_name.split("_x")[0]


def main() -> int:
    """Run every verification check.

    Returns:
        0 when all checks pass, else 1.
    """
    analysis = json.loads(ANALYSIS.read_text())
    dedup_summary = json.loads((SCORING / "dedup_summary.json").read_text())

    # ── 1. Raw and deduplicated counts ────────────────────────────────
    recomputed: dict[tuple[str, str], dict] = {}
    for arm, runs in PASS_FILES.items():
        for run, paths in runs.items():
            pts: list[tuple[float, float]] = []
            tiles: set[str] = set()
            for p in paths:
                data = json.loads(p.read_text())
                pts.extend(centroid_xy(f["geometry"]) for f in data["features"])
                tiles.update(data.get("processed_tiles") or [])
            dd = greedy_dedup(pts, DEDUP_M)
            recomputed[(arm, run)] = {"raw": len(pts), "dedup": dd, "tiles": tiles}

            rec = next(r for r in dedup_summary["passes"]
                       if r["arm"] == arm and r["run"] == run)
            check(
                f"counts {arm}/{run}",
                rec["n_raw"] == len(pts) and rec["n_dedup"] == len(dd),
                f"raw {len(pts)} vs {rec['n_raw']}, dedup {len(dd)} vs {rec['n_dedup']}",
            )

    # ── 2. Common footprint and ground truth in scope ─────────────────
    unions = {}
    for arm in ("armA", "armB", "armC"):
        b = json.loads((SCORING / "bounds" / f"h13_{arm}_bounds.geojson").read_text())
        unions[arm] = unary_union([shape(f["geometry"]) for f in b["features"]])
    common = unions["armA"].intersection(unions["armB"]).intersection(unions["armC"])
    check(
        "common footprint area",
        close(common.area / 1e6, analysis["scope"]["area_km2"], tol=1e-3),
        f"{common.area / 1e6:.3f} km2 vs {analysis['scope']['area_km2']:.3f} km2",
    )

    gt = json.loads(GT_PATH.read_text())
    gt_pts: dict[str, list[tuple[float, float]]] = {}
    common_bounds = json.loads(
        (SCORING / "bounds" / "h13_common_bounds.geojson").read_text())
    tile_shapes = [(f["properties"]["tile_name"], shape(f["geometry"]))
                   for f in common_bounds["features"]]
    for f in gt["features"]:
        p = Point(*centroid_xy(f["geometry"]))
        m = f["properties"]["Map"]
        if any(map_of(tn) == m and g.intersects(p) for tn, g in tile_shapes):
            gt_pts.setdefault(m, []).append((p.x, p.y))
    n_gt = sum(len(v) for v in gt_pts.values())
    check(
        "ground truth in common scope",
        n_gt == analysis["edge_detection"]["n_mounds"],
        f"{n_gt} vs {analysis['edge_detection']['n_mounds']}",
    )

    # ── 3. Per-arm micro precision / recall / F1 ──────────────────────
    for arm in ("armA", "armB", "armC"):
        tot = {"tp": 0, "fp": 0, "fn": 0}
        for run in RUNS:
            dd = [p for p in recomputed[(arm, run)]["dedup"]
                  if common.contains(Point(p))]
            by_map: dict[str, list[tuple[float, float]]] = {}
            for pt in dd:
                pp = Point(pt)
                for tn, g in tile_shapes:
                    if g.intersects(pp):
                        by_map.setdefault(map_of(tn), []).append(pt)
                        break
            for m in set(list(by_map) + list(gt_pts)):
                tp, fp, fn = hungarian_counts(
                    by_map.get(m, []), gt_pts.get(m, []), BUFFER_M)
                tot["tp"] += tp
                tot["fp"] += fp
                tot["fn"] += fn
        tp, fp, fn = (tot[k] / len(RUNS) for k in ("tp", "fp", "fn"))
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        ref = analysis["f1_vs_overlap"]["arms"][arm]
        check(
            f"micro-F1 {arm}",
            close(f1, ref["micro_f1"], tol=2e-3),
            f"F1 {f1:.4f} vs {ref['micro_f1']:.4f} "
            f"(P {prec:.4f} vs {ref['precision']:.4f}, "
            f"R {rec:.4f} vs {ref['recall']:.4f})",
        )

    # ── 4. Audited cost ───────────────────────────────────────────────
    for arm, rel_dir in (("armB", "outputs/h13/armB"), ("armC", "outputs/h13/armC")):
        total = 0.0
        for meta in sorted((PROJECT_ROOT / rel_dir).glob("*/*.meta.json")):
            total += float(json.loads(meta.read_text())
                           ["cost_estimate"]["total_cost_usd"])
        ref = analysis["cost_efficiency"]["per_arm"][arm]["total_usd"]
        check(f"audited cost {arm}", close(total, ref, tol=1e-6),
              f"${total:.6f} vs ${ref:.6f}")

    # ── 5. Edge low-margin subgroup ───────────────────────────────────
    low_ref = analysis["edge_detection"]["low_margin_subgroup"]
    native_tiles: dict[str, list[tuple[str, object]]] = {}
    for arm in ("armA", "armB", "armC"):
        b = json.loads((SCORING / "bounds" / f"h13_{arm}_bounds.geojson").read_text())
        native_tiles[arm] = [(f["properties"]["tile_name"], shape(f["geometry"]))
                             for f in b["features"]]

    flat_gt = [(m, p) for m, pts in gt_pts.items() for p in pts]
    margins_a = []
    for m, pt in flat_gt:
        p = Point(pt)
        ds = [g.exterior.distance(p) for tn, g in native_tiles["armA"]
              if map_of(tn) == m and g.intersects(p)]
        margins_a.append(max(ds) if ds else 0.0)
    low_idx = [i for i, v in enumerate(margins_a) if v < 100]
    check("low-margin subgroup size", len(low_idx) == low_ref["n_mounds"],
          f"{len(low_idx)} vs {low_ref['n_mounds']}")

    for arm in ("armA", "armB", "armC"):
        hits = np.zeros(len(flat_gt))
        for run in RUNS:
            dd = [p for p in recomputed[(arm, run)]["dedup"]
                  if common.contains(Point(p))]
            by_map: dict[str, list[tuple[float, float]]] = {}
            for pt in dd:
                pp = Point(pt)
                for tn, g in tile_shapes:
                    if g.intersects(pp):
                        by_map.setdefault(map_of(tn), []).append(pt)
                        break
            for m in set(gt_pts):
                refs_m = gt_pts[m]
                dets_m = by_map.get(m, [])
                if not refs_m or not dets_m:
                    continue
                d = np.asarray(dets_m, dtype=float)
                r = np.asarray(refs_m, dtype=float)
                dist = np.hypot(d[:, None, 0] - r[None, :, 0],
                                d[:, None, 1] - r[None, :, 1])
                cost = np.where(dist <= BUFFER_M, dist, BUFFER_M * 1000.0)
                di, ri = linear_sum_assignment(cost)
                offset = flat_gt.index((m, refs_m[0]))
                for a, bb in zip(di, ri):
                    if dist[a, bb] <= BUFFER_M:
                        hits[offset + bb] += 1
        recall_low = float(hits[low_idx].mean() / len(RUNS))
        check(f"low-margin recall {arm}",
              close(recall_low, low_ref[f"recall_{arm}"], tol=2e-3),
              f"{recall_low:.4f} vs {low_ref[f'recall_{arm}']:.4f}")

    n_fail = sum(1 for _, ok, _ in results if not ok)
    print(f"\n{len(results) - n_fail}/{len(results)} checks passed.")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
