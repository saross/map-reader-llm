# Leaderboard — 50m buffer

**Generated**: 2026-04-17T03:51:29.400397+00:00
**Conditions**: 20 in 7 tier(s)
**Updated**: 2026-04-24 — gold-standard-v2 scope-unified to Era 2 (487-tile)
inserted at F1 rank. Existing rows and their pairwise tier assignments are
unchanged; earlier tiers are renumbered to accommodate the new solitary Tier 1.

## Tier 1 (F1: 0.873–0.873)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 1 | gold-standard-v2-greedy-v1-487 | 2 | text | 5 | 4 | 0.873 | n/a[^gs2ci] | 0.949 | 0.809 |

[^gs2ci]: Bootstrap CI not emitted by `score_leaderboard_cells.py` for the
    gold-standard-v2 Era 2 cell; see the Q1 Era 2 sweep for CIs at the same
    scope. The Era 3 (327-tile) scope-pair sibling
    (`results/leaderboard/cells/gold-standard-v2-greedy-v1-327tile.json`) is
    intentionally preserved for comparability with the Era 3 h8-v2 / h10-v2 /
    h12-v2 library-design artefacts.

## Tier 2 (F1: 0.826–0.854)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 2 | h11-pvd-pro-high-text-n5 | 2 | text | 10 | 6 | 0.854 | [0.817, 0.885] | 0.947 | 0.777 |
| 3 | h11-pvd-flash-high-text-n5 | 2 | text | 30 | 26 | 0.826 | [0.793, 0.858] | 0.846 | 0.807 |

## Tier 3 (F1: 0.730–0.865)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 4 | h11-pvd-flash-high-image-n5 | 2 | image | 10 | 7 | 0.824 | [0.788, 0.857] | 0.854 | 0.795 |
| 5 | scale4-optimal-487 | 2 | image | 10 | 6 | 0.831 | [0.796, 0.861] | 0.864 | 0.800 |
| 6 | p3a-high-image-t1.0 | 2 | image | 10 | 6 | 0.818 | [0.784, 0.849] | 0.820 | 0.816 |
| 7 | p3a-high-image-t0.3 | 2 | image | 10 | 9 | 0.794 | [0.758, 0.829] | 0.875 | 0.726 |
| 8 | h11-e47-propose-brief | 2 | text | 5 | 5 | 0.730 | [0.683, 0.772] | 0.709 | 0.752 |
| 9 | h11-pvd-pro-high-image-n5 | 2 | image | 5 | 3 | 0.865 | [0.839, 0.893] | 0.832 | 0.901 |

## Tier 4 (F1: 0.669–0.752)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 10 | h11-pvd-image-n5 | 2 | image | 10 | 8 | 0.747 | [0.706, 0.784] | 0.702 | 0.798 |
| 11 | h11-n1-image-t03 | 2 | image | 3 | 3 | 0.752 | [0.715, 0.788] | 0.665 | 0.867 |
| 12 | h11-pvd-flash-minimal-text-n30-t07 | 2 | text | 30 | 29 | 0.669 | [0.621, 0.715] | 0.609 | 0.743 |
| 13 | p3a-min-image-t0.3 | 2 | image | 10 | 10 | 0.719 | [0.674, 0.759] | 0.661 | 0.786 |
| 14 | p3a-min-image-t1.0 | 2 | image | 10 | 8 | 0.735 | [0.696, 0.770] | 0.710 | 0.761 |

## Tier 5 (F1: 0.605–0.719)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 15 | h11-n1-image-t0 | 2 | image | 3 | 2 | 0.719 | [0.678, 0.754] | 0.589 | 0.922 |
| 16 | h11-pvd-text-n10 | 2 | text | 10 | 10 | 0.628 | [0.573, 0.681] | 0.536 | 0.759 |
| 17 | h11-n1-brief-text-t03 | 2 | text | 3 | 3 | 0.605 | [0.545, 0.660] | 0.469 | 0.855 |

## Tier 6 (F1: 0.603–0.660)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 18 | h11-n1-pro-text-high-t0 | 2 | text | 3 | 3 | 0.603 | [0.548, 0.655] | 0.469 | 0.844 |
| 19 | h11-n1-pro-image-high-t0 | 2 | image | 3 | 3 | 0.660 | [0.609, 0.703] | 0.568 | 0.788 |

## Tier 7 (F1: 0.593–0.593)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 20 | p3a-high-image-t0.0 | 2 | image | 3 | 1 | 0.593 | [0.546, 0.645] | 0.458 | 0.844 |
