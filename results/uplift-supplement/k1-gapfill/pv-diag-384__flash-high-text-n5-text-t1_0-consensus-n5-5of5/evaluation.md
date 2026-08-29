# Evaluation: pv-diag-384__flash-high-text-n5-text-t1_0-consensus-n5-5of5-n1

**Generated**: 2026-08-29T07:05:26.678633+00:00  
**Detections**: 1587  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.132 | N/A * | 0.084 | N/A * | 0.306 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 10m | 0.286 | N/A * | 0.182 | N/A * | 0.664 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 15m | 0.341 | N/A * | 0.217 | N/A * | 0.793 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 20m | 0.363 | N/A * | 0.231 | N/A * | 0.844 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 25m | 0.377 | N/A * | 0.240 | N/A * | 0.876 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 30m | 0.390 | N/A * | 0.248 | N/A * | 0.906 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 35m | 0.392 | N/A * | 0.249 | N/A * | 0.910 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 40m | 0.395 | N/A * | 0.251 | N/A * | 0.917 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 45m | 0.396 | N/A * | 0.252 | N/A * | 0.919 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 50m | 0.398 | N/A * | 0.253 | N/A * | 0.924 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 75m | 0.404 | N/A * | 0.257 | N/A * | 0.938 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 100m | 0.407 | N/A * | 0.260 | N/A * | 0.947 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 125m | 0.408 | N/A * | 0.260 | N/A * | 0.949 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |
| 150m | 0.408 | N/A * | 0.260 | N/A * | 0.949 | N/A * | 0.301 | N/A * | 0.987 | 0.205 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 3/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

