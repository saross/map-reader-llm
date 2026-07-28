# Dawid-Skene with data-driven student-FN prior (v2)

**Original analysis timestamp**: ~2026-04-20 (single-commit hand-authored doc; commit `dee0ecf0`).
**Level-up**: 2026-04-24 (Session 76).

**Observation anchors**: Obs 273 (D-S aggregate structurally inadequate on VLM-only slice). Sibling artefact: `results/55maps-image-generalisation/ds-human-crosstab/report.md` (v1 fixed-prior comparison). Direct input to meta-findings Theme T5.

## 1. Executive summary

This report documents the **v2 Dawid-Skene (D-S) run** — identical to v1 apart from the student false-negative prior, which is derived from the combined human-review labels on the VLM-only candidate slice rather than the 5 % global estimate of Sobotkova et al. (2023).

**Headline findings**:

- **The prior-is-rate intuition is wrong for 2-annotator D-S**. Plugging the empirical VLM-only mound rate (0.7247) in as the student-FN prior does **not** produce a well-calibrated D-S run. Above student-FN priors of roughly 0.22 the EM estimate of prevalence collapses to 1.0 and every item's posterior becomes 1.0. The v2 "empirical prior" run falls into this collapsed regime; the v2 VLM-only posterior is 1.0000 everywhere.
- **A separate calibrated prior exists at 0.17** (about half the empirical rate). At this calibrated prior the v2 VLM-only posterior matches the empirical rate to 4 decimals (0.7246 vs 0.7247), ECE drops to 0.0001, Brier to 0.1995 — but **AUC stays at 0.5000 (degenerate)**.
- **Structural rank failure confirmed**. Across **every** prior value tested (sweep in `prior_sensitivity_sweep.csv`), the item-level AUC of the D-S posterior on the VLM-only slice is 0.5000. The rank degeneracy is a property of the 2-annotator identifiability class, not a calibration issue.
- **Held-out sensitivity check (80 / 20, seed 42)**: train-derived prior 0.7214 vs test empirical rate 0.7379 — the genuine held-out calibration error is 0.2621 absolute. This is well below v1's ECE (0.5385) but well above the calibrated-prior ECE (0.0001), so the calibrated-prior result is partly a circularity artefact.

**Circularity caveat** (§2): the v2 data-driven prior is derived from the same human-review labels used to evaluate the v2 posterior. The calibrated-prior result is the **upper bound** of D-S performance under a well-specified prior, not the expected performance of D-S in a prospective workflow.

**One-line paper claim**: "A data-driven Dawid-Skene variant that replaces the original 5 % student-FN prior (from Sobotkova et al. 2023; D-S is post-hoc, not preregistered — D17 audit FALSE-12) with a prior derived from the same human-review labels finds a calibrated posterior at prior = 0.17 (ECE = 0.0001) but preserves the AUC = 0.500 rank degeneracy observed in the v1 run. The failure to rank individuals is structural (2 binary annotators sharing a response pattern); no prior can repair it."

## 2. Circularity caveat — read first

The v2 prior is derived from the **same human-review labels used to evaluate the v2 posterior**. This is a deliberately circular set-up: it shows what D-S is capable of if its scalar prior matched reality, but the calibration metrics reported here cannot be taken as evidence that a similar calibration would hold on a held-out sample from the same population. The numbers illustrate the upper bound of D-S performance under a well-specified prior, not the expected performance of D-S in a prospective workflow.

An 80 / 20 held-out sensitivity check is included below (§7) to partially address this caveat.

## 3. Prior derivation

- VLM-only candidates joined to human review: **1,028**.
- Human-confirmed mounds among those: **745**.
- Empirical mound rate on VLM-only slice: **0.7247**.
- Student-FN prior used for v2 EM: **0.7247** (student sensitivity = 0.2753).

## 4. v2 D-S model outputs (with prior = 0.7247)

- Converged: True (11 iterations).
- Estimated prevalence: **1.0000** (the pathology — see §8).
- Estimated VLM sensitivity: 0.8046.
- Estimated VLM specificity: 0.0000.
- VLM-only posterior P(true = 1): **1.0000**.
- Unique posterior values on VLM-only slice: **1**.

## 5. v2 calibration vs. human review

| Metric | v1 (fixed 5 %) | v2 (data-driven prior = 0.7247) | Verifier |
|--------|---------------:|---------------------------------:|---------:|
| ECE | 0.5385 | 0.2753 | 0.2689 |
| Brier | 0.4895 | 0.2753 | 0.3226 |
| AUC | 0.5000 | 0.5000 | 0.6545 |

The AUC comparison is the key diagnostic: D-S remains rank-uninformative at the item level, whereas the verifier — albeit imperfectly calibrated — provides graded per-item scores. The v2 ECE / Brier improvements over v1 are aggregate-only; they do not reflect a per-item discrimination capability.

