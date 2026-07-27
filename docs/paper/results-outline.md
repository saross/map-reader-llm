# Results — structural outline (spine AGREED; section calls still open)

> **Status**: collaborative structure document. Part A's spine calls (D1–D4)
> are **settled**; D5–D15 remain **OPEN** with recommendations marked `(REC)`;
> D16–D17 are **new and open** (preregistration handling). This is a
> decision-forward outline, **not** prose. Prose drafting for a section waits
> until that section's structure is agreed. `docs/paper/results-draft.md`
> remains the **zero-draft** reference (claims and anchors live there) and is
> not extended until the relevant structure lands.

## Revision history

| rev | date | change |
|---|---|---|
| v0 | 2026-06-14 | Strawman; 15 decisions D1–D15 raised, all OPEN (Session 114). |
| v1 | 2026-07-27 | **D1–D4 settled** (Session 118). Spine reorganised into two explicit parts with a named seam; anti-double-telling convention added as a standing rule; D16–D17 raised on preregistration handling; decision register updated. |

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
  R0 reading guide → R1 precisions → R2 single-pass → R3 consensus →
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

---

## Part 1 — Characterisation (gold standard: 4 maps, 487 tiles)

### R0 — Reading guide: instruments, metrics, conventions

- **Purpose**: orient the reader to the two instruments and the one
  statistical machinery, so each later result can be read correctly.
- **Claims**: two-instrument framing; headline metric = buffered F1 at an
  empirical working precision + tile-MCC; tile-swap permutation + BH-FDR +
  greedy-clique tiering throughout. Anchor: §R0 of the zero-draft.
- **Now also carries** the two-headline stub (per D2) and a pointer to the
  preregistration status statement (per D16).
- **▸ D5**: keep R0 as a Results subsection, or fold the stats-convention
  detail into Methods and leave only a 2–3 line orientation here?
  **(REC: trim — orientation stays, convention detail → Methods)** to avoid
  duplicating Methods.

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
- **▸ D6 — Results or Methods?** Deriving the buffer is data-driven but reads
  as methodology.
  - **A (REC)**: Methods (the derivation) + a one-line Results recap of the
    chosen radii.
  - **B**: keep wholly in Results (current).
  - *Lean A*: it's a calibration decision; Results should consume it, not
    derive it. But it's a genuine empirical result, so the call is real.

### R2 — Single-pass baselines: a floor, and which factors moved it

- **Purpose**: establish the ~0.63 single-pass floor and report what the
  preregistered single-factor sweep did and did not separate.
- **Claims**:
  - Floor: 36 single-pass cells → 4 tiers, a broad 20-cell Tier-1 tie
    (F1 0.583–0.631); the GS set cannot separate the stronger configs
    (`era1-single-pass-baseline-matrix`). **Load-bearing.**
  - Modality: no clean F1 win, but drives the F1↔MCC trade (text→F1,
    image→MCC). **This is the home of the D3 thread.**
  - Temperature: T=0.0 > T=0.7, a clean Tier-1/Tier-2 split
    (`n1-baseline-matrix-384`, Pro).
  - Inert: prompt elaboration (H1), ordering (H4), negative-text (H5),
    example-library (H8) — all inside the tie.
  - Signpost: thinking level is inert-to-harmful at single pass; its effect
    arrives under consensus (→ R3).
- **▸ D7 — the factor split.** Group the four inert factors in one sentence;
  pull out modality (as a trade) and temperature (T=0 best); route thinking
  level forward to R3. **(REC: yes — this version.)**
- **▸ D8 — board basis.** The floor lives on the Flash 512 px board; the
  temperature signal lives on the Pro 384 px matrix.
  - **A (REC)**: lead with the Flash board (the floor), bring in the Pro
    matrix for the temperature result and the genuine-Pro context.
  - **B**: one board only (drop the temperature claim or relocate it).
  - *Lean A*: temperature is a real single-pass signal worth keeping; it just
    needs its correct (Pro) home named.

### R3 — Consensus voting buys performance; the mechanism is pass diversity

- **Purpose**: the first large clean gain (single-pass → 0.69–0.77) and its
  mechanism (diversity, not pass count).
