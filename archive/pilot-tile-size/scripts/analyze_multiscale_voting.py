#!/usr/bin/env python3
"""
Multi-Scale Voting Analysis for Tile Size Pilot
================================================

Description:
    Evaluates cross-scale voting strategies using existing pilot detection data.
    Tests 10 aggregation strategies with parameter sweeps to determine if
    multi-scale approaches outperform single-scale voting.

    No new API calls required - pure post-hoc analysis.

Usage:
    python scripts/analyze_multiscale_voting.py

Output:
    outputs/pilot/multiscale_analysis.json - Structured results with CIs
    outputs/pilot/multiscale_summary.md - Human-readable summary
    outputs/pilot/multiscale_full_sweep.csv - All configurations in flat format

Author: Shawn Ross, Adela Sobotkova
Licence: Apache 2.0
"""

import sys
import json
import csv
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set, Optional
from collections import defaultdict
from datetime import datetime, timezone
import numpy as np

# Setup Project Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import shared functions from existing analysis script
from scripts.analyze_pilot_results import (
    load_detections,
    load_ground_truth,
    load_reference_ground_truth,
    normalised_to_pixel,
    box_centre,
    get_tile_to_region_offset,
    pixel_distance,
    metres_to_pixels,
    compute_metrics,
    bootstrap_metrics,
    match_detections_to_ground_truth,
    deduplicate_detections,
    SPATIAL_TOLERANCE_M,
    BOOTSTRAP_ITERATIONS,
    VALID_REGION_MARGIN,
    REFERENCE_TILE_SIZE,
    NUM_PASSES,
    OUTPUT_DIR,
)

# Script version
__version__ = "1.0.0"

# Scale configuration
SCALES = ['small', 'medium', 'large']
SCALE_TO_SIZE = {'small': 256, 'medium': 512, 'large': 1024}
SIZE_TO_SCALE = {256: 'small', 512: 'medium', 1024: 'large'}

# Voting thresholds
WITHIN_THRESHOLDS = [1, 2, 3, 4, 5]  # Out of 5 passes
CROSS_THRESHOLDS = [1, 2, 3]  # Number of scales


# =============================================================================
# DATA LOADING AND NORMALISATION
# =============================================================================

def load_all_detections_normalised() -> Dict[str, Dict[str, Dict[int, List[Dict]]]]:
    """
    Load detections from all scales, convert to 1024px reference coordinates.

    Returns:
        {scale: {region_id: {pass_id: [detection_dicts]}}}

    Each detection dict contains:
        - x, y: coordinates in 1024px reference space
        - scale: source scale name
        - tile_id: source tile identifier
        - pass_id: which pass (1-5)
    """
    all_detections = {}

    for scale in SCALES:
        tile_size = SCALE_TO_SIZE[scale]
        detections_data = load_detections(tile_size)
        ground_truth_data = load_ground_truth(tile_size)

        scale_detections = defaultdict(lambda: defaultdict(list))

        for tile_name, tile_info in detections_data.get('tiles', {}).items():
            # Get tile metadata
            gt_key = tile_name + '.png'
            if gt_key not in ground_truth_data:
                continue

            region_id = ground_truth_data[gt_key]['region_id']
            offset_x, offset_y = get_tile_to_region_offset(
                tile_name, tile_size, ground_truth_data
            )

            # Process each pass
            for pass_str, pass_info in tile_info.get('passes', {}).items():
                pass_id = int(pass_str)

                for det in pass_info.get('detections', []):
                    if 'box_2d' not in det:
                        continue

                    # Convert to tile pixel coordinates
                    det_x, det_y = box_centre(det['box_2d'], tile_size)

                    # Convert to 1024px reference coordinates
                    ref_x = det_x + offset_x
                    ref_y = det_y + offset_y

                    # Only include detections in the valid region
                    if (VALID_REGION_MARGIN <= ref_x < (REFERENCE_TILE_SIZE - VALID_REGION_MARGIN) and
                            VALID_REGION_MARGIN <= ref_y < (REFERENCE_TILE_SIZE - VALID_REGION_MARGIN)):
                        scale_detections[region_id][pass_id].append({
                            'x': ref_x,
                            'y': ref_y,
                            'scale': scale,
                            'tile_id': tile_name,
                            'pass_id': pass_id
                        })

        all_detections[scale] = dict(scale_detections)

    return all_detections


def deduplicate_within_pass(
    detections: List[Dict],
    tolerance_px: float
) -> List[Dict]:
    """
    Cluster detections from overlapping tiles within a single pass.

    Returns one centroid per cluster, preserving metadata from first detection.
    """
    if not detections:
        return []

    deduped = []
    used = set()

    for i, det1 in enumerate(detections):
        if i in used:
            continue

        cluster = [det1]
        used.add(i)

        for j, det2 in enumerate(detections):
            if j in used:
                continue
            dist = pixel_distance((det1['x'], det1['y']), (det2['x'], det2['y']))
            if dist <= tolerance_px:
                cluster.append(det2)
                used.add(j)

        # Use cluster centroid
        avg_x = np.mean([d['x'] for d in cluster])
        avg_y = np.mean([d['y'] for d in cluster])
        deduped.append({
            'x': avg_x,
            'y': avg_y,
            'scale': cluster[0]['scale'],
            'pass_id': cluster[0]['pass_id']
        })

    return deduped


def prepare_deduplicated_detections(
    all_detections: Dict[str, Dict[str, Dict[int, List[Dict]]]]
) -> Dict[str, Dict[str, Dict[int, List[Dict]]]]:
    """
    Apply within-pass deduplication to all detections.

    Returns same structure but with overlap duplicates merged.
    """
    tolerance_px = metres_to_pixels(SPATIAL_TOLERANCE_M, REFERENCE_TILE_SIZE)
    deduped = {}

    for scale in SCALES:
        deduped[scale] = {}
        for region_id, passes in all_detections.get(scale, {}).items():
            deduped[scale][region_id] = {}
            for pass_id, dets in passes.items():
                deduped[scale][region_id][pass_id] = deduplicate_within_pass(
                    dets, tolerance_px
                )

    return deduped


# =============================================================================
# SPATIAL CLUSTERING UTILITIES
# =============================================================================

