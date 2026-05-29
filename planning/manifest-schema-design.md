# Manifest Schema Design Brief

> **Last revised**: 2026-05-29 (added the deviation-run identity convention —
> E43 worked example, § 1A; the 4-entity model and field lists are unchanged).
> See [§ Changelog](#changelog) for revision history.

**Status**: Decisions **resolved**; JSON Schema files authored under
`docs/manifest-schemas/`. This brief now records the resolved
schema decisions (it began life as the pre-session brief of proposals). The
entity model and per-level field lists below are the current truth; the
schema files are their machine-readable encoding. Population of the manifests
remains out of scope (deferred to the Phase 1 generator).

> **Recovery note**: the schema-design session (Session 91, 2026-05-28)
> crashed mid-conversation on an unrecoverable `thinking`-block API error.
> The reasoning was recovered from the session transcript
> (`8529ef59-9d20-4d03-a3a1-01193d026c4e`) and is captured here. No design
> decision was lost.

**Purpose**: The project is replacing the overloaded "Era 1 / 2 / 3"
terminology with empirical, machine-readable manifests of runs, conditions,
passes, and analyses. These manifests become the canonical structured
representation of the experimental work; prose docs reference entries by ID.
They are also intended as paper supplementary material (reproducibility /
transparency).

---

## 1. Decisions (locked + resolved this session)

Items 2–9 were settled in the Session 90 planning conversation and were
treated as fixed inputs. Item 1 was **deliberately reopened and revised** in
the schema-design session (3 manifests → a 4-entity model); the revision is
recorded in place below and in the [Changelog](#changelog). For the full
worked rationale of the entity model, see [§ 1A](#1a-resolved-entity-model-schema-design-session).

1. **Four entities + study-as-grouping + a run registry** (revised from the
   original "three manifests: runs / analyses / passes"). The normalised
   chain is `study → run → condition → pass`, with analyses sitting over
   conditions:
   - `runs`, `conditions`, `passes`, `analyses` are entities (each its own
     manifest). `conditions` and `passes` carry a foreign key to `runs`;
     `analyses` reference `conditions`.
   - `study` is **not** an entity — it is a grouping tag carried on runs
     (`primary_hypothesis` + `also_informs[]`); study *findings* live in
     analyses. Promotable to a `studies-manifest.json` later without breaking
     the chain.
   - A **run registry** (`run_id → directory_path`) is the enumeration
     mechanism and the generator's input. Its format is defined this session;
     it is populated in Phase 1.
2. **JSON-canonical, Markdown-rendered**: the JSON file is the source of
   truth; a script renders human-readable Markdown tables from it. Humans do
   not hand-edit the rendered Markdown.
3. **Location**: `results/` (i.e. `results/runs-manifest.json`,
   `results/conditions-manifest.json`, `results/passes-manifest.json`,
   `results/analyses-manifest.json`, `results/run-registry.json`, plus the
   rendered `.md` siblings).
4. **Sequencing III — schema-first, populate-later**: design and commit the
   schemas in this session; defer population until Phase 1 (the generator
   script) writes both per-run post-run-reports and manifest rows from the
   same extraction pipeline.
5. **Generator-as-only-writer** for `runs`, `conditions`, and `passes`: these
   are machine-extracted from source-of-truth files (`*.meta.json`,
   `cost_manifest.json`, `evaluation/*.json`, bounds manifests, YAML
   configs). Humans edit the *source* files, never the manifest; the
   generator re-extracts. The user confirms source-of-truth files are
   accurate or have known issues already captured in errata / working-notes.
6. **Analyses manifest is hybrid**: machine-fills the auto-extractable
   fields (`analysis_id`, `output_path`, `working_notes_obs`); humans author
   `outcome`, `paper_section`, the preregistration linkage; each
   human-authored row carries a `manually_verified_at` timestamp; the
   generator never overwrites human-authored fields.
7. **"Era" retired going forward**, but preserved as `historical_aliases`
   field values so existing prose (paper drafts, working-notes Obs entries,
   the README) stays traceable. We do not rewrite the past; we recognise
   prior "Era" usage as an alias.
8. **Lineage-block integration** (Phase 4, not this session): the `## See
   also` blocks codified in `docs/methodology/output-directory-standard.md`
   will reference manifest IDs (`run:<id>`, `analysis:<id>`) instead of
   opaque paths. The ID conventions are designed to survive directory renames
   (stable `run_id` slug + mutable `directory_path`) so lineage references
   stay valid.
9. **H11 scope principle** (memory `2026-05-28-3be9d3066363`): governs the
   `primary_hypothesis` / `also_informs` field values for `outputs/h11/`
   runs. H11 = the tile-size study + the 384px detection-approach
   characterisation that fed the H11 leaderboard. See the Session 91 beacon
   in `planning/paper-writeup-continuity.md` for the stay/move classification.

---

## 1A. Resolved entity model (schema-design session)

The pre-session brief proposed three flat manifests. Walking the design
against the *actual* filesystem (three Explore agents + direct re-reads of
`*.meta.json`, `condition-inventory.json`, and the WBF fusion script) forced
a cleaner, normalised four-entity model. The reasoning, for the record:

### Why four entities, not three

The brief's `passes` manifest mixed two kinds of field: **per-pass execution
facts** (tokens, cost, wall-clock, retries) and **config that is constant
across every pass of a configuration** (model, thinking level, temperature,
thresholds). Storing the latter per-pass repeats it N times. Splitting a
**condition** level out removes the redundancy — and the data showed why it
is conceptually necessary, not just tidier:

- **Generation vs evaluation are different jobs.** A *proposer config* (model,
  modality, thinking, temperature, library, prompt) produces raw detection
  passes (`run_1 … run_K`) — this is where **cost** lives. An *aggregation +
  threshold + verifier config* turns those passes into one scored, evaluable
  detection set (`consensus-n5`, `verified-v1-n10`, `greedy`, `wbf`) — this is
  where **metrics** live. The brief's single "condition" was doing both jobs.
- **N-sweeps share a pass pool.** Verified on disk:
  `pv-diag-384/scale-4-optimal-487/` holds `run_1 … run_10` *plus*
  `consensus-n5`, `verified-v1-n5`, `verified-v1-n10`, `consensus`. `…-n5` and
  `…-n10` are the **same** proposer passes aggregated at N=5 vs N=10. So a
  "condition" cannot *own* its passes — it *consumes the first N* of a pool
  the run owns.

The resolution moves passes **up to the run** and lets the metric-bearing unit
*reference* them:

| Entity | Is | Owns | Key fields |
|---|---|---|---|
| **run** | one coherent execution unit (≈ one `post_run_report`'s worth) | — | study tags, corpus, GT reference, tile grid, nominal scope |
| **pass** | one raw proposer/verifier execution (`run_N`) | the **generation config + cost** | model (from metadata), modality, thinking, temp, hashes; tokens / cost / timing / retries / status. FK → run |
| **condition** | one *evaluable scored result* (= a leaderboard cell) | the **metrics** | aggregation, n_passes, vote/prob thresholds, verifier config; per-buffer F1/P/R + buffer-agnostic tile block (MCC/sens/spec); references its source passes. FK → run |
| **analysis** | a comparison / finding over conditions | — | `conditions_compared[]`, prereg linkage, outcome |

(+ **study** = a grouping tag on runs, as decided; **run registry** = the
`run_id → directory_path` enumeration table.)

### Why study is a grouping tag, not an entity

The decisive test is cardinality, checked against the data. `pv-diag-384/`
simultaneously feeds **four** studies (H11 tile-size, PV-strategy comparison,
consensus N-sweep, Flash-vs-Pro). So **run ↔ study is many-to-many** — a
single scalar FK cannot express it. The scientific groupings *are* analyses
that select subsets of conditions across runs; a study's *finding* is the
output of an analysis. A studies entity would therefore be a thin shell
duplicating the preregistration + analyses. The reversible choice is a
grouping tag now, promotable to an entity later. The run carries a
**`primary_hypothesis`** (the clean single-value grouping for the common
query) plus **`also_informs[]`** (the M:N tail).

### Why no fifth "proposer-pass-set" entity

A pass-set (the group of passes sharing one generation config) is *derivable*
by grouping passes on their config fields — the same call made for "study". A
focused git-history + working-notes investigation confirmed the load-bearing
fact: **cross-config / cross-model fusion was never executed.** Every entry in
`SPECIAL_CONFIGS` (`scripts/fuse_detections_wbf.py`) fuses passes from a single
proposer configuration; the H9 "diversity dividend" (Obs 140–148) was
diversity *within* one config's passes, not fusion across configs. Therefore
**condition → pass is a simple reference** (`proposer_pool` + `n_passes`, the
prefix rule), not a many-to-many lineage table. An optional explicit
`source_pass_ids[]` is retained for the rare non-prefix case but is not
required.

### Headline metric — no auto-"best"

Because metrics live on the **condition**, the run never needs to compute a
single "best" condition (which would over-claim when CIs overlap). Instead the
run carries a **human-designated** `headline_condition_id` (FK) +
`headline_rationale`; statistical ties between conditions are recorded as an
**analysis** (`tie_set[]`), where the indistinguishability scientifically
belongs.

### Identity decoupled from location

`run_id` is a **stable flat slug** (no slashes — a slash would re-encode the
path), seeded from the leaf directory name and group-prefixed only where the
bare leaf is not globally unique (`retest-phase2a`). It is assigned once and
never changes. `directory_path` is a **separate, mutable** field the generator
refreshes. The H11 reorganisation (executed Session 92, 2026-05-29) edited
`directory_path` for the moved runs; every FK and lineage reference survived
untouched. This is the mechanism that satisfies locked decision #8.

### Deviation runs keep a neutral identity (E43 worked example)

The same identity-vs-location decoupling resolves a question the H11
reorganisation surfaced (Session 92, 2026-05-29): how to identify a run whose
*physical directory name* encodes a protocol deviation. The H11 consensus run
executed at T=1.0 instead of the intended T=0.7 (erratum **E43**) and was
renamed `consensus-384-UNINTENDED-T1.0` to flag this at the point of use — at a
time when no structured deviation record existed. That "shout-in-the-filename"
is brittle (it accreted ~150 references) and conflates **identity** with
**status**.

The schema's resolution: the **`run_id` is the neutral, parameter-descriptive
identity**; the deviation is **status carried in metadata**, never welded into
the identity string. For E43 the generator assigns:

- `run_id`: `consensus-384-t1.0` — neutral slug (architecture + tile size +
  *actual* temperature, read from `*.meta.json`), no pejorative.
- `directory_path`: `outputs/h11/consensus-384-UNINTENDED-T1.0` — the physical
  location is left **unchanged** (no mass rename of the ~150 references); it is
  now an incidental breadcrumb, not the identity.
- `historical_aliases`: `["consensus-384-UNINTENDED-T1.0"]` — preserves the old
  shout-name so existing prose and result-file paths stay searchable (the field
  was designed for exactly this; see locked decision #7).
- The **deviation linkage lives on the analysis**, not the run: the
  T=0.7-vs-T=1.0 temperature analysis that consumes this run's conditions
  records `preregistered: preregistered-with-deviation` and
  `deviations: ["E43"]` (§ 2.4) — where the deviation scientifically belongs.

**Generator rule**: read the *actual* parameters from `*.meta.json` (here
`temperature: 1.0`) to mint the neutral `run_id`; never propagate a
status-bearing directory name into the identity. **Open schema consideration**
(flag, do not assume): whether to add an optional run-level `deviations: []`
field for at-a-glance visibility in the runs manifest, versus relying solely on
the analysis-level linkage above. The unused counterpart run (erratum **E44**,
`single-pass-384-UNINTENDED-T1.0`) was archived to
`archive/h11-unintended-t1.0/` in the same reorganisation and is simply omitted
from the run registry.

---

## 2. Field lists (resolved)

These are the resolved per-level fields, encoded in the schema files under
`docs/manifest-schemas/`. Types and required/optional status are
given here; the schema files are authoritative for validation.

### 2.1 Runs manifest — one row per run

| Field | Type | Req. | Source | Notes |
|---|---|---|---|---|
| `run_id` | string | ✓ | registry | stable flat slug (PK); no slashes |
| `directory_path` | string | ✓ | filesystem | **mutable**; current `outputs/<...>` location |
| `primary_hypothesis` | string \| null | ✓ | config / manual | main study grouping (e.g. `H11`); null for non-hypothesis runs |
| `also_informs` | array[string] | – | manual | secondary studies/hypotheses (the M:N tail) |
| `purpose` | string \| null | – | manual | free-text for genuinely non-hypothesis runs (dev / debug / exploratory) |
| `run_type` | string (enum) | – | inferred | coarse architecture family: `single-pass` / `consensus` / `proposer-verifier` / `mixed` |
| `tile_size_px` | integer | ✓ | bounds / tile manifest | 256 / 384 / 512 |
| `corpus` | string | ✓ | manual / bounds | which map sheets (`4-map-gs` / `55-map` / subset) |
| `gt_reference` | string (enum) | ✓ | manual | `curator` / `student` / `combined` |
| `scope` | object | ✓ | bounds manifest | nominal/default evaluation scope: `test_set_id`, `bounds_path`, `n_test_tiles`, `calibration_set_id`, `n_calibration_tiles` |
| `headline_condition_id` | string \| null | – | **human** | FK → the designated headline condition |
| `headline_rationale` | string \| null | – | **human** | why that condition; notes any statistical tie |
| `post_run_report_path` | string \| null | – | filesystem | null if not yet authored |
| `working_notes_obs` | array[string] | – | grep | `Obs N — title` (no line numbers; they drift) |
| `historical_aliases` | array[string] | – | manual | e.g. `["Era 2", "the v2 GS run"]` |
| `provenance` | object | ✓ | generator | `source_files[]`, `last_extracted_at`, `extractor_version` |

*Derived, not stored* (compute-on-demand; recipes in the spec/README):
`dates_run` (min/max of pass timestamps), `total_cost_usd` (sum of pass cost).

### 2.2 Conditions manifest — one row per evaluable scored result (NEW level)

| Field | Type | Req. | Source | Notes |
|---|---|---|---|---|
| `condition_id` | string | ✓ | derived | PK (see ID convention, § 3) |
| `run_id` | string | ✓ | parent | FK → runs |
| `label` | string | ✓ | dir / meta | e.g. `flash-high-text-n5` |
| `architecture` | string (enum) | ✓ | config | `single-pass` / `consensus` / `proposer-verifier` |
| `aggregation` | string (enum) | ✓ | config | `none` / `greedy` / `wbf` / `consensus` / `verified` |
| `proposer_pool` | string | ✓ | derived | identifier of the source proposer config (the pass pool this draws from) |
| `n_passes` | integer | ✓ | config | the first N of `proposer_pool` consumed |
| `source_pass_ids` | array[string] | – | derived | explicit pass FKs; only for the rare non-prefix selection |
| `vote_threshold` | number \| null | – | config | consensus vote threshold |
| `prob_threshold` | number \| null | – | config | probability threshold |
| `verifier_config` | object \| null | – | YAML | verifier variant, scale, calibration pool, instruction file |
| `scope_override` | object \| null | – | bounds | as-evaluated scope when it diverges from the run's nominal scope (rare, ~2%) |
| `metrics` | object | ✓ | `evaluation/*.json` | **two-part**, see below |
| `n_candidates` / `n_detections` / `n_reference_mounds` | integer | – | `evaluation/*.json` | detection counts |
| `provenance` | object | ✓ | generator | as above |

`metrics` object shape:

- `per_buffer`: keyed by buffer radius `20` / `30` / `40` / `50` (m) → `{ f1,
  precision, recall, ci: { low, high, method: "BCa", n_iter, seed: 42,
  resampling: "tile-level" }, coverage, ci_unreliable }`.
- `tile_classification` (buffer-agnostic, single block): `{ mcc, sensitivity,
  specificity, tp, tn, fp, fn }`. **MCC always present** at this level (per
  standing preference), even where cross-scope tile-matching is required.

### 2.3 Passes manifest — one row per raw proposer/verifier execution

| Field | Type | Req. | Source | Notes |
|---|---|---|---|---|
| `pass_id` | string | ✓ | derived | PK (see ID convention, § 3) |
| `run_id` | string | ✓ | parent | FK → runs (passes belong to the run, not the condition) |
| `proposer_pool` | string | ✓ | derived | which generation config produced this pass |
| `pass_n` | integer | ✓ | meta / dir | the Nth pass (`run_N`) in the pool |
| `model_used` | string | ✓ | `per_item_metadata.model_used` | **authoritative**; never inferred from the directory name |
| `model_requested` | string \| null | – | `per_item_metadata.model_requested` | what was asked for (may differ from used) |
| `model_version` | string \| null | – | `per_item_metadata.model_version` | API-reported version string |
| `modality` | string (enum) | ✓ | meta / config | `image` / `text` |
| `thinking_level` | string \| null | – | meta | `minimal` / `low` / `medium` / `high` |
| `temperature` | number \| null | – | meta | |
| `instruction_hash` | string \| null | – | config | system-instruction hash (detects silent prompt drift) |
| `library_hash` | string \| null | – | config | few-shot library hash |
| `status` | string (enum) | ✓ | `*.tiles.json` | `ok` / `partial` / `failed` |
| `n_tiles_processed` | integer | ✓ | `*.tiles.json` | |
| `tokens` | object | – | `*.meta.json` | input billed / cached / output / thinking / total |
| `cost_usd` | number \| null | – | `*.meta.json` | |
| `wall_clock_s` | number \| null | – | `*.meta.json` | |
| `timestamps` | object \| null | – | `*.meta.json` | start / end (UTC); feed the run's derived `dates_run` |
| `retries` | integer | – | `*.meta.json` | |
| `provenance` | object | ✓ | generator | the `*.meta.json` path |

### 2.4 Analyses manifest — one row per analysis

| Field | Type | Req. | Source | Notes |
|---|---|---|---|---|
| `analysis_id` | string | ✓ | `results/` subdir name | PK (see ID convention, § 3) |
| `type` | string (enum) | ✓ | manual | `comparison` / `leaderboard` / `sweep` / `diagnostic` / `classification` / `gt-audit` |
| `conditions_compared` | array[string] | ✓ | manual + auto-suggest | FKs → `condition_id` (**changed** from `runs_compared`: studies compare conditions) |
| `hypothesis_refs` | array[string] | – | **human** | controlled vocab `H1 … H15` + named programmes |
| `preregistered` | string (enum) | – | **human** | `preregistered` / `exploratory` / `preregistered-with-deviation` |
| `deviations` | array[string] | – | **human** | D-/E-numbers from `decisions-log.md` / `protocol-errata.md` |
| `predicted_outcome` | string \| null | – | **human** | what the prereg predicted |
| `tie_set` | array[string] | – | **human** | conditions found statistically indistinguishable |
| `outcome` | string | – | **human** | one-sentence headline finding |
| `paper_section` | string (enum) | – | **human** | `Methods` / `Results` / `Discussion` / `Limitations` / `Appendix` |
| `output_path` | string | ✓ | filesystem | `results/<analysis_id>/` or a top-level `.md` |
| `working_notes_obs` | array[string] | – | grep | `Obs N — title` |
| `manually_verified_at` | string (ISO) \| null | – | human | set when a human authors/verifies the row |
| `provenance` | object | ✓ | generator | as above |

### 2.5 Run registry — the enumeration table

| Field | Type | Req. | Notes |
|---|---|---|---|
| `run_id` | string | ✓ | stable flat slug (PK) |
| `directory_path` | string | ✓ | current location; the one field the H11 reorg edits |
| `status` | string (enum) | – | `active` / `archived` |
| `notes` | string \| null | – | e.g. why a dir is omitted, or a rename history pointer |

The registry's rows define *what is a run* (hand-verified — no path-depth rule
can enumerate runs reliably, since the same depth means "condition" in one
subtree and "run" in another). Non-runs (`outputs/results/`, `figures/`,
`qgis-*/`, stub manifests) are simply omitted.

---

## 3. Schema-session sub-decisions — resolutions

The original §3 listed eight open decisions. Their resolutions follow. Items
marked **(locked)** were settled with the user; items marked **(proposed)**
are assistant defaults made to author the schemas — low-stakes and easily
revised, flagged here for veto.

1. **`run_id` convention** — **(locked)** stable flat slug, no slashes, seeded
   from the leaf name, group-prefixed where the bare leaf is not globally
   unique. Location decoupled into the mutable `directory_path`. The original
   "run boundary = directory containing `post_run_report.md`" rule is
   **rejected** — only ~3 such reports exist today, and the enumeration is the
   hand-verified registry instead.
2. **`analysis_id` convention** — **(proposed)** the `results/` subdir name
   (lowercased, hyphenated). Top-level `.md` analyses get a row whose
   `output_path` is the file and whose `analysis_id` is the filename stem.
3. **`pass_id` convention** — **(proposed)** `{run_id}::{proposer_pool}::run{N}`.
   (Passes now belong to the run, so the condition no longer appears in the
   key.) The `*.meta.json` path is retained in `provenance`.
4. **`condition_id` convention** — **(proposed)** `{run_id}::{label}` (e.g.
   `pv-diag-384::flash-high-text-n5`).
5. **Pass-level granularity** — **(locked)** separate `passes-manifest.json`,
   passes FK to the run; per-run "Passes" tables render from it filtered by
   `run_id`.
6. **Schema versioning + file location** — **(locked)** top-level
   `schema_version` (`"1.0"`) on each manifest. **(proposed)** the JSON Schema
   validation files live in `docs/manifest-schemas/`
   (`runs-manifest.schema.json`, etc.) — a dedicated subdir, since there are
   now five of them. `extractor_version` tracks the **generator script**
   version (semver); a separate `schema_version` tracks the format.
7. **Provenance object shape** — **(locked)**
   `{ "source_files": [...], "last_extracted_at": "<ISO>", "extractor_version": "<semver>" }`.
8. **`experiment_program` enum vs free-text** — **(resolved by the model
   change)** superseded by `primary_hypothesis` + `also_informs[]`. Hypothesis
   references use a **controlled vocabulary** (`H1 … H15` plus a documented
   list of named programmes); `purpose` is the free-text escape hatch.
9. **Required vs optional per field** — **(proposed)** marked in the § 2
   tables. Validation is **lenient** for back-fill-in-progress rows: only
   identity + FK + provenance fields are strictly required; metric/cost fields
   are nullable so older Era 1 runs (no `cost_manifest.json`, no
   `post_run_report.md`) validate while incomplete.

---

## 4. Constraints and cross-references

- **Document Revision Policy** applies to `results/**.md` — the rendered
  `.md` manifests are in scope. But since they are *generated*, the banner /
  changelog discipline applies to the *generator* and the *JSON source*, not
  hand-edits to the rendered MD. The rendered MD carries a "do not edit;
  generated from the JSON source" banner at the top (the generator emits it).
- **Anti-confabulation** (`~/.claude/CLAUDE.md`): every extracted value must
  trace to a source file. The `provenance.source_files` array is the
  mechanism. The generator must not invent values; missing values are
  `null`, never guessed. The `model_used` field specifically must be read
  from `per_item_metadata.model_used`, never inferred from a directory name
  (a `pro-`named condition was verified to have run on Flash — memory
  `2026-05-28-b6bc50ca773e`).
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
| Model, dates, cost, tokens (per pass) | `outputs/<run>/.../run_N/*.meta.json` (`per_item_metadata[].model_used/model_requested/model_version`), `cost_manifest.json` (Era 2 only) |
| Tile counts, bounds, scope | `inputs/.../full_evaluation_manifest.json`, `inputs/vectors/bounds/...`, `results/evaluation-scopes.md` (canonical tile-pool definitions) |
| Metrics (per-buffer F1/P/R + CIs; tile MCC/sens/spec) | `outputs/<run>/evaluation/*.json`, or `results/<run>/evaluation.json` |
| Hypothesis / config / hashes | `configs/run-configs/*.yaml`, `planning/condition-inventory.json` |
| Working-notes Obs | `docs/notes/reflections/working-notes.md` (grep by run path) |
| Historical aliases | manual; `results/evaluation-scopes.md` for Era definitions |
| GS tile-pool assignment | `reports/gs-tile-pool-mapping-2026-05-28.md` |
| Preregistration linkage | `docs/methodology/preregistration/`, `decisions-log.md`, `protocol-errata.md` |

---

## 6. Read-first for the schema session

1. This brief.
2. `planning/paper-writeup-continuity.md` — Session 91 beacon (manifest
   decision context + H11 principle).
3. `results/evaluation-scopes.md` — canonical tile-pool (Era) definitions;
   the data behind `scope` (`calibration_set_id` / `test_set_id`).
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
- **A normative `manifest-standard.md` spec** — the general level definitions
  (study / run / condition / pass) and the entity-vs-grouping rule are
  captured in § 1A here and in the schema `$comment` fields; promoting them to
  a standalone normative spec for *future projects* is a follow-up, not part
  of this session's deliverable.

The schema-design session's deliverable: committed JSON Schema files for the
manifests, plus this brief updated with the resolved decisions. **Both done**
(schemas under `docs/manifest-schemas/`; this brief).

---

## Changelog

### 2026-05-29 — Deviation-run identity convention (E43)

**Refresh trigger**: the H11 reorganisation (Session 92) raised how to identify
a run whose physical directory name encodes a protocol deviation. Resolved by
applying the existing `run_id`/`directory_path` decoupling to the
identity-vs-status question.

**What changed**: added the § 1A subsection "Deviation runs keep a neutral
identity (E43 worked example)" — the generator mints a neutral `run_id`
(`consensus-384-t1.0`), leaves the physical `directory_path` unchanged, records
the old name in `historical_aliases`, and carries the deviation linkage on the
analysis (`preregistered-with-deviation`, `deviations: ["E43"]`). Flagged an
open consideration: an optional run-level `deviations[]` field. Also refreshed
the stale "TaskList #17" reference (the reorg is now executed).

**What did NOT change**: the entity model, the per-level field lists, and the
resolved sub-decisions (§§ 1–3) are unchanged; this adds a worked-example
identity convention for the Phase 1 generator only.

### 2026-05-28 — Schema-design session: 4-entity model resolved

**Refresh trigger**: the schema-design session (Session 91) walked the
proposed three-manifest design against the real filesystem and deliberately
revised it. Session crashed on an API `thinking`-block error; decisions
recovered from transcript `8529ef59-9d20-4d03-a3a1-01193d026c4e` and captured
here.

**What moved**:

| Item | Before (pre-session brief) | After (resolved) |
|---|---|---|
| Manifests | 3 (runs / analyses / passes) | 4 entities (runs / conditions / passes / analyses) + study-as-grouping + run registry |
| Metrics home | runs manifest (`headline_f1`) | **conditions** (per-buffer F1/P/R + tile-level MCC block) |
| Config home | passes manifest | **passes** (generation config) + **conditions** (aggregation/threshold/verifier) |
| Pass ownership | per condition | **per run** (conditions reference the first N) |
| Study | `experiment_program` scalar on runs | grouping tag (`primary_hypothesis` + `also_informs[]`); findings in analyses |
| Analyses target | `runs_compared` | **`conditions_compared`** |
| `run_id` | path relative to `outputs/` (slashes) | stable flat slug + mutable `directory_path` |
| Headline metric | auto `headline_f1` on run | human-designated `headline_condition_id` + rationale; ties → analyses |

**What did NOT change**: locked decisions 2–9 (JSON-canonical + MD-rendered;
`results/` location; schema-first sequencing; generator-as-only-writer;
hybrid analyses; "Era" retired-as-alias; lineage-block integration deferred to
Phase 4; H11 scope principle). Population remains out of scope.

**New finding folded in**: cross-config / cross-model fusion was never
executed (`scripts/fuse_detections_wbf.py` `SPECIAL_CONFIGS` all single-config;
H9 diversity was within-config) → condition → pass is a simple
prefix-reference, no M:N lineage table needed.

**Deliverable landed**: JSON Schema (draft 2020-12) files under
`docs/manifest-schemas/` (runs, conditions, passes, analyses,
run-registry). Commit hash: `3204993e`.

### 2026-05-28 — Original publication

Brief authored at the close of Session 90 to capture the manifest-design
decisions and proposed field lists from that session's planning
conversation, so the schema-design session can start cold without context
loss. Captured 9 locked decisions, proposed field lists for three manifests
(runs / analyses / passes), 8 open decisions for the schema session,
constraints, data sources, and a read-first list. No schema files written
yet — those are the schema session's deliverable.
