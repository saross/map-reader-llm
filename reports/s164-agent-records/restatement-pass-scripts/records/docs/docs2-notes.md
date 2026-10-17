# S164 restatement pass: document restatements, lead 2 docs2

Drafted 2026-10-16 by Claude (Opus 5.5, sub-agent of lead 2) over
`~/scratch/s164-restate-2026-10-15/wt`, read only through `git show` at
BASE = `718d0ee08` and NEW = `4660c0549`. No file in the worktree was
written and no model Application Programming Interface (API) call was made.
Edited copies mirror repository paths under this directory; `edits.diff`
is `diff -u` of each against NEW. Every edit script read its values from
the artefacts at run time (the scripts were piped over ssh and are not
kept here). `markdownlint-cli2` with the worktree's `.markdownlint.json`:
0 errors on all five files.

## 1. `results/gemini3-image-55map-2026-09-16/findings.md` (edited)

| Line (edited file) | Old → new | Source at NEW (key) |
|---|---|---|
| 3–7 | banner: 2026-10-15 entry prepended; prior 2026-09-21 kept | — |
| 304 | K = 5 arm 1 row A GS F1 0.9254 → 0.9353; gap 0.0823 → 0.0922 | `results/conditions-manifest.json` `gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5` `metrics.per_buffer["20"].f1`; unrounded 0.9353348730 in `results/gemini37-image-gs-2026-09-01/arm1/analysis.json` `operating_point.f1` (n 438); row B 0.8431137725 in `results/gemini3-image-55map-2026-09-16/gs-calibration/k5/arm1/analysis.json` `f1` (unchanged BASE → NEW) |
| 305 | K = 5 arm 2 0.9308 → 0.9408; gap 0.0757 → **0.0856** | manifest `…::g37-image-k5-verified-swap37-p0.90-k5` `metrics.per_buffer["20"].f1`; unrounded 0.9407665505 in `…/arm2/analysis.json` `image_best.f1` (prob_t 0.9, min_votes 5, n 433); row B 0.8551236749 in `…/gs-calibration/k5/arm2/analysis.json` |
| 307–315 | new note: registered point under D65 (3), argmax (0.05, k5) F1 0.9381, rounding of the arm-2 gap, K = 3 rows and row B not re-run | 0.9380733945 = `…/arm1/analysis.json` `image_best.f1` (prob_t 0.05); "not re-run" = `reports/s164-agent-records/rescore-repaired-gs.md` lines 623–627 |
| 390–419 | new changelog entry (newest first) | commits `f6f10d605` (arm analyses), `459657e18` (manifest) |

**Gap rounding (flag).** The brief gave 0.0857 for arm 2. On unrounded F1
the gap is 0.940767 − 0.855124 = 0.085643 → **0.0856**; 0.0857 is the
difference of the rounded cells. I followed the pass's own convention
(`94d5815b3`, "round the all-3.7 gap to −0.0044": unrounded, then
round) and said so in the note under the table. Arm 1's gap is 0.0922
either way (0.092221). BASE gaps reproduce either way (0.082294, 0.075709).

**Not edited, flagged:** the K = 3 rows (0.9197/0.9245 row A; 0.8200/0.8408
row B) and the K = 3 paragraph's 0.0837/0.0997 come from the two
`gs-calibration/` analyses, which read re-verified K = 3 arms and were not
re-run (rescore record above). They are labelled "as run" in the note.

## 2. The three paper tables (edited; banner + changelog only)

