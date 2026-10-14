# Sapphire fault windows: what was computed there, and what is still unverified

> **Last revised**: 2026-10-14 (D62 (7) re-check verdicts marked; record
> `reports/s164-agent-records/fault-window-rechecks.md`). See
> [§ Changelog](#changelog) for revision history.

- **Prepared by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a read-only overnight agent of Session 163,
  2026-10-12/13 (UTC).
- **Task**: the approved first step of the item "Re-check results computed
  on sapphire in the fault windows" in `planning/paper-writeup-continuity.md`.
  This document is a list only. Nothing has been re-run.
- **Repository read**: local `main` at `d84c22981`. The tracked data under
  `results/` and `outputs/` is unchanged since PR #29's data head
  `f2277608d`, apart from three study scripts (`55ff8a02e`, `90f16c9ff`)
  and the running probe's files.
- **Guarantees**: no branch, commit, or file in the repository was written.
  On sapphire I only read: `journalctl`, file listings, `md5sum`, and
  existing JSON records under `~/scratch/`. No model Application Programming
  Interface (API) was called.

## 1. The windows, as confirmed from sapphire's journal

`journalctl --list-boots` and `journalctl -k -b <n>` on sapphire, read
2026-10-13:

| Boot | Span (UTC) | `Bad page state` reports | Window and risk |
|---|---|---:|---|
| −3 | 2026-01-29T11:15:32Z – 2026-05-06T13:58:23Z | 36, all 2026-05-06 11:44:18Z – 13:58:23Z | W3: 2026-05-06 high, the rest low |
| −2 | 2026-05-12T00:26:22Z – 2026-09-05T06:00:05Z | 0 | clean |
| −1 | 2026-09-05T06:58:03Z – 2026-10-10T04:56:47Z | 5: 2026-10-05T04:14:24Z, then four 2026-10-09 13:51Z – 15:22:55Z | W2 (before 10-05T04:14Z) low; W1 (from then) high |
| 0 | 2026-10-10T05:09:43Z – | 0 | fixed (JEDEC 4,800 MT/s; soak passed) |

The 36 reports of 2026-05-06 name only `bash` (19), `sleep` (8), `grep` (4),
and kernel workers (5). The 5 reports of boot −1 name `python`
(`reports/s163-agent-records/d57-4-rescore-census.md` § Sapphire).

## 2. Method

1. For every tracked file under `results/`, `reports/`, and `outputs/`, I
   took the commit that last changed it and bucketed it by that commit's
   author date in UTC. This finds what was last written in each window. A
   file whose numbers were computed in a window but re-touched afterwards
   by a stamp or prose edit is caught only where I traced it (the restamp
   `8e343e6e7`, the board's cost edits).
2. Host evidence, in order of strength: a commit body or report saying
   where it ran ("on sapphire", "local"); author `saross`, which is
   sapphire's git identity; an author-date offset of `+0000` (sapphire's
   clock is UTC; amd-tower commits carry `+1000`/`+1100`, zbook in May
   `+0800`); scratch directories and their modification times on sapphire.
3. Subtracted as verified by exact reproduction: the census
   (`census_cells.csv` read from sapphire: 2,123 of 2,216 replays
   reproduce, 432 byte-diff cells, 25 Stage A cells); PR #29's independent
   re-run (2,262 files identical); Phase 3's OLD reproductions (the
   `phase3-out/diffs/*.txt` files on sapphire); Phase 4's Run B and Run C
   comparison (57 files) and its BEFORE-against-committed comparison
   (`q4/compare-committed-vs-before.json`: 193 identical, 12 differing only
   in metadata); the soak (part of the census). I also counted two
   computations that agree exactly as a verification even when both ran in
   a window: a random set bit cannot produce agreement.
4. "Feeds" names the register row (`results/analyses-manifest.json`), the
   Results claims inventory row (`docs/paper/results-claims-inventory-2026-09-12.md`),
   or the PI ruling that uses the artefact.

## 3. Totals

Number-bearing tracked files (logs, images, scripts, and backups
excluded), by the window of their last change. "Partly" means the points
reproduce and the intervals or flags do not.

| Window | Files | Verified exactly | Partly | Not verified | of which prose `.md` | of which `.geojson` |
|---|---:|---:|---:|---:|---:|---:|
| W1 (high) | 3,890 | 3,083 | 0 | 807 | 68 | 76 |
| W2 (low) | 3,858 | 2,349 | 77 | 1,432 | 193 | 463 |
| W3, 2026-05-06 (high) | 66 | n/a (computed on zbook, not sapphire) | | | | |
| W3, rest (low) | 6,618 | 4 | 4 | 6,610 | 330 | 2,052 |

