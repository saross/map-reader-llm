# Evaluation: HIGH-t1.0-4of5

**Generated**: 2026-04-30T06:58:14.199024+00:00  
**Detections**: 357  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.697 | N/A * | 0.773 | N/A * | 0.634 | N/A * | 0.656 | N/A * | 0.755 | 0.891 |
| 30m | 0.752 | N/A * | 0.835 | N/A * | 0.685 | N/A * | 0.656 | N/A * | 0.755 | 0.891 |
| 40m | 0.760 | N/A * | 0.843 | N/A * | 0.692 | N/A * | 0.656 | N/A * | 0.755 | 0.891 |
| 50m | 0.770 | N/A * | 0.854 | N/A * | 0.701 | N/A * | 0.656 | N/A * | 0.755 | 0.891 |

\* Bootstrap CI suppressed for sparse-coverage buffers (53.4%, 53.4%, 53.4%, 53.4% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

