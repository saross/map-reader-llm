# Multi-Scale Voting Analysis: Pilot Study

## Overview

This document describes the multi-scale voting analysis to be performed on the tile size pilot data. The pilot tests three tile sizes (256×256, 512×512, 1024×1024) on the same geographic area with K=5 passes each. This provides an opportunity to simulate cross-scale voting strategies at minimal additional cost.

## Data Structure

**Input**: Raw detections from the tile size pilot

| Scale | Tile Size | Tile Count | Passes | Total API Calls |
|-------|-----------|------------|--------|-----------------|
| Small | 256×256 | 160 | 5 | 800 |
| Medium | 512×512 | 40 | 5 | 200 |
| Large | 1024×1024 | 10 | 5 | 50 |

**Key property**: All three scales cover the **exact same geographic area** (10 stratified regions). Detections can be converted to common map coordinates for cross-scale comparison.

**Ground truth**: 19 mound symbols in the valid comparison region (48px margins on 1024px tiles).

**API configuration**: 1024px tiles processed with `media_resolution=HIGH` to prevent internal tiling by Gemini API.

## Empirical Single-Scale Results

The pilot produced the following within-scale results (used to calibrate multi-scale strategies):

### 256px Tiles (Small)

| Threshold | Precision | Recall | F1 | TP | FP | FN |
|-----------|-----------|--------|------|----|----|-----|
| 1/5 | 0.032 | 0.947 | 0.062 | 18 | 546 | 1 |
| 2/5 | 0.098 | 0.895 | 0.176 | 17 | 157 | 2 |
| 3/5 | 0.156 | 0.895 | 0.266 | 17 | 92 | 2 |
| 4/5 | 0.213 | 0.684 | 0.325 | 13 | 48 | 6 |
| 5/5 | 0.286 | 0.526 | 0.370 | 10 | 25 | 9 |

**Character**: High recall, very low precision. Catches almost everything but hallucinates constantly.

### 512px Tiles (Medium)

| Threshold | Precision | Recall | F1 | TP | FP | FN |
|-----------|-----------|--------|------|----|----|-----|
| 1/5 | 0.061 | 0.947 | 0.114 | 18 | 279 | 1 |
| 2/5 | 0.152 | 0.789 | 0.254 | 15 | 84 | 4 |
| 3/5 | 0.245 | 0.684 | 0.361 | 13 | 40 | 6 |
| 4/5 | 0.476 | 0.526 | **0.500** | 10 | 11 | 9 |
| 5/5 | 0.857 | 0.316 | 0.462 | 6 | 1 | 13 |

**Character**: Balanced precision-recall trade-off. Best overall F1 at 4/5 threshold.

### 1024px Tiles (Large)

| Threshold | Precision | Recall | F1 | TP | FP | FN |
|-----------|-----------|--------|------|----|----|-----|
| 1/5 | 0.063 | 0.632 | 0.114 | 12 | 179 | 7 |
| 2/5 | 0.304 | 0.368 | 0.333 | 7 | 16 | 12 |
| 3/5 | 0.556 | 0.263 | 0.357 | 5 | 4 | 14 |
| 4/5 | 0.600 | 0.158 | 0.250 | 3 | 2 | 16 |
| 5/5 | 1.000 | 0.053 | 0.100 | 1 | 0 | 18 |

**Character**: Higher precision but very low recall. Misses ~63% of mounds at 2/5 threshold.

### Scale Comparison Summary

| Scale | Best Threshold | Best F1 | P at 2/5 | R at 2/5 |
|-------|----------------|---------|----------|----------|
| Small (256px) | 5/5 | 0.370 | 0.098 | 0.895 |
| Medium (512px) | 4/5 | **0.500** | 0.152 | 0.789 |
| Large (1024px) | 3/5 | 0.357 | 0.304 | 0.368 |

**Key insight**: Scales are complementary but with asymmetric strengths:
- Small tiles have excellent recall (0.90) but terrible precision (0.10)
- Large tiles have better precision (0.30) but unacceptable recall (0.37)
- Medium tiles offer the best single-scale balance

**Implication for multi-scale**: The low recall of large tiles limits their value as a confirmation layer — they can only confirm things they also detected (≤37% of true mounds).

## Coordinate Normalisation

Before any cross-scale analysis, all detections must be converted to a common coordinate system:

```python
def normalise_to_map_coords(detection, tile_info):
    """
    Convert tile-relative detection (0-1000) to map pixel coordinates.
    
    Args:
        detection: dict with 'box_2d': [ymin, xmin, ymax, xmax] in 0-1000 range
        tile_info: dict with 'x_offset', 'y_offset', 'tile_size' in map pixels
    
    Returns:
        dict with 'centroid_x', 'centroid_y' in map pixel coordinates
    """
    # Detection centroid in normalised coords
    ymin, xmin, ymax, xmax = detection['box_2d']
    cx_norm = (xmin + xmax) / 2 / 1000  # 0-1 range
    cy_norm = (ymin + ymax) / 2 / 1000
    
    # Convert to map pixels
    cx_map = tile_info['x_offset'] + cx_norm * tile_info['tile_size']
    cy_map = tile_info['y_offset'] + cy_norm * tile_info['tile_size']
    
    return {
        'centroid_x': cx_map,
        'centroid_y': cy_map,
        'source_scale': tile_info['scale'],
        'source_tile': tile_info['tile_id'],
        'source_pass': detection['pass_id']
    }
```

