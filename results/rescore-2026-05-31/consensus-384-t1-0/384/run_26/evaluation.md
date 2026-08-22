# Evaluation: detections_384_run26

**Generated**: 2026-08-21T13:52:44.667733+00:00  
**Detections**: 605  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.158 | N/A * | 0.136 | N/A * | 0.189 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 10m | 0.294 | N/A * | 0.253 | N/A * | 0.352 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 15m | 0.354 | N/A * | 0.304 | N/A * | 0.423 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 20m | 0.375 | N/A * | 0.322 | N/A * | 0.448 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 25m | 0.389 | N/A * | 0.334 | N/A * | 0.464 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 30m | 0.402 | N/A * | 0.345 | N/A * | 0.480 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 35m | 0.404 | N/A * | 0.347 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 40m | 0.410 | N/A * | 0.352 | N/A * | 0.490 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 45m | 0.411 | N/A * | 0.354 | N/A * | 0.492 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 50m | 0.413 | N/A * | 0.355 | N/A * | 0.494 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 75m | 0.417 | N/A * | 0.359 | N/A * | 0.499 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 100m | 0.419 | N/A * | 0.360 | N/A * | 0.501 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 125m | 0.419 | N/A * | 0.360 | N/A * | 0.501 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 150m | 0.419 | N/A * | 0.360 | N/A * | 0.501 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

