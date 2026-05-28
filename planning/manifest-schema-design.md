# Manifest Schema Design Brief

> **Last revised**: 2026-05-28 (initial brief; input to the schema-design
> session). See [§ Changelog](#changelog) for revision history.

**Status**: Design brief — captures decisions and proposed field lists from
the Session 90 planning conversation so the schema-design session can start
cold. The actual JSON Schema files are the deliverable of that session, not
this brief.

**Purpose**: The project is replacing the overloaded "Era 1 / 2 / 3"
terminology with empirical, machine-readable manifests of runs, analyses,
and passes. These manifests become the canonical structured representation
of the experimental work; prose docs reference entries by ID. They are also
intended as paper supplementary material (reproducibility / transparency).

---

## 1. Decisions already locked (do NOT re-litigate)

These were settled in conversation on 2026-05-28. The schema session should
treat them as fixed inputs.

1. **Three manifests**: `runs`, `analyses`, `passes` (normalised; `passes`
   and `analyses` carry foreign keys to `runs`).
2. **JSON-canonical, Markdown-rendered**: the JSON file is the source of
   truth; a script renders human-readable Markdown tables from it. Humans do
   not hand-edit the rendered Markdown.
3. **Location**: `results/` (i.e. `results/runs-manifest.json`,
   `results/analyses-manifest.json`, `results/passes-manifest.json`, plus
   the rendered `.md` siblings).
4. **Sequencing III — schema-first, populate-later**: design and commit the
   schemas in this session; defer population until Phase 1 (the generator
   script) writes both per-run post-run-reports and manifest rows from the
   same extraction pipeline.
5. **Generator-as-only-writer** for `runs` and `passes`: these are
   machine-extracted from source-of-truth files (`*.meta.json`,
   `cost_manifest.json`, `evaluation/*.json`, bounds manifests, YAML
   configs). Humans edit the *source* files, never the manifest; the
   generator re-extracts. The user confirms source-of-truth files are
   accurate or have known issues already captured in errata / working-notes.
6. **Analyses manifest is hybrid**: machine-fills the auto-extractable
   fields (`analysis_id`, `output_path`, `working_notes_obs`); humans author
   `outcome`, `paper_section`; each human-authored row carries a
   `manually_verified_at` timestamp; the generator never overwrites
   human-authored fields.
7. **"Era" retired going forward**, but preserved as `historical_aliases`
   field values so existing prose (paper drafts, working-notes Obs entries,
   the README) stays traceable. We do not rewrite the past; we recognise
   prior "Era" usage as an alias.
8. **Lineage-block integration** (Phase 4, not this session): the `## See
   also` blocks codified in `docs/methodology/output-directory-standard.md`
   will reference manifest IDs (`run:<id>`, `analysis:<id>`) instead of
   opaque paths. Design the ID conventions to survive directory renames so
   lineage references stay valid.
9. **H11 scope principle** (memory `2026-05-28-3be9d3066363`): governs the
   `experiment_program` field values for `outputs/h11/` runs. H11 = the
   tile-size study + the 384px detection-approach characterisation that fed
   the H11 leaderboard. See the Session 91 beacon in
   `planning/paper-writeup-continuity.md` for the stay/move classification.

---

## 2. Proposed field lists (refine these in the schema session)

These are starting proposals from the conversation, not final schemas. The
schema session should pressure-test each field, decide types, required vs
optional, and enums.

### 2.1 Runs manifest — one row per run

| Field | Type | Source | Notes |
|---|---|---|---|
| `run_id` | string | directory path under `outputs/` | See ID convention, § 3 |
| `experiment_program` | string (enum?) | manual / inferred | Logical grouping orthogonal to directory path (e.g. `H11-tile-size`, `GS-validation`, `55map-generalisation`, `phase2-OFAT`) |
| `directory_path` | string | filesystem | `outputs/<...>` — the physical location |
| `hypothesis_or_purpose` | string | YAML config / manual | e.g. `H11`, or a one-line purpose for non-hypothesis runs |
| `model_config` | object | `*.meta.json` | model id, thinking level, modality |
| `tile_size_px` | integer | bounds / tile manifest | 256 / 384 / 512 |
| `calibration_set_id` | string | bounds manifest | references the calibration tile pool |
| `n_calibration_tiles` | integer | bounds manifest | |
| `test_set_id` | string | bounds manifest | references the test tile pool |
| `n_test_tiles` | integer | bounds manifest | |
| `test_set_bounds_path` | string | bounds manifest | the `.geojson` defining the pool |
| `proposer_config` | object | YAML | prompt variant, etc. |
| `verifier_config` | object | YAML | verifier variant, scale, etc. |
| `n_passes` | integer | YAML / meta | |
| `vote_threshold` | number | YAML / meta | |
| `prob_threshold` | number | YAML / meta | |
| `dates_run` | object | `*.meta.json` execution timeline | start / end (UTC) |
| `total_cost_usd` | number | `cost_manifest.json` (Era 2) or reconstructed from meta | flag reconstruction in provenance |
| `headline_f1` | object | `evaluation/*.json` | value + 95% CI; note buffer radius |
| `precision` / `recall` | object | `evaluation/*.json` | value + 95% CI |
| `outputs_path` | string | filesystem | canonical artefact location |
| `post_run_report_path` | string \| null | filesystem | null if not yet authored |
| `working_notes_obs` | array[string] | grep `working-notes.md` | `Obs N — title` (no line numbers; they drift) |
| `historical_aliases` | array[string] | manual | e.g. `["Era 2", "the v2 GS run"]` |
| `provenance` | object | generator | `source_files[]`, `last_extracted_at`, `extractor_version` |

### 2.2 Analyses manifest — one row per analysis

| Field | Type | Source | Notes |
|---|---|---|---|
| `analysis_id` | string | `results/` subdir name | See ID convention, § 3 |
| `type` | string (enum) | manual | `comparison` / `leaderboard` / `sweep` / `diagnostic` / `classification` / `gt-audit` |
| `runs_compared` | array[string] | manual + auto-suggest | foreign keys to `run_id` |
| `outcome` | string | **human-authored** | one-sentence headline finding |
| `paper_section` | string (enum) | **human-authored** | `Methods` / `Results` / `Discussion` / `Limitations` / `Appendix` |
| `output_path` | string | filesystem | `results/<analysis_id>/` |
| `working_notes_obs` | array[string] | grep | `Obs N — title` |
| `manually_verified_at` | string (ISO) \| null | human | set when a human authors/verifies the row |
| `provenance` | object | generator | as above |

### 2.3 Passes manifest — one row per pass (the linked pass-level record)

| Field | Type | Source | Notes |
|---|---|---|---|
| `pass_id` | string | derived | See ID convention, § 3 |
| `run_id` | string | parent | foreign key to runs manifest |
| `condition` | string | meta / dir | e.g. `flash-high-image-n5` |
| `pass_n` | integer | meta | the Nth pass in a consensus set |
| `model` | string | `*.meta.json` | |
| `thinking_level` | string | `*.meta.json` | |
| `temperature` | number | `*.meta.json` | |
| `n_tiles_processed` | integer | `*.tiles.json` | |
| `status` | string (enum) | `*.tiles.json` | `ok` / `partial` / `failed` |
| `tokens` | object | `*.meta.json` | input billed / cached / output / thinking / total |
| `cost_usd` | number | `*.meta.json` | |
| `wall_clock_s` | number | `*.meta.json` | |
| `retries` | integer | `*.meta.json` | |
| `provenance` | object | generator | as above |

---

## 3. Open decisions for the schema session

1. **`run_id` convention for multi-level paths.** Proposal: `run_id` = path
   relative to `outputs/`, lowercase, slashes preserved (`phase2a`,
   `55maps-image-generalisation`, `h11/pv-diag-384`). The **run boundary =
   the directory containing the canonical `post_run_report.md`**. For H11
   this means ~6 post-run-reports under `outputs/h11/`, not one umbrella
   report (this contradicts the audit plan § 5.1's "1 H11 report" — the
   audit plan was wrong; see beacon). Confirm or revise.
2. **`analysis_id` convention.** Proposal: `results/` subdir name. Some
   analyses are top-level `.md` files, not subdirs — decide how those map
   (own row? folded into a related subdir?).
3. **`pass_id` convention.** Proposal: `{run_id}::{condition}::pass{N}` or
   reuse the `*.meta.json` filename stem. Decide.
4. **Pass-level granularity confirmation.** The separate `passes-manifest.json`
   with `run_id` FK is the agreed design. Confirm the field list (§ 2.3) is
   sufficient and that per-run "Passes" tables in each `post_run_report.md`
   render from it (filtered by `run_id`).
5. **Schema versioning.** Add a top-level `schema_version` (start `"1.0"`)
   to each manifest. Decide where the JSON Schema validation files live —
   proposal: `docs/methodology/runs-manifest-schema.json`, etc.
6. **Provenance object shape.** Proposal:
   `{ "source_files": [...], "last_extracted_at": "<ISO>", "extractor_version": "<semver>" }`.
   Decide whether `extractor_version` tracks the generator script version or
   a manifest-format version.
7. **`experiment_program` enum vs free-text.** Enum gives consistency but
   needs maintenance as new programmes appear; free-text is flexible but
   drift-prone. Decide (lean: small controlled enum with a documented list).
8. **Required vs optional per field.** Many fields will be null for older
   Era 1 runs (no `cost_manifest.json`, no `post_run_report.md` yet). Decide
   which fields are required vs nullable, and whether the schema validation
   should be lenient for back-fill-in-progress rows.

---

## 4. Constraints and cross-references

- **Document Revision Policy** applies to `results/**.md` — the rendered
  `.md` manifests are in scope. But since they are *generated*, the banner /
  changelog discipline applies to the *generator* and the *JSON source*, not
  hand-edits to the rendered MD. Decide how the rendered MD carries a "do
  not edit; generated from the JSON source" banner.
- **Anti-confabulation** (`~/.claude/CLAUDE.md`): every extracted value must
  trace to a source file. The `provenance.source_files` array is the
  mechanism. The generator must not invent values; missing values are
  `null`, never guessed.
- **Synergy with Phase 1 generator**: the generator
  (`scripts/generate_post_run_report.py`, not yet written) reads the same
  source files to populate the post-run-report template. Extend it to emit
  manifest rows from the same extraction pass. One pipeline, multiple
  outputs.
- **API Call Review Gate**: schema design and the generator are pure
  extraction (no API calls). No gate needed for this work. (The gate applies
  later if any manifest field requires re-running a detection.)

---

## 5. Data sources for population (reference)

| Field group | Source file(s) |
|---|---|
| Front-matter, model, dates, cost, tokens | `outputs/<run>/*.meta.json`, `outputs/<run>/cost_manifest.json` (Era 2 only) |
| Tile counts, bounds | `inputs/.../full_evaluation_manifest.json`, `inputs/vectors/bounds/...`, `results/evaluation-scopes.md` (canonical tile-pool definitions) |
| Metrics (F1/P/R + CIs) | `outputs/<run>/evaluation/*.json`, or `results/<run>/evaluation.json` |
| Hypothesis / config | `configs/run-configs/*.yaml`, `planning/condition-inventory.json` |
| Working-notes Obs | `docs/notes/reflections/working-notes.md` (grep by run path) |
| Historical aliases | manual; `results/evaluation-scopes.md` for Era definitions |
| GS tile-pool assignment | `reports/gs-tile-pool-mapping-2026-05-28.md` |

---

## 6. Read-first for the schema session

1. This brief.
2. `planning/paper-writeup-continuity.md` — Session 91 beacon (manifest
   decision context + H11 principle).
3. `results/evaluation-scopes.md` — canonical tile-pool (Era) definitions;
   the data behind `calibration_set_id` / `test_set_id`.
4. `docs/methodology/output-directory-standard.md` § "Post-Run Report
   Schema" and § "Cross-reference / Lineage Block" — the conventions the
   manifests dovetail with.
5. `reports/gs-tile-pool-mapping-2026-05-28.md` and
   `reports/h11-reorganisation-cost-estimate-2026-05-28.md` — empirical
   inputs.
6. Memory `2026-05-28-3be9d3066363` (H11 scope principle) via `/recall h11`.

---

## 7. Out of scope for the schema session

- **Population** of the manifests (deferred to Phase 1 generator).
- **The H11 reorganisation** (TaskList #17 — happens after schema lock,
  before generator).
- **Lineage-block ID migration** (Phase 4).
- **The generator script itself** (Phase 1).

The schema session's single deliverable: committed JSON Schema files for the
three manifests, plus this brief updated with the resolved decisions.

---

## Changelog

### 2026-05-28 — Original publication

Brief authored at the close of Session 90 to capture the manifest-design
decisions and proposed field lists from that session's planning
conversation, so the schema-design session can start cold without context
loss. Captures 9 locked decisions, proposed field lists for the three
manifests (runs / analyses / passes), 8 open decisions for the schema
session, constraints, data sources, and a read-first list. No schema files
written yet — those are the schema session's deliverable.
