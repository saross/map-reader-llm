# Evaluation: pro-image-high-t0-single-pass-run_2-rescore-2026-09-07

**Generated**: 2026-09-07T04:32:09.958647+00:00  
**Detections**: 744  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.095 | N/A * | 0.075 | N/A * | 0.129 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 10m | 0.310 | N/A * | 0.246 | N/A * | 0.421 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 15m | 0.458 | N/A * | 0.363 | N/A * | 0.621 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 20m | 0.548 | N/A * | 0.434 | N/A * | 0.743 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 25m | 0.590 | N/A * | 0.468 | N/A * | 0.800 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 30m | 0.626 | N/A * | 0.496 | N/A * | 0.848 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 35m | 0.646 | N/A * | 0.512 | N/A * | 0.876 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 40m | 0.660 | N/A * | 0.523 | N/A * | 0.894 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 45m | 0.667 | N/A * | 0.528 | N/A * | 0.903 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 50m | 0.667 | N/A * | 0.528 | N/A * | 0.903 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 75m | 0.675 | N/A * | 0.535 | N/A * | 0.915 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 100m | 0.677 | N/A * | 0.536 | N/A * | 0.917 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 125m | 0.680 | N/A * | 0.539 | N/A * | 0.922 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 150m | 0.682 | N/A * | 0.540 | N/A * | 0.924 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

