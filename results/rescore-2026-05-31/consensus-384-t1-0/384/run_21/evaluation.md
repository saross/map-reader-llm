# Evaluation: detections_384_run21

**Generated**: 2026-08-21T13:52:20.670902+00:00  
**Detections**: 605  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.175 | N/A * | 0.150 | N/A * | 0.209 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 10m | 0.314 | N/A * | 0.269 | N/A * | 0.375 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 15m | 0.356 | N/A * | 0.306 | N/A * | 0.425 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 20m | 0.390 | N/A * | 0.336 | N/A * | 0.467 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 25m | 0.402 | N/A * | 0.345 | N/A * | 0.480 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 30m | 0.408 | N/A * | 0.350 | N/A * | 0.487 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 35m | 0.411 | N/A * | 0.354 | N/A * | 0.492 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 40m | 0.413 | N/A * | 0.355 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 45m | 0.413 | N/A * | 0.355 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 50m | 0.413 | N/A * | 0.355 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 75m | 0.419 | N/A * | 0.360 | N/A * | 0.501 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 100m | 0.421 | N/A * | 0.362 | N/A * | 0.503 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 125m | 0.421 | N/A * | 0.362 | N/A * | 0.503 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 150m | 0.421 | N/A * | 0.362 | N/A * | 0.503 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

