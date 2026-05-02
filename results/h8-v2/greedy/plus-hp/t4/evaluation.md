# Evaluation: plus-hp-greedy-t4

**Generated**: 2026-04-30T06:53:02.013020+00:00  
**Detections**: 254  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.584 | N/A * | 0.791 | N/A * | 0.462 | N/A * |
| 30m | 0.641 | N/A * | 0.870 | N/A * | 0.508 | N/A * |
| 40m | 0.650 | N/A * | 0.882 | N/A * | 0.515 | N/A * |
| 50m | 0.653 | N/A * | 0.886 | N/A * | 0.517 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (57.1%, 57.1%, 57.1%, 57.1% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

