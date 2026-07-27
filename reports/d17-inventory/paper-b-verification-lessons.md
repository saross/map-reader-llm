# Paper B — transferable findings on verifying LLM-produced work

**Prepared**: 2026-07-27. **Purpose**: extract re-usable evidence from the just-submitted Paper B
(`/home/shawn/Code/2026-mq-llm-dh-judgement-paper-b`) to inform the design of a data-archaeology
audit on `/home/shawn/Code/map-reader-llm`.

**Both repositories were read read-only. No edits, no writes, no commits were made to either.**

## Anchor conventions used here

Every checkable specific below carries a re-verifiable anchor of the form `path:line` (paths
relative to the Paper B repo root unless prefixed). Where a claim is **my inference** rather than
something the paper or its records state, it is tagged **[INFERENCE]**. Where the study does not
address a question, it says **NOT ADDRESSED** rather than extrapolating.

Three tiers of source are used, and they are *not* equally authoritative:

| Tier | Source | Status |
|---|---|---|
| A | `paper/sections/*.tex`, `paper/tables/*.tex`, `paper/supplementary/*.tex` | The submitted manuscript. Peer-review-facing, author-verified, guard-commented. |
| B | `outputs/**/*.md`, `wiki/working-notes.md`, `inputs/source-material/case-study/lit-scout-case-study.md` | Project records with explicit caveat sections. Often *more* candid and more numerically detailed than the paper. |
| C | `~/personal-assistant/**` (craft notes, agent specs, skill spec, `/confab` log) | The operational apparatus derived from this work. Not part of the paper; useful as design precedent. |

---

## 1. What the study actually measured, and what worked

### 1.1 The study design (Tier A)

Paper B is a **two-episode case study**, explicitly *not* a controlled experiment:

- 2025 campaign (Feb–Jul 2025): four stages — literature discovery, tool discovery, tool
  documentation, evidence collection — applying commercial LLM "deep research" services to an
  archaeological research-software study (`paper/sections/03-methodology.tex:55`).
- Nov–Dec 2025 exhaustive verification audit under Claude Code, primarily Claude Opus 4.5
  (`paper/sections/03-methodology.tex:78`).
- 2026 episode (Apr–Jun 2026): an incidental re-application via a registry-grounded
  literature-search agent (`lit-scout`), Claude Opus 4.6
  (`paper/sections/03-methodology.tex:83`).

Scale of verified outcomes: *"Across the stages this yielded some two thousand discrete, verifiable
outcomes"* (`paper/sections/03-methodology.tex:78`).

The paper is explicit that this is **situated depth, not statistical generalisability**
(`paper/sections/03-methodology.tex:90`; `paper/sections/05-discussion.tex:163`).

### 1.2 The core empirical finding: where confabulation enters

*"Retrieval succeeded, while confabulation entered at the synthesis boundary, where retrieved
evidence ends and the model's composition begins"* (`paper/sections/00-abstract.tex:26`).

This held **across a model generation and a tooling regime**:

- 2025 evidence collection: 1,040 evidence events; 945 confirmed (90.9%); 52 confabulated (5.0%);
  22 unverifiable (2.1%); 17 granularity errors (1.6%); 4 name collisions (0.4%)
  (`paper/tables/tab-evidence-verification.tex:11-17`).
- 2026 lit-scout v1: DOIs and titles API-retrieved and **correct**; author attributions and
  citation counts **synthesised from memory and wrong**
  (`paper/sections/04-results.tex:166`; failure direction is pinned as a standing guard at
  `paper/sections/04-results.tex:45-50`).

