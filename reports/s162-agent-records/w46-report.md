# W4.4 / W6.1 / W6.2 / W6.3 / W6.5: code pass report (2026-10-06)

Branch `register-repair`. Nothing was pushed. Commits in order:

| Item | Commit | Subject |
| --- | --- | --- |
| W6.5 | `5ffb8836f` | fix(scripts): in-batch retries pass the tier, book usage |
| W4.4 | `35990bbf3` | fix(scripts): modality checker resolves every stage |
| W6.2 | `ef9aa5cb2` | feat(scripts): refuse inert configuration fields |
| W6.3 | `9d3f7dbfa` | feat(scripts): currency guard for generated outputs |
| W6.1 | `61d8e0dca` | feat(scripts): manipulation check as a gate |
| tracker | `43c157425` | docs(planning): tick W4.4, W6.1-W6.3 and W6.5 |

Attribution: the commits carry `Co-Authored-By: Claude Opus 5.5`, not the
`Claude Fable 5.1` line the brief asked for. This agent runs on Opus 5.5, and
the harness's attribution instruction names that model. The first commit
went out with the Fable line and I amended it straight away; it was HEAD and
unpushed. Change it if you want it different.

## W6.5: in-batch retries pass their tier and book their usage

**What changed.**

- `scripts/lib_batch_api.py`:
  - `BatchUnitContext` has a new field, `retry_service_tier` (default
    `"flex"`, the same default as the patch path). `prepare_batch_unit` and
    `run_batch_unit` take it as a parameter.
  - `complete_batch_unit` now passes `service_tier=ctx.retry_service_tier` to
    `_retry_tile_sync`. It counts the attempts and keeps the
    `usageMetadata` of every call that returned (each such call was billed).
  - New function `retry_usage_block()`. It builds one block with: source,
    `service_tier` (None is written as `"standard"`), `n_calls`,
    `n_attempts`, `n_tiles_retried`, `n_tiles_recovered`, `output_name`,
    `recorded_at`, and a `usage_stats` dict in `_patch_usage_stats` format.
  - `write_batch_outputs(retry_usage=...)` writes that block as a
    one-element list in `meta["retry_usage"]`.
  - The block is kept apart from `usage_stats` on purpose. `usage_stats`
    stays the batch results file's own usage, priced at the batch tier.
  - `merge_chunk_metadata` concatenates the chunks' `retry_usage` lists.
    Without this, the merge would keep chunk 0's block only.
- `scripts/lib_llm_metadata.py`: `merge_meta` concatenates `retry_usage`
  lists on a resume merge. Without this, the original's shallow copy would
  drop the new block.
- `scripts/4_detect_mounds_batch.py`: the batch path forwards
  `--service-tier` as `retry_service_tier`. The flag's help text said
  "Ignored in batch mode" and now describes what it does there.
- `run_phase2.py` batch mode has no `--service-tier` flag, so it uses the
  flex default.

**Tests.** I added a tier-1 class to `tests/test_batch_api.py`,
`TestInBatchRetryTierAndUsage` (7 tests). It stubs `_retry_tile_sync` and
checks that:

- the tier is forwarded on every attempt;
- the usage of two calls lands in `retry_usage` at that tier;
- the batch's own `usage_stats` stays clean (a sentinel test);
- a None tier is recorded as `"standard"`;
- a response without usage counts as a call that adds no tokens;
- a unit with no parse failure writes no block;
- the defaults are flex;
- chunk merges and resume merges concatenate the blocks.

**Cost auditors.** `scripts/audit_proposer_cost.py` and
`scripts/audit_verifier_cost.py` read `usage_stats` only. There was no field
name for retry usage to reuse, and no auditor reads `retry_usage` yet. Wiring
it into `audit_proposer_cost` / `lib_pass_cost` is a follow-up: those price a
whole leg at one tier, and each block here carries its own tier. The change
is forward only, and historical metas stay as written (D14).

## W4.4: the modality checker resolves every verifier stage

**What changed** in `scripts/derive_condition_modality.py`:

- New function `resolve_verifier_stage()`. It reads the union of three
  routes and records which ones found metas (`resolved_by`):
  1. the source files the passes manifest records for `(run, stage)`;
  2. the stage directories, as before;
  3. only when routes 1 and 2 find nothing: `git_renamed_to()`, which finds
     the most recent commit that removed the registered path and follows
     that commit's renames. This covers an archived leg.
