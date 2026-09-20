# The final 55-map board @ 50 m — every run, carried and oracle (reference r2)

> **Last revised**: 2026-09-20 (tile-MCC oracle redefined as the
> optimum at each family's carried vote count — ten new addendum cells,
> the ten unconstrained ones superseded but kept; `IM-k4`
> vote-provenance note; the tiered board unchanged). See
> [§ Changelog](#changelog) for revision history.
> Card:
> `planning/55map-final-board-2026-08-27.md`. Reference:
> revision r2 (4,726 student + 278 extension + 14 audit-reviewed; card `planning/reference-revision-2026-09-06.md`).
> Instrument: round-robin tile-swap micro-F1 permutation (10000, seed 42) + BH q=0.05 + greedy-clique tiers (the GS chain).
> 512/595 pairs significant.

| rank | cell | basis | tier | group | cost | point | F1@50 | 95% CI | P@50 | R@50 | tile-MCC | n |
|---:|---|---|---:|---|---:|---|---:|---|---:|---:|---:|---:|
| 1 | ARM2-N5-oracle | oracle | 1 | a | — | (0.95, k5) | 0.8871 | [0.8794, 0.8943] | 0.8956 | 0.8788 | 0.715 | 4924 |
| 2 | ARM2-N3-oracle | oracle | 1 | ab | — | (0.95, k3) | 0.8848 | [0.8770, 0.8919] | 0.8780 | 0.8918 | 0.716 | 5097 |
| 3 | ARM2-N5-carried | carried | 2 | bc | — | (0.80, k5) | 0.8827 | [0.8749, 0.8899] | 0.8841 | 0.8814 | 0.706 | 5003 |
| 4 | FOURTH-N10-oracle | oracle | 2 | ab | — | (0.96, k9) | 0.8813 | [0.8736, 0.8886] | 0.9326 | 0.8354 | 0.736 | 4495 |
| 5 | FOURTH-N3-oracle | oracle | 3 | cd | — | (0.96, k3) | 0.8747 | [0.8670, 0.8820] | 0.9118 | 0.8406 | 0.738 | 4626 |
| 6 | FOURTH-N10-carried | carried | 3 | d | — | (0.98, k10) | 0.8728 | [0.8646, 0.8808] | 0.9522 | 0.8057 | 0.726 | 4246 |
| 7 | ARM1-N5-oracle | oracle | 3 | d | — | (0.15, k5) | 0.8727 | [0.8644, 0.8803] | 0.9107 | 0.8378 | 0.715 | 4616 |
| 8 | ARM1-N3-oracle | oracle | 3 | d | — | (0.15, k3) | 0.8705 | [0.8625, 0.8780] | 0.8929 | 0.8491 | 0.718 | 4772 |
| 9 | ARM2-N1-oracle | oracle | 4 | e | — | (0.98, k1) | 0.8610 | [0.8534, 0.8684] | 0.8608 | 0.8613 | 0.742 | 5021 |
| 10 | B-N10-oracle | oracle | 4 | e | $174 | (0.20, k9) | 0.8560 | [0.8477, 0.8638] | 0.8909 | 0.8236 | 0.712 | 4639 |
| 11 | ARM1-N5-carried | carried | 4 | efg | — | (0.10, k5) | 0.8551 | [0.8466, 0.8631] | 0.8378 | 0.8731 | 0.665 | 5229 |
| 12 | B-N5-oracle | oracle | 5 | fg | $97 | (0.20, k5) | 0.8516 | [0.8430, 0.8596] | 0.8938 | 0.8133 | 0.710 | 4566 |
| 13 | B-N3-oracle | oracle | 5 | g | $65 | (0.20, k3) | 0.8507 | [0.8424, 0.8586] | 0.8726 | 0.8298 | 0.713 | 4772 |
| 14 | B-N5-carried | carried | 5 | fg | $97 | (0.15, k5) | 0.8503 | [0.8418, 0.8583] | 0.8756 | 0.8264 | 0.701 | 4736 |
| 15 | B-N10-carried | carried | 5 | fgh | $174 | (0.15, k10) | 0.8497 | [0.8410, 0.8579] | 0.8981 | 0.8063 | 0.698 | 4505 |
| 16 | B-N3-carried | carried (post-hoc) | 6 | fhi | $65 | (0.15, k3) | 0.8477 | [0.8395, 0.8556] | 0.8517 | 0.8438 | 0.702 | 4971 |
| 17 | A-N10-oracle | oracle | 6 | hij | $104 | (0.15, k7) | 0.8419 | [0.8330, 0.8502] | 0.8763 | 0.8101 | 0.695 | 4639 |
| 18 | ARM1-N1-oracle | oracle | 6 | hijk | — | (0.20, k1) | 0.8413 | [0.8332, 0.8492] | 0.8251 | 0.8581 | 0.725 | 5219 |
| 19 | T03-oracle | oracle | 6 | ijkl | $261 | (0.20, k3) | 0.8399 | [0.8311, 0.8483] | 0.8625 | 0.8185 | 0.696 | 4762 |
| 20 | A-N10-carried | carried | 7 | km | $104 | (0.15, k8) | 0.8391 | [0.8302, 0.8478] | 0.8901 | 0.7937 | 0.693 | 4475 |
| 21 | A-N5-oracle | oracle | 7 | km | $60 | (0.15, k4) | 0.8383 | [0.8294, 0.8468] | 0.8767 | 0.8031 | 0.691 | 4597 |
| 22 | A-N5-carried | carried | 7 | km | $60 | (0.15, k4) | 0.8383 | [0.8294, 0.8468] | 0.8767 | 0.8031 | 0.691 | 4597 |
| 23 | TH7-oracle | oracle | 7 | jkl | $207 | (0.15, k3) | 0.8380 | [0.8287, 0.8467] | 0.8583 | 0.8187 | 0.679 | 4786 |
| 24 | FOURTH-N1-oracle | oracle | 7 | jklmn | — | (0.96, k1) | 0.8352 | [0.8272, 0.8428] | 0.8102 | 0.8617 | 0.747 | 5337 |
| 25 | A-N3-oracle | oracle | 8 | ln | $41 | (0.20, k2) | 0.8321 | [0.8233, 0.8405] | 0.8513 | 0.8137 | 0.702 | 4796 |
| 26 | A-N3-carried | carried (post-hoc) | 8 | ln | $41 | (0.15, k3) | 0.8307 | [0.8217, 0.8395] | 0.8891 | 0.7796 | 0.688 | 4400 |
| 27 | T03-k4 | carried | 8 | mno | $261 | (0.15, k4) | 0.8294 | [0.8199, 0.8384] | 0.8931 | 0.7742 | 0.669 | 4350 |
| 28 | UPL-oracle | oracle | 8 | no | $58 | (0.15, k5) | 0.8274 | [0.8174, 0.8367] | 0.8897 | 0.7732 | 0.669 | 4361 |
| 29 | A-N1-oracle | oracle | 9 | op | $21 | (0.20, k1) | 0.8227 | [0.8139, 0.8313] | 0.8344 | 0.8113 | 0.701 | 4879 |
| 30 | TH7-k4 | carried | 9 | pq | $207 | (0.15, k4) | 0.8162 | [0.8059, 0.8261] | 0.8999 | 0.7467 | 0.665 | 4164 |
| 31 | TM-oracle | oracle | 10 | qr | $23 | (0.20, k3) | 0.8103 | [0.7999, 0.8204] | 0.8944 | 0.7407 | 0.662 | 4156 |
| 32 | B-N1-oracle | oracle | 10 | r | $31 | (0.20, k1) | 0.8013 | [0.7925, 0.8096] | 0.7561 | 0.8521 | 0.709 | 5655 |
| 33 | IM-oracle | oracle | 10 | r | $195 | (0.15, k3) | 0.8008 | [0.7907, 0.8102] | 0.8297 | 0.7738 | 0.711 | 4680 |
| 34 | TM-k4 | carried | 11 | s | $23 | (0.15, k4) | 0.7826 | [0.7713, 0.7936] | 0.8994 | 0.6927 | 0.640 | 3865 |
| 35 | IM-k4 | carried | 12 | t | $195 | (0.15, k4) | 0.7398 | [0.7276, 0.7519] | 0.8941 | 0.6309 | 0.654 | 3541 |

**Reading the groups**: `tier` is the greedy-clique tier (disjoint
bands); `group` is the compact letter display — cells sharing ANY
letter are statistically indistinguishable under the BH-adjusted
pairwise tests, so letters show the overlaps the disjoint tiers
cannot. `cost` is the run's audited all-in flex spend (full
basis); a run's carried and oracle cells share it. See
`significance-groups.png` for the dot-and-CI plot and the full
pairwise significance matrix.