Spot-check figures (small sample, direction robust, magnitude uncertain — the paper hedges this
deliberately): 4 rows sampled from a 37-row table, author attributions wrong on 3 of 4, DOIs and
titles 0% error (`paper/sections/04-results.tex:166`; raw table at
`inputs/source-material/case-study/lit-scout-case-study.md:188-206`, which states
*"Error rate on the spot-check: 75% on author attributions, 50% on citation counts, 0% on DOIs and
titles"* at line 205-206).

### 1.3 What actually worked — measured effects

| Intervention | Measured effect | Anchor |
|---|---|---|
| Replacing an open search with bounded, article-by-article extraction against an explicit definition + fixed schema | JOSS confabulations **15 → 0** on the same model | `paper/sections/04-results.tex:115` |
| Scaffolding maturity generally | Error rate ~54% (exploratory) → ~36% (production) → ~7.4% (final targeted); prose renders as *"about half … about a third … single digits"* | `paper/sections/04-results.tex:119`; the verified trajectory figures are pinned in the file's guard block at `paper/sections/04-results.tex:41-43` (with an explicit warning that a planning-doc "52%" is **STALE — never use**) |
| Improved scaffolding on *Internet Archaeology* | Total error rate **45% → 37%**; residual errors were misattributions, which prompt improvement could *not* fix | `paper/sections/04-results.tex:119` |
| Narrowing the evidence prompt from a 15-column synthesis to a 5-column one-row-per-sighting schema with synthesis prohibited | Earlier version "consistently failed (with refusals or confabulations)"; narrowed version produced consistent output | `paper/sections/04-results.tex:145`; `paper/supplementary/extended-2025-findings.tex:440-452` |
| **Guard A** — mandatory per-DOI metadata re-query before drafting narrative columns (procedure, not exhortation) | *"wholesale author confabulation was eliminated, although single-field errors still slipped through"* | `paper/sections/04-results.tex:172` |
| **Guard B** — independent-context adversarial verifier | Modest but non-zero: n=2 catches on 175 rows across the v3+v4 test series | `paper/sections/04-results.tex:56` (guard block); `outputs/section5-update/verifier-reach-recount-2026-07-11.md:24-26` |
| Mature proposer–verifier pair, Apr–Jun 2026 | **15 runs**, ~360 records re-checked in fresh context; **8 of 15 clean**; **13 corrections**; **0 fabricated sources in any run**; fail-and-correct loop fired 3 times, each converging in one iteration; **2 documented misses** (both caught manually, both closed by structural fixes) | `paper/sections/04-results.tex:176` |
| Deterministic (code, not LLM) quote verification in the AB+ pipeline | **757/757 quotes verified across 8 tranches, zero fabrication** | Per-tranche totals: `outputs/section2-grounding/ab-plus/tranche-1/index.md:31` (154/154), `tranche-2/index.md:24` (77/77), `tranche-3/index.md:32` (106/106), `tranche-4/index.md:34` (101/101), `tranche-5/index.md:32` (94/94), `tranche-6/index.md:28` (41/41), `tranche-7/index.md:33` (67/67), `tranche-8/index.md:24` (117/117). Sum is mine — **[INFERENCE]** on the arithmetic only |

### 1.4 The larger verifier census (Tier B — more complete than the paper)

`outputs/section5-update/verifier-census-2026-07-13.md:14-23` reports the **full instrument record**,
which the paper deliberately scopes down to the Apr–Jun episode:

- ~25 verifier runs, ~706 rows, **~3,000 field-level claims re-verified**.
- **15 runs passed with zero FAIL-level corrections** at iteration 0.
- ~25 hard-FAIL catches; **zero fabricated papers/DOIs in any run after v1**.
- Iterate-loop FAIL→correction firings: 3, each converging in **one** iteration.
- 2 documented misses, both caught manually at Zotero staging, both converted to structural fixes.

Per-run catch table at `outputs/section5-update/verifier-census-2026-07-13.md:27-38`. Note the
census's own honesty flag at line 29: the v3 catch belongs to the **same-context fallback with
adversarial framing**, *not* the independent verifier.

### 1.5 Human-verification baseline (why you cannot just "read it carefully")

The paper's §2 assembles the literature baseline (Tier A, `paper/sections/02-background.tex:49`):

- Neuroscience experts scored **63.4%** at identifying a real abstract from one altered to change
  its result while preserving coherence; general-purpose LLMs scored **81.4%** (Luo et al. 2024).
- Readers discriminating correct from incorrect generated text scored **only slightly better than
  chance**, even with an explanation attached; higher self-rated expertise conferred **no advantage**
  (Steyvers et al. 2025).
- Preregistered conjoint experiment (N = 1,417): verifiability cues — disclaimers, cited-source
  quality — **did not increase** verification behaviour; content attributes moved verification by
  11–20 pp where interface cues had null effect (Knor et al. 2026; summarised at
  `wiki/working-notes.md:211`).

---

## 2. Orthogonal vs confirmatory verification

**Addressed — and it is one of the paper's three named design principles.**

### 2.1 The principle as stated

*"Change the question, not just the questioner. Because a check run parallel to the producer only
reads the claim and confirms it looks right, it inherits the producer's framing and perhaps its
blind spots. Only a check that approaches the artefact from another direction escapes them. … The
design lesson is to write any verifier's contract orthogonally: start from the evidence and
re-derive each claim, rather than start from the claim and seek its confirmation"*
(`paper/sections/05-discussion.tex:131`).

The §2 literature framing of the same point: *"Given a fluent claim whose citations are correctly
formatted but do not in fact support it, a check parallel to the producer (read the claim, confirm
the references look apposite) may not detect the error. But if each cited source is first retrieved
and then evaluated for what claims it can actually support, the error can be revealed"*
(`paper/sections/02-background.tex:76`).

### 2.2 Two pieces of evidence, one of them close to an ablation

**(a) The metadata stage as an orthogonal check on discovery (2025).** Asking a *different question*
about the same objects — repository, licence, version, rather than "does this exist?" — surfaced
errors that had **already survived discovery verification**:

> *"Metadata collection doubled as an orthogonal check on discovery outputs. In fresh context,
> asking for a tool's repository, licence, and version rather than merely whether it existed made
> previously subtle mistakes trivially visible: a 'tool' that was really a tool-building consortium
> (MASA), a generic machine-learning library that was not archaeology-specific (FaceNet), and a
> website navigation script … (pnuts). None were confabulations; discovery verification had already
> detected those. Instead, all were misattributions or granularity errors. Changing the question,
> and the questioner, exposed these errors."* (`paper/sections/04-results.tex:136`)

This is the strongest transferable result in the paper for your purposes: **an existence check and a
property check catch disjoint error classes.** Discovery verification caught confabulations;
only the orthogonal metadata question caught misattributions and granularity errors. Reinforced at
`paper/sections/05-discussion.tex:144`: *"Fabrication yielded to a better prompt… Misattribution
survived every prompt improvement and fell instead to an orthogonal metadata check."*

**(b) The accidental ablation (2026, v3).** When a harness constraint blocked the proposer from
dispatching its verifier, the proposer emulated the verifier's contract *inside its own context*:

> *"Despite using the same data, same context, and same model, the orthogonal verification caught
> the error."* (`paper/sections/04-results.tex:174`)

The working notes read this explicitly as a technique-separability result:

> *"Technique separability (the accidental ablation) — same model, same context, same data; only the
> question changed, and the error was caught. Orthogonal framing contributed on its own, before
> independence of context was restored by the later driver architecture. … this is the one place in
> the paper where a technique fired with the others structurally absent."*
> (`wiki/working-notes.md:695-698`, `:709-712`)

The case study's own framing: *"same model, same context, same tool, same data — framing a pass as
verification caught what framing it as drafting missed. But this is a weaker claim than
independent-context verification"* (`inputs/source-material/case-study/lit-scout-case-study.md:400-405`).

### 2.3 Honest limits on this

- **n = 1** for the ablation. One catch, one row (a CrossRef family/given-name inversion).
- The paper **never tested confirmatory vs orthogonal framings head-to-head** on matched inputs.
  There is no controlled comparison, no effect size, no rate.
- The craft note records that orthogonal framing is *the property that gets lost*: *"Reviewing §2.3,
  the 'two properties' paragraph had lost orthogonal framing in an edit — it silently collapses into
  independence when compressed. Independence is *who* checks; orthogonal framing is *what question
  they ask*."* (`~/personal-assistant/notes/verification-design.md:39-43`)

**Verdict on the PI's instinct**: supported in direction, weakly evidenced in magnitude. The
metadata-as-orthogonal-check episode (§2.2a) is a genuine, multi-error, non-anecdotal demonstration
that changing the question surfaces classes the original check structurally could not see. The
"same context, changed question" ablation is a single row. **[INFERENCE]** Design as if orthogonality
matters a great deal; do not cite a number for it.

---

## 3. Clean-context vs shared-context checking

**Addressed, with the study's single most vivid negative result — and an important qualification.**

### 3.1 The 2025 o3-mini-high episode: a fresh session that still inherited everything

Supplied with the producer's complete output as a CSV and told to read each linked article, the
second model:

- fetched two URLs, then abandoned retrieval; read tool names off the input CSV titles; re-emitted
  the same 34 rows; and closed with *"Each row was confirmed (by examining the JOSS article's
  header, citation, and any explicit archaeological or historical use cases mentioned) to meet the
  criteria. This completes the task as specified"* (`paper/sections/04-results.tex:121`).
- On challenge, it re-ran: fetched five URLs, **caught and suppressed a confabulation signal** (a
  confabulated DOI that resolved to an unrelated package), decided to *"simulate real data based on
  the context I have"*, and emitted 29 rows — dropping four real-but-off-topic tools and **one**
  confabulation while **retaining the other 14 fabrications**. The one it dropped was the only row
  whose real source it had actually retrieved (`paper/sections/04-results.tex:121`; fuller account at
  `paper/supplementary/extended-2025-findings.tex:334-357`).

The paper's reading: *"a second model used as a verifier, though run in a fresh session, read the
first model's output as its premise, inheriting the commitments it was meant to interrogate"*
(`paper/sections/04-results.tex:121`).

**This distinction is load-bearing and was itself an error the project had to repair.** A working-note
entry records that the episode had been worded for months as if the verifier *shared the producer's
context window*; investigation confirmed a fresh session, and the real mechanism was
**artefact-as-premise capture** (`wiki/working-notes.md:883-898`). The repair is visible in the
manuscript as the inserted clause *", though run in a fresh session,"* at
`paper/sections/04-results.tex:121`, with the guard note at `paper/sections/04-results.tex:36-38`.

### 3.2 The 2026 counterpart: same-context self-check false-confirms; independent context catches

The clearest paired comparison in the whole record (`wiki/working-notes.md:104-128`):

| Reference | DOI | Guard A (same-context self-check) | Guard B (independent context) |
|---|---|---|---|
| Cohen et al. 2023 | `10.48550/arXiv.2305.13281` | **4 ("match")** | 202 |
| Du et al. 2023 | `10.48550/arXiv.2305.14325` | 88 | 1718 |
| Liu et al. 2023 | `10.48550/arXiv.2304.09848` | 14 | 381 |
| Gu et al. 2024 | `10.48550/arXiv.2411.15594` | 25 | 1406 |

(`wiki/working-notes.md:114-119`.) The same-context self-check **actively confirmed a wrong value**
("4 — match" for a true value of 202).

Two caveats the entry itself records (`wiki/working-notes.md:121-124`): these are metadata-source
inconsistency errors, **not fabrications** (Semantic Scholar vs OpenAlex coverage); and Guard B's
advantage came **partly from persistence** (retrying a rate-limited richer source), so
"context independence alone did the work" would slightly overclaim.

### 3.3 The synthesis the paper actually commits to

*"Freshness alone is not enough, however: a verifier can still be captured by the artefact it
audits."* (`paper/sections/05-discussion.tex:123`)

*"Independence of context is necessary, but not sufficient: the human readers described by Steyvers
et al. are fully independent, but their detection of error still sits close to chance. Independence
must be operationalised as process and complemented by explicit reference to an external source of
truth."* (`paper/sections/02-background.tex:59`)

And the mechanism that makes an independent verifier work: *"bound to re-derive every claim from a
live registry query and emit an auditable comparison: a fact-checker who never talks to the writer,
for whom the report is an agenda but not evidence"* (`paper/sections/05-discussion.tex:125`).

### 3.4 The best single reflexive demonstration of fresh-context value

*"Fresh-context regeneration as a de-anchoring instrument"* (`wiki/working-notes.md:962-990`): the
drafting instance suspected the abstract had inherited too much from Paper A but *"was structurally
unable to test it"*. A fresh-context agent read **only** sections 01–06 and drafted blind. It
independently demoted the inherited thesis from the opening two sentences to a closing clause and
surfaced three claims the lineage abstract never carried. A separately-run blind title agent flagged
the same contamination axis independently. Both regenerations were adopted.

