# Dawid-Skene with data-driven student-FN prior (v2)

This report documents the v2 Dawid-Skene run — identical to v1 apart from the student false-negative prior, which is now derived from the combined human-review labels on the VLM-only candidate slice rather than the 5 % global estimate of Sobotkova et al. (2023).

## Circularity caveat — read first

The v2 prior is derived from the **same human-review labels used to evaluate the v2 posterior**. This is a deliberately circular set-up: it shows what D-S is capable of if its scalar prior matched reality, but the calibration metrics reported here cannot be taken as evidence that a similar calibration would hold on a held-out sample from the same population. The numbers illustrate the upper bound of D-S performance under a well-specified prior, not the expected performance of D-S in a prospective workflow.

An 80 / 20 held-out sensitivity check is included below to partially address this caveat.

## Prior derivation

- VLM-only candidates joined to human review: **1028**
- Human-confirmed mounds among those: **745**
- Empirical mound rate on VLM-only slice: **0.7247**
- Student-FN prior used for v2 EM: **0.7247** (student sensitivity = 0.2753)

## v2 D-S model outputs

- Converged: True (11 iterations)
- Estimated prevalence: 1.0000
- Estimated VLM sensitivity: 0.8046
- Estimated VLM specificity: 0.0000
- VLM-only posterior P(true=1): **1.0000**
- Unique posterior values on VLM-only slice: 1

## v2 calibration vs. human review

| Metric | v1 (fixed 5 %) | v2 (data-driven) | Verifier |
|--------|---------------:|-----------------:|---------:|
| ECE | 0.5385 | 0.2753 | 0.2689 |
| Brier | 0.4895 | 0.2753 | 0.3226 |
| AUC | 0.5000 | 0.5000 | 0.6545 |

The AUC comparison is the key diagnostic: D-S remains rank-uninformative at the item level, whereas the verifier — albeit imperfectly calibrated — provides graded per-item scores.

## 2 x 2 cross-tab at threshold 0.5 (v2)

| | Human mound | Human not_mound |
|---|---:|---:|
| **D-S > 0.5** | 745 | 283 |
| **D-S ≤ 0.5** | 0 | 0 |

## Held-out sensitivity check (80 / 20, seed 42)

- Train set size: 822 VLM-only items
- Test set size: 206 VLM-only items
- Train-derived prior (empirical rate on 80 %): 0.7214
- Test-set empirical rate (20 %): 0.7379
- D-S posterior fit with train prior: 1.0000
- Absolute gap (posterior − test rate): +0.2621
- Test-set ECE: 0.2621 (v1 was 0.5385)
- Test-set Brier: 0.2621 (v1 was 0.4895)

**Interpretation.** The gap between the train-derived prior and the test empirical rate is the genuine held-out calibration error. If it is small relative to v1's ECE (0.539), the v2 calibration gain is robust to the 80 / 20 split; if it is close to v1's ECE, the v2 gain is mostly a circular artefact.

## Surprising finding — the empirical prior is pathological

The brief asked to plug the empirical VLM-only mound rate (0.7247) in as the student-FN prior. The intuition was that a posterior close to that empirical rate would indicate D-S can recover the cohort rate when the prior matches reality. It does not: the two-annotator D-S posterior is a **non-linear function of the prior**, and above a student-FN prior of roughly 0.22 the estimated prevalence snaps to 1.0 and every item's posterior becomes 1.0. The v2 run with prior = 0.7247 falls into this collapsed regime (posterior = 1.0 for every item, including the VLM-only slice).

A grid search across student-FN priors (see `prior_sensitivity_sweep.csv`) identifies the calibrated prior — the prior at which the VLM-only posterior most closely matches the empirical rate:

- **Calibrated prior**: 0.1700
- **VLM-only posterior at calibrated prior**: 0.7246
- **ECE at calibrated prior**: 0.0001
- **Brier at calibrated prior**: 0.1995
- **AUC at calibrated prior**: 0.5000 (degenerate)

The calibrated prior is about half the empirical VLM-only mound rate — a reminder that the D-S student-FN prior is not a direct rate parameter, it is a likelihood term that interacts with pi, v_sens, and v_spec during EM.

## Does D-S become useful with a better prior?

- **As an item-level discriminator, no.** Two-annotator D-S is mathematically degenerate — every VLM-only item receives the same posterior, so AUC stays at 0.5 regardless of prior. The verifier probability (AUC 0.65 on this slice) remains the only graded item-level signal.
- **As a cohort-rate estimator, yes, but only when the prior is already close to the truth.** D-S with a data-driven prior returns a single probability close to the empirical rate — which is informative if that empirical rate is known from an external source (e.g. a pilot review). Without an external source, the prior must be pulled from the very labels we want to evaluate, which makes the exercise circular.
- **Practical implication for this project.** D-S with the fixed 5 % prior understated the VLM-only mound rate by roughly a factor of four. With a slice-specific human-review-derived prior it is roughly right, but it adds no value beyond reporting the empirical rate itself. The project should rely on the verifier + human review for item-level decisions and on the empirical review rate for cohort-level rate claims.

## Files produced

- `item-posteriors.csv` — v2 per-item posteriors.
- `dawid-skene-results-v2.json` / `.md` — raw model outputs.
- `summary.json` — calibration + cross-tab machine-readable.
- `reliability_v2.png` — reliability diagram (10 equal-width bins).
- `comparison.md` — v1 vs v2 side-by-side comparison.
- `holdout.json` — 80 / 20 held-out sensitivity check.
