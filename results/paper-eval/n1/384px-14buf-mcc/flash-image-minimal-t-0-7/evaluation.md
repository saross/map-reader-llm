# Evaluation: Flash Image MINIMAL T=0.7

**Generated**: 2026-08-22T14:42:15.875282+00:00  
**Runs**: 10  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.136 | N/A * | 0.107 | N/A * | 0.186 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 10m | 0.347 | N/A * | 0.273 | N/A * | 0.475 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 15m | 0.476 | N/A * | 0.374 | N/A * | 0.652 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 20m | 0.553 | N/A * | 0.435 | N/A * | 0.759 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 25m | 0.602 | N/A * | 0.473 | N/A * | 0.825 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 30m | 0.630 | N/A * | 0.496 | N/A * | 0.864 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 35m | 0.647 | N/A * | 0.509 | N/A * | 0.888 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 40m | 0.657 | N/A * | 0.517 | N/A * | 0.901 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 45m | 0.661 | N/A * | 0.520 | N/A * | 0.906 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 50m | 0.666 | N/A * | 0.524 | N/A * | 0.913 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 75m | 0.676 | N/A * | 0.532 | N/A * | 0.928 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 100m | 0.680 | N/A * | 0.535 | N/A * | 0.933 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 125m | 0.682 | N/A * | 0.537 | N/A * | 0.936 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |
| 150m | 0.683 | N/A * | 0.538 | N/A * | 0.937 | N/A * | 0.330 | N/A * | 0.998 | 0.210 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

