# Evaluation: detections_384_run24

**Generated**: 2026-08-21T13:52:39.745928+00:00  
**Detections**: 608  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.174 | N/A * | 0.150 | N/A * | 0.209 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 10m | 0.297 | N/A * | 0.255 | N/A * | 0.356 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 15m | 0.349 | N/A * | 0.299 | N/A * | 0.418 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 20m | 0.378 | N/A * | 0.324 | N/A * | 0.453 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 25m | 0.391 | N/A * | 0.336 | N/A * | 0.469 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 30m | 0.399 | N/A * | 0.342 | N/A * | 0.478 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 35m | 0.405 | N/A * | 0.347 | N/A * | 0.485 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 40m | 0.406 | N/A * | 0.349 | N/A * | 0.487 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 45m | 0.408 | N/A * | 0.350 | N/A * | 0.490 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 50m | 0.410 | N/A * | 0.352 | N/A * | 0.492 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 75m | 0.416 | N/A * | 0.357 | N/A * | 0.499 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 100m | 0.418 | N/A * | 0.359 | N/A * | 0.501 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 125m | 0.418 | N/A * | 0.359 | N/A * | 0.501 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 150m | 0.418 | N/A * | 0.359 | N/A * | 0.501 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

