# End-to-end verification charter — preregistration → experiments → results → mine documents

> **Status**: REVISED per PI review 2026-07-29 (all § 10 questions answered;
> design approved; gates and folder structure to be refined after a first
> run). Execution begins with Phase 0. **This document is the
> controller for the whole verification programme**: it is self-sufficient —
> any executor (a Claude session, a background agent, a script, or a
> non-Anthropic model) resumes from this file and the ledgers alone, with no
> reliance on conversational memory. Approved changes to this charter are
> themselves commits; the charter is the audit trail of its own evolution.

## 1. Goal — the operational definition of "bulletproof"

Every checkable claim in the mine-able corpus either **carries a verified,
resolvable anchor to a less-writable artefact**, or is **explicitly flagged
as unverified/interpretive** — with each verification recorded in a
machine-readable ledger row so it can be re-run mechanically, and with a
**standing monitoring layer** that re-validates anchors at build time so the
swept state persists instead of decaying (the April-2026 audit verified a
snapshot and decayed; this programme must not).

Explicitly NOT the goal: a guarantee about interpretive prose. Paper-B's
lesson, already recorded at `planning/audit-and-completion-plan.md` § 6.6:
reliability transfers exactly as far as a structural check exists.
Interpretation gets adversarial reconstruct-and-diff review and mandatory
anchors — controls, not proofs.

**Reusability**: this apparatus is intended to become routine for future
papers (next: inscriptions; also llm-reproducibility). Prefer generalisable
mechanisms (schemas, scripts, verdict vocabularies) over project-specific
hacks; anything project-specific must be isolated in § 4's corpus tables so
the rest lifts out cleanly.

## 2. Scope

**In scope (the mine)**: `results/**.md`; `reports/**.md` (excluding
`reports/d17-inventory/` which is audit apparatus); the six manifests —
`results/passes-manifest.json`, `results/conditions-manifest.json`,
`results/runs-manifest.json`, `results/analyses-manifest.json`,
`results/run-registry.json`, and `results/run-conditions.json` (their
generated `.md` renderings are verified by regeneration, never read);
the `docs/methodology/` mine subset — the top-level methodology docs,
`methodology/reports/`, `methodology/transparency/`, and, inside
`preregistration/`: `protocol-errata.md` plus the five tracking docs
(`decisions-log.md`, `hypothesis-tracking.md`, `execution-plan.md`,
`execution-checklist.md`, `analysis-summary.md`); `docs/methods-outline.md`;
and the lodged registration (as the fixed root — verified byte-identical
to the OSF-posted artefact 2026-07-28, blob `fa221b30…`; anchor only,
never a correction target).

**Excluded from the mine but usable as attestation sources** (GATE 0
ruling, 2026-07-29): `docs/methodology/references/` (third-party
literature), `docs/methodology/research/` (commissioned external
reports), `preregistration/simulations/`, `preregistration/tasks/`, and
non-lodged preregistration drafts.

**Out of scope**: all paper-bound prose (`docs/paper/**` — will be
regenerated from the mine; PI decision 2026-07-28); `archive/**` (frozen
history); `docs/notes/**` reflections (historical record).

**Working notes have a dual role (PI, 2026-07-29)** — they are both:
(a) an **attestation source** for interpretive claims — real-time
observations made during the experiments, months closer to the source than
anything written now, and explicitly planned as material for the Discussion;
and (b) a **correction target** where they contain *factual* errors about
empirical results. Factual corrections never edit an Obs: one new Obs rider
per error family, with a pointer appended at the original Obs (appending a
pointer is permitted; editing is not).

**The stratum rule (PI, 2026-07-29)**: artefacts up to and including
`results/**` are **facts only** — the kind of content that belongs in a
paper's Results section. Interpretation belongs in `reports/**` (Discussion
or occasionally Methodology material) and must be anchored either to results
artefacts (its factual basis) or to attested contemporaneous interpretation
(working notes / transcripts). A **stratum-purity check** — verifying that
`results/**` documents contain no unflagged interpretation — is queued as a
deferred item in § 7; it need not run in the first sweep but the rule
governs all new writing immediately.

