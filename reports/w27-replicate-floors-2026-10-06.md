# W2.7 / W7.6: replicate floors for configuration-level claims, measured

> **Last revised**: 2026-10-07 (§ 6b added: the 55-map floors from every
> pass subset; three § 7.2 verdicts move). See [§ Changelog](#changelog) for
> revision history.

**Status: measured; the floors are in § 3 to § 6, the inventory of the paper's
configuration-level claims against them in § 7.** Rulings D45 to D47
(`planning/pi-decisions-2026-09-20.md`): a claim that one configuration beats
another needs the paired tile-swap permutation test to reject AND the
difference to exceed the run-to-run floor for its corpus and aggregation; the
floor statistic is the 95th percentile of replicate |ΔF1|; no replicate run is
bought until the inventory shows which claims the paper leans on. Options
note: `planning/w27-configuration-level-testing-2026-10-05.md`. Tracker items
W2.7 and W7.6 (1) to (3) in `planning/text-track-transmission-2026-10-05.md`.
No Application Programming Interface (API) call was made; every number below
comes from passes the project already held. Scripts, gates and raw outputs:
`reports/w27-replicate-floors-2026-10-06-scripts/`.

## 1. What a floor is here, and which stage it covers

The tile-swap permutation test treats each output as fixed, so between two
outputs of ONE configuration it rejects at its nominal rate on the small
corpora and far above it on the 55-map corpus (W2.7 note § 2). A replicate
floor is the spread of |ΔF1| between two outputs of the same configuration,
read at the 95th percentile, below which a difference between two cells is
not evidence that their configurations differ. Three kinds are measured:

1. **Within-execution, single pass** (W2's calibration, re-read here by
   execution): two passes of one run on one date.
2. **Within-execution, consensus** (new): two consensus cells built from
   DISJOINT subsets of one run's passes at the same K and vote threshold t.
   On the gold-standard corpora the cells are proposer-only consensus (the
   voting algorithm of preregistration § 8.5). On the 55-map board the cells
   are proposer-verifier rungs built with the board's own rung mechanism
   (`stride55_ladder.cluster_first_n`: re-cluster the subset, inherit each
   candidate's verifier probability from the family's K-union verification
   within 10 m). **The inheritance holds the verifier fixed**, so these
   floors cover the PROPOSER stage only and are a lower bound on the full
   run-to-run spread. The verifier stage's own re-invocation noise is
   measured separately by the two 2026-09-20 batch replicates of the 3.7
   image campaign's K = 5 verifier legs (drift-only contrast +0.0005 and
   +0.0008 micro-F1 at the carried points, 2.4 % of decisions flipping;
   `results/gemini37-image-55map-2026-09-13/replicate-k5-arm{1,2}-batch-2026-09-20/findings.md`).
   A conservative full floor for a board claim is the proposer floor plus
   that verifier contrast (§ 6).
3. **Cross-execution** (W7.6): the same transmitted request on two dates.
   Single-pass pairs from W2's groups, split by execution; consensus pairs
   between the first K passes of one execution and the disjoint K-subsets of
   the other; and on the 55-map corpus itself the uplift family's first
   five (2026-04-18) against its last five (2026-06-11) passes, with the
   verifier fixed.

Every floor is a 95th percentile of |ΔF1| over pairs that are not
independent (subsets of one pool share no passes but share the pool's
tiles; the few 10-pass pools give one or three pairs at K = 5 and K = 3).
Read them as the right order of magnitude, with the pair count beside them.

## 2. Gates (nothing below was written until these passed)

- **The subset builder is the board's rung builder.** The first-N subset at
  each family's committed rung point reproduces the committed cell's
  detection count EXACTLY: B-N5-carried 4,736; A-N5-carried 4,597;
  ARM1-N3-carried 5,482; ARM2-N3-carried 5,187; FOURTH-N5-carried 4,431;
  FOURTH-N3-carried 4,623 (`gates.json`).
- **The fast within-pass deduplication equals the committed one** on a
  real pass (3.7 arms run_1: 17,994 raw → 8,511 deduplicated, every
  centroid, tile set and cluster size identical). The committed function
  is a pure-Python double loop (minutes per 55-map pass); the vectorised
  restatement reproduces it bit for bit once the centroid mean uses the
  built-in `sum`, which since Python 3.12 is compensated (a plain loop and
  `numpy.mean` both differ in the last bit; the gate caught both).
- **The in-memory consensus equals the committed sweeps.** For four
  pools with committed `consensus/consensus_t<t>.geojson` files, the
  feature count is reproduced at EVERY threshold (3-, 3-, 10- and 30-pass
  pools: 3 + 3 + 10 + 30 thresholds, all exact; `gs_gates.json`).
  **Incidental finding:** the 10- and 30-pass sweeps reproduce only when
  the passes are taken in LEXICOGRAPHIC run order (run_1, run_10, run_11,
  …, run_2, …), which is how the April 2026 builds iterated `run_*`
  directories; the current `merge_passes.resolve_pass_files` orders them
  numerically. Greedy star clustering is seed-order dependent, so a rebuild
  today would move counts by about 0.3 to 1 % at most thresholds (for the
  30-pass T0.7 HIGH pool, 11,771 → 11,731 at t = 1; 1,991 → 2,006 at
  t = 5). No committed result is affected; a regeneration would be, so the
  order should be pinned before any committed union is rebuilt (W6.3).

## 3. Consensus floors on the gold-standard corpora (within execution)

Proposer-only consensus cells from disjoint K-subsets of one run's passes,
at every vote threshold t, scored at 20 m with the board's own path; the
tile-swap test between every disjoint pair at the same (K, t). Pools: every
W2 replicate member with at least six passes (the 10- and 30-pass pools of
`pv-diag-384`, `retest-phase3a`, `-high`, `-replication`,
`retest-h11-single-pass-384-t0`). Pairs within a 30-pass pool: 3 at K = 10,
15 at K = 5, 45 at K = 3; within a 10-pass pool: 1 at K = 5, 3 at K = 3.

| corpus | K | t | pairs | median \|ΔF1\| | 95th pct | max | tile-swap rejects |
|---|---:|---:|---:|---:|---:|---:|---:|
| era1 | 3 | 1 | 315 | 0.0080 | 0.0234 | 0.0355 | 1% |
| era1 | 3 | 2 | 315 | 0.0094 | 0.0325 | 0.0480 | 8% |
| era1 | 3 | 3 | 315 | 0.0128 | 0.0324 | 0.0517 | 4% |
| era1 | 5 | 1 | 105 | 0.0067 | 0.0259 | 0.0391 | 4% |
| era1 | 5 | 2 | 105 | 0.0056 | 0.0200 | 0.0267 | 3% |
| era1 | 5 | 3 | 105 | 0.0064 | 0.0277 | 0.0377 | 3% |
| era1 | 5 | 4 | 105 | 0.0091 | 0.0238 | 0.0466 | 8% |
| era1 | 5 | 5 | 105 | 0.0126 | 0.0403 | 0.0674 | 6% |
| era1 | 10 | 1 | 21 | 0.0060 | 0.0235 | 0.0280 | 10% |
| era1 | 10 | 2 | 21 | 0.0047 | 0.0147 | 0.0184 | 5% |
| era1 | 10 | 3 | 21 | 0.0051 | 0.0127 | 0.0149 | 0% |
| era1 | 10 | 4 | 21 | 0.0070 | 0.0193 | 0.0207 | 0% |
| era1 | 10 | 5 | 21 | 0.0085 | 0.0216 | 0.0217 | 0% |
| era1 | 10 | 6 | 21 | 0.0078 | 0.0224 | 0.0300 | 14% |
| era1 | 10 | 7 | 21 | 0.0083 | 0.0201 | 0.0245 | 0% |
| era1 | 10 | 8 | 21 | 0.0113 | 0.0303 | 0.0468 | 10% |
| era1 | 10 | 9 | 21 | 0.0129 | 0.0381 | 0.0490 | 14% |
| era1 | 10 | 10 | 21 | 0.0134 | 0.0578 | 0.0712 | 14% |
| px384 | 3 | 1 | 102 | 0.0077 | 0.0185 | 0.0246 | 6% |
| px384 | 3 | 2 | 102 | 0.0084 | 0.0197 | 0.0285 | 2% |
| px384 | 3 | 3 | 102 | 0.0103 | 0.0465 | 0.0608 | 12% |
| px384 | 5 | 1 | 34 | 0.0064 | 0.0140 | 0.0163 | 9% |
| px384 | 5 | 2 | 34 | 0.0069 | 0.0166 | 0.0189 | 0% |
| px384 | 5 | 3 | 34 | 0.0045 | 0.0139 | 0.0179 | 0% |
| px384 | 5 | 4 | 34 | 0.0066 | 0.0211 | 0.0238 | 6% |
| px384 | 5 | 5 | 34 | 0.0122 | 0.0295 | 0.0374 | 6% |
| px384 | 10 | 1 | 6 | 0.0013 | 0.0039 | 0.0040 | 0% |
| px384 | 10 | 2 | 6 | 0.0059 | 0.0163 | 0.0172 | 33% |
| px384 | 10 | 3 | 6 | 0.0113 | 0.0138 | 0.0140 | 33% |
| px384 | 10 | 4 | 6 | 0.0030 | 0.0035 | 0.0035 | 0% |
| px384 | 10 | 5 | 6 | 0.0052 | 0.0155 | 0.0158 | 0% |
| px384 | 10 | 6 | 6 | 0.0040 | 0.0132 | 0.0135 | 0% |
| px384 | 10 | 7 | 6 | 0.0064 | 0.0136 | 0.0141 | 0% |
| px384 | 10 | 8 | 6 | 0.0048 | 0.0107 | 0.0108 | 0% |
| px384 | 10 | 9 | 6 | 0.0083 | 0.0191 | 0.0213 | 0% |
| px384 | 10 | 10 | 6 | 0.0137 | 0.0253 | 0.0288 | 17% |

