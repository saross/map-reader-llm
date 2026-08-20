# Selection-aware uncertainty: pilot on the tile-size × overlap grid

> **Last revised**: 2026-08-20 (audit remediation: `n1-baseline-matrix-384`
> re-tiered at the standard B = 10,000 — admissible set 3, not 4; overrides now
> recorded in artefacts). See [§ Changelog](#changelog) for revision history.

**Classification**: POST-HOC (E41-class), a methodological re-analysis of
committed detections. Not a registered test.

## Why

Every "best cell" figure in this study is an argmax over a candidate sweep scored
on the evaluation set itself, so the reported maximum has been chosen partly for
its noise. Erratum E56 documents this for verifier probability thresholds; it is
general. An ordinary confidence interval on the winner describes the wrong
quantity, because it treats the winner as though it were the only configuration
ever scored.

Two instruments were implemented, because the study makes two kinds of claim:
**MCB** (multiple comparisons with the best) for "which configurations cannot be
ruled out as best", and a **selection-aware bootstrap** (Efron–Gong optimism with
the argmax replayed inside each resample) for the de-biased point estimate. Both
resample tiles, the unit Decision 10 registers, and both resample the *same*
tiles for every candidate so the strong correlation between neighbouring
operating points is preserved.

**Scope, deliberately narrow.** This applies only where an argmax was taken over
candidates scored on the evaluation data. It is **not** applied to the grid's
overlap, tile-size, or interaction contrasts: `grid_analysis.build_per_tile`
computes those on run-averaged single-pass counts with no consensus filter and no
selection, so they are already selection-free and correcting them would introduce
a bias rather than remove one.

## Headline: the winner's curse is negligible here, and MCB is what changes

| Cell | Selected | Apparent F1 | Optimism | Corrected | argmax stability | MCB set |
|---|---|---:|---:|---:|---:|---:|
| 512 px / 50 % | c ≥ 2, k ≥ 8 | 0.7518 | **+0.0016** | 0.7501 | 0.891 | 9 / 30 |
| 512 px / 12.5 % | c ≥ 1, k ≥ 8 | 0.6759 | **+0.0041** | 0.6718 | 0.704 | 7 / 30 |
| 384 px / 50 % | c ≥ 2, k ≥ 10 | 0.7205 | **+0.0011** | 0.7194 | 0.947 | 10 / 30 |
| 384 px / 12.5 % | c ≥ 1, k ≥ 10 | 0.6475 | **−0.0008** | 0.6483 | 1.000 | 4 / 30 |

B = 10 000 tile resamples, seed 42, 20 m buffer, 487 carrier tiles. Monte Carlo
standard error on every optimism estimate is ≤ 0.00026.

**Optimism is at most 0.004 F1**, against main effects of 0.08–0.13. It is
too small to move any conclusion in the grid, and the selection-aware interval is
visually indistinguishable from the naive one (512 px / 50 %: [0.7037, 0.7946]
naive against [0.7020, 0.7930] corrected).