## 3. The chain and its six claim classes

| # | class | typical claim | verified against | phase |
|---|---|---|---|---|
| C1 | Commitment | "the registration specifies X" (as an obligation) | the lodged text, decomposed into `commitments.json` | 1 |
| C2 | Execution | "X was run / never run" | manifests + `outputs/` artefacts; errata for licence | 1 |
| C3 | Provenance | manifest field values (model, tokens, dates, counts) | raw `*.meta.json` / eval JSONs at source | 2 |
| C4 | Quantitative | any number in a mine document (F1, MCC, p, Δ, $, N) | the artefact it cites, recomputed | 3 |
| C5 | Attribution | "the preregistration says / preregistered X" | the three lodged documents only (`osf/README.md:3,9-11`) | 4 |
| C6 | Rationale & event | "we did X because Y"; "X was deprioritised because…"; bare "we did X" narrative | attested contemporaneous sources (§ 5 hierarchy) | 4 |

**C6 verdict vocabulary** (true/false is the wrong shape here):

- **ATTESTED** — a contemporaneous dated source states it; quote + locator
  required. (Template: the H6 deferral — the invented "budget prioritised"
  was replaced by the *stronger* attested reason, a dated PI turn.)
  **Interpretive claims** in reports are ATTESTED when traceable to a
  contemporaneous working-notes or transcript record of the observation or
  decision. **Attestation establishes provenance of the thinking, not its
  truth** (PI, 2026-07-29): an attested interpretation may still be
  empirically wrong — later evidence may invalidate it — and its current
  empirical validity is a separate check against the results artefacts.
  Both facts go in the ledger row when they diverge.
- **RECONSTRUCTED** — consistent with evidence, no direct attestation; the
  document must label it as inference, never state it as fact.
- **UNSUPPORTED** — no evidence; searches enumerated (auditable negative);
  delete or flag.
- **CONTRADICTED** — evidence says otherwise; correct, citing the evidence.

All other classes use: **VERIFIED / CORRECTED (was wrong, now fixed, commit
ref) / FLAGGED (unresolvable — downgraded or explicitly marked unverified) /
DEFERRED (blocked, reason stated)**.

## 4. Authority hierarchy (least-writable first)

1. Raw run outputs: `outputs/**` `*.meta.json`, detection GeoJSONs,
   eval JSONs. Physical measurements (GeoTIFF headers) outrank all prose.
2. The lodged registration: `docs/methodology/preregistration/osf/`
   (three documents; frozen; **never edit, never lint**). Bright line =
   lodgement 2026-01-31 **12:54:09 UTC** (OSF API `date_registered`).
3. Manifests (generated; verified by Phase 2 before use as authority).
4. Errata register `docs/methodology/preregistration/protocol-errata.md`
   (the amendment record — but it has
   itself carried false content: E10/E37/E45/E54 pre-correction. Errata are
   authority for *what was decided*, never for *what the registration says*
   — that is always checked at source 2).
5. Session transcript archives: `~/cc-archives/<project>/` (per-session
   `session.jsonl.gz` + `session.meta.json` + `subagents/`; top-level
   `CATALOG.json`). The 2026-03→05 coverage hole is **plugged** (verified
   2026-07-28: 41 sessions in the window); per-session metadata verification
   is still in progress (PI, 2026-07-28) — treat `session.meta.json` fields
   as provisional; content is authoritative. **The postgres query layer is
   mid-repair: grep/read the raw archives directly; do not trust query
   results until the PI clears it.**
6. Dated working-notes / decisions-log entries (contemporaneous only —
   see execution rule 6).
7. Git history (timestamps, diffs — not commit-message rationales).

## 5. Execution rules (all learned the hard way in this project)

1. **Verify against the least-writable artefact available.** Prose about
   prose is weakest.