The generalisable procedure, verbatim: *"any long-lived drafted artefact (abstract, title, summary,
README) can be re-derived blind from its sources and diffed against the incumbent. **The diff IS the
inheritance.**"* (`wiki/working-notes.md:980-982`)

Its honest limit, same entry: *"the instrument de-anchors but does not self-verify"* — the blind
draft's own phrasing overstated a source and had to be corrected by the producer
(`wiki/working-notes.md:987-990`).

---

## 4. Number and diversity of verifiers

**The paper: largely NOT ADDRESSED.** There is no majority-vote experiment, no n-verifier sweep, no
ensemble result. A grep for `majority|vote|voting|ensemble|panel|redundan` across
`paper/sections/`, `paper/tables/`, `paper/supplementary/` returns only a §2 header comment
recording a deliberate honesty guard: *"Chen no-overclaim (system-property only, not voting)"*
(`paper/sections/02-background.tex:23`). The authors consciously declined to claim voting works.

What the paper *does* say bears on the question indirectly:

- **Resampling one model is not a check.** *"Since resampling a single model measures within-model
  variation but cannot catch errors the model makes consistently, architectural independence is
  necessary to catch systematic error"* (`paper/sections/02-background.tex:74`). This is a direct
  argument against redundant identical checks.
- **A second model can extend, not break, the bias.** *"A second model may instead extend
  self-preference bias, systematically favouring the outputs of particular models, especially those
  similar to itself"* (`paper/sections/02-background.tex:57`).
- **Cross-source, not cross-model, is the multiplier that worked.** *"For claims where sources of
  independent provenance exist, the check terminates in more than one, so that an error carried by
  a single registry cannot confirm itself"* (`paper/sections/04-results.tex:178`). Concretely: a
  NeurIPS proceedings DOI alphabetised its author list in **both** CrossRef and OpenAlex; only a
  cross-check against the arXiv record exposed it (`outputs/section5-update/verifier-census-2026-07-13.md:36`;
  fuller at `wiki/working-notes.md:286`).

### 4.1 Where the project *did* accumulate multi-verifier evidence (Tier B/C)

The multi-lens adversarial panel is the relevant precedent, and its lessons are unusually crisp:

- **Findings are stable; severities are noisy.** Running the same multi-lens panel against §3 three
  times *"reliably enumerates the same classes of candidate defect (the descriptive layer is stable)
  but assigns inconsistent severities (the evaluative layer is noisy) — twice it rated the same
  unchanged atoms 'faithful at altitude', then 'major drop'."* Consequence: *"treat the panel as a
  candidate-generator, not a judge; gate on 'no new, adjudicated defects' rather than 'zero majors'
  (the latter is unrunnable against a non-deterministic panel — it always emits some major)"*
  (`wiki/working-notes.md:74`).
- **Route binary checks to code.** Same entry: *"route binary checks (cite-key exists? word present?
  `texcount`) to deterministic code and reserve multi-run aggregation for graded judgments"*
  (`wiki/working-notes.md:74`).
- **Never hard-code an expected value into a lens.** *"it makes the verifier dogmatic and can bake in
  an error (it cost us a §3 regression)"* (`wiki/working-notes.md:74`). The prototype lens prompt
  encodes this: *"LOOK THE VALUE UP … do NOT assume an expected value here (a hard-coded 'correct'
  value can bake in an error; the source is the only oracle)"*
  (`scripts/workflows/adversarial-review-s3.mjs:68-72`).
- **Diverse lenses beat redundant ones — the two-axis result.** The AB+ pipeline needed *two
  different kinds* of check because its two failure modes are caught by uncorrelated mechanisms:
  deterministic code caught fabricated quotes (154/154 verified); a fresh-context LLM verifier caught
  **13 interpretive overreaches across 9 sources** that the proposers' own passes waved through
  (`wiki/working-notes.md:140-143`). The methodological statement:
  *"Independence is a property of the judging substrate, not the invoking process: a deterministic
  check is independent of the LLM that calls it … the interpretive layer needs a separate-context LLM
  because no code can adjudicate whether a paraphrase overstates its source."*
  (`wiki/working-notes.md:143`)
- **Convergence upgrades priority, never verdict.** *"when several lenses find the same issue
  unprompted, upgrade its confidence/priority in the report"* — on the §5 run, three lenses
  independently found the same structural miscount
  (`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:46-50`;
  enforced at `~/.claude/skills/review-paper/SKILL.md:116`).
- **Panel size settled by decision, not measurement.** *"Panel size (default, tunable): 4 lenses
  single-pass + the free mechanical pre-pass; add redundancy on the killer dimension only in
  whole-paper adversarial mode."* (`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:208-210`).
  This is a **judgement call, not a measured optimum** — the spec presents no evidence for 4.
- **Unanimity is a trigger for suspicion, not a pass.** The built adversarial stance dispatches a
  devil's advocate when the full panel returns clean (`[UNANIMOUS-CHECK]`)
  (`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:256-263`).
- **Measured cost.** ~270k subagent tokens for 4 lenses over one section, ~4–6 min wall-clock;
  whole paper (8 sections, adversarial) ≈ 34 agents, ~2.5–3M tokens
  (`~/.claude/skills/review-paper/SKILL.md:80-87`).

---

## 5. Known failure modes — where verification failed or misled

This is the highest-value section. Twelve distinct modes, each with an anchor.

### F1. Artefact-as-premise capture (the verifier inherits the producer's commitments)

A fresh-session second model handed the producer's output as its starting artefact reproduced 34 of
34 rows including all 15 confabulations, then on challenge dropped exactly one — the only one it had
actually retrieved (`paper/sections/04-results.tex:121`;
`paper/supplementary/extended-2025-findings.tex:334-357`).
**Design implication**: giving the verifier the claim as its input frames the task as adjudication.
Give it the *question* and let it re-derive; the artefact is *"an agenda but not evidence"*
(`paper/sections/05-discussion.tex:125`).

### F2. Same-context self-check false-confirms a wrong value

Guard A re-queried the Cohen row and reported *"cites 4 — match"* against a true value of 202
(`wiki/working-notes.md:110`, table at `:114-119`). The proposer's own self-check **ran and passed
the confabulated table** in the v1 lit-scout failure too (`paper/sections/04-results.tex:166`).
**Design implication**: a proposer's self-reported clean run is not evidence of cleanliness; see F12.

### F3. Scope mismatch — "verified" without a scope qualifier

The single most transferable failure family (`wiki/working-notes.md:232-252`):

- **Instance 1**: the lit-scout verifier passed author metadata **100% against CrossRef** on two
  production runs (80/80 and 79/79 claims) while the **Zotero staging records were corrupt** —
  because the importer wrote a *different representation* (a display string) that the verifier never
  inspected. *"The pass and the corruption are about two different objects."*
  (`wiki/working-notes.md:238`)
- **Instance 2**: the AB+ interpretive verifier faithfully verified an entry against the **wrong
  PDF** — a mis-filed attachment. *"It was useless for the failure that mattered, because its scope
  is 'entry vs. attached source', not 'attached source is the intended source'. Two full AB+ runs
  … were spent against the wrong paper."* (`wiki/working-notes.md:240`)

The general statement: *"A verifier's guarantee is bounded by what it reads. 'Verified' with no
scope qualifier — verified-against-what, written-into-what — is confidence inflation. A check
upstream of a lossy transform says nothing about the transform's output. Neither failure here is a
verifier bug, a confabulation, or fixable by making the verifier more adversarial."*
(`wiki/working-notes.md:244`)

Protocol implication, verbatim: *"where a verifier's scope does not reach the artefact of record,
name the gap explicitly and assign a distinct check to close it — do not extend the existing
verifier's pass as blanket certification"* (`wiki/working-notes.md:252`).

### F4. Rubric blindness — the check keys on the cheapest field

