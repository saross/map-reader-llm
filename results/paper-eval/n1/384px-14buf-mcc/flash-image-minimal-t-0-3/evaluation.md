# Evaluation: Flash Image MINIMAL T=0.3

**Generated**: 2026-08-21T13:29:41.179997+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.150 | N/A * | 0.119 | N/A * | 0.205 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 10m | 0.402 | N/A * | 0.318 | N/A * | 0.547 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 15m | 0.525 | N/A * | 0.415 | N/A * | 0.714 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 20m | 0.593 | N/A * | 0.469 | N/A * | 0.807 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 25m | 0.630 | N/A * | 0.498 | N/A * | 0.858 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 30m | 0.653 | N/A * | 0.516 | N/A * | 0.888 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 35m | 0.663 | N/A * | 0.524 | N/A * | 0.903 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 40m | 0.671 | N/A * | 0.530 | N/A * | 0.913 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 45m | 0.673 | N/A * | 0.532 | N/A * | 0.916 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 50m | 0.677 | N/A * | 0.535 | N/A * | 0.921 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 75m | 0.686 | N/A * | 0.542 | N/A * | 0.933 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 100m | 0.689 | N/A * | 0.544 | N/A * | 0.937 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 125m | 0.691 | N/A * | 0.546 | N/A * | 0.939 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |
| 150m | 0.691 | N/A * | 0.546 | N/A * | 0.940 | N/A * | 0.305 | N/A * | 0.991 | 0.200 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

