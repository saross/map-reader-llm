# Verifier-robustness run — experiment intent

> **Last revised**: 2026-06-09 (pre-data publication — design, phase-gate, and
> cost recorded at launch of the Stage-1 T=0.0 verification). See
> [§ Changelog](#changelog) for revision history.

This file records the **intent** of the Session-109 verifier-robustness run
*before* its results are known, so the design rationale is anchored
independently of whatever the data shows. Results land in the companion
findings doc (`results/verifier-robustness/verifier-robustness-findings.md`,
authored once analysis completes).

## 1. The two questions

Both bear on **every n=1 verified cell in the paper** — the Stage-D PV grid, the
55-map deployment oracle, and all proposer-verifier cells.

1. **Verifier determinism.** Every verified cell to date is **n=1**, on the
   assumption that the production verifier (T=0.0) is deterministic. It is
   **not**: two independent T=0.0 runs of the *identical* config on the *same*
   crops disagree on **2.96 %** of candidates (115 / 3,890), with accepted count
   588 → 571 and only 54.5 % identical probabilities (mean |Δprob| 0.050) — the
   pre-existing pair `outputs/wbf/e47-propose-brief-n5/verified-v1` vs `-v2`
   (both `gemini-3-flash`, T=0.0, minimal, n=1). This run measures whether that
   candidate-level flicker propagates to **F1** at the aggregate (tile) level,
   by running the verifier at **N=5 iterations** and comparing the spread of the
   5 single runs against a 5-run **consensus** verifier.

2. **Proposer input.** What proposer pool should feed the verifier — the
   permissive 1-of-5 **union** (max recall, FP-heavy, the verifier prunes), or a
   pre-filtered strict consensus? We verify the union **once** and derive every
   proposer-vote input level (1of5 → 5of5) as a free post-hoc subset, because
   the union geojson carries `vote_count` per feature.

## 2. Design (Shawn-approved, Session 109)

Verify the **1-of-5 proposer union** of the two Gold-Standard consensus+PV
cells at **N=5 verifier iterations**, **T=0.0 only** (Stage 1). Later stages add
the verifier temperature **0.3 / 0.7 / 1.0** one notch at a time (the
hypothesis: a higher-T *consensus* verifier may mirror the proposer-side
diversity dividend, even though higher T was worse at n=1).

| field | value |
|---|---|
| verifier config | `prompts/configs/verify_adversarial-text.json` |
| model | `gemini-3-flash-preview` |
| thinking | minimal |
| temperature | 0.0 (Stage 1) |
| examples | none (text-only labels) |
| iterations (N) | 5 |
| execution | realtime, **flex** (50 %-off) |
| driver | `scripts/run_verifier_robustness.py --full --temperature 0.0` |
| analysis | `scripts/analyse_verifier_robustness.py` ($0, local) |
| host | zbook (`zbook-ubuntu`) |
| launcher commit | `16add03c6` |

This run **adds no new API surface** — it wraps the canonical `run_pv.py verify
--iterations N --temperature T --service-tier flex` path. The verify step is the
only API spend; extract and scoring are local ($0).

## 3. Cells and scope

| cell | proposer union | union cands | proposer-vote cumulative (1→5 of 5) |
|---|---|---:|---|
| 384-flash-high-text-1of5-union | `outputs/h11/pv-diag-384/consensus/flash-high-text-1of5.geojson` | 3,736 | 3736 / 1376 / 855 / 584 / 415 |
| 256-text-1of5-union | `outputs/h11/pv-diag-256/consensus/text-1of5.geojson` | 2,558 | 2558 / 1909 / 1645 / 1423 / 1165 |

The 384 cell is the **leading** GS consensus+PV proposer (flash-high-text, the
F1 0.890 lineage); 63 % of its 1of5 union is single-pass-only (vote_count = 1),
the FP-heavy permissive extreme. The 256 cell is the **rescue** cell (Obs 352);
smaller tiles benefit most from verifier efficacy.

## 4. Cost (gated, approved)

| quantity | value |
|---|---|
| union candidates (both cells) | 6,294 |
| iterations | 5 |
| **verifier calls** | **31,470** |
| **est. cost** | **$21.93 flex** / $43.87 standard |
| per-call (flex) | $0.000697 (calibrated to the Session-107 actuals: 7,113 → $4.96) |

Later temperature notches add ~$21.93 flex each (1of5 union, both cells), so the
full four-temperature sweep on the union would total ~$87.74 flex — which is why
Stage 1 runs T=0.0 only and the higher-T sweep is staged and targeted by these
results.

## 5. Gating

- **`/phase-gate`** run before launch (Session 109). Verdict: **validate first —
  this run *is* the validation** of the most load-bearing untested premise in
  the paper (n=1 determinism). The free e47 evidence (§ 1) shows the assumption
  is already violated at the candidate level; what is unmeasured is the F1-level
  impact on the headline cells.
- **API review gate** satisfied: model `gemini-3-flash`, realtime flex, 31,470
  calls, ~$21.93 — explicitly approved.
- **Pre-launch validation**: $0 dry-run (extraction 0-fail, cost confirmed) +
  ~$0.08 smoke (pipeline green; the 256 smoke already showed 1 / 12 candidates
  splitting across the 5 T=0.0 iterations at prob_t = 0.2) + a logic test of the
  analysis chain against the smoke data.

## See also

- **Preceding experiment(s)**: `results/era1-pv-stage-d/stage-d-findings.md` —
  the n=1 PV grid whose § 4 flagged this determinism check as future work; the
  384 / 256 cells here are the same proposer lineages.
- **Preceding experiment(s)**: `results/era1-pv-stage-d/384-leg-recon.md` — the
  384 flash-high-text proposer / verifier provenance reused here.
- **Follow-up experiment(s)**: `results/verifier-robustness/verifier-robustness-findings.md`
  — the results narrative (authored once analysis completes).
- **Run output directory**: `outputs/verifier-robustness/`.
- **Working-notes Observations**: None yet (Obs authored with results).
- **Decisions / Errata**: E56 governs verifier prob_t diagnostics only (dated
  scope-clarification, 2026-06-06); no preregistration amendment needed for a
  robustness check.

## Changelog

### 2026-06-09 — Original publication (pre-data)

Authored at launch of the Stage-1 T=0.0 verification (commit `16add03c6`),
before any results are known, to anchor the design rationale independently of
the outcome. Records the two questions (determinism; proposer-input
optimisation), the N=5 / 1-of-5-union design, the two cells and their
proposer-vote distributions, the gated cost ($21.93 flex / 31,470 calls), the
phase-gate verdict (validate first), and the free prior evidence of
candidate-level non-determinism (e47 v1/v2, 2.96 % flip). Results, Observations,
and manifest registration to follow in the findings doc.
