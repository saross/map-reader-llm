# D.9 drafting brief: the preregistration retrospective, read from the AB+ corpus

> **Last revised**: 2026-09-03 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Status**: a pre-prose deliverable. It converts the D.9 outline
(`docs/paper/discussion-outline.md` § D.9, DD7 settled as one
subsection) into a concept skeleton at target density, with every
specific anchored to a verified Annotated Bibliography Plus (AB+) entry
under `outputs/ab-plus/` or to the project record. It is not prose.
Three gates still stand before prose is written:

1. **Prose scheduling** (Principal Investigator (PI), Session 139): all
   Discussion prose waits until the earlier sections are written.
2. **The naming/reframe ruling** (PI, Session 139, deferred to prose
   time pending a full read of Gould et al. 2026). The Gould read now
   exists as a verified entry (`gould_but_2026.md`, pilot batch) and the
   term-occupancy question it left open is settled by
   `srivastava_sound_2018.md` (tail batch). § 4 below re-scores the
   options on that evidence and adds one new consideration.
3. **The home ruling (D-5)**. The venue skeleton
   (`docs/paper/manuscript-skeleton-isprs.md` § 6, 2026-08-25) routes
   Seed 7 OUT to the companion paper, and D-5 asks whether this paper
   promises it as future work or reserves it silently. The 2026-09-03
   rulings stake the automation cell "in D.9 and M.12" and the
   methods-paper stub (`planning/llm-assisted-preregistration-methods-paper.md`)
   says the ISPRS paper "stakes the territory" while the methods paper
   "works it". The skeleton below is written so that any of the three
   envelopes in § 2 can be cut from it.

Reading set for this brief: the seven entries the S147 handoff named
(`srivastava_sound_2018`, `ofosu_pre-analysis_2023`, `willroth_best_2024`,
`sarafoglou_comparing_2023`, `thomas_mitigating_2026`,
`vaccaro_preregistration_2026`, `gerasimova_argumentbased_2024`), plus
`gould_but_2026` and `ross_introducing_2022`, the tail report's
"What the corpus now attests" section
(`reports/ab-plus-tail-report-2026-09-02.md`), Seed 7
(`docs/paper/discussion-seeds.md`), the naming brief
(`reports/d9-naming-decision-brief-2026-08-21.md`), and the M.12 slot
in `docs/paper/methods-draft.md`. Page anchors below use the entries'
`page_index` convention (printed page = index + 1, best effort).

## 1. What D.9 has to do

The D16 settlement gives the subsection two duties in one argument:
interpret the deviations, and deliver the retrospective (what
registration cost, what it bought, the grain-not-volume diagnosis, and
the waterfall → agile arc). DD7 = A means the errata story is told once,
inside the retrospective, and not again as a formal deviations
subsection. The subsection also carries the LLM-support claim, scoped to
implemented-and-evaluated, with the Thomas 2026 objection answered.
Methods § M.12 describes the practice; D.9 interprets it. Keep the two
from double-telling: M.12 says what was done and names the pitfalls,
D.9 says what it means against the field's measured base rates.

## 2. Three length envelopes (D-5 decides which)

| Envelope | Where | Words | What survives from § 3 |
|---|---|---:|---|
| (a) Pointer | ISPRS § 6 or § 7, one clause; full treatment in the companion | 40–70 | Moves 1 and 6 compressed to one sentence each; a citation to Ross 2022 and to the companion |
| (b) Paragraph | ISPRS § 6 as one paragraph of the 1,300-word Discussion | 180–250 | Moves 1, 2, 3, and 6; Moves 4 and 5 reduced to a clause; no epigraph |
| (c) Section | Companion/methods paper, full subsection | 1,200–1,800 | All seven moves at full skeleton, with the naming contrast and the base-rate table |

Anchor-density target for evidence prose is 28–32 per 1,000 words
(canonical register). Envelope (b) at 220 words therefore carries about
six or seven anchored specifics, which is why it cannot hold the
base-rate comparison in full.

## 3. Concept skeleton (mechanism, instance, boundary per move)

### Move 1. The registration delivered what it promises

- **Mechanism**: a registered confirmatory family with a pre-committed
  false-discovery rule converts a set of results into a small number of
  claims that survive multiplicity, and makes a falsified prediction
  more credible for having been written down.