Reading:

- **Consensus shrinks the floor modestly at mid thresholds and widens it at
  unanimity.** At K = 5 and t = 4 the 95th percentile of replicate |ΔF1| is
  0.024 (Era-1) and 0.021 (384-px GS), about a third below the single-pass
  floors of 0.034 and 0.030 (W2.7 note § 2); at unanimity it is wider than a
  single pass (Era-1 K = 5 t = 5 0.040, K = 10 t = 10 0.058). A unanimity
  cell keeps few detections, so one pass's disagreement moves its F1 more
  than it moves a looser cell's. The registered consensus cells sit near the
  top of the lattice (`results/run-conditions.json`, read 2026-10-06: of 60
  K = 5 consensus conditions, 34 use t = 4 and 13 use t = 5; of 28 K = 10
  conditions, 11 use t = 8 and 7 use t = 10), so the cells the paper
  compares sit where the floor is near its single-pass size or wider.
- **The tile-swap test rejects 5.0 % of the 2,216 within-execution
  consensus pairs at α = 0.05** (per (corpus, K, t) cell 0 to 33 %, median
  4 %, the 33 % on six-pair cells), against 1.6 to 3.5 % between single
  passes on the same corpora (W2.7 note § 2): the test is at its nominal
  rate on consensus replicates, so a significant tile-swap p between two
  consensus cells is still not, by itself, evidence that their
  configurations differ.
- **D46's floors for the gold-standard boards**, as the 95th percentile at
  the board's operating point: Era-1 (340 tiles) K = 5 t = 4 **0.024**, t = 5
  **0.040**; K = 10 t = 8 **0.030**, t = 9 **0.038**, t = 10 **0.058**; K = 3
  t = 2 or 3 **0.032**. 384-px GS (487 tiles) K = 5 t = 4 **0.021**, t = 5
  **0.030**; K = 10 t = 9 **0.019**, t = 10 **0.025** (six pairs only); K = 3
  t = 3 **0.047**. Single-pass floors stay as W2 measured them (0.034 and
  0.030).

## 4. The replicate atlas: within against across executions, by time gap (W7.6 items 1 and 2)

Every W2 group with two executions, with the single-pass pairs split by
execution and the consensus pairs added (first-K of one execution against
each disjoint K-subset of the other). Dates are from the pass metas
(`start_time`; read 2026-10-06). The column format is n / median |ΔF1| /
95th percentile / max / tile-swap rejections at 0.05.

| group | corpus | configuration | gap (days) | dates | buffer | single-pass within | single-pass ACROSS | consensus within | consensus ACROSS |
|---:|---|---|---:|---|---:|---|---|---|---|
| 10 | H10 327 | image HIGH T0.7 (h8-v2 / h10) | 0 | 04-15 same day | 20 m | 20 / 0.009 / 0.029 / 0.032 / 0% | 25 / 0.009 / 0.027 / 0.038 / 0% | — | 4 / 0.016 / 0.029 / 0.030 / 0% |
| 13 | Era-1 | text MIN T1.0 | 0 | 03-15 hours | 20 m | 441 / 0.012 / 0.034 / 0.049 / 2% | 189 / 0.014 / 0.045 / 0.061 / 1% | 120 / 0.014 / 0.034 / 0.038 / 9% | 42 / 0.009 / 0.028 / 0.030 / 2% |
| 17 | Era-1 | text MIN T0.3 | 0 | 03-15 hours | 20 m | 438 / 0.007 / 0.027 / 0.046 / 1% | 90 / 0.008 / 0.023 / 0.033 / 1% | 120 / 0.006 / 0.018 / 0.025 / 0% | 20 / 0.008 / 0.018 / 0.018 / 0% |
| 18 | Era-1 | text MIN T0.7 | 1 | 03-15 / 03-17 | 20 m | 873 / 0.010 / 0.027 / 0.045 / 1% | 1080 / 0.010 / 0.028 / 0.049 / 2% | 240 / 0.008 / 0.023 / 0.035 / 5% | 312 / 0.009 / 0.025 / 0.036 / 4% |
| 23 | Era-1 | image HIGH T0.7 (3c pools) | 1 | 03-21..25 | 20 m | 60 / 0.017 / 0.053 / 0.077 / 7% | 375 / 0.017 / 0.048 / 0.079 / 4% | — | 60 / 0.019 / 0.041 / 0.059 / 5% |
| 24 | Era-1 | text HIGH diversity pools | 1 | 03-18..22 | 20 m | 20 / 0.007 / 0.035 / 0.035 / 0% | 25 / 0.005 / 0.039 / 0.040 / 4% | — | 4 / 0.016 / 0.022 / 0.023 / 0% |
| 8 | 384-px GS | text MIN T0.7 | 2 | 03-22 / 03-24 | 20 m | 480 / 0.010 / 0.030 / 0.039 / 5% | 300 / 0.010 / 0.027 / 0.042 / 4% | 128 / 0.009 / 0.029 / 0.041 / 8% | 84 / 0.012 / 0.038 / 0.044 / 21% |
| 21 | Era-1 | text HIGH T0.7 | 2 | 03-16/17 / 03-18..22 | 20 m | 930 / 0.012 / 0.031 / 0.054 / 0% | 3075 / 0.012 / 0.034 / 0.055 / 1% | 240 / 0.014 / 0.039 / 0.065 / 7% | 716 / 0.014 / 0.039 / 0.066 / 8% |
| 22 | Era-1 | text HIGH T1.0 | 2 | 03-17..21 / 03-19..21 | 20 m | 445 / 0.013 / 0.047 / 0.073 / 6% | 150 / 0.012 / 0.037 / 0.072 / 5% | 120 / 0.018 / 0.042 / 0.067 / 9% | 32 / 0.015 / 0.042 / 0.065 / 6% |
| 11 | 55-map | text HIGH T0.7 | 8 | 04-10 / 04-18 | 20 m | 20 / 0.004 / 0.009 / 0.010 / 20% | 25 / 0.004 / 0.011 / 0.014 / 20% | — | 4 / 0.003 / 0.005 / 0.005 / 0% |
| 11 | 55-map | text HIGH T0.7 | 8 | 04-10 / 04-18 | 50 m | 20 / 0.004 / 0.007 / 0.008 / 5% | 25 / 0.006 / 0.013 / 0.014 / 28% | — | 4 / 0.004 / 0.008 / 0.008 / 25% |
| 1 | 384-px GS | text HIGH T0.7 | 17 | 03-24 / 04-10 | 20 m | 445 / 0.012 / 0.033 / 0.052 / 2% | 150 / 0.009 / 0.030 / 0.039 / 0% | 120 / 0.009 / 0.042 / 0.061 / 6% | 32 / 0.008 / 0.019 / 0.042 / 0% |
| 4 | 384-px GS | image MIN T0.3 | 20 | 03-27 / 04-16 | 20 m | 48 / 0.006 / 0.018 / 0.022 / 0% | 30 / 0.037 / 0.045 / 0.047 / 57% | 8 / 0.007 / 0.013 / 0.013 / 0% | 6 / 0.034 / 0.041 / 0.043 / 67% |
| 5 | 384-px GS | image HIGH T0.0 | 20 | 03-27 / 04-16 | 20 m | 6 / 0.007 / 0.010 / 0.010 / 0% | 9 / 0.061 / 0.071 / 0.072 / 100% | — | 2 / 0.070 / 0.072 / 0.073 / 100% |
| 2 | 384-px GS | text MIN T0.3 | 21 | 03-27 / 04-17 | 20 m | 48 / 0.008 / 0.021 / 0.023 / 0% | 30 / 0.010 / 0.019 / 0.019 / 0% | 8 / 0.004 / 0.012 / 0.013 / 0% | 6 / 0.007 / 0.021 / 0.024 / 0% |
| 6 | 384-px GS | text HIGH T0.0 | 21 | 03-27 / 04-17 | 20 m | 6 / 0.009 / 0.013 / 0.014 / 0% | 9 / 0.006 / 0.017 / 0.019 / 0% | — | 2 / 0.019 / 0.034 / 0.036 / 0% |
| 7 | 384-px GS | text MIN T0.0 | 23 | 03-25 / 04-17 | 20 m | 48 / 0.004 / 0.012 / 0.028 / 4% | 43 / 0.014 / 0.030 / 0.034 / 12% | 8 / 0.004 / 0.008 / 0.009 / 12% | 6 / 0.030 / 0.053 / 0.054 / 50% |
| 12 | 55-map | text MIN T0.7 (TM / uplift) | 54 | 04-18 / 06-11 | 20 m | 20 / 0.001 / 0.005 / 0.005 / 0% | 25 / 0.003 / 0.008 / 0.009 / 4% | — | 4 / 0.020 / 0.023 / 0.023 / 100% |
| 12 | 55-map | text MIN T0.7 (TM / uplift) | 54 | 04-18 / 06-11 | 50 m | 20 / 0.003 / 0.007 / 0.007 / 0% | 25 / 0.007 / 0.012 / 0.015 / 40% | — | 4 / 0.027 / 0.030 / 0.030 / 100% |

