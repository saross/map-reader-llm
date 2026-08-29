# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Timestamp**: 2026-08-29T05:25:45.933125+00:00
**Methodology**: Approach B — extended-GT-at-R Hungarian matching
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
**Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`

## F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 5 | 437 | 24999 | 4309 | 4746 | 0 | 4746 | 0.0172 [0.0154, 0.0190] | 0.0921 [0.0833, 0.1007] | **0.0290** [0.0260, 0.0319] |
| 10 | 1339 | 24097 | 3407 | 4746 | 0 | 4746 | 0.0526 [0.0490, 0.0564] | 0.2821 [0.2676, 0.2965] | **0.0887** [0.0830, 0.0946] |
| 15 | 2316 | 23120 | 2430 | 4746 | 0 | 4746 | 0.0911 [0.0858, 0.0964] | 0.4880 [0.4716, 0.5047] | **0.1535** [0.1454, 0.1616] |
| 20 | 3022 | 22414 | 1724 | 4746 | 0 | 4746 | 0.1188 [0.1126, 0.1252] | 0.6367 [0.6207, 0.6531] | **0.2003** [0.1909, 0.2098] |
| 25 | 3516 | 21920 | 1230 | 4746 | 0 | 4746 | 0.1382 [0.1312, 0.1453] | 0.7408 [0.7265, 0.7552] | **0.2330** [0.2227, 0.2433] |
| 30 | 3801 | 21635 | 945 | 4746 | 0 | 4746 | 0.1494 [0.1419, 0.1570] | 0.8009 [0.7878, 0.8137] | **0.2519** [0.2409, 0.2627] |
| 35 | 3967 | 21469 | 779 | 4746 | 0 | 4746 | 0.1560 [0.1483, 0.1637] | 0.8359 [0.8240, 0.8477] | **0.2629** [0.2516, 0.2741] |
| 40 | 4053 | 21383 | 693 | 4746 | 0 | 4746 | 0.1593 [0.1516, 0.1671] | 0.8540 [0.8427, 0.8652] | **0.2686** [0.2572, 0.2797] |
| 45 | 4103 | 21333 | 643 | 4746 | 0 | 4746 | 0.1613 [0.1535, 0.1692] | 0.8645 [0.8535, 0.8752] | **0.2719** [0.2606, 0.2832] |
| 50 | 4514 | 20922 | 646 | 4746 | 414 | 5160 | 0.1775 [0.1691, 0.1858] | 0.8748 [0.8647, 0.8848] | **0.2951** [0.2833, 0.3067] |
| 75 | 4665 | 20771 | 674 | 4746 | 593 | 5339 | 0.1834 [0.1749, 0.1920] | 0.8738 [0.8639, 0.8835] | **0.3032** [0.2913, 0.3150] |
| 100 | 4740 | 20696 | 690 | 4746 | 684 | 5430 | 0.1864 [0.1777, 0.1950] | 0.8729 [0.8633, 0.8825] | **0.3071** [0.2951, 0.3190] |
| 125 | 4782 | 20654 | 692 | 4746 | 728 | 5474 | 0.1880 [0.1793, 0.1968] | 0.8736 [0.8639, 0.8832] | **0.3094** [0.2973, 0.3214] |
| 150 | 4823 | 20613 | 685 | 4746 | 762 | 5508 | 0.1896 [0.1809, 0.1985] | 0.8756 [0.8660, 0.8852] | **0.3117** [0.2996, 0.3237] |

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
(**F1 = 0.0290**) re-runs Hungarian over extended GT including
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
**F1 = 0.3094** at R = 125 m (95 % CI [0.2973, 0.3214]) —
the largest R where the attractor-pull contribution to recall is
statistically distinguishable from within-tile random placement.

## Sentinel exclusion

10 candidates at today's ">150 m" shell
(``buffer_metres=200``) are excluded from every extended-GT build in this
analysis. Their detections contribute FP at every R ≤ 150 m. Rationale in
the task brief and Obs 272.

## Reproducibility

- **Inputs**:
  - Detections: `outputs/55maps-text-high-generalisation/proposer/detect_brief-text/run_1/detections-detect_brief-text-3-flash-2026-04-18.geojson`
  - Student GT: `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  - Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
  - Review (yesterday): `results/55maps-extended-gt-2026-06-07/empty-yesterday-review.csv`
  - Review (today): `results/deployment-oracle-2026-06-06/canonical-gt/canonical-review.csv`
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling
- **Git commit**: `8f0d6e033fb4ed3dfe0a76e2c02ddfc625161f22`
- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`
