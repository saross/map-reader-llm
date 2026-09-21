# The June 2026 image pool, swept on r2: findings

> **Last revised**: 2026-09-21 (the `IM-5pass-k3-mcc-oracle` row retired from
> § 3's cell table under PI ruling 2026-09-21 and the phrase "MCC oracle"
> retired from the prose; the cell stays on disk, re-labelled retained and
> not presented; no number changed). Prior: 2026-09-20 (§ 7 added — the
> 16-candidate vote-count
> divergence noted in § 1 traced to the 2026-05-03 recovery campaign, with its
> blast radius across the committed board measured; no figure in §§ 1-6 moved).
> Prior: 2026-09-20 (original publication — the June image run's
> threshold-by-votes grid on the r2 reference, its four scored cells, and the
> comparison with the September rebuilt Gemini 3 image pool of the image 2x2).
> See [§ Changelog](#changelog) for revision history.

**What this is.** The image 2x2 of September 2026 compared its rebuilt Gemini 3
image pool (`outputs/gemini3-image-55map-2026-09-16`) against `IM-k3` — the
single committed cell of the June 2026 image generalisation run
(`outputs/55maps-image-generalisation`), read at one operating point
(probability >= 0.15, votes >= 3). One point is not a comparison: the rebuilt
pool was swept over its whole achievable space and then read at its oracle,
while the June run was judged at a point it had chosen for other reasons. This
note builds the fullest grid the June run's own data can support — at zero API
cost — and reads the two pools side by side.

**Instrument.** `scripts/im_june_pool_grid.py`, which imports every primitive
from `scripts/gemini37_image_55map_r2.py`: the operating-point predicate, the
`assign_eval_frame_tiles` tile re-stamp, the per-tile TP/FP/FN arrays, the
micro-F1 and tile-MCC mechanism, and the engine command. Nothing about the
measurement is re-implemented, so a difference between the two pools cannot be
an artefact of two scorers. The four materialised cells are then scored by
`scripts/evaluate_detections.py` on the r2 board's own stage-2 recipe — 14
buffers, `inputs/vectors/references/best-available-gt-55maps-r2.geojson`
(5,018 references), `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`
(8,541 tiles), tile-level BCa bootstrap 10,000 / seed 42, `--mcc`,
`--require-clean-inputs` — the same invocation the 2x2's own cells went
through. Grid: `sweep_IM-5pass.csv`; oracles and the gate: `grid.json`; cells:
`cells/<label>/evaluation.json`.

**The tile re-stamp, and what it costs.** `source_tile` is re-stamped by
`stride55_score.assign_standard_tile` — nearest standard-grid tile centroid
within the origin raster's own map — because that is the writer every other r2
cell went through, and `IM-k3`'s committed file did not (83.65 % idempotent;
`results/run-facts.json` § IM-k3 CAVEAT). **Every figure in this note is
re-stamped.** The re-stamp is not cosmetic but it is small, and this is the
first time its cost has been measured: at the carried point it leaves
micro-F1 @ 50 m unchanged at 0.8008 and moves tile-MCC from the committed
**0.7110 to 0.7087** (−0.0023). That puts a number on an open item:
`results/gemini37-image-55map-2026-09-13/findings.md` § 7 records the mixed
assignment rule as a limitation, and its 2026-09-16 changelog entry left the
reconciliation to the PI because it "would move `IM-k3`'s published MCC and
therefore the eight-cell tiering where it is sole Tier 1". The move is
−0.0023 on tile-MCC and nothing on micro-F1 — whether that disturbs the
tiering is still the PI's call, but it is no longer an unmeasured one.

**Reproduction gate.** The grid's carried point (0.15, k3) retains exactly the
4,680 detections of the committed `IM-k3` cell and reproduces its committed
numbers within the board's 0.003 mechanism bound: micro-F1 @ 50 m 0.8008
against 0.8008 (Δ 0.0000) and tile-MCC 0.7087 against 0.7110 (Δ −0.0023).
Read without the re-stamp — that is, on `IM-k3`'s own tile convention — the
carried point reproduces **both** committed figures exactly (0.8008 / 0.7110).
The grid was not written until that gate passed
(`scripts/im_june_pool_grid.py` `--stage sweep` refuses otherwise).

