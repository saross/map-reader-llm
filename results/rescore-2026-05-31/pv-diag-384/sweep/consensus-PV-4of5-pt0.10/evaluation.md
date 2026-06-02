# Evaluation: materialised_vt4_pt0.10

**Generated**: 2026-06-02T01:20:46.113388+00:00  
**Detections**: 452  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.289 | [0.277, 0.297] | 0.283 | [0.272, 0.293] | 0.294 | [0.283, 0.304] | 0.687 | [0.671, 0.701] | 0.834 | 0.853 |
| 10m | 0.663 | [0.653, 0.673] | 0.650 | [0.640, 0.661] | 0.676 | [0.665, 0.686] | 0.687 | [0.671, 0.701] | 0.834 | 0.853 |
| 15m | 0.785 | [0.776, 0.793] | 0.770 | [0.760, 0.780] | 0.800 | [0.790, 0.811] | 0.687 | [0.671, 0.701] | 0.834 | 0.853 |
| 20m | 0.828 | N/A * | 0.812 | N/A * | 0.844 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |
| 25m | 0.841 | N/A * | 0.825 | N/A * | 0.858 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |
| 30m | 0.852 | N/A * | 0.836 | N/A * | 0.869 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |
| 35m | 0.852 | N/A * | 0.836 | N/A * | 0.869 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |
| 40m | 0.852 | N/A * | 0.836 | N/A * | 0.869 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |
| 45m | 0.852 | N/A * | 0.836 | N/A * | 0.869 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |
| 50m | 0.852 | N/A * | 0.836 | N/A * | 0.869 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |
| 75m | 0.855 | N/A * | 0.839 | N/A * | 0.871 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |
| 100m | 0.857 | N/A * | 0.841 | N/A * | 0.874 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |
| 125m | 0.857 | N/A * | 0.841 | N/A * | 0.874 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |
| 150m | 0.857 | N/A * | 0.841 | N/A * | 0.874 | N/A * | 0.687 | N/A * | 0.834 | 0.853 |

\* Bootstrap CI suppressed for sparse-coverage buffers (50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1%, 50.1% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

