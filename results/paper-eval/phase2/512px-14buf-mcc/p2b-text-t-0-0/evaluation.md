# Evaluation: T0.0

**Generated**: 2026-08-21T13:42:48.147723+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.269 | N/A * | 0.217 | N/A * | 0.356 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.479 | N/A * | 0.385 | N/A * | 0.633 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.565 | N/A * | 0.455 | N/A * | 0.746 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.606 | N/A * | 0.487 | N/A * | 0.800 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.627 | N/A * | 0.505 | N/A * | 0.829 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.643 | N/A * | 0.518 | N/A * | 0.850 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.648 | N/A * | 0.521 | N/A * | 0.856 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.651 | N/A * | 0.524 | N/A * | 0.860 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.655 | N/A * | 0.527 | N/A * | 0.865 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.656 | N/A * | 0.528 | N/A * | 0.866 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.658 | N/A * | 0.530 | N/A * | 0.870 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.660 | N/A * | 0.531 | N/A * | 0.871 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.660 | N/A * | 0.531 | N/A * | 0.871 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.661 | N/A * | 0.532 | N/A * | 0.873 | N/A * | undefined | undefined | 1.000 | 0.000 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here (defined on 0 of 3 passes): the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

