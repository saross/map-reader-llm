# Leaderboard Tier Clustering (20m buffer, FDR-corrected)

> **Last revised**: 2026-10-30 (the E72 block's regenerated-board figures
> updated, PI ruling D69 Q15: 198 significant, not 199). Prior: 2026-10-15
> (restated-figures banner added for the 20 m
> pairwise run regenerated on the consensus route, PI ruling D60 (3); tables
> unchanged). Prior: 2026-08-02 (E72 — superseded-figures banner added). See
> [§ Changelog](#changelog) for revision history.
>
> **Restated figures (2026-10-15, D60 (3))**: the 325-pair run under
> `results/pairwise/leaderboard-20m/` was regenerated with the consensus route
> that keeps each cluster's contributing tiles (PR #37). Sixteen consensus and
> single-pass rows (#6, #9, #11 to #14, #17 to #26) rise by +0.0018 to +0.0033
> F1, with their precision and recall rising alongside; no proposer–verifier
> row moves. Among them, #9 (FH text 26/30) reads 0.816 and now sits above #8
> (0.814) inside Tier 3, and #23 (single-pass T=0 5/5) reads 0.547 on 954
> detections (D61 (2); its March per-pair files stay as records, with today's
> runs beside them under `results/rescore-2026-10-15/pairwise/`). The nine
> tiers keep their members, 265 of 325 pairs are still significant (two pairs
> swap in opposite directions), and #1 against #2 keeps raw p = 0.0398 with
> q = 0.0490 (was 0.0488). The tables below keep their 2026-03-29 values; the
> changelog lists every moved row. The E72 banner's reduced-board figures come
> from `results/e43-board-regen/`, which this pass did not regenerate.
>
> **⚠ Superseded figures (2026-08-02, E72)**: rows #24 (FM text T=1.0 5/5),
> #25 (22/30) and #26 (9/10) — Tier 8's last member and the whole of Tier 9 —
> derive from `outputs/h11/consensus-384-UNINTENDED-T1.0`, a 240-tile study
> scored against 487-tile bounds (coverage confound — see protocol-errata E43
> correction block + E72), and understate that arm by ~0.17–0.19 F1. The tier
> structure is affected as well: with those three cells dropped the board has
> 23 conditions, 253 pairwise tests, 199 significant after BH (198 since the
> 2026-10-30 regeneration on the restated inputs), and **8 tiers**;
> Tier 9 disappears and #2 (FH text 4/5 + PV, min vf) joins the leader in
> Tier 1 because their separation (q = 0.0488; 0.0490 since the 2026-10-15
> restatement) no longer survives the smaller family (q = 0.0503; 0.0506 since
> 2026-10-30). Regenerated 23-condition board:
> `results/e43-board-regen/`. Matched-scope analysis:
> `results/e43-matched-temperature/`. Dated snapshot; body unchanged; do not
> cite the affected rows.

Conditions within the same tier are statistically indistinguishable
(all pairwise adjusted p-values >= 0.05). Based on 325 pairwise
permutation tests (10,000 permutations, seed 42) among all 26
leaderboard conditions, FDR-corrected at q=0.05.

MCC, sensitivity, and specificity are tile-level metrics (does this
384px tile contain any mound?). These are independent of spatial buffer.
Two conditions (#13, #17) have MCC from the nearest evaluated threshold,
marked with ~.

**Scope unification note (2026-04-24)**: this document uses phase3a
condition labels (e.g. "FH text 16/30 + PV (min vf)") and is not a mirror
of `results/leaderboard/era2/leaderboard_tiers_20m.md`, which uses the
h11-series cell naming. The Session 78 gold-standard-v2 scope-unified cell
at Era 2 (487-tile) scope reports F1=0.854 at 20 m
(`results/leaderboard/cells/gold-standard-v2-greedy-v1-487tile.json`).
It would sit in Tier 2 here on F1 but is not inserted as a distinct row
because the tier discussion focuses on phase3a matrix conditions with
matched pairwise permutation statistics. The Era 3 (327-tile) scope-pair
sibling (`gold-standard-v2-greedy-v1-327tile.json`) is intentionally
preserved for comparability with the Era 3 h8-v2 / h10-v2 / h12-v2
library-design artefacts.

## Tier 1 (F1: 0.890)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 1 | FH text 16/30 + PV (min vf) | 0.890 | 0.915 | 0.867 | 0.790 | [0.733, 0.840] | 0.821 | 0.957 |

## Tier 2 (F1: 0.836–0.864)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 2 | FH text 4/5 + PV (min vf) | 0.864 | 0.915 | 0.818 | 0.769 | [0.716, 0.820] | 0.786 | 0.965 |
| 3 | FH text 4/5 + PV (med vf) | 0.859 | 0.878 | 0.841 | 0.739 | [0.679, 0.793] | 0.804 | 0.926 |
| 4 | FH text 9/10 + PV (min vf) | 0.856 | 0.957 | 0.775 | 0.749 | [0.696, 0.797] | 0.738 | 0.981 |
| 5 | Pro H text 3/5 + PV (min vf) | 0.849 | 0.957 | 0.763 | 0.730 | [0.676, 0.783] | 0.703 | 0.988 |
| 6 | Pro H text 3/5 (N=5 cons.) | 0.840 | 0.918 | 0.775 | 0.736 | [0.682, 0.788] | 0.747 | 0.965 |
| 7 | Pro H text 6/10 (N=10 cons.) | 0.837 | 0.921 | 0.767 | 0.710 | [0.654, 0.764] | 0.703 | 0.973 |

## Tier 3 (F1: 0.778–0.814)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 8 | Text baseline + PV | 0.814 | 0.789 | 0.841 | 0.833 | [0.783, 0.877] | 0.869 | 0.957 |
| 9 | FH text 26/30 (consensus) | 0.814 | 0.834 | 0.795 | 0.620 | [0.549, 0.691] | 0.777 | 0.841 |
| 10 | FH image 3/5 + PV | 0.778 | 0.800 | 0.756 | 0.827 | [0.777, 0.873] | 0.847 | 0.969 |

## Tier 4 (F1: 0.779–0.797)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 11 | FH text 9/10 (consensus) | 0.797 | 0.800 | 0.793 | 0.621 | [0.545, 0.691] | 0.795 | 0.826 |
| 12 | FH text 5/5 (consensus) | 0.779 | 0.798 | 0.761 | 0.600 | [0.529, 0.671] | 0.769 | 0.830 |

## Tier 5 (F1: 0.700–0.750)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 13 | FH image 7/10 (consensus) | 0.750 | 0.778 | 0.724 | ~0.675 | [0.604, 0.736] | 0.838 | 0.837 |
| 14 | FH image 3/5 (consensus) | 0.727 | 0.676 | 0.786 | 0.665 | [0.598, 0.724] | 0.856 | 0.810 |
| 15 | Image baseline + PV | 0.717 | 0.663 | 0.779 | 0.877 | [0.833, 0.919] | 0.943 | 0.934 |
| 16 | Pro H image 3/5 (consensus) | 0.700 | 0.673 | 0.729 | 0.761 | [0.706, 0.816] | 0.843 | 0.915 |

## Tier 6 (F1: 0.640–0.680)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 17 | FM image 8/10 (consensus) | 0.680 | 0.640 | 0.726 | ~0.361 | [0.283, 0.433] | 0.860 | 0.477 |
| 18 | FM image 4/5 (consensus) | 0.664 | 0.608 | 0.731 | 0.390 | [0.310, 0.469] | 0.843 | 0.531 |
| 19 | FM text T=0.7 29/30 | 0.661 | 0.602 | 0.733 | 0.381 | [0.302, 0.460] | 0.817 | 0.554 |
| 20 | FM text T=0.7 5/5 | 0.640 | 0.533 | 0.800 | 0.315 | [0.230, 0.395] | 0.860 | 0.426 |

## Tier 7 (F1: 0.633)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 21 | FM text T=0.7 10/10 | 0.633 | 0.562 | 0.724 | 0.366 | [0.284, 0.444] | 0.834 | 0.516 |

## Tier 8 (F1: 0.471–0.552)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 22 | Single-pass T=0 10/10 | 0.552 | 0.410 | 0.846 | 0.212 | [0.126, 0.293] | 0.913 | 0.248 |
| 23 | Single-pass T=0 5/5 | 0.544 | 0.396 | 0.867 | 0.178 | [0.096, 0.255] | 0.926 | 0.198 |
| 24 | FM text T=1.0 5/5 | 0.471 | 0.583 | 0.395 | 0.257 | [0.176, 0.338] | 0.454 | 0.787 |

## Tier 9 (F1: 0.462–0.467)

| # | Condition | F1 | P | R | MCC | MCC CI | Sens | Spec |
|--:|---|:---:|:---:|:---:|:---:|---|:---:|:---:|
| 25 | FM text T=1.0 22/30 | 0.467 | 0.499 | 0.439 | 0.208 | [0.122, 0.298] | 0.498 | 0.705 |
| 26 | FM text T=1.0 9/10 | 0.462 | 0.545 | 0.400 | 0.212 | [0.122, 0.303] | 0.467 | 0.736 |

## Statistics

- 325 pairwise comparisons (all 26 leaderboard conditions)
- 265/325 significant after FDR correction (q=0.05)
- 9 tiers identified via greedy clique-based clustering
- MCC values marked with ~ are from the nearest evaluated consensus
  threshold; the difference is minor

## Changelog

### 2026-10-30 — E72 block: the regenerated board on the restated inputs (PI ruling D69 Q15)

**Trigger**: E72's board and families regenerated on the restated pairwise
layout (`results/e43-board-regen/`, PI ruling D69 Q15; Session 166, merged
`68efaad41`).

| Figure (E72's 23-condition board, 20 m) | Before | After |
|---|---|---|
| BH-significant of 253 | 199 | 198 |
| #1 against #2, q in the 253-pair family | 0.0503 | 0.0506 |
| #1 against #2, q in the full 325-pair family | 0.0488 | 0.0490 (already restated 2026-10-15) |

**What did NOT change**: 8 tiers; #2 still joins the leader in Tier 1; no
retained condition changes tier; the tables (2026-03-29 values).

**Commit**: see `git log` for this entry's date.

### 2026-10-15 — Restated-figures banner for the regenerated 20 m run (PI ruling D60 (3))

**Trigger**: the S164 restatement pass under PI ruling D65 (2)
(`reports/s164-agent-records/restatement-pass.md`, § 1.5), executing PI
rulings D60 (3) and D62 (2) (`planning/pi-decisions-2026-09-20.md`).
PR #37 (fix `4e9d659ab`;
`reports/s163-agent-records/d60-3-consensus-route.md`) made the
in-memory consensus route keep each cluster's contributing tiles, so a
consensus detection is scored on its origin sheet. The 20 m leaderboard
run (`run_pairwise_tests.py` and `apply_fdr_correction.py`) was
regenerated and committed at `08af04cf3`. This table is a hand-written
dated snapshot of that run (`reports/verification/generated-file-registry.json`,
rule `hw-paper-tables`), so, as under E72, its rows keep their values and
a banner carries the restatement; the sibling
`leaderboard-20m-annotated.md` received the same banner.

| Row | F1 @ 20 m before | after | P before → after | R before → after |
|---|---:|---:|---|---|
| #6 Pro H text 3/5 (N=5 cons.) | 0.840 (0.8404) | 0.843 (0.8429) | 0.918 → 0.921 | 0.775 → 0.777 |
| #9 FH text 26/30 (consensus) | 0.814 (0.8141) | 0.816 (0.8165) | 0.834 → 0.836 | 0.795 → 0.798 |
| #11 FH text 9/10 (consensus) | 0.797 (0.7968) | 0.799 (0.7991) | 0.800 → 0.803 | 0.793 → 0.795 |
| #12 FH text 5/5 (consensus) | 0.779 (0.7788) | 0.781 (0.7812) | 0.798 → 0.800 | 0.761 → 0.763 |
| #13 FH image 7/10 (consensus) | 0.750 (0.7500) | 0.752 (0.7524) | 0.778 → 0.780 | 0.724 → 0.726 |
| #14 FH image 3/5 (consensus) | 0.727 (0.7269) | 0.729 (0.7290) | 0.676 → 0.678 | 0.786 → 0.789 |
| #17 FM image 8/10 (consensus) | 0.680 (0.6803) | 0.682 (0.6825) | 0.640 → 0.642 | 0.726 → 0.729 |
| #18 FM image 4/5 (consensus) | 0.664 (0.6639) | 0.666 (0.6660) | 0.608 → 0.610 | 0.731 → 0.733 |
| #19 FM text T=0.7 29/30 | 0.661 (0.6611) | 0.663 (0.6632) | 0.602 → 0.604 | 0.733 → 0.736 |
| #20 FM text T=0.7 5/5 | 0.640 (0.6397) | 0.642 (0.6415) | 0.533 → 0.534 | 0.800 → 0.802 |
| #21 FM text T=0.7 10/10 | 0.633 (0.6332) | 0.635 (0.6352) | 0.562 → 0.564 | 0.724 → 0.726 |
| #22 Single-pass T=0 10/10 | 0.552 (0.5521) | 0.555 (0.5554) | 0.410 → 0.412 | 0.846 → 0.853; detections 898 → 901 |
| #23 Single-pass T=0 5/5 | 0.544 (0.5440) | 0.547 (0.5472) | 0.396 → 0.398 | 0.867 → 0.874; detections 951 → 954 |
| #24 FM text T=1.0 5/5 (void, E72) | 0.471 (0.4712) | 0.474 (0.4740) | 0.583 → 0.586 | 0.395 → 0.398 |
| #25 FM text T=1.0 22/30 (void, E72) | 0.467 (0.4670) | 0.469 (0.4694) | 0.499 → 0.501 | 0.439 → 0.441 |
| #26 FM text T=1.0 9/10 (void, E72) | 0.462 (0.4615) | 0.464 (0.4642) | 0.545 → 0.549 | 0.400 → 0.402 |
| #1 against #2: raw p; q | 0.0398; 0.048811 | 0.0398; 0.048996 | | |
| Image baseline + PV against FM text T=0.7 29/30: q | 0.04715 (significant) | 0.056875 (not significant) | | |
| Single-pass T=0 5/5 against FM text T=1.0 22/30: q | 0.050949 (not significant) | 0.049547 (significant) | | |

Source: `results/pairwise/leaderboard-20m/fdr/pairwise_results_fdr.json`
(`comparisons[]`: `f1_a`/`f1_b`, `precision_a`/`precision_b`,
`recall_a`/`recall_b`, `n_detections_a`/`n_detections_b`,
`p_value_raw`, `p_value_adj`, `significant`), read at `718d0ee08`
(before) and `4660c0549` (after). The tiers were checked by applying the
greedy-clique rule to both files.

**What did NOT change**: every proposer–verifier row
(#1 to #5, #8, #10 and #15), #7 and #16; 26 conditions, 325 tests,
265 significant, 9 tiers with the same members (#8 and #9 swap order inside Tier 3); #1 against #3
(raw p 0.0207, q 0.0263). The MCC, MCC CI, sensitivity and specificity
columns are tile-level metrics from evaluations this pass did not
re-run. The E72 banner and its reduced-board figures
(`results/e43-board-regen/`, not regenerated in this pass).

**Commit**: `08af04cf3` (the regenerated 20 m leaderboard run); this
document refresh in the restatement pass's document commit.

### 2026-08-02 — Superseded-figures banner (E72)

Banner added for rows #24 to #26, whose T=1.0 arm was scored over a
240-tile study against 487-tile bounds (protocol erratum E72, coverage
confound), with the 23-condition board's figures. Body unchanged.
Commit `2f3ef020a`.

### 2026-04-24 — Scope unification note

Note added naming the scope-unified gold-standard-v2 cell (F1 0.854 at
20 m) and why it is not a row. Commit `7ab7d7fa1`.

### 2026-03-29 — Original publication

Tier clustering of the 20 m leaderboard: 325 pairwise permutation tests
among 26 conditions, BH-corrected at q = 0.05, greedy-clique tiers, with
tile-level MCC added the same day. Commits `f859cd1ad`, `899bb39ef`,
`33db78e4a` and `f3bb8e46b`.
