# K-ladder review: pass count at fixed parameters, Pareto-framed

> **Last revised**: 2026-09-12 (R1–R5 RULED and two project principles
> recorded; B3 ruled: the 27 first-N twins are derived inside this job;
> prior 2026-09-11: DRAFT scaffold, S153, from committed
> material only; **no compute, no API, no register change until the PI
> rules on § 4**). See
> [§ Changelog](#changelog).

**Status**: SCOPING CARD, not a run card. The PI asked in Session 152 for
a review of the pass-count ladder — K = 1, 3, 5, 10 at fixed parameters,
framed as a Pareto (cost-against-F1) question, together with a ruling on
whether re-materialised and current-vintage cells belong on the board
(`planning/paper-writeup-continuity.md`, "STATE AFTER S152", item B4).
This card scopes that review so the PI can rule on it before anything
is computed. Every number below is re-read from the file cited beside it.

## 1. The question

Across the study the number of proposer passes (K) has been treated as a
cost lever whose F1 return saturates early. Three registered analyses
already say so on three instruments, but each ladder varies something
besides K, and the Gold Standard (GS) Era-2 verified board excludes
K = 1 cells by rule. The review asks:

1. **At genuinely fixed parameters** (one tile geometry, one thinking
   level, one temperature, one verifier, one operating-point rule), what
   does F1 do across K = 1, 3, 5, 10?
2. **On a Pareto framing**, which rungs are efficient once the audited
   per-pass cost is attached, on GS and projected to the 55-map corpus?
3. **Board membership**: should the K = 1 rungs (excluded as
   "single-pass proposer + verifier") and any rung that exists only as a
   re-materialised or current-vintage cell sit on the Era-2 board, or on
   a separate ladder table?

## 2. What already exists ($0, committed)

| Ladder | K rungs | Fixed | Varies besides K | Result | Anchor |
|---|---|---|---|---|---|
| `pass-budget-pareto-v2` (GS, Era-2 frame) | 6, 11, 31, 35 total passes | 384 px, curator GT, 20 m | thinking level (min vs HIGH), temperature, verifier input rule | all seven rungs one statistical tier; efficient set min6 $2.43 / 0.8784, min11 $4.00 / 0.8835, high31 $69.21 / 0.8902, high35 $71.23 / 0.8951; MCB admissible 6 of 7 | `results/run-analyses.json` row `pass-budget-pareto-v2`, outcome text; signed 2026-06-12 |
| `grid-2026-08-18` K-ladder (GS, grid-common frame) | 1, 3, 5, 10 | per cell: geometry, MINIMAL text, T 0.7 | consensus-only until the 2026-08-24 verifier stage; only K = 10 verified | union recall 0.8972 → 0.9229 → 0.9393 → 0.9416 at 512 / 50 %; "diminishing returns in K are steep"; vote optimum at the grid edge at K = 3 | `results/grid-2026-08-18/findings.md` lines 196–202 |
| `stride-winner-ladder-exact-2026-08-25` (GS, B geometry) | N = 1, 3, 5 (of K = 10) | 384 / 50 %, MINIMAL text, carried verifier | first-N sub-pools of one K = 10 run, not independent runs | N = 1 0.8677; N = 3 0.8911 (~$2.64 all-in); N = 5 0.8856; N = 3 within noise of K = 10 (0.8982) | `results/run-analyses.json` row `stride-winner-ladder-exact-2026-08-25`; Obs 436 |
| `stride55-ladder-2026-08-27` (55-map, r2) | first-N rungs of A and B | as above at deployment | first-N sub-pools | P2 pass exact; saturation by N = 3 for the all-3.7 stack (§ R7.3) | `results/run-analyses.json` row `stride55-ladder-2026-08-27` |
| Gemini 3.7 screen (GS, grid-common) | 5, 10 | B geometry, 3.7-low text, T 0.7 | none | K = 10 adds +0.0003 over K = 5 (0.9142 vs 0.9139) | `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/membership.txt`; `planning/gemini38-screen-2026-09-04.md` cells table |

Rung inventory in the conditions register, verified cells on the GS
pools (`results/conditions-manifest.json`, field `n_passes`, counted
2026-09-11): `pv-diag-384` has K = 1 (24 conditions), 3 (6), 5 (65),
10 (31), 30 (2); `verifier-robustness` K = 1 (2), 5 (12);
`grid-2026-08-18` K = 10 only (11); `gemini37-screen` K = 5 (6), 10 (2).
So a K = 1 / 3 / 5 / 10 ladder at fixed parameters **may already be
scorable from committed pools** for the Gemini 3 MINIMAL-text 384 px
family in `pv-diag-384`, if its K = 3 and K = 1 conditions share the
K = 5 / K = 10 cells' temperature, thinking level, and verifier. That
check is § 3 step 1, and it is $0.

## 3. Proposed review, in order (all $0 unless stated)

1. **Inventory the fixed-parameter ladders that exist.** For each GS
   family (Gemini 3 MINIMAL text 384 px; Gemini 3 HIGH text; Gemini 3
   image; 3.7 text; 3.7 image), list the committed verified cells at
   K = 1, 3, 5, 10 whose non-K parameters are identical, from
   `results/conditions-manifest.json`. Output: one table, gaps marked.
   Expected: the Gemini 3 MINIMAL text family is complete or nearly so;
   3.7 has K = 5 and 10 only; image has K = 5 and 10 only.
2. **Fill gaps from existing pools where the first-N rule permits**
   (sub-pool consensus with `merge_passes --passes 1..N`, the
   preregistered rule used in Session 106) and re-verify only where a
   verifier pass over a smaller union is missing. Any verifier call is
   API spend and is gated: cost it per family before running.
3. **Score every rung on the board's own frame** (`era2-b-487`, 20 m,
   tile-MCC alongside F1) with the board instrument
   (`scripts/era1_leaderboard_tiering.py`), on sapphire. Paired
   tile-swap permutation between adjacent rungs; BH q = 0.05; Hsu MCB
   admissible set per family.