2. **Fresh-context adversarial verification.** The author of a claim, a
   correction, or a fix never verifies it in their own context. This applies
   to the ~150 Session-119 corrections (author: Claude Fable; six waves,
   commits `2c354ca2e`→`df16d855a`) — they are themselves Phase-4
   verification targets, ideally cross-family (§ 8).
3. **No sampling at this error density** — full enumeration per class.
   Any bounded coverage (top-N, stratification) must be logged as dropped
   scope, never silent.
4. **Auditable negatives.** Every "not found" states what was searched, over
   which files, with which variants (including the three generations of
   hypothesis numbering: H2-C↔H10, H6↔H8, H14↔H12, H15↔H13, H13←"H18").
5. **JSON-parse, never line-grep, structured files.** A line-based grep over
   pretty-printed JSON has twice produced confident false absences here.
6. **Rationales first appearing in documentation-catch-up commits are
   unsourced by default.** Both discredited H6/H2-C rationales entered that
   way.
7. **Never attribute transcript content by role metadata** (`userType`,
   `isMeta`, `type` are all untrustworthy). Read content; attribute to the
   PI only from a retrieved full turn.
8. **Commit before delegating; restore by inverse edit, never checkout**
   (the `/audit` rule). Verification agents run read-only.
9. **Corrections land as commits referencing ledger rows**; errata edits use
   explicit dated withdrawal/correction blocks, never silent rewrites.
10. **Pre-execution registration for any new run**: registry entry,
    conditions, `predicted_outcome` committed with `status: planned` BEFORE
    the API call (`audit-and-completion-plan.md` § 6.4).
11. **Change the question, not just the questioner** (paper-B; PI,
    2026-07-29). Where feasible, verification asks an *orthogonal* question
    of the source — "reconstruct what the source says about X" rather than
    "is claim Y true?" — because a fabrication survives same-question
    re-checking far more easily than orthogonal interrogation. Not always
    possible; use whenever it is.
12. **Charter self-sufficiency is itself verified** (GATE 0 ruling,
    2026-07-29, generalising the Phase 0 stumble log). Every artefact this
    charter names carries a repo-relative path; every glob is checked
    against the tree when written or revised; every external figure
    (price, quota, rate limit) carries a dated source anchor and is
    re-verified at the gate that spends against it. Executors log every
    place they must guess or look outside the charter and ledgers; those
    stumbles are charter bugs, fixed by commit at the next gate.
13. **Every breach-class verdict requires a defence search** (Phase 1
    lesson, 2026-07-29: the PI caught one-sided evidence assembly in 2 of
    12 headline findings; a blind defence pass then qualified all 12).
    A CONTRADICTED/FLAGGED/unlicensed-deviation verdict must record which
    licensing and exculpatory sources were searched (errata, decisions
    log, execution-checklist deviation table, registered qualifiers,
    commit timeline) and the nearest miss — the rule-4
    auditable-negative discipline applied to context. Prosecution
    without a recorded defence search is an incomplete verdict. Where
    stakes warrant, run the defence as a separate fresh-context pass
    (rule 2 applied to the finding itself).

## 6. Ledgers

Home: `reports/verification/ledgers/` — one JSONL file per claim class
(`c4-quantitative.jsonl` etc.), append-only. Row schema (v1):

```json
{
  "claim_id": "c4-0001",
  "class": "C4",
  "source": {"file": "results/x/report.md", "line": 123},
  "claim_text": "verbatim quoted claim",
  "anchor": {"file": "results/x/eval.json", "path": "$.f1_at_20m"},
  "method": "recompute|diff|attest-search|reconstruct-and-diff",
  "verdict": "VERIFIED",
  "evidence": "recomputed 0.8902 == quoted 0.890 (2 d.p. rounding)",
  "checker": {"model": "returned model string", "request_id": "…",
               "harness": "claude-session|script|openai-batch",
               "date": "2026-07-29"},
  "disposition": null
}
```

