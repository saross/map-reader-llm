# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-06-07T06:21:57.553836+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 420 | 4485 | 4326 | 4746 | 0 | 4746 | 0.0856 [0.0776, 0.0939] | 0.0885 [0.0803, 0.0970] | **0.0870** [0.0790, 0.0954] |
| 10 | 1347 | 3558 | 3399 | 4746 | 0 | 4746 | 0.2746 [0.2610, 0.2881] | 0.2838 [0.2698, 0.2979] | **0.2791** [0.2657, 0.2925] |
| 15 | 2272 | 2633 | 2474 | 4746 | 0 | 4746 | 0.4632 [0.4480, 0.4790] | 0.4787 [0.4628, 0.4945] | **0.4708** [0.4562, 0.4858] |
| 20 | 3038 | 1867 | 1708 | 4746 | 0 | 4746 | 0.6194 [0.6043, 0.6349] | 0.6401 [0.6249, 0.6556] | **0.6296** [0.6159, 0.6436] |
| 25 | 3466 | 1439 | 1280 | 4746 | 0 | 4746 | 0.7066 [0.6924, 0.7207] | 0.7303 [0.7161, 0.7441] | **0.7183** [0.7059, 0.7303] |
| 30 | 3692 | 1213 | 1054 | 4746 | 0 | 4746 | 0.7527 [0.7392, 0.7661] | 0.7779 [0.7646, 0.7907] | **0.7651** [0.7541, 0.7759] |
| 35 | 3810 | 1095 | 936 | 4746 | 0 | 4746 | 0.7768 [0.7636, 0.7899] | 0.8028 [0.7903, 0.8148] | **0.7896** [0.7793, 0.7997] |
| 40 | 3862 | 1043 | 884 | 4746 | 0 | 4746 | 0.7874 [0.7745, 0.8003] | 0.8137 [0.8016, 0.8256] | **0.8003** [0.7904, 0.8101] |
| 45 | 3899 | 1006 | 847 | 4746 | 0 | 4746 | 0.7949 [0.7821, 0.8078] | 0.8215 [0.8094, 0.8333] | **0.8080** [0.7982, 0.8176] |
| 50 | 4266 | 639 | 895 | 4746 | 415 | 5161 | 0.8697 [0.8593, 0.8798] | 0.8266 [0.8149, 0.8378] | **0.8476** [0.8388, 0.8559] |
| 75 | 4321 | 584 | 1019 | 4746 | 594 | 5340 | 0.8809 [0.8708, 0.8907] | 0.8092 [0.7976, 0.8205] | **0.8435** [0.8349, 0.8518] |
| 100 | 4348 | 557 | 1083 | 4746 | 685 | 5431 | 0.8864 [0.8764, 0.8961] | 0.8006 [0.7888, 0.8119] | **0.8413** [0.8328, 0.8496] |
| 125 | 4366 | 539 | 1109 | 4746 | 729 | 5475 | 0.8901 [0.8803, 0.8997] | 0.7974 [0.7856, 0.8088] | **0.8412** [0.8327, 0.8494] |
| 150 | 4381 | 524 | 1128 | 4746 | 763 | 5509 | 0.8932 [0.8834, 0.9026] | 0.7952 [0.7834, 0.8066] | **0.8414** [0.8328, 0.8495] |

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
(**F1 = 0.0870**) re-runs Hungarian over extended GT including
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
**F1 = 0.8412** at R = 125 m (95 % CI [0.8327, 0.8494]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/k3-scoring/55maps-text-high-t0.3-generalisation/k3_verified.geojson`
  - Student GT: `/home/shawn/Code/map-reader-llm/inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `/home/shawn/Code/map-reader-llm/results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `bb7d5279e818cd52f7b9925e5f19790adf537676`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