## Overlap Deduplication

**The issue**: With 12.5% overlap, a symbol near a tile edge appears in multiple adjacent tiles. Within a single pass, this creates multiple "detections" of the same physical symbol.

**Solution**: Deduplicate within each pass first, then vote across passes. This requires **two-stage clustering**:

1. **First clustering** (within pass): Handles tile overlap — same symbol detected in adjacent tiles becomes one detection
2. **Second clustering** (across passes): Groups detections near the same location across passes for voting

Both stages use the same 20m threshold for consistency with F1 evaluation.

```python
def process_scale_with_dedup(raw_detections, tile_info, cluster_distance=20):
    """
    Process raw detections for one scale with proper deduplication.
    
    Args:
        raw_detections: list of dicts, each with 'tile_id', 'pass_id', 'box_2d'
        tile_info: dict mapping tile_id -> {x_offset, y_offset, tile_size, scale}
    
    Returns:
        dict mapping pass_id -> list of deduplicated detection centroids (map coords)
    """
    # Step 1: Convert all detections to map coordinates
    map_detections = []
    for det in raw_detections:
        info = tile_info[det['tile_id']]
        map_det = normalise_to_map_coords(det, info)
        map_det['pass_id'] = det['pass_id']
        map_detections.append(map_det)
    
    # Step 2: Group by pass
    by_pass = defaultdict(list)
    for det in map_detections:
        by_pass[det['pass_id']].append(det)
    
    # Step 3: Within each pass, cluster to deduplicate overlap
    deduplicated = {}
    for pass_id, pass_dets in by_pass.items():
        clusters = spatial_cluster(pass_dets, distance_threshold=cluster_distance)
        # Each cluster becomes one detection (the centroid)
        deduplicated[pass_id] = [cluster_centroid(c) for c in clusters]
    
    return deduplicated


def count_votes_across_passes(deduplicated_by_pass, location, cluster_distance=20):
    """
    Count how many passes detected something near this location.
    """
    votes = 0
    for pass_id, detections in deduplicated_by_pass.items():
        if any(distance(location, det) < cluster_distance for det in detections):
            votes += 1
    return votes
```

**Processing workflow**:

```
Raw detections (per tile, per pass)
    ↓
Convert to map coordinates
    ↓
Group by pass
    ↓
Within each pass: cluster to merge overlap duplicates
    ↓
Now have: deduplicated detections per pass
    ↓
Pool across passes, cluster again
    ↓
Count unique passes contributing to each cluster = vote count
    ↓
Apply threshold
```

**Edge case example**: A symbol exactly on the overlap boundary might be:
- Detected in tile A, pass 1
- Detected in tile B, pass 1 (same pass, adjacent tile)
- Detected in tile A, pass 2
- Missed in tile B, pass 2

After within-pass deduplication:
- Pass 1: 1 detection (A and B merged)
- Pass 2: 1 detection (only A)

Vote count: 2/5 ✓

This is the correct behaviour — we're counting "did the model find it in this pass" not "how many tiles saw it."

## Aggregation Strategies

### Strategy 1: Simple Pool (Baseline)

Pool all detections from all scales and passes into one set, apply spatial clustering and vote threshold.

**Method**:
1. Collect all detections (D_small ∪ D_medium ∪ D_large)
2. Cluster spatially (20m threshold)
3. Apply vote threshold (e.g., require N votes)

**Problem**: Massively unbalanced — small tiles contribute 16× more detections than large tiles for the same area. A threshold of "10 votes" is trivial for small-scale detections but impossible for large-scale.

**Purpose**: Naive baseline to show why scale-aware voting matters.

```python
def simple_pool_voting(all_detections, vote_threshold, cluster_distance=20):
    """
    Naive pooling across all scales.
    """
    clusters = spatial_cluster(all_detections, distance_threshold=cluster_distance)
    
    voted_detections = []
    for cluster in clusters:
        if len(cluster) >= vote_threshold:
            voted_detections.append(cluster_centroid(cluster))
    
    return voted_detections
```

### Strategy 2: Scale-Normalised Voting

Weight votes inversely by the number of opportunities to detect at that scale.

**Method**:
1. Compute max possible votes per scale: small=800, medium=200, large=50
2. Weight each vote: w_small=1/800, w_medium=1/200, w_large=1/50
3. Sum weighted votes per cluster
4. Apply threshold on weighted sum (e.g., ≥0.5 means majority coverage)

**Rationale**: Treats each scale fairly regardless of tile count.

```python
def scale_normalised_voting(all_detections, threshold=0.5, cluster_distance=20):
    """
    Weight votes by inverse of scale's detection opportunities.
    """
    # Max possible detections per scale (tiles × passes)
    max_votes = {'small': 800, 'medium': 200, 'large': 50}
    
    clusters = spatial_cluster(all_detections, distance_threshold=cluster_distance)
    
    voted_detections = []
    for cluster in clusters:
        # Count votes per scale
        scale_counts = {'small': 0, 'medium': 0, 'large': 0}
        for det in cluster:
            scale_counts[det['source_scale']] += 1
        
        # Compute weighted score (0-3 range, one per scale)
        weighted_score = sum(
            min(count / max_votes[scale], 1.0)  # Cap at 1.0 per scale
            for scale, count in scale_counts.items()
        )
        
        if weighted_score >= threshold:
            voted_detections.append({
                'centroid': cluster_centroid(cluster),
                'score': weighted_score,
                'scale_votes': scale_counts
            })
    
    return voted_detections
```

