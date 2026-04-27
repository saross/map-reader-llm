#!/usr/bin/env python3
"""
Inter-Pass Agreement Analysis (Cohen's kappa + borderline-instability)
=======================================================================

For each Phase 3a stratum and the gold-standard-v2 4-map 487-tile data,
this script computes:

1. **Pairwise Cohen's kappa — candidate-match**
   Uses ``lib_consensus.cluster_across_passes`` at the canonical 20 m
   UTM-32635 distance threshold to build the union cluster set across
   all K passes for a condition. For each cluster c and pass-pair (i, j),
   pass i is assigned 1 if it contributed a member to c, else 0. Cohen's
   kappa is computed on the per-cluster vectors of pass i vs pass j across
   the union; the observed agreement P_o is reported alongside, since
   kappa exhibits the well-known marginal-prevalence paradox at extremes.

2. **Pairwise Cohen's kappa — tile-presence**
   The denominator is the intersection of ``*.tiles.json`` ``completed``
   lists across all passes in the cell (typically 487). For each tile t,
   pass i is assigned 1 if it made any detection on t, else 0. Kappa is
   computed pairwise.

3. **Borderline-instability check**
   At the consensus threshold t* (read from the per-condition cell or
   recomputed locally on the same data), the borderline set
   B = {clusters with vote_count in {t*-1, t*, t*+1}} is identified.
   The script reports (a) absolute count, (b) percent of consensus
   survivors at t*, (c) percent of GT mounds gained / lost (via spatial
   join to the reference layer at 20 m), and (d) the fragility ratio
   |borderline| / |consensus@t*|.

4. **Sensitivity row**
   For the gold-standard-v2 cell, candidate-match kappa is also computed
   at 30 m cluster radius (in addition to 20 m).

Outputs (all under ``results/inter-pass-agreement/``)
    - ``agreement.json`` — full per-pair K x K matrices per stratum,
      condition-level summaries
    - ``report_autogen.md`` — auto-generated synthesis tables
    - ``figures/<stratum>__<condition>.png`` — K x K heatmap per stratum

Caveats (also noted in the autogen md)
    - Cluster radius default 20 m; 30 m sensitivity row included for
      gold-standard-v2.
    - Tile denominator aligned via intersection of per-pass
      ``completed`` lists.
    - Marginal-prevalence kappa paradox: P_o is always reported
      alongside kappa.

Usage::

    python scripts/analyse_inter_pass_agreement.py \\
        --output-dir results/inter-pass-agreement/ \\
        --max-workers 4

Author: Shawn Ross, Claude Code
Licence: Apache 2.0
Created: 2026-04-27
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # headless backend for sapphire / CI
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import cohen_kappa_score

# sklearn raises noisy "single label found" warnings when one pass
# detects nothing on the intersected tile universe (genuine signal —
# we want to record it as kappa = NaN, not log-spam each call).
warnings.filterwarnings(
    "ignore", category=UserWarning, module="sklearn",
)
warnings.filterwarnings(
    "ignore", category=RuntimeWarning,
    message="invalid value encountered in scalar divide",
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from lib_consensus import (  # noqa: E402
    cluster_across_passes,
    deduplicate_within_pass,
)

__version__ = "1.0.0"

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_GT = (
    PROJECT_ROOT / "inputs/vectors/references/mounds-reference.geojson"
)
BOUNDS_487 = PROJECT_ROOT / "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"
BOUNDS_340 = PROJECT_ROOT / "inputs/vectors/bounds/full_evaluation_bounds.geojson"

DEFAULT_RADIUS_M = 20.0
SENSITIVITY_RADIUS_M = 30.0
GT_BUFFER_M = 20.0  # for "GT gained/lost" join


# ---------------------------------------------------------------------------
# Stratum / condition registry
# ---------------------------------------------------------------------------
#
# Each entry is keyed by stratum name; the value is a dict mapping condition
# names to dicts with:
#   run_dir          — Path (relative to PROJECT_ROOT)
#   K                — declared number of passes
#   bounds           — Path to evaluation bounds GeoJSON
#   optimal_t        — F1-optimal consensus threshold (from
#                      secondary_effects.md / phase3a-text-matrix); used
#                      for borderline analysis only. May be None — in that
#                      case borderline analysis is skipped for that cell.
#
# Notes on K/threshold provenance
#   - Phase3a image-track matrix (487 tiles): K=10 (T=0.0 has K=3); thresholds
#     read from results/secondary-effects/secondary_effects.json
#   - Phase3a text-track matrix: T=0.7 has K=30; thresholds from
#     results/phase3a-text-matrix/secondary_effects.json
#   - Phase3a retest (340 tiles): K=30 across T=0.3/0.7/1.0; no canonical
#     optimal threshold has been published for these — borderline analysis
#     uses a locally-computed optimum.
#   - Gold-standard-v2 (487 tiles): K=5; canonical threshold = 4 (4-of-5)
#     per the extended-buffer report.

CONDITION_REGISTRY: dict[str, dict[str, dict[str, Any]]] = {
    # ----- Phase 3a image-track matrix (8 cells, 487 tiles) -----
    "phase3a_image_matrix": {
        "HIGH-T0.0": {
            "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0",
            "K": 3, "optimal_t": 1, "bounds": BOUNDS_487,
        },
        "HIGH-T0.3": {
            "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3",
            "K": 10, "optimal_t": 9, "bounds": BOUNDS_487,
        },
        "HIGH-T0.7": {
            "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7",
            "K": 10, "optimal_t": 7, "bounds": BOUNDS_487,
        },
        "HIGH-T1.0": {
            "run_dir": "outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0",
            "K": 10, "optimal_t": 6, "bounds": BOUNDS_487,
        },
        "MIN-T0.0": {
            "run_dir": "outputs/h11/n1-outstanding-384/image-t0",
            "K": 3, "optimal_t": 2, "bounds": BOUNDS_487,
        },
        "MIN-T0.3": {
            "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t0.3",
            "K": 10, "optimal_t": 10, "bounds": BOUNDS_487,
        },
        "MIN-T0.7": {
            "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t0.7",
            "K": 10, "optimal_t": 8, "bounds": BOUNDS_487,
        },
        "MIN-T1.0": {
            "run_dir": "outputs/h11/pv-diag-384/image-n5/image-t1.0",
            "K": 10, "optimal_t": 8, "bounds": BOUNDS_487,
        },
    },
    # ----- Phase 3a text-track matrix (8 cells, 487 tiles) -----
    "phase3a_text_matrix": {
        "HIGH-T0.0": {
            "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0",
            "K": 3, "optimal_t": 3, "bounds": BOUNDS_487,
        },
        "HIGH-T0.3": {
            "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3",
            "K": 10, "optimal_t": 10, "bounds": BOUNDS_487,
        },
        "HIGH-T0.7": {
            "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7",
            "K": 30, "optimal_t": 26, "bounds": BOUNDS_487,
        },
        "HIGH-T1.0": {
            "run_dir": "outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0",
            "K": 10, "optimal_t": 9, "bounds": BOUNDS_487,
        },
        "MIN-T0.0": {
            "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.0",
            "K": 3, "optimal_t": 3, "bounds": BOUNDS_487,
        },
        "MIN-T0.3": {
            "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3",
            "K": 10, "optimal_t": 10, "bounds": BOUNDS_487,
        },
        "MIN-T0.7": {
            "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7",
            "K": 30, "optimal_t": 29, "bounds": BOUNDS_487,
        },
        "MIN-T1.0": {
            "run_dir": "outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0",
            "K": 10, "optimal_t": 9, "bounds": BOUNDS_487,
        },
    },
    # ----- SCALE4-T0.7 (MCC winner, K=10, 487 tiles) -----
    "scale4_t07": {
        "SCALE4-T0.7": {
            "run_dir": "outputs/h11/pv-diag-384/scale-4-optimal-487",
            "K": 10, "optimal_t": 6, "bounds": BOUNDS_487,
        },
    },
    # ----- Phase 3a retest extensions (K=30, 340 tiles) -----
    # Threshold is locally optimised from the per-condition vote distribution
    # because no canonical t* is published for the retest layout; we use the
    # round(K * 0.7) heuristic as the borderline anchor (consistent with
    # secondary_effects observations that ~70% of K is the typical optimum
    # at high temperature).
    "phase3a_retest": {
        "image-T0.3": {
            "run_dir": "outputs/retest/phase3a/track1-image/T0.3",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
        "image-T0.7": {
            "run_dir": "outputs/retest/phase3a/track1-image/T0.7",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
        "image-T1.0": {
            "run_dir": "outputs/retest/phase3a/track1-image/T1.0",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
        "text-T0.3": {
            "run_dir": "outputs/retest/phase3a/track2-text/T0.3",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
        "text-T0.7": {
            "run_dir": "outputs/retest/phase3a/track2-text/T0.7",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
        "text-T1.0": {
            "run_dir": "outputs/retest/phase3a/track2-text/T1.0",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
        "high-text-T0.3": {
            "run_dir": "outputs/retest/phase3a-high/track2-text/T0.3",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
        "high-text-T0.7": {
            "run_dir": "outputs/retest/phase3a-high/track2-text/T0.7",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
        "high-text-T1.0": {
            "run_dir": "outputs/retest/phase3a-high/track2-text/T1.0",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
        "replication-high": {
            "run_dir": "outputs/retest/phase3a-replication/high",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
        "replication-minimal": {
            "run_dir": "outputs/retest/phase3a-replication/minimal",
            "K": 30, "optimal_t": None, "bounds": BOUNDS_340,
        },
    },
    # ----- Gold-standard-v2 (K=5, 487 tiles, canonical 4-of-5) -----
    "gold_standard_v2": {
        "detect_brief-text": {
            "run_dir": "outputs/h11/gold-standard-v2/proposer/detect_brief-text",
            "K": 5, "optimal_t": 4, "bounds": BOUNDS_487,
        },
    },
}


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_run_features(run_dir: Path) -> list[dict]:
    """Load all detection GeoJSON features from a run directory.

    Mirrors ``analyse_secondary_effects.py``'s tolerant glob: any
    ``*.geojson`` that does not have ``.meta`` or ``.tiles`` in its
    name. This handles both ``detections_T<x>_run<NN>.geojson`` (retest
    layout) and ``detections-<config>-3-flash-<date>.geojson`` (h11 /
    gold-standard-v2 layout) without falling foul of the underscore-only
    glob in ``lib_consensus.load_run_detections``.

    Args:
        run_dir: Path to a run directory.

    Returns:
        List of GeoJSON feature dictionaries (possibly empty).
    """
    if not run_dir.exists() or not run_dir.is_dir():
        return []
    features: list[dict] = []
    candidates = [
        f for f in sorted(run_dir.glob("*.geojson"))
        if ".meta" not in f.name and ".tiles" not in f.name
    ]
    for gj in candidates:
        try:
            with open(gj, encoding="utf-8") as f:
                data = json.load(f)
            features.extend(data.get("features", []))
        except json.JSONDecodeError as exc:
            logger.warning("Could not parse %s: %s", gj, exc)
    return features


def load_run_tiles(run_dir: Path) -> set[str]:
    """Load the set of completed tile names from a run's tiles.json.

    Returns an empty set if no ``*.tiles.json`` is present, in which
    case the caller should treat the pass as unusable for tile-presence
    kappa.

    Args:
        run_dir: Path to a run directory.

    Returns:
        Set of tile names that completed successfully in this pass.
    """
    if not run_dir.exists():
        return set()
    tiles_files = sorted(run_dir.glob("*.tiles.json"))
    if not tiles_files:
        return set()
    try:
        with open(tiles_files[0], encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        logger.warning("Could not parse %s: %s", tiles_files[0], exc)
        return set()
    completed = data.get("completed", []) or []
    return set(completed)


def discover_run_dirs(run_root: Path) -> list[Path]:
    """List all ``run_*`` subdirectories of a condition root, sorted by
    numeric run id (so run_2 comes before run_10).

    Args:
        run_root: Path to a condition root that contains ``run_<N>``
            subdirectories.

    Returns:
        Sorted list of run directory paths.
    """
    if not run_root.exists():
        return []
    runs = []
    for p in run_root.glob("run_*"):
        if not p.is_dir():
            continue
        m = re.match(r"run_(\d+)$", p.name)
        if m:
            runs.append((int(m.group(1)), p))
    runs.sort(key=lambda pair: pair[0])
    return [p for _, p in runs]


# ---------------------------------------------------------------------------
# Per-condition computation
# ---------------------------------------------------------------------------


def compute_candidate_match_matrix(
    pass_run_dirs: dict[str, Path],
    radius_m: float,
) -> tuple[np.ndarray, np.ndarray, list[str], list[dict]]:
    """Build the candidate-match kappa and observed-agreement matrices.

    For each pass, detections are first deduplicated (within-pass) at
    the given radius via ``deduplicate_within_pass``. Detections are then
    pooled across passes and clustered via ``cluster_across_passes``.
    The resulting union cluster set defines the rating space:

        For each cluster c and each pass i,
            x_{i,c} = 1 if pass i contributed at least one detection to c
                    = 0 otherwise.

    Cohen's kappa and observed agreement are computed pairwise on the
    K passes' x-vectors.

    Args:
        pass_run_dirs: ordered mapping ``pass_id -> run_dir``.
        radius_m: clustering radius in metres (canonical 20 m, or 30 m
            for the gold-standard sensitivity row).

    Returns:
        Tuple ``(kappa_matrix, p_o_matrix, pass_ids, clusters)`` where:

        - ``kappa_matrix``: K x K float array, NaN on the diagonal.
        - ``p_o_matrix``:   K x K float array of observed agreement
          (proportion of clusters where both passes agree).
        - ``pass_ids``: ordered list of pass identifiers.
        - ``clusters``: list of cluster dicts from
          ``cluster_across_passes`` (preserved for downstream
          borderline analysis to avoid recomputation).
    """
    pass_detections: dict[str, list[dict]] = {}
    for pass_id, run_dir in pass_run_dirs.items():
        feats = load_run_features(run_dir)
        if not feats:
            # Preserve empty pass — clustering will still treat it as
            # contributing nothing, which gives a row/column of all 0.
            pass_detections[pass_id] = []
            continue
        pass_detections[pass_id] = deduplicate_within_pass(
            feats, distance_thresh=radius_m,
        )

    clusters = cluster_across_passes(
        pass_detections, distance_thresh=radius_m,
    )

    pass_ids = list(pass_run_dirs.keys())
    K = len(pass_ids)

    if not clusters:
        return (
            np.full((K, K), np.nan),
            np.full((K, K), np.nan),
            pass_ids,
            clusters,
        )

    # Build presence matrix: rows = passes, cols = clusters
    presence = np.zeros((K, len(clusters)), dtype=np.int8)
    pass_index = {pid: i for i, pid in enumerate(pass_ids)}
    for c_idx, cluster in enumerate(clusters):
        for pid in cluster["contributing_passes"]:
            if pid in pass_index:
                presence[pass_index[pid], c_idx] = 1

    kappa_matrix = np.full((K, K), np.nan)
    p_o_matrix = np.full((K, K), np.nan)
    for i in range(K):
        for j in range(K):
            if i == j:
                continue
            try:
                kappa_matrix[i, j] = cohen_kappa_score(
                    presence[i], presence[j],
                )
            except ValueError:
                kappa_matrix[i, j] = np.nan
            p_o_matrix[i, j] = float(
                (presence[i] == presence[j]).mean()
            )

    return kappa_matrix, p_o_matrix, pass_ids, clusters


def compute_tile_presence_matrix(
    pass_run_dirs: dict[str, Path],
) -> tuple[np.ndarray, list[str], list[str], list[str]]:
    """Build the tile-presence kappa matrix.

    For each pass, the union of source-tile names across all detections
    is computed. The denominator is the intersection of completed-tile
    sets across all retained passes. A pass is dropped from the
    intersection (and recorded in ``dropped``) if it has no
    ``*.tiles.json`` available.

    Args:
        pass_run_dirs: ordered mapping ``pass_id -> run_dir``.

    Returns:
        Tuple ``(kappa_matrix, pass_ids, tile_universe_sorted, dropped)``:

        - ``kappa_matrix``: KxK float array (NaN diagonal); K is the
          number of retained passes.
        - ``pass_ids``: retained pass identifiers (in original order).
        - ``tile_universe_sorted``: sorted list of tile names used as
          the denominator.
        - ``dropped``: pass identifiers excluded for missing
          ``*.tiles.json``.
    """
    tile_sets_per_pass: dict[str, set[str]] = {}
    detection_tiles_per_pass: dict[str, set[str]] = {}
    dropped: list[str] = []

    for pass_id, run_dir in pass_run_dirs.items():
        completed = load_run_tiles(run_dir)
        if not completed:
            dropped.append(pass_id)
            continue
        tile_sets_per_pass[pass_id] = completed

        feats = load_run_features(run_dir)
        det_tiles: set[str] = set()
        for feat in feats:
            props = feat.get("properties", {})
            t = props.get("source_tile") or props.get("tile_id")
            if t:
                det_tiles.add(t)
        detection_tiles_per_pass[pass_id] = det_tiles

    pass_ids = list(tile_sets_per_pass.keys())
    K = len(pass_ids)
    if K < 2:
        return np.full((K, K), np.nan), pass_ids, [], dropped

    # Intersection across retained passes
    universe: set[str] = set.intersection(
        *tile_sets_per_pass.values(),
    )
    universe_sorted = sorted(universe)
    if not universe_sorted:
        return np.full((K, K), np.nan), pass_ids, [], dropped

    # Build presence vectors over the intersected universe
    presence = np.zeros((K, len(universe_sorted)), dtype=np.int8)
    for i, pid in enumerate(pass_ids):
        det_tiles = detection_tiles_per_pass.get(pid, set())
        for j, t in enumerate(universe_sorted):
            if t in det_tiles:
                presence[i, j] = 1

    kappa_matrix = np.full((K, K), np.nan)
    for i in range(K):
        for j in range(K):
            if i == j:
                continue
            try:
                kappa_matrix[i, j] = cohen_kappa_score(
                    presence[i], presence[j],
                )
            except ValueError:
                kappa_matrix[i, j] = np.nan

    return kappa_matrix, pass_ids, universe_sorted, dropped


def compute_borderline_metrics(
    clusters: list[dict],
    optimal_t: int | None,
    K: int,
    bounds_path: Path,
    gt_gdf,
) -> dict[str, Any]:
    """Compute borderline-instability metrics for one condition.

    Args:
        clusters: cluster list from ``cluster_across_passes``.
        optimal_t: published optimal consensus threshold, or ``None``.
            If ``None``, a local optimum is taken as ``round(K * 0.7)``
            clamped to ``[1, K]`` (a coarse anchor used only when no
            canonical t* exists; this is documented in the report).
        K: number of passes in the condition.
        bounds_path: path to the evaluation-bounds GeoJSON (used only to
            log the corpus size; clusters are already pooled in UTM).
        gt_gdf: GeoDataFrame of GT mounds in the canonical UTM CRS.

    Returns:
        Dict with keys: ``optimal_t``, ``t_source``, ``borderline_n``,
        ``consensus_n``, ``fragility_ratio``, ``borderline_pct``,
        ``gt_gained_pct``, ``gt_lost_pct``, ``gt_total``.
    """
    if not clusters:
        return {
            "optimal_t": optimal_t,
            "t_source": "registry" if optimal_t is not None else "none",
            "borderline_n": 0,
            "consensus_n": 0,
            "fragility_ratio": None,
            "borderline_pct": None,
            "gt_gained_pct": None,
            "gt_lost_pct": None,
            "gt_total": int(len(gt_gdf)),
        }

    if optimal_t is None:
        # Local fallback anchor: 70 percent of K, clamped to [1, K].
        optimal_t = max(1, min(K, int(round(K * 0.7))))
        t_source = f"fallback_round(K*0.7)={optimal_t}"
    else:
        t_source = "registry"

    consensus = [c for c in clusters if c["vote_count"] >= optimal_t]
    borderline = [
        c for c in clusters
        if (optimal_t - 1) <= c["vote_count"] <= (optimal_t + 1)
    ]
    consensus_n = len(consensus)
    borderline_n = len(borderline)
    fragility = (
        borderline_n / consensus_n if consensus_n > 0 else None
    )
    borderline_pct = (
        100.0 * borderline_n / consensus_n if consensus_n > 0 else None
    )

    # GT gained / lost: spatial join of borderline to GT at GT_BUFFER_M
    from shapely.geometry import Point as ShapelyPoint  # local import OK

    gt_gained_pct: float | None = None
    gt_lost_pct: float | None = None
    if not gt_gdf.empty:
        # Build the set of GT indices matched by clusters at vote >= t-1
        # ("gained") and at vote >= t+1 ("retained" — used as the
        # baseline). The difference, divided by total GT, gives the
        # fraction of GT that the borderline band represents.
        # GT may be MultiPoint geometries (the canonical mounds-
        # reference uses MultiPoint per row); use centroid.x/y to
        # collapse to a single representative coordinate.
        from scipy.spatial import cKDTree

        gt_xy = np.array(
            [(g.centroid.x, g.centroid.y)
             for g in gt_gdf.geometry.values],
        )
        gt_tree = cKDTree(gt_xy)

        def _gt_indices_for(threshold: int) -> set[int]:
            idx_set: set[int] = set()
            for c in clusters:
                if c["vote_count"] < threshold:
                    continue
                pt = ShapelyPoint(c["centroid"])
                hits = gt_tree.query_ball_point(
                    [pt.x, pt.y], r=GT_BUFFER_M,
                )
                idx_set.update(hits)
            return idx_set

        gt_at_t_minus = _gt_indices_for(max(1, optimal_t - 1))
        gt_at_t = _gt_indices_for(optimal_t)
        gt_at_t_plus = _gt_indices_for(min(K, optimal_t + 1))

        n_gt = len(gt_gdf)
        # Mounds matched only when including the borderline band
        # (i.e. would be lost on raising t by one).
        lost_if_raise = gt_at_t - gt_at_t_plus
        # Mounds matched only by relaxing to t-1 (gained).
        gained_if_lower = gt_at_t_minus - gt_at_t
        gt_lost_pct = 100.0 * len(lost_if_raise) / n_gt
        gt_gained_pct = 100.0 * len(gained_if_lower) / n_gt

    return {
        "optimal_t": int(optimal_t),
        "t_source": t_source,
        "borderline_n": borderline_n,
        "consensus_n": consensus_n,
        "fragility_ratio": (
            round(fragility, 4) if fragility is not None else None
        ),
        "borderline_pct": (
            round(borderline_pct, 2)
            if borderline_pct is not None else None
        ),
        "gt_gained_pct": (
            round(gt_gained_pct, 2)
            if gt_gained_pct is not None else None
        ),
        "gt_lost_pct": (
            round(gt_lost_pct, 2)
            if gt_lost_pct is not None else None
        ),
        "gt_total": int(len(gt_gdf)),
    }


def summarise_matrix(matrix: np.ndarray) -> dict[str, float | None]:
    """Summarise an off-diagonal matrix of pairwise statistics.

    Args:
        matrix: K x K array (NaN on the diagonal).

    Returns:
        Dict with mean / sd / min / max / n_pairs (off-diagonal,
        non-NaN only).
    """
    if matrix.size == 0:
        return {
            "mean": None, "sd": None, "min": None,
            "max": None, "n_pairs": 0,
        }
    K = matrix.shape[0]
    if K < 2:
        return {
            "mean": None, "sd": None, "min": None,
            "max": None, "n_pairs": 0,
        }
    mask = ~np.eye(K, dtype=bool)
    flat = matrix[mask]
    flat = flat[~np.isnan(flat)]
    if flat.size == 0:
        return {
            "mean": None, "sd": None, "min": None,
            "max": None, "n_pairs": 0,
        }
    return {
        "mean": round(float(flat.mean()), 4),
        "sd": (
            round(float(flat.std(ddof=1)), 4)
            if flat.size > 1 else 0.0
        ),
        "min": round(float(flat.min()), 4),
        "max": round(float(flat.max()), 4),
        "n_pairs": int(flat.size),
    }


def _process_condition(
    args: tuple,
) -> tuple[str, str, dict[str, Any]]:
    """Worker entrypoint for ProcessPoolExecutor.

    Loads everything fresh in the worker process — sklearn, geopandas,
    and shapely all serialise poorly across process boundaries.

    Args:
        args: 6-tuple of (stratum, condition, cfg, gt_path, default_radius,
            sensitivity_radius).

    Returns:
        Tuple of (stratum, condition, condition_result_dict).
    """
    (
        stratum, condition, cfg, gt_path, default_radius,
        sensitivity_radius,
    ) = args

    # Fresh imports inside the worker
    import sys as _sys
    import warnings as _warnings
    _sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
    # Mirror parent-process filters: sklearn warns when a kappa input
    # has only one class on the tile universe (typical for sparse
    # detection patterns at K=30) — we record those as NaN.
    _warnings.filterwarnings(
        "ignore", category=UserWarning, module="sklearn",
    )
    _warnings.filterwarnings(
        "ignore", category=RuntimeWarning,
        message="invalid value encountered in scalar divide",
    )
    from evaluate_detections import load_geojson as _lg

    gt_gdf = _lg(gt_path)
    run_root = PROJECT_ROOT / cfg["run_dir"]
    run_dirs = discover_run_dirs(run_root)
    if not run_dirs:
        return stratum, condition, {
            "error": f"No run_* dirs under {run_root}",
            "K_declared": cfg["K"],
            "K_found": 0,
        }

    pass_run_dirs = {p.name: p for p in run_dirs}
    K_found = len(pass_run_dirs)

    # Skip K < 3 cells (instructed by the task spec)
    if K_found < 3:
        return stratum, condition, {
            "skipped_reason": "K < 3",
            "K_declared": cfg["K"],
            "K_found": K_found,
        }

    # 1. Candidate-match kappa at the default 20 m radius
    cm_kappa, cm_p_o, pass_ids, clusters = compute_candidate_match_matrix(
        pass_run_dirs, radius_m=default_radius,
    )

    # 2. Tile-presence kappa
    tp_kappa, tp_pass_ids, tile_universe, dropped = (
        compute_tile_presence_matrix(pass_run_dirs)
    )

    # 3. Borderline metrics (uses the 20 m clusters)
    borderline = compute_borderline_metrics(
        clusters,
        optimal_t=cfg.get("optimal_t"),
        K=K_found,
        bounds_path=cfg["bounds"],
        gt_gdf=gt_gdf,
    )

    # 4. Sensitivity row (gold-standard-v2 only)
    sens: dict[str, Any] | None = None
    if stratum == "gold_standard_v2":
        cm_kappa_30, cm_p_o_30, _, _ = compute_candidate_match_matrix(
            pass_run_dirs, radius_m=sensitivity_radius,
        )
        sens = {
            "radius_m": sensitivity_radius,
            "kappa_matrix": cm_kappa_30.tolist(),
            "p_o_matrix": cm_p_o_30.tolist(),
            "pass_ids": pass_ids,
            "summary": {
                "kappa": summarise_matrix(cm_kappa_30),
                "p_o": summarise_matrix(cm_p_o_30),
            },
        }

    return stratum, condition, {
        "K_declared": cfg["K"],
        "K_found": K_found,
        "n_clusters_union": len(clusters),
        "tile_universe_n": len(tile_universe),
        "tile_passes_dropped": dropped,
        "candidate_match": {
            "radius_m": default_radius,
            "kappa_matrix": cm_kappa.tolist(),
            "p_o_matrix": cm_p_o.tolist(),
            "pass_ids": pass_ids,
            "summary": {
                "kappa": summarise_matrix(cm_kappa),
                "p_o": summarise_matrix(cm_p_o),
            },
        },
        "tile_presence": {
            "kappa_matrix": tp_kappa.tolist(),
            "pass_ids": tp_pass_ids,
            "summary": {"kappa": summarise_matrix(tp_kappa)},
        },
        "borderline": borderline,
        "candidate_match_sensitivity": sens,
    }


# ---------------------------------------------------------------------------
# Output: figures + markdown
# ---------------------------------------------------------------------------


def _coerce_matrix(payload: list[list[float | None]]) -> np.ndarray:
    """Convert a JSON-friendly nested list (with possible Nones) into a
    NaN-safe numpy float array."""
    arr = np.array(payload, dtype=float)
    return arr


def write_heatmap(
    kappa_matrix: np.ndarray,
    pass_ids: list[str],
    title: str,
    output_path: Path,
) -> None:
    """Write a K x K heatmap of pairwise kappa values to disk.

    Args:
        kappa_matrix: K x K float array (NaN allowed on diagonal).
        pass_ids: K labels.
        title: figure title.
        output_path: PNG output path. Parent dirs will be created.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    K = kappa_matrix.shape[0]

    # Cap dimensions for very large K (e.g. K=30) so labels remain legible
    figsize = (max(6, K * 0.35), max(5, K * 0.35))
    fig, ax = plt.subplots(figsize=figsize)
    im = ax.imshow(
        kappa_matrix, cmap="viridis", vmin=-0.1, vmax=1.0,
        aspect="auto",
    )
    ax.set_xticks(range(K))
    ax.set_yticks(range(K))
    ax.set_xticklabels(pass_ids, rotation=90, fontsize=7)
    ax.set_yticklabels(pass_ids, fontsize=7)
    ax.set_title(title, fontsize=10)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("Cohen's kappa", fontsize=9)
    fig.tight_layout()
    fig.savefig(output_path, dpi=120)
    plt.close(fig)