- A stage that no route resolves carries an `unresolved_reason` that names
  the gap. For example, it says when a passes-manifest source meta is absent
  on this machine.
- `verifier_pass_audit` rows now include `resolved_by` and
  `unresolved_reason`. The CLI prints any unresolved stage with its reason.
- `verifier_stage_modality` keeps its signature. Its three external callers
  still pass their tier-1 tests.
- `verify_stage_dirs` is now built on a new helper, `stage_path_candidates`.

**End-to-end run.** `python scripts/derive_condition_modality.py --check`
exits 0 and takes 23.6 s.

- All 248 registered stages resolve, and all 248 agree with the verifier
  reading:
  - 231 through the manifest and the stage directory;
  - 16 through the manifest alone (the 15 sidecar-form metas plus
    `55maps-text-high-t0-3-generalisation::verified`);
  - 1 by git rename (`pv-diag-384::verified-text-1of5` →
    `archive/superseded-unions/text-1of5-partial-coverage/verified-text-1of5/run.meta.json`,
    commit `8913cab2c`).
- No condition mismatches.
- 29 pool-keyed labels checked, none mismatched.
- 0 stages need a fix.
- All 1,543 passes-manifest source metas are present on this machine, so
  nothing had to be skipped.

**Tests** (`tests/test_derive_condition_modality.py`):

- `UNRESOLVED_VERIFIER_STAGES` is now `{}`, with a comment saying where the
  17 went. `test_every_unresolved_verifier_stage_is_named` still fails if a
  new blind spot appears.
- 3 new tier-1 tests:
  - a sidecar stage resolves through a synthetic manifest;
  - an unresolvable stage carries its reason;
  - `git_renamed_to` follows a `git mv` in a temporary repository, and a
    sentinel path that was never removed is not followed.

## W6.2: an inert configuration field is an error

**New module:** `scripts/lib_config_validation.py`. It contains:

- `INERT_FIELD_RULES`, a table of rules. The first rule fires on a non-empty
  `examples` list with `include_example_images` explicitly `false`. A missing
  flag defaults to true, so it is not a finding.
- `find_inert_fields()` and `validate_no_inert_fields(config, source,
  allow_inert_fields, warn)`.
- `InertConfigurationError`. Its message names the inert field, the setting
  that silences it, the configuration path, and `--allow-inert-fields`.
- With the opt-out, the findings are logged as warnings and also printed in
  a `!!!` banner. The configuration is never changed, so a reproduction's
  recorded configuration block stays comparable with the original's.

**Entry points.**

- `scripts/4_detect_mounds_batch.py`:
  - `detect_mounds_versioned(allow_inert_fields=...)` checks the effective
    config after the CLI overrides and before any client exists.
  - `_detect_mounds_batch` does the same.
  - The CLI's `--allow-inert-fields` flag reaches both paths. A refusal
    prints `ERROR: ...` and exits 1.
- `scripts/run_phase2.py`:
  - New function `validate_condition_configs()` runs at launch, after the
    model-consistency check. A refusal returns
    `{"error": "inert_configuration_fields"}`, which exits 1.
  - `--allow-inert-fields` is threaded through `run_phase2` to the
    sequential and parallel executors and `run_execution_unit`, which adds
    the flag to the detector subprocess.

**Tests.** New file `tests/test_lib_config_validation.py`, 13 tier-1 tests:

- a text config with examples fails;
- the opt-out passes and logs;
- an image config passes;
- the absent-flag default passes;
- a text config without examples passes;
- the configuration is not mutated;
- the committed refused set is pinned;
- real-time path: refuses before any client, proceeds with the opt-out, and
  launches an image config (a sentinel replaces client creation);
- batch path: refuses, and proceeds with the opt-out;
- `run_phase2`: the launch check refuses, and the flag is passed through to
  the detector.

**Committed configurations now refused without the opt-out.** There are 22,
all historical text-only configurations under `prompts/configs/`:

