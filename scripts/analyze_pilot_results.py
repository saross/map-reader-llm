#!/usr/bin/env python3
"""
Tile Size Pilot: Analysis Script
=================================

Description:
    Analyses the detection results from the tile size pilot experiment.
    Computes precision, recall, and F1 with bootstrapped 95% confidence
    intervals for each tile size and voting threshold combination.

Usage:
    python scripts/analyze_pilot_results.py

Output:
    outputs/pilot/pilot_results.json - Structured metrics with CIs
    outputs/pilot/pilot_summary.md - Human-readable summary

Author: Shawn Ross, Adela Sobotkova
Licence: Apache 2.0
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import numpy as np

# Setup Project Path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Configuration
OUTPUT_DIR = BASE_DIR / "outputs" / "pilot"
PILOT_TILES_DIR = BASE_DIR / "inputs" / "pilot_tiles"

# Analysis parameters
TILE_SIZES = [256, 512, 1024]
VOTING_THRESHOLDS = [1, 2, 3, 4, 5]  # Out of 5 passes
NUM_PASSES = 5
SPATIAL_TOLERANCE_M = 20  # Metres for matching
BOOTSTRAP_ITERATIONS = 1000
CI_PERCENTILES = (2.5, 97.5)  # 95% CI

# Coverage margins due to overlap (smallest tiles define valid region)
# With 12.5% overlap: 256px tiles cover 928×928 of 1024×1024 (48px margins)
VALID_REGION_MARGIN = 48  # Pixels to exclude from edges of 1024 tile

# Reference tile size for ground truth (all comparisons use 1024px GT)
REFERENCE_TILE_SIZE = 1024

# Script version
__version__ = "1.2.0"  # Region-level pooling for correct boundary handling


def load_detections(tile_size: int) -> Dict:
    """Load detection results for a given tile size."""
    path = OUTPUT_DIR / str(tile_size) / "detections.json"
    with open(path, 'r') as f:
        return json.load(f)


def load_ground_truth(tile_size: int) -> Dict:
    """Load ground truth for a given tile size."""
    path = PILOT_TILES_DIR / str(tile_size) / "ground_truth.json"
    with open(path, 'r') as f:
        return json.load(f)


def load_reference_ground_truth() -> Dict[str, List[Dict]]:
    """
    Load and filter the reference ground truth (1024px) for all regions.

    Uses 1024px ground truth as the single source of truth, filtered to
    the valid comparison region (48px margins). This ensures consistent
    mound counts across all tile sizes.

    Returns:
        Dictionary mapping region_id to list of valid mounds with 1024px coords.
    """
    gt_1024 = load_ground_truth(REFERENCE_TILE_SIZE)

    reference_by_region = {}
    for tile_name, tile_data in gt_1024.items():
        region_id = tile_data['region_id']
        mounds = tile_data.get('mounds', [])

        # Filter to valid region (48px margin on 1024px tile)
        valid_mounds = []
        for mound in mounds:
            x, y = mound['pixel_x'], mound['pixel_y']
            if (VALID_REGION_MARGIN <= x < (REFERENCE_TILE_SIZE - VALID_REGION_MARGIN) and
                    VALID_REGION_MARGIN <= y < (REFERENCE_TILE_SIZE - VALID_REGION_MARGIN)):
                valid_mounds.append({
                    'pixel_x': x,
                    'pixel_y': y,
                    'symbol': mound.get('symbol', 'mound')
                })

        reference_by_region[region_id] = valid_mounds

    return reference_by_region


def get_tile_to_region_offset(tile_name: str, tile_size: int, gt_data: Dict) -> Tuple[int, int]:
    """
    Get the offset to convert tile coordinates to 1024px region coordinates.

    For tiles smaller than 1024px, they are positioned within the region
    with an offset. This returns (offset_x, offset_y) to add to tile coords
    to get 1024px region coords.

    Args:
        tile_name: Name of the tile (without .png extension)
        tile_size: Size of the tile
        gt_data: Ground truth data for this tile size

    Returns:
        (offset_x, offset_y) in pixels
    """
    gt_key = tile_name + '.png'
    if gt_key not in gt_data:
        return (0, 0)

    tile_info = gt_data[gt_key]
    tile_origin = tile_info.get('origin_px', [0, 0])

    # The 1024px tile has origin at (region_origin_x, region_origin_y)
    # Smaller tiles have origins offset from there
    # We need to find the 1024px tile's origin for this region to compute offset

    # Get the region's 1024px origin
    region_id = tile_info['region_id']
    gt_1024 = load_ground_truth(REFERENCE_TILE_SIZE)

    for name_1024, data_1024 in gt_1024.items():
        if data_1024['region_id'] == region_id:
            origin_1024 = data_1024['origin_px']
            # Offset = tile_origin - 1024_origin
            offset_x = tile_origin[0] - origin_1024[0]
            offset_y = tile_origin[1] - origin_1024[1]
            return (offset_x, offset_y)

    return (0, 0)


def filter_mounds_to_valid_region(
    mounds: List[Dict],
    tile_size: int
) -> List[Dict]:
    """
    Filter mounds to only those within the valid comparison region.

    The valid region is defined by the 256px tile coverage (48px margins
    from edges of the 1024 reference tile). For smaller tiles, we scale
    the margin proportionally.

    Args:
        mounds: List of mound dicts with pixel_x, pixel_y
        tile_size: Size of the tile these mounds are from

    Returns:
        Filtered list of mounds within valid region.
    """
    # Scale margin to tile size (48px margin on 1024 → proportional on smaller)
    scale = tile_size / 1024
    margin = VALID_REGION_MARGIN * scale

    valid_mounds = []
    for mound in mounds:
        x, y = mound['pixel_x'], mound['pixel_y']
        # Check if within valid region (margin from all edges)
        if margin <= x < (tile_size - margin) and margin <= y < (tile_size - margin):
            valid_mounds.append(mound)

    return valid_mounds


def normalised_to_pixel(coord: int, tile_size: int) -> float:
    """
    Convert normalised coordinate (0-1000) to pixel coordinate.

    The model returns bounding boxes with coordinates normalised to 0-1000.
    """
    return coord * tile_size / 1000.0


def box_centre(box: List[int], tile_size: int) -> Tuple[float, float]:
    """
    Get centre point of a bounding box in pixel coordinates.

    Args:
        box: [ymin, xmin, ymax, xmax] in normalised coords (0-1000)
        tile_size: Tile size in pixels

    Returns:
        (x, y) centre in pixel coordinates
    """
    ymin, xmin, ymax, xmax = box
    x_centre = normalised_to_pixel((xmin + xmax) / 2, tile_size)
    y_centre = normalised_to_pixel((ymin + ymax) / 2, tile_size)
    return x_centre, y_centre


def pixel_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """Calculate Euclidean distance between two points."""
    return np.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def metres_to_pixels(metres: float, tile_size: int) -> float:
    """
    Convert metres to pixels.

    Assuming 2.5m/pixel resolution (standard for these Soviet maps).
    """
    pixels_per_metre = 1 / 2.5
    return metres * pixels_per_metre


def aggregate_detections_by_voting(
    tile_data: Dict,
    threshold: int
) -> List[Tuple[float, float]]:
    """
    Aggregate detections across passes using spatial voting.

    Returns list of (x, y) centres that appear in >= threshold passes.
    """
    tile_size = tile_data.get('tile_size', 512)  # Fallback
    passes_data = tile_data.get('passes', {})

    # Collect all detections with their pass numbers
    all_detections = []
    for pass_num, pass_info in passes_data.items():
        detections = pass_info.get('detections', [])
        for det in detections:
            if 'box_2d' in det:
                centre = box_centre(det['box_2d'], tile_size)
                all_detections.append({
                    'centre': centre,
                    'pass': int(pass_num),
                    'label': det.get('label', 'mound')
                })

    if not all_detections:
        return []

    # Cluster detections spatially
    tolerance_px = metres_to_pixels(SPATIAL_TOLERANCE_M, tile_size)

    # Simple greedy clustering
    clusters = []
    used = set()

    for i, det in enumerate(all_detections):
        if i in used:
            continue

        cluster = [det]
        cluster_passes = {det['pass']}
        used.add(i)

        for j, other in enumerate(all_detections):
            if j in used:
                continue
            if other['pass'] in cluster_passes:
                continue  # One detection per pass per cluster

            dist = pixel_distance(det['centre'], other['centre'])
            if dist <= tolerance_px:
                cluster.append(other)
                cluster_passes.add(other['pass'])
                used.add(j)

        # Check if cluster meets threshold
        if len(cluster_passes) >= threshold:
            # Average position of cluster
            avg_x = np.mean([d['centre'][0] for d in cluster])
            avg_y = np.mean([d['centre'][1] for d in cluster])
            clusters.append((avg_x, avg_y))

    return clusters


def match_detections_to_ground_truth(
    detections: List[Tuple[float, float]],
    ground_truth: List[Dict],
    tile_size: int
) -> Tuple[int, int, int]:
    """
    Match detections to ground truth mounds.

    Returns:
        (true_positives, false_positives, false_negatives)
    """
    tolerance_px = metres_to_pixels(SPATIAL_TOLERANCE_M, tile_size)

    gt_matched = set()
    det_matched = set()

    # Match detections to ground truth
    for i, det in enumerate(detections):
        for j, gt in enumerate(ground_truth):
            if j in gt_matched:
                continue
            gt_pos = (gt['pixel_x'], gt['pixel_y'])
            if pixel_distance(det, gt_pos) <= tolerance_px:
                gt_matched.add(j)
                det_matched.add(i)
                break

    tp = len(gt_matched)
    fp = len(detections) - len(det_matched)
    fn = len(ground_truth) - len(gt_matched)

    return tp, fp, fn


def compute_metrics(tp: int, fp: int, fn: int) -> Dict[str, float]:
    """Compute precision, recall, and F1 from counts."""
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'tp': tp,
        'fp': fp,
        'fn': fn
    }


def bootstrap_metrics(
    tile_results: List[Dict],
    n_iterations: int = BOOTSTRAP_ITERATIONS
) -> Dict[str, Dict[str, float]]:
    """
    Compute bootstrapped confidence intervals for metrics.

    Args:
        tile_results: List of per-tile (tp, fp, fn) dicts
        n_iterations: Number of bootstrap samples

    Returns:
        Dict with mean and CI for each metric
    """
    if not tile_results:
        return {
            'precision': {'mean': 0.0, 'ci_low': 0.0, 'ci_high': 0.0},
            'recall': {'mean': 0.0, 'ci_low': 0.0, 'ci_high': 0.0},
            'f1': {'mean': 0.0, 'ci_low': 0.0, 'ci_high': 0.0}
        }

    rng = np.random.default_rng(42)  # Fixed seed for reproducibility

    precisions = []
    recalls = []
    f1s = []

    for _ in range(n_iterations):
        # Resample tiles with replacement
        sample_indices = rng.choice(len(tile_results), size=len(tile_results), replace=True)

        # Aggregate counts
        total_tp = sum(tile_results[i]['tp'] for i in sample_indices)
        total_fp = sum(tile_results[i]['fp'] for i in sample_indices)
        total_fn = sum(tile_results[i]['fn'] for i in sample_indices)

        metrics = compute_metrics(total_tp, total_fp, total_fn)
        precisions.append(metrics['precision'])
        recalls.append(metrics['recall'])
        f1s.append(metrics['f1'])

    def summarise(values):
        return {
            'mean': float(np.mean(values)),
            'ci_low': float(np.percentile(values, CI_PERCENTILES[0])),
            'ci_high': float(np.percentile(values, CI_PERCENTILES[1]))
        }

    return {
        'precision': summarise(precisions),
        'recall': summarise(recalls),
        'f1': summarise(f1s)
    }


# =============================================================================
# REGION-LEVEL POOLING FUNCTIONS
# =============================================================================

def collect_region_detections_by_pass(
    tile_names: List[str],
    detections_data: Dict,
    ground_truth_data: Dict,
    tile_size: int
) -> Dict[int, List[Dict]]:
    """
    Collect all raw detections from tiles in a region, organised by pass.

    Converts all detections to 1024px reference coordinates.

    Args:
        tile_names: List of tile names in this region
        detections_data: Full detections data structure
        ground_truth_data: Ground truth with tile offsets
        tile_size: Size of tiles being processed

    Returns:
        {pass_id: [{'x': float, 'y': float, 'tile_id': str}, ...]}
    """
    from collections import defaultdict
    detections_by_pass = defaultdict(list)

    for tile_name in tile_names:
        tile_info = detections_data['tiles'].get(tile_name, {})

        # Get offset for this tile
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
                    detections_by_pass[pass_id].append({
                        'x': ref_x,
                        'y': ref_y,
                        'tile_id': tile_name
                    })

    return dict(detections_by_pass)


def deduplicate_within_pass(
    detections: List[Dict],
    tolerance_px: float
) -> List[Dict]:
    """
    Deduplicate detections from overlapping tiles within a single pass.

    Clusters nearby detections and returns one centroid per cluster.

    Args:
        detections: List of detection dicts with 'x', 'y' keys
        tolerance_px: Maximum distance to consider detections as duplicates

    Returns:
        List of deduplicated detection dicts
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
            'y': avg_y
        })

    return deduped


