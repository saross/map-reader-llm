# W2 findings: the retest-era bootstrap

> **Last revised**: 2026-10-05 (original publication, Session 160). See
> [§ Changelog](#changelog) for revision history.

**Status**: workstream W2 of `planning/text-track-transmission-2026-10-05.md`,
by a read-only Opus subagent of Session 160 (computing on sapphire, no API).
Its mechanism was re-checked in session at source: the p-value
2 × min(P(d ≤ 0), P(d > 0)) floored at 1/B in `lib_advanced_metrics.py` at
`fc832dfa9` and still live today, with `tests/test_e45_bootstrap_pairings.py`
pinning the identical-arms floor as documented behaviour. Scratch paths
below are the investigation's own; its scripts, calibration and re-test
results are kept in `retest-bootstrap-check-2026-10-05-scripts/` (the raw
inventory greps and re-run outputs, 7 MB, are not: they regenerate from
the scripts). Nothing here is decided: the recommendation is the PI's to
rule (tracker W2.4).

Read-only investigation, 2026-10-05, for workstream W2 of
`planning/text-track-transmission-2026-10-05.md` (§ 4, W2.1-W2.4).
Repository `map-reader-llm`, branch `register-repair` at `97d2afaf1`
(local). Computation ran on sapphire in `/tmp/w2/` (the sapphire checkout
moved to `eb6d797e0` during the work through another session's commit;
no input used here changed). Nothing in either checkout was written.
Scratch scripts and outputs sit beside this file (listed at the end).

## W2.1 Diagnosis

### What produced the artefact

- `results/retest/pairwise-bootstrap-comparisons.json` was added by
  `fc832dfa9` (2026-03-18, "feat(stats): pairwise bootstrap comparisons
  with p-values across all phases"). The commit adds only the JSON. No
  script in `scripts/` writes it.
- The producing code was two inline `python3 -c` programmes in session
  `6bbac468` (archive
  `~/cc-archives/map-reader-llm/2026-03-16T10-03_optimise-robust-tile-retry-and-design-batch/session.jsonl.gz`,
  JSONL lines 2133 and 2147). Rows 0-60 come from the first programme
  (OFAT phases 2a-2e, 807 s); rows 61-69 come from the second (Phase 3a,
  appended to the same file).
- Both programmes call `bootstrap_effect_size_ci(a, bounds, b, bounds, ref,
  n_iterations=1000, random_seed=42, return_p_values=True)` from
  `scripts/lib_advanced_metrics.py`. At `fc832dfa9` that function is
  `lib_advanced_metrics.py:635-751`. The p-value was added the day before
  by `9d3fcbb02`.
- Inputs: one detection file per condition, the first of
  `sorted(child.rglob('detections_*.geojson'))`, which is `run_1`
  ("Use first run as representative"). Rows 68-69 compare consensus sets
  built in-session (`precompute_clusters` and `apply_threshold`).
- `significant_raw` in the JSON is "95 % percentile CI excludes 0". It is
  not "p < 0.05". The two agree on all 70 rows.

### What it does (file:line at `fc832dfa9`)

| Property | Answer | Source |
|---|---|---|
| Unit resampled | Tiles (the 340 Era-1 tiles), with replacement, n = 340 per draw. Detections and passes are not resampled | `:705` `rng.choice(common_tiles, n_tiles, replace=True)` |
| Paired? | Yes. The same tile draw is applied to both arms | `:704-708` |
| Per-tile input | TP/FP/FN per tile, from one per-map Hungarian match of the whole set, computed once per arm | `:692-697`, `compute_per_tile_tp_fp_fn` `:310-435` |
| Statistic | Micro-F1 (also P, R) of the pooled resampled counts; the difference is A − B | `:707-713`, `aggregate_tile_metrics` `:438-484` |
| Match buffer | 20 m, hard-coded in the call (the function had no buffer argument) | `:693`, `:696` |
| Iterations, seed | B = 1,000; `default_rng(42)` | session code; `:686` |
| p-value | p = max(2 · min(P*(d ≤ 0), P*(d > 0)), 1/B): the minority-tail share of the **uncentred** bootstrap distribution of the difference, doubled, floored at 0.001. It is a percentile-interval inversion, not a null distribution | `:726-736` |
| Tile order | `common_tiles = list(tiles_a & tiles_b)`: a set, so the order of the draw depends on `PYTHONHASHSEED`. The digits are not reproducible run to run (CI upper bound −0.00096 committed; −0.00083 to −0.00137 across four hash seeds; p = 0.001 every time) | `:680` |

The same p-value code is still live in the current library
(`scripts/lib_advanced_metrics.py:1945-1955`). The buffer is now an
argument (`:1854`), and the CI is BCa since `2026999ad`.

### Why it rejects between identical requests

Reproduced on sapphire (`w21_reproduce.py`, `w21_dissect.json`). The
historical library was used, loaded exactly as the session loaded it.

- **Row [45]**: `plus-hp` vs `scale-4` (Phase 2c text), ΔF1 −0.0125,
  p = 0.001.
- **The two runs differ on 5 of 340 tiles**, and on all five `plus-hp` is
  the worse one. It has 1, 2, 1, 6 and 1 more FP on them, and 1, 0, 1, 6
  and 0 fewer TP. The tiles are `K-35-062-2_Rakovski_x448_y3136` (6 FP
  more, 6 TP fewer) and four others.
- **Effect on the bootstrap.** Any resample that contains one of those
  tiles gives d < 0. A resample that contains none gives d = 0 exactly
  (0.6 % of draws), and `d <= 0` (`:730`) counts it on the same side.
  P*(d > 0) is therefore 0 and p = 1/B = 0.001, whatever the size of the
  effect. The 95 % percentile CI [−0.032, −0.001] excludes zero for the
  same reason.
- **The exact tile-swap null for the same arrays.** Swapping a concordant
  tile changes nothing, so the null is the 2^5 = 32 sign assignments of
  the five discordant tiles. Two of them, all one way and all the other
  way, are as extreme as observed: **p = 2/32 = 0.0625**. The Monte-Carlo
  permutation test (`permutation_test_float`, 10,000 perms) gives 0.0588,
  the board's value. With 5 discordant tiles, no two-sided exact test can
  reach p < 0.05.

**Mechanism.** The bootstrap asks whether the resampling distribution of
the observed difference covers zero, not how often chance alone would
produce a difference this large. When the two outputs differ on only a
few tiles, that distribution sits entirely on one side whenever those
tiles happen to agree in sign. The p-value then floors at 1/B. Under the
null, k discordant tiles all agree with probability 2/2^k: 6 % for
k = 5, 50 % for k = 2.

Two corollaries were checked on the real arrays:

- **Identical outputs reject.** Group 15's `retest-phase2b::track1-image-t0.0`
  run_2 and `retest-phase2c::track1-image-scale-8` run_1 have identical
  per-tile arrays (k = 0, ΔF1 = 0). The bootstrap gives p = 0.001 with
  CI [0, 0]. The permutation test gives p = 1.0.
- **The p-value depends on which arm is labelled A.** The ties at zero go
  to the "≤ 0" side, so swapping A and B in row [45] changes p from 0.001
  to 0.012 on identical data.

**Single-run question.** The brief asked whether the test "treats a
single run as the population". Both tests do: each conditions on one
output per arm and resamples or permutes tiles only. Neither carries
run-to-run (pass-level) variance. That is not what produced row [45].
On 340 tiles the pass-level component is small: replicate passes from
one execution are rejected about 2 % of the time by either test (W2.3).
It does matter on large test sets: on the 55-map set (8,541 tiles) both
tests reject 4 of 40 same-execution replicate pairs at 20 m, all of them
in group 11 (W2.3).

**Where the bootstrap is sound.** The failure needs few discordant tiles,
which is the T = 0 regime: median k = 27 over the replicate pairs at
T = 0.0, against 79 to 236 at T ≥ 0.3. With k > 50 the bootstrap and the
permutation test agree: 2.1 % against 1.9 % false positives, and a
Spearman correlation of p-values of 0.993 over all pairs (W2.3).

## W2.2 Inventory

**Source.** A read-only Opus subagent swept the repository: `results/**`,
`reports/**`, `docs/paper/*.md`, the decisions log, the errata, the
working notes, `osf/`, and the register. It re-read every path:line it
cites. The full inventory is in `inv/inventory.md`, the machine-readable
version in `inv/inventory.json` (107 entries, one per cited contrast, with
every citing site), the rest of the tested set in `inv/uncited.json`, and
detail in `inv/class_b_notes.md` and `inv/class_c2_notes.md`. I spot-checked
five of its anchors at source: `d17-inventory-h5-h8.md:905-919`,
`results-draft.md:229-232`, `methods-draft.md:613-619`,
`tests/test_e45_bootstrap_pairings.py:71-89` and
`ci-metadata-registry.md:146`. All five hold.

**The construction is in five code paths, not one.** The brief named three.

| # | Code | p construction | Class |
|---|---|---|---|
| 1 | `lib_advanced_metrics.bootstrap_effect_size_ci(return_p_values=True)` (`:1945-1955`) | max(2 · min(P(d ≤ 0), P(d > 0)), 1/B) | A, B |
| 2 | `compute_family_fdr.py:326-328` (H1) | same, B = 10,000 | C1 |
| 3 | `e45_bootstrap_pairings.paired_bootstrap` (`:130-132`; also used by `h6_registered_analyses.py`) | same | C1 |
| 4 | `h13_overlap_analysis.paired_bootstrap` (`:205-207`), imported by `grid_analysis`, `grid_verifier_analysis`, `grid_incumbent_rescore`, `stride_verifier_analysis` | ties counted on both sides: identical arms give p = 2, not the floor; a one-signed sparse difference still gives roughly 2 · P*(d = 0) | C2 |
| 5 | `grid_analysis.paired_interaction` (`:410-414`) | as #4 | C2 |

Producer of class A. The inventory reports "no committed producer" and
`results/ci-metadata-registry.md:146` names `scripts/run_pairwise_tests.py`,
which is wrong. The session archive identifies the actual producer:
inline code calling path #1 (W2.1).

**Counts** (from `inv/inventory.json`):

| Class | Artefacts | Entries (significant as reported) | Paper text | Confirmatory |
|---|---|---:|---:|---:|
| A | `pairwise-bootstrap-comparisons.json` (70 rows × F1/P/R) | 50 (25) | 6 (A-01, A-02, A-21, A-33, A-38, A-49) | 4 (H7, H4, H5 inputs; A[68] cited as an H3 "alternative") |
| C1 | family FDR H1, `family_fdr.json`, E45 pairings, H6 A-06 | 5 (3) | 2 (E45 CIs) | 2 (H1; the family set) |
| B | PV `pairwise-effect-sizes{,-v2}.json`, `phase3a-high-text-pairwise.json`, `fair-384-vs-512.json`, `pairwise-384px.json`, two `pro-proposer-verifier-thinking-*/comparison.json` | 18 (14) | 0 | 0 |
| C2 | `h13_overlap_analysis.json`, `grid_analysis.json`, `verifier_analysis.json`, `incumbents_common_footprint.json`, `stride_verifier_analysis.json` | 31 (15) | 25 (paper outline § R1b and claims inventory) | 0 (H13 is registered exploratory) |
| unclear | p-values with no traceable artefact | 3 (1) | 1 | 0 |

**Claims that reach the paper or the H-series**, with p as reported:

- **H7 rejected.** A[25], text T0.3 vs T1.0, p = 0.001 (the floor), BH
  0.00233. Cited at `methods-draft.md:151`, `:616` and
  `results-draft.md:230`.
- **H7 parenthetical "+0.072 at FDR p = 0.004".** Cited at
  `results-draft.md:231`. This is A[27]'s **raw** p, and A[27] is not the
  registered H7 row. Within-track BH gives 0.010 on A's own values. The
  same label appears at 25 sites, including E43 and E72.
- **H4 not rejected.** A[55], p 0.124. **H5 not rejected.** A[53]
  precision, p 0.756. **H1 not rejected.** C1-01, p 0.1774. All three are
  cited in `methods-draft.md:615-619` and `results-draft.md:226-229`.
- **"brief-text > image-only, p = 0.004".** A[1], cited at
  `methods-draft.md:615`. It also carries E68 (`protocol-errata.md:3065`)
  and `docs/pipelines.md:54`.
- **E45 "registered instrument corroborates H2/H3".** C1-03 and C1-04, CIs
  only.
- **§ R1b grid, stride and H13 block.** 25 C2 contrasts. The inventory's
  prime suspects were C2-1 (H13 A − B, p 0.0416), C2-11 (0.034), C2-30
  (0.020) and C2-10 (0.021).

**Decisions that used a bootstrap verdict** (inventory § 4):

- **A-D4 / A-D5.** E68 retires the "academic baseline" designation, and
  brief-text is carried forward, both on A[1].
- **A-D7.** E43 and E72 call A[27] "FDR p = 0.004".
- **A-D11.** The D17 audit (`reports/d17-inventory/d17-inventory-h5-h8.md:905-919`)
  cites A[45] to call the "functionally identical prompts" rationale
  "empirically falsified". That is the reverse of the truth, and the site
  is **not** in the manipulation check's affected-claims table (§ C.1).
- **B-D6.** E69 and PI ruling 1a use B-17 (Obs 187, p 0.001 at the floor)
  as evidence that two verifier configurations differed.
- **C2-D2, C2-D4, C2-D8.** These rest on C2-11, C2-30 and C2-1.

**Reporting defects the inventory found** (not test calibration; they
stand whatever the test):

- "6/10 FDR-significant" is 5/10 on A's own numbers.
- "All p > 0.19" for the image-track library contrasts is wrong: A[34] is
  0.076.
- `retest-production-summary.md:145` gives "Config-default also
  significantly beats random (p = 0.046)" (A[60]).
- The `h13` JSON stores B = 1,000 under `primary`, while the findings
  declare B = 10,000 primary per E82.
- Obs 187 cites ΔF1 +0.010 against a bootstrap mean of −0.0175 (an
  A − B sign and estimand mismatch).

**Out of scope, flagged by the inventory:**

- **An older instrument.** The February 2026 60-tile Phase 2 analyses use
  a CI-position pseudo-p (Decision 10, `analyse_phase2_results.py`). It
  feeds Decisions 16-18 and E61, and needs its own audit.
- **A test enshrines the defect.**
  `tests/test_e45_bootstrap_pairings.py:71-89` asserts that identical arms
  return p = 1/B.

## W2.3 Calibration on replicate sets

### Replicate sets and pairs

- **Source**: all 23 `replicate-group-N` flags in
  `reports/manipulation-check-2026-10-05-arms.json`. Each arm was
  expanded to every pass in its pool.
- **Correction**: `arms.json` lists at most 12 meta paths per arm, so the
  enumeration walked the pool's `run_<N>` directories. The pass count then
  equals `n_metas` for every arm.
- **Totals**: 61 arms, 520 passes (`replicate_sets.json`,
  `pass_index.json`).
- **Pairs**: every pair of passes within a group, 10,035 at 20 m plus 90
  at 50 m on the 55-map set:
  - **within-execution**: two passes of one arm;
  - **cross-arm**: passes of different arms that sent the same request;
  - **disjoint**: a random one-pass-per-pair subset per group (seeded),
    for independent tests;
  - **first-pass cross-arm**: run_1 of one arm against run_1 of another,
    which is the retest's own design.

### Scoring (one instrument for both tests)

- **Per-tile scoring**: each pass was scored once with the board's own
  per-tile path (`era1_leaderboard_tiering._read_detections_gdf` →
  `pairwise_permutation_test.assign_source_tiles` → `_per_tile_one_set` →
  `lib_advanced_metrics.compute_per_tile_tp_fp_fn`). Both tests then ran
  on the same arrays.
- **Validation against the historical scorer**: all 319 Era-1 passes were
  re-scored with the `fc832dfa9` library, loaded exactly as the March
  session loaded it. The per-tile arrays are identical for 319 of 319
  (`validation_old_vs_new.json`). On Era-1, "the bootstrap as coded" and
  "the bootstrap on the board's arrays" are therefore the same input.
- **Scopes and buffers**:

| Scope | Groups | Ground truth | Bounds (tiles) | Buffer |
|---|---|---|---|---|
| Era 1, 512 px | 13-24 | `mounds-reference.geojson` | `full_evaluation_bounds.geojson` (340) | 20 m |
| 4-map, 384 px | 1-8 | same | `384/full_evaluation_bounds.geojson` (487) | 20 m |
| h10 test | 10 | same | `384/h10_test_bounds.geojson` (327) | 20 m |
| 55-map | 11, 12 | `best-available-gt-55maps-r2.geojson` | `384/55maps_evaluation_bounds.geojson` (8,541) | 20 m and 50 m |

- **Instrument settings**:
  - **(a) Retest bootstrap as coded**: paired tile resampling, micro-F1,
    B = 1,000, seed 42, p = max(2 · min tail, 1/B). Vectorised;
    `rng.integers(0, n, (B, n))` was checked to be the same stream as B
    calls of `rng.choice(tiles, n, replace=True)`. Tile order is the
    bounds order (the original's set order is hash-dependent).
  - **(b) Paired tile-swap permutation**: `permutation_test_float`,
    imported from `n1_baseline_leaderboard_tiering` (the kernel
    `era1_leaderboard_tiering.py` imports), 10,000 permutations, seed 42,
    two-sided.
- **Instrument mismatches**:
  - **Buffer on the 55-map set**: the bootstrap's own buffer is 20 m
    (hard-coded); the 55-map board's headline is 50 m. Both buffers were
    run, and each test was given both.
  - **55-map ground truth**: the two arms of group 11 were originally
    scored against different references. Here every 55-map pass is scored
    against r2.
  - **Single passes, not pass-means**: the board compares pass-mean cells
    where K > 1. Here each test sees single passes, which is the retest's
    design.
  - **No re-scoring was needed** beyond this.

### Results: false-positive rate at α = 0.05

Rates are shown as rejections / pairs, with Wilson 95 % intervals.

| Set | Pairs | Bootstrap (as coded) | Permutation (board) |
|---|---:|---|---|
| All pairs, 20 m | 10,035 | 253 (2.5 % [2.2, 2.8]) | 223 (2.2 % [2.0, 2.5]) |
| Clean set: 340/487/327-tile scopes, groups 4 and 5 excluded (below) | 9,852 | 215 (2.2 % [1.9, 2.5]) | 187 (1.9 % [1.6, 2.2]) |
| Clean, within-execution | 4,269 | 106 (2.5 %) | 97 (2.3 %) |
| Clean, cross-arm | 5,583 | 109 (2.0 %) | 90 (1.6 %) |
| Clean, disjoint (independent) pairs | 218 | 5 (2.3 % [1.0, 5.3]) | 5 (2.3 % [1.0, 5.3]) |
| First-pass cross-arm (the retest's design) | 84 | 5 (6.0 % [2.6, 13.2]) | 2 (2.4 % [0.7, 8.3]) |
| Era 1, T = 0.0 | 36 | 3 (8.3 % [2.9, 21.8]) | 0 (0 % [0, 9.6]) |
| Era 1, T > 0 | 8,206 | 156 (1.9 %) | 133 (1.6 %) |
| Clean, k ≤ 50 discordant tiles | 96 | 12 (12.5 % [7.3, 20.6]) | 6 (6.2 % [2.9, 13.0]) |
| Clean, k > 50 | 9,756 | 203 (2.1 % [1.8, 2.4]) | 181 (1.9 % [1.6, 2.1]) |
| Groups 4 and 5, cross-execution | 39 | 27 (69 %) | 26 (67 %) |
| Groups 4 and 5, within-execution | 54 | 0 | 0 |
| 55-map, 20 m (all pairs) | 90 | 11 (12.2 %) | 10 (11.1 %) |
| 55-map, 20 m, within-execution | 40 | 4 (10 %) | 4 (10 %) |
| 55-map, 50 m (all pairs) | 90 | 17 (18.9 %) | 18 (20.0 %) |
| 55-map, 50 m, within-execution | 40 | 1 (2.5 %) | 1 (2.5 %) |

**p-value distributions** (all 10,035 pairs at 20 m):

| Statistic | Bootstrap | Permutation |
|---|---|---|
| 5th / 25th / 50th percentile | 0.088 / 0.323 / 0.564 | 0.096 / 0.329 / 0.570 |
| Share ≤ 0.01 | 0.46 % | 0.33 % |
| Share ≤ 0.05 | 2.6 % | 2.2 % |
| Share ≤ 0.10 | 5.8 % | 5.3 % |
| Pairs at p ≤ 0.001 | 6 | 2 |

The bootstrap's six pairs at the floor include the three sparse ones
above: k = 0 (identical outputs), k = 2 (ΔF1 −0.0013, permutation
p = 0.50) and k = 5 (row [45]). The rest have large effects that the
permutation test also rejects. Spearman ρ between the two tests' p-values
is 0.993. Of the 96 clean pairs with k ≤ 50, the bootstrap's p is the
smaller in 72.

**Reading.**

1. **Both tests are conservative overall.** On replicates of 327-487
   tiles, under exchangeability, both sit at about 2 %, below the nominal
   5 %.
2. **The bootstrap fails where discordance is sparse.** It is
   anti-conservative for k ≤ 50, roughly double the permutation test's
   rate: 12.5 % against 6.2 %. It is worst at T = 0.0 on Era 1 (3 of 36
   against 0 of 36). The retest's text runs at T = 0.0 sit in exactly
   this regime (k = 5 to 14 for the five Phase 2c text arms).
3. **The permutation test does not fail there.** It is exact under
   tile-wise exchangeability. Its 6 of 96 rejections in the sparse class
   are all in group 7, the 384 px text set at T = 0:
   - **five** set `retest-h11-single-pass-384-t0` passes against the
     single `pv-diag-384::text-baseline` pass, a separate execution whose
     F1 (0.520) sits above all ten retest-h11 passes (0.496-0.509);
   - **one** is within-execution (k = 30, p = 0.036).
4. **Surprise: two flagged replicate groups are not exchangeable.**
   - **Group 4**: n1-outstanding `image-t03` (F1 0.590-0.594, about 750
     detections) against pv-diag `image-n5` T = 0.3 (0.548-0.570, about
     810).
   - **Group 5**: n1-outstanding `pro-image-high-t0` (0.540-0.548, about
     745) against pv-diag `flash-high-image` T = 0.0 (0.476-0.487, about
     890).
   - Both tests reject 67-69 % of their cross-execution pairs and none of
     their within-execution pairs. Identical transmitted signatures did not
     give identical output distributions across these executions.
   - **Cause unverified**: serving drift between dates, or a request
     difference the signature does not record. For group 5, E57's
     "intended Pro, dispatched Flash" could be re-checked against these
     detection counts.
   - This is a property of the data, not of either test.
5. **Pass-level variance on large test sets.** On the 55-map set
   (8,541 tiles) both tests reject the same pairs to within one.
   - **Within-execution**: 4 of 20 rejected in group 11 at 20 m, 1 of 20
     at 50 m. Group 12: 0 of 20 at either buffer.
   - **Cross-execution at 50 m**: 7 of 25 in group 11, and 9 (bootstrap)
     or 10 (permutation) of 25 in group 12. In group 12 the five
     `-uplift` passes score F1@50 0.411-0.418, against 0.403-0.409 for the
     original five.
   - **Reading**: on this many tiles, pass-level and execution-level
     shifts (run-to-run variance that neither test models) become
     detectable. A cell-vs-cell claim on the 55-map set needs a test that
     carries pass-level variance, such as resampling passes or a mixed
     model. This affects both tests alike and is not the retest defect.

Per-group detail is in `calibration_summary.json` (`by_group_20m`). The
per-pair CSV (`calibration_pairs.csv`, 10,125 rows) carries k, both
p-values, the bootstrap CI and the flags.

## W2.4 Re-test and recommendation (for the PI; nothing decided here)

### Which test

**Recommended: the paired tile-swap permutation test**
(`n1_baseline_leaderboard_tiering.permutation_test_float`, equivalently
`pairwise_permutation_test.run_permutation_test`). Use 10,000
permutations, seed 42, the board's buffer, and BH-FDR within each
reported family, as the boards already do.

- **Exact under the null that applies.** Under tile-wise exchangeability,
  which is what identical requests satisfy, the test is exact.
- **Calibrated on 9,852 replicate pairs**: 1.9 %.
- **Agrees with the bootstrap where the bootstrap is sound**: k > 50,
  ρ = 0.993.
- **Differs only where the bootstrap fails**: sparse discordance and
  identical outputs.

**If a bootstrap is kept for interval estimates,** no p-value or
"CI excludes 0" verdict should be read from it when k is small. The
p-value code is live in all five paths listed in W2.2, and
`tests/test_e45_bootstrap_pairings.py:71-89` asserts the identical-arms
behaviour. Whether to retire `return_p_values`, add a k-guard, or switch
the CI/p construction is a PI call.

**What neither test answers.** Neither carries pass-level (run-to-run)
or execution-level variance:

- On 8,541 tiles (the 55-map set), both reject same-execution replicates
  (group 11, 4 of 20).
- Across separate executions both reject heavily (groups 4 and 5,
  67-69 %).
- **Consequence**: a claim that one *configuration* beats another, made
  from one run each, needs a pass-resampling or random-effects design.
- **Status**: this is a limit of the replacement, not a W2 defect. It
  bears on W5 and on Obs 187 / E69-type inferences ("p small, therefore
  the configurations differ").

### Re-test results

**Class A: all 70 rows.**

- **Method**: exact March inputs (first run file per condition; rows
  68-69 from the Stage B board cells), 20 m, F1/P/R.
- **Outputs**: `retest70.json`, `retest70.csv`.
- **Reproduction**: committed ΔF1 reproduced within 0.002 except for 9
  rows (max 0.0059: Phase 2c image `canonical`-involving rows and rows
  22, 37, 38, 51, 52).
- **Input caveat**: most first-run files carry local mtimes of 2026-03-22
  15:44 (AEDT), after the 2026-03-18 run. The cause is **unverified**.

| Measure | Bootstrap (committed) | Permutation (same inputs) |
|---|---|---|
| F1 rows significant at raw 0.05 | 24 | 21 |
| F1 rows flipping | — | [18] image T0.7 vs T1.3 (0.042 → 0.0588); **[45]** (0.001 → 0.0588); [60] config-default vs random (0.046 → 0.0563) |
| Precision flips | — | [45] (0.001 → 0.0588); [57] canonical-first vs random (0.046 → 0.057) |
| Recall flips | — | [4] (0.046 → 0.065), [14] (0.034 → 0.051), [26] (0.038 → 0.054), [33] (0.032 → 0.083), [45] (0.001 → 0.249) |
| Within-phase BH (F1), significant rows | 2a {1,4,8}; 2b-img {11,12,13,15,16}; 2b-txt {22,23,25,26,27}; 2c-txt {45}; 2e {59}; 3a {62,63,64,65} | identical, **except [45] drops** (BH 0.588) |

- **The A[45] verdict** is the only within-phase BH change.
- **A[18] and A[60]** were already non-significant after BH (0.070 and
  0.138 on the bootstrap). The retest summary's "config-default
  significantly beats random (p = 0.046)" (`:145`) does not survive
  either way.

**Claims that matter to the paper:**

| Claim | Committed p | Permutation p (same single runs) | Board p (pass-mean cells) | Verdict |
|---|---|---|---|---|
| H7 primary A[25] | 0.001 (floor) | 0.0002 | 0.0 | unchanged |
| H4 primary A[55] | 0.124 | 0.1366 | 0.1366 | unchanged (null) |
| H5 primary A[53], precision | 0.756 | 0.7262 | — | unchanged (null) |
| A[1] brief-text > image-only (E68) | 0.004 (BH 0.020) | 0.0055 (BH 0.030) | 0.0003 | unchanged |
| A[27] text T0.7 > T1.0 ("FDR p = 0.004") | 0.004 raw (BH 0.010) | 0.0055 raw (BH 0.011) | 0.0 | significance unchanged; the "FDR" label stays wrong |
| A[59] canonical-last > random | 0.002 | 0.0019 | 0.0019 | unchanged |
| A[68] consensus 18/30 > canonical-last | 0.001 | 0.0014 | 0.0014 | unchanged |
| A[69] HIGH consensus > minimal | 0.001 | 0.0004 | 0.0004 | unchanged |
| A[67] minimal > HIGH (single pass) | 0.001 | 0.0 | — | unchanged |
| A[54] text terse > verbose, recall | 0.001 | 0.003 | — | unchanged |

**H-series family** (`compute_family_fdr.py` step-up, q = 0.05, m = 7),
with the permutation values substituted for H7, H4 and H5:

- **Inputs**: H2 1e-4, H3 1e-4, H7 2e-4, H4 0.1366, H1 0.1774 (not
  re-tested, below), H5 0.7262, H8 0.8344.
- **Rejection set**: **{H2, H3, H7}, unchanged**.

**Class C2: all 33 bootstrap rows (31 distinct contrasts).**

- **Method**: re-run through the committed scripts. `paired_bootstrap`
  was wrapped so each call also ran the permutation test on the same
  arrays, and outputs were redirected to `/tmp/w2/c2/`.
- **Reproduction**: every committed bootstrap p was reproduced exactly.
  The exception is `grid_analysis`, whose committed run used B = 10,000
  where the default is 1,000.
- **Provenance gap**: the two `ladder384` rows are in the committed JSON
  but **not** in the committed `stride_verifier_analysis.py` `CONTRASTS`.
  I added them with the cells their names imply; the reproduction exactly
  matched the committed values (0.0202, 0.297).
- **Results** (`c2/c2_retest_rows.json`):

| Contrast | Bootstrap p | Permutation p | k |
|---|---|---|---:|
| C2-1 H13 A − B (B = 10,000; findings' primary) | 0.0416 | 0.0385 | 284 |
| C2-1 H13 A − B (B = 1,000; JSON "primary") | 0.0500 | 0.0385 | 284 |
| C2-10 | 0.0208 | 0.0235 | 65 |
| C2-11 | 0.034 | 0.0373 | 81 |
| C2-21 | 0.015 | 0.0196 | 76 |
| C2-29 | 0.0206 | 0.0222 | 65 |
| C2-30 | 0.0202 | 0.0215 | 65 |

- **No C2 verdict changes** at 0.05. The other C2 rows are ties or nulls
  on both, or floor values that the permutation test also puts at
  p ≤ 0.0003.
- **Why they agree**: C2 contrasts have k = 51-437, the regime where the
  two tests agree.

**Class B: partly re-tested.**

- **B-17** (Obs 187, E69 and PI ruling 1a). The recorded inputs were
  renamed after March and were mapped by `run.meta.json` thinking level
  (`pro-text-minimal-verifier`, `pro-text-medium-verifier`,
  `crops/pro-medium-text-baseline`). The mapping is confirmed by
  reproducing the committed bootstrap mean (−0.0172 against −0.0175) and
  p (0.001). Result: bootstrap 0.001 → permutation **0.0047** (k = 20).
  Still significant (`b17_retest.json`).
- **B-18**: 0.166 → 0.1626.
- **B-6**: HIGH vs minimal at T0.7, run 1. Current files give F1
  0.434/0.569 against the recorded 0.452/0.596, so the data differ (cause
  unverified). Both tests give p ≈ 0 (k = 248).
- **B-7 and B-8**: Stage B board look-ups give the N = 5 HIGH vs minimal
  contrast at 0.0038 (bootstrap 0.002), and the three HIGH-temperature
  nulls stay null.
- **Not re-tested**: `fair-384-vs-512.json` (B-9 to B-15, decision B-D1)
  and the PV `pairwise-effect-sizes{,-v2}.json`. Their inputs are not at
  the recorded paths: `compare-384-vs-512.py` reads a March
  `outputs/references` layout and 512 px PV files that no longer resolve.
  Rebuilding them is path archaeology, perhaps 1-2 hours of agent time;
  the compute is negligible.
- **Expected outcome of the B re-test**: effects of 0.06-0.13 F1 on 487
  tiles are unlikely to sit in the sparse regime. That is an expectation,
  not a result.

**Class C1.**

- **H1 (pooled five-condition contrast)** has no direct tile-swap
  analogue. The registered statistic is a mean of per-run F1s across
  unequal groups. It is a null (p 0.1774), and Phase 2a condition pairs (run_1 against run_1) have
  k = 164-209, the regime where the tests agree. **Not re-tested.**
- **E45 companions** (Δ +0.076 and +0.427, CIs far from 0) and **H6
  A-06** (p never cited): not re-tested.

### Conclusions that change

1. **A[45]**: "scale-4 > plus-hp on text, p = 0.001". On the calibrated
   test it is p = 0.0588 (BH 0.588). It was already void as a library
   claim (C-01, C-03). This is the only reported verdict that flips.
2. **A[60]**: "config-default significantly beats random, p = 0.046"
   (`retest-production-summary.md:145`). Permutation gives 0.0563, so it
   is not significant at raw α. It was also not significant after BH on
   the bootstrap.
3. **A[18] and recall/precision raw-level flips**: [4], [14], [26],
   [33], [57]. The inventory finds none of them cited as significant in
   paper text. The "6/10 FDR-significant" Track 1 count is already 5/10
   on A's own values.
4. **No confirmatory H-series verdict changes**, no paper-text C2 verdict
   changes, and E68's A[1] holds.
5. **Interpretive change, not a p change.** Two decisions read a small p
   between single runs as proof that the configurations differ: D17
   (A-D11) and E69 / PI ruling 1a (B-D6). A[45] shows that this inference
   is unsafe. B-17's difference is still significant on the permutation
   test, but W2.3 shows separate executions of one request can differ
   significantly. B-17 is consistent with a configuration effect; it
   cannot by itself prove one.

### Cost (sapphire, 24 cores, all measured on this run)

| Step | Wall time |
|---|---|
| Pass enumeration | seconds |
| Scoring 520 passes (20 workers) | about 2 min |
| Historical-scorer validation (319 passes) | about 1 min |
| 10,125 replicate-pair tests (20 workers) | about 3.6 min |
| 70-row re-test | about 1 min |
| C2 scripts (run in parallel) | 2-10 min each |
| B-17 | about 1 min |

Re-testing everything except class B's unresolved inputs took under 30
minutes of wall time. No API calls.

## Files

Scratch scripts (read-only; each writes only to `/tmp/w2/`):

- `w21_reproduce.py`: row [45] under the historical library, with
  dissection.
- `w23_enumerate.py`: replicate sets → passes.
- `w23_score.py`: per-tile arrays and historical-scorer validation.
- `w23_tests.py`: both tests on every pair.
- `w23_summarise.py`: the calibration summary.
- `w24_retest.py`: the 70-row re-test.
- `c2_retest.py`: C2 scripts with a permutation wrapper.
- `b17_retest.py`: B-17 and B-18.
- `fair384_retest.py`: attempted; inputs missing.

Outputs (copied here from sapphire `/tmp/w2/`):

- `calibration_pairs.csv` (10,125 pairs)
- `calibration_summary.json`
- `replicate_sets.json`
- `pass_index.json`
- `validation_old_vs_new.json`
- `w21_dissect.json`
- `w21_hashseed_{1,2,3}.json`
- `retest70.{json,csv}`
- `c2/` (per-script captures and `c2_retest_rows.json`)
- `b17_retest.json`
- `inv/` (inventory)
- `session-extract.txt` (the producing session code)

## Changelog

### 2026-10-05 — Original publication (Session 160)

Commissioned after the manipulation check found the retest-era bootstrap
reporting p = 0.001 between identical requests.
