#!/usr/bin/env python3
"""Dawid-Skene latent truth model for corrected VLM evaluation metrics.

Models student digitisers and the VLM pipeline as two noisy binary
annotators, then uses Expectation-Maximisation (EM) to jointly estimate:

    1. The **true mound label** for each spatial location (latent variable)
    2. Each annotator's **confusion matrix** (sensitivity and specificity)

This produces bias-corrected precision, recall, and F1 for the VLM
pipeline, accounting for the documented ~5 % false-negative rate in the
student ground truth (Sobotkova et al. 2023).

Reference:
    Dawid, A.P. & Skene, A.M. (1979). Maximum likelihood estimation of
    observer error-rates using the EM algorithm. *Applied Statistics*,
    28(1), 20-28.

Usage:
    python scripts/analyse_dawid_skene.py
    python scripts/analyse_dawid_skene.py --threshold 0.15 --buffer 50
    python scripts/analyse_dawid_skene.py --sensitivity-analysis
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path setup — allow imports from scripts/
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

from lib_advanced_metrics import (  # noqa: E402
    get_map_name,
    match_detections_to_references,
    scope_references_to_tiles,
)
from lib_consensus import ensure_utm_crs  # noqa: E402

logger = logging.getLogger(__name__)

# =========================================================================
# Constants and defaults
# =========================================================================

_REPO_ROOT = _SCRIPT_DIR.parent
_INPUTS = _REPO_ROOT / "inputs" / "vectors"
_STUDENT_GT_PATH = _INPUTS / "references" / "student-mounds-55maps.geojson"
_BOUNDS_PATH = _INPUTS / "bounds" / "384" / "55maps_evaluation_bounds.geojson"
_CONSENSUS_PATH = (
    _REPO_ROOT
    / "outputs"
    / "55maps-generalisation"
    / "consensus"
    / "consensus-4of5.geojson"
)
_PROBS_V1_PATH = (
    _REPO_ROOT
    / "outputs"
    / "55maps-generalisation"
    / "verified"
    / "probabilities.json"
)
_PROBS_V2_PATH = (
    _REPO_ROOT
    / "outputs"
    / "55maps-generalisation"
    / "verified-v2"
    / "probabilities.json"
)
_TARGET_CRS = "EPSG:32635"

# Prior: student error rates from Sobotkova et al. (2023) quality audit
STUDENT_SENSITIVITY_DEFAULT = 0.95   # P(student=1 | true=1)
STUDENT_SPECIFICITY_DEFAULT = 1.00   # P(student=0 | true=0)

DEFAULT_THRESHOLD = 0.15
DEFAULT_BUFFER = 50


# =========================================================================
# Step 1: Build shared item set from spatial matching
# =========================================================================


def load_detections(
    consensus_path: Path,
    probabilities_path: Path,
    threshold: float,
    target_crs: str = _TARGET_CRS,
) -> gpd.GeoDataFrame:
    """Load consensus candidates, join verifier probabilities, filter.

    Reads the consensus GeoJSON (all candidates passing the vote
    threshold) and the verifier probabilities JSON, joins them by
    candidate index, and returns only candidates whose probability
    meets or exceeds the given threshold.

    Args:
        consensus_path: Path to consensus-4of5.geojson.
        probabilities_path: Path to probabilities.json from verifier.
        threshold: Minimum mound_probability to accept a candidate.
        target_crs: Target CRS for reprojection (default EPSG:32635).

    Returns:
        GeoDataFrame with columns: source_tile, mound_probability,
        candidate_id, geometry. CRS is target_crs.
    """
    gdf = gpd.read_file(consensus_path)
    # Handle both legacy (UTM-in-4326) and spec-compliant (real 4326)
    # consensus GeoJSON files
    gdf = ensure_utm_crs(gdf, source_label=str(consensus_path))

    with open(probabilities_path, encoding="utf-8") as f:
        prob_data = json.load(f)
    results = prob_data.get("results", {})

    # Candidate IDs are 0-based sequential, matching GeoDataFrame rows
    probabilities = []
    for i in range(len(gdf)):
        key = f"candidate_{i:05d}"
        entry = results.get(key, {})
        probabilities.append(entry.get("mound_probability", 0.0))

    gdf["mound_probability"] = probabilities
    gdf["candidate_id"] = range(len(gdf))

    # Derive a single source_tile from the first element of source_tiles
    gdf["source_tile"] = gdf["source_tiles"].apply(
        lambda tiles: tiles[0] if hasattr(tiles, '__len__') and len(tiles) > 0
        else "unknown"
    )

    # Filter by probability threshold
    gdf_filtered = gdf[gdf["mound_probability"] >= threshold].copy()

    logger.info(
        "Loaded %d candidates, %d accepted at threshold %.2f",
        len(gdf), len(gdf_filtered), threshold,
    )

    return gdf_filtered[
        ["source_tile", "mound_probability", "candidate_id", "geometry"]
    ]


def build_shared_item_set(
    gdf_det: gpd.GeoDataFrame,
    gdf_ref: gpd.GeoDataFrame,
    gdf_bounds: gpd.GeoDataFrame,
    buffer_metres: int = DEFAULT_BUFFER,
) -> pd.DataFrame:
    """Build a shared item set from per-map Hungarian matching.

    Creates a DataFrame where each row is a spatial location where at
    least one annotator (student or VLM) reported a mound. Three item
    categories:

    - **matched** (student=1, vlm=1): Both annotators agree.
    - **student_only** (student=1, vlm=0): Student digitised, VLM missed.
    - **vlm_only** (student=0, vlm=1): VLM detected, no nearby student
      point — either a true mound the students missed, or a VLM FP.

    Args:
        gdf_det: GeoDataFrame of VLM detections (already filtered by
            probability threshold). Must have ``source_tile`` and
            ``mound_probability`` columns.
        gdf_ref: GeoDataFrame of student ground truth points. Must have
            ``source_map`` column.
        gdf_bounds: GeoDataFrame of evaluation tile boundaries.
        buffer_metres: Maximum distance in metres for a valid match.

    Returns:
        DataFrame with columns: item_id, student_label, vlm_label,
        vlm_probability, map_name, category, x, y.
    """
    items: list[dict] = []
    item_id = 0

    # Detect reference map column
    if "source_map" in gdf_ref.columns:
        ref_map_col = "source_map"
    elif "Map" in gdf_ref.columns:
        ref_map_col = "Map"
    else:
        raise ValueError(
            f"Reference has no 'source_map' or 'Map' column. "
            f"Columns: {list(gdf_ref.columns)}"
        )

    # Get maps from bounds
    processed_maps = {
        get_map_name(n) for n in gdf_bounds["tile_name"].unique()
    }

    for map_name in sorted(processed_maps):
        if map_name == "Unknown":
            continue

        map_bounds = gdf_bounds[
            gdf_bounds["tile_name"].str.startswith(map_name)
        ]

        ref_scope = gdf_ref[gdf_ref[ref_map_col] == map_name]
        if not ref_scope.empty:
            ref_scope = scope_references_to_tiles(ref_scope, map_bounds)

        det_scope = gdf_det[
            gdf_det["source_tile"].str.startswith(map_name)
        ]

        if det_scope.empty and ref_scope.empty:
            continue

        if det_scope.empty:
            # All student-only items for this map
            for _, row in ref_scope.iterrows():
                pt = row.geometry.centroid
                items.append({
                    "item_id": item_id,
                    "student_label": 1,
                    "vlm_label": 0,
                    "vlm_probability": 0.0,
                    "map_name": map_name,
                    "category": "student_only",
                    "x": pt.x,
                    "y": pt.y,
                })
                item_id += 1
            continue

        if ref_scope.empty:
            # All VLM-only items for this map
            for _, row in det_scope.iterrows():
                pt = row.geometry.centroid
                items.append({
                    "item_id": item_id,
                    "student_label": 0,
                    "vlm_label": 1,
                    "vlm_probability": row.get("mound_probability", 1.0),
                    "map_name": map_name,
                    "category": "vlm_only",
                    "x": pt.x,
                    "y": pt.y,
                })
                item_id += 1
            continue

        # Per-map Hungarian matching
        det_geoms = list(det_scope.geometry)
        ref_geoms = list(ref_scope.geometry)

        matched_det, matched_ref, unmatched_det, unmatched_ref = (
            match_detections_to_references(
                det_geoms, ref_geoms, buffer_metres
            )
        )

        # Matched pairs — use reference location as canonical
        for d_idx, r_idx in zip(matched_det, matched_ref):
            det_row = det_scope.iloc[d_idx]
            ref_pt = ref_scope.iloc[r_idx].geometry.centroid
            items.append({
                "item_id": item_id,
                "student_label": 1,
                "vlm_label": 1,
                "vlm_probability": det_row.get(
                    "mound_probability", 1.0
                ),
                "map_name": map_name,
                "category": "matched",
                "x": ref_pt.x,
                "y": ref_pt.y,
            })
            item_id += 1

        # Student-only (unmatched references = VLM false negatives)
        for r_idx in unmatched_ref:
            ref_pt = ref_scope.iloc[r_idx].geometry.centroid
            items.append({
                "item_id": item_id,
                "student_label": 1,
                "vlm_label": 0,
                "vlm_probability": 0.0,
                "map_name": map_name,
                "category": "student_only",
                "x": ref_pt.x,
                "y": ref_pt.y,
            })
            item_id += 1

        # VLM-only (unmatched detections = VLM false positives or
        # real mounds the students missed)
        for d_idx in unmatched_det:
            det_row = det_scope.iloc[d_idx]
            det_pt = det_row.geometry.centroid
            items.append({
                "item_id": item_id,
                "student_label": 0,
                "vlm_label": 1,
                "vlm_probability": det_row.get(
                    "mound_probability", 1.0
                ),
                "map_name": map_name,
                "category": "vlm_only",
                "x": det_pt.x,
                "y": det_pt.y,
            })
            item_id += 1

    df = pd.DataFrame(items)
    logger.info(
        "Shared item set: %d items "
        "(matched=%d, student_only=%d, vlm_only=%d)",
        len(df),
        (df["category"] == "matched").sum() if len(df) > 0 else 0,
        (df["category"] == "student_only").sum() if len(df) > 0 else 0,
        (df["category"] == "vlm_only").sum() if len(df) > 0 else 0,
    )
    return df


# =========================================================================
# Step 2: Dawid-Skene EM algorithm
# =========================================================================


def dawid_skene_em(
    student_labels: np.ndarray,
    vlm_labels: np.ndarray,
    student_sens_init: float = STUDENT_SENSITIVITY_DEFAULT,
    student_spec_init: float = STUDENT_SPECIFICITY_DEFAULT,
    vlm_sens_init: float = 0.73,
    vlm_spec_init: float = 0.86,
    prevalence_init: float | None = None,
    max_iter: int = 100,
    tol: float = 1e-6,
    fix_student_spec: bool = True,
    fix_student_sens: bool = True,
) -> dict:
    """Run Dawid-Skene EM for two annotators with binary labels.

    Estimates the latent true label for each item by iteratively
    refining annotator confusion matrices and item posteriors.

    With ``fix_student_spec=True`` (default), student specificity is
    held at its initial value — justified by the documented ~0 % student
    false-positive rate (Sobotkova et al. 2023).

    With ``fix_student_sens=True`` (default), student sensitivity is
    held at its initial value. This is necessary for identifiability
    with only 2 annotators: without this constraint, the EM converges
    to s_sens=1.0 (attributing all VLM-only items to VLM FPs rather
    than student FNs), regardless of the prior. Fixing the sensitivity
    at the externally validated value (0.95 from QA) forces the model
    to account for the documented student omission rate.

    Args:
        student_labels: 1-D array of binary student labels (0 or 1).
        vlm_labels: 1-D array of binary VLM labels (0 or 1).
        student_sens_init: Initial student sensitivity P(s=1|T=1).
        student_spec_init: Initial student specificity P(s=0|T=0).
        vlm_sens_init: Initial VLM sensitivity P(v=1|T=1).
        vlm_spec_init: Initial VLM specificity P(v=0|T=0).
        prevalence_init: Initial prevalence P(T=1). Defaults to the
            fraction of items where student_label=1.
        max_iter: Maximum number of EM iterations.
        tol: Convergence threshold on max absolute posterior change.
        fix_student_spec: If True, hold student specificity fixed at
            ``student_spec_init`` throughout EM.
        fix_student_sens: If True, hold student sensitivity fixed at
            ``student_sens_init`` throughout EM. Required for
            identifiability with 2 annotators.

    Returns:
        Dict containing:
            - posteriors: np.ndarray of P(true=1) per item
            - prevalence: estimated base rate of true mounds
            - student_sensitivity, student_specificity: final estimates
            - vlm_sensitivity, vlm_specificity: final estimates
            - n_iterations: number of EM iterations run
            - converged: whether the algorithm converged within tol
    """
    n = len(student_labels)
    if n != len(vlm_labels):
        raise ValueError(
            f"Label arrays must have equal length: "
            f"{n} vs {len(vlm_labels)}"
        )
    if n == 0:
        raise ValueError("Empty label arrays")

    s = np.asarray(student_labels, dtype=np.float64)
    v = np.asarray(vlm_labels, dtype=np.float64)

    # Initialise confusion matrices
    # cm[class, observation] where class ∈ {0=neg, 1=pos}
    #   cm[0, 0] = specificity    P(ann=0 | T=0)
    #   cm[0, 1] = 1-specificity  P(ann=1 | T=0)  (false positive rate)
    #   cm[1, 0] = 1-sensitivity  P(ann=0 | T=1)  (false negative rate)
    #   cm[1, 1] = sensitivity    P(ann=1 | T=1)
    s_sens = student_sens_init
    s_spec = student_spec_init
    v_sens = vlm_sens_init
    v_spec = vlm_spec_init

    # Prevalence: fraction of items that are truly positive
    pi = prevalence_init if prevalence_init is not None else np.mean(s)

    posteriors = np.full(n, 0.5)
    max_change = np.inf
    n_iter = 0

    for iteration in range(max_iter):
        prev_posteriors = posteriors.copy()

        # ---------------------------------------------------------------
        # E-step: compute P(T=1 | s_i, v_i) for each item (vectorised)
        # ---------------------------------------------------------------
        # Log-likelihoods under T=1 and T=0
        eps = 1e-300  # Prevent log(0)

        # P(s_i | T=1): s_i=1 → sensitivity, s_i=0 → 1-sensitivity
        log_s_given_pos = s * np.log(s_sens + eps) + (1 - s) * np.log(
            1 - s_sens + eps
        )
        log_s_given_neg = s * np.log(1 - s_spec + eps) + (1 - s) * np.log(
            s_spec + eps
        )

        # P(v_i | T=1): v_i=1 → sensitivity, v_i=0 → 1-sensitivity
        log_v_given_pos = v * np.log(v_sens + eps) + (1 - v) * np.log(
            1 - v_sens + eps
        )
        log_v_given_neg = v * np.log(1 - v_spec + eps) + (1 - v) * np.log(
            v_spec + eps
        )

        log_joint_pos = np.log(pi + eps) + log_s_given_pos + log_v_given_pos
        log_joint_neg = (
            np.log(1 - pi + eps) + log_s_given_neg + log_v_given_neg
        )

        # Log-sum-exp normalisation
        log_max = np.maximum(log_joint_pos, log_joint_neg)
        posteriors = np.exp(log_joint_pos - log_max) / (
            np.exp(log_joint_pos - log_max)
            + np.exp(log_joint_neg - log_max)
        )

        # ---------------------------------------------------------------
        # M-step: re-estimate parameters from soft assignments
        # ---------------------------------------------------------------
        w_pos = posteriors       # Soft weight for T=1
        w_neg = 1.0 - posteriors  # Soft weight for T=0

        sum_pos = np.sum(w_pos) + eps
        sum_neg = np.sum(w_neg) + eps

        pi = np.sum(w_pos) / n

        # Student confusion matrix
        if not fix_student_sens:
            s_sens = np.sum(w_pos * s) / sum_pos
        if not fix_student_spec:
            s_spec = np.sum(w_neg * (1 - s)) / sum_neg

        # VLM confusion matrix
        v_sens = np.sum(w_pos * v) / sum_pos
        v_spec = np.sum(w_neg * (1 - v)) / sum_neg

        # Convergence check
        max_change = float(np.max(np.abs(posteriors - prev_posteriors)))
        n_iter = iteration + 1

        if max_change < tol:
            logger.info(
                "D-S converged after %d iterations (max Δ=%.2e)",
                n_iter, max_change,
            )
            break
    else:
        logger.warning(
            "D-S did NOT converge after %d iterations (max Δ=%.2e)",
            max_iter, max_change,
        )

    return {
        "posteriors": posteriors,
        "prevalence": float(pi),
        "student_sensitivity": float(s_sens),
        "student_specificity": float(s_spec),
        "vlm_sensitivity": float(v_sens),
        "vlm_specificity": float(v_spec),
        "n_iterations": n_iter,
        "converged": max_change < tol,
    }


# =========================================================================
# Step 3: Compute corrected metrics
# =========================================================================


def compute_corrected_metrics(
    item_set: pd.DataFrame,
    posteriors: np.ndarray,
) -> dict:
    """Compute corrected P, R, F1 using D-S posteriors as latent truth.

    Uses **expected counts** (soft assignment) rather than hard
    thresholding. This is necessary because with only 2 annotators,
    D-S assigns the same posterior to all VLM-only items — hard
    thresholding at 0.5 either reclassifies all or none, losing the
    aggregate correction. Expected counts correctly capture the
    fractional reclassification.

    Args:
        item_set: DataFrame from ``build_shared_item_set`` with
            ``vlm_label`` column.
        posteriors: Array of P(true=1) per item from D-S EM.

    Returns:
        Dict with corrected precision, recall, F1, plus expected
        reclassification counts and per-category breakdowns.
    """
    vlm = item_set["vlm_label"].values.astype(float)
    cats = item_set["category"].values

    # Expected counts using soft assignments
    # TP: VLM positive AND truly positive (expected)
    tp = float(np.sum(vlm * posteriors))
    # FP: VLM positive AND truly negative (expected)
    fp = float(np.sum(vlm * (1.0 - posteriors)))
    # FN: VLM negative AND truly positive (expected)
    fn = float(np.sum((1.0 - vlm) * posteriors))

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    # Per-category breakdown
    vlm_only_mask = cats == "vlm_only"
    expected_reclassified = float(np.sum(posteriors[vlm_only_mask]))
    total_vlm_only = int(np.sum(vlm_only_mask))

    # Also compute hard-threshold version for comparison
    latent_truth_hard = (posteriors >= 0.5).astype(int)
    hard_reclassified = int(np.sum(
        vlm_only_mask & (latent_truth_hard == 1)
    ))

    # Uniform posterior for VLM-only items (all get same value)
    vlm_only_posterior = (
        float(posteriors[vlm_only_mask][0])
        if total_vlm_only > 0 else 0.0
    )

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp_expected": round(tp, 1),
        "fp_expected": round(fp, 1),
        "fn_expected": round(fn, 1),
        "total_latent_positives_expected": round(
            float(np.sum(posteriors)), 1
        ),
        "expected_reclassified": round(expected_reclassified, 1),
        "hard_threshold_reclassified": hard_reclassified,
        "vlm_only_posterior": round(vlm_only_posterior, 4),
        "total_vlm_only": total_vlm_only,
    }


def compute_simple_correction(
    item_set: pd.DataFrame,
    student_fn_rate: float = 0.05,
) -> dict:
    """Compute the simple multiplicative FN-rate correction.

    Assumes a uniform false-negative rate across all student-labelled
    mounds, inflates the true mound count accordingly, and reclassifies
    a proportional number of VLM-only detections as true positives.

    Args:
        item_set: DataFrame from ``build_shared_item_set``.
        student_fn_rate: Assumed student false-negative rate.

    Returns:
        Dict with corrected precision, recall, F1.
    """
    n_student_pos = int(
        (item_set["student_label"] == 1).sum()
    )
    n_vlm_pos = int((item_set["vlm_label"] == 1).sum())
    n_matched = int((item_set["category"] == "matched").sum())
    n_vlm_only = int((item_set["category"] == "vlm_only").sum())

    # Estimated true mound count: observed / sensitivity
    student_sens = 1.0 - student_fn_rate
    estimated_true_mounds = n_student_pos / student_sens

    # Estimated student FNs that the VLM also detected
    student_fns = estimated_true_mounds - n_student_pos
    # VLM sensitivity estimated from confirmed positives
    vlm_sens = n_matched / n_student_pos if n_student_pos > 0 else 0.0
    reclassified = min(
        int(round(student_fns * vlm_sens)),
        n_vlm_only,
    )

    tp_corrected = n_matched + reclassified
    fp_corrected = n_vlm_pos - tp_corrected
    fn_corrected = int(round(estimated_true_mounds)) - tp_corrected

    precision = (
        tp_corrected / (tp_corrected + fp_corrected)
        if (tp_corrected + fp_corrected) > 0
        else 0.0
    )
    recall = (
        tp_corrected / (tp_corrected + fn_corrected)
        if (tp_corrected + fn_corrected) > 0
        else 0.0
    )
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "estimated_true_mounds": int(round(estimated_true_mounds)),
        "reclassified_fp_to_tp": reclassified,
        "vlm_sensitivity_from_confirmed": round(vlm_sens, 4),
    }


# =========================================================================
# Step 4: Sensitivity analysis
# =========================================================================


def sensitivity_analysis(
    item_set: pd.DataFrame,
    fn_rates: list[float] | None = None,
    buffers: list[int] | None = None,
    gdf_det: gpd.GeoDataFrame | None = None,
    gdf_ref: gpd.GeoDataFrame | None = None,
    gdf_bounds: gpd.GeoDataFrame | None = None,
) -> list[dict]:
    """Vary student FN rate and matching tolerance; report D-S results.

    When ``buffers`` is provided along with the raw GeoDataFrames, the
    shared item set is rebuilt at each buffer distance. Otherwise, only
    the FN-rate prior is varied on the existing item set.

    Args:
        item_set: DataFrame from ``build_shared_item_set`` (used when
            only varying FN rate).
        fn_rates: List of student FN rates to test (default 0.01–0.10).
        buffers: Optional list of buffer distances in metres.
        gdf_det: Detection GeoDataFrame (needed if buffers is not None).
        gdf_ref: Reference GeoDataFrame (needed if buffers is not None).
        gdf_bounds: Bounds GeoDataFrame (needed if buffers is not None).

    Returns:
        List of result dicts, one per (fn_rate, buffer) combination.
    """
    if fn_rates is None:
        fn_rates = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08,
                     0.09, 0.10]

    if buffers is None:
        buffers = [DEFAULT_BUFFER]

    results = []

    for buffer_m in buffers:
        # Rebuild item set at this buffer if needed
        if buffer_m != DEFAULT_BUFFER and gdf_det is not None:
            current_items = build_shared_item_set(
                gdf_det, gdf_ref, gdf_bounds, buffer_metres=buffer_m,
            )
        else:
            current_items = item_set

        for fn_rate in fn_rates:
            student_sens = 1.0 - fn_rate

            ds_result = dawid_skene_em(
                current_items["student_label"].values,
                current_items["vlm_label"].values,
                student_sens_init=student_sens,
                student_spec_init=STUDENT_SPECIFICITY_DEFAULT,
            )

            corrected = compute_corrected_metrics(
                current_items, ds_result["posteriors"],
            )

            simple = compute_simple_correction(
                current_items, student_fn_rate=fn_rate,
            )

            results.append({
                "buffer_metres": buffer_m,
                "student_fn_rate_prior": fn_rate,
                "ds_f1": corrected["f1"],
                "ds_precision": corrected["precision"],
                "ds_recall": corrected["recall"],
                "ds_reclassified": corrected["expected_reclassified"],
                "ds_prevalence": round(ds_result["prevalence"], 4),
                "ds_student_sensitivity": round(
                    ds_result["student_sensitivity"], 4
                ),
                "ds_vlm_sensitivity": round(
                    ds_result["vlm_sensitivity"], 4
                ),
                "ds_vlm_specificity": round(
                    ds_result["vlm_specificity"], 4
                ),
                "ds_converged": ds_result["converged"],
                "ds_iterations": ds_result["n_iterations"],
                "simple_f1": simple["f1"],
                "simple_precision": simple["precision"],
                "simple_recall": simple["recall"],
                "n_items": len(current_items),
            })

    return results


# =========================================================================
# Output formatting
# =========================================================================


def format_results_markdown(
    measured: dict,
    simple: dict,
    ds_corrected: dict,
    ds_result: dict,
    item_counts: dict,
    sensitivity_results: list[dict] | None = None,
) -> str:
    """Format all results as a Markdown report.

    Args:
        measured: Dict with measured (uncorrected) P, R, F1.
        simple: Dict from ``compute_simple_correction``.
        ds_corrected: Dict from ``compute_corrected_metrics``.
        ds_result: Dict from ``dawid_skene_em`` (annotator estimates).
        item_counts: Dict with category counts from the shared item set.
        sensitivity_results: Optional list from ``sensitivity_analysis``.

    Returns:
        Markdown string.
    """
    lines = [
        "# Dawid-Skene Latent Truth Model — Results",
        "",
        "## Summary",
        "",
        "Joint model of student digitisers and VLM pipeline as noisy",
        "annotators, estimating latent true mound locations via EM.",
        "",
        "## Shared Item Set",
        "",
        "| Category | Count |",
        "|----------|-------|",
        f"| Matched (student=1, vlm=1) | {item_counts['matched']:,} |",
        f"| Student-only (student=1, vlm=0) "
        f"| {item_counts['student_only']:,} |",
        f"| VLM-only (student=0, vlm=1) "
        f"| {item_counts['vlm_only']:,} |",
        f"| **Total** | **{item_counts['total']:,}** |",
        "",
        "## Corrected Metrics Comparison",
        "",
        "| Method | F1 | Precision | Recall | Notes |",
        "|--------|----|-----------|--------|-------|",
        f"| Measured (vs student GT) | {measured['f1']} "
        f"| {measured['precision']} | {measured['recall']} "
        f"| Baseline |",
        f"| Simple correction (5% FN) | {simple['f1']} "
        f"| {simple['precision']} | {simple['recall']} "
        f"| Assumes uniform FN |",
        f"| **Dawid-Skene posterior** | **{ds_corrected['f1']}** "
        f"| **{ds_corrected['precision']}** "
        f"| **{ds_corrected['recall']}** "
        f"| Model-based |",
        "",
        "## D-S Model Details",
        "",
        f"- **Converged**: {ds_result['converged']} "
        f"({ds_result['n_iterations']} iterations)",
        f"- **Estimated prevalence**: {ds_result['prevalence']:.4f} "
        f"(fraction of items that are true mounds)",
        "",
        "### Estimated Annotator Confusion Matrices",
        "",
        "**Student digitisers:**",
        "",
        f"- Sensitivity: {ds_result['student_sensitivity']:.4f} "
        f"(prior: {STUDENT_SENSITIVITY_DEFAULT})",
        f"- Specificity: {ds_result['student_specificity']:.4f} "
        f"(prior: {STUDENT_SPECIFICITY_DEFAULT}, fixed)",
        "",
        "**VLM pipeline:**",
        "",
        f"- Sensitivity: {ds_result['vlm_sensitivity']:.4f}",
        f"- Specificity: {ds_result['vlm_specificity']:.4f}",
        "",
        "### Reclassification of VLM-Only Items",
        "",
        f"- Total VLM-only items: {ds_corrected['total_vlm_only']}",
        f"- Per-item posterior P(true=1): "
        f"{ds_corrected['vlm_only_posterior']}",
        f"- Expected reclassified (soft): "
        f"{ds_corrected['expected_reclassified']}",
        f"- Hard-threshold (≥0.5) reclassified: "
        f"{ds_corrected['hard_threshold_reclassified']}",
        f"- Total latent positives (expected): "
        f"{ds_corrected['total_latent_positives_expected']}",
        "",
        "**Note on 2-annotator identifiability:** With only two binary",
        "annotators, D-S assigns the same posterior to all VLM-only",
        "items because they share identical labels (s=0, v=1). The",
        "model correctly estimates the aggregate fraction of real mounds",
        "but cannot discriminate individual items. Hard thresholding at",
        "0.5 reclassifies none; expected counts capture the aggregate.",
        "The verifier probability provides per-item discrimination for",
        "human review (see item-posteriors.csv).",
        "",
    ]

    if sensitivity_results:
        lines.extend([
            "## Sensitivity Analysis",
            "",
            "### Varying Student FN Rate Prior and Buffer Distance",
            "",
            "| Buffer | FN Rate | D-S F1 | D-S P | D-S R "
            "| Simple F1 | Reclassified |",
            "|--------|---------|--------|-------|-------"
            "|-----------|--------------|",
        ])
        for r in sensitivity_results:
            lines.append(
                f"| {r['buffer_metres']}m "
                f"| {r['student_fn_rate_prior']:.2f} "
                f"| {r['ds_f1']} "
                f"| {r['ds_precision']} "
                f"| {r['ds_recall']} "
                f"| {r['simple_f1']} "
                f"| {r['ds_reclassified']} |"
            )
        lines.append("")

    lines.extend([
        "## References",
        "",
        "- Dawid, A.P. & Skene, A.M. (1979). Maximum likelihood "
        "estimation of observer error-rates using the EM algorithm. "
        "*Applied Statistics*, 28(1), 20-28.",
        "- Sobotkova, A. et al. (2023). Creating large, high-quality "
        "geospatial datasets from historical maps using novice "
        "volunteers.",
        "",
    ])

    return "\n".join(lines)


# =========================================================================
# Main
# =========================================================================


def main(argv: list[str] | None = None) -> None:
    """Run the full Dawid-Skene analysis pipeline."""
    parser = argparse.ArgumentParser(
        description="Dawid-Skene latent truth model for corrected "
                    "VLM evaluation metrics.",
    )
    parser.add_argument(
        "--threshold", type=float, default=DEFAULT_THRESHOLD,
        help="Verifier probability threshold (default: %(default)s)",
    )
    parser.add_argument(
        "--buffer", type=int, default=DEFAULT_BUFFER,
        help="Matching tolerance in metres (default: %(default)s)",
    )
    parser.add_argument(
        "--verifier", choices=["v1", "v2"], default="v1",
        help="Which verifier probabilities to use (default: v1)",
    )
    parser.add_argument(
        "--sensitivity-analysis", action="store_true",
        help="Run sensitivity analysis over FN rates and buffers",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=_REPO_ROOT / "results" / "dawid-skene",
        help="Output directory (default: results/dawid-skene/)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # ---------------------------------------------------------------
    # Load data
    # ---------------------------------------------------------------
    probs_path = _PROBS_V1_PATH if args.verifier == "v1" else _PROBS_V2_PATH
    logger.info("Loading data (verifier=%s, threshold=%.2f, buffer=%dm)",
                args.verifier, args.threshold, args.buffer)

    gdf_det = load_detections(
        _CONSENSUS_PATH, probs_path, args.threshold,
    )
    gdf_ref = gpd.read_file(_STUDENT_GT_PATH)
    if gdf_ref.crs != _TARGET_CRS:
        gdf_ref = gdf_ref.to_crs(_TARGET_CRS)
    gdf_bounds = gpd.read_file(_BOUNDS_PATH)
    if gdf_bounds.crs != _TARGET_CRS:
        gdf_bounds = gdf_bounds.to_crs(_TARGET_CRS)

    # ---------------------------------------------------------------
    # Step 1: Build shared item set
    # ---------------------------------------------------------------
    logger.info("Building shared item set...")
    item_set = build_shared_item_set(
        gdf_det, gdf_ref, gdf_bounds, buffer_metres=args.buffer,
    )

    # ---------------------------------------------------------------
    # Step 2: Run D-S EM
    # ---------------------------------------------------------------
    logger.info("Running Dawid-Skene EM...")
    ds_result = dawid_skene_em(
        item_set["student_label"].values,
        item_set["vlm_label"].values,
    )

    # ---------------------------------------------------------------
    # Step 3: Compute corrected metrics
    # ---------------------------------------------------------------
    ds_corrected = compute_corrected_metrics(
        item_set, ds_result["posteriors"],
    )

    # Measured (uncorrected) metrics — derived from the item set
    n_matched = int((item_set["category"] == "matched").sum())
    n_vlm_only = int((item_set["category"] == "vlm_only").sum())
    n_student_only = int((item_set["category"] == "student_only").sum())
    measured_tp = n_matched
    measured_fp = n_vlm_only
    measured_fn = n_student_only
    measured_p = (
        measured_tp / (measured_tp + measured_fp)
        if (measured_tp + measured_fp) > 0 else 0.0
    )
    measured_r = (
        measured_tp / (measured_tp + measured_fn)
        if (measured_tp + measured_fn) > 0 else 0.0
    )
    measured_f1 = (
        2 * measured_p * measured_r / (measured_p + measured_r)
        if (measured_p + measured_r) > 0 else 0.0
    )
    measured = {
        "precision": round(measured_p, 4),
        "recall": round(measured_r, 4),
        "f1": round(measured_f1, 4),
    }

    simple = compute_simple_correction(item_set)

    item_counts = {
        "matched": n_matched,
        "student_only": n_student_only,
        "vlm_only": n_vlm_only,
        "total": len(item_set),
    }

    # ---------------------------------------------------------------
    # Step 4: Sensitivity analysis (optional)
    # ---------------------------------------------------------------
    sens_results = None
    if args.sensitivity_analysis:
        logger.info("Running sensitivity analysis...")
        buffers = [20, 30, 40, 50] if args.buffer == 50 else [args.buffer]
        sens_results = sensitivity_analysis(
            item_set,
            gdf_det=gdf_det,
            gdf_ref=gdf_ref,
            gdf_bounds=gdf_bounds,
            buffers=buffers,
        )

    # ---------------------------------------------------------------
    # Write outputs
    # ---------------------------------------------------------------
    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Markdown report
    md = format_results_markdown(
        measured, simple, ds_corrected, ds_result,
        item_counts, sens_results,
    )
    md_path = args.output_dir / "dawid-skene-results.md"
    md_path.write_text(md, encoding="utf-8")
    logger.info("Wrote Markdown report: %s", md_path)

    # JSON results (machine-readable)
    json_out = {
        "parameters": {
            "threshold": args.threshold,
            "buffer_metres": args.buffer,
            "verifier": args.verifier,
            "student_fn_rate_prior": 1 - STUDENT_SENSITIVITY_DEFAULT,
        },
        "item_counts": item_counts,
        "measured": measured,
        "simple_correction": simple,
        "dawid_skene": {
            "corrected_metrics": ds_corrected,
            "model_estimates": {
                "prevalence": ds_result["prevalence"],
                "student_sensitivity": ds_result["student_sensitivity"],
                "student_specificity": ds_result["student_specificity"],
                "vlm_sensitivity": ds_result["vlm_sensitivity"],
                "vlm_specificity": ds_result["vlm_specificity"],
                "n_iterations": ds_result["n_iterations"],
                "converged": ds_result["converged"],
            },
        },
    }
    if sens_results:
        json_out["sensitivity_analysis"] = sens_results

    json_path = args.output_dir / "dawid-skene-results.json"
    json_path.write_text(
        json.dumps(json_out, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    logger.info("Wrote JSON results: %s", json_path)

    # Per-item posteriors (for downstream use in review app)
    posteriors_df = item_set.copy()
    posteriors_df["posterior_p_true"] = ds_result["posteriors"]
    posteriors_df["latent_truth"] = (
        ds_result["posteriors"] >= 0.5
    ).astype(int)
    posteriors_csv = args.output_dir / "item-posteriors.csv"
    posteriors_df.to_csv(posteriors_csv, index=False)
    logger.info("Wrote per-item posteriors: %s", posteriors_csv)

    # ---------------------------------------------------------------
    # Console summary
    # ---------------------------------------------------------------
    print("\n" + "=" * 60)
    print("Dawid-Skene Latent Truth Model — Summary")
    print("=" * 60)
    print(f"\nShared item set: {len(item_set):,} items")
    print(f"  Matched:      {n_matched:,}")
    print(f"  Student-only: {n_student_only:,}")
    print(f"  VLM-only:     {n_vlm_only:,}")
    print(f"\nD-S converged: {ds_result['converged']} "
          f"({ds_result['n_iterations']} iterations)")
    print(f"\n{'Method':<30} {'F1':>6} {'P':>6} {'R':>6}")
    print("-" * 52)
    print(f"{'Measured (vs student GT)':<30} "
          f"{measured['f1']:>6} {measured['precision']:>6} "
          f"{measured['recall']:>6}")
    print(f"{'Simple correction (5% FN)':<30} "
          f"{simple['f1']:>6} {simple['precision']:>6} "
          f"{simple['recall']:>6}")
    print(f"{'Dawid-Skene posterior':<30} "
          f"{ds_corrected['f1']:>6} {ds_corrected['precision']:>6} "
          f"{ds_corrected['recall']:>6}")
    print(f"\nVLM-only items: {ds_corrected['total_vlm_only']} "
          f"(posterior={ds_corrected['vlm_only_posterior']:.4f})")
    print(f"  Expected reclassified (soft): "
          f"{ds_corrected['expected_reclassified']:.0f}")
    print(f"  Hard-threshold (≥0.5): "
          f"{ds_corrected['hard_threshold_reclassified']}")
    print(f"Estimated student sensitivity: "
          f"{ds_result['student_sensitivity']:.4f} "
          f"(prior: {STUDENT_SENSITIVITY_DEFAULT})")
    print(f"Results written to: {args.output_dir}")
    print()


if __name__ == "__main__":
    main()
