# Evaluation: scale-8-greedy-t4

**Generated**: 2026-04-30T06:53:27.780564+00:00  
**Detections**: 250  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.587 | N/A * | 0.804 | N/A * | 0.462 | N/A * |
| 30m | 0.645 | N/A * | 0.884 | N/A * | 0.508 | N/A * |
| 40m | 0.651 | N/A * | 0.892 | N/A * | 0.513 | N/A * |
| 50m | 0.654 | N/A * | 0.896 | N/A * | 0.515 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (57.3%, 57.3%, 57.3%, 57.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

