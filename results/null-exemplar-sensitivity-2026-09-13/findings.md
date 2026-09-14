# The null-exemplar leak: how much of the Gold-Standard boards moves when the leaked tiles come out

> **Last revised**: 2026-09-13 (original publication). See [§ Changelog](#changelog) for revision history.

Three "null" (empty) exemplar tiles in the few-shot library
(`inputs/examples/null-tiles/`) were never excluded from the Gold-Standard
evaluation frames. Every configuration that transmitted the example **images**
therefore showed the model those pixels labelled "no mounds here" and was then
scored on them. This is a sensitivity analysis **beside** the boards: nothing
under `results/leaderboard/**` is modified, and every "after" number below
comes from this directory's own re-scores.

**The short answer, in three parts.**

1. **The leak is real and it is measurable where it must show up first.**
   On the Era-2 board, image-bearing cells suppress false positives on the
   leaked tiles about a fifth more than text controls do — FP-rate ratio
   0.561 against
   0.685 — and the contrast
   survives restriction to a single run, at
   p < 0.0001.
2. **No cell's published number moves more than a hundredth.** The largest
   movement of any Era-2 cell is 0.0074 in F1@20 and 0.0120 in tile-MCC,
   and the reduction costs the image cells *less* than the text controls,
   not more, because the leaked tiles hold 12 of the frame's 435 reference
   mounds as well as the quiet ground.
3. **The tie sets do move at their edges, and that is worth disclosing.**
   F1 Tier 1 goes from five cells to four — the cell it loses is a *text*
   cell — the F1 tier count from 14 to 13, tile-MCC Tier 1 from 33 cells
   to 28, and the two Hsu admissible sets by one and two members. The top
   of both rankings, and the selection-aware winner under both metrics,
   are unchanged.

## The leak, established at the byte level

The mechanism was verified rather than assumed:

- `inputs/examples/neutral-naming/example_15.png`, `example_16.png` and
  `example_17.png` are SHA-256-identical to `null_lesovo.png`,
  `null_elenovo.png` and `null_32635.png`, and carry `"category": "null"`
  in every proposer config's example list.
- `include_example_images` defaults to **true** in the pipeline
  (`scripts/4_detect_mounds_batch.py:885`), so a config without the key
  sent the images. A text-only config sets it false and sent the labels
  only.
- No `verify_*.json` config carries a null-category example — all eight
  have zero — so the verifier stage never transmitted the pixels. A cell
  whose `-image`/`-text` suffix names its *verifier* is therefore
  classified by its *proposer*.
- No reference mound lies inside any of the three null windows (0, 0, 0
  against `inputs/vectors/references/mounds-reference.geojson`), so the
  leak can only have suppressed **false positives**.

### The exposed tiles

Computed from the tile windows here rather than imported
(`scripts/compute_null_exemplar_overlap.py`; record in `overlap_tiles.json`). A
tile name encodes its window's top-left pixel offset on a named sheet, and
exposure is a property of the window the model was shown — not of the
sometimes-clipped polygon the scorer credits detections inside — so the test is
an axis-aligned window overlap in pixel space. That is exact because one
resolution and one origin fit all 85 tiles of each sheet in the 512 px frame,
and every tile of every frame under test is either exactly its nominal window
under that same affine or a clipped subset of it; both are asserted at run time
and each verdict is cross-checked in ground space.

| frame | tiles | exposed | reduced | leaked share of an exposed tile (mean / median / max) | references in the exposed tiles |
|---|---:|---:|---:|---:|---:|
| `era2-b-487` (384 px, 336 px step) | 487 | **20** | 467 | 0.281 / 0.191 / 1.000 | 12 of 435 |
| `era1-full-340` (512 px, 448 px step) | 340 | **25** | 315 | 0.186 / 0.125 / 1.000 | 52 of 539 |

The two sets are exposed very differently, and the exposure depth is the
difference. The three null windows are themselves members of the 340-tile frame
— 3 of that frame's 25 exposed tiles ARE a null window — and every other tile
in the Era-1 set merely clips one. Its leaked shares run 10 at 1.6%, 12 at
12.5%, 3 at 100.0%: the 448 px stride leaves a diagonal neighbour a
sixty-fourth exposed and an edge neighbour an eighth, and nothing in between.
The Era-2 set, cut at 384 px on a 336 px step inside a 512 px window, is spread
from 2.1 % to 45.8 % with 2 tiles lying entirely inside a null window.

### The cells

Exposure is decided per cell from the proposer pool's **run metadata**
(`include_example_images`, and whether the config snapshot carries a
null-category example), cross-checked against the register's
`proposer_pools[...].modality` and, where the pool key names one, the config
file. Wherever two sources are both observable they agree exactly, and no
cell's sources disagree (`cell_inventory.json`).

| board | frame | cells in frame | image-bearing | text control |
|---|---|---:|---:|---:|
| `gs-era2-verified-board-2026-09-10` | `era2-b-487` | 153 | 59 | 94 |
| `era1-leaderboard` | `era1-full-340` | 82 | 38 | 44 |
| `era1-single-pass-baseline-matrix` | `era1-full-340` | 36 | 22 | 14 |
| `tile-size-sweep`, 512 px leg | `era1-full-340` | 16 | 7 | 9 |

Seven Era-2 cells come out differently from the board's own `track` field. The
three `proposer-verifier-384::verified-{adversarial,brief,checklist}-image`
cells carry `track: image`, but that names their image *verifier* over a
`detect_brief-text` proposer with `include_example_images: false` — no pixels
went out, so they are text controls here. The four
`pv-diag-384::pv-scale4-optimal-n{1,3}-*` cells carry `track: text`, but their
run metadata records the proposer config `detect_h8_scale-4_v2` with
`include_example_images: true` and three null examples — they are
image-bearing, and two of them sit in the board's tile-MCC Tier 1. Nothing on
the board was changed; the divergence is reported.

## The leak signature: false positives on the leaked tiles

This is the test that has to come first. No reference mound lies in the three
null windows, so the leak can only have suppressed **false positives** on the
exposed tiles, and only for cells whose proposer sent the images. The statistic
is each cell's own within-frame contrast — its false-positive rate on the
exposed tiles against its rate on the rest of the same frame,

    r = log((FP_exposed / n_exposed + 0.5) / (FP_rest / n_rest + 0.5))

— so a cell is compared with itself before image cells are compared with text
ones, and a cell that simply makes more false positives everywhere does not
register. The reference distribution is a 10,000-draw permutation of the
image/text labels across cells (seed 42), exact under the null that exposure
changes nothing. A NEGATIVE image-minus-text difference is the leak's
signature.

| board | exposed / rest tiles | image / text cells | FP per tile, image (exposed → rest) | ratio | FP per tile, text (exposed → rest) | ratio | mean r, image | mean r, text | image − text | p (image lower) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `gs-era2-verified-board-2026-09-10` | 20 / 467 | 59 / 91 | 0.121 → 0.216 | 0.561 | 0.070 → 0.103 | 0.685 | -0.1433 | -0.0552 | **-0.0881** | **< 0.0001** |
| `era1-leaderboard` | 25 / 315 | 38 / 44 | 0.721 → 0.903 | 0.798 | 0.647 → 0.798 | 0.811 | -0.1717 | -0.1645 | **-0.0072** | **0.4224** |
| `era1-single-pass-baseline-matrix` | 25 / 315 | 22 / 14 | 1.065 → 1.205 | 0.884 | 1.304 → 1.431 | 0.911 | -0.0912 | -0.0868 | **-0.0045** | **0.4493** |
| `tile-size-sweep`, 512 px leg | 25 / 315 | 7 / 9 | 0.663 → 0.877 | 0.756 | 0.484 → 0.627 | 0.772 | -0.2007 | -0.1562 | **-0.0445** | **0.2542** |

**The Era-2 board carries the signature and the other three boards do not.** On
the Era-2 board an image-bearing cell's false-positive rate on the exposed
tiles is 0.561 times its rate on the other 467 tiles, while a text control's is
0.685 times its own — the image cells suppress false positives on the leaked
ground about a fifth more than the controls do, and the per-cell contrast is
-0.0881 in log ratio at p < 0.0001. Both groups suppress: the null exemplars
were selected as *empty* tiles, so the ground they sit on is quiet for
everyone. The leak is the **difference** between the two suppressions, and only
the image cells could have seen the pixels.

**It is not a between-run confound.** Image and text cells differ in more than
example images — model, thinking level, verifier, pipeline — so the test was
re-run stratified by run, permuting the labels only within a run. On the Era-2
board the comparison lives almost entirely inside one run: `pv-diag-384`
supplies 54 image and 61 text cells from the same pipeline, and there the
difference is -0.0773 at p < 0.0001. Where image and text cells differ only in
whether the pixels went out, the signature is still there.

On the Era-1 boards the unstratified test is null. Stratifying by run lifts it
without settling it: `era1-leaderboard` -0.0705 at p 0.0208;
`era1-single-pass-baseline-matrix` -0.0514 at p 0.1201; the sweep's 512 px leg
-0.0913 at p 0.1493.

## Per-cell before → after: F1@20 and tile-MCC

Every cell of every board was re-scored on its reduced frame with the board's
own recipe. The full per-cell table is `analysis.json` (`per_cell[].cells`);
the distribution of the change is what matters here.

| board | metric | group | n | mean Δ | median Δ | range | largest \|Δ\| (cell) |
|---|---|---|---:|---:|---:|---|---|
| `gs-era2-verified-board-2026-09-10` | F1@20 | image | 59 | -0.00213 | -0.00290 | [-0.00680, +0.00480] | -0.00680 (`g384-ov192-image-high-k10-verified-p0.20-k8-era2b`) |
| `gs-era2-verified-board-2026-09-10` | F1@20 | text | 94 | -0.00275 | -0.00245 | [-0.00740, +0.00360] | -0.00740 (`g37-text-k1-verified-opmax`) |
| `gs-era2-verified-board-2026-09-10` | tile-MCC | image | 59 | -0.00126 | -0.00220 | [-0.00700, +0.01100] | +0.01100 (`pv-min-image-t0.3-n1-opmax`) |
| `gs-era2-verified-board-2026-09-10` | tile-MCC | text | 91 | -0.00286 | -0.00350 | [-0.01200, +0.00640] | -0.01200 (`verified-checklist-text-era2b`) |
| `era1-leaderboard` | F1@20 | image | 38 | -0.01458 | -0.01200 | [-0.02600, +0.00020] | -0.02600 (`image-t0.3-n5-4of5`) |
| `era1-leaderboard` | F1@20 | text | 44 | -0.02120 | -0.02600 | [-0.03300, -0.00460] | -0.03300 (`text-minimal-t0.7-n10-8of10`) |
| `era1-leaderboard` | tile-MCC | image | 37 | -0.02433 | -0.02320 | [-0.06560, +0.00860] | -0.06560 (`image-t0.3-n5-4of5`) |
| `era1-leaderboard` | tile-MCC | text | 35 | -0.03777 | -0.03820 | [-0.10100, +0.00450] | -0.10100 (`text-high-t0.7-n5-4of5`) |
| `era1-single-pass-baseline-matrix` | F1@20 | image | 22 | -0.00911 | -0.00925 | [-0.01500, +0.00020] | -0.01500 (`image-pure-positive-canon`) |
| `era1-single-pass-baseline-matrix` | F1@20 | text | 14 | -0.00885 | -0.00985 | [-0.01190, -0.00460] | -0.01190 (`text-plus-hp`) |
| `era1-single-pass-baseline-matrix` | tile-MCC | image | 21 | -0.01327 | -0.01140 | [-0.03790, +0.00860] | -0.03790 (`config-default`) |
| `era1-single-pass-baseline-matrix` | tile-MCC | text | 5 | +0.00450 | +0.00450 | [+0.00450, +0.00450] | +0.00450 (`brief-text`) |
| `tile-size-sweep`, 512 px leg | F1@20 | image | 7 | -0.01556 | -0.00950 | [-0.02490, -0.00850] | -0.02490 (`image-t0.7-n30-18of30`) |
| `tile-size-sweep`, 512 px leg | F1@20 | text | 9 | -0.02228 | -0.02580 | [-0.03080, -0.00740] | -0.03080 (`text-minimal-t0.7-n30-25of30`) |
| `tile-size-sweep`, 512 px leg | tile-MCC | image | 7 | -0.03027 | -0.03430 | [-0.05170, -0.00700] | -0.05170 (`image-t0.3-n30-22of30`) |
| `tile-size-sweep`, 512 px leg | tile-MCC | text | 7 | -0.04560 | -0.04550 | [-0.06790, -0.01940] | -0.06790 (`text-t0.3-n30-23of30`) |

**On the Era-2 board the reduction is worth thousandths.** The largest movement
of any cell's headline F1@20 is 0.0074 and of any cell's tile-MCC 0.0120,
against tier separations an order of magnitude larger. Image cells lose a mean
0.00213 of F1 and text cells 0.00275: the reduction costs the image cells
**less**, not more (+0.00062 in mean ΔF1, +0.00160 in mean ΔMCC). That is the
opposite of what a leak inflating image scores would predict, and it has a
plain cause: the exposed tiles hold 12 of the frame's 435 reference mounds, so
dropping them removes positives as well as the quiet ground, and the two
effects nearly cancel.

The Era-1 boards move about an order of magnitude more — mean ΔF1 around −0.015
to −0.021, mean ΔMCC around −0.024 to −0.038 — because their reduction drops 25
of 340 tiles carrying 52 of 539 references, 9.6 % of the positives against 2.8
% on the Era-2 frame. That is a frame effect every cell on the board shares,
which is exactly why the text controls are the reference and not zero.

## The paired tile-swap, full frame against reduced frame

Each image-bearing cell was paired with the text control nearest to it in
full-frame F1@20 — a pairing fixed **before** the reduction, so it cannot be
chosen by the result it produces — and the board's round-robin tile-swap
permutation (10,000 draws, seed 42) was run on the pair twice: on the full
frame and on the reduced one.

| board | pairs | mean ΔF1 (image − text), full → reduced | mean ΔMCC, full → reduced | F1 verdict flips at α = 0.05 | MCC flips |
|---|---:|---:|---:|---:|---:|
| `gs-era2-verified-board-2026-09-10` | 59 | -0.00802 → -0.01102 | +0.08482 → +0.08519 | 5 | 1 |
| `era1-leaderboard` | 38 | -0.00283 → -0.00106 | +0.17687 → +0.17282 | 0 | 0 |
| `era1-single-pass-baseline-matrix` | 22 | -0.00360 → -0.00558 | — → — | 0 | 0 |
| `tile-size-sweep`, 512 px leg | 7 | -0.00683 → -0.00512 | +0.11246 → +0.13223 | 0 | 0 |

Every verdict that flips does so across α from just above to just below — the
largest move is a p-value from 0.0600 to 0.0309 — with the pair's difference
growing slightly rather than reversing. No pair changes sign. The flips are
listed in `analysis.json` (`paired_tile_swap_flips`).

## The Era-2 board rebuilt on the reduced frame

The board's own instruments, pointed at register overrides so the board's files
are read and never written.

| quantity | full frame (487 tiles) | reduced frame (467 tiles) |
|---|---:|---:|
| cells tiered | 150 | 150 |
| cells withheld by the tile-join invariant | 3 | 3 |
| pairs significant (BH q = 0.05, of 11,175) | 7961 | 7905 |
| **F1 tiers** | **14** | **13** |
| F1 tie set | 5 | 4 |
| cells whose F1 tier *label* changes (see note) | — | 130 |
| cells moving by more than one F1 tier | — | **2** |
| F1 Hsu MCB admissible | 65 | 66 |
| tile-MCC pairs significant | 2982 | 3118 |
| **tile-MCC tiers** | **6** | **7** |
| tile-MCC tie set | 33 | 28 |
| cells changing tile-MCC tier | — | 28 |
| tile-MCC Hsu MCB admissible | 59 | 57 |

**Things do move, at the tie-set boundaries.** The answer to the PI's question
is not "nothing changed":

- **F1 Tier 1 loses one member** (5 → 4): `g37-text-k10-verified-carried-p0.10-k10-era2b` — a **text** cell — drops to Tier 2.
  Both image cells in Tier 1 stay, as do the other two text cells. The
  demoted cell is the one whose F1@20 fell furthest of the five
  (−0.0066, to 0.9002), and the cell at rank 5 (0.9013) passed it.
- **The F1 tier count falls 14 → 13** and 7961 → 7905 pairs are significant: 20 fewer tiles
  is a little less power, and a tier boundary merges.
- **tile-MCC Tier 1 loses 7 and gains 2** (33 → 28 cells), and the MCC tier count rises 6 → 7 on 2982 → 3118 significant
  pairs. **Every cell that leaves and every cell that joins is an image
  cell** — the family is image-dominated at the top either way.
- **The Hsu admissible sets move by a member or two**: F1 65 → 66 (1 admitted, 0 dropped, 65 carried over); tile-MCC 59 → 57 (0 admitted, 2 dropped, 57 carried over). The two dropped from the
  tile-MCC set are text cells; the one added to the F1 set is an image
  cell.

These are boundary effects, not a re-ordering. A tie set is a clique of cells a
permutation test cannot separate, so its edge is exactly where a 4 % change in
the resampling unit should show up, and a tier *label* moves for 130 of 150
cells simply because the tier count changed. What the ranks say is that the
board is the same board: Spearman correlation 0.9989 between the two rankings,
largest rank shift 8 places, 13 cells moving more than three places, and only 2
cells moving by more than one tier.

### What did NOT change

- **The top of the F1 board.** Ranks 1–4 are the same four cells in the
  same order, each losing 0.005–0.007 of F1@20 — image and text alike —
  and the leading cell is still the Gemini 3.7 image cell.
- **The top of the tile-MCC ranking.** Ranks 1–7 are the same seven cells
  in the same order, their MCC moving by at most 0.0035, three of the
  seven upwards.
- **The selection-aware winner** under both metrics: the same argmax cell
  on the reduced frame as on the full one.
- **The withholding**: the same three cells, refused by the tile-join
  invariant for the same reason on both frames.
- **Every Era-1 board's paired tile-swap verdict**: zero flips.

## Verdict: do Obs 482 and the 3.7 image Tier-1 placement need a qualifier?

**Both claims survive, and what they need is a one-sentence disclosure of the
leak with its measured size, not a qualifier on the finding.**

Obs 482's reading — that tile-MCC is led by single-pass image proposer-verifier
baselines while the F1 board is led by Gemini 3.7 consensus cells — is the
claim most exposed to this leak, because the leak's only possible effect is to
suppress false positives, and a suppressed false positive is precisely what
lifts a tile-level metric by keeping an empty tile empty. The measurement says
the leak did do that and did not do nearly enough to carry the claim. Across
the 59 image cells of the Era-2 board paired against their nearest text
comparators, the image-over-text tile-MCC advantage is +0.0848 on the full
frame and +0.0852 on the reduced one — a change of +0.0004, under half a
percent of the advantage itself. The seven cells at the head of the tile-MCC
ranking are the same seven in the same order on both frames, their MCC moving
by at most 0.0035 and three of the seven **upwards**; the top three shed one or
fewer false positives each across all 20 leaked tiles (13 → 12, 16 → 15, 17 →
16). tile-MCC Tier 1 does shrink, from 33 cells to 28, but the seven that leave
and the two that join are all image cells and none is among the leaders: the
tie set tightens, it does not change character.

The 3.7 image Tier-1 placement also holds.
`g37-image-k5-verified-swap37-p0.90-k5` keeps rank 1 and Tier 1, losing 0.0062
of F1@20 while the two 3.7 text cells immediately behind it lose 0.0052 each,
so its lead narrows by 0.0010 and its ordering is unchanged. The one real
movement at the top is on the **text** side: F1 Tier 1 goes from five cells to
four because `g37-text-k10-verified-carried-p0.10-k10` falls out of the tie
set. Removing the leaked tiles therefore demotes a text cell and leaves both
image cells in place — the opposite of what a leak inflating image scores would
do.

So the disclosure to carry is: three empty exemplar tiles leaked into 20 of the
Era-2 frame's 487 tiles, and image-bearing cells measurably suppressed false
positives on that ground — an FP-rate ratio of 0.56 against the text controls'
0.68, within a single run, at p < 0.0001 — but removing those tiles moves no
cell's headline F1@20 by more than 0.0074 or its tile-MCC by more than 0.0120,
leaves the top of both rankings in place, and costs the image cells less than
the text controls rather than more.

Three caveats belong with that. First, the tie sets DO move at their edges — F1
Tier 1 5 → 4, tile-MCC Tier 1 33 → 28, the Hsu sets by one and two — so any
text that quotes a tie-set *size* is frame-specific and should say so. Second,
the Era-1 boards show no signature unstratified and a weak, heterogeneous one
stratified by run (one run strongly negative, one positive), which is
consistent with their exposed tiles being shallower — mean leaked share 0.186
against 0.281 — but is not established by this analysis; their reduction is
dominated by its much larger frame effect either way. Third, the signature test
remains a between-cell contrast even stratified: it establishes that cells
which sent the pixels behave differently on the leaked ground, not that any
individual cell's published number is wrong by a stated amount. The per-cell
re-scores answer that question, and they answer it in thousandths.

## Method

- **Recipe.** The board's own: curator reference
  `inputs/vectors/references/mounds-reference.geojson`, 14 buffers
  (5–150 m), headline 20 m, 10,000 BCa bootstrap, seed 42, tile-MCC
  through the name-based (`id`) tile join with the withhold-not-abort
  invariant, via `scripts/evaluate_detections.py`. The Era-2 tiering, its
  Hsu MCB sets and the tile-MCC family are rebuilt by the board's own
  instruments (`scripts/era1_leaderboard_tiering.py --permute-mcc`,
  `scripts/selection_aware_intervals.py --board`, 10,000 draws, seed 42,
  Benjamini–Hochberg q = 0.05 per family, greedy clique) pointed at
  register **overrides** in `tiering-input/`, so the board's files are
  read and never written.
- **The reduction removes the tiles AND what the model said about them.**
  Excluding a tile from the evaluation must also exclude the predictions
  made from it: those came from the contaminated prompt. Nor is this
  optional book-keeping. The published `id` join books a detection by its
  `source_tile` string, so a detection reported from a dropped tile but
  lying inside a retained one has no frame tile to be credited to, and
  the shortfall invariant refuses the cell's whole per-tile table — the
  first reduced-frame score attempted here was refused for exactly that
  reason, 6 of 364 in-frame detections unbooked. Filtering restores the
  invariant by construction and is the correct counterfactual. Where a
  file carries no `source_tile`, the booking tile is back-filled by the
  same spatial join `evaluate_detections.py` uses, so the filter matches
  the scorer's own rule.
- **Cell shape is preserved.** A replicate-mean cell is the per-tile mean
  over its pass files and a single-set cell is one set, so the filtered
  tree mirrors the source layout and both readers keep the committed
  shape. Collapsing a replicate-mean cell into a union produced apparent
  between-frame deltas of up to 0.33 in F1 in a first pass — impossible
  from dropping 25 of 340 tiles, and the tell that the statistic rather
  than the frame had changed.
- **Artefacts.** `overlap_tiles.json`, `cell_inventory.json`,
  `detections_manifest.json`, `leak_signature.json`,
  `paired_tile_swap.json`, `analysis.json`, per-cell evaluations under
  `cells/<frame>/<cell>/`, the reduced tiering under `tiering-reduced/`,
  the MCB artefacts under `mcb-reduced/`, and the reduced frames under
  `bounds/`. The filtered detection copies are gitignored: they are a
  deterministic function of committed inputs and
  `scripts/analyse_null_exemplar_sensitivity.py --stage filter`, and
  every per-file feature count is recorded in
  `detections_manifest.json`. This document is rendered from the
  artefacts by `scripts/render_null_exemplar_findings.py`, so its numbers
  cannot drift from them.

## Changelog

### 2026-09-13 — Original publication

First measurement of the null-exemplar leak's effect on the Gold-Standard
boards, on the PI's ruling of 2026-09-13. Establishes the leak mechanism at the
byte level; computes the exposed tile sets for both frames (20 of 487 and 25 of
340); classifies every board cell by whether its proposer transmitted the null
images; runs the leak-signature test on the full frames, stratified and
unstratified; re-scores every cell on the reduced frames; re-runs the paired
tile-swap on both frames; and rebuilds the Era-2 F1 tiering, both Hsu MCB sets
and the tile-MCC permutation family on the reduced frame. No prior revision to
diff against. **Unsigned** — registered as
`null-exemplar-sensitivity-2026-09-13` (type comparison, post-hoc) pending the
PI's reading.