## Runs: as run versus theoretical maximum

One row per run: the carried ("as run / GS-chosen") result and
the oracle (standardised-reference argmax within the verified
sweep space). Tiers from the 35-cell board above.

| run | carried F1@50 (tier) | oracle F1@50 (tier) | oracle point |
|---|---|---|---|
| B, N = 10 (384/50 %) | 0.8497 (T5) | 0.8560 (T4) | (0.20, k9) |
| B, N = 5 | 0.8503 (T5) | 0.8516 (T5) | (0.20, k5) |
| B, N = 3 | 0.8477 (T6) | 0.8507 (T5) | (0.20, k3) |
| B, N = 1 | — | 0.8013 (T10) | (0.20, k1) |
| A, N = 10 (384/33 %) | 0.8391 (T7) | 0.8419 (T6) | (0.15, k7) |
| A, N = 5 | 0.8383 (T7) | 0.8383 (T7) | (0.15, k4) |
| A, N = 3 | 0.8307 (T8) | 0.8321 (T8) | (0.20, k2) |
| A, N = 1 | — | 0.8227 (T9) | (0.20, k1) |
| T0.3 (HIGH, K = 5) | 0.8294 (T8) | 0.8399 (T6) | (0.20, k3) |
| T0.7 (HIGH, K = 5) | 0.8162 (T9) | 0.8380 (T7) | (0.15, k3) |
| min-uplift (K = 10) | — | 0.8274 (T8) | (0.15, k5) |
| text-min (K = 5) | 0.7826 (T11) | 0.8103 (T10) | (0.20, k3) |
| image (HIGH, K = 5) — as shipped (k3) | 0.8008 (T10) | 0.8008 (T10) | (0.15, k3) |
| image comparability (k4, E82) | 0.7398 (T12) | — | — |
| 3.7 arm 1: 3.7 proposer + G3 verifier, N = 5 | 0.8551 (T4) | 0.8727 (T3) | (0.15, k5) |
| 3.7 arm 1, N = 3 | — | 0.8705 (T3) | (0.15, k3) |
| 3.7 arm 1, N = 1 | — | 0.8413 (T6) | (0.20, k1) |
| 3.7 arm 2: all-3.7 stack, N = 5 | 0.8827 (T2) | 0.8871 (T1) | (0.95, k5) |
| 3.7 arm 2, N = 3 | — | 0.8848 (T1) | (0.95, k3) |
| 3.7 arm 2, N = 1 | — | 0.8610 (T4) | (0.98, k1) |
| fourth cell: B K = 10 union + 3.7 verifier | 0.8728 (T3) | 0.8813 (T2) | (0.96, k9) |
| fourth cell, N = 3 | — | 0.8747 (T3) | (0.96, k3) |
| fourth cell, N = 1 | — | 0.8352 (T7) | (0.96, k1) |

