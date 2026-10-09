# D57 (4) re-score, Phases 0 and 2: the S2 deltas

> **Last revised**: 2026-10-10 (census results; sapphire memory-fault
> caveat). See [§ Changelog](#changelog) for revision history.

- **Executed by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), a subagent of the main Session 163 session, on
  sapphire.
- **Date**: 2026-10-09 (Sydney).
- **Repository**: `map-reader-llm`.
- **Scorer**: NEW at `494b5a7af` (same `scripts/`, `tests/`, and
  `conftest.py` as `8988f3f17`); OLD from `git archive b3c52591d`.
- **Plan**: `planning/d57-4-rescore-plan-2026-10-09.md`; rulings D58.
- **Where the outputs are**: `~/scratch/d57-4-rescore-2026-10-09/` on
  sapphire (`new/` is a detached worktree at `494b5a7af`; `out/` holds the
  gate records, `registered_deltas.json`, `copy_list.txt` (2,222 paths),
  and `report_tables.md`). Nothing was copied into the tracked tree,
  nothing was committed, no model API was called, and sapphire's shared
  checkout was not touched.

## Session checks of this report (2026-10-09)

The main session re-read these at source before publishing:

- `out/copy_list.txt` has 2,222 lines; the NEW worktree is at `494b5a7af`
  with 2,222 modified files and one untracked directory (the scripts);
  sapphire's shared checkout is at `8988f3f17`.
- `out/registered_deltas.json` has 61 rows. F1@20 (four decimals, file
  value minus committed value) rises in all 61: from +0.0004
  (`e47-propose-brief::consensus-1of5`) to +0.0155
  (`h13::arm-a-native-12-5`); outside h13 at most +0.0028
  (`consensus-384-t1-0::consensus-5of5`). None falls.
- Spot values agree with the file: `pv-diag-384::flash-high-text-n5-text-t0.7-consensus-26of30`
  0.8141 → 0.8165 at 20 m; h13 arm A common 0.5580 → 0.5734.
- **One rounding difference.** For `h13::arm-a-native-12-5` the unrounded
  NEW value is 0.573044 but the regenerated file reads **0.5731**, not the
  0.5730 the agent's table below gives. The multi-pass summary averages
  per-pass F1 values that were already rounded to four decimals (mean
  0.573067). It is the only such case among the 61 registered rows, and it
  predates D50. Documents cite the file's value.
- `script_git_status: "dirty"` in the regenerated cells is the norm, not a
  defect: 2,638 of the 2,640 committed `results/**/evaluation.json` files
  carry it, because a batch written in place dirties the tree for every
  later cell (`scripts/evaluate_detections.py:486`, `_git_status` reads
  `git status --porcelain`). The provenance anchor is
  `script_git_commit` with the scorer blob SHAs below.

## Bottom line

Every Phase 2 gate passed, with one exception. 737 of 737 regenerated
cells equal `rescore_b.jsonl` at the buffers it covers: 6,210 values
compared, worst |Δ| exactly 0.0. `n_origin_switched` is 0 everywhere. The
manifest diff is exactly the 61 expected rows. The stride results match the
plan, and OLD reproduces every committed stride file byte for byte. The
exception is byte-diff check (a): 432 of 433 pass, and the one failure is
an archived cell whose difference predates D50 (flag 6).

## What ran, where, and for how long

- **Machine:** sapphire, `~/Code/map-reader-llm/.venv/bin/python`, with
  numerical libraries pinned to one thread; at most 20 worker processes.
- **Scorer blob SHAs (OLD → NEW):**
  - `lib_advanced_metrics.py`: d5ccb55bb… → c6e6198b0…
  - `evaluate_detections.py`: 12ba135f2… → 72c412229…
  - `prepare_h13_scoring.py`: 40d01bcf7… → 205f8b187…
  - `lib_permutation.py`: 8527fee24… → 8527fee24… (unchanged)
  - `lib_assessed_area.py`: absent in OLD → 361dc34a8…
- **Wall clock:**
  - Phase 2 replay: 2,434 s at 18 workers (11.5 summed per-cell hours;
    median 30 s, longest 577 s).
  - Q2 Stage A: 428 s, 4 cells at a time.
  - Stride chains, OLD and NEW in parallel: sweeps about 30 min, ladders
    about 56 min.
  - Byte-diff (a): 2,638 s at 12 workers.
