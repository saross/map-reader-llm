# Evaluation: P2c Image scale-4

**Generated**: 2026-08-21T13:38:55.412301+00:00  
**Detections**: 811  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.584 | N/A * | 0.486 | N/A * | 0.731 | N/A * |
| 30m | 0.637 | N/A * | 0.530 | N/A * | 0.798 | N/A * |
| 40m | 0.670 | N/A * | 0.557 | N/A * | 0.839 | N/A * |
| 50m | 0.690 | N/A * | 0.575 | N/A * | 0.865 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

