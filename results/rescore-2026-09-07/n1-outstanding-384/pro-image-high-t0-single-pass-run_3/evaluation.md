# Evaluation: pro-image-high-t0-single-pass-run_3-rescore-2026-09-07

**Generated**: 2026-09-07T04:33:03.435723+00:00  
**Detections**: 741  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.099 | N/A * | 0.078 | N/A * | 0.133 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 10m | 0.309 | N/A * | 0.246 | N/A * | 0.418 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 15m | 0.451 | N/A * | 0.358 | N/A * | 0.609 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 20m | 0.546 | N/A * | 0.433 | N/A * | 0.738 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 25m | 0.587 | N/A * | 0.466 | N/A * | 0.793 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 30m | 0.621 | N/A * | 0.493 | N/A * | 0.839 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 35m | 0.643 | N/A * | 0.510 | N/A * | 0.869 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 40m | 0.658 | N/A * | 0.522 | N/A * | 0.890 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 45m | 0.665 | N/A * | 0.528 | N/A * | 0.899 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 50m | 0.665 | N/A * | 0.528 | N/A * | 0.899 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 75m | 0.673 | N/A * | 0.534 | N/A * | 0.910 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 100m | 0.675 | N/A * | 0.536 | N/A * | 0.913 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 125m | 0.679 | N/A * | 0.538 | N/A * | 0.917 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |
| 150m | 0.680 | N/A * | 0.540 | N/A * | 0.919 | N/A * | 0.643 | N/A * | 0.983 | 0.628 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 2/487 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

