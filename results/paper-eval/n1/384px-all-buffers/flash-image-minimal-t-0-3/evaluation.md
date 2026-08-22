# Evaluation: Flash Image MINIMAL T=0.3

**Generated**: 2026-08-21T13:33:16.935997+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.593 | N/A * | 0.469 | N/A * | 0.807 | N/A * |
| 30m | 0.653 | N/A * | 0.516 | N/A * | 0.888 | N/A * |
| 40m | 0.671 | N/A * | 0.530 | N/A * | 0.913 | N/A * |
| 50m | 0.677 | N/A * | 0.535 | N/A * | 0.921 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