def spatial_cluster(
    detections: List[Dict],
    tolerance_px: float
) -> List[List[Dict]]:
    """
    Cluster detections within tolerance distance.

    Returns list of clusters, each cluster is a list of detection dicts.
    """
    if not detections:
        return []

    clusters = []
    used = set()

    for i, det1 in enumerate(detections):
        if i in used:
            continue

        cluster = [det1]
        used.add(i)

        for j, det2 in enumerate(detections):
            if j in used:
                continue
            dist = pixel_distance((det1['x'], det1['y']), (det2['x'], det2['y']))
            if dist <= tolerance_px:
                cluster.append(det2)
                used.add(j)

        clusters.append(cluster)

    return clusters


def cluster_centroid(cluster: List[Dict]) -> Tuple[float, float]:
    """Get centroid of a cluster."""
    if not cluster:
        return (0.0, 0.0)
    avg_x = np.mean([d['x'] for d in cluster])
    avg_y = np.mean([d['y'] for d in cluster])
    return (avg_x, avg_y)


def count_unique_passes(cluster: List[Dict]) -> int:
    """Count unique pass IDs in a cluster."""
    return len(set(d['pass_id'] for d in cluster))


def count_unique_scales(cluster: List[Dict]) -> Set[str]:
    """Get unique scales in a cluster."""
    return set(d['scale'] for d in cluster)


# =============================================================================
# SINGLE-SCALE VOTING (BASELINE)
# =============================================================================

