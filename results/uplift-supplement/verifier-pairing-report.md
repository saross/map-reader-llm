# With/without-verifier pairing — worklist

> **Last revised**: 2026-08-29 (original publication; the with/without-verifier pairing plan). See [§ Changelog](#changelog) for revision history.
>
> **Regenerated**: 2026-08-29T03:49:56Z by `scripts/build_verifier_pairing_worklist.py`. This document is generated in full from committed artefacts; regeneration is not a revision, and git carries the content history.

Build order step 3 of `planning/uplift-supplement-2026-08-28.md`. No
scoring has been run: this document and its worklist are the plan.

Verifier uplift is the difference a verifier makes holding everything
else fixed. Each row pairs one verified cell with the consensus set that
went INTO its verifier at the same vote threshold — same passes, same
reference, same buffer, same frame.

The two sides carry SEPARATE stratum ids (`verified_stratum_id` and
`unverified_stratum_id`). For a derived twin they agree by construction,
because the twin is scored with the verified cell's own recipe; for a
registered twin the id is derived from that cell's own evidence, so a
mismatch is detectable. `scripts/compute_verifier_uplift.py` passes both
to the cross-stratum guard, which is what makes the guard a check rather
than a formality.

118 verified cell(s) in the registry.

## Status

| Status | Cells |
|---|---:|
| `already-registered` | 6 |
| `blocked` | 79 |
| `ready` | 13 |
| `ready-after-materialise` | 20 |

`already-registered` pairs need nothing: the twin is scored. `ready`
pairs have a committed consensus GeoJSON and one scoring invocation.
`ready-after-materialise` pairs need the vote shell filtered out of the
committed union first — a local geometry filter, no API spend and no
re-aggregation — and the row records the exact predicate in
`materialise_filter`.

## How the twin was located

| `pairing_basis` | Cells |
|---|---:|
| `consensus-file` | 13 |
| `registered` | 6 |
| `union` | 20 |
| `unresolved` | 79 |

## Blocked pairs

79 verified cell(s) have no locatable pre-verifier twin.
They are recorded with the reason and left empty in the uplift column;
no substitute set is constructed.

| Verified cell | Reason |
|---|---|
| `55maps-image-generalisation::verified-k4-standardised-gt` | no committed pre-verifier set was found for (run=55maps-image-generalisation, pool='library_plus-hp', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `55maps-text-high-generalisation::verified-k3-canonical-gt` | no committed pre-verifier set was found for (run=55maps-text-high-generalisation, pool='detect_brief-text', N=5, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `55maps-text-high-generalisation::verified-k3-standardised-gt` | no committed pre-verifier set was found for (run=55maps-text-high-generalisation, pool='detect_brief-text', N=5, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `55maps-text-high-t0-3-generalisation::verified-k3-canonical-gt` | no committed pre-verifier set was found for (run=55maps-text-high-t0-3-generalisation, pool='detect_brief-text', N=5, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `55maps-text-high-t0-3-generalisation::verified-k3-standardised-gt` | no committed pre-verifier set was found for (run=55maps-text-high-t0-3-generalisation, pool='detect_brief-text', N=5, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `55maps-text-high-t0-3-generalisation::verified-oracle-p0.20-k3-standardised-gt` | no committed pre-verifier set was found for (run=55maps-text-high-t0-3-generalisation, pool='detect_brief-text', N=5, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `55maps-text-min-generalisation::verified-k3-canonical-gt` | no committed pre-verifier set was found for (run=55maps-text-min-generalisation, pool='detect_brief-text', N=5, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `55maps-text-min-generalisation::verified-k3-standardised-gt` | no committed pre-verifier set was found for (run=55maps-text-min-generalisation, pool='detect_brief-text', N=5, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `55maps-text-min-generalisation::verified-oracle-p0.20-k3-standardised-gt` | no committed pre-verifier set was found for (run=55maps-text-min-generalisation, pool='detect_brief-text', N=5, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `proposer-verifier-384::verified-adversarial-text` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `proposer-verifier-384::verified-adversarial-image` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `proposer-verifier-384::verified-brief-text` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `proposer-verifier-384::verified-brief-image` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `proposer-verifier-384::verified-checklist-text` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `proposer-verifier-384::verified-checklist-image` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `proposer-verifier-384::verified-cascade-adversarial-checklist` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `proposer-verifier-384::verified-cascade-checklist-adversarial` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `proposer-verifier-512::verified-adversarial-text` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `pv-diag-256::verified-adv-text-consensus-5of5` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `pv-diag-384::verified-adv-text-consensus-16of30` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `pv-diag-384::verified-adv-text-4of5` | 2 committed 4-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (flash-high-text-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-text-6of10` | 1 committed 6-of-10 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (flash-high-text-1of10). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-text-high-vf-4of5` | 2 committed 4-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (flash-high-text-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-text-medium-vf-4of5` | 2 committed 4-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (flash-high-text-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-pro-text-flash-vf-3of5` | 2 committed 3-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (pro-high-text-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-pro-text-pro-vf-3of5` | 2 committed 3-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (pro-high-text-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-text-min-true-3of5` | 2 committed 3-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (text-min-t07-true-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-text-min-n30lineage-4of5` | 2 committed 4-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (flash-minimal-text-t07-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-text-min-6of10` | 1 committed 6-of-10 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (text-1of10). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-text-t03-4of5` | 2 committed 4-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (flash-high-text-t03-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-image-3of5` | 2 committed 3-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (flash-high-image-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-text-pro-vf-4of5` | 2 committed 4-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (flash-high-text-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-image-min-3of5` | 2 committed 3-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (image-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-image-min-6of10` | 1 committed 6-of-10 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (image-1of10). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-image-baseline` | no committed pre-verifier set was found for (run=pv-diag-384, pool='image-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-image-baseline-medium-vf` | no committed pre-verifier set was found for (run=pv-diag-384, pool='image-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-image-baseline-pro-vf` | no committed pre-verifier set was found for (run=pv-diag-384, pool='image-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-text-baseline` | no committed pre-verifier set was found for (run=pv-diag-384, pool='text-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-text-baseline-medium-vf` | no committed pre-verifier set was found for (run=pv-diag-384, pool='text-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-text-baseline-pro-vf` | no committed pre-verifier set was found for (run=pv-diag-384, pool='text-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-pro-text-medium-vf-3of5` | 2 committed 3-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (pro-high-text-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-pro-image-pro-vf-3of5` | 2 committed 3-of-5 consensus set(s) sit under the run tree, which serves 41 distinct pool/geometry lineages, and none carries this cell's tokens (pro-high-image-1of5). None can be shown to be the set its verifier consumed; refused rather than guessed |
| `pv-diag-384::verified-adv-pro-text-baseline` | no committed pre-verifier set was found for (run=pv-diag-384, pool='pro-medium-text-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-pro-text-baseline-medium-vf` | no committed pre-verifier set was found for (run=pv-diag-384, pool='pro-medium-text-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-pro-text-baseline-pro-vf` | no committed pre-verifier set was found for (run=pv-diag-384, pool='pro-medium-text-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-pro-image-baseline` | no committed pre-verifier set was found for (run=pv-diag-384, pool='pro-medium-image-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-pro-image-baseline-medium-vf` | no committed pre-verifier set was found for (run=pv-diag-384, pool='pro-medium-image-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `pv-diag-384::verified-adv-pro-image-baseline-pro-vf` | no committed pre-verifier set was found for (run=pv-diag-384, pool='pro-medium-image-baseline', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `retest-phase2b::verified-adv-text-t0.0` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `retest-phase2b::verified-adv-image-t0.0` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `retest-phase3a::verified-adv-image-t0.7-n30-18of30` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `retest-phase3a-high::verified-adv-text-high-t1.0-n30-23of30` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `verifier-t-pilot::verified-t0-0` | no committed pre-verifier set was found for (run=verifier-t-pilot, pool='detect_brief-text', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `verifier-t-pilot::verified-t0-5` | no committed pre-verifier set was found for (run=verifier-t-pilot, pool='detect_brief-text', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `verifier-t-pilot::verified-t1-0` | no committed pre-verifier set was found for (run=verifier-t-pilot, pool='detect_brief-text', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `verifier-robustness::verified-384-union-t0-0-n5` | no committed pre-verifier set was found for (run=verifier-robustness, pool='flash-high-text-1of5', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `verifier-robustness::verified-256-union-t0-0-n5` | no committed pre-verifier set was found for (run=verifier-robustness, pool='text-1of5', N=5, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `verifier-robustness::verified-256-ge3of5-t0-3-n5` | no committed pre-verifier set was found for (run=verifier-robustness, pool='text-1of5', N=5, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `verifier-robustness::verified-384-ge3of5-t0-3-n5` | no committed pre-verifier set was found for (run=verifier-robustness, pool='flash-high-text-1of5', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `verifier-robustness::verified-384-ge3of5-t0-7-n5` | no committed pre-verifier set was found for (run=verifier-robustness, pool='flash-high-text-1of5', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `verifier-robustness::verified-384-ge3of5-t0-3-high-n5` | no committed pre-verifier set was found for (run=verifier-robustness, pool='flash-high-text-1of5', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `verifier-robustness::verified-384-ge3of5-t0-7-high-n5` | no committed pre-verifier set was found for (run=verifier-robustness, pool='flash-high-text-1of5', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `verifier-robustness::verified-384-16of30-t0-3-n5-opmax` | the verified cell records no vote threshold, so there is no 'same vote threshold' pre-verifier set to pair it with |
| `flash35-pv-2x2::f35prop-f3vf-4of10` | no committed pre-verifier set was found for (run=flash35-pv-2x2, pool='flash35-min-text-1of10', N=10, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `flash35-pv-2x2::f35prop-f35vf-4of10` | no committed pre-verifier set was found for (run=flash35-pv-2x2, pool='flash35-min-text-1of10', N=10, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `flash35-pv-2x2::f3prop-f35vf-6of10` | no committed pre-verifier set was found for (run=flash35-pv-2x2, pool='f3-min-text-1of10', N=10, k=6): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `55maps-text-min-n10-uplift::verified-5of10-canonical-gt` | no committed pre-verifier set was found for (run=55maps-text-min-n10-uplift, pool='detect_brief-text-min-n10', N=10, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `55maps-text-min-n10-uplift::verified-5of10-standardised-gt` | no committed pre-verifier set was found for (run=55maps-text-min-n10-uplift, pool='detect_brief-text-min-n10', N=10, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=3, k=2): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `stride-55map-2026-08-25::g384-ov128-55map-n5-carried-p0.15-k4-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `stride-55map-2026-08-25::g384-ov192-55map-n1-oracle-p0.20-k1-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-oracle-p0.20-k3-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `stride-55map-2026-08-25::g384-ov192-55map-n5-oracle-p0.20-k5-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=5, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `stride-55map-2026-08-25::g384-ov192-55map-n5-carried-p0.15-k5-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=5, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-carried-posthoc-p0.15-k3-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-carried-posthoc-p0.15-k3-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |
| `image-b-gs-2026-08-28::g384-ov192-image-min-k10-verified-p0.15-k9` | no committed pre-verifier set was found for (run=image-b-gs-2026-08-28, pool='g384_ov192_image', N=10, k=9): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes |

## Producing the uplift column

Once the twins have scores, `scripts/compute_verifier_uplift.py` joins
them and writes `verifier-uplift.csv`. It refuses any pair whose two
cells do not share a `stratum_id`, so a mis-paired row fails loudly
rather than producing a plausible number.

## Changelog

### 2026-08-29 — Original publication

Generated with the first build of the verifier-pairing worklist.
