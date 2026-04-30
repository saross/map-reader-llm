# Evaluation: 55maps-image-generalisation

**Generated**: 2026-04-30T06:54:17.762055+00:00  
**Detections**: 4665  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 50m | 0.773 | N/A * | 0.779 | N/A * | 0.766 | N/A * | 0.692 | N/A * | 0.707 | 0.948 |
| 75m | 0.790 | N/A * | 0.796 | N/A * | 0.783 | N/A * | 0.692 | N/A * | 0.707 | 0.948 |
| 100m | 0.795 | N/A * | 0.801 | N/A * | 0.788 | N/A * | 0.692 | N/A * | 0.707 | 0.948 |
| 125m | 0.797 | N/A * | 0.804 | N/A * | 0.790 | N/A * | 0.692 | N/A * | 0.707 | 0.948 |
| 150m | 0.799 | N/A * | 0.805 | N/A * | 0.792 | N/A * | 0.692 | N/A * | 0.707 | 0.948 |

\* Bootstrap CI suppressed for sparse-coverage buffers (65.1%, 65.2%, 65.2%, 65.2%, 65.2% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

