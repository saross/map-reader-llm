# Evaluation: stride-55map-2026-08-25__g384-ov192-55map-n10-carried-p0_15-k10-r2-gt-n1

**Generated**: 2026-09-07T06:11:16.929961+00:00  
**Detections**: 40746  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.055 | N/A * | 0.031 | N/A * | 0.252 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 10m | 0.114 | N/A * | 0.064 | N/A * | 0.521 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 15m | 0.155 | N/A * | 0.087 | N/A * | 0.706 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 20m | 0.180 | N/A * | 0.101 | N/A * | 0.820 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 25m | 0.193 | N/A * | 0.108 | N/A * | 0.879 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 30m | 0.198 | N/A * | 0.111 | N/A * | 0.904 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 35m | 0.201 | N/A * | 0.113 | N/A * | 0.918 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 40m | 0.203 | N/A * | 0.114 | N/A * | 0.924 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 45m | 0.203 | N/A * | 0.114 | N/A * | 0.926 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 50m | 0.204 | N/A * | 0.114 | N/A * | 0.929 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 75m | 0.205 | N/A * | 0.115 | N/A * | 0.934 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 100m | 0.206 | N/A * | 0.115 | N/A * | 0.937 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 125m | 0.206 | N/A * | 0.116 | N/A * | 0.940 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |
| 150m | 0.207 | N/A * | 0.116 | N/A * | 0.943 | N/A * | -0.011 | N/A * | 0.073 | 0.921 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 7881/8541 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