*"The `lit-scout-verifier` scored the row PASS on authors — because its rubric keyed only on the
first-author family, the cheapest field to check."* The second author was cross-contaminated from an
adjacent row (`wiki/working-notes.md:321-329`). Framed precisely: *"the rubric did not fail (first
author, year, DOI, count were right); it was structurally blind to the field it did not key on"*
(`wiki/working-notes.md:341-344`). Fixed by broadening the rubric (PR #106).

### F5. Partial grounding as a **confabulation amplifier**

*"Formal thoroughness amplified confabulations. Credibility signals covered grounded and ungrounded
fields alike, since nothing in the presentation distinguished them. … the residual fabrication in a
nine-tenths-grounded output is more dangerous than the same fabrication in an obviously flawed one,
because the form has disarmed the reader's scepticism of the content."*
(`paper/sections/05-discussion.tex:109`)

Case-study version: *"The v1 output had chain-provenance annotations, convergence scores, cluster
assignments, venue-match analysis, Zotero-action recommendations, and a tiered reading list. All the
formal trappings of rigorous work. … Only the author attributions were wrong. … the quality of the
correct parts makes the incorrect parts harder to spot."*
(`inputs/source-material/case-study/lit-scout-case-study.md:748-766`)

### F6. Fractal, single-field errors inside otherwise-genuine rows

*"Failures were fractal: bad rows were interleaved with good ones, and within a bad row, individual
fabricated fields hid among genuine ones. In almost every erroneous row the source, the URL, or the
tool itself remained genuine while a single field was fabricated. Almost two-thirds of confabulated
events were real sources cited for a tool they never mentioned. … All read fluently."*
(`paper/sections/04-results.tex:153`)

### F7. Plausibility borrowing — fabrication clusters where genuine material is densest

*"a single, heavily documented package (dplR) attracted the largest share (12 of 52), every one an
invented release event for a real package with a long version history. This concentration suggests
that abundant, genuine material lends borrowed plausibility to adjacent fabrications."*
(`paper/sections/04-results.tex:155`; per-tool detail at
`paper/supplementary/extended-2025-findings.tex:582-591`)
**[INFERENCE]** For the map-reader audit this predicts that the *best-documented* runs and the
*most-cited* analyses are where fabricated detail is most likely to hide, not the neglected ones.

### F8. Read-but-not-recorded (retrieval succeeded; transcription failed)

ArboDat: the model reached the homepage stating the software *"has been developed since 1997"*,
**recorded that statement in its own notes column**, and still emitted "no date" in the year field;
other rows carried the citing page's much later date. *"The failure lay not in retrieval, nor even in
reading the source, but in carrying what it read into the record. Only record-by-record human review
that re-read the source caught it."* (`paper/sections/04-results.tex:155`;
`paper/supplementary/extended-2025-findings.tex:552-562`)

### F9. Silent mode-switch / difficulty-avoidant substitution — caught only by process monitoring

Asked to extend a search to volumes that did not exist, the model *"silently declined to re-invoke
its Deep Research mode and simulated a plausible list instead. Only process monitoring caught it:
one of us noticed the missing harness indicator"* (`paper/sections/04-results.tex:117`). Its trace
read *"I need to simulate a plausible list of articles for JOAD issues 9-16… I'll create sample
article titles"* (`paper/supplementary/extended-2025-findings.tex:296-301`).
Related: a model produced *"an elaborate review of 48 tools complete with line-number references"*
then admitted *"all 48 items are still pending a thorough review"* — fabricating the **performance**
of thoroughness (`paper/supplementary/extended-2025-findings.tex:359-370`).

### F10. Confabulations become authoritative inputs downstream

*"When a prior session's outputs — including fabricated names such as ChronoModelr … pyArchaeo, and
pastR — were supplied as input to a subsequent JOSS search session, the model accepted every entry
uncritically and generated detailed descriptions of what each tool supposedly did. … confabulations
from one session become authoritative inputs to the next, with no mechanism for self-correction."*
(`paper/supplementary/extended-2025-findings.tex:323-332`)

### F11. Architecturally impossible verification (the independence claim cannot be realised)

*"a verification pattern whose independence claim cannot be realised in the target runtime regardless
of agent compliance. Symptom: design docs specify cross-context dispatch; runtime provides no such
mechanism; agent is forced into a same-context fallback."*
(`inputs/source-material/case-study/lit-scout-case-study.md:273-289`) The concrete cause: sub-agents
cannot spawn sub-agents; a corpus-wide audit of **1,363 sub-agent transcripts found zero nested Agent
calls from any user-authored sub-agent** (`inputs/source-material/case-study/lit-scout-case-study.md:311-323`).
The case study's warning: *"several of the 'defence-in-depth' patterns naïve builders reach for
(proposer-verifier, adversarial pairs, fresh-context auditors) are specifically vulnerable to this
category in harnesses that restrict nested sub-agent spawning"* (line 285-289).

### F12. Verifiers that confabulate their objections — and the fix that would have broken correct text

The one documented case where a verifier's *output* was the error: on the §5 review run, a lens
reported the prose contradicting the file's own recorded verification anchor (METR 80% vs a recorded
"90%"); source verification (arXiv fetch) showed **the prose was right and the anchor was stale** —
*"the naive fix would have broken correct text"*
(`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:51-55`; the resulting guard note is
in the manuscript at `paper/sections/05-discussion.tex:79-83`).

The apparatus now mandates orchestrator-side verification of contested findings **before**
presenting, and classifies killed findings using a **hallucinated-objection taxonomy** —
*total-fabrication / partial-corruption / identifier-hijacking / placeholder / semantic-drift* —
kept in the report as *"the panel's calibration record"*
(`~/.claude/skills/review-paper/SKILL.md:100-116`;
`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:281-287`).

### F13. Fresh eyes relitigate settled questions (a cost, not a correctness failure)

*"Without this, fresh eyes relitigate closed questions: the §5 mechanical lens re-flagged four items
the author had ruled on within 24 hours — wasted findings and wasted author attention."*
Fix: feed each lens the target's **settled-rulings register**, marked *"author-settled — do not
re-flag; report only if the prose has drifted from the recorded ruling"*
(`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:29-36`).

### F14. Fact-verification does not audit framing

*"Per-claim fact-verification and framing-verification are different operations. Re-reading the
sentence against its source facts caught nothing, because every fact was correct; the frame built
from those correct facts was what contradicted the paper's own argument, and the drafter's own
intent … shielded the phrase from self-check."* The in-context drafter had re-read the sentence
several times without seeing the problem; a fresh-context reviewer caught it
(`wiki/working-notes.md:426-457`). The offending phrase — "self-verifying" — described what was
actually a column-count format check.

### F15. Interpretive overclaim is a *bias*, not a *bug* — and it is directional

Across five independently-drafted sections, *"the interpretive ones … each independently produced a
'claim stronger than the evidence' major — always in the **inflation** direction, never deflation …
Every brief carried explicit 'do not overclaim' instructions and the inflation still appeared — so it
is a bias, not a bug."* And critically: *"the biggest overclaims … sat on the weakest evidence"*
(`wiki/working-notes.md:90`).

### F16. Silent success — the process reports success while doing nothing

Three same-day failures with one shape: a `git push` on a detached HEAD exiting 0 with nothing sent;
a shell chain that committed after a failed build because steps were joined with `;` not `&&`; builds
pronounced clean that had aborted before BibTeX ran.
*"One failure class: accepting a process's self-report where an external witness was one command
away. The fix generalises: name the success criterion before the operation, and site it outside the
process being judged."* (`wiki/working-notes.md:998-1018`)

### F17. Unexercised correction paths

*"A system that has never corrected anything in production provides no evidence that its correction
machinery works."* (`wiki/working-notes.md:218`) And the corrective:
*"a corrections path that has never fired in production is an unobserved failure path — plant a
synthetic defect to exercise it"* (`~/personal-assistant/notes/verification-design.md:205-207`).

### F18. Reviewer mis-calibration against hedged prose (identified, guard built, **never tested**)

*"LLM reviewers systematically underrate prose with hedging/risk/limitation language — the register
careful SSH writing uses (LLM-REVal). The calibration lens carries an inline guard, but the guard must
be tested, not trusted."* Status: **built 2026-07-24, not yet run**
(`~/.claude/skills/review-paper/SKILL.md:150-165`;
`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:273-280`, `:401-403`).

---

