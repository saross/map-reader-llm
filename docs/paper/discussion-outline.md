# Discussion — structural outline (ALL DECISIONS SETTLED)

> **Addendum 2026-09-03**: D.9's lit-scout gate is discharged by the
> AB+ corpus; the recipe reframes to endorsement-with-citation and the
> automation cell is staked (PI ruling). See the D.9 bullet "Gate
> DISCHARGED". No DD decision reopened. Later the same day (S148) the
> D.9 concept skeleton was written from the corpus:
> `docs/paper/d9-drafting-brief-2026-09-03.md` (three length envelopes
> pending D-5; naming inputs updated; seven rulings listed).
>
> **Status**: collaborative structure document, per the outline-first
> contract (claude-obs 56: the contract re-arms at every major section
> boundary — an existing seed file does not count as agreement). Built
> from `docs/paper/discussion-seeds.md` Seeds 1–11 plus the Discussion
> duties routed here by settled Results-outline rulings (D14 rider,
> D15, D16 + rider). This is a decision-forward outline, **not**
> prose. **ALL THIRTEEN DECISIONS DD1–DD13 SETTLED** (DD1–DD10 at the
> Session 139 walk; DD11–DD13 at the same session's foregrounding
> amendment — PI, 2026-08-21). **Prose scheduling (PI, S139)**:
> Discussion prose waits until the earlier sections of the paper are
> written — outline and seeds only until then. Two lit gates
> additionally stand: **D.1** (detection-baseline lit pass, launched
> S139) and **D.9** (Seed 7 `/lit-scout` micro-registration novelty
> check).

## Revision history

| rev | date | change |
|---|---|---|
| v0 | 2026-08-17 | Strawman; 10 decisions DD1–DD10 raised, all OPEN (Session 135). |
| v1 | 2026-08-21 | DD1–DD10 ALL SETTLED at the Session 139 walk (PI): nine as recommended; DD8a inventory extended with two PI additions (cross-model-family tests; benchmark/eval development), parked doors OUT. Detection-baseline lit pass ruled WANTED as a D.4 gate. |
| v2 | 2026-08-21 | **Foregrounding amendment** (PI, same session): five headline outcomes must lead the Discussion. Seeds 8–11 drafted; spine reorganised to a two-part core (Part I what-the-study-shows, Part II lessons-for-survey-practice); old D.4 dissolved into new D.1; sections renumbered D.0–D.11. DD11–DD13 raised and settled; student-GT lineage to the 2023 campaign confirmed by the PI. |

*Brief by design — consult `git log docs/paper/discussion-outline.md`
for full history.*

## How to read this

- **Part A** holds the spine-level calls, the cross-cutting decisions,
  and the standing conventions the Discussion inherits from the
  Results outline.
- **Part B** walks the proposed sections at subsection/move
  granularity: each carries its *purpose*, its *load-bearing moves*
  (with seed and evidence anchors), and any *in-section decisions*.
  Sections are numbered D.0–D.11 since the v2 amendment; "(was D.x)"
  annotations preserve traceability to v0/v1 rulings.
- **Decision register** at the bottom lists every `DDn` in one place.
  Numbering: sections are `D.0–D.11` (Discussion), decisions are
  `DDn` — mirroring the Methods pattern (sections `M.x`, decisions
  `MDn`) and avoiding collision with the Results decisions `Dn`.

---

## Part A — spine & cross-cutting decisions

### ✅ DD1 — the overall spine — SETTLED (A, lessons-led hybrid; amended by DD11)

What order does the Discussion take?

- **A (RULED)**: **hybrid, lessons-led** — a compact findings-in-context
  opening (D.0), then the thematic subsections that are the paper's
  exportable contributions, then the conventional apparatus
  (limitations, preregistration retrospective, future work,
  conclusion). The thematic sections lead because they are what the
  paper is *for*; the conventional moves follow because reviewers
  expect to find them.
- **B**: conventional order throughout — summary → relation to prior
  work → implications → limitations → future work.
- **C**: lessons-only — minimal conventional apparatus, limitations
  and literature distributed into the thematic subsections.

