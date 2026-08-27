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
| **A, N = 5 rung** | (0.15, k4) — also its rung oracle | (same cell) |
| **B, N = 5 rung** | (0.15, k5) | — excluded: rung oracle differs by +0.0012 (noise); noted in prose |

Open to pruning at sign-off: the two N = 5 rows (recommend KEEP —
they carry the deployment recommendation). Oracle points stay FROZEN
as originally selected (the A/B oracles were selected on the
canonical-GT sweep; the incumbent k3 completions on the S104
deployment GT) and are re-PRICED on the standardised reference, not
re-picked — same treatment the existing board gave T03-k3. A
standardised-reference re-sweep is possible ($0) but would change the
oracle definition mid-stream; not recommended.

## 3. Prerequisite: standardised re-score of the new cells (6 evals)

Materialise verified-detection GeoJSONs at the six A/B operating
points above (from the committed unions + probabilities), score with
`scripts/evaluate_detections.py` against the standardised reference
(14 buffers, `--mcc`, tile-level BCa bootstrap 10,000/seed 42 — the
IM-k4 template), into the new results home.

## 4. Instrument

Round-robin **tile-swap micro-F1 permutation** on the shared
8,541-tile frame (10,000, seed 42) + Benjamini–Hochberg q = 0.05 over
all 120 pairs + greedy-clique tiers — the existing board instrument
verbatim. Presentation: (a) the ranked 16-cell tier board,
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
   (F1s and tiers) before any 16-cell result is trusted.

## 6. Deliverables

`results/55map-final-board-2026-08-27/`: six new-cell evaluation
sets; `final_board_50m.json` + `final-board-50m.md` (ranked board +
paper table + changelog); a findings section folding in the
S143 pairwise results (per-map A-vs-B, saturation) as the pairwise
companion to the board's tile-swap tiers. Register rows: held for the
interactive session (standing rule — the registry is hand-verified).

## 7. Sign-off

- [ ] PI sign-off to execute (membership table § 2 as listed, or
      with pruning noted here)

## Changelog

### 2026-08-27 — Original publication

Drafted in-session from the two PI decisions (membership: all runs,
carried + oracle; home: new document). Prerequisite re-score, gates,
and instrument declared before execution per house practice.
