# Tile-level MCC: what it measures, and the three things that mislead

> **Last revised**: 2026-08-19 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Why this exists.** Working on this study's own data, with the code in front of
me, I derived tile-level MCC wrongly on the first attempt and got a plausible
number — 0.898 where the committed value is 0.790. The error was silent: the
confusion matrix looked reasonable and only a direct comparison against a
committed block exposed it. A reviewer, a reuser, or a future maintainer will hit
the same three traps. This note removes the need to rediscover them.

## What the metric is

Registered § 4.2 defines tile-level discrimination. Every evaluation tile is
classified once, as a **binary** outcome, independently of how many mounds it
holds:

| | Reference has ≥ 1 mound | Reference empty |
|---|---|---|
| **Model detected ≥ 1** | TP | FP |
| **Model detected nothing** | FN | TN |

MCC is then the Matthews correlation of that 2 × 2 table:

```text
MCC = (TP·TN − FP·FN) / √((TP+FP)(TP+FN)(TN+FP)(TN+FN))
```

Canonical implementation: `lib_advanced_metrics.calculate_tile_classification`.

**It is a different question from F1.** F1 asks "of the mounds, how many did you
find, and how many things you flagged were mounds?" — counted per *detection*.
Tile MCC asks "can you tell a populated map region from an empty one?" — counted
per *tile*. A configuration can be good at one and poor at the other, and in this
study several are. That is a finding, not an inconsistency.

## Trap 1: the two axes book features to tiles by *different rules*

This is the one that produced my wrong number, and it is not documented anywhere
else in the project.

- **Detections** are booked to **one** tile: the E79 rule, the tile whose centroid
  is nearest among those the detection intersects. One detection, one tile.
- **References** are booked by **intersection**: a mound counts for *every* tile
  it intersects. With overlapping tilings, one mound can make several tiles
  reference-populated.

So a tile's reference occupancy cannot be recovered from the detection-level
per-tile false-negative column, which is what I assumed. Doing that on a real cell
gives TP/TN/FP/FN = 185/278/14/10 where the truth is **188/247/11/41** — the
predicted-positive total is right (199 either way) and the reference side is
wrong. MCC comes out 0.898 against a true 0.790.

**Rule**: derive `has_detections` from the detection booking if you like
(`(tp + fp) > 0` is correct), but derive `has_mounds` **only** by intersecting
references against tile geometry.

## Trap 2: an undefined MCC is not a zero

If any row or column marginal of the 2 × 2 table is zero the denominator
vanishes and MCC is **undefined**. It is not 0, and 0 is not a neutral filler:
registered § 4.2 supplies the legend "0 (random)", so publishing a zero says the
model discriminates at chance when the truth is that the question was not
answerable.

This bit the study. Erratum **E81** records nine conditions published at `0.0`
that were all undefined, plus four more depressed by averaging an undefined pass
into a mean. The corpus contains **35** degenerate per-pass blocks, and in every
one the vanishing marginal is the same: `TN + FN = 0`, because the model returned
at least one detection on every tile in scope, emptying the predicted-negative
column.

**Rule**: undefined MCC is `null`, never `0.0`, and carries
`mcc_undefined_reason` naming the vanishing marginal. Thirteen conditions are
affected; they are excluded from MCC boards rather than imputed.

## Trap 3: the number depends on the tiling, so it is not comparable across scopes

MCC's classification units *are* the carrier tiles. Change the tile size, the
overlap, or the evaluation footprint and you change the denominator of the
metric itself — more, smaller tiles make the empty class larger and inflate TN.
Two MCC values computed on different tilings are not comparable even when they
score the same detections against the same references.

**Rule**: state the carrier with any tile MCC — tile size, overlap, footprint,
and tile count. Where two configurations are compared on MCC, they must sit on
one carrier grid.

## Reading an MCC alongside an F1

Both are reported wherever inputs support it, by standing preference. When they
disagree, the disagreement is informative:

- **High F1, low or undefined MCC** — the model finds mounds but flags almost
  every tile, so it cannot separate populated from empty. Typical of the
  permissive text single-pass configurations.
- **Lower F1, higher MCC** — fewer or less precisely placed detections, but
  placed in the right regions. Typical of several image-track configurations.

Neither dominates. Which matters depends on the deployment question: locating
individual mounds, or triaging which sheets and regions deserve attention.

## Where the numbers live

| Artefact | Field |
|---|---|
| `evaluation.json` | `summary.tile_classification.mcc` (`point`, `mean`, `ci_lower`, `ci_upper`, `n_runs`, `n_runs_defined`) and `.confusion` |
| `results/conditions-manifest.json` | `metrics.tile_classification.mcc`, with `mcc_undefined_reason` where null |
| Leaderboards | `results/leaderboard/**/leaderboard_tiers_mcc.md` |

`mcc.point` is the all-data estimate. `mcc.mean` is the mean of the bootstrap
distribution and differs slightly; boards read `mean`, and the divergence is
below 0.0025 wherever it has been measured.

## See also

- `docs/methodology/inference-instrument-policy.md` (which instrument licenses
  which claim, and the sparse-coverage rule)
- Errata E81 (undefined MCC published as zero), E79 (detection tile assignment),
  E83 (tie sets, where MCC boards are re-tiered)
- `scripts/selection_aware_intervals.py` (`mcc_from_indicators`, which implements
  the rules above and is verified against a committed block before use)

## Changelog

### 2026-08-19 — Original publication

Written after deriving tile MCC incorrectly while extending the selection-aware
interval work to MCC-tiered boards: reference occupancy was taken from the
detection-level false-negative column rather than by intersection, giving 0.898
against a committed 0.790. The error was silent and the wrong confusion matrix
looked plausible, so the trap is documented rather than left for the next reader.
