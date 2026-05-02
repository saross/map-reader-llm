# Evaluation: HIGH-t1.0-7of10

**Generated**: 2026-04-30T06:58:03.424233+00:00  
**Detections**: 377  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.717 | N/A * | 0.772 | N/A * | 0.669 | N/A * | 0.635 | N/A * | 0.742 | 0.884 |
| 30m | 0.768 | N/A * | 0.828 | N/A * | 0.717 | N/A * | 0.635 | N/A * | 0.742 | 0.884 |
| 40m | 0.783 | N/A * | 0.844 | N/A * | 0.731 | N/A * | 0.635 | N/A * | 0.742 | 0.884 |
| 50m | 0.796 | N/A * | 0.857 | N/A * | 0.743 | N/A * | 0.635 | N/A * | 0.742 | 0.884 |

\* Bootstrap CI suppressed for sparse-coverage buffers (53.2%, 53.2%, 53.2%, 53.2% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

