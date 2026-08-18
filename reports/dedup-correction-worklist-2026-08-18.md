# Deduplication correction worklist: full blast radius and a prioritised remediation plan

> **Last revised**: 2026-08-18 (original publication — the S136 blast-radius
> trace and correction worklist for the missing within-pass deduplication).
> See [§ Changelog](#changelog) for revision history.

**Date**: 2026-08-18 (Session 136)
**Author**: Claude Code (Opus 5), amd-tower; all measurement executed on sapphire
**API spend**: US$0.00 — every number below is recomputed from committed
artefacts or read at source
**Scope**: every downstream consumer of the 155 duplicate-exposed conditions in
`results/scoring-sensitivity-2026-08-18/exposure-survey.json`
**Companions**: `reports/scoring-sensitivity-review-2026-08-18.md` (the
measurement this builds on), `reports/dedup-gap-compliance-2026-08-18.md` (the
preregistration reading), errata
[E79](../docs/methodology/preregistration/protocol-errata.md) (tile assignment)
and E80 (this gap)

---

## TL;DR

1. **The blast radius is wider than the prior review's § 3 survey.** Seventeen
   of the 37 registered analyses touch at least one duplicate-exposed
   condition; **five have duplicate-exposed members inside their `tie_set`**;
   **eleven of fifteen hypotheses** have an exposed analysis somewhere in their
   evidence chain. Two hundred and seventy committed markdown documents name at
   least one exposed cell.
2. **Four conclusions — not merely numbers — are at risk, one more than the
   prior review found.** The new one is the **`era1-leaderboard` Tier-1
   leader**: `retest-phase2b::verified-adv-text-t0.0` is exposed at 20.5 % pair
   involvement and rises from rank 7 (F1@20 0.7703) to **0.8128**, above the
   sole Tier-1 cell's committed 0.7925. The paper prose that this breaks is
   `docs/paper/results-draft.md:221-227`.
3. **The largest wholly unquantified risk is MCC, and it sits on the paper's
   Discussion.** The **top three tile-MCC rows** of
   `results/metric-leaderboards/gs-era2-pv-family-30m.json` are all
   duplicate-exposed (0.8887, 0.8848, 0.8766, at 20–22 % pair involvement), as
   is the era-1 MCC board leader and the 55-map MCC sole-Tier-1 cell. Discussion
   Seed 4 ("the tile-MCC counter-board replicates across all three
   instruments") therefore rests on exposed cells at **all three** instruments,
   and no MCC movement has been measured anywhere.
4. **The pre- versus post-verification approximation is small and now
   measured.** Re-deriving the accept decision on the deduplicated proposer feed
   for nine proposer-verifier cells moves F1 by **at most 0.0041** against the
   post-hoc route, against a deduplication correction of +0.042 to +0.058. **A
   correct pre-verification correction does not require API spend**; if the
   principal investigator wants the exact pipeline anyway it costs
   **≈ US$0.50** on the flex-discounted basis.
5. **Two corrections to the prior review's own numbers.** The claim that the
   probe "reproduces the committed `evaluation.json` F1 to four decimal places
   in every one of the 48 cells" fails for
   `pv-diag-384::baseline-pro-text-medium-t-0-0` (probe 0.7764 versus committed
   0.7921 at 20 m) — because the register read **1 of 3** committed runs for
   that condition and for `pv-diag-384::baseline-pro-image-medium-t-0-0`. Both
   are `diversity-dividend-384` cells and one is a **Tier-1 member**.
6. **Cost tiers.** Tier A (point-estimate re-scoring) ≈ 45 min sapphire, $0.
   Tier B (confidence intervals plus permutation re-tiering of six boards)
   ≈ 4–8 h sapphire, $0. Tier C (exact pre-verification re-verification)
   ≈ US$0.50–10 and is **optional**, not required.

---

## 1. What I re-verified at source before using it

Anti-confabulation pass. Every load-bearing premise below was re-read rather
than inherited from the prior review.

| Premise | Verified at | Verdict |
|---|---|---|
| Scorer has no deduplication step | `scripts/evaluate_detections.py` — the only `dedup` mention is `:1437`, a *tile-assignment* de-duplication of sjoin rows, not a feature merge | Confirmed |
| Candidate extraction has no clustering | `scripts/extract_candidates.py` — zero `dedup`/`cluster` matches; the per-feature loop is `for idx, feature in enumerate(features):` at `:315` | Confirmed |
| The preregistered step lives elsewhere | `scripts/merge_passes.py:137` `deduplicate_within_pass`; `DISTANCE_THRESHOLD_METRES = 20.0` at `:71` | Confirmed |
| 155 of 333 exposed; 123 tie-break; 6 both | `results/scoring-sensitivity-2026-08-18/exposure-survey.json` `summary` | Confirmed |
| 48 cells measured; 108 exposed conditions unmeasured | 48 distinct names across the five probe batches; 47 of them dedup-exposed (the 48th is `h13::arm-a-overlap-12-5`); 155 − 47 = 108 | Confirmed |
| Probe reproduces committed F1 | 91 of 93 cell-buffer pairs match the register to ≤ 0.0002 | **Two fail** — see § 1.1 |
| Cost basis is flex-discounted | `results/verifier-robustness/pareto/pareto_v2.json` `cost_model.basis` — "measured … at F3 flex rates"; `vf_call_usd = 0.000693` | Confirmed |
| `evaluate_detections.py` has a `--deduplicate` flag | grep: no match | **Not yet implemented** |

### 1.1 Two conditions were measured on one of three committed runs

`pv-diag-384::baseline-pro-text-medium-t-0-0` and
`pv-diag-384::baseline-pro-image-medium-t-0-0` each have a committed
`evaluation.json` whose `summary.n_runs` is **3**, but the exposure register
read **1** artefact for each. The cause is the recorded directory glob:
`results/paper-eval/n1/384px-14buf-mcc/pro-text-medium-t-0-0/evaluation.json`
records `cli_args.glob = "*/detections_*.geojson"`, which matches
`run_1/detections_text-t0.0_run01.geojson` but not
`run_2|run_3/detections-detect_brief-text-3.1-pro-2026-06-03.geojson`.
Per-run F1@20 is 0.7764 / 0.8031 / 0.7969, mean **0.7921** — the committed
value; the probe scored only the 0.7764 run.

Consequences, all actionable at $0:

- the two conditions' `duplicate_fraction` (0.2130 and 0.2249) is a
  single-run figure;
- the deduplicated estimate quoted for a **Tier-1 member of both
  `diversity-dividend-384` and `n1-baseline-matrix-384`** (0.8211 at 20 m) is a
  single-run figure and is not comparable with the board's three-run mean;
- a directory-listing cross-check over all 333 conditions found **only these
  two** under-read, so the register is otherwise sound.

- [ ] **W0.1** Re-run `scoring_sensitivity_probe.py` over all three runs of both
  conditions; correct the register entries and the two review tables.

### 1.2 Two phrasing inconsistencies in the prior review

Recorded here so the sibling owner can fix them in their own document; **I have
not edited `reports/scoring-sensitivity-review-2026-08-18.md`.**

- § 3.1 closes "Three of the four boards in `results/metric-leaderboards/` …
  carry no exposed rows at all." All four contain the IM-k3 row
  (`55maps-image-generalisation::verified-k3-*`), which the register marks
  `dedup_exposed: true` at 0.0105, above its own 0.01 threshold. The same
  section's table does acknowledge the 1.05 % load, so this is internal
  phrasing, not a measurement error.
- § 3.1 lists the "Entire § R5 verifier-robustness matrix" as safe, while
  § 3.3(b) states that twelve rows of that board are exposed at 20–25 %. The
  registered analysis behind § R5's completeness claim,
  `unswept-pools-completeness`, has **12 of its 18 conditions exposed**.

---

## 2. Task 1 — every downstream consumer

### 2.1 Registered analyses (`results/analyses-manifest.json`)

Thirty-seven analyses; **17 touch ≥ 1 exposed condition**; **5 have exposed
`tie_set` members**. `maxdup` is the largest pair-involvement fraction among the
analysis's exposed conditions (pair involvement is roughly twice the removal
fraction: a 25 % pair involvement corresponds to ~12.7 % of features removed).

| Analysis | Type | Cells | Exposed | tie_set exposed | maxdup | Output | Paper |
|---|---|--:|--:|--:|--:|---|---|
| `era1-single-pass-baseline-matrix` | leaderboard | 36 | **36** | **20 / 20** | 0.159 | `results/paper-eval/n1/512px-14buf-mcc` | Results |
| `era1-leaderboard` | leaderboard | 82 | 38 | 0 / 1 | 0.205 | `results/era1-leaderboard` | Results |
| `diversity-dividend-384` | leaderboard | 22 | 18 | **2 / 3** | 0.229 | `results/diversity-dividend-384` | Results |
| `n1-baseline-matrix-384` | leaderboard | 18 | **18** | **2 / 2** | 0.229 | `results/paper-eval/n1/384px-14buf-mcc` | Results |
| `tile-size-sweep` | sweep | 35 | 13 | 0 | 0.225 | `results/tile-size-sweep` | Results |
| `unswept-pools-completeness` | sweep | 18 | 12 | 0 | 0.250 | `results/verifier-robustness` | Results |
| `family-bh-fdr-confirmatory` | comparison | 12 | 8 | 0 | 0.159 | `results/family-fdr/family_fdr.json` | Results |
| `h6-a06-decision-rule` | comparison | 8 | **8** | 0 | 0.229 | `results/h6-registered-analyses` | Methods |
| `h1-cmt0106-pooled-modality` | comparison | 5 | **5** | 0 | 0.120 | `results/family-fdr/h1_cmt0106_pooled_modality.json` | Results |
| `h6-a09-cost-gate` | diagnostic | 4 | **4** | 0 | 0.229 | `results/h6-registered-analyses` | Methods |
| `55map-canonical-leaderboard-mcc-50m` | leaderboard | 8 | 1 | **1 / 1** | 0.010 | `results/metric-leaderboards` | Results |
| `55map-standardised-leaderboard-mcc-50m` | leaderboard | 8 | 1 | **1 / 1** | 0.010 | `results/metric-leaderboards` | Results |
| `55map-canonical-leaderboard-50m` | leaderboard | 8 | 1 | 0 / 2 | 0.010 | `results/55map-leaderboard` | Results |
| `55map-standardised-leaderboard-50m` | leaderboard | 8 | 1 | 0 / 2 | 0.010 | `results/55map-leaderboard` | Results |
| `e45-bootstrap-pairings` | comparison | 3 | 1 | 0 | 0.110 | `results/e45-bootstrap-pairings` | Methods |
| `h13-overlap-2026-08-18` | comparison | 3 | 1 | 0 | 0.032 | `results/h13-overlap-2026-08-18` | Results |
| `obs280-shared-reference` | comparison | 8 | 1 | 0 | 0.010 | `results/55maps-standardised-ref-2026-08-14/obs280-remeasurement.md` | — |

Twenty analyses are clean, including every consensus-calibration sweep, the
Pareto analyses, `verifier-robustness-matrix`, `min-vs-high-thinking-pv`,
`flash35-model-roles`, `h10-pool-size` and `h12-v2-hp-hn-ratio`.

Two `h6-*` analyses (Obs 415) and `family-bh-fdr-confirmatory` are **new to this
trace** — the prior review did not name them.

- [ ] **W1.1** Re-score and re-author the `outcome` text of all 17 exposed
  analyses; re-run the tiering for the 5 with exposed `tie_set` members.

### 2.2 Leaderboards and tiering artefacts

One hundred and fifty-two committed tiering / leaderboard JSON artefacts exist
outside caches. Of these:

| Artefact | Cells | Exposed | Tier 1 | Tier 1 exposed | Status |
|---|--:|--:|--:|--:|---|
| `results/paper-eval/n1/512px-14buf-mcc/tiering/tiering_20m.json` | 36 | **36** | 20 | **20** | Every Tier-1 member exposed |
| `results/paper-eval/n1/384px-14buf-mcc/tiering/tiering_20m.json` | 18 | **18** | 2 | **2** | Both Tier-1 members exposed |
| `results/diversity-dividend-384/tiering-champions/tiering_20m.json` | 22 | 18 | 3 | **2** | Ordering reverses (§ 2.6) |
| `results/diversity-dividend-384/tiering-with-deployable/tiering_20m.json` | 22 | 18 | 3 | **2** | Same |
| `results/era1-leaderboard/tiering_20m.json` | 82 | 38 | 1 | 0 | **Leader flips** (§ 2.6) |
| `results/metric-leaderboards/gs-era2-pv-family-30m.json` | 39 | 12 | n/a | n/a | F1 ranks 25–38; **MCC ranks 1, 2, 3, 6, 7, 8, 9, 10, 12** |
| `results/metric-leaderboards/55map-mcc-tiering.json` | 8 | 1 | 1 | **1** | IM-k3 is the sole Tier-1 cell |
| `results/metric-leaderboards/55map-mcc-tiering-standardised.json` | 8 | 1 | 1 | **1** | Same |
| `results/metric-leaderboards/55map-canonical-50m.json` | 8 | 1 | n/a | n/a | IM-k3 row only |

Beyond these, **118 legacy board files under `results/leaderboard/`** (90 under
`per-architecture/`, 28 under `combined/`) name exposed cells under their
Session-79 labels (`h4-canonical-last`, `h8-track2-text-scale-4`,
`h11-pvd-pro-medium-text-baseline`, …). They are not cited by any paper draft
(`grep -n "results/leaderboard" docs/paper/*.md` returns nothing) but they are
committed artefacts and carry `tier_stability` claims.

Their 4,669 `.cache/pairwise_*` files are **untracked** (`git ls-files
'results/**/.cache/**'` returns 0), so they are an invalidation concern only —
delete-and-regenerate, nothing to archive.

- [ ] **W1.2** Rebuild the 9 first-class boards above.
- [ ] **W1.3** Decide whether the 118 `results/leaderboard/**` files are
  refreshed or explicitly marked superseded (they predate the analyses
  manifest).
- [ ] **W1.4** Invalidate `results/leaderboard/**/.cache/` after any re-score.

### 2.3 Hypothesis dispositions (`results/hypothesis-outcome-table/`)

Eleven of fifteen hypotheses have an exposed analysis in their chain.

| H | Disposition | Exposed analyses in its chain | Conclusion at risk? |
|---|---|---|---|
| H1 | not rejected | `family-bh-fdr-confirmatory`, `h1-cmt0106-pooled-modality`, + all three post-hoc boards | No — Δ moves +0.0238 → +0.0300 against a half-width ≈ 0.034 |
| H2 | rejected (q=0.05) | `e45-bootstrap-pairings`, `family-bh-fdr`, `era1-leaderboard`, `unswept-pools-completeness` | No — adjusted p = 0.00035 |
| H3 | rejected (q=0.05) | `diversity-dividend-384`, `e45-bootstrap-pairings`, `family-bh-fdr`, `era1-leaderboard` | Test no; **the diversity-dividend framing yes** |
| H4 | not rejected | `family-bh-fdr`, `era1-leaderboard`, `era1-single-pass-baseline-matrix` | No — adjusted p = 0.217 |
| H5 | not rejected | as H4 | No — adjusted p = 0.834; but the F1-leg direction reverses |
| H6 | not executed | `h6-a06-decision-rule` (8/8 exposed), `h6-a09-cost-gate` (4/4 exposed) | Obs 415's rider needs re-checking |
| H7 | rejected (q=0.05) | `family-bh-fdr`, three post-hoc boards | No — adjusted p = 0.00233; T0.3/T0.0 ordering flips |
| H8 | not rejected | `family-bh-fdr`, two post-hoc boards | No — Simes p = 0.8344 |
| H9 | executed | `era1-leaderboard` | No |
| H11 | executed | `tile-size-sweep`, `unswept-pools-completeness` | No — monotonicity holds |
| H13 | partially executed | `h13-overlap-2026-08-18` (arm C residual 3.2 %) | No |

`results/family-fdr/family_fdr.json` ranks seven p-values; only H1's is computed
from an exposed comparison, and the rejection set {H2, H3, H7} has an enormous
margin (largest rejected adjusted p = 0.00233; smallest non-rejected = 0.217).
**No family-FDR disposition is expected to change.**

- [ ] **W1.5** Recompute H1's bootstrap on deduplicated inputs and re-emit
  `family_fdr.json`; confirm the disposition set is unchanged.
- [ ] **W1.6** Re-check the Obs 415 rider (optimal vote threshold reverses
  between models at matched N) on deduplicated Pro baselines.

### 2.4 Paper drafts (`docs/paper/**`)

| Location | Quoted quantity | Exposure | Number or conclusion? |
|---|---|---|---|
| `results-draft.md:124-127` | "Tier 1 is a 20-cell statistical tie spanning F1 0.583–0.631, led numerically by `canonical-last`, F1 0.631, MCC 0.213 … 227/630 pairs significant" | All 36 cells, all 20 tie members | **Number certain, tie membership uncertain**; `canonical-last` 0.6314 → 0.6593 |
| `results-draft.md:133-136` | "text cells reach F1 ≈ 0.60 at near-zero MCC while image cells trade F1 for far better tile discrimination" | Exposed cells, MCC unmeasured | **Conclusion — unquantified** |
| `results-draft.md:140-144` | H1 Δ +0.0238, CI −0.0104 to +0.0585, p = 0.1774, adj 0.248; H4 0.217; H5 0.834; H8 0.834 | Exposed arms throughout | Numbers |
| `results-draft.md:148-152` | "on the single-pass Pro 384 px board the two Tier-1 cells run at T = 0.0 and the two Tier-2 cells at T = 0.7 (`n1-baseline-matrix-384`)" | Both Tier-1 cells exposed at 21–23 % | Number; ordering holds, margin narrows 38 % |
| `results-draft.md:156-157` | "Single-pass performance, at best ~0.63 F1, is the floor every architectural intervention below is measured against" | `canonical-last`, 15.9 % | **Load-bearing floor**; becomes ~0.66 |
| `results-draft.md:170-174` | "lifts the text pipeline from the single-pass tie (~0.63) to 0.69–0.77" | Same floor | The measured lift shrinks by ~0.03 |
| `results-draft.md:174-178` | "the 'diversity dividend' … replication +0.067 F1, +0.234 MCC" | `diversity-dividend-384` Tier 1 | **Conclusion reverses** (§ 2.6) |
| `results-draft.md:221-227` | "the sole Tier-1 leader … (F1 0.792, MCC 0.676), statistically clear of everything below … a MINIMAL single-pass plus verifier … reaches the same tier as the 30-call HIGH-thinking consensus (0.770)" | `verified-adv-text-t0.0`, 20.5 % | **Conclusion changes** (§ 2.6) |
| `results-draft.md:231-238` | "256 px 0.342 < 384 px 0.520 < 512 px 0.606"; "0.460 bare and 0.856 verified (+0.396)" | All three legs exposed | Numbers; ordering holds (0.3586 / 0.5465 / 0.6371) |
| `results-draft.md:241-242` | Headline F1@20 0.890 / MCC 0.790 | Unexposed | Safe |
| `results-draft.md:247` | "A completeness sweep of all 18 never-swept proposer pools … confirmed this is the global optimum (`unswept-pools-completeness`, Obs 363)" | 12 of 18 exposed at 20–25 % | **The margin over the runner-up shrinks; re-check the "global optimum" claim** |
| `results-draft.md:398-437` | 55-map board, IM-k3 tile-MCC 0.712, sole Tier 1, ΔMCC +0.023, BH p = 0.0014 | IM-k3 exposed at 1.05 %; MCC movement unmeasured | **Conclusion — unquantified** |
| `results-draft.md:404` | Deployment headline corrected-F1@50 0.8169 | Unexposed | Safe |
| `discussion-seeds.md:90-113` | Seed 4: `verified-adv-image-baseline-pro-vf` tile-MCC 0.889; `era1-leaderboard` `verified-adv-image-t0.0` MCC 0.889; IM-k3 0.710 | **All three instruments exposed** | **Conclusion — unquantified** |
| `results-outline.md:199, 224, 237, 241, 243, 329` | The same six claims, marked "Load-bearing" | As above | Mirror of the above |
| `methods-draft.md:289` | `results/e45-bootstrap-pairings/e45_bootstrap_pairings.json` | 1 of 3 cells exposed | Number |

- [ ] **W1.7** Restate each row above once the re-scored boards land; attach the
  E80 disclosure wherever an exposed cell is compared against an unexposed one.

### 2.5 Working notes (`docs/notes/working-notes.md`)

Twenty-five distinct exposed cells are named. Observations resting on them,
established by mapping each hit to its enclosing `## Observation N` header:

| Obs | Subject | Risk |
|---|---|---|
| **346** | "The diversity dividend tested and signed off — HIGH-thinking consensus reaches the Pro single-pass tier on F1" | **Reverses** |
| **369** | "The tile-MCC counter-board replicates across all three instruments" | **Unquantified — MCC never measured** |
| **370** | "IM-k3 is the SOLE Tier-1 cell on the MCC axis" | **Unquantified** |
| 351 | Tile-size × architecture interaction across three sizes | Numbers; ordering holds |
| 352 | "The verifier rescues 256 px … PV is the single best Era-1 architecture" | Number 0.460 → 0.856; the Era-1 leader claim is at risk |
| 363 | The completeness sweep (`unswept-pools-completeness`) | Margin shrinks |
| 415 | Temperature, not thinking, drives the genuine-Pro corner gap | Numbers; rider needs re-check |
| 358, 362, 364 | 55-map canonical board findings | 1.05 % exposure; F1 movement +0.0004 |
| 280, 292 | F1/MCC tier-leader divergence; corrected-55-map reproduction | 1.05 %; MCC unmeasured |
| 207, 232, 279, 323, 324, 325, 344, 349 | Historical lever/leaderboard/replication notes | Numbers only |

- [ ] **W1.8** Write a single new Obs recording the correction (do **not** edit
  the existing entries — house rule is new-Obs-cross-references-old).

### 2.6 The four conclusions at risk

**(a) `era1-leaderboard` Tier-1 leader — NEW, not in the prior review.**
`results/era1-leaderboard/tiering_20m.json` ranks
`retest-phase3a-high::verified-adv-text-high-t1.0-n30-23of30` first at
`eval_f1` **0.7925**, sole Tier 1. Rank 7 is
`retest-phase2b::verified-adv-text-t0.0` at **0.7703**, dedup-exposed at 0.2046
pair involvement; probe batch 3 measures it at **0.8128** deduplicated
(`mean_over_passes["20"].deduplicated.f1 = 0.812826`). On deduplicated numbers
the rank-7 cell **leads the board**. The prose at
`docs/paper/results-draft.md:221-227` — "the sole Tier-1 leader … statistically
clear of everything below … the verifier's lift (0.775 → 0.792) is what breaks
the old six-way consensus tie" and "a MINIMAL single-pass plus verifier … reaches
the same tier as the 30-call HIGH-thinking consensus (0.770)" — does not survive
the point estimates. Note the direction: this *strengthens* the paper's
proposer-verifier thesis (two calls per tile now beat 31), but it changes which
cell is the leader and it dissolves the "reaches the same tier" framing.

**(b) `diversity-dividend-384` Tier-1 tie.** As the prior review found, with the
§ 1.1 correction attached: the consensus champion (0.8141, unexposed to
deduplication but tie-break-exposed) falls behind
`n1-pro-rerun-384::baseline-pro-text-high-t-0-0` (0.80454 → **0.854476**). The
third member, `pv-diag-384::baseline-pro-text-medium-t-0-0`, has a board value of
0.7921 that the probe did **not** reproduce (§ 1.1), so its deduplicated position
is not yet known.

**(c) § R5 zero-diversity anchor and 12 rows of `gs-era2-pv-family-30m`.**
`verified-adv-text-baseline` F1@30 0.832036 → **0.890476**, moving it from 29th
to level with `min6-true` (0.8902) at 13th. The associated
`unswept-pools-completeness` "global optimum" claim rests on the same twelve
rows.

**(d) The tile-MCC counter-board.** Ranked by MCC, `gs-era2-pv-family-30m`'s
top three rows are `verified-adv-image-baseline-pro-vf` (0.8887),
`verified-adv-image-baseline-medium-vf` (0.8848) and
`verified-adv-image-baseline` (0.8766) — all exposed at 20–22 % pair
involvement — and 9 of the top 12 are exposed. The era-1 leg
(`verified-adv-image-t0.0`, MCC 0.889) is exposed at 17.5 %; the deployment leg
(IM-k3, MCC 0.7104 canonical / 0.7120 standardised, sole Tier 1) at 1.05 %.
Tile-level MCC is **not** invariant to deduplication: merging two copies emitted
from two overlapping tiles into one centroid can empty the other tile, flipping
its predicted class. The direction is plausibly favourable (a false-positive
tile becomes a true negative), which would *widen* the image cells' MCC lead —
but it is unmeasured, and the argument the Discussion builds on it is
"image + verifier is the best tile-prioritisation instrument in the study".

### 2.7 Anchor documents in Document Revision Policy scope

Two hundred and seventy committed markdown files name at least one exposed cell
by an unambiguous identifier (220 under `results/`, 22 under `reports/`, 28
under `docs/`). By directory:

| Files | Directory | Note |
|--:|---|---|
| 90 | `results/leaderboard/per-architecture/` | Legacy Session-79 boards |
| 28 | `results/leaderboard/combined/` | Legacy |
| 32 | `results/rescore-2026-05-31/proposer-verifier-{384,512}/` | Per-cell re-score records |
| 12 | `results/verifier-robustness/evals/` | Per-cell evaluations |
| 1 | `results/conditions-manifest.md` | 220 exposed cells — the master register |
| 1 | `results/working-precision/gs-plateau-characterisation.md` | 106 exposed cells |
| 1 | `results/passes-manifest.md` | 49 exposed cells |
| 1 | `results/metric-leaderboards/*.md` | 13 exposed cells |
| 1 each | `results/{era1-leaderboard,diversity-dividend-384/*,paper-eval/n1/*,tile-size-sweep,family-fdr,era1-pv-stage-d,retest,analyses-manifest,h11-tile-size-results,…}` | Board and finding docs |
| 25 | `reports/d17-inventory/**`, `reports/verification/**` | Audit trail; historical, annotate rather than restate |
| 19 | `docs/methodology/n1-baseline-matrix.md` | Methodology anchor |

- [ ] **W1.9** Attach the Document Revision Policy pattern (banner + changelog)
  to each in-scope document **on touch**; do not bulk back-fill.

### 2.8 Cost models and candidate-count estimates

Duplicates inflate the proposer feed, so any figure derived from a candidate
count is affected. Measured feed inflation on the four `pv-diag-384` baseline
pools:

| Proposer pool | Feed | After deduplication | Crops never extracted | Inflation |
|---|--:|--:|--:|--:|
| `text-baseline` | 1,047 | 974 | 73 | 7.0 % |
| `image-baseline` | 746 | 682 | 64 | 8.6 % |
| `pro-medium-text-baseline` | 430 | 385 | 45 | 10.5 % |
| `pro-medium-image-baseline` | 587 | 520 | 67 | 11.4 % |

`results/verifier-robustness/pareto/pareto_v2.json` prices every rung as
`passes × pass_usd + crops × 0.000693`. Its rungs are all **multi-pass**
(30×HIGH, 10×MIN, 5×MIN …), whose crop counts come through `merge_passes` and
are therefore already deduplicated — the Pareto model is **not** exposed. What
*is* exposed is any single-raw-pass verifier workload quoted elsewhere:
the § R5 "≈ $54 flex as-run" programme total (`results-draft.md:253`) includes
single-pass-pool cells whose crop counts are 7–11 % inflated, and the
`h6-a09-cost-gate` diagnostic runs entirely on exposed Pro baselines.

- [ ] **W1.10** Re-derive `h6-a09-cost-gate` on deduplicated candidate counts.
- [ ] **W1.11** Add a one-line note to § R5 that single-raw-pass verifier
  workloads were 7–11 % larger than a deduplicated feed would have required —
  which makes every reported PV cost a **conservative upper bound**, not an
  understatement.

### 2.9 The second axis — order-dependent tile assignment (E79)

Disjoint from the deduplication exposure except for 6 conditions: **123
conditions, all `consensus`**. Magnitude −0.0028 to −0.0138 F1 across 14
measured cells, always in the same direction (the committed rule is the
optimistic one). It touches `diversity-dividend-384`'s Tier-1 consensus
champion, so the two axes **compound** on the one board where a conclusion
reverses: 0.8141 → 0.8047 under nearest-centroid, against 0.8545 for the
deduplicated Pro baseline — a 0.050 gap.

- [ ] **W1.12** Keep the two corrections in **separate commits and separate
  re-score runs** so their deltas remain attributable (the prior review's
  recommendation, endorsed here).

---

## 3. Task 2 — pre- versus post-verification deduplication, measured

### 3.1 The question

The committed proposer-verifier pipeline is: raw pass → one crop per feature
(`extract_candidates.py`, no clustering) → verify each crop → accept at
`prob ≥ threshold` → score. The preregistered § 8.5 Step 1 pipeline would
deduplicate **first**, so the verifier would see fewer crops, and the survivors
of a multi-member cluster would be centred on a **cluster mean centroid** — a
different image. The prior review deduplicated the *accepted* set post hoc,
which cannot capture a changed accept decision.

### 3.2 Method (zero API spend)

For each cell I clustered the proposer feed with the same greedy algorithm as
`merge_passes.deduplicate_within_pass`, retaining member indices; then
re-derived each cluster's accept decision from the **committed per-candidate
probabilities** in `outputs/h11/pv-diag-384/verified/*/probabilities.json` under
four merge rules — `max`, `mean`, `seed` (first member) and `min` of the members'
probabilities — which bracket what the verifier could plausibly say about a
merged crop. I also computed a pathological hard bound in which **every**
multi-member cluster flips its verdict. Threshold reproduction was asserted
first: the recomputed accept count matches the committed accepted GeoJSON
feature count exactly in all nine resolved cells.

### 3.3 How many candidates change

| Pool | Deduplicated feed | Crops never extracted | Crops whose centre **moves** | Median move | Max move |
|---|--:|--:|--:|--:|--:|
| `text-baseline` | 974 | 73 (7.0 %) | 71 (7.3 %) | 2.6 m | 9.9 m |
| `image-baseline` | 682 | 64 (8.6 %) | 60 (8.8 %) | 4.9 m | 9.6 m |
| `pro-medium-text-baseline` | 385 | 45 (10.5 %) | 45 (11.7 %) | 3.0 m | 8.7 m |
| `pro-medium-image-baseline` | 520 | 67 (11.4 %) | 64 (12.3 %) | 4.9 m | 9.8 m |

A 150 × 150 px crop at 75 px padding is ~750 m across at 5.02 m/px, so a
median 3–5 m centroid move shifts the crop by well under 1 % of its width: the
verifier sees a near-identical image. Every **singleton** cluster's crop is
byte-identical to the committed one, so only the moved crops could differ at all.

### 3.4 The measured bound

Nine of the twelve `*-baseline*` rows resolved (three
`pro-medium-image-baseline` cells could not: the probabilities file holds 519
results while the raw pass on disk holds 587 features — see § 5.3).

| Cell | Buffer | Committed | Post-hoc | Pre-dedup `max`/`mean` | `seed` | `min` | Max divergence from post-hoc |
|---|--:|--:|--:|--:|--:|--:|--:|
| `verified-adv-text-baseline` | 20 | 0.8142 | 0.8714 | 0.8714 | 0.8714 | 0.8714 | **0.0000** |
| `verified-adv-text-baseline` | 30 | 0.8320 | 0.8905 | 0.8905 | 0.8905 | 0.8905 | **0.0000** |
| `verified-adv-text-baseline-medium-vf` | 20 | 0.8244 | 0.8823 | 0.8823 | 0.8823 | 0.8823 | 0.0000 |
| `verified-adv-text-baseline-pro-vf` | 20 | 0.8263 | 0.8833 | 0.8833 | 0.8844 | 0.8831 | +0.0011 |
| `verified-adv-text-baseline-pro-vf` | 30 | 0.8419 | 0.9000 | 0.9000 | 0.9011 | 0.8998 | +0.0011 |
| `verified-adv-image-baseline` | 20 | 0.7167 | 0.7590 | 0.7599 | 0.7585 | 0.7585 | +0.0009 |
| `verified-adv-image-baseline` | 30 | 0.7822 | 0.8333 | 0.8343 | 0.8352 | 0.8352 | +0.0019 |
| `verified-adv-image-baseline-medium-vf` | 20 | 0.7300 | 0.7713 | 0.7713 | 0.7672 | 0.7672 | **−0.0041** |
| `verified-adv-image-baseline-pro-vf` | 30 | 0.7966 | 0.8478 | 0.8478 | 0.8465 | 0.8452 | −0.0026 |
| `verified-adv-pro-text-baseline` | 30 | 0.7889 | 0.8331 | 0.8331 | 0.8316 | 0.8316 | −0.0015 |
| `verified-adv-pro-text-baseline-pro-vf` | 20 | 0.7861 | 0.8287 | 0.8287 | 0.8258 | 0.8258 | −0.0029 |

**The approximation error is at most 0.0041 F1** across nine cells, two buffers
and four merge rules — an order of magnitude below the deduplication correction
itself (+0.042 to +0.058). In eight of the nine cells the `max`/`mean` rules
reproduce the post-hoc number **exactly**, because a cluster whose best member
cleared the threshold and whose worst member did not is rare: the verifier gives
near-identical probabilities to two crops of the same symbol.

The pathological bound is wider and worth stating honestly: if **every**
multi-member cluster flipped, `verified-adv-text-baseline` F1@30 would lie in
[0.8097, 0.8905] — the floor is 0.022 *below* the committed 0.8320. That
scenario requires the verifier to reverse itself on ~71 of 974 near-identical
crops, which the § 3.3 displacement figures make implausible, but it is the only
statement that is guaranteed without spending money.

### 3.5 Verdict

**A proper correction does not require re-running verification.** Report the
post-hoc-deduplicated numbers with a stated ±0.004 approximation band and the
E80 disclosure. If the principal investigator wants the exact preregistered
pipeline anyway, the price is in § 4.3 and it is small.

---

## 4. Task 3 — prioritised correction worklist

Ordering: (a) conclusion changes before numbers, (b) paper-cited before
internal, (c) cheap before dear.

### 4.1 Tier A — $0, point estimates only (sapphire, ≈ 45 min wall clock)

The probe harness already exists (`scripts/scoring_sensitivity_probe.py`); the
five committed batches took ≈ 6 min for 62 cells, so 155 conditions is ≈ 15 min
of scoring plus setup.

- [ ] **A1** Fix the two under-read conditions (§ 1.1) — 6 detection files,
  ~2 min. **Blocks A3, B2, B3.**
- [ ] **A2** Score the **6 exposed consensus conditions** the review could not
  probe (they carry no `source_tile`; score them under the committed
  first-intersecting rule so the two mechanisms stay separated). Expected
  ≤ +0.006 F1 by analogy with H13 arm C; currently an inference, not a
  measurement.
- [ ] **A3** Score the remaining **108 unmeasured exposed conditions** and
  rewrite `results/scoring-sensitivity-2026-08-18/exposure-survey.json` with a
  deduplicated F1 column, so every consumer can be audited without a bespoke run.
- [ ] **A4** Recompute the `era1-leaderboard` ranking on deduplicated point
  estimates and confirm the rank-7 → rank-1 flip (§ 2.6a).
- [ ] **A5** Recompute the `h6-a06-decision-rule` and `h6-a09-cost-gate` tables.
- [ ] **A6** Recompute `h1-cmt0106-pooled-modality`'s point estimate (+0.0238 →
  +0.0300 arithmetic already done; confirm from re-scored inputs).

