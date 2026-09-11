# With/without-verifier pairing — worklist

> **Last revised**: 2026-09-11 (regenerated from committed artefacts by `scripts/build_verifier_pairing_worklist.py`; original publication; the with/without-verifier pairing plan). See [§ Changelog](#changelog) for revision history.
>
> **First published**: 2026-08-29. Regenerated 2026-09-11T06:52:41Z. This document is generated in full from committed artefacts, so its body always reflects the current corpus; git carries the content history.
>
> **GENERATED — do not hand-edit.** Every number, table and count below
> is computed by the generator named above from the committed corpus;
> edit the generator, not this file. Source commit (the checkout this
> build read): `2ae61feea`.

Build order step 3 of `planning/uplift-supplement-2026-08-28.md`. This
document and `verifier-pairing-worklist.csv` are the PLAN; the scores
they call for are produced by `verifier-pairing-commands.sh` and joined
into the uplift column by `scripts/compute_verifier_uplift.py`. What
has actually been computed at any moment is in `verifier-uplift.csv`,
not here.

Verifier uplift is the difference a verifier makes holding everything
else fixed. Each row pairs one verified cell with the consensus set that
went INTO its verifier at the same vote threshold — same passes, same
reference, same buffer, same frame.

The two sides carry SEPARATE stratum ids (`verified_stratum_id` and
`unverified_stratum_id`), and `scripts/compute_verifier_uplift.py`
passes both to the cross-stratum guard.

**What that guard is and is not.** A `stratum_id` is
corpus × reference × buffer × frame. Pool, geometry, and fusion family
are NOT in it — they are in the pairing key, which already forces the
two sides to agree on all four stratum components before a pair is
emitted. The guard is therefore a consistency TRIPWIRE: it catches an
externally edited worklist, or a future change that lets the key and the
stratum drift apart. It cannot catch a cross-LINEAGE mispair, because
two cells of the same run at different geometries share a stratum. What
protects against that is the lineage matching in this builder, not the
guard downstream.

172 verified cell(s) in the registry.

79 board-frame row(s) excluded by rule (PI, 2026-09-10): rows whose
`scope_override.test_set_id` names a leaderboard scoring frame are board
artefacts (the GS Era-2 board's `-era2b` and `-opmax` rows), not
measurements of their own, and are neither paired nor offered as twins
(`lib_uplift_supplement.is_board_frame_condition`).

## Status

| Status | Cells |
|---|---:|
| `already-registered` | 14 |
| `blocked` | 27 |
| `ready` | 27 |
| `ready-after-materialise` | 104 |

`already-registered` pairs need nothing: the twin is scored. `ready`
pairs have a committed consensus GeoJSON and one scoring invocation.
`ready-after-materialise` pairs need the vote shell filtered out of the
recorded candidate universe first — a committed union, the crop manifest
of the cell's own verifier stage, or a base manifest joined with the
committed increment that completes it. That is a local geometry filter:
no API spend and no re-aggregation, and the row records the exact
predicate in `materialise_filter`.

## How the twin was located

| `pairing_basis` | Cells |
|---|---:|
| `consensus-file` | 21 |
| `crop-manifest` | 14 |
| `registered` | 14 |
| `shell-manifests` | 13 |
| `single-pass-manifest` | 21 |
| `source-run-consensus` | 6 |
| `stage-manifest` | 13 |
| `union` | 43 |
| `unresolved` | 27 |

## Blocked pairs

27 verified cell(s) have no locatable pre-verifier twin.
They are recorded with the reason and left empty in the uplift column;
no substitute set is constructed.

| Verified cell | Reason |
|---|---|
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 1; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the run records no crop manifest for this pool (tried crops/g384_ov128_55map/candidate_manifest.json, verified/g384_ov128_55map/candidate_manifest.json), and the run-level fallback needs a single-lineage run (this run registers 2 lineage(s)) |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=3, k=2): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 2 |
| `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 5; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 5, k = 4 |
| `stride-55map-2026-08-25::g384-ov128-55map-n5-carried-p0.15-k4-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 5; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 5, k = 4 |
| `stride-55map-2026-08-25::g384-ov192-55map-n1-oracle-p0.20-k1-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 1; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the run records no crop manifest for this pool (tried crops/g384_ov192_55map/candidate_manifest.json, verified/g384_ov192_55map/candidate_manifest.json), and the run-level fallback needs a single-lineage run (this run registers 2 lineage(s)) |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-oracle-p0.20-k3-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 3 |
| `stride-55map-2026-08-25::g384-ov192-55map-n5-oracle-p0.20-k5-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=5, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 5; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 5, k = 5 |
| `stride-55map-2026-08-25::g384-ov192-55map-n5-carried-p0.15-k5-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=5, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 5; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 5, k = 5 |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-carried-posthoc-p0.15-k3-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 3 |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-carried-posthoc-p0.15-k3-standardised-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 3 |
| `stride-55map-2026-08-25::g384-ov128-55map-n1-oracle-p0.20-k1-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 1; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the run records no crop manifest for this pool (tried crops/g384_ov128_55map/candidate_manifest.json, verified/g384_ov128_55map/candidate_manifest.json), and the run-level fallback needs a single-lineage run (this run registers 2 lineage(s)) |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-oracle-p0.20-k2-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=3, k=2): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 2 |
| `stride-55map-2026-08-25::g384-ov128-55map-n5-oracle-p0.15-k4-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 5; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 5, k = 4 |
| `stride-55map-2026-08-25::g384-ov128-55map-n5-carried-p0.15-k4-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=5, k=4): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 5; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 5, k = 4 |
| `stride-55map-2026-08-25::g384-ov192-55map-n1-oracle-p0.20-k1-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 1; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the run records no crop manifest for this pool (tried crops/g384_ov192_55map/candidate_manifest.json, verified/g384_ov192_55map/candidate_manifest.json), and the run-level fallback needs a single-lineage run (this run registers 2 lineage(s)) |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-oracle-p0.20-k3-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 3 |
| `stride-55map-2026-08-25::g384-ov192-55map-n5-oracle-p0.20-k5-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=5, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 5; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 5, k = 5 |
| `stride-55map-2026-08-25::g384-ov192-55map-n5-carried-p0.15-k5-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=5, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 5; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 5, k = 5 |
| `stride-55map-2026-08-25::g384-ov192-55map-n1-verified37-oracle-p0.96-k1-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 1; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the run records no crop manifest for this pool (tried crops/g384_ov192_55map/candidate_manifest.json, verified/g384_ov192_55map/candidate_manifest.json), and the run-level fallback needs a single-lineage run (this run registers 2 lineage(s)) |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-verified37-oracle-p0.96-k3-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 3 |
| `stride-55map-2026-08-25::g384-ov128-55map-n3-carried-posthoc-p0.15-k3-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov128_55map', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 3 |
| `stride-55map-2026-08-25::g384-ov192-55map-n3-carried-posthoc-p0.15-k3-r2-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 3 |
| `stride-55map-2026-08-25::g384-ov192-55map-n5-carried-p0.15-k5-canonical-gt` | no committed pre-verifier set was found for (run=stride-55map-2026-08-25, pool='g384_ov192_55map', N=5, k=5): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/crops/candidate_manifest.json counts votes over 10 pass(es) but the cell consumed N = 5; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/stride-55map-2026-08-25/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 5, k = 5 |
| `gemini37-55map-2026-08-29::arm1-n1-oracle-p0.20-k1-r2-gt` | no committed pre-verifier set was found for (run=gemini37-55map-2026-08-29, pool='g384_ov192_55map_g37', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/crops/candidate_manifest.json counts votes over 5 pass(es) but the cell consumed N = 1; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/gemini37-55map-2026-08-29/crops/candidate_manifest.json; single-pass: the run records no crop manifest for this pool (tried crops/g384_ov192_55map_g37/candidate_manifest.json, verified/g384_ov192_55map_g37/candidate_manifest.json), and the run-level fallback needs a single-lineage run (this run registers 1 lineage(s)) |
| `gemini37-55map-2026-08-29::arm1-n3-oracle-p0.15-k3-r2-gt` | no committed pre-verifier set was found for (run=gemini37-55map-2026-08-29, pool='g384_ov192_55map_g37', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/crops/candidate_manifest.json counts votes over 5 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/gemini37-55map-2026-08-29/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 3 |
| `gemini37-55map-2026-08-29::arm2-n1-oracle-p0.98-k1-r2-gt` | no committed pre-verifier set was found for (run=gemini37-55map-2026-08-29, pool='g384_ov192_55map_g37', N=1, k=1): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/crops/candidate_manifest.json counts votes over 5 pass(es) but the cell consumed N = 1; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/gemini37-55map-2026-08-29/crops/candidate_manifest.json; single-pass: the run records no crop manifest for this pool (tried crops/g384_ov192_55map_g37/candidate_manifest.json, verified/g384_ov192_55map_g37/candidate_manifest.json), and the run-level fallback needs a single-lineage run (this run registers 1 lineage(s)) |
| `gemini37-55map-2026-08-29::arm2-n3-oracle-p0.95-k3-r2-gt` | no committed pre-verifier set was found for (run=gemini37-55map-2026-08-29, pool='g384_ov192_55map_g37', N=3, k=3): the registry holds no consensus sibling, no consensus GeoJSON names that threshold under the pool or run tree, and the run holds no vote >= 1 union over N passes — and stage-manifest: outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/crops/candidate_manifest.json counts votes over 5 pass(es) but the cell consumed N = 3; they are different rungs of the pass ladder, so its shell at k is a different universe; shell-manifests: the run records no base crop manifest at outputs/gemini37-55map-2026-08-29/crops/candidate_manifest.json; single-pass: the vacuous-shell rule needs N = 1 and k = 1; this cell is N = 3, k = 3 |

## Producing the uplift column

Once the twins have scores, `scripts/compute_verifier_uplift.py` joins
them and writes `verifier-uplift.csv`. It refuses any pair whose two
cells do not share a `stratum_id`, so a mis-paired row fails loudly
rather than producing a plausible number.

### How many pairs can be computed

A pair is computable when BOTH sides have a score. The ceiling below is
counted from THIS build's statuses and from the jobs this build
actually emitted — a row counts as computable only if it carries a
`command`, whether or not it also needs a `materialise_command` first.
An earlier version of this section hard-coded a 2026-08-29 model of the
pipeline in which materialise-then-score jobs did not yet exist, and
went on reporting `ready-after-materialise` as uncomputable long after
the materialiser was emitting them.

| Status | Pairs | Computable | Why |
|---|---:|---:|---|
| `already-registered` | 14 | 14 | Both sides are registered conditions, so both are already in `conditions.csv`. No scoring needed. |
| `ready` | 27 | 27 | The twin is a committed GeoJSON; one emitted job scores it. |
| `ready-after-materialise` | 104 | 104 | Two emitted commands: the materialiser filters the vote shell out of the recorded universe, then the score runs on the twin. No API spend and no re-aggregation. |
| `blocked` | 27 | 0 | No twin located. |

So the ceiling after a clean run of `verifier-pairing-commands.sh` is **145 computed, 27 pending** — 14 pair(s) needing no scoring at all and 131 emitted job(s).

Two defects of the 2026-08-29 batch, both since fixed, are why that
run produced 8 rather than its ceiling — kept here because both are
failure modes a future batch can repeat:

1. **The script aborted at the first failure.** `set -e` stopped the
   batch at the third command, so twelve jobs that would have succeeded
   never ran. The preamble no longer sets it, and failures are
   collected and reported at the end.
2. **Corrected-F1 scores were unreadable anyway.** Those jobs use
   `compute_corrected_f1_multi_buffer.py`, which writes `summary.json`;
   the uplift computer only looked for `evaluation.json`, so even a
   fully successful batch would have left every corrected-F1 pair at
   `pending` with nothing to say why. It now reads both shapes.

## Changelog

### 2026-08-29 — Original publication

Generated with the first build of the verifier-pairing worklist.
