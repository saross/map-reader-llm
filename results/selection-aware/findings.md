# Selection-aware uncertainty: pilot on the tile-size × overlap grid

> **Last revised**: 2026-08-19 (original publication). See
> [§ Changelog](#changelog) for revision history.

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

## Recommendation

1. Report the **MCB admissible set** wherever the paper currently reports a best
   operating point, and state the corroboration-versus-threshold asymmetry
   directly.
2. Report the **corrected point estimate** with the optimism beside it. In this
   grid the correction is ≤ 0.004 F1 and can be stated as negligible, but it
   should be stated, not omitted.
3. Do **not** apply either instrument to fixed-operating-point contrasts.
4. Extend to the flat-plateau selections next — the Era-1 single-pass board
   carries a 20-of-36 tie set and is where MCB should bite hardest, and E56's
   verifier threshold curve is flat by measurement. The grid was the stable case;
   these are not.

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

### 2026-08-19 — Original publication

Pilot across all four grid cells at B = 10 000, plus an *m*-out-of-*n*
sensitivity on the least stable cell. Establishes that selection optimism in the
grid is ≤ 0.004 F1 and tracks argmax stability, that this is an order of
magnitude below the nearest published analogue because the candidate set is
nested rather than independent, and that the substantive change comes from MCB:
4–10 of 30 candidates per cell cannot be ruled out as best, with corroboration
resolved and vote threshold not. Written after a `/review-implementation` pass
that rejected the originally proposed single-instrument approach.