Reading:

- **Hours to days apart: no execution component.** Every Era-1 retest pair
  (groups 13, 17, 18, 21, 22, 23, 24; 0 to 2 days) and the same-day 327-tile
  pair (group 10) have cross-execution spreads equal to their within spreads,
  single-pass and consensus alike. Two days apart on the text track (group 8)
  the consensus rejection rate rises (21 % against 8 %) with the same median.
- **Twenty days apart in March to April 2026: an execution component on
  some configurations, not all.** The image track drifted (groups 4 and 5:
  medians 0.034 and 0.070 at consensus against 0.007 within; 67 % and 100 %
  rejections), as did text MIN at T = 0.0 (group 7: 0.030 against 0.004; 50 %
  against 12 %); text HIGH T0.7 (group 1, 17 days), text MIN T0.3 (group 2)
  and text HIGH T0.0 (group 6) did not (cross spreads inside the within
  spreads). The W7.5 serving-drift explanation (Obs 497) therefore applies
  to the image track and to one text setting, not uniformly.
- **On the 55-map corpus the execution component is larger than the
  within-execution spread, and it grows with the gap.** Eight days apart
  (group 11, text HIGH T0.7, 2026-04-10 against 04-18) the single-pass
  spread at 50 m is 0.006 median against 0.004 within (28 % against 5 %
  rejections) and the five-pass consensus differs by 0.002 to 0.011
  (significant at K = 5 t = 3 only). Fifty-four days apart (group 12, text
  MIN T0.7, the uplift's two halves) the five-pass consensus differs by
  **0.011 to 0.022 F1 at 20 m and 0.018 to 0.030 at 50 m at the boards'
  thresholds (3, 4 and 5 of 5; all p ≤ 0.0013)**, the later execution
  scoring higher with fewer detections, where the within-execution
  single-pass spread is 0.003. The gap depends on the threshold: at 2 of 5
  it is 0.001 at 20 m (p = 0.70) and 0.007 at 50 m, and at 1 of 5 it
  reverses (the earlier execution 0.009 to 0.010 higher, p ≤ 0.0003); the
  three-pass consensus at 3 of 3 differs by 0.023 and 0.029. That is the
  cross-execution consensus floor on the paper's main corpus, with one pair
  of executions to measure it.

| group | buffer | K | t | n det a | n det b | F1 a | F1 b | ΔF1 | p |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 11 | 20 m | 3 | 3 | 7497 | 7690 | 0.4374 | 0.4356 | +0.0018 | 0.7237 |
| 11 | 50 m | 3 | 3 | 7497 | 7690 | 0.5341 | 0.5362 | -0.0021 | 0.6792 |
| 11 | 20 m | 5 | 3 | 13099 | 13573 | 0.3625 | 0.3541 | +0.0084 | 0.0113 |
| 11 | 50 m | 5 | 3 | 13099 | 13573 | 0.4527 | 0.4415 | +0.0112 | 0.0001 |
| 11 | 20 m | 5 | 4 | 8942 | 9206 | 0.4277 | 0.4277 | -0.0001 | 0.9860 |
| 11 | 50 m | 5 | 4 | 8942 | 9206 | 0.5254 | 0.5252 | +0.0002 | 0.9678 |
| 11 | 20 m | 5 | 5 | 5519 | 5728 | 0.4702 | 0.4746 | -0.0044 | 0.4010 |
| 11 | 50 m | 5 | 5 | 5519 | 5728 | 0.5645 | 0.5710 | -0.0065 | 0.2318 |
| 12 | 20 m | 3 | 3 | 9001 | 8129 | 0.3809 | 0.4042 | -0.0233 | 0.0000 |
| 12 | 50 m | 3 | 3 | 9001 | 8129 | 0.4571 | 0.4862 | -0.0291 | 0.0000 |
| 12 | 20 m | 5 | 3 | 12351 | 11652 | 0.3582 | 0.3692 | -0.0109 | 0.0013 |
| 12 | 50 m | 5 | 3 | 12351 | 11652 | 0.4309 | 0.4491 | -0.0182 | 0.0000 |
| 12 | 20 m | 5 | 4 | 10131 | 9188 | 0.3823 | 0.3998 | -0.0175 | 0.0000 |
| 12 | 50 m | 5 | 4 | 10131 | 9188 | 0.4556 | 0.4808 | -0.0252 | 0.0000 |
| 12 | 20 m | 5 | 5 | 7816 | 6930 | 0.3938 | 0.4155 | -0.0217 | 0.0000 |
| 12 | 50 m | 5 | 5 | 7816 | 6930 | 0.4680 | 0.4980 | -0.0300 | 0.0000 |

## 5. Drift timeline from the run metas (W7.6 item 3)

A read-only sweep of every proposer meta (1,317 passes under `outputs/` and
`archive/pre-recovery-2026-07-30/`; agent record
`w76-drift-timeline.md` beside the scripts) grouped 165 transmitted
signatures (model, thinking, temperature, instruction hash, library hash,
image or text, tile size, corpus); 53 occur on more than one date. With at
least 100 items on both dates, one signature passes a 20 % change test on
thought tokens or detections per 1,000 items: `gemini-3-flash-preview`,
HIGH, T = 0.0, image library, 384-px tiles, 2026-03-27 → 2026-04-16 (median
thought tokens 1,322 → 1,601, +21 %; detections per 1,000 items 1,495 →
2,140, +43 %; MAX_TOKENS finishes 3.6 % → 7.1 %). That is the S-9 group 5
pair, now visible in the metas without any scoring. The timeline is thin
where it would help most: the March batch metas (`lib_batch_api.py` v1.5.0)
booked no token usage, minimal-thinking metas record zero thought tokens by
construction, and only 545 of 1,557 metas carry per-item usage. A sentinel
(W7.6 item 5) is the only way to see drift on the text track at MINIMAL
thinking, where detections per pass are the sole signal.

## 6. The 55-map board: proposer-stage replicate floors with the verifier fixed

Every family whose pool holds more passes than a rung uses was rebuilt from
disjoint pass subsets with the board's rung mechanism (§ 1, kind 2; gates
§ 2) and scored at 50 m on reference r2 at the family's carried and oracle
probability thresholds with every vote count the rung allows: A, B and
FOURTH (ten passes: 45 pairs at N = 1, 10 at N = 2, 3 at N = 3, 1 at N = 5),
ARM1, ARM2 and the two image pools (five passes: 10 pairs at N = 1, 15 at
N = 2). UPL is the cross-execution case. 466 subset cells; the full table is
`subset_pairs.csv`, summarised here at the board's own operating points.

