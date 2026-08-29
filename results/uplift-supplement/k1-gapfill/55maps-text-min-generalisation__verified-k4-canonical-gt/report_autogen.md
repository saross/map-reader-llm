# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-08-29T06:38:07.229141+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 451 | 14163 | 4295 | 4746 | 0 | 4746 | 0.0309 [0.0278, 0.0340] | 0.0950 [0.0863, 0.1038] | **0.0466** [0.0421, 0.0512] |
| 10 | 1407 | 13207 | 3339 | 4746 | 0 | 4746 | 0.0963 [0.0901, 0.1027] | 0.2965 [0.2817, 0.3116] | **0.1454** [0.1368, 0.1542] |
| 15 | 2303 | 12311 | 2443 | 4746 | 0 | 4746 | 0.1576 [0.1494, 0.1661] | 0.4853 [0.4686, 0.5020] | **0.2379** [0.2271, 0.2490] |
| 20 | 2944 | 11670 | 1802 | 4746 | 0 | 4746 | 0.2015 [0.1917, 0.2112] | 0.6203 [0.6039, 0.6365] | **0.3041** [0.2918, 0.3163] |
| 25 | 3336 | 11278 | 1410 | 4746 | 0 | 4746 | 0.2283 [0.2178, 0.2388] | 0.7029 [0.6875, 0.7182] | **0.3446** [0.3315, 0.3575] |
| 30 | 3546 | 11068 | 1200 | 4746 | 0 | 4746 | 0.2426 [0.2319, 0.2536] | 0.7472 [0.7325, 0.7616] | **0.3663** [0.3532, 0.3795] |
| 35 | 3660 | 10954 | 1086 | 4746 | 0 | 4746 | 0.2504 [0.2395, 0.2615] | 0.7712 [0.7569, 0.7851] | **0.3781** [0.3648, 0.3915] |
| 40 | 3707 | 10907 | 1039 | 4746 | 0 | 4746 | 0.2537 [0.2427, 0.2647] | 0.7811 [0.7670, 0.7947] | **0.3830** [0.3697, 0.3964] |
| 45 | 3741 | 10873 | 1005 | 4746 | 0 | 4746 | 0.2560 [0.2450, 0.2671] | 0.7882 [0.7744, 0.8017] | **0.3865** [0.3732, 0.3999] |
| 50 | 4084 | 10530 | 1076 | 4746 | 414 | 5160 | 0.2795 [0.2680, 0.2911] | 0.7915 [0.7786, 0.8043] | **0.4131** [0.3996, 0.4264] |
| 75 | 4151 | 10463 | 1188 | 4746 | 593 | 5339 | 0.2840 [0.2724, 0.2959] | 0.7775 [0.7645, 0.7903] | **0.4161** [0.4026, 0.4293] |
| 100 | 4197 | 10417 | 1233 | 4746 | 684 | 5430 | 0.2872 [0.2754, 0.2992] | 0.7729 [0.7599, 0.7857] | **0.4188** [0.4054, 0.4320] |
| 125 | 4218 | 10396 | 1256 | 4746 | 728 | 5474 | 0.2886 [0.2768, 0.3006] | 0.7706 [0.7576, 0.7834] | **0.4200** [0.4065, 0.4332] |
| 150 | 4238 | 10376 | 1270 | 4746 | 762 | 5508 | 0.2900 [0.2782, 0.3019] | 0.7694 [0.7564, 0.7823] | **0.4212** [0.4078, 0.4345] |

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
(**F1 = 0.0466**) re-runs Hungarian over extended GT including
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
**F1 = 0.4200** at R = 125 m (95 % CI [0.4065, 0.4332]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `outputs/55maps-text-min-generalisation/proposer/detect_brief-text/run_1/detections-detect_brief-text-3-flash-2026-04-18.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
