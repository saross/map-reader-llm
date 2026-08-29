# Evaluation: stride-phasec-2026-08-25__g384-ov240-k10-verified-p0_15-k10-n1

**Generated**: 2026-08-29T07:41:41.080177+00:00  
**Detections**: 5698  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.136 | N/A * | 0.073 | N/A * | 0.970 | N/A * | 0.060 | N/A * | 0.156 | 0.885 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 422/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