## 1. What the grid can cover, and what it cannot

The June verifier saw **only the 3-of-5 consensus union**. Its crop manifest
(`outputs/55maps-image-generalisation/crops/candidate_manifest.json`) holds
7,878 candidates, every one with `vote_count` in {3, 4, 5} — 2,896, 2,159 and
2,823 respectively — and `verified/probabilities.json` holds a probability for
each. Candidates carrying **one or two votes were never verified**, so they
have no probability and cannot be scored at any threshold. The grid therefore
covers `min_votes` in {3, 4, 5} only: the ladder is the 17 distinct observed
probabilities (zero is one of them, so the board's "zero plus each observed
value" rule adds nothing), crossed with three vote thresholds — 51 points in
all. The rebuilt pool's votes 1-2 rows have **no
June counterpart**, and this is a limit of the June run's design, not of the
sweep.

**Which of the two June union records the grid reads.** The run holds two
records of the same 3-of-5 union: `consensus/consensus-3of5.geojson` and
`crops/candidate_manifest.json`. They hold the same 7,878 candidates — matched
one to one, median centroid separation 0 m, maximum 6.9 m — but **16 of them
(0.20 %) carry a different `vote_count` in the two files**, so the vote
histograms differ: 2,891 / 2,153 / 2,834 in the consensus file against
2,896 / 2,159 / 2,823 in the manifest. Rebuilding the union from the five
passes (§ 5) reproduces the **consensus file** exactly, so it is the manifest
that carries the divergent counts: they are the run's *pre-recovery* vote
counts, frozen by an incremental re-extraction on 2026-05-03 that appended the
one new candidate without refreshing the 7,877 it matched (§ 7). The
grid reads the **crop manifest** regardless, because that is the file the
verifier was given, the one `verified/probabilities.json` keys to by
`candidate_id`, and the one the 55-map board's own `IM` family loads
(`final_board_sweeps.build_families`). Reading the other would pair 16
candidates' probabilities with the wrong vote count.

## 2. Best F1 and best MCC per vote count

The June pool (`sweep_IM-5pass.csv`, 51 points) beside the rebuilt Gemini 3
pool at K = 5 under the identical verifier arm
(`results/gemini3-image-55map-2026-09-16/sweep_G3IMG-ARM1-K5.csv`, 100
points). Each metric is given at its own argmax over that vote count's rows,
with the probability threshold and the detection count at that point, on the
same reference, frame and scorer.

| votes | June best F1 @ 50 m | at *p* | *n* | June best tile-MCC | at *p* | *n* | Sept best F1 @ 50 m | at *p* | *n* | Sept best tile-MCC | at *p* | *n* |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| >= 1 | — | — | — | — | — | — | 0.5341 | 0.95 | 9,999 | **0.7496** | 0.40 | 11,739 |
| >= 2 | — | — | — | — | — | — | 0.6534 | 0.35 | 7,949 | 0.7447 | 0.40 | 7,937 |
| >= 3 | **0.8008** | 0.15 | 4,680 | **0.7139** | 0.20 | 4,561 | 0.7357 | 0.20 | 6,974 | 0.7413 | 0.40 | 6,316 |
| >= 4 | 0.7398 | 0.15 | 3,541 | 0.6597 | 0.20 | 3,467 | 0.7931 | 0.20 | 5,828 | 0.7335 | 0.40 | 5,295 |
| >= 5 | 0.5851 | 0.15 | 2,283 | 0.5459 | 0.15 | 2,283 | **0.8177** | 0.15 | 4,858 | 0.7199 | 0.20 | 4,729 |

Three things fall out of the June column that no single-point reading could
have shown.

1. **The June run was already at its own F1 optimum.** Probability 0.15 — the
   threshold its `resolved_config.yaml` fixed before any scoring — is the
   micro-F1 argmax at **every** vote count the pool can reach. There is no
   carried-versus-oracle tax on F1 at all; on tile-MCC the tax is 0.0052
   (0.7087 at the carried point against 0.7139 at *p* = 0.20).
2. **The two pools run in opposite directions with the vote threshold.** June's
   F1 *falls* as votes rise (0.8008 → 0.7398 → 0.5851); September's *rises*
   (0.7357 → 0.7931 → 0.8177). Unanimity costs June 0.2157 of F1 and buys
   September 0.0820. The reason is that June's five passes corroborate each
   other far less: of its 63,217-candidate 1-of-5 union (§ 5) only **12.5 %**
   reaches three votes and **4.5 %** is unanimous, against **38.6 %** and
   **22.6 %** of September's 45,786 (`sweep_G3IMG-ARM1-K5.csv`, the *p* = 0.0
   rows: 17,683 and 10,353). "A vote" is not the same object in the two pools
   (§ 4), so this is a description of the difference rather than an
   explanation of it.