4. **Attach audited cost per rung** on the token-load-audit basis
   (`reports/token-load-audit-2026-06-12.md` pattern; the 3.7 rates
   from the S153 R7 deltas report once it lands). Pareto frontier per
   family on GS, then the 55-map projection column as
   `pass-budget-pareto-v2` did (tile factor 8,541 / 487).
5. **Write one findings document** with the Pareto figure and a
   per-family ladder table, and register one analysis row for the PI to
   sign. Feed the Results outline (§ R6 frontier) as a claims-with-anchors
   delta, not prose.

## 4. Rulings — given by the PI on 2026-09-12 (originally "needed before step 1")

**Two principles the PI stated with the rulings, recorded as project rules:**

- **Keep history, present the best available.** Registers keep every
  run; nothing is rewritten. Anything paper-facing — leaderboards,
  ladders, tables, results documents — carries, for each configuration,
  the best-QUALITY cell available: the one on the most complete inputs,
  the sound vintage, the current reference and frame, usually the newest;
  never chosen on F1. When a board's representative for a configuration
  changes, the board's changelog says so and the superseded cell stays in
  the register and the supplement.
- **Ladder, then board.** Each major lever (pass count K, stride, tile
  size, temperature, thinking level, model family) is analysed in
  isolation as a ladder at otherwise fixed parameters, registered as its
  own analysis; then every cell, ladder rungs included, feeds the board.
  This is the preregistration's factor-at-a-time intent, reached by a
  different road.


- **R1 — RULED: the carried Gemini 3 verifier at every rung, no
  swapping.** The ladder's question is the proposer's pass count.
- **R2 — RULED: report both operating points; tier on the sweep-optimal
  on the board frame (the `-opmax` convention, Obs 466 gate); show the
  carried point (prob 0.15, k = K) as the transfer-tax column.**
