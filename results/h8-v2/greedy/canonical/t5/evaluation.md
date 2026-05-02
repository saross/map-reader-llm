# Evaluation: canonical-greedy-t5

**Generated**: 2026-04-30T06:52:55.259350+00:00  
**Detections**: 176  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.491 | N/A * | 0.852 | N/A * | 0.345 | N/A * |
| 30m | 0.524 | N/A * | 0.909 | N/A * | 0.368 | N/A * |
| 40m | 0.534 | N/A * | 0.926 | N/A * | 0.375 | N/A * |
| 50m | 0.534 | N/A * | 0.926 | N/A * | 0.375 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (56.9%, 56.9%, 56.9%, 56.9% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

