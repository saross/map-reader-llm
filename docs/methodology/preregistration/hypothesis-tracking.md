# Hypothesis Tracking Matrix

**Purpose**: Map preregistered hypotheses to their experimental conditions, configs, and status.

**Last updated**: 2026-07-28 (D17 audit corrections: H2-C note, H6 row, H9
status — see `reports/d17-inventory/prereg-attribution-sweep.md` FALSE-2, S7,
U12)

**Last regenerated**: 2026-08-28 (Session 143). Every status row in the two
summary tables below was re-verified **at source** in this pass — each row
carries the file path, and where practical the line or figure, it was read
from. Rows that could not be verified are marked `unverified` rather than
asserted.

> **Caution**: this file has carried stale and invented content (D17 audit,
> 2026-07-28) and should be **generated, not hand-maintained** — see
> `planning/audit-and-completion-plan.md` § 5. Verify against
> `osf/preregistration.md` and the manifests before citing.
>
> The 2026-08-28 pass does not lift that caution. It corrects the summary
> tables against source, but the file remains hand-maintained and will drift
> again. The **authoritative** hypothesis-disposition record is the generated
> table at `results/hypothesis-outcome-table/hypothesis-outcome-table.md`
> (projected from `results/analyses-manifest.json`, "GENERATED FILE — do not
> hand-edit"). Where this file and that one disagree, **believe the generated
> table**.

---

## Confirmatory Hypotheses (H1-H8)

Statuses and the family BH-FDR column are transcribed from the generated
ledger `results/hypothesis-outcome-table/hypothesis-outcome-table.md`
(read 2026-08-28), which projects `results/analyses-manifest.json`. The
"Verified at" column names the artefact read for this row.

| ID | Hypothesis | Factor | Phase | Status | Family BH-FDR | Verified at (2026-08-28) |
|----|------------|--------|-------|--------|---------------|--------------------------|
| H1 | Modality/Elaboration Level | M/E | 2a | Executed | not rejected | ledger H1 row |
| H2 | Two-Stage Pipelines | Architecture | 3c/3d | **Partially executed** — Condition C (fine-to-coarse) never run (E59) | rejected (q=0.05) | ledger H2 row; errata E58, E59 |
| H3 | Consensus Voting | N, threshold | 3a | Executed | rejected (q=0.05) | ledger H3 row |
| H4 | Example Ordering | Ordering | 2e | Executed — no significant effect (0/6 after FDR) | not rejected | `results/phase2e-carry-forward-parameters.md` § Results Summary |
| H5 | Negative Text Treatment | Text level | 2d | Executed | not rejected | ledger H5 row |
| H6 | Flash→Pro Transfer | Model | 4 | **Not executed — formally CLOSED disclose-only** (PI ruling 2026-08-24) | excluded: never run | errata E74 § RULING; ledger H6 row |
| H7 | Temperature | T | 2b | Executed — T=0.0 optimal both tracks | rejected (q=0.05) | `results/retest/phase2b-track{1,2}-evaluation.json` |
| H8 | Library Composition/Scaling | Library size | 2c | Executed — v2 rerun NULL (0 of 7 contrasts significant after BH-FDR) | not rejected | `results/h8-v2/analysis_summary.md` § Headline result |

---

## Exploratory Hypotheses (H9-H15)

| ID | Hypothesis | Factor | Tier | Status | Verified at (2026-08-28) |
|----|------------|--------|------|--------|--------------------------|
| H9 | Diversity Mechanisms | Text/Image/Temp diversity | A | **Executed — H9 REJECTED (null).** All five registered conditions A–E ran on Track 1; A/B/D/E on Track 2 (C is degenerate without example images). Corrected 2026-08-28: the previous "H9-D only; H9-B/C/E not run" row was **false** — see § H9 below | `results/phase3c-diversity/phase3c-comprehensive-results-report.md` §§ 1.1, 2.1–2.3; 225 metas under `outputs/retest/phase3c/`; errata E63; ledger H9 row |
| H10 | Training Pool Size | Pool size | B | **Executed — v2 rerun NULL.** Corrected 2026-08-28 (was "Not started") | `results/h10/analysis_summary.md` § Headline result; errata E49, E50 |
| H11 | Tile Size Effects | Tile dimensions | B | Executed (384 pathway closed) | ledger H11 row |
| H12 | HP:HN Ratio | Hard example ratio | B | **Executed — v2 rerun NULL** (3-way, BH-FDR q=0.05). Corrected 2026-08-28 (was "In progress") | `results/h12-v2/analysis_summary.md` § 2; errata E52 |
| H13 | Overlap/Stride Effects | Tile overlap | B | **Executed — registered three-arm contrast ran 2026-08-17/18.** F1 falls monotonically as overlap rises. Corrected 2026-08-28 (was "Not started"). Extended by three later post-hoc campaigns — see § H13 below | `results/h13-overlap-2026-08-18/findings.md` § The headline; errata E75 § Disposition; ledger H13 row |
| H14 | Cross-Model Consistency | Provider | C | Not executed — registered as deferred and honoured | errata E76; ledger H14 row |
| H15 | Cross-Model Voting | Multi-provider voting | C | Not executed — registered as deferred, gated on H14 | errata E77; ledger H15 row |

---

## Detailed Condition Mapping

### H1: Modality/Elaboration Level (Phase 2a) — COMPLETE

Tests how text presence and detail level affect detection performance.

**Status (2026-02-08)**: Phase 2a complete. Optimal modality/elaboration level
identified and carried forward into subsequent phases.

| Condition | M/E Level | Text | Images | Config File | Instruction File |
|-----------|-----------|------|--------|-------------|------------------|
| H1-1 | Image-only | Minimal | Yes | `detect_image-only.json` | `detect_image-only.md` |
| H1-2 | Brief-text | Brief | No | `detect_brief-text.json` | `detect_brief-text.md` |
| H1-3 | Brief-text+image | Brief | Yes | `detect_brief-text-image.json` | `detect_brief-text-image.md` |
| H1-4 | Verbose-text | Verbose | No | `detect_verbose-text.json` | `detect_verbose-text.md` |
| H1-5 | Verbose-text+image | Verbose | Yes | `detect_verbose-text-image.json` | `detect_verbose-text-image.md` |

---

### H2: Two-Stage Pipelines (Phase 3c/3d) — COMPLETE

Tests whether two-stage architectures improve over single-stage detection.

**Status (2026-03-11)**: Complete. The preregistered null prediction (two-stage
will not improve) was **contradicted** with large effect size. Phase 3c pilot
exceeded the GO criterion (ΔF1 ≥ 0.05) by a 2× margin, achieving +0.09 to
+0.14 F1 improvement with proposer-verifier architecture.

Phase 3d triggered exploratory extensions were comprehensive:

- Phase 3c pilot (Session 43): 3 verifier strategies × 2 tracks
- Phase 3d Experiments A–D (Sessions 44–48): provenance preamble, visual
  examples, temperature sweeps, cascaded verification
- Phase 3d Experiment E (Session 48): text proposer ablation — negative result
  confirming baseline is near capability frontier
- H11 factorial (Session 50): 3 strategies × 2 tracks at 384 tiles

**Best result**: F1=0.796 (adversarial verifier, text-only, 512 tiles) — but
see Observation 163 regarding model drift and the corrected v2 result
(F1=0.732) obtained after config audit.

| Condition | Architecture | Verifier Strategy | Best F1 |
|-----------|--------------|-------------------|---------|
| Single-stage baseline | N/A | N/A | 0.660 |
| Proposer-verifier | Coarse-to-fine | Adversarial (text-only) | 0.732 (v2 corrected) |
| Proposer-verifier | Coarse-to-fine | Standard (text-only) | 0.768 (pre-correction) |
| Proposer-verifier | Coarse-to-fine | Checklist (text-only) | 0.782 (pre-correction) |

**Note**: Fine-to-coarse (H2 Condition C, `osf/preregistration.md:469`) was
**not executed**, and no decision to drop it is on record (asked twice on
2026-03-07, unanswered — see
`reports/d17-inventory/step0-fine-to-coarse-archaeology.md`). This is an
unexecuted registered confirmatory condition and requires a Deviation-class
erratum. An earlier note here claimed it was deprioritised because "the
coarse-to-fine results were strong enough"; that reasoning is invalid under
the registered design — the registration predicted *neither* architecture
would help, so a strong coarse-to-fine result falsifies the prediction and is
the registered trigger to pursue two-stage architectures further, not to stop
(corrected 2026-07-28, D17 audit FALSE-2).

---

### H3: Consensus Voting (Phase 3a) — COMPLETE

Tests voting pool sizes and thresholds. No separate configs — voting is
post-hoc analysis.

**Status (2026-03-07)**: Complete. Consensus voting confirmed to improve over
single-run baseline for both tracks. N=30 at T=0.7 optimal. Detailed results
in `results/phase3a-consensus/`.

**Note (2026-03-15)**: The Phase 3a metadata files in `track2-text-high/`
incorrectly record `thinking_level: minimal` due to a metadata-recording bug
(the script captured the config file default rather than the actual API
parameter). The directory label "HIGH" is correct — the runs did use HIGH
thinking at the API level (see Observation 141). A clean replication
(2026-03-15) with properly controlled configs confirmed the direction:
HIGH F1=0.735 vs minimal F1=0.699 (+3.6 pp).

| Pool Size | Source | Thresholds Tested |
|-----------|--------|-------------------|
| N=5 | Runs 1-5 or 6-10 | 1, 2, 3, 4, 5 |
| N=10 | All 10 runs | 1, 2, ..., 10 |
| N=30 | Extended (20 additional runs) | 1, 2, ..., 30 |

---

### H4: Example Ordering (Phase 2e) — COMPLETE

Tests positioning of canonical vs hard examples.

**Status (2026-02-12)**: Complete. No significant ordering effect after FDR
correction. Config-default (canonical-first) ordering carried forward.

| Condition | ID | Canonical Position | Config Pattern |
|-----------|----|--------------------|----------------|
| Canonical-first | H4-A | First (positions 1-6) | `detect_*.json` (base configs) |
| Canonical-last | H4-B | Last (final positions) | `detect_*_canonical-last.json` |
| Random | H4-C | Shuffled | `detect_*_random-order.json` |

**Triggered exploratory (H4b)**: If H4 significant, test HP-first vs HN-first
ordering within hard block. **Not triggered** — H4 showed no significant
effect (2026-02-12).

---

### H5: Negative Text Treatment (Phase 2d) — COMPLETE

Tests whether exclusion guidance text in the system instruction reduces false
positives. Three levels tested at the carried-forward optimal M/E per track
(OFAT, not full factorial). See Decision 17 and Erratum E28.

**Status (2026-02-12)**: Complete. H5=minimal optimal for both tracks. Carried
forward to subsequent phases.

**Instruction text adaptation**: Terse and verbose instruction files were
modified to remove references to non-existent HN reference images (HN
excluded after Phase 2c). Exclusion *descriptions* (what not to detect)
retained as domain knowledge. Minimal instruction unchanged (serves as
baseline from prior phases).

| Condition | H5 Level | Exclusion Text | Track 1 Config (image) | Track 2 Config (text-only) |
|-----------|----------|----------------|------------------------|---------------------------|
| H5-A | Minimal | No exclusion text | `library_plus-hp.json` | `detect_brief-text.json` |
| H5-B | Terse | Brief "do not mark" list | `library_plus-hp_terse.json` | `detect_brief-text_terse.json` |
| H5-C | Verbose | Detailed per-type criteria | `library_plus-hp_verbose.json` | `detect_brief-text_verbose.json` |

**Dual-track OFAT design** (4 net new cells, 2 per track):

| Track | M/E Level | H5=Minimal | H5=Terse | H5=Verbose |
|-------|-----------|------------|----------|------------|
| Track 1 (image) | brief-text-image | Reuse Phase 2c | **New** | **New** |
| Track 2 (text) | brief-text | Reuse Phase 2b T=0.0 | **New** | **New** |

**Preregistered design was**: 3×3 factorial (3 image-using M/E × 3 H5).
Simplified to single-factor OFAT at carried-forward M/E per Decision 17.

---

### H6: Flash→Pro Transfer (Phase 4) — NOT EXECUTED; formally CLOSED

Tests whether Flash-optimal config transfers to Pro. OFAT sensitivity testing.
This is the only confirmatory hypothesis with no result.

**Status (2026-08-24, verified at source 2026-08-28)**: none of the registered
four-phase transfer protocol was executed (erratum **E74**). The PI ruled
disclose-only — quoting the erratum's RULING paragraph: "**disclose-only — H6
is formally CLOSED as not-executed; the ~US$48 re-run will not be run.**" H6
was excluded from, and disclosed as excluded from, the family BH-FDR, which
ran over m = 7 (`results/hypothesis-outcome-table/hypothesis-outcome-table.md`,
H6 row: "— (excluded: never run)").

The Pro work that does exist is an exploratory extension, not H6 (E41,
corrected under E57). The four registered OFAT factors below were therefore
never evaluated under the registered protocol.

| Factor | Tests | Decision Rule |
|--------|-------|---------------|
| M/E | 2 adjacent levels | Adjust if Δ ≥ 0.03 F1 |
| H5 | 2 alternatives | Adjust if Δ ≥ 0.03 F1 |
| T | 2 adjacent temperatures | Adjust if Δ ≥ 0.03 F1 |
| O | 2 alternative orderings | Adjust if Δ ≥ 0.03 F1 |

---

### H7: Temperature (Phase 2b) — COMPLETE

Tests temperature effect on detection performance.

| Condition | Temperature | Rationale |
|-----------|-------------|-----------|
| H7-1 | 0.0 | Minimum (deterministic) |
| H7-2 | 0.3 | Low variance (evidence for visual detection) |
| H7-3 | 0.7 | Moderate variance |
| H7-4 | 1.0 | Vendor default |
| H7-5 | 1.3 | Above default |

**Temperature is a runtime parameter** — no separate config files needed.

**Result (2026-02-08)**: T=0.0 optimal for both tracks. FDR-significant pairwise
differences: 6/10 comparisons (Track 1), 4/10 comparisons (Track 2). T=0.0 carried
forward as the optimal temperature setting for subsequent phases.

---

### H8: Library Composition and Scaling (Phase 2c) — COMPLETE

Tests library component effects and scaling.

**Status (2026-02-09)**: Phase 2c complete (Track 1 image-using only; Track 2
text-only skipped because library composition is inherently visual). plus-hp
selected as optimal library (F1=0.609). No pairwise comparisons significant
after FDR correction, but consistent directional gradient: more positive
examples = better performance. Carried forward to Phase 2d.

| Condition | ID | Canon+ | Canon- | HP | HN | Null | Total | Config File |
|-----------|----|--------|--------|----|----|------|-------|-------------|
| Pure Positive Canon | H8-1 | 4 | 0 | 0 | 0 | 3 | 7 | `library_pure-positive-canon.json` |
| Canonical | H8-2 | 4 | 2 | 0 | 0 | 3 | 9 | `library_canonical.json` |
| +HP | H8-3 | 4 | 2 | 4 | 0 | 3 | 13 | `library_plus-hp.json` |
| Scale-4 | H8-4 | 4 | 2 | 2 | 2 | 3 | 13 | `library_scale-4.json` |
| Scale-8 | H8-5 | 4 | 2 | 4 | 4 | 3 | 17 | `library_scale-8.json` |
| Scale-16 | H8-6 | 4 | 2 | 8 | 8 | 3 | 25 | **DEFERRED** |
| Scale-32 | H8-7 | 4 | 2 | 16 | 16 | 3 | 41 | **DEFERRED** |

**Note (2026-02-02, SUPERSEDED — see the v2 status below)**: Scale-16 and Scale-32 are
deferred because the HP pool is structurally exhausted at 4 recognition failures
(>50m threshold). These conditions collapse to Scale-8 under the 1:1 HP:HN constraint.
Deferred to post-H10 when calibration tile expansion may yield additional recognition
failures. See Decision 11 in decisions-log.md.

**v2 status (2026-04-15, verified at source 2026-08-28)**: the deferral above was
resolved. Erratum **E51** re-mined 108 hard positives under a v2 definition, re-enabling
Scale-16 and Scale-32, and H8 was re-run in full under production carry-forward settings
(384 px, K = 5, 327-tile Era 3 scope). **All seven preregistered contrasts are null after
Benjamini–Hochberg FDR at q = 0.05**; the seven conditions cluster in a 0.693–0.733 F1
band with fully overlapping 95 % bootstrap CIs, and the smallest raw p is 0.164
(`results/h8-v2/analysis_summary.md` § Headline result). Three of the six registered
directional predictions point the wrong way within noise. The two rows marked
**DEFERRED** in the table above therefore *were* executed in v2, as Scale-16
(F1 = 0.693) and Scale-32 (F1 = 0.713); the planned contrasts S2 and S3 struck through
below were likewise executed and are null.

**Planned contrasts**:

- C1: Pure Positive Canon → Canonical (Canon- effect)
- C2: Canonical → +HP (HP effect)
- C3: +HP → Scale-8 (HN effect)
- S1: Scale-4 → Scale-8 (initial scaling)
- ~~S2: Scale-8 → Scale-16 (mid scaling)~~ — deferred (post-H10)
- ~~S3: Scale-16 → Scale-32 (ceiling)~~ — deferred (post-H10)
- B1: +HP vs Scale-4 (composition at matched size)

---

### H9: Diversity Mechanisms (Phase 3c — Exploratory) — EXECUTED; H9 REJECTED

Tests whether diversity in prompts, images, or temperature improves voting.

**Status (corrected 2026-08-28, Session 143 — the previous status was
factually wrong)**: H9 was **executed as registered**, and the registered
conditions returned a **null**. The 2026-07-28 status recorded here — "the
formal H9-A through H9-E conditions were never run as separate experiments" —
is contradicted by every primary artefact, and is withdrawn.

**What was actually run.** The dual-track Phase 3c design covers Track 1
(image) conditions A, B, C, D, E and Track 2 (text-only) conditions A, B, D, E
— C is omitted on Track 2 because image rotation is degenerate when
`include_example_images=false`
(`results/phase3c-diversity/phase3c-comprehensive-results-report.md` § 1.1).
Each condition has five sub-conditions × five replications: 125 execution
units on Track 1, 100 on Track 2 (§ 1.5). The filesystem agrees — all five
`h9-A`…`h9-E` condition directories exist under
`outputs/retest/phase3c/track1-image/`, and the tree carries 225 `*.meta.json`
files. Erratum **E63** independently records the same scope: "all five track-1
conditions (h9-A through h9-E) and all four track-2 conditions … across all
225 passes", executed 2026-03-18 to 2026-03-25.

The registered design was run **twice**: a 60-tile pilot (report dated
2026-03-08) and a 340-tile Era-1 retest with cross-variant pooling
(`results/analyses-manifest.json`, analysis `phase3c-diversity-calibration`).

**The result — H9 rejected on both runs.** No diversity condition beats the
identical-pass baseline A on either track:

| Track | B vs A | C vs A | D vs A | E vs A |
|-------|-------|-------|-------|-------|
| 1 (image), 60-tile pilot | −0.009 (p=0.816) | +0.004 (p=0.942) | +0.014 (p=0.626) | −0.000 (p=1.000) |
| 2 (text), 60-tile pilot | −0.035 (p=0.121) | n/a | −0.034 (p=0.496) | −0.038 (p=0.245) |

ΔF1 against baseline, paired permutation
(`phase3c-comprehensive-results-report.md` § 2.3, Table 2.2). The 340-tile
retest reaches the same verdict: "H9 is REJECTED: at the best-F1@20m operating
point each diverse condition is statistically indistinguishable from the
identical-pass baseline A" (`results/analyses-manifest.md`, line 17).

The **preregistered advance criterion** ("Any diversity mechanism
significantly improves F1 over baseline") is recorded as **not met**, so no
further diversity exploration was triggered (§ 2.4).

**Two riders that must accompany any report of this null** (erratum E63
§ Protocol impact): (a) the runs executed at HIGH thinking, not the registered
`minimal`; (b) HIGH thinking is itself a diversity mechanism (Obs 140), so the
H9 baseline is not a low-diversity baseline and the null may be biased toward
acceptance. Erratum **E12** additionally records that H9-C ran as
HN-diversity-only, the HP channel being frozen by pool exhaustion.

Note the standing tension with the post-registration **diversity-dividend**
finding: a diversity mechanism H9 did not register (thinking level) *does*
improve consensus substantially (`results/diversity-dividend-384/`). That is a
separate, post-hoc result and must not be merged into the H9 claim.

#### Provenance of the withdrawn status — how the error propagated

⚠ Recorded so the same error is not reintroduced. This file asserted, from
2026-03 onwards, that the A–E conditions "were not run as separate
experiments". The D17 audit finding **U12**
(`reports/d17-inventory/prereg-attribution-sweep.md:1007-1036`, 2026-07-28)
audited that claim *against the file's own text* rather than against the
experiment's artefacts, accepted it, and proposed the wording "Partially
tested (H9-D only; H9-B/C/E not run)" — which was then written in here.

A **different D17 document, dated one day earlier**, had already caught it:
`reports/d17-inventory/d17-inventory-h9-h12.md` § 7, item 1 states that the
tracking matrix says the conditions "were not run as separate experiments.
They were — twice. **Believe the artefacts**". E63 (2026-07-30) then documented
the 225-pass execution in detail. U12 is therefore superseded on this point by
both an earlier and a later source.

⚠ **Known downstream contamination**: the U12 wording appears to have
propagated into the paper draft at `docs/paper/results-draft.md:214-219`,
which states that "registered H9-B/C/E — text and image diversity — were never
run, D17 audit U12". That sentence is incorrect and needs revision. The
substantive conclusion (H9 rejected) is unaffected. Correcting the paper draft
is **outside this pass's write scope** and is flagged for action.

#### PI ruling of 2026-08-28 — recorded, NOT applied

On 2026-08-28 the PI ruled, in session: "**Tier A: I approve disclose only**"
— the intent being that H9-B/C/E would be disclosed as not-run-as-registered,
with the Phase 3c cross-variant evidence standing in, and that a disclose-only
erratum would be minted on the E74 precedent.

**That ruling has not been applied, and no erratum was minted.** The ruling
rests on the premise that H9-B/C/E were not executed. Section § H9 above
establishes at source that they **were** executed — the premise is false, so
there is no omission to disclose. Minting an erratum asserting a
non-existent omission would put a false claim into the permanent protocol
record, which is a worse defect than the stale tracking row it was meant to
close.

The ruling is recorded here as a fact of the project's decision trail, and is
**referred back to the PI** for a decision on the corrected facts. If the PI
still wants an errata entry, the defensible subject is the *documentation*
defect — that this file and `docs/paper/results-draft.md` carried a false
"not executed" claim for H9 between 2026-07-28 and 2026-08-28 — not a protocol
omission. Session 143 declined to mint that entry unprompted.

| Condition | Text | Images | Temperature | Description |
|-----------|------|--------|-------------|-------------|
| H9-A | Fixed | Fixed | Fixed | Baseline (identical passes) |
| H9-B | Varied | Fixed | Fixed | Text diversity only |
| H9-C | Fixed | Varied | Fixed | Image diversity only |
| H9-D | Fixed | Fixed | Varied | Temperature diversity only |
| H9-E | Varied | Varied | Varied | Full diversity |

**Note (2026-02-02)**: H9 runs as **HN-diversity-only** for image diversity (H9-C).
HP channel is frozen: 4 slots, 4 examples, every HP appears in every pass. Only HN
examples rotate across passes. HP diversity is untestable due to pool exhaustion (only
4 recognition failures exist). HN rotation is the more important diversity dimension
given that FPs outnumber FNs ~23:1. See Decision 11 in decisions-log.md.

---

### H10: Training Pool Size (Exploratory Tier B) — EXECUTED; NULL

**Status (corrected 2026-08-28; was "Not started (HP pool exhausted)")**. The
v1 arm was formally retracted (Obs 235, 2026-04-14) because the proposer config
ran `include_example_images: false`, so the few-shot library never reached the
API. The **v2 rerun** (launched and evaluated 2026-04-15) resolved the original
HP-pool-exhaustion deferral by re-mining the pool, and returned a null.

Four nested calibration pools (20 ⊂ 40 ⊂ 80 ⊂ 160) give post-verifier F1s
indistinguishable within sampling noise: pool_020 0.727 → pool_160 0.722,
ΔF1 +0.005, p = 0.845, not significant
(`results/h10/analysis_summary.md` § Headline result). Errata: **E49**
(cold-start production config substituted for the preregistered image-only
baseline) and **E50** (holdout expanded from 60 to 327 tiles).

---

### H12: HP:HN Ratio (Exploratory Tier B) — EXECUTED; NULL

**Status (corrected 2026-08-28; was "In progress — h12-v2")**. The v2 rerun
(runs launched 2026-04-15, summary dated 2026-04-16) is complete. Three
conditions — R1 HN-heavy 2:6, R2 balanced 4:4, R3 HP-heavy 6:2 — at 384 px,
K = 5 consensus, on the 327-tile Era 3 scope.

**Three-way null after BH-FDR at q = 0.05.** All three preregistered pairwise
contrasts are non-significant (adjusted p 0.500–0.717); all condition F1s fall
in 0.688–0.717 with fully overlapping 95 % bootstrap CIs
(`results/h12-v2/analysis_summary.md` § 2). The registered directional
prediction is falsified rather than merely unsupported: R3 (HP-heavy) is
directionally the *worst*, and recall is near-identical across all three.
Erratum: **E52**.

**Library axis closed.** H8 v2, H10 v2, and H12 v2 all return nulls under
production carry-forward settings; the 45-pair cross-hypothesis permutation
matrix confirms zero significant pairwise differences (min adjusted
p = 0.966) — `results/cross-hypothesis-library/permutation-t4/fdr_summary.json`,
as cited in `results/h12-v2/analysis_summary.md` § 1.

---

### H13: Overlap/Stride Effects (Exploratory Tier B) — EXECUTED (registered design)

**Status (corrected 2026-08-28; was "Not started (low priority)")**. The
registered three-arm contrast (`osf/preregistration.md:1014-1048`: A = 64 px /
stride 448 / 12.5 %, B = 128 px / 384 / 25 %, C = 256 px / 256 / 50 %) **was
executed**. Erratum **E75** originally disclosed the contrast as silently
dropped; its Disposition paragraph (2026-08-18, Sessions 135–136) records the
omission as "closed by execution, not by disclosure alone". Arms B and C ran
2026-08-17/18; arm A was re-scored from its committed Phase 2a `brief-text`
detections rather than re-run, so **the committed arm-A F1 values are
superseded**. Actual spend US$5.7488 against a $4.37 gate estimate (+31 %,
flagged to the PI).

All three registered analyses are reported in
`results/h13-overlap-2026-08-18/findings.md`:

| Arm | Overlap | Stride | Precision | Recall | F1 |
|---|---|---|---:|---:|---:|
| A | 12.5 % | 448 px | 0.4484 | 0.7379 | 0.5578 |
| B | 25 % | 384 px | 0.3887 | 0.7844 | 0.5198 |
| C | 50 % | 256 px | 0.2616 | 0.8717 | 0.4025 |

**Prediction split** — the registered *mechanism* is confirmed, the registered
*performance* claim is falsified. F1 falls monotonically as overlap rises; all
three paired contrasts exclude zero. Recall behaves as registered
(0.7379 → 0.7844 → 0.8717) but precision falls faster. The registered
edge-detection analysis confirms and localises the mechanism: the ten mounds
arm A could only ever see within 100 m of a tile edge go from recall 0.2667 (A)
to 0.9333 (C), against 0.7468 → 0.8706 for the other 528. Every additional API
dollar spent on overlap buys negative F1
(`results/analyses-manifest.json`, analysis `h13-overlap-2026-08-18`,
`outcome` field). Errata: **E54**, **E66**, **E75**.

**Scope limit.** These numbers hold **only** for the carried `brief-text`
configuration on the Era-1 four-sheet corpus, single-pass, no consensus and no
verifier. E75 § "What the paper may now say" is explicit that "overlap was a
fixed parameter throughout" remains correct for every other result in the
study.

#### Later campaigns that also bear on overlap/stride — post-hoc, not H13

Three subsequent campaigns characterise overlap/stride far beyond the
registered arms. **None is an execution of the registered H13 design**; all are
post-hoc / E41-class, and the generated ledger places the grid rows outside
the H1–H15 frame entirely
(`results/hypothesis-outcome-table/hypothesis-outcome-table.md`
§ "Register rows outside the hypothesis frame": `grid-tilesize-overlap-2026-08-18`,
`grid-postverifier-2026-08-18`).

| Campaign | Path | What it adds |
|---|---|---|
| Grid (tile size × overlap 2 × 2) | `results/grid-2026-08-18/findings.md` | 384/512 px × 12.5/50 % overlap, K = 10. **Reverses the H13 single-pass finding once aggregation is switched on**: "both bigger tiles and less overlap win" at a single pass, but "overlap reverses and becomes the single most valuable thing in the grid" after consensus |
| Stride programme (nine geometries) | `results/stride-2026-08-25/findings.md` | Nine tile-size × overlap cells, K = 10 + verifier. Best cell 384 px / 33.3 % overlap, F1@20 m 0.8982 |
| 55-map deployment portfolio | `results/stride55-2026-08-27/findings.md`; `results/55map-final-board-2026-08-27/final-board-50m.md` | Carries two geometries to the 55-map corpus: A (384 / 33.3 %) corrected-F1@50 0.8326, B (384 / 50 %) 0.8422 |

⚠ **Reconciliation note.** The H13 arms and the later campaigns point in
*opposite directions* on overlap, and the difference is not a contradiction:
H13 is single-pass with no consensus and no verifier, where extra overlap adds
duplicate false positives faster than it adds recall; the grid and stride
campaigns aggregate over K passes, where overlap supplies the cross-tile
corroboration that a vote threshold can exploit. Any paper claim about overlap
must state which regime it is in.

⚠ **Manifest gap (unresolved).** `results/analyses-manifest.json` was
generated 2026-08-24 (`generated_at`), which pre-dates the stride
(2026-08-25) and 55-map portfolio (2026-08-27) campaigns. Neither is in the
manifest, and neither therefore appears in the generated ledger. The manifest
needs regenerating before the ledger can be treated as complete for these
campaigns.

---

## Conditional Triggers

Preregistered conditional obligations — promises of the form "if X, then we
will also run Y". Verified at source 2026-08-28 (Session 143).

### H7 temperature-escalation trigger (`osf/preregistration.md:731`)

The registered rule has **two independent clauses**. Verdicts differ, so they
are recorded separately.

Source numbers for both clauses — Phase 2b retest, 340 tiles × K = 3, 20 m
buffer (`results/retest/phase2b-track1-evaluation.json`,
`results/retest/phase2b-track2-evaluation.json`; per-temperature mean F1):

| Track | T=0.0 | T=0.3 | T=0.7 | T=1.0 | T=1.3 |
|---|---:|---:|---:|---:|---:|
| 1 (image) | 0.5869 | 0.5751 | 0.5367 | 0.5269 | 0.4903 |
| 2 (text) | 0.6048 | 0.6065 | 0.5842 | 0.5335 | 0.5442 |

**Clause 1 — upper bound.** "If T=1.3 yields higher F1 than T=1.0 (point
estimate, same M/E and H5 condition), exploratory testing at T=1.6 and T=2.0
will be conducted."

**Verdict: FIRED — and the obligation is OUTSTANDING.** On Track 2 (text),
T=1.3 (0.5442) exceeds T=1.0 (0.5335) on the point estimate, which is exactly
the condition the rule names. (It did not fire on Track 1: T=1.0 0.5269 >
T=1.3 0.4903.) The promised T=1.6 and T=2.0 runs **have not been executed**:
`planning/run-predictions/h7-escalation-t1.6.md` § Outcome reads "*Not yet
run. To be completed after execution*", and a filesystem search for T=1.6 or
T=2.0 artefacts under `outputs/` and `results/` returns nothing. **This is a
genuine unmet preregistration obligation and should be disclosed as such.**

Mitigating evidence, recorded but not sufficient to discharge the promise: the
triggering difference does not survive replication. Paired tile-swap
permutations across the three replicate runs
(`results/h7-escalation-check/text-run0{1,2,3}/pairwise_permutation_result.json`,
tabulated at `planning/run-predictions/h7-escalation-t1.6.md:43-47`) give
ΔF1 (T=1.0 − T=1.3) of −0.0362 (p = 0.247), +0.0022 (p = 0.910), and +0.0020
(p = 0.926) — none significant, and **the sign is not consistent across
replicates**; the aggregate that fired the trigger is carried entirely by
run01. The registered instrument agrees: paired bootstrap ΔF1 −0.0357,
95 % CI [−0.0908, +0.0137], p = 0.204. The honest disclosure is that the
trigger fired on noise and the promised runs were nevertheless never made.

**Clause 2 — lower bound.** "If T=0.3 or T=0.7 improves performance (alone or
in ensembles), further testing at low temperatures will be conducted at the
optimal configuration to characterise the lower bound."

