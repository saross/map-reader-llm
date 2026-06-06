# Evaluation: consensus_t4

**Generated**: 2026-06-06T01:37:41.303906+00:00  
**Detections**: 4987  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.046 | N/A * | 0.045 | N/A * | 0.047 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 10m | 0.164 | N/A * | 0.160 | N/A * | 0.168 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 15m | 0.297 | N/A * | 0.290 | N/A * | 0.304 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 20m | 0.415 | N/A * | 0.405 | N/A * | 0.426 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 25m | 0.501 | N/A * | 0.489 | N/A * | 0.513 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 30m | 0.550 | N/A * | 0.537 | N/A * | 0.564 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 35m | 0.579 | N/A * | 0.565 | N/A * | 0.594 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 40m | 0.592 | N/A * | 0.578 | N/A * | 0.607 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 45m | 0.602 | N/A * | 0.588 | N/A * | 0.617 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 50m | 0.608 | N/A * | 0.594 | N/A * | 0.624 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 75m | 0.617 | N/A * | 0.602 | N/A * | 0.633 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 100m | 0.620 | N/A * | 0.605 | N/A * | 0.636 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 125m | 0.622 | N/A * | 0.607 | N/A * | 0.638 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |
| 150m | 0.623 | N/A * | 0.608 | N/A * | 0.639 | N/A * | 0.481 | N/A * | 0.661 | 0.815 |

\* Bootstrap CI suppressed for sparse-coverage buffers (54.6%, 55.0%, 55.5%, 55.9%, 56.1%, 56.3%, 56.4%, 56.4%, 56.4%, 56.5%, 56.5%, 56.6%, 56.6%, 56.6% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

