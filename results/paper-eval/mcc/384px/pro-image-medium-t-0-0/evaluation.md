# Evaluation: Pro Image MEDIUM T=0.0

**Generated**: 2026-08-20T13:13:04.323097+00:00  
**Detections**: 519  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 30m | 0.734 | N/A * | 0.674 | N/A * | 0.805 | N/A * | 0.734 | N/A * | 0.882 | 0.853 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 26/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

