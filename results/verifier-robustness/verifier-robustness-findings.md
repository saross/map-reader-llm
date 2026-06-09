# Verifier-robustness — findings (Stage 1, T=0.0)

> **Last revised**: 2026-06-09 (Stage-1 publication — the T=0.0 determinism +
> proposer-input results). See [§ Changelog](#changelog) for revision history.

This document is the citable home for the **verifier-robustness** programme
(Session 109). It answers two questions that bear on **every n=1 verified cell
in the paper** — the Stage-D PV grid, the 55-map deployment oracle, and all
proposer-verifier cells. Pre-run design and gating are recorded separately in
[`outputs/verifier-robustness/experiment_intent.md`](../../outputs/verifier-robustness/experiment_intent.md).

**Stage 1 (this document)** runs the production verifier at **N=5 iterations,
T=0.0** over the **1-of-5 proposer union** of the two Gold-Standard
consensus+PV cells (the leading 384 `flash-high-text` and the 256 rescue cell),
deriving every proposer-vote input level (1of5→5of5) as a free post-hoc subset.
Later stages add the verifier temperature 0.3 / 0.7 / 1.0 one notch at a time.

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
- Pre-run intent: `outputs/verifier-robustness/experiment_intent.md`

## See also

- **Preceding experiment(s)**: `results/era1-pv-stage-d/stage-d-findings.md` —
  the n=1 PV grid whose § 4 flagged this determinism check; same 384/256
  proposer lineages.
- **Preceding experiment(s)**: `results/era1-pv-stage-d/384-leg-recon.md` — the
  384 `flash-high-text` proposer/verifier provenance reused here.
- **Follow-up experiment(s)**: verifier-robustness Stage 2+ (higher-T consensus
  verifier, T=0.3 → 0.7 → 1.0) — to be added to this document.
- **Follow-up experiment(s)**: the pencilled `384-flash-high-image-1of5-union`
  image-proposer tranche (`planning/verifier-robustness-cells.json`
  `_deferred_cells`).
- **Run output directory**: `outputs/verifier-robustness/`.
- **Working-notes Observations**: Obs 354 — verifier T=0.0 determinism is
  negligible at F1 level (n=1 vindicated); Obs 355 — the 1-of-5 union is the
  worst verifier input (verifier does not rescue the FP flood).
- **Decisions / Errata**: E56 governs verifier prob_t diagnostics only; no
  preregistration amendment needed for a robustness check.

## Changelog

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
