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

## Operating-point reading

This is a **characterisation** against known test-tile ground truth, not a
deployment prediction. The preregistered H3 analysis plan
(`analysis-summary.md` §H3) is "compare voted F1 vs single-pass mean F1" with
output "threshold sweep curves showing **optimal (N, threshold) combinations**".
So reporting each configuration's **best (N, threshold)** operating point is the
preregistered method — the study's purpose is to measure how well VLM symbol
extraction *can* localise mounds. Best-achievable performance is the deliverable.
Deployment generalisation to unseen maps is a separate question, answered by the
55-map runs (calibration → carried-forward production vs corrected student
ground truth, with the carry-forward − best delta).

1. **Operating-point sensitivity (co-headlined, not hedged).** The Tier-1
   Flash-consensus/Pro-single-pass parity is at the best (N, threshold) point
   (26-of-30). At the production **N=5** carry-forward point (text 4-of-5), the
   same pool reaches **Tier 2** (0.720), tying genuine Pro text at **T=0.7** —
   a **best − N5 delta of ≈0.094 F1**. This delta *is* a result (the within-test
   cousin of the carry-forward − best delta the 55-map analysis reports), not a
   limitation: the cross-architecture competitiveness is robust across the
   operating-point range.
2. **F1-parity is not MCC-parity.** The genuine Pro text leaders have higher
   tile-level discrimination (MCC 0.790, 11 tile FPs) than the Flash consensus
   champion (MCC 0.620, 41 tile FPs); Pro image is the overall MCC leader
   (0.85–0.91). The metric-dependent-winner pattern of the n1 board persists:
   Flash consensus matches Pro on localisation F1 but is less tile-precise.
3. **The diversity dividend itself is robust** to operating-point choice — the
   HIGH > minimal ordering holds at the production N=5 thresholds, at greedy
   4-of-5, and at the best (N, threshold).

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

The diversity-dividend statistical test (Session 103). Realises the registered
`pv-diag-384-consensus-calibration` sweep as a verified finding
(`diversity-dividend-384`, signed off). Both named claims confirmed: the
diversity dividend (HIGH > minimal consensus) is significant on F1 and MCC in
both modalities; consensus significantly beats matched single-pass at both the
best (N, threshold) and the production N=5 operating points; and the best Flash
HIGH-text consensus forms a three-member Tier-1 tie with the two genuine-Pro
single-pass text leaders. Framing (Session 103 discussion): the best
(N, threshold) operating point against test-tile ground truth is the
preregistered H3 characterisation (`analysis-summary.md` §H3), **not** an
in-sample limitation — the earlier E56-style "in-sample caveat" wording was
imported in error from the verifier prob_t rule (a distinct case; see E56
Update 2026-06-06) and has been replaced with an operating-point-sensitivity
reading. The best − N5 delta (≈0.094 F1) and the F1≠MCC asymmetry are reported
as characterisations, not hedges. Deployment generalisation is deferred to the
55-map analysis. Landed in commits `db582f1d`→`fd52bb82`→`811bc9b5` (harness +
finding + audit fixes) and the Session-103 reframe commit.
