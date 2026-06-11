# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-06-11T12:14:35.309935+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `7aa28475b9f525f7059d594dd2f286819dde1c85`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 461 | 3900 | 4285 | 4746 | 0 | 4746 | 0.1057 [0.0961, 0.1153] | 0.0971 [0.0881, 0.1062] | **0.1012** [0.0920, 0.1105] |
| 10 | 1430 | 2931 | 3316 | 4746 | 0 | 4746 | 0.3279 [0.3123, 0.3439] | 0.3013 [0.2867, 0.3161] | **0.3140** [0.2996, 0.3289] |
| 15 | 2295 | 2066 | 2451 | 4746 | 0 | 4746 | 0.5263 [0.5097, 0.5436] | 0.4836 [0.4671, 0.5001] | **0.5040** [0.4887, 0.5199] |
| 20 | 2947 | 1414 | 1799 | 4746 | 0 | 4746 | 0.6758 [0.6597, 0.6920] | 0.6209 [0.6045, 0.6373] | **0.6472** [0.6325, 0.6618] |
| 25 | 3333 | 1028 | 1413 | 4746 | 0 | 4746 | 0.7643 [0.7499, 0.7786] | 0.7023 [0.6867, 0.7177] | **0.7320** [0.7193, 0.7447] |
| 30 | 3502 | 859 | 1244 | 4746 | 0 | 4746 | 0.8030 [0.7894, 0.8165] | 0.7379 [0.7229, 0.7527] | **0.7691** [0.7573, 0.7808] |
| 35 | 3584 | 777 | 1162 | 4746 | 0 | 4746 | 0.8218 [0.8088, 0.8348] | 0.7552 [0.7407, 0.7692] | **0.7871** [0.7761, 0.7981] |
| 40 | 3625 | 736 | 1121 | 4746 | 0 | 4746 | 0.8312 [0.8182, 0.8443] | 0.7638 [0.7496, 0.7778] | **0.7961** [0.7853, 0.8067] |
| 45 | 3642 | 719 | 1104 | 4746 | 0 | 4746 | 0.8351 [0.8223, 0.8480] | 0.7674 [0.7532, 0.7814] | **0.7998** [0.7891, 0.8105] |
| 50 | 3947 | 414 | 1214 | 4746 | 415 | 5161 | 0.9051 [0.8954, 0.9144] | 0.7648 [0.7512, 0.7783] | **0.8290** [0.8190, 0.8385] |
| 75 | 3970 | 391 | 1370 | 4746 | 594 | 5340 | 0.9103 [0.9009, 0.9195] | 0.7434 [0.7297, 0.7570] | **0.8185** [0.8084, 0.8281] |
| 100 | 3982 | 379 | 1449 | 4746 | 685 | 5431 | 0.9131 [0.9038, 0.9222] | 0.7332 [0.7192, 0.7469] | **0.8133** [0.8032, 0.8230] |
| 125 | 3989 | 372 | 1486 | 4746 | 729 | 5475 | 0.9147 [0.9054, 0.9238] | 0.7286 [0.7145, 0.7423] | **0.8111** [0.8008, 0.8209] |
| 150 | 3997 | 364 | 1512 | 4746 | 763 | 5509 | 0.9165 [0.9074, 0.9255] | 0.7255 [0.7115, 0.7393] | **0.8099** [0.7998, 0.8197] |

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
(**F1 = 0.1012**) re-runs Hungarian over extended GT including
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
**F1 = 0.8111** at R = 125 m (95 % CI [0.8008, 0.8209]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `/home/shawn/Code/map-reader-llm/results/55map-leaderboard/min11-uplift-5of10-pt0.15.geojson`
  - Student GT: `/home/shawn/Code/map-reader-llm/inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `/home/shawn/Code/map-reader-llm/results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `7aa28475b9f525f7059d594dd2f286819dde1c85`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