**This was not the expected result and is flagged as a surprise.** The nearest
published analogue, SIREN on adaptive LLM benchmarking
([arXiv 2605.05973](https://arxiv.org/html/2605.05973)), measures naive-winner
optimism at +0.42 to +3.70 percentage points and reports that it sometimes
reverses near-tie deployment decisions. Ours is an order of magnitude smaller.
The mechanism is visible in the table: **optimism tracks argmax instability
almost perfectly**, from −0.0008 at stability 1.000 to +0.0041 at stability
0.704. SIREN's candidates come from random search over prompts and are close to
independent; ours are a nested sweep over corroboration and vote threshold on a
smooth two-dimensional surface, so 30 nominal candidates behave like a handful of
effective ones and there is little selection noise to be optimistic about. The
correction is small **because the candidate set is correlated**, not because
selection is harmless in general.

## What MCB changes, which is the substantive finding

MCB returns the candidates that cannot be ruled out as best at simultaneous 95 %
confidence. Those sets are wide, and structured:

| Cell | Cannot be ruled out as best |
|---|---|
| 512 px / 50 % | c ≥ 2 with **k = 2…10** (all nine) |
| 384 px / 50 % | c ≥ 2 with k = 7…10, **and** c ≥ 3 with k = 4…9 |
| 512 px / 12.5 % | c ≥ 1 with **k = 4…10** |
| 384 px / 12.5 % | c ≥ 1 with k = 7…10 |

Read across the rows, the pattern is consistent and useful: **the corroboration
level is what the data resolve, and the consensus vote threshold is not.** At
50 % overlap the admissible sets sit at c ≥ 2 (and, at 384 px, c ≥ 3); at 12.5 %
overlap corroboration is unavailable and every admissible cell is c ≥ 1. Within a
corroboration level the vote threshold ranges freely over most of its span
without the data distinguishing the resulting cells.

The deployment claim therefore changes shape. "The best operating point is
c ≥ 2, k ≥ 8, F1 0.7518" overstates what was measured. What the grid supports is
**"require cross-tile corroboration; the vote threshold is not resolvable at this
sample size"** — which is both weaker and more actionable, because it says the
tuning effort should go into the corroboration filter rather than the threshold.

This also formalises something the project already does by hand. Fourteen of the
37 register rows declare a tie set, currently derived from pairwise permutation
plus BH-FDR plus a greedy clique. MCB is the canonical instrument for exactly
that object and is simultaneous by construction rather than by correction
([Hsu 1984](https://projecteuclid.org/journals/annals-of-statistics/volume-12/issue-3/Constrained-Simultaneous-Confidence-Intervals-for-Multiple-Comparisons-with-the-Best/10.1214/aos/1176346732.full)).

## The tie caveat, measured rather than assumed

Both source methods warn that the ordinary *n*-out-of-*n* bootstrap of an argmax
is delicate when candidates are tied, and this study's selections sit in flat
regions by design. Subsampling the least stable cell:

| *m* / *n* | argmax stability | Optimism | MCB set | MCB critical width |
|---:|---:|---:|---:|---:|
| 1.00 | 0.704 | +0.0041 | 7 / 30 | 0.0756 |
| 0.50 | 0.549 | +0.0096 | 8 / 30 | 0.1064 |
| 0.25 | 0.414 | +0.0183 | 8 / 30 | 0.1499 |

Optimism grows as *m* shrinks, and grows **faster than the 1/√*m*** that a
simple scaling argument predicts (a 4× reduction in *m* inflates it 4.5×, not
2×). This is the delicacy the literature warns about, and it has a practical
consequence: the *m*-out-of-*n* figures must **not** be read as better estimates
of the optimism in the published number. They estimate the optimism you would
suffer selecting on 122 or 243 tiles. The *n*-out-of-*n* value is the one that
answers "how optimistic is what we published"; the subsampling rows are a
sensitivity check, and they show the estimate is not stable under subsampling.

**MCB set membership is stable under the same subsampling** (7 → 8 → 8) even as
its critical width inflates with the smaller sample, which is a further argument
for treating MCB as the primary instrument and the optimism correction as
secondary.

## Extension to the registered boards, and what it found

The grid was the stable case. Applying the same two instruments to the
registered leaderboards, where argmax stability is lower by construction:

| Board | Cells | Selected | Apparent | Optimism | Corrected | Stability | MCB | Register `tie_set` |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| `era1-single-pass-baseline-matrix` | 36 | canonical-last | 0.6314 | **+0.0132** | 0.6183 | 0.646 | 23 | 20 |
| `era1-leaderboard` | 82 | verified-adv-text-high-t1.0-n30-23of30 | 0.7925 | +0.0067 | 0.7857 | 0.738 | **15** | **1** |
| `verifier-robustness-matrix` | 6 | verified-384-ge3of5-t0-3-high-n5 | 0.8764 | +0.0027 | 0.8737 | 0.545 | 5 | 5 |
| `pass-budget-pareto-v2` | 7 | verified-384-16of30-t0-3-n5-opmax | 0.8951 | +0.0050 | 0.8902 | 0.672 | 6 | 7 |
| `min-vs-high-thinking-pv` | 7 | verified-384-16of30-t0-3-n5-opmax | 0.8951 | +0.0048 | 0.8903 | 0.679 | 6 | 6 |

Optimism is larger here than in the grid, up to **+0.0132** on the single-pass
board, and again tracks argmax stability. It remains small in absolute terms. MCB
mostly agrees with the register's tie sets, is slightly wider on the single-pass
board (23 against 20, a strict superset adding three image cells just below the
published Tier-1 floor), and is slightly **tighter** on `pass-budget-pareto-v2`
(6 against 7), so it is not uniformly more conservative.

### The exception, which is a defect: `era1-leaderboard`

The register publishes a **sole** Tier-1 leader there, `tie_set` of one, with the
outcome reading "proposer-verifier is the single best Era-1 architecture ... clear
of the HIGH-consensus cluster (Tier 2)". MCB puts **15 of 82** cells in the
admissible set. That gap was large enough to be worth chasing to its cause, and
the cause is not a disagreement between methods.

`greedy_clique_tiers` walks conditions in F1-descending order and closes the
current tier at the **first** condition significant against any current member.
On this board the rank-2 cell is significant at **BH p = 0.048** — marginal — and
closes Tier 1 immediately. Five lower-ranked cells are non-significant against the
leader and, checked pairwise, mutually non-significant: **all 15 pairs within
{leader + those five} are non-significant**. The leader's true clique therefore has
**6** members, verified with zero violating pairs. The function's own docstring
promises that `tiers[0]` is "the leader's clique"; on this board it is not.

Three independent instruments agree the published claim is too strong, and they
bracket it: the artefact's own pairwise tests say at least 6, the true clique says
6, and MCB at simultaneous 95 % says 15.

`scripts/audit_tier1_cliques.py` checks every committed tiering artefact. **3 of
11 understate Tier 1, and all three are this board** (the main artefact and its two
dedup-impact variants). The other eight agree exactly, including the 36-cell board
whose Tier 1 of 20 reproduces its clique of 20. The defect fires only when a
marginal result sits at rank 2, which is why it went unnoticed.

Recorded as **D20**, left OPEN: the code fix is mechanical, but it changes a
published headline claim and the correction scope is a PI decision.

**Caveat on the MCB implementation, now partly discharged.** The first pass used
a two-sided band, an adaptation rather than Hsu's construction, and predicted it
would run conservative. Hsu's constrained one-sided form is now computed
alongside it and confirms that prediction — see
[§ Hsu's constrained construction](#hsus-constrained-construction-and-a-correction).
What remains unverified is the bootstrap critical value itself as a substitute
for Dunnett's tabulated one; the substitution is necessary here because the
normality and homoscedasticity Dunnett assumes do not hold for micro-F1 on
correlated tiles, but a statistician should check it before it carries a paper
claim.

## Hsu's constrained construction, and a correction

The first pass used a bootstrap **two-sided max-|deviation| band**, flagged at
the time as an adaptation that would run conservative. Hsu's published
construction is **one-sided and constrained**: the critical value comes from the
one-sided distribution of the largest deviation in the direction that decides
exclusion, and the bounds are truncated at zero because no candidate can beat the
best by construction. A candidate is ruled out only when its simultaneous upper
bound falls at or below zero. Both are now computed; the bootstrap replaces
Dunnett's tabulated critical value, which assumes normal homoscedastic means that
micro-F1 on correlated tiles does not satisfy.

Hsu's critical value is smaller in every candidate set tested, as expected, and
the admissible sets are correspondingly tighter:

| Candidate set | Cells | Two-sided band | **Hsu** | Register `tie_set` | Relation of Hsu to register |
|---|---:|---:|---:|---:|---|
| `era1-leaderboard` | 82 | 15 | **10** | **1** | strict superset — register **9 too few** |
| `era1-single-pass-baseline-matrix` | 36 | 23 | **15** | **20** | strict subset — register **5 too many** |
| `min-vs-high-thinking-pv` | 7 | 6 | 5 | 6 | **neither** — overlap only, +1 / −2 |
| `pass-budget-pareto-v2` | 7 | 6 | 6 | 7 | strict subset — register 1 too many |
| `verifier-robustness-matrix` | 6 | 5 | 5 | 5 | identical |
| E56 consensus-PV threshold | 8 | 5 | 5 | — | — |
| grid 512 / 50 % | 30 | 9 | 9 | — | — |
| grid 512 / 12.5 % | 30 | 7 | 7 | — | — |
| grid 384 / 50 % | 30 | 10 | 8 | — | — |
| grid 384 / 12.5 % | 30 | 4 | 4 | — | — |

**Correction.** The previous revision reported that MCB was a strict superset of
the register's tie set on `era1-single-pass-baseline-matrix` (23 against 20) and
concluded the register was anti-conservative there by three cells. Under Hsu's
construction the relation **reverses**: the admissible set is 15, a strict subset,
and the register's 20 is **five too many**. The earlier reading was an artefact of
the conservative two-sided band and should not be relied on.

**D20 is unaffected and strengthened.** On `era1-leaderboard` Hsu still gives 10
against the register's 1, so the sole-Tier-1-leader claim does not survive the
proper construction either. It never depended on MCB in any case: the clique
argument reaches six using only the artefact's own pairwise tests.

**The most important row is `min-vs-high-thinking-pv`**, where Hsu's set is
neither a subset nor a superset of the register's — it adds one condition and
drops two. The sequential tiering is therefore **not biased in a single
direction**: on these six candidate sets it runs too narrow once, too wide twice,
identical once, and simply *different* once. That rules out any correction by a
uniform adjustment, and is the strongest argument for replacing the instrument
rather than tuning it.

## Recommendation

1. Report the **MCB admissible set** wherever the paper currently reports a best
   operating point, and state the corroboration-versus-threshold asymmetry
   directly.
2. Report the **corrected point estimate** with the optimism beside it. In this
   grid the correction is ≤ 0.004 F1 and can be stated as negligible, but it
   should be stated, not omitted.
3. Do **not** apply either instrument to fixed-operating-point contrasts.
4. **Settle D20 before any board claim goes into the paper.** The
   `era1-leaderboard` headline is the one materially affected.
5. E56's verifier threshold curve has now been tested; see below.

## Reproducing

```bash
python scripts/selection_aware_intervals.py --cell g512_ov256 --K 10 \
    --bootstrap 10000 --out results/selection-aware/
```

Run on sapphire, $0 API. One JSON per cell under `results/selection-aware/`.

## See also

- `reports/bca-axis-defect-2026-08-18.md` and erratum E82 (the interval machinery)
- Erratum E56 (in-sample operating points, the problem this addresses)
- `results/grid-2026-08-18/findings.md` (the selection-free contrasts)

## Changelog

### 2026-08-20 — Session 137 audit remediation: artefact re-emissions

Trigger: the Session 137 audit (`reports/session-137-audit-report-2026-08-20.md`)
and erratum E83's 2026-08-20 correction block. Instrument fixes
(`scripts/selection_aware_intervals.py` now records `--ground-truth`/`--bounds`
overrides in its output and threads `--buffer` through the `--evals` path) and
re-emissions: `n1-baseline-matrix-384` was found to have been tiered at
**B = 200** — at the standard B = 10,000 its admissible set is **3, not 4**
(`w_upper` 0.0599 → 0.0571; the +0.0004 knife-edge cell is excluded at every
seed tested); the supplementary `verifier-robustness-matrix` MCC artefact
(B = 2,000) re-emitted at 10,000 with membership unchanged; all four 55-map
artefacts re-emitted with their mandatory ground-truth overrides recorded,
reproducing with zero change to any shared value; the two pre-Hsu m-out-of-n
artefacts re-emitted at the current code vintage (band values identical, Hsu
fields added, filenames now buffer-stamped) with the originals archived to
`archive/superseded-selection-aware/`. No claim in this document changes; the
m-out-of-n table below quotes the two-sided band, which is unchanged.

### 2026-08-19 (later) — Extended to five registered boards; D20 found

Applied both instruments to `era1-single-pass-baseline-matrix`,
`era1-leaderboard`, `verifier-robustness-matrix`, `pass-budget-pareto-v2`, and
`min-vs-high-thinking-pv`. Optimism rises to +0.0132 on the single-pass board and
still tracks argmax stability. MCB broadly corroborates the register's tie sets
except on `era1-leaderboard`, where chasing a 1-against-15 gap surfaced **D20**:
`greedy_clique_tiers` closes a tier at the first significant condition, so a
marginal BH p = 0.048 at rank 2 published a sole Tier-1 leader where the leader's
true clique has six members. 3 of 11 tiering artefacts affected, all this board.
Audit script `scripts/audit_tier1_cliques.py` added.

### 2026-08-19 — Original publication

Pilot across all four grid cells at B = 10 000, plus an *m*-out-of-*n*
sensitivity on the least stable cell. Establishes that selection optimism in the
grid is ≤ 0.004 F1 and tracks argmax stability, that this is an order of
magnitude below the nearest published analogue because the candidate set is
nested rather than independent, and that the substantive change comes from MCB:
4–10 of 30 candidates per cell cannot be ruled out as best, with corroboration
resolved and vote threshold not. Written after a `/review-implementation` pass
that rejected the originally proposed single-instrument approach.

## E56's threshold curve: flat does not mean unstable

The verifier probability-threshold sweep was expected to be the hard case,
because E56 records the curve as flat (≤ 0.022 F1 across the plateau) and
flatness was assumed to imply an unstable argmax. **It does not.** Across the
eight `consensus-PV-4of5` operating points, argmax stability is **0.906** and
optimism is **+0.0004** — the smallest of any candidate set tested.

The reason is that these candidates are the *same detection set* at different
probability thresholds, so they nest: a higher threshold's accepted set is a
subset of a lower one's. Under a tile resample the candidates move together
almost exactly, and it is the variance of the *differences*, not the size of the
differences, that determines whether the argmax moves. A flat curve made of
strongly nested candidates has a stable argmax; a flat curve made of independent
candidates would not.

Practically, this vindicates E56's reporting rule from a second direction. E56
argued the in-sample optimum and the fixed reference are interchangeable because
the curve is flat (0.15: 0.8641 against 0.20: 0.8610). The selection analysis
adds that the optimum is also barely optimistic, so quoting it costs almost
nothing. MCB puts **5 of 8** thresholds in the admissible set (0.15 through 0.40),
which is the honest statement of how well the threshold is resolved.