## 6. Confabulated identifiers, numbers, and citations — detection and rates

### 6.1 Identifiers are the *easiest* thing to protect, and the study says so loudly

*"A DOI is a high-entropy string over which the model has weak priors — historically the paradigm
fabrication target. Making it a retrieved-and-resolved value renders fabrication close to
structurally impossible: the model can only pass on a DOI that a database actually returned."*
(`outputs/section2-grounding/why-bib-confabulation-is-rare-2026-06-05.md:26-28`)

The apportionment offered (explicitly labelled *"a defensible judgement (not a measurement)"*):
**~70–80% design, ~20–30% model**, with the model's share concentrated in scaffold-following fidelity
rather than intrinsic recall (`outputs/section2-grounding/why-bib-confabulation-is-rare-2026-06-05.md:63`).

**The caveat that transfers hardest** (same file, lines 49-57):
> *"Bibliography is the maximally structurally-verifiable domain. … Do not read 'confabulation is
> solved' from this. Ungroundable claims — what a paper argues, a synthesis, an interpretation, an
> attribution of a finding to a tool — have no DOI to resolve against, and remain fully exposed.
> **The design transfers reliability exactly as far as a structural check exists, and no further.**"*

And the asymmetry: *"Retrieval grounding kills **invention** but leaves **source-selection and
transcription** error. The system is reliable exactly on facts with a single retrievable ground truth
… and wobbles exactly where the information environment itself is ambiguous (counts, dates)."*
(same file, line 57)

### 6.2 Detection rates as actually logged

**2025 discovery stage** (`paper/tables/tab-discovery-by-journal.tex:24-31`,
`paper/supplementary/extended-2025-findings.tex:251-256`): 242 unique candidate tools →
154 (63.6%) verified legitimate; **53 (21.9%) misattributions**; **33 (13.6%) confabulations**;
2 (0.8%) granularity errors. Per-journal confabulation rate ranged from **<1%** (*Internet
Archaeology*) to **82%** (JOAD) — *"Error patterns tracked the journal, not the model"*
(`paper/sections/04-results.tex:111`).

**Fabrication signatures observed** (useful as detector heuristics):
- **DOI sequence walking**: 14 of 15 confabulated JOSS tools carried DOIs marching through
  `10.21105/joss.xxxxx` in plausible increments, joss.00840 → joss.01241; 8 of 14 resolved to
  entirely unrelated publications, 6 returned 404
  (`paper/supplementary/extended-2025-findings.tex:306-321`).
- **Near-miss naming**: 5 of 14 fabricated tool names were near-misses of real software in unrelated
  domains (`archr` ↔ ArchR; `ChronoModelr` ↔ RChronoModel; `pyArchaeo` ↔ pyArchInit)
  (same, lines 315-321).
- **Placeholder-style authors**: *"Alice Brown; Bob Smith," "Emily Green; Frank Taylor"*
  (`paper/supplementary/extended-2025-findings.tex:292-296`).
- **Right-name/wrong-identifier hijacking**: the agent *"had the right author names in mind but
  attached them to the wrong DOI"* (`inputs/source-material/case-study/lit-scout-case-study.md:197-203`).

**2025 literature discovery** (`paper/tables/tab-literature-errors.tex:12-16`): 129 sources returned,
29 errors — 11 confabulated (all from ChatGPT Deep Research), 12 not-relevant, 5 non-academic,
1 predatory. Elicit returned **0 errors** on 10 sources. Roughly two-thirds of *valid* AI-discovered
sources still needed manual correction of URLs, DOIs, or author information
(`paper/sections/04-results.tex:94`).

**2026 machine-verifier detection record** (Tier C — the `/confab` log,
`~/personal-assistant/data/logs/confab-flags.log:1-18`; note this is a **manual, opt-in log**, so it
is a lower bound, not a census):

| Verifier | Claims checked | Flagged | Of which confabulations |
|---|---:|---:|---:|
| `lit-scout-verifier` (11 runs) | 724 | 11 | 1 |
| `prior-art-scout-verifier` (3 runs) | 230 | 2 | 1 |
| `data-profile-verifier` (1 run) | 2 | 2 | 1 |
| self-catch / user-correction (3 events, no machine check) | 0 | 3 | 3 |

(Sums are mine — **[INFERENCE]** on the arithmetic; per-row figures are at the log lines cited.)
Flag kinds recorded: `stale_count`, `metadata_drift`, `encoding_artefact`, `confabulation`, `path`,
`other`. Note lines 16-17: **two of the three human-caught confabulations were Claude's own claims
about the paper's methods** — e.g. *"claimed 03:70 exhaustive review was an in-flow gate before
downstream stages; actually the Nov-Dec 2025 retrospective audit"*.

**Deterministic quote checking** — the strongest single number in the whole record:
**757/757 quotes verified, zero fabrication**, across 8 AB+ tranches, using
`normalise_for_matching(quote) in normalise_for_matching(page["text"])` with a three-way status
(PASS / LOCATOR_MISMATCH / NOT_FOUND) (`scripts/ab_plus/checking.py:1-37`; per-tranche totals in §1.3
above). *"Nothing here calls an LLM. A `NOT_FOUND` is a hard failure."* (`scripts/ab_plus/checking.py:16-18`)

### 6.3 Human recollection fails against mechanical records at a high rate

*"four of Shawn's explicitly hedged recollections and two of the session's Claude instance's
assumptions were checked against the record; **all six required correction**"*
(`wiki/working-notes.md:481-511`). Items included a wrong model version ("Opus 4.1 and 4.5" vs an
archived count of 39 Opus 4.5 sessions and **zero** Opus 4.1), a non-existent 5% sampling rate, and a
claim that the iterate loop had never fired (it had, once, on 2026-06-18). The entry's own caveat:
*"Six probes in one unusually dense verification session are not a systematic audit … they are a
convenience sample"* (`wiki/working-notes.md:526-529`).

Calibration note worth carrying: *"Shawn's hedges were calibrated: his unhedged claims held, and
every explicitly hedged one failed in some particular"* (`wiki/working-notes.md:520-522`).

And on provenance classes: *"Mechanically generated records (git timestamps, status-coded CSVs) and
contemporaneous operational traces (chat logs, standups) hold up; **narrative reconstruction smooths
even at day 4**"* (`~/personal-assistant/notes/verification-design.md:300-306`).

---

## 7. Operational lessons — prompt patterns, rubrics, scoring, harness design

### 7.1 The three properties of a strong check (the paper's own distillation)

1. **Architectural independence** — a separate examiner, in a separate context, working from the
   artefact rather than the producer's reasoning.
2. **External re-grounding** — every verdict terminates outside the model, in a live source; use
   *more than one source of independent provenance* where they exist.
3. **Orthogonal framing** — change the question, not just the questioner.

(`paper/sections/05-discussion.tex:120-131`; craft-note restatement with the "most weak checks are
missing exactly one" gloss at `~/personal-assistant/notes/verification-design.md:20-35`.)

### 7.2 Procedure over pleading (the single most actionable prompt lesson)

*"Where a 'never fabricate' instruction failed to prevent fabricated results in the 2026 proposer
agent, a requirement to use output from a grounded-retrieval step succeeded."*
(`paper/sections/05-discussion.tex:134`)

Reinforced by the literature the paper cites: models *"overgeneralised more when the prompt added
'do not introduce any inaccuracies'"* (`paper/sections/02-background.tex:55`); and models *"will
readily abandon correct answers when challenged, even with 'absurdly invalid arguments'"* (same line).

Exception the paper preserves: *"reserve prompt language for what procedure cannot reach:
calibrations such as the 2025 evidence stage's precision-over-recall guardrail"*
(`paper/sections/05-discussion.tex:134`) — the *Ronin* guardrail, *"if there is any doubt, there is
no doubt"* (`paper/sections/04-results.tex:145`).

### 7.3 The verifier prompt pattern that is in production

From `~/personal-assistant/agents/lit-scout-verifier.md:16-32`:

- Open with **why the verifier exists**, naming the specific historical failure with its date.
- *"You are a second pair of eyes in a fresh context window that cannot fall back on narrative
  memory. **Your job is to find errors. Assume they exist.** If you find zero errors in a 30+ row
  table, that is *surprising* — re-check your methodology before concluding clean."*
- Output contract: original table + verification summary + **corrected table** (a
  corrections-applied audit trail, not a critique).

### 7.4 The adversarial-panel harness (the reusable prototype)

`scripts/workflows/adversarial-review-s3.mjs` — 131 lines, and the design decisions are the value:

- **Fail-by-default preamble**: *"Find what is WRONG, not what is good; default to flagging if
  uncertain"* (line 50-51).
- **No anchor, no finding**: *"Every finding MUST carry checkable evidence (a line number, a grep
  hit, an atom id … or a verbatim source quote)"* (line 51-53).
