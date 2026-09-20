# Arm 1 K = 5 replicate: the Gemini 3 verifier's drift floor, measured

> **Last revised**: 2026-09-20 (original publication — the batch replicate of
> the arm 1 K = 5 verifier leg, its two cells, the four paired permutation
> tests, and the verdict against the declaration's replicate rule). See
> [§ Changelog](#changelog) for revision history.

## 1. The question and the rule it is answered against

The image-2x2 declaration's caveat 1
(`reports/image-2x2-tests-declaration-2026-09-19.md` § 5) measures the E89
re-invocation drift floor on **one** verifier. Its Scope paragraph says so
plainly: the floor is measured on `gemini-3.7-flash` at low thinking and
T = 0 — the arm 2 seat — and the arm 1 verifier
(`gemini-3-flash-preview`, `minimal`, T = 0) has **no measured floor**, so an
arm-1 difference of order 0.001 is *uncharacterised* rather than known to be
drift. Two documents lean on that absence: the 3.7 row's inheritance note
(`results/gemini37-image-55map-2026-09-13/inheritance-2026-09-20/findings.md`
§ 8) reads its H1 and H2 as "no effect large enough to see" rather than
"proven to be drift", and the Gemini 3 row's
(`results/gemini3-image-55map-2026-09-16/inheritance-2026-09-20/findings.md`
§ 8) admits H1's micro-F1 result only because its arm 2 twin H3 is larger and
in the same direction on a verifier whose floor *is* measured.

There is also an arm 1 effect waiting on the same rule. The 3.7 image pool
verified by the Gemini 3 verifier gains **+0.0105 micro-F1 @ 50 m** going from
the K = 3 carried point (0.10, k3) to the K = 5 carried point (0.10, k5), with
tile-MCC at **+0.0039**. Those point estimates follow from the campaign's own
sweep (`results/gemini37-image-55map-2026-09-13/sweeps.json`,
`rungs.IMG-ARM1-K3.carried` and `rungs.IMG-ARM1-K5.carried`: micro-F1
0.9025347 and 0.9130393, tile-MCC 0.7489984 and 0.7528612), but until this
note no paired test had been run on the pair and no floor existed to read one
against.

The rule the declaration attaches is a margin, not a threshold:

> A tile-swap permutation tests sampling variation over tiles, not verifier
> nondeterminism, so a difference of drift's own size can be "significant" and
> still be drift. **An effect is not claimable without a replicate arm unless
> it exceeds the drift-only contrast by a clear margin**; a null result remains
> uninformative about small effects.

This note supplies the arm 1 replicate arm and measures the arm 1 floor in
both of the forms caveat 1 now uses — the decision-flip rate with an interval,
and the drift-only contrast in metric units.

## 2. What was run

A second, independent invocation of the **same** verifier over the **same**
9,173-candidate K = 5 union — same crops (`…/crops_k5/`), same union
(`…/union_k5.geojson`), same model, thinking level and temperature — on the
Batch API rather than realtime flex, per the 2026-09-18 routing ruling. This
mirrors the arm 2 replicate of the same date exactly: same union, same rung,
same route change, same instrument.

| item | value |
|---|---|
| Leg | `outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img/verify_k5_arm1_replicate-batch-2026-09-20/` |
| Original leg | `…/verify_k5_arm1/` (realtime flex) |
| Model / thinking / temperature | `gemini-3-flash-preview` / minimal / 0.0 |
| Candidates | 9,173 of 9,173, 0 failed |
| Route | Batch API, three jobs |
| Data commit | `5778b5569` |
| Audited cost | **US$6.4909** (US$0.000708/candidate) |

The cost is the `STAGE TOTAL (audited)` line of
`scripts/audit_verifier_cost.py <leg> --tier flex`, re-run for this note and
reproduced as the tool printed it:

```text
  STAGE TOTAL (audited)                                       n=   9173             audited=$    6.4909  $0.000708/candidate
```

As on arm 2, the leg's own `run.meta.json` `cost_estimate` reads exactly
double — US$12.9819 — and the auditor marks it "do NOT use at a gate". The
audited figure is the one quoted. At US$0.000708 per candidate the arm 1 seat
costs about **64 %** of the arm 2 seat's US$0.001112 over the identical
candidate set.

"Same config" is checked at source rather than assumed. The two legs'
`run.meta.json` `configuration` blocks agree on every field that could move a
probability: `version` `verify_adversarial-text`, `model`
`gemini-3-flash-preview`, `instruction_file` `verify_adversarial.md`,
`system_instruction_hash` `2518d529…3497e15d`, `library_hash` `no_examples`,
`temperature` 0.0, `thinking_level` `minimal`, `max_output_tokens` 8192,
`include_example_images` true. The replicate's `execution_stats` record
`items_processed` 9,173 and `items_failed` 0 across three batch chunks of
4,000 / 4,000 / 1,173, all `JOB_STATE_SUCCEEDED` (`batch_jobs.json`).

One asymmetry between the legs is worth recording rather than smoothing over.
The **original flex leg needed 52 server-error retries** — `retries_total` 52,
`retries_server_error` 52, `parse_failures` 52, `empty_responses` 52 against
`finish_reason_counts` `{"success": 9173, "error": 52}` — where the batch
replicate needed none (`retries_total` 0). Both legs end with all 9,173
candidates answered and none failed, so nothing is missing from either side;
but 52 of the original's probabilities are second attempts, which is one more
small way in which "same verifier, different invocation" is not "same
verifier, same conditions". It runs in the same direction as the route
difference: this pair, like arm 2's, is batch-against-flex, so the band it
measures covers route and invocation together and is if anything an
over-estimate of same-route drift.

Every derived artefact below was produced by *importing*
`scripts/gemini37_image_55map_r2.py` — its `rung_frame` inputs, its
`assign_eval_frame_tiles` re-stamping, its `materialise` predicate, its
`achievable_points` grid, its `engine_command` recipe, its `load_frames`,
`read_detections`, `per_tile_arrays`, `tile_vectors`, `permutation_test_float`
and `permutation_test_mcc`. Nothing in `scripts/` was modified. The driver
beside this note, `replicate_k5_arm1.py`, is the arm 2 note's
`replicate_k5_arm2.py` **parametrised by arm**: one `Arm` record per verifier
seat carries its pair of invocations, its home, its label stem and its carried
threshold, so `--arm arm2` reproduces the arm 2 artefacts on this same code
path. The replicate therefore lands on the same instrument as the cells it is
compared against: the r2 reference (`best-available-gt-55maps-r2.geojson`,
5,018 points), the 8,541-tile evaluation frame, 50 m matching, BCa intervals
from 10,000 bootstrap draws at seed 42, `--mcc`, `--require-clean-inputs`.

## 3. Agreement between the two invocations

Computed over all 9,173 shared `candidate_id` keys (`agreement.json`). The
arm 2 column is that arm's committed pair of legs recomputed here read-only,
at the same three thresholds, so the comparison has a single source; nothing
in the arm 2 home was written or re-run (`agreement.json`, `arm2_reference`).

| statistic | **arm 1** (`gemini-3-flash-preview`, minimal) | arm 2 (`gemini-3.7-flash`, low) |
|---|---:|---:|
| n compared | 9,173 | 9,173 |
| identical probabilities | **7,507 = 81.84 %** | 5,826 = 63.51 % |
| chance-identical baseline | 20.06 % | 27.64 % |
| κ against that baseline | **0.7728** | 0.4957 |
| distinct probability values (original / replicate) | 20 / 19 | 24 / 26 |
| flips at **0.10** | 221 = 2.41 % | 218 = 2.38 % |
| flips at **0.50** | 332 = 3.62 % | 202 = 2.20 % |
| flips at **0.90** | 479 = **5.22 %** | 226 = 2.46 % |
| flips at the arm's **own carried point** | 221 = **2.41 %** (at 0.10) | 226 = 2.46 % (at 0.90) |
| Wilson 95 % on that flip rate | **[2.11 %, 2.74 %]** | [2.17 %, 2.80 %] |
| \|Δp\| > 0.5 | **268 = 2.92 %** | 186 = 2.03 % |
| mean \|Δp\| | 0.0371 | 0.0254 |
| median \|Δp\| | 0.0000 | 0.0000 |
| 90th percentile \|Δp\| | 0.05 | 0.03 |
| max \|Δp\| | 1.00 | 0.95 |

Four readings follow, and they do not all point the same way.

**At their own operating points the two verifiers are equally steady.** Arm 1
flips 2.41 % of decisions at 0.10 and arm 2 flips 2.46 % at 0.90; the Wilson
intervals, [2.11 %, 2.74 %] and [2.17 %, 2.80 %], overlap almost completely.
Whatever else differs between the seats, the thing caveat 1's flip rate was
introduced to bound is the same size on both.

**The higher identical share is real, not a vocabulary artefact.** Arm 1
agrees with itself exactly on 81.84 % of candidates against arm 2's 63.51 %,
and the obvious suspicion is that it simply answers on a shorter list of round
numbers — it uses 19–20 distinct values against arm 2's 24–26. The check is
the agreement the two legs would reach if each drew independently from its
own observed distribution of probabilities: **20.06 % for arm 1, 27.64 % for
arm 2**. Arm 1's chance baseline is *lower*, not higher, because arm 2
concentrates 48.3 % of its mass on the single value 0.98 where arm 1's
commonest value, 1.0, takes 37.7 %. Correcting for it widens the gap rather
than closing it: κ = 0.7728 against 0.4957. On the identical-value criterion
the Gemini 3 verifier at minimal thinking is genuinely the steadier of the
two.

**It is nevertheless the one with more large jumps.** \|Δp\| > 0.5 on 2.92 %
of candidates against arm 2's 2.03 %, mean \|Δp\| 0.0371 against 0.0254, and a
maximum of a full 1.00 — at least one candidate that one leg called certain
and the other called impossible — against arm 2's 0.95. The two facts are
consistent: arm 1 repeats itself exactly more often *and*, when it does not,
moves further. Its disagreement is concentrated in fewer, larger reversals
where arm 2's is spread over many small ones.

**Arm 1's flip rate depends on where the threshold is cut; arm 2's does not.**
Arm 1 runs 2.41 % → 3.62 % → 5.22 % across 0.10, 0.50 and 0.90 while arm 2 sits
at 2.38 % → 2.20 % → 2.46 %. That is a fact about the answer lattice, and the
flip anatomy in `agreement.json` shows it directly: of arm 1's 479 flips at
0.90, **242 (50.5 %)** are 0.95 ↔ 0.85 or 0.85 ↔ 1.00 — one-rung nudges on a
lattice whose rungs straddle the cut — and of its 221 flips at 0.10,
**161 (72.9 %)** are 0.05 ↔ 0.10, the same thing one rung apart. The
consequence for reading this table is that **a flip rate is only interpretable
at the threshold a cell is actually deployed at**. Comparing the two arms at
the common 0.90 would say arm 1 is twice as unsteady as arm 2; comparing each
at its own carried point says they are the same. The second comparison is the
one that bears on any cell this study reports, because no arm 1 cell is
materialised at 0.90.

No arm 1 equivalent of the 2026-09-19 batch-versus-flex probe exists: that
probe ran 200 candidates on the arm 2 verifier only
(`…/probe-batch-vs-flex-2026-09-19/README.md`), so the arm 1 column above has
no independent small-sample estimate beside it, where arm 2's has one.

## 4. The cells

All five are at 50 m on the r2 reference, BCa 10,000, seed 42. Replicate cells
are in `cells/` beside this note; the three comparators are the campaign's own
committed cells in `results/gemini37-image-55map-2026-09-13/cells/`.

| cell | point | n | P @ 50 m | R @ 50 m | F1 @ 50 m | tile-MCC |
|---|---|---:|---|---|---|---|
| **IMG-ARM1-K5-carried-replicate** | (0.10, k5) | 5,285 | 0.8904 [0.8812, 0.8993] | 0.9378 [0.9306, 0.9445] | **0.9135** [0.9075, 0.9193] | **0.7530** [0.7394, 0.7662] |
| IMG-ARM1-K5-carried (original) | (0.10, k5) | 5,297 | 0.8890 [0.8797, 0.8978] | 0.9384 [0.9311, 0.9450] | 0.9130 [0.9068, 0.9189] | 0.7529 [0.7394, 0.7662] |
| **IMG-ARM1-K5-f1-oracle-replicate** | (0.10, k5) | 5,285 | 0.8904 [0.8812, 0.8993] | 0.9378 [0.9306, 0.9445] | **0.9135** [0.9075, 0.9193] | **0.7530** [0.7394, 0.7662] |
| IMG-ARM1-K5-f1-oracle (original) | (0.10, k5) | 5,297 | 0.8890 [0.8797, 0.8978] | 0.9384 [0.9311, 0.9450] | 0.9130 [0.9068, 0.9189] | 0.7529 [0.7394, 0.7662] |
| IMG-ARM1-K3-carried (original) | (0.10, k3) | 5,437 | 0.8678 [0.8580, 0.8772] | 0.9402 [0.9330, 0.9467] | 0.9025 [0.8961, 0.9087] | 0.7490 [0.7351, 0.7625] |

Three observations before the tests.

**On this arm the F1 oracle IS the carried point, on both invocations.** The
replicate's achievable grid has 95 points (`sweep_IMG-ARM1-K5-replicate.csv`)
against the original's 100
(`results/gemini37-image-55map-2026-09-13/sweeps.json`,
`rungs.IMG-ARM1-K5.n_sweep_points`), and on both legs the best micro-F1 row is
(0.10, k5) — the carried point itself. So rows one and three of the table are
the same cell, as are rows two and four, and the carried-versus-oracle tax
that cost arm 2 +0.0012 F1 is **zero** here. Arm 2's oracle sat at (0.95, k5)
on both of its legs, one rung above its carried 0.90; arm 1's sits exactly on
its carried point on both of its legs. Either way the finding is the same one
and it is now shown twice: **re-invocation moves individual probabilities a
great deal and moves the selected operating point not at all.** The tile-MCC
oracle also coincides across the legs, at (0.15, k5) on both — tile-MCC
0.755880 on the replicate (`sweeps.json`,
`rungs.IMG-ARM1-K5-replicate.mcc_oracle`) and 0.754221 on the original
(`results/gemini37-image-55map-2026-09-13/sweeps.json`,
`rungs.IMG-ARM1-K5.mcc_oracle`).

The consequence for the test family is mechanical: test (d), which on arm 2
was a second, independent drift reading at a different operating point, is on
arm 1 **test (a) over again**. The driver detects this by comparing each
test's two sides cell-for-cell against every earlier test's and records it
under `degenerate_contrasts` in `tests.json`. Arm 1's drift band therefore
rests on **one** contrast where arm 2's rests on two.

**Every interval overlaps heavily.** The replicate's F1 CI [0.9075, 0.9193]
contains the original's point estimate and vice versa, and both K = 5 CIs
overlap the K = 3 CI. The BCa intervals here are unpaired and so are the wrong
instrument for a within-union contrast — which is exactly why the paired
permutation tests below exist.

**Precision, not recall, carries the K difference — as on arm 2.** K = 3 →
K = 5 buys +0.023 precision on the replicate (0.8678 → 0.8904) for −0.002
recall (0.9402 → 0.9378). Unanimity is the image pool's precision filter under
either verifier seat.

## 5. The four tests

Paired tile-swap permutation, 10,000 permutations, seed 42, over all 8,541
tiles, on both metrics, using the script's own `permutation_test_float` and
`permutation_test_mcc`. Truth vectors were asserted equal for every pair. Full
output with null means and standard deviations: `tests.json`.

### Micro-F1 @ 50 m

| test | A | B | F1 A | F1 B | observed Δ | *p* | null mean | null SD | \|Δ\|/SD |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| **(a)** drift only | K5 replicate | K5 original | 0.913520 | 0.913039 | **+0.000481** | 0.5773 | −0.000005 | 0.000842 | 0.57 |
| **(b)** the claim | K5 replicate | K3 original | 0.913520 | 0.902535 | **+0.010986** | **< 0.0001** | −0.000010 | 0.001617 | 6.79 |
| **(c)** for the record | K5 original | K3 original | 0.913039 | 0.902535 | **+0.010505** | **< 0.0001** | −0.000005 | 0.001598 | 6.57 |
| **(d)** = (a) | K5 oracle replicate | K5 oracle original | 0.913520 | 0.913039 | +0.000481 | 0.5773 | −0.000005 | 0.000842 | 0.57 |

### Tile-MCC

| test | A | B | MCC A | MCC B | observed Δ | *p* | null mean | null SD | \|Δ\|/SD |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| **(a)** drift only | K5 replicate | K5 original | 0.753006 | 0.752861 | **+0.000145** | 0.9310 | +0.000003 | 0.001533 | 0.09 |
| **(b)** the claim | K5 replicate | K3 original | 0.753006 | 0.748998 | **+0.004008** | 0.1037 | −0.000027 | 0.002513 | 1.59 |
| **(c)** for the record | K5 original | K3 original | 0.752861 | 0.748998 | **+0.003863** | 0.0990 | −0.000029 | 0.002369 | 1.63 |
| **(d)** = (a) | K5 oracle replicate | K5 oracle original | 0.753006 | 0.752861 | +0.000145 | 0.9310 | +0.000003 | 0.001533 | 0.09 |

*p* = 0 over 10,000 permutations is reported as *p* < 0.0001, per the
campaign's convention. Test (d) is redundant by its own numbers: it is test
(a) with the same two cells under different labels (§ 4), so it is reported
for symmetry with the arm 2 note and adds nothing.

**Test (c) reproduces the campaign's own point estimates exactly.**
+0.010505 F1 and +0.003863 tile-MCC, against the +0.0105047 and +0.0038629
that follow by subtraction from
`results/gemini37-image-55map-2026-09-13/sweeps.json`
(`rungs.IMG-ARM1-K3.carried` and `rungs.IMG-ARM1-K5.carried`). The *p*-values,
*p* < 0.0001 and *p* = 0.0990, are new: no paired test of this pair had been
run before this note, so unlike arm 2's test (c) there was no published
p-value to reproduce. The pipeline is nevertheless gated the same way — every
primitive is imported from the campaign's own module, and the point estimates
it recovers are the committed ones to seven decimal places.

No Benjamini–Hochberg adjustment is applied. These four are a replication
probe of one already-declared contrast, not a new declared family; raw
*p*-values are reported, and the strongest claim below would survive a ×4
adjustment anyway.

## 6. Verdict

### 6.1 The arm 1 floor is now measured

In flip-rate units: **2.41 % of decisions flip** between independent
invocations of the arm 1 verifier at its carried operating point, 221 of
9,173, **Wilson 95 % [2.11 %, 2.74 %]**, with identical probabilities on
81.84 % and \|Δp\| > 0.5 on 2.92 %.

In metric units — the form that matters to a test — the **drift-only
contrast** is **+0.0005 micro-F1** (*p* = 0.5773, null SD 0.0008) and
**+0.0001 tile-MCC** (*p* = 0.9310, null SD 0.0015), at 0.57 and 0.09 null
standard deviations. Caveat 1's Scope paragraph can be rewritten: an arm-1
difference of order 0.001 is no longer uncharacterised.

The caveat that travels with it is the one arm 2's note also carries, and it
binds slightly harder here. Both forms rest on **one pair of legs**, and on
arm 1 they rest on **one contrast** rather than two, because this arm's F1
oracle coincides with its carried point so test (d) is test (a) again (§ 4).
Arm 2 had two drift readings at two operating points that agreed with each
other (+0.0008 and +0.0010); arm 1 has one. Treat "+0.0005 F1" as a band of
the right order, not as an estimate with an interval.

### 6.2 The arm 1 K = 3 → K = 5 micro-F1 gain is claimable; the tile-MCC gain is not

**Micro-F1: yes.** Test (c) puts the original contrast at **+0.0105,
*p* < 0.0001, 6.57 null SDs**, and test (b) — the same contrast with the K = 5
side re-verified from scratch — puts it at **+0.0110, *p* < 0.0001, 6.79 null
SDs**, nominally *larger* rather than smaller. Against a drift-only contrast
of +0.0005 at 0.57 null SDs, that is a margin of about **twenty-two times**
(21.8× for the original, 22.8× for the replicate). The declaration's rule asks
for a clear margin over the drift contrast and for the effect to survive a
fresh invocation; this clears both, and by a wider relative margin than the
arm 2 gain the rule was written around (+0.0079 against +0.0008, about ten
times).

**Tile-MCC: no — and for a different reason than on arm 2.** The contrast is
+0.0039 original (*p* = 0.0990) and +0.0040 replicated (*p* = 0.1037), which is
about twenty-seven times the +0.0001 tile-MCC drift contrast. So unlike arm 2's
tile-MCC reading — +0.0007 at *p* = 0.75, genuinely inside its band — this one
is **not** inside the drift band; it fails on its own significance, at 1.6
null standard deviations and *p* ≈ 0.10 on both legs. That distinction is
worth keeping straight, because the two failures license different
statements. Arm 2's says "the effect, if any, is the size of noise". Arm 1's
says "the effect is comfortably above drift and consistent across two
invocations, but this instrument cannot separate it from tile-level sampling
variation at the conventional level". The honest summary is a **small positive
tile-MCC difference of consistent sign and replicated size that does not reach
significance** — a direction, not a verdict, and not a claim.

It is the same shape as arm 2's finding, one notch further along: K = 5 buys
precision at the detection level, where F1 sees it, and buys little at the
tile level, where MCC is driven by whether a tile has *any* detection. That
K = 3 → K = 5 drops 152 detections (5,437 → 5,285) while moving the tile
confusion by only nine true positives and twenty-two false positives
(`tests.json`, `tile_confusion`) is the mechanism in one line.

### 6.3 How the two floors compare

Stated as the data have it, because the comparison does not reduce to one
verifier being noisier than the other:

- **At each verifier's own carried point the floors are the same size.**
  2.41 % of decisions flip on arm 1, 2.46 % on arm 2, with Wilson intervals
  that overlap almost entirely. In metric units arm 1's drift contrast is
  *smaller* — +0.0005 F1 and +0.0001 MCC against arm 2's +0.0008 F1 and
  −0.0005 MCC — but both sit well under one null SD, and with one pair of legs
  each the difference between them is not resolvable.
- **On probability agreement arm 1 is clearly the steadier**, and that holds
  after correcting for its coarser answer set: 81.8 % identical against
  63.5 %, κ 0.77 against 0.50, on a *lower* chance baseline (20.1 % against
  27.6 %).
- **On large jumps arm 1 is clearly the less steady**: \|Δp\| > 0.5 on 2.92 %
  of candidates against 2.03 %, mean \|Δp\| 0.0371 against 0.0254, maximum
  1.00 against 0.95. It repeats itself exactly more often and, when it does
  not, disagrees with itself further.
- **Arm 1's flip rate is threshold-sensitive and arm 2's is not** (2.41 / 3.62
  / 5.22 % against 2.38 / 2.20 / 2.46 % at 0.10 / 0.50 / 0.90), which is a
  property of where its answer lattice falls rather than of its judgement: at
  0.90 half its flips are one-rung 0.85 ↔ 0.95 or 0.85 ↔ 1.00 nudges (§ 3).
  **Read a flip rate only at the threshold the cell is deployed at.**

So "which verifier is more self-consistent" has no single answer, and the
sentence that survives all four readings is the one worth carrying: *the
Gemini 3 verifier at minimal thinking is more self-consistent on probabilities
and produces more large reversals, and at the operating points these cells
actually use the two seats' drift floors are indistinguishable and both of
order 0.001 in metric units.*

### 6.4 What this changes elsewhere

Three documents were re-read against the measured floor and re-worded (numbers
unchanged in all three):

- **The declaration**, `reports/image-2x2-tests-declaration-2026-09-19.md`
  § 5 caveat 1 Scope, which said arm 1 had no measured floor.
- **T2** (proposer effect under arm 1) at every rung, and the arm 1 rows of
  the 2x2 family, read against an arm 1 band rather than an arm 2 one. T2's
  margins are +0.1813 / +0.1001 / +0.0953 micro-F1 and +0.0179 / +0.0243 /
  +0.0364 tile-MCC at K = 1 / 3 / 5
  (`results/image-2x2-2026-09-19/tests_2x2_K1.json`, `…_K3.json`,
  `…_K5.json`), so the substitution changes nothing: every one of them clears
  +0.0005 F1 and +0.0001 MCC by two orders of magnitude. The value of the
  measurement here is that the clearance is now *demonstrated* on the right
  verifier rather than borrowed from the other one.
- **Both inheritance notes' H1 and H2**, whose arm 1 verdicts were hedged as
  "no floor measured".

## 7. Artefacts

| file | what it holds |
|---|---|
| `replicate_k5_arm1.py` | The instrument: the arm 2 driver parametrised by arm. Stages `agree`, `materialise`, `score`, `tests`. |
| `agreement.json` | Identical share with its chance baseline and κ, flips with Wilson intervals and flip anatomy at 0.10 / 0.50 / 0.90, \|Δp\| statistics and each leg's probability vocabulary — for this arm and, read-only, for the other. |
| `sweep_IMG-ARM1-K5-replicate.csv` | The replicate's full 95-point achievable sweep, same columns as the campaign's sweep CSVs. |
| `sweeps.json`, `cells_manifest.json` | The rung's carried row, F1 oracle and MCC oracle; the two cells and their operating points. |
| `cells/IMG-ARM1-K5-{carried,f1-oracle}-replicate/` | Detections, `evaluation.json`/`.csv`/`.md`, `score.log`. The two are the same operating point (§ 4). |
| `tests.json` | Tests (a)–(d) on both metrics, per-cell tile confusions, and the `degenerate_contrasts` record that (d) is (a). |

## Changelog

### 2026-09-20 — Original publication

First publication. The arm 1 K = 5 verifier leg was re-run on the Batch API
over the same 9,173-candidate union (data commit `5778b5569`, audited
US$6.4909) to measure the E89 drift floor for the arm 1 verifier
(`gemini-3-flash-preview`, `minimal`, T = 0), which
`reports/image-2x2-tests-declaration-2026-09-19.md` § 5 caveat 1 recorded as
unmeasured, and to test the arm 1 K = 3 → K = 5 gain against it under the
declaration's replicate rule. It mirrors the arm 2 replicate of the same date
(`../replicate-k5-arm2-batch-2026-09-20/`) in layout, method and instrument.

State at publication: the replicate was materialised at the carried point
(0.10, k5) and at its own F1 oracle, which fell at (0.10, k5) — the carried
point itself, as on the original leg — from a 95-point achievable sweep; both
cells were scored on the r2 board's own engine recipe; four paired tile-swap
permutation tests were run at 10,000 permutations, seed 42, of which test (d)
proved to be test (a) again because the oracle and carried cells coincide.

Verdict: the arm 1 floor is **2.41 % of decisions** at the carried point
(Wilson 95 % [2.11 %, 2.74 %]) and **+0.0005 micro-F1 / +0.0001 tile-MCC** as a
drift-only contrast; the K = 3 → K = 5 micro-F1 gain **is** claimable
(+0.0110 replicated, +0.0105 original, both *p* < 0.0001, about twenty-two
times drift); the tile-MCC gain is **not**, failing at *p* ≈ 0.10 on its own
significance rather than by sitting inside the drift band. No board was
re-tiered, no signed row touched, and no campaign cell or manifest was
modified — the replicate's artefacts live entirely in this directory.

Commits: `82020b941` (cells and agreement), `d1134a707` (scores and tests),
`321dd4549` (flip anatomy), `c2e5bc8a7` (this note).
