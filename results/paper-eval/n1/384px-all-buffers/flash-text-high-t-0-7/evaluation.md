# Evaluation: Flash Text HIGH T=0.7

**Generated**: 2026-08-21T13:38:29.737156+00:00  
**Runs**: 30  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.387 | N/A * | 0.249 | N/A * | 0.869 | N/A * |
| 30m | 0.406 | N/A * | 0.261 | N/A * | 0.912 | N/A * |
| 40m | 0.413 | N/A * | 0.266 | N/A * | 0.928 | N/A * |
| 50m | 0.416 | N/A * | 0.268 | N/A * | 0.934 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

