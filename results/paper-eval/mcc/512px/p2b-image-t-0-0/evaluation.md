# Evaluation: P2b Image T=0.0

**Generated**: 2026-08-20T13:13:44.876372+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 30m | 0.654 | N/A * | 0.555 | N/A * | 0.795 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

