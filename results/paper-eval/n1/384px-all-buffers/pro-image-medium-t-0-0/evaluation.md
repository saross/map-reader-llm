# Evaluation: Pro Image MEDIUM T=0.0

**Generated**: 2026-08-21T13:35:42.983916+00:00  
**Detections**: 519  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.606 | N/A * | 0.557 | N/A * | 0.664 | N/A * |
| 30m | 0.734 | N/A * | 0.674 | N/A * | 0.805 | N/A * |
| 40m | 0.763 | N/A * | 0.701 | N/A * | 0.837 | N/A * |
| 50m | 0.778 | N/A * | 0.715 | N/A * | 0.853 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 26/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

