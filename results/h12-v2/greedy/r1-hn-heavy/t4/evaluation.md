# Evaluation: r1-hn-heavy-greedy-t4

**Generated**: 2026-04-30T06:52:32.306587+00:00  
**Detections**: 240  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.584 | N/A * | 0.821 | N/A * | 0.453 | N/A * |
| 30m | 0.634 | N/A * | 0.892 | N/A * | 0.492 | N/A * |
| 40m | 0.643 | N/A * | 0.904 | N/A * | 0.499 | N/A * |
| 50m | 0.643 | N/A * | 0.904 | N/A * | 0.499 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (57.1%, 57.1%, 57.1%, 57.1% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

