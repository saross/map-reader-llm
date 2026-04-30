# Evaluation: scale-8-greedy-t3

**Generated**: 2026-04-30T06:53:26.426003+00:00  
**Detections**: 317  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.614 | N/A * | 0.729 | N/A * | 0.531 | N/A * |
| 30m | 0.668 | N/A * | 0.792 | N/A * | 0.577 | N/A * |
| 40m | 0.681 | N/A * | 0.808 | N/A * | 0.589 | N/A * |
| 50m | 0.686 | N/A * | 0.814 | N/A * | 0.593 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (55.2%, 55.2%, 55.2%, 55.2% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

