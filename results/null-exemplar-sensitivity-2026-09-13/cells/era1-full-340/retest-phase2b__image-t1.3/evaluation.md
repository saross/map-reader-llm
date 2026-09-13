# Evaluation: retest-phase2b__image-t1.3

**Generated**: 2026-09-13T14:01:17.931947+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.085 | N/A * | 0.071 | N/A * | 0.107 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 10m | 0.250 | N/A * | 0.208 | N/A * | 0.315 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 15m | 0.382 | N/A * | 0.317 | N/A * | 0.480 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 20m | 0.482 | N/A * | 0.400 | N/A * | 0.607 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 25m | 0.547 | N/A * | 0.454 | N/A * | 0.689 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 30m | 0.592 | N/A * | 0.491 | N/A * | 0.746 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 35m | 0.616 | N/A * | 0.511 | N/A * | 0.775 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 40m | 0.639 | N/A * | 0.530 | N/A * | 0.805 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 45m | 0.654 | N/A * | 0.542 | N/A * | 0.823 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 50m | 0.666 | N/A * | 0.552 | N/A * | 0.838 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 75m | 0.694 | N/A * | 0.576 | N/A * | 0.874 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 100m | 0.700 | N/A * | 0.580 | N/A * | 0.881 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 125m | 0.705 | N/A * | 0.585 | N/A * | 0.888 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |
| 150m | 0.709 | N/A * | 0.589 | N/A * | 0.893 | N/A * | 0.191 | N/A * | 1.000 | 0.060 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (tile-level detail not retained in this aggregation). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

