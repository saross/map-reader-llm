# Evaluation: 55maps-gen-verified-paired

**Generated**: 2026-05-30T02:38:43.338295+00:00  
**Detections**: 4068  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.625 | N/A * | 0.677 | N/A * | 0.581 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 30m | 0.757 | N/A * | 0.821 | N/A * | 0.703 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 40m | 0.786 | N/A * | 0.851 | N/A * | 0.730 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |
| 50m | 0.792 | N/A * | 0.858 | N/A * | 0.736 | N/A * | 0.651 | N/A * | 0.637 | 0.959 |

\* Bootstrap CI suppressed for sparse-coverage buffers (65.9%, 66.5%, 66.6%, 66.6% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

