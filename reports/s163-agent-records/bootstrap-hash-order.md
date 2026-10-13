# D63: resampling order no longer follows the hash seed

> **Last revised**: 2026-10-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), an overnight subagent of the main Session 163
  session (workstream `bootstrap-hash-order`), in the reused scratch clone
  `~/scratch/d61-regenerations-2026-10-12/repo` on sapphire, on 2026-10-13
  from about 05:00 UTC.
- **Repository**: `map-reader-llm`, branch `bootstrap-hash-order` from
  `main` at `67a3f2795`, with `main` merged in after PR #33 (§ 4). Fix
  commits: `4cef29150` (library), `0ce4a296b` (SD-shrinkage seeds),
  `b9d3e4d97` (their test), `2c4228390` (a docstring); merge `c4fd95b25`.
- **Ruling**: `planning/pi-decisions-2026-09-20.md` D63.
- **Guarantees**: no model Application Programming Interface (API) call;
  no committed output was regenerated or edited. Every "after" number comes
  from a replay in a disposable `git archive` copy under `/tmp/d63-runs/`
  on sapphire, and every replay ran twice with byte-identical outputs
  (§ 6).
- **Scripts and records**: `reports/s163-agent-records/bootstrap-hash-order-scripts/`
  (harness, replay drivers, summariser, and the JSON records under `out/`).

**Conventions.** "main" is `main` re-run today on today's inputs under
`PYTHONHASHSEED` 0, 1, 2, and 3 (`67a3f2795` for the retest, interaction,
and SD replays; `8ec0fa5e7`, after PR #33, for the fair-384 and
proposer–verifier (PV) replays); "fixed" is this branch, which gives one
output under every hash seed; "committed" is the file on `main`. A "flip"
is an interval that starts or stops excluding zero. BCa is the
bias-corrected and accelerated bootstrap interval; BH is the
Benjamini–Hochberg correction; RNG is random number generator; SD is
standard deviation.

## 1. Headline

1. **No verdict the project currently uses crosses.** The fix moves no p
   value (the D42 permutation tests already sorted their tiles), so no p
   crosses 0.05 and no BH decision changes. No thinking × temperature
   interaction flag and no SD-shrinkage slope flag changes. This holds
   for every output replayed (16 committed files, 316 intervals; § 5).
2. **Interval readings do cross, and the hash seed alone was enough to
   cross them.** In the nine retest phase evaluations
   (`results/retest/phase2*-evaluation.json`: 61 pairs, 183 intervals), 14
   intervals change their excludes-zero reading with the hash seed alone
   on today's code, and 5 flip between the committed (March) file and the
   fixed code. Three of the five are F1 intervals, so the retired
   `significant` field (D42: "bootstrap CI excludes zero, uncorrected")
   would read differently: two true → false, one false → true. All 15
   rows have permutation p between 0.04 and 0.25; none of their D42
   verdicts changes. Outside the retest files one more interval
   (fair-384 I1 recall) flips with the seed alone; it includes zero both
   as committed and as fixed.
