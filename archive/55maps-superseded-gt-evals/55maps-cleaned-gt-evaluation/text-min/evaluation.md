# Evaluation: text-min-vs-cleaned-gt

**Generated**: 2026-04-30T06:53:18.871800+00:00  
**Detections**: 3861  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.620 | N/A * | 0.691 | N/A * | 0.562 | N/A * |
| 30m | 0.730 | N/A * | 0.813 | N/A * | 0.662 | N/A * |
| 40m | 0.756 | N/A * | 0.843 | N/A * | 0.686 | N/A * |
| 50m | 0.761 | N/A * | 0.849 | N/A * | 0.691 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (66.0%, 66.5%, 66.6%, 66.6% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

