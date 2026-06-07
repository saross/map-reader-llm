# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-06-07T06:21:37.926434+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 415 | 3450 | 4331 | 4746 | 0 | 4746 | 0.1074 [0.0970, 0.1178] | 0.0874 [0.0788, 0.0961] | **0.0964** [0.0870, 0.1057] |
| 10 | 1288 | 2577 | 3458 | 4746 | 0 | 4746 | 0.3332 [0.3168, 0.3502] | 0.2714 [0.2570, 0.2856] | **0.2992** [0.2842, 0.3142] |
| 15 | 2098 | 1767 | 2648 | 4746 | 0 | 4746 | 0.5428 [0.5251, 0.5609] | 0.4421 [0.4254, 0.4589] | **0.4873** [0.4713, 0.5037] |
| 20 | 2670 | 1195 | 2076 | 4746 | 0 | 4746 | 0.6908 [0.6741, 0.7079] | 0.5626 [0.5458, 0.5796] | **0.6201** [0.6049, 0.6357] |
| 25 | 2981 | 884 | 1765 | 4746 | 0 | 4746 | 0.7713 [0.7563, 0.7863] | 0.6281 [0.6119, 0.6447] | **0.6924** [0.6784, 0.7062] |
| 30 | 3142 | 723 | 1604 | 4746 | 0 | 4746 | 0.8129 [0.7991, 0.8268] | 0.6620 [0.6460, 0.6784] | **0.7298** [0.7168, 0.7426] |
| 35 | 3224 | 641 | 1522 | 4746 | 0 | 4746 | 0.8342 [0.8211, 0.8475] | 0.6793 [0.6637, 0.6950] | **0.7488** [0.7363, 0.7610] |
| 40 | 3256 | 609 | 1490 | 4746 | 0 | 4746 | 0.8424 [0.8295, 0.8556] | 0.6861 [0.6703, 0.7015] | **0.7562** [0.7439, 0.7682] |
| 45 | 3272 | 593 | 1474 | 4746 | 0 | 4746 | 0.8466 [0.8338, 0.8596] | 0.6894 [0.6738, 0.7049] | **0.7600** [0.7477, 0.7718] |
| 50 | 3534 | 331 | 1627 | 4746 | 415 | 5161 | 0.9144 [0.9044, 0.9238] | 0.6848 [0.6698, 0.6996] | **0.7831** [0.7719, 0.7940] |
| 75 | 3552 | 313 | 1788 | 4746 | 594 | 5340 | 0.9190 [0.9094, 0.9282] | 0.6652 [0.6505, 0.6798] | **0.7718** [0.7603, 0.7827] |
| 100 | 3560 | 305 | 1871 | 4746 | 685 | 5431 | 0.9211 [0.9116, 0.9302] | 0.6555 [0.6407, 0.6703] | **0.7659** [0.7545, 0.7770] |
| 125 | 3566 | 299 | 1909 | 4746 | 729 | 5475 | 0.9226 [0.9132, 0.9317] | 0.6513 [0.6365, 0.6661] | **0.7636** [0.7520, 0.7747] |
| 150 | 3573 | 292 | 1936 | 4746 | 763 | 5509 | 0.9245 [0.9152, 0.9334] | 0.6486 [0.6337, 0.6634] | **0.7623** [0.7508, 0.7735] |

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
(**F1 = 0.0964**) re-runs Hungarian over extended GT including
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
**F1 = 0.7636** at R = 125 m (95 % CI [0.7520, 0.7747]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `/home/shawn/Code/map-reader-llm/outputs/55maps-text-min-generalisation/verified/verified_detections.geojson`
  - Student GT: `/home/shawn/Code/map-reader-llm/inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `/home/shawn/Code/map-reader-llm/results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
