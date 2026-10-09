# D57 (4) re-score: plan card (phase 1 of 6)

**Status:** plan for PI review, 2026-10-09. Nothing has been run or changed.
Written by a read-only planning agent (Claude Opus, S163) at local
`fefb73f2b`, plus read-only `ls`, `cat`, and `git log` on sapphire (also at
`fefb73f2b`, on `main`, with no modified tracked files and 122 untracked
entries). Spot-checked at source by the session before saving: the 762 rows
of `moved_new.csv`; Run B's union properties (`source_tile` and
`vote_count` only); `docs/methodology/signature-policy.md:90`; the sweep
writers at `scripts/derive_g37_gs_opmax_rungs.py:231–236`; the empty
null-exemplar `detections/` on sapphire (only `.gitignore`).

**Authority:** D57 (4), `planning/pi-decisions-2026-09-20.md:87`: "The
re-score is approved as one tracked step (report § 6, plus Run B and Run C
re-scored together); ladder files wait for (3)."

**Scorer under test (NEW):** `8988f3f17`, which is `origin/main`. Locally
the object exists, but the local branch is still at `fefb73f2b`. PR #27
touches four files: `lib_advanced_metrics.py`, `evaluate_detections.py`,
the scorer-frames report (+5 lines before § 6, so § 6 starts at line 538
there and at 533 locally), and `tests/test_detection_scope.py`.

**Scorer for the differential (OLD):** `b3c52591d`, the first parent of
`fefb73f2b` (`main` just before PR #26).

**Expected values:** `~/scratch/source-tile-gap-2026-10-08/out/rescore_b.jsonl`
on sapphire (2,800 rows; rule b is the draft fix PR #27 applied unchanged).
It is equal to `rescore_a.jsonl` and to § 4.1's NEW values to 1e-9 (report
§ 5.7). The tracked summary is
`reports/scorer-frames-d50-d51-2026-10-08-scripts/out/summary/moved_new.csv`:
762 rows, OFF and NEW F1 at 20 m and 50 m.

---

## 0. Findings that change the brief

1. **Run B and Run C will probably not move.** This contradicts the
   continuity note's expectation (`planning/paper-writeup-continuity.md:116–121`).
   - Origin restoration needs an origin column. The Run B unions carry only
     `source_tile` and `vote_count`. Checked:
     `outputs/grid-2026-08-18/verifier/g384_ov192/union_k10.geojson`,
     `outputs/modality-bridge-2026-10-07/g3-text/verifier/detect_brief-text/union_k10.geojson`,
     and `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/union_k5.geojson`.
   - The committed verified sets carry `vote_count`, `source_tile`, and
     `mound_probability` (e.g.
     `results/modality-bridge-2026-10-07/g3-text-g3v/verified_best_20m.geojson`).
   - The floors' rungs are bare centroids (`modality_bridge_floors.build_rung`,
     which assigns tiles by the legacy rule when no origin is given).
   - The scoring frame is grid-common (`stride_verifier_analysis.COMMON_BOUNDS`),
     and the unions are clipped to it.
   - This is a prediction. Phase 4 confirms it with gate-only runs.
2. **Input drift affects 26 of the 762 moved cells.** Their detection file's
   feature count no longer equals the recorded `n_detections`. None of them
   is a registered condition.
   - The 26 are: 12 pinned by `_metadata.e82_input_vintage`; 11
     pre-recovery records under `results/rescore-2026-05-31/` (5 e47
     consensus, 6 n1-outstanding Pro HIGH T 0); 2 waived `h12-v2` cells;
     and 1 archived 3.7 K = 3 copy.
   - § 5 measured OFF and NEW on today's inputs, not on the inputs these
     cells were scored against. Example:
     `results/rescore-2026-06-05/pv-diag-384/consensus-sweep/flash-high-image-n5__image-t0.0__consensus__t1`
     reads 0.4883 committed (802 detections, vintage `2e8cc6481`). Today's
     file has 889 features, and § 5 gives 0.4969 → 0.4984.
   - A naive replay would mix drift with D50.
3. **The 49 null-exemplar twins have no inputs on disk.** Their inputs are
   gitignored, and `results/null-exemplar-sensitivity-2026-09-13/detections/`
   is empty on sapphire. They must be rebuilt first (`--stage filter`).
