# Run B, the modality bridging pair: first findings

> **Last revised**: 2026-10-08 (scoring plan items 4, 6 and 7: the gap-change
> interaction test, the date component, and the replicate floors; wording
> after an independent audit). See
> [§ Changelog](#changelog) for revision history.

**Status: SCORED, FOR THE PRINCIPAL INVESTIGATOR'S (PI'S) REVIEW.** Point
estimates and tile-swap p-values (§§ 2–3), the gap-change interaction test
(§ 5), the date component per cell (§ 6), and the D45/D46 replicate floors
(§ 7), every run behind the six-cell anchor gate. Not yet computed: Matthews
correlation coefficient (MCC) gaps. §§ 2–3 were scored with the scorer on
`main` at `aa1746fbd`; §§ 5–7 with `scripts/modality_bridge_floors.py` on
`a9c5d4ef3` (no scorer file changed between the two), which reproduces every
number of §§ 2–3 exactly before computing anything new. The D50/D51 scorer
change (pull request #26, open) may move cells slightly when it is merged
and the re-score is approved.

## 1. What ran

Run B re-ran the four proposer arms of the modality claim (R7.3-22/23) on one
day, 2026-10-07, on the Batch API, with their original configurations (PI
ruling D49), plus three arms the PI added that day (D52; Stage 1 card
`planning/modality-bridge-2026-10-07.md` § 4.8):

- **The fifth leg** (`g37-image-cache`): Gemini 3.7 image through the explicit
  context cache, the Gemini 3 image arm's request shape.
- **A temperature-matched Gemini 3 pair** (`g3-text-temp1`, `g3-image-temp1`):
  text and image at temperature (T) 1.0 and K = 5. Gemini 3.7 samples at its
  default, 1.0, whatever is sent (`planning/temperature-probe-2026-10-07.md`
  §§ 7, 8.5).

All 45 proposer passes landed at exact coverage (1,398 tiles each). Ten
verifier legs followed on the same UTC day (Stage 2 card
`planning/modality-bridge-2026-10-07-stage2.md`). Unions, verifier settings
and every check are recorded in the two cards and their commits.

## 2. Cells (F1 at 20 m, 487-tile frame)

| Cell | Bridge F1 (point) | Original F1 | Bridge − original | MCC |
|---|---:|---:|---:|---:|
| Gemini 3 text, K = 10, Gemini 3 verifier | 0.8916 (0.15, k10) | 0.8961 | −0.0045 | 0.7939 |
| Gemini 3 image, K = 10, Gemini 3 verifier | 0.8331 (0.15, k9); best 0.8393 | 0.8412 | −0.0081 | 0.7954 |
| 3.7 text, K = 5, Gemini 3 verifier | 0.9154 (0.10, k5) | 0.9139 | +0.0015 | 0.8069 |
| 3.7 text, K = 5, 3.7 verifier | 0.9265 (0.80, k5) | 0.9265 | 0.0000 | 0.8116 |
| 3.7 image, K = 5, Gemini 3 verifier | 0.9160 (0.10, k5) | 0.9254 | −0.0094 | 0.8184 |
| 3.7 image, K = 5, 3.7 verifier | 0.9288 (0.90, k5) | 0.9308 | −0.0020 | 0.8368 |
| 3.7 image **cached**, Gemini 3 verifier | 0.9318 (0.10, k5) | — | — | 0.8184 |
| 3.7 image **cached**, 3.7 verifier | 0.9352 (0.90, k5); best 0.9363 | — | — | 0.8223 |
| Gemini 3 text, **T 1.0**, K = 5 | best 0.8824 (0.15, k5) | — | — | — |
| Gemini 3 image, **T 1.0**, K = 5 | best 0.8242 (0.15, k5) | — | — | — |

Source: `*/analysis.json` (`operating_point`, `image_best`). "Bridge −
original" is date plus serving mode (batch against the originals' real-time
tiers), never date alone (Stage 1 card § 9 item 6); § 6 tests it.

## 3. Gaps, text − image (tile-swap permutation, 10,000, 487 tiles)

