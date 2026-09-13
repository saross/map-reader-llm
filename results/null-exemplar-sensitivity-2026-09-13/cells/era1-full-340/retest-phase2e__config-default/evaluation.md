# Evaluation: retest-phase2e__config-default

**Generated**: 2026-09-13T14:02:40.873608+00:00  
**Detections**: 693  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.135 | N/A * | 0.115 | N/A * | 0.162 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 10m | 0.385 | N/A * | 0.329 | N/A * | 0.463 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 15m | 0.516 | N/A * | 0.442 | N/A * | 0.621 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 20m | 0.597 | N/A * | 0.511 | N/A * | 0.718 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 25m | 0.642 | N/A * | 0.550 | N/A * | 0.773 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 30m | 0.664 | N/A * | 0.569 | N/A * | 0.799 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 35m | 0.686 | N/A * | 0.587 | N/A * | 0.826 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 40m | 0.708 | N/A * | 0.606 | N/A * | 0.852 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 45m | 0.720 | N/A * | 0.616 | N/A * | 0.866 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 50m | 0.730 | N/A * | 0.625 | N/A * | 0.878 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 75m | 0.742 | N/A * | 0.635 | N/A * | 0.892 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 100m | 0.749 | N/A * | 0.641 | N/A * | 0.901 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 125m | 0.757 | N/A * | 0.648 | N/A * | 0.911 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |
| 150m | 0.759 | N/A * | 0.649 | N/A * | 0.913 | N/A * | 0.175 | N/A * | 1.000 | 0.049 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/315 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