- **Instance** (project record, `results/analyses-manifest.json`):
  rejection set {H2, H3, H7} at q = 0.05 over m = 7
  (`family-bh-fdr-confirmatory`); H2's registered direction was
  falsified (`e45-bootstrap-pairings`, both registered-instrument CIs
  exclude zero in the permutation direction); CMT-0106, the H1 pooled
  modality test, was executed outcome-blind on 2026-07-30 and returned
  a null (`h1-cmt0106-pooled-modality`, delta +0.0238, CI95
  [−0.0104, +0.0585]).
- **Boundary**: three of the fifteen numbered hypotheses never executed
  (H6 phase-4 transfer, H14, H15; manifest disposition rows), H2's
  Condition C never ran, and the registered § 8.9 post-experiment
  verification never ran (E78). Each is a disclosure obligation the OSF
  record makes visible. Do not repeat the S133 count that included H13;
  H13 ran later as registered-exploratory with a split prediction
  (`h13-overlap-2026-08-18`).

### Move 2. The over-bake, with receipts and a field comparison

- **Mechanism**: when the marginal cost of a registered clause falls,
  the register grows past what the study can honour. Specific
  operational bindings age badly; design-level commitments age well.
- **Instance** (project record): fifteen numbered hypotheses plus H4b
  (`osf/preregistration.md` headings); 83 numbered errata entries at
  drafting (M.12; the file carries 84 heading ids including a
  lettered one, re-count at prose time); an unregistered inference
  method adopted throughout (E45, tile-swap permutation testing; the
  registered method was bootstrap CIs with BH-FDR); a registered
  escalation trigger that fired only on an unregistered corpus and was
  judged uninformative (E60).
- **Field comparison** (`ofosu_pre-analysis_2023`, page_index 4, KP3):
  34 % of 169 coded pre-analysis plans registered one to five
  hypotheses, 18 % six to ten, 18 % eleven to twenty, 21 % twenty-one to
  fifty, 8 % more than fifty. Fifteen sits in the eleven-to-twenty band.
  Ofosu and Posner's operating threshold is five, not the tail: the
  safeguard discussion applies to every plan above five (60 % of those
  distinguished primary from secondary; 29 % pre-committed to a
  multiple-testing adjustment). Their median plan ran to eleven
  single-spaced pages, the longest decile above thirty-one (overflow,
  note 16). Denominator caution: the hypothesis-count bars sum to 169,
  not 195.
- **Boundary** (the first counterweight): the amendment count is a
  biased measure of drift, because absent a registration there is no
  record to deviate from (`ofosu`, page_index 1, KP7: "absent a PAP,
  there is no record of the analyses or hypotheses that were
  pre-specified"). State it as biased, not as understating: Ofosu and
  Posner decline a direction. Sarafoglou 2023 supplies the empirical
  version and it cuts both ways: self-reported deviations and
  independently coded ones agreed poorly (ICC = .43; 50 self-reported
  against 44 coded over 118 teams), the two records disagreed in both
  directions by category, and the coded record gave the stronger
  condition effect (BFr0 357.18 against 71.40)
  (`sarafoglou_comparing_2023`, page_index 12, KP3 and verifier E1).

### Move 3. Deviations disclosed, against the measured base rate

- **Mechanism**: a disclosed deviation is judged on its reason and
  timing; an undisclosed one is judged as concealment. The liability is
  the undisclosed deviation, not the disclosed one.
- **Instance** (`ofosu`, page_index 3, KP1): fourteen model deviations
  in the 93-paper subsample, one disclosed. Median paper omitted 25 % of
  its registered hypotheses (page_index 4, KP4); 18 % tested
  unregistered hypotheses and 82 % of those were silent (summary,
  verified). (`willroth_best_2024`, page_index 3, KP5): 34 psychology
  editors rated a disclosed deviation M = 3.3 on a 1–5 impact scale and
  the same deviation left unreported and found in review M = 1.3;
  Claesen et al. 2021 (re-reported at page_index 1) found deviations in
  93 % of 27 preregistered Psychological Science studies, 89 % of which
  did not report all of them. Cite the count of fourteen, not Ofosu's
  "19 %" (no reconcilable denominator).
- **Boundary**: the Willroth vignette varied disclosure, not volume;
  Willroth and Atherton warn that numerous substantive deviations may lead readers
  to treat the work as exploratory (page_index 8), and that a
  preregistration badge "might be misleading" once data-dependent
  deviations make risk of bias high (page_index 11, KP4). Our errata
  rows record date, type, impact, and often files or a commit, but
  carry neither the reason nor the timing axis Willroth's schema asks
  for (verifier check against `protocol-errata.md`: 81 entries at their
  count, none with reason or timing). That is a concession to make in
  D.9 and an apparatus change to consider (§ 6, ruling 5).

### Move 4. Grain, not volume

- **Mechanism**: what a registration can fix without seeing the data is
  design, hypothesis direction, decision rules, and the inference family.
  What it cannot fix well is any binding that depends on the data
  (exclusion rules, operationalisations, corpora, thresholds). Register
  rules and procedures; leave operational parameters to disclosed,
  rule-governed selection.
- **Instance**: Sarafoglou's blinding advantage was concentrated in
  exactly the data-dependent bindings, exclusion criteria (self-report
  10/61 against 1/59; independent coding 15/61 against 0/59) and
  operationalisation of the independent variable
  (`sarafoglou`, page_index 13, KP2). Srivastava's operational test:
  "If the data were different, could the decisions have been
  different?" (`srivastava_sound_2018`, page_index 7, KP6), with his
  own list of data-dependent checks worth the risk (manipulation
  checks, residuals, model checking). Gould's line: not whether a
  decision is data-dependent but whether it is systematic under
  preregistered rules or opportunistic, glossed as result-seeking
  without disclosure (`gould_but_2026`, page_index 2, KP4). The
  project's own rule-governed selection (Seed 6's plateau rule) is the
  worked instance.
