# Evaluation: P2d Image terse

**Generated**: 2026-08-21T13:39:05.269928+00:00  
**Detections**: 773  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.605 | N/A * | 0.514 | N/A * | 0.737 | N/A * |
| 30m | 0.649 | N/A * | 0.551 | N/A * | 0.790 | N/A * |
| 40m | 0.695 | N/A * | 0.590 | N/A * | 0.846 | N/A * |
| 50m | 0.717 | N/A * | 0.608 | N/A * | 0.872 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

