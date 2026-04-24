# Leaderboard — 30m buffer

**Generated**: 2026-04-17T03:51:29.400204+00:00
**Conditions**: 20 in 7 tier(s)
**Updated**: 2026-04-24 — gold-standard-v2 scope-unified to Era 2 (487-tile)
inserted at F1 rank. Existing rows and their pairwise tier assignments are
unchanged; earlier tiers are renumbered to accommodate the new solitary Tier 1.

## Tier 1 (F1: 0.871–0.871)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 1 | gold-standard-v2-greedy-v1-487 | 2 | text | 5 | 4 | 0.871 | n/a[^gs2ci] | 0.946 | 0.807 |

[^gs2ci]: Bootstrap CI not emitted by `score_leaderboard_cells.py` for the
    gold-standard-v2 Era 2 cell; see the Q1 Era 2 sweep for CIs at the same
    scope. The Era 3 (327-tile) scope-pair sibling
    (`results/leaderboard/cells/gold-standard-v2-greedy-v1-327tile.json`) is
    intentionally preserved for comparability with the Era 3 h8-v2 / h10-v2 /
    h12-v2 library-design artefacts.

## Tier 2 (F1: 0.826–0.851)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 2 | h11-pvd-pro-high-text-n5 | 2 | text | 10 | 6 | 0.851 | [0.813, 0.883] | 0.944 | 0.775 |
| 3 | h11-pvd-flash-high-text-n5 | 2 | text | 30 | 26 | 0.826 | [0.793, 0.858] | 0.846 | 0.807 |

## Tier 3 (F1: 0.730–0.821)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 4 | h11-pvd-flash-high-image-n5 | 2 | image | 10 | 7 | 0.809 | [0.773, 0.843] | 0.840 | 0.782 |
| 5 | scale4-optimal-487 | 2 | image | 10 | 6 | 0.804 | [0.766, 0.838] | 0.836 | 0.775 |
| 6 | p3a-high-image-t1.0 | 2 | image | 10 | 6 | 0.788 | [0.751, 0.822] | 0.790 | 0.786 |
| 7 | p3a-high-image-t0.3 | 2 | image | 10 | 9 | 0.784 | [0.748, 0.818] | 0.864 | 0.717 |
| 8 | h11-e47-propose-brief | 2 | text | 5 | 5 | 0.730 | [0.683, 0.772] | 0.709 | 0.752 |
| 9 | h11-pvd-pro-high-image-n5 | 2 | image | 5 | 3 | 0.821 | [0.787, 0.851] | 0.790 | 0.855 |

## Tier 4 (F1: 0.669–0.737)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 10 | h11-pvd-image-n5 | 2 | image | 10 | 8 | 0.728 | [0.685, 0.765] | 0.684 | 0.777 |
| 11 | h11-n1-image-t03 | 2 | image | 3 | 3 | 0.737 | [0.696, 0.774] | 0.651 | 0.848 |
| 12 | h11-pvd-flash-minimal-text-n30-t07 | 2 | text | 30 | 29 | 0.669 | [0.621, 0.715] | 0.609 | 0.743 |
| 13 | p3a-min-image-t0.3 | 2 | image | 10 | 10 | 0.710 | [0.667, 0.751] | 0.654 | 0.777 |
| 14 | p3a-min-image-t1.0 | 2 | image | 10 | 8 | 0.715 | [0.674, 0.751] | 0.691 | 0.740 |

## Tier 5 (F1: 0.601–0.692)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 15 | h11-n1-image-t0 | 2 | image | 3 | 2 | 0.692 | [0.650, 0.728] | 0.567 | 0.887 |
| 16 | h11-pvd-text-n10 | 2 | text | 10 | 10 | 0.628 | [0.573, 0.681] | 0.536 | 0.759 |
| 17 | h11-n1-brief-text-t03 | 2 | text | 3 | 3 | 0.601 | [0.542, 0.655] | 0.465 | 0.848 |

## Tier 6 (F1: 0.593–0.618)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 18 | h11-n1-pro-text-high-t0 | 2 | text | 3 | 3 | 0.593 | [0.539, 0.644] | 0.461 | 0.830 |
| 19 | h11-n1-pro-image-high-t0 | 2 | image | 3 | 3 | 0.618 | [0.569, 0.665] | 0.531 | 0.738 |

## Tier 7 (F1: 0.550–0.550)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 20 | p3a-high-image-t0.0 | 2 | image | 3 | 1 | 0.550 | [0.497, 0.602] | 0.424 | 0.782 |
