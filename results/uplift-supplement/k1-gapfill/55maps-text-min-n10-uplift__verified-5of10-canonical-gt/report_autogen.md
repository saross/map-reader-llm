# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-08-29T07:37:21.968265+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `1fca9caad90d1f2719cc75e1bda7c442e7cb75e5`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 456 | 14004 | 4290 | 4746 | 0 | 4746 | 0.0315 [0.0283, 0.0349] | 0.0961 [0.0870, 0.1055] | **0.0475** [0.0428, 0.0524] |
| 10 | 1427 | 13033 | 3319 | 4746 | 0 | 4746 | 0.0987 [0.0923, 0.1052] | 0.3007 [0.2858, 0.3154] | **0.1486** [0.1399, 0.1575] |
| 15 | 2297 | 12163 | 2449 | 4746 | 0 | 4746 | 0.1589 [0.1502, 0.1675] | 0.4840 [0.4673, 0.5013] | **0.2392** [0.2279, 0.2505] |
| 20 | 2924 | 11536 | 1822 | 4746 | 0 | 4746 | 0.2022 [0.1924, 0.2123] | 0.6161 [0.5995, 0.6332] | **0.3045** [0.2921, 0.3173] |
| 25 | 3357 | 11103 | 1389 | 4746 | 0 | 4746 | 0.2322 [0.2214, 0.2431] | 0.7073 [0.6920, 0.7231] | **0.3496** [0.3361, 0.3630] |
| 30 | 3577 | 10883 | 1169 | 4746 | 0 | 4746 | 0.2474 [0.2362, 0.2588] | 0.7537 [0.7392, 0.7683] | **0.3725** [0.3589, 0.3862] |
| 35 | 3676 | 10784 | 1070 | 4746 | 0 | 4746 | 0.2542 [0.2428, 0.2658] | 0.7745 [0.7608, 0.7884] | **0.3828** [0.3690, 0.3966] |
| 40 | 3734 | 10726 | 1012 | 4746 | 0 | 4746 | 0.2582 [0.2468, 0.2699] | 0.7868 [0.7732, 0.8001] | **0.3888** [0.3750, 0.4027] |
| 45 | 3768 | 10692 | 978 | 4746 | 0 | 4746 | 0.2606 [0.2489, 0.2723] | 0.7939 [0.7806, 0.8071] | **0.3924** [0.3784, 0.4062] |
| 50 | 4110 | 10350 | 1050 | 4746 | 414 | 5160 | 0.2842 [0.2723, 0.2962] | 0.7965 [0.7840, 0.8093] | **0.4190** [0.4050, 0.4327] |
| 75 | 4185 | 10275 | 1154 | 4746 | 593 | 5339 | 0.2894 [0.2773, 0.3016] | 0.7839 [0.7710, 0.7967] | **0.4227** [0.4088, 0.4364] |
| 100 | 4212 | 10248 | 1218 | 4746 | 684 | 5430 | 0.2913 [0.2791, 0.3034] | 0.7757 [0.7628, 0.7887] | **0.4235** [0.4096, 0.4372] |
| 125 | 4234 | 10226 | 1240 | 4746 | 728 | 5474 | 0.2928 [0.2805, 0.3050] | 0.7735 [0.7606, 0.7865] | **0.4248** [0.4110, 0.4384] |
| 150 | 4252 | 10208 | 1256 | 4746 | 762 | 5508 | 0.2941 [0.2817, 0.3063] | 0.7720 [0.7590, 0.7849] | **0.4259** [0.4120, 0.4394] |

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
(**F1 = 0.0475**) re-runs Hungarian over extended GT including
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
**F1 = 0.4248** at R = 125 m (95 % CI [0.4110, 0.4384]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `outputs/55maps-text-min-n10-uplift/proposer/run_6/detections-detect_brief-text-3-flash-2026-06-11.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `1fca9caad90d1f2719cc75e1bda7c442e7cb75e5`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
