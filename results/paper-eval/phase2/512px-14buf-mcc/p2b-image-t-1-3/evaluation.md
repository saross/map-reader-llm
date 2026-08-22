# Evaluation: T1.3

**Generated**: 2026-08-21T13:42:53.539168+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.087 | N/A * | 0.072 | N/A * | 0.110 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 10m | 0.253 | N/A * | 0.209 | N/A * | 0.319 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 15m | 0.388 | N/A * | 0.321 | N/A * | 0.490 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 20m | 0.492 | N/A * | 0.407 | N/A * | 0.622 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 25m | 0.556 | N/A * | 0.460 | N/A * | 0.703 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 30m | 0.601 | N/A * | 0.498 | N/A * | 0.759 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 35m | 0.624 | N/A * | 0.516 | N/A * | 0.788 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 40m | 0.645 | N/A * | 0.534 | N/A * | 0.815 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 45m | 0.659 | N/A * | 0.545 | N/A * | 0.832 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 50m | 0.671 | N/A * | 0.555 | N/A * | 0.847 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 75m | 0.696 | N/A * | 0.576 | N/A * | 0.879 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 100m | 0.701 | N/A * | 0.580 | N/A * | 0.886 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 125m | 0.706 | N/A * | 0.584 | N/A * | 0.892 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |
| 150m | 0.710 | N/A * | 0.588 | N/A * | 0.897 | N/A * | 0.210 | N/A * | 1.000 | 0.073 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

