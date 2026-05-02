# Evaluation: scale-32-greedy-t4

**Generated**: 2026-04-30T06:53:18.681907+00:00  
**Detections**: 242  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.588 | N/A * | 0.822 | N/A * | 0.458 | N/A * |
| 30m | 0.606 | N/A * | 0.847 | N/A * | 0.471 | N/A * |
| 40m | 0.620 | N/A * | 0.868 | N/A * | 0.483 | N/A * |
| 50m | 0.626 | N/A * | 0.876 | N/A * | 0.487 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (57.1%, 57.1%, 57.1%, 57.1% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

