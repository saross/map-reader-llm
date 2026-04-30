# Evaluation: pro-high-text-consensus-pool-t9

**Generated**: 2026-04-30T06:57:19.939949+00:00  
**Detections**: 313  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.810 | N/A * | 0.968 | N/A * | 0.697 | N/A * | 0.718 | N/A * | 0.681 | 0.992 |
| 30m | 0.816 | N/A * | 0.974 | N/A * | 0.701 | N/A * | 0.718 | N/A * | 0.681 | 0.992 |
| 40m | 0.818 | N/A * | 0.978 | N/A * | 0.703 | N/A * | 0.718 | N/A * | 0.681 | 0.992 |
| 50m | 0.818 | N/A * | 0.978 | N/A * | 0.703 | N/A * | 0.718 | N/A * | 0.681 | 0.992 |

\* Bootstrap CI suppressed for sparse-coverage buffers (59.3%, 59.3%, 59.3%, 59.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

