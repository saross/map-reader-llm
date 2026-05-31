# Evaluation: verified_detections

**Generated**: 2026-05-31T13:12:22.642796+00:00  
**Detections**: 4164  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.086 | N/A * | 0.091 | N/A * | 0.080 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 10m | 0.275 | N/A * | 0.295 | N/A * | 0.259 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 15m | 0.479 | N/A * | 0.512 | N/A * | 0.449 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 20m | 0.626 | N/A * | 0.670 | N/A * | 0.588 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 25m | 0.710 | N/A * | 0.760 | N/A * | 0.667 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 30m | 0.757 | N/A * | 0.810 | N/A * | 0.711 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 35m | 0.778 | N/A * | 0.832 | N/A * | 0.730 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 40m | 0.787 | N/A * | 0.842 | N/A * | 0.739 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 45m | 0.790 | N/A * | 0.846 | N/A * | 0.742 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 50m | 0.792 | N/A * | 0.848 | N/A * | 0.744 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 75m | 0.794 | N/A * | 0.850 | N/A * | 0.746 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 100m | 0.796 | N/A * | 0.851 | N/A * | 0.747 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 125m | 0.797 | N/A * | 0.853 | N/A * | 0.748 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 150m | 0.798 | N/A * | 0.854 | N/A * | 0.749 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |

\* Bootstrap CI suppressed for sparse-coverage buffers (63.8%, 64.3%, 65.1%, 65.6%, 66.0%, 66.2%, 66.3%, 66.3%, 66.3%, 66.3%, 66.3%, 66.3%, 66.3%, 66.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

