# Evaluation: P2b Text T=0.0

**Generated**: 2026-08-21T13:38:44.096523+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.606 | N/A * | 0.487 | N/A * | 0.800 | N/A * |
| 30m | 0.643 | N/A * | 0.518 | N/A * | 0.850 | N/A * |
| 40m | 0.651 | N/A * | 0.524 | N/A * | 0.860 | N/A * |
| 50m | 0.656 | N/A * | 0.528 | N/A * | 0.866 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