| family | N (rung) | prob_t | k | pairs | median \|ΔF1\| | 95th pct | max | rejects |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| A | 1 | 0.15 | 1 | 45 | 0.0034 | 0.0076 | 0.0080 | 20% |
| A | 1 | 0.2 | 1 | 45 | 0.0036 | 0.0082 | 0.0094 | 24% |
| A | 2 | 0.15 | 1 | 10 | 0.0033 | 0.0076 | 0.0083 | 30% |
| A | 2 | 0.15 | 2 | 10 | 0.0043 | 0.0095 | 0.0101 | 30% |
| A | 2 | 0.2 | 1 | 10 | 0.0021 | 0.0071 | 0.0075 | 30% |
| A | 2 | 0.2 | 2 | 10 | 0.0038 | 0.0086 | 0.0090 | 30% |
| A | 3 | 0.15 | 2 | 3 | 0.0010 | 0.0012 | 0.0012 | 0% |
| A | 3 | 0.15 | 3 | 3 | 0.0028 | 0.0051 | 0.0054 | 0% |
| A | 3 | 0.2 | 2 | 3 | 0.0008 | 0.0013 | 0.0014 | 0% |
| A | 3 | 0.2 | 3 | 3 | 0.0025 | 0.0047 | 0.0050 | 0% |
| A | 5 | 0.15 | 3 | 1 | 0.0009 | 0.0009 | 0.0009 | 0% (ΔF1 -0.0009; F1 0.8347 vs 0.8356) |
| A | 5 | 0.15 | 4 | 1 | 0.0027 | 0.0027 | 0.0027 | 0% (ΔF1 +0.0027; F1 0.8383 vs 0.8356) |
| A | 5 | 0.15 | 5 | 1 | 0.0040 | 0.0040 | 0.0040 | 0% (ΔF1 +0.0040; F1 0.8210 vs 0.8170) |
| A | 5 | 0.2 | 3 | 1 | 0.0003 | 0.0003 | 0.0003 | 0% (ΔF1 -0.0003; F1 0.8355 vs 0.8359) |
| A | 5 | 0.2 | 4 | 1 | 0.0024 | 0.0024 | 0.0024 | 0% (ΔF1 +0.0024; F1 0.8368 vs 0.8344) |
| A | 5 | 0.2 | 5 | 1 | 0.0045 | 0.0045 | 0.0045 | 0% (ΔF1 +0.0045; F1 0.8185 vs 0.8140) |
| ARM1 | 1 | 0.1 | 1 | 10 | 0.0022 | 0.0049 | 0.0054 | 0% |
| ARM1 | 1 | 0.15 | 1 | 10 | 0.0015 | 0.0033 | 0.0034 | 0% |
| ARM1 | 2 | 0.1 | 1 | 15 | 0.0042 | 0.0075 | 0.0081 | 27% |
| ARM1 | 2 | 0.1 | 2 | 15 | 0.0024 | 0.0038 | 0.0040 | 0% |
| ARM1 | 2 | 0.15 | 1 | 15 | 0.0028 | 0.0067 | 0.0070 | 20% |
| ARM1 | 2 | 0.15 | 2 | 15 | 0.0014 | 0.0035 | 0.0042 | 0% |
| ARM2 | 1 | 0.8 | 1 | 10 | 0.0015 | 0.0023 | 0.0025 | 0% |
| ARM2 | 1 | 0.95 | 1 | 10 | 0.0015 | 0.0031 | 0.0036 | 0% |
| ARM2 | 2 | 0.8 | 1 | 15 | 0.0046 | 0.0080 | 0.0082 | 33% |
| ARM2 | 2 | 0.8 | 2 | 15 | 0.0013 | 0.0031 | 0.0033 | 0% |
| ARM2 | 2 | 0.95 | 1 | 15 | 0.0047 | 0.0079 | 0.0081 | 40% |
| ARM2 | 2 | 0.95 | 2 | 15 | 0.0016 | 0.0033 | 0.0039 | 0% |
| B | 1 | 0.15 | 1 | 45 | 0.0031 | 0.0067 | 0.0073 | 13% |
| B | 1 | 0.2 | 1 | 45 | 0.0031 | 0.0069 | 0.0075 | 18% |
| B | 2 | 0.15 | 1 | 10 | 0.0033 | 0.0082 | 0.0088 | 30% |
| B | 2 | 0.15 | 2 | 10 | 0.0012 | 0.0024 | 0.0025 | 0% |
| B | 2 | 0.2 | 1 | 10 | 0.0031 | 0.0074 | 0.0083 | 30% |
| B | 2 | 0.2 | 2 | 10 | 0.0016 | 0.0031 | 0.0036 | 0% |
| B | 3 | 0.15 | 2 | 3 | 0.0014 | 0.0025 | 0.0026 | 0% |
| B | 3 | 0.15 | 3 | 3 | 0.0039 | 0.0049 | 0.0050 | 33% |
| B | 3 | 0.2 | 2 | 3 | 0.0016 | 0.0019 | 0.0019 | 0% |
| B | 3 | 0.2 | 3 | 3 | 0.0033 | 0.0054 | 0.0057 | 33% |
| B | 5 | 0.15 | 3 | 1 | 0.0005 | 0.0005 | 0.0005 | 0% (ΔF1 -0.0005; F1 0.8228 vs 0.8232) |
| B | 5 | 0.15 | 4 | 1 | 0.0015 | 0.0015 | 0.0015 | 0% (ΔF1 +0.0015; F1 0.8437 vs 0.8423) |
| B | 5 | 0.15 | 5 | 1 | 0.0023 | 0.0023 | 0.0023 | 0% (ΔF1 -0.0023; F1 0.8503 vs 0.8526) |
| B | 5 | 0.2 | 3 | 1 | 0.0007 | 0.0007 | 0.0007 | 0% (ΔF1 -0.0007; F1 0.8285 vs 0.8292) |
| B | 5 | 0.2 | 4 | 1 | 0.0016 | 0.0016 | 0.0016 | 0% (ΔF1 +0.0016; F1 0.8476 vs 0.8460) |
| B | 5 | 0.2 | 5 | 1 | 0.0014 | 0.0014 | 0.0014 | 0% (ΔF1 -0.0014; F1 0.8516 vs 0.8530) |
| FOURTH | 1 | 0.96 | 1 | 45 | 0.0025 | 0.0059 | 0.0061 | 11% |
| FOURTH | 1 | 0.98 | 1 | 45 | 0.0025 | 0.0060 | 0.0062 | 11% |
| FOURTH | 2 | 0.96 | 1 | 10 | 0.0037 | 0.0065 | 0.0069 | 20% |
| FOURTH | 2 | 0.96 | 2 | 10 | 0.0011 | 0.0020 | 0.0022 | 0% |
| FOURTH | 2 | 0.98 | 1 | 10 | 0.0038 | 0.0064 | 0.0067 | 20% |
| FOURTH | 2 | 0.98 | 2 | 10 | 0.0011 | 0.0021 | 0.0023 | 0% |
| FOURTH | 3 | 0.96 | 2 | 3 | 0.0015 | 0.0022 | 0.0023 | 0% |
| FOURTH | 3 | 0.96 | 3 | 3 | 0.0024 | 0.0038 | 0.0039 | 0% |
| FOURTH | 3 | 0.98 | 2 | 3 | 0.0014 | 0.0021 | 0.0022 | 0% |
| FOURTH | 3 | 0.98 | 3 | 3 | 0.0024 | 0.0038 | 0.0039 | 0% |
| FOURTH | 5 | 0.96 | 3 | 1 | 0.0014 | 0.0014 | 0.0014 | 0% (ΔF1 -0.0014; F1 0.8574 vs 0.8588) |
| FOURTH | 5 | 0.96 | 4 | 1 | 0.0021 | 0.0021 | 0.0021 | 0% (ΔF1 +0.0021; F1 0.8748 vs 0.8726) |
| FOURTH | 5 | 0.96 | 5 | 1 | 0.0020 | 0.0020 | 0.0020 | 0% (ΔF1 -0.0020; F1 0.8758 vs 0.8778) |
| FOURTH | 5 | 0.98 | 3 | 1 | 0.0013 | 0.0013 | 0.0013 | 0% (ΔF1 -0.0013; F1 0.8571 vs 0.8584) |
| FOURTH | 5 | 0.98 | 4 | 1 | 0.0021 | 0.0021 | 0.0021 | 0% (ΔF1 +0.0021; F1 0.8744 vs 0.8723) |
| FOURTH | 5 | 0.98 | 5 | 1 | 0.0020 | 0.0020 | 0.0020 | 0% (ΔF1 -0.0020; F1 0.8754 vs 0.8774) |
| G37IMG-ARM1 | 1 | 0.1 | 1 | 10 | 0.0020 | 0.0066 | 0.0066 | 20% |
| G37IMG-ARM1 | 2 | 0.1 | 1 | 15 | 0.0069 | 0.0116 | 0.0124 | 80% |
| G37IMG-ARM1 | 2 | 0.1 | 2 | 15 | 0.0008 | 0.0022 | 0.0027 | 0% |
| G37IMG-ARM2 | 1 | 0.88 | 1 | 10 | 0.0022 | 0.0055 | 0.0064 | 10% |
| G37IMG-ARM2 | 1 | 0.9 | 1 | 10 | 0.0020 | 0.0055 | 0.0062 | 10% |
| G37IMG-ARM2 | 2 | 0.88 | 1 | 15 | 0.0066 | 0.0086 | 0.0087 | 60% |
| G37IMG-ARM2 | 2 | 0.88 | 2 | 15 | 0.0019 | 0.0030 | 0.0035 | 0% |
| G37IMG-ARM2 | 2 | 0.9 | 1 | 15 | 0.0065 | 0.0083 | 0.0085 | 60% |
| G37IMG-ARM2 | 2 | 0.9 | 2 | 15 | 0.0018 | 0.0030 | 0.0034 | 0% |
| G3IMG-ARM1 | 1 | 0.15 | 1 | 10 | 0.0068 | 0.0170 | 0.0189 | 50% |
| G3IMG-ARM1 | 2 | 0.15 | 1 | 15 | 0.0241 | 0.0301 | 0.0301 | 80% |
| G3IMG-ARM1 | 2 | 0.15 | 2 | 15 | 0.0035 | 0.0075 | 0.0077 | 13% |
| G3IMG-ARM2 | 1 | 0.88 | 1 | 10 | 0.0068 | 0.0177 | 0.0204 | 60% |
| G3IMG-ARM2 | 1 | 0.95 | 1 | 10 | 0.0069 | 0.0179 | 0.0206 | 50% |
| G3IMG-ARM2 | 2 | 0.88 | 1 | 15 | 0.0265 | 0.0307 | 0.0318 | 80% |
| G3IMG-ARM2 | 2 | 0.88 | 2 | 15 | 0.0033 | 0.0076 | 0.0087 | 13% |
| G3IMG-ARM2 | 2 | 0.95 | 1 | 15 | 0.0262 | 0.0315 | 0.0328 | 80% |
| G3IMG-ARM2 | 2 | 0.95 | 2 | 15 | 0.0025 | 0.0071 | 0.0081 | 13% |
| UPL — cross-execution (04-18 vs 06-11) | 5 | 0.15 | 3 | 1 | 0.0032 | 0.0032 | 0.0032 | 0% (ΔF1 -0.0032; F1 0.8156 vs 0.8188) |
| UPL — cross-execution (04-18 vs 06-11) | 5 | 0.15 | 4 | 1 | 0.0036 | 0.0036 | 0.0036 | 0% (ΔF1 +0.0036; F1 0.7894 vs 0.7858) |
| UPL — cross-execution (04-18 vs 06-11) | 5 | 0.15 | 5 | 1 | 0.0060 | 0.0060 | 0.0060 | 0% (ΔF1 +0.0060; F1 0.7347 vs 0.7286) |

