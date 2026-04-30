# Evaluation: HIGH-t0.7-7of10

**Generated**: 2026-04-30T06:57:46.050138+00:00  
**Detections**: 405  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.750 | N/A * | 0.778 | N/A * | 0.724 | N/A * | 0.678 | N/A * | 0.803 | 0.872 |
| 30m | 0.809 | N/A * | 0.840 | N/A * | 0.782 | N/A * | 0.678 | N/A * | 0.803 | 0.872 |
| 40m | 0.824 | N/A * | 0.854 | N/A * | 0.795 | N/A * | 0.678 | N/A * | 0.803 | 0.872 |
| 50m | 0.824 | N/A * | 0.854 | N/A * | 0.795 | N/A * | 0.678 | N/A * | 0.803 | 0.872 |

\* Bootstrap CI suppressed for sparse-coverage buffers (51.5%, 51.5%, 51.5%, 51.5% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

