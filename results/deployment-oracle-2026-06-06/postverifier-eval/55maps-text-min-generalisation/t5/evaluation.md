# Evaluation: filtered

**Generated**: 2026-06-06T01:43:15.998829+00:00  
**Detections**: 3285  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.090 | N/A * | 0.111 | N/A * | 0.076 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 10m | 0.279 | N/A * | 0.341 | N/A * | 0.236 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 15m | 0.455 | N/A * | 0.556 | N/A * | 0.385 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 20m | 0.580 | N/A * | 0.709 | N/A * | 0.491 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 25m | 0.648 | N/A * | 0.792 | N/A * | 0.548 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 30m | 0.682 | N/A * | 0.833 | N/A * | 0.577 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 35m | 0.698 | N/A * | 0.853 | N/A * | 0.590 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 40m | 0.704 | N/A * | 0.861 | N/A * | 0.596 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 45m | 0.708 | N/A * | 0.866 | N/A * | 0.599 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 50m | 0.710 | N/A * | 0.867 | N/A * | 0.600 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 75m | 0.711 | N/A * | 0.869 | N/A * | 0.602 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 100m | 0.712 | N/A * | 0.870 | N/A * | 0.602 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 125m | 0.713 | N/A * | 0.872 | N/A * | 0.604 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |
| 150m | 0.714 | N/A * | 0.873 | N/A * | 0.604 | N/A * | 0.590 | N/A * | 0.551 | 0.964 |

\* Bootstrap CI suppressed for sparse-coverage buffers (65.3%, 65.8%, 66.3%, 66.7%, 67.0%, 67.1%, 67.2%, 67.2%, 67.2%, 67.2%, 67.2%, 67.2%, 67.3%, 67.3% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

