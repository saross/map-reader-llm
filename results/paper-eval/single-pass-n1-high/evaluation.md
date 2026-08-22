# Evaluation: Single-pass brief-text T=0.7 HIGH (N=1 mean of 30)

**Generated**: 2026-08-21T13:46:49.994683+00:00  
**Runs**: 30  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.387 | N/A * | 0.249 | N/A * | 0.869 | N/A * |
| 30m | 0.406 | N/A * | 0.261 | N/A * | 0.912 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

