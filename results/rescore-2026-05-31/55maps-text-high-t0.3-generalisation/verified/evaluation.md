# Evaluation: verified_detections

**Generated**: 2026-06-02T01:22:54.037295+00:00  
**Detections**: 4350  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.089 | N/A * | 0.093 | N/A * | 0.085 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 10m | 0.284 | N/A * | 0.297 | N/A * | 0.272 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 15m | 0.475 | N/A * | 0.497 | N/A * | 0.455 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 20m | 0.631 | N/A * | 0.659 | N/A * | 0.605 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 25m | 0.719 | N/A * | 0.752 | N/A * | 0.689 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 30m | 0.764 | N/A * | 0.799 | N/A * | 0.732 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 35m | 0.787 | N/A * | 0.823 | N/A * | 0.754 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 40m | 0.796 | N/A * | 0.833 | N/A * | 0.763 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 45m | 0.803 | N/A * | 0.840 | N/A * | 0.769 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 50m | 0.805 | N/A * | 0.841 | N/A * | 0.771 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 75m | 0.808 | N/A * | 0.845 | N/A * | 0.774 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 100m | 0.809 | N/A * | 0.846 | N/A * | 0.775 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 125m | 0.810 | N/A * | 0.846 | N/A * | 0.776 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |
| 150m | 0.810 | N/A * | 0.847 | N/A * | 0.777 | N/A * | 0.654 | N/A * | 0.656 | 0.951 |

\* Bootstrap CI suppressed for sparse-coverage buffers (63.6%, 64.1%, 64.7%, 65.2%, 65.6%, 65.8%, 66.0%, 66.0%, 66.0%, 66.0%, 66.0%, 66.1%, 66.1%, 66.1% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