4. **The ten gold-standard sweeps of § 4.2 belong in the ladder phase.** They
   are written only by the D51-gated ladder drivers:
   - `derive_g37_gs_opmax_rungs.py:231–236` writes `sweep_2d_era2b.json` and
     `sweep_2d.json`;
   - `run_k_ladder_tier_e.py:1141–1146` writes `sweep_board.json`;
   - `score_k_ladder_phase2_rungs.py:394–395`.

   Those drivers rewrite the sweeps clipped. Regenerating them unclipped in
   Phase 2 would be overwritten in Phase 6, so they are planned in Phase 6.
   - Several committed Era-2-frame siblings were never measured by § 4.2:
     tier E `sweep_era2.json` ×4, and 3.7 `verify_k3/sweep_2d.json` and
     `verify_k*_recovery-fixed/sweep_2d.json`.
5. **Many drivers refuse unless they reproduce committed or hard-coded
   values.** This applies to the Run B six-cell anchors, the floors gates
   1–3, the verifier-SD gates 1–3, the e45 gate (1e-6), the family-FDR
   expected p-values, and the stride55 replication gate (1e-6). Hence the
   OLD/NEW differential in § 1 and the strict ordering in Phase 3.
6. **Signatures lapse when numbers move.** `docs/methodology/signature-policy.md:90`
   moves a signature to `re-sign-pending` on "any change to the row's
   numbers". At least six signed analyses consume moved cells (§ 4). Most
   will become `re-sign-pending`.
7. **15 more cells change, but by less than 0.001.** These are 55-map stride
   pairing twins (as-predicted 70 minus 55, `summary_new.json`). They are
   not in `moved_new.csv`; they are in the sapphire jsonl.
8. **The Q4 agent's list of citing documents is not in the repository.** It
   is reconstructed in § 5.2 by `git grep`.

---

## 1. Conventions for every phase

- **Where.** Sapphire, after the PI-approved sync to `8988f3f17`, on a data
  branch (suggested name `d57-4-rescore`).
  - Phases 2–3 run in a detached worktree at `8988f3f17`. Every input they
    need is tracked, except the null-exemplar inputs, which `--stage filter`
    rebuilds there.
  - Phase 4 runs in the main checkout, because it needs untracked inputs:
    - `verify_g3_repaired/` for `g3-text`, `g3-image`, and `g3-text-temp1`
      (confirmed present on sapphire);
    - the deduplicated passes under
      `outputs/modality-bridge-2026-10-07/<arm>/scoring/` (present:
      10/10/5/5/5/5/5).
  - Phase 4 writes only to `--out-dir` scratch.
  - Use `.venv/bin/python` and at most 20 workers (sapphire has 24 cores).
- **OLD/NEW differential for every derived test.** Run each driver twice
  into scratch:
  - from a `git archive` of `b3c52591d`, which must reproduce the committed
    artefact exactly;
  - from `8988f3f17`, which gives the "after".

  Only NEW outputs are copied into the tree. Copying happens after the PI
  has seen the deltas.
- **One scorer version.** Inside each phase, nothing under `scripts/` is
  committed except Phase 4's Q4 change. Each phase's run log records the
  blob SHAs of the scorer modules: `lib_advanced_metrics.py`,
  `evaluate_detections.py`, `lib_assessed_area.py`,
  `prepare_h13_scoring.py`, and `lib_permutation.py`.
  - Gate: `git diff --quiet 8988f3f17 <every commit named in a regenerated
    _metadata.script_git_commit> -- <those files>`.
- **Recipes are replayed as recorded.** Keep each cell's recorded
  bootstrap; never standardise it. Across the 762 cells: BCa 10,000 seed 42
  ×749; "mixed" ×7; no method recorded ×4; B 1,000 ×2.
- **Stop rule.** Any failed gate, any cell whose NEW differs from
  `rescore_b.jsonl` by more than 1e-9, any `n_origin_switched ≠ 0`, or any
  unexpected file in `git status`: stop and report. Do not patch around it.
- **Order.** Each phase reports before→after deltas to the PI before any
  document is edited (§ 6).

---

## 2. Order, dependencies, wall clock, and stop points

