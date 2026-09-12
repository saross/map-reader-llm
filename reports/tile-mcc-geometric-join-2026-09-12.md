# The tile join: making it geometric, and what that costs

> **Last revised**: 2026-09-12 (original publication — the response to the
> PI's 2026-09-12 ruling on `reports/k-ladder-phase2-deltas-2026-09-12.md`
> § 6.3). See [§ Changelog](#changelog).

## 0. Headline, and a STOP

The PI ruled on 2026-09-12: **make the tile assignment geometric, re-score
the three withheld cells, and generalise the solution so this class of
error cannot recur.** Two of the three are done. The middle one is
**stopped and put back**, because the premise it rested on turns out to be
false.

| Ruling | State |
|---|---|
| Generalise so the error cannot recur | **Done.** One named join at one place, and an invariant that refuses a confusion the frame's geometry contradicts. Three separate copies of the string join removed. |
| Make the assignment geometric | **Implemented, not defaulted.** Available as `--tile-join geometric-primary` / `geometric-contains`; the default is still `id`. |
| Re-score the three withheld cells | **STOPPED.** Their geometric MCC is computed and reported below under both variants, but not written into `findings.md`, because it cannot be written without choosing a variant, and choosing a variant moves all 146 other cells too. |

**Why the stop.** The ruling and the brief both state that a geometric
join must reproduce the string join wherever the vocabulary matches —
"same tiles, same points" — and that any difference is a stop-and-report.
Measured over all 149 committed cells of the signed Era-2 board and the
K-ladder Phase 2 run: **it does not reproduce, on any of them, by a wide
margin.**

| | mean Δ MCC vs `id` | median | range | higher on |
|---|---:|---:|---|---:|
| `geometric-primary` | **+0.1059** | +0.1089 | +0.0478 … +0.1472 | **146 of 146** |
| `geometric-contains` | **+0.0754** | +0.0770 | −0.0011 … +0.1190 | **145 of 146** |

Anchor: `results/tile-join-audit/board-era2-2026-09-12.json` and
`results/tile-join-audit/k-ladder-phase2-cells-2026-09-12.json`, both by
`scripts/audit_tile_join_variants.py` on sapphire.

**The reason is that the evaluation frames overlap, and nobody's
assumption accounted for it.**
`inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` holds 384 px
tiles on a 336 px stride: tile width 1923.84 m against a 1686.33 m stride,
so neighbours overlap by 237.51 m and the sum of the 487 tile areas is
**1.2783x** the area of their union. A **median 30.6 %** of a cell's
detections (range 24.4–45.4 %) therefore lie inside **more than one** frame
tile, and "the frame tile whose polygon contains this point" is not a
well-defined thing. There is no single geometric join; there are two
defensible ones, and they differ from each other by 0.02–0.05 MCC.

So the choice is not between a broken join and a correct one. It is
between three different metrics:

- **`id`** answers *did the model, when shown tile T, report a mound?* — a
  question about exposure. Well defined only when the cell's proposer
  tiling **is** the scoring frame.
- **`geometric-primary`** answers *is T the nearest-centroid tile of a
  detection?* — one tile per detection, so the per-tile TP/FP/FN totals are
  preserved exactly (see § 4.3), but a tile can hold a detection without
  being credited with it.
- **`geometric-contains`** answers *does T contain a detection?* — symmetric
  with the reference side's long-standing rule, at the cost of
  double-counting a detection across every overlapping tile that holds it.

Adopting either geometric variant would move every MCC in the committed
corpus upward by roughly a tenth, including 103 cells of a board signed on
2026-09-12, and would make that board's own confusion gate fail on all of
them. That is a methodological decision with the PI's name on it, not a
bug fix, so the default was left where it reproduces published numbers and
the question is put in § 6.

**What was nonetheless made safe.** The silent failure is gone. The scorer
now refuses to emit an MCC whose join the frame's geometry contradicts, so
the 0.1337-beside-0.8495 outcome cannot recur under any join, default
included.

## 1. The join sites

Every place in `scripts/` that turns a detection or a reference mound into
a tile for the purpose of a per-tile confusion, a per-tile count table, or
a tile-keyed array. "Vocabulary-exposed" means the site consumes a tile
**name** that came from somewhere other than the bounds file it then
iterates over, so the join can silently mismatch.

| # | Site | What it joins | Rule before | Exposed? | Feeds |
|---:|---|---|---|:---:|---|
| 1 | `lib_advanced_metrics.py:2512` `calculate_tile_classification` | detections → frame tiles; references → frame tiles | **detections by `source_tile` STRING; references by `intersects` geometry** | **YES** | tile-MCC, sensitivity, specificity, every `tile_classification` block in every committed evaluation |
| 2 | `lib_advanced_metrics.py:1019` `compute_per_tile_tp_fp_fn` | TPs and FPs → the detection's tile; FNs → the reference's primary tile | **TP/FP by `source_tile` STRING; FN by nearest-centroid geometry** | **YES** | per-tile bootstrap CIs for F1, and the pairwise permutation tests' F1 arm |
| 3 | `lib_advanced_metrics.py:1239` `compute_per_tile_classification` | thin per-tile view of site 1 | inherits site 1 | inherits | the MCC arm's per-tile swap masks |
| 4 | `lib_advanced_metrics.py` `bootstrap_tile_classification_ci` | resamples site 1's labels | inherits site 1 | inherits | tile-MCC / sensitivity / specificity BCa CIs |
| 5 | `lib_advanced_metrics.py` `bootstrap_tile_effect_size_ci` | site 1 on two conditions | inherits site 1 | inherits | paired tile-MCC effect sizes |
| 6 | `lib_advanced_metrics.py` `score_detection_set` | site 1, point estimate only | inherits site 1 | inherits | every sweep and operating-point grid that ranks on MCC |
| 7 | `mcc_tiering_55map.py:143` `tile_vectors` | **an independent second copy** — `pred` from `source_tile` names, `truth` from geometry | **own STRING join** | **YES** | the 55-map MCC tiering and its confusion gate |
| 8 | `era1_leaderboard_tiering.py` `cell_per_tile_classification` → `check_confusion_gate` | rebuilds a cell's confusion and compares it with the cell's committed record | inherits site 1 **and gates against itself** | **YES, and blind** | the board's MCC permutation gate — reproduced the same wrong confusion and passed it |
| 9 | `paired_mcc_permutation.py` `aggregate_confusion` → `check_confusion_gate` | same shape as 8, via `compute_per_tile_classification` | inherits site 3 | inherits | the paired-arm MCC permutation gate |
| 10 | `evaluate_detections.py:2191` | writes `source_tile` when absent: `sjoin(intersects)` then `keep="first"` | **a third rule** — arbitrary spatial-index order | n/a (writes) | whatever site 1 later reads |
| 11 | `prepare_h13_scoring.py:287` `assign_primary_tiles` | writes `source_tile`: nearest tile centroid among intersected | geometric, deterministic | n/a (writes) | the materialisation scripts' `source_tile` |
| 12 | `lib_advanced_metrics.py:1491` `calculate_f1_internal` | detections → **map sheets**, to scope the Hungarian match | **`source_tile.str.startswith(map_name)`** — a STRING join | **YES** (§ 5.1a) | **global F1, precision and recall at every buffer** |
| 13 | `augment_per_arch_with_mcc.py:45–48, 141` | picks the frame from an era number | frame selection, not a join | **YES, differently** (§ 5.1b) | MCC + CIs written back into tier JSONs |
| 14 | `pairwise_permutation_test.py` `compute_per_tile_metrics`, `compute_family_fdr.py`, `consensus_vs_baseline_tiering.py`, `build_55map_leaderboard.py` | index a per-tile table by `tile_name` | tile keys derived from the same bounds they iterate | **NO** | tiering, FDR, leaderboards |

Sites 1–9 are now routed through one function; site 10 and site 11 are the
two rules that *write* `source_tile`, and together with a proposer's own
tiling they are why three mutually inconsistent detection→tile rules
already existed in the corpus before any of this. Sites 12 and 13 are
exposed and **not** fixed here — see § 5.1. The census also found roughly a
dozen further reimplementations and propagators downstream of sites 1–9
(published CSV and Markdown renderings, the derived tile-level F1 in
`derive_tile_level_f1.py:202`, the 55-map paired permutations); they inherit
whatever the library does and were not separately audited.

**Site 2 is the finding the ruling did not anticipate: the exposure was
never MCC alone.** Under the string join a vocabulary-mismatched cell
loses **every** TP and FP from the per-tile table (no name matches any
frame tile), leaving a table of pure false negatives with a micro-F1 of
0.0000 — which the per-tile bootstrap CIs and the pairwise permutation
tests would then resample. The three affected cells escaped this only
because `k-ladder-phase2-deltas-2026-09-12.md` § 4 excluded the family from
the permutation testing for an unrelated reason. Verified by running site 2
on `g37-text-k1-verified-opmax`: it now raises, where it previously
returned tp 0 / fp 0 / fn 37.

## 2. The rule, stated once

`lib_advanced_metrics.assign_points_to_tiles` is the single place a point
becomes a tile. Three named rules, `TILE_JOINS`:

| Rule | Candidate tiles | Winner | Tiles per point |
|---|---|---|---:|
| `id` | — geometry not consulted | the tile whose `tile_name` equals the point's `source_tile` | 0 or 1 |
| `geometric-primary` | every tile the point **intersects** | nearest tile centroid; exact ties to the lexicographically smallest `tile_name` | 0 or 1 |
| `geometric-contains` | every tile the point **intersects** | all of them | 0 or more |

**Shared edges.** Candidacy uses `intersects`, not `contains`, so a point
lying exactly on the boundary between two tiles is a candidate for
**both**. `geometric-contains` books it to both; `geometric-primary` books
it to exactly one, and because an edge point is equidistant from two
equal-sized neighbours' centroids, the lexicographic tie-break is what
makes the result deterministic rather than dependent on spatial-index
order. Pinned by `tests/test_tile_join_geometric.py`.

**Points in no tile.** Never booked anywhere. They are excluded from the
confusion and counted in `n_outside_union`, which is reported in the
evaluation's `tile_join_diagnostics`. Across the 146 sound cells this
count is **0**; on the three refused cells it is 27, 27 and 32 — detections
the 3.7 proposer made outside the board frame's footprint entirely.

**Symmetry.** Under either geometric rule the *same* rule is applied to
references as to detections, so the confusion is no longer built one way on
one axis and another way on the other. `id` deliberately keeps the legacy
asymmetric pairing (names for detections, containment for references),
because that pairing is what the committed numbers were made with.

## 3. The invariant

> After assignment, the number of points booked to some tile must equal the
> number of points geometrically inside the frame's tile union.

It holds by construction under both geometric rules. It is exactly what
`id` violates on a vocabulary mismatch. A shortfall aborts the metric with
a named reason — `tile_join_detection_shortfall`,
`tile_join_reference_shortfall`, `detections_have_no_source_tile` — and
returns `{"error", "reason", "tile_join_diagnostics"}` where a number would
have been. `evaluate_detections.py` records that as
`tile_classification.withheld` with the reason, and does not bootstrap
around it.

Enforced at three levels:

1. **The scorer** (`check_tile_join_invariant`, called by
   `calculate_tile_classification`) — no MCC, no CI, no sweep ranking.
2. **The per-tile table** (`compute_per_tile_tp_fp_fn`) — raises, so no
   bootstrap or permutation test receives a truncated table.
3. **The board's confusion gate** (`era1_leaderboard_tiering.check_confusion_gate`,
   new `geometry_check` argument) — fails on a shortfall **even when the
   rebuilt confusion matches the committed record exactly.** This is the
   substantive change: the gate previously rebuilt the confusion by calling
   the same function that produced the committed number, so it could only
   ever confirm that a computation agreed with itself. It now appeals to the
   frame's polygons.

