# Evaluation: image-only

**Generated**: 2026-08-21T13:41:10.452281+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.082 | N/A * | 0.067 | N/A * | 0.106 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 10m | 0.224 | N/A * | 0.183 | N/A * | 0.289 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 15m | 0.375 | N/A * | 0.306 | N/A * | 0.485 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 20m | 0.470 | N/A * | 0.383 | N/A * | 0.607 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 25m | 0.528 | N/A * | 0.430 | N/A * | 0.681 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 30m | 0.574 | N/A * | 0.468 | N/A * | 0.742 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 35m | 0.601 | N/A * | 0.490 | N/A * | 0.776 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 40m | 0.620 | N/A * | 0.506 | N/A * | 0.801 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 45m | 0.635 | N/A * | 0.518 | N/A * | 0.821 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 50m | 0.649 | N/A * | 0.529 | N/A * | 0.839 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 75m | 0.666 | N/A * | 0.544 | N/A * | 0.861 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 100m | 0.674 | N/A * | 0.550 | N/A * | 0.871 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 125m | 0.678 | N/A * | 0.553 | N/A * | 0.876 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |
| 150m | 0.682 | N/A * | 0.556 | N/A * | 0.881 | N/A * | 0.109 | N/A * | 0.998 | 0.025 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

