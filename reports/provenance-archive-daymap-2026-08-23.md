# Archive model day-map — provenance evidence for the Observation register

> **Last revised**: 2026-08-23 (original publication). See
> [§ Changelog](#changelog) for revision history.

**What this is.** The canonical-archive evidence base for upgrading the
MEDIUM/LOW-confidence attributions in
`docs/notes/obs-model-provenance.md`, produced in Session 140 per the
Session 139 queue ("provenance finalisation from the canonical
`~/cc-archives` store only"). Extraction ran read-only over both archive
names (`map-reader-llm`, 204 entries; `vlm-burial-mound-detection`, 49)
by a Sonnet-tier subagent; the day-map below is its § (a)–(d) output
verbatim. Companion artefacts:
`reports/provenance-archive-timeline-2026-08-23.json` (253 records, one
per archive entry) and
`reports/provenance-obs-coverage-2026-08-23.json` (the 428-heading
join). Meta-vs-transcript agreement was verified on 8 sampled sessions
(8/8 exact, single distinct assistant-turn model each; see § (c)).

---

## Archive Model Day-Map — map-reader-llm / vlm-burial-mound-detection

Read-only extraction over `~/cc-archives/map-reader-llm` (204 entries, excluding
the nested stale-duplicate directory described in § Anomalies) and
`~/cc-archives/vlm-burial-mound-detection` (49 entries) — the two archive
names under which this project's Claude Code sessions are stored. Source
data: `archive-model-timeline.json` (253 records, one per entry directory,
built by `build_timeline.py`). All times are UTC as recorded in
`session.meta.json`.

Scope note: sections (a) and (b) use **non-agent** entries only (`is_agent:
false`), since agent (subagent) transcripts do not represent the
project's "which model was I actually talking to" timeline in the same
sense — a subagent can run on a different tier by design (see the user's
Subagent Model Policy). Agent entries are counted in § Anomalies and in the
raw JSON but excluded from the day-level model map.

### (a) Day-level model coverage

Contiguous runs of calendar days on which the *set* of models found in any
non-agent session's `[started_at, ended_at]` span is unchanged. A day
showing two models is a same-day model-transition day (the transition
happened partway through that day, mid-session-chain). A gap row marks a
span with **no archived session evidence at all** (agent or non-agent) in
either archive name.

| Date range | Days | Model(s) present | Note |
|---|---|---|---|
| 2025-12-22 → 2026-01-27 | 37 | claude-opus-4-5-20251101 | earliest archived session: `map-reader-llm/2025-12-22T03-05_6c7214f9` |
| 2026-01-28 → 2026-01-30 | 3 | — no session evidence — | gap |
| 2026-01-31 → 2026-02-05 | 6 | claude-opus-4-5-20251101 | |
| 2026-02-06 | 1 | claude-opus-4-5-20251101 + claude-opus-4-6 | transition day (4-5→4-6 switch ~06:25 UTC) |
| 2026-02-07 → 2026-02-17 | 11 | claude-opus-4-6 | |
| 2026-02-18 → 2026-03-06 | 18 | — no session evidence — | gap |
| 2026-03-07 → 2026-03-11 | 5 | claude-opus-4-6 | |
| 2026-03-12 → 2026-03-13 | 2 | — no session evidence — | gap |
| 2026-03-14 → 2026-04-02 | 20 | claude-opus-4-6 | |
| 2026-04-03 → 2026-04-06 | 4 | — no session evidence — | gap |
| 2026-04-07 → 2026-04-17 | 11 | claude-opus-4-6 | |
| 2026-04-18 | 1 | claude-opus-4-6 + claude-opus-4-7 | transition day |
| 2026-04-19 → 2026-05-12 | 24 | claude-opus-4-7 | unbroken run |
| 2026-05-13 → 2026-05-22 | 10 | — no session evidence — | gap |
| 2026-05-23 → 2026-05-28 | 6 | claude-opus-4-7 | mirrored in both archive names from this point (see § Anomalies) |
| 2026-05-29 | 1 | claude-opus-4-7 + claude-opus-4-8 | transition day |
| 2026-05-30 → 2026-06-09 | 11 | claude-opus-4-8 | unbroken run |
| 2026-06-10 | 1 | claude-opus-4-8 + claude-fable-5 | transition day |
| 2026-06-11 → 2026-06-23 | 13 | claude-fable-5 | |
| 2026-06-24 → 2026-07-26 | 33 | — no session evidence — | large gap |
| 2026-07-27 | 1 | claude-opus-5 | project-identity-fork session (see § Anomalies) |
| 2026-07-28 | 1 | claude-fable-5 + claude-opus-5 | transition day; also the day `map-reader-llm` archiving stops entirely |
| 2026-07-29 → 2026-08-02 | 5 | claude-fable-5 | archived under `vlm-burial-mound-detection` only from here on |
| 2026-08-03 → 2026-08-06 | 4 | claude-fable-5 + claude-opus-5 | overlapping/concurrent sessions, not a same-day handover (see § Anomalies) |
| 2026-08-07 → 2026-08-17 | 11 | claude-fable-5 | |
| 2026-08-18 → 2026-08-19 | 2 | claude-opus-5 | standalone top-level (non-agent) opus-5 sessions |
| 2026-08-20 → 2026-08-22 | 3 | claude-fable-5 | last day with archived evidence at time of writing |

### (b) Explicit window and single-date coverage

#### Window 2026-02-06 → 2026-04-17

Every day in this window with archived evidence shows **claude-opus-4-6**,
except the opening day (2026-02-06), which is the transition day from
claude-opus-4-5-20251101 to claude-opus-4-6 (opus-4-5 sessions end
~06:24 UTC that day; opus-4-6 sessions begin ~06:25 UTC). No opus-4-7
evidence appears anywhere in this window — the next model, opus-4-7, first
appears the day *after* this window closes (2026-04-18). Three gaps fall
inside the window with no archived session evidence: 2026-02-18→03-06 (18
days), 2026-03-12→03-13 (2 days), 2026-04-03→04-06 (4 days) — 24 of the
window's 71 days (34%) have no archive coverage either way.

#### Window 2026-04-17 → 2026-05-12

2026-04-17 itself is still **claude-opus-4-6** (the session
`2026-04-16T05-56_b089991e` spans 04-16→04-18 and is opus-4-6 throughout).
2026-04-18 is the transition day (opus-4-6 session `b089991e` overlaps
briefly with the first opus-4-7 session, `2026-04-18T00-17_resolve-git-sync-issues-and-clear-stale`,
which starts 00:17 UTC while `b089991e` doesn't end until 14:04 UTC the
same day). From 2026-04-19 through the end of the window (2026-05-12),
coverage is **claude-opus-4-7** with no gaps — a clean, unbroken 24-day
run.

#### Window 2026-05-30 → 2026-06-09

Entirely **claude-opus-4-8**, no gaps, no mixed days, no ambiguity. Every
non-agent session touching this window is mirrored identically under both
`map-reader-llm` and `vlm-burial-mound-detection` (see § Anomalies).

#### Individual dates

| Date | Model | Evidence |
|---|---|---|
| 2026-03-25 | claude-opus-4-6 | `2026-03-24T09-55_complete-384px-consensus-sweeps-audit-run` (spans into 03-25) and `2026-03-25T06-02_complete-proposer-verifier-pipeline-sweeps` (starts 03-25); both opus-4-6. The latter is transcript-verified (sample 3, § c) — single distinct assistant-turn model. |
| 2026-04-15 | claude-opus-4-6 | Three consecutive sessions cover the day (`2026-04-14T13-21…`, `2026-04-15T07-08…`, `2026-04-15T12-42…`), all opus-4-6. |
| 2026-04-24 | claude-opus-4-7 | `2026-04-23T11-07…` (spans into 04-24) and `2026-04-24T05-29_establish-image-track-proposer-verifier-f1` (starts 04-24); both opus-4-7. The latter is transcript-verified (sample 4, § c). |
| 2026-04-27 | claude-opus-4-7 | `2026-04-25T00-16…` (spans into 04-27) and `2026-04-27T02-10_complete-55-map-generalisation-analysis-grid` (starts 04-27); both opus-4-7. |
| 2026-04-28 | claude-opus-4-7 | Fully inside the span of `2026-04-27T02-10_complete-55-map-generalisation-analysis-grid` (04-27→04-30), opus-4-7. |
| 2026-06-07 | claude-opus-4-8 | Three sessions cover the day (`2026-06-06T00-51…`, `2026-06-07T05-16_establish-two-reference-generalisation`, `2026-06-07T12-40…`), each mirrored in both archive names (6 entries total), all opus-4-8. The middle one is transcript-verified (sample 6, § c). |

All six requested dates resolve to a **single, unambiguous model** in the
archive — no date in this list falls inside a transition day or a
no-evidence gap.

### (c) Transcript verification (8 sampled non-agent sessions)

Method: `zcat session.jsonl.gz` piped directly into a small Python scanner
(`scan_transcript_models.py`) — no file was decompressed to disk. The
scanner distinguishes genuine main-session assistant turns
(`type: "assistant"`, model read from `message.model`) from model ids
nested inside `type: "progress"` events, which report a **subagent's**
(Task-tool) own turns streamed live into the parent transcript. A naive
`grep -o '"model":"claude-...'` conflates the two — see the note on
sessions 2 and 3 below.

| # | Archive / entry | Meta `model_id` | Transcript assistant-turn model(s) (count) | Match? | Notes |
|---|---|---|---|---|---|
| 1 (earliest) | map-reader-llm / `2025-12-22T03-05_6c7214f9` | claude-opus-4-5-20251101 | claude-opus-4-5-20251101 (1746) | Yes | Single distinct model; no subagent progress events. |
| 2 (2026-02) | map-reader-llm / `2026-02-01T11-43_abe6f808` | claude-opus-4-5-20251101 | claude-opus-4-5-20251101 (303) | Yes | Main session single-model. Nested subagent `progress` events additionally show claude-haiku-4-5-20251001 (184) and claude-opus-4-5-20251101 (99) — these are Task-tool subagents, not main-session turns; a raw grep on the whole file would wrongly report 2 distinct models. |
| 3 (2026-03) | map-reader-llm / `2026-03-25T06-02_complete-proposer-verifier-pipeline-sweeps` | claude-opus-4-6 | claude-opus-4-6 (862) | Yes | Same pattern as #2: nested subagent progress shows claude-haiku-4-5-20251001 (206) and claude-opus-4-6 (68), not main-session turns. |
| 4 (2026-04) | map-reader-llm / `2026-04-24T05-29_establish-image-track-proposer-verifier-f1` | claude-opus-4-7 | claude-opus-4-7 (693) | Yes | Single distinct model; no subagent progress events. |
| 5 (2026-05) | map-reader-llm / `2026-05-06T14-41_audit-and-patch-documentation-before-paper` | claude-opus-4-7 | claude-opus-4-7 (284) | Yes | Two additional `type: "assistant"` lines carry `message.model: "<synthetic>"` — confirmed (by inspecting the raw records) as Claude Code's internal zero-token "No response requested." placeholder, not a real model call and not a `claude-*` id, so not counted as a second distinct model. |
| 6 (2026-06) | map-reader-llm / `2026-06-07T05-16_establish-two-reference-generalisation` | claude-opus-4-8 | claude-opus-4-8 (510) | Yes | Single distinct model; no subagent progress events. |
| 7 (2026-08, a) | vlm-burial-mound-detection / `2026-08-01T05-21_refuse-silent-fallback-repair-pathless` | claude-fable-5 | claude-fable-5 (555) | Yes | Single distinct model. |
| 8 (2026-08, b) | vlm-burial-mound-detection / `2026-08-19T01-04_filing-of-erratum-e82-10k-bootstrap` | claude-opus-5 | claude-opus-5 (1049) | Yes | Single distinct model. This session is one of the standalone top-level opus-5 sessions flagged in § Anomalies; the transcript confirms it is genuinely opus-5 throughout, consistently with its own metadata — not a mislabelled subagent or stray meta value. |

**Flag check**: none of the eight sampled sessions' *main-session assistant
turns* contain more than one distinct `claude-*` model id. All eight
meta `model_id` values match their transcripts exactly. The only
multi-model signal found (sessions 2 and 3) comes from nested subagent
progress events, which is expected behaviour, not a data-integrity
problem — but it does mean a metadata-only or raw-grep audit would
under- or over-count model usage depending on whether it separates
assistant turns from subagent progress.

### (d) Anomalies

1. **Nested stale-duplicate directory**: `~/cc-archives/map-reader-llm/vlm-burial-mound-detection`
   contains 149 entry directories (dated 2025-12-22 → 2026-05-06). Every
   one of these 149 entries' `session.meta.json` → `session.id` matches a
   session that also exists as a **top-level** entry directly under
   `~/cc-archives/map-reader-llm` (confirmed programmatically: 149/149
   matched, 0 unmatched). A spot check on the earliest pair
   (`2025-12-22T03-05_6c7214f9` top-level vs.
   `2025-12-22T03-05_vlm-pipeline-development-and-codebase` nested) found
   identical `session.id`, `started_at`, `ended_at`, and `model` block, but
   the **decompressed transcripts differ**: the nested copy has 2,806
   lines vs. 2,807 in the top-level copy, and different content
   checksums. The top-level copy also carries a `subagents/` subdirectory
   and an extra `subagents` key in its meta.json that the nested copy
   lacks. This is consistent with the nested directory being a
   pre-consolidation snapshot, superseded by the (fuller) top-level copy —
   matching the project `CLAUDE.md` note that a consolidation on
   2026-05-21 resolved an older `archive/cc-sessions/` location into the
   canonical store. **This nested directory was excluded from
   `archive-model-timeline.json`** to avoid double-counting; it is
   reported here only per the task's request to investigate it.

2. **Cross-archive mirroring (the "project identity fork")**: 25 non-agent
   sessions between 2026-05-23 and 2026-07-27 are archived identically —
   same `session.id`, same entry directory name, same `started_at`/
   `ended_at` — under **both** `map-reader-llm` and
   `vlm-burial-mound-detection`. From 2026-07-28 onward, every session
   (through the end of current archive coverage, 2026-08-22) is archived
   **only** under `vlm-burial-mound-detection`; `map-reader-llm` receives
   no further entries after 2026-07-27. The fork happens mid-session: the
   session with `session.id` starting `64b33adf…` (started
   2026-07-27T02:32:40Z) exists under both archive names but with
   **different `ended_at` values** — the `map-reader-llm` copy ends
   2026-07-27T23:00:24Z, while the `vlm-burial-mound-detection` copy ends
   2026-07-28T07:37:55Z (~8.5 hours later) — i.e. the `map-reader-llm`
   side stopped receiving updates partway through that session while
   archiving continued under the other name. This matches the
   project `CLAUDE.md` note that project's former `# Project:` line forked
   the archive; per that note, `map-reader-llm` was ruled canonical on
   2026-08-22.

3. **Within-archive double-archiving** (same session, two different
   directory slugs, same archive name): `session.id` `9d8336fb…` (started
   2026-07-29T06:16) appears as both
   `vlm-burial-mound-detection/2026-07-29T06-16_establish-map-reader-end-to-end-verification`
   and `…establish-map-reader-llm-verification`, with `ended_at` 10
   minutes apart. `session.id` `d8bd85a9…` (started 2026-08-19T01:04, the
   sample-8 session above) similarly appears as both
   `…filing-of-erratum-e82-10k-bootstrap` and
   `…register-the-tile-size-grid-at-10k-bootstrap`, `ended_at` 12 minutes
   apart. `session.id` `9b9b057f…` (started 2026-06-09T04:37) appears
   **three** times total: once under `map-reader-llm` and twice under
   `vlm-burial-mound-detection` with two different slugs. In total, **27**
   distinct `session.id`s appear as more than one timeline record (25 are
   the clean cross-archive mirrors in point 2; the remainder are these
   extra same-archive, multiple-slug cases).

4. **Nine empty/abandoned sessions**, all in `map-reader-llm`, all dated
   January 2026 (`2026-01-13T10-20_empty-abandoned-session`,
   `2026-01-14T13-55_empty-abandoned-session` ×2,
   `2026-01-15T08-44_empty-abandoned-session`,
   `2026-01-17T13-50_empty-abandoned-session`,
   `2026-01-17T16-32_empty-abandoned-session`,
   `2026-01-23T07-21_minimal-abandoned-session`,
   `2026-01-23T11-53_minimal-abandoned-session`,
   `2026-01-27T22-23_minimal-abandoned-session`). These are genuinely
   empty CLI invocations, not a metadata-parsing failure: `session.meta.json`
   has `model.model_id: null` and (for the "empty" ones) `session.started_at`/
   `ended_at: null`, with a ~2–4 KB `session.jsonl.gz`. All nine are
   correctly flagged `meta_ok: false` in the timeline JSON; none carry a
   `model_id`, so none contribute to the day-map.

5. **No missing files**: every one of the 253 timeline entries (across
   both archive names) has both `session.meta.json` and `session.jsonl.gz`
   present. No unparseable `session.meta.json` was encountered — all 253
   files parsed as valid JSON under the current schema
   (`schema_version: "1.1"`, `session`/`model` nested blocks). The
   "tolerate older/missing schema" fallback path in `build_timeline.py`
   was written defensively but never exercised by this corpus; only the
   genuinely-empty-session path (point 4) was.

6. **Overlapping/concurrent sessions on different models**: two windows
   show two different models both active on the same calendar days without
   a clean single-session handover: 2026-08-03→2026-08-06 (a claude-fable-5
   session, `2026-08-03T04-20_adjudicate-ninety-two-wave-five-and-two`,
   runs 2026-08-03T04:20→2026-08-06T13:47 concurrently with three
   claude-opus-5 sessions covering roughly the same span) and
   2026-08-18→2026-08-19 (two consecutive top-level claude-opus-5
   sessions sandwiched between claude-fable-5 sessions immediately before
   and after). Both are non-agent, top-level session entries — not
   subagents. This read-only task did not determine a cause; it is
   reported as an observed fact for the user to interpret (per the
   project's finding-calibration convention).

7. **Large no-evidence gap**: 2026-06-24 → 2026-07-26 (33 days) has no
   archived session of any kind — agent or non-agent — in either archive
   name. The model in evidence immediately before the gap is
   claude-fable-5 (last seen 2026-06-23); the model immediately after is
   claude-opus-5 (first seen 2026-07-27, the same session implicated in
   the archive fork, point 2). Nothing in the archive bridges what
   happened model-wise during the gap itself.

8. **Model transition days** (day carries two models because a
   model-switch happened partway through, not a data error): 2026-02-06,
   2026-04-18, 2026-05-29, 2026-06-10, 2026-07-28. Listed here for
   completeness; each is also called out inline in § (a) and, where
   relevant, § (b).

## Changelog

### 2026-08-23 — Original publication

Banked in Session 140 as the evidence base for the provenance-draft
upgrade. The day-map content is the extraction subagent's output
verbatim; the header and this changelog are the session's additions.

### 2026-08-24 — Completeness re-verified after the archiving repair; boundary adopted

The PI gated the Obs 258 boundary adoption on confirming the archive holds
everything needed after the archiving-system repair. Verified on five
grounds (full record: `docs/notes/obs-model-provenance.md` § 4.1): the
canonical union and local mirror hold identical populations (205 + 49;
gate 0; catalogue of 2026-08-23 22:14 agrees); none of the session log's
120 dated entries falls inside any no-evidence window in § (a) — the gaps
are genuine no-work periods; every Claude-era Obs heading sits on a
covered day; the § (c) sampling stands; and the boundary coheres across
archive, session log, and git (the trailer being the outlier). The
boundary was ADOPTED and the census closed at HIGH 380 · MEDIUM 48 ·
LOW 0. Post-adoption join: `provenance-obs-coverage-2026-08-24.json`
(the 2026-08-23 file is retained as the pre-adoption record).
