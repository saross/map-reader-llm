# The recovery-fragment drop — how far does it reach into committed unions?

> **Last revised**: 2026-09-13 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Verdict in one line.** Blocker B2 of
`reports/gemini37-image-55map-deltas-2026-09-13.md` is real, reproduced here to
the candidate, and its reach into committed artefacts is **small**: of the
**28 committed consensus unions** whose proposer pool holds recovery
directories, **0 are MATERIAL** (≥ 0.5 % of features), **5 are NEGLIGIBLE**
(< 0.5 %), and **23 are UNAFFECTED**. The two pools where the drop is large —
the 3.7 gold-standard (GS) image pool at 5,109 dropped features and the 3.7
55-map text pool at 13,319 — have **no `merge_passes.py` union at all**; their
unions were built by the recovery-merging `image_b_prepare_and_union` /
`grid_prepare_scoring` family, and are demonstrably recovery-inclusive. Nothing
was written over a committed union, evaluation or register row; no Application
Programming Interface (API) call was made and **US$0.00** was spent.

Every figure below was measured on sapphire on 2026-09-13 at branch
`worktree-agent-a69bbbee5ef09c208`, commit `641896b12`, in an isolated worktree
at `~/worktrees/map-reader-llm/claude-recovery-reach`.

## 1. The mechanism, at file and line

`resolve_pass_files` derives a pass directory's number by stripping the prefix
and casting:

```python
            if pass_name.startswith("pass_"):
                pass_num = int(pass_name.replace("pass_", ""))
            elif pass_name.startswith("run_"):
                pass_num = int(pass_name.replace("run_", ""))
```

— `scripts/merge_passes.py:453-456`, whose `except ValueError: continue` sits at
`scripts/merge_passes.py:459-460`. `int("2_recovery")` raises, so
`run_2_recovery` and `run_2_recovery2` are skipped. There is no warning: the
`continue` is silent, unlike
`lib_detection_paths.resolve_pool_passes`, which walks numeric `run_<N>`
directories only but **logs** each skipped fragment as one that "supplements a
pass rather than constituting one, and must be merged explicitly"
(`scripts/lib_detection_paths.py:277-284`, rationale at `:133-138`).

Two consequences, and the second is the graver:

