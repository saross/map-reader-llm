# Evaluation: P2a Verbose text+image

**Generated**: 2026-08-21T13:37:52.296201+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.517 | N/A * | 0.434 | N/A * | 0.639 | N/A * |
| 30m | 0.613 | N/A * | 0.515 | N/A * | 0.758 | N/A * |
| 40m | 0.658 | N/A * | 0.553 | N/A * | 0.813 | N/A * |
| 50m | 0.683 | N/A * | 0.573 | N/A * | 0.844 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

