# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-09-10T23:53:08.020574+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 589 | 12983 | 4421 | 4731 | 279 | 5010 | 0.0434 [0.0396, 0.0472] | 0.1176 [0.1078, 0.1271] | **0.0634** [0.0580, 0.0687] | 0.2081 [0.1891, 0.2269] |
| 10 | 1724 | 11848 | 3286 | 4731 | 279 | 5010 | 0.1270 [0.1198, 0.1346] | 0.3441 [0.3291, 0.3590] | **0.1856** [0.1761, 0.1953] | 0.2081 [0.1891, 0.2269] |
| 15 | 2763 | 10809 | 2247 | 4731 | 279 | 5010 | 0.2036 [0.1943, 0.2132] | 0.5515 [0.5359, 0.5670] | **0.2974** [0.2857, 0.3091] | 0.2081 [0.1891, 0.2269] |
| 20 | 3475 | 10097 | 1535 | 4731 | 279 | 5010 | 0.2560 [0.2452, 0.2668] | 0.6936 [0.6788, 0.7079] | **0.3740** [0.3611, 0.3865] | 0.2081 [0.1891, 0.2269] |
| 25 | 3896 | 9676 | 1114 | 4731 | 279 | 5010 | 0.2871 [0.2756, 0.2986] | 0.7776 [0.7647, 0.7903] | **0.4193** [0.4062, 0.4324] | 0.2081 [0.1891, 0.2269] |
| 30 | 4146 | 9426 | 864 | 4731 | 279 | 5010 | 0.3055 [0.2934, 0.3175] | 0.8275 [0.8157, 0.8391] | **0.4462** [0.4326, 0.4597] | 0.2081 [0.1891, 0.2269] |
| 35 | 4266 | 9306 | 744 | 4731 | 279 | 5010 | 0.3143 [0.3021, 0.3266] | 0.8515 [0.8404, 0.8624] | **0.4592** [0.4454, 0.4728] | 0.2081 [0.1891, 0.2269] |
| 40 | 4314 | 9258 | 696 | 4731 | 279 | 5010 | 0.3179 [0.3055, 0.3301] | 0.8611 [0.8502, 0.8718] | **0.4643** [0.4505, 0.4779] | 0.2081 [0.1891, 0.2269] |
| 45 | 4341 | 9231 | 669 | 4731 | 279 | 5010 | 0.3198 [0.3074, 0.3322] | 0.8665 [0.8558, 0.8770] | **0.4672** [0.4534, 0.4808] | 0.2081 [0.1891, 0.2269] |
| 50 | 4356 | 9216 | 654 | 4731 | 279 | 5010 | 0.3210 [0.3085, 0.3333] | 0.8695 [0.8588, 0.8799] | **0.4688** [0.4550, 0.4825] | 0.2081 [0.1891, 0.2269] |
| 75 | 4379 | 9193 | 631 | 4731 | 279 | 5010 | 0.3226 [0.3102, 0.3351] | 0.8741 [0.8636, 0.8842] | **0.4713** [0.4574, 0.4851] | 0.2081 [0.1891, 0.2269] |
| 100 | 4397 | 9175 | 613 | 4731 | 279 | 5010 | 0.3240 [0.3115, 0.3365] | 0.8776 [0.8674, 0.8877] | **0.4733** [0.4593, 0.4869] | 0.2081 [0.1891, 0.2269] |
| 125 | 4409 | 9163 | 601 | 4731 | 279 | 5010 | 0.3249 [0.3123, 0.3374] | 0.8800 [0.8698, 0.8900] | **0.4745** [0.4606, 0.4882] | 0.2081 [0.1891, 0.2269] |
| 150 | 4416 | 9156 | 594 | 4731 | 279 | 5010 | 0.3254 [0.3128, 0.3380] | 0.8814 [0.8713, 0.8914] | **0.4753** [0.4614, 0.4890] | 0.2081 [0.1891, 0.2269] |

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
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-high-generalisation__verified-k3-standardised-gt/twin-3of5.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