Rules: `claim_text` and `evidence` are **verbatim spans, not paraphrase**
(structurally prevents bare assertion — required for all executors, see
§ 8). `checker.model` records the *returned* model string per call (no dated
snapshot IDs exist for Sol; this is the only reproducibility anchor).
Coverage matrix (`reports/verification/coverage.md`) is **generated** from
the ledgers by script — never hand-maintained.

**Monitoring layer** (Phase 5, the part that makes it stick): a
`revalidate_ledgers.py` script re-resolves every anchor, re-diffs every
recomputable value, and **mechanically verifies every `claim_text` and
`evidence` span appears verbatim at its cited locator** (verbatim spans are
load-bearing — a paraphrase logged as a quote is itself a fabrication class,
so the spans themselves are verified, not trusted; PI, 2026-07-29). It also
**enforces rule 13 mechanically** (GATE 1 ruling, 2026-07-29): every
breach-class row (CONTRADICTED / FLAGGED / unlicensed-deviation) must carry
a non-empty defence-search record, or the build fails — prosecution without
a recorded defence search cannot persist in the ledgers. Wired beside
`drift_check` so any regeneration or edit that breaks a verified claim
fails loudly. New rationale claims in regenerated prose are quotable only
from ATTESTED ledger rows. The defence-pass protocol itself (blind
counsel-for-the-defence agents with calibration probes) is part of the
reusable apparatus for future repo reviews (§ 1 reusability).

## 7. Work queue and gates

Granularity: per-document (C4) or per-claim-family (others). An executor
claims an item by ticking it with its identity, appends ledger rows, commits
corrections, moves on. **GATE** = PI review before proceeding.

- [x] **Phase 0 — scoping.** Enumerate the corpus: document list, estimated
  claim counts per class, cost per class (tokens + $ for Sol batch), and the
  proposed foreground/background split. Produces
  `reports/verification/phase0-scope.md`. **GATE 0**: PI approves scope,
  budget, and executor assignment. *(Claimed and executed 2026-07-29,
  Claude Fable 5 interactive session; report produced. **GATE 0 PASSED
  2026-07-29** — all six decisions approved; cross-model spend capped at
  US$150, § 10 item 6.)*
- [x] **Phase 1 — commitments and execution (C1, C2).** *(Claimed and
  executed 2026-07-29, Claude Fable 5 interactive session; deliverables
  complete — ledger v1.2 (702 commitments, 402 discharged / 89 waived /
  211 open), c1+c2 ledgers (1,617 rows), licence census (13
  UNLICENSED), guard wired; package at
  `reports/verification/phase1-gate-package.md`; **GATE 1 PASSED
  2026-07-29** with directives — § 10 item 7.)* Build
  `results/commitments.json` from the lodged text (subsumes publishing the
  trigger census; five-element trigger rule: statistic, comparison scope,
  uncertainty criterion, evaluation moment, **evaluation corpus**). Run the
  execution→errata inverse census (every unlicensed factor level in
  `run-conditions.json` needs an erratum). Wire the open-commitment warning
  into `drift_check` (closes C3 of the guard via the append-only ledger).
  **GATE 1.**
- [x] **Phase 2 — provenance (C3).** *(Claimed 2026-07-29; executed
  Sessions 120–121, Claude Fable 5. **GATE 2 PASSED 2026-07-30** —
  § 10 item 8. 1,514/1,534 ledger rows VERIFIED, 20 FLAGGED with
  landed dispositions; conditions manifest 100 % clean; E62–E71 +
  five correction blocks; generator v0.6.0; family-FDR registered
  then computed (rejection set {H2, H3, H7}); E71 recovery campaign
  265/288 with a 6-tile permanent residue (Obs 374); per-era
  verifiability map in the package.)* Field-level re-derivation of
  `passes-manifest.json` and `conditions-manifest.json` rows from raw
  metas/evals. **Full enumeration** (settled, PI 2026-07-29; 1,132
  passes / 322 conditions — script job on sapphire, LLM only for
  discrepancy triage). Known wall, discovered at GATE 1: the
  retest-era pipeline left `usage_stats` unpopulated (all 225 phase3c
  metas and phase3a siblings) — token-level fields are unverifiable
  for that era; record per-era field verifiability explicitly.
  **GATE 2.**