`scripts/check_tile_vocabulary_match.py` is no longer needed for
correctness and is kept as a cheap survey instrument over an
already-scored corpus.

Tier-1 cover, `tests/test_tile_join_geometric.py`, 16 tests: two tile
vocabularies (offset grids) where `id` books nothing and both geometric
rules recover the right confusion; an overlapping frame where all three
rules disagree; the shared-edge rule and its deterministic tie-break; the
no-tile rule, including that an out-of-frame point does **not** trip the
invariant; the invariant firing in the scorer, in the per-tile table, on a
missing `source_tile` column, and in the board gate against a confusion
that reproduces its own record; and an unknown rule name raising rather
than falling back.

## 4. The regression, on the committed corpus

Run on sapphire in an isolated worktree,
`scripts/audit_tile_join_variants.py`, over every committed evaluation the
board reads.

### 4.1 Is the refactor behaviour-preserving?

| corpus | cells | EXACT under `id` | DRIFT | REFUSED |
|---|---:|---:|---:|---:|
| Era-2 board `cells/` | 103 | **103** | 0 | 0 |
| K-ladder Phase 2 `phase2/cells/` | 46 | **43** | 0 | 3 |
| **total** | **149** | **146** | **0** | **3** |

Every one of the 146 reproduces its committed confusion **and** its
committed four-decimal MCC point estimate exactly. Zero drift. The
refactor changed the structure of the code and not one published number.

