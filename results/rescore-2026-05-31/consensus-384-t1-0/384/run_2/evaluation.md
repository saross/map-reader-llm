# Evaluation: detections_384_run02

**Generated**: 2026-08-21T13:52:04.939935+00:00  
**Detections**: 593  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.173 | N/A * | 0.150 | N/A * | 0.205 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 10m | 0.323 | N/A * | 0.280 | N/A * | 0.382 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 15m | 0.373 | N/A * | 0.324 | N/A * | 0.441 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 20m | 0.389 | N/A * | 0.337 | N/A * | 0.460 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 25m | 0.395 | N/A * | 0.342 | N/A * | 0.467 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 30m | 0.399 | N/A * | 0.346 | N/A * | 0.471 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 35m | 0.401 | N/A * | 0.347 | N/A * | 0.474 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 40m | 0.401 | N/A * | 0.347 | N/A * | 0.474 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 45m | 0.403 | N/A * | 0.349 | N/A * | 0.476 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 50m | 0.403 | N/A * | 0.349 | N/A * | 0.476 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 75m | 0.405 | N/A * | 0.351 | N/A * | 0.478 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 100m | 0.409 | N/A * | 0.354 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 125m | 0.409 | N/A * | 0.354 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |
| 150m | 0.409 | N/A * | 0.354 | N/A * | 0.483 | N/A * | 0.030 | N/A * | 0.507 | 0.523 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

