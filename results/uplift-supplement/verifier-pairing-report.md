# With/without-verifier pairing — worklist

> **Last revised**: 2026-09-12 (regenerated from committed artefacts by `scripts/build_verifier_pairing_worklist.py`; original publication; the with/without-verifier pairing plan). See [§ Changelog](#changelog) for revision history.
>
> **First published**: 2026-08-29. Regenerated 2026-09-12T08:57:13Z. This document is generated in full from committed artefacts, so its body always reflects the current corpus; git carries the content history.
>
> **GENERATED — do not hand-edit.** Every number, table and count below
> is computed by the generator named above from the committed corpus;
> edit the generator, not this file. Source commit (the checkout this
> build read): `326181bcd`.

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

170 verified cell(s) in the registry.

149 board-frame row(s) excluded by rule (PI, 2026-09-10): rows whose
`scope_override.test_set_id` names a leaderboard scoring frame are board
artefacts (the GS Era-2 board's `-era2b` and `-opmax` rows), not
measurements of their own, and are neither paired nor offered as twins
(`lib_uplift_supplement.is_board_frame_condition`).

## Status

| Status | Cells |
|---|---:|
| `already-registered` | 13 |
| `ready` | 53 |
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
| `consensus-file` | 20 |
| `crop-manifest` | 14 |
| `first-n-recluster` | 27 |
| `registered` | 13 |
| `shell-manifests` | 13 |
| `single-pass-manifest` | 21 |
| `source-run-consensus` | 6 |
| `stage-manifest` | 13 |
| `union` | 43 |

## Blocked pairs

0 verified cell(s) have no locatable pre-verifier twin.
They are recorded with the reason and left empty in the uplift column;
no substitute set is constructed.


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
| `already-registered` | 13 | 13 | Both sides are registered conditions, so both are already in `conditions.csv`. No scoring needed. |
| `ready` | 53 | 53 | The twin is a committed GeoJSON; one emitted job scores it. |
| `ready-after-materialise` | 104 | 104 | Two emitted commands: the materialiser filters the vote shell out of the recorded universe, then the score runs on the twin. No API spend and no re-aggregation. |
| `blocked` | 0 | 0 | No twin located. |

So the ceiling after a clean run of `verifier-pairing-commands.sh` is **170 computed, 0 pending** — 13 pair(s) needing no scoring at all and 157 emitted job(s).

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
