# Stage-D — Era-1 proposer-verifier (PV) findings

> **Last revised**: 2026-06-09 (initial publication — consolidates the Session 107
> PV grid (5 cells) and the Session 108 384 leg into one results narrative).
> See [§ Changelog](#changelog) for revision history.

This document is the single citable home for the **Stage-D proposer-verifier
results** of the Era-1 (Gold-Standard 4-map, curator ground truth) leaderboard
programme. Stage-D added a clean PV grid — consensus champions and clean
single-pass cells, each judged by one carry-forward adversarial verifier — to
replace the sidelined `proposer-verifier-512` cell (D1) and to close the open
256-px consensus+verifier question (Obs 351).

It draws together six verified cells produced across two sessions:

- **Session 107** (gated API run, ~$5 flex): the five 256/512-px cells.
- **Session 108** ($0, on-disk re-score): the missing **384-px** consensus+PV
  leg — see the provenance/disambiguation record in
  [`384-leg-recon.md`](384-leg-recon.md).

## 1. The carry-forward verifier (one configuration, all cells)

Every Stage-D cell was judged by the **same** verifier — the production
carry-forward — so the grid is internally comparable:

| field | value |
|---|---|
| prompt / version | `verify_adversarial-text` (`verify_adversarial.md`), text-only labels |
| model | `gemini-3-flash` |
| thinking | minimal |
| temperature | 0.0 |
| examples | none (`library_hash: no_examples`) |
| passes (n) | 1 |
| execution | realtime, flex (50%-off) |

Each cell's accepted set was materialised over a `prob_t` sweep
`[0.1, 0.15, 0.2, 0.3, 0.5]` and scored at the **14-buffer corrected-F1 +
tile-MCC** standard against the curator ground truth; the **best-F1@20 m**
operating point per cell is reported. Config: `prompts/configs/verify_adversarial-text.json`.
Orchestration: `scripts/run_era1_pv_stage_d.py`.

## 2. The Stage-D grid (F1@20 m, tile-MCC, best prob_t)

| cell | registered condition | arch | tiles | F1@20 m | tile-MCC | prob_t |
|---|---|---|---:|---:|---:|---:|
| 384-consensus-text-high | `pv-diag-384::verified-adv-text-consensus-16of30` | consensus+PV | 487 | **0.890** | 0.790 | 0.2 |
| 256-consensus-text-5of5 | `pv-diag-256::verified-adv-text-consensus-5of5` | consensus+PV | 1032 | 0.856 | 0.745 | 0.2 |
| 512-consensus-text-high | `retest-phase3a-high::verified-adv-text-high-t1.0-n30-23of30` | consensus+PV | 340 | 0.792 | 0.676 | 0.1 |
| 512-single-text-t0.0 | `retest-phase2b::verified-adv-text-t0.0` | single-pass+PV | 340 | 0.770 | 0.789 | 0.2 |
| 512-consensus-image | `retest-phase3a::verified-adv-image-t0.7-n30-18of30` | consensus+PV | 340 | 0.728 | 0.785 | 0.15 |
| 512-single-image-t0.0 | `retest-phase2b::verified-adv-image-t0.0` | single-pass+PV | 340 | 0.674 | **0.889** | 0.15 |

Source: `outputs/era1-pv-stage-d/stage_d_score_summary.json` (256/512) +
`stage_d_score_summary_384.json` (384).

**Comparability**: F1@20 m IS cross-size comparable (the three tile sizes are
different tilings of the same four Gold-Standard maps + the same curator
ground-truth mounds), so the 256/384/512 column compares directly. **tile-MCC is
NOT differenced across sizes** — the true-negative base differs with tile count
(1032 / 487 / 340), so MCC is read per cell, never subtracted across sizes. The
four 512-px cells are mutually MCC-comparable (shared 340-tile base).

## 3. Headline findings

### 3.1 Proposer-verifier is the single best Era-1 architecture

On the definitive 512-px Era-1 leaderboard (`era1-leaderboard`, 82 cells, 10
tiers), the **sole Tier-1 leader** is `512-consensus-text-high` —
HIGH-thinking text consensus + the adversarial verifier, **F1 0.792 / MCC
0.676**. The verifier lifts the bare consensus champion **0.775 → 0.792**, just
enough to break the old six-way HIGH-consensus tie (now Tier 2). No bare
single-pass or bare consensus cell reaches it.

### 3.2 Cheap single-pass+PV rivals expensive consensus

`512-single-text-t0.0` is a **MINIMAL single-pass proposer + one verifier pass —
two model calls per tile**, ~15× cheaper than the 30-pass HIGH-thinking
consensus. It reaches **Tier 2 (F1 0.770)**, matching the 30-call consensus on
F1 and **beating it on MCC (0.789 vs ~0.55–0.64)**. This echoes Obs 174/175: the
verifier substitutes cheaply for proposer-side diversity. For a deployment that
values precision/discrimination (MCC), single-pass+PV is the cost-efficient
choice.

### 3.3 The verifier lifts MCC across the board

Every PV cell carries strong tile-discrimination MCC. `512-single-image-t0.0`
posts the **board-best MCC 0.889** (at a modest F1 0.674 — the F1-vs-MCC
divergence again), and `512-consensus-image` 0.785. The verifier's pruning of
false positives is what raises MCC.

### 3.4 Tile size at consensus+PV: 384 is the sweet spot

The consensus+PV tile-size head-to-head (`tile-size-sweep` View 3) orders
**384 (0.890) > 256 (0.856) > 512 (0.792)** — **384 px leads**, the same sweet
spot it holds at consensus-only, **confirming the Obs 179 prior** (its
original-eval estimate ≈ 0.883). This is **not** a surprise.

### 3.5 The verifier RESCUES 256 px — but does not overturn 384 (Obs 352)

The genuinely surprising result. The 256-px consensus pool is the **worst**
architecture at consensus-only (F1 **0.460**, below 512's 0.775 and 384's
0.814). The **same pool**, verified, jumps to **0.856 (+0.396)** — the largest
PV lift of any cell — **leapfrogging 512** to take second place. So the
per-architecture tile-size order *changes*:

| architecture | tile-size order (F1@20 m) |
|---|---|
| single-pass | 512 > 384 > 256 |
| consensus-only | 384 > 512 > 256 |
| **consensus+PV** | **384 > 256 > 512** |

This **answers Obs 351's open question** — *does 256 px overwhelm even the
verifier?* — with **no**: the verifier rescues 256 rather than drowning in its
dense false-positive pool, yet **384 retains the lead**. The lift magnitude
tracks proposer false-positive density (largest at the smallest tile),
consistent with the Obs 172 mechanism: PV gain scales with the proposer's FP
pool, which the verifier prunes.

**Caveat**: the 256 cell's proposer is the *plain* text 5-of-5 (N=5) family,
whereas 384/512 share the HIGH-thinking text N=30 lineage (HIGH-text was not run
at 256), so the 256 cell remains a thin-provenance anchor — see
[`384-leg-recon.md`](384-leg-recon.md) § 1.

## 4. Provenance and caveats

- The sidelined `proposer-verifier-512::verified-adversarial-text` cell (D1: thin
  GAP-9 provenance, n=1) is **excluded** from this grid and the 82-cell board.
- The pre-existing `proposer-verifier-384::verified-adversarial-text` (F1 0.471)
  is a **single-pass+PV** cell (`detect_brief-text`, 1 pass) — a different
  architecture, NOT the 384 consensus+PV cell, and is not superseded by it.
- Determinism: every cell is **n=1** at T=0.0. T=0.0 is *not* fully deterministic
  (the PV `-v2` replicate accepted-count drift), so a multi-verifier (N=5)
  robustness check on a few cells remains future work.

## 5. Artefacts

- Score summaries: `outputs/era1-pv-stage-d/stage_d_score_summary.json` (+ `_384.json`)
- Per-cell evals: `results/era1-pv-stage-d/<cell>/evaluation.json` (14-buffer + MCC)
- 384 disambiguation record: `results/era1-pv-stage-d/384-leg-recon.md`
- Tile-size head-to-head: `results/tile-size-sweep/tile_size_sweep.{json,md}` (View 3)
- Definitive board: `results/era1-leaderboard/tiering_20m.{json,md}`
- Orchestration: `scripts/run_era1_pv_stage_d.py`; tabulation: `scripts/tile_size_sweep.py`
- Working notes: Obs 351 (tile-size × architecture), Obs 352 (verifier rescues 256)

## Changelog

### 2026-06-09 — Original publication

Consolidates Stage-D into one results narrative. Session 107 produced the five
256/512-px cells (gated API run, carry-forward adversarial verifier, ~$5 flex);
Session 108 added the 384-px consensus+PV leg ($0, on-disk re-score of the
`flash-high-text-16of30` pool verified by the same carry-forward verifier) and
registered it as `pv-diag-384::verified-adv-text-consensus-16of30`. Headlines:
PV is the single best Era-1 architecture (sole Tier-1, F1 0.792); cheap
single-pass+PV rivals expensive consensus (Tier 2, F1 0.770, MCC 0.790); 384 px
is the consensus+PV tile-size sweet spot (0.890 > 256 0.856 > 512 0.792,
confirming Obs 179); the verifier rescues 256 px (0.460 → 0.856, Obs 352) without
overturning 384. Landed alongside commits `4532a896b` (384 registration) and
`9451f1b39` (tile-size-sweep sign-off).
