# Results claims-with-anchors inventory — `results-draft.md`, 2026-09-12

> **Last revised**: 2026-09-12 (original publication; outline-first claims
> inventory for the PI's section-by-section Results review). See
> [§ Changelog](#changelog) for revision history.

**What this is.** The Principal Investigator (PI) has ruled that the paper's
Results are rebuilt outline-first: before any prose is re-drafted, each
Results section is reduced to a list of the empirical claims it actually
makes, each claim tied to a source the assistant re-read and re-checked, so
the PI can rule section by section on what stays, what goes, and what is not
yet supported. This document is that list for
`docs/paper/results-draft.md` sections R0, R1, R2, R4, R5, R7 (all three
sub-blocks), R8, and R9.

**Sections R3 and R6 are deliberately not inventoried** — a K-ladder
(pass-count) job running in parallel will change their claims. Placeholders
stand in their place.

**Anchor discipline.** Every `anchor` cell names a file this session opened
and a value read out of it. The draft itself is never an anchor, and
`planning/paper-writeup-continuity.md` is never an anchor. Where no source
could be found the row is marked UNANCHORED — that is a finding, not a
failure. Statuses:

- **VERIFIED** — the anchor reproduces the number as the draft states it.
- **DRIFTED** — the anchor gives a different value; both are shown.
- **UNANCHORED** — no source located for the number.
- **REGISTERED** / **SIGNED** / **POST-HOC** — the registration standing the
  row's register entry carries (`preregistered` and `manually_verified_at` in
  `results/run-analyses.json`), given alongside the numeric status where a
  register row governs the claim.

**Word budget.** `docs/paper/manuscript-skeleton-isprs.md` § 5 gives Results
**~2,200 words** inside the locked ~8,500-word manuscript. Current prose
across all eleven blocks (tables, `[DRAFT NOTE]`s, and HTML comments
excluded) is **7,186 words** — **3.3×** the budget. Every section's count is
given below.

**Structural decisions cited.** All seventeen decisions D1–D17 in
`docs/paper/results-outline.md` are SETTLED (D1–D4 Session 118, D5–D17
Session 133; the D17 reconciliation gate closed in Session 134). Decisions
D-1 to D-5 in the ISPRS skeleton are DEFERRED by the PI (2026-09-10) and are
not re-opened here.

---

## R0 — Reading guide: instruments, metrics, and statistical conventions

**Section question (plain register).** *What two things did we measure
performance on, what number counts as performance, and how do we decide that
one configuration beat another?*

The section introduces two **instruments** — two different bodies of map and
reference data against which any configuration can be scored. The
**gold-standard (GS)** instrument is four Soviet 1:50,000 sheets whose burial
mounds were checked by a curator; it is the *calibration* instrument, used to
choose settings. The **55-map** instrument is 55 unseen sheets with a
reference built from student digitisation plus human-confirmed additions; it
is the *deployment* instrument, used to find out what the chosen settings
actually deliver.

**Prose word count: 447** (pro-rata share of a 2,200-word Results at eleven
blocks ≈ 200).

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R0-01 | The GS instrument is four Soviet General Staff 1:50,000 sheets with curator-adjudicated ground truth; it is the characterisation instrument. | `docs/paper/methods-draft.md:340` ("Four Soviet General Staff 1:50,000"); `results/evaluation-scopes.md:198,203` (4-map GS corpus, intersection with the 55-map set = 0) | VERIFIED | D6 puts the derivation in Methods; this is the permitted recap. |
| R0-02 | The 55-map instrument is 8,541 tiles on the ruling-21 standardised extended reference: 4,731 standardised student digitisations plus 279 human-confirmed extension mounds, from a 773-candidate phantom pool adjudicated down to distinct real mounds. | `results/deployment-oracle-2026-06-06/canonical-gt/standardised/README.md:21-23` (4731 student layer; 279 extension = 278 model-detected survivors of 773 + 1 marking-pass extra); `results/evaluation-scopes.md:206` (8,541 evaluable tiles) | **DRIFTED** | Every number verifies — **against reference r1 (the ruling-21 standardised layer)**. § R7 is now scored on **r2**, whose composition is 4,726 student + 278 extension + 14 audit-reviewed = **5,018** (`results/55map-leaderboard/55map-leaderboard-50m-r2.md:28-38`). R0 introduces an instrument one revision behind the board it introduces. |
| R0-03 | Positions are mixed-provenance: 641 reviewed student records and all 279 extension mounds at hand-marked centres (±2.5 m); 4,090 out-of-scope student records as-digitised (median 8.6 m from the true centre). | same README `:29-31` (527 directly reviewed + 114 proxy-confirmed = 641; 4090 out-of-scope, median 8.6 m, p90 18.3 m) and `:52-58` | VERIFIED | Same r1-vs-r2 caveat as R0-02: r2 reads 641 reviewed of 4,726. |
| R0-04 | Headline metric is buffered F1 at a per-instrument empirical working precision, reported with tile-level Matthews correlation coefficient (MCC) wherever inputs allow. | `results/working-precision/gs-plateau-characterisation.md:3` (plateau-onset definition); `results/tile-level-f1/` register row (MCC recomputation gate) | VERIFIED | Satisfies the standing "report MCC alongside F1" instruction. |
| R0-05 | Statistics: paired tile-swap micro-F1 permutation (10,000 permutations, seed 42, two-sided) + Benjamini–Hochberg FDR at q = 0.05 for pairwise claims; Hsu multiple comparisons with the best (MCB) for tie-set membership, the critical value a tile-level bootstrap analogue of Dunnett's. | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering_20m.json` (`n_permutations` 10000, `seed` 42, `fdr_q` 0.05); `docs/methodology/preregistration/protocol-errata.md:4965-4966` (E83: bootstrap critical value rather than Dunnett's table) | VERIFIED | **Not disclosed here**: the permutation test is *unregistered* — the registration's inference is bootstrap + BH (E45 correction; outline § D17 systemic issue 1). D5 also says convention detail belongs in Methods; this paragraph is ~200 words of it. |
| R0-06 | "Tier 1" always means the MCB admissible set; tiers below the first are descriptive rank bands carrying no claim of separation. | `results/run-analyses.json` → `era1-leaderboard`, `era1-single-pass-baseline-matrix`, `pass-budget-pareto-v2` outcomes, each carrying the same E83 tie-set note verbatim | VERIFIED | The E83 revision is applied consistently across the register. |
| R0-07 | Tile sets differ by instrument and tile size: GS 512 px 340 tiles, GS 384 px 487, GS 256 px 1,032, 55-map 8,541. | 340: `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.json` (`n_tiles` 340); 487: `results/leaderboard/era2/.../README.md:3`; 1,032: `results/h11/analysis_summary.md:35,47`; 8,541: `results/evaluation-scopes.md:206` | VERIFIED | — |
| R0-08 | A generated table reconciles all fifteen registered hypotheses (registered tier, execution disposition, family-FDR verdict, register entries, qualifying errata) and cannot drift from the record because it is generated, not hand-kept. | `results/hypothesis-outcome-table/hypothesis-outcome-table.md` — header states generated from `results/analyses-manifest.json` at commit `54ae2dc03`; 32 hypothesis-table rows rendered across the 15 hypotheses | VERIFIED (D16) | The table exists and is current to the head commit. |
| R0-09 | Three statuses recur below — confirmatory (reported with family-FDR verdicts), registered-exploratory (hypothesis-generating), post-hoc (characterisation only) — and each section opens with a one-line registration status. | `results/run-analyses.json` `preregistered` field: values in use are `confirmatory-with-deviation` (5 rows), `registered-exploratory` (11), `post-hoc` (44), `not-executed` (6) over 66 rows | VERIFIED (D16, D17) | The draft's three-way summary omits `not-executed`, which is the fourth value in the vocabulary and the one covering H6, H13-adjacent, H14, H15, H2-C. |

**Gaps.**

- The E45 disclosure — that the permutation test used on every board is
  *unregistered*, and that the registered inference was bootstrap + BH — is
  promised by the outline's D17 findings but appears nowhere in R0.
- The two-headline stub D2 requires ("GS F1@20 m 0.890 / MCC 0.790;
  deployment corrected-F1@50 m 0.815, carry-forward") is **not present**. R0
  ends on the hypothesis-table pointer. Both headlines are derived later
  (R4, R7.1), but the reader meets them without warning, which is precisely
  the conflation D1 and D2 were settled to prevent.
- No pointer to the seam section the D1 spine requires (the section between
  Part 1 and Part 2 stating what changes between instruments). **There is no
  seam section in the draft at all** — see the cross-section summary.
- `Table [N]` (the hypothesis-outcome table) is the draft's only promised
  exhibit and it exists. **No figure is promised anywhere in Results, and
  none exists**: `docs/paper/figures/` contains only
  `review-app-examples/`; `results/figures/` holds two Phase-3d PNGs
  referenced nowhere in the draft.

**Rulings needed.**

1. Re-point R0's instrument description to reference r2 (4,726 + 278 + 14 =
   5,018), keeping the r1 composition only if the supplement needs the
   lineage? **Recommended: yes, re-point** — R0 currently introduces a
   reference no § R7 number is scored on.
2. Add the D2 two-headline stub at the end of R0 as settled, at roughly 60
   words? **Recommended: yes** — it is a settled decision the draft never
   implemented.
3. Move the statistical-convention paragraph to Methods per D5, leaving two
   or three orientation lines? **Recommended: yes** — it is ~200 words of
   the 2,200-word budget and D5 already settled the call.
4. Does the E45 permutation-registration disclosure live in R0, in Methods,
   or in both with one clause here? **Recommended: Methods, with one clause
   in R0** — a reviewer checking the Open Science Framework (OSF) record
   will look for it beside the first use of the test.

---

## R1 — Working precisions are empirical properties, not free parameters

**Section question.** *Why is the match radius — how far a detection may sit
from a real mound and still count — the value we chose, and not a number
picked to flatter the results?*

The **working precision** is that radius. The claim is that it was read off
the data: widen the radius and scores rise until they stop rising, and the
point where they stop is a property of the pipeline, not of the analyst.

**Prose word count: 235** (target ≈ 200; roughly on budget, the only section
that is).

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R1-01 | Buffer radius is the analyst's largest free parameter, so it was derived rather than asserted. | framing claim; the derivation itself is at `results/working-precision/gs-plateau-characterisation.md:3` (plateau onset = smallest canonical buffer where every later step gains ≤ 0.005 F1) | VERIFIED | D6 settled: derivation → Methods, recap only here. This section is still a derivation, not a recap. |
| R1-02 | Plateau-onset analysis covers **all 259 conditions** with full buffer curves. | `results/working-precision/gs-plateau-characterisation.md:5` and `.json` `n_analysed`: **306** conditions (skipped: 86 non-GS corpus, 46 with fewer than 10 buffers) | **DRIFTED** | draft 259 → anchor **306**. |
| R1-03 | Text pipeline plateaus at 30 m; proposer–verifier (PV) at 30 m, consensus at 35 m, **single-pass at 40 m**. | same file `:17-19` — single-pass/none onset median **75 m** (n = 133); consensus 35 m (n = 102); PV 30 m (n = 71); text 30 m (n = 164) | **DRIFTED** | draft 40 m → anchor **75 m** for single-pass. 40 m is the *unknown-thinking-level* row (`:42`), a coincidental match. |
| R1-04 | Image-modality localisation plateaus at 75 m, roughly 2.5× looser than text. | same file `:34-35` — text 30 m, image 75 m; 75/30 = 2.5 | VERIFIED | — |
| R1-05 | Modality, not architecture, is the dominant factor. | same file `:17-19` vs `:34-35` — modality spread 30→75 m; architecture spread also 30→75 m once single-pass is read correctly | **DRIFTED** | With R1-03 corrected, architecture spans the same range as modality, so the claim as written is no longer supported by this table. Needs re-statement or a different statistic. |
| R1-06 | For the production text-PV family the buffer curve is flat from 30 m to 50 m, so GS headline values are insensitive within that range. | `results/working-precision/gs-plateau-characterisation.md:19` (PV onset 30 m, median tail drift +0.0049 to the last buffer) | VERIFIED | — |
| R1-07 | On the 55-map instrument a complete-spatial-randomness (CSR) null shows chance matching negligible at every canonical radius (null F1 ≤ 0.015 even at 150 m). | `results/working-precision/55maps-csr-noise-floor.json`, `cells[0].curve` buffer 150: `f1_null` **0.0146** | VERIFIED | — |
| R1-08 | Observed marginal gains die at 50 m while chance creep continues. | same file: `obs_step_gain` 50 → 75 m is **−0.0041** while `null_step_gain` is +0.0020 | VERIFIED | — |
| R1-09 | The attribution-ambiguity bound bites first: 10th-percentile nearest-neighbour spacing 65 m, so 21 % of mounds are at cross-match risk at 50 m and 42 % at 125 m. | same file: `gt_nn_percentiles_m["10"]` = **64.81**; `ambiguity_by_buffer["50"]` = **0.2133**, `["125"]` = **0.4195** | VERIFIED | — |
| R1-10 | The 50 m buffer is ~2× the measured student digitisation jitter. | `docs/notes/working-notes.md:19805` ("50 ≈ 2× jitter"); jitter ≈ 25 m at Obs 260, cited at `:14865,14919` | VERIFIED | — |
| R1-11 | GS results are quoted at 20 m (the preregistered radius) or 30 m (the plateau); all 55-map results at 50 m. | `results/leaderboard/era2/.../tiering_20m.json` (`buffer_metres` 20); `results/55map-leaderboard/55map-leaderboard-50m-r2.md:3` (50 m per the noise-floor derivation) | VERIFIED (preregistered radius) | — |