### 4.2 Tier B — $0 but compute-heavy: CIs and permutation re-tiering (≈ 4–8 h sapphire)

Every tier, tie-set and p-value in the study comes from a 10,000-iteration BCa
bootstrap or a 10,000-iteration tile-swap permutation with BH-FDR. Point
estimates cannot answer tier membership.

Priority order — conclusion-bearing first:

- [ ] **B1** `results/diversity-dividend-384/tiering-{champions,with-deployable}/`
  — 22 cells, 3-member Tier 1, **conclusion reverses**. Re-run the permutation
  tiering. *Highest value per unit of work.*
- [ ] **B2** `results/era1-leaderboard/tiering_20m.json` — 82 cells, 3,321
  pairs, **Tier-1 leader flips**. Paper-cited at `results-draft.md:221-227`.
- [ ] **B3** `results/paper-eval/n1/512px-14buf-mcc/tiering/` — 36 cells, 630
  pairs, **all 20 Tier-1 members exposed**. Paper-cited at
  `results-draft.md:124-127` and marked "Load-bearing".
- [ ] **B4** `results/paper-eval/n1/384px-14buf-mcc/tiering/` — 18 cells, both
  Tier-1 members exposed. Paper-cited at `results-draft.md:148-152`.
- [ ] **B5** `results/metric-leaderboards/gs-era2-pv-family-30m` — rebuild the
  board with the 12 deduplicated `*-baseline*` rows, **F1 and MCC**, with CIs.
  This is the § R5 anchor **and** the tile-MCC top three.