PI ruling 2026-08-28 on the image rows: the real-world column
shows the cell the image run actually SHIPPED (k3 — which for
image coincides with the standardised-reference argmax, so its
carried and oracle entries are the same cell); IM-k4 remains on
the board as E82's like-for-like comparability derivation.

## Cost efficiency: what a dollar buys

One row per run at its DEPLOYMENT basis (carried where one
exists, otherwise the rung oracle, marked). `$/mound` is the
run's full flex cost per true-positive mound at 50 m — the
project's established per-mound economics. `marginal $/+0.01 F1`
prices each step UP the cost-sorted Pareto frontier (— =
dominated: a cheaper run scores higher). Plain F1-per-dollar is
deliberately omitted — it is maximised by the cheapest run
almost regardless of quality.

| run | basis | cost | F1@50 (tier) | TP mounds | $/mound | frontier | marginal $/+0.01 F1 |
|---|---|---:|---|---:|---:|---|---:|
| A, N = 1 | oracle | $21 | 0.8227 (T9) | 4,071 | $0.0050 | YES | — |
| text-min (K = 5) | carried | $23 | 0.7826 (T11) | 3,476 | $0.0067 | — | — |
| B, N = 1 | oracle | $31 | 0.8013 (T10) | 4,276 | $0.0072 | — | — |
| A, N = 3 | carried (post-hoc) | $41 | 0.8307 (T8) | 3,912 | $0.0105 | YES | $25.86 |
| min-uplift (K = 10) | oracle | $58 | 0.8274 (T8) | 3,880 | $0.0149 | — | — |
| A, N = 5 | carried | $60 | 0.8383 (T7) | 4,030 | $0.0148 | YES | $24.38 |
| B, N = 3 | carried (post-hoc) | $65 | 0.8477 (T6) | 4,234 | $0.0155 | YES | $6.10 |
| B, N = 5 | carried | $97 | 0.8503 (T5) | 4,147 | $0.0234 | YES | $122.08 |
| A, N = 10 (384/33 %) | carried | $104 | 0.8391 (T7) | 3,983 | $0.0261 | — | — |
| B, N = 10 (384/50 %) | carried | $174 | 0.8497 (T5) | 4,046 | $0.0429 | — | — |
| image (HIGH, K = 5) — as shipped (k3) | as-shipped (k3) | $195 | 0.8008 (T10) | 3,883 | $0.0503 | — | — |
| image comparability (k4, E82) | comparability (k4) | $195 | 0.7398 (T12) | 3,166 | $0.0617 | — | — |
| T0.7 (HIGH, K = 5) | carried | $207 | 0.8162 (T9) | 3,747 | $0.0554 | — | — |
| T0.3 (HIGH, K = 5) | carried | $261 | 0.8294 (T8) | 3,885 | $0.0672 | — | — |

## Post-hoc: the emergent N = 3 carried cells

The `A-N3-carried` and `B-N3-carried` cells are **emergent
post-hoc nominations**, not registered claims: the card carried
operating points only at N = 5 and N = 10, so no N = 3 point was
nominated before launch. They are on the board because the
question "could the N = 3 configuration have been specified in
advance?" turns out to have a documented answer: the committed
GS stride ladder (`results/stride-2026-08-25/
plateau_analyses.json`, built before the 55-map launch) had
already selected **(0.15, k3-of-3) for BOTH geometries** at
N = 3. These cells simply evaluate that pre-existing GS
selection at deployment — the same derivation discipline as the
registered P2/P4 points, applied one rung further down. The
distinction that matters: the GS selection is pre-launch and
committed; the DECISION to evaluate it is post-hoc (2026-08-28,
PI-directed), motivated by the N = 3 oracle's position on the
cost frontier. Read their tiers and group letters accordingly —
instructive, not confirmatory. A registered replication (e.g.
nominating N = 3 in any future deployment card, or the
retro-N = 3 exploration of other runs the PI has flagged) is
the honest path to promoting this rung.

<!-- BEGIN board-addendum — generated by scripts/final_board_addendum_render.py; edit the script -->
## Addendum: post-hoc cells beside the tiered board

