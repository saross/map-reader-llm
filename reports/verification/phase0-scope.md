# Phase 0 — verification programme scoping report

> **Last revised**: 2026-07-29 (PI decision record externalised verbatim).
> See [§ Changelog](#changelog) for revision history.

**Controller**: `planning/audit-charter.md` (§ 7 Phase 0). **Executor**:
Claude Fable 5 interactive session, 2026-07-29. **Status**: complete;
**awaiting GATE 0** — Principal Investigator (PI) approval of scope,
budget, and executor assignment. No Phase 1 work has begun.

All counts below were computed this session by scripts preserved in the
session scratchpad (`enumerate_corpus.py`, `count_claims.py`,
`reclassify.py`); structured files were JSON-parsed, never line-grepped
(charter § 5 rule 5). Claim counts are **scoping estimates** from regex
heuristics — Phase 1–4 enumeration is the authoritative census; charter
§ 5 rule 3 (no sampling) binds execution, not this estimate.

## 1. Corpus enumeration

### 1.1 The mine, by charter § 2 clause

| Charter clause | Files | Words | Notes |
|---|---:|---:|---|
| `results/**.md` | 2,241 | 1,325,118 | Dominated by generated artefacts (§ 1.3) |
| `reports/**.md` (excl. `d17-inventory/`) | 18 | 43,511 | All hand-written |
| Six manifests (§ 1.2) | 6 JSON + 5 companion `.md` | — | Companions are generated |
| `docs/methodology/**` mine subset (§ 1.4) | 24 | 63,249 | 10 top-level + 6 `reports/`+`transparency/` + 6 errata/tracking + 2 spatial/index (counted within top-level) |
| `docs/methods-outline.md` | 1 | 2,605 | Hand-written |
| Lodged registration (fixed root) | 3 | 31,708 | Never edited; anchor only |

### 1.2 The six manifests, resolved

Charter § 2 says "six manifests (`results/*-manifest.json` + sources)",
but that glob matches only four files. The six manifest-family files in
`results/` are (row × field counts recomputed from source this session):

| File | Rows | Fields/row | Field checks |
|---|---:|---:|---:|
| `passes-manifest.json` | 1,132 | 20 | 22,640 |
| `conditions-manifest.json` | 322 | 16 | 5,152 |
| `runs-manifest.json` | 31 | 16 | 496 |
| `analyses-manifest.json` | 18 | 15 | 270 |
| `run-registry.json` | 31 | 4 | 124 |
| `run-conditions.json` | 31 study families | ~5,448 leaf entries | (C2 census source) |

The charter's settled Phase 2 figures (1,132 passes / 322 conditions)
are **confirmed against source**. The five companion `.md` renderings
(`passes-manifest.md` etc.) carry explicit `GENERATED FILE — DO NOT
EDIT` headers and are verified by regeneration, not reading.
`docs/manifest-schemas/` holds six schemas (one is shared definitions),
corroborating the six-manifest count. Charter § 2 needs a text fix
(stumble log, § 6).

### 1.3 Two strata: generated vs hand-written

The single most consequential Phase 0 finding. Classifying every mine
markdown file by generation markers (`_autogen` names, `evaluation.md`
and sweep/leaderboard filename patterns, `<!-- GENERATED`,
`**Generated**:`/`> Generated` headers):

| Stratum | Files | Words | Verification method |
|---|---:|---:|---|
| **Generated** | 2,136 | 1,128,898 | Script: re-derive from source artefacts + diff (Phase 3); file-level ledger rows |
| **Hand-written** | 148 | 306,360 | Large Language Model (LLM) claim extraction + script recompute |

The generated stratum is 79 % of mine words but costs no LLM reading:
`evaluation.md` (1,633 files), `report_autogen.md`, leaderboard tiers,
threshold sweeps, False Discovery Rate (FDR) tables, and manifest
companions are all re-derivable from committed JSON/GeoJSON sources.
The hand-written stratum breaks down as: `results/` 105 files
(196,220 w), `reports/` 18 (43,511 w), `docs/methodology/` 24
(63,249 w), `docs/methods-outline.md` (2,605 w). Classification was
heuristic; Phase 3's first step hardens it into a committed
generated-file registry (each file's generator + source named).

### 1.4 Proposed scope rulings (GATE 0 decisions)

Charter § 2's `docs/methodology/**` glob is broader than its
parenthetical "(errata, tracking, methodology docs)". Proposed reading:

- **In the mine**: the 10 top-level methodology docs;
  `methodology/reports/` (6) and `methodology/transparency/` (2); and —
  found *inside* `preregistration/` — the errata register
  (`protocol-errata.md`, 19,628 w) plus the five tracking docs
  (`decisions-log.md`, `hypothesis-tracking.md`, `execution-plan.md`,
  `execution-checklist.md`, `analysis-summary.md`; 18,575 w together).
- **Excluded from the mine** (usable as attestation sources, never
  correction targets): `references/` (3 files, 672,477 w of third-party
  literature), `research/` (9 commissioned external reports),
  `preregistration/simulations/` and `preregistration/tasks/` (planning
  apparatus, historical record), and non-lodged preregistration drafts.
- **Anchor only, never edited**: `preregistration/osf/` — the three
  lodged documents (`preregistration.md` 18,904 w, appendix-prompts
  10,768 w, coverage 2,036 w; identified from `osf/README.md:3,9-11`,
  matching the charter's C5 anchor exactly) plus four supporting files.

## 2. Estimated claim counts per class

| Class | Estimated volume | Basis (this session) |
|---|---|---|
| C1 Commitment | ~150–250 commitments | 201 commitment-candidate sentences across the 3 lodged docs (149 + 42 + 10) |
| C2 Execution | 61 errata entries; 31 study families, ~5,448 leaf factor-level entries | Parsed `run-conditions.json`; counted `E<n>` headings in the errata register (E1–E61 range seen) |
| C3 Provenance | **28,682 field checks** (27,792 charter-settled passes+conditions, + 890 proposed extension to runs/analyses/registry) | Row × field counts, § 1.2 |
| C4 Quantitative | Hand-written: 18,971 numeric spans (≈ 12–18 k genuine claims after excluding dates/identifiers); generated: 2,136 file-level re-derivations | Regex over the hand-written stratum; span counts concentrate — top 50 files hold ~54 % |
| C5 Attribution | ~560 sites | `preregist*`/`prespecif*`/`lodged`/"registration says" matches; 162 in the errata register alone |
| C6 Rationale & event | ~426 rationale sentences (≈ 150–250 claim families after grouping) | Sentence-level rationale-marker matches |

Session-119 corrections (first Sol target, Phase 4): **~150 sites**,
landed in six waves, commits `2c354ca2e`→`df16d855a` (located via
`planning/paper-writeup-continuity.md`; the charter itself carries no
locator — stumble log, § 6).

Caveat: the errata register and `decisions-log.md` are simultaneously
correction targets (claims *in* them) and § 4-hierarchy attestation
sources (claims elsewhere checked *against* them). Their ledger rows
must record which role each check exercises.

## 3. Executor assignment per class

Per charter § 8 economics and § 10 ruling 4 (Sol first, then Opus 5,
Gemini 3.1 Pro tiebreak):

| Class | Extraction | Verification | Adjudication |
|---|---|---|---|
| C1 | Opus 5 agents decompose lodged text → `commitments.json` | Fable spot-audit of decomposition | PI at GATE 1 |
| C2 | Script census (run-conditions ↔ errata inverse) | Script | Fable → PI |
| C3 | — (full enumeration) | **Script on sapphire** | Opus 5 triage of discrepancies only |
| C4 | Opus 5 agents (hand-written stratum, ~40–60 background runs) | **Script recompute + diff**; generated stratum by re-derivation | Opus 5 triage; Fable for load-bearing items |
| C5 | Script grep census → Opus 5 verification against the 3 lodged docs | **Sol cross-family** (proposed Stage B) | Gemini 3.1 Pro tiebreak |
| C6 | Fable/Opus 5 tracing through § 4 hierarchy | **Sol cross-family**: S119 corrections first (~150), then C6 verdicts (proposed Stage B) | Gemini 3.1 Pro tiebreak; PI for residuals |

## 4. Cost model — the script/Claude/Sol split

### 4.1 Deterministic scripts (sapphire) — US$0

All recomputation, re-derivation, censuses, and monitoring. Wall-clock:
Phase 2 field re-derivation runs in minutes once written (~1 session to
write and test); Phase 3 re-derivation of 2,136 generated files is
hours on sapphire (bootstrap-bearing evaluations are the heavy tail);
`revalidate_ledgers.py` (Phase 5) runs per-build thereafter.

### 4.2 Claude (Max plan) — US$0 marginal; session budget

The binding cost is session/token time, not money. Biggest sink: the
Phase 3 extraction fleet — the 306 k-word hand-written stratum is
~410 k input tokens, chunked over ~40–60 Opus 5 background agents
across 1–2 sessions. Phase 1 decomposition (31.7 k words → 150–250
commitments): 1 session. C6 tracing and all adjudication: foreground,
1–2 sessions. Programme total: **roughly 6–9 working sessions**.

### 4.3 GPT-5.6 Sol (OpenAI credit) — raw Batch API, stacked discounts

Rates **verified 2026-07-29 against the official OpenAI pricing page**
(`https://developers.openai.com/api/docs/pricing`, supplied by the PI at
GATE 0; matches the third-party figures used in the original
publication): standard **$5.00 / $0.50 / $6.25 / $30.00 per million
tokens** (input / cached read / cache write / output); **Batch API is
50 % off across all four token types**, and the Batch table itself
prices cached input — confirming, from the official source, that the
batch and cache discounts stack (charter § 8). Effective stacked rates:
**$2.50 fresh input, $0.25 cached read, $3.125 cache write, $15.00
output per million**. Long-context columns ($10 / $1 / $12.50 / $45)
never trigger at our call sizes. Anchor recorded in charter § 8;
re-verify at each API review gate.

Per-call model (structure per charter § 8: static preamble ~1.5 k
tokens with `cache_control` breakpoint + variable payload last):

| Component | Tokens | Stacked rate | Cost/call |
|---|---:|---:|---:|
| Preamble (cached read) | ~1,500 | $0.25 /M | $0.0004 |
| Payload (claim + verbatim source context) | ~2,000 | $2.50 /M | $0.0050 |
| Output incl. reasoning (medium effort) | ~1,000 | $15.00 /M | $0.0150 |
| **Total, medium effort** | | | **≈ $0.02** |
| **Total, high effort** (~2.5–3 k output) | | | **≈ $0.04–0.05** |
| **Worst case** (high effort + ~10 k-token source excerpt + ~5 k reasoning/output) | ~11,500 in / ~5,000 out | | **≈ $0.10** |

Cache writes (~$0.005 per 30-minute window) are negligible. Aggregate
(per the global compute-aggregate rule), with the worst-case column
assuming *every* call hits ~$0.10 — deliberately pessimistic so the
budget cannot be caught short:

| Stage | Calls | Expected | Worst case |
|---|---:|---:|---:|
| Pilot (~30 items, two effort levels) | ~60 | ~$2 | $6 |
| **Stage A — S119 corrections** | ~150 | **$3–8** | **$15** |
| Stage B — full C5 sweep | ~560 | $11–28 | $56 |
| Stage B — full C6 sweep | ~426 | $9–21 | $43 |
| **Programme total (all stages + retries)** | ~1,200 | **$25–60** | **~$120** |

Worst-case containment: the pilot fixes measured per-call cost and the
right reasoning-effort level *before* Stage B's go/no-go at GATE 3, and
Stage B submits in waves so a surprise in wave 1 caps exposure at that
wave.

Gemini 3.1 Pro tiebreak on two-way disagreements (5–15 % of Sol-checked
items ≈ 60–170 calls): estimated < $10; rate pinned at the pilot gate.
Every Sol/Gemini run passes the standing API-review gate (model, batch
vs real-time, call count, cost) before launch; approval for one batch
never carries to the next.

**Recommendation**: approve the pilot + Stage A now (expected $5–10
all-in, bounded at **≤ $21 absolute worst case**); defer the Stage B
go/no-go to GATE 3, decided on pilot-calibrated per-call cost and
observed disagreement rate.

### 4.4 Per-phase summary

| Phase | Executor mix | API $ | Wall-clock |
|---|---|---:|---|
| 1 (C1, C2) | Opus agents + script | $0 | 1–2 sessions |
| 2 (C3) | Script (sapphire); Opus triage | $0 | 1 session + minutes runtime |
| 3 (C4) | Script + Opus fleet (background) | $0 | 1–2 sessions + hours on sapphire |
| 4 (C5, C6) | Fable/Opus + **Sol batch** + Gemini | $5–60 (staged) | 2–3 sessions + ≤ 24 h/batch turnaround |
| 5 (monitoring) | Script | $0 | 1 session |

## 5. Proposed foreground/background split

- **Foreground** (interactive Fable session): orchestration, charter
  maintenance, gate packages, discrepancy adjudication, C6 tracing on
  load-bearing paragraphs, all commits.
- **Background**: Opus 5 extraction fleet (background agents); sapphire
  script runs (Secure Shell (SSH), detached); Sol Batch jobs
  (asynchronous by design, ≤ 24 h turnaround); Gemini tiebreak calls.

Rationale: everything mechanical or fresh-context is backgroundable;
judgement and gate-facing work stays foreground where the PI can steer.

## 6. Charter stumble log (self-sufficiency bugs, § for after-run review)

Places this execution had to guess or look outside the charter — each a
charter bug to fix once GATE 0 clears:

1. **§ 2 six-manifests clause**: the glob `results/*-manifest.json`
   matches 4 of the 6 (misses `run-conditions.json` and
   `run-registry.json`, both named elsewhere in the charter); "+
   sources" is undefined (companion `.md`? generators? sidecars?).
   Resolved via `docs/manifest-schemas/` and § 7 Phase 1's naming.
2. **§ 2 `docs/methodology/**` glob vs parenthetical**: the glob
   sweeps in 672 k words of third-party literature (`references/`),
   commissioned external reports (`research/`), and planning apparatus
   (`simulations/`, `tasks/`), none plausibly correction targets — and
   the tracking docs the parenthetical *does* mean live unlabelled
   inside `preregistration/`. Proposed ruling at § 1.4.
3. **§ 4 authority 4** names `protocol-errata.md` without a path; three
   errata-named files exist. Actual:
   `docs/methodology/preregistration/protocol-errata.md`.
4. **§ 8 cost model**: the charter directs Phase 0 to price the
   preamble at stacked rates but neither it nor the referenced
   cross-model plan records per-token rates — fetched this session from
   third-party web sources (§ 4.3). The charter should pin dated rates
   or name the official pricing anchor to check at the pilot.
5. **§ 7 Phase 0** asks for a "foreground/background split" without
   defining the terms; interpreted as § 5 above.
6. **§ 5 rule 2 / § 8**: the ~150 Session-119 corrections have no
   locator in the charter; found via the continuity beacon (six waves,
   commits `2c354ca2e`→`df16d855a`). Phase 4's first target should be
   enumerable from the charter and ledgers alone.

Positive check: the charter's C5 anchor `osf/README.md:3,9-11` resolved
exactly; the Phase 2 row counts (1,132 / 322) reconfirmed at source.

**Status**: all six fixes approved at GATE 0 (decision 6, with the
instruction to generalise/cascade for durability) and landed in the
charter as commit `a1bd74f49` — explicit § 2 scope lists, § 4 path fix,
new § 5 rule 12 (charter self-sufficiency verified), § 8 pricing anchor
and foreground/background definitions, § 10 ruling record.

## 7. GATE 0 decision list

**Ruling status — GATE 0 PASSED (PI, 2026-07-29)**: decisions 1–4
approved as proposed; decision 6 approved with the generalise/cascade
instruction (landed, § 6); decision 5 approved after verification of
the § 4.3 figures, with headroom — **cross-model spend capped at
US$150 programme-wide** (above the ~$120 absolute worst case).
Per-batch API review gates still apply before each launch.

1. **Scope**: approve § 1.4 rulings (methodology-subset reading;
   exclusions; six tracking/errata docs in the mine).
2. **Generated stratum**: approve re-derive-and-diff with file-level
   ledger rows for the 2,136 generated files (in place of LLM reading),
   with the generated-file registry as Phase 3's first deliverable.
3. **C3 extension**: approve adding runs/analyses/run-registry manifests
   (+890 field checks → 28,682 total).
4. **Executor assignment** (§ 3) and foreground/background split (§ 5).
5. **Sol budget**: approve pilot + Stage A (≤ $10); defer Stage B
   (≤ $60 ceiling) to GATE 3 with pilot-calibrated numbers.
6. **Charter fixes**: approve landing § 6's six text fixes as commits.

## 8. PI decision record — verbatim

GATE 0 was ruled in-session on 2026-07-29. The PI's turns are quoted
verbatim below (typography preserved) as the attestation source for the
§ 7 ruling summaries; implementing commits: `a1bd74f49` (charter
fixes), `a8dcbb5b6` (cost verification), `2794539b8` (gate closure).

**Turn 1** (with the official OpenAI pricing URL and a screenshot of
the `gpt-5.6-sol` pricing table attached):

> Official OpenAI pricing can be found here:
> <https://developers.openai.com/api/docs/pricing>
>
> Regarding Section 7 Gate 0 decision list:
>
> 1. Approve
> 2. Approve
> 3. Approve
> 4. Approve
> 5. I don't want to get caught short, please check estimate against
> the pricing I provided above.
> 6. Approve the Section 6 fixes -- generalise / cascade solutions
> where possible to make these decisions durable
>
> Please confirm costs and I'll approve the run

**Turn 2** (after the worst-case-honest budget was presented):

> I approve this spend up to $150 (just to give us a bit more
> headroom). Gate 0 passed, please proceed to Phase 1.

## Changelog

### 2026-07-29 — PI decision record externalised

At the PI's request, the two in-session GATE 0 ruling turns are now
quoted verbatim in § 8 as the attestation source for the § 7 ruling
summaries (previously paraphrase-only). No ruling content changed.

### 2026-07-29 — GATE 0 partial ruling; official pricing verification

**Trigger**: PI GATE 0 review — decisions 1–4 and 6 approved; for
decision 5 the PI supplied the official OpenAI pricing page and asked
for the estimate to be re-checked so the budget cannot be caught short.

Numerical claims that moved:

| Claim | Before | After |
|---|---|---|
| Rate source | Third-party aggregators, unverified | Official page, verified 2026-07-29 (figures unchanged) |
| Batch+cache stacking | Settled by PI ruling only | Confirmed at source (Batch table prices cached input) |
| Pilot + Stage A ask | ≤ $10 | Expected $5–10, worst case ≤ $21 |
| Programme ceiling | ≤ $60 | Expected $25–60, absolute worst case ~$120 |

Not changed: corpus enumeration, strata, all claim counts, executor
assignment, foreground/background split. Charter fixes (decision 6)
landed as commit `a1bd74f49`. This revision's own commit is referenced
from the git history of this file. Later the same day the PI approved
decision 5 with a US$150 programme-wide cross-model spend cap —
**GATE 0 PASSED**, Phase 1 unlocked.

### 2026-07-29 — Original publication

Phase 0 scoping report produced per charter § 7 by the Claude Fable 5
session of 2026-07-29: corpus enumeration (two strata), per-class claim
estimates, script/Claude/Sol cost model at stacked batch+cache rates,
foreground/background split, charter stumble log, and the GATE 0
decision list. Baseline for all future revisions.
