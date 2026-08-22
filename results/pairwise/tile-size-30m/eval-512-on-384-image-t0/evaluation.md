# Evaluation: 512px Image T=0.0 (on 384px grid)

**Generated**: 2026-08-20T13:12:48.682270+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.514 | N/A * | 0.402 | N/A * | 0.713 | N/A * |
| 30m | 0.574 | N/A * | 0.449 | N/A * | 0.797 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

