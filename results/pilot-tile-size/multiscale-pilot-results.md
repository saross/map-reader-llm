# Multi-Scale Voting Analysis: Pilot Results

**Date**: 2026-01-07
**Analysis Version**: 1.0
**Ground Truth**: 19 mound symbols across 10 stratified regions

## Executive Summary

The multi-scale voting analysis tested whether combining detections from multiple tile sizes (256px, 512px, 1024px) improves performance over single-scale detection. Point estimates suggest substantial improvement (+0.12 F1), but wide confidence intervals due to limited ground truth (n=19) prevent definitive conclusions.

**Key Findings**:
- Best single-scale: Medium (512px) at 4/5 threshold, F1 = 0.488 [0.14, 0.73]
- Best multi-scale: Scale Confirmation (3/3 agreement), F1 = 0.611 [0.28, 0.91]
- Improvement: +0.123 F1 (25% relative), but CIs overlap substantially
- Error correlation: Low/independent (-0.18 to +0.13), validating theoretical basis
- Recommendation: **Consider for Paper 2** with appropriate uncertainty caveats

---

## Methodological Note: Pooling Strategy

Both the pilot analysis and multi-scale analysis use **region-level pooling** with within-pass deduplication. This approach correctly handles detections near tile boundaries:

1. **Within each pass**: Deduplicate detections from overlapping tiles (merge detections of the same object from adjacent tiles)
2. **Across passes**: Count unique passes that detected each location
3. **Apply threshold**: Require N-of-5 passes for final detection

This contrasts with tile-level pooling, which would count votes per-tile before deduplication—incorrectly penalising detections near tile boundaries where votes are split across tiles.

**Verification**: Both analyses produce identical results (e.g., 512px at 4/5: TP=10, FP=12, FN=9, F1=0.488).

---

## Single-Scale Results

### Performance by Threshold

#### Small (256px) Tiles

| Threshold | Precision | Recall | F1 | TP | FP | FN | 95% CI |
|-----------|-----------|--------|------|----|----|-----|--------|
| 1/5 | 0.031 | 0.947 | 0.061 | 18 | 556 | 1 | [0.02, 0.11] |
| 2/5 | 0.094 | 0.895 | 0.170 | 17 | 164 | 2 | [0.06, 0.28] |
| 3/5 | 0.155 | 0.895 | 0.264 | 17 | 93 | 2 | [0.09, 0.43] |
| 4/5 | 0.238 | 0.789 | 0.366 | 15 | 48 | 4 | [0.14, 0.56] |
| **5/5** | **0.324** | **0.632** | **0.429** | 12 | 25 | 7 | [0.14, 0.64] |

**Character**: High recall, very low precision. Best F1 at 5/5 threshold.

#### Medium (512px) Tiles

| Threshold | Precision | Recall | F1 | TP | FP | FN | 95% CI |
|-----------|-----------|--------|------|----|----|-----|--------|
| 1/5 | 0.058 | 0.947 | 0.109 | 18 | 294 | 1 | [0.03, 0.21] |
| 2/5 | 0.149 | 0.789 | 0.250 | 15 | 86 | 4 | [0.09, 0.46] |
| 3/5 | 0.250 | 0.684 | 0.366 | 13 | 39 | 6 | [0.16, 0.57] |
| **4/5** | **0.455** | **0.526** | **0.488** | 10 | 12 | 9 | [0.14, 0.73] |
| 5/5 | 0.857 | 0.316 | 0.462 | 6 | 1 | 13 | [0.00, 0.63] |

**Character**: Balanced precision-recall. Best single-scale F1 overall.

#### Large (1024px) Tiles

| Threshold | Precision | Recall | F1 | TP | FP | FN | 95% CI |
|-----------|-----------|--------|------|----|----|-----|--------|
| 1/5 | 0.062 | 0.632 | 0.113 | 12 | 182 | 7 | [0.03, 0.23] |
| 2/5 | 0.292 | 0.368 | 0.326 | 7 | 17 | 12 | [0.12, 0.42] |
| **3/5** | **0.556** | **0.263** | **0.357** | 5 | 4 | 14 | [0.07, 0.59] |
| 4/5 | 0.600 | 0.158 | 0.250 | 3 | 2 | 16 | [0.00, 0.55] |
| 5/5 | 1.000 | 0.053 | 0.100 | 1 | 0 | 18 | [0.00, 0.29] |

