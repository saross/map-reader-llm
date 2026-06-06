# Evaluation: filtered

**Generated**: 2026-06-06T01:43:15.377805+00:00  
**Detections**: 3252  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.078 | N/A * | 0.096 | N/A * | 0.066 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 10m | 0.256 | N/A * | 0.315 | N/A * | 0.216 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 15m | 0.444 | N/A * | 0.545 | N/A * | 0.374 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 20m | 0.577 | N/A * | 0.709 | N/A * | 0.486 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 25m | 0.649 | N/A * | 0.798 | N/A * | 0.547 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 30m | 0.686 | N/A * | 0.844 | N/A * | 0.578 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 35m | 0.703 | N/A * | 0.864 | N/A * | 0.592 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 40m | 0.711 | N/A * | 0.874 | N/A * | 0.599 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 45m | 0.714 | N/A * | 0.878 | N/A * | 0.602 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 50m | 0.715 | N/A * | 0.879 | N/A * | 0.602 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 75m | 0.716 | N/A * | 0.881 | N/A * | 0.604 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 100m | 0.717 | N/A * | 0.882 | N/A * | 0.605 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 125m | 0.718 | N/A * | 0.883 | N/A * | 0.605 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |
| 150m | 0.718 | N/A * | 0.883 | N/A * | 0.605 | N/A * | 0.592 | N/A * | 0.540 | 0.970 |

\* Bootstrap CI suppressed for sparse-coverage buffers (65.4%, 65.8%, 66.5%, 67.0%, 67.3%, 67.4%, 67.5%, 67.5%, 67.5%, 67.5%, 67.5%, 67.5%, 67.5%, 67.5% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

