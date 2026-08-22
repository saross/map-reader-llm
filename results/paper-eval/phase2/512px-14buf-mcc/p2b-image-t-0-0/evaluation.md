# Evaluation: T0.0

**Generated**: 2026-08-21T13:41:09.494411+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.142 | N/A * | 0.120 | N/A * | 0.172 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 10m | 0.344 | N/A * | 0.292 | N/A * | 0.418 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 15m | 0.508 | N/A * | 0.432 | N/A * | 0.618 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 20m | 0.586 | N/A * | 0.498 | N/A * | 0.713 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 25m | 0.637 | N/A * | 0.541 | N/A * | 0.775 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 30m | 0.654 | N/A * | 0.555 | N/A * | 0.795 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 35m | 0.674 | N/A * | 0.572 | N/A * | 0.820 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 40m | 0.686 | N/A * | 0.582 | N/A * | 0.834 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 45m | 0.694 | N/A * | 0.589 | N/A * | 0.844 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 50m | 0.703 | N/A * | 0.597 | N/A * | 0.855 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 75m | 0.719 | N/A * | 0.611 | N/A * | 0.875 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 100m | 0.726 | N/A * | 0.616 | N/A * | 0.882 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 125m | 0.730 | N/A * | 0.620 | N/A * | 0.888 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 150m | 0.733 | N/A * | 0.622 | N/A * | 0.892 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