**The 44/44 the brief asked for.** Read against the 47 *materialised* files
the brief counted, 44 are not refused and 3 are; read against the 46
committed *evaluations*, 43 reproduce exactly and 3 are refused. The
difference is one materialised file with no separate evaluation — ten of
the 28 rungs share a cell, per
`k-ladder-phase2-deltas-2026-09-12.md` § 3 note 2. Both readings agree on
the three.

### 4.2 Was any published MCC wrong?

**No, outside the three already known.** Sweeping all 149 cells with the
new invariant refuses exactly the three Gemini 3.7 GS text rungs and **no
other cell in either corpus** — including all 103 cells of the signed
board. The `tile-vocabulary-match.json` count of 44/3 over the Phase 2
materialised set generalises: the board is clean.

The three, with the shortfall the invariant measures:

| cell | n det | in-union | booked by `id` | outside frame | multi-tile | committed MCC |
|---|---:|---:|---:|---:|---:|---:|
| `g37-text-k1-verified-opmax` | 502 | 475 | **21** | 27 | 129 | 0.1337 |
| `g37-text-k1-verified-carried-p0.10-k1` | 558 | 526 | **22** | 32 | 140 | 0.1422 |
| `g37-text-k3-verified-opmax` | 494 | 467 | **20** | 27 | 129 | 0.1337 |

