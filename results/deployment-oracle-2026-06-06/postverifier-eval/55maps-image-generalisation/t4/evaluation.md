# Evaluation: filtered

**Generated**: 2026-06-06T01:43:19.551500+00:00  
**Detections**: 3541  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.055 | N/A * | 0.064 | N/A * | 0.048 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 10m | 0.194 | N/A * | 0.227 | N/A * | 0.170 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 15m | 0.351 | N/A * | 0.410 | N/A * | 0.306 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 20m | 0.489 | N/A * | 0.572 | N/A * | 0.427 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 25m | 0.594 | N/A * | 0.695 | N/A * | 0.519 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 30m | 0.654 | N/A * | 0.765 | N/A * | 0.571 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 35m | 0.686 | N/A * | 0.802 | N/A * | 0.599 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 40m | 0.703 | N/A * | 0.823 | N/A * | 0.614 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 45m | 0.714 | N/A * | 0.836 | N/A * | 0.624 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 50m | 0.721 | N/A * | 0.844 | N/A * | 0.629 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 75m | 0.731 | N/A * | 0.855 | N/A * | 0.638 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 100m | 0.733 | N/A * | 0.858 | N/A * | 0.640 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 125m | 0.735 | N/A * | 0.861 | N/A * | 0.642 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |
| 150m | 0.736 | N/A * | 0.861 | N/A * | 0.643 | N/A * | 0.638 | N/A * | 0.607 | 0.966 |

\* Bootstrap CI suppressed for sparse-coverage buffers (64.6%, 65.0%, 65.4%, 65.8%, 66.2%, 66.4%, 66.5%, 66.7%, 66.7%, 66.7%, 66.8%, 66.8%, 66.8%, 66.8% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

