# Evaluation: r2-balanced-greedy-t5

**Generated**: 2026-04-30T06:52:38.784529+00:00  
**Detections**: 163  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.485 | N/A * | 0.890 | N/A * | 0.333 | N/A * |
| 30m | 0.515 | N/A * | 0.945 | N/A * | 0.354 | N/A * |
| 40m | 0.518 | N/A * | 0.951 | N/A * | 0.356 | N/A * |
| 50m | 0.518 | N/A * | 0.951 | N/A * | 0.356 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (58.5%, 58.5%, 58.5%, 58.5% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