3. **September's best MCC sits where June has no data.** The rebuilt pool's
   unconstrained tile-MCC optimum is at one vote (0.7496 at *p* = 0.40,
   *n* = 11,739; `results/tile-presence-2026-09-21/leaderboard.md`,
   `G3IMG-ARM1-K5`) — inside the region June never verified. Restricted to
   the votes the June pool can reach, September's best tile-MCC is 0.7413 at
   three votes.

The cells scored on the full recipe (three presented; a fourth, the tile-MCC
argmax at three votes, is retained on disk and not presented — see the
pointer below the table):

| cell | point | *n* | F1 @ 50 m [BCa 95 %] | precision | recall | tile-MCC [BCa 95 %] |
|---|---|---:|---|---:|---:|---|
| `IM-5pass-k3-f1-oracle` | (0.15, k3) | 4,680 | 0.8008 [0.7909, 0.8101] | 0.8297 | 0.7738 | 0.7087 [0.6944, 0.7225] |
| `IM-5pass-k5-carried` | (0.15, k5) | 2,283 | 0.5851 [0.5693, 0.6004] | 0.9356 | 0.4257 | 0.5459 [0.5314, 0.5602] |
| `IM-5pass-k5-f1-oracle` | (0.15, k5) | 2,283 | 0.5851 [0.5693, 0.6004] | 0.9356 | 0.4257 | 0.5459 [0.5314, 0.5602] |

The June pool's tile-MCC optimum is not a row here (PI ruling 2026-09-21: the
tile-MCC optimum is off every board and campaign table under both
definitions). Its unconstrained form, `IM` at (0.20, k3), is presented with its
vote count and pool cost in
[`results/tile-presence-2026-09-21/`](../tile-presence-2026-09-21/leaderboard.md);
the cell this note scored at that point, `IM-5pass-k3-mcc-oracle`, stays in
`cells/` with its committed evaluation, re-labelled in `cells_manifest.json`
as retained and not presented. The per-vote-count grid above keeps both
argmaxes as recorded data (`grid.json`, `mcc_argmax`). One caution when
following the pointer: the tile-presence `IM` row is scored from the r2
board's own `IM` sweep on the board's tile convention, not this note's
re-stamped one (§ 1), so it reads tile-MCC 0.7173 at the same point where
the retained cell reads 0.7139 — the documented re-stamp difference, not a
disagreement about the cell.

The last two are the **same cell**: 0.15 is already the F1 argmax at
unanimity, which is finding 1 above showing up in the cell list. Both are kept
because the coincidence is the result. Note what unanimity buys and costs on
the June pool — precision 0.9356 against 0.8297, recall 0.4257 against 0.7738.

## 3. The matched comparison at three votes

Two readings, both at three votes out of five passes, both under the identical
verifier arm:

| reading | June (`IM-5pass`) | September (`G3IMG-ARM1-K5` pool) | Δ (June − Sept) |
|---|---|---|---|
| best F1 at votes >= 3 | **0.8008** (*p* = 0.15, *n* = 4,680) | 0.7357 (*p* = 0.20, *n* = 6,974) | **+0.0651** |
| best tile-MCC at votes >= 3 | 0.7139 (*p* = 0.20, *n* = 4,561) | **0.7413** (*p* = 0.40, *n* = 6,316) | −0.0274 |
| same point (0.15, k3), F1 | **0.8008** (*n* = 4,680) | 0.7312 (*n* = 7,222) | **+0.0696** |
| same point (0.15, k3), tile-MCC | 0.7087 | **0.7235** | −0.0148 |

