# Evaluation: pro-text-high-t0-single-pass-run_2-rescore-2026-09-07

**Generated**: 2026-09-07T04:32:38.653407+00:00  
**Detections**: 1112  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.167 | N/A * | 0.116 | N/A * | 0.297 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 10m | 0.378 | N/A * | 0.263 | N/A * | 0.671 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 15m | 0.462 | N/A * | 0.321 | N/A * | 0.821 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 20m | 0.485 | N/A * | 0.337 | N/A * | 0.862 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 25m | 0.495 | N/A * | 0.344 | N/A * | 0.880 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 30m | 0.505 | N/A * | 0.352 | N/A * | 0.899 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 35m | 0.509 | N/A * | 0.354 | N/A * | 0.906 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 40m | 0.513 | N/A * | 0.357 | N/A * | 0.913 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 45m | 0.513 | N/A * | 0.357 | N/A * | 0.913 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 50m | 0.514 | N/A * | 0.358 | N/A * | 0.915 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 75m | 0.520 | N/A * | 0.361 | N/A * | 0.924 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 100m | 0.521 | N/A * | 0.362 | N/A * | 0.926 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 125m | 0.522 | N/A * | 0.363 | N/A * | 0.929 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |
| 150m | 0.522 | N/A * | 0.363 | N/A * | 0.929 | N/A * | 0.392 | N/A * | 0.991 | 0.298 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 3/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