| Phase | Content | Depends on | Wall clock on sapphire (estimate) | Stop for the PI |
|---|---|---|---|---|
| 0 | Sync sapphire and local to `8988f3f17` (PI decision); tier-1 at that head; pre-flight checks (§ 7) | PI | tier-1 about 5 min (278 s at `842f9e92a`, report § 4.3) | after pre-flight |
| 2 | Cells, the stride sweeps, `conditions-manifest` | 0 | Replay of about 737 cells: 7–17 CPU-h, about 0.5–1 h at 20 workers. Scaled from E82's 16–38 CPU-h per 1,655 cells (`planning/e82-corpus-reemission-2026-08-20.md:357`); 55-map cells are heavier. Stride sweeps and manifest under 1 h. | deltas S2 |
| 3 | Statistical tests (OLD + NEW) | 2 (tests read regenerated cells) | 3–6 h. Unmeasured: null-exemplar tiering and the diversity-dividend round robin dominate. | deltas S3 |
| 4 | Run B and Run C together; Q4 adoption | 0; independent of 2–3 | Run B scoring about 1 h (`modality-bridge-2026-10-07-score.sh` header); floors 379.5 s and verifier SD 34.8 s (their `gates.json` meta). Q4 55-map stages 2–6 h (unmeasured; Hungarian matching over 8,541 tiles). | deltas S4 |
| 5 | Documents | S2–S4 approved | — | wording review |
| 6 | Ladder files and their cells and sweeps | D57 (3) review returned and ruled | 1–3 h | deltas S6, then documents |

---

## 3. Phase 2: cells, sweeps, and the conditions manifest

### 3.1 Cells (`moved_new.csv`, partitioned at `fefb73f2b`)

| Group | Cells (registered) | Action | Regenerated by |
|---|---:|---|---|
| Replayable as recorded | 673 (61) | regenerate in place | `scripts/evaluate_detections.py` from each cell's `_metadata.cli_args` (below) |
| Null-exemplar twins (42 Era-1, 7 Era-2) | 49 (0) | rebuild inputs, then replay | `scripts/analyse_null_exemplar_sensitivity.py --stage filter`, then replay as above |
| Changed by less than 0.001 (not in the CSV) | 15 (0) | regenerate (PI Q1) | replay |
| Drift, unpinned | 13 (0) | **hold** (PI Q2) | `reports/input-drift-2026-10-07-scripts/rescore_scored_vintage.py` pattern if replayed |
| Pinned (`e82_input_vintage`) | 12 (0) | **hold** (PI Q2) | vintage-aware replay (`scripts/rerun_bca_corpus.py` machinery) if replayed |
| Ladder directories (`phase2/cells` 3, `tier-e/cells` 4, `recovery-fix-2026-09-13/reproduced-k5-evaluation` 1, whose input is `/home/shawn/scratch/recovery-drop-fix/rescore/k5.geojson`) | 8 (7) | **Phase 6** | the ladder drivers |
| `archive/**` | 7 (0) | leave (PI Q3) | — |

**Command per cell.** Every recorded `cli_args` key is replayed into the
cell's own directory. That rewrites `evaluation.json`, `.csv`, and `.md`;
all 762 cells carry that trio.

```bash
.venv/bin/python scripts/evaluate_detections.py \
  --detections <cli.detections…> | --detections-dir <dir> --glob <glob> \
  --buffers <cli.buffers> --ground-truth <cli.ground_truth> \
  --bounds <cli.bounds> --bootstrap <cli.bootstrap> --seed <cli.seed> \
  --label <cli.label> [--mcc] --output-dir <cell dir> --workers 4 \
  --require-clean-inputs        # omitted for null-exemplar inputs (untracked)
```

The driver is a small new wrapper modelled on `scripts/recovery_reeval.py`
(`protocol_of`, `command`), with an **inverted point gate**. Every F1, P,
and R at every buffer, plus MCC or its refusal, must equal the cell's
`rescore_b.jsonl` NEW value to 1e-9.

The three `gold-standard-v2` consensus conditions have no `eval_path` in
`results/run-conditions.json`. Confirm the generator's lookup resolves them
to the regenerated files.

**Expected moves, NEW − OFF (from `moved_new.csv`):**

