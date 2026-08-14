# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-14T08:41:09.491560+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 543 | 3621 | 4467 | 4731 | 279 | 5010 | 0.1304 [0.1193, 0.1413] | 0.1084 [0.0989, 0.1175] | **0.1184** [0.1082, 0.1283] | 0.6650 [0.6513, 0.6786] |
| 10 | 1534 | 2630 | 3476 | 4731 | 279 | 5010 | 0.3684 [0.3523, 0.3845] | 0.3062 [0.2914, 0.3207] | **0.3344** [0.3196, 0.3492] | 0.6650 [0.6513, 0.6786] |
| 15 | 2436 | 1728 | 2574 | 4731 | 279 | 5010 | 0.5850 [0.5687, 0.6010] | 0.4862 [0.4706, 0.5021] | **0.5311** [0.5162, 0.5461] | 0.6650 [0.6513, 0.6786] |
| 20 | 3054 | 1110 | 1956 | 4731 | 279 | 5010 | 0.7334 [0.7188, 0.7480] | 0.6096 [0.5936, 0.6252] | **0.6658** [0.6518, 0.6794] | 0.6650 [0.6513, 0.6786] |
| 25 | 3400 | 764 | 1610 | 4731 | 279 | 5010 | 0.8165 [0.8040, 0.8290] | 0.6786 [0.6635, 0.6934] | **0.7412** [0.7288, 0.7533] | 0.6650 [0.6513, 0.6786] |
| 30 | 3602 | 562 | 1408 | 4731 | 279 | 5010 | 0.8650 [0.8536, 0.8759] | 0.7190 [0.7041, 0.7334] | **0.7853** [0.7740, 0.7961] | 0.6650 [0.6513, 0.6786] |
| 35 | 3692 | 472 | 1318 | 4731 | 279 | 5010 | 0.8866 [0.8762, 0.8967] | 0.7369 [0.7226, 0.7509] | **0.8049** [0.7944, 0.8152] | 0.6650 [0.6513, 0.6786] |
| 40 | 3724 | 440 | 1286 | 4731 | 279 | 5010 | 0.8943 [0.8843, 0.9042] | 0.7433 [0.7290, 0.7573] | **0.8119** [0.8015, 0.8221] | 0.6650 [0.6513, 0.6786] |
| 45 | 3740 | 424 | 1270 | 4731 | 279 | 5010 | 0.8982 [0.8883, 0.9078] | 0.7465 [0.7323, 0.7604] | **0.8153** [0.8050, 0.8254] | 0.6650 [0.6513, 0.6786] |
| 50 | 3747 | 417 | 1263 | 4731 | 279 | 5010 | 0.8999 [0.8901, 0.9095] | 0.7479 [0.7336, 0.7618] | **0.8169** [0.8066, 0.8268] | 0.6650 [0.6513, 0.6786] |
| 75 | 3755 | 409 | 1255 | 4731 | 279 | 5010 | 0.9018 [0.8921, 0.9113] | 0.7495 [0.7354, 0.7633] | **0.8186** [0.8084, 0.8285] | 0.6650 [0.6513, 0.6786] |
| 100 | 3763 | 401 | 1247 | 4731 | 279 | 5010 | 0.9037 [0.8940, 0.9131] | 0.7511 [0.7369, 0.7650] | **0.8204** [0.8101, 0.8301] | 0.6650 [0.6513, 0.6786] |
| 125 | 3767 | 397 | 1243 | 4731 | 279 | 5010 | 0.9047 [0.8949, 0.9140] | 0.7519 [0.7377, 0.7658] | **0.8212** [0.8110, 0.8310] | 0.6650 [0.6513, 0.6786] |
| 150 | 3770 | 394 | 1240 | 4731 | 279 | 5010 | 0.9054 [0.8957, 0.9147] | 0.7525 [0.7384, 0.7664] | **0.8219** [0.8117, 0.8316] | 0.6650 [0.6513, 0.6786] |

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
  - Detections: `/home/shawn/Code/map-reader-llm/outputs/55maps-text-high-generalisation/verified/verified_detections.geojson`
  - Student GT (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