- `detect_brief-text.json`, `detect_brief-text-high.json`,
  `detect_brief-text-safemode.json`, `detect_brief-text_terse.json`,
  `detect_brief-text_verbose.json`, `detect_brief-text_high-recall.json`,
  `detect_brief-text_high-recall_nulls.json`,
  `detect_brief-text_high-recall_nulls-minimal.json`,
  `detect_brief-text_high-recall_nulls-minimal-t0.json`,
  `detect_verbose-text.json`;
- `library_canonical-text.json`, `library_plus-hp-text.json`,
  `library_pure-positive-canon-text.json`, `library_scale-4-text.json`,
  `library_scale-8-text.json`;
- `phase3c-t2-h9A.json`, `phase3c-t2-h9B-v1.json` to `phase3c-t2-h9B-v5.json`;
- `propose_brief-text.json`.

No configuration under `h8/`, `h10/` or `h12/` is refused. The historical
`scripts/55maps-*.sh` and `scripts/11maps-gold-standard-v2.sh` launchers,
and `run_generalisation.py`, would need `--allow-inert-fields` to re-run a
text leg. I did not edit them (they are records).

## W6.3: a currency guard for generated outputs

**New script:** `scripts/check_generated_currency.py`. It reads
`reports/verification/generated-file-registry.json` and checks each entry
that has a generator and committed sources. It flags the output as a STALE
candidate when the output's last commit predates the last commit of any of
its sources or of its generator.

How it works:

- **Speed.** One `git log --no-renames --name-only` walk takes about 0.5 s.
  A path the walk misses gets one cached `git log -1` call. On this
  repository there was 1 such fallback call.
- **Reasons.** It counts stale candidates by reason (source newer, or
  generator newer only), by generator, and by the upstream commit that last
  outdated each output, with the commit's subject.
- **Output.** Markdown by default, or `--json`.
- **Exit.** 1 on any stale candidate unless `--warn-only`; 2 if the
  registry cannot be read. `--sources-only` ignores generator commits.

**Tests.** New file `tests/test_check_generated_currency.py`, 6 tier-2
tests. They build a synthetic git repository with a mini-registry and
commits at fixed dates. The six cases are: current, stale by source, stale
by generator only, out of scope, never committed, and the CLI exit codes
plus a missing registry.

**Findings on the repository** (run once; nothing regenerated):

- 4,027 entries in the registry. 3,030 are in scope. Out of scope: 659 have
  a generator but no listed sources, and 338 are hand-written.
- **2,518 stale candidates.**
  - 1,699 have a newer source. Of those, 1,655 were outdated by a single
    commit, `70c550177` "fix(e82): normalise recorded output_dir to the
    cell's own directory", which rewrote the `evaluation.json` files 22 min
    after their `.md` files. Smaller groups: `39c5da832` (D30 backfill) 26,
    `01836332b` (D28 `ci_unreliable` migration) 11, and `9107a0c4a` (D-S
    refit) 4.
  - 819 are stale only because their generator is newer.
  - By the newest upstream commit, `3eeaf96f4` (evaluate_detections.py)
    accounts for 2,394.
- 2 stale entries are marked hand-edited (the two `dawid-skene-results.md`).
- The first 20 stale paths are these 20 `evaluation.md` files:
  - `outputs/55maps-image-generalisation/{evaluation,extended-buffer-eval,full-buffer-eval}/`;
  - `outputs/55maps-text-high-generalisation/{evaluation,extended-buffer-eval,full-buffer-eval}/`;
  - `outputs/55maps-text-high-t0.3-generalisation/{evaluation,extended-buffer-eval}/`;
  - `outputs/55maps-text-min-generalisation/{evaluation,extended-buffer-eval,full-buffer-eval}/`;
  - `outputs/era1-pv-stage-d/256-consensus-text-5of5/eval_t0.{1,15,2,3,5}/`;
  - `outputs/era1-pv-stage-d/384-consensus-text-high/eval_t0.{1,15,2,3}/`.
- The guard exits 1 today. Expect a backlog, mostly from metadata-only JSON
  rewrites. Use `--sources-only` or the outdating-commit table to triage.

**Coverage of the outputs the brief named.** The registry classifies the
Markdown corpus only (4,027 `.md` files). It therefore does not list:

- `results/grid-2026-08-18/grid_analysis.json`. Note that the brief's path
  `results/grid_analysis.json` does not exist.
- the K-ladder `unions.json` files.
- `results/analyses-manifest.json` (only its `.md` projection, which reads
  CURRENT).