The 35-cell table at the head of this document is the **signed** board:
its greedy-clique tiers and its 595-pair Benjamini–Hochberg (BH) family
were computed over exactly those cells. The cells below were
materialised and scored afterwards on the same instrument —
`scripts/evaluate_detections.py`, reference r2, the 8,541-tile
evaluation frame, 14 buffers, tile-level bias-corrected and accelerated
(BCa) bootstrap of 10,000 draws at seed 42, `--mcc` — but the board was
**not** re-tiered for them (PI ruling 2026-09-13, carried forward
2026-09-20). They therefore carry no tier and no group letter, and they
are **post-hoc** nominations, not registered claims. Read them as point
estimates with intervals beside the tiered rows; a difference between an
addendum row and a tiered row has not been through the board's pairwise
family.

`FOURTH-N5-oracle` sits off the tiered board for the same reason and is
not repeated here: it is a tiered-board-eligible oracle cell whose
scored evaluation is committed at
`cells/FOURTH-N5-oracle/evaluation.json` and whose condition is
registered, but the board was not rebuilt when it landed on 2026-09-13.

**Carried-analogue cells** (`carried-analogue (post-hoc)`) take their
family's top-rung GS-carried probability — ARM1 (0.10, k5), ARM2
(0.80, k5), FOURTH (0.98, k10) — and apply that same threshold downward
at a lower rung, with `k` set to the rung's own N. The canonical grid
board already published this construction for the two arms
(`results/gemini37-55map-2026-08-31/grid-board/grid_board.json`,
`basis: "carried-analogue"`); it was never carried onto the r2 board, so
until 2026-09-20 an image *carried* cell at K = 1 or K = 3 could only be
compared with a text *oracle*, which flatters the text track and
understates the image-minus-text gap at K = 1 by a factor of 2.4
(`reports/comparability-inventory-37-runs-2026-09-20.md` § 3.2).

**MCC-oracle cells at the carried k**
(`mcc-oracle at carried k (post-hoc, 2026-09-20)`) are the tile-MCC
optimum over the probability threshold **with the vote count pinned to
the family's carried `k`** — the counterpart of the F1-argmax `-oracle`
cells already on the board, asked of the same configuration. The image
campaigns publish an `mcc_oracle` for every rung; the text track and the
fourth cell had none, because the board's sweep record carried micro-F1
only, so no MCC comparison across the two tracks was possible (§ 1.2,
§ 3.7 of the same inventory). The sweep record now carries the tile
confusion per point, and each family's `mcc_argmax_at_carried_k` in
`sweeps.json` names the point, its `carried_k` and the carried cell that
fixed it (`carried_k_source`). Read each row's F1@50 beside its
tile-MCC before quoting it.

| cell | basis | point | F1@50 | 95% CI | P@50 | R@50 | tile-MCC | 95% CI | n |
|---|---|---|---:|---|---:|---:|---:|---|---:|
| ARM2-N5-mcc-oracle-k5 | mcc-oracle at carried k | (0.96, k5) | 0.8821 | [0.8741, 0.8897] | 0.9466 | 0.8258 | 0.7291 | [0.7167, 0.7421] | 4378 |
| ARM2-N3-mcc-oracle-k3 | mcc-oracle at carried k | (0.96, k3) | 0.8818 | [0.8740, 0.8893] | 0.9327 | 0.8362 | 0.7326 | [0.7203, 0.7457] | 4499 |
| ARM2-N3-carried | carried-analogue | (0.80, k3) | 0.8802 | [0.8722, 0.8873] | 0.8658 | 0.8950 | 0.7076 | [0.6929, 0.7225] | 5187 |
| FOURTH-N5-mcc-oracle-k5 | mcc-oracle at carried k | (0.96, k5) | 0.8758 | [0.8679, 0.8832] | 0.9335 | 0.8248 | 0.7326 | [0.7200, 0.7453] | 4434 |
| FOURTH-N5-carried | carried-analogue | (0.98, k5) | 0.8754 | [0.8675, 0.8829] | 0.9334 | 0.8242 | 0.7322 | [0.7196, 0.7450] | 4431 |
| FOURTH-N3-mcc-oracle-k3 | mcc-oracle at carried k | (0.96, k3) | 0.8747 | [0.8670, 0.8820] | 0.9118 | 0.8406 | 0.7376 | [0.7250, 0.7504] | 4626 |
| FOURTH-N3-carried | carried-analogue | (0.98, k3) | 0.8744 | [0.8667, 0.8817] | 0.9117 | 0.8400 | 0.7372 | [0.7246, 0.7500] | 4623 |
| FOURTH-N10-mcc-oracle-k10 | mcc-oracle at carried k | (0.96, k10) | 0.8732 | [0.8650, 0.8811] | 0.9522 | 0.8063 | 0.7269 | [0.7142, 0.7394] | 4249 |
| ARM1-N5-mcc-oracle-k5 | mcc-oracle at carried k | (0.20, k5) | 0.8688 | [0.8603, 0.8767] | 0.9218 | 0.8216 | 0.7196 | [0.7061, 0.7331] | 4473 |
| ARM1-N3-mcc-oracle-k3 | mcc-oracle at carried k | (0.20, k3) | 0.8676 | [0.8596, 0.8755] | 0.9057 | 0.8326 | 0.7236 | [0.7098, 0.7371] | 4613 |
| ARM2-N1-mcc-oracle-k1 | mcc-oracle at carried k | (0.96, k1) | 0.8610 | [0.8533, 0.8683] | 0.8606 | 0.8613 | 0.7422 | [0.7298, 0.7551] | 5022 |
| ARM1-N3-carried | carried-analogue | (0.10, k3) | 0.8469 | [0.8382, 0.8549] | 0.8110 | 0.8860 | 0.6591 | [0.6430, 0.6751] | 5482 |
| ARM2-N1-carried | carried-analogue | (0.80, k1) | 0.8459 | [0.8380, 0.8532] | 0.7805 | 0.9233 | 0.7073 | [0.6920, 0.7222] | 5936 |
| ARM1-N1-mcc-oracle-k1 | mcc-oracle at carried k | (0.20, k1) | 0.8413 | [0.8332, 0.8492] | 0.8251 | 0.8581 | 0.7246 | [0.7109, 0.7384] | 5219 |
| FOURTH-N1-mcc-oracle-k1 | mcc-oracle at carried k | (0.96, k1) | 0.8352 | [0.8272, 0.8428] | 0.8102 | 0.8617 | 0.7471 | [0.7343, 0.7596] | 5337 |
| FOURTH-N1-carried | carried-analogue | (0.98, k1) | 0.8348 | [0.8269, 0.8425] | 0.8101 | 0.8611 | 0.7466 | [0.7340, 0.7592] | 5334 |
| ARM1-N1-carried | carried-analogue | (0.10, k1) | 0.7859 | [0.7767, 0.7947] | 0.6890 | 0.9145 | 0.6178 | [0.6006, 0.6342] | 6660 |

