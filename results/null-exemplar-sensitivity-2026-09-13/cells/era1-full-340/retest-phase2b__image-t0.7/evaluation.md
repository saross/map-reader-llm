# Evaluation: retest-phase2b__image-t0.7

**Generated**: 2026-09-13T14:01:01.573572+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.117 | N/A * | 0.099 | N/A * | 0.145 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 10m | 0.289 | N/A * | 0.244 | N/A * | 0.356 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 15m | 0.436 | N/A * | 0.367 | N/A * | 0.537 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 20m | 0.527 | N/A * | 0.444 | N/A * | 0.649 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 25m | 0.587 | N/A * | 0.494 | N/A * | 0.723 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 30m | 0.626 | N/A * | 0.527 | N/A * | 0.771 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 35m | 0.650 | N/A * | 0.547 | N/A * | 0.801 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 40m | 0.666 | N/A * | 0.560 | N/A * | 0.820 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 45m | 0.682 | N/A * | 0.574 | N/A * | 0.841 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 50m | 0.693 | N/A * | 0.583 | N/A * | 0.853 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 75m | 0.712 | N/A * | 0.599 | N/A * | 0.877 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 100m | 0.718 | N/A * | 0.605 | N/A * | 0.884 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 125m | 0.723 | N/A * | 0.609 | N/A * | 0.890 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |
| 150m | 0.729 | N/A * | 0.613 | N/A * | 0.897 | N/A * | 0.164 | N/A * | 1.000 | 0.044 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

