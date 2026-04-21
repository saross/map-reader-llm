# Dawid-Skene v1 (fixed 5 % prior) vs v2 (data-driven prior)

Side-by-side comparison of the two D-S runs on the 55-map
image-generalisation VLM-only candidate slice. Everything
other than the student false-negative prior is identical
between the two runs.

## Prior provenance

- **v1 student-FN prior**: 0.05 (fixed, Sobotkova et al. 2023).
- **v2 student-FN prior**: 0.7247 (= empirical mound rate on VLM-only slice: 745/1028).

## Posterior comparison

| Quantity | v1 (fixed 5 %) | v2 (data-driven) |
|----------|---------------:|-----------------:|
| VLM-only posterior P(true=1 \| s=0, v=1) | 0.1862 | 1.0000 |
| Estimated prevalence | 0.8557 | 1.0000 |
| Estimated VLM sensitivity | 0.7716 | 0.8046 |
| Estimated VLM specificity | 0.0000 | 0.0000 |
| Iterations to convergence | 11 | 11 |

## Calibration against human review (VLM-only slice only)

| Metric | v1 | v2 | Change |
|--------|---:|---:|-------:|
| ECE (lower is better) | 0.5385 | 0.2753 | -0.2632 |
| Brier (lower is better) | 0.4895 | 0.2753 | -0.2142 |
| AUC (higher is better) | 0.5000 | 0.5000 | +0.0000 |

## 2 x 2 cross-tab at threshold 0.5

### v1 (fixed 5 % prior)

| | Human mound | Human not_mound |
|---|---:|---:|
| **D-S > 0.5** | 0 | 0 |
| **D-S ≤ 0.5** | 745 | 283 |

### v2 (data-driven prior)

| | Human mound | Human not_mound |
|---|---:|---:|
| **D-S > 0.5** | 745 | 283 |
| **D-S ≤ 0.5** | 0 | 0 |

- **v1**: precision = n/a, recall = 0.0000, F1 = n/a
- **v2**: precision = 0.7247081712062257, recall = 1.0000, F1 = 0.8403835307388606

## Best-calibrated-prior variant (grid search)

The D-S posterior is a non-linear function of the student-FN prior — feeding in the empirical rate (0.7247) does **not** produce a posterior equal to the empirical rate. A grid search across prior values identifies the prior at which the VLM-only posterior is closest to the empirical rate.

| Quantity | v2 (empirical prior 0.725) | v2 (calibrated prior) |
|----------|--------------------------:|----------------------:|
| Student-FN prior | 0.7247 | 0.1700 |
| VLM-only posterior | 1.0000 | 0.7246 |
| ECE | 0.2753 | 0.0001 |
| Brier | 0.2753 | 0.1995 |
| AUC | 0.5000 | 0.5000 |
| 2x2 @ 0.5 TP/FP/FN/TN | 745/283/0/0 | 745/283/0/0 |

## Prior sensitivity sweep

Selected rows from the full sweep (`prior_sensitivity_sweep.csv`):

| Student-FN prior | pi (est.) | VLM sens | VLM spec | VLM-only posterior | |posterior − empirical| |
|-----------------:|----------:|---------:|---------:|-------------------:|-----------------------:|
| 0.0500 | 0.8557 | 0.7716 | 0.0000 | 0.1862 | 0.5385 |
| 0.0800 | 0.8772 | 0.7772 | 0.0000 | 0.3076 | 0.4171 |
| 0.1000 | 0.8924 | 0.7810 | 0.0000 | 0.3931 | 0.3316 |
| 0.1100 | 0.9002 | 0.7829 | 0.0000 | 0.4373 | 0.2874 |
| 0.1200 | 0.9082 | 0.7848 | 0.0000 | 0.4824 | 0.2423 |
| 0.1300 | 0.9164 | 0.7868 | 0.0000 | 0.5287 | 0.1960 |
| 0.1400 | 0.9248 | 0.7887 | 0.0000 | 0.5759 | 0.1488 |
| 0.1500 | 0.9334 | 0.7906 | 0.0000 | 0.6243 | 0.1004 |
| 0.1600 | 0.9422 | 0.7926 | 0.0000 | 0.6739 | 0.0508 |
| 0.1700 | 0.9512 | 0.7946 | 0.0000 | 0.7246 | 0.0001 |
| 0.1800 | 0.9604 | 0.7965 | 0.0000 | 0.7766 | 0.0519 |
| 0.1900 | 0.9698 | 0.7985 | 0.0000 | 0.8299 | 0.1052 |
| 0.2000 | 0.9795 | 0.8005 | 0.0000 | 0.8845 | 0.1598 |
| 0.2200 | 0.9977 | 0.8041 | 0.0000 | 0.9870 | 0.2622 |
| 0.2500 | 1.0000 | 0.8046 | 0.0000 | 1.0000 | 0.2753 |
| 0.3000 | 1.0000 | 0.8046 | 0.0000 | 1.0000 | 0.2753 |
| 0.4000 | 1.0000 | 0.8046 | 0.0000 | 1.0000 | 0.2753 |
| 0.5000 | 1.0000 | 0.8046 | 0.0000 | 1.0000 | 0.2753 |
| 0.6000 | 1.0000 | 0.8046 | 0.0000 | 1.0000 | 0.2753 |
| 0.7000 | 1.0000 | 0.8046 | 0.0000 | 1.0000 | 0.2753 |
| 0.7247 | 1.0000 | 0.8046 | 0.0000 | 1.0000 | 0.2753 |
| 0.8000 | 1.0000 | 0.8046 | 0.0000 | 1.0000 | 0.2753 |
| 0.9000 | 1.0000 | 0.8046 | 0.0000 | 1.0000 | 0.2753 |
| 0.9500 | 1.0000 | 0.8046 | 0.0000 | 1.0000 | 0.2753 |

## Interpretation

- **AUC is unchanged (0.5) because the D-S posterior remains degenerate under a 2-annotator design.** All 1,028 VLM-only items share the same posterior — so the posterior carries zero rank information about individual candidates regardless of the prior.
- **Calibration (ECE / Brier) is what the prior controls, but non-linearly.** Feeding in the empirical mound rate (0.725) does not produce a posterior equal to 0.725. Above a student-FN prior of roughly 0.22 the EM snaps into a degenerate regime where the estimated prevalence pi collapses to 1 and every item posterior becomes 1.0.
- **The v2 (prior = 0.725) run is therefore pathological in the opposite direction to v1.** v1 under-predicted mounds; v2 over-predicts them. Neither is useful as a calibrated probability. The only genuine reduction in miscalibration comes from the grid-searched prior near 0.17, which produces a VLM-only posterior near 0.725 — numerically matching the empirical rate by construction.
- **The 2 x 2 cross-tab at 0.5 is not meaningful here.** Because the posterior is degenerate, the cell counts are deterministic given whether the single posterior is above or below 0.5. Precision and recall reflect prevalence, not model skill.
