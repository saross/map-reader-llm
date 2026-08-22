# Evaluation: Flash Text HIGH T=0.7

**Generated**: 2026-08-22T14:54:28.786791+00:00  
**Runs**: 30  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.139 | N/A * | 0.090 | N/A * | 0.313 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 10m | 0.292 | N/A * | 0.188 | N/A * | 0.657 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 15m | 0.360 | N/A * | 0.231 | N/A * | 0.808 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 20m | 0.387 | N/A * | 0.249 | N/A * | 0.869 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 25m | 0.398 | N/A * | 0.256 | N/A * | 0.895 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 30m | 0.406 | N/A * | 0.261 | N/A * | 0.912 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 35m | 0.411 | N/A * | 0.264 | N/A * | 0.923 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 40m | 0.413 | N/A * | 0.266 | N/A * | 0.928 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 45m | 0.415 | N/A * | 0.267 | N/A * | 0.932 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 50m | 0.416 | N/A * | 0.268 | N/A * | 0.934 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 75m | 0.420 | N/A * | 0.270 | N/A * | 0.943 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 100m | 0.422 | N/A * | 0.272 | N/A * | 0.948 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 125m | 0.423 | N/A * | 0.272 | N/A * | 0.949 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |
| 150m | 0.423 | N/A * | 0.272 | N/A * | 0.950 | N/A * | 0.331 | N/A * | 0.990 | 0.231 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

