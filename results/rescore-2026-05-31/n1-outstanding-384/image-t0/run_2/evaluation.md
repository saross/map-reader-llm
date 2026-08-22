# Evaluation: detections_image-t0_run02

**Generated**: 2026-08-21T13:55:30.810714+00:00  
**Detections**: 747  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.159 | N/A * | 0.126 | N/A * | 0.216 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 10m | 0.401 | N/A * | 0.317 | N/A * | 0.545 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 15m | 0.535 | N/A * | 0.423 | N/A * | 0.726 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 20m | 0.596 | N/A * | 0.471 | N/A * | 0.809 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 25m | 0.631 | N/A * | 0.499 | N/A * | 0.858 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 30m | 0.653 | N/A * | 0.517 | N/A * | 0.887 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 35m | 0.665 | N/A * | 0.526 | N/A * | 0.903 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 40m | 0.672 | N/A * | 0.531 | N/A * | 0.913 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 45m | 0.678 | N/A * | 0.537 | N/A * | 0.922 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 50m | 0.678 | N/A * | 0.537 | N/A * | 0.922 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 75m | 0.685 | N/A * | 0.542 | N/A * | 0.931 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 100m | 0.689 | N/A * | 0.545 | N/A * | 0.936 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 125m | 0.692 | N/A * | 0.547 | N/A * | 0.940 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |
| 150m | 0.692 | N/A * | 0.547 | N/A * | 0.940 | N/A * | 0.316 | N/A * | 0.996 | 0.202 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 4/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

