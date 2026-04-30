# Evaluation: 512px-text-t0

**Generated**: 2026-04-30T06:53:41.542410+00:00  
**Detections**: 884  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.537 | N/A * | 0.401 | N/A * | 0.814 | N/A * |
| 30m | 0.567 | N/A * | 0.423 | N/A * | 0.860 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (81.9%, 83.4% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

