# Evaluation: Pro Image MEDIUM T=0.7

**Generated**: 2026-08-21T13:30:14.034372+00:00  
**Detections**: 941  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.095 | N/A * | 0.069 | N/A * | 0.149 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 10m | 0.259 | N/A * | 0.189 | N/A * | 0.409 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 15m | 0.375 | N/A * | 0.274 | N/A * | 0.593 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 20m | 0.452 | N/A * | 0.331 | N/A * | 0.715 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 25m | 0.498 | N/A * | 0.364 | N/A * | 0.788 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 30m | 0.538 | N/A * | 0.393 | N/A * | 0.851 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 35m | 0.557 | N/A * | 0.407 | N/A * | 0.880 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 40m | 0.567 | N/A * | 0.414 | N/A * | 0.897 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 45m | 0.579 | N/A * | 0.423 | N/A * | 0.915 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 50m | 0.586 | N/A * | 0.428 | N/A * | 0.926 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 75m | 0.592 | N/A * | 0.432 | N/A * | 0.936 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 100m | 0.593 | N/A * | 0.434 | N/A * | 0.938 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 125m | 0.597 | N/A * | 0.437 | N/A * | 0.945 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |
| 150m | 0.597 | N/A * | 0.437 | N/A * | 0.945 | N/A * | 0.598 | N/A * | 0.996 | 0.550 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

