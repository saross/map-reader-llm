# Re-scoring the four cells the recovery-fragment fix touched

> **Last revised**: 2026-09-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

The recovery-fragment fix (`75d7c8d4cd55b6ec8d2a40abff70a31f62b67725`) rebuilt
five committed consensus unions. Four registered conditions read them. This
directory holds the measurement that settles what moved.

**Headline: three of the four are unchanged at the headline buffer, and the
fourth moves by −0.0010.** The whole numerical consequence of the defect, across
the repository, is one false-positive detection.

## The four cells, before → after

Measured at 20 m on the board frame `era2_b_intersection_bounds.geojson`, against
the curator reference, with the Hungarian one-to-one matching the corpus uses
(`lib_advanced_metrics.calculate_f1_internal`):

| condition | F1@20 before | after | Δ | detections | Δ det |
|---|---:|---:|---:|---|---:|
| `gemini37-screen-2026-08-28::g37-text-k1-verified-opmax` | 0.8495 | **0.8495** | 0.0000 | 502 → 502 | 0 |
| `gemini37-screen-2026-08-28::g37-text-k1-verified-carried-p0.10-k1` | 0.8338 | **0.8338** | 0.0000 | 558 → 558 | 0 |
| `gemini37-screen-2026-08-28::g37-text-k3-verified-opmax` | 0.8870 | **0.8860** | **−0.0010** | 494 → **495** | **+1** |
| `grid-2026-08-18::g384-ov192-k5-verified-opmax` | 0.8905 | **0.8905** | 0.0000 | 435 → 435 | 0 |

**Every "before" figure in that table was re-derived here, in the same process as
its "after", and reproduces the committed value exactly** (0.8495, 0.8338, 0.8870,
0.8905). That matters: it rules out the alternative explanation that a difference
came from the scorer changing between 2026-09-12 and now rather than from the
detections changing.

The operating point held in all four cases — no argmax migrated, 0 ties, and the
board frame and the Era-2 frame still agree on every one
(`operating-points.json`).

### The one movement, decomposed

`g37-text-k3-verified-opmax` gains exactly one detection: `candidate_00049` at
(25.865733, 42.441604), source tile `K-35-052-4_32635_x1920_y960.png`, which the
recovery fragment promoted from 2 votes to 3 so that it clears the rung's
vote ≥ 3 gate. Its verifier probability is 1.0, so it also clears prob ≥ 0.10.

It is a **false positive**: precision falls 0.8340 → 0.8323 while recall holds at
0.9471 exactly. So a fragment whose recovery was unambiguously correct data
recovery made this cell very slightly worse — which is the honest shape of the
result and not a reason to doubt the fix.

None of the three candidates that needed a fresh verifier call enters the scored
set: all three sit at 1 or 2 votes against a vote ≥ 3 gate.

### A second movement, only at 5 m

The two K = 1 cells are unchanged at 20 m and at every buffer from 10 m up, but
both move at **5 m**:

| condition | F1@5 before | after | Δ |
|---|---:|---:|---:|
| `g37-text-k1-verified-opmax` | 0.4781 | 0.4760 | −0.0021 |
| `g37-text-k1-verified-carried-p0.10-k1` | 0.4693 | 0.4673 | −0.0020 |

Their detection counts do not change. The cause is a single candidate whose
cluster centroid moved **3.026 m** when the fragment contributed a co-located
detection — far inside a 20 m match radius, and straddling a 5 m one. Recorded
because a reader who checks only the headline buffer would conclude, wrongly,
that these two cells are untouched.

## What is in here

| path | what it is |
|---|---|
| `operating-points.json` | the chosen (vote, probability) point for each cell, the board- and Era-2-frame argmaxes, tie counts, and whether the point moved |
| `f1-only/*.json` | per-buffer precision/recall/F1 for before and after, all 14 buffers, plus the deltas and the explicit withheld block |
| `materialised/*.geojson` | the "after" detection sets, materialised at each cell's operating point |
| `reproduced-k5-evaluation/` | the tier-E cell's full re-evaluation — **dict-identical** to the committed `evaluation.json` summary |

The pre-fix evaluations are snapshotted at
`archive/superseded-consensus-2026-09-13/recovery-fragment-drop/evaluations-as-read-2026-09-13/`.

## Why three cells have an F1 arm only, and what that blocks

