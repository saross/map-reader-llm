# W2.7: testing configurations, not outputs — options for the PI

> **Last revised**: 2026-10-05 (original publication, Session 161). See
> [§ Changelog](#changelog) for revision history.

**Status: OPEN, for the PI's decision.** Tracker
`planning/text-track-transmission-2026-10-05.md`, W2.7 (surprise S-10).
Nothing here changes a result yet.

## 1. The problem

The paired tile-swap permutation test (D42's test for every contrast) asks
whether two OUTPUTS differ by more than tile-level noise. It treats each
output as fixed. A claim that one CONFIGURATION beats another also needs the
difference to exceed what two runs of the same configuration would show.
The test cannot see that variance, so on its own it cannot license a
configuration-level claim.

## 2. How big the gap is (measured, no new runs)

From W2's replicate calibration (`reports/retest-bootstrap-check-2026-10-05-scripts/calibration_pairs.csv`:
10,125 pairs of passes of one configuration within one execution, plus the
two cross-execution groups of S-9):

| Corpus | Tiles | Replicate pairs | Median \|ΔF1\| | 95th percentile | Maximum | Tile-swap test rejects at 0.05 |
|---|---:|---:|---:|---:|---:|---:|
| Era-1 | 340 | 8,242 | 0.012 | 0.034 | 0.079 | 1.6 % |
| 384 px gold standard | 487 | 1,565 | 0.010 | 0.030 | 0.052 | 3.5 % |
| H10 pool | 327 | 45 | 0.009 | 0.029 | 0.038 | 0 % |
| 55-map, 20 m | 8,541 | 90 | 0.003 | 0.009 | 0.014 | **11 %** |
| 55-map, 50 m | 8,541 | 90 | 0.005 | 0.012 | 0.015 | **20 %** |
| Across executions (S-9 group 4 / group 5) | 487 | 78 / 15 | 0.013 / 0.054 | — | — | 22 % / 60 % |

Reading:

- On the small corpora the test behaves as a configuration test should
  (under 5 % false rejections between replicates). The replicate spread is
  wide there (95th percentile about 0.03 F1), so small differences between
  single runs mean little.
- On the 55-map corpus, the paper's main board, the test is powerful enough
  to call run-to-run noise significant: 11-20 % of same-configuration pairs
  reject. A significant tile-swap p between two 55-map cells is therefore
  not, by itself, evidence that the configurations differ.
- Across executions (different dates or code; S-9) the gap can exceed every
  within-execution floor: 0.054 median in group 5.
- One concrete case: B-17's two runs of the same minimal verifier differ by
  0.007 F1 at one threshold, against the 0.018 minimal-vs-medium difference
  that E69 and ruling 1a read as a configuration effect.

These are single-pass replicates. Consensus cells (K passes merged) should
vary less from run to run; how much less is not yet measured for the 55-map
board.

## 3. Options

1. **Replicate floor (the D4/D8 drift-floor pattern).** A configuration claim
   needs the permutation test to reject AND the difference to exceed the
   run-to-run floor for that corpus and aggregation (for example the 95th
   percentile of |ΔF1| between replicates). Cheap: uses existing replicates.
   Weakness: a floor is a threshold, not a test, and it needs a replicate
   set matching each cell's aggregation (single pass, consensus at K).
2. **A two-level test.** Put run-to-run variance into the null: permute or
   resample whole runs within each arm as well as tiles (for example a
   run-label permutation where each arm has several runs, or a
   random-effects model of per-tile counts with a run effect). Principled.
   Weakness: needs several independent runs per arm; with three runs a side
   a run-label permutation has 20 arrangements, so p cannot go below 0.05.
3. **Reword, do not re-test.** Keep the tile-swap p and say what it tests
   ("these outputs differ"), and make configuration claims only where
   replicates exist and agree. Cheapest; moves the work to the text.

## 4. Recommendation

Option 1 now, with option 3's wording everywhere; option 2 only for the few
claims the paper's argument rests on and where replicate runs exist or are
worth buying (W5, API gate). Concretely:

1. Measure the floors the boards need: single-pass floors are in § 2; the
   consensus floors can be measured without API calls where a cell has more
   passes than it uses (disjoint pass subsets give independent consensus
   replicates; the calibration file already marks `disjoint` pairs).
2. Inventory the paper's configuration-level claims and, for each, whether
   it compares single runs, whether the two arms come from different
   executions (dates, code), and whether its difference clears the floor.
   The 55-map board is the priority: its cells come from runs months apart
   (the text and image runs of April, the uplift of June, the stride and
   3.7 runs of late August; first proposer metas checked), so its
   cross-execution comparisons carry an unmeasured component (S-9).
3. Reword or qualify the claims that fail; flag to the PI any that the paper
   leans on.

## 5. Decisions for the PI

1. Which option (or combination) governs configuration-level claims?
2. The floor statistic: the 95th percentile of replicate |ΔF1| (recommended),
   or another?
3. Whether to buy replicate runs for claims that cannot be settled from
   existing data (W5, each with its own API approval).

## Changelog

### 2026-10-05 — Original publication (Session 161)

Written for tracker item W2.7 from W2's replicate calibration; no new runs.
