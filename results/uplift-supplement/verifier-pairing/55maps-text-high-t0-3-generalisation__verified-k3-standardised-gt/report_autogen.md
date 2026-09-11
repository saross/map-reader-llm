# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-09-10T23:54:48.632990+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 618 | 13327 | 4392 | 4731 | 279 | 5010 | 0.0443 [0.0405, 0.0482] | 0.1234 [0.1137, 0.1331] | **0.0652** [0.0598, 0.0707] | 0.1979 [0.1785, 0.2167] |
| 10 | 1730 | 12215 | 3280 | 4731 | 279 | 5010 | 0.1241 [0.1171, 0.1310] | 0.3453 [0.3307, 0.3599] | **0.1825** [0.1733, 0.1917] | 0.1979 [0.1785, 0.2167] |
| 15 | 2740 | 11205 | 2270 | 4731 | 279 | 5010 | 0.1965 [0.1874, 0.2057] | 0.5469 [0.5315, 0.5625] | **0.2891** [0.2778, 0.3005] | 0.1979 [0.1785, 0.2167] |
| 20 | 3506 | 10439 | 1504 | 4731 | 279 | 5010 | 0.2514 [0.2409, 0.2621] | 0.6998 [0.6858, 0.7141] | **0.3699** [0.3575, 0.3825] | 0.1979 [0.1785, 0.2167] |
| 25 | 3942 | 10003 | 1068 | 4731 | 279 | 5010 | 0.2827 [0.2714, 0.2941] | 0.7868 [0.7741, 0.7995] | **0.4159** [0.4028, 0.4289] | 0.1979 [0.1785, 0.2167] |
| 30 | 4169 | 9776 | 841 | 4731 | 279 | 5010 | 0.2990 [0.2874, 0.3107] | 0.8321 [0.8205, 0.8435] | **0.4399** [0.4266, 0.4532] | 0.1979 [0.1785, 0.2167] |
| 35 | 4290 | 9655 | 720 | 4731 | 279 | 5010 | 0.3076 [0.2957, 0.3196] | 0.8563 [0.8455, 0.8668] | **0.4527** [0.4391, 0.4661] | 0.1979 [0.1785, 0.2167] |
| 40 | 4349 | 9596 | 661 | 4731 | 279 | 5010 | 0.3119 [0.2999, 0.3239] | 0.8681 [0.8576, 0.8781] | **0.4589** [0.4453, 0.4723] | 0.1979 [0.1785, 0.2167] |
| 45 | 4386 | 9559 | 624 | 4731 | 279 | 5010 | 0.3145 [0.3026, 0.3266] | 0.8754 [0.8652, 0.8854] | **0.4628** [0.4493, 0.4763] | 0.1979 [0.1785, 0.2167] |
| 50 | 4408 | 9537 | 602 | 4731 | 279 | 5010 | 0.3161 [0.3041, 0.3282] | 0.8798 [0.8698, 0.8897] | **0.4651** [0.4515, 0.4786] | 0.1979 [0.1785, 0.2167] |
| 75 | 4437 | 9508 | 573 | 4731 | 279 | 5010 | 0.3182 [0.3062, 0.3304] | 0.8856 [0.8759, 0.8952] | **0.4682** [0.4546, 0.4817] | 0.1979 [0.1785, 0.2167] |
| 100 | 4462 | 9483 | 548 | 4731 | 279 | 5010 | 0.3200 [0.3079, 0.3323] | 0.8906 [0.8809, 0.8999] | **0.4708** [0.4570, 0.4845] | 0.1979 [0.1785, 0.2167] |
| 125 | 4473 | 9472 | 537 | 4731 | 279 | 5010 | 0.3208 [0.3087, 0.3331] | 0.8928 [0.8833, 0.9021] | **0.4720** [0.4581, 0.4856] | 0.1979 [0.1785, 0.2167] |
| 150 | 4482 | 9463 | 528 | 4731 | 279 | 5010 | 0.3214 [0.3093, 0.3337] | 0.8946 [0.8852, 0.9038] | **0.4729** [0.4592, 0.4866] | 0.1979 [0.1785, 0.2167] |

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
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-high-t0-3-generalisation__verified-k3-standardised-gt/twin-3of5.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
