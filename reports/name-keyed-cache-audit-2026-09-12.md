# Name-keyed cache and derived-artefact audit

> **Last revised**: 2026-09-12 (original publication). See [§ Changelog](#changelog) for revision history.
>
> **Audited**: 2026-09-12 against HEAD `2fabf4e1d`, branch `worktree-agent-a98527f84011ee57d`
> (clean tree). Read-only: no repository file was modified, no Application
> Programming Interface (API) call was made, and no analysis heavier than a few
> seconds of local JavaScript Object Notation (JSON) counting was run. Every
> `path:line` below was opened in this session.

## 1. The defect class and the two known instances

The class is a cache, registry, index, or derived artefact **keyed by a name** —
a label, a condition identifier, a file path, a run identifier, a stage name —
rather than by the **content** it was built from. While nothing re-materialises
under that name the artefact is correct; the moment the content changes under
the same name the derived value goes on serving, silently, with no error, no
schema violation, and no warning. The only available signal is a
cross-artefact one: a count, a hash, or a vintage comparison that nothing in
the pipeline performs routinely. Two instances of the class surfaced in
Session 152, both inside the same archived board, and both invisible to that
board's own gates.

**Instance 1 — the board builder's evaluation cache** (Obs 464,
`docs/notes/working-notes.md:33329`). `build_tiered_leaderboard._cache_path_eval`
(`scripts/build_tiered_leaderboard.py:647-649`) keys an evaluation on
`(slugify(label), threshold, buffer_m)` and nothing else, so the archived Era-2
proposer–verifier (PV) board's cache entry for `pv-high-image-t0.3-n5`
(`n_detections` 372, F1@20 0.746, written 2026-04-25) kept serving after the
cell's detection file was re-materialised to 373 features on 2026-05-06 —
seventy seconds after the board's own build timestamp. Gate G1 read the
resulting disagreement as instrument drift in a retired builder; it was a stale
cache, and the cache's own `n_detections` (372) against the input file's feature
count (373) would have caught it in one line.

**Instance 2 — operating points taken from the wrong frame's registry**
(Obs 466, `docs/notes/working-notes.md:33812`). The archived PV materialisation
registry recorded, by label, "the best point" for each free-sweep cell; for nine
cells the file that had been materialised under that label was the argmax on the
**327-tile Era-3 frame**, not the 487-tile Era-2 frame the board scored it on.
The registry was current and the file was current; what was missing was any key
binding the file to the sweep frame its argmax came from. The lesson generalises:
a materialised "best" cell must carry the frame its argmax was taken on.

