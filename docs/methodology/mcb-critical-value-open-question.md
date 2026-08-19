# Open methodological question: the MCB critical value

> **Last revised**: 2026-08-19 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Status: OPEN.** Recorded as defect **D24**. This is a self-contained brief for
a statistician; it assumes no knowledge of the wider study.

## The one-paragraph version

We report, for each of fourteen leaderboards, the set of configurations that
cannot be ruled out as the best — Hsu's multiple comparisons with the best (MCB).
Hsu's critical value comes from a one-sided Dunnett distribution, which assumes
normal, homoscedastic, independent group means. Our statistics are micro-F1 and a
tile-level Matthews correlation coefficient computed over the *same* spatial
units for every configuration, so they are neither normal nor independent across
groups. We therefore substituted a tile-level bootstrap analogue of the critical
value. **We would like that substitution checked**: does it attain nominal
simultaneous coverage, and if not, in which direction does it fail?

## The setting

A **board** is *k* configurations of a detection pipeline, each scored on the
*same* set of *n* map tiles. Per configuration and tile we hold integer counts of
true positives, false positives, and false negatives, from which micro-F1 over any
subset of tiles is a deterministic function; tile-level MCC comes from a 2 × 2
table of the same tiles.

| | Range across the fourteen boards |
|---|---|
| Configurations *k* | 5 to 82 |
| Tiles *n* | 327 to 8,541 |
| Statistic | micro-F1 (10 boards) or tile MCC (4 boards) |
| Resampling unit | the tile, fixed by the study's pre-registration |

Two features matter and both push against the textbook setting.

**The groups are strongly dependent.** Every configuration is scored on the same
tiles, and many differ only in a threshold, so their per-tile counts are highly
correlated. We resample tiles, applying one resampled index set to all *k*
configurations simultaneously, which preserves that dependence — but it is
dependence Dunnett's tabulated value does not contemplate.

**The statistic is a ratio of sums, not a mean.** Micro-F1 is
`2TP / (2TP + FP + FN)` over the resampled tiles, so it is neither a sample mean
nor asymptotically normal at small effective sample sizes. Tile MCC is worse: it
is a correlation coefficient on a 2 × 2 table, and it is **undefined** whenever a
row or column marginal vanishes, which happens in real resamples.

## What we implemented

For configuration *i*, Hsu's quantity is

```text
theta_i = stat_i − max_{j != i} stat_j
```

so `theta_i > 0` only for the empirical winner. Writing `theta_hat` for the
value on the full data and `theta_b` for resample *b* of *B* = 10,000:

```text
w_upper = 95th percentile of  max_i ( theta_b,i − theta_hat_i )
```

and configuration *i* is declared **admissible** — not ruled out as best — when

```text
theta_hat_i + w_upper > 0
```

Bounds are truncated at zero in Hsu's manner, since no configuration can exceed
the best by construction. Undefined MCC values stay `NaN` and are excluded from
both the argmax and the quantiles rather than imputed.

The intent is that `w_upper` plays the role of Dunnett's critical value scaled by
the standard error, estimated non-parametrically from the same dependence
structure the data carry.

## The questions

1. **Coverage.** Does `theta_hat_i + w_upper > 0` attain 95 % simultaneous
   coverage of the true admissible set under this dependence, or does the
   percentile substitution mis-calibrate? A studentised or double bootstrap would
   be the obvious alternative; is either warranted here?
2. **Direction of failure.** If coverage is wrong, is it conservative or
   anti-conservative? Conservative would be tolerable — we would over-admit and
   under-claim. Anti-conservative would mean published tie sets are too small.
3. **The argmax inside the statistic.** `theta` is defined through a maximum over
   the other configurations, so it is a non-smooth functional and the ordinary
   *n*-out-of-*n* bootstrap is known to be delicate at ties. Ties are our common
   case — the largest admissible set is 15 of 36. We measured argmax stability
   per board (0.545 to 1.000) and ran *m*-out-of-*n* subsampling as a sensitivity
   check, but did not use it for the published values. Should we?
4. **The MCC boards specifically.** Is a bootstrap MCB defensible at all for a
   statistic that is undefined on a non-trivial fraction of resamples, given we
   exclude rather than impute those?

