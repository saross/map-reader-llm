# Evaluation: verified-adv-text-baseline

**Generated**: 2026-06-12T07:14:22.447429+00:00  
**Detections**: 464  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.423 | N/A * | 0.409 | N/A * | 0.437 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 10m | 0.692 | N/A * | 0.670 | N/A * | 0.715 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 15m | 0.779 | N/A * | 0.754 | N/A * | 0.805 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 20m | 0.814 | N/A * | 0.789 | N/A * | 0.841 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 25m | 0.825 | N/A * | 0.800 | N/A * | 0.853 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 30m | 0.832 | N/A * | 0.806 | N/A * | 0.860 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 35m | 0.834 | N/A * | 0.808 | N/A * | 0.862 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 40m | 0.839 | N/A * | 0.812 | N/A * | 0.867 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 45m | 0.839 | N/A * | 0.812 | N/A * | 0.867 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 50m | 0.839 | N/A * | 0.812 | N/A * | 0.867 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 75m | 0.841 | N/A * | 0.815 | N/A * | 0.869 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 100m | 0.848 | N/A * | 0.821 | N/A * | 0.876 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 125m | 0.850 | N/A * | 0.823 | N/A * | 0.878 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |
| 150m | 0.850 | N/A * | 0.823 | N/A * | 0.878 | N/A * | 0.833 | N/A * | 0.869 | 0.957 |

\* Bootstrap CI suppressed for sparse-coverage buffers (53.8%, 54.6%, 54.8%, 54.8%, 54.8%, 54.8%, 54.8%, 54.8%, 54.8%, 54.8%, 54.8%, 54.8%, 54.8%, 54.8% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

