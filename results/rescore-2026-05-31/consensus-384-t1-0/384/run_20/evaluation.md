# Evaluation: detections_384_run20

**Generated**: 2026-08-21T13:52:06.393687+00:00  
**Detections**: 544  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.155 | N/A * | 0.140 | N/A * | 0.175 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 10m | 0.317 | N/A * | 0.285 | N/A * | 0.356 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 15m | 0.378 | N/A * | 0.340 | N/A * | 0.425 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 20m | 0.396 | N/A * | 0.357 | N/A * | 0.446 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 25m | 0.413 | N/A * | 0.371 | N/A * | 0.464 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 30m | 0.419 | N/A * | 0.377 | N/A * | 0.471 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 35m | 0.425 | N/A * | 0.382 | N/A * | 0.478 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 40m | 0.427 | N/A * | 0.384 | N/A * | 0.480 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 45m | 0.429 | N/A * | 0.386 | N/A * | 0.483 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 50m | 0.431 | N/A * | 0.388 | N/A * | 0.485 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 75m | 0.437 | N/A * | 0.393 | N/A * | 0.492 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 100m | 0.441 | N/A * | 0.397 | N/A * | 0.497 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 125m | 0.441 | N/A * | 0.397 | N/A * | 0.497 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 150m | 0.441 | N/A * | 0.397 | N/A * | 0.497 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

