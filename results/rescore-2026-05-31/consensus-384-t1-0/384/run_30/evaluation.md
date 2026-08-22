# Evaluation: detections_384_run30

**Generated**: 2026-08-21T13:53:21.264357+00:00  
**Detections**: 564  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.176 | N/A * | 0.156 | N/A * | 0.202 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 10m | 0.314 | N/A * | 0.278 | N/A * | 0.361 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 15m | 0.376 | N/A * | 0.333 | N/A * | 0.432 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 20m | 0.404 | N/A * | 0.358 | N/A * | 0.464 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 25m | 0.410 | N/A * | 0.363 | N/A * | 0.471 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 30m | 0.420 | N/A * | 0.372 | N/A * | 0.483 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 35m | 0.428 | N/A * | 0.379 | N/A * | 0.492 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 40m | 0.432 | N/A * | 0.383 | N/A * | 0.497 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 45m | 0.434 | N/A * | 0.385 | N/A * | 0.499 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 50m | 0.436 | N/A * | 0.387 | N/A * | 0.501 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 75m | 0.440 | N/A * | 0.390 | N/A * | 0.506 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 100m | 0.440 | N/A * | 0.390 | N/A * | 0.506 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 125m | 0.442 | N/A * | 0.392 | N/A * | 0.508 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |
| 150m | 0.442 | N/A * | 0.392 | N/A * | 0.508 | N/A * | 0.034 | N/A * | 0.511 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

