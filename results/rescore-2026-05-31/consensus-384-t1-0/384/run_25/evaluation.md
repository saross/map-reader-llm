# Evaluation: detections_384_run25

**Generated**: 2026-08-21T13:52:43.200033+00:00  
**Detections**: 575  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.146 | N/A * | 0.129 | N/A * | 0.170 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 10m | 0.293 | N/A * | 0.257 | N/A * | 0.340 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 15m | 0.343 | N/A * | 0.301 | N/A * | 0.398 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 20m | 0.368 | N/A * | 0.324 | N/A * | 0.428 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 25m | 0.382 | N/A * | 0.336 | N/A * | 0.444 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 30m | 0.396 | N/A * | 0.348 | N/A * | 0.460 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 35m | 0.406 | N/A * | 0.356 | N/A * | 0.471 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 40m | 0.410 | N/A * | 0.360 | N/A * | 0.476 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 45m | 0.410 | N/A * | 0.360 | N/A * | 0.476 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 50m | 0.410 | N/A * | 0.360 | N/A * | 0.476 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 75m | 0.414 | N/A * | 0.363 | N/A * | 0.480 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 100m | 0.416 | N/A * | 0.365 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 125m | 0.416 | N/A * | 0.365 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 150m | 0.416 | N/A * | 0.365 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