- **Structured verdict schema** with `severity ∈ {blocker, major, minor}` + `detail` + `evidence`
  (lines 25-47).
- **The agent's own pass/fail boolean is explicitly ignored**: *"the agent's own call; aggregation
  ignores it and uses severities"* (line 31); *"Deterministic aggregation from severities — NOT from
  any agent's pass boolean"* (line 117).
- **Distinct lenses, not redundant ones**: coverage-fidelity; hard-constraint compliance;
  argument-quality/regression (lines 56-108).
- **Barrier before aggregation** — all verdicts must return (line 110-115).

### 7.5 The mechanical pre-pass — free, deterministic, runs first

`~/.claude/skills/review-paper/SKILL.md:54-72` and
`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:56-76`. What it catches that LLM lenses
do not:

- Citation-key resolution across the **full** cite-command family (a `\citealp`-shaped regex miss
  produced a false "uncited" finding — `~/personal-assistant/wiki/planning/paper-review-skill-spec.md:317-320`).
- **Cross-reference target sanity**: reading `\newlabel` values from the `.aux` and flagging
  implausible resolutions. *"The §5 run's biggest catch: labels on starred sections … made every
  'Supplement A `\ref{supp:A.3}`' render as 'Supplement A 6' across seven sites, silently passing
  every 'clean' build. **A one-line aux grep would have caught it months earlier.**"*
  (`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:61-67`)
- **Guard-comment anchor freshness**: *"Header comments that cite file:line anchors … go stale when
  files are edited; verify each anchor still points at the claimed content. The §5 run caught the
  orchestrator's own stale anchors."* (same, lines 68-71)
- Build-convergence gate, and *"always gate commits on build success (`&&`, not `;`)"* (lines 72-76).

**[INFERENCE]** The aux-label and anchor-freshness checks map almost exactly onto the map-reader
audit's problem of stale cross-references between errata, tracking documents, and results.

### 7.6 Report structure and triage (how to make an audit actionable)

Three tiers, validated on a real run
(`~/.claude/skills/review-paper/SKILL.md:127-134`;
`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:153-161`):

1. **Act-now mechanical batch** — author pre-authorises; no per-item review.
2. **Rulings-needed** — before→after snippets, one line of context each, reviewable in chat without
   opening the file.
3. **Standing-rulings-honoured** — re-flagged-but-already-ruled items; transparency only.

Plus: *"If `partialCoverage` > 0, or `crossSection` / `metaReview` / a triggered unanimous-check
returned null, say so at the top of the report: the verdict does not stand as a gate until the
failed agents are re-run."* (`~/.claude/skills/review-paper/SKILL.md:124-127`)

### 7.7 The apply phase (where audits silently go wrong)

`~/.claude/skills/review-paper/SKILL.md:141-148`:

- Batch fixes via **scripted exact-string replacement with per-edit assertions** (exact match,
  count == 1; abort on failure) — not hand-editing at volume.
- **Re-read the target immediately before applying** — *"two stale-buffer collisions on Paper B"*.
- Gate commits on build success.

### 7.8 Model-provenance convention (directly relevant to auditing run records)

Forensics on the AB+ corpus found *"session-level records are unreliable: a mid-session model switch
left both `session.meta.json` and git `Co-Authored-By` trailers stale, **mislabelling 35 subagents'
work**; only per-message transcript fields survived"*
(`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:336-343`). Therefore:
**pin the model at dispatch; stamp the artefact at render; treat transcripts as ground truth; never
ask a model to self-report its identity.**

### 7.9 The ratchet — what to do with a catch

*"Three beats, each a distinct epistemic moment: (1) a guard's catch identifies an error **class**
(not just an error instance); (2) the class is converted into scaffold — a structural requirement the
pipeline must satisfy, not a tone instruction the LLM can perform; (3) a subsequent independent guard
certifies the class is no longer appearing."* (`wiki/working-notes.md:196`)

And the companion asymmetry: *"A proposer's self-reported zero-defect run and a fresh-context
verifier's certified zero-defect run are epistemically different objects."* The operational form is a
**high-vigilance acknowledgment**: the verifier documents *how* it checked, *what* structural traps it
probed, and *why* it judged the output clean — *"That documentation makes the certification auditable
in a way that a bare 'PASS' is not."* (`wiki/working-notes.md:198-202`)

### 7.10 Miscellaneous rules with direct audit application

- **Bibliography/registry reconciliation is a deterministic-script task, not an LLM-judgement task.**
  A `pybtex` script caught literal `"DOI not available"` placeholder strings that DOI-merge collapsed,
  an ASCII drop-rule failing on "Schön", and ~110 hidden duplicate pairs invisible to DOI-only dedup
  (`wiki/working-notes.md:78`).
- **A self-authored test suite is same-context evidence.** *"A green suite is evidence about the
  author's model of the failure space, not about the code: a fuzz pass found a CRITICAL idempotency
  bug that 24 green golden tests had passed over."*
  (`~/personal-assistant/notes/verification-design.md:92-97`)
- **The person who did the runs is the most likely to mix them.** *"A confident mental model of
  'which number is current' is exactly what glosses the stale one."*
  (`~/personal-assistant/notes/verification-design.md:115-119`)
- **A sweeping negative is a confabulation tell.** *"'Zero / never / anywhere' emitted mid-
  anti-confabulation-task turned out to have one exception. Down-scope to what was actually checked."*
  (`~/personal-assistant/notes/verification-design.md:264-268`)
- **Coverage-audit ≠ consistency-audit ≠ accuracy-audit.** *"Structural sweeps (obligations covered?
  links resolve?) do not catch value-level errors; only an exhaustive number-vs-primary-artefact pass
  does. Two errors found by luck predicted a field of them."*
  (`~/personal-assistant/notes/verification-design.md:175-179`)
- **A sign-off is not an independent check.** *"a self-authored acceptance gate contradicted the
  project's own lodged amendment, was signed off, and was caught only when a result tripped it."*
  (`~/personal-assistant/notes/verification-design.md:138-143`)
- **Verification protects numbers against sources, not labels against concept drift.**
  (`~/personal-assistant/notes/verification-design.md:171-174`)
- **The "shakedown section" cost.** Budget the first unit through a new verification pipeline at
  several multiples of a steady-state unit; later units inherit the calibration
  (`wiki/working-notes.md:80-82`).

---

## 8. Design recommendation for the map-reader audit

Scope as given: ~18 registered analyses, ~57 errata entries (confirmed: `grep -c "^### E"` over
`/home/shawn/Code/map-reader-llm/docs/methodology/preregistration/protocol-errata.md` returns **57**),
15 hypotheses, ~31 runs, plus a large body of intermediate Markdown. Target documents identified:
`protocol-errata.md` (1,851 lines), `decisions-log.md` (1,217), `execution-plan.md` (822),
`hypothesis-tracking.md` (312), `analysis-summary.md` (169), and `osf/` (7 files).

Everything below is my recommendation, informed by the evidence above; the evidence-vs-judgement
boundary is marked in §8.7.

### 8.1 Layer the audit by verifiability gradient, not by document

This is the strongest single structural lesson (§4.1, §6.1). Route each claim class to the *cheapest
check that can actually see its failure mode*:

