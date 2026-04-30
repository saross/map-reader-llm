# Evaluation: pro-high-text-consensus-pool-t10

**Generated**: 2026-04-30T06:57:12.693110+00:00  
**Detections**: 295  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.794 | N/A * | 0.983 | N/A * | 0.667 | N/A * | 0.710 | N/A * | 0.664 | 0.996 |
| 30m | 0.800 | N/A * | 0.990 | N/A * | 0.671 | N/A * | 0.710 | N/A * | 0.664 | 0.996 |
| 40m | 0.803 | N/A * | 0.993 | N/A * | 0.674 | N/A * | 0.710 | N/A * | 0.664 | 0.996 |
| 50m | 0.803 | N/A * | 0.993 | N/A * | 0.674 | N/A * | 0.710 | N/A * | 0.664 | 0.996 |

\* Bootstrap CI suppressed for sparse-coverage buffers (59.3%, 59.3%, 59.3%, 59.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

