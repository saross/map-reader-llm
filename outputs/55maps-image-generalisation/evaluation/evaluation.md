# Evaluation: 55maps-image-generalisation

**Generated**: 2026-05-03T02:43:59.531135+00:00  
**Detections**: 4680  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.508 | N/A * | 0.511 | N/A * | 0.504 | N/A * | 0.692 | N/A * | 0.708 | 0.948 |
| 30m | 0.689 | N/A * | 0.693 | N/A * | 0.684 | N/A * | 0.692 | N/A * | 0.708 | 0.948 |
| 40m | 0.752 | N/A * | 0.757 | N/A * | 0.747 | N/A * | 0.692 | N/A * | 0.708 | 0.948 |
| 50m | 0.774 | N/A * | 0.780 | N/A * | 0.769 | N/A * | 0.692 | N/A * | 0.708 | 0.948 |

\* Bootstrap CI suppressed for sparse-coverage buffers (64.1%, 64.9%, 65.1%, 65.2% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

