# Evaluation: verified_detections

**Generated**: 2026-05-31T13:12:50.775787+00:00  
**Detections**: 4680  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.056 | N/A * | 0.056 | N/A * | 0.055 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 10m | 0.196 | N/A * | 0.197 | N/A * | 0.195 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 15m | 0.359 | N/A * | 0.361 | N/A * | 0.356 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 20m | 0.508 | N/A * | 0.512 | N/A * | 0.505 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 25m | 0.621 | N/A * | 0.625 | N/A * | 0.617 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 30m | 0.689 | N/A * | 0.694 | N/A * | 0.684 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 35m | 0.728 | N/A * | 0.733 | N/A * | 0.723 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 40m | 0.752 | N/A * | 0.757 | N/A * | 0.747 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 45m | 0.766 | N/A * | 0.772 | N/A * | 0.761 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 50m | 0.775 | N/A * | 0.780 | N/A * | 0.769 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 75m | 0.791 | N/A * | 0.797 | N/A * | 0.786 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 100m | 0.796 | N/A * | 0.802 | N/A * | 0.791 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 125m | 0.799 | N/A * | 0.804 | N/A * | 0.793 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |
| 150m | 0.800 | N/A * | 0.806 | N/A * | 0.794 | N/A * | 0.693 | N/A * | 0.708 | 0.948 |

\* Bootstrap CI suppressed for sparse-coverage buffers (62.8%, 63.2%, 63.7%, 64.1%, 64.5%, 64.9%, 65.0%, 65.1%, 65.1%, 65.2%, 65.2%, 65.3%, 65.3%, 65.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

