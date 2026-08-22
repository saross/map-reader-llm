# Evaluation: Flash Image MINIMAL T=0.7

**Generated**: 2026-08-21T13:34:15.743949+00:00  
**Runs**: 10  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.553 | N/A * | 0.435 | N/A * | 0.759 | N/A * |
| 30m | 0.630 | N/A * | 0.496 | N/A * | 0.864 | N/A * |
| 40m | 0.657 | N/A * | 0.517 | N/A * | 0.901 | N/A * |
| 50m | 0.666 | N/A * | 0.524 | N/A * | 0.913 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

