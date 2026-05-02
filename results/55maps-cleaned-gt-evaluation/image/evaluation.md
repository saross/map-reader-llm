# Evaluation: image-vs-cleaned-gt

**Generated**: 2026-04-30T06:53:22.778332+00:00  
**Detections**: 4665  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.507 | N/A * | 0.511 | N/A * | 0.503 | N/A * |
| 30m | 0.687 | N/A * | 0.693 | N/A * | 0.681 | N/A * |
| 40m | 0.750 | N/A * | 0.756 | N/A * | 0.744 | N/A * |
| 50m | 0.773 | N/A * | 0.779 | N/A * | 0.766 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (64.1%, 64.8%, 65.1%, 65.1% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

