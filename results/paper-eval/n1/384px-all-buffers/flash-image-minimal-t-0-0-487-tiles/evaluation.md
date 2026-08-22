# Evaluation: Flash Image MINIMAL T=0.0 (487 tiles)

**Generated**: 2026-08-21T13:32:53.914282+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.598 | N/A * | 0.474 | N/A * | 0.812 | N/A * |
| 30m | 0.655 | N/A * | 0.518 | N/A * | 0.889 | N/A * |
| 40m | 0.673 | N/A * | 0.533 | N/A * | 0.914 | N/A * |
| 50m | 0.680 | N/A * | 0.538 | N/A * | 0.923 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

