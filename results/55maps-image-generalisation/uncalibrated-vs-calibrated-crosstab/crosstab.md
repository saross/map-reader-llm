# Uncalibrated vs calibrated human-review cross-tabulation

**Timestamp**: 2026-04-20T07:33:47.285914+00:00

**Observation anchor**: Obs 268 (`docs/notes/reflections/working-notes.md` §"Observation 263" revision block, lines 11905–11937). This report is the empirical artefact that Obs 268 points to, and the direct quantitative input to meta-findings Theme T1 ("Human-review calibration and the corrected-F1 lower bound").

**Context**: During the 55-map image-generalisation human review, the reviewer initially used a "fuzzy" UI without an explicit spatial tolerance. After 327 reviews, the UI was upgraded to overlay a magenta 50 m tolerance circle on the candidate crop, and the reviewer restarted and completed all 1,028 reviews. This report quantifies how the calibrated UI changed reviewer decisions on the 327-candidate overlap, as empirical evidence for Obs 263's ambiguity-band claim.

## 1. Executive summary

**Definition — "flip"**. In this report, a *flip* is a review-UI-induced reversal of the same reviewer's decision on the same candidate. The uncalibrated UI presented no explicit spatial tolerance; after 327 reviews, the UI was upgraded to overlay a magenta 50 m tolerance circle on the candidate crop, and the reviewer re-reviewed all 1,028 candidates. The *flip rate* is the proportion of the 327-candidate overlap where the reviewer's decision changed between the uncalibrated and calibrated sessions.

**Headline numbers**:

- **Flip rate**: 70 / 327 = **21.41 %** [17.13 %, 25.99 %] (bootstrap 95 % CI, 10,000 iterations, seed 42).
- **Directional asymmetry**: 100 % of flips ran Uncal = mound → Cal = not_mound; zero flips in the reverse direction. The calibrated UI uniformly *tightened* reviewer judgement toward more conservative labelling.
- **Corrected-F1 impact**: applying the tighter (calibrated) labels across the full 1,028-candidate review reduces the counterfactual mixed-label F1 from 0.8377 to **0.8295** at 50 m (ΔF1 = −0.0082). The calibrated labels therefore establish the **lower-bound corrected-F1** for paper citation; the ~0.8 % penalty is the measurable cost of the UI-correction.
- **Stratification caveat**: all 327 overlap candidates sit in the top verifier-probability bin [0.90, 1.00] (median 1.000). The 21.4 % flip rate is therefore a *stricter-than-expected* signal — the UI change moved decisions even among the candidates the verifier was most confident about. The low-p tail prediction from Obs 263 cannot be tested from this overlap.

**One-line paper claim**: "A calibrated review UI (magenta 50 m tolerance overlay) tightened reviewer decisions on 21.4 % of an n=327 overlap, all one-directionally toward stricter labelling; the corresponding corrected-F1 penalty is 0.0082 at 50 m."

## 2. Overall agreement

- Uncalibrated total reviews: **327**
- Calibrated total reviews: **1028**
- Overlap on `candidate_id`: **327**
- Agreement rate: **0.7859** (257/327)
- Disagreement rate: **0.2141** (70/327)
- Bootstrap 95% CI for disagreement rate (10,000 iterations, seed 42): [0.1713, 0.2599]

## 3. Disagreement decomposition

| Direction | Count | Share of overlap |
|---|---:|---:|
| Both mound (stable positive) | 186 | 0.5688 |
| Both not_mound (stable negative) | 71 | 0.2171 |
| Uncal=mound -> Cal=not_mound (uncal FP) | 70 | 0.2141 |
| Uncal=not_mound -> Cal=mound (uncal FN) | 0 | 0.0000 |

## 4. Stratified disagreement by verifier probability

**Critical caveat on the overlap composition**: the 327 overlap candidates have verifier_probability in [1.000, 1.000] (median 1.000). The uncalibrated session reviewed only the highest-confidence slice of the candidate queue, so the stratification below cannot directly test Obs 263's prediction that disagreement concentrates in the low-p tail. What it CAN show is whether disagreement arises even among high-verifier-confidence candidates — a stricter bar than the Obs 263 prediction.

| Probability bin | n | Disagreements | Rate | Uncal->not | Uncal->mound |
|---|---:|---:|---:|---:|---:|
| [0.90, 1.00] | 327 | 70 | 0.2141 | 70 | 0 |
| [0.70, 0.90) | 0 | 0 | 0.0000 | 0 | 0 |
| [0.50, 0.70) | 0 | 0 | 0.0000 | 0 | 0 |
| [0.15, 0.50) | 0 | 0 | 0.0000 | 0 | 0 |

*Interpretation*: With all 327 overlap candidates in the top bin, a non-trivial disagreement rate there is a stronger-than-expected signal — the UI change moved reviewer decisions even on the candidates the verifier was most confident about. The low-p tail prediction from Obs 263 remains untested by this overlap and would require a separate uncalibrated-review session sampling across the probability range.

## 5. Symbol-type flow table

