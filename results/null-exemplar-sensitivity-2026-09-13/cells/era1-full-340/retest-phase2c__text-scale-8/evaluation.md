# Evaluation: retest-phase2c__text-scale-8

**Generated**: 2026-09-13T14:02:11.108126+00:00  
**Detections**: 809  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.260 | N/A * | 0.209 | N/A * | 0.343 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.467 | N/A * | 0.376 | N/A * | 0.617 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.556 | N/A * | 0.448 | N/A * | 0.734 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.596 | N/A * | 0.480 | N/A * | 0.787 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.619 | N/A * | 0.498 | N/A * | 0.817 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.637 | N/A * | 0.513 | N/A * | 0.842 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.642 | N/A * | 0.517 | N/A * | 0.848 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.645 | N/A * | 0.519 | N/A * | 0.852 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.650 | N/A * | 0.523 | N/A * | 0.858 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.651 | N/A * | 0.524 | N/A * | 0.860 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.654 | N/A * | 0.527 | N/A * | 0.864 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.656 | N/A * | 0.528 | N/A * | 0.866 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.656 | N/A * | 0.528 | N/A * | 0.866 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.657 | N/A * | 0.529 | N/A * | 0.868 | N/A * | undefined | undefined | 1.000 | 0.000 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/315 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=193, TN=0, FP=122, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

