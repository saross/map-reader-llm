# Dawid-Skene cross-run summary — three 55-map runs (T=0.3, T=0.7, image)

**Date**: 2026-04-27.
**Runs analysed**: T=0.3 (`55maps-text-high-t0.3-generalisation`), T=0.7
(`55maps-text-high-generalisation`), image (`55maps-image-generalisation`).
**Aggregator**: `scripts/analyse_dawid_skene.py` (canonical), preregistered
fixed-prior fit (student sensitivity 0.95, specificity 1.0, fixed in EM).
**Cross-tab**: `scripts/analyse_ds_vs_human_review.py` (degenerate-posterior
diagnostic against multi-buffer human review).

## 1. Summary

Three sibling Dawid-Skene (D-S) latent-truth fits on the 55-map
generalisation set — one for each of the production runs that produced
publishable corrected-F1 metrics — are now in place. The T=0.3 run, which
landed only this session, had no D-S aggregate and no D-S vs human-review
crosstab; both have been generated. The T=0.7 D-S fit existed but had no
crosstab against its own multi-buffer review; the crosstab has been
generated. The image run already had both artefacts (level-up Apr 23,
Session 76) and is current — no re-run needed.

**Headline pattern across the three runs.** D-S aggregate F1 follows the
same ranking as measured F1 (T=0.7 > T=0.3 > image), with the +0.024 D-S
correction over measured F1 essentially constant across runs. The
crosstabs against per-candidate human review tell a different and more
interesting story: D-S posterior calibration against the empirical mound
rate is **best for T=0.7, intermediate for T=0.3, and worst for image**.
This is a non-trivial cross-run comparison worth recording — see §4.

## 2. Per-run × per-class D-S agreement metrics

### 2.1 Shared item set (matched / student-only / VLM-only)

| Run | Matched | Student-only | VLM-only | Total |
|-----|--------:|-------------:|---------:|------:|
| T=0.3 | 3,531 | 1,239 | 819 | 5,589 |
| T=0.7 | 3,513 | 1,257 | 630 | 5,400 |
| Image | 3,637 | 1,133 | 1,028 | 5,798 |

T=0.3 produces the most matched + VLM-only items (4,350 VLM positives) but
the smallest VLM-only-to-matched ratio (819 / 3,531 = 0.23). Image
produces the most VLM-only items in absolute terms (1,028) and by ratio
(1,028 / 3,637 = 0.28). T=0.7 is the most conservative on the VLM side —
fewer total VLM positives (4,143) and the smallest VLM-only count (630).

### 2.2 Worker accuracy (D-S confusion matrix estimates)

| Run | Student sensitivity | Student specificity | VLM sensitivity | VLM specificity | Estimated prevalence |
|-----|--------------------:|--------------------:|----------------:|----------------:|---------------------:|
| T=0.3 | 0.9500 (fixed) | 1.0000 (fixed) | 0.7500 | 0.0000 | 0.8867 |
| T=0.7 | 0.9500 (fixed) | 1.0000 (fixed) | 0.7463 | 0.0000 | 0.9176 |
| Image | 0.9500 (fixed) | 1.0000 (fixed) | 0.7716 | 0.0000 | 0.8557 |

Student sensitivity / specificity are held fixed by the EM as required for
identifiability with two binary annotators. The VLM-sensitivity estimates
sit in a tight 0.7463–0.7716 band — image returns the highest VLM
sensitivity, consistent with image's higher VLM-only count flagging more
true positives the students missed. VLM specificity converges to 0 in
every run; this is a known property of the 2-annotator response pattern,
not a meaningful per-class statistic.

The estimated prevalence of true mounds in the D-S item set varies
non-trivially: 0.92 (T=0.7), 0.89 (T=0.3), 0.86 (image). Higher
prevalence in T=0.7 reflects that the threshold-0.15 detection set is
smaller and proportionally more concentrated on student-confirmed
locations.

### 2.3 D-S corrected metrics vs measured baseline

