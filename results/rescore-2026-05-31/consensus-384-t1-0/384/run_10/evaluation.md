# Evaluation: detections_384_run10

**Generated**: 2026-08-21T13:51:03.741678+00:00  
**Detections**: 589  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.144 | N/A * | 0.126 | N/A * | 0.170 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 10m | 0.285 | N/A * | 0.248 | N/A * | 0.336 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 15m | 0.353 | N/A * | 0.307 | N/A * | 0.416 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 20m | 0.373 | N/A * | 0.324 | N/A * | 0.439 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 25m | 0.383 | N/A * | 0.333 | N/A * | 0.451 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 30m | 0.398 | N/A * | 0.346 | N/A * | 0.469 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 35m | 0.404 | N/A * | 0.351 | N/A * | 0.476 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 40m | 0.406 | N/A * | 0.353 | N/A * | 0.478 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 45m | 0.408 | N/A * | 0.355 | N/A * | 0.480 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 50m | 0.408 | N/A * | 0.355 | N/A * | 0.480 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 75m | 0.410 | N/A * | 0.356 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 100m | 0.412 | N/A * | 0.358 | N/A * | 0.485 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 125m | 0.412 | N/A * | 0.358 | N/A * | 0.485 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 150m | 0.412 | N/A * | 0.358 | N/A * | 0.485 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

