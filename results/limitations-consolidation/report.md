# Limitations consolidation — 55-map VLM burial-mound detection study

**Created**: 2026-04-24 (Session 76).
**Purpose**: Consolidate all substantive limitations of the study into a single paper-citation source, ordered by likely paper-section priority (data quality → methodology → coverage → calibration → process deviations). Each limitation states the finding, the source of truth, the quantification (where available), and the paper-implication framing.

This is a synthesis doc (new in Session 76), not a data-generation pipeline. All limitations cite existing artefacts; no new analyses are conducted here.

## 1. Executive summary

The study has **four first-order limitations** that materially shape what the paper can claim:

1. **v2 verifier contamination** (`archive/v2-verifier-contamination/`): the v2 verifier prompt was calibrated on the gold-standard false-positive set before evaluation, violating held-out evaluation. All v2-on-GS results are quarantined; the paper cites only v1-verifier results.
2. **H10/H12 v1 retracted probe** (`archive/h10-h12-v1-retracted-probe/`): a 2026-04-11 run with `include_example_images: false` on a text-only proposer silently omitted the entire library; the null result was tautological. Data physically moved to archive in Session 75 (commit `52404476`); the clean cross-hypothesis coverage lives in H8 v2 + H12 v2.
3. **Student-GT positional noise and completeness** on the 55-map generalisation corpus: the extended-buffer analysis shows a ~25 – 35 m rightward shift of the 55-map F1 curve relative to the curator-GT gold-standard curve, indicating position noise of that magnitude. Per-candidate human review of the VLM-only candidates finds 45.9 % phantom-TP rate (472 / 1,028 at 50 m) — student GT missed ~10 % of mounds in the VLM-only candidate set. Both effects drag down the uncorrected F1 headline.
4. **Dawid-Skene structural inadequacy on the VLM-only slice** (Obs 273): 2-annotator binary D-S with all items in the same response-pattern class yields AUC = 0.500 regardless of prior. D-S is retained as a preregistered comparator but cannot be used as a per-item discriminator on this slice.

A further **~15 second-order limitations** covering preregistered protocol deviations, coverage gaps in the experimental matrix, and calibration issues are catalogued in §§2 – 7 below. The paper's Limitations section should anchor on §§2 – 5 (first-order); §§6 – 7 are available as supporting citations and scope notes.

**One-line paper claim for the Limitations section opener**: "Four limitations materially shape the claims available from this study: a methodological quarantine of the v2 verifier prompt (calibration-on-test); a methodological retraction of the H10 / H12 v1 library probe (silent library omission); position noise on the 55-map student ground truth (~25 – 35 m empirical shift); and a structural inadequacy of the 2-annotator Dawid-Skene aggregate posterior on the VLM-only candidate slice (AUC = 0.500 by identifiability construction). The first three are fully mitigated by downstream artefacts (v1 verifier citation only; clean H8 v2 / H12 v2 cross-hypothesis replacement; per-candidate human review). The fourth is an inherent scope limit of the preregistered D-S framing."

## 2. First-order limitations (4)

### 2.1 v2 verifier contamination (calibration-on-test)

| Aspect | Value |
|---|---|
| Category | Data quality / methodological integrity |
| Source of truth | `archive/v2-verifier-contamination/README.md`; `docs/methodology/v2-verifier-contamination-policy.md` |
| Obs anchor | Session 73-era quarantine decision; codified in the v2-verifier-contamination-policy doc |
| Quantified | ~100 gold-standard-v2 runs affected; scope is 4-map corpus + Phase 2 verifier-sweep cells |
| Mitigation | v1 verifier retained as paper-citation source; v2 data preserved in `archive/` for methodology transparency |

**Finding**: the v2 verifier prompt was tuned against the gold-standard false-positive set before evaluation. This violates held-out evaluation principle (calibration-on-test). Any metric computed against gold-standard FPs using v2 probabilities is contaminated.

**Paper implication**: the detection-F1 headline at 0.904 (487-tile matrix, K = 30 text-HIGH + PV) uses **verifier v1**, verified during the quarantine process (see `planning/paper-writeup-continuity.md` §Executive state). The headline is not contaminated. All Limitations-section language about v2 should (a) acknowledge the quarantine, (b) confirm the paper-headline numbers are v1-verifier, (c) cite `docs/methodology/v2-verifier-contamination-policy.md` for the full scope.