| Run | Measured F1 | Measured P | Measured R | D-S F1 | D-S P | D-S R | Δ F1 (D-S − measured) |
|-----|------------:|-----------:|-----------:|-------:|------:|------:|----------------------:|
| T=0.3 | 0.7743 | 0.8117 | 0.7403 | 0.7988 | 0.8544 | 0.7500 | **+0.0245** |
| T=0.7 | 0.7883 | 0.8479 | 0.7365 | 0.8129 | 0.8926 | 0.7463 | **+0.0246** |
| Image | 0.7710 | 0.7796 | 0.7625 | 0.7954 | 0.8207 | 0.7716 | **+0.0244** |

The +0.024 ± 0.0001 D-S correction is essentially identical across runs.
This is consistent with the structural identifiability constraint of the
2-annotator fit: the correction magnitude is driven almost entirely by
the fixed 5 % student-FN prior reclassifying ~185 VLM-only items as soft
true positives, and that reclassification scales with the absolute count
of VLM-only items (not their per-run distribution).

### 2.4 VLM-only posterior — the headline aggregate

| Run | VLM-only n | VLM-only posterior P(true=1) | Expected reclassified (soft) | Hard-threshold reclassified |
|-----|-----------:|-----------------------------:|------------------------------:|----------------------------:|
| T=0.3 | 819 | 0.2269 | 185.8 | 0 |
| T=0.7 | 630 | 0.2935 | 184.9 | 0 |
| Image | 1,028 | 0.1862 | 191.4 | 0 |

T=0.7 produces the **highest** VLM-only posterior (0.294), reflecting that
its VLM-only set is smallest in proportion to the matched set — D-S
attributes a larger fraction of those items to true student false
negatives. Image produces the **lowest** posterior (0.186) because its
VLM-only set is largest in proportion to matched, so the fixed prior
spreads thinner per item.

This is the slot in which the cross-run comparison gets interesting,
because each run's VLM-only posterior is being matched against a
per-candidate human-review label set in §3.

## 3. D-S vs human-review crosstab — per run

The script `analyse_ds_vs_human_review.py` cross-tabulates the
per-candidate D-S posterior against the combined human-review label
(yesterday's 50 m-strict review unioned with today's multi-buffer
re-review) on the VLM-only slice. With two binary annotators the D-S
posterior **collapses to a single value per response pattern**, so the
2×2 cross-tab at threshold 0.5 is degenerate and the AUC is 0.5 by
construction in every run. The informative numbers are the calibration
metrics (ECE, Brier) and the gap between the D-S aggregate posterior and
the empirical human-mound rate on the VLM-only slice.

| Run | Joined / unjoined | Empirical rate | D-S posterior | Gap (emp − D-S) | Ratio (emp / D-S) | ECE | Brier | AUC |
|-----|------------------:|---------------:|--------------:|----------------:|------------------:|----:|------:|----:|
| T=0.3 | 628 / 64 | 0.5748 (361/628) | 0.2269 | +0.348 | 2.53× | 0.3479 | 0.3655 | 0.500 |
| T=0.7 | 630 / 0 | 0.5587 (352/630) | 0.2935 | +0.265 | 1.90× | 0.2652 | 0.3169 | 0.500 |
| Image | 1,028 / 1 | 0.7247 (745/1028) | 0.1862 | +0.539 | 3.89× | 0.5385 | 0.4895 | 0.500 |

Notes:

- **AUC = 0.500 in every run** — degenerate by construction (a single
  unique posterior value per joined VLM-only item). The D-S posterior on
  the VLM-only slice cannot rank individuals; this is a property of the
  2-annotator identifiability class, not a calibration failure.
- **2 × 2 cross-tab at threshold 0.5 collapses in every run** — every
  run's VLM-only posterior is below 0.5, so D-S `>` 0.5 is always 0 and
  D-S `≤` 0.5 captures the entire joined set (TP=0, FP=0, FN=n_mound,
  TN=n_not_mound).
