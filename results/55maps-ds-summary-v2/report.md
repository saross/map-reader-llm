# Dawid-Skene cross-run summary — four 55-map runs (T=0.3, T=0.7, image, text-MIN)

> **Last revised**: 2026-08-15 (post-queue refresh — the
> corrected-F1-multi-buffer figures in §§ 4.1, 4.3, 5.3 and 5.4 moved
> onto the standardised reference now that queue items 2–5 are
> complete; the Obs 293 middle-pair disagreement dissolves and all
> three estimators agree on the full four-run ordering).
> See [§ Changelog](#changelog) for revision history.

**Date**: 2026-04-28 (text-MIN added to the previous three-run summary
of 2026-04-27).
**Post-recovery refresh**: 2026-05-03 (cross-track-v2 commit `42ed1d32`).
T=0.7 row re-derived against the recovered single-round consensus + verifier
(commits `366f9c66`, `e07dae37`, `f533fda5`). Image row re-derived against the +1 phantom-promoted cand 2397
review (item counts 3,637 / 1,133 / 1,028 → 3,650 / 1,095 / 1,030; D-S F1
0.7954 → 0.7990; VLM-only posterior 0.1862 → 0.1865). text-MIN row
re-derived against the canonical updated GT (D-S F1 0.7834 unchanged at
4 d.p.). T=0.3 row carries forward unchanged. Pre-recovery numbers are
preserved as `*.pre-recovery-20260502T235912.backup` siblings under each
run's `dawid-skene/` and `ds-human-crosstab/` directories. The post-recovery
shifts are small on every row — D-S F1 deltas ≤ +0.0036, VLM-only-posterior
deltas ≤ +0.0033, ECE / Brier deltas ≤ +0.001 — and do not change the
relative position of any run in any §4 ranking.

> **Correction, 2026-08-04 (W7-D9).** The T=0.7 sentence above previously
> ended "and the updated 4,745-mound curator GT". That is true of the
> *re-evaluation* (`f533fda5`) but false of the *D-S re-aggregation*
> (`366f9c66`), which took the script default reference — the fixed
> 4,770-feature base, `analyse_dawid_skene.py:57` — and so never saw the
> curator addition. Commit `366f9c66`'s own message makes the same claim
> and is contradicted by its artefact; this document inherited the error.
> The clause is removed rather than restated because the sentence
> describes three commits at once and no single GT count is true of all
> three. See § 2.1's reference caveat.

**Runs analysed**: T=0.3 (`55maps-text-high-t0.3-generalisation`), T=0.7
(`55maps-text-high-generalisation`), image (`55maps-image-generalisation`),
text-MIN (`55maps-text-min-generalisation`).
**Aggregator**: `scripts/analyse_dawid_skene.py` (canonical), post-hoc
fixed-prior fit (student sensitivity 0.95, specificity 1.0, fixed in EM;
D-S is not preregistered — D17 audit FALSE-12; the 5 % student-FN prior
derives from Sobotkova et al. 2023).
**Cross-tab**: `scripts/analyse_ds_vs_human_review.py` (degenerate-posterior
diagnostic against multi-buffer human review).

## 1. Summary

Four sibling Dawid-Skene (D-S) latent-truth fits on the 55-map
generalisation set — one for each of the production runs that produced
publishable corrected-F1 metrics — are in place, and as of 2026-08-14
all four are **re-fit against the standardised reference** (4,731
student records, `canonical-gt/standardised/`) using each run's
current canonical consensus + verifier probabilities (ruling 21;
queue item 1; artefacts under `dawid-skene-standardised/` per run,
commit `b140f686a`). The W7-D9 defect — the fits not sharing a
ground truth — is closed: every fit satisfies
matched + student-only = 4,731 exactly. Crosstabs against the
per-candidate human review are re-run against the new posteriors
(`ds-human-crosstab-standardised/` per run).

**Headline pattern across the four runs (standardised reference).**
D-S aggregate F1 follows the **measured** F1 ranking — now
**T=0.3 > T=0.7 > image > text-MIN** on both metrics. This is a
leader change from the pre-refresh report (T=0.7 > image > T=0.3 >
text-MIN): T=0.3's old fit consumed provenance-unresolved stale
inputs (§ 6.3) that suppressed its matched count by ~128; on current
inputs it leads. The +0.024 D-S correction over measured F1 remains
essentially constant across all four runs. The disagreement with the
corrected-F1-multi-buffer ranking (§ 4.3) **fully dissolves**: with
items 2–5 complete, all three estimators — measured, D-S, and
corrected-F1-multi-buffer — agree on the full ordering, and the two
corrections agree within 0.004 on every run (the middle-pair swap
was a per-run-vintage artefact; §§ 4.3, 5.3).
The crosstabs extend Obs 293's headline finding on cleaner data: the
**D-S calibration gap still scales monotonically with the VLM-only /
matched ratio**, with T=0.3 moving toward the conservative text
cluster (2.02×, was 2.53×) now its input artefact is gone; text-MIN
remains the best calibrated, nearly indistinguishable from T=0.7.

## 2. Per-run × per-class D-S agreement metrics

### 2.1 Shared item set (matched / student-only / VLM-only)

> **Reference caveat RESOLVED (2026-08-14).** The W7-D9 finding — the
> four fits not sharing a ground truth (image on the 4,745 reviewed
> layer, the three text runs on the fixed 4,770 base) — is closed by
> the ruling-21 refresh: all four fits below consume the
> **standardised reference** (4,731 student records) and each run's
> current canonical consensus + verifier probabilities. Verified:
> matched + student-only = 4,731 in every fit. The superseded fits
> remain under each run's `dawid-skene/` directory as history; the
> figures in this report are from `dawid-skene-standardised/`.

| Run | Matched | Student-only | VLM-only | Total | VLM-only / matched |
|-----|--------:|-------------:|---------:|------:|-------------------:|
| text-MIN | 3,279 | 1,452 | 586 | 5,317 | 0.179 |
| T=0.7 | 3,524 | 1,207 | 640 | 5,371 | 0.182 |
| T=0.3 | 3,658 | 1,073 | 692 | 5,423 | 0.189 |
| Image | 3,658 | 1,073 | 1,022 | 5,753 | 0.279 |

Sorted by VLM-only / matched ratio. text-MIN and T=0.7 keep the
conservative end (0.179 vs 0.182). T=0.3 moves sharply toward them
(0.189, was 0.232 in the superseded fit — the shrinkage is the
input-vintage correction of § 6.3, not a reference effect). Image
remains the most permissive on the VLM side (0.279). text-MIN still
has the smallest matched count (3,279) and the largest student-only
count (1,452), reflecting that it is the lowest-recall of the four
runs at the measured-F1 stage.

**T=0.3 and image share identical matched / student-only counts
(3,658 / 1,073) — verified a coincidence of aggregates, not an
artefact.** The matched student *sets* differ: intersection 3,207,
with each run matching a different 451 students the other misses (a
set-level check run 2026-08-14 on the two `item-posteriors.csv`
files; same benign shape as the S114 identical-confusion-matrix
case). Because the student-side counts coincide and the student
parameters are fixed, the two runs' D-S recall and student-side
expectations coincide arithmetically throughout §§ 2.2–2.4.

### 2.2 Worker accuracy (D-S confusion matrix estimates)

| Run | Student sensitivity | Student specificity | VLM sensitivity | VLM specificity | Estimated prevalence |
|-----|--------------------:|--------------------:|----------------:|----------------:|---------------------:|
| T=0.3 | 0.9500 (fixed) | 1.0000 (fixed) | 0.7821 | 0.0000 | 0.9079 |
| T=0.7 | 0.9500 (fixed) | 1.0000 (fixed) | 0.7545 | 0.0000 | 0.9154 |
| Image | 0.9500 (fixed) | 1.0000 (fixed) | 0.7821 | 0.0000 | 0.8558 |
| text-MIN | 0.9500 (fixed) | 1.0000 (fixed) | 0.7039 | 0.0000 | 0.9222 |

Student sensitivity / specificity are held fixed by the EM as required
for identifiability with two binary annotators. The VLM-sensitivity
estimates sit in a 0.7039–0.7821 band — text-MIN returns the
**lowest** VLM sensitivity (0.7039), consistent with its lowest
matched count: fewer student-known mounds were flagged by the VLM.
T=0.3 and image tie at the top (0.7821 each, to 4 d.p.) — the § 2.1
count coincidence propagating: with matched / student-only equal and
the student parameters fixed, VLM sensitivity is determined by the
same student-side arithmetic. VLM specificity converges to 0 in every
run; a known property of the 2-annotator response pattern, not a
meaningful per-class statistic.

The estimated prevalence of true mounds in the D-S item set is
highest for text-MIN (0.92), narrowly above T=0.7 (0.92), above
T=0.3 (0.91, up from the superseded 0.89 with its input artefact
removed) and image (0.86). Higher prevalence in text-MIN reflects
that the threshold-0.15 detection set is the smallest of the four
and proportionally the most concentrated on student-confirmed
locations.

### 2.3 D-S corrected metrics vs measured baseline

| Run | Measured F1 | Measured P | Measured R | D-S F1 | D-S P | D-S R | Δ F1 (D-S − measured) |
|-----|------------:|-----------:|-----------:|-------:|------:|------:|----------------------:|
| T=0.3 | 0.8056 | 0.8409 | 0.7732 | 0.8304 | 0.8852 | 0.7821 | **+0.0248** |
| T=0.7 | 0.7924 | 0.8463 | 0.7449 | 0.8170 | 0.8908 | 0.7545 | **+0.0246** |
| Image | 0.7774 | 0.7816 | 0.7732 | 0.8019 | 0.8228 | 0.7821 | **+0.0245** |
| text-MIN | 0.7629 | 0.8484 | 0.6931 | 0.7873 | 0.8930 | 0.7039 | **+0.0244** |

The +0.024–0.025 D-S correction remains essentially identical across
all four runs on the standardised reference. The mechanism is purer
than this report previously stated (a wording inherited from the
superseded version and corrected 2026-08-14 after blind
verification): the expected reclassification is
**matched × (0.05 / 0.95) exactly — independent of the VLM-only
count entirely**. The report's own § 2.4 shows it directly: image
carries 1,022 VLM-only items against T=0.3's 692, yet both
reclassify 192.5, because their matched counts coincide. The
correction magnitude is therefore a property of the fixed prior and
the matched count alone, not of any run's detection geometry — and
the constancy survived both the input-vintage correction (T=0.3)
and the reference move.

### 2.4 VLM-only posterior — the headline aggregate

| Run | VLM-only n | VLM-only posterior P(true=1) | Expected reclassified (soft) | Hard-threshold reclassified |
|-----|-----------:|-----------------------------:|------------------------------:|----------------------------:|
| T=0.3 | 692 | 0.2782 | 192.5 | 0 |
| T=0.7 | 640 | 0.2898 | 185.5 | 0 |
| Image | 1,022 | 0.1884 | 192.5 | 0 |
| text-MIN | 586 | 0.2945 | 172.6 | 0 |

text-MIN produces the **highest** VLM-only posterior of the four
(0.2945), narrowly above T=0.7 (0.2898), with T=0.3 now close behind
(0.2782 — up sharply from the superseded 0.2269, the input-vintage
correction having removed ~128 spurious VLM-only items). All three
text runs now cluster; image remains the clear **lowest** (0.1884)
because its VLM-only set is largest in proportion to matched, so the
fixed prior spreads thinner per item.

text-MIN remains the run with the **fewest absolute soft
reclassifications** (172.6 — the smallest of the four), reflecting
its smallest absolute VLM-only count. T=0.3 and image tie at 192.5 —
the § 2.1 student-side coincidence again, since expected
reclassification is set by the student-side arithmetic.

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
| text-MIN | 577 / 8 | 0.5477 (316/577) | 0.2945 | +0.253 | 1.86× | 0.2532 | 0.3118 | 0.500 |
| T=0.7 | 631 / 6 | 0.5547 (350/631) | 0.2898 | +0.265 | 1.91× | 0.2649 | 0.3172 | 0.500 |
| T=0.3 | 679 / 13 | 0.5626 (382/679) | 0.2782 | +0.284 | 2.02× | 0.2844 | 0.3270 | 0.500 |
| Image | 1,013 / 17 | 0.7206 (730/1,013) | 0.1884 | +0.532 | 3.83× | 0.5322 | 0.4846 | 0.500 |

Sorted by calibration gap. Notes:

- **AUC = 0.500 in every run** — degenerate by construction (a single
  unique posterior value per joined VLM-only item). The D-S posterior
  on the VLM-only slice cannot rank individuals; this is a property
  of the 2-annotator identifiability class, not a calibration failure.
- **2 × 2 cross-tab at threshold 0.5 collapses in every run** — every
  run's VLM-only posterior is below 0.5, so D-S `>` 0.5 is always 0
  and D-S `≤` 0.5 captures the entire joined set (TP=0, FP=0,
  FN=n_mound, TN=n_not_mound).
- **Unjoined rows are now small and uniform across all four runs**
  (6–17, i.e. ~1–2 % of each review cohort), where the superseded
  crosstabs had 0 / 0 / 64 / 0. The mechanism reversed: against the
  standardised reference a few review-cohort candidates reclassify
  from VLM-only to matched — verified per item for T=0.7, text-MIN
  and image (each dropped row sits within 50 m of a `matched` item
  in the new fit; the reclassification to specific GT edits —
  proxy-confirmed records vs marked-centre moves — is plausible but
  not itemised). T=0.3's 13 is additionally confounded by its
  input-vintage change, so it is not a clean reference-only effect.
  Their review rows no longer join the VLM-only slice either way.
  T=0.3's old 64-unjoined
  anomaly — previously attributed to its recovery pattern — is gone:
  it was an artefact of the superseded fit's provenance-unresolved
  inputs (§ 6.3), and § 5.5 is retired accordingly.
- **text-MIN's empirical mound rate (0.5477) is the lowest** of the
  four, just below T=0.7 (0.5547) and T=0.3 (0.5626), well below
  image (0.7206). The three text runs now sit inside a 0.015 band —
  the wide text-run spread in the superseded table (0.5538–0.5748)
  was largely the T=0.3 input artefact.

## 4. Cross-run comparison — extending Obs 293's headline

### 4.1 Aggregate F1 ordering — D-S matches measured, not corrected-F1

| Metric | Best | 2nd | 3rd | Worst |
|--------|------|-----|-----|-------|
| Measured F1 | T=0.3 (0.8056) | T=0.7 (0.7924) | Image (0.7774) | text-MIN (0.7629) |
| D-S corrected F1 | T=0.3 (0.8304) | T=0.7 (0.8170) | Image (0.8019) | text-MIN (0.7873) |
| Corrected-F1-multi-buffer F1 (R=50 m; standardised reference) | T=0.3 (0.8303) | T=0.7 (0.8169) | Image (0.8010) | text-MIN (0.7833) |
| D-S calibration ECE (lower = better) | text-MIN (0.253) | T=0.7 (0.265) | T=0.3 (0.284) | Image (0.532) |
| D-S calibration Brier (lower = better) | text-MIN (0.312) | T=0.7 (0.317) | T=0.3 (0.327) | Image (0.485) |

The D-S F1 ranking and the measured F1 ranking are **identical**
across all four runs — now **T=0.3 > T=0.7 > Image > text-MIN**.
This is a leader change from the superseded report (T=0.7 first):
T=0.3's superseded fit consumed provenance-unresolved inputs that
suppressed its matched count by ~128 (§ 6.3); on its current
canonical inputs and the common reference it leads decisively
(+0.0134 D-S F1 over T=0.7 — no longer a rounding-scale gap).

> **The W7-D9 withdrawal is RESOLVED (2026-08-14).** The
> Image-versus-T=0.3 ordering, withdrawn 2026-08-04 because the two
> fits were not on a common reference, is now established on the
> standardised reference: **T=0.3 clears Image by +0.0285 D-S F1**
> (0.8304 vs 0.8019), far outside any reference-effect envelope. The
> superseded near-tie (0.0002) was an artefact of comparing across
> references.

The corrected-F1-multi-buffer ranking on the standardised reference
is **T=0.3 > T=0.7 > Image > text-MIN — identical to the D-S and
measured rankings**. The rank-disagreement first noted in Obs 293 is
now fully resolved: the residual middle-pair swap (Image above T=0.7
on the old corrected-F1 column) was a per-run-vintage artefact — it
was already absent on the legacy *common* reference (the canonical
board scores T=0.7 0.8153 > Image 0.7988 at R=50 m,
`results/55maps-standardised-ref-2026-08-14/legacy-baseline/`), and
standardisation preserves that (0.8169 > 0.8010). The original
four-way disagreement therefore decomposes entirely into reference
artefacts: T=0.3's stale D-S inputs (§ 6.3) plus the per-run-vintage
extension references the old per-run summaries scored against
(cf. Obs 292's R≥75 m crossover, the same artefact class).

The calibration ECE / Brier ranking is unchanged in order —
**text-MIN narrowly first**, T=0.7 second, T=0.3 third, image last —
but T=0.3 closes most of its gap to the leaders (ECE 0.284, was
0.348). Consistent with §4.2: calibration ranks by VLM-only /
matched ratio, and the three text runs now cluster (0.179 / 0.182 /
0.189) with image far behind (0.279).

### 4.2 Calibration gap scales monotonically with VLM-only / matched ratio

The size of the calibration gap between D-S aggregate and empirical
human-review rate continues to scale monotonically with the VLM-only
share of the detection set; the four-run comparison **strengthens**
the three-run pattern reported in Obs 293:

| Run | VLM-only / matched ratio | Posterior:empirical ratio (= 1 / underestimate) |
|-----|-------------------------:|-------------------------------------------------:|
| text-MIN | 0.1787 (586 / 3,279) | 1.86× |
| T=0.7 | 0.1816 (640 / 3,524) | 1.91× |
| T=0.3 | 0.1892 (692 / 3,658) | 2.02× |
| Image | 0.2794 (1,022 / 3,658) | 3.83× |

The pattern: as the VLM-only share grows, the fixed 5 % student-FN
prior under-counts true positives more severely. **The monotonic
scaling survives both the reference move and the T=0.3 input
correction** — the strongest test the pattern has had, since T=0.3's
ratio moved substantially (0.232 → 0.189) and its calibration ratio
moved with it (2.53× → 2.02×), staying exactly in rank order. There
is still no rank inversion at any point along the scale. text-MIN —
narrowly the most conservative on VLM-only share — remains the best
calibrated; image — by far the most permissive — remains by far the
worst.

The three text runs now sit on a tight section of the curve (ratios
0.179–0.189, calibration 1.86–2.02×) with image alone on the steep
section — sharpening § 5.2's modality reading. The unjoined-row
noise that previously singled out T=0.3 is gone (§ 3): all four runs
carry a uniform ~1–2 % unjoined rate with a common, documented
mechanism.

### 4.3 D-S corrected F1 vs corrected-F1-multi-buffer F1 — different methods, different answers

The D-S corrected F1 reported here is **not** the headline corrected-F1
that lands in the per-run `corrected-f1-multi-buffer/` summaries. The
two analyses use different correction methodologies and different
ground truth:

| Run | D-S corrected F1 (standardised) | corrected-F1-multi-buffer F1 (R=50 m; standardised) | Δ |
|-----|--------------------------------:|----------------------------------------------------:|---:|
| T=0.3 | 0.8304 | 0.8303 | −0.0001 |
| T=0.7 | 0.8170 | 0.8169 | −0.0001 |
| Image | 0.8019 | 0.8010 | −0.0009 |
| text-MIN | 0.7873 | 0.7833 | −0.0040 |

(The corrected-F1-multi-buffer numbers are the standardised-reference
board cells {T03-k4, TH7-k4, IM-k3, TM-k4} at R=50 m,
`results/55maps-standardised-ref-2026-08-14/consolidated-standardised.csv`;
the cell↔run identity was gated by feature-count crosscheck — each
cell scored the same `verified/verified_detections.geojson` the
per-run summaries scored, counts 4,350 / 4,164 / 4,680 / 3,865.)

The D-S correction now uses the **standardised student layer**
(`canonical-gt/standardised/student-mounds-55maps-standardised.geojson`)
and applies a fixed 5 % student-FN prior to the 2-annotator EM. The
corrected-F1-multi-buffer correction uses the reviewed student GT
extended by the human-review mound calls at each buffer band, then
runs Hungarian matching against that extended ground truth. The
corrected-F1-multi-buffer correction is the headline reported
elsewhere; the D-S correction reported here is a secondary diagnostic
of how the 2-annotator latent-truth model performs on the same
underlying data.

With both columns on the standardised reference the two corrections
**converge almost exactly**: every run agrees within 0.004, and the
three text runs within 0.0001–0.0040 — against superseded gaps of
+0.010 to +0.045 that were reference artefacts, layer by layer
(T=0.3's stale D-S inputs, then image's per-run-vintage extension).
This is a striking cross-validation rather than a tautology: the two
estimators reach their numbers by different routes — a fixed-prior
2-annotator EM over candidate-grain votes versus Hungarian matching
against the extended reference at R=50 m — and were computed and
blind-verified in independent sessions (S131 refits `b140f686a`;
S132 board re-score, summary blind-verified 249/242/234/8). On a
common reference they now measure the same quantity to within each
method's own uncertainty. The earlier reading that image's +0.031
residual gap was "the substantive methodological difference" is
**withdrawn**: it was the last reference artefact standing, not
methodology (image's per-run-vintage extension was the furthest from
the standardised layer, cf. § 5.4).

## 5. Surprising patterns — flagged

### 5.1 text-MIN's calibration metrics nearly clone T=0.7's

text-MIN and T=0.7 produce **nearly identical** D-S calibration
diagnostics:

| Metric | text-MIN | T=0.7 | Difference |
|--------|---------:|------:|-----------:|
| VLM-only / matched | 0.1787 | 0.1816 | −0.0029 |
| VLM-only posterior | 0.2945 | 0.2898 | +0.0047 |
| Empirical rate | 0.5477 | 0.5547 | −0.0070 |
| Calibration gap (emp − D-S) | 0.253 | 0.265 | −0.012 |
| ECE | 0.2532 | 0.2649 | −0.0117 |
| Brier | 0.3118 | 0.3172 | −0.0054 |

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

The image run's D-S calibration gap (3.83×) is roughly **double**
T=0.3's (2.02×) and T=0.7's (1.91×), and more than double
text-MIN's (1.86×) — and the refresh *sharpens* the contrast: the
three text-prompt runs now sit on a tight section of the same
calibration curve (1.86–2.02×, ratios 0.179–0.189), while image
stands alone on the steep section. This isolates the image-modality
calibration penalty as a **modality-specific** effect rather than a
prompt-specific one — text prompts at three different configurations
all calibrate consistently; the image prompt does not. This is
consistent with Obs 273 (D-S structurally inadequate on the VLM-only
slice for the image run) and with the v2 data-driven-prior diagnostic
in `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/`.

### 5.3 D-S F1 and corrected-F1 now agree on the FULL ordering — the middle-pair disagreement is resolved

The superseded report could claim agreement only on text-MIN being
last; the 2026-08-14 refresh extended it to the leader with the
middle pair still swapped. With the corrected-F1 column now on the
standardised reference, the agreement is **complete**:

- D-S F1 ranks: **T=0.3** > T=0.7 > Image > **text-MIN**
- Corrected-F1 ranks (standardised): **T=0.3** > T=0.7 > Image >
  **text-MIN**

The middle-pair swap was a per-run-vintage artefact of the old
corrected-F1 column (§ 4.1): on any common reference — legacy
canonical or standardised — T=0.7 sits above Image on corrected-F1
as well. Obs 293's cross-method disagreement is thereby fully
dissolved. The agreement on text-MIN being last remains robust for
the original reason — its combination of (lowest matched, highest
student-only, lowest VLM sensitivity) is consistent across
methodologies, and its recall floor is below what extension-based
correction can bridge. **text-MIN's corrected F1 (0.7833,
standardised) remains the only sub-0.80 run on the headline
corrected metric** (Image clears it at 0.8010).

### 5.4 All four runs' F1 estimates now agree tightly — the "loose image" reading dissolves

| Run | Measured | D-S | Corrected-F1-multi-buffer (standardised) | Spread |
|-----|---------:|----:|------------------------------------------:|-------:|
| T=0.3 | 0.8056 | 0.8304 | 0.8303 | 0.025 |
| T=0.7 | 0.7924 | 0.8170 | 0.8169 | 0.025 |
| Image | 0.7774 | 0.8019 | 0.8010 | 0.025 |
| text-MIN | 0.7629 | 0.7873 | 0.7833 | 0.024 |

Two successive artefacts have now been peeled off this table. The
original reading — "T=0.7 is the only run where the three estimates
agree" — fell with T=0.3's stale D-S inputs (2026-08-14). The
intermediate reading — "the three text runs agree in a 0.034–0.038
envelope and image alone is loose (0.056)" — falls with the
corrected column's per-run-vintage references: on the standardised
reference **all four spreads land at 0.024–0.025**, and the spread
is simply the D-S/extension correction itself, since the two
corrected estimators agree within 0.004 everywhere (§ 4.3). No
modality effect on estimator agreement survives; image's apparent
looseness was its extension reference sitting furthest from the
standardised layer.

### 5.5 RESOLVED — the 64 unjoined T=0.3 review rows were an artefact of the superseded fit's inputs

The superseded crosstab showed T=0.3 with 64 / 692 = 9.2 % unjoined
review rows against 0 % for the other three runs, and this section
previously attributed the divergence to T=0.3's single-round
recovery pattern. **That attribution was wrong.** Against the
refreshed fit — current canonical inputs, standardised reference —
T=0.3's unjoined count drops to 13 / 692 (1.9 %), inside the uniform
6–17-row band all four runs now show (§ 3), whose mechanism is the
reference change, not any per-run property. The 64-row anomaly was
produced by the superseded fit's provenance-unresolved input set
(§ 6.3), whose ~128 surplus VLM-only items misaligned the D-S slice
with the review cohort. The recovery-pattern explanation is
withdrawn; nothing about T=0.3's recovery is implicated.

## 6. Provenance and inputs

All four D-S aggregations use the same canonical pattern:

- Script: `scripts/analyse_dawid_skene.py`
- Threshold: 0.15
- Buffer: 50 m
- Verifier: v1 (the production verifier, not the v2 family)
- Student-FN prior: 0.05 (Sobotkova et al. 2023, fixed)
- Student GT: `results/deployment-oracle-2026-06-06/canonical-gt/`
  `standardised/student-mounds-55maps-standardised.geojson` (4,731;
  the ruling-21 standardised reference — since 2026-08-14. The
  superseded fits under `dawid-skene/` used the legacy
  `student-mounds-55maps.geojson`, or for image the 4,745 reviewed
  snapshot; see § 6.3)
- Bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`

Per-run consensus and verifier probabilities:

| Run | Consensus | Probabilities |
|-----|-----------|---------------|
| T=0.3 | `outputs/55maps-text-high-t0.3-generalisation/consensus/consensus-4of5.geojson` | `outputs/55maps-text-high-t0.3-generalisation/verified/probabilities.json` |
| T=0.7 | `outputs/55maps-text-high-generalisation/consensus/consensus-4of5.geojson` | `outputs/55maps-text-high-generalisation/verified/probabilities.json` |
| Image | `outputs/55maps-image-generalisation/consensus/consensus-3of5.geojson` | `outputs/55maps-image-generalisation/verified/probabilities.json` |
| text-MIN | `outputs/55maps-text-min-generalisation/consensus/consensus-4of5.geojson` | `outputs/55maps-text-min-generalisation/verified/probabilities.json` |

### 6.1 Resolved — T=0.7 + image D-S re-aggregated post-recovery 2026-05-03

The earlier (Apr 19) T=0.7 D-S sibling was run against the analyse-script's
**default** legacy consensus (`outputs/55maps-generalisation/...`) rather
than the T=0.7-specific run output. The post-recovery re-aggregation on
2026-05-03 (commit `366f9c66`) re-runs D-S against the T=0.7-specific
paths shown in the table above, alongside the recovered single-round
proposer + verifier passes (commits `731466d8`, `d7f85978`, `e20f3e18`)
and the canonical updated curator GT (4,745 mounds, including the
+1 added at K-35-064-3 in `baf1497a`). The image row was also
re-aggregated as part of cross-track-v2 (commit `42ed1d32`) to
reflect the canonical updated GT and the +1 phantom-promoted cand
2397 on the image side. The pre-recovery D-S artefacts are preserved
as `*.pre-recovery-20260502T235912.backup` and
`*.pre-recovery-20260503T023258.backup` siblings under each
re-aggregated run's `dawid-skene/` and `ds-human-crosstab/`
directories.

T=0.7 item-set deltas vs the legacy-path Apr 19 result:

- matched: 3,513 → 3,527 (+14)
- student-only: 1,257 → 1,243 (−14)
- VLM-only: 630 → 637 (+7)
- VLM-only posterior: 0.2935 → 0.2914
- D-S F1: 0.8129 → 0.8142

Image item-set deltas vs the pre-recovery row:

- matched: 3,637 → 3,650 (+13)
- student-only: 1,133 → 1,095 (−38, reflecting canonical-GT join cleanup)
- VLM-only: 1,028 → 1,030 (+2, the cand 2397 promotion plus one canonical-GT join shift)
- VLM-only posterior: 0.1862 → 0.1865
- D-S F1: 0.7954 → 0.7990

Each re-aggregated run's relative position vs the other three is
preserved on every §4 ranking — see §4.1 / §4.2. Shifts are smaller
than expected from the legacy/canonical path divergence because each
post-recovery verified set is close in cardinality to its
pre-recovery counterpart and the new GT mounds are matched, not
left dangling.

The T=0.3 and text-MIN D-S aggregations use their run-specific
paths and were not re-run for the cross-track-v2 refresh; their
numbers carry forward unchanged from the previous summary (text-MIN
D-S F1 = 0.7834; T=0.3 D-S F1 = 0.7988; both verified against
their current `dawid-skene/dawid-skene-results.json` files on
2026-05-03).

### 6.2 Per-run human-review files

| Run | Yesterday review | Today review |
|-----|------------------|--------------|
| T=0.3 | (none — empty placeholder used) | `results/55maps-text-high-t0.3-generalisation/human-review-multi-buffer.csv` (692 rows) |
| T=0.7 | (none — empty placeholder used) | `results/55maps-text-high-generalisation/human-review-multi-buffer.csv` (637 rows) |
| Image | `results/55maps-image-generalisation/human-review.csv` (1,028 rows) | `results/55maps-image-generalisation/human-review-multi-buffer.csv` (558 rows) |
| text-MIN | (none — empty placeholder used) | `results/55maps-text-min-generalisation/human-review-multi-buffer.csv` (585 rows) |

*Row counts corrected 2026-08-04 (W7-D6). Every cell in this table is a
**data-row count**, excluding the CSV header. text-MIN previously read 586,
which counted its header line — the file has 586 lines and 585 data rows —
and was inconsistent with the T=0.3, T=0.7 and image cells, all of which
already excluded theirs. Image previously read 557, which is the
cross-tabulator's accounting (556 today-rows also present in the yesterday
review, plus the 1 `today_only` recorded in `ds-human-crosstab/summary.json`)
rather than the file's row count; under this table's own stated semantics —
the column names the CSV and reports its rows — it is 558.*

The image run is the only one with a separate yesterday-strict review;
T=0.3, T=0.7, and text-MIN only have the multi-buffer review. The
crosstab script treats the empty-yesterday case correctly — every
multi-buffer row lands in the `today_only` source bucket with its
multi-buffer label intact.

### 6.3 The 2026-08-14 standardised refits — vintages, decomposition, and one open provenance question

All four fits were re-run once (ruling 21; queue item 1; commit
`b140f686a`) with each run's **current canonical** consensus +
probabilities (§ 6's table) and the standardised reference. To
attribute the movement, each text run was also fitted with current
inputs against the legacy 4,770 GT (fit "B" — a diagnostic, not a
citable performance number; not committed). D-S F1 decomposition:

| Run | A: superseded fit | B: current inputs, legacy GT | C: standardised (this report) | B − A (input vintage) | C − B (reference) |
|-----|------------------:|------------------------------:|-------------------------------:|----------------------:|-------------------:|
| T=0.7 | 0.8142 | 0.8142 (exact reproduction) | 0.8170 | 0.0000 | +0.0028 |
| T=0.3 | 0.7988 | 0.8272 | 0.8304 | **+0.0284** | +0.0032 |
| text-MIN | 0.7834 | 0.7838 | 0.7873 | +0.0004 | +0.0035 |
| Image | 0.7990 | — (4,745 base is record-only, ruling 19a) | 0.8019 | — | +0.0029 (joint) |

**The reference move is uniform (+0.0028 to +0.0035 across all four
runs)** — the standardised layer's duplicate removals and position
corrections lift D-S F1 by ~+0.003 regardless of configuration.
Everything larger is input vintage: text-MIN's +0.0004 is the
documented `c1ea6df3c` recovery (+39 consensus features, +4
verified); T=0.7's exact B-reproduction confirms its committed fit
was already on current inputs.

**Open and not guessed at — the superseded T=0.3 fit's inputs are
unidentified.** Two hypotheses were tested exactly and falsified on
2026-08-14: (i) "inputs repaired after the fit" — falsified by
commit order (the `548604d95` recovery landed 01:19 Z, the fit
`0b14e4fcd` committed 11:35 Z — 21:35 AEST — the same day, 10 h 16 m
later; `git merge-base --is-ancestor` confirms); (ii) "fit computed
pre-recovery, committed late" — falsified by re-running the fit on
the pre-recovery inputs extracted from `548604d95^`, which gives
{3,658 / 1,112 / 691 / 5,461}, not the committed
{3,531 / 1,239 / 819 / 5,589}. The committed fit consumed a larger,
worse-matching detection set matching neither vintage. The earlier
in-session attribution to the fit's inputs being "repaired after the
fit" (commit `b140f686a`'s message) is withdrawn. The superseded fit
is superseded wholesale either way; the provenance question is
registered as a verification item, not a blocker.

## 7. References and sibling artefacts

Per-run outputs (current — the standardised refits this report cites):

- `results/<run>/dawid-skene-standardised/` — the four ruling-21 D-S
  refits (commit `b140f686a`), one per run.
- `results/<run>/ds-human-crosstab-standardised/` — the four
  crosstabs against the refit posteriors.

Superseded per-run outputs (history; pre-standardisation figures):

- `results/55maps-text-high-t0.3-generalisation/dawid-skene/` — T=0.3 D-S aggregation.
- `results/55maps-text-high-t0.3-generalisation/ds-human-crosstab/` — T=0.3 D-S vs human review.
- `results/55maps-text-high-generalisation/dawid-skene/` — T=0.7 D-S aggregation (preserved from Apr 19).
- `results/55maps-text-high-generalisation/ds-human-crosstab/` — T=0.7 D-S vs human review.
- `results/55maps-image-generalisation/dawid-skene/` — image D-S aggregation (preserved from Apr 18).
- `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/` — image v2 data-driven prior sensitivity sweep (preserved from Apr 21–23).
- `results/55maps-image-generalisation/ds-human-crosstab/` — image D-S vs human review (preserved from Apr 21–23, hand-levelled-up Apr 23).
- `results/55maps-text-min-generalisation/dawid-skene/` — text-MIN D-S aggregation (re-run 2026-04-28 against canonical text-MIN paths; reproduced byte-identically).
- `results/55maps-text-min-generalisation/ds-human-crosstab/` — text-MIN D-S vs human review (new 2026-04-28).

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
  `docs/notes/working-notes.md` (path corrected 2026-08-14; the
  `reflections/` form propagated from older artefacts and never
  existed).

## Changelog

### 2026-08-15 — Post-queue refresh: §§ 4.1/4.3/5.3/5.4 corrected-F1 figures onto the standardised reference

**Trigger**: reference-standardisation queue items 2–5 complete
(S132); this discharges the S131 carry-forward ("§§ 4.1/4.3/5.3/5.4
… then re-examine the middle-pair swap") and the banner's stale
"pending items 2–5" flag. Executed under the S133 block plan
(`planning/s133-analysis-block-2026-08-15.md`, hardenings 4–5).

**Source**: standardised board cells {T03-k4, TH7-k4, IM-k3, TM-k4}
at R=50 m
(`results/55maps-standardised-ref-2026-08-14/consolidated-standardised.csv`,
S132, blind-verified). Cell↔run identity gated by feature-count
crosscheck: each cell scored the same
`outputs/<run>/verified/verified_detections.geojson` the superseded
per-run summaries scored (4,350 / 4,164 / 4,680 / 3,865). The
superseded figures were **per-run-vintage** (each run's
`corrected-f1-multi-buffer/summary.json`, scored against its own
extension vintage) — they matched neither the legacy canonical board
nor the standardised one, so this is a documented two-step vintage
jump.

| Site | Quantity | Was (per-run vintage) | Now (standardised) |
|---|---|---:|---:|
| §§ 4.1/4.3/5.4 | T=0.3 corrected F1 @50 m | 0.8437 | 0.8303 |
| §§ 4.1/4.3/5.4 | T=0.7 corrected F1 @50 m | 0.8273 | 0.8169 |
| §§ 4.1/4.3/5.4 | Image corrected F1 @50 m | 0.8333 | 0.8010 |
| §§ 4.1/4.3/5.4 | text-MIN corrected F1 @50 m | 0.7968 | 0.7833 |
| § 4.3 | D-S − corrected gaps | +0.010…+0.031 | −0.0001…−0.0040 |
| § 5.4 | Three-estimator spreads | 0.034–0.056 | 0.024–0.025 |

**Findings the refresh produced**: (1) the Obs 293 middle-pair swap
(Image above T=0.7 on corrected-F1) **dissolves** — it was a
per-run-vintage artefact, already absent on the legacy common
reference (T=0.7 0.8153 > Image 0.7988); all three estimators now
agree on the full ordering T=0.3 > T=0.7 > Image > text-MIN. (2) The
two correction methodologies **converge to within 0.004 on every
run** — a cross-validation, since the D-S refits (S131) and the
board re-score (S132) were computed and blind-verified
independently. (3) § 5.4's "image is the loose one" reading
**withdrawn**: all four spreads land at 0.024–0.025.

**Not changed**: measured and D-S F1 columns (already standardised,
2026-08-14); §§ 1–3, 4.2, 5.1, 5.2, 5.5, 6; all crosstab and
calibration figures; text-MIN's only-sub-0.80 status (0.7833; Image
clears at 0.8010). Historical changelog entries retain their
old-reference wording as records of their own time.

### 2026-08-14 — Ruling-21 refresh: all four fits on the standardised reference

Queue item 1 executed (commit `b140f686a` for the fits; this commit
for the report). All four D-S fits re-run once against the
standardised reference (4,731) with each run's current canonical
inputs; crosstabs re-run against the new posteriors. Headline moves:

| Claim | Before | After |
|-------|--------|-------|
| D-S / measured F1 leader | T=0.7 (0.8142 / 0.7896) | **T=0.3 (0.8304 / 0.8056)** |
| D-S F1 ranking | T=0.7 > Image > T=0.3 > MIN | **T=0.3 > T=0.7 > Image > MIN** |
| Image-vs-T=0.3 ordering | WITHDRAWN (W7-D9) | resolved: T=0.3 +0.0285 |
| T=0.3 calibration ratio | 2.53× | 2.02× |
| T=0.3 unjoined crosstab rows | 64 (9.2 %) | 13 (1.9 %) |
| D-S-vs-corrected-F1 gap, T=0.3 | +0.045 | +0.013 |

What did NOT change: the +0.024–0.025 D-S correction constancy; the
§ 4.2 monotonic calibration scaling (now on its strongest evidence);
text-MIN last on every F1 metric and first on calibration; image's
modality-specific calibration penalty (sharpened). Most of the old
cross-method disagreement (§ 4.3) and the T=0.3 crosstab anomaly
(§ 5.5) resolve into artefacts of the superseded T=0.3 fit's inputs,
whose provenance is unresolved after two falsified hypotheses —
documented with the B/C decomposition in the new § 6.3. The § 2.1
reference caveat and § 4.1 withdrawal are resolved in place.
Corrected-F1-multi-buffer figures remain old-reference (flagged
throughout) pending queue items 2–5.

### 2026-08-04 (later) — W7 repair queue: the reference split, and three internal contradictions

**Refresh trigger**: repairing W7-D5 — a FALSE GREEN in this document's own
extraction, `reports/verification/c4-extraction/073.json`, where the front
matter's "4,745-mound curator GT" had been anchored to the T=0.7
*corrected-F1* artefact. That anchor agreed numerically and verified green
for a computation the sentence is not about. Re-anchoring it to the T=0.7
*Dawid–Skene* artefact turned it red and exposed W7-D9.

**W7-D9 — the four D-S fits do not share a ground truth.** Image's fit
consumed the reviewed curator layer (4,745 student points); T=0.7, T=0.3 and
text-MIN consumed the fixed 4,770-feature base, which is the default in
`scripts/analyse_dawid_skene.py:57`. Established two ways: `student_label == 1`
rows per run's `item-posteriors.csv` (4,770 / 4,770 / 4,770 against image's
4,745), and — independent of counts — the single feature commit `baf1497a7`
added to the reviewed layer, which is a student point *only* in the image
item set while T=0.7 carries `student_label = 0` at that same coordinate.
Commit `366f9c66`'s message asserts the D-S re-run used the updated GT and is
contradicted by its own artefact; this document inherited the error.

| § | Claim | Before | After | Basis |
|---|-------|--------|-------|-------|
| Front matter | What the T=0.7 re-derivation consumed | "recovered consensus + verifier **and the updated 4,745-mound curator GT**" | the 4,745 attribution corrected in place: true of the re-evaluation (`f533fda5`), false of the D-S re-aggregation (`366f9c66`) | `analyse_dawid_skene.py:57`; the `baf1497a7` point test |
| 1 | Measured-F1 ranking (W7-D3) | T=0.7 > T=0.3 > image > text-MIN | T=0.7 > image > T=0.3 > text-MIN | measured F1 0.7896 / 0.7745 / 0.7743 / 0.7591; § 4.1's own table already had it right |
| 2.1 | — | (no caveat) | reference caveat added | as above |
| 4.1 | Image-versus-T=0.3 D-S F1 ordering | asserted | **withdrawn pending re-analysis**, text left in place | 0.0002 gap against a 25-point reference difference |
| 4.2 | text-MIN unjoined rows (W7-D4) | "the **only** run with zero unjoined rows" | one of three (with T=0.7 and image) | `ds-human-crosstab/summary.json` `n_unjoined` = 0 / 0 / 0 / 64 |
| 1, 4.3 | text-MIN review cohort (W7-D6) | 586 rows | 585 rows | 586 lines, 585 data rows; the sibling "692" for T=0.3 is a data-row count |
| 5 | Image today-review cohort (W7-D6) | 557 rows | 558 rows | 558 data rows; 557 was the cross-tabulator's accounting, not the file's |

**What did NOT change**: no metric was recomputed and no artefact was
re-generated. Every D-S, measured and corrected-F1 value stands exactly as
before. T=0.7 remains first and text-MIN last on both the measured and D-S
rankings; the rank-*disagreement* between those and the corrected-F1
ordering — this document's headline finding, and Obs 293's — is untouched,
because it does not depend on the Image/T=0.3 ordering. § 4.2's calibration
conclusion is unchanged: text-MIN's status as the cleanest test rested on
its VLM-only/matched ratio, not on being uniquely unjoined.

**Why nothing was re-run.** Under ruling 21 the ground-truth reference is
standardised *first* and every reference-tainted analysis then runs once
against it. Re-running these four fits now would waste the run, because the
reference moves again when the 773 promoted phantoms are re-reviewed with
point-marking. The queue is
`reports/verification/reference-standardisation-queue.md` (item 1).

Landed at commit `TBD` (recorded in the next revision).

### 2026-08-04 (earlier) — C4 wave-7 repair: image corrected-F1 @ 50 m, plus GT-count adjudication

**Refresh trigger**: the W6-E9 de-duplication chain — `1de559119`
(coincidence de-dup in `build_extended_gt`), `30a902f56` (corrected-F1
regenerated from the tracked HEAD ground truth (GT)), and `fcfc90bff`
(5 m tolerance plus canonical guard). The chain's 2026-08-03 cand-2397
re-run moved the image run's corrected-F1-multi-buffer value at
R = 50 m from 0.8332 to 0.833333…, i.e. **0.8333** at 4 d.p. This
document carried the pre-re-run 0.8332 in three live table cells, all
restating the same artefact figure. The sibling
`results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md`
already carries 0.8333 and records the transition in its own changelog.

| § | Cell | Before | After | Artefact value |
|---|------|-------:|------:|----------------|
| 4.1 | Image corrected-F1-multi-buffer F1 (R = 50 m) | 0.8332 | 0.8333 | `$.results[0].F1` = 0.8333333333333333 |
| 4.3 | Image corrected-F1-multi-buffer F1 (R = 50 m) | 0.8332 | 0.8333 | as above |
| 5.4 | Image corrected-F1-multi-buffer F1 (R = 50 m) | 0.8332 | 0.8333 | as above |

Artefact re-read for every value above:
`results/55maps-image-generalisation/corrected-f1-multi-buffer/summary.json`,
whose `results[0]` carries `R_m` = 50, `n_ref_student_only` = 4746,
`n_phantom_duplicates_dropped` = 1, and `F1` = 0.8333333333333333.

**What did NOT change**: every ranking, every derived cell, and every
conclusion. The § 4.1 corrected-F1 ordering (T=0.3 > Image > T=0.7 >
text-MIN) and the rank-disagreement framing against the D-S and measured
orderings are untouched. The § 4.3 Δ column stays at +0.034 for image
(0.8333 − 0.7990 = 0.0343, still +0.034 at 3 d.p.) and text-MIN plus
T=0.7 still share the smallest gap at +0.013. The § 5.4 spread column
stays at 0.059 for image (0.8333 − 0.7745 = 0.0588, still 0.059 at
3 d.p.), so T=0.3 remains the loosest at 0.069 and text-MIN remains
joint-tightest with T=0.7 at 0.038. The correction is fourth-decimal
throughout.

**GT-count occurrences deliberately left unchanged**: this document
contains two references to a 4,745-mound curator GT — in the
post-recovery preamble ("the updated 4,745-mound curator GT (commits
`366f9c66`, `e07dae37`, `f533fda5`)") and in § 6.1 ("the canonical
updated curator GT (4,745 mounds, including the +1 added at K-35-064-3
in `baf1497a`)"). Both are **era-faithful history, not stale**, and
both are correct as written. The canonical GT timeline, established by
timestamp comparison and recorded in
`reports/verification/c4-triage/coverage-drift-2026-08-04.json` under
`gt_count_era_resolution`, is: `baf1497a7` took the GT from 4,744 to
4,745 at 2026-05-03T00:32:53Z, and `2e075eb99` took it from 4,745 to
4,746 at 2026-05-03T05:28:57Z. Every commit cited in the two clauses
above landed inside that window — `f533fda5` at 00:42:38Z, `366f9c66`
at 01:08:13Z, `e07dae37` at 01:08:30Z, and the cross-track-v2 commit
`42ed1d32` at 04:34:20Z — so the re-derivations those sentences
describe genuinely consumed a 4,745-feature GT. Both sentences assert
what a past evaluation used, not what the current canonical count is;
under the disposition rule they are "do not touch". For the avoidance
of doubt, the live GT
(`inputs/vectors/references/student-mounds-55maps-reviewed.geojson`)
holds **4,746** features at this commit.

> **Correction, 2026-08-04 (same day).** This entry originally continued:
> "and the D-S aggregations documented here consume the separate legacy
> layer `inputs/vectors/references/student-mounds-55maps.geojson` (see
> § 6), not the reviewed layer at all." **That blanket statement is
> withdrawn.** An independent blind verification pass of this repair
> (`reports/verification/c4-triage/blind-passes/wave7-w7e4-verification-2026-08-04.json`)
> found the four runs are **not** uniform on this point: the image run's
> Dawid–Skene fit implies a 4,745-point student ground truth, while the
> other three imply the 4,770-feature legacy layer. Which layer each D-S
> fit actually consumed is **open and unadjudicated**, and it is escalated
> rather than asserted here. It matters beyond bookkeeping: every
> cross-run D-S comparison in this document assumes a common reference,
> and that assumption is currently unverified.

### 2026-08-03 — C4 wave-6 calibration-cell repairs

**Refresh trigger**: Session-126 C4 wave-6 triage. Blind pass P4
recommendation R4 and its five row-level exceptions
(`reports/verification/c4-triage/blind-passes/wave6-pass-P4-2026-08-03.json`);
consolidated adjudication in
`reports/verification/c4-triage/mismatch-triage-2026-08-03-wave6.json`.
Two mechanisms account for all five cells: (a) stale carry-over from
the 2026-05-03 image-recovery propagation (`fc536a19c`), where a row
was refreshed cell by cell and the derived cell was left untouched
even though the recovery moved it across a rounding boundary; and
(b) double-rounding, where a restatement was rounded from a displayed
4 d.p. value rather than from the artefact.

| § | Cell | Before | After | Artefact value |
|---|------|-------:|------:|----------------|
| 3 | Image calibration gap (emp − D-S) | +0.539 | +0.538 | 0.7249757046 − 0.1865 = 0.5384757 |
| 3 | Empirical-rate span across the four runs | 0.55–0.73 | 0.55–0.72 | max 0.7249757046 (image) → 0.72; min 0.5538461538 (text-MIN) → 0.55 |
| 4.1 | Image D-S calibration ECE | 0.539 | 0.538 | `ece` = 0.5384655048 |
| 4.1 | T=0.3 D-S calibration Brier | 0.366 | 0.365 | `brier` = 0.3654520487 |
| 5.2 | T=0.7 posterior:empirical ratio | 1.90× | 1.92× | 0.5588697017 / 0.2914 = 1.91788 |

Artefacts re-read for every value above:
`results/55maps-image-generalisation/ds-human-crosstab/summary.json`
(`prevalence`, `ece`),
`results/55maps-image-generalisation/dawid-skene/dawid-skene-results.json`
(`vlm_only_posterior`),
`results/55maps-text-high-t0.3-generalisation/ds-human-crosstab/summary.json`
(`brier`),
`results/55maps-text-high-generalisation/ds-human-crosstab/summary.json`
(`prevalence`),
`results/55maps-text-high-generalisation/dawid-skene/dawid-skene-results.json`
(`vlm_only_posterior`),
`results/55maps-text-min-generalisation/ds-human-crosstab/summary.json`
(`prevalence`).

**What did NOT change**: every ranking and every conclusion. The § 3
calibration-gap ordering (image ≫ T=0.3 > T=0.7 > text-MIN), the § 4.1
ECE / Brier ordering (text-MIN < T=0.7 < T=0.3 < image), the § 4.2
monotonic scaling of the calibration gap with the VLM-only / matched
ratio, and the § 5.2 image-modality framing (image's gap roughly double
T=0.7's) all hold under both the old and the new values. All five
corrections are third-decimal.

**Also resolved**: the § 5.2 sentence previously read 1.90× for T=0.7
while §§ 3 and 4.2 read 1.92× for the same run and the same statistic —
the document contradicted itself. The 1.92× form (refreshed by the
2026-05-03 recovery propagation) is correct and now appears in all
three places.

### 2026-07-28 — Dawid-Skene attribution corrected (no trail left at the time)

Commit `1844e5887` (wave 5 of the D17 attribution sweep, FALSE-12)
replaced the "preregistered fixed-prior fit" framing in the preamble
with post-hoc framing, and repointed the 5 % student-FN prior to
Sobotkova et al. (2023); § 4.3's "preregistered fixed prior" became
"fixed Sobotkova-derived prior". No numerical value changed. That
revision left no banner or changelog entry; it is recorded here
retrospectively as part of the first Revision-Policy stub for this
document.

### 2026-04-27 — Original publication

First authored as a three-run D-S cross-run summary (T=0.3, T=0.7,
image) at commit `da0552381`. Extended to four runs the following day
with text-MIN (`750d2c51b`, 2026-04-28 — the date the document's own
header carries), then refreshed twice on 2026-05-03 to propagate the
post-recovery T=0.7 numbers (`ae50d94de`) and the image / text-MIN /
GS-v2 recovery numbers (`fc536a19c`); those two refreshes are
documented in the document's own preamble and § 6.1 rather than here.
This banner and changelog were added on 2026-08-03, the first
Revision-Policy stub for this document.
