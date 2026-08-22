# Evaluation: verbose-text-image

**Generated**: 2026-08-21T13:41:09.376106+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.101 | N/A * | 0.085 | N/A * | 0.124 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 10m | 0.269 | N/A * | 0.226 | N/A * | 0.332 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 15m | 0.427 | N/A * | 0.358 | N/A * | 0.527 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 20m | 0.517 | N/A * | 0.434 | N/A * | 0.639 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 25m | 0.576 | N/A * | 0.483 | N/A * | 0.711 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 30m | 0.613 | N/A * | 0.515 | N/A * | 0.758 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 35m | 0.640 | N/A * | 0.537 | N/A * | 0.790 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 40m | 0.658 | N/A * | 0.553 | N/A * | 0.813 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 45m | 0.672 | N/A * | 0.564 | N/A * | 0.831 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 50m | 0.683 | N/A * | 0.573 | N/A * | 0.844 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 75m | 0.704 | N/A * | 0.591 | N/A * | 0.870 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 100m | 0.711 | N/A * | 0.597 | N/A * | 0.878 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 125m | 0.718 | N/A * | 0.603 | N/A * | 0.887 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |
| 150m | 0.724 | N/A * | 0.608 | N/A * | 0.894 | N/A * | 0.291 | N/A * | 1.000 | 0.135 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

