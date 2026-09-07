# Evaluation: pro-text-high-t0-single-pass-run_3-rescore-2026-09-07

**Generated**: 2026-09-07T04:33:31.991502+00:00  
**Detections**: 1060  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.173 | N/A * | 0.122 | N/A * | 0.297 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 10m | 0.380 | N/A * | 0.268 | N/A * | 0.653 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 15m | 0.471 | N/A * | 0.332 | N/A * | 0.809 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 20m | 0.498 | N/A * | 0.351 | N/A * | 0.855 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 25m | 0.506 | N/A * | 0.357 | N/A * | 0.869 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 30m | 0.516 | N/A * | 0.364 | N/A * | 0.887 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 35m | 0.522 | N/A * | 0.368 | N/A * | 0.897 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 40m | 0.526 | N/A * | 0.371 | N/A * | 0.903 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 45m | 0.527 | N/A * | 0.372 | N/A * | 0.906 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 50m | 0.527 | N/A * | 0.372 | N/A * | 0.906 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 75m | 0.532 | N/A * | 0.376 | N/A * | 0.915 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 100m | 0.534 | N/A * | 0.376 | N/A * | 0.917 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 125m | 0.535 | N/A * | 0.377 | N/A * | 0.919 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |
| 150m | 0.536 | N/A * | 0.378 | N/A * | 0.922 | N/A * | 0.408 | N/A * | 0.991 | 0.318 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 2/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

