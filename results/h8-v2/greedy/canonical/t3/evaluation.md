# Evaluation: canonical-greedy-t3

**Generated**: 2026-04-30T06:52:57.284368+00:00  
**Detections**: 346  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.594 | N/A * | 0.670 | N/A * | 0.533 | N/A * |
| 30m | 0.648 | N/A * | 0.731 | N/A * | 0.582 | N/A * |
| 40m | 0.673 | N/A * | 0.760 | N/A * | 0.605 | N/A * |
| 50m | 0.679 | N/A * | 0.766 | N/A * | 0.609 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (50.9%, 50.9%, 50.9%, 51.1% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

