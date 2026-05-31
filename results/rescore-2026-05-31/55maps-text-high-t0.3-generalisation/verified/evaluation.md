# Evaluation: verified_detections

**Generated**: 2026-05-31T13:12:31.769351+00:00  
**Detections**: 4350  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.087 | N/A * | 0.091 | N/A * | 0.083 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 10m | 0.283 | N/A * | 0.296 | N/A * | 0.270 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 15m | 0.474 | N/A * | 0.497 | N/A * | 0.453 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 20m | 0.629 | N/A * | 0.659 | N/A * | 0.601 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 25m | 0.717 | N/A * | 0.751 | N/A * | 0.685 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 30m | 0.762 | N/A * | 0.799 | N/A * | 0.729 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 35m | 0.785 | N/A * | 0.823 | N/A * | 0.750 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 40m | 0.794 | N/A * | 0.832 | N/A * | 0.759 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 45m | 0.801 | N/A * | 0.839 | N/A * | 0.765 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 50m | 0.802 | N/A * | 0.841 | N/A * | 0.767 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 75m | 0.805 | N/A * | 0.844 | N/A * | 0.770 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 100m | 0.806 | N/A * | 0.845 | N/A * | 0.771 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 125m | 0.807 | N/A * | 0.846 | N/A * | 0.772 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |
| 150m | 0.808 | N/A * | 0.847 | N/A * | 0.773 | N/A * | 0.654 | N/A * | 0.655 | 0.951 |

\* Bootstrap CI suppressed for sparse-coverage buffers (63.5%, 64.1%, 64.7%, 65.2%, 65.6%, 65.8%, 65.9%, 66.0%, 66.0%, 66.0%, 66.0%, 66.0%, 66.0%, 66.0% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

