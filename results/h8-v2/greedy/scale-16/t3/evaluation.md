# Evaluation: scale-16-greedy-t3

**Generated**: 2026-04-30T06:53:14.214231+00:00  
**Detections**: 333  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.602 | N/A * | 0.694 | N/A * | 0.531 | N/A * |
| 30m | 0.646 | N/A * | 0.745 | N/A * | 0.570 | N/A * |
| 40m | 0.672 | N/A * | 0.775 | N/A * | 0.593 | N/A * |
| 50m | 0.682 | N/A * | 0.787 | N/A * | 0.602 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (54.0%, 54.0%, 54.0%, 54.2% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

