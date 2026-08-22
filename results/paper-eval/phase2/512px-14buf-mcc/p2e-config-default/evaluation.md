# Evaluation: detections_config-default_run01

**Generated**: 2026-08-21T13:44:23.240971+00:00  
**Detections**: 752  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.138 | N/A * | 0.118 | N/A * | 0.165 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 10m | 0.395 | N/A * | 0.339 | N/A * | 0.473 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 15m | 0.525 | N/A * | 0.451 | N/A * | 0.629 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 20m | 0.606 | N/A * | 0.520 | N/A * | 0.725 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 25m | 0.649 | N/A * | 0.557 | N/A * | 0.777 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 30m | 0.671 | N/A * | 0.576 | N/A * | 0.803 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 35m | 0.691 | N/A * | 0.593 | N/A * | 0.828 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 40m | 0.713 | N/A * | 0.612 | N/A * | 0.853 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 45m | 0.724 | N/A * | 0.621 | N/A * | 0.866 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 50m | 0.734 | N/A * | 0.630 | N/A * | 0.879 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 75m | 0.747 | N/A * | 0.641 | N/A * | 0.894 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 100m | 0.753 | N/A * | 0.646 | N/A * | 0.902 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 125m | 0.761 | N/A * | 0.653 | N/A * | 0.911 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |
| 150m | 0.762 | N/A * | 0.654 | N/A * | 0.913 | N/A * | 0.213 | N/A * | 1.000 | 0.073 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