### Strategy 3: Two-Stage (Scales as Voters)

First vote within each scale, then treat each scale's output as a single "voter" and require cross-scale agreement.

**Method**:
1. Within-scale voting: Apply 2/5 threshold at each scale independently
2. Cross-scale voting: Require detection in ≥N scales (N ∈ {1, 2, 3})

**Rationale**: Cleanest interpretation — each scale provides one "opinion", then we aggregate opinions.

```python
def two_stage_voting(detections_by_scale, within_threshold=2, cross_threshold=2, 
                     cluster_distance=20):
    """
    Two-stage voting: within-scale first, then cross-scale.
    
    Args:
        detections_by_scale: dict mapping scale -> list of detections
        within_threshold: minimum votes within a scale (out of 5 passes)
        cross_threshold: minimum scales that must agree (out of 3)
    """
    # Stage 1: Within-scale voting
    scale_predictions = {}
    for scale, detections in detections_by_scale.items():
        clusters = spatial_cluster(detections, distance_threshold=cluster_distance)
        scale_predictions[scale] = [
            cluster_centroid(c) for c in clusters 
            if count_unique_passes(c) >= within_threshold
        ]
    
    # Stage 2: Cross-scale voting
    # Pool all scale predictions
    all_predictions = []
    for scale, preds in scale_predictions.items():
        for pred in preds:
            pred['source_scale'] = scale
            all_predictions.append(pred)
    
    # Cluster across scales
    cross_clusters = spatial_cluster(all_predictions, distance_threshold=cluster_distance)
    
    # Require N scales to agree
    final_detections = []
    for cluster in cross_clusters:
        scales_present = set(p['source_scale'] for p in cluster)
        if len(scales_present) >= cross_threshold:
            final_detections.append({
                'centroid': cluster_centroid(cluster),
                'scales_agreeing': scales_present,
                'n_scales': len(scales_present)
            })
    
    return final_detections
```

### Strategy 4: Scale Confirmation

Require detection at ≥2 different scales, regardless of within-scale vote count.

**Method**:
1. Pool all raw detections (no within-scale voting)
2. Cluster spatially
3. For each cluster, count distinct scales represented
4. Keep clusters with ≥2 scales

**Rationale**: Multi-scale redundancy as a precision filter. If both small and large tiles see it, it's probably real.

```python
def scale_confirmation(all_detections, min_scales=2, cluster_distance=20):
    """
    Require detection in multiple scales (regardless of vote count).
    """
    clusters = spatial_cluster(all_detections, distance_threshold=cluster_distance)
    
    confirmed = []
    for cluster in clusters:
        scales_present = set(d['source_scale'] for d in cluster)
        if len(scales_present) >= min_scales:
            confirmed.append({
                'centroid': cluster_centroid(cluster),
                'scales': scales_present,
                'total_votes': len(cluster)
            })
    
    return confirmed
```

### Strategy 5: Confidence-Weighted Fusion

Use within-scale vote counts as confidence scores, combine across scales.

**Method**:
1. For each scale, compute voted detections with confidence (vote_count / 5)
2. For detections near the same location across scales, combine confidences
3. Apply threshold on combined confidence

**Combination options**:
- **Max**: confidence = max(conf_small, conf_medium, conf_large)
- **Mean**: confidence = mean of available scale confidences
- **Product**: confidence = product (high only if all scales agree)

```python
def confidence_weighted_fusion(detections_by_scale, method='mean', 
                                threshold=0.5, cluster_distance=20):
    """
    Fuse detections using confidence scores from each scale.
    """
    # Compute within-scale confidences
    scale_confidences = {}
    for scale, detections in detections_by_scale.items():
        clusters = spatial_cluster(detections, distance_threshold=cluster_distance)
        scale_confidences[scale] = [
            {
                'centroid': cluster_centroid(c),
                'confidence': count_unique_passes(c) / 5.0
            }
            for c in clusters
        ]
    
    # Pool and cluster across scales
    all_confident = []
    for scale, confs in scale_confidences.items():
        for c in confs:
            c['source_scale'] = scale
            all_confident.append(c)
    
    cross_clusters = spatial_cluster(all_confident, distance_threshold=cluster_distance)
    
    # Combine confidences
    fused = []
    for cluster in cross_clusters:
        confidences_by_scale = {}
        for det in cluster:
            scale = det['source_scale']
            # Take max confidence if multiple detections from same scale
            if scale not in confidences_by_scale:
                confidences_by_scale[scale] = det['confidence']
            else:
                confidences_by_scale[scale] = max(confidences_by_scale[scale], 
                                                   det['confidence'])
        
        # Combine
        conf_values = list(confidences_by_scale.values())
        if method == 'max':
            combined = max(conf_values)
        elif method == 'mean':
            combined = sum(conf_values) / len(conf_values)
        elif method == 'product':
            combined = 1.0
            for v in conf_values:
                combined *= v
        
        if combined >= threshold:
            fused.append({
                'centroid': cluster_centroid(cluster),
                'combined_confidence': combined,
                'scale_confidences': confidences_by_scale
            })
    
    return fused
```