W1's verified 3,083: PR #29 re-run 2,257; pricing sidecars equal to a
rebuild 729; Phase 4 59; tier-1 drift checks after the fix 33; Phase 3 5.
W2's verified 2,349: census 2,157; S2 byte-diff 84; Phase 4 BEFORE 71;
tier-1 drift checks 24; Phase 3 8; in-window repeat runs 5. W2's partly
verified 77 are 69 tile-join-withheld cell files and 8 adapter cells with
no recipe. The unverified counts include inputs (API outputs, unions,
materialised cells) and prose that only quotes other files. The counts are
mechanical: §§ 4.1 and 5.1 also credit a few files the table leaves under
"not verified" (the input-drift trace, the D51 provenance outputs, and the
`n5-companion` evaluation, 14 files). Sections 4 to 6 reduce the rest to the
groups that matter.

## 4. Window 1: 2026-10-05T04:14Z to 2026-10-10T05:09Z (highest risk)

### 4.1 Already verified (subtracted)

| Artefact or group | Verified by |
|---|---|
| PR #29: 737 Phase 2 cells, 12 Stage A cells, stride CSVs, manifests, renderings (2,257 files) | Independent re-run 2026-10-09T21:57Z to 10-10T00:08Z; 2,262 files identical (S2 record changelog) |
| `5986316b5` (D42 p values, 10-05T07:15Z): `e45_bootstrap_pairings.json`, `family_fdr.json` and its metadata, `h1_cmt0106_pooled_modality.json`, `h13_overlap_analysis.json` | Phase 3 OLD reruns, 0 differing leaves (`diffs/e45-fdr-h8.txt`, `diffs/h13.txt`) |
| Run B and Run C scoring outputs under `results/modality-bridge-2026-10-07/` (cells, floors, gap tests, verifier SD; 57 files) | Phase 4 re-run: 49 identical, 8 differing only in set-aside metadata (`runbc-compare.json`) |
| W2.7 floors-v2 `subset_cells_all.csv` and § 6 `gates.json` | Phase 4 BEFORE outputs byte-identical (I compared `md5sum` against `~/scratch/q4-repaired-readers-2026-10-09/q4/before/`) |
| 729 cost sidecars and the archive ledger (`8e343e6e7`, run on sapphire) | Only the register stamp changed; the content "matches a rebuild exactly" (commit body) |
| Input-drift trace (`abe87128f`) | Census vintage replays: 26 of 26 drifted cells reproduce on their inputs as scored |
| D51 ladder provenance (`1fc1f72df`, `94a9e5cc7`, `63f2ecf16`) | A re-run of the gate survey on sapphire (scratch `d51-review-fixes-2026-10-10`, 2026-10-09T22:04Z – 22:27Z) reproduced the committed survey on all fourteen ladders (report); pool rebuilds are byte-equality tests |
| D51 clipped 3.7 GS ladder, 0.8682 / 0.9073 / 0.9066 / 0.9068 | Three separate W1 runs agree: the k-ladder frames report's counterfactual (`76e1af87a`), the blast-radius gate (ii), and scorer-frames `ladders_new.json` ("The ruled ladder numbers hold") |
| Q4 before→after deltas (S4 record) | Agree exactly with the Q4 agent's 2026-10-08 prediction |
| Run C requests byte-identical to Run B's | Hash equality; corruption cannot manufacture a match |
| 33 generated renderings (post-run reports and similar) | Tier-1 drift checks at PR #29's merge head on the fixed boot (D59) |

### 4.2 Not verified

