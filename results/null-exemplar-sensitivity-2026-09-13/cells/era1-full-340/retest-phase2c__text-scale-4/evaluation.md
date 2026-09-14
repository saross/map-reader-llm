# Evaluation: retest-phase2c__text-scale-4

**Generated**: 2026-09-13T14:02:19.309043+00:00  
**Detections**: 810  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.261 | N/A * | 0.210 | N/A * | 0.345 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.462 | N/A * | 0.372 | N/A * | 0.611 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.557 | N/A * | 0.448 | N/A * | 0.736 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.599 | N/A * | 0.481 | N/A * | 0.791 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.616 | N/A * | 0.495 | N/A * | 0.813 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.632 | N/A * | 0.509 | N/A * | 0.836 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.638 | N/A * | 0.514 | N/A * | 0.844 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.642 | N/A * | 0.516 | N/A * | 0.848 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.646 | N/A * | 0.520 | N/A * | 0.854 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.648 | N/A * | 0.521 | N/A * | 0.856 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.652 | N/A * | 0.525 | N/A * | 0.862 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.655 | N/A * | 0.527 | N/A * | 0.866 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.655 | N/A * | 0.527 | N/A * | 0.866 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.657 | N/A * | 0.528 | N/A * | 0.868 | N/A * | undefined | undefined | 1.000 | 0.000 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/315 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=193, TN=0, FP=122, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