### 2.2 H10 / H12 v1 retracted probe (silent library omission)

| Aspect | Value |
|---|---|
| Category | Data quality / experimental integrity |
| Source of truth | `archive/h10-h12-v1-retracted-probe/README.md` (added Session 75 2026-04-24) |
| Obs anchor | Obs 235 (Session 74 / 75) |
| Quantified | 7,988 tracked files archived on 2026-04-24; 5 configs × 10 runs affected |
| Mitigation | Clean v2 replacements at `results/h8-v2/` + `results/h12-v2/` (paper-citation sources) |

**Finding**: the 2026-04-11 H10 / H12 v1 library-composition probe used a text-only proposer config with `include_example_images: false`, which silently omitted the entire few-shot library (library is example-image-delivered on the image track; the text-only proposer's equivalent library wasn't transmitted). The null result was tautological — the library was never sent to the API. Seven months passed before detection; archived Session 75 item 2.

**Paper implication**: the paper's library-composition-axis claim rests on **H8 v2** and **H12 v2** (Era 3 re-tests; `gemini-3-flash` proposer with correct library transmission), not on the H10 / H12 v1 probe. Any Limitations-section text about the library-design closure must cite the v2 artefacts and explicitly note the v1 retraction for open-science transparency.

### 2.3 55-map student-GT position noise + incompleteness

| Aspect | Value |
|---|---|
| Category | Data quality / ground-truth precision |
| Source of truth | `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md` (position noise); `results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md` (GT incompleteness) |
| Obs anchors | Obs 260 (GT precision plateau shift), Obs 267 (corrected-F1 headline) |
| Quantified | ~25 – 35 m position noise (from F1-curve rightward shift); 474 / 1,028 ≈ 45.9 % phantom-TP rate on VLM-only slice at 50 m (the student GT missed ~10 % of all mounds that the VLM plus review found: 474 / (4,744 + 474) ≈ 9.1 %) |
| Mitigation | Multi-buffer corrected F1 + per-candidate human review (image track only); gold-standard extended-buffer comparison anchors the position-noise argument |

**Finding**: the 55-map student ground truth has two quality issues:

1. **Position noise**: individual mound-centroid positions on the 55-map student GT are less precise than on the 4-map gold-standard (curator-annotated) GT. The extended-buffer-report empirically quantifies the shift at ~25 – 35 m — at 20 m matching buffer the 55-map F1 is dragged down by ~0.19, at 50 m by ~0.04.
2. **Incompleteness**: 472 (yesterday) + 2 (today) = 474 candidates the VLM flagged at 50 m are confirmed mounds missed by student GT. The student-FN rate on the VLM-only slice is substantial (~72 % empirical; see `dawid-skene-v2-data-driven-prior/report.md` §3).

**Paper implication**: the paper's raw F1 at 20 m on the 55-map corpus (0.506 image, 0.623 text-HIGH, 0.618 text-MIN) **understates** detection quality. The corrected-F1 headline **F1 ≥ 0.830** at 50 m is the conservative lower bound after human review on the image track. The paper's Results section should open with the uncorrected comparison, note the two GT-quality issues as known scope limits, and cite the corrected F1 and extended-buffer analysis as the empirical mitigations.

### 2.4 Dawid-Skene 2-annotator AUC degeneracy (Obs 273)

| Aspect | Value |
|---|---|
| Category | Calibration / methodology |
| Source of truth | `results/55maps-image-generalisation/ds-human-crosstab/report.md`; `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/report.md` |
| Obs anchor | Obs 273 |
| Quantified | AUC = 0.500 on the VLM-only slice regardless of prior (tested across grid of ~100 prior values) |
| Mitigation | Paper uses verifier probability + human review as item-level signals; D-S retained as preregistered comparator with explicit inadequacy-disclosure |

**Finding**: with only two binary annotators (student GT, VLM pipeline) and all VLM-only candidates in the same response-pattern class (student = 0, VLM = 1), the 2-annotator Dawid-Skene model assigns an identical posterior to every item. Item-level AUC is degenerate at 0.500. This is a combinatorial consequence of the preregistered 2-annotator design, not a prior-choice failure — confirmed empirically by sweeping priors across the grid `[0.01, 0.99]` (see §8 of `dawid-skene-v2-data-driven-prior/report.md`).

