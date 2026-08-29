# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-08-29T06:10:32.298808+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 445 | 21494 | 4301 | 4746 | 0 | 4746 | 0.0203 [0.0183, 0.0224] | 0.0938 [0.0852, 0.1026] | **0.0334** [0.0301, 0.0368] |
| 10 | 1427 | 20512 | 3319 | 4746 | 0 | 4746 | 0.0650 [0.0608, 0.0694] | 0.3007 [0.2858, 0.3151] | **0.1070** [0.1005, 0.1134] |
| 15 | 2354 | 19585 | 2392 | 4746 | 0 | 4746 | 0.1073 [0.1014, 0.1134] | 0.4960 [0.4796, 0.5126] | **0.1764** [0.1678, 0.1853] |
| 20 | 3111 | 18828 | 1635 | 4746 | 0 | 4746 | 0.1418 [0.1347, 0.1492] | 0.6555 [0.6395, 0.6715] | **0.2332** [0.2230, 0.2436] |
| 25 | 3597 | 18342 | 1149 | 4746 | 0 | 4746 | 0.1640 [0.1559, 0.1722] | 0.7579 [0.7437, 0.7720] | **0.2696** [0.2582, 0.2810] |
| 30 | 3872 | 18067 | 874 | 4746 | 0 | 4746 | 0.1765 [0.1681, 0.1850] | 0.8158 [0.8032, 0.8282] | **0.2902** [0.2786, 0.3018] |
| 35 | 4021 | 17918 | 725 | 4746 | 0 | 4746 | 0.1833 [0.1747, 0.1920] | 0.8472 [0.8354, 0.8587] | **0.3014** [0.2895, 0.3134] |
| 40 | 4099 | 17840 | 647 | 4746 | 0 | 4746 | 0.1868 [0.1781, 0.1957] | 0.8637 [0.8525, 0.8746] | **0.3072** [0.2952, 0.3193] |
| 45 | 4159 | 17780 | 587 | 4746 | 0 | 4746 | 0.1896 [0.1808, 0.1985] | 0.8763 [0.8656, 0.8868] | **0.3117** [0.2995, 0.3239] |
| 50 | 4570 | 17369 | 590 | 4746 | 414 | 5160 | 0.2083 [0.1990, 0.2176] | 0.8857 [0.8756, 0.8953] | **0.3373** [0.3248, 0.3497] |
| 75 | 4721 | 17218 | 618 | 4746 | 593 | 5339 | 0.2152 [0.2056, 0.2248] | 0.8842 [0.8747, 0.8935] | **0.3461** [0.3335, 0.3588] |
| 100 | 4788 | 17151 | 642 | 4746 | 684 | 5430 | 0.2182 [0.2086, 0.2280] | 0.8818 [0.8722, 0.8910] | **0.3499** [0.3372, 0.3624] |
| 125 | 4833 | 17106 | 641 | 4746 | 728 | 5474 | 0.2203 [0.2106, 0.2300] | 0.8829 [0.8735, 0.8920] | **0.3526** [0.3399, 0.3652] |
| 150 | 4869 | 17070 | 639 | 4746 | 762 | 5508 | 0.2219 [0.2122, 0.2317] | 0.8840 [0.8746, 0.8931] | **0.3548** [0.3421, 0.3673] |

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
(**F1 = 0.0334**) re-runs Hungarian over extended GT including
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
**F1 = 0.3526** at R = 125 m (95 % CI [0.3399, 0.3652]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `outputs/55maps-text-high-t0.3-generalisation/proposer/detect_brief-text/run_1/detections-detect_brief-text-3-flash-2026-04-26.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
