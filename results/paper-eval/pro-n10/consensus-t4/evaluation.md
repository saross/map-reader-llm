# Evaluation: pro-high-text-consensus-pool-t4

**Generated**: 2026-04-30T06:57:14.273843+00:00  
**Detections**: 393  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.833 | N/A * | 0.878 | N/A * | 0.793 | N/A * | 0.735 | N/A * | 0.768 | 0.950 |
| 30m | 0.848 | N/A * | 0.893 | N/A * | 0.807 | N/A * | 0.735 | N/A * | 0.768 | 0.950 |
| 40m | 0.850 | N/A * | 0.896 | N/A * | 0.809 | N/A * | 0.735 | N/A * | 0.768 | 0.950 |
| 50m | 0.850 | N/A * | 0.896 | N/A * | 0.809 | N/A * | 0.735 | N/A * | 0.768 | 0.950 |

\* Bootstrap CI suppressed for sparse-coverage buffers (56.7%, 56.7%, 56.7%, 56.7% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

