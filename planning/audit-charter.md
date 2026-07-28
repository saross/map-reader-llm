# End-to-end verification charter — preregistration → experiments → results → mine documents

> **Status**: DRAFT for PI review (written overnight 2026-07-28/29, Session
> 119; Shawn to review before any execution). **This document is the
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

**In scope (the mine)**: `results/**.md`, `reports/**.md` (excluding
`reports/d17-inventory/` which is audit apparatus), the six manifests
(`results/*-manifest.json` + sources), `docs/methodology/**` (errata,
tracking, methodology docs), `docs/methods-outline.md`, the lodged
registration (as the fixed root — verified byte-identical to the OSF-posted
artefact 2026-07-28, blob `fa221b30…`).

**Out of scope**: all paper-bound prose (`docs/paper/**` — will be
regenerated from the mine; PI decision 2026-07-28); `archive/**` (frozen
history); `docs/notes/**` reflections (historical record — corrections land
as appended notes or new Obs, never edits; not mine material).

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
4. Errata register `protocol-errata.md` (the amendment record — but it has
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
   to the ~150 Session-119 corrections (author: Claude Fable) — they are
   themselves Phase-4 verification targets, ideally cross-family (§ 8).
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
`revalidate_ledgers.py` script re-resolves every anchor and re-diffs every
recomputable value; wired beside `drift_check` so any regeneration or edit
that breaks a verified claim fails loudly. New rationale claims in
regenerated prose are quotable only from ATTESTED ledger rows.

## 7. Work queue and gates

Granularity: per-document (C4) or per-claim-family (others). An executor
claims an item by ticking it with its identity, appends ledger rows, commits
corrections, moves on. **GATE** = PI review before proceeding.

- [ ] **Phase 0 — scoping.** Enumerate the corpus: document list, estimated
  claim counts per class, cost per class (tokens + $ for Sol batch), and the
  proposed foreground/background split. Produces
  `reports/verification/phase0-scope.md`. **GATE 0**: PI approves scope,
  budget, and executor assignment.
- [ ] **Phase 1 — commitments and execution (C1, C2).** Build
  `results/commitments.json` from the lodged text (subsumes publishing the
  trigger census; five-element trigger rule: statistic, comparison scope,
  uncertainty criterion, evaluation moment, **evaluation corpus**). Run the
  execution→errata inverse census (every unlicensed factor level in
  `run-conditions.json` needs an erratum). Wire the open-commitment warning
  into `drift_check` (closes C3 of the guard via the append-only ledger).
  **GATE 1.**
- [ ] **Phase 2 — provenance (C3).** Field-level re-derivation of
  `passes-manifest.json` and `conditions-manifest.json` rows from raw
  metas/evals. Full enumeration (1,132 passes / 322 conditions — script job
  on sapphire, LLM only for discrepancy triage). **GATE 2.**
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
- [ ] **Phase 5 — monitoring.** `revalidate_ledgers.py`, coverage
  generation, drift-check integration, and the final coverage report
  stating verified classes and named residual (unswept or unverifiable)
  surfaces. **GATE 5**: PI signs the end-state.

Sequencing constraint: Phases 1–2 precede 3 (documents cite manifests;
manifests must be verified before they serve as anchors).

## 8. Executors and the cross-model layer

Any executor follows §§ 5–7. Assignment guidance (PI economics,
2026-07-28):

- **Deterministic scripts (sapphire)** — all recomputation, revalidation,
  coverage generation. Cheapest and most trustworthy; prefer whenever the
  check can be made mechanical.
- **Claude (Max plan)** — charter maintenance, orchestration, C6 tracing,
  reconstruct-and-diff, disagreement adjudication.
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

## 9. Resumption protocol

1. Read this charter top to bottom.
2. Read `reports/verification/coverage.md` (if absent, Phase 0 has not run).
3. Take the first unchecked, ungated queue item; honour every § 5 rule.
4. Append ledger rows; commit with messages referencing claim_ids; tick the
   item; push.
5. Stop at any GATE whose review is pending — gates belong to the PI.

## 10. Open items for PI review of this draft

1. Placement of gates — add/remove/merge as you see fit.
2. Phase 4 notes-file handling: appended correction notes vs one new Obs
   rider per family (obs-writer convention says new Obs).
3. Whether Phase 2 runs full-enumeration (recommended, script-led, cheap)
   or stratified.
4. Sol first-target confirmation (the Session-119 corrections) and the
   third-family choice for tiebreaks (Gemini is the obvious candidate but
   is also the *object* of study in this project — consider whether that
   matters for verification of cost/billing claims specifically).
5. Whether `reports/verification/` is the right home (alternative:
   `results/verification/`; charter assumes reports/).
