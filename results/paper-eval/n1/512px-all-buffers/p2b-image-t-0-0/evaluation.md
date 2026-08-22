# Evaluation: P2b Image T=0.0

**Generated**: 2026-08-21T13:38:16.388119+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.586 | N/A * | 0.498 | N/A * | 0.713 | N/A * |
| 30m | 0.654 | N/A * | 0.555 | N/A * | 0.795 | N/A * |
| 40m | 0.686 | N/A * | 0.582 | N/A * | 0.834 | N/A * |
| 50m | 0.703 | N/A * | 0.597 | N/A * | 0.855 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