**Verdict: FIRED — and substantially discharged by later work.** Against the
registered planned contrast (T=1.0 vs each other level), T=0.3 improves on
both tracks (Track 1 0.5751 > 0.5269; Track 2 0.6065 > 0.5335), and T=0.3 is
the Track 2 optimum outright. Low-temperature characterisation was then
carried out extensively, though never under the H7-escalation label:

- Phase 3a ran consensus voting at **T=0.3 and T=0.7** rather than the
  carry-forward T=0.0, precisely because T=0.0 is near-deterministic
  (erratum **E32**).
- The 55-map final board carries dedicated **T0.3 (HIGH, K = 5)** and
  **T0.7 (HIGH, K = 5)** cells — carried F1@50 0.8303 and 0.8169, oracle
  0.8406 and 0.8387 (`results/55map-final-board-2026-08-27/final-board-50m.md`
  § "Runs: as run versus theoretical maximum").
- The stride programme ran throughout at **T = 0.7**
  (`results/stride-2026-08-25/findings.md`).

The substance of the promise is met; the *letter* is not, in that none of this
work was framed or reported as the registered H7 escalation. Recommended
disclosure: the lower-bound obligation was discharged by later campaigns,
named above, rather than by a dedicated escalation run.

### H4b HP/HN-ordering follow-up (`osf/preregistration.md:564`)

