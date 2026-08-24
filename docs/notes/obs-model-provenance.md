---
priority: 3
scope: always
title: "Observation Model Provenance (DRAFT)"
audience: "researchers and future instances"
---

# Observation Register — Model Provenance Record

> **⚠ DRAFT — attribution boundaries pending PI confirmation against release dates.**
>
> **Correction (2026-08-22)**: this draft's "12-week transcript hole
> (2026-05-13 → 08-06)" and "no corroborating API model id for Opus
> 4.8" claims are artefacts of consulting the WRONG STORE. The agent
> followed this repo's (stale) archive documentation to the absent
> `archive/cc-sessions/` path and fell back to the per-machine LIVE
> transcript store, which is a partial population (sessions run on
> other machines are absent). The canonical archive
> (`~/cc-archives` / rpi-server) is healthy — ~850 sessions per
> machine, gzipped transcripts from ~Feb 2026, 0 missing (infra
> session audit, 2026-08-22). Consequences: the Opus 4.8 era and all
> MEDIUM/LOW-confidence attributions are upgradeable from the
> archived `.gz` transcripts; no data was lost; NO BACKFILL is
> needed or safe. Rule going forward: provenance work reads the
> canonical archive, never a live store. The repo's archive docs
> were repointed at the real location on 2026-08-22 (`703c28afc`).
> **The upgrade was EXECUTED on 2026-08-23 and CLOSED on 2026-08-24**
> (see [§ 4.1](#41-archive-based-re-grading-2026-08-23-session-140)):
> after a PI-ordered completeness re-verification (five grounds, all
> passed — § 4.1), the PI adopted the corrected 4.6→4.7 boundary at
> Obs 258 (§ 6.6). The census stands at **HIGH 380 · MEDIUM 48 ·
> LOW 0**; the era table, § 3, and § 4 carry the re-graded values.
> The document remains DRAFT only for the § 3
> `[PI to confirm: release date]` markers.
> Every switch boundary below is *derived from repository evidence only* (session transcripts,
> explicit prose statements, and git trailers). No model release date has been asserted from an
> instance's own background knowledge, because several of these releases post-date model training
> cutoffs and an invented date would seed exactly the class of confabulation this project has spent
> months clearing. Each boundary therefore carries a `[PI to confirm: release date]` marker. Do not
> cite this document as settled provenance until those markers are resolved.

**Created**: 2026-08-21. **Covers**: Observations 1–425 (428 headings) in
[`docs/notes/working-notes.md`](working-notes.md), as at commit `52df62c7d`.

---

## 1. Purpose and scope

The Observation register is the project's canonical findings log. Because the register was written
across nine months by a succession of different Claude models — and, at the start, by a
non-Claude agent — a reader who wants to weigh an entry needs to know which instance produced it.
This record supplies that mapping.

It is a **new, additive artefact**. Nothing in `working-notes.md`, the session log, the reflections
set, or git history has been rewritten to produce it, and nothing in them should be rewritten on the
strength of it. Where the evidence conflicts, the conflict is reported in [§ 6](#6-conflicts-and-register-defects),
not silently resolved.

### 1.1 Two models per entry, not one

Many Observations were drafted by a **subagent** dispatched from a session running a **different**
model. The project's standing subagent policy (global `CLAUDE.md`, "Subagent Model Policy") sends
mechanical work down-tier deliberately, so an entry can legitimately have:

- an **orchestrating session model** — the instance that did the analysis, held the context, and
  decided the finding was worth recording; and
- a **writing-agent model** — the instance that composed the register prose and committed it
  (typically the `obs-writer` agent).

The era table below attributes to the **orchestrating session model**, because that is the instance
whose reasoning produced the finding. Where a writing-agent model is separately determinable it is
recorded in [§ 5.3](#53-writing-agent-models-where-determinable).

---

## 2. Era table

Rows are grouped by contiguous model era, not by individual Observation. Confidence is defined in
[§ 4](#4-coverage-and-confidence). Obs counts are **headings**, which exceeds the count of distinct
Obs numbers by three because of the duplicate numbering defect in [§ 6.4](#64-three-duplicated-observation-numbers).

| Model (as named in-repo) | Sessions | Obs range | Date range | Principal evidence | Confidence |
|---|---|---|---|---|---|
| **Not Claude** — Antigravity IDE on Gemini 3 | pre-session-log ("Phase 1") | 1–47 (48 headings) | 2025-12-15 → 2025-12-21 | `archive/preliminary-work/ARCHIVE_MANIFEST.md`; `session-log.md:6731`; `session-reflection.md:8460`; zero `Co-Authored-By` trailers on any commit before 2025-12-23; no Claude Code transcript before 2025-12-22 | MEDIUM (48) |
| **Opus 4.5** (`claude-opus-4-5-20251101`) | pre-session-log → S18 | 48–101 (55) | 2025-12-23 → 2026-02-05 | transcript model id on essentially every working day; trailer `Claude Opus 4.5` from 2025-12-23 15:35 (`156a9f3e0`) | HIGH (55) |
| **Opus 4.6** (`claude-opus-4-6`) | S19 → S70 | 102–257 (157) | 2026-02-06 → 2026-04-18 (4.6-exclusive to 00:17 UTC; session `b089991e` ran on to 14:04 UTC) | transcript model id throughout via the canonical archive (§ 4.1); trailer `Claude Opus 4.6` / `Claude Opus 4.6 (1M context)`; boundary adopted at Obs 258 (§ 6.6, PI 2026-08-24) | HIGH (157) |
| **Opus 4.7** (`claude-opus-4-7`) | S71 → S91 (approx.) | 258–325 (68) | 2026-04-18 (from 00:17 UTC) → 2026-05-12 | archived transcript model id from 2026-04-18T00:17Z, unbroken to 05-12 (§ 4.1); trailers `Claude Opus 4 (1M context)` then `Claude Opus 4.7 (1M context)`; `session-log.md` S70–71 combined entry "Opus 4.7 was newly released at session start" (the second session of the pair) | HIGH (68) |
| **Opus 4.8** (`claude-opus-4-8`) | S91 → S110 (approx.) | 326–356 (31) | 2026-05-30 → 2026-06-09 | archived transcripts cover the era unbroken (§ 4.1; resolves § 6.3's id half); trailer `Claude Opus 4.8 (1M context)` from 2026-05-29; `session-reflection.md:9059` | HIGH (31) |
| **Fable 5** (`claude-fable-5`) — stint 1 | S111–S114 | 357–370 (14) | 2026-06-10 → 2026-06-13 | `session-log.md:7240`; `session-reflection.md:8926–8927`; continuity line 4; trailer `Claude Fable 5` from 2026-06-10 | HIGH (14) |
| **Opus 5** (`claude-opus-5`) — stint 1 | S118 | 371 (1) | 2026-07-27 | `session-reflection.md:9113–9114` "First session on Opus 5"; trailer `Claude Opus 5 (1M context)` | HIGH (1) |
| **Fable 5** — stint 2 | S119–S126 (Obs from S121–S125) | 372–387 (16) | 2026-07-30 → 2026-08-03 | continuity `[Session 119…126 CLOSED …; ran in Fable]`; `session-log.md:7481` | HIGH (16) |
| **Opus 5** — stint 2 (the "48-hour Opus window") | S127–S129 | 388–395, 398–400 (11) | 2026-08-04 → 2026-08-06 | `session-log.md:7914` "**Model**: Opus (first session of the 48-hour Opus window; Fable credit exhausted)"; `session-log.md:8010` "**Model**: Opus 5"; continuity `[Session 129 CLOSED 2026-08-06; ran in Opus]` | HIGH (11) |
| **Fable 5** — stint 3 | S130–S135 | 396–397, 401–415 (17) | 2026-08-10 → 2026-08-17 | continuity `[Session 130/132/133/134/135 CLOSED …; ran in Fable]`; `session-log.md:8580, 8584`; transcript model id 2026-08-10 | HIGH (17) |
| **Opus 5** — stint 3 | S136–S137 | 416–423 (8) | 2026-08-18 → 2026-08-19 | continuity `[Session 136 CLOSED 2026-08-19; ran on Opus 5]`, `[Session 137 CLOSED 2026-08-19; ran on Opus 5]` | HIGH (8) |
| **Fable 5** — stint 4 | S138–S139 | 424–425 (2) | 2026-08-20 → 2026-08-21 | transcript model id `claude-fable-5` on both days; continuity S138 paragraph | HIGH (2) |

**Interleaving is real, not noise.** From 2026-06-10 the eras stop being contiguous: Fable 5 became
the PI's preferred driver, with Opus-class sessions substituted whenever Fable credit was exhausted
(`session-log.md:8162` "Fable credit exhausted at session tail"; continuity line 297 "SESSION 136
RUNS ON A DIFFERENT MODEL (Fable credits exhausted)"). Any "era" framing after 2026-06-10 must be
read as *stints*, not a one-way switch.

---

## 3. Inferred switch boundaries — for PI confirmation

The following are **first-appearance dates in this repository**, not release dates. The PI switched
to each new model close to its release, so these should be within a day or so of the true release —
but that inference is his to confirm, and the record must not manufacture the dates.

| Transition | Last evidence of old model | First evidence of new model | Boundary sharpness |
|---|---|---|---|
| → **Opus 4.5** | — | transcript 2025-12-22; trailer 2025-12-23 15:35 (`156a9f3e0`) | Coincides with the "Phase 2 reset" from Antigravity to Claude Code. `[PI to confirm: release date]` |
| Opus 4.5 → **Opus 4.6** | trailer 2026-02-05; transcript 2026-02-06 (part-day) | transcript + trailer 2026-02-06 | Same-day handover, sharp. `[PI to confirm: release date]` |
| Opus 4.6 → **Opus 4.7** | archived session `b089991e`, `claude-opus-4-6` throughout its 2026-04-16T05:56 → 04-18T14:04 UTC span | archived transcript `claude-opus-4-7` from 2026-04-18T**00:17** UTC (10:17 AEST) | **ARCHIVE-RESOLVED to the minute** and PI-adopted 2026-08-24 (§ 6.6): the trailer flip at 04-17 20:20 AEST (`09fe46a7f`) preceded the model switch and is the record's outlier. Boundary Obs 258. `[PI to confirm: release date]` |
| Opus 4.7 → **Opus 4.8** | archived `claude-opus-4-7` sessions to 2026-05-29 | archived `claude-opus-4-8` from the 05-29 transition day; trailer `Claude Opus 4.8 (1M context)` 2026-05-29 **22:49** (`3a17575fd`) | Transcript-corroborated (the 2026-08-23 re-grade resolved § 6.3's "trailer-only" premise). `[PI to confirm: release date]` |
| Opus 4.8 → **Fable 5** | archived `claude-opus-4-8` to 2026-06-09 | archived `claude-fable-5` on the 06-10 transition day; trailer `Claude Fable 5` 2026-06-10 | Sharp, transcript-corroborated (the "store gap" was the wrong-store artefact). `[PI to confirm: release date]` |
| → **Opus 5** | — | archived `claude-opus-5` transcript 2026-07-27; trailer `Claude Opus 5 (1M context)` same day; `session-reflection.md:9113–9114` | Opus 5 **post-dates** Fable 5 in this project by ~7 weeks. `[PI to confirm: release date]` |

A ~5-week near-hiatus separates 2026-06-24 from 2026-07-26 (one commit, 2026-07-15). Whether a model
switch happened inside that window is unknowable from repo evidence.

---

## 4. Coverage and confidence

Confidence grades follow the brief:

- **HIGH** — an authoritative API model id recorded in a Claude Code session transcript covering that
  date, **or** an explicit prose statement of the session's model in the continuity file, session
  log, or session reflection.
- **MEDIUM** — consistent `Co-Authored-By` trailers on the introducing commit and its neighbours,
  with no higher-tier evidence available and no contradiction.
- **LOW** — no direct evidence; interpolated from the nearest evidence-anchored sessions on either
  side.

| Confidence | Headings | Share |
|---|---|---|
| HIGH | 380 | 88.8 % |
| MEDIUM | 48 | 11.2 % |
| LOW | 0 | 0 % |
| **Total** | **428** | **100 %** |

Basis breakdown: 366 headings rest on an archived transcript model id covering their introducing
commit (day-grain or commit-instant; § 4.1), 14 on explicit prose statements (the 8
concurrent-window headings of the 2026-08-04/06 credit-exhaustion overlap plus the 6
draft-then-accept divergences of § 6.5), and 48 — the pre-archive Antigravity era — on the
manifest-and-negative evidence of the § 2 table. No heading rests on trailers alone or on
interpolation.

> **History**: the 2026-08-21 census, graded from the (machine-partial) live store, read HIGH 210 /
> MEDIUM 203 / LOW 15 with 203 headings resting on trailers and 15 on interpolation. The
> canonical-archive re-grading (§ 4.1, 2026-08-23) and the PI's boundary adoption (§ 6.6,
> 2026-08-24) produced the census above.

### 4.1 Archive-based re-grading (2026-08-23, Session 140)

**Method.** Every non-agent `session.meta.json` in both archive names
(`~/cc-archives/map-reader-llm`, 204 entries; `~/cc-archives/vlm-burial-mound-detection`, 49) was
read into a session-span → `model_id` timeline; meta-versus-transcript agreement was verified on
8 sampled sessions spanning 2025-12 → 2026-08 (**8/8 exact**, single distinct assistant-turn model
each, subagent `progress` events correctly excluded). Each of the 428 Observation headings was
dated by `git blame` to its introducing commit (the file's 2026-05-29 rename is followed; the
duplicate-number renumberings surface as late dates and are handled below), then joined against the
timeline — at day grain first, and by commit **instant** against exact session spans on the five
model-transition days. Evidence artefacts:
`reports/provenance-archive-daymap-2026-08-23.md` (the day-map, verification table, and anomalies),
`reports/provenance-archive-timeline-2026-08-23.json` (253 records), and
`reports/provenance-obs-coverage-2026-08-23.json` (the per-heading join). The partition is exact —
357 + 15 + 8 + 48 = 428:

| Finding | Headings | Meaning |
|---|---|---|
| **archive-confirmed** | **357** | The introducing commit falls inside archived session span(s) of exactly one model, and that model agrees with the era table's attribution. Upgrade to **HIGH** (basis: archived transcript-grade model id). **All 15 LOW entries are in this set** — every one of their six dates (2026-03-25, 04-15, 04-24, 04-27, 04-28, 06-07) resolves to a single unambiguous model. |
| archive-conflict | 15 | The archive disagreed with the table's attribution for the WRITING session: Obs 249–257 (the era-boundary conflict — **RESOLVED 2026-08-24**: the PI adopted the Obs 258 boundary after the completeness re-verification below, moving the nine to archive-confirmed Opus 4.6, [§ 6.6](#66-the-4647-era-boundary-is-nine-observations-early)) and Obs 398–400, 421–423 (the draft-then-accept divergence of [§ 6.5](#65-other-trailer-versus-evidence-discrepancies-benign), transcript-corroborated — attribution to the producing session stands per § 1.1 on the continuity/session-log prose). Post-adoption partition: **366 archive-confirmed + 6 divergence + 8 concurrent + 48 pre-archive = 428**. |
| prior-evidence-stands | 8 | Obs 388–395: committed while Fable 5 and Opus 5 sessions ran **concurrently** (2026-08-04/06, the credit-exhaustion window), so the instant test cannot separate them. The session-log prose ("first session of the 48-hour Opus window") remains the operative HIGH evidence. |
| pre-archive | 48 | Obs 1–47 (Antigravity/Gemini 3): the archive starts 2025-12-22, after the era closed. MEDIUM stands on the manifest evidence. |

**Boundaries confirmed by the archive**: 4.5→4.6 at Obs 102 (2026-02-06, an abutting handover
06:24/06:25 UTC — Obs 102–108's commit instants all fall on the 4.6 side); 4.8→Fable 5 at Obs 357
(2026-06-10); and — resolving [§ 6.3](#63-opus-48-has-no-corroborating-api-model-id) — the whole
Opus 4.8 era 2026-05-30 → 06-09 is covered **unbroken** by `claude-opus-4-8` transcripts, so
"Opus 4.8" is corroborated by authoritative API model ids after all (the earlier "no coverage"
claim was the wrong-store artefact).

**Resulting census** (closed 2026-08-24 with the § 6.6 adoption): **HIGH 380 · MEDIUM 48 ·
LOW 0** — 366 archive-confirmed, 14 prose-anchored (8 concurrent-window + 6 divergence), 48
pre-archive Antigravity.

**Completeness re-verification (2026-08-24, ordered by the PI before adopting the boundary).**
Five independent grounds, all passed: (i) the canonical union on rpi-server and the local mirror
hold IDENTICAL entry populations for both archive names (205 + 49 directories each side), with the
completeness gate (`~/.cache/cc-archives-gate`) reading 0 and the archive catalogue (rebuilt
2026-08-23 22:14, after the archiving-system repair converged) deduplicating to the same 230
sessions; (ii) **the session log is an independent record of which days had sessions at all, and
none of its 120 dated entries falls inside any archive no-evidence window** — the gaps (including
the 33-day 2026-06-24 → 07-26 window) are genuine no-work periods matching the known travel
breaks, not missing transcripts; (iii) every Claude-era Obs heading (380 of 428) falls on an
archive-covered day — the no-coverage class is exactly the 48 pre-archive Antigravity headings;
(iv) meta-versus-transcript agreement held 8/8 on the sampled sessions; (v) at the boundary
specifically, three record types cohere — the archive (4.6-exclusive until 04-18T00:17Z), the
session log (the combined S70–71 entry's "Opus 4.7 was newly released at session start" reading
naturally as the second session of the pair, whose S71 confabulation observation implies real 4.7
use on the 18th), and git — whose trailer flip at 04-17 20:20 AEST is thereby identified as the
outlier, a CLI self-report that changed ahead of the model.

**The former 15 LOW entries — all resolved to HIGH by the archive** (each of their six dates
carries unambiguous single-model transcript coverage; § 4.1): Obs 186–193 (2026-03-25, Opus 4.6),
Obs 236–237 (2026-04-15, Opus 4.6), Obs 276–277 (2026-04-24), Obs 290 (2026-04-27), Obs 295
(2026-04-28, all Opus 4.7), and Obs 349 (2026-06-07, Opus 4.8).

---

## 5. Session → model evidence appendix

### 5.1 Explicit prose statements (HIGH-tier evidence)

Every statement below was re-read at its cited line during compilation.

| Session | Statement | Source |
|---|---|---|
| S111–112 | "One continuous conversation (first Fable 5 session on this project)" | `docs/notes/reflections/session-log.md:7240` |
| S111–112 | "the first on this project run by Fable 5 rather than Opus 4.x" | `docs/notes/reflections/session-reflection.md:8926–8927` |
| S111–112 | "One continuous conversation, first Fable 5 session." | `planning/paper-writeup-continuity.md:4` (Sessions 111–112 paragraph) |
| S114–117 | "a user crash mid-way, a model switch to Opus 4.8" | `docs/notes/reflections/session-reflection.md:9059` |
| S118 | "First session on Opus 5." | `docs/notes/reflections/session-reflection.md:9113–9114` |
| S118 | "[Session 118 CLOSED 2026-07-28; ran in Fable]" | `planning/paper-writeup-continuity.md:1751` — **conflicts with the line above** |
| S119 | "First Fable session, convened for a cross-model second opinion on the Session-118 audit." | `docs/notes/reflections/session-log.md:7481` |
| S119 | "Written by the primary instance (Fable 5 — the first Fable session deliberately convened as a cross-model second opinion on an Opus audit)." | `docs/notes/reflections/session-reflection.md:9178–9180` |
| S119 | "[Session 119 CLOSED 2026-07-29; runs in **Fable**, Claude driving]" | `planning/paper-writeup-continuity.md:1715` |
| S120–S126 | "ran in Fable" | `planning/paper-writeup-continuity.md:1649, 1575, 1494, 1410, 1282, 1047, 899` |
| S127 | "**Model**: Opus (first session of the 48-hour Opus window; Fable credit exhausted)" | `docs/notes/reflections/session-log.md:7914` |
| S127 | "First Opus session of the 48-hour window." | `docs/notes/reflections/session-reflection.md:9588` |
| S128 | "**Model**: Opus 5." | `docs/notes/reflections/session-log.md:8010` |
| S129 | "[Session 129 CLOSED 2026-08-06; ran in Opus]" | `planning/paper-writeup-continuity.md:814` |
| S130, S132, S133, S134 | "ran in Fable" | `planning/paper-writeup-continuity.md:734, 580, 484, 380` |
| S134 | "the session ran in Fable" | `docs/notes/reflections/session-log.md:8580` |
| S135 | "One continuous Fable session (amd-tower + sapphire)" | `docs/notes/reflections/session-log.md:8584` |
| S135 → S136 | "ran in Fable — SESSION 136 RUNS ON A DIFFERENT MODEL (Fable credits exhausted)" | `planning/paper-writeup-continuity.md:297` |
| S136, S137 | "ran on Opus 5" | `planning/paper-writeup-continuity.md:166, 82` |
| S138 | "first Fable session" | `planning/paper-writeup-continuity.md:114` — **conflicts, see § 6.1** |
| S138 | "First session of this project on Fable" | `docs/notes/reflections/session-reflection.md:10516` — **conflicts, see § 6.1** |
| Phase 1 | "the earliest work was done in Google's Antigravity IDE on Gemini 3 … that self-misidentification contaminated the repo before he switched to Opus in Claude Code" | `docs/notes/reflections/session-reflection.md:8458–8461`; corroborated at `session-log.md:6729–6732` |

### 5.2 Session transcript evidence (HIGH-tier, authoritative model ids)

The archiving specification (`docs/methodology/transparency/cc-session-archiving-specification.md`
§ 2.1, § 4) defines `archive/cc-sessions/` with per-session `session.meta.json` carrying
`model.model_id` and `model.model_version`. **That directory does not exist in the working tree** —
`.gitignore` excludes both `archive/cc-sessions/*.jsonl` (line 20) and `archive/cc-sessions/`
(line 176), and no `CATALOG.json` is present. The specified per-session model metadata was therefore
unavailable for this compilation.

The substitute source is the live Claude Code transcript store at
`~/.claude/projects/-home-shawn-Code-map-reader-llm/` — 160 session `*.jsonl` files plus 605
subagent `*/subagents/*.jsonl` files, ~1.3 GB. Each assistant turn records the API model id, and
`*/subagents/*.meta.json` records `agentType` and (where set) the agent's model alias. **This store
is outside the repository, is not version-controlled, and rotates**; the coverage gaps below are
gaps in that store, not evidence of inactivity.

Distinct model ids observed, with their in-repo coverage:

| API model id | Role | Dates covered by surviving transcripts |
|---|---|---|
| `claude-opus-4-5-20251101` | session + subagent | 2025-12-22 → 2026-02-06 |
| `claude-opus-4-6` | session + subagent | 2026-02-06 → 2026-04-14 |
| `claude-opus-4-7` | session + subagent | 2026-04-18 → 2026-05-12 |
| `claude-fable-5` | session | 2026-08-07 → 2026-08-10, 2026-08-20 → 2026-08-21 |
| `claude-opus-5` | subagent | 2026-08-20 → 2026-08-21 |
| `claude-sonnet-4-5-20250929` | session + subagent | 2025-12-22 → 2026-02-11 |
| `claude-sonnet-4-6` | subagent | 2026-05-06, 2026-05-12 |
| `claude-sonnet-5` | subagent | 2026-08-20 → 2026-08-21 |
| `claude-haiku-4-5-20251001` | session + subagent | 2026-01-12 → 2026-05-06 |

Transcript coverage gaps (no surviving transcript): 2026-02-17 → 2026-03-06; 2026-03-12 → 2026-03-16;
2026-03-18 → 2026-04-06; 2026-04-15 → 2026-04-17; 2026-04-19 → 2026-05-03; **2026-05-13 → 2026-08-06**
(the largest, ~12 weeks); 2026-08-11 → 2026-08-19.

### 5.3 Writing-agent models, where determinable

| Obs | Orchestrating session model | Writing-agent model | Evidence |
|---|---|---|---|
| 313–316, 319, 321, 325–327, 330–337, 340–348, 351–353, 357–368 (41 entries) | Opus 4.7 (7), Opus 4.8 (22), Fable 5 (12) | **Sonnet 4.6** (`obs-writer`) | Introducing-commit trailer `Claude Sonnet 4.6`, 2026-04-30 → 2026-06-13; corroborated by `claude-sonnet-4-6` subagent turns in the 2026-05-06 and 2026-05-12 transcripts |
| 381, 386–387, 415 | Fable 5 | **Opus 5** (subagent) | Introducing-commit trailer `Claude Opus 5 (1M context)` on days whose sessions are explicitly Fable |
| 424, 425 | **Fable 5** (`claude-fable-5`, transcript-confirmed 2026-08-21) | **Sonnet 5** (`claude-sonnet-5`) | `obs-writer` subagent transcripts `agent-afceec8a7ecab1cc9.jsonl` (Obs 424, 69 turns) and `agent-ab000b08b12355656.jsonl` (Obs 425, 84 turns), both recording `"model":"claude-sonnet-5"`; their `.meta.json` records `agentType: obs-writer` |

For the 2026-07-30 → 2026-08-03 block the writing-agent model is **not** determinable: the trailers
are corrupt (see [§ 6.2](#62-fourteen-observations-carry-a-stale-opus-47-trailer)) and no transcripts
survive for those dates.

---

## 6. Conflicts and register defects

### 6.1 Three mutually exclusive "first Fable session" claims

The repository asserts, in five places, that three *different* sessions were the first Fable session.

| Claim | Session | Date | Source |
|---|---|---|---|
| "first Fable 5 session on this project" | **S111–112** | 2026-06-10/11 | `session-log.md:7240`; `session-reflection.md:8926–8927`; `paper-writeup-continuity.md:4` |
| "First Fable session, convened for a cross-model second opinion" | **S119** | 2026-07-28/29 | `session-log.md:7481`; `session-reflection.md:9178–9180` |
| "first Fable session" / "First session of this project on Fable" | **S138** | 2026-08-20/21 | `paper-writeup-continuity.md:114`; `session-reflection.md:10516` |

**Not resolved here.** For the PI's adjudication, the independent evidence is:

- The first `Claude Fable 5` commit trailer anywhere in the repository is **2026-06-10**, inside
  S111–112. Thirty-eight Fable-trailered commits land that day.
- The S119 claim is qualified in both its sources by "*deliberately convened as a cross-model second
  opinion*", which reads naturally as "first Fable session **of the verification programme**" rather
  than an absolute first. It follows a ~5-week near-hiatus (2026-06-24 → 2026-07-26).
- The S138 claim carries no such qualifier and is the hardest to reconcile: `claude-fable-5` appears
  in surviving transcripts from **2026-08-07**, and continuity records Fable sessions from S119
  onward, both preceding S138 by weeks.
- A plausible mechanism, offered as a hypothesis only: each was written by an instance that could
  see its own session but not the earlier ones, and "first Fable session" was reconstructed from
  local context rather than checked at source. That is the same failure shape the register itself
  documents at Obs 423 and Obs 424.

### 6.2 Fourteen Observations carry a stale `Opus 4.7` trailer

The brief named two corrupt commits. There are **thirteen**, spanning two separate windows; twelve
of them introduce **fourteen** Observations (12 of the 215 Obs-introducing commits, 5.6 %). All carry `Co-Authored-By: Claude Opus 4.7 (1M context)` while
the session was, on explicit prose evidence, Fable 5 — the trailer is inherited from an agent
template, not observed.

| Commit | Date | Obs introduced |
|---|---|---|
| `039444c20` | 2026-07-30 | 372, 373 |
| `a8ef637c1` | 2026-07-30 | 374 |
| `b598b6887` | 2026-07-31 | 375 |
| `78f9e442b` | 2026-07-31 | 376 |
| `00420b076` | 2026-08-01 | 377 |
| `986570268` | 2026-08-01 | 378, 379 |
| `b46c59fc0` | 2026-08-01 | 380 |
| `1bdbca86e` | 2026-08-02 | 382 |
| `ac10b6074` | 2026-08-02 | 383 |
| `b82905374` | 2026-08-03 | 385 |
| `a6588fb55` | 2026-08-21 | 424 (named in the brief) |
| `349cdd1b6` | 2026-08-21 | 425 (named in the brief) |
| `43d066a64` | 2026-08-21 | — (non-Obs commit, same corruption) |

The 2026-08-21 pair is directly falsified by transcript evidence: the session model that day was
`claude-fable-5` and the writing agents were `claude-sonnet-5`. Neither is Opus 4.7. The
2026-07-30 → 2026-08-03 block cannot be falsified the same way (no surviving transcripts) but shares
the signature and sits inside sessions the continuity file states ran in Fable.

**Consequence for the trust order**: git trailers were demoted to corroborative-only for this
compilation, as instructed. They were nonetheless the *sole* evidence for 203 of 428 headings
(47.4 %), because the transcript store does not cover those dates. Those attributions inherit the
trailer mechanism's fragility.

### 6.3 "Opus 4.8" has no corroborating API model id

`Claude Opus 4.8 (1M context)` appears in 2026-05-29 → 2026-06-23 trailers and in prose
(`session-reflection.md:9059`), and is the sole basis for attributing Obs 326–356. But the transcript
store has **no coverage at all** between 2026-05-13 and 2026-08-06, and no `claude-opus-4-8` string
occurs anywhere in the reachable evidence. The label rests entirely on self-report.
`[PI to confirm: that "Opus 4.8" names a real model he used, and its release date]`

**RESOLVED 2026-08-23** ([§ 4.1](#41-archive-based-re-grading-2026-08-23-session-140)): the
"no coverage" premise was the wrong-store artefact this draft's header corrects. The canonical
archive covers 2026-05-30 → 06-09 unbroken with `claude-opus-4-8` API model ids
(meta-and-transcript verified on `2026-06-07T05-16_establish-two-reference-generalisation`), with
clean transition days on 05-29 (from 4.7) and 06-10 (to Fable 5). "Opus 4.8" is a real model id,
not a self-report — only the release-date confirmation remains for the PI.

### 6.4 Three duplicated Observation numbers

`working-notes.md` contains 428 `## Observation N` headings but only 425 distinct numbers.

| Number | First use | Second use |
|---|---|---|
| 45 | line 218, 2025-12-20, "Two-Stage Redemption (v4.6)" | line 708, 2025-12-21, "The Flash Swarm Paradox (Image-Only Collapse)" |
| 66 | line 989, 2026-01-26, "Univariate Experimental Discipline" | line 1422, 2026-02-01, "Silent Test Failures and Propagation Debt" |
| 234 | line 9142, 2026-04-14 | line 9196, 2026-04-14 (near-identical H10/H12 pool-sweep title) |

Both members of each pair fall inside the same era, so the defect does not change any attribution.
It is recorded because a future citation of "Obs 45" or "Obs 66" is ambiguous. Note that Obs 234 is
covered by the E48/Obs 235 retraction, and Obs 45 already carries a 2026-06-05 erratum banner.

### 6.5 Other trailer-versus-evidence discrepancies (benign)

- **Obs 243–248** (2026-04-17, morning) carry `Claude Opus 4.6 (1M context)`; **Obs 249–252**
  (same calendar day, evening) carry `Claude Opus 4 (1M context)`. This is the switch itself, not
  corruption — the era boundary is placed between them.
- **`Claude Opus 4 (1M context)`** is used from 2026-04-17 20:20 to 2026-04-19 00:00, then replaced
  by `Claude Opus 4.7 (1M context)`. Read as an incomplete self-name during the first ~28 hours on
  the new model, corroborated by `claude-opus-4-7` in the 2026-04-18 transcripts.
- **Obs 398–400 and 421–423** are attributed to Opus 5 (their headings name S129 and S137) but were
  *committed* in later Fable sessions — Obs 421–423 are explicitly headed "(Session 137, 2026-08-19;
  accepted 2026-08-21)". This is the register's normal draft-then-accept workflow: **produced by one
  model, minted by another**. The table attributes to the producing session, per § 1.1.
  *Archive corroboration (2026-08-23)*: the introducing commits (`bc7301fac` 2026-08-14,
  `dc869b24f` 2026-08-21) fall inside `claude-fable-5` archived sessions, transcript-grade —
  exactly as this bullet inferred. The producing-session attribution stands.
- **Obs 1–47** were committed by `Shawn Ross` with a second human contributor (`adivea`) also active
  on 2025-12-17. The register is not a single-agent artefact even in its earliest layer.

---

### 6.6 The 4.6→4.7 era boundary is nine Observations early

**Surfaced by the 2026-08-23 archive re-grading** ([§ 4.1](#41-archive-based-re-grading-2026-08-23-session-140)).
The era table starts Opus 4.7 at Obs 249, "2026-04-17 (from ~20:20 AEST)" — a timestamp that turns
out to be the **commit clock of `09fe46a7f`** (2026-04-17T20:20:23+10:00), the commit introducing
Obs 249–252 under the ambiguous `Claude Opus 4 (1M context)` trailer that § 6.5 read as an
incomplete self-name on the new model. The canonical archive contradicts that reading: at that
instant (10:20 UTC) — and at `857d5f714`'s (Obs 253–255, 14:17 UTC), and at the commit instants of
Obs 256–257 early on 04-18 — the **only archived session running is
`2026-04-16T05-56_b089991e`, `claude-opus-4-6` throughout** (span 04-16T05:56 → 04-18T14:04 UTC).
The first `claude-opus-4-7` session starts 2026-04-18T00:17 UTC, and the first headings whose
commit instants fall in 4.7-exclusive time are **Obs 258–259**. On the archive's evidence the
trailer changed BEFORE the model did, and the corrected boundary is: **Opus 4.6 era extends
through Obs 257; Opus 4.7 begins at Obs 258** (first 4.7 session 2026-04-18T00:17 UTC =
10:17 AEST). Nine headings (249–257) would move 4.7 → 4.6, each then transcript-grade HIGH.

*Caveat*: this assumes the introducing commits came from an archived session of this project — the
archive audit reports 0 missing sessions, and no 4.7 session exists anywhere in either archive name
before 04-18T00:17Z, but a session archived under an unrelated project name would be invisible to
the sweep.

**ADOPTED (PI, 2026-08-24)** — after the archiving-system repair had converged and the
completeness re-verification recorded in § 4.1 passed on all five grounds (canonical = mirror,
gate 0; no logged session in any archive gap; every Claude-era heading on a covered day; 8/8
transcript sampling; three-record coherence at the boundary, with the git trailer identified as
the outlier). The era table, § 3, and § 4 now carry the Obs 258 boundary; Obs 249–257 are
archive-confirmed Opus 4.6.

## 7. How to finalise

1. **PI confirms the switch boundaries** in [§ 3](#3-inferred-switch-boundaries--for-pi-confirmation)
   against actual release dates, resolving each `[PI to confirm: release date]` marker. Where a
   release date and the repo's first-appearance date differ by more than a day or two, the era
   boundary should move to whichever the PI judges correct, and the reason should be noted inline.
2. **PI adjudicates the three "first Fable session" claims** ([§ 6.1](#61-three-mutually-exclusive-first-fable-session-claims)).
   Because the register and the reflections set are append-only, the correction belongs in a
   *new* rider entry — not an edit to the three original statements.
3. **PI rules on "Opus 4.8"** ([§ 6.3](#63-opus-48-has-no-corroborating-api-model-id)) — as of
   2026-08-23 only the release-date half remains; the model id is archive-corroborated.
4. **PI rules on the corrected 4.6→4.7 boundary** ([§ 6.6](#66-the-4647-era-boundary-is-nine-observations-early)):
   adopting Obs 258 re-attributes Obs 249–257 to Opus 4.6 at transcript-grade confidence and
   closes the census at HIGH 380 · MEDIUM 48 · LOW 0 ([§ 4.1](#41-archive-based-re-grading-2026-08-23-session-140)).
5. **Drop the DRAFT banner** and replace it with a `**Last revised**` line once 1–4 are settled.
6. **Optionally mint a closing Observation** recording the attribution exercise itself — the
   findings worth carrying are that a nine-month register spans seven authoring configurations
   including a non-Claude one; that commit trailers were the sole evidence for 47 % of entries and
   are demonstrably corrupt in 12 of the 215 Obs-introducing commits (5.6 %); and that the specified
   `archive/cc-sessions/` model metadata was never materialised, leaving an unversioned, rotating
   transcript store as the only authoritative source.
7. **Consider a forward fix**: the archiving specification already requires `model.model_version` per
   session. Materialising even a minimal `session.meta.json` per session — model id, date, session
   number — would make this record cheap to maintain and would not depend on trailers at all.

---

## 8. Method and reproducibility

- **Obs → (session, date) map**: all 428 `## Observation N` headings parsed from
  `docs/notes/working-notes.md`. 373 headings carry an explicit date; the remaining 55 were dated
  from `git blame --line-porcelain -M -C` on the heading line (the introducing commit), which also
  supplied each entry's `Co-Authored-By` trailer. Session numbers, where absent from the heading,
  were taken from `docs/notes/reflections/session-log.md` (Sessions 4–138 with dates).
- **Session → model table**: explicit prose statements ([§ 5.1](#51-explicit-prose-statements-high-tier-evidence));
  API model ids from the transcript store ([§ 5.2](#52-session-transcript-evidence-high-tier-authoritative-model-ids));
  trailers as corroboration only.
- **Join rule**: explicit statement → transcript id → trailer → interpolation, in that order, with
  the confidence grade set by whichever tier supplied the answer.
- **Not consulted**: the compiling instance's own background knowledge of model release dates.
- **Nothing was modified.** This file is the only artefact created.
