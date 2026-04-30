# Evaluation: scale-8-greedy-t5

**Generated**: 2026-04-30T06:53:27.101555+00:00  
**Detections**: 157  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.460 | N/A * | 0.866 | N/A * | 0.313 | N/A * |
| 30m | 0.497 | N/A * | 0.936 | N/A * | 0.338 | N/A * |
| 40m | 0.500 | N/A * | 0.943 | N/A * | 0.340 | N/A * |
| 50m | 0.503 | N/A * | 0.949 | N/A * | 0.343 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (58.3%, 58.3%, 58.3%, 58.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