def apply_region_level_voting(
    detections_by_pass: Dict[int, List[Dict]],
    threshold: int,
    tolerance_px: float
) -> List[Tuple[float, float]]:
    """
    Apply voting at the region level after within-pass deduplication.

    Args:
        detections_by_pass: {pass_id: [deduplicated detections]}
        threshold: Minimum number of passes required
        tolerance_px: Clustering tolerance

    Returns:
        List of (x, y) voted prediction centroids
    """
    # Pool all detections with pass tags
    all_dets = []
    for pass_id, dets in detections_by_pass.items():
        for det in dets:
            all_dets.append({
                'x': det['x'],
                'y': det['y'],
                'pass_id': pass_id
            })

    if not all_dets:
        return []

    # Cluster spatially
    clusters = []
    used = set()

    for i, det1 in enumerate(all_dets):
        if i in used:
            continue

        cluster = [det1]
        used.add(i)

        for j, det2 in enumerate(all_dets):
            if j in used:
                continue
            dist = pixel_distance((det1['x'], det1['y']), (det2['x'], det2['y']))
            if dist <= tolerance_px:
                cluster.append(det2)
                used.add(j)

        clusters.append(cluster)

    # Filter by vote threshold (unique passes)
    voted = []
    for cluster in clusters:
        unique_passes = len(set(d['pass_id'] for d in cluster))
        if unique_passes >= threshold:
            avg_x = np.mean([d['x'] for d in cluster])
            avg_y = np.mean([d['y'] for d in cluster])
            voted.append((avg_x, avg_y))

    return voted