| Directory | Cells (registered) | ΔF1@20 | ΔF1@50 |
|---|---:|---|---|
| `results/rescore-2026-06-05` | 241 (25) | +0.0002 to +0.0033 | +0.0002 to +0.0033 |
| `results/phase3a-{text,image}-matrix` | 244 (0) | +0.0002 to +0.0033 | same |
| `results/uplift-supplement` | 54 (1) | +0.0010 to +0.0245 | +0.0011 to +0.0382 |
| `results/null-exemplar-sensitivity-2026-09-13/cells` | 49 (0) | +0.0061 to +0.0349 | +0.0081 to +0.0357 |
| `results/h8-v2`, `h12-v2`, `rescore-2026-05-31`, `recovery-reeval-*`, `deployment-oracle-*`, `paper-eval`, others | 141 (24) | +0.0000 to +0.0034 | up to +0.0027 |
| `results/h13-overlap-2026-08-18/{common,native}/arm*` | 6 (6) | +0.0055 to +0.0155 (common A 0.5580 → 0.5734, B 0.5198 → 0.5300, C 0.4025 → 0.4116) | not scored |
| `results/pairwise/tile-size-30m` (waived, 512 px on the 384 px frame) | 5 (0) | +0.0602 to +0.0689 | not scored |
| `outputs/h11/consensus-384-UNINTENDED-T1.0` | 5 (5) | +0.0014 to +0.0027 | same |

F1@20 rises in every moved cell (report § 5.2). Outside h13, tier E, and
the 3.7 rungs, no registered cell moves by more than 0.0034.

### 3.2 Sweeps in this phase

| Artefact | Command | Expected |
|---|---|---|
| `results/stride55-2026-08-27/{g384_ov128_55map,g384_ov192_55map}/sweep_50m.csv`, `sweep_oracle.json` | `.venv/bin/python scripts/stride55_sweep_oracle.py` (replication gate at each primary point to 1e-6; A-versus-B permutation 10,000, seed 42) | 14 and 16 rows change by more than 1e-9 (2 and 3 by ≥ 0.001), all at prob_t 0.00 or 0.05. Oracles unchanged: (k7, 0.15) 0.8362 and (k9, 0.20) 0.8503 (`stride55_new.json`). No primary point is among the moving rows, so the gate should pass. |
| `results/stride55-2026-08-27/*/ladder_sweep_50m.csv` | `scripts/stride55_ladder.py` (never measured) | scratch re-run and diff first |

### 3.3 Conditions manifest

1. `.venv/bin/python scripts/generate_post_run_report.py --all --dry-run`,
   then a scripted diff.
2. `--all --write`.
3. `--check-renderings`.
4. `.venv/bin/python scripts/verify_run_conditions.py` (the drift check,
   including its feature-count check).

Expected: only the 61 Phase 2 registered rows change (metric blocks and
CIs), plus `conditions-manifest.md`. The other seven move in Phase 6. Then
rebuild the registry with
`.venv/bin/python scripts/build_generated_file_registry.py` and run tier-1.

---

## 4. Phase 3: statistical tests that consume moved cells

Each test runs OLD then NEW into scratch, as in § 1. Every one seeds
`np.random.default_rng(seed)` per call (`lib_permutation.py:215, :423`;
`h13_overlap_analysis.py:202`; `lib_advanced_metrics.py:677` and others).
The tests are therefore deterministic given the same inputs and NumPy, and
the OLD reproduction proves it empirically.

