# Evaluation: gold-standard-extended-buffer-sweep

**Generated**: 2026-04-30T06:52:29.714506+00:00  
**Detections**: 250  

| Buffer | F1 | F1 CI | P | P CI | R | R CI |
|---|---|---|---|---|---|---|
| 5m | 0.250 | N/A * | 0.284 | N/A * | 0.223 | N/A * |
| 10m | 0.654 | N/A * | 0.744 | N/A * | 0.583 | N/A * |
| 15m | 0.777 | N/A * | 0.884 | N/A * | 0.693 | N/A * |
| 25m | 0.823 | N/A * | 0.936 | N/A * | 0.734 | N/A * |
| 35m | 0.823 | N/A * | 0.936 | N/A * | 0.734 | N/A * |
| 45m | 0.823 | N/A * | 0.936 | N/A * | 0.734 | N/A * |

\* Bootstrap CI suppressed for sparse-coverage buffers (52.9%, 53.5%, 54.1%, 54.4%, 54.4%, 54.4% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