`scripts/evaluate_detections.py` **cannot run at HEAD** for the three
`gemini37-screen-2026-08-28` cells. The tile-join invariant
(`lib_advanced_metrics.compute_per_tile_tp_fp_fn`) refuses their per-tile table —
their proposer ran on the 192 px-stride `inputs/tiles_384_ov192` vocabulary, not
the board frame's 336 px-stride one, so only ~21 of ~475 in-frame detections book
to a frame tile. Because the F1 bootstrap resamples **tiles**, that refusal
aborts the whole evaluation, not merely the tile-MCC block. Their committed
evaluations predate the invariant (`7ba47b63b`).

So this directory reports, for those three, exactly what the invariant permits and
names what it does not:

- **reported**: precision, recall and F1 point estimates at all 14 buffers, from
  the same function `evaluate_detections.py` calls for them;
- **withheld**: every bootstrap confidence interval, and the whole per-tile
  confusion and tile-MCC block.

This is consistent with the board, which already lists these three as
`tiering.withheld_cells` and publishes only their whole-frame F1.

**The consequence the PI needs to weigh.** `g37-text-k3-verified-opmax`'s F1 has
genuinely moved, but its `evaluation.json` **cannot be regenerated** at HEAD, so
its committed evaluation — and therefore
`results/conditions-manifest.json`'s row, which carries `per_buffer["20"].f1 =
0.8870` sourced from it — could not be refreshed by this job. Correcting that
artefact is **blocked on the tile-join ruling** (`reports/tile-mcc-geometric-join-2026-09-12.md`,
still carrying a STOP). Until then the committed 0.8870 is stale by −0.0010, and
this document is the record of the true value.

The tier-E cell needed no update at all: its re-evaluation is dict-identical to
what is committed, so the committed artefact is already correct.

## How to reproduce

The drivers' own logic was reused, not restated: the operating point comes from
`score_k_ladder_phase2_rungs.argmax_at_headline`, the cell name from
`cell_dir_name`, and the tier-E carrier re-key from
`run_k_ladder_tier_e.reassign_carrier_tiles`. Only the input paths differ — the
`*_recovery-fixed` verifier stages instead of the originals. Per cell:

1. sweep the 2-D (vote, probability) grid on both frames —
   `sweep_f1_greedy_pv.py --buffer-m 20 30 40 50`;
2. take the board frame's F1@20 argmax (ruling R2), or the family's carried point;
3. materialise — `materialise_pv_geojson.py --vote-t V --prob-t P`;
4. tier E only: re-key `source_tile` to the frame's 336 px stride;
5. score — the recorded recipe: curator reference,
   `era2_b_intersection_bounds.geojson`, 14 buffers (5…150), 10,000 BCa draws,
   seed 42, `--mcc`. For the three refused cells, the F1 arm of that recipe only.

Run on sapphire, 2026-09-13, in an isolated worktree at
`~/worktrees/map-reader-llm/claude-unions`.

## Changelog

### 2026-09-13 — Original publication

Created under the PI's "fix properly" ruling of 2026-09-13. Four cells re-scored
against the rebuilt unions and the three extended verifier stages; 4 verifier
calls, US$0.002784 audited on the corpus flex basis.

| claim | before | after |
|---|---|---|
| `g37-text-k1-verified-opmax` F1@20 | 0.8495 | 0.8495 (unchanged) |
| `g37-text-k1-verified-carried-p0.10-k1` F1@20 | 0.8338 | 0.8338 (unchanged) |
| `g37-text-k3-verified-opmax` F1@20 | 0.8870 | **0.8860** |
| `g37-text-k3-verified-opmax` detections | 494 | **495** |
| `g384-ov192-k5-verified-opmax` F1@20 / tile-MCC | 0.8905 / 0.8139 | 0.8905 / 0.8139 (unchanged) |
| the two K = 1 cells' F1@**5** | 0.4781 / 0.4693 | **0.4760 / 0.4673** |

**What did NOT change**: every operating point (no argmax migrated, 0 ties,
both frames still agreeing); every detection count except K = 3's; the tier-E
cell's entire evaluation, including its BCa confidence intervals and its
193/248/10/36 confusion; the board's tiering, ranks and signatures, which the PI
ruled are picked up at the next rebuild; and the uplift supplement, whose
board-frame exclusion rule keys on `scope_override.test_set_id` and so is
unaffected.

**Flagged for the PI, not smoothed over**: (1) `g37-text-k3-verified-opmax`'s
committed `evaluation.json` and its register row cannot be refreshed until the
tile-join question is ruled on; (2) the tier-E zero delta is exact only
conditional on carrying `candidate_01335`'s 0.10 across a 1 px crop shift; (3) the
single K = 1 verifier call proved confirmatory rather than necessary, because
coverage was tested on metric distance where it should be tested on the integer
crop window. All three are set out in `reports/recovery-drop-fix-2026-09-13.md`.
