# Evaluation: retest-phase2e__random

**Generated**: 2026-09-13T14:02:40.246240+00:00  
**Detections**: 747  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.142 | N/A * | 0.118 | N/A * | 0.178 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 10m | 0.324 | N/A * | 0.269 | N/A * | 0.408 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 15m | 0.469 | N/A * | 0.390 | N/A * | 0.590 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 20m | 0.560 | N/A * | 0.465 | N/A * | 0.704 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 25m | 0.602 | N/A * | 0.499 | N/A * | 0.757 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 30m | 0.637 | N/A * | 0.529 | N/A * | 0.801 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 35m | 0.658 | N/A * | 0.546 | N/A * | 0.828 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 40m | 0.668 | N/A * | 0.554 | N/A * | 0.840 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 45m | 0.682 | N/A * | 0.566 | N/A * | 0.858 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 50m | 0.692 | N/A * | 0.574 | N/A * | 0.870 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 75m | 0.707 | N/A * | 0.586 | N/A * | 0.888 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 100m | 0.710 | N/A * | 0.589 | N/A * | 0.892 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 125m | 0.715 | N/A * | 0.593 | N/A * | 0.899 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 150m | 0.715 | N/A * | 0.593 | N/A * | 0.899 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/315 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

