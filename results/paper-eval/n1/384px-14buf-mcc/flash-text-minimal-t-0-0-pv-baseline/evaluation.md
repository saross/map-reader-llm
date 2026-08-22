# Evaluation: Flash Text MINIMAL T=0.0 (PV baseline)

**Generated**: 2026-08-21T13:28:52.557653+00:00  
**Detections**: 1047  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.269 | N/A * | 0.190 | N/A * | 0.458 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 10m | 0.443 | N/A * | 0.313 | N/A * | 0.754 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 15m | 0.498 | N/A * | 0.352 | N/A * | 0.848 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 20m | 0.520 | N/A * | 0.368 | N/A * | 0.885 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 25m | 0.526 | N/A * | 0.372 | N/A * | 0.897 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 30m | 0.530 | N/A * | 0.375 | N/A * | 0.903 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 35m | 0.533 | N/A * | 0.377 | N/A * | 0.908 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 40m | 0.536 | N/A * | 0.379 | N/A * | 0.913 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 45m | 0.536 | N/A * | 0.379 | N/A * | 0.913 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 50m | 0.536 | N/A * | 0.379 | N/A * | 0.913 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 75m | 0.537 | N/A * | 0.380 | N/A * | 0.915 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 100m | 0.538 | N/A * | 0.381 | N/A * | 0.917 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 125m | 0.540 | N/A * | 0.382 | N/A * | 0.919 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |
| 150m | 0.540 | N/A * | 0.382 | N/A * | 0.919 | N/A * | -0.004 | N/A * | 0.996 | 0.004 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