- **Scripts:** 13 files in `new/reports/d57-4-rescore-2026-10-09-scripts/`
  (untracked; `ruff check` clean). The replay wrapper `replay_cell.py` runs
  the scorer in-process with each cell's recorded `cli_args`; passive spies
  record the unrounded point estimates, since the files store four
  decimals.

## Phase 0: all four checks passed

1. **Trees** confirmed as above.
2. **Feature counts:** exactly the 26 mismatches the plan names (12 pinned:
   `phase3a-{image,text}-matrix/high-t0.0` ×6 and
   `rescore-2026-06-05/pv-diag-384/…t0.0__consensus__t1–3` ×6; 11 in
   `rescore-2026-05-31`: e47 `consensus_t1–t5` and n1-outstanding Pro
   image/text HIGH T 0 `consensus_t1–t3`; 2 `h12-v2`; 1 archived 3.7
   K = 3 copy). A value-based check (committed four-decimal values against
   the jsonl's OFF values, at 1e-4) flags the same 26 and no others.
   Partition: 673 replayable (61 registered), 49 null-exemplar, 15 twins,
   13 drifted unpinned, 12 pinned, 8 ladder (7 registered), 7 archive.
3. **Expected values:** `rescore_b.jsonl` present, 2,800 rows.
4. **Determinism:** one unchanged cell replayed twice gives identical
   summaries and an identical CSV.

## Phase 2: cells

The null-exemplar inputs were rebuilt by `--stage filter` (no API path):
305 files, byte-identical to the copies the expected values were measured
on.

| Group | Replayed | Gate | ΔF1@20 (NEW − OFF) | ΔF1@50 |
|---|---:|---|---|---|
| Replayable | 673 (61 reg.) | 673 pass | +0.0000 to +0.0689 | +0.0002 to +0.0382 |
| Null-exemplar twins | 49 | 49 pass | +0.0061 to +0.0349 | +0.0081 to +0.0357 |
| Pairing twins (< 0.001) | 15 | 15 pass | +0.0000 to +0.0002 | +0.0000 to +0.0002 |
| Drifted (13), pinned (12), ladder (8), archive (7) | not replayed | — | — | — |

- No F1 falls at any buffer in any cell.
- MCC moved in 18 unregistered cells only (55-map uplift supplement), both
  directions, |Δ| ≤ 0.00027. Every registered MCC is unchanged.
- **Against the committed files, 42 regenerated cells lose their intervals
  (and 37 their tile block, MCC included), and this is not D50.** They are
  `results/uplift-supplement/k1-gapfill` (35),
  `results/pairwise/tile-size-30m` (5), and
  `results/uplift-supplement/verifier-pairing` (2), scored between
  2026-08-20 and 2026-09-08, before the tile-join refusal (`7ba47b63b`,
  `fd59a68b0`, `3eeaf96f4`); the OLD scorer withholds them identically, and
  their points reproduce. None is registered or cited in `docs/paper/`
  (`reports/s163-agent-records/d57-4-rescore-census.md`).
- MCC matched to 1e-9 in 635 cells and the refusal matched in 41. Every
  evaluation carries all 10 `_DETECTION_SCOPE_COUNTS` keys;
  `n_out_of_frame` and `n_origin_restored` equal the jsonl's `new_scope`;
  feature counts unchanged.
- The plan card's "others up to +0.0027 at 50 m" is wrong: unregistered
  `h8-v2` and `h12-v2` cells reach +0.0034, and they match their expected
  values.

**Registered cells, F1@20 OFF → NEW** (agent's table from unrounded values;
see the rounding note above for h13 arm A native; both buffers are in
`out/report_tables.md`):

- **consensus-384-t1-0**, 1of5–5of5: 0.3038→0.3052, 0.3977→0.3996,
  0.4331→0.4353, 0.4554→0.4578, 0.4712→0.4740.
- **e47-propose-brief**, consensus-1of5–5of5: 0.1798→0.1802,
  0.4128→0.4138, 0.5471→0.5485, 0.6543→0.6561, 0.7326→0.7348.
- **gold-standard-v2**, consensus-3/4/5of5: 0.5925→0.5940, 0.6999→0.7018,
  0.7649→0.7673 (the generator resolves all three to regenerated files).
- **h13** (20 m only): arm A native 0.5576→0.5730 (file 0.5731), arm A
  overlap 0.5580→0.5734; arm B native 0.5222→0.5277, overlap
  0.5198→0.5300; arm C native 0.4067→0.4130, overlap 0.4025→0.4116.
- **n1-outstanding-384**: brief-text-t03 1/2/3of3 0.4663→0.4675,
  0.5537→0.5552, 0.5907→0.5924; image-t0 0.6240→0.6258, 0.6290→0.6308,
  0.6288→0.6306; image-t03 1/2of3 0.5822→0.5838, 0.6424→0.6442;
  pro-image-high-t0 0.5614→0.5631, 0.5760→0.5778, 0.5854→0.5873;
  pro-text-high-t0 0.4634→0.4647, 0.5203→0.5217, 0.5748→0.5764.
- **pv-diag-384** (28 conditions; the three t0.0 ones score cells under
  `results/recovery-reeval-2026-07-30/` and `…-2026-09-08/`): every one
  rises by +0.0015 to +0.0025; the list is in `out/report_tables.md`.

## D58 Q2: the 25 drifted or pinned cells (Stage A only)

- **All 25 inputs as scored are recoverable from git.** Pinned cells use
  their `e82_input_vintage`; unpinned cells use the newest commit with the
  committed feature count, which agrees with the 2026-10-07 input-drift
  trace in 13 of 13. References and bounds from `cfc10c133` and
  `8b52ab63b`.
- **OLD reproduces the committed cell in 25 of 25** (every four-decimal
  point and interval bound at every buffer, MCC, sensitivity, specificity,
  confusion, and `n_detections`). Tile MCC and confusion are unchanged by
  D50 in all 25.
- **Stage B not run.** All 25 could take it.

| Cells (vintage; n scored/today) | Stage A F1@20 OLD→NEW (Δ) | Δ@50 |
|---|---|---|
| phase3a-image high-t0.0 1of10 ≡ rescore-06-05 image-t0.0 t1 (`2e8cc6481`; 802/889) | 0.4883→0.4899 (+0.0016) | +0.0016 |
| … 2of10 ≡ t2 (736/816) | 0.4594→0.4611 (+0.0017) | +0.0017 |
| … 3of10 ≡ t3 (718/782) | 0.4666→0.4683 (+0.0017) | +0.0017 |
| phase3a-text high-t0.0 1/2/3of3 ≡ text-t0.0 t1/t2/t3 (`09fe46a7f`) | 0.4364, 0.5099, 0.6051 unchanged | 0 |
| h12-v2 greedy r3-hp-heavy t1 (`2e84d4a65`; 1518/1521) | 0.2683→0.2693 (+0.0010) | +0.0010 |
| h12-v2 wbf r3-hp-heavy (`2e84d4a65`; 1097/1099) | 0.3055→0.3068 (+0.0013) | +0.0013 |
| e47 consensus_t1–t5 (`1f443fd69`) | 0.1669→0.1673, 0.3868→0.3878, 0.5188→0.5201, 0.6394→0.6411, 0.7143→0.7165 | +0.0004 to +0.0022 |
| n1 pro-image t1–t3 (`1f443fd69`) | 0.5509→0.5527, 0.5499→0.5518, 0.5525→0.5544 | +0.0018 to +0.0019 |
| n1 pro-text t1–t3 (`1f443fd69`) | 0.4726→0.4739, 0.5199→0.5214, 0.5665→0.5681 | +0.0013 to +0.0017 |

The six pinned text cells (`09fe46a7f`) do not move under D50 on their
inputs as scored, though the scope restores 3 to 5 detections; their
+0.0011 to +0.0016 on today's inputs comes from detections the drift
added.

## Stride sweeps and the conditions manifest

- `stride55_sweep_oracle.py` passes its replication gate under OLD and NEW
  (0.832590 and 0.842214); OLD reproduces `sweep_50m.csv`,
  `sweep_oracle.json`, `ladder_sweep_50m.csv`, and `ladder.json` byte for
  byte. NEW `sweep_50m.csv`: 14 and 16 rows move (2 and 3 by ≥ 0.001;
  largest +0.0085 and +0.0098), all at `prob_t` 0.00 or 0.05; all 400 rows
  equal `stride55_new.json` to 1e-9. `sweep_oracle.json` unchanged (oracles
  (k7, 0.15) 0.8362 and (k9, 0.20) 0.8503).
- Ladders (never measured before): every gate passes; NEW
  `ladder_sweep_50m.csv` moves 16 and 16 rows (6 and 7 by ≥ 0.001; largest
  +0.0057 and +0.0079), all at 0.00 or 0.05; `ladder.json` unchanged.
- Manifest: `--all --dry-run` and `--all --write` change exactly the 61
  expected condition rows (metric blocks only), with every other row of
  the four manifests byte-identical; `--check-renderings` passes;
  `verify_run_conditions.py` 41 pass, 3 partial, 0 fail (all 12 WARN rows
  concern evaluations not regenerated here). Registry rebuilt; `--check`
  passes.

## Byte-diff checks

- **(a)** 383 of 383 restored-but-unmoved cells and 49 of 50 random
  unchanged cells (seed 42) pass. The one failure is the archived
  `paper-eval-384px-outstanding/flash-text-minimal-t-0-3`: points equal,
  but its 2026-04-30 intervals do not reproduce (F1 CI [0.5055, 0.5294] →
  [0.4591, 0.5738], now flagged `partial_coverage`). OLD gives the same new
  interval, so this is an older scorer vintage, not D50; it is archived and
  left alone (D58 Q3).
- **(b)** `git status`: no detection, union, `detections_dedup`, crop
  manifest, or `probabilities.json` changed.
- **(c)** Manifest rows outside the moved set byte-identical.
- **(d)** Stride rows outside the moving set byte-identical.

## Files that would be copied (2,222)

2,211 cell files (the `.json`, `.csv`, and `.md` of each of the 737 cells),
4 stride CSVs, `conditions-manifest.json` and `.md`,
`generated-file-registry.json`, and 4 renderings whose only change is the
source-commit stamp. Full list `out/copy_list.txt`; the 13 scripts
separately.

## Flags

1. **Gate coverage is partial.** `rescore_b.jsonl` covers mostly 20 m and
   50 m; in 652 of 737 cells the other buffers are checked only for
   consistency with the scorer's own rounding.
2. **D50 alone moves nothing in the six pinned text cells** (Q2 table).
3. **Four register renderings change only their source-commit stamp**
   (`analyses`, `passes`, and `runs` manifests `.md`, and
   `run-registry.md`); the registry also changes 737 marker timestamps.
4. **Regenerated metadata**: `script_git_commit` `494b5a7af`; 688 cells now
   record `require_clean_inputs: true`; older cells gain
   `tile_join: "id"`.
5. **Tier-1 is due at the copy step** (plan § 3.3), though no code changed.
6. **The byte-diff (a) failure** above is a failed check by the letter of
   the plan.

## Changelog

### 2026-10-10 — census results and a hardware caveat

The OLD-scorer census (`reports/s163-agent-records/d57-4-rescore-census.md`)
reproduces 695 of the 737 Phase 2 cells exactly, so every change in those
695 regenerated files is D50 alone. The other 42 lose intervals for a
reason that predates D50; a bullet now says so under § Phase 2. The census
also found a memory fault on sapphire (a single bit set in 64-bit values
under load). This report's NEW values were computed on sapphire about
09:35–10:15Z on 2026-10-09 and have been checked against an independent
computation only at the gated points; a byte-for-byte reproduction is
recommended before PR #29 is merged. No number in this report changed.

### 2026-10-09 — pv-diag-384 count corrected

The registered-cells list said "pv-diag-384 (25 conditions)"; `out/registered_deltas.json` has
28, three of which score cells under `results/recovery-reeval-2026-*`, so the
per-family counts now sum to 61. The range (+0.0015 to +0.0025) was re-checked
over all 28 and is unchanged; no number moved. Found by the copy step's agent
(draft PR #29).

### 2026-10-09 — Original publication

The agent's hand-back, with the main session's checks at source added
(§ Session checks), including the h13 arm A native rounding difference.
