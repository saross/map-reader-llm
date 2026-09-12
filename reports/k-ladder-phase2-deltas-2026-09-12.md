# K-ladder Phase 2: what US$24.81 bought

> **Last revised**: 2026-09-12 (original publication — the Phase 2 run's
> closing report). Controlling card:
> `planning/k-ladder-review-2026-09-11.md` (rulings R1–R5); gate and costing:
> `reports/k-ladder-phase2-costing-2026-09-12.md`; pre-launch audit:
> `results/k-ladder-2026-09-12/phase2/pre_launch_audit.md`; findings:
> `results/k-ladder-2026-09-12/findings.md`.
> See [§ Changelog](#changelog).

## 1. The headline

The PI approved tiers A–D on 2026-09-12 at **US$24.84** — one pass of the
carried Gemini 3 verifier over each of 28 first-N consensus unions, 35,844
candidates. The run executed all four tiers and **spent US$24.8065** on the
audited flex basis: **3.35 cents, or 0.13 %, under the approval**, with every
candidate verified and none failed.

| Quantity | Approved | Actual |
|---|---:|---:|
| Rungs | 28 | **28** |
| Candidates offered | 35,844 | **35,844** |
| Candidates verified | — | **35,844 (100 %)**, 0 failed |
| Audited flex spend | US$24.84 | **US$24.8065** |
| Rungs stopped before verification | — | **none** |

**What it bought**: fourteen families that held two rungs each (K = 5 and
K = 10) now hold **four** (K = 1, 3, 5, 10) on one frame, one reference, one
verifier and one recipe — the thirteen Gemini 3 `pv-diag-384` families and the
3.7 gold-standard text screen. `results/k-ladder-2026-09-12/findings.md` § 7
reports them; the result is that **K's return is governed by the proposer's
thinking level**, with the F1 gain significant on 7 of 7 HIGH-thinking ladders,
2 of 6 MINIMAL ones, and four ladders — all MINIMAL — collapsing to a single
statistical tier in which K buys nothing detectable.

**The flex correction, stated first because the artefacts do not carry it.**
`scripts/run_pv.py` passes `--service-tier` to the API but stamps nothing about
it: every one of the 28 metas records `cost_basis: "list"`, `discount: 1.0`,
`discount_reason: "no discount applied"`, and no field anywhere names the tier.
Their recorded totals sum to **US$49.6130** — twice the invoice. Every figure in
this report is recomputed from the metas' own token counts on the basis the
whole corpus uses (`input × 0.25 + (output + thinking) × 1.50` per million,
i.e. flex at half of list), so the metas' own `total_cost_usd` must not be cited
unhalved. This reproduces `reports/r7-gaps-deltas-2026-09-11.md` § 2.3 on runs
made this session.

## 2. What was spent, per tier

Every figure below is a key of
`results/k-ladder-2026-09-12/phase2/spend-ledger.json`, rebuilt from the 28
committed `run.meta.json` files by
`scripts/run_k_ladder_phase2_verifier.py --recompute-ledger`.

| tier | rungs | candidates | verified | API requests | retries | audited flex USD | costed USD | USD per candidate | wall |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 4 | 6,492 | 6,492 | 6,635 | 143 | **4.4641** | 4.50 | 0.000688 | 25 m 52 s |
| B | 8 | 12,662 | 12,662 | 12,774 | 112 | **8.7115** | 8.77 | 0.000688 | 45 m 00 s |
| C | 12 | 12,877 | 12,877 | 13,004 | 127 | **8.9654** | 8.92 | 0.000696 | 47 m 02 s |
| D | 4 | 3,813 | 3,813 | 3,813 | 0 | **2.6655** | 2.64 | 0.000699 | 13 m 12 s |
| **total** | **28** | **35,844** | **35,844** | **36,226** | **382** | **24.8065** | **24.84** | **0.000692** | **2 h 11 m** |

**Requests and candidates are not the same number, and the ledger keeps them
apart.** 36,226 requests delivered 35,844 verified candidates; the 382-request
difference is retries, all of them server errors (`retries_server_error`), with
**zero rate-limit retries** at 20 workers throughout. The retried attempts
returned empty responses, so they cost tokens close to nothing — which is why
tier A's 143 retries did not move its spend above its costing. Tier D, the
smallest, needed no retries at all.

**The audited rate is corroborated a fifth time.** The adopted constant is
`VF_CALL_USD = 0.000693` (`reports/token-load-audit-2026-06-12.md` § 5, on a
measured spread of 0.000684–0.000698 across four deployment verifiers). All
four tiers land inside that spread — 0.000688, 0.000688, 0.000696 — with tier D
at 0.000699, one ten-millionth above its top. The 28-rung mean is **0.000692**,
0.1 % below the constant.

**Wall time.** 2 h 11 m for the whole gap-fill, in four sequential tiers at 20
workers. Sequential by design: the ledger is one JSON file the driver rewrites
after each rung, so two concurrent drivers would clobber each other's entries.
Daily quotas never came near binding — Gemini 3 Flash has no daily request cap,
and the 7 pm AEDT reset was never approached.

## 3. The 28 rungs

Sweep-optimal point per ruling R2, board frame `era2-b-487`, curator reference,
14 buffers, 10,000 BCa draws, seed 42, MCC. Every figure is a key of
`results/k-ladder-2026-09-12/phase2/scores.json`; `=` in a carried column means
the carried point is the same cell as the sweep-optimal one.

| # | family | K | cand. | opmax (k, p) | n | F1@20 | tile-MCC | carried F1@20 | carried MCC | same |
|---:|---|---:|---:|---|---:|---:|---:|---:|---:|:---:|
| 1 | MINIMAL text T 0.3 | 1 | 938 | (1, 0.15) | 409 | 0.8555 | 0.7986 | = | = | yes |
| 2 | MINIMAL text T 0.3 | 3 | 1,244 | (2, 0.15) | 401 | 0.8708 | 0.8040 | 0.8586 | 0.7556 | no |
| 3 | MINIMAL text T 0.7 | 1 | 1,012 | (1, 0.15) | 414 | 0.8575 | 0.7881 | = | = | yes |
| 4 | MINIMAL text T 0.7 | 3 | 1,355 | (2, 0.15) | 404 | 0.8725 | 0.7910 | 0.8629 | 0.7665 | no |
| 5 | MINIMAL text T 1.0 | 1 | 1,022 | (1, 0.20) | 415 | 0.8235 | 0.8095 | 0.8228 | 0.7961 | no |
| 6 | MINIMAL text T 1.0 | 3 | 1,588 | (2, 0.15) | 400 | 0.8647 | 0.8040 | 0.8279 | 0.7413 | no |
| 7 | HIGH text T 0.3 | 1 | 1,326 | (1, 0.20) | 443 | 0.8314 | 0.8068 | 0.8301 | 0.8022 | no |
| 8 | HIGH text T 0.3 | 3 | 2,201 | (3, 0.15) | 387 | 0.8783 | 0.8053 | = | = | yes |
| 9 | HIGH text T 0.7 | 1 | 1,370 | (1, 0.15) | 464 | 0.8009 | 0.7737 | = | = | yes |
| 10 | HIGH text T 0.7 | 3 | 2,755 | (2, 0.15) | 427 | 0.8492 | 0.7979 | 0.8408 | 0.7762 | no |
| 11 | HIGH text T 1.0 | 1 | 1,495 | (1, 0.20) | 451 | 0.7810 | 0.8162 | 0.7788 | 0.8071 | no |
| 12 | HIGH text T 1.0 | 3 | 2,848 | (2, 0.15) | 422 | 0.8541 | 0.7986 | 0.8220 | 0.7443 | no |
| 13 | MINIMAL image T 0.3 | 1 | 729 | (1, 0.20) | 440 | 0.7680 | 0.8443 | 0.7654 | 0.8475 | no |
| 14 | MINIMAL image T 0.3 | 3 | 885 | (3, 0.15) | 396 | 0.7774 | 0.8178 | = | = | yes |
| 15 | MINIMAL image T 0.7 | 1 | 694 | (1, 0.15) | 453 | 0.7252 | 0.8437 | = | = | yes |
| 16 | MINIMAL image T 0.7 | 3 | 950 | (2, 0.15) | 423 | 0.7599 | 0.8377 | 0.7522 | 0.7994 | no |
| 17 | MINIMAL image T 1.0 | 1 | 792 | (1, 0.15) | 465 | 0.7044 | 0.8360 | = | = | yes |
| 18 | MINIMAL image T 1.0 | 3 | 1,174 | (2, 0.20) | 424 | 0.7288 | 0.8178 | 0.7016 | 0.7629 | no |
| 19 | HIGH image T 0.3 | 1 | 872 | (1, 0.15) | 469 | 0.6925 | 0.8270 | = | = | yes |
| 20 | HIGH image T 0.3 | 3 | 1,619 | (2, 0.15) | 441 | 0.7215 | 0.8237 | 0.7207 | 0.7788 | no |
| 21 | HIGH image T 0.7 | 1 | 771 | (1, 0.15) | 474 | 0.6909 | 0.8435 | = | = | yes |
| 22 | HIGH image T 0.7 | 3 | 1,522 | (2, 0.20) | 426 | 0.7666 | 0.8435 | 0.7046 | 0.7621 | no |
| 23 | HIGH image T 1.0 | 1 | 982 | (1, 0.20) | 490 | 0.6119 | 0.8640 | 0.6098 | 0.8601 | no |
| 24 | HIGH image T 1.0 | 3 | 1,887 | (2, 0.15) | 418 | 0.7245 | 0.8294 | 0.6955 | 0.7389 | no |
| 25 | scale-4-optimal 487 | 1 | 830 | (1, 0.20) | 484 | 0.6376 | 0.8726 | 0.6350 | 0.8599 | no |
| 26 | scale-4-optimal 487 | 3 | 1,586 | (2, 0.15) | 412 | 0.7296 | 0.8443 | 0.7019 | 0.7354 | no |
| 27 | 3.7 text, GS B | 1 | 640 | (1, 0.15) | 502 | 0.8495 | — † | 0.8338 | — † | no |
| 28 | 3.7 text, GS B | 3 | 757 | (3, 0.10) | 494 | 0.8870 | — † | = | = | yes |

† tile-MCC withheld, not missing: this family's `source_tile` vocabulary is not
the board frame's, and tile-MCC is computed by string match rather than
geometrically. `findings.md` § 7.3 and § 6.1 below. F1 is unaffected.

**Three things worth noting about the operating points.**

1. **The two 487-tile frames never disagree.** Each rung was swept on both the
   board frame and the Era-2 frame `full_evaluation_bounds.geojson` — the frame
   the committed `-opmax` optima were selected on — and the F1@20 argmax
   coincided on **28 of 28**. The board's note that the two frames' optima agree
   for twenty of twenty-one committed pv cells extends to all 28 new ones, so the
   frame choice is not load-bearing for any rung here.
2. **Ten of the 28 rungs have one cell for both operating points.** Nine are
   K = 1 rungs, where the vote axis is degenerate (vote_t can only be 1) and the
   sweep argmax also lands on the carried probability; the tenth is HIGH text
   T 0.3 at K = 3, whose argmax is (3, 0.15), the carried point exactly. For
   those ten the transfer tax is **0.0000 by construction rather than by
   measurement**, one cell is materialised and scored, and one condition row is
   registered — registering two rows pointing at the same detections file would
   double-count the cell.
3. **One argmax needed the tie-break**, HIGH text T 0.7 at K = 1: two points tie
   at F1@20 0.8009 and the documented rule — highest F1, then lowest `vote_t`,
   then lowest `prob_t` — chose (1, 0.15). The project had no tie rule before
   this run; it now has one, and the number of tied points is recorded per rung.

## 4. What changed in each ladder

`findings.md` § 7 is the analysis; this is the delta. Thirteen of the fourteen
ladders went through the board's tile-swap instrument with `--permute-mcc`
(10,000 permutations, seed 42, BH q = 0.05) — the same instrument, gated the
same way, that §§ 4.1–4.2 used on the eight Phase 1 ladders. **All thirteen
gates passed**: every cell's rebuilt micro-F1 and tile confusion reproduce its
committed evaluation exactly (gap ±0.0000).

| ladder | ΔF1, K = 1 → best | BH p | tiers | tie set | ΔMCC | BH p | MCC sig. |
|---|---:|---:|---:|---:|---:|---:|:---:|
| MINIMAL text T 0.3 | +0.0224 | 0.2768 | **1** | 4 | −0.0251 | 0.6044 | no |
| MINIMAL text T 0.7 | +0.0164 | 0.5780 | **1** | 4 | +0.0077 | 0.8125 | no |
| MINIMAL text T 1.0 | +0.0546 | **0.0012** | 2 | 3 | −0.0214 | 0.5760 | no |
| HIGH text T 0.3 | +0.0559 | **0.0000** | 2 | 3 | −0.0263 | 0.5690 | no |
| HIGH text T 0.7 | +0.0735 | **0.0000** | 3 | 2 | −0.0096 | 0.8387 | no |
| HIGH text T 1.0 | +0.0993 | **0.0000** | 3 | 2 | −0.0252 | 0.8065 | no |
| MINIMAL image T 0.3 | +0.0139 | 0.7803 | **1** | 4 | −0.0065 | 0.9954 | no |
| MINIMAL image T 0.7 | +0.0629 | **0.0006** | 3 | 2 | −0.0214 | 0.9768 | no |
| MINIMAL image T 1.0 | +0.0383 | 0.1236 | **1** | 4 | −0.0282 | 0.6072 | no |
| HIGH image T 0.3 | +0.0780 | **0.0000** | 2 | 2 | +0.0024 | 0.9886 | no |
| HIGH image T 0.7 | +0.0959 | **0.0000** | 2 | 3 | −0.0076 | 0.8746 | no |
| HIGH image T 1.0 | +0.1514 | **0.0000** | 3 | 1 | **−0.0637** | **0.0420** | **yes** |
| scale-4-optimal 487 | +0.1307 | **0.0000** | 3 | 2 | −0.0572 | 0.0762 | no |
| 3.7 text, GS B | +0.0573 | not tested ‡ | — | — | withheld | — | — |

‡ The 3.7 family is excluded from the permutation testing by design, not by
oversight: the instrument runs the F1 and MCC arms over one set of swap masks,
and three of its five cells have an uninterpretable MCC (§ 6.1), so tiering it
would manufacture a large spurious MCC drop. Its F1 ladder is complete and is
reported in full in `findings.md` § 4.3 and `phase2/ladder-tables.md`.

**The four headline deltas.**

1. **Thinking level governs whether K pays at all.** Significant on **7 of 7**
   HIGH-thinking ladders and **2 of 6** MINIMAL; ΔF1 ranges +0.0559 to +0.1514
   with HIGH against +0.0139 to +0.0629 with MINIMAL.
2. **Four ladders are one statistical tier** — all four rungs in the tie set, K
   indistinguishable from K = 1 — and **every one is MINIMAL**: text T 0.3, text
   T 0.7, image T 0.3, image T 1.0. This is the first time the corpus can say
   that the pass-count lever buys nothing detectable on a specific
   configuration, because it is the first time a family has had four rungs.
3. **Temperature orders the gain within HIGH thinking, monotonically on both
   tracks**: text +0.0559 → +0.0735 → +0.0993 and image
   +0.0780 → +0.0959 → +0.1514 across T 0.3 → 0.7 → 1.0.
4. **The corpus's first significant tile-MCC decline**: HIGH image T 1.0,
   −0.0637, BH p = 0.0420, in the family with the largest F1 gain.
   `findings.md` § 4.1 found none among the eight Phase 1 ladders; the direction
   is now negative on 11 of the 13 with an interpretable MCC and supported by
   twenty-two ladders rather than eight.

**And the sharpest economic number in the corpus.** The 3.7 family's
K = 5 → K = 10 step buys **+0.0002 F1@20 for US$8.65** — about **US$43,000 per
0.001 F1**, two and a half times `findings.md` § 5's US$17,400 for 55-map
stride B. Every one of the fourteen ladders has K = 3 on its efficient set, at
31–44 % of the top rung's cost for 37–92 % of the gain.

## 5. What did NOT change

Listed because a reader's first question about a run this size is what it
disturbed.

- **The eight Phase-1 ladders.** No rung was added to any of them, no number in
  `findings.md` §§ 2–3 moved, and their permutation results (§§ 4.1–4.2, landed
  by a concurrent session the same day) are untouched. Phase 2 adds ladders; it
  does not revise them.
- **The signed Era-2 board.** It was not rebuilt, not re-tiered, and no
  signature field (`manually_verified_at`, `_signature_note`,
  `gates.G1.pi_ruling`) was written anywhere. Whether the new cells should join
  the board is a decision for the PI under "ladder, then board", not a side
  effect of this run — see § 8.
- **Every analysis row.** None was authored, none amended. The tiering the new
  ladders went through reads its cell set from a **scratch** analyses file, the
  pattern Phase 1 established, so the register gained no placeholder row.
- **The 55-map instrument ruling.** `findings.md` § 6.1 puts the choice of
  instrument for the seven 55-map ladders back to the PI. This run tiered
  **gold-standard ladders only** and did not pre-empt it.
- **The registered `pass-budget-pareto-v2` efficient set**, the E83 MCB ruling,
  and the stride ladders' registered outcomes — all outside this card's scope
  (`planning/k-ladder-review-2026-09-11.md` § 5) and all left alone.
- **The verifier.** One configuration for all 28 rungs, byte-identical, with no
  CLI override of model, temperature or thinking level (ruling R1). A tier-1
  test now greps the driver to keep it that way.

## 6. Corrections to documents this run read

Three, all recorded here rather than silently absorbed.

### 6.1 The costing's tier-A rationale overstates the ladder by one rung

`reports/k-ladder-phase2-costing-2026-09-12.md` § 5 justifies tier A partly on
the claim that MINIMAL text T 0.7 and HIGH text T 0.7 "also hold a K = 30 rung —
so [they] would each carry K = 1, 3, 5, 10, 30: five rungs, the longest
fixed-parameter ladder the corpus could have".

**That is wrong, and the register says so plainly.** The two K = 30 cells of
those pools are
`pv-diag-384::flash-minimal-text-n30-t07-text-t0.7-consensus-29of30` and
`pv-diag-384::flash-high-text-n5-text-t0.7-consensus-26of30`, and both carry
`aggregation: "consensus"` with `verifier_config: null` — they are
consensus-only cells at vote thresholds 29/30 and 26/30, with no verifier pass
at all. Ruling R1 fixes the carried verifier **at every rung**, so a
consensus-only cell cannot be a rung of one of these ladders.

Nor is the corpus's one verified 30-pass cell a substitute:
`pv-diag-384::verified-adv-text-consensus-16of30` is registered with
`n_passes: 1` and `vote_threshold: null` on pool
`flash-high-text-consensus-16of30`, because its verifier ran over an
already-thresholded 16-of-30 consensus rather than over the vote ≥ 1 union of
thirty passes. Its candidate universe is a different kind of object from a
ladder rung's.

So tier A bought a **four**-rung verified ladder at K = 1, 3, 5, 10, not a
five-rung one. Nothing about the purchase decision changes — four rungs at
fixed parameters on the pools the paper is built from was the point — but the
costing's sentence should not be quoted as it stands. The tier-A recommendation
itself is unaffected.

### 6.2 `pass_provenance` arrived mid-run

This run's brief said `pass_provenance` was not on `main`, and at the branch
point (`00e0d7759`) that was true: `voting_summary.json` carried only
`total_passes` and `thresholds`, and `build_pass_provenance` was not defined
anywhere in `scripts/`. Each rung's pass list was therefore recorded by hand in
its `experiment_intent.md`.

`origin/main` had in fact advanced 22 commits, one of them
`ac7d393c7 fix(consensus): record and check a union's pass list`. (The run's
first `git merge main` resolved the stale **local** `main` ref and reported
"Already up to date", which is why the divergence went unnoticed until later —
worth remembering as a failure mode: `git merge main` and
`git merge origin/main` are not the same command.) After merging, all 28 unions
were rebuilt under the new builder and now carry a machine-readable
`pass_provenance` block with a `git_blob_hash` per pass. § 7 records what that
rebuild proved.

### 6.3 Tile-MCC is a string join, and nothing warns when it breaks

This is the run's one substantive instrument finding, and it is not a
correction to a document so much as to an assumption every MCC column in the
corpus rests on.

`scripts/lib_advanced_metrics.py:2079` decides whether a tile holds a detection
like this:

```python
dets_in_tile = gdf_det[gdf_det['source_tile'] == tile_name]
```

A **string** comparison, not a geometric one. Point matching — and therefore F1
at every buffer — is geometric and unaffected. So a cell scored on a frame whose
`tile_name` vocabulary differs from the tiling its proposer ran on yields a
**correct F1 beside a meaningless tile-MCC**, and it fails quietly: the number
looks plausible, the evaluation reports nothing, and the board's own confusion
gate reproduces the same wrong confusion and passes it.

Phase 2's exposure was measured rather than assumed, with a new standing guard
(`scripts/check_tile_vocabulary_match.py`, output
`phase2/tile-vocabulary-match.json`): of **47** materialised cells, **44 MATCH
and exactly 3 MISMATCH**, all three the Gemini 3.7 GS text family's new rungs.
That family's proposer ran on the `ov192` tile set, whose names
(`…_x0_y1920.png`) are absent from the board frame's 336-stride vocabulary
(`…_x0_y2016.png`), so **21 of 502** detections land in a frame tile and the
K = 1 rung reports tp 10 / tn 257 / fp 1 / fn 219 — MCC 0.1337 — beside an F1@20
of 0.8495. The family's committed K = 5 rung is sound (tp 185, MCC 0.7651)
because its union carries frame-vocabulary names.

The response was to withhold, not to repair or to publish: those cells'
tile-MCC is kept as `tile_mcc_raw` with the reason and reported as withheld, and
the family is excluded from the permutation testing. `findings.md` § 7.3 states
it for the paper-facing reader; § 8 below puts the repair and the corpus-wide
question to the PI.

### 6.4 A pre-existing one-line drift in the conditions manifest

Regenerating the manifests surfaces one change that is **not** this run's: in
`results/conditions-manifest.json` the `verifier-t-pilot` entry's evaluation
path moves from `…/verifier-t-pilot__verified-t0-5/evaluation.json` to
`…/verifier-t-pilot__verified-t1-0/evaluation.json`. It is deterministic — the
generator produces a byte-identical manifest on repeat runs — so it is a drift
between `main`'s committed manifest and what `main`'s own register now yields,
not non-determinism in the generator. Flagged, not fixed: it belongs to whoever
owns the `verifier-t-pilot` rows.

## 7. Verification

Every gate this run passed, with the artefact that records it.

| # | Check | Result | Anchor |
|---:|---|---|---|
| 1 | Each rung's union size against the costing table | **28 of 28 exact** (delta +0 on every rung; nothing within an order of magnitude of the 2 % STOP) | `results/k-ladder-2026-09-12/phase2/unions.json` |
| 2 | Union totals against the approved figure | 35,844 candidates — the § 3 total the PI approved US$24.84 for | same |
| 3 | Independent re-derivation of every union from its pool | **28 of 28 `SUBPOOL-CONSISTENT`**: identical feature count and coordinates under bidirectional nearest-neighbour matching, correctly declared as a first-N sub-pool. **Zero `STALE`, zero `UNRESOLVED`** | `results/k-ladder-2026-09-12/phase2/union-provenance.json`, by `scripts/check_union_provenance.py` |
| 4 | That the union rebuild under the new builder changed no candidate | **28 `voting_summary.json` modified, zero `consensus_t*.geojson`** — so the refactor is behaviour-preserving AND these unions are the ones the verifier consumed | commit `19e56ed80` |
| 5 | Crops from the source rasters, never tile PNGs (E33) | every rung's manifest: `raster_crops == total_detections`, `tile_fallback_crops == 0`, enforced as a pre-spend gate rather than checked afterwards | `scripts/run_k_ladder_phase2_verifier.py`, `verify_rung` |
| 6 | Crop count equals union size, per rung, before any API call | gate passed on every rung | same |
| 7 | Every candidate resolves to a gold-standard raster | 35,844 of 35,844; four rasters and only four; **0 missing `source_tile`, 0 unresolvable** | `pre_launch_audit.md` § 3 |
| 8 | Verifier configuration identical across rungs | one config file, unmodified; instruction SHA-256 `2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25dc1454af3497e15d`, the same hash the August 3.7-screen verifier stamped | `pre_launch_audit.md` §§ 2–3 |
| 9 | Candidates verified against API requests billed | reconciled per rung; the difference is retries, all recorded | `spend-ledger.json` |
| 10 | Audited flex cost against the recorded list cost | exactly half, on every rung, by construction of the basis | same |
| 11 | The 3.7 stage's index join before deriving anything from it | re-applying (vote 5, prob 0.10) to the committed K = 5 stage reproduces **443 features**, the count its committed cell holds | `scripts/derive_g37_gs_opmax_rungs.py`, `CARRIED_CROSSCHECK` |
| 12 | This run's cost model against the registered Pareto's | the MINIMAL text T 0.7 K = 5 rung prices at **US$2.43 all-in**, reproducing `pass-budget-pareto-v2`'s "min6 $2.43" for the same cell | `results/k-ladder-2026-09-12/phase2/ladders.json`; card § 2 |
| 13 | Register validator, before and after the 46 new rows | **identical profile**: `pv-diag-384` 0 errors with 10 `geojson-missing` and 66 `pool-unresolved` (verdict `partial`) both before and after; `gemini37-screen-2026-08-28` a clean `PASS` both times. The new rows add no warning and no error | `scripts/verify_run_conditions.py` |
| 14 | Schema validation of the whole register after regeneration | **ALL VALID** — 41 runs + 588 conditions + 1,314 passes + 66 analyses | `scripts/generate_post_run_report.py --all --write` |
| 15 | Tier-1 tests | **2,403 passed, 1 skipped, 3 xfailed, 0 failed** in 193 s (`python -m pytest -m tier1 -q`, on sapphire). 37 of them are this run's new module; the known `test_per_arch_md_ownership.py` environment failure did not recur, having been fixed on `main` | `tests/test_k_ladder_phase2.py` and the suite |

## 8. What is still outstanding, and whose call it is

- **The Hsu MCB admissible set per family.** Still not supplied, exactly as
  `findings.md` § 6.1 says; it is a different instrument
  (`scripts/selection_aware_intervals.py`). A gap in the run, not in the data.
- **Whether the new cells join the Era-2 board.** Under "ladder, then board"
  every verified cell on the board's frame feeds the board, and these **46**
  cells qualify on frame, reference and verifier. They were not admitted here:
  the board was re-signed on 2026-09-10 and admitting a cohort this size is a
  re-tier and a re-signature, which is the PI's to authorise. Note that
  admitting them would roughly halve the board's Gemini 3 F1 floor — several
  K = 1 image rungs score in the 0.61–0.69 range — so the decision changes what
  the board's tiering means, not just its row count.
- **Whether the 3.7 family's tile-MCC should be repaired.** Re-keying its
  `source_tile` to the frame's vocabulary by spatial containment would work and
  would reproduce what that family's committed unions already do, but it
  requires a rule for which tile wins where tiles overlap. That is a
  methodological choice, so it is put rather than taken. The wider question —
  which other cells in the corpus are scored on a frame whose tile vocabulary
  differs from their proposer's tiling — is also open;
  `scripts/check_tile_vocabulary_match.py` can answer it in one run over any
  cell set.
- **Which reading of "the carried point" the ladders should report.** The
  corpus holds two and they diverge sharply above K = 3 (§ 4). Both are
  computed and committed; the choice is the PI's.
- **The signed verifier-uplift analysis row needs nothing.** This was the one
  open worry, and it resolved cleanly rather than by judgement. Its outcome text
  states "145 of 172 pairs computed on F1", and the concern was that 46 new
  verified cells would move those counts and strand a signed row. They do not:
  **every one of the 46 is a board-frame row**, and the supplement excludes
  board-frame rows by the PI's 2026-09-10 rule — a row whose
  `scope_override.test_set_id` names a leaderboard frame is a board artefact
  rather than a measurement of its own
  (`scripts/lib_uplift_supplement.py:1227`, `BOARD_FRAMES = {"era2-b-487"}`).
  Regenerating the plan says so in its own numbers: **board-frame exclusions
  rise from 103 to 149 — exactly the 46 — while the pairable population stays at
  170 rows with 0 blocked.** The row was not touched and is not stale. Had the
  rows been registered on a native frame instead, this would have been a
  re-signature request.
- **The 55-map ladders' instrument.** Unchanged and still with the PI.

## Changelog

### 2026-09-12 — Original publication (K-ladder Phase 2)

The closing report of the Phase 2 run: tiers A–D, approved by the PI on
2026-09-12 at US$24.84 and executed the same day for **US$24.8065** audited
flex over 28 rungs and 35,844 candidates, with 0 failures and no rung stopped.

Written from artefacts this run produced and re-read in the same session:
`results/k-ladder-2026-09-12/phase2/spend-ledger.json` (§ 2),
`…/phase2/scores.json` (§ 3), `…/phase2/mcc-test/summary.json` and
`…/phase2/mcc-test/tiering/*/tiering_20m.json` (§ 4),
`…/phase2/unions.json` and `…/phase2/union-provenance.json` (§ 7 rows 1–4),
`…/phase2/tile-vocabulary-match.json` (§ 6.3),
`…/phase2/ladders.json` and `…/phase2/ladder-tables.md` (§ 4's economics),
`results/run-conditions.json` (the 46 rows and the K = 30 correction of § 6.1),
`results/uplift-supplement/verifier-pairing-report.md` (§ 8's uplift item), and
`scripts/lib_advanced_metrics.py`, `scripts/lib_uplift_supplement.py` and
`scripts/run_pv.py` for the three mechanisms the report names.

Companions written or amended in the same run:
`results/k-ladder-2026-09-12/findings.md` § 7 (the analysis),
`reports/k-ladder-phase2-costing-2026-09-12.md` (marked RUN; its tier-A
rationale corrected), and
`results/k-ladder-2026-09-12/phase2/pre_launch_audit.md` (the gate).

Landed on branch `worktree-agent-ae87367bcee3e0e5c`.