**Gaps.**

- Obs 371's ruling that the 55 m→50 m buffer is a **floor, not a generous
  choice** — below R = 50 m the extended reference collapses back to the
  reviewed student layer, so sub-50 m Track-2 figures penalise correct
  detections of student-missed mounds — is required by the outline's R1
  update note and is **absent**.
- The D6 PI rider (a supplement reporting full sweeps for all results on the
  agreed 14-buffer 5–150 m grid) has no pointer sentence here.
- The GS **stride/geometry** programme has no home anywhere in the draft, yet
  § R7.2 cross-references it as "(§ R1, Obs 435)". Obs 435
  (`docs/notes/working-notes.md:28698`) is a nine-cell geometry board, not a
  buffer plateau; the cross-reference points at a section that does not
  contain the result.

**Rulings needed.**

1. Correct R1-02, R1-03, and re-state R1-05 from the current
   `gs-plateau-characterisation` table? **Recommended: yes** — three of
   eleven rows in the draft's most-quoted derivation are stale.
2. Reduce R1 to the D6 recap (chosen radii + "derived, not chosen") and send
   the derivation to Methods? **Recommended: yes** — D6 settled this and it
   frees ~150 words.
3. Add the Obs 371 floor sentence here, or carry it only in R8?
   **Recommended: here, one clause, cross-referenced from R8** — it governs
   how every 55-map number may be read.
4. Where does the GS stride/geometry programme go — a new R1b, folded into
   R4, or supplement-only with the § R7.2 cross-reference re-pointed?
   **Recommended: decide before prose** — the ISPRS skeleton's exhibit (i)
   names it, and § R7.2 already cites a section that does not exist.

---

## R2 — Single-pass baselines: a broad statistical tie at modest performance

**Section question.** *One model call per map tile, no second opinion: how
good is that, and did any of the prompt-design choices we registered
actually change it?*

**Prose word count: 543** (target ≈ 200; 2.7× over).

*Registration status the section asserts*: H1, H4, H5, H7, H8 confirmatory
and adjudicated in the registered family false-discovery-rate (FDR)
correction; H7 rejected; H1, H4, H5, H8 not rejected; the organising boards
post-hoc.

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R2-01 | No single-pass configuration separates from the pack: on the Era-1 board (512 px, 340 tiles, curator GT, F1@20 m) the Tier-1 admissible set spans **15 of 36** cells. | `results/run-analyses.json` → `era1-single-pass-baseline-matrix`: `tie_set` length **15**; outcome "Was 20 condition(s), now 15" (E83) | VERIFIED; POST-HOC (`preregistered: post-hoc`, `manually_verified_at` 2026-06-09) | "Era 1" = the 512 px / 340-tile evaluation frame; needs a gloss. |
| R2-02 | Led numerically by a few-shot-ordering variant (`canonical-last`, F1 0.631, MCC 0.213). | same row's outcome; `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.json` rank 1: `observed_micro_f1` 0.63142, `mcc` 0.2132 | VERIFIED | — |
| R2-03 | 227/630 pairs significant. | same `tiering_20m.json`: 227 of 630 pairwise rows `significant: true` (recounted this session) | VERIFIED | — |
| R2-04 | The five registered single-factor manipulations (H1 modality/elaboration, H4 ordering, H5 negative text, H7 temperature, H8 library composition) all land inside or near the tie. | `results/hypothesis-outcome-table/hypothesis-outcome-table.md` rows H1, H4, H5, H7, H8 (all "executed", registered as confirmatory) | VERIFIED; REGISTERED | — |
| R2-05 | Text-modality prompts dominate image-only prompts at the bottom of the board. | `tiering_20m.json` Tier 4 = `image-t1.3` 0.4920 and `image-only` 0.4696, the two lowest cells | VERIFIED | — |
| R2-06 | Text-only cells reach F1 ≈ 0.60 with essentially no tile-level discrimination; image-bearing cells trade F1 for markedly better discrimination, **MCC 0.094–0.291 across the seventeen computable image-bearing cells**. | `tiering_20m.json`: 17 image-bearing cells have a non-null MCC, range **0.0942–0.2907** (recomputed this session) | VERIFIED | — |
| R2-07 | Eight of the fourteen text-only cells returned at least one detection on every one of the 340 evaluation tiles, emptying the predicted-negative column and leaving MCC undefined. | `docs/methodology/preregistration/protocol-errata.md` § E81, table at `:4247-4268` — nine conditions at confusion matrix TP 204 / TN 0 / FP 136 / FN 0, of which eight are text | VERIFIED (E81) | — |
| R2-08 | The six computable text cells all sit at 0.0665, the value of leaving exactly one of the **136 reference-empty tiles** alone. | E81 at `:4247` ("TN + FP is the count of reference-empty tiles, 136") and `:4271-4274` (the 0.0665 cells) | VERIFIED (E81) | — |
| R2-09 | H1's registered pooled modality contrast returns a null: Δ = +0.0238, 95 % CI −0.0104 to +0.0585, two-sided paired bootstrap p = 0.1774, adjusted p = 0.248. | `results/family-fdr/h1_cmt0106_pooled_modality.json` via register row `h1-cmt0106-pooled-modality` (delta +0.0238, CI95 [−0.0104, +0.0585], p 0.1774); `results/family-fdr/family_fdr.json` H1 `adjusted_p` 0.24836 | VERIFIED; **SIGNED** (`confirmatory-with-deviation`, `manually_verified_at` 2026-08-14) | — |
| R2-10 | H4, H5, H8 likewise not rejected (adjusted p = 0.217, 0.834, 0.834). | `results/family-fdr/family_fdr.json` — H4 0.217, H5 0.8344, H8 (Simes) 0.8344 | VERIFIED; SIGNED | — |
| R2-11 | H7 rejects at adjusted p = 0.00233, from the registered five-level Phase 2b sweep (single-pass text track, F1, +0.072 at FDR p = 0.004). | `results/family-fdr/family_fdr.json` H7 `adjusted_p` 0.0023333; `docs/methodology/preregistration/protocol-errata.md:1268` and `:3458` ("the preregistered Phase 2b evidence (text +0.072, FDR p=0.004)") | VERIFIED; SIGNED | — |
| R2-12 | H7 rejects *against its own registered expectation* — the registration predicted the vendor-recommended T = 1.0 would be optimal with lower temperatures degrading performance; the reverse held. | `results/run-analyses.json` → `n1-baseline-matrix-384` `predicted_outcome`; register outcome "T=0.0 beats T=0.7 … (H7)" | VERIFIED; REGISTERED | — |
| R2-13 | At single-pass Pro 384 px this is a point-estimate ordering only: the four leading cells put T = 0.0 above T = 0.7 (0.804 and 0.792 against 0.755 and 0.745), the admissible set has three members at B = 10,000 and spans both temperatures, and only the trailing T = 0.7 cell is excluded. | `results/run-analyses.json` → `n1-baseline-matrix-384`: `tie_set` = 3 members {pro-text-high-t-0-0, pro-text-medium-t-0-0, pro-text-medium-t-0-7}; outcome's E83 correction block ("only pro-text-high-t-0-7 ruled out"; F1 0.804 / 0.792 / 0.755 / 0.745) | VERIFIED (E83) | The `exploratory`→`post-hoc` label on this row was *argued* and must not be bulk-overwritten (outline § D17). |
| R2-14 | Temperature claims in this study do not generalise across metric or corpus, so each carries instrument, corpus, and metric. | `results/run-analyses.json` → `e43-matched-temperature` outcome (matched-scope effect does not survive; on tile-MCC the advantage runs the other way) | VERIFIED (E43/E72) | Satisfies the D8 drafting note. |
| R2-15 | Single-pass performance, at best ~0.63 F1, is the floor every architectural intervention is measured against. | `era1-single-pass-baseline-matrix` outcome ("single-pass alone tops out at F1 ~0.63") | VERIFIED | This is the sentence that carries R2's whole load; it survives all E81/E83 revisions. |

**Gaps.**

- **H10 and H12 are invisible.** Both ran to completion, both returned
  nulls, both carry `registered-exploratory` register rows
  (`h10-pool-size`, `h12-v2-hp-hn-ratio`, both `manually_verified_at`
  2026-08-17), and neither analysis id nor result appears anywhere in the
  draft. The outline's D17 findings flagged exactly this as systemic issue 3;
  it is still open.
- Two further `registered-exploratory` H1 rows —
  `image-b-modality-2026-08-28`, `image-b-thinking-pair-2026-08-28` — are
  likewise uncited.
- `h7-escalation-2026-08-28` (registered-exploratory; the H7 escalation
  trigger that fired and was not honoured, disclosed at erratum E60) is
  routed to an Appendix in the register and gets no clause here.
- The family-FDR verdicts in this section cite "Methods § M.x" rather than
  the register rows `family-bh-fdr-confirmatory` and
  `h1-cmt0106-pooled-modality` that carry them.
- The D3 thread's *home* is supposed to be R2 (F1-versus-MCC trade). R2-06
  states the trade but never names it as a recurring theme, so R4's and
  R7's callbacks have nothing to call back to.

**Rulings needed.**

1. Give H10 and H12 one sentence each here (two registered factors, both
   null) plus their register rows? **Recommended: yes** — a reviewer
   checking the OSF record against the paper will find them missing, and the
   fix is two sentences.
2. Name the F1-versus-MCC trade explicitly as the study's recurring theme at
   R2-06, since D3 made R2 its home? **Recommended: yes.**
3. Cut R2 to ~250 words by moving the E81 undefined-MCC mechanism to a
   footnote or supplement, keeping the direction in the body?
   **Recommended: yes** — the mechanism costs ~120 words and the direction
   survives without it.
4. Report the four not-rejected confirmatory hypotheses as one sentence with
   a table pointer rather than four adjusted p-values in prose?
   **Recommended: yes**, per D7's settled one-sentence treatment.

---

## R3 — Consensus voting *(NOT INVENTORIED)*

**Placeholder.** R3's claims turn on pass count and the diversity dividend,
and a K-ladder (pass-count) job running in parallel will change them. The
section is deliberately excluded from this inventory; it must be inventoried
against the ladder's outputs once they land. Current prose word count:
**303**. Register rows that will govern it:
`diversity-dividend-384` (confirmatory-with-deviation, verified
2026-06-06), `phase3a-consensus-calibration`,
`phase3a-high-consensus-calibration`,
`phase3a-replication-thinking-calibration`,
`phase3c-diversity-calibration` — none of the last four is cited by the
present draft.

---

## R4 — The proposer–verifier architecture

**Section question.** *Does adding a second model pass that re-examines each
candidate and votes it up or down beat doing the detection in one stage —
and does the answer depend on how big the image tiles are?*

A **proposer–verifier (PV)** pipeline is two-stage: the proposer nominates
candidate mounds, then an independent text-prompted pass looks at a crop
around each candidate and returns an acceptance probability. The section
also carries the study's gold-standard headline and, at its end, a newer
board on which a later model generation displaces the whole incumbent field.

