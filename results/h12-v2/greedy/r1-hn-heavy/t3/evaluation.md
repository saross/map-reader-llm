# Evaluation: r1-hn-heavy-greedy-t3

**Generated**: 2026-04-30T06:52:31.397331+00:00  
**Detections**: 327  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.617 | N/A * | 0.719 | N/A * | 0.540 | N/A * |
| 30m | 0.680 | N/A * | 0.792 | N/A * | 0.595 | N/A * |
| 40m | 0.696 | N/A * | 0.810 | N/A * | 0.609 | N/A * |
| 50m | 0.703 | N/A * | 0.820 | N/A * | 0.616 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (54.0%, 54.0%, 54.0%, 54.0% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