| Test (register row, signature) | Moved inputs | Driver, in order | Iterations and seed | Committed → expected |
|---|---|---|---|---|
| h13 A − B (`h13-overlap-2026-08-18`, signed) | 6 arms | `scripts/h13_overlap_analysis.py --scoring-dir outputs/h13/scoring --output-dir <scratch>` (writes `h13_overlap_analysis.json` and `per_tile_counts.json`); then `h13_k_sensitivity.py`, `h13_aggregation_sweep.py`, and `h13_tilesize_overlap_grid.py`, re-run and diffed (unmeasured) | bootstrap B 1,000 primary and 10,000 sensitivity, percentile, seed 42; tile-swap permutation 10,000, seed 42 | +0.0380 [+0.0009, +0.0708], p 0.0385 → about +0.043 (point, § 5.5). CI and p not predicted. |
| Null-exemplar, Era-1 and Era-2 (`null-exemplar-sensitivity-2026-09-13`, signed) | 49 twins | `analyse_null_exemplar_sensitivity.py --stage signature`, `override`, `swap`, `assemble`; `era1_leaderboard_tiering.py --permute-mcc` (tiering-reduced); `selection_aware_intervals.py --board` (mcb-reduced) | bootstrap 10,000; permutations 10,000; seed 42 | Example: `text-high-t0.3-n10-8of10` reduced − full −0.0245 → −0.0142. "Largest Era-2 movement" 0.0074 → about 0.0068 (frames report § 5.2). |
| H2 input (feeds e45 and FDR) | `pv-diag-384::…-consensus-26of30` (+0.0024) | `scripts/run_pairwise_tests.py --config configs/pairwise-comparisons.yaml --buffer-metres 20 --output-dir <scratch> --filter-group 1` | 10,000, seed 42 | Δ 0.076083, p 0.0 → p expected to stay 0.0. The committed file is dated 2026-03-28, so OLD may expose input drift. |
| H3 input (`diversity-dividend-384`, unsigned) | 4 | `scripts/consensus_vs_baseline_tiering.py --cells planning/diversity-dividend-cells-2026-06-06.json --kinds champion --output-dir <scratch>` | `--n-permutations` default 10,000, seed 42 | not predicted |
| e45 (`e45-bootstrap-pairings`, signed) | via H2 and H3 | `scripts/e45_bootstrap_pairings.py --h2-rerun-json …` (gate 1e-6 against the H2 and H3 files, so it runs after them) | B 1,000 and 10,000, seed 42; permutation 10,000, seed 42 | not predicted |
| Confirmatory BH (`family-bh-fdr-confirmatory`, unsigned) | via H2 and H3 | `scripts/compute_family_fdr.py`; asserts H2 = H3 = 0.0 (`:146–148`) | B 10,000; permutations 10,000; seed 42 | BH family unchanged if H2 and H3 stay at 0.0. Otherwise the gate refuses: PI Q6. |
| `h6-a07-voting-thresholds` (signed) | 6 | `scripts/h6_registered_analyses.py` | `B_DELTA_CI` 1,000, seed 42 | not predicted |
| `e43-matched-temperature` (unsigned) | 7 | `scripts/regen_e43_board.py --execute --output-dir <scratch>` | 10,000 | not predicted |
| `tile-size-sweep` (unsigned) | 8 | `scripts/tile_size_sweep.py --output-dir <scratch>` | — | not predicted |
| `uplift-supplement-flatten` and `verifier-uplift-pairing` (both signed) | 61 rows plus the pairing twins | `scripts/build_uplift_supplement.py`, then `compute_verifier_uplift.py`, then `compute_verifier_uplift.py --metric MCC` | — | F1@50 uplift changes up to −0.0033; MCC up to 0.0003 (frames report § 5.3) |
| `pv-diag-384-consensus-calibration` (unsigned by design) | 27 | none (the sweep is the cells) | — | — |

---

## 5. Phase 4: Run B and Run C together, and the Q4 adoption

### 5.1 Run B and Run C

| Step | Reads | Writes (scratch first) | Committed gates |
|---|---|---|---|
| `scripts/modality_bridge_anchors.py` (called by the next two) | six original unions and probabilities | — | F1 to 1e-3 against hard-coded 0.8961, 0.8412, 0.9139, 0.9265, 0.9254, 0.9308 (`:86–110`) |
| the ten `image_b_analysis.py --six-cell-gate … --out-dir <scratch>/<cell>` lines and the three `gemini37_image_gap_test.py --six-cell-gate` lines of `scripts/modality-bridge-2026-10-07-score.sh`, run directly so the output goes to scratch | unions plus `verify_*_repaired` | `analysis.json`, `sweep_20m.csv`, `verified_*.geojson`, `gap_test.json`, `k5/`, `additions/` | anchors |
| `scripts/modality_bridge_floors.py --scoring-root outputs/modality-bridge-2026-10-07 --workers 20 --out-dir <scratch>/floors` | committed sets and `analysis.json`; the deduplicated passes | `floors.json`, `gates.json`, `gap_change.json`, `date_component.json`, `subset_cells.csv`, `summary.csv` | gate 1 anchors; gate 2 sets against `analysis.json` (1e-3); gate 3 gap tests exact; gate 4 subset machinery. Gap change B 1,000 and permutation 10,000, seed 42. |
| `scripts/modality_bridge_verifier_sd.py --gate-only`, then the full run with `--out-dir <scratch>/verifier-sd` | `floors/{floors,gates,gap_change}.json`, the three replicates (`rep_dir`) | `gates.json`, `verifier_sd.json`, `floors_with_verifier.json`, `summary.csv` | gate 1: replicate 1 equals the committed sets per tile; gate 2: deduplicated-pass SHA-256 against `floors/gates.json`; gate 3: floors re-derive to 1e-12; gate 4: join and `_repaired` |

Consumers: `results/modality-bridge-2026-10-07/findings.md` §§ 2–3 (cells,
gaps), § 5 (gap change), § 6 (date component), § 7 (floors), and § 7a
(Run C).

**One scorer version.** All four steps run in one session at `8988f3f17`.