- **Boundary**: a registered contingency rule is not automatically
  safe; Srivastava asks that contingency plans be checked for whether
  they could capitalise on chance (overflow, page_index 9). Willroth's
  prevention list reaches the same decision-tree device from the static
  side and presents it as deviation prevention, citing Nosek 2018
  (page_index 10); the "registered flexibility under another name"
  reading is ours and must be marked as ours.

### Move 5. The recipe is endorsement-with-citation, and grain is a continuum

- **Mechanism**: a lean upfront registration (design, a few sharp
  confirmatory hypotheses, procedural rules) plus registrations
  authored outcome-blind at each analysis boundary. The novelty clause
  on the recipe drops; the contribution is an executed instance in a
  computational-evaluation setting plus the LLM-support element.
- **Prior art to cite, with what each actually says**:
  - Srivastava 2018: "researchers can write adaptive preregistrations
    with plans to deploy flexible strategies ... sometimes iteratively
    in interim registrations as different parts of the data are
    observed" (page_index 10, KP1). His post-training interim
    registration before the holdout is touched (page_index 16, KP4) is
    the template our carried-operating-point transfer meets only in
    part: his guard is two-part, holdout plan registered before first
    contact plus the interim registration, and we match only the second
    half (verifier E5–E7).
  - Gould 2026: registered flexibility (decision trees) plus phase-based
    interim preregistrations (page_index 4, KP2–KP3); Box 1 tip 4
    contemplates "sequential analysis plans ... preregistered separately
    for the same study with metadata linking the chain", and the number
    of interims is unbounded, so per-analysis grain is a point on a
    continuum they already span (verifier KP2). Not a replacement for
    static preregistration (page_index 13, KP6). Cross-domain
    application "could be applied", untested outside ecology
    (page_index 0, KP5): an executed non-ecological instance is a
    contribution against an aspiration.
  - Vaccaro 2026: "Researchers may preregister an initial design with
    explicit decision rules for subsequent stages" (page_index 5, KP4),
    the second occupant of the staged cell, from machine learning; her
    remit reaches ML-style models through Alternative View 3
    (page_index 6, KP6) though her paradigm is agents as subjects.
  - Gerasimova 2024: a two-tier registration (argument-level plus
    per-study) in a versioned living document, post-evidence changes
    marked (page_index 7–10, KP1–KP3); the closest structural analogue
    on our reading, proposed and not demonstrated (page_index 15, KP6).
  - Nosek 2018 ("sequential preregistration"), Crüwell 2021 § 6.2,
    Ioannidis 2022 ("small bites" alongside, not instead of, registering
    the space): per the tail report's attestation list; take page
    anchors from those entries at prose time.
