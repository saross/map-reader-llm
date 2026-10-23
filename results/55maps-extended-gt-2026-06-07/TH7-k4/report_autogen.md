# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-10-15T10:46:57.239049+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `98ab69abc5e677480b0fa56b129419779cf063d0`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 381 | 3783 | 4365 | 4746 | 0 | 4746 | 0.0915 [0.0822, 0.1010] | 0.0803 [0.0720, 0.0886] | **0.0855** [0.0769, 0.0943] |
| 10 | 1227 | 2937 | 3519 | 4746 | 0 | 4746 | 0.2947 [0.2792, 0.3102] | 0.2585 [0.2443, 0.2727] | **0.2754** [0.2612, 0.2899] |
| 15 | 2133 | 2031 | 2613 | 4746 | 0 | 4746 | 0.5122 [0.4953, 0.5291] | 0.4494 [0.4334, 0.4656] | **0.4788** [0.4632, 0.4943] |
| 20 | 2789 | 1375 | 1957 | 4746 | 0 | 4746 | 0.6698 [0.6541, 0.6860] | 0.5877 [0.5710, 0.6038] | **0.6260** [0.6113, 0.6408] |
| 25 | 3164 | 1000 | 1582 | 4746 | 0 | 4746 | 0.7598 [0.7456, 0.7742] | 0.6667 [0.6510, 0.6822] | **0.7102** [0.6972, 0.7231] |
| 30 | 3372 | 792 | 1374 | 4746 | 0 | 4746 | 0.8098 [0.7963, 0.8231] | 0.7105 [0.6952, 0.7253] | **0.7569** [0.7449, 0.7687] |
| 35 | 3465 | 699 | 1281 | 4746 | 0 | 4746 | 0.8321 [0.8192, 0.8449] | 0.7301 [0.7153, 0.7446] | **0.7778** [0.7664, 0.7889] |
| 40 | 3505 | 659 | 1241 | 4746 | 0 | 4746 | 0.8417 [0.8291, 0.8543] | 0.7385 [0.7237, 0.7531] | **0.7868** [0.7755, 0.7977] |
| 45 | 3521 | 643 | 1225 | 4746 | 0 | 4746 | 0.8456 [0.8330, 0.8579] | 0.7419 [0.7271, 0.7565] | **0.7903** [0.7794, 0.8012] |
| 50 | 3801 | 363 | 1359 | 4746 | 414 | 5160 | 0.9128 [0.9035, 0.9219] | 0.7366 [0.7225, 0.7504] | **0.8153** [0.8051, 0.8251] |
| 75 | 3823 | 341 | 1516 | 4746 | 593 | 5339 | 0.9181 [0.9090, 0.9269] | 0.7161 [0.7016, 0.7301] | **0.8046** [0.7942, 0.8145] |
| 100 | 3841 | 323 | 1589 | 4746 | 684 | 5430 | 0.9224 [0.9135, 0.9311] | 0.7074 [0.6928, 0.7213] | **0.8007** [0.7903, 0.8107] |
| 125 | 3851 | 313 | 1623 | 4746 | 728 | 5474 | 0.9248 [0.9160, 0.9334] | 0.7035 [0.6888, 0.7177] | **0.7991** [0.7886, 0.8093] |
| 150 | 3858 | 306 | 1650 | 4746 | 762 | 5508 | 0.9265 [0.9178, 0.9349] | 0.7004 [0.6857, 0.7145] | **0.7978** [0.7872, 0.8079] |

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
(**F1 = 0.0855**) re-runs Hungarian over extended GT including
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
**F1 = 0.7991** at R = 125 m (95 % CI [0.7886, 0.8093]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `/home/shawn/Code/map-reader-llm/outputs/55maps-text-high-generalisation/verified/verified_detections.geojson`
  - Student GT: `/home/shawn/Code/map-reader-llm/inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `/home/shawn/Code/map-reader-llm/inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `/home/shawn/Code/map-reader-llm/results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `98ab69abc5e677480b0fa56b129419779cf063d0`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
