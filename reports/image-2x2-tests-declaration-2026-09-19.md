# The image proposer x verifier 2x2 at deployment scale: test declaration

> **Last revised**: 2026-09-20 (PI ruling: the E89 floor of § 5 caveat 1
> revised against the full-scale replicate, in both flip-rate and metric
> units). Prior: 2026-09-20 (T5m added as § 3a; the BH family at K = 1 and
> K = 5 is T1–T4). See [§ Changelog](#changelog) for revision history.

**Declared**: 2026-09-19, 06:40 UTC, by the PI (Shawn Ross) with Claude
Code, session S155. **State of the data at declaration**: the 3.7 row
(`gemini37-image-55map-2026-09-13`) is scored at K = 1, 3, 5 on both arms;
the Gemini 3 row (`gemini3-image-55map-2026-09-16`) is scored at K = 1 on
both arms (`ba19eebd1`), its arm 1 K = 3 and K = 5 legs are verified but
unscored, and its **arm 2 K = 3 leg is in flight** (ten batch jobs, three
returned) and K = 5 not yet lodged. The primary rung's Gemini 3 arm 2 cell
therefore does not exist at declaration.

## 1. What the 2x2 is

Two proposer pools (rows) x two verifier arms (columns), all on the 55-map
corpus, the `g384_ov192` tiling (24,561 tiles), the `detect_brief-text-image`
configuration, and the stride-builder first-N unions:

| | arm 1: `gemini-3-flash-preview`, `minimal`, T 0.0 | arm 2: `gemini-3.7-flash`, `low`, T 0.0 |
|---|---|---|
| **row A**: 3.7 image pool (`gemini-3.7-flash`, `low`, T 0.7) | `IMG-ARM1-K{K}-carried` | `IMG-ARM2-K{K}-carried` |
| **row B**: Gemini 3 image pool (`gemini-3-flash-preview`, `minimal`, T 0.7) | `G3IMG-ARM1-K{K}-carried` | `G3IMG-ARM2-K{K}-carried` |

Every cell is materialised at its row's GS-carried operating point (row A:
`planning/gemini37-image-55map-2026-09-13.md` § 2 and the registered GS K = 5
cells; row B: `results/gemini3-image-55map-2026-09-16/gs-calibration/`), and
scored on the r2 board's instrument: micro-F1 at 50 m and tile-MCC
on the 8,541-tile evaluation frame, `inputs/vectors/references/best-available-gt-55maps-r2.geojson`
(`scripts/gemini37_image_55map_r2.py`, `--campaign g37|g3`).

## 2. The primary rung and the two exploratory rungs

**K = 3 is the primary rung.** It is the 3.7 campaign's declared primary
(card § 4) and the rung whose row B arm 2 cell is unbuilt at declaration.

**K = 1 and K = 5 are exploratory replicates** of the same family. K = 1's
row B cells are already scored (`ba19eebd1`), so any K = 1 result is post
hoc whatever the family says; K = 5 is not preregistered on either row (the
3.7 card stops its ladder at K = 3; the K = 5 rung was added on 2026-09-16/17
for this 2x2). They are reported beside K = 3 as a coherent
three-rung reading, never as confirmatory results.

**The K = 3 → K = 5 contrast within the 3.7 row is exploratory** (PI ruling
2026-09-19): the K = 5 rung was added after the K = 3 results were known.

## 3. The family, per metric

Five tests at the primary rung, run separately on tile-MCC and on micro-F1
at 50 m, with Benjamini–Hochberg at q = 0.05 across the five within each
metric. All cells at the same K; `_c` is the carried cell.