- [ ] **Phase 3 — quantitative sweep (C4).** LLM extracts claims to ledger;
  deterministic script recomputes from cited artefacts and diffs; LLM
  triages mismatches. The biggest unswept surface. Background-batchable.
  **GATE 3.**
- [ ] **Phase 4 — attribution and rationale (C5, C6).** Re-verify the
  Session-119 corrections cross-family (§ 8); sweep remaining C5 sites
  (notes-file families from the D17 sweep, as appended notes/new Obs);
  trace every C6 rationale/event claim in the mine through the § 4
  hierarchy; reconstruct-and-diff the load-bearing interpretive paragraphs.
  **GATE 4.**
- [ ] **Phase 4b — open-set discharge campaign** (GATE 1 directive,
  2026-07-29). After Phase 4: drive the open commitment set (211 at
  GATE 1) as low as it can honestly go, under the **run-it-now policy**
  (§ 10 item 7): a promised metric or analysis that was omitted but can
  be run now is run, not merely erratum'd — barring *excessive* API
  expense (PI budget: a few hundred US dollars; per-batch API review
  gates still apply). Includes the registered eight-hypothesis BH-FDR
  family, the promised-vs-chosen side-by-side metric comparisons, and
  categorisation of the remainder (waive by erratum / owed to Stage 2
  registration / discharge in paper drafting). Produces a campaign plan
  for PI approval before any spend. **GATE 4b.**
- [ ] **Phase 5 — monitoring.** `revalidate_ledgers.py` (incl. verbatim-span
  verification and the rule-13 defence-search check), coverage generation,
  drift-check integration, and the final coverage report stating verified
  classes and named residual (unswept or unverifiable) surfaces.
  **GATE 5**: PI signs the end-state.
- [ ] **Deferred — stratum-purity check.** Verify `results/**` documents are
  facts-only per the § 2 stratum rule; migrate or flag any interpretation
  found there. Not required for the first sweep (PI, 2026-07-29); the rule
  binds all new writing immediately.

Sequencing constraint: Phases 1–2 precede 3 (documents cite manifests;
manifests must be verified before they serve as anchors).

## 8. Executors and the cross-model layer

Any executor follows §§ 5–7. **Foreground** = interactive, PI-steerable
session work (orchestration, adjudication, gate packages, commits);
**background** = detached executors (background agents, sapphire script
runs, asynchronous batch jobs). Assignment guidance (PI economics,
2026-07-28):

- **Deterministic scripts (sapphire)** — all recomputation, revalidation,
  coverage generation. Cheapest and most trustworthy; prefer whenever the
  check can be made mechanical.
