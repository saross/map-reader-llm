# Regenerated tier clustering — 23 conditions (20 m buffer, FDR-corrected, E72)

> **Last revised**: 2026-10-30 (regenerated on the restated pairwise layout, PI ruling D69 Q15). Prior: 2026-08-02 (original publication — E72 remediation). See [§ Changelog](#changelog) for revision history.

Conditions within a tier are statistically indistinguishable (all pairwise BH-adjusted p-values >= 0.05). Based on 253 retained permutation tests (10,000 permutations, seed 42) among the 23 retained conditions, BH-corrected at q = 0.05 over the retained family.

Dropped under E72: `flash-min-text-t10 N=10 N=10, 9-of-10`, `flash-min-text-t10 N=30 N=30, 22-of-30`, `flash-min-text-t10 N=5 N=5, 5-of-5`.

## Tier 1 (F1: 0.864–0.890)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 1 | flash-high-text-16-of-30--flash-min-vf (t=0.2) | 0.890 | 0.915 | 0.867 |
| 2 | flash-high-text-4-of-5--flash-min-vf (t=0.15) | 0.864 | 0.915 | 0.818 |

## Tier 2 (F1: 0.836–0.859)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 3 | flash-high-text-4-of-5--flash-medium-vf (t=0.95) | 0.859 | 0.878 | 0.841 |
| 4 | flash-high-text-9-of-10--flash-min-vf (t=0.2) | 0.856 | 0.957 | 0.775 |
| 5 | pro-high-text-3-of-5--flash-min-vf (t=0.15) | 0.849 | 0.957 | 0.763 |
| 6 | pro-high-text N=5 N=5, 3-of-5 | 0.843 | 0.921 | 0.777 |
| 7 | pro-high-text N=10 N=10, 6-of-10 | 0.836 | 0.927 | 0.761 |

## Tier 3 (F1: 0.814–0.816)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 8 | flash-high-text N=30 N=30, 26-of-30 | 0.816 | 0.836 | 0.798 |
| 9 | text-baseline--flash-min-vf (t=0.15) | 0.814 | 0.789 | 0.841 |

## Tier 4 (F1: 0.778–0.799)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 10 | flash-high-text N=10 N=10, 9-of-10 | 0.799 | 0.803 | 0.795 |
| 11 | flash-high-text N=5 N=5, 5-of-5 | 0.781 | 0.800 | 0.763 |
| 12 | flash-high-image-3-of-5--flash-min-vf (t=0.15) | 0.778 | 0.800 | 0.756 |

## Tier 5 (F1: 0.700–0.752)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 13 | flash-high-image N=10 N=10, 7-of-10 | 0.752 | 0.780 | 0.726 |
| 14 | flash-high-image N=5 N=5, 3-of-5 | 0.729 | 0.678 | 0.789 |
| 15 | image-baseline--flash-min-vf (t=0.2) | 0.717 | 0.663 | 0.779 |
| 16 | pro-high-image N=5 N=5, 3-of-5 | 0.700 | 0.673 | 0.729 |

## Tier 6 (F1: 0.642–0.682)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 17 | flash-min-image N=10 N=10, 8-of-10 | 0.682 | 0.642 | 0.729 |
| 18 | flash-min-image N=5 N=5, 4-of-5 | 0.666 | 0.610 | 0.733 |
| 19 | flash-min-text-t07 N=30 N=30, 29-of-30 | 0.663 | 0.604 | 0.736 |
| 20 | flash-min-text-t07 N=5 N=5, 5-of-5 | 0.642 | 0.534 | 0.802 |

## Tier 7 (F1: 0.635)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 21 | flash-min-text-t07 N=10 N=10, 10-of-10 | 0.635 | 0.564 | 0.726 |

## Tier 8 (F1: 0.547–0.555)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 22 | single-pass-t0 N=10 N=10, 10-of-10 | 0.555 | 0.412 | 0.853 |
| 23 | single-pass-t0 N=5 N=5, 5-of-5 | 0.547 | 0.398 | 0.874 |

## Changelog

### 2026-10-30 — Regenerated on the restated pairwise layout (Session 166)

**Trigger**: the S164 restatement pass regenerated `results/pairwise/` in place on the consensus route of PI ruling D60 (3) (`08af04cf3`; PR #52, merged as `0d195cac8`). The per-pair files that read the two drifted single-pass arms stay at their paths as dated March records, with today's runs beside them under `results/rescore-2026-10-15/pairwise/` (D61 (2)); this revision reads those runs in place of the 100 records the boards and families use. The PI queued the regeneration as D69 Q15. No permutation test was re-run. The full entry is in [`../summary.md` § Changelog](../summary.md#changelog).

| Figure | 2026-08-02 | 2026-10-30 |
|---|--:|--:|
| BH-significant pairs | 199 of 253 | 198 of 253 |
| Tiers | 8 | 8 |
| Retained pairs whose raw p moved | — | 64 of 253 |
| Retained conditions whose F1 or tier moved | — | 13 of 23 |

| Condition | F1 (2026-08-02) | F1 (2026-10-30) | Tier (2026-08-02) | Tier (2026-10-30) |
|---|:---:|:---:|--:|--:|
| pro-high-text N=5 N=5, 3-of-5 | 0.840399 | 0.842893 | 2 | 2 |
| flash-high-text N=30 N=30, 26-of-30 | 0.814118 | 0.816471 | 3 | 3 |
| flash-high-text N=10 N=10, 9-of-10 | 0.796767 | 0.799076 | 4 | 4 |
| flash-high-text N=5 N=5, 5-of-5 | 0.778824 | 0.781176 | 4 | 4 |
| flash-high-image N=10 N=10, 7-of-10 | 0.750000 | 0.752381 | 5 | 5 |
| flash-high-image N=5 N=5, 3-of-5 | 0.726886 | 0.729012 | 5 | 5 |
| flash-min-image N=10 N=10, 8-of-10 | 0.680301 | 0.682454 | 6 | 6 |
| flash-min-image N=5 N=5, 4-of-5 | 0.663883 | 0.665971 | 6 | 6 |
| flash-min-text-t07 N=30 N=30, 29-of-30 | 0.661140 | 0.663212 | 6 | 6 |
| flash-min-text-t07 N=5 N=5, 5-of-5 | 0.639706 | 0.641544 | 6 | 6 |
| flash-min-text-t07 N=10 N=10, 10-of-10 | 0.633166 | 0.635176 | 7 | 7 |
| single-pass-t0 N=10 N=10, 10-of-10 | 0.552138 | 0.555389 | 8 | 8 |
| single-pass-t0 N=5 N=5, 5-of-5 | 0.544012 | 0.547156 | 8 | 8 |

BH verdicts that changed between the two revisions: 1 (see the summary's changelog).

Not changed: the 23 retained conditions and 253 retained pairs, the dropped cells, and the method.

### 2026-08-02 — Original publication

First version, written by `scripts/regen_e43_board.py` at `bc45133b4` and committed in `2f3ef020a` under protocol erratum E72, option (a): the March round-robin with the three coverage-confounded `flash-min-text-t10` cells dropped, BH recomputed over the retained family, and the greedy-clique tiers re-run. It carried a banner and no changelog.
