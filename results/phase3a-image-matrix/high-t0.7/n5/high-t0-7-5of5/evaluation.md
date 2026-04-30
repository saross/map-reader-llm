# Evaluation: HIGH-t0.7-5of5

**Generated**: 2026-04-30T06:57:53.884744+00:00  
**Detections**: 282  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.658 | N/A * | 0.837 | N/A * | 0.542 | N/A * | 0.656 | N/A * | 0.681 | 0.946 |
| 30m | 0.695 | N/A * | 0.883 | N/A * | 0.572 | N/A * | 0.656 | N/A * | 0.681 | 0.946 |
| 40m | 0.709 | N/A * | 0.901 | N/A * | 0.584 | N/A * | 0.656 | N/A * | 0.681 | 0.946 |
| 50m | 0.711 | N/A * | 0.904 | N/A * | 0.586 | N/A * | 0.656 | N/A * | 0.681 | 0.946 |

\* Bootstrap CI suppressed for sparse-coverage buffers (55.6%, 55.6%, 55.6%, 55.6% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `planning/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