- **Boundary** (the objections the recipe must answer):
  - Policing: iterative plans are "tricky to implement in practice"
    because without a neutral gatekeeper a researcher cannot easily show
    the iterations were pre-specified (`ofosu`, page_index 7, KP2);
    Ofosu and Posner's own preferred remedy is labelling discipline plus
    mandatory reporting of every pre-specified analysis (KP5), which the
    analyses register already practises. Our answer is machine-readable,
    timestamped registers in a public repository, which lowers the cost
    of the demand Laitin's line names (framing hook, page_index 10).
  - Update-versus-deviate: "Once results are known, preregistrations
    should not be updated" (`willroth`, page_index 11, KP6). A
    just-in-time registration is written before the analysis it governs
    and after earlier results are known; the prose must state that
    ordering plainly so it is not read as post-results updating.
  - The evidenced alternative: analysis blinding halved the modelled
    deviation probability (38 % against 20 %, BFr0 71.40) but saved no
    time (BF0− 13.19; Stage 1 hours M = 19.11 blinding against 8.43
    preregistration) (`sarafoglou`, page_index 8–10, KP1 and KP5).
    Their recommendation is the hybrid, preregister then finalise on
    blinded data (page_index 15, KP7), which CMT-0106 instantiates once.
    Their scope limits travel: small groups often have no guarantee
    blinding was effective (page_index 15, KP6), and the study has no
    unregistered baseline.

### Move 6. The LLM-support claim, stated against the empty cell

- **Mechanism** (PI, Seed 7): LLM assistance collapses composition and
  revision friction, which is what makes registration at the analysis
  grain practicable, and is also what made the over-bake cheap to
  enumerate. The claim cuts both ways and the prose says both halves.
- **Instance, the friction baseline**: 88 % of 155 surveyed potential
  plan users spent a week or more per plan, 26 % more than a month, 34 %
  reported project delay (`ofosu`, page_index 6, KP6; 2018 convenience
  sample, cite as a share of respondents). Gould's case-study lead
  expected about a month's delay and found it much longer, attributing
  the overrun to first-time use (`gould`, summary, verified): a learning
  cost on their framing, which is the friction the LLM claim addresses.
- **Instance, the empty cell**: across the 30 preregistration sources
  nothing implements or evaluates an LLM that authors or checks a
  registration (tail report). Nearest: Pu 2019's "could even be
  partially or fully automated" (proposal); Thomas 2026 § 6, autonomous
  AI-scientist systems "should commit to the procedure and
  eligible-model set before the confirmatory model is available"
  (`thomas_mitigating_2026`, page_index 13; proposal, verifier E4);
  Vaccaro has zero hits for "automat*" across fourteen pages and makes
  LLM judges a registrable object (§ 4.3). Gould cite Hofman et al.
  2023, so Gould's silence shows only that Gould do not occupy the cell.
- **The objection and the answer**: Thomas et al. credit checklists
  with making disclosures "more principled" but hold they "have limited
  effectiveness, since they rely solely on self-report" (page_index
  12–13, KP6; the referent is Goldberg et al. 2024's LLM checklist
  assistant). The answer is the three machine-checked layers (errata
  file, classified analysis register, generated hypothesis-outcome
  table), not more prose. State the objection at its actual strength
  (qualified, not a dismissal).
- **The concession to make first**: our registration was written
  against models that already existed (`osf/preregistration.md` line
  1199: "Primary: Gemini 3 Flash, Gemini 3 Pro"). "Once released, an
  LLM is always accessible", so traditional preregistration "cannot
  safeguard LLM-based statistical analyses against p-hacking"
  (`thomas`, page_index 1, KP1). Two mitigations, both ours to argue:
  the study tuned toward accuracy against adjudicated reference data and
  reported the transfer loss, which Thomas's KP5 treats as differently
  placed from tuning toward a downstream test; and the Gemini 3.7
  campaigns (Obs 441, 444, 447) were run against a model that
  postdates the registration `[unverified: the Gemini 3.7 Flash release
  date against the 2026-01-31 lodgement; the 3.7 cards carry no release
  date]` with carried operating points committed before any deployment
  scoring (`planning/gemini37-55map-2026-08-29.md`, 2026-08-31
  changelog entry), which is Thomas's device applied post hoc rather
  than by design. Do not claim the second as compliance; claim it as the
  comparison case.
