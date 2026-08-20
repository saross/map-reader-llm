# Leaderboard — 40m buffer

**Generated**: 2026-04-17T03:51:29.400307+00:00
**Conditions**: 20 in 7 tier(s)
**Updated**: 2026-08-20 — gold-standard-v2 scope-unified to Era 2 (487-tile)
inserted at F1 rank, matching the 20 / 30 / 50 m siblings, which received the
same row on 2026-04-24 (commit `7ab7d7fa1`) while this board did not (defect
D34: four siblings disagreed, 20-in-7 / 20-in-7 / 19-in-6 / 20-in-7). Existing
rows and their pairwise tier assignments are unchanged; earlier tiers are
renumbered to accommodate the new solitary Tier 1. Values are the current
committed evaluation; the interval is BCa and post-E82-correction.
**Hand edit**: the `gold-standard-v2-greedy-v1-487` row is inserted by hand and
is not reproducible from this board's source `leaderboard_tiers_20m.json` —
regenerating this board would drop it. Declared `hand_edited: true` under rule
`gen-era2-lb-handedit-siblings` in
`reports/verification/apparatus/generator-map.json`.

## Tier 1 (F1: 0.883–0.883)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 1 | gold-standard-v2-greedy-v1-487 | 2 | text | 5 | 4 | 0.883 | [0.851, 0.909][^gs2ci] | 0.947 | 0.828 |

[^gs2ci]: Point estimates from
    `results/leaderboard/cells/gold-standard-v2-greedy-v1-487tile.json`
    (`sweep`, vote_t = 4, prob_t = 0.15, n = 380); 95% CI from
    `results/gold-standard-extended-buffer-sweep-era2/evaluation.json` (BCa,
    10,000 iterations, seed 42, re-emitted 2026-08-20 with the corrected —
    wider — intervals). This cell is scored outside
    `score_leaderboard_cells.py`, so its interval is not the 1,000-iteration
    bootstrap this board's generator computes for the other rows. The Era 3
    (327-tile) scope-pair sibling
    (`results/leaderboard/cells/gold-standard-v2-greedy-v1-327tile.json`) is
    intentionally preserved for comparability with the Era 3 h8-v2 / h10-v2 /
    h12-v2 library-design artefacts.

## Tier 2 (F1: 0.826–0.854)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 2 | h11-pvd-pro-high-text-n5 | 2 | text | 10 | 6 | 0.854 | [0.817, 0.885] | 0.947 | 0.777 |
| 3 | h11-pvd-flash-high-text-n5 | 2 | text | 30 | 26 | 0.826 | [0.793, 0.858] | 0.846 | 0.807 |

## Tier 3 (F1: 0.730–0.852)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 4 | h11-pvd-flash-high-image-n5 | 2 | image | 10 | 7 | 0.824 | [0.788, 0.857] | 0.854 | 0.795 |
| 5 | scale4-optimal-487 | 2 | image | 10 | 6 | 0.826 | [0.790, 0.858] | 0.859 | 0.795 |
| 6 | p3a-high-image-t1.0 | 2 | image | 10 | 6 | 0.804 | [0.768, 0.837] | 0.806 | 0.802 |
| 7 | p3a-high-image-t0.3 | 2 | image | 10 | 9 | 0.794 | [0.758, 0.829] | 0.875 | 0.726 |
| 8 | h11-e47-propose-brief | 2 | text | 5 | 5 | 0.730 | [0.683, 0.772] | 0.709 | 0.752 |
| 9 | h11-pvd-pro-high-image-n5 | 2 | image | 5 | 3 | 0.852 | [0.823, 0.881] | 0.820 | 0.887 |

## Tier 4 (F1: 0.669–0.745)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 10 | h11-pvd-image-n5 | 2 | image | 10 | 8 | 0.745 | [0.704, 0.782] | 0.700 | 0.795 |
| 11 | h11-n1-image-t03 | 2 | image | 3 | 3 | 0.745 | [0.706, 0.779] | 0.658 | 0.858 |
| 12 | h11-pvd-flash-minimal-text-n30-t07 | 2 | text | 30 | 29 | 0.669 | [0.621, 0.715] | 0.609 | 0.743 |
| 13 | p3a-min-image-t0.3 | 2 | image | 10 | 10 | 0.716 | [0.672, 0.757] | 0.660 | 0.784 |
| 14 | p3a-min-image-t1.0 | 2 | image | 10 | 8 | 0.735 | [0.696, 0.770] | 0.710 | 0.761 |

## Tier 5 (F1: 0.604–0.712)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 15 | h11-n1-image-t0 | 2 | image | 3 | 2 | 0.712 | [0.670, 0.746] | 0.583 | 0.913 |
| 16 | h11-pvd-text-n10 | 2 | text | 10 | 10 | 0.628 | [0.573, 0.681] | 0.536 | 0.759 |
| 17 | h11-n1-brief-text-t03 | 2 | text | 3 | 3 | 0.604 | [0.544, 0.659] | 0.467 | 0.853 |

## Tier 6 (F1: 0.603–0.653)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 18 | h11-n1-pro-text-high-t0 | 2 | text | 3 | 3 | 0.603 | [0.548, 0.655] | 0.469 | 0.844 |
| 19 | h11-n1-pro-image-high-t0 | 2 | image | 3 | 3 | 0.653 | [0.602, 0.696] | 0.561 | 0.779 |

## Tier 7 (F1: 0.580–0.580)

| # | Condition | Era | Track | K | t | F1 | 95% CI | P | R |
|--:|-----------|:---:|:-----:|--:|--:|---:|:------:|---:|---:|
| 20 | p3a-high-image-t0.0 | 2 | image | 3 | 1 | 0.580 | [0.529, 0.633] | 0.448 | 0.825 |
