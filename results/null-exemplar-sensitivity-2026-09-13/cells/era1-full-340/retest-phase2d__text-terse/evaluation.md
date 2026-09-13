# Evaluation: retest-phase2d__text-terse

**Generated**: 2026-09-13T14:02:20.923338+00:00  
**Detections**: 788  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.236 | [0.193, 0.285] | 0.192 | [0.153, 0.237] | 0.306 | [0.254, 0.365] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.437 | [0.378, 0.497] | 0.355 | [0.297, 0.415] | 0.568 | [0.497, 0.631] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.540 | [0.480, 0.597] | 0.439 | [0.375, 0.502] | 0.702 | [0.638, 0.757] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.592 | [0.533, 0.646] | 0.481 | [0.414, 0.544] | 0.769 | [0.713, 0.817] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.612 | [0.553, 0.666] | 0.497 | [0.430, 0.562] | 0.795 | [0.741, 0.841] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.623 | [0.564, 0.676] | 0.506 | [0.438, 0.571] | 0.809 | [0.756, 0.854] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.634 | [0.575, 0.688] | 0.515 | [0.448, 0.580] | 0.824 | [0.771, 0.867] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.640 | [0.582, 0.694] | 0.520 | [0.452, 0.586] | 0.832 | [0.782, 0.873] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.645 | [0.587, 0.698] | 0.524 | [0.456, 0.589] | 0.838 | [0.789, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.651 | [0.593, 0.703] | 0.529 | [0.460, 0.594] | 0.846 | [0.797, 0.885] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.659 | [0.600, 0.711] | 0.535 | [0.465, 0.600] | 0.856 | [0.810, 0.893] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.662 | [0.603, 0.714] | 0.538 | [0.467, 0.603] | 0.860 | [0.816, 0.895] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.662 | [0.603, 0.714] | 0.538 | [0.467, 0.603] | 0.860 | [0.816, 0.895] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.663 | [0.604, 0.715] | 0.539 | [0.469, 0.604] | 0.862 | [0.818, 0.897] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=193, TN=0, FP=122, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

