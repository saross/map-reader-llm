# Evaluation: P2c Image canonical

**Generated**: 2026-08-21T13:38:48.795998+00:00  
**Detections**: 720  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.581 | N/A * | 0.508 | N/A * | 0.679 | N/A * |
| 30m | 0.653 | N/A * | 0.571 | N/A * | 0.762 | N/A * |
| 40m | 0.680 | N/A * | 0.594 | N/A * | 0.794 | N/A * |
| 50m | 0.689 | N/A * | 0.603 | N/A * | 0.805 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