| # | Artefact or group | Computed when and where (evidence) | Verified? | Feeds | Proposed re-check (cheapest exact route; rough compute) |
|---|---|---|---|---|---|
| W1-1 | D42 p values, the remainder of `5986316b5`: `results/grid-2026-08-18/{grid_analysis,verifier_analysis,incumbents_common_footprint}.json`, `results/stride-2026-08-25/stride_verifier_analysis.json` (4) | 2026-10-05T07:15Z, three hours after the first kernel report; saross; "Generated on sapphire from 7aef6d2ff" | No. Points carried from clean-boot files; only the p fields are new. **2026-10-14: VERIFIED** (S164 record) | Signed rows `grid-tilesize-overlap-2026-08-18`, `grid-postverifier-2026-08-18`; stride findings; p quotes in findings (`0926e5627`) | Re-run those steps of `reports/d42-implementation-2026-10-05-scripts/d42_regen.sh` at `7aef6d2ff` in a clone; compare the p fields exactly; minutes |
| W1-2 | Retest phase annotations: `results/retest/phase*-evaluation.json` (9 files, 61 `permutation_retest` rows) | 2026-10-05T07:15Z; saross (`5f02cfbc2`) | No (census "unclassified"). **2026-10-14: VERIFIED** (S164 record) | Register rows `phase3a-consensus-calibration`, `phase3a-replication-thinking-calibration`, `e43-matched-temperature`; D42 report ("4 of 61 rows lose significance") | Re-run `retest_annotate.py` on the March files; compare the blocks; minutes |
| W1-3 | February 60-tile re-test: `results/d42-retest-2026-10-05/feb-60-tile/*.json` and summary (11) | 2026-10-05T07:16Z; saross (`35f9814d7`) | Partly: per-condition F1 reproduces the archived reports exactly (2a, 2b, 2e) or to 8e-5 (2c, 2d), per the commit body; p not. **2026-10-14: VERIFIED** (S164 record) | D42 report (four contrasts significant after BH) | Re-run the February step of `d42_regen.sh` on a fresh copy; minutes |
| W1-4 | D42 class B: 16 JSON under `results/d42-retest-2026-10-05/class-b/` and in-place annotations of `fair-384-vs-512`, PV pairwise v1 and v2, Phase 3a HIGH text pairwise | Authored 2026-10-06T06:49Z, "re-run on sapphire" (`e7b32de0b`) | Partly: point estimates checked against the re-run (commit body); p not. **2026-10-14: VERIFIED** (S164 record) | D43, D44 (B-17 p 0.0047, re-sweep 0.0067; I4 p 0.007; E39 F1 0.7701, p 0.0111; one raw-alpha flip to 0.0527) | Re-run `scripts/annotate_classb_permutation.py` and the class B runner; minutes to tens of minutes |
| W1-5 | W2.7 / W7.6 floors (29 files under `reports/w27-replicate-floors-2026-10-06-scripts/`): § 6 `subset_cells.json`, `subset_pairs.csv`; gold-standard consensus floors; floors-v2 derived outputs (`floors55_all.csv`, `nested_*`, `extrapolation55.csv`, `propensity55.csv`, `cell_sds.csv`, `gs_*`, `results.json`); `vdate-results*.json`; `runA/runA_results.json` | 2026-10-06/07 on sapphire (report changelog: "Compute on sapphire"; "they ran on sapphire with /tmp/vdate/") | Partly: 462 of 466 § 6 cells and 839 of 865 pair rows equal Phase 4's BEFORE; the other 4 cells and 26 rows are attributed to D50, not proven; G3 arm 2 floors equal `floors55_all.csv` on 20 rows (S4). **2026-10-14: DONE** (D65; PR #38, `446171b97`; residue in the S164 record) | D45–D48; § 7 claims-inventory verdicts on configuration-level claims | D60 (4) already regenerates § 6 and § 6b in Phase 5. Add: an OLD-scorer (`b3c52591d`) replay of § 6 that must reproduce the committed files exactly, then the floors-v2 analysis and the GS run from verified inputs; about 25 min on 16 workers plus 7.5 min on 20 (the report's timings) |
| W1-6 | Run A (verifier date): `outputs/verifier-date-2026-10-07/` (16) | 2026-10-07T05:26Z; saross (`f13f7b308`) | No | D48; W2.7 § 6c | Re-parse probabilities from the committed batch results; re-run `runA_score.py`; minutes |
| W1-7 | Temperature probe: `outputs/temperature-probe-2026-10-07/` (36) | 2026-10-07; saross (`a79e960f4`, `9f19110b0`); commands "sapphire" in `planning/temperature-probe-2026-10-07.md` | No | "Gemini 3.7 ignores temperature; no residual effect" (continuity; planning card §§ 7, 8.5) | Re-derive the summaries from the committed raw JSONL; seconds to minutes |
| W1-8 | Run B inputs: `outputs/modality-bridge-2026-10-07/` (331: Stage 1 passes, deduplicated passes, unions, crop manifests, Stage 2 probabilities and metas, repaired copies) | 2026-10-07T18:05Z – 22:03Z; saross | No. Phase 4 reproduced the scoring of these inputs, not the inputs. **2026-10-14: VERIFIED** for the 100 checkable files; 212 raw API outputs NOT CHECKABLE (S164 record) | Run B findings §§ 4, 7, 9; D53; D56 | Rebuild unions and deduplication with `scripts/check_union_provenance.py` (it ran at verifier launch; read its logs first); re-parse probabilities from committed batch results; re-run the cost audits; minutes to an hour. API responses themselves are not re-checkable without spend |
| W1-9 | Run C legs (222 files) and `run-c-cost-audit.json` | 2026-10-08T09:58Z – 10:42Z; saross | Verifier SDs yes (Phase 4); legs and cost audit no | D56 (US$25.3176; per-cell SDs) | Re-parse; re-run the cost audit; minutes |
| W1-10 | Q4 re-verified rows: `*_repaired/` under `outputs/gemini3-image-55map-2026-09-16/` and `outputs/gemini37-image-55map-2026-09-13/` (20) | 2026-10-08T10:53Z – 11:02Z; `~/scratch/q4-rescore-2026-10-08` and `q4-tools` on sapphire (10:59Z – 11:33Z) | Deltas yes (agreement); the 7 re-sent and 2 re-booked rows no | D55 Q4; PR #28 readers | Re-parse the rows from the committed batch-result JSONL; seconds |
| W1-11 | Scorer-frames measurement and the `source_tile` gap (16 files under `reports/scorer-frames-d50-d51-2026-10-08-scripts/`) | 2026-10-07T12:27Z – 14:06Z and 2026-10-08T08:54Z – 11:25Z; sapphire scratch; report says so | Partly: the 737 Phase 2 cells match PR #29 at the gated points (6,210 values); the D51 ladder agrees (§ 4.1). Counts such as 707 and 696 cells are not re-derived | D50, D51, D57 rulings; `rescore_b.jsonl` | Low priority: superseded by PR #29 and by Phase 6. Re-run only if a count is re-used in the paper |
| W1-12 | Frames blast-radius (14) | 2026-10-07T06:38Z – 07:21Z; report: "All computation ran on sapphire" | No | D50 (70 cells; 3 registered conditions move) | Low priority; superseded in value by PR #29 |
| W1-13 | Register projections: `results/analyses-manifest.json` (`c117cd012`), `results/runs-manifest.json` (`0a08eedc9`), `results/passes-manifest.json` (`e5f702d2c`), `results/run-conditions.json` and `results/manipulation-gate-bindings.json` (`20e0be0d3`), `results/run-analyses.json` (`69df3b5d4`), the union-sweep JSON (`da86896c4`) | 2026-10-05 to 10-08; the first two saross (sapphire); the rest committed from amd-tower (`+1100`), where they were built is not recorded | No. **2026-10-14: VERIFIED** (S164 record; the authored inputs validated) | Every register row; R0-06, R0-08, R0-09, R2-01, R2-12 to R2-14 | Run each builder's `--check` on the fixed machine; seconds |
| W1-14 | Uncommitted W1 values quoted in records and rulings: Phase 3's NEW values (S3 record, 2026-10-09 12:29Z – 13:54Z, during the burst of crashes: h13 A − B p 0.0237, H3 0.4294, e43 p values, null-exemplar Tier 1 4 → 5, uplift 0.2014 → 0.1632); S4 flag 2's W2.7 deltas; D60 (1)'s Stage A for 13 unpinned cells | Sapphire scratch, `~/scratch/d57-4-rescore-2026-10-09/phase3-out/` and `q4-repaired-readers-2026-10-09/` | No (D60 (1) already requires a byte match) | D60, D61 | No extra compute: when the Phases 3 to 5 PR regenerates them on the fixed machine, require equality with the S3 and S4 records' values |

