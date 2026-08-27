# The final 55-map board: every run, carried and oracle, one reference

> **Last revised**: 2026-08-27 (original publication; awaiting PI
> sign-off — nothing runs until it is given). See
> [§ Changelog](#changelog) for revision history.

**Status**: PREPARED FOR SIGN-OFF. PI decisions already taken
(2026-08-27, interactive): membership = ALL runs at both their
carried ("as run / chosen from the Gold Standard (GS)") and oracle
points, so one table shows the real-world results and the theoretical
maximum; home = a NEW final-board document (the existing
`results/55map-leaderboard/55map-leaderboard-50m-standardised.md`
freezes as the pre-portfolio state). The PI has declared this board
FINAL — no further 55-map runs.

**Classification**: $0 re-score and tiering of committed data; no API
calls. Compute on sapphire.

## 1. Reference and metric

The ruling-21 **standardised reference**
(`inputs/vectors/references/best-available-gt-55maps.geojson`: 4,731
student + 279 extension records, no ring gate), F1@50 m led, tile-MCC
alongside on the shared 8,541-tile standard frame — the same basis as
the existing standardised board. The new runs' detections already
carry standard-frame tile assignments, so both the metric and the
instrument extend without new machinery.

## 2. Membership (16 cells)

| Run | Carried ("as run / GS-chosen") | Oracle (theoretical max) |
|---|---|---|
| T03 (HIGH T0.3, K = 5) | k4 | k3 |
| TH7 (HIGH T0.7, K = 5) | k4 | k3 |
| TM (min, K = 5) | k4 | k3 |
| IM (image, K = 5) | k4 (standardised score exists, 2026-08-23 — joins the board for the first time) | k3 |
| min11-uplift (min, K = 10) | — none exists (flag: post-hoc-only run) | 5-of-10 @ 0.15 |
| **A** (384/33 %, K = 10) | (0.15, k8) | (0.15, k7) |
| **B** (384/50 %, K = 10) | (0.15, k10) | (0.20, k9) |
| **A, N = 5 rung** | (0.15, k4) | re-derived (see below) |
| **B, N = 5 rung** | (0.15, k5) | re-derived |
| **A, N = 1 rung** | — none registered (oracle-only row) | re-derived |
| **A, N = 3 rung** | — none registered (oracle-only row) | re-derived |
| **B, N = 1 rung** | — none registered (oracle-only row) | re-derived |
| **B, N = 3 rung** | — none registered (oracle-only row) | re-derived |

(→ 20 cells, 190 pairs. PI 2026-08-27: N = 5 rows KEPT; N = 1 / N = 3
rows ADDED as oracle-only, matching their treatment in the stride55
Pareto.)

**Oracle definition (PI ruling 2026-08-27, replacing the drafted
freeze)**: every oracle cell is the **standardised-reference argmax**,
re-derived by $0 re-sweep — the column's claim is the theoretical
maximum, so the argmax must be computed on the board's own reference,
uniformly for all runs. Bound honestly by each run's verified sweep
space: vote ≥ 1 (full union) for A/B and their rungs; the vote ≥ 3
verified shells for the K = 5 incumbents; the ≥ 3-of-10 band for
uplift — incumbent oracles are best-within-verified-space, stated as
such. The previously selected points (canonical-GT argmaxes for A/B;
S104 completions for incumbents) remain documented history; the
stride55 transfer-tax analysis is unaffected (it lives on the
canonical GT).

## 3. Prerequisite: standardised re-score of the new cells (6 evals)

Materialise verified-detection GeoJSONs at the six A/B operating
points above (from the committed unions + probabilities), score with
`scripts/evaluate_detections.py` against the standardised reference
(14 buffers, `--mcc`, tile-level BCa bootstrap 10,000/seed 42 — the
IM-k4 template), into the new results home.

## 4. Instrument

Round-robin **tile-swap micro-F1 permutation** on the shared
8,541-tile frame (10,000, seed 42) + Benjamini–Hochberg q = 0.05 over
all 190 pairs + greedy-clique tiers. Provenance verified 2026-08-27:
this is the GS instrument itself
(`pairwise_permutation_test.py::run_permutation_test` + the
tiering machinery of `n1_baseline_leaderboard_tiering.py`), imported
verbatim by every board since (Era-1, stride 13-cell, the 55-map
standardised board via `build_55map_leaderboard.py`) — the final
board continues the unbroken chain, per the PI's direction. Presentation: (a) the ranked 16-cell tier board,
basis-labelled; (b) the paper table — rows = runs, columns =
carried F1 (tier) | oracle F1 (tier).

## 5. Gates (nothing published unless all pass)

1. **Engine gate**: re-running the driver on IM-k4 reproduces its
   committed standardised `evaluation.json` @ 50 m exactly.
2. **Band gate**: A/B canonical→standardised deltas fall inside the
   incumbent-observed band (|Δ| ≲ 0.005 at 50 m); larger drift halts
   for diagnosis, not silent publication.
3. **Board regression gate**: the tiering harness re-run on the
   existing 8 cells alone reproduces the committed standardised board
   (F1s and tiers) before any 20-cell result is trusted.
4. **Sweep-scorer gate**: the light F1@50 point scorer used for the
   oracle re-sweeps must reproduce `evaluate_detections.py`'s
   committed F1@50 on at least two existing standardised cells before
   any argmax it produces is trusted.

## 6. Deliverables

`results/55map-final-board-2026-08-27/`: six new-cell evaluation
sets; `final_board_50m.json` + `final-board-50m.md` (ranked board +
paper table + changelog); a findings section folding in the
S143 pairwise results (per-map A-vs-B, saturation) as the pairwise
companion to the board's tile-swap tiers. Register rows: held for the
interactive session (standing rule — the registry is hand-verified).

## 7. Sign-off

- [x] PI sign-off to execute — given 2026-08-27 ("do clear the three
      gates"), with three amendments folded in above: same GS board
      instrument confirmed as intended; N = 5 rows kept and N = 1/3
      oracle-only rows added; oracles re-derived as
      standardised-reference argmaxes.

## Changelog

### 2026-08-27 (later) — Sign-off amendments

PI interactive review: (1) instrument provenance verified — the GS
tile-swap chain, applied unchanged; (2) membership widened to 20
cells (N = 1/3 oracle-only rungs for A and B); (3) oracle cells
redefined from frozen-as-selected to standardised-reference argmax
within verified sweep space, with a fourth gate covering the sweep
scorer. Sign-off recorded.

### 2026-08-27 — Original publication

Drafted in-session from the two PI decisions (membership: all runs,
carried + oracle; home: new document). Prerequisite re-score, gates,
and instrument declared before execution per house practice.
