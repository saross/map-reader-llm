# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-29T06:15:34.565434+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 638 | 21301 | 4372 | 4731 | 279 | 5010 | 0.0291 [0.0266, 0.0317] | 0.1273 [0.1177, 0.1372] | **0.0473** [0.0434, 0.0514] | 0.2377 [0.2217, 0.2529] |
| 10 | 1734 | 20205 | 3276 | 4731 | 279 | 5010 | 0.0790 [0.0743, 0.0838] | 0.3461 [0.3311, 0.3607] | **0.1287** [0.1216, 0.1358] | 0.2377 [0.2217, 0.2529] |
| 15 | 2688 | 19251 | 2322 | 4731 | 279 | 5010 | 0.1225 [0.1162, 0.1291] | 0.5365 [0.5207, 0.5524] | **0.1995** [0.1904, 0.2087] | 0.2377 [0.2217, 0.2529] |
| 20 | 3390 | 18549 | 1620 | 4731 | 279 | 5010 | 0.1545 [0.1471, 0.1622] | 0.6766 [0.6619, 0.6917] | **0.2516** [0.2411, 0.2622] | 0.2377 [0.2217, 0.2529] |
| 25 | 3863 | 18076 | 1147 | 4731 | 279 | 5010 | 0.1761 [0.1678, 0.1845] | 0.7711 [0.7579, 0.7844] | **0.2867** [0.2751, 0.2982] | 0.2377 [0.2217, 0.2529] |
| 30 | 4136 | 17803 | 874 | 4731 | 279 | 5010 | 0.1885 [0.1798, 0.1974] | 0.8255 [0.8136, 0.8375] | **0.3070** [0.2950, 0.3189] | 0.2377 [0.2217, 0.2529] |
| 35 | 4282 | 17657 | 728 | 4731 | 279 | 5010 | 0.1952 [0.1863, 0.2042] | 0.8547 [0.8435, 0.8657] | **0.3178** [0.3056, 0.3300] | 0.2377 [0.2217, 0.2529] |
| 40 | 4358 | 17581 | 652 | 4731 | 279 | 5010 | 0.1986 [0.1896, 0.2078] | 0.8699 [0.8592, 0.8802] | **0.3234** [0.3112, 0.3357] | 0.2377 [0.2217, 0.2529] |
| 45 | 4415 | 17524 | 595 | 4731 | 279 | 5010 | 0.2012 [0.1921, 0.2105] | 0.8812 [0.8709, 0.8912] | **0.3277** [0.3152, 0.3400] | 0.2377 [0.2217, 0.2529] |
| 50 | 4443 | 17496 | 567 | 4731 | 279 | 5010 | 0.2025 [0.1933, 0.2118] | 0.8868 [0.8767, 0.8966] | **0.3297** [0.3173, 0.3421] | 0.2377 [0.2217, 0.2529] |
| 75 | 4513 | 17426 | 497 | 4731 | 279 | 5010 | 0.2057 [0.1964, 0.2151] | 0.9008 [0.8913, 0.9099] | **0.3349** [0.3223, 0.3475] | 0.2377 [0.2217, 0.2529] |
| 100 | 4542 | 17397 | 468 | 4731 | 279 | 5010 | 0.2070 [0.1977, 0.2165] | 0.9066 [0.8974, 0.9154] | **0.3371** [0.3245, 0.3497] | 0.2377 [0.2217, 0.2529] |
| 125 | 4559 | 17380 | 451 | 4731 | 279 | 5010 | 0.2078 [0.1985, 0.2173] | 0.9100 [0.9010, 0.9188] | **0.3383** [0.3258, 0.3510] | 0.2377 [0.2217, 0.2529] |
| 150 | 4574 | 17365 | 436 | 4731 | 279 | 5010 | 0.2085 [0.1992, 0.2180] | 0.9130 [0.9041, 0.9216] | **0.3395** [0.3268, 0.3521] | 0.2377 [0.2217, 0.2529] |

## How to read this table

- **Reference**: the ruling-21 standardised layers — the standardised
  student ground truth plus the standardised extension layer (confirmed
  mounds the students missed, at marked centres ±2.5 m). Because marked
  centres are exactly localised, the extension layer enters the extended
  ground truth **whole at every R**: the legacy ring gate (Obs 371) is
  dissolved, `n_extension` is constant across rows, and only the Hungarian
  matching radius varies with R. Sub-50 m rows are therefore genuine
  Track-2 figures, not a collapse to the student layer.
- **n_ref_student**: standardised student records scoped to the evaluation
  tile bounds.
- **n_extension**: extension records admitted to the extended GT before
  tile scoping (0 dropped by the 5 m channel-duplicate audit —
  expected 0 on the standardised layers, whose minimum
  `nearest_student_m` is 10.32 m).
- **n_ref_extended**: scoped extended-GT count — the recall denominator.
- **Tile MCC** (when present) is computed against the SAME extended GT.
  Tile classification does not use the matching radius, and the extended
  GT no longer varies with R, so MCC is constant across rows by
  construction.
- **Known reference biases** (Obs 396, artefact README): residual
  long-range duplicates deflate F1 ≈ −0.03 at a balanced operating point;
  absent joint student+model misses inflate it ≈ +0.011–0.012; net at
  point estimates ≈ −0.017, rank-preserving to first order.

## Reproducibility

- **Inputs**:
  - Detections: `outputs/55maps-text-high-t0.3-generalisation/proposer/detect_brief-text/run_1/detections-detect_brief-text-3-flash-2026-04-26.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
