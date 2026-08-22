# Evaluation: detections_pro-image-high-t0_run02

**Generated**: 2026-08-21T13:56:32.467244+00:00  
**Detections**: 681  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.086 | N/A * | 0.070 | N/A * | 0.110 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 10m | 0.294 | N/A * | 0.241 | N/A * | 0.377 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 15m | 0.443 | N/A * | 0.363 | N/A * | 0.568 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 20m | 0.530 | N/A * | 0.435 | N/A * | 0.680 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 25m | 0.565 | N/A * | 0.463 | N/A * | 0.724 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 30m | 0.595 | N/A * | 0.487 | N/A * | 0.763 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 35m | 0.615 | N/A * | 0.504 | N/A * | 0.788 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 40m | 0.627 | N/A * | 0.514 | N/A * | 0.805 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 45m | 0.634 | N/A * | 0.520 | N/A * | 0.814 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 50m | 0.634 | N/A * | 0.520 | N/A * | 0.814 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 75m | 0.642 | N/A * | 0.526 | N/A * | 0.823 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 100m | 0.643 | N/A * | 0.527 | N/A * | 0.825 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 125m | 0.649 | N/A * | 0.532 | N/A * | 0.832 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |
| 150m | 0.650 | N/A * | 0.533 | N/A * | 0.835 | N/A * | 0.607 | N/A * | 0.943 | 0.643 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 19/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