Already-guarded relatives, listed here as KNOWN so they are not re-reported
below as discoveries: the **probabilities-grew** class (a stage's `sweep_2d.json`
older than its own `probabilities.json` — Obs 461,
`docs/notes/working-notes.md:32946`) and the **union-rebuilt** class (a union
re-materialised under the same path, so the index join `candidate_{i:05d}` to
`probabilities.json` mis-pairs), both diagnosed by
`scripts/check_pv_sweep_vintage.py` (classes named in its docstring, lines
27-35, using the sweep's own universe size as the decisive diagnostic); the
generated-file registry's `--check` drift test
(`scripts/build_generated_file_registry.py:25-32`, `:309`); and the projection
drift test on the hypothesis outcome table
(`scripts/generate_hypothesis_outcome_table.py:277-296`, which regenerates in
memory and exits non-zero if the committed file differs).

## 2. Method

Searched, in this order:

1. **Every disk cache in `scripts/`.** `grep -rn '\.cache' scripts/*.py` returns
   exactly four families: the leaderboard `.cache/` writer
   (`scripts/build_tiered_leaderboard.py:2171`), its reconstruction tool
   (`scripts/rebuild_leaderboard_cache_from_committed.py:133`, `:197`), one live
   reader (`scripts/build_gs_era2_board_opmax.py:171-173`), and the Gemini
   context cache (`scripts/4_detect_mounds_batch.py:977`, `:1321` — an API-side
   cache created from uploaded content, not a name key).
2. **In-memory memoisation.** `lru_cache`, `pickle`, `joblib`, `shelve`,
   `diskcache` across `scripts/` (four files); plus every hand-rolled `cache: dict`
   (`scripts/run_pairwise_tests.py:242`, `scripts/scoring_sensitivity_survey.py:160`,
   `scripts/dedup_metric_impact.py:718`, `scripts/analyse_verifier_robustness.py:208`,
   `scripts/extract_candidates.py:305`, `scripts/5_verify_crops.py:146`).
3. **Reuse and resume logic.** `--resume`, `--skip-existing`, `.done` markers,
   `recovery_manifest`, `checkpoint`, and the "skip if present" pattern
   (`exists()` / `is_file()` guarding a `return` / `continue`; 421 occurrences
   across `scripts/*.py`, triaged by whether the artefact they gate feeds the
   register, a board, or the paper).
4. **Registries, manifests, and indices on disk.** `results/*.json` aggregates,
   `results/ci-metadata-registry.md`, the four generated manifests, the
   archived `pv_registry.json` pair, `outputs/**/voting_summary.json` (151),
   `outputs/**/*.tiles.json`, `outputs/**/.done` (shell drivers only), and
   `archive/superseded-leaderboards/leaderboard/**/.cache/**` (37,675 JSON files).

**LIVE / DORMANT / GUARDED.** A site is **GUARDED** when a content-level check
exists and is wired into something that runs: a feature-count cross-check, a
content comparison, a `--check` drift test, or a gate. It is **LIVE** when a
current pipeline reads it and that pipeline feeds the register
(`results/run-conditions.json`), the signed GS Era-2 board, or the paper — or,
for the API pipelines, when it is the pipeline that would execute the one
remaining registered run (the image-based generalisation run). It is **DORMANT**
only where a `grep` for readers found none; where a grep found no reader the row
says so in those words rather than asserting dormancy.

## 3. Candidate table

Key: **N** = name (label / path / id / stage name), **C** = content hash,
**P** = presence of an output file, **∅** = no key.

| # | Site or artefact | Derives / caches | Key | Built from | Guard (where) | Risk |
|---|---|---|---|---|---|---|
| 1 | `scripts/build_tiered_leaderboard.py:647-649` | evaluation at a buffer | N (label, threshold, buffer) | a detections GeoJSON | none | DORMANT (retired builder; readers are the archived boards and `scripts/g1_drift_bisect_rescore.py`) — **the Obs 464 instance** |
| 2 | `archive/superseded-leaderboards/leaderboard/**/.cache/evaluations/<label>/t*_*m.json` (37,675 files incl. pairwise) | evaluations, pairwise permutation tests | N | detections GeoJSONs at the 2026-04/05 vintage | none | **LIVE at one site**: `scripts/build_gs_era2_board_opmax.py:171-173` reads `n_detections` from this cache for **all 44** archived cells (every cell's `evaluations["20"].n_detections` is absent) → **Finding 2** |
| 3 | `results/all-bootstrap-cis.json` (496 entries) | bootstrap F1/P/R means and confidence intervals (CIs) | N (`"single:phase2a/brief-text/run_2"`; `source_file` is a path) | per-pass detection GeoJSONs | none wired; the entry's own `n_detections` makes a check possible | **LIVE-by-policy, unguarded → Finding 1 (85 stale entries)** |
| 4 | `results/pv/all-bootstrap-cis.json` (496 entries) | same values, same keys | N | same | none | same — **Finding 1** (identical 85) |
| 5 | `scripts/build_condition_inventory.py:492-503` | ingests f1 mean + CI from #3 into `planning/condition-inventory*.json` | N (the same key strings) | #3 | none | DORMANT chain (inventory last written `03bf71c8f`, 2026-04-25; its consumers read counts and labels — `scripts/lib_c4_runners.py:18` counts rows, not F1) |
| 6 | `scripts/run_generalisation.py:2177-2185` `.resume_state.json` | "stage already done" for proposer / consensus / extract / verify / evaluate | N (stage name) + ∅ | the resolved run config | none — and `resolved_config.yaml` is **overwritten** at `:2015` before the resume decision at `:1877-1895` | **LIVE unguarded → Finding 3** (this is the pipeline for the pending generalisation run) |
| 7 | `scripts/build_all_consensus.py:439-446` + `check_existing_consensus:329-356` | skip rebuilding a consensus union | P (glob of `consensus_t*.geojson` + `voting_summary.json`) | the pool's pass GeoJSONs | none: presence only, no count or vintage comparison | **LIVE unguarded → Finding 4** |
| 8 | `scripts/merge_passes.py:554`, `:568-570` `voting_summary.json` | the union's own provenance record | ∅ | the pass GeoJSONs it read | records `total_passes` and per-threshold counts; **no pass list, no paths, no hashes** | **LIVE unguarded → Finding 4** (this is why #7 cannot be checked cheaply today) |
| 9 | `scripts/lib_llm_metadata.py:313-343` `_compute_library_hash` | `library_hash`, the example-library fingerprint | N (sorted `(path, label, category)` triples) | the example **images** | none | **LIVE unguarded → Finding 5**: a field that looks like a content hash is a name hash; `scripts/lib_hypothesis_requirements.py:328` uses `library_hash` in the no-op rule table that enforces "only the target parameter changed" |
| 10 | `scripts/lib_llm_metadata.py:1214-1227` `merge_meta` | merged `*.meta.json` on a resume | N (file path) | two passes' metadata | merges timestamps, `execution_stats`, usage, `per_item_metadata`, `recovery_history`; **`configuration` is taken from the ORIGINAL** (`merged = dict(original)`, never re-set) | **LIVE unguarded → Finding 5**: a resumed pass records the first launch's `system_instruction_hash` |
| 11 | `scripts/4_detect_mounds_batch.py:1052-1066` | tile-level resume from the existing output GeoJSON | N (output path) + N (tile filename) | prior API responses under the prior config | partial: `scripts/lib_experiment_intent.py:59-69` compares **8 config fields** against an existing `experiment_intent.md` and warns interactively (`:505-515`); `instruction_file` is compared **by filename**, never by the text's hash | LIVE, partially guarded → **Finding 6** |
| 12 | `scripts/r2_score_cells.py:106-108` `Job.done` | skip a cell that has an `evaluation.json` | P | a detections GeoJSON | partial: `--require-clean-inputs` on by default and `check_output:162-175` verifies ground truth + `input_git_state` — but only for cells it actually runs | LIVE, partially guarded (see § 5 fix 6) |
| 13 | `scripts/evaluate_detections.py:710-726` `_metadata` | the per-evaluation provenance record | N (paths) | detections / ground truth / bounds | records `input_git_state` (`clean` / `modified` / … plus HEAD) and `n_detections` (`:1024`) — **a state word and a HEAD hash, never the input's blob hash** | LIVE, partially guarded (the recorded `n_detections` is what makes #14 possible) |
| 14 | `scripts/verify_run_conditions.py:9-14`, `:271-295` | register-wide eval ↔ detections, scope, and **feature-count** cross-check | content (count) | every register row | the project's general guard for this class; WARN severity; tier-1 test `tests/test_verify_run_conditions.py` | **GUARDED** |
| 15 | `scripts/build_gs_era2_board.py:244-270` gate G2 | committed-vs-reproduced F1 **and** `n_detections` equality (`:260`) | content | every board member | the live board's own content guard | **GUARDED** |
| 16 | `scripts/check_pv_sweep_vintage.py` | `probabilities-grew` / `union-rebuilt` classification | content (universe sizes) | registry cells | the Obs 461 guard | **GUARDED** (KNOWN) |
| 17 | `scripts/build_gs_era2_board_opmax.py:260-271` | per-row `vintage` verdict recorded into `opmax/membership.json` | content (`n_union`, `n_probabilities`, `n_sweep`) | union + probabilities + sweep | added 2026-09-11 | **GUARDED** |
| 18 | `scripts/generate_post_run_report.py:1654`, `:1886-1928` | carries `last_extracted_at` / `generated_at` forward | rows matched by **id**, then compared by **content** (`_strip_ts(row) == _strip_ts(old_row)`, `:1920`) | the manifests on disk | the comparison itself | **GUARDED** — "unchanged" is decided by content, not by name (see § 6) |
| 19 | `scripts/build_generated_file_registry.py:25-32`, `:299`, `:309` | generated-vs-hand-written registry | N (path patterns) | the markdown tree + `generator-map.json` | `--check` rebuilds and diffs, ignoring `generated_at`; tier-1 test | **GUARDED** (KNOWN) |
| 20 | `scripts/generate_hypothesis_outcome_table.py:277-296` | H1–H15 outcome projection | N | the register | `--check` regenerates and compares; tier-1 test | **GUARDED** (KNOWN) |
| 21 | `scripts/analyse_verifier_robustness.py:208-213` | per-accepted-set scores | **C** (`frozenset` of accepted candidate ids) | candidate sets | key *is* the content | **GUARDED** by construction |
| 22 | `scripts/run_pairwise_tests.py:242-275`, `scripts/scoring_sensitivity_survey.py:174-199`, `scripts/dedup_metric_impact.py:733-737`, `scripts/extract_candidates.py:305-331`, `scripts/5_verify_crops.py:146-170`, `scripts/build_example_pool.py:142-144` | in-process memos | N (path / config strings) | files read once per invocation | process-scoped; keys cover every loader argument | not the class (see § 6) |
| 23 | `scripts/build_tiered_leaderboard.py:1111-1147` pairwise cache paths | permutation tests | N (`<a>_vs_<b>`, metric, buffer folded into the directory) | two conditions' detections | none | DORMANT (retired builder; the buffer/metric namespacing fixed a *different* collision bug) |
| 24 | `scripts/rebuild_leaderboard_cache_from_committed.py:115-207` | writes #2's layout back from a committed board | N (label) | the committed board JSON | none — it **propagates** whatever the board recorded | DORMANT (no reader found by grep for `rebuild_leaderboard_cache_from_committed` outside its own file and `planning/`) |
| 25 | `scripts/enrich_per_arch_markdown.py:244-248` | `n_detections` fallback for the per-architecture boards | N (label) | #2 | none | DORMANT (its `--root results/leaderboard/per-architecture` no longer exists; the tree is under `archive/superseded-leaderboards/`) |
| 26 | `outputs/**/.done` markers | pass-level idempotence in the shell drivers (`scripts/gemini37-overnight.sh:79`, `:91`; `gemini37-image-gs-driver.sh:35`, `:47`; `gemini37-55map-driver.sh`) | P | a completed pass | none | DORMANT (those campaigns are complete; the pattern recurs in any new driver — § 5 fix 7) |
| 27 | `results/ci-metadata-registry.md:97-98`, `:329-331` | designates #3/#4 as paper-citable CI sources and names their provenance chain | N (path) | #3/#4 | none; the chain it names (`data/retest/**`) **no longer exists** | LIVE-by-policy → **Finding 1** |

## 4. Findings

### Finding 1 (the third instance, demonstrated): 85 of 456 resolvable entries in `results/all-bootstrap-cis.json` were computed from a pass file that has since grown under the same name

`results/all-bootstrap-cis.json` holds 496 bootstrap CI entries keyed by a
condition path-string. Each entry records `source_file` (a path) and
`n_detections`, but nothing binds it to the file's content. Two observations,
both made this session:

1. **Every one of the 496 `source_file` values names a path that does not
   exist**: they are all under `data/retest/**`, and there is no `data/`
   directory in the repository. Remapping the prefix to `outputs/retest/**`
   resolves 456 of them (the other 40 name `data/consensus-proposers/*.geojson`,
   also absent). The remap is an inference, but a well-supported one: 371 of the
   456 then match their recorded `n_detections` **exactly**.
2. **85 of the 456 do not match.** In every case the file at the remapped path
   holds *more* features than the entry recorded — from +1 to +119.

The mechanism is established, not merely plausible. For each of the 85, the
pass's `.tiles.json` sidecar was read: **84 of 85 record `patched` > 0**, against
**339 of the 371 matching entries recording no patch at all**. Patched tiles are
the March 2026 out-of-band tile-recovery campaign disclosed as **E70**
(`docs/methodology/preregistration/protocol-errata.md:3154-3158`: "campaign
~2026-03-17 onwards", 127 passes / 350 tiles, `patch_failed_tiles()` writing
recovered detections into the existing pass GeoJSON). The aggregate was
committed 2026-03-26 (`a371376c1`); the patch timestamps in the sidecars read
2026-03-22. The CIs are therefore values computed on the pre-patch file, still
serving under the post-patch file's name.

The three largest, with both values:

| entry | recorded `n_detections` | recorded F1 mean [CI] | features today | `.tiles.json` `patched` |
|---|---:|---|---:|---:|
| `single:phase3c/track2-text/h9-E-p2/run_5` | 1114 | 0.453595 [0.394606, 0.508639] | **1233** (+119) | — (no patch recorded) |
| `single:phase3c/track2-text/h9-B-v4/run_2` | 1340 | 0.402443 [0.342079, 0.462453] | **1421** (+81) | 10 (2026-03-22T03:48:39Z) |
| `single:phase3c/track2-text/h9-E-p2/run_3` | 1226 | 0.437480 [0.379349, 0.492835] | **1259** (+33) | 3 (2026-03-22T04:22:22Z) |

Anchors: `results/all-bootstrap-cis.json` (read 2026-09-12: 496 entries, each
with `f1`/`precision`/`recall` mean and CI, `n_iterations` 1000, `n_detections`,
`source_file`; `_metadata.n_bootstrap` 1000, `random_seed` 42);
`outputs/retest/phase3c/track2-text/h9-E-p2/run_5/detections_h9-E-p2_run05.geojson`
and its two siblings above (feature counts recounted 2026-09-12);
`results/pv/all-bootstrap-cis.json` (read 2026-09-12 — **the same 496 keys and
the same 85 stale entries**, so the defect is duplicated);
`docs/methodology/preregistration/protocol-errata.md:3154-3199` (E70);
`git log --follow results/all-bootstrap-cis.json` → `a371376c1` 2026-03-26,
sole commit of that path.

**Reach.** No current code recomputes from these files: the only reader found is
`scripts/build_condition_inventory.py:492-503`, which copies the f1 mean and CI
into `planning/condition-inventory*.json`, last written 2026-04-25
(`03bf71c8f`); the C4 recompute runner reads that inventory to **count** matching
rows, not to read F1 (`scripts/lib_c4_runners.py:18-26`). No reader was found by
grep for `all-bootstrap-cis` in `paper/`. What makes this LIVE rather than
DORMANT is policy, not code: `results/ci-metadata-registry.md:97-98` lists both
files as `YES`-complete, paper-citable CI sources ("the paper can cite each
reported CI with a full bootstrap specification"), and `:329-331` records their
provenance chain as `data/retest/**` — a path that no longer exists. Any Era-1
single-pass CI quoted from these files today is at 19 % risk (85/456) of being a
pre-recovery number, and the registry gives a reader no way to tell.

This is the same failure as Obs 464 one layer down the stack: a derived value
keyed by a label, whose own recorded `n_detections` disagrees with its named
input's feature count — the `feedback_feature_count_crosscheck` signal, never
checked.

### Finding 2 (demonstrated, in a signed-board artefact): a `"match"` verdict in `opmax/membership.json` comes from the stale label-keyed cache of Obs 464

`archived_cells()` in `scripts/build_gs_era2_board_opmax.py:161-176` reads each
archived cell's `n_detections` from the archived board JSON and, when it is
absent, falls back to
`archive/…/per-architecture/era2/pv/.cache/evaluations/<label>/t1_20m.json`
(`:171-173`). It is absent for **all 44** cells (verified 2026-09-12 by walking
`leaderboard_tiers_20m.json`), so every `archived_n` on the `-opmax` rows comes
from the label-keyed cache — the artefact Obs 464 showed can be a file the input
no longer is. `archived_n` is not decorative: `:228-235` compares it with the
registry's count to set `registry_vs_archived`, and `:246-247` switches the row's
`detections` to a re-materialised file only when that verdict starts with
`"differs"`.

For `pv-high-image-t0.3-n5` the committed board artefact reads:

```text
registry_n 372 · archived_n 372 · registry_vs_archived "match"
detections archive/…/era2/pv-materialised/pv-high-image-t0.3-n5.geojson
```

(`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/membership.json`,
read 2026-09-12). **The file it names holds 373 features today** (recounted
2026-09-12). Had the count been taken from the file rather than the cache, the
verdict would have read `"differs"`. The cache's 372 and the registry's 372
agree only because both predate the 2026-05-06 re-materialisation, so the stale
value *suppresses* the disagreement it should have raised. The F1 consequence is
already disclosed — the same cell is the hard-coded `BISECTED` exception at
`scripts/build_gs_era2_board_opmax.py:143-147` — but the membership row's
verdict is the un-remediated residue, and the fallback read at `:171-173`
remains a live dependency of a signed board on a cache with no content key.

Cross-check run over all 44 archived cells (2026-09-12): cache `n_detections`
equals the materialised file's feature count for 43, and `pv-high-image-t0.3-n5`
is the single exception (372 vs 373) — i.e. the archived cache contains exactly
the one known-stale entry, and the survey found no second one.

### Finding 3 (LIVE, unguarded, no stale instance on disk): the generalisation pipeline's resume is keyed by stage name, and the snapshot that would detect a config change is overwritten first

`scripts/run_generalisation.py` records completion as
`{stage: {completed_at, summary}}` in `.resume_state.json`
(`_save_resume_state:2177-2185`), and `cmd_all:1877-1895` skips any stage whose
**name** is present: `if "proposer" not in resumed`, `if "consensus" not in
resumed`, and so on. Nothing about the config that produced that stage is
recorded in the state file or compared on resume. Worse, the artefact that could
have detected the change is destroyed first: `_prepare_run` rewrites
`resolved_config.yaml` from the *current* config (`:2000-2018`) and rewrites
`launch_manifest.json` and `experiment_intent.md` (`:2042-2054`) before
`cmd_all` consults the resume state. The generalisation script's own
`write_experiment_intent:1771` simply overwrites (unlike
`scripts/lib_experiment_intent.py:356-400`, which compares against an existing
intent file), and `confirm_intent:1827-1843` prints the **new** intent and asks
for a yes — it never shows what changed.

**Failure scenario.** Edit the verifier config (or the proposer's temperature,
or the evaluation's `prob_threshold`), re-invoke with `--resume` into the same
`output_dir`, answer yes: stages already marked done keep their old-config
outputs, `resolved_config.yaml` and `experiment_intent.md` now describe the new
config, and the run's `evaluation.json` is a mixture whose recorded intent is
uniformly the new config. The paper-facing number is the generalisation run's
headline F1 — and this is the pipeline for the one remaining registered API run
(`project_generalisation_run_prerequisites`). No stale instance exists on disk
today: the existing `.resume_state.json` files belong to completed runs.

### Finding 4 (LIVE, unguarded, not demonstrable with today's artefacts): a consensus union carries no record of the passes it was built from, and the builder skips on presence alone

`check_existing_consensus` (`scripts/build_all_consensus.py:329-356`) returns
"exists" from a glob — `consensus_t*.geojson` present, `voting_summary.json`
present — and `:439-446` then skips the condition unless `--force`. Nothing
compares the union against the pool it came from. That check is impossible to
make cheaply today because `scripts/merge_passes.py:554`, `:568-570` writes
`voting_summary.json` as `{"total_passes": N, "thresholds": {...}}` and nothing
else: no pass paths, no pass count per file, no hashes (confirmed by reading
`outputs/h12-v2/greedy/r3-hp-heavy/voting_summary.json`, 2026-09-12 — eight
lines, exactly those two keys).

**Failure scenario.** A recovery or top-up adds or rewrites a pass under the
pool (E57 and E70 both did exactly this), `build_all_consensus.py` is re-run to
refresh the tree, every affected condition is reported `skipped — existing
consensus: complete`, and the stale union goes on being the candidate universe
for crop extraction, verification, the index join `candidate_{i:05d}`, and every
sweep downstream. This is the upstream cause of the already-guarded
`union-rebuilt` class: `scripts/check_pv_sweep_vintage.py` can *detect* the
symptom for archived registry cells, but nothing prevents it, and nothing
detects it for a union that no registry row names.

**Attempted demonstration (negative).** I surveyed all 151
`outputs/**/voting_summary.json` and compared `total_passes` with the number of
`run_*` directories in the parent pool. 37 disagree — and all 37 are legitimate
subpool unions whose names declare the subset (`consensus-n5` under a 30-pass
pool, `consensus-n10` under 30, and so on). So the survey is not decisive, which
is precisely the finding: with `total_passes` as the only provenance field, a
legitimate subpool and a stale union are indistinguishable from the artefact.
A decisive check needs the pass list, which is what fix 4 adds. Establishing it
retrospectively would require re-deriving each union from its pool and comparing
cluster sets — real compute, **needs sapphire**.

### Finding 5 (LIVE, unguarded): `library_hash` is a name hash wearing a content hash's name, and a resumed pass records the first launch's configuration

Two adjacent defects in the run-metadata layer:

- `_compute_library_hash` (`scripts/lib_llm_metadata.py:313-343`) documents
  itself as "a unique fingerprint for each library variant" that
  "distinguishes conditions that share the same system instruction but use
  different example sets", and computes SHA-256 over the sorted
  `(path, label, category)` triples from the config — **the example images'
  filenames, never their bytes**. Replace `example_08.png` in a pool with a
  different crop and `library_hash` is unchanged. That field is not inert: it
  is a `changed_field` in the no-op rule table
  (`scripts/lib_hypothesis_requirements.py:308-336`) that the launch check uses
  to police "only the target parameter changed" — the H10/H12 failure class
  (`feedback_experimental_parameter_control`). By contrast
  `system_instruction_hash` (`:292-294`) *is* a true content hash, of the
  instruction text — so the two sibling fields make opposite guarantees under
  the same naming.
- `merge_meta` (`scripts/lib_llm_metadata.py:1214-1227`, called on every resume
  via `merge_meta_into_existing:1447-1492`) starts from `merged =
  dict(original)` and then explicitly re-sets `timestamp`, `execution_stats`,
  `usage_stats`, `cost_estimate`, `per_item_metadata`, and `recovery_history`
  — never `configuration`. A pass resumed under an edited config therefore
  records the **original** launch's `configuration` block, including its
  `system_instruction_hash`, for a file whose later tiles were produced under
  different instructions. The double-count guard at `:1474-1490` warns about
  overlapping `completed_items`; nothing warns about disagreeing configurations.

### Finding 6 (LIVE, partially guarded): the detection resume trusts `instruction_file` by filename

`scripts/4_detect_mounds_batch.py:1052-1066` resumes from the output GeoJSON at
a path derived from the run's version and label, skipping any tile named in
`processed_tiles`. The guard is `scripts/lib_experiment_intent.py:59-69`, which
compares eight fields of the existing `experiment_intent.md` against the current
config (`version`, `hypothesis`, `include_example_images`, `temperature`,
`thinking_level`, `instruction_file`, `model`, `base_config`) and, on
disagreement, prints a warning and asks for confirmation (`:505-515`) — waivable
with `--skip-intent-check`. `instruction_file` is compared as a **filename**.
Edit the instruction markdown in place and every one of the eight fields still
agrees, so a resume silently mixes tiles answered under two different prompts
inside one pass file. The content hash that would settle it is computed on the
same run (`system_instruction_hash`) and written into the meta — but per
Finding 5 the resume keeps the original meta's copy, so even the artefact cannot
be used to detect the mix after the fact.

## 5. Proposed fixes, ranked by risk

None implemented. Each prefers a pattern the repository already uses; the
content-addressed helper to reach for is `git_blob_hash`
(`scripts/materialise_opmax_cells.py:125-141`, "``git hash-object`` is
content-addressed, so this anchors a provenance record to the exact bytes read").

1. **Finding 1** — add a tier-1-tested `--check` mode (the
   `generate_hypothesis_outcome_table.py:277-296` pattern) that re-counts every
   `all-bootstrap-cis.json` entry's `source_file` against its recorded
   `n_detections`, fix the 496 dead `data/retest/**` paths to
   `outputs/retest/**`, and annotate the 85 divergent entries in
   `results/ci-metadata-registry.md` as PRE-E70 (or re-run them on sapphire —
   496 × 1,000 draws, hours not minutes) before any of them is cited.
2. **Finding 3** — record a hash of the resolved config in `.resume_state.json`
   beside each stage and refuse `--resume` when it differs (or print the diff
   and require an explicit `--allow-config-change`), and stop overwriting
   `resolved_config.yaml` / `experiment_intent.md` on a resume — compare them,
   as `lib_experiment_intent.write_experiment_intent` already does.
3. **Finding 2** — stop reading `n_detections` from the archived label-keyed
   cache: count the features of the file the row names
   (`build_gs_era2_board_opmax.py:171-173`), which is one `len(...)` on a file
   the function already resolves, and re-derive `registry_vs_archived` from it.
4. **Finding 4** — have `merge_passes.py` write the pass list (relative paths +
   `git_blob_hash` each) into `voting_summary.json`, and have
   `check_existing_consensus` compare that list against the pool before
   reporting "exists"; mismatch → rebuild, or refuse and name the difference.
5. **Finding 5** — hash the example images' bytes in `_compute_library_hash`
   (keeping the path/label triple alongside for legibility), and have
   `merge_meta` compare the two metas' `configuration` blocks, recording a
   `configuration_history` list rather than silently keeping the original.
6. **Findings 6 and 12** — add the input's `git_blob_hash` to
   `evaluate_detections.py`'s `input_git_state` (`:710-726`) so a state word and
   a HEAD hash become a content anchor, and extend the eight-field intent check
   to compare the instruction file's **hash**, not its name. With the blob hash
   recorded, `r2_score_cells.Job.done` can cheaply verify that the existing
   `evaluation.json` was scored from the detections file that is there now.
7. **Row 26 (pattern, not an instance)** — new shell drivers should write the
   config's hash into the `.done` marker rather than `touch`ing an empty file,
   so idempotence is keyed on what was run and not only on that something was.

## 6. What did NOT turn out to be this class

- **In-process memos** (`run_pairwise_tests.build_cache_key:242-273`,
  `scoring_sensitivity_survey:174-199`, `dedup_metric_impact:733-737`,
  `extract_candidates:305-331`, `5_verify_crops:146-170`,
  `build_example_pool:142-144`). All are dicts living inside one invocation, and
  each key covers every argument its loader uses — `run_pairwise_tests`'s PV key
  is `(probabilities, manifest, threshold)` and its consensus key is
  `(study_dir, config)`, which together with the run-wide `gdf_bounds` fully
  determine the loaded frame. Nothing can be re-materialised between the write
  and the read.
- **`generate_post_run_report._stabilise_timestamps`** (`:1886-1928`). The brief
  asked whether "unchanged" is decided by content or by name: it is decided by
  **content**. Rows are *located* by id (`_ROW_ID_FIELD:1657-1661`) but then
  compared field for field with timestamps blanked (`_strip_ts`, `:1663-1670`),
  and `_carry_timestamps:1672-1688` recurses only where the two structures are
  identical. `source_files` is part of the compared row, so a provenance change
  re-stamps. Not this class.
- **`drift_check`** in the same module. It is a run-**set** consistency check
  (registry ↔ facts ↔ decomposition membership by `run_id`, per
  `tests/test_generate_post_run_report.py:469-487`), not a currency check on
  content. It is a guard, but for a different failure.
- **`analyse_verifier_robustness`'s dedup cache** (`:208-213`), keyed on a
  `frozenset` of accepted candidate ids — the key *is* the content.
- **The Gemini context cache** (`4_detect_mounds_batch.py:966-1001`,
  `:1318-1323`). `cache_name` is a server-side handle for content uploaded in
  the same invocation and deleted at the end; no name outlives its content.
- **The 37 `voting_summary.json` files whose `total_passes` differs from the
  pool's `run_*` count.** All 37 are declared subpool unions (`consensus-n5`
  under 30 passes, etc.), not stale unions. Recorded here so the negative is on
  the record — see Finding 4.
- **The archived `.cache/` trees as a whole** (37,675 JSON files). They are the
  Obs 464 class by construction, but 37,674 of those files have no current
  reader; the single live dependency is Finding 2's fallback read. The archived
  boards' own `n_detections` values agree with their materialised files for 43
  of 44 cells, so the archive contains one stale entry, not a field of them.
- **`results/leaderboard/`** has **no** `.cache` directory (`find results/leaderboard
  -name .cache -type d` → empty, 2026-09-12): the live GS Era-2 board
  re-scores per cell into `cells/<slug>/` and gates on F1 **and**
  `n_detections` (`build_gs_era2_board.py:260`). The class was designed out of
  the current board, not merely guarded.

## Changelog

### 2026-09-12 — Original publication

Commissioned after Session 152 found two instances of the name-keyed
derived-artefact class inside one archived board (Obs 464, Obs 466) and the
Principal Investigator asked whether a third exists. Read-only audit of
`scripts/` (368 Python files), `results/`, `outputs/`, and
`archive/superseded-leaderboards/`; 27 candidate sites or artefact families
tabulated (§ 3); six findings (§ 4), of which two are demonstrated stale values
in committed artefacts — 85 stale bootstrap CI entries duplicated across
`results/all-bootstrap-cis.json` and `results/pv/all-bootstrap-cis.json`
(Finding 1), and a `"match"` verdict in the signed board's
`opmax/membership.json` derived from the Obs 464 cache (Finding 2). No file was
modified and no fix was implemented.
