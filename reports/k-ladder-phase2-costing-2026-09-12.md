# K-ladder Phase 2: what the missing rungs would cost

> **Last revised**: 2026-09-12 (later — tiers A–D approved and **run**; § 5's
> tier-A rationale corrected, the K = 30 "fifth rung" withdrawn. Prior: original
> publication — step 6 of the K-ladder Phase-1 run,
> `planning/k-ladder-phase1-run-2026-09-12.md`). Controlling card:
> `planning/k-ladder-review-2026-09-11.md` (ruling R5: up to US$50 for loose
> ends, every run costed and approved by the PI first).
> See [§ Changelog](#changelog).

**APPROVED AND RUN.** The PI approved all four tiers on 2026-09-12 at
US$24.84; the run executed them. This document remains the costing — the plan
and the prices it was approved on — and is **not** updated with the outcome. The
audited spend, every rung's numbers, and what each ladder gained are in
`reports/k-ladder-phase2-deltas-2026-09-12.md`; the ladders themselves are in
`results/k-ladder-2026-09-12/findings.md`.

## 1. The headline

| Quantity | Value |
|---|---:|
| Rungs that still lack a verifier output | **28** |
| Candidates to verify, in total | **35,844** |
| Cost at the audited Gemini 3 verifier rate | **US$24.84** |
| Cells needing RE-verification because their union is newer than their probabilities | **0** |
| Total against the PI's US$50 ceiling | **US$24.84 — 50 % of it** |

The whole gap-fill fits inside the ceiling with room to spare, so the question
the PI faces is not "which rungs can we afford" but "which rungs are worth
having". § 5 recommends an order on that basis.

## 2. The rate, and where it comes from

Every one of the 28 rungs is a Gemini 3 family under ruling R1 (the carried
Gemini 3 verifier at every rung, no swapping), so one rate applies throughout.

| Rate | USD per candidate | Anchor |
|---|---:|---|
| Gemini 3 verifier (`gemini-3-flash-preview`, MINIMAL, T 0.0, flex) | **0.000693** | `reports/token-load-audit-2026-06-12.md` § 5, `VF_CALL_USD`, "opmax meta recompute; deployment runs measured 0.000684–0.000698" |
| — corroboration | 0.000699 | `reports/r7-gaps-deltas-2026-09-11.md` § 2.3: arm 1, `gemini-3-flash-preview`, 12,715 candidates for US$8.89 audited → 8.890222 / 12,715 |
| Gemini 3.7 verifier (`gemini-3.7-flash`, low, flex) | 0.001125 | same § 2.3 and § 2.5: arm 2, 12,715 candidates for US$14.3055 audited → 0.001125 per candidate |

The 3.7 rate is tabled for completeness and is **not** used below: swapping the
verifier is outside R1. At 0.001125 the same 35,844 candidates would cost
US$40.33, still inside the ceiling but answering a different question.

The two Gemini 3 figures differ by 0.9 %, which is the spread the audit itself
records across four measured deployment verifiers (0.000684–0.000698). The
table uses the adopted constant, 0.000693; at the arm-1 figure the total would
be US$25.06, so the choice moves nothing material.

**Rate basis, stated because the two are not interchangeable.** All figures are
flex tier (0.5 × list), thinking priced at the output rate, cached input
measured at zero in this family. That is the same basis as every other cost
column in the corpus (`docs/methodology/notation-key.md` § 8).

## 3. The 28 rungs

Union sizes are **measured, not extrapolated**. No first-N sub-pool union is
committed for any of these rungs, and
`results/k-ladder-2026-09-12/inventory.md` § 4 shows a shorter sub-pool union is
neither a positional prefix of a longer committed one nor a coordinate subset of
it, so its size cannot be read off an existing artefact. Each was built at US$0
with the canonical consensus chain — `merge_passes.load_pass_detections`
(`pass_filter` 1..N), `deduplicate_within_pass`, `cluster_across_passes` — and
counted at vote ≥ 1 without writing a consensus file
(`scripts/probe_first_n_union_sizes.py`; every figure below is a key of
`results/k-ladder-2026-09-12/first-n-union-sizes.json`).

| # | family | K | candidates | USD |
|---:|---|---:|---:|---:|
| 1 | Gemini 3 MINIMAL text 384 px, T 0.3 | 1 | 938 | 0.65 |
| 2 | Gemini 3 MINIMAL text 384 px, T 0.3 | 3 | 1,244 | 0.86 |
| 3 | Gemini 3 MINIMAL text 384 px, T 0.7 | 1 | 1,012 | 0.70 |
| 4 | Gemini 3 MINIMAL text 384 px, T 0.7 | 3 | 1,355 | 0.94 |
| 5 | Gemini 3 MINIMAL text 384 px, T 1.0 | 1 | 1,022 | 0.71 |
| 6 | Gemini 3 MINIMAL text 384 px, T 1.0 | 3 | 1,588 | 1.10 |
| 7 | Gemini 3 HIGH text 384 px, T 0.3 | 1 | 1,326 | 0.92 |
| 8 | Gemini 3 HIGH text 384 px, T 0.3 | 3 | 2,201 | 1.53 |
| 9 | Gemini 3 HIGH text 384 px, T 0.7 | 1 | 1,370 | 0.95 |
| 10 | Gemini 3 HIGH text 384 px, T 0.7 | 3 | 2,755 | 1.91 |
| 11 | Gemini 3 HIGH text 384 px, T 1.0 | 1 | 1,495 | 1.04 |
| 12 | Gemini 3 HIGH text 384 px, T 1.0 | 3 | 2,848 | 1.97 |
| 13 | Gemini 3 MINIMAL image 384 px, T 0.3 | 1 | 729 | 0.51 |
| 14 | Gemini 3 MINIMAL image 384 px, T 0.3 | 3 | 885 | 0.61 |
| 15 | Gemini 3 MINIMAL image 384 px, T 0.7 | 1 | 694 | 0.48 |
| 16 | Gemini 3 MINIMAL image 384 px, T 0.7 | 3 | 950 | 0.66 |
| 17 | Gemini 3 MINIMAL image 384 px, T 1.0 | 1 | 792 | 0.55 |
| 18 | Gemini 3 MINIMAL image 384 px, T 1.0 | 3 | 1,174 | 0.81 |
| 19 | Gemini 3 HIGH image 384 px, T 0.3 | 1 | 872 | 0.60 |
| 20 | Gemini 3 HIGH image 384 px, T 0.3 | 3 | 1,619 | 1.12 |
| 21 | Gemini 3 HIGH image 384 px, T 0.7 | 1 | 771 | 0.53 |
| 22 | Gemini 3 HIGH image 384 px, T 0.7 | 3 | 1,522 | 1.05 |
| 23 | Gemini 3 HIGH image 384 px, T 1.0 | 1 | 982 | 0.68 |
| 24 | Gemini 3 HIGH image 384 px, T 1.0 | 3 | 1,887 | 1.31 |
| 25 | Gemini 3 scale-4-optimal 487 | 1 | 830 | 0.58 |
| 26 | Gemini 3 scale-4-optimal 487 | 3 | 1,586 | 1.10 |
| 27 | Gemini 3.7 text, GS B geometry | 1 | 640 | 0.44 |
| 28 | Gemini 3.7 text, GS B geometry | 3 | 757 | 0.52 |
| | **total** | | **35,844** | **24.84** |

Rows 27 and 28 are the 3.7 PROPOSER screened at GS, verified by the carried
Gemini 3 verifier — which is what the family's committed K = 5 and K = 10 rungs
use (`gemini37-screen-2026-08-28::g37-text-k5-verified-carried-p0.10-k5`), so
R1 holds for them without a swap.

**The inventory counts 30 gaps and this table 28.** The Gemini 3.7 GS text
family appears twice in the inventory, once per evaluation recipe (grid-common
and the board frame `era2-b-487`), but both recipes read the same proposer pool
and so the same two unions: one verifier pass serves both. Two of the thirty
gaps are therefore the same API call as two others, and paying for them twice
would be an accounting error, not a cost.

**Two rungs are not in the table, and cannot be.** The 3.7 55-map arms' K = 10
rung is `no-passes`: those arms hold five proposer passes
(`outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37/run_1..run_5`), so the
rung cannot be built at any price. Extending them would be five new 3.7
proposer passes over 8,541 tiles — about US$144 on the audited basis
(`reports/r7-gaps-deltas-2026-09-11.md` § 2.2, US$144.27 for exactly that) —
which is three times the whole ceiling and a different proposal.

## 4. Re-verification: nothing is owed

Ruling R4 asks for any cell whose candidate union is newer than its
probabilities to be re-verified, costed under R5.
`scripts/check_pv_sweep_vintage.py survey`, re-run on sapphire this session,
classifies all 30 registry cells:

| verdict | n | re-verification owed |
|---|---:|---|
| `same-vintage` | 24 | none — union, probabilities and sweep all agree |
| `probabilities-grew` | 4 | **none.** The index join stays sound; only the sweep was stale, and all four were re-swept on 2026-09-08 (`results/recovery-reeval-2026-09-08/pv-diag-384/`). No API call re-verifies a sweep |
| `union-rebuilt` | 1 | **none, already paid.** `pv-high-text-t0.0-n3`; the rebuilt union was completely re-verified on 2026-09-08 for US$1.82 (stage `verified-v1-n3-recovery-2026-09-08`, `43516df9a`), and step 3 of this run registered that pair as `pv-diag-384::pv-high-text-t0.0-n3-recovery-2026-09-08-opmax` |
| `manifest-mode` | 1 | none — `pv-flash-high-text-16of30` is keyed by `candidate_id`, so there is no index join to go stale |

The four `probabilities-grew` cells are, for the record,
`pv-high-image-t0.3-n5` (union 2,190, probabilities 2,190, sweep 2,179),
`pv-high-image-t0.7-n5` (2,017 / 2,017 / 2,016), `pv-high-image-t1.0-n5`
(2,840 / 2,840 / 2,839) and `pv-scale4-optimal-n10` (3,601 / 3,601 / 3,600).

**So the entire R4 exposure is already discharged, and Phase 2's cost is
gap-filling alone.**

## 5. Recommended order

Ranked by what each purchase buys the review, not by price. Every tier is
independently approvable, and the running total stays inside the ceiling at
every step.

| tier | rungs | candidates | USD | running | what it buys |
|---:|---|---:|---:|---:|---|
| **A** | K = 1 and K = 3 of **Gemini 3 MINIMAL text T 0.7** and **HIGH text T 0.7** (rows 3, 4, 9, 10) | 6,492 | **4.50** | 4.50 | The two pools the registered `pass-budget-pareto-v2` efficient set is built on, at the temperature its rungs use. This is the one purchase that turns the Pareto analysis's two-point comparison into a **four-rung** ladder — K = 1, 3, 5, 10 — on the GS frame, for the two families the rest of the paper is built from (**corrected 2026-09-12**: this cell previously claimed a fifth rung at K = 30. It does not exist as a rung. See the note below the table) |
| **B** | K = 1 and K = 3 of the remaining **text** families (rows 1, 2, 5–8, 11, 12) | 12,662 | **8.77** | 13.27 | Temperature × K at four rungs across T 0.3 / 0.7 / 1.0 on both thinking levels. Turns the ladder into a factorial and lets the review say whether K's return depends on temperature — a question no committed cell can answer |
| **C** | K = 1 and K = 3 of the four **image** families (rows 13–24) | 12,877 | **8.92** | 22.19 | The same for the image track, where the committed K = 5 → 10 steps are the smallest in the corpus and tile-MCC moves opposite to F1. Lower priority because the image track is not the paper's headline architecture |
| **D** | K = 1 and K = 3 of **scale-4-optimal** and the **3.7 GS text screen** (rows 25–28) | 3,813 | **2.64** | **24.84** | Completeness. The 3.7 rungs would give a second model family a four-rung GS ladder, which is the only way to ask whether the saturation shape is a property of the pipeline or of Gemini 3 |

**No family reaches five rungs, and the two K = 30 cells are not the reason to
think otherwise** (corrected 2026-09-12, during the Phase 2 run). The K = 30
cells of these two pools are
`pv-diag-384::flash-minimal-text-n30-t07-text-t0.7-consensus-29of30` and
`pv-diag-384::flash-high-text-n5-text-t0.7-consensus-26of30`, and both carry
`aggregation: "consensus"` with `verifier_config: null` — consensus-only cells
at vote thresholds 29/30 and 26/30, with no verifier pass. Ruling R1 fixes the
carried verifier at **every** rung, so neither can be a rung of one of these
ladders. The corpus's one verified 30-pass cell,
`pv-diag-384::verified-adv-text-consensus-16of30`, is registered at
`n_passes: 1` with `vote_threshold: null` because its verifier ran over an
already-thresholded 16-of-30 consensus rather than over the vote ≥ 1 union, so
its candidate universe is a different object from a ladder rung's. Tier A
therefore buys a four-rung verified ladder, which is what it was worth buying;
the recommendation is unchanged.

Tier A alone — **US$4.50** — is the recommendation if only one approval is
wanted. It is 9 % of the ceiling and it is the tier whose absence the Phase-1
findings actually feel: the GS ladder that exists
(`stride-phaseb-2026-08-25` `g384_ov128`, K = 1/3/5/10) is a stride-geometry
cell, and tier A would give the same four rungs on the pools the rest of the
paper is built from.

Tiers A–D partition the 28 rungs exactly — 6,492 + 12,662 + 12,877 + 3,813 =
35,844 candidates, the § 3 total — so approving all four is the US$24.84 of § 1
and nothing is counted twice. Approving a prefix of the order costs the running
total in the last column.

**Practical notes for whoever runs it.** Each rung is one verifier pass over a
freshly built first-N consensus union, so each needs the consensus built first
(`scripts/merge_passes.py --sweep --passes 1,..,N`, US$0, on sapphire) and then
one `scripts/5_verify_crops.py` stage. The unions are 640–2,848 candidates, so
no rung is a long-running job. Daily Gemini quotas reset at midnight US Pacific
(7 pm AEDT), and the whole tier A is about 6,500 calls, well inside a day.

## Changelog

### 2026-09-12 (later) — Tiers A–D approved and RUN; § 5's tier-A rationale corrected

**Trigger**: the PI approved all four tiers on 2026-09-12 at US$24.84 and the
run executed them. Closing report, with the audited spend and every rung's
numbers: `reports/k-ladder-phase2-deltas-2026-09-12.md`. Findings:
`results/k-ladder-2026-09-12/findings.md`. Pre-launch audit:
`results/k-ladder-2026-09-12/phase2/pre_launch_audit.md`.

**What moved in this document**: one claim, in § 5's tier-A rationale.

| Claim | before | after |
|---|---|---|
| What tier A completes for MINIMAL text T 0.7 and HIGH text T 0.7 | "K = 1, 3, 5, 10, 30: five rungs, the longest fixed-parameter ladder the corpus could have" | a **four**-rung ladder at K = 1, 3, 5, 10 |
| Why | the two pools were read as holding a K = 30 rung | both K = 30 cells carry `aggregation: "consensus"` and `verifier_config: null`, so ruling R1 excludes them; the one verified 30-pass cell is registered at `n_passes: 1` over a 16-of-30 consensus, not over the union |

**What did NOT change**: every number in §§ 1–4 — the 28 rungs, their measured
union sizes, the 35,844 candidates, the US$24.84 total, the rates and their
anchors, and the nil re-verification exposure of § 4. Nor does the tier-A
recommendation change: four rungs at fixed parameters on the pools the paper is
built from was the reason to buy it.

### 2026-09-12 — Original publication (Session 154, K-ladder Phase 1 step 6)

Written from `results/k-ladder-2026-09-12/inventory.json` (which rungs are
missing and why), `results/k-ladder-2026-09-12/first-n-union-sizes.json` (the
measured union sizes, built on sapphire at US$0),
`reports/token-load-audit-2026-06-12.md` § 5 and
`reports/r7-gaps-deltas-2026-09-11.md` § 2.3 (the two verifier rates), and a
same-session re-run of `scripts/check_pv_sweep_vintage.py survey` on sapphire.
No API call was made to produce it, and none is authorised by it.
