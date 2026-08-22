# Evaluation: 512px-text-t07

**Generated**: 2026-08-20T13:12:40.690488+00:00  
**Detections**: 924  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.525 | N/A * | 0.386 | N/A * | 0.821 | N/A * |
| 30m | 0.542 | N/A * | 0.398 | N/A * | 0.846 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 447/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

