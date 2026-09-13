# Evaluation: retest-phase2a__verbose-text

**Generated**: 2026-09-13T14:01:20.114510+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.136 | [0.106, 0.172] | 0.107 | [0.082, 0.138] | 0.186 | [0.145, 0.233] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.323 | [0.275, 0.376] | 0.254 | [0.211, 0.304] | 0.442 | [0.380, 0.504] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.433 | [0.379, 0.490] | 0.341 | [0.289, 0.398] | 0.594 | [0.528, 0.653] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.497 | [0.440, 0.555] | 0.391 | [0.335, 0.452] | 0.681 | [0.615, 0.737] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.529 | [0.471, 0.587] | 0.417 | [0.357, 0.478] | 0.725 | [0.661, 0.778] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.553 | [0.494, 0.611] | 0.436 | [0.374, 0.498] | 0.758 | [0.697, 0.809] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.571 | [0.513, 0.627] | 0.450 | [0.388, 0.512] | 0.782 | [0.724, 0.830] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.583 | [0.525, 0.639] | 0.459 | [0.396, 0.521] | 0.798 | [0.743, 0.843] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.593 | [0.535, 0.648] | 0.467 | [0.404, 0.529] | 0.812 | [0.760, 0.854] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.601 | [0.543, 0.655] | 0.473 | [0.409, 0.535] | 0.823 | [0.772, 0.864] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.610 | [0.552, 0.664] | 0.480 | [0.416, 0.542] | 0.836 | [0.787, 0.874] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.615 | [0.556, 0.668] | 0.484 | [0.419, 0.546] | 0.843 | [0.796, 0.879] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.618 | [0.559, 0.671] | 0.486 | [0.421, 0.549] | 0.846 | [0.801, 0.883] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.620 | [0.561, 0.673] | 0.488 | [0.422, 0.550] | 0.849 | [0.805, 0.885] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here (defined on 0 of 3 passes): the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=193, TN=0, FP=122, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

