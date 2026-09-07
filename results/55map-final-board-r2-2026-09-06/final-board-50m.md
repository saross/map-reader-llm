# The final 55-map board @ 50 m — every run, carried and oracle (reference r2)

> **Last revised**: 2026-09-07 (original publication, reference r2). Card:
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

### 2026-09-07 — Original publication (reference r2)

Built per `planning/reference-revision-2026-09-06.md` § 4 step 4d on
reference r2; $0 API, sapphire. Membership per the PI's
2026-09-06 ruling (incumbents, A/B rungs, and the 3.7 campaign's
arm 1, arm 2 and fourth cell with their N = 1 / N = 3 rungs).
