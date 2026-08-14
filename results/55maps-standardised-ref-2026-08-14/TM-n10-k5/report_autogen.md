# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-14T08:41:36.348505+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 689 | 3672 | 4321 | 4731 | 279 | 5010 | 0.1580 [0.1463, 0.1694] | 0.1375 [0.1270, 0.1480] | **0.1470** [0.1360, 0.1579] | 0.6709 [0.6573, 0.6844] |
| 10 | 1755 | 2606 | 3255 | 4731 | 279 | 5010 | 0.4024 [0.3866, 0.4185] | 0.3503 [0.3350, 0.3654] | **0.3746** [0.3596, 0.3897] | 0.6709 [0.6573, 0.6844] |
| 15 | 2626 | 1735 | 2384 | 4731 | 279 | 5010 | 0.6022 [0.5860, 0.6181] | 0.5242 [0.5081, 0.5399] | **0.5605** [0.5453, 0.5754] | 0.6709 [0.6573, 0.6844] |
| 20 | 3223 | 1138 | 1787 | 4731 | 279 | 5010 | 0.7391 [0.7244, 0.7534] | 0.6433 [0.6273, 0.6591] | **0.6879** [0.6738, 0.7016] | 0.6709 [0.6573, 0.6844] |
| 25 | 3578 | 783 | 1432 | 4731 | 279 | 5010 | 0.8205 [0.8078, 0.8327] | 0.7142 [0.6991, 0.7290] | **0.7636** [0.7512, 0.7755] | 0.6709 [0.6573, 0.6844] |
| 30 | 3744 | 617 | 1266 | 4731 | 279 | 5010 | 0.8585 [0.8469, 0.8697] | 0.7473 [0.7328, 0.7615] | **0.7991** [0.7877, 0.8099] | 0.6709 [0.6573, 0.6844] |
| 35 | 3822 | 539 | 1188 | 4731 | 279 | 5010 | 0.8764 [0.8658, 0.8868] | 0.7629 [0.7489, 0.7764] | **0.8157** [0.8052, 0.8257] | 0.6709 [0.6573, 0.6844] |
| 40 | 3856 | 505 | 1154 | 4731 | 279 | 5010 | 0.8842 [0.8737, 0.8943] | 0.7697 [0.7560, 0.7829] | **0.8230** [0.8129, 0.8326] | 0.6709 [0.6573, 0.6844] |
| 45 | 3871 | 490 | 1139 | 4731 | 279 | 5010 | 0.8876 [0.8773, 0.8977] | 0.7727 [0.7590, 0.7859] | **0.8262** [0.8163, 0.8358] | 0.6709 [0.6573, 0.6844] |
| 50 | 3879 | 482 | 1131 | 4731 | 279 | 5010 | 0.8895 [0.8792, 0.8994] | 0.7743 [0.7607, 0.7875] | **0.8279** [0.8181, 0.8374] | 0.6709 [0.6573, 0.6844] |
| 75 | 3885 | 476 | 1125 | 4731 | 279 | 5010 | 0.8909 [0.8807, 0.9007] | 0.7754 [0.7619, 0.7887] | **0.8292** [0.8194, 0.8387] | 0.6709 [0.6573, 0.6844] |
| 100 | 3889 | 472 | 1121 | 4731 | 279 | 5010 | 0.8918 [0.8816, 0.9016] | 0.7762 [0.7627, 0.7894] | **0.8300** [0.8204, 0.8394] | 0.6709 [0.6573, 0.6844] |
| 125 | 3891 | 470 | 1119 | 4731 | 279 | 5010 | 0.8922 [0.8821, 0.9020] | 0.7766 [0.7632, 0.7898] | **0.8304** [0.8208, 0.8398] | 0.6709 [0.6573, 0.6844] |
| 150 | 3897 | 464 | 1113 | 4731 | 279 | 5010 | 0.8936 [0.8835, 0.9033] | 0.7778 [0.7643, 0.7911] | **0.8317** [0.8221, 0.8411] | 0.6709 [0.6573, 0.6844] |

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
  - Detections: `/home/shawn/Code/map-reader-llm/results/55map-leaderboard/min11-uplift-5of10-pt0.15.geojson`
  - Student GT (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
