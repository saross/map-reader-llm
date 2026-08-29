# Evaluation: pv-diag-384__flash-high-text-n5-text-t0_0-consensus-3of3-n1

**Generated**: 2026-08-29T07:01:39.807108+00:00  
**Detections**: 1139  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.169 | N/A * | 0.117 | N/A * | 0.306 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 10m | 0.375 | N/A * | 0.259 | N/A * | 0.678 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 15m | 0.459 | N/A * | 0.317 | N/A * | 0.830 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 20m | 0.489 | N/A * | 0.338 | N/A * | 0.885 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 25m | 0.502 | N/A * | 0.347 | N/A * | 0.908 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 30m | 0.508 | N/A * | 0.351 | N/A * | 0.919 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 35m | 0.512 | N/A * | 0.354 | N/A * | 0.926 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 40m | 0.516 | N/A * | 0.356 | N/A * | 0.933 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 45m | 0.516 | N/A * | 0.356 | N/A * | 0.933 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 50m | 0.516 | N/A * | 0.356 | N/A * | 0.933 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 75m | 0.521 | N/A * | 0.360 | N/A * | 0.943 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 100m | 0.523 | N/A * | 0.362 | N/A * | 0.947 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 125m | 0.523 | N/A * | 0.362 | N/A * | 0.947 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |
| 150m | 0.523 | N/A * | 0.362 | N/A * | 0.947 | N/A * | 0.383 | N/A * | 0.983 | 0.306 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 2/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