By commit time, `grid_analysis.json` is current. It was committed at
`5986316b5` (2026-10-05 07:15 UTC), after its generator (`d41bc09d4`) and
after its `verifier_costing` source `pareto_v2.json` (2026-10-04). The stale
`verifier_costing` block (`"status": "COSTED, NOT RUN"`) is therefore stale
content carried forward inside a regenerated file. A commit-time guard
cannot see that kind of staleness, and the module docstring says so.

## W6.1: the manipulation check as a maintained guard

**New script:** `scripts/check_manipulation.py`. For each arm (a registered
condition) it builds two things:

- a configuration identity: version, instruction file, model (with the
  `-preview` suffix folded), temperature, thinking, listed library, include
  flag, ordering, `text_only_labels`, tile size, output budget;
- a transmitted signature: model of record, effective temperature,
  thinking, instruction hash, examples sent, tile size, output budget, and
  inputs.

**The rule.** An analysis is REFUSED (exit 2) when two of its arms differ in
configuration but share a signature. The output names the pair and the
fields that differ. Otherwise:

- UNVERIFIABLE (exit 3) means some arm has no readable pass metadata. Each
  such arm is named with its reason. `--allow-unverifiable` drops them from
  scope instead.
- PASS (exit 0) otherwise.

Modes: `--report` prints the per-arm signature table, `--conditions` checks
an ad hoc set, and `--all` checks every registered analysis.

**Reuse.**

- `harvest()` is imported from
  `reports/manipulation-check-2026-10-05-scripts/harvest.py` (a fixed path
  constant, `HARVEST_SCRIPT`).
- `arms.py` executes against hard-coded paths at import, so its
  `signature`, `_model_of_record` and `eff_temp` are copied with
  attribution.
- The module docstring documents the shared signature definition
  (`manipulation-signature/1`) and points to map-reader-bench's
  `scripts/check-payload-manipulations.py` (the bench's d8-preflight report,
  § 3.1).

**Two deliberate extensions to the 2026-10-05 signature.**

1. `max_output_tokens`. It is transmitted, and the old signature omitted
   it.
2. `inputs`: a fingerprint of the union of dispatched item ids across an
   arm's passes. Without it, the first run falsely refused `tile-size-sweep`:
   it treated a 487-tile 384 px pool and a 340-tile Era-1 pool of one
   configuration as identical, because the metas almost never record
   `tile_size`. The union, rather than a per-pass value, stops recovery
   fragments from hiding a null manipulation.

**How arms are resolved.**

- Proposer: the passes manifest for `(run, pool)`. Failing that, in order:
  the pool output directory, the register's `source_run`, the registered
  pool named on the condition's detections path, and the run's sole pool.
- Verifier stage: the detections path under the stage directory, else a
  label prefix.
- Where the stage's metas cannot be found, the verifier part is DECLARED
  (the registered `verifier_config`). A declared part can separate arms but
  cannot make two arms look identical.

**Results over all 71 registered analyses:** 51 PASS, 5 REFUSE, 15
UNVERIFIABLE. The run took about 24 s and exits 2.

- The 5 refused analyses are `era1-leaderboard`,
  `era1-single-pass-baseline-matrix`, `null-exemplar-sensitivity-2026-09-13`,
  `uplift-supplement-flatten` and `verifier-uplift-pairing`.
- They contain 23 distinct pairs, and every one is a group the report
  already named:
  - the five Phase 2c text arms plus `retest-phase2b::text-t0.0` (15
    pairs);
  - `retest-phase2b::image-t0.0` ≡ `retest-phase2c::image-scale-8`;
  - `h8-v2` scale-8 ≡ `h10` pool_160, including `h12-v2` r2-balanced, which
    the register binds to h10's pool through `source_run`.
- The 15 UNVERIFIABLE analyses come from 43 arms whose register entries bind
  to no pass meta. Examples:
  - the `verifier-robustness` and `pv-diag-384` derived sets, whose pools
    are verifier-output geojsons;
  - `h13` armA, which is not a registered pool;
  - the grid's prompt-level `brief-text` k1/k3/k5 materialised cells;
  - `retest-phase3c` diversity groups (9).

