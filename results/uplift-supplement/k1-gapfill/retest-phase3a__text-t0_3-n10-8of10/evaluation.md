# Evaluation: retest-phase3a__text-t0_3-n10-8of10-n1

**Generated**: 2026-08-29T07:17:27.045590+00:00  
**Detections**: 871  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.265 | [0.220, 0.316] | 0.215 | [0.174, 0.260] | 0.347 | [0.288, 0.406] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.481 | [0.425, 0.539] | 0.389 | [0.333, 0.449] | 0.629 | [0.564, 0.689] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.582 | [0.525, 0.635] | 0.471 | [0.409, 0.531] | 0.761 | [0.704, 0.807] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.606 | [0.550, 0.659] | 0.490 | [0.427, 0.551] | 0.792 | [0.735, 0.837] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.627 | [0.571, 0.677] | 0.507 | [0.443, 0.567] | 0.820 | [0.771, 0.859] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.638 | [0.582, 0.688] | 0.517 | [0.450, 0.577] | 0.835 | [0.787, 0.871] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.647 | [0.591, 0.696] | 0.523 | [0.458, 0.583] | 0.846 | [0.802, 0.881] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.651 | [0.595, 0.700] | 0.527 | [0.461, 0.587] | 0.852 | [0.809, 0.886] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.655 | [0.599, 0.704] | 0.530 | [0.465, 0.591] | 0.857 | [0.817, 0.890] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.658 | [0.602, 0.706] | 0.533 | [0.468, 0.593] | 0.861 | [0.821, 0.894] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.664 | [0.608, 0.712] | 0.537 | [0.471, 0.599] | 0.868 | [0.830, 0.900] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.664 | [0.608, 0.712] | 0.537 | [0.471, 0.599] | 0.868 | [0.830, 0.900] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.665 | [0.609, 0.714] | 0.538 | [0.473, 0.599] | 0.870 | [0.832, 0.901] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.665 | [0.609, 0.714] | 0.538 | [0.473, 0.599] | 0.870 | [0.832, 0.901] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