- **Claude (Max plan)** — charter maintenance, orchestration, C6 tracing,
  reconstruct-and-diff, disagreement adjudication. **Model policy (PI,
  2026-07-29): agents default to Opus 5**; escalate to Fable only where
  Fable-class judgement is genuinely required (orchestrator's call);
  consider Sonnet 5 only for huge-but-straightforward passes.
- **GPT-5.6 Sol (OpenAI credit)** — per
  `~/personal-assistant/wiki/planning/cross-model-verification-plan-2026-07-27.md`:
  **Path C, raw Batch API only** (model `gpt-5.6-sol`, ~50 % off; ~US$10–45
  per ~700 calls). NOT the agent CLI (harness nondeterminism; Sol measures
  differently by harness), NOT tmux-driving (screen-scrape, no completion
  signal, bad provenance), NOT a ChatGPT subscription (no API access).
  Role: cross-family verifier — first target is the ~150 Session-119
  corrections (rule 2: the author must not check its own work; cross-vendor
  is the strongest fresh context). Schema-constrained verdicts **requiring a
  verbatim evidence span** (Sol's system card flags unverified completion
  claims; the schema structurally prevents bare assertion). Log returned
  model string + request ID per call. Bulk passes are script jobs;
  Claude orchestration only on disagreements. Similarity bias is graded
  (Goel et al. 2025): cross-vendor reduces, does not eliminate — disputed
  items with two-way disagreement go to a **third family** for tiebreak.
  **Prompt caching (PI note, 2026-07-29)**: Sol supports explicit caching
  (90 % off cache reads, 1.25× writes, ≥1,024-token prompts, ≥30 min
  life). Structure every request as [static preamble: schema + method +
  verdict vocabulary — byte-identical, front-loaded] + [variable per-item
  payload last]: costs nothing, versions the verification instrument, and
  earns the read discount wherever it applies. **Stacking SETTLED (PI,
  2026-07-29): the Batch 50 % and cache-read discounts stack
  independently for Sol** — a batch job with a shared static system
  prompt gets both the batch discount and the ~90 % cache-read reduction
  on the shared prefix. Implementation: stable content at the top of the
  prompt with **explicit cache breakpoint markers**
  (`cache_control: {"type": "ephemeral"}`) so the prefix is cached and
  reused across batch requests. Routing therefore simplifies: bulk passes
  stay on Batch *and* collect cache reads on the preamble; synchronous
  calls only where latency matters (disagreement triage). Phase 0's cost
  model prices the preamble at stacked rates; the only residual check at
  implementation time is the marker syntax against current docs.
  **Pricing anchor** (rule 12): official page
  `https://developers.openai.com/api/docs/pricing`, verified 2026-07-29 —
  `gpt-5.6-sol` Batch rates US$2.50 input / $0.25 cached read / $3.125
  cache write / $15.00 output per million tokens (the Batch table itself
  prices cached input, confirming the stacking); long-context columns do
  not apply at verification call sizes. Re-verify at every API review
  gate before spend.

## 9. Resumption protocol

1. Read this charter top to bottom.
2. Read `reports/verification/coverage.md` (if absent, Phase 0 has not run).
3. Take the first unchecked, ungated queue item; honour every § 5 rule.
4. Append ledger rows; commit with messages referencing claim_ids; tick the
   item; push.
5. Stop at any GATE whose review is pending — gates belong to the PI.

## 10. PI review decisions (2026-07-29)

1. **Gates**: approved as drafted; review and refine after a first run.
2. **Notes handling**: one new Obs rider per error family, with a pointer
   appended at the original Obs (append-only; no edits to originals).
3. **Phase 2**: full enumeration.
4. **Verifier order**: Sol first (Session-119 corrections as first target),
   then Opus 5 (Fable where Fable-class judgement is needed — orchestrator's
   call), then **Gemini 3.1 Pro as tiebreaker**. Caveat carried from the
   draft: Gemini is the object of study — weigh that when the disputed item
   concerns Gemini cost/billing claims specifically.
5. **Ledger home**: `reports/verification/` stands; folder structure
   reassessed after a first run.
6. **GATE 0 (2026-07-29, partial)**: of `phase0-scope.md` § 7 — decisions
   1–4 approved (scope rulings incl. methodology-subset reading and
   exclusions; re-derive-and-diff for the generated stratum with a
   committed generated-file registry; C3 extension to all six manifests,
   28,682 field checks; executor assignment and foreground/background
   split). Decision 6 approved with the instruction to generalise/cascade
   the stumble-log fixes for durability — landed as the § 2 explicit scope
   lists, § 4 path fix, § 5 rule 12, § 8 pricing anchor and
   foreground/background definitions, and this record. Decision 5 (Sol
   budget): PI supplied the official pricing page; rates verified
   (matching the third-party figures); revised worst-case-honest budget
   (Stage A ≤ US$15 worst case, expected $3–8; programme expected $25–60,
   absolute worst ~$120) awaiting PI confirmation before any Sol spend.
   **Ruled 2026-07-29 (same review, follow-up turn): decision 5 approved
   with headroom — cross-model (Sol + tiebreak) spend capped at US$150
   programme-wide. GATE 0 PASSED; Phase 1 unlocked.** Per-batch API
   review gates still apply before each launch.
7. **GATE 1 (2026-07-29) — PASSED with directives.** Preceded by a PI
   memory-review that qualified 2 of 12 headline findings, answered by
   the calibrated blind defence pass (rule 13 born; all 12 findings
   qualified; apparatus record
   `reports/verification/apparatus/defence-pass-adjudication-2026-07-29.md`).
   Rulings:
   (a) **Defence check institutionalised** — in the Phase 5 monitor
   (§ 6, mechanical rule-13 enforcement) and as reusable apparatus for
   future repo reviews.
   (b) **Registration-contradiction errata policy**: file errata
   recognising each internal contradiction in the lodged text; adopt
   the reading that fits the spirit of the campaign; explain the
   reasoning; acknowledge openly that the choice is post facto, made
   with results in hand.
   (c) **Run-it-now policy**: an omitted-but-runnable promised metric
   or analysis is run, not merely erratum'd, barring *excessive* API
   expense (PI dedicates a few hundred US dollars; emphasis on
   excessive; per-batch review gates apply). Promised metrics are
   displayed alongside the eventually-chosen ones — side-by-side
   comparisons demonstrating why the change was made.
   (d) **Eight-hypothesis BH-FDR family**: run it now (zero API cost),
   plus a Methods/Discussion disclosure of why practice deviated.
   (e) **Erratum queue approved** with amendments: the three unlicensed
   families erratum frames them as *additional, unregistered extensions
   of the proposer-verifier programme* (verified: all three carry PV
   architectures; E37 frames the PV programme as the registered
   contingency exercised) — serendipitous additions, not deviations
   from registered studies. HIGH-thinking erratum approved with a
   verification caveat: configured HIGH in all 225 phase3c metas and
   pre-committed YAML declarations, but token-level corroboration is
   unavailable (retest-era usage_stats unpopulated) — worded honestly,
   per the PI's mis-recording warning. Errata 3–6 approved as queued.
   (f) **Open-set discharge campaign** authorised as Phase 4b (plan
   before spend).
   (g) **Phase 2 start approved.**

Also settled in the same review: the stratum rule and working-notes dual
role (§ 2), the interpretive-ATTESTED extension (§ 3), orthogonal
interrogation as execution rule 11 (§ 5), verbatim-span verification in the
monitor (§ 6), and the Claude model policy (§ 8).

8. **GATE 2 (2026-07-30) — PASSED.** Package:
   `reports/verification/phase2-gate-package.md`; the day's PI rulings
   verbatim at `reports/verification/phase2-rulings-2026-07-30.md`.
   Rulings at the gate (PI, verbatim): "1. I'm happy to acept your
   dispositions. 2. Ratified, thanks. 3. I approve progressoin to
   phase 3."
   (a) **Correction-queue dispositions accepted** at the table grain
   (package § 3) — every row's resolution is a landed, anchored fact;
   row-by-row manual review judged unnecessary (mechanical; Phase 5
   re-verifies each anchor).
   (b) **Ledger-supersession convention ratified**: superseding rows
   for resolved FLAGGED claims land with the Phase 5
   `revalidate_ledgers.py` design, which owns row lifecycle; nothing
   appended before that design exists.
   (c) **Phase 3 (C4 quantitative sweep) unlocked** — the § 7
   sequencing constraint is satisfied (manifests Phase-2-verified and
   usable as anchors). Phase 3 inherits the per-era verifiability map
   (package § 4): retest-era token-level claims are permanently
   unverifiable and must be flagged, not fought.
   Also standing from the same day (phase2-rulings + session record):
   the **always-flex instruction** for realtime API calls, the
   per-pass own-model rule for recoveries, and the E71 recovery
   campaign's outcome (265/288; 6 permanent tiles; Obs 374).
