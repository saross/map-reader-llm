# Evaluation: P2b Image T=0.3

**Generated**: 2026-08-21T13:38:20.128516+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.575 | N/A * | 0.488 | N/A * | 0.699 | N/A * |
| 30m | 0.651 | N/A * | 0.553 | N/A * | 0.792 | N/A * |
| 40m | 0.685 | N/A * | 0.581 | N/A * | 0.833 | N/A * |
| 50m | 0.704 | N/A * | 0.598 | N/A * | 0.857 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