### Strategy 6: Cascaded Disambiguation

Use small tiles for primary detection (best resolution), medium/large for disambiguation of uncertain cases.

**Method**:
1. Run within-scale voting on small tiles
2. Partition into: confident (≥4/5), uncertain (2-3/5), rejected (<2/5)
3. For uncertain detections, check if medium or large scale confirms
4. Promote uncertain → confident if confirmed; otherwise reject

**Rationale**: Small tiles have best symbol visibility; larger tiles provide context to break ties.

```python
def cascaded_disambiguation(detections_by_scale, 
                             confident_threshold=4,
                             uncertain_range=(2, 3),
                             cluster_distance=20):
    """
    Use small tiles as primary, larger tiles for disambiguation.
    """
    # Within-scale voting for small tiles
    small_clusters = spatial_cluster(
        detections_by_scale['small'], 
        distance_threshold=cluster_distance
    )
    
    confident = []
    uncertain = []
    
    for cluster in small_clusters:
        votes = count_unique_passes(cluster)
        if votes >= confident_threshold:
            confident.append(cluster_centroid(cluster))
        elif uncertain_range[0] <= votes <= uncertain_range[1]:
            uncertain.append({
                'centroid': cluster_centroid(cluster),
                'small_votes': votes
            })
    
    # Check uncertain against medium and large
    medium_predictions = get_voted_predictions(
        detections_by_scale['medium'], threshold=2, cluster_distance=cluster_distance
    )
    large_predictions = get_voted_predictions(
        detections_by_scale['large'], threshold=2, cluster_distance=cluster_distance
    )
    
    # Disambiguation
    for unc in uncertain:
        # Check if medium or large confirms
        medium_confirms = any(
            distance(unc['centroid'], m) < cluster_distance 
            for m in medium_predictions
        )
        large_confirms = any(
            distance(unc['centroid'], l) < cluster_distance 
            for l in large_predictions
        )
        
        if medium_confirms or large_confirms:
            confident.append(unc['centroid'])
    
    return confident
```

### Strategy 7: Unanimous Cross-Scale

Maximum precision: require detection in ALL three scales.

**Method**: Two-stage voting with cross_threshold=3

**Purpose**: Tests whether there's a "gold standard" subset that all scales agree on.

```python
def unanimous_cross_scale(detections_by_scale, within_threshold=2, cluster_distance=20):
    """
    Require all three scales to detect.
    """
    return two_stage_voting(
        detections_by_scale, 
        within_threshold=within_threshold,
        cross_threshold=3,  # All scales must agree
        cluster_distance=cluster_distance
    )
```

### Strategy 8: Scale-Specific Precision/Recall Optimisation

Combine scales based on their observed precision/recall characteristics.

**Method**:
1. From single-scale results, identify which scale has best precision vs recall
2. Use high-recall scale as candidate generator
3. Use high-precision scale as filter

**Implementation**: Depends on observed single-scale results; defined post-hoc.

```python
def precision_recall_optimised(detections_by_scale, 
                                generator_scale, 
                                filter_scale,
                                generator_threshold=2,
                                cluster_distance=20):
    """
    Use one scale for recall (generator), another for precision (filter).
    
    Args:
        generator_scale: Scale with best recall (probably 'small')
        filter_scale: Scale with best precision (probably 'large' or 'medium')
    """
    # Generate candidates from high-recall scale
    candidates = get_voted_predictions(
        detections_by_scale[generator_scale],
        threshold=generator_threshold,
        cluster_distance=cluster_distance
    )
    
    # Get filter predictions
    filter_predictions = get_voted_predictions(
        detections_by_scale[filter_scale],
        threshold=2,
        cluster_distance=cluster_distance
    )
    
    # Keep candidates confirmed by filter
    confirmed = [
        c for c in candidates
        if any(distance(c, f) < cluster_distance for f in filter_predictions)
    ]
    
    return confirmed
```

### Strategy 9: F1-Weighted Voting

Weight each scale's vote by its observed single-scale F1 performance.

**Method**:
1. Compute single-scale F1 for each scale (from primary analysis)
2. Weight each scale's contribution by its F1 score
3. Higher-performing scales get more influence on final predictions

**Rationale**: Data-driven weighting — scales that perform better individually should have more say in the ensemble.

```python
def f1_weighted_voting(detections_by_scale, scale_f1_scores, 
                       within_threshold=2, cluster_distance=20):
    """
    Weight each scale's vote by its observed single-scale F1.
    
    Args:
        scale_f1_scores: dict like {'small': 0.72, 'medium': 0.75, 'large': 0.61}
    """
    # Get voted predictions per scale
    scale_predictions = {}
    for scale, detections in detections_by_scale.items():
        clusters = spatial_cluster(detections, distance_threshold=cluster_distance)
        scale_predictions[scale] = [
            {
                'centroid': cluster_centroid(c),
                'votes': count_unique_passes(c),
                'confidence': count_unique_passes(c) / 5.0
            }
            for c in clusters
            if count_unique_passes(c) >= within_threshold
        ]
    
    # Pool and cluster across scales
    all_predictions = []
    for scale, preds in scale_predictions.items():
        for pred in preds:
            pred['source_scale'] = scale
            pred['weight'] = scale_f1_scores[scale]
            all_predictions.append(pred)
    
    cross_clusters = spatial_cluster(all_predictions, distance_threshold=cluster_distance)
    
    # Compute weighted score
    results = []
    for cluster in cross_clusters:
        weighted_sum = sum(p['weight'] * p['confidence'] for p in cluster)
        max_possible = sum(scale_f1_scores.values())  # If all scales with max confidence
        normalised_score = weighted_sum / max_possible
        
        results.append({
            'centroid': cluster_centroid(cluster),
            'weighted_score': normalised_score,
            'scales': set(p['source_scale'] for p in cluster)
        })
    
    return results
```