**✅ SETTLED = A** (PI, Session 139, 2026-08-21). The seeds are
already organised as lessons; B buries them and C would read as
evasive to a reviewer looking for a limitations section. **Amended
by DD11 (same session)**: the thematic core is now two-part — Part I
(what the study shows, Seeds 8–10) precedes Part II (lessons for
survey practice, Seeds 1+6, 2+3, 4+5, 11). The lessons-led principle
is preserved; the ordering within the core is DD11's.

### ✅ DD2 — seed clustering — SETTLED (A, three thematic homes; extended by DD11–DD13)

Seven seeds, how many homes?

- **A (RULED)**: **three thematic homes**: Seeds 1 + 6 (both are
  the calibration-transfer argument — representativeness before
  size is *why* the plateau rule works); Seeds 2 + 3 (both are
  the production protocol — deploy-and-evaluate economics, then
  GT-free selection as its no-reference branch); Seeds 4 + 5
  (both are tile-MCC — the cross-instrument replication and the
  workflow it serves). Seed 7 stands alone at the retrospective.
- **B**: one subsection per seed — more faithful to the
  drafting record, but Seeds 1/6 and 4/5 would double-tell their
  shared mechanisms.

**✅ SETTLED = A** (PI, Session 139, 2026-08-21). The merges follow
the argument structure, and anti-double-telling forces them anyway.
**Extended (same session)**: Seeds 8–11 each take their own home
(DD12: Seeds 8 and 10 stay separate; DD13: Seed 11 gets its own
subsection closing Part II).

### ✅ DD3 — claims scope: how far do the lessons generalise? — SETTLED (A, case-scoped)

The seeds oscillate between two registers: survey-archaeology
practice (mound detection on historical maps) and general
methodology (calibrate-small, deploy-large AI-assisted detection).
One ruling governs verb strength throughout the section.

- **A (RULED)**: **scope claims to the demonstrated case** — VLM
  feature detection on historical maps, addressed to survey
  archaeology and map-corpus digitisation — and present the
  methodological lessons (plateau rule, deploy-and-evaluate, GT-free
  selection, metric-by-workflow) as *candidates* for the broader
  class of calibrate-small/deploy-large detection pipelines, hedged
  in one clause each. Matches Seed 3's own discipline ("claim
  exactly that much and no more").
- **B**: claim the methodology lessons at general
  calibrate-small/deploy-large scope, with this study as the
  evidence case.

**✅ SETTLED = A** (PI, Session 139, 2026-08-21). One corpus, one
symbol type, one model family; the falsifiable-proposal framing
already committed the production protocol to modesty, and a mixed
register would read as inconsistent. This ruling governs verb
strength in every subsection below — including Seed 8's
bitter-lesson claim, which is drafted under exactly this discipline
(the demonstrated case, with the HTR parallel making the wider
interpretation plausible rather than demonstrated).

### ✅ DD11 — the foregrounding amendment: two-part core — SETTLED (split)

Raised by the PI at S139: the v1 outline under-foregrounded the
paper's five headline outcomes — (a) map-symbol extraction is
getting the bitter lesson; (b) results comparable to good
traditional CV/ML (lit-pass-gated); (c) the characteristics of
high-performance extraction runs; (d) costs and expertise lower
than traditional CV/ML, accessible to domain experts working with
LLMs; (e) comparison and interoperability with participatory
GIS/crowdsourcing. Seeds 8–11 drafted to carry them.

- **A**: two-part core, all four new subsections in Part I.
- **B (RULED — the split)**: **Part I = what the study shows**
  (D.1 bitter lesson + parity, Seed 8; D.2 high-performing runs,
  Seed 9; D.3 cost & expertise, Seed 10); **Part II = lessons for
  survey practice** (D.4 calibration, D.5 production protocol,
  D.6 metric-by-workflow, **D.7 crowdsourcing interop, Seed 11,
  closing the part**). Seed 10 stays with the bitter-lesson arc it
  completes; Seed 11 extends metric-by-workflow's triage into the
  participatory frame. D.0 names all five outcomes up front, so
  foregrounding survives the split.
- **C**: both Seeds 10 and 11 in Part II.

**✅ SETTLED = the split** (PI, Session 139, 2026-08-21). Old D.4
("relation to prior approaches") **dissolves into new D.1** — the
head-to-head positioning it was scoped to do *is* Seed 8's parity
leg; DD5's distributed rule is unchanged.

### ✅ DD12 — Seeds 8 and 10: one subsection or two? — SETTLED (separate)

