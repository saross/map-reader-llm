# Era-1 leaderboard — statistical tiering (20 m) — `era1-single-pass-baseline-matrix`

- **Cells**: 36 (36 single-pass + 0 consensus), 340 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 630 (227 significant) -> **4 tiers**
- **Tie set (Tier 1)**: `retest-phase2e::canonical-last`, `retest-phase2c::text-scale-4`, `retest-phase2c::text-scale-8`, `retest-phase2b::text-t0.3`, `retest-phase2e::config-default`, `retest-phase2b::text-t0.0`, `retest-phase2d::image-terse`, `retest-phase2c::text-canonical`, `retest-phase2c::text-pure-positive-canon`, `retest-phase2d::image-verbose`, `retest-phase2c::image-plus-hp`, `retest-phase2c::image-exploratory-pure-positive-4hp`, `retest-phase2e::canonical-first`, `retest-phase2d::text-terse`, `retest-phase2c::text-plus-hp`, `retest-phase2c::image-scale-8`, `retest-phase2b::image-t0.0`, `retest-phase2b::text-t0.7`, `retest-phase2c::image-scale-4`, `retest-phase2d::text-verbose`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `canonical-last` | single-pass | 1 | 0.631 | 0.631 | +0.000 | 0.213 | 1 |
| 2 | `text-scale-4` | single-pass | 1 | 0.609 | 0.609 | +0.000 | 0.000 | 1 |
| 3 | `text-scale-8` | single-pass | 1 | 0.607 | 0.607 | +0.000 | 0.000 | 1 |
| 4 | `text-t0.3` | single-pass | 3 | 0.607 | 0.606 | -0.000 | 0.044 | 1 |
| 5 | `config-default` | single-pass | 1 | 0.606 | 0.606 | +0.000 | 0.213 | 1 |
| 6 | `text-t0.0` | single-pass | 3 | 0.606 | 0.605 | -0.000 | 0.000 | 1 |
| 7 | `image-terse` | single-pass | 1 | 0.605 | 0.605 | -0.000 | 0.224 | 1 |
| 8 | `text-canonical` | single-pass | 1 | 0.605 | 0.604 | -0.000 | 0.000 | 1 |
| 9 | `text-pure-positive-canon` | single-pass | 1 | 0.605 | 0.604 | -0.000 | 0.000 | 1 |
| 10 | `image-verbose` | single-pass | 1 | 0.603 | 0.603 | -0.000 | 0.281 | 1 |
| 11 | `image-plus-hp` | single-pass | 1 | 0.599 | 0.598 | -0.000 | 0.094 | 1 |
| 12 | `image-exploratory-pure-positive-4hp` | single-pass | 1 | 0.599 | 0.598 | -0.000 | 0.164 | 1 |
| 13 | `canonical-first` | single-pass | 1 | 0.599 | 0.598 | -0.000 | 0.094 | 1 |
| 14 | `text-terse` | single-pass | 1 | 0.598 | 0.598 | +0.000 | 0.000 | 1 |
| 15 | `text-plus-hp` | single-pass | 1 | 0.597 | 0.597 | +0.000 | 0.000 | 1 |
| 16 | `image-scale-8` | single-pass | 1 | 0.587 | 0.587 | +0.000 | 0.150 | 1 |
| 17 | `image-t0.0` | single-pass | 3 | 0.586 | 0.586 | -0.000 | 0.150 | 1 |
| 18 | `text-t0.7` | single-pass | 3 | 0.584 | 0.584 | -0.000 | 0.000 | 1 |
| 19 | `image-scale-4` | single-pass | 1 | 0.584 | 0.584 | +0.000 | 0.134 | 1 |
| 20 | `text-verbose` | single-pass | 1 | 0.583 | 0.583 | -0.000 | 0.067 | 1 |
| 21 | `image-canonical` | single-pass | 1 | 0.581 | 0.581 | +0.000 | 0.094 | 2 |
| 22 | `image-t0.3` | single-pass | 3 | 0.575 | 0.575 | -0.000 | 0.123 | 2 |
| 23 | `image-exploratory-pure-positive-2hp` | single-pass | 1 | 0.571 | 0.571 | +0.000 | 0.000 | 2 |
| 24 | `random` | single-pass | 1 | 0.571 | 0.571 | -0.000 | 0.067 | 2 |
| 25 | `image-exploratory-pure-positive-canon` | single-pass | 1 | 0.570 | 0.570 | -0.000 | 0.094 | 2 |
| 26 | `image-pure-positive-canon` | single-pass | 1 | 0.568 | 0.568 | +0.000 | 0.094 | 2 |
| 27 | `brief-text` | single-pass | 3 | 0.552 | 0.552 | -0.000 | 0.044 | 2 |
| 28 | `text-t1.3` | single-pass | 3 | 0.544 | 0.544 | -0.000 | 0.067 | 2 |
| 29 | `image-t0.7` | single-pass | 3 | 0.537 | 0.537 | -0.000 | 0.173 | 3 |
| 30 | `text-t1.0` | single-pass | 3 | 0.533 | 0.533 | -0.000 | 0.022 | 3 |
| 31 | `image-t1.0` | single-pass | 3 | 0.527 | 0.527 | -0.000 | 0.181 | 3 |
| 32 | `brief-text-image` | single-pass | 3 | 0.522 | 0.522 | -0.000 | 0.177 | 3 |
| 33 | `verbose-text-image` | single-pass | 3 | 0.517 | 0.517 | -0.000 | 0.291 | 3 |
| 34 | `verbose-text` | single-pass | 3 | 0.502 | 0.502 | -0.000 | 0.044 | 3 |
| 35 | `image-t1.3` | single-pass | 3 | 0.492 | 0.492 | -0.000 | 0.210 | 4 |
| 36 | `image-only` | single-pass | 3 | 0.470 | 0.470 | -0.000 | 0.109 | 4 |
