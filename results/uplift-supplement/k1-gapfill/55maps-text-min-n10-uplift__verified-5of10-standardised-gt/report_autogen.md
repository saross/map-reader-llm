# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-29T07:40:59.814741+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `1fca9caad90d1f2719cc75e1bda7c442e7cb75e5`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 652 | 13808 | 4358 | 4731 | 279 | 5010 | 0.0451 [0.0412, 0.0492] | 0.1301 [0.1198, 0.1406] | **0.0670** [0.0614, 0.0727] | 0.0610 [0.0427, 0.0772] |
| 10 | 1734 | 12726 | 3276 | 4731 | 279 | 5010 | 0.1199 [0.1128, 0.1273] | 0.3461 [0.3307, 0.3613] | **0.1781** [0.1685, 0.1877] | 0.0610 [0.0427, 0.0772] |
| 15 | 2585 | 11875 | 2425 | 4731 | 279 | 5010 | 0.1788 [0.1695, 0.1881] | 0.5160 [0.4994, 0.5328] | **0.2655** [0.2537, 0.2773] | 0.0610 [0.0427, 0.0772] |
| 20 | 3186 | 11274 | 1824 | 4731 | 279 | 5010 | 0.2203 [0.2099, 0.2309] | 0.6359 [0.6198, 0.6522] | **0.3273** [0.3144, 0.3402] | 0.0610 [0.0427, 0.0772] |
| 25 | 3592 | 10868 | 1418 | 4731 | 279 | 5010 | 0.2484 [0.2372, 0.2596] | 0.7170 [0.7019, 0.7321] | **0.3690** [0.3556, 0.3823] | 0.0610 [0.0427, 0.0772] |
| 30 | 3807 | 10653 | 1203 | 4731 | 279 | 5010 | 0.2633 [0.2517, 0.2748] | 0.7599 [0.7459, 0.7741] | **0.3911** [0.3772, 0.4048] | 0.0610 [0.0427, 0.0772] |
| 35 | 3910 | 10550 | 1100 | 4731 | 279 | 5010 | 0.2704 [0.2586, 0.2822] | 0.7804 [0.7670, 0.7939] | **0.4016** [0.3878, 0.4154] | 0.0610 [0.0427, 0.0772] |
| 40 | 3967 | 10493 | 1043 | 4731 | 279 | 5010 | 0.2743 [0.2624, 0.2862] | 0.7918 [0.7787, 0.8049] | **0.4075** [0.3936, 0.4213] | 0.0610 [0.0427, 0.0772] |
| 45 | 3997 | 10463 | 1013 | 4731 | 279 | 5010 | 0.2764 [0.2645, 0.2884] | 0.7978 [0.7849, 0.8107] | **0.4106** [0.3966, 0.4243] | 0.0610 [0.0427, 0.0772] |
| 50 | 4018 | 10442 | 992 | 4731 | 279 | 5010 | 0.2779 [0.2658, 0.2898] | 0.8020 [0.7893, 0.8146] | **0.4127** [0.3987, 0.4265] | 0.0610 [0.0427, 0.0772] |
| 75 | 4049 | 10411 | 961 | 4731 | 279 | 5010 | 0.2800 [0.2680, 0.2919] | 0.8082 [0.7956, 0.8208] | **0.4159** [0.4018, 0.4298] | 0.0610 [0.0427, 0.0772] |
| 100 | 4064 | 10396 | 946 | 4731 | 279 | 5010 | 0.2811 [0.2689, 0.2930] | 0.8112 [0.7986, 0.8238] | **0.4175** [0.4033, 0.4314] | 0.0610 [0.0427, 0.0772] |
| 125 | 4070 | 10390 | 940 | 4731 | 279 | 5010 | 0.2815 [0.2694, 0.2935] | 0.8124 [0.7998, 0.8249] | **0.4181** [0.4039, 0.4320] | 0.0610 [0.0427, 0.0772] |
| 150 | 4082 | 10378 | 928 | 4731 | 279 | 5010 | 0.2823 [0.2702, 0.2944] | 0.8148 [0.8022, 0.8272] | **0.4193** [0.4051, 0.4331] | 0.0610 [0.0427, 0.0772] |

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
  - Detections: `outputs/55maps-text-min-n10-uplift/proposer/run_6/detections-detect_brief-text-3-flash-2026-06-11.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `1fca9caad90d1f2719cc75e1bda7c442e7cb75e5`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