3. **Size.** On today's code the hash order alone moves an interval bound
   by up to 0.0144 (in the image interaction file) and by up to 0.0134 in
   the retest files. Committed → fixed shifts reach 0.0662 (the text
   interaction), most of it from code and input changes since the
   committed runs (the D50 scorer; in the image file the HIGH T 0.0
   condition's optimal consensus threshold moved from 1 to 3), not D63.
4. **It explains the fair-384 and pairwise-384px March digits, and the
   retest row the 2026-10-05 check examined; it explains none of the S3
   record's stopped lines** (§ 5.5).
5. **Five sites varied; all five are fixed.** Three in
   `scripts/lib_advanced_metrics.py` (the found case and two siblings) and
   two RNG seeds taken from the built-in `hash()` in the SD-shrinkage
   scripts. No varying site is in a file another agent owns today. Four
   sites change only key or row order (no number) and are listed, not
   fixed (§ 2.4), for the PI.
6. **This defect had been seen twice before.** It was flagged on
   2026-09-12 (`reports/tile-mcc-geometric-join-2026-09-12.md` § 5.1 (c),
   deferred to that report's § 6 decision) and on 2026-10-05
   (`reports/retest-bootstrap-check-2026-10-05.md`, "What it does", Tile
   order; commit `06c71b39e`), when the D42 class-B regenerations were
   pinned to `PYTHONHASHSEED=0` as a workaround. Neither note reached a
   ruling until D63.

## 2. Sweep: every site, whether it varies, what it feeds

### 2.1 Method

1. **Static review** of every Python file under `scripts/`, `reports/`,
   and `results/` outside `archive/` (595 files at `67a3f2795`). The 127
   files that call a seeded RNG or one of the project's resampling helpers
   were split into four groups of about 20,000 lines and read by four
   read-only reviewers (Opus subagents), which traced every array handed
   to a resampler back to where its order was set. A fifth reviewer
   triaged the other 468 files with an abstract-syntax-tree (AST) scan for
   set expressions that are iterated, listed, or popped, and for `hash(`
   calls, and read every hit in context.
2. **Function-level harness** (`hash_seed_harness.py`): twelve resampling
   and permutation functions (the seven `lib_advanced_metrics` bootstraps,
   `lib_permutation.paired_permutation_test`,
   `e45_bootstrap_pairings.paired_bootstrap`,
   `n1_baseline_leaderboard_tiering.permutation_test_float`,
   `pairwise_permutation_test.run_permutation_test`, and
   `selection_aware_intervals.run`) on fixed synthetic inputs, each in a
   fresh interpreter under `PYTHONHASHSEED` 0–3. On `main`, three vary
   (four distinct outputs each) and nine are stable; on the fix all twelve
   are stable.
3. **Script-level replays** (`script_replay.py` and the replay drivers):
   whole analyses run from a `git archive` copy under the same hash seeds,
   outputs digested with timestamps and run paths removed (§ 6).

The synthetic tile names must follow the tiling pipeline's
`<sheet>_x<N>_y<N>.png` form. A first harness run used `…_tile_000.png`
names; the scorer scoped every detection out as unattributed, every
interval was [0, 0], and every case read "stable". The tier-1 test
therefore carries a guard that fails if its intervals have no width.

### 2.2 Sites that vary (all fixed)

Line numbers are at `67a3f2795`. After PR #33 merged (`7a8a081e1`) the
three library sites sit at `scripts/lib_advanced_metrics.py:3801`, `:4311`,
and `:5327`; this branch merges `main` and carries the fix onto them (§ 4).

| # | Set built (consumer) | Function | Kind | Evidence that it varies | Fix |
|---|---|---|---|---|---|
| 1 | `scripts/lib_advanced_metrics.py:2649` `list(tiles_a & tiles_b)` (`:2674` `rng.choice`) | `bootstrap_effect_size_ci` | set order indexed by a seeded RNG | harness: 4 distinct outputs under hash seeds 0–3; script replays: every retest, fair-384, and PV pairwise output differs by seed | `sorted(...)` |
| 2 | `:3149` `list(set.intersection(*tile_sets))` (`:3184`) | `bootstrap_interaction_ci` | same | harness: 4 distinct; replay: both interaction outputs differ by seed | `sorted(...)` |
| 3 | `:4150` `list(tiles_a & tiles_b)` (`:4211`) | `bootstrap_tile_effect_size_ci` | same | harness: 4 distinct | `sorted(...)` |
| 4 | `scripts/analyse_consensus_sd_shrinkage.py:284` `hash((track, thinking, temperature, k_used))` (`:285` `default_rng`) | `compute_sd_per_cell_per_k` | seed from salted `hash()` | replay: `sd_shrinkage.json` 4 distinct digests under seeds 0–3; tier-1 test fails on `main` | `zlib.crc32` of a fixed-format key |
| 5 | `scripts/analyse_consensus_sd_shrinkage_v2.py:470` `abs(hash(stratum["label"]))` (`:480` → `generate_subsamples` → `random.Random`) | `_process_stratum` | seed from salted `hash()` | tier-1 test (input/output stubbed) fails on `main`; not replayed on real inputs (§ 5.1) | `zlib.crc32` of the label |

The permutation p values beside sites 1 and 2 never varied:
`_permutation_on_tile_metrics` (`:2789`) and
`bootstrap_multi_run_effect_size_ci` already sorted their tiles (D42,
`06c71b39e`).

### 2.3 What the varying sites feed

| Site | Caller (`file:line`) | Committed outputs | Registered or signed? | Generated-file registry |
|---|---|---|---|---|
| 1 | `scripts/evaluate_retest_all.py:234` | `results/retest/phase2{a,b-track1,b-track2,c-exploratory,c-track1,c-track2,d-track1,d-track2,e}-evaluation.json` (March 2026 values, D42-annotated `5f02cfbc2`) | no; cited by `results/commitments.json` (e.g. `phase2a`, `phase2e`) | not registered (JSON) |
| 1 | `scripts/compare-384-vs-512.py:304`; inline March script (B-16) | `results/h11-384-pv-diagnostic/pairwise/fair-384-vs-512.json`, `pairwise-384px.json` (March values, D42-annotated `e7b32de0b`) | no | not registered |
| 1 | `scripts/evaluate_pv_results.py:552` (`--pairwise`) | `results/h11-384-pv-diagnostic/pairwise/pro-proposer-verifier-thinking-{text,image}/comparison.json` | no | not registered |
| 1 | `scripts/compute-pairwise-effect-sizes.py:563` | `results/pv/pairwise-effects/pairwise-effect-sizes{,-v2}.json` | no; cited by `results/commitments.json` | not registered |
| 1 | `scripts/consensus-sweep-phase3a-high-text.py:272` | `results/retest/phase3a-high-text/phase3a-high-text-pairwise.json` | no | not registered |
| 1 | D42 class-B regenerations (`reports/d42-implementation-2026-10-05-scripts/run_classb.sh`, `PYTHONHASHSEED=0`) | `results/d42-retest-2026-10-05/class-b/*.json` (8 files) | no | not registered |
| 1, 3 | `scripts/analyse_study_effects.py:222`, `:233` | none committed (no committed JSON carries `mcc_difference`) | – | – |
| 2 | `scripts/analyse_secondary_effects.py:581`, `scripts/analyse_secondary_effects_text.py:583` | `results/secondary-effects/secondary_effects.json`, `results/phase3a-text-matrix/secondary_effects.json` | no | `secondary_effects_autogen.md` in both directories (rules `gen-autogen-secondary-image`, `gen-autogen-secondary-text`) |
| 4 | the script itself | `results/secondary-effects-consensus-sd/sd_shrinkage.json`, `sd_shrinkage.png`, `report.md` | no | `report.md` (rule `gen-report-consensus-sd`) |
| 5 | the script itself | `results/secondary-effects-consensus-sd/sd_shrinkage_v2.json`, `sd_shrinkage_v2.png`, `report.md` § 3 | no | as site 4 |

None of these outputs is the artefact of a row in
`results/analyses-manifest.json` (71 rows checked), so no signature lapses.
A path search of `docs/paper/` finds none of them cited.

### 2.4 Sites that vary only in key or row order (not fixed; for the PI)

D63 covers set order that feeds resampling, permutation, "or any other
numeric output". These four change no number, only the order of keys or
rows in a written file, so a rerun is not byte-identical. They are left
for a ruling; each fix is one `sorted()`.

| Site | Effect | Committed evidence |
|---|---|---|
| `results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20/replicate_k5_arm1.py:720` and `…/replicate-k5-arm2-batch-2026-09-20/replicate_k5_arm2.py:377` (`for label in {…}`) | key order of `n_detections` and `tile_confusion` in each `tests.json` | the two committed `tests.json` files list their labels in different, unsorted orders |
| `scripts/build_tier_stability.py:255–270` (`sorted(<set>, key=…)` with tied keys) | row order of tied conditions (every undefined score) in `tier_stability{,_mcc}.md` | only archived copies are committed |
| `scripts/lib_batch_api.py:3256` → `:2730` | order of `execution_stats.completed_items` in each Batch API pass's `.meta.json` | readers checked are order-free |
| `scripts/extract_candidates.py:311` → `:408` | order of `missing_sources` in `candidate_manifest.json` | no reader uses the order |

One more prints only: `scripts/verify_phase2a_metrics.py:758` averages a
list built from a set (`np.mean` in set order, last-bit at most) and writes
no file.

### 2.5 Order that is not hash-dependent (outside D63; noted)

- **Filesystem order.** `scripts/lib_advanced_metrics.py:903`
  (`load_data`) concatenates `reference_*.geojson` in `glob` order, unsorted;
  `scripts/select_tiles_phase2.py:519` feeds an unsorted `glob` to a seeded
  `random.shuffle`; `scripts/stride_plateau_analyses.py:243` sums floats
  over an unsorted `glob` (an owned file; last-bit only).
- **Worker completion order.** `scripts/build_tiered_leaderboard.py:847–851`
  with `:970–975` keeps the first of two exactly tied thresholds in the
  order workers finish, so `best_threshold` can change between runs
  (metrics cannot); key order in `compute-pairwise-effect-sizes.py` and
  `analyse_consensus_sd_shrinkage_v2.py:1138–1142` follows completion order.
- **A log line.** `analyse_secondary_effects*.py` logs
  `result.get("any_significant")`, a key `bootstrap_interaction_ci` never
  returns, so the log always says "not significant" (all three image
  interactions are detected).

### 2.6 Files other agents own

No varying site is in `grid_analysis.py`, `stride_plateau_analyses.py`,
`grid_verifier_analysis.py`, `stride_verifier_analysis.py`, the Image-B
scripts (`image_b_analysis.py`, `image_b_pair.py`), `prepare_h13_scoring.py`,
`h13_*`, `lib_consensus.py`, `analyse_diversity.py`, or the W2.7 floors
scripts. Their per-tile arrays follow the bounds file or a sorted list; the
floors scripts already derive seeds with `zlib.crc32`; `floors2_lib.py:112`
builds its map list from a set but sums only integer per-map counts.
Nothing in them was edited.

## 3. Tests

`tests/test_hash_seed_determinism.py` (tier-1, about 6 s) computes each
fixed function in two fresh interpreters under `PYTHONHASHSEED` 1 and 2
and requires identical JSON:

- the three library functions on a fixed two-sheet, 60-tile synthetic
  problem (condition B on a reversed subset of the tiles);
- `compute_sd_per_cell_per_k` (SD v1) on fixed per-pass F1 values;
- `_process_stratum` (SD v2) with its file, deduplication, and consensus
  steps stubbed, eight passes and at most five subsamples per K′, so the
  seeded draws are exercised.

A sixth test guards against a vacuous pass: the synthetic intervals must
have width and the v2 stub must leave a non-exhaustive K′.

**Red sentinel.** In a `git archive` copy of `main` (`67a3f2795`) with the
new test file added, five of the six tests fail (the guard passes); on the
branch all six pass. After the merge with PR #33 the same holds: in a
copy of `main` at `8ec0fa5e7` five of six fail, and on the merged branch
all six pass.

## 4. PR #33 and the merge

PR #33 (`d50-review-fixes`) merged into `main` as `7a8a081e1` while this
work ran. It rewrote the scoring calls of the same three functions
(`parent_bounds=_parent_of_cut(...)` a few lines below each
`common_tiles`, and new `Raises:` sections just above). The branch merges
`origin/main` (`c4fd95b25`) with no conflict; the sorted lines now sit
at `scripts/lib_advanced_metrics.py:3804`, `:4317`, and `:5336`. A scan of
the lines PR #33 added found no new set iterated into a numeric output (its
sheet resolver sorts by `(-len, name)`). On the merged code the harness
again finds the same three varying functions on `main` (`8ec0fa5e7`) and
none on the branch, each pair of runs agreeing; and the merged branch's
replays (hash seed 1, two runs) give byte-identical outputs to the
pre-merge branch's for all 16 replayed files (`out/merged-check.json`), so
every number in § 5 holds after the merge.

## 5. Impact (report only; nothing regenerated)

### 5.1 What was replayed

All five varying sites feed committed outputs; none of those outputs is
registered or signed, so every one counts as "the rest", and the replay
covers 16 of them (the retest phase files, both interaction files, the SD
v1 file, the fair-384 and pairwise-384px files, and the two B-17/B-18 PV
comparisons). Not replayed: the two PV pairwise-effect-size files, the
Phase 3a HIGH-text pairwise file, the D42 class-B records other than those
compared below, and SD v2 (its 13 strata rebuild consensus from the raw
passes for up to 200 subsamples per K′, well beyond this budget; its seed
defect is covered by the tier-1 test).

### 5.2 Per-output summary

| Output (committed file) | Intervals | Hash-seed spread on `main` (largest bound range, seeds 0–3) | Largest bound shift committed → fixed | Excludes-zero reading varies with the seed | Flips committed → fixed |
|---|---|---|---|---|---|
| `results/retest/phase2a-evaluation.json` | 30 | 0.0121 | 0.0106 | 4 | 2 |
| `results/retest/phase2b-track1-evaluation.json` | 30 | 0.0087 | 0.0087 | 3 | 1 |
| `results/retest/phase2b-track2-evaluation.json` | 30 | 0.0134 | 0.0070 | 3 | 0 |
| `results/retest/phase2c-exploratory-evaluation.json` | 9 | 0.0087 | 0.0051 | 0 | 0 |
| `results/retest/phase2c-track1-evaluation.json` | 30 | 0.0074 | 0.0168 | 1 | 1 |
| `results/retest/phase2c-track2-evaluation.json` | 30 | 0.0056 | 0.0099 | 1 | 0 |
| `results/retest/phase2d-track1-evaluation.json` | 3 | 0.0055 | 0.0048 | 0 | 0 |
| `results/retest/phase2d-track2-evaluation.json` | 3 | 0.0067 | 0.0016 | 0 | 0 |
| `results/retest/phase2e-evaluation.json` | 18 | 0.0113 | 0.0088 | 2 | 1 |
| `results/secondary-effects/secondary_effects.json` | 9 | 0.0144 | 0.0370 | 0 | 0 |
| `results/phase3a-text-matrix/secondary_effects.json` | 9 | 0.0073 | 0.0662 | 0 | 0 |
| `results/secondary-effects-consensus-sd/sd_shrinkage.json` | 67 | 0.0010 | 0.0010 | 0 | 0 |
| `results/h11-384-pv-diagnostic/pairwise/fair-384-vs-512.json` | 18 | 0.0102 | 0.0075 | 1 | 0 |
| `results/h11-384-pv-diagnostic/pairwise/pairwise-384px.json` | 24 | 0.0096 | 0.0106 | 0 | 0 |
| `results/h11-384-pv-diagnostic/pairwise/pro-proposer-verifier-thinking-text/comparison.json` | 3 | 0.0031 | 0.0011 | 0 | 0 |
| `results/h11-384-pv-diagnostic/pairwise/pro-proposer-verifier-thinking-image/comparison.json` | 3 | 0.0023 | 0.0015 | 0 | 0 |

### 5.3 The 15 retest intervals whose reading moves

The permutation p and the pair's D42 F1 verdict (BH within the phase) are
the same in the committed annotation, on `main` under every seed, and on
the fix.

| Phase: pair | Metric | Committed (March) | `main`, seeds 0–3 (lower; upper) | Fixed | Excludes zero: committed → fixed | Permutation p (unchanged) | Pair's D42 F1 verdict, BH (unchanged) |
|---|---|---|---|---|---|---|---|
| phase2a: brief-text-image vs image-only | recall | [-0.0010, +0.1029] | -0.0080 to +0.0015; +0.0950 to +0.1071 | [-0.0007, +0.1023] | no → no | 0.0653 | True |
| phase2a: brief-text-image vs verbose-text | recall | [-0.0923, +0.0016] | -0.0947 to -0.0925; -0.0033 to +0.0028 | [-0.0958, +0.0034] | no → no | 0.0481 | False |
| phase2a: image-only vs verbose-text | f1 | [-0.1008, -0.0034] | -0.1059 to -0.0958; -0.0027 to +0.0016 | [-0.1021, +0.0072] | yes → no | 0.0573 | False |
| phase2a: image-only vs verbose-text-image | recall | [-0.1005, -0.0011] | -0.1057 to -0.1008; -0.0089 to +0.0002 | [-0.1020, +0.0008] | yes → no | 0.0555 | True |
| phase2b-track1-image: T0.3 vs T0.7 | f1 | [-0.0012, +0.0759] | -0.0017 to +0.0029; +0.0711 to +0.0747 | [-0.0023, +0.0750] | no → no | 0.0661 | False |
| phase2b-track1-image: T0.7 vs T1.3 | f1 | [+0.0021, +0.0691] | -0.0037 to +0.0008; +0.0664 to +0.0733 | [-0.0007, +0.0682] | yes → no | 0.0588 | False |
| phase2b-track1-image: T0.7 vs T1.3 | precision | [+0.0046, +0.0695] | -0.0007 to +0.0037; +0.0670 to +0.0724 | [+0.0030, +0.0709] | yes → yes | 0.0421 | False |
| phase2b-track2-text: T0.3 vs T1.3 | recall | [+0.0021, +0.0730] | -0.0017 to +0.0039; +0.0714 to +0.0779 | [+0.0002, +0.0764] | yes → yes | 0.0535 | True |
| phase2b-track2-text: T0.7 vs T1.3 | f1 | [+0.0015, +0.0754] | -0.0051 to +0.0013; +0.0710 to +0.0758 | [+0.0017, +0.0779] | yes → yes | 0.0535 | False |
| phase2b-track2-text: T0.7 vs T1.3 | recall | [+0.0035, +0.0761] | -0.0005 to +0.0045; +0.0738 to +0.0790 | [+0.0025, +0.0769] | yes → yes | 0.0406 | False |
| phase2c-track1-image: canonical vs scale-8 | recall | [-0.0847, -0.0026] | -0.0755 to -0.0687; +0.0015 to +0.0054 | [-0.0724, +0.0049] | yes → no | 0.083 | False |
| phase2c-track1-image: pure-positive-canon vs scale-8 | recall | [-0.0788, -0.0064] | -0.0821 to -0.0760; -0.0040 to +0.0032 | [-0.0794, -0.0020] | yes → yes | 0.043 | False |
| phase2c-track2-text: plus-hp vs scale-4 | recall | [-0.0393, +0.0000] | -0.0481 to -0.0462; -0.0017 to +0.0000 | [-0.0444, +0.0000] | no → no | 0.2485 | False |
| phase2e: canonical-first vs random | precision | [-0.0016, +0.0736] | -0.0010 to +0.0005; +0.0700 to +0.0757 | [-0.0001, +0.0717] | no → no | 0.057 | False |
| phase2e: config-default vs random | f1 | [-0.0021, +0.0718] | -0.0008 to +0.0014; +0.0692 to +0.0777 | [+0.0029, +0.0740] | no → yes | 0.0563 | False |

### 5.4 Interactions, SD slopes, fair-384, and PV

| Track | Metric | Committed | `main`, seeds 0–3 (lower; upper) | Fixed | Interaction detected: committed → fixed |
|---|---|---|---|---|---|
| image | f1 | [+0.1786, +0.2841] | +0.1482 to +0.1535; +0.2605 to +0.2678 | [+0.1496, +0.2629] | True → True |
| image | precision | [+0.1928, +0.3128] | +0.1676 to +0.1705; +0.2877 to +0.2901 | [+0.1678, +0.2892] | True → True |
| image | recall | [+0.1119, +0.2497] | +0.0844 to +0.0945; +0.2201 to +0.2345 | [+0.0936, +0.2270] | True → True |
| text | f1 | [+0.0386, +0.1533] | +0.0373 to +0.0445; +0.1364 to +0.1415 | [+0.0389, +0.1398] | True → True |
| text | precision | [+0.1131, +0.2365] | +0.1234 to +0.1273; +0.2333 to +0.2402 | [+0.1220, +0.2407] | True → True |
| text | recall | [-0.0396, +0.0844] | -0.0678 to -0.0615; +0.0206 to +0.0229 | [-0.0646, +0.0207] | False → False |

The SD v1 slope intervals come from a separate generator that never
depended on the hash seed (they are identical committed, on `main`, and
fixed); the slope points do. No stratum's "slower than independent and
identically distributed (i.i.d.)" flag (β₁ > −0.3) changes:

| Stratum | β₁ committed | β₁ on `main`, seeds 0–3 | β₁ fixed | β₁ interval (all) | Slower than i.i.d. (all) |
|---|---|---|---|---|---|
| image HIGH T0.3 | -0.5172 | -0.5256 to -0.5188 | -0.5324 | [-0.5792, -0.4757] | false |
| image HIGH T0.7 | -0.5298 | -0.5243 to -0.5043 | -0.5211 | [-0.5793, -0.4732] | false |
| image HIGH T1.0 | -0.5180 | -0.5283 to -0.5155 | -0.5243 | [-0.5817, -0.4723] | false |
| image MINIMAL T0.3 | -0.5201 | -0.5339 to -0.5022 | -0.5120 | [-0.5857, -0.4747] | false |
| image MINIMAL T0.7 | -0.5344 | -0.5319 to -0.5171 | -0.5307 | [-0.5871, -0.4720] | false |
| image MINIMAL T1.0 | -0.5054 | -0.5386 to -0.5116 | -0.5209 | [-0.5806, -0.4738] | false |
| image SCALE4 T0.7 | -0.5331 | -0.5231 to -0.5144 | -0.5264 | [-0.5856, -0.4730] | false |
| text HIGH T0.3 | -0.5271 | -0.5299 to -0.5130 | -0.5135 | [-0.5766, -0.4747] | false |
| text HIGH T0.7 | -0.5036 | -0.5110 to -0.4932 | -0.5046 | [-0.5451, -0.4710] | false |
| text HIGH T1.0 | -0.5186 | -0.5397 to -0.5191 | -0.5189 | [-0.5792, -0.4732] | false |
| text MINIMAL T0.3 | -0.5233 | -0.5334 to -0.5129 | -0.5239 | [-0.5782, -0.4768] | false |
| text MINIMAL T0.7 | -0.5068 | -0.5111 to -0.4970 | -0.5194 | [-0.5484, -0.4692] | false |
| text MINIMAL T1.0 | -0.5254 | -0.5324 to -0.5152 | -0.5171 | [-0.5787, -0.4790] | false |

F1 only below (precision and recall in `out/impact-rows.json`). The
pairwise-384px rows I:I1 and I:I2 are refused by today's scorer (a
tile-join shortfall: they compare raw 512 px detections whose `source_tile`
names are not the 384 px frame's), on `main` and on the fix alike.

| File: comparison | Committed (March) | D42 class-B record (hash seed 0) | `main`, seeds 0–3 (lower; upper) | Fixed | March library, seeds 0–7 (lower; upper) |
|---|---|---|---|---|---|
| fair-384-vs-512: I1:loose_consensus | [+0.0175, +0.1201] | [+0.0288, +0.1263] | +0.0186 to +0.0288; +0.1195 to +0.1263 | [+0.0231, +0.1230] | +0.0189 to +0.0260; +0.1188 to +0.1256 |
| fair-384-vs-512: I2:goldilocks | [+0.0209, +0.1044] | [+0.0257, +0.1078] | +0.0218 to +0.0259; +0.0992 to +0.1078 | [+0.0245, +0.1031] | +0.0216 to +0.0253; +0.0993 to +0.1070 |
| fair-384-vs-512: I3:best_vs_best | [+0.0234, +0.1055] | [+0.0263, +0.1089] | +0.0253 to +0.0281; +0.1033 to +0.1089 | [+0.0266, +0.1026] | +0.0246 to +0.0272; +0.1014 to +0.1073 |
| fair-384-vs-512: I5:image_moderate | [+0.0768, +0.1781] | [+0.0778, +0.1783] | +0.0763 to +0.0801; +0.1733 to +0.1783 | [+0.0773, +0.1788] | +0.0768 to +0.0794; +0.1744 to +0.1781 |
| fair-384-vs-512: I6:image_baseline | [+0.0180, +0.1266] | [+0.0201, +0.1223] | +0.0177 to +0.0201; +0.1223 to +0.1271 | [+0.0172, +0.1234] | +0.0176 to +0.0204; +0.1226 to +0.1277 |
| fair-384-vs-512: I4:deterministic | [+0.0197, +0.1116] | [+0.0185, +0.1115] | +0.0185 to +0.0245; +0.1114 to +0.1149 | [+0.0186, +0.1134] | +0.0188 to +0.0235; +0.1112 to +0.1165 |
| pairwise-384px: J:J1 | [+0.0725, +0.1481] | – | +0.0708 to +0.0737; +0.1455 to +0.1491 | [+0.0759, +0.1513] | +0.0701 to +0.0750; +0.1463 to +0.1507 |
| pairwise-384px: J:J2 | [+0.0783, +0.1527] | – | +0.0757 to +0.0807; +0.1513 to +0.1590 | [+0.0735, +0.1531] | +0.0777 to +0.0801; +0.1538 to +0.1589 |
| pairwise-384px: J:J3 | [+0.0625, +0.1334] | – | +0.0540 to +0.0608; +0.1345 to +0.1384 | [+0.0564, +0.1361] | +0.0556 to +0.0611; +0.1350 to +0.1398 |
| pairwise-384px: J:J4 | [+0.0414, +0.1323] | – | +0.0417 to +0.0460; +0.1268 to +0.1340 | [+0.0461, +0.1297] | +0.0388 to +0.0461; +0.1281 to +0.1326 |
| pairwise-384px: K:K1 | [-0.1103, -0.0650] | – | -0.1117 to -0.1082; -0.0651 to -0.0631 | [-0.1093, -0.0647] | -0.1114 to -0.1084; -0.0649 to -0.0615 |
| pairwise-384px: K:K2 | [+0.0394, +0.0936] | – | +0.0393 to +0.0408; +0.0935 to +0.0952 | [+0.0399, +0.0916] | +0.0390 to +0.0424; +0.0921 to +0.0951 |
| pairwise-384px: K:K3 | [-0.0972, -0.0391] | – | -0.0960 to -0.0949; -0.0413 to -0.0401 | [-0.0984, -0.0431] | -0.0962 to -0.0947; -0.0412 to -0.0385 |
| pairwise-384px: K:K4 | [-0.0136, +0.0502] | – | -0.0145 to -0.0119; +0.0466 to +0.0500 | [-0.0130, +0.0510] | -0.0143 to -0.0107; +0.0475 to +0.0508 |
| text-asis: pro-text-flash-verifier vs pro-text-pro-verifier | [-0.0288, -0.0070] | [-0.0301, -0.0073] | -0.0306 to -0.0284; -0.0076 to -0.0072 | [-0.0299, -0.0062] | – |
| image-asis: pro-image-flash-verifier vs pro-image-pro-verifier | [-0.0213, +0.0032] | [-0.0207, +0.0038] | -0.0207 to -0.0198; +0.0032 to +0.0046 | [-0.0205, +0.0042] | – |

### 5.5 Does this explain the known unreproducible intervals?

- **`fair-384-vs-512.json` and `pairwise-384px.json` (March).** Yes, as
  far as a replay can show. The March code (`1ca43283e`, percentile intervals) replayed
  on today's inputs (the same detection counts as March) under eight hash
  seeds puts the committed March values inside its own hash-order spread:
  over the 144 committed bounds and means, median |z| is 0.88,
  16 exceed |z| = 2 and 3 exceed 3 (largest 4.33), where an independent
  ninth draw would put about 14.6 and 3.7 of 144 (Student's t, 7 degrees of
  freedom, scaled by √(9/8)). No exact match was expected: unpinned, the
  hash key is drawn from the operating system's random source, not from a
  small seed that could be searched. The further difference
  between the March values and today's is the percentile → BCa change
  (`2026999ad`) and later scorer changes, not D63.
- **The D42 class-B records** were made under `PYTHONHASHSEED=0` and
  reproduce exactly: today's `main` at hash seed 0 gives every interval in
  `fair-384-vs-512-march-sweep.json` and in the B-17 and B-18 "as is"
  comparisons to the last digit.
- **The retest row the 2026-10-05 check examined** (row [45] of
  `results/retest/pairwise-bootstrap-comparisons.json`): that report
  already found its committed CI upper bound (−0.00096) inside the range
  four hash seeds give with the historical library (−0.00083 to −0.00137).
- **The S3 record's stopped lines** ("OLD does not reproduce",
  `reports/s163-agent-records/d57-4-rescore-s3-deltas.md`): no. None of
  them goes through a varying site. The h13 aggregation sweep uses
  `bootstrap_ci`, whose tiles follow the bounds file (stable in the
  harness); its 54 bounds moved with the BCa adapter fix `122104b8a`
  (D61 (1)). The H2 contrasts moved with their inputs (951 → 954
  detections; D61 (2)); A-06 carries pre-D42 p fields; A-09 moved with
  costs; the uplift flatten with registrations and costs.