**✅ SETTLED = keep separate** (PI, Session 139, 2026-08-21): the
bitter-lesson/parity argument gets full room for the head-to-head
positioning it absorbs from old D.4 (with the lit-pass evidence),
and cost/expertise gets full room for the 2024-paper foil
(Sobotkova et al. 2024, *Journal of Documentation*,
10.1108/JD-05-2022-0096). Each of the five headline outcomes keeps
a nameable home; Seed 8 bridges to Seed 10 in one clause.

### ✅ DD13 — Seed 11's home — SETTLED (own subsection, closes Part II)

**✅ SETTLED = own subsection** (PI, Session 139, 2026-08-21): the
crowdsourcing material carries a distinct literature (participatory
GIS; Sobotkova et al. 2023, *Applied Geography*,
10.1016/j.apgeog.2023.102967) and a distinct argument (comparison +
interoperability + mutual QA). **Lineage confirmed by the PI (same
session): the 55-map student-digitised reference layer descends
from the 2023 campaign's dataset** — the mutual-QA framing
sharpens: each method independently estimates the other's error
rate on the same corpus.

### Standing conventions inherited (no ruling needed)

- **Anti-double-telling** (Results outline, Part A) applies with full
  force: the Discussion **never re-derives a number**. Every measured
  quantity keeps its Results home; Discussion carries one-clause
  callbacks with section references, and adds only interpretation,
  implication, and recommendation. The callback ledger below makes
  this enforceable.
- **Registration-status discipline**: every Discussion claim inherits
  its class from the vocabulary-v2 register (32 rows; gate-status
  note at `docs/paper/results-outline.md`, decision register;
  rulings in `reports/s134-relabel-walk-dossier.md` § 8). Post-hoc
  results are interpreted as hypothesis-generating, not
  confirmatory; when drafting each claim, check its analysis row
  rather than assuming. The hypothesis-outcome table
  (`results/hypothesis-outcome-table/`) is the authoritative
  projection.
- **Currency rule for gated items**: H13 arms B + C and the H2-C
  pricing run are API-gated and *may* run before submission. If they
  run, their results land in Results and the corresponding
  future-work lines in D.10 drop out. Draft D.10 with those lines
  marked conditional.

### The callback ledger (Results homes the Discussion consumes)

| item | Results home | what Discussion adds (home) |
|---|---|---|
| power arithmetic: ~10–20 representative sheets per axis | R9 (Obs 366 § 2) | representativeness-before-size inversion (D.4) |
| min→HIGH reversal −0.030; ±0.03 resolving power | R7 / seam (Obs 362) | bounded-ignorance reading of GS ties (D.4) |
| threshold decomposition: k4→k3 recovers +0.0218 of +0.0224; temperature +0.0006, p = 0.857 | R7 (D13 figures) | the plateau rule + decision tree (D.4) |
| ~$733 covering design ≈ $722 as-run | R9 (Obs 367) | the deploy-and-evaluate recommendation (D.5); the cost/accessibility argument (D.3) |
| LOFO ρ = +0.881; vote≥3 inversion; retrodiction caveat | R9 (Obs 368) | falsifiable-proposal framing + prospective test (D.5) |
| IM-k3 sole Tier-1 MCC at deployment; MCC/F1 divergence | R7 lesson iii (D3 thread home R2) | metric-by-workflow argument (D.6) |
| GT error bounds: recall +2.4–2.7 %; +3 %/+5 % band | R8 (Obs 361) | implications for reported metrics (D.8, per the D14 rider); the mutual-QA leg (D.7) |
| T = 1.0/N = 5 vs T = 0.7/N = 10 cost equivalence | R6/R7 economics (e43 findings § 13) | budget-constrained configuration advice (D.6) |
| headline pair: GS F1@20 m 0.890; deployment corrected-F1@50 m 0.815 | R4 / R7 derivation homes | third appearance in D.0 (DD4); the parity leg of D.1 |
| text vs image ordering (pilot 0.796 vs 0.711; deployment text oracle) | R-home to pin at prose time (results-draft R1–R7) | the surprising-modality move (D.2) |
| HIGH-thinking diversity dividend (consensus ≈ 0.77 vs ≈ 0.69, Era-1) | R-home to pin at prose time | which-diversity-works move (D.2) |
| PV pilot gains +0.086 to +0.138; verifier robustness | R-home to pin at prose time | architecture move (D.2) |

