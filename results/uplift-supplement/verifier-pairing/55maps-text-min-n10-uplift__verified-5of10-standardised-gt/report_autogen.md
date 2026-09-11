# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-09-10T23:58:34.963969+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 718 | 11558 | 4292 | 4731 | 279 | 5010 | 0.0585 [0.0537, 0.0634] | 0.1433 [0.1326, 0.1539] | **0.0831** [0.0766, 0.0897] | 0.0565 [0.0354, 0.0771] |
| 10 | 1840 | 10436 | 3170 | 4731 | 279 | 5010 | 0.1499 [0.1414, 0.1586] | 0.3673 [0.3518, 0.3825] | **0.2129** [0.2023, 0.2238] | 0.0565 [0.0354, 0.0771] |
| 15 | 2744 | 9532 | 2266 | 4731 | 279 | 5010 | 0.2235 [0.2129, 0.2344] | 0.5477 [0.5315, 0.5640] | **0.3175** [0.3048, 0.3302] | 0.0565 [0.0354, 0.0771] |
| 20 | 3364 | 8912 | 1646 | 4731 | 279 | 5010 | 0.2740 [0.2621, 0.2863] | 0.6715 [0.6558, 0.6870] | **0.3892** [0.3757, 0.4029] | 0.0565 [0.0354, 0.0771] |
| 25 | 3741 | 8535 | 1269 | 4731 | 279 | 5010 | 0.3047 [0.2921, 0.3175] | 0.7467 [0.7322, 0.7610] | **0.4328** [0.4186, 0.4469] | 0.0565 [0.0354, 0.0771] |
| 30 | 3922 | 8354 | 1088 | 4731 | 279 | 5010 | 0.3195 [0.3065, 0.3326] | 0.7828 [0.7692, 0.7963] | **0.4538** [0.4395, 0.4678] | 0.0565 [0.0354, 0.0771] |
| 35 | 4003 | 8273 | 1007 | 4731 | 279 | 5010 | 0.3261 [0.3129, 0.3392] | 0.7990 [0.7859, 0.8119] | **0.4631** [0.4487, 0.4771] | 0.0565 [0.0354, 0.0771] |
| 40 | 4044 | 8232 | 966 | 4731 | 279 | 5010 | 0.3294 [0.3161, 0.3426] | 0.8072 [0.7942, 0.8197] | **0.4679** [0.4534, 0.4820] | 0.0565 [0.0354, 0.0771] |
| 45 | 4062 | 8214 | 948 | 4731 | 279 | 5010 | 0.3309 [0.3175, 0.3441] | 0.8108 [0.7980, 0.8234] | **0.4700** [0.4555, 0.4840] | 0.0565 [0.0354, 0.0771] |
| 50 | 4069 | 8207 | 941 | 4731 | 279 | 5010 | 0.3315 [0.3181, 0.3447] | 0.8122 [0.7994, 0.8247] | **0.4708** [0.4564, 0.4848] | 0.0565 [0.0354, 0.0771] |
| 75 | 4080 | 8196 | 930 | 4731 | 279 | 5010 | 0.3324 [0.3191, 0.3455] | 0.8144 [0.8017, 0.8268] | **0.4721** [0.4577, 0.4861] | 0.0565 [0.0354, 0.0771] |
| 100 | 4092 | 8184 | 918 | 4731 | 279 | 5010 | 0.3333 [0.3201, 0.3465] | 0.8168 [0.8043, 0.8291] | **0.4734** [0.4590, 0.4875] | 0.0565 [0.0354, 0.0771] |
| 125 | 4096 | 8180 | 914 | 4731 | 279 | 5010 | 0.3337 [0.3204, 0.3469] | 0.8176 [0.8052, 0.8299] | **0.4739** [0.4594, 0.4880] | 0.0565 [0.0354, 0.0771] |
| 150 | 4105 | 8171 | 905 | 4731 | 279 | 5010 | 0.3344 [0.3212, 0.3476] | 0.8194 [0.8070, 0.8316] | **0.4750** [0.4605, 0.4890] | 0.0565 [0.0354, 0.0771] |

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
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-min-n10-uplift__verified-5of10-standardised-gt/twin-5of10.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
