# Evaluation: detections_384_run03

**Generated**: 2026-08-21T13:53:17.046581+00:00  
**Detections**: 579  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.136 | N/A * | 0.119 | N/A * | 0.159 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 10m | 0.298 | N/A * | 0.261 | N/A * | 0.347 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 15m | 0.361 | N/A * | 0.316 | N/A * | 0.421 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 20m | 0.377 | N/A * | 0.330 | N/A * | 0.439 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 25m | 0.389 | N/A * | 0.340 | N/A * | 0.453 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 30m | 0.398 | N/A * | 0.349 | N/A * | 0.464 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 35m | 0.410 | N/A * | 0.359 | N/A * | 0.478 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 40m | 0.412 | N/A * | 0.361 | N/A * | 0.480 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 45m | 0.412 | N/A * | 0.361 | N/A * | 0.480 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 50m | 0.412 | N/A * | 0.361 | N/A * | 0.480 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 75m | 0.422 | N/A * | 0.370 | N/A * | 0.492 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 100m | 0.424 | N/A * | 0.371 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 125m | 0.424 | N/A * | 0.371 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 150m | 0.424 | N/A * | 0.371 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

