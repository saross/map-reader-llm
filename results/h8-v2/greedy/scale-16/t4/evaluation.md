# Evaluation: scale-16-greedy-t4

**Generated**: 2026-04-30T06:53:12.684424+00:00  
**Detections**: 238  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.571 | N/A * | 0.807 | N/A * | 0.441 | N/A * |
| 30m | 0.603 | N/A * | 0.853 | N/A * | 0.467 | N/A * |
| 40m | 0.621 | N/A * | 0.878 | N/A * | 0.480 | N/A * |
| 50m | 0.630 | N/A * | 0.891 | N/A * | 0.487 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (56.5%, 56.5%, 56.5%, 56.7% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

