# Evaluation: retest-phase2a__verbose-text-image

**Generated**: 2026-09-13T14:00:52.168725+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.098 | N/A * | 0.082 | N/A * | 0.120 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 10m | 0.260 | N/A * | 0.218 | N/A * | 0.321 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 15m | 0.415 | N/A * | 0.349 | N/A * | 0.512 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 20m | 0.503 | N/A * | 0.423 | N/A * | 0.621 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 25m | 0.563 | N/A * | 0.473 | N/A * | 0.696 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 30m | 0.603 | N/A * | 0.506 | N/A * | 0.744 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 35m | 0.631 | N/A * | 0.530 | N/A * | 0.780 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 40m | 0.651 | N/A * | 0.547 | N/A * | 0.804 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 45m | 0.666 | N/A * | 0.559 | N/A * | 0.822 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 50m | 0.676 | N/A * | 0.568 | N/A * | 0.834 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 75m | 0.697 | N/A * | 0.586 | N/A * | 0.861 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 100m | 0.704 | N/A * | 0.592 | N/A * | 0.870 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 125m | 0.713 | N/A * | 0.599 | N/A * | 0.880 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |
| 150m | 0.719 | N/A * | 0.604 | N/A * | 0.888 | N/A * | 0.271 | N/A * | 1.000 | 0.117 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

