# Evaluation: HIGH-t0.7-8of10

**Generated**: 2026-04-30T06:57:47.451943+00:00  
**Detections**: 344  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.729 | N/A * | 0.826 | N/A * | 0.653 | N/A * | 0.678 | N/A * | 0.750 | 0.915 |
| 30m | 0.778 | N/A * | 0.881 | N/A * | 0.697 | N/A * | 0.678 | N/A * | 0.750 | 0.915 |
| 40m | 0.788 | N/A * | 0.892 | N/A * | 0.706 | N/A * | 0.678 | N/A * | 0.750 | 0.915 |
| 50m | 0.788 | N/A * | 0.892 | N/A * | 0.706 | N/A * | 0.678 | N/A * | 0.750 | 0.915 |

\* Bootstrap CI suppressed for sparse-coverage buffers (54.0%, 54.0%, 54.0%, 54.0% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