### Superseded: the unconstrained tile-MCC optima

Until 2026-09-20 the board's MCC oracle was the tile-MCC argmax over a
family's **whole** achievable grid, free to choose the vote count as
well as the probability threshold. Every one of the board's 23 families
put that optimum at the **lowest vote count its sweep offers**: every
family whose rungs reach down to a single vote collapsed to k = 1, and
the five incumbents, whose sweeps floor at k = 3, sat on that floor. It
buys a few hundredths of tile-MCC. Across the thirteen families whose
optimum drops from a multi-vote F1 oracle to a single vote it costs
**0.054 (A-N3) to 0.181 (B-N10) of micro-F1@50** against that family's
own F1 oracle (PI decision log D6a, 2026-09-20, states the range as
0.06 to 0.18). The reason is structural, not incidental:
tile-MCC asks only whether a tile was hit at all, so over-generation is
nearly free in that currency and expensive in F1. An unconstrained MCC
oracle is therefore not a like-for-like companion of the F1 oracle, and
the PI redefined the board's MCC oracle on 2026-09-20 as the optimum at
the family's carried vote count (the rows in the table above). The ten
cells below are the superseded selection. They are kept — materialised,
scored, and listed here — because the collapse is a recorded property of
the metric on this corpus, and these are the evidence for it. Do not
quote them as the board's MCC oracle.

| cell | basis | point | F1@50 | 95% CI | P@50 | R@50 | tile-MCC | 95% CI | n |
|---|---|---|---:|---|---:|---:|---:|---|---:|
| ARM2-N1-mcc-oracle | mcc-oracle (unconstrained k) | (0.96, k1) | 0.8610 | [0.8533, 0.8683] | 0.8606 | 0.8613 | 0.7422 | [0.7298, 0.7551] | 5022 |
| ARM1-N1-mcc-oracle | mcc-oracle (unconstrained k) | (0.20, k1) | 0.8413 | [0.8332, 0.8492] | 0.8251 | 0.8581 | 0.7246 | [0.7109, 0.7384] | 5219 |
| FOURTH-N1-mcc-oracle | mcc-oracle (unconstrained k) | (0.96, k1) | 0.8352 | [0.8272, 0.8428] | 0.8102 | 0.8617 | 0.7471 | [0.7343, 0.7596] | 5337 |
| ARM2-N3-mcc-oracle | mcc-oracle (unconstrained k) | (0.96, k1) | 0.8245 | [0.8164, 0.8322] | 0.7804 | 0.8739 | 0.7475 | [0.7352, 0.7604] | 5619 |
| ARM2-N5-mcc-oracle | mcc-oracle (unconstrained k) | (0.96, k1) | 0.8055 | [0.7974, 0.8137] | 0.7439 | 0.8782 | 0.7487 | [0.7365, 0.7617] | 5924 |
| ARM1-N3-mcc-oracle | mcc-oracle (unconstrained k) | (0.40, k1) | 0.7979 | [0.7895, 0.8063] | 0.7747 | 0.8224 | 0.7303 | [0.7172, 0.7436] | 5327 |
| FOURTH-N3-mcc-oracle | mcc-oracle (unconstrained k) | (0.96, k1) | 0.7798 | [0.7714, 0.7881] | 0.7005 | 0.8792 | 0.7514 | [0.7388, 0.7640] | 6298 |
| ARM1-N5-mcc-oracle | mcc-oracle (unconstrained k) | (0.40, k1) | 0.7787 | [0.7701, 0.7871] | 0.7363 | 0.8262 | 0.7308 | [0.7175, 0.7443] | 5631 |
| FOURTH-N5-mcc-oracle | mcc-oracle (unconstrained k) | (0.96, k1) | 0.7488 | [0.7400, 0.7573] | 0.6486 | 0.8856 | 0.7555 | [0.7425, 0.7679] | 6852 |
| FOURTH-N10-mcc-oracle | mcc-oracle (unconstrained k) | (0.96, k1) | 0.7025 | [0.6934, 0.7115] | 0.5792 | 0.8926 | 0.7567 | [0.7438, 0.7694] | 7733 |

