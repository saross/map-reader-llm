# D57 (4) re-score, Phase 4: the Q4 reader fix, Run B and Run C, and Q4

> **Last revised**: 2026-10-10 (original publication). See
> [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a subagent of the main Session 163 session; code in
  a local worktree, runs in a scratch clone on sapphire, 2026-10-09
  12:25–15:25 UTC.
- **Repository**: `map-reader-llm`. Pull request (PR) #28,
  <https://github.com/saross/map-reader-llm/pull/28>, branch
  `q4-repaired-readers`, head `19e3f13ea`; open, not merged, its body opens
  "**DO NOT MERGE.**".
- **Plan**: `planning/d57-4-rescore-plan-2026-10-09.md` § 5; rulings D58
  (Q8, Q9).
- **Where the outputs are**: `~/scratch/q4-repaired-readers-2026-10-09/` on
  sapphire — `runbc-compare.json`, `repo/runbc-out/`,
  `q4/compare-committed-vs-before.json`, `q4/compare-before-vs-after.json`,
  and `q4/{before,after}/`.
- **Guarantees**: nothing merged, no comments posted, no model Application
  Programming Interface (API) call, no document edited. Sapphire's shared
  checkout stayed at `8988f3f17` with an identical 122-line porcelain list.
- **⚠ Hardware caveat**: this run overlapped sapphire's memory fault
  (`reports/s163-agent-records/d57-4-rescore-census.md` § Sapphire). The
  byte-identical Run B and Run C files stand; the Q4 deltas below agree
  exactly with the prediction the Q4 agent made on 2026-10-08, an
  independent computation.

## Main-session checks (2026-10-10)

- `gh pr view 28`: OPEN, not draft, not merged, head
  `19e3f13eadffff9904adda1476dc442baad0d592`.
- `q4/compare-before-vs-after.json` contains the arm 1 values in the table
  below (F1 0.913520 and 0.913432; detections 5,285 and 5,286; tile-MCC
  0.7530 and 0.7527).

## The code fix (PR #28)

- New `scripts/lib_verify_dirs.py` with one rule: read `<leg>_repaired/`
  when it holds `probabilities.json`, else the leg.
  `MAP_READER_VERIFY_DIRS=fixed` restores the old reading. Provenance
  records the directory, its SHA-256, the `parse_repair.json` counts, and
  the re-verification rows and cost.
- Repository roots derived from `__file__` in `replicate_k5_arm1.py`,
  `replicate_k5_arm2.py`, and `inheritance_ladder.py`.
- Readers moved onto the helper: r2 `rung_frame`, the arm 1 replicate, the
  inheritance `source_leg` string, W2.7 `build_families` (plus a
  `W27_CACHE` override and 20 legacy E501 lines fixed), and the
  tile-presence image cost legs; `--floors-dir` added to
  `modality_bridge_verifier_sd.py`; tests for all of these.
- **Judgement call for review**: each tile-presence image leg is still
  priced at its own stage (the register keys its row there, and the
  `_repaired` copy's `run.meta.json` is a byte copy); the copy's audited
  re-verification cost is added on top.
- Tier-1 on sapphire (one process): at merged `19e3f13ea`, **4,196 passed,
  0 failed**, 5 skipped, 3 xfailed, 59 deselected (411.3 s). Expect tier-2
  drift in `test_the_committed_costs_regenerate_exactly` and
  `--stage costs --check` until regenerated tile-presence costs are
  committed.
- Scorer blobs are identical to `8988f3f17` at `7ca7ee82f` and `19e3f13ea`
  (`lib_advanced_metrics.py` `c6e6198b0…`, `evaluate_detections.py`
  `72c412229…`, `lib_assessed_area.py` `361dc34a8…`,
  `prepare_h13_scoring.py` `205f8b187…`, `lib_permutation.py`
  `8527fee24…`).

## Run B and Run C: nothing moves, as predicted

- Inputs: 57 untracked files copied (not symlinked) from the shared
  checkout, checksums verified; the deduplicated passes were not rebuilt.
- Gates-only pass (12:57–13:02Z): all six anchors and three anchor gaps
  reproduce; verifier-SD gates 1–4 pass.
- Full pass (13:02–13:33Z): all 10 cells, 3 gap tests, floors, and verifier
  SD exit 0.
- Of 57 committed output files, **49 are byte-identical** (all 44 cell
  files; floors `subset_cells.csv`, `summary.csv`, `gap_change.json`, and
  `date_component.json`; verifier-SD `summary.csv`). **8 differ only in
  metadata**: floors `gates.json` and `floors.json` and the three
  verifier-SD JSONs in `meta` (`wall_seconds`, `scoring_root`, the new
  `floors_dir`; `floors.json` also lists 48 NaN-against-NaN entries, which
  are not differences), and the three `gap_test.json` files in
  `pair_sources` (scratch paths). Per D58 Q9 this becomes a dated § 7a
  note, not re-committed files.

## Q4: before → after

BEFORE = `MAP_READER_VERIFY_DIRS=fixed`; AFTER = the `_repaired` copies;
same clone and scorer.

**3.7 K = 5 arm 1 replicate** (carried = F1 oracle at (0.10, k5)):

| Output | Before | After |
|---|---|---|
| Detections | 5,285 | 5,286 (+1 false positive) |
| F1@50 | 0.913520 [0.9075, 0.9193] | 0.913432 [0.9074, 0.9192] |
| Precision / recall | 0.8904 / 0.9378 | 0.8903 / 0.9378 |
| Tile-MCC | 0.7530 [0.7394, 0.7662] | 0.7527 [0.7392, 0.7660] |
| Flips at 0.10 | 221 (2.4092 %) | 220 (2.3983 %) |
| Flips at 0.50 / 0.90 | 332 / 479 | 332 / 479 |
| Identical probabilities | 7,507 | 7,509 |
| Identical-share kappa | 0.772801 | 0.773072 |
| Test (a) F1 | +0.000481, p 0.5773 | +0.000392, p 0.6508 |
| Test (a) tile-MCC | +0.000145, p 0.931 | −0.000132, p 0.97 |
| Test (b) F1 | +0.010986, p < 0.0001 | +0.010897, p < 0.0001 |
| Test (b) tile-MCC | +0.004008, p 0.1037 | +0.003731, p 0.1288 |

Test (c) is unchanged and (d) equals (a). 20 of 95 sweep rows move (prob_t
0.05–0.20); the MCC oracle stays at (0.15, k5), 0.75588 → 0.755588.

**Gemini 3 r2 campaign, arm 2**: all 13 cells re-derive with identical
detections; the six re-scored evaluations have identical metrics; the
carried, F1-oracle, and tile-MCC argmax rows of `sweeps.json` are
unchanged. Nine sweep rows at prob_t ≤ 0.05 gain 1–2 detections (F1
−0.000012 to −0.000043; tile-MCC at most −0.000202). The 2×2 tests (K1, K3,
K5) are byte-identical.

**W2.7**: § 6 subset replicates byte-identical; § 6b floors-v2
`subset_cells_all.csv` and `gates.json` byte-identical; the G3 arm 2 floors
equal the committed `floors55_all.csv` on all 20 rows.

**Tile-presence cost legs** (US$):

| Leg | Before | After | Re-verification |
|---|---:|---:|---:|
| G3IMG-ARM2-K1 | 25.397835 | 25.398964 | +0.001129 |
| G3IMG-ARM2-K3 | 40.581277 | 40.584492 | +0.003215 |
| G3IMG-ARM2-K5 | 51.092455 | 51.095783 | +0.003328 |

Only K5's Markdown figure changes (51.09 → 51.10); ranks, tile-MCC, and F1
are unchanged.

**Inheritance ladder**: could not run (flag 3).

**BEFORE against committed** (the new scorer, not Q4): metrics identical
everywhere except W2.7 (flag 2); otherwise metadata only (the new
`detection_scope` block with every counter 0, provenance blocks, the
recorded `--workers`, `merge_cells` ordering, `tests.json` key order, and
`evaluation.md` timestamps).

## Flags

1. **A transient crash with the memory-fault signature**:
   `IndexError: index 17179872156` (2^34 + 2,972) in the MCC bootstrap of
   `IMG-ARM1-K5-f1-oracle-replicate`; a re-run was identical to the carried
   cell.
2. **The new scorer moves W2.7 cells (outside Q4; D57 (4) scope)**: 4 of
   466 § 6 subset cells (family B, subsets (8,) and (8, 9) at k1, F1 about
   +0.00007, `n_det` unchanged), and 26 of 865 pair rows follow (e.g. one
   p 0.0576 → 0.0615). floors-v2's `FastScorer` still reproduces the old
   cells (its gate 4 passes), so the § 6b floors rest on a scorer
   restatement that no longer matches the current scorer for some family B
   cells.
3. **The inheritance ladder cannot run**: `--stage ladder` raises
   `KeyError: 'mcc_oracle'`, the own-leg key the 2026-09-21 relabel renamed
   to `mcc_argmax_at_carried_k`. Pre-existing; affects both campaigns; not
   patched. A read-only diagnostic shows the two inherited arm 2 cells
   unchanged under both readings.
4. **First Run B/C attempt set aside**: `image_b_analysis.py` and
   `gemini37_image_gap_test.py` log `out_dir.relative_to(PROJECT_ROOT)`,
   which raises for an out-dir outside the repository (exit 1 after
   writing). Re-run with outputs inside the clone; attempt 1 kept.
5. **Last-digit float difference**: `results/image-2x2-2026-09-19/tests_2x2_K3.json`
   differs from BEFORE only in the last digits of the T4 F1 test's
   `null_mean` and `null_std` (about 1e-16 relative); K3 dates from
   `ed3861cac`, while K1 and K5 (regenerated at `d04ceacbb`) reproduce.
6. **Budget breach**: up to 9 worker processes for about 90 s
   (14:00:42–14:02:10Z) while the determinism re-run overlapped W2.7.

## Changelog

### 2026-10-10 — Original publication

The Phase 4 agent's hand-back, with the main session's checks of PR #28's
state and the arm 1 values.