- **Claims**: diversity dividend — HIGH-thinking consensus ≫ minimal at
  matched N (`diversity-dividend-384`); engineered diversity adds nothing
  (H9 rejected); permissive thresholds win, unanimity hurts; the consensus-era
  "buy HIGH thinking" reading is revised by R5. Anchor: §R3.
- **▸ D9 — the dividend's "retirement" under PV** is asserted here but only
  demonstrated at R5. Keep the forward-reference, or move the retirement next
  to the dividend? **(REC: keep forward-ref + a one-line signpost)** — the
  retirement needs the verifier machinery R4/R5 build.

### R4 — Proposer–verifier is the best architecture on every tile size

- **Purpose**: the key architectural move (H2) and the study's GS headline.
- **Claims**:
  - PV is the sole Tier-1 Era-1 leader; the verifier's lift breaks the
    consensus tie (`era1-leaderboard`). **Load-bearing.**
  - Cheap PV (minimal single-pass + verifier, 2 calls/tile) reaches the
    30-call HIGH tier, beating it on MCC (→ D3 callback).
  - Tile size × verifier (H11): architecture-dependent optimum; verifier
    *rescues* 256 px (0.460→0.856) (`tile-size-sweep`).
  - **GS headline**: F1@20 m 0.890 / MCC 0.790, global optimum confirmed
    (`unswept-pools-completeness`). **Load-bearing.**