- [ ] **B6** **Tile-level MCC under deduplication**, everywhere it is unmeasured
  — the single largest unquantified risk. Minimum set: the 12 `gs-era2`
  `*-baseline*` rows, the era-1 `verified-adv-image-t0.0` row, and the 55-map
  IM-k3 cell with a re-run of both MCC tierings.
- [ ] **B7** `results/tile-size-sweep` and `results/verifier-robustness`
  (`unswept-pools-completeness`) — re-run with CIs; the "global optimum" margin
  narrows.
- [ ] **B8** `results/family-fdr/{family_fdr.json,h1_cmt0106_pooled_modality.json}`
  — re-run the five-cell paired bootstrap and re-emit the BH table.
- [ ] **B9** Decide and execute on the 118 `results/leaderboard/**` legacy boards
  (refresh or mark superseded), then purge `.cache/`.

Sibling agent (a) already owns the MCC/CI/tiering re-measurement and has landed
`results/dedup-metric-impact-2026-08-18/spec-{diversity-dividend-384,
era1-single-pass-board,gs-era2-pv-family,consensus-exposed}.json` — B1, B3, B5
and A2 map directly onto those specs. **Coordinate before starting; do not
duplicate.**

### 4.3 Tier C — API spend (optional; **not** required)

Cost basis: `results/verifier-robustness/pareto/pareto_v2.json`
`cost_model.vf_call_usd = 0.000693`, measured at Gemini flex rates. Flex carries
the same 50 % discount as the async Batch API. The per-run `cost_estimate`
blocks in `outputs/**/*.meta.json` do **not** apply that discount and overstate
billing by ≈ 2×; they are not used here.

