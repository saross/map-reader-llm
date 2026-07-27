# Session-transcript archive and search: labelling and indexing error diagnostic

> **Infrastructure-facing document.** This diagnoses the *session-archiving and
> search infrastructure* (`~/cc-archives`, the `claude_memories` PostgreSQL
> index, `~/personal-assistant/scripts/`, `~/Code/cc-session-toolkit`), not the
> map-reader research record. It was gathered during a map-reader audit because
> the defects below caused concrete analytical errors in that audit. **When
> acted upon, port this file to the `personal-assistant` repository** (suggested
> home: `wiki/planning/` alongside
> `session-archiving-upgrade-plan-2026-07-21.md`) and leave a stub here.

**Last revised**: 2026-07-28 (original publication). See [§ Changelog](#changelog)
for revision history.

**Evidence gathered**: 2026-07-28, on amd-tower, read-only.

**Anchors for re-verification**:

- `map-reader-llm` @ `2810195f4`
- `cc-session-toolkit` @ `ab5031e`
- `personal-assistant` @ `e9e917f`
- `~/cc-archives/CATALOG.json` `generated_at: 2026-07-27T12:59:44.430781`,
  `schema_version: 1.2`
- Database `claude_memories`, tables `session_chunks` (54,620 rows) and
  `sessions` (725 rows) as at 2026-07-28

---

## Executive summary

| # | Error class | Severity | Measured magnitude |
|---|---|---|---|
| 1 | `role='user'` over-captures non-human text | **Critical** | 40.0% of all indexed `user` chunks; **87.5% of `user` chunks >2,000 chars** |
| 2 | Content index misses nested archives entirely | **Critical** | 189 transcripts (27% of transcripts on disk) have zero index rows |
| 3 | Uncompressed `session.jsonl` archives are invisible to the indexer | **High** | 103 session directories |
| 4 | Completeness gate is structurally blind to both of the above | **High** | gate reads `0`; true unsearchable count is 292 |
| 5 | Project attribution differs between `sessions` and `session_chunks` | **High** | `vlm-burial-mound-detection`: 151 vs 25 |
| 6 | Renamed project split the archive; no link between halves | **High** | 3 stores, 196 distinct ids, no `supersedes`/`isPartOf` link |
| 7 | Duplicate archives of the same session under different slugs | Medium | 77 duplicate-id groups (77 redundant directories) |
| 8 | `CATALOG.json` under-counts and is internally inconsistent | Medium | 538 catalogued vs 727 on disk; `projects{}` sums to 411 |
| 9 | Subagent runs are archived as peer "sessions" with fabricated human-message counts | Medium | 116 directories; e.g. `human_messages: 18` for a subagent |
| 10 | `duration_minutes` is wall-clock, not working time | Low | 218 of 804 sessions exceed 24 h |
| 11 | `artifacts.*` paths that resolve nowhere | Low | ~3.6% neither on disk nor in git history |
| 12 | `~/cc-archives/_indexes/` is empty and referenced by nothing | Trivial | 1 vestigial directory |

**Bottom line for auditors.** Two independent defects mean a search that returns
nothing is *not* evidence of absence, and a search hit labelled `user` is *not*
evidence the principal investigator said it. Both were load-bearing in the
map-reader audit.

---

## 1. `role='user'` over-captures text the user never wrote

**Severity: Critical.** This is the defect that can put fabricated quotations
into the principal investigator's mouth.

### 1.1 What was measured

`index-session-content.py` assigns `role` from
`record["message"]["role"] or record["type"]`
(`~/personal-assistant/scripts/index-session-content.py`, line 105). In the
Claude Code JSONL format, `type: "user"` is the transport envelope for **every
non-assistant record**, not a claim about authorship. The indexer keeps any such
record whose content is a bare string or contains `text` blocks. That admits at
least six classes of machine-generated text under the `user` label.

### 1.2 Error rate, with sampling method

Two independent estimates:

**(a) Whole-population, deterministic (no sampling).** Counting only `user`
chunks whose text begins with an unambiguous machine marker
(`<…>` tag, `This session is being continued`, `Caveat: The messages below`,
`[Request interrupted`):

- 3,751 of 12,748 `user` chunks = **29.4%**. This is a hard floor, not an
  estimate.

**(b) Ground-truth sample.** 1,000 `user` chunks drawn without replacement
(`random.Random(20260728).sample`) from the full 12,748-row population, each
resolved back to its source record in the source `.gz` and classified on the
raw record's `isSidechain` / `isMeta` / `isCompactSummary` flags and content
shape. All 1,000 resolved; 385 archive files touched.

| Class | n | % |
|---|---:|---:|
| **Genuine human turn** | 600 | **60.0%** |
| `isMeta` — harness-injected context (slash-command bodies, skill text) | 157 | 15.7% |
| `<task-notification>` — **a subagent's report** | 71 | 7.1% |
| Compact summary — model-authored continuation summary | 45 | 4.5% |
| `<local-command-stdout>` | 41 | 4.1% |
| `<command-message>` | 37 | 3.7% |
| `<command-name>` | 31 | 3.1% |
| `[Request interrupted …]` | 13 | 1.3% |
| `<system-reminder>` / `<bash-stdout>` / other tags | 5 | 0.5% |

**Error rate: 40.0% (95% CI 37.1–42.9%, finite-population corrected).**

The deterministic floor (29.4%) is lower than the sampled rate because the
largest single class — `isMeta` at 15.7% — carries **no textual marker at all**.
A `/recap` command body indexed as a user turn begins `# /recap — End-of-Day
Recap`. Nothing in the indexed text distinguishes it from prose the user typed.
Only the raw record's `isMeta: true` flag reveals it, and that flag is not
stored in `session_chunks`.

### 1.3 The rate is far worse for the chunks an audit actually quotes

Auditors quote *substantive* passages, not one-liners. Restricting the
population to `user` chunks over 2,000 characters (2,144 chunks) and sampling
400 (`seed=77`, all resolved):

| Class | n | % |
|---|---:|---:|
| `isMeta` | 165 | 41.2% |
| Compact summary | 100 | 25.0% |
| `<task-notification>` (subagent report) | 80 | 20.0% |
| **Genuine human turn** | 50 | **12.5%** |
| Other injections | 5 | 1.3% |

**87.5% of long `user` chunks are not the user's words** (95% CI 84.6–90.4%).
A long, articulate, technically-detailed "user" turn is *a priori* about seven
times more likely to be machine-generated than human-typed.

### 1.4 Mechanism — confirmed, not inferred

The subagent case reported in the map-reader audit is `<task-notification>`.
When a background agent completes, the harness injects its report into the
parent transcript as `type: "user"`, `isSidechain: false`, string content.
Raw record keys for the verified example:
`['cwd','gitBranch','isSidechain','message','parentUuid','permissionMode',
'sessionId','slug','thinkingMetadata','timestamp','type','userType','uuid',
'version']` — nothing marks it as non-human except the `<task-notification>`
tag in the text itself.

Note what is *not* the mechanism: subagent conversations are **not** merged
inline. In a 12-file sample of map-reader transcripts there were 10,362
`progress` records (subagent turn wrappers) and zero `isSidechain: true`
records, and `progress` is correctly skipped by the indexer. The chunker also
does not split turns badly — see §4.1.

The `assistant` role is clean by contrast: 399 of 400 sampled chunks
(seed 11) were genuine assistant prose; the single exception was an
`API Error: Unable to connect to API (ConnectionRefused)` record. **The defect
is one-directional.**

### 1.5 Reproducible examples

| Handle | Class | What it actually is |
|---|---|---|
| `2026-02-07T04-52_22c8755f` `#1532` (`map-reader-llm`) | `task-notification` | Report from agent *"Simplify generate_metrics_for_consensus"* — a code-simplifier subagent's summary, labelled `user` |
| `2026-01-17T12-38_d40e04c4` `#235` (`map-reader-llm`) | compact summary | Model-authored context summary, labelled `user` |
| `2026-04-15T12-16_end-of-day-recap-and-time-tracking` `#5` (`personal-assistant`) | `isMeta` | The body of the `/recap` slash-command definition, labelled `user` |
| `2026-06-09T01-04_sign-off-era-1-leaderboard-and-complete` `#957` (`vlm-burial-mound-detection`) | `local-command-stdout` | The string `Goodbye!` |

### 1.6 Blast radius

Every consumer that trusts `role`: `search-sessions.py --role user`, the
`search_sessions` MCP tool, `/recall`, `/search-sessions`, memory extraction,
and any agent asked to "find what Shawn said about X". In the map-reader audit
this produced at least two attributions of machine text to the principal
investigator. Because the `isMeta` class is textually invisible, a careful
reader cannot filter it out by eye.

### 1.7 Proposed fix

1. **Add provenance columns to `session_chunks`** — `is_meta`, `is_sidechain`,
   `is_compact_summary`, `record_type` (boolean/text, all available on the raw
   record at index time). Schema migration plus a `--force` reindex.
2. **Introduce a `speaker` label distinct from `role`.** Suggested vocabulary:
   `human`, `assistant`, `subagent-report`, `system-injected`,
   `compact-summary`, `command-io`. Derive it once at index time from the flags
   plus a prefix table; keep raw `role` for backwards compatibility.
3. **Default `--role user` to `speaker = 'human'`**, and make the non-human
   classes reachable only by explicit opt-in.
4. **Render the speaker in CLI output** so a hit reads
   `· subagent-report ·` rather than `· user ·`.

**Effort**: ~4–6 h (2 h classifier and migration, 1 h reindex of 512 files,
1–2 h updating `search-sessions.py`, the MCP tool, and the `/recall` and
`/search-sessions` commands). No API spend. Reindex is local parse work only.

**Interim mitigation, zero effort**: treat any `user` hit longer than ~2,000
characters as machine-generated until proven otherwise, and never quote a
`user` chunk without running `--show` and eyeballing the opening line.

---

## 2. The content index never sees nested archives

**Severity: Critical.** This is the sole cause of the "April 2026 gap".

### 2.1 Evidence

`index-session-content.py::discover()` (lines 125–143) hand-rolls a
**fixed two-level walk**: `<root>/<project>/<session-dir>/session.jsonl.gz`.
Every sibling script uses `rglob` instead:

- `sync-sessions-to-postgres.py` line 143 — `archive_root.rglob("session.meta.json")`
- `reprocess-sessions.py` line 225 — `ARCHIVE_ROOT.rglob("session.meta.json")`
- `_scan_archives.py` lines 57–58 — `root.rglob("session.jsonl.gz")`

So the metadata layer walks the whole tree and the content layer does not.

Whole-tree count (804 `session.meta.json` files, 727 distinct session ids):

| State | Count |
|---|---:|
| Transcript present **and** indexed | 512 |
| Transcript present, **zero index rows** | 189 |
| Only an uncompressed `session.jsonl` (see §3) | 103 |
| True meta-only shells (no transcript at all) | **0** |

The 189 unindexed transcripts sit under three nested stores:

- `map-reader-llm/vlm-burial-mound-detection/` — 81
- `LLM-History-Paper/theseus-ship/` — 60
- `_legacy/…` — 48 (excluded deliberately: `discover()` skips `_`-prefixed dirs)

### 2.2 The April 2026 sessions are fully recoverable

They were never missing — they are in
`~/cc-archives/map-reader-llm/vlm-burial-mound-detection/`, one level below
where the indexer looks. All 27 April directories carry a `session.jsonl.gz`,
sizes 48 KB to 12 MB. They collapse to **21 distinct session ids** (six
duplicate pairs, §7).

Nested-store transcript coverage by month:

| Month | Directories | With `.gz` |
|---|---:|---:|
| 2025-12 | 13 | 0 |
| 2026-01 | 65 | 10 |
| 2026-02 | 8 | 8 |
| 2026-03 | 31 | 31 |
| **2026-04** | **27** | **27** |
| 2026-05 | 5 | 5 |

Across the map-reader family, **73 archived directories (≈51 distinct real
sessions after de-duplication, all of March–May 2026 plus stragglers) exist in
no indexed store**. The December–January directories that lack `.gz` are
`agent-*` subagent runs and `empty-abandoned-session` stubs — negligible.

### 2.3 Demonstrated false negative

Verbatim user text in
`map-reader-llm/vlm-burial-mound-detection/2026-04-25T00-16_recover-lost-verifier-calibration-matrix-and`
turn 50:

> "First, we'd better clear up the issue with 'Re-run canonical
> verify_adversarial-text on S78 shared-crops'."

Both of these return **"No matches"**:

```bash
~/personal-assistant/venv/bin/python \
  ~/personal-assistant/scripts/search-sessions.py \
  "Re-run canonical verify_adversarial-text on S78 shared-crops"

~/personal-assistant/venv/bin/python \
  ~/personal-assistant/scripts/search-sessions.py \
  "verify_adversarial-text on S78 shared-crops" --substring
```

### 2.4 Proposed fix

Replace the hand-rolled walk in `discover()` with
`archive_root.rglob("session.jsonl.gz")`, deriving `project` from the
`session.meta.json` `project.name` rather than the directory name (§5). Keep
the `_`-prefix exclusion as an explicit skip list. Then reindex.

**Effort**: ~30 min to patch, plus one indexing run over ~190 additional files
(local, niced, no API). Strongly recommended to fix §5 in the same change so
the new rows are not mislabelled on arrival.

---

## 3. Uncompressed `session.jsonl` archives are invisible

**Severity: High.**

103 session directories contain a plain `session.jsonl` and no `.gz`; a further
34 contain both. `discover()` globs `session.jsonl.gz` only, so the 103 are
unreachable. `archive.py` line 1823 writes `session.jsonl` uncompressed when
`use_gzip` is false, and the resulting metadata records
`archive.jsonl_path: "session.jsonl"` — so the archive is internally
self-consistent and only the indexer disagrees.

Distribution: `map-reader-llm` 68 (all inside the nested store), and
`llm-reproducibility` 35. Most are `agent-*` subagent runs, but not all.

**Fix**: glob both extensions in `discover()`; `iter_turns()` already streams
line-by-line and needs only an `open` vs `gzip.open` branch.
**Effort**: ~20 min, folded into the §2 patch.

---

## 4. The completeness gate is structurally blind to all of the above

**Severity: High.**

`~/.cache/cc-archives-gate` currently reads **`0`** (file mtime 2026-07-27
11:48). It is a true statement of a predicate that does not mean what the
system relies on it to mean.

The gate (`daily-sync.sh` lines 594–619) counts metas where
`archive.jsonl_sha256` is set **and** no sibling transcript exists. Because:

- every one of the 804 metas that lacks a `.gz` has a sibling `session.jsonl`
  instead, and
- there are **zero** true meta-only shells,

the predicate is vacuously satisfied. The gate therefore reports `0` while 292
of 804 session directories (36.3%) are unsearchable. It measures *transcript
presence on disk*, and is silently read as *archive completeness*.

**Fix**: add a second gate counting `session.meta.json` files whose transcript
has no rows in `session_chunks`, and surface both numbers in
`daily-sync-trigger.sh`. Naming them distinctly ("transcripts missing" /
"transcripts unindexed") prevents the same conflation recurring.

**Effort**: ~1 h (the query is a single `LEFT JOIN`; the announcement plumbing
already exists).

---

## 5. Two incompatible definitions of "project"

**Severity: High.**

| Table | Source of `project` | `vlm-burial-mound-detection` |
|---|---|---:|
| `sessions` | `session.meta.json` → `project.name` (`sync-sessions-to-postgres.py` line 213) | **151** |
| `session_chunks` | depth-1 directory name under `~/cc-archives` (`index-session-content.py` line 136, `proj_name = proj_root.name`) | **25** |

`search-sessions.py --project X` filters `session_chunks.project`, so
`--project vlm-burial-mound-detection` searches 25 sessions while the metadata
layer knows 151. Conversely `--project map-reader-llm` returns 73 chunk-level
sessions while `sessions` has only 45 under that name.

The directory-name derivation also invents projects that do not exist:
`theseus-ship` (48), `TRAP-WD-2020-04` (14), `Code` (10), `shawn` (3),
`trap-extraction` (7) all appear as `sessions.project` values because they are
leaf directory names of nested stores.

**Related**: 219 of 725 `sessions` rows (30.2%) have **zero** indexed chunks —
for `vlm-burial-mound-detection`, 99 of 151 (65.6%). A search-by-metadata finds
the session; a search-by-content cannot see inside it.

Two `archive_dir`s (105 chunks) have a `session_id` with no matching `sessions`
row, so their hits render with a null title and date:
`2026-07-15T01-14_establish-daily-standup-sync-multi-machine` and
`2026-07-17T03-33_consolidate-and-review-paper-b-bibliography`.

**Fix**: make `session.meta.json` → `project.name` the single authority for
both tables; keep the directory name only as a fallback when metadata is
absent. Add a foreign-key-style consistency check to the daily sync.
**Effort**: ~2 h including a reindex.

---

## 6. The project rename split the archive, and nothing links the halves

**Severity: High.**

### 6.1 What happened

`get_project_name()` (`cc-session-toolkit/src/cc_session_toolkit/project.py`,
lines 59–104) resolves a project name in priority order: a
`# Project: <name>` line in `CLAUDE.md`, then the git remote, then the
directory name. `~/Code/map-reader-llm/CLAUDE.md` line 1 reads
`# Project: vlm-burial-mound-detection` and has done since the file was created
(commit `cfc10c133`, 2026-01-09). The *directory* was never renamed.

`get_archive_directory()` (`naming.py` line 68) then computes
`project_dir = archive_dir / project_name`. With `archive_root` set (global
hook mode) that yields `~/cc-archives/vlm-burial-mound-detection/`; in
project mode it yields `<repo>/archive/cc-sessions/vlm-burial-mound-detection/`,
which at some point was copied wholesale into
`~/cc-archives/map-reader-llm/`. The repo's own `archive/cc-sessions/` is now
empty and untracked, so the nested store is the only surviving copy.

The result is three stores for one project:

| Store | Directories | Distinct ids | Indexed? |
|---|---:|---:|---|
| A `map-reader-llm/` | 73 | 73 | yes |
| B `map-reader-llm/vlm-burial-mound-detection/` | 149 | 127 | **no** |
| C `vlm-burial-mound-detection/` | 25 | 24 | yes |

Overlaps: A∩B = 28 ids, B∩C = 0, A∩C = 0. **196 distinct ids in total; 99 of
them exist only in B.** A and B overlap in *time* (both cover 2025-12 →
2026-03), so this is not a clean before/after rename split — it is two parallel
archives produced by two code paths.

### 6.2 Is there an intended linking mechanism? Effectively no

`relationships.isPartOf` is populated on all 804 metas, but it is always just
`[project_name]` — a project label, not a session or archive pointer. Across
the entire archive:

- `supersedes`: set **0** times
- `references`: non-empty 4 times
- `continues`: 78; `continuedBy`: 13

No metadata in store B references `map-reader-llm`, and none in A or C
references the other. **The two map-reader archives are mutually orphaned.**
The only thing tying them together is the shared
`project.directory: "/home/shawn/Code/map-reader-llm"` field, which is not
indexed or exposed by any search path.

**Fix**, in order of increasing ambition:

1. *Minimum* — index B (fixes §2) and normalise `project` (fixes §5). All 196
   sessions then answer to `--project vlm-burial-mound-detection`.
2. *Better* — add a `project_aliases` table (or a `relationships.supersedes`
   entry on the store-A metas pointing at the new name) so historical queries
   under either name resolve.
3. *Structural* — teach the toolkit that a project-name change with an
   unchanged `project.directory` is a **rename**, and either consolidate the
   store or write reciprocal `supersedes`/`isPartOf` links at archive time.

**Effort**: (1) folded into §2/§5; (2) ~2 h; (3) ~1 day in the toolkit.

---

## 7. Duplicate archives of the same session

**Severity: Medium.**

77 session ids appear in more than one directory (77 redundant directories out
of 804). Typical pattern — the same id archived once under a hash slug and once
under a generated title:

```text
2026-03-14T21-50_correct-experimental-configuration-drift-and
2026-03-14T21-50_d86b9454
```

Both carry `started_at: 2026-03-14T21:50:39.369Z` and the same session id
`d86b9454-d8a2-4d65-8ae4-bb679456a727`, but **different `jsonl_sha256`
values**, so they are not byte-identical captures — most likely a mid-session
snapshot and a final archive (the toolkit's known failure mode 2), never
reconciled because `supersedes` is never written.

Grouped by top-level store: `map-reader-llm` 50, `_legacy` 11,
`LLM-History-Paper` 11, six others 1 each.

One duplicate is **cross-project**: id `179adf8a-a223-48db-a557-7bb57191772c`
appears as both `absence-judgement/2026-01-13T06-50_179adf8a` and
`LLM-History-Paper/theseus-ship/2026-01-13T06-50_179adf8a`. At least one of
those project attributions is wrong.

In April 2026 alone, 27 directories collapse to 21 distinct sessions.

**Fix**: a de-duplication pass keyed on session id — keep the longest
transcript, write `supersedes` on the loser, archive rather than delete (per
the repo's file-preservation policy). Then implement the toolkit's planned
automatic supersede detection (plan item B8).
**Effort**: ~3 h for the one-off pass; the B8 toolkit change is separate.

---

## 8. `CATALOG.json` is incomplete and internally inconsistent

**Severity: Medium.**

- `total_sessions: 538`, `len(sessions): 538`, 538 distinct ids.
- On disk: **727** distinct ids across 804 directories.
- **189 session ids on disk are absent from the catalogue**:
  `map-reader-llm` 99, `LLM-History-Paper` 48, `_legacy` 37,
  `personal-assistant` 2, `2026-mq-llm-dh-judgement-paper-b` 2,
  `llm-reproducibility` 1. Nothing in the catalogue is missing from disk.
- The `projects{}` block disagrees with its own `sessions[]` list: the
  per-project counts sum to **411**, not 538. `projects{}` lists 16 projects
  and omits `vlm-burial-mound-detection` entirely, even though 24 of its
  `sessions[]` entries have directories beginning `vlm-burial-mound-detection/`.
  Example: `personal-assistant` is recorded as 88 sessions but has 126
  `sessions[]` entries.

**Fix**: regenerate the catalogue from an `rglob` walk with the same
project-name authority as §5, and add an assertion that
`sum(projects[].session_count) == len(sessions)`.
**Effort**: ~1–2 h in `cc_session_toolkit/catalogue.py`.

---

## 9. Subagent runs are archived as peer sessions with fabricated human-message counts

**Severity: Medium.**

116 archived directories are subagent runs (`_agent_*` / `agent-*` names,
`session.id` of the form `agent-ab1640f`). They sit alongside real sessions in
the same stores and become ordinary rows in the `sessions` table.

Their statistics repeat the §1 error at the metadata layer. From
`map-reader-llm/vlm-burial-mound-detection/2026-01-01T23-08_agent_llm-api-script-search/session.meta.json`:

```json
"statistics": { "turns": 18, "human_messages": 18, "assistant_messages": 25 }
```

A subagent run has **zero** human messages. The 18 counted are the parent
agent's dispatch prompt plus tool results.

This also explains an otherwise puzzling model distribution: 78 `sessions` rows
attributed to `claude-haiku-4-5-20251001`. Spot-checking shows these are
subagent runs that genuinely ran on Haiku, so the model attribution itself is
sound — it is the framing of subagents as sessions that misleads. Three rows
carry `model_id: "<synthetic>"`, taken from an API-error record rather than a
real assistant message.

**Fix**: add a `session_kind` column (`main` | `subagent`) derived from the
`agent-` id prefix; exclude subagents from session counts by default; rename
`human_messages` to `inbound_messages` in the schema, or compute it from the
same `speaker` classifier built for §1.
**Effort**: ~2 h.

---

## 10. `duration_minutes` measures wall-clock, not work

**Severity: Low, but it corrupts any productivity or cost analysis.**

218 of 804 sessions record a duration over 24 hours; `duration_minutes` is
`ended_at - started_at`, so a session resumed after a night's sleep reads as a
1,400-minute session. `CATALOG.json` propagates this: one
`2026-mq-llm-dh-judgement-paper-b` session is recorded at 12,024 minutes
(8.3 days), and `voice-assistant`'s 9 sessions total 12,971 minutes.

Directory timestamps are otherwise sound: 793 of 804 directory-name timestamps
match `session.started_at` exactly (UTC); 6 metas have no `started_at`, 5
directory names have no timestamp; **zero mismatches**.

**Fix**: add `active_minutes` computed from inter-turn gaps with an idle
threshold (say, gaps >30 min excluded), and prefer it in the catalogue.
**Effort**: ~2 h.

---

## 11. `artifacts.*` paths that resolve nowhere

**Severity: Low — the field is broadly trustworthy.**

Sample of 60 metas (`seed=42`), 827 artefact entries checked against disk and,
where absent, against `git log --all`:

| Field | Entries | Missing from disk | Of those, in git history | Neither |
|---|---:|---:|---:|---:|
| `created` | 218 | 32 | 31 | 1 |
| `modified` | 207 | 39 | 36 | 3 |
| `referenced` | 402 | 111 | 85 | 26 |

So ~22% of artefact paths no longer resolve on disk, but **the overwhelming
majority are files that genuinely existed and were later moved or archived** —
expected under the repositories' archive-never-delete policies. Only 30 of 827
entries (**3.6%**) are unverifiable in both disk and git history, and several of
those are in `trap-extraction`, a legacy repository whose working tree has
diverged.

**Fix**: low priority. If desired, verify artefact paths at archive time and
mark unresolvable entries (toolkit plan item B3 already proposes archive-time
identifier verification).
**Effort**: folded into B3.

---

## 12. `~/cc-archives/_indexes/` is empty and unreferenced

**Severity: Trivial.** Created 2026-05-21, contains nothing, and `grep` across
`~/personal-assistant/scripts/` and `~/Code/cc-session-toolkit/src/` finds no
reference to it. Either populate it or remove it, so future diagnostics do not
treat it as a missing index.

---

## Answers to the audit questions

**Can "no search hits" be a false negative?** Yes, from two independent causes,
and the second is unavoidable by design:

1. **Whole sessions are unsearchable.** 292 of 804 session directories (36.3%)
   have zero index rows — 189 nested transcripts plus 103 uncompressed ones.
   For the map-reader family specifically, ~51 distinct real sessions including
   *all of April 2026* are absent from the index.
2. **Even indexed sessions are only 8.2% searchable.** Measured over 12
   map-reader transcripts (14.1 M characters of message content): `tool_result`
   63.7%, `tool_use` inputs 24.5%, assistant `text` 4.4%, assistant `thinking`
   3.7%, user string content 3.2%, user `text` blocks 0.6%. The index keeps
   only the last three — **91.8% of transcript content is structurally
   unsearchable**. This is deliberate (`index-session-content.py` docstring) and
   sensible for prose search, but it means any string that appeared *only* in a
   file the agent wrote, a command it ran, a grep pattern, a tool result, or its
   own reasoning **cannot be found**. Filenames, config values, and identifiers
   are exactly the class most likely to live only in tool traffic.

**Is partial indexing systematic?** No. The "361 of 4,198 turns" observation is
the expected prose-to-raw-record ratio, not truncation. Re-running the
indexer's own extraction predicate over 40 randomly sampled indexed transcripts
(`seed=3`) gave an exact row-count match in **40 of 40** cases, with zero stale
`source_mtime` values. Indexing is complete for every file it reaches; the
problem is which files it reaches (§2, §3) and which content it keeps (above).

---

## How to reproduce

All commands are read-only. Use `~/personal-assistant/venv/bin/python`.

**Role mislabelling — deterministic floor:**

```bash
psql -d claude_memories -c "
SELECT count(*) FILTER (WHERE role='user') AS user_chunks,
       count(*) FILTER (WHERE role='user' AND (
         text LIKE '<%' OR text LIKE 'This session is being continued%' OR
         text LIKE 'Caveat: The messages below%' OR text LIKE '[Request interrupted%'
       )) AS machine_text
FROM session_chunks;"
```

**Role mislabelling — inspect the four verified examples:**

```bash
S=~/personal-assistant/scripts/search-sessions.py
P=~/personal-assistant/venv/bin/python
$P $S --show 2026-02-07T04-52_22c8755f --turn 1532 --context 0
$P $S --show 2026-01-17T12-38_d40e04c4 --turn 235  --context 0
$P $S --show 2026-04-15T12-16_end-of-day-recap-and-time-tracking --turn 5 --context 0
```

**The April sessions exist and have transcripts:**

```bash
ls -d ~/cc-archives/map-reader-llm/vlm-burial-mound-detection/2026-04* | wc -l   # 27
find ~/cc-archives/map-reader-llm/vlm-burial-mound-detection/2026-04* \
     -name session.jsonl.gz | wc -l                                             # 27
```

**They are not in the index:**

```bash
psql -d claude_memories -t -A -c "
SELECT count(*) FROM session_chunks
WHERE archive_path LIKE 'map-reader-llm/vlm-burial-mound-detection/%';"          # 0
```

**Demonstrated false negative** (text is verbatim in the April 25 transcript):

```bash
~/personal-assistant/venv/bin/python \
  ~/personal-assistant/scripts/search-sessions.py \
  "Re-run canonical verify_adversarial-text on S78 shared-crops"                 # No matches
```

**Archive-versus-index coverage:**

```bash
find ~/cc-archives -name session.meta.json | wc -l                               # 804
psql -d claude_memories -t -A -c \
  "SELECT count(DISTINCT archive_path) FROM session_chunks;"                     # 512
```

**Project-attribution split:**

```bash
psql -d claude_memories -t -A -c \
  "SELECT count(*) FROM sessions WHERE project='vlm-burial-mound-detection';"    # 151
psql -d claude_memories -t -A -c \
  "SELECT count(DISTINCT archive_dir) FROM session_chunks
   WHERE project='vlm-burial-mound-detection';"                                  # 25
```

**Gate state:**

```bash
cat ~/.cache/cc-archives-gate                                                    # 0
```

**Catalogue inconsistency:**

```bash
~/personal-assistant/venv/bin/python -c "
import json, pathlib
c = json.loads((pathlib.Path.home()/'cc-archives/CATALOG.json').read_text())
print(c['total_sessions'], len(c['sessions']),
      sum(p['session_count'] for p in c['projects'].values()))"                   # 538 538 411
```

---

## Suggested fix order

1. **§2 + §3 + §5 together** — one patch to `index-session-content.py`
   (`rglob`, both transcript extensions, metadata-derived project name) plus a
   reindex. Recovers 292 sessions and fixes project attribution in one pass.
   *~2 h plus indexing time.*
2. **§1 speaker classification** — schema migration and `--force` reindex.
   Do it in the same reindex window as (1) to avoid parsing 800 files twice.
   *~4–6 h.*
3. **§4 gate** — add the unindexed-transcript counter so this cannot silently
   recur. *~1 h.*
4. **§8 catalogue** regeneration with an internal-consistency assertion.
   *~1–2 h.*
5. **§7 de-duplication** pass and **§6** alias/`supersedes` linking. *~5 h.*
6. **§9, §10, §11, §12** — metadata-quality follow-ups, batchable with the
   toolkit's existing C-series plan items. *~6 h total.*

Items 1–3 are the ones that make audit conclusions trustworthy again; the rest
are hygiene.

---

## Changelog

### 2026-07-28 — Original publication

Initial diagnostic, gathered read-only on amd-tower during the map-reader D17
inventory audit. Twelve error classes characterised against `CATALOG.json`
`generated_at 2026-07-27T12:59:44.430781`, the `claude_memories` database as at
2026-07-28 (`session_chunks` 54,620 rows, `sessions` 725 rows), and 804
`session.meta.json` files on disk. Headline measurements: 40.0% role-attribution
error on `user` chunks (n=1,000 ground-truth sample), 87.5% on `user` chunks
over 2,000 characters (n=400), 292 of 804 sessions unsearchable, and all 27
April 2026 map-reader archives confirmed present with intact transcripts.