**Paper implication**: the paper must state that the preregistered D-S analysis is **structurally inadequate for item-level ranking** on the VLM-only slice. The aggregate-rate estimator remains functional with a well-specified prior (at prior = 0.17 the v2 posterior matches the empirical rate to 4 decimals) but per-item ranking requires a third annotator. The paper's per-item confidence reporting uses the verifier probability (also flawed; see §3 below) and the human-review labels.

## 3. Calibration / evaluation limitations (3)

### 3.1 Verifier miscalibration at the high end (Obs 269)

| Aspect | Value |
|---|---|
| Source of truth | `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.md` |
| Obs anchor | Obs 269 |
| Quantified | ECE = 0.2689; AUC = 0.6545 [0.6217, 0.6867]; saturated-high-confidence bin (p = 1.000) correct only 54.9 % of the time |

**Finding**: the VLM verifier's probability output is over-confident above p = 0.30, with the largest gap at p = 1.000 (predicted 1.0 vs empirical 0.549; gap −0.451). Discrimination is modest (AUC = 0.655) and the probability distribution is heavily quantised (13 distinct values across 1,028 candidates).

**Paper implication**: the verifier cannot, on its own, discharge the pipeline's per-candidate confidence estimate. Pipelines relying on a verifier filter must combine it with additional signal (attractor-pull heuristics, consensus vote share, spatial-tolerance guards). The per-symbol Brier breakdown shows the calibration failure is *rejection-specific* (the verifier handles mound sub-classes well but fails to reject non-mounds).

### 3.2 Attractor-pull scale cap at 125 m (Obs 272)

| Aspect | Value |
|---|---|
| Source of truth | `results/55maps-image-generalisation/buffer-band-lift/report.md` |
| Obs anchor | Obs 272 |
| Quantified | Shell permutation p = 0.002 at 100 – 125 m vs p = 0.381 at 125 – 150 m (1,000 permutations, seed 42) |

**Finding**: the attractor-pull effect that underwrites the corrected-F1 framing is statistically distinguishable from within-tile random placement only through the 125 m shell. Beyond 125 m, mounds near detections cannot be attributed to a causal attractor-pull relationship — they are indistinguishable from coincidental within-tile co-occurrences.

**Paper implication**: practitioner tolerance claims beyond 125 m inflate recall in a way the within-tile null cannot distinguish from random placement. The multi-buffer corrected-F1 analysis (`corrected-f1-multi-buffer/report.md`) treats the 150 m row as an upper bound rather than a practitioner-useful operating point. The paper should cite the 125 m cap as the practitioner-useful ceiling.

### 3.3 Review-UI calibration effect — 21 % flip rate one-directional (Obs 263 revision / Obs 268)

| Aspect | Value |
|---|---|
| Source of truth | `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.md` |
| Obs anchors | Obs 263 (revised post-analysis); Obs 268 |
| Quantified | 70 / 327 = 21.41 % flip rate [17.13 %, 25.99 %]; 100 % one-directional (Uncal = mound → Cal = not_mound); ΔF1 impact = −0.0082 |

**Finding**: switching the reviewer-UI from a non-calibrated "fuzzy" interface to a calibrated magenta-50-m-circle overlay tightened reviewer decisions on 21.4 % of the 327-candidate overlap, **always** toward stricter labelling. The calibrated review therefore sets an empirical **lower bound** on the corrected-F1 — no alternative labelling of the overlap within this reviewer's two sessions produces a smaller F1.

**Paper implication**: the paper's corrected-F1 ≥ 0.830 is empirically a lower bound under a conservative reviewer policy. A more permissive reviewer policy would likely push the number higher; the paper cannot quantify that upper bound without a separate review round.

## 4. Methodological / protocol deviations (6)

These are preregistered-vs-executed deviations documented as errata. Each is a scoped limitation.

### 4.1 E4 — Tile bounds Y-axis inversion

| Source | `docs/methodology/preregistration/protocol-errata.md` lines 80+ |
|---|---|
| Quantified | ~2,565 m systematic Y-axis shift on pre-fix bounds |
| Mitigation | Fixed retroactively; early Phase 2a runs (pre-2026-02-05) with shifted bounds identified and re-executed |