- The verifier-SD step must read the NEW floors. Point `fl.RESULTS` at the
  scratch floors by running in a scratch tree, or add a `--floors-dir`
  option.
- Never rebuild the deduplicated passes. `write_dedup_geojson` now re-keys
  8–17 points per pass (report § 7 item 5), which would break gate 2's SHA.
  The floors' 2026-10-08 root `/tmp/runb-floors` no longer exists on
  sapphire. The Stage 2 root matched it (verifier-SD gate 2 passed reading
  it).

**Expected result.** Every output is byte-identical to the committed one
except `meta` (`wall_seconds`, `scoring_root`). PI Q9 decides whether that
is recorded as a dated note in the § 7a changelog or as re-committed files.

### 5.2 Q4: prefer `_repaired` where it exists

**Readers of fixed names** (verified by the planning agent):

| Site | What it reads |
|---|---|
| `scripts/gemini37_image_55map_r2.py:580` (`rung_frame`) | `verify_k{k}_{arm}`; serves both campaigns and the inheritance ladder's frames |
| `results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/inheritance_ladder.py:465` | a recorded provenance path |
| `…/replicate-k5-arm1-batch-2026-09-20/replicate_k5_arm1.py:161–170` | `verify_k5_arm1_replicate-batch-2026-09-20` |
| `…/replicate-k5-arm2-batch-2026-09-20/replicate_k5_arm2.py:91–92` | no repaired copy, so this is a no-op |
| `reports/w27-replicate-floors-2026-10-06-scripts/w27_55map_subset_replicates.py:270` | `verify_k5_{a}`, including G3 arm 2 |
| `scripts/build_tile_presence_board.py:163–169` | the legs for cost only |

**Minimal change.** Add one helper:

```python
resolve_verify_dir(vroot, name)
# -> vroot / f"{name}_repaired" if that directory holds probabilities.json,
#    else vroot / name
```

- Use it at the r2 and replicate read sites, and update the inheritance
  provenance string.
- Record the directory read, its SHA-256, and `parse_repair.json` counts in
  each output, as `modality_bridge_verifier_sd.load_replicates` does.
- In the same change, derive `PROJECT_ROOT` from `__file__` in
  `replicate_k5_arm1.py:88`, `replicate_k5_arm2.py:56`, and
  `inheritance_ladder.py:114`.
- Add a tier-1 test.

**Repaired copies** (`outputs/**/verify_*_repaired/parse_repair.json`):

- 3.7 `verify_k5_arm1_replicate-batch-2026-09-20_repaired`: 2 rows changed.
- G3 `verify_k{1,3,5}_arm2_repaired`: 1, 3, and 3 rows. These are
  unrecoverable by parse repair and were re-sent under D55 Q4
  (`reverify-2026-10-08.json`).

**Runs.**

- `replicate_k5_arm1.py --arm arm1 --stage agree`, then `materialise`.
  Commit the detections, because `--require-clean-inputs` applies. Then
  `score --workers 5 --jobs 2`, then `tests`.
- `gemini37_image_55map_r2.py --campaign g3 --stage sweep`, `materialise`,
  `score --cells <arm 2>`, `tests`.
- `inheritance_ladder.py --campaign g3 --stage ladder`, `score`, `tests`.

**Expected moves** (Q4 agent, old scorer):

- `IMG-ARM1-K5-carried-replicate` and `-f1-oracle-replicate`
  (`results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20/cells/`):
  F1 0.9135 → 0.9134, MCC 0.7530 → 0.7527. Drift test (a) tile-MCC
  +0.000145 → −0.000132. Flips 221 → 220.
- G3 arm 2: none of 13 cells (11 under
  `results/gemini3-image-55map-2026-09-16/cells/G3IMG-ARM2-*`, plus 2 under
  inheritance).
- Not yet measured: the G3 `sweeps.json` rows, the W2.7 § 6b G3 arm 2
  subset floors, and the tile-presence leg costs (US$0.007672 of
  re-verification).

These are scorer-invariant: none of the 49 55-map image cells is in
`moved_new.csv`, and the sampled NEW rows show 0 out-of-frame and 0
restored. Re-verify under `8988f3f17` as before (fixed names) and after
(repaired), so the Q4 delta never spans two scorers.

**Citing documents, updated once** (`git grep`; the hand-back list is not in
the repository):

