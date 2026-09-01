# Gemini 3.7 at deployment: the gain changes seats

> **Last revised**: 2026-09-01 (fourth cell harvested; the 2×2 grid,
> five-test family, N-ladders, and the 16-cell grid board complete).
> See [§ Changelog](#changelog) for revision history.

**Classification**: registered-by-card deployment test (card:
`planning/gemini37-55map-2026-08-29.md`; predictions D1–D7 and both
carried operating points committed before any deployment scoring).
Primary evaluation is corrected-F1 at 50 m against the canonical
adjudicated extended Ground Truth (GT), tile-level Matthews
Correlation Coefficient (MCC) alongside, on the established 55-map
machinery (per-sheet paired sign-swap permutation, 10,000 draws, seed
42; Benjamini–Hochberg (BH) False Discovery Rate (FDR) q = 0.05
across the declared five-test family).

## ⚠ Reference instruments — read first

This campaign's committed primaries are scored on the **canonical
adjudicated extended GT** (4,746 student + canonical-review
promotions; 5,160 references at 50 m) — the chain of
`results/stride55-2026-08-27/`. The **final 55-map board**
(`results/55map-final-board-2026-08-27/`) is scored on a different
instrument: the **ruling-21 standardised reference** (4,731 student +
279 extension = 5,010). Session 144's interim headlines compared
across the two ("arm 1 0.8494 vs incumbent 0.8502"; "arm 2 above the
entire board"), which mixes instruments. This document reports each
chain separately:

- **Canonical chain** (this campaign's primaries + committed
  incumbent values): incumbent B N=5 carried **0.8438**
  (`ladder.json`, 0.843775); B K=10 carried **0.8422**.
- **Standardised chain** (the board's instrument): incumbent
  B-N5-carried **0.8502**, board ceiling B-N10-oracle **0.8558**; the
  campaign cells re-evaluated on this instrument in
  § Board comparability below.

The substantive conclusions survive on both chains, but every delta
below names its chain.

## Headlines (committed carried points, canonical chain)

| Cell | Stack | Carried point | corrected-F1@50 | Precision | Recall | MCC |
|---|---|---|---:|---:|---:|---:|
| Arm 1 | 3.7 proposer + carried G3 verifier | (0.10, k5) | **0.8494** | 0.844 | 0.855 | 0.666 |
| Arm 2 | all-3.7 (3.7 proposer + 3.7 verifier) | (0.80, k5) | **0.8763** | 0.890 | 0.863 | 0.707 |
| Fourth cell | G3 Run B K=10 union + 3.7 verifier | (0.98, k10) | **0.8656** | 0.959 | 0.789 | 0.727 |
| Incumbent B N=5 | G3 proposer + G3 verifier (K=5) | (0.15, k5) | 0.8438 | 0.882 | 0.809 | — |
| Incumbent B K=10 | G3 proposer + G3 verifier (K=10) | (0.15, k10) | 0.8422 | 0.903 | 0.789 | 0.698 |

Union: 12,715 candidates from the 3.7 K=5 passes (vs ~44k estimated
from the G3 profile — the 3.7 proposer proposes ~3.5× tighter).

- **Arm 1 vs incumbent (canonical, like-for-like K=5)**: +0.0056 —
  below the 55-map MDE80 of 0.013. D1's pre-named informative failure
  stands: the proposer-seat GS gain (+0.018) did **not** transfer as
  a resolvable deployment win. (S144's "dead heat with 0.8502"
  compared across instruments; the canonical anchor is 0.8438.)
- **Arm 2 vs arm 1 (verifier seat)**: +0.0270 — the family gain lives
  in the verifier seat, at roughly twice D6's predicted +0.013.
- **Arm 2 vs incumbent (all-3.7 vs G3 stack)**: +0.0325 canonical.

## The sweeps: oracles and the transfer question

The PI's queued oracle question: did the carried points hit each
cell's deployment oracle?

| Cell | Carried | Carried F1 | Oracle point | Oracle F1 | Transfer gap | Hit exactly? |
|---|---|---:|---|---:|---:|---|
| Arm 1 | (0.10, k5) | 0.8494 | (0.15, k5) | 0.8662 | +0.0168 | NO |
| Arm 2 | (0.80, k5) | 0.8763 | (0.95, k5) | 0.8806 | +0.0043 | NO — but nearly |
| Fourth cell | (0.98, k10) | 0.8656 | (0.96, k9) | 0.8758 | +0.0102 | NO |

**The PI's oracle question answered**: arm 2's carried (0.80, k5) did
**not** land on the 55-map oracle exactly — but it came within
+0.0043 of it, and the oracle stayed in the same high-probability
region ((0.95, k5); P 0.9017 / R 0.8605 at the oracle). The
calibration shift transferred; only the exact threshold moved.

The instructive contrast is between the arms. Arm 1's carried
threshold — the GS screen's sweep best for the same stack — was
**not** the 55-map optimum: the G3-verifier arm re-opens a transfer
tax (+0.0168) of the order the within-Gemini-3 runs had collapsed to
near zero (S143: +0.0036/+0.0081), while the all-3.7 arm's tax
(+0.0043) sits inside that collapsed band. At its oracle (0.15, k5)
arm 1 would have reached 0.8662 (P 0.9172 / R 0.8205) — above the
canonical incumbent by +0.0224. The proposer-seat gain partially
exists; the GS-selected threshold failed to carry it across the
corpus change, and the failure is specific to the G3-verifier arm.

## The N-ladder: first-N rungs under both arms (canonical chain)

Card § 5 step 4's N ∈ {1, 3} rungs, derived by the gated stride55
ladder method (first-5 union rebuild exact at 12,715 / max centroid
drift 0.069 m; both carried points reproduced to 1e-6; probability
inheritance ≤ 10 m, unmatched 54 at N=1 and 3 at N=3). Rung oracles
are descriptive (screening protocol — no carried claims below N=5):

| Rung | Union | Arm 1 oracle | Arm 2 oracle |
|---|---:|---|---|
| N=1 | 8,426 | 0.8378 at (0.20, k1) | **0.8563** at (0.98, k1) |
| N=3 | 11,079 | 0.8645 at (0.15, k3) | **0.8790** at (0.95, k3) |
| N=5 (committed) | 12,715 | carried 0.8494 / oracle 0.8662 | carried 0.8763 / oracle 0.8806 |

Two patterns replicate from the Gemini-3 programme: **saturation by
N=3** (arm 2's N=3 oracle sits within 0.0016 of its N=5 oracle), and
the all-3.7 lattice staying at the probability scale's top on every
rung (D7 across the ladder). The cost headline: a **single 3.7 pass
under the 3.7 verifier (N=1, 0.8563) beats the canonical incumbent
five-pass Gemini-3 stack (0.8438)** on roughly one-fifth the proposer
spend (~$29 of the $144 K=5 token-basis proposer total).

## Paired tests (per-sheet permutation + BH, canonical chain)

Preview over the three fourth-cell-independent tests of the declared
five-test family (per-sheet sign-swap permutation, 10,000 draws, seed
42; BH q = 0.05 over the subset — the full family re-runs when the
fourth cell lands):

| Test | ΔF1@50 | p (two-sided) | BH sig. |
|---|---:|---:|---|
| D1: arm 1 − B N=5 (proposer axis, G3 verifier) | +0.0056 | 0.3488 | no |
| D6: arm 2 − arm 1 (verifier axis, 3.7 proposer) | +0.0270 | 0.0001 | **yes** |
| Diagonal: arm 2 − B N=5 (all-3.7 vs incumbent stack) | +0.0325 | 0.0001 | **yes** |

**The full five-test family (2026-09-01 harvest)** — BH q = 0.05
family-adjusted, `sweeps/sweep_oracle.json`:

| Test | ΔF1@50 | p | BH sig. |
|---|---:|---:|---|
| D1: arm 1 − B N=5 (proposer axis, G3 verifier) | +0.0056 | 0.3488 | no |
| D6: arm 2 − arm 1 (verifier axis, 3.7 proposer) | +0.0270 | 0.0001 | **yes** |
| Diagonal: arm 2 − B N=5 | +0.0325 | 0.0001 | **yes** |
| Fourth − B K=10 (verifier axis, G3 pool) | +0.0234 | 0.0001 | **yes** |
| Arm 2 − fourth (proposer axis, 3.7 verifier) | +0.0107 | 0.0738 | no |

**The grid's verdict**: both verifier-axis tests are significant
(+0.027 on the 3.7 pool, +0.023 on the G3 pool); both proposer-axis
tests are not. The family gain lives in the verifier seat on the
complete 2×2, not one diagonal. The fourth cell also takes the
grid's MCC crown (0.7268) and precision crown (0.9588) — the
discriminating 3.7 verifier on the noisy G3 pool trades recall for
precision hard.

## The grid board (16 cells, all-pairs + BH + tiers)

`grid-board/grid_board.json`: 120 pairs, 89 BH-significant, six
greedy-clique tiers. Tier 1 = arm 2's N5 and N3 oracles alone;
Tier 2 = arm2-N5-carried, fourth-N10-oracle, and **arm2-N3-carried**
— the practitioner cell shares the deployed tier at 3/5 proposer
cost; **both Gemini-3 incumbents sit in Tier 4 of six**. Named
contrasts, family-corrected: all five carried→oracle gaps are
significant (even arm 2's +0.0043, adj p = 0.0002) — threshold
transfer costs are sheet-consistent real effects at every scale;
N1→N3 is significant everywhere, while **N3→N5 is not significant
for arm 2 on either basis** (saturation at N=3 is statistical, and
arm 2's fourth-cell sibling saturates identically — ladder N=3
0.8688 vs N=5-inheritance 0.8697 with oracle prob_t pinned at 0.96
on every rung).

## Board comparability — completed

Fourth cell standardised-reference @50: **0.8732** [0.8649, 0.8810]
(P 0.9517 / R 0.8066) — above the board ceiling 0.8558, second only
to arm 2's 0.8825 among deployment cells on the board's instrument.

## Board comparability (standardised chain)

Both arms' carried detection sets re-evaluated with the board's exact
stage-2 instrument (`evaluate_detections.py`, best-available-gt-55maps
= ruling-21 standardised reference, 5,010 mounds, 14 buffers, BCa
bootstrap 10,000, seed 42):

| Cell | F1@50 (standardised) | 95 % CI | Board anchor |
|---|---:|---|---|
| Arm 1 carried | **0.8550** | [0.8465, 0.8630] | B-N5-carried 0.8502 [0.8416, 0.8582] — +0.0048, CIs overlap |
| Arm 2 carried | **0.8825** | [0.8746, 0.8897] | board ceiling B-N10-oracle 0.8558 — **+0.0267 above the whole board incl. oracles** |

The instrument offset is roughly uniform (standardised reads
~+0.005–0.006 above canonical for these cells), which is why the
substantive conclusions agree across chains: D1 stays an
unresolvable near-tie on both, and arm 2 clears the entire final
board **on the board's own instrument** — the S144 interim claim
survives the reference correction.
(The fourth cell's standardised evaluation appears in § The grid
board above.)

## Prediction verdicts D1–D7

| # | Bet | Prediction | Verdict |
|---|---|---|---|
| D1 | Headline vs B-Gemini-3 | carried above B-N5 by ≥ MDE80 0.013 | **INFORMATIVE FAILURE (pre-named)** — +0.0056 canonical, unresolvable |
| D2 | Direction of the gain | recall-led | **CONFIRMED** — arm 1 recall 0.855 vs incumbent 0.809; precision 0.844 vs 0.882 |
| D3 | Operating lattice | prob_t ∈ {0.10, 0.15}, k4–k5 | **CONFIRMED** — arm 1 oracle (0.15, k5) on the predicted lattice |
| D4 | Thinking volume | ≈ 276 t/tile on 55-map content | **CONFIRMED** — clean passes 265–277 t/call (run_1..run_5 metas; run_3's meta carries the known collapse accounting mismatch: 24,561 recorded calls vs ~9.2k calls' worth of tokens) |
| D5 | Cost | within card § 4 envelope | **PROVISIONAL PASS (token basis)** — proposer $144 (envelope $93–150), verifier arms $12.54 + $14.31; campaign ≈ $171 token-basis flex before the fourth cell. Billed-actual reconciliation ~2026-09-02 (3.7 SKU has billed ~0.6× token basis to date) |
| D6 | Arm 2 vs arm 1 | +≈0.013, direction positive | **CONFIRMED, magnitude 2×** — +0.0270, p = 0.0001, BH-significant |
| D7 | Arm-2 lattice | oracle prob_t ≥ 0.6 | **CONFIRMED** — 55-map oracle (0.95, k5); the calibration shift transfers |

## Changelog

### 2026-09-01 — Fourth cell harvested; grid complete

Verification completed 04:07 UTC through the storm-resilient loop
driver (seven rounds, five storm-killed; only round-7 usage survives
in run.meta.json — noted in the data commit). Harvest chain all
gates green: primary 0.8656 (n=4,246), ladder (N=3 saturation),
full five-test family (verifier axis significant on both edges,
proposer axis on neither), 16-cell grid board (six tiers; all
carried→oracle contrasts significant; arm-2 N3→N5 ns both bases),
standardised eval 0.8732. Data commit `a73d64346`.

### 2026-08-31 — Original publication

Initial findings for the 55-map Gemini 3.7 campaign: committed
carried-point primaries for both verifier arms (from Session 144);
the canonical-vs-standardised reference-instrument correction (S144's
interim headlines mixed the two chains — both substantive conclusions
survive on the correct instruments); both arm sweeps and oracles
(arm 1 gap +0.0168, arm 2 gap +0.0043 — the PI's
"carried-hit-oracle-exactly" answer is NO but nearly); the
three-test paired preview; board-instrument re-evaluations (arm 1
0.8550, arm 2 0.8825 vs ceiling 0.8558); verdicts D1–D4, D6–D7.
Fourth grid cell (57,482-candidate verification in flight at
publication) and the full five-test family marked [PENDING] in place.
