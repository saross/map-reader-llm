# W2.7: testing configurations, not outputs — options for the PI

> **Last revised**: 2026-10-06 (later: status RULED, D45-D47; earlier the
> same day the cross-execution row corrected: it had pooled
> within-execution pairs). See [§ Changelog](#changelog) for revision
> history.

**Status: RULED 2026-10-06 (D45 option 1 with option 3's wording, D46 the
95th percentile, D47 replicate runs claim by claim); the floors are measured
in `reports/w27-replicate-floors-2026-10-06.md`.** Tracker
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
| Across executions (S-9 group 4 / group 5; cross pairs only) | 487 | 30 / 9 | 0.037 / 0.061 | — | 0.047 / 0.072 | 57 % / 100 % |

Reading:

- On the small corpora the test behaves as a configuration test should
  (under 5 % false rejections between replicates). The replicate spread is
  wide there (95th percentile about 0.03 F1), so small differences between
  single runs mean little.
- On the 55-map corpus, the paper's main board, the test is powerful enough
  to call run-to-run noise significant: 11-20 % of same-configuration pairs
  reject. A significant tile-swap p between two 55-map cells is therefore
  not, by itself, evidence that the configurations differ.
- Across executions (different dates; S-9) the gap exceeds every
  within-execution floor: a median of 0.037 F1 in group 4 and 0.061 in
  group 5, where the same groups' within-execution pairs differ by a median
  of about 0.006. W7.5 found the two executions sent byte-identical requests
  (`reports/w75-cross-date-drift-2026-10-05.md`).
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

### 2026-10-06 (later) — Ruled and measured (Session 162)

Status line updated for D45-D47; the measured floors and the claims screen
are in `reports/w27-replicate-floors-2026-10-06.md`. The § 2 table and the
recommendation are unchanged.

### 2026-10-06 — The cross-execution row corrected

The § 2 row for S-9's groups 4 and 5 pooled all their pairs, including the
within-execution ones, and so understated the gap. Cross-execution pairs only:

| | Before | After |
|---|---|---|
| Pairs (group 4 / 5) | 78 / 15 | 30 / 9 |
| Median \|ΔF1\| | 0.013 / 0.054 | 0.037 / 0.061 |
| Tile-swap test rejects | 22 % / 60 % | 57 % / 100 % (39 pairs, 67 %, as W2 reported) |

The recommendation is unchanged; the case for cross-date caveats is stronger.

### 2026-10-05 — Original publication (Session 161)

Written for tracker item W2.7 from W2's replicate calibration; no new runs.
