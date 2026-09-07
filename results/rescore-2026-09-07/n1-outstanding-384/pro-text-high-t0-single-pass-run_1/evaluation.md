# Evaluation: pro-text-high-t0-single-pass-run_1-rescore-2026-09-07

**Generated**: 2026-09-07T04:31:45.314956+00:00  
**Detections**: 1090  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.174 | N/A * | 0.122 | N/A * | 0.306 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 10m | 0.386 | N/A * | 0.270 | N/A * | 0.676 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 15m | 0.464 | N/A * | 0.325 | N/A * | 0.814 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 20m | 0.493 | N/A * | 0.345 | N/A * | 0.864 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 25m | 0.502 | N/A * | 0.351 | N/A * | 0.880 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 30m | 0.511 | N/A * | 0.358 | N/A * | 0.897 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 35m | 0.515 | N/A * | 0.361 | N/A * | 0.903 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 40m | 0.519 | N/A * | 0.363 | N/A * | 0.910 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 45m | 0.519 | N/A * | 0.363 | N/A * | 0.910 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 50m | 0.521 | N/A * | 0.364 | N/A * | 0.913 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 75m | 0.527 | N/A * | 0.369 | N/A * | 0.924 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 100m | 0.528 | N/A * | 0.370 | N/A * | 0.926 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 125m | 0.530 | N/A * | 0.371 | N/A * | 0.929 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |
| 150m | 0.531 | N/A * | 0.372 | N/A * | 0.931 | N/A * | 0.397 | N/A * | 0.996 | 0.295 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 2/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