(Rows at the board's operating points, k ≥ N/2; the k = 1 union points of two- and three-pass subsets are in `subset_pairs.csv`. The parenthesis on a one-pair row gives the signed ΔF1 and both cells' F1.)

| N (rung) | pairs | median \|ΔF1\| | 95th pct | max | rejects |
|---:|---:|---:|---:|---:|---:|
| 1 | 370 | 0.0028 | 0.0078 | 0.0206 | 17% |
| 2 | 420 | 0.0027 | 0.0261 | 0.0328 | 27% |
| 3 | 54 | 0.0025 | 0.0113 | 0.0134 | 24% |
| 5 | 18 | 0.0018 | 0.0041 | 0.0045 | 0% |

Reading:

- **At the board's operating points the proposer-stage floor is small.**
  Two disjoint five-pass rungs of one execution differ by 0.001 to 0.005
  F1 at k = 3 to 5 (one pair per family); three-pass rungs by 0.001 to
  0.006 at k = 2 or 3 (three pairs per family); single verified passes by
  0.003 median and about 0.008 at the 95th percentile (45 pairs per
  Gemini 3 text family; 0.006 for the 3.7 image pool; 0.017 to 0.018 for
  the Gemini 3 image pool, whose passes vary more). Only the k = 1 union
  points of two- and three-pass subsets, which no board cell uses, reach
  0.01 to 0.03.
- **The verifier absorbs most of the proposer drift.** UPL's first five
  passes (2026-04-18) and last five (2026-06-11) differ by 0.011 to 0.030
  F1 as proposer-only consensus at the board's thresholds (§ 4,
  p ≤ 0.0013);
  through the fixed verifier at the board's band they differ by 0.003
  (k3), 0.004 (k4) and 0.006 (k5), with the later execution's cells
  holding 50 to 90 fewer detections. The verifier re-scores each candidate
  on its crop, so a candidate that one execution proposes and the other
  does not changes the cell only if the verifier also accepts it. That is
  the mechanism behind the small proposer-verifier floors above, and it is
  why the architecture's deployment claims are better placed than the
  consensus-only claims of § 3.
- **The tile-swap test still over-rejects replicate pairs at the single-pass
  rung.** Between two verified single passes of one execution (differences
  of 0.003 median, 0.008 at the 95th percentile) it rejects 11 to 24 % of
  pairs for the Gemini 3 text families; at N = 5 it rejects none of the
  eighteen pairs, and UPL's three cross-execution pairs are not significant
  either. S-10 therefore bites hardest exactly where the board's N = 1 rows
  are read.
- **What the floors do not cover.** The verifier's own re-invocation noise
  (of order +0.001 F1 at the carried points, measured on one pair of legs
  per arm, same week, batch against flex) and its cross-date drift, which
  no replicate measures. A conservative full floor for a board claim is
  therefore the proposer floor at the rung plus 0.001: **about 0.005 at
  N = 5, 0.007 at N = 3, 0.009 at N = 1** for the Gemini 3 text families;
  for a cross-execution claim add the one measured cross-execution
  proposer-verifier difference, 0.006 at N = 5, and the verifier-vintage
  effect of § 6a, 0.004 to 0.007, giving **about 0.011 to 0.013**.
  Where a claim compares an image family at N = 1 the floor is 0.018.

## 6a. The verifier-date confound, checked free on text MIN (added 2026-10-06)

The 3-of-5 cells of the Gemini 3 board (TH7, T03, TM at k3) add a vote-3
shell whose candidates were verified on 2026-06-06, 40 to 49 days after the
4-of-5 sets (§ 7.2, lesson (i)). For text MIN a free test exists: the
uplift run re-verified, on 2026-06-11, every candidate with three or more
votes of ten passes, and its passes 1 to 5 are TM's. Matched by centroid,
TM's April-verified 4-of-5 set and its June-6 shell both have June-11
near-replicates: 76 % and 67 % of candidates within 2 m, 98 % and 94 %
within 5 m; of the 4-of-5 pairs within 5 m, 6,985 have byte-identical crops
(the same request). The same verifier configuration ran each time
(`gemini-3-flash-preview`, minimal, T = 0, `verify_adversarial` text). Agent
record, scripts and results: `verifier-date-tm-check.md`, `vdate_*.py`,
`vdate-results*.json` beside this report (they ran on sapphire with
`/tmp/vdate/` as scratch). The committed mixed-date probabilities reproduce
the board exactly (TM-k4 0.7826, TM-oracle 0.8103) before anything is
swapped.

| quantity (50 m, r2) | mixed dates (board) | one date (all June-11, 2 m match) | difference |
|---|---:|---:|---:|
| TM k3 − k4 at 0.15 | +0.0275 | +0.0264 | −0.0011 |
| TM-oracle (0.20, k3) − TM-k4 (0.15, k4) | +0.0277 | +0.0255 | −0.0022 |
| TM-k4 itself (same candidates, April → June probabilities) | 0.7826 | 0.7867 | +0.0041, p = 0.038 |

Reading:

- **Lesson (i)'s threshold effect is not a verifier-date artefact on text
  MIN.** Under one verifier date k3 still beats k4 by +0.025 to +0.027 in
  every variant (2 m, 5 m, identical crops only, k4 set only), all
  p < 0.0001; mixing dates inflated it by 0.001 to 0.002.