**Prose word count: 864** (target ≈ 200; 4.3× over — the second-largest
block in Results).

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R4-01 | Adding an adversarial verification stage is, by point estimate, the best architectural move in the study on every tile size tested, and its cells sit among the admissible best on every board carrying them. | `results/run-analyses.json` → `era1-leaderboard` outcome (point-estimate leader is the verified cell; E83 block retracts "sole"/"single best" as statistical claims) | VERIFIED as re-stated | The section *title* still says "is the best architecture on every tile size", which E83 retracted. Title and body disagree. |
| R4-02 | The registration predicted the opposite: H2 predicted neither two-stage architecture would improve on single-stage-with-voting, and set a stopping rule of at least 0.05 F1 before two-stage designs would be pursued. | `results/run-analyses.json` → `family-bh-fdr-confirmatory` outcome ("H2 is a FALSIFIED directional prediction … clearing the registered >= 0.05 stopping threshold in the direction the registration predicted against") | VERIFIED; **SIGNED** (confirmatory-with-deviation, verified 2026-08-14) | — |
| R4-03 | The family FDR rejects H2's null at adjusted p = 0.00035. | `results/family-fdr/family_fdr.json` H2 `adjusted_p` 0.00034996 | VERIFIED; SIGNED | — |
| R4-04 | On the 384 px instrument the verified pipeline's margin over the best consensus-only configuration (0.890 against 0.814) exceeds the registered adoption bar. | `results/run-analyses.json` → `tile-size-sweep` outcome (consensus-only ceiling at 384 px = 0.814; consensus+verifier 384 px = 0.890); `family-bh-fdr-confirmatory` (+0.076) | VERIFIED; REGISTERED-EXPLORATORY for the tile-size leg | 0.890 − 0.814 = 0.076, matching the family row's effect size. |
| R4-05 | The conclusion is scoped to coarse-to-fine PV, because the registered fine-to-coarse Condition C was never built. | `results/run-analyses.json` → `h2-condition-c-fine-to-coarse`, `preregistered: not-executed`, verified 2026-08-17; `results/hypothesis-outcome-table/...md` H2 row "partially executed" | VERIFIED; **NOT-EXECUTED** (E59) | Good practice: this is the kind of disclosure a reviewer checks first. |
| R4-06 | The Era-1 definitive board has 82 cells (36 single-pass + 42 consensus + 4 clean PV). | `era1-leaderboard` outcome ("36 single-pass + 42 consensus + 4 verified-PV = 82 cells") | VERIFIED | — |
| R4-07 | The point-estimate leader is HIGH-thinking text consensus plus the adversarial verifier at F1 0.792, MCC 0.676. | same outcome | VERIFIED | — |
| R4-08 | Its Tier-1 admissible set has 10 members and includes all six HIGH-consensus cells, so the verifier's lift over the consensus champion (0.775 → 0.792) tops the board without separating from the strongest consensus-only configurations; 2,351/3,321 pairs significant. | same outcome ("the admissible set has 10 members, including all six HIGH-consensus cells"; 0.775 → 0.792; 2351/3321); `tie_set` length 10 | VERIFIED (E83) | This is the correctly-rewritten E83 sentence. |
| R4-09 | A MINIMAL single-pass plus verifier — two calls per tile — matches the 30-call HIGH-thinking consensus on F1 (0.770) and beats it on tile-level MCC. | same outcome ("verified-adv-text-t0.0 … reaches Tier 2 (F1 0.770) — matching the 30-call HIGH-thinking consensus on F1 and BEATING it on MCC (0.789 vs ~0.55-0.64)") | VERIFIED | This is the section's most practically useful claim and it is the least prominent. |
| R4-10 | H11's trigger — 512 px performance below F1 0.85 — was met on every cell of the single-pass board; the registered comparison was 512 vs 384 px and the 256 px arm is a post-hoc extension. | `results/run-analyses.json` → `tile-size-sweep`, `registered-exploratory`, verified 2026-06-09; `docs/methodology/preregistration/osf/preregistration.md:2225` | **VERIFIED with a reading question** | The registration reads "Specify success threshold: **F1 ≥ 0.85 triggers** H11 tile size testing" — i.e. the registered wording states the trigger in the *opposite* direction from the draft's "performance below F1 0.85". The board tops out at 0.631, so on the literal registered wording the trigger never fired. Needs a PI reading. |
| R4-11 | Single-pass climbs monotonically with tile size in the clean isolation: 256 px 0.342 < 384 px 0.520 < 512 px 0.606. | `tile-size-sweep` outcome (256 = 0.342, 384 = 0.520, 512 = 0.606) | VERIFIED | — |
| R4-12 | Consensus prefers 384 px. | `tile-size-sweep` outcome: text **MINIMAL** consensus still prefers 512 px (+0.02..+0.05 over 384); only text **HIGH** consensus flips to 384 (T0.7 0.814 > 0.773) | **DRIFTED** | The unqualified claim contradicts the register for minimal-thinking consensus. Must carry the thinking-level qualifier. |
| R4-13 | Under consensus + verifier the ordering is 384 (0.890) > 256 (0.856) > **512 (0.792)**. | `tile-size-sweep` outcome View 3: 384 = 0.890 > 256 = 0.856 > 512 = **0.793** | **DRIFTED** | draft 0.792 → anchor 0.793 (0.792 is the Era-1 board's 340-tile value for the same cell; the draft has mixed the two footprints). |
| R4-14 | The verifier rescues 256 px: the same pool scores 0.460 bare and 0.856 verified (+0.396). | `tile-size-sweep` outcome and Obs 352 as recorded in the row's `working_notes_obs` | VERIFIED | The row's own cross-scope caveat (the three numbers sit on 487-, 1,032- and 340-tile footprints) is in an HTML comment in the draft, not in the prose. |
| R4-15 | The study headline is F1@20 m 0.890 / MCC 0.790 on the GS 384 px instrument, from 30 HIGH-thinking text passes, a ≥16-of-30 consensus vote, and a single adversarial verifier pass. | `results/run-analyses.json` → `unswept-pools-completeness` outcome (0.8902 at k = 16 / prob 0.2 over 11,771 candidates); `tile-level-f1` outcome (the same cell's MCC 0.7903) | VERIFIED; POST-HOC | — |
| R4-16 | A completeness sweep of all **18** never-swept proposer pools confirms this is the global optimum of the 30-pass union. | `docs/notes/working-notes.md:20208` Obs 363 title and `:20232` ("genuinely unswept — swept now: **18**"); `unswept-pools-completeness` outcome | VERIFIED | — |
| R4-17 | The GS Era-2 verified board places 79 verified cells on one frame (39 register cells at committed operating points and 40 sweep optima), on the Era-2 carrier clipped to the B tiling's union (487 tiles, 435 reference mounds). | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md:3,5` ("39 → 79 cells"; 487 tiles, 435 curator reference mounds; 79 cells) | VERIFIED; POST-HOC | "Era 2", "`-opmax`", and "B tiling" all need glosses. Note: 42 of the 79 row ids contain the string `-opmax`, so the "40 sweep optima" set is not identifiable from the id alone. |
| R4-18 | Of 3,081 pairs, 1,845 are significant at BH q = 0.05, giving seven tiers. | same README `:5`; `results/run-analyses.json` → `gs-era2-verified-board-2026-09-10` outcome | VERIFIED | — |
| R4-19 | Greedy Tier 1 holds five Gemini 3.7 and 3.8 cells: image under the 3.7 verifier 0.9233, text under 3.7 0.9190, text under 3.8 0.9182, image under the carried Gemini 3 verifier 0.9179, text at K = 10 under the carried verifier 0.9068. | register outcome (all five values verbatim); board README table rows 1–5 | VERIFIED | "swap37"/"swap38" = the same candidate set re-verified by a different model version in the verifier seat. |
| R4-20 | The Hsu MCB admissible set holds 28 of the 79 cells. | register outcome ("MCB admissible set = 28"); README `:5` | VERIFIED | — |
| R4-21 | Every Gemini 3 cell sits in Tier 2 or below at either level: best committed incumbent the 16-of-30 cell at 0.8951, best sweep optimum the HIGH text T0.3 K = 5 cell at 0.8873 (rank 11). | README table: `pv-high-text-t0.3-n5-opmax` 0.8873 at rank 11, Tier 2; `verifier-robustness::verified-384-16of30-t0-3-n5-opmax` 0.8951 at rank 8, Tier 2 | VERIFIED with a naming problem | The 0.8951 cell's own id ends `-opmax`, so calling it "the best **committed** incumbent" reads as a contradiction of the 39/40 split in R4-17. Needs either a different phrase or an explicit note that this row's id is not a sweep-optimum marker. |
| R4-22 | 30 of the 40 sweep optima are significantly below the lowest Tier-1 cell and all 40 below the top one. | README changelog 2026-09-10 (later still) board-effects table: "`-opmax` cells significantly below the lowest Tier-1 cell 31 → **30** of 40"; "below the top cell 40 of 40" | VERIFIED | — |
| R4-23 | The lowest Tier-1 cell against the best sweep optimum: **+0.020, p = 0.16, not significant**. | `results/leaderboard/era2/.../tiering_20m.json` pairwise, `g37-text-k10-verified-carried-p0.10-k10-era2b` vs `pv-high-text-t0.3-n5-opmax`: diff **+0.0195**, p **0.1783**, BH **0.2438** | **DRIFTED** | draft p = 0.16 → anchor p = 0.178. The direction and non-significance hold. |
| R4-24 | The top cell against it: **+0.037, p = 0.011, BH-adjusted 0.021**. | same file, `g37-image-k5-verified-swap37-p0.90-k5-era2b` vs the same cell: diff **+0.0359**, p **0.0158**, BH **0.0284** | **DRIFTED** | draft +0.037 / 0.011 / 0.021 → anchor +0.036 / 0.0158 / 0.0284. These are the p-values the 2026-09-10 re-tiering moved (1,853 → 1,845 significant pairs); the point estimates were refreshed, the p-values were not. |
| R4-25 | Removing the screens' selection optimism (Efron–Gong, argmax replayed per tile resample) costs the 3.7 and 3.8 cells 0.0006 to 0.0035, leaving corrected board-frame F1 of 0.9027 to 0.9215. | `results/leaderboard/era2/.../optimism/README.md` board-frame rows: optimism +0.0006 (g37-text-k5-carried) to +0.0035 (grid verified37-p0.98-k10); corrected 0.9027 to 0.9215 | VERIFIED | **Efron–Gong optimism** = how much picking the best of many operating points flatters the score. |
| R4-26 | The family step § R7.3 measures at deployment is therefore a tier move on the GS instrument against the whole Era-2 incumbency at once, at both levels. | R4-19 to R4-22 taken together (all five Tier-1 cells are 3.7/3.8; every Gemini 3 cell Tier 2 or below at committed *and* sweep-optimal points) | VERIFIED as an inference | The inference is sound on the anchors, but it depends on R4-23/R4-24, one of which is not significant. |
| R4-27 | The frame itself moved no incumbent's F1 at four decimals and moved the B-geometry cells 0.007 to 0.008 downward. | board README table `Δ frame` column: +0.0000 for every `pv-diag-384` / `verifier-robustness` incumbent; −0.0070 to −0.0076 for the B-geometry and screen cells; register outcome "G6 max \|delta\| 0.0078" | VERIFIED | — |
| R4-28 | *(draft note)* The analysis row was SIGNED by the PI on 2026-09-10 after ruling gate G1 was satisfied on the true-input reproduction (44/44 cells, 946/946 pairs; Obs 464). | `results/run-analyses.json` → `gs-era2-verified-board-2026-09-10`, `manually_verified_at` **2026-09-10T12:34:56Z**; Obs 464 at `docs/notes/working-notes.md:33329` | **DRIFTED — conflicting record** | The board README, revised **2026-09-11**, ends: "The analysis row remains **UNSIGNED**; the publication ruling is the PI's." The draft's own top banner also says "unsigned, ruling pending". The register timestamp `12:34:56Z` is formulaic enough to be a placeholder. Three records, two answers. |
| R4-29 | *(draft note)* Nine of the 40 `-opmax` files, materialised on 2026-04-19, were found **mis-materialised** on 2026-09-10 and rebuilt from their stages the same day (each rose by 0.0004 to 0.0081; Tier 1 and the admissible set unchanged). | Obs 466, `docs/notes/working-notes.md:33812-33860`: the nine rose by +0.0004 to +0.0081 (table verified cell by cell); **but** "the materialiser **was correct**. **It was fed the Era-3 operating points**" — a cross-frame (327-vs-487 tile) operating-point leak, explicitly "**not** staleness" and not mis-materialisation | **DRIFTED (mechanism)** | The magnitudes verify exactly; the *diagnosis* in the draft is the superseded one. Obs 466 is dated 2026-09-11, one day after the sentence was written. |

**Gaps.**

- The section title asserts what E83 retracted ("is the best architecture on
  every tile size"). The body is correct; the heading is not.
- The D3 callback to the F1-versus-MCC trade is promised by the outline for
  R4 and is present only implicitly, inside R4-09's parenthesis.
- No statement of what the Era-2 board does to the study's *headline*. R4-15
  states 0.890 / 0.790 as "the study headline"; R4-19 then reports five
  cells above 0.906 on a 487-tile frame. The draft never says which number
  the paper will headline.
- The cross-scope caveat on R4-13/R4-14 (three tile footprints) lives in an
  HTML comment, so it will not reach a reader.
- The GS stride/geometry register rows (`stride-plateau-2026-08-25`,
  `stride-winner-ladder-exact-2026-08-25`,
  `grid-tilesize-overlap-2026-08-18`, `grid-postverifier-2026-08-18`,
  `h13-overlap-2026-08-18`) are all `paper_section: Results` and none is
  cited anywhere in the draft.

**Rulings needed.**

1. Does the paper headline the Gemini 3 cell (0.890 / 0.790) or the Gemini
   3.7 Era-2 cell (0.9233, 0.9215 optimism-corrected)? **Recommended:
   headline the Gemini 3 recipe as the study's calibrated result and report
   the 3.7 family step as a separate, dated finding** — it keeps the
   calibrate-then-deploy spine intact and does not stake the paper on a
   board whose signature status is contested (R4-28).
2. Is the Era-2 verified board signed or not? **Recommended: PI to state it
   once and have the register, the board README, and the draft banner
   updated together** — three artefacts currently disagree.
3. Correct the section title to the E83-compliant claim ("the strongest
   architecture by point estimate on every tile size tested")?
   **Recommended: yes.**
4. Split R4 into R4 (PV architecture + headline, ~250 words) and a separate
   short block for the model-generation board, or move the Era-2 board
   paragraph wholesale into § R7.3 where the family step is argued?
   **Recommended: move it to R7.3** — it is 300 words of § R7.3's argument
   sitting in Part 1, and moving it also removes a forward reference.

---

## R5 — Verifier robustness: nothing dearer is measurably better

**Section question.** *We tried making the verification stage better in
every way we could pay for — more runs, more deliberation, a stronger model.
Did any of it help enough to measure?*

**Prose word count: 662** (target ≈ 200; 3.3× over).

*Registration status the section asserts*: post-hoc throughout; no
registered hypothesis is adjudicated here.

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R5-01 | The robustness programme cost ≈ **$54 flex as-run**, recorded at run time. | not located. `results/verifier-robustness/verifier-robustness-findings.md` gives per-cell and per-pass costs (`:294` $2.54; `:597` ~$20.86 + ~$2.54 + four $0 cells) but no programme total; the register row carries none | **UNANCHORED** | Either anchor it or drop the figure. |
| R5-02 | The production verifier is gemini-3-flash, adversarial text, minimal thinking, T = 0.0, n = 1. | `results/verifier-robustness/verifier-robustness-findings.md:19-20` | VERIFIED | — |
| R5-03 | Scope note (E83): the tie statements are pairwise; MCB returns narrower sets — three of five rungs on `pass-budget-pareto`, six of seven on `pass-budget-pareto-v2` — so some cheap rungs are excluded as *the best* even though no dearer rung beats them pairwise. | `results/run-analyses.json` → `pass-budget-pareto` (`tie_set` length 3, outcome "only 3 of the 5 rungs"), `pass-budget-pareto-v2` (`tie_set` length 6, outcome "6 of the 7 rungs … verified-adv-text-4of5 (0.8641) is excluded") | VERIFIED (E83); POST-HOC | This is the most careful paragraph in the draft and should survive compression intact. |
| R5-04 | Determinism: five-fold verifier replication gives single-run SD 0.0025–0.0072 F1 with consensus ≈ mean, vindicating n = 1. | `results/verifier-robustness/verifier-robustness-findings.md:81` ("Across **all** proposer levels the single-run F1 SD is **0.0025–0.0072**"), table `:76-78`; Obs 354 via the register row's `working_notes_obs` | VERIFIED | — |
| R5-05 | A thinking × temperature matrix at N = 5 is one statistical tier (0/10 pairs significant, F1 0.8709–0.8764); only single-pass HIGH thinking drops a tier (0.8519). | `results/run-analyses.json` → `verifier-robustness-matrix` outcome (all five N = 5 configs one tier, 0/10, 0.8709–0.8764; single-pass HIGH 0.8519) | VERIFIED; POST-HOC | — |
| R5-06 | Verifier consensus: even at the 30-pass proposer, N = 5 verifier consensus lifts F1 only +0.0049 (0.8951 vs 0.8902), p = 0.363. | `results/run-analyses.json` → `pass-budget-pareto` outcome ("+0.0049, p=0.363") | VERIFIED | — |
| R5-07 | Compute allocation: at equal call budget, proposer passes beat verifier passes (10-proposer + 1-verifier 0.8769 ≥ 5 + 5 at 0.8739–0.8764). | `pass-budget-pareto-v2` outcome (high11 0.8769, high5+5vf 0.8739); `verifier-robustness-matrix` outcome (N = 5 band top 0.8764) | VERIFIED | The claim splices two rows; the splice is sound but should be one anchor in the supplement. |
| R5-08 | Verifier model: a Pro-class verifier ties the Flash verifier on the pools that matter and costs more; on high-recall pools it shows a small post-hoc advantage (0.8792, raw p = 0.019, not multiplicity-controlled), itself dominated on cost. | `results/run-analyses.json` → `unswept-pools-completeness` outcome ("the PRO verifier over the Flash-HIGH 5-pass union scores 0.8792 (4of5/pt0.25) … raw p=0.019, POST-HOC, not multiplicity-controlled … min11 dominates it on cost") | VERIFIED | — |
| R5-09 | Model upgrades: neither Gemini Pro 3.1 nor Flash 3.5 wins any role; Pro is a better bare proposer but a worse PV partner because near-deterministic sampling caps pool recall. | `results/run-analyses.json` → `flash35-model-roles` outcome ("the Pro pattern of consistency-without-coverage, and PV needs coverage") | VERIFIED | — |
| R5-10 | The Flash 3.5 2×2×2 (proposer × verifier × n; ~$34) ties bare (0.6196 vs 0.6204), loses as PV proposer (−0.0355, targeted pairwise p = 0.035 — the board's three-member admissible set still admits the cell, so the gap is pairwise-resolved but not simultaneous), and ties as verifier at 3× the price (p = 0.17 / 0.10). | `flash35-model-roles` outcome (0.6196 vs 0.6204; −0.0355 p = 0.035; p = 0.17 own pool / 0.10 F3 pool; `tie_set` length 3); `results/verifier-robustness/verifier-robustness-findings.md:362` ("~$34 flex") | VERIFIED (E83) | — |
| R5-11 | The meta-rule: on a within-noise tie, take the cheaper configuration — and on the GS instrument the cheaper option pointed the same way on every axis tested. | Obs 357 via the `working_notes_obs` of `verifier-robustness-matrix`, `pass-budget-pareto`, `flash35-model-roles` | VERIFIED | — |
| R5-12 | Mechanism: the verifier shifts the binding constraint from precision to pool recall. | `results/run-analyses.json` → `min-vs-high-thinking-pv` outcome ("the verifier shifts the binding constraint to POOL RECALL"); Obs 359 | VERIFIED | D12 settled this as its own hub subsection that R3, R4, and R6 point back to. It is currently a paragraph, and nothing points back to it. |
| R5-13 | Minimal-thinking T = 0.7 passes saturate Flash's recall ceiling at 0.9195 within ~5 passes (passes 6–10 add zero new ground-truth mounds); HIGH thinking adds volume (union growth per pass 2.46 vs 1.44) but only +0.023 of ceiling. | `min-vs-high-thinking-pv` outcome (0.9195; "the 10-pass lineage adds zero new GT mounds"; union/pass 2.46 vs 1.44; +0.023 ceiling) | VERIFIED | — |
| R5-14 | A zero-diversity anchor (one T = 0.0 pass + verifier) scores 0.8142, so temperature diversity is worth +0.057, about 60 % of it via the ceiling lift. | `min-vs-high-thinking-pv` outcome (0.8142); `results/verifier-robustness/verifier-robustness-findings.md:354` ("temperature diversity buys +0.057, ~60 % of it via the ceiling lift") | VERIFIED | — |
| R5-15 | At equal pass count, minimal-thinking proposers reach statistical parity with HIGH: **min6 0.8784** vs high6 0.8641, p = 0.66; min11 0.8835 vs high11 0.8769, p = 0.59; min11 vs the 31-pass headline p = 0.56. | `min-vs-high-thinking-pv` outcome: "min6 (**n30-lineage, 0.8708**) vs high6 (0.8641) **p=0.656**; min11 (0.8835) vs high11 (0.8769) p=0.591; min11 vs the 31-pass headline (0.8902) p=0.562. The TRUE min6 merge (**0.8784**) sits numerically above its permuted n30-lineage stand-in" | **DRIFTED** | The min11 and headline pairs verify. The min6 pair does not: p = 0.656 belongs to **0.8708 vs 0.8641**, not to 0.8784 vs 0.8641. The draft has paired the true-merge point estimate with the stand-in's p-value. |
| R5-16 | The consensus-era diversity dividend is thereby explained and retired for PV architectures — on the GS instrument; the comparison reverses at deployment. | `min-vs-high-thinking-pv` outcome ("the consensus-era dividend (Obs 141) is real for consensus-only architectures and OBSOLETE under PV"; "SCOPE: GS-characterised only — the parity REVERSED at 55-map deployment … Obs 362") | VERIFIED (D9 forward-reference discharged) | The draft forwards to "§ R6"; the reversal is argued in § R6 and again in § R7.1. |

**Gaps.**

- The Obs 362 **scope-qualification** the outline requires in the body of R5
  ("the meta-rule holds only where the instrument can resolve the
  difference") appears only as the closing sentence "Section R6 qualifies the
  rule's scope" — a pointer, not the clause D11 settled must be here.
- D11 settled: meta-rule + **summary table** in the body, per-axis detail to
  the supplement. R5 currently carries six per-axis bullets and no table.
- D12 settled: the recall-ceiling mechanism gets **its own short
  subsection** that R3, R4, and R6 point back to. It has no heading and no
  inbound pointers.

**Rulings needed.**

1. Replace the six per-axis bullets with the D11 summary table plus the
   meta-rule sentence, sending detail to Supplement S2?
   **Recommended: yes** — it is the settled decision and saves ~300 words.
2. Promote the recall-ceiling mechanism to its own labelled subsection per
   D12, with explicit callbacks added at R3, R4, and R6?
   **Recommended: yes.**
3. Fix or drop the min6 pairing at R5-15? **Recommended: state the tested
   pair (0.8708 vs 0.8641, p = 0.656) and mention the true merge's 0.8784
   separately** — as written the sentence attributes a p-value to a
   comparison that was not run.
4. Anchor or drop the "≈ $54 flex" programme cost? **Recommended: drop it**
   — the per-axis costs that carry the argument are all anchored, and the
   total adds nothing the cost table does not.

---

## R6 — The cost frontier *(NOT INVENTORIED)*

**Placeholder.** R6 prices the pass ladder and is the section a parallel
K-ladder (pass-count) job will change: its seven-rung table, its
efficient/dominated split, and its transfer table all key off pass counts.
Deliberately excluded; must be inventoried against the ladder's outputs.
Current prose word count: **494** plus a seven-row cost table and a
four-row transfer table. Governing register row: `pass-budget-pareto-v2`
(post-hoc, verified 2026-06-12), whose own outcome already flags that the
draft's transfer table quotes the **standardised**-reference vintage while
the row's deltas are canonical-vintage, "which differs by up to 0.008".

---

## R7 lead-in — Deployment: the 55-map board (reference r2)

**Section question.** *What did the settings we chose on four sheets actually
deliver on 55 sheets nobody had calibrated on?*

**Prose word count: 71** (the three-block signpost only).

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R7-01 | The 55-map corpus appears nowhere in the registration; the registration anticipated transfer testing on out-of-sample maps as Stage 2 future work but registered no analysis plan, so deployment results are pre-planned characterisation, not registered claims. | `results/run-analyses.json` → `55map-r2-leaderboard-50m`, `55map-final-board-r2-2026-09-06`, `gemini37-55map-grid-2026-08-31` all `preregistered: post-hoc`; `docs/methodology/preregistration/osf/preregistration.md:2280` ff. (§ 12 Future Directions) | VERIFIED; POST-HOC | An honest and load-bearing disclosure. |
| R7-02 | Three blocks per the PI's 2026-09-08 ruling: R7.1 the calibrate-then-deploy result on the Gemini 3 board, R7.2 the portfolio transfer and final board, R7.3 the model-generation leg. | `docs/paper/manuscript-skeleton-isprs.md` changelog 2026-09-08 ("reported inside § R7 of the Results draft as blocks R7.2 and R7.3") | VERIFIED (PI ruling, Session 151) | — |

**Gaps.** The **seam** section D1 settled — a half-page hinge stating what
changes between the two instruments (corpus 487 → 8,541 tiles; reference
curator GT → student GT + adjudicated supplement; buffer 20/30 m → 50 m and
why; resolving power, the sentence that licenses the reversal) — **does not
exist**. Its content is scattered across R0, R1, R6, and R7.1, which is
exactly the double-telling the standing convention forbids.

**Rulings needed.**

1. Write the D1 seam as its own short block before R7? **Recommended: yes,
   ~150 words** — it is settled, it is the paper's honest hinge, and it lets
   R0, R1, and R6 each shed a sentence.
2. Keep the three-block R7 structure as ruled? **Recommended: yes** — no new
   evidence bears against it.

---

## R7.1 — Calibrate, then deploy: the Gemini 3 board

**Section question.** *Taking the exact settings committed before
deployment, what score did we get, how much better could we have done with
hindsight, and what are the three lessons in that gap?*

Two terms carry the block. The **carry-forward** (or carried) point is the
operating point committed before any deployment scoring — the honest result.
The **oracle** is the best operating point visible only afterwards — an
upper bound, not an achievement. **r2** is the second revision of the 55-map
reference data.

**Prose word count: 562** (target ≈ 200; 2.8× over), plus an eight-row
table.

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R7.1-01 | The board is reference r2 at 50 m, eight cells, 24/28 pairs significant, five tiers. | `results/55map-leaderboard/55map-leaderboard-50m-r2.md:3`; register row `55map-r2-leaderboard-50m` outcome ("24/28 pairs significant, 5 tiers") | VERIFIED; POST-HOC (verified 2026-09-07) | — |
| R7.1-02 | Tier structure is identical to its standardised and canonical predecessors, so neither the reference standardisation nor its revision moved a conclusion. | `55map-r2-leaderboard-50m` outcome ("identical tier structure to the r1 standardised board"); `results/55map-leaderboard/55map-leaderboard-50m-standardised.md:3-14` (same ranks, same tiers, 24/28) | VERIFIED (E84) | — |
| R7.1-03 | r2 moved no cell by more than 0.0009 F1. | the two board docs differenced cell by cell this session: max \|Δ\| = **0.0009** (T03-k4 0.8303 → 0.8294) | VERIFIED | — |
| R7.1-04 | The study's primary deployment claim is the carry-forward row at 0.8162. | `results/55map-leaderboard/55map-leaderboard-50m-r2.md:11` (TH7-k4 carry-forward, tier 3, F1@50 0.8162) | VERIFIED (D13 settled) | — |
| R7.1-05 | Every row above it relaxes at least one carried setting after seeing deployment results, and those rows report the measured deployment gap, with the joint oracle (+0.022) as its upper bound. | `results/55map-leaderboard/55map_leaderboard_50m_r2.json` pairwise: T03-k3 vs TH7-k4 `observed_diff` **+0.0225**, p 0.0 | VERIFIED (D13; E56 applies) | D13 requires **E56 cited wherever the relaxed rows appear**. E56 is not cited in R7.1. |
| R7.1-06 | The eight-row table: T03-k3 0.8387/0.689 (T1); TH7-k3 0.8380/0.679 (T1); T03-k4 0.8294/0.669 (T2); TM-n10-k5 0.8274/0.669 (T2); TH7-k4 0.8162/0.665 (T3); TM-k3 0.8102/0.656 (T3); IM-k3 0.8008/**0.711** (T4); TM-k4 0.7826/0.640 (T5). | `results/55map-leaderboard/55map-leaderboard-50m-r2.md:7-14` — all eight rows, ranks, tiers, F1 and tile-MCC reproduce exactly | VERIFIED | — |
| R7.1-07 | The estimated correction puts F1̂ within 0.0007 of each r2 point with an interval of about ±0.005 — wider than the gaps between tiers, uniform across cells, unable to re-order the board. | `results/run-analyses.json` → `estimated-correction-r2` outcome ("F1-hat sits within 0.0007 of the r2 point … ≈ ±0.005 intervals, wider than the tier gaps") | VERIFIED; POST-HOC | "uniform" is a simplification: the correction is *below* the point for 32 of 35 cells, *at* it for one, and *above* it for two. See R7.2-19. |
| R7.1-08 | Lesson (i): the calibrate→deploy gap is a threshold-transfer failure, not a model failure — the carried T0.7 × 4-of-5 left +0.022 F1 on the table against the joint oracle T0.3 × 3-of-5 (0.8387, p < 0.001). | `55map_leaderboard_50m_r2.json`: +0.0225, p = 0.0 | VERIFIED; Obs 358 | The single most important deployment claim in the paper. |
| R7.1-09 | The threshold axis alone accounts for most of it: vote 3-of-5 beats the carried 4-of-5 for all three text configurations (+0.009 to +0.028, all BH p ≤ 0.001). | same file: T03-k3 vs T03-k4 +0.0092 (BH 0.0005); TH7-k3 vs TH7-k4 +0.0219 (BH 0.0); TM-k3 vs TM-k4 +0.0275 (BH 0.0) | VERIFIED | — |
| R7.1-10 | On the GS sheets those thresholds sat on a statistical plateau; at deployment the plateau resolves, and resolves *looser* — a pattern that recurred when the uplift cell's best deployment threshold (5-of-10) again sat looser than its GS optimum (6-of-10). | deployment 5-of-10: `results/55map-final-board-r2-2026-09-06/final-board-50m.md` row 28 (UPL-oracle at (0.15, **k5**) of 10); GS 6-of-10: condition id `pv-diag-384::verified-adv-text-min-6of10` in the `min-vs-high-thinking-pv` and `pass-budget-pareto-v2` tie sets | VERIFIED | — |
| R7.1-11 | Lesson (ii): thinking level is a priced trade (§ R6). | cross-reference to R6 | *depends on R6* | R6 is not inventoried; this claim inherits whatever the K-ladder job does to it. |
| R7.1-12 | Lesson (iii): the image configuration ranks seventh on F1 but carries the board's best tile-MCC (0.711); re-tiering the same eight cells on MCC makes it the **sole Tier-1 cell**, statistically clear of all seven others (ΔMCC +0.022 vs the runner-up, BH p = 0.002; 20/28 pairs significant, five tiers). | `results/metric-leaderboards/55map-mcc-tiering-r2.md:3,7` (20/28, 5 tiers; IM-k3 Tier 1 alone at 0.7110) and `:75` (IM-k3 vs T03-k3 +0.0221, raw 0.0013, BH **0.0020**) | VERIFIED; POST-HOC | — |
| R7.1-13 | The MCC tier order inverts the F1 board's top while **the six text-only cells keep their F1 ordering**, so the reversal is a modality effect rather than noise. | `results/metric-leaderboards/55map-mcc-tiering-r2.md:7-14`: the board has **seven** text-only cells, and their MCC order is **not** the F1 order — TM-n10-k5 (F1 rank 4, MCC 0.6695) overtakes T03-k4 (F1 rank 3, MCC 0.6691) | **DRIFTED** | Two errors: "six" → **seven**, and the ordering is preserved for five of seven, not all. The *conclusion* (modality effect) survives; the supporting clause does not. |
| R7.1-14 | The shared-reference re-measurement shows the reversal is ≈ 90 % metric behaviour, not reference effect — the reference axis moves the MCC gap by +0.003 of 0.042. | `results/55maps-r2-ref-2026-09-06/obs280-shared-reference-r2.json`: `mcc_gap_image_minus_f1_leader` student-only 0.0386 → standardised 0.0419, i.e. **+0.0033 of 0.0419** (92 % metric) | VERIFIED | — |
| R7.1-15 | For survey prioritisation, where tile-level discrimination matters more than exact counts, the image pipeline is the resolved best instrument, at two calls per tile. | R7.1-12 plus the two-call architecture at R4-09 | VERIFIED as an inference | The archaeologically most useful sentence in the Results. |

**Gaps.**

- **E56 is not cited** at the relaxed rows, which D13 settled as a
  requirement (the verifier probability thresholds are in-sample).
- The two caveats the 2026-07-27 sign-off attached to this board — the
  marginal-CI-versus-paired-test reading and the attribution resolution —
  are in the board docs (`55map-leaderboard-50m-r2.md:17-38`) and not in the
  prose.
- Obs 371's provenance point (the phantom pool was reviewed
  config-agnostically and the residual asymmetry favours *text*, so the
  image cell's MCC lead is **conservative**) is required here by the outline
  and is absent. It strengthens the section's best claim.
- The "joint oracle" framing survives in the table's rank-1 label
  ("oracle"), which D13 settled should not crown a single oracle cell.

**Rulings needed.**

1. Add the Obs 371 conservatism clause to lesson (iii)?
   **Recommended: yes, one clause** — it makes the section's strongest claim
   stronger at almost no word cost.
2. Cite E56 at the relaxed rows as D13 requires? **Recommended: yes.**
3. Fix or cut the "six text-only cells keep their F1 ordering" clause?
   **Recommended: cut it and keep the conclusion**, which R7.1-14 already
   supports independently.
4. Does the eight-cell Gemini 3 board stay in the main text now that the
   35-cell r2 final board (R7.2) contains all of its cells?
   **Recommended: keep R7.1's table, compress to five rows** — it is the
   only place the carry-forward-versus-oracle logic is legible, but six of
   its eight rows reappear in R7.2's table.

---

## R7.2 — The portfolio transfer: stride geometry at deployment, and the final board

**Section question.** *We ran the same detector twice over all 55 sheets,
changing only how much neighbouring image tiles overlap. Did the denser
tiling find more mounds, and did the thresholds we had chosen in advance
finally transfer?*

**Stride** and **overlap** describe how far the tiling window moves between
tiles: 384 px tiles at stride 256 overlap by 33 %, at stride 192 by 50 %.
The **transfer tax** is the F1 lost by using the threshold chosen in advance
rather than the best one visible afterwards. **K** is the number of proposer
passes; **k** (as in "k ≥ 8 of 10") is how many of them must agree.

**Prose word count: 879** (target ≈ 200; 4.4× over), plus a ten-row family
table.

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R7.2-01 | The portfolio ran two Gemini 3 text-MINIMAL geometries at ten passes each over the full 8,541-tile corpus: A at 384 px / 33 % overlap (stride 256), B at 384 px / 50 % overlap (stride 192). | `results/stride55-2026-08-27/findings.md:21-22` | VERIFIED; REGISTERED BY CARD (`stride55-sweep-oracle-2026-08-27`, `registered-exploratory`, verified 2026-08-28) | — |
| R7.2-02 | Each carried one operating point selected on the GS stride ladder and declared before launch: A at prob ≥ 0.15 with k ≥ 8 of 10, B at prob ≥ 0.15 with k ≥ 10 of 10. | `results/stride55-2026-08-27/findings.md:21-22`; `results/55map-final-board-r2-2026-09-06/final-board-50m.md` rows 20 (A-N10-carried at (0.15, k8)) and 15 (B-N10-carried at (0.15, k10)) | VERIFIED | — |
| R7.2-03 | The design froze the configuration axis (one carrier configuration per run), so overlap is the only lever; eight bets P1–P8 were named in advance, one expected to fail informatively. | `results/stride55-2026-08-27/findings.md:57-59` (frozen config axis) and `:140-150` (the bets table) | VERIFIED | — |
| R7.2-04 | Both carried points landed above the carried incumbent on the campaign's committed instrument, the canonical adjudicated extended reference (5,160 mounds at 50 m): A 0.8326 and B 0.8422 corrected F1 against 0.8152, at MINIMAL thinking where the incumbent ran HIGH. | `results/stride55-2026-08-27/findings.md:21-22,25,34` (A 0.8326, B 0.8422, incumbent 0.8152; "5,160 references at 50 m") | VERIFIED | "corrected F1" = F1 after human adjudication of candidate detections; needs a gloss. `results/gtfree-selection/gtfree-selection-findings.md:41` gives the same reference as **5,161** — a one-mound internal inconsistency. |
| R7.2-05 | The transfer tax collapsed from the incumbent's +0.0324 to +0.0036 for A and +0.0081 for B. | `results/stride55-2026-08-27/findings.md:40-42` | VERIFIED | — |
| R7.2-06 | The k lattice is finer at K = 10, so a one-step k error near the top costs 0.004–0.007 where the same step cost +0.027 at K = 5. | same file `:52-56` ("A −0.0036 (k7→k8) and B −0.0072 (k9→k10); at the incumbent's K = 5 the same one-step move cost +0.027") | VERIFIED; Obs 437 | — |
| R7.2-07 | The top is flat: A's k5–k8 all lie within 0.008 of its oracle. | same file `:58-59` | VERIFIED | — |
| R7.2-08 | The verifier threshold transfers exactly: both probability curves peak at 0.15–0.20, and 0.10 collapses the board by about 0.12. | same file `:60-63` | VERIFIED | — |
| R7.2-09 | The frozen configuration axis left no temperature loss to pay. | same file `:64-67` (the incumbent's +0.021 marginal temperature loss had no analogue) | VERIFIED | — |
| R7.2-10 | Each committed evaluation was reproduced to 1e-6 by the sweep before any oracle was read. | same file `:34-36` (A 0.832590, B 0.842214) | VERIFIED | A strong methodological point that is currently a subordinate clause. |
| R7.2-11 | The P5 overshoot — B's +0.0270 margin over the incumbent's carried point — decomposes additively into the incumbent's transfer tax (+0.0324), the oracle-to-oracle geometry gap (+0.0027), and B's own tax (−0.0081). | same file `:162-167` (the arithmetic reproduced line for line) | VERIFIED | — |
| R7.2-12 | The geometry therefore found few additional mounds; the calibration transferred instead — what GS calibration could not see was worth about 0.010 and what it protected was worth about 0.03. | derived from R7.2-05 and R7.2-11 (geometry +0.0027 at oracle; the A-versus-B effect ≈ 0.010–0.014; the protected tax +0.0324) | VERIFIED as an inference | The "about 0.010 / about 0.03" pairing is an interpretation of the decomposition, not a quoted figure. Flag for PI wording. |
| R7.2-13 | P6 failed as pre-named: B beats A at the carried primaries (ΔF1 −0.0096, p = 0.0147, per-sheet sign-swap permutation, 10,000 draws), at the oracles (−0.0141, p = 0.0001), and at the N = 5 rung (−0.0116, p = 0.0042, a post-hoc test outside the declared family). | `results/stride55-2026-08-27/findings.md:75-76` and `:87-88`; `results/run-analyses.json` → `stride55-a5-vs-b5-2026-08-27` (post-hoc) | VERIFIED | — |
| R7.2-14 | Every non-tie result survives Benjamini–Hochberg at q = 0.05 over the seven tests. | same file `:92-98` (five non-tie results survive; the two carried-point saturation ties stay non-significant) | VERIFIED | — |
| R7.2-15 | On the GS geometry grid the two geometries had tied; a GS tie is bounded ignorance at roughly ±0.03 resolution (Obs 362) and a real effect of about 0.01 sat inside the bound. | `docs/notes/working-notes.md:28698` Obs 435 ("the nine-cell geometry board lands on a plateau"); `min-vs-high-thinking-pv` outcome for the ±0.03 resolution | VERIFIED; but the **cross-reference is wrong** | The draft cites "(§ R1, Obs 435)". § R1 is buffer plateaus; the GS geometry grid appears in no section of the draft. |
| R7.2-16 | Pass count saturates at the carried points (P7): N = 5 is within noise of N = 10 for both runs (p = 0.82 and 0.32); the oracles keep a small BH-significant residue (−0.004 and −0.005). | `results/stride55-2026-08-27/findings.md:92-98` (the two carried-point saturation ties non-significant; A and B oracle-saturation BH-significant at 0.0131 and 0.0003) | VERIFIED (structure) | The structure verifies; the two p-values (0.82, 0.32) and the two residues (−0.004, −0.005) sit in `results/stride55-2026-08-27/ladder.json` rather than the findings prose, so anchor the four figures explicitly. |
| R7.2-17 | The N = 3 carried cells are emergent post-hoc nominations: the GS ladder had selected (0.15, k3) for both geometries before launch, but the decision to evaluate that rung at deployment was taken afterwards (2026-08-28), motivated by the N = 3 oracle's cost-frontier position. | `results/55map-final-board-r2-2026-09-06/final-board-50m.md` rows 16 and 26, both labelled "carried (**post-hoc**)" | VERIFIED | Exemplary disclosure; keep verbatim. |
| R7.2-18 | The final board scores every run on reference r2: 35 cells, 512 of 595 pairs significant, 12 tiers. | `results/55map-final-board-r2-2026-09-06/final-board-50m.md:7` ("512/595 pairs significant") and its 35-row table; register row `55map-final-board-r2-2026-09-06` (post-hoc, verified 2026-09-07) | VERIFIED | — |
| R7.2-19 | The estimated-correction column moves **every cell by −0.0004 to −0.0007** with intervals of about ±0.005 and re-tiers nothing. | `results/run-analyses.json` → `estimated-correction-r2`: below the r2 point for 32 of 35 cells, **at** it for one, and **above** it for two (TM-k4 **+0.0003**, IM-k4 **+0.0007**) | **DRIFTED** | "every cell" and the all-negative range are both wrong; three of 35 cells move the other way or not at all. The "re-tiers nothing" conclusion holds. |
| R7.2-20 | Family table, row 1: Gemini 3 text HIGH T0.7 K = 5 (carry-forward) 0.8162 (T9), tile-MCC 0.665, $207, oracle 0.8380 (T7) at (0.15, k3). | final board rows 30 and 23 | VERIFIED | — |
| R7.2-21 | Row 2: text HIGH T0.3 K = 5 — 0.8294 (T8), 0.669, $261, oracle 0.8399 (T6) at (0.20, k3). | final board rows 27 and 19 | VERIFIED | — |
| R7.2-22 | Row 3: text MIN K = 5 — 0.7826 (T11), 0.640, $23, oracle 0.8103 (T10) at (0.20, k3). | final board rows 34 and 31 | VERIFIED | — |
| R7.2-23 | Row 4: text MIN uplift K = 10 — carried **none**, MCC none, **cost none**, oracle 0.8274 (T8) at (0.15, k5). | final board row 28 (UPL-oracle 0.8274, T8, (0.15, k5)) carries **cost $58** | **DRIFTED** | "carried: none" is right (no carried point was registered at this rung); "cost: none" is not — the board gives $58. |
| R7.2-24 | Row 5: image HIGH K = 5 — 0.8008 (T10), 0.711, $195, oracle 0.8008 (T10) at (0.15, k3); the E82 k4 comparability cell (0.7398, T12) is not tabled. | final board rows 33 and 35 (IM-k4 0.7398, T12) | VERIFIED (E82) | — |
| R7.2-25 | Row 6: A — 0.8391 (T7), 0.693, $104, oracle 0.8419 (T6) at (0.15, k7). | final board rows 20 and 17 | VERIFIED | — |
| R7.2-26 | Row 7: B — 0.8503 (T5), 0.701, $97, oracle 0.8560 (T4) at (0.20, k9). | final board row 14 (B-N5-carried 0.8503, T5, 0.701, $97) and row 10 (B-N10-oracle 0.8560, T4, $174) | VERIFIED per the table's stated "best carried and best oracle per family" rule | The carried and oracle cells in this row are **different pass counts** (N = 5 and N = 10) with **different costs** ($97 and $174). The single cost cell is therefore not the oracle's cost. Needs a footnote. |
| R7.2-27 | Row 8: 3.7 arm 1 — 0.8551 (T4), 0.665, $153, oracle 0.8727 (T3) at (0.15, k5). | final board rows 11 and 7; costs at `reports/r7-gaps-deltas-2026-09-11.md:180` | VERIFIED | — |
| R7.2-28 | Row 9: 3.7 arm 2 — 0.8827 (T2), 0.706, $159, oracle 0.8871 (T1) at (0.95, k5). | final board rows 3 and 1; costs at `reports/r7-gaps-deltas-2026-09-11.md:181` | VERIFIED | — |
| R7.2-29 | Row 10: fourth cell — 0.8728 (T3), 0.726, ≈ $231 (mixed basis, PI-approved 2026-09-12), oracle 0.8813 (T2) at (0.96, k9). | final board rows 6 and 4; `results/stride55-2026-08-27/findings.md:118` ($173.59 audited B K = 10); `reports/billing-reconciliation-2026-09-11.md:134` (≈ US$58 verifier on its billing day) | VERIFIED | 173.59 + 58 = 231.6. |
| R7.2-30 | Among Gemini 3 families B holds the top (N = 10 oracle 0.8560 T4, N = 5 carried 0.8503 T5), above every incumbent cell, whose carried points sit in tiers 8–11. | final board rows 10, 14; tabled incumbent carried cells T03-k4 (row 27, T8), TH7-k4 (row 30, T9), IM-k3 (row 33, T10), TM-k4 (row 34, T11) | VERIFIED | True of the incumbent cells the family table carries. The untabled E82 comparability cell IM-k4 (row 35) sits at T12, so "8–11" holds only because that cell is deliberately excluded — worth a footnote so the range is not read as the board's. |
| R7.2-31 | The image cell keeps the highest tile-MCC among Gemini 3 cells (0.711) but the board's MCC crown now belongs to the fourth cell of § R7.3. | final board row 33 (IM-k3 0.711, the best tile-MCC of any Gemini 3 cell) against row 6 (fourth cell carried 0.726) and row 24 (FOURTH-N1-oracle 0.747, the board maximum) | VERIFIED | The crown belongs to the fourth-cell family on either reading — 0.726 among carried cells, 0.747 including oracles. |
| R7.2-32 | The practitioner recommendation (pre-declared question 4) is B at N = 5 with the GS-carried (0.15, k5), scoring 0.8503 on r2 (0.8438 on the canonical chain) for about $97 full or $77 lean-deploy over 55 sheets, above its own N = 10 carried point (0.8497, $174) and the HIGH incumbent (0.8162, $207). | `results/stride55-2026-08-27/findings.md:222,232-240`; final board rows 14, 15, 30 | VERIFIED | "lean-deploy" = cost excluding the passes a production run would not need; needs a gloss. |
| R7.2-33 | A budget floor exists at A with N = 3–5 ($35–48 lean), holding 0.827–0.832 on the canonical chain. | `results/stride55-2026-08-27/findings.md:240-241` | VERIFIED | — |
| R7.2-34 | Costs are flex-tier estimates rather than billing figures, and the N < 10 rungs' costs are simulated from audited per-call rates because those passes ran inside the K = 10 campaign. | same file `:244-247` | VERIFIED | — |
| R7.2-35 | The bets were assessed on the canonical chain and the board is scored on r2; the offset is roughly uniform (B N = 5 carried 0.8438 → 0.8503, B N = 10 carried 0.8422 → 0.8497, A N = 10 carried 0.8326 → 0.8391), and no verdict depends on the chain. | `results/stride55-2026-08-27/findings.md:222-223` (canonical) against final board rows 14, 15, 20 (r2) | VERIFIED | — |

**Gaps.**

- The GS stride ladder on which both carried points were **selected** is
  never reported (see R7.2-15). A reader cannot check that the carried
  points were chosen on GS rather than on the deployment sweeps — which is
  the whole claim.
- H13 (overlap/stride) is a registered hypothesis. Its register rows
  (`h13-overlap-2026-08-18` registered-exploratory;
  `stride-plateau-2026-08-25`; `stride-winner-ladder-exact-2026-08-25`) are
  uncited, and this section never says that the overlap result discharges a
  registered obligation.
- `results/55map-final-board-r2-2026-09-06/significance-groups.png` exists —
  a dot-and-interval plot of the 35 cells with the significance groups — and
  is referenced nowhere. It is the obvious candidate for the paper's one
  deployment figure.
- The block's own closing draft note states it runs to ~1,700 words with
  R7.3 against a 2,200-word Results budget; the measured figure is
  **2,163 words** for R7.2 + R7.3 alone.

**Rulings needed.**

1. Report the GS stride ladder (one or two sentences plus a supplement
   pointer), so the "declared before launch" claim is checkable?
   **Recommended: yes** — without it the section's central discipline claim
   is unverifiable by a reader.
2. Promote `significance-groups.png` to the paper's deployment figure?
   **Recommended: yes** — Results currently has no figure at all, and this
   one already exists at publication quality.
3. Compress the four sweep-surface mechanisms (R7.2-06 to R7.2-09) to one
   sentence each as the draft note proposes? **Recommended: yes — one
   sentence for all four**, keeping the k-lattice point, which is the
   transferable lesson.
4. Does the family table keep mixed pass counts in one row (R7.2-26), or
   split B into N = 5 and N = 10 rows? **Recommended: keep the rule, add a
   footnote naming the cost as the carried cell's** — splitting costs a row
   the budget cannot afford.

---

## R7.3 — The model-generation leg: Gemini 3.7 Flash in the proposer and verifier seats

**Section question.** *A newer model appeared mid-study. Where in the
pipeline does the improvement actually land — in the detector, or in the
checker — and does it survive at deployment scale?*

The pipeline has two **seats**: the **proposer** (nominates candidates) and
the **verifier** (accepts or rejects them). A **swap** re-runs one seat with
a different model version on the identical candidate set, so the model
version is the only thing that changes. **MDE80** is the smallest
difference the corpus can detect at 80 % power.

**Prose word count: 1,284** (target ≈ 200; **6.4× over** — the largest block
in Results by a wide margin).

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R7.3-01 | A GS screen came first: the Gemini 3.7 Flash text proposer under the carried Gemini 3 verifier reached 0.9139 F1 at 20 m at (0.10, k5), on a 791-candidate union at 59 % unanimity, for about $7.4 all-in. | `results/run-analyses.json` → `gemini37-screen-2026-08-28` outcome (0.9139 at (0.10, k5), 791-candidate union); `planning/gemini37-screen-2026-08-28.md:71-72` (union 791 with 59 % unanimous, all-in ~$7.4) | VERIFIED; POST-HOC, registered by card, `manually_verified_at` **None** | This register row is **not human-verified**. So are `gemini37-55map-grid-2026-08-31`, `-gridboard-`, `gemini37-image-gs-2026-09-01`, and `gemini38-screen-armv-2026-09-04` — every row § R7.3 rests on. |
| R7.3-02 | Every earlier family step (the 3.5 precedent) had landed at or below the Gemini 3 plateau (≤ 0.8934 plus the GS resolution), so the pre-named informative outcome G1 fired. | `planning/gemini37-screen-2026-08-28.md:25` (anchor 0.8934) and `:38` (G1's condition verbatim); register outcome ("G1's pre-named informative outcome FIRED") | VERIFIED | — |
| R7.3-03 | At deployment the campaign completed a 2 × 2 grid — proposer (Gemini 3 run B K = 10 union, or five 3.7 passes) × verifier (Gemini 3 or 3.7) — each cell's operating point committed before scoring; arm 1 at (0.10, k5), arm 2 at (0.80, k5), the fourth cell at (0.98, k10). | `results/run-analyses.json` → `gemini37-55map-grid-2026-08-31` outcome ("every corner at an operating point committed before any deployment scoring"); `results/gemini37-55map-2026-08-31/findings.md:45-48`; `gemini37-fourth-cell-gs-leg-2026-08-31` outcome ((0.98, k10) committed at `planning/gemini37-55map-2026-08-29.md:201`) | VERIFIED | — |
| R7.3-04 | On the canonical chain arm 1 scored 0.8494 against B N = 5's 0.8438 (+0.0056, p = 0.35), below the corpus's MDE80 of 0.013, so D1's pre-named informative failure stands: the GS proposer gain of +0.018 did not transfer as a resolvable deployment win. | `gemini37-55map-grid-2026-08-31` outcome (arm 1 0.8494, B N = 5 0.8438, +0.0056 p = 0.3488, MDE80 0.013, "D1 is the pre-named informative failure") | VERIFIED | — |
| R7.3-05 | Arm 2 scored 0.8763 (+0.0325 over the incumbent, p = 0.0001); the fourth cell 0.8656 against B K = 10's 0.8422 (+0.0234, p = 0.0001). | same outcome (arm 2 0.8763, fourth 0.8656, B K = 10 0.8422; "+0.0325, p = 0.0001"; "+0.0234, p = 0.0001") | VERIFIED | — |
| R7.3-06 | Both verifier-axis contrasts are significant (+0.0270 on the 3.7 pool, +0.0234 on the Gemini 3 pool) and both proposer-axis contrasts are not (+0.0056 and +0.0107, p = 0.35 and 0.074), with BH at q = 0.05 over the declared five-test family; the family gain lives in the verifier seat. | same outcome, all four contrasts verbatim | VERIFIED; Obs 444 | The section's headline finding, cleanly anchored. |
| R7.3-07 | The 3.7 verifier's probability scale sits at the top of the lattice (D7 confirmed, oracle at (0.95, k5)) and its carried threshold transferred with a tax of only +0.0043. | `gemini37-55map-gridboard-2026-08-31` outcome ("arm 2's +0.0043 (adjusted p = 0.000162)"); final board row 1 (ARM2-N5-oracle at (0.95, k5)) | VERIFIED | Note the register says that +0.0043 tax is itself **BH-significant** — "only +0.0043" is true in magnitude and not in significance. |
| R7.3-08 | The 3.7 proposer proposes about 3.5× tighter (12,715 candidates in the K = 5 union against roughly 44,000 projected from the Gemini 3 profile) and recall-led (D2 confirmed, recall 0.855 against 0.809). | `results/gemini37-55map-2026-08-31/findings.md:51` (12,715 vs ~44k estimated), `:45,48` (recall 0.855 vs 0.809), `:199` (D2 confirmed) | VERIFIED | — |
| R7.3-09 | The proposer seat's gain partly exists: arm 1's oracle 0.8662 would have cleared the incumbent by +0.0224, but its GS-selected threshold re-opened a transfer tax of +0.0168 that the all-3.7 arm did not pay. | `results/gemini37-55map-2026-08-31/findings.md:103` (N = 5 committed: carried 0.8494 / oracle 0.8662); `gemini37-55map-gridboard-2026-08-31` outcome (arm 1 gaps +0.0544 / +0.0227 / **+0.0168** at N = 1/3/5) | VERIFIED | 0.8662 − 0.8438 = +0.0224. |
| R7.3-10 | Gemini 3.8 Flash, published 2026-09-02 at 3.7's list price, re-verified the identical 791-candidate union at its lowest thinking level, so the two verifiers differ in model version alone. | `planning/gemini38-screen-2026-09-04.md:7` (released 2 September 2026) and `:14-19` ("Pricing identical to 3.7"; thinking levels `low, medium, high`) | VERIFIED | — |
| R7.3-11 | It reached 0.9258 F1 at 20 m against the all-3.7 stack's 0.9265, a difference of −0.0007 at p = 0.78; because both arms score the same candidates the paired instrument resolves about 0.011, making this a measured tie rather than an underpowered one. | `results/run-analyses.json` → `gemini38-screen-armv-2026-09-04` outcome (0.9258 at (0.88, k5); "dF1 −0.0007 at p = 0.7769"); `reports/r7-gaps-deltas-2026-09-11.md:37-38` (`null_std` 0.00379 over 487 tiles, 2.8 σ ≈ 0.0106) | VERIFIED | The measured-tie-versus-underpowered-tie distinction is a genuine methodological contribution. |
| R7.3-12 | On the Era-2 board of § R4 the 3.8 cell joins Tier 1 at 0.9182, third of the five, and in that seat 3.8 thinks 28 % less per candidate than 3.7 (76 tokens against 106) for about $0.85. | `results/leaderboard/era2/.../README.md` row 3 (0.9182, Tier 1); `gemini38-screen-armv-2026-09-04` outcome ("76 thinking tokens per candidate … against the 3.7 verifier's 106"; "~$0.85 flex token-basis") | VERIFIED | (106 − 76)/106 = 28.3 %. |
| R7.3-13 | The family ladder stops at 3.7, and because the 3.8 proposer seat was never measured nothing here bears on 3.8 as a proposer. | same outcome ("E1 CONFIRMED — a tie … E2 is untested: the PI ruled STOP after Arm V, so Arm P … was not run") | VERIFIED; Obs 448 | Strictly, a 3.8 *proposer probe* was run for thinking volume ("307 vs 275 t/tile"); only its detection performance is unmeasured. Worth a one-word qualifier. |
| R7.3-14 | On the r2 board the all-3.7 stack takes tier 1: arm 2 N = 5 oracle 0.8871 and carried 0.8827 (T2). | final board rows 1 and 3 | VERIFIED | — |
| R7.3-15 | Its carried point alone stands +0.0267 above the best cell the Gemini 3 board can field (B's N = 10 oracle at 0.8560) and its oracle +0.0311 above the same cell, so the family clears the incumbent family even when the incumbent is allowed its own hindsight. | final board rows 3, 1, 10 (0.8827 − 0.8560 = 0.0267; 0.8871 − 0.8560 = 0.0311); `results/gemini37-55map-2026-08-31/findings.md:183` states the same +0.0267 on the standardised chain | VERIFIED | — |
| R7.3-16 | The fourth cell scores 0.8728 carried (T3) and 0.8813 oracle (T2) and holds the board's highest carried tile-MCC, 0.726 at precision 0.952 and recall 0.806 — the discriminating verifier on the noisier Gemini 3 pool trading recall for precision. | final board rows 6 (0.8728, T3, P 0.9522, R 0.8057, MCC 0.726) and 4 (0.8813, T2) | VERIFIED | — |
| R7.3-17 | Arm 1 carried sits at 0.8551 (T4). | final board row 11 | VERIFIED | — |
| R7.3-18 | Saturation by N = 3 replicates for the all-3.7 stack (N = 3 oracle 0.8848, within 0.0023 of N = 5 on r2; the canonical N = 3 → 5 step is not significant) and does not replicate for arm 1 (+0.0076 at the carried points, significant). | final board row 2 (ARM2-N3-oracle 0.8848); `gemini37-55map-gridboard-2026-08-31` outcome ("arm 2's N3-to-N5 is non-significant on both bases … whereas arm 1's carried N3-to-N5 IS significant at +0.0076") | VERIFIED | — |
| R7.3-19 | A single 3.7 pass under the 3.7 verifier reaches 0.8563 at its rung oracle on the canonical chain, above the Gemini 3 five-pass incumbent, but only 0.8421 at the carried threshold, so the one-pass economy requires a rung-tuned threshold the carry-forward discipline does not supply. | `gemini37-55map-gridboard-2026-08-31` outcome ("a single 3.7 pass under the 3.7 verifier reaches 0.8563 at its rung oracle … the honest carried N = 1 reads 0.8421, a Tier 4 tie") | VERIFIED | Cost-wise the most consequential sentence in the block for a practitioner. |
| R7.3-20 | The gold-standard instrument records the same step: on the Era-2 verified board all five Tier-1 cells are Gemini 3.7 or 3.8 and every Gemini 3 cell falls to Tier 2 or below at both its committed and its sweep-optimal point. | `results/leaderboard/era2/.../README.md:5` and its rank table | VERIFIED | This repeats R4-19 to R4-22 almost verbatim — a double-telling the standing convention forbids. |
| R7.3-21 | The 3.7 image proposer scored 0.9254 at 20 m under the Gemini 3 verifier and 0.9308 under the 3.7 verifier, +0.084 and +0.090 over the Gemini 3 image anchor of 0.8412 (I1), about five times the text-side gain. | `results/run-analyses.json` → `gemini37-image-gs-2026-09-01` outcome (0.9254 / 0.9308 against 0.8412; "+0.0842 / +0.0896"; "about five times the text-side family gain") | VERIFIED | — |
| R7.3-22 | The within-family text − image gap moved from +0.0549 (p = 0.001) in Gemini 3 to −0.0115 (p = 0.25) and −0.0043 (p = 0.68) in 3.7, supporting parity rather than inversion (I2 overshot its prediction to zero). | same outcome, all five figures verbatim | VERIFIED | — |
| R7.3-23 | "Text beats image" is therefore a property of the Gemini 3 family, not of the task. | same outcome ("the study's 'text examples beat image examples' claim must be reframed as Gemini-3-specific") | VERIFIED; Obs 447 | This **obliges a change in § R2 and § R4**, which still state the modality result unqualified. The register row says so explicitly. |
| R7.3-24 | The pre-agreed trigger for a 55-map image extension was not met (all-3.7 image 0.9308 against the all-3.7 text swap's 0.9265, +0.0043, not significant and under MDE80 ≈ 0.024), so the deployment table carries text cells only. | same outcome ("+0.0043 at p = 0.677, far inside MDE80 … a registered negative decision, not an absence") | VERIFIED | — |
| R7.3-25 | The five 3.7 proposer passes over the deployment tiling cost $144.27 at flex rates; the two verifier arms $8.89 (Gemini 3 over 12,715 candidates) and $14.31 (3.7 over the same candidates), giving $153 for arm 1 and $159 for arm 2; the two arms share one proposer, so the campaign spent $167 to place both. | `reports/r7-gaps-deltas-2026-09-11.md:123` ($144.27 total), `:148` (arm 1 $8.89), `:155-160` (the $12.54 → $8.89 correction), `:180-183` ($153 / $159 / $167.47) | VERIFIED | The register row `gemini37-55map-grid-2026-08-31` still carries the **superseded $12.54**. Register hygiene item, not a draft error. |
| R7.3-26 | The fourth cell's verifier token load is not on file because its run metadata records only the cleanup pass, so its cost is taken from the invoice — about $58 for the verifier on the one billing day it occupied — giving about $231 with B's audited K = 10 proposer. | `reports/billing-reconciliation-2026-09-11.md:124,134-135` (31 Aug day; ≈ US$58 at flex against a US$64.7 simulation); `results/stride55-2026-08-27/findings.md:118` ($173.59) | VERIFIED; mixed basis PI-approved 2026-09-12 | — |
| R7.3-27 | The invoice reconciles: over the four billing days Google charged US$247 for the 3.7 SKUs against a known token basis of US$242, the 2 % residual being two aborted partial passes that left no metadata; billed output tokens match the reconstruction within 0.2 %. | `reports/billing-reconciliation-2026-09-11.md:94,106,108-109` (billed US$247.41 vs known US$242.3, ≈ 2 %) and `:110-113` (billed 62.43 M output tokens against a 62.3 M reconstruction = 0.21 %) | VERIFIED | — |
| R7.3-28 | An earlier expectation that this SKU billed at about 0.6 × the token basis was an artefact of the run metadata's own cost stamps, which priced 3.7 at Gemini 3 rates. | same report `:154-161,197` | VERIFIED | — |
| R7.3-29 | Thinking volume was 265–277 tokens per call on the text arms (D4) and 88–157 on image (I4). | `gemini37-55map-grid-2026-08-31` outcome ("D4 is confirmed at 265-277 t/call"); `gemini37-image-gs-2026-09-01` outcome ("I4 is confirmed and lighter than predicted (88-157 t/call)") | VERIFIED | — |

**Gaps.**

- Five register rows this block rests on have `manually_verified_at: None`
  — `gemini37-screen-2026-08-28`, `gemini37-55map-grid-2026-08-31`,
  `gemini37-55map-gridboard-2026-08-31`, `gemini37-image-gs-2026-09-01`,
  `gemini38-screen-armv-2026-09-04`. The whole model-generation leg is
  unsigned in the register even where the sentences carry "[DRAFT, S153 —
  pending PI ruling]" resolved notes.
- `gemini38-screen-armv-2026-09-04` is the 3.8 leg's own register row and is
  **not cited**; the draft cites the 3.7 screen's `swap38` condition id
  instead.
- The register row `gemini37-image-gs-2026-09-01` states an **obligation on
  the paper** — reframe "text beats image" as Gemini-3-specific — which
  §§ R2 and R4 do not yet discharge.
- The I5 informative failure (implicit caching engaged at 79.5 % of input
  against a registered ≥ 90 % bar) is a registered negative result and is
  not reported.
- Three `[DRAFT, S153 — pending PI ruling]` markers remain open in this
  block (after R7.3-13, after R7.3-15, after R7.3-29) plus one in the
  closing draft note.

**Rulings needed.**

1. Do the five unsigned 3.7/3.8 register rows get signed before this block
   is drafted as prose? **Recommended: yes, sign or gate them** — the
   block's entire evidence base currently sits outside the
   `manually_verified_at` discipline every other section's rows observe.
2. Discharge the Obs 447 obligation by qualifying the modality claim in
   §§ R2 and R4 as Gemini-3-specific? **Recommended: yes, one clause in
   each** — the register row names it as an obligation on the paper.
3. Cut R7.3 from 1,284 words to ~350 by moving the cost reconciliation
   (R7.3-25 to R7.3-28, ~230 words) and the GS screen (R7.3-01, R7.3-02)
   to the supplement, keeping the 2×2 result, the verifier-seat conclusion,
   the measured tie, and the one-pass economy? **Recommended: yes** — the
   billing reconciliation is exemplary transparency and belongs in S1/S2,
   not in a 2,200-word Results.
4. Resolve the R7.3-20 double-telling with § R4 by choosing one home for the
   Era-2 board? **Recommended: R7.3** (see the R4 rulings) — the family step
   is a deployment argument.

---

## R8 — What the ground truth can and cannot support

**Section question.** *Our reference data is itself imperfect. How wrong is
it, in which direction, and by how much — so that every score above can be
read with the right error bars?*

**Prose word count: 255** (target ≈ 200; roughly on budget).

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R8-01 | Every metric above is bounded by the reference data, so its own error structure was measured rather than assumed away. | Obs 361 (`docs/notes/working-notes.md:19878`), Obs 396 (`:26413`) | VERIFIED; POST-HOC (D14 settled: Results, as results-of-validation) | — |
| R8-02 | Precision is review-verified and position-marked: the 773-candidate phantom pool was adjudicated point by point (278 of 773 confirmed as distinct real mounds the students missed, plus one marking-pass extra; the rest resolved as duplicates or non-mounds) and every reviewed position hand-marked to the mound centre (±2.5 m), so reported precision is robust to GT omissions. | `results/deployment-oracle-2026-06-06/canonical-gt/standardised/README.md:23` ("278 model-detected survivors (of 773 reviewed) + 1 marking-pass extra, all at marked centres") and `:29-31` | VERIFIED | The **phantom pool** is the set of model detections absent from the student layer that were sent for human adjudication; needs a gloss. |
| R8-03 | Recall is a measured upper bound: on the GS sheets, configurations miss mounds the GT contains at a rate implying reported 55-map recall is inflated by ~2.4–2.7 %. | `results/working-precision/gs-miss-correlation.json`: `implied_55map_recall_inflation_factor` **1.0242** at 20 m and **1.0271** at 30/50 m | VERIFIED | — |
| R8-04 | The double-miss correlation between independent configurations is only 1.5–1.7× (4/435 GS double-misses), so mounds missed by *every* configuration — invisible to detection-led review — are rare but non-zero. | same file: `n_curator_in_bounds` **435**, `both_miss` **4**, `correlation_ratio` **1.5** (20 m) and **1.67** (30/50 m) | VERIFIED | — |
| R8-05 | In the opposite direction, an estimated ~370 residual long-range duplicate records among the unreviewed student majority deflate measured F1 by ≈ 0.03 at a balanced operating point. | `results/deployment-oracle-2026-06-06/canonical-gt/standardised/README.md:38-45` (~370, 95 % CI ≈ 200–660, hard ceiling 549; F1 ≈ 0.03 at a balanced ~0.85 operating point) | VERIFIED; Obs 396 | — |
| R8-06 | The net reference bias at point estimates is ≈ −0.017, rank-preserving to first order. | same README `:49-51` ("Net at point estimates ≈ −0.017 … the intervals span near-zero") | VERIFIED | The README adds "the intervals span near-zero", which the draft omits. |
| R8-07 | Deployment recall is therefore presented with a +3 %/+5 % sensitivity band rather than a point correction, the band chosen wide because the correlation estimate rests on four events. | `results/working-precision/gs-miss-correlation.json` (`both_miss` 4; `fisher_p` 0.281–0.323, i.e. the correlation is not itself significant) | **UNANCHORED (the band)** | The four-event basis verifies; the +3 %/+5 % band itself was found in no file opened this session, and its endpoints do not follow arithmetically from the measured 2.4–2.7 %. Either anchor the derivation or state it as a judgement. |

**Gaps.**

- The outline requires R8 to carry, "new per Obs 371", the 55-map
  reference's **two error structures** and the **R ≥ 50 m validity floor**.
  Neither appears.
- The S133 drafting note requires R8's description of the 55-map reference to
  reflect the *standardised* layer, in which the extension carries exact
  marked-centre distances, so the historical "25 m interval-censored rings"
  characterisation is retired. R8 correctly describes marked centres — but
  it describes r1, like R0 (see R0-02), not r2's three-class 5,018-mound
  composition.
- D14b settled that R8 speaks to **both** instruments, contrasted. R8 covers
  the GS curator GT only as the source of the double-miss estimate; the GS
  reference's own error structure is not characterised.
- The PI's framing note (the GS set functioned as a test set for
  configuration selection, then applied to a production set that happens
  also to have ground truth) is not stated here or in the missing seam.

**Rulings needed.**

1. Re-point R8 to r2's three-class composition and add the Obs 371 R ≥ 50 m
   validity floor? **Recommended: yes** — it is the same r1/r2 currency
   problem as R0 and is fixed in one pass with it.
2. Anchor or re-label the +3 %/+5 % band? **Recommended: state it as a
   judgement with the four-event reason given**, which is what the draft
   already implies and would then be honest about.
3. Add one sentence on the GS curator reference's own error structure so R8
   genuinely speaks to both instruments per D14b? **Recommended: yes.**
4. Keep R8 in Results as results-of-validation? **Recommended: yes, no
   change** — D14 is settled and the section is one of only two on budget.

---

## R9 — Selecting a configuration without ground truth

**Section question.** *On a new map region with no reference data at all, can
you still tell which of your pipeline configurations did best — using nothing
but the runs themselves?*

**LOFO** (leave-one-family-out) is the device: group the runs into families
by recipe, build a stand-in reference from the *other* families' detections,
and score each run against a reference that contains none of its own output.

**Prose word count: 587** (target ≈ 200; 2.9× over).

| # | claim | anchor | status | note |
|---|---|---|---|---|
| R9-01 | Building a bigger calibration reference is not the realistic alternative: the permutation machinery's noise scaling (null SD ∝ 1/√N_tiles, validated at both ends of the corpus) prices the counterfactual. | Obs 366 § 2, `docs/notes/working-notes.md:20769-20778` ("null SD scales as s/√N_tiles, validated at both ends": GS 487 tiles null SDs 0.0113–0.0148; 55-map 8,541 tiles 0.0026–0.0058) | VERIFIED; POST-HOC (`preregistered` field absent — R9 is anchored to a findings document, not a register row) | — |
| R9-02 | Grounding the decisions the GS instrument got wrong would have needed ~10–20 sheets (~900–1,900 mounds) per decision axis at 80 % power — up to roughly a third of the eventual deployment corpus, curated up front. | Obs 366 § 2 table, `docs/notes/working-notes.md:20781-20787`: vote threshold ~12 sheets / ~1,100 mounds; temperature ~20 / ~1,900; min-vs-HIGH ~10 / ~900. 20/55 = 36 % | VERIFIED | `results/gtfree-selection/gtfree-selection-findings.md:11` rounds the same table to "~1,000–2,000 mounds" — a minor internal inconsistency between the findings document and the Obs it cites. The draft matches the Obs. |
| R9-03 | And decisively, the sheets would have to be sampled from the *deployment* population: the vote-threshold direction actually reversed on the curated GS sheets, so more tiles of the same sheets would have converged confidently on the wrong answer. Representativeness, not size, was the binding failure. | Obs 366 § 2 (i), `docs/notes/working-notes.md:20797-20801` ("the threshold direction reversed on the curated GS sheets … More tiles of the *same* sheets [would not help]") | VERIFIED | The strongest methodological claim in the Results and the one the Discussion's Seeds 1 + 2 rest on. |
| R9-04 | Deploying the calibration tie-set instead is affordable: threshold sweeps are free post hoc and pass pools nest, so the end-of-calibration tie-set collapses to four proposer pools — ~25 passes, ~$733 audited flex on the 8,541-tile corpus. | Obs 367, `docs/notes/working-notes.md:21003` (title) and `:21050` (table total 25 passes / ~$733; exact sum $733.04) | VERIFIED | — |
| R9-05 | That is within ~2 % of what the study's five deployment campaigns actually spent (≈ $722, audit § 6) — the programme converged on the minimal covering design incrementally, without having planned it. | Obs 367, `docs/notes/working-notes.md:21063-21070` ("The project actually spent ~$722 across the four deployment campaigns plus the uplift (audit § 6 total)"; "the gap is within the retry/lower-bound margin") | VERIFIED | "four campaigns plus the uplift" = five; the draft's phrasing is fine. |
| R9-06 | The LOFO construction: union the other three families' detections, single-linkage cluster at 50 m, keep clusters supported by ≥ 2 distinct families, score each cell against its own family's held-out reference — so no cell is ever evaluated against a reference containing its own family's detections. | `results/gtfree-selection/gtfree-selection-findings.md:15-27` (four families; union, single-linkage at 50 m, ≥ 2 distinct families, ≥ 3 as sensitivity; "the anti-circularity device the design depends on") | VERIFIED | — |
| R9-07 | It ranks the eight deployment cells at Spearman ρ = +0.881 against the true board; the standardised re-tiering preserved the full rank order, so ρ is unchanged. | same file `:55` ("**Spearman(pseudo, true) = +0.881** over all eight cells") | VERIFIED | The parenthetical "+0.857 over the seven text cells" on the same line is a *Spearman*, easily confused with the p-value at R9-08. |
| R9-08 | The GT-free top pick (TH7-k3) is statistically tied with the true winner on the real board: p = 0.127 on the canonical reference, and the tie deepens to p = 0.857 on the standardised one. | `results/55map-leaderboard/55map_leaderboard_50m.json` pairwise T03-k3 vs TH7-k3: p **0.1271**; `..._standardised.json`: p **0.8569** | VERIFIED | On **r2** — the reference every § R7 figure now uses — the same pair reads p **0.8553** (`55map_leaderboard_50m_r2.json`). R9 is two reference revisions behind § R7. |
| R9-09 | The "miss" therefore sits inside a tie the 8,541-tile instrument itself cannot resolve, and the cost meta-rule then breaks the residual tie at exactly the scope § R6 qualified it to. | R9-08 plus Obs 357 / Obs 362 via `min-vs-high-thinking-pv`'s `working_notes_obs` | VERIFIED as an inference | Depends on § R6, which is not inventoried. |
| R9-10 | The consensus must be permissive: requiring unanimity of the other families *inverts* the ranking (ρ = −0.095), because a unanimous reference amplifies the double-miss blind spot § R8 measures. | `results/gtfree-selection/gtfree-selection-findings.md:62-66` ("Spearman −0.095 all eight; −0.536 text-only; reference 3,285–3,654 points") | VERIFIED | — |
| R9-11 | The pseudo-ranking is therefore precision-tilted, and the practitioner should keep the recall-permissive lean the threshold-transfer lesson (§ R7) independently recommends. | R9-10 plus R7.1-10 | VERIFIED as an inference | A genuinely useful convergence of two independent results; worth stating as such. |
| R9-12 | The validation is a retrodiction on one corpus, one symbol type, and eight cells; a prospective, preregistered application to a new corpus is the natural test. | `results/gtfree-selection/gtfree-selection-findings.md` § 4 ff.; register has **no row** for this analysis (the draft says so explicitly) | VERIFIED (self-disclosed) | The honesty here is the section's main asset. |
| R9-13 | The four-step field protocol (deploy the tie-set → rank by LOFO vote ≥ 2 agreement → break the residual tie by cost with a recall-permissive lean → sanity-check with the free vote-distribution and density diagnostics) is specified in the findings document § 5. | `results/gtfree-selection/gtfree-selection-findings.md:88-95` (steps 1–2 read verbatim; the section is § 5) | VERIFIED (D15 settled: the protocol-as-recipe goes to **Discussion**) | The draft names the protocol's four steps here, which D15 routed to Discussion. One pointing sentence is what D15 allows. |

**Gaps.**

- R9 alone has no register row. The draft discloses this, but it means the
  section's numbers have no `manually_verified_at` signature anywhere —
  unlike every other Results section.
- The pseudo-GT sizes (4,399–4,539 points against a true GT of 5,161) are in
  the findings document and not in the prose, though they are what make the
  ρ = +0.881 interpretable.
- R9's figures are on the **canonical** and **standardised** chains while
  § R7 is on **r2**; nothing tells the reader that.

**Rulings needed.**

1. Author a register row for the GT-free selection analysis and sign it?
   **Recommended: yes** — it is the only Results thread outside the
   register, and the register is the paper's machine-readable backbone.
2. Re-run or re-quote R9-08 on r2 (p = 0.8553) so R9 and § R7 share a
   reference? **Recommended: re-quote on r2 and note that no verdict
   moves** — the tie is unaffected and the currency question disappears.
3. Cut the four-step protocol here to one pointing sentence per D15?
   **Recommended: yes** — it saves ~70 words and removes a Discussion
   double-telling.
4. Keep R9 in Results at all, given the 3.3× budget overrun?
   **Recommended: yes, compressed to ~250 words** — it is the section a
   survey-archaeology reader can act on, and D15 already settled its
   Results/Discussion split.

---

## Changelog

### 2026-09-12 — Original publication

Per-section claims-with-anchors inventory for R0, R1, R2, R4, R5, R7 (lead-in,
R7.1, R7.2, R7.3), R8, and R9; R3 and R6 left as placeholders pending the
parallel K-ladder (pass-count) job. Cross-section summary follows in the
next commit.
