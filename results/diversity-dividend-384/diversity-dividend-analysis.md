# Diversity dividend — consensus vs single-pass baseline (H3)

> **Last revised**: 2026-10-30 (the HIGH-text champion reads 0.816, not 0.817:
> 0.816471 had been rounded twice, PI ruling D69). Prior: 2026-10-15 (the
> 22-cell champions tiering restated on the
> consensus route that keeps each cluster's contributing tiles, PI ruling
> D60 (3): the four consensus champions rise by about 0.002 F1; tiers, tie set
> and verdicts unchanged; the 26-cell companion was not regenerated). Prior:
> 2026-06-06 (original publication — the diversity-dividend statistical test,
> Session 103). See [§ Changelog](#changelog) for revision history.

The **diversity-dividend test** asks two
linked questions (the second is preregistered **H3**, `osf/preregistration.md:501`;
the first — thinking-level diversity — is a post-registration question: the
registration fixes `thinking_level=minimal` (§8.2, §8.9) and registered H9's
diversity mechanisms are text, image, and temperature only — D17 audit U5) about consensus voting over multiple Vision Language Model
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
(26-cell). The 22-cell table was regenerated on 2026-10-15; the 26-cell
companion was not, so it still carries the four champions' 2026-06-06 values
(for example 0.814 for the HIGH-text champion).

### 1. Diversity dividend (HIGH > minimal consensus, matched modality)

| Modality | HIGH F1 | minimal F1 | ΔF1 | BH-p | ΔMCC |
|---|---:|---:|---:|---:|---:|
| Text | 0.816 | 0.663 | **+0.153** | <0.001 | +0.239 |
| Image | 0.752 | 0.682 | **+0.070** | <0.001 | +0.272 |

Both significant, on both F1 and MCC. The HIGH-thinking pools take the larger
consensus gain: more varied proposals let a high vote threshold prune their
false positives (the HIGH-text champion carries 41 tile-level FPs vs the
minimal-text champion's 115).

### 2. Consensus beats matched single-pass — everywhere, including deployable

Every consensus champion significantly beats its **matched within-pool**
single-pass baseline (same model, modality, thinking, temperature):

| Pool (T=0.7) | single-pass F1 | best-F1 consensus | ΔF1 | deployable N=5 | ΔF1 (deploy) |
|---|---:|---:|---:|---:|---:|
| `flash-high-text` (HIGH) | 0.387 | 0.816 | +0.429 | 0.720 (4-of-5) | +0.333 |
| `flash-high-image` (HIGH) | 0.499 | 0.752 | +0.254 | 0.727 (3-of-5) | +0.228 |
| `flash-minimal-text` (min) | 0.488 | 0.663 | +0.175 | 0.602 (4-of-5) | +0.114 |
| `image-n5` (min) | 0.553 | 0.682 | +0.129 | 0.644 (3-of-5) | +0.091 |

The deployable N=5 columns come from the 26-cell companion, which was not
re-scored on 2026-10-15.

All eight contrasts BH-p < 0.001. Consensus voting lifts F1 over a single pass
at both the in-sample best threshold and the honest a-priori N=5 deployable
threshold.

### 3. Cross-architecture headline — Flash consensus reaches the Pro tier

**Tier 1 (the `tie_set`) is a three-member statistical tie:**

| Cell | F1@20 m | MCC |
|---|---:|---:|
| `flash-high-text` consensus (26-of-30) | 0.816 | 0.620 |
| `pro-text-high-t-0-0` single pass (genuine Pro) | 0.804 | 0.790 |
| `pro-text-medium-t-0-0` single pass (genuine Pro) | 0.792 | 0.790 |

The permutation cannot separate the Flash consensus champion from the genuine
Gemini 3 Pro single-pass leader (p = 0.527, BH-p = 0.57). **Cheap Flash
consensus reaches the expensive Pro single-pass tier on localisation F1.**

## Operating-point reading

This is a **characterisation** against known test-tile ground truth, not a
deployment prediction. The registered H3 analysis plan
(`osf/preregistration.md:519-521`; citation corrected 2026-07-28, D17 audit U4)
is "Compare single-pass mean F1 vs voted F1 at each (N, threshold) combination"
with "threshold sweep curves" and "Identify **optimal (N, threshold)**" as
outputs.
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
   a **best − N5 delta of ≈0.096 F1** (≈0.094 before the 2026-10-15
   restatement of the best point; the N=5 point, from the 26-cell
   companion, was not re-scored). This delta *is* a result (the within-test
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

### 2026-10-30 — The HIGH-text champion's F1 rounded once

**Trigger.** PR #52's claim-row walk-through (PI ruling D69, on R4-04): the
26-of-30 HIGH-text consensus champion scores 0.816471
(`tiering-champions/tiering_20m.json`, rank 1, `observed_micro_f1`), which is
0.816 at three decimals; the 2026-10-15 restatement wrote 0.817 by rounding
its four-decimal 0.8165 a second time.

| Place | Before | After |
|---|---|---|
| § 1, diversity dividend, text HIGH F1 | 0.817 | 0.816 |
| § 1, single-pass baseline table, best-F1 consensus | 0.817 | 0.816 |
| Tier 1 table, `flash-high-text` consensus | 0.817 | 0.816 |

**What did NOT change**: the deltas beside them (+0.153 and +0.429 hold on
the unrounded values), every tier and verdict.

**Commit**: see `git log` for this entry's date.

### 2026-10-15 — The champions tiering restated on the consensus route (PI ruling D60 (3))

**Refresh trigger**: PI rulings D60 (3) and D62 (2)
(`planning/pi-decisions-2026-09-20.md`), executed by the S164
restatement pass (`reports/s164-agent-records/restatement-pass.md`,
§ 1.5). PR #37 (fix `4e9d659ab`;
`reports/s163-agent-records/d60-3-consensus-route.md`) made the
in-memory consensus route keep each cluster's contributing tiles, so a
consensus detection is scored on its origin sheet, as its file already
was. Each of the four consensus champions gains about one detection's
worth of F1 (+0.0021 to +0.0024 micro-F1); no single-pass cell moves,
except one MCC in the fourth decimal (`baseline-flash-image-minimal-t-0-7`,
0.3295 → 0.3296). `consensus_vs_baseline_tiering.py` regenerated
`tiering-champions/` (the 22-cell board, which `e45_bootstrap_pairings.py`
gates H3 against) on sapphire in two independent runs that agree apart
from timestamps, committed at `08af04cf3`; it equals the S3 record's
prediction. `tiering-with-deployable/` (the 26-cell companion) was
**not** regenerated in this pass, so its four deployable cells and its
copies of the champions keep their 2026-06-06 values; whether the
deployable cells move under the fixed route was not measured.

| Quantity | Before | After |
|---|---|---|
| HIGH-text champion (26-of-30), F1 @ 20 m (eval; micro) | 0.8141; 0.814118 | 0.8165; 0.816471 |
| HIGH-image champion (7-of-10) | 0.7500; 0.750000 | 0.7524; 0.752381 |
| Minimal-image champion (8-of-10) | 0.6803; 0.680301 | 0.6825; 0.682454 |
| Minimal-text champion (29-of-30) | 0.6611; 0.661140 | 0.6632; 0.663212 |
| Diversity dividend ΔF1, text; image | +0.153 (0.1530); +0.070 (0.0697) | +0.153 (0.1533); +0.070 (0.0699) |
| Consensus − matched single pass: HIGH text, HIGH image, minimal text, minimal image | +0.427, +0.251, +0.173, +0.127 | +0.429, +0.254, +0.175, +0.129 |
| Flash HIGH-text consensus − Pro single-pass leader: ΔF1; p; BH-p | +0.0096; 0.6163; 0.662 | +0.0120; 0.5266; 0.569 |
| Best − N5 delta (HIGH text; the N5 side not re-scored) | ≈0.094 | ≈0.096 |

Sources: `tiering-champions/tiering_20m.json` (`ranking`,
`headline_contrasts`) and, for the N5 side of the delta,
`tiering-with-deployable/tiering_20m.json`
(`deploy-flash-high-text-n5-4of5`, 0.720314, unchanged); each read at
`718d0ee08` (before) and at the pass's head (after). The tables above
quote the 22-cell render's three-decimal values (`tiering_20m.md`).

**What did NOT change**: 197 of 231 pairs significant; seven tiers; the
three-member Tier 1 (`tie_set`) and its order; every headline contrast's
significance; every MCC quoted (0.620, 0.790, the ΔMCC +0.239 and
+0.272, the 41 and 115 tile false positives); the single-pass baselines;
both claims (the diversity dividend, and consensus beating matched
single-pass) and the cross-architecture tie. Older changelog entries
keep the figures they reported.

**Commits**: `08af04cf3` (the regenerated champions tiering); this
document refresh in the restatement pass's document commit.

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
registered H3 characterisation (`osf/preregistration.md:519-521`), **not** an
in-sample limitation — the earlier E56-style "in-sample caveat" wording was
imported in error from the verifier prob_t rule (a distinct case; see E56
Update 2026-06-06) and has been replaced with an operating-point-sensitivity
reading. The best − N5 delta (≈0.094 F1) and the F1≠MCC asymmetry are reported
as characterisations, not hedges. Deployment generalisation is deferred to the
55-map analysis. Landed in commits `db582f1d`→`fd52bb82`→`811bc9b5` (harness +
finding + audit fixes) and the Session-103 reframe commit.
