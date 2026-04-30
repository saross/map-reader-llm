# Evaluation: HIGH-t1.0-10of10

**Generated**: 2026-04-30T06:57:55.410090+00:00  
**Detections**: 169  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.507 | N/A * | 0.905 | N/A * | 0.352 | N/A * | 0.562 | N/A * | 0.498 | 0.985 |
| 30m | 0.520 | N/A * | 0.929 | N/A * | 0.361 | N/A * | 0.562 | N/A * | 0.498 | 0.985 |
| 40m | 0.526 | N/A * | 0.941 | N/A * | 0.365 | N/A * | 0.562 | N/A * | 0.498 | 0.985 |
| 50m | 0.526 | N/A * | 0.941 | N/A * | 0.365 | N/A * | 0.562 | N/A * | 0.498 | 0.985 |

\* Bootstrap CI suppressed for sparse-coverage buffers (57.9%, 57.9%, 57.9%, 57.9% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