The third value, **0.1422**, is recorded here for the first time;
`k-ladder-phase2-deltas-2026-09-12.md` § 6.3 names only 0.1337.

### 4.3 What the three would be, under each variant

Not written into `findings.md` — see § 0 and § 6.

| cell | withheld (`id`) | `geometric-primary` | `geometric-contains` | sibling K = 5 (`id`, sound) |
|---|---|---:|---:|---:|
| `g37-text-k1-verified-opmax` | withheld (0.1337 raw) | **0.9535** | **0.9262** | 0.7651 |
| `g37-text-k1-verified-carried-p0.10-k1` | withheld (0.1422 raw) | **0.9059** | **0.8761** | 0.7651 |
| `g37-text-k3-verified-opmax` | withheld (0.1337 raw) | **0.9121** | **0.8903** | 0.7651 |

Two things to notice, and both argue for putting the choice rather than
taking it.

1. **The two variants differ by 0.02–0.03 on these cells**, and by up to
   0.05 on the sound ones. Picking one silently would bury a 0.03
   methodological decision inside a bug fix.
2. **Either value is far above the family's sound K = 5 sibling's 0.7651**,
   which was computed under `id`. Restoring these three geometrically
   while leaving the sibling on `id` would put a 0.95 beside a 0.77 within
   one family and invite exactly the misreading § 7.3 of `findings.md`
   withheld them to avoid — with the arrow reversed. A coherent restoration
   requires re-scoring the whole family, which means re-scoring the board.