**Character**: Higher precision but unacceptably low recall (37% at 2/5). Best F1 at 3/5.

### Scale Comparison Summary

| Scale | Best Threshold | Best F1 | P | R | 95% CI |
|-------|----------------|---------|------|------|--------|
| Small (256px) | 5/5 | 0.429 | 0.324 | 0.632 | [0.14, 0.64] |
| **Medium (512px)** | **4/5** | **0.488** | 0.455 | 0.526 | [0.14, 0.73] |
| Large (1024px) | 3/5 | 0.357 | 0.556 | 0.263 | [0.07, 0.59] |

---

## Multi-Scale Results

### Strategy Comparison (Top 10 by F1)

| Rank | Strategy | Config | F1 | P | R | 95% CI |
|------|----------|--------|-----|------|------|--------|
| 1 | **Scale Confirmation** | min_scales_3 | **0.611** | 0.647 | 0.579 | [0.28, 0.91] |
| 2 | F1-Weighted | within_1_thresh_0.6 | 0.600 | 0.571 | 0.632 | [0.30, 0.83] |
| 3 | F1-Weighted | within_1_thresh_0.5 | 0.566 | 0.441 | 0.789 | [0.25, 0.83] |
| 4 | F1-Weighted | within_2_thresh_0.5 | 0.542 | 0.448 | 0.684 | [0.27, 0.74] |
| 5 | Fine-to-Coarse | medium_large_conf5_unc2-4 | 0.533 | 0.462 | 0.632 | [0.22, 0.78] |
| 5 | Two-Stage | within_5_cross_1 | 0.533 | 0.390 | 0.842 | [0.19, 0.76] |
| 7 | F1-Weighted | within_1_thresh_0.4 | 0.522 | 0.360 | 0.947 | [0.20, 0.80] |
| 8 | Two-Stage | within_1_cross_3 | 0.500 | 0.529 | 0.474 | [0.15, 0.80] |
| 9 | Two-Stage | within_3_cross_2 | 0.490 | 0.400 | 0.632 | [0.25, 0.65] |
| 10 | Single Medium | 4/5 | 0.488 | 0.455 | 0.526 | [0.14, 0.73] |

### Best Multi-Scale Strategy: Scale Confirmation (3/3)

The winning strategy requires detection by all three scales:

- **TP**: 11 (58% of ground truth detected)
- **FP**: 6 
- **FN**: 8
- **Precision**: 0.647
- **Recall**: 0.579
- **F1**: 0.611

**Why it works**: 
1. True positives are more likely to be detected consistently across scales
2. False positives tend to be scale-specific (different hallucinations at each scale)
3. Requiring unanimous agreement filters out most noise

### Fine-to-Coarse Performance

The simulated fine-to-coarse pipeline showed modest results:

| Config | F1 | P | R | Promotion Rate |
|--------|-----|------|------|----------------|
| medium→large, conf5, unc2-4 | 0.533 | 0.462 | 0.632 | 20% |
| medium→large, conf4, unc2-3 | 0.481 | 0.371 | 0.684 | 16% |
| small→large, conf5, unc2-4 | 0.486 | 0.333 | 0.895 | 10% |
| small→medium, conf5, unc2-4 | 0.340 | 0.213 | 0.842 | 26% |

**Key limitation**: With 1024px recall at only 37%, the large-tile context cannot confirm most true positives. The fine-to-coarse approach requires a context scale with reasonable recall, which 1024px lacks in this configuration.

---

## Scale Agreement Analysis

### Detection Overlap

| Pattern | Count | % of GT | Interpretation |
|---------|-------|---------|----------------|
| All three scales | 5 | 26% | High-confidence detections |
| Exactly two scales | 10 | 53% | Moderate confidence |
| Only one scale | 4 | 21% | Difficult cases |
| Missed by all | 0 | 0% | Excellent combined coverage |

### Scale-Specific Patterns

| Pattern | Count | Interpretation |
|---------|-------|----------------|
| Small only | 3 | Small catches things others miss |
| Medium only | 1 | Rare |
| Large only | 0 | Large never uniquely detects |
| Small + Medium only | 8 | Most common two-scale pattern |
| Small + Large only | 1 | Rare |
| Medium + Large only | 1 | Rare |

