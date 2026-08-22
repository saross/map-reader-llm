# Evaluation: P2c Text scale-4

**Generated**: 2026-08-21T13:39:03.882663+00:00  
**Detections**: 882  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.609 | N/A * | 0.491 | N/A * | 0.803 | N/A * |
| 30m | 0.640 | N/A * | 0.516 | N/A * | 0.844 | N/A * |
| 40m | 0.649 | N/A * | 0.523 | N/A * | 0.855 | N/A * |
| 50m | 0.654 | N/A * | 0.527 | N/A * | 0.863 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

