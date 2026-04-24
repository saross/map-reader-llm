# Verifier calibration crosstab (55-map image generalisation)

Evaluation of the Vision Language Model (VLM) verifier's probability output against per-candidate human-review labels on the 55-map image-generalisation VLM-only candidate set.

- Total candidates reviewed: **630**
- Mounds (human-confirmed): **352**
- Non-mounds: **278**
- Mound prevalence in VLM-only set: **0.559**
- All candidates: buffer_metres = 50

## 1. Probability-binned calibration table

| Bin | Count | n_mound | n_not_mound | Mean predicted P | Empirical P(mound) | Gap |
|-----|-------|---------|-------------|------------------|--------------------|-----|
| [0.15, 0.30] | 222 | 47 | 175 | 0.193 | 0.212 | +0.019 |
| (0.30, 0.50] | 58 | 20 | 38 | 0.397 | 0.345 | -0.052 |
| (0.50, 0.70] | 7 | 4 | 3 | 0.671 | 0.571 | -0.100 |
| (0.70, 0.90] | 78 | 50 | 28 | 0.831 | 0.641 | -0.190 |
| (0.90, 0.95] | 110 | 99 | 11 | 0.950 | 0.900 | -0.050 |
| (0.99, 1.00] | 155 | 132 | 23 | 1.000 | 0.852 | -0.148 |

**Expected Calibration Error (ECE):** 0.0813

Positive gap (empirical > predicted) indicates the verifier is **under-confident** in that bin; negative gap indicates over-confidence.

## 2. Reliability diagram

See `reliability-diagram.png`. Points above the y=x line are under-confident bins.

## 3. ROC curve and AUC

- **AUC:** 0.8290 (95% bootstrap CI: 0.7957, 0.8604)
See `roc-curve.png`.

## 4. Precision-Recall curve

See `pr-curve.png`.

## 5. Threshold-sweep table (VLM-only set)

Precision and recall are measured within this slice only; they are not comparable to full-corpus F1. `precision_delta_vs_0_15` shows the absolute change from the current 0.15 threshold.

| Threshold | n_accepted | TP (mound) | FP (not_mound) | Precision | Precision delta vs 0.15 | Recall (within set) | F1 (within set) |
|-----------|------------|------------|----------------|-----------|-------------------------|---------------------|-----------------|
| 0.15 | 630 | 352 | 278 | 0.559 | +0.000 | 1.000 | 0.717 |
| 0.20 | 570 | 346 | 224 | 0.607 | +0.048 | 0.983 | 0.751 |
| 0.30 | 422 | 309 | 113 | 0.732 | +0.173 | 0.878 | 0.798 |
| 0.50 | 350 | 285 | 65 | 0.814 | +0.256 | 0.810 | 0.812 |
| 0.70 | 346 | 283 | 63 | 0.818 | +0.259 | 0.804 | 0.811 |
| 0.90 | 269 | 232 | 37 | 0.862 | +0.304 | 0.659 | 0.747 |
| 0.95 | 265 | 231 | 34 | 0.872 | +0.313 | 0.656 | 0.749 |

## 6. Brier score

- **Overall Brier score:** 0.1666 (95% bootstrap CI: 0.1450, 0.1887)

### Per-symbol-type Brier score

| Symbol type | n | n_mound | Mean predicted P | Empirical P(mound) | Brier |
|-------------|---|---------|------------------|--------------------|-------|
| bench_mark_on_mound | 70 | 70 | 0.836 | 1.000 | 0.0944 |
| burial_mound | 247 | 247 | 0.813 | 1.000 | 0.1173 |
| not_mound | 278 | 0 | 0.384 | 0.000 | 0.2362 |
| settlement_mound | 9 | 9 | 0.772 | 1.000 | 0.1403 |
| trig_point_on_mound | 26 | 26 | 0.837 | 1.000 | 0.0947 |

## 7. Bootstrap confidence intervals (10,000 resamples, seed 42)

| Statistic | Point | 95% CI lo | 95% CI hi |
|-----------|-------|-----------|-----------|
| AUC | 0.8290 | 0.7957 | 0.8604 |
| Brier | 0.1666 | 0.1450 | 0.1887 |
| P(mound \| p ≤ 0.25) | 0.2067 | 0.1531 | 0.2617 |

## 8. Low-p deep dive (p ≤ 0.25)

- Candidates in tail: **208**
- Mounds in tail: **43**
- P(mound | p ≤ 0.25) = **0.2067** (bootstrap 95% CI: 0.1531, 0.2617)

### Symbol-type breakdown of mounds in the tail

| Symbol type | Count |
|-------------|-------|
| burial_mound | 31 |
| bench_mark_on_mound | 8 |
| trig_point_on_mound | 3 |
| settlement_mound | 1 |

### Top 5 maps by mound count in the tail

| Map | Mounds in tail |
|-----|----------------|
| K-35-076-2 | 5 |
| K-35-063-1_Granit_4326 | 4 |
| K-35-077-2 | 4 |
| K-35-066-1 | 3 |
| K-35-054-1_Straldzha_4326 | 2 |

## Interpretation guide

- **Under-confidence hypothesis**: the spot-check of 4/4 low-p mounds suggested the verifier systematically underweights faint/low-contrast real mounds. See the deep-dive P(mound | p ≤ 0.25) and its CI.
- **Threshold choice**: precision rises monotonically with threshold; recall (within-set) falls. The choice depends on downstream use — archaeology prioritises recall at the cost of manual review, so the 0.15 accept threshold may still be preferred even if precision is low.
- **Per-class Brier**: large per-symbol Brier scores flag a subclass the verifier handles poorly (e.g. settlement_mound with n=13 may be noisy; burial_mound is the dominant positive class).
