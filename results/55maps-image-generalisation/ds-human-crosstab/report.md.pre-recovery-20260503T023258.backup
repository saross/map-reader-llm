# Dawid-Skene aggregate posterior vs. human review (55-map image generalisation)

**Original analysis timestamp**: ~2026-04-20 (single-commit hand-authored doc; commit `dee0ecf0`).
**Level-up**: 2026-04-24 (Session 76).

**Observation anchors**: Obs 273 (D-S aggregate structurally inadequate on VLM-only slice); Obs 269 (verifier calibration); Obs 268 (review-UI calibration crosstab). Direct input to meta-findings Theme T5.

## 1. Executive summary

This artefact cross-tabulates the **Dawid-Skene (D-S) aggregate posterior** against **per-candidate human-review labels** on the VLM-only slice of the 55-map image-generalisation run (1,029 candidates; 1,028 successfully joined to D-S posteriors; 1 unjoined). The D-S model is fit with two binary annotators (student digitisers + VLM pipeline) and a preregistered 5 % student-false-negative prior.

**Headline finding — D-S is structurally inadequate on this slice**:

- Every one of the 1,028 VLM-only candidates receives the **same** D-S posterior of 0.1862 (because two binary annotators with identical response patterns land in the same identifiability class). The D-S posterior cannot rank individuals by construction.
- The D-S posterior as an item-level classifier has **AUC = 0.5000** (degenerate), **ECE = 0.5385**, **Brier = 0.4895**.
- The aggregate prediction (0.1862) is **2.5× below** the human-confirmed mound rate on the joined set (0.7247 = 745 / 1,028). This is not a small calibration error; it is a systematic under-counting of real mounds at the cohort level that the D-S fit cannot repair without a revised prior or additional annotators.
- The verifier (Obs 269) **out-performs D-S** on every calibration metric: ECE 0.2689 (D-S 0.5385), Brier 0.3226 (D-S 0.4895), AUC 0.6545 (D-S 0.5000 degenerate).

**One-line paper claim**: "With only two binary annotators, the Dawid-Skene aggregate posterior on the VLM-only slice is structurally degenerate (AUC = 0.5000; all items share posterior 0.1862) and 2.5× below the human-confirmed mound rate (0.7247). D-S cannot be used as a per-candidate discriminator on this slice; the verifier (ECE = 0.269; AUC = 0.655) and human review remain the only item-level signals."

## 2. Input provenance

- **D-S posteriors**: `results/55maps-image-generalisation/dawid-skene/item-posteriors.csv` — per-item posteriors from the two-annotator D-S fit (preregistered 5 % student-FN prior). See sibling analysis at `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/report.md` for the v2 (data-driven-prior) variant which also returns AUC = 0.5000 — confirming the pathology is structural, not prior-specific.
- **Review-yesterday**: `results/55maps-image-generalisation/human-review.csv` — initial calibrated-UI review labels (1,028 rows; 472 mound / 556 not-mound at the 50 m tolerance).
- **Review-today**: `results/55maps-image-generalisation/human-review-multi-buffer.csv` — multi-buffer re-review adding 274 mound calls at buffer bands > 50 m (273 today_mound + 1 today_only) and 283 today_not_mound confirmations.
- **Combined review**: 1,029 rows = 472 yesterday_mound + 283 today_not_mound + 273 today_mound + 1 today_only.

## 3. Sample composition

- Combined review rows: **1,029**.
- Rows successfully joined to D-S posterior: **1,028**.
- Unjoined rows (no D-S posterior found): **1** (the single `today_only` row that has no yesterday record).
- Human-mound prevalence in joined set: **0.7247** (745 / 1,028). Higher than the 0.459 prevalence under yesterday-only (50 m-strict) labels because today's multi-buffer re-review rescues 273 mounds at > 50 m buffers.

### Combined-label source breakdown

| Source | Count |
|--------|------:|
| yesterday_mound | 472 |
| today_not_mound | 283 |
| today_mound | 273 |
| today_only | 1 |

## 4. Structural note — D-S 2-annotator identifiability

With only two binary annotators (student vote, VLM vote) the Dawid-Skene model assigns an **identical posterior** to every item that shares the same annotator response pattern. All 1,028 VLM-only items (student = 0, VLM = 1) receive the same posterior value (0.1862). Consequently:

