# Evaluation: detections_scale-8_run01

**Generated**: 2026-08-21T13:43:25.733462+00:00  
**Detections**: 770  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.142 | N/A * | 0.121 | N/A * | 0.172 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 10m | 0.345 | N/A * | 0.293 | N/A * | 0.419 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 15m | 0.509 | N/A * | 0.432 | N/A * | 0.618 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 20m | 0.587 | N/A * | 0.499 | N/A * | 0.712 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 25m | 0.639 | N/A * | 0.543 | N/A * | 0.775 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 30m | 0.655 | N/A * | 0.557 | N/A * | 0.796 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 35m | 0.675 | N/A * | 0.574 | N/A * | 0.820 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 40m | 0.688 | N/A * | 0.584 | N/A * | 0.835 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 45m | 0.695 | N/A * | 0.591 | N/A * | 0.844 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 50m | 0.704 | N/A * | 0.599 | N/A * | 0.855 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 75m | 0.721 | N/A * | 0.613 | N/A * | 0.876 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 100m | 0.727 | N/A * | 0.618 | N/A * | 0.883 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 125m | 0.732 | N/A * | 0.622 | N/A * | 0.889 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |
| 150m | 0.735 | N/A * | 0.625 | N/A * | 0.892 | N/A * | 0.150 | N/A * | 1.000 | 0.037 |

\* **Partial coverage** — the detection set does not cover the evaluation bounds it is scored against (partial: 1/340 tiles unprocessed). Ground-truth mounds on unprocessed tiles are counted as artificial false negatives, so the POINT ESTIMATE is deflated as well as the interval; neither is comparable with a full-coverage cell. Re-score both arms against bounds the data actually covers. See erratum E72 in `docs/methodology/preregistration/protocol-errata.md` and `results/evaluation-scopes.md` § 12.

