# D60 (3): the consensus route keeps contributing tiles

> **Last revised**: 2026-10-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), an overnight subagent of the main Session 163
  session (workstream `d60-consensus-route`); code and runs in a scratch
  clone on sapphire, from about 12:40 UTC on 2026-10-12 (the night of
  12–13 October in Sydney).
- **Repository**: `map-reader-llm`, branch `d60-consensus-route` from
  `main` at `c546f6901`. The fix is commit `4e9d659ab`.
- **Rulings**: `planning/pi-decisions-2026-09-20.md` D60 (3) and D61 (2).
- **Where the outputs are**: `~/scratch/d60-consensus-route-2026-10-12/`
  on sapphire. `out/new1-{20,30}m/` and `out/new2-{20,30}m/` are the two
  independent runs of the fixed route; `out/old-{20,30}m/` is the
  pre-fix route on the same inputs; `out/delta-{20,30}m.json` hold every
  row tabulated below; `replay/t389043b80/` is the D61 (2) replay tree;
  `bin/` holds the drivers, `logs/` and `pids/` the logs and exit codes.
- **Guarantees**: no model Application Programming Interface (API) call;
  nothing under `results/` and no other document was changed. Every
  number below comes from a run in the scratch clone, not from a
  committed file being rewritten.

**Conventions.** "Committed" is the file under `results/pairwise/`
(2026-03-28); "OLD" is today's pre-fix code (`main`, `c546f6901`) re-run
on today's inputs; "NEW" is the fixed route. Where OLD reproduces the
committed file, NEW − committed is the effect of the fix alone. PV is
proposer–verifier; BH is the Benjamini–Hochberg false discovery rate
(FDR) correction that `scripts/apply_fdr_correction.py` applies within
each family (confirmatory, exploratory).

## 1. D61 (2): the 951 → 954 single-pass arm is an input change

**Finding: the code did not change; the pass files did, before they
were tracked.** Under D58 Q2 the two March contrasts therefore stay as
historical records; today's values sit beside them in § 3.

