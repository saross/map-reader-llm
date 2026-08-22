# Evaluation: detections_384_run09

**Generated**: 2026-08-21T13:53:34.407670+00:00  
**Detections**: 585  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.157 | N/A * | 0.137 | N/A * | 0.184 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 10m | 0.296 | N/A * | 0.258 | N/A * | 0.347 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 15m | 0.343 | N/A * | 0.299 | N/A * | 0.402 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 20m | 0.369 | N/A * | 0.321 | N/A * | 0.432 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 25m | 0.384 | N/A * | 0.335 | N/A * | 0.451 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 30m | 0.394 | N/A * | 0.344 | N/A * | 0.462 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 35m | 0.410 | N/A * | 0.357 | N/A * | 0.480 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 40m | 0.410 | N/A * | 0.357 | N/A * | 0.480 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 45m | 0.412 | N/A * | 0.359 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 50m | 0.412 | N/A * | 0.359 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 75m | 0.416 | N/A * | 0.362 | N/A * | 0.487 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 100m | 0.418 | N/A * | 0.364 | N/A * | 0.490 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 125m | 0.420 | N/A * | 0.366 | N/A * | 0.492 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 150m | 0.420 | N/A * | 0.366 | N/A * | 0.492 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

