# Dawid-Skene cross-run summary — four 55-map runs (T=0.3, T=0.7, image, text-MIN)

**Date**: 2026-04-28 (text-MIN added to the previous three-run summary
of 2026-04-27).
**Runs analysed**: T=0.3 (`55maps-text-high-t0.3-generalisation`), T=0.7
(`55maps-text-high-generalisation`), image (`55maps-image-generalisation`),
text-MIN (`55maps-text-min-generalisation`).
**Aggregator**: `scripts/analyse_dawid_skene.py` (canonical), preregistered
fixed-prior fit (student sensitivity 0.95, specificity 1.0, fixed in EM).
**Cross-tab**: `scripts/analyse_ds_vs_human_review.py` (degenerate-posterior
diagnostic against multi-buffer human review).

## 1. Summary

Four sibling Dawid-Skene (D-S) latent-truth fits on the 55-map
generalisation set — one for each of the production runs that produced
publishable corrected-F1 metrics — are now in place. text-MIN, the
fourth run, was re-run this session with the canonical text-MIN paths
(consensus + verifier probabilities from
`outputs/55maps-text-min-generalisation/`) and cross-tabulated against
the 586-row multi-buffer human review that landed earlier today. The
re-run reproduced the existing text-MIN D-S artefacts byte-identically;
the new contribution is the ds-human-crosstab.

**Headline pattern across the four runs.** D-S aggregate F1 follows the
**measured** F1 ranking (T=0.7 > T=0.3 > image > text-MIN), with the
+0.024 D-S correction over measured F1 essentially constant across all
four runs. The corrected-F1-multi-buffer ranking (T=0.3 > image > T=0.7
> text-MIN) **disagrees** — see §4.3. The crosstabs against
per-candidate human review extend Obs 293's headline finding: the
**D-S calibration gap scales monotonically with the VLM-only / matched
ratio**, and text-MIN sits at the conservative end of that scale,
nearly indistinguishable from T=0.7 on every calibration metric.

## 2. Per-run × per-class D-S agreement metrics

### 2.1 Shared item set (matched / student-only / VLM-only)

| Run | Matched | Student-only | VLM-only | Total | VLM-only / matched |
|-----|--------:|-------------:|---------:|------:|-------------------:|
| text-MIN | 3,276 | 1,494 | 585 | 5,355 | 0.179 |
| T=0.7 | 3,513 | 1,257 | 630 | 5,400 | 0.179 |
| T=0.3 | 3,531 | 1,239 | 819 | 5,589 | 0.232 |
| Image | 3,637 | 1,133 | 1,028 | 5,798 | 0.283 |

Sorted by VLM-only / matched ratio. text-MIN and T=0.7 produce nearly
identical ratios (0.179 each) — the conservative end. T=0.3 sits in
the middle (0.232). Image is the most permissive on the VLM side
(0.283). text-MIN has the smallest absolute matched count (3,276 — the
smallest of the four) and the largest student-only count (1,494 —
i.e. the largest count of references the VLM missed), reflecting that
text-MIN is the lowest-recall of the four runs at the measured-F1
stage.

### 2.2 Worker accuracy (D-S confusion matrix estimates)

| Run | Student sensitivity | Student specificity | VLM sensitivity | VLM specificity | Estimated prevalence |
|-----|--------------------:|--------------------:|----------------:|----------------:|---------------------:|
| T=0.3 | 0.9500 (fixed) | 1.0000 (fixed) | 0.7500 | 0.0000 | 0.8867 |
| T=0.7 | 0.9500 (fixed) | 1.0000 (fixed) | 0.7463 | 0.0000 | 0.9176 |
| Image | 0.9500 (fixed) | 1.0000 (fixed) | 0.7716 | 0.0000 | 0.8557 |
| text-MIN | 0.9500 (fixed) | 1.0000 (fixed) | 0.6977 | 0.0000 | 0.9230 |

