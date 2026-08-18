# Evaluation: detections_pure-positive-2hp_run01

**Generated**: 2026-08-18T13:03:40.828603+00:00  
**Detections**: 823  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.148 | [0.143, 0.153] | 0.123 | [0.118, 0.127] | 0.187 | [0.181, 0.193] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.339 | [0.331, 0.347] | 0.281 | [0.272, 0.288] | 0.429 | [0.418, 0.438] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.501 | [0.492, 0.510] | 0.414 | [0.405, 0.424] | 0.633 | [0.623, 0.643] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.571 | [0.562, 0.580] | 0.473 | [0.462, 0.482] | 0.722 | [0.713, 0.730] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.617 | [0.609, 0.626] | 0.510 | [0.500, 0.520] | 0.779 | [0.770, 0.787] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.631 | [0.623, 0.640] | 0.522 | [0.512, 0.532] | 0.798 | [0.790, 0.806] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.653 | [0.645, 0.662] | 0.541 | [0.530, 0.552] | 0.826 | [0.816, 0.833] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.665 | [0.657, 0.674] | 0.550 | [0.540, 0.561] | 0.840 | [0.832, 0.847] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.671 | [0.663, 0.680] | 0.555 | [0.545, 0.566] | 0.848 | [0.839, 0.855] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.678 | [0.669, 0.687] | 0.561 | [0.551, 0.572] | 0.857 | [0.849, 0.864] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.690 | [0.682, 0.699] | 0.571 | [0.560, 0.582] | 0.872 | [0.864, 0.879] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.696 | [0.688, 0.705] | 0.576 | [0.566, 0.587] | 0.879 | [0.872, 0.886] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.698 | [0.690, 0.706] | 0.577 | [0.567, 0.588] | 0.881 | [0.874, 0.887] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.700 | [0.692, 0.709] | 0.580 | [0.569, 0.590] | 0.885 | [0.877, 0.891] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

