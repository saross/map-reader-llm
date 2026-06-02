# Verifier calibration crosstab (55-map image generalisation)

Evaluation of the Vision Language Model (VLM) verifier's probability output against per-candidate human-review labels on the 55-map image-generalisation VLM-only candidate set.

- Total candidates reviewed: **585**
- Mounds (human-confirmed): **324**
- Non-mounds: **261**
- Mound prevalence in VLM-only set: **0.554**
- All candidates: buffer_metres = 50

## 1. Probability-binned calibration table

| Bin | Count | n_mound | n_not_mound | Mean predicted P | Empirical P(mound) | Gap |
|-----|-------|---------|-------------|------------------|--------------------|-----|
| [0.15, 0.30] | 190 | 35 | 155 | 0.189 | 0.184 | -0.004 |
| (0.30, 0.50] | 55 | 23 | 32 | 0.398 | 0.418 | +0.020 |
| (0.50, 0.70] | 3 | 0 | 3 | 0.667 | 0.000 | -0.667 |
| (0.70, 0.90] | 76 | 46 | 30 | 0.818 | 0.605 | -0.213 |
| (0.90, 0.95] | 95 | 81 | 14 | 0.950 | 0.853 | -0.097 |
| (0.99, 1.00] | 166 | 139 | 27 | 1.000 | 0.837 | -0.163 |

**Expected Calibration Error (ECE):** 0.0963

Positive gap (empirical > predicted) indicates the verifier is **under-confident** in that bin; negative gap indicates over-confidence.

## 2. Reliability diagram

See `reliability-diagram.png`. Points above the y=x line are under-confident bins.

## 3. ROC curve and AUC

- **AUC:** 0.8205 (95% bootstrap CI: 0.7845, 0.8544)
See `roc-curve.png`.

## 4. Precision-Recall curve

See `pr-curve.png`.

## 5. Threshold-sweep table (VLM-only set)

Precision and recall are measured within this slice only; they are not comparable to full-corpus F1. `precision_delta_vs_0_15` shows the absolute change from the current 0.15 threshold.

| Threshold | n_accepted | TP (mound) | FP (not_mound) | Precision | Precision delta vs 0.15 | Recall (within set) | F1 (within set) |
|-----------|------------|------------|----------------|-----------|-------------------------|---------------------|-----------------|
| 0.15 | 585 | 324 | 261 | 0.554 | +0.000 | 1.000 | 0.713 |
| 0.20 | 521 | 317 | 204 | 0.608 | +0.055 | 0.978 | 0.750 |
| 0.30 | 405 | 291 | 114 | 0.719 | +0.165 | 0.898 | 0.798 |
| 0.50 | 340 | 266 | 74 | 0.782 | +0.229 | 0.821 | 0.801 |
| 0.70 | 338 | 266 | 72 | 0.787 | +0.233 | 0.821 | 0.804 |
| 0.90 | 261 | 220 | 41 | 0.843 | +0.289 | 0.679 | 0.752 |
| 0.95 | 261 | 220 | 41 | 0.843 | +0.289 | 0.679 | 0.752 |

## 6. Brier score

- **Overall Brier score:** 0.1781 (95% bootstrap CI: 0.1541, 0.2026)

### Per-symbol-type Brier score

| Symbol type | n | n_mound | Mean predicted P | Empirical P(mound) | Brier |
|-------------|---|---------|------------------|--------------------|-------|
| bench_mark_on_mound | 68 | 68 | 0.837 | 1.000 | 0.0907 |
| burial_mound | 223 | 223 | 0.832 | 1.000 | 0.1045 |
| not_mound | 261 | 0 | 0.415 | 0.000 | 0.2735 |
| settlement_mound | 10 | 10 | 0.835 | 1.000 | 0.0818 |
| trig_point_on_mound | 23 | 23 | 0.828 | 1.000 | 0.1088 |

## 7. Bootstrap confidence intervals (10,000 resamples, seed 42)

| Statistic | Point | 95% CI lo | 95% CI hi |
|-----------|-------|-----------|-----------|
| AUC | 0.8205 | 0.7845 | 0.8544 |
| Brier | 0.1781 | 0.1541 | 0.2026 |
| P(mound \| p ≤ 0.25) | 0.1833 | 0.1279 | 0.2419 |

## 8. Low-p deep dive (p ≤ 0.25)

- Candidates in tail: **180**
- Mounds in tail: **33**
- P(mound | p ≤ 0.25) = **0.1833** (bootstrap 95% CI: 0.1279, 0.2419)

### Symbol-type breakdown of mounds in the tail

| Symbol type | Count |
|-------------|-------|
| burial_mound | 24 |
| bench_mark_on_mound | 6 |
| trig_point_on_mound | 3 |

### Top 5 maps by mound count in the tail

| Map | Mounds in tail |
|-----|----------------|
| K-35-065-1_Radetski_4326 | 3 |
| K-35-051-3 | 2 |
| K-35-063-1_Granit_4326 | 2 |
| K-35-064-1_Sredets_4326 | 2 |
| K-35-064-3_Dimitrovgrad_4326 | 2 |

## Interpretation guide

- **Under-confidence hypothesis**: the spot-check of 4/4 low-p mounds suggested the verifier systematically underweights faint/low-contrast real mounds. See the deep-dive P(mound | p ≤ 0.25) and its CI.
- **Threshold choice**: precision rises monotonically with threshold; recall (within-set) falls. The choice depends on downstream use — archaeology prioritises recall at the cost of manual review, so the 0.15 accept threshold may still be preferred even if precision is low.
- **Per-class Brier**: large per-symbol Brier scores flag a subclass the verifier handles poorly (e.g. settlement_mound with n=13 may be noisy; burial_mound is the dominant positive class).
