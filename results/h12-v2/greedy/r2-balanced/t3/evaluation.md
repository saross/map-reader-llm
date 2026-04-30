# Evaluation: r2-balanced-greedy-t3

**Generated**: 2026-04-30T06:52:37.826907+00:00  
**Detections**: 313  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.588 | N/A * | 0.703 | N/A * | 0.506 | N/A * |
| 30m | 0.644 | N/A * | 0.770 | N/A * | 0.554 | N/A * |
| 40m | 0.682 | N/A * | 0.815 | N/A * | 0.586 | N/A * |
| 50m | 0.687 | N/A * | 0.821 | N/A * | 0.591 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (54.0%, 54.2%, 54.2%, 54.2% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