**Threshold options**: Apply threshold on `normalised_score` (range 0-1). Test thresholds: 0.3, 0.4, 0.5, 0.6, 0.7.

---

### Strategy 10: Fine-to-Coarse Pipeline Simulation

Simulate the two-stage fine-to-coarse pipeline (H2 Condition C) using existing multi-scale data.

**What the real pipeline does**:
1. Stage 1: Detect on smaller tiles with voting
2. Identify uncertain candidates (e.g., 2-3/5 agreement)
3. Stage 2: Extract NEW larger tile centred on candidate, re-query with verification prompt

**What we can approximate**:
1. Stage 1: Use small (256) or medium (512) detections ✓
2. Identify uncertain: Find detections with vote count in uncertainty range ✓
3. Stage 2: Check if existing large (1024) tiles have detections nearby ≈

**Limitations**:
- Large tiles aren't centred on candidates — candidate falls somewhere in fixed tile
- No verification prompt — large tiles did a general sweep, not focused confirmation
- No attention guidance — real pipeline would highlight region of interest

**What it still tells us**:
- Do large tiles tend to **confirm** uncertain small/medium-tile detections?
- Do large tiles tend to **miss** things smaller tiles are uncertain about?
- Is there signal in scale agreement for the uncertain subset specifically?

**Empirically-calibrated thresholds** (based on pilot results):

For 512px (medium) as primary scale:
| Votes | Precision | Classification |
|-------|-----------|----------------|
| 5/5 | 0.86 | Confident — accept directly |
| 4/5 | 0.48 | Moderate — accept or verify |
| 2-3/5 | 0.15-0.25 | Uncertain — send to Stage 2 |
| 1/5 | 0.06 | Low confidence — reject or verify |

For 256px (small) as primary scale:
| Votes | Precision | Classification |
|-------|-----------|----------------|
| 5/5 | 0.29 | Moderate — verify recommended |
| 3-4/5 | 0.16-0.21 | Uncertain — send to Stage 2 |
| 2/5 | 0.10 | Very uncertain — send to Stage 2 |
| 1/5 | 0.03 | Reject |

```python
def simulate_fine_to_coarse(detections_by_scale, 
                            primary_scale='medium',
                            context_scale='large',
                            confident_threshold=4,
                            uncertain_range=(2, 3),
                            reject_threshold=1,
                            cluster_distance=20):
    """
    Simulate fine-to-coarse pipeline with existing multi-scale data.
    
    Caveat: Real pipeline would centre large tile on candidate and use
    verification prompt. This approximation uses fixed large tiles with
    detection prompt.
    
    Args:
        primary_scale: Scale for initial detection ('small' or 'medium')
        context_scale: Scale for confirmation ('large')
        confident_threshold: Minimum votes to accept without confirmation (e.g., 4 or 5)
        uncertain_range: (min, max) votes for uncertain candidates sent to Stage 2
        reject_threshold: Maximum votes to reject without confirmation (e.g., 1)
    """
    # Stage 1: Within-scale voting on primary (smaller) scale
    primary_clusters = spatial_cluster(
        detections_by_scale[primary_scale],
        distance_threshold=cluster_distance
    )
    
    confident = []
    uncertain = []
    rejected = []
    
    for cluster in primary_clusters:
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
        elif votes <= reject_threshold:
            rejected.append({
                'centroid': centroid,
                'primary_votes': votes
            })
        else:
            # Between reject and uncertain — treat as low-confidence uncertain
            uncertain.append({
                'centroid': centroid, 
                'primary_votes': votes
            })
    
    # Stage 2: Check uncertain candidates against context (larger) scale
    # Get voted predictions from context scale (not raw — we want some filtering)
    context_clusters = spatial_cluster(
        detections_by_scale[context_scale],
        distance_threshold=cluster_distance
    )
    context_predictions = [
        {
            'centroid': cluster_centroid(c),
            'votes': count_unique_passes(c)
        }
        for c in context_clusters
        if count_unique_passes(c) >= 1  # Any detection counts as signal
    ]
    
    promoted = []
    still_uncertain = []
    
    for unc in uncertain:
        # Check if context scale has detection nearby
        context_nearby = [
            cp for cp in context_predictions
            if distance(unc['centroid'], cp['centroid']) < cluster_distance
        ]
        
        if context_nearby:
            # Context scale confirms — promote to confident
            best_context = max(context_nearby, key=lambda x: x['votes'])
            promoted.append({
                'centroid': unc['centroid'],
                'source': 'stage2_promoted',
                'primary_votes': unc['primary_votes'],
                'context_votes': best_context['votes']
            })
        else:
            # No context confirmation — remains uncertain
            still_uncertain.append(unc)
    
    # Final predictions: confident + promoted
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
        },
        'parameters': {
            'primary_scale': primary_scale,
            'context_scale': context_scale,
            'confident_threshold': confident_threshold,
            'uncertain_range': uncertain_range
        }
    }
```