- `…/replicate-k5-arm1-batch-2026-09-20/findings.md` (:199, :201, :254–257);
- `reports/image-2x2-tests-declaration-2026-09-19.md`;
- `reports/google-temperature-notice-2026-10-07.md`;
- both `inheritance-2026-09-20/findings.md`;
- `results/tile-presence-2026-09-21/findings.md`;
- D8 at `planning/pi-decisions-2026-09-20.md:103` (a dated note only);
- `reports/register-repair-2026-10-05-investigations/d31-other-legs.md`;
- `results/run-analyses.json` and the generated `analyses-manifest`.

---

## 6. Phase 5 (documents) and Phase 6 (ladders)

**Phase 5.**

- `results/**.md` and `reports/**.md` get the banner plus a changelog with a
  before→after table and a "what did not change" note
  (`docs/agent-guidance.md:96–106`).
- Generated projections are re-rendered, never hand-edited:
  `evaluation.md`, `conditions-manifest.md`, and
  `tiering-reduced/tiering_20m.md`. So is
  `results/null-exemplar-sensitivity-2026-09-13/findings.md`, via
  `scripts/render_null_exemplar_findings.py` and its `--check`; its
  changelog lives in the template.
- `docs/paper/results-claims-inventory-2026-09-12.md` gets dated notes only
  (D55 Q1).
- Register outcomes in `results/run-analyses.json` change only after PI
  wording; signatures go to `re-sign-pending` with history kept.
- Before editing, run a citing-site census: `git grep` every moved cell's
  directory and its four-decimal OFF values.

