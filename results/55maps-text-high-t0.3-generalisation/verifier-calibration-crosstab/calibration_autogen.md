# Verifier calibration crosstab (55-map image generalisation)

Evaluation of the Vision Language Model (VLM) verifier's probability output against per-candidate human-review labels on the 55-map image-generalisation VLM-only candidate set.

- Total candidates reviewed: **692**
- Mounds (human-confirmed): **395**
- Non-mounds: **297**
- Mound prevalence in VLM-only set: **0.571**
- All candidates: buffer_metres = 50

## 1. Probability-binned calibration table

| Bin | Count | n_mound | n_not_mound | Mean predicted P | Empirical P(mound) | Gap |
|-----|-------|---------|-------------|------------------|--------------------|-----|
| [0.15, 0.30] | 242 | 44 | 198 | 0.196 | 0.182 | -0.014 |
| (0.30, 0.50] | 46 | 24 | 22 | 0.401 | 0.522 | +0.121 |
| (0.50, 0.70] | 7 | 3 | 4 | 0.657 | 0.429 | -0.229 |
| (0.70, 0.90] | 90 | 59 | 31 | 0.827 | 0.656 | -0.171 |
| (0.90, 0.95] | 117 | 99 | 18 | 0.950 | 0.846 | -0.104 |
| (0.99, 1.00] | 190 | 166 | 24 | 1.000 | 0.874 | -0.126 |

**Expected Calibration Error (ECE):** 0.0898

Positive gap (empirical > predicted) indicates the verifier is **under-confident** in that bin; negative gap indicates over-confidence.

## 2. Reliability diagram

See `reliability-diagram.png`. Points above the y=x line are under-confident bins.

## 3. ROC curve and AUC

- **AUC:** 0.8374 (95% bootstrap CI: 0.8061, 0.8677)
See `roc-curve.png`.

## 4. Precision-Recall curve

See `pr-curve.png`.

## 5. Threshold-sweep table (VLM-only set)

Precision and recall are measured within this slice only; they are not comparable to full-corpus F1. `precision_delta_vs_0_15` shows the absolute change from the current 0.15 threshold.

| Threshold | n_accepted | TP (mound) | FP (not_mound) | Precision | Precision delta vs 0.15 | Recall (within set) | F1 (within set) |
|-----------|------------|------------|----------------|-----------|-------------------------|---------------------|-----------------|
| 0.15 | 692 | 395 | 297 | 0.571 | +0.000 | 1.000 | 0.727 |
| 0.20 | 631 | 389 | 242 | 0.616 | +0.046 | 0.985 | 0.758 |
| 0.30 | 471 | 355 | 116 | 0.754 | +0.183 | 0.899 | 0.820 |
| 0.50 | 405 | 327 | 78 | 0.807 | +0.237 | 0.828 | 0.818 |
| 0.70 | 399 | 325 | 74 | 0.815 | +0.244 | 0.823 | 0.819 |
| 0.90 | 308 | 266 | 42 | 0.864 | +0.293 | 0.673 | 0.757 |
| 0.95 | 307 | 265 | 42 | 0.863 | +0.292 | 0.671 | 0.755 |

## 6. Brier score

- **Overall Brier score:** 0.1641 (95% bootstrap CI: 0.1430, 0.1860)

### Per-symbol-type Brier score

| Symbol type | n | n_mound | Mean predicted P | Empirical P(mound) | Brier |
|-------------|---|---------|------------------|--------------------|-------|
| bench_mark_on_mound | 81 | 81 | 0.822 | 1.000 | 0.1019 |
| burial_mound | 275 | 275 | 0.829 | 1.000 | 0.1060 |
| not_mound | 297 | 0 | 0.393 | 0.000 | 0.2505 |
| settlement_mound | 11 | 11 | 0.832 | 1.000 | 0.0893 |
| trig_point_on_mound | 28 | 28 | 0.921 | 1.000 | 0.0288 |

## 7. Bootstrap confidence intervals (10,000 resamples, seed 42)

| Statistic | Point | 95% CI lo | 95% CI hi |
|-----------|-------|-----------|-----------|
| AUC | 0.8374 | 0.8061 | 0.8677 |
| Brier | 0.1641 | 0.1430 | 0.1860 |
| P(mound \| p ≤ 0.25) | 0.1810 | 0.1312 | 0.2335 |

## 8. Low-p deep dive (p ≤ 0.25)

- Candidates in tail: **221**
- Mounds in tail: **40**
- P(mound | p ≤ 0.25) = **0.1810** (bootstrap 95% CI: 0.1312, 0.2335)

### Symbol-type breakdown of mounds in the tail

| Symbol type | Count |
|-------------|-------|
| burial_mound | 32 |
| bench_mark_on_mound | 7 |
| trig_point_on_mound | 1 |

### Top 5 maps by mound count in the tail

| Map | Mounds in tail |
|-----|----------------|
| K-35-076-2 | 6 |
| K-35-064-2_Radnevo_4326 | 3 |
| K-35-053-2 | 2 |
| K-35-054-1_Straldzha_4326 | 2 |
| K-35-054-2_Atolov_4326 | 2 |

## Interpretation guide

- **Under-confidence hypothesis**: the spot-check of 4/4 low-p mounds suggested the verifier systematically underweights faint/low-contrast real mounds. See the deep-dive P(mound | p ≤ 0.25) and its CI.
- **Threshold choice**: precision rises monotonically with threshold; recall (within-set) falls. The choice depends on downstream use — archaeology prioritises recall at the cost of manual review, so the 0.15 accept threshold may still be preferred even if precision is low.
- **Per-class Brier**: large per-symbol Brier scores flag a subclass the verifier handles poorly (e.g. settlement_mound with n=13 may be noisy; burial_mound is the dominant positive class).
