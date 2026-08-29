# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-29T06:53:20.370150+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 652 | 13962 | 4358 | 4731 | 279 | 5010 | 0.0446 [0.0408, 0.0485] | 0.1301 [0.1200, 0.1401] | **0.0664** [0.0610, 0.0720] | 0.0736 [0.0552, 0.0897] |
| 10 | 1713 | 12901 | 3297 | 4731 | 279 | 5010 | 0.1172 [0.1103, 0.1242] | 0.3419 [0.3267, 0.3571] | **0.1746** [0.1652, 0.1840] | 0.0736 [0.0552, 0.0897] |
| 15 | 2588 | 12026 | 2422 | 4731 | 279 | 5010 | 0.1771 [0.1685, 0.1860] | 0.5166 [0.5004, 0.5327] | **0.2638** [0.2527, 0.2752] | 0.0736 [0.0552, 0.0897] |
| 20 | 3202 | 11412 | 1808 | 4731 | 279 | 5010 | 0.2191 [0.2091, 0.2294] | 0.6391 [0.6232, 0.6549] | **0.3263** [0.3140, 0.3387] | 0.0736 [0.0552, 0.0897] |
| 25 | 3582 | 11032 | 1428 | 4731 | 279 | 5010 | 0.2451 [0.2344, 0.2561] | 0.7150 [0.7000, 0.7295] | **0.3651** [0.3520, 0.3783] | 0.0736 [0.0552, 0.0897] |
| 30 | 3781 | 10833 | 1229 | 4731 | 279 | 5010 | 0.2587 [0.2476, 0.2700] | 0.7547 [0.7406, 0.7685] | **0.3853** [0.3721, 0.3987] | 0.0736 [0.0552, 0.0897] |
| 35 | 3897 | 10717 | 1113 | 4731 | 279 | 5010 | 0.2667 [0.2554, 0.2783] | 0.7778 [0.7639, 0.7914] | **0.3972** [0.3837, 0.4106] | 0.0736 [0.0552, 0.0897] |
| 40 | 3944 | 10670 | 1066 | 4731 | 279 | 5010 | 0.2699 [0.2585, 0.2815] | 0.7872 [0.7736, 0.8004] | **0.4020** [0.3886, 0.4155] | 0.0736 [0.0552, 0.0897] |
| 45 | 3976 | 10638 | 1034 | 4731 | 279 | 5010 | 0.2721 [0.2607, 0.2837] | 0.7936 [0.7802, 0.8066] | **0.4052** [0.3918, 0.4188] | 0.0736 [0.0552, 0.0897] |
| 50 | 3996 | 10618 | 1014 | 4731 | 279 | 5010 | 0.2734 [0.2620, 0.2850] | 0.7976 [0.7842, 0.8104] | **0.4073** [0.3938, 0.4208] | 0.0736 [0.0552, 0.0897] |
| 75 | 4016 | 10598 | 994 | 4731 | 279 | 5010 | 0.2748 [0.2633, 0.2864] | 0.8016 [0.7883, 0.8144] | **0.4093** [0.3958, 0.4228] | 0.0736 [0.0552, 0.0897] |
| 100 | 4042 | 10572 | 968 | 4731 | 279 | 5010 | 0.2766 [0.2651, 0.2881] | 0.8068 [0.7937, 0.8193] | **0.4119** [0.3984, 0.4253] | 0.0736 [0.0552, 0.0897] |
| 125 | 4050 | 10564 | 960 | 4731 | 279 | 5010 | 0.2771 [0.2656, 0.2887] | 0.8084 [0.7952, 0.8209] | **0.4128** [0.3991, 0.4261] | 0.0736 [0.0552, 0.0897] |
| 150 | 4062 | 10552 | 948 | 4731 | 279 | 5010 | 0.2780 [0.2664, 0.2896] | 0.8108 [0.7979, 0.8232] | **0.4140** [0.4003, 0.4274] | 0.0736 [0.0552, 0.0897] |

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
  - Detections: `outputs/55maps-text-min-generalisation/proposer/detect_brief-text/run_1/detections-detect_brief-text-3-flash-2026-04-18.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