**Phase 6** (gated on the D57 (3) review on branch `d51-ladder-provenance`,
`1fc1f72df`, and the PI's ruling).

- Files: `results/k-ladder-2026-09-12/phase2/` (`ladders.json`, tables,
  figure, 3 registered cells); `tier-e/` (`ladder.json`, `scores.json`, 4
  registered cells); `recovery-fix-2026-09-13/`.
- The ten gold-standard sweeps and their unmeasured Era-2-frame siblings.
- Re-registration of the 7 conditions.
- The quoted F1s of the signed Era-2 board (frames report § 5.1).
- Citing sites (§ 6 of the report, re-verified 2026-10-09):
  `results/k-ladder-2026-09-12/findings.md:602, :1573, :1295, :1317, :1338,
  :1408, :1410`; `results/null-exemplar-sensitivity-2026-09-13/findings.md:24,
  :166, :183`; claims inventory `:461` (R3-13).
- Drivers: `score_k_ladder_phase2_rungs.py prepare`,
  `derive_g37_gs_opmax_rungs.py prepare`, `run_k_ladder_tier_e.py prepare`
  (D51 gate, `--clip-to-common-area`; `--allow-undetermined-area` as ruled),
  then `build_k_ladder_phase2_tables.py`.
- Expected ladders:
  - 3.7: 0.8682 / 0.9073 / 0.9066 / 0.9068;
  - tier E: 0.8604 / 0.8902 / 0.8968 / 0.8886 (report §§ 5.3–5.4).

---

## 7. Safety checks before each phase

| Check | How | Preview at `fefb73f2b` (local, read-only) |
|---|---|---|
| **Feature count.** Each detection GeoJSON's feature count must equal the cell's recorded `n_detections` (summary, or per run for multi-pass cells), before and after regeneration. NEW must not change `n_detections`. | A script over the resolved `cli_args`; for null-exemplar inputs, against `detections_manifest.json` after `--stage filter`; `verify_run_conditions.py` for registered rows. | 679 match; **26 mismatch** (§ 0.2, all unregistered); 41 inputs absent (40 null-exemplar, 1 scratch); 16 multi-file or directory (the 6 h13 cells all match per run) |
| **Byte-diff of artefacts that should not move.** | (a) Replay all 383 cells where the scope restored a detection but nothing moved (1,090 − 707, `summary_new.json`), plus 50 random unchanged cells, into scratch. Metric blocks must be identical apart from `detection_scope`, `generated_at_utc`, and `script_git_commit`. (b) `git status` shows no change to any detection, union, `detections_dedup`, crop manifest, or `probabilities.json`. (c) Manifest rows outside the moved set are byte-identical. (d) Stride rows outside the 14 and 16 are byte-identical. (e) The Run B and Run C outputs are byte-identical apart from `meta`. (f) The 55-map image cells read the same before Q4. | — |
| **Every regenerated evaluation carries `detection_scope`** with every `_DETECTION_SCOPE_COUNTS` key, including `n_origin_switched`. | `n_origin_switched == 0` everywhere (§ 5.7). `n_out_of_frame` and `n_origin_restored` must equal `rescore_b.jsonl` `new_scope`. | — |
| **Scorer version** | blob-SHA gate (§ 1) | — |
| **Determinism** | replay one unchanged cell twice; CI blocks must be identical | — |

---

## 8. Risks and open questions for the PI

1. **Q1 Scope.** Regenerate the changed cells that have usable recipes
   (673 + 49 + 15, less the holds), not only the 61 registered ones.
   Recommended, so that no committed file holds a number the scorer no
   longer gives. The 1,950 unchanged cells and the 383 restored-but-unmoved
   cells are left alone.
2. **Q2 The 25 live drifted or pinned cells.** Default: leave them as
   historical records (ruling 3a), noted in the S2 deltas. The alternative
   is a vintage-aware replay, for which no expected values have been
   measured.
3. **Q3 Archive.** Leave all 7 `archive/**` cells.
4. **Q4 In place versus a new home.** Recommend in place, following the E82
   precedent: same inputs, a changed instrument, git as the record.
   `recovery_reeval.py`'s new home plus re-pointing fits changed inputs,
   which is not the case here.
5. **Q5 The 3.7 registered rungs (Phase 6).** Should the condition carry
   the D50 board value (0.8747 / 0.9135 / 0.8616) or the D51-clipped value
   (0.8682 / 0.9073 / 0.8553)? The gated driver clips the materialised
   cells.
6. **Q6 Gates pinned to committed or hard-coded values.** Approve the
   OLD/NEW differential. Where a NEW run must pass a constant (anchors
   `ORIGINAL_CELLS`, family-FDR `expected_value`), approve a dated constant
   update only if NEW actually differs (expected for neither).
7. **Q7 Signature load.** These signed analyses are likely to lapse: h13,
   null-exemplar, e45, h6-a07, uplift-flatten, and verifier-uplift-pairing.
   k-ladder and the Era-2 board lapse in Phase 6.
8. **Q8 Q4 scope.** Should it include the W2.7 § 6b G3 arm 2 floors and the
   tile-presence cost legs?
9. **Q9 Run B and Run C reproduce byte for byte.** Record that as a dated
   § 7a note, or re-commit the files?
10. **Q10 Gold-standard sweeps.** Accept moving the ten sweeps of § 4.2
    (plus the unmeasured Era-2-frame ones) into Phase 6?
11. **Unmeasured derived artefacts** (h13 sub-analyses, stride55 ladder
    sweeps): scratch re-run and diff, reported in the deltas.
12. **Hard-coded roots.** Seven `Path("/home/shawn/Code/map-reader-llm")`
    assignments, as the continuity note says. `git grep` also finds the
    literal path in 48 `.py` and `.sh` files, mostly `cd` or `REPO=` lines
    in older shell drivers. Of the drivers this plan runs, only the three
    Q4 drivers carry one. Fix them before running (§ 5.2), and never run
    them from a scratch copy before the fix.
13. **Shared checkout.** Phase 4 must use sapphire's main checkout, so a
    concurrent session there is a hazard (Obs 353). Confirm no other
    session is active first. Use read-only checks, and never `pgrep -f`
    over ssh.
14. **Not re-read by § 6 itself:** the register outcomes in
    `results/run-analyses.json`, the signed board's README and tiering,
    `results/conditions-manifest.md`, and the uplift CSVs. They are in
    Phase 5's census.
15. **Limits.** The frames report's 49 unscored cells stay unmeasured, and
    its 24 corrected-F1 adapter cells were diagnosed only. Wall-clock
    figures not taken from a recorded log are estimates.
16. **The sync to `8988f3f17` waits on the PI.** Nothing in Phases 2–4 may
    run before it.

## Rulings

RULED 2026-10-09 (S163), D58 in `planning/pi-decisions-2026-09-20.md`.
Every recommendation accepted:

| Q | Ruling |
|---|---|
| Q1 | Every changed cell with a usable recipe |
| Q2 | Two stages where the inputs as scored can be recovered (scorer change first, drift second); otherwise historical records |
| Q3 | Leave the `archive/**` cells |
| Q4 | In place |
| Q5 | Decide at the ladder step |
| Q6 | As recommended |
| Q7 | The six signature lapses accepted |
| Q8 | Yes |
| Q9 | A dated § 7a note |
| Q10 | Yes |

Phase 0's sync was done 2026-10-09: local and sapphire at `8988f3f17`.
