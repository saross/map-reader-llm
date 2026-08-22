# Evaluation: detections_384_run15

**Generated**: 2026-08-21T13:51:28.981325+00:00  
**Detections**: 607  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.154 | N/A * | 0.132 | N/A * | 0.184 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 10m | 0.288 | N/A * | 0.247 | N/A * | 0.345 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 15m | 0.363 | N/A * | 0.311 | N/A * | 0.434 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 20m | 0.386 | N/A * | 0.331 | N/A * | 0.462 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 25m | 0.395 | N/A * | 0.339 | N/A * | 0.474 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 30m | 0.409 | N/A * | 0.351 | N/A * | 0.490 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 35m | 0.415 | N/A * | 0.356 | N/A * | 0.497 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 40m | 0.416 | N/A * | 0.357 | N/A * | 0.499 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 45m | 0.420 | N/A * | 0.361 | N/A * | 0.503 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 50m | 0.422 | N/A * | 0.362 | N/A * | 0.506 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 75m | 0.426 | N/A * | 0.366 | N/A * | 0.510 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 100m | 0.426 | N/A * | 0.366 | N/A * | 0.510 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 125m | 0.426 | N/A * | 0.366 | N/A * | 0.510 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 150m | 0.426 | N/A * | 0.366 | N/A * | 0.510 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

