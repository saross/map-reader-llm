# Evaluation: stride-phaseb-2026-08-25__g384-ov128-ladder-n3-verified-p0_15-k3-n1

**Generated**: 2026-08-29T07:41:26.893732+00:00  
**Detections**: 1893  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.340 | N/A * | 0.208 | N/A * | 0.921 | N/A * | 0.007 | N/A * | 0.009 | 0.992 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 483/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

