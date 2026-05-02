# Evaluation: pro-high-text-consensus-pool-t5

**Generated**: 2026-04-30T06:57:16.474709+00:00  
**Detections**: 369  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 20m | 0.833 | N/A * | 0.908 | N/A * | 0.770 | N/A * | 0.726 | N/A * | 0.747 | 0.957 |
| 30m | 0.851 | N/A * | 0.927 | N/A * | 0.786 | N/A * | 0.726 | N/A * | 0.747 | 0.957 |
| 40m | 0.853 | N/A * | 0.929 | N/A * | 0.788 | N/A * | 0.726 | N/A * | 0.747 | 0.957 |
| 50m | 0.853 | N/A * | 0.929 | N/A * | 0.788 | N/A * | 0.726 | N/A * | 0.747 | 0.957 |

\* Bootstrap CI suppressed for sparse-coverage buffers (57.3%, 57.3%, 57.3%, 57.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

