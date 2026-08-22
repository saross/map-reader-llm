# Evaluation: T0.7

**Generated**: 2026-08-21T13:42:50.104919+00:00  
**Runs**: 3  
**Detections**: —  

| Buffer | F1 | F1 CI | P | P CI | R | R CI | MCC | MCC CI | Sens | Spec |
|---|---|---|---|---|---|---|---|---|---|---|
| 5m | 0.219 | [0.182, 0.260] | 0.172 | [0.140, 0.209] | 0.299 | [0.251, 0.348] | undefined | undefined | 1.000 | 0.000 |
| 10m | 0.448 | [0.393, 0.504] | 0.353 | [0.298, 0.410] | 0.612 | [0.553, 0.669] | undefined | undefined | 1.000 | 0.000 |
| 15m | 0.545 | [0.486, 0.601] | 0.430 | [0.367, 0.491] | 0.745 | [0.687, 0.793] | undefined | undefined | 1.000 | 0.000 |
| 20m | 0.584 | [0.524, 0.641] | 0.461 | [0.397, 0.524] | 0.798 | [0.743, 0.843] | undefined | undefined | 1.000 | 0.000 |
| 25m | 0.601 | [0.541, 0.658] | 0.474 | [0.409, 0.537] | 0.821 | [0.768, 0.864] | undefined | undefined | 1.000 | 0.000 |
| 30m | 0.612 | [0.552, 0.668] | 0.483 | [0.417, 0.547] | 0.837 | [0.787, 0.876] | undefined | undefined | 1.000 | 0.000 |
| 35m | 0.621 | [0.561, 0.677] | 0.490 | [0.424, 0.554] | 0.849 | [0.801, 0.887] | undefined | undefined | 1.000 | 0.000 |
| 40m | 0.624 | [0.565, 0.679] | 0.492 | [0.427, 0.557] | 0.854 | [0.808, 0.889] | undefined | undefined | 1.000 | 0.000 |
| 45m | 0.628 | [0.569, 0.683] | 0.496 | [0.430, 0.560] | 0.859 | [0.814, 0.894] | undefined | undefined | 1.000 | 0.000 |
| 50m | 0.632 | [0.572, 0.686] | 0.498 | [0.432, 0.563] | 0.863 | [0.820, 0.897] | undefined | undefined | 1.000 | 0.000 |
| 75m | 0.636 | [0.576, 0.690] | 0.501 | [0.434, 0.567] | 0.869 | [0.826, 0.902] | undefined | undefined | 1.000 | 0.000 |
| 100m | 0.638 | [0.578, 0.692] | 0.503 | [0.436, 0.568] | 0.871 | [0.830, 0.904] | undefined | undefined | 1.000 | 0.000 |
| 125m | 0.638 | [0.579, 0.693] | 0.503 | [0.436, 0.569] | 0.873 | [0.831, 0.905] | undefined | undefined | 1.000 | 0.000 |
| 150m | 0.639 | [0.580, 0.693] | 0.504 | [0.437, 0.569] | 0.873 | [0.832, 0.906] | undefined | undefined | 1.000 | 0.000 |

**Undefined MCC** — the tile-level Matthews Correlation Coefficient is not computable here (defined on 0 of 3 passes): the 2 x 2 tile confusion matrix is degenerate, so the denominator sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN)) vanishes (TP=204, TN=0, FP=136, FN=0). It is reported as `undefined` rather than 0.000, because 0 on this scale means "random" (§ 4.2 of the preregistration) and would assert a measurement that was not made. See erratum E81 in `docs/methodology/preregistration/protocol-errata.md`.