*The three "pin at prose time" rows are new with v2; their Results
homes exist in `docs/paper/results-draft.md` but the precise R-section
references must be verified when D.2 drafts, not assumed here.*

---

## Part B — proposed sections

### D.0 — Findings in context (opening move)

- **Purpose**: re-orient the reader in two short paragraphs — what
  the study set out to test, what it found, and **the five headline
  outcomes about to be argued** (bitter lesson; parity with bespoke
  CV/ML; the high-performance recipe; cost/expertise accessibility;
  crowdsourcing interoperability) followed by the practice lessons.
  No derivations; callbacks only.
- **✅ In-section decision — DD4 SETTLED = A** (PI, Session 139,
  2026-08-21): yes — the two headline numbers (GS F1@20 m 0.890;
  deployment corrected-F1@50 m 0.815) may appear here a third time
  (R0 stub, derivation homes, now D.0). A Discussion opening that
  names its headline numbers is conventional, and the two-instrument
  pairing *is* the paper's central honesty device; one sentence, both
  numbers, instruments attached. (Rejected B: callback-only with no
  numerals.)

### Part I — what the study shows

### D.1 — The bitter lesson arrives at map-symbol extraction (Seed 8; absorbs old D.4)

- **Purpose**: the paper's headline interpretive frame — a
  generalist VLM with no fine-tuning or bespoke architecture
  matches the specialist route on this task — plus the head-to-head
  positioning duty inherited from old D.4.
