# Verifier calibration crosstab (55-map image generalisation)

Evaluation of the Vision Language Model (VLM) verifier's probability output against per-candidate human-review labels on the 55-map image-generalisation VLM-only candidate set.

- Total candidates reviewed: **1028**
- Mounds (human-confirmed): **472**
- Non-mounds: **556**
- Mound prevalence in VLM-only set: **0.459**
- All candidates: buffer_metres = 50

## 1. Probability-binned calibration table

| Bin | Count | n_mound | n_not_mound | Mean predicted P | Empirical P(mound) | Gap |
|-----|-------|---------|-------------|------------------|--------------------|-----|
| [0.15, 0.30] | 243 | 44 | 199 | 0.192 | 0.181 | -0.010 |
| (0.30, 0.50] | 75 | 25 | 50 | 0.399 | 0.333 | -0.065 |
| (0.50, 0.70] | 13 | 5 | 8 | 0.692 | 0.385 | -0.308 |
| (0.70, 0.90] | 147 | 84 | 63 | 0.830 | 0.571 | -0.259 |
| (0.90, 0.95] | 180 | 111 | 69 | 0.950 | 0.617 | -0.333 |
| (0.99, 1.00] | 370 | 203 | 167 | 1.000 | 0.549 | -0.451 |

**Expected Calibration Error (ECE):** 0.2689

Positive gap (empirical > predicted) indicates the verifier is **under-confident** in that bin; negative gap indicates over-confidence.

## 2. Reliability diagram

See `reliability-diagram.png`. Points above the y=x line are under-confident bins.

## 3. ROC curve and AUC

- **AUC:** 0.6545 (95% bootstrap CI: 0.6217, 0.6867)
See `roc-curve.png`.

## 4. Precision-Recall curve

See `pr-curve.png`.

## 5. Threshold-sweep table (VLM-only set)

Precision and recall are measured within this slice only; they are not comparable to full-corpus F1. `precision_delta_vs_0_15` shows the absolute change from the current 0.15 threshold.

| Threshold | n_accepted | TP (mound) | FP (not_mound) | Precision | Precision delta vs 0.15 | Recall (within set) | F1 (within set) |
|-----------|------------|------------|----------------|-----------|-------------------------|---------------------|-----------------|
| 0.15 | 1028 | 472 | 556 | 0.459 | +0.000 | 1.000 | 0.629 |
| 0.20 | 961 | 465 | 496 | 0.484 | +0.025 | 0.985 | 0.649 |
| 0.30 | 798 | 432 | 366 | 0.541 | +0.082 | 0.915 | 0.680 |
| 0.50 | 711 | 403 | 308 | 0.567 | +0.108 | 0.854 | 0.681 |
| 0.70 | 708 | 403 | 305 | 0.569 | +0.110 | 0.854 | 0.683 |
| 0.90 | 553 | 316 | 237 | 0.571 | +0.112 | 0.669 | 0.617 |
| 0.95 | 550 | 314 | 236 | 0.571 | +0.112 | 0.665 | 0.614 |

## 6. Brier score

- **Overall Brier score:** 0.3226 (95% bootstrap CI: 0.2974, 0.3476)

### Per-symbol-type Brier score

| Symbol type | n | n_mound | Mean predicted P | Empirical P(mound) | Brier |
|-------------|---|---------|------------------|--------------------|-------|
| bench_mark_on_mound | 92 | 92 | 0.841 | 1.000 | 0.0838 |
| burial_mound | 338 | 338 | 0.848 | 1.000 | 0.0876 |
| not_mound | 556 | 0 | 0.625 | 0.000 | 0.5239 |
| settlement_mound | 13 | 13 | 0.869 | 1.000 | 0.0573 |
| trig_point_on_mound | 29 | 29 | 0.876 | 1.000 | 0.0784 |

## 7. Bootstrap confidence intervals (10,000 resamples, seed 42)

| Statistic | Point | 95% CI lo | 95% CI hi |
|-----------|-------|-----------|-----------|
| AUC | 0.6545 | 0.6217 | 0.6867 |
| Brier | 0.3226 | 0.2974 | 0.3476 |
| P(mound \| p ≤ 0.25) | 0.1739 | 0.1265 | 0.2241 |

## 8. Low-p deep dive (p ≤ 0.25)

- Candidates in tail: **230**
- Mounds in tail: **40**
- P(mound | p ≤ 0.25) = **0.1739** (bootstrap 95% CI: 0.1265, 0.2241)

### Symbol-type breakdown of mounds in the tail

| Symbol type | Count |
|-------------|-------|
| burial_mound | 30 |
| bench_mark_on_mound | 7 |
| trig_point_on_mound | 2 |
| settlement_mound | 1 |

### Top 5 maps by mound count in the tail

| Map | Mounds in tail |
|-----|----------------|
| K-35-077-2 | 5 |
| K-35-053-2 | 3 |
| K-35-067-4 | 3 |
| K-35-076-2 | 3 |
| K-35-062-4_Asenovgrad_4326 | 2 |

## Interpretation guide

- **Under-confidence hypothesis**: the spot-check of 4/4 low-p mounds suggested the verifier systematically underweights faint/low-contrast real mounds. See the deep-dive P(mound | p ≤ 0.25) and its CI.
- **Threshold choice**: precision rises monotonically with threshold; recall (within-set) falls. The choice depends on downstream use — archaeology prioritises recall at the cost of manual review, so the 0.15 accept threshold may still be preferred even if precision is low.
- **Per-class Brier**: large per-symbol Brier scores flag a subclass the verifier handles poorly (e.g. settlement_mound with n=13 may be noisy; burial_mound is the dominant positive class).
