# Evaluation: HIGH-t1.0-8of10

**Generated**: 2026-04-30T06:58:05.524411+00:00  
**Detections**: 319  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.692 | N/A * | 0.818 | N/A * | 0.600 | N/A * | 0.675 | N/A * | 0.720 | 0.934 |
| 30m | 0.737 | N/A * | 0.872 | N/A * | 0.639 | N/A * | 0.675 | N/A * | 0.720 | 0.934 |
| 40m | 0.748 | N/A * | 0.884 | N/A * | 0.648 | N/A * | 0.675 | N/A * | 0.720 | 0.934 |
| 50m | 0.759 | N/A * | 0.897 | N/A * | 0.657 | N/A * | 0.675 | N/A * | 0.720 | 0.934 |

\* Bootstrap CI suppressed for sparse-coverage buffers (55.9%, 55.9%, 55.9%, 55.9% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

