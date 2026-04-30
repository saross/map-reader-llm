# Evaluation: pure-positive-canon-greedy-t4

**Generated**: 2026-04-30T06:53:09.793745+00:00  
**Detections**: 275  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.580 | N/A * | 0.749 | N/A * | 0.474 | N/A * |
| 30m | 0.617 | N/A * | 0.796 | N/A * | 0.503 | N/A * |
| 40m | 0.631 | N/A * | 0.815 | N/A * | 0.515 | N/A * |
| 50m | 0.631 | N/A * | 0.815 | N/A * | 0.515 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (53.8%, 53.8%, 54.0%, 54.0% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

