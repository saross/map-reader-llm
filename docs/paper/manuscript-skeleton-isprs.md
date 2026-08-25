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
- **D-2**: Related work as its own § 2 (proposed) vs folded into the
  Introduction (frees ~400 words for Results)?
- **D-3**: single Results (proposed) vs Experiments+Results split?
- **D-4**: the three main-text exhibits as proposed (GS board+geometry,
  Pareto, transfer)?
- **D-5**: the companion-paper boundary — is Seed 7
  (micro-registration) promised in this paper's Discussion as future
  work, or silently reserved?

## Changelog

### 2026-08-25 — Original publication

S142, on the PI's "start planning for the usual sections" direction,
same day as the venue lock. Strawman for joint review; the five open
decisions gate conversion of the drafts.