**Key insight**: Small tiles provide unique coverage (3 mounds detected only by small), while large tiles provide no unique coverage. The small + medium combination captures 8 mounds that large misses entirely.

---

## Error Correlation Analysis

| Scale Pair | Correlation | Interpretation |
|------------|-------------|----------------|
| Small-Medium | -0.177 | Slightly complementary |
| Small-Large | -0.094 | Independent |
| Medium-Large | +0.127 | Weakly similar |

**Overall interpretation**: **Independent**

The low/negative correlations validate the theoretical basis for multi-scale fusion. The scales make different errors, so combining them adds genuine information rather than redundant signals.

---

## Confidence Interval Analysis

### The Uncertainty Problem

With only 19 ground truth mounds, confidence intervals are necessarily wide:

| Strategy | F1 | CI Width | CI Range |
|----------|-----|----------|----------|
| Scale Confirmation (3/3) | 0.611 | 0.635 | [0.28, 0.91] |
| F1-Weighted (1, 0.6) | 0.600 | 0.530 | [0.30, 0.83] |
| Single Medium (4/5) | 0.488 | 0.588 | [0.14, 0.73] |

**Critical observation**: The best multi-scale CI [0.28, 0.91] includes the best single-scale point estimate (0.488), and vice versa. We cannot statistically distinguish multi-scale from single-scale performance with this sample size.

### What We Can and Cannot Claim

**Can claim**:
- Point estimates favour multi-scale (+0.12 F1)
- Error correlation is low, supporting theoretical basis
- Scale agreement patterns show complementary coverage
- No mounds missed by all scales (excellent combined recall ceiling)

**Cannot claim**:
- Multi-scale is definitively better than single-scale
- Any specific strategy is optimal
- Results will generalise to other maps/regions

---

## Recommendations

### For Paper 1 (Current Preregistration)

1. **Retain 512px single-scale** as the primary methodology
2. **Note multi-scale as promising future direction** with appropriate caveats
3. **Do not make confirmatory claims** about multi-scale superiority

### For Paper 2 (Future Work)

1. **Pursue multi-scale fusion** as exploratory analysis
2. **Prioritise**: Scale Confirmation (3/3) or F1-Weighted strategies
3. **Larger validation set**: Need 50+ ground truth mounds for meaningful CIs
4. **Consider 256px + 512px fusion** (skip 1024px given poor recall)
5. **Test on held-out maps** to assess generalisation

### Methodological Improvements

1. **Standardise deduplication**: Use two-stage clustering (within-pass, then across-pass) consistently
2. **Report all CIs**: Wide intervals are informative, not embarrassing
3. **Pre-specify multi-scale strategy** if including in confirmatory analysis

---

## Archived Outputs

| File | Description |
|------|-------------|
| `multiscale_analysis.json` | Full structured results |
| `multiscale_full_sweep.csv` | All configurations tested |
| `multiscale-voting-analysis.md` | Analysis methodology document |
| `pilot_results.json` | Single-scale pilot results (region-level pooling) |
| `pilot_summary.md` | Human-readable pilot summary |

**Analysis scripts**: 
- `analyze_pilot_results.py` v1.2.0 (region-level pooling)
- `analyze_multiscale.py` (matching methodology)

---

## Appendix: Raw Detection Counts by Scale

### Small (256px)
- 1/5: 574 detections (18 TP, 556 FP)
- 2/5: 181 detections (17 TP, 164 FP)
- 3/5: 110 detections (17 TP, 93 FP)
- 4/5: 63 detections (15 TP, 48 FP)
- 5/5: 37 detections (12 TP, 25 FP)

### Medium (512px)
- 1/5: 312 detections (18 TP, 294 FP)
- 2/5: 101 detections (15 TP, 86 FP)
- 3/5: 52 detections (13 TP, 39 FP)
- 4/5: 22 detections (10 TP, 12 FP)
- 5/5: 7 detections (6 TP, 1 FP)

### Large (1024px)
- 1/5: 194 detections (12 TP, 182 FP)
- 2/5: 24 detections (7 TP, 17 FP)
- 3/5: 9 detections (5 TP, 4 FP)
- 4/5: 5 detections (3 TP, 2 FP)
- 5/5: 1 detection (1 TP, 0 FP)