- **64 unjoined T=0.3 review rows**: T=0.3 has the highest unjoined rate.
  Cause: the human review CSV was generated against the corrected-f1
  pipeline (which Hungarian-matches detections to the *reviewed* student
  GT at the multi-buffer extended ring), whereas the D-S pipeline here
  matches against the legacy student GT at 50 m. Items the corrected-f1
  pipeline marks as VLM-only against the extended GT can be classed as
  D-S `matched` against the legacy GT, so they fail to join on
  (map_name, x, y) to a D-S `vlm_only` row. T=0.7 has 0 unjoined and
  image has 1 unjoined — T=0.3's 64 unjoined is a quantitative outlier
  worth recording.

## 4. Cross-run comparison — the interesting pattern

### 4.1 Aggregate F1 ordering preserved; calibration ordering matches

| Metric | Best | Middle | Worst |
|--------|------|--------|-------|
| Measured F1 | T=0.7 (0.7883) | T=0.3 (0.7743) | Image (0.7710) |
| D-S corrected F1 | T=0.7 (0.8129) | T=0.3 (0.7988) | Image (0.7954) |
| D-S calibration ECE (lower = better) | T=0.7 (0.265) | T=0.3 (0.348) | Image (0.539) |
| D-S calibration Brier (lower = better) | T=0.7 (0.317) | T=0.3 (0.366) | Image (0.490) |

The two rankings are **the same**: T=0.7 wins on both aggregate F1 and on
calibration of the D-S aggregate posterior against per-candidate human
review. There is **no rank reversal across the three runs** — T=0.7
dominates on every D-S metric reported here.

### 4.2 The structural pathology is consistent — the magnitude is not

All three runs hit the same structural issue: a single D-S posterior
value per VLM-only item, AUC = 0.5 at the item level, 2 × 2 cross-tab
collapse. But the **size of the calibration gap** between D-S aggregate
and empirical human-review rate scales monotonically with the VLM-only
share of the detection set:

| Run | VLM-only / matched ratio | Posterior:empirical ratio (= 1 / underestimate) |
|-----|-------------------------:|-------------------------------------------------:|
| T=0.7 | 0.179 (630 / 3,513) | 1.90× |
| T=0.3 | 0.232 (819 / 3,531) | 2.53× |
| Image | 0.283 (1,028 / 3,637) | 3.89× |

The pattern: as the VLM-only share grows, the fixed 5 % student-FN prior
under-counts true positives more severely. Image — with the largest
VLM-only fraction — is the most miscalibrated. T=0.7 — with the smallest
VLM-only fraction — is the least miscalibrated. T=0.3 sits between.

### 4.3 D-S corrected F1 vs corrected-F1-multi-buffer F1 — different methods, different answers

The D-S corrected F1 reported here is **not** the headline corrected-F1
that lands in the per-run `corrected-f1-multi-buffer/` summaries. The
two analyses use different correction methodologies and different ground
truth:

| Run | D-S corrected F1 | corrected-F1-multi-buffer F1 (R=50 m) | Δ |
|-----|-----------------:|--------------------------------------:|---:|
| T=0.3 | 0.7988 | 0.8437 | +0.045 |
| T=0.7 | 0.8129 | 0.8260 | +0.013 |
| Image | 0.7954 | 0.8317 | +0.036 |

(The corrected-F1-multi-buffer numbers are read from each run's
`corrected-f1-multi-buffer/summary.json` at R=50 m for the headline 50 m
buffer.)

The D-S correction uses the legacy `student-mounds-55maps.geojson` GT and
applies a fixed 5 % student-FN prior to the 2-annotator EM. The
corrected-F1-multi-buffer correction uses the **reviewed** student GT
(`student-mounds-55maps-reviewed.geojson`) extended by the human-review
mound calls at each buffer band, then runs Hungarian matching against
that extended ground truth. The corrected-F1-multi-buffer correction is
the headline reported elsewhere; the D-S correction reported here is a
secondary diagnostic of how the 2-annotator latent-truth model performs
on the same underlying data.

