# Performance-shape 2×2 — per-run availability map

> **Last revised**: 2026-05-31 (original publication). See [§ Changelog](#changelog) for revision history.

**Created**: 2026-05-31.
**Status**: READ-ONLY inspection — no scoring, no data writes. A planning artefact
mapping which of four "performance-shape" points each run can yield, and at what
cost (already-on-disk vs deterministic-transform vs new API spend).
**Inputs**: live `outputs/` tree, `results/run-registry.json` (27 runs),
`results/run-facts.json`. Pass-layout reference: `planning/manifest-3b-conditions-plan.md`,
`scripts/generate_post_run_report.py --draft-run <id>`.
**Scope**: the 26 non-gold-standard runs in the registry. `gold-standard-v2` is the
complete-2×2 exemplar (single-run + consensus_t1…t5 + verified-v1 over the 4-of-5
consensus) and is excluded per the task brief.

---

## 1. The 2×2 being mapped

For each run, four performance points drawn from its detection passes:

| Quadrant | Definition | Typical on-disk evidence |
|---|---|---|
| **single-run** (no verify) | each of the K proposer passes scored individually (n=1) → single-pass mean ± σ | per-pass `…/run_N/detections*.geojson`, or a `…-baseline` single-pass set |
| **consensus** (no verify) | vote-threshold sets over the K passes | `consensus/consensus_t1…tK.geojson` or `consensus-Nof5.geojson` |
| **single-run-PV** (n=1 + verify) | a VERIFIED set whose candidate input is the **single-pass union** (every point returned by 1-of-n) | verified geojson / probabilities whose candidate manifest `source_geojson` is a single proposer pass or a `…-1of-n` / `1of5` set |
| **consensus-PV** (consensus + verify) | a VERIFIED set whose candidate input is a **k-of-n consensus** set | verified geojson / probabilities whose candidate manifest `source_geojson` is a `consensus-Nof5` / `vt≥2` set (e.g. gs-v2's verified-v1 over 4-of-5) |

**Which quadrant a verified output fills is determined per run by inspecting what
candidate set the verifier ran over** (candidate-manifest `source_geojson`, the
`…NofM` / `vtN` naming, and the verified geojson's `vote_count` distribution),
**not assumed**. Per the project lead's note, the verifier's candidate set
migrated over time from "verify a particular k-of-n" to "verify everything 1-of-n
returned"; both patterns appear in the corpus below.

### Legend

- **M** = **materialised** — a scoreable geojson exists on disk now.
- **D** = **derivable-cheap** — exists but needs a deterministic transform + re-score,
  no API. Two flavours:
  - *D(filter)* — a full-candidate verified geojson carrying a `verified` boolean +
    `verification_threshold`; the accepted subset is `verified:true` (Decision 1A).
  - *D(materialise)* — verifier `probabilities.json` (per-candidate `mound_probability`)
    exists but no geojson; materialise at a probability threshold, then score.
  - *D(score)* — per-pass / consensus geojsons exist but have not been scored for this
    quadrant; just run the scorer.
- **A** = **absent** — would need new API spend (no verification was run over this
  candidate set; or no passes exist to build the quadrant).
- **n/a** = structurally inapplicable (e.g. a K=1 single-pass run has no consensus).

---

## 2. Per-run availability table

K = number of proposer passes (per pool; the dominant pool's K is shown, with
per-pool variation noted). PV columns note the verifier's candidate set and
accepted/total where visible.

| run | K | single-run | consensus | single-run-PV | consensus-PV | notes |
|---|---|---|---|---|---|---|
| 55maps-generalisation | 5 | M | M (`consensus-4of5`) | A | **M** | verified over **4-of-5** (manifest `source_geojson=consensus-4of5`); pre-filtered `verified_detections_paired` = 4 068 accepted (no `verified` flag → materialised). Carry-forward #10 (paired verifier). |
| 55maps-image-generalisation | 5 | M | M (`consensus-3of5`) | A | **M** | pool `library_plus-hp`; verified over **3-of-5**; pre-filtered `verified_detections` = 4 680 accepted. |
| 55maps-text-high-generalisation | 5 | M | M (`consensus-4of5`) | A | **M** | verified over **4-of-5**; `verified_detections` = 4 164 accepted. |
| 55maps-text-high-t0-3-generalisation | 5 | M | M (`consensus-4of5`) | A | **M** | verified over **4-of-5**; `verified_detections` = 4 350 accepted. Physical dir is dotted (`…t0.3…`). |
| 55maps-text-min-generalisation | 5 | M | M (`consensus-4of5`) | A | **M** | verified over **4-of-5**; `verified_detections` = 3 865 accepted. |
| h10 | 5 | M (4 pools ×5) | M (`consensus_t1…t5`, 4 pools) | A | **M (pool_160 only)** | verified materialised only for `pool_160_hp4hn4` (`detections_vt4_pt0.05` = 232, over **4-of-5**). pool_020/040/080 have single-run+consensus but **no verified** → their consensus-PV is **A**. |
| consensus-384-t1-0 | 30 | M (30 passes) | M (`consensus_t1…t5` ×2 clip variants) | A | A | E43 T=1.0 deviation; rich single-run+consensus, **no verifier ran** at all → both PV quadrants absent. |
| e47-propose-brief | 5 | M | M (`consensus_t1…t5`) | A | A | propose-brief proposer; no verifier outputs in tree → PV column empty. |
| n1-outstanding-384 | 3 (5 pools); 1 (2 pro pools) | M | M (`consensus_t1…t3`, 5 pools) | A | A | 7 pools, mostly K=3; two `pro-*-medium-t07` pools are K=1 (single-run only, n/a consensus). No verifier → PV absent. |
| proposer-verifier-384 | 1 | M (1 proposer pass) | n/a | **D(filter)** | A | **single-pass** run: candidate manifest `source_geojson` = one proposer pass (572). 14 verified geojsons carry `verified` flag (e.g. `verified-brief-text` = 269/572). Verifies the **single-pass union** → single-run-PV (derivable: filter `verified:true`). No consensus (K=1). |
| proposer-verifier-512 | 1 | M (1 proposer pass) | n/a | **D(filter)** | A | single-pass; manifest source = one proposer pass (140). `verified-adversarial-text` = 72/140 (`verified` flag). single-run-PV derivable; no consensus. |
| pv-diag-256 | 5 | M (`text-baseline`) | M (`text-2of5…5of5`; `text-1of5`=vote≥1 union) | A | A | 256px diagnostic. Only consensus + single-pass-baseline geojsons live; **no verified geojsons and no verifier `probabilities.json`** in tree (evals archived to `archive/results-non-production-tile-sizes/h11-256-pv-diagnostic/`). Both PV quadrants absent on disk. |
| pv-diag-384 | 1/3/5/10/30 (many pools) | M (per-pass + `…-baseline`) | M (`consensus_t1…tK` per pool) | **D(materialise)** | **D(materialise)** | GAP-7 many-pass run. `verified/<set>/probabilities.json` exist for ~138 candidate sets spanning **`1of5`/`1of10`/`1of30` (single-pass union → single-run-PV)** AND **`2of5`…`Nof5` (consensus → consensus-PV)**, each with real per-candidate `mound_probability` (e.g. `text-1of5` results=974). **No materialised verified geojson** → both PV quadrants derivable by materialising at a probability threshold. |
| h12-v2 | 5 | M (`r1-hn-heavy`, `r3-hp-heavy`) | M (`greedy/…/consensus_t1…t5`) | A | A | r2-balanced is a cross-run condition (reuses h10 pool_160, GAP-6). No verifier outputs → PV absent. |
| h8-v2 | 5 (7 pools) | M (7 composition pools ×5) | M (`greedy/<pool>/consensus_t1…t5`) | A | **M (3 pools only)** | verified materialised only for `scale-4` (`detections_vt4_pt0.10`=251, over 4-of-5) and wbf `scale-4`/`scale-8`. The other 4 pools (canonical, plus-hp, pure-positive-canon, scale-16, scale-32) have single-run+consensus but **no verified** → their consensus-PV is **A**. |
| retest-phase2a | 3 | M (5 pools ×3) | M (`consensus_t1…t3`, 5 pools) | A | A | Era-1 512px (H1). No verifier → PV absent. GAP-9 meta shape (no `per_item_metadata`). |
| retest-phase2b | 3 | M (10 temp pools ×3) | M (`consensus_t1…t3`, 10 pools) | A | A | H7 temperature sweep; no verifier → PV absent. |
| retest-phase2c | 1 | M (13 composition pools ×1) | n/a | A | A | H8; all pools K=1 (single-pass only) → consensus n/a, no verifier → PV absent. |
| retest-phase2d | 1 | M (4 pools ×1) | n/a | A | A | H5; K=1 pools (`detections_*_run01` are the single passes, not verified). consensus n/a, no verifier. |
| retest-phase2e | 1 | M (4 pools ×1) | n/a | A | A | H4 ordering study; K=1 → consensus n/a, no verifier. |
| retest-phase3a | 30 | M (6 temp pools ×30) | M (`consensus_t1…t30`, 6 pools) | A | A | H3; deep consensus sweep, no verifier → PV absent. |
| retest-phase3a-high | 30 | M (3 temp pools ×30) | M (`consensus_t1…t30`) | A | A | H3 HIGH; no verifier. |
| retest-phase3a-replication | 30 | M (`high`, `minimal` ×30) | M (`consensus_t1…t30`) | A | A | H3 replication; no verifier. |
| retest-phase3c | 5 | M (45 H9 pools ×5) | M (`consensus_t1…t5`, 45 pools) | A | A | H9 diversity (track1-image/track2-text × h9-A…E × passes). No verifier → PV absent. |
| retest-h11-single-pass-384-t0 | 10 | M (10 passes) | M (`consensus_t1…t10`) | A | A | H11 single-pass baseline; no verifier → PV absent. |
| verifier-t-pilot | — (no own proposer) | n/a (reuses gs-v2) | n/a (reuses gs-v2) | A | **M** | Verifier-only run: T0.0/T0.5/T1.0 verify gs-v2's **4-of-5 consensus** (vote4). `T*/materialised/vote4_prob*.geojson` are materialised consensus-PV (e.g. `vote4_prob0.20` = 371 features, votes {5:317,4:54}). single-run/consensus columns belong to its source run (gs-v2), not here. |

---

## 3. Summary

**Complete-or-cheap 2×2 (all four reachable quadrants are M or D):** the
generalisation family and the two proposer-verifier runs.

| Group | Count | Shape |
|---|---|---|
| **Complete materialised 2×2** (single-run M + consensus M + a PV that is M) | **5** | 55maps-generalisation, -image, -text-high, -text-high-t0-3, -text-min — each has single-run, consensus, and a **materialised consensus-PV** (over 3- or 4-of-5). single-run-PV is **A** (not the same candidate set), but the consensus-PV diagonal is complete. |
| **Cheap-to-complete via derivation** (PV is D, no API) | **3** | proposer-verifier-384, proposer-verifier-512 (single-run-PV = D-filter), pv-diag-384 (both PV columns = D-materialise across the candidate-set sweep). |
| **Partial PV materialised** (PV exists for some pools, A for others) | **2** | h10 (consensus-PV M for pool_160 only; A for pool_020/040/080), h8-v2 (consensus-PV M for scale-4 + wbf scale-4/scale-8; A for 4 other pools). |
| **Verifier-only (PV M, no own no-verify columns)** | **1** | verifier-t-pilot (consensus-PV materialised; single-run/consensus inherited from gs-v2). |
| **No-verify only — both PV quadrants A** (have single-run ± consensus, no verifier ran) | **15** | consensus-384-t1-0, e47-propose-brief, n1-outstanding-384, pv-diag-256, h12-v2, retest-phase2a/2b/2c/2d/2e, retest-phase3a/3a-high/3a-replication/3c, retest-h11-single-pass-384-t0. |

**Headline counts (of the 26 non-gs runs):**

- **Both PV quadrants reachable now without API** (M or D on at least the
  consensus-PV diagonal): **11 runs** — the 5 generalisation runs (consensus-PV M),
  proposer-verifier-384/512 (single-run-PV D), pv-diag-384 (both D), h10 +
  h8-v2 (consensus-PV partially M), verifier-t-pilot (consensus-PV M).
- **PV gaps that would need a little API to round out**: **15 runs** have **no
  verifier output at all** (both PV quadrants A), plus **2 runs** (h10, h8-v2)
  have consensus-PV materialised for only a subset of pools. The single-run-PV
  quadrant is the most universally absent: only proposer-verifier-384/512 and
  pv-diag-384 carry it, and only the latter two as already-on-disk evidence.

> **Note on "complete 2×2":** *no non-gs run has all four quadrants as M/D.* The
> generalisation runs and the partial-PV runs (h10, h8-v2) have a materialised
> **consensus-PV** but an absent **single-run-PV** (the verifier ran over the
> consensus set, not the 1-of-n union). The proposer-verifier runs have the
> opposite (single-run-PV D, no consensus at all because K=1). **pv-diag-384 is
> the only non-gs run whose verifier swept *both* candidate-set families** —
> making it the single closest analogue to a full 2×2, entirely derivable.

---

## 4. To round out the PV column

Runs needing **new n=1 (single-pass-union) verification** to gain a single-run-PV
point (the most-absent quadrant). Rough scale = number of single-pass-union
candidates to verify (1 API call per candidate crop, 1 verifier pass):

| run | candidate set to verify | rough scale | note |
|---|---|---|---|
| 55maps × 5 | 1-of-5 union per run (≈ the `consensus-4of5` is already verified; the union is larger) | ~5–9 k crops/run | large (8 541-tile corpus); only do if the single-run-PV diagonal is wanted for the generalisation headline. |
| h10 (pool_020/040/080) | per-pool 1-of-5 union | a few hundred–~1 k crops/pool | also needs consensus-PV for these 3 pools (only pool_160 done). |
| h8-v2 (canonical, plus-hp, pure-positive-canon, scale-16, scale-32) | per-pool 1-of-5 union | a few hundred–~1.5 k crops/pool | consensus-PV also absent for these 5 pools. |
| n1-outstanding-384, e47-propose-brief, consensus-384-t1-0, h12-v2, retest-phase2a/2b/2c/2d/2e, retest-phase3a/3a-high/3a-replication/3c, retest-h11-single-pass-384-t0 | per-pool single-pass union | varies; the K=30 retest runs are the largest unions | these have **no verifier at all** — rounding out *either* PV quadrant is new API for the whole run. |

**Cheapest wins (no API):**

1. **pv-diag-384** — materialise its existing `probabilities.json` at a chosen
   probability threshold to get **both** single-run-PV (`…1of5/1of10/1of30`) and
   consensus-PV (`…2of5…Nof5`) points. Pure transform + score.
2. **proposer-verifier-384 / -512** — filter the existing `verified:true` subset
   from the materialised-with-flag geojsons for a single-run-PV point. Pure filter
   + score.
3. **h10 pool_160 / h8-v2 scale-4 / verifier-t-pilot / the 5 generalisation runs**
   — consensus-PV geojsons already materialised; just score.

**Smallest API to add the single-run-PV diagonal where it is most informative:**
the two proposer-verifier runs already *have* it (single-pass), and pv-diag-384
already has it derivable — so the single-run-PV story can be told at **zero API
cost** on those three. Extending it to the generalisation headline runs is the
only PV expansion that would justify fresh verifier spend, and that is a large
(thousands-of-crops) job on the 55-map corpus.

---

## Changelog

### 2026-05-31 — Original publication

First availability map. Built READ-ONLY from the live `outputs/` tree,
`results/run-registry.json` (27 runs), and `results/run-facts.json`, with
candidate-set provenance read from per-run `crops/candidate_manifest.json`
(`source_geojson`), verified-geojson `vote_count` distributions and `verified`
flags, and verifier `probabilities.json` shapes. Classifies the 26 non-gs runs
across the four performance-shape quadrants (M/D/A). Headline: 0 non-gs runs have
a fully materialised 4-quadrant 2×2; 11 are reachable now without API (mostly on
the consensus-PV diagonal); the single-run-PV quadrant is the most absent
(present/derivable only on proposer-verifier-384/512 and pv-diag-384). No data
were scored or modified.