- **Boundary**: Thomas's evidence is two text binary-classification
  tasks scored by thresholds, and detection at F1 and MCC over match
  radii lies outside it by their own scoping (page_index 13, KP4).
  Vaccaro's "Preregistration provides the friction that cost no longer
  does" (page_index 6) answers the cheap-inference objection but is a
  position paper with an illustrative simulation. The drift pitfall
  (claude-obs 86; a model drafting toward a thesis drifts toward it) is
  the project's own receipt that LLM authoring needs an independent
  reader.

### Move 7. The first-person anchor and the disciplinary baseline

- **Mechanism**: the advocacy predated practicability; the friction
  collapse converts the 2022 argument into routine practice; the
  over-bake → grain → just-in-time arc is the lived learning between
  the two points (PI, Seed 7).
- **Instance** (`ross_introducing_2022`, page_index 7, KP1): "A search
  of OSF's 304,904 registrations (as of March 19, 2020) produced only
  four" non-teaching hits for archaeology, all Open-Ended Registrations
  depositing data and code, none a preregistration of approach or
  method (KP2). The chapter's registrable objects, data models and data
  workflows (KP5), are what the apparatus executes.
- **Boundary**: the count is six years old against a registry that has
  grown; both the denominator and the date must travel, and a re-run of
  the search is owed before the figure appears in prose. The chapter's
  "best-effort" licence is scoped to fieldwork findings outside
  researcher control (KP3), and its transparency-not-replication
  concession (KP6) is attributed to the discipline at large; a
  computational study can be replicated outright, so D.9 argues for the
  stricter bar rather than inheriting the lowered one. Self-citation
  needs care: the verifier layer flagged self-flattering drift in this
  entry.

## 4. The naming ruling: inputs updated by the corpus

The naming brief's four options stand. Two facts settle the occupancy
question the brief left open, and one new consideration enters.

- **Term occupancy is thin and undefined.** Srivastava uses "adaptive
  preregistration" four times as a lowercase common noun, never in
  quotation marks, never formally defined; the concept he defines is
  decision independence (37 occurrences) (`srivastava`, page_index 2,
  10, 11, KP2 and verifier). "Registered flexibility" occurs nowhere in
  Srivastava; his phrase is "plans to deploy flexible strategies", and
  he writes "interim registration" (six occurrences), never "interim
  preregistration". Gould use the term "sensu Srivastava, 2018" and also
  present the methodology as one they "call" Adaptive Preregistration;
  the two-component structure is their construction (`gould`, KP1 and
  verifier). Adopting "adaptive preregistration" therefore cedes no
  brand; it adopts a descriptive common noun with two citations.
- **Grain is a continuum, not a boundary.** Gould's Box 1 tip 4 and
  unbounded interims (verifier KP2) mean "per-analysis versus
  phase-based" is a difference of degree. The sharpest genuine
  contrasts left are the executed non-ecological instance, the
  outcome-blind ordering, and the LLM-support element.
- **New: "just-in-time" collides with the PI's own prior usage.** Ross
  and Ballsun-Stanton 2022 diagnose archaeology's problem as
  "just-in-time" research and fieldwork, "where insufficient attention
  is paid to articulating a research design before fieldwork begins"
  (`ross`, framing hook and KP4). Option 1 in the naming brief,
  "just-in-time preregistration", would reuse the chapter's pejorative
  as the name of the remedy. Either the prose reclaims the phrase
  deliberately (registration delivered just in time is the cure for
  research done just in time), or the option drops. A reader of the
  chapter will notice; the choice should be explicit.

**Recommendation for the ruling** (mine, for the PI to take or leave):
option 2, "adaptive preregistration" with the LLM modifier
("LLM-assisted adaptive preregistration"), citing Srivastava for the
term and Gould for the methodology, contrasting our variant on three
axes (analysis-grain interims, outcome-blind ordering, LLM-supported
authoring with machine-checked layers). Field hygiene favours one term
over three; the LLM element carries the priority claim regardless.
"Micro-registration" stays as the project record's internal name.
Question 4 of the naming brief (the prospective GT-free test adopts the
chosen name) should be ruled at the same time.

## 5. Epigraph candidates

Each entry carries a framing hook. Seven are on point; the ISPRS
venue is unlikely to take an epigraph, so these are for envelope (c)
or for an opening sentence in the author's voice.

- Srivastava, page_index 21: "should not let the perfect be the enemy
  of the good. Almost any researcher can at least create a partial
  preregistration, which will create transparency."
