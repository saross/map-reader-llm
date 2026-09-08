# Evaluation: gemini37-55map-2026-08-29__arm2-n3-oracle-p0_95-k3-r2-gt-n1

**Generated**: 2026-09-08T13:08:23.123781+00:00  
**Detections**: 17718  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.140 | N/A * | 0.090 | N/A * | 0.317 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 10m | 0.257 | N/A * | 0.165 | N/A * | 0.581 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 15m | 0.331 | N/A * | 0.212 | N/A * | 0.750 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 20m | 0.375 | N/A * | 0.240 | N/A * | 0.849 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 25m | 0.393 | N/A * | 0.252 | N/A * | 0.891 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 30m | 0.402 | N/A * | 0.258 | N/A * | 0.910 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 35m | 0.406 | N/A * | 0.261 | N/A * | 0.920 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 40m | 0.408 | N/A * | 0.262 | N/A * | 0.924 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 45m | 0.409 | N/A * | 0.263 | N/A * | 0.927 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 50m | 0.410 | N/A * | 0.263 | N/A * | 0.929 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 75m | 0.411 | N/A * | 0.264 | N/A * | 0.931 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 100m | 0.412 | N/A * | 0.264 | N/A * | 0.933 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 125m | 0.413 | N/A * | 0.265 | N/A * | 0.936 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |
| 150m | 0.413 | N/A * | 0.265 | N/A * | 0.936 | N/A * | 0.116 | N/A * | 0.054 | 0.986 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 7889/8541 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

