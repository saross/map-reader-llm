# Evaluation: Pro Text HIGH T=0.0

**Generated**: 2026-08-21T13:36:40.083290+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.494 | N/A * | 0.352 | N/A * | 0.826 | N/A * |
| 30m | 0.515 | N/A * | 0.367 | N/A * | 0.861 | N/A * |
| 40m | 0.523 | N/A * | 0.373 | N/A * | 0.875 | N/A * |
| 50m | 0.525 | N/A * | 0.374 | N/A * | 0.877 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

