# Regenerated tier clustering — 22 conditions (30 m buffer, FDR-corrected, E72)

> **Last revised**: 2026-10-30 (regenerated on the restated pairwise layout, PI ruling D69 Q15). Prior: 2026-08-02 (original publication — E72 remediation). See [§ Changelog](#changelog) for revision history.

Conditions within a tier are statistically indistinguishable (all pairwise BH-adjusted p-values >= 0.05). Based on 231 retained permutation tests (10,000 permutations, seed 42) among the 22 retained conditions, BH-corrected at q = 0.05 over the retained family.

Dropped under E72: `flash-min-text-t10 N=10 N=10, 9-of-10`, `flash-min-text-t10 N=30 N=30, 22-of-30`, `flash-min-text-t10 N=5 N=5, 5-of-5`.

## Tier 1 (F1: 0.885–0.904)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 1 | flash-high-text-16-of-30--flash-min-vf (t=0.2) | 0.904 | 0.930 | 0.880 |
| 2 | flash-high-text-4-of-5--flash-min-vf (t=0.15) | 0.891 | 0.943 | 0.844 |
| 3 | flash-high-text-4-of-5--flash-medium-vf (t=0.95) | 0.885 | 0.904 | 0.867 |

## Tier 2 (F1: 0.851–0.869)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 4 | flash-high-text-9-of-10--flash-min-vf (t=0.2) | 0.869 | 0.972 | 0.786 |
| 5 | pro-high-text-3-of-5--flash-min-vf (t=0.15) | 0.864 | 0.974 | 0.777 |
| 6 | pro-high-text N=5 N=5, 3-of-5 | 0.858 | 0.937 | 0.791 |
| 7 | flash-high-image-3-of-5--flash-min-vf (t=0.15) | 0.851 | 0.876 | 0.828 |

## Tier 3 (F1: 0.801–0.832)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 8 | text-baseline--flash-min-vf (t=0.15) | 0.832 | 0.806 | 0.860 |
| 9 | flash-high-text N=30 N=30, 26-of-30 | 0.828 | 0.848 | 0.809 |
| 10 | pro-high-image N=5 N=5, 3-of-5 | 0.821 | 0.790 | 0.855 |
| 11 | flash-high-image N=10 N=10, 6-of-10 | 0.814 | 0.790 | 0.839 |
| 12 | flash-high-text N=10 N=10, 9-of-10 | 0.813 | 0.817 | 0.809 |
| 13 | flash-high-image N=5 N=5, 3-of-5 | 0.801 | 0.745 | 0.867 |

## Tier 4 (F1: 0.782–0.791)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 14 | flash-high-text N=5 N=5, 5-of-5 | 0.791 | 0.810 | 0.772 |
| 15 | image-baseline--flash-min-vf (t=0.2) | 0.782 | 0.724 | 0.851 |

## Tier 5 (F1: 0.727–0.735)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 16 | flash-min-image N=10 N=10, 6-of-10 | 0.735 | 0.645 | 0.855 |
| 17 | flash-min-image N=5 N=5, 4-of-5 | 0.727 | 0.665 | 0.800 |

## Tier 6 (F1: 0.649–0.672)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 18 | flash-min-text-t07 N=30 N=30, 29-of-30 | 0.672 | 0.611 | 0.745 |
| 19 | flash-min-text-t07 N=5 N=5, 5-of-5 | 0.649 | 0.541 | 0.811 |

## Tier 7 (F1: 0.643)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 20 | flash-min-text-t07 N=10 N=10, 10-of-10 | 0.643 | 0.571 | 0.736 |

## Tier 8 (F1: 0.557–0.566)

| # | Condition | F1 | P | R |
|--:|---|:---:|:---:|:---:|
| 21 | single-pass-t0 N=10 N=10, 10-of-10 | 0.566 | 0.420 | 0.869 |
| 22 | single-pass-t0 N=5 N=5, 5-of-5 | 0.557 | 0.406 | 0.890 |

## Changelog

### 2026-10-30 — Regenerated on the restated pairwise layout (Session 166)

**Trigger**: the S164 restatement pass regenerated `results/pairwise/` in place on the consensus route of PI ruling D60 (3) (`08af04cf3`; PR #52, merged as `0d195cac8`). The per-pair files that read the two drifted single-pass arms stay at their paths as dated March records, with today's runs beside them under `results/rescore-2026-10-15/pairwise/` (D61 (2)); this revision reads those runs in place of the 100 records the boards and families use. The PI queued the regeneration as D69 Q15. No permutation test was re-run. The full entry is in [`../summary.md` § Changelog](../summary.md#changelog).

| Figure | 2026-08-02 | 2026-10-30 |
|---|--:|--:|
| BH-significant pairs | 181 of 231 | 178 of 231 |
| Tiers | 8 | 8 |
| Retained pairs whose raw p moved | — | 58 of 231 |
| Retained conditions whose F1 or tier moved | — | 13 of 22 |

| Condition | F1 (2026-08-02) | F1 (2026-10-30) | Tier (2026-08-02) | Tier (2026-10-30) |
|---|:---:|:---:|--:|--:|
| pro-high-text N=5 N=5, 3-of-5 | 0.855362 | 0.857855 | 2 | 2 |
| flash-high-text N=30 N=30, 26-of-30 | 0.825882 | 0.828235 | 3 | 3 |
| flash-high-image N=10 N=10, 6-of-10 | 0.811594 | 0.813824 | 3 | 3 |
| flash-high-text N=10 N=10, 9-of-10 | 0.810624 | 0.812933 | 3 | 3 |
| flash-high-image N=5 N=5, 3-of-5 | 0.799150 | 0.801275 | 3 | 3 |
| flash-high-text N=5 N=5, 5-of-5 | 0.788235 | 0.790588 | 4 | 4 |
| flash-min-image N=10 N=10, 6-of-10 | 0.733202 | 0.735178 | 5 | 5 |
| flash-min-image N=5 N=5, 4-of-5 | 0.724426 | 0.726514 | 5 | 5 |
| flash-min-text-t07 N=30 N=30, 29-of-30 | 0.669430 | 0.671503 | 6 | 6 |
| flash-min-text-t07 N=5 N=5, 5-of-5 | 0.647059 | 0.648897 | 6 | 6 |
| flash-min-text-t07 N=10 N=10, 10-of-10 | 0.641206 | 0.643216 | 7 | 7 |
| single-pass-t0 N=10 N=10, 10-of-10 | 0.562641 | 0.565868 | 8 | 8 |
| single-pass-t0 N=5 N=5, 5-of-5 | 0.554113 | 0.557235 | 8 | 8 |

BH verdicts that changed between the two revisions: 3 (see the summary's changelog).

Not changed: the 22 retained conditions and 231 retained pairs, the dropped cells, and the method.

### 2026-08-02 — Original publication

First version, written by `scripts/regen_e43_board.py` at `bc45133b4` and committed in `2f3ef020a` under protocol erratum E72, option (a): the March round-robin with the three coverage-confounded `flash-min-text-t10` cells dropped, BH recomputed over the retained family, and the greedy-clique tiers re-run. It carried a banner and no changelog.
