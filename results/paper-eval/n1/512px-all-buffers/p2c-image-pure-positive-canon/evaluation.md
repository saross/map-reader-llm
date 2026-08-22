# Evaluation: P2c Image pure-positive-canon

**Generated**: 2026-08-21T13:38:53.571863+00:00  
**Detections**: 736  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.568 | N/A * | 0.492 | N/A * | 0.672 | N/A * |
| 30m | 0.646 | N/A * | 0.560 | N/A * | 0.764 | N/A * |
| 40m | 0.676 | N/A * | 0.586 | N/A * | 0.800 | N/A * |
| 50m | 0.695 | N/A * | 0.602 | N/A * | 0.822 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