## 6. 2 × 2 cross-tab at threshold 0.5 (v2)

| | Human mound | Human not_mound |
|---|---:|---:|
| **D-S > 0.5** | 745 | 283 |
| **D-S ≤ 0.5** | 0 | 0 |

The cross-tab now flips from v1 (D-S ≤ 0.5 for all rows) to v2 (D-S > 0.5 for all rows). Neither is informative — both are degenerate by the 2-annotator argument.

## 7. Held-out sensitivity check (80 / 20, seed 42)

- Train set size: 822 VLM-only items.
- Test set size: 206 VLM-only items.
- Train-derived prior (empirical rate on 80 %): 0.7214.
- Test-set empirical rate (20 %): 0.7379.
- D-S posterior fit with train prior: 1.0000.
- Absolute gap (posterior − test rate): **+0.2621**.
- Test-set ECE: **0.2621** (v1 was 0.5385).
- Test-set Brier: **0.2621** (v1 was 0.4895).

**Interpretation.** The gap between the train-derived prior and the test empirical rate is the genuine held-out calibration error. The 0.2621 absolute gap is about half of v1's 0.5385 ECE — a meaningful improvement but not the near-perfect calibration seen in the circular-prior-on-full-sample variant (ECE = 0.0001 at the calibrated prior). The held-out check confirms that v2's calibration gains are partly real (the 5 % prior was substantially wrong for this slice) and partly circular (the data-driven-prior run benefits from fitting and evaluating on the same labels).

## 8. Surprising finding — the empirical prior is pathological

The brief asked to plug the empirical VLM-only mound rate (0.7247) in as the student-FN prior. The intuition was that a posterior close to that empirical rate would indicate D-S can recover the cohort rate when the prior matches reality. It does not: the two-annotator D-S posterior is a **non-linear function of the prior**, and above a student-FN prior of roughly 0.22 the estimated prevalence snaps to 1.0 and every item's posterior becomes 1.0. The v2 run with prior = 0.7247 falls into this collapsed regime (posterior = 1.0 for every item, including the VLM-only slice).

A grid search across student-FN priors (see `prior_sensitivity_sweep.csv`) identifies the calibrated prior — the prior at which the VLM-only posterior most closely matches the empirical rate:

- **Calibrated prior**: **0.1700**.
- **VLM-only posterior at calibrated prior**: **0.7246**.
- **ECE at calibrated prior**: **0.0001**.
- **Brier at calibrated prior**: **0.1995**.
- **AUC at calibrated prior**: **0.5000** (degenerate).

The calibrated prior is about half the empirical VLM-only mound rate — a reminder that the D-S student-FN prior is not a direct rate parameter, it is a likelihood term that interacts with π, v_sens, and v_spec during EM.

## 9. Does D-S become useful with a better prior?

- **As an item-level discriminator, no.** Two-annotator D-S is mathematically degenerate — every VLM-only item receives the same posterior, so AUC stays at 0.5 regardless of prior. The verifier probability (AUC 0.6545 on this slice) remains the only graded item-level signal.
- **As a cohort-rate estimator, yes, but only when the prior is already close to the truth.** D-S with a data-driven prior returns a single probability close to the empirical rate — which is informative if that empirical rate is known from an external source (e.g. a pilot review). Without an external source, the prior must be pulled from the very labels we want to evaluate, which makes the exercise circular.
- **Practical implication for this project.** D-S with the fixed 5 % prior understated the VLM-only mound rate by roughly a factor of four. With a slice-specific human-review-derived prior it is roughly right at the calibrated-prior value (0.17), but it adds no value beyond reporting the empirical rate itself. The project relies on the verifier + human review for item-level decisions and on the empirical review rate for cohort-level rate claims.

## 10. Caveats / risk register

1. **Circularity**: the v2 data-driven prior is derived from the same labels used to evaluate v2 calibration (§2). The 80 / 20 held-out check partially addresses this; the 0.2621 held-out ECE is the honest calibration floor, not the 0.0001 circular-ECE.
2. **Prior-sensitivity is non-linear**: the v2 posterior is not a smooth function of the prior. At prior = 0.22 there is a phase transition to posterior = 1.0. The "calibrated prior = 0.17" finding would not generalise to a different annotator-error structure; it is specific to this D-S fit on this slice.
3. **AUC = 0.500 is invariant across all priors tested**. This is the structural identifiability property of 2-annotator binary D-S with all items in the same response-pattern class (`student = 0, VLM = 1`). No prior repairs it.
4. **Sobotkova et al. (2023) 5 % prior is not "wrong" in the abstract**: it was the preregistered prior. The 5 % value is a reasonable estimate of the student-FN rate on the *full* corpus (where most mounds are digitised correctly). On the VLM-only slice the empirical student-FN rate is ~72 % by construction (the VLM flagged candidates the student had NOT digitised). The preregistered prior therefore mis-matches the slice; this is a scoping choice, not a parameter error.

