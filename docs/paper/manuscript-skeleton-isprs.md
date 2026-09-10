# Manuscript skeleton — mapping our material onto the ISPRS shape

> **Last revised**: 2026-08-25 (original publication; STRAWMAN for the
> PI's outline-first review — five decisions flagged OPEN). See
> [§ Changelog](#changelog) for revision history.

**Why this exists**: the venue's observed skeleton
(`journal-requirements-isprs.md` § 2) differs from our internal
structure — the methods-draft's M.x/M.2–M.12 sections and
results-draft's R0–R9 were organised around the project outline, not a
journal tree. This document maps existing material onto the ISPRS
shape within the locked ~8,500-word budget. Nothing is discarded:
everything not in the main text routes to a numbered supplement or the
companion paper.

## The proposed tree (venue-modal, with our dataset section)

### 1. Introduction (~1,100 words)

The locked framing: one symbol family among dozens on a dense
historical map; find all members, nothing else. The general problem
(small-object detection on degraded scanned cartography at quantified
cost), the archaeological instance stated not assumed, the
contributions list (trade-space + measured transfer protocol +
efficiency frontier + GT-free selection + full transparency
apparatus). Mostly new prose; seeds from the outline's framing notes.

### 2. Related work (~900 words)

Sources: the three verified lit-scout reports, Seed 8 (the
area→point difficulty ladder, O'Hara/GMFS with the corrected
figures and metric-hygiene inoculation), Wu 2023 as the venue
precedent, the VLM-EO cluster, historical-map extraction lineage.

### 3. Study area, materials, and reference data (~800 words)

The venue's dataset-section convention (top-level in 5/16 surveyed
papers). Sources: methods-draft **M.9** (study area and materials),
the corpus/tiling description, curator GT + canonical adjudicated
773-mound GT with the asymmetric-epistemics summary (Obs 361, one
paragraph; detail → Supplement S4).

### 4. Methods (~2,000 words)

Sources: **M.10** (pipeline) compressed; **M.2–M.7** fragments
(instruments, pairings, corrected-F1 estimator); the geometry and
verifier configurations; aggregation (greedy consensus primary);
**the AI-as-instrument reporting the venue policy mandates** (models,
versions, developer; the assistant's code role "declared in detail")
— drawn from M.12's division-of-responsibility passage, operationalised
not reflexive; study design + preregistration apparatus as a short
§ 4.1 (M.x compressed to ~150 words, full apparatus → Supplement S3).
**M.11's execution protocol and phase table → Supplement S3** almost
entirely.

### 5. Results (~2,200 words)

Sources: results-draft **R0–R9**, compressed around three exhibits:
(i) the GS verified board + the stride/geometry programme (the
plateau, iso-stride verdict, interior optimum); (ii) the Pareto
frontier (the ~19× efficiency result, N-ladder); (iii) the 55-map
portfolio transfer (running now; primary carried points vs oracle,
bets P1–P8 assessed). Everything else (consensus-only boards, per-cell
sweeps, historical eras) → Supplement S2 with the register as the
machine-readable backbone.

### 6. Discussion (~1,300 words)

**The hard cut — 12 seeds into ~5 moves** (proposal, PI to rule):

- IN: **Seed 12 + rider** (Pareto/efficiency frontier; the P/R dial;
  interior-optima shape; MCC thread; the simulated-workflow protocol
  with its two sharpenings) — the spine.
- IN: **Seeds 1+2 merged** (representativeness before size;
  deploy-and-evaluate economics) — one move.
- IN: **Seed 3** (GT-free selection as a falsifiable proposal).
- PARTIAL: **Seed 8** — the positioning half may migrate up into
  Related work; keep one Discussion clause.
- OUT (→ companion paper): Seeds 7 (micro-registration/registration
  recipe), the collaboration reflexives; OUT (→ supplement or cut):
  Seeds 4, 5 (tile-MCC extraction instrument — one clause survives in
  the MCC thread), 9, 10, 11.

### 7. Conclusions (~300 words)

### Back matter (~200 words)

Declaration of generative AI (manuscript-preparation template, named
tools/models); CRediT; data AND code availability (OSF, repo, Zenodo,
transcript archive — the differentiator); competing interests;
funding; acknowledgements.

### Supplements manifest

- **S1** Extended methods: configurations, prompts, verifier detail,
  execution protocol (M.11), runner/governor.
- **S2** Full results: trade-space tables, sweeps, boards, all eras;
  register-derived.
- **S3** Preregistration and transparency apparatus: M.x in full,
  errata log, analyses register description, hypothesis-outcome
  table, the phase table.
- **S4** Reference-data construction and epistemics (Obs 361 in
  full; canonical-GT adjudication).
- **S5** Human–AI collaboration summary + transcript/repo access
  statement (pointer to the companion paper).

## What changed vs our internal structure (the deltas the PI noticed)

1. **M-numbering redistributes, it doesn't rename**: M.9→§3,
   M.10→§4, M.11→S3, M.x→§4.1-brief+S3, M.12→back matter+S5. The
   methods-draft remains the prose source; this tree is its
   destination map.
2. **The dataset section is top-level** (venue convention) — it was
   inside Methods in our outline.
3. **Single Results section** (no separate Experiments): we follow
   the domain-science spine variant, which the venue accepts (3/16),
   rather than the CS Experiments form — our results are boards and
   measured claims, not ablation suites. [OPEN — see D-3.]
4. **The Discussion cut is the big new decision** — 12 seeds cannot
   fit 1,300 words; the proposal above is a selection, and rejected
   seeds route to the companion paper rather than vanishing.

## Open decisions (PI)

- **D-1**: the § 6 seed slate as proposed?
  **DEFERRED 2026-09-10 (PI)**: briefing banked below (§ D-1 briefing); the PI will work through the literature review and the Results with the assistant first, and rule on the Discussion once the evidence → analysis → results pipeline is closed.
- **D-2**: Related work as its own § 2 (proposed) vs folded into the
  Introduction (frees ~400 words for Results)?
- **D-3**: single Results (proposed) vs Experiments+Results split?
- **D-4**: the three main-text exhibits as proposed (GS board+geometry,
  Pareto, transfer)?
- **D-5**: the companion-paper boundary — is Seed 7
  (micro-registration) promised in this paper's Discussion as future
  work, or silently reserved?

## D-1 briefing (2026-09-10, banked for the deferred ruling)

**What is being decided.** The internal outline
(`docs/paper/discussion-outline.md`, DD1–DD13 settled in Session 139)
has eleven subsections built from twelve seeds
(`docs/paper/discussion-seeds.md`). The venue gives the Discussion about
1,300 words, so § 6 above proposes a hard cut to about five moves. D-1
asks whether that cut is the Discussion's content for this paper; it
decides content and emphasis, not prose, and DD1–DD13 stay settled for
whatever survives.

**The seeds, one line each.** 1 — a calibration instrument's resolution
depends on representativeness before size. 2 — deploy-and-evaluate is
cheaper than the reference data it replaces. 3 — GT-free selection is a
falsifiable proposal, not a validated method. 4 — the tile-MCC
counter-board replicates across instruments. 5 — tile-MCC as the basis
for semi-automated extraction; temperature and pool-size cost
equivalences. 6 — the plateau rule: what transfers from a small
calibration corpus and what does not. 7 — the preregistration
retrospective and the micro-registration alternative. 8 — the bitter
lesson arrives at map-symbol extraction. 9 — what a high-performing
extraction run looks like. 10 — cost and expertise: the generalist route
is accessible. 11 — crowdsourcing and participatory mapping as comparison
and mutual QA. 12 — the efficiency breakthrough from the stride
programme, with the simulated-workflow rider.

**The proposed slate** (about 250 words per move): spine = Seed 12 plus
rider (IN); Seeds 1 + 2 merged (IN); Seed 3 (IN); Seed 8 partial (most
migrates to Related work, one clause stays); Seed 7 and the
collaboration reflexives OUT to the companion paper; Seeds 4, 5 (one
clause survives in the MCC thread), 9, 10, 11 OUT to supplement or cut.

**What changed after the slate was written (2026-08-25).**

1. Seed 12's first move ("no new F1 high, only a cheaper frontier") is
   now partly untrue: the Gemini 3.7 and 3.8 campaigns produced a new
   high on the GS instrument (0.923–0.931), and the GS Era-2 verified
   board (Obs 463, 465) shows it as a tier move against the whole Era-2
   incumbency, robust to the symmetry fix. The spine's claim needs
   re-stating: the architecture ceiling held within a model generation
   and moved with the generation, at the same recipe.
2. The transfer story is fuller: the 55-map 3.7 text run, the r2
   reference, and § R7.2–R7.3 now exist; Seed 12's cost frontier has a
   deployment-scale column it did not have.
3. Seed 6, the plateau rule, is cut although the internal outline calls
   it the central methodological lesson; the 3.7 results are also a
   test of what transferred from the calibration corpus.

**Options.** (a) Accept as proposed; the family step lives in Results
only and Seed 12 is corrected at prose time. (b) Accept with one
amendment: the Seed 12 spine gains the family-step clause (frontier
moved in cost within the generation and in F1 across generations at the
same recipe) — the assistant's recommendation, since it keeps the
five-move budget and fixes the one claim now false. (c) Revise the cut:
for example restore Seed 6 as its own move by folding Seed 3 into the
Seeds 1 + 2 move, so the Discussion carries the plateau rule the 3.7
transfer test speaks to; costs a re-cut and a fresh word budget.

**Sequencing ruling (PI, 2026-09-10).** Work through the literature
review and the Results together first, so the material is in mind
before deciding what is important; ensure the evidence → analysis →
results pipeline is completely closed; then turn to writing and rule on
D-1 to D-5 and the D.9 naming question.

## Changelog

### 2026-09-10 — D-1 briefing banked; D-1 to D-5 deferred behind the pipeline close-out (PI, Session 152)

The D-1 options were laid out with what changed since the slate (the 3.7/3.8 new high, the fuller transfer story, Seed 6's cut) and banked as § D-1 briefing; the PI deferred the Discussion decisions until the literature review and the Results have been worked through together and the evidence → analysis → results pipeline is closed.

### 2026-09-08 — Exhibit (iii)'s home settled (PI ruling, Session 151)

The 55-map portfolio transfer and the Gemini 3.7 campaign (not yet run
when this skeleton was written) are reported inside § R7 of the Results
draft as blocks R7.2 and R7.3, with the 35-cell r2 final board compressed
to one row per run family (best carried and best oracle) in the main text
and the full board in S2. D-1 to D-5 remain open; D-4's exhibit (iii) now
has a drafted source.

### 2026-08-25 — Original publication

S142, on the PI's "start planning for the usual sections" direction,
same day as the venue lock. Strawman for joint review; the five open
decisions gate conversion of the drafts.