- The D-S posterior on this slice is a single point estimate of the **aggregate rate** of true mounds in the VLM-only cohort, not an item-level discriminator.
- The reliability diagram has exactly one populated bin (§6).
- The AUC of the D-S posterior as a classifier is undefined (degenerate ordering) and defaults to 0.5.
- The 2 × 2 cross-tab at threshold 0.5 collapses (posterior < 0.5 for all rows).

**Framing check — correction to the original hypothesis**. The original hypothesis (pre-analysis) was "aggregate estimates rate, human disambiguates individuals". On this slice, the D-S aggregate is **not** close to the empirical rate (0.186 predicted vs. 0.725 observed) — see §9 Interpretation for the prior-misspecification diagnosis. The identifiability argument still holds — the D-S posterior cannot rank individuals by construction — but the aggregate itself is badly miscalibrated here, so the framing needs qualification rather than confirmation. The v2 (data-driven-prior) variant in the sibling artefact finds the same AUC = 0.500 pathology even with a non-pathological aggregate estimate, so the rank-failure is the structural invariant, not the aggregate miscalibration.

## 5. Coarse cross-tab (D-S > 0.5 vs. human mound)

| | Human mound | Human not_mound |
|---|---:|---:|
| **D-S > 0.5** | 0 | 0 |
| **D-S ≤ 0.5** | 745 | 283 |

- Precision: **nan** (no D-S > 0.5 items).
- Recall: **0.0000** (no D-S > 0.5 items among real mounds).
- F1: **nan**.

The 2 × 2 table collapses because D-S posterior = 0.1862 < 0.5 for all 1,028 items.

## 6. Reliability diagram (10 equal-width bins)

| Bin | n | n_mound | Mean predicted P | Empirical P | Gap (pred − emp) | 95 % Wilson CI on empirical |
|-----|---:|---:|---:|---:|---:|---|
| [0.1, 0.2] | 1028 | 745 | 0.1862 | 0.7247 | -0.5385 | [0.697, 0.751] |

Only one bin populated — the [0.1, 0.2] bin carrying all 1,028 items. The empirical mound rate 0.7247 [0.697, 0.751] is 0.54 higher than the D-S predicted 0.1862; the Wilson CI on the empirical rate does not overlap the D-S prediction.

- **Expected Calibration Error (ECE, 10 bins)**: **0.5385**.
- **Brier score**: **0.4895**.
- **AUC (D-S posterior as mound classifier)**: **0.5000** *(degenerate — all inputs share one posterior; no rank information.)*

## 7. Ambiguity-band isolation

Evidence for "human disambiguates individuals, D-S estimates rate" is untestable on this slice because the D-S posterior has no spread.

| Band | Range | n | n_mound | Human-mound rate | 95 % Wilson CI |
|------|-------|---:|---:|---:|---|
| Ambiguous | [0.3, 0.7] | 0 | 0 | nan | [nan, nan] |
| Confident | [0, 0.1) ∪ (0.9, 1] | 0 | 0 | nan | [nan, nan] |
| Middle remainder | elsewhere | 1028 | 745 | 0.7247 | — |

All 1,028 items land in "middle remainder"; the "ambiguous" and "confident" bands are empty.

## 8. Buffer-band view (D-S posterior vs. review band)

| Buffer band | n | Mean D-S posterior | 95 % CI |
|------------:|---:|-------------------:|---|
| 50 | 473 | 0.1862 | [0.1862, 0.1862] |
| 75 | 121 | 0.1862 | [0.1862, 0.1862] |
| 100 | 47 | 0.1862 | [0.1862, 0.1862] |
| 125 | 19 | 0.1862 | [0.1862, 0.1862] |
| 150 | 11 | 0.1862 | [0.1862, 0.1862] |
| 200 (sentinel) | 74 | 0.1862 | [0.1862, 0.1862] |

Because the D-S posterior is degenerate, the mean posterior is identical across all buffer bands (0.1862 at 50, 75, 100, 125, 150, and 200 m). It carries no information about buffer-band separation — consistent with the attractor-pull analysis (Obs 272) finding that the buffer-dependent signal lives in the verifier probability, not in the D-S posterior.

