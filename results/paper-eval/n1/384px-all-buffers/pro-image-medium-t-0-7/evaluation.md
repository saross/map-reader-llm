# Evaluation: Pro Image MEDIUM T=0.7

**Generated**: 2026-08-21T13:35:52.639840+00:00  
**Detections**: 941  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.452 | N/A * | 0.331 | N/A * | 0.715 | N/A * |
| 30m | 0.538 | N/A * | 0.393 | N/A * | 0.851 | N/A * |
| 40m | 0.567 | N/A * | 0.414 | N/A * | 0.897 | N/A * |
| 50m | 0.586 | N/A * | 0.428 | N/A * | 0.926 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

