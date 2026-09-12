# Name-keyed cache hardening — implementation report

> **Last revised**: 2026-09-12 (original publication). See [§ Changelog](#changelog) for revision history.
>
> **Implements**: fixes 2, 4, 5, 6, and 7 of
> [`reports/name-keyed-cache-audit-2026-09-12.md`](name-keyed-cache-audit-2026-09-12.md)
> § 5, approved by the Principal Investigator (PI) on 2026-09-12 as a
> pull-request-sized branch for review because it touches the experiment runner.
> Fix 1 (bootstrap confidence intervals) and fix 3 (the `-opmax` archived
> counts) are **not** in scope here — fix 1 is another agent's branch, fix 3
> already landed on `main`.
>
> **Branch**: `worktree-agent-a7e988cf0b4419ae7`, five commits on top of
> `210086e15`. Zero Application Programming Interface (API) calls; no
> experiment was run.

## 1. What the class is, and what "hardening" means here

The audit's defect class is a derived artefact keyed by a **name** — a label, a
path, a stage name, or merely "a file is present" — rather than by the
**content** it was built from. Nothing errors when the content changes under
that name; the derived value simply goes on serving. Every fix below therefore
does one of exactly two things:

1. **Records a content anchor** — a hash of the bytes an artefact was built
   from, written into the artefact itself; or
2. **Compares that anchor before reuse**, and refuses (or warns, where the
   anchor is absent) instead of assuming a match.

Nothing else changed. In particular: no cached, committed, or derived number
was recomputed, and no behaviour changes for a run that is not resumed or an
input that has not changed. § 7 states that negatively and in detail.

**The one rule that recurs in every fix**: an artefact with no recorded anchor
is reported as **UNKNOWN provenance**, never as a match. Reading "something
ran" as "this configuration ran" is the defect class itself, so backwards
compatibility is expressed as an explicit unknown, not as a silent pass.

## 2. Fix 7 (audit row 26) — the shared helper

Committed first because fixes 2, 4, and 6 use it.
Commit `41ea08c5e`. New module: `scripts/lib_content_anchor.py`.

| What | Where | Why |
|---|---|---|
| `git_blob_hash(path)` | `scripts/lib_content_anchor.py:99` | The value `git hash-object <path>` prints, computed in pure Python (`SHA-1("blob " + size + "\0" + bytes)`), so it works for paths outside the repository and needs no subprocess. `scripts/materialise_opmax_cells.py:125-141` records the same anchor by shelling out for repository-relative paths; this generalises it so test fixtures and temporary materialisations can be anchored too. |
| `config_hash(config)` | `:129` | Canonical-JavaScript-Object-Notation SHA-256 of a configuration; key-order-independent and `Path`-tolerant (command-line overrides install `Path` objects where the YAML had strings). |
| `config_hash_of_files(paths)` | `:153` | The same, over a set of files' blob hashes — a shell driver's "configuration" is usually a prompt config plus an instruction file. A missing file contributes the literal `"missing"`, so absence changes the hash. |
| `write_done_marker` / `read_done_marker` / `done_marker_matches` | `:178`, `:209`, `:232` | A `.done` marker that records the config hash of the work it marks, and the checker that reads it. |
| Command-line interface for shell drivers | `:307` (`main`) | `hash-config`, `write-done`, `check-done`, documented in the module docstring as the replacement for `touch <marker>`. |

`check-done` exits 0 **only** on a verified match, printing:

```text
outputs/run_07/.done: mismatch (config_hash 4f2c9a1b77de)
```

and exits 1 for `mismatch`, `missing`, and `unknown-provenance` alike, so a
shell `if` re-runs the work. The audit's row 26 drivers
(`scripts/gemini37-overnight.sh` and siblings) are **deliberately not
retrofitted**: their campaigns are complete and their markers are history. The
docstring is addressed to the next driver.

## 3. Fix 2 (audit Finding 3) — the generalisation resume

Commit `dc83a5918`. `scripts/run_generalisation.py` (version 1.0.0 → 1.1.0).

The defect: `cmd_all` skipped any stage whose **name** appeared in
`.resume_state.json`, and `_prepare_run` rewrote `resolved_config.yaml`,
`launch_manifest.json`, and `experiment_intent.md` from the *current* config
before that decision was taken. Edit the verifier config (or a temperature, or
`prob_threshold`), re-invoke with `--resume`, answer yes: the completed stages
keep their old-config outputs while every provenance artefact describes the new
config. This is the pipeline for the one remaining registered API run, and its
headline F1 is paper-facing.

| What changed | Where |
|---|---|
| `_resolved_config_snapshot()` — one definition of the snapshot, both written to `resolved_config.yaml` and hashed | `scripts/run_generalisation.py:2285` |
| `_resolved_config_hash()` | `:2309` |
| `_flatten_snapshot()` / `_snapshot_diff()` — dotted field-level diff | `:2321`, `:2344` |
| `_refuse_config_change()` + the shared override hint | `:2377`, `:2368` |
| `_reconcile_resolved_config()` — compare, do not clobber, on resume | `:2391` |
| `_check_resume_config()` — per-stage anchor comparison | `:2461` |
| `_save_resume_state(..., config_hash_value=, config_snapshot=)` — records the hash beside each stage, and the snapshot once under `_config` | `:2534` |
| `_intent_body()` + `write_experiment_intent(preserve_existing=)` — an existing intent file is compared, not rewritten | `:1779`, `:1798` |
| Wiring: `cmd_all` checks before any stage runs; `_prepare_run` reconciles instead of writing | `:1950-1968`, `:2095`, `:2136` |
| New `--allow-config-change` flag (on every subcommand, beside `--resume`) | `:2634` |

### The two new refusals, verbatim

`_prepare_run`, when `--resume` meets a snapshot written from another config:

```text
Refusing to resume: outputs/gen-run/resolved_config.yaml was written from a different resolved configuration.
  Differences (recorded → current):
    - proposer.temperature: 0.3 → 0.7
  Re-run with --allow-config-change to proceed anyway (the change is logged and
  recorded in .resume_state.json, and the run becomes a mixed-configuration run),
  or launch into a fresh output_dir.
```

`cmd_all`, when a completed stage's recorded hash disagrees:

```text
Refusing to resume: the resolved configuration differs from the one that produced the completed stage(s) in .resume_state.json.
  Stages already complete under the recorded configuration: consensus, proposer
  Recorded config hash 0f1e2d3c; current 9a8b7c6d.
  Differences (recorded → current):
    - verify.config: prompts/configs/verify_a.json → prompts/configs/verify_b.json
  Re-run with --allow-config-change to proceed anyway (the change is logged and
  recorded in .resume_state.json, and the run becomes a mixed-configuration run),
  or launch into a fresh output_dir.
```

A stage with no recorded hash (any state file written before this branch) warns
instead:

```text
Resume: stage(s) proposer carry no config_hash (recorded before resume
provenance was added). Their configuration is UNKNOWN and cannot be verified —
treat their outputs as unverified provenance rather than as a match.
```

An unparseable `resolved_config.yaml` warns and is left in place:

```text
<path> is not a readable config snapshot: resume provenance is UNKNOWN, so the
configuration cannot be verified. Leaving the file in place (not overwriting).
```

The `experiment_intent.md` precedent is `lib_experiment_intent.write_experiment_intent`,
which verifies rather than overwrites an existing intent; on a resume the
generalisation launcher now behaves the same way and logs
`… exists and matches the current config; not overwriting.` or, on a material
difference, `… Leaving the launch-time record in place (not overwriting).`
followed by the lines the current config would have written.

**Tests**: `tests/test_run_generalisation_resume_config.py`, 13 tier-1 —
fresh launch writes all three artefacts; an unchanged resume proceeds and
leaves them byte-for-byte identical; a changed config refuses and names the
field; `--allow-config-change` proceeds, logs, and updates the snapshot; an
unparseable snapshot is unknown provenance; an existing intent with a human
note survives; the stage anchor round-trips through `.resume_state.json`; a
legacy state file warns; the diff helper handles nesting and absent fields.

## 4. Fix 4 (audit Finding 4) — a consensus union records its passes

Commit `ac7d393c7`. `scripts/merge_passes.py` (1.1.0 → 1.2.0) and
`scripts/build_all_consensus.py` (1.0.0 → 1.1.0).

The defect: `check_existing_consensus` reported "exists" from a glob, and
`voting_summary.json` held `{"total_passes": N, "thresholds": {…}}` and nothing
else. A pool whose passes had been added to or rewritten in place — E57 and E70
both did exactly that — was reported `skipped — existing consensus: complete`,
and the stale union went on being the candidate universe for crop extraction,
verification, the `candidate_{i:05d}` index join, and every sweep downstream.
The audit's own survey of 151 summaries was inconclusive because `total_passes`
cannot distinguish a declared sub-pool from a stale union; a pass list can.

| What changed | Where |
|---|---|
| `resolve_pass_files()` — the single definition of "which files make up this pool", now shared by the loader and the provenance builder | `scripts/merge_passes.py:408` |
| `build_pass_provenance()` — one entry per file: `pass_id`, repository-relative `path`, `git_blob_hash` | `:478` |
| `load_pass_detections()` refactored onto `resolve_pass_files` (glob order preserved deliberately — within-pass dedup keeps the *first* of a near-duplicate pair, so sorting could have changed outputs) | `:511` |
| `threshold_sweep` writes `pass_provenance`, `pass_ids`, `pass_provenance_schema` into `voting_summary.json`; `merge_passes()` records the same in its stats | `:679`, `:611`, `:80` |
| `compare_pass_provenance()` — verified / stale / unknown | `scripts/build_all_consensus.py:380` |
| `check_existing_consensus(consensus_dir, pool_dir, pass_filter)` — compares before reporting complete; `pool_dir=None` preserves the old presence-only contract | `:457` |
| `process_single_condition` refuses a stale union (new `"stale"` status), the summary prints a Stale count and a `STALE CONSENSUS` block, and `main` exits 1 | `:606-619`, `:934`, `:952`, `:1219` |

### The new refusal, verbatim

```text
stale: 3 threshold files, but 1 pass file(s) rewritten since the union was built
(outputs/<condition>/run_2/detections_test_run02.geojson). Refusing to report
this union as current. Re-run with --force to rebuild it from the pool as it now
stands (which invalidates any crops, probabilities, or sweeps derived from the
old union), or investigate the pool change.
```

The detail clause names which of the three differences occurred — `rewritten
since the union was built`, `recorded pass file(s) no longer present`, or `pass
file(s) in the pool that the union does not record` — listing up to three paths
each. **Refusal, not rebuild**: a union re-materialised under the same path
invalidates every downstream index join, so the operator decides, with
`--force` (whose existing behaviour — clear the stale threshold files, then
rebuild — is unchanged).

A union written before this branch reports:

```text
complete (provenance UNKNOWN): 3 threshold files + voting_summary.json —
voting_summary.json records no pass_provenance (written before provenance
recording was added), so the union cannot be checked against the pool
```

and is skipped exactly as before, with a `WARNING` saying "Treating as existing
but UNVERIFIED (a legacy union is never evidence of a match)". Every committed
union today is of this kind, so no existing tree changes behaviour.

**Tests**: `tests/test_consensus_pass_provenance.py`, 13 tier-1 — the pass list
is written and content-keyed; a `--passes` sub-pool records only its own passes
(the audit's inconclusive survey becomes decisive); provenance is sorted and
order-stable; match, rewritten, added, removed, legacy, and corrupt verdicts;
the `pool_dir`-less call is byte-identical to the old contract; a partial build
is still "partial"; the driver skips a verified union and refuses a stale one.

## 5. Fix 5 (audit Finding 5) — `library_hash` and resumed configurations

Commit `9bbdf490a`. `scripts/lib_llm_metadata.py`.

Two adjacent defects. First, `_compute_library_hash` documented itself as an
example-library fingerprint and hashed the sorted `(path, label, category)`
triples — the images' **filenames**. Replace `example_08.png` with a different
crop and the hash was unchanged, while the sibling `system_instruction_hash` is
a true content hash: two fields making opposite guarantees under the same
naming. The field is a `changed_field` in the no-op rule table that polices
"only the target parameter changed" (`scripts/lib_hypothesis_requirements.py:308-336`
— the H10/H12 failure class), so a name-only hash weakened a live launch guard.

| What changed | Where |
|---|---|
| `_resolve_example_path()` — resolves an example against `inputs/examples`, as the pipeline does | `scripts/lib_llm_metadata.py:335` |
| `_example_library_manifest()` — the `(path, label, category)` triple **plus** the SHA-256 of the image's bytes; an unresolvable example records `"missing"` | `:362` |
| `_compute_library_hash()` — now digests that manifest | `:402` |
| `configuration.library_hash_basis` (`LIBRARY_HASH_BASIS`, `:61`) and `configuration.library_manifest` in the finalised meta | `:657`, `:660` |

Second, `merge_meta` started from `merged = dict(original)` and re-set every
block except `configuration`, so a pass resumed under an edited config recorded
the **first** launch's configuration — including its `system_instruction_hash`
— for a file whose later tiles were produced under different instructions.

| What changed | Where |
|---|---|
| `_configuration_fingerprint()` — comparable scalars (instruction text dropped, already covered by its hash; the full snapshot summarised by its own digest) | `:1316` |
| `compare_configurations()` — names the differing fields | `:1345` |
| `merge_meta` records `configuration_history` (an `original` entry, then one `resume` entry per merge, each with `differs_from_previous` and `changed_fields`) and warns on disagreement | `:1623` |

`merged["configuration"]` **deliberately** remains the original block: cost
aggregation, the post-run report, and manifest re-derivation all read it as the
pass's configuration. The change is that the disagreement is now disclosed
rather than discarded:

```text
merge_meta: the resumed pass's configuration differs from the original launch's
on 2 field(s): system_instruction_hash, temperature. merged['configuration']
remains the ORIGINAL block; the disagreement is recorded in
configuration_history. The merged pass file therefore mixes tiles produced under
two configurations.
```

**Compatibility note for readers of committed metas**: `library_hash` values
recorded before 2026-09-12 are **filename** hashes and are not comparable with
the content hashes written from now on. `library_hash_basis` is what
distinguishes them; the constant's value is
`example-bytes+path-label-category/1`. `scripts/grid_analysis.py:741`'s
hard-coded `library_hash_prefix` reads committed metas and is unaffected.

**Tests**: `tests/test_library_hash_and_config_history.py`, 13 tier-1 — a
replaced image changes the hash (the defect, directly); order-independence and
label sensitivity survive; `no_examples` is unchanged; a missing example is
recorded rather than ignored; repository-relative example paths resolve; the
finalised meta carries manifest and basis; and the history chain covers
agreeing, disagreeing, chained, configuration-less, and snapshot-only merges.

## 6. Fix 6 (audit Finding 6 and row 12) — evaluations and the intent check

Commit `6cbfb0859`.

**(a) `scripts/evaluate_detections.py`.** `input_git_state` recorded a state
*word* per input plus the repository HEAD, never the inputs' own bytes, so
nothing bound an evaluation to the detections file it scored.
`_input_blob_hashes()` (`:540`) adds `input_git_state.blob_hashes` (`:767`),
keyed exactly as `inputs` is, with `None` for an absent input.
`metadata_version` 1.3 → 1.4 (`:727`). `scripts/rerun_bca_corpus.py:110`'s
`DONE_VINTAGE` became `DONE_VINTAGES = ("1.3", "1.4")` so the E82 census still
counts a 1.4 evaluation as bias-corrected-and-accelerated-done.

**(b) `scripts/lib_experiment_intent.py`.** The eight-field intent check
compared `instruction_file` by **filename**: edit the instruction markdown in
place and all eight fields still agreed, so a resume silently mixed tiles
answered under two prompts inside one pass file. `instruction_file_hash()`
(`:109`) resolves the file under `prompts/system-instructions` and digests it;
the derived `instruction_file_sha256` (`INSTRUCTION_HASH_FIELD`, `:65`) is
written into the Verified-values table and compared alongside the name
(`:83`, `:254`). An intent file predating the row simply lacks it and is skipped
by the existing absent-field rule, so no unchanged experiment starts failing.
When the named file cannot be found:

```text
instruction_file <name> not found under <repo>/prompts/system-instructions: its
content hash cannot be recorded, so the intent check falls back to the filename
alone.
```

**(c) `scripts/r2_score_cells.py`.** `Job.done` tested **presence** of an
`evaluation.json`, so a cell whose detections were re-materialised after
scoring resumed as "already done" and kept the earlier file's evaluation. With
the anchor from (a) the check is one dict lookup and one hash of a file already
on disk: `Job.done` (`:120`) now consults `Job.evaluation_provenance()`
(`:146`).

```text
TEST-k3: existing evaluation.json was scored from detections.geojson at blob
4b825dc642cb, but that file is now 2e81c8f1a03d -- will re-score
```

```text
TEST-k3: existing evaluation.json records no content anchor for
detections.geojson (written before input blob hashes were recorded); its
provenance is UNKNOWN, so it is not evidence that the detections on disk are the
ones scored
```

The first is an `ERROR` and reports not-done (the cell is re-scored); the second
is a `WARNING` and still counts as done — the pre-fix behaviour, since every
committed evaluation predates the anchor.

**Tests**: `tests/test_evaluation_content_anchors.py`, 11 tier-1 — the
instruction hash tracks content; an unresolvable file is unknown and says so;
the intent table carries the row; an edited instruction file makes the intent
inconsistent while an unedited one does not; a legacy intent without the row is
not a mismatch; and `Job.done` verifies, rejects a re-materialised file, treats
a legacy evaluation as unknown-but-done, handles no evaluation and a corrupt
one. Two cases were added to `tests/test_evaluate_detections_metadata.py` (the
`blob_hashes` block and the version bump), beside the rest of that module's
metadata tests.

## 7. What did NOT change

- **No committed output, register row, board cell, or evaluation was altered.**
  The branch touches nine scripts (one of them new) and six test modules, plus this report.
  `results/`, `outputs/`, `archive/`, `planning/`, and `paper/` are untouched.
- **No number was recomputed**, no API call was made, and no analysis was run.
- **A run that is not resumed behaves exactly as before.** `_prepare_run`
  writes the same three artefacts; the intent confirmation prompt is unchanged.
- **A resume whose inputs have not changed behaves as before**, only quieter:
  it now leaves `resolved_config.yaml` and `experiment_intent.md` byte-for-byte
  alone instead of rewriting them.
- **Every existing artefact lacking an anchor still resumes / still skips.** A
  `.resume_state.json` without `config_hash`, a `voting_summary.json` without
  `pass_provenance`, an `experiment_intent.md` without the hash row, an
  `evaluation.json` without `blob_hashes`, and a `touch`-ed `.done` marker are
  all treated as **unknown provenance**: a warning, and the prior behaviour —
  never a verified match.
- **The `.done` markers of the completed campaigns were not retrofitted** (the
  audit asked for the pattern, not a migration), and no existing shell driver
  was modified.
- **`merged["configuration"]` in a resumed meta is still the original launch's
  block**, so cost aggregation, the post-run report, and manifest re-derivation
  read exactly what they read before.
- **`load_pass_detections` keeps its glob iteration order**, so no consensus
  union changes by a single cluster.
- **Fix 1 and fix 3 were not touched** (another agent's branch, and already on
  `main`, respectively).
- **Not attempted**: retrospectively establishing whether any committed union
  IS stale. The audit records that this needs re-deriving each union from its
  pool and comparing cluster sets — real compute, and per project policy a
  sapphire job. The anchors added here make the check cheap for every union
  built from now on, but they cannot be back-dated.

## 8. Verification

- `ruff check` clean on every touched file:
  `scripts/lib_content_anchor.py`, `scripts/run_generalisation.py`,
  `scripts/merge_passes.py`, `scripts/build_all_consensus.py`,
  `scripts/lib_llm_metadata.py`, `scripts/evaluate_detections.py`,
  `scripts/lib_experiment_intent.py`, `scripts/r2_score_cells.py`,
  `scripts/rerun_bca_corpus.py`, and the six test modules.
- `python -m pytest -m tier1 -q`:
  **`2311 passed, 1 skipped, 27 deselected, 3 xfailed, 4 warnings in 230.11s`**
  (the skip is pre-existing —
  `tests/test_analyse_phase2.py:550`, "Existing Phase 2a image-only detection
  files not available"). 66 of those tests are new on this branch (15 + 13 + 13 + 13 + 11 in the five
  new modules, plus one added to the evaluation-metadata module).

## Changelog

### 2026-09-12 — Original publication

Implementation report for fixes 2, 4, 5, 6, and 7 of the name-keyed cache audit
(`reports/name-keyed-cache-audit-2026-09-12.md`, published the same day), PI-
approved as a review branch because the work touches the generalisation runner.
Five commits: `41ea08c5e` (fix 7, the shared helper), `dc83a5918` (fix 2),
`ac7d393c7` (fix 4), `9bbdf490a` (fix 5), `6cbfb0859` (fix 6). No numerical
claim in any other document moved, because no committed artefact was
recomputed; the branch adds content anchors and refusals only. Tier-1 suite
green at 2,311 passed.
