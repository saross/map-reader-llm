# Evaluation: HIGH-t1.0-9of10

**Generated**: 2026-04-30T06:58:08.475585+00:00  
**Detections**: 254  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.639 | N/A * | 0.866 | N/A * | 0.506 | N/A * | 0.644 | N/A * | 0.655 | 0.953 |
| 30m | 0.668 | N/A * | 0.905 | N/A * | 0.529 | N/A * | 0.644 | N/A * | 0.655 | 0.953 |
| 40m | 0.673 | N/A * | 0.913 | N/A * | 0.533 | N/A * | 0.644 | N/A * | 0.655 | 0.953 |
| 50m | 0.676 | N/A * | 0.917 | N/A * | 0.536 | N/A * | 0.644 | N/A * | 0.655 | 0.953 |

\* Bootstrap CI suppressed for sparse-coverage buffers (56.5%, 56.5%, 56.5%, 56.5% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