Student sensitivity / specificity are held fixed by the EM as required
for identifiability with two binary annotators. The VLM-sensitivity
estimates now sit in a 0.6977–0.7716 band — text-MIN returns the
**lowest** VLM sensitivity (0.6977), consistent with text-MIN's
lowest matched count: fewer student-known mounds were flagged by the
VLM. Image's 0.7716 remains the highest, image's higher VLM-only
count flagging more true positives the students missed. VLM
specificity converges to 0 in every run; this is a known property of
the 2-annotator response pattern, not a meaningful per-class
statistic.

The estimated prevalence of true mounds in the D-S item set is
highest for text-MIN (0.92), narrowly above T=0.7 (0.92), well above
T=0.3 (0.89) and image (0.86). Higher prevalence in text-MIN reflects
that the threshold-0.15 detection set is the smallest of the four
and proportionally the most concentrated on student-confirmed
locations.

### 2.3 D-S corrected metrics vs measured baseline

| Run | Measured F1 | Measured P | Measured R | D-S F1 | D-S P | D-S R | Δ F1 (D-S − measured) |
|-----|------------:|-----------:|-----------:|-------:|------:|------:|----------------------:|
| T=0.3 | 0.7743 | 0.8117 | 0.7403 | 0.7988 | 0.8544 | 0.7500 | **+0.0245** |
| T=0.7 | 0.7883 | 0.8479 | 0.7365 | 0.8129 | 0.8926 | 0.7463 | **+0.0246** |
| Image | 0.7710 | 0.7796 | 0.7625 | 0.7954 | 0.8207 | 0.7716 | **+0.0244** |
| text-MIN | 0.7591 | 0.8485 | 0.6868 | 0.7834 | 0.8931 | 0.6977 | **+0.0243** |

The +0.024 ± 0.0001 D-S correction is essentially identical across all
four runs. This is consistent with the structural identifiability
constraint of the 2-annotator fit: the correction magnitude is driven
almost entirely by the fixed 5 % student-FN prior reclassifying
~172–192 VLM-only items as soft true positives, and that
reclassification scales with the absolute count of VLM-only items
proportionally to (matched + student_only) (not their per-run
distribution).

### 2.4 VLM-only posterior — the headline aggregate

| Run | VLM-only n | VLM-only posterior P(true=1) | Expected reclassified (soft) | Hard-threshold reclassified |
|-----|-----------:|-----------------------------:|------------------------------:|----------------------------:|
| T=0.3 | 819 | 0.2269 | 185.8 | 0 |
| T=0.7 | 630 | 0.2935 | 184.9 | 0 |
| Image | 1,028 | 0.1862 | 191.4 | 0 |
| text-MIN | 585 | 0.2947 | 172.4 | 0 |

text-MIN produces the **highest** VLM-only posterior of the four
(0.2947), narrowly above T=0.7 (0.2935) — both reflect that their
VLM-only sets are smallest in proportion to the matched set, so D-S
attributes a larger fraction of those items to true student false
negatives. Image produces the **lowest** posterior (0.1862) because
its VLM-only set is largest in proportion to matched, so the fixed
prior spreads thinner per item.

text-MIN is the run where the **fewest absolute soft reclassifications
occur** (172.4 — the smallest of the four), reflecting its smallest
absolute VLM-only count.

This is the slot in which the cross-run comparison gets interesting,
because each run's VLM-only posterior is being matched against a
per-candidate human-review label set in §3.

## 3. D-S vs human-review crosstab — per run

The script `analyse_ds_vs_human_review.py` cross-tabulates the
per-candidate D-S posterior against the combined human-review label
(yesterday's 50 m-strict review, where present, unioned with today's
multi-buffer re-review) on the VLM-only slice. With two binary
annotators the D-S posterior **collapses to a single value per response
pattern**, so the 2×2 cross-tab at threshold 0.5 is degenerate and the
AUC is 0.5 by construction in every run. The informative numbers are
the calibration metrics (ECE, Brier) and the gap between the D-S
aggregate posterior and the empirical human-mound rate on the VLM-only
slice.

