# Inheritance against own-leg verification on the Gemini 3 image row

> **Last revised**: 2026-09-20 (§ 6 and § 8 re-read against the arm 1
> verifier's now-measured drift floor; H1 no longer rests on a borrowed
> warrant — no number in this note moved). Prior: 2026-09-20 (original
> publication — the Gemini 3 image row's K = 1 and K = 3 rungs derived by
> inheritance from its K = 5 legs, the eight-cell head-to-head, the
> candidate-level agreement statistics, the density stress test of the 10 m
> radius, the arm 2 ladder contrasts under each method, and the verdict
> against the E89 drift floor). See [§ Changelog](#changelog) for revision
> history.

## 1. Why this row

The 3.7 image row's head-to-head
(`results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/findings.md`)
found inheritance indistinguishable from the campaign's per-rung verifier legs
and named this row as the measurement that would close the D2 adoption
question. Three things made row A a weak test:

1. **It is one pool.** The adoption decision is for the benchmark, which spans
   both rows of the image 2 x 2.
2. **Its K = 1 cell is already precise** (F1 0.87). The dropped-candidate
   precision bias the D2 options list flags as "unmeasured" should be largest
   on a *low-precision* candidate set, and row A does not contain one. Row B's
   K = 1 cells over-generate badly — F1 0.66, precision 0.51–0.53
   (`reports/image-2x2-tests-declaration-2026-09-19.md` § 5 caveat 4).
3. **Its unions are sparse.** Row B carries **22,785 / 36,389 / 45,786**
   candidates over the same 55 map sheets against row A's 6,985 / 8,337 /
   9,173 — about five times the count — so it is also the density stress test
   of the 10 m inheritance radius, which was validated on the gold standard at
   text-track densities and has never been exercised at this one.

Same method, same instrument, same constraints, zero API cost. The instrument
is the row A study's, parametrised by `--campaign` rather than copied:
`results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/inheritance_ladder.py`.
Both pools' campaign records — verifier root, cell name, results home, carried
points — are the r2 script's own `CAMPAIGNS`, so nothing about either pool is
restated in the study.

Carried points, read from `results/gemini3-image-55map-2026-09-16/sweeps.json`
and the r2 script's table: arm 1 (0.15, k1) and (0.15, k3); arm 2 (0.88, k1)
and (0.88, k3).

## 2. What the match does

Source: `verify_k5_arm{1,2}` over the 45,786-candidate K = 5 union. Geometry
is shared by the two arms, so these statistics are arm-invariant by
construction.

| rung | union | matched | unmatched | p50 | p95 | p99 | max | exactly coincident |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| K = 1 | 22,785 | 22,219 | **566 (2.48 %)** | 2.960 m | 9.112 m | 11.299 m | 14.814 m | 4,191 |
| K = 3 | 36,389 | 36,308 | **81 (0.22 %)** | 0.687 m | 6.355 m | 9.233 m | 12.669 m | 15,405 |

Against row A's 50 of 6,985 (0.72 %) and 2 of 8,337 (0.024 %). **The drop
mechanism is three to nine times larger here**, and the K = 1 figure sits at
the top of the D2 options list's 0.6–2.6 % band rather than the bottom. Match
distances are also longer at K = 1 (p50 2.96 m against row A's 1.49 m), which
is what a denser first-pass union does: more candidates that the K = 5
clustering shifted or absorbed.

## 3. The density stress test: does the radius ever have to choose?

**Almost never — and the reason is structural, not lucky.**

| rung | ambiguous (> 1 K = 5 candidate within 10 m) | max in radius | decision-ambiguous | exact distance ties |
|---|---:|---:|---:|---:|
| row B, K = 1 | **12** (0.054 % of matched) | 2 | **0** | **0** |
| row B, K = 3 | **34** (0.094 % of matched) | 2 | **2** | **0** |
| row A, K = 1 | 2 (0.029 %) | 2 | 1 | 0 |
| row A, K = 3 | 2 (0.024 %) | 2 | 0 | 0 |

*Ambiguous* means the rule had a choice at all. *Decision-ambiguous* means the
candidates inside the radius did **not** all fall on the same side of the
carried threshold, so the tie-break — not the verifier — set that candidate's
decision. On row B that is **0 candidates of 22,219 at K = 1 and 2 of 36,308
at K = 3**.

**The tie-break, stated exactly.** The rule is the nearest Euclidean
neighbour (`cKDTree.query(..., k=1)`). Exact distance ties would fall to the
tree's internal ordering, which is deterministic per build but not part of the
documented API — so they are counted rather than relied upon, and **there are
none at any rung of either row**. The rule names a winner unaided every time.
It also names it decisively: the runner-up is a median **38.9 m** (K = 1) and
**39.4 m** (K = 3) further away than the winner, and even at the fifth
percentile the margin is about 15 m.

**Why density does not produce ambiguity** (`union_separation.json`). A union
is not a scatter of independent points: it is the centroid set of a greedy
star clustering at `DEDUP_METRES` = 20 m
(`scripts/h13_k_sensitivity.cluster_votes`, absorbing every point within that
radius). Two union candidates within 10 m of each other are therefore the
exception, and an ambiguous match needs exactly that.

| union | n | nn min | nn p01 | nn p50 | with a same-union neighbour within 10 m |
|---|---:|---:|---:|---:|---:|
| row B, K = 1 | 22,785 | 20.003 m | 20.613 m | 204.5 m | 0 (0.000 %) |
| row B, K = 3 | 36,389 | 9.158 m | 14.459 m | 56.7 m | 6 (0.017 %) |
| row B, K = 5 | 45,786 | 6.675 m | 13.110 m | 41.0 m | 66 (0.144 %) |
| row A, K = 5 | 9,173 | 8.496 m | 14.131 m | 147.4 m | 8 (0.087 %) |

Row B's K = 5 union is **3.6 times denser** than row A's by median
nearest-neighbour separation (41.0 m against 147.4 m), yet the share of source
candidates that *could* create an ambiguous match rises only from 0.087 % to
0.144 %. The radius survives the density increase because the clustering
radius that built the union is twice the inheritance radius. **That is the
invariant to watch**: if a future pool is ever unioned at a dedup radius at or
below 10 m, this guarantee lapses and the ambiguity counts must be re-measured
before inheritance is used on it.

## 4. Candidate-level agreement, on the matched candidates

| rung (threshold) | identical probability | mean \|Δp\| | \|Δp\| > 0.5 | flips | flip share |
|---|---|---:|---:|---:|---:|
| arm 1, K = 1 (0.15) | 14,474 / 22,219 = **65.1 %** | 0.0590 | 1,049 | 840 | 3.78 % |
| arm 1, K = 3 (0.15) | 26,964 / 36,308 = **74.3 %** | 0.0393 | 1,064 | 1,011 | 2.78 % |
| arm 2, K = 1 (0.88) | 12,847 / 22,219 = **57.8 %** | 0.0315 | 546 | 524 | 2.36 % |
| arm 2, K = 3 (0.88) | 21,058 / 36,308 = **58.0 %** | 0.0288 | 796 | 762 | 2.10 % |

Mean signed Δp (own-leg minus inherited): +0.0012, −0.0002, +0.0001, +0.0002.

The shape reproduces row A's almost exactly — arm 1 agreeing more often than
arm 2, K = 3 more often than K = 1, medians of zero, mean \|Δp\| under 0.06 —
and the arm 2 rows again sit beside the E89 replicate's own figures for two
independent invocations of that same verifier over one union (63.5 % identical,
2.46 % flips;
`results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20/agreement.json`).
Row B's arm 2 agrees slightly *less* (57.8–58.0 %), which is consistent with
its legs being batch-served rather than flex, and is a reminder that this row's
arm 2 comparison is a cross-route one.

**How a cell moves**, with the two mechanisms separated:

| rung | own-leg cell | of which unmatched (dropped) | own keeps / inherited drops | inherited keeps / own drops | inherited cell |
|---|---:|---:|---:|---:|---:|
| arm 1, K = 1 | 8,529 | **228** | 412 | 428 | 8,317 |
| arm 1, K = 3 | 5,538 | 0 | 185 | 178 | 5,531 |
| arm 2, K = 1 | 9,172 | **257** | 264 | 260 | 8,911 |
| arm 2, K = 3 | 5,941 | 0 | 124 | 141 | 5,958 |

This is the row's central structural fact. At **K = 3 the drop mechanism does
nothing at all** — the 81 unmatched candidates carry fewer than three votes, so
the carried point excludes them anyway — and the cells move only by
two-directional probability disagreement, exactly as both rungs of row A did.
At **K = 1 the drop mechanism removes 228 and 257 detections**, 2.7 % and 2.8 %
of the cell, and it is one-directional by construction.

## 5. The eight cells

Scored by `scripts/evaluate_detections.py` on the r2 board's recipe — the
8,541-tile frame, `inputs/vectors/references/best-available-gt-55maps-r2.geojson`,
fourteen buffers, BCa bootstrap 10,000 at seed 42, `--mcc`,
`--require-clean-inputs`. Precision, recall and F1 at 50 m; intervals BCa.

| rung | method | n | P | R | F1 @ 50 m | tile-MCC |
|---|---|---:|---|---|---|---|
| arm 1, K = 1 | own leg | 8,529 | 0.5293 [0.5211, 0.5373] | 0.8996 [0.8901, 0.9078] | 0.6664 [0.6593, 0.6734] | 0.7144 [0.6992, 0.7286] |
| arm 1, K = 1 | inherited | 8,317 | 0.5391 [0.5308, 0.5475] | 0.8936 [0.8842, 0.9024] | 0.6725 [0.6651, 0.6798] | 0.7112 [0.6960, 0.7257] |
| arm 1, K = 3 | own leg | 5,538 | 0.7647 [0.7544, 0.7746] | 0.8440 [0.8325, 0.8546] | 0.8024 [0.7943, 0.8101] | 0.7247 [0.7106, 0.7392] |
| arm 1, K = 3 | inherited | 5,531 | 0.7677 [0.7573, 0.7774] | 0.8462 [0.8348, 0.8571] | 0.8050 [0.7969, 0.8128] | 0.7250 [0.7108, 0.7392] |
| arm 2, K = 1 | own leg | 9,172 | 0.5140 [0.5059, 0.5217] | 0.9394 [0.9320, 0.9457] | 0.6644 [0.6572, 0.6712] | 0.7063 [0.6907, 0.7212] |
| arm 2, K = 1 | inherited | 8,911 | 0.5260 [0.5177, 0.5342] | 0.9340 [0.9265, 0.9406] | 0.6730 [0.6658, 0.6802] | 0.7129 [0.6978, 0.7279] |
| arm 2, K = 3 | own leg | 5,941 | 0.7495 [0.7392, 0.7596] | 0.8874 [0.8776, 0.8965] | 0.8127 [0.8050, 0.8201] | 0.7234 [0.7087, 0.7379] |
| arm 2, K = 3 | inherited | 5,958 | 0.7482 [0.7378, 0.7583] | 0.8884 [0.8786, 0.8974] | 0.8123 [0.8046, 0.8198] | 0.7236 [0.7090, 0.7381] |

**The precision bias is real here, and it is where the theory says it should
be.** Deltas, inherited minus own-leg:

| rung | ΔP | ΔR | ΔF1 | ΔMCC | detections dropped |
|---|---:|---:|---:|---:|---:|
| arm 1, K = 1 | **+0.0098** | −0.0060 | **+0.0061** | −0.0032 | 228 |
| arm 2, K = 1 | **+0.0120** | −0.0054 | **+0.0086** | +0.0066 | 257 |
| arm 1, K = 3 | +0.0030 | +0.0022 | +0.0026 | +0.0003 | 0 |
| arm 2, K = 3 | −0.0013 | +0.0010 | −0.0004 | +0.0002 | 0 |

At **K = 1**, where inheritance drops detections, precision rises on both arms
by about a point and recall falls by about half that: the dropped candidates
contain far more false positives than true ones, which is exactly the
dropped-candidate bias the D2 options list predicted, now measured. At
**K = 3**, where it drops nothing, the movements are the size of drift and
their signs disagree — row A's result, reproduced.

Row A saw none of this because its K = 1 rung drops only 40 and 35 detections
from an already-precise cell. **The bias is a function of how much the rung
drops and how much precision headroom the cell has**, and row B has both.

**The oracle tax.** Each inherited rung was swept over its own achievable
grid (19 / 60 / 28 / 87 points against the own-leg rungs' 20 / 60 / 26 / 84).
Inherited F1 oracles are +0.0051, +0.0027, +0.0077 and −0.0001 against the
own-leg oracles — the same pattern as the carried points, so the K = 1 gain is
not an artefact of the operating point.

## 6. The head-to-head tests

Paired tile-swap permutation, 10,000 permutations, seed 42, equal truth
vectors asserted on every pair; `tests.json`. Convention **own-leg minus
inherited**, so a positive difference favours the own-leg method.

| test | rung | ΔF1 | *p* | \|Δ\|/null SD | ΔMCC | *p* | \|Δ\|/null SD |
|---|---|---:|---:|---:|---:|---:|---:|
| H1 | arm 1, K = 1 | **−0.0061** | 0.0025 | 3.00 | +0.0033 | 0.4426 | 0.78 |
| H2 | arm 1, K = 3 | −0.0026 | 0.1328 | 1.50 | −0.0003 | 0.9285 | 0.10 |
| H3 | arm 2, K = 1 | **−0.0086** | < 0.0001 | 5.92 | −0.0066 | 0.1083 | 1.58 |
| H4 | arm 2, K = 3 | +0.0003 | 0.7773 | 0.27 | −0.0001 | 0.9849 | 0.04 |

Both K = 1 contrasts favour **inheritance** on micro-F1, consistently in sign
and at 3.0 and 5.9 null standard deviations. Neither K = 3 contrast is
resolvable — H4 at 0.27 null SDs is inside the drift band outright, and H2 at
1.50 null SDs and *p* = 0.13 is above its arm's drift contrast (about five
times +0.0005) but not separable from its own null, which is a different kind
of negative and is read as one in § 8. **Every tile-MCC contrast is inside or
at the edge of the band** (0.04–1.58 null SDs, all *p* ≥ 0.10): the effect is
micro-F1 only, which is what a precision-versus-recall trade at fixed tile
coverage looks like.

## 7. The ladder contrasts under each method (arm 2)

| test | contrast | ΔF1 | *p* | ΔMCC | *p* |
|---|---|---:|---:|---:|---:|
| L1 | K1 → K3, both own leg | +0.1483 | < 0.0001 | +0.0171 | 0.0004 |
| L2 | K1 → K3, both inherited | +0.1393 | < 0.0001 | +0.0107 | 0.0030 |
| L3 | K3 → K5, both own leg (what the current documents report) | +0.0180 | < 0.0001 | +0.0019 | 0.6372 |
| L4 | K3 → K5 under inheritance (pure) | +0.0183 | < 0.0001 | +0.0018 | 0.5639 |

Every ladder conclusion survives the method change, as on row A. Two
differences from row A are worth recording. First, **the K1 → K3 gain shrinks
under inheritance** (+0.1483 → +0.1393 F1, +0.0171 → +0.0107 MCC) — a direct
consequence of § 5: inheritance strengthens the K = 1 baseline, so the step up
to K = 3 has less to recover. Second, **L4's tile-MCC does not become readable
here** (+0.0018, *p* = 0.56) as it did on row A, because this row's K3 → K5
tile-MCC effect is genuinely near zero under either method, not merely masked
by drift.

## 8. Verdict

**Does inheritance differ from own-leg verification by more than drift?**
**At K = 3, no. At K = 1, yes — on micro-F1, in inheritance's favour, on both
arms.**

Read against the E89 drift-only contrast as revised in
`reports/image-2x2-tests-declaration-2026-09-19.md` § 5 caveat 1 (+0.0008
micro-F1, *p* = 0.4015, null SD 0.0009; −0.0005 tile-MCC, *p* = 0.8225, null SD
0.0016), with its rule that an effect is not claimable without a replicate arm
unless it exceeds the drift-only contrast by a clear margin:

- **K = 3, both arms**: −0.0026 and +0.0003 micro-F1, −0.0003 and −0.0001
  tile-MCC, at 0.04–1.50 null SDs, signs inconsistent, neither claimable. Row
  A's verdict reproduces exactly. Since the arm 1 floor was measured this
  bullet needs one distinction it could not draw at publication: H4 (arm 2,
  +0.0003) is inside its arm's drift band, while H2 (arm 1, −0.0026) is
  *outside* arm 1's +0.0005 band and fails instead on its own null at
  *p* = 0.1328. Both are negatives; only the first is a statement that the
  effect is the size of noise.
- **K = 1, both arms**: −0.0061 and −0.0086 micro-F1 at 3.0 and 5.9 null SDs,
  *p* = 0.0025 and < 0.0001. That is **7.6 and 10.8 times** the drift
  contrast — both ratios taken against arm 2's +0.0008, the only floor
  measured when this note was published. Read each against its own arm's
  floor, now that arm 1's is measured at +0.0005, H1 is **12.7 times** drift
  and H3 is unchanged at 10.8. The contrasts are consistent in sign across two
  arms and two verifier models, and mechanically explained — 228 and 257
  dropped detections, precision up about a point, recall down about half a
  point. This is claimable, and it is not drift.
- **tile-MCC, everywhere**: inside or at the edge of the band. No tile-MCC
  claim follows from any of these four contrasts, in either direction.

**What it means, stated carefully.** The inherited K = 1 cell is not a *better*
cell; it is a **smaller and more precise** one. Inheritance at K = 1 over a
low-precision union acts as an extra filter — it silently removes the
candidates the K = 5 clustering did not corroborate — worth about +0.01
precision for about −0.006 recall. Three consequences:

1. **Cross-model comparison at a fixed rung is unaffected**, which is D2's own
   point and the benchmark's actual purpose: every model's K = 1 rung carries
   the same filter, so the level shift is common and cancels.
2. **Comparing an inherited rung against an own-leg rung is not safe at
   K = 1.** Anything that mixes the two methods at that rung — a legacy cell
   read beside a new one, a board row carried forward — inherits a bias of
   about +0.006 to +0.009 F1 in the inherited cell's favour.
3. **Ladder contrasts that start at K = 1 are compressed** under inheritance
   (§ 7), by about 6 % of the gain on this row. A K1 → K3 claim should state
   which method produced both rungs.

**Is inheritance safe to adopt for the benchmark?** **Yes**, on the evidence of
both rows, provided the K = 1 caveat above is carried with it. It is
indistinguishable from own-leg verification wherever the drop mechanism is
inert (both rows at K = 3; row A at both rungs), the 10 m radius is never
asked to make an ambiguous choice even at five times the candidate density
(§ 3), and where it does bite it does so in a direction that is understood,
measured, and common to every model at that rung.

**Two qualifications, as on row A.** This row's **arm 1 verifier
(`gemini-3-flash-preview`, minimal) now has a measured drift floor of its
own** — it had none when this note was published, and H1's micro-F1 result
was admitted only because its arm 2 twin (H3) was larger, in the same
direction, on a verifier whose floor *was* measured. The arm 1 floor was
measured at full scale on 2026-09-20: a **drift-only contrast of +0.0005
micro-F1 (*p* = 0.5773, null SD 0.0008) and +0.0001 tile-MCC (*p* = 0.9310,
null SD 0.0015)**
(`results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20/findings.md`
§ 6.1; declaration § 5 caveat 1 Scope). **H1 no longer needs the borrowed
warrant**: its −0.0061 micro-F1 is about **twelve times** that drift contrast
and 3.0 null SDs at *p* = 0.0025, so it clears the rule on its own arm's
footing, and H3's agreement in sign and size now corroborates it rather than
carrying it. H2's −0.0026 is about five times drift but only 1.50 null SDs at
*p* = 0.1328, so it stays unclaimed — the margin rule is necessary, not
sufficient, and an effect still has to be resolvable against its own null.
On tile-MCC nothing changes: arm 1's measured tile-MCC drift contrast is
+0.0001, near enough to zero that ratios against it carry no information, and
every tile-MCC row here remains inside or at the edge of its own null.

Two limits on that upgrade, both recorded rather than assumed away. The arm 1
band is measured over the **3.7 row's** 9,173-candidate union, not this row's
22,785–45,786-candidate ones, so carrying it here assumes the verifier's
re-invocation behaviour does not depend on the candidate set it is shown —
plausible for a per-candidate call at T = 0, and untested. And this row's
**arm 2 legs are batch-served**, so its arm 2 comparisons are cross-route. The
2026-09-19 batch-versus-flex probe found the route indistinguishable from
same-route drift (declaration § 5 caveat 2), and both replicate pairs are
themselves batch-against-flex, which makes each floor if anything an
over-estimate.

## 9. Artefacts

| file | what it holds |
|---|---|
| `ladder.json` | Per rung and arm: union and match counts, distance quantiles, the ambiguity block, the agreement block, the carried and oracle sweep rows, and the own-leg rows they are compared against. |
| `union_separation.json` | Within-union nearest-neighbour distances for all three unions — the ambiguity capacity of the source. |
| `sweep_G3IMG-ARM{1,2}-K{1,3}-inherited.csv` | Each inherited rung's full achievable-point sweep, same columns as the campaign's sweep CSVs. |
| `cells/G3IMG-ARM{1,2}-K{1,3}-carried-inherited/` | The four inherited cells: detections, `evaluation.json`/`.csv`/`.md`, `score.log`. |
| `cells_manifest.json` | The four cells, their arms, rungs and operating points. |
| `tests.json` | H1–H4 and L1–L4 on both metrics, with the per-cell tile confusions. |

The instrument lives with the row A study, which it also still serves:
`results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/inheritance_ladder.py`,
run here as `--campaign g3`.

## Changelog

### 2026-09-20 — Re-read against the arm 1 verifier's measured drift floor

**Trigger**:
`results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20/findings.md`
§ 6.1 — a full-scale replicate of the arm 1 verifier
(`gemini-3-flash-preview`, `minimal`, T = 0), the seat this row's § 8 recorded
as having no measured drift floor at all. Its drift-only contrast is
**+0.0005 micro-F1** (*p* = 0.5773, null SD 0.0008) and **+0.0001 tile-MCC**
(*p* = 0.9310, null SD 0.0015).

**What changed.** Wording, and one ratio stated beside the original rather
than in place of it.

| reading | at publication | now |
|---|---|---|
| H1's warrant | claimable only because H3, its arm 2 twin, is larger and in the same direction on a verifier whose floor *is* measured | claimable **on its own arm's footing**: −0.0061 is about **12.7×** the arm 1 drift contrast at 3.0 null SDs, *p* = 0.0025; H3 now corroborates rather than carries it |
| H1's drift ratio | 7.6× (against arm 2's +0.0008, the only floor then measured) | 7.6× retained as the published figure, **12.7×** added against arm 1's own floor |
| H2's negative | "inside the band" | **outside** arm 1's +0.0005 band at about 5×, unresolvable against its own null (*p* = 0.1328, 1.50 null SDs) — a different kind of negative, and still not claimed |
| H4's negative | "inside the band" | unchanged: inside arm 2's band at 0.27 null SDs |

**What did NOT change.** No number in H1–H4 or L1–L4, no cell, no verdict, no
adoption recommendation, and no tile-MCC reading — arm 1's measured tile-MCC
drift contrast is +0.0001, near enough to zero that ratios against it carry no
information, so every tile-MCC row stands exactly as published, inside or at
the edge of its own null. Two limits are recorded with the upgrade: the arm 1
band is measured over the **3.7 row's** 9,173-candidate union rather than this
row's much larger ones, so carrying it here assumes the verifier's
re-invocation behaviour does not depend on the candidate set; and this row's
arm 2 legs remain batch-served, so its arm 2 comparisons remain cross-route.

Commit: `e1a9d8f8e`.

### 2026-09-20 — Original publication

First publication, executing the PI's ruling that the row A head-to-head
(`results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/findings.md`)
be repeated on the Gemini 3 image row, with particular attention to the
density stress test that note's § 9 proposed.

State at publication: the four inherited rungs were derived from
`verify_k5_arm{1,2}` at the 10 m radius (unmatched 566 of 22,785 at K = 1,
81 of 36,389 at K = 3), swept over 194 achievable points in total,
materialised at the campaign's own carried points, scored on the r2 board's
engine recipe, and tested at 10,000 permutations and seed 42.

Verdict: inheritance is indistinguishable from own-leg verification at K = 3
(both arms inside the E89 drift band, signs inconsistent — row A's result
reproduced) but **differs at K = 1**, where it drops 228 and 257 detections and
gains +0.0061 and +0.0086 micro-F1 at 3.0 and 5.9 null standard deviations,
with precision up about a point and recall down about half a point on both
arms. The dropped-candidate precision bias the D2 options list called
unmeasured is therefore **real, one-directional, and confined to the rung where
the drop mechanism bites**. Tile-MCC shows nothing anywhere. The 10 m radius
passed the density stress test: 12 and 34 ambiguous matches (0.05–0.09 %), never
more than two candidates in the radius, no exact distance ties, and 0 and 2
decision-ambiguous cases — because the unions are built by a greedy star
clustering at twice the inheritance radius.

No campaign cell, manifest, board or signed row was modified; every artefact
lives in this directory. Commits: `2ba1914b6` (ladder, materialisation and the
parametrised instrument), `a14d218ee` (scores and tests).
