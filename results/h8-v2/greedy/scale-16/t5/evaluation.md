# Evaluation: scale-16-greedy-t5

**Generated**: 2026-04-30T06:53:13.327974+00:00  
**Detections**: 153  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.476 | N/A * | 0.915 | N/A * | 0.322 | N/A * |
| 30m | 0.493 | N/A * | 0.948 | N/A * | 0.333 | N/A * |
| 40m | 0.500 | N/A * | 0.961 | N/A * | 0.338 | N/A * |
| 50m | 0.500 | N/A * | 0.961 | N/A * | 0.338 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (58.5%, 58.5%, 58.5%, 58.5% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