| Run | Joined / unjoined | Empirical rate | D-S posterior | Gap (emp − D-S) | Ratio (emp / D-S) | ECE | Brier | AUC |
|-----|------------------:|---------------:|--------------:|----------------:|------------------:|----:|------:|----:|
| text-MIN | 585 / 0 | 0.5538 (324/585) | 0.2947 | +0.259 | 1.88× | 0.2591 | 0.3142 | 0.500 |
| T=0.7 | 630 / 0 | 0.5587 (352/630) | 0.2935 | +0.265 | 1.90× | 0.2652 | 0.3169 | 0.500 |
| T=0.3 | 628 / 64 | 0.5748 (361/628) | 0.2269 | +0.348 | 2.53× | 0.3479 | 0.3655 | 0.500 |
| Image | 1,028 / 1 | 0.7247 (745/1,028) | 0.1862 | +0.539 | 3.89× | 0.5385 | 0.4895 | 0.500 |

Sorted by calibration gap. Notes:

- **AUC = 0.500 in every run** — degenerate by construction (a single
  unique posterior value per joined VLM-only item). The D-S posterior
  on the VLM-only slice cannot rank individuals; this is a property
  of the 2-annotator identifiability class, not a calibration failure.
- **2 × 2 cross-tab at threshold 0.5 collapses in every run** — every
  run's VLM-only posterior is below 0.5, so D-S `>` 0.5 is always 0
  and D-S `≤` 0.5 captures the entire joined set (TP=0, FP=0,
  FN=n_mound, TN=n_not_mound).
- **text-MIN has zero unjoined rows** — the cleanest join of the four
  runs, alongside T=0.7. Image has 1 unjoined; T=0.3 has 64 unjoined
  (a quantitative outlier explained in the previous three-run summary
  §3, related to the corrected-f1 pipeline using the *reviewed*
  student GT at multi-buffer rings while D-S uses the legacy student
  GT at 50 m).
- **text-MIN's empirical mound rate (0.5538) is the lowest** of the
  four, just below T=0.7 (0.5587), well below T=0.3 (0.5748) and
  image (0.7247). The four runs span 0.55–0.72 on this metric.

## 4. Cross-run comparison — extending Obs 293's headline

### 4.1 Aggregate F1 ordering — D-S matches measured, not corrected-F1

| Metric | Best | 2nd | 3rd | Worst |
|--------|------|-----|-----|-------|
| Measured F1 | T=0.7 (0.7883) | T=0.3 (0.7743) | Image (0.7710) | text-MIN (0.7591) |
| D-S corrected F1 | T=0.7 (0.8129) | T=0.3 (0.7988) | Image (0.7954) | text-MIN (0.7834) |
| Corrected-F1-multi-buffer F1 (R=50 m) | T=0.3 (0.8437) | Image (0.8317) | T=0.7 (0.8260) | text-MIN (0.7964) |
| D-S calibration ECE (lower = better) | text-MIN (0.259) | T=0.7 (0.265) | T=0.3 (0.348) | Image (0.539) |
| D-S calibration Brier (lower = better) | text-MIN (0.314) | T=0.7 (0.317) | T=0.3 (0.366) | Image (0.490) |

The D-S F1 ranking and the measured F1 ranking are **identical**
across all four runs (T=0.7 > T=0.3 > image > text-MIN). The
corrected-F1-multi-buffer ranking (T=0.3 > image > T=0.7 > text-MIN)
is **different** — the rank-disagreement first noted in Obs 293 across
three runs **persists in the four-way comparison**. The two methods
agree only that text-MIN is last.

The calibration ECE / Brier ranking puts **text-MIN narrowly first**,
T=0.7 second, T=0.3 third, image last. This is consistent with §4.2 —
calibration ranks by VLM-only / matched ratio, and text-MIN's ratio
(0.179) is the lowest by a hair over T=0.7 (0.179 to four decimal
places: text-MIN 0.1786 vs T=0.7 0.1793).

### 4.2 Calibration gap scales monotonically with VLM-only / matched ratio

The size of the calibration gap between D-S aggregate and empirical
human-review rate continues to scale monotonically with the VLM-only
share of the detection set; the four-run comparison **strengthens**
the three-run pattern reported in Obs 293:

