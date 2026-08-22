# Evaluation: detections_canonical_run01

**Generated**: 2026-08-21T13:41:48.607724+00:00  
**Detections**: 720  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.122 | N/A * | 0.107 | N/A * | 0.143 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 10m | 0.338 | N/A * | 0.296 | N/A * | 0.395 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 15m | 0.518 | N/A * | 0.453 | N/A * | 0.605 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 20m | 0.581 | N/A * | 0.508 | N/A * | 0.679 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 25m | 0.621 | N/A * | 0.543 | N/A * | 0.725 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 30m | 0.653 | N/A * | 0.571 | N/A * | 0.762 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 35m | 0.664 | N/A * | 0.581 | N/A * | 0.775 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 40m | 0.680 | N/A * | 0.594 | N/A * | 0.794 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 45m | 0.688 | N/A * | 0.601 | N/A * | 0.803 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 50m | 0.689 | N/A * | 0.603 | N/A * | 0.805 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 75m | 0.707 | N/A * | 0.618 | N/A * | 0.826 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 100m | 0.709 | N/A * | 0.619 | N/A * | 0.828 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 125m | 0.712 | N/A * | 0.622 | N/A * | 0.831 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |
| 150m | 0.713 | N/A * | 0.624 | N/A * | 0.833 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

