# Experiment intent — tier E K = 5 union

> **Last revised**: 2026-09-12 (original publication — built by
> `scripts/run_k_ladder_tier_e.py unions`). See [§ Changelog](#changelog).

**What this directory is.** The first-5 sub-pool consensus
union of the grid study's 384 px / 50 % overlap MINIMAL text pool, built for
tier E of the K-ladder review (`planning/k-ladder-review-2026-09-11.md`,
rulings R1 and R2).

| field | value |
|---|---|
| pool | `outputs/grid-2026-08-18/g384_ov192` |
| passes | `1,2,3,4,5` (runs 1–5) |
| `merge_passes.py --passes` | `1,2,3,4,5` |
| K | 5 |
| expected candidates (PI's approval) | 2,932 |
| measured candidates (vote ≥ 1) | 2,932 |
| delta | +0 (0.000 %) |
| verdict | **OK** |
| planned verifier stage | `g384_ov192-k-ladder-k5-verify` |
| verifier output | `outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k5` |

**How it was built.**

```bash
python scripts/merge_passes.py \
    --input-dir outputs/grid-2026-08-18/g384_ov192 \
    --output-dir outputs/grid-2026-08-18/g384_ov192/consensus-n5 \
    --sweep \
    --passes 1,2,3,4,5
```

`merge_passes.py` deduplicates within each pass at 20 m, clusters across
passes at 20 m, and records each cluster's MEAN centroid, so a first-N union
is **not** a positional prefix or a coordinate subset of a longer union. The
pass filter selects directories by the integer after `run_`, so the pool's
`run_4_recovery`, `run_8_recovery` and `run_10_recovery` directories are
skipped (`int("4_recovery")` raises and the directory is passed over) —
verified rather than assumed. The union's own `voting_summary.json` carries a
machine-readable `pass_provenance` block with a `git_blob_hash` per
contributing pass file.

**The K = 10 sibling is built differently, and that is recorded here.** The
committed K = 10 rung of this family is
`outputs/grid-2026-08-18/verifier/g384_ov192/union_k10.geojson`
(3,319 candidates), built by
`scripts/materialise_grid_unions.py`, which filters the union to the grid study's
common 487-tile carrier footprint. A `merge_passes` union of the same ten
passes holds 3,591 candidates, of which
3,325 survive that filter. This rung is
therefore built on the pool's native footprint, as the PI's expected counts
require, and the difference is reported in
`results/k-ladder-2026-09-12/tier-e/pre_launch_audit.md`.

## Changelog

### 2026-09-12 — Original publication

Built as step 1 of tier E, at US$0. No API call was made by this step.