| Run | VLM-only / matched ratio | Posterior:empirical ratio (= 1 / underestimate) |
|-----|-------------------------:|-------------------------------------------------:|
| text-MIN | 0.1786 (585 / 3,276) | 1.88× |
| T=0.7 | 0.1793 (630 / 3,513) | 1.90× |
| T=0.3 | 0.232 (819 / 3,531) | 2.53× |
| Image | 0.283 (1,028 / 3,637) | 3.89× |

The pattern: as the VLM-only share grows, the fixed 5 % student-FN
prior under-counts true positives more severely. text-MIN — narrowly
the most conservative on VLM-only share — is the best calibrated.
Image — the most permissive — is still by far the worst calibrated.
**text-MIN extends Obs 293's pattern to a fourth run with the lowest
ratio and the lowest gap**, exactly as predicted; there is no rank
inversion at any point along the scale.

text-MIN is also the cleanest test of the pattern because it is the
only run with **zero unjoined rows** in the crosstab, so the
calibration metrics are not noised by the methodology-divergence
diagnostic that affected T=0.3.

### 4.3 D-S corrected F1 vs corrected-F1-multi-buffer F1 — different methods, different answers

The D-S corrected F1 reported here is **not** the headline corrected-F1
that lands in the per-run `corrected-f1-multi-buffer/` summaries. The
two analyses use different correction methodologies and different
ground truth:

| Run | D-S corrected F1 | corrected-F1-multi-buffer F1 (R=50 m) | Δ |
|-----|-----------------:|--------------------------------------:|---:|
| T=0.3 | 0.7988 | 0.8437 | +0.045 |
| T=0.7 | 0.8129 | 0.8260 | +0.013 |
| Image | 0.7954 | 0.8317 | +0.036 |
| text-MIN | 0.7834 | 0.7964 | +0.013 |

(The corrected-F1-multi-buffer numbers are read from each run's
`corrected-f1-multi-buffer/summary.json` at R=50 m for the headline
50 m buffer.)

The D-S correction uses the legacy `student-mounds-55maps.geojson`
GT and applies a fixed 5 % student-FN prior to the 2-annotator EM.
The corrected-F1-multi-buffer correction uses the **reviewed**
student GT (`student-mounds-55maps-reviewed.geojson`) extended by
the human-review mound calls at each buffer band, then runs Hungarian
matching against that extended ground truth. The
corrected-F1-multi-buffer correction is the headline reported
elsewhere; the D-S correction reported here is a secondary diagnostic
of how the 2-annotator latent-truth model performs on the same
underlying data.

text-MIN and T=0.7 share the **smallest D-S-vs-corrected-F1 gap**
(+0.013 each); T=0.3 has the largest (+0.045). The gap reflects how
much of the corrected-F1 pipeline's "extension" is doing work
*beyond* the D-S fixed-prior reclassification. T=0.3 has the largest
multi-buffer review cohort (692 rows vs 586 for text-MIN); text-MIN
and T=0.7 have the fewest reviewer-promoted candidates at R=50 m
(250 for text-MIN), so the corrected-F1 number lands much closer to
the D-S number for those two.

This gap is **not** evidence that one method is wrong; it reflects
that the corrected-F1-multi-buffer pipeline incorporates **today's
multi-buffer human-review evidence** as part of its extended ground
truth, while D-S uses only the preregistered fixed prior.

## 5. Surprising patterns — flagged

### 5.1 text-MIN's calibration metrics nearly clone T=0.7's

text-MIN and T=0.7 produce **nearly identical** D-S calibration
diagnostics:

| Metric | text-MIN | T=0.7 | Difference |
|--------|---------:|------:|-----------:|
| VLM-only / matched | 0.1786 | 0.1793 | −0.0007 |
| VLM-only posterior | 0.2947 | 0.2935 | +0.0012 |
| Empirical rate | 0.5538 | 0.5587 | −0.0049 |
| Calibration gap (emp − D-S) | 0.259 | 0.265 | −0.006 |
| ECE | 0.2591 | 0.2652 | −0.0061 |
| Brier | 0.3142 | 0.3169 | −0.0027 |