**Finding**: an early tile-bounds generation bug shifted all tile bounds one tile height south. Discovered and corrected mid-project. Some early Phase 2a evaluations ran against shifted bounds; those cells were re-executed after the fix.

**Paper implication**: cross-check any Phase 2a figure against the re-executed post-fix evaluation; do not cite pre-fix bounds-affected runs.

### 4.2 E25 — Text-only conditions received example images

| Source | `docs/methodology/preregistration/protocol-errata.md` lines 543+ |
|---|---|
| Quantified | Phase 2a only; corrected from Phase 2b onward |
| Mitigation | Phase 2a H1 Modality (text-only conditions) re-run in later preregistered phases with properly text-only proposer |

**Finding**: the preregistered Phase 2a text-only conditions had images in the few-shot examples (early-discovery configuration bug). Corrected in Phase 2b onward.

**Paper implication**: Phase 2a H1 Modality headline figures (F1 = 0.5518 for brief-text; §3 of `retest-production-summary.md`) should be treated as "text + text-plus-image hybrid" rather than strict text-only baseline. The stricter text-only benchmark is the Era 2 / 3 `gemini-3-flash` text-track runs.

### 4.3 E43 — H11 consensus-384 executed at T = 1.0 instead of T = 0.7

| Source | `docs/methodology/preregistration/protocol-errata.md` lines 1039+ |
|---|---|
| Quantified | 157 downstream references to the UNINTENDED-T1.0 dirs; 487 tiles per run |
| Mitigation | UNINTENDED-T1.0 dirs retained with dual-role framing (origin = error, retention = serendipitous Era 2 T = 1.0 coverage); not archived |

**Finding**: the consensus-384 runs were executed at T = 1.0 due to a YAML-propagation failure; the preregistered setting was T = 0.7. The runs are retained because they provide an independent Era 2 T = 1.0 coverage that the preregistered Phase 2b (340 tiles, T = 1.0) data does not extend to.

**Paper implication**: any cross-reference to the `consensus-384-UNINTENDED-T1.0` or `single-pass-384-UNINTENDED-T1.0` directories must state the T = 1.0 condition came from a preregistered error; scientific T = 1.0 evidence anchors on Phase 2b (Obs 116 / 177 / 209), not E43 data. The `outputs/h11/*/UNINTENDED-T1.0/README.md` banners document the dual-role framing.

### 4.4 E47 — Primary spatial matching buffer reverted to preregistered 20 m

| Source | `docs/methodology/preregistration/protocol-errata.md` lines 1233+ |
|---|---|
| Quantified | Buffer reverted from a temporary 50 m pilot setting back to the preregistered 20 m |
| Mitigation | Primary matching is 20 m throughout the paper; 50 m remains an alternative buffer for specific buffer-sensitivity analyses (extended-buffer + multi-buffer corrected-F1) |

**Finding**: the primary matching buffer was briefly moved to 50 m during a pilot and then reverted to the preregistered 20 m. This is a process clarification; no runs are affected.

**Paper implication**: all primary F1 claims are at the preregistered 20 m matching buffer. The multi-buffer / corrected-F1 / extended-buffer analyses that use 50 m or 125 m explicitly state the deviation and provide the rationale (attractor-pull cap, corrected-F1 lower-bound framing, or GT-precision-noise argument).

### 4.5 E50 – E53 — H10 / H8 / H12 / Phase 3a-HIGH re-runs under production carry-forward

| Source | `docs/methodology/preregistration/protocol-errata.md` lines 1340 – 1670 |
|---|---|
| Quantified | H10: 60 → 327 tile holdout expansion; H8 v2 / H12 v2: 512 px / T = 0.0 / minimal / K = 10 → 384 px / T = 0.7 / HIGH / K = 5; Phase 3a-HIGH: 340 tiles (Era 1) → 487 tiles (Era 2) |
| Mitigation | All deviations documented in errata; post-hoc justifications paired with closure commitments |

**Finding**: four preregistered hypotheses (H10 calibration pool, H8 library, H12 HP:HN, Phase 3a-HIGH image) were re-run under updated production carry-forward parameters, deviating from their preregistered configurations. Justification: the carry-forward configurations reflect downstream paper-relevant pipeline choices that surfaced after preregistration.

