# Evaluation: T0.3

**Generated**: 2026-08-21T13:41:13.077477+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.133 | N/A * | 0.113 | N/A * | 0.162 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 10m | 0.340 | N/A * | 0.289 | N/A * | 0.414 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 15m | 0.492 | N/A * | 0.418 | N/A * | 0.599 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 20m | 0.575 | N/A * | 0.488 | N/A * | 0.699 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 25m | 0.621 | N/A * | 0.527 | N/A * | 0.756 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 30m | 0.651 | N/A * | 0.553 | N/A * | 0.792 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 35m | 0.674 | N/A * | 0.572 | N/A * | 0.820 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 40m | 0.685 | N/A * | 0.581 | N/A * | 0.833 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 45m | 0.698 | N/A * | 0.592 | N/A * | 0.849 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 50m | 0.704 | N/A * | 0.598 | N/A * | 0.857 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 75m | 0.723 | N/A * | 0.614 | N/A * | 0.879 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 100m | 0.727 | N/A * | 0.617 | N/A * | 0.884 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 125m | 0.731 | N/A * | 0.621 | N/A * | 0.889 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |
| 150m | 0.733 | N/A * | 0.622 | N/A * | 0.891 | N/A * | 0.123 | N/A * | 0.998 | 0.029 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

