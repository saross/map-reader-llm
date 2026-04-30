# Evaluation: scale-32-greedy-t5

**Generated**: 2026-04-30T06:53:18.343618+00:00  
**Detections**: 158  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.479 | N/A * | 0.899 | N/A * | 0.326 | N/A * |
| 30m | 0.489 | N/A * | 0.918 | N/A * | 0.333 | N/A * |
| 40m | 0.496 | N/A * | 0.930 | N/A * | 0.338 | N/A * |
| 50m | 0.499 | N/A * | 0.937 | N/A * | 0.340 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (58.5%, 58.5%, 58.5%, 58.5% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