- **▸ D10 — tile size (H11)**: keep folded into R4 (it's a PV story), or give
  it its own subsection? **(REC: keep folded.)**
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
- **▸ D11 — compress the six axes** into the meta-rule + a summary table
  (per-axis detail → supplement)? **(REC: yes — meta-rule + table;** the six
  bullets are dense and individually minor.)
- **▸ D12 — elevate the recall-ceiling mechanism.** It explains R3 (why
  diversity helps), R4 (why the verifier wins) *and* R6 (why minimal ties HIGH
  on GS). Keep it as R5's closing paragraph, or pull it into its own short
  mechanism subsection the others point back to? **(REC: elevate)** — it is
  the conceptual hub of the pipeline story, and elevating it is what makes the
  anti-double-telling rule enforceable for this mechanism.

### R6 — The cost frontier (gold standard)

- **Purpose**: price the pass ladder; show the efficient set — **as a GS
  result**.
- **Claims**: audited flex re-pricing collapses the frontier to four rungs;
  all seven rungs one F1 tier on GS (`pass-budget-pareto-v2`). Anchor: §R6
  front half. **Cost basis = audited (token-load audit); cite audited dollars
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
- **▸ D13 — carry-forward vs oracle ordering** (original decision).
  - **A (REC)**: carry-forward (0.8152) is the primary deployment claim;
    oracle + relaxed rows = the measured deployment gap (+0.032 upper bound);
    table F1-ordered.
  - **B**: oracle-led (0.8476 as best-achievable; carry-forward as a
    sensitivity row).
  - *Lean A*: preregistration honesty — the oracle is post-hoc threshold
    selection; lead with what the protocol committed to. **Note (2026-07-27)**:
    errata **E56** already declares the verifier probability-threshold
    operating points to be in-sample rather than calibrated, which
    independently supports A and should be cited where the oracle is reported.

### R8 — What the ground truth can and cannot support

- **Purpose**: bound every metric above by measuring the reference data's own
  error structure.
- **Claims**: precision review-verified; recall a measured upper bound
  (+2.4–2.7 %); double-miss correlation 1.5–1.7×; present a +3 %/+5 % band
  (Obs 361). Anchor: §R8. **Plus (new, Obs 371)**: the 55-map reference's two
  error structures and the R ≥ 50 m validity floor.
- **▸ D14 — Results or Discussion** (original decision).
  - **A (REC)**: Results as results-of-validation (measured quantities R9 and
    the deployment claims depend on); implications → Discussion.
  - **B**: move the whole subsection to Discussion as a validity passage.
  - *Lean A*: it reports measurements, not interpretation.
- **▸ D14b — placement under the two-part structure (new, 2026-07-27).** R8
  now covers *both* references (GS curator GT and the 55-map canonical GT), so
  it straddles the seam.
  - **A (REC)**: keep it whole here, at the head of the validity block, and
    let it speak to both instruments — the GS and 55-map GT stories are
    genuinely different in kind and read better contrasted than separated.
  - **B**: split — GS GT epistemics into Part 1, 55-map GT epistemics into
    Part 2.
  - *Lean A*: splitting would double-tell the shared framing (what a reference
    standard can support) for a modest gain in instrument purity.

### R9 — Selecting a configuration without ground truth

- **Purpose**: complete the production story — deploy, rank GT-free, tie-break
  by cost — for corpora with no reference data.
- **Claims**: calibration-corpus power analysis (Obs 366 §2); the ~$733
  covering design ≈ $722 as-run (Obs 367); LOFO consensus ranks at ρ = +0.881,
  permissive-only, retrodiction caveat (Obs 368). Anchor: §R9,
  `gtfree-selection-findings.md`.
- **▸ D15 — Results or Discussion?** It carries a measured result (ρ = +0.881)
  but is framed as a falsifiable *proposal*.
  - **A**: Results (it has a result).
  - **B**: Discussion (it's a proposed method / future-facing).
  - **C (REC?)**: split — the validation result stays in Results, the protocol
    + prospective-test framing go to Discussion.
  - *Genuinely undecided* — still the call I'd most want your read on. Note
    that the two-part structure makes C slightly more attractive: R9's
    validation result is a Part 2 deployment finding, while the protocol is a
    forward-facing proposal that sits naturally in Discussion.

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

**▸ D16 — where the preregistration material lives, and where the
hypothesis-outcome table goes.**

- **A (REC)**: Methods carries a "Preregistration, amendments, and analysis
  status" subsection (registration + the E1–E57 errata summarised by class,
  not enumerated); Results carries the hypothesis-outcome table plus a
  per-subsection status marker; Discussion carries the interpretation of
  deviations. Table lives at the head of Results, immediately after R0.
- **B**: table in Methods, Results carries markers only.
- **C**: table in a supplement, summarised in Results.
- *Lean A*: the table is a Results object — it is the map from what was
  promised to what was found. In Methods it reads as bookkeeping; in a
  supplement it stops doing the work it exists to do.

**▸ D17 — the confirmatory/exploratory reconciliation (BLOCKING for final
Results prose).**

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
T=1.6/T=2.0 runs exist and no erratum covers it. And **E56** rules H3's
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
| D5 | R0 | trim reading guide (convention → Methods) vs keep | OPEN — *lean A* trim |
| D6 | R1 | working precisions: Methods+recap vs all-Results | OPEN — *lean A* Methods+recap |
| D7 | R2 | factor split (inert group + pull out modality/temp; thinking → R3) | OPEN — *lean A* yes |
| D8 | R2 | Flash board lead + Pro matrix for temperature, vs one board | OPEN — *lean A* both |
| D9 | R3 | dividend-retirement: forward-ref vs co-locate | OPEN — *lean A* forward-ref |
| D10 | R4 | tile size folded into R4 vs own subsection | OPEN — *lean A* folded |
| D11 | R5 | compress six robustness axes to meta-rule + table | OPEN — *lean A* compress |
| D12 | R5 | elevate the recall-ceiling mechanism to its own hub subsection | OPEN — *lean A* elevate |
| D13 | R7 | carry-forward primary vs oracle-led | OPEN — *lean A* carry-forward (E56 supports) |
| D14 | R8 | Results (validation) vs Discussion | OPEN — *lean A* Results |
| D14b | R8 | GT epistemics whole vs split across the two parts | OPEN — *lean A* keep whole |
| D15 | R9 | Results vs Discussion vs split | OPEN — *lean C?* split — least sure |
| D16 | prereg | where prereg material and the hypothesis-outcome table live | OPEN — *lean A* |
| D17 | prereg | confirmatory/exploratory reconciliation | OPEN — *lean A* — **blocking** |

**Settled**: D1–D4 (spine). **Next most valuable**: D17 (blocking for final
Results claims), then D15 (least settled), D6 (straddle removal), D13 (has new
support from E56). D5, D7–D12, D14/D14b are clear-lean quick waves.