**Paper implication**: the Era 3 closure claims (H8 v2, H10 v2, H12 v2 null on library-design axis; Phase 3a-HIGH image on the 487-tile matrix) are preregistered-with-errata claims, not strict-preregistered-plan claims. The paper's Limitations section should explicitly note the scope-shift from preregistration.

### 4.6 E54 — Bootstrap iteration count non-uniform

| Source | `docs/methodology/preregistration/protocol-errata.md` lines 1670+ |
|---|---|
| Quantified | 1,000 iterations for preregistered primary F1; 10,000 for post-hoc narrow-effect analyses (corrected-F1, subtype classification, verifier calibration) |

**Finding**: the preregistered bootstrap iteration count was 1,000. Several post-hoc analyses with narrow effect sizes used 10,000 iterations for tighter CIs.

**Paper implication**: CI widths are comparable within each iteration-count family; direct CI-width comparisons across the two families are not commensurable. The CI metadata registry (`results/ci-metadata-registry.md`) documents every run's bootstrap setting; paper tables should cite per-row iteration count where it varies.

## 5. Coverage / untested cells (3)

### 5.1 No image-vs-text paired permutation test on the 55-map corpus

| Source | `results/55maps-cross-track-comparison/report.md` §5 |
|---|---|
| Quantified | 4 paired permutation tests exist, all text-HIGH vs text-MIN (20 m n.s.; 30 / 40 / 50 m p = 0.0); no image-vs-text paired tests |
| Mitigation | Raw F1 differences are stated; follow-up image-vs-text paired test is a ~10-min CPU task flagged in `55maps-cross-track-comparison/report.md` §9.4 |

**Finding**: cross-modality paired significance testing on the 55-map corpus is not available. Paper claims of the form "image significantly better/worse than text" must cite raw F1 differences + CI overlap, not a formal paired test.

**Paper implication**: limit cross-modality claims to descriptive F1 comparisons until the follow-up paired test is run.

### 5.2 Text-HIGH and text-MIN corrected-F1 not available

| Source | `results/55maps-cross-track-comparison/report.md` §4 |
|---|---|
| Quantified | 0 candidates reviewed for text-HIGH; 0 for text-MIN; 1,028 reviewed for image |
| Mitigation | Paper cites image-track corrected-F1 as the 55-map headline; text tracks use uncorrected F1 |

**Finding**: per-candidate human review was conducted only for the image track (1,028 candidates). text-HIGH and text-MIN have no corrected F1 — their raw F1 is the paper-citable figure.

**Paper implication**: cross-track comparisons must use uncorrected F1 to be apples-to-apples; do not cite the image-track corrected F1 (0.830) against the text tracks' uncorrected F1 (0.759 / 0.788) as a "cross-track leader" claim.

### 5.3 Phase 3a matrix coverage gaps

| Source | `results/phase3a-image-matrix/consensus-analysis-summary.md` §3; `results/phase3a-text-matrix/secondary_effects.md` §10 |
|---|---|
| Quantified | Image-track matrix caps at K = 10 (no K = 30); text-track matrix has K = 30 but the text-HIGH T = 0.0 cell uses K = 3 only (base-rate limit); MINIMAL × T = 0.0 variants sparse |
| Mitigation | K = 10 is the matched-N comparison level across tracks; conclusions at K = 30 apply to text-track only |

**Finding**: the Phase 3a image-track consensus sweep ceils at K = 10. The text-track extends to K = 30 but the cross-track consensus analyses in `results/55maps-cross-track-comparison/report.md` use K = 5 (matched to the 55-map generalisation pipeline). Full K = 30 comparison across modalities is not available.

**Paper implication**: any paper claim of the form "consensus at K = 30 is better than K = 10" is text-track-specific. Cross-modality consensus claims should use the K = N = 10 matched-N level.

## 6. Process limitations (2)

### 6.1 Single human reviewer on the 55-map human-review

| Source | `results/55maps-image-generalisation/human-review.csv` + `human-review-multi-buffer.csv` |
|---|---|
| Quantified | 1 reviewer, 2 sessions (uncalibrated UI → calibrated UI; see Obs 263/268) |
| Mitigation | 21.4 % flip rate under calibrated UI quantifies *within-reviewer* UI-induced calibration variability; inter-reviewer variability is out of scope |

