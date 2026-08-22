# Evaluation: detections_384_run18

**Generated**: 2026-08-21T13:51:47.737960+00:00  
**Detections**: 624  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.149 | N/A * | 0.127 | N/A * | 0.182 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 10m | 0.280 | N/A * | 0.237 | N/A * | 0.340 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 15m | 0.338 | N/A * | 0.287 | N/A * | 0.411 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 20m | 0.357 | N/A * | 0.303 | N/A * | 0.434 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 25m | 0.380 | N/A * | 0.322 | N/A * | 0.462 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 30m | 0.397 | N/A * | 0.337 | N/A * | 0.483 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 35m | 0.400 | N/A * | 0.340 | N/A * | 0.487 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 40m | 0.406 | N/A * | 0.345 | N/A * | 0.494 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 45m | 0.406 | N/A * | 0.345 | N/A * | 0.494 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 50m | 0.406 | N/A * | 0.345 | N/A * | 0.494 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 75m | 0.408 | N/A * | 0.346 | N/A * | 0.497 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 100m | 0.412 | N/A * | 0.349 | N/A * | 0.501 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 125m | 0.412 | N/A * | 0.349 | N/A * | 0.501 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 150m | 0.412 | N/A * | 0.349 | N/A * | 0.501 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