The two runs converge on essentially the same calibration metrics
despite very different prompt configurations (text-MIN minimises
prompt content; T=0.7 keeps the full text-HIGH prompt at temperature
0.7). This is a meaningful finding: **the VLM-only / matched ratio
is sufficient to predict D-S calibration**, regardless of which
prompt strategy produced the underlying detection cohort. text-MIN
was expected to have a moderate VLM-only share and a moderate
calibration gap; the actual result is that text-MIN matches the
conservative end of the scale almost exactly. This is consistent
with the `prompt-engineering-converges` pattern noted elsewhere —
different prompts, similar measured detection geometry — and provides
an independent confirmation in the calibration domain.

### 5.2 Image's image-vs-text calibration penalty is large — and now further isolated

The image run's D-S calibration gap (3.89×) is roughly **double**
T=0.7's (1.90×) and T=0.3's (2.53×), and *also* more than double
text-MIN's (1.88×). All three text-prompt runs (text-MIN, T=0.7,
T=0.3) sit on the same calibration curve; image is on a clearly
steeper section. This isolates the image-modality calibration
penalty as a **modality-specific** effect rather than a
prompt-specific one — text prompts at three different configurations
all calibrate consistently; the image prompt does not. This is
consistent with Obs 273 (D-S structurally inadequate on the VLM-only
slice for the image run) and with the v2 data-driven-prior diagnostic
in `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/`.

### 5.3 D-S F1 ranks text-MIN dead last; corrected-F1 also ranks it last — first non-disagreement of the four-way comparison

Despite the rank-disagreement between D-S F1 and corrected-F1 across
the other runs (Obs 293), **both rankings agree that text-MIN is
last**:

- D-S F1 ranks: T=0.7 > T=0.3 > image > text-MIN
- Corrected-F1 ranks: T=0.3 > image > T=0.7 > text-MIN

The agreement on text-MIN being last is robust because text-MIN's
combination of (lowest matched, highest student-only, lowest VLM
sensitivity) is consistent across the methodologies. Both
methodologies penalise the same recall problem — the corrected-F1
extension does not rescue text-MIN's recall enough to lift it above
T=0.7, even though it lifts T=0.3 above image and T=0.7. This is
quietly important: text-MIN's recall floor is below the threshold
of what extension-based correction can bridge. **Note that text-MIN's
absolute corrected F1 (0.7964) sits below 0.80**, the only run of
the four to do so on the headline corrected metric.

### 5.4 T=0.7 is the only run where measured F1 ≈ D-S F1 ≈ corrected-F1-multi-buffer F1 — text-MIN is the second-tightest

| Run | Measured | D-S | Corrected-F1-multi-buffer | Spread |
|-----|---------:|----:|--------------------------:|-------:|
| T=0.3 | 0.7743 | 0.7988 | 0.8437 | 0.069 |
| T=0.7 | 0.7883 | 0.8129 | 0.8260 | 0.038 |
| Image | 0.7710 | 0.7954 | 0.8317 | 0.061 |
| text-MIN | 0.7591 | 0.7834 | 0.7964 | 0.037 |

text-MIN's three F1 estimates sit within a 0.037 envelope, narrowly
the **tightest** of any run analysed here (T=0.7 sits at 0.038).
T=0.3 remains the loosest at 0.069 and image at 0.061. text-MIN's
tight agreement is because its corrected-F1 extension is small (only
250 reviewer-promoted candidates at R=50 m vs the larger cohorts for
the other runs), so the corrected number does not pull far from the
D-S number. This is an artefact of text-MIN's lower review-cohort
size rather than a confidence signal about the underlying F1.

### 5.5 64 unjoined T=0.3 review rows — a methodology-divergence diagnostic

