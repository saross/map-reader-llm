# Verifier-robustness — findings

> **Last revised**: 2026-06-11 (Session 113: the Flash 3.5 role
> permutations — proposer loss resolved at p = 0.035, verifier losses are
> cost-rule ties — and the second-wave manifest registration). See
> [§ Changelog](#changelog) for revision history.

This document is the citable home for the **verifier-robustness** programme
(Sessions 109–111). It answers the questions that bear on **every n=1 verified
cell in the paper** — the Stage-D PV grid, the 55-map deployment oracle, and all
proposer-verifier cells. Pre-run design and gating are recorded separately in
[`outputs/verifier-robustness/experiment_intent.md`](../../outputs/verifier-robustness/experiment_intent.md).

**Headline**: the production carry-forward verifier — **gemini-3-flash, T=0.0,
minimal thinking, n=1** — is **vindicated on every axis tested**. Run-to-run
non-determinism is negligible at F1 (§ 2); a higher-temperature *consensus*
verifier does **not** help (§ 7); the optimal *input* is a pre-filtered
proposer pool, not the permissive union (§ 3); thinking level and temperature
make no significant F1 difference at N=5, and high thinking *hurts* a single
pass (§ 8); a stronger (Pro) verifier model buys nothing (§ 9); at equal cost,
passes are better spent on the proposer than the verifier (§ 10); and the
0.8951 operational maximum is **not** significantly above the 0.890 headline
(§ 11). The whole 6→35-pass budget ladder sits in **one statistical tier**
(§ 12).

**The meta-rule: on a within-noise tie, take the cheaper configuration** —
n=1 over consensus, minimal over high thinking, Flash over Pro, proposer
passes over verifier passes. The carry-forward verifier is cost-optimal
everywhere it has been tested. **SCOPE QUALIFICATION (§ 16, Obs 362)**: a
tie is only as strong as the instrument that measured it — the GS
minimal-vs-high tie *reversed* at 55-map deployment (−0.030,
tier-separated), so where deployment evidence exists it overrides a
characterisation tie, and GS ties at ±0.03 resolution do not licence
production extrapolation.

- **Stage 1** (T=0.0): verify the **1-of-5 proposer union** of the two
  Gold-Standard consensus+PV cells (the leading 384 `flash-high-text` and the
  256 rescue cell) at **N=5**, deriving every proposer-vote input level
  (1of5→5of5) as a free post-hoc subset — § 2 (determinism), § 3 (input).
- **Stage 2** (temperature): a per-cell greedy snowball climbing the verifier
  temperature 0.3 → 0.7 → 1.0 on the **≥3-of-5 band** — § 7.

## 1. The run

| field | value |
|---|---|
| verifier config | `prompts/configs/verify_adversarial-text.json` (text-only adversarial) |
| model | `gemini-3-flash-preview` |
| thinking / temperature | minimal / **0.0** |
| iterations (N) | 5 |
| execution | realtime, **flex** |
| cells | `384-flash-high-text-1of5-union` (3,736 cands), `256-text-1of5-union` (2,558) |
| calls / cost | 31,470 (0 failures) / **$21.93 flex** |
| scoring | point F1@20 m + tile-MCC, EPSG:32635, `lib_advanced_metrics.score_detection_set` |
| driver / analysis | `scripts/run_verifier_robustness.py` / `scripts/analyse_verifier_robustness.py` |

The accepted set for each `(proposer-vote k, verifier rule, prob_t)` cell was
scored in-process; "verifier rule" is one of the five single iterations
(`iter1…5`), the N-run consensus at vote threshold `vt1…5`, or the per-candidate
mean probability.

## 2. Determinism — n=1 is vindicated

**The headline robustness result.** T=0.0 is not bit-deterministic — at the
candidate level **~3 % of candidates flip** accept/reject across the 5 iterations
(256 cell: 81 / 2,558 split at prob_t 0.2; cf. the free e47 `v1`/`v2` prior of
2.96 %). But that flicker **washes out at the aggregate (tile) level**: the F1
spread across the 5 independent single runs is negligible.

| cell | proposer level | single-run F1 mean | **SD (5 runs)** | min–max spread |
|---|---|---:|---:|---|
| 384 | 4of5 | 0.8601 | **0.0072** | 0.8498–0.8689 |
| 384 | 3of5 | 0.8472 | 0.0032 | 0.8426–0.8525 |
| 256 | 5of5 | 0.8555 | 0.0025 | 0.8519–0.8585 |
| 256 | 3of5 | 0.8526 | 0.0039 | 0.8467–0.8578 |

Across **all** proposer levels the single-run F1 SD is **0.0025–0.0072** (worst
spread ~0.019). Two corollaries:

- **5-run consensus ≈ single-run mean.** At every level the majority-vote
  consensus F1 lands within ~0.001–0.01 of the single-run mean (e.g. 384/3of5:
  consensus 0.8488 vs mean 0.8472). There is **no consensus benefit at T=0.0** —
  expected, since five near-identical T=0.0 passes carry no diversity to pool.
  *Stage-3 refinement (§ 8): this reading applies to the **majority** vote; a
  permissive aggregation (vt1 union at T=0.0, mean-probability at T=0.3) does
  beat the expected single pass by ~+0.012.*
- **The verifier-vote threshold barely moves F1.** At the 384 optimum (4of5,
  prob_t 0.15) the vt1→vt5 sweep spans only 0.8522–0.8722; at the 256 optimum
  (5of5, prob_t 0.15), 0.8396–0.8620.

**Consequence for the paper**: every n=1 verified cell carries only **~±0.005 F1**
of hidden run-to-run noise (worst-case single-draw deviation ~0.01), far below
the tier gaps the paper reports. **The n=1 verification protocol is sound** — the
Stage-D grid, the 55-map oracle, and all PV cells do not need re-running at N>1
for determinism reasons.

## 3. Proposer input — feed the verifier a filtered pool, not the union

The proposer-vote sweep (best F1@20 m per input level, over the reproducible
consensus/mean rules):

| proposer input | 384 F1@20 m (MCC) | 256 F1@20 m (MCC) |
|---|---:|---:|
| 1of5 (union) | 0.734 (0.778) | 0.827 (0.762) |
| 2of5 | 0.834 (0.786) | 0.846 (0.766) |
| 3of5 | 0.859 (0.783) | 0.861 (0.757) |
| **4of5** | **0.872** (0.762) | 0.860 (0.750) |
| 5of5 | 0.844 (0.732) | **0.864** (0.750) |

- **The permissive 1-of-5 union is the *worst* input at both cells.** The
  verifier does **not** rescue the single-pass false-positive flood: as the
  proposer is loosened, precision falls faster than recall rises, so F1 drops.
- **384 is an inverted-U with a clear peak at 4-of-5 (0.872).** Too strict
  (5of5) loses real mounds; too loose (≤2of5) drowns in FPs.
- **256 is a plateau from 3-of-5 up (~0.86).** Smaller tiles tolerate a looser
  input, but the union still trails.
- **MCC is comparatively flat** (0.73–0.79) even where F1 swings 0.13 — the
  tile-level discrimination survives the FP flood that point-level F1 punishes
  (the familiar F1-vs-MCC divergence).

This **refines the Stage-D "verifier rescues 256" finding** (Obs 352): the
verifier rescues a *moderately filtered* proposer pool well, but the permissive
union much less so. The optimal *input* to the verifier is a pre-filtered
consensus (≥3–4 of 5), not the maximal-recall union.

## 4. Implications

1. **n=1 backbone vindicated** — no re-runs needed for determinism (§ 2).
2. **Image-proposer tranche** (pencilled `384-flash-high-image-1of5-union`):
   **do not pay for the full 1-of-5 image union.** Verify the **≥3-of-5 band**
   (506 cands, ~$1.76 flex) rather than the union (2,017 cands, ~$7.03) — the
   text patterns show the permissive end is dominated. Score the image
   consensus-only F1 first (free) to confirm it is high-performing.
3. **Temperature stages teed up** — the absence of any consensus benefit at
   T=0.0 (§ 2) is the baseline against which the higher-T *consensus* verifier
   (0.3 → 0.7 → 1.0) is tested: if a diversity dividend exists on the verifier
   side, it must appear as T rises and the iterations decorrelate.

## 5. Caveats

- **5-pass vs 30-pass proposer.** These cells use a 5-pass proposer family (so
  the input axis is in fifths). The Stage-D headline 384 cell used a 30-pass
  consensus (16of30); the 5-pass 384 optimum here (0.872 at 4of5) sits just
  below the 30-pass Stage-D figure (0.890), consistent with fewer proposer
  passes. The *patterns* (determinism, proposer-input shape) are the
  deliverable, not a new headline F1.
- **T=0.0 only; text-only.** Stage 1 is the production temperature and the
  text proposer/verifier. Determinism at higher T, and on the image-proposer
  crop distribution, are later stages.
- **Population SD** (`pstdev`, ÷N) is reported for the 5 runs treated as the
  stochastic population at T=0.0; a sample SD (÷N−1) would be ~1.12× larger.

## 6. Artefacts

- Grid + summary: `results/verifier-robustness/robustness_{grid,summary}_T0.0.json`
- Raw verifier outputs: `outputs/verifier-robustness/<cell>/T0.0/verified/`
  (`probabilities.json` per-iteration, `consensus.json`, `run.meta.json`)
- Driver / analysis: `scripts/run_verifier_robustness.py`,
  `scripts/analyse_verifier_robustness.py`
- Reusable scorer: `lib_advanced_metrics.score_detection_set` (bootstrap-free
  point F1/MCC for grid analyses)
- Stage-2 artefacts: `results/verifier-robustness/snowball_summary.json`,
  `robustness_{grid,summary}_T0.3.json`; `outputs/verifier-robustness/<cell>/T0.3/verified/`;
  driver `scripts/run_verifier_temperature_snowball.py`
- Stage-3 artefacts (§ 8–10): `matrix_tiering.json` + `matrix-sets/` (best-op
  geojsons), `robustness_{grid,summary}_T0.{3,7}-high.json`,
  `robustness_{grid,summary}_T0.7.json`, `high_thinking_prior.log`,
  `nof10_comparison.log`, `pro_pv.log`; scripts `run_stage3_matrix.sh`,
  `tier_verifier_matrix.py`, `score_high_thinking_prior.py`,
  `score_nof10_comparison.py`, `score_pro_pv.py`
- Operational-maximum artefacts (§ 11):
  `robustness_{grid,summary}_T0.3-16of30.json` (re-homed from the T0.3 names
  in Session 111 after an overwrite — see `--out-suffix` in
  `analyse_verifier_robustness.py`), `opmax.log`,
  `opmax_vs_headline_permutation.json` + `opmax-sets/`;
  script `permutation_opmax_vs_headline.py`
- Pareto artefacts (§ 12): `pareto/pareto_leaderboard.{json,png}`,
  `pareto/pareto_build.log`, the cheap6/nof10 best-op geojsons;
  script `build_pareto_leaderboard.py`
- Pre-run intent: `outputs/verifier-robustness/experiment_intent.md`

## 7. Stage 2 — a higher-temperature consensus verifier does not help

The Stage-1 finding that consensus ≈ single-run at T=0.0 (§ 2) left one
hypothesis open: a *higher*-temperature verifier decorrelates the N passes, so a
higher-T **consensus** verifier might mirror the proposer-side diversity
dividend. Stage 2 tested it with a **per-cell greedy snowball**
(`run_verifier_temperature_snowball.py`): verify the **≥3-of-5 band** (the
productive band from § 3) at N=5, climbing T=0.3 → 0.7 → 1.0, advancing a cell
to the next temperature only if its best-consensus F1@20 m beats its *own*
previous temperature by > 0.005 (the § 2 noise floor). Each tile size climbs
independently. Held constant: model, **minimal thinking**, band, N=5, flex.

**Result: both cells stalled at the first rung (T=0.3); T=0.7 and T=1.0 never
ran.**

| cell | T=0.0 (best consensus) | T=0.3 | Δ | verdict |
|---|---:|---:|---:|---|
| 384-flash-high-text ≥3of5 | 0.8722 | 0.8739 | **+0.0017** | stall (within noise) |
| 256-text ≥3of5 | 0.8637 | 0.8582 | **−0.0055** | stall (worse) |

The higher-T **consensus verifier hypothesis is rejected**. Raising verifier
temperature produces more *noise* diversity (the 256 inter-iteration split rose
3.2 % → 5.7 % at T=0.3) but no *signal* diversity: the consensus of noisier
passes ≈ the clean T=0.0 result for 384, and is slightly worse for 256. The
proposer-side diversity dividend (HIGH-thinking, high-T *proposer*) does **not**
transfer to the verifier's per-candidate adversarial judgement. **The T=0.0
carry-forward verifier stands as optimal.** Cost: one rung, ~$8.71 flex (the
snowball's early stop saved the T=0.7/1.0 spend).

**Thinking axis: CLOSED in Stage 3 (§ 8)** — the free on-disk HIGH-thinking
prior was scored, the medium prior alongside it, and the full thinking ×
temperature matrix run and tiered. High thinking *hurts* a single verifier
pass and merely reaches parity under consensus.

## 8. Stage 3 — the thinking × temperature matrix is one statistical tier at N=5

Stage 3 completed the verifier configuration space: a **thinking (minimal/high)
× temperature (0.0/0.3/0.7) matrix** on the 384 ≥3-of-5 band (855 candidates,
N=5; three new cells × 4,275 calls, est **$20.86 flex** —
`planning/verifier-robustness-stage3-384-cells.json`), tiered with the
project-canonical round-robin (`scripts/tier_verifier_matrix.py`: 15 pairs,
10k tile-swap, seed 42, BH-FDR q=0.05, greedy-clique —
`matrix_tiering.json`).

| rank | config | F1@20 m | tier | best operating point |
|---|---|---:|---:|---|
| 1 | high T0.3 (N=5) | 0.8764 | 1 | 4of5 / consensus_vt5 / pt0.3 |
| 2 | min T0.3 (N=5) | 0.8739 | 1 | 4of5 / mean / pt0.15 |
| 3 | high T0.7 (N=5) | 0.8739 | 1 | 4of5 / consensus_vt5 / pt0.4 |
| 4 | min T0.0 (N=5) | 0.8722 | 1 | 4of5 / consensus_vt1 / pt0.15 |
| 5 | min T0.7 (N=5) | 0.8709 | 1 | 4of5 / consensus_vt2 / pt0.2 |
| 6 | **high T0.0 (n=1)** | **0.8519** | **2** | 4of5 / mean / pt0.5 |

- **All five N=5 configurations are ONE tier** (0/10 pairs among them
  significant): neither temperature nor thinking level moves F1 once the
  verifier runs at N=5. The only Tier-2 cell is the *single-pass* high-thinking
  prior — all 5 significant pairs are it-vs-others.
- **High thinking HURTS a single verifier pass.** At the 4-of-5 input:
  minimal n=1 0.8659 > medium 0.8545 > high 0.8519
  (`high_thinking_prior.log`, $0 on-disk re-scores). The adversarial prompt
  plus more thinking produces more spurious rejections and lower recall;
  consensus rescues high thinking back to tier parity.
- **What high thinking buys at N=5 is MCC, not F1**: high T0.3 MCC 0.789 vs
  minimal T0.3 0.771 (+0.018) at ~3× the verifier cost.
- **Aggregation refinement** (corrects the § 2 majority-vote reading): a
  PERMISSIVE consensus beats the *expected* single pass by ~+0.012 — at T=0.0
  the vt1 union (0.8722 vs single-run mean 0.8601), at T=0.3 the
  mean-probability rule (0.8739). Strict/unanimous voting hurts. Note
  `mean-prob` is a real materialisable operating point (average the five
  probabilities, threshold once); the single-pass mean is **not** a detection
  set — it is E[F1] over five separate sets.

## 9. Model roles — Pro is a better proposer, an equal (so dearer) verifier

`gemini-3.1-pro-preview` artefacts already on disk allowed a $0 re-score
(`pro_pv.log`):

- **As a bare proposer Pro wins its tiers**: single-pass 0.763, consensus
  0.836 (`results/leaderboard/per-architecture/cross-architecture-era2_20m_f1.md`).
- **As a PV proposer Pro loses**: Pro 5-pass + Flash verifier 0.8491, + Pro
  verifier 0.8506 (both 3of5 / pt0.15) ≪ Flash 5-pass + verifier 0.8739. The
  verifier needs a **high-recall** proposer to prune; Pro's 504-candidate pool
  is already precise, leaving the verifier little to do.
- **The verifier model barely matters on the PRO pool** (Pro-vf 0.8506 ≈
  Flash-vf 0.8491): there, the recall ceiling binds everything. **Refinement
  (S112, unswept-pools sweep)**: on the high-recall Flash HIGH 5-pass union
  the verifier model DOES matter — the Pro verifier scores **0.8792** vs the
  Flash carry-forward's 0.8641 (+0.015, raw p = 0.019; post-hoc-selected
  pair, hypothesis-generating), statistically tied with the headline
  (p = 0.41) and min11 (p = 0.76). It is nonetheless **dominated by min11 on
  both cost and F1** (~$10 of Pro verifier calls), so the frontier and the
  cheap-Flash-verifier production choice stand. (Flex rates, recorded June
  2026: Flash 3 $0.25/$1.50, Flash 3.5 $0.75/$4.50, Pro 3.1 $1.00/$6.00 per
  1M in/out.)

## 10. Compute allocation — spend passes on the proposer, not the verifier

At approximately equal pass budgets (`nof10_comparison.log`, $0 re-score):
**10-proposer + 1-verifier (11 passes) 0.8769** (6of10 / pt0.2) ≥
**5-proposer + 5-verifier (10 passes) 0.8739** (minimal) / 0.8764 (high).
Proposer diversity dominates verifier diversity at equal cost — consistent
with § 7 (no verifier-side diversity dividend) and § 2 (verifier flicker
washes out). Both sit at ~98.5 % of the 30-pass headline 0.890.

## 11. Operational maximum — verifier consensus does NOT lift the 30-pass proposer

The best-available stack was tested: the **16-of-30 headline proposer pool**
(729 candidates) re-verified at **N=5 minimal T=0.3 consensus** (3,645 calls,
**$2.54 flex**; `robustness_{grid,summary}_T0.3-16of30.json`). Best operating
point: consensus_vt3 / pt0.15, 423 accepted — **F1@20 m 0.8951, MCC 0.794**,
vs the registered n=1-verifier headline **0.8902** (412 accepted, pt0.2).

**The +0.0049 lift is NOT significant**: paired tile-swap permutation
(10k, seed 42, two-sided, 487 tiles) gives **p = 0.363** — the observed
difference sits at the null SD (0.0050)
(`opmax_vs_headline_permutation.json`, verification gates reproduced both
cells exactly). Per the meta-rule, **30-prop + n=1 verifier (0.890) stays the
practical ceiling**; 0.8951 is a numerical high only. This is the 30-pass
confirmation of § 2/§ 8: verifier consensus adds nothing the cheap single
pass does not already provide.

## 12. The pass-budget Pareto board — the whole ladder is one tier

The passes-vs-F1 board (`scripts/build_pareto_leaderboard.py`;
`pareto/pareto_leaderboard.{json,png}`; the 6-pass cheap end scored fresh
here, every other rung gate-verified against its committed record):

| total passes | config (proposer + verifier) | F1@20 m | MCC | best op |
|---:|---|---:|---:|---|
| 6 | 5-prop + n=1 vf (**cheap end, new**) | 0.8641 | 0.769 | 4of5 / pt0.15 |
| 10 | 5-prop + N=5 min T0.3 vf | 0.8739 | 0.771 | 4of5 / mean / pt0.15 |
| 11 | 10-prop + n=1 vf | 0.8769 | 0.790 | 6of10 / pt0.2 |
| 31 | 30-prop (16of30) + n=1 vf (**headline**) | 0.8902 | 0.790 | pt0.2 |
| 35 | 30-prop (16of30) + N=5 vf (opmax) | 0.8951 | 0.794 | vt3 / pt0.15 |

Context rows: high-thinking 10-pass 0.8764 (tied with minimal, § 8); Pro
6-pass 0.8491/0.8506 (§ 9).

**Round-robin result: 0/10 pairs significant after BH-FDR → ONE statistical
tier from 6 to 35 passes.** Adjacent rung-steps are clearly noise (raw p
0.03–0.79). The spans are more interesting: cheap6 vs opmax35 (+0.031) has
raw p = 0.012 but BH-adjusted 0.096 — **suggestive that the 30-pass rungs
genuinely lead, not confirmed at q = 0.05**. Two honest readings, stated in
order of evidential weight:

1. **The 487-tile GS instrument cannot resolve a +0.03 F1 difference at this
   significance standard** (the familiar GS-plateau resolving-power limit,
   Obs 347). The point estimates climb monotonically and the per-rung
   operating points are stable, so the ladder ordering is probably real but
   unprovable in-sample.
2. **Every rung is statistically defensible.** By the meta-rule, the budget
   recommendation is the cheap end: **6 passes ≈ 0.864** — ~97 % of the
   35-pass numerical maximum at ~17 % of the pass budget. The 0.890
   headline (31 passes) remains the showcase/ceiling configuration.

## 13. Minimal-thinking rungs — the diversity dividend does not survive the verifier

At equal pass count under PV, MINIMAL-thinking proposers reach statistical
parity with HIGH on the GS instrument (min6 0.8784 true-merge / 0.8708
n30-lineage vs high6 0.8641, p = 0.66; min11 0.8835 vs high11 0.8769,
p = 0.59; min11 vs the 31-pass headline p = 0.56 —
`min_vs_high_permutations.json`, `min6_true_makeup.json`). **Mechanism**
(`pool_recall_ceilings.json`, `zero_diversity_anchor.json`): the verifier
shifts the binding constraint from precision to **pool recall**; T = 0.7
sampling at minimal thinking saturates Flash's reachable recall in ~5
passes (0.9195 — the 10-pass lineage adds *zero* new GT mounds); HIGH
thinking adds volume (union/pass 2.46 vs 1.44) but only +0.023 ceiling.
The zero-diversity anchor (1 × T=0.0 pass + n=1 vf) scores 0.8142 — so
temperature diversity buys +0.057, ~60 % of it via the ceiling lift —
while carrying the board's second-best tile-MCC (0.833). min11 holds the
best MCC on the PV board (0.807). The consensus-era diversity dividend
(Obs 141) is real for consensus-only architectures and **obsolete under
PV** (Obs 359). *But see § 16: GS parity did not transfer to deployment.*

## 14. Flash 3.5 — wins in no role at the minimal operating point

The 2×2×2 tranche (proposer × verifier model × n∈{5,10}, ~$34 flex,
method-matched n=5 derivation per `first5of10-validation/`): as a **bare
proposer** Flash 3.5 ties Flash 3 (0.6196 vs 0.6204); as a **PV proposer**
it loses −0.036 (0.8480 vs 0.8835 under the same F3 verifier) — its union
is 1,132 candidates vs Flash 3's 1,939 with **53 % at 10/10 votes**
(union/pass 1.32): the Pro pattern of consistency-without-coverage, and PV
needs coverage; as a **verifier** it loses −0.012..−0.015 on both pools at
3× the price. Targeted permutations (S113, the tests § 11 of the dossier
left pending; `results/flash35-2x2/flash35_permutations.json`): the
**proposer-role loss is statistically resolved** (−0.0355, p = 0.035 raw;
marginal under BH across the three role tests), while both verifier-role
losses are within-noise ties (p = 0.17 own-pool, p = 0.10 F3-pool) — so
the verifier verdict rests on the cost meta-rule (Obs 357: a tie at 3×
the price loses). The all-Flash-3 stack stands (`results/flash35-2x2/`,
harness self-validated by reproducing min11 exactly).

## 15. Pareto v2 — the cost-weighted frontier

The passes-axis board (§ 12) is superseded by the cost-weighted v2
(`pareto/pareto_v2.{json,png}`; proposer-centric rung names — the old
"cheap6" is **high6**, the third most expensive way to buy ~0.87). Cost
model: measured verifier rate ($0.000697/call), proposer pass from
measured per-call tokens at F3 flex rates, HIGH = 3× minimal; **flex ≡
batch pricing**. All seven rungs remain ONE statistical tier (0/21 pairs).

| rung | F1@20m | GS run | 55-map production | frontier |
|---|---:|---:|---:|---|
| min6 | 0.8784 | $3.81 | ~$67 | ✓ |
| min11 | 0.8835 | $6.75 | ~$118 | ✓ |
| high6 | 0.8641 | $10.65 | ~$187 | dominated |
| high5+5vf | 0.8739 | $11.03 | ~$193 | dominated |
| high11 | 0.8769 | $20.19 | ~$354 | dominated |
| high31 (headline) | 0.8902 | $48.81 | ~$856 | ✓ |
| high35 (opmax) | 0.8951 | $50.84 | ~$892 | ✓ |

Costs recalibrated 2026-06-11 to the TM run's MEASURED token load
(~$9.40 per 8,541-tile minimal pass at flex; the earlier smoke-derived
model under-priced proposer passes 1.8×); efficient set unchanged.
Production costs scale both components by the tile factor (8,541/487);
crops/tile from the GS pools (the 55-map corpus is sparser → slight
upper bounds). **The F1 column is GS-characterised — see § 16 before
reading the min rungs as production recommendations.**

## 16. The deployment reversal — scope-qualifying the meta-rule

The min6 recipe has *already run* at production: it is the
`55maps-text-min-generalisation` deployment (config verified at source —
same model, prompt, T = 0.7, minimal thinking, 5-pass + carry-forward
verifier). On the 55-map canonical-GT board at 50 m, **TM-k3 (0.8127,
Tier 3) sits two tiers below TH7-k3 (0.8425, Tier 1)** at the matched
threshold — the GS tie (minimal ahead +0.007, ns) **reversed by −0.030**
on the instrument that resolves (24/28 pairs significant on the
refreshed 8-cell board, S113; 18/21 on the original 7-cell). The full
transfer picture (`results/55map-leaderboard/gs-vs-55map-transfer.md`,
@ 50 m): text HIGH −0.048, image −0.078, text MIN −0.087 — GS clustering
at 0.88–0.90 concealed differential deployment robustness, and minimal
text *led* on GS before degrading hardest. Interpretation (Obs 362): not
a contradiction but bounded ignorance resolved — the 487-tile instrument
cannot resolve ±0.03; HIGH thinking's diversity plausibly earns its keep
on the diverse 55-map sheets, and the § 13 recall-ceiling saturation may
be GS-specific. **Consequences**: (a) the meta-rule holds only where the
tie's instrument could detect a difference of consequence; (b) deployment
evidence overrides characterisation ties — the deployment-evidenced
production text config is HIGH thinking at k3; (c) **ANSWERED 2026-06-11
(Run B, ~$60)**: pass count closes about HALF the thinking gap — the
min11 uplift (10 minimal passes + band verifier) scores **0.8290** @ 50 m
(5of10/pt0.15), significantly above TM-k3 (+0.0163, p < 0.0001) and
significantly below TH7-k3 (−0.0134, p = 0.0026). Both steps resolve, so
the production choice is a genuine cost/quality trade (~$105 for 0.829
vs ~$150 for 0.843 at recalibrated production rates), not a tie; note
the deployment optimum again sat looser than GS (5of10 vs the GS-best
6of10 — the k3 lesson recurring at n = 10); (d) **CLOSED 2026-06-11**: the
T0.3 proposer is now GS-characterised (Run A, $2.06: 0.8783 @ 20 m /
0.9045 @ 50 m, 4of5/pt0.2) — the transfer table is complete, final deltas
HIGH-T0.7 −0.048 < HIGH-T0.3 −0.057 < image −0.078 < MIN −0.087: the
deployment champion *started higher and degraded more*; T0.7-HIGH remains
the best transferrer.

## 17. Board coverage and scope (documentation note)

The leaderboard stock-take (S111) found ~48 % of the 295 manifest
conditions on no statistically tiered board. This is by design, not
omission: the absentees are per-N decomposition grains whose aggregates
are ranked, errata-preserved material (e.g. the T=1.0 `consensus-384-t1-0`
run, E43), and the H8/H10/H12 greedy/WBF cells, which are preregistered
hypothesis tests reported in their preregistered form. Cross-era boards
are structurally impossible for paired tile-swap tests (disjoint tile
sets); cross-era comparison is descriptive, with within-era tiers doing
the statistics. Metric-led (MCC/P/R) rankings with degenerate-trade-off
flags live at `results/metric-leaderboards/` (GS @ 30 m; 55-map @ 50 m).

## See also

- **Preceding experiment(s)**: `results/era1-pv-stage-d/stage-d-findings.md` —
  the n=1 PV grid whose § 4 flagged this determinism check; same 384/256
  proposer lineages.
- **Preceding experiment(s)**: `results/era1-pv-stage-d/384-leg-recon.md` — the
  384 `flash-high-text` proposer/verifier provenance reused here.
- **Follow-up experiment(s)**: the pencilled `384-flash-high-image-1of5-union`
  image-proposer tranche (`planning/verifier-robustness-cells.json`
  `_deferred_cells`) — verify the ≥3-of-5 band, not the union (§ 3).
- **Follow-up experiment(s)**: Flash 3.5 bare-proposer tranche (~$46 flex,
  parked) — the only angle a stronger model might win, since the PV
  architecture disadvantages precise proposers (§ 9).
- **Run output directory**: `outputs/verifier-robustness/`.
- **Working-notes Observations**: Obs 354 — verifier T=0.0 determinism is
  negligible at F1 level (n=1 vindicated); Obs 355 — the 1-of-5 union is the
  worst verifier input (verifier does not rescue the FP flood); Obs 356 — a
  higher-T consensus verifier does not help (both cells stall at T=0.3);
  Obs 357 — the cost meta-rule (on a within-noise tie, take the cheaper
  config; the 6→35-pass ladder is one statistical tier).
- **Decisions / Errata**: E56 governs verifier prob_t diagnostics only; no
  preregistration amendment needed for a robustness check.

## Changelog

### 2026-06-11 (S113) — Flash 3.5 role permutations; second-wave manifest registration

**Refresh trigger**: Session 113 ran the three Flash 3.5 model-role
permutations § 11 of the review dossier left pending ($0, zbook),
registered the second wave in the manifest (runs `flash35-pv-2x2` and
`55maps-text-min-n10-uplift`; 6 pv-diag-384 additions; analyses
`min-vs-high-thinking-pv`, `pass-budget-pareto-v2`, `flash35-model-roles`,
`unswept-pools-completeness`, `55map-canonical-leaderboard-50m`), and
refreshed the 55-map canonical board with the uplift cell (8 cells,
24/28 pairs significant, 5 tiers — the uplift shares Tier 2 with T03-k4
rather than minting a sixth tier; § 16's board citation updated).
§ 14 sharpened:

| claim | before | after |
|---|---|---|
| F3.5 proposer-role loss (−0.0355) | "~5× noise scale", untested | resolved, p = 0.035 raw |
| F3.5 verifier-role losses | "−0.012..−0.015 at 3×" | within-noise ties (p = 0.17 / 0.10) → cost rule decides |

What did NOT change: the § 14 verdict (Flash 3.5 wins in no role) and
every other section stand; the all-Flash-3 stack remains production.

### 2026-06-11 (later) — unswept-pools sweep, T0.3 closure, cost recalibration

**Refresh trigger**: the systematic sweep of 18 never-swept PV pools
(`unswept_pools_sweep.json`), Run A (the T0.3 GS comparator, $2.06), and
the TM-cost-manifest recalibration of the Pareto cost model. § 9 refined
(the verifier model DOES matter on high-recall pools: Pro-vf 0.8792 over
the Flash HIGH union, +0.015 raw p = 0.019, post-hoc-selected; dominated
by min11 — frontier unchanged); § 15 dollar columns recalibrated (×~1.8,
efficient set unchanged); § 16 (c) the min11 uplift is running, (d) the
T0.3 gap is closed and the transfer table complete. Also recorded by the
sweep: the full 30-pass union's global optimum IS the registered 16of30
headline (0.8902 reproduced exactly — no hidden better operating point).

### 2026-06-11 — Second wave: min rungs, Flash 3.5, Pareto v2, the deployment reversal

**Refresh trigger**: Sessions 111–112's post-fold work — the
minimal-thinking PV rungs and recall-ceiling mechanism (§ 13, Obs 359),
the Flash 3.5 2×2×2 tranche (§ 14), the cost-weighted Pareto v2 with
55-map production costs (§ 15, superseding § 12's passes axis), the
GS-vs-deployment transfer table and the min/high reversal that
scope-qualifies the headline meta-rule (§ 16, Obs 362), and the board-
coverage note (§ 17).

| claim | before | after |
|---|---|---|
| diversity dividend | HIGH ≫ MIN (consensus era) | obsolete under PV **on GS** (§ 13) |
| binding constraint under PV | precision (implicit) | pool recall ceiling (§ 13) |
| stronger models | Pro worse PV partner | Flash 3.5 wins in NO role (§ 14) |
| Pareto axis | passes (§ 12) | estimated flex-$ + production costs (§ 15) |
| meta-rule scope | unqualified | qualified by instrument resolution (§ 16) |
| production text config | (GS tie → min) | deployment-evidenced: HIGH at k3 (§ 16) |

What did NOT change: §§ 1–11 stand; the carry-forward verifier remains
production; no new champion. Obs 358–362 staged this wave.

### 2026-06-10 — Stage 3 + model/cost deep-dive + operational maximum + Pareto board

**Refresh trigger**: Session 110 ran the thinking × temperature matrix
(~$20.86 flex) and the operational-maximum cell (~$2.54 flex) plus four $0
re-scores (high-thinking prior, nof10, Pro PV, matrix tiering); Session 111
ran the opmax-vs-headline permutation test and built the pass-budget Pareto
board (both $0). Added §§ 8–12, the meta-rule headline, a § 2 aggregation
refinement note, and closed the § 7 thinking-axis loose end.

| claim | before | after |
|---|---|---|
| thinking/temperature at N=5 | untested | one statistical tier (§ 8) |
| thinking at n=1 | open ($0 to close) | high HURTS a single pass (§ 8) |
| consensus vs single pass | "no benefit" (majority read) | permissive consensus +0.012 (§ 8) |
| verifier model | assumed Flash | Pro ≈ Flash as verifier; keep Flash (§ 9) |
| pass allocation | untested | proposer ≥ verifier at equal cost (§ 10) |
| ceiling | 0.890 (n=1 headline) | 0.8951 numerical high, NOT significant (p=0.363) — 0.890 stands (§ 11) |
| budget guidance | none | 6→35-pass ladder one tier; cheap end 0.864 at 6 passes (§ 12) |

What did NOT change: §§ 2–3 and § 7 results stand (with the § 2 majority-vote
reading refined); the carry-forward verifier remains the production
configuration; no new champion is minted. Data-integrity note: the opmax run
had overwritten `robustness_{grid,summary}_T0.3.json`; the Stage-2 snowball
content was restored and the opmax content re-homed to
`robustness_{grid,summary}_T0.3-16of30.json` (commit `7d85b00ef`), with an
`--out-suffix` guard added to the analyser.

### 2026-06-09 — Stage-2 (higher-T consensus verifier rejected)

**Refresh trigger**: the Stage-2 temperature snowball completed (commit
`af9214554`). Added § 7 and the headline. **Both cells stalled at T=0.3** — 384
0.8722 → 0.8739 (+0.0017, within noise), 256 0.8637 → 0.8582 (−0.0055) — so
T=0.7/1.0 never ran. The higher-T consensus verifier hypothesis is rejected; the
T=0.0 carry-forward stands.

| claim | before (Stage 1) | after (Stage 2) |
|---|---|---|
| higher-T consensus verifier | open hypothesis | rejected (both stall at T=0.3) |
| title / scope | "Stage 1, T=0.0" | spans Stage 1 + Stage 2 |

What did NOT change: the Stage-1 determinism (§ 2) and proposer-input (§ 3)
results. The thinking axis remains open (free on-disk HIGH-thinking prior to be
scored next session).

### 2026-06-09 — Stage-1 publication (T=0.0)

First publication. Records the Stage-1 T=0.0 run (31,470 calls, $21.93 flex,
0 failures): the determinism result (single-run F1 SD 0.0025–0.0072 → n=1
vindicated; consensus ≈ mean; verifier-vote threshold ~inert at T=0.0) and the
proposer-input optimisation (1-of-5 union worst at both cells; 384 peaks at
4of5 = 0.872, 256 plateaus 3–5of5 ≈ 0.86; the verifier does not rescue the
single-pass FP flood). Implication: image tranche should verify the ≥3-of-5
band, not the union. Results from `robustness_grid_T0.0.json`; landed with
commit `643999a7b` (results) and the analysis code at `7ef2679cb` (post-audit).
Higher-temperature stages (0.3/0.7/1.0) to follow as new Changelog entries.
