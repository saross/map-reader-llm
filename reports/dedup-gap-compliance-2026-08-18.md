# Is within-pass deduplication registered? A compliance reading of § 8.5

> **Last revised**: 2026-08-18 (original publication — the compliance analysis
> behind erratum E80). See [§ Changelog](#changelog) for revision history.

**Date**: 2026-08-18 (Session 136)
**Author**: Claude Code (Opus 5), amd-tower
**API spend**: US$0.00 — no model was called; every claim is read from committed
text or recomputed from committed artefacts
**Question**: is within-pass deduplication registered as part of the
**evaluation protocol generally**, or is it scoped to the **consensus/voting
pipeline**?
**Verdict**: **scoped**. Scoring a single-pass condition without deduplication
is preregistration-compliant. The 155-condition exposure is a **comparability
confound**, not a protocol violation.
**Consequence**: recorded as erratum
[E80](../docs/methodology/preregistration/protocol-errata.md)

---

## 1. Why the distinction decides the remediation posture

If within-pass deduplication is registered as a general property of scoring,
then 155 of 333 committed conditions were scored outside the registered
protocol, and the paper owes a correction: re-score, restate, and disclose a
deviation. If it is registered only as a step inside consensus voting, then
those conditions were scored exactly as § 4.1.2 prescribes, no committed number
is wrong, and what the paper owes is a **disclosure of asymmetry** plus a
targeted re-scoring wherever an exposed cell is compared against an unexposed
one.

The two postures differ in cost by roughly two orders of magnitude, so the
question was answered from the registered text rather than from intuition about
what good practice would have been.

---

## 2. The registered text

### 2.1 The section that contains the deduplication step is a *voting* section

Section 8.5 is headed **"Voting Implementation"**
(`docs/methodology/preregistration/osf/preregistration.md:1861`) and opens:

> Consensus voting aggregates detections from multiple passes into a single
> prediction set. (`:1863`)

Its first sub-heading, **"Pooling Scope"** (`:1865`), gives the two-step
framing from which the deduplication requirement comes:

> 1. **Within-pass deduplication**: Before voting, detections from overlapping
>    tiles within the same pass are deduplicated using the 20m spatial
>    tolerance. This prevents a single pass from contributing multiple votes for
>    the same physical location detected in adjacent tiles. (`:1869`)
>
> 2. **Cross-pass voting**: After within-pass deduplication, detections are
>    pooled across all N passes and clustered to count distinct pass
>    contributions. (`:1871`)

Three features of that text are decisive, and all three point the same way:

- **The temporal scoping is explicit.** "Before voting" is a precondition on an
  operation that only multi-pass aggregation performs. A single-pass condition
  never reaches the operation the precondition qualifies.
- **The stated purpose is vote-count integrity, not false-positive
  integrity.** The registered justification is "prevents a single pass from
  contributing multiple votes". A single-pass condition casts no votes. The
  harm the registered step exists to prevent cannot arise there.
- **The closing rationale repeats the scoping.** "This region-level approach
  ensures that tile boundaries (which are arbitrary processing artefacts) do not
  affect **vote counts**" (`:1873`, emphasis added). The general-sounding
  premise — tile boundaries are arbitrary artefacts — is registered in service
  of a conclusion about votes.

### 2.2 The deduplication step has no existence outside the voting algorithm

The operative specification is a seven-step **"Spatial Clustering Algorithm"**
(`:1875-1885`), of which deduplication is step 1:

> 1. **Deduplicate within each pass**: For each of N passes, cluster detections
>    from all tiles using 20m tolerance; retain one centroid per cluster
>    (`:1877`)
>
> 2. **Pool deduplicated detections** from all N passes into a single
>    collection (`:1878`)

Steps 3–7 are pairwise distances, clustering, vote counting per cluster, vote
thresholding, and consensus output geometry (`:1879-1885`). Step 1 is not a
free-standing scoring convention that voting happens to invoke; it is the first
step of a procedure whose remaining six steps are meaningless without N > 1
passes. The registration provides no other place where it is prescribed.

The project's own methods outline reads it the same way independently:
`docs/methods-outline.md:212-214` places "**Within-pass deduplication**: greedy
clustering at 20 m tolerance removes duplicates from overlapping tiles within a
single detection pass" under the heading **"3.6 Consensus Voting Mechanism
(H3)"** (`:210`).

### 2.3 The registered *evaluation* protocol specifies the duplicate's fate

Section 4.1.2 "Detection Matching Algorithm"
(`osf/preregistration.md:358-375`) is the registered evaluation procedure. It
is specified in full — five algorithmic steps and three outcome definitions —
and it contains no clustering, merging, or deduplication of detections. What it
does contain is the rule that determines how a duplicate scores:

> 7\. **False Positive**: Each unmatched detection (not assigned to any
> reference) (`:368`)

and, among the properties the registration claims for the algorithm:

> - **No double-counting**: A single reference cannot contribute multiple TPs,
>   and a single detection cannot satisfy multiple references (`:375`)

This is the load-bearing point. The registration does not merely omit
deduplication from the evaluation protocol; it **specifies the fate of a second
copy** — Hungarian one-to-one assignment gives the first copy the reference and
books the second as a false positive. The scorer's behaviour is what the
registered algorithm says it should be. `scripts/evaluate_detections.py` has no
deduplication step (verified: its only "deduplicate" comment, at `:1437-1442`,
deduplicates the *tile list* for a detection, which is the separate E79
tie-break), and its per-buffer point estimate is computed by
`lib_advanced_metrics.calculate_f1_internal` (`evaluate_detections.py:430-432`)
over whatever features it is handed. That is compliance, not deviation.

Section 3.8 "Evaluation Protocol" (`:313-329`) is likewise silent: it
specifies K=10 independent single-pass runs characterised statistically, and
post-hoc voting computed from the same runs. Nothing about overlap-band
duplicates.

### 2.4 The one non-voting registration of the step — H13 — was honoured

H13 (overlap/stride) registers deduplication in its own Implementation block:

> - Spatial deduplication applied to handle redundant detections (`:1039`)
> - Ground truth matching accounts for symbols detected in multiple overlapping
>   tiles (`:1040`)

This is the only general-purpose, non-voting registration of the step in the
whole document, and it sits in the one hypothesis where tile overlap is the
manipulated factor — precisely where undeduplicated scoring would manufacture
the result. It was honoured. The S135 phase gate caught the scorer's behaviour
before any spend, and all three H13 arms were scored after uniform within-pass
20 m deduplication (`results/h13-overlap-2026-08-18/findings.md:127-134`;
E75 disposition). The three `h13::arm-*` conditions are the only ones in the
manifest scored on explicitly deduplicated inputs.

That H13 needed to say this at all is itself evidence for the scoped reading: if
§ 8.5 Step 1 already bound all evaluation, `:1039` would be redundant.

### 2.5 The strongest text pointing the other way, and why it does not carry

Section 8.5's "Alignment with F1 Evaluation" sub-heading (`:1896-1901`) does
connect the two procedures:

> The 20m clustering threshold deliberately matches the spatial tolerance used
> in F1 calculation (Section 4.1.1). This ensures that:
>
> - Detections considered "the same" during voting are also treated as matching
>   the same reference during evaluation
> - No artificial precision loss from threshold misalignment

Read charitably, this is the registration noticing that voting and evaluation
share a notion of "the same detection", which could be argued to imply that
evaluation ought to apply that notion to duplicates too. But the passage argues
for **threshold alignment**, not for step transplantation: the entailment it
asserts runs voting → evaluation ("detections considered the same *during
voting* are also treated as matching the same reference *during evaluation*"),
which is a statement about the 20 m constant, not an instruction to cluster
before scoring. It is not enough to convert a voting-pipeline step into a
general evaluation requirement, particularly against § 4.1.2's explicit
disposal of unmatched detections.

### 2.6 The decisions log adds nothing that changes the reading

Twenty-six numbered decisions were searched
(`docs/methodology/preregistration/decisions-log.md`). None establishes
deduplication as a general evaluation step. The three nearest are:

- **Decision 26** (`:1167-1216`) — retains greedy-ball consensus clustering as
  primary with Weighted Boxes Fusion as robustness check. Concerns *cross-pass*
  aggregation, and reaches the same structural reading of the registration in
  passing: "the preregistration specifies the Hungarian matching tolerance and
  consensus voting framework but not the clustering algorithm" (`:1214`).
- **Decision 22** (`:1066-1088`) — adopts the proposer-verifier pipeline as "a
  two-stage Proposer-Verifier (PV) pipeline as a **post-hoc extension** to the
  preregistered single-stage detection approach" (`:1070`, emphasis added).
  Since PV is registered nowhere, no registered deduplication requirement
  attaches to it; the 26 exposed PV conditions cannot be in violation of a
  protocol that does not cover them.
- **Decision 4, edge clearance** (`:149`) — reasons about overlap on the
  *reference* side ("Truncated symbols are not genuine recognition failures
  because the 64px tile overlap ensures the full symbol appears in an adjacent
  tile"). Overlap and its consequences were understood; the detection-side
  duplicate was simply never taken up.

---

## 3. Verdict

**Within-pass deduplication is registered as step 1 of the consensus voting
algorithm (§ 8.5) and, separately and specifically, as part of H13's
implementation (`:1039`). It is not registered as part of the evaluation
protocol generally.**

Therefore:

| Family | n exposed | Registered position | Status |
|---|--:|---|---|
| single-pass | 123 | § 8.5 does not reach them; § 4.1.2 books the duplicate as an FP | **Compliant** |
| proposer-verifier | 26 | PV is an unregistered post-hoc extension (Decision 22) | **Not covered by the registration** |
| consensus | 6 | § 8.5 Step 1 applies and **was** applied; 1.6–6.9 % residual is greedy clustering's non-idempotency | **Compliant; implementation-fidelity residual** |
| `h13::arm-*` | 0 (of 3) | `:1039` applies and was applied | **Compliant** |

No committed number is withdrawn. No protocol violation is disclosed.

**What is nevertheless wrong** is a comparability confound the registration did
not anticipate and the study did not notice: § 8.5 Step 1 makes every multi-pass
consensus artefact deduplicated **by construction**, while single-pass
artefacts and single-proposer-pass PV artefacts are not. Two scoring paths
therefore coexist in the same result set, differing by an F1 offset that scales
with detection density. Any comparison that places an exposed cell against an
unexposed one — which is exactly the shape of the consensus-versus-single-pass
and diversity-dividend claims — measures the scoring-path difference as well as
the effect it names.

This is why the finding is recorded as a **sensitivity with a confound**, not as
a violation, and why the remedy is targeted re-scoring plus disclosure rather
than a blanket correction.

---

## 4. What made this survivable for six months

`docs/troubleshooting.md:121` — the operator-facing documentation for the exact
symptom — stated:

> **Symptom**: Same location detected multiple times.
>
> **Explanation**: Expected with overlapping tiles (STRIDE < TILE_SIZE). The
> evaluation script handles deduplication using 20m clustering.

The second sentence is false, and has been since the line was written
(`211a1bce4`, 2026-01-18, thirteen days before lodgement). Anyone who noticed
duplicate detections — the correct instinct — was told by the repository's own
documentation that the scorer already dealt with them. The line has been
corrected in the same commit as this note.

This is the more transferable lesson than the gap itself: a **false
reassurance** in documentation is worse than no documentation, because it
converts a live suspicion into a closed question. The gap was found in Session
135 only because a phase gate re-derived the scorer's behaviour from the source
instead of consulting the docs.

---

## 5. Measured exposure and effect (verified for this note)

Re-verified from `results/scoring-sensitivity-2026-08-18/exposure-survey.json`
(`summary` block) and the five probe batches in the same directory:

| Quantity | Value |
|---|---|
| Conditions surveyed / unresolved | 333 / 0 |
| Duplicate-exposed (>1 % of features within 20 m of another) | **155** |
| — single-pass / proposer-verifier / consensus | 123 / 26 / 6 |
| Tie-break-exposed (E79), for contrast | 123, all consensus |
| Exposed to both | 6 |
| Features across all exposed conditions | 289,065 |

Two different fractions are in play and must not be conflated:

- **Pair involvement** (`duplicate_fraction` in the register — features having
  at least one neighbour within 20 m, `scoring_sensitivity_survey.py:155-185`):
  exposed single-pass median **0.129**, max 0.229; exposed PV median **0.190**,
  max **0.250**; exposed consensus 0.016–0.069.
- **Removal fraction** (features actually deleted by
  `merge_passes.deduplicate_within_pass`): **0.0 %–12.7 %** across the 48
  probed cells, and **39.2–40.0 %** for H13 arm C at 50 % overlap
  (`results/h13-overlap-2026-08-18/findings.md:138-142`).

Effect on F1, recomputed across all 48 probed cells: **every delta is
non-negative**. ΔF1@20 spans **+0.0000 to +0.0578**; ΔF1@30 spans **+0.0000 to
+0.0589**. The three near-zero cells are `h13::arm-a-overlap-12-5` (already
deduplicated, +0.0000), `55maps-image-generalisation::verified` (+0.0004), and
`h13::arm-c-overlap-50` (+0.0044); the remaining 45 span +0.0090 to +0.0578 at
20 m. Recall is bit-identical before and after in every proposer-verifier cell,
so precision does all the work — the signature of pure duplicate removal.

The single most exposed condition in the study is
`pv-diag-384::verified-adv-text-baseline` (pair involvement 0.2500, F1@20
0.8142, F1@30 0.8320), which is the § R5 zero-diversity anchor. The gold-standard
headline `pv-diag-384::verified-adv-text-consensus-16of30` has pair involvement
**0.0000** and is unexposed.

---

## 6. What the paper must do

1. **Do not disclose a protocol violation.** Disclose a scoring-path asymmetry.
   The registered evaluation algorithm was followed.
2. **Describe both paths in Methods.** The Methods draft currently mentions
   deduplication nowhere (`docs/paper/methods-draft.md`, searched for
   "dedup"/"within-pass": no hits). It must say that multi-pass aggregation
   applies § 8.5 Step 1 within-pass deduplication at 20 m, that single-pass and
   single-proposer-pass conditions are scored as emitted, and that overlap-band
   duplicates therefore score as false positives in the latter per § 4.1.2.
3. **Re-score before comparing across the asymmetry.** Targeted campaign per
   `reports/scoring-sensitivity-review-2026-08-18.md` § 6 — the
   `diversity-dividend-384` tiering, the twelve `*-baseline*` rows of
   `gs-era2-pv-family-30m` with the § R5 anchor, the two single-pass baseline
   matrices, and the H1 pooled-modality bootstrap. Not all 155 conditions.
4. **Keep E79 and E80 separate in the prose.** They are near-disjoint exposures
   (6 conditions overlap) with opposite signs and different magnitudes; a
   combined "scoring caveats" paragraph would make the deltas unattributable.

---

## See also

- `docs/methodology/preregistration/protocol-errata.md` — **E80** (this gap),
  E79 (tile-assignment tie-break), E75 (H13 execution, whose disposition first
  recorded the mechanism)
- `reports/scoring-sensitivity-review-2026-08-18.md` — the measurement review
  this note supplies the compliance reading for
- `results/scoring-sensitivity-2026-08-18/` — exposure register and five probe
  batches
- `results/h13-overlap-2026-08-18/findings.md` — the first analysis scored under
  uniform deduplication

---

## Changelog

### 2026-08-18 — Original publication

Written to answer one question left open by
`reports/scoring-sensitivity-review-2026-08-18.md` § 4: whether the missing
within-pass deduplication is a preregistration violation or a comparability
sensitivity. Read § 8.5, § 4.1.2, § 3.8, and H13 of the lodged registration plus
all 26 entries of the decisions log; concluded **scoped to consensus voting plus
H13**, therefore compliant, therefore a confound rather than a violation.
Re-verified the exposure register (155/333) and recomputed the ΔF1 range across
all 48 probed cells (+0.0000 to +0.0578 at 20 m, no negative deltas) rather than
carrying the review's figures forward. Surfaced one new finding not in the
review: `docs/troubleshooting.md:121` asserted since `211a1bce4` (2026-01-18)
that "the evaluation script handles deduplication using 20m clustering", which
is false and plausibly explains why the gap survived to Session 135; corrected
in the landing commit. Landed with erratum E80.