**The replay.** The brief's rule, `git log --until=2026-03-28T06:53:00Z
-1`, returns `bb73b52f5` (2026-03-26), which does not contain
`scripts/run_pairwise_tests.py` or `scripts/pairwise_permutation_test.py`:
both were first committed at 2026-03-28T07:17Z (`389043b80`, `0f5be48d7`),
about 23 minutes after the run's last write (06:54:36Z), so the run used
them uncommitted. Every
consensus-path file (`analyse_consensus_sweep.py`, `merge_passes.py`,
`analyse_phase2_results.py`, `paired_permutation_consensus.py`,
`lib_advanced_metrics.py`, `evaluate_pv_results.py`) is identical between
`bb73b52f5` and `389043b80`. The replay therefore used a `git archive` of
`389043b80` (scripts and the 384 px frame and references), with today's
`outputs/retest/h11-single-pass-384-t0` copied in (pass-file MD5 hashes
identical to the tracked files), building the "Single-pass text 5-of-5"
arm (`brief-text-t0,5,5`) through that tree's own
`load_consensus_detections`:

| Quantity | Committed (2026-03-28) | March code, today's files | Today's code (OLD) |
|---|---:|---:|---:|
| Detections | 951 | **954** | 954 |
| F1 @ 20 m | 0.544012 | 0.545716 | 0.545716 |
| F1 @ 30 m | 0.554113 | 0.555796 | 0.555796 |

The replay's pass counts are 1,093, 1,107, 1,113, 1,090, and 1,093
features (each equal to its meta's `total_detections`), clustering to
1,105 clusters, 954 of them with five votes.

**Corroboration.**

- The 10-of-10 arm of the same pool moved too: 898 detections in the
  committed March table (`results/paper-tables/metrics_master.csv`,
  `71d81cd5e`), 901 from the March code on today's files.
- Two earlier March runs recorded 951 for the 5-of-5 set:
  `results/h11-384-single-pass-t0-rerun/consensus-sweep-results.csv`
  (report timestamp 2026-03-25T12:02:15Z) and
  `results/paper-eval/single-pass-t0-20m/consensus-sweep-results.csv`
  (2026-03-26T12:48:33Z).
- On amd-tower, the pass files of runs 1 and 3 to 9 carry modification
  times of 2026-03-26 23:02–23:03 +1100 (12:02–12:03Z), a day after
  their metas' timestamps (all ten metas: 2026-03-25 07:03–09:00Z), and
  after the first March sweep above; runs 2 and 10 keep times equal to
  their metas, to the second. Sapphire's copies date from
  the 2026-04-14 checkout of `3d22184d6`. This is consistent with runs 1
  and 3 to 9 having been rewritten after the first March sweep while
  the March analyses read earlier copies, but it is not proof: no
  earlier copy survives in either checkout.

**Caveat.** The replay ran under today's library versions (Python
3.13.3 in the shared virtual environment). The clustering is plain
arithmetic on the files' Universal Transverse Mercator (UTM)
coordinates, so a library effect is
unlikely, but it is not excluded.

**What else this moves.** Nothing new: the drifted inputs are the
`outputs/retest/h11-single-pass-384-t0` passes, and every committed
pairwise output that reads them is listed in § 4 (the two group-1
contrasts at each buffer, and 49 leaderboard files at 20 m and 47 at
30 m whose single-pass 5-of-5 or 10-of-10 arm differs from today's).

## 2. The fix

**Where origins live.** A committed consensus GeoJSON carries each
cluster's contributing tiles as the property `source_tiles`, a list
written by `merge_passes.apply_threshold`. The shared scorer
(`lib_advanced_metrics.scope_detections_to_frame`, D50 as merged)
reads `origin_source_tile`, `origin_tiles`, or `source_tiles`
(`ORIGIN_TILE_COLUMNS`), in any of their serialisations
(`parse_tile_list`).

**The gap.** `consensus_to_gdf` (`scripts/analyse_consensus_sweep.py`)
built a GeoDataFrame from those features and returned only
`source_tile` (first intersecting tile), `subtype`, and geometry. With no
origin column, the scorer attributed every in-memory consensus
detection by location, while the same set read from its file was
attributed by origin.

**The change** (`4e9d659ab`).

- `consensus_to_gdf` keeps `source_tiles`, one list of tile names per
  row (parsed by `parse_tile_list`, which raises on a malformed record;
  `[]` where a feature records none). `source_tile` is still assigned
  exactly as `evaluate_detections.py` assigns it to a file that lacks
  one, so the per-tile booking is also the file route's.
- **The PV loader had the same gap.**
  `pairwise_permutation_test.load_pv_detections` builds its arm with
  `evaluate_pv_results.build_candidate_gdf`, which dropped each
  candidate's `properties.source_tiles`; `extract_candidates.py` writes
  only the alphabetically first member into `source_tile`, so a
  candidate seen on two sheets could only be scored on that one. It is
  fixed the same way. Across all 271 committed candidate manifests, 9
  candidates were seen on two sheets, all in 55-map manifests; none of
  the 8 PV arms in the 32 comparisons moves.
- Docstrings of both loaders name the column.

**Tests.** `tests/test_consensus_route_origins.py` (10 tier-1):
synthetic two-sheet cases in which the location rule and the origin rule
disagree, for both builders; the committed 26-of-30 set
(`outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/consensus/consensus_t26.geojson`)
routed through `consensus_to_gdf` must give F1 0.816471 at 20 m and the
same F1 (20 m, 30 m) and per-tile table as the file read the way
`evaluate_detections.py` reads it. `tests/test_consensus_route_h2_rebuild.py`
(1 tier-2): H2's arm rebuilt from its 30 passes gives 415 detections,
one origin restored, F1 0.816471. **Red sentinel**: in a copy of
`c546f6901` with only the two test files added, all 11 fail (the
committed-set tests read 0.814118); on the branch all 11 pass.

**The acceptance check.** H2's 26-of-30 arm (`text-t0.7,30,26`) reads
F1 0.814118 on `main` and **0.816471** on the branch, equal to the
re-scored committed cell
(`results/rescore-2026-06-05/pv-diag-384/consensus-sweep/flash-high-text-n5__text-t0.7__consensus__t26/evaluation.json`,
0.8165 at four places, `n_origin_restored` 1) and to H3's value in
`reports/s163-agent-records/d57-4-rescore-s3-deltas.md`. One detection
moves: true positives 346 → 347, false positives 69 → 68, false
negatives 89 → 88.

**PR #33** (`d50-review-fixes`, unmerged, head `d99128f65`) does not
touch the three changed scripts, and `git merge-tree` with the branch is
clean. With PR #33's library and this branch's loaders, all 23 distinct
arms of the 32 comparisons give the same detections and the same F1,
precision, and recall at 20 m and 30 m as on the branch; their scope
counters are identical, and PR #33's two new counters
(`n_origin_excluded`, `n_origin_partly_excluded`) are zero for every arm.

## 3. The 32 comparisons under the fixed route

**Runs.** `scripts/run_pairwise_tests.py --config
configs/pairwise-comparisons.yaml --n-permutations 10000 --seed 42
--quiet` at 20 m and 30 m (the two buffers committed under
`results/pairwise/`), then `apply_fdr_correction.py` on each, with the
config's paths made absolute so OLD and NEW read the same files.

**Integrity (sapphire has no error-correcting code (ECC) memory).** The fixed route was run
twice per buffer into separate directories. Per buffer, all 36 files
(32 comparisons, the run manifest, and three FDR files) agree: 2 are
byte-identical (the FDR CSV and Markdown) and 34 are identical after
dropping JSON keys named exactly `timestamp` (each file's
`metadata.timestamp`, and the FDR JSON's
`metadata.fdr_correction.timestamp`). Nothing else was ignored; no
output path is recorded in the files. The comparator was checked first
by one deliberate edit (a single `p_value`), which it reported.

**OLD reproduces the committed files** in 30 of 32 comparisons at each
buffer, every field of the run manifest and the FDR table. The two
exceptions are #7 and #8, whose shared B arm is the drifted single-pass
set of § 1.

### 3.1 H2's primary contrast

PV 16-of-30 against consensus 26-of-30, confirmatory, group 1:

| Buffer | Arm A F1 | Arm B F1 | ΔF1 | p | Tile wins / losses / ties |
|---|---:|---:|---:|---:|---|
| 20 m committed | 0.890201 | 0.814118 | 0.076083 | 0.0 | 52 / 27 / 408 |
| 20 m NEW | 0.890201 | **0.816471** | **0.073730** | 0.0 | 51 / 28 / 408 |
| 30 m committed | 0.904368 | 0.825882 | 0.078486 | 0.0 | 54 / 27 / 406 |
| 30 m NEW | 0.904368 | 0.828235 | 0.076133 | 0.0 | 53 / 28 / 406 |

As predicted (arm B +0.0024, ΔF1 about 0.0761 → 0.0737, still
p < 0.0001): arm B +0.002353, ΔF1 0.076083 → 0.073730, and no permuted
difference reached the observed one in 10,000 permutations. BH
significance is unchanged.

### 3.2 All comparisons, 20 m

Values to four places; "→" marks a change (committed → NEW). The BH
column is the FDR table's marker after correction within the family.
Full-precision values, OLD included, are in `out/delta-20m.json`.

| # | G | Contrast (A vs B) | F1 A | F1 B | ΔF1 | p | BH |
|---:|---:|---|---|---|---|---|---|
| 1 | 1 | Flash HIGH text 16-of-30 + PV vs Flash HIGH text 26-of-30 | 0.8902 | 0.8141 → 0.8165 | 0.0761 → 0.0737 | 0.0000 | *** |
| 2 | 1 | Flash HIGH text 9-of-10 + PV vs Flash HIGH text 9-of-10 | 0.8564 | 0.7968 → 0.7991 | 0.0597 → 0.0573 | 0.0000 | *** |
| 3 | 1 | Flash HIGH text 4-of-5 + PV vs Flash HIGH text 5-of-5 | 0.8641 | 0.7788 → 0.7812 | 0.0853 → 0.0829 | 0.0000 | *** |
| 4 | 1 | Flash HIGH text 4-of-5 + medium vf vs Flash HIGH text 5-of-5 | 0.8592 | 0.7788 → 0.7812 | 0.0803 → 0.0780 | 0.0000 | *** |
| 5 | 1 | Flash HIGH image 3-of-5 + PV vs Flash HIGH image 3-of-5 | 0.7778 | 0.7269 → 0.7290 | 0.0509 → 0.0488 | 0.0004 | *** |
| 6 | 1 | Pro HIGH text 3-of-5 + PV vs Pro HIGH text 3-of-5 | 0.8491 | 0.8404 → 0.8429 | 0.0087 → 0.0062 | 0.2580 → 0.4128 | ns |
| 7 | 1 | Text baseline + PV vs Single-pass text 5-of-5 | 0.8142 | 0.5440 → 0.5472 | 0.2702 → 0.2671 | 0.0000 | *** |
| 8 | 1 | Image baseline + PV vs Single-pass text 5-of-5 | 0.7167 | 0.5440 → 0.5472 | 0.1727 → 0.1695 | 0.0000 | *** |
| 9 | 2 | Flash HIGH text 5-of-5 vs Flash HIGH image 3-of-5 | 0.7788 → 0.7812 | 0.7269 → 0.7290 | 0.0519 → 0.0522 | 0.0143 → 0.0141 | * |
| 10 | 2 | Flash HIGH text 9-of-10 vs Flash HIGH image 6-of-10 | 0.7968 → 0.7991 | 0.7402 → 0.7425 | 0.0565 → 0.0566 | 0.0054 → 0.0050 | ** |
| 11 | 2 | Flash MIN text 5-of-5 vs Flash MIN image 4-of-5 | 0.6397 → 0.6415 | 0.6639 → 0.6660 | -0.0242 → -0.0244 | 0.3604 → 0.3554 | ns |
| 12 | 2 | Flash HIGH text 4-of-5 + PV vs Flash HIGH image 3-of-5 + PV | 0.8641 | 0.7778 | 0.0863 | 0.0000 | *** |
| 13 | 3 | Flash HIGH text 5-of-5 vs Flash MIN text 5-of-5 | 0.7788 → 0.7812 | 0.6397 → 0.6415 | 0.1391 → 0.1396 | 0.0000 | *** |
| 14 | 3 | Flash HIGH text 9-of-10 vs Flash MIN text 10-of-10 | 0.7968 → 0.7991 | 0.6332 → 0.6352 | 0.1636 → 0.1639 | 0.0000 | *** |
| 15 | 3 | Flash HIGH text 26-of-30 vs Flash MIN text 29-of-30 | 0.8141 → 0.8165 | 0.6611 → 0.6632 | 0.1530 → 0.1533 | 0.0000 | *** |
| 16 | 3 | Flash HIGH image 3-of-5 vs Flash MIN image 4-of-5 | 0.7269 → 0.7290 | 0.6639 → 0.6660 | 0.0630 → 0.0630 | 0.0003 | *** |
| 17 | 4 | Flash MIN text T=0.7 5-of-5 vs Flash MIN text T=1.0 5-of-5 | 0.6397 → 0.6415 | 0.4712 → 0.4740 | 0.1685 → 0.1676 | 0.0000 | *** |
| 18 | 4 | Flash MIN text T=0.7 10-of-10 vs Flash MIN text T=1.0 9-of-10 | 0.6332 → 0.6352 | 0.4615 → 0.4642 | 0.1716 → 0.1710 | 0.0000 | *** |
| 19 | 4 | Flash MIN text T=0.7 29-of-30 vs Flash MIN text T=1.0 22-of-30 | 0.6611 → 0.6632 | 0.4670 → 0.4694 | 0.1941 → 0.1938 | 0.0000 | *** |
| 20 | 5 | Pro HIGH text 3-of-5 vs Flash HIGH text 5-of-5 | 0.8404 → 0.8429 | 0.7788 → 0.7812 | 0.0616 → 0.0617 | 0.0042 → 0.0041 | ** |
| 21 | 5 | Pro HIGH image 3-of-5 vs Flash HIGH image 3-of-5 | 0.6998 | 0.7269 → 0.7290 | -0.0271 → -0.0292 | 0.2939 → 0.2630 | ns |
| 22 | 5 | Pro HIGH text 3-of-5 + PV vs Flash HIGH text 4-of-5 + PV | 0.8491 | 0.8641 | -0.0150 | 0.4002 | ns |
| 23 | 6 | Flash HIGH text 16-of-30 + PV vs Flash HIGH text 4-of-5 + PV | 0.8902 | 0.8641 | 0.0261 | 0.0398 | ns |
| 24 | 6 | Flash HIGH text 16-of-30 + PV vs Flash HIGH text 4-of-5 + medium vf | 0.8902 | 0.8592 | 0.0310 | 0.0207 | * |
| 25 | 6 | Flash HIGH text 16-of-30 + PV vs Flash HIGH text 9-of-10 + PV | 0.8902 | 0.8564 | 0.0338 | 0.0017 | * |
| 26 | 6 | Flash HIGH text 16-of-30 + PV vs Pro HIGH text 3-of-5 + PV | 0.8902 | 0.8491 | 0.0411 | 0.0119 | * |
| 27 | 6 | Flash HIGH text 4-of-5 + PV vs Flash HIGH text 4-of-5 + medium vf | 0.8641 | 0.8592 | 0.0049 | 0.4701 | ns |
| 28 | 6 | Flash HIGH text 4-of-5 + PV vs Flash HIGH text 9-of-10 + PV | 0.8641 | 0.8564 | 0.0077 | 0.4656 | ns |
| 29 | 7 | Flash HIGH text 9-of-10 vs Flash HIGH text 5-of-5 | 0.7968 → 0.7991 | 0.7788 → 0.7812 | 0.0179 → 0.0179 | 0.1404 → 0.1413 | ns |
| 30 | 7 | Flash HIGH text 26-of-30 vs Flash HIGH text 9-of-10 | 0.8141 → 0.8165 | 0.7968 → 0.7991 | 0.0174 → 0.0174 | 0.0375 → 0.0357 | * |
| 31 | 7 | Flash MIN text 10-of-10 vs Flash MIN text 5-of-5 | 0.6332 → 0.6352 | 0.6397 → 0.6415 | -0.0065 → -0.0064 | 0.6338 → 0.6431 | ns |
| 32 | 7 | Flash MIN text 29-of-30 vs Flash MIN text 10-of-10 | 0.6611 → 0.6632 | 0.6332 → 0.6352 | 0.0280 → 0.0280 | 0.0005 | *** |

### 3.3 All comparisons, 30 m

| # | G | Contrast (A vs B) | F1 A | F1 B | ΔF1 | p | BH |
|---:|---:|---|---|---|---|---|---|
| 1 | 1 | Flash HIGH text 16-of-30 + PV vs Flash HIGH text 26-of-30 | 0.9044 | 0.8259 → 0.8282 | 0.0785 → 0.0761 | 0.0000 | *** |
| 2 | 1 | Flash HIGH text 9-of-10 + PV vs Flash HIGH text 9-of-10 | 0.8691 | 0.8106 → 0.8129 | 0.0585 → 0.0562 | 0.0000 | *** |
| 3 | 1 | Flash HIGH text 4-of-5 + PV vs Flash HIGH text 5-of-5 | 0.8908 | 0.7882 → 0.7906 | 0.1025 → 0.1002 | 0.0000 | *** |
| 4 | 1 | Flash HIGH text 4-of-5 + medium vf vs Flash HIGH text 5-of-5 | 0.8850 | 0.7882 → 0.7906 | 0.0967 → 0.0944 | 0.0000 | *** |
| 5 | 1 | Flash HIGH image 3-of-5 + PV vs Flash HIGH image 3-of-5 | 0.8511 | 0.7992 → 0.8013 | 0.0519 → 0.0498 | 0.0002 → 0.0003 | *** |
| 6 | 1 | Pro HIGH text 3-of-5 + PV vs Pro HIGH text 3-of-5 | 0.8645 | 0.8554 → 0.8579 | 0.0091 → 0.0066 | 0.2174 → 0.3607 | ns |
| 7 | 1 | Text baseline + PV vs Single-pass text 5-of-5 | 0.8320 | 0.5541 → 0.5572 | 0.2779 → 0.2748 | 0.0000 | *** |
| 8 | 1 | Image baseline + PV vs Single-pass text 5-of-5 | 0.7822 | 0.5541 → 0.5572 | 0.2281 → 0.2250 | 0.0000 | *** |
| 9 | 2 | Flash HIGH text 5-of-5 vs Flash HIGH image 3-of-5 | 0.7882 → 0.7906 | 0.7992 → 0.8013 | -0.0109 → -0.0107 | 0.5589 → 0.5601 | ns |
| 10 | 2 | Flash HIGH text 9-of-10 vs Flash HIGH image 6-of-10 | 0.8106 → 0.8129 | 0.8116 → 0.8138 | -0.0010 → -0.0009 | 0.9561 → 0.9577 | ns |
| 11 | 2 | Flash MIN text 5-of-5 vs Flash MIN image 4-of-5 | 0.6471 → 0.6489 | 0.7244 → 0.7265 | -0.0774 → -0.0776 | 0.0013 | ** |
| 12 | 2 | Flash HIGH text 4-of-5 + PV vs Flash HIGH image 3-of-5 + PV | 0.8908 | 0.8511 | 0.0397 | 0.0120 | * |
| 13 | 3 | Flash HIGH text 5-of-5 vs Flash MIN text 5-of-5 | 0.7882 → 0.7906 | 0.6471 → 0.6489 | 0.1412 → 0.1417 | 0.0000 | *** |
| 14 | 3 | Flash HIGH text 9-of-10 vs Flash MIN text 10-of-10 | 0.8106 → 0.8129 | 0.6412 → 0.6432 | 0.1694 → 0.1697 | 0.0000 | *** |
| 15 | 3 | Flash HIGH text 26-of-30 vs Flash MIN text 29-of-30 | 0.8259 → 0.8282 | 0.6694 → 0.6715 | 0.1565 → 0.1567 | 0.0000 | *** |
| 16 | 3 | Flash HIGH image 3-of-5 vs Flash MIN image 4-of-5 | 0.7992 → 0.8013 | 0.7244 → 0.7265 | 0.0747 → 0.0748 | 0.0000 | *** |
| 17 | 4 | Flash MIN text T=0.7 5-of-5 vs Flash MIN text T=1.0 5-of-5 | 0.6471 → 0.6489 | 0.4795 → 0.4822 | 0.1676 → 0.1667 | 0.0001 | *** |
| 18 | 4 | Flash MIN text T=0.7 10-of-10 vs Flash MIN text T=1.0 9-of-10 | 0.6412 → 0.6432 | 0.4695 → 0.4721 | 0.1717 → 0.1711 | 0.0000 | *** |
| 19 | 4 | Flash MIN text T=0.7 29-of-30 vs Flash MIN text T=1.0 22-of-30 | 0.6694 → 0.6715 | 0.4768 → 0.4792 | 0.1927 → 0.1923 | 0.0000 | *** |
| 20 | 5 | Pro HIGH text 3-of-5 vs Flash HIGH text 5-of-5 | 0.8554 → 0.8579 | 0.7882 → 0.7906 | 0.0671 → 0.0673 | 0.0010 → 0.0009 | ** |
| 21 | 5 | Pro HIGH image 3-of-5 vs Flash HIGH image 3-of-5 | 0.8212 | 0.7992 → 0.8013 | 0.0220 → 0.0199 | 0.2507 → 0.2971 | ns |
| 22 | 5 | Pro HIGH text 3-of-5 + PV vs Flash HIGH text 4-of-5 + PV | 0.8645 | 0.8908 | -0.0263 | 0.1131 | ns |
| 23 | 6 | Flash HIGH text 16-of-30 + PV vs Flash HIGH text 4-of-5 + PV | 0.9044 | 0.8908 | 0.0136 | 0.2098 | ns |
| 24 | 6 | Flash HIGH text 16-of-30 + PV vs Flash HIGH text 4-of-5 + medium vf | 0.9044 | 0.8850 | 0.0194 | 0.1162 | ns |
| 25 | 6 | Flash HIGH text 16-of-30 + PV vs Flash HIGH text 9-of-10 + PV | 0.9044 | 0.8691 | 0.0352 | 0.0009 | ** |
| 26 | 6 | Flash HIGH text 16-of-30 + PV vs Pro HIGH text 3-of-5 + PV | 0.9044 | 0.8645 | 0.0399 | 0.0106 | * |
| 27 | 6 | Flash HIGH text 4-of-5 + PV vs Flash HIGH text 4-of-5 + medium vf | 0.8908 | 0.8850 | 0.0058 | 0.4334 | ns |
| 28 | 6 | Flash HIGH text 4-of-5 + PV vs Flash HIGH text 9-of-10 + PV | 0.8908 | 0.8691 | 0.0217 | 0.0097 | * |
| 29 | 7 | Flash HIGH text 9-of-10 vs Flash HIGH text 5-of-5 | 0.8106 → 0.8129 | 0.7882 → 0.7906 | 0.0224 → 0.0223 | 0.0607 → 0.0715 | ns |
| 30 | 7 | Flash HIGH text 26-of-30 vs Flash HIGH text 9-of-10 | 0.8259 → 0.8282 | 0.8106 → 0.8129 | 0.0153 → 0.0153 | 0.0671 → 0.0668 | ns |
| 31 | 7 | Flash MIN text 10-of-10 vs Flash MIN text 5-of-5 | 0.6412 → 0.6432 | 0.6471 → 0.6489 | -0.0059 → -0.0057 | 0.6704 → 0.6740 | ns |
| 32 | 7 | Flash MIN text 29-of-30 vs Flash MIN text 10-of-10 | 0.6694 → 0.6715 | 0.6412 → 0.6432 | 0.0282 → 0.0283 | 0.0005 | *** |

### 3.4 What moved, and what did not

- **No crossings.** No p crosses 0.05 and no BH decision changes, at
  either buffer: 24 raw p values below 0.05 at 20 m and 21 at 30 m,
  before and after; 23 and 21 BH-significant. The closest call is #30
  at 20 m (N = 30 against N = 10, HIGH text): BH-adjusted p
  0.04875 → 0.04641, significant before and after.
- **Every moved arm rose.** 14 of the 15 distinct consensus arms gain
  F1, by +0.0014 (the single-pass 5-of-5 set) to +0.0027 (the T 1.0
  5-of-5 set); each has one to three detections restored to their
  origin sheet. The fifteenth, Pro HIGH image 3-of-5, restores one
  detection without changing its F1. The 8 PV arms do not move.
  So 24 of the 32 comparisons move at each buffer; the 8 that do not
  are PV against PV.
- **Group 1 (H2), #1 to #6, narrows by 0.0021 to 0.0025** at both
  buffers, since only the consensus arm moves. The largest change in p is #6 (Pro HIGH
  text, PV against consensus): ΔF1 0.0087 → 0.0062, p 0.2580 → 0.4128
  at 20 m (0.2174 → 0.3607 at 30 m), not significant before or after.
- **Consensus against consensus barely moves** where both arms gain
  (|change in ΔF1| at most 0.0009, #17). In #21 only the Flash arm moves,
  so ΔF1 shifts by 0.0021 (−0.0271 → −0.0292 at 20 m), p 0.2939 →
  0.2630, not significant before or after.
- **#7 and #8 combine two changes.** Against the committed B arm (951
  detections, F1 0.544012 at 20 m), today's inputs give 0.545716 (OLD)
  and the fix 0.547156 (NEW): ΔF1 for #7 0.270226 → 0.268522 (inputs)
  → 0.267082 (fix); p is 0.0 throughout. Under D61 (2) the March
  results stay historical, with these values beside them.

## 4. Other callers, and what would move

Nothing listed here was regenerated. "Would move" is decided arm by
arm: each committed output's arms (from its `condition_a.source` and
`condition_b.source`) were rebuilt under OLD and NEW and scored at the
output's buffer; an output moves when an arm's F1 does.

**Callers of the changed functions.**

| Caller | Uses | Committed outputs | Would move |
|---|---|---|---|
| `run_pairwise_tests.py` | `load_consensus_detections`, `load_pv_detections` | `results/pairwise/20m/` and `30m/` (32 each) | 24 of 32 at each buffer (§ 3), with each run manifest and FDR roll-up |
| | | `results/pairwise/leaderboard-20m/` (325) | 280, with its manifest and FDR roll-up |
| | | `results/pairwise/leaderboard-30m/` (300) | 264, likewise |
| | | `results/pairwise/factor-analysis-20m/` (12) | 5 |
| | | `results/e45-bootstrap-pairings/h2-rerun/` (1) | 1 (H2's primary contrast) |
| `pairwise_permutation_test.py` (command line) | consensus and PV modes | 112 committed results, all in GeoJSON mode | none |
| `analyse_consensus_sweep.py` | `consensus_to_gdf` in `evaluate_single_config` | `results/paper-eval/*/consensus-sweep-results.csv` and reports (32 directories), `results/h11-384-single-pass-t0-rerun/`, `results/retest/phase3a-consensus/` (3) | not probed; F1, its intervals, and the optimum can move wherever a set has a cross-sheet cluster, as above |
| `evaluate_tile_mcc.py` | `consensus_to_gdf`, `build_candidate_gdf` | `results/paper-eval/mcc/` | tile confusion: no. Checked on all 15 consensus arms of § 3 (identical cells with and without `source_tiles`), and so by construction: a consensus row's `source_tile` is a tile holding it, so a restored row is retained either way |
| `paired_permutation_consensus.py` | `consensus_to_gdf` | none outside `archive/` | none live |
| `evaluate_pv_results.py`, `analyse_pv_buffer_sensitivity.py` | `build_candidate_gdf` | 4-map PV sweeps and `results/paper-eval/pv/*/buffer_sensitivity.json` | none: no 4-map candidate was seen on two sheets |
| | | 55-map PV sweeps and `results/55maps-generalisation/buffer_sensitivity.json` | at most the 9 two-sheet candidates (1 in each of five 55-map union manifests, 4 in `outputs/55maps-text-min-n10-uplift/crops-3of10/`); not determined |

**Arm-level reproduction.** Today's OLD route reproduces every arm F1
recorded in these 702 files except the two single-pass arms of § 1
(5-of-5: 951 → 954 detections; 10-of-10: 898 → 901), which account for
the 2 + 2 group-1 files and 49 (20 m) and 47 (30 m) leaderboard files.
Of the 28 distinct arms, 18 move under the fix, all consensus; the 8 PV
arms and 2 consensus arms (Pro HIGH image 3-of-5, Pro HIGH text 6-of-10)
do not.

**Downstream readers of the moved files.**

- `scripts/compute_family_fdr.py` reads H2's p from the group-1 file:
  0.0 before and after, so the family set {H2, H3, H7} is not affected.
- `scripts/e45_bootstrap_pairings.py` gates a fresh
  `run_pairwise_tests.py` rerun of H2 (`h2-rerun/`) against the
  committed group-1 file. Under the fixed route the rerun reads
  0.816471 for arm B, so that gate refuses until the group-1 file is
  regenerated with it; the two must move together. (Its H3 gate already
  refuses against the committed H3 tiering under D50, 0.816471 against
  0.814118; S3 record.) The `e45-bootstrap-pairings` register row
  quotes ΔF1 +0.076083 and its intervals, which would move with them.
- `scripts/regen_e43_board.py` reads the March pairwise and leaderboard
  JSONs.
- `scripts/collect-factor-analysis.py` reads `factor-analysis-20m/`.
- **A twin with the same gap, not fixed here**: `scripts/analyse_diversity.py`
  defines its own `consensus_to_gdf`, which also drops `source_tiles`.
  Its outputs (`results/phase3c-diversity/`) are outside D60 (3); fixing
  it would move them, so it is left for a ruling.

## 5. Not done

- No committed file under `results/` was regenerated, and no register
  row or document was edited (D60 (3): report before any document
  changes).
- The `analyse_consensus_sweep.py` outputs and the 55-map PV outputs
  were not probed arm by arm (§ 4).
- The `analyse_diversity.py` twin is not fixed.

## Changelog

### 2026-10-13 — Original publication

First publication, by the overnight `d60-consensus-route` subagent. It
records the D61 (2) replay (954: an input change before tracking), the
fix of the in-memory consensus and PV routes (`4e9d659ab`), the
re-run of the 32 comparisons at 20 m and 30 m (twice, byte-compared),
and the list of other committed outputs the fix would move. No earlier
version exists.