## What we measured, in case it helps

`w_upper` against the two-sided max-|deviation| band we first used, which is the
same decision rule with a wider critical value. The Hsu value is smaller
everywhere, as theory predicts, and the admissible set correspondingly tighter.

| Board | Statistic | *k* | *n* | `w_upper` | two-sided | Admissible |
|---|---|---:|---:|---:|---:|---:|
| `era1-leaderboard` | F1 | 82 | 340 | 0.0582 | 0.0689 | 10 |
| `era1-single-pass-baseline-matrix` | F1 | 36 | 340 | 0.0435 | 0.0608 | 15 |
| `diversity-dividend-384` | F1 | 22 | 487 | 0.0523 | 0.0651 | 3 |
| `n1-baseline-matrix-384` | F1 | 18 | 487 | 0.0599 | 0.0640 | 4 |
| `min-vs-high-thinking-pv` | F1 | 7 | 487 | 0.0234 | 0.0292 | 5 |
| `pass-budget-pareto-v2` | F1 | 7 | 487 | 0.0229 | 0.0285 | 6 |
| `h12-v2-hp-hn-ratio` | F1 | 6 | 327 | 0.0415 | 0.0574 | 6 |
| `verifier-robustness-matrix` | F1 | 6 | 487 | 0.0091 | 0.0141 | 5 |
| `flash35-model-roles` | F1 | 5 | 487 | 0.0401 | 0.0496 | 3 |
| `pass-budget-pareto` | F1 | 5 | 487 | 0.0206 | 0.0249 | 3 |
| `55map-standardised-leaderboard-50m` | F1 | 8 | 8,541 | 0.0088 | 0.0115 | 2 |
| `55map-canonical-leaderboard-50m` | F1 | 8 | 8,541 | 0.0099 | 0.0114 | 2 |
| `55map-standardised-leaderboard-mcc-50m` | MCC | 8 | 8,541 | 0.0161 | 0.0178 | 1 |
| `55map-canonical-leaderboard-mcc-50m` | MCC | 8 | 8,541 | 0.0161 | 0.0177 | 1 |

The two-sided band is strictly more conservative and brackets the Hsu result from
above, so if the bootstrap substitution turns out anti-conservative, the band
gives a fallback that is wrong in the safe direction.

## What is at stake

The MCB set replaced a sequential greedy-clique tiering rule that was
order-dependent and demonstrably wrong on at least one board (defect **D20**,
disclosed as erratum **E83**): it published a *sole* best configuration where the
board's own pairwise tests could not separate the leader from five others. MCB is
a better instrument on any reading, and the substantive conclusions of the study
do not turn on it — no registered hypothesis is stated in terms of tie-set
membership. What turns on it is how wide the published "indistinguishable from
best" sets are, which is a claim the paper makes fourteen times.

Ten of the fourteen boards changed membership under MCB; four returned exactly
what was published.

## What we can provide

- Per-tile TP/FP/FN arrays for every configuration on every board, as committed
  artefacts.
- The implementation: `scripts/selection_aware_intervals.py`, ~200 lines, no
  dependencies beyond NumPy and GeoPandas.
- Per-board results including the full bootstrap diagnostics: `theta` per
  configuration, both critical values, argmax stability, and the *m*-out-of-*n*
  sensitivity, under `results/selection-aware/`.
- A reproduction path: every board re-scores from committed detections and
  reproduces its published F1 to within 0.0005.

## See also

- `results/selection-aware/findings.md` — the measured results and the
  selection-optimism analysis this came from
- `docs/methodology/inference-instrument-policy.md` — which instrument licenses
  which claim in this study
- Erratum E83; defects D20 (the rule replaced) and D24 (this question)
- Hsu (1984), *Annals of Statistics* 12(3), 1136–1144; Edwards & Hsu (1983),
  *JASA* 78, 965–971

## Changelog

### 2026-08-19 — Original publication

Written when the MCB instrument was adopted across fourteen boards under erratum
E83, so that the one unverified step — a bootstrap critical value standing in for
Dunnett's tabulated one — is stated precisely enough for an external statistician
to act on without reading the project.