## 6. Integrity

- Every replay ran twice (`run1`, `run2`) in separate copies; for every
  family, ref, hash seed, and output the two runs' digests agree after
  timestamps (`generated` and similar keys, ISO times in Markdown) and the
  copy's own path are removed (`out/impact-rows.json`,
  `run1_equals_run2_digests`, 96 entries). The March-library
  replays and the function-level harness (on `main` and on the fix, before
  and after the merge) also agree run for run.
- The fixed code gives the same output under every hash seed it ran with
  (1 and 2; the harness 0–3).
- `journalctl -k -b | grep -c -i "bad page"` on sapphire read 0 before the
  first run and 0 after the last.
- Run in three workers at most; free disk stayed above 39 GB.

## 7. Reproduction

From the clone root on sapphire, with `PY=~/Code/map-reader-llm/.venv/bin/python`
and `S=reports/s163-agent-records/bootstrap-hash-order-scripts`:

```bash
$PY $S/hash_seed_harness.py --out harness.json      # 12 functions, hash seeds 0-3
$PY -m pytest -q tests/test_hash_seed_determinism.py
# Replays: $S/drivers/run-impact-*.sh (as run, from /tmp/d63-runs/) call
# $S/script_replay.py with the inputs listed there; then
$PY $S/impact_summary.py --repo . --work /tmp/d63-runs --out $S/out
$PY $S/impact_render.py --rows $S/out/impact-rows.json   # Markdown, not committed
$PY $S/record_tables.py --rows $S/out/impact-rows.json --work /tmp/d63-runs --repo .
$PY $S/merged_check.py --work /tmp/d63-runs --out $S/out/merged-check.json \
    --premerge-main $S/out/harness-main-67a3f2795-run{1,2}.json \
    --premerge-fix $S/out/harness-fix-premerge-run{1,2}.json
```

## Changelog

### 2026-10-13 — Original publication

First version: the sweep, the five fixes, the tier-1 test and its red
sentinel, the merge with PR #33, and the impact replays.