At three votes out of five, the June pool is **markedly better on micro-F1 and
slightly worse on tile-MCC**, and it gets there with about two-thirds as many
detections (4,680 against 7,222 at the same point). The two metrics disagree
because the extra detections are a recall-for-precision trade. September's
2,542 additional detections at (0.15, k3) buy 592 more true positives and
1,950 more false positives against the 5,018-point reference — recall 0.892
against June's 0.774, precision 0.620 against 0.830. Micro-F1 @ 50 m penalises
that trade heavily. Tile-MCC barely notices it, because on an 8,541-tile frame
the extra recall lifts tile true positives from 2,443 to 2,621 while tile
false positives rise only from 152 to 245: many of those 1,950 false positives
land on tiles a true positive had already claimed.

At unanimity the ordering reverses violently — June 0.5851 against September
0.8177 on F1 — because the pools disagree about what a vote is worth (§ 4).

## 4. What is not comparable

The two pools share a **verifier that is identical in every recorded
particular**: `gemini-3-flash-preview`, instruction file `verify_adversarial.md`
under config `verify_adversarial-text`, system-instruction SHA-256
`2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25dc1454af3497e15d`, temperature
0.0, thinking level `minimal`, no exemplar images
(`outputs/55maps-image-generalisation/verified/run.meta.json` against
`outputs/gemini3-image-55map-2026-09-16/verifier/g384_ov192_55map_g3img/verify_k3_arm1/run.meta.json`).
Arm 1 of the 2x2 is the June verifier **in configuration**. It is not the
same invocation: erratum E89 measures independent re-invocations of these
verifiers at T = 0 differing in ~40 % of probabilities and flipping 3.5–5.3 %
of decisions at the operating point
(`reports/image-2x2-tests-declaration-2026-09-19.md` § 5 caveat 1), so part of
any difference between the two pools is verifier drift rather than a proposer
effect. The differences in § 2 and § 3 (0.015 to 0.233) are far above that
floor; a difference of a few thousandths — T5's 0.0016, for instance — is not.
Everything else differs:

| factor | June (`55maps-image-generalisation`) | September (`gemini3-image-55map-2026-09-16`) |
|---|---|---|
| proposer model | `gemini-3-flash-preview` | `gemini-3-flash-preview` |
| proposer instruction | `detect_brief-text-image.md`, SHA-256 `e169b72…` | the same file, same hash |
| exemplar library | `library_plus-hp`, **13** exemplars (4 canonical +, 2 canonical −, 4 hard +, **0 hard −**, 3 null) | `detect_brief-text-image`, **17** exemplars — the Scale-8 set (4 canonical +, 2 canonical −, 4 hard +, **4 hard −**, 3 null) |
| thinking level | **high** | **minimal** |
| temperature | 0.7 | 0.7 |
| passes | 5 | 5 |
| tiling | `inputs/tiles_384_55maps`, **8,541** tiles — 384 px on a 336 px stride, the evaluation frame itself | `g384_ov192_55map`, **24,561** tiles — 384 px on a 192 px stride |
| candidates verified | **7,878** (the 3-of-5 union only) | **45,786** at K = 5 (the full 1-of-5 union); 36,389 at K = 3; 22,785 at K = 1 |
| `source_tile` convention as committed | origin tile (83.65 % idempotent under the board's writer) | the board's writer |

Four of those are live confounds for any June-versus-September reading.

- **The library differs by exactly the four hard-negative exemplars.** The
  example lists are otherwise identical, and the instruction text is
  byte-identical.
- **The thinking level differs**, high against minimal. The project has
  measured a diversity dividend from high-thinking proposer passes before
  (Obs 141); this is the mechanism most likely behind June's much lower
  cross-pass agreement, and it is confounded with everything else here.
- **The tiling differs by a factor of ~2.9 in tile count.** A 192 px stride
  puts most locations inside up to four tiles, against the 336 px stride's one
  or two, so "a vote" is not the same object in the two pools — a point
  the vote-threshold reversal in § 2 makes concrete.
- **The verified span differs.** June verified 7,878 candidates; September
  verified 45,786. This is why the grid stops at three votes.

Two things that are **not** confounds, and should not be treated as such:

- **The union builder.** June used `scripts/merge_passes.py` (within-pass
  dedup at 20 m via `deduplicate_within_pass`, then greedy star clustering of
  the pooled passes at 20 m); September used
  `scripts/stride55_prepare_and_union.py`, which calls the **same**
  `deduplicate_within_pass` at 20 m and then `h13_k_sensitivity.cluster_votes`
  — a NumPy-vectorised restatement of the same greedy star clustering at the
  same 20 m radius (`DEDUP_M = 20.0`). The June run's own
  `consensus/consensus_meta.json` records `dedup_radius_m` 20.0. Different
  code, same rule.
- **The scorer.** Both are read through `gemini37_image_55map_r2.py`'s
  primitives and scored by `evaluate_detections.py` on the same recipe,
  reference and frame.

## 5. What a full June grid would need verified

Rebuilding the 1-of-5 union from the five June proposer passes with the run's
own builder — `scripts/merge_passes.py --threshold 1` over
`outputs/55maps-image-generalisation/proposer/library_plus-hp`, which is what
`run_generalisation.run_consensus` invoked, at the 20 m radius
`consensus/consensus_meta.json` records as `dedup_radius_m` — yields **63,217
candidates**:

| votes | candidates | verified in June? |
|---|---:|---|
| 1 | 48,716 | no |
| 2 | 6,623 | no |
| 3 | 2,891 | yes |
| 4 | 2,153 | yes |
| 5 | 2,834 | yes |
| **total** | **63,217** | **7,878** of them |

The rebuild reproduces `consensus/consensus-3of5.geojson` exactly at every
vote count, which is the check that it is the clustering the run actually
performed. So a grid carrying the rebuilt pool's votes 1-2 rows would need
**55,339 further candidates verified** — 7.0 times the number the June run
verified, and 1.2 times the whole September K = 5 union of 45,786. At the June
verifier stage's own audited rate (US$5.4831 for 7,878 candidates on flex,
`cost_manifest.json` § `by_stage.verifier`) that is of the order of **US$38**
in API spend, plus crop extraction for 55,339 new crops (compute, not API) and
the ~55,000 extra crop files on disk. Nothing of the kind is proposed here:
the figure is simply what the "votes 1-2 are not comparable" caveat would cost
to remove. Counts only — no verification was run, and the rebuilt union lives
outside the repository (`~/tmp/im-june-union/union_1of5.geojson` on sapphire);
what is committed is `union_1of5_counts.json` beside this note.

