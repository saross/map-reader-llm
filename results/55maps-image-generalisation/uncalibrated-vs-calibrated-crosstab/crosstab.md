# Uncalibrated vs calibrated human-review cross-tabulation

**Timestamp**: 2026-04-20T07:33:47.285914+00:00

**Context**: During the 55-map image-generalisation human review, the reviewer initially used a "fuzzy" UI without an explicit spatial tolerance. After 327 reviews, the UI was upgraded to overlay a magenta 50 m tolerance circle on the candidate crop, and the reviewer restarted and completed all 1,028 reviews. This report quantifies how the calibrated UI changed reviewer decisions on the 327-candidate overlap, as empirical evidence for Obs 263's ambiguity-band claim.

## Overall agreement

- Uncalibrated total reviews: **327**
- Calibrated total reviews: **1028**
- Overlap on `candidate_id`: **327**
- Agreement rate: **0.7859** (257/327)
- Disagreement rate: **0.2141** (70/327)
- Bootstrap 95% CI for disagreement rate (10,000 iterations, seed 42): [0.1713, 0.2599]

## Disagreement decomposition

| Direction | Count | Share of overlap |
|---|---:|---:|
| Both mound (stable positive) | 186 | 0.5688 |
| Both not_mound (stable negative) | 71 | 0.2171 |
| Uncal=mound -> Cal=not_mound (uncal FP) | 70 | 0.2141 |
| Uncal=not_mound -> Cal=mound (uncal FN) | 0 | 0.0000 |

## Stratified disagreement by verifier probability

**Critical caveat on the overlap composition**: the 327 overlap candidates have verifier_probability in [1.000, 1.000] (median 1.000). The uncalibrated session reviewed only the highest-confidence slice of the candidate queue, so the stratification below cannot directly test Obs 263's prediction that disagreement concentrates in the low-p tail. What it CAN show is whether disagreement arises even among high-verifier-confidence candidates — a stricter bar than the Obs 263 prediction.

| Probability bin | n | Disagreements | Rate | Uncal->not | Uncal->mound |
|---|---:|---:|---:|---:|---:|
| [0.90, 1.00] | 327 | 70 | 0.2141 | 70 | 0 |
| [0.70, 0.90) | 0 | 0 | 0.0000 | 0 | 0 |
| [0.50, 0.70) | 0 | 0 | 0.0000 | 0 | 0 |
| [0.15, 0.50) | 0 | 0 | 0.0000 | 0 | 0 |

*Interpretation*: With all 327 overlap candidates in the top bin, a non-trivial disagreement rate there is a stronger-than-expected signal — the UI change moved reviewer decisions even on the candidates the verifier was most confident about. The low-p tail prediction from Obs 263 remains untested by this overlap and would require a separate uncalibrated-review session sampling across the probability range.

## Symbol-type flow table

| uncal \ cal | bench_mark_on_mound | burial_mound | not_mound | settlement_mound | trig_point_on_mound | Row total |
|---|---|---|---|---|---|---|
| bench_mark_on_mound | 22 | 0 | 4 | 0 | 0 | 26 |
| burial_mound | 0 | 146 | 62 | 0 | 0 | 208 |
| not_mound | 0 | 0 | 71 | 0 | 0 | 71 |
| settlement_mound | 0 | 0 | 2 | 2 | 0 | 4 |
| trig_point_on_mound | 0 | 1 | 2 | 0 | 15 | 18 |
| Column total | 22 | 147 | 141 | 2 | 15 | 327 |

## Corrected-F1 accounting

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

## Reproducibility

- Bootstrap: 10,000 iterations, seed 42
- Uncalibrated CSV: `archive/human-review-sessions/human-review-55maps-image-uncalibrated-2026-04-20.csv`
- Calibrated CSV: `results/55maps-image-generalisation/human-review.csv`
- Measured evaluation: `outputs/55maps-image-generalisation/evaluation/evaluation.json`
- Script: `scripts/crosstab_uncalibrated_vs_calibrated.py`
