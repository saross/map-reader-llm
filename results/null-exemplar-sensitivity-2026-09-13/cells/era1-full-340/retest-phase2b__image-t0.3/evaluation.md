# Evaluation: retest-phase2b__image-t0.3

**Generated**: 2026-09-13T14:00:54.167858+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.132 | N/A * | 0.112 | N/A * | 0.160 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 10m | 0.331 | N/A * | 0.282 | N/A * | 0.401 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 15m | 0.484 | N/A * | 0.412 | N/A * | 0.586 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 20m | 0.570 | N/A * | 0.485 | N/A * | 0.690 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 25m | 0.616 | N/A * | 0.524 | N/A * | 0.745 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 30m | 0.646 | N/A * | 0.550 | N/A * | 0.782 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 35m | 0.670 | N/A * | 0.571 | N/A * | 0.811 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 40m | 0.681 | N/A * | 0.580 | N/A * | 0.825 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 45m | 0.695 | N/A * | 0.592 | N/A * | 0.842 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 50m | 0.703 | N/A * | 0.599 | N/A * | 0.851 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 75m | 0.722 | N/A * | 0.615 | N/A * | 0.874 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 100m | 0.727 | N/A * | 0.619 | N/A * | 0.880 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 125m | 0.731 | N/A * | 0.623 | N/A * | 0.885 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |
| 150m | 0.733 | N/A * | 0.624 | N/A * | 0.887 | N/A * | 0.131 | N/A * | 0.998 | 0.033 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

