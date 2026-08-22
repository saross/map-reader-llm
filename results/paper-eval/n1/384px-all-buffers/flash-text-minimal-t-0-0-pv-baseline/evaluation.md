# Evaluation: Flash Text MINIMAL T=0.0 (PV baseline)

**Generated**: 2026-08-21T13:33:46.976648+00:00  
**Detections**: 1047  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.520 | N/A * | 0.368 | N/A * | 0.885 | N/A * |
| 30m | 0.530 | N/A * | 0.375 | N/A * | 0.903 | N/A * |
| 40m | 0.536 | N/A * | 0.379 | N/A * | 0.913 | N/A * |
| 50m | 0.536 | N/A * | 0.379 | N/A * | 0.913 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