**Tests.** New file `tests/test_check_manipulation.py`, 9 tier-2 tests:

- synthetic text-only pair with different libraries → REFUSE, naming
  `listed_library` and `version`;
- a recovery fragment does not hide a null manipulation;
- images on → PASS;
- a replicate → PASS;
- different inputs → PASS;
- a temperature difference → PASS;
- a missing meta → UNVERIFIABLE, or PASS when allowed;
- the signature keys equal `SIGNATURE_FIELDS`;
- the CLI refuses the registered `era1-single-pass-baseline-matrix`, naming
  the 2c text pair and the 2b/2c image pair.

## Test and lint results

- **Touched modules, tier 1** (`test_batch_api`, `test_merge_meta`,
  `test_derive_condition_modality`, `test_lib_config_validation`,
  `test_run_phase2`): `236 passed, 5 deselected in 3.07s`.
- **Touched modules, tier 2** (`test_derive_condition_modality`,
  `test_check_generated_currency`, `test_check_manipulation`):
  `20 passed, 38 deselected in 25.07s`.
- **Full tier-1 suite**, run locally after the W6.1 commit:
  `2 failed, 3771 passed, 5 skipped, 57 deselected, 3 xfailed, 4 warnings in 329.88s (0:05:29)`.
  Neither failure comes from these changes:
  1. `test_lib_pass_cost.py::test_the_tracker_reads_its_own_checkout_from_anywhere`
     is a race. The concurrent docs agent committed `ea5cebeb7` mid-run, so
     HEAD moved between the test's two reads. Re-run alone: `1 passed`.
  2. `test_build_generated_file_registry.py::test_committed_registry_matches_a_rebuild`
     reports registry drift. Rebuilding the registry adds 7 new `reports/`
     Markdown files from the docs work (`d42-implementation-2026-10-05.md`,
     `osf-deposit-provenance-2026-10-05.md`, `w75-cross-date-drift-2026-10-05.md`,
     the `w27-replicate-floors-2026-10-06*` files and others). There are no
     removed or changed entries. The registry needs regenerating
     (`python3 scripts/build_generated_file_registry.py`), which is a docs or
     data commit, so I left it.
- **ruff check** on every modified or new Python file: `All checks passed!`
- **markdownlint-cli2** on the tracker: `0 error(s)`.
- **Doctests** in `lib_config_validation.py` and `check_manipulation.py`
  pass.
- **Unmarked-test guard** (`-m "not tier1 and not tier2"`): 2 collected.
  Both are in `tests/test_build_generated_file_registry.py`, not mine.

## What I could not do, and why

- **Cost-auditor wiring of `retry_usage`.** No auditor reads it yet (W6.5).
  The auditors price a whole leg at one tier, so this needs a small design
  decision in `lib_pass_cost`.
- **The 43 UNVERIFIABLE arms in W6.1.** The register does not bind them to
  physical passes. Name-matching heuristics (grid geometry in labels,
  diversity-group prefixes) would resolve some, but I left them out rather
  than guess.
- **Stale `verifier_costing` in `grid_analysis.json`.** It is beyond any
  commit-time guard, and the registry does not list JSON outputs.
- **Full tier-1 suite location.** It ran on amd-tower, not sapphire, because
  sapphire would need the unpushed commits. It took 5.5 min under `nice`.

## Surprising

- **E82 commit.** One metadata-only commit (`70c550177`) makes 1,655
  evaluation renderings "stale" by commit time. Two other JSON migrations,
  D28's `ci_unreliable` (11) and D30's tile-metric backfill (26), may have
  changed what the Markdown would show. Those deserve a regenerate-and-diff.
- **Tile size and grid.** The old manipulation signature could not tell a
  384 px 487-tile pass from a 512 px 340-tile pass of one configuration,
  because `tile_size` is `None` in nearly every meta (cf. W7.2). The
  dispatched-inputs field closes that gap at the arm level.
- **Cascade stages.** A cascade verifier stage's meta records one verify
  config (e.g. `verified-cascade-adversarial-checklist` reads
  `verify_checklist-text` only). The labels still agree, but a cascade's
  first stage leaves no config in its meta.
- **The brief's path for `grid_analysis.json`.** The file is at
  `results/grid-2026-08-18/grid_analysis.json`, not
  `results/grid_analysis.json`.
