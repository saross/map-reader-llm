# Evaluation: retest-phase3a-replication__text-high-t0_7-n30-21of30-n1

**Generated**: 2026-08-29T07:28:09.645492+00:00  
**Detections**: 1328  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.126 | N/A * | 0.089 | N/A * | 0.219 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 10m | 0.303 | N/A * | 0.213 | N/A * | 0.525 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 15m | 0.397 | N/A * | 0.279 | N/A * | 0.688 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 20m | 0.442 | N/A * | 0.311 | N/A * | 0.766 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 25m | 0.470 | N/A * | 0.331 | N/A * | 0.815 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 30m | 0.486 | N/A * | 0.342 | N/A * | 0.842 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 35m | 0.497 | N/A * | 0.349 | N/A * | 0.861 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 40m | 0.508 | N/A * | 0.357 | N/A * | 0.879 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 45m | 0.512 | N/A * | 0.360 | N/A * | 0.887 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 50m | 0.514 | N/A * | 0.361 | N/A * | 0.890 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 75m | 0.526 | N/A * | 0.370 | N/A * | 0.911 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 100m | 0.530 | N/A * | 0.373 | N/A * | 0.918 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 125m | 0.532 | N/A * | 0.374 | N/A * | 0.922 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |
| 150m | 0.533 | N/A * | 0.375 | N/A * | 0.924 | N/A * | 0.307 | N/A * | 0.990 | 0.176 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 4/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