| uncal \ cal | bench_mark_on_mound | burial_mound | not_mound | settlement_mound | trig_point_on_mound | Row total |
|---|---|---|---|---|---|---|
| bench_mark_on_mound | 22 | 0 | 4 | 0 | 0 | 26 |
| burial_mound | 0 | 146 | 62 | 0 | 0 | 208 |
| not_mound | 0 | 0 | 71 | 0 | 0 | 71 |
| settlement_mound | 0 | 0 | 2 | 2 | 0 | 4 |
| trig_point_on_mound | 0 | 1 | 2 | 0 | 15 | 18 |
| Column total | 22 | 147 | 141 | 2 | 15 | 327 |

## 6. Corrected-F1 accounting

Buffer: 50 m. Measured pipeline counts held fixed: TP=3637, FP=1028, FN=1133 (F1=0.7710).

- Mounds on overlap under calibrated labels: **186** / 327
- Mounds on overlap under uncalibrated labels: **256** / 327
- Phantom TP (full calibrated, all 1,028): **472**
- Phantom TP (mixed, uncal labels on 327 overlap + cal on 701 remainder): **542**

| Scenario | Precision | Recall | F1 |
|---|---:|---:|---:|
| All calibrated | 0.8808 | 0.7839 | **0.8295** |
| Mixed (uncal on overlap) | 0.8958 | 0.7867 | **0.8377** |
| Delta (all-cal minus mixed) | -0.0150 | -0.0028 | **-0.0082** |

*Interpretation*: Positive delta means the calibrated UI produced a higher corrected F1 than the uncalibrated labels would have on the same 327-row overlap. The delta isolates the UI-induced change; the 701 non-overlap rows use calibrated labels in both scenarios because no uncalibrated labels exist for them.

## 7. Paper implications

### 7.1 Lower-bound framing of corrected F1 is empirically justified

The 55-map corrected-F1 headline of F1 ≥ 0.830 at 50 m (see `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md`) is computed using calibrated labels. This cross-tabulation shows that switching to the *looser* uncalibrated labels on the 327-candidate overlap would have produced F1 = 0.8377 — i.e., 0.0082 higher than the calibrated headline. Because every flip ran toward stricter labelling, the calibrated F1 is provably a lower bound: no alternative labelling of the overlap within this reviewer's two sessions produces a smaller F1. This is the empirical confirmation of the "corrected F1 is a lower bound" language in Obs 268 and meta-findings Theme T1.

### 7.2 Tolerance-calibration is a methodological requirement, not an aesthetic choice

The 21.4 % flip rate at the strictest verifier-confidence bin shows that a review UI without an explicit spatial-tolerance guide produces materially different labels from one with it, even when reviewer and candidate set are held fixed. The UI upgrade transformed "is this symbol close enough to the candidate centre?" from an uncalibrated visual judgement into a binary geometric check against the preregistered 50 m tolerance. The direction of change (always toward stricter labelling) indicates reviewers default to *overclaiming* matches when no tolerance guide is visible. For reproducibility, any future crop-review pipeline should render the matching buffer explicitly on the crop.

### 7.3 Suggested paper text (Results — human review)

> A cross-tabulation of the 327-candidate overlap between the uncalibrated and calibrated review sessions finds a 21.4 % flip rate (95 % CI [17.1 %, 26.0 %] over 10,000 bootstrap iterations), with every flip in the direction Uncal = mound → Cal = not_mound. Applying the calibrated labels across the full 1,028-candidate review reduces the counterfactual mixed-label F1 at 50 m from 0.8377 to 0.8295 (ΔF1 = −0.0082). Because the UI-induced reversals are strictly one-directional toward stricter labelling, the calibrated corrected-F1 is an empirical lower bound under this reviewer's two sessions.

### 7.4 Scope limitations

- All 327 overlap candidates have verifier_probability = 1.000; the stratified table cannot test the Obs 263 prediction that flip rate concentrates in the low-p tail. Testing that prediction would require a separate uncalibrated-review session that samples across the probability range.
- A single reviewer conducted both sessions. Inter-reviewer flip rates (between independent reviewers under the same UI) are out of scope here; see the human-review-sessions archive for raw session logs if a second-reviewer probe is ever staged.

## 8. Files manifest

**Outputs (this directory)**:

- `crosstab.md` — this report.
- `crosstab.json` — machine-readable form of the §Overall agreement, §Disagreement decomposition, §Stratified disagreement, §Symbol-type flow, and §Corrected-F1 accounting tables.

**Inputs**:

- `archive/human-review-sessions/human-review-55maps-image-uncalibrated-2026-04-20.csv` — uncalibrated-session labels (n=327).
- `results/55maps-image-generalisation/human-review.csv` — calibrated-session labels (n=1,028).
- `outputs/55maps-image-generalisation/evaluation/evaluation.json` — measured pipeline counts at 50 m (TP/FP/FN) held fixed across both scenarios.

**Script**: `scripts/crosstab_uncalibrated_vs_calibrated.py`.

## 9. Reproducibility

- Bootstrap: 10,000 iterations, seed 42.
- Uncalibrated CSV: `archive/human-review-sessions/human-review-55maps-image-uncalibrated-2026-04-20.csv`.
- Calibrated CSV: `results/55maps-image-generalisation/human-review.csv`.
- Measured evaluation: `outputs/55maps-image-generalisation/evaluation/evaluation.json`.
- Script: `scripts/crosstab_uncalibrated_vs_calibrated.py`.
