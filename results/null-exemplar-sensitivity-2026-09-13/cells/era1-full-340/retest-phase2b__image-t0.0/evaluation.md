# Evaluation: retest-phase2b__image-t0.0

**Generated**: 2026-09-13T14:01:15.855358+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.136 | N/A * | 0.116 | N/A * | 0.166 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 10m | 0.331 | N/A * | 0.281 | N/A * | 0.402 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 15m | 0.499 | N/A * | 0.424 | N/A * | 0.607 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 20m | 0.578 | N/A * | 0.491 | N/A * | 0.703 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 25m | 0.632 | N/A * | 0.536 | N/A * | 0.768 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 30m | 0.647 | N/A * | 0.549 | N/A * | 0.786 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 35m | 0.669 | N/A * | 0.568 | N/A * | 0.813 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 40m | 0.682 | N/A * | 0.579 | N/A * | 0.829 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 45m | 0.690 | N/A * | 0.586 | N/A * | 0.839 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 50m | 0.700 | N/A * | 0.594 | N/A * | 0.851 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 75m | 0.718 | N/A * | 0.610 | N/A * | 0.874 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 100m | 0.725 | N/A * | 0.616 | N/A * | 0.882 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 125m | 0.730 | N/A * | 0.620 | N/A * | 0.888 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 150m | 0.733 | N/A * | 0.623 | N/A * | 0.892 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

