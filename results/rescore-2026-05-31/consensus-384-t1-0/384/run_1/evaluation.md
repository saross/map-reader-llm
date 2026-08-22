# Evaluation: detections_384_run01

**Generated**: 2026-08-21T13:50:50.646090+00:00  
**Detections**: 570  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.143 | N/A * | 0.126 | N/A * | 0.166 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 10m | 0.310 | N/A * | 0.274 | N/A * | 0.359 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 15m | 0.366 | N/A * | 0.323 | N/A * | 0.423 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 20m | 0.390 | N/A * | 0.344 | N/A * | 0.451 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 25m | 0.402 | N/A * | 0.354 | N/A * | 0.464 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 30m | 0.410 | N/A * | 0.361 | N/A * | 0.474 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 35m | 0.416 | N/A * | 0.367 | N/A * | 0.480 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 40m | 0.422 | N/A * | 0.372 | N/A * | 0.487 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 45m | 0.424 | N/A * | 0.374 | N/A * | 0.490 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 50m | 0.424 | N/A * | 0.374 | N/A * | 0.490 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 75m | 0.428 | N/A * | 0.377 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 100m | 0.428 | N/A * | 0.377 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 125m | 0.428 | N/A * | 0.377 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 150m | 0.428 | N/A * | 0.377 | N/A * | 0.494 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