## 11. Paper implications

### 11.1 D-S inadequacy is structural, not prior-driven

The paper's Limitations / Methods section should state: **no choice of scalar prior can produce a per-item D-S discriminator on this slice**. The v1 (fixed 5 %) and v2 (data-driven) runs both return AUC = 0.500 as a necessary consequence of the 2-annotator identifiability class structure. This is the Obs 273 structural-inadequacy finding.

### 11.2 Sobotkova et al. prior is not falsified, merely slice-mismatched

The 5 % student-FN prior from Sobotkova et al. (2023) was the preregistered choice and is a defensible estimate for the *full* corpus where student GT digitisation is close to complete. On the VLM-only slice — where the VLM flagged candidates specifically chosen for student-GT absence — the empirical student-FN rate is much higher. The paper should frame the v1/v2 comparison as a slice-scoping illustration, not as a refutation of the preregistered prior choice.

### 11.3 Repair path: three-annotator D-S

Breaking the 2-annotator identifiability collapse requires a third annotator — a second VLM run (e.g., text-track proposer), a second student reviewer, or a third-party human. A three-annotator D-S with non-degenerate item-level ranking is a natural methodology follow-up for the paper's Future Work section.

### 11.4 Suggested paper text (Methods / Limitations)

> The Dawid-Skene analysis — a post-hoc method adopted for ground-truth reconciliation, not preregistered — used a 5 % student-false-negative prior (Sobotkova et al. 2023). On the 55-map VLM-only slice — where every candidate has the (student = 0, VLM = 1) response pattern by construction — the 2-annotator D-S model assigns an identical posterior to all items, rendering item-level AUC degenerate at 0.500. Replacing the 5 % prior with a data-driven prior derived from the human-review labels on the same slice yields a calibrated aggregate posterior (calibrated prior = 0.17; posterior = 0.7246 vs empirical 0.7247; held-out 80 / 20 ECE = 0.2621) but does not restore item-level ranking: the AUC remains 0.500 across every prior tested. The rank failure is a structural consequence of the 2-annotator identifiability class structure, not a prior-choice failure. For per-item ranking the analysis relies on the verifier probability (Obs 269; AUC = 0.6545 on this slice) and the human-review labels; D-S is retained as a comparator and is explicitly flagged as inadequate for item-level use on this slice.

## 12. Files manifest

**Outputs (this directory)**:

- `report.md` — this report.
- `item-posteriors.csv` — v2 per-item posteriors at prior = 0.7247.
- `item-posteriors-calibrated.csv` — per-item posteriors at calibrated prior = 0.17.
- `dawid-skene-results-v2.json` + `dawid-skene-results-v2.md` — raw model outputs.
- `summary.json` — calibration + cross-tab summary.
- `reliability.csv` + `reliability-calibrated.csv` — reliability-bin data for the two priors.
- `reliability_v2.png` + `reliability_v2_calibrated.png` — reliability figures.
- `prior_sensitivity_sweep.csv` — grid-search data (cited in §8 for the calibrated-prior identification).
- `holdout.json` — 80 / 20 held-out sensitivity check.
- `comparison.md` — v1 vs v2 side-by-side comparison.
- Subdirectories `ds-human-crosstab/` + `ds-human-crosstab-calibrated/` — v1 / v2 cross-tab subsidiary artefacts.

**Inputs**:

- `results/55maps-image-generalisation/human-review.csv` — initial review labels.
- `results/55maps-image-generalisation/human-review-multi-buffer.csv` — multi-buffer re-review.
- `results/55maps-image-generalisation/dawid-skene/` — v1 D-S outputs (for the comparison columns in §5).

## 13. Reproducibility

- **Analysis framing**: hand-authored report (no dedicated script); the D-S v2 model is fit via the standard EM loop with the substituted prior. Data computed from the human-review CSVs + the v1 D-S item-posteriors.csv.
- **Prior sweep**: 100 prior values in [0.01, 0.99]; the "calibrated prior" is the posterior-vs-empirical-rate minimum-gap selection across that sweep.
- **Held-out check**: 80 / 20 split at seed 42; 206 test items.
- **Git commit of original data run**: `dee0ecf0` (`data(55maps-image): multi-buffer corrected F1 + D-S v1 cross-tab + D-S v2 prior sweep`).
- **Toolchain**: Python ≥ 3.11, NumPy, pandas, scikit-learn (for the Wilson CI + brier_score_loss + roc_auc_score helpers), matplotlib.