## 6. What this does to the 2x2's T5

T5 of the image 2x2 declaration asked whether, "with the five confounds
removed (library, tiling, thinking, passes, tile convention), the earlier
Gemini 3 image cell is reproduced", and answered it by testing
`G3IMG-ARM1-K3-carried` against `IM-k3`
(`reports/image-2x2-tests-declaration-2026-09-19.md` § 3;
`results/image-2x2-2026-09-19/tests_2x2_K3.json`). It found a near-tie on
micro-F1 — 0.8024 against 0.8008, Δ 0.0016, permutation *p* = 0.7604 — and a
non-significant 0.0137 on tile-MCC (0.7247 against 0.7110, *p* = 0.0578,
BH-adjusted 0.0723). The trouble is that the two cells are not the same kind
of cell. `G3IMG-ARM1-K3-carried` is **3-of-3 unanimity on a three-pass pool**
— the first-3-passes union, 36,389 candidates, all verified — while `IM-k3` is
**3-of-5 majority on a five-pass pool** (*n* = 5,538 against 4,680). The
declaration lists "passes" among the five confounds T5 removes, but matching
the absolute vote count across pools of different depth does not remove that
confound: it converts it into a vote-*fraction* confound of 1.0 against 0.6.

The sweep shows how much that matters. Hold the absolute vote count at three
and compare like with like on a five-pass pool, and the September cell falls
to F1 0.7312 (0.7357 at its own oracle), so June *leads* by 0.0651 to 0.0696
rather than trailing by 0.0016. Hold consensus *stringency* fixed instead and
compare unanimity with unanimity, and June falls to 0.5851 against September's
0.8177, a gap of 0.2326 the other way. **T5's near-tie is one point in a space
where the two pools differ by −0.23 to +0.07 on micro-F1 depending on which
axis is held fixed**, and the axis T5 held fixed — the absolute vote count,
across pools of different depth — is the one that makes them agree.

