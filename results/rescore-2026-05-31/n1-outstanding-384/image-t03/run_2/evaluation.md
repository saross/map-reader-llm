# Evaluation: detections_image-t03_run02

**Generated**: 2026-08-21T13:55:50.594151+00:00  
**Detections**: 746  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.154 | N/A * | 0.122 | N/A * | 0.209 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 10m | 0.406 | N/A * | 0.322 | N/A * | 0.552 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 15m | 0.522 | N/A * | 0.413 | N/A * | 0.708 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 20m | 0.594 | N/A * | 0.470 | N/A * | 0.807 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 25m | 0.638 | N/A * | 0.505 | N/A * | 0.867 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 30m | 0.659 | N/A * | 0.521 | N/A * | 0.894 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 35m | 0.667 | N/A * | 0.528 | N/A * | 0.906 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 40m | 0.671 | N/A * | 0.531 | N/A * | 0.910 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 45m | 0.674 | N/A * | 0.533 | N/A * | 0.915 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 50m | 0.676 | N/A * | 0.535 | N/A * | 0.917 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 75m | 0.688 | N/A * | 0.544 | N/A * | 0.933 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 100m | 0.691 | N/A * | 0.547 | N/A * | 0.938 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 125m | 0.693 | N/A * | 0.548 | N/A * | 0.940 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |
| 150m | 0.693 | N/A * | 0.548 | N/A * | 0.940 | N/A * | 0.293 | N/A * | 0.987 | 0.198 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 5/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

