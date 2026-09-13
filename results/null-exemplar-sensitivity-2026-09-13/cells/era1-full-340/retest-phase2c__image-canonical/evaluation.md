# Evaluation: retest-phase2c__image-canonical

**Generated**: 2026-09-13T14:01:34.390146+00:00  
**Detections**: 658  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.113 | N/A * | 0.099 | N/A * | 0.132 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 10m | 0.325 | N/A * | 0.284 | N/A * | 0.379 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 15m | 0.504 | N/A * | 0.441 | N/A * | 0.588 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 20m | 0.570 | N/A * | 0.498 | N/A * | 0.665 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 25m | 0.612 | N/A * | 0.535 | N/A * | 0.714 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 30m | 0.643 | N/A * | 0.562 | N/A * | 0.750 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 35m | 0.655 | N/A * | 0.573 | N/A * | 0.765 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 40m | 0.671 | N/A * | 0.587 | N/A * | 0.783 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 45m | 0.679 | N/A * | 0.594 | N/A * | 0.793 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 50m | 0.681 | N/A * | 0.596 | N/A * | 0.795 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 75m | 0.700 | N/A * | 0.613 | N/A * | 0.817 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 100m | 0.702 | N/A * | 0.614 | N/A * | 0.820 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 125m | 0.706 | N/A * | 0.617 | N/A * | 0.824 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |
| 150m | 0.707 | N/A * | 0.619 | N/A * | 0.826 | N/A * | 0.101 | N/A * | 1.000 | 0.016 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/315 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

