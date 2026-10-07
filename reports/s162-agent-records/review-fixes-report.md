# PR #24 review fixes: report (2026-10-06)

Branch `register-repair`, 13 commits on top of `b74bbc464`, NOT pushed.
Every finding was checked against the source before any change; none was
wrong. Two judgement calls (Findings 2 and 3) and one order change
(Finding 4 before Finding 6) are explained below.

## Commits, in order

| Commit | Finding | Subject |
| --- | --- | --- |
| `99a4dc106` | 5 | fix(scripts): keep the D12 note on an unpriced carry |
| `d1f48b235` | 3 | fix(scripts): cap an overlapping verifier leg count |
| `7f6d1b92a` | 7 | fix(scripts): check inert fields on filtered conditions |
| `f265f3473` | (support) | test(check-manipulation): run synthetic gate tests at tier 1 |
| `5caf73ecc` | 2 | fix(scripts): stop declared verifiers passing as sent |
| `9c29fa781` | 4 + 9 | refactor(scripts): move the gate's signature into a lib |
| `f3228a505` | 6 | fix(scripts): read gzipped metas in the gate |
| `9fdcc68c6` | 8 | fix(scripts): name the D42 figures expected_value |
| `8f2894b91` | 10 | fix(scripts): exit 2 when --repo is not a git tree |
| `147641d25` | 12 | refactor(scripts): document the class B annotator |
| `f8c2d9085` | 12 (new defect) | fix(scripts): let the class B annotator re-run |
| `cb67d8abf` | 11 | style(scripts): wrap the PR's lines over 100 chars |
| `ecdfe6928` | 1 | feat(scripts): label documented null manipulations |

## Per finding

### Finding 5: carry note overwrote the D12 note (`99a4dc106`)

- **Change**: `scripts/lib_pass_cost.py`, `PassCoster.cost_pass`: the carry
  note is written only when `basis in ("audited", "audited-upper-bound")`.
  On `unrecorded` the D12 "null, not zero" note now stands; on `unpriceable`
  no whole-spend claim is added.
- **Test**: `tests/test_lib_pass_cost.py::test_a_carry_note_never_replaces_a_null_basis_note`
  (tier 1, parametrised: an unrecorded and an unpriceable carry-forward
  stage). Red before the fix, green after.

### Finding 3: overlapping fragments double-counted (`d1f48b235`)

- **Change**: `scripts/generate_post_run_report.py`, `_verifier_candidates`
  gains `results=`; the call site passes `lib_pass_cost.verifier_coverage`'s
  distinct-candidate count. When an unlisted fragment sits beside another,
  the sum is capped at that count. A union of listed fragments is never
  capped.
- **Why a cap, not a subtraction**: the main leg that predates
  `completed_items` (pv-384 v1-prompt, `run.meta.main-2026-04-10.json`)
  records no candidate ids at all, so the overlap cannot be computed. The
  cap is an upper bound, not an exact count; on a carry-forward stage the
  results also include carried candidates (said in the docstring).
- **Effect on the register**: none today. A fresh extraction of all 247
  committed verifier rows across 32 runs differs from
  `results/passes-manifest.json` in 0 rows (pv-384 stays 572).