1. **The fragment's detections never reach the union.** Measured directly (§ 3).
2. **The vote denominator is computed over the wrong pass count.**
   `merge_passes.merge_passes` sets `total_passes = len(raw_passes)`
   (`scripts/merge_passes.py:573`, and again at `:652` on the sweep path) from
   the loader's output, and `load_pass_detections` keeps a pass only `if
   features` (`scripts/merge_passes.py:538-540`). A pass whose main directory
   holds a valid but EMPTY FeatureCollection therefore vanishes entirely.
   `apply_threshold` divides `vote_count` by `total_passes` to write
   `confidence` (`scripts/merge_passes.py:395`), so both the confidence and
   every vote threshold are computed against a denominator that omits a pass
   which contributed thousands of detections through its fragment.

The second consequence is live in exactly the pool the blocker names. On
`outputs/gemini37-image-gs-2026-09-01/g384_ov192_g37img`, `run_3`'s main file
holds **0 features** against 1,663 in `run_3_recovery`, so a
`merge_passes --passes 1,2,3,4,5` build over that pool resolves five pass
directories but loads **four passes** — `total_passes` reads 4, not 5. Measured:
`~/scratch/recovery-reach/deltas2.json`, field `defective.total_passes`.

The blocker's own measurement reproduces exactly: a defective-resolver build of
that pool at vote ≥ 1 returns **650** candidates. This report's independent
re-derivation returns 650.

## 2. Enumeration — every committed union in a recovery-bearing pool

### 2.1 The pools

Fifteen pools under `outputs/` hold `run_<N>_recovery*` directories. Recovery
fragments are **additive, never duplicative**: in all fifteen, the set of tiles
on which a fragment recorded a detection is **disjoint** from the main file's
(`det_tiles_in_main = 0` for every one of the 43 fragments;
`~/scratch/recovery-reach/dup.json`). The `*.tiles.json` sidecars corroborate
it structurally — `run_2`'s reads `completed: 4, failed: 1394` and
`run_2_recovery`'s completes those 1,394. So the June "recovery merge" pattern
(`reports/token-load-audit-2026-06-12.md` § 2) does **not** apply to any of
them: a dropped fragment is lost data, not a duplicate.

| pool | recovery dirs | recovery features |
|---|---:|---:|
| `outputs/gemini37-55map-2026-08-29/g384_ov192_55map_g37` | 6 | **13,319** |
| `outputs/gemini37-image-gs-2026-09-01/g384_ov192_g37img` | 5 | **5,109** |
| `outputs/stride-55map-2026-08-25/g384_ov192_55map` | 9 | 178 |
| `outputs/gemini37-screen-2026-08-28/g384_ov192_g37` | 6 | 61 |
| `outputs/stride-55map-2026-08-25/g384_ov128_55map` | 9 | 27 |
| `outputs/image-b-gs-2026-08-28/g384_ov192_image_high` | 5 | 23 |
| `outputs/grid-2026-08-18/g384_ov192` | 3 | 14 |
| `outputs/image-b-gs-2026-08-28/g384_ov192_image` | 5 | 8 |
| `outputs/h13/armB` | 1 | 8 |
| `outputs/grid-2026-08-18/g384_ov048` | 1 | 7 |
| `outputs/stride-phaseb-2026-08-25/g512_ov176` | 1 | 7 |
| `outputs/grid-2026-08-18/g512_ov256` | 1 | 10 |
| `outputs/grid-2026-08-18/g512_ov064` | 1 | 4 |
| `outputs/stride-phaseb-2026-08-25/g512_ov320` | 2 | 3 |
| `outputs/stride-phasec-2026-08-25/g384_ov240` | 1 | 2 |

The ten pools the blocker's brief names all appear with the same feature counts;
five more turned up that the brief does not name (`image_b` non-HIGH 8,
`h13/armB` 8, stride phase B `g512_ov176` 7 and `g512_ov320` 3, phase C
`g384_ov240` 2). Source: `~/scratch/recovery-reach/pools.json`.

### 2.2 The unions those pools feed, and who built them

Twenty-eight committed unions read a recovery-bearing pool: **13
`consensus_t*.geojson` files** in five `consensus-n*` directories (all
`merge_passes.py` products, confirmed by their `voting_summary.json`
`pass_provenance` blocks, schema `consensus-pass-provenance/1`) and **15
`union_k*.geojson` files** under `outputs/**/verifier/`. (Five further
`union_k*` files under `stride-phaseb-2026-08-25/verifier/` — the `g256_ov064`
cell and the four `g384_ov128` thresholds — sit in pools with no recovery
directory and are out of scope.) The builder attribution:

| union | builder | recovery? | class |
|---|---|---|---|
| `gemini37-screen-…/g384_ov192_g37/consensus-n1/consensus_t1` | `merge_passes.py` via `build_k_ladder_phase2_unions.py` | dropped | **NEGLIGIBLE** (count 0, one candidate swapped) |
| `gemini37-screen-…/g384_ov192_g37/consensus-n3/consensus_t{1,2,3}` | same | dropped | **NEGLIGIBLE** ×3 |
| `grid-2026-08-18/g384_ov192/consensus-n1/consensus_t1` | `merge_passes.py` via `run_k_ladder_tier_e.py` | n/a — pass 1 has no fragment | UNAFFECTED |
| `grid-…/g384_ov192/consensus-n3/consensus_t{1,2,3}` | same | n/a — fragments are in passes 4, 8, 10 | UNAFFECTED ×3 |
| `grid-…/g384_ov192/consensus-n5/consensus_t{1,2,3,4}` | same | dropped, no effect | UNAFFECTED ×4 |
| `grid-…/g384_ov192/consensus-n5/consensus_t5` | same | dropped | **NEGLIGIBLE** |
| `gemini37-55map-…/verifier/g384_ov192_55map_g37/union_k5` | `stride55_prepare_and_union.py` | **included** | UNAFFECTED |
| `gemini37-image-gs-…/verifier/g384_ov192_g37img/union_k5` | `image_b_prepare_and_union.py --root … --k 5` | **included** | UNAFFECTED |
| `gemini37-screen-…/verifier/g384_ov192_g37/union_k{5,10}` | same | included | UNAFFECTED ×2 |
| `grid-…/verifier/{g384_ov048,g384_ov192,g512_ov064,g512_ov256}/union_k10` | `materialise_grid_unions.py` over `grid_prepare_scoring.py`'s prepared passes | **included** | UNAFFECTED ×4 |
| `image-b-gs-…/verifier/{g384_ov192_image,…_image_high}/union_k10` | `image_b_prepare_and_union.py` | **included** | UNAFFECTED ×2 |
| `stride-55map-…/verifier/{g384_ov128_55map,g384_ov192_55map}/union_k10` | `stride55_prepare_and_union.py` | **included** | UNAFFECTED ×2 |
| `stride-phaseb-…/verifier/{g512_ov176,g512_ov320}/union_k10` | `stride_prepare_and_union.py` | **included** | UNAFFECTED ×2 |
| `stride-phasec-…/verifier/g384_ov240/union_k10` | same | **included** | UNAFFECTED |

`outputs/h13/armB` holds a fragment but no union; `prepare_h13_scoring.load_pass`
merges it explicitly (`scripts/lib_detection_paths.py:137-138` names that chain
as the precedent).

**Classification counts.** MATERIAL (≥ 0.5 % of features) **0**; NEGLIGIBLE
(< 0.5 %, non-zero effect on the artefact) **5** — the four `consensus_t*`
files of `gemini37-screen-…/consensus-n1` and `…/consensus-n3` plus
`grid-…/consensus-n5/consensus_t5`; UNAFFECTED **23** — eight `consensus_t*`
files whose sub-pool contains no fragment or whose threshold does not move, and
all fifteen `union_k*` files, whose builders merge fragments.

**How "included" was established, not assumed.** Four independent lines,
because no single one is decisive everywhere:

1. **Code.** `grid_prepare_scoring.resolve_cell_passes` looks each fragment up
   and appends it to its parent pass's file list, with the departure from
   `lib_detection_paths.resolve_pool_passes` documented at
   `scripts/grid_prepare_scoring.py:188-208` and the merge loop at `:245`;
   `materialise_grid_unions.py:113` reads the prepared
   `detections_dedup.geojson` files that loop produced, via
   `grid_analysis.load_cell_passes` (`scripts/grid_analysis.py:149`).
   `image_b_prepare_and_union.py:82` resolves each pass through
   `stride_prepare_and_union.resolve_pass_paths`
   (`scripts/stride_prepare_and_union.py:89-100`, "main first" then the
   fragment) and logs `"(+recovery)"` at `:98`.
   `stride55_prepare_and_union.py:73` globs `f"{run}_recovery*"`, which also
   catches `_recovery2`.
2. **Builder identity.** `image_b_prepare_and_union.py` is `--root`-,
   `--cell`- and `--k`-parameterised, and its own `--root` help text names
   `outputs/gemini37-screen-2026-08-28` as the example
   (`scripts/image_b_prepare_and_union.py:63-65`). It writes
   `root/verifier/<cell>/union_k<k>.geojson` at `:122`, which is exactly where
   the gemini37 GS unions sit, at exactly the two K values committed.
3. **Coverage gate.** That script raises `CoverageError` unless a pass's
   processed-tile set equals the pinned manifest **exactly**
   (`scripts/image_b_prepare_and_union.py:84-89`). On the 3.7 GS image pool,
   `run_3`'s own `*.tiles.json` records `total_tiles: 1398, completed: 1,
   failed: 1397`, and `run_3_recovery`'s records `completed: 1397` — strict
   complements. The union could not have been written at all without the
   fragments. Decisive, and the strongest single line here.
4. **Counts.** The 3.7 GS image `union_k5` holds **674** candidates. A
   defective-resolver build of its pool yields **650** and a corrected one
   **742**. The carrier-tile filter in `union_with_votes`
   (`scripts/materialise_grid_unions.py:70-95`) can only remove candidates, so
   674 cannot descend from a 650-candidate recovery-less union. Independently
   decisive. Separately, the 3.7 55-map pool has 212 tiles on which *only* a
   fragment detected, and its committed `union_k5` names **148** of them
   (`~/scratch/recovery-reach/witness.json`) — nothing but a fragment could
   have put them there.

**One residue, 15 features wide.** `stride_prepare_and_union.resolve_pass_paths`
globs the exact `f"{run}_recovery"`, so a `_recovery2` would be missed by
anything routed through it. Exactly one pool in the repository has one —
`gemini37-55map-…/g384_ov192_55map_g37/run_3_recovery2`, 15 features — and its
union was built by `stride55_prepare_and_union.py`, whose `_recovery*` glob does
catch it. Whether those 15 features are in the committed 12,715-candidate union
was not separately confirmed; at 0.11 % of that pool's 13,319 recovery features
it is NEGLIGIBLE on any reading, and it is named here so it is not forgotten.

**A caution about a test that looked decisive and is not.** A
`contributing_passes` probe — does a union candidate near a fragment detection
credit the fragment's pass? — is worthless on the `union_k*` family, which
carries only `source_tile` and `vote_count` and no `contributing_passes` at all;
and on the `consensus_t*` family it yields false positives, because 50 %
tile overlap means the main file often detected the same mound from a
neighbouring tile. It is recorded here so it is not re-run as evidence.

### 2.3 What the September retrospective already settled, and what it did not

`reports/union-staleness-retrospective-2026-09-12.md` re-derived the **106**
`merge_passes.py` consensus unions that a registered condition reads and
classified 64 REPRODUCES, 36 SUBPOOL-CONSISTENT, 1 UNRESOLVED, 5 STALE. Those
106 sit in **48 pools, none of which is one of the 15 above** — the sets are
disjoint (checked by pool path against `results/union-staleness-retrospective-2026-09-12.json`).

That is the good news and it needs stating precisely, because the
retrospective's method cannot have caught this defect: it re-derived each union
using `merge_passes.py`'s own resolver, so "REPRODUCES" certifies that the
union is faithful to *the pool as that resolver sees it*. A union built and
re-derived through the same blind spot reproduces perfectly while omitting the
same data twice. The retrospective's verdicts stand; their scope does not
extend to fragment inclusion, and this report is the complement.

## 3. Measured deltas — rebuilt with a corrected resolver

The rebuild ran a corrected resolver (`run_<N><suffix>` folds into pass N, the
fragment's files appended after the main file's so within-pass dedup still
prefers the main feature) through `merge_passes.py`'s **own**
`deduplicate_within_pass` → `cluster_across_passes` → `apply_threshold` chain,
so a difference is a difference in inputs, not in algorithm. Harness:
`~/scratch/recovery-reach/rebuild_with_recovery.py`;
output `~/scratch/recovery-reach/deltas.json`. `scripts/merge_passes.py` was not
modified.

### 3.1 The five `merge_passes.py` unions — the only ones the defect touches

| union dir | passes | threshold | committed | corrected | Δ | Δ % | class |
|---|---|---:|---:|---:|---:|---:|---|
| `gemini37-screen-…/consensus-n1` | 1 | T1 | 640 | 640 | 0 | 0.000 | NEGLIGIBLE — count holds, set changes; § 3.2 |
| `gemini37-screen-…/consensus-n3` | 1–3 | T1 | 757 | **759** | +2 | +0.264 | NEGLIGIBLE |
| | | T2 | 608 | **609** | +1 | +0.164 | NEGLIGIBLE |
| | | T3 | 529 | **530** | +1 | +0.189 | NEGLIGIBLE |
| `grid-…/g384_ov192/consensus-n1` | 1 | T1 | 1,826 | 1,826 | 0 | 0.000 | UNAFFECTED |
| `grid-…/g384_ov192/consensus-n3` | 1–3 | T1–T3 | 2,481 / 1,701 / 1,303 | identical | 0 | 0.000 | UNAFFECTED |
| `grid-…/g384_ov192/consensus-n5` | 1–5 | T1–T4 | 2,932 / 2,025 / 1,650 / 1,396 | identical | 0 | 0.000 | UNAFFECTED |
| | | T5 | 1,168 | **1,169** | +1 | +0.086 | NEGLIGIBLE |

Every committed count is reproduced exactly by the defective resolver, which is
what identifies these five as `merge_passes.py` products in the first place.

The grid `consensus-n1` and `consensus-n3` rungs are untouched for a structural
reason worth recording: that pool's fragments are in passes **4, 8 and 10**, so
a first-3 sub-pool never reads one. Raw feature counts are byte-identical
(3,198 and 9,582 defective and corrected), so the candidate sets are identical,
not merely equinumerous.

At `consensus-n5` the whole effect of the pool's 14 dropped features is **one
cluster promoted from 4 votes to 5** (vote distribution `{…, 4: 228, 5: 1168}`
→ `{…, 4: 227, 5: 1169}`); T1–T4 are unchanged in count *and* in membership.

### 3.2 A count that does not move while the set does

`gemini37-screen-…/consensus-n1` is the cautionary case. Committed 640,
corrected 640 — and a per-candidate positional match (2 m, EPSG:32635) shows
**639 matched, 1 new, 1 absent**. The recovery fragment displaced one candidate
without changing the total. A count check passes; the artefact is different.
`consensus-n3` behaves the same way at a slightly larger scale: 757 → 759 with
**756 matched, 3 new, 1 absent**, and one further candidate promoted from 2
votes to 3.

This is the reason a rebuild-and-diff was necessary rather than a count sweep,
and it is the reason the blocker's "only 3.6 % low, so no count check would
catch it" understates the problem: at these rungs the count is not low at all.

### 3.3 The non-`merge_passes` unions, measured anyway

These are UNAFFECTED — their builders merge fragments — but the same rebuild was
run over their pools so the PI can see the size of the effect the defect *would*
have had, and so the one genuinely large number is on the record.

| pool → committed union | defective | corrected | Δ | Δ % |
|---|---:|---:|---:|---:|
| 3.7 GS image → `union_k5` (674) | 650 | **742** | **+92** | **+14.154** |
| grid `g512_ov256` → `union_k10` (2,585) | 2,905 | 2,915 | +10 | +0.344 |
| image-B HIGH → `union_k10` (9,189) | 9,795 | 9,821 | +26 | +0.265 |
| grid `g512_ov064` → `union_k10` (1,402) | 1,547 | 1,543 | **−4** | −0.259 |
| stride phase B `g512_ov320` → `union_k10` (3,778) | 4,242 | 4,251 | +9 | +0.212 |
| grid `g384_ov192` → `union_k10` (3,319) | 3,591 | 3,585 | **−6** | −0.167 |
| image-B → `union_k10` (4,065) | 4,357 | 4,364 | +7 | +0.161 |
| stride phase B `g512_ov176` → `union_k10` (1,981) | 2,166 | 2,169 | +3 | +0.139 |
| 3.7 GS text → `union_k5` (791) | 859 | 860 | +1 | +0.116 |
| stride phase C `g384_ov240` → `union_k10` (5,250) | 5,870 | 5,869 | −1 | −0.017 |
| 3.7 GS text → `union_k10` (913) | 991 | 991 | 0 | 0.000 |
| grid `g384_ov048` → `union_k10` (1,827) | 1,885 | 1,885 | 0 | 0.000 |
| `h13/armB` (no union) | 1,724 | 1,724 | 0 | 0.000 |

Two things to notice.

**The defect's severity is not the fragment's size — it is the fragment's share
of its pass.** The 3.7 GS image pool is the only one where the drop is
order-of-magnitude (+14.2 %), and not because 5,109 features is a big number
but because runs 2, 3 and 4 are *almost entirely* fragment: `run_3`'s main file
holds 0 features. Contrast the 3.7 55-map pool, where 13,319 features — the
largest absolute drop in the repository — sit against five substantially
complete main passes.

**Folding a fragment can reduce the candidate count.** Three pools go *down*
(−6, −4, −1). A fragment feature 20 m from two previously separate clusters
bridges them, and two candidates become one. Any fix therefore cannot be gated
on "the count should go up", and the `± 2 %` count gates in
`run_k_ladder_tier_e.py:165-166` and `build_k_ladder_phase2_unions.py` would not
have caught any of this in either direction.

## 4. Readers of the four NEGLIGIBLE unions, and what re-scoring costs

### 4.1 K-ladder Phase 2 — `gemini37-screen-2026-08-28`, pool `g384_ov192_g37`

This is the one affected pool of the 14 that
`results/k-ladder-2026-09-12/first-n-union-sizes.json` enumerates. Its rungs:

| rung | registered condition | union | Δ union | new candidates needing a verifier call |
|---|---|---|---:|---:|
| K = 1 | `gemini37-screen-2026-08-28::g37-text-k1-verified-opmax` | `consensus-n1/consensus_t1` | 0 (1 swapped) | **1** |
| K = 1 | `gemini37-screen-2026-08-28::g37-text-k1-verified-carried-p0.10-k1` | same | 0 (1 swapped) | (same 1) |
| K = 3 | `gemini37-screen-2026-08-28::g37-text-k3-verified-opmax` | `consensus-n3/consensus_t{1,2,3}` | +2 / +1 / +1 | **3** |

Verifier coverage checked by candidate position against the committed crops
manifests (`crops_k1/candidate_manifest.json`, 640 entries;
`crops_k3/candidate_manifest.json`, 757 entries — both stamped
`source_geojson` pointing at the very consensus files above). K = 1: 639 of 640
corrected candidates covered, **1 uncovered** at (25.945875, 42.354136).
K = 3: 756 of 759 covered, **3 uncovered** at (24.986074, 42.311519),
(24.761750, 42.290037), (24.920161, 42.274606).

**So these two cells cannot be re-scored at US$0.** They need a 1-candidate and
a 3-candidate verifier pass respectively — 4 calls, **US$0.0028** at the
audited Gemini 3 flash verifier rate of US$0.000693 per candidate
(`reports/token-load-audit-2026-06-12.md` § 5, as carried in
`scripts/run_k_ladder_tier_e.py:170`). That is the whole API cost of closing
this defect out across the repository.

What *can* be said at US$0 about the K = 3 cell: the candidate promoted from 2
votes to 3 at (25.865733, 42.441604) is `candidate_00049` in the committed run,
source tile `K-35-052-4_32635_x1920_y960.png`, with `mound_probability` **1.0**.
The rung's operating point is vote ≥ 3, prob ≥ 0.10, so that candidate **does**
enter the scored detection set. The committed cell
(`results/k-ladder-2026-09-12/phase2/cells/gemini37-screen-2026-08-28__g37-text-k3-verified-opmax/evaluation.json`)
carries 494 detections, F1 0.887 at 20 m (p 0.834, r 0.9471), F1 0.902 at 50 m,
tile-Matthews Correlation Coefficient (MCC) 0.1337. The change is between one
and four detections on 494 — at most **0.81 % of the detection set** — so
|ΔF1| at 20 m is bounded at roughly **±0.006** on the cell's own precision and
recall, sign depending on whether the added detections match reference mounds.
That decomposition is reconstructed from rounded precision and recall and is a
bound, not a measurement; the measurement needs the 4 verifier calls.

### 4.2 K-ladder tier E — `grid-2026-08-18`, pool `g384_ov192`

| rung | registered condition | union | Δ union | verifier call needed |
|---|---|---|---:|---|
| K = 1 | `grid-2026-08-18::g384-ov192-k1-verified-opmax`, `::g384-ov192-k1-verified-p0.15-k1` | `consensus-n1/consensus_t1` | 0, identical set | no |
| K = 3 | `grid-2026-08-18::g384-ov192-k3-verified-opmax` | `consensus-n3/consensus_t{1,2,3}` | 0, identical set | no |
| K = 5 | `grid-2026-08-18::g384-ov192-k5-verified-opmax` | `consensus-n5/consensus_t5` | +1 | **no** |
| K = 10 | `grid-2026-08-18::g384-ov192-k10-verified-p0.15-k10-boardframe` | `verifier/g384_ov192/union_k10` (`materialise_grid_unions.py`) | UNAFFECTED | no |

**The tier-E K = 5 cell re-scores at US$0, and its delta is exactly zero.**
The corrected `consensus-n5` union is the same 2,932 candidates, all matched
within 2 m, and all 2,932 are covered by the committed
`k-ladder/k5/crops/candidate_manifest.json` — `0 UNCOVERED`. The single change
is the one cluster promoted from 4 votes to 5, at (26.513551, 41.879916),
which is `candidate_01335`, source tile `K-35-078-1_Lesovo_x192_y2496.png`,
`mound_probability` **0.1**. The rung's operating point is vote ≥ 5,
**prob ≥ 0.15** (`results/k-ladder-2026-09-12/tier-e/operating-points.json`,
row 3, `carried_is_opmax: true`), which 0.1 does not clear. The scored
detection set is therefore byte-identical and the cell's committed F1 0.8905 at
20 m and tile-MCC 0.8139 (`results/k-ladder-2026-09-12/tier-e/ladder.json`)
**do not move**.

The operating point itself is also stable. The promoted candidate only joins
the vote ≥ 5 column at probability thresholds ≤ 0.10, and the best 20 m F1
anywhere in that region of the committed sweep is **0.8036** at (vote 5, prob
0.10) with 573 detections, against the opmax **0.8828**
(`outputs/grid-2026-08-18/verifier/g384_ov192/k-ladder/k5/sweep_board.json`,
buffer 20 m). One extra detection cannot close a 0.079 gap, so the argmax
cannot migrate and the rung stays a rung.

### 4.3 Boards and paper-facing artefacts

`g37-text` conditions are referenced from the register
(`results/run-conditions.json`, `results/conditions-manifest.json`,
`results/run-analyses.json`, `results/analyses-manifest.json`),
`results/uplift-supplement/build-report.md`, and the era-2 verified board
`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/` — but the board
carries the **K = 10** cells (`g37-text-k10-verified-carried-p0.10-k10`,
`…-era2b`, `…-swap37`, `…-swap38`), all of which read
`verifier/g384_ov192_g37/union_k10`, measured UNAFFECTED (Δ 0 even on the
`merge_passes` basis). The K = 1 and K = 3 rungs that do move are Phase 2
ladder cells only, and carry no board membership.

The paper tree names exactly two cells from this pool. `grep -rhoE
'g384-ov192-k[0-9]+|g37-text-k[0-9]+'` over `docs/paper/` and `paper/` returns
only **`g37-text-k10`** and **`g37-text-k5`** — the sole occurrence is claim
R4-23 of `docs/paper/results-claims-inventory-2026-09-12.md:326`. Both read
`verifier/g384_ov192_g37/union_k{5,10}`, which
`image_b_prepare_and_union.py` built with the fragments merged. Nothing matches
`g37-text-k1` (as a whole token), `g37-text-k3`, or any `g384-ov192-k{1,3,5}`.
**No paper-facing artefact is affected.**

## 5. What did NOT turn out affected

- **No MATERIAL union anywhere.** The largest delta on any committed artefact is
  +2 candidates on 757 (+0.264 %).
- **The two big-drop pools.** 13,319 and 5,109 dropped features reach nothing:
  their unions include the fragments. Had `merge_passes.py` built the 3.7 GS
  image union, it would have been wrong by +14.2 % with `total_passes` reading
  4 instead of 5 — which is exactly why the blocker was right to stop before
  building the K = 3 calibration union on that pool.
- **The 106 unions of the September retrospective.** Disjoint pool sets; the
  earlier verdicts are unchanged and unchallenged.
- **The 55-map corpus.** Both stride cells and the 3.7 55-map cell are
  fragment-inclusive; no 55-map board row, tiering, or condition moves.
- **Every `union_k*.geojson`.** All 15 in recovery-bearing pools were built by
  the merging family.
- **`scripts/merge_passes.py`** — untouched on this branch. The repair is a
  file, `reports/recovery-fragment-drop/merge_passes.patch`.
- **Every committed union, evaluation, `voting_summary.json` and register row**
  — untouched. All rebuilds went to `~/scratch/recovery-reach/scratch/` on
  sapphire.
- **US$0.00 spent; no API call.**

## 6. The proposed patch and its test

`reports/recovery-fragment-drop/merge_passes.patch` (126 lines, `git apply
--check` clean at `641896b12`) replaces `resolve_pass_files` with a version
that groups directories by pass number through a
`^(?:pass|run)_(?P<num>\d+)(?P<suffix>.*)$` match, appends each fragment's
files after the main directory's, keeps the main directory's name as the pass
id, logs each fold, and leaves the pass **count** unchanged — a fragment joins
an existing pass and never creates one. Filtering still selects by pass number,
so a fragment is filtered with its parent.

`tests/test_merge_passes_recovery.py` (committed, tier 1, 12 tests) is written
to be green in both states, because the patch is deliberately not applied:

- **3 characterisation tests** assert today's behaviour, including the
  denominator collapse, and are expected to FAIL the moment the patch lands.
  Each docstring says so and says what to invert. This is the designed signal,
  not a regression.
- **5 acceptance tests** assert the repaired behaviour — folding, main-first
  ordering, every pass reaching the loader, filtering, sidecar exclusion — and
  skip while the patch's `_PASS_DIR_RE` constant is absent.
- **4 state-independent invariants**: a fragment-free pool is unchanged,
  `pass_NN` naming is preserved, an empty pool resolves to nothing, and a
  sidecar-only directory contributes nothing.

Verified both ways on sapphire: unpatched, `53 passed, 5 skipped` across
`test_merge_passes_recovery`, `test_merge_passes`,
`test_consensus_pass_provenance` and `test_check_union_provenance`; with the
patch applied in a scratch checkout, `3 failed, 44 passed` — the three
characterisation tests, and **no regression in the 35 pre-existing
`merge_passes` and `pass_provenance` tests**. The patch was reverted
(`git checkout --`) and sapphire's worktree left clean.

Two further repairs the PI may want folded into the same ruling:

1. **Make the skip loud.** Even patched, an unparsable directory name still
   `continue`s in silence. `lib_detection_paths.resolve_pool_passes` warns
   (`scripts/lib_detection_paths.py:277-284`); `merge_passes.py` should too.
2. **Widen the two narrow globs.** `grid_prepare_scoring.py:245`
   (`run_*_recovery`, which requires the name to end there) and
   `stride_prepare_and_union.py:95` (the exact `f"{run}_recovery"`) would both
   miss a `_recovery2`. That matters beyond the grid, because
   `image_b_prepare_and_union.py:82` — the builder of every committed gemini37
   GS union — routes through the second of them. Only
   `stride55_prepare_and_union.py:73` globs `_recovery*`. No committed artefact
   is known to be affected (§ 2.2, "One residue"); the next storm-hit campaign
   needing a second recovery round would be.

## 7. Ruling options for the PI

1. **Fix the builder.** Apply `merge_passes.patch`, invert the three
   characterisation tests, and add the warning of § 6.1. No committed artefact
   changes by applying it; what changes is every union built afterwards —
   including the 3.7 image 55-map campaign's, which is the reason the blocker
   raised it. **Recommended.**
2. **Rebuild and re-score at US$0 where possible.** One cell qualifies:
   `grid-2026-08-18::g384-ov192-k5-verified-opmax`. Its corrected union differs
   by one vote count, the promoted candidate fails the carried probability
   threshold, and its F1 and tile-MCC are provably unchanged. Rebuilding it is
   therefore optional bookkeeping, not a correction — the PI may reasonably
   decline and instead annotate the cell.
3. **Spend US$0.0028 to close the two Phase 2 cells.** `g37-text-k1-verified-*`
   needs 1 verifier call and `g37-text-k3-verified-opmax` needs 3. The K = 3
   cell's F1 will move by at most ±0.006 at 20 m; the K = 1 cell's candidate
   swap may move it by less. Neither is on a board or in the paper. Options:
   spend it and re-score; or leave both and attach a caveat to the three
   register rows recording the measured candidate deltas (+0 with one swap,
   and +2 / +1 / +1).
4. **Re-open the September retrospective's scope.** Its 106 unions are clean of
   this defect by disjointness, but the method — re-derive with the same
   resolver — cannot detect fragment inclusion by construction. If the PI wants
   a single certificate covering both staleness and fragment inclusion,
   `check_union_provenance.py` should grow a fragment-aware second pass. Cheap,
   local, no API.
5. **Do nothing beyond recording it.** Defensible on the numbers — nothing
   MATERIAL, nothing paper-facing — but it leaves a builder that will silently
   corrupt `total_passes` on the next storm-hit campaign, which is the
   circumstance the 3.7 image 55-map run is most likely to create.

## Changelog

### 2026-09-13 — Original publication

Measured the reach of blocker B2 of
`reports/gemini37-image-55map-deltas-2026-09-13.md` across every committed
consensus union in a recovery-bearing pool. Fifteen pools hold 43 recovery
fragments, all additive (detecting-tile sets disjoint from their main files, so
the June recovery-merge duplication does not apply). Twenty-eight committed
unions read them: **0 MATERIAL, 5 NEGLIGIBLE, 23 UNAFFECTED**. The five
`merge_passes.py` unions in those pools are the only ones the defect touches,
with a largest delta of +2 candidates on 757. The two pools where the drop is
large (13,319 and 5,109 features) feed only recovery-merging builders and are
unaffected; the 3.7 GS image case was settled by the count argument
(committed 674 cannot descend from the defective 650). The tier-E K = 5 cell
re-scores at US$0 with a provably zero F1/MCC delta; the two Phase 2 `g37-text`
cells need 4 verifier calls totalling US$0.0028. No board row, tiering or
paper artefact moves. `reports/recovery-fragment-drop/merge_passes.patch` and
`tests/test_merge_passes_recovery.py` landed at commit `641896b12`;
`scripts/merge_passes.py` was not modified, and US$0.00 was spent.
