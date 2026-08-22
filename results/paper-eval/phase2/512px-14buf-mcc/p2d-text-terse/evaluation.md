# Evaluation: detections_terse_run01

**Generated**: 2026-08-21T13:43:59.467074+00:00  
**Detections**: 868  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.242 | [0.201, 0.291] | 0.196 | [0.159, 0.241] | 0.315 | [0.264, 0.372] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.441 | [0.383, 0.499] | 0.357 | [0.300, 0.416] | 0.575 | [0.508, 0.638] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.546 | [0.487, 0.603] | 0.442 | [0.379, 0.504] | 0.712 | [0.651, 0.765] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.598 | [0.540, 0.652] | 0.485 | [0.420, 0.547] | 0.781 | [0.727, 0.826] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.617 | [0.559, 0.669] | 0.500 | [0.434, 0.563] | 0.805 | [0.753, 0.848] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.627 | [0.569, 0.679] | 0.508 | [0.442, 0.572] | 0.818 | [0.767, 0.860] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.637 | [0.577, 0.689] | 0.516 | [0.449, 0.580] | 0.831 | [0.781, 0.872] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.644 | [0.585, 0.696] | 0.522 | [0.454, 0.586] | 0.840 | [0.794, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.648 | [0.590, 0.700] | 0.525 | [0.457, 0.589] | 0.846 | [0.800, 0.883] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.654 | [0.596, 0.705] | 0.530 | [0.462, 0.593] | 0.853 | [0.808, 0.890] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.661 | [0.603, 0.712] | 0.536 | [0.467, 0.599] | 0.863 | [0.820, 0.897] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.664 | [0.606, 0.715] | 0.538 | [0.469, 0.602] | 0.866 | [0.824, 0.900] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.664 | [0.606, 0.715] | 0.538 | [0.469, 0.602] | 0.866 | [0.824, 0.900] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.665 | [0.607, 0.716] | 0.539 | [0.470, 0.603] | 0.868 | [0.826, 0.901] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

