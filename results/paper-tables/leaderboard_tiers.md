# Leaderboard Tier Clustering (30m buffer, FDR-corrected)

> **Last revised**: 2026-10-30 (the E72 block's regenerated-board count
> updated, PI ruling D69 Q15: 178 significant, not 181). Prior: 2026-10-15
> (restated-figures banner added for the 30 m
> pairwise run regenerated on the consensus route, PI ruling D60 (3); tables
> unchanged). Prior: 2026-08-02 (E72 — superseded-figures banner added). See
> [§ Changelog](#changelog) for revision history.
>
> **Restated figures (2026-10-15, D60 (3))**: the 300-pair run under
> `results/pairwise/leaderboard-30m/` was regenerated with the consensus route
> that keeps each cluster's contributing tiles (PR #37). Sixteen consensus and
> single-pass rows rise by +0.0018 to +0.0032 F1; no proposer–verifier row
> moves. FH text 26/30 reads 0.828, Pro text 3/5 0.858 and FH text 5/5 0.791,
> and every row keeps its tier and its place within it. The nine tiers keep
> their members, but 240 of 300 pairs are now significant (was 243): Pro text
> 3/5 + PV against FH text 26/30 (q 0.0395 → 0.0510), FH image 3/5 + PV
> against FH text 9/10 (q 0.0458 → 0.0610), and Text base + PV against FH
> text 5/5 (q 0.0458 → 0.0567) no longer separate. The tables below keep
> their 2026-03-28 values; the changelog lists every moved row. The E72
> banner's reduced-board figures come from `results/e43-board-regen/`, which
> this pass did not regenerate.
>
> **⚠ Superseded figures (2026-08-02, E72)**: the rows `FM text T=1.0 5/5`
> (Tier 8), `FM text T=1.0 22/30` and `FM text T=1.0 9/10` (Tier 9) derive from
> `outputs/h11/consensus-384-UNINTENDED-T1.0`, a 240-tile study scored against
> 487-tile bounds (coverage confound — see protocol-errata E43 correction block
> and E72), and understate that arm by ~0.17–0.19 F1. With those three cells
> dropped the board has 22 conditions, 231 pairwise tests, 181 significant
> after BH (178 since the 2026-10-30 regeneration on the restated inputs), and
> **8 tiers**; Tier 9 disappears and no retained condition
> changes tier. The companion `leaderboard_tiers.csv` carries the same
> superseded rows. Regenerated board: `results/e43-board-regen/`.
> Matched-scope analysis: `results/e43-matched-temperature/`. Dated snapshot;
> body unchanged; do not cite the affected rows.

Conditions within the same tier are statistically indistinguishable
(all pairwise adjusted p-values ≥ 0.05).

**Scope unification note (2026-04-24)**: this document uses phase3a
condition labels and is not a mirror of
`results/leaderboard/era2/leaderboard_tiers_30m.md`, which uses the
h11-series cell naming. The Session 78 gold-standard-v2 scope-unified
cell at Era 2 (487-tile) scope reports F1=0.871 at 30 m
(`results/leaderboard/cells/gold-standard-v2-greedy-v1-487tile.json`).
It would sit in Tier 2 here on F1 but is not inserted as a distinct row
because the tier discussion focuses on phase3a matrix conditions with
matched pairwise permutation statistics. The Era 3 (327-tile) scope-pair
sibling (`gold-standard-v2-greedy-v1-327tile.json`) is intentionally
preserved for comparability with the Era 3 h8-v2 / h10-v2 / h12-v2
library-design artefacts.

## Tier 1 (F1: 0.885–0.904)

| Condition | F1 |
|-----------|------|
| FH text 16/30 + PV | 0.904 |
| FH text 4/5 + PV | 0.891 |
| FH text 4/5 + med vf | 0.885 |

## Tier 2 (F1: 0.851–0.869)

| Condition | F1 |
|-----------|------|
| FH text 9/10 + PV | 0.869 |
| Pro text 3/5 + PV | 0.865 |
| Pro text 3/5 | 0.855 |
| FH image 3/5 + PV | 0.851 |

## Tier 3 (F1: 0.799–0.832)

| Condition | F1 |
|-----------|------|
| Text base + PV | 0.832 |
| FH text 26/30 | 0.826 |
| Pro image 3/5 | 0.821 |
| FH image 6/10 | 0.812 |
| FH text 9/10 | 0.811 |
| FH image 3/5 | 0.799 |

## Tier 4 (F1: 0.782–0.788)

| Condition | F1 |
|-----------|------|
| FH text 5/5 | 0.788 |
| Image base + PV | 0.782 |

## Tier 5 (F1: 0.724–0.733)

| Condition | F1 |
|-----------|------|
| FM image 6/10 | 0.733 |
| FM image 4/5 | 0.724 |

## Tier 6 (F1: 0.647–0.669)

| Condition | F1 |
|-----------|------|
| FM text T=0.7 29/30 | 0.669 |
| FM text T=0.7 5/5 | 0.647 |

## Tier 7 (F1: 0.641)

| Condition | F1 |
|-----------|------|
| FM text T=0.7 10/10 | 0.641 |

## Tier 8 (F1: 0.479–0.563)

| Condition | F1 |
|-----------|------|
| Single-pass 10/10 | 0.563 |
| Single-pass 5/5 | 0.554 |
| FM text T=1.0 5/5 | 0.479 |

## Tier 9 (F1: 0.469–0.477)

| Condition | F1 |
|-----------|------|
| FM text T=1.0 22/30 | 0.477 |
| FM text T=1.0 9/10 | 0.469 |

## Changelog

### 2026-10-30 — E72 block: the regenerated board on the restated inputs (PI ruling D69 Q15)

**Trigger**: E72's board and families regenerated on the restated pairwise
layout (`results/e43-board-regen/`, PI ruling D69 Q15; Session 166, merged
`68efaad41`).

| Figure (E72's 22-condition board, 30 m) | Before | After |
|---|---|---|
| BH-significant of 231 | 181 | 178 |

Three retained pairs lose significance on the restated inputs (their raw p
moved), listed in `results/e43-board-regen/summary.md` § Changelog.

**What did NOT change**: 8 tiers; no retained condition changes tier; the
tables (2026-03-29 values).

**Commit**: see `git log` for this entry's date.

### 2026-10-15 — Restated-figures banner for the regenerated 30 m run (PI ruling D60 (3))

**Trigger**: the S164 restatement pass under PI ruling D65 (2)
(`reports/s164-agent-records/restatement-pass.md`, § 1.5), executing PI
rulings D60 (3) and D62 (2) (`planning/pi-decisions-2026-09-20.md`).
PR #37 (fix `4e9d659ab`;
`reports/s163-agent-records/d60-3-consensus-route.md`) made the
in-memory consensus route keep each cluster's contributing tiles, so a
consensus detection is scored on its origin sheet. The 30 m leaderboard
run was regenerated and committed at `08af04cf3`. This table is a
hand-written dated snapshot of that run
(`reports/verification/generated-file-registry.json`, rule
`hw-paper-tables`), so its rows keep their values and a banner carries
the restatement.

| Row | F1 @ 30 m before | after |
|---|---:|---:|
| Pro text 3/5 (Tier 2) | 0.855 (0.8554) | 0.858 (0.8579) |
| FH text 26/30 (Tier 3) | 0.826 (0.8259) | 0.828 (0.8282) |
| FH image 6/10 (Tier 3) | 0.812 (0.8116) | 0.814 (0.8138) |
| FH text 9/10 (Tier 3) | 0.811 (0.8106) | 0.813 (0.8129) |
| FH image 3/5 (Tier 3) | 0.799 (0.7992) | 0.801 (0.8013) |
| FH text 5/5 (Tier 4) | 0.788 (0.7882) | 0.791 (0.7906) |
| FM image 6/10 (Tier 5) | 0.733 (0.7332) | 0.735 (0.7352) |
| FM image 4/5 (Tier 5) | 0.724 (0.7244) | 0.727 (0.7265) |
| FM text T=0.7 29/30 (Tier 6) | 0.669 (0.6694) | 0.672 (0.6715) |
| FM text T=0.7 5/5 (Tier 6) | 0.647 (0.6471) | 0.649 (0.6489) |
| FM text T=0.7 10/10 (Tier 7) | 0.641 (0.6412) | 0.643 (0.6432) |
| Single-pass 10/10 (Tier 8) | 0.563 (0.5626) | 0.566 (0.5659) (detections 898 → 901) |
| Single-pass 5/5 (Tier 8) | 0.554 (0.5541) | 0.557 (0.5572) (detections 951 → 954) |
| FM text T=1.0 5/5 (Tier 8; void, E72) | 0.479 (0.4795) | 0.482 (0.4822) |
| FM text T=1.0 22/30 (Tier 9; void, E72) | 0.477 (0.4768) | 0.479 (0.4792) |
| FM text T=1.0 9/10 (Tier 9; void, E72) | 0.469 (0.4695) | 0.472 (0.4721) |
| Pro text 3/5 + PV against FH text 26/30: raw p; q | 0.0315; 0.03954 (significant) | 0.041; 0.051037 (not significant) |
| FH image 3/5 + PV against FH text 9/10: raw p; q | 0.0371; 0.045802 (significant) | 0.0506; 0.060964 (not significant) |
| Text base + PV against FH text 5/5: raw p; q | 0.0371; 0.045802 (significant) | 0.0465; 0.056707 (not significant) |

Source: `results/pairwise/leaderboard-30m/fdr/pairwise_results_fdr.json`
(`comparisons[]`: `f1_a`/`f1_b`, `n_detections_a`/`n_detections_b`,
`p_value_raw`, `p_value_adj`, `significant`), read at `718d0ee08`
(before) and `4660c0549` (after). The tiers were checked by applying the
greedy-clique rule to both files. The tier headings' F1 ranges move with
their rows (for example Tier 3 now spans 0.801 to 0.832).

**What did NOT change**: every proposer–verifier row (Text base + PV and
Image base + PV among them) and Pro image 3/5; 25 conditions and 300 tests; nine
tiers with the same members, in the same order; the E72 banner and its
reduced-board figures (`results/e43-board-regen/`, not regenerated in
this pass).

**Commit**: `08af04cf3` (the regenerated 30 m leaderboard run); this
document refresh in the restatement pass's document commit.

### 2026-08-02 — Superseded-figures banner (E72)

Banner added for the three `FM text T=1.0` rows (protocol erratum E72,
coverage confound), with the 22-condition board's figures. Body
unchanged. Commit `2f3ef020a`.

### 2026-04-24 — Scope unification note

Note added naming the scope-unified gold-standard-v2 cell (F1 0.871 at
30 m) and why it is not a row. Commit `7ab7d7fa1`.

### 2026-03-28 — Original publication

Tier clustering of the 30 m leaderboard: 25 conditions, BH-corrected
pairwise permutation tests, greedy-clique tiers. Commit `71d81cd5e`.
