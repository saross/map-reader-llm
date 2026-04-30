# Evaluation: pure-positive-canon-greedy-t5

**Generated**: 2026-04-30T06:53:07.828295+00:00  
**Detections**: 188  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.504 | N/A * | 0.835 | N/A * | 0.361 | N/A * |
| 30m | 0.530 | N/A * | 0.878 | N/A * | 0.379 | N/A * |
| 40m | 0.539 | N/A * | 0.894 | N/A * | 0.386 | N/A * |
| 50m | 0.539 | N/A * | 0.894 | N/A * | 0.386 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (57.3%, 57.3%, 57.3%, 57.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

