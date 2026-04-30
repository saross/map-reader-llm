# Evaluation: pro-high-text-consensus-pool-t1

**Generated**: 2026-04-30T06:57:13.466395+00:00  
**Detections**: 566  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.733 | N/A * | 0.648 | N/A * | 0.844 | N/A * | 0.716 | N/A * | 0.812 | 0.899 |
| 30m | 0.747 | N/A * | 0.661 | N/A * | 0.860 | N/A * | 0.716 | N/A * | 0.812 | 0.899 |
| 40m | 0.751 | N/A * | 0.664 | N/A * | 0.864 | N/A * | 0.716 | N/A * | 0.812 | 0.899 |
| 50m | 0.751 | N/A * | 0.664 | N/A * | 0.864 | N/A * | 0.716 | N/A * | 0.812 | 0.899 |

\* Bootstrap CI suppressed for sparse-coverage buffers (53.6%, 53.6%, 53.6%, 53.6% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

