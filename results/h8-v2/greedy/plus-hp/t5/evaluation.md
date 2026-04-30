# Evaluation: plus-hp-greedy-t5

**Generated**: 2026-04-30T06:53:01.149024+00:00  
**Detections**: 162  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.482 | N/A * | 0.889 | N/A * | 0.331 | N/A * |
| 30m | 0.516 | N/A * | 0.951 | N/A * | 0.354 | N/A * |
| 40m | 0.516 | N/A * | 0.951 | N/A * | 0.354 | N/A * |
| 50m | 0.519 | N/A * | 0.957 | N/A * | 0.356 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (59.3%, 59.3%, 59.3%, 59.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

