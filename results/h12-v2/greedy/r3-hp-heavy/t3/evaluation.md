# Evaluation: r3-hp-heavy-greedy-t3

**Generated**: 2026-04-30T06:52:45.895455+00:00  
**Detections**: 326  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.591 | N/A * | 0.690 | N/A * | 0.517 | N/A * |
| 30m | 0.665 | N/A * | 0.776 | N/A * | 0.582 | N/A * |
| 40m | 0.683 | N/A * | 0.797 | N/A * | 0.598 | N/A * |
| 50m | 0.691 | N/A * | 0.807 | N/A * | 0.605 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (54.6%, 54.6%, 54.8%, 54.8% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