<!-- END board-addendum -->
## Provenance and gates

- Stage 1 (`final_board_sweeps.py --reference r2`): sweep on
  reference r2 across 22 families; every gate (G4
  scorer, family identity, mechanism triples, A/B and 3.7 geometry)
  pinned to the r1 reference and passed — the sweep does not run
  otherwise. Oracle argmaxes are this reference's own.
- Stage 2: `evaluate_detections.py`, 14 buffers, tile-level BCa
  bootstrap 10,000 / seed 42, `--mcc`, `--require-clean-inputs`,
  per cell (`r2_score_cells.py --stage board`).
- Stage 3 (this build): G3 board-regression gate — the 8-cell
  committed r1 board reproduced exactly on r1 (f1, all 28
  pairwise p-values, tiers) before this board was assembled;
  per-cell mechanism bound 0.003. Coincidence gates:
  - TH7-oracle: coincides with the committed set; evaluation reproduced (0.8380)
  - IM-oracle: coincides with the committed set; evaluation reproduced (0.8008)
  - UPL-oracle: coincides with the committed set; evaluation reproduced (0.8274)
- Incumbent oracles are best-within-VERIFIED-space (vote ≥ 3
  shells / the ≥ 3-of-10 band); A/B oracles search the full
  vote ≥ 1 unions. N = 1/3 rungs are oracle-only (no carried
  point was ever registered there).

## Changelog

### 2026-09-20 — The tile-MCC oracle redefined: the optimum at the carried k

**Refresh trigger**: the tile-MCC oracle added earlier the same day was the
argmax over a family's **whole** achievable grid, vote count included, and
every one of the board's 23 families put it at the lowest vote count its
sweep offers (PI decision log D6a). That is a vote-threshold choice wearing
a metric's name, not a companion to the F1 oracle. PI ruling 2026-09-20.

**What changed**: the board's tile-MCC oracle is now the optimum over
`prob_t` with `min_votes` **pinned to the family's carried vote count**.
`sweeps.json` gains `mcc_argmax_at_carried_k`, `carried_k` and
`carried_k_source` for all 23 families, computed from the committed sweep
CSVs with **no re-sweep** — the rows already carried `tile_mcc` per point,
so the new oracle is a different argmax over unchanged evidence — plus a
`_README` and an `mcc_carried_k_families` index. Twenty families have a
carried cell on this board and so a carried k; `UPL`, `A-N1` and `B-N1`
have none and record `"no carried k"`. Ten new cells,
`ARM1-N{1,3,5}-mcc-oracle-k{1,3,5}`, `ARM2-N{1,3,5}-mcc-oracle-k{1,3,5}`
and `FOURTH-N{1,3,5,10}-mcc-oracle-k{1,3,5,10}`, were materialised, gated
and scored on the board's own stage-2 recipe.

**Numbers that moved — the ten addendum MCC-oracle rows.** The superseded
cells keep their own numbers and their own rows; what moved is which cell
the board calls its MCC oracle.

| family | superseded point | its F1@50 | its tile-MCC | carried-k point | its F1@50 | its tile-MCC |
|---|---|---:|---:|---|---:|---:|
| ARM1-N1 | (0.20, k1) | 0.8413 | 0.7246 | (0.20, k1) | 0.8413 | 0.7246 |
| ARM1-N3 | (0.40, k1) | 0.7979 | 0.7303 | (0.20, k3) | 0.8676 | 0.7236 |
| ARM1-N5 | (0.40, k1) | 0.7787 | 0.7308 | (0.20, k5) | 0.8688 | 0.7196 |
| ARM2-N1 | (0.96, k1) | 0.8610 | 0.7422 | (0.96, k1) | 0.8610 | 0.7422 |
| ARM2-N3 | (0.96, k1) | 0.8245 | 0.7475 | (0.96, k3) | 0.8818 | 0.7326 |
| ARM2-N5 | (0.96, k1) | 0.8055 | 0.7487 | (0.96, k5) | 0.8821 | 0.7291 |
| FOURTH-N1 | (0.96, k1) | 0.8352 | 0.7471 | (0.96, k1) | 0.8352 | 0.7471 |
| FOURTH-N3 | (0.96, k1) | 0.7798 | 0.7514 | (0.96, k3) | 0.8747 | 0.7376 |
| FOURTH-N5 | (0.96, k1) | 0.7488 | 0.7555 | (0.96, k5) | 0.8758 | 0.7326 |
| FOURTH-N10 | (0.96, k1) | 0.7025 | 0.7567 | (0.96, k10) | 0.8732 | 0.7269 |

The three N = 1 rungs offer one vote count, so the two definitions coincide
there and the detections files are byte-identical (SHA-256). Across the
seven that move, pinning the vote count gives up 0.0067 to 0.0298 of
tile-MCC and recovers 0.0573 to 0.1707 of micro-F1 @ 50 m.

**Gates**: each cell's detection count reproduces its committed sweep row
exactly; re-scoring each materialised subset through the sweep's own scorer
reproduces the row's detection `tp`/`fp`/`fn` **and** its four tile counts
exactly; and each scored `evaluation.json` reproduces the row's F1 @ 50 m
and tile-MCC to four decimal places, end to end on all ten cells.