**Finding**: all 1,028 VLM-only human-review labels come from a single reviewer (the PI), across two sessions with a UI upgrade mid-review. Inter-reviewer agreement is not tested on this slice.

**Paper implication**: the corrected-F1 lower bound is specific to this reviewer's calibrated-UI labelling policy. A different reviewer under the same UI might produce different labels; the paper cannot quantify the between-reviewer variance.

### 6.2 Flawed audit (2026-04-19) corrections log

| Source | `archive/flawed-audit-2026-04-19/NOTE.md`; fresh audit at `verification-2026-04-21.md` |
|---|---|
| Quantified | 82 / 85 claims in the flawed audit confirmed PASS under the fresh audit; 3 claims superseded |
| Mitigation | Original audit archived; paper-citation audit is the 2026-04-21 re-run |

**Finding**: the initial 2026-04-19 documentation audit contained hallucinated cost figures, conflated runs with similar names, and misattributed observations. A fresh-context audit on 2026-04-21 confirmed 82 / 85 claims; 3 were corrected.

**Paper implication**: the paper's numeric claims cite the `results/documentation-audit/` (2026-04-21) as the authoritative inventory; the flawed 2026-04-19 audit is preserved for transparency but not cited.

## 7. Preserved-but-superseded data (2)

### 7.1 Pre-retest Phase 2b pilot data (60-tile K = 10 runs, 2026-02-09)

| Source | `archive/outputs-pre-retest-60-tile/phase2b/` |
|---|---|
| Quantified | 6 orphan pre-retest phase2b pilot docs archived Session 74 (commit `16ee3ae5`); 5 configs in the pilot |
| Mitigation | Paper cites the 340-tile K = 3 retest (Session 75 Phase 2b doc at `results/retest/phase2b/analysis_summary.md`); pre-retest data retained for open-science transparency |

**Finding**: Phase 2b was first run as a 60-tile K = 10 pilot on 2026-02-09 before the full 340-tile K = 3 retest. The pilot results are preserved but superseded.

**Paper implication**: paper-citable Phase 2b F1 numbers are from the 340-tile retest; pilot figures are not cited.

### 7.2 UNINTENDED-T1.0 retention (see §4.3)

Covered under E43 above; retention framing documented in the `outputs/h11/*/UNINTENDED-T1.0/README.md` banners.

## 8. Suggested priority ordering for the paper's Limitations section

Highest-impact to lowest:

1. **§2.3 Student-GT position noise + incompleteness** — materially shifts every per-corpus F1 claim; requires explicit mitigation (corrected-F1 + extended-buffer argument).
2. **§2.4 Dawid-Skene 2-annotator inadequacy** (Obs 273) — the preregistered aggregate method is structurally unable to rank items on the VLM-only slice.
3. **§2.1 v2 verifier contamination** — methodology-transparency requirement; paper-headline v1-verifier is clean.
4. **§3.1 Verifier miscalibration** (Obs 269) — weakens the per-candidate confidence story; cites the verifier-calibration artefact.
5. **§3.2 Attractor-pull 125 m cap** (Obs 272) — practitioner-tolerance scope limit.
6. **§2.2 H10 / H12 v1 retraction** — transparency; mitigated by v2 artefacts.
7. **§4 Methodological deviations (E1–E54)** — scope + preregistered framing; each noted individually where relevant.
8. **§5 Coverage gaps** — follow-up-ready, not blocking.
9. **§6 Process limitations** + **§7 Preserved-but-superseded** — transparency + archive policy.

## 9. Paper text (suggested Limitations section)

