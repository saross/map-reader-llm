# Evaluation: accepted_t0.3

**Generated**: 2026-06-08T11:48:46.037685+00:00  
**Detections**: 369  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.438 | N/A * | 0.474 | N/A * | 0.406 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 10m | 0.748 | N/A * | 0.810 | N/A * | 0.694 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 15m | 0.823 | N/A * | 0.892 | N/A * | 0.763 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 20m | 0.840 | N/A * | 0.911 | N/A * | 0.780 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 25m | 0.848 | N/A * | 0.919 | N/A * | 0.786 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 30m | 0.850 | N/A * | 0.921 | N/A * | 0.789 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 35m | 0.853 | N/A * | 0.924 | N/A * | 0.791 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 40m | 0.853 | N/A * | 0.924 | N/A * | 0.791 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 45m | 0.853 | N/A * | 0.924 | N/A * | 0.791 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 50m | 0.853 | N/A * | 0.924 | N/A * | 0.791 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 75m | 0.855 | N/A * | 0.927 | N/A * | 0.793 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 100m | 0.855 | N/A * | 0.927 | N/A * | 0.793 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 125m | 0.855 | N/A * | 0.927 | N/A * | 0.793 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |
| 150m | 0.863 | N/A * | 0.935 | N/A * | 0.800 | N/A * | 0.752 | N/A * | 0.716 | 0.977 |

\* Bootstrap CI suppressed for sparse-coverage buffers (72.0%, 72.4%, 72.6%, 72.8%, 72.9%, 72.9%, 72.9%, 72.9%, 72.9%, 72.9%, 72.9%, 72.9%, 72.9%, 72.9% of evaluation tiles have zero TP/FP/FN counts; threshold > 50 %). Numeric bounds remain in `evaluation.json` and `evaluation.csv` for downstream tooling. The point estimate (F1, P, R, MCC) is unaffected. See `archive/planning-completed-session-81-82/pairwise-bootstrap-ci-fix-plan-2026-04-29.md` for the underlying methodology decision.