| Pair | Bridge gap (p) | Original gap (p) |
|---|---:|---:|
| Gemini 3, K = 10 | **+0.0523 (0.0029)** | +0.0549 (0.0010) |
| Gemini 3, K = 5 (inherited rung) | +0.0609 (0.0002) | — |
| Gemini 3, **T 1.0**, K = 5 | **+0.0582 (0.0002)** | — |
| 3.7, Gemini 3 verifier | −0.0006 (0.95) | −0.0115 (0.25) |
| 3.7, 3.7 verifier | −0.0023 (0.75) | −0.0043 (0.68) |
| 3.7 text − **cached** image, Gemini 3 verifier | −0.0164 (0.074) | — |
| 3.7 text − **cached** image, 3.7 verifier | −0.0098 (0.25) | — |

Gap change against Gemini 3: −0.0529 (3.7, Gemini 3 verifier) and −0.0547
(all 3.7), interaction p 0.0047 and 0.0040 (§ 5). Sources: `gap_test.json`
(best points, as the originals), `k5/gap_test.json`,
`additions/gap_test.json`; each gap against its floor in § 7.

## 4. What it says, against the floors

1. **The modality result replicates on one day, on one serving mode.**
   Gemini 3 keeps a text advantage of about +0.05 F1 (p 0.003), 1.5 times
   its floor (§ 7). Gemini 3.7 shows none, under either verifier. The change
   between the families, −0.053 and −0.055, is resolved (interaction
   p 0.005 and 0.004, § 5) and 1.2 to 1.3 times its own floor. Each bridge
   cell sits within 0.01 F1 of its original, at most 0.46 of its run-to-run
   floor (§ 6).
2. **Temperature does not explain it.** At T 1.0, the temperature 3.7
   actually samples at, the Gemini 3 text advantage is +0.058 (p 0.0002,
   1.9 times its floor), as large as at T 0.7.
3. **Nor does the request shape.** Sent through the explicit cache, as
   Gemini 3 image is, 3.7 image still shows no text advantage. If anything,
   image leads, by −0.016 (p 0.074) and −0.010 (p 0.25), but neither is
   rejected and they sit at 0.69 and 0.43 of their floors: no resolved
   gap, and no image lead. The cached 3.7 image cells score a little above
   the inline ones at the operating points (0.9318 against 0.9160; 0.9352
   against 0.9288), differences of 0.74 and 0.32 of the floor of two
   independent 3.7 image cells (1.96 · √(SD² + SD²) + 0.001 from § 7's cell
   SDs at those points); not tested by permutation.
4. With temperature, request structure, tier, K and day matched, the family
   difference remains once only the model and its thinking level differ:
   the fully matched gap change is −0.075 and −0.068 (p < 0.0001), 1.9 and
   1.7 times its floor (§ 7). What remains is Gemini 3's text advantage
   against no resolved gap in Gemini 3.7: of R7.3-22's "parity or
   inversion", these runs show no inversion. They do not show parity in
   the strict sense: the evidence is that the test does not reject and each
   3.7 gap sits below its floor, which is not a test of equivalence.
5. **Under D45 the family claim stands on these runs: every gap change
   clears its point floor, and every one sits inside its floor's upper
   bound.** All ten gap changes reject and clear their point floors (1.24
   to 1.87 times),
   the floors re-derived from § 3 of the W2.7 report (1.36 to 1.79) and the
   direct-SD sensitivity (1.40 to 1.87), but none clears the upper bound of
   its floor (0.66 to 0.99). The K = 10 contrast the claim was first made
   on is the narrowest (1.24 and 1.28); the K-matched and fully matched
   contrasts are clearer (1.66 to 1.87).

## 5. The gap change, tested (scoring plan item 4)

The grid's interaction instrument (`grid_analysis.paired_interaction`, as the
2026-08-18 grid used it): the difference of differences (T37 − I37) −
(T3 − I3) on the gap tests' own per-tile counts (20 m, 487 tiles), a paired
tile bootstrap interval (1,000 draws, seed 42), and a permutation p (10,000,
seed 42) in which each tile swaps its text and image labels in both families
together (Stage 1 card § 9 item 4). As a sensitivity, each tile swaps the two
families instead; to first order both are the sign-flip test of each tile's
contribution, and the two agree. Benjamini-Hochberg (BH) adjustment is over
all ten tests. Script `scripts/modality_bridge_floors.py`; results
`floors/gap_change.json`.