- **Load-bearing moves** (Seed 8):
  1. **The frame**: Sutton's bitter lesson; Humphries' HTR result
     as the adjacent-domain precedent (generalist Gemini 3 vs
     fine-tuned Transkribus; anchors in the seed).
  2. **This study as the map-symbol instance**: the headline pair
     (D.0 callback), no task-specific training.
  3. **The parity leg — GATED on the detection-baselines lit pass**
     (launched S139): where do good CNN/segmentation and
     remote-sensing mound-detection pipelines land, and in what
     protocol sense are the numbers comparable? Positioning
     (CNN/segmentation map extraction, RS mound detection,
     VLM-based detection) lives here per DD11. *S140 rider (Seed 8):
     present the area→point difficulty gradient as an explicit
     ladder (target-class area cluster 0.84–0.91 with O'Hara at the
     corrected 0.908; Goldman's same-protocol grain isolation), plus
     the GMFS novelty qualifiers and the O'Hara 98.2/90.8
     metric-hygiene sentence.*
  4. **The honesty moves**: engineering moved up a level (workflow,
     not training — bridge to D.3); DD3's case-scoped verb
     discipline; the trajectory rider (generalist capability
     improves with each model generation at no workflow cost).
- **In-section decisions**: none open — DD5 (distributed
  literature + short positioning) and DD12 (separate from Seed 10)
  govern; both settled.

### D.2 — What a high-performing extraction run looks like (Seed 9)

- **Purpose**: assemble the configuration profile of the study's
  best runs as a headline outcome, with mechanisms and one-clause
  Results callbacks.
- **Load-bearing moves** (Seed 9): (1) text specification beats
  few-shot image examples — the surprising one, with the E48
  boundary (mechanism only partially characterised); (2) which
  diversity works (temperature and reasoning budget feeding
  consensus pools; structural decomposition) and which does not
  (parametric variants, ensemble verifiers); (3) consensus voting
  converts diversity into precision, with the vote threshold as the
  deployment-re-tuned dial (pointer to D.4's plateau rule); (4) the
  proposer–verifier architecture as the largest structural gain,
  with the deliberately minimal production verifier. Boundary: the
  recall ceiling is perceptual (Experiment E).
- **In-section decisions**: none — registration-status discipline
  (Part A) applies to each claim individually at prose time.

### D.3 — Cost and expertise: the generalist route is accessible (Seed 10)

- **Purpose**: convert the accessibility finding into the paper's
  answer to the team's own 2024 cautionary paper.
- **Load-bearing moves** (Seed 10): (1) the foil — Sobotkova et al.
  2024 on the time/effort/expertise ML demands; (2) the existence
  proof — domain expert + LLM agents, ≈ $722 deployment campaign,
  no CS team, no training infrastructure; (3) the
  expertise-profile shift (domain knowledge + research methods +
  LLM direction, not ML engineering); (4) boundaries — effort did
  not vanish, and the code layer exists but no longer requires a
  software team (bridge back to D.1's engineering-moved-up-a-level
  move).
- **In-section decisions**: none.

### Part II — lessons for survey practice

### D.4 (was D.1) — What a small calibration instrument can and cannot decide (Seeds 1 + 6)

- **Purpose**: the paper's central methodological lesson, stated as a
  transferable rule with its mechanism.
- **Load-bearing moves** (order within the subsection):
  1. **The plateau rule** (Seed 6): nothing the calibration corpus
     concluded *with significance* was overturned at deployment; its
     ties and plateaus were the entire risk surface. Both deployment
     surprises are instances (threshold plateau → +0.022; min-vs-HIGH
     tie → −0.030).
  2. **Why — representativeness before size** (Seed 1): the power
     arithmetic says the corpus was too small, but two calibration
     failures were not power failures — a larger sample of the same
     unrepresentative sheets would have converged confidently on the
     wrong answer. Inverts the reference-data investment instinct:
     buy sampling before annotation.
  3. **The mechanism of the one real transfer failure** (Seed 6): the
     F1-optimal vote threshold is a property of the
     pipeline–corpus encounter (marginal-mound prevalence), not of
     the configuration — which is why it is also the cheapest dial
     to re-tune.
  4. **The decision tree** (Seed 6, four steps: carry significant
     calls / treat ties as unresolved with cheaper-or-more-permissive
     tie-breakers / budget the cheap deployment re-tune / GT-free
     branch where no reference exists → points forward to D.5).
  5. **The caution**: relative choices transfer, absolute performance
     does not (transfer table, R7 callback).
- **✅ In-section decision — DD9 SETTLED = A** (PI, Session 139,
  2026-08-21): a displayed box/figure — the four-step tree is the
  single most screenshot-able practitioner artefact in the paper;
  branch 4 carries the pointer to D.5's protocol so the two recipes
  read as one system. (Rejected B: prose only.)

### D.5 (was D.2) — The production protocol: deploy-and-evaluate, then select without ground truth (Seeds 2 + 3)

- **Purpose**: convert the economics and the GT-free result into the
  paper's practice recommendation, at exactly the claim strength the
  evidence supports.
- **Load-bearing moves**:
  1. **The economics reframe** (Seed 2): calibration buys the
     short-list, not the decision — the tie-set *is* the calibration
     product; the resolution campaign is a line item (~$733) because
     thresholds are free post hoc and pass-counts nest; the study is
     its own existence proof ($722 as-run ≈ the covering design).
  2. **The GT-free branch** (Seed 3): the four-step protocol
     completes the production story; claim it as a **falsifiable
     proposal with a pre-specified test** (apply preregistered to
     the next discovery corpus), not a validated method. The two
     characterised failure modes (permissive-consensus requirement;
     family-diversity requirement) stay prominent.
  3. **The seam with Results**: R9 reports the measured items
     (per D15); this subsection carries recipe, framing, and the
     prospective-test proposal only.
- **In-section decisions**: none beyond DD3's verb-strength ruling —
  Seed 3's framing was PI-shaped and reads as settled.

### D.6 (was D.3) — Metric choice is a workflow decision (Seeds 4 + 5)

- **Purpose**: the strongest evidence-backed advice the paper can
  give a survey project: which pipeline is "best" depends on whether
  the survey consumes coordinates or tiles.
- **Load-bearing moves**:
  1. **The cross-instrument replication** (Seed 4): image + verifier
     tops tile-MCC on all three instruments while sitting mid-board
     on F1; mechanism legible (tile-MCC is localisation-free; image's
     weakness is localisation, not detection; verification controls
     its false-positive tiles). Deployment leg carries permutation
     backing (IM-k3 sole Tier-1 on MCC).
  2. **The workflow mapping** (Seed 5): fully-automated extraction
     optimises object-F1; semi-automated triage ("show me the tiles,
     I'll pinpoint") optimises tile-MCC — and a cheap
     two-call-per-tile stack is the best triage instrument in the
     study.
  3. **Budget-constrained configuration** (Seed 5): the
     temperature-vs-pool-size cost equivalences belong in the advice
     (T = 1.0/N = 5 vs T = 0.7/N = 10; the 5.5× dead heat), so
     practitioners see the trade, not just the per-configuration
     frontier.
  4. **Registration-status note**: the MCC counter-board analyses are
     post-hoc class — frame as replicated-across-instruments
     exploratory finding plus recommendation, not as a confirmatory
     claim (standing convention above).
  5. **Forward pointer**: the triage workflow hands into D.7's
     participatory frame; the app follow-on lives in D.10, one
     clause here.

### D.7 — Crowdsourcing and participatory mapping: comparison, interoperability, mutual QA (Seed 11; closes Part II)

- **Purpose**: place the pipeline against and alongside the team's
  demonstrated crowdsourcing route (Sobotkova et al. 2023), closing
  the practice part with the human–AI division of labour.
- **Load-bearing moves** (Seed 11): (1) the comparison — both routes
  priced from the team's own record (241 person-hours vs ≈ $722
  API), with error profiles that differ in kind; (2)
  interoperability demonstrated in-study — the deployment reference
  descends from the 2023 campaign's dataset (**lineage
  PI-confirmed, S139**), so crowdsourced data validated the VLM at
  scale while the pipeline's error apparatus (R8 callback)
  quantified residual incompleteness in the crowdsourced layer in
  return: each method independently estimates the other's error
  rate on the same corpus; (3) the hybrid workflow —
  triage-plus-pinpointing as a participatory task specification
  (extends D.6 move 2; app instrument in D.10). Boundary: no
  prospective hybrid deployment ran — retrospective economics and
  workflow analysis only.
- **In-section decisions**: none — DD13 settled the home.

### Apparatus

### D.8 (was D.5) — Limitations

- **Purpose**: the dedicated limitations inventory — restricted to
  limitations *without* a thematic home, so the section adds rather
  than repeats.
- **✅ DD6 SETTLED = A** (PI, Session 139, 2026-08-21) — inventory
  and placement:
  - **A (RULED)**: dedicated subsection with a strict one-home rule.
    Proposed inventory: single map series / region / symbol type;
    single model family (with the H14/H15 disclosed-not-run tie-in);
    GT error structure implications for every reported metric (the
    D14 rider routes implications here; R8 keeps the measurements);
    verifier probability thresholds in-sample at the relaxed rows
    (E56); single-symbol generalisation unknown. Items that already
    live inside thematic subsections (GS representativeness → D.4;
    retrodiction-only GT-free validation → D.5) get **no**
    restatement here — at most a pointer clause.
  - **B**: fully distributed limitations, no dedicated subsection
    (risks reading as evasive; see DD1).

### D.9 (was D.6) — Preregistration in practice: deviations and the retrospective (Seed 7)

- **Purpose**: discharge the D16 Discussion duty (interpretation of
  deviations) and the D16 rider (the retrospective): what
  registration cost, what it bought, and the grain-not-volume
  diagnosis with the waterfall → agile arc.
- **Load-bearing moves** (from Seed 7, already PI-articulated): the
  over-bake with receipts; the two counterweights (amendment count
  is a biased measure — unregistered drift is invisible; the
  registration delivered its goods: {H2, H3, H7} family-FDR, the
  falsified H2 direction *more* credible for being registered,
  CMT-0106 outcome-blind); grain-not-volume; the LLM-support claim
  cutting both ways; micro-registration as the resolution evidenced
  from the project's own record.
- **✅ DD7 SETTLED = A** (PI, Session 139, 2026-08-21): one
  subsection — deviations-interpretation flows into the
  retrospective; they are one argument (what the deviations *mean*
  is the retrospective), and splitting invites double-telling the
  errata story. (Rejected B: a short formal "deviations and their
  cost" subsection plus a separate essayistic retrospective.)
- **Gates**: prose here waits on the `/lit-scout`
  micro-registration check (launched S139 — does incremental /
  living / just-in-time registration already have a name in the
  meta-science literature?). If prior art exists, the recipe
  reframes from proposal to endorsement-with-citation and the
  novelty clause drops.
- **✅ Gate DISCHARGED by the AB+ corpus (S147, 2026-09-02; PI
  ruling 2026-09-03)** — 30 preregistration sources verified at
  `outputs/ab-plus/` (tail report
  `reports/ab-plus-tail-report-2026-09-02.md` § "What the corpus now
  attests"). Two findings reshape the subsection:
  1. **The staged/adaptive cell is occupied; the recipe becomes
     endorsement-with-citation.** "Adaptive preregistration" occurs in
     Srivastava 2018 only as a lowercase common noun, never defined;
     "registered flexibility" nowhere. Antecedents to cite: Nosek 2018
     (four data-dependent strategies incl. "sequential
     preregistration"), Crüwell 2021 §6.2 (a registration "for each
     of the models"), Ioannidis 2022 ("small bites" offered alongside,
     not instead of, registering the space of approaches), Willroth
     2022 (analysis-level registration forced by circumstance),
     Gerasimova 2024 (a living document whose criteria may move with
     disclosure), Gould 2026 and Vaccaro 2026 (the two occupants of the
     staged cell). The novelty clause on the RECIPE drops.
  2. **The AUTOMATION cell is empty — stake it (PI, 2026-09-03).**
     Across all 30 sources nothing implements or evaluates an LLM that
     authors or checks a registration. Nearest: Pu 2019's
     "declaration of match … could even be partially or fully
     automated" (proposal, unbuilt); Thomas 2026 §6 (autonomous
     AI-scientist systems should commit before the confirmatory model
     exists — proposal). Thomas 2026 also cites Goldberg 2024 (an LLM
     checklist assistant) and dismisses checklists as self-report —
     **that is the objection the LLM-support claim must answer**, and
     the concession to make first: our registration was written
     against Gemini models that already existed, the commitment Thomas
     et al. argue is unprotected. Territory to stake in Methods
     (§ M.12: how the LLM assisted authoring, checking, and the errata
     machinery — described as unreported practice, with the
     over-specification pitfall named) and here in D.9 (the claim,
     scoped to implemented-and-evaluated, with the Thomas objection
     answered). A follow-up methods paper is planned:
     `planning/llm-assisted-preregistration-methods-paper.md`.
  3. **Measured base rates now available for the counterweights**:
     Ofosu 2023 (deviation noted in 1 of 14; median 25 % of registered
     hypotheses omitted; iterative PAPs "tricky to implement" without
     a neutral gatekeeper — the objection to just-in-time
     re-registration); Sarafoglou 2023 (self-report vs coders ICC .43,
     coded data gave the STRONGER condition effect); Willroth 2024
     (register schema: type, reason, timing — ours lacks reason and
     timing; "once results are known, preregistrations should not be
     updated").
- **Concept skeleton written (S148, 2026-09-03)**:
  `docs/paper/d9-drafting-brief-2026-09-03.md` — seven moves at
  mechanism/instance/boundary with page anchors; three length envelopes
  pending D-5 (the venue skeleton routes Seed 7 OUT); naming inputs
  updated (Srivastava's common-noun usage settles occupancy; Gould's
  grain is a continuum; "just-in-time" collides with Ross 2022's
  pejorative); seven rulings needed before prose.

### D.10 (was D.7) — Future work

- **Purpose**: a short, disciplined list — each item one or two
  sentences with its motivating anchor.
- **✅ DD8 SETTLED** (PI, Session 139, 2026-08-21): the inventory as
  proposed, **extended with two PI additions** (items 4–5 below);
  parked doors **EXCLUDED** (item 7). In priority order:
  1. **The prospective GT-free test** (Seed 3's pre-specified test —
     the headline future item; arguably a closing move rather than a
     list entry).
  2. **Tile-triage + human pinpointing follow-on** (Seed 5; the
     planned pinpoint-correction app as instrument).
  3. **Multi-model voting pools** (H14/H15 disclosed-not-run — the
     registered strand future work honestly inherits).
  4. **Cross-model-family tests** (PI addition, S139 walk): whether
     the configuration lessons (plateau rule, verifier architecture,
     metric-by-workflow) transfer beyond the single Gemini family —
     pairs with the single-model-family limitation in D.8 and with
     item 3, but is replication across families rather than voting
     across them.
  5. **A proper benchmark or eval** (PI addition, S139 walk):
     formalise the task (tiles, reference data, metrics, splits) as
     a shared benchmark so future models and pipelines can be
     evaluated comparably.
  6. **Conditional entries**: H13 overlap arms B + C and the H2-C
     1024 px condition — drop from D.10 if the gated runs execute
     pre-submission (currency rule, Part A).
  7. **Parked doors — EXCLUDED** (ruled): the vector-extension
     project (displacement bearings vs colour-classified attractors)
     and the higher-T MCC upper bound (T > 1.3) stay in the project
     notes (S133 block plan); the paper stays tight.

### D.11 (was D.8) — Conclusion

- **✅ DD10 SETTLED = A** (PI, Session 139, 2026-08-21): separate
  and short (three paragraphs maximum): the two-instrument result
  pair, the headline lessons in a sentence each, the
  prospective-test invitation as the closing move. Most archaeology
  and digital-humanities venues expect one, and it protects the
  Discussion's ending from doing double duty. (Rejected B: closing
  paragraph only — can still be re-cut at submission formatting if
  the venue demands it.)

---

## Decision register (at a glance)

DD1–DD10 settled at the Session 139 walk; DD11–DD13 at the same
session's foregrounding amendment (PI, 2026-08-21).

| DDn | scope | the call | status |
|---|---|---|---|
| DD1 | spine | lessons-led hybrid vs conventional order vs lessons-only | ✅ SETTLED = A (hybrid, lessons-led); amended by DD11 |
| DD2 | spine | seed clustering: three thematic homes vs seven | ✅ SETTLED = A (three: 1+6, 2+3, 4+5); extended by DD11–DD13 |
| DD3 | spine | claims scope: demonstrated case + hedged candidates vs general | ✅ SETTLED = A (case-scoped) |
| DD4 | D.0 | headline numbers third appearance vs callback-only | ✅ SETTLED = A (yes, once, both numbers) |
| DD5 | D.1 (was D.4) | literature: distributed + short positioning vs concentrated vs deferred to Intro | ✅ SETTLED = A (distributed + positioning, now living in D.1); Intro dependency stands |
| DD6 | D.8 | limitations: dedicated one-home subsection vs distributed | ✅ SETTLED = A (dedicated) |
| DD7 | D.9 | deviations + retrospective: one subsection vs two | ✅ SETTLED = A (one) |
| DD8 | D.10 | future-work inventory (incl. parked doors in/out) | ✅ SETTLED = as listed + 2 PI additions (cross-family tests; benchmark/eval); parked doors OUT |
| DD9 | D.4 | decision tree as displayed box/figure vs prose | ✅ SETTLED = A (displayed) |
| DD10 | D.11 | separate Conclusion vs closing paragraph | ✅ SETTLED = A (separate, short) |
| DD11 | spine | foregrounding amendment: two-part core; homes for Seeds 10/11 | ✅ SETTLED = split (S10 in Part I; S11 closes Part II); old D.4 dissolved into D.1 |
| DD12 | D.1/D.3 | Seeds 8 + 10: merge vs separate | ✅ SETTLED = separate |
| DD13 | D.7 | Seed 11: own subsection vs folded into D.6 | ✅ SETTLED = own subsection; student-GT lineage to the 2023 campaign PI-confirmed |

**Gates independent of these rulings**: Seed 7 `/lit-scout`
(micro-registration novelty) — **COMPLETE AND VERIFIED S139**
(31/31 rows pass; verdict ADJACENT BUT DISTINCT — Gould et al. 2026
"adaptive preregistration" is near prior art, the LLM-support
element is the clean novelty;
`docs/methodology/research/lit-scout-micro-registration-2026-08-21.md`);
**what remains before D.9 prose is the PI naming/reframe ruling —
DEFERRED to prose time (PI, S139)**, to follow a full read of Gould
et al. and discussion; the decision inputs are banked at
`reports/d9-naming-decision-brief-2026-08-21.md`. The
detection-baseline lit pass is also **COMPLETE AND VERIFIED S139**
(185/185 claims pass;
`docs/methodology/research/lit-scout-detection-baselines-2026-08-21.md`)
— D.1's gate is discharged, with the report's own to-do noted (full-
text metric extraction for the nine [not retrieved] comparators and
the Tier-1 reads before D.1 prose reaches a reviewer).
`academic-prose` loads before any Seeds→prose conversion. **Prose
scheduling (PI, S139)**: all Discussion prose waits until the
earlier sections of the paper are written.
