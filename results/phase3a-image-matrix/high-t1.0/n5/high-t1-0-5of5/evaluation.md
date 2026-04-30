# Evaluation: HIGH-t1.0-5of5

**Generated**: 2026-04-30T06:58:12.724201+00:00  
**Detections**: 248  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.612 | N/A * | 0.843 | N/A * | 0.480 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 30m | 0.644 | N/A * | 0.887 | N/A * | 0.506 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 40m | 0.650 | N/A * | 0.895 | N/A * | 0.510 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |
| 50m | 0.656 | N/A * | 0.903 | N/A * | 0.515 | N/A * | 0.635 | N/A * | 0.650 | 0.949 |

\* Bootstrap CI suppressed for sparse-coverage buffers (56.3%, 56.3%, 56.3%, 56.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

