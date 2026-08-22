# Evaluation: detections_384_run04

**Generated**: 2026-08-21T13:53:21.747668+00:00  
**Detections**: 604  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.158 | N/A * | 0.136 | N/A * | 0.189 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 10m | 0.306 | N/A * | 0.263 | N/A * | 0.365 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 15m | 0.354 | N/A * | 0.305 | N/A * | 0.423 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 20m | 0.379 | N/A * | 0.326 | N/A * | 0.453 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 25m | 0.397 | N/A * | 0.341 | N/A * | 0.474 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 30m | 0.406 | N/A * | 0.349 | N/A * | 0.485 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 35m | 0.412 | N/A * | 0.354 | N/A * | 0.492 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 40m | 0.416 | N/A * | 0.358 | N/A * | 0.497 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 45m | 0.416 | N/A * | 0.358 | N/A * | 0.497 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 50m | 0.416 | N/A * | 0.358 | N/A * | 0.497 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 75m | 0.418 | N/A * | 0.359 | N/A * | 0.499 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 100m | 0.422 | N/A * | 0.363 | N/A * | 0.503 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 125m | 0.422 | N/A * | 0.363 | N/A * | 0.503 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 150m | 0.422 | N/A * | 0.363 | N/A * | 0.503 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

