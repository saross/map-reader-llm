# Evaluation: T0.7

**Generated**: 2026-08-21T13:41:11.733714+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.119 | N/A * | 0.100 | N/A * | 0.147 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 10m | 0.298 | N/A * | 0.251 | N/A * | 0.367 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 15m | 0.448 | N/A * | 0.378 | N/A * | 0.551 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 20m | 0.537 | N/A * | 0.452 | N/A * | 0.660 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 25m | 0.597 | N/A * | 0.503 | N/A * | 0.734 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 30m | 0.634 | N/A * | 0.534 | N/A * | 0.779 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 35m | 0.657 | N/A * | 0.553 | N/A * | 0.808 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 40m | 0.673 | N/A * | 0.567 | N/A * | 0.828 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 45m | 0.688 | N/A * | 0.580 | N/A * | 0.846 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 50m | 0.699 | N/A * | 0.589 | N/A * | 0.859 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 75m | 0.717 | N/A * | 0.604 | N/A * | 0.881 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 100m | 0.722 | N/A * | 0.609 | N/A * | 0.888 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 125m | 0.727 | N/A * | 0.612 | N/A * | 0.894 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |
| 150m | 0.732 | N/A * | 0.617 | N/A * | 0.900 | N/A * | 0.173 | N/A * | 1.000 | 0.049 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

