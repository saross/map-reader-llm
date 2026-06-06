# Evaluation: filtered

**Generated**: 2026-06-06T01:43:20.969696+00:00  
**Detections**: 3601  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.085 | N/A * | 0.099 | N/A * | 0.075 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 10m | 0.266 | N/A * | 0.309 | N/A * | 0.234 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 15m | 0.449 | N/A * | 0.520 | N/A * | 0.394 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 20m | 0.594 | N/A * | 0.689 | N/A * | 0.522 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 25m | 0.676 | N/A * | 0.784 | N/A * | 0.595 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 30m | 0.718 | N/A * | 0.832 | N/A * | 0.631 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 35m | 0.738 | N/A * | 0.855 | N/A * | 0.649 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 40m | 0.745 | N/A * | 0.863 | N/A * | 0.655 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 45m | 0.751 | N/A * | 0.870 | N/A * | 0.660 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 50m | 0.752 | N/A * | 0.871 | N/A * | 0.661 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 75m | 0.753 | N/A * | 0.873 | N/A * | 0.662 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 100m | 0.754 | N/A * | 0.873 | N/A * | 0.663 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 125m | 0.754 | N/A * | 0.874 | N/A * | 0.663 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |
| 150m | 0.754 | N/A * | 0.875 | N/A * | 0.663 | N/A * | 0.616 | N/A * | 0.580 | 0.966 |

\* Bootstrap CI suppressed for sparse-coverage buffers (64.9%, 65.4%, 66.0%, 66.6%, 66.9%, 67.1%, 67.2%, 67.2%, 67.3%, 67.3%, 67.3%, 67.3%, 67.3%, 67.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

