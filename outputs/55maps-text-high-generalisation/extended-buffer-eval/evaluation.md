# Evaluation: 55maps-text-high-generalisation-extended-buffer

**Generated**: 2026-05-03T00:42:19.223945+00:00  
**Detections**: 4164  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 75m | 0.794 | N/A * | 0.850 | N/A * | 0.746 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 100m | 0.796 | N/A * | 0.851 | N/A * | 0.747 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |
| 125m | 0.797 | N/A * | 0.852 | N/A * | 0.748 | N/A * | 0.648 | N/A * | 0.644 | 0.953 |

\* Bootstrap CI suppressed for sparse-coverage buffers (66.3%, 66.3%, 66.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

