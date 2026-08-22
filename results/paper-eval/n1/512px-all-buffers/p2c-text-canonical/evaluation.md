# Evaluation: P2c Text canonical

**Generated**: 2026-08-21T13:38:59.168150+00:00  
**Detections**: 897  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.605 | N/A * | 0.484 | N/A * | 0.805 | N/A * |
| 30m | 0.636 | N/A * | 0.509 | N/A * | 0.848 | N/A * |
| 40m | 0.646 | N/A * | 0.517 | N/A * | 0.861 | N/A * |
| 50m | 0.650 | N/A * | 0.521 | N/A * | 0.866 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

