# Evaluation: detections_canonical_run01

**Generated**: 2026-08-21T13:43:28.181641+00:00  
**Detections**: 897  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.265 | N/A * | 0.212 | N/A * | 0.352 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.476 | N/A * | 0.381 | N/A * | 0.634 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.558 | N/A * | 0.447 | N/A * | 0.744 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.605 | N/A * | 0.484 | N/A * | 0.805 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.623 | N/A * | 0.498 | N/A * | 0.829 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.636 | N/A * | 0.509 | N/A * | 0.848 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.643 | N/A * | 0.515 | N/A * | 0.857 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.646 | N/A * | 0.517 | N/A * | 0.861 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.649 | N/A * | 0.519 | N/A * | 0.865 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.650 | N/A * | 0.521 | N/A * | 0.866 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.653 | N/A * | 0.523 | N/A * | 0.870 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.655 | N/A * | 0.524 | N/A * | 0.872 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.655 | N/A * | 0.524 | N/A * | 0.872 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.656 | N/A * | 0.525 | N/A * | 0.874 | N/A * | undefined | undefined | 1.000 | 0.000 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

