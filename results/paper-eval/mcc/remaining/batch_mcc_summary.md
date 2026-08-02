# Tile-Level MCC Summary

> **⚠ Superseded figures (2026-08-02, E72)**: rows 12, 14 and 15
> (`Flash MIN text T=1.0` 5-of-5, 9-of-10 and 22-of-30) derive from
> `outputs/h11/consensus-384-UNINTENDED-T1.0`, a 240-tile study scored against
> 487-tile bounds (coverage confound — see protocol-errata E43 correction block
> and E72). Their confusion cells sum to 487 tiles although only 240 were
> processed, so the tile-level MCC, sensitivity and specificity for these three
> rows are depressed on the same mechanism that understates their F1 by
> ~0.17–0.19. Regenerated 23-condition board: `results/e43-board-regen/`.
> Matched-scope analysis: `results/e43-matched-temperature/`. Dated snapshot;
> body unchanged; do not cite the affected rows.

**Generated**: 2026-03-28T07:14:50.660200+00:00  
**Conditions**: 16  
**Description**: Tile-level MCC for remaining consensus and PV conditions at 384px. Covers flash-min-text-t07/t10, flash-min-image, pro-high-image, single-pass-t0 consensus conditions, and five additional PV conditions with various verifier configurations.
  

| # | Condition | Det | MCC [95% CI] | Sens [95% CI] | Spec [95% CI] | TP | TN | FP | FN |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Image baseline + flash-min-vf | 511 | 0.877 [0.833, 0.919] | 0.943 [0.910, 0.970] | 0.934 [0.902, 0.965] | 216 | 241 | 17 | 13 |
| 2 | Text baseline + flash-min-vf | 464 | 0.833 [0.783, 0.877] | 0.869 [0.827, 0.906] | 0.957 [0.929, 0.981] | 199 | 247 | 11 | 30 |
| 3 | Flash HIGH image 3-of-5 + flash-min-vf | 411 | 0.827 [0.777, 0.873] | 0.847 [0.799, 0.891] | 0.969 [0.948, 0.989] | 194 | 250 | 8 | 35 |
| 4 | Pro HIGH image 3-of-5 | 471 | 0.761 [0.706, 0.816] | 0.843 [0.796, 0.889] | 0.915 [0.881, 0.947] | 193 | 236 | 22 | 36 |
| 5 | Flash HIGH text 9-of-10 + flash-min-vf | 352 | 0.749 [0.696, 0.797] | 0.738 [0.678, 0.789] | 0.981 [0.961, 0.996] | 169 | 253 | 5 | 60 |
| 6 | Flash HIGH text 4-of-5 + flash-medium-vf | 417 | 0.739 [0.679, 0.793] | 0.803 [0.750, 0.853] | 0.926 [0.891, 0.957] | 184 | 239 | 19 | 45 |
| 7 | Flash MIN image 4-of-5 | 523 | 0.390 [0.310, 0.469] | 0.843 [0.794, 0.887] | 0.531 [0.465, 0.594] | 193 | 137 | 121 | 36 |
| 8 | Flash MIN text T=0.7 29-of-30 | 530 | 0.381 [0.302, 0.460] | 0.817 [0.764, 0.864] | 0.554 [0.491, 0.615] | 187 | 143 | 115 | 42 |
| 9 | Flash MIN text T=0.7 10-of-10 | 560 | 0.365 [0.284, 0.444] | 0.834 [0.784, 0.882] | 0.515 [0.454, 0.575] | 191 | 133 | 125 | 38 |
| 10 | Flash MIN image 6-of-10 | 577 | 0.361 [0.283, 0.432] | 0.860 [0.815, 0.904] | 0.477 [0.410, 0.540] | 197 | 123 | 135 | 32 |
| 11 | Flash MIN text T=0.7 5-of-5 | 653 | 0.315 [0.230, 0.395] | 0.860 [0.813, 0.904] | 0.426 [0.366, 0.482] | 197 | 110 | 148 | 32 |
| 12 | Flash MIN text T=1.0 5-of-5 | 295 | 0.257 [0.175, 0.338] | 0.454 [0.391, 0.519] | 0.787 [0.734, 0.835] | 104 | 203 | 55 | 125 |
| 13 | Single-pass T=0.0 10-of-10 | 898 | 0.212 [0.126, 0.293] | 0.913 [0.873, 0.948] | 0.248 [0.196, 0.304] | 209 | 64 | 194 | 20 |
| 14 | Flash MIN text T=1.0 9-of-10 | 319 | 0.212 [0.122, 0.302] | 0.467 [0.406, 0.533] | 0.736 [0.682, 0.789] | 107 | 190 | 68 | 122 |
| 15 | Flash MIN text T=1.0 22-of-30 | 383 | 0.208 [0.122, 0.298] | 0.498 [0.434, 0.567] | 0.705 [0.648, 0.757] | 114 | 182 | 76 | 115 |
| 16 | Single-pass T=0.0 5-of-5 | 951 | 0.178 [0.096, 0.255] | 0.926 [0.891, 0.957] | 0.198 [0.152, 0.247] | 212 | 51 | 207 | 17 |

