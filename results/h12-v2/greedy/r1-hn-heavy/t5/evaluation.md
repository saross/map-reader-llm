# Evaluation: r1-hn-heavy-greedy-t5

**Generated**: 2026-04-30T06:52:31.773320+00:00  
**Detections**: 169  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.483 | N/A * | 0.864 | N/A * | 0.336 | N/A * |
| 30m | 0.526 | N/A * | 0.941 | N/A * | 0.365 | N/A * |
| 40m | 0.530 | N/A * | 0.947 | N/A * | 0.368 | N/A * |
| 50m | 0.530 | N/A * | 0.947 | N/A * | 0.368 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (58.3%, 58.3%, 58.3%, 58.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

