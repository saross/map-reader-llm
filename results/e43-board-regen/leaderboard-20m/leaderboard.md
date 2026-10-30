# Regenerated leaderboard — 23 conditions (20 m buffer, E72)

> **Last revised**: 2026-10-30 (regenerated on the restated pairwise layout, PI ruling D69 Q15). Prior: 2026-08-02 (original publication — E72 remediation). See [§ Changelog](#changelog) for revision history.

Dropped under E72 (240-tile study scored against 487-tile bounds): `flash-min-text-t10 N=10 N=10, 9-of-10`, `flash-min-text-t10 N=30 N=30, 22-of-30`, `flash-min-text-t10 N=5 N=5, 5-of-5`.

Retained pairs: **253**; BH-significant at q = 0.05: **198**; tiers: **8**.

| Rank | Condition | Tier | F1 | P | R | Detections |
|--:|---|--:|:---:|:---:|:---:|--:|
| 1 | flash-high-text-16-of-30--flash-min-vf (t=0.2) | 1 | 0.890 | 0.915 | 0.867 | 412 |
| 2 | flash-high-text-4-of-5--flash-min-vf (t=0.15) | 1 | 0.864 | 0.915 | 0.818 | 389 |
| 3 | flash-high-text-4-of-5--flash-medium-vf (t=0.95) | 2 | 0.859 | 0.878 | 0.841 | 417 |
| 4 | flash-high-text-9-of-10--flash-min-vf (t=0.2) | 2 | 0.856 | 0.957 | 0.775 | 352 |
| 5 | pro-high-text-3-of-5--flash-min-vf (t=0.15) | 2 | 0.849 | 0.957 | 0.763 | 347 |
| 6 | pro-high-text N=5 N=5, 3-of-5 | 2 | 0.843 | 0.921 | 0.777 | 367 |
| 7 | pro-high-text N=10 N=10, 6-of-10 | 2 | 0.836 | 0.927 | 0.761 | 357 |
| 8 | flash-high-text N=30 N=30, 26-of-30 | 3 | 0.816 | 0.836 | 0.798 | 415 |
| 9 | text-baseline--flash-min-vf (t=0.15) | 3 | 0.814 | 0.789 | 0.841 | 464 |
| 10 | flash-high-text N=10 N=10, 9-of-10 | 4 | 0.799 | 0.803 | 0.795 | 431 |
| 11 | flash-high-text N=5 N=5, 5-of-5 | 4 | 0.781 | 0.800 | 0.763 | 415 |
| 12 | flash-high-image-3-of-5--flash-min-vf (t=0.15) | 4 | 0.778 | 0.800 | 0.756 | 411 |
| 13 | flash-high-image N=10 N=10, 7-of-10 | 5 | 0.752 | 0.780 | 0.726 | 405 |
| 14 | flash-high-image N=5 N=5, 3-of-5 | 5 | 0.729 | 0.678 | 0.789 | 506 |
| 15 | image-baseline--flash-min-vf (t=0.2) | 5 | 0.717 | 0.663 | 0.779 | 511 |
| 16 | pro-high-image N=5 N=5, 3-of-5 | 5 | 0.700 | 0.673 | 0.729 | 471 |
| 17 | flash-min-image N=10 N=10, 8-of-10 | 6 | 0.682 | 0.642 | 0.729 | 494 |
| 18 | flash-min-image N=5 N=5, 4-of-5 | 6 | 0.666 | 0.610 | 0.733 | 523 |
| 19 | flash-min-text-t07 N=30 N=30, 29-of-30 | 6 | 0.663 | 0.604 | 0.736 | 530 |
| 20 | flash-min-text-t07 N=5 N=5, 5-of-5 | 6 | 0.642 | 0.534 | 0.802 | 653 |
| 21 | flash-min-text-t07 N=10 N=10, 10-of-10 | 7 | 0.635 | 0.564 | 0.726 | 560 |
| 22 | single-pass-t0 N=10 N=10, 10-of-10 | 8 | 0.555 | 0.412 | 0.853 | 901 |
| 23 | single-pass-t0 N=5 N=5, 5-of-5 | 8 | 0.547 | 0.398 | 0.874 | 954 |

Tile-level MCC is not reproduced here — the permutation artefacts carry only mound-level counts. Dropping whole cells does not change any retained condition's metrics, but the MCC column of the dated March snapshot keeps its March 2026 values, which predate the 2026-10-15 restatement of the mound-level metrics above; it is not asserted current for these rows.

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
