# Evaluation: detections_384_run22

**Generated**: 2026-08-21T13:52:24.513195+00:00  
**Detections**: 609  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.149 | N/A * | 0.128 | N/A * | 0.179 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 10m | 0.320 | N/A * | 0.274 | N/A * | 0.384 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 15m | 0.376 | N/A * | 0.322 | N/A * | 0.451 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 20m | 0.385 | N/A * | 0.330 | N/A * | 0.462 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 25m | 0.397 | N/A * | 0.340 | N/A * | 0.476 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 30m | 0.400 | N/A * | 0.343 | N/A * | 0.480 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 35m | 0.408 | N/A * | 0.350 | N/A * | 0.490 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 40m | 0.410 | N/A * | 0.351 | N/A * | 0.492 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 45m | 0.412 | N/A * | 0.353 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 50m | 0.412 | N/A * | 0.353 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 75m | 0.416 | N/A * | 0.356 | N/A * | 0.499 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 100m | 0.418 | N/A * | 0.358 | N/A * | 0.501 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 125m | 0.418 | N/A * | 0.358 | N/A * | 0.501 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 150m | 0.418 | N/A * | 0.358 | N/A * | 0.501 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

