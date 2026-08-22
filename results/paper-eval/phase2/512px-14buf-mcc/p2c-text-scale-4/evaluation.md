# Evaluation: detections_scale-4_run01

**Generated**: 2026-08-21T13:43:49.510151+00:00  
**Detections**: 882  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.266 | N/A * | 0.214 | N/A * | 0.351 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.476 | N/A * | 0.383 | N/A * | 0.627 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.566 | N/A * | 0.456 | N/A * | 0.746 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.609 | N/A * | 0.491 | N/A * | 0.803 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.625 | N/A * | 0.503 | N/A * | 0.824 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.640 | N/A * | 0.516 | N/A * | 0.844 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.646 | N/A * | 0.520 | N/A * | 0.852 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.649 | N/A * | 0.523 | N/A * | 0.855 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.653 | N/A * | 0.526 | N/A * | 0.861 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.654 | N/A * | 0.527 | N/A * | 0.863 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.659 | N/A * | 0.531 | N/A * | 0.868 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.661 | N/A * | 0.533 | N/A * | 0.872 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.661 | N/A * | 0.533 | N/A * | 0.872 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.663 | N/A * | 0.534 | N/A * | 0.874 | N/A * | undefined | undefined | 1.000 | 0.000 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