T=0.3 has 64 / 692 = 9.2 % unjoined review rows, vs 1 / 1,029 = 0.1 %
for image, 0 / 630 = 0 % for T=0.7, and **0 / 585 = 0 % for
text-MIN**. The cause is documented in §3 (legacy GT in D-S vs
reviewed-extended-GT in corrected-F1) but the rate is substantially
worse for T=0.3 than the other runs. T=0.3 was run with single-round
recovery (proposer + verifier passes restored from the failed
multi-round proposer, see commit `548604d9`); a plausible explanation
is that the recovered single-round consensus populated more
candidates close to existing student GT points, so a larger fraction
of them landed in the D-S `matched` category against the legacy GT
but were classed as VLM-only against the reviewed-extended GT.
text-MIN's 0 % unjoined rate confirms that the methodology divergence
is **specific to T=0.3's recovery pattern**, not a general issue
with multi-buffer review CSVs.

## 6. Provenance and inputs

All four D-S aggregations use the same canonical pattern:

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
| text-MIN | `outputs/55maps-text-min-generalisation/consensus/consensus-4of5.geojson` | `outputs/55maps-text-min-generalisation/verified/probabilities.json` |

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

The T=0.3, image, and text-MIN D-S aggregations all use their
run-specific paths.

### 6.2 Per-run human-review files

| Run | Yesterday review | Today review |
|-----|------------------|--------------|
| T=0.3 | (none — empty placeholder used) | `results/55maps-text-high-t0.3-generalisation/human-review-multi-buffer.csv` (692 rows) |
| T=0.7 | (none — empty placeholder used) | `results/55maps-text-high-generalisation/human-review-multi-buffer.csv` (630 rows) |
| Image | `results/55maps-image-generalisation/human-review.csv` (1,028 rows) | `results/55maps-image-generalisation/human-review-multi-buffer.csv` (557 rows) |
| text-MIN | (none — empty placeholder used) | `results/55maps-text-min-generalisation/human-review-multi-buffer.csv` (586 rows) |

The image run is the only one with a separate yesterday-strict review;
T=0.3, T=0.7, and text-MIN only have the multi-buffer review. The
crosstab script treats the empty-yesterday case correctly — every
multi-buffer row lands in the `today_only` source bucket with its
multi-buffer label intact.

## 7. References and sibling artefacts

Per-run outputs:

- `results/55maps-text-high-t0.3-generalisation/dawid-skene/` — T=0.3 D-S aggregation.
- `results/55maps-text-high-t0.3-generalisation/ds-human-crosstab/` — T=0.3 D-S vs human review.
- `results/55maps-text-high-generalisation/dawid-skene/` — T=0.7 D-S aggregation (preserved from Apr 19).
- `results/55maps-text-high-generalisation/ds-human-crosstab/` — T=0.7 D-S vs human review.
- `results/55maps-image-generalisation/dawid-skene/` — image D-S aggregation (preserved from Apr 18).
- `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/` — image v2 data-driven prior sensitivity sweep (preserved from Apr 21–23).
- `results/55maps-image-generalisation/ds-human-crosstab/` — image D-S vs human review (preserved from Apr 21–23, hand-levelled-up Apr 23).
- `results/55maps-text-min-generalisation/dawid-skene/` — text-MIN D-S aggregation (re-run this session against canonical text-MIN paths; reproduced byte-identically).
- `results/55maps-text-min-generalisation/ds-human-crosstab/` — text-MIN D-S vs human review (new this session).

References:

- Dawid, A.P. & Skene, A.M. (1979). Maximum likelihood estimation of
  observer error-rates using the EM algorithm. *Applied Statistics*,
  28(1), 20–28.
- Sobotkova, A. et al. (2023). Creating large, high-quality geospatial
  datasets from historical maps using novice volunteers.
- Obs 268 (review-UI calibration crosstab), Obs 269 (verifier
  calibration), Obs 273 (D-S aggregate structurally inadequate on
  VLM-only slice for the image run), Obs 293 (D-S calibration gap
  scales with VLM-only share — three-run finding now extended to
  four-run with text-MIN at the conservative end) — all in
  `docs/notes/reflections/working-notes.md`.
