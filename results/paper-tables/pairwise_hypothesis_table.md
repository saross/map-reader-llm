# Pairwise Hypothesis Test Results (30m buffer, FDR-corrected)

> **Last revised**: 2026-10-30 (E72's recomputed families regenerated on
> the restated layout, PI ruling D69 Q15: Group 7's 20 m flip reverses,
> q 0.0507 → 0.0483). Prior: 2026-10-15 (restated-figures banner added for the two
> hypothesis-family runs regenerated on the consensus route, PI ruling
> D60 (3); tables unchanged). Prior: 2026-08-02 (E72 — superseded-figures
> banner added). See [§ Changelog](#changelog) for revision history.
>
> **Restated figures (2026-10-15, D60 (3))**: the 32-pair families under
> `results/pairwise/30m/` and `results/pairwise/20m/` were regenerated with
> the consensus route that keeps each cluster's contributing tiles (PR #37).
> Fourteen consensus and single-pass cells rise by +0.0018 to +0.0031 F1 at
> 30 m; no proposer–verifier cell moves, nor does Pro image 3/5, so Group 6
> is unchanged. FH text 26/30 reads 0.828, FM text 29/30 0.672 and FH text
> 9/10 0.813, and Group 1's N=30 PV − consensus ΔF1 is 0.076 (0.0761; the
> table prints 0.079 for 0.0785). No verdict moves: the same 21 of 32 pairs
> are significant at 30 m and the same 23 at 20 m, and every 20 m
> agree/disagree mark holds. The largest move is Group 1's Pro text 3/5 + PV
> against Pro text 3/5 (ΔF1 0.0091 → 0.0066, p_adj 0.2569 → 0.4077). Group
> 7's N=30 vs N=10 (HIGH text) reads p_adj 0.0914 at 30 m (was 0.0872) and
> q 0.0464 at 20 m (was 0.0488). The E72 banner's recomputed families
> (`results/e43-board-regen/bh-families/`, including that row's q = 0.0507)
> predate the regeneration and were not re-run in this pass [2026-10-30:
> regenerated on the restated layout; that row now reads q = 0.0483,
> significant, D69 Q15]. The tables
> below keep their 2026-03-28 values; the changelog lists every moved row.
>
> **⚠ Superseded figures (2026-08-02, E72)**: the three Group 4 temperature
> rows (`T=0.7 vs T=1.0` at N=30, N=10 and N=5) pair a 487-tile arm against
> `outputs/h11/consensus-384-UNINTENDED-T1.0`, a 240-tile study scored against
> 487-tile bounds (coverage confound — see protocol-errata E43 correction block
> and E72); their ΔF1 of +0.193/+0.172/+0.168 understates the T=1.0 arm by
> ~0.17–0.19 F1 and the "3/3 significant" Group 4 summary does not stand. At
> matched 487-tile scope the contrast reverses sign and is not significant
> (−0.021 at N=5, −0.034 at N=10). Dropping them leaves a 23-member
> confirmatory family; the recomputed BH also flips Group 7's
> `N=30 vs N=10 (HIGH text)` at 20 m from significant (q = 0.0488) to
> non-significant (q = 0.0507) — the 30 m family is unchanged [2026-10-30: on
> the restated inputs (raw p 0.0375 → 0.0357) the recomputed q is 0.0483,
> significant, so the flip no longer holds; the full family's q is 0.0464]. The companion
> `pairwise_hypothesis_table.csv` carries the same superseded rows.
> Recomputed families: `results/e43-board-regen/bh-families/`. Matched-scope
> analysis: `results/e43-matched-temperature/`. Dated snapshot; body unchanged;
> do not cite the affected rows.

## Group 1

| Question | Condition A | Condition B | F1 A | F1 B | ΔF1 | p_adj | Sig | 20m |
|----------|-------------|-------------|------|------|-----|-------|-----|-----|
| PV on single-pass text | Text base + PV | Single-pass 5/5 | 0.832 | 0.554 | 0.278 | <0.0001 | *** | *** agree |
| PV on single-pass image | Image base + PV | Single-pass 5/5 | 0.782 | 0.554 | 0.228 | <0.0001 | *** | *** agree |
| PV vs consensus | FH text 4/5 + PV | FH text 5/5 | 0.891 | 0.788 | 0.102 | <0.0001 | *** | *** agree |
| PV verifier thinking | FH text 4/5 + med vf | FH text 5/5 | 0.885 | 0.788 | 0.097 | <0.0001 | *** | *** agree |
| PV vs consensus | FH text 16/30 + PV | FH text 26/30 | 0.904 | 0.826 | 0.079 | <0.0001 | *** | *** agree |
| PV vs consensus | FH text 9/10 + PV | FH text 9/10 | 0.869 | 0.811 | 0.059 | <0.0001 | *** | *** agree |
| PV vs consensus (image) | FH image 3/5 + PV | FH image 3/5 | 0.851 | 0.799 | 0.052 | 0.0004 | *** | *** agree |
| PV vs consensus (Pro) | Pro text 3/5 + PV | Pro text 3/5 | 0.865 | 0.855 | 0.009 | 0.2569 | ns | ns agree |

**Summary:** 7 significant / 8 total comparisons

## Group 2

| Question | Condition A | Condition B | F1 A | F1 B | ΔF1 | p_adj | Sig | 20m |
|----------|-------------|-------------|------|------|-----|-------|-----|-----|
| Text vs image (MINIMAL) | FM text 5/5 | FM image 4/5 | 0.647 | 0.724 | -0.077 | 0.0020 | ** | ns agree |
| Text vs image (PV) | FH text 4/5 + PV | FH image 3/5 + PV | 0.891 | 0.851 | 0.040 | 0.0173 | * | *** agree |
| Text vs image | FH text 5/5 | FH image 3/5 | 0.788 | 0.799 | -0.011 | 0.6055 | ns | * disagree |
| Text vs image (N=10) | FH text 9/10 | FH image 6/10 | 0.811 | 0.812 | -0.001 | 0.9561 | ns | ** disagree |

**Summary:** 2 significant / 4 total comparisons

## Group 3

| Question | Condition A | Condition B | F1 A | F1 B | ΔF1 | p_adj | Sig | 20m |
|----------|-------------|-------------|------|------|-----|-------|-----|-----|
| HIGH vs MINIMAL (text N=10) | FH text 9/10 | FM text 10/10 | 0.811 | 0.641 | 0.169 | <0.0001 | *** | *** agree |
| HIGH vs MINIMAL (text N=30) | FH text 26/30 | FM text 29/30 | 0.826 | 0.669 | 0.157 | <0.0001 | *** | *** agree |
| HIGH vs MINIMAL (text N=5) | FH text 5/5 | FM text 5/5 | 0.788 | 0.647 | 0.141 | <0.0001 | *** | *** agree |
| HIGH vs MINIMAL (image N=5) | FH image 3/5 | FM image 4/5 | 0.799 | 0.724 | 0.075 | <0.0001 | *** | *** agree |

**Summary:** 4 significant / 4 total comparisons

## Group 4

| Question | Condition A | Condition B | F1 A | F1 B | ΔF1 | p_adj | Sig | 20m |
|----------|-------------|-------------|------|------|-----|-------|-----|-----|
| T=0.7 vs T=1.0 (N=30) | FM text T=0.7 29/30 | FM text T=1.0 22/30 | 0.669 | 0.477 | 0.193 | <0.0001 | *** | *** agree |
| T=0.7 vs T=1.0 (N=10) | FM text T=0.7 10/10 | FM text T=1.0 9/10 | 0.641 | 0.469 | 0.172 | <0.0001 | *** | *** agree |
| T=0.7 vs T=1.0 (N=5) | FM text T=0.7 5/5 | FM text T=1.0 5/5 | 0.647 | 0.479 | 0.168 | 0.0002 | *** | *** agree |

**Summary:** 3 significant / 3 total comparisons

## Group 5

| Question | Condition A | Condition B | F1 A | F1 B | ΔF1 | p_adj | Sig | 20m |
|----------|-------------|-------------|------|------|-----|-------|-----|-----|
| Pro vs Flash (text consensus) | Pro text 3/5 | FH text 5/5 | 0.855 | 0.788 | 0.067 | 0.0016 | ** | ** agree |
| Pro vs Flash (PV text) | Pro text 3/5 + PV | FH text 4/5 + PV | 0.865 | 0.891 | -0.026 | 0.1400 | ns | ns agree |
| Pro vs Flash (image consensus) | Pro image 3/5 | FH image 3/5 | 0.821 | 0.799 | 0.022 | 0.2834 | ns | ns disagree |

**Summary:** 1 significant / 3 total comparisons

## Group 6

| Question | Condition A | Condition B | F1 A | F1 B | ΔF1 | p_adj | Sig | 20m |
|----------|-------------|-------------|------|------|-----|-------|-----|-----|
| Best vs runner-up 4 | FH text 16/30 + PV | Pro text 3/5 + PV | 0.904 | 0.865 | 0.040 | 0.0212 | * | * agree |
| Best vs runner-up 3 | FH text 16/30 + PV | FH text 9/10 + PV | 0.904 | 0.869 | 0.035 | 0.0054 | ** | * agree |
| Runner-up 1 vs 3 | FH text 4/5 + PV | FH text 9/10 + PV | 0.891 | 0.869 | 0.022 | 0.0212 | * | ns agree |
| Best vs runner-up 2 | FH text 16/30 + PV | FH text 4/5 + med vf | 0.904 | 0.885 | 0.019 | 0.1743 | ns | * agree |
| Best vs runner-up 1 | FH text 16/30 + PV | FH text 4/5 + PV | 0.904 | 0.891 | 0.014 | 0.2518 | ns | ns agree |
| Runner-up 1 vs 2 | FH text 4/5 + PV | FH text 4/5 + med vf | 0.891 | 0.885 | 0.006 | 0.4334 | ns | ns agree |

**Summary:** 3 significant / 6 total comparisons

## Group 7

| Question | Condition A | Condition B | F1 A | F1 B | ΔF1 | p_adj | Sig | 20m |
|----------|-------------|-------------|------|------|-----|-------|-----|-----|
| N=30 vs N=10 (MIN text) | FM text 29/30 | FM text 10/10 | 0.669 | 0.641 | 0.028 | 0.0009 | *** | *** agree |
| N=10 vs N=5 (HIGH text) | FH text 9/10 | FH text 5/5 | 0.811 | 0.788 | 0.022 | 0.0831 | ns | ns agree |
| N=30 vs N=10 (HIGH text) | FH text 26/30 | FH text 9/10 | 0.826 | 0.811 | 0.015 | 0.0872 | ns | * agree |
| N=10 vs N=5 (MIN text) | FM text 10/10 | FM text 5/5 | 0.641 | 0.647 | -0.006 | 0.6972 | ns | ns agree |

**Summary:** 1 significant / 4 total comparisons

## Changelog

### 2026-10-30 — E72's Group 7 flip reverses on the restated inputs (PI ruling D69 Q15)

**Trigger**: E72's board and families regenerated on the restated pairwise
layout (`results/e43-board-regen/`, PI ruling D69 Q15; Session 166, merged
`68efaad41`).

| Figure | Before | After |
|---|---|---|
| Group 7, N=30 vs N=10 (HIGH text), 20 m: raw p | 0.0375 | 0.0357 |
| Group 7, q in E72's 23-member family | 0.0507 (n.s.) | 0.0483 (significant) |
| 20 m confirmatory family, BH-significant of the 23 retained | 16 | 17 |

**What did NOT change**: the tables (2026-03-28 values); the full 26-member
family's verdict on Group 7 (significant, q 0.0464); the 30 m family; the
three superseded Group 4 rows.

**Commit**: see `git log` for this entry's date.

### 2026-10-15 — Restated-figures banner for the regenerated hypothesis families (PI ruling D60 (3))

**Trigger**: the S164 restatement pass under PI ruling D65 (2)
(`reports/s164-agent-records/restatement-pass.md`, § 1.5), executing PI
rulings D60 (3) and D62 (2) (`planning/pi-decisions-2026-09-20.md`).
PR #37 (fix `4e9d659ab`;
`reports/s163-agent-records/d60-3-consensus-route.md`) made the
in-memory consensus route keep each cluster's contributing tiles, so a
consensus detection is scored on its origin sheet. The 30 m and 20 m
hypothesis-family runs were regenerated and committed at `08af04cf3`.
This table is hand-written from those runs; its writer was never
retained (`reports/verification/generated-file-registry.json`, rule
`hw-paper-tables`), so its rows keep their values and a banner carries
the restatement. The March table rounds a few values differently from
its source (0.079 for 0.078486, 0.102 for 0.102541, 0.865 for
0.86445); the tables below give the source values.

Cells whose F1 @ 30 m moved (the source's labels):

| Cell | F1 before | after |
|---|---:|---:|
| Pro HIGH text 3-of-5 | 0.855 (0.8554) | 0.858 (0.8579) |
| Flash HIGH text 26-of-30 | 0.826 (0.8259) | 0.828 (0.8282) |
| Flash HIGH image 6-of-10 | 0.812 (0.8116) | 0.814 (0.8138) |
| Flash HIGH text 9-of-10 | 0.811 (0.8106) | 0.813 (0.8129) |
| Flash HIGH image 3-of-5 | 0.799 (0.7992) | 0.801 (0.8013) |
| Flash HIGH text 5-of-5 | 0.788 (0.7882) | 0.791 (0.7906) |
| Flash MIN image 4-of-5 | 0.724 (0.7244) | 0.727 (0.7265) |
| Flash MIN text 29-of-30 | 0.669 (0.6694) | 0.672 (0.6715) |
| Flash MIN text 5-of-5 | 0.647 (0.6471) | 0.649 (0.6489) |
| Flash MIN text 10-of-10 | 0.641 (0.6412) | 0.643 (0.6432) |
| Single-pass text 5-of-5 | 0.554 (0.5541) | 0.557 (0.5572) |
| Flash MIN text T=1.0 5-of-5 | 0.479 (0.4795) | 0.482 (0.4822) |
| Flash MIN text T=1.0 22-of-30 | 0.477 (0.4768) | 0.479 (0.4792) |
| Flash MIN text T=1.0 9-of-10 | 0.469 (0.4695) | 0.472 (0.4721) |

Comparisons whose ΔF1 moved (30 m; p_adj as the table prints it):

| Group | Comparison | ΔF1 before | after | p_adj before | after |
|---|---|---:|---:|---:|---:|
| 1 | Flash HIGH text 16-of-30 + PV vs Flash HIGH text 26-of-30 | +0.0785 | +0.0761 | <0.0001 | <0.0001 |
| 1 | Flash HIGH text 9-of-10 + PV vs Flash HIGH text 9-of-10 | +0.0585 | +0.0562 | <0.0001 | <0.0001 |
| 1 | Flash HIGH text 4-of-5 + PV vs Flash HIGH text 5-of-5 | +0.1025 | +0.1002 | <0.0001 | <0.0001 |
| 1 | Flash HIGH text 4-of-5 + medium vf vs Flash HIGH text 5-of-5 | +0.0967 | +0.0944 | <0.0001 | <0.0001 |
| 1 | Flash HIGH image 3-of-5 + PV vs Flash HIGH image 3-of-5 | +0.0519 | +0.0498 | 0.0004 | 0.0006 |
| 1 | Pro HIGH text 3-of-5 + PV vs Pro HIGH text 3-of-5 | +0.0091 | +0.0066 | 0.2569 | 0.4077 |
| 1 | Text baseline + PV vs Single-pass text 5-of-5 | +0.2779 | +0.2748 | <0.0001 | <0.0001 |
| 1 | Image baseline + PV vs Single-pass text 5-of-5 | +0.2281 | +0.2250 | <0.0001 | <0.0001 |
| 2 | Flash HIGH text 5-of-5 vs Flash HIGH image 3-of-5 | -0.0109 | -0.0107 | 0.6055 | 0.6068 |
| 2 | Flash HIGH text 9-of-10 vs Flash HIGH image 6-of-10 | -0.0010 | -0.0009 | 0.9561 | 0.9577 |
| 2 | Flash MIN text 5-of-5 vs Flash MIN image 4-of-5 | -0.0774 | -0.0776 | 0.0020 | 0.0020 |
| 3 | Flash HIGH text 5-of-5 vs Flash MIN text 5-of-5 | +0.1412 | +0.1417 | <0.0001 | <0.0001 |
| 3 | Flash HIGH text 9-of-10 vs Flash MIN text 10-of-10 | +0.1694 | +0.1697 | <0.0001 | <0.0001 |
| 3 | Flash HIGH text 26-of-30 vs Flash MIN text 29-of-30 | +0.1565 | +0.1567 | <0.0001 | <0.0001 |
| 3 | Flash HIGH image 3-of-5 vs Flash MIN image 4-of-5 | +0.0747 | +0.0748 | <0.0001 | <0.0001 |
| 4 | Flash MIN text T=0.7 5-of-5 vs Flash MIN text T=1.0 5-of-5 | +0.1676 | +0.1667 | 0.0002 | 0.0002 |
| 4 | Flash MIN text T=0.7 10-of-10 vs Flash MIN text T=1.0 9-of-10 | +0.1717 | +0.1711 | <0.0001 | <0.0001 |
| 4 | Flash MIN text T=0.7 29-of-30 vs Flash MIN text T=1.0 22-of-30 | +0.1927 | +0.1923 | <0.0001 | <0.0001 |
| 5 | Pro HIGH text 3-of-5 vs Flash HIGH text 5-of-5 | +0.0671 | +0.0673 | 0.0016 | 0.0015 |
| 5 | Pro HIGH image 3-of-5 vs Flash HIGH image 3-of-5 | +0.0220 | +0.0199 | 0.2834 | 0.3511 |
| 7 | Flash HIGH text 9-of-10 vs Flash HIGH text 5-of-5 | +0.0224 | +0.0223 | 0.0831 | 0.0930 |
| 7 | Flash HIGH text 26-of-30 vs Flash HIGH text 9-of-10 | +0.0153 | +0.0153 | 0.0872 | 0.0914 |
| 7 | Flash MIN text 10-of-10 vs Flash MIN text 5-of-5 | -0.0059 | -0.0057 | 0.6972 | 0.7010 |
| 7 | Flash MIN text 29-of-30 vs Flash MIN text 10-of-10 | +0.0282 | +0.0283 | 0.0009 | 0.0009 |

Group 7's N=30 vs N=10 (HIGH text) in detail: 30 m raw p
0.0671 → 0.0668; 20 m raw p
0.0375 → 0.0357 and q
0.0488 → 0.0464.

Source: `results/pairwise/30m/fdr/pairwise_results_fdr.json` and
`results/pairwise/20m/fdr/pairwise_results_fdr.json` (`comparisons[]`:
`f1_a`/`f1_b`, `delta_f1`, `p_value_raw`, `p_value_adj`,
`significant`), read at `718d0ee08` (before) and `4660c0549` (after).
The Group 4 rows are void under E72 whatever their values; their ΔF1
now reads +0.1667/+0.1711/+0.1923 against the banner's
+0.168/+0.172/+0.193.

**What did NOT change**: every Sig and 20 m mark, and so every group
summary (7/8, 2/4, 4/4, 3/3, 1/3, 3/6, 1/4); every proposer–verifier F1
and Pro image 3/5; Group 6 entirely; the 30 m and 20 m family sizes
(32 comparisons each); the E72 banner
and its recomputed families (`results/e43-board-regen/`, not regenerated
in this pass).

**Commit**: `08af04cf3` (the regenerated hypothesis-family runs); this
document refresh in the restatement pass's document commit.

### 2026-08-02 — Superseded-figures banner (E72)

Banner added for the three Group 4 temperature rows (protocol erratum
E72, coverage confound) and Group 7's 20 m flip in the 23-member
family. Body unchanged. Commit `2f3ef020a`.

### 2026-03-28 — Original publication

The 32 hypothesis-family comparisons at 30 m (Groups 1 to 7), with the
20 m verdict and direction beside each. Commit `71d81cd5e`.
