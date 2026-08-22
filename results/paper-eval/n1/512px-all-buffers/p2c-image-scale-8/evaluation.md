# Evaluation: P2c Image scale-8

**Generated**: 2026-08-21T13:38:57.821563+00:00  
**Detections**: 770  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.587 | N/A * | 0.499 | N/A * | 0.712 | N/A * |
| 30m | 0.655 | N/A * | 0.557 | N/A * | 0.796 | N/A * |
| 40m | 0.688 | N/A * | 0.584 | N/A * | 0.835 | N/A * |
| 50m | 0.704 | N/A * | 0.599 | N/A * | 0.855 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

