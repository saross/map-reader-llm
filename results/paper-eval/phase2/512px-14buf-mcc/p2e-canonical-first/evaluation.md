# Evaluation: detections_canonical-first_run01

**Generated**: 2026-08-21T13:44:00.624044+00:00  
**Detections**: 771  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.139 | N/A * | 0.118 | N/A * | 0.169 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 10m | 0.386 | N/A * | 0.328 | N/A * | 0.469 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 15m | 0.528 | N/A * | 0.449 | N/A * | 0.642 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 20m | 0.599 | N/A * | 0.508 | N/A * | 0.727 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 25m | 0.630 | N/A * | 0.536 | N/A * | 0.766 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 30m | 0.664 | N/A * | 0.564 | N/A * | 0.807 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 35m | 0.689 | N/A * | 0.585 | N/A * | 0.837 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 40m | 0.715 | N/A * | 0.607 | N/A * | 0.868 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 45m | 0.724 | N/A * | 0.615 | N/A * | 0.879 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 50m | 0.730 | N/A * | 0.620 | N/A * | 0.887 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 75m | 0.739 | N/A * | 0.628 | N/A * | 0.898 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 100m | 0.739 | N/A * | 0.628 | N/A * | 0.898 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 125m | 0.744 | N/A * | 0.632 | N/A * | 0.903 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 150m | 0.747 | N/A * | 0.634 | N/A * | 0.907 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 2/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

