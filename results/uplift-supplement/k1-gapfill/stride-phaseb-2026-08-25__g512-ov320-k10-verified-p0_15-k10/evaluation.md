# Evaluation: stride-phaseb-2026-08-25__g512-ov320-k10-verified-p0_15-k10-n1

**Generated**: 2026-08-29T07:41:22.193811+00:00  
**Detections**: 3926  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.187 | N/A * | 0.104 | N/A * | 0.953 | N/A * | -0.082 | N/A * | 0.058 | 0.897 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 447/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