**Configurations to test**:

| Primary | Context | Confident | Uncertain Range | Rationale |
|---------|---------|-----------|-----------------|-----------|
| medium | large | 5 | (2, 4) | Conservative: only 5/5 accepted directly |
| medium | large | 4 | (2, 3) | Moderate: 4-5/5 accepted, 2-3/5 verified |
| medium | large | 4 | (1, 3) | Liberal: only 1/5 rejected outright |
| small | large | 5 | (2, 4) | Small primary, conservative |
| small | large | 4 | (2, 3) | Small primary, moderate |
| small | medium | 5 | (2, 4) | Medium as context (higher recall than large) |
| small | medium | 4 | (2, 3) | Medium as context, moderate |

**Analysis metrics**:

| Metric | Definition | Interpretation |
|--------|------------|----------------|
| Promotion rate | promoted / (promoted + rejected) | How often does context confirm? |
| Promotion precision | TP among promoted / total promoted | Are promotions correct? |
| Rejection precision | FP among rejected / total rejected | Are rejections correct? |
| Overall F1 | Standard F1 on final predictions | Net benefit of pipeline |
| Recall cost | R(pipeline) - R(accept all) | TP lost by requiring confirmation |
| Precision gain | P(pipeline) - P(accept all) | FP avoided by confirmation |

**Expected outcome given pilot data**:

With 1024px recall at only 0.37, the context scale will miss most of the uncertain candidates (even true positives). This limits the value of large-tile confirmation:

- If 512px flags 10 uncertain TPs, 1024px might only see ~4 of them
- Those 4 get promoted; the other 6 are incorrectly rejected
- Net effect: modest precision gain at significant recall cost

The simulation will quantify whether this trade-off is worthwhile, or whether an alternative (like 256px → 512px confirmation, or simply using higher single-scale thresholds) performs better.

---

## Analysis Plan

### Full Threshold Sweep

For all strategies that use within-scale voting thresholds, test all x-of-5 values:

```python
within_thresholds = [1, 2, 3, 4, 5]  # x-of-5
cross_thresholds = [1, 2, 3]  # for multi-scale strategies

# Example: Two-stage voting full sweep
results = {}
for within_t in within_thresholds:
    for cross_t in cross_thresholds:
        key = f"within_{within_t}_cross_{cross_t}"
        results[key] = two_stage_voting(
            detections_by_scale,
            within_threshold=within_t, 
            cross_threshold=cross_t
        )
```

**Combinations to test**:

| Strategy | Parameters | Total Configurations |
|----------|------------|---------------------|
| Single-scale (each) | threshold: 1-5 | 5 × 3 = 15 |
| Two-stage | within: 1-5, cross: 1-3 | 15 |
| Scale confirmation | min_scales: 1-3 | 3 |
| Confidence fusion | method: max/mean/product, threshold: 0.3-0.7 | 15 |
| Cascaded | confident: 3-5, uncertain: (1,2)/(2,3) | 6 |
| Unanimous | within: 1-5 | 5 |
| F1-weighted | within: 1-5, threshold: 0.3-0.7 | 25 |
| P/R optimised | generator_threshold: 1-5 | 5 |
| Fine-to-coarse | 7 configurations (see Strategy 10) | 7 |

Total: ~110 configurations. Computation is trivial on local machine.

### Primary Analysis

For each aggregation strategy and parameter combination, compute:
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)  
- **F1**: 2 × (P × R) / (P + R)
- **95% CI**: Bootstrapped confidence intervals (1000 iterations)

Report best configuration per strategy, plus full sweep tables in appendix.

**Summary table** (best configuration per strategy):

| Strategy | Best Config | Precision | Recall | F1 | 95% CI |
|----------|-------------|-----------|--------|-----|--------|
| Single-scale: Small (256) | 5/5 | 0.286 | 0.526 | 0.370 | [0.10-0.62] |
| Single-scale: Medium (512) | 4/5 | 0.476 | 0.526 | 0.500 | [0.14-0.77] |
| Single-scale: Large (1024) | 3/5 | 0.556 | 0.263 | 0.357 | [0.00-0.62] |
| Simple Pool | threshold | | | | |
| Scale-Normalised | threshold | | | | |
| Two-Stage | within_x, cross_y | | | | |
| Scale Confirmation | min_scales | | | | |
| Confidence Fusion | method, threshold | | | | |
| Cascaded Disambiguation | conf_t, unc_range | | | | |
| Unanimous | within_x | | | | |
| F1-Weighted | within_x, threshold | | | | |
| P/R Optimised | gen, filter, threshold | | | | |
| Fine-to-Coarse | primary, context, conf_t, unc_range | | | | |

### Secondary Analysis: Scale Agreement

Characterise what each scale detects:

```python
def analyse_scale_agreement(ground_truth, predictions_by_scale, cluster_distance=20):
    """
    Analyse which ground truth symbols are detected by which scales.
    """
    results = []
    
    for gt in ground_truth:
        detected_by = set()
        for scale, preds in predictions_by_scale.items():
            if any(distance(gt, p) < cluster_distance for p in preds):
                detected_by.add(scale)
        
        results.append({
            'ground_truth': gt,
            'detected_by': detected_by,
            'n_scales': len(detected_by)
        })
    
    # Summary statistics
    all_three = sum(1 for r in results if r['n_scales'] == 3)
    two_scales = sum(1 for r in results if r['n_scales'] == 2)
    one_scale = sum(1 for r in results if r['n_scales'] == 1)
    none = sum(1 for r in results if r['n_scales'] == 0)
    
    # Scale-specific
    by_small_only = sum(1 for r in results if r['detected_by'] == {'small'})
    by_large_only = sum(1 for r in results if r['detected_by'] == {'large'})
    
    return {
        'all_three': all_three,
        'two_scales': two_scales,
        'one_scale': one_scale,
        'none': none,
        'small_only': by_small_only,
        'large_only': by_large_only,
        'total': len(ground_truth)
    }
```

Report as Venn-style summary:
- Detected by all 3 scales: N (X%)
- Detected by exactly 2 scales: N (X%)
- Detected by only 1 scale: N (X%)
- Missed by all scales: N (X%)

### Tertiary Analysis: Error Correlation

Are errors correlated or independent across scales?

```python
def analyse_error_correlation(ground_truth, predictions_by_scale, cluster_distance=20):
    """
    Analyse whether FNs and FPs are correlated across scales.
    """
    # For each ground truth, record hit/miss per scale
    fn_matrix = []  # Each row: [small_missed, medium_missed, large_missed]
    
    for gt in ground_truth:
        row = []
        for scale in ['small', 'medium', 'large']:
            missed = not any(
                distance(gt, p) < cluster_distance 
                for p in predictions_by_scale[scale]
            )
            row.append(1 if missed else 0)
        fn_matrix.append(row)
    
    # Compute pairwise correlation of misses
    fn_matrix = np.array(fn_matrix)
    correlations = {
        'small_medium': np.corrcoef(fn_matrix[:, 0], fn_matrix[:, 1])[0, 1],
        'small_large': np.corrcoef(fn_matrix[:, 0], fn_matrix[:, 2])[0, 1],
        'medium_large': np.corrcoef(fn_matrix[:, 1], fn_matrix[:, 2])[0, 1]
    }
    
    return correlations
```

**Interpretation**:
- High correlation (>0.7): Scales make similar errors; multi-scale voting won't help much
- Low correlation (<0.3): Scales make independent errors; multi-scale voting likely beneficial
- Negative correlation: Scales are complementary; multi-scale voting very promising

---

## Decision Framework

After analysis, classify the multi-scale approach:

| Outcome | Interpretation | Recommendation |
|---------|----------------|----------------|
| Best multi-scale F1 < best single-scale F1 | Multi-scale hurts | Don't pursue |
| Best multi-scale within 0.02 of best single-scale | No benefit | Don't pursue (not worth complexity) |
| Best multi-scale 0.02-0.05 better | Modest benefit | Consider for Paper 2 if budget allows |
| Best multi-scale >0.05 better | Substantial benefit | Prioritise multi-scale in Paper 2 |

Additionally, examine:
- Does multi-scale primarily help precision (fewer FPs) or recall (fewer FNs)?
- Which strategy works best? (Informs future experimental design)
- Is error correlation low? (Validates theoretical basis for multi-scale)

---

## Implementation Notes

### Spatial Clustering

Use consistent 20m threshold matching F1 evaluation:

```python
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist

def spatial_cluster(detections, distance_threshold=20):
    """
    Cluster detections within distance_threshold metres.
    """
    if len(detections) == 0:
        return []
    if len(detections) == 1:
        return [detections]
    
    coords = np.array([[d['centroid_x'], d['centroid_y']] for d in detections])
    
    # Convert pixel distance to metres (assuming ~1m/pixel at 1:50,000)
    # Adjust conversion factor based on actual map resolution
    distances = pdist(coords)
    
    if len(distances) == 0:
        return [detections]
    
    linkage_matrix = linkage(distances, method='single')
    cluster_ids = fcluster(linkage_matrix, t=distance_threshold, criterion='distance')
    
    clusters = {}
    for det, cid in zip(detections, cluster_ids):
        if cid not in clusters:
            clusters[cid] = []
        clusters[cid].append(det)
    
    return list(clusters.values())
```

### Ground Truth Matching

Use same Hungarian algorithm as main evaluation:

```python
from scipy.optimize import linear_sum_assignment

def match_detections_to_ground_truth(detections, ground_truth, tolerance=20):
    """
    One-to-one matching using Hungarian algorithm.
    Returns TP, FP, FN counts.
    """
    if len(detections) == 0:
        return 0, 0, len(ground_truth)  # All FN
    if len(ground_truth) == 0:
        return 0, len(detections), 0  # All FP
    
    # Build cost matrix
    cost_matrix = np.zeros((len(detections), len(ground_truth)))
    for i, det in enumerate(detections):
        for j, gt in enumerate(ground_truth):
            dist = distance(det, gt)
            cost_matrix[i, j] = dist if dist <= tolerance else 1e6
    
    # Hungarian assignment
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    # Count matches within tolerance
    tp = sum(1 for i, j in zip(row_ind, col_ind) if cost_matrix[i, j] <= tolerance)
    fp = len(detections) - tp
    fn = len(ground_truth) - tp
    
    return tp, fp, fn
```

---

## Output Specification

### Primary Output: `outputs/pilot/multiscale_analysis.json`

