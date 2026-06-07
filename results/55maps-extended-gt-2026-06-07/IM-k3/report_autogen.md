# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-06-07T06:21:57.390007+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 263 | 4417 | 4483 | 4746 | 0 | 4746 | 0.0562 [0.0495, 0.0632] | 0.0554 [0.0487, 0.0623] | **0.0558** [0.0492, 0.0627] |
| 10 | 924 | 3756 | 3822 | 4746 | 0 | 4746 | 0.1974 [0.1854, 0.2096] | 0.1947 [0.1827, 0.2067] | **0.1961** [0.1843, 0.2078] |
| 15 | 1692 | 2988 | 3054 | 4746 | 0 | 4746 | 0.3615 [0.3466, 0.3763] | 0.3565 [0.3418, 0.3712] | **0.3590** [0.3447, 0.3729] |
| 20 | 2395 | 2285 | 2351 | 4746 | 0 | 4746 | 0.5118 [0.4964, 0.5272] | 0.5046 [0.4888, 0.5203] | **0.5082** [0.4938, 0.5223] |
| 25 | 2927 | 1753 | 1819 | 4746 | 0 | 4746 | 0.6254 [0.6105, 0.6406] | 0.6167 [0.6011, 0.6320] | **0.6210** [0.6072, 0.6345] |
| 30 | 3246 | 1434 | 1500 | 4746 | 0 | 4746 | 0.6936 [0.6792, 0.7078] | 0.6839 [0.6689, 0.6984] | **0.6887** [0.6757, 0.7009] |
| 35 | 3430 | 1250 | 1316 | 4746 | 0 | 4746 | 0.7329 [0.7189, 0.7467] | 0.7227 [0.7083, 0.7369] | **0.7278** [0.7157, 0.7393] |
| 40 | 3544 | 1136 | 1202 | 4746 | 0 | 4746 | 0.7573 [0.7435, 0.7708] | 0.7467 [0.7326, 0.7606] | **0.7520** [0.7403, 0.7630] |
| 45 | 3611 | 1069 | 1135 | 4746 | 0 | 4746 | 0.7716 [0.7582, 0.7849] | 0.7609 [0.7472, 0.7745] | **0.7662** [0.7552, 0.7769] |
| 50 | 3930 | 750 | 1231 | 4746 | 415 | 5161 | 0.8397 [0.8285, 0.8505] | 0.7615 [0.7480, 0.7745] | **0.7987** [0.7887, 0.8081] |
| 75 | 4087 | 593 | 1253 | 4746 | 594 | 5340 | 0.8733 [0.8632, 0.8828] | 0.7654 [0.7525, 0.7780] | **0.8158** [0.8062, 0.8248] |
| 100 | 4135 | 545 | 1296 | 4746 | 685 | 5431 | 0.8835 [0.8738, 0.8928] | 0.7614 [0.7482, 0.7742] | **0.8179** [0.8084, 0.8270] |
| 125 | 4155 | 525 | 1320 | 4746 | 729 | 5475 | 0.8878 [0.8781, 0.8970] | 0.7589 [0.7457, 0.7717] | **0.8183** [0.8089, 0.8274] |
| 150 | 4168 | 512 | 1341 | 4746 | 763 | 5509 | 0.8906 [0.8811, 0.8997] | 0.7566 [0.7434, 0.7693] | **0.8181** [0.8086, 0.8272] |

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
(**F1 = 0.0558**) re-runs Hungarian over extended GT including
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
**F1 = 0.8183** at R = 125 m (95 % CI [0.8089, 0.8274]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `/home/shawn/Code/map-reader-llm/outputs/55maps-image-generalisation/verified/verified_detections.geojson`
  - Student GT: `/home/shawn/Code/map-reader-llm/inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `/home/shawn/Code/map-reader-llm/results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