| Option | Calls | Cost (flex-discounted) | Buys |
|---|--:|--:|---|
| **C1** Re-verify only the **moved crops** of the four `pv-diag-384` baseline pools, × 3 verifier variants each: (71 + 60 + 45 + 64) × 3 = 720 | 720 | **≈ $0.50** | The exact preregistered accept decision for all 12 `gs-era2-pv-family-30m` `*-baseline*` rows |
| **C2** Full re-verification of the four deduplicated pools × 3 variants: (974 + 682 + 385 + 520) × 3 = 7,683 | 7,683 | ≈ $5.32 | The same, without relying on singleton-crop identity |
| **C3** Extend C1 to the other 14 exposed PV conditions (`proposer-verifier-384` ×8, `-512` ×1, `retest-phase2b` ×2, `55maps-image-generalisation` ×3, feed 7,878 crops at 1.05 % pair involvement ≈ 40 moved) | ≈ 800 | ≈ $0.55 | Completeness across all 26 exposed PV conditions |
| **C4** All of C2 + C3 | ≈ 10,000 | **≈ $7** | Belt and braces |

Caveats to state at the review gate: the $0.000693 rate is a Flash-verifier
measurement; six of the twelve baseline cells use a `gemini-3.1-pro-preview`
verifier, which is dearer — even at a 10× premium C1 stays under $5. **No
proposer (detection) call is needed under any option**, because deduplication is
strictly downstream of detection.