- **Tests**: `tests/test_generate_post_run_report.py::test_an_overlapping_cleanup_is_not_counted_twice`
  (overlap capped at 3, non-overlap 4, no bound 4) and
  `::test_the_overlap_cap_reads_the_legs_distinct_candidates` (a
  two-iteration leg's results reduce to candidates), beside
  `test_a_preserved_main_leg_counts_its_own_candidates`.

### Finding 7: inert check ran before `--condition` (`7f6d1b92a`)

- **Change**: `scripts/run_phase2.py`, `run_phase2`: the
  `validate_condition_configs` block moved after the condition filter.
- **Test**: `tests/test_lib_config_validation.py::test_run_phase2_checks_only_the_conditions_that_will_run`
  (dry run of a study with one clean and one inert condition:
  `--condition clean` passes; `--condition inert` and the whole study are
  refused). Red on the `clean` case before the fix.
- **Note**: `validate_model_consistency` still runs over the whole study
  before the filter. That was not in the finding, so it is unchanged; it
  has the same shape and may deserve the same move.

### Support commit: gate tests at tier 1 (`f265f3473`)

`tests/test_check_manipulation.py` was `pytestmark = tier2` for the whole
module, so `-m tier1` would have run none of the new gate tests. The eight
synthetic tests (tmp_path metas, whole module 0.17 s) are now tier 1; the
committed-register test stays tier 2. No assertion changed. Flagging it
because it changes what the per-commit gate runs.

### Finding 2: declared verifier counted as transmitted (`5caf73ecc`)

- **Change**: `scripts/check_manipulation.py`: `arm_from_metas` keeps the
  declared `verifier_config` in the configuration identity only (new field
  `declared_verifier`), not in `signature`. New
  `transmission_relation(a, b)` returns `same` / `differ` / `undetermined`:
  the proposer half is always evidence; the verifier half is evidence only
  when both arms' verifier metas were read. `judge` adds
  `undetermined_pairs`, which make the verdict UNVERIFIABLE (exit 3, or out
  of scope under `--allow-unverifiable`). `render` prints each as
  `UNVERIFIABLE PAIR`, and the note now says the declared configuration
  "is not transmitted evidence, so it separated no pair".
- **Judgement calls** (both written into the docstrings):
  1. Two arms with *equal* declared verifier configurations are judged on
     the proposer half (so the Phase 2c text-track null manipulation is
     still refused beside a declared verifier). Treating those as
     undetermined too would turn real refusals into unverifiable verdicts.
  2. An arm with no verifier stage beside one with a stage, declared or
     transmitted, counts as `differ`: only one sent verifier requests.
     Every proposer-verifier condition in the manifest (389 of 389)
     carries a `verifier_config`, so a missing stage means single-pass.
- **Effect (flag this)**: 21 analyses move from PASS to UNVERIFIABLE (for
  example `55map-canonical-leaderboard-50m`, whose
  `55maps-text-min-n10-uplift::verified-5of10-canonical-gt` arm has no
  located verifier stage). The five refusals are unchanged.
  `verifier-uplift-pairing` now shows 227 unverifiable pairs beside its
  119 declared arms. This is the honest reading, but it shows how much of
  the verifier side the gate cannot currently see; the real fix is
  resolving those stages' metas.
- **Tests** (tier 1): `test_a_declared_verifier_difference_is_not_a_transmitted_one`,
  `test_a_declared_and_a_transmitted_verifier_cannot_be_compared`,
  `test_the_proposer_half_decides_beside_a_declared_verifier` (3 cases),
  `test_the_render_note_says_what_the_declared_configuration_did`. The two
  scenario tests and the render test are red before the fix.

### Finding 4 (+ 9): gate imported a report script (`9c29fa781`)

- **Change**: new `scripts/lib_manipulation_signature.py` holds the
  harvester (`harvest`, `harvest_meta`, `load_meta`, `_dig`, `_stats`) and
  the signature (`signature`, `model_of_record`, `eff_temp`,
  `is_verifier_record`, `dispatched_ids`, `inputs_fingerprint`,
  `SIGNATURE_VERSION`, `SIGNATURE_FIELDS`), copied with attribution to
  `97d2afaf1` (the report scripts) and `61d8e0dca` (the gate).
  `check_manipulation.py` imports and re-exports them; the `importlib` load
  of `reports/manipulation-check-2026-10-05-scripts/harvest.py` and the
  copied block are gone. The report scripts are untouched.
- **Finding 9 folded in**: `harvest()` is split into a read and a parse,
  and the record carries `max_output_tokens` and `dispatched_ids`, so
  `meta_record` parses each meta once. `--all` went from 29 s to 19 s on
  amd-tower. The review said `--all` "takes minutes"; it did not here,
  because `meta_record`'s cache is shared across analyses. One parse
  remains on the pool-directory fallback route (`dcm.read_meta` for
  `is_proposer_meta`).
- **Verification**: `--all` output is the same verdict for verdict and pair
  for pair as before the move.
- **Tests**: new `tests/test_lib_manipulation_signature.py` (tier 1): the
  copy returns every field of the original harvester with the same value
  (skipped once the report is archived); the two new fields; one parse per
  meta (`load_meta` monkeypatched to count); and the gate loads nothing
  from `reports/`.
- **Order change**: Finding 6's fix had to land in the harvester's reader,
  which is only editable once it lives in `scripts/`. So 4 (+9) went before
  6 rather than adding a throwaway shim to the report-loaded module.

### Finding 6: gzipped metas silently dropped (`f3228a505`)

- **Confirmed at source**: the cited
  `outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37/run_3/detections-detect_brief-text-3.7-flash-2026-08-30.meta.json.gz`
  was an "unreadable" entry for all 26 arms of that run, and its pass was
  missing from each signature.
- **Change**: `scripts/derive_condition_modality.py`: the gzip handling of
  `read_meta` (magic bytes) is factored into `load_meta_json`, and
  `read_meta` uses it (and now also treats a truncated stream, `EOFError`,
  as unreadable). `lib_manipulation_signature.load_meta` calls it, and
  since the Finding 4 commit that is the gate's only reader.
- **Effect**: every `--all` verdict is unchanged (the recovered pass has its
  siblings' signature).
- **Tests**: `test_a_gzipped_meta_is_read_like_a_plain_one` (`.meta.json.gz`
  and gzipped in place under `.meta.json`; red before the fix) and
  `test_a_truncated_gzip_meta_is_an_error_record`.
- **Residuals**: the pool-directory glob still matches only `*.meta.json`
  (no effect today: the one gzipped meta in `outputs/` is reached through
  the passes manifest). Two non-meta files remain "unreadable" in every
  sweep: `outputs/verifier-t-pilot/T0.5/run.log` and `T1.0/run.log`, which
  the passes manifest cites as source files (temperature provenance) and
  the gate tries to harvest. That is harmless but noisy, and out of scope.

### Finding 8: `registered_value` held the D42 figure (`9fdcc68c6`)

- **Change**: `scripts/compute_family_fdr.py`: every `FIXED_PRIMARIES`
  entry carries `expected_value` (what the artefact must hold: H4 0.1366,
  H5 0.7262, H7 0.0002) and `registered_value` (what the registration
  quoted: 0.124, 0.756, 0.001; H2 0.0, H3 0.0, H8 0.8344 equal in both).
  `registration_quoted_bootstrap` is gone. The check is factored into
  `fixed_primary_row()`, whose message reads "expected value mismatch ...
  vs expected X (the D42 permutation re-test; the registration quoted Y)"
  or "(the registered figure)".
- **Output unchanged**: rows still carry `registration_quoted_bootstrap_p`
  where the figures differ, so `results/family-fdr/family_fdr.json` stays
  current. A test checks this against the committed file.
- **Tests** (tier 1): `test_registered_value_holds_the_registered_figure`,
  `test_every_reader_returns_its_expected_value` (reads the small committed
  artefacts, 3.5 to 109 KB), `test_a_mismatch_names_the_expected_values_origin` (H4, H8).

### Finding 10: non-git `--repo` crashed (`8f2894b91`)

- **Change**: `scripts/check_generated_currency.py`, `main`: catches
  `CalledProcessError` from `GitClock.prefill()` (and `OSError`: git
  missing, or `--repo` not a directory), prints git's reason, and exits 2.
  The exit-code table in the docstring says so.
- **Test**: `tests/test_check_generated_currency.py::test_a_repo_that_is_not_a_git_work_tree_exits_two`
  (with `GIT_CEILING_DIRECTORIES` pinned so the test is hermetic). Red
  before the fix with the reported traceback.

### Finding 12: class B annotator quality (`147641d25`, `f8c2d9085`)

- **Change**: `scripts/annotate_classb_permutation.py`: docstrings on all
  functions (`load`, `block`, `check`, `fair_384`, `pes`, `p3a`,
  `verifier_thinking`, `main`, and the new `write_like`); `load` typed; the
  `jobs` tuples lose the unused `2`; the duplicated indent-and-write block
  becomes `write_like(path, raw, data)`.
- **Verification without touching committed results**: the dry run could
  NOT be used on the committed tree, because of a defect I found (next
  point). Instead, a scratch tree was built with the seven artefacts as
  they were at `e7b32de0b^` (before annotation) and the re-run inputs. The
  old and new scripts were each run with `--write` there: identical logs,
  and every write byte-identical to the committed file. The same check was
  repeated after the Finding 11 wrap.
- **New defect, fixed in `f8c2d9085`**: `fair_384()` iterated every
  top-level key, and the first `--write` added a top-level
  `d42_annotation` string. Every later run, the default dry run included,
  died with `KeyError: 'd42_annotation'`. Non-comparison entries are now
  skipped. On the committed tree the dry run completes with the original
  log. A `--write` captured in memory (`Path.write_text` patched; nothing
  written) reproduces all seven committed artefacts byte for byte, so a
  re-run is a no-op.
- **Tests**: new `tests/test_annotate_classb_permutation.py` (tier 1):
  `write_like` layout (3 cases), annotation-only diff, and the re-run case
  (red before `f8c2d9085`).

### Finding 11: line length (`cb67d8abf`)

- **Change**: wrapped the 10 added lines over 100 characters in
  `git diff main...HEAD -- scripts/ tests/`: the six named in
  `annotate_classb_permutation.py`, `build_archive_ledger.py` (134),
  `build_tile_presence_board.py` (120), and two the review did not name
  (`tests/test_generate_post_run_report.py`, `tests/test_lib_pass_cost.py`).
  Layout only: each file's AST is identical before and after, so the README
  strings the two builders write into generated outputs are unchanged.
  After the commit the diff has 0 added lines over 100.
- **Which config wins today**: the repo-root `ruff.toml`. ruff 0.15.6
  reports `Settings path: ".../ruff.toml"`, which ignores E501 and E402 and
  selects only E, F and W. It shadows `pyproject.toml`'s `[tool.ruff]`
  entirely, so that file's I (isort) and UP (pyupgrade) rules are not
  applied either, although `docs/agent-guidance.md` names `pyproject.toml`
  as the config. `ruff.toml` and `pyproject.toml` are untouched; the
  reconciliation is the PI's call.
- **Left as is**: 10 E501 hits remain in touched files, all on `main`
  before the PR (checked line by line): `generate_post_run_report.py`
  (7), `lib_pass_cost.py:102`, and `tests/test_lib_pass_cost.py:177-178`.

### Finding 1: registered analysis pairs two replicate pools (`ecdfe6928`)

- **The finding, plainly**: `verifier-uplift-pairing`, a registered
  analysis, compares `h10::verified-pool-160` with
  `h8-v2::verified-wbf-scale-8`. Their transmitted signatures are
  identical: same proposer library (`images:d1c1e46e9da7/17`), same
  instruction hash `e169b7237b85`, T 0.7, HIGH, the same 327 tiles, and the
  same verifier signature (both legs' verifier inputs are `unrecorded`, so the
  candidate sets themselves are not compared). They are two executions of one configuration
  (`reports/manipulation-check-2026-10-05.md` § B.5 group 10; the 2026-04-15
  same-day replicate). The same family also produces 6 more refusing pairs
  in `uplift-supplement-flatten` (h10 greedy vs h8-v2 greedy/wbf; h12-v2
  `*-r2-balanced` vs h8-v2 `*-scale-8`, since h12-v2's R2 reuses the
  pool_160_hp4hn4 run per `results/h12-v2/analysis_summary.md` lines 73-74
  and 148). The register was not changed.
- **Change**: `scripts/check_manipulation.py`: `KNOWN_NULL_MANIPULATIONS`
  lists the three documented groups as `(run_id, proposer_pool)` sets with
  their documents (§ B.5 group 16, the text track; group 15, the 2b/2c
  image twin; group 10 plus the h12-v2 summary). `check_conditions` labels
  every null pair `documented_by` (or None); `render` appends
  `[KNOWN: ...]` or `[NEW: documented nowhere]`; `--all` ends with a
  summary naming each refusal KNOWN or NEW. A single analysis still exits
  2 on a known pair, since it still compares replicates; `--all` exits 2
  only for a NEW pair.
- **Result today**: `--all`: 71 analyses, 30 PASS, 5 REFUSE (all KNOWN:
  era1-leaderboard 16, era1-single-pass-baseline-matrix 16,
  null-exemplar-sensitivity-2026-09-13 16, uplift-supplement-flatten 23,
  verifier-uplift-pairing 1), 36 UNVERIFIABLE; exit 3.
  `--all --allow-unverifiable` exits 0. `verifier-uplift-pairing` alone
  exits 2.
- **Tests**: tier 1: `test_every_known_null_manipulation_cites_documents_that_exist`,
  `test_a_null_pair_is_known_only_inside_one_documented_group`,
  `test_all_fails_only_on_an_undocumented_refusal` (known only 0, a new
  refusal 2, known beside unverifiable 3, the same with
  `--allow-unverifiable` 0). Tier 2: `test_the_h8_h10_replicate_pair_is_a_known_refusal`
  (the registered pair refuses with exit 2 and is labelled group 10). All
  seven new tests are red without the change.
- **Design note**: "exit 0 when every refusal is documented" needs
  `--allow-unverifiable` today, because UNVERIFIABLE keeps its own exit 3
  (36 analyses, 21 of them from Finding 2). I did not fold unverifiable
  into the known-refusal rule.

## Lint and tests

- `ruff check` on all 19 touched files: All checks passed!
- `ruff check --select E501` on the same files: Found 10 errors, all
  pre-existing on `main` (listed under Finding 11); 0 on lines this PR adds.
- Tier 1 on the touched test modules (plus `test_run_phase2.py` and
  `test_derive_condition_modality.py`):
  `499 passed, 14 deselected in 81.95s (0:01:21)`.
- `pytest --collect-only -m "not tier1 and not tier2"` on the touched
  modules: `no tests collected (426 deselected)`.
- Gate tier 2 (`tests/test_check_manipulation.py -m tier2`): `2 passed, 20 deselected`.
- **Full tier-1 suite** (`.venv/bin/python -m pytest -m tier1 -q -p no:cacheprovider`):
  `3819 passed, 5 skipped, 51 deselected, 3 xfailed, 4 warnings in 317.46s (0:05:17)`,
  exit 0 (the warnings are rasterio `NotGeoreferencedWarning`s).

All runs were on amd-tower (the main agent's instruction for the suite).
The `--all` sweeps (about 20 to 30 s each) also ran locally, because the
branch is unpushed and sapphire's checkout could not see it.
