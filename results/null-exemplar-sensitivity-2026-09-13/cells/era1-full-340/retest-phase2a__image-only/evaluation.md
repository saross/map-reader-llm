# Evaluation: retest-phase2a__image-only

**Generated**: 2026-09-13T14:01:02.263816+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.081 | N/A * | 0.066 | N/A * | 0.105 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 10m | 0.213 | N/A * | 0.174 | N/A * | 0.275 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 15m | 0.363 | N/A * | 0.296 | N/A * | 0.468 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 20m | 0.457 | N/A * | 0.373 | N/A * | 0.590 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 25m | 0.518 | N/A * | 0.423 | N/A * | 0.668 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 30m | 0.567 | N/A * | 0.463 | N/A * | 0.731 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 35m | 0.594 | N/A * | 0.485 | N/A * | 0.766 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 40m | 0.614 | N/A * | 0.501 | N/A * | 0.792 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 45m | 0.631 | N/A * | 0.515 | N/A * | 0.814 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 50m | 0.645 | N/A * | 0.527 | N/A * | 0.832 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 75m | 0.662 | N/A * | 0.541 | N/A * | 0.854 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 100m | 0.670 | N/A * | 0.547 | N/A * | 0.865 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 125m | 0.675 | N/A * | 0.551 | N/A * | 0.871 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |
| 150m | 0.679 | N/A * | 0.554 | N/A * | 0.876 | N/A * | 0.107 | N/A * | 0.998 | 0.025 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