**Recommendation: do not spend.** § 3.4 bounds the error at 0.0041 F1. Spend
only if a reviewer explicitly challenges the post-hoc approximation.

### 4.4 Totals

| Tier | Work | Wall clock | US$ |
|---|---|---|--:|
| A | 6 items, point estimates over 155 conditions | ≈ 45 min sapphire | 0.00 |
| B | 9 items, CIs + permutation re-tiering of 6 first-class boards (+118 legacy) | ≈ 4–8 h sapphire | 0.00 |
| C | Optional exact pre-verification correction | ≈ 1 h + queue | 0.50 – 7.00 |
| — | Prose restatement, Obs, revision banners | ≈ 1 session | 0.00 |

---

## 5. What cannot be corrected without re-running experiments

- **5.1 The verifier's actual verdict on a merged crop.** Only recoverable by
  calling the API (Tier C, ≈ $0.50). **What the paper should do**: report the
  post-hoc-deduplicated value, state the ±0.004 measured band from § 3.4, and
  cite E80. This is a legitimate, quantified approximation, not a gap.
- **5.2 Tile-level MCC under a pre-verification pipeline.** Same dependency as
  5.1 for the PV cells; MCC under **post-hoc** deduplication is free (Tier B6).
  **What the paper should do**: report post-hoc MCC and note that the
  pre-verification variant is bounded by the same ±0.004-class argument.