```json
{
  "analysis_date": "YYYY-MM-DD",
  "single_scale_results": {
    "small": {
      "by_threshold": {
        "1_of_5": {"precision": X, "recall": X, "f1": X, "tp": N, "fp": N, "fn": N},
        "2_of_5": {"precision": X, "recall": X, "f1": X, "tp": N, "fp": N, "fn": N},
        "3_of_5": {...},
        "4_of_5": {...},
        "5_of_5": {...}
      },
      "best_threshold": "2_of_5",
      "best_f1": X,
      "best_precision": X,
      "best_recall": X,
      "ci_lower": X,
      "ci_upper": X
    },
    "medium": {...},
    "large": {...}
  },
  "multiscale_results": {
    "two_stage": {
      "by_config": {
        "within_1_cross_1": {"precision": X, "recall": X, "f1": X},
        "within_1_cross_2": {...},
        "within_1_cross_3": {...},
        "within_2_cross_1": {...},
        "within_2_cross_2": {...},
        "within_2_cross_3": {...},
        ...
        "within_5_cross_3": {...}
      },
      "best_config": "within_2_cross_2",
      "best_f1": X,
      "best_precision": X,
      "best_recall": X
    },
    "scale_confirmation": {
      "by_config": {
        "min_scales_1": {...},
        "min_scales_2": {...},
        "min_scales_3": {...}
      },
      "best_config": "min_scales_2",
      "best_f1": X
    },
    "confidence_fusion": {
      "by_config": {
        "max_0.3": {...},
        "max_0.5": {...},
        "mean_0.3": {...},
        "mean_0.5": {...},
        "product_0.3": {...},
        ...
      },
      "best_config": "mean_0.5",
      "best_f1": X
    },
    "cascaded_disambiguation": {
      "by_config": {
        "conf_3_unc_1-2": {...},
        "conf_4_unc_2-3": {...},
        ...
      },
      "best_config": "conf_4_unc_2-3",
      "best_f1": X
    },
    "unanimous": {
      "by_config": {
        "within_1": {...},
        "within_2": {...},
        ...
      },
      "best_config": "within_2",
      "best_f1": X
    },
    "f1_weighted": {
      "scale_weights": {"small": X, "medium": X, "large": X},
      "by_config": {
        "within_1_thresh_0.3": {...},
        "within_1_thresh_0.5": {...},
        ...
      },
      "best_config": "within_2_thresh_0.5",
      "best_f1": X
    },
    "pr_optimised": {
      "by_config": {
        "gen_small_filt_medium_thresh_1": {...},
        "gen_small_filt_large_thresh_2": {...},
        ...
      },
      "best_config": "gen_small_filt_medium_thresh_2",
      "best_f1": X
    },
    "fine_to_coarse": {
      "by_config": {
        "medium_large_conf5_unc2-4": {
          "precision": X, "recall": X, "f1": X,
          "breakdown": {
            "stage1_confident": N,
            "stage2_promoted": N,
            "stage2_rejected": N,
            "stage1_rejected": N
          },
          "promotion_rate": X,
          "promotion_precision": X,
          "recall_cost": X,
          "precision_gain": X
        },
        "medium_large_conf4_unc2-3": {...},
        "small_large_conf5_unc2-4": {...},
        "small_medium_conf4_unc2-3": {...},
        ...
      },
      "best_config": "medium_large_conf4_unc2-3",
      "best_f1": X,
      "best_precision": X,
      "best_recall": X
    }
  },
  "scale_agreement": {
    "all_three": N,
    "two_scales": N,
    "one_scale": N,
    "none": N,
    "small_only": N,
    "medium_only": N,
    "large_only": N,
    "small_medium_only": N,
    "small_large_only": N,
    "medium_large_only": N
  },
  "error_correlation": {
    "small_medium": X,
    "small_large": X,
    "medium_large": X,
    "interpretation": "independent | weakly_correlated | strongly_correlated"
  },
  "summary": {
    "best_single_scale": {"scale": "medium", "config": "2_of_5", "f1": X},
    "best_multiscale": {"strategy": "two_stage", "config": "within_2_cross_2", "f1": X},
    "improvement": X,
    "recommendation": "pursue | consider | do_not_pursue"
  }
}
```

### Summary Output: `outputs/pilot/multiscale_summary.md`

Human-readable summary with:
1. **Executive summary**: Best single-scale vs best multi-scale, improvement magnitude
2. **Single-scale results**: Full threshold sweep tables for each scale
3. **Multi-scale comparison table**: Best configuration per strategy
4. **Fine-to-coarse analysis**: Breakdown of promotion/rejection rates and precision gains
5. **Full sweep appendix**: All tested configurations with results
6. **Scale agreement breakdown**: Venn-style analysis
7. **Error correlation interpretation**: Independence assessment
8. **Recommendation with rationale**

### Supplementary Output: `outputs/pilot/multiscale_full_sweep.csv`

Flat CSV with all tested configurations for easy analysis:

```csv
strategy,config,precision,recall,f1,tp,fp,fn
single_small,1_of_5,0.45,0.92,0.60,46,56,4
single_small,2_of_5,0.68,0.84,0.75,42,20,8
...
two_stage,within_2_cross_2,0.78,0.82,0.80,41,12,9
fine_to_coarse,medium_large_conf4_unc2-3,0.65,0.70,0.67,35,19,15
...
```