> This study has several limitations that shape the available claims. First, the 55-map student ground truth has empirical position noise of approximately 25 – 35 m (quantified by comparing the F1-curve plateau shift between the 4-map curator-annotated gold-standard corpus and the 55-map student corpus; see Supplementary extended-buffer analysis) and is incomplete: per-candidate human review of the 1,028 VLM-only candidates at 50 m matching tolerance finds 45.9 % (472 / 1,028) to be confirmed mounds missed by the student GT. The uncorrected F1 at 20 m on the 55-map corpus therefore understates detection quality; the corrected F1 at 50 m after human-review rescue is the conservative paper-citation figure (F1 ≥ 0.830).
>
> Second, the preregistered Dawid-Skene (D-S) aggregate-posterior analysis is structurally unable to rank individual VLM-only candidates on this slice. With two binary annotators (student GT, VLM pipeline) and all VLM-only candidates in the same `(student = 0, VLM = 1)` response-pattern class, D-S assigns an identical posterior to every item by identifiability construction, yielding item-level AUC = 0.500 regardless of the prior on student false-negative rate. We retain D-S as a preregistered comparator and explicitly flag its inadequacy for per-item ranking on the VLM-only slice.
>
> Third, a v2 verifier prompt was calibrated against the gold-standard false-positive set before evaluation, violating held-out evaluation principle (calibration-on-test). All v2-on-gold-standard results are quarantined under `archive/v2-verifier-contamination/`. All paper-cited verifier probabilities and derived calibration metrics use v1-verifier results, which were not exposed to gold-standard FPs during development.
>
> Fourth, the VLM verifier is miscalibrated in the over-confident direction (Expected Calibration Error = 0.269; AUC = 0.655 on the VLM-only slice; saturated-high-confidence `p = 1.0` predictions are correct 54.9 % of the time). The pipeline therefore cannot rely on verifier probability alone for per-candidate confidence; paper results use the combination of verifier probability + spatial attractor-pull + human review.
>
> Beyond these first-order limitations, the study has several methodological caveats documented in full in Supplementary Limitations: an attractor-pull scale cap at 125 m (tolerance claims beyond this distance are indistinguishable from random within-tile co-occurrences); a 21.4 % one-directional flip rate under calibrated-UI review (conservative reviewer policy sets the corrected-F1 as a lower bound); preregistered-vs-executed protocol deviations (errata E4 – E54); and coverage gaps including no paired image-vs-text permutation test on the 55-map corpus, no corrected-F1 for the text tracks, and a Phase 3a image-track consensus ceiling at K = 10. Each limitation is mitigated or scope-limited by downstream artefacts cited in the paper's Methods and Results.

## 10. Files manifest

**Outputs (this directory)**:

- `report.md` — this consolidation report (synthesis, new 2026-04-24 Session 76).

**Source artefacts cited (selection)**:

- `archive/v2-verifier-contamination/README.md` — v2 quarantine.
- `archive/h10-h12-v1-retracted-probe/README.md` — Session 75 retraction.
- `archive/flawed-audit-2026-04-19/NOTE.md` — prior audit retraction.
- `archive/outputs-pre-retest-60-tile/phase2b/` — pre-retest pilot data.
- `docs/methodology/v2-verifier-contamination-policy.md` — quarantine policy.
- `docs/methodology/preregistration/protocol-errata.md` — E1 – E54 errata register.
- `docs/notes/reflections/working-notes.md` §Obs 260 / 263 / 267 / 268 / 269 / 272 / 273.
- `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md` — corrected-F1 lower bound.
- `results/55maps-image-generalisation/corrected-f1-multi-buffer/report.md` — multi-buffer corrected F1.
- `results/55maps-image-generalisation/buffer-band-lift/report.md` — attractor-pull cap (Obs 272).
- `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.md` — review-UI flip rate.
- `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.md` — verifier miscalibration.
- `results/55maps-image-generalisation/ds-human-crosstab/report.md` — D-S v1 inadequacy.
- `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/report.md` — D-S v2 inadequacy confirmation.
- `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md` — position-noise quantification.
- `results/55maps-cross-track-comparison/report.md` — cross-track gaps.
- `results/meta-findings-summary.md` — Theme T1 – T5 synthesis.
- `results/ci-metadata-registry.md` — bootstrap iteration-count registry.

## 11. Reproducibility

This is a synthesis doc. All limitations are derivable from the source artefacts cited in §10; no new analyses were run for this consolidation. To refresh: re-read the source artefacts and update any limitation where the underlying finding has moved since the 2026-04-24 synthesis date.

**Level-up / regeneration cadence**: this doc should be touched only when a new first-order limitation is discovered or when an existing limitation's mitigation changes status (e.g., the image-vs-text paired test is eventually run, which would move §5.1 from "not available" to "resolved").

**Toolchain**: hand-authored synthesis; no scripted regeneration.
