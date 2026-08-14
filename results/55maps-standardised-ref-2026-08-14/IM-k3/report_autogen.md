# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-14T08:41:29.183878+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 326 | 4354 | 4684 | 4731 | 279 | 5010 | 0.0697 [0.0622, 0.0772] | 0.0651 [0.0580, 0.0722] | **0.0673** [0.0601, 0.0746] | 0.7120 [0.6987, 0.7248] |
| 10 | 1104 | 3576 | 3906 | 4731 | 279 | 5010 | 0.2359 [0.2231, 0.2487] | 0.2204 [0.2077, 0.2327] | **0.2279** [0.2155, 0.2402] | 0.7120 [0.6987, 0.7248] |
| 15 | 1950 | 2730 | 3060 | 4731 | 279 | 5010 | 0.4167 [0.4015, 0.4315] | 0.3892 [0.3743, 0.4038] | **0.4025** [0.3881, 0.4163] | 0.7120 [0.6987, 0.7248] |
| 20 | 2646 | 2034 | 2364 | 4731 | 279 | 5010 | 0.5654 [0.5503, 0.5801] | 0.5281 [0.5126, 0.5433] | **0.5461** [0.5318, 0.5598] | 0.7120 [0.6987, 0.7248] |
| 25 | 3166 | 1514 | 1844 | 4731 | 279 | 5010 | 0.6765 [0.6622, 0.6904] | 0.6319 [0.6169, 0.6467] | **0.6535** [0.6400, 0.6663] | 0.7120 [0.6987, 0.7248] |
| 30 | 3478 | 1202 | 1532 | 4731 | 279 | 5010 | 0.7432 [0.7295, 0.7562] | 0.6942 [0.6797, 0.7080] | **0.7179** [0.7052, 0.7295] | 0.7120 [0.6987, 0.7248] |
| 35 | 3666 | 1014 | 1344 | 4731 | 279 | 5010 | 0.7833 [0.7706, 0.7955] | 0.7317 [0.7180, 0.7452] | **0.7567** [0.7453, 0.7674] | 0.7120 [0.6987, 0.7248] |
| 40 | 3777 | 903 | 1233 | 4731 | 279 | 5010 | 0.8071 [0.7948, 0.8188] | 0.7539 [0.7405, 0.7669] | **0.7796** [0.7689, 0.7897] | 0.7120 [0.6987, 0.7248] |
| 45 | 3837 | 843 | 1173 | 4731 | 279 | 5010 | 0.8199 [0.8080, 0.8313] | 0.7659 [0.7527, 0.7790] | **0.7920** [0.7818, 0.8017] | 0.7120 [0.6987, 0.7248] |
| 50 | 3881 | 799 | 1129 | 4731 | 279 | 5010 | 0.8293 [0.8177, 0.8403] | 0.7747 [0.7614, 0.7875] | **0.8010** [0.7911, 0.8105] | 0.7120 [0.6987, 0.7248] |
| 75 | 3956 | 724 | 1054 | 4731 | 279 | 5010 | 0.8453 [0.8341, 0.8559] | 0.7896 [0.7768, 0.8022] | **0.8165** [0.8069, 0.8256] | 0.7120 [0.6987, 0.7248] |
| 100 | 3973 | 707 | 1037 | 4731 | 279 | 5010 | 0.8489 [0.8379, 0.8594] | 0.7930 [0.7802, 0.8055] | **0.8200** [0.8106, 0.8290] | 0.7120 [0.6987, 0.7248] |
| 125 | 3986 | 694 | 1024 | 4731 | 279 | 5010 | 0.8517 [0.8408, 0.8620] | 0.7956 [0.7828, 0.8079] | **0.8227** [0.8133, 0.8316] | 0.7120 [0.6987, 0.7248] |
| 150 | 3992 | 688 | 1018 | 4731 | 279 | 5010 | 0.8530 [0.8421, 0.8633] | 0.7968 [0.7840, 0.8091] | **0.8239** [0.8147, 0.8327] | 0.7120 [0.6987, 0.7248] |

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
  - Detections: `/home/shawn/Code/map-reader-llm/outputs/55maps-image-generalisation/verified/verified_detections.geojson`
  - Student GT (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `6e38c0e5ff808da6475580085d2fcd408e1e57ac`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
