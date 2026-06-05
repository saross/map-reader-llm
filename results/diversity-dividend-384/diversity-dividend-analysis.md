# Diversity dividend — consensus vs single-pass baseline (H3)

> **Last revised**: 2026-06-06 (original publication — the diversity-dividend
> statistical test, Session 103). See [§ Changelog](#changelog) for revision history.

The **diversity-dividend test** (preregistered hypothesis **H3**) asks two
linked questions about consensus voting over multiple Vision Language Model
(VLM) proposer passes:

1. **Diversity dividend** — does **HIGH-thinking** consensus (more diverse
   proposals) recover or exceed **minimal-thinking** consensus?
2. **Consensus vs single-pass** — does consensus voting beat the single-pass
   baseline, and can cheap **Gemini 3 Flash** consensus approach the expensive
   **Gemini 3 Pro** single pass?

It is the significance layer over the registered `pv-diag-384-consensus-calibration`
sweep: that sweep registered the best-F1 operating point per configuration; this
analysis tiers the best consensus operating points against the single-pass
baseline board and tests every contrast for significance.

## Method

The project-canonical **N=1 leaderboard** method, reused verbatim
(`scripts/consensus_vs_baseline_tiering.py` imports
`scripts/n1_baseline_leaderboard_tiering.py`):

- **Round-robin tile-swap permutation** on micro-average F1@20 m — all C(N, 2)
  pairs, probability-0.5 per-tile label swap, 10,000 permutations, seed 42,
  two-sided.
- **Benjamini–Hochberg FDR** at q = 0.05.
- **Greedy-clique tiering** — cells in descending F1; a cell joins the current
  tier iff it is statistically indistinguishable from all current members.
  Tier 1 is the `tie_set`.

The board is **22 cells**: 4 consensus pool-champions (best-F1@20 m per proposer
pool, at the T=0.7 production carry-forward temperature) + the **18 single-pass
cells** of `n1-baseline-matrix-384`. Consensus cells contribute integer per-tile
TP/FP/FN from their single aggregated set; single-pass cells keep the
pass-averaged per-tile counts — both feed the identical float tile-swap. A
companion **26-cell** run adds the four **deployable N=5** operating points (text
**4-of-5**, image **3-of-5** — the 55maps deployment thresholds) so deployable
performance is tiered too. Era-2 487-tile scope, 384 px, `gemini-3-flash`
proposer; ground truth `mounds-reference.geojson`.

**MCC** (tile-level, buffer-agnostic) is reported beside F1 per the standing
report-MCC-with-F1 preference; the permutation statistic is F1 (as on the n1
board).

## Result — both claims confirmed

**197 / 231 pairs significant → 7 tiers.** Full tables:
[`tiering-champions/tiering_20m.md`](tiering-champions/tiering_20m.md) (22-cell)
and [`tiering-with-deployable/tiering_20m.md`](tiering-with-deployable/tiering_20m.md)
(26-cell).

### 1. Diversity dividend (HIGH > minimal consensus, matched modality)

| Modality | HIGH F1 | minimal F1 | ΔF1 | BH-p | ΔMCC |
|---|---:|---:|---:|---:|---:|
| Text | 0.814 | 0.661 | **+0.153** | <0.001 | +0.239 |
| Image | 0.750 | 0.680 | **+0.070** | <0.001 | +0.272 |

Both significant, on both F1 and MCC. The HIGH-thinking pools take the larger
consensus gain: more varied proposals let a high vote threshold prune their
false positives (the HIGH-text champion carries 41 tile-level FPs vs the
minimal-text champion's 115).

### 2. Consensus beats matched single-pass — everywhere, including deployable

Every consensus champion significantly beats its **matched within-pool**
single-pass baseline (same model, modality, thinking, temperature):

| Pool (T=0.7) | single-pass F1 | best-F1 consensus | ΔF1 | deployable N=5 | ΔF1 (deploy) |
|---|---:|---:|---:|---:|---:|
| `flash-high-text` (HIGH) | 0.387 | 0.814 | +0.427 | 0.720 (4-of-5) | +0.333 |
| `flash-high-image` (HIGH) | 0.499 | 0.750 | +0.251 | 0.727 (3-of-5) | +0.228 |
| `flash-minimal-text` (min) | 0.488 | 0.661 | +0.173 | 0.602 (4-of-5) | +0.114 |
| `image-n5` (min) | 0.553 | 0.680 | +0.127 | 0.644 (3-of-5) | +0.091 |

All eight contrasts BH-p < 0.001. Consensus voting lifts F1 over a single pass
at both the in-sample best threshold and the honest a-priori N=5 deployable
threshold.

### 3. Cross-architecture headline — Flash consensus reaches the Pro tier

**Tier 1 (the `tie_set`) is a three-member statistical tie:**

| Cell | F1@20 m | MCC |
|---|---:|---:|
| `flash-high-text` consensus (26-of-30) | 0.814 | 0.620 |
| `pro-text-high-t-0-0` single pass (genuine Pro) | 0.804 | 0.790 |
| `pro-text-medium-t-0-0` single pass (genuine Pro) | 0.792 | 0.790 |

The permutation cannot separate the Flash consensus champion from the genuine
Gemini 3 Pro single-pass leader (p = 0.616, BH-p = 0.66). **Cheap Flash
consensus reaches the expensive Pro single-pass tier on localisation F1.**

## Caveats (honest reporting)

1. **The Tier-1 parity is in-sample.** The consensus champion sits at its
   best-F1@20 m vote threshold (26-of-30), selected on the 487-tile test set —
   an in-sample operating point per **E56**. At the honest a-priori **N=5
   deployable** point, HIGH-thinking Flash consensus reaches **Tier 2** (text
   4-of-5 = 0.720, image 3-of-5 = 0.727), tying genuine Pro text at **T=0.7**
   rather than the absolute Pro leader. The cross-architecture competitiveness
   is robust to operating-point honesty — it drops one tier, not out of
   contention.
2. **F1-parity is not MCC-parity.** The genuine Pro text leaders have higher
   tile-level discrimination (MCC 0.790, 11 tile FPs) than the Flash consensus
   champion (MCC 0.620, 41 tile FPs); Pro image is the overall MCC leader
   (0.85–0.91). The metric-dependent-winner pattern of the n1 board persists:
   Flash consensus matches Pro on localisation F1 but is less tile-precise.
3. **The diversity dividend itself is robust** to operating-point choice — the
   HIGH > minimal ordering holds at the deployable N=5 thresholds, at greedy
   4-of-5, and at the in-sample best.

## Provenance

- **Script**: `scripts/consensus_vs_baseline_tiering.py` (reuses
  `n1_baseline_leaderboard_tiering.py`); **tests**:
  `tests/test_consensus_vs_baseline_tiering.py` (6 tier-1).
- **Cell spec**: `planning/diversity-dividend-cells-2026-06-06.json`.
- **Evals**: `results/rescore-2026-06-05/pv-diag-384/consensus-sweep/` (14-buffer
  + MCC re-score, worklist `pv-diag-384-consensus-14buf-mcc-2026-06-05.json`).
- **Manifest entry**: `results/run-analyses.json` → `diversity-dividend-384`.
- **Compute**: zbook (round-robin permutation sweep); $0 API.

## Changelog

### 2026-06-06 — Original publication

The diversity-dividend statistical test (Session 103). Promotes the registered
`pv-diag-384-consensus-calibration` sweep to a verified finding. Both named
claims confirmed: the diversity dividend (HIGH > minimal consensus) is
significant on F1 and MCC in both modalities; consensus significantly beats
matched single-pass at both the in-sample best and the deployable N=5
operating points; and the Flash HIGH-text consensus champion forms a
three-member Tier-1 tie with the two genuine-Pro single-pass text leaders.
Caveats: the Tier-1 parity is in-sample (E56) — deployable HIGH consensus
reaches Tier 2; F1-parity is not MCC-parity (Pro is more tile-precise). Landed
in commit `<pending>`.
