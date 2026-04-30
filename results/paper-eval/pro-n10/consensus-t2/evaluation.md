# Evaluation: pro-high-text-consensus-pool-t2

**Generated**: 2026-04-30T06:57:17.163257+00:00  
**Detections**: 469  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.799 | N/A * | 0.770 | N/A * | 0.830 | N/A * | 0.734 | N/A * | 0.803 | 0.922 |
| 30m | 0.816 | N/A * | 0.787 | N/A * | 0.848 | N/A * | 0.734 | N/A * | 0.803 | 0.922 |
| 40m | 0.823 | N/A * | 0.793 | N/A * | 0.855 | N/A * | 0.734 | N/A * | 0.803 | 0.922 |
| 50m | 0.823 | N/A * | 0.793 | N/A * | 0.855 | N/A * | 0.734 | N/A * | 0.803 | 0.922 |

\* Bootstrap CI suppressed for sparse-coverage buffers (54.8%, 55.0%, 55.0%, 55.0% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

