# Evaluation: detections_pure-positive-2hp_run01

**Generated**: 2026-08-21T13:42:22.688180+00:00  
**Detections**: 823  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.148 | N/A * | 0.123 | N/A * | 0.187 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.339 | N/A * | 0.281 | N/A * | 0.429 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.501 | N/A * | 0.414 | N/A * | 0.633 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.571 | N/A * | 0.473 | N/A * | 0.722 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.617 | N/A * | 0.510 | N/A * | 0.779 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.631 | N/A * | 0.522 | N/A * | 0.798 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.653 | N/A * | 0.541 | N/A * | 0.826 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.665 | N/A * | 0.550 | N/A * | 0.840 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.671 | N/A * | 0.555 | N/A * | 0.848 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.678 | N/A * | 0.561 | N/A * | 0.857 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.690 | N/A * | 0.571 | N/A * | 0.872 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.696 | N/A * | 0.576 | N/A * | 0.879 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.698 | N/A * | 0.577 | N/A * | 0.881 | N/A * | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.700 | N/A * | 0.580 | N/A * | 0.885 | N/A * | undefined | undefined | 1.000 | 0.000 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 2/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