def single_scale_voting(
    detections_by_pass: Dict[int, List[Dict]],
    threshold: int,
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Apply within-scale voting to get final predictions.

    Args:
        detections_by_pass: {pass_id: [detection_dicts]}
        threshold: minimum passes required (1-5)
        tolerance_px: clustering tolerance

    Returns:
        List of (x, y) centroid predictions
    """
    # Pool all detections
    all_dets = []
    for pass_id, dets in detections_by_pass.items():
        all_dets.extend(dets)

    if not all_dets:
        return []

    # Cluster spatially
    clusters = spatial_cluster(all_dets, tolerance_px)

    # Filter by vote threshold
    voted = []
    for cluster in clusters:
        if count_unique_passes(cluster) >= threshold:
            voted.append(cluster_centroid(cluster))

    return voted


# =============================================================================
# MULTI-SCALE VOTING STRATEGIES
# =============================================================================

def strategy_simple_pool(
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    region_id: str,
    vote_threshold: int,
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Strategy 1: Simple Pool (Baseline)
    Pool all detections from all scales and apply single vote threshold.
    """
    all_dets = []
    for scale in SCALES:
        for pass_id, dets in deduped.get(scale, {}).get(region_id, {}).items():
            all_dets.extend(dets)

    if not all_dets:
        return []

    clusters = spatial_cluster(all_dets, tolerance_px)
    return [cluster_centroid(c) for c in clusters if len(c) >= vote_threshold]


def strategy_scale_normalised(
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    region_id: str,
    threshold: float,
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Strategy 2: Scale-Normalised Voting
    Weight votes inversely by scale's detection opportunities.
    """
    # Max possible per region per scale (approximate)
    max_votes = {'small': 16 * NUM_PASSES, 'medium': 4 * NUM_PASSES, 'large': 1 * NUM_PASSES}

    all_dets = []
    for scale in SCALES:
        for pass_id, dets in deduped.get(scale, {}).get(region_id, {}).items():
            all_dets.extend(dets)

    if not all_dets:
        return []

    clusters = spatial_cluster(all_dets, tolerance_px)

    results = []
    for cluster in clusters:
        # Count per scale
        scale_counts = defaultdict(int)
        for d in cluster:
            scale_counts[d['scale']] += 1

        # Normalised score (0-3 range)
        score = sum(
            min(scale_counts[scale] / max_votes[scale], 1.0)
            for scale in SCALES
        )

        if score >= threshold:
            results.append(cluster_centroid(cluster))

    return results


def strategy_two_stage(
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    region_id: str,
    within_threshold: int,
    cross_threshold: int,
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Strategy 3: Two-Stage (Scales as Voters)
    First vote within each scale, then require cross-scale agreement.
    """
    # Stage 1: Within-scale voting
    scale_predictions = {}
    for scale in SCALES:
        passes = deduped.get(scale, {}).get(region_id, {})
        preds = single_scale_voting(passes, within_threshold, tolerance_px)
        scale_predictions[scale] = [{'x': x, 'y': y, 'scale': scale} for x, y in preds]

    # Stage 2: Pool and cluster across scales
    all_preds = []
    for scale, preds in scale_predictions.items():
        all_preds.extend(preds)

    if not all_preds:
        return []

    clusters = spatial_cluster(all_preds, tolerance_px)

    # Require N scales to agree
    results = []
    for cluster in clusters:
        scales_present = count_unique_scales(cluster)
        if len(scales_present) >= cross_threshold:
            results.append(cluster_centroid(cluster))

    return results


def strategy_scale_confirmation(
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    region_id: str,
    min_scales: int,
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Strategy 4: Scale Confirmation
    Require detection in >= min_scales different scales (regardless of votes).
    """
    all_dets = []
    for scale in SCALES:
        for pass_id, dets in deduped.get(scale, {}).get(region_id, {}).items():
            all_dets.extend(dets)

    if not all_dets:
        return []

    clusters = spatial_cluster(all_dets, tolerance_px)

    results = []
    for cluster in clusters:
        scales_present = count_unique_scales(cluster)
        if len(scales_present) >= min_scales:
            results.append(cluster_centroid(cluster))

    return results


def strategy_confidence_fusion(
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    region_id: str,
    method: str,
    threshold: float,
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Strategy 5: Confidence-Weighted Fusion
    Use within-scale vote counts as confidence, combine across scales.
    """
    # Get within-scale confidences
    scale_confidences = {}
    for scale in SCALES:
        passes = deduped.get(scale, {}).get(region_id, {})
        all_dets = []
        for pass_id, dets in passes.items():
            all_dets.extend(dets)

        if not all_dets:
            scale_confidences[scale] = []
            continue

        clusters = spatial_cluster(all_dets, tolerance_px)
        scale_confidences[scale] = [
            {
                'x': cluster_centroid(c)[0],
                'y': cluster_centroid(c)[1],
                'confidence': count_unique_passes(c) / NUM_PASSES,
                'scale': scale
            }
            for c in clusters
        ]

    # Pool and cluster across scales
    all_confident = []
    for scale, confs in scale_confidences.items():
        all_confident.extend(confs)

    if not all_confident:
        return []

    clusters = spatial_cluster(all_confident, tolerance_px)

    # Combine confidences
    results = []
    for cluster in clusters:
        # Group by scale, take max confidence per scale
        conf_by_scale = {}
        for det in cluster:
            scale = det['scale']
            if scale not in conf_by_scale:
                conf_by_scale[scale] = det['confidence']
            else:
                conf_by_scale[scale] = max(conf_by_scale[scale], det['confidence'])

        values = list(conf_by_scale.values())

        if method == 'max':
            combined = max(values)
        elif method == 'mean':
            combined = np.mean(values)
        elif method == 'product':
            combined = np.prod(values)
        else:
            combined = np.mean(values)

        if combined >= threshold:
            results.append(cluster_centroid(cluster))

    return results


def strategy_cascaded(
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    region_id: str,
    confident_threshold: int,
    uncertain_range: Tuple[int, int],
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Strategy 6: Cascaded Disambiguation
    Use small tiles for primary detection, larger tiles for disambiguation.
    """
    # Primary: small tiles
    small_passes = deduped.get('small', {}).get(region_id, {})
    small_all = []
    for pass_id, dets in small_passes.items():
        small_all.extend(dets)

    if not small_all:
        return []

    small_clusters = spatial_cluster(small_all, tolerance_px)

    confident = []
    uncertain = []

    for cluster in small_clusters:
        votes = count_unique_passes(cluster)
        centroid = cluster_centroid(cluster)

        if votes >= confident_threshold:
            confident.append(centroid)
        elif uncertain_range[0] <= votes <= uncertain_range[1]:
            uncertain.append({'centroid': centroid, 'votes': votes})

    # Get medium/large predictions for disambiguation
    medium_preds = single_scale_voting(
        deduped.get('medium', {}).get(region_id, {}), 2, tolerance_px
    )
    large_preds = single_scale_voting(
        deduped.get('large', {}).get(region_id, {}), 2, tolerance_px
    )

    # Promote uncertain if confirmed by medium or large
    for unc in uncertain:
        medium_confirms = any(
            pixel_distance(unc['centroid'], m) < tolerance_px
            for m in medium_preds
        )
        large_confirms = any(
            pixel_distance(unc['centroid'], l) < tolerance_px
            for l in large_preds
        )
        if medium_confirms or large_confirms:
            confident.append(unc['centroid'])

    return confident


def strategy_unanimous(
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    region_id: str,
    within_threshold: int,
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Strategy 7: Unanimous Cross-Scale
    Require all three scales to detect (cross_threshold=3).
    """
    return strategy_two_stage(
        deduped, region_id, within_threshold, 3, tolerance_px
    )


def strategy_pr_optimised(
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    region_id: str,
    generator_scale: str,
    filter_scale: str,
    generator_threshold: int,
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Strategy 8: Precision/Recall Optimised
    Use high-recall scale as generator, high-precision scale as filter.
    """
    # Generate candidates
    gen_passes = deduped.get(generator_scale, {}).get(region_id, {})
    candidates = single_scale_voting(gen_passes, generator_threshold, tolerance_px)

    # Get filter predictions
    filt_passes = deduped.get(filter_scale, {}).get(region_id, {})
    filter_preds = single_scale_voting(filt_passes, 2, tolerance_px)

    # Keep candidates confirmed by filter
    confirmed = [
        c for c in candidates
        if any(pixel_distance(c, f) < tolerance_px for f in filter_preds)
    ]

    return confirmed


def strategy_f1_weighted(
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    region_id: str,
    scale_f1_scores: Dict[str, float],
    within_threshold: int,
    threshold: float,
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Strategy 9: F1-Weighted Voting
    Weight each scale's vote by its observed F1 performance.
    """
    # Get voted predictions per scale
    scale_predictions = {}
    for scale in SCALES:
        passes = deduped.get(scale, {}).get(region_id, {})
        all_dets = []
        for pass_id, dets in passes.items():
            all_dets.extend(dets)

        if not all_dets:
            scale_predictions[scale] = []
            continue

        clusters = spatial_cluster(all_dets, tolerance_px)
        scale_predictions[scale] = [
            {
                'x': cluster_centroid(c)[0],
                'y': cluster_centroid(c)[1],
                'confidence': count_unique_passes(c) / NUM_PASSES,
                'scale': scale,
                'weight': scale_f1_scores.get(scale, 0.5)
            }
            for c in clusters
            if count_unique_passes(c) >= within_threshold
        ]

    # Pool and cluster
    all_preds = []
    for scale, preds in scale_predictions.items():
        all_preds.extend(preds)

    if not all_preds:
        return []

    clusters = spatial_cluster(all_preds, tolerance_px)

    # Compute weighted scores
    max_possible = sum(scale_f1_scores.values())
    results = []
    for cluster in clusters:
        weighted_sum = sum(d['weight'] * d['confidence'] for d in cluster)
        normalised = weighted_sum / max_possible if max_possible > 0 else 0

        if normalised >= threshold:
            results.append(cluster_centroid(cluster))

    return results


def strategy_fine_to_coarse(
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    region_id: str,
    primary_scale: str,
    context_scale: str,
    confident_threshold: int,
    uncertain_range: Tuple[int, int],
    tolerance_px: float
) -> Dict[str, Any]:
    """
    Strategy 10: Fine-to-Coarse Pipeline Simulation
    Simulates two-stage detection with primary and context scales.

    Returns detailed breakdown for analysis.
    """
    # Stage 1: Within-scale voting on primary
    primary_passes = deduped.get(primary_scale, {}).get(region_id, {})
    primary_all = []
    for pass_id, dets in primary_passes.items():
        primary_all.extend(dets)

    confident = []
    uncertain = []
    rejected = []

    if primary_all:
        clusters = spatial_cluster(primary_all, tolerance_px)

        for cluster in clusters:
            votes = count_unique_passes(cluster)
            centroid = cluster_centroid(cluster)

            if votes >= confident_threshold:
                confident.append({
                    'centroid': centroid,
                    'source': 'stage1_confident',
                    'primary_votes': votes
                })
            elif uncertain_range[0] <= votes <= uncertain_range[1]:
                uncertain.append({
                    'centroid': centroid,
                    'primary_votes': votes
                })
            else:
                rejected.append({
                    'centroid': centroid,
                    'primary_votes': votes
                })

    # Stage 2: Check uncertain against context scale
    context_passes = deduped.get(context_scale, {}).get(region_id, {})
    context_all = []
    for pass_id, dets in context_passes.items():
        context_all.extend(dets)

    context_predictions = []
    if context_all:
        context_clusters = spatial_cluster(context_all, tolerance_px)
        context_predictions = [
            {
                'centroid': cluster_centroid(c),
                'votes': count_unique_passes(c)
            }
            for c in context_clusters
            if count_unique_passes(c) >= 1
        ]

    promoted = []
    still_uncertain = []

    for unc in uncertain:
        context_nearby = [
            cp for cp in context_predictions
            if pixel_distance(unc['centroid'], cp['centroid']) < tolerance_px
        ]

        if context_nearby:
            best_context = max(context_nearby, key=lambda x: x['votes'])
            promoted.append({
                'centroid': unc['centroid'],
                'source': 'stage2_promoted',
                'primary_votes': unc['primary_votes'],
                'context_votes': best_context['votes']
            })
        else:
            still_uncertain.append(unc)

    # Final predictions
    final = confident + promoted

    return {
        'predictions': [p['centroid'] for p in final],
        'detailed': final,
        'breakdown': {
            'stage1_confident': len(confident),
            'stage2_promoted': len(promoted),
            'stage2_rejected': len(still_uncertain),
            'stage1_rejected': len(rejected),
            'total_accepted': len(final)
        }
    }


# =============================================================================
# SECONDARY ANALYSES
# =============================================================================

def analyse_scale_agreement(
    reference_gt: Dict[str, List[Dict]],
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    tolerance_px: float
) -> Dict[str, Any]:
    """
    Analyse which ground truth mounds are detected by which scales.
    """
    results = {
        'all_three': 0,
        'two_scales': 0,
        'one_scale': 0,
        'none': 0,
        'small_only': 0,
        'medium_only': 0,
        'large_only': 0,
        'small_medium_only': 0,
        'small_large_only': 0,
        'medium_large_only': 0,
        'by_mound': []
    }

    # Get predictions per scale (using 2/5 threshold as reference)
    scale_preds = {}
    for scale in SCALES:
        scale_preds[scale] = {}
        for region_id in reference_gt.keys():
            passes = deduped.get(scale, {}).get(region_id, {})
            preds = single_scale_voting(passes, 2, tolerance_px)
            scale_preds[scale][region_id] = preds

    # Analyse each ground truth mound
    for region_id, mounds in reference_gt.items():
        for mound in mounds:
            gt_pos = (mound['pixel_x'], mound['pixel_y'])
            detected_by = set()

            for scale in SCALES:
                preds = scale_preds[scale].get(region_id, [])
                if any(pixel_distance(gt_pos, p) < tolerance_px for p in preds):
                    detected_by.add(scale)

            results['by_mound'].append({
                'region': region_id,
                'position': gt_pos,
                'detected_by': list(detected_by)
            })

            n_scales = len(detected_by)
            if n_scales == 3:
                results['all_three'] += 1
            elif n_scales == 2:
                results['two_scales'] += 1
                if detected_by == {'small', 'medium'}:
                    results['small_medium_only'] += 1
                elif detected_by == {'small', 'large'}:
                    results['small_large_only'] += 1
                elif detected_by == {'medium', 'large'}:
                    results['medium_large_only'] += 1
            elif n_scales == 1:
                results['one_scale'] += 1
                if 'small' in detected_by:
                    results['small_only'] += 1
                elif 'medium' in detected_by:
                    results['medium_only'] += 1
                elif 'large' in detected_by:
                    results['large_only'] += 1
            else:
                results['none'] += 1

    return results


def analyse_error_correlation(
    reference_gt: Dict[str, List[Dict]],
    deduped: Dict[str, Dict[str, Dict[int, List[Dict]]]],
    tolerance_px: float
) -> Dict[str, Any]:
    """
    Analyse whether false negatives are correlated across scales.
    """
    # Get predictions per scale
    scale_preds = {}
    for scale in SCALES:
        scale_preds[scale] = {}
        for region_id in reference_gt.keys():
            passes = deduped.get(scale, {}).get(region_id, {})
            preds = single_scale_voting(passes, 2, tolerance_px)
            scale_preds[scale][region_id] = preds

    # Build miss matrix
    miss_matrix = []  # Each row: [small_missed, medium_missed, large_missed]

    for region_id, mounds in reference_gt.items():
        for mound in mounds:
            gt_pos = (mound['pixel_x'], mound['pixel_y'])
            row = []

            for scale in SCALES:
                preds = scale_preds[scale].get(region_id, [])
                missed = not any(
                    pixel_distance(gt_pos, p) < tolerance_px for p in preds
                )
                row.append(1 if missed else 0)

            miss_matrix.append(row)

    if len(miss_matrix) < 2:
        return {
            'small_medium': 0.0,
            'small_large': 0.0,
            'medium_large': 0.0,
            'interpretation': 'insufficient_data'
        }

    miss_matrix = np.array(miss_matrix)

    # Compute pairwise correlations
    def safe_corr(a, b):
        if np.std(a) == 0 or np.std(b) == 0:
            return 0.0
        return np.corrcoef(a, b)[0, 1]

    correlations = {
        'small_medium': safe_corr(miss_matrix[:, 0], miss_matrix[:, 1]),
        'small_large': safe_corr(miss_matrix[:, 0], miss_matrix[:, 2]),
        'medium_large': safe_corr(miss_matrix[:, 1], miss_matrix[:, 2])
    }

    # Interpretation
    avg_corr = np.mean(list(correlations.values()))
    if avg_corr > 0.7:
        interp = 'strongly_correlated'
    elif avg_corr > 0.3:
        interp = 'weakly_correlated'
    else:
        interp = 'independent'

    correlations['interpretation'] = interp

    return correlations


# =============================================================================
# EVALUATION AND SWEEPS
# =============================================================================

def evaluate_strategy(
    predictions: List[Tuple[float, float]],
    ground_truth: List[Dict],
    tolerance_px: float
) -> Dict[str, Any]:
    """Evaluate predictions against ground truth."""
    tp, fp, fn = match_detections_to_ground_truth(
        predictions,
        [{'pixel_x': m['pixel_x'], 'pixel_y': m['pixel_y']} for m in ground_truth],
        REFERENCE_TILE_SIZE
    )
    return compute_metrics(tp, fp, fn)


def run_single_scale_baselines(
    deduped: Dict,
    reference_gt: Dict,
    tolerance_px: float
) -> Dict[str, Dict]:
    """Run single-scale voting for all scales and thresholds."""
    results = {}

    for scale in SCALES:
        results[scale] = {'by_threshold': {}}

        for threshold in WITHIN_THRESHOLDS:
            region_results = []

            for region_id, gt_mounds in reference_gt.items():
                passes = deduped.get(scale, {}).get(region_id, {})
                preds = single_scale_voting(passes, threshold, tolerance_px)
                metrics = evaluate_strategy(preds, gt_mounds, tolerance_px)
                region_results.append(metrics)

            # Aggregate
            total_tp = sum(r['tp'] for r in region_results)
            total_fp = sum(r['fp'] for r in region_results)
            total_fn = sum(r['fn'] for r in region_results)

            point = compute_metrics(total_tp, total_fp, total_fn)
            bootstrap = bootstrap_metrics(region_results)

            results[scale]['by_threshold'][f'{threshold}_of_5'] = {
                'precision': point['precision'],
                'recall': point['recall'],
                'f1': point['f1'],
                'tp': total_tp,
                'fp': total_fp,
                'fn': total_fn,
                'ci_low': bootstrap['f1']['ci_low'],
                'ci_high': bootstrap['f1']['ci_high']
            }

        # Find best threshold
        best_thresh = max(
            results[scale]['by_threshold'].items(),
            key=lambda x: x[1]['f1']
        )
        results[scale]['best_threshold'] = best_thresh[0]
        results[scale]['best_f1'] = best_thresh[1]['f1']

    return results


def run_multiscale_sweep(
    deduped: Dict,
    reference_gt: Dict,
    tolerance_px: float,
    scale_f1_scores: Dict[str, float]
) -> Dict[str, Dict]:
    """Run all multi-scale strategy sweeps."""
    results = {}

    # Strategy 3: Two-Stage
    print("  Two-stage voting...")
    results['two_stage'] = {'by_config': {}}
    for within_t in WITHIN_THRESHOLDS:
        for cross_t in CROSS_THRESHOLDS:
            config = f'within_{within_t}_cross_{cross_t}'
            region_results = []

            for region_id, gt_mounds in reference_gt.items():
                preds = strategy_two_stage(
                    deduped, region_id, within_t, cross_t, tolerance_px
                )
                metrics = evaluate_strategy(preds, gt_mounds, tolerance_px)
                region_results.append(metrics)

            total_tp = sum(r['tp'] for r in region_results)
            total_fp = sum(r['fp'] for r in region_results)
            total_fn = sum(r['fn'] for r in region_results)
            point = compute_metrics(total_tp, total_fp, total_fn)
            bootstrap = bootstrap_metrics(region_results)

            results['two_stage']['by_config'][config] = {
                'precision': point['precision'],
                'recall': point['recall'],
                'f1': point['f1'],
                'tp': total_tp, 'fp': total_fp, 'fn': total_fn,
                'ci_low': bootstrap['f1']['ci_low'],
                'ci_high': bootstrap['f1']['ci_high']
            }

    # Strategy 4: Scale Confirmation
    print("  Scale confirmation...")
    results['scale_confirmation'] = {'by_config': {}}
    for min_scales in CROSS_THRESHOLDS:
        config = f'min_scales_{min_scales}'
        region_results = []

        for region_id, gt_mounds in reference_gt.items():
            preds = strategy_scale_confirmation(
                deduped, region_id, min_scales, tolerance_px
            )
            metrics = evaluate_strategy(preds, gt_mounds, tolerance_px)
            region_results.append(metrics)

        total_tp = sum(r['tp'] for r in region_results)
        total_fp = sum(r['fp'] for r in region_results)
        total_fn = sum(r['fn'] for r in region_results)
        point = compute_metrics(total_tp, total_fp, total_fn)
        bootstrap = bootstrap_metrics(region_results)

        results['scale_confirmation']['by_config'][config] = {
            'precision': point['precision'],
            'recall': point['recall'],
            'f1': point['f1'],
            'tp': total_tp, 'fp': total_fp, 'fn': total_fn,
            'ci_low': bootstrap['f1']['ci_low'],
            'ci_high': bootstrap['f1']['ci_high']
        }

    # Strategy 5: Confidence Fusion
    print("  Confidence fusion...")
    results['confidence_fusion'] = {'by_config': {}}
    for method in ['max', 'mean', 'product']:
        for thresh in [0.3, 0.4, 0.5, 0.6, 0.7]:
            config = f'{method}_{thresh}'
            region_results = []

            for region_id, gt_mounds in reference_gt.items():
                preds = strategy_confidence_fusion(
                    deduped, region_id, method, thresh, tolerance_px
                )
                metrics = evaluate_strategy(preds, gt_mounds, tolerance_px)
                region_results.append(metrics)

            total_tp = sum(r['tp'] for r in region_results)
            total_fp = sum(r['fp'] for r in region_results)
            total_fn = sum(r['fn'] for r in region_results)
            point = compute_metrics(total_tp, total_fp, total_fn)
            bootstrap = bootstrap_metrics(region_results)

            results['confidence_fusion']['by_config'][config] = {
                'precision': point['precision'],
                'recall': point['recall'],
                'f1': point['f1'],
                'tp': total_tp, 'fp': total_fp, 'fn': total_fn,
                'ci_low': bootstrap['f1']['ci_low'],
                'ci_high': bootstrap['f1']['ci_high']
            }

    # Strategy 6: Cascaded Disambiguation
    print("  Cascaded disambiguation...")
    results['cascaded'] = {'by_config': {}}
    configs = [
        (3, (1, 2)), (3, (2, 2)), (4, (1, 3)), (4, (2, 3)), (5, (2, 4)), (5, (3, 4))
    ]
    for conf_t, unc_range in configs:
        config = f'conf_{conf_t}_unc_{unc_range[0]}-{unc_range[1]}'
        region_results = []

        for region_id, gt_mounds in reference_gt.items():
            preds = strategy_cascaded(
                deduped, region_id, conf_t, unc_range, tolerance_px
            )
            metrics = evaluate_strategy(preds, gt_mounds, tolerance_px)
            region_results.append(metrics)

        total_tp = sum(r['tp'] for r in region_results)
        total_fp = sum(r['fp'] for r in region_results)
        total_fn = sum(r['fn'] for r in region_results)
        point = compute_metrics(total_tp, total_fp, total_fn)
        bootstrap = bootstrap_metrics(region_results)

        results['cascaded']['by_config'][config] = {
            'precision': point['precision'],
            'recall': point['recall'],
            'f1': point['f1'],
            'tp': total_tp, 'fp': total_fp, 'fn': total_fn,
            'ci_low': bootstrap['f1']['ci_low'],
            'ci_high': bootstrap['f1']['ci_high']
        }

    # Strategy 7: Unanimous
    print("  Unanimous cross-scale...")
    results['unanimous'] = {'by_config': {}}
    for within_t in WITHIN_THRESHOLDS:
        config = f'within_{within_t}'
        region_results = []

        for region_id, gt_mounds in reference_gt.items():
            preds = strategy_unanimous(
                deduped, region_id, within_t, tolerance_px
            )
            metrics = evaluate_strategy(preds, gt_mounds, tolerance_px)
            region_results.append(metrics)

        total_tp = sum(r['tp'] for r in region_results)
        total_fp = sum(r['fp'] for r in region_results)
        total_fn = sum(r['fn'] for r in region_results)
        point = compute_metrics(total_tp, total_fp, total_fn)
        bootstrap = bootstrap_metrics(region_results)

        results['unanimous']['by_config'][config] = {
            'precision': point['precision'],
            'recall': point['recall'],
            'f1': point['f1'],
            'tp': total_tp, 'fp': total_fp, 'fn': total_fn,
            'ci_low': bootstrap['f1']['ci_low'],
            'ci_high': bootstrap['f1']['ci_high']
        }

    # Strategy 8: P/R Optimised
    print("  P/R optimised...")
    results['pr_optimised'] = {'by_config': {}}
    configs = [
        ('small', 'medium', 1), ('small', 'medium', 2),
        ('small', 'large', 1), ('small', 'large', 2),
        ('medium', 'large', 2)
    ]
    for gen_scale, filt_scale, gen_t in configs:
        config = f'gen_{gen_scale}_filt_{filt_scale}_t{gen_t}'
        region_results = []

        for region_id, gt_mounds in reference_gt.items():
            preds = strategy_pr_optimised(
                deduped, region_id, gen_scale, filt_scale, gen_t, tolerance_px
            )
            metrics = evaluate_strategy(preds, gt_mounds, tolerance_px)
            region_results.append(metrics)

        total_tp = sum(r['tp'] for r in region_results)
        total_fp = sum(r['fp'] for r in region_results)
        total_fn = sum(r['fn'] for r in region_results)
        point = compute_metrics(total_tp, total_fp, total_fn)
        bootstrap = bootstrap_metrics(region_results)

        results['pr_optimised']['by_config'][config] = {
            'precision': point['precision'],
            'recall': point['recall'],
            'f1': point['f1'],
            'tp': total_tp, 'fp': total_fp, 'fn': total_fn,
            'ci_low': bootstrap['f1']['ci_low'],
            'ci_high': bootstrap['f1']['ci_high']
        }

    # Strategy 9: F1-Weighted
    print("  F1-weighted voting...")
    results['f1_weighted'] = {'by_config': {}, 'scale_weights': scale_f1_scores}
    for within_t in WITHIN_THRESHOLDS:
        for thresh in [0.3, 0.4, 0.5, 0.6, 0.7]:
            config = f'within_{within_t}_thresh_{thresh}'
            region_results = []

            for region_id, gt_mounds in reference_gt.items():
                preds = strategy_f1_weighted(
                    deduped, region_id, scale_f1_scores, within_t, thresh, tolerance_px
                )
                metrics = evaluate_strategy(preds, gt_mounds, tolerance_px)
                region_results.append(metrics)

            total_tp = sum(r['tp'] for r in region_results)
            total_fp = sum(r['fp'] for r in region_results)
            total_fn = sum(r['fn'] for r in region_results)
            point = compute_metrics(total_tp, total_fp, total_fn)
            bootstrap = bootstrap_metrics(region_results)

            results['f1_weighted']['by_config'][config] = {
                'precision': point['precision'],
                'recall': point['recall'],
                'f1': point['f1'],
                'tp': total_tp, 'fp': total_fp, 'fn': total_fn,
                'ci_low': bootstrap['f1']['ci_low'],
                'ci_high': bootstrap['f1']['ci_high']
            }

    # Strategy 10: Fine-to-Coarse
    print("  Fine-to-coarse simulation...")
    results['fine_to_coarse'] = {'by_config': {}}
    configs = [
        ('medium', 'large', 5, (2, 4)),
        ('medium', 'large', 4, (2, 3)),
        ('medium', 'large', 4, (1, 3)),
        ('small', 'large', 5, (2, 4)),
        ('small', 'large', 4, (2, 3)),
        ('small', 'medium', 5, (2, 4)),
        ('small', 'medium', 4, (2, 3))
    ]
    for primary, context, conf_t, unc_range in configs:
        config = f'{primary}_{context}_conf{conf_t}_unc{unc_range[0]}-{unc_range[1]}'
        region_results = []
        all_breakdowns = []

        for region_id, gt_mounds in reference_gt.items():
            result = strategy_fine_to_coarse(
                deduped, region_id, primary, context, conf_t, unc_range, tolerance_px
            )
            metrics = evaluate_strategy(result['predictions'], gt_mounds, tolerance_px)
            region_results.append(metrics)
            all_breakdowns.append(result['breakdown'])

        total_tp = sum(r['tp'] for r in region_results)
        total_fp = sum(r['fp'] for r in region_results)
        total_fn = sum(r['fn'] for r in region_results)
        point = compute_metrics(total_tp, total_fp, total_fn)
        bootstrap = bootstrap_metrics(region_results)

        # Aggregate breakdowns
        total_breakdown = {
            'stage1_confident': sum(b['stage1_confident'] for b in all_breakdowns),
            'stage2_promoted': sum(b['stage2_promoted'] for b in all_breakdowns),
            'stage2_rejected': sum(b['stage2_rejected'] for b in all_breakdowns),
            'stage1_rejected': sum(b['stage1_rejected'] for b in all_breakdowns)
        }

        # Compute promotion rate
        uncertain_total = total_breakdown['stage2_promoted'] + total_breakdown['stage2_rejected']
        promotion_rate = (
            total_breakdown['stage2_promoted'] / uncertain_total
            if uncertain_total > 0 else 0.0
        )

        results['fine_to_coarse']['by_config'][config] = {
            'precision': point['precision'],
            'recall': point['recall'],
            'f1': point['f1'],
            'tp': total_tp, 'fp': total_fp, 'fn': total_fn,
            'ci_low': bootstrap['f1']['ci_low'],
            'ci_high': bootstrap['f1']['ci_high'],
            'breakdown': total_breakdown,
            'promotion_rate': promotion_rate
        }

    # Find best config for each strategy
    for strategy_name, strategy_data in results.items():
        if 'by_config' in strategy_data and strategy_data['by_config']:
            best = max(
                strategy_data['by_config'].items(),
                key=lambda x: x[1]['f1']
            )
            strategy_data['best_config'] = best[0]
            strategy_data['best_f1'] = best[1]['f1']

    return results


# =============================================================================
# OUTPUT GENERATION
# =============================================================================

def generate_summary_markdown(all_results: Dict) -> str:
    """Generate human-readable summary."""
    lines = [
        "# Multi-Scale Voting Analysis: Summary",
        "",
        f"Generated: {all_results.get('analysis_date', 'N/A')}",
        "",
        "## Executive Summary",
        "",
    ]

    # Best single vs multi-scale
    best_single = all_results['summary']['best_single_scale']
    best_multi = all_results['summary']['best_multiscale']
    improvement = all_results['summary']['improvement']

    lines.extend([
        f"**Best Single-Scale**: {best_single['scale']} at {best_single['config']} "
        f"(F1={best_single['f1']:.3f})",
        f"**Best Multi-Scale**: {best_multi['strategy']} at {best_multi['config']} "
        f"(F1={best_multi['f1']:.3f})",
        f"**Improvement**: {improvement:+.3f}",
        f"**Recommendation**: {all_results['summary']['recommendation']}",
        "",
        "---",
        "",
        "## Single-Scale Baselines",
        "",
    ])

    # Single-scale tables
    for scale in SCALES:
        scale_data = all_results['single_scale_results'].get(scale, {})
        lines.append(f"### {scale.capitalize()} ({SCALE_TO_SIZE[scale]}px)")
        lines.append("")
        lines.append("| Threshold | Precision | Recall | F1 | 95% CI |")
        lines.append("|-----------|-----------|--------|------|--------|")

        for thresh in WITHIN_THRESHOLDS:
            key = f'{thresh}_of_5'
            data = scale_data.get('by_threshold', {}).get(key, {})
            lines.append(
                f"| {key} | {data.get('precision', 0):.3f} | "
                f"{data.get('recall', 0):.3f} | {data.get('f1', 0):.3f} | "
                f"[{data.get('ci_low', 0):.3f}-{data.get('ci_high', 0):.3f}] |"
            )
        lines.append("")

    # Multi-scale comparison
    lines.extend([
        "---",
        "",
        "## Multi-Scale Strategy Comparison",
        "",
        "Best configuration per strategy:",
        "",
        "| Strategy | Config | Precision | Recall | F1 | 95% CI |",
        "|----------|--------|-----------|--------|------|--------|",
    ])

    for strategy in ['two_stage', 'scale_confirmation', 'confidence_fusion',
                     'cascaded', 'unanimous', 'pr_optimised', 'f1_weighted',
                     'fine_to_coarse']:
        strategy_data = all_results['multiscale_results'].get(strategy, {})
        best_config = strategy_data.get('best_config', 'N/A')
        best_data = strategy_data.get('by_config', {}).get(best_config, {})

        lines.append(
            f"| {strategy} | {best_config} | "
            f"{best_data.get('precision', 0):.3f} | "
            f"{best_data.get('recall', 0):.3f} | "
            f"{best_data.get('f1', 0):.3f} | "
            f"[{best_data.get('ci_low', 0):.3f}-{best_data.get('ci_high', 0):.3f}] |"
        )
    lines.append("")

    # Fine-to-coarse breakdown
    lines.extend([
        "---",
        "",
        "## Fine-to-Coarse Pipeline Analysis",
        "",
        "| Config | Stage1 Conf | Stage2 Promoted | Stage2 Rejected | Promotion Rate |",
        "|--------|-------------|-----------------|-----------------|----------------|",
    ])

    f2c_data = all_results['multiscale_results'].get('fine_to_coarse', {}).get('by_config', {})
    for config, data in f2c_data.items():
        breakdown = data.get('breakdown', {})
        lines.append(
            f"| {config} | {breakdown.get('stage1_confident', 0)} | "
            f"{breakdown.get('stage2_promoted', 0)} | "
            f"{breakdown.get('stage2_rejected', 0)} | "
            f"{data.get('promotion_rate', 0):.2%} |"
        )
    lines.append("")

    # Scale agreement
    lines.extend([
        "---",
        "",
        "## Scale Agreement Analysis",
        "",
    ])

    agreement = all_results.get('scale_agreement', {})
    total = sum([
        agreement.get('all_three', 0),
        agreement.get('two_scales', 0),
        agreement.get('one_scale', 0),
        agreement.get('none', 0)
    ])

    if total > 0:
        lines.extend([
            f"- Detected by all 3 scales: {agreement.get('all_three', 0)} "
            f"({100 * agreement.get('all_three', 0) / total:.1f}%)",
            f"- Detected by exactly 2 scales: {agreement.get('two_scales', 0)} "
            f"({100 * agreement.get('two_scales', 0) / total:.1f}%)",
            f"- Detected by only 1 scale: {agreement.get('one_scale', 0)} "
            f"({100 * agreement.get('one_scale', 0) / total:.1f}%)",
            f"- Missed by all scales: {agreement.get('none', 0)} "
            f"({100 * agreement.get('none', 0) / total:.1f}%)",
            "",
        ])

    # Error correlation
    lines.extend([
        "---",
        "",
        "## Error Correlation",
        "",
    ])

    corr = all_results.get('error_correlation', {})
    lines.extend([
        f"- Small-Medium FN correlation: {corr.get('small_medium', 0):.3f}",
        f"- Small-Large FN correlation: {corr.get('small_large', 0):.3f}",
        f"- Medium-Large FN correlation: {corr.get('medium_large', 0):.3f}",
        f"- Interpretation: {corr.get('interpretation', 'N/A')}",
        "",
    ])

    return "\n".join(lines)


def generate_csv(all_results: Dict) -> List[List[str]]:
    """Generate flat CSV data."""
    rows = [['strategy', 'config', 'precision', 'recall', 'f1', 'tp', 'fp', 'fn',
             'ci_low', 'ci_high']]

    # Single-scale
    for scale in SCALES:
        scale_data = all_results['single_scale_results'].get(scale, {})
        for thresh, data in scale_data.get('by_threshold', {}).items():
            rows.append([
                f'single_{scale}', thresh,
                f"{data.get('precision', 0):.4f}",
                f"{data.get('recall', 0):.4f}",
                f"{data.get('f1', 0):.4f}",
                str(data.get('tp', 0)),
                str(data.get('fp', 0)),
                str(data.get('fn', 0)),
                f"{data.get('ci_low', 0):.4f}",
                f"{data.get('ci_high', 0):.4f}"
            ])

    # Multi-scale
    for strategy in ['two_stage', 'scale_confirmation', 'confidence_fusion',
                     'cascaded', 'unanimous', 'pr_optimised', 'f1_weighted',
                     'fine_to_coarse']:
        strategy_data = all_results['multiscale_results'].get(strategy, {})
        for config, data in strategy_data.get('by_config', {}).items():
            rows.append([
                strategy, config,
                f"{data.get('precision', 0):.4f}",
                f"{data.get('recall', 0):.4f}",
                f"{data.get('f1', 0):.4f}",
                str(data.get('tp', 0)),
                str(data.get('fp', 0)),
                str(data.get('fn', 0)),
                f"{data.get('ci_low', 0):.4f}",
                f"{data.get('ci_high', 0):.4f}"
            ])

    return rows


# =============================================================================
# MAIN
# =============================================================================

def main():
    print(f"Multi-Scale Voting Analysis v{__version__}")
    print("=" * 60)

    tolerance_px = metres_to_pixels(SPATIAL_TOLERANCE_M, REFERENCE_TILE_SIZE)

    # Load reference ground truth
    print("\nLoading reference ground truth...")
    reference_gt = load_reference_ground_truth()
    total_mounds = sum(len(m) for m in reference_gt.values())
    print(f"  {total_mounds} mounds across {len(reference_gt)} regions")

    # Load and normalise all detections
    print("\nLoading and normalising detections...")
    all_detections = load_all_detections_normalised()
    for scale in SCALES:
        n_dets = sum(
            len(dets)
            for passes in all_detections.get(scale, {}).values()
            for dets in passes.values()
        )
        print(f"  {scale}: {n_dets} detections")

    # Apply within-pass deduplication
    print("\nApplying within-pass deduplication...")
    deduped = prepare_deduplicated_detections(all_detections)

    # Run single-scale baselines
    print("\nRunning single-scale baselines...")
    single_results = run_single_scale_baselines(deduped, reference_gt, tolerance_px)

    # Get F1 scores for weighted voting
    scale_f1_scores = {
        scale: single_results[scale]['best_f1']
        for scale in SCALES
    }
    print(f"  Scale F1 scores: {scale_f1_scores}")

    # Run multi-scale sweep
    print("\nRunning multi-scale parameter sweep...")
    multi_results = run_multiscale_sweep(
        deduped, reference_gt, tolerance_px, scale_f1_scores
    )

    # Secondary analyses
    print("\nRunning secondary analyses...")
    print("  Scale agreement...")
    agreement = analyse_scale_agreement(reference_gt, deduped, tolerance_px)
    print("  Error correlation...")
    correlation = analyse_error_correlation(reference_gt, deduped, tolerance_px)

    # Find best overall
    best_single_f1 = max(single_results[s]['best_f1'] for s in SCALES)
    best_single_scale = max(SCALES, key=lambda s: single_results[s]['best_f1'])
    best_single_config = single_results[best_single_scale]['best_threshold']

    best_multi_f1 = 0
    best_multi_strategy = ''
    best_multi_config = ''
    for strategy, data in multi_results.items():
        if 'best_f1' in data and data['best_f1'] > best_multi_f1:
            best_multi_f1 = data['best_f1']
            best_multi_strategy = strategy
            best_multi_config = data.get('best_config', '')

    improvement = best_multi_f1 - best_single_f1

    # Determine recommendation
    if improvement < 0:
        recommendation = 'do_not_pursue'
    elif improvement < 0.02:
        recommendation = 'do_not_pursue'
    elif improvement < 0.05:
        recommendation = 'consider'
    else:
        recommendation = 'pursue'

    # Compile results
    all_results = {
        'analysis_date': datetime.now(timezone.utc).isoformat(),
        'ground_truth_count': total_mounds,
        'parameters': {
            'spatial_tolerance_m': SPATIAL_TOLERANCE_M,
            'bootstrap_iterations': BOOTSTRAP_ITERATIONS
        },
        'single_scale_results': single_results,
        'multiscale_results': multi_results,
        'scale_agreement': {k: v for k, v in agreement.items() if k != 'by_mound'},
        'error_correlation': correlation,
        'summary': {
            'best_single_scale': {
                'scale': best_single_scale,
                'config': best_single_config,
                'f1': best_single_f1
            },
            'best_multiscale': {
                'strategy': best_multi_strategy,
                'config': best_multi_config,
                'f1': best_multi_f1
            },
            'improvement': improvement,
            'recommendation': recommendation
        }
    }

    # Save outputs
    print("\nSaving outputs...")

    json_path = OUTPUT_DIR / "multiscale_analysis.json"
    with open(json_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"  Saved: {json_path}")

    md_path = OUTPUT_DIR / "multiscale_summary.md"
    with open(md_path, 'w') as f:
        f.write(generate_summary_markdown(all_results))
    print(f"  Saved: {md_path}")

    csv_path = OUTPUT_DIR / "multiscale_full_sweep.csv"
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(generate_csv(all_results))
    print(f"  Saved: {csv_path}")

    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"\nBest single-scale: {best_single_scale} ({best_single_config}) "
          f"F1={best_single_f1:.3f}")
    print(f"Best multi-scale: {best_multi_strategy} ({best_multi_config}) "
          f"F1={best_multi_f1:.3f}")
    print(f"Improvement: {improvement:+.3f}")
    print(f"Recommendation: {recommendation}")
    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
