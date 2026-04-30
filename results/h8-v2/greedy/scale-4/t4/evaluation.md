# Evaluation: scale-4-greedy-t4

**Generated**: 2026-04-30T06:53:24.055631+00:00  
**Detections**: 257  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.607 | N/A * | 0.817 | N/A * | 0.483 | N/A * |
| 30m | 0.662 | N/A * | 0.891 | N/A * | 0.526 | N/A * |
| 40m | 0.673 | N/A * | 0.907 | N/A * | 0.536 | N/A * |
| 50m | 0.676 | N/A * | 0.910 | N/A * | 0.538 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (57.1%, 57.3%, 57.3%, 57.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