The two corrections give similar but non-identical answers, with the
D-S correction landing 0.013–0.045 below the corrected-F1-multi-buffer
correction depending on run. This gap is **not** evidence that one method
is wrong; it reflects that the corrected-F1-multi-buffer pipeline
incorporates **today's multi-buffer human-review evidence** as part of
its extended ground truth, while D-S uses only the preregistered fixed
prior.

## 5. Surprising patterns — flagged

### 5.1 Image's image-vs-text calibration penalty is large

The image run's D-S calibration gap (3.89×) is roughly **double** T=0.7's
(1.90×). Both runs use the same student GT and the same D-S fit; the
difference is that image's verifier accepts more candidates at threshold
0.15 (4,665 vs 4,143) and a much higher proportion of those candidates
are not student-known (1,028 vs 630 VLM-only). Image is finding more
true mounds the students missed — and the fixed 5 % student-FN prior
cannot accommodate that. This is consistent with Obs 273 (D-S
structurally inadequate on the VLM-only slice for the image run) and
with the v2 data-driven-prior diagnostic in
`results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/`.

### 5.2 T=0.7 is the only run where measured F1 ≈ D-S F1 ≈ corrected-F1-multi-buffer F1

| Run | Measured | D-S | Corrected-F1-multi-buffer | Spread |
|-----|---------:|----:|--------------------------:|-------:|
| T=0.3 | 0.7743 | 0.7988 | 0.8437 | 0.069 |
| T=0.7 | 0.7883 | 0.8129 | 0.8260 | 0.038 |
| Image | 0.7710 | 0.7954 | 0.8317 | 0.061 |

T=0.7's three F1 estimates sit within a 0.038 envelope; T=0.3's spread
is 0.069 and image's 0.060. T=0.7 has the lowest method-disagreement
about the true F1 of any run analysed here. This is consistent with
T=0.7's lower VLM-only share and lower D-S calibration error.

### 5.3 64 unjoined T=0.3 review rows — a methodology-divergence diagnostic

T=0.3 has 64 / 692 = 9.2 % unjoined review rows, vs 1 / 1,029 = 0.1 % for
image and 0 / 630 = 0 % for T=0.7. The cause is documented in §3 (legacy
GT in D-S vs reviewed-extended-GT in corrected-F1) but the rate is
substantially worse for T=0.3 than the other runs. T=0.3 was run
yesterday with single-round recovery (proposer + verifier passes
restored from the failed multi-round proposer, see commit `548604d9`); a
plausible explanation is that the recovered single-round consensus
populated more candidates close to existing student GT points, so a
larger fraction of them landed in the D-S `matched` category against the
legacy GT but were classed as VLM-only against the reviewed-extended GT.
Worth noting but not blocking — the 628 joined rows are sufficient for
the calibration estimates reported.

## 6. Provenance and inputs

All three D-S aggregations use the same canonical pattern:

- Script: `scripts/analyse_dawid_skene.py`
- Threshold: 0.15
- Buffer: 50 m
- Verifier: v1 (the production verifier, not the v2 family)
- Student-FN prior: 0.05 (Sobotkova et al. 2023, fixed)
- Student GT: `inputs/vectors/references/student-mounds-55maps.geojson`
  (legacy; predates the reviewed GT used by corrected-F1-multi-buffer)
- Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`

Per-run consensus and verifier probabilities:

| Run | Consensus | Probabilities |
|-----|-----------|---------------|
| T=0.3 | `outputs/55maps-text-high-t0.3-generalisation/consensus/consensus-4of5.geojson` | `outputs/55maps-text-high-t0.3-generalisation/verified/probabilities.json` |
| T=0.7 | `outputs/55maps-generalisation/consensus/consensus-4of5.geojson` (legacy default; not the T=0.7-specific consensus — see §6.1) | `outputs/55maps-generalisation/verified/probabilities.json` |
| Image | `outputs/55maps-image-generalisation/consensus/consensus-3of5.geojson` | `outputs/55maps-image-generalisation/verified/probabilities.json` |

### 6.1 Caveat — T=0.7 D-S used legacy consensus paths

The existing T=0.7 D-S sibling (Apr 19) was run with the analyse-script's
**default** legacy consensus (`outputs/55maps-generalisation/...`),
**not** the T=0.7-specific run output
(`outputs/55maps-text-high-generalisation/...`). At threshold 0.15 the
two paths produce 4,068 vs 4,143 VLM positives respectively, and by
coincidence the 630 VLM-only items align exactly across (map_name, x, y)
keys with the T=0.7 human-review CSV (which itself was generated against
the T=0.7-specific corrected-F1 pipeline using
`outputs/55maps-text-high-generalisation/verified/verified_detections.geojson`).

The fact that the keys align across the two consensus paths is a
coincidence — the legacy consensus and the T=0.7 verified detections
share the same threshold-0.15 cut. If the T=0.7 D-S were re-run on
T=0.7-specific paths the matched / vlm-only counts would shift by a
modest amount (~75 additional VLM positives) and the calibration ECE /
Brier would change accordingly. For the cross-run comparison reported
here, the legacy-path T=0.7 D-S is preserved because it was the basis of
the published Apr 19 result; a run on T=0.7-specific paths is
recommended for future work but is not blocking the cross-run comparison.

The T=0.3 and image D-S aggregations both use their run-specific paths.

### 6.2 Per-run human-review files

| Run | Yesterday review | Today review |
|-----|------------------|--------------|
| T=0.3 | (none — empty placeholder used) | `results/55maps-text-high-t0.3-generalisation/human-review-multi-buffer.csv` (692 rows) |
| T=0.7 | (none — empty placeholder used) | `results/55maps-text-high-generalisation/human-review-multi-buffer.csv` (630 rows) |
| Image | `results/55maps-image-generalisation/human-review.csv` (1,028 rows) | `results/55maps-image-generalisation/human-review-multi-buffer.csv` (557 rows) |

The image run is the only one with a separate yesterday-strict review;
T=0.3 and T=0.7 only have the multi-buffer review. The crosstab script
treats the empty-yesterday case correctly — every multi-buffer row lands
in the `today_only` source bucket with its multi-buffer label intact.

## 7. References and sibling artefacts

Per-run outputs:

- `results/55maps-text-high-t0.3-generalisation/dawid-skene/` — T=0.3 D-S aggregation (new this session).
- `results/55maps-text-high-t0.3-generalisation/ds-human-crosstab/` — T=0.3 D-S vs human review (new this session).
- `results/55maps-text-high-generalisation/dawid-skene/` — T=0.7 D-S aggregation (preserved from Apr 19).
- `results/55maps-text-high-generalisation/ds-human-crosstab/` — T=0.7 D-S vs human review (new this session).
- `results/55maps-image-generalisation/dawid-skene/` — image D-S aggregation (preserved from Apr 18).
- `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/` — image v2 data-driven prior sensitivity sweep (preserved from Apr 21–23).
- `results/55maps-image-generalisation/ds-human-crosstab/` — image D-S vs human review (preserved from Apr 21–23, hand-levelled-up Apr 23).

References:

- Dawid, A.P. & Skene, A.M. (1979). Maximum likelihood estimation of
  observer error-rates using the EM algorithm. *Applied Statistics*,
  28(1), 20–28.
- Sobotkova, A. et al. (2023). Creating large, high-quality geospatial
  datasets from historical maps using novice volunteers.
- Obs 268 (review-UI calibration crosstab), Obs 269 (verifier
  calibration), Obs 273 (D-S aggregate structurally inadequate on
  VLM-only slice for the image run) — all in
  `docs/notes/reflections/working-notes.md`.