Lower-weight W1 items, not tabled: the retest-bootstrap (W2) and Phase 2e
ordering (W3) investigations of 2026-10-05 (both straddle the W1 start;
see § 7), the rest of the k-ladder frames note (`76e1af87a`), and 68 prose documents
that quote the groups above.

## 5. Window 2: 2026-09-05T06:58Z to 2026-10-05T04:14Z (lower risk)

### 5.1 Already verified (subtracted)

| Artefact or group | Verified by |
|---|---|
| 835 evaluation cells scored in W2 (809 replayed, 26 byte-diff), across every campaign below | Census, exact (whole `summary` and every `per_run` block) |
| Gemini 3 image 55-map row: cells, `sweeps.json`, `sweep_*.csv`, GS calibration, inheritance ladder and tests; image 2×2 tests K1, K5, and `tests_t5m_K3.json`; 3.7 K = 5 arm 1 replicate (cells, sweeps, tests, agreement); tile-presence leaderboard and frontier | Phase 4 BEFORE against committed: identical, or differing only in metadata keys |
| Era-2 GS board: `tiering_20m.json`, both MCB artefacts, gates, membership | In-window repeat runs: the 2026-09-13 rebuild reproduced the F1 arm and F1 MCB byte for byte (`b3c56a221`), and the 2026-09-14 rebuild reproduced both arms and both MCB files (`60b07ffcc`) |
| h6 A-07, `tile_size_sweep.json`, `verifier-uplift.csv` and `-mcc.csv`, null-exemplar manifest, signature, swap, reduced tiering, MCB, and `analysis.json` | Phase 3 OLD reruns, 0 differing leaves |
| Stride55 sweeps and ladders | S2: OLD reproduces byte for byte (and PR #29) |
| `stride55-2026-08-27/.../n5-companion` corrected F1 | Equals `ladder.json` (clean boot) to ten decimals (`22353e660` body) |

### 5.2 Not verified

| # | Artefact or group | Computed when and where (evidence) | Verified? | Feeds | Proposed re-check (cheapest exact route; rough compute) |
|---|---|---|---|---|---|
| W2-1 | **Gemini 3.7 image 55-map statistics**: the five-test family `tests_IMG-ARM2-K3-carried.json`; sweeps `sweep_IMG-ARM*-K*.csv`; arm 2 K = 5 replicate `tests.json`, `agreement.json`, `sweeps.json`; inheritance `ladder.json`, `tests.json`, `union_separation.json` (61 files with materialised cells) | 2026-09-14 to 09-20; saross (`392a06933`, `e0f9a4d03`, `8d800f2d6`, `0569b0d2f`, `62b13e6fd`, `3fc3f0751`, `2ba1914b6`); `7351bcce8` from amd-tower | No (cells yes, census). **2026-10-14: VERIFIED** (S164 record) | Signed `gemini37-image-55map-2026-09-13` and `-k5-replicate-2x2-2026-09-20`; **D53** (P3: 0.9199 against 0.8848, +0.0351, BH p < 0.0001; ladder 0.8719 / 0.9199 / 0.9270) | Re-run the test family and replicate/inheritance tests at their commits (10,000 permutations, seed 42) and the sweeps from committed probabilities; compare exactly; minutes to tens of minutes |
| W2-2 | **55-map r2 boards**: `final_board_50m.json` (+ `.md`), `55map_leaderboard_50m_r2.json` (+ `.md`), `55map-mcc-tiering-r2.json` (+ `.md`) | Tiering 2026-09-07T04:29Z, "sapphire, $0" (`22353e660`, saross); rows added on sapphire 2026-09-20 (`de009ed5d`, `892633660`); cost fields 10-04/05 (`927d99ced`, `61870d9e7`, `b044c486e`, amd-tower) | No: cell values come from census-verified evaluations; tiers and p values do not. **2026-10-14: VERIFIED** (S164 record) | Signed `55map-final-board-r2-2026-09-06`, `55map-r2-leaderboard-50m`, `55map-r2-leaderboard-mcc-50m`; R0-02, R1-11, R6-06, R6-12, R6-14, R7.1-01/-04/-05/-06/-10/-12/-13, R7.2-02/-17/-18/-23; the headline 0.8827 / 0.8871; D53's text P and R | (a) Cross-read each board cell's F1 and MCC against its verified `evaluation.json` (read-only, seconds); (b) rebuild the three boards at `22353e660` (`final_board_build.py`, `build_55map_leaderboard.py`, `mcc_tiering_55map.py`, `--reference r2`) and compare tiering exactly; tens of minutes (not recorded) |
| W2-3 | K-ladder: Phase 2 verifier stages, unions, carried-point derivations, tier E, MCB sets, MCC test, ladder tables (547 files, 170 of them materialised cells) | 2026-09-12/13, "executed on sapphire" (`326181bcd`), unions "on sapphire" (`e3232d65b`), MCB "all compute on sapphire" (`b7e2821ba`); ladder tables regenerated on sapphire 2026-10-04 (`0f484491c`, `2e0c2941d`, `32d0c6445`) | Cells yes (105 replayed, 3 byte-diff); MCB gated against the committed ranking within 4.958e-05 (a tolerance, not exact); rest no | Signed `k-ladder-2026-09-12`; R1b-17, R3-10 to R3-15, R6-11, R6-14 to R6-18; frontier costs | `check_union_provenance.py` on the 28 unions; tiering and MCB at their commits (seed 42) compared exactly; table builders' `--check`; about an hour (estimate). Phase 6 recomputes the 3.7 ladders anyway |
| W2-4 | Tile-MCC re-sweeps of 23 families and the carried-analogue and MCC-oracle cells on the r2 board (52 files) | 2026-09-20; saross, "on sapphire, 20 workers, 51 min" (`a1c4bf2c3`) and "50 min" (`03b8496ed`) | Cells yes; sweeps no | D6, D6a ("every family's tile-MCC argmax at the lowest vote count"), D6c; tile-presence presentation | Re-run the sweeps; about 100 min on 20 workers (recorded) |
| W2-5 | Uplift supplement: flatten `conditions.csv`, `conditions-by-buffer.csv`, `strata.csv`, `column-spec.json`; verifier-pairing engine summaries; twin materialisations (177) | 2026-09-08 to 09-12; twins "scored on sapphire" (`d23596c78`), saross (`51392bc59`) | Partly: the flatten's OLD rerun differs only through 66 later registrations and `cost_usd` (S3 stopped line) | Signed `uplift-supplement-flatten`; the paper's 55-map uplift | Fold into D61 (5): replay the flatten at `741a4eaff` and require an exact match; re-materialise twins and byte-compare; minutes |
| W2-6 | Era-2 board extras: optimism sweeps (`3097e9bbe`), opmax re-materialisations (`2c3132edc`) and staleness re-sweep (`fe84765d8`), admission scoring (`7ea38de6e`) (65) | 2026-09-10 to 09-12; `fe84765d8` and `7ea38de6e` name sapphire; the others record no host | No | R4-25 (optimism); signed `gs-era2-verified-board-2026-09-10` | Re-run the optimism sweeps; minutes. Phase 6 rebuilds the board (S3 flag 5) |
| W2-7 | Modality-track audit recomputation (`recomputation.json`, recomputed tile-size and working-precision files) | 2026-09-13T23:48Z, "Run on sapphire" (`d5eaeb1ee`) | No | R2-06 (image-bearing tile MCC 0.0665 to 0.291); E88 amendments (`70b47979a`); R0-04, R1-01, R1-02, R1-06 via `gs-plateau-characterisation` | Re-run the recomputation; minutes |
| W2-8 | E70 bootstrap interval re-run: `results/all-bootstrap-cis.json` (85 entries), `ci-metadata-registry.md` | 2026-09-12, "37.6 s wall on 16 workers on sapphire" (`8c89ccebb`) | No | The interval registry the paper cites from | Re-run; under a minute |
| W2-9 | h6 A-06 and A-09 (`a06_decision_rule.json`, `a09_cost_gate.json`) | 2026-09-08T13:01Z; saross (`cd8dc5591`) | Partly: Phase 3's OLD rerun differs from A-06 only in its 28 p-method fields and from A-09 only in 18 cost fields. **2026-10-14: DONE** (D65; PR #35, `3a5e5c453`) | Signed `h6-a06-decision-rule`, `h6-a09-cost-gate` | Already superseded by D61 (3) and D61 (4); require the regenerated non-p and non-cost fields to equal the committed ones |
| W2-10 | Rulings 2 and 3a re-scores: Track-2 engine outputs under `results/stride55-rescore-2026-09-07/` (19) | 2026-09-07T04:42Z, "sapphire, $0" (`26cc430ad`, saross) | No (not evaluation cells) | Stride rows' evidence homes | Re-run the engine (B = 10,000, seed 42); minutes |
| W2-11 | Inputs written on sapphire: r2 sweep materialisations (`7894b5b5a`, 31), union rebuilds (`e9d1db0d0`, `f8e0eb600`), recovery verifier stages and consensus rebuilds of 2026-09-08 (`43516df9a` and four others), and the API outputs of the image campaigns (227 files) | 2026-09-07 to 09-20; saross or bodies naming sapphire | No: the census verifies scoring given these files, not the files. **2026-10-14: VERIFIED** for every checkable file; raw API outputs NOT CHECKABLE (S164 record) | Every cell built on them | Unions: `check_union_provenance.py`; materialisations and consensus: rebuild and byte-compare (seconds each); API outputs: re-parse from committed per-chunk results where kept (`21d1b497d`), otherwise not without spend |
| W2-12 | Image 2×2 `tests_2x2_K3.json` | 2026-09-19T14:11Z; saross (`ed3861cac`) | Almost: Phase 4's re-run differs only in two null-distribution fields, about 1e-14 relative, too small for a bit-34 flip | The declared primary 2×2 family | Re-run at `ed3861cac`; seconds |
| W2-13 | Smaller sapphire items: tile-join audit (`3d6b47e33`), June image pool grid (`4ac321a79`), union-staleness retrospective (`30609d5c8`), cost and frontier regenerations (`61870d9e7`, `6fc63546e`, `7c9499846`) | 2026-09-12 to 10-05; bodies name sapphire, or saross | No. **2026-10-14: VERIFIED** (S164 record) | PI ruling 6 (tile join); the June-pool note; R6-01 (`pareto_v2.json`); frontier costs | Each a re-run or `--check` of minutes or less |
| W2-14 | Tile-join-withheld cells: 21 unregistered uplift cells (2026-09-07/08) and 2 registered k-ladder cells (2026-09-12) | Sapphire scoring runs of those dates | Partly: F1, P, R, and detections reproduce; the intervals and MCC were withdrawn by later code | `k-ladder-2026-09-12`, `null-exemplar-sensitivity-2026-09-13` (2 cells) | Replay at their recorded scoring commits (`26cc430ad`, `c1d6424b7`, `f724b7a10`); minutes |

Not tabled as computations: the cluster and empty-tile audits and the r2
reference instructions of 2026-09-05/06 (PI verdicts; the reference was
materialised in `40361b26f` from amd-tower), and 193 prose documents.

## 6. Window 3: the boot of 2026-01-29 to 2026-05-06

### 6.1 2026-05-06 (high risk): nothing found

No committed artefact was computed on sapphire that day. The last login of
that boot was 2026-05-03T21:42:49Z (`systemd-logind`); the PI was
travelling and sapphire was unreachable (`ede5f80b9`: "sapphire
unreachable during user travel"); the day's eight data commits
(`6683952ac` to `38892df97`, 08:38Z to 09:42Z) ran on zbook ("re-extracted
locally", offset `+0800`). The 36 reports name no `python` process. The
sapphire-side Tier-2/3 clean-up, run 2026-05-03 15:19Z to 15:28Z, was
archived unused (`a19918ccb`).

### 6.2 The rest of the boot (lower risk)

The compute-on-sapphire rule dates from 2026-03-24 (`d0580d0ad`); work
before it was probably local.

| # | Artefact or group | Computed when and where (evidence) | Verified? | Feeds | Proposed re-check |
|---|---|---|---|---|---|
| W3-1 | `results/pairwise/` (726 files: 32 hypothesis comparisons at two buffers, the leaderboard round robin of 300 and later 325 pairs, and the 61-test lever analysis; 10,000 tile swaps each) | 2026-03-28 to 03-31; no host recorded; the same day's sapphire evaluation scripts (`f903f4ac6`) make sapphire likely | Partly: Phase 3 reproduced four group-1 H2 files and the e45 H2 rerun; two group-1 files do not reproduce (D61 (2)) | H2 and other H-series contrasts; the five-factor lever analysis; the e43 board | Extend D61 (2)'s replay of the 2026-03-28 code to every comparison and compare byte for byte, before D60 (3)'s re-run; 1 to 3 h (estimate) |
| W3-2 | `results/h11-384-pv-diagnostic/` threshold sweeps (335) | 2026-03-22 to 03-28; `scripts/sapphire-final-sweeps.sh`, `sapphire-pro-verifier-analysis.sh` (`f903f4ac6`) | No (the cells were re-scored since and are verified) | Operating points of the `pv-diag-384` conditions | Replay the sweeps at their commits; tens of minutes |
| W3-3 | `results/paper-eval/` tables (145), the N = 10,000 and BCa migrations (2026-04-28 to 04-30, saross) | `scripts/sapphire-paper-eval.sh` (2026-03-28); MCC 2026-04-22 | Cells mostly verified (census and vintage replays); the rest no | Paper tables of the March era | Replay at commits; minutes each |
| W3-4 | 55-map analyses run by saross 2026-04-26 to 05-03: `55maps-pairwise-permutation-v2` (66 JSON), attractor pull v2, FP classification, per-map shell variance, TP localisation, text-high t0.3 and t0.7 recoveries, GS subtype | Sapphire (saross) | No | r1-era 55-map findings | Replay at commits; tens of minutes |
| W3-5 | Verifier calibration matrix and its pairwise tiers (44) | 2026-04-25 and 05-03; saross | No | Verifier calibration findings | Replay; minutes |
| W3-6 | Two 55-map t0.3 evaluations (`outputs/55maps-text-high-t0.3-generalisation/{evaluation,extended-buffer-eval}`) | Scored 2026-04-27; saross (`291715b4b`, `548604d95`) | Partly: points and MCC reproduce; 28 and 30 interval values do not; the difference is deterministic but unattributed (census) | Unregistered | Replay at `291715b4b` on the fixed machine; seconds |
| W3-7 | API outputs and consensus layers under `outputs/` (about 4,700 files: retest, h11, h8-v2, h10, h12-v2, 55-map runs) | Mixed hosts | No | Inputs to everything later | Consensus layers: rebuild and compare; API responses: not without spend |

## 7. Items I could not date or place

1. `estimated-correction-r2` and `student-baseline-r2` (`42dbc1147`,
   `81c1f3fff`, 2026-09-07; Monte Carlo, 10,000 draws, seed 42): no host
   recorded; the sibling step 5 ran "local". Seconds to re-run anywhere.
2. Era-2 optimism sweeps and opmax re-materialisations (`3097e9bbe`,
   `2c3132edc`, 2026-09-10), and the null-exemplar overlap tile sets
   (`7e0680183`, `48dec436c`, `0dd95b2d3`, 2026-09-13): no host recorded.
3. K-ladder carried-point derivations and tier E (`9457b2689`,
   `98e54baf6`, `5167b9a5c`, 2026-09-12): the last two carry `+0000`
   offsets under the name Shawn Ross, which suggests sapphire; not stated.
4. The 3.7 image GS calibration (`30e36bcd1`) and five MCC-oracle commits
   of 2026-09-20 by Shawn Ross (`681b4e246`, `cc6d9537f`, `2645e499c`,
   `98d29af39`, `67e7b8a12`); their evaluations are census-verified.
5. The 2026-09-08 consensus rebuilds (`185681674`, `e01b8617a`,
   `c053f5a41`, `e7ebc1695`).
6. The retest-bootstrap check (`238606a15`, sapphire `/tmp/w2/`) and the
   Phase 2e ordering check (`ccf9c613d`; R2-02's anchor): both ran around
   the first kernel report (04:14:24Z), committed 04:56Z and 04:21Z. The
   Phase 2e result is per-tile counts, spot-checked in session.
7. The board's cost increments (`b044c486e`, `final_board_cost_refresh.py
   --write`, offset `+1100`): probably amd-tower; not stated.
8. W3: `results/pairwise/` (likely sapphire), and the April analyses
   `cross-hypothesis-library`, `h10` (signed `h10-pool-size`), `h12-v2`,
   `e47-propose-brief`, and `inter-pass-agreement`: no host recorded.

## 8. Suggested order

1. W2-1 and W2-2: the 3.7 image test family behind D53 and the r2 boards
   behind the headline. Small compute, highest claim weight.
2. W1-1 to W1-5: the D42 p values on signed rows, then W2.7 folded into
   Phase 5.
3. W2-3, W2-4, W2-7, and W2-8, then the `--check` items (W1-13, W2-13).
4. Inputs (W1-8, W2-11) through the existing provenance and rebuild tools.
5. W3-1 folded into D61 (2) and D60 (3); the rest of W3 as capacity allows.

## Overnight evidence (2026-10-12/13), to fold into the rows after review

The overnight agents' draft PRs reproduced several listed items. Each entry names the rows it
bears on; no row above is ticked until the PI has read the evidence. All of it ran on sapphire
after the memory fix, with a kernel-log tripwire that recorded no new error, and every
committed artefact was produced twice and compared byte for byte.

- **W1-5 (W2.7 floors)**, draft PR #38: the § 6 cell, pair, and gate files equal Phase 4's
  2026-10-09 runs byte for byte; the rebuilt `FastScorer` reproduces the live scorer on all 466
  § 6 cells and 1,000 sampled § 6b cells, so the 4 moved cells and 26 pair rows are the D50
  scorer; § 6b regenerated, with a seeded 10 % rebuilt independently and byte-identical. The
  § 3 gold-standard floors were not regenerated (its 486 coincident cells reproduce).
- **W1-14 (uncommitted W1 values)**: the 13 Stage A cells reproduce the 2026-10-09 preview byte
  for byte (draft PR #36); Phase 3's H2 26-of-30 value 0.816471 is reproduced by the fixed
  route (draft PR #37); A-06's permutation p values (0, 0.0019, 0, 0.0002) and the tier-0
  interval change are reproduced (draft PR #35); the S4 flag 2 W2.7 deltas are reproduced
  (draft PR #38). Other Phase 3 NEW values are not yet reproduced.
- **W2-9 (h6 A-06 and A-09)**: both regenerated twice, byte-identical apart from timestamps,
  on draft PR #35; the committed files are superseded once it merges.
- **W3-1 (`results/pairwise/`)**, draft PR #37: today's unfixed code reproduces 30 of the 32
  hypothesis comparisons exactly; the other two share the single-pass arm whose inputs changed
  before tracking (D61 (2) outcome). The leaderboard round robin was not checked file by file.
- **W1-1 and stride outputs**, draft PR #39: re-running every consumer of `per_map_counts()`
  reproduced each committed output byte for byte (stride sweep, full ladder, ladder pairs,
  A5 against B5, Gemini 3.7 sweep, grid board; its inventory names the files); which of W1-1's
  files that covers is to be checked against the inventory before ticking.

## Changelog

### 2026-10-14 — D62 (7) re-check verdicts

PI ruling D65, item D62 (7), re-checked the rows below on the fixed
sapphire by exact reproduction at each file's generating commit, with no
API call. Record: `reports/s164-agent-records/fault-window-rechecks.md`;
drivers and comparisons in `reports/s164-agent-records/fault-window-rechecks-scripts/`.
The dated mark in each row's "Verified?" cell is the only change to the
tables; nothing else in them was rewritten. No unexplained difference was
found, and the kernel's "Bad page state" count stayed 0 before and after.

| Row | Verdict (2026-10-14) |
|---|---|
| W2-1 | VERIFIED: byte for byte; two replicate `tests.json` field for field (key order follows the hash seed) |
| W2-2 | VERIFIED: the three boards byte for byte at `22353e660` |
| W1-1 | VERIFIED: byte for byte after `generated_at_utc` |
| W1-2 | VERIFIED: byte for byte |
| W1-3 | VERIFIED: byte for byte after timestamp and study path |
| W1-4 | VERIFIED: annotated files byte for byte; re-run records field for field |
| W1-5 | DONE (D65), on PR #38 (`446171b97`); five W1 files outside its regeneration listed in the record |
| W1-13 | VERIFIED: manifests byte for byte; union sweep field for field; authored inputs validated |
| W2-9 | DONE (D65), on PR #35 (`3a5e5c453`) |
| W2-13 | VERIFIED: all six commits |
| W1-8 | VERIFIED for 100 checkable files; 212 raw API outputs NOT CHECKABLE |
| W2-11 | VERIFIED for every checkable file; raw API outputs NOT CHECKABLE |

Not re-checked, outside D62 (7)'s limit: W1-6, W1-7, W1-9 to W1-12,
W1-14, W2-3 to W2-8, W2-10, W2-12, W2-14, and W3.

### 2026-10-13 (later) — Overnight reproduction evidence

Added § Overnight evidence, pointing rows W1-1, W1-5, W1-14, W2-9, and W3-1 at the overnight
draft PRs #35–#39 that reproduce them in part. No row's status changed.

### 2026-10-13 — Original publication

The overnight read-only listing for the fault-window re-check, before any
re-run, for the PI to read first.
