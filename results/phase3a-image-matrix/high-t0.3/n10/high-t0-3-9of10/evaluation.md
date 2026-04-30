# Evaluation: HIGH-t0.3-9of10

**Generated**: 2026-04-30T06:57:34.826824+00:00  
**Detections**: 361  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.731 | N/A * | 0.806 | N/A * | 0.669 | N/A * | 0.683 | N/A * | 0.751 | 0.918 |
| 30m | 0.784 | N/A * | 0.864 | N/A * | 0.717 | N/A * | 0.683 | N/A * | 0.751 | 0.918 |
| 40m | 0.794 | N/A * | 0.875 | N/A * | 0.726 | N/A * | 0.683 | N/A * | 0.751 | 0.918 |
| 50m | 0.794 | N/A * | 0.875 | N/A * | 0.726 | N/A * | 0.683 | N/A * | 0.751 | 0.918 |

\* Bootstrap CI suppressed for sparse-coverage buffers (54.6%, 54.6%, 54.6%, 54.6% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

