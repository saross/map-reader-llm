# Evaluation: 512px-image-t0

**Generated**: 2026-08-20T13:12:38.253459+00:00  
**Detections**: 777  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.513 | N/A * | 0.400 | N/A * | 0.715 | N/A * |
| 30m | 0.571 | N/A * | 0.445 | N/A * | 0.795 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 447/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

