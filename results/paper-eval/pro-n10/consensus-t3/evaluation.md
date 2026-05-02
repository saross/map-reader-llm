# Evaluation: pro-high-text-consensus-pool-t3

**Generated**: 2026-04-30T06:57:15.388242+00:00  
**Detections**: 425  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.823 | N/A * | 0.833 | N/A * | 0.814 | N/A * | 0.745 | N/A * | 0.790 | 0.942 |
| 30m | 0.840 | N/A * | 0.849 | N/A * | 0.830 | N/A * | 0.745 | N/A * | 0.790 | 0.942 |
| 40m | 0.842 | N/A * | 0.852 | N/A * | 0.832 | N/A * | 0.745 | N/A * | 0.790 | 0.942 |
| 50m | 0.842 | N/A * | 0.852 | N/A * | 0.832 | N/A * | 0.745 | N/A * | 0.790 | 0.942 |

\* Bootstrap CI suppressed for sparse-coverage buffers (55.6%, 55.9%, 55.9%, 55.9% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