def analyse_tile_size(tile_size: int, reference_gt: Dict[str, List[Dict]]) -> Dict:
    """
    Analyse detection results for a given tile size.

    Uses region-level pooling: detections from all tiles in a region are
    pooled, deduplicated within each pass, then voted at the region level.
    This correctly handles detections near tile boundaries.

    Args:
        tile_size: Size of tiles to analyse
        reference_gt: Reference ground truth (1024px, filtered) by region_id

    Returns:
        Metrics for each voting threshold.
    """
    print(f"\nAnalysing {tile_size}px tiles...")

    detections_data = load_detections(tile_size)
    ground_truth_data = load_ground_truth(tile_size)

    # Count reference ground truth
    total_ref_mounds = sum(len(mounds) for mounds in reference_gt.values())
    print(f"  Reference ground truth: {total_ref_mounds} mounds (from 1024px, filtered)")

    results = {
        'tile_size': tile_size,
        'tile_count': len(detections_data.get('tiles', {})),
        'thresholds': {}
    }

    # Group tiles by region for region-level analysis
    tiles_by_region: Dict[str, List[str]] = {}
    for tile_name in detections_data.get('tiles', {}).keys():
        gt_key = tile_name + '.png'
        if gt_key in ground_truth_data:
            region_id = ground_truth_data[gt_key]['region_id']
            if region_id not in tiles_by_region:
                tiles_by_region[region_id] = []
            tiles_by_region[region_id].append(tile_name)

    tolerance_px = metres_to_pixels(SPATIAL_TOLERANCE_M, REFERENCE_TILE_SIZE)

    # Pre-collect and deduplicate detections for each region (once per region)
    # This is done outside the threshold loop for efficiency
    region_deduped_by_pass: Dict[str, Dict[int, List[Dict]]] = {}

    for region_id, tile_names in tiles_by_region.items():
        # Collect all raw detections organised by pass
        detections_by_pass = collect_region_detections_by_pass(
            tile_names, detections_data, ground_truth_data, tile_size
        )

        # Deduplicate within each pass (handles tile overlap)
        deduped_by_pass = {}
        for pass_id, dets in detections_by_pass.items():
            deduped_by_pass[pass_id] = deduplicate_within_pass(dets, tolerance_px)

        region_deduped_by_pass[region_id] = deduped_by_pass

    for threshold in VOTING_THRESHOLDS:
        print(f"  Threshold {threshold}/5...")

        region_metrics = []

        for region_id, tile_names in tiles_by_region.items():
            # Get reference ground truth for this region
            gt_mounds = reference_gt.get(region_id, [])

            # Apply region-level voting with this threshold
            voted_detections = apply_region_level_voting(
                region_deduped_by_pass[region_id],
                threshold,
                tolerance_px
            )

            # Match against reference ground truth (in 1024px coords)
            tp, fp, fn = match_detections_to_ground_truth(
                voted_detections,
                [{'pixel_x': m['pixel_x'], 'pixel_y': m['pixel_y']} for m in gt_mounds],
                REFERENCE_TILE_SIZE
            )

            region_metrics.append({
                'tp': tp, 'fp': fp, 'fn': fn,
                'region': region_id,
                'gt_count': len(gt_mounds)
            })

        # Aggregate counts
        total_tp = sum(r['tp'] for r in region_metrics)
        total_fp = sum(r['fp'] for r in region_metrics)
        total_fn = sum(r['fn'] for r in region_metrics)

        # Compute point estimates
        point_metrics = compute_metrics(total_tp, total_fp, total_fn)

        # Bootstrap CIs (resample regions)
        bootstrap_results = bootstrap_metrics(region_metrics)

        results['thresholds'][threshold] = {
            'counts': {
                'tp': total_tp,
                'fp': total_fp,
                'fn': total_fn
            },
            'point_estimates': point_metrics,
            'bootstrap': bootstrap_results,
            'tile_count': len(tiles_by_region)
        }

        print(f"    TP={total_tp}, FP={total_fp}, FN={total_fn}")
        print(f"    P={point_metrics['precision']:.3f}, "
              f"R={point_metrics['recall']:.3f}, "
              f"F1={point_metrics['f1']:.3f}")

    return results


