# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-14T08:41:12.934336+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 574 | 3776 | 4436 | 4731 | 279 | 5010 | 0.1320 [0.1215, 0.1426] | 0.1146 [0.1053, 0.1240] | **0.1226** [0.1129, 0.1325] | 0.6690 [0.6550, 0.6822] |
| 10 | 1579 | 2771 | 3431 | 4731 | 279 | 5010 | 0.3630 [0.3479, 0.3780] | 0.3152 [0.3010, 0.3294] | **0.3374** [0.3233, 0.3515] | 0.6690 [0.6550, 0.6822] |
| 15 | 2474 | 1876 | 2536 | 4731 | 279 | 5010 | 0.5687 [0.5527, 0.5848] | 0.4938 [0.4785, 0.5095] | **0.5286** [0.5140, 0.5436] | 0.6690 [0.6550, 0.6822] |
| 20 | 3149 | 1201 | 1861 | 4731 | 279 | 5010 | 0.7239 [0.7096, 0.7382] | 0.6285 [0.6134, 0.6438] | **0.6729** [0.6596, 0.6862] | 0.6690 [0.6550, 0.6822] |
| 25 | 3522 | 828 | 1488 | 4731 | 279 | 5010 | 0.8097 [0.7972, 0.8220] | 0.7030 [0.6887, 0.7172] | **0.7526** [0.7410, 0.7641] | 0.6690 [0.6550, 0.6822] |
| 30 | 3714 | 636 | 1296 | 4731 | 279 | 5010 | 0.8538 [0.8424, 0.8647] | 0.7413 [0.7277, 0.7548] | **0.7936** [0.7830, 0.8038] | 0.6690 [0.6550, 0.6822] |
| 35 | 3807 | 543 | 1203 | 4731 | 279 | 5010 | 0.8752 [0.8647, 0.8855] | 0.7599 [0.7465, 0.7732] | **0.8135** [0.8036, 0.8231] | 0.6690 [0.6550, 0.6822] |
| 40 | 3849 | 501 | 1161 | 4731 | 279 | 5010 | 0.8848 [0.8747, 0.8949] | 0.7683 [0.7550, 0.7815] | **0.8224** [0.8129, 0.8319] | 0.6690 [0.6550, 0.6822] |
| 45 | 3874 | 476 | 1136 | 4731 | 279 | 5010 | 0.8906 [0.8806, 0.9003] | 0.7733 [0.7600, 0.7863] | **0.8278** [0.8184, 0.8369] | 0.6690 [0.6550, 0.6822] |
| 50 | 3886 | 464 | 1124 | 4731 | 279 | 5010 | 0.8933 [0.8836, 0.9029] | 0.7756 [0.7625, 0.7886] | **0.8303** [0.8210, 0.8394] | 0.6690 [0.6550, 0.6822] |
| 75 | 3895 | 455 | 1115 | 4731 | 279 | 5010 | 0.8954 [0.8856, 0.9048] | 0.7774 [0.7642, 0.7903] | **0.8323** [0.8230, 0.8413] | 0.6690 [0.6550, 0.6822] |
| 100 | 3900 | 450 | 1110 | 4731 | 279 | 5010 | 0.8966 [0.8867, 0.9060] | 0.7784 [0.7653, 0.7913] | **0.8333** [0.8241, 0.8423] | 0.6690 [0.6550, 0.6822] |
| 125 | 3903 | 447 | 1107 | 4731 | 279 | 5010 | 0.8972 [0.8875, 0.9066] | 0.7790 [0.7658, 0.7920] | **0.8340** [0.8247, 0.8430] | 0.6690 [0.6550, 0.6822] |
| 150 | 3910 | 440 | 1100 | 4731 | 279 | 5010 | 0.8989 [0.8891, 0.9083] | 0.7804 [0.7673, 0.7934] | **0.8355** [0.8263, 0.8445] | 0.6690 [0.6550, 0.6822] |

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
  - Detections: `/home/shawn/Code/map-reader-llm/outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson`
  - Student GT (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
