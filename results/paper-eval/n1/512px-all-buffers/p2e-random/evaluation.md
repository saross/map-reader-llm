# Evaluation: P2e Random

**Generated**: 2026-08-21T13:39:14.809968+00:00  
**Detections**: 821  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.571 | N/A * | 0.473 | N/A * | 0.720 | N/A * |
| 30m | 0.644 | N/A * | 0.533 | N/A * | 0.813 | N/A * |
| 40m | 0.673 | N/A * | 0.558 | N/A * | 0.850 | N/A * |
| 50m | 0.697 | N/A * | 0.577 | N/A * | 0.879 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