**One further result worth having.** The per-tile TP/FP/FN totals — and
therefore the micro-F1 the board's G1/G2 gate reproduces — are **identical**
under `id` and `geometric-primary` (measured 0.6925 either way on
`pv-high-image-t0.3-n1-opmax`, matching the deltas report § 3 rung 19
exactly), because each detection is booked to exactly one tile under both
rules and only *which* tile differs. Under `geometric-contains` they move
(0.6902), because a detection in an overlap zone is booked twice. So
`geometric-primary` is the only variant that leaves the F1 side of the
board untouched while changing the MCC side — which may be decisive for
the PI, or may be an argument that the two sides should change together.

## 5. What did NOT change

- **Every committed evaluation.** Not one was rewritten, board or K-ladder,
  including the three withheld cells. The audit writes a side report.
- **Every published number.** 146 of 149 reproduce exactly and the other
  three were already withheld. No F1 anywhere moved — but see § 5.1: "F1 is
  geometric and unaffected" is not quite true, and this report does not
  repeat that claim unqualified.
- **The default join.** Still `id`, so a re-run of any committed scoring
  command produces the committed numbers.
- **`findings.md` §§ 4, 4.1, 7.2, 7.4** and the ladder tables. § 7.3's
  withheld note is amended to record the measurement and the sharper
  question, not to fill in a value.
- **The signed Era-2 board.** Not rebuilt, not re-tiered, no signature
  field written. The audit found nothing that would require it.
- **The permutation testing.** The 3.7 family is still excluded, for the
  same reason plus a new one (§ 1, site 2).
- **`check_tile_vocabulary_match.py`.** Kept, unchanged, now as a survey
  instrument rather than a correctness guard.

## 5.1 Four things the census turned up that this work did not fix

Reported because they were found, not because they were in scope. The first
corrects a claim the corpus has been repeating.

**(a) F1 is name-dependent after all, at the map-sheet level.**
`k-ladder-phase2-deltas-2026-09-12.md` § 6.3, `findings.md` § 7.3 and the
guard script's own docstring all say F1 is geometric and therefore
unaffected. Its *matching* is. Its *scoping* is not:
`lib_advanced_metrics.py:1491`, inside `calculate_f1_internal`, selects each
map sheet's detections with

```python
det_scope = gdf_det[gdf_det['source_tile'].str.startswith(map_name)]
```

where `map_name` comes from the **bounds** file's tile names. So a cell
whose `source_tile` values do not begin with one of the frame's map-name
prefixes silently contributes **no detections to F1 either**. The same
pattern is at `:1164` in `compute_per_tile_tp_fp_fn`.

The three refused cells are **not** affected: their names
(`K-35-052-4_32635_x0_y1152.png`) share the frame's map prefix
`K-35-052-4_32635` and differ only in the tile offset, which is why their
F1 of 0.8495 is sound. But the corpus's standing reassurance is too strong,
and a cell from a differently-named sheet set would lose F1 as quietly as it
loses MCC. Unfixed: correcting it means deciding whether sheet scoping
should be geometric too, which is the same class of decision as § 6.

**(b) The era-indexed frame in `augment_per_arch_with_mcc.py`.**
`:45–48` picks the scoring frame from an `ERAS_BOUNDS` dict by era number
and applies it at `:141`, so a cell whose tiling belongs to a different era
than its board is scored on the wrong frame. Because that script assigns
`source_tile` geometrically when it is absent (`:89–97`), the failure mode
is a **wrong frame** rather than a mismatched vocabulary, and the § 3
invariant would not fire: every point would be booked, to the tiles of the
wrong tiling. A different class of error, and not one this work addresses.

*Not quantified here.* A candidate instance was put forward —
`outputs/retest/h11-single-pass-384-t0/brief-text-t0/consensus/consensus_t10.geojson`,
901 features, in an era-1 board — but on re-reading, that file carries **no
`source_tile` property at all** (0 of 901 features match either frame's
vocabulary, because there is nothing to match), so the "86 of 901 booked"
figure could not be reproduced and is not repeated. The mechanism is real;
its exposure is unmeasured.