Read as the declaration frames it, T5 is a confound check whose null result
says the earlier Gemini 3 image cell is reproduced. On micro-F1 that reading
does not survive the grid: the agreement is a property of the matching, not a
reproduction, and it is 0.0016 — below the E89 verifier-drift floor in any
case (§ 4). The tile-MCC half fares better, because tile-MCC is much flatter
across this whole region (0.7087–0.7139 for June at three votes, 0.7199–0.7496
for September across its five vote-count oracles), so its reading is less
sensitive to where on the grid the comparison is taken. Nothing here re-runs
T5, re-tiers a board or touches a signed row; the claim T5 can support is
narrower than a bare null makes it look, and the honest supplement is the § 3
table. A properly matched T5 is available for US$0 whenever the PI wants one:
the (0.15, k3) row of `sweep_G3IMG-ARM1-K5.csv` is already swept, so
materialising that point as a cell and running the same paired tile-swap
against `IM-5pass-k3-f1-oracle` is on-disk work.

## 7. Why the two June union records disagree, and how far it reaches

**What the 16 are.** Every one of them is **exactly one vote lower in the crop
manifest**, with exactly one pass missing from `contributing_passes` and
`cluster_size` short by one — eleven read 4 in the manifest and 5 in the
consensus file, five read 3 and 4. They sit on ten tiles, and on each tile it
is one and the same pass that is absent:

| tile | pass missing from the manifest | `candidate_id`s | manifest → consensus |
|---|---|---|---|
| `K-35-042-3_x3360_y1344` | run_3 | 6662, 6663 | 3 → 4 |
| `K-35-050-4_x1008_y2352` | run_1 | 6655 | 4 → 5 |
| `K-35-051-4_x336_y2352` | run_2 | 591 | 4 → 5 |
| `K-35-062-4_Asenovgrad_4326_x336_y1008` | run_5 | 2470 | 4 → 5 |
| `K-35-063-2_Chirpan_4326_x0_y2352` | run_3 | 7055 | 3 → 4 |
| `K-35-063-2_Chirpan_4326_x2352_y3696` | run_1 | 7040 | 4 → 5 |
| `K-35-064-2_Radnevo_4326_x2352_y1680` | run_3 | 3402, 3403 | 4 → 5 |
| `K-35-064-2_Radnevo_4326_x2352_y2688` | run_1 | 7119 | 4 → 5 |
| `K-35-064-3_Dimitrovgrad_4326_x2352_y2688` | run_3 | 3527 (3 → 4), 3528, 3529 | 4 → 5 except 3527 |
| `K-35-065-2_GManastir_4326_x3024_y336` | run_5 | 3925 (3 → 4), 3924, 3926 | 4 → 5 except 3925 |

**The mechanism.** One pass missing per tile is the signature of the 2026-05-03
**recovery campaign**, and the manifest records it itself. The original run
(2026-04-18, `.resume_state.json`) left 26 tiles unrecovered across the five
passes — residuals 8/3/8/2/5 — which commit `2992056be` recovered. The
consensus was then re-merged from the completed passes, and commit `8699f456b`
re-ran the extract stage with `scripts/55maps-t0.3-extract-new-candidates.py`.
That script spatially matches each new consensus feature to an existing
manifest candidate within 20 m and **appends only the unmatched ones**,
deliberately preserving existing candidate IDs so the verifier's
`probabilities.json` stays valid — and therefore never refreshing a matched
entry's `properties`. The manifest's own `recovery_history` block books the
step: `existing_candidates` 7,877, `new_consensus_features` 7,878,
`matched_to_existing` 7,877, `new_extracted` 1. So the consensus file is
post-recovery and 7,877 of the manifest's 7,878 entries carry pre-recovery
vote counts. It is **not** a dedup-radius difference (both are 20 m), not a
`merge_passes` version change, and not the mid-write race that `8699f456b`
separately diagnosed and corrected — that race produced the wrong *feature
count*, which was fixed; this is the property refresh that the incremental
extractor does not do by design.

**Blast radius.** Five of the 263 `candidate_manifest.json` files under
`outputs/` carry a non-empty `recovery_history`; all five are April/May 2026
recovery-campaign runs, and all five show the same one-vote-low divergence:

| run | consensus | manifest | divergent candidates | direction |
|---|---:|---:|---:|---|
| `55maps-text-high-generalisation` | 9,206 | 9,205 | 110 | all 4 → 5 |
| `55maps-text-high-t0.3-generalisation` | 9,910 | 9,910 | 15 | all 4 → 5 |
| `55maps-text-min-generalisation` | 10,170 | 10,170 | 88 | all 4 → 5 |
| `55maps-image-generalisation` | 7,878 | 7,878 | 16 | 11 at 4 → 5, 5 at 3 → 4 |
| `gs/gold-standard-v2` | 608 | 608 | 15 | all 4 → 5 |

**The current chain is clean.** Both rows of the image 2x2 were checked rung by
rung, union `vote_count` against crop-manifest `vote_count`, index-aligned and
spatially matched: `gemini37-image-55map-2026-09-13` K = 1/3/5 (6,985 / 8,337 /
9,173) and `gemini3-image-55map-2026-09-16` K = 1/3/5 (22,785 / 36,389 /
45,786) — **zero disagreeing candidates in all six**, and no manifest carries a
`recovery_history`. Each was built once from its union and never incrementally
patched, so the mechanism is inert there.

**Does any committed cell's membership change?** Almost none, and the one that
does moves by three detections.

- **No candidate crosses the 2 → 3 boundary** in any of the five runs, so no
  cell defined at votes ≥ 3 changes membership. `IM-k3` — and with it
  `IM-oracle`, this note's `IM-5pass-k3-f1-oracle` and the retained
  `-k3-mcc-oracle` cell, and
  the 2x2's T5 comparator — is **unaffected**, as is every votes ≥ 3 row of
  `sweep_IM-5pass.csv`.
- The three text runs' divergences are **all 4 → 5**, above their own 4-of-5
  consensus threshold, so their k3 and k4 board cells are unaffected too.
- The one exception is **`IM-k4`** (`results/55map-final-board-r2-2026-09-06/cells_manifest.json`,
  point (0.15, k4)), whose committed 3,541 detections are the manifest-vote
  count. Read on the consensus file's votes it would be 3,544 (+3, 0.08 %).
  Scored on the r2 recipe the difference is micro-F1 @ 50 m 0.7398 → 0.7402 and
  tile-MCC 0.6577 → 0.6579 — an order of magnitude inside the board's own
  0.003 mechanism bound.
- **No board oracle could move.** Every affected family's k = 5 row sits far
  below its k = 3 argmax (`IM` 0.5851 against 0.8008; `TH7` 0.7340 against
  0.8380; `T03` 0.7729 against 0.8399; `TM` 0.7289 against 0.8103), so
  promoting 15 to 110 candidates into the k = 5 band cannot change any argmax.
- Within **this** note, the votes ≥ 4 and ≥ 5 rows of the grid would gain at
  most 11 detections. At the two carried points the divergence can reach:
  (0.15, k4) F1 0.7398 → 0.7402 and MCC 0.6577 → 0.6579; (0.15, k5) F1 0.5851
  → 0.5867 and MCC 0.5459 → 0.5472, with *n* 2,283 → 2,291. All four shifts
  are inside the 0.003 bound and far below the E89 verifier-drift floor, so
  nothing in §§ 2-6 changes. The grid stays on the manifest's votes, which are
  the votes the verifier was actually shown.

**One piece of by-catch, outside this note's scope.** The same incremental
extractor left `55maps-text-high-generalisation` with **9,205 manifest
candidates against 9,206 consensus features**: two distinct 4-vote consensus
clusters 17.29 m apart both fell inside the 20 m match radius of manifest
`candidate_id` 505 (`K-35-051-4_x1344_y3360.png`), so the second was matched
rather than extracted and has never been verified. Its `recovery_history`
records the double match plainly — `existing_candidates` 9,131 but
`matched_to_existing` 9,132. One candidate in 9,206 is a small completeness
gap, but it is a real one and it is the PI's call, not this note's.

## Changelog

### 2026-09-21 — The tile-MCC optimum retired from this note's table

**Refresh trigger**: PI ruling 2026-09-21 (`planning/pi-decisions-2026-09-20.md`
D6c, amended), which dropped the "MCC oracle" from every board and campaign
table under both definitions, and the S156 close block's first open thread,
which named this note's script as still writing one such cell.