def render_autogen_md(
    results: dict[str, dict[str, dict[str, Any]]],
    output_path: Path,
) -> None:
    """Render the auto-generated synthesis markdown.

    Note: the hand-authored synthesis is at ``report.md``; this file is
    the auto-generated companion (matches the existing ``_autogen.md``
    convention used by ``analyse_secondary_effects.py``).
    """
    lines: list[str] = []
    lines.append("# Inter-Pass Agreement Analysis (autogen)")
    lines.append("")
    lines.append(
        f"**Generated**: {datetime.now(tz=timezone.utc).isoformat()}",
    )
    lines.append(f"**Script version**: {__version__}")
    lines.append(
        "**Script**: `scripts/analyse_inter_pass_agreement.py`",
    )
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    lines.append(
        "- **Cluster radius**: candidate-match kappa uses a 20 m radius "
        "in UTM-32635 by default. A 30 m sensitivity row is reported "
        "for the gold-standard-v2 cell only (and labelled `_sens` "
        "in tables)."
    )
    lines.append(
        "- **Tile denominator alignment**: tile-presence kappa uses "
        "the intersection of per-pass `*.tiles.json` `completed` lists. "
        "Passes with no tiles.json are dropped and listed under "
        "`tile_passes_dropped` in the JSON output."
    )
    lines.append(
        "- **Marginal-prevalence kappa paradox**: Cohen's kappa "
        "deflates when one rating dominates (e.g. very few "
        "detections per pass means most cluster-presence vectors are "
        "near-all-zero). Observed agreement P_o is reported alongside "
        "kappa to make this visible at extremes."
    )
    lines.append(
        "- **Phase 3a retest borderline thresholds**: no canonical "
        "F1-optimal threshold has been published for the K=30 retest "
        "cells; the borderline anchor uses `round(K * 0.7) = 21` as a "
        "documented fallback. Borderline metrics for these cells should "
        "be read in relative comparison rather than as headline numbers."
    )
    lines.append("")

    # Headline summary table — one row per (stratum, condition)
    lines.append("## 1. Headline Pairwise Kappa Summary")
    lines.append("")
    lines.append(
        "Mean / SD / min / max are computed over off-diagonal entries "
        "of the K x K matrix."
    )
    lines.append("")
    lines.append(
        "| Stratum | Condition | K | n_clusters | "
        "kappa_cm mean | kappa_cm SD | kappa_cm min | kappa_cm max | "
        "P_o_cm mean | kappa_tile mean |"
    )
    lines.append(
        "|---------|-----------|--:|----------:|"
        "------:|------:|------:|------:|------:|------:|"
    )
    for stratum, conds in results.items():
        for cond, row in conds.items():
            if "skipped_reason" in row or "error" in row:
                lines.append(
                    f"| {stratum} | {cond} | "
                    f"{row.get('K_found', '-')} | - | "
                    f"_{row.get('skipped_reason') or row.get('error')}_ "
                    "| - | - | - | - | - |"
                )
                continue
            cm = row["candidate_match"]["summary"]["kappa"]
            po = row["candidate_match"]["summary"]["p_o"]
            tk = row["tile_presence"]["summary"]["kappa"]
            lines.append(
                f"| {stratum} | {cond} | {row['K_found']} | "
                f"{row['n_clusters_union']} | "
                f"{_fmt(cm['mean'])} | {_fmt(cm['sd'])} | "
                f"{_fmt(cm['min'])} | {_fmt(cm['max'])} | "
                f"{_fmt(po['mean'])} | {_fmt(tk['mean'])} |"
            )
    lines.append("")

    # Borderline-instability table
    lines.append("## 2. Borderline-Instability")
    lines.append("")
    lines.append(
        "Borderline set B = {clusters with vote_count in "
        "{t* - 1, t*, t* + 1}}; fragility = |B| / |consensus@t*|."
    )
    lines.append("")
    lines.append(
        "| Stratum | Condition | K | t* | t* source | "
        "Consensus n | Borderline n | Borderline % | "
        "Fragility | GT lost % | GT gained % |"
    )
    lines.append(
        "|---------|-----------|--:|---:|-----------|"
        "----------:|----------:|----------:|"
        "----------:|----------:|----------:|"
    )
    for stratum, conds in results.items():
        for cond, row in conds.items():
            if "skipped_reason" in row or "error" in row:
                continue
            b = row["borderline"]
            lines.append(
                f"| {stratum} | {cond} | {row['K_found']} | "
                f"{b['optimal_t']} | {b['t_source']} | "
                f"{b['consensus_n']} | {b['borderline_n']} | "
                f"{_fmt(b['borderline_pct'])} | "
                f"{_fmt(b['fragility_ratio'])} | "
                f"{_fmt(b['gt_lost_pct'])} | "
                f"{_fmt(b['gt_gained_pct'])} |"
            )
    lines.append("")

    # Sensitivity row (gold-standard-v2)
    lines.append("## 3. Cluster-Radius Sensitivity (gold-standard-v2)")
    lines.append("")
    lines.append(
        "Candidate-match kappa is recomputed at 30 m for the "
        "gold-standard-v2 cell. Compare with the 20 m row above."
    )
    lines.append("")
    sens_rows = []
    for stratum, conds in results.items():
        for cond, row in conds.items():
            sens = row.get("candidate_match_sensitivity")
            if not sens:
                continue
            cm = sens["summary"]["kappa"]
            po = sens["summary"]["p_o"]
            sens_rows.append(
                f"| {stratum} | {cond} | {sens['radius_m']} m | "
                f"{_fmt(cm['mean'])} | {_fmt(cm['sd'])} | "
                f"{_fmt(cm['min'])} | {_fmt(cm['max'])} | "
                f"{_fmt(po['mean'])} |"
            )
    if sens_rows:
        lines.append(
            "| Stratum | Condition | Radius | "
            "kappa mean | kappa SD | kappa min | kappa max | P_o mean |"
        )
        lines.append(
            "|---------|-----------|-------:|"
            "----------:|---------:|----------:|----------:|---------:|"
        )
        lines.extend(sens_rows)
    else:
        lines.append("_No sensitivity rows produced._")
    lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Markdown (autogen): %s", output_path)


