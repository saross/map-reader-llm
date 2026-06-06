# Evaluation: filtered

**Generated**: 2026-06-06T01:43:00.827472+00:00  
**Detections**: 2283  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.044 | N/A * | 0.068 | N/A * | 0.033 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 10m | 0.162 | N/A * | 0.249 | N/A * | 0.120 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 15m | 0.290 | N/A * | 0.447 | N/A * | 0.215 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 20m | 0.407 | N/A * | 0.626 | N/A * | 0.301 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 25m | 0.485 | N/A * | 0.747 | N/A * | 0.359 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 30m | 0.531 | N/A * | 0.817 | N/A * | 0.393 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 35m | 0.551 | N/A * | 0.849 | N/A * | 0.408 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 40m | 0.561 | N/A * | 0.864 | N/A * | 0.415 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 45m | 0.568 | N/A * | 0.875 | N/A * | 0.421 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 50m | 0.572 | N/A * | 0.881 | N/A * | 0.424 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 75m | 0.577 | N/A * | 0.888 | N/A * | 0.427 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 100m | 0.578 | N/A * | 0.890 | N/A * | 0.428 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 125m | 0.579 | N/A * | 0.890 | N/A * | 0.428 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |
| 150m | 0.579 | N/A * | 0.891 | N/A * | 0.429 | N/A * | 0.530 | N/A * | 0.442 | 0.980 |

\* Bootstrap CI suppressed for sparse-coverage buffers (66.2%, 66.6%, 67.0%, 67.3%, 67.5%, 67.7%, 67.8%, 67.8%, 67.9%, 67.9%, 67.9%, 67.9%, 67.9%, 67.9% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

