# Evaluation: scale-32-greedy-t3

**Generated**: 2026-04-30T06:53:17.462140+00:00  
**Detections**: 334  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.585 | N/A * | 0.674 | N/A * | 0.517 | N/A * |
| 30m | 0.637 | N/A * | 0.734 | N/A * | 0.563 | N/A * |
| 40m | 0.661 | N/A * | 0.760 | N/A * | 0.584 | N/A * |
| 50m | 0.671 | N/A * | 0.772 | N/A * | 0.593 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (52.4%, 52.4%, 52.4%, 52.6% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

