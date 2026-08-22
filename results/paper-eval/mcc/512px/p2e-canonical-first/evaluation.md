# Evaluation: P2e Canonical first

**Generated**: 2026-08-21T13:28:19.027813+00:00  
**Detections**: 771  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 30m | 0.664 | N/A * | 0.564 | N/A * | 0.807 | N/A * | 0.094 | N/A * | 1.000 | 0.015 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 2/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

