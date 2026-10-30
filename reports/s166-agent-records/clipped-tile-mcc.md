# S166 record: tile-MCC on PI ruling D51's clipped basis (tier E and six Phase 2 ladders)

> **Last revised**: 2026-10-30 (original publication). See [§ Changelog](#changelog) for revision history.

| | |
|---|---|
| Agent / model lane | Claude (Anthropic), Opus 5.5 (`claude-opus-5-5`), in Claude Code, a sub-agent of the S166 main session |
| Date | 2026-10-30 |
| Repository | `saross/map-reader-llm` |
| Branch | `clipped-tile-mcc-2026-10-30`, from `origin/main` at `3cbe6867e`; pushed, no pull request |
| Commits | `4970cb53f` (driver, two instrument options, tier-1 tests); `6546feed3` (results, run scripts, logs) |
| Compute | sapphire, `~/scratch/clipped-tile-mcc-2026-10-30/`, a whole-tree `git archive` of `4970cb53f`; at most six workers; US$0, no model call |

This record and `results/k-ladder-2026-09-12/clipped-mcc-2026-10-30/summary.md`
were written to disk by the main session from the sub-agent's hand-back,
because the harness does not let a sub-agent write report files. Every
number below was read from the committed artefacts named beside it.

## Bottom line

1. **§ 8.6's tile-MCC sign reversal survives the clip.** Tier E's verified
   K = 1 → 10 change in tile-level Matthews correlation coefficient
   (tile-MCC) is **−0.0161** on D51's clipped basis (−0.0238 as evaluated),
   against **+0.0444** consensus-only. The swing is **0.0604** (0.0682 as
   evaluated); the F1 reduction stays **48.7 %**. As before, the verified
   change is not statistically separated (Benjamini–Hochberg (BH) adjusted
   p 1.0000 clipped, 0.8094 as evaluated).
2. **Clipped tier E tile-MCC per rung: 0.8133 / 0.8089 / 0.8063 / 0.7973**
   (K = 1 / 3 / 5 / 10), still falling at every step.
3. **The six Phase 2 ladders all still lose tile-MCC from K = 1 to their best
   rung, and none separates.** On four the clip removes no detection, so the
   clipped reading equals the as-evaluated one exactly. On two it deepens the
   fall: HIGH text T 1.0 −0.0252 → −0.0290, MINIMAL image T 0.7 −0.0214 →
   −0.0253. Every F1 and tile-MCC Hsu multiple-comparisons-with-the-best
   (MCB) admissible set equals the committed one, on all seven ladders.
4. **No verdict moves.** R3-14 and R6-17 need their "tile-MCC has not been
   computed on the clipped basis" clause replaced, R3-13's counts can be put
   on one basis, and the K-ladder findings §§ 4.3, 7.2, 8.4 and 8.6 carry
   now-answered "not computed" or "withheld" statements (§ 5). R3-12 and
   § 4.1 are unaffected.
5. **Reference used:** D51 option 1, as the committed clipped F1 is scored.
   That means the board frame `era2-b-487` (487 tiles) and the 435 curator
   reference mounds inside it, kept whole. The consensus-only side of § 8.6
   is still scored against the 428 mounds on the grid study's common
   footprint, so the comparison matches areas but not references.

## 1. What was done

`scripts/k_ladder_clipped_cells.py` (new, `4970cb53f`) writes D51-clipped
per-tile evaluations for the seven ladders whose tile-MCC the clipped tables
withheld. It reuses the existing machinery rather than reimplementing it:

- **The common area** comes from the library's own gate
  (`lib_assessed_area.determine_assessed_area` and `compare_assessed_areas`
  with the clip). It runs on each rung's pool exactly as the Phase 2 builder
  resolves it (`new_rung_pools`, `committed_sibling_pools`; checked equal to
  the committed record's pool sources) and as the tier E driver names it
  (`run_k_ladder_tier_e.rungs`, `COMMITTED_K10`).
- **The clip** is the library's keep rule (`clip_points_to_area`). The kept
  features are written back verbatim: the source file's own feature dicts in
  their original order. A rung the clip leaves whole is copied byte for byte.
- **Each clipped cell** is scored by `scripts/evaluate_detections.py` with the
  as-evaluated cell's recorded recipe: all 14 buffers, 10,000 bootstrap draws,
  seed 42, `--mcc`, and the recorded tile join. Only the detections, output
  directory and label change (label suffix `-d51clip`).
- **The two instruments** are then run on the clipped cells:
  `scripts/k_ladder_mcc_test.py`, which gains `--conditions` so it can read a
  conditions sidecar, and `scripts/k_ladder_mcb.py`, which gains `--registry`
  so it can read a replacement registry. Both options default to the
  committed behaviour. The sidecar names only the clipped cells, so no
  clipped condition id can resolve to an as-evaluated cell.

The run was staged on sapphire with `clipped-tile-mcc-scripts/stage.sh`
(copy, prepare, evals, collect, mcc, mcb, report). Each stage was launched
detached with all three descriptors redirected and a pid file written from
inside the job, and watched on its terminal state. Stage logs are in
`clipped-tile-mcc-scripts/logs/`.

## 2. Gates

Every gate refuses rather than warns. All passed.

### 2.1 The D51 area gate (`prepare.json` → `area_gate`)

Run over all fourteen Phase 2 ladders and tier E, with no
`--allow-undetermined-area` escape, so a partial copy would have exited 4.
Every pool's area was determined, by pass provenance or by a declaration.
**Exactly the expected seven Phase 2 ladders clip**, the 3.7 text ladder and
the six Gemini 3 ladders, and tier E clips too. Every recomputed common area,
excess, and per-pool effective area equals its committed record
(`phase2/ladders.json`; for tier E,
`reports/scorer-frames-d50-d51-2026-10-08-scripts/out/ladders_new.json`).

| ladder | gate status | common area (km²) | largest excess (km²) |
|---|---|---:|---:|
| MINIMAL text T 0.3 | clipped | 1,400.3248 | 2.0819 |
| MINIMAL text T 1.0 | clipped | 1,400.3175 | 2.0893 |
| HIGH text T 1.0 | clipped | 1,397.6458 | 4.7609 |
| MINIMAL image T 0.3 | clipped | 1,400.3069 | 2.0998 |
| MINIMAL image T 0.7 | clipped | 1,399.9778 | 2.4289 |
| MINIMAL image T 1.0 | clipped | 1,399.9778 | 2.4289 |
| Gemini 3.7 text (gated, not rebuilt) | clipped | 1,364.4713 | 37.9354 |
| tier E | clipped | 1,364.4713 | 37.9354 |
| the other seven Phase 2 ladders | same area | 1,402.4067 | 0.0000 |

### 2.2 The clip and the F1 pre-gate (`prepare.json` → each rung's `clip`, `pre_gate`)

For every rung, the number of detections the clip removed equals the
committed re-score's count, and so does the number it kept. The F1 at 20 m
of the **written** clipped file, scored as the committed re-score scores it,
reproduces the committed clipped F1 to 4 decimal places on all 28 rungs.
Tier E's K = 1, 3 and 5 also match the committed unrounded values to 6 dp
(0.860360 / 0.890187 / 0.896797; absolute difference 0.0). Tier E's
K = 10 rung, the restated one with 406 detections, loses nothing to the clip,
as findings § 8.4 states; this was checked, not assumed.

### 2.3 The evaluation gate (`gate.json`)

All 28 clipped evaluations reproduce the committed clipped F1@20 to 4 dp,
hold the kept detection count, name the clipped file as their input, and
carry a tile-classification block. No tile-MCC was read before this passed.

### 2.4 After the instruments (`summary.json` → `report_gate`)

Every cell's rebuilt micro-F1 equals its evaluation's F1 within half a unit
in the fourth place, and every cell passed the tiering harness's confusion
gate, including its geometric arm. Tier E's K = 1, 3 and 5 micro-F1 equal the
committed unrounded clipped values at 6 dp. Wherever the clip removed
nothing (18 of the 24 Phase 2 rungs and tier E's K = 10), the clipped tile
confusion equals the as-evaluated one. No cell was withheld. Both
instruments' own gates passed (`mcc-test/summary.json`, `mcb/summary.json`:
`gate_all_passed` true).

### 2.5 The clip alone moves the moved cells

The Phase 2 as-evaluated cells were scored in September 2026, before the
D50 scorer, and their clipped twins with today's. So today's tile
classification was run on both files of each moved pair
(`clipped-tile-mcc-scripts/attribution_check.py`, output beside it).
**Today's scorer reproduces all six unclipped confusions exactly.** The
whole clipped-minus-as-evaluated difference is the clip: one true-positive
tile becomes a false-negative tile on each moved rung, and nothing else in
the confusion changes. On tier E's K = 1, 3 and 5, already re-scored on
today's scorer, the clip turns exactly two true-positive tiles into
false-negative tiles.

### 2.6 Tests and the red sentinel

`tests/test_k_ladder_clipped_cells.py` has 31 tier-1 tests, all passing.
They cover the verbatim writer, the recipe replay, the gates, and the
contracts with the two instruments. The existing related tier-1 modules
(`test_k_ladder_mcb.py`, `test_k_ladder_mcc_instruments.py`,
`test_k_ladder_phase2.py`, `test_assessed_area.py`; 118 tests) pass, and
`ruff check` is clean on every touched Python file.

The red sentinel ran on a real-file copy (no symlinks) of `scripts/`, the
test module, `conftest.py`, `config.py` and `pytest.ini`. Unmutated,
`test_clip_keeps_the_source_features_verbatim_and_in_order` passed (1 passed).
The writer was then broken to keep every feature
(`out["features"] = list(features)`), and the test failed (1 failed).

## 3. Per ladder, clipped beside as evaluated

Each row compares K = 1 with the ladder's best F1 rung, which is the same
rung on both bases. ΔF1 is at 20 m. Every delta is (higher K) − (lower K),
from the instrument's unrounded statistics. Each BH p is adjusted within
the ladder's own six pairs. Sources: clipped, `summary.json`; as evaluated,
`phase2/mcc-test/<ladder>.json` and `tier-e/ladder.json`; MCB, the two
`mcb/summary.json`.

| ladder | detections clipped (K = 1/3/5/10) | ΔF1 clipped (BH p) | Δtile-MCC clipped (BH p) | Δtile-MCC as evaluated (BH p) |
|---|---|---:|---:|---:|
| MINIMAL text T 0.3, K1 → K5 | 0/0/0/0 | +0.0224 (0.2768) | −0.0251 (0.6044) | −0.0251 (0.6044) |
| MINIMAL text T 1.0, K1 → K10 | 0/0/0/0 | +0.0546 (0.0012) | −0.0214 (0.5760) | −0.0214 (0.5760) |
| HIGH text T 1.0, K1 → K10 | 0/3/3/3 | +0.0954 (<0.0001) | **−0.0290** (0.5529) | −0.0252 (0.8065) |
| MINIMAL image T 0.3, K1 → K10 | 0/0/0/0 | +0.0139 (0.7803) | −0.0065 (0.9954) | −0.0065 (0.9954) |
| MINIMAL image T 0.7, K1 → K10 | 0/2/2/2 | +0.0600 (0.0018) | **−0.0253** (0.8191) | −0.0214 (0.9768) |
| MINIMAL image T 1.0, K1 → K10 | 0/0/0/0 | +0.0383 (0.1236) | −0.0282 (0.6072) | −0.0282 (0.6072) |
| tier E, K1 → K5 | 29/29/27/0 | +0.0364 (0.0006) | −0.0071 (1.0000) | −0.0071 (1.0000) |

On the four zero-clip ladders the clipped test reproduces the committed
2026-09-12 test exactly: the same deltas, raw p and BH p. Tile-MCC MCB
admissible sets are {1, 3, 10} on MINIMAL text T 0.3 and {1, 3, 5, 10} on the
other six, on both bases. F1 sets are also unchanged: {3, 5, 10} on five
ladders, {1, 3, 5, 10} on MINIMAL image T 0.3, and {5, 10} on MINIMAL image
T 0.7. The rung with the highest tile-MCC is unchanged too: K = 3 on MINIMAL
text T 0.3 and K = 1 on the other six. No tile-MCC pair separates on any of
the seven ladders (0 of 42 pairs), and the F1 tiers of the two moved ladders
are unchanged.

Rung-level tile-MCC where the clip moves it (clipped, with as evaluated in
brackets):

| ladder | K = 1 | K = 3 | K = 5 | K = 10 |
|---|---:|---:|---:|---:|
| HIGH text T 1.0 | 0.8162 (0.8162) | 0.7948 (0.7986) | 0.7819 (0.7857) | 0.7872 (0.7910) |
| MINIMAL image T 0.7 | 0.8437 (0.8437) | 0.8339 (0.8377) | 0.8345 (0.8383) | 0.8185 (0.8223) |
| tier E | 0.8133 (0.8211) | 0.8089 (0.8167) | 0.8063 (0.8139) | 0.7973 (0.7973) |

## 4. The § 8.6 answer, and tier E's six pairs

| stage (384 px, 50 % overlap, K = 1 → 10) | ΔF1@20 | Δtile-MCC |
|---|---:|---:|
| consensus only (`tension/grid-overlap.json`, cell `g384_ov192`) | +0.0660 | +0.0444 |
| verified, D51 clipped | +0.0338 | **−0.0161** |
| verified, as evaluated | +0.0262 | −0.0238 |

The reversal survives, about a third smaller in size: the swing is 0.0604
against 0.0682. The F1 reduction is 1 − 0.033813 / 0.065954 = 48.7 %.

Tier E, all six pairs, clipped (as evaluated, from § 8.4, in brackets):

| pair | ΔF1@20 (BH p) | Δtile-MCC (BH p) |
|---|---:|---:|
| K1 → K3 | +0.0298 (0.0024) [+0.0299 (0.0036)] | −0.0044 (1.0000) [−0.0044 (1.0000)] |
| K1 → K5 | +0.0364 (0.0006) [+0.0366 (0.0006)] | −0.0071 (1.0000) [−0.0072 (1.0000)] |
| K1 → K10 | +0.0338 (0.0021) [+0.0262 (0.0292)] | −0.0161 (1.0000) [−0.0238 (0.8094)] |
| K3 → K5 | +0.0066 (0.5307) [+0.0067 (0.4246)] | −0.0026 (1.0000) [−0.0028 (1.0000)] |
| K3 → K10 | +0.0040 (0.6865) [−0.0037 (0.6559)] | −0.0116 (1.0000) [−0.0194 (0.8094)] |
| K5 → K10 | −0.0026 (0.6865) [−0.0104 (0.2077)] | −0.0090 (1.0000) [−0.0167 (0.8094)] |

Tiers are unchanged: Tier 1 = {K = 3, 5, 10}, Tier 2 = {K = 1}. F1
separates on the same three pairs, every pair involving K = 1, and tile-MCC
separates on none.

**Why the clip shrinks tier E's decline but deepens the two Phase 2 ones.**
On tier E the lower rungs (K = 1, 3, 5) searched the 37.94 km² band and
K = 10 did not, so the clip removes lower-rung true positives there. K = 1's
tile-MCC falls (0.8211 → 0.8133) while K = 10's stays (0.7973), and the
K = 1 → 10 fall shrinks. On HIGH text T 1.0 and MINIMAL image T 0.7 it is
the higher rungs that searched the extra area, so the clip removes their
true positives and the fall deepens.

## 5. Claims that would need qualifying

No claim's direction or verdict moves. What changes is wording that says the
clipped tile-MCC "has not been computed" or is "withheld", plus figures that
can now lead on the clipped basis. The inventory, findings, register and
planning documents were not edited (job card); these are proposals.

- **R3-14 and R6-17** (`docs/paper/results-claims-inventory-2026-09-12.md`,
  2026-10-30 notes). Both claims survive. The approved re-draft's last clause,
  "tile-MCC has not been computed on the clipped basis", is no longer true.
  On the clipped basis the verified tile-MCC change is −0.0161 (−0.0238 as
  evaluated) and the swing 0.0604 (0.0682). Under D69 decision A, where the
  clipped reading leads, the consistent form would lead with −0.0161 and
  0.0604 and give the as-evaluated values beside them. The F1 figures (48.7 %,
  60.3 %) do not move. The wording is for the PI.
- **R3-13.** Holds. Its re-draft splits the count across two bases ("15 …
  tile-MCC falls on 10; as evaluated it also falls on the six others (16 of
  21)"). Each of the six withheld ladders also falls on the clipped basis, so
  the count is 16 of 21 on either basis. None of the six separates clipped,
  so "no significant rise" and the four significant falls stand. HIGH image
  T 1.0, the one significant Phase 2 fall, is not clipped.
- **R3-12.** Holds without change. Its note says the Phase 2 tile-MCC tests
  "were not re-run". They now have been, on the clipped basis, and every
  F1 and tile-MCC admissible set and every highest-tile-MCC rung is
  unchanged on the seven ladders.
- **Findings § 4.1.** Unaffected: its eight ladders are Phase 1 ladders,
  none clipped, and its three significant falls stand.
- **Findings § 4.3** (‡ note and the paragraph after the table). "Those
  tests were not re-run" and "every withheld reading is a decline" can now
  read: re-run on the clipped basis, and every clipped reading is a decline.
  Two clipped values differ from the table's: HIGH text T 1.0 0.8162 →
  0.7872 (−0.0290) and MINIMAL image T 0.7 0.8437 → 0.8185 (−0.0253). § 7.2's
  parenthesis ("the builder now withholds six of those readings, all six
  declines") is in the same position.
- **Findings § 8.4.** "no clipped per-tile table exists" is answered. The
  clipped tile-MCC column is 0.8133 / 0.8089 / 0.8063 / 0.7973, still
  monotone. Item 3's "+0.0262 at BH p = 0.0292" reads +0.0338 at BH p = 0.0021
  clipped; it is still between § 8.1's +0.019 and +0.055, so the "band, not a
  threshold" reading holds. "K = 10 is below it by 0.0104" becomes 0.0026
  clipped.
- **Findings § 8.6.** "Clipped tile-MCC has not been computed, so its sign and
  magnitude are unknown" is answered: −0.0161, the sign reversal holds, and
  the swing is 0.0604. Also see § 6 item 4 on its "unrounded values".

## 6. Surprises, flagged and not explained away

1. **On four of the six Phase 2 ladders the clip removes no detection at any
   rung.** Their gates do clip, by 2.08 to 2.43 km², but no larger-area rung
   placed a detection in that strip at its operating point. So the tables'
   withholding of their tile-MCC was formal: clipped equals as evaluated, and
   the committed tests reproduce exactly.
2. **The clip moves a ladder's tile-MCC trend in either direction**,
   depending on which rungs searched the extra area (§ 4). It shrinks tier
   E's fall and deepens the other two.
3. **Tier E's F1 K = 1 → 10 rise becomes much clearer clipped**: BH p
   0.0292 → 0.0021. The K = 5 lead over K = 10 shrinks from 0.0104 to 0.0026,
   and K = 3 → 10 changes sign (−0.0037 → +0.0040; not significant either
   way).
4. **§ 8.6's "unrounded values" are not quite unrounded.** It computes
   48.7 % as 1 − 0.033840 / 0.065954 and 60.3 % as 1 − 0.026191 / 0.065954.
   Both numerators pair the 4 dp K = 10 value 0.8942 with a 6 dp K = 1 value.
   At full precision they are 0.033813 and 0.026165, and both percentages are
   unchanged. In the same way, some findings deltas are differences of 4 dp
   values: § 8.4's −0.0072 is −0.007148 unrounded, and § 4.3's HIGH text
   T 1.0 +0.0955 is +0.095419. None moves a reported figure beyond the fourth
   decimal.
5. **The clipped-away band is not whole tiles.** On tier E, 49 frame tiles
   touch the 37.94 km² band. The seven band mounds lie in seven tiles, each
   71 % to 78 % inside the common area, and four of those tiles hold no mound
   inside it. D51 option 1 keeps every tile and reference, so a partly
   clipped tile is scored whole.
6. **Renderer lint debt.** `evaluate_detections.py` writes `evaluation.md`
   with two consecutive blank lines (MD012, line 23), and `k_ladder_mcb.py`
   writes `table.md` with no heading (MD041). Both faults are in the
   committed counterparts too. The 29 generated files were left out of the
   commit; the JSON they project is committed.
7. **Provenance fields read `unknown`.** The artefacts' own `git_commit`
   and `script_git_commit` fields read `unknown` because the copy was a
   `git archive`. `source-commit.txt` records the source commit,
   `4970cb53f`.

## 7. Options not taken (for the PI)

- **A reference-matched reading.** Scoring the clipped rungs against only
  the mounds inside the common area would match § 8.6's consensus side on
  references as well as area. It changes the reference set, so it was not
  chosen here; D51 option 1 is the ruled basis.
- **The shrink-the-frame sensitivity** (D57 (2), "to be measured"). This
  needs a rule for the partly clipped tiles of § 6 item 5, which is a
  methodological choice, so it was not computed.

## 8. Not done

- Nothing was edited in the K-ladder findings, the claims inventory,
  `results/run-analyses.json`, `docs/`, `planning/`, or the committed Phase 2
  tables.
- The Gemini 3.7 text ladder was gated but not rebuilt: the tile-join
  invariant still withholds its K = 1 and K = 3 tile-MCC (findings § 7.3).
- Part (b) of the MCC robustness job, the tile-join sensitivity, is another
  job.
- No pull request was opened.

## 9. Reproduction

On sapphire, from `~/scratch/clipped-tile-mcc-2026-10-30/`, each line
launched detached as
`nohup bash stage.sh <stage> > logs/<stage>.log 2>&1 < /dev/null &`:

```bash
bash stage.sh copy 4970cb53f40fe423da60609f60beb55085532b03
bash stage.sh prepare
WORKERS=6 bash stage.sh evals
bash stage.sh collect
bash stage.sh mcc
bash stage.sh mcb
bash stage.sh report
```

Wall time from copy to report was about seven minutes. Each evaluation took
about 18 s (`logs/evals-times.tsv`).

## Changelog

### 2026-10-30 — Original publication

First record of the clipped tile-MCC job (Session 166; PI ruling D69
decision C; `planning/paper-writeup-continuity.md`, "Planned: one $0 MCC
robustness job", part (a)). Results committed at `6546feed3`.
