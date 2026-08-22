# Evaluation: detections_384_run11

**Generated**: 2026-08-21T13:51:07.839667+00:00  
**Detections**: 583  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.167 | N/A * | 0.146 | N/A * | 0.195 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 10m | 0.312 | N/A * | 0.273 | N/A * | 0.365 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 15m | 0.358 | N/A * | 0.312 | N/A * | 0.418 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 20m | 0.383 | N/A * | 0.335 | N/A * | 0.448 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 25m | 0.401 | N/A * | 0.350 | N/A * | 0.469 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 30m | 0.407 | N/A * | 0.355 | N/A * | 0.476 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 35m | 0.413 | N/A * | 0.360 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 40m | 0.414 | N/A * | 0.362 | N/A * | 0.485 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 45m | 0.420 | N/A * | 0.367 | N/A * | 0.492 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 50m | 0.420 | N/A * | 0.367 | N/A * | 0.492 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 75m | 0.426 | N/A * | 0.372 | N/A * | 0.499 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 100m | 0.428 | N/A * | 0.374 | N/A * | 0.501 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 125m | 0.428 | N/A * | 0.374 | N/A * | 0.501 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 150m | 0.428 | N/A * | 0.374 | N/A * | 0.501 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

