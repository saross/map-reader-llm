# K-ladder tile-MCC under the three tile joins

> **Last revised**: 2026-10-30 (original publication). See [§ Changelog](#changelog) for revision history.

Rendered by `reports/s166-agent-records/k-ladder-mcc-join-scripts/render.py` from `summary.json` in this directory; the record, with the reading, is `reports/s166-agent-records/k-ladder-mcc-join.md`. Computed at `463257349` on sapphire. Joins: `id` is the published name join; "primary" and "contains" are `geometric-primary` and `geometric-contains` (`lib_advanced_metrics.TILE_JOINS`). Every delta is (higher K) − (lower K); BH p is adjusted within each ladder's own round-robin; bold marks BH q = 0.05 significance.

## 1. Gate: the `id` runs against the committed artefacts

| artefact set | files compared | passed | keys this run adds |
|---|---:|---|---:|
| `phase1_mcc_test` | 17 | yes | 14 |
| `phase2_mcc_test` | 27 | yes | 14 |
| `clipped_mcc_test` | 15 | yes | 0 |
| `phase1_2_tier_e_mcb` | 45 | yes | 0 |
| `clipped_mcb` | 15 | yes | 0 |
| `tier_e_tiering` | 1 | yes | 0 |
| `consensus_grid_sweep` | 57 | yes | 0 |

All passed: **yes**.

## 2. Tile-MCC from K = 1 to the best F1 rung

| ladder | pair | `id` | primary | contains |
|---|---|---:|---:|---:|
| 3.7 arm 1 | K1-vs-K5 | **-0.0099 (0.0168)** | -0.0068 (0.1280) | **-0.0096 (0.0240)** |
| 3.7 arm 2 | K1-vs-K5 | **-0.0275 (<0.0001)** | **-0.0319 (<0.0001)** | **-0.0339 (<0.0001)** |
| 55-map stride A, r2 | K1-vs-K10 | -0.0052 (0.1984) | -0.0076 (0.0622) | -0.0066 (0.1226) |
| 55-map stride A, standardised | K1-vs-K10 | -0.0052 (0.1984) | -0.0076 (0.0622) | -0.0066 (0.1226) |
| GS stride A (board frame) | K1-vs-K10 | +0.0130 (0.7633) | +0.0214 (0.2166) | +0.0214 (0.2460) |
| 55-map stride B, r2 | K1-vs-K10 | +0.0031 (0.5592) | **+0.0111 (0.0075)** | +0.0079 (0.0816) |
| 55-map stride B, 3.7 verifier | K1-vs-K10 | **-0.0112 (<0.0001)** | **-0.0110 (<0.0001)** | **-0.0112 (<0.0001)** |
| 55-map stride B, standardised | K1-vs-K10 | +0.0031 (0.5832) | **+0.0110 (0.0093)** | +0.0079 (0.0885) |
| MINIMAL text T 0.3 | K1-vs-K5 | -0.0251 (0.6044) | -0.0253 (0.2854) | -0.0318 (0.2034) |
| MINIMAL text T 0.7 | K1-vs-K5 | +0.0077 (0.8125) | +0.0000 (1.0000) | +0.0369 (0.1308) |
| MINIMAL text T 1.0 | K1-vs-K10 | -0.0214 (0.5760) | +0.0170 (0.8772) | -0.0168 (0.6724) |
| HIGH text T 0.3 | K1-vs-K5 | -0.0263 (0.5689) | +0.0156 (1.0000) | +0.0306 (0.1466) |
| HIGH text T 0.7 | K1-vs-K10 | -0.0096 (0.8387) | +0.0276 (0.4699) | +0.0300 (0.2984) |
| HIGH text T 1.0 | K1-vs-K10 | -0.0252 (0.8065) | +0.0164 (0.7116) | -0.0168 (0.6040) |
| MINIMAL image T 0.3 | K1-vs-K10 | -0.0065 (0.9954) | -0.0132 (0.5155) | +0.0079 (0.8803) |
| MINIMAL image T 0.7 | K1-vs-K10 | -0.0214 (0.9768) | -0.0096 (0.6636) | -0.0098 (0.9981) |
| MINIMAL image T 1.0 | K1-vs-K10 | -0.0282 (0.6072) | +0.0079 (0.9779) | +0.0108 (0.8690) |
| HIGH image T 0.3 | K1-vs-K10 | +0.0024 (0.9886) | +0.0370 (0.1068) | +0.0315 (0.3357) |
| HIGH image T 0.7 | K1-vs-K5 | -0.0076 (0.8746) | +0.0235 (0.7068) | +0.0380 (0.1890) |
| HIGH image T 1.0 | K1-vs-K10 | **-0.0637 (0.0420)** | +0.0029 (1.0000) | -0.0236 (0.6214) |
| scale-4-optimal 487 | K1-vs-K10 | -0.0572 (0.0762) | -0.0048 (0.8991) | -0.0293 (0.6078) |
| MINIMAL text T 0.3, D51 clipped | K1-vs-K5 | -0.0251 (0.6044) | -0.0253 (0.2854) | -0.0318 (0.2034) |
| MINIMAL text T 1.0, D51 clipped | K1-vs-K10 | -0.0214 (0.5760) | +0.0170 (0.8772) | -0.0168 (0.6724) |
| HIGH text T 1.0, D51 clipped | K1-vs-K10 | -0.0290 (0.5529) | +0.0121 (0.9185) | -0.0168 (0.6040) |
| MINIMAL image T 0.3, D51 clipped | K1-vs-K10 | -0.0065 (0.9954) | -0.0132 (0.5155) | +0.0079 (0.8803) |
| MINIMAL image T 0.7, D51 clipped | K1-vs-K10 | -0.0253 (0.8191) | -0.0139 (0.6324) | -0.0140 (0.9874) |
| MINIMAL image T 1.0, D51 clipped | K1-vs-K10 | -0.0282 (0.6072) | +0.0079 (0.9779) | +0.0108 (0.8690) |
| tier E, D51 clipped | K1-vs-K5 | -0.0071 (1.0000) | -0.0005 (0.8837) | -0.0002 (1.0000) |
| tier E (as evaluated) | K1-vs-K5 | -0.0071 (1.0000) | -0.0006 (0.8837) | -0.0003 (1.0000) |

The 21 verified ladders (as evaluated):

| join | falls | rises | significant falls | significant rises |
|---|---:|---:|---|---|
| `id` | 16 of 21 | 5 of 21 | 4: 3.7 arm 1; 3.7 arm 2; 55-map stride B, 3.7 verifier; HIGH image T 1.0 | 0: — |
| primary | 9 of 21 | 12 of 21 | 2: 3.7 arm 2; 55-map stride B, 3.7 verifier | 2: 55-map stride B, r2; 55-map stride B, standardised |
| contains | 11 of 21 | 10 of 21 | 3: 3.7 arm 1; 3.7 arm 2; 55-map stride B, 3.7 verifier | 0: — |

The 21 verified ladders (six Phase 2 ladders on D51's clipped basis):

| join | falls | rises | significant falls | significant rises |
|---|---:|---:|---|---|
| `id` | 16 of 21 | 5 of 21 | 4: 3.7 arm 1; 3.7 arm 2; 55-map stride B, 3.7 verifier; HIGH image T 1.0 | 0: — |
| primary | 9 of 21 | 12 of 21 | 2: 3.7 arm 2; 55-map stride B, 3.7 verifier | 2: 55-map stride B, r2; 55-map stride B, standardised |
| contains | 11 of 21 | 10 of 21 | 3: 3.7 arm 1; 3.7 arm 2; 55-map stride B, 3.7 verifier | 0: — |

Every other BH-significant tile-MCC pair (adjacent rungs, not the K = 1 → best pair):

| join | ladder | pair | ΔMCC (BH p) |
|---|---|---|---:|
| `id` | 3.7 arm 1 | K1-vs-K3 | -0.0067 (0.0498) |
| `id` | 3.7 arm 1 | K3-vs-K5 | -0.0032 (0.0498) |
| `id` | 3.7 arm 2 | K1-vs-K3 | -0.0258 (<0.0001) |
| `id` | 55-map stride A, r2 | K3-vs-K5 | -0.0111 (0.0066) |
| `id` | 55-map stride A, r2 | K5-vs-K10 | +0.0047 (0.0300) |
| `id` | 55-map stride A, standardised | K3-vs-K5 | -0.0111 (0.0066) |
| `id` | 55-map stride A, standardised | K5-vs-K10 | +0.0047 (0.0300) |
| `id` | 55-map stride B, 3.7 verifier | K1-vs-K3 | -0.0095 (<0.0001) |
| primary | 3.7 arm 2 | K1-vs-K3 | -0.0302 (<0.0001) |
| primary | 55-map stride A, r2 | K3-vs-K5 | -0.0160 (<0.0001) |
| primary | 55-map stride A, r2 | K5-vs-K10 | +0.0067 (0.0016) |
| primary | 55-map stride A, standardised | K3-vs-K5 | -0.0160 (<0.0001) |
| primary | 55-map stride A, standardised | K5-vs-K10 | +0.0067 (0.0016) |
| primary | 55-map stride B, r2 | K1-vs-K3 | +0.0114 (0.0072) |
| primary | 55-map stride B, 3.7 verifier | K1-vs-K3 | -0.0089 (0.0006) |
| primary | 55-map stride B, standardised | K1-vs-K3 | +0.0114 (0.0072) |
| contains | 3.7 arm 1 | K3-vs-K5 | -0.0055 (0.0045) |
| contains | 3.7 arm 2 | K1-vs-K3 | -0.0288 (<0.0001) |
| contains | 3.7 arm 2 | K3-vs-K5 | -0.0052 (0.0094) |
| contains | 55-map stride A, r2 | K3-vs-K5 | -0.0139 (<0.0001) |
| contains | 55-map stride A, r2 | K5-vs-K10 | +0.0049 (0.0232) |
| contains | 55-map stride A, standardised | K3-vs-K5 | -0.0139 (<0.0001) |
| contains | 55-map stride A, standardised | K5-vs-K10 | +0.0049 (0.0232) |
| contains | 55-map stride B, 3.7 verifier | K1-vs-K3 | -0.0094 (0.0001) |
| contains | MINIMAL text T 0.3 | K3-vs-K5 | -0.0443 (0.0108) |
| contains | HIGH text T 0.3 | K1-vs-K3 | +0.0516 (0.0483) |
| contains | HIGH text T 0.7 | K1-vs-K3 | +0.0632 (0.0054) |
| contains | MINIMAL text T 0.3, D51 clipped | K3-vs-K5 | -0.0443 (0.0108) |

## 3. Tile-MCC Hsu MCB admissible sets and the highest-MCC rung

| ladder | `id` set (top) | primary set (top) | contains set (top) |
|---|---|---|---|
| GS stride A (board frame) | {1, 3, 5, 10} (K = 10) | {1, 3, 5, 10} (K = 10) | {1, 3, 5, 10} (K = 10) |
| tier E (as evaluated) | {1, 3, 5, 10} (K = 1) | {1, 3, 5} (K = 3) | {1, 3, 5, 10} (K = 3) |
| MINIMAL text T 0.3 | {1, 3, 10} (K = 3) | {1, 3, 10} (K = 10) | {1, 3, 10} (K = 3) |
| MINIMAL text T 0.7 | {1, 3, 5, 10} (K = 5) | {1, 3, 5, 10} (K = 3) | {3, 5} (K = 5) |
| MINIMAL text T 1.0 | {1, 3, 5, 10} (K = 1) | {1, 3, 5, 10} (K = 10) | {1, 3, 5, 10} (K = 1) |
| HIGH text T 0.3 | {1, 3, 5, 10} (K = 1) | {1, 3, 5, 10} (K = 5) | {3, 5, 10} (K = 3) |
| HIGH text T 0.7 | {1, 3, 5, 10} (K = 3) | {3, 5, 10} (K = 3) | {3, 5, 10} (K = 3) |
| HIGH text T 1.0 | {1, 3, 5, 10} (K = 1) | {3, 5, 10} (K = 3) | {1, 3, 5, 10} (K = 3) |
| MINIMAL image T 0.3 | {1, 3, 5, 10} (K = 1) | {1, 5, 10} (K = 1) | {1, 3, 5, 10} (K = 10) |
| MINIMAL image T 0.7 | {1, 3, 5, 10} (K = 1) | {1, 3, 5} (K = 5) | {1, 3, 5, 10} (K = 5) |
| MINIMAL image T 1.0 | {1, 3, 5, 10} (K = 1) | {1, 3, 5, 10} (K = 10) | {1, 3, 5, 10} (K = 5) |
| HIGH image T 0.3 | {1, 3, 5, 10} (K = 10) | {3, 5, 10} (K = 10) | {1, 3, 5, 10} (K = 10) |
| HIGH image T 0.7 | {1, 3, 5} (K = 1) | {1, 3, 5, 10} (K = 5) | {3, 5, 10} (K = 5) |
| HIGH image T 1.0 | {1, 3, 5} (K = 1) | {1, 3, 5, 10} (K = 10) | {1, 3, 5, 10} (K = 1) |
| scale-4-optimal 487 | {1, 3, 5} (K = 1) | {1, 3, 5, 10} (K = 1) | {1, 3, 5, 10} (K = 1) |
| 55-map stride A, r2 | {1, 3} (K = 3) | {1, 3} (K = 3) | {1, 3} (K = 3) |
| 55-map stride A, standardised | {1, 3} (K = 3) | {1, 3} (K = 3) | {1, 3} (K = 3) |
| 55-map stride B, r2 | {1, 3, 5, 10} (K = 3) | {3, 5, 10} (K = 3) | {3, 5, 10} (K = 10) |
| 55-map stride B, standardised | {1, 3, 5, 10} (K = 3) | {3, 5, 10} (K = 3) | {3, 5, 10} (K = 10) |
| 55-map stride B, 3.7 verifier | {1} (K = 1) | {1} (K = 1) | {1} (K = 1) |
| 3.7 arm 1 | {1, 3} (K = 1) | {1, 3, 5} (K = 1) | {1, 3} (K = 1) |
| 3.7 arm 2 | {1} (K = 1) | {1} (K = 1) | {1} (K = 1) |
| MINIMAL text T 0.3, D51 clipped | {1, 3, 10} (K = 3) | {1, 3, 10} (K = 10) | {1, 3, 10} (K = 3) |
| MINIMAL text T 1.0, D51 clipped | {1, 3, 5, 10} (K = 1) | {1, 3, 5, 10} (K = 10) | {1, 3, 5, 10} (K = 1) |
| HIGH text T 1.0, D51 clipped | {1, 3, 5, 10} (K = 1) | {1, 3, 5, 10} (K = 3) | {1, 3, 5, 10} (K = 3) |
| MINIMAL image T 0.3, D51 clipped | {1, 3, 5, 10} (K = 1) | {1, 5, 10} (K = 1) | {1, 3, 5, 10} (K = 10) |
| MINIMAL image T 0.7, D51 clipped | {1, 3, 5, 10} (K = 1) | {1, 3, 5} (K = 5) | {1, 3, 5, 10} (K = 5) |
| MINIMAL image T 1.0, D51 clipped | {1, 3, 5, 10} (K = 1) | {1, 3, 5, 10} (K = 10) | {1, 3, 5, 10} (K = 5) |
| tier E, D51 clipped | {1, 3, 5, 10} (K = 1) | {1, 3, 5, 10} (K = 3) | {1, 3, 5, 10} (K = 3) |

| join | ladders | K = 1 admissible | K = 1 highest | highest at K = 1 / 3 / 5 / 10 | whole ladder admissible | K = 10 excluded |
|---|---:|---:|---:|---|---:|---:|
| `id` (22) | 22 | 22 | 13 | 13 / 6 / 1 / 2 | 13 | 6 |
| primary (22) | 22 | 17 | 5 | 5 / 8 / 3 / 6 | 9 | 5 |
| contains (22) | 22 | 16 | 6 | 6 / 7 / 4 / 5 | 10 | 4 |
| `id` (7 clipped) | 7 | 7 | 6 | 6 / 1 / 0 / 0 | 6 | 0 |
| primary (7 clipped) | 7 | 7 | 1 | 1 / 2 / 1 / 3 | 4 | 1 |
| contains (7 clipped) | 7 | 7 | 1 | 1 / 3 / 2 / 1 | 6 | 0 |

## 4. § 8.6: K = 1 → 10 tile-MCC, consensus-only against verified

| join | consensus only (K1 → K10) | verified, as evaluated (BH p) | verified, D51 clipped (BH p) | swing, as evaluated / clipped | sign reversal, as evaluated / clipped |
|---|---:|---:|---:|---:|---|
| `id` | 0.4465 → 0.4909 (+0.0444) | 0.8211 → 0.7973 (-0.0238, 0.8094) | 0.8133 → 0.7973 (-0.0161, 1.0000) | 0.0682 / 0.0604 | yes / yes |
| primary | 0.5413 → 0.5793 (+0.0380) | 0.9330 → 0.9113 (-0.0216, 0.3682) | 0.9242 → 0.9113 (-0.0128, 0.8363) | 0.0597 / 0.0509 | yes / yes |
| contains | 0.4935 → 0.5544 (+0.0610) | 0.8935 → 0.8813 (-0.0122, 0.6490) | 0.8850 → 0.8813 (-0.0037, 1.0000) | 0.0732 / 0.0647 | yes / yes |

## 5. Diagnostic: `id`-join FN tiles that hold the rung's own detections

Pooled over the 22 as-evaluated ladders' rungs: 19,671 of 29,227 false-negative tiles (67.3 %). Cross-check of each rung's `id` MCC against its tiering: 0 mismatches.

From K = 1 to each ladder's top rung, the number of ladders whose count rises / falls / stays the same:

| ladders | detections | FN tiles | FN tiles holding a detection | share | geometric − `id` MCC gain larger at the top rung (primary / contains) |
|---|---|---|---|---|---|
| gold-standard frame (15) | 1 / 14 / 0 | 15 / 0 / 0 | 15 / 0 / 0 | 8 / 7 / 0 | 13 / 15 of 15 |
| 55-map deployment (7) | 0 / 7 / 0 | 4 / 3 / 0 | 2 / 5 / 0 | 1 / 6 / 0 | 4 / 3 of 7 |
| all 22 (22) | 1 / 21 / 0 | 19 / 3 / 0 | 17 / 5 / 0 | 9 / 13 / 0 | 17 / 18 of 22 |

| ladder | FN tiles holding a detection / FN tiles, by K | share, K = 1 → top K | geometric − `id` MCC gain, K = 1 → top K (primary; contains) |
|---|---|---:|---|
| 3.7 arm 1 | K1 734/1040; K3 739/1067; K5 732/1097 | 0.706 → 0.667 (-0.038) | +0.1561 → +0.1592; +0.1522 → +0.1526 |
| 3.7 arm 2 | K1 743/1088; K3 745/995; K5 733/1027 | 0.683 → 0.714 (+0.031) | +0.1633 → +0.1589; +0.1595 → +0.1530 |
| 55-map stride A, r2 | K1 714/1105; K3 717/1105; K5 705/1123; K10 708/1100 | 0.646 → 0.644 (-0.003) | +0.1509 → +0.1485; +0.1449 → +0.1436 |
| 55-map stride A, standardised | K1 713/1101; K3 716/1101; K5 704/1119; K10 707/1096 | 0.648 → 0.645 (-0.003) | +0.1515 → +0.1490; +0.1447 → +0.1434 |
| GS stride A (board frame) | K1 25/41; K3 27/48; K5 28/47; K10 26/45 | 0.610 → 0.578 (-0.032) | +0.1117 → +0.1201; +0.0774 → +0.0857 |
| 55-map stride B, r2 | K1 723/1004; K3 730/1077; K5 726/1107; K10 731/1088 | 0.720 → 0.672 (-0.048) | +0.1499 → +0.1579; +0.1471 → +0.1520 |
| 55-map stride B, 3.7 verifier | K1 736/1056; K3 737/1109; K10 735/1118 | 0.697 → 0.657 (-0.040) | +0.1642 → +0.1644; +0.1577 → +0.1577 |
| 55-map stride B, standardised | K1 722/1000; K3 729/1073; K5 725/1103; K10 730/1084 | 0.722 → 0.673 (-0.049) | +0.1504 → +0.1584; +0.1469 → +0.1517 |
| MINIMAL text T 0.3 | K1 28/40; K3 31/41; K5 30/43; K10 30/42 | 0.700 → 0.714 (+0.014) | +0.1206 → +0.1283; +0.0742 → +0.0818 |
| MINIMAL text T 0.7 | K1 27/44; K3 30/47; K5 31/47; K10 31/47 | 0.614 → 0.660 (+0.046) | +0.1183 → +0.1168; +0.0596 → +0.0751 |
| MINIMAL text T 1.0 | K1 27/36; K3 30/41; K5 33/45; K10 32/44 | 0.750 → 0.727 (-0.023) | +0.0970 → +0.1354; +0.0801 → +0.0847 |
| HIGH text T 0.3 | K1 20/30; K3 31/47; K5 33/46; K10 34/43 | 0.667 → 0.791 (+0.124) | +0.1053 → +0.1320; +0.0473 → +0.1103 |
| HIGH text T 0.7 | K1 24/34; K3 31/39; K5 33/48; K10 33/53 | 0.706 → 0.623 (-0.083) | +0.1011 → +0.1383; +0.0689 → +0.1085 |
| HIGH text T 1.0 | K1 23/32; K3 30/40; K5 29/41; K10 30/42 | 0.719 → 0.714 (-0.004) | +0.0911 → +0.1327; +0.0655 → +0.0739 |
| MINIMAL image T 0.3 | K1 18/26; K3 24/35; K5 21/30; K10 23/31 | 0.692 → 0.742 (+0.050) | +0.0840 → +0.0773; +0.0496 → +0.0641 |
| MINIMAL image T 0.7 | K1 18/24; K3 22/31; K5 22/32; K10 24/35 | 0.750 → 0.686 (-0.064) | +0.0808 → +0.0926; +0.0471 → +0.0588 |
| MINIMAL image T 1.0 | K1 18/27; K3 22/35; K5 28/44; K10 27/40 | 0.667 → 0.675 (+0.008) | +0.0838 → +0.1199; +0.0379 → +0.0769 |
| HIGH image T 0.3 | K1 17/25; K3 23/29; K5 25/42; K10 25/32 | 0.680 → 0.781 (+0.101) | +0.0686 → +0.1032; +0.0397 → +0.0688 |
| HIGH image T 0.7 | K1 17/23; K3 21/33; K5 25/35; K10 32/49 | 0.739 → 0.653 (-0.086) | +0.0735 → +0.1174; +0.0320 → +0.0994 |
| HIGH image T 1.0 | K1 12/17; K3 19/32; K5 22/36; K10 25/42 | 0.706 → 0.595 (-0.111) | +0.0481 → +0.1147; +0.0235 → +0.0638 |
| scale-4-optimal 487 | K1 14/20; K3 20/34; K5 24/34; K10 27/38 | 0.700 → 0.711 (+0.011) | +0.0557 → +0.1080; +0.0338 → +0.0617 |
| tier E (as evaluated) | K1 24/33; K3 27/33; K5 26/36; K10 28/38 | 0.727 → 0.737 (+0.010) | +0.1119 → +0.1140; +0.0724 → +0.0840 |
| MINIMAL text T 0.3, D51 clipped | K1 28/40; K3 31/41; K5 30/43; K10 30/42 | 0.700 → 0.714 (+0.014) | +0.1206 → +0.1283; +0.0742 → +0.0818 |
| MINIMAL text T 1.0, D51 clipped | K1 27/36; K3 30/41; K5 33/45; K10 32/44 | 0.750 → 0.727 (-0.023) | +0.0970 → +0.1354; +0.0801 → +0.0847 |
| HIGH text T 1.0, D51 clipped | K1 23/32; K3 31/41; K5 30/42; K10 31/43 | 0.719 → 0.721 (+0.002) | +0.0911 → +0.1321; +0.0655 → +0.0777 |
| MINIMAL image T 0.3, D51 clipped | K1 18/26; K3 24/35; K5 21/30; K10 23/31 | 0.692 → 0.742 (+0.050) | +0.0840 → +0.0773; +0.0496 → +0.0641 |
| MINIMAL image T 0.7, D51 clipped | K1 18/24; K3 22/32; K5 22/33; K10 24/36 | 0.750 → 0.667 (-0.083) | +0.0808 → +0.0921; +0.0471 → +0.0583 |
| MINIMAL image T 1.0, D51 clipped | K1 18/27; K3 22/35; K5 28/44; K10 27/40 | 0.667 → 0.675 (+0.008) | +0.0838 → +0.1199; +0.0379 → +0.0769 |
| tier E, D51 clipped | K1 24/35; K3 27/35; K5 26/38; K10 28/38 | 0.686 → 0.737 (+0.051) | +0.1109 → +0.1140; +0.0717 → +0.0840 |

## Changelog

### 2026-10-30 — Original publication

Written by the S166 K-ladder tile-join job from `summary.json`.