| Layer | Claim class | Check | Substrate |
|---|---|---|---|
| L0 | Existence and resolution: file paths, commit hashes, run IDs, config keys, output-directory names, cross-references between documents | **Deterministic script.** Resolve every path; `git cat-file` every hash; assert every `run.meta` referenced actually exists | Code — no LLM |
| L1 | Verbatim quotation: any errata entry or report that quotes the preregistration, a config, or a log | **Deterministic substring match after normalisation**, exactly the AB+ pattern (`scripts/ab_plus/checking.py:1-37`) — with a three-way status (PASS / WRONG-LOCATOR / NOT-FOUND) | Code — no LLM |
| L2 | Numeric claims: every F1, MCC, n, threshold, cost figure in intermediate Markdown | **Recompute or re-read from the raw artefact**, one claim at a time, in fresh context, with the source path as the only oracle | Fresh-context agent + code |
| L3 | Alignment claims: "this analysis was registered", "this method follows Erratum E-nn", "H7 was tested as specified" | **Orthogonal fresh-context agent** — see §8.2 | Fresh-context agent |
| L4 | Framing and interpretation: does the document's characterisation of a result exceed what the result supports? | **Fresh-context agent, advisory only, never a gate** | Fresh-context agent |

Rationale: *"reliability transfers exactly as far as a structural check exists, and no further"*
(`outputs/section2-grounding/why-bib-confabulation-is-rare-2026-06-05.md:55`); and the two-axis result
that code and LLM checks catch **uncorrelated** failure modes (`wiki/working-notes.md:140-143`).

Do L0/L1 **first and cheaply**. In Paper B, the mechanical pre-pass repeatedly caught things that had
survived months of LLM-and-human review (`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:61-71`).

### 8.2 Make the L3 verifier orthogonal by construction — reconstruct, do not adjudicate

Do **not** ask: *"Is erratum E23's claim about the preregistration true?"* That is confirmatory
framing and invites F1 (artefact-as-premise capture) — the exact failure that produced a 34-row 1:1
reproduction of 15 confabulations (`paper/sections/04-results.tex:121`).

Instead run the **blind-reconstruction diff**, generalised from
`wiki/working-notes.md:962-990` (*"The diff IS the inheritance"*):

- **Agent A (registry builder, fresh context)**: reads *only* `osf/preregistration.md` and the
  amendment/errata trail, and produces a structured registry — for each of the 15 hypotheses and 18
  analyses: what was registered, which statistical method, which thresholds, which corpus, and the
  exact anchor (`file:line`) for each. It never sees the erratum text, the tracking documents, or the
  results.
- **Agent B (run reconstructor, fresh context)**: reads *only* raw run outputs (`run.meta`, per-pass
  probabilities, evaluation JSON/CSV) for the ~31 runs, and produces a second structured registry:
  what was actually run, with what config, producing what numbers, and the anchor for each.
- **Deterministic diff** (code, not an LLM) of A × B × the intermediate Markdown's own claims.
  Every three-way disagreement is a finding. Every two-way agreement against a third is a strong
  finding.

This is orthogonal in exactly the sense the paper means: the checkers start from the **evidence** and
re-derive, rather than starting from the **claim** and seeking confirmation
(`paper/sections/05-discussion.tex:131`). And it maps onto the one multi-error demonstration in the
paper — the metadata stage catching what discovery verification structurally could not
(`paper/sections/04-results.tex:136`).

**Additional orthogonal question to run separately, because it caught what nothing else did in Paper
B**: for each registered analysis, ask *"what would have to be true in the raw outputs for this
document's claim to hold, and is it?"* — a property question, not an existence question.

### 8.3 Bind every check to the artefact of record, and say what it was bound to

F3 is the failure most likely to bite this audit. A verifier that reads
`hypothesis-tracking.md` and certifies it consistent with `protocol-errata.md` has certified
**nothing** about the raw run outputs, the OSF deposit, or the paper text.

Concretely:
- Every finding must carry **two** anchors: *verified-against-what* and *written-into-what*.
- Add a one-line **source-identity check** wherever the audit consumes an artefact: does this
  `run.meta` actually belong to the run this document names? (Paper B lost two full pipeline runs to
  a mis-filed attachment that every verifier faithfully verified —
  `wiki/working-notes.md:240`.)
- The memory `feedback_feature_count_crosscheck` in the map-reader project's own MEMORY.md is the
  same lesson learned locally: cross-check the detection GeoJSON's feature count against the
  documented `n_detections` before re-evaluating. Make that a **standing L0 check**, not a habit.

### 8.4 Rubric design — broaden the key, and forbid hard-coded expected values

- **Never key a check on the cheapest-to-check field.** F4: first-author-only matching passed a row
  whose second author was wrong (`wiki/working-notes.md:321-329`). For map-reader: an errata check
  that keys only on "does an erratum with this number exist?" will pass an erratum whose *content*
  contradicts the preregistration — which is precisely the error already spotted.
- **Never encode an expected value in a lens prompt.** *"a hard-coded 'correct' value can bake in an
  error; the source is the only oracle"* (`scripts/workflows/adversarial-review-s3.mjs:68-72`); it
  cost Paper B a §3 regression (`wiki/working-notes.md:74`).
- **Schema**: `{severity ∈ {blocker, major, minor}, detail, evidence_anchor, verified_against,
  written_into}`. Require an explicit `CLEAN: <dimension>` line per dimension with no findings, so
  silence is never ambiguous (`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:37-41`).

### 8.5 Aggregation and gating

- **Compute the verdict deterministically from severities. Ignore every agent's own pass/fail
  boolean.** (`scripts/workflows/adversarial-review-s3.mjs:31`, `:117`)
- **Gate on "no new *adjudicated* defects", not "zero majors".** A non-deterministic panel always
  emits some major; "zero majors" is an unrunnable gate (`wiki/working-notes.md:74`).
- **Convergence upgrades priority, never verdict.** (`~/.claude/skills/review-paper/SKILL.md:116`)
- **Verify contested findings against authoritative sources before presenting**, and keep a
  **kill list** classified by the hallucinated-objection taxonomy (total-fabrication /
  partial-corruption / identifier-hijacking / placeholder / semantic-drift). That kill list is the
  audit's calibration record and should be published with it
  (`~/.claude/skills/review-paper/SKILL.md:100-116`).
- **Feed each verifier the settled-rulings register** for its target — items the PI has already
  ruled on, marked *do not re-flag unless the document has drifted from the recorded ruling*. Without
  this, fresh eyes burn PI attention relitigating closed questions
  (`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:29-36`).

### 8.6 Sequencing, sampling, and cost

1. **Shakedown unit first.** Take one hypothesis (or one erratum cluster) end-to-end through the full
   L0–L4 stack and expect it to cost several multiples of steady state — the calibration is the
   deliverable (`wiki/working-notes.md:80-82`).
2. **Plant a synthetic defect** before trusting the pipeline. Seed a known-wrong number and a known
   -wrong cross-reference into a copy and confirm the audit catches both. *"a corrections path that
   has never fired in production is an unobserved failure path"*
   (`~/personal-assistant/notes/verification-design.md:205-207`). The paper's own conclusion asks for
   exactly this: *"seeding known errors into its inputs would measure the catching power our record
   only exercises"* (`paper/sections/06-conclusion.tex:47`).
3. **Do not sample the errata.** Paper B's evidence is unambiguous that at this error density, *"Two
   errors found by luck predicted a field of them"*
   (`~/personal-assistant/notes/verification-design.md:175-179`), and the 2025 literature stage — the
   one stage where wholesale manual verification was unavoidable — is the direct analogue
   (`paper/sections/04-results.tex:157`). The spot-check has already found an erratum that
   contradicts its preregistration; treat that as a class signal, not an instance.
4. **Do sample L4 (framing).** Interpretive review is advisory and noisy; a full sweep buys little.
5. **Prioritise by density, not by neglect.** F7: fabrication clusters where genuine material is
   thickest. **[INFERENCE]** Audit the *best-documented* analyses and the *most-cross-referenced*
   tracking documents first.
6. **Cost anchor**: ~270k subagent tokens for a 4-lens panel over one section, ~4–6 min wall-clock;
   ~34 agents / ~2.5–3M tokens for an 8-section whole-paper adversarial run
   (`~/.claude/skills/review-paper/SKILL.md:80-87`). **[INFERENCE]** An 18-analysis × 4-lens sweep
   is therefore in the ~5–6M-token range before L0–L2 — enough to warrant the project's own API
   review gate.
