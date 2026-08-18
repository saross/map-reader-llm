# Era-1 leaderboard — statistical tiering (20 m) — `era1-leaderboard`

- **Cells**: 82 (36 single-pass + 42 consensus + 4 verified-PV), 340 evaluation tiles
- **Metric**: micro-average F1 @ 20 m; MCC reported (tile-level, buffer-agnostic — NOT cross-era comparable)
- **`undefined` in the MCC column**: the tile-level MCC is not computable for that cell — the configuration returned a detection on every evaluation tile, so the predicted-negative column of the tile confusion matrix is empty and the MCC denominator vanishes. It is **not** a value of zero; see erratum E81 in `docs/methodology/preregistration/protocol-errata.md`. Tiering here is on micro-F1, so no rank or tier depends on it.
- **Test**: round-robin tile-swap permutation, 10,000 perms, seed 42, two-sided; **BH-FDR** q = 0.05
- **Pairs**: 3321 (2351 significant) -> **10 tiers**
- **Tie set (Tier 1)**: `retest-phase3a-high::verified-adv-text-high-t1.0-n30-23of30`

| rank | condition | kind | passes | F1@20m | micro-F1 | gap | MCC | tier |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | `verified-adv-text-high-t1.0-n30-23of30` | verified-PV | 1 | 0.792 | 0.792 | -0.000 | 0.676 | 1 |
| 2 | `text-high-t1.0-n30-23of30` | consensus | 1 | 0.775 | 0.775 | +0.000 | 0.642 | 2 |
| 3 | `text-high-t0.3-n30-23of30` | consensus | 1 | 0.774 | 0.774 | +0.000 | 0.576 | 2 |
| 4 | `text-high-t0.7-n30-22of30` | consensus | 1 | 0.773 | 0.773 | -0.000 | 0.572 | 2 |
| 5 | `text-high-t1.0-n10-8of10` | consensus | 1 | 0.772 | 0.772 | -0.000 | 0.548 | 2 |
| 6 | `text-high-t0.7-n30-21of30` | consensus | 1 | 0.770 | 0.771 | +0.000 | 0.547 | 2 |
| 7 | `verified-adv-text-t0.0` | verified-PV | 3 | 0.770 | 0.770 | -0.000 | 0.789 | 2 |
| 8 | `text-high-t0.3-n10-8of10` | consensus | 1 | 0.759 | 0.759 | -0.000 | 0.583 | 2 |
| 9 | `text-high-t0.7-n10-8of10` | consensus | 1 | 0.747 | 0.747 | +0.000 | 0.559 | 3 |
| 10 | `text-high-t0.7-n10-7of10` | consensus | 1 | 0.740 | 0.740 | +0.000 | 0.456 | 3 |
| 11 | `text-high-t0.3-n5-4of5` | consensus | 1 | 0.732 | 0.732 | -0.000 | 0.521 | 3 |
| 12 | `text-h9-d-diversity-4of5` | consensus | 5 | 0.730 | 0.730 | -0.000 | 0.484 | 3 |
| 13 | `text-high-t0.7-n5-4of5` | consensus | 1 | 0.730 | 0.730 | -0.000 | 0.475 | 3 |
| 14 | `verified-adv-image-t0.7-n30-18of30` | verified-PV | 1 | 0.728 | 0.727 | -0.000 | 0.785 | 3 |
| 15 | `text-high-t1.0-n5-4of5` | consensus | 1 | 0.726 | 0.726 | -0.000 | 0.440 | 3 |
| 16 | `text-h9-a-diversity-4of5` | consensus | 5 | 0.717 | 0.717 | -0.000 | 0.442 | 4 |
| 17 | `text-high-t0.7-n5-4of5` | consensus | 1 | 0.713 | 0.713 | -0.000 | 0.456 | 4 |
| 18 | `text-minimal-t0.7-n30-25of30` | consensus | 1 | 0.703 | 0.703 | -0.000 | 0.313 | 4 |
| 19 | `text-minimal-t0.7-n10-8of10` | consensus | 1 | 0.701 | 0.701 | +0.000 | 0.290 | 4 |
| 20 | `text-h9-e-diversity-4of5` | consensus | 5 | 0.694 | 0.694 | -0.000 | 0.456 | 5 |
| 21 | `text-t0.3-n30-23of30` | consensus | 1 | 0.692 | 0.692 | +0.000 | 0.181 | 5 |
| 22 | `text-t0.7-n30-24of30` | consensus | 1 | 0.692 | 0.692 | +0.000 | 0.269 | 5 |
| 23 | `image-t0.7-n30-18of30` | consensus | 1 | 0.691 | 0.691 | -0.000 | 0.442 | 5 |
| 24 | `text-minimal-t0.7-n5-4of5` | consensus | 1 | 0.691 | 0.691 | +0.000 | 0.223 | 5 |
| 25 | `text-t0.3-n10-8of10` | consensus | 1 | 0.687 | 0.687 | -0.000 | 0.154 | 5 |
| 26 | `text-h9-b-diversity-4of5` | consensus | 5 | 0.686 | 0.686 | -0.000 | 0.475 | 5 |
| 27 | `text-t1.0-n30-22of30` | consensus | 1 | 0.686 | 0.686 | -0.000 | 0.333 | 5 |
| 28 | `text-t0.3-n5-5of5` | consensus | 1 | 0.684 | 0.684 | -0.000 | 0.194 | 5 |
| 29 | `text-t1.0-n10-7of10` | consensus | 1 | 0.683 | 0.683 | -0.000 | 0.318 | 5 |
| 30 | `image-t1.0-n30-19of30` | consensus | 1 | 0.679 | 0.679 | +0.000 | 0.472 | 5 |
| 31 | `text-t0.7-n10-8of10` | consensus | 1 | 0.675 | 0.675 | -0.000 | 0.231 | 6 |
| 32 | `verified-adv-image-t0.0` | verified-PV | 3 | 0.674 | 0.674 | +0.000 | 0.889 | 6 |
| 33 | `image-h9-c-diversity-3of5` | consensus | 5 | 0.671 | 0.671 | -0.000 | 0.654 | 6 |
| 34 | `image-h9-e-diversity-3of5` | consensus | 5 | 0.670 | 0.670 | -0.000 | 0.660 | 6 |
| 35 | `image-t0.7-n10-7of10` | consensus | 1 | 0.669 | 0.669 | +0.000 | 0.461 | 6 |
| 36 | `image-h9-d-diversity-3of5` | consensus | 5 | 0.669 | 0.669 | +0.000 | 0.664 | 6 |
| 37 | `text-t1.0-n5-4of5` | consensus | 1 | 0.668 | 0.668 | -0.000 | 0.282 | 6 |
| 38 | `image-h9-b-diversity-3of5` | consensus | 5 | 0.668 | 0.668 | -0.000 | 0.648 | 6 |
| 39 | `image-t0.3-n30-22of30` | consensus | 1 | 0.666 | 0.666 | -0.000 | 0.271 | 6 |
| 40 | `image-h9-a-diversity-3of5` | consensus | 5 | 0.664 | 0.664 | +0.000 | 0.660 | 6 |
| 41 | `text-t0.7-n5-4of5` | consensus | 1 | 0.663 | 0.663 | +0.000 | 0.229 | 6 |
| 42 | `image-t0.3-n5-4of5` | consensus | 1 | 0.662 | 0.662 | -0.000 | 0.298 | 6 |
| 43 | `image-t0.3-n10-8of10` | consensus | 1 | 0.662 | 0.662 | +0.000 | 0.284 | 6 |
| 44 | `image-t0.7-n5-4of5` | consensus | 1 | 0.658 | 0.658 | -0.000 | 0.442 | 6 |
| 45 | `image-t1.0-n10-7of10` | consensus | 1 | 0.655 | 0.655 | +0.000 | 0.459 | 6 |
| 46 | `image-t1.0-n5-4of5` | consensus | 1 | 0.639 | 0.639 | +0.000 | 0.460 | 6 |
| 47 | `canonical-last` | single-pass | 1 | 0.631 | 0.631 | +0.000 | 0.213 | 6 |
| 48 | `text-scale-4` | single-pass | 1 | 0.609 | 0.609 | +0.000 | undefined | 7 |
| 49 | `text-scale-8` | single-pass | 1 | 0.607 | 0.607 | +0.000 | undefined | 7 |
| 50 | `text-t0.3` | single-pass | 3 | 0.607 | 0.606 | -0.000 | 0.067 | 7 |
| 51 | `config-default` | single-pass | 1 | 0.606 | 0.606 | +0.000 | 0.213 | 7 |
| 52 | `text-t0.0` | single-pass | 3 | 0.606 | 0.605 | -0.000 | undefined | 7 |
| 53 | `image-terse` | single-pass | 1 | 0.605 | 0.605 | -0.000 | 0.224 | 7 |
| 54 | `text-canonical` | single-pass | 1 | 0.605 | 0.604 | -0.000 | undefined | 7 |
| 55 | `text-pure-positive-canon` | single-pass | 1 | 0.605 | 0.604 | -0.000 | undefined | 7 |
| 56 | `image-verbose` | single-pass | 1 | 0.603 | 0.603 | -0.000 | 0.281 | 7 |
| 57 | `image-plus-hp` | single-pass | 1 | 0.599 | 0.598 | -0.000 | 0.094 | 7 |
| 58 | `image-exploratory-pure-positive-4hp` | single-pass | 1 | 0.599 | 0.598 | -0.000 | 0.164 | 7 |
| 59 | `canonical-first` | single-pass | 1 | 0.599 | 0.598 | -0.000 | 0.094 | 7 |
| 60 | `text-terse` | single-pass | 1 | 0.598 | 0.598 | +0.000 | undefined | 7 |
| 61 | `text-plus-hp` | single-pass | 1 | 0.597 | 0.597 | +0.000 | undefined | 7 |
| 62 | `image-scale-8` | single-pass | 1 | 0.587 | 0.587 | +0.000 | 0.150 | 7 |
| 63 | `image-t0.0` | single-pass | 3 | 0.586 | 0.586 | -0.000 | 0.150 | 7 |
| 64 | `text-t0.7` | single-pass | 3 | 0.584 | 0.584 | -0.000 | undefined | 7 |
| 65 | `image-scale-4` | single-pass | 1 | 0.584 | 0.584 | +0.000 | 0.134 | 7 |
| 66 | `text-verbose` | single-pass | 1 | 0.583 | 0.583 | -0.000 | 0.067 | 7 |
| 67 | `image-canonical` | single-pass | 1 | 0.581 | 0.581 | +0.000 | 0.094 | 7 |
| 68 | `image-t0.3` | single-pass | 3 | 0.575 | 0.575 | -0.000 | 0.123 | 8 |
| 69 | `image-exploratory-pure-positive-2hp` | single-pass | 1 | 0.571 | 0.571 | +0.000 | undefined | 8 |
| 70 | `random` | single-pass | 1 | 0.571 | 0.571 | -0.000 | 0.067 | 8 |
| 71 | `image-exploratory-pure-positive-canon` | single-pass | 1 | 0.570 | 0.570 | -0.000 | 0.094 | 8 |
| 72 | `image-pure-positive-canon` | single-pass | 1 | 0.568 | 0.568 | +0.000 | 0.094 | 8 |
| 73 | `brief-text` | single-pass | 3 | 0.552 | 0.552 | -0.000 | 0.067 | 8 |
| 74 | `text-t1.3` | single-pass | 3 | 0.544 | 0.544 | -0.000 | 0.067 | 8 |
| 75 | `image-t0.7` | single-pass | 3 | 0.537 | 0.537 | -0.000 | 0.173 | 9 |
| 76 | `text-t1.0` | single-pass | 3 | 0.533 | 0.533 | -0.000 | 0.067 | 9 |
| 77 | `image-t1.0` | single-pass | 3 | 0.527 | 0.527 | -0.000 | 0.181 | 9 |
| 78 | `brief-text-image` | single-pass | 3 | 0.522 | 0.522 | -0.000 | 0.177 | 9 |
| 79 | `verbose-text-image` | single-pass | 3 | 0.517 | 0.517 | -0.000 | 0.291 | 9 |
| 80 | `verbose-text` | single-pass | 3 | 0.502 | 0.502 | -0.000 | 0.067 | 9 |
| 81 | `image-t1.3` | single-pass | 3 | 0.492 | 0.492 | -0.000 | 0.210 | 10 |
| 82 | `image-only` | single-pass | 3 | 0.470 | 0.470 | -0.000 | 0.109 | 10 |
