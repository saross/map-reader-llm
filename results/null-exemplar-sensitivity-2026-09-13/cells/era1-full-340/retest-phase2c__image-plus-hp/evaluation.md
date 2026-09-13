# Evaluation: retest-phase2c__image-plus-hp

**Generated**: 2026-09-13T14:01:39.952891+00:00  
**Detections**: 708  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.132 | N/A * | 0.112 | N/A * | 0.160 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 10m | 0.373 | N/A * | 0.316 | N/A * | 0.454 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 15m | 0.523 | N/A * | 0.444 | N/A * | 0.637 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 20m | 0.593 | N/A * | 0.503 | N/A * | 0.722 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 25m | 0.625 | N/A * | 0.530 | N/A * | 0.761 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 30m | 0.658 | N/A * | 0.558 | N/A * | 0.801 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 35m | 0.681 | N/A * | 0.578 | N/A * | 0.830 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 40m | 0.709 | N/A * | 0.602 | N/A * | 0.864 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 45m | 0.718 | N/A * | 0.609 | N/A * | 0.874 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 50m | 0.724 | N/A * | 0.614 | N/A * | 0.882 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 75m | 0.734 | N/A * | 0.623 | N/A * | 0.894 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 100m | 0.734 | N/A * | 0.623 | N/A * | 0.894 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 125m | 0.739 | N/A * | 0.627 | N/A * | 0.901 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |
| 150m | 0.743 | N/A * | 0.630 | N/A * | 0.905 | N/A * | 0.071 | N/A * | 1.000 | 0.008 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/315 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

