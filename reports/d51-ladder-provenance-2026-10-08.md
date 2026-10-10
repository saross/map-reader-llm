# D51 ladder provenance and the cost of the clip: rulings D57 (2) and (3), 2026-10-08

> **Last revised**: 2026-10-10 (Astra's review of 2026-10-09: file total corrected, the rebuild's
> inverse-provenance claim qualified, the coverage-authority claim scoped, declarations pinned to
> the consensus and inputs). See [§ Changelog](#changelog) for revision history.

**Status: FOR RE-REVIEW** (Astra reviewed `1fc1f72df` on 2026-10-09 and asked for
changes; the fixes are on branch `d51-ladder-provenance-fixes`, then the PI). Branch
`d51-ladder-provenance`, cut from PR #26's branch `scorer-frames-d50-d51` at
`842f9e92a`. It adds
evidence-cited declarations so that the D51 gate can determine every Phase 2
pv-diag-384 rung, and measures what the D51 clip costs the ladders the gate
then refuses. No API call was made. No committed consensus, evaluation, sweep,
ladder file or register row was changed; `results/k-ladder-2026-09-12/phase2/`
was not regenerated (that is the re-score of D57 (4)). All computation ran on
sapphire, from a disposable worktree of this branch
(`~/worktrees/map-reader-llm/claude-d51-ladder-provenance`), writing to
`~/scratch/d51-ladder-provenance-2026-10-08/`; the small outputs are committed
in `d51-ladder-provenance-2026-10-08-scripts/out/` beside this file.

Abbreviations, first use: PI is the principal investigator; F1 is the
point-matched F1 score at 20 m, and P and R are its precision and recall; MCC is
the tile-level Matthews correlation coefficient (tile join `id`, the evaluator's
default); TP, FP and FN are true positives, false positives and false
negatives; K is the number of proposer passes a candidate pool unions; T is the
proposer's sampling temperature; opmax is a rung's sweep-optimal operating
point. D50, D51 and D57 are PI rulings in `planning/pi-decisions-2026-09-20.md`
(D57 at line 87).

## 1. Headline

- **Task A (D57 (3)).** The four T 0.7 ladders' passes are determinable through
  a declared tiling. Each of the 40 passes their rungs use (runs 1–10) passed
  five checks against the study YAML at its writer commit, the batch writer's
  source, the manifest's history and its own `.tiles.json`. As expected,
  **MINIMAL image T 0.7 is now refused**, like its T 1.0 sibling, on the same
  tile (`K-35-053-3_Elenovo_x1344_y672.png`, 2.4289 km², 2 board reference
  mounds). The other three assess the same area at every rung.
- **Task B (D57 (3)).** All 26 K = 5 and K = 10 pools of the thirteen
  pv-diag-384 ladders were rebuilt from their presumed passes.
  `merge_passes.py` as of `362f1a305`, the version in force when every one of
  them was committed on 2026-04-17 (name order), reproduces **all 26 byte for
  byte**: every threshold file, 195 in all, and every count in each
  `voting_summary.json`. The 52 threshold files of the 26 K = 1 and K = 3
  validation pools reproduce byte for byte too (247 across both groups). The current merger (numeric order since `75d7c8d4c`)
  reproduces the 13 K = 5 pools and **none of the 13 K = 10 pools**. Each pool
  is declared with the pass list the April rebuild read. An exact rebuild shows
  that those passes, read in that order, construct the committed pool; it does
  not show that no other pass history could (§ 3.2), so each declaration is an
  evidence-cited retrospective reconstruction, not a proof of uniqueness.
- **Surprising: a new refusal.** Once its K = 10 pool is determinable,
  **MINIMAL image T 0.3 is refused** too. Runs 1–5 and 10 all skipped
  `K-35-078-1_Lesovo_x2352_y3024.png`, so K = 1, 3 and 5 share an area that
  K = 10 exceeds by 2.0998 km². The gap holds no reference mound.
- **Gate survey** over the fourteen ladders (§ 5): before, 5 refused and 9
  undetermined; after, **7 refused, 7 the same, 0 undetermined**.
- **Task C (D57 (2)).** The clip with references kept lowers F1 only where a
  higher rung had found mounds in the gap. HIGH text T 1.0 loses **−0.0040,
  −0.0040, −0.0039** at K = 3, 5 and 10 (3 mounds), and MINIMAL image T 0.7
  loses **−0.0029** at each (2 mounds). Elsewhere it changes nothing to 4 dp.
  The PI's per-mound estimate, (2 − F1)/(2TP + FP + FN), matches every measured
  loss to within 0.00002 F1. Two parts of the estimate's framing do not hold
  (§ 6.5): MINIMAL image T 1.0, expected to lose about 0.003, loses nothing,
  because its rungs never found the two gap mounds; and the zero-mound gaps
  remove no false positives, because no committed point has any detection in
  them. The K = 1 → K = 10 gains fall by 0.0039 (HIGH text T 1.0) and 0.0029
  (MINIMAL image T 0.7). The gain on every other ladder is unchanged.
- **Validation.** All 18 declared-route areas on the rungs the gate could
  already determine reproduce the recorded-route area exactly (symmetric
  difference 0.0 km²). An independent recomputation, without the library,
  agrees with the gate on all 52 rung areas. All 44 unclipped scores equal
  their committed F1 at 4 dp. All six red-sentinel mutations turn their tests
  red. The tier-1 suite passes (4,160 tests).

## 2. Task A: the four T 0.7 ladders

### 2.1 What the gate lacked

PR #26's survey (`reports/scorer-frames-d50-d51-2026-10-08.md` § 5.6) refused
every rung of these ladders with "pass … has no meta file recording its tile
manifest". The meta files exist. Their `configuration.full_config_snapshot` is
the prompt configuration only, with no `manifest_path`, because the passes were
written by `lib_batch_api.py` 1.5.0 in March 2026. The pass GeoJSONs do record
`processed_tiles` (487, and 486 for MINIMAL image runs 1 and 5). The gate
cannot tell which tiling those names belong to, and by design it never infers a
tiling from a name.

### 2.2 The change

The smallest change consistent with `scripts/lib_assessed_area.py`'s design is
a declaration of exactly the missing fact. A new `pass_tilings` section in
`inputs/provenance/assessed-area-declarations.json` names the tile manifest
for a list of pass files, each anchored by its git blob hash. The new
`resolve_pass_manifest` (commit `283d2626c`) falls back to it only when the
meta records no manifest. The pass's own `processed_tiles` still define what it
assessed (within the scope set out below), so the declared tiling cannot hide a
skipped tile. The existing check
still refuses a processed tile outside the manifest, now reached through the
declared route as well; a tier-1 test covers it. A meta that records a
different manifest, a pass declared twice, or a pass whose bytes have changed
since its declaration all make the area undetermined rather than picking one.

**The scope of `processed_tiles` as the coverage record (added 2026-10-10,
Astra's review).** For the passes declared here, the top-level
`processed_tiles` records the tiles whose output was incorporated, empty tiles
included, and leaves out a tile whose response failed. The April writer
(`b57cf6c22:scripts/4_detect_mounds_batch.py`) logs a success before parsing
(line 562), returns nothing on a parse failure (583–586), and adds a tile to
the record only when output came back (1152–1164). The March batch writer
removes unresolved parse failures before writing the record
(`8b52ab63b:scripts/lib_batch_api.py:1583`). The claim does not extend to every
historical writer path. That revision's patch route (`:1975–2007`) writes the
tiles it recovers into a nested `properties.processed_tiles`, which
`read_processed_tiles` does not read. It rewrites the GeoJSON only when the
recovered tiles yielded features, and it marks the sidecar `.tiles.json` with
`patched` and `patch_timestamp`. None of the 130 declared pass files was
patched. All carry a top-level record and none a nested one; no feature's
`source_tile` lies outside the top-level set; and no sidecar records `patched`
or `patch_timestamp` (Astra's scan, repeated 2026-10-10). A patched file, or a
pass from another campaign, needs the same sidecar check before its top-level
record is taken as its coverage.

### 2.3 The evidence, per pass

`t07_tilings.py` checks each of the 40 passes (runs 1–10 of each cell) and
aborts the cell on any failure (`out/t07_tilings.json`, per-pass records):

1. **Writer.** The meta's `environment` names the commit and script, and its
   `configuration` the model, prompt version, temperature and thinking level.
   No meta records `manifest_path`.
2. **Study.** At the writer commit, exactly one `studies/*.yaml` has this
   cell's parent as `execution.output_dir` and a condition named after the
   cell; its `inputs.manifest` is `inputs/tiles_384/full_evaluation_manifest.json`,
   and its condition's prompt configuration and temperature equal the meta's.
3. **Writer source.** `scripts/lib_batch_api.py` at that commit reads
   `inputs["manifest"]` and resolves tiles with
   `_resolve_tile_paths(manifest_path`.
4. **Manifest history.** The manifest's bytes at the writer commit equal its
   bytes now. Its only commit is `8b52ab63b`.
5. **Tile for tile.** The pass's `.tiles.json` `completed` ∪ `failed` equals the
   487-tile manifest exactly, and `processed_tiles` lies inside it.

| Cell (`outputs/h11/pv-diag-384/…`) | Study YAML | Writer commits (runs 1–10) | Meta configuration | Unprocessed tiles |
|---|---|---|---|---|
| `flash-minimal-text-n30-t07/text-t0.7` | `h11-384-flash-minimal-text-n30-t07.yaml` | `2126c3efa`, `9017ca7bc`, `af571fc69` | `detect_brief-text`, 0.7, minimal | none |
| `flash-high-text-n5/text-t0.7` | `h11-384-flash-high-text-n5.yaml` | `765cb232a`, `2126c3efa`, `9017ca7bc`, `e55c9c3ad` | `detect_brief-text`, 0.7, high | none |
| `image-n5/image-t0.7` | `h11-384-pv-diag-image-n5.yaml` | `8b52ab63b`, `2f425fc8a` | `library_plus-hp`, 0.7, minimal | run_1 and run_5: `K-35-053-3_Elenovo_x1344_y672.png` |
| `flash-high-image-n5/image-t0.7` | `h11-384-flash-high-image-n5.yaml` | `765cb232a`, `2126c3efa`, `9017ca7bc` | `library_plus-hp`, 0.7, high | none |

**Found on the way: a second tiling with the same names.**
`inputs/grid-2026-08-18/grid_384_ov048_manifest.json` (created 2026-08-18 in
`d325d9e0d`, and a `KNOWN_TILINGS` key) holds the same 487 tile names, so
check 5 alone matches two registered tilings. It is harmless here. Its polygons are identical tile for
tile (symmetric difference 0 m² for every one of the 487 pairs), and the file
is absent at every writer commit (`git cat-file -e` fails). Both facts are
checked per pass, and the declaration names the manifest the study YAML names.
If either check had failed, the cell would have been refused.

**Outcome.** As expected: MINIMAL image T 0.7's K = 1 rung (run 1) lacks the
Elenovo tile, and K = 3 (runs 1–3), K = 5 and K = 10 include it, so the gate
refuses with 2.4289 km², the same tile and excess as the T 1.0 sibling. The
other three ladders assess 1402.4067 km² at every rung. Also noted: **run 5 of
MINIMAL image T 0.7 skipped the same tile**, which D57's premise check (runs
1–3) did not cover. It changes no verdict, because runs 2–4 cover the tile.

## 3. Task B: the K = 5 and K = 10 pools

### 3.1 Method

`rebuild_pools.py` rebuilds every K = 5 and K = 10 pool of the thirteen
pv-diag-384 ladders. A pool here is the union `consensus_t1.geojson` the
board's R1 verifier member names (`vintage.union` in
`results/leaderboard/era2/gs-era2-verified-board-2026-09-10/opmax/membership.json`).
The 3.7 GS ladder's pools were declared in PR #26.

- **Presumed passes.** `consensus-n<N>/` means `--passes 1,..,N` (the first-N
  rule: `scripts/run_phase3a_image_analysis.sh` at `1415e704e` passes the
  literal `"1,2,3,4,5"`; `reports/union-staleness-retrospective-2026-09-12.md`
  § 2). `consensus/` means every `run_*` of the cell, checked to number exactly
  ten. No pool has a recovery fragment.
- **Mergers.** Every consensus directory was committed once, on 2026-04-17
  (`2e8cc6481` image, `09fe46a7f` text, `c3e8e0701` scale-4), and never
  modified (`git log` per directory). The rebuild uses
  `scripts/merge_passes.py` extracted from `362f1a305` (2026-04-17 00:20:32
  +1000, the version in force), which reads `sorted(glob("run_*"))`: run_1,
  run_10, run_2, …. It also uses the branch's merger, which reads in numeric
  order since `75d7c8d4c` (2026-09-13). Between `362f1a305` and `ac7d393c7` the
  algorithm did not change (`git diff`: provenance recording only).
- **Comparison.** Every `consensus_t*.geojson` in the committed directory
  against its rebuild: bytes, then parsed JSON (every feature's coordinates and
  properties, in order), plus `total_passes` and every threshold count in
  `voting_summary.json`. A pool is exact only if all of these agree. A
  difference is sized by feature counts, multiset identity, and the largest
  nearest-neighbour offset in EPSG:32635.
- **Validation of the procedure.** The same rebuild on the 26 K = 1 and K = 3
  pools (`consensus-n1`, `consensus-n3`, written 2026-09-12 with pass
  provenance) must reproduce them and read exactly the files, with the blob
  hashes, that their `voting_summary.json` records.

### 3.2 Result

| Merger | K = 1 | K = 3 | K = 5 | K = 10 |
|---|---|---|---|---|
| `362f1a305` (name order) | 13 of 13 exact | 13 of 13 exact | 13 of 13 exact | 13 of 13 exact |
| branch (numeric order) | 13 of 13 exact | 13 of 13 exact | 13 of 13 exact | **0 of 13** |

Under `362f1a305` all 195 threshold files of the 26 target pools are
byte-identical, as are the 52 of the 26 validation pools (247 across both
groups), and all 26 validation pools read exactly their recorded passes. Under the current merger
every K = 10 pool differs. At `consensus_t1` the feature counts differ by 0 to
9, and dozens of features have no partner within 1 m (for example HIGH text
T 0.7: 5,866 committed against 5,858 rebuilt, with 176 and 168 unmatched);
`out/rebuild_pools.json` → `rows[].differences` lists each. This confirms
the union-staleness retrospective's § 7 note: these unions are not stale, but
any re-derivation must pin name order.

**What an exact rebuild establishes (revised 2026-10-10, Astra's review).** It
establishes a reproducible forward construction: these pass files, read in
this order by this merger, produce the committed directory byte for byte. It
does not establish a unique inverse history. The merger consumes features, so
two pass histories that differ only where no pass found a candidate (in
particular, which zero-detection tiles each pass processed) yield the same
consensus and the same counts, but not the same assessed area. The numeric
rebuild shows the merger is order-sensitive at K = 10. It does not show that
every other pass history would be distinguishable. The declarations therefore
rest on the forward construction together with the historical evidence: the
first-N rule in the script that wrote the pools, the single 2026-04-17 commit
of each directory, and Astra's check that every declared input had its
declared blob at each pool's addition commit. They are named as
evidence-cited retrospective declarations, not proofs of uniqueness.

### 3.3 Declarations

Each of the 26 target pools is declared with the pass list the April rebuild
read (`pass_id`, `path`, `git_blob_hash`), `clip: null` (`merge_passes.py`
applies none), the builder command, and evidence naming the committing commit,
the rebuild, both merger verdicts and this script. The library treats the list
exactly like recorded pass provenance, after checking each file's blob hash
(`area_from_declared_passes`, commit `283d2626c`). The T 0.7 pools' passes
resolve their tiling through Task A's declarations. Declarations are written
by `write_declarations.py` and committed in `3a8fca8f5`; PR #26's three
declarations are unchanged.

**Pins (added 2026-10-10, Astra's review, finding 2).** The pass hashes alone
did not bind a declaration to the consensus it was checked against: a K = 1
or differently clipped union written over the declared path, with every pass
file intact, kept the declared K = 10 area. A smaller candidate set cannot
contradict a larger declared area through the candidates-inside check. Each
pool declaration now records the blob hash of its consensus
(`pool_git_blob_hash`). Every declaration, the three of PR #26 and the four
declared tilings included, also pins each other file its area is read from
(`inputs`: pass metas, tile manifests and polygons, footprint and clip
polygons). The library checks both before applying a declaration
(`check_declaration_pins`), and a change to any of them makes the area
undetermined. The declarations were regenerated by `write_declarations.py`
from the committed outputs and files, without re-running the rebuild. Their
content is otherwise unchanged. All 294 pinned files equal both
`git hash-object` and the blob committed at `HEAD` (`out/declaration_pins.json`).

## 4. Validation

1. **The declared routes reproduce the recorded areas** (`out/gate_survey.json`
   → `validation`). For the 18 K = 1 and K = 3 pools of the nine ladders whose
   rungs the gate determined before D57 (eight pv-diag-384 and
   `scale-4-optimal-487`), the area was computed twice. Once through recorded
   provenance (meta manifests and `voting_summary.json`). Once with the meta
   reader disabled (`pass_manifest` returns nothing), from a scratch file
   holding the tilings check 5 identified and the pool lists the rebuild read.
   **18 of 18 agree exactly** (symmetric difference 0.0 km²; method
   `pass-provenance` against `declared`). The T 0.7 rungs are excluded, since
   their areas now rest on Task A itself.
2. **Check 5 names the recorded tiling.** On the 27 K = 1 and K = 3 passes of
   those nine ladders, `.tiles.json` completed ∪ failed, restricted to tilings
   that existed at the writer commit, names exactly the manifest the meta
   records, **27 of 27** (`out/t07_tilings.json` → `validation`). Checks 2–4
   are specific to the March batch runner and are not validated there.
3. **An independent area recomputation agrees** (`independent`). For all 52
   rungs of the thirteen pv-diag-384 ladders, the union of the 487-tile
   polygons of every tile any of the rung's first K passes processed,
   intersected with the board frame and computed without the library, equals
   the gate's effective area to 4 dp: **52 of 52**.
4. **Unclipped scores reproduce the committed ones.** All 44 points scored in
   Task C equal their committed F1 at 4 dp under the branch's scorer
   (`out/clip_cost.json`, `committed_f1_20` against `unclipped.f1`).
5. **Tests.** Nine new tier-1 tests in `tests/test_assessed_area.py` (37 in
   the file) cover the declared tiling, the refusal of a processed tile
   outside the declared manifest, the blob anchor (tiling and pool), a meta
   contradicting a declaration, a pass declared twice, a declaration naming
   two routes, and the declared pool route. A tier-2 module,
   `tests/test_assessed_area_declarations_committed.py` (35 tests), re-checks
   every committed declaration against the data and the four T 0.7 verdicts.
   Both pass on sapphire. The full tier-1 suite passes (4,160 passed,
   5 skipped, 3 xfailed).
6. **Red sentinel** (`red_sentinel.py`, `out/red_sentinel.json`). It runs on a
   `git archive` copy of `94a9e5cc7` with no symlinks, green before and after.
   Six mutations to `lib_assessed_area.py` (declarations never consulted, the
   outside-manifest check off, the blob check off, a meta conflict ignored,
   duplicates allowed, two routes allowed) **each turn their named test(s)
   red**.

## 5. The gate survey, before → after

The gate runs as `build_k_ladder_phase2_tables.py` would: `build()`, then
`apply_area_gate`, unclipped, undetermined rungs allowed, one ladder at a time
(`gate_survey.py`). "Before" uses PR #26's declarations file at `842f9e92a`
with this branch's code, and reproduces PR #26's committed survey on every
ladder (status and excess).

| Ladder (proposer pool) | PR #26 survey | After D57 (3) | Rung methods after (K = 1 / 3 / 5 / 10) |
|---|---|---|---|
| `flash-minimal-text-n30-t07-text-t0.3` | refused, 2.0819 km² | refused, 2.0819 km² | pass-provenance / pass-provenance / declared / declared |
| `flash-minimal-text-n30-t07-text-t0.7` | undetermined | same | pass-provenance / pass-provenance / declared / declared |
| `flash-minimal-text-n30-t07-text-t1.0` | refused, 2.0893 km² | refused, 2.0893 km² | pass-provenance / pass-provenance / declared / declared |
| `flash-high-text-n5-text-t0.3` | undetermined | same | pass-provenance / pass-provenance / declared / declared |
| `flash-high-text-n5-text-t0.7` | undetermined | same | pass-provenance / pass-provenance / declared / declared |
| `flash-high-text-n5-text-t1.0` | refused, 4.7609 km² | refused, 4.7609 km² | pass-provenance / pass-provenance / declared / declared |
| `image-n5-image-t0.3` | undetermined | **refused, 2.0998 km²** | pass-provenance / pass-provenance / declared / declared |
| `image-n5-image-t0.7` | undetermined | **refused, 2.4289 km²** | pass-provenance / pass-provenance / declared / declared |
| `image-n5-image-t1.0` | refused, 2.4289 km² | refused, 2.4289 km² | pass-provenance / pass-provenance / declared / declared |
| `flash-high-image-n5-image-t0.3` | undetermined | same | pass-provenance / pass-provenance / declared / declared |
| `flash-high-image-n5-image-t0.7` | undetermined | same | pass-provenance / pass-provenance / declared / declared |
| `flash-high-image-n5-image-t1.0` | undetermined | same | pass-provenance / pass-provenance / declared / declared |
| `scale-4-optimal-487` | undetermined | same | pass-provenance / pass-provenance / declared / declared |
| `g384_ov192_g37` (3.7 GS) | refused, 37.9354 km² | refused, 37.9354 km² | pass-provenance / pass-provenance / declared / declared |

For the four T 0.7 ladders "pass-provenance" at K = 1 and 3 means recorded pass
provenance whose passes take their tiling from Task A's declarations.

## 6. Task C: the cost of the clip

### 6.1 Method

`clip_cost.py` takes every pv-diag-384 ladder the gate refuses after A and B:
the four of PR #26 § 5.6, plus MINIMAL image T 0.7 and T 0.3. The 3.7 GS
ladder is excluded, because its clip was measured under D51 (PR #26 § 5.3).
The common area is the gate's own (`compare_assessed_areas`, clip and
undetermined allowed); for these ladders it is the K = 1 area, or K = 1–5 for
image T 0.3. Each rung's opmax point (and its stride-shell carried point,
where distinct) is scored on the board frame
(`era2_b_intersection_bounds`) at 20 m with the branch's scorer, three ways:

- **(i) unclipped**: the committed detections;
- **(ii) clipped**: detections outside the common area removed, the frame and
  its reference set kept (D51 option 1, as
  `--clip-to-common-area --allow-undetermined-area` computes);
- **(iii) gap removed**: sensitivity. Every frame tile polygon is intersected
  with the common area, so references in the gap leave the frame along with the
  detections.

TP, FP and FN come from the scorer's own per-sheet loop, checked against
`calculate_f1_internal` on every call. "Gap mounds found" counts the
references inside the gap (frame minus common area) that a rung matched in (i).

### 6.2 The gaps

| Ladder | Common area (km²) | Gap (km²) | Gap tile(s) | Reference mounds in the gap |
|---|---:|---:|---|---:|
| MINIMAL text T 0.3 | 1400.3248 | 2.0819 | `K-35-053-3_Elenovo_x336_y2016.png` | 0 |
| MINIMAL text T 1.0 | 1400.3175 | 2.0893 | `K-35-062-2_Rakovski_x3360_y2688.png` | 0 |
| HIGH text T 1.0 | 1397.6458 | 4.7609 | `K-35-052-4_32635_x4032_y336.png`, `K-35-062-2_Rakovski_x1680_y0.png`, `K-35-078-1_Lesovo_x1008_y2016.png` | 3 (all in `Rakovski_x1680_y0`) |
| MINIMAL image T 0.3 | 1400.3069 | 2.0998 | `K-35-078-1_Lesovo_x2352_y3024.png` (K = 10 only) | 0 |
| MINIMAL image T 0.7 | 1399.9778 | 2.4289 | `K-35-053-3_Elenovo_x1344_y672.png` | 2 |
| MINIMAL image T 1.0 | 1399.9778 | 2.4289 | `K-35-053-3_Elenovo_x1344_y672.png` | 2 |

### 6.3 Results at the committed opmax point

Values are (i) unclipped / (ii) clipped / (iii) gap removed. The last column
gives the estimate's linear ΔF1 for (ii) against the measured one.

| Ladder | K | Gap mounds found | F1 | P | R | Tile MCC | ΔF1 (ii): estimate / measured |
|---|---:|---:|---|---|---|---|---|
| MINIMAL text T 0.3 | 1 | 0 of 0 | 0.8555 / 0.8555 / 0.8555 | 0.8826 / 0.8826 / 0.8826 | 0.8299 / 0.8299 / 0.8299 | 0.7986 / 0.7986 / 0.7986 | +0.0000 / +0.0000 |
| MINIMAL text T 0.3 | 3 | 0 of 0 | 0.8708 / 0.8708 / 0.8708 | 0.9077 / 0.9077 / 0.9077 | 0.8368 / 0.8368 / 0.8368 | 0.8040 / 0.8040 / 0.8040 | +0.0000 / +0.0000 |
| MINIMAL text T 0.3 | 5 | 0 of 0 | 0.8778 / 0.8778 / 0.8778 | 0.9069 / 0.9069 / 0.9069 | 0.8506 / 0.8506 / 0.8506 | 0.7735 / 0.7735 / 0.7735 | +0.0000 / +0.0000 |
| MINIMAL text T 0.3 | 10 | 0 of 0 | 0.8730 / 0.8730 / 0.8730 | 0.8770 / 0.8770 / 0.8770 | 0.8690 / 0.8690 / 0.8690 | 0.7910 / 0.7910 / 0.7910 | +0.0000 / +0.0000 |
| MINIMAL text T 1.0 | 1 | 0 of 0 | 0.8235 / 0.8235 / 0.8235 | 0.8434 / 0.8434 / 0.8434 | 0.8046 / 0.8046 / 0.8046 | 0.8095 / 0.8095 / 0.8095 | +0.0000 / +0.0000 |
| MINIMAL text T 1.0 | 3 | 0 of 0 | 0.8647 / 0.8647 / 0.8647 | 0.9025 / 0.9025 / 0.9025 | 0.8299 / 0.8299 / 0.8299 | 0.8040 / 0.8040 / 0.8040 | +0.0000 / +0.0000 |
| MINIMAL text T 1.0 | 5 | 0 of 0 | 0.8714 / 0.8714 / 0.8714 | 0.9037 / 0.9037 / 0.9037 | 0.8414 / 0.8414 / 0.8414 | 0.7797 / 0.7797 / 0.7797 | +0.0000 / +0.0000 |
| MINIMAL text T 1.0 | 10 | 0 of 0 | 0.8781 / 0.8781 / 0.8781 | 0.9049 / 0.9049 / 0.9049 | 0.8529 / 0.8529 / 0.8529 | 0.7881 / 0.7881 / 0.7881 | +0.0000 / +0.0000 |
| HIGH text T 1.0 | 1 | 0 of 3 | 0.7810 / 0.7810 / 0.7837 | 0.7672 / 0.7672 / 0.7672 | 0.7954 / 0.7954 / 0.8009 | 0.8162 / 0.8162 / 0.8162 | +0.0000 / +0.0000 |
| HIGH text T 1.0 | 3 | 3 of 3 | 0.8541 / 0.8501 / 0.8531 | 0.8673 / 0.8663 / 0.8663 | 0.8414 / 0.8345 / 0.8403 | 0.7986 / 0.7948 / 0.7948 | −0.0040 / −0.0040 |
| HIGH text T 1.0 | 5 | 3 of 3 | 0.8688 / 0.8648 / 0.8678 | 0.8779 / 0.8771 / 0.8771 | 0.8598 / 0.8529 / 0.8588 | 0.7857 / 0.7819 / 0.7819 | −0.0039 / −0.0040 |
| HIGH text T 1.0 | 10 | 3 of 3 | 0.8804 / 0.8765 / 0.8795 | 0.8897 / 0.8889 / 0.8889 | 0.8713 / 0.8644 / 0.8704 | 0.7910 / 0.7872 / 0.7872 | −0.0039 / −0.0039 |
| MINIMAL image T 0.3 | 1 | 0 of 0 | 0.7680 / 0.7680 / 0.7680 | 0.7636 / 0.7636 / 0.7636 | 0.7724 / 0.7724 / 0.7724 | 0.8443 / 0.8443 / 0.8443 | +0.0000 / +0.0000 |
| MINIMAL image T 0.3 | 3 | 0 of 0 | 0.7774 / 0.7774 / 0.7774 | 0.8157 / 0.8157 / 0.8157 | 0.7425 / 0.7425 / 0.7425 | 0.8178 / 0.8178 / 0.8178 | +0.0000 / +0.0000 |
| MINIMAL image T 0.3 | 5 | 0 of 0 | 0.7767 / 0.7767 / 0.7767 | 0.8034 / 0.8034 / 0.8034 | 0.7517 / 0.7517 / 0.7517 | 0.8416 / 0.8416 / 0.8416 | +0.0000 / +0.0000 |
| MINIMAL image T 0.3 | 10 | 0 of 0 | 0.7819 / 0.7819 / 0.7819 | 0.8119 / 0.8119 / 0.8119 | 0.7540 / 0.7540 / 0.7540 | 0.8377 / 0.8377 / 0.8377 | +0.0000 / +0.0000 |
| MINIMAL image T 0.7 | 1 | 0 of 2 | 0.7252 / 0.7252 / 0.7269 | 0.7108 / 0.7108 / 0.7108 | 0.7402 / 0.7402 / 0.7436 | 0.8437 / 0.8437 / 0.8477 | +0.0000 / +0.0000 |
| MINIMAL image T 0.7 | 3 | 2 of 2 | 0.7599 / 0.7570 / 0.7588 | 0.7707 / 0.7696 / 0.7696 | 0.7494 / 0.7448 / 0.7483 | 0.8377 / 0.8339 / 0.8376 | −0.0029 / −0.0029 |
| MINIMAL image T 0.7 | 5 | 2 of 2 | 0.7734 / 0.7705 / 0.7723 | 0.7862 / 0.7852 / 0.7852 | 0.7609 / 0.7563 / 0.7598 | 0.8383 / 0.8345 / 0.8382 | −0.0029 / −0.0029 |
| MINIMAL image T 0.7 | 10 | 2 of 2 | 0.7881 / 0.7852 / 0.7871 | 0.8173 / 0.8164 / 0.8164 | 0.7609 / 0.7563 / 0.7598 | 0.8223 / 0.8185 / 0.8221 | −0.0029 / −0.0029 |
| MINIMAL image T 1.0 | 1 | 0 of 2 | 0.7044 / 0.7044 / 0.7060 | 0.6817 / 0.6817 / 0.6817 | 0.7287 / 0.7287 / 0.7321 | 0.8360 / 0.8360 / 0.8398 | +0.0000 / +0.0000 |
| MINIMAL image T 1.0 | 3 | 0 of 2 | 0.7288 / 0.7288 / 0.7305 | 0.7382 / 0.7382 / 0.7382 | 0.7195 / 0.7195 / 0.7229 | 0.8178 / 0.8178 / 0.8215 | +0.0000 / +0.0000 |
| MINIMAL image T 1.0 | 5 | 0 of 2 | 0.7384 / 0.7384 / 0.7403 | 0.8104 / 0.8104 / 0.8104 | 0.6782 / 0.6782 / 0.6813 | 0.8021 / 0.8021 / 0.8056 | +0.0000 / +0.0000 |
| MINIMAL image T 1.0 | 10 | 0 of 2 | 0.7428 / 0.7428 / 0.7446 | 0.7783 / 0.7783 / 0.7783 | 0.7103 / 0.7103 / 0.7136 | 0.8078 / 0.8078 / 0.8114 | +0.0000 / +0.0000 |

The stride-shell carried points (`out/summary.md`, second table) follow the
same pattern. HIGH text T 1.0 loses −0.0042 at K = 5 and K = 10 and nothing at
K = 3, where the carried vote threshold (3) exceeds the 2 of 3 passes that
processed the gap tiles. MINIMAL image T 0.7 loses −0.0031 at K = 10 (vote
threshold 8, gap tile processed by 8 of 10 passes). It loses nothing at K = 3
or K = 5, where its thresholds (3 and 4) exceed the passes that processed the
tile (2 of 3, 3 of 5; § 6.6).

### 6.4 The gains

| Ladder | Gain (opmax) | (i) unclipped | (ii) clipped | (iii) gap removed |
|---|---|---:|---:|---:|
| MINIMAL text T 0.3 | K = 1 → K = 3 / K = 10 | +0.0154 / +0.0175 | +0.0154 / +0.0175 | +0.0154 / +0.0175 |
| MINIMAL text T 1.0 | K = 1 → K = 3 / K = 10 | +0.0411 / +0.0546 | +0.0411 / +0.0546 | +0.0411 / +0.0546 |
| HIGH text T 1.0 | K = 1 → K = 3 / K = 10 | +0.0731 / +0.0993 | +0.0691 / +0.0954 | +0.0694 / +0.0958 |
| MINIMAL image T 0.3 | K = 1 → K = 3 / K = 10 | +0.0094 / +0.0139 | +0.0094 / +0.0139 | +0.0094 / +0.0139 |
| MINIMAL image T 0.7 | K = 1 → K = 3 / K = 10 | +0.0347 / +0.0629 | +0.0318 / +0.0600 | +0.0319 / +0.0602 |
| MINIMAL image T 1.0 | K = 1 → K = 3 / K = 10 | +0.0243 / +0.0383 | +0.0243 / +0.0383 | +0.0244 / +0.0386 |

The clip (ii) and the sensitivity (iii) agree on every gain to within 0.0004.
Under (iii) the K = 1 rung rises as well, because its unfound gap mounds stop
counting as misses. That is the "building in misses" the PI asked about: under
(ii) it lowers the higher rungs by up to 0.0040 and leaves K = 1 untouched.

### 6.5 The estimate, tested

D57 (2) estimated each mound a higher rung found in the gap and loses at about
(2 − F1)/(2TP + FP + FN), at most about 0.004 F1 (3 mounds) and 0.003 (2
mounds), nothing on K = 1, and only false positives removed where the gap
holds no mound.

- **The per-mound cost holds.** At every one of the nine points that lose
  detections, the linear estimate with the rung's own counts matches the
  measured ΔF1 to within 0.00002 (`out/clip_cost.json` → `estimate`). The cost
  per mound is 0.0013–0.0016. Every removed detection is a gap mound's TP; the
  clip removed no FP anywhere.
- **3 mounds, about 0.004: holds.** HIGH text T 1.0: −0.0040 / −0.0040 /
  −0.0039 at opmax; −0.0042 at the carried K = 5 and 10.
- **2 mounds, about 0.003: holds, but on the other ladder.** MINIMAL image
  T 0.7, newly refused, loses −0.0029 (opmax) and −0.0031 (carried K = 10).
  **MINIMAL image T 1.0, the ladder the estimate named, loses nothing: none of
  its rungs found either gap mound** (§ 6.6).
- **Nothing on K = 1: holds by construction.** K = 1's area is the common
  area, so the clip removes none of its detections.
- **Zero-mound gaps remove only false positives: they remove nothing.** No
  committed point of MINIMAL text T 0.3, MINIMAL text T 1.0 or MINIMAL image
  T 0.3 has a detection in its gap, so (i), (ii) and (iii) are identical there.

### 6.6 Why some gap mounds are never found (surprising)

A gap lies in a tile's unshared part, so only passes that processed that tile
can vote for a mound there; a candidate's vote count cannot exceed that number.
The rebuild record gives, for each rung, how many of its passes processed each
gap tile (`out/summary.md`, "passes that processed each gap tile"):

| Ladder | Gap tile | K = 1 | K = 3 | K = 5 | K = 10 | opmax vote threshold (K = 3 / 5 / 10) |
|---|---|---|---|---|---|---|
| HIGH text T 1.0 | each of its three | 0 of 1 | 2 of 3 | 4 of 5 | 9 of 10 | 2 / 3 / 5 |
| MINIMAL image T 0.7 | `Elenovo_x1344_y672` | 0 of 1 | 2 of 3 | 3 of 5 | 8 of 10 | 2 / 3 / 6 |
| MINIMAL image T 1.0 | `Elenovo_x1344_y672` | 0 of 1 | 1 of 3 | 1 of 5 | 2 of 10 | 2 / 4 / 6 |
| MINIMAL image T 0.3 | `Lesovo_x2352_y3024` | 0 of 1 | 0 of 3 | 0 of 5 | 4 of 10 | 3 / 4 / 7 |
| MINIMAL text T 0.3 | `Elenovo_x336_y2016` | 0 of 1 | 1 of 3 | 1 of 5 | 4 of 10 | 2 / 3 / 3 |

MINIMAL image T 1.0's gap tile was processed by only 2 of its 10 passes (runs
2 and 8), below every rung's opmax vote threshold, so its two gap mounds could
not be reported and the clip has nothing to remove. In run 1, the meta records
a JSON parse error for that tile (illegal trailing comma); the other runs'
reasons were not tallied. The same tile is also missing from runs 1 and 5 at
T 0.7 and runs 2 and 3 at T 0.3. **This is a second, quieter area effect the
D51 gate does not see.** The gate compares the union of a pool's processed
tiles, but within a pool a tile that only some passes processed caps every
vote count there. The K = 10 rung of MINIMAL image T 1.0 "assessed"
`Elenovo_x1344_y672` by the gate's definition, yet could not report a mound in
it at its operating point. This is flagged for the PI; it is not addressed
here.

## 7. Surprises, collected

1. **MINIMAL image T 0.3 is refused** once its K = 10 pool is determinable
   (§ 1, § 5), on a tile six of its first ten passes skipped. Its gap holds no
   mound and the clip changes nothing.
2. **The 2-mound cost lands on MINIMAL image T 0.7, not T 1.0** (§ 6.5), and
   within-pool partial coverage, not the clip, is why T 1.0 never found them
   (§ 6.6).
3. **The current merger reproduces none of the 13 K = 10 pools** (§ 3.2). The
   numbers are not stale, but any re-derivation must pin name order.
4. **A second registered tiling has the same 487 names** (§ 2.3), harmless here
   because its polygons are identical and it postdates the passes.
5. **Run 5 of MINIMAL image T 0.7 skipped the gap tile too** (§ 2.3). D57's
   premise check covered runs 1–3 only.

## 8. Limits and what is not settled

- **Point estimates only.** No bootstrap interval or permutation test was
  recomputed for the clipped points.
- **The tile MCC under (iii) is a sensitivity on clipped tile polygons.** A gap
  tile keeps its shared strips, and with them any reference there. HIGH text
  T 1.0's `Rakovski_x1680_y0` holds a fourth reference outside the gap, so
  under (iii) the tile stays "has mounds" and its MCC equals (ii)'s
  (`gap_tile_confusion` in `out/clip_cost.json`).
- **The declared tilings cover runs 1–10 only**, the passes any K ≤ 10 rung
  uses. Runs 11–30 of the two 30-pass text cells are undeclared; the K = 30
  unions are not Phase 2 rungs.
- **The presumed-pass rule is checked against the committed bytes, not
  assumed, but the check is one-directional** (revised 2026-10-10). Every
  pool's rebuild from its presumed passes matched exactly. A pool built from
  other passes would usually not have matched, as the numeric order did not at
  K = 10. Passes differing only where none found a candidate would have, with a
  different assessed area (§ 3.2). The declarations rest on the forward
  construction and the historical evidence together.
- **The coverage record is scoped to unpatched passes** (§ 2.2). Patched files
  and other campaigns need their sidecars checked first.
- **D57 (4), the re-score, is not done.** The builder (`phase2/ladders.json`)
  will now refuse seven ladders unless run with `--clip-to-common-area`. With
  every rung determined, `--allow-undetermined-area` is no longer needed for
  the pv-diag-384 ladders.
- **§ 6.6's partial-coverage effect is unquantified** beyond the six refused
  ladders' gap tiles. A rule for it, if one is wanted, is a question for the PI.

## 9. How to check

Commits on `d51-ladder-provenance`: `283d2626c` (library and tier-1 tests),
`3b4c7e58d` (Task A/B scripts), `3a8fca8f5` (declarations and tier-2 test),
`94a9e5cc7` (survey, Task C, sentinel and summary scripts, Task A/B outputs).
Task A/B outputs were produced at `3b4c7e58d`; the survey, Task C and the
sentinel at `94a9e5cc7` (`run_c.log`: `head 94a9e5cc7`). On sapphire, with
`W` the worktree at that head, `S` the scratch directory, `D` the scripts
directory and `PY` `~/Code/map-reader-llm/.venv/bin/python`:

```bash
PYTHONDONTWRITEBYTECODE=1 "$PY" "$D/t07_tilings.py" --code "$W" \
    --out "$S/out/t07_tilings.json" --validation-declarations "$S/validation-tilings.json"
PYTHONDONTWRITEBYTECODE=1 "$PY" "$D/rebuild_pools.py" --code "$W" \
    --scratch "$S/rebuilds" --out "$S/out/rebuild_pools.json" --workers 10
"$PY" "$D/write_declarations.py" --repo "$W" \
    --tilings "$S/out/t07_tilings.json" --pools "$S/out/rebuild_pools.json" \
    --pins-out "$S/out/declaration_pins.json"
git -C "$W" show 842f9e92a:inputs/provenance/assessed-area-declarations.json \
    > "$S/base-declarations.json"
PYTHONDONTWRITEBYTECODE=1 "$PY" "$D/gate_survey.py" --code "$W" \
    --base-declarations "$S/base-declarations.json" \
    --validation-tilings "$S/validation-tilings.json" \
    --rebuild "$S/out/rebuild_pools.json" --out "$S/out/gate_survey.json"
PYTHONDONTWRITEBYTECODE=1 "$PY" "$D/clip_cost.py" --code "$W" \
    --survey "$S/out/gate_survey.json" --out "$S/out/clip_cost.json"
"$PY" "$D/red_sentinel.py" --worktree "$W" --scratch "$S" --out "$S/out/red_sentinel.json"
python3 "$D/summarise.py" --out-dir "$D/out" --repo "$W"
PYTHONDONTWRITEBYTECODE=1 "$PY" -m pytest -q tests/test_assessed_area.py \
    tests/test_assessed_area_declarations_committed.py
```

What each check would have shown if a claim were false:

- **A wrong tiling:** check 5 fails (completed ∪ failed ≠ manifest), or the
  tier-2 test does.
- **A wrong pass list or merge order:** the April rebuild differs, as the
  numeric-order one does at K = 10, except for a pass list differing only
  where no pass found a candidate, which no rebuild can detect (§ 3.2).
- **A pool or tiling rewritten after its declaration:** the pins refuse it
  (§ 3.3; tier-1 mutation tests in `tests/test_assessed_area.py`).
- **A library error in the declared routes:** the 18 validation areas or the
  52 independent areas disagree.
- **A scorer or loader difference:** an unclipped score departs from its
  committed F1.
- **Tests that cannot fail:** the red sentinel stays green.

The rebuilt directories (260 MB, both mergers) and every log stay on sapphire
in `~/scratch/d51-ladder-provenance-2026-10-08/`. The first, identical rebuild
run is kept beside them as `rebuilds-first-run/`; its verdict table equals the
committed one.

## Changelog

### 2026-10-10 — Astra's review: file total, inverse provenance, coverage scope, pins

Trigger: Astra's cross-vendor source review of `1fc1f72df` (agent mail of
2026-10-09, findings 2 and 3); the PI asked for the fixes on 2026-10-10.

