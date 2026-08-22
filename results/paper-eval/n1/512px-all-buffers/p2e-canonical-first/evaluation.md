# Evaluation: P2e Canonical first

**Generated**: 2026-08-21T13:39:12.017789+00:00  
**Detections**: 771  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.599 | N/A * | 0.508 | N/A * | 0.727 | N/A * |
| 30m | 0.664 | N/A * | 0.564 | N/A * | 0.807 | N/A * |
| 40m | 0.715 | N/A * | 0.607 | N/A * | 0.868 | N/A * |
| 50m | 0.730 | N/A * | 0.620 | N/A * | 0.887 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 2/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

