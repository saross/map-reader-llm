# Evaluation: Pro Text MEDIUM T=0.0

**Generated**: 2026-08-21T13:36:52.834475+00:00  
**Detections**: 430  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.763 | N/A * | 0.767 | N/A * | 0.759 | N/A * |
| 30m | 0.784 | N/A * | 0.788 | N/A * | 0.779 | N/A * |
| 40m | 0.795 | N/A * | 0.800 | N/A * | 0.791 | N/A * |
| 50m | 0.802 | N/A * | 0.807 | N/A * | 0.798 | N/A * |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 26/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