**(c) Three paired bootstrap CIs are irreproducible despite `random_seed`.**
`bootstrap_effect_size_ci` (`:1734`), `bootstrap_interaction_ci` (`:2107`)
and `bootstrap_tile_effect_size_ci` (`:2902`) each build their tile list as
`list(<set>)` and then resample it with `rng.choice(common_tiles, …)`
(`:1759`, `:2142`, `:2963`). Python's string hashing is randomised per
interpreter unless `PYTHONHASHSEED` is set, so the list order — and hence
the sampled tile multiset — differs between runs even with the seed fixed.
`bootstrap_ci` (`:1592`) already avoids this by going through `.unique()`.
The fix is one word in three places (`sorted()` or `.unique()`), but it
would move every paired ΔF1 / ΔP / ΔR and ΔMCC interval the corpus has
published, so it belongs with § 6's decision rather than in this commit.

**(d) `pairwise_permutation_test.assign_source_tiles:277` deduplicates by
geometry, not index** — `drop_duplicates(subset=joined.geometry.name)` —
so two distinct detections at identical coordinates collapse into one and
`n_detections` changes. Every other site in the repository uses
`~joined.index.duplicated(keep="first")`. Unfixed, and untested either way.

**And one structural point worth keeping.** An F1-tolerance gate *cannot*
detect a tile-assignment error, because micro-F1 sums TP/FP/FN over tiles
and is invariant to which tile an outcome is booked to. Only the
confusion/MCC equality gates are sensitive — and they are equality gates
against the committed name-join numbers, so the moment the default join
becomes geometric they will fail on **every** cell. That is a cost of
§ 6's decision, not an argument against it, but it should be priced in.

## 6. What is put back to the PI

1. **Which geometric variant, if either?** `geometric-primary` preserves
   the per-tile F1 totals and books each detection once;
   `geometric-contains` is symmetric with the reference rule and matches
   "does this tile contain a detection". They differ by up to 0.05 MCC.
2. **Is a corpus-wide MCC shift of ≈ +0.1 acceptable, and when?** Flipping
   `TILE_JOIN_DEFAULT` is a one-line change, but it requires re-scoring 149
   cells, re-tiering and re-signing the Era-2 board, and re-deriving every
   MCC-based tier boundary and confidence interval. The shift is close to
   uniform (+0.048 to +0.147), so rankings would move little — but every
   published value would change.
3. **Should the three cells be restored at all, or stay withheld?** A
   coherent restoration re-scores their whole family, which is item 2.
4. **The deeper question the overlap raises.** The reference side has
   always booked a mound to *every* tile it touches, so on this frame ~21 %
   of reference mounds are counted in more than one tile and the "tile" is
   not an independent unit. That is a property of tile-level MCC on an
   overlapping frame, not of any join, and it was outside this work's
   scope.

## 7. Verification

| # | Check | Result | Anchor |
|---:|---|---|---|
| 1 | `id` reproduces every committed confusion and MCC | **146 of 146 EXACT, 0 DRIFT** | `results/tile-join-audit/*.json` |
| 2 | The invariant refuses only the known three | **3 of 149, all the 3.7 GS text rungs** | same |
| 3 | No published board MCC affected | **0 of 103 board cells refused** | `results/tile-join-audit/board-era2-2026-09-12.json` |
| 4 | The frame really does overlap | tile 1923.84 m on a 1686.33 m stride; Σ areas / union = **1.2783**; median **30.6 %** of detections in > 1 tile | `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`, measured |
| 5 | Site 2's wider exposure | `compute_per_tile_tp_fp_fn` now raises on the refused cell; previously returned tp 0 / fp 0 | § 1 |
| 6 | The board gate now checks geometry | fails a shortfall even when rebuilt == recorded | `tests/test_tile_join_geometric.py::test_board_gate_fails_a_shortfall_even_when_the_record_agrees` |
| 7 | Lint | `ruff check` clean on all five touched Python files; `markdownlint-cli2` clean on this report and the two amended documents | — |
| 8 | Tier-1 suite | see § Changelog | `python -m pytest -m tier1 -q` on sapphire |

## 8. Observation candidate

**The class: a metric keyed by a name beside a metric keyed by geometry.**

