# Evaluation: pro-image-high-t0-single-pass-run_1-rescore-2026-09-07

**Generated**: 2026-09-07T04:31:15.537439+00:00  
**Detections**: 750  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.096 | N/A * | 0.076 | N/A * | 0.131 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 10m | 0.304 | N/A * | 0.240 | N/A * | 0.414 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 15m | 0.447 | N/A * | 0.353 | N/A * | 0.609 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 20m | 0.540 | N/A * | 0.427 | N/A * | 0.736 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 25m | 0.577 | N/A * | 0.456 | N/A * | 0.786 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 30m | 0.616 | N/A * | 0.487 | N/A * | 0.839 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 35m | 0.643 | N/A * | 0.508 | N/A * | 0.876 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 40m | 0.656 | N/A * | 0.519 | N/A * | 0.894 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 45m | 0.665 | N/A * | 0.525 | N/A * | 0.906 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 50m | 0.665 | N/A * | 0.525 | N/A * | 0.906 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 75m | 0.672 | N/A * | 0.531 | N/A * | 0.915 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 100m | 0.673 | N/A * | 0.532 | N/A * | 0.917 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 125m | 0.677 | N/A * | 0.535 | N/A * | 0.922 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |
| 150m | 0.678 | N/A * | 0.536 | N/A * | 0.924 | N/A * | 0.651 | N/A * | 0.991 | 0.624 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