## 9. Comparison to the verifier (Observation 269)

| Metric | D-S posterior | Verifier | Better-calibrated? |
|--------|--------------:|---------:|-------------------|
| ECE (lower is better) | 0.5385 | 0.2689 | Verifier |
| Brier (lower is better) | 0.4895 | 0.3226 | Verifier |
| AUC (higher is better) | 0.5000 | 0.6545 | Verifier (D-S has no item-level rank) |

The verifier is better-calibrated on every metric. Both are poorly calibrated relative to an ideal classifier (ideal ECE = 0, Brier ≤ 0.25 at prevalence 0.7, AUC → 1); the ordering is D-S is worse than the verifier, and the verifier is worse than a well-calibrated model would be. See `verifier-calibration-crosstab/calibration.md` for the full verifier-calibration picture.

## 10. Interpretation

- **D-S aggregate is badly wrong here — flagged as surprising.** The D-S posterior predicts an aggregate mound rate of 0.1862 for the VLM-only cohort; the combined human-review label (including today's wider-buffer rescues) finds 0.7247. The absolute gap is 0.539. Even against yesterday's 50 m-strict labels, the empirical rate was 0.459 (472 / 1,028) — still 2.5× the D-S estimate. This is the reverse of the expected framing: rather than "aggregate estimates rate well, human disambiguates individuals", the D-S aggregate is systematically under-counting real mounds at the cohort level.
- **Prior-driven artefact for the aggregate estimate**. The D-S run used a fixed prior of 5 % student false-negative rate (see `dawid-skene-results.json`). The data imply the student FN rate on the VLM-only slice is much higher — the VLM independently flagged 1,028 locations that students had not digitised, and human review confirms nearly three-quarters of them are real mounds at some buffer. A D-S fit with an honest, data-driven student-FN prior — or with more than two annotators — would land much closer to the empirical rate. The sibling artefact at `dawid-skene-v2-data-driven-prior/report.md` empirically confirms this: with a data-driven prior at 0.7247 student-FN, the aggregate posterior tracks the empirical rate but **the item-level AUC remains 0.500** — the rank failure is structural, not prior-specific.
- **Aggregate vs. individual — revised.** With only two binary annotators, the D-S posterior collapses to a single value per response pattern, so it cannot rank individuals by design. Human review is the only per-candidate signal available on this slice. The verifier probability (Obs 269) is a graded item-level signal but is itself poorly calibrated at the high end. Downstream use should treat D-S as a (currently miscalibrated) cohort-rate estimator and rely on the verifier plus human review for item-level discrimination.
- **Buffer-band view.** Because the D-S posterior is degenerate, mean posterior is identical across all buffer bands (0.1862 at 50, 75, 100, 125, 150, and 200 m). It carries no information about buffer-band separation, which is consistent with Obs 268 + 272 — the signal for "wider-buffer mounds are genuinely lower-signal" lives entirely in the attractor-pull shell analysis (Obs 272) and the verifier-probability calibration tail (Obs 269), not in the D-S posterior.

## 11. Caveats / risk register

1. **AUC = 0.500 is structural, not a bug**. The D-S AUC of 0.500 reflects the 2-annotator identifiability class structure, not a calibration failure specifically. Any D-S fit with only two binary annotators sharing the same response pattern would produce the same result regardless of prior choice.
2. **Prior-sensitivity**: the 5 % student-FN prior is paired with the observed ~72 % empirical student-FN rate on the VLM-only slice. The v2 data-driven-prior variant (sibling artefact) produces a better-calibrated aggregate but does not recover per-item rank — confirming §4's identifiability claim.
3. **74 sentinel candidates at buffer = 200 m**: the `> 150 m` sentinel shell is treated as "mound" in the combined label (via today_mound), contributing to the 745 mound count. The attractor-pull analysis (Obs 272) rules those candidates out as causally attributable to detections. If the D-S comparison is re-run excluding the 74 sentinels, the joined n drops to 954 and the human-mound rate drops to 0.704 (671 / 954) — still ~3.8× the D-S posterior.
4. **Unjoined row** (n = 1, `today_only`): trivial but should be reported in §3 for auditability.
5. **Verifier-vs-D-S comparison (§9) uses the same 1,028 rows** as the verifier-calibration artefact — direct apples-to-apples. See `verifier-calibration-crosstab/calibration.md` for the verifier-side methodology.

## 12. Paper implications

### 12.1 Structural inadequacy of 2-annotator D-S

The paper's Methods / Limitations section should state plainly: **a 2-annotator binary Dawid-Skene fit cannot rank individuals on a slice where both annotators share a response pattern.** On the VLM-only slice (student = 0, VLM = 1 for all rows by construction), every item lands in a single identifiability class; the D-S posterior is a single point regardless of the underlying mound status. This is independent of the prior; it is a combinatorial consequence of the 2-annotator structure.

### 12.2 D-S should not be cited as an item-level classifier

Downstream pipelines should not use the D-S posterior as a per-candidate confidence score on this slice. Rank-based uses (top-K, threshold-sweep) are not defined on a degenerate-ordering classifier. The verifier probability (`verifier-calibration-crosstab/calibration.md`) and the human-review labels remain the only item-level signals for VLM-only candidates.

### 12.3 Three-annotator or mixed-annotation-strength re-design would repair

A three-annotator D-S (student + VLM + a second VLM run, say a text-track proposer) would break the identifiability collapse and allow item-level ranking. This is out of scope for the current paper but a natural methodology-follow-up note.

### 12.4 Suggested paper text (Limitations / Methods)

> The preregistered Dawid-Skene analysis of the 55-map image-generalisation VLM-only slice was conducted with two binary annotators (student digitisers and the VLM pipeline). Because every VLM-only candidate has the same (student, VLM) = (0, 1) response pattern by construction, the D-S model assigns an identical posterior (0.1862) to all 1,028 items; the item-level AUC is degenerate (0.500) and the cross-tab against human review at threshold 0.5 is empty. The D-S aggregate estimate is 2.5× below the empirical mound rate established by full human review (0.7247 = 745 / 1,028), reflecting the preregistered 5 % student-false-negative prior mismatching the empirical ~72 % rate on the VLM-only slice. A data-driven-prior variant (`dawid-skene-v2-data-driven-prior/report.md`) recovers the aggregate rate but preserves the rank degeneracy, confirming the failure is structural. The verifier probability is better-calibrated on every metric (ECE 0.269 vs 0.539; Brier 0.323 vs 0.490; AUC 0.655 vs 0.500) but itself miscalibrated at the high end (Obs 269).

## 13. Files manifest

**Outputs (this directory)**:

- `report.md` — this report.
- `buffer_band_vs_ds.csv` — buffer-band view source data.
- `crosstab_coarse.csv` — §5 coarse cross-tab data.
- `reliability.csv` — §6 reliability bin data.
- `reliability_plot.png` — reliability diagram figure.
- `buffer_scatter.png` — buffer-band scatter figure.
- `summary.json` — machine-readable summary.

**Inputs**:

- `results/55maps-image-generalisation/dawid-skene/item-posteriors.csv` — D-S per-item posteriors.
- `results/55maps-image-generalisation/human-review.csv` — initial review labels.
- `results/55maps-image-generalisation/human-review-multi-buffer.csv` — multi-buffer re-review.

**Figures**:

- `reliability_plot.png` — reliability diagram.
- `buffer_scatter.png` — D-S posterior vs. buffer band for mound candidates.

## 14. Reproducibility

- **Analysis framing**: hand-authored report (no dedicated script); data computed from `dawid-skene/item-posteriors.csv` + review CSVs with standard pandas/NumPy operations.
- **Bootstrap**: none invoked (the degenerate AUC, NaN precision/F1 at threshold 0.5, and constant posterior mean all have exact closed-form values; bootstrap CIs would be width-zero degenerate).
- **Re-run**: to regenerate the CSV + summary / figures side data, a short Python script could be written following the pattern in `scripts/crosstab_verifier_vs_human.py`. This is not currently scripted; the CSVs in this directory are the canonical data product.
- **Git commit of original data run**: `dee0ecf0` (`data(55maps-image): multi-buffer corrected F1 + D-S v1 cross-tab + D-S v2 prior sweep`).
- **Toolchain**: Python ≥ 3.11, pandas, scikit-learn (for the Wilson CI helper), matplotlib.