def deduplicate_detections(
    detections: List[Tuple[float, float]],
    tile_size: int
) -> List[Tuple[float, float]]:
    """
    Deduplicate detections from overlapping tiles.

    Clusters nearby detections and returns cluster centres.
    """
    if not detections:
        return []

    tolerance_px = metres_to_pixels(SPATIAL_TOLERANCE_M, tile_size)
    deduped = []
    used = set()

    for i, (x1, y1) in enumerate(detections):
        if i in used:
            continue

        cluster = [(x1, y1)]
        used.add(i)

        for j, (x2, y2) in enumerate(detections):
            if j in used:
                continue
            dist = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
            if dist <= tolerance_px:
                cluster.append((x2, y2))
                used.add(j)

        # Use cluster centre
        avg_x = np.mean([p[0] for p in cluster])
        avg_y = np.mean([p[1] for p in cluster])
        deduped.append((avg_x, avg_y))

    return deduped


def generate_summary_markdown(all_results: Dict) -> str:
    """Generate a human-readable markdown summary."""
    lines = [
        "# Tile Size Pilot: Analysis Summary",
        "",
        f"Generated: {all_results.get('analysis_timestamp', 'N/A')}",
        "",
        "## Overview",
        "",
        f"- Total tiles analysed: {sum(r['tile_count'] for r in all_results['sizes'].values())}",
        f"- Tile sizes tested: 256px, 512px, 1024px",
        f"- Voting thresholds: 1/5 to 5/5",
        f"- Spatial tolerance: {SPATIAL_TOLERANCE_M}m",
        f"- Bootstrap iterations: {BOOTSTRAP_ITERATIONS}",
        "",
        "**Note:** Ground truth filtered to valid comparison region (48px margins on 1024 tiles,",
        "scaled proportionally for smaller tiles). This ensures fair comparison across tile sizes",
        "by excluding edge mounds that smaller tile grids don't fully cover.",
        "",
        "## Results by Tile Size",
        ""
    ]

    for size in TILE_SIZES:
        size_data = all_results['sizes'].get(str(size), {})
        lines.append(f"### {size}px Tiles")
        lines.append("")
        lines.append("| Threshold | Precision | Recall | F1 | TP | FP | FN |")
        lines.append("|-----------|-----------|--------|----|----|----|----|")

        for threshold in VOTING_THRESHOLDS:
            thresh_data = size_data.get('thresholds', {}).get(threshold, {})
            bootstrap = thresh_data.get('bootstrap', {})
            counts = thresh_data.get('counts', {})

            p = bootstrap.get('precision', {})
            r = bootstrap.get('recall', {})
            f = bootstrap.get('f1', {})

            p_str = f"{p.get('mean', 0):.3f} [{p.get('ci_low', 0):.3f}-{p.get('ci_high', 0):.3f}]"
            r_str = f"{r.get('mean', 0):.3f} [{r.get('ci_low', 0):.3f}-{r.get('ci_high', 0):.3f}]"
            f_str = f"{f.get('mean', 0):.3f} [{f.get('ci_low', 0):.3f}-{f.get('ci_high', 0):.3f}]"

            lines.append(
                f"| {threshold}/5 | {p_str} | {r_str} | {f_str} | "
                f"{counts.get('tp', 0)} | {counts.get('fp', 0)} | {counts.get('fn', 0)} |"
            )

        lines.append("")

    # Add comparison at 2/5 threshold (main decision point)
    lines.extend([
        "## Comparison at 2/5 Threshold",
        "",
        "| Size | Precision | Recall | F1 |",
        "|------|-----------|--------|-------|"
    ])

    for size in TILE_SIZES:
        size_data = all_results['sizes'].get(str(size), {})
        thresh_data = size_data.get('thresholds', {}).get(2, {})
        bootstrap = thresh_data.get('bootstrap', {})

        f1_mean = bootstrap.get('f1', {}).get('mean', 0)
        p_mean = bootstrap.get('precision', {}).get('mean', 0)
        r_mean = bootstrap.get('recall', {}).get('mean', 0)

        lines.append(f"| {size}px | {p_mean:.3f} | {r_mean:.3f} | {f1_mean:.3f} |")

    lines.extend([
        "",
        "## Decision Criteria",
        "",
        "Per the pre-registration:",
        "",
        "| Comparison | Condition | Action |",
        "|------------|-----------|--------|",
        "| 256 vs 512 | 256px F1 ≥ 0.05 better | Switch to 256px |",
        "| 256 vs 512 | Within 0.03 | Stay at 512px |",
        "| 1024 vs 512 | 1024px F1 ≥ 0.10 worse | Confirms smaller better |",
        "| 1024 vs 512 | Within 0.05 | Consider 1024px for context |",
        ""
    ])

    # Add automated decision
    size_256 = all_results['sizes'].get('256', {}).get('thresholds', {}).get(2, {})
    size_512 = all_results['sizes'].get('512', {}).get('thresholds', {}).get(2, {})
    size_1024 = all_results['sizes'].get('1024', {}).get('thresholds', {}).get(2, {})

    f1_256 = size_256.get('bootstrap', {}).get('f1', {}).get('mean', 0)
    f1_512 = size_512.get('bootstrap', {}).get('f1', {}).get('mean', 0)
    f1_1024 = size_1024.get('bootstrap', {}).get('f1', {}).get('mean', 0)

    lines.append("## Automated Assessment")
    lines.append("")

    diff_256_512 = f1_256 - f1_512
    diff_1024_512 = f1_1024 - f1_512

    lines.append(f"- F1(256px) - F1(512px) = {diff_256_512:+.4f}")
    lines.append(f"- F1(1024px) - F1(512px) = {diff_1024_512:+.4f}")
    lines.append("")

    if diff_256_512 >= 0.05:
        lines.append("**Recommendation**: Switch to 256px tiles (≥0.05 F1 improvement)")
    elif abs(diff_256_512) <= 0.03:
        lines.append("**Recommendation**: Stay with 512px tiles (256px within 0.03 F1)")
    elif diff_256_512 < -0.03:
        lines.append("**Recommendation**: Stay with 512px tiles (512px performs better)")
    else:
        lines.append("**Recommendation**: Stay with 512px tiles (marginal difference)")

    lines.append("")

    return "\n".join(lines)