- Gould, page_index 14: "Any first attempt to implement Adaptive
  Preregistration is unlikely to work perfectly ... Being upfront about
  this in study reporting is still better than avoiding preregistration
  entirely."
- Willroth, page_index 11: "preregistration is a skill, and
  preregistrations are likely to be messy while that skill is being
  honed" (attributed there to Kirtley et al. 2021).
- Ofosu, page_index 10 (Laitin 2018): "We have increased the supply of
  transparency but have given insufficient attention to generating a
  demand for it".
- Sarafoglou, page_index 2: "This makes preregistration a challenge for
  research that includes any sort of nontrivial statistical modeling".
- Thomas, page_index 1: "the result might also appear superficially
  reproducible to a reader: rerunning the reported configuration on the
  reported model may obtain similar outputs, even though the
  configuration was selected precisely because it produced the desired
  conclusion".
- Vaccaro, page_index 6: "Preregistration provides the friction that
  cost no longer does."

## 6. Rulings needed before prose

1. **Home and envelope (D-5).** Rule: which of (a), (b), or (c) this
   paper carries. Reason: the skeleton routes Seed 7 OUT while the
   2026-09-03 rulings stake the automation cell in D.9. Check: the
   Discussion's 1,300-word budget and whether M.12's paragraph already
   discharges the staking for the ISPRS paper.
2. **The name.** Rule: option 2 as recommended, or another. Reason: § 4.
   Check: the "just-in-time" collision with Ross 2022.
3. **The Thomas concession.** Rule: whether D.9 names the
   already-released-model exposure and offers the 3.7 campaigns as the
   comparison case. Reason: better conceded than found by a reviewer
   who knows the paper. Check: the carried-point commitments on the 3.7
   cards predate the runs (`planning/gemini37-55map-2026-08-29.md`).
4. **The C1↔C3 bridge.** Rule: whether D.9 claims that the
   adaptive-preregistration and statistical-analysis-plan literatures do
   not cite each other as a secondary contribution. Reason: verified
   structural hole in the S139 scout; costs a sentence. Check: Gamble
   2017 and Hemming 2020 entries for any citation of Srivastava or
   Gould.
5. **Willroth's schema.** Rule: whether the errata register gains
   reason and timing fields before submission, or D.9 concedes their
   absence. Reason: an apparatus change touching 83 rows is not a
   drafting decision. Check: whether timing can be derived from the
   existing date and commit fields without re-adjudication.
6. **The Sarafoglou hybrid.** Rule: whether D.9 says the project
   "already practises" the preregister-then-finalise-blind hybrid on the
   strength of one outcome-blind execution (CMT-0106). Reason: one
   instance is an instance, not a practice. Check: whether any other
   analysis in the register was executed outcome-blind.
7. **The OSF baseline re-run.** Rule: whether the four-of-304,904
   figure appears at all without a fresh search. Reason: the entry's own
   caution. Check: a current OSF keyword search for "archaeology",
   dated, before prose.

## 7. Drafting rules carried from the register and the outline

- One subsection (DD7). The errata story is told once, inside the
  retrospective.
- Skeleton legs per move: mechanism, one instance, honest boundary.
  Evidence prose expands; do not compress the boundaries away.
- Every number above traces to an entry or the manifest; a number that
  moves at prose time is re-read at source, not copied from here.
- Concede at about one sentence in eight, and only where the
  counter-position has merit: the policing objection, the Thomas
  exposure, and the Willroth schema gap qualify; performed candour does
  not.
- The mappings from the sources' constructs to our registers (Gerasimova
  living document ≈ errata log; Willroth decision trees ≈ registered
  flexibility) are ours and are marked as ours.
- Citations are venue-determined; this brief names sources by citekey
  only.

## Changelog

### 2026-09-03 — Original publication

Written in Session 148 from the AB+ preregistration cluster (the seven
entries the S147 handoff named, plus Gould 2026 and Ross 2022) once
the corpus was complete. Records the three standing gates, the three
length envelopes pending D-5, a seven-move concept skeleton with
anchors, the naming inputs the corpus settled (Srivastava's common-noun
usage; Gould's "sensu"; the grain continuum) and one it raised (the
"just-in-time" collision with Ross 2022), seven epigraph candidates,
and seven rulings needed before prose.