def _fmt(val: float | int | None) -> str:
    """Format a numeric value with a missing-value placeholder."""
    if val is None:
        return "—"
    if isinstance(val, int):
        return str(val)
    return f"{val:.3f}"


# ---------------------------------------------------------------------------
# CLI + main
# ---------------------------------------------------------------------------


def main() -> int:
    """Run inter-pass agreement analysis across all strata."""
    parser = argparse.ArgumentParser(
        description=(
            "Inter-pass agreement (Cohen's kappa) and "
            "borderline-instability for Phase 3a strata and the "
            "gold-standard-v2 4-map 487-tile data."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=PROJECT_ROOT / "results" / "inter-pass-agreement",
        help="Directory for agreement.json, report_autogen.md, "
             "figures/.",
    )
    parser.add_argument(
        "--ground-truth", type=Path, default=DEFAULT_GT,
        help="GeoJSON of GT mounds (used for GT gained / lost).",
    )
    parser.add_argument(
        "--max-workers", type=int, default=4,
        help="ProcessPoolExecutor worker count.",
    )
    parser.add_argument(
        "--radius", type=float, default=DEFAULT_RADIUS_M,
        help="Default cluster radius in metres (canonical 20).",
    )
    parser.add_argument(
        "--sensitivity-radius", type=float,
        default=SENSITIVITY_RADIUS_M,
        help="Sensitivity cluster radius (gold-standard-v2 only).",
    )
    parser.add_argument(
        "--strata", nargs="*", default=None,
        help="Optional subset of stratum names to process.",
    )
    parser.add_argument(
        "--version", action="version",
        version=f"%(prog)s {__version__}",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )
    logger.info(
        "analyse_inter_pass_agreement.py v%s — %d workers",
        __version__, args.max_workers,
    )
    start = time.monotonic()

    # Filter strata if --strata was passed
    strata = (
        {k: v for k, v in CONDITION_REGISTRY.items() if k in args.strata}
        if args.strata else CONDITION_REGISTRY
    )

    # Build task list — one per (stratum, condition)
    tasks = []
    for stratum, conds in strata.items():
        for cond, cfg in conds.items():
            tasks.append((
                stratum, cond, cfg, args.ground_truth,
                args.radius, args.sensitivity_radius,
            ))
    logger.info("Submitting %d (stratum, condition) tasks", len(tasks))

    results: dict[str, dict[str, dict[str, Any]]] = {
        s: {} for s in strata
    }

    with ProcessPoolExecutor(max_workers=args.max_workers) as executor:
        futures = {
            executor.submit(_process_condition, t): (t[0], t[1])
            for t in tasks
        }
        for fut in as_completed(futures):
            stratum, condition = futures[fut]
            try:
                s, c, payload = fut.result()
                results[s][c] = payload
                if "error" in payload:
                    logger.error(
                        "  %s / %s — error: %s",
                        s, c, payload["error"],
                    )
                elif "skipped_reason" in payload:
                    logger.info(
                        "  %s / %s — skipped (%s, K=%d)",
                        s, c, payload["skipped_reason"],
                        payload["K_found"],
                    )
                else:
                    cm = payload["candidate_match"]["summary"]["kappa"]
                    bl = payload["borderline"]
                    logger.info(
                        "  %s / %s — K=%d kappa_cm_mean=%.3f "
                        "borderline=%d/%d (frag=%s)",
                        s, c, payload["K_found"], cm["mean"] or 0,
                        bl["borderline_n"], bl["consensus_n"],
                        bl["fragility_ratio"],
                    )
            except Exception as exc:
                logger.exception(
                    "  %s / %s — unhandled exception: %s",
                    stratum, condition, exc,
                )
                results[stratum][condition] = {"error": str(exc)}

    # ---------- Write outputs ----------
    out_dir = args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # JSON
    json_path = out_dir / "agreement.json"

    class _NumpyEncoder(json.JSONEncoder):
        def default(self, obj):  # noqa: D401
            """Serialise numpy / Path objects."""
            if isinstance(obj, (np.integer,)):
                return int(obj)
            if isinstance(obj, (np.floating,)):
                if np.isnan(obj):
                    return None
                return float(obj)
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, Path):
                return str(obj)
            return super().default(obj)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, cls=_NumpyEncoder)
    logger.info("JSON: %s", json_path)

    # Heatmaps
    fig_dir = out_dir / "figures"
    for stratum, conds in results.items():
        for cond, row in conds.items():
            if "skipped_reason" in row or "error" in row:
                continue
            mat = _coerce_matrix(
                row["candidate_match"]["kappa_matrix"],
            )
            pass_ids = row["candidate_match"]["pass_ids"]
            title = (
                f"{stratum} / {cond} (K={row['K_found']}, "
                f"radius={args.radius:.0f} m)"
            )
            png = fig_dir / f"{stratum}__{cond}.png"
            write_heatmap(mat, pass_ids, title, png)

    # Markdown
    md_path = out_dir / "report_autogen.md"
    render_autogen_md(results, md_path)

    elapsed = time.monotonic() - start
    logger.info("Complete in %.1fs", elapsed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
