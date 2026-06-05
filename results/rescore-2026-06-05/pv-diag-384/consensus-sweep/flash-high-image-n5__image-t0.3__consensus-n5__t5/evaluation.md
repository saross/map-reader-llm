# Evaluation: consensus_t5

**Generated**: 2026-06-05T06:52:20.787855+00:00  
**Detections**: 346  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.195 | N/A * | 0.220 | N/A * | 0.175 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 10m | 0.461 | N/A * | 0.520 | N/A * | 0.414 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 15m | 0.622 | N/A * | 0.702 | N/A * | 0.559 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 20m | 0.712 | N/A * | 0.803 | N/A * | 0.639 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 25m | 0.755 | N/A * | 0.853 | N/A * | 0.678 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 30m | 0.763 | N/A * | 0.861 | N/A * | 0.685 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 35m | 0.768 | N/A * | 0.867 | N/A * | 0.690 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 40m | 0.771 | N/A * | 0.870 | N/A * | 0.692 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 45m | 0.773 | N/A * | 0.873 | N/A * | 0.694 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 50m | 0.776 | N/A * | 0.876 | N/A * | 0.697 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 75m | 0.778 | N/A * | 0.879 | N/A * | 0.699 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 100m | 0.778 | N/A * | 0.879 | N/A * | 0.699 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 125m | 0.778 | N/A * | 0.879 | N/A * | 0.699 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |
| 150m | 0.781 | N/A * | 0.881 | N/A * | 0.701 | N/A * | 0.680 | N/A * | 0.742 | 0.922 |

\* Bootstrap CI suppressed for sparse-coverage buffers (53.6%, 54.4%, 54.8%, 54.8%, 55.0%, 55.0%, 55.0%, 55.0%, 55.0%, 55.0%, 55.0%, 55.0%, 55.0%, 55.0% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

