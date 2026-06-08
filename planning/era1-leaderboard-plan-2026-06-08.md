# Era-1 (Gold-Standard) definitive leaderboard — plan

**Created**: 2026-06-08 (Session 106). **Updated**: 2026-06-08 (D1 → sideline dodgy
PV-512 + add Stage D, a gated clean-verifier run). **Status**: PLAN ONLY — execute
next session. **Compute**: Stages A/B/C are local $0 (zbook/sapphire, never
amd-tower); **Stage D is a gated API verifier run, budget ≤$50**.

## Why this exists

The **Gold-Standard 4-map runs (Era 1)** are a *different class* of result from the
**55-map run**: GS is the in-depth **characterisation** thread (expert curator GT,
4 maps, deep parameter sweeps); the 55-map run is the **generalisation** thread
(many maps, weaker student GT, out-of-sample). The GS thread must be **complete and
analysable on its own terms** — the 55-map deployment cannot stand in for a gap in
the GS characterisation. This plan delivers (a) a definitive Era-1 leaderboard and
(b) an Era-1 (512 px) ↔ 384 px comparison to characterise the effect of tile size,
which is the natural close-out of the GS thread.

## Foundation — VERIFIED COMPLETE (no re-scoring needed)

Independently re-verified 2026-06-08 (read every Era-1 condition's `evaluation.json`):
**10 Era-1 runs, 79 conditions, 79/79 carry the full 14-buffer set + non-null tile
MCC, 0 gaps.** The phase2 (Session 102) and phase3 (Session 106) re-scores already
closed the data gaps. So Stage A below is *not* a re-scoring task — every deliverable
is secondary analysis over already-complete data.

| Run | H | Architecture | Conditions |
|---|---|---|---|
| retest-phase2a | H1 | single-pass (K=3) | 5 |
| retest-phase2b | H7 | single-pass (K=3) | 10 |
| retest-phase2c | H8 | single-pass (K=3) | 13 |
| retest-phase2d | H5 | single-pass (K=3) | 4 |
| retest-phase2e | H4 | single-pass (K=3) | 4 |
| retest-phase3a | H3 | consensus sweep | 18 |
| retest-phase3a-high | H3 | consensus sweep | 9 |
| retest-phase3a-replication | H3 | consensus sweep | 6 |
| retest-phase3c | H9 | consensus sweep | 9 |
| proposer-verifier-512 | H2/H11 | PV-verified (n=1) | 1 |
| **total** | | | **79** |

All single-pass + consensus conditions are `gemini-3-flash`, **MINIMAL thinking
except** phase3a-high + phase3a-replication/high + phase3c (HIGH) — the consensus
calibration analyses are already published + signed off
(`phase3a-consensus-calibration`, `phase3a-high-consensus-calibration`,
`phase3a-replication-thinking-calibration`, `phase3c-diversity-calibration`).

## Stage A — Era-1 single-pass baseline leaderboard (the missing n1 analogue)

Era 2 has `n1-baseline-matrix-384` (a tiered single-pass board at 384 px); **Era 1
has no published single-pass leaderboard** though all 36 phase2 single-pass
conditions are scored. Build it:

- **Harness**: `scripts/n1_baseline_leaderboard_tiering.py` (round-robin tile-swap
  micro-F1 permutation, 10k perms, seed 42, two-sided + BH-FDR q=0.05 +
  greedy-clique tiering at the 20 m headline buffer) — the project-canonical method.
  Adapt to the 512 px / Era-1 conditions (replicate-mean per-tile counts from the
  K=3 phase2 evals).
- **Cells**: the 36 single-pass conditions (phase2a/b/c/d/e). Decide whether to tier
  all 36 together or per-hypothesis sub-boards (recommend: one combined board to find
  the overall best single-pass Era-1 config + tiers, with the OFAT structure noted).
- **Output**: `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.{json,md}`;
  register as analysis `era1-single-pass-baseline-matrix` (H1/H4/H5/H7/H8) in
  `results/run-analyses.json`.

## Stage B — the definitive Era-1 leaderboard

Combine single-pass + consensus + PV into one tiered board (the Era-1 analogue of
`diversity-dividend-384`), so "best Era-1 configuration overall" is a statistical
statement, not a max over separate sweeps.

- **Harness**: `scripts/consensus_vs_baseline_tiering.py` (reuses the n1 tiering
  verbatim; consensus cells contribute integer per-tile TP/FP/FN from their single
  aggregated set, single-pass cells keep pass-averaged per-tile counts).
- **Cell set (D2 — FULL board)**: all **79 Era-1 conditions** — 36 single-pass +
  **all 42 consensus conditions (per cell×N, not just cell-champions)** + the 1
  PV-verified condition. Tier them in the usual way (greedy-clique over the
  permutation+BH-FDR significance graph). Keeping all 42 (rather than collapsing to
  cell-champions) keeps the board shape comprehensive and **compatible with the later
  256/384 boards**. Expect a many-tier board; the calibration analyses remain the
  per-config sweep detail.
- **Output**: `results/era1-leaderboard/tiering_20m.{json,md}`; register as analysis
  `era1-leaderboard` (H1–H9 cross-cut) in `run-analyses.json`. Headline at 20 m;
  report MCC alongside (the F1-vs-MCC divergence is expected to recur).
- **Expected shape** (from the calibration analyses): HIGH-thinking text consensus
  (~0.77) should top F1; minimal single-pass and image trail; the diversity dividend
  is the story. Confirm with tiering.

## Stage C — tile-size comparison across the FULL sweep (256 / 384 / 512)

Characterise the effect of tile size on **all matched configurations** (D3). We now
have all three tile sizes scored at 14-buf+MCC: **256 px** (pv-diag-256, decomposed
this session — text single-pass + 5-pass consensus sweep), **384 px** (Era 2/3:
pv-diag-384 + n1 board + library), **512 px** (Era 1). So this is a 3-point sweep,
not a single 512↔384 pair.

- **Matched single-pass**: phase2b {text,image} × T{0.0,0.7} (512) ↔ pv-diag-384
  `baseline-flash-{text,image}-minimal-t-{0-0,0-7}` (384) ↔ pv-diag-256 `text-baseline`
  (256, text-only — image was not run at 256). Enumerate exactly what matches at all
  three sizes vs only two.
- **Matched consensus**: Flash text/image consensus exists at multiple sizes —
  phase3a (512, minimal) ↔ pv-diag-384 flash-minimal-text/image (384) ↔ pv-diag-256
  `text-consensus-5of5` (256); phase3a-high (512, HIGH text) ↔ pv-diag-384
  flash-high-text (384). Enumerate the model×modality×thinking×temp×(N,threshold)
  matched sets across sizes.
- **Method**: extract F1@20 m (the cross-era-comparable metric) for every matched
  config at each available tile size; tabulate the size→F1 curve per config; note the
  apparent **non-monotonicity** (the headline single-pass/consensus numbers so far
  order 256 < 512 < 384 at 20 m — 384 looks like a sweet spot, not "smaller is always
  better"). Report MCC per-size (not differenced — tile-count base differs). Register
  as `tile-size-sweep` in `run-analyses.json`.
- **Pipeline tie-in (D3 rationale)**: this is a direct input to the "give-us-your-map"
  pipeline (`planning/generalised-pipeline-roadmap.md`) — it lets a user trade tile
  size against speed/cost. Present the accuracy-vs-tile-size curve next to the
  speed/cost cost so users can choose. Consider adding a WS to the roadmap for
  tile-size guidance, seeded by this analysis.

### ⚠ Methodological flags (decide before running Stage C)

1. **F1 is cross-era comparable; tile-MCC is NOT.** Eras share the same 4 maps + GT
   mounds, so mound-level **F1@20 m is directly comparable** across tile sizes. But
   **tile-MCC depends on tile count** (340 vs 487 vs 327 → different true-negative
   base), so MCC is **not** directly comparable across eras — report it per-era,
   don't difference it. Headline the tile-size effect on **F1**.
2. **Tile size is confounded with tile set.** 512 px→340 tiles and 384 px→487 tiles
   are *different tilings of the same maps*, not the same tiles re-sized. The Δ
   therefore measures the combined "smaller-tile + more-tiles" effect, which is the
   honest operational quantity — but state it as such, not as a pure tile-size
   isolation. (A pure isolation would need the same regions scored at both sizes.)
3. **Which 384 scope?** Compare against Era-2 (487) for the broadest match;
   Era-3 (327, leakage-clean) is the stricter set. Recommend Era-2 for the matched
   baselines (they live in pv-diag-384), noting the Era-3 leakage caveat.

## Stage D — clean Era-1 PV grid (gated API run; replaces the dodgy PV-512)

A small, fresh verifier pass to give clean, well-provenanced proposer-verifier cells
at Era-1 — building toward a **clean cross-era grid: tile size (256/384/512) ×
{consensus, single-pass} × {text, image}**, all verified with the production
verifier. Executes **after Stage B** (the consensus selection is "~tier 1", so we
need the tiering first) and **feeds a re-tier of the board + Stage C**.

- **Verifier config**: `verify_adversarial.md`, `gemini-3-flash`(-preview), minimal
  thinking, T=0.0, **n=1** (matches Era-2 proposer-verifier-384).
- **Cells to verify** (review the exact cut together once Stage B tiers are in):
  - **Consensus** (proposer→consensus→verifier): the leading **text + image**
    consensus cells, ~Tier 1 of the Stage-B board.
  - **Single-pass** (proposer→verifier): the clean **K=3 phase2b** single-pass text +
    image — **already on disk, NO re-run needed** (confirmed: phase2b is single-pass
    K=3, passes under `outputs/retest/phase2b/track{1-image,2-text}/`). Verify the
    passes (n=1 verifier each) for a K=3 replicate, matching the single-pass structure.
- **Mechanics**: generate candidate crops locally ($0); run the verifier (Gemini,
  $) over each selected output; score the verified outputs at 14-buf+MCC; mint clean
  `verified-*` conditions. **Sideline** `proposer-verifier-512::verified-adversarial-
  text` (flag superseded in its `_note`; keep the data — archive-never-delete).
- **Budget**: up to **$50** (est ~$2–10; anchor: 55-map verifier ~$0.0007/candidate,
  Era-1 cells ~1–2k candidates each). **API review gate applies** — present
  model/mode/#calls/$ for approval before running.
- **Feeds**: the re-tiered leaderboard (clean PV cells in place of the dodgy one) and
  the Stage-C grid (PV row of the tile × consensus/single × text/image matrix).
- **Note**: 256 px (pv-diag-256) is text-only (no image at 256), so the grid's
  256-image cell will be absent — state it rather than impute.

## Decisions — RESOLVED (Shawn, 2026-06-08)

- **D1 — SIDELINE the dodgy proposer-verifier-512; run a clean Era-2-matched verifier
  instead (new Stage 0, gated API).** The existing `proposer-verifier-512::verified-
  adversarial-text` is thin (GAP-9 weak provenance, `pool-unresolved`, n=1) and mirrors
  no Era-2 PV cell cleanly. Sideline it from the leaderboard (keep the data; flag
  superseded in its `_note`) and instead generate clean PV cells via Stage 0 below.
  Budget approved: **up to $50** (est ~$2–10). Verifier config = **adversarial only**
  (`verify_adversarial.md`, gemini-3-flash, minimal thinking, T=0.0), the production
  carry-forward. Verifier passes = **n=1** (confirmed: Era-2 proposer-verifier-384 ran
  a single verifier pass per condition; the `-v2` files are replicate re-runs, not
  n=3) — replicate later eras = n=1.
- **D2 — full board: tier ALL 42 consensus conditions** (per cell×N), not just
  cell-champions, alongside the 36 single-pass + the **clean Stage-0 PV cells** (the
  dodgy PV-512 excluded) = the usual tiers. Rationale (Shawn): keep it comprehensive
  and **fully compatible with later eras** so the same board shape carries across
  256/384/512.
- **D3 — Stage C: compare ALL matched configs** (single-pass + consensus) across the
  **full tile-size sweep 256 / 384 / 512** (pv-diag-256 was decomposed this session,
  giving the 256 anchor). Rationale (Shawn): 512 px has real advantages (speed, cost),
  and the "give-us-your-map" pipeline must present the smaller-tile accuracy gains
  *alongside* the speed/cost cost so users can choose their tile size — so the
  characterisation should be as complete as the matched configs allow, not minimal.

## Execution order (next session)

1. Stage A ($0) — adapt + run `n1_baseline_leaderboard_tiering.py` at 512 px over the
   36 single-pass conditions → register `era1-single-pass-baseline-matrix`.
2. Stage B ($0) — run `consensus_vs_baseline_tiering.py` over the board (36 single-pass
   + 42 consensus; **dodgy PV-512 sidelined**) → register `era1-leaderboard`. Review
   the tiers together to pick the ~Tier-1 text + image consensus cells for Stage D.
3. Stage D (**gated API, ≤$50**) — clean Era-1 PV grid: adversarial verifier (n=1) over
   the selected consensus champions (text+image) + the clean phase2b single-pass
   (text+image). API review gate first. Mint clean `verified-*` conditions; sideline
   PV-512. Re-tier the leaderboard to fold the clean PV cells in.
4. Stage C ($0) — the tile-size sweep grid across **256 / 384 / 512** × {consensus,
   single-pass} × {text, image} (now with the clean PV row); F1@20 m size-curve, MCC
   per-size → register `tile-size-sweep`.
5. Tier-1 tests for any new/adapted harness; regenerate manifest; drift-check;
   commit + push; sync machines.

## What this does NOT need

- No re-scoring of existing data, and **no new proposer/detection runs** (all proposer
  data is complete — including pv-diag-256, the 256 px anchor, decomposed 2026-06-08,
  and the clean K=3 phase2b single-pass passes already on disk). The only API spend is
  the Stage-D verifier pass (≤$50, gated).
- No new detection runs.
