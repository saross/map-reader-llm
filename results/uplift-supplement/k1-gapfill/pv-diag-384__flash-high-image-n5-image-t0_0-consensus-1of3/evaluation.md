# Evaluation: pv-diag-384__flash-high-image-n5-image-t0_0-consensus-1of3-n1

**Generated**: 2026-08-29T06:58:23.708124+00:00  
**Detections**: 882  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.105 | N/A * | 0.078 | N/A * | 0.159 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 10m | 0.278 | N/A * | 0.207 | N/A * | 0.421 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 15m | 0.392 | N/A * | 0.292 | N/A * | 0.593 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 20m | 0.486 | N/A * | 0.363 | N/A * | 0.736 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 25m | 0.533 | N/A * | 0.398 | N/A * | 0.807 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 30m | 0.545 | N/A * | 0.407 | N/A * | 0.825 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 35m | 0.560 | N/A * | 0.418 | N/A * | 0.848 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 40m | 0.576 | N/A * | 0.430 | N/A * | 0.871 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 45m | 0.585 | N/A * | 0.436 | N/A * | 0.885 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 50m | 0.589 | N/A * | 0.440 | N/A * | 0.892 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 75m | 0.594 | N/A * | 0.443 | N/A * | 0.899 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 100m | 0.595 | N/A * | 0.444 | N/A * | 0.901 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 125m | 0.601 | N/A * | 0.449 | N/A * | 0.910 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |
| 150m | 0.601 | N/A * | 0.449 | N/A * | 0.910 | N/A * | 0.541 | N/A * | 0.987 | 0.492 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 3/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