**What changed**: `scripts/im_june_pool_grid.py` no longer materialises the
`mcc-oracle` basis (three cell specs, not four) and records the per-vote
tile-MCC argmax in `grid.json` under `mcc_argmax` rather than `mcc_oracle`
(a key rename, values untouched); `cells_manifest.json` re-labels
`IM-5pass-k3-mcc-oracle` as retained and not presented, with the same
presentation text the tile-presence builder wrote on the campaigns'
manifests; § 3's cell table loses that row and gains a pointer; § 3 item 3
and § 7 say "tile-MCC optimum" where they said "MCC oracle". The cell's
files are not moved or deleted.

| | before | after |
|---|---:|---:|
| § 3 cell-table rows | 4 | **3** |
| cells on disk | 4 | **4** (none deleted) |
| `IM-5pass-k3-mcc-oracle` F1 / MCC (evaluation.json) | 0.7999 / 0.7139 | unchanged |

**Numbers that moved**: none.

### 2026-09-20 — § 7: the vote-count divergence diagnosed

**Refresh trigger**: the PI asked why the June run's consensus file and its
crop manifest disagree on `vote_count` for 16 of 7,878 candidates, and whether
it signals a broader problem. Read-only investigation; § 7 is its answer and
§ 1's hedge ("the artefacts do not say") is replaced in place by the mechanism.

**What moved numerically: nothing.** Every figure in §§ 1-6 is unchanged,
because the divergence never crosses the 2 → 3 vote boundary:

| claim | before | after |
|---|---|---|
| `IM-5pass-k3-f1-oracle` F1 / MCC | 0.8008 / 0.7087 | unchanged |
| `IM-5pass-k3-mcc-oracle` F1 / MCC | 0.7999 / 0.7139 | unchanged |
| every votes ≥ 3 row of `sweep_IM-5pass.csv` | — | unchanged |
| `IM-k3` and the 2x2's T5 comparator | 0.8008 / 0.7110 | unchanged |
| votes ≥ 4 / ≥ 5 rows, if read on consensus votes | *n* +1 to +11 | (0.15, k5) F1 0.5851 → 0.5867, MCC 0.5459 → 0.5472 — not adopted |
| `IM-k4` on the r2 board, if read on consensus votes | *n* = 3,541 | *n* = 3,544; F1 0.7398 → 0.7402, MCC 0.6577 → 0.6579 — not adopted |

**What did not change**: the grid, the four cells and their evaluations are
untouched; the reproduction gate still passes at |ΔF1| 0.0000 / |ΔMCC| 0.0023;
the § 3 comparison and the § 6 reading of T5 stand; no board was re-tiered and
no committed artefact was rewritten. The grid continues to read the crop
manifest, which is the record of what the verifier was actually shown.

**Two items referred to the PI**: whether `IM-k4` should be rebuilt on
post-recovery votes (+3 detections, +0.0004 F1), and the one
`55maps-text-high-generalisation` consensus feature that the incremental
extractor matched instead of extracting and that has never been verified
(§ 7, last paragraph).

Commit: see `git log -- results/im-june-pool-grid-2026-09-20/findings.md`.

### 2026-09-20 — Original publication

First publication. Written from the committed grid
(`sweep_IM-5pass.csv`, `grid.json`) and the four committed
`cells/<label>/evaluation.json` files, with the comparator rows read from
`results/gemini3-image-55map-2026-09-16/sweep_G3IMG-ARM1-K5.csv` and
`sweep_G3IMG-ARM1-K3.csv`, the T5 figures from
`results/image-2x2-2026-09-19/tests_2x2_K3.json`, the union counts from
`union_1of5_counts.json` beside this note, and the configuration table from
each run's own `run.meta.json` and `resolved_config.yaml` rather than carried
from any prior note. The grid, the four cells and the 1-of-5 union rebuild all
ran on sapphire.

Upstream commits this document rests on: `4ac321a79` (the 51-point sweep, the
reproduction gate, and the four materialised cells) and `cb12de12b` (the
engine scores). Zero API spend: every figure is a re-read of data already on
disk.

State at publication: the reproduction gate passes with |ΔF1| = 0.0000 and
|ΔMCC| = 0.0023 against a 0.003 tolerance; no board re-tiered, no signed row
touched, and T5 not re-run.
