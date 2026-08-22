# Evaluation: detections_scale-4_run01

**Generated**: 2026-08-21T13:43:22.945295+00:00  
**Detections**: 811  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.118 | N/A * | 0.099 | N/A * | 0.148 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 10m | 0.338 | N/A * | 0.281 | N/A * | 0.423 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 15m | 0.499 | N/A * | 0.415 | N/A * | 0.625 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 20m | 0.584 | N/A * | 0.486 | N/A * | 0.731 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 25m | 0.625 | N/A * | 0.520 | N/A * | 0.783 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 30m | 0.637 | N/A * | 0.530 | N/A * | 0.798 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 35m | 0.659 | N/A * | 0.549 | N/A * | 0.826 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 40m | 0.670 | N/A * | 0.557 | N/A * | 0.839 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 45m | 0.683 | N/A * | 0.568 | N/A * | 0.855 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 50m | 0.690 | N/A * | 0.575 | N/A * | 0.865 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 75m | 0.705 | N/A * | 0.587 | N/A * | 0.883 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 100m | 0.705 | N/A * | 0.587 | N/A * | 0.883 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 125m | 0.708 | N/A * | 0.589 | N/A * | 0.887 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |
| 150m | 0.711 | N/A * | 0.592 | N/A * | 0.890 | N/A * | 0.134 | N/A * | 1.000 | 0.029 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

