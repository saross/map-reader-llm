# Evaluation: 512px-image-t07

**Generated**: 2026-08-20T13:12:39.943499+00:00  
**Detections**: 783  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.471 | N/A * | 0.366 | N/A * | 0.660 | N/A * |
| 30m | 0.570 | N/A * | 0.443 | N/A * | 0.798 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 447/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

