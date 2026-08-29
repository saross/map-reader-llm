# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-29T10:24:35.852687+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 558 | 8647 | 4452 | 4731 | 279 | 5010 | 0.0606 [0.0552, 0.0660] | 0.1114 [0.1019, 0.1207] | **0.0785** [0.0717, 0.0852] | 0.2886 [0.2694, 0.3079] |
| 10 | 1605 | 7600 | 3405 | 4731 | 279 | 5010 | 0.1744 [0.1646, 0.1842] | 0.3204 [0.3054, 0.3350] | **0.2258** [0.2145, 0.2372] | 0.2886 [0.2694, 0.3079] |
| 15 | 2559 | 6646 | 2451 | 4731 | 279 | 5010 | 0.2780 [0.2659, 0.2903] | 0.5108 [0.4950, 0.5267] | **0.3600** [0.3470, 0.3732] | 0.2886 [0.2694, 0.3079] |
| 20 | 3214 | 5991 | 1796 | 4731 | 279 | 5010 | 0.3492 [0.3357, 0.3625] | 0.6415 [0.6257, 0.6567] | **0.4522** [0.4383, 0.4658] | 0.2886 [0.2694, 0.3079] |
| 25 | 3588 | 5617 | 1422 | 4731 | 279 | 5010 | 0.3898 [0.3755, 0.4039] | 0.7162 [0.7014, 0.7304] | **0.5048** [0.4908, 0.5187] | 0.2886 [0.2694, 0.3079] |
| 30 | 3802 | 5403 | 1208 | 4731 | 279 | 5010 | 0.4130 [0.3983, 0.4276] | 0.7589 [0.7447, 0.7725] | **0.5349** [0.5206, 0.5488] | 0.2886 [0.2694, 0.3079] |
| 35 | 3895 | 5310 | 1115 | 4731 | 279 | 5010 | 0.4231 [0.4082, 0.4379] | 0.7774 [0.7639, 0.7908] | **0.5480** [0.5337, 0.5619] | 0.2886 [0.2694, 0.3079] |
| 40 | 3930 | 5275 | 1080 | 4731 | 279 | 5010 | 0.4269 [0.4118, 0.4418] | 0.7844 [0.7708, 0.7976] | **0.5529** [0.5387, 0.5669] | 0.2886 [0.2694, 0.3079] |
| 45 | 3950 | 5255 | 1060 | 4731 | 279 | 5010 | 0.4291 [0.4140, 0.4440] | 0.7884 [0.7749, 0.8016] | **0.5558** [0.5416, 0.5696] | 0.2886 [0.2694, 0.3079] |
| 50 | 3963 | 5242 | 1047 | 4731 | 279 | 5010 | 0.4305 [0.4154, 0.4454] | 0.7910 [0.7776, 0.8040] | **0.5576** [0.5434, 0.5714] | 0.2886 [0.2694, 0.3079] |
| 75 | 3976 | 5229 | 1034 | 4731 | 279 | 5010 | 0.4319 [0.4167, 0.4469] | 0.7936 [0.7803, 0.8065] | **0.5594** [0.5451, 0.5733] | 0.2886 [0.2694, 0.3079] |
| 100 | 3986 | 5219 | 1024 | 4731 | 279 | 5010 | 0.4330 [0.4178, 0.4480] | 0.7956 [0.7823, 0.8086] | **0.5608** [0.5465, 0.5747] | 0.2886 [0.2694, 0.3079] |
| 125 | 3991 | 5214 | 1019 | 4731 | 279 | 5010 | 0.4336 [0.4183, 0.4485] | 0.7966 [0.7833, 0.8095] | **0.5615** [0.5471, 0.5753] | 0.2886 [0.2694, 0.3079] |
| 150 | 3996 | 5209 | 1014 | 4731 | 279 | 5010 | 0.4341 [0.4188, 0.4492] | 0.7976 [0.7844, 0.8105] | **0.5622** [0.5477, 0.5760] | 0.2886 [0.2694, 0.3079] |

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
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-high-generalisation__verified-k4-standardised-gt/twin-4of5.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `390c65af31865305f183aa6c22e89805b6ef806b`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
