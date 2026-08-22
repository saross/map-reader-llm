# Evaluation: detections_terse_run01

**Generated**: 2026-08-21T13:43:53.329145+00:00  
**Detections**: 773  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.125 | N/A * | 0.106 | N/A * | 0.152 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 10m | 0.337 | N/A * | 0.286 | N/A * | 0.410 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 15m | 0.503 | N/A * | 0.427 | N/A * | 0.612 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 20m | 0.605 | N/A * | 0.514 | N/A * | 0.737 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 25m | 0.637 | N/A * | 0.541 | N/A * | 0.775 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 30m | 0.649 | N/A * | 0.551 | N/A * | 0.790 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 35m | 0.672 | N/A * | 0.571 | N/A * | 0.818 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 40m | 0.695 | N/A * | 0.590 | N/A * | 0.846 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 45m | 0.707 | N/A * | 0.600 | N/A * | 0.861 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 50m | 0.717 | N/A * | 0.608 | N/A * | 0.872 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 75m | 0.736 | N/A * | 0.625 | N/A * | 0.896 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 100m | 0.738 | N/A * | 0.626 | N/A * | 0.898 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 125m | 0.741 | N/A * | 0.629 | N/A * | 0.902 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |
| 150m | 0.744 | N/A * | 0.631 | N/A * | 0.905 | N/A * | 0.224 | N/A * | 1.000 | 0.081 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