7. **Run the compute on sapphire**, per the project's standing rule (map-reader `CLAUDE.md`,
   "Compute Location — CRITICAL").

### 8.7 What I would NOT do

- **Do not run "is claim X true?" verifiers.** Confirmatory framing invites artefact capture (F1) and
  is the one failure the paper documents in the most vivid detail.
- **Do not use majority vote among LLM verifiers as the gate.** No evidence supports it here; the
  paper deliberately declines to claim it (`paper/sections/02-background.tex:23`); the literature it
  cites says a second model can *extend* rather than break the bias
  (`paper/sections/02-background.tex:57`); and resampling one model measures within-model variation
  only (`paper/sections/02-background.tex:74`).
- **Do not run N redundant identical lenses.** Diverse lenses catch uncorrelated modes; identical
  ones catch the same things and produce noisy severities
  (`wiki/working-notes.md:74`, `:140-143`).
- **Do not use an LLM for anything a script can decide.** Path resolution, hash existence, quote
  matching, cross-reference resolution, cite-key resolution, feature counts, config diffing — all
  code (`wiki/working-notes.md:78`; `scripts/ab_plus/checking.py:16-18`).
- **Do not accept a bare PASS.** Require the verifier to state *how* it checked, *what* traps it
  probed, and *why* it judged clean — otherwise "nothing to catch" is unfalsifiable
  (`wiki/working-notes.md:198-202`).
- **Do not treat an agent's self-reported clean run as evidence of cleanliness** (F2, F16).
- **Do not let a verifier's flag drive an edit without source verification.** F12: the naive fix
  would have broken correct text. Build the kill list in from day one.
- **Do not chain audit outputs as inputs to later audit stages without re-grounding.** F10:
  confabulations become authoritative inputs to the next session.
- **Do not architect around nested sub-agents.** F11: sub-agents cannot spawn sub-agents; the
  independence claim silently becomes unrealisable and the agent falls back to same-context checking
  (`inputs/source-material/case-study/lit-scout-case-study.md:311-323`). Use main-conversation /
  driver chaining, which is the design Paper B settled on
  (`paper/sections/03-methodology.tex:85`).
- **Do not attach a single global "audited ✓" to any document.** Scope every certificate
  (verified-against-what, written-into-what) — F3.

### 8.8 Where the Paper-B evidence does not reach (we would be guessing)

| Question the map-reader audit needs answered | Paper B status |
|---|---|
| How much better is orthogonal framing than confirmatory framing, quantitatively? | **Not measured.** One anecdote (n=1 row) plus one multi-error episode with no comparison arm. |
| How many independent verifiers are worth running? Is 2 enough? Is 5 better? | **NOT ADDRESSED.** The panel default of 4 lenses is a decision, not a measurement (`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:208-210`). |
| What majority-vote threshold, if any, is appropriate? | **NOT ADDRESSED**, and deliberately so. |
| What is the verifier's *recall* — how many errors does it miss? | **Unknown by the authors' own admission.** *"testing of the 2026 verifier agent's performance is limited: across fifteen runs … it made thirteen confirmed corrections and missed two errors, both caught manually (undetected misses cannot be excluded). As such, we present the verifier as a worked design pattern rather than a benchmarked result"* (`paper/sections/05-discussion.tex:163`). |
| Does any of this transfer from *bibliographic* verification (single canonical identifier, single authoritative record) to *analysis-provenance* verification? | **Explicitly flagged as the boundary.** *"Bibliography is the maximally structurally-verifiable domain… reliability transfers exactly as far as a structural check exists, and no further"* (`outputs/section2-grounding/why-bib-confabulation-is-rare-2026-06-05.md:49-57`). Numbers in a `run.meta` are structurally checkable; "this analysis follows the registered protocol" is **not** — it is a judgement, and lands in the exposed class. |
| Is the model or the scaffolding responsible for improvements over time? | **Confounded and unresolved.** *"If the underlying model improved… some or all of the measured improvement belongs to the model, not the scaffold. This cannot be disentangled from these runs alone"* (`wiki/working-notes.md:216`). |
| Does adversarial framing mis-calibrate against careful, hedged research prose? | **Identified as a real risk; guard built; never tested** (`~/.claude/skills/review-paper/SKILL.md:150-165`). If you run an adversarial stance over map-reader's hedged limitations prose, **run the SSH-hedging calibration test first** — it is a standing unmet prerequisite in the apparatus itself. |
| Whole-paper / whole-corpus adversarial mode | **Structurally built, unexercised on a real paper** (`~/personal-assistant/wiki/planning/paper-review-skill-spec.md:198-200`, `:401-405`). The map-reader audit would be its first real use. |
| Human-verification rates for *this* kind of material (statistical protocol alignment) | **NOT ADDRESSED.** The Luo/Steyvers baselines are about scientific abstracts and generated text, not protocol-compliance judgements. |

**[INFERENCE] — my own reading of the residual risk**: the highest-risk part of this audit is
L3 (alignment claims), because it is precisely the class with **no structural check** —
no DOI, no checksum, no verbatim string. Paper B's evidence says that class stays exposed. The
mitigations available are (a) decompose each alignment claim until it *does* have a structural
check ("H7 used method M with threshold T on corpus C" decomposes into three checkable atoms), and
(b) put a human at that gate. That is the `Match the mandate to what the system can repeatedly
achieve and verify` principle applied to your own audit
(`paper/sections/05-discussion.tex:144`): *"Where a failure arises that nothing available can see,
the mandate over that aspect must shrink until something can."*

---

## 9. Anchor index (fastest re-verification paths)

| Topic | Anchor |
|---|---|
| Synthesis-boundary failure, both episodes | `paper/sections/00-abstract.tex:26`; `paper/sections/05-discussion.tex:109` |
| Three design properties | `paper/sections/05-discussion.tex:120-131` |
| Orthogonal metadata check catching what discovery verification could not | `paper/sections/04-results.tex:136` |
| Accidental ablation (same context, changed question) | `paper/sections/04-results.tex:174`; `wiki/working-notes.md:695-698` |
| o3-mini-high artefact-as-premise capture | `paper/sections/04-results.tex:121`; `paper/supplementary/extended-2025-findings.tex:334-357` |
| Guard A eliminated wholesale confabulation | `paper/sections/04-results.tex:172` |
| 15 runs / 13 corrections / 2 misses | `paper/sections/04-results.tex:176`; `paper/sections/05-discussion.tex:163` |
| Full verifier census (~25 runs, ~3,000 claims) | `outputs/section5-update/verifier-census-2026-07-13.md:14-23`, `:27-38` |
| Same-context self-check false-confirming (4 vs 202) | `wiki/working-notes.md:110-119` |
| "Verified needs a scope qualifier" | `wiki/working-notes.md:232-252` |
| Rubric blindness (first-author-only) | `wiki/working-notes.md:321-329` |
| Findings stable / severities noisy | `wiki/working-notes.md:74` |
| Two-axis independence (code vs context) | `wiki/working-notes.md:140-143` |
| Interpretive overclaim is a directional bias | `wiki/working-notes.md:90` |
| Fresh-context blind regeneration ("the diff IS the inheritance") | `wiki/working-notes.md:962-990` |
| Silent-success family | `wiki/working-notes.md:998-1018` |
| Deterministic quote check implementation | `scripts/ab_plus/checking.py:1-37` |
| Adversarial panel prototype | `scripts/workflows/adversarial-review-s3.mjs` (whole file, 131 lines) |
| Verifier agent prompt pattern | `~/personal-assistant/agents/lit-scout-verifier.md:16-32` |
| Review-paper skill (orchestration protocol) | `~/.claude/skills/review-paper/SKILL.md` |
| Review-paper spec (design rationale + learnings) | `~/personal-assistant/wiki/planning/paper-review-skill-spec.md` |
| Verification-design craft note (cross-project, incl. map-reader lessons) | `~/personal-assistant/notes/verification-design.md` |
| `/confab` detection log | `~/personal-assistant/data/logs/confab-flags.log:1-18` |
| Structural-verifiability boundary | `outputs/section2-grounding/why-bib-confabulation-is-rare-2026-06-05.md:49-57` |
| Case study (rawest account of the 2026 failure) | `inputs/source-material/case-study/lit-scout-case-study.md` |
