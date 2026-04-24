# Leaderboard — 20m buffer

**Generated**: 2026-04-17T03:51:29.400040+00:00
**Conditions**: 20 in 7 tier(s)
**Updated**: 2026-04-24 — gold-standard-v2 scope-unified to Era 2 (487-tile)
inserted at F1 rank. Existing rows and their pairwise tier assignments are
unchanged; earlier tiers are renumbered to accommodate the new solitary Tier 1.

## Tier 1 (F1: 0.854–0.854)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 1 | gold-standard-v2-greedy-v1-487 | 2 | text | 5 | 4 | 0.854 | n/a[^gs2ci] | 0.927 | 0.791 |

[^gs2ci]: Bootstrap CI not emitted by `score_leaderboard_cells.py` for the
    gold-standard-v2 Era 2 cell; see the Q1 Era 2 sweep for CIs at the same
    scope. The Era 3 (327-tile) scope-pair sibling
    (`results/leaderboard/cells/gold-standard-v2-greedy-v1-327tile.json`) is
    intentionally preserved for comparability with the Era 3 h8-v2 / h10-v2 /
    h12-v2 library-design artefacts.

## Tier 2 (F1: 0.814–0.836)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 2 | h11-pvd-pro-high-text-n5 | 2 | text | 10 | 6 | 0.836 | [0.797, 0.872] | 0.927 | 0.761 |
| 3 | h11-pvd-flash-high-text-n5 | 2 | text | 30 | 26 | 0.814 | [0.778, 0.846] | 0.834 | 0.795 |

## Tier 3 (F1: 0.700–0.750)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 4 | h11-pvd-flash-high-image-n5 | 2 | image | 10 | 7 | 0.750 | [0.707, 0.790] | 0.778 | 0.724 |
| 5 | scale4-optimal-487 | 2 | image | 10 | 6 | 0.742 | [0.699, 0.783] | 0.772 | 0.715 |
| 6 | p3a-high-image-t1.0 | 2 | image | 10 | 6 | 0.735 | [0.692, 0.776] | 0.737 | 0.733 |
| 7 | p3a-high-image-t0.3 | 2 | image | 10 | 9 | 0.731 | [0.690, 0.772] | 0.806 | 0.669 |
| 8 | h11-e47-propose-brief | 2 | text | 5 | 5 | 0.714 | [0.666, 0.760] | 0.694 | 0.736 |
| 9 | h11-pvd-pro-high-image-n5 | 2 | image | 5 | 3 | 0.700 | [0.653, 0.741] | 0.673 | 0.729 |

## Tier 4 (F1: 0.646–0.680)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 10 | h11-pvd-image-n5 | 2 | image | 10 | 8 | 0.680 | [0.634, 0.723] | 0.640 | 0.726 |
| 11 | h11-n1-image-t03 | 2 | image | 3 | 3 | 0.677 | [0.633, 0.718] | 0.598 | 0.779 |
| 12 | h11-pvd-flash-minimal-text-n30-t07 | 2 | text | 30 | 29 | 0.661 | [0.610, 0.706] | 0.602 | 0.733 |
| 13 | p3a-min-image-t0.3 | 2 | image | 10 | 10 | 0.660 | [0.612, 0.703] | 0.607 | 0.722 |
| 14 | p3a-min-image-t1.0 | 2 | image | 10 | 8 | 0.646 | [0.599, 0.688] | 0.625 | 0.669 |

## Tier 5 (F1: 0.591–0.629)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 15 | h11-n1-image-t0 | 2 | image | 3 | 2 | 0.629 | [0.582, 0.668] | 0.515 | 0.807 |
| 16 | h11-pvd-text-n10 | 2 | text | 10 | 10 | 0.619 | [0.561, 0.673] | 0.528 | 0.747 |
| 17 | h11-n1-brief-text-t03 | 2 | text | 3 | 3 | 0.591 | [0.535, 0.646] | 0.457 | 0.835 |

## Tier 6 (F1: 0.552–0.567)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 18 | h11-n1-pro-text-high-t0 | 2 | text | 3 | 3 | 0.567 | [0.512, 0.617] | 0.441 | 0.793 |
| 19 | h11-n1-pro-image-high-t0 | 2 | image | 3 | 3 | 0.552 | [0.506, 0.599] | 0.475 | 0.660 |

## Tier 7 (F1: 0.488–0.488)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 20 | p3a-high-image-t0.0 | 2 | image | 3 | 1 | 0.488 | [0.438, 0.539] | 0.377 | 0.694 |
