# Evaluation: text-high-vs-cleaned-gt

**Generated**: 2026-04-30T06:53:24.395112+00:00  
**Detections**: 4143  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 20m | 0.625 | N/A * | 0.670 | N/A * | 0.585 | N/A * |
| 30m | 0.755 | N/A * | 0.810 | N/A * | 0.708 | N/A * |
| 40m | 0.785 | N/A * | 0.842 | N/A * | 0.736 | N/A * |
| 50m | 0.791 | N/A * | 0.848 | N/A * | 0.741 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (65.7%, 66.2%, 66.3%, 66.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