They are **hand-written**, not generated:
`reports/verification/generated-file-registry.json` gives
`stratum: hand-written`, rule `hw-paper-tables` (generator-map note: "machine-
shaped but their ephemeral writer was never retained — verify by
extraction, not regeneration", commit `71d81cd5e`). No script writes these
paths (`git grep` over `scripts/`; `regen_e43_board.py` only cites the 20 m
file). So the banner belongs in the file, as in `d6e2f40e8`'s
`leaderboard-20m-annotated.md`. None had a changelog; each now has the
2026-10-15 entry, the E72 (`2f3ef020a`) and scope-note (`7ab7d7fa1`, tier
tables only) entries, and an original-publication stub (20 m:
2026-03-29, `f859cd1ad`…`f3bb8e46b`; 30 m and hypothesis table:
2026-03-28, `71d81cd5e`). Body tables untouched.

| File | Lines | Source at NEW (keys: `comparisons[]` `f1_a/b`, `precision_a/b`, `recall_a/b`, `n_detections_a/b`, `delta_f1`, `p_value_raw`, `p_value_adj`, `significant`) |
|---|---|---|
| `results/paper-tables/leaderboard_tiers_20m.md` | 3–21 banner; 139–214 changelog | `results/pairwise/leaderboard-20m/fdr/pairwise_results_fdr.json` |
| `results/paper-tables/leaderboard_tiers.md` | 3–20 banner; 120–189 changelog | `results/pairwise/leaderboard-30m/fdr/pairwise_results_fdr.json` |
| `results/paper-tables/pairwise_hypothesis_table.md` | 3–24 banner; 122–221 changelog | `results/pairwise/30m/fdr/…json` and `results/pairwise/20m/fdr/…json` |

Key values (all checked at both refs): 20 m — 16 rows move +0.001838 to
+0.003251 F1, 265/325 significant both, two flips (q 0.04715 → 0.056875;
0.050949 → 0.049547), #1 v #2 q 0.048811 → 0.048996, raw p 0.0398. 30 m
leaderboard — 16 rows +0.001838 to +0.003227; **243 → 240 significant**
(three pairs lose significance: q 0.03954 → 0.051037, 0.045802 →
0.060964, 0.045802 → 0.056707); nine tiers, same members and order.
Hypothesis families — 14 cells +0.001838 to +0.003122 (Pro image 3/5 and
every PV cell unmoved); 21/32 (30 m) and 23/32 (20 m) significant with
identical marks; every 20 m direction mark holds; largest move Pro text
3/5 + PV vs Pro text 3/5 p_adj 0.256927 → 0.407748.

**Checks I computed (not artefacts, so not written into the documents):**

- E72's reduced families, recomputed with plain BH on the files.
  BASE reproduces E72 exactly (20 m leaderboard 253 tests, 199
  significant, #1 v #2 q 0.050347; 30 m 231 tests, 181; hypothesis 20 m
  23-member Group 7 q 0.050735). At NEW: 20 m leaderboard 253/**198**,
  #1 v #2 q 0.0506 (still shares Tier 1); 30 m 231/**178**; and the
  hypothesis 20 m 23-member Group 7 (N=30 vs N=10 HIGH text) **q 0.0483**,
  so **E72's flip of that row to non-significant no longer happens**. This
  matches the pass record's remark (`restatement-pass.md` line 286). The
  E72 banners in all three tables therefore quote stale reduced-family
  figures; the documents say `results/e43-board-regen/` was not
  regenerated, without asserting the new values.
- The 20 m table places #10 (FH image 3/5 + PV) in Tier 3 with #8 and #9;
  the greedy rule in F1 order puts it with #11 and #12 at both refs. Both
  partitions are free of significant pairs at both refs (pairs among #8
  to #12: only #9 v #11 and #9 v #12 significant), so the March layout is
  a valid alternative ordering, not a stale value. Not changed.
- The March hypothesis table double-rounds some values (0.079 for
  0.078486, 0.102 for 0.102541, 0.865 for 0.86445, 0.157 for 0.156452);
  the changelog says so and gives source values.

## 3. `results/k-ladder-2026-09-12/inventory.md` (edited)

**Hand-written**: registry `stratum: hand-written`, no generator;
`scripts/build_k_ladder_inventory.py` writes only `inventory.json` and
`inventory-tables.md` (its lines 521–523). At NEW those two were not
rebuilt but value-refreshed by
`reports/s164-agent-records/restatement-pass-scripts/kladder/kl_inventory_refresh.py`
(`inventory.json` `values_refreshed`; commit `f53f6e97c`).

| Line | Old → new (F1@20; tile-MCC; n) | Source at NEW |
|---|---|---|
| 3–6 | banner prepended | — |
| 77 | K = 1: 0.8677; 0.7894; 411 → 0.8737; 0.8010; 419 | `results/stride-2026-08-25/conditions-verified/g384_ov128-ladder-n1/eval/evaluation.json` `summary.buffers[buffer_metres=20].f1`, `summary.tile_classification.mcc.point`, `summary.n_detections` |
| 78 | K = 3: 0.8911; 0.7814; 380 → 0.8993; 0.7927; 386 | `…/g384_ov128-ladder-n3/eval/evaluation.json` (same keys) |
| 79 | K = 5: 0.8856; 0.7805; 394 → 0.8937; 0.7918; 400 | `…/g384_ov128-ladder-n5/eval/evaluation.json` |
| 80 | K = 10: 0.8982; 0.8022; 387 → 0.9075; 0.8134; 394 | `…/g384_ov128/eval/evaluation.json` |
| 199–238 | changelog entry | commits `f6f10d605`, `f53f6e97c`, `459657e18` |

Each new value was asserted equal to `inventory.json` (`f1_20`, `mcc`,
`n_detections`) and matches `inventory-tables.md` lines 379–382 and the
manifest's `metrics.per_buffer["20"].f1`. A scan of every 0.xxx(x) number
in the document against both `inventory-tables.md` versions found no
other moved value.

## 4. `results/working-precision/gs-plateau-characterisation.md` (NOT edited)

Generated: registry rule `gen-gs-plateau`, generator
`scripts/characterise_gs_plateau.py` (write site line 238; also writes
`gs-plateau-characterisation.json`, line 230). No check mode. Command, on
sapphire, from the checkout root once the manifests are final:

```bash
.venv/bin/python scripts/characterise_gs_plateau.py
```

(default `--out-dir results/working-precision`; pass
`--out-dir <scratch dir>` first to diff before overwriting; never
`--legacy-modality`). Inputs: `results/conditions-manifest.json` (moved
in `459657e18`), `results/runs-manifest.json` (unchanged BASE → NEW), and
through `scripts/derive_condition_modality.py`:
`results/passes-manifest.json` (unchanged), `results/run-conditions.json`
(changed, `41acb3d50`, the carried-arm register row), `prompts/configs/`,
and the proposer pools' `*.meta.json`. Expected move includes line 113
`gemini37-screen-2026-08-28::g37-text-k1-verified-opmax` F1@20
0.8495 → 0.8747 (manifest at NEW), with onset, F1@onset, drift and the
header aggregates by regeneration. The two copies under
`results/modality-track-audit-2026-09-14/recomputed/` are dated records
(rule `gen-gs-plateau-modality-audit`) and should not be regenerated.
