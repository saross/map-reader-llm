# Evaluation: detections_image-t03_run01

**Generated**: 2026-08-21T13:55:49.631542+00:00  
**Detections**: 753  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.145 | N/A * | 0.114 | N/A * | 0.198 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 10m | 0.391 | N/A * | 0.308 | N/A * | 0.533 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 15m | 0.527 | N/A * | 0.416 | N/A * | 0.720 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 20m | 0.594 | N/A * | 0.469 | N/A * | 0.811 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 25m | 0.625 | N/A * | 0.493 | N/A * | 0.853 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 30m | 0.648 | N/A * | 0.511 | N/A * | 0.885 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 35m | 0.658 | N/A * | 0.519 | N/A * | 0.899 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 40m | 0.665 | N/A * | 0.525 | N/A * | 0.908 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 45m | 0.667 | N/A * | 0.526 | N/A * | 0.910 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 50m | 0.675 | N/A * | 0.532 | N/A * | 0.922 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 75m | 0.682 | N/A * | 0.538 | N/A * | 0.931 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 100m | 0.685 | N/A * | 0.540 | N/A * | 0.936 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 125m | 0.687 | N/A * | 0.542 | N/A * | 0.938 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |
| 150m | 0.689 | N/A * | 0.543 | N/A * | 0.940 | N/A * | 0.306 | N/A * | 0.991 | 0.202 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 4/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