- **The verifier itself drifted between April and June, a little.** On
  identical candidates the June verifier flips 3.8 to 4.1 % of decisions at
  0.15 against 2.4 to 2.5 % in the same-week control (June 6 against June
  11), balanced in direction (148 up, 146 down), and the cell it scores
  moves by +0.0036 to +0.0069 F1 depending on the match rule (true
  positives 3,476 → 3,495, false positives 389 → 372). That is the first
  measured cross-date verifier floor on this corpus: five to nine times the
  same-week re-invocation band of § 1. The p-values are not corrected for
  the several variants tested.
- **What it does not settle.** TH7 and T03 have no later re-verification of
  their 4-of-5 sets, so their k3 − k4 contrasts are checked only by
  analogy: a date effect of the size measured here (0.001 to 0.002 on the
  contrast) cannot overturn TH7's +0.022, and leaves T03's +0.009 standing
  but no longer by a wide margin. A paid same-date re-verification of T03's
  full vote-3-and-above set (13,945 candidates, about US$10 at the
  register's US$0.0007 a candidate) would settle T03 directly, if
  `gemini-3-flash-preview` is still served.
- **For every cross-date comparison on the board**, the April-verified cells
  (TH7-k4, T03-k4, TM-k4, IM) carry a verifier-vintage component of a few
  thousandths of F1 against cells verified later; § 6's cross-execution
  floor now includes it.

## 6b. The 55-map floors from every pass subset (added 2026-10-07)

§ 6's floors at N = 5 rested on ONE disjoint pair of five-pass rungs per
ten-pass family, at N = 3 on three pairs, and at N = 10 on none, so its
"95th percentiles" were typical differences, not floors. A second analysis
(`floors-v2/` beside this report: method, scripts, gates, results; agent
record `floors-v2/floors-v2.md`) rebuilt every family's rung from EVERY
K-subset of its passes with the § 6 mechanism (verifier held fixed):
16,260 cells. It reproduces every § 2 gate count, all 460 W2.7 subset
cells and 486 matching gold-standard cells exactly.

**Method.** The run-to-run SD of a K-pass rung is estimated from the
variance of F1 over all K-subsets, corrected for the subsets' overlap:
SD_run = sqrt(V_sub · N / (N − K)), which is unbiased for a mean and
conservative in expectation for consensus F1; the floor is
1.96 · √2 · SD_run. **Validation:** on the 30-pass gold-standard pools, the
estimate from one 10-pass slice is 1.08 times the disjoint-subset truth on
Era-1 (seven pools) and 1.15 times on the 384-px corpus (two pools), pooled
over K and t: conservative, as expected. A single family's floor carries
about ±15 to 40 % (jackknife).

| family, rung (point) | new floor | § 6 floor (pairs) |
|---|---:|---:|
| A, N5 carried = oracle (0.15, k4) | 0.0068 | 0.0027 (1) |
| B, N5 carried (0.15, k5) | 0.0056 | 0.0023 (1) |
| FOURTH, N5 carried (0.98, k5) | 0.0054 | 0.0020 (1) |
| A, N3 carried (0.15, k3) | 0.0093 | 0.0051 (3) |
| B, N3 carried (0.15, k3) | 0.0051 | 0.0049 (3) |
| A / B / FOURTH, N10 carried (extrapolated) | 0.0068 / 0.0056 / 0.0054 (high ends 0.0083–0.0107) | — (0.005 used) |
| A / B / FOURTH, N1 | 0.0090 / 0.0080 / 0.0069 | 0.0082 / 0.0069 / 0.0060 (45) |

Reading:

- **The five-pass floors were 2.4 to 3.9 times too small.** The full
  within-execution floors (adding the verifier's 0.001 re-invocation band)
  are about **0.007 at N = 5, 0.006 to 0.010 at N = 3, 0.008 to 0.010 at
  N = 1 and 0.006 to 0.008 at N = 10** (up to 0.012); the Gemini 3 image
  pool 0.017 to 0.021. The five-pass families' N = 5 floors (ARM1 0.0050,
  ARM2 0.0069–0.0072) rest on subsets of at most four passes and are the
  weakest numbers here.
- **The floor barely shrinks with K.** The fitted exponents of SD on K run
  from −0.13 to −0.30, not the −0.5 of a mean: through the verifier, what
  varies from run to run is which borderline candidates cross the vote
  threshold, not how many passes vote.
- **Nested contrasts have their own, smaller floors.** A threshold or rung
  contrast on the same passes is measured on each subset and its spread
  taken (`floors-v2/results/nested_*.csv`); the shared passes cancel most of
  the run-to-run variance (ARM2's carried-to-oracle tax: 0.0020).
- **The PI's between-pass model understates the floor.** Simulating fresh
  rungs from each candidate's per-pass vote rate, as if candidates voted
  independently, gives floors 21 to 32 % too small (median) on the text and
  3.7 families and three times too small on the Gemini 3 image pool,
  because one pass moves many candidates together; a pass bootstrap
  overstates it 1.3 to 3.3 times. The pass, not the candidate, is the unit
  to resample, which is what the subset method does.

The § 7.2 screen below now uses these floors.

## 7. The paper's configuration-level claims against the floors

A read-only inventory of `docs/paper/results-draft.md` (agent record
`claims-inventory-draft.md` beside the scripts; every figure it quotes from
the boards was re-read from `final_board_50m.json` and the register before
use here) finds **103 configuration-level claims**: § R7.1 12, § R7.2 16,
§ R7.3 22, § R2 9, § R3 7, § R4 13, § R5 15, § R6 7, § R9 2. **70 compare
outputs from different execution dates** (or an arm whose pool spans
dates), and **88 rest on single runs in every arm**; all 50 claims of the
55-map board (§ R7) are single-run in every arm. The screens below apply
D45: a configuration claim stands where the tile-swap test rejects AND the
difference exceeds the floor for its corpus and aggregation; where the arms
come from different executions the cross-execution floor applies.

### 7.1 Gold-standard and Era-1 claims (floors of § 3 and § 4)

| claim | difference | floor that applies | verdict under D45 |
|---|---|---|---|
| R7.3-01: the 3.7 text proposer under the Gemini 3 verifier "landed above the Gemini 3 plateau", so G1 fired and the family escalated (draft L755–761) | +0.0178, tile-swap p = 0.1697 (register `gemini37-screen-2026-08-28`; the draft omits the p) | 487-tile single-pass 0.030; cross-execution (10 days, Aug) not measured | **Not a configuration claim: not significant and under the floor.** The escalation decision was procedural; the sentence should say the direction only. R7.3-21's "about five times the text-side gain" divides by this difference and goes with it. |
| R7.3-22/23: "text beats image" is a Gemini 3 property (gap +0.0549 → −0.0115 / −0.0043) (L839–843; §§ R2, R4) | gap change −0.059 to −0.066; four single-run arms on four dates (2026-08-18/24, 08-28, 08-28/29, 09-01); K = 10 against K = 5 | 487-tile cross-execution single-pass medians 0.037 / 0.061 (S-9, 20 days, March→April); within-execution consensus 0.02 to 0.03 | **Reword.** The gap change is the size of the measured cross-date drift on this corpus; a tile-swap p cannot see it. Claimable only as "on these runs"; a same-day bridging pair would settle it (D47, W5). |
| R4-21/23: the lowest Tier-1 Era-2 cell against the best Gemini 3 sweep optimum, +0.0195 (L368–374) | p = 0.178, BH 0.244; 133 days apart | 487-tile 0.030 | **Not resolved**; the tier boundary is not a resolved difference for this pair (the draft already says so). |
| R4-24: the top Era-2 cell against the best Gemini 3 optimum, +0.036, BH 0.028 (L374–375) | +0.036; 137 days apart | 487-tile single-pass 0.030; cross-execution medians 0.037 / 0.061 | **Clears the within floor narrowly; inside the cross-date band.** State both. |
| R4-03/04 (H2): PV beats consensus-only, +0.076 (L300–304) | same 30 passes; verifier added later | 487-tile consensus K = 30 not measured (one pool); K = 10 t = 9/10 0.019 to 0.025; verifier re-invocation of order 0.001 | **Stands** (a registered claim; the margin is three times the widest measured floor). |
| R3-04/05: the diversity dividend, HIGH beats MIN at matched N by +0.067 F1 (L260–267) | +0.067, adjacent days | Era-1 K = 30 not measured; K = 10 t = 8 0.030 | **Stands** on margin; the 487-tile sibling (+0.153, same day) is cleaner. |
| R5 (fifteen claims, eleven cross-execution): every difference under 0.030 except R5-10b (−0.0355, 80 days) | ties | 487-tile 0.030; cross-date band 0.037 to 0.061 | **Ties are consistent with the floors**, which is what tie claims need; R5-11's meta-rule inherits the cross-execution caveat. R5-10b sits at the floor inside an 80-day gap: say so. |
| R2-09 (H1): the registered modality contrast is null, p = 0.1774 (L224–227) | paired bootstrap p | — | **Reporting:** D42 retired the bootstrap p; quote the permutation p (W1, C-25). |
| R2-11/12 (H7): low temperature beats T = 1.0, +0.072, replicate means of three per arm, same day | +0.072 | Era-1 single-pass 0.034 | **Stands.** |

### 7.2 The 55-map board (floors of § 6)

Floors used (§ 6b, 2026-10-07): within-execution about 0.007 (N = 5),
0.006–0.010 (N = 3), 0.008–0.010 (N = 1), 0.006–0.008 (N = 10), each
family's own where measured; nested contrasts their own (§ 6b);
cross-execution the within floor plus 0.004–0.007 of verifier vintage
(§ 6a), about 0.010–0.018. Rows below marked "§ 6b" changed verdict on
2026-10-07; every other verdict holds on a thinner margin
(`floors-v2/results/rescreen.csv`). Differences are the r2
board's tile-swap results (`final_board_50m.json` → `pairwise`, read
2026-10-06), or the campaign's own per-sheet test where the draft quotes
it.

| claim | difference, test | executions | floor | verdict under D45 |
|---|---|---|---|---|
| R7.1-05/08, lesson (i): the carried T0.7 × 4-of-5 left +0.022 on the table against the joint oracle T0.3 × 3-of-5 (L565–572, L595–599) | +0.0225, p < 0.0001 | CROSS 8 days (proposers 04-18 against 04-26/27); the k3 shell's candidates verified 2026-06-06, 40–49 days after the k4 legs | 0.011–0.013 | **Clears the floor.** The k3 cells are mixed-verifier-execution cells; on text MIN the threshold effect survives a one-date reading (§ 6a: +0.0275 → +0.0264), so say so, and name the date mix. |
| R7.1-09a: T0.3, 3-of-5 beats 4-of-5 by +0.009 (L599–601) | +0.0092, BH 0.0005 | nested passes; verifier dates differ (04-26/27 against 06-06) | 0.0069 (upper 0.0111), borrowed from A and B | **§ 6b: clears narrowly** (1.3 times), with the verifier-date caveat of § 6a; Run A (the T03 re-verification) settles it directly. |
| R7.1-09b/c: the same for T0.7 (+0.022) and MIN (+0.028) | BH < 0.0001 | as above | as above | **Stand on margin** (twenty times the verifier band); same caveat. |
| R7.1-11, lesson (ii): HIGH beats MIN at K = 5, +0.028 to +0.034 (L605–606); R6-06 (L505–511) | p < 0.0001 | SAME-DAY proposers (2026-04-18), same-day k3 shells | 0.005 | **Stands**; the cleanest configuration claim on the board. |
| R7.1-12/15, lesson (iii): the image cell is the sole Tier-1 cell on tile-MCC, +0.022 MCC (L606–615) | MCC BH 0.0020 | CROSS 8 days, k3 shells 06-06 | no MCC floor measured | **Stands on F1 reasoning only**; an MCC floor is not measured (W2.5). |
| R7.2-13a: B beats A at the carried primaries, −0.0096 (L671–672) | per-sheet p = 0.0147; r2 tile-swap −0.0106, p = 0.0075 | ADJACENT (same day) | 0.0072 (upper 0.0106) | **§ 6b: stands narrowly**, exactly at the floor's upper bound; 13b and 13c carry "B beats A". |
| R7.2-13b/c: at the oracles −0.0141; at N = 5 −0.0116 | p = 0.0001; r2 −0.0120, p = 0.0024 | ADJACENT | 0.0072 | **Stand** (2.0 and 1.7 times the floor). |
| R7.2-15: "its sign held at every rung tested" (L679–680) | A-N1-oracle beats B-N1-oracle +0.0214, p < 0.0001 | ADJACENT | 0.009 | **Correct the sentence**: the sign reverses at N = 1 (a resolved difference, above the floor). |
| R7.2-16a, P7: N = 5 within noise of N = 10 (L682–683) | A −0.0009, p = 0.55; B +0.0006, p = 0.72 | SAME (nested) | 0.005 | **A tie consistent with the floor.** |
| R7.2-16b: the oracles keep a residue (−0.004, −0.005; per-sheet BH-significant) | canonical −0.0040 / −0.0053; r2 tile-swap +0.0036 (BH 0.0096) / +0.0043 (BH 0.0038), N = 10 above N = 5 | SAME (nested) | 0.005 | **Inside the floor: not a configuration difference.** Reword. |
| R7.2-04/05/11/12/30/32b: A and B against the April incumbents (+0.023 to +0.034 carried; +0.016 geometry gap on r2) | p ≤ 0.0001 | CROSS about 4 months, with thinking, K and geometry also changed | 0.011–0.013 | **Clear the floor**, but they are not single-factor claims: say "run A/B against run TH7" rather than "geometry" or "thinking". The P5 decomposition is chain-dependent (r2: incumbent tax +0.0237, gap +0.0161, not +0.0324 and +0.0027), so L745–749's "no verdict depends on the chain" needs correcting. |
| R7.2-30: B-N5-carried above T03-oracle, +0.0104 (L725–727) | p = 0.0177 | CROSS about 4 months | 0.011–0.013 | **Inside the cross-execution floor:** state as "above by 0.010, inside the cross-date band". |
| R7.2-31: the image cell holds the highest Gemini 3 tile-MCC (0.711) (L727–729) | untested; B-N3-oracle 0.713 and B-N10-oracle 0.712 exceed it | CROSS | — | **Restrict to carried cells.** |
| R7.2-32a: B at N = 5 "above" its own N = 10 carried point (L729–733) | +0.0006, p = 0.72 | SAME | 0.005 | **A tie**: say "equal to". |
| R7.3-04, D1: arm 1 against B N = 5, +0.0056, p = 0.35 (L768–772) | r2 +0.0048, p = 0.27 | CROSS 3–6 days (D48: within floor) | 0.0063 | **Tie, inside the floor** (as the draft reads it). |
| R7.3-05a/15: arm 2 above the incumbent stack +0.0325; above B's N = 10 oracle +0.0267 / +0.0311 (L772, L805–810) | p < 0.0001 | CROSS 3–6 days | 0.011–0.013 | **Stand** (about twice the floor); the headline survives. |
| R7.3-05b/06: the verifier axis, +0.0234 (fourth against B K = 10) and +0.0270 (arm 2 against arm 1) | p < 0.0001 | same proposer; verifiers 4–5 days apart / same day | 0.001 (verifier band) + 0.005 | **Stand.** |
| R7.3-06b: the proposer axis under the 3.7 verifier is not significant (+0.0107, per-sheet p = 0.074) (L776–777) | r2 tile-swap +0.0099, p = 0.0198, BH 0.024 | CROSS 3–6 days (D48: within floor); K = 5 against K = 10 | 0.0072 | **D48: clears narrowly (1.4 times) and is test-dependent:** the "not significant" reading does not hold on D42's test; report both tests and call it a small proposer-axis difference, not a null. |
| R7.3-07: the 3.7 verifier's transfer tax "only +0.0043" (L779–781) | canonical adjusted p = 0.000162; r2 tile-swap +0.0044, p < 0.0001 | SAME (nested threshold) | own floor 0.0020 (upper 0.0033) | **§ 6b: a small real effect**, 2.1 times its own floor; the earlier screen applied an independent-run floor to a contrast that shares its passes. Keep "small", drop "only". |
| R7.3-18a/b: saturation by N = 3 for the all-3.7 stack (−0.0023) but not for arm 1 (+0.0076) (L818–821) | p = 0.12; adjusted p = 0.000162 | SAME (nested) | 0.007 (N = 3) | **18a a tie; 18b at the floor** (0.0076 against 0.007): "replicates" overstates it. |
| R7.3-19: a single 3.7 pass at its rung oracle above the five-pass incumbent (+0.0107 on r2) (L821–825) | p = 0.0125, BH 0.015 | CROSS 3–6 days (D48: within floor) | 0.0055 | **D48: clears (1.9 times).** |
| R6-12a: doubling MIN passes, UPL above TM-k3 by +0.017 (L536–538) | p < 0.0001 | MIXED: the gain is carried by passes 6–10, 54 days later | 0.011–0.013 | **Clears the floor, but is confounded with execution**: the proposer-only consensus of the June passes alone scores 0.02 to 0.03 above the April passes (§ 4). Say "ten passes from two executions". |
| R6-12b: UPL significantly below HIGH, −0.0106, "closing about half the gap" (L535–542) | r2 −0.0106, p = 0.0165, BH 0.021 | MIXED against SAME-DAY | 0.011–0.013 | **Inside the floor**: "a priced trade, not a tie" is not resolved. |
| R9-03: the vote-threshold direction reversed between GS and deployment (L968–972) | GS p = 0.11–0.43 against 55-map BH ≤ 0.001 | CROSS corpora and dates; the 55-map k3 arms are the 06-06 shells | — | **Stands as stated** (a resolved difference on deployment against a tie on GS), with the verifier-date caveat. |
| R9-08/09: TH7-k3 tied with T03-k3, +0.0006, p = 0.855 (L997–1004) | tie | CROSS 8 days | 0.011–0.013 | **A tie consistent with the floor.** |

**What this changes.** Of the 50 board claims, the headline (all-3.7 above
every Gemini 3 cell), the verifier-axis result, lesson (ii), the April-to-
August transfer and "B beats A" at the oracles and at N = 5 clear their
floors, on the § 6b floors by about 1.7 to 3 times. Under § 6b one verdict
reverses: the 3.7 verifier's "+0.0043" tax (R7.3-07) is a small real effect
against its own nested floor, not noise. Two hold only narrowly: B beats A at
the carried primaries (R7.2-13a, at the floor's upper bound) and T03's
3-of-5 over 4-of-5 (R7.1-09a, 1.3 times a borrowed floor). Four sit at or
inside a floor and need rewording as output differences or ties: the oracle
saturation residue (R7.2-16b), B N = 5 "above" N = 10 (R7.2-32a), arm 1's
non-saturation (R7.3-18b, inside its upper bound) and the uplift "half the
gap" (R6-12b). The proposer-axis "null" (R7.3-06b) is reworded the other way:
under D42's test and D48's floor it is a small difference, not a null. Two need a correction of fact (R7.2-15's sign at N = 1;
R7.2-11/12's chain dependence) and one a restriction (R7.2-31). Lesson (i)
and every 3-of-5-against-4-of-5 contrast mix verifier dates; on text MIN a
one-date reading moves the contrast by only 0.001 to 0.002 (§ 6a), so the
claims stand with the date mix named; Run A (T03, about US$10) settles the
narrowest of them. **Ruled (D48, 2026-10-07):** runs at most seven days apart take the
same-week floor, so R7.3-06b and R7.3-19 clear their within floors (1.4 and
1.9 times) and R7.3-04 stays a tie.

## 8. What follows

1. **For the paper (W1.5, drafted for the PI's review):** the rewordings and
   corrections of § 7 in `docs/paper/results-draft.md`, a one-paragraph
   statement of the floors in § R0 (which stage each covers, and that
   same-signature runs on different dates are not replicates: Obs 497), and
   the run date beside every cell in the board tables.
2. **For the boards:** a D9 note on the signed 55-map analyses recording the
   floors of § 6 and the verifier-date confound of the k3 cells; no tier
   changes (the floors change how differences are read, not the tests).
3. **Replicate runs (D47, each with its own API gate):** (a) optional
   since § 6a: a same-date re-verification of T03's vote-3-and-above set
   (about US$10), the one family whose k3 − k4 margin (+0.009) a date effect
   of the measured size could approach; (b) a same-day bridging pair for the
   modality reversal on the 487-tile corpus; (c) a sentinel configuration
   on a fixed tile set at every future run date (W7.6 item 5), so drift is
   measured and not inferred. Nothing else in § 7 needs a run.
4. **Engineering:** pin the pass order before any committed union is
   regenerated (§ 2); carry the floors into `lib_permutation` as an
   optional "floor" field on every contrast so a report cannot print a
   significant difference without the floor beside it (W2.5).
5. **Not done here (W7.6 items 4 and 5):** which tiles flip between
   replicates against the ground-truth reviews and FP classes, and the
   sentinel design; both are offline and can follow.

## Changelog

### 2026-10-07 (latest) — D48 applied to the three short-gap claims

PI ruling D48: runs at most seven days apart take the same-week floor.
R7.3-04 stays a tie; R7.3-06b and R7.3-19 clear (1.4 and 1.9 times); § 7.2's
open question becomes the ruling. No other row changes. Commit: see git log
for this entry's date.

### 2026-10-07 (later) — § 6b: the 55-map floors from every pass subset

**Trigger**: a side review noted that § 6's floors rested on one to three
replicate pairs; the PI asked for a more precise method. § 6b added from
`floors-v2/` (every K-subset of each family's passes, overlap-corrected,
validated on the 30-pass gold-standard pools); § 7.2's floors line, three
rows and its summary updated.

| | Before | After |
|---|---|---|
| 55-map within floor, N = 5 | 0.005 (one pair) | about 0.007 (252 subsets per family) |
| R7.3-07 (3.7 verifier's tax) | inside the floor, "noise-sized" | a small real effect against its own nested floor (0.0020) |
| R7.2-13a (B beats A, carried) | stands | stands narrowly (at the floor's upper bound) |
| R7.1-09a (T03 k3 over k4) | reword | clears narrowly (1.3 times), date caveat kept |

**What did NOT change**: the gold-standard floors (§ 3), § 6a, and every
other § 7 verdict (on thinner margins). Commit: see git log for this
entry's date.

### 2026-10-07 — §§ 4 and 6: the uplift's cross-execution range corrected

Found by the agent writing Obs 506, which re-read `gs_consensus_pairs.csv`.
§ 4 said the uplift's two executions differ by "0.020 to 0.022 F1 at 20 m
and 0.025 to 0.030 at 50 m at every threshold, all p < 0.0001", and § 6
repeated it. The table supports that range only at 4 and 5 of 5.

| | Before | After |
|---|---|---|
| Range, boards' thresholds | 0.020–0.022 (20 m), 0.025–0.030 (50 m) "at every threshold" | 0.011–0.022 (20 m), 0.018–0.030 (50 m) at 3–5 of 5, p ≤ 0.0013 |
| Lower thresholds | not stated | 2 of 5: 0.001 (20 m, p = 0.70), 0.007 (50 m); 1 of 5: reversed, earlier execution 0.009–0.010 higher |

**What did NOT change**: the 55-map within-execution floors, § 6a, and every
§ 7 verdict (the cross-execution floor uses the proposer-verifier
difference, 0.003–0.006, not this proposer-only range). Commit: see git log
for this entry's date.

### 2026-10-06 (latest) — § 6a: the verifier-date confound checked on text MIN

**Trigger**: the PI asked how much the k3 shells' June verification matters.
A free test existed (the uplift run re-verified TM's candidates on
2026-06-11); an agent ran it read-only on sapphire. § 6a added; § 6's
cross-execution floor and § 7.2's floors line updated.

| | Before | After |
|---|---|---|
| Cross-execution floor (55-map, N = 5) | about 0.011 | about 0.011 to 0.013 (verifier vintage 0.004 to 0.007 added) |
| R7.2-30, R7.3-06b, R7.3-19, R6-12b | at the floor | inside the floor |
| R7.3-05a/15 | three times the floor | about twice the floor |
| Lesson (i), verifier-date caveat | cross-date drift unmeasured | measured on TM: contrast moves 0.001 to 0.002 |

**What did NOT change**: every verdict of a claim that cleared its floor;
every within-execution floor; the gold-standard sections. Commit: see git
log for this entry's date.

### 2026-10-06 (later) — § 3's first reading corrected

The first bullet under § 3 said consensus "does not shrink" the floor. The
table beneath it shows a modest shrink at the 4-of-5 threshold the boards
mostly use and a widening only at unanimity; the bullet now says so.

| | Before | After |
|---|---|---|
| § 3 headline | "Consensus does not shrink the floor" | shrinks it by about a third at t = 4 (0.021–0.024 against 0.030–0.034), widens it at unanimity |

**What did NOT change**: every number in every table, the D46 floors listed
at the end of § 3, and every verdict in § 7 (the § 7 screens use the
measured floor at each claim's own operating point). Commit: see git log
for this entry's date.

### 2026-10-06 — Original publication (Session 162)

Written for tracker items W2.7 and W7.6 (1) to (3) under rulings D45 to
D47. Scripts and raw outputs in
`reports/w27-replicate-floors-2026-10-06-scripts/` (gates `gates.json`,
`gs_gates.json`; pairs `subset_pairs.csv`, `gs_consensus_pairs.csv`; the
claims inventory `claims-inventory-2026-10-06.md` and the drift timeline
`w76-drift-timeline.md` are agent records, read-only, with every figure
used in § 7 re-read from the boards and the register). Compute on sapphire
(the 55-map run about 25 minutes on 16 workers; the gold-standard run 7.5
minutes on 20). No API call.
