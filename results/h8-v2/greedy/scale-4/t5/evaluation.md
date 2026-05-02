# Evaluation: scale-4-greedy-t5

**Generated**: 2026-04-30T06:53:23.499832+00:00  
**Detections**: 175  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.508 | N/A * | 0.886 | N/A * | 0.356 | N/A * |
| 30m | 0.541 | N/A * | 0.943 | N/A * | 0.379 | N/A * |
| 40m | 0.547 | N/A * | 0.954 | N/A * | 0.384 | N/A * |
| 50m | 0.551 | N/A * | 0.960 | N/A * | 0.386 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (58.3%, 58.3%, 58.3%, 58.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

