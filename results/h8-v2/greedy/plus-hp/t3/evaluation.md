# Evaluation: plus-hp-greedy-t3

**Generated**: 2026-04-30T06:53:03.711733+00:00  
**Detections**: 347  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.586 | N/A * | 0.660 | N/A * | 0.526 | N/A * |
| 30m | 0.655 | N/A * | 0.738 | N/A * | 0.589 | N/A * |
| 40m | 0.667 | N/A * | 0.752 | N/A * | 0.600 | N/A * |
| 50m | 0.675 | N/A * | 0.761 | N/A * | 0.607 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (50.7%, 50.7%, 50.7%, 50.7% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

