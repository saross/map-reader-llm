# Multi-Scale Voting Analysis: Summary

Generated: 2026-01-07T11:29:14.452473+00:00

## Executive Summary

**Best Single-Scale**: medium at 4_of_5 (F1=0.488)
**Best Multi-Scale**: scale_confirmation at min_scales_3 (F1=0.611)
**Improvement**: +0.123
**Recommendation**: pursue

---

## Single-Scale Baselines

### Small (256px)

| Threshold | Precision | Recall | F1 | 95% CI |
|-----------|-----------|--------|------|--------|
| 1_of_5 | 0.031 | 0.947 | 0.061 | [0.018-0.111] |
| 2_of_5 | 0.094 | 0.895 | 0.170 | [0.056-0.284] |
| 3_of_5 | 0.155 | 0.895 | 0.264 | [0.089-0.433] |
| 4_of_5 | 0.238 | 0.789 | 0.366 | [0.143-0.563] |
| 5_of_5 | 0.324 | 0.632 | 0.429 | [0.136-0.640] |

### Medium (512px)

| Threshold | Precision | Recall | F1 | 95% CI |
|-----------|-----------|--------|------|--------|
| 1_of_5 | 0.058 | 0.947 | 0.109 | [0.033-0.207] |
| 2_of_5 | 0.149 | 0.789 | 0.250 | [0.088-0.456] |
| 3_of_5 | 0.250 | 0.684 | 0.366 | [0.162-0.566] |
| 4_of_5 | 0.455 | 0.526 | 0.488 | [0.143-0.731] |
| 5_of_5 | 0.857 | 0.316 | 0.462 | [0.000-0.629] |

### Large (1024px)

| Threshold | Precision | Recall | F1 | 95% CI |
|-----------|-----------|--------|------|--------|
| 1_of_5 | 0.062 | 0.632 | 0.113 | [0.028-0.226] |
| 2_of_5 | 0.292 | 0.368 | 0.326 | [0.118-0.424] |
| 3_of_5 | 0.556 | 0.263 | 0.357 | [0.069-0.588] |
| 4_of_5 | 0.600 | 0.158 | 0.250 | [0.000-0.545] |
| 5_of_5 | 1.000 | 0.053 | 0.100 | [0.000-0.286] |

---

## Multi-Scale Strategy Comparison

Best configuration per strategy:

| Strategy | Config | Precision | Recall | F1 | 95% CI |
|----------|--------|-----------|--------|------|--------|
| two_stage | within_5_cross_1 | 0.390 | 0.842 | 0.533 | [0.190-0.762] |
| scale_confirmation | min_scales_3 | 0.647 | 0.579 | 0.611 | [0.278-0.913] |
| confidence_fusion | max_0.7 | 0.240 | 0.947 | 0.383 | [0.138-0.598] |
| cascaded | conf_5_unc_3-4 | 0.304 | 0.895 | 0.453 | [0.171-0.710] |
| unanimous | within_1 | 0.529 | 0.474 | 0.500 | [0.154-0.800] |
| pr_optimised | gen_medium_filt_large_t2 | 1.000 | 0.316 | 0.480 | [0.000-0.895] |
| f1_weighted | within_1_thresh_0.6 | 0.571 | 0.632 | 0.600 | [0.296-0.826] |
| fine_to_coarse | medium_large_conf5_unc2-4 | 0.462 | 0.632 | 0.533 | [0.216-0.784] |

---

## Fine-to-Coarse Pipeline Analysis

| Config | Stage1 Conf | Stage2 Promoted | Stage2 Rejected | Promotion Rate |
|--------|-------------|-----------------|-----------------|----------------|
| medium_large_conf5_unc2-4 | 7 | 19 | 75 | 20.21% |
| medium_large_conf4_unc2-3 | 22 | 13 | 66 | 16.46% |
| medium_large_conf4_unc1-3 | 22 | 26 | 264 | 8.97% |
| small_large_conf5_unc2-4 | 37 | 14 | 130 | 9.72% |
| small_large_conf4_unc2-3 | 63 | 9 | 109 | 7.63% |
| small_medium_conf5_unc2-4 | 37 | 38 | 106 | 26.39% |
| small_medium_conf4_unc2-3 | 63 | 27 | 91 | 22.88% |

---

## Scale Agreement Analysis

- Detected by all 3 scales: 5 (26.3%)
- Detected by exactly 2 scales: 10 (52.6%)
- Detected by only 1 scale: 4 (21.1%)
- Missed by all scales: 0 (0.0%)

---

## Error Correlation

- Small-Medium FN correlation: -0.177
- Small-Large FN correlation: -0.094
- Medium-Large FN correlation: 0.127
- Interpretation: independent
