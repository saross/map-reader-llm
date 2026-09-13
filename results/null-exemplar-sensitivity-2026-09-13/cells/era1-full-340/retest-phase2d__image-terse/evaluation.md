# Evaluation: retest-phase2d__image-terse

**Generated**: 2026-09-13T14:02:19.949587+00:00  
**Detections**: 711  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.121 | N/A * | 0.103 | N/A * | 0.148 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 10m | 0.331 | N/A * | 0.280 | N/A * | 0.404 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 15m | 0.495 | N/A * | 0.419 | N/A * | 0.605 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 20m | 0.596 | N/A * | 0.505 | N/A * | 0.728 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 25m | 0.626 | N/A * | 0.530 | N/A * | 0.765 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 30m | 0.638 | N/A * | 0.540 | N/A * | 0.779 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 35m | 0.663 | N/A * | 0.561 | N/A * | 0.809 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 40m | 0.686 | N/A * | 0.581 | N/A * | 0.838 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 45m | 0.699 | N/A * | 0.592 | N/A * | 0.854 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 50m | 0.709 | N/A * | 0.601 | N/A * | 0.866 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 75m | 0.729 | N/A * | 0.617 | N/A * | 0.890 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 100m | 0.731 | N/A * | 0.619 | N/A * | 0.892 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 125m | 0.734 | N/A * | 0.622 | N/A * | 0.897 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |
| 150m | 0.738 | N/A * | 0.625 | N/A * | 0.901 | N/A * | 0.190 | N/A * | 1.000 | 0.057 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/315 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

