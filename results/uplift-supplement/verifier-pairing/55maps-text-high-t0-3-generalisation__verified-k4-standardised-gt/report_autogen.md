# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-29T10:37:31.396140+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 591 | 9319 | 4419 | 4731 | 279 | 5010 | 0.0596 [0.0544, 0.0648] | 0.1180 [0.1084, 0.1276] | **0.0792** [0.0727, 0.0858] | 0.2728 [0.2535, 0.2920] |
| 10 | 1644 | 8266 | 3366 | 4731 | 279 | 5010 | 0.1659 [0.1569, 0.1749] | 0.3281 [0.3139, 0.3426] | **0.2204** [0.2096, 0.2309] | 0.2728 [0.2535, 0.2920] |
| 15 | 2593 | 7317 | 2417 | 4731 | 279 | 5010 | 0.2617 [0.2502, 0.2733] | 0.5176 [0.5021, 0.5335] | **0.3476** [0.3349, 0.3604] | 0.2728 [0.2535, 0.2920] |
| 20 | 3304 | 6606 | 1706 | 4731 | 279 | 5010 | 0.3334 [0.3205, 0.3463] | 0.6595 [0.6446, 0.6746] | **0.4429** [0.4293, 0.4562] | 0.2728 [0.2535, 0.2920] |
| 25 | 3705 | 6205 | 1305 | 4731 | 279 | 5010 | 0.3739 [0.3601, 0.3873] | 0.7395 [0.7260, 0.7534] | **0.4966** [0.4827, 0.5102] | 0.2728 [0.2535, 0.2920] |
| 30 | 3908 | 6002 | 1102 | 4731 | 279 | 5010 | 0.3943 [0.3803, 0.4083] | 0.7800 [0.7672, 0.7927] | **0.5239** [0.5100, 0.5374] | 0.2728 [0.2535, 0.2920] |
| 35 | 4005 | 5905 | 1005 | 4731 | 279 | 5010 | 0.4041 [0.3898, 0.4182] | 0.7994 [0.7869, 0.8119] | **0.5369** [0.5230, 0.5505] | 0.2728 [0.2535, 0.2920] |
| 40 | 4053 | 5857 | 957 | 4731 | 279 | 5010 | 0.4090 [0.3946, 0.4231] | 0.8090 [0.7967, 0.8215] | **0.5433** [0.5293, 0.5571] | 0.2728 [0.2535, 0.2920] |
| 45 | 4082 | 5828 | 928 | 4731 | 279 | 5010 | 0.4119 [0.3974, 0.4260] | 0.8148 [0.8024, 0.8269] | **0.5472** [0.5333, 0.5609] | 0.2728 [0.2535, 0.2920] |
| 50 | 4094 | 5816 | 916 | 4731 | 279 | 5010 | 0.4131 [0.3988, 0.4273] | 0.8172 [0.8049, 0.8292] | **0.5488** [0.5349, 0.5625] | 0.2728 [0.2535, 0.2920] |
| 75 | 4106 | 5804 | 904 | 4731 | 279 | 5010 | 0.4143 [0.3999, 0.4286] | 0.8196 [0.8073, 0.8316] | **0.5504** [0.5365, 0.5641] | 0.2728 [0.2535, 0.2920] |
| 100 | 4115 | 5795 | 895 | 4731 | 279 | 5010 | 0.4152 [0.4008, 0.4295] | 0.8214 [0.8093, 0.8334] | **0.5516** [0.5378, 0.5653] | 0.2728 [0.2535, 0.2920] |
| 125 | 4118 | 5792 | 892 | 4731 | 279 | 5010 | 0.4155 [0.4010, 0.4298] | 0.8220 [0.8098, 0.8340] | **0.5520** [0.5381, 0.5657] | 0.2728 [0.2535, 0.2920] |
| 150 | 4124 | 5786 | 886 | 4731 | 279 | 5010 | 0.4161 [0.4017, 0.4305] | 0.8232 [0.8110, 0.8353] | **0.5528** [0.5390, 0.5665] | 0.2728 [0.2535, 0.2920] |

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
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-high-t0-3-generalisation__verified-k4-standardised-gt/twin-4of5.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
