# Evaluation: verified_detections_paired

**Generated**: 2026-05-31T13:12:31.462077+00:00  
**Detections**: 4068  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.080 | N/A * | 0.086 | N/A * | 0.074 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 10m | 0.266 | N/A * | 0.288 | N/A * | 0.247 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 15m | 0.472 | N/A * | 0.512 | N/A * | 0.439 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 20m | 0.625 | N/A * | 0.677 | N/A * | 0.581 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 25m | 0.710 | N/A * | 0.769 | N/A * | 0.659 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 30m | 0.757 | N/A * | 0.821 | N/A * | 0.703 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 35m | 0.777 | N/A * | 0.842 | N/A * | 0.722 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 40m | 0.786 | N/A * | 0.851 | N/A * | 0.730 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 45m | 0.790 | N/A * | 0.856 | N/A * | 0.734 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 50m | 0.792 | N/A * | 0.858 | N/A * | 0.736 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 75m | 0.795 | N/A * | 0.861 | N/A * | 0.738 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 100m | 0.796 | N/A * | 0.863 | N/A * | 0.740 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 125m | 0.797 | N/A * | 0.864 | N/A * | 0.740 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 150m | 0.798 | N/A * | 0.864 | N/A * | 0.741 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |

\* Bootstrap CI suppressed for sparse-coverage buffers (64.1%, 64.8%, 65.3%, 65.9%, 66.2%, 66.5%, 66.5%, 66.6%, 66.6%, 66.6%, 66.7%, 66.7%, 66.7%, 66.7% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

