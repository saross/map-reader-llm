# Evaluation: retest-phase2b__text-t0.0

**Generated**: 2026-09-13T14:01:19.193523+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.265 | N/A * | 0.212 | N/A * | 0.350 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.467 | N/A * | 0.375 | N/A * | 0.619 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.555 | N/A * | 0.446 | N/A * | 0.735 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.594 | N/A * | 0.477 | N/A * | 0.787 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.618 | N/A * | 0.497 | N/A * | 0.819 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.636 | N/A * | 0.511 | N/A * | 0.842 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.641 | N/A * | 0.515 | N/A * | 0.849 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.644 | N/A * | 0.518 | N/A * | 0.853 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.648 | N/A * | 0.520 | N/A * | 0.858 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.649 | N/A * | 0.522 | N/A * | 0.860 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.652 | N/A * | 0.524 | N/A * | 0.863 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.654 | N/A * | 0.525 | N/A * | 0.865 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.654 | N/A * | 0.525 | N/A * | 0.865 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.655 | N/A * | 0.526 | N/A * | 0.868 | N/A * | undefined | undefined | 1.000 | 0.000 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here (defined on 0 of 3 passes): the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=193, TN=0, FP=122, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

