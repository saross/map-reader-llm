# Step 0 — unexecuted preregistered work: consolidated summary

> **Last revised**: 2026-07-27 (initial publication — consolidates the Step 0
> agent walkthroughs). See [§ Changelog](#changelog) for revision history.

Consolidated findings from the Step 0 pass of the D17 preregistration
reconciliation: **what was registered but never run**, what was run instead,
and whether a decision is on record. Companion documents in this directory
hold the full detail; this page is the reading order and the conclusions.

Every claim below was verified at source. Where a claim rests on session
transcripts — which are volatile — the durable corroboration (or its absence)
is stated.

## Reading order

| document | scope |
|---|---|
| this page | conclusions and cross-cutting findings |
| `step0-h6-walkthrough.md` | H6 (Flash→Pro transfer) — 846 lines |
| `step0-h13-h15-walkthrough.md` | H13, H14, H15 |
| `step0-fine-to-coarse-archaeology.md` | H2 Condition C |
| `e37-pv-preregistration-audit.md` | whether PV was preregistered (it was) |
| `d17-inventory-h1-h4.md` … `d17-inventory-h9-h12.md` | per-hypothesis inventories |
| `d17-errata-census.md` | all 57 errata classified |
| `paper-b-verification-lessons.md` | verification design input |

## The unexecuted set

**H6, H13, H14, H15, and H2 Condition C.** H10 and H12 were previously
believed unexecuted on the authority of `hypothesis-tracking.md`; both in fact
**ran to completion** and returned nulls.

### H6 — Flash→Pro transfer

**Registered** (`osf/preregistration.md:651-701`) as a *protocol*, not a
comparison: Flash-optimal config on Pro, K=10 runs on a 20-tile stratified
holdout at 512 px; OFAT sensitivity on four named factors — M/E, H5,
temperature, ordering (`:670-675`); decision rule "if alternative outperforms
Flash-optimal by ≥0.03 F1, flag factor for adjustment" (`:677`); a
voting-threshold comparison; a conditional refinement phase; and a three-way
transfer verdict (full / partial / poor). Confirmatory per
`execution-plan.md:743`. Costed at **US$48 maximum**
(`studies/phase4-transfer.yaml:165`).

**Not run.** `studies/phase4-transfer.yaml` holds **13 `PLACEHOLDER`
strings** (verified). The 20-tile manifest never existed (`git log --all` → 0
commits). `scripts/analyse_phase4_transfer.py` was never written. No
`outputs/phase4*`. `execution-checklist.md:108` is blank. **H5 and ordering
were never varied on Pro**; the ≥0.03 rule, the voting comparison, and the
three-way verdict were never computed. Thinking level was varied instead — not
a registered factor, forced by E40.

*Partial credit*: the Phase-4 **decision logic** was built and tested (51
tests). Only the manifest, the driver, and the experiment are missing.

**Run instead**: `n1-pro-rerun-384` and `pv-diag-384` (both
`primary_hypothesis: "H11"`), 487 tiles at 384 px on the 4-map GS corpus,
crossing modality × thinking level × temperature. Genuine Pro text T=0.0 leads
(`pro-text-high-t-0-0` F1 0.804; `pro-text-medium-t-0-0` 0.792) against a best
Flash cell of 0.600 — after **E57** found four "Pro" cells had been billed as
Flash and forced a genuine-Pro re-run.

**The decision, in Shawn's own words** — 2026-03-11, cc-archive
`2026-03-11T04-33_b21c542c` turn #49, retrieved and verified verbatim:

> "no, this can wait, I need to work on the LLM-History-Paper, I just wanted
> to get it clear in my mind where we are. […] We should also undertake at
> least H10-H12 I think."

This answers a direct question about running Phase 4 before a paper deadline.
It is a **deferral for a competing deadline, not an abandonment** — and Phase 4
never reappeared. On 2026-03-24 Shawn was told explicitly that the Pro work
departed from H6 on thinking level, scope, and tile size, and proceeded
knowingly (→ E40, E41).

### H13 — overlap / stride

Registered Exploratory Tier B (`:1016`) with a **question, not a prediction**
(`:1020`) and three arms A/B/C (`:1024-1028`). Overlap was held at 12.5 % at
every tile size (256→stride 224, 384→336, 512→448; verified by computing
tile-origin spacing from the manifests).

**Calling the fixed tiling "arm A" would overstate twice**: all three
registered analyses are comparative, so a single arm yields nothing; and arm A
is specified in *pixels* (64/448), so only the 512 px corpus matches the
specification.

**Decision trail: silent.** Zero occurrences of "H13" or "overlap/stride" in
the session log, working notes, decisions log, or errata. Four status
assertions exist — undated, unattributed, giving **three different reasons**.

Two findings that undercut the reasons on record: the registered trigger was
**silently broadened** on 2026-01-09 (`ce17da492`) to add "or if disappointing
F1 performance…", with no changelog note — and that clause was arguably
**satisfied** (baseline F1 = 0.660), answered via voting and proposer–verifier
rather than overlap. And the drafters costed H13 at **~$6**, which undercuts
both recorded reasons ("budget"; "would require re-tiling" — the repo holds
three tile trees).

**H13 cannot shelter under H14/H15's "registered as deferred" framing.**

### H14 and H15 — cross-model consistency and voting

Both registered **Tier C and explicitly deferred at registration** — an
honest, documented position. H15's registered precondition was H14, which was
never run, so the precondition was never satisfied.

Confirmed unexecuted: 1,131 model-labelled passes are all Gemini
(784/305/30/12 across four model strings); zero `claude`/`gpt`/`anthropic`/
`openai` occurrences across all six results manifests; no such client in
`requirements.txt`.

Two qualifications worth carrying: the H14 deferral was introduced *during*
the v4.0 restructure (pre-v4.0 it read "Exploratory but important for
generalisability claims" with a four-phase protocol), and
`execution-plan.md:683-686` still promotes H14 to first priority.

### H2 Condition C — fine-to-coarse

**No decision was ever made.** Three things that resemble one:

1. **A drafting mismatch.** `execution-plan.md:587-590` has listed only
   Conditions A and B since `b91d76884` (**2026-01-01**). The preregistration's
   A/B/C table arrived a week *later*, in `af486fa56` (**2026-01-08**). No
   commit ever removes C — the operational plan and the registered design were
   drafted on separate tracks and never reconciled.
2. **An unanswered question.** Session `2026-03-07T05-59_c634c7c3` turns #3568
   and #3509 asked Shawn to confirm C stays dropped. His replies address other
   topics. *Caveat*: the index holds 361 of 4,198 turns in that session;
   coverage appears complete but this is an inference, and reading the full
   session would settle it.
3. **A post-hoc rationalisation with an invalid reason.**
   `hypothesis-tracking.md:86-87`, added **2026-03-15** (`7fb1d0b47`), says C
   "was not tested — the coarse-to-fine results were strong enough that context
   expansion was deprioritised". Under the registered logic this does not hold:
   the preregistration predicted **neither** architecture would help, and C
   tested the opposite mechanism independently. **This line needs correcting.**

**The mechanism reasoning is genuinely attested** and predates the drop — but
it is not H11 (which registered only 512 vs 384 and never ran 1024 px). It
comes from the 2026-01-07 multi-scale calibration pilot,
`archive/pilot-tile-size/results/multiscale-pilot-results.md:128`:

> "**Key limitation**: With 1024px recall at only 37%, the large-tile context
> cannot confirm most true positives. The fine-to-coarse approach requires a
> context scale with reasonable recall, which 1024px lacks in this
> configuration."

**Something was built**: `analyze_multiscale_voting.py:675`
`strategy_fine_to_coarse` ("Strategy 10") ran — 7 configurations, best F1
0.533. But it is an *approximation*: fixed grid tiles and a detection prompt,
not candidate-centred crops with a verification prompt. A verifier prompt was
drafted (`preregistration-appendix-prompts.md:1129-1160`) but never became a
file.

**Running it now is feasible** — roughly 1–1.5 days, mostly glue. Stage 1
exists (`outputs/retest/phase3a/`, 512 px, 30 runs per cell; the subpool
builder and `vote_count` already exist). Stage 2 needs no new crop code
(`extract_candidates.py --padding 512` yields 1024×1024). New work: the prompt
file, an `expand_*.json`, ~4–6 h orchestration. Two flags: the spec
contradicts itself on crop size (1024 px body `:482` vs 896 px appendix
`:1144`), and **the 37 % recall premise is itself stale** given model drift
(E37, Obs 163) — which argues *for* running it. No cost estimate yet; the
audited anchor is for 384 px crops and 1024 px is ~7× the pixel area.

## Two claims that must not reach the paper

1. **"Budget prioritised for Flash experiments"** (`docs/methods-outline.md:341`,
   the recorded reason H6 was deferred) is **assistant-invented**. It appears
   in no user turn and is contradicted by arithmetic: Phase 4 was costed at
   **$48** against far larger spend on the Pro work that replaced it. The real
   reason is on record and is better — a deliberate deferral for a competing
   paper deadline.
2. **"The coarse-to-fine results were strong enough"** as the reason H2-C was
   dropped (`hypothesis-tracking.md:86-87`) is logically invalid under the
   registered design, and post-dates the omission by two months.

## One finding in the project's favour

The `n1-baseline-matrix-384` **`exploratory` label was argued and approved, not
defaulted**. On **2026-06-03** Shawn was asked how to frame the board against
the preregistration and approved a reasoned proposal — `exploratory` with
`hypothesis_refs: ["H1","H6","H7"]` — on an argument that expressly denies it
is H6's confirmatory test ("yes, this is perfect… Proceed using this plan").
The surviving H6 reference is therefore a dated, human-approved *provenance*
decision. **Do not overwrite it in a bulk relabelling pass**
(`docs/methodology/n1-baseline-matrix.md:405-411`).

## Cross-cutting findings for the audit design

These affect method, not just content, and should be built into the audit.

### 1. Three generations of hypothesis numbering

Searching current numbers over pre-2026-01-08 material produces **both false
negatives and false positives**. Confirmed mappings:

| current | pre-v4.0 | note |
|---|---|---|
| H2 Condition C | **H10** | fine-to-coarse |
| H6 | **H8** | pre-v4.0 "H6" means prompt diversity |
| H14 | **H12** | cross-model consistency |
| H15 | **H13** | cross-model voting |
| H13 | *new at v4.0* | drafted as **"H18"** |

v4.0 is commit `af486fa56` (2026-01-08); last pre-v4.0 text is `fbca6b454`.
**Every audit step keyed to hypothesis numbers must carry this mapping and
state which identifiers were searched, so negatives are auditable.**

### 2. The transcript archive has a coverage hole

The indexed corpus stops **2026-03-11** and resumes **2026-05-23**. The
March–April window is reachable only via raw JSONL, which itself lacks
**2026-04-03 → 13**. Any "no evidence found" conclusion about that window is
weaker than elsewhere and must say so.

### 3. The index mislabels roles

At least two hits that appear to be Shawn's words are not — a subagent audit
report indexed as `user`, and an unrelated "phase 4" meaning step 4 of a
session plan. **Attribution to the PI must be confirmed by retrieving the turn,
never taken from a search snippet.**

### 4. Documentation-catch-up commits invent rationales

Both discredited claims above entered via post-hoc "update tracking to reflect
status" commits. Treat any rationale first appearing in a documentation-sync
commit as unsourced until traced to a decision.

## Open questions for the PI

1. **Run H2 Condition C?** Scaffolding largely exists; ~1–1.5 days; would
   convert a disclosure into a completed registration. Needs an API gate with a
   proper 1024 px cost estimate.
2. **Run H6/Phase 4?** Scaffolding intact, ~$48 — but E40 means even a re-run
   deviates from the registered protocol.
3. **The `pro-high-text` provenance thread** (see `d17-inventory-h13-h15.md`
   § 5): one pool's passes appear to span two models. May need billing-console
   reconciliation, as E57 did.
4. Correct or annotate the three `H6-exploratory` study YAMLs?
5. Recover the 2026-04-11 session (absent from both corpora)?

## Minimum remedial actions, independent of the above

- Erratum recording that **H2 Condition C** was never executed and never
  formally dropped.
- Correct `hypothesis-tracking.md:86-87` (invalid reason).
- Correct `docs/methods-outline.md:341` (invented reason).
- Erratum recording that the **registered inference method** (bootstrap +
  BH-FDR) is not the method used in the leaderboards (tile-swap permutation);
  see the D17 section of `docs/paper/results-outline.md`.
- Author analysis rows for `h8-v2`, `h10`, `h12-v2` so H8/H10/H12 can be
  represented at all.

## Changelog

### 2026-07-27 — Original publication

Consolidates the four Step 0 agent walkthroughs (H6; H13–H15; H2 Condition C;
plus the E37 PV audit and the Paper-B verification lessons) into a single
reading order with conclusions. All claims verified at source at time of
writing. Landed alongside the agent outputs in commit — see `git log` for this
directory.
