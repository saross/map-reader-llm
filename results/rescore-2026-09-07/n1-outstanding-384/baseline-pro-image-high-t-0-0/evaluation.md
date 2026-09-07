# Evaluation: baseline-pro-image-high-t-0-0-rescore-2026-09-07

**Generated**: 2026-09-07T04:34:44.247994+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.097 | N/A * | 0.076 | N/A * | 0.131 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 10m | 0.308 | N/A * | 0.244 | N/A * | 0.418 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 15m | 0.452 | N/A * | 0.358 | N/A * | 0.613 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 20m | 0.545 | N/A * | 0.431 | N/A * | 0.739 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 25m | 0.585 | N/A * | 0.463 | N/A * | 0.793 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 30m | 0.621 | N/A * | 0.492 | N/A * | 0.842 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 35m | 0.644 | N/A * | 0.510 | N/A * | 0.874 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 40m | 0.658 | N/A * | 0.521 | N/A * | 0.893 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 45m | 0.666 | N/A * | 0.527 | N/A * | 0.903 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 50m | 0.666 | N/A * | 0.527 | N/A * | 0.903 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 75m | 0.673 | N/A * | 0.533 | N/A * | 0.913 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 100m | 0.675 | N/A * | 0.535 | N/A * | 0.916 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 125m | 0.678 | N/A * | 0.537 | N/A * | 0.920 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |
| 150m | 0.680 | N/A * | 0.539 | N/A * | 0.923 | N/A * | 0.648 | N/A * | 0.988 | 0.625 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

