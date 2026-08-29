# Corrected F1 / P / R on the 55-map set — standardised reference

**Timestamp**: 2026-08-29T05:46:46.714037+00:00
**Methodology**: Approach B — extended-GT Hungarian matching against the
ruling-21 **standardised reference** (student layer standardised; extension
layer at marked centres, included whole at every R)
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`

## Result table

| R (m) | TP | FP | FN | n_ref_student | n_extension | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] | MCC [95 % CI] |
|------:|---:|---:|---:|--------------:|------------:|---------------:|:-----------:|:-----------:|:------------:|:------------:|
| 5 | 587 | 24849 | 4423 | 4731 | 279 | 5010 | 0.0231 [0.0209, 0.0253] | 0.1172 [0.1074, 0.1267] | **0.0386** [0.0350, 0.0421] | 0.2169 [0.2012, 0.2321] |
| 10 | 1641 | 23795 | 3369 | 4731 | 279 | 5010 | 0.0645 [0.0603, 0.0687] | 0.3275 [0.3129, 0.3420] | **0.1078** [0.1014, 0.1142] | 0.2169 [0.2012, 0.2321] |
| 15 | 2620 | 22816 | 2390 | 4731 | 279 | 5010 | 0.1030 [0.0974, 0.1088] | 0.5230 [0.5069, 0.5392] | **0.1721** [0.1637, 0.1807] | 0.2169 [0.2012, 0.2321] |
| 20 | 3309 | 22127 | 1701 | 4731 | 279 | 5010 | 0.1301 [0.1235, 0.1368] | 0.6605 [0.6452, 0.6757] | **0.2174** [0.2076, 0.2270] | 0.2169 [0.2012, 0.2321] |
| 25 | 3782 | 21654 | 1228 | 4731 | 279 | 5010 | 0.1487 [0.1414, 0.1561] | 0.7549 [0.7414, 0.7684] | **0.2484** [0.2378, 0.2591] | 0.2169 [0.2012, 0.2321] |
| 30 | 4065 | 21371 | 945 | 4731 | 279 | 5010 | 0.1598 [0.1521, 0.1676] | 0.8114 [0.7989, 0.8236] | **0.2670** [0.2559, 0.2782] | 0.2169 [0.2012, 0.2321] |
| 35 | 4232 | 21204 | 778 | 4731 | 279 | 5010 | 0.1664 [0.1584, 0.1743] | 0.8447 [0.8336, 0.8559] | **0.2780** [0.2667, 0.2893] | 0.2169 [0.2012, 0.2321] |
| 40 | 4318 | 21118 | 692 | 4731 | 279 | 5010 | 0.1698 [0.1617, 0.1779] | 0.8619 [0.8513, 0.8725] | **0.2836** [0.2722, 0.2951] | 0.2169 [0.2012, 0.2321] |
| 45 | 4364 | 21072 | 646 | 4731 | 279 | 5010 | 0.1716 [0.1635, 0.1798] | 0.8711 [0.8607, 0.8813] | **0.2867** [0.2752, 0.2982] | 0.2169 [0.2012, 0.2321] |
| 50 | 4398 | 21038 | 612 | 4731 | 279 | 5010 | 0.1729 [0.1648, 0.1811] | 0.8778 [0.8678, 0.8877] | **0.2889** [0.2774, 0.3004] | 0.2169 [0.2012, 0.2321] |
| 75 | 4459 | 20977 | 551 | 4731 | 279 | 5010 | 0.1753 [0.1671, 0.1836] | 0.8900 [0.8805, 0.8994] | **0.2929** [0.2812, 0.3045] | 0.2169 [0.2012, 0.2321] |
| 100 | 4497 | 20939 | 513 | 4731 | 279 | 5010 | 0.1768 [0.1685, 0.1852] | 0.8976 [0.8884, 0.9068] | **0.2954** [0.2836, 0.3072] | 0.2169 [0.2012, 0.2321] |
| 125 | 4519 | 20917 | 491 | 4731 | 279 | 5010 | 0.1777 [0.1694, 0.1862] | 0.9020 [0.8929, 0.9110] | **0.2969** [0.2850, 0.3087] | 0.2169 [0.2012, 0.2321] |
| 150 | 4534 | 20902 | 476 | 4731 | 279 | 5010 | 0.1783 [0.1699, 0.1867] | 0.9050 [0.8960, 0.9138] | **0.2978** [0.2860, 0.3097] | 0.2169 [0.2012, 0.2321] |

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
  - Detections: `outputs/55maps-text-high-generalisation/proposer/detect_brief-text/run_1/detections-detect_brief-text-3-flash-2026-04-18.geojson`
  - Student GT (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Extension layer (standardised): `results/deployment-oracle-2026-06-06/canonical-gt/standardised/extension-mounds-standardised.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
  (standardised-extension mode)
