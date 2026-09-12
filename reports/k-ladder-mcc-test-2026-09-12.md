# The K-ladder tile-MCC direction, tested

> **Last revised**: 2026-09-12 (original publication). See
> [§ Changelog](#changelog) for revision history.

**What this reports.** The PI ruled that the metric divergence in
`results/k-ladder-2026-09-12/findings.md` § 4 — F1 rising with pass count K on
all eight fixed-parameter ladders while tile-level Matthews Correlation
Coefficient (MCC) falls on five, is flat on two, and rises only on the gold
standard — be **tested** rather than described, and that the registered
`pass-budget-pareto-v2` analysis **gain a tile-MCC column**. Both are done. All
compute ran on sapphire at US$0 with zero Application Programming Interface
(API) calls.

**One-line answer.** The direction survives: F1 rises significantly on all eight
ladders, **no ladder shows a significant tile-MCC rise**, three show a
significant fall, and § 4's one counter-example — the gold standard's +0.0134 —
does not survive testing.

---

## 1. The gate, before any MCC number

Nothing below was read before its ladder's gate passed.

| ladder group | gate | result |
|---|---|---|
| the seven 55-map ladders (25 pairs) | every tested pair's reproduced `f1_a`, `f1_b`, `observed_diff` (6 dp) and raw `p_value` (4 dp) must equal the committed board `pairwise` entry | **PASS, 25/25** |
| gold-standard ladder (4 pairs) | no committed pairwise table exists, so: each rung's rebuilt micro-F1 vs its committed evaluation F1, and each rung's rebuilt tile confusion and MCC vs its committed `tile_classification` | **PASS** — F1 gap +0.0000 on all four cells; confusion and MCC exact |
| per-cell MCC gate, all 8 ladders (29 rungs) | rebuilt per-tile one-hot classification must aggregate to the recorded confusion cells exactly, and to the recorded MCC within 5e-5 | **PASS**, hard `ConfusionGateError` otherwise |
| sign-swap rebuild (stride A and B) | committed K = 10 union reproduced (count, votes, centroids ≤ 0.2 m); committed primary F1 to 1e-6; each rung's committed oracle corrected-F1 to 1e-6 | **PASS** — see § 4 |

**Anchors.** Gate records: `results/k-ladder-2026-09-12/mcc-test/<ladder>.json`
key `gate` (per-pair `committed` / `reproduced` / `abs_delta`) and
`gate.cell_gates`; roll-up `mcc-test/summary.json` key `gate_all_passed: true`.
Committed sources: `results/55map-final-board-r2-2026-09-06/final_board_50m.json`
(the r2 ladders, 595 pairs, `instrument` field: "round-robin tile-swap micro-F1
permutation (10000, seed 42) + BH q=0.05 + greedy-clique tiers (the GS chain)")
and `results/55map-final-board-2026-08-27/final_board_50m.json` (the
standardised siblings). `bh_adjusted_p` is deliberately not gated: the board
adjusts over its 595-pair family, this run adjusts within each ladder.

**Why the gate matters here.** The F1 side of this run is a *reproduction* of a
committed result, so it is checkable to the last recorded digit; the MCC side is
new. Passing the F1 gate is what licenses trusting the MCC numbers produced by
the same harness, on the same tiles, under the same swap masks.

## 2. The instrument, and what was extended

**The test.** Round-robin tile-swap permutation — the board chain — 10,000
permutations, seed 42, two-sided, Benjamini-Hochberg (BH) q = 0.05 within each
ladder's own round-robin. F1 statistic: micro-average F1 at the ladder's headline
buffer (20 m gold standard, 50 m 55-map) over per-tile TP/FP/FN. MCC statistic:
tile-level MCC over per-tile one-hot (TP, TN, FP, FN).

**One permutation, two statistics.** `permutation_test_float` (F1, in
`scripts/n1_baseline_leaderboard_tiering.py`) draws one
`(n_permutations, n_tiles)` uniform block from `default_rng(42)`;
`permutation_test_mcc_arrays` (MCC, in `scripts/pairwise_permutation_test.py`)
draws `n_tiles` per iteration from the same seed. NumPy fills the block row-major
from the same stream, so with one seed and one tile order the two kernels see
**byte-identical swap masks** — pinned by
`tests/test_k_ladder_mcc_instruments.py::test_f1_and_mcc_kernels_draw_identical_swap_masks`.
A ΔF1 and a ΔMCC on one rung pair are therefore two statistics of one
permutation, not two experiments.

**Buffer invariance.** Tile truth is intersection with any reference and tile
prediction is any detection assigned to the tile, with no matching tolerance, so
the MCC column is the same number at 20 m and 50 m. Only the F1 column carries a
buffer.

**Extensions made** (commit `156bddf36`):

| file | change |
|---|---|
| `scripts/pairwise_permutation_test.py` | extract `permutation_test_mcc_arrays`, the array-level MCC sibling of `permutation_test_float`; `run_permutation_test_mcc` now delegates to it, so one implementation of the MCC permutation remains |
| `scripts/era1_leaderboard_tiering.py` | `--permute-mcc` (per-tile classification rebuild + hard confusion/MCC gate + MCC round-robin with its own BH family) and `--buffer` (so a 55-map board tiers at its own 50 m headline). Its header previously said MCC "is NOT the permutation statistic"; it now can be |
| `scripts/stride55_sweep_oracle.py` | `per_map_tile_confusion` and `paired_permutation_mcc` — the sign-swap's MCC sibling on the same 55 pairing units, same seed, same permutation count |
| `scripts/stride55_ladder.py` | `--pairs-output-dir` (all rung pairs, both statistics, BH within each cell's ladder), `--reuse-oracles` (gate the rebuilt rungs against the committed oracle F1 instead of re-sweeping), `--output-dir` (keeps a re-run off the committed 2026-08-27 artefacts) |
| `scripts/k_ladder_mcc_test.py` | new driver: oracle-rung selection, per-ladder analysis rows, the run, the board gate, the collation |

**Rung basis.** Oracle, the basis § 4 tabulates. Where a K commits both a carried
and an oracle cell, the oracle is selected
(`select_rungs`, pinned by a tier-1 test).

## 3. The per-ladder result

ΔF1 and ΔMCC are both **(higher K) − (lower K)**; p-values are BH-adjusted
within the ladder; bold is significant at q = 0.05. `<0.0001` is below the
1/10,000 permutation floor. Full table with raw p-values and permutation
parameters: `results/k-ladder-2026-09-12/findings.md` § 4.1 and
`mcc-test/<ladder>.json`.

| ladder | K = 1 → best rung | ΔF1 (BH p) | ΔMCC (BH p) | verdict on the § 4 direction |
|---|---|---:|---:|---|
| GS stride A (20 m, board frame) | K1 → K10 | **+0.0300** (0.0072) | +0.0134 (0.7678) | § 4's MCC **rise does not survive** |
| 55-map stride A, r2 | K1 → K10 | **+0.0192** (<0.0001) | −0.0052 (0.1984) | fall not resolved by the instrument |
| 55-map stride A, standardised | K1 → K10 | **+0.0188** (<0.0001) | −0.0052 (0.1984) | fall not resolved |
| 55-map stride B, r2 | K1 → K10 | **+0.0547** (<0.0001) | +0.0031 (0.5592) | flat, as § 4 said; not resolved |
| 55-map stride B, standardised | K1 → K10 | **+0.0545** (<0.0001) | +0.0031 (0.5832) | flat; not resolved |
| 55-map stride B, 3.7 verifier | K1 → K10 | **+0.0462** (<0.0001) | **−0.0112** (<0.0001) | **fall confirmed** |
| 3.7 arm 1 | K1 → K5 | **+0.0315** (<0.0001) | **−0.0099** (0.0168) | **fall confirmed** |
| 3.7 arm 2 | K1 → K5 | **+0.0261** (<0.0001) | **−0.0275** (<0.0001) | **fall confirmed** |

**Three things to read off it.**

1. **F1 rises significantly on all eight.** Nothing in § 4's F1 column is
   weakened, the gold standard included.
2. **No ladder shows a significant MCC rise; three show a significant fall.**
   The three are exactly the three with a Gemini 3.7 component, which are also
   the three with the largest MCC movements — consistent with § 4's mechanism
   (extra true positives land in already-positive tiles and move no tile; extra
   false positives flip negative tiles), whose size should track how many new
   false positives the extra passes contribute.
3. **The one counter-example does not survive.** The gold standard's +0.0134
   tests at BH p = 0.7678 on 487 tiles. That is the same power limitation § 2
   already records for the gold standard's F1 confidence intervals (half-widths
   ≈ ±0.025): the 4-map instrument cannot resolve a ΔMCC of this size. So the
   honest reading is not "seven fall and one rises" but "the direction holds
   wherever the instrument resolves, and has no tested counter-example".

**New, from the adjacent pairs.** The within-ladder path is **not monotonic**.
Both stride A ladders lose MCC significantly at K = 3 → 5 (−0.0111,
BH p = 0.0066) and regain it significantly at K = 5 → 10 (+0.0047,
BH p = 0.0300) — two significant, opposite-signed MCC steps inside one ladder
whose end-to-end ΔMCC (−0.0052) does not separate. § 4's endpoint framing hides
that. And on 3.7 arm 1 the K = 3 → 5 step is the mirror image of the headline
trade: **MCC falls significantly (−0.0032, BH p = 0.0498) while ΔF1 does not
separate at all** — the only pair of the 29 where the MCC test resolves and the
F1 test does not.

**What is still not claimed.** That the five non-separating ladders' MCC moves
are zero: five of eight are simply below this instrument's resolution, and a
non-significant −0.0052 is not a demonstrated absence of decline. No MCC
*ranking* of rungs is claimed either — tiering stays on the preregistered F1.

## 4. The instrument question, which is NOT resolved here

`findings.md` § 6.1 records the PI's ruling on the 55-map ladders' instrument as
pending, and this run does not take it. Two corrections to that section were
needed first, because both of its factual claims about the alternatives are
wrong at source:

1. **The 55-map cells are rebuildable.** § 6.1 said they "were scored by
   `compute_corrected_f1_multi_buffer.py`, which writes `summary.json` with no
   `cli_args`". Checked: **all 31** cells of
   `results/55map-final-board-r2-2026-09-06/cells/` and **all 19** of
   `results/55map-final-board-2026-08-27/cells/` carry a `detections.geojson` and
   an `evaluation.json` written by `scripts/evaluate_detections.py` with complete
   `_metadata.cli_args` (detections, `best-available-gt-55maps-r2.geojson`,
   bounds, `mcc: true`, 10,000 draws, seed 42) and a
   `summary.tile_classification.confusion` block. The tile-swap rebuild is a
   one-liner over them, which is how § 4.1 ran.
2. **One of the two cited sign-swap artefacts is not a sign-swap.** The
   `pairwise` table of `final_board_50m.json` states its own instrument as
   "round-robin tile-swap micro-F1 permutation (10000, seed 42) + BH q=0.05 +
   greedy-clique tiers (the GS chain)". And `scripts/gemini37_arm_ladder.py`
   carries **no permutation test at all** — it writes rung oracles and a sweep
   CSV, nothing inferential.

So the instruments actually registered over these ladders are:

| instrument | coverage | committed F1 gate | reference |
|---|---|---|---|
| board round-robin tile-swap (`final_board_build.py`, the GS chain) | all 7 × every pair asked about, 8,541 tiles | yes, for all 25 pairs | materialised `best-available-gt-55maps-r2.geojson` (or the standardised sibling) |
| per-map paired sign-swap (`scripts/stride55_ladder.py`, bet P7) | 2 of 7 ladders (Gemini-3 stride A, B), 1 pair each as committed (N = 5 vs N = 10), 55 map sheets | yes, for those 2 pairs | in-process extended GT: student references + adjudicated phantoms gated at 50 m |

They are not interchangeable: the sign-swap's rung F1 values (0.8186 / 0.8274 /
0.8322 on stride A, `results/stride55-2026-08-27/ladder.json`) differ from the
board cells' (0.8227 / 0.8321 / 0.8383) because the references differ. **Both are
therefore reported**: § 4.1 of the findings under the board instrument for all
eight ladders, and § 4.2 under the sign-swap, extended to the same pair set and
to tile-MCC, for the two ladders where it is registered
(`mcc-test/sign-swap/ladder_pairs.json`). The ruling remains the PI's.

**Its gate passed, to ten decimal places.** The sign-swap rebuild reproduced the
committed K = 10 unions (38,713 and 57,482 candidates, votes identical, max
centroid drift 0.069 m), the committed primary F1 to 1e-6, each rung's committed
oracle corrected-F1 to 1e-6, and **all four committed `p7_saturation` F1 results
exactly** — stride A carried −0.0003664980 / p = 0.8239 and oracle −0.0039847569
/ p = 0.0131; stride B carried +0.0015610879 / p = 0.3243 and oracle
−0.0053391701 / p = 0.0003, matching
`results/stride55-2026-08-27/ladder.json` in every digit.

**What the ruling would change: on MCC, nothing.** Across the eight pairs both
instruments cover, **all eight tile-MCC significance calls agree** — the same two
separate (stride A's K = 3 → 5 fall, −0.0111 board / −0.0105 sign-swap, and its
K = 5 → 10 rise, +0.0047 on both) and the same six do not, with ΔMCC estimates
agreeing to 0.0006 or better. **One F1 call differs**: stride A's K = 3 → 5 step
is significant on the board tile-swap (+0.0062, BH p = 0.0079) and not on the
sign-swap (+0.0048, BH p = 0.0655) — unsurprising, since 55 map sheets are far
fewer pairing units than 8,541 tiles and the references differ. So the
instrument question is live for marginal **F1** claims and **immaterial to the
MCC conclusion this report is about**. Full comparison table: findings § 4.2.

## 5. The Pareto tile-MCC column

`pass-budget-pareto-v2` (`results/verifier-robustness/pareto/pareto_v2.json`;
script `scripts/build_pareto_v2.py`, extended not rewritten; findings home
`results/verifier-robustness/verifier-robustness-findings.md` § 15).

**Gate.** Each rung declares the registered condition it is; the script refuses
to proceed unless that condition is a member of the row's
`conditions_compared` **and** its `detections` path in
`results/run-conditions.json` is the geojson this board scores. The MCC is then
read from that condition's committed `evaluation.json` and re-derived from the
same geojson through the house per-tile classification, cell-for-cell against
the record. **All seven pass exactly.**

**Before → after.**

| | before | after |
|---|---|---|
| § 15 table | F1@20 m, cost, frontier | + **tile-MCC** column, + MCC-frontier column |
| `pareto_v2.png` | one panel (cost × F1) | two panels: (a) cost × F1@20 m, (b) cost × tile-MCC |
| F1-efficient set | `min6, min11, high31, high35` | **unchanged** |
| MCC-efficient set | — | **`min6, min11`** |
| statistical separation | F1: 0/21 pairs, one tier | unchanged; **MCC: 0/21 pairs, one tier** |

| rung | F1@20 m | tile-MCC | GS run | F1 frontier | MCC frontier |
|---|---:|---:|---:|---|---|
| min6 | 0.8784 | 0.7903 | $2.43 | ✓ | ✓ |
| min11 | 0.8835 | **0.8068** | $4.00 | ✓ | ✓ |
| high6 | 0.8641 | 0.7693 | $14.04 | dominated | dominated |
| high5+5vf | 0.8739 | 0.7713 | $14.41 | dominated | dominated |
| high11 | 0.8769 | 0.7903 | $26.97 | dominated | dominated |
| high31 (headline) | 0.8902 | 0.7903 | $69.21 | ✓ | **dominated** |
| high35 (opmax) | **0.8951** | 0.7941 | $71.23 | ✓ | **dominated** |

**The finding.** **min11, at $4.00, has the highest tile-MCC of all seven rungs
(0.8068)** — above high35's 0.7941 at $71.23, a 17.8× cost ratio — and min11's MCC
lead over high35 (+0.0127) is larger than high35's F1 lead over min11 (+0.0116).
Read on tile discrimination rather than point localisation, the $67.23 of extra
GS spend between min11 and high35 buys nothing measurable.

**Two qualifications, in the document body.** (a) **Nothing separates**: 0/21 MCC
pairs significant, the same one-tier verdict as F1, so the MCC frontier is a
point-estimate ordering on one tier exactly as the F1 frontier is. (b) **The
487-tile frame is coarse enough to tie**: `min6`, `high11` and `high31` share
one *identical* tile confusion (188 TP / 247 TN / 11 FP / 41 FN) and therefore
one MCC of 0.7903, despite F1s spanning 0.8769–0.8902 and GS costs spanning
$2.43–$69.21. Not an error — the gate recomputed all three from their own
geojsons and reproduced the recorded cells exactly — but it is why a tile-level
metric on 487 tiles cannot be asked to rank fine-grained rungs.

### 5.1 Proposed amendment to the SIGNED analysis row — for the PI to rule on

The signed row was **not** altered: `pass-budget-pareto-v2`'s `outcome`,
`conditions_compared`, `tie_set` and `manually_verified_at`
(`2026-06-12T06:59:01Z`) are byte-unchanged in `results/run-analyses.json`. The
text below is proposed for appending to that row's `outcome`, in the bracketed
revision style the row already uses, if the PI agrees:

> [AMENDED 2026-09-12, tile-MCC column added per PI ruling: the board now
> carries tile-level MCC beside F1@20 m on the same Era-2 487-tile frame, and
> the MCC-efficient set is **NOT** the F1-efficient set. F1-efficient is
> unchanged — min6 $2.43/0.8784, min11 $4.00/0.8835, high31 $69.21/0.8902,
> high35 $71.23/0.8951 — but **MCC-efficient is min6 ($2.43/0.7903) and min11
> ($4.00/0.8068) alone**: both HIGH rungs on the F1 frontier are MCC-dominated,
> and min11 is the MCC maximum of all seven rungs, 0.0127 above high35's 0.7941
> at 5.6 % of its cost. The one-tier verdict extends to the new metric:
> the C(7,2) round-robin on tile-MCC (10,000 permutations, seed 42, identical
> swap masks to the F1 test, BH q = 0.05) returns 0/21 significant, so the
> MCC-efficient set is a point-estimate ordering on a single tier, exactly as the
> F1 set is, and neither licenses a separation claim. Two caveats belong with
> it: tile-MCC is buffer-invariant here, so this column is not a second reading
> of the 20 m buffer but a different question; and on 487 tiles min6, high11 and
> high31 share one identical tile confusion (188/247/11/41), so the metric
> cannot rank fine-grained rungs on this frame. The practical consequence is
> narrow but real — nothing in the cost range above min11 can be shown to buy
> tile-level discrimination, which strengthens rather than weakens the existing
> "extra spend cannot be shown to buy F1 on this instrument" reading. Artefacts:
> results/verifier-robustness/pareto/pareto_v2.{json,png}; script
> scripts/build_pareto_v2.py.]

## 6. What did NOT change

- **Every committed metric.** No F1, MCC, cost, `n_detections` or confusion
  figure anywhere was recomputed into a different value; the 55-map F1 side of
  this run is a bit-level reproduction of committed board numbers (§ 1).
- **The signed Pareto row.** `outcome`, counts, `tie_set` and signature
  untouched; the amendment above is a proposal, not an edit.
- **The F1 tiering and the F1-efficient set** of `pass-budget-pareto-v2`
  (0/21 pairs, one tier; `min6, min11, high31, high35`).
- **The K-ladder tables of §§ 2–5**, the ladder shape and its frame-invariance,
  and § 4's mechanism account, which the test is consistent with.
- **The PI's open ruling** on the 55-map instrument (§ 4).
- **The register.** `results/run-conditions.json` and
  `results/run-analyses.json` are unmodified; the per-ladder analysis rows this
  run needed are local tiering INPUTS under
  `mcc-test/tiering-input/<ladder>/run-analyses.json`, clearly marked NOT
  REGISTERED.
- **The committed 2026-08-27 stride55 artefacts.** The sign-swap re-run writes
  under `mcc-test/sign-swap/` via `--output-dir`; `results/stride55-2026-08-27/`
  is untouched.

## 7. Still outstanding

- **The Hsu MCB admissible sets** per ladder family (`findings.md` § 6.1) — a
  different instrument (`scripts/selection_aware_intervals.py`), not run.
- **The K-ladder analysis row** (`findings.md` § 6.2), which waits on those.
- **The `pv-diag-384` Phase-2 ladders** (`findings.md` § 6.3).
- **The PI's instrument ruling** for the seven 55-map ladders (§ 4 above).
- **The PI's ruling** on the proposed Pareto amendment (§ 5.1 above).

## 8. Verification

```text
ruff check scripts/{era1_leaderboard_tiering,pairwise_permutation_test,\
stride55_ladder,stride55_sweep_oracle,k_ladder_mcc_test,build_pareto_v2}.py \
  tests/test_k_ladder_mcc_instruments.py          # All checks passed!
npx markdownlint-cli2 results/k-ladder-2026-09-12/findings.md \
  results/verifier-robustness/verifier-robustness-findings.md \
  reports/k-ladder-mcc-test-2026-09-12.md         # Summary: 0 error(s)
python -m pytest -m tier1 -q
  2255 passed, 1 skipped, 27 deselected, 3 xfailed, 4 warnings in 177.51s
```

The tier-1 suite was run on sapphire against commit `d900ed1d5` (an isolated
worktree, so it could not collide with the other session holding sapphire's main
checkout).

New tests: `tests/test_k_ladder_mcc_instruments.py` (10 tier-1 tests). They pin
the three properties the result depends on: that the array kernel and its
GeoDataFrame wrapper agree after the refactor; that the F1 and MCC kernels draw
identical swap masks; and that a **synthetic fixture in which F1 rises while
tile-MCC falls on the same pair** — the exact shape of the finding under test —
is handled with correct, independent signs on both statistics, for the tile-swap
and the per-map sign-swap alike.

## Changelog

### 2026-09-12 — Original publication

Written at the close of the K-ladder § 4.1 campaign. Records: the gate result
(25/25 committed board F1 p-values reproduced; the gold standard's
harness-internal gate); the eight-ladder ΔF1/ΔMCC table; the two corrections to
`findings.md` § 6.1; the Pareto tile-MCC before→after with the MCC-efficient set
`min6, min11` against the F1 set `min6, min11, high31, high35`; and the proposed
amendment text for the signed `pass-budget-pareto-v2` row, which was NOT applied.

Commits: `156bddf36` (instrument extensions + tier-1 tests), `d10137595`
(the test result and `findings.md` § 4.1), `605def6d2` (the Pareto MCC column),
`d900ed1d5` (the sign-swap cross-check and `findings.md` § 4.2), and the commit
that lands this report.
