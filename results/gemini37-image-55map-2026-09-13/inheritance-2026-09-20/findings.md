# Inheritance against own-leg verification on the 3.7 image row

> **Last revised**: 2026-09-20 (§ 8 and § 9 re-read against the arm 1
> verifier's now-measured drift floor — no number in this note moved).
> Prior: 2026-09-20 (the instrument parametrised to serve both pools of the
> image 2 x 2, and the ambiguity and union-separation measurements added);
> 2026-09-20 (original publication). See [§ Changelog](#changelog) for
> revision history.

## 1. The question

The PI ruled on 2026-09-20 that **inheritance is the project's
verifier-ladder method** (`planning/pi-decisions-2026-09-20.md`, D2): one
verifier leg is run over the top-rung union, and every lower-rung candidate
takes the probability of its nearest top-rung candidate within 10 m, with
unmatched candidates counted and excluded from scoring. That is what
`scripts/stride55_ladder.py` does for the Gemini 3 text row (its docstring
lines 16-17: "probability inheritance by nearest K = 10 candidate within 10 m
(unmatched clusters counted, excluded from scoring, included in cost)") and
what `scripts/gemini37_arm_ladder.py` does for the 3.7 text row
(`results/gemini37-55map-2026-08-31/ladder/ladder.json`, `inherit_tol_m`
10.0, unmatched 54 at N = 1 and 3 at N = 3;
`results/gemini37-55map-2026-08-31/findings.md` lines 93-97).

The 3.7 **image** campaign departed from it. It ran a *separate verifier leg
per rung* — `verify_k1_arm{1,2}`, `verify_k3_arm{1,2}`, `verify_k5_arm{1,2}`,
six legs over three unions — so its K = 1 and K = 3 cells are own-leg cells.
The D2 options list records the cost of the choice the project is now making
in the other direction: inheritance "drops unmatched candidates, 0.6-2.6 %,
biasing lower-rung precision upward by **an unmeasured amount**".

This note measures it. Both methods are applied to the *same candidates* at
the *same carried operating points* and scored on the *same instrument*, so
the eight cells differ in exactly one thing: how a candidate got its
probability.

Everything here is derived at zero API cost from legs that already exist.

## 2. What was run

`inheritance_ladder.py` in this directory. Every primitive is imported from
`scripts/gemini37_image_55map_r2.py` — the frames, the tile re-stamp, the
materialiser, the achievable grid, the per-tile machinery, the permutation
tests and the engine recipe — so the inherited cells land on the instrument
the own-leg cells were scored on. Nothing in `scripts/` was modified.

**The matching rule.** `stride55_ladder.py` does not expose its matching as a
function: the rule is inline (`cKDTree(...).query(..., k=1)` then
`d <= INHERIT_TOL_M`, lines 435-440 of that file, repeated at lines 201-207 of
`scripts/gemini37_arm_ladder.py`). It is therefore **reproduced** here rather
than imported, with one exception — `INHERIT_TOL_M` itself is imported from
`stride55_ladder`, so the 10 m radius is provably the same constant and not a
retyped one.

**One structural difference from the text track.** There the lower-rung unions
are *rebuilt* from the first-N passes, because no lower-rung union was ever
built. Here the campaign's lower-rung unions already exist and are committed
(`union_k1.geojson` 6,985, `union_k3.geojson` 8,337, `union_k5.geojson`
9,173), and the own-leg cells this comparison is against were built from
exactly those crop manifests. Rebuilding them would have turned the comparison
from "two verification methods over one candidate set" into "two verification
methods over two candidate sets". So the unions are taken as given and only
the probabilities differ.

## 3. What the match does

Source: `verify_k5_arm{1,2}` over the 9,173-candidate K = 5 union. The
geometry is shared by the two arms — the unions are the same candidates — so
the match statistics are arm-invariant by construction.

| rung | union | matched | unmatched | p50 | p95 | max | exactly coincident |
|---|---:|---:|---:|---:|---:|---:|---:|
| K = 1 | 6,985 | 6,935 | 50 (0.72 %) | 1.487 m | 6.494 m | 14.615 m | 399 |
| K = 3 | 8,337 | 8,335 | 2 (0.024 %) | 0.561 m | 3.838 m | 10.426 m | 1,467 |

The distance quantiles are over *all* union candidates, matched and not. Every
matched candidate is within 10 m by construction, so a maximum above 10 m is
an unmatched candidate. The unmatched share is at the bottom of the D2 options
list's 0.6-2.6 % band, and the text track's own figures are the same order
(54 of 8,426 at N = 1, 3 of 11,079 at N = 3).

These are the counts in `ladder.json`; the K = 3 rung's two unmatched
candidates are the whole of the "dropped candidate" mechanism at that rung.

**The radius is never asked to choose.** Only **2** candidates at each rung
(0.03 % and 0.02 % of the matched set) have more than one K = 5 candidate
inside the 10 m radius, never more than two, and of those only one — at
arm 1, K = 1 — has neighbours that disagree about the carried decision. There
are **no exact distance ties**, so the rule's tie-break (nearest Euclidean
neighbour wins) names a winner unaided in every case. The reason is
structural and is measured in `union_separation.json`: a union is the centroid
set of a greedy star clustering at `DEDUP_METRES` = 20 m
(`scripts/h13_k_sensitivity.cluster_votes`), so same-union candidates closer
than 10 m to each other are rare — **8 of 9,173** in this row's K = 5 union
(0.087 %), against a median nearest-neighbour separation of 147 m. The
[Gemini 3 row](../../gemini3-image-55map-2026-09-16/inheritance-2026-09-20/findings.md)
tests the same radius at about five times the candidate count.

## 4. Candidate-level agreement, on the matched candidates

The decision threshold is the rung's carried `prob_t`. "Flips" are
probability-threshold flips over every matched candidate; the vote-gated
columns in `ladder.json` are the subset that reaches the cell.

| rung (threshold) | identical probability | mean abs delta-p | median | abs delta-p > 0.5 | flips | flip share |
|---|---|---:|---:|---:|---:|---:|
| arm 1, K = 1 (0.10) | 4,670 / 6,935 = **67.3 %** | 0.0830 | 0.0 | 526 | 290 | 4.18 % |
| arm 1, K = 3 (0.10) | 6,217 / 8,335 = **74.6 %** | 0.0603 | 0.0 | 444 | 303 | 3.64 % |
| arm 2, K = 1 (0.88) | 4,347 / 6,935 = **62.7 %** | 0.0283 | 0.0 | 167 | 180 | 2.60 % |
| arm 2, K = 3 (0.88) | 5,183 / 8,335 = **62.2 %** | 0.0288 | 0.0 | 201 | 226 | 2.71 % |

Mean signed delta-p (own-leg minus inherited): -0.0007, -0.0045, -0.0028,
+0.0010.

**The headline of this section.** Compare the arm 2 rows with the E89 floor's
own replicate — two independent invocations of *that same verifier* over the
*same* 9,173-candidate union
(`results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20/agreement.json`,
quoted in `reports/image-2x2-tests-declaration-2026-09-19.md` § 5 caveat 1):
**63.5 %** identical, **2.46 %** decision flips at 0.90, **2.03 %** with
absolute delta-p above 0.5. The inheritance rows sit on top of those numbers —
62.2-62.7 % identical, 2.60-2.71 % flips at 0.88, 2.41 % with absolute delta-p
above 0.5. Inheriting a probability from a neighbouring candidate within 10 m
disagrees with the own leg *no more than the verifier disagrees with itself*.
The inheritance error, at candidate level, is not separable from re-invocation
drift.

**How a cell moves.** Two mechanisms act, and `ladder.json` now separates
them exactly:

| rung | own-leg cell | of which unmatched (dropped) | own keeps / inherited drops | inherited keeps / own drops | inherited cell |
|---|---:|---:|---:|---:|---:|
| arm 1, K = 1 | 6,250 | 40 | 132 | 158 | 6,236 |
| arm 1, K = 3 | 5,437 | 0 | 61 | 80 | 5,456 |
| arm 2, K = 1 | 5,997 | 35 | 80 | 100 | 5,982 |
| arm 2, K = 3 | 5,357 | 0 | 52 | 69 | 5,374 |

The drop mechanism the D2 note worries about removes **40 and 35 detections at
K = 1 and none at all at K = 3**, while probability disagreement moves 121-290
candidates at every rung and does so in *both* directions. At K = 3 the
inherited cell is larger than the own-leg cell, not smaller.

## 5. The eight cells

Scored by `scripts/evaluate_detections.py` on the r2 board's recipe — the
8,541-tile frame, `inputs/vectors/references/best-available-gt-55maps-r2.geojson`,
fourteen buffers, BCa bootstrap 10,000 at seed 42, `--mcc`,
`--require-clean-inputs`. Precision, recall and F1 are at 50 m; the intervals
are BCa.

| rung | method | n | P | R | F1 @ 50 m | tile-MCC |
|---|---|---:|---|---|---|---|
| arm 1, K = 1 | own leg | 6,250 | 0.7642 [0.7532, 0.7751] | 0.9518 [0.9454, 0.9576] | 0.8477 [0.8402, 0.8550] | 0.7324 [0.7175, 0.7463] |
| arm 1, K = 1 | inherited | 6,236 | 0.7648 [0.7535, 0.7758] | 0.9504 [0.9439, 0.9564] | 0.8475 [0.8398, 0.8549] | 0.7300 [0.7153, 0.7440] |
| arm 1, K = 3 | own leg | 5,437 | 0.8678 [0.8580, 0.8772] | 0.9402 [0.9330, 0.9467] | 0.9025 [0.8961, 0.9087] | 0.7490 [0.7351, 0.7625] |
| arm 1, K = 3 | inherited | 5,456 | 0.8673 [0.8575, 0.8768] | 0.9430 [0.9360, 0.9493] | 0.9036 [0.8970, 0.9098] | 0.7475 [0.7336, 0.7609] |
| arm 2, K = 1 | own leg | 5,997 | 0.8007 [0.7903, 0.8109] | 0.9570 [0.9509, 0.9624] | 0.8719 [0.8650, 0.8784] | 0.7569 [0.7432, 0.7702] |
| arm 2, K = 1 | inherited | 5,982 | 0.8036 [0.7930, 0.8139] | 0.9580 [0.9521, 0.9633] | 0.8740 [0.8670, 0.8805] | 0.7574 [0.7437, 0.7710] |
| arm 2, K = 3 | own leg | 5,357 | 0.8908 [0.8820, 0.8993] | 0.9510 [0.9447, 0.9568] | 0.9199 [0.9142, 0.9254] | 0.7648 [0.7516, 0.7776] |
| arm 2, K = 3 | inherited | 5,374 | 0.8876 [0.8788, 0.8963] | 0.9506 [0.9443, 0.9564] | 0.9180 [0.9122, 0.9235] | 0.7621 [0.7488, 0.7753] |

Every inherited interval overlaps its own-leg interval on every metric.

**The precision prediction fails.** The dropped-candidate bias predicts
inherited precision at least own-leg precision at every rung. Measured, the
precision deltas (inherited minus own-leg) are **+0.0006, -0.0005, +0.0029,
-0.0032** — two up, two down, and the largest single movement is in the
*wrong* direction. Section 4 says why: the drop mechanism touches at most 40
detections, and is swamped by two-directional probability disagreement.

**The oracle tax.** Each inherited rung was swept over its own achievable
`(prob_t x min_votes)` grid (20 / 60 / 24 / 72 points against the own-leg
rungs' 20 / 63 / 24 / 72), so the tax is visible rather than assumed. There
is none to speak of, and its sign is not consistent either:

| rung | inherited F1 oracle | own-leg F1 oracle | delta |
|---|---|---|---:|
| arm 1, K = 1 | 0.8624 at (0.15, k1) | 0.8606 at (0.15, k1) | +0.0018 |
| arm 1, K = 3 | 0.9036 at (0.10, k3) | 0.9025 at (0.10, k3) | +0.0010 |
| arm 2, K = 1 | 0.8765 at (0.95, k1) | 0.8742 at (0.95, k1) | +0.0023 |
| arm 2, K = 3 | 0.9198 at (0.95, k3) | 0.9206 at (0.90, k3) | -0.0007 |

(These are sweep-instrument figures from `ladder.json`, not engine figures;
the sweep and the engine agree on the carried cells to four decimal places and
on the tile confusion exactly.)

## 6. The head-to-head tests

Paired tile-swap permutation, 10,000 permutations, seed 42, equal truth
vectors asserted on every pair; `tests.json`. The convention is **own-leg
minus inherited**, so a positive difference favours the own-leg method.

| test | rung | delta F1 | *p* | vs null SD | delta MCC | *p* | vs null SD |
|---|---|---:|---:|---:|---:|---:|---:|
| H1 | arm 1, K = 1 | +0.0002 | 0.9030 | 0.13 | +0.0024 | 0.3871 | 0.86 |
| H2 | arm 1, K = 3 | -0.0010 | 0.3475 | 0.95 | +0.0015 | 0.4096 | 0.84 |
| H3 | arm 2, K = 1 | -0.0021 | 0.0869 | 1.73 | -0.0005 | 0.8487 | 0.21 |
| H4 | arm 2, K = 3 | +0.0019 | 0.0735 | 1.80 | +0.0027 | 0.1654 | 1.41 |

No contrast reaches *p* < 0.05 on either metric, the signs are inconsistent
across rungs and arms on both metrics, and the largest differences in each
direction are at the same two rungs of the same arm.

## 7. The ladder contrasts under each method (arm 2)

| test | contrast | delta F1 | *p* | delta MCC | *p* |
|---|---|---:|---:|---:|---:|
| L1 | K1 to K3, both own leg | +0.0480 | < 0.0001 | +0.0078 | 0.0022 |
| L2 | K1 to K3, both inherited | +0.0440 | < 0.0001 | +0.0046 | 0.0125 |
| L3 | K3 to K5, both own leg (what the current documents report) | +0.0071 | < 0.0001 | +0.0012 | 0.6141 |
| L4 | K3 to K5 under inheritance (pure) | +0.0090 | < 0.0001 | +0.0039 | 0.0061 |

L4 is *pure* because under inheritance the K = 5 cell **is** the source leg —
there is nothing to derive at the top rung — so both sides of the contrast
draw their probabilities from a single verifier invocation and no
re-invocation drift enters it. That is precisely the advantage the D2 options
list claims for inheritance ("rung contrasts free of re-invocation drift"),
and it is visible here: L3's tile-MCC reading is +0.0012 at *p* = 0.61, which
the declaration's revised caveat 1 now reads as uninformative because it sits
inside the drift band; L4's is +0.0039 at *p* = 0.0061 and 2.65 null standard
deviations, on a contrast that has no drift in it to hide behind. The micro-F1
gain, already confirmed claimable by the PI on the replicate evidence
(+0.0079 against drift's +0.0008), comes out slightly *larger* under
inheritance (+0.0090) than under the own-leg pairing (+0.0071).

Every ladder conclusion the campaign currently reports survives the method
change: both directions hold, both K1-to-K3 contrasts are overwhelming, and
the K3-to-K5 F1 gain is preserved.

## 8. Verdict

**Does inheritance differ from own-leg verification by more than drift?** No —
not on either metric, at either rung, in either arm.

The floor to read against is the E89 drift-only contrast as revised in
`reports/image-2x2-tests-declaration-2026-09-19.md` § 5 caveat 1: the same
union at the same operating point scored twice from two invocations of the
same verifier moves micro-F1 by **+0.0008** (*p* = 0.4015, null SD 0.0009) and
tile-MCC by **-0.0005** (*p* = 0.8225, null SD 0.0016) — "of order 0.001 F1
and plus or minus 0.001 tile-MCC". The rule attached to it: an effect is not
claimable without a replicate arm unless it exceeds the drift-only contrast
**by a clear margin**, the worked claimable example being about ten times
drift at 5.4 null standard deviations.

The four head-to-head differences are 0.0002-0.0021 micro-F1 and
0.0005-0.0027 tile-MCC, at 0.13-1.80 and 0.21-1.41 null standard deviations.
The two largest F1 differences (H3 -0.0021, H4 +0.0019) are about 2.4 times
drift — nowhere near the clear margin the rule demands, and they point in
**opposite directions**, which a systematic method bias would not do. On
tile-MCC every difference is inside or at the edge of the band. Nothing here
is claimable as a method effect, and the pattern is what one would expect if
the entire difference between the two methods were verifier nondeterminism —
which § 4 shows it is, candidate by candidate.

**Which way, and on which metric?** Own-leg is nominally higher on tile-MCC at
three of four rungs (+0.0024, +0.0015, -0.0005, +0.0027) and on micro-F1 at
two of four. **The dropped-candidate precision bias is not detectable**: it
predicts inherited precision at least own-leg precision, and the measured
precision deltas are sign-inconsistent with the largest movement the other way
(§ 5). On this row the bias is smaller than the noise it would have to be read
through.

**Is inheritance safe to adopt for the benchmark on this evidence?** Yes, for
this row, with two qualifications stated plainly:

1. **The evidence is one pool.** Four rung-by-arm head-to-heads on one
   proposer pool, one corpus and one pair of rungs, each resting on single
   verifier legs. This is enough to say inheritance costs nothing measurable
   *here*; it is not enough to say it costs nothing anywhere.
2. **Arm 1's drift floor is now measured, and H1 and H2 sit in it.** When
   this note was first published the declaration's caveat 1 scope note said
   the floor was measured on `gemini-3.7-flash` at low thinking and T = 0
   (arm 2) only, so an arm 1 difference of order 0.001 was *uncharacterised*
   rather than known to be drift, and H1 and H2 had to be read as "no effect
   large enough to see" rather than "drift". That gap is closed: the arm 1
   verifier (`gemini-3-flash-preview`, `minimal`, T = 0) has its own
   full-scale replicate, and its **drift-only contrast is +0.0005 micro-F1
   (*p* = 0.5773) and +0.0001 tile-MCC (*p* = 0.9310)**
   (`results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20/findings.md`
   § 6.1; declaration § 5 caveat 1 Scope). H1's +0.0002 micro-F1 is *below*
   that contrast and H2's −0.0010 about twice it, both null at 0.13 and 0.95
   null standard deviations — so on micro-F1 these two now read as **inside
   the arm 1 drift band**, which is a stronger statement than the one this
   note could make at publication.

   Two limits on that upgrade. The tile-MCC readings do **not** follow the
   same route: arm 1's tile-MCC drift contrast came out at +0.0001, so close
   to zero that ratios against it are meaningless, and H1's +0.0024 and H2's
   +0.0015 are nominally many times it while sitting at 0.86 and 0.84 null
   SDs with *p* = 0.39 and 0.41. The declaration's margin rule is a
   *necessary* condition, not a sufficient one — an effect still has to be
   resolvable against its own null — and where the measured drift contrast
   lands near zero the null SD is the yardstick that means anything. And the
   arm 1 band is measured on this row's own 9,173-candidate union, so
   carrying it to another pool is an assumption rather than a measurement.

The D2 recommendation to **keep the own-leg cells as replicates** is well
founded and should stand: they are what makes this measurement possible, they
are already paid for, and on arm 2 they are the only independent re-invocation
the row has at K = 1 and K = 3.

## 9. What the same measurement on the Gemini 3 row would add

Row B's three unions are **22,785 / 36,389 / 45,786** candidates
(`outputs/gemini3-image-55map-2026-09-16/verifier/g384_ov192_55map_g3img/union_k{1,3,5}.geojson`),
and all six of its verifier legs already exist (`verify_k{1,3,5}_arm{1,2}`), so
the same measurement is another zero-API job. Row A's whole chain — inherit,
sweep, materialise, score, test — took about eight minutes of sapphire
wall-clock; row B's unions are roughly five times larger, so budget well under
an hour.

It would add four things this row cannot give:

1. **A second pool.** The adoption decision is for the benchmark, which spans
   both rows of the image 2 x 2. One pool is a single observation.
2. **A hard test of the drop mechanism.** Row B's K = 1 cell over-generates
   badly (F1 0.66 against row A's 0.87; declaration § 5 caveat 4). The
   dropped-candidate precision bias should be largest on a low-precision
   candidate set — exactly the case this row does not contain.
3. **A density stress test of the 10 m radius.** Row B carries 45,786
   candidates over the same 55 map sheets against row A's 9,173 — five times
   the candidate density, so the mean spacing between candidates is much
   smaller and a nearest neighbour within 10 m is correspondingly more likely
   to belong to a *different* feature. The 10 m radius was validated at
   plus or minus 0.008 on the gold standard at text-track densities; it has
   never been exercised at this one, and the unmatched share and
   match-distance quantiles there are unmeasured.
4. **A second arm-2 reading with the floor that exists.** Row B's arm 2 is
   the same `gemini-3.7-flash` verifier whose drift floor is measured, so its
   head-to-head would be interpretable in the same units as H3 and H4 here,
   doubling the arm-2 evidence.

What it would *not* fix, **as this section stood on publication**: row B's
arm 1 is the Gemini 3 verifier, which then had no measured drift floor, so an
arm-1 difference of order 0.001 would have remained uncharacterised there too.
That limitation has since lapsed — the arm 1 verifier's floor was measured on
2026-09-20 (+0.0005 micro-F1, +0.0001 tile-MCC;
`../replicate-k5-arm1-batch-2026-09-20/findings.md` § 6.1) — with the
qualification in § 8 that it is measured over *this* row's union, so applying
it to row B's much larger and lower-precision unions is an assumption.

## 10. Artefacts

| file | what it holds |
|---|---|
| `inheritance_ladder.py` | The instrument. Stages `ladder`, `score`, `tests`. |
| `ladder.json` | Per rung and arm: union and match counts, distance quantiles, the agreement block, the carried and oracle sweep rows, and the own-leg rows they are compared against. |
| `sweep_IMG-ARM{1,2}-K{1,3}-inherited.csv` | Each inherited rung's full achievable-point sweep, same columns as the campaign's sweep CSVs. |
| `cells/IMG-ARM{1,2}-K{1,3}-carried-inherited/` | The four inherited cells: detections, `evaluation.json`/`.csv`/`.md`, `score.log`. |
| `cells_manifest.json` | The four cells, their arms, rungs and operating points. |
| `tests.json` | H1-H4 and L1-L4 on both metrics, with the per-cell tile confusions. |

## Changelog

### 2026-09-20 — Re-read against the arm 1 verifier's measured drift floor

**Trigger**:
`results/gemini37-image-55map-2026-09-13/replicate-k5-arm1-batch-2026-09-20/findings.md`
§ 6.1 — a full-scale replicate of this row's arm 1 K = 5 verifier leg, which
measures the drift floor this note's § 8 qualification 2 and § 9 closing
paragraph both recorded as missing. The arm 1 drift-only contrast is
**+0.0005 micro-F1** (*p* = 0.5773, null SD 0.0008) and **+0.0001 tile-MCC**
(*p* = 0.9310, null SD 0.0015).

**What changed.** Wording only, in two places. § 8 qualification 2 no longer
says arm 1 has no measured floor; it gives the floor, and upgrades H1
(+0.0002 micro-F1) and H2 (−0.0010) from "no effect large enough to see" to
**inside the arm 1 drift band** on micro-F1, which is the stronger statement
this note could not make at publication. § 9's closing paragraph is marked as
the position at publication and records that the limitation has since lapsed.

**What did NOT change.** No number in H1–H4 or L1–L4, no cell, no verdict, and
not the adoption recommendation. Two limits are added rather than removed: the
tile-MCC readings are **not** upgraded, because arm 1's measured tile-MCC
drift contrast (+0.0001) sits so near zero that ratios against it carry no
information and H1's +0.0024 and H2's +0.0015 remain null at 0.86 and 0.84
null SDs — the declaration's margin rule is necessary, not sufficient; and the
arm 1 band is measured over this row's own union, so carrying it to another
pool stays an assumption.

Commit: `TBDINH`.

### 2026-09-20 — Instrument parametrised; ambiguity and separation measured

**Trigger**: the PI ruled that the same head-to-head be run on the Gemini 3
image row, which this note's § 9 had named as the measurement that would close
the adoption question.

`inheritance_ladder.py` gained a `--campaign` flag selecting one of the r2
script's own `CAMPAIGNS` records, so one instrument now serves both pools; the
default stays `g37`. Under the parametrised code this row's four cells and four
sweep CSVs re-derived **byte for byte**, and `ladder.json`'s diff was 68 lines
added and none removed.

Two measurements were added and are reported in § 3 above: an **ambiguity**
block (how often the 10 m radius offers a choice of K = 5 candidates, whether
the alternatives disagree about the carried decision, how many are exact
distance ties, and how decisive the margin is) and a **`separation` stage**
writing `union_separation.json` (within-union nearest-neighbour distances,
which set how ambiguous the radius can be at all).

| claim | before | after |
|---|---|---|
| every cell metric, agreement statistic and test in this note | — | unchanged |
| ambiguous matches, row A | not measured | 2 per rung (0.02–0.03 %), max 2 in radius |
| decision-ambiguous matches, row A | not measured | 1 (arm 1, K = 1), 0 elsewhere |
| exact distance ties, row A | not measured | 0 at every rung |
| K = 5 union candidates with a same-union neighbour within 10 m | not measured | 8 of 9,173 (0.087 %) |

Landed in `2ba1914b6`. Nothing else in this note changed.

### 2026-09-20 — Original publication

First publication, executing the PI's D2 ruling of the same day
(`planning/pi-decisions-2026-09-20.md`): inheritance is the project's
verifier-ladder method, and the 3.7 image row's K = 1 and K = 3 rungs were to
be derived by inheritance from its K = 5 legs and tested head-to-head against
the own-leg cells that already existed.

State at publication: the four inherited rungs were derived from
`verify_k5_arm{1,2}` at the 10 m radius (unmatched 50 of 6,985 at K = 1, 2 of
8,337 at K = 3), swept over 176 achievable points in total, materialised at
the campaign's own carried points, scored on the r2 board's engine recipe, and
tested at 10,000 permutations and seed 42 against the own-leg cells and across
the arm 2 ladder. Verdict: inheritance differs from own-leg verification by
**less than the E89 drift floor** on both metrics at every rung and arm
(absolute delta F1 at most 0.0021, absolute delta MCC at most 0.0027, all
*p* at least 0.07, signs inconsistent), the predicted dropped-candidate
precision bias is **not detectable**, and every ladder conclusion the campaign
reports survives the method change — with the K3-to-K5 tile-MCC contrast
becoming readable under inheritance (+0.0039, *p* = 0.0061) where the own-leg
pairing left it inside the drift band (+0.0012, *p* = 0.61).

No campaign cell, manifest, board or signed row was modified; every artefact
lives in this directory. Commits: `62b13e6fd` (ladder and materialisation),
`3fc3f0751` (scores and tests), `58500a739` (vote-gated flip counts, which
close the cell-size identity exactly and left every other number unchanged).
