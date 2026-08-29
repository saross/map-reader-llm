# K = 1 gap-fill — worklist and verifier-coverage disclosure

> **Last revised**: 2026-08-29 (regenerated from committed artefacts by `scripts/build_k1_gapfill_worklist.py`; original publication; the K = 1 plan and its disclosure). See [§ Changelog](#changelog) for revision history.
>
> **First published**: 2026-08-29. Regenerated 2026-08-29T04:34:04Z. This document is generated in full from committed artefacts, so its body always reflects the current corpus; git carries the content history.

Build order step 2 of `planning/uplift-supplement-2026-08-28.md`. No
scoring has been run: this document and its worklist are the plan.

The worklist tracks two anchors separately, because they have different
availability. `status` is the readiness of the **no-verifier** N = 1
job — the anchor consensus uplift needs, scored from a committed raw
pass. `k1_with_verifier` is the verdict on the **with-verifier** N = 1
anchor, which no job can supply where the verifier never saw singleton
candidates.

## No-verifier N = 1 jobs

| Status | Cells |
|---|---:|
| `already-registered` | 26 |
| `blocked` | 51 |
| `ready` | 115 |

## With-verifier N = 1 anchors

| Verdict | Verified cells |
|---|---:|
| `blocked` | 50 |
| `derivable` | 37 |

## The disclosure: K = 1 WITH verifier

Consensus uplift needs an N = 1 anchor. For a *verified* cell the
honest anchor would be a single pass put through the same verifier —
and for most of the corpus that cell cannot exist, because the verifier
never saw singleton candidates. The card records this; the numbers below
are measured rather than assumed.

Each verifier stage writes a `candidate_manifest.json` listing the
candidates it cropped, each carrying the `vote_count` it arrived with.
The minimum in THAT stage's manifest is the floor of coverage for the
cells it produced.

**Only verified cells carry a citation.** A consensus cell has no
verifier stage, so any manifest attributed to it is a false evidence
path. Forty-one such rows were published before this was noticed, every
one of them pointing at some other lineage's stage.

**A pool that verified in its own subtree owns those stages.** Run-level
stages belong to whichever lineage built them. In `pv-diag-384` they
belong to different pools entirely: `verified/image-6of10` cropped
`consensus/image-1of10.geojson`, while the
`flash-high-image-n5/image-t1.0` pool cropped its own
`image-t1.0/consensus/consensus_t1.geojson`. Both are image, both carry
the shell, so token scoring cannot separate them; containment in the
pool directory decides it.

One apparent exception was checked and is not one. `h8-v2`'s
WBF-verified cells cite `outputs/h8-v2/wbf/scale-4/crops/`, outside the
`scale-4` proposer-pool directory. The recorded sources settle it: that
stage cropped `wbf_candidates.geojson` while the in-pool stage cropped
`consensus_t1.geojson`, so the WBF stage IS the right one for a
WBF-verified cell. The pool-subtree rule therefore runs after the
fusion-family filter, never before it.

**Coverage is a property of a verifier STAGE, not of a run.** An earlier
build of this worklist took the minimum across every manifest in a run
and published it per condition. That is wrong wherever a run verified
several shells: `verifier-robustness` ran a vote >= 1 union stage
alongside three vote >= 3 stages and one vote >= 16 stage, so the
run-wide minimum of 1 declared a K = 1 PV anchor derivable for cells
whose verifier never saw a candidate below vote 3, citing as evidence a
manifest belonging to a different condition. Each cell is now matched to
its own stage, and `verifier_floor_basis` names the rule that matched
it; a cell that cannot be matched is disclosed as unmeasurable rather
than given the run minimum.

The `Manifest` column is the evidence path: thirty-one stages share a
source-set name, so the source alone does not identify which stage a
floor was measured on.

| Run | Manifest | Source set | Floor (`vote_count` >=) | Cropped |
|---|---|---|---:|---:|
| `55maps-generalisation` | `outputs/55maps-generalisation/crops/candidate_manifest.json` | `consensus-4of5.geojson` | 4 | 8942 |
| `55maps-image-generalisation` | `outputs/55maps-image-generalisation/crops/candidate_manifest.json` | `consensus-3of5.geojson` | 3 | 7878 |
| `55maps-text-high-generalisation` | `outputs/55maps-text-high-generalisation/crops/candidate_manifest.json` | `consensus-4of5.geojson` | 4 | 9205 |
| `55maps-text-high-t0-3-generalisation` | `outputs/55maps-text-high-t0.3-generalisation/crops/candidate_manifest.json` | `consensus-4of5.geojson` | 4 | 9910 |
| `55maps-text-min-generalisation` | `outputs/55maps-text-min-generalisation/crops/candidate_manifest.json` | `consensus-4of5.geojson` | 4 | 10170 |
| `55maps-text-min-n10-uplift` | `outputs/55maps-text-min-n10-uplift/crops-3of10/candidate_manifest.json` | `text-min-3of10.geojson` | 3 | 16482 |
| `e47-propose-brief` | `outputs/h11/e47-propose-brief/crops/flash-high-text-1of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 1 | 4358 |
| `e47-propose-brief` | `outputs/h11/e47-propose-brief/crops/flash-high-text-1of5-v2-failed/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 1 | 66 |
| `e47-propose-brief` | `outputs/h11/e47-propose-brief/crops/flash-high-text-1of5-v2-final-retry/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 1 | 1 |
| `e47-propose-brief` | `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 1 | 4358 |
| `e47-propose-brief` | `outputs/h11/e47-propose-brief/verified/flash-high-text-2of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 2 | 1654 |
| `e47-propose-brief` | `outputs/h11/e47-propose-brief/verified/flash-high-text-3of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 3 | 1072 |
| `e47-propose-brief` | `outputs/h11/e47-propose-brief/verified/flash-high-text-4of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 4 | 753 |
| `e47-propose-brief` | `outputs/h11/e47-propose-brief/verified/flash-high-text-5of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 5 | 487 |
| `flash35-pv-2x2` | `outputs/flash35-pv-2x2/crops/candidate_manifest.json` | `flash35-min-text-1of10.geojson` | 1 | 1132 |
| `flash35-pv-2x2` | `outputs/flash35-pv-2x2/min-f3-crops/candidate_manifest.json` | `f3-min-text-1of10-with-passes.geojson` | 1 | 1939 |
| `gold-standard-v2` | `outputs/gs/gold-standard-v2/crops/candidate_manifest.json` | `consensus-4of5.geojson` | 4 | 608 |
| `grid-2026-08-18` | `outputs/grid-2026-08-18/verifier/g384_ov048/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 1827 |
| `grid-2026-08-18` | `outputs/grid-2026-08-18/verifier/g384_ov192/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 3319 |
| `grid-2026-08-18` | `outputs/grid-2026-08-18/verifier/g512_ov064/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 1402 |
| `grid-2026-08-18` | `outputs/grid-2026-08-18/verifier/g512_ov256/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 2585 |
| `h10` | `outputs/h10/evaluation-v2/pool_020_hp4hn4/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 1763 |
| `h10` | `outputs/h10/evaluation-v2/pool_160_hp4hn4/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 1454 |
| `h8-v2` | `outputs/h8-v2/scale-4/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 1551 |
| `h8-v2` | `outputs/h8-v2/wbf/scale-4/crops/candidate_manifest.json` | `wbf_candidates.geojson` | 1 | 1114 |
| `h8-v2` | `outputs/h8-v2/wbf/scale-8/crops/candidate_manifest.json` | `wbf_candidates.geojson` | 1 | 1002 |
| `image-b-gs-2026-08-28` | `outputs/image-b-gs-2026-08-28/verifier/g384_ov192_image/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 4065 |
| `image-b-gs-2026-08-28` | `outputs/image-b-gs-2026-08-28/verifier/g384_ov192_image_high/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 9189 |
| `n1-outstanding-384` | `outputs/h11/n1-outstanding-384/image-t0/verified-v1-n3/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 690 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/flash-high-image-1of5/candidate_manifest.json` | `flash-high-image-1of5.geojson` | 1 | 2017 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/flash-high-text-1of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 1 | 5866 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/flash-high-text-1of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 1 | 11771 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/flash-high-text-1of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 1 | 3736 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/flash-high-text-t03-1of5/candidate_manifest.json` | `flash-high-text-t03-1of5.geojson` | 1 | 2954 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/flash-minimal-text-t07-1of5/candidate_manifest.json` | `flash-minimal-text-t07-1of5.geojson` | 1 | 1593 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/image-1of10/candidate_manifest.json` | `image-1of10.geojson` | 1 | 1444 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/image-1of5/candidate_manifest.json` | `image-1of5.geojson` | 1 | 1123 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/image-2of5/candidate_manifest.json` | `image-2of5.geojson` | 2 | 754 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/image-3of5/candidate_manifest.json` | `image-3of5.geojson` | 3 | 617 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/image-4of5/candidate_manifest.json` | `image-4of5.geojson` | 4 | 523 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/image-5of5/candidate_manifest.json` | `image-5of5.geojson` | 5 | 427 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/pro-high-image-1of5/candidate_manifest.json` | `pro-high-image-1of5.geojson` | 1 | 841 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/pro-high-text-1of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 1 | 504 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-10of10/candidate_manifest.json` | `text-10of10.geojson` | 10 | 616 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-1of10/candidate_manifest.json` | `text-1of10.geojson` | 1 | 1939 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-1of5/candidate_manifest.json` | `text-1of5.geojson` | 1 | 974 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-2of10/candidate_manifest.json` | `text-2of10.geojson` | 2 | 1350 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-2of5/candidate_manifest.json` | `text-2of5.geojson` | 2 | 616 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-3of10/candidate_manifest.json` | `text-3of10.geojson` | 3 | 1177 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-3of5/candidate_manifest.json` | `text-3of5.geojson` | 3 | 484 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-4of10/candidate_manifest.json` | `text-4of10.geojson` | 4 | 1075 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-4of5/candidate_manifest.json` | `text-4of5.geojson` | 4 | 395 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-5of10/candidate_manifest.json` | `text-5of10.geojson` | 5 | 999 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-5of5/candidate_manifest.json` | `text-5of5.geojson` | 5 | 295 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-6of10/candidate_manifest.json` | `text-6of10.geojson` | 6 | 929 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-7of10/candidate_manifest.json` | `text-7of10.geojson` | 7 | 851 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-8of10/candidate_manifest.json` | `text-8of10.geojson` | 8 | 771 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-9of10/candidate_manifest.json` | `text-9of10.geojson` | 9 | 708 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/crops/text-min-t07-true-1of5/candidate_manifest.json` | `text-min-t07-true-1of5.geojson` | 1 | 1586 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 802 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n10/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 3412 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 2190 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/shared-crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 2017 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n10/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 3211 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 2017 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n10/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 4638 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 2840 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/shared-crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 3736 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/image-n5/image-t0.3/verified-v1-n10/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 1114 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/image-n5/image-t0.3/verified-v1-n5/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 987 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/image-n5/image-t0.7/verified-v1-n10/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 1450 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/image-n5/image-t0.7/verified-v1-n5/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 1123 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/image-n5/image-t1.0/verified-v1-n10/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 1975 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/image-n5/image-t1.0/verified-v1-n5/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 1443 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 3601 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n5/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 2198 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-image-1of5/candidate_manifest.json` | `flash-high-image-1of5.geojson` | 1 | 2017 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-image-2of5/candidate_manifest.json` | `flash-high-image-1of5.geojson` | 2 | 741 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-image-3of5/candidate_manifest.json` | `flash-high-image-1of5.geojson` | 3 | 506 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-image-4of5/candidate_manifest.json` | `flash-high-image-1of5.geojson` | 4 | 388 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-image-5of5/candidate_manifest.json` | `flash-high-image-1of5.geojson` | 5 | 282 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-10of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 10 | 345 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-10of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 10 | 1161 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-11of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 11 | 1070 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-12of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 12 | 975 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-13of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 13 | 907 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-14of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 14 | 850 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-15of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 15 | 789 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-16of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 16 | 729 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-17of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 17 | 682 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-18of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 18 | 637 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-19of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 19 | 607 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-1of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 1 | 5866 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-1of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 1 | 11771 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-1of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 1 | 3736 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-20of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 20 | 571 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-21of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 21 | 536 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-22of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 22 | 510 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-23of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 23 | 491 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-24of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 24 | 469 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-25of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 25 | 441 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-26of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 26 | 415 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-27of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 27 | 390 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-28of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 28 | 361 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-29of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 29 | 327 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-2of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 2 | 2215 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-2of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 2 | 4543 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-2of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 2 | 1376 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-30of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 30 | 256 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-3of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 3 | 1493 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-3of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 3 | 3072 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-3of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 3 | 855 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-4of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 4 | 1104 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-4of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 4 | 2363 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-4of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 4 | 584 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-5of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 5 | 879 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-5of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 5 | 1991 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-5of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 5 | 415 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-6of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 6 | 727 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-6of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 6 | 1713 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-7of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 7 | 590 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-7of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 7 | 1536 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-8of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 8 | 511 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-8of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 8 | 1387 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-9of10/candidate_manifest.json` | `flash-high-text-1of10.geojson` | 9 | 431 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-9of30/candidate_manifest.json` | `flash-high-text-1of30.geojson` | 9 | 1271 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-1of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 1 | 3736 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-2of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 2 | 1376 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-3of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 3 | 855 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-4of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 4 | 584 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-5of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 5 | 415 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-1of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 1 | 3736 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-2of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 2 | 1376 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-3of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 3 | 855 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-4of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 4 | 584 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-5of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 5 | 415 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-1of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 1 | 3736 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-2of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 2 | 1376 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-3of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 3 | 855 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-4of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 4 | 584 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-5of5/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 5 | 415 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-1of5/candidate_manifest.json` | `flash-minimal-text-t07-1of5.geojson` | 1 | 1593 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-2of5/candidate_manifest.json` | `flash-minimal-text-t07-1of5.geojson` | 2 | 1104 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-3of5/candidate_manifest.json` | `flash-minimal-text-t07-1of5.geojson` | 3 | 950 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-4of5/candidate_manifest.json` | `flash-minimal-text-t07-1of5.geojson` | 4 | 807 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-5of5/candidate_manifest.json` | `flash-minimal-text-t07-1of5.geojson` | 5 | 653 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/image-10of10/candidate_manifest.json` | `image-1of10.geojson` | 10 | 361 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/image-1of10/candidate_manifest.json` | `image-1of10.geojson` | 1 | 1444 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/image-2of10/candidate_manifest.json` | `image-1of10.geojson` | 2 | 954 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/image-3of10/candidate_manifest.json` | `image-1of10.geojson` | 3 | 777 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/image-4of10/candidate_manifest.json` | `image-1of10.geojson` | 4 | 698 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/image-5of10/candidate_manifest.json` | `image-1of10.geojson` | 5 | 627 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/image-6of10/candidate_manifest.json` | `image-1of10.geojson` | 6 | 577 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/image-7of10/candidate_manifest.json` | `image-1of10.geojson` | 7 | 536 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/image-8of10/candidate_manifest.json` | `image-1of10.geojson` | 8 | 493 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/image-9of10/candidate_manifest.json` | `image-1of10.geojson` | 9 | 442 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-1of5/candidate_manifest.json` | `pro-high-image-1of5.geojson` | 1 | 841 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-2of5/candidate_manifest.json` | `pro-high-image-1of5.geojson` | 2 | 583 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-3of5/candidate_manifest.json` | `pro-high-image-1of5.geojson` | 3 | 471 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-4of5/candidate_manifest.json` | `pro-high-image-1of5.geojson` | 4 | 391 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-5of5/candidate_manifest.json` | `pro-high-image-1of5.geojson` | 5 | 297 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-1of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 1 | 504 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-2of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 2 | 409 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-3of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 3 | 367 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-4of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 4 | 337 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-5of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 5 | 306 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-1of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 1 | 504 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-2of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 2 | 409 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-3of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 3 | 367 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-4of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 4 | 337 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-5of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 5 | 306 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-1of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 1 | 504 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-2of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 2 | 409 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-3of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 3 | 367 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-4of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 4 | 337 |
| `pv-diag-384` | `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-5of5/candidate_manifest.json` | `pro-high-text-1of5.geojson` | 5 | 306 |
| `stride-55map-2026-08-25` | `outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 38713 |
| `stride-55map-2026-08-25` | `outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 57482 |
| `stride-phaseb-2026-08-25` | `outputs/stride-phaseb-2026-08-25/verifier/g256_ov064/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 3570 |
| `stride-phaseb-2026-08-25` | `outputs/stride-phaseb-2026-08-25/verifier/g384_ov128/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 2387 |
| `stride-phaseb-2026-08-25` | `outputs/stride-phaseb-2026-08-25/verifier/g384_ov128/crops_k1/candidate_manifest.json` | `union_k1.geojson` | 1 | 1290 |
| `stride-phaseb-2026-08-25` | `outputs/stride-phaseb-2026-08-25/verifier/g384_ov128/crops_k3/candidate_manifest.json` | `union_k3.geojson` | 1 | 1700 |
| `stride-phaseb-2026-08-25` | `outputs/stride-phaseb-2026-08-25/verifier/g384_ov128/crops_k5/candidate_manifest.json` | `union_k5.geojson` | 1 | 1968 |
| `stride-phaseb-2026-08-25` | `outputs/stride-phaseb-2026-08-25/verifier/g512_ov176/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 1981 |
| `stride-phaseb-2026-08-25` | `outputs/stride-phaseb-2026-08-25/verifier/g512_ov320/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 3778 |
| `stride-phasec-2026-08-25` | `outputs/stride-phasec-2026-08-25/verifier/g384_ov240/crops/candidate_manifest.json` | `union_k10.geojson` | 1 | 5250 |
| `verifier-robustness` | `outputs/verifier-robustness/256-text-1of5-union/crops/candidate_manifest.json` | `text-1of5.geojson` | 1 | 2558 |
| `verifier-robustness` | `outputs/verifier-robustness/256-text-ge3of5/crops/candidate_manifest.json` | `text-ge3of5.geojson` | 3 | 1645 |
| `verifier-robustness` | `outputs/verifier-robustness/384-flash-high-text-16of30/crops/candidate_manifest.json` | `flash-high-text-16of30.geojson` | 16 | 729 |
| `verifier-robustness` | `outputs/verifier-robustness/384-flash-high-text-1of5-union/crops/candidate_manifest.json` | `flash-high-text-1of5.geojson` | 1 | 3736 |
| `verifier-robustness` | `outputs/verifier-robustness/384-flash-high-text-ge3of5/crops/candidate_manifest.json` | `flash-high-text-ge3of5.geojson` | 3 | 855 |

**9 candidate manifest(s) were excluded from the
measurement.** A silently dropped manifest can RAISE a measured floor
and flip a verdict, so every exclusion is listed with its ground:

| Manifest | Ground |
|---|---|
| `outputs/h11/e47-propose-brief/crops/text-baseline/candidate_manifest.json` | no integer vote count under any of vote_count, proposer_votes; 1180 candidate(s) carry properties ['confidence', 'label', 'method', 'model', 'source_tile', 'subtype'] |
| `outputs/h11/pv-diag-384/crops/image-baseline/candidate_manifest.json` | no integer vote count under any of vote_count, proposer_votes; 746 candidate(s) carry properties ['confidence', 'label', 'method', 'model', 'source_tile', 'subtype'] |
| `outputs/h11/pv-diag-384/crops/pro-medium-image-baseline/candidate_manifest.json` | no integer vote count under any of vote_count, proposer_votes; 519 candidate(s) carry properties ['confidence', 'label', 'method', 'model', 'source_tile', 'subtype'] |
| `outputs/h11/pv-diag-384/crops/pro-medium-text-baseline/candidate_manifest.json` | no integer vote count under any of vote_count, proposer_votes; 430 candidate(s) carry properties ['confidence', 'label', 'method', 'model', 'source_tile', 'subtype'] |
| `outputs/h11/pv-diag-384/crops/text-baseline/candidate_manifest.json` | no integer vote count under any of vote_count, proposer_votes; 1047 candidate(s) carry properties ['confidence', 'label', 'method', 'model', 'source_tile', 'subtype'] |
| `outputs/verifier-robustness/_smoke/256-text-1of5-union/crops/candidate_manifest.json` | smoke-test tree (path segment '_smoke'), excluded by design |
| `outputs/verifier-robustness/_smoke/256-text-ge3of5/crops/candidate_manifest.json` | smoke-test tree (path segment '_smoke'), excluded by design |
| `outputs/verifier-robustness/_smoke/384-flash-high-text-1of5-union/crops/candidate_manifest.json` | smoke-test tree (path segment '_smoke'), excluded by design |
| `outputs/verifier-robustness/_smoke/384-flash-high-text-ge3of5/crops/candidate_manifest.json` | smoke-test tree (path segment '_smoke'), excluded by design |

**50 verified cell(s) have no derivable
with-verifier N = 1 anchor.** They are disclosed, not approximated: no
substitute is computed, and the supplement's verified-cell uplift column
is left empty rather than filled with a number the corpus cannot
support. Their no-verifier N = 1 jobs still run, and carry the
consensus-uplift signal for those pools.

A floor of 1 means that stage processed the full vote >= 1 union, so a
K = 1 WITH-verifier cell IS derivable from it — the modern stride, grid,
and image campaigns, whose ladder rungs are in several cases already
registered.

**Refinement on the card.** The card records the block as a
"vote >= 3 shells" phenomenon. Measured per stage, the floors are not
uniform:

| Measured floor | Verifier stages |
|---:|---:|
| vote_count >= 1 | 73 |
| vote_count >= 2 | 17 |
| vote_count >= 3 | 21 |
| vote_count >= 4 | 22 |
| vote_count >= 5 | 17 |
| vote_count >= 6 | 4 |
| vote_count >= 7 | 4 |
| vote_count >= 8 | 4 |
| vote_count >= 9 | 4 |
| vote_count >= 10 | 4 |
| vote_count >= 11 | 1 |
| vote_count >= 12 | 1 |
| vote_count >= 13 | 1 |
| vote_count >= 14 | 1 |
| vote_count >= 15 | 1 |
| vote_count >= 16 | 2 |
| vote_count >= 17 | 1 |
| vote_count >= 18 | 1 |
| vote_count >= 19 | 1 |
| vote_count >= 20 | 1 |
| vote_count >= 21 | 1 |
| vote_count >= 22 | 1 |
| vote_count >= 23 | 1 |
| vote_count >= 24 | 1 |
| vote_count >= 25 | 1 |
| vote_count >= 26 | 1 |
| vote_count >= 27 | 1 |
| vote_count >= 28 | 1 |
| vote_count >= 29 | 1 |
| vote_count >= 30 | 1 |

The per-stage numbers in the table above are the ones to quote; a single
corpus-wide threshold would be wrong for some stages in both directions.

## A judgement call: K-pass union floors cited for lower rungs

Eight stride-55map ladder rungs at N = 3 and N = 5 have no verifier
stage of their own: the campaign cropped the vote >= 1 union of all ten
passes once, and the lower rungs were derived from those probabilities.
Their `verifier_floor_basis` therefore ends `-via-union_k10-superset`.

The inference this licenses, stated so a reader can reject it: every
candidate in the first-N union also appears in the K-pass union, since
appearing in at least one of N passes implies appearing in at least one
of K >= N. The K-pass crop set is therefore a SUPERSET of the rung's, so
a floor of 1 there means the verifier did see every candidate the rung
could contain. What it does NOT give is a vote count expressed out of N:
the recorded counts are out of K, and no rung-level shell was measured.
The rows carry the basis string so this can be filtered out of any
analysis that wants only directly measured stages.

## How a ready job is scored

Each ready job reproduces its parent cell's own recipe, recovered from
the parent's committed evaluation artefact (`_metadata.cli_args`, or the
engine summary an adapter names), with only the detections path, output
directory, and label swapped. Scoring the anchor a different way would
make the uplift a measurement of the scorer.

The invocations are in `k1-gapfill-commands.sh`. They are
bootstrap-heavy; run them on sapphire.

## Changelog

### 2026-08-29 — Original publication

Generated with the first build of the K = 1 gap-fill worklist.
