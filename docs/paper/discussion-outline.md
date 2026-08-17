# Discussion — structural outline (strawman; ALL DECISIONS OPEN)

> **Status**: collaborative structure document, per the outline-first
> contract (claude-obs 56: the contract re-arms at every major section
> boundary — an existing seed file does not count as agreement). Built
> from `docs/paper/discussion-seeds.md` Seeds 1–7 plus the Discussion
> duties routed here by settled Results-outline rulings (D14 rider,
> D15, D16 + rider). This is a decision-forward outline, **not**
> prose. Seeds→prose for a subsection waits until that subsection's
> structure is agreed; **Seed 7 additionally waits on its `/lit-scout`
> check** (micro-registration novelty claim) regardless of rulings
> here.

## Revision history

| rev | date | change |
|---|---|---|
| v0 | 2026-08-17 | Strawman; 10 decisions DD1–DD10 raised, all OPEN (Session 135). |

*Brief by design — consult `git log docs/paper/discussion-outline.md`
for full history.*

## How to read this

- **Part A** holds the spine-level calls, the cross-cutting decisions,
  and the standing conventions the Discussion inherits from the
  Results outline.
- **Part B** walks the proposed sections at subsection/move
  granularity: each carries its *purpose*, its *load-bearing moves*
  (with seed and evidence anchors), and any *in-section decisions*.
- **Decision register** at the bottom lists every `DDn` in one place.
  Numbering: sections are `D.0–D.8` (Discussion), decisions are
  `DDn` — mirroring the Methods pattern (sections `M.x`, decisions
  `MDn`) and avoiding collision with the Results decisions `Dn`.

---

## Part A — spine & cross-cutting decisions

### DD1 — the overall spine — OPEN

What order does the Discussion take?

- **A (REC)**: **hybrid, lessons-led** — a compact findings-in-context
  opening (D.0), then the three thematic lesson subsections that are
  the paper's exportable contributions (D.1–D.3), then the
  conventional apparatus (prior approaches D.4, limitations D.5,
  preregistration retrospective D.6, future work D.7, conclusion
  D.8). The thematic sections lead because they are what the paper
  is *for*; the conventional moves follow because reviewers expect
  to find them.
- **B**: conventional order throughout — summary → relation to prior
  work → implications → limitations → future work.
- **C**: lessons-only — minimal conventional apparatus, limitations
  and literature distributed into the thematic subsections.

*Lean A. The seeds are already organised as lessons; B buries them
and C will read as evasive to a reviewer looking for a limitations
section.*

### DD2 — seed clustering — OPEN

Seven seeds, how many homes?

- **A (REC)**: **three thematic homes**: D.1 = Seeds 1 + 6 (both are
  the calibration-transfer argument — representativeness before
  size is *why* the plateau rule works); D.2 = Seeds 2 + 3 (both are
  the production protocol — deploy-and-evaluate economics, then
  GT-free selection as its no-reference branch); D.3 = Seeds 4 + 5
  (both are tile-MCC — the cross-instrument replication and the
  workflow it serves). Seed 7 stands alone at D.6.
- **B**: one subsection per seed (seven homes) — more faithful to the
  drafting record, but Seeds 1/6 and 4/5 would double-tell their
  shared mechanisms.

*Lean A. The merges follow the argument structure, and
anti-double-telling forces them anyway.*

### DD3 — claims scope: how far do the lessons generalise? — OPEN

The seeds oscillate between two registers: survey-archaeology
practice (mound detection on historical maps) and general
methodology (calibrate-small, deploy-large AI-assisted detection).
One ruling governs verb strength throughout the section.

- **A (REC)**: **scope claims to the demonstrated case** — VLM
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

*Lean A. One corpus, one symbol type, one model family; the
falsifiable-proposal framing already committed D.2 to modesty, and a
mixed register (modest in D.2, expansive elsewhere) would read as
inconsistent.*

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
  future-work lines in D.7 drop out. Draft D.7 with those lines
  marked conditional.

### The callback ledger (Results homes the Discussion consumes)

