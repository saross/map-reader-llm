# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-06-07T06:21:47.783720+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 403 | 3947 | 4343 | 4746 | 0 | 4746 | 0.0926 [0.0839, 0.1017] | 0.0849 [0.0769, 0.0932] | **0.0886** [0.0803, 0.0971] |
| 10 | 1290 | 3060 | 3456 | 4746 | 0 | 4746 | 0.2966 [0.2820, 0.3113] | 0.2718 [0.2580, 0.2857] | **0.2836** [0.2699, 0.2973] |
| 15 | 2160 | 2190 | 2586 | 4746 | 0 | 4746 | 0.4966 [0.4802, 0.5136] | 0.4551 [0.4394, 0.4710] | **0.4749** [0.4598, 0.4905] |
| 20 | 2869 | 1481 | 1877 | 4746 | 0 | 4746 | 0.6595 [0.6439, 0.6757] | 0.6045 [0.5887, 0.6205] | **0.6308** [0.6166, 0.6454] |
| 25 | 3270 | 1080 | 1476 | 4746 | 0 | 4746 | 0.7517 [0.7374, 0.7660] | 0.6890 [0.6743, 0.7036] | **0.7190** [0.7065, 0.7313] |
| 30 | 3476 | 874 | 1270 | 4746 | 0 | 4746 | 0.7991 [0.7856, 0.8124] | 0.7324 [0.7182, 0.7464] | **0.7643** [0.7528, 0.7754] |
| 35 | 3579 | 771 | 1167 | 4746 | 0 | 4746 | 0.8228 [0.8098, 0.8354] | 0.7541 [0.7402, 0.7677] | **0.7869** [0.7761, 0.7974] |
| 40 | 3622 | 728 | 1124 | 4746 | 0 | 4746 | 0.8326 [0.8201, 0.8452] | 0.7632 [0.7493, 0.7765] | **0.7964** [0.7858, 0.8065] |
| 45 | 3652 | 698 | 1094 | 4746 | 0 | 4746 | 0.8395 [0.8271, 0.8519] | 0.7695 [0.7557, 0.7828] | **0.8030** [0.7927, 0.8129] |
| 50 | 3975 | 375 | 1186 | 4746 | 415 | 5161 | 0.9138 [0.9045, 0.9225] | 0.7702 [0.7570, 0.7831] | **0.8359** [0.8265, 0.8447] |
| 75 | 3993 | 357 | 1347 | 4746 | 594 | 5340 | 0.9179 [0.9089, 0.9266] | 0.7478 [0.7343, 0.7609] | **0.8241** [0.8145, 0.8333] |
| 100 | 4006 | 344 | 1425 | 4746 | 685 | 5431 | 0.9209 [0.9120, 0.9295] | 0.7376 [0.7239, 0.7513] | **0.8191** [0.8093, 0.8285] |
| 125 | 4016 | 334 | 1459 | 4746 | 729 | 5475 | 0.9232 [0.9143, 0.9317] | 0.7335 [0.7196, 0.7473] | **0.8175** [0.8075, 0.8270] |
| 150 | 4023 | 327 | 1486 | 4746 | 763 | 5509 | 0.9248 [0.9160, 0.9331] | 0.7303 [0.7164, 0.7440] | **0.8161** [0.8063, 0.8256] |

## How to read this table

- **TP / FP / FN**: Hungarian-matching counts against the extended GT at R.
  Every reviewer-promoted phantom within R is added to the GT before matching.
- **n_ref_student**: Student GT points scoped to the evaluation tile bounds
  (the denominator without any human-review correction).
- **n_promoted@R**: Number of reviewer-promoted phantoms included in the
  extended GT at this R. Yesterday's 472 mound labels appear at every R ≥ 50.
  Today's shell-stratified mound labels accumulate as R rises: +2 @50 m,
  +121 @75 m, +47 @100 m, +19 @125 m, +11 @150 m.
- **n_ref_extended**: Scoped extended-GT count at R (student GT scoped ∪
  in-scope phantoms at R). This is the recall denominator.
- **F1 [95 % CI]**: Corrected F1 at R with tile-level bootstrap CI.

## Comparison to yesterday's 50 m result

Yesterday's single-buffer correction (``compute_corrected_f1_human_reviewed.py``)
produced **F1 = 0.8295** at R = 50 m via an analytic adjustment to measured
counts (moved 472 FPs into TP and added them to the GT denominator, without
re-running Hungarian). This script's R = 5 m row
(**F1 = 0.0886**) re-runs Hungarian over extended GT including
the 2 today-corrections at 50 m. Expected ΔF1 ≈ +0.003 versus yesterday's
number. The two numbers are methodologically close but not identical —
Approach B allows detections to rematch optimally against the extended GT,
which can free a detection previously bound to a distant student-GT point
to pair with a closer phantom.

## Obs 272 caveat — the 150 m row is an upper bound

Obs 272 in ``docs/notes/reflections/working-notes.md`` shows the
attractor-pull effect (reviewer confirmations concentrating closer to the
detection than a uniform within-tile null would predict) is statistically
significant only through 125 m. At the (125, 150] shell the shell-specific
mound-confirmation rate is indistinguishable from the within-tile random-
placement null, and the (150, 286] shell ("200 m" sentinel in today's CSV)
is completely indistinguishable.

**Implication for interpretation:**

- **R ≤ 125 m**: corrected F1 / P / R are practitioner-meaningful. The
  reviewer-promoted phantoms in these shells are confirming detections
  genuinely spatially associated with visible mound symbols.
- **R = 150 m**: corrected F1 at 150 m is an **upper bound on achievable
  practitioner recall**, not a practitioner-useful operating point.
  Including the 11 mounds in the (125, 150] shell inflates recall in a way
  the attractor-pull null cannot distinguish from coincidental alignment.
- **R > 150 m (excluded from this analysis)**: the 74 candidates at the
  ">150 m" sentinel (``buffer_metres=200``) are visible mounds inside the
  286 m corners-plus-5 px review circle but outside every review ring.
  They are **not** added as phantoms at any R in this analysis; their
  detections appear as FP at every R ≤ 150 m, which is the correct
  behaviour under the 150 m practitioner cap.


## Practitioner-useful cap: F1 at R = 125 m

Recommended single-number summary for downstream quotation:
**F1 = 0.8175** at R = 125 m (95 % CI [0.8075, 0.8270]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `/home/shawn/Code/map-reader-llm/outputs/55maps-text-high-t0.3-generalisation/verified/verified_detections.geojson`
  - Student GT: `/home/shawn/Code/map-reader-llm/inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `/home/shawn/Code/map-reader-llm/results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