- **5.3 `pro-medium-image-baseline` provenance mismatch.** The crop manifest
  records `total_detections = 519` sourced from
  `outputs/h11/pv-diag-384/pro-medium-image-baseline/image-t0.0/run_1/detections_image-t0.0_run01.geojson`,
  but that file now holds **587** features; the probabilities file holds 519
  results. The artefact the crops were built from is not the artefact on disk.
  Three `gs-era2` board rows depend on it. **What the paper should do**:
  investigate first (the 519-feature version may be recoverable from the crop
  manifest's `centroid_x`/`centroid_y`, as I did for `pro-medium-text-baseline`
  whose raw pass at `outputs/h11/pv-diag-384/pro-pilot-text/…` no longer exists
  at all); if not, report those three rows with a provenance caveat.
- **5.4 Whether a deduplicated proposer feed would have changed the
  *detections*.** It would not — deduplication is downstream of detection.
  Nothing to re-run. Worth stating explicitly so no reviewer asks.
- **5.5 The 12.5 %-overlap design decision itself.** H13 (arms A/B/C, the only
  conditions scored on explicitly deduplicated inputs) already answers what
  overlap buys; no further runs are needed.

---

## 6. Reproduction

All measurement ran on **sapphire** (`ssh sapphire`, `~/Code/map-reader-llm`,
`source .venv/bin/activate`); zero API calls; total wall clock ≈ 8 min. The four
throwaway analysis scripts are reproduced in the session transcript rather than
committed; each is a thin wrapper over committed library code:

- the analyses-manifest cross-reference joins
  `results/scoring-sensitivity-2026-08-18/exposure-survey.json` to
  `results/analyses-manifest.json` on `conditions_compared` and `tie_set`;
- the artefact-completeness check compares each condition's register
  `n_artefacts_read` against its committed `evaluation.json` `summary.n_runs`
  and against a directory listing of the recorded `input_files.detections`;
- the consumer census greps every full `condition_id` plus distinctive cell
  labels across `docs/`, `results/` and `reports/` markdown;
- the pre-versus-post-verification simulation reuses
  `merge_passes.deduplicate_within_pass`,
  `evaluate_detections.load_geojson` and
  `lib_advanced_metrics.calculate_f1_internal` unchanged, and asserts that the
  recomputed accept count equals the committed accepted-GeoJSON feature count
  before reporting anything.

---

## See also

- `reports/scoring-sensitivity-review-2026-08-18.md` — the measurement this
  worklist extends; § 1.1 and § 1.2 record two corrections to it
- `reports/dedup-gap-compliance-2026-08-18.md` — the preregistration reading
  (verdict: § 8.5 Step 1 is scoped to voting, so no committed number is wrong
  and the issue is a comparability confound)
- `docs/methodology/preregistration/protocol-errata.md` — **E80** (this gap,
  `:3835`), **E79** (order-dependent tile assignment), E75 (H13 execution)
