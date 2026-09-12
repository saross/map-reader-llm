# Results — structural outline (spine AGREED; section calls still open)

> **Status**: collaborative structure document. **ALL TWENTY-TWO
> DECISIONS ARE SETTLED** (D1–D4 in Session 118; D5–D17 in Session
> 133; D18–D22 in Session 153, the PI's rulings of
> 2026-09-12). Prose drafting can begin per the agreed structure, gated only
> by the D17 reconciliation block (its own pre-run-reviewed pass,
> before final Results prose). This is a
> decision-forward outline, **not** prose. Prose drafting for a section waits
> until that section's structure is agreed. `docs/paper/results-draft.md`
> remains the **zero-draft** reference (claims and anchors live there) and is
> not extended until the relevant structure lands.

## Revision history

| rev | date | change |
|---|---|---|
| v0 | 2026-06-14 | Strawman; 15 decisions D1–D15 raised, all OPEN (Session 114). |
| v1 | 2026-07-27 | **D1–D4 settled** (Session 118). Spine reorganised into two explicit parts with a named seam; anti-double-telling convention added as a standing rule; D16–D17 raised on preregistration handling; decision register updated. |
| v2 | 2026-08-15 | **D5–D6 settled = A** (Session 133, PI in-session). D6 carries a supplement rider (full sweeps in supplementary material; data-derived headlines in the body). E60 note added to the prereg section (the "no erratum covers it" line at D17's inventory was written the day before E60 landed). |
| v3 | 2026-08-15 | **D7–D10 settled per REC** (Session 133, PI in-session): factor split yes; both boards with the temperature-qualifier drafting note; dividend retirement forward-referenced; tile size folded into R4. |
| v4 | 2026-08-15 | **D11–D12 settled per REC** (Session 133, PI in-session): six robustness axes compressed to meta-rule + table (detail → supplement, Obs 362 scope-qualification stays in body); recall-ceiling mechanism elevated to its own hub subsection within R5. |
| v5 | 2026-08-16 | **D13 settled = A + merged (b)/(c)** (Session 133, PI in-session): carry-forward primary; deployment gap framed against the Tier-1 set with no single-oracle crown; E56 cited at the relaxed rows. D13 block figures refreshed to standardised vintage; the threshold-axis decomposition punchline recorded. |
| v6 | 2026-08-16 | **D14/D14b settled = A/A** (Session 133, PI in-session): R8 stays in Results as results-of-validation, whole at the head of the validity block. PI framing note recorded (GS = test set for configuration selection, 55-map = production with the luxury of GT to audit generalisation) + the standardised-reference drafting note for R8's error-structure description. |
| v7 | 2026-08-16 | **D15 settled = C; D16 settled = A + Discussion prereg-retrospective rider; D17 settled = A + schema amendment** (Session 133, PI in-session). **All seventeen decisions settled.** D17 currency note added (family FDR, CMT-0106, E45 correction, E60 all landed since the block was drafted); the reconciliation block queued as the gate before final Results prose. |
| v8 | 2026-08-17 | **D17 reconciliation block EXECUTED** (S134, `planning/s134-d17-reconciliation-block-2026-08-17.md`): vocabulary v2 + 31-row register + errata E74–E77/E59-update + the generated hypothesis-outcome table (`results/hypothesis-outcome-table/`). Gate-status note added at the decision register. PI walk pending (`reports/s134-relabel-walk-dossier.md`); prose drafting begins after the walk. |
| v9 | 2026-09-12 | **D18–D22 SETTLED** (Session 153, PI rulings of 2026-09-12 on the claims inventory): r2 as the single reference revision across Results; the Gemini 3.7 stack as the headline, with "models improve, the calibrated configuration carries across" as a Results-level claim; information into tables, not repeated in prose; the GS stride/geometry programme promoted to its own block, **§ R1b**; exhibits-first. A **Figures and tables** section added per D22. |

*Brief by design — consult `git log docs/paper/results-outline.md` for the
full history and diffs.*

## How to read this

- **Part A** holds the spine-level calls and the standing conventions that
  govern every section below.
- **Part 1** (characterisation, gold standard) and **Part 2** (deployment at
  scale) walk the sections at subsection/claim granularity: each carries its
  *purpose*, its *load-bearing claims* (with the evidence anchor), and any
  *in-section decisions*.
- **Decision register** at the very bottom lists every `Dn` in one place with
  its status, so settled calls are visible and open ones are easy to find.

---

## Part A — spine & cross-cutting decisions

### ✅ D1 — the overall spine — SETTLED (A, realised as an explicit two-part structure)

**Decision (Shawn, 2026-07-27)**: architecture-ascending (option A), with the
gold-standard→deployment seam made explicit.

**How it is realised.** Walking the original spine by instrument shows R2–R6
are *all* gold standard and R7 is deployment — so the ascending spine was
already nearly "characterise, then deploy". Settling **D4** (below) moves the
transfer table and reversal out of R6 into R7, which makes R6 purely a GS
result and removes the one objection originally raised against a
characterise-then-deploy structure ("it splits the cost story"). D4 splits
that story deliberately, to stop the double-telling.

Options A and C therefore converge. What remains is not a restructure but a
**relabelling**: present two named parts rather than nine flat subsections.

```text
PART 1 — CHARACTERISATION (gold standard, 4 maps / 487 tiles)
  R0 reading guide → R1 precisions → R1b tile geometry (per D21) →
  R2 single-pass → R3 consensus →
  R4 proposer–verifier → R5 verifier robustness → R6 cost frontier (GS)

SEAM — what carries forward, and what changes (§ S)

PART 2 — DEPLOYMENT (55 maps / 8,541 tiles)
  R7 deployment board (+ transfer, reversal, buyable gap) →
  R8 what the ground truth can support → R9 selecting without ground truth
```

**Why explicit parts** (the case Shawn made, plus three more):

1. Part 1 *is* the option-space exploration — it exercises configurations the
   deployment run never revisited. Naming it that way makes this structure
   rather than apology.
2. It is honest about the instrument change: different corpus, different GT
   provenance, different working buffer, different resolving power.
3. It stops a reader conflating **0.890 (GS, F1@20 m)** with **0.815
   (deployment, corrected-F1@50 m)** — a very likely confusion otherwise.
4. The deployment reversal gets a natural home: it is the first thing Part 2
   says.

**Two residual straddles**, both small and both flagged in place: **R1**
(working precisions — covers both instruments) and **R8** (GT epistemics —
covers both the GS curator GT and the 55-map canonical GT). See D6 and D14.

### ✅ D2 — where the headline lands — SETTLED (A, extended to both instruments)

**Decision (Shawn, 2026-07-27)**: state the headline early — and lay out
**both** the GS and the deployment headline early, not just the GS one.

- A short "principal results" stub at the end of R0 gives both numbers with
  their instruments and buffers attached: GS **F1@20 m 0.890 / MCC 0.790**;
  deployment **corrected-F1@50 m 0.815** (carry-forward, per D13).
- Each is then derived in full in its own home (R4 and R7).
- Stating them together up front is what makes the two-part structure legible
  from the first page, and pre-empts the conflation D1 guards against.

**⚠ Numbers superseded by D19 (PI, 2026-09-12)**: the
placement call above stands unchanged, but the two numbers the stub
quotes do not. The headline is now the all-3.7 stack — GS 0.9265 on the
screen union / 0.9190 Tier 1 on the Era-2 board frame, deployment r2
0.8827 carried / 0.8871 oracle — with **0.890 / 0.790** and **0.8162**
retained as the Gemini 3 *calibrated* result the family step is measured
against. See [§ D19](#-d19--the-papers-headline-is-the-gemini-37-stack--settled-supersedes-d2s-numbers).

### ✅ D3 — the F1-vs-MCC theme — SETTLED (A, threaded)

**Decision (Shawn, 2026-07-27)**: distributed but explicitly threaded — name
it once at R2, call back at R4 and R7, so the reader tracks one recurring
theme rather than three coincidences.

Threading is governed by the anti-double-telling rule below: R2 is the
theme's **home**; R4 and R7 carry one-clause callbacks with a section
reference, not restatements of the mechanism.

### ✅ D4 — the GS-cost / deployment-economics split — SETTLED (A, split)

**Decision (Shawn, 2026-07-27)**: split. Cost, cost–output trade-offs, and the
Pareto frontier are discussed at **both** levels, but each result is told
once:

- **R6 (Part 1)** — the GS cost frontier: the pass ladder priced, the
  efficient set, all seven rungs inside one F1 tier on GS.
- **R7 (Part 2)** — deployment economics: the transfer table, the min→HIGH
  reversal, the buyable gap, and what the frontier costs at 55-map scale.

The seam section carries the one-sentence bridge ("the GS frontier is a
statement about an instrument that cannot resolve ±0.03; deployment prices
what GS could not distinguish").

### 📐 Standing convention — one home per result (no double-telling)

Shawn's general instruction (2026-07-27): *structure tightly, avoid
double-telling.* This is the operative rule for drafting every section:

> **Every mechanism, number, and finding has exactly one home. Everywhere else
> it appears as a one-clause callback carrying a section reference — never a
> restatement, never a re-derivation.**

The known repeat-offenders, with their assigned homes:

| item | home | callbacks allowed at |
|---|---|---|
| min→HIGH reversal | R7 | R6 (one clause) |
| F1-vs-MCC trade | R2 | R4, R7 (D3 thread) |
| recall-ceiling mechanism | R5 (hub, per D12) | R3, R4, R6 |
| working precisions | Methods (per D6) | R1 recap, seam |
| diversity dividend → its retirement | R3 → R5 | forward-ref only (D9) |
| cost / Pareto frontier | R6 (GS), R7 (deployment) | seam bridge |
| GS stride/geometry programme | R1b (per D21) | R4 (one clause), R7.2 (one clause) |

### The 2026-09-12 PI rulings (D18–D22)

> Five further spine-level calls, taken by the PI on 2026-09-12 on the
> evidence of `docs/paper/results-claims-inventory-2026-09-12.md`. They are
> numbered in the same D-series as D1–D17 and are all SETTLED. (The
> `Dnn` *defect* numbers used in the errata — defect D20 for E83, defect
> D13, defect D15 — are a separate series and are not these.)

#### ✅ D18 — one reference revision across Results — SETTLED (r2 throughout)

**Decision (PI, 2026-09-12; ruling 1)**: the whole of Results quotes
**reference r2**. Figures that exist only on an older reference move to
the supplement; r1, the canonical chain, and the standardised chain are
named in the body only where a *bet* was assessed on them.

- Executed in `results-draft.md` the same day: §§ R0, R8, and R9
  re-pointed (§ R7 had been on r2 since erratum E84). Four § R8
  error-structure figures have no r2 twin and carry
  `[REF: r1 — supplement candidate per ruling 1]` for routing.
- **Consequence for R6**: its transfer table is on the standardised
  vintage and is *not* swept here — R6 is reserved for the parallel
  K-ladder job and inherits this decision when that lands.

#### ✅ D19 — the paper's headline is the Gemini 3.7 stack — SETTLED (supersedes D2's numbers)

**Decision (PI, 2026-09-12; ruling 2)**: the headline is the **all-3.7
text stack**, and the Gemini 3 board is the **calibration story that got
there**.

- GS: **F1@20 m 0.9265** on the 791-candidate screen union, **0.9190** on
  the Era-2 487-tile board frame, where it sits in **Tier 1** (rank 2 of
  79 cells).
- Deployment (r2, 50 m): **0.8827 carried (T2)** and **0.8871 oracle
  (T1)**.
- The Gemini 3 recipe's **0.890 / 0.790** (GS) and **0.8162**
  (deployment carry-forward) are retained as the *calibrated* result and
  the thing the family step is measured against — not as the headline.
- **D2's spine call stands** (state the headline early, both instruments
  together); **D2's two numbers are superseded** by the four above.
- **A Results-level claim to place**: *models keep improving, and the
  calibrated configuration carries across model versions, at least
  within the Gemini family.* Recommended home **§ R7.3**, where the
  verifier-seat result and the 3.8 tie already establish it, with a
  one-clause echo in **§ R0**'s headline stub so the reader meets it
  before Part 1. This is the claim that makes the calibrate-then-deploy
  spine pay off rather than date it.

#### ✅ D20 — word budget: move information into tables, do not repeat it in prose — SETTLED

**Decision (PI, 2026-09-12; ruling 3)**: the PI's "paper-b" practice.
Information goes into a table once and is *not* restated in the text;
the supplement is referenced rather than summarised. Every major section
and finding must be **present**; prose polish is explicitly **not** the
current goal, because the paper will be re-drafted from the outline.

- Operative consequence: drafting effort goes to *coverage and
  placement*, not sentences. A block that exists as a claims-with-anchors
  list plus a table pointer is complete for this pass.
- This supersedes nothing; it sets the standard against which D5, D7,
  D11, and D13's compressions are executed.

#### ✅ D21 — the GS stride/geometry programme gets its own Results block — SETTLED (§ R1b)

**Decision (PI, 2026-09-12; ruling 5)**: the tile-size × overlap ×
pass-count grid and the stride ladders get **their own Results block**,
not a fold into R4 and not supplement-only. Realised as **§ R1b**,
between R1 and R2, so no existing section renumbers. The block's claims-with-anchors outline is
[§ R1b](#r1b--tile-geometry-tile-size--overlap--pass-count-and-the-stride-ladders),
between the R1 and R2 blocks of Part 1 — twenty-three claims, each
anchored.

- This closes the gap the inventory found at R7.2-15: § R7.2's
  "(§ R1, Obs 435)" cross-reference pointed at a section that did not
  contain the GS geometry grid, and the GS stride ladder on which both
  deployment carried points were *selected* was reported nowhere.
- It also gives the five uncited `paper_section: Results` register rows
  (`grid-tilesize-overlap-2026-08-18`, `grid-postverifier-2026-08-18`,
  `stride-plateau-2026-08-25`, `stride-winner-ladder-exact-2026-08-25`,
  `h13-overlap-2026-08-18`) a home, and is where H13 — a registered
  hypothesis — is discharged.

#### ✅ D22 — exhibits first: figures and tables carry what they carry better — SETTLED

**Decision (PI, 2026-09-12; ruling 6)**: anything communicated more
directly, clearly, or concisely by a figure, chart, or table is done that
way. Per-block assignments are in
[§ Figures and tables](#figures-and-tables), after the decision register.

- The inventory established that Results currently promises **one table
  and no figure**, while
  `results/55map-final-board-r2-2026-09-06/significance-groups.png`
  already exists at publication quality and is referenced nowhere.

---

## Part 1 — Characterisation (gold standard: 4 maps, 487 tiles)

### R0 — Reading guide: instruments, metrics, conventions

- **Purpose**: orient the reader to the two instruments and the one
  statistical machinery, so each later result can be read correctly.
- **Claims**: two-instrument framing; headline metric = buffered F1 at an
  empirical working precision + tile-MCC; tile-swap permutation + BH-FDR +
  greedy-clique tiering throughout. Anchor: §R0 of the zero-draft. <!-- [E83]
  Tie sets are now the Hsu MCB admissible set; the greedy-clique rule is
  superseded (defect D20). This methods claim must change with the sibling
  sentence already flagged in results-draft.md §R2. -->
- **Now also carries** the two-headline stub (per D2, with D19's numbers)
  and a pointer to the preregistration status statement (per D16).
- **Also carries, per D19 (2026-09-12)**: a one-clause echo of the
  Results-level claim that *models keep improving and the calibrated
  configuration carries across model versions, at least within the
  Gemini family* — its derivation home is § R7.3, and the echo here is
  what lets the reader read Part 1 as calibration rather than as a dated
  ceiling.
- **✅ D5 SETTLED = A** (PI, Session 133, 2026-08-15): trim —
  orientation (2–3 lines) stays in R0, stats-convention detail moves
  to Methods.

### R1 — Working precisions are empirical, not free parameters

- **Purpose**: justify the buffer radii as data-derived properties, not
  analyst choices.
- **Claims**: text plateau 30 m, image 75 m, modality dominates architecture
  (`gs-plateau-characterisation`); 55-map 50 m from converging lines
  (`55maps-csr-noise-floor`). Anchor: §R1.
- **⚠ Updated 2026-07-27 (Obs 371)**: the 55-map 50 m buffer is a **floor, not
  a generous choice**. Below R = 50 m the extended GT reduces to the reviewed
  student GT, so sub-50 m Track-2 figures penalise correct detections of
  student-missed mounds. Do **not** repeat Obs 360's "partly a GT-composition
  artefact" framing — the bias runs the other way. The two error sources are
  distinct: ~20–25 m continuous jitter on student positions; 25 m
  interval-censored rings on phantom match distances.
- **Straddle note (D1)**: this subsection covers both instruments, so it sits
  in Part 1 but forward-references the seam. If D6 resolves to Methods, the
  straddle disappears and only a recap line remains here.
- **✅ D6 SETTLED = A** (PI, Session 133, 2026-08-15): Methods carries
  the derivation; Results keeps a one-line recap of the chosen radii,
  written so the reader sees they were derived, not chosen. The
  straddle dissolves (only the recap line remains in R1).
  **PI rider**: a supplement/appendix reports the **full sweeps for
  all results at the previously-agreed threshold grid** (the 14-buffer
  5–150 m standard); the paper body emphasises the data-derived
  headline precisions (30 m text / 75 m image / 50 m 55-map). PI
  wording: "in a supplement or appendix we should report full sweeps
  for all results using the thresholds we previously agreed on, then
  in the paper we should emphasise the data-derived headlines."

### R1b — Tile geometry: tile size × overlap × pass count, and the stride ladders

> **New block, per D21 (PI ruling 5, 2026-09-12).** Numbered **R1b** —
> between R1 and R2 — so that no existing section renumbers. It is a
> **claims-with-anchors list, not prose**: per D20, this pass establishes
> coverage and placement, and the paper is re-drafted from the outline.
>
> **Why it exists.** The gold-standard geometry programme is the ISPRS
> skeleton's exhibit (i) half that had no section anywhere in the draft.
> § R7.2 already cross-referenced it as "(§ R1, Obs 435)" — a section
> that does not contain the geometry grid — and the GS stride ladder on
> which § R7.2's two deployment carried points were *selected* was
> reported nowhere, leaving that block's central discipline claim
> uncheckable by a reader.
>
> **Registration status.** Post-hoc (E41-class) throughout, with one
> registered leg: **H13** (overlap/stride) is `registered-exploratory`
> and is discharged here — the only place in Results where it is. Three
> of the five governing register rows are unsigned
> (`manually_verified_at: None`): `grid-tilesize-overlap-2026-08-18`,
> `grid-postverifier-2026-08-18`, `h13-overlap-2026-08-18`.
> `stride-plateau-2026-08-25` and
> `stride-winner-ladder-exact-2026-08-25` are signed 2026-08-28.
>
> **Scope boundary.** The *deployment* stride leg is § R7.2's and is not
> re-told here; R1b ends on a one-clause hand-off. Everything below is on
> the GS instrument, 487-tile common footprint, F1@20 m.

| # | claim | anchor |
|---|---|---|
| R1b-01 | The design is a clean 2 × 2 crossing tile size (384, 512 px) with overlap (12.5 %, 50 %) at K = 10 proposer passes per cell, one configuration throughout (`detect_brief-text`, gemini-3-flash-preview, MINIMAL, T = 0.7), so only the two geometry factors vary; 30,130 calls, **$18.53 billed flex**, scoring $0. | `results/grid-2026-08-18/findings.md:10-22,215` |
| R1b-02 | **At a single pass both bigger tiles and less overlap win.** 50 % overlap costs +0.1200 F1 at 512 px and +0.1348 at 384 px; 384 px costs −0.0824 at 12.5 % overlap and −0.0972 at 50 %. All four contrasts exclude zero (paired tile bootstrap, B = 10,000, seed 42, E82). | same file `:77-80` |
| R1b-03 | The **interaction is unresolved**: difference-of-differences −0.0148 [−0.0552, +0.0268], p = 0.4902. The two factors are additive to within the instrument's resolution. | same file `:81` |
| R1b-04 | **Mechanism — overlap manufactures its own consensus.** Within-pass 20 m deduplication records how many overlapping tiles independently reported a location; corroborated detections (c ≥ 2) are 7.0 % / 7.7 % of the 12.5 % cells but **40.8 % / 41.7 %** of the 50 % cells. At 12.5 % the same filter is demolition rather than filtering; at 50 % it keeps recall near 0.87–0.89 while lifting precision from 0.156 → 0.531 (512 px). | same file `:101-117` |
| R1b-05 | **Under aggregation the overlap ranking inverts and the tile-size ranking does not.** Best cell per configuration at K = 10: 512/50 % **0.7518**, 384/50 % 0.7205, 512/12.5 % 0.6759, 384/12.5 % 0.6475. | same file `:133-140`; register `grid-tilesize-overlap-2026-08-18` |
| R1b-06 | **Passes do not substitute for overlap**, on all three counts at once: 384/12.5 % at K = 10 (union recall 0.8925, best F1 0.6475, $2.91) loses to 512/50 % at K = 3 (0.9229, 0.7429, $1.60). More overlap is better *and* cheaper. | same file `:176-185` |
| R1b-07 | Sharper still: **one single pass** of 512/50 % (F1 0.7121, $0.53) beats **ten** passes of either 12.5 % cell (0.6759 at $1.90; 0.6475 at $2.91). Overlap buys corroboration inside one pass; extra passes buy the same corroboration at K times the price. | same file `:163,187-191` |
| R1b-08 | **The verifier stage reverses the tile-size ranking.** Post-verifier board (best F1@20 m per cell, 9,133/9,133 candidates verified, zero failures): 384/50 % **0.8961**, 512/50 % 0.8815, 384/12.5 % 0.8677, 512/12.5 % 0.8311. | same file `:337-345`; register `grid-postverifier-2026-08-18` |
| R1b-09 | **The overlap reversal survives the verifier, at about half the margin**: (12.5 − 50) = −0.0504, p = 0.0004 at 512 px and −0.0285, p = 0.0208 at 384 px, against a K = 10 consensus baseline of −0.0758, p = 0.0004 and −0.0730, p = 0.0026. The corroboration filter and the verifier are partially redundant, not interchangeable. | same file `:360-366,389-397` |
| R1b-10 | **The like-for-like baseline is what makes the reversal statable.** The pre-verifier arm is the registered K = 10 consensus operating points scored as single sets on the same instrument — (384 − 512) = −0.0284, p = 0.281 at 12.5 % and −0.0312, p = 0.089 at 50 %, **both non-significant** — not the single-pass contrasts of R1b-02. So: aggregation alone erodes 512 px's significant single-pass advantage to non-significance, and the verifier then flips the sign, significantly at 12.5 % (+0.0366, p = 0.034) and unresolved at 50 % (+0.0147, p = 0.231). | same file `:351-366,368-375`; register row's 2026-08-24 audit revision |
| R1b-11 | The verifier's gain over the consensus-only board is **+0.130 to +0.220**, largest exactly where consensus-only was worst (the two 384 px cells, +0.220 and +0.176), because the verifier recovers the precision 384 px lacked while its higher union-recall ceilings (0.8925 / 0.9509 against 0.8715 / 0.9416) are the resource a verifier cannot create. **→ D12 callback to R5's recall-ceiling hub**; the Obs 352 256 px rescue at a new tile-size pair. | same file `:347-349,376-388` |
| R1b-12 | **Consensus and verifier are complements, not substitutes**: every cell's best operating point keeps a vote threshold (k ≥ 5..10) on top of the probability threshold, and the pure-verifier k = 1 board tops out at 0.8153, trailing the stacked optimum in every cell by 0.052–0.203. | same file `:399-404`; register `grid-postverifier-2026-08-18` |
| R1b-13 | **Stride is not the lever.** The nine-cell verified board's iso-stride contrasts are all non-significant, but the direction is consistent: **at fixed stride, 384 px is at or above every alternative at every stride tested, and never below** — the study's long-standing 384 px preference surviving the one design that could have unconfounded it. | `results/stride-2026-08-25/findings.md:44-53`; Obs 435, `docs/notes/working-notes.md:28698` |
| R1b-14 | **The optimum is interior.** The 384 px ladder reads 0.8677 (stride 336) → **0.8982** (256) → 0.8961 (192) → 0.8860 (144): 336 → 256 is significant (+0.0305 [+0.0052, +0.0564], p = 0.020), the top is flat (256 vs 192: +0.0020, p = 0.862), and the 144 rung falls away (p = 0.297 / 0.360). The stop rule fired at stride 144. | same file `:55-61` |
| R1b-15 | **The exit criterion resolves to plateau, not winner.** The 13-cell tiered board gives **6 of 78 pairs significant, all involving 512/12.5 %**, with Tier 1 holding the other twelve cells including all four incumbents; the best new cell ties the grid winner (+0.0020, p = 0.862) and at 30 m the top three are indistinguishable to the third decimal. **No new GS F1 high comes from geometry**: the leading shelf stays at ~0.896–0.898 @ 20 m, ~0.903 @ 30 m. | same file `:63-70,144-146`; register `stride-plateau-2026-08-25` |
| R1b-16 | **What geometry bought was cost, not F1.** 384/33.3 % runs 820 tiles per pass against the grid winner's 1,398 — the same performance at ~59 % of the calls — for ≈ $6.6 all-in on this footprint against ≈ $10.7 (384/50 %) and ~$50-class for the HIGH-thinking incumbents that share the 30 m shelf. | same file `:72-81`; Obs 435 |
| R1b-17 | **The exact winner ladder** (384/33.3 %, N ∈ {1, 3, 5, 10}, exactly re-verified, 4,958/4,958 candidates, zero failures): F1@20 m 0.8677 / **0.8911** / 0.8856 / 0.8982 at $1.38 / **$2.64** / $3.81 / $6.56 all-in flex. N ∈ {3, 5, 10} are one statistical point; N = 3 reaches 0.8911 for $2.64 — within 0.007 of the full K = 10 winner at 40 % of its cost and ~19× cheaper than the $50-class incumbents. | same file `:149-163`; register `stride-winner-ladder-exact-2026-08-25`; `results/stride-2026-08-25/plateau_analyses.json` → `winner_ladder_exact` |
| R1b-18 | **The GS ladder that § R7.2's carried points were selected on, made checkable.** At prob_t 0.15 the A geometry's k-curve argmax is **k = 8** with a flat top at k 6–9 (within 0.005), and the B geometry's is **k = 10** with a single-point top — exactly the (0.15, k8) and (0.15, k10) operating points § R7.2 says were declared before launch. This is the anchor a reader needs to verify that the deployment carried points were chosen on GS and not on the deployment sweeps. | `results/stride-2026-08-25/plateau_analyses.json` → `k_curves.g384_ov128` (`best_k` 8, `k_within_0p005` [6,7,8,9]) and `k_curves.g384_ov192` (`best_k` 10); `results/stride-2026-08-25/findings.md:147-148` |
| R1b-19 | **H13, the registered leg: prediction split.** The registered *mechanism* is confirmed and the registered *performance* claim falsified. F1 falls monotonically as overlap rises — arm A (12.5 %) 0.5578, arm B (25 %) 0.5198, arm C (50 %) 0.4025 — with all three paired contrasts excluding zero. Recall behaves exactly as registered (0.7379 → 0.7844 → 0.8717); precision falls faster (0.4484 → 0.3887 → 0.2616). | register `h13-overlap-2026-08-18` (`registered-exploratory`, **unsigned**) |
| R1b-20 | H13's edge mechanism **localises and is real but small**: the ten mounds arm A could only ever see within 100 m of a tile edge go from recall 0.2667 (A) to 0.7667 (B) to 0.9333 (C), against 0.7468 → 0.7847 → 0.8706 for the other 528. The gain is concentrated in under 2 % of mounds — too few to pay for the precision lost elsewhere, so **every additional API dollar spent on overlap buys negative F1**. | same register row |
| R1b-21 | The registration's own cost multiplier for H13 arm C (~2×) was **wrong before any result existed**: arm C needs **2.99×** the tiles. A disclosure-grade point about the registration, not about the result. | same register row's `predicted_outcome` (authoring disclosure) |
| R1b-22 | **Selection caveat, stated once for both boards**: every operating point is F1-selected on the same 487 tiles it is scored on, and the post-verifier sweep offers ~4–5× the consensus sweep's selection space, so the contrasts condition on that selection (E41-class). | `results/grid-2026-08-18/findings.md:384-388`; register `grid-postverifier-2026-08-18` |
| R1b-23 | **Hand-off to § R7.2, one clause, no re-telling**: the two geometries selected here went to the 55-map corpus, where their GS-selected carried points transferred with taxes of +0.0036 (A) and +0.0081 (B) against the incumbent's +0.0324, and B beat A — the pre-named P6 failure. | `results/stride55-2026-08-27/findings.md:40-42,75-76`; register `stride55-sweep-oracle-2026-08-27`, `stride55-ladder-2026-08-27`, `stride55-a5-vs-b5-2026-08-27` |

**Twenty-three claims.** Load-bearing for the paper: R1b-05 (the
aggregation inversion), R1b-08 to R1b-11 (the verifier reverses tile
size, and the like-for-like baseline that licenses saying so), R1b-15
(plateau, not winner), R1b-17 (the ~19× efficiency result the ISPRS
skeleton's exhibit (ii) also draws on), R1b-18 (the checkable GS ladder),
and R1b-19 (H13 discharged).

**Cross-references out** (one clause each, per the anti-double-telling
convention): **R4** gains a clause noting that the tile-size optimum's
architecture dependence is corroborated at a second tile-size pair here;
**R5** is the recall-ceiling hub R1b-11 points back to; **R7.2's**
"(§ R1, Obs 435)" is re-pointed to § R1b.

**Not in this block**: the deployment stride leg (§ R7.2), the pass-count
ladder as a *cost* object (§ R6 — and the parallel K-ladder job will
extend it), and the consensus-only per-cell sweeps (Supplement S2).

### R2 — Single-pass baselines: a floor, and which factors moved it

- **Purpose**: establish the ~0.63 single-pass floor and report what the
  preregistered single-factor sweep did and did not separate.
- **Claims**:
  - Floor: 36 single-pass cells → 4 tiers, a broad 20-cell Tier-1 tie
    (F1 0.583–0.631); the GS set cannot separate the stronger configs
    (`era1-single-pass-baseline-matrix`). **Load-bearing.** <!-- [E83]
    20 → 15 under MCB. -->
  - Modality: no clean F1 win, but drives the F1↔MCC trade (text→F1,
    image→MCC). **This is the home of the D3 thread.**
  - Temperature: T=0.0 > T=0.7, a clean Tier-1/Tier-2 split
    (`n1-baseline-matrix-384`, Pro). <!-- [E83] The clean split does not
    exist: the MCB set at B = 10,000 is 3 of 18 and spans both temperatures
    (only high-T0.7 excluded; E83 correction block 2026-08-20). Restate as a
    point-estimate ordering plus one exclusion. -->
  - Inert: prompt elaboration (H1), ordering (H4), negative-text (H5),
    example-library (H8) — all inside the tie.
  - Signpost: thinking level is inert-to-harmful at single pass; its effect
    arrives under consensus (→ R3).
- **✅ D7 SETTLED = yes** (PI, Session 133, 2026-08-15): one sentence
  for the four inert factors; modality pulled out as the F1↔MCC
  trade; temperature pulled out; thinking level routed to R3.
- **✅ D8 SETTLED = A** (PI, Session 133, 2026-08-15): lead with the
  Flash 512 px board (the floor), bring in the Pro 384 px matrix for
  the temperature result with the genuine-Pro context named.
  **Drafting note (S133)**: the temperature sentence must carry its
  instrument/corpus/metric qualifiers ("single-pass, Pro 384 px, F1")
  — the E43/E72 lesson is that temperature claims do not generalise
  across metric or corpus (Obs 274; `e43-matched-temperature`).

### R3 — Consensus voting buys performance; the mechanism is pass diversity

- **Purpose**: the first large clean gain (single-pass → 0.69–0.77) and its
  mechanism (diversity, not pass count).
- **Claims**: diversity dividend — HIGH-thinking consensus ≫ minimal at
  matched N (`diversity-dividend-384`); engineered diversity adds nothing
  (H9 rejected); permissive thresholds win, unanimity hurts; the consensus-era
  "buy HIGH thinking" reading is revised by R5. Anchor: §R3.
- **✅ D9 SETTLED = forward-ref** (PI, Session 133, 2026-08-15): the
  retirement stays at R5 with a one-line signpost here — it needs the
  verifier machinery R4/R5 build, and co-locating would violate
  anti-double-telling.

### R4 — Proposer–verifier is the best architecture on every tile size

<!-- [E83] "the best" rests on the retracted sole-leader claim; under MCB it
is "among the 10 admissible of 82", with PV the point-estimate leader. -->

- **Purpose**: the key architectural move (H2) and the study's GS headline.
- **Claims**:
  - PV is the sole Tier-1 Era-1 leader; the verifier's lift breaks the
    consensus tie (`era1-leaderboard`). **Load-bearing.** <!-- [E83] RETRACTED
    as stated: MCB admits 10 of 82, including all six HIGH-consensus cells;
    the leader's own clique has 6 (D20). PV remains the point-estimate
    leader; "sole" and "breaks the tie" must go. -->
  - Cheap PV (minimal single-pass + verifier, 2 calls/tile) reaches the
    30-call HIGH tier, beating it on MCC (→ D3 callback).
  - Tile size × verifier (H11): architecture-dependent optimum; verifier
    *rescues* 256 px (0.460→0.856) (`tile-size-sweep`).
  - **GS headline**: F1@20 m 0.890 / MCC 0.790, global optimum confirmed
    (`unswept-pools-completeness`). **Load-bearing.**
- **✅ D10 SETTLED = folded** (PI, Session 133, 2026-08-15): tile size
  stays inside R4 — the optimum is architecture-dependent *because of*
  the verifier (the 256 px rescue), so it is a PV story.
- (Headline *placement* settled at D2; this remains its derivation home.)

### R5 — Verifier robustness: every cheaper option ties, so the cheap stack wins

- **Purpose**: stress-test the production verifier; establish the cost
  meta-rule and the recall-ceiling mechanism.
- **Claims** (currently six axes — determinism, temp/thinking, verifier
  consensus, compute allocation, verifier model, model upgrades): all tie;
  nothing dearer is better; meta-rule "on a within-noise tie, take the cheaper
  config" (Obs 357). Mechanism: the verifier shifts the binding constraint
  precision→pool recall (Obs 359). Anchor: §R5.
- **Scope-qualification (must appear here, not only at R7)**: the meta-rule
  holds only where the instrument can resolve the difference (Obs 362). One
  clause, forward-referencing R7 where it is priced.
- **✅ D11 SETTLED = compress** (PI, Session 133, 2026-08-15):
  meta-rule + summary table in the body; per-axis detail to the
  supplement (harmonises with the D6 rider). The Obs 362
  scope-qualification stays in the body regardless — one clause,
  forward-referencing R7.
- **✅ D12 SETTLED = elevate** (PI, Session 133, 2026-08-15): the
  recall-ceiling mechanism gets its own short subsection that R3, R4,
  and R6 point back to — the pipeline story's conceptual hub, and the
  single home that makes anti-double-telling enforceable. Placement:
  within R5, after the verifier machinery exists on the page.

### R6 — The cost frontier (gold standard)

- **Purpose**: price the pass ladder; show the efficient set — **as a GS
  result**.
- **Claims**: audited flex re-pricing collapses the frontier to four rungs;
  all seven rungs one F1 tier on GS (`pass-budget-pareto-v2`). Anchor: §R6
  front half. <!-- [E83] 6 of 7 admissible under MCB; verified-adv-text-4of5
  is ruled out as best. --> **Cost basis = audited (token-load audit); cite audited dollars
  only, Pareto v2 only.**
- **Per D4**: the transfer table, the reversal, and the buyable gap are **not**
  here — they are R7. R6 closes on the one-clause bridge into the seam.

---

## Seam — what carries forward, and what changes

> **New subsection (D1).** Short — half a page — but load-bearing. It is the
> honest hinge of the paper and the place the two-instrument framing is
> cashed out.

- **Purpose**: state precisely what changes between the two instruments, so
  every Part 2 number is read against the right baseline.
- **Content**:
  - **Corpus**: 4 maps / 487 tiles → 55 maps / 8,541 tiles; unseen at
    calibration time.
  - **Reference**: curator GT → reviewed student GT + adjudicated phantom
    supplement (and what that supplement is — per Obs 371, model detections
    human review confirmed as real student-missed mounds).
  - **Working buffer**: 20/30 m → 50 m, and *why* (the ring-censoring floor,
    Obs 371 — not an analyst preference).
  - **Resolving power**: the 487-tile GS cannot resolve ±0.03; the 8,541-tile
    deployment instrument can (Obs 362). This is why a GS tie is *bounded
    ignorance*, not equivalence — and it is the sentence that licenses the
    reversal in R7.
  - **What carried forward**: the config and the vote threshold selected on
    GS; what did *not* transfer (threshold, Obs 358).
- **Anti-double-telling**: this section *names* the changes; it does not
  re-derive the precisions (Methods/R1) or pre-empt the reversal (R7).

---

## Part 2 — Deployment (55 maps, 8,541 tiles)

### R7 — The deployment board (+ transfer, reversal, buyable gap, economics)

- **Purpose**: what a GS-calibrated config actually delivers on a large unseen
  corpus, the three deployment lessons, and what the frontier costs at scale.
- **Claims**:
  - Board: 8 cells, 5 tiers, 24/28 sig (`55map-canonical-leaderboard-50m`).
  - The min→HIGH reversal: GS tie reverses −0.030 on the instrument with power
    to resolve it (Obs 362); cost meta-rule scope-qualified. **Home of the
    reversal.**
  - Transfer table: every config degrades, unequally; HIGH-T0.7 transfers
    best. Buyable gap: +pass-count closes ~half (Obs 364).
  - **Deployment economics (per D4)**: what the Part 1 frontier costs at
    55-map scale; the cost–output trade at deployment resolution.
  - Lesson (i) threshold-transfer failure (Obs 358); (ii) thinking is a priced
    trade; (iii) F1/MCC trade → image is the **registered sole Tier-1 MCC
    cell** (`55map-canonical-leaderboard-mcc-50m`, signed 2026-07-27; → D3
    callback).
- **⚠ Carries two caveats from the 2026-07-27 sign-off** (both now in the
  board docs, `results/metric-leaderboards/55map-mcc-tiering.md` §"Reading
  this board"): the marginal-CI-vs-paired-test reading, and the attribution
  resolution. The IM-k3 provenance point belongs here too — the phantom pool
  was reviewed config-agnostically and the residual asymmetry favours *text*,
  so the image cell's MCC lead is conservative (Obs 371).
- **✅ D13 SETTLED = A + merged (b)/(c) oracle framing** (PI, Session
  133, 2026-08-15): carry-forward is the primary deployment claim;
  the relaxed/post-hoc rows are reported as **the measured deployment
  gap against the Tier-1 set**, without crowning a single "oracle"
  cell; table F1-ordered; **E56** cited wherever the relaxed rows
  appear (the verifier probability thresholds are in-sample).
  **Figures refreshed to the standardised reference** (S132 boards;
  `results/55maps-standardised-ref-2026-08-14/consolidated-standardised.csv`
  @ R=50 m): carry-forward TH7-k4 **0.8169**; Tier-1 pair {T03-k3
  0.8393, TH7-k3 0.8387}, indistinguishable (Δ +0.0006, p = 0.857);
  deployment gap **≈ +0.022** (was +0.032 canonical-vintage).
  **Decomposition punchline (S133)**: fixing only the vote threshold
  on the carried config (TH7 k4→k3) recovers +0.0218 of the +0.0224
  gap; post-hoc temperature selection at k3 buys +0.0006 — the gap is
  essentially pure threshold-transfer failure, which sharpens lesson
  (i) (Obs 358) and licenses retiring the single-cell "oracle" label
  (Obs 409 measured the collapse).
- **⚠ Structure moved on (PI ruling, 2026-09-08)**: § R7 is drafted as
  three blocks — R7.1 the calibrate-then-deploy result on the Gemini 3
  board, R7.2 the portfolio transfer and the 35-cell final board, R7.3
  the model-generation leg. The claims above are R7.1's; R7.2 and R7.3
  are inventoried in
  `docs/paper/results-claims-inventory-2026-09-12.md`.
- **Home of the D19 claim (2026-09-12)**: § R7.3 carries *models keep
  improving and the calibrated configuration carries across model
  versions, at least within the Gemini family* — the verifier-seat
  result and the 3.8 measured tie are its evidence, and the same recipe
  transferring across two model generations is what makes it a claim
  about method rather than about a vendor release. § R0 echoes it in one
  clause; nowhere else restates it.

### R8 — What the ground truth can and cannot support

- **Purpose**: bound every metric above by measuring the reference data's own
  error structure.
- **Claims**: precision review-verified; recall a measured upper bound
  (+2.4–2.7 %); double-miss correlation 1.5–1.7×; present a +3 %/+5 % band
  (Obs 361). Anchor: §R8. **Plus (new, Obs 371)**: the 55-map reference's two
  error structures and the R ≥ 50 m validity floor.
- **✅ D14 SETTLED = A** (PI, Session 133, 2026-08-16): Results, as
  results-of-validation — measured quantities R9 and the deployment
  claims consume; implications → Discussion. The GT-error
  measurement is also a contribution in its own right for the
  survey-archaeology audience.
- **✅ D14b SETTLED = A** (PI, Session 133, 2026-08-16): keep R8 whole
  at the head of the validity block, speaking to both instruments —
  the two GT stories are different in kind and read better
  contrasted; splitting would double-tell the shared framing.
  **PI framing note (2026-08-16)**: the bigger picture is that the GS
  set functioned as a *test set for configuration selection* which
  was then applied to the 55-map *production* set — exactly as a real
  research project would proceed — with the one difference that
  production here also has ground truth, so generalisation can be
  assessed. Not a contradiction of A; the framing to keep in mind
  when R8 (and the seam) are drafted.
  **Drafting note (S133)**: R8's description of the 55-map reference
  must reflect the ruling-21 *standardised* reference — the extension
  layer now carries exact marked-centre distances, so the "25 m
  interval-censored rings" characterisation is historical.

### R9 — Selecting a configuration without ground truth

- **Purpose**: complete the production story — deploy, rank GT-free, tie-break
  by cost — for corpora with no reference data.
- **Claims**: calibration-corpus power analysis (Obs 366 §2); the ~$733
  covering design ≈ $722 as-run (Obs 367); LOFO consensus ranks at ρ = +0.881,
  permissive-only, retrodiction caveat (Obs 368). Anchor: §R9,
  `gtfree-selection-findings.md`.
- **✅ D15 SETTLED = C** (PI, Session 133, 2026-08-16): split. R9
  (Results) reports the measured items as results-of-validation — the
  power analysis, the covering-design cost identity, and the LOFO
  retrodiction with the vote≥3 inversion and the retrodiction caveat
  prominent. The protocol-as-recipe, its decision-tree placement, and
  the prospective-test proposal go to Discussion (zero-draft already
  exists: Seeds 3 and 6). One pointing sentence each way; no
  double-telling. Mirrors the D14 results-of-validation logic.

---

## Preregistration handling (new, 2026-07-27)

> Raised in response to Shawn's question: this is his first fully
> preregistered paper, registered as an **OSF open-ended registration** with
> errata/amendments. Two decisions, both OPEN.

**The conventional three-way split** for a preregistered study:

- **Methods** — the registration itself (registry, DOI, date), what was
  registered, the amendment history, and the *rule* being applied for what
  counts as confirmatory.
- **Results** — a status marker on each result, plus a **hypothesis-outcome
  table** (hypothesis → prediction → verdict → where reported → status).
  Reviewers of preregistered work look for this table first.
- **Discussion** — what the deviations cost, and which exploratory findings
  most need independent replication.

An open-ended registration binds design and hypotheses but not a full analysis
plan. That is a weaker instrument than a Registered Report, and the correct
move is to say so plainly. The failure mode is not a loose registration — it
is claiming tighter binding than was actually in place.

**✅ D16 SETTLED = A** (PI, Session 133, 2026-08-16): Methods carries
a "Preregistration, amendments, and analysis status" subsection
(registration + errata summarised by class, not enumerated); Results
carries the hypothesis-outcome table at its head, immediately after
R0, plus per-subsection status markers; Discussion carries the
interpretation of deviations.
**PI rider (2026-08-16)**: plan Discussion space for a
**preregistration retrospective** — what worked and what didn't, on
the thesis that LLM support makes routine preregistration feasible
but may also invite over-planning/over-registration (the PI's read:
this project somewhat over-baked its prereg, requiring many
amendments). Zero-draft: `docs/paper/discussion-seeds.md` Seed 7
(S133 dialogue).

**✅ D17 SETTLED = A** (PI, Session 133, 2026-08-16): the
per-hypothesis reconciliation pass runs before Results prose is
drafted. **Schema sub-decision also settled: amend the schema** —
add `not-executed` and split "registered-as-exploratory" from
"post-hoc" — rather than carry a parallel hand-maintained table,
which would reintroduce the drift class the standardisation arc
eliminated; the hypothesis-outcome table generates from the manifest.
**Currency note (S133)**: A's cost has collapsed since this block was
drafted — the family BH-FDR has now been run as one family
(registration-before-compute, rejection set {H2, H3, H7}, PI-signed),
CMT-0106 executed (NULL, outcome-blind, PI-signed), E45 corrected
(permutation disclosed as unregistered; pair registered
bootstrap+BH with permutation wherever confirmatory claims appear),
E60 landed. **Remaining scope**: schema amendment; the relabelling
pass (preserve the argued `n1-baseline-matrix-384` exception);
analysis rows for H10 and H12-v2 (both ran, both null, both
invisible); erratum coverage check for the unexecuted set (H6, H13,
H14, H15, H2-C); generate the table. To run as its own
pre-run-reviewed block.

**The original decision text (for the record):**

A three-way discrepancy needs resolving before the Results claims are fixed:

| source | what it says |
|---|---|
| the preregistration | **H1–H8 confirmatory**, H9–H15 exploratory |
| `hypothesis-tracking.md` (last updated 2026-04-15) | H6, H10, H13 not started; H14, H15 deferred; H12 in progress |
| `results/analyses-manifest.json` | **all 18 analyses marked `exploratory`** — including every analysis whose `hypothesis_refs` point at H1–H8 |

The manifest schema permits `preregistered`, `exploratory`,
`preregistered-with-deviation` and `null`; only `exploratory` was ever used.
So the register currently asserts that fifteen hypotheses were preregistered
and none was tested confirmatorily — which contradicts the preregistration's
own H1–H8 classification.

- **A (REC)**: run a per-hypothesis reconciliation pass before drafting
  Results prose. For each of H1–H15: executed or not; if executed, is the
  analysis confirmatory, confirmatory-with-deviation (citing the errata
  entry), or exploratory; and where it is reported. Update the manifest field
  to match, then generate the hypothesis-outcome table from the manifest.
- **B**: present the whole study as exploratory-with-preregistered-design and
  make no confirmatory claims.
- *Lean A, with a caveat*: A is more work but it is the difference between a
  preregistered paper and a paper that mentions a preregistration. B is
  defensible and safe, but if any of H1–H8 *are* clean confirmatory tests, B
  discards the strongest claim available. **The reconciliation also determines
  whether Results needs a confirmatory-first ordering** — worth noting that
  H1–H8 map almost entirely onto R2–R4, so a confirmatory-first reading is
  nearly satisfied by the agreed spine already.
- **Also required either way**: the paper must account for
  registered-but-unexecuted hypotheses. Silence on these is the specific
  thing a reviewer checking the OSF record will catch. **Corrected
  2026-07-27** — an earlier revision of this line listed H10 as unexecuted on
  the authority of the stale tracking matrix; the D17 inventory establishes
  that **H10 and H12 both ran to completion** (see the reconciliation below).
  The genuinely unexecuted set is **H6, H13, H14, H15** (plus H2 Condition C).

### D17 inventory — findings (2026-07-27)

Four parallel read-only inventories reconciled the preregistration, the
tracking matrix and the manifest per hypothesis. Full detail in the four
inventory documents; the load-bearing conclusions:

**Executed and registered (candidates for `preregistered-with-deviation`)**:
H1, H2 (Condition B only), H3, H4, H5, H7, H8, H9, H10, H11, H12.

**Not executed**: **H6** (the registered Phase-4 transfer study — 13
`PLACEHOLDER` strings remain in `studies/phase4-transfer.yaml`; a *different*
Pro-vs-Flash experiment was labelled H6 post hoc, which **E41** already
declares "an exploratory extension rather than a strict implementation of
H6"); **H13** (only arm A ran, as the study's fixed 12.5 % tiling — no
overlap contrast exists); **H14** and **H15** (registered as deferred; no
non-Google model was ever called, and the four multi-model conditions split
models by *pipeline stage*, not within a voting pool); **H2 Condition C**
(fine-to-coarse — no `expand_*` configs exist; dropped without an erratum).

**The `exploratory` label has a traceable origin**:
`docs/methodology/preregistration/analysis-summary.md:82` says of H2
"Treated as exploratory due to preliminary evidence of no benefit",
contradicting `osf/preregistration.md:453` (`Confirmatory (architectural)`)
and `execution-plan.md:743` ("H2 and H6 remain confirmatory"). The label
appears to have propagated from a derived summary that was never corrected.
**Exception**: `n1-baseline-matrix-384`'s `exploratory` label was *argued*
(`docs/methodology/n1-baseline-matrix.md:405-411`) — do not overwrite it in a
bulk pass.

**⚠ Three systemic issues that outrank the relabelling**

1. **The registered inference method is not the method used.**
   `grep -c -i permutation` on `osf/preregistration.md` returns **0**; the
   registered inference is bootstrap CIs + Benjamini-Hochberg FDR at q = 0.05
   "across confirmatory hypotheses" (`:270`). The tile-swap micro-F1
   permutation used across *every* leaderboard is unregistered, and **E45**
   mis-describes it as "preregistered (Section 3.5)". Needs an erratum and a
   Methods statement; it does not invalidate anything (permutation is
   arguably the better test) but it cannot be presented as registered.
2. **The registered family-level BH-FDR across H1–H8 was deferred and appears
   never to have been run as one family.** Per-phase FDR exists in separate
   artefacts (`retest-production-summary.md:209`, `:278`). This constrains the
   wording of every "preregistered and significant" claim.
3. **Three completed preregistered factors are invisible.** `h8-v2`, `h10`
   and `h12-v2` ran to completion, are in the runs/conditions manifests, and
   are referenced by **zero** of the 18 analyses — and appear nowhere in
   `results-draft.md`. All three returned nulls. Authoring their analysis rows
   is a prerequisite to the manifest ever representing H8/H10/H12 correctly.

**Schema blocker**: `not-executed` is not a legal enum value
(`docs/manifest-schemas/analyses-manifest.schema.json:48`), and the enum
cannot distinguish "registered as exploratory" from "post-hoc". Either amend
the schema or carry a separate hypothesis-level table. **This is the first
decision to take**, because it determines the shape of everything else.

**Also newly surfaced**: the H7 escalation trigger fired (text T=1.3 0.5442 >
T=1.0 0.5335, `osf/preregistration.md:731`) and was not honoured — no
T=1.6/T=2.0 runs exist. **[Resolved next day — noted 2026-08-15]**:
erratum **E60** (2026-07-28) discloses the conditional, both
evaluations of its firing (never fired on the registered 60-tile
corpus; fired only on the unregistered expanded corpus, text track,
within noise), and the not-run disposition
(`docs/methodology/preregistration/protocol-errata.md` § E60). And **E56** rules H3's
swept-optimal reporting *preregistered* rather than in-sample, which is
favourable and should not be given away.

---

## Decision register (at a glance)

| Dn | section | the call | status |
|---|---|---|---|
| D1 | spine | architecture-ascending vs question-driven vs characterise-then-deploy | ✅ **A** — ascending, as two explicit parts + seam |
| D2 | spine | state headline early vs only at R4 | ✅ **A** — early, **both** headlines |
| D3 | spine | F1-vs-MCC theme: threaded vs own subsection vs distributed | ✅ **A** — threaded, home at R2 |
| D4 | R6/R7 | split GS-cost from deployment, or keep fused | ✅ **A** — split, both levels, told once |
| D5 | R0 | trim reading guide (convention → Methods) vs keep | ✅ **A** — trim (S133) |
| D6 | R1 | working precisions: Methods+recap vs all-Results | ✅ **A** — Methods+recap; supplement carries full sweeps (S133 rider) |
| D7 | R2 | factor split (inert group + pull out modality/temp; thinking → R3) | ✅ **yes** (S133) |
| D8 | R2 | Flash board lead + Pro matrix for temperature, vs one board | ✅ **A** — both boards; temperature sentence carries qualifiers (S133) |
| D9 | R3 | dividend-retirement: forward-ref vs co-locate | ✅ **forward-ref** (S133) |
| D10 | R4 | tile size folded into R4 vs own subsection | ✅ **folded** (S133) |
| D11 | R5 | compress six robustness axes to meta-rule + table | ✅ **compress** (S133) |
| D12 | R5 | elevate the recall-ceiling mechanism to its own hub subsection | ✅ **elevate** (S133) |
| D13 | R7 | carry-forward primary vs oracle-led | ✅ **A** + Tier-1-set gap framing, no single-oracle crown (S133) |
| D14 | R8 | Results (validation) vs Discussion | ✅ **A** — Results (S133) |
| D14b | R8 | GT epistemics whole vs split across the two parts | ✅ **A** — whole; test-set→production framing note (S133) |
| D15 | R9 | Results vs Discussion vs split | ✅ **C** — split; protocol → Discussion via Seeds 3/6 (S133) |
| D16 | prereg | where prereg material and the hypothesis-outcome table live | ✅ **A** + Discussion prereg-retrospective rider (S133) |
| D17 | prereg | confirmatory/exploratory reconciliation | ✅ **A** + schema amendment; reconciliation block queued (S133) |
| D18 | spine | one reference revision across Results, or per-section currency | ✅ **r2 throughout**; older-reference figures → supplement (PI ruling 1, 2026-09-12) |
| D19 | spine | headline the Gemini 3 calibrated result or the Gemini 3.7 stack | ✅ **the 3.7 stack** (GS 0.9265 screen / 0.9190 board-frame Tier 1; deployment r2 0.8827 carried / 0.8871 oracle); Gemini 3 is the calibration story; **supersedes D2's two numbers, not its placement** (PI ruling 2) |
| D20 | spine | word budget: compress prose, or move information into tables | ✅ **into tables**, referenced not restated; coverage over polish, the paper being re-drafted from the outline (PI ruling 3) |
| D21 | R1b | GS stride/geometry: new block, fold into R4, or supplement-only | ✅ **its own block, § R1b**, between R1 and R2 (PI ruling 5) |
| D22 | all | exhibits: prose-first or figure/table-first | ✅ **figure/table-first** wherever it carries the claim better (PI ruling 6) |

**Settled**: ALL — D1–D4 (Session 118), D5–D17 (Session 133),
D18–D22 (Session 153).
**Gate before final Results prose**: the D17 reconciliation block
(schema amendment → relabelling → H10/H12-v2 rows → unexecuted-set
erratum check → generate the hypothesis-outcome table).
**Gate status (S134, 2026-08-17)**: ✅ COMPLETE — vocabulary v2
landed (final register: 32 rows — 3 confirmatory-with-deviation, 5
registered-exploratory, 18 post-hoc, 6 not-executed incl. the § 8.9
named-programme row), errata E74–E78 + the E59 update filed and
PI-approved, the table generating at
`results/hypothesis-outcome-table/` (15/15, verifier-confirmed), and
**the PI walk closed same-day**
(`reports/s134-relabel-walk-dossier.md` § 8). **Prose drafting is
OPEN.** Three gated future items queued from the unexecuted-set
adjudication (H6 $0 analyses; H13 re-pricing → arms B+C; H2-C
pricing run) — each needs its own phase-gate before execution.

---

## Figures and tables

> **New section, per D22 (PI ruling 6, 2026-09-12).** One row per Results
> block: what the block's claims are best carried by, and the existing
> artefact that could serve or "to be made". **No figure was made in this
> pass** and no prose was cut — this is the plan, not its execution.

**A correction to the inventory's premise.** The claims inventory
concluded that "no paper figure has been made", on the evidence that
`docs/paper/figures/` holds only `review-app-examples/`. That is true of
`docs/paper/figures/`, but **`results/` carries about a hundred committed
figures**, several of them directly serving the ISPRS skeleton's three
exhibits. The most consequential finds, none of them referenced anywhere
in the draft:

- `results/verifier-robustness/pareto/pareto_v2.png` (and
  `pareto_leaderboard.png`) — the cost/F1 frontier, i.e. **exhibit (ii)**,
  generated by `scripts/build_pareto_v2.py:167`.
- `results/55map-final-board-r2-2026-09-06/significance-groups.png` — the
  35-cell dot-and-interval plot with significance groups, i.e.
  **exhibit (iii)**, generated by `scripts/final_board_build.py:520`.
- `results/gs-fp-classification/figures/cross_corpus_comparison.png` and
  `category_distribution.png` — the error-mode comparison.
- `results/double-miss-crops-2026-09-06/contact-sheet.png` — the
  double-miss cases § R8 counts, as images.
- `results/student-gt-fn-rate-analysis/figures/fn_rate_by_stratum.png`
  and `.../-gs4/figures/fn_rate_by_sheet.png` — the reference's own
  omission structure.

So the gap is **selection and adaptation**, not creation from nothing.

| block | best carried by | existing artefact, or to be made |
|---|---|---|
| **R0** reading guide | **table** — the two instruments side by side (corpus, tiles, reference, buffer, resolving power), plus the hypothesis-outcome table | hypothesis-outcome table exists and is generated: `results/hypothesis-outcome-table/hypothesis-outcome-table.md`. The two-instrument table is **to be made** — it is small, and it also discharges much of the D1 seam. |
| **R1** working precisions | **prose**, two or three lines (D6 sent the derivation to Methods); the full 14-buffer sweeps go to the supplement per the D6 rider | tables exist at `results/working-precision/gs-plateau-characterisation.md`; a buffer-curve figure is **to be made for the supplement**, not the body |
| **R1b** tile geometry | **one figure + one table.** Figure: F1 against cost across the geometry cells, which carries R1b-05 through R1b-17 at once — the aggregation inversion, the verifier reversal, the interior optimum, and the ~19× efficiency point. Table: the nine-cell stride board | both **to be made**, but from committed numbers at $0: the board table is `results/stride-2026-08-25/findings.md:28-40` and the ladder `:152-157`; the grid boards are `results/grid-2026-08-18/findings.md:135-141,336-343` |
| **R2** single-pass | **table**, and a small one — D7 settled one sentence for the four inert factors, so the board belongs in the supplement with only the floor and the tie size in the body | `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.md` is the full board (supplement); the body table is **to be made** (3–4 rows) |
| **R3** consensus | **figure** — the vote-threshold × N surface is the natural carrier of "diversity, not pass count" | inter-pass agreement figures exist (`results/inter-pass-agreement/figures/`, e.g. `phase3a_retest__replication-high.png`) but measure agreement, not the dividend; the dividend figure is **to be made**. *Held pending the K-ladder job, which governs R3.* |
| **R4** proposer–verifier | **table** — the Era-2 verified board, top rows only | exists: `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/README.md` rank table, 79 rows; the body needs the top ~8 plus the best Gemini 3 cells. Compression is **to be made**; the source is generated |
| **R5** verifier robustness | **table** — exactly the D11 summary table the block still does not have: one row per axis (determinism, temperature × thinking, verifier consensus, compute allocation, verifier model, model upgrades) with the delta, the p-value, and the cost | **to be made**; every cell exists in `results/verifier-robustness/verifier-robustness-findings.md` and the four register rows. This is the highest-value missing table in Results: it discharges D11 and saves ~300 words |
| **R6** cost frontier (GS) | **figure** — the Pareto frontier; the seven-rung table then reduces to the supplement | **exists and is unused**: `results/verifier-robustness/pareto/pareto_v2.png`. *Held pending the K-ladder job, which governs R6.* |
| **Seam** | **prose**, half a page; it is the one place a paragraph beats a table, because what changes between instruments is a set of *reasons* | shares the R0 two-instrument table rather than adding its own |
| **R7.1** Gemini 3 board | **table**, compressed to five rows per the inventory's recommendation — six of its eight rows reappear in R7.2's table | source exists: `results/55map-leaderboard/55map-leaderboard-50m-r2.md`; the MCC re-tiering that carries lesson (iii) is `results/metric-leaderboards/55map-mcc-tiering-r2.md` |
| **R7.2** portfolio transfer + final board | **figure + table.** Figure: the significance-groups plot, which is the paper's obvious single deployment exhibit. Table: the ten-row family table already rendered by script | **figure exists**: `results/55map-final-board-r2-2026-09-06/significance-groups.png` (publication quality, referenced nowhere). Table is generated by `scripts/render_r7_family_table.py` from `final_board_50m.json` |
| **R7.3** model-generation leg | **table** — the 2 × 2 grid (proposer × verifier) with each cell's carried and oracle F1, which carries the verifier-seat finding in four cells and replaces ~200 words | **to be made**; a 2 × 2 is the smallest possible exhibit for the block's headline finding. The cost reconciliation goes to the supplement per the inventory's ruling-3 recommendation |
| **R8** ground-truth error structure | **table** — the opposing biases with their directions, magnitudes, and bases (recall inflation, double-miss correlation, residual duplicates, net), which also makes the `[REF: r1]` provenance visible per D18 | **to be made** (4 rows). Optional supporting figure exists: `results/double-miss-crops-2026-09-06/contact-sheet.png`, and the omission structure at `results/student-gt-fn-rate-analysis*/figures/` |
| **R9** GT-free selection | **figure** — pseudo-rank against true rank for the eight cells, which shows ρ = +0.881 and the vote ≥ 3 inversion on one pair of axes | **to be made**; the numbers are in `results/gtfree-selection/gtfree-selection-findings.md`. The four-step protocol stays prose and goes to Discussion per D15 |

**Count**: 3 figures and 1 table already exist and are unused
(`pareto_v2.png`, `significance-groups.png`, the hypothesis-outcome
table, and — for the supplement — the phase-3d PR curves); 4 figures and
7 tables are to be made, all from committed numbers at **$0 compute**.

**Priority order, if the budget for making exhibits is finite**:

1. **R5's D11 summary table** — settled, missing, and saves the most words.
2. **R7.2's significance-groups figure** — exists; Results currently has
   no figure at all.
3. **R6's Pareto figure** — exists; it is exhibit (ii).
4. **R1b's F1-against-cost figure** — carries the most claims per square
   inch of any proposed exhibit.
5. **R0's two-instrument table** — small, and doubles as the seam's spine.
6. **R7.3's 2 × 2** and **R8's bias table** — each replaces ~200 words.