The registered rule: "HP/HN ordering within the hard block is tested
separately in exploratory H4b **if H4 main effect is significant**."

**Verdict: NOT FIRED. No obligation arises.** Phase 2e tested four ordering
conditions at K = 10 with bootstrapped 95 % CIs and Benjamini–Hochberg FDR at
q = 0.05, and returned **0 of 6 FDR-significant comparisons**
(`results/phase2e-carry-forward-parameters.md` § Results Summary: "**FDR-significant
comparisons**: 0/6. Two comparisons initially significant at α=0.05
(config-default vs random, canonical-last vs random) did not survive FDR
correction across 6 comparisons"). Condition F1s: config-default 0.609,
canonical-last 0.609, canonical-first 0.579, random 0.529. H4 = config-default
was carried forward with no change. This matches the pre-existing note in
§ H4 above, which is confirmed rather than corrected.

---

## Execution Dependency Chain

```text
Phase 0: Preparation
    ↓
Phase 1: Library + Text Construction
    ↓
Phase 2a: H1 (M/E) → optimal M/E                    ✓ COMPLETE
    ↓
Phase 2b: H7 (Temperature) → optimal T               ✓ COMPLETE (T=0.0)
    ↓
Phase 2c: H8 (Library) → optimal library              ✓ COMPLETE (plus-hp)
    ↓
Phase 2d: H5 (Negative Text) → optimal text           ✓ COMPLETE (minimal)
    ↓
Phase 2e: H4 (Ordering) → optimal ordering             ✓ COMPLETE (no effect)
    ↓
    ├── Phase 3a: H3 (Voting N=30)                     ✓ EXECUTED
    ├── Phase 3c: H9 (Diversity — all A-E conditions)  ✓ EXECUTED (rejected)
    └── Phase 3c/3d: H2 (Two-Stage)                    ◐ PARTIAL (Cond. C never run)
    ↓
    └── H11 (Tile Size — exploratory)                  ✓ EXECUTED (384 closed)
    ↓
Phase 4: H6 (Flash→Pro Transfer)                       ✗ NOT EXECUTED — CLOSED (E74)
    ↓
Phase 5: Exploratory
    ├── H10 (Pool size)                                ✓ EXECUTED v2 (null)
    ├── H12 (HP:HN ratio)                              ✓ EXECUTED v2 (null)
    ├── H13 (Overlap/stride)                           ✓ EXECUTED (E75 remediated)
    └── H14, H15 (Cross-model)                         ✗ NOT EXECUTED (deferred; E76/E77)
```

---

## Status Key

Aligned 2026-08-28 with the vocabulary of the generated ledger
(`results/hypothesis-outcome-table/hypothesis-outcome-table.md`), which is
authoritative.

| Status | Meaning |
|--------|---------|
| Executed | Registered design run and analysed |
| Partially executed | Some registered conditions run, others never run |
| Not executed | No registered condition run (see the governing erratum) |
| Deferred | Registered as deferred; deferral honoured |

A hypothesis being "Executed" says nothing about the direction of its result:
H9, H10, and H12 were all executed and all returned nulls.

---

## Related Documents

- **Hypothesis-outcome ledger (AUTHORITATIVE)**:
  `results/hypothesis-outcome-table/hypothesis-outcome-table.md` — generated
  projection of `results/analyses-manifest.json`; believe it over this file
- **Protocol errata**: `protocol-errata.md` — E12, E32, E49, E50, E52, E63,
  E74, E75, E76, E77 govern the corrected rows above
- **Preregistration**: `preregistration.md` — Full hypothesis specifications
- **Execution plan**: `execution-plan.md` — Operational sequencing
- **Decisions log**: `decisions-log.md` — Rationale for key decisions
- **Config schema**: `prompts/README.md` — Configuration file documentation