**What did NOT change**: the 35-cell tiered board — rows, values, tiers,
group letters, the 595-pair Benjamini–Hochberg family and
`significance-groups.png`. `scripts/final_board_build.py` was not run. The
ten unconstrained cells stay on disk with their committed evaluations,
relabelled `mcc-oracle, unconstrained k (post-hoc, superseded 2026-09-20)`
and tabled in the addendum's
[§ Superseded](#superseded-the-unconstrained-tile-mcc-optima) sub-block:
the collapse is the evidence for the redefinition. `cells_manifest.json`
grows 53 → 63.

**Commits**: `481d63be8` (sweep-record selector + tests), `539372938`
(the record), `836466ff2` (gate fix + tests), `681b4e246` (detections +
manifest), plus the evaluations and this render.

### 2026-09-20 — Correction note: `IM-k4`'s vote provenance

**Refresh trigger**: the PI asked why the June image run's consensus file
and its crop manifest disagree on `vote_count`
(`results/im-june-pool-grid-2026-09-20/findings.md` § 7, commit
`f859646ba`).

**The note**: row 35's `IM-k4` detections were filtered at
`vote_count >= 4` on the June run's **crop manifest**, whose vote counts
predate the 2026-05-03 recovery on 16 of 7,878 candidates. Read on the
consensus file's votes the cell would hold **3,544** detections (+3) and
score **F1@50 m 0.7402** (+0.0004), with the tile-MCC shifting by
**+0.0002**. PI ruling 2026-09-20: **documented, not rebuilt** — the shift
is an order of magnitude inside this board's 0.003 mechanism bound, no
number or tier on this board changes, and no signature lapses. The same
note is already attached at the two citation points outside the board,
`results/uplift-supplement/build-report.md` and the cell's own
`results/55maps-r2-ref-2026-09-06/IM-k4/evaluation.md` (commit
`bcf1169f7`).

**Read the tile-MCC as the shift, not the level.** The source note and the
cell's correction note quote the pair as 0.6577 → 0.6579, which is that
note's own instrument; row 35 above and
`results/55maps-r2-ref-2026-09-06/IM-k4/evaluation.json` publish **0.654**
for the same cell, and `sweep_IM.csv` at (0.15, k4) records 0.65395. The
+0.0002 delta is what the ruling rests on; the level is the board's.

**Numbers that moved**: none. `IM-k4` keeps (0.15, k4), n = 3,541,
F1@50 0.7398, tile-MCC 0.654, tier 12, group t.

### 2026-09-20 — Post-hoc addendum: the ten tile-MCC oracles

**Refresh trigger**: this board's sweep record carried micro-F1 and nothing
else, so no family on it could publish a tile-MCC oracle, while both image
campaigns publish an `mcc_oracle` for every rung — leaving every text-vs-image
MCC comparison one-sided
(`reports/comparability-inventory-37-runs-2026-09-20.md` § 1.2, § 3.7). PI
ruling 2026-09-20, item 2.

**What changed**: `scripts/final_board_sweeps.py` now records `tile_mcc`,
`tile_tp`, `tile_tn`, `tile_fp` and `tile_fn` per sweep point and an
`mcc_argmax` per family. The six 3.7 families and the four fourth-cell rungs
were re-swept — 926 points, sapphire, 20 workers, 51 minutes, $0 API — and
their argmax cells materialised and scored into the
[§ Addendum](#addendum-post-hoc-cells-beside-the-tiered-board):
`ARM1-N{1,3,5}-mcc-oracle`, `ARM2-N{1,3,5}-mcc-oracle`,
`FOURTH-N{1,3,5,10}-mcc-oracle`. `cells_manifest.json` grows 43 → 53;
`sweeps.json` gains `mcc_families`, naming the ten families whose record
carries the tile columns.

**Numbers that moved**: none. The re-sweep is deterministic and was gated on
that: all 926 rows of the ten re-swept CSVs were compared field by field
against the committed files, and `family`, `prob_t`, `min_votes`,
`n_detections`, `tp`, `fp`, `fn` and `micro_f1_50` are byte-identical
throughout; the five tile columns are the only additions. The thirteen
families that were not re-swept are byte-identical objects in `sweeps.json`,
and every re-swept family's F1 argmax keeps its point and its value.

**What the new rows say — read F1 beside MCC.** Every family with a choice of
`k` puts its tile-MCC argmax at **k = 1**, abandoning unanimity, and pays
0.06–0.18 of micro-F1 for a fraction of a point of tile-MCC:

| family | F1 oracle | its F1@50 | MCC oracle | its F1@50 | its tile-MCC |
|---|---|---:|---|---:|---:|
| ARM1-N5 | (0.15, k5) | 0.8727 | (0.40, **k1**) | 0.7787 | 0.7308 |
| ARM2-N5 | (0.95, k5) | 0.8871 | (0.96, **k1**) | 0.8055 | 0.7487 |
| FOURTH-N10 | (0.96, k9) | 0.8813 | (0.96, **k1**) | 0.7025 | 0.7567 |
| FOURTH-N5 | (0.96, k5) | 0.8758 | (0.96, **k1**) | 0.7488 | 0.7555 |

tile-MCC asks only whether a tile was hit at all, so over-generation is cheap
in that currency and expensive in F1. An MCC oracle is therefore **not** a
like-for-like companion to the F1 oracle on this corpus. The inventory
reported this collapse for the Gemini 3 image row alone (§ 5.10); it is a
property of the metric on this corpus, not of that row.

**Cross-check obtained for free**: every scored tile-MCC reproduces the
`tile_mcc` the extended sweep record wrote for the same point, to four
decimal places, on all ten cells — an end-to-end confirmation, on ten
independent points, that the new sweep columns are the engine's tile-MCC and
not a look-alike.

**What did NOT change**: the 35-cell tiered board — rows, values, tiers,
group letters, the 595-pair Benjamini–Hochberg family and
`significance-groups.png`. `scripts/final_board_build.py` was not run.
Addendum rows carry no tier and no group letter.

**Commits**: `835c2f3a0` (sweep-record extension + tests), `a1c4bf2c3`
(re-swept CSVs + `sweeps.json`), `1ed3e54cb` (detections + manifest),
`89d7f7e7c` (evaluations).

### 2026-09-20 — Post-hoc addendum: the seven carried-analogue cells

**Refresh trigger**: `reports/comparability-inventory-37-runs-2026-09-20.md`
§ 3.2 found that this board's own committed sweep CSVs already held the 3.7
families' carried-analogue points — swept, but never materialised — so an
image *carried* cell at K/N = 1 or 3 could only be compared against a text
*oracle*, which flatters the text track. PI ruling 2026-09-20, item 1.

**What changed**: seven cells materialised from the board's own family
frames, scored on this board's instrument, and published in the new
[§ Addendum](#addendum-post-hoc-cells-beside-the-tiered-board) —
`ARM2-N1-carried`, `ARM2-N3-carried`, `ARM1-N1-carried`, `ARM1-N3-carried`,
`FOURTH-N1-carried`, `FOURTH-N3-carried`, `FOURTH-N5-carried`.
`cells_manifest.json` grows 36 → 43; `final_board_50m.json` gains an
`addendum_cells` list and an `addendum` block. Each cell's scored F1@50
reproduces its committed sweep row to four decimal places (d = 0.0000 on all
seven, against the board's documented 0.003 mechanism bound).

**Numbers that moved**: none in this document's own tables — the addendum
rows are additions, not revisions. What the rows move is the comparison they
were built for, image minus text at 50 m on reference r2:

| rung | before (image carried − text **oracle**) | after (carried − carried), arm 2 | after, arm 1 |
|---|---:|---:|---:|
| K/N = 1 | +0.0109 | **+0.0260** | **+0.0618** |
| K/N = 3 | +0.0351 | **+0.0397** | **+0.0556** |
| K/N = 5 | +0.0443 | +0.0443 | +0.0579 |

The K = 1 row moves by a factor of 2.4, because the text track's
carried-analogue tax at N = 1 is large and the image track's is small — an
artefact of which cells had been materialised, not a property of either
track.

**What did NOT change**: the 35-cell tiered board. Its rows, F1 values,
confidence intervals, greedy-clique tiers, group letters, cost column,
595-pair Benjamini–Hochberg family and `significance-groups.png` are
untouched, and `scripts/final_board_build.py` was not run. Addendum rows
carry no tier and no group letter by construction.

**Commits**: `3ced9749c` (generator + tests), `cca6ccda5` (detections +
manifest), `85dd99c38` (evaluations).

### 2026-09-20 — `FOURTH-N5-oracle`'s absence from the board is deliberate

**Refresh trigger**: the same inventory (§ 2.1, § 5.7) flagged that
`FOURTH-N5-oracle` is scored on r2 and registered
(`results/run-conditions.json`, run `stride-55map-2026-08-25`, condition
`g384-ov192-55map-n5-verified37-oracle-p0.96-k5-r2-gt`) while
`final_board_50m.json` carried 35 cells and `cells_manifest.json` 36. PI
ruling 2026-09-20, item 3: establish why, and add the cell only if it was an
omission.

**Finding — deliberate, not an omission.** The rung was swept, materialised
and scored on 2026-09-13 under a PI ruling of that date whose instruction
was, in the words of the commit that carried it out, to "finish the
stride-B-under-3.7 K = 5 rung and register it, but do NOT re-tier the 55-map
board" (`f407d4f5d`; registration `c2060da40`; companion evaluation
artefacts `35d56402a`). All three commit bodies record that
`final_board_50m.json`, its tiering and its 595-pair BH family were left
untouched and that `scripts/final_board_build.py` was not run. The cell is
therefore off the published board by ruling. **It is not added here.**

**What changed**: nothing but this minute and one paragraph of the Addendum
section, which now names the cell so a reader who counts this document's
rows against `cells_manifest.json` can see why the two differ without
reading `git log`.

**What did NOT change**: the tiered board, and `FOURTH-N5-oracle` itself —
its detections, evaluation and registration are exactly as committed on
2026-09-13.

### 2026-09-07 — Original publication (reference r2)

Built per `planning/reference-revision-2026-09-06.md` § 4 step 4d on
reference r2; $0 API, sapphire. Membership per the PI's
2026-09-06 ruling (incumbents, A/B rungs, and the 3.7 campaign's
arm 1, arm 2 and fourth cell with their N = 1 / N = 3 rungs).
