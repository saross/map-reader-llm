# Evaluation: detections_pro-text-high-t0_run03

**Generated**: 2026-08-21T13:57:31.663369+00:00  
**Detections**: 1004  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.171 | N/A * | 0.122 | N/A * | 0.283 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 10m | 0.379 | N/A * | 0.272 | N/A * | 0.628 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 15m | 0.468 | N/A * | 0.336 | N/A * | 0.775 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 20m | 0.495 | N/A * | 0.355 | N/A * | 0.818 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 25m | 0.503 | N/A * | 0.361 | N/A * | 0.832 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 30m | 0.514 | N/A * | 0.368 | N/A * | 0.851 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 35m | 0.520 | N/A * | 0.372 | N/A * | 0.860 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 40m | 0.524 | N/A * | 0.376 | N/A * | 0.867 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 45m | 0.525 | N/A * | 0.377 | N/A * | 0.869 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 50m | 0.525 | N/A * | 0.377 | N/A * | 0.869 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 75m | 0.531 | N/A * | 0.381 | N/A * | 0.878 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 100m | 0.532 | N/A * | 0.382 | N/A * | 0.880 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 125m | 0.534 | N/A * | 0.383 | N/A * | 0.883 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |
| 150m | 0.535 | N/A * | 0.384 | N/A * | 0.885 | N/A * | 0.381 | N/A * | 0.961 | 0.345 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 27/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

