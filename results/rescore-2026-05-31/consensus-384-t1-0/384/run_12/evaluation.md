# Evaluation: detections_384_run12

**Generated**: 2026-08-21T13:51:09.708772+00:00  
**Detections**: 577  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.174 | N/A * | 0.152 | N/A * | 0.202 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 10m | 0.332 | N/A * | 0.291 | N/A * | 0.386 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 15m | 0.385 | N/A * | 0.338 | N/A * | 0.448 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 20m | 0.403 | N/A * | 0.354 | N/A * | 0.469 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 25m | 0.413 | N/A * | 0.362 | N/A * | 0.480 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 30m | 0.419 | N/A * | 0.367 | N/A * | 0.487 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 35m | 0.423 | N/A * | 0.371 | N/A * | 0.492 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 40m | 0.427 | N/A * | 0.374 | N/A * | 0.497 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 45m | 0.427 | N/A * | 0.374 | N/A * | 0.497 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 50m | 0.429 | N/A * | 0.376 | N/A * | 0.499 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 75m | 0.433 | N/A * | 0.380 | N/A * | 0.503 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 100m | 0.435 | N/A * | 0.381 | N/A * | 0.506 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 125m | 0.435 | N/A * | 0.381 | N/A * | 0.506 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |
| 150m | 0.435 | N/A * | 0.381 | N/A * | 0.506 | N/A * | 0.038 | N/A * | 0.511 | 0.527 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 247/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

