# Evaluation: retest-phase2c__image-scale-8

**Generated**: 2026-09-13T14:01:41.338499+00:00  
**Detections**: 706  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.137 | N/A * | 0.116 | N/A * | 0.166 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 10m | 0.332 | N/A * | 0.282 | N/A * | 0.404 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 15m | 0.499 | N/A * | 0.423 | N/A * | 0.607 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 20m | 0.577 | N/A * | 0.490 | N/A * | 0.702 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 25m | 0.632 | N/A * | 0.537 | N/A * | 0.769 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 30m | 0.647 | N/A * | 0.550 | N/A * | 0.787 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 35m | 0.669 | N/A * | 0.568 | N/A * | 0.813 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 40m | 0.682 | N/A * | 0.579 | N/A * | 0.830 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 45m | 0.691 | N/A * | 0.586 | N/A * | 0.840 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 50m | 0.701 | N/A * | 0.595 | N/A * | 0.852 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 75m | 0.719 | N/A * | 0.611 | N/A * | 0.874 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 100m | 0.726 | N/A * | 0.616 | N/A * | 0.882 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 125m | 0.731 | N/A * | 0.620 | N/A * | 0.888 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |
| 150m | 0.734 | N/A * | 0.623 | N/A * | 0.892 | N/A * | 0.143 | N/A * | 1.000 | 0.033 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/315 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

