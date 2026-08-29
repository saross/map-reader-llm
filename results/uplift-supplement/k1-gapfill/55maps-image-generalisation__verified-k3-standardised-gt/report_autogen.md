# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-29T05:04:27.066982+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 352 | 19278 | 4658 | 4731 | 279 | 5010 | 0.0179 [0.0160, 0.0200] | 0.0703 [0.0630, 0.0778] | **0.0286** [0.0255, 0.0318] | 0.3649 [0.3491, 0.3799] |
| 10 | 1115 | 18515 | 3895 | 4731 | 279 | 5010 | 0.0568 [0.0530, 0.0609] | 0.2226 [0.2103, 0.2349] | **0.0905** [0.0848, 0.0965] | 0.3649 [0.3491, 0.3799] |
| 15 | 1959 | 17671 | 3051 | 4731 | 279 | 5010 | 0.0998 [0.0942, 0.1056] | 0.3910 [0.3759, 0.4062] | **0.1590** [0.1510, 0.1672] | 0.3649 [0.3491, 0.3799] |
| 20 | 2702 | 16928 | 2308 | 4731 | 279 | 5010 | 0.1376 [0.1306, 0.1450] | 0.5393 [0.5237, 0.5554] | **0.2193** [0.2095, 0.2294] | 0.3649 [0.3491, 0.3799] |
| 25 | 3284 | 16346 | 1726 | 4731 | 279 | 5010 | 0.1673 [0.1592, 0.1755] | 0.6555 [0.6406, 0.6701] | **0.2666** [0.2557, 0.2775] | 0.3649 [0.3491, 0.3799] |
| 30 | 3663 | 15967 | 1347 | 4731 | 279 | 5010 | 0.1866 [0.1778, 0.1955] | 0.7311 [0.7173, 0.7449] | **0.2973** [0.2855, 0.3090] | 0.3649 [0.3491, 0.3799] |
| 35 | 3935 | 15695 | 1075 | 4731 | 279 | 5010 | 0.2005 [0.1912, 0.2098] | 0.7854 [0.7728, 0.7980] | **0.3194** [0.3072, 0.3316] | 0.3649 [0.3491, 0.3799] |
| 40 | 4116 | 15514 | 894 | 4731 | 279 | 5010 | 0.2097 [0.2002, 0.2194] | 0.8216 [0.8095, 0.8333] | **0.3341** [0.3215, 0.3467] | 0.3649 [0.3491, 0.3799] |
| 45 | 4244 | 15386 | 766 | 4731 | 279 | 5010 | 0.2162 [0.2066, 0.2261] | 0.8471 [0.8359, 0.8581] | **0.3445** [0.3317, 0.3573] | 0.3649 [0.3491, 0.3799] |
| 50 | 4327 | 15303 | 683 | 4731 | 279 | 5010 | 0.2204 [0.2108, 0.2304] | 0.8637 [0.8529, 0.8741] | **0.3512** [0.3385, 0.3640] | 0.3649 [0.3491, 0.3799] |
| 75 | 4515 | 15115 | 495 | 4731 | 279 | 5010 | 0.2300 [0.2200, 0.2404] | 0.9012 [0.8923, 0.9101] | **0.3665** [0.3534, 0.3798] | 0.3649 [0.3491, 0.3799] |
| 100 | 4571 | 15059 | 439 | 4731 | 279 | 5010 | 0.2329 [0.2228, 0.2433] | 0.9124 [0.9038, 0.9209] | **0.3710** [0.3579, 0.3844] | 0.3649 [0.3491, 0.3799] |
| 125 | 4599 | 15031 | 411 | 4731 | 279 | 5010 | 0.2343 [0.2242, 0.2447] | 0.9180 [0.9098, 0.9260] | **0.3733** [0.3601, 0.3867] | 0.3649 [0.3491, 0.3799] |
| 150 | 4623 | 15007 | 387 | 4731 | 279 | 5010 | 0.2355 [0.2253, 0.2460] | 0.9228 [0.9149, 0.9304] | **0.3752** [0.3620, 0.3886] | 0.3649 [0.3491, 0.3799] |

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
  - Detections: `outputs/55maps-image-generalisation/proposer/library_plus-hp/run_1/detections-library_plus-hp-3-flash-2026-04-18.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
