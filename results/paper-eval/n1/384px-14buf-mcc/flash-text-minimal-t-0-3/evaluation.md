# Evaluation: Flash Text MINIMAL T=0.3

**Generated**: 2026-08-21T13:30:16.949139+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.232 | N/A * | 0.163 | N/A * | 0.403 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 10m | 0.421 | N/A * | 0.295 | N/A * | 0.730 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 15m | 0.478 | N/A * | 0.336 | N/A * | 0.830 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 20m | 0.499 | N/A * | 0.351 | N/A * | 0.867 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 25m | 0.509 | N/A * | 0.358 | N/A * | 0.884 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 30m | 0.517 | N/A * | 0.363 | N/A * | 0.897 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 35m | 0.520 | N/A * | 0.366 | N/A * | 0.903 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 40m | 0.522 | N/A * | 0.366 | N/A * | 0.906 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 45m | 0.523 | N/A * | 0.367 | N/A * | 0.907 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 50m | 0.523 | N/A * | 0.367 | N/A * | 0.908 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 75m | 0.523 | N/A * | 0.367 | N/A * | 0.908 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 100m | 0.525 | N/A * | 0.369 | N/A * | 0.911 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 125m | 0.527 | N/A * | 0.370 | N/A * | 0.915 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |
| 150m | 0.527 | N/A * | 0.370 | N/A * | 0.915 | N/A * | 0.039 | N/A * | 0.997 | 0.008 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