| # | Name | Contrast | Question |
|---|---|---|---|
| T1 | proposer effect under arm 2 | `IMG-ARM2-K_c` vs `G3IMG-ARM2-K_c` | does the proposer family matter with the 3.7 verifier? |
| T2 | proposer effect under arm 1 | `IMG-ARM1-K_c` vs `G3IMG-ARM1-K_c` | does it matter with the Gemini 3 verifier? |
| T3 | verifier seat within row B | `G3IMG-ARM2-K_c` vs `G3IMG-ARM1-K_c` | does the 3.7 verifier help a Gemini 3 pool? (row A's is tested already: +0.0158 MCC at K = 3, `findings.md` § 4 — an order of magnitude above the drift band of § 5 caveat 1) |
| T4 | interaction | (A2 − A1) − (B2 − B1) | does the verifier's gain depend on the proposer family? |
| T5 | confound check | `G3IMG-ARM1-K3_c` vs `IM-k3` | with the five confounds removed (library, tiling, thinking, passes, tile convention), is the earlier Gemini 3 image cell reproduced? |

T5 is meaningful only at K = 3 (IM-k3 is a three-vote cell); at K = 1 and
K = 5 it is reported for completeness and labelled as such.

**The family is the rung's** (PI ruling 2026-09-20, on audit finding M1).
At K = 3 the correction runs over all five tests, `m = 5`. At K = 1 and
K = 5 it runs over **T1–T4 only, `m = 4`**: a contrast the declaration calls
meaningless at a rung is not a member of that rung's family, so it must
neither enlarge `m` — which would correct the four real tests against a
family they are not in — nor carry a verdict of its own. The T5 row is still
written at those rungs, with its raw observed difference and p-value, a note
recording that it is outside the family, and no `bh_adjusted_p` and no
`significant`.

## 3a. T5m — protocol-matched confound check (additional, 2026-09-20)

**The contrast.** `G3IMG-ARM1-K5-votes3-carried` — the September Gemini 3
image pool at K = 5, read at `min_votes` 3 and at IM-k3's own probability
threshold of 0.15, under the same arm-1 verifier — against `IM-k3`. Reported
beside it, the same pool's best micro-F1 row at three votes,
`G3IMG-ARM1-K5-votes3-f1-oracle` at (0.20, k3), so the carried-versus-oracle
tax on the September side is visible rather than implied. Both cells are
materialised and scored on this board's own instrument by
`scripts/t5m_matched_comparator.py`, which imports every primitive from
`scripts/gemini37_image_55map_r2.py` and modifies nothing in it; results in
`results/image-2x2-2026-09-19/tests_t5m_K3.json`.

**Why it exists.** T5 compares a **3-of-3 unanimous cell on a three-pass
pool** (n 5,538) with a **3-of-5 majority cell on a five-pass pool**
(n 4,680). Matching the absolute vote count across pools of different depth
does not remove the passes confound § 3 lists; it converts it into a
vote-*fraction* confound of 1.0 against 0.6, and the sign of the comparison
depends on which axis the matching holds fixed
(`results/im-june-pool-grid-2026-09-20/findings.md` § 6, which also shows the
matched comparator is already swept and costs nothing to materialise). T5m is
that matched comparison.

**Status.** T5m is **additional and post-hoc**. It was specified on
2026-09-20, after the K = 3 results were known and after the June grid was
read. T5 stands exactly as declared — `tests_2x2_K3.json` is untouched, its
Benjamini–Hochberg family is unchanged at `m = 5`, and its verdicts stand —
and T5m enters no family: it is one contrast plus its own oracle twin,
reported with raw p-values, which the JSON records under `multiplicity`. Like
T5, T5m is meaningful only at K = 3, IM-k3 being a three-vote cell, and is run
there only.

**Result.** Paired tile-swap permutation, 10,000 permutations, seed 42, over
all 8,541 tiles, on the instruments of § 4. The third row is the declared T5
re-run through this path as a pipeline gate; it reproduces
`tests_2x2_K3.json` exactly, so the matched rows can be read against it
without a mechanism caveat. IM-k3 is read on its own committed file and so on
its own tile convention, as in T5 (§ 5 caveat 5).

| contrast | *n* (a vs b) | micro-F1 a vs b | Δ F1 | *p* | tile-MCC a vs b | Δ MCC | *p* |
|---|---:|---:|---:|---:|---:|---:|---:|
| **T5m** `…K5-votes3-carried` (0.15, k3) vs `IM-k3` | 7,222 vs 4,680 | 0.7312 vs 0.8008 | **−0.0696** | **< 0.0001** | 0.7235 vs 0.7110 | +0.0125 | 0.0887 |
| **T5m oracle** `…K5-votes3-f1-oracle` (0.20, k3) vs `IM-k3` | 6,974 vs 4,680 | 0.7357 vs 0.8008 | **−0.0651** | **< 0.0001** | 0.7347 vs 0.7110 | +0.0237 | 0.0009 |
| T5 as declared `G3IMG-ARM1-K3-carried` vs `IM-k3` | 5,538 vs 4,680 | 0.8024 vs 0.8008 | +0.0016 | 0.7604 | 0.7247 vs 0.7110 | +0.0137 | 0.0578 |

**The reading.** On **micro-F1 the declared near-tie is a property of the
matching, not a reproduction**. Matched on pool depth, the September cell is
0.0696 *behind* IM-k3 — more than forty times T5's own 0.0016, about thirteen
null standard deviations, and far above the drift floor of § 5 caveat 1 — and
it is still 0.0651 behind when the September side is given its own three-vote
F1 oracle. T5's micro-F1 null must therefore not be read as "the earlier
Gemini 3 image cell is reproduced"; what it says is that one particular
matching makes the two agree.

On **tile-MCC the reading survives the match.** All three contrasts put the
September cell above IM-k3, by +0.0125 to +0.0237, so the direction and the
rough size are stable across the matchings; the raw p-values run 0.0887
(matched carried), 0.0578 (declared) and 0.0009 (matched oracle), none of them
corrected here. The honest summary is a small positive tile-MCC difference of
consistent sign rather than a single verdict — which is what the June note
predicts from tile-MCC's flatness across this whole region.

Nothing in T5m re-runs T5, re-tiers a board or touches a signed row.

## 4. The instruments

**T1, T2, T3, T5**: the paired tile-swap permutation test already used by the
board and the 3.7 campaign — `n1_baseline_leaderboard_tiering.permutation_test_float`
for micro-F1 on per-tile TP/FP/FN and `mcc_tiering_55map.permutation_test_mcc`
for tile-MCC on per-tile predictions against a fixed truth vector — 10,000
permutations, `numpy.random.default_rng(42)`, probability-0.5 per-tile label
swap, two-sided p = mean(|null| ≥ |observed|).

**T4**: the same machinery lifted to four cells. Per tile *i* the four cells
contribute (A1, A2, B1, B2) — per-tile TP/FP/FN for micro-F1, per-tile
predictions for MCC. The statistic is

    D = [S(A2) − S(A1)] − [S(B2) − S(B1)]

with S the corpus-level statistic (micro-F1 from summed counts, or MCC from
the tile confusion). Under the null of no interaction the arm effect is the
same in both rows, so a tile's row-A pair and row-B pair are exchangeable:
each permutation draws a probability-0.5 mask over tiles and, for masked
tiles, swaps the (A1, A2) pair with the (B1, B2) pair; D is recomputed;
p = mean(|D_null| ≥ |D_obs|), two-sided, 10,000 permutations, seed 42. This
is the tile-swap test applied to the per-tile arm difference, and reduces to
T3-versus-row-A's-T3 for micro-F1's additive counts.

Implementation: `scripts/gemini37_image_55map_r2.py --stage tests-2x2 --rungs K`,
output `results/image-2x2-2026-09-19/tests_2x2_K{K}.json`, one file per rung.

## 5. Caveats declared with the family

1. **The E89 floor.** Independent re-invocations of the arm 2 verifier
   (`gemini-3.7-flash`, low thinking, T = 0) over the same 9,173-candidate
   K = 5 union agree on only **63.5 %** of probabilities (5,826 of 9,173) and
   **flip 2.46 % of decisions** at the 0.90 operating point — 226 of 9,173,
   **Wilson 95 % interval [2.17 %, 2.80 %]** — with |Δp| > 0.5 on 2.03 %
   (186 of 9,173). Measured at full scale by the batch replicate of
   2026-09-20:
   `results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20/`
   (`agreement.json`; `findings.md` § 3). The interval is the Wilson score
   interval for a binomial proportion — `(p̂ + z²/2n ± z·sqrt(p̂(1 − p̂)/n +
   z²/4n²)) / (1 + z²/n)` with `z` = 1.96 — rather than the normal
   approximation, which is unreliable at a proportion this small. These
   figures supersede the 2026-09-19 171-twin probe's (see the changelog).

   **The floor in metric units.** A flip rate is not what a test sees. What a
   test sees is the **drift-only contrast**: the same union at the same
   operating point, scored twice from two invocations of the same verifier.
   That contrast is **+0.0008 micro-F1** (*p* = 0.4015, null SD 0.0009) at
   the carried point and **+0.0010** (*p* = 0.2861) at each leg's own F1
   oracle, and **−0.0005 tile-MCC** (*p* = 0.8225, null SD 0.0016) at the
   carried point and **−0.0007** (*p* = 0.7100) at the oracles
   (`tests.json` beside the note above). So re-invocation moves a third of
   the individual probabilities, the selected operating point not at all, and
   the corpus metric by **of order 0.001 F1 and ±0.001 tile-MCC**.

   **One degree of freedom.** Both forms come from **one pair of legs**. The
   two drift contrasts agree with each other, and the flip rate agrees with
   the independent 2026-09-19 probe to within a factor of two, so the band is
   consistently characterised — but a claim about drift's *own* size rests on
   two contrasts from a single replicate, not on a distribution of
   re-invocations. Treat the metric-unit figures as a band of the right order,
   not as an estimate with an interval.

   **The rule.** A tile-swap permutation tests sampling variation over tiles,
   not verifier nondeterminism, so a difference of drift's own size can be
   "significant" and still be drift. **An effect is not claimable without a
   replicate arm unless it exceeds the drift-only contrast by a clear
   margin**; a null result remains uninformative about small effects. The
   worked example is the arm 2 K = 3 → K = 5 micro-F1 gain: **+0.0079 against
   drift's +0.0008**, about ten times the drift contrast and about 5.4 null
   standard deviations where both drift contrasts sit under 1.1 — claimable,
   and in that case replicated outright. Its tile-MCC counterpart, +0.0007 at
   *p* = 0.75, is inside the drift band and is not claimed.

   **Applied to this family at K = 3.** The margins are wide enough that the
   rule bites on one row only. T1 and T2 (≈ 0.10 F1, 0.024–0.041 MCC), T3's
   micro-F1 (+0.0103) and T4 on both metrics (+0.0071 F1, +0.0170 MCC) all
   clear the band by roughly an order of magnitude or more. **T3's tile-MCC
   reading, −0.0013 at *p* = 0.7954, sits inside the drift band**: its null
   is uninformative and no "the verifier seat does not matter on tile-MCC"
   claim follows from it. T5 and T5m are covered in the same way — T5's
   +0.0016 F1 is the size of drift, while T5m's −0.0696 is not (§ 3a).

   **Scope.** The floor is measured on `gemini-3.7-flash` at low thinking and
   T = 0 — the arm 2 verifier. The arm 1 verifier
   (`gemini-3-flash-preview`, `minimal`, T = 0) has **no measured floor**:
   E89's qualitative finding that these verifiers are nondeterministic at
   T = 0 covers it, but no replicate of an arm 1 leg exists, so an arm-1
   difference of order 0.001 is uncharacterised rather than known to be
   drift.
2. **Route.** Row A's arm 2 ran on realtime flex; row B's arm 2 runs on the
   Batch API (PI ruling 2026-09-18). The 2026-09-19 batch-versus-flex probe
   (`outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img/probe-batch-vs-flex-2026-09-19/`)
   found the route's effect indistinguishable from same-route re-invocation
   drift, so the route is not treated as a factor; it is recorded per cell.
   The replicate of caveat 1 is itself a cross-route pair — batch against
   flex — so the band it measures is drift and route together, which makes
   it if anything an over-estimate of same-route drift.
3. **Operating points differ by row by design.** Each row is at its own
   GS-carried point, so T1 and T2 compare rows as deployed, not at a common
   threshold. The sweep oracles are reported beside the carried cells to
   show what a common-threshold reading would change.
4. **Row B at K = 1 over-generates** (F1 0.66 against row A's 0.87, tile-MCC
   0.71 against 0.76; `planning/observation-drafts-2026-09-19.md` Obs 485
   draft). The primary rung is K = 3 precisely because unanimity is the
   image pool's precision filter; the K = 1 replicate is expected to show
   the largest proposer effect and the K = 5 replicate the smallest.
5. **IM-k3's tile join** is not this chain's (83.65 % idempotent; `findings.md`
   § 7), so T5 inherits the caveat already recorded for the 3.7 campaign's
   IM-k3 comparison.
6. **Nothing here re-tiers a board or touches a signed row.** The 2x2's
   registration and signature are the PI's, after the tests are run.

## Changelog

### 2026-09-20 — The E89 floor revised against the full-scale replicate

**Trigger**:
`results/gemini37-image-55map-2026-09-13/replicate-k5-arm2-batch-2026-09-20/`
— a second, independent invocation of the **arm 2** verifier over the same
9,173-candidate K = 5 union, at the same model, instruction file, system
instruction hash, temperature and thinking level, approved by the PI on
2026-09-20 and run on the Batch API. It measures at full scale what § 5
caveat 1 had been estimating from a 171-twin probe, and the two disagree by
about a factor of two on the flip rate.

**Before → after**, on the batch-versus-flex comparison the two share:

| figure | superseded: 2026-09-19 probe, 171 twins | revised: replicate, 9,173 candidates |
|---|---|---|
| identical probabilities | 60 % (61 % on the same-route twin) | **63.5 %** (5,826 / 9,173) |
| decision flips at 0.90 | 5.3 %; 3.5 % same-route twin — quoted here as "3.5–5.3 %" | **2.46 %** (226 / 9,173), Wilson 95 % **[2.17 %, 2.80 %]** |
| \|Δp\| > 0.5 | 6 / 171 = 3.5 % | **2.03 %** (186 / 9,173) |
| the floor in **metric units** | not stated | **+0.0008 micro-F1** (*p* = 0.4015, null SD 0.0009) and **−0.0005 tile-MCC** (*p* = 0.8225, null SD 0.0016), drift-only at the carried point; +0.0010 / −0.0007 at the oracles |

Probe figures re-read from its own
`outputs/gemini37-image-55map-2026-09-13/verifier/g384_ov192_55map_g37img/probe-batch-vs-flex-2026-09-19/README.md`;
replicate figures from `agreement.json` and `tests.json` beside the note
above. The old "~40 % of probabilities differ" reads as 36.5 % at full scale
— the probe was not a small-sample fluke on that statistic; the flip rate was.

**What the revision changes.** The caveat now gives the floor in **both
forms** — the decision-flip rate with an interval, and the drift-only
*contrast in metric units*, which is what a paired test actually sees — and
states the rule as a **margin over the drift-only contrast** rather than as a
threshold on the flip rate. It records that both forms rest on **one pair of
legs**, so a claim about drift's own size has one degree of freedom, and it
records the **scope**: the floor is measured on `gemini-3.7-flash` at low
thinking and T = 0, and the arm 1 verifier (`gemini-3-flash-preview`,
`minimal`, T = 0) has no measured floor. The worked example of a claimable
effect is the arm 2 K = 3 → K = 5 micro-F1 gain, +0.0079 against drift's
+0.0008.

**What does not change.** No test's numbers, no verdict, no family, no
instrument, no rung. The revision is *downwards* on the flip rate, so nothing
that was withheld under the old floor becomes less claimable by it, and
nothing previously reported is created or destroyed. The replicate's own
verdict — that the K = 3 → K = 5 micro-F1 gain is claimable and its tile-MCC
counterpart is not — was reached under the old wording and is unaffected.

**Consequences written into the body.** With the floor in metric units the
rule can be applied row by row, so caveat 1 now records that T1, T2, T3's
micro-F1 (+0.0103) and T4 on both metrics (+0.0071 F1, +0.0170 MCC) clear the
band by roughly an order of magnitude or more, while **T3's tile-MCC reading,
−0.0013 at *p* = 0.7954, sits inside it** and supports no claim either way.
§ 3's T3 row and § 5 caveat 2 are re-worded to match — caveat 2 also now
names the probe it had been citing as "the probe above", and records that the
replicate pair is itself batch-against-flex, so its band covers route and
drift together. **No number in § 3 or § 5 moved.**

Commit: `73a4f09df`.

### 2026-09-20 — T5m: a protocol-matched confound check, added beside T5

**Trigger**: `results/im-june-pool-grid-2026-09-20/findings.md` § 6. That note
swept the June image pool on the r2 reference and found T5's pair matched on
the *absolute* vote count across pools of different depth — 3-of-3 on three
passes (n 5,538) against 3-of-5 on five passes (n 4,680) — so the passes
confound § 3 says T5 removes is not removed but converted into a
vote-*fraction* confound of 1.0 against 0.6, and the sign of the comparison
depends on which axis the matching holds fixed. Escalated to the PI and ruled
on the same day.

**The ruling**: keep T5 exactly as declared — it is committed in three citable
JSONs and in this changelog — and **add** a matched test, T5m, at the K = 3
rung only, IM-k3 being a three-vote cell. New § 3a states it. Instrument:
`scripts/t5m_matched_comparator.py` (`d985a5e51`), which imports every
primitive from `scripts/gemini37_image_55map_r2.py` and modifies nothing in
it; cells materialised in `2bd86154e`, scored and tested in `c9abda52e`.

**What does not change**: `results/image-2x2-2026-09-19/tests_2x2_K3.json` is
untouched. The family is still the five tests, the Benjamini–Hochberg
correction still runs over `m = 5` at the primary rung, and T5's own verdicts
stand — micro-F1 +0.0016 at *p* = 0.7604 (BH 0.7604, ns) and tile-MCC +0.0137
at *p* = 0.0578 (BH 0.07225, ns). T5m enters no family and carries no adjusted
p-value. The instruments, the other caveats, which rung is primary, and every
other test are as they were. The declared T5 pair re-run through the new
script reproduces its committed row exactly — the script refuses to write
without that gate — so the added rows are on the same pipeline.

**What T5m adds**, at K = 3 against `IM-k3` (paired tile-swap, 10,000
permutations, seed 42, 8,541 tiles):

| contrast | Δ micro-F1 | *p* | Δ tile-MCC | *p* |
|---|---:|---:|---:|---:|
| T5 as declared — 3-of-3 on three passes | +0.0016 | 0.7604 | +0.0137 | 0.0578 |
| T5m matched — 3-of-5 on five passes, (0.15, k3) | **−0.0696** | **< 0.0001** | +0.0125 | 0.0887 |
| T5m matched at its own three-vote F1 oracle, (0.20, k3) | **−0.0651** | **< 0.0001** | +0.0237 | 0.0009 |

The micro-F1 half of T5's null does not survive the match, and § 3a says so in
the body: the agreement is a property of the matching, not a reproduction. The
tile-MCC half does survive, with the sign and rough size stable across all
three matchings.

**Artefacts**: `results/image-2x2-2026-09-19/tests_t5m_K3.json`; cells
`results/gemini3-image-55map-2026-09-16/cells/G3IMG-ARM1-K5-votes3-carried/`
and `…/G3IMG-ARM1-K5-votes3-f1-oracle/`, both recorded in that campaign's
`cells_manifest.json` with a `basis` naming them post-hoc T5m comparators.
**Tests**: `tests/test_t5m_matched_comparator.py` pins the matched cell to
IM-k3's own threshold, the oracle twin to the three-vote rows only, and the
declared-T5 reproduction gate to exact rather than tolerant equality.
Commit: `3783e0e03`.

### 2026-09-20 — Erratum: the metric is plain micro-F1, not "corrected"

Trigger: `reports/comparability-inventory-37-runs-2026-09-20.md` § 5 item 5.
§ 2 called the r2 board's instrument "corrected micro-F1 at 50 m"; the r2
chain scores with `scripts/evaluate_detections.py` (plain micro-F1, per-map
Hungarian matching) and never invokes the canonical Track-2 corrected-F1
engine. Wording corrected in place here and in the r2 script's module
docstring; no number changes.

### 2026-09-20 — The BH family is the rung's: T1–T4 at K = 1 and K = 5

**Trigger**: audit finding M1 in
`reports/code-audit-2026-09-20-storage-preflight.md` § 3.2, escalated to the
PI as § 6 item 2 and ruled on the same day: *implement it*. The audit found
that `stage_tests_2x2` computed T5 at every rung, marked it
`meaningful: k == 3`, and then passed all five rows to the
Benjamini–Hochberg correction anyway — verified at source, not inferred, on
the committed K = 5 file, where the MCC T3 row's `bh_adjusted_p` of 0.104833
is exactly `0.0629 × 5/3`.

**The ruling**, now implemented in `scripts/gemini37_image_55map_r2.py`
(`apply_bh_to_family`): at a rung where T5 is not meaningful the correction
runs over T1–T4 (`m = 4`), and the T5 row is written with its raw
`observed_diff` and `p_value`, a `note` recording that it sits outside the
family at that rung, `significant: null`, and **no** `bh_adjusted_p`. The
operator-facing log line marks the row rather than printing a bare verdict
beside the members (audit finding m4, the half of it that M1 settles).

**What moves, per metric, at K = 1 and K = 5**: every member's adjusted
p-value falls by a factor of 4/5 before the monotonicity step — e.g. the
K = 5 MCC T3 row from `0.0629 × 5/3 = 0.104833` to `0.0629 × 4/3 =
0.083867`. The old direction was **conservative**, so nothing previously
reported as significant is at risk and no reported finding is created or
destroyed by this change.

**What does not change**: K = 3, the primary rung, where T5 is meaningful
and the family is all five — the correction, the verdicts, and the JSON
shape are bit-for-bit what they were, and `tests_2x2_K3.json` stands as
committed. Nothing here touches the family's composition, the instruments,
the caveats, or which rung is primary.

**Artefacts**: `results/image-2x2-2026-09-19/tests_2x2_K1.json` and
`tests_2x2_K5.json` are regenerated by the PI's session — the session that
landed this change was scoped out of `results/`. Until they are
regenerated, their `bh_adjusted_p` values are the `m = 5` ones described
above and their T5 rows still carry a `significant` verdict.

**Tests**: `tests/test_image_2x2_tests.py` pins the family size by
arithmetic on fake p-values (`m = 4` at K ≠ 3, `m = 5` at K = 3), the row
shape outside the family, and the bit-for-bit identity of the primary rung
against a plain correction over all five rows. Commit: `f750b96ef`.

### 2026-09-19 — Original publication

Declared with the Gemini 3 row's primary-rung arm 2 cell unbuilt (ten batch
jobs in flight, three returned at 06:27 UTC). Commit: `0e5985d83`.