The tile confusion matrix had one axis joined by string equality and the
other by spatial containment. Both axes looked like "which tile is this
in?", and for a year they agreed, because every cell happened to be scored
on the tiling its proposer ran on. The first cell scored on a foreign frame
produced a correct F1 beside a meaningless MCC, and every guard in the
pipeline passed it: the evaluation reported no error, the board's confusion
gate rebuilt the confusion with the same wrong function and confirmed it,
and the number itself (0.1337) was low but not absurd.

Three things generalise beyond this bug.

**A name is a claim about provenance; geometry is a claim about the world.**
When a name and a coordinate are both available for the same entity, the
name encodes *where it came from* and the coordinate *where it is*. Those
are different facts. A metric that mixes them is not approximately right;
it is two metrics wearing one label. The tell is an asymmetry — here, one
axis of a 2 x 2 table keyed differently from the other — and asymmetry in a
confusion matrix is worth auditing for its own sake.

**A gate that recomputes with the function under suspicion cannot fail.**
The board's confusion gate was carefully built, hard-raising, and
completely blind, because it compared a computation with itself. A gate
earns its name only by appealing to something the suspect code does not
touch — here the frame's polygons. "Does the rebuild match the record?" and
"does the record match the world?" are different questions, and only the
second is a check.

**Fixing a silent failure can be cheaper than fixing what it concealed.**
Making the failure loud took an afternoon and moved no published number.
Making the metric geometric is a corpus-wide re-scoring, a re-signature,
and a choice between two defensible rules that differ by more than most
effects this project reports — because the frames overlap, so "the tile
containing this point" was never a function in the first place. The
assumption that let the bug live (one tiling per cell) is also the
assumption that made the fix look free. Worth checking, at the moment a
defect is diagnosed, whether the repair and the diagnosis rest on the same
unexamined premise.

## Changelog

### 2026-09-12 — Original publication

Written in response to the PI's 2026-09-12 ruling on
`reports/k-ladder-phase2-deltas-2026-09-12.md` § 6.3, on branch
`worktree-agent-a5339796998dcf596` (merged from
`origin/worktree-agent-ae87367bcee3e0e5c`, pull request #15, where the
three affected cells live).

Reports: a twelve-row census of the repository's tile-join sites (§ 1); the
three named rules and their edge and no-tile behaviour (§ 2); the invariant
and its three enforcement points (§ 3); the regression over all 149
committed cells the board reads — **146 EXACT, 0 DRIFT, 3 REFUSED** (§ 4.1);
the answer to "was any published MCC wrong?" — **no, outside the three
already withheld** (§ 4.2); and the three withheld cells' value under each
geometric variant, reported rather than written back (§ 4.3).

**Four out-of-scope findings** are recorded in § 5.1 rather than fixed, the
first of which corrects a claim the corpus has been repeating: F1's
*matching* is geometric but its map-sheet *scoping* is a `source_tile`
string prefix (`lib_advanced_metrics.py:1491`), so "F1 is geometric and
unaffected" is too strong. The other three are an era-indexed frame
selection in `augment_per_arch_with_mcc.py`, three paired bootstrap
confidence intervals that are irreproducible despite `random_seed` because
they resample `list(<set>)`, and a geometry-keyed deduplication in
`pairwise_permutation_test.assign_source_tiles` that collapses coincident
detections. Each was re-read at source before being written down; one
candidate instance offered for the second was **not** reproducible and is
reported as unquantified rather than repeated.

**The stop.** The ruling's premise — that a geometric join reproduces the
string join where the vocabulary matches — is false, because the 384 px
evaluation frames overlap on a 336 px stride (Σ tile areas / union =
1.2783; median 30.6 % of detections inside more than one tile). A geometric
join raises MCC on **146 of 146** correctly-joined cells, by +0.1059 mean
under `geometric-primary` and +0.0754 under `geometric-contains`. The
default was therefore left at `id` and the variant choice put back to the
PI (§ 6). No committed evaluation was rewritten.

Landed by commits on the branch above: the library fix, the
`--tile-join` wiring, the tier-1 tests, the gate hardening, the audit
instrument, and the audit results.

Tier-1 suite at publication: recorded in the session's final report.
