# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-09-10T23:52:33.654078+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 689 | 11701 | 4321 | 4731 | 279 | 5010 | 0.0556 [0.0509, 0.0603] | 0.1375 [0.1271, 0.1477] | **0.0792** [0.0727, 0.0855] | 0.0503 [0.0290, 0.0707] |
| 10 | 1759 | 10631 | 3251 | 4731 | 279 | 5010 | 0.1420 [0.1337, 0.1503] | 0.3511 [0.3359, 0.3663] | **0.2022** [0.1917, 0.2126] | 0.0503 [0.0290, 0.0707] |
| 15 | 2676 | 9714 | 2334 | 4731 | 279 | 5010 | 0.2160 [0.2055, 0.2265] | 0.5341 [0.5179, 0.5504] | **0.3076** [0.2951, 0.3200] | 0.0503 [0.0290, 0.0707] |
| 20 | 3286 | 9104 | 1724 | 4731 | 279 | 5010 | 0.2652 [0.2533, 0.2771] | 0.6559 [0.6403, 0.6717] | **0.3777** [0.3643, 0.3913] | 0.0503 [0.0290, 0.0707] |
| 25 | 3630 | 8760 | 1380 | 4731 | 279 | 5010 | 0.2930 [0.2805, 0.3055] | 0.7246 [0.7100, 0.7392] | **0.4172** [0.4032, 0.4310] | 0.0503 [0.0290, 0.0707] |
| 30 | 3805 | 8585 | 1205 | 4731 | 279 | 5010 | 0.3071 [0.2944, 0.3200] | 0.7595 [0.7456, 0.7735] | **0.4374** [0.4231, 0.4515] | 0.0503 [0.0290, 0.0707] |
| 35 | 3905 | 8485 | 1105 | 4731 | 279 | 5010 | 0.3152 [0.3022, 0.3283] | 0.7794 [0.7661, 0.7930] | **0.4489** [0.4345, 0.4630] | 0.0503 [0.0290, 0.0707] |
| 40 | 3945 | 8445 | 1065 | 4731 | 279 | 5010 | 0.3184 [0.3053, 0.3316] | 0.7874 [0.7743, 0.8007] | **0.4534** [0.4391, 0.4677] | 0.0503 [0.0290, 0.0707] |
| 45 | 3965 | 8425 | 1045 | 4731 | 279 | 5010 | 0.3200 [0.3068, 0.3331] | 0.7914 [0.7784, 0.8046] | **0.4557** [0.4414, 0.4698] | 0.0503 [0.0290, 0.0707] |
| 50 | 3976 | 8414 | 1034 | 4731 | 279 | 5010 | 0.3209 [0.3076, 0.3340] | 0.7936 [0.7806, 0.8068] | **0.4570** [0.4427, 0.4711] | 0.0503 [0.0290, 0.0707] |
| 75 | 3989 | 8401 | 1021 | 4731 | 279 | 5010 | 0.3220 [0.3088, 0.3351] | 0.7962 [0.7831, 0.8092] | **0.4585** [0.4443, 0.4727] | 0.0503 [0.0290, 0.0707] |
| 100 | 4003 | 8387 | 1007 | 4731 | 279 | 5010 | 0.3231 [0.3099, 0.3363] | 0.7990 [0.7859, 0.8118] | **0.4601** [0.4459, 0.4743] | 0.0503 [0.0290, 0.0707] |
| 125 | 4009 | 8381 | 1001 | 4731 | 279 | 5010 | 0.3236 [0.3104, 0.3368] | 0.8002 [0.7871, 0.8132] | **0.4608** [0.4465, 0.4750] | 0.0503 [0.0290, 0.0707] |
| 150 | 4020 | 8370 | 990 | 4731 | 279 | 5010 | 0.3245 [0.3113, 0.3377] | 0.8024 [0.7895, 0.8153] | **0.4621** [0.4477, 0.4762] | 0.0503 [0.0290, 0.0707] |

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
  - Detections: `results/uplift-supplement/verifier-pairing/55maps-text-min-generalisation__verified-k3-standardised-gt/twin-3of5.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `7973ffd2ead92bfdd1326e2bb497265e1b655e18`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
