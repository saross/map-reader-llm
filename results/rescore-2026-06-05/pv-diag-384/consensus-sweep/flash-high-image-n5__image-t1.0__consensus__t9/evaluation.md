# Evaluation: consensus_t9

**Generated**: 2026-06-05T06:53:47.304923+00:00  
**Detections**: 254  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.177 | N/A * | 0.240 | N/A * | 0.140 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 10m | 0.421 | N/A * | 0.571 | N/A * | 0.333 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 15m | 0.578 | N/A * | 0.783 | N/A * | 0.458 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 20m | 0.639 | N/A * | 0.866 | N/A * | 0.506 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 25m | 0.659 | N/A * | 0.894 | N/A * | 0.522 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 30m | 0.668 | N/A * | 0.905 | N/A * | 0.529 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 35m | 0.670 | N/A * | 0.909 | N/A * | 0.531 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 40m | 0.673 | N/A * | 0.913 | N/A * | 0.533 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 45m | 0.673 | N/A * | 0.913 | N/A * | 0.533 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 50m | 0.676 | N/A * | 0.917 | N/A * | 0.536 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 75m | 0.676 | N/A * | 0.917 | N/A * | 0.536 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 100m | 0.676 | N/A * | 0.917 | N/A * | 0.536 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 125m | 0.676 | N/A * | 0.917 | N/A * | 0.536 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |
| 150m | 0.679 | N/A * | 0.921 | N/A * | 0.538 | N/A * | 0.645 | N/A * | 0.655 | 0.954 |

\* Bootstrap CI suppressed for sparse-coverage buffers (55.4%, 55.9%, 56.3%, 56.5%, 56.5%, 56.5%, 56.5%, 56.5%, 56.5%, 56.5%, 56.5%, 56.5%, 56.5%, 56.5% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