def main():
    from datetime import datetime, timezone

    print(f"Tile Size Pilot Analysis v{__version__}")
    print("=" * 50)

    # Check that detection results exist
    for size in TILE_SIZES:
        det_path = OUTPUT_DIR / str(size) / "detections.json"
        if not det_path.exists():
            print(f"Error: Detection results not found for {size}px")
            print(f"  Expected: {det_path}")
            print("  Run detection script first.")
            sys.exit(1)

    # Load reference ground truth (1024px, filtered to valid region)
    print("\nLoading reference ground truth (1024px, filtered)...")
    reference_gt = load_reference_ground_truth()
    total_ref_mounds = sum(len(mounds) for mounds in reference_gt.values())
    print(f"Reference: {total_ref_mounds} mounds across {len(reference_gt)} regions")

    # Analyse each tile size
    all_results = {
        'analysis_timestamp': datetime.now(timezone.utc).isoformat(),
        'parameters': {
            'spatial_tolerance_m': SPATIAL_TOLERANCE_M,
            'bootstrap_iterations': BOOTSTRAP_ITERATIONS,
            'ci_percentiles': list(CI_PERCENTILES),
            'num_passes': NUM_PASSES,
            'reference_mound_count': total_ref_mounds
        },
        'sizes': {}
    }

    for size in TILE_SIZES:
        results = analyse_tile_size(size, reference_gt)
        all_results['sizes'][str(size)] = results

    # Save structured results
    results_path = OUTPUT_DIR / "pilot_results.json"
    with open(results_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\nSaved structured results: {results_path}")

    # Generate and save summary
    summary = generate_summary_markdown(all_results)
    summary_path = OUTPUT_DIR / "pilot_summary.md"
    with open(summary_path, 'w') as f:
        f.write(summary)
    print(f"Saved summary: {summary_path}")

    # Print summary to console
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)

    print("\nF1 scores at 2/5 threshold:")
    for size in TILE_SIZES:
        size_data = all_results['sizes'].get(str(size), {})
        thresh_data = size_data.get('thresholds', {}).get(2, {})
        f1 = thresh_data.get('bootstrap', {}).get('f1', {})
        print(f"  {size}px: {f1.get('mean', 0):.3f} "
              f"[{f1.get('ci_low', 0):.3f}-{f1.get('ci_high', 0):.3f}]")

    print("\nAnalysis complete.")


if __name__ == "__main__":
    main()
