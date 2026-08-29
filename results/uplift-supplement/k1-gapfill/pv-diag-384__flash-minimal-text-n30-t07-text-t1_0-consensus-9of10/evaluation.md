# Evaluation: pv-diag-384__flash-minimal-text-n30-t07-text-t1_0-consensus-9of10-n1

**Generated**: 2026-08-29T07:08:31.577491+00:00  
**Detections**: 1084  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.196 | N/A * | 0.138 | N/A * | 0.343 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 10m | 0.366 | N/A * | 0.257 | N/A * | 0.639 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 15m | 0.448 | N/A * | 0.314 | N/A * | 0.782 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 20m | 0.484 | N/A * | 0.340 | N/A * | 0.846 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 25m | 0.495 | N/A * | 0.347 | N/A * | 0.864 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 30m | 0.504 | N/A * | 0.353 | N/A * | 0.880 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 35m | 0.512 | N/A * | 0.359 | N/A * | 0.894 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 40m | 0.517 | N/A * | 0.362 | N/A * | 0.903 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 45m | 0.519 | N/A * | 0.363 | N/A * | 0.906 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 50m | 0.519 | N/A * | 0.363 | N/A * | 0.906 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 75m | 0.520 | N/A * | 0.364 | N/A * | 0.908 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 100m | 0.521 | N/A * | 0.365 | N/A * | 0.910 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 125m | 0.521 | N/A * | 0.365 | N/A * | 0.910 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |
| 150m | 0.523 | N/A * | 0.366 | N/A * | 0.913 | N/A * | 0.074 | N/A * | 1.000 | 0.012 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

