# Evaluation: detections_scale-8_run01

**Generated**: 2026-08-21T13:43:53.729222+00:00  
**Detections**: 881  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.266 | N/A * | 0.214 | N/A * | 0.351 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.480 | N/A * | 0.387 | N/A * | 0.633 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.568 | N/A * | 0.457 | N/A * | 0.748 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.607 | N/A * | 0.489 | N/A * | 0.800 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.628 | N/A * | 0.506 | N/A * | 0.828 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.645 | N/A * | 0.520 | N/A * | 0.850 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.649 | N/A * | 0.523 | N/A * | 0.855 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.652 | N/A * | 0.525 | N/A * | 0.859 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.656 | N/A * | 0.529 | N/A * | 0.865 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.658 | N/A * | 0.530 | N/A * | 0.866 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.661 | N/A * | 0.532 | N/A * | 0.870 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.662 | N/A * | 0.533 | N/A * | 0.872 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.662 | N/A * | 0.533 | N/A * | 0.872 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.663 | N/A * | 0.535 | N/A * | 0.874 | N/A * | undefined | undefined | 1.000 | 0.000 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

