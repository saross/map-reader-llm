# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-29T10:50:35.663341+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 650 | 9520 | 4360 | 4731 | 279 | 5010 | 0.0639 [0.0584, 0.0695] | 0.1297 [0.1195, 0.1397] | **0.0856** [0.0785, 0.0926] | 0.1079 [0.0875, 0.1285] |
| 10 | 1655 | 8515 | 3355 | 4731 | 279 | 5010 | 0.1627 [0.1534, 0.1722] | 0.3303 [0.3152, 0.3455] | **0.2181** [0.2068, 0.2293] | 0.1079 [0.0875, 0.1285] |
| 15 | 2497 | 7673 | 2513 | 4731 | 279 | 5010 | 0.2455 [0.2338, 0.2573] | 0.4984 [0.4820, 0.5152] | **0.3290** [0.3159, 0.3423] | 0.1079 [0.0875, 0.1285] |
| 20 | 3059 | 7111 | 1951 | 4731 | 279 | 5010 | 0.3008 [0.2875, 0.3141] | 0.6106 [0.5942, 0.6271] | **0.4030** [0.3891, 0.4171] | 0.1079 [0.0875, 0.1285] |
| 25 | 3370 | 6800 | 1640 | 4731 | 279 | 5010 | 0.3314 [0.3174, 0.3451] | 0.6727 [0.6569, 0.6884] | **0.4440** [0.4296, 0.4582] | 0.1079 [0.0875, 0.1285] |
| 30 | 3529 | 6641 | 1481 | 4731 | 279 | 5010 | 0.3470 [0.3327, 0.3613] | 0.7044 [0.6892, 0.7195] | **0.4650** [0.4503, 0.4793] | 0.1079 [0.0875, 0.1285] |
| 35 | 3611 | 6559 | 1399 | 4731 | 279 | 5010 | 0.3551 [0.3407, 0.3694] | 0.7208 [0.7057, 0.7356] | **0.4758** [0.4610, 0.4901] | 0.1079 [0.0875, 0.1285] |
| 40 | 3642 | 6528 | 1368 | 4731 | 279 | 5010 | 0.3581 [0.3436, 0.3724] | 0.7269 [0.7121, 0.7418] | **0.4798** [0.4651, 0.4943] | 0.1079 [0.0875, 0.1285] |
| 45 | 3658 | 6512 | 1352 | 4731 | 279 | 5010 | 0.3597 [0.3451, 0.3740] | 0.7301 [0.7154, 0.7449] | **0.4819** [0.4671, 0.4964] | 0.1079 [0.0875, 0.1285] |
| 50 | 3666 | 6504 | 1344 | 4731 | 279 | 5010 | 0.3605 [0.3460, 0.3749] | 0.7317 [0.7170, 0.7465] | **0.4830** [0.4682, 0.4975] | 0.1079 [0.0875, 0.1285] |
| 75 | 3674 | 6496 | 1336 | 4731 | 279 | 5010 | 0.3613 [0.3468, 0.3757] | 0.7333 [0.7186, 0.7480] | **0.4841** [0.4693, 0.4986] | 0.1079 [0.0875, 0.1285] |
| 100 | 3684 | 6486 | 1326 | 4731 | 279 | 5010 | 0.3622 [0.3477, 0.3767] | 0.7353 [0.7207, 0.7499] | **0.4854** [0.4707, 0.4998] | 0.1079 [0.0875, 0.1285] |
| 125 | 3687 | 6483 | 1323 | 4731 | 279 | 5010 | 0.3625 [0.3480, 0.3770] | 0.7359 [0.7214, 0.7505] | **0.4858** [0.4711, 0.5002] | 0.1079 [0.0875, 0.1285] |
| 150 | 3693 | 6477 | 1317 | 4731 | 279 | 5010 | 0.3631 [0.3486, 0.3776] | 0.7371 [0.7225, 0.7517] | **0.4866** [0.4719, 0.5010] | 0.1079 [0.0875, 0.1285] |

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
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-min-generalisation__verified-k4-standardised-gt/twin-4of5.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
