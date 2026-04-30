# Evaluation: scale-4-greedy-t3

**Generated**: 2026-04-30T06:53:25.300390+00:00  
**Detections**: 330  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.599 | N/A * | 0.694 | N/A * | 0.526 | N/A * |
| 30m | 0.667 | N/A * | 0.773 | N/A * | 0.586 | N/A * |
| 40m | 0.685 | N/A * | 0.794 | N/A * | 0.602 | N/A * |
| 50m | 0.693 | N/A * | 0.803 | N/A * | 0.609 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (52.8%, 53.0%, 53.0%, 53.2% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