| item | Results home | what Discussion adds (home) |
|---|---|---|
| power arithmetic: ~10–20 representative sheets per axis | R9 (Obs 366 § 2) | representativeness-before-size inversion (D.1) |
| min→HIGH reversal −0.030; ±0.03 resolving power | R7 / seam (Obs 362) | bounded-ignorance reading of GS ties (D.1) |
| threshold decomposition: k4→k3 recovers +0.0218 of +0.0224; temperature +0.0006, p = 0.857 | R7 (D13 figures) | the plateau rule + decision tree (D.1) |
| ~$733 covering design ≈ $722 as-run | R9 (Obs 367) | the deploy-and-evaluate recommendation (D.2) |
| LOFO ρ = +0.881; vote≥3 inversion; retrodiction caveat | R9 (Obs 368) | falsifiable-proposal framing + prospective test (D.2) |
| IM-k3 sole Tier-1 MCC at deployment; MCC/F1 divergence | R7 lesson iii (D3 thread home R2) | metric-by-workflow argument (D.3) |
| GT error bounds: recall +2.4–2.7 %; +3 %/+5 % band | R8 (Obs 361) | implications for reported metrics (D.5, per the D14 rider) |
| T = 1.0/N = 5 vs T = 0.7/N = 10 cost equivalence | R6/R7 economics (e43 findings § 13) | budget-constrained configuration advice (D.3) |

---

## Part B — proposed sections

### D.0 — Findings in context (opening move)

- **Purpose**: re-orient the reader in two short paragraphs — what
  the study set out to test, what it found, and the shape of the
  three lessons about to be argued. No derivations; callbacks only.
- **In-section decision — DD4 (OPEN)**: may the two headline numbers
  (GS F1@20 m 0.890; deployment corrected-F1@50 m 0.815) appear here
  a third time (R0 stub, derivation homes, now D.0)?
  - **A (REC)**: yes — a Discussion opening that names its headline
    numbers is conventional, and the two-instrument pairing *is* the
    paper's central honesty device; one sentence, both numbers,
    instruments attached.
  - **B**: callback-only — "the headline results (§§ R4, R7)" with no
    numerals, maximal anti-double-telling.

### D.1 — What a small calibration instrument can and cannot decide (Seeds 1 + 6)

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
     branch where no reference exists → points forward to D.2).
  5. **The caution**: relative choices transfer, absolute performance
     does not (transfer table, R7 callback).
- **In-section decision — DD9 (OPEN)**: presentation of the decision
  tree.
  - **A (REC)**: a displayed box/figure — the four-step tree is the
    single most screenshot-able practitioner artefact in the paper;
    branch 4 carries the pointer to D.2's protocol so the two
    recipes read as one system.
  - **B**: prose only.

### D.2 — The production protocol: deploy-and-evaluate, then select without ground truth (Seeds 2 + 3)

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