- **R3 — RULED: the ladder carries K = 1, AND a K = 1 cell that earns a
  place on a board is admitted.** The board's twenty single-pass
  exclusions were a scope choice of the inventory builder (architecture
  class), not a statistical one; under "ladder, then board" the board
  takes every verified cell on its frame regardless of K, and the
  Era-2 board is re-tiered and re-signed with them in.
- **R4 — RULED (with a clarification): compare like with like by
  rebuilding older cells on the best available inputs, and let the best
  available cell per configuration stand on ladders and boards.** The
  PI's framing was "the ground truth is a moving target"; the
  clarification (accepted 2026-09-12) is that three things move
  separately. (a) The REFERENCE (ground truth) and (b) the FRAME are
  already held fixed by the board: every cell is re-scored on one
  reference and one frame (gate G1), and the 55-map cells on r2. The
  Gold Standard curator reference has not moved. (c) The CANDIDATE
  VINTAGE is what B2 was about: a union rebuilt from recovered passes is
  a different input set, and a verifier's probabilities are API output
  tied to the candidates it saw, so an old cell cannot be "re-scored" on
  a new union — it has to be re-verified (API spend). The vintage guard
  (`scripts/check_pv_sweep_vintage.py`) says the exposure is small: of
  the 30 registry cells, 24 same-vintage, 4 probabilities-grew (already
  re-swept 2026-09-08), 1 union-rebuilt (`pv-high-text-t0.0-n3`, whose
  current-vintage pair was re-verified 2026-09-08 for US$1.82), 1
  manifest-mode. So R4 in practice: register the September pair of
  `pv-high-text-t0.0-n3` under its own name as the best available cell
  for that configuration (the April pair stays as the archived board's
  cell — B2); re-verify any other cell whose union is newer than its
  probabilities, costed under R5; and every cell is scored on the current
  reference and frame by the board as now.
- **R5 — RULED: up to US$50 for loose ends, every run costed and
  approved by the PI first; batching approvals is fine.** The 3.8
  screen's verifier arm cost about US$0.82 billed per 791-candidate
  union, so gap-filling verifier passes are cents to a few dollars each.

## 5. What this card does not do

It does not re-open the pass-budget Pareto's efficient set, the E83 MCB
ruling, or the stride ladders' registered outcomes. **It DOES now own
the uplift supplement's 27 truly-absent first-N twins**: the PI ruled on
2026-09-12 (B3) that their pre-verifier universes are derived inside this
ladder job, under its gates, rather than by a separate re-run — the
rungs of `stride-55map-2026-08-25` A and B (23 pairs) and
`gemini37-55map-2026-08-29` arms 1 and 2 (4 pairs), re-clustered from
the first N passes exactly as `scripts/stride55_ladder.py` and
`scripts/gemini37_arm_ladder.py` do, materialised, registered as
conditions, and scored on the cells' own recipes. Step 2 therefore
includes the 55-map rungs, not only the GS families, and the uplift
supplement is regenerated when they land.

## Changelog

### 2026-09-12 — R1–R5 ruled; two principles recorded; B3 folded in (Session 153)

The PI ruled R1–R5 (§ 4) and stated the "keep history, present the best
available" and "ladder, then board" principles, both recorded at the head
of § 4. R4 was accepted with the clarification that reference, frame and
candidate vintage move separately. B3: the 27 blocked first-N ladder
rungs get their twins from this job (§ 5). The card is no longer a
scaffold; the job can be planned (Phase 1 at $0, Phase 2 costed).

### 2026-09-11 — Original publication (S153, DRAFT scaffold)

Scoped from the PI's Session-152 intent. Sources re-read this session:
the three ladder register rows in `results/run-analyses.json`, the grid
findings' K-ladder passage, the signed Era-2 board's `membership.txt`,
and the conditions register's `n_passes` field. No compute, no API, no
register change. Awaiting the § 4 rulings.