- `results/scoring-sensitivity-2026-08-18/` — exposure register and five probe
  batches with their specs
- `results/dedup-metric-impact-2026-08-18/` — the sibling MCC/CI/tiering
  re-measurement (specs for `diversity-dividend-384`,
  `era1-single-pass-board`, `gs-era2-pv-family` and the exposed consensus cells)
- `results/analyses-manifest.json`, `results/hypothesis-outcome-table/`,
  `results/metric-leaderboards/`, `results/conditions-manifest.json` — the
  registers audited here
- `results/verifier-robustness/pareto/pareto_v2.json` — the flex-discounted cost
  model used for every US$ figure above

---

## Changelog

### 2026-08-18 — Original publication

First full blast-radius trace of the missing within-pass deduplication and the
prioritised correction worklist that follows from it. Built by joining the
155-condition exposure register to `results/analyses-manifest.json`,
`results/hypothesis-outcome-table/`, all 152 committed tiering artefacts, the
four `results/metric-leaderboards/` boards, the paper drafts, and a census of
270 markdown consumers; and by two new measurements: a completeness check of the
register's artefact resolution (which found two conditions read at 1 of 3
committed runs, one of them a Tier-1 member of two boards) and a
pre-versus-post-verification simulation over nine proposer-verifier cells that
bounds the post-hoc approximation error at **0.0041 F1**. Principal additions
beyond the prior review: a **fourth** conclusion at risk (the `era1-leaderboard`
Tier-1 leader flips, `results-draft.md:221-227`); the identification of tile-MCC
as the largest unquantified risk, with the top three MCC rows of
`gs-era2-pv-family-30m` all exposed and Discussion Seed 4 resting on exposed
cells at all three instruments; the H6 analyses (`h6-a06-decision-rule`,
`h6-a09-cost-gate`, Obs 415) which the prior review did not name; and a
costed finding that **no API spend is required** — the exact pre-verification
correction, if wanted, is ≈ US$0.50 on the flex-discounted basis.