### D.3 — Metric choice is a workflow decision (Seeds 4 + 5)

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
  5. **Future-work pointer**: the tile-triage-plus-pinpointing
     follow-on (Seed 5's app-repurposing idea) lives in D.7, one
     clause here.

### D.4 — Relation to prior approaches

- **Purpose**: position the results against the mound-detection and
  historical-map feature-extraction literature; give the reader the
  comparison they will otherwise construct badly themselves.
- **DD5 (OPEN) — where literature engagement lives** (dependency: no
  Introduction outline exists yet, so the Intro/Discussion split of
  literature duty cannot be fully settled here):
  - **A (REC)**: **distributed + one short positioning subsection**
    — each thematic subsection (D.1–D.3) engages the specific
    literature its lesson speaks to, in one or two sentences; D.4
    stays short and does only the head-to-head positioning
    (CNN/segmentation approaches to map symbol extraction,
    remote-sensing mound detection, VLM-based detection); the
    survey/motivation literature is Introduction duty, ruled when
    the Introduction outline is walked.
  - **B**: concentrate all literature engagement in D.4.
  - **C**: defer everything to the Introduction; Discussion carries
    contrast sentences only.
- **Gate**: Seed 7's `/lit-scout` check is scoped to
  micro-registration novelty; a **second, separate lit pass** on
  detection baselines (what F1/MCC do comparable pipelines report?)
  may be wanted before D.4 drafts. Flagged as a question for the
  walk, not assumed.

### D.5 — Limitations

- **Purpose**: the dedicated limitations inventory — restricted to
  limitations *without* a thematic home, so the section adds rather
  than repeats.
- **DD6 (OPEN) — inventory and placement**:
  - **A (REC)**: dedicated subsection with a strict one-home rule.
    Proposed inventory: single map series / region / symbol type;
    single model family (with the H14/H15 disclosed-not-run tie-in);
    GT error structure implications for every reported metric (the
    D14 rider routes implications here; R8 keeps the measurements);
    verifier probability thresholds in-sample at the relaxed rows
    (E56); single-symbol generalisation unknown. Items that already
    live inside thematic subsections (GS representativeness → D.1;
    retrodiction-only GT-free validation → D.2) get **no**
    restatement here — at most a pointer clause.
  - **B**: fully distributed limitations, no dedicated subsection
    (risks reading as evasive; see DD1).

### D.6 — Preregistration in practice: deviations and the retrospective (Seed 7)

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
- **DD7 (OPEN) — one subsection or two?**
  - **A (REC)**: one — deviations-interpretation flows into the
    retrospective; they are one argument (what the deviations *mean*
    is the retrospective), and splitting invites double-telling the
    errata story.
  - **B**: two — a short formal "deviations and their cost"
    subsection (reviewer-facing), then the retrospective as its own
    essayistic subsection.
- **Gates**: prose here waits on (i) this walk AND (ii) the
  `/lit-scout` micro-registration check (does incremental / living /
  just-in-time registration already have a name in the meta-science
  literature?). If prior art exists, the recipe reframes from
  proposal to endorsement-with-citation and the novelty clause
  drops.

### D.7 — Future work

- **Purpose**: a short, disciplined list — each item one or two
  sentences with its motivating anchor.
- **DD8 (OPEN) — the inventory**. Proposed, in priority order:
  1. **The prospective GT-free test** (Seed 3's pre-specified test —
     the headline future item; arguably a closing move rather than a
     list entry).
  2. **Tile-triage + human pinpointing follow-on** (Seed 5; the
     planned pinpoint-correction app as instrument).
  3. **Multi-model voting pools** (H14/H15 disclosed-not-run — the
     registered strand future work honestly inherits).
  4. **Conditional entries**: H13 overlap arms B + C and the H2-C
     1024 px condition — drop from D.7 if the gated runs execute
     pre-submission (currency rule, Part A).
  5. **Parked doors — include or exclude?** The vector-extension
     project (displacement bearings vs colour-classified attractors)
     and the higher-T MCC upper bound (T > 1.3) are parked in the
     S133 block plan. *Lean exclude* (paper stays tight; the parked
     doors are project-notes material), but this is the PI's call —
     hence part of DD8 rather than assumed.
- Ruling wanted on: the inventory as listed, and specifically
  item 5.

### D.8 — Conclusion

- **DD10 (OPEN)**: separate short Conclusion section after the
  Discussion, or a closing paragraph inside it?
  - **A (REC)**: separate and short (three paragraphs maximum): the
    two-instrument result pair, the three lessons in three
    sentences, the prospective-test invitation as the closing move.
    Most archaeology and digital-humanities venues expect one, and
    it protects the Discussion's ending from doing double duty.
  - **B**: closing paragraph only, no separate section
    (venue-dependent; can be re-cut at submission formatting).

---

## Decision register (at a glance)

| DDn | scope | the call | status |
|---|---|---|---|
| DD1 | spine | lessons-led hybrid vs conventional order vs lessons-only | ⏳ OPEN — lean A (hybrid) |
| DD2 | spine | seed clustering: three thematic homes vs seven | ⏳ OPEN — lean A (three: 1+6, 2+3, 4+5) |
| DD3 | spine | claims scope: demonstrated case + hedged candidates vs general | ⏳ OPEN — lean A (case-scoped) |
| DD4 | D.0 | headline numbers third appearance vs callback-only | ⏳ OPEN — lean A (yes, once) |
| DD5 | D.4 | literature: distributed + short positioning vs concentrated vs deferred to Intro | ⏳ OPEN — lean A (distributed + positioning); Intro dependency flagged |
| DD6 | D.5 | limitations: dedicated one-home subsection vs distributed | ⏳ OPEN — lean A (dedicated) |
| DD7 | D.6 | deviations + retrospective: one subsection vs two | ⏳ OPEN — lean A (one) |
| DD8 | D.7 | future-work inventory (incl. parked doors in/out) | ⏳ OPEN — lean as listed, parked doors OUT |
| DD9 | D.1 | decision tree as displayed box/figure vs prose | ⏳ OPEN — lean A (displayed) |
| DD10 | D.8 | separate Conclusion vs closing paragraph | ⏳ OPEN — lean A (separate, short) |

**Gates independent of these rulings**: Seed 7 `/lit-scout`
(micro-registration novelty) before D.6 prose; the possible
detection-baseline lit pass before D.4 prose (raised at DD5, needs a
yes/no in the walk); `academic-prose` loads before any Seeds→prose
conversion.