| Claim | Before | After |
|---|---|---|
| Threshold files byte-identical under the April merger (§ 1, § 3.2) | 247, attached to the 26 target pools | 195 for the 26 target pools, 52 for the 26 validation pools, 247 across both |
| What an exact rebuild shows (§ 1, § 3.2, § 8, § 9) | a wrong pass list or order would have produced a different rebuild | a reproducible forward construction, not a unique inverse history |
| `processed_tiles` as the coverage record (§ 2.2) | stated without scope | scoped to unpatched passes; all 130 declared pass files checked unpatched |
| Declarations (§ 3.3) | pass blob hashes only | the consensus blob hash and every input pinned: 294 files, each equal to `git hash-object` and to `HEAD` |

Not changed: every gate verdict (7 refused, 7 the same, 0 undetermined),
every area, every Task C number, the pool-level rebuild verdicts (26 of 26
exact under the April merger, 0 of 13 K = 10 pools under the current one),
and the declared pass lists and tilings. A re-run of the gate survey on
sapphire with the pinned declarations reproduced the committed "after"
survey on all fourteen ladders (the PR records the run).

Code and data: `scripts/lib_assessed_area.py` (`declaration_inputs`,
`pin_declaration`, `check_declaration_pins`, `tiling_inputs`; the declared
routes check the pins), `rebuild_pools.py` (`declaration` records the
consensus hash), `write_declarations.py` (pins every entry and checks each
pin against git), `inputs/provenance/assessed-area-declarations.json`
(regenerated), `out/declaration_pins.json` (new), and the tests. Landed in
the commits on `d51-ladder-provenance-fixes` that add this entry.

### 2026-10-08 — Original publication

First version: Tasks A–C of D57 (2) and (3) on branch `d51-ladder-provenance`.
Code `283d2626c`, declarations `3a8fca8f5`, scripts and outputs `3b4c7e58d` and
`94a9e5cc7`; this report and `out/summary.md` in the commit that adds them.
