# Evaluation: P2a Image only

**Generated**: 2026-08-21T13:37:48.701419+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.470 | N/A * | 0.383 | N/A * | 0.607 | N/A * |
| 30m | 0.574 | N/A * | 0.468 | N/A * | 0.742 | N/A * |
| 40m | 0.620 | N/A * | 0.506 | N/A * | 0.801 | N/A * |
| 50m | 0.649 | N/A * | 0.529 | N/A * | 0.839 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

