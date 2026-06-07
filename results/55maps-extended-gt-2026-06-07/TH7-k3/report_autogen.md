# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-06-07T06:21:56.646258+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 401 | 4385 | 4345 | 4746 | 0 | 4746 | 0.0838 [0.0754, 0.0922] | 0.0845 [0.0761, 0.0930] | **0.0841** [0.0759, 0.0925] |
| 10 | 1313 | 3473 | 3433 | 4746 | 0 | 4746 | 0.2743 [0.2603, 0.2884] | 0.2767 [0.2624, 0.2912] | **0.2755** [0.2618, 0.2893] |
| 15 | 2290 | 2496 | 2456 | 4746 | 0 | 4746 | 0.4785 [0.4626, 0.4943] | 0.4825 [0.4663, 0.4986] | **0.4805** [0.4654, 0.4956] |
| 20 | 3006 | 1780 | 1740 | 4746 | 0 | 4746 | 0.6281 [0.6124, 0.6438] | 0.6334 [0.6174, 0.6488] | **0.6307** [0.6164, 0.6449] |
| 25 | 3427 | 1359 | 1319 | 4746 | 0 | 4746 | 0.7160 [0.7016, 0.7300] | 0.7221 [0.7077, 0.7364] | **0.7191** [0.7067, 0.7312] |
| 30 | 3666 | 1120 | 1080 | 4746 | 0 | 4746 | 0.7660 [0.7521, 0.7796] | 0.7724 [0.7589, 0.7856] | **0.7692** [0.7579, 0.7803] |
| 35 | 3782 | 1004 | 964 | 4746 | 0 | 4746 | 0.7902 [0.7769, 0.8033] | 0.7969 [0.7840, 0.8096] | **0.7935** [0.7831, 0.8040] |
| 40 | 3832 | 954 | 914 | 4746 | 0 | 4746 | 0.8007 [0.7878, 0.8136] | 0.8074 [0.7945, 0.8199] | **0.8040** [0.7939, 0.8143] |
| 45 | 3856 | 930 | 890 | 4746 | 0 | 4746 | 0.8057 [0.7927, 0.8184] | 0.8125 [0.7999, 0.8248] | **0.8091** [0.7989, 0.8191] |
| 50 | 4190 | 596 | 971 | 4746 | 415 | 5161 | 0.8755 [0.8652, 0.8856] | 0.8119 [0.7999, 0.8236] | **0.8425** [0.8335, 0.8512] |
| 75 | 4231 | 555 | 1109 | 4746 | 594 | 5340 | 0.8840 [0.8741, 0.8940] | 0.7923 [0.7800, 0.8045] | **0.8357** [0.8266, 0.8445] |
| 100 | 4263 | 523 | 1168 | 4746 | 685 | 5431 | 0.8907 [0.8809, 0.9004] | 0.7849 [0.7725, 0.7971] | **0.8345** [0.8254, 0.8433] |
| 125 | 4280 | 506 | 1195 | 4746 | 729 | 5475 | 0.8943 [0.8846, 0.9039] | 0.7817 [0.7692, 0.7941] | **0.8342** [0.8250, 0.8430] |
| 150 | 4293 | 493 | 1216 | 4746 | 763 | 5509 | 0.8970 [0.8874, 0.9065] | 0.7793 [0.7667, 0.7916] | **0.8340** [0.8248, 0.8427] |

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
(**F1 = 0.0841**) re-runs Hungarian over extended GT including
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
**F1 = 0.8342** at R = 125 m (95 % CI [0.8250, 0.8430]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-high-generalisation/k3_verified.geojson`
  - Student GT: `/home/shawn/Code/map-reader-llm/inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `/home/shawn/Code/map-reader-llm/results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
