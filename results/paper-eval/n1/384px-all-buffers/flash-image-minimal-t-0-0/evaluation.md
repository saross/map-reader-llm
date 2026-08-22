# Evaluation: Flash Image MINIMAL T=0.0

**Generated**: 2026-08-21T13:33:00.398641+00:00  
**Detections**: 746  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.600 | N/A * | 0.474 | N/A * | 0.814 | N/A * |
| 30m | 0.655 | N/A * | 0.519 | N/A * | 0.890 | N/A * |
| 40m | 0.674 | N/A * | 0.533 | N/A * | 0.915 | N/A * |
| 50m | 0.681 | N/A * | 0.539 | N/A * | 0.924 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 4/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

