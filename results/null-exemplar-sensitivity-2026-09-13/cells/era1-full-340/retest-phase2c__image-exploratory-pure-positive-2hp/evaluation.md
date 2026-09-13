# Evaluation: retest-phase2c__image-exploratory-pure-positive-2hp

**Generated**: 2026-09-13T14:01:52.810147+00:00  
**Detections**: 746  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.145 | [0.116, 0.178] | 0.121 | [0.094, 0.149] | 0.183 | [0.146, 0.224] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.337 | [0.295, 0.382] | 0.280 | [0.238, 0.324] | 0.424 | [0.374, 0.476] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.497 | [0.448, 0.545] | 0.413 | [0.359, 0.461] | 0.625 | [0.565, 0.678] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.571 | [0.517, 0.619] | 0.474 | [0.414, 0.526] | 0.718 | [0.659, 0.769] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.615 | [0.561, 0.661] | 0.511 | [0.447, 0.563] | 0.773 | [0.717, 0.819] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.629 | [0.576, 0.676] | 0.523 | [0.458, 0.576] | 0.791 | [0.736, 0.837] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.647 | [0.593, 0.694] | 0.537 | [0.470, 0.590] | 0.813 | [0.758, 0.858] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.660 | [0.605, 0.706] | 0.548 | [0.480, 0.601] | 0.830 | [0.775, 0.872] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.667 | [0.612, 0.713] | 0.554 | [0.486, 0.607] | 0.838 | [0.783, 0.880] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.675 | [0.620, 0.719] | 0.560 | [0.492, 0.614] | 0.848 | [0.797, 0.888] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.688 | [0.631, 0.732] | 0.571 | [0.501, 0.625] | 0.864 | [0.813, 0.903] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.694 | [0.639, 0.737] | 0.576 | [0.506, 0.630] | 0.872 | [0.824, 0.908] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.696 | [0.641, 0.739] | 0.578 | [0.508, 0.632] | 0.874 | [0.829, 0.909] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.699 | [0.644, 0.741] | 0.580 | [0.511, 0.634] | 0.878 | [0.834, 0.913] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here: the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=193, TN=0, FP=122, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