| Gap change (3.7 gap − Gemini 3 gap) | Estimate | CI95 | p | p, family swap | BH |
|---|---:|---|---:|---:|---:|
| **Primary:** 3.7 (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0529 | [−0.0887, −0.0198] | 0.0047 | 0.0031 | 0.0047 |
| **Primary:** all-3.7 − Gemini 3 K = 10 | −0.0547 | [−0.0909, −0.0195] | 0.0040 | 0.0029 | 0.0044 |
| 3.7 (Gemini 3 verifier) − Gemini 3 K = 5 rung | −0.0615 | [−0.0970, −0.0275] | 0.0004 | 0.0004 | 0.0008 |
| all-3.7 − Gemini 3 K = 5 rung | −0.0633 | [−0.1003, −0.0277] | 0.0002 | 0.0002 | 0.0007 |
| 3.7 (Gemini 3 verifier) − Gemini 3 T 1.0 | −0.0588 | [−0.0917, −0.0256] | 0.0006 | 0.0005 | 0.0010 |
| all-3.7 − Gemini 3 T 1.0 | −0.0605 | [−0.0955, −0.0288] | 0.0004 | 0.0002 | 0.0008 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0687 | [−0.1072, −0.0316] | 0.0008 | 0.0005 | 0.0011 |
| Fifth leg (3.7 verifier) − Gemini 3 K = 10 | −0.0621 | [−0.0978, −0.0270] | 0.0011 | 0.0009 | 0.0014 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 T 1.0, fully matched | −0.0746 | [−0.1098, −0.0416] | < 0.0001 | < 0.0001 | < 0.0001 |
| Fifth leg (3.7 verifier) − Gemini 3 T 1.0, fully matched | −0.0680 | [−0.1008, −0.0359] | < 0.0001 | < 0.0001 | < 0.0001 |

"Fifth leg" is 3.7 text − cached 3.7 image; "< 0.0001" means no permutation
of 10,000 reached the observed value (D42 default (d)). Every interval
excludes zero. This is the p the original claim could not compute across
campaigns.

## 6. The date component per cell (scoring plan item 6): date plus serving mode

Bridge minus original at the original's operating point and at each side's
oracle (its own sweep best; each original's operating point is its oracle,
gate 1). Every difference combines date with serving mode (batch against the
originals' real-time flex or standard tiers); none is a date effect alone.
Tile-swap p (10,000, seed 42). Same-tile flips on the 487 tiles: a tile is
**discordant** when any of its TP, FP or FN counts differ; it is **fixed**
when it leaves error (FP + FN > 0) and **broken** when it enters it. The
within-execution yardstick is the discordant-tile rate between disjoint
subset rungs of the bridge arm, K' = 5 for Gemini 3 (126 pairs) and K' = 2
for 3.7 (15 pairs): smaller rungs flip more tiles than the K = 10 or K = 5
cells, so the yardstick is generous in pass count. It holds the verifier
fixed, though, while each bridge cell was re-verified on a different date
from its original, so verifier re-invocation flips are in the comparison
but not in the yardstick. Floor: 1.96 · √2 · SD + 0.001, the
original's SD taken equal to the bridge's (§ 7). Results
`floors/date_component.json`.

| Cell | Point (bridge) | Bridge − original | p | Discordant tiles | Fixed / broken | Within execution, median (95th) | Of floor |
|---|---|---:|---:|---:|---:|---:|---:|
| Gemini 3 text | (0.15, k10), the oracle too | −0.0045 | 0.62 | 32 (6.6 %) | 12 / 14 | 4.7 % (5.3 %) | 0.27 |
| Gemini 3 image | original (0.15, k9) | −0.0081 | 0.53 | 60 (12.3 %) | 12 / 18 | 12.8 % (14.4 %) | 0.17 |
| Gemini 3 image | oracle (0.15, k10) | −0.0019 | 0.88 | 55 (11.3 %) | 15 / 13 | 12.8 % (14.4 %) | 0.04 |
| 3.7 text, Gemini 3 verifier | (0.10, k5), the oracle too | +0.0015 | 0.87 | 33 (6.8 %) | 13 / 8 | 7.8 % (8.0 %) | 0.06 |
| 3.7 text, 3.7 verifier | (0.80, k5); oracle (0.75, k5), same set | 0.0000 | 1.00 | 22 (4.5 %) | 8 / 8 | 5.5 % (6.0 %) | 0.00 |
| 3.7 image, Gemini 3 verifier | (0.10, k5), the oracle too | −0.0094 | 0.26 | 24 (4.9 %) | 4 / 9 | 7.0 % (8.1 %) | 0.46 |
| 3.7 image, 3.7 verifier | (0.90, k5); oracle (0.88, k5), same set | −0.0020 | 0.84 | 19 (3.9 %) | 5 / 6 | 6.0 % (7.2 %) | 0.10 |

Reading:

- **No date-plus-mode component is resolved in F1.** No p falls below 0.25,
  and every difference is at most 0.46 of its within-execution floor (and
  0.42 of the § 3 floor).
- **On five of six cells the bridge moves no more tiles than two disjoint
  rungs of one execution do** (five-pass rungs for Gemini 3, two-pass rungs
  for 3.7). Gemini 3 text is the exception: 6.6 % of tiles change against a
  95th percentile of 5.3 % between rungs half its size, balanced (12 fixed,
  14 broken), so its F1 hardly moves (flagged, § 8). Part or all of the
  excess may be verifier re-invocation, which the yardstick leaves out.
- Gemini 3 image at the original point gains 10 TP and 22 FP (its union is
  15 % smaller and its passes agree more, § 8); at its oracle the difference
  is −0.0019. The lower F1 at k9 is the operating point moving, not the
  cell.

## 7. Against the floors (scoring plan item 7; rulings D45, D46)

**Method** (W2.7 report § 6b, `reports/w27-replicate-floors-2026-10-06.md`,
and its `floors-v2/` scripts). Each arm's rung was rebuilt from every subset
of its passes (2,201 rungs: 1,023 per ten-pass arm, 31 per five-pass arm)
with the K = 5 ladder's own mechanism: re-cluster the subset, and inherit
each candidate's verifier probability from the arm's union verification
within 10 m, so the verifier is held fixed. Each rung was scored at 20 m on
the 487-tile frame along the cell's vote path (k' = round(k / K · K')). The
run-to-run SD at K' passes is √(V_sub · N / (N − K')) over all C(N, K')
subsets. At K = N it is carried by § 6b's rules: for ten passes, the largest
of a power-law fit, a hyperbola fit (both on K' = 1..5) and the K' = 5 value;
for five passes, the largest of the fits and the direct K' = 3 and K' = 4
values. Upper bounds add 1.96 jackknife standard errors. Floors: two
independent cells 1.96 · √(SD_x² + SD_y²) + 0.001; a gap change of four
1.96 · √ΣSD² + 0.002 (the verifier re-invocation band, 0.001 per contrast).
"Direct" replaces the ten-pass K = 10 carry by the largest direct estimate
from K' = 5 to 9, which only these arms have. "§ 3" is the W2.7 report's
committed 487-tile within-execution floor at the cell's (K, t): proposer-only
consensus, re-derived from its pairs file to four places, and read as a
per-cell SD where a contrast has more than two cells. Gates, all passed:
the six original cells and three gaps; every committed bridge set re-scored
to its F1 within 1e-3; every committed gap test reproduced exactly (both
F1s, the difference and the p); each all-pass rung equal to its arm's union
(count, votes, within 2 nanometres) and to every committed cell set tile for
tile; the first-five rungs equal to the committed K = 5 ladder sets. Results
`floors/floors.json`, `floors/summary.csv`, `floors/gates.json` and
`floors/subset_cells.csv`; 380 s on sapphire.

**Cell SDs** (the run-to-run SD of each cell at its point):

| Cell (point) | K | SD | Upper | Direct | § 3 floor |
|---|---:|---:|---:|---:|---:|
| Gemini 3 text (0.15, k10) | 10 | 0.0056 | 0.0086 | 0.0060 | 0.0253 |
| Gemini 3 image (0.15, k10) | 10 | 0.0164 | 0.0319 | 0.0129 | 0.0253 |
| Gemini 3 image (0.15, k9) | 10 | 0.0164 | 0.0319 | 0.0126 | 0.0191 |
| Gemini 3 text, K = 5 rung (0.15, k5) | 5 of 10 | 0.0056 | 0.0093 | — | 0.0295 |
| Gemini 3 image, K = 5 rung (0.15, k5) | 5 of 10 | 0.0126 | 0.0196 | — | 0.0295 |
| 3.7 text, Gemini 3 verifier (0.10, k5) | 5 | 0.0089 | 0.0171 | — | 0.0295 |
| 3.7 text, 3.7 verifier (0.75 / 0.80, k5) | 5 | 0.0089 / 0.0080 | 0.0199 / 0.0176 | — | 0.0295 |
| 3.7 image, Gemini 3 verifier (0.10, k5) | 5 | 0.0071 | 0.0137 | — | 0.0295 |
| 3.7 image, 3.7 verifier (0.88 / 0.90, k5) | 5 | 0.0072 / 0.0073 | 0.0137 / 0.0138 | — | 0.0295 |
| 3.7 image cached, Gemini 3 verifier (0.10, k5) | 5 | 0.0076 | 0.0206 | — | 0.0295 |
| 3.7 image cached, 3.7 verifier (0.95 / 0.90, k5) | 5 | 0.0064 / 0.0066 | 0.0190 / 0.0190 | — | 0.0295 |
| Gemini 3 text, T 1.0 (0.15, k5) | 5 | 0.0085 | 0.0185 | — | 0.0295 |
| Gemini 3 image, T 1.0 (0.15, k5) | 5 | 0.0128 | 0.0213 | — | 0.0295 |

**Gaps** (text − image; p from § 3):

| Gap | Estimate | p | Floor (upper) | Of floor (of upper) | Direct floor (of it) | § 3 floor (of it) |
|---|---:|---:|---:|---:|---:|---:|
| Gemini 3, K = 10 | +0.0523 | 0.0029 | 0.0349 (0.0658) | 1.50 (0.80) | 0.0289 (1.81) | 0.0253 (2.07) |
| Gemini 3, K = 5 rung | +0.0609 | 0.0002 | 0.0280 (0.0436) | 2.17 (1.40) | — | 0.0295 (2.06) |
| Gemini 3, T 1.0, K = 5 | +0.0582 | 0.0002 | 0.0311 (0.0564) | 1.87 (1.03) | — | 0.0295 (1.97) |
| 3.7, Gemini 3 verifier | −0.0006 | 0.95 | 0.0232 (0.0438) | 0.03 (0.01) | — | 0.0295 (0.02) |
| 3.7, 3.7 verifier | −0.0023 | 0.75 | 0.0234 (0.0483) | 0.10 (0.05) | — | 0.0295 (0.08) |
| 3.7 text − cached image, Gemini 3 verifier | −0.0164 | 0.074 | 0.0239 (0.0534) | 0.69 (0.31) | — | 0.0295 (0.55) |
| 3.7 text − cached image, 3.7 verifier | −0.0098 | 0.25 | 0.0225 (0.0548) | 0.43 (0.18) | — | 0.0295 (0.33) |

**Gap changes** (p from § 5):

| Gap change | Estimate | p | Floor (upper) | Of floor (of upper) | Direct floor (of it) | § 3-derived floor (of it) |
|---|---:|---:|---:|---:|---:|---:|
| **Primary:** 3.7 (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0529 | 0.0047 | 0.0426 (0.0797) | 1.24 (0.66) | 0.0377 (1.40) | 0.0389 (1.36) |
| **Primary:** all-3.7 − Gemini 3 K = 10 | −0.0547 | 0.0040 | 0.0427 (0.0822) | 1.28 (0.66) | 0.0378 (1.45) | 0.0389 (1.41) |
| 3.7 (Gemini 3 verifier) − Gemini 3 K = 5 rung | −0.0615 | 0.0004 | 0.0370 (0.0624) | 1.66 (0.99) | — | 0.0417 (1.47) |
| all-3.7 − Gemini 3 K = 5 rung | −0.0633 | 0.0002 | 0.0371 (0.0657) | 1.70 (0.96) | — | 0.0417 (1.52) |
| 3.7 (Gemini 3 verifier) − Gemini 3 T 1.0 | −0.0588 | 0.0006 | 0.0394 (0.0720) | 1.49 (0.82) | — | 0.0417 (1.41) |
| all-3.7 − Gemini 3 T 1.0 | −0.0605 | 0.0004 | 0.0395 (0.0748) | 1.53 (0.81) | — | 0.0417 (1.45) |
| Fifth leg (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0687 | 0.0008 | 0.0429 (0.0854) | 1.60 (0.81) | 0.0381 (1.81) | 0.0389 (1.77) |
| Fifth leg (3.7 verifier) − Gemini 3 K = 10 | −0.0621 | 0.0011 | 0.0422 (0.0862) | 1.47 (0.72) | 0.0372 (1.67) | 0.0389 (1.60) |
| Fifth leg (Gemini 3 verifier) − Gemini 3 T 1.0, fully matched | −0.0746 | < 0.0001 | 0.0398 (0.0783) | 1.87 (0.95) | — | 0.0417 (1.79) |
| Fifth leg (3.7 verifier) − Gemini 3 T 1.0, fully matched | −0.0680 | < 0.0001 | 0.0390 (0.0792) | 1.74 (0.86) | — | 0.0417 (1.63) |

Reading (D45: a configuration claim needs the test to reject AND the
difference to exceed its floor):

- **The Gemini 3 text advantage is a configuration-level result** at K = 5
  (2.17 times the floor, 1.40 times its upper bound) and at T 1.0 (1.87;
  1.03). At K = 10 it clears the point floor (1.50, or 1.81 on direct SDs,
  2.07 on § 3) but not the upper bound (0.80), which the image arm's
  carried SD drives.
- **No 3.7 gap is resolved** (none rejected; 0.03 to 0.69 of its floor),
  the fifth leg's included. This is the absence of a resolved gap, not a
  demonstrated equivalence.
- **Every gap change rejects and clears its point floor** (1.24 to 1.87), on
  all three floor readings; none clears its upper bound (0.66 to 0.99). The
  family claim therefore stands on these runs as a configuration claim, in
  the re-screen's category "clears the point floor; inside its upper bound"
  (W2.7 report § 6b), most narrowly on the K = 10 contrast it was first made
  on. The upper bound is conservative: it adds each cell's upper SD in
  quadrature; a delta-method 95 % upper for the primary floor is about
  0.068 (ratio 0.78), still below 1 (independent audit, 2026-10-08).

Limits:

- **The verifier band is borrowed, and probably too small for this
  frame.** The 0.001 per contrast was measured on the 55-map corpus (W2.7
  report § 1); no verifier re-invocation has been measured on the 487-tile
  frame. Each cell here holds 393 to 441 detections, so one verifier
  decision moves F1 by about 0.0011 to 0.0013, and the whole band is about
  one decision; the 2.4 % same-week re-invocation flip rate would be about
  ten. Scaled from the 55-map corpus (about 11 times as many detections),
  the band would be about 0.003 to 0.005 per contrast. At 0.003 the primary
  gap changes are 1.14 and 1.17 times their floors; at 0.005, 1.05 and
  1.08. Both still clear the point floor, with a thin margin. The floors
  are proposer-stage floors plus that band.
- **Gemini 3 image at (0.15, k9)** follows a unanimity vote path at every
  K' ≤ 5, so its carried SD is the k10 cell's (0.0164). This affects only
  that cell's date-component floor, in the conservative direction.
- **No floor at K = N is measured; each is carried.** The Gemini 3 image
  arm's SD rises with K (power exponent +0.31: unanimity rungs keep fewer,
  more borderline detections), so the power fit reads 0.0164 at K = 10
  against direct values of 0.0119 to 0.0129 at K' = 6 to 9; the rule is
  conservative there, and the direct column shows by how much. The
  five-pass cells' K = 5 SDs rest on subsets of at most four passes, and
  their upper bounds are about twice their points.
- The 95th percentile assumes normal differences and exchangeable passes
  within an arm (W2.7 report § 6b, floors-v2 § 7). The § 3 floors are
  proposer-only consensus from 30-pass pools; its K = 10, t = 10 value
  rests on six pairs.

## 8. Flags

- **The Gemini 3 image K = 10 union is 15.0 % smaller than the original**
  (3,456 against 4,065; the passes agree more; Stage 2 card § 8, F-cal). Its F1
  moved by −0.0081 only. Raised as a surprise; the chain that built it rebuilds
  the original unions byte for byte, so it is not a pipeline artefact.
- **Gemini 3 text changes more tiles between dates than within an
  execution, without changing F1** (§ 6): 32 of 487 tiles (6.6 %) differ
  between bridge and original, against a 95th percentile of 5.3 % between
  disjoint five-pass rungs of the bridge, which should flip more than two
  K = 10 cells. Fixed and broken balance (12 and 14). The date-plus-mode
  component shows in which tiles fail, not in how many, as the verifier's
  balanced cross-date flips did on the 55-map corpus (W2.7 report § 6c).
- **§ 4 item 4 is reworded** (2026-10-08): it said the family difference "is
  an inversion"; the 3.7 gaps are not rejected and sit inside their floors,
  so the runs show no resolved 3.7 gap (not a demonstrated parity), and the
  family difference that remains is the loss of Gemini 3's text advantage
  (§ 7).
- **Two Stage 2 outputs were never committed**, although the Stage 2 card
  § 7 item 12 lists both: every arm's `scoring/` (the deduplicated passes)
  and the `verify_g3_repaired/` copies of `g3-text`, `g3-image` and
  `g3-text-temp1`. §§ 5–7 rebuilt the passes from the committed pass
  GeoJSONs with `scripts/modality_bridge_union.py` (seven unions
  byte-identical to the committed ones; 45 pass files byte-identical to
  sapphire's uncommitted copies) and read `verify_g3/`, whose probabilities
  equal the repaired copies' for every candidate (their `parse_repair.json`
  records no change).
- T 1.0 text passes lost more tiles to flex-retry failures (31 across five
  passes against 11 across ten at T 0.7), all recovered in round 1.
- The original Gemini 3 image leg's six recovery tiles went inline (Stage 2
  card § 8); negligible here.
- Batch metas do not book thinking tokens separately; the audited costs
  carry them.

## 9. Cost (audited, batch)

Stage 1: Gemini 3 text US$8.39, Gemini 3 image US$19.52, 3.7 text US$8.64,
3.7 image US$18.93, fifth leg US$12.33, T 1.0 text US$4.26, T 1.0 image
US$9.76 (US$81.83). Stage 2, ten legs: US$12.69. In all, US$94.52, plus the
cache storage (shortened by deleting each cache once its pass landed,
D52). The 3.7 cache reads are priced at the rate card's US$0.0375/M. At the
US$0.075/M the September invoices show, add about US$9. §§ 5–7 made no
Application Programming Interface (API) call.

## Changelog

### 2026-10-08 — Wording after the independent audit

An independent audit of `scripts/modality_bridge_floors.py` at `3d3cfe18e`
(`reports/s163-agent-records/run-b-floors-audit.md`) found no code defect and
recomputed the primary gap changes, their interaction p and the primary floor
exactly. Its prose findings are applied: "parity" becomes "no resolved gap"
(§§ 4, 7, 8; non-rejection below a floor is not an equivalence test); the
D45 verdict takes the re-screen's own label; the verifier band's likely
understatement is quantified (§ 7 Limits); the flip yardstick's fixed verifier
is stated (§ 6); the cached-against-inline 3.7 image ratios are restated at the
operating points (0.74 and 0.32; formerly "0.74 and 0.37 at the best points").
No number from `floors/` changed.

### 2026-10-08 — Items 4, 6 and 7: gap-change test, date component, floors

Scoring plan items 4, 6 and 7 (Stage 1 card § 9) computed with
`scripts/modality_bridge_floors.py` (`984c12505`, `38505f81f`; results in
`floors/`), behind gates that first reproduce every cell, gap and p of
§§ 2–3 exactly. New §§ 5 (gap change, interaction permutation), 6 (date
component, same-tile flips) and 7 (floors); the former §§ 5 and 6 are now
§§ 8 and 9.

| Claim | Before | After |
|---|---|---|
| § 3, gap change | −0.0529 and −0.0547, "descriptive; no interaction permutation yet" | the same, interaction p 0.0047 and 0.0040, 1.24 and 1.28 times the floor |
| § 4 item 1 | text advantage "about +0.05 F1 (p 0.003)"; cells "within 0.01 F1" of the originals | the same, plus 1.5 times its floor; the gap change resolved; each cell at most 0.46 of its floor |
| § 4 item 3 | "image leads, by −0.016 (p 0.074) and −0.010 (p 0.25)" | the same numbers, at 0.69 and 0.43 of their floors: no resolved gap |
| § 4 item 4 | the family difference "is an inversion that remains" | the family difference remains (−0.075 and −0.068, p < 0.0001, 1.9 and 1.7 times the floor); no resolved 3.7 gap, so no inversion (not a demonstrated parity) |
| § 4 item 5 | — | new: the D45 verdict, clears the point floor and inside its upper bound |
| Status | floors, interaction and MCC gaps not computed | MCC gaps not computed |

Unchanged: every cell, gap and p of §§ 2–3 (reproduced exactly), and
§§ 1, 8 (formerly 5, three flags added) and 9 (formerly 6).

### 2026-10-07 — Original publication (Session 163)

First scoring of Run B (`aeff1e207`, driver
`scripts/modality-bridge-2026-10-07-score.sh`), written overnight under the
PI's delegation, for review.
