# Evaluation: detections_pure-positive-canon_run01

**Generated**: 2026-08-18T13:03:43.299251+00:00  
**Detections**: 887  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.268 | [0.260, 0.276] | 0.215 | [0.208, 0.223] | 0.354 | [0.344, 0.365] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.477 | [0.466, 0.487] | 0.383 | [0.372, 0.393] | 0.631 | [0.619, 0.642] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.562 | [0.552, 0.573] | 0.452 | [0.441, 0.463] | 0.744 | [0.734, 0.753] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.605 | [0.595, 0.615] | 0.486 | [0.474, 0.497] | 0.800 | [0.790, 0.808] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.628 | [0.618, 0.638] | 0.505 | [0.492, 0.516] | 0.831 | [0.823, 0.838] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.641 | [0.631, 0.651] | 0.515 | [0.503, 0.526] | 0.848 | [0.840, 0.854] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.647 | [0.636, 0.656] | 0.520 | [0.508, 0.531] | 0.855 | [0.848, 0.862] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.651 | [0.641, 0.660] | 0.523 | [0.511, 0.534] | 0.861 | [0.854, 0.867] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.654 | [0.643, 0.663] | 0.525 | [0.514, 0.536] | 0.865 | [0.858, 0.871] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.655 | [0.645, 0.664] | 0.526 | [0.515, 0.538] | 0.866 | [0.859, 0.872] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.658 | [0.648, 0.667] | 0.529 | [0.517, 0.540] | 0.870 | [0.863, 0.876] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.659 | [0.649, 0.669] | 0.530 | [0.518, 0.541] | 0.872 | [0.865, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.659 | [0.649, 0.669] | 0.530 | [0.518, 0.541] | 0.872 | [0.865, 0.878] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.661 | [0.651, 0.670] | 0.531 | [0.519, 0.542] | 0.874 | [0.867, 0.880] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

