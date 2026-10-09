# Run B, the modality bridging pair: first findings

> **Last revised**: 2026-10-08 (Run C: the verifier's re-invocation noise
> measured on these cells, and § 7's floors with it, in the new § 7a;
> earlier the same day, the 55-map 3.7 result, scoring plan items 4, 6 and
> 7, and the audit's wording). See
> [§ Changelog](#changelog) for revision history.

**Status: SCORED, FOR THE PRINCIPAL INVESTIGATOR'S (PI'S) REVIEW.** Point
estimates and tile-swap p-values (§§ 2–3), the gap-change interaction test
(§ 5), the date component per cell (§ 6), and the D45/D46 replicate floors
(§ 7), every run behind the six-cell anchor gate; § 7a adds Run C, three
verifier replicates of every leg, and the floors with the verifier's
measured noise (`scripts/modality_bridge_verifier_sd.py`, which first
reproduces every committed set tile for tile). Not yet computed: Matthews
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
   inversion", these runs show no inversion on this frame. They do not
   show parity in the strict sense: the evidence is that the test does not
   reject and each 3.7 gap sits below its floor, which is not a test of
   equivalence. **At deployment scale the inversion is there:** on the
   55-map corpus (8,541 tiles), 3.7 image at K = 3 beats 3.7 text at
   K = 3 by +0.0351 F1 (BH p < 0.0001) and +0.0484 tile-MCC, with text at
   its post-hoc best threshold and image at its carried point
   (`results/gemini37-image-55map-2026-09-13/findings.md` § 1, P3), mostly
   through recall (0.951 against 0.892). The two 55-map arms ran about two
   weeks apart (text passes 2026-08-29 to 08-31, image 2026-09-13), but
   every 3.7 cell here moves at most
   0.0094 between its original date and Run B's (§ 2), well under the 55-map
   lead. The gold-standard frame cannot resolve a gap of that size, and the
   cached arm's −0.0164 points the same way. PI ruling D53 adopts the
   55-map result for the paper.
5. **Under D45 the family claim stands on these runs: every gap change
   clears its point floor, and every one sits inside its floor's upper
   bound.** All ten gap changes reject and clear their point floors (1.24
   to 1.87 times),
   the floors re-derived from § 3 of the W2.7 report (1.36 to 1.79) and the
   direct-SD sensitivity (1.40 to 1.87), but none clears the upper bound of
   its floor (0.66 to 0.99). The K = 10 contrast the claim was first made
   on is the narrowest (1.24 and 1.28); the K-matched and fully matched
   contrasts are clearer (1.66 to 1.87). **With the verifier's noise
   measured (Run C, § 7a)** in place of the borrowed band, every point
   ratio rises (1.27 to 1.93; the primaries 1.27 and 1.33), and the
   verdict stands; one upper reading reaches 1.01 (3.7 with the Gemini 3
   verifier against the Gemini 3 K = 5 rung).

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
  These floors carry the borrowed verifier band; § 7a replaces it with the
  verifier's measured noise, which raises every ratio slightly.

Limits:

- **The verifier band is borrowed; it was suspected too small for this
  frame, and the measurement does not bear that out** (Run C, § 7a,
  2026-10-08). The 0.001 per contrast was measured on the 55-map corpus
  (W2.7 report § 1). Each cell here holds 393 to 441 detections, so one
  verifier decision moves F1 by about 0.0011 to 0.0013, and the whole band
  is about one decision; the 2.4 % same-week re-invocation flip rate would
  be about ten. Scaled from the 55-map corpus (about 11 times as many
  detections), the band would be about 0.003 to 0.005 per contrast. At
  0.003 the primary gap changes are 1.14 and 1.17 times their floors; at
  0.005, 1.05 and 1.08. The floors are proposer-stage floors plus that
  band. Measured on these cells and added in quadrature, the verifier's
  noise lowers every gap-change floor below its banded value (§ 7a).
- **The Gemini 3 verifier's re-invocation noise has been measured on a
  487-tile gold-standard frame of 384-pixel tiles, against the same
  reference** (corrected 2026-10-08: this note and the audit said none had
  been). Five verifications of the same candidates by Gemini 3 Flash at
  T 0.0 gave single-run F1 SDs of 0.0025 to 0.0072 per cell
  (`results/verifier-robustness/verifier-robustness-findings.md` § 2,
  June 2026, scored on `inputs/vectors/bounds/384/full_evaluation_bounds.geojson`).
  Clarified 2026-10-08 (Run C): the range spans two cells, 0.0032 to
  0.0072 for the 384-pixel cell and 0.0025 to 0.0048 for a 256-pixel one
  (`results/verifier-robustness/robustness_summary_T0.0.json`).
  The **Gemini 3.7 verifier's** had not been measured before Run C. It
  samples at its default temperature, 1.0, whatever is sent, so it may be
  noisier. Added
  in quadrature for each of the four cells, in place of the band, a
  per-cell verifier SD moves the two primary gap changes' ratios as
  follows: 0.0025 gives 1.27 and 1.31; 0.0072 gives 1.07 and 1.10; 0.010
  gives 0.94 and 0.97. The fully matched gap changes stay above 1 up to
  0.012 (1.24 and 1.14). So the family claim holds on the matched
  contrasts for any plausible verifier noise; whether the original K = 10
  contrast clears its floor depends on the 3.7 verifier's. Run C (PI
  ruling D56, `planning/pi-decisions-2026-09-20.md`) measured it by two
  further verifications of all ten legs (§ 7a): the 3.7 verifier's per-cell
  SD is 0.0003 to 0.0021 (pooled 0.0011) and the Gemini 3 verifier's 0.0011
  to 0.0034 (pooled 0.0022), well under the 0.0087 at which the primary
  would reach its floor; with them the primaries are 1.27 and 1.33.
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

## 7a. The verifier's re-invocation noise, measured (Run C)

**What ran.** On 2026-10-08 each of the ten Stage 2 legs was verified twice
more (replicates 2 and 3; the committed legs, verified on 2026-10-07, are
replicate 1). Same verifier, config, temperature and crops, on the Batch API
(PI ruling D56; card `planning/run-c-verifier-reinvocation-2026-10-08.md`).
Every replicate's request file equals the original's byte for byte (34,332
of 34,332 lines), so only the invocation differs. All twenty legs booked
every candidate. One response did not parse and was repaired to the value
booked (card § 9). Audited cost US$25.32.

**Method** (card § 7, fixed before the first lodge). Each committed set of
§§ 2, 5 and 7 is scored at its own point with each replicate's
probabilities; the K = 5 rungs re-inherit them within 10 m. Gate, passed:
replicate 1 reproduces all 20 committed sets tile for tile. Per cell: the SD
of the three F1s (two degrees of freedom) and its 95 % chi-square interval,
0.52 to 6.3 times the estimate. "Split" counts the candidates the cell's
vote gate admits whose accept/reject decision differs between replicates.
The floors are § 7's, with 1.96 · √(Σ proposer SD² + Σ verifier SD²) in
place of the 0.001-per-contrast band; the proposer SDs are § 7's, read from
`floors/floors.json`. Script `scripts/modality_bridge_verifier_sd.py`;
results `verifier-sd/verifier_sd.json`, `verifier-sd/floors_with_verifier.json`,
`verifier-sd/summary.csv` and `verifier-sd/gates.json`; 35 s on sapphire.

**Cells** (F1 at 20 m, 487-tile frame):

| Cell (point) | Verifier | F1, replicates 1 / 2 / 3 | SD (95 % interval) | Split |
|---|---|---|---:|---:|
| Gemini 3 text (0.15, k10) | Gemini 3 | 0.8916 / 0.8905 / 0.8932 | 0.0014 (0.0007–0.0085) | 19 of 942 |
| Gemini 3 image (0.15, k10) | Gemini 3 | 0.8393 / 0.8364 / 0.8393 | 0.0016 (0.0009–0.0104) | 13 of 580 |
| Gemini 3 image (0.15, k9) | Gemini 3 | 0.8331 / 0.8304 / 0.8341 | 0.0019 (0.0010–0.0121) | 14 of 680 |
| Gemini 3 text, K = 5 rung (0.15, k5) | Gemini 3 | 0.8849 / 0.8849 / 0.8868 | 0.0011 (0.0006–0.0068) | 23 of 1,086 |
| Gemini 3 image, K = 5 rung (0.15, k5) | Gemini 3 | 0.8239 / 0.8231 / 0.8269 | 0.0020 (0.0010–0.0123) | 16 of 670 |
| 3.7 text (0.10, k5) | Gemini 3 | 0.9154 / 0.9131 / 0.9097 | 0.0029 (0.0015–0.0180) | 7 of 466 |
| 3.7 text (0.75, k5) | Gemini 3.7 | 0.9265 / 0.9271 / 0.9283 | 0.0009 (0.0005–0.0059) | 10 of 466 |
| 3.7 text (0.80, k5) | Gemini 3.7 | 0.9265 / 0.9282 / 0.9294 | 0.0015 (0.0008–0.0092) | 11 of 466 |
| 3.7 image (0.10, k5) | Gemini 3 | 0.9160 / 0.9218 / 0.9158 | 0.0034 (0.0018–0.0216) | 10 of 460 |
| 3.7 image (0.88, k5) | Gemini 3.7 | 0.9288 / 0.9272 / 0.9282 | 0.0008 (0.0004–0.0050) | 14 of 460 |
| 3.7 image (0.90, k5) | Gemini 3.7 | 0.9288 / 0.9294 / 0.9292 | 0.0003 (0.0002–0.0019) | 15 of 460 |
| 3.7 image cached (0.10, k5) | Gemini 3 | 0.9318 / 0.9343 / 0.9307 | 0.0018 (0.0009–0.0114) | 4 of 455 |
| 3.7 image cached (0.95, k5) | Gemini 3.7 | 0.9363 / 0.9377 / 0.9393 | 0.0015 (0.0008–0.0094) | 17 of 455 |
| 3.7 image cached (0.90, k5) | Gemini 3.7 | 0.9352 / 0.9377 / 0.9394 | 0.0021 (0.0011–0.0133) | 15 of 455 |
| Gemini 3 text, T 1.0 (0.15, k5) | Gemini 3 | 0.8824 / 0.8814 / 0.8786 | 0.0020 (0.0010–0.0123) | 17 of 1,018 |
| Gemini 3 image, T 1.0 (0.15, k5) | Gemini 3 | 0.8242 / 0.8228 / 0.8210 | 0.0017 (0.0009–0.0104) | 12 of 588 |

Where a cell's operating point and best point coincide, one row serves both.

**By verifier:**

- **Gemini 3:** per-cell SDs 0.0011 to 0.0034. Pooled over the best sets of
  its seven legs, 0.0022 (14 degrees of freedom; 95 % 0.0016 to 0.0035).
  June's single-run SDs, from five verifications at T 0.0 (§ 7 Limits), were
  0.0025 to 0.0072: 0.0032 to 0.0072 over the five vote levels of its
  384-pixel cell and 0.0025 to 0.0048 over those of a 256-pixel cell
  (`results/verifier-robustness/robustness_summary_T0.0.json`). These are
  lower (flagged, § 8).
- **Gemini 3.7:** per-cell SDs 0.0003 to 0.0021. Pooled over its three legs,
  0.0011 (6 degrees of freedom; 0.0007 to 0.0025).
- **Responses.** Between any two replicates, Gemini 3 returns byte-identical
  text for 48.0 to 52.5 % of candidates and changes 13 to 17 % of
  probabilities; Gemini 3.7 never returns identical text and changes 35 to
  43 % of probabilities. At the cells' points Gemini 3.7 splits more
  decisions (2.1 to 3.7 % of admitted candidates, against 0.9 to 2.4 %), yet
  its F1 SDs are the smaller (flagged, § 8).
- **Day.** Replicate 1 ran a day before 2 and 3. Replicate 1 minus the mean
  of 2 and 3 ranges from −0.0034 to +0.0040, with both signs on both
  verifiers: no day-to-day shift shows.

**Gaps** against floors with the measured verifier SD (point; the upper
reading uses each cell's upper proposer SD):

| Gap | Estimate | Floor, band (ratio) | Floor, measured (ratio) | Upper ratio, band → measured | Break-even verifier SD |
|---|---:|---:|---:|---:|---:|
| Gemini 3, K = 10 | +0.0523 | 0.0349 (1.50) | 0.0342 (1.53) | 0.80 → 0.81 | 0.0144 |
| Gemini 3, K = 5 rung | +0.0609 | 0.0280 (2.17) | 0.0274 (2.22) | 1.40 → 1.42 | 0.0197 |
| Gemini 3, T 1.0, K = 5 | +0.0582 | 0.0311 (1.87) | 0.0305 (1.91) | 1.03 → 1.05 | 0.0180 |
| 3.7, Gemini 3 verifier | −0.0006 | 0.0232 (0.03) | 0.0239 (0.02) | 0.01 → 0.01 | — |
| 3.7, 3.7 verifier | −0.0023 | 0.0234 (0.10) | 0.0226 (0.10) | 0.05 → 0.05 | — |
| 3.7 text − cached image, Gemini 3 verifier | −0.0164 | 0.0239 (0.69) | 0.0238 (0.69) | 0.31 → 0.31 | — |
| 3.7 text − cached image, 3.7 verifier | −0.0098 | 0.0225 (0.43) | 0.0218 (0.45) | 0.18 → 0.18 | — |

**Gap changes:**

| Gap change | Estimate | Floor, band (ratio) | Floor, measured (ratio) | Upper ratio, band → measured | Direct, band → measured | § 3-derived, without → with verifier | Break-even verifier SD |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Primary:** 3.7 (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0529 | 0.0426 (1.24) | 0.0417 (1.27) | 0.66 → 0.68 | 1.40 → 1.43 | 1.36 → 1.32 | 0.0087 |
| **Primary:** all-3.7 − Gemini 3 K = 10 | −0.0547 | 0.0427 (1.28) | 0.0410 (1.33) | 0.66 → 0.68 | 1.45 → 1.51 | 1.41 → 1.39 | 0.0093 |
| 3.7 (Gemini 3 verifier) − Gemini 3 K = 5 rung | −0.0615 | 0.0370 (1.66) | 0.0364 (1.69) | 0.99 → 1.01 | — | 1.47 → 1.43 | 0.0129 |
| all-3.7 − Gemini 3 K = 5 rung | −0.0633 | 0.0371 (1.70) | 0.0355 (1.78) | 0.96 → 0.99 | — | 1.52 → 1.51 | 0.0134 |
| 3.7 (Gemini 3 verifier) − Gemini 3 T 1.0 | −0.0588 | 0.0394 (1.49) | 0.0388 (1.52) | 0.82 → 0.83 | — | 1.41 → 1.37 | 0.0116 |
| all-3.7 − Gemini 3 T 1.0 | −0.0605 | 0.0395 (1.53) | 0.0380 (1.59) | 0.81 → 0.83 | — | 1.45 → 1.44 | 0.0121 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0687 | 0.0429 (1.60) | 0.0417 (1.65) | 0.81 → 0.82 | 1.81 → 1.86 | 1.77 → 1.73 | 0.0141 |
| Fifth leg (3.7 verifier) − Gemini 3 K = 10 | −0.0621 | 0.0422 (1.47) | 0.0405 (1.53) | 0.72 → 0.74 | 1.67 → 1.74 | 1.60 → 1.58 | 0.0121 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 T 1.0, fully matched | −0.0746 | 0.0398 (1.87) | 0.0387 (1.93) | 0.95 → 0.97 | — | 1.79 → 1.75 | 0.0164 |
| Fifth leg (3.7 verifier) − Gemini 3 T 1.0, fully matched | −0.0680 | 0.0390 (1.74) | 0.0375 (1.81) | 0.86 → 0.88 | — | 1.63 → 1.61 | 0.0145 |

"Break-even" is the verifier SD that, on all four cells alike, brings the
point ratio to 1; "—" in that column means the gap is below its floor with
no verifier noise at all. § 3's committed floors carry no band, so adding
the verifier lowers those ratios slightly.

**Verifier sensitivities** on the gap changes' point ratios: the pooled SD
of each cell's verifier family, that SD at its 95 % upper bound (added after
the results), and each cell at its own upper bound (pre-specified):

| Gap change | Measured per cell | Pooled | Pooled, upper | Each cell at its upper |
|---|---:|---:|---:|---:|
| **Primary:** 3.7 (Gemini 3 verifier) − Gemini 3 K = 10 | 1.27 | 1.28 | 1.24 | 0.72 |
| **Primary:** all-3.7 − Gemini 3 K = 10 | 1.33 | 1.32 | 1.29 | 1.08 |
| 3.7 (Gemini 3 verifier) − Gemini 3 K = 5 rung | 1.69 | 1.71 | 1.64 | 0.87 |
| all-3.7 − Gemini 3 K = 5 rung | 1.78 | 1.77 | 1.71 | 1.34 |
| 3.7 (Gemini 3 verifier) − Gemini 3 T 1.0 | 1.52 | 1.53 | 1.47 | 0.80 |
| all-3.7 − Gemini 3 T 1.0 | 1.59 | 1.59 | 1.54 | 1.18 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 K = 10 | 1.65 | 1.64 | 1.59 | 1.07 |
| Fifth leg (3.7 verifier) − Gemini 3 K = 10 | 1.53 | 1.52 | 1.48 | 1.18 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 T 1.0, fully matched | 1.93 | 1.92 | 1.85 | 1.16 |
| Fifth leg (3.7 verifier) − Gemini 3 T 1.0, fully matched | 1.81 | 1.81 | 1.75 | 1.28 |

Reading:

- **The verifier adds less than the band assumed.** Measured per cell and
  added in quadrature, it lowers every gap change's floor, so every point
  ratio rises: the primaries from 1.24 and 1.28 to 1.27 and 1.33, the
  K = 5 contrasts to 1.69 and 1.78, the T 1.0 ones to 1.52 and 1.59, and
  the fully matched ones to 1.93 and 1.81. The audit's suspicion that the
  0.001 band was too small (§ 7 Limits) is not borne out (flagged, § 8).
- **The K = 10 contrast clears its floor with the verifier measured.** It
  would need a per-cell verifier SD of 0.0087 (Gemini 3 verifier) or 0.0093
  (all-3.7) to reach its floor. The largest measured is 0.0034, and the
  pooled upper bounds are 0.0035 (Gemini 3) and 0.0025 (Gemini 3.7).
- **No contrast changes side of its point, upper, direct or § 3 floor,
  save one upper reading.** 3.7 (Gemini 3 verifier) − Gemini 3 K = 5 rung
  moves from 0.99 to 1.01 times its upper floor; every other gap change
  stays inside its upper bound (0.68 to 0.99).
- **Three replicates bound one cell's SD loosely.** With every cell at its
  own two-degree-of-freedom upper bound at once (6.3 times its SD), the
  three gap changes built on the inline 3.7 cells under the Gemini 3
  verifier fall below 1 (0.72, 0.87 and 0.80), because those two cells'
  SDs are the largest measured (0.0029 and 0.0034). Every other gap change
  stays above 1 (1.07 to 1.34). Pooled within each verifier, the upper
  bounds leave every gap change at 1.24 or more.

Limits:

- Three replicates per cell. The per-cell SDs are rough; the pooled SDs
  assume one SD per verifier across its cells.
- The replicates measure re-invocation within a day and across one day, on
  the batch tier. They do not cover longer drift or the originals' real-time
  tiers (§ 6 compares those).
- Verifier noise is taken as independent of the proposer's and between
  cells, since each cell's leg is a separate invocation. The K = 5 rungs
  inherit probabilities from the K = 10 legs, so they share those legs'
  verifier draws; no contrast pairs a rung with its own K = 10 cell.
- Otherwise the floors are § 7's, with the same carried proposer SDs and
  normality assumption.

## 8. Flags

- **Run C's verifier noise runs against three expectations** (§ 7a; raised
  as findings, not explained away):
  - **It is smaller than the band assumed.** The audit and § 7 Limits
    expected the 0.001-per-contrast band to understate it; measured, it
    lowers every gap-change floor and raises every ratio.
  - **The Gemini 3.7 verifier is the steadier in F1, not the noisier.** It
    samples at T 1.0 and never repeats a response, changes 35 to 43 % of
    probabilities between replicates (Gemini 3: 13 to 17 %) and splits more
    decisions at the cells' points (2.1 to 3.7 % against 0.9 to 2.4 %), yet
    its per-cell F1 SDs are the smaller (pooled 0.0011 against 0.0022).
  - **The Gemini 3 verifier's SDs (0.0011 to 0.0034) sit below June's**
    0.0025 to 0.0072 (0.0032 to 0.0072 on its 384-pixel cell). June's run
    differs in tier (real-time flex), in its cells (the 1-of-5 unions of
    3,736 and 2,558 candidates, one of them on 256-pixel tiles) and in its
    points, so the two are not the same measurement.

  Gemini 3 returns byte-identical text for about half the candidates
  between any two replicates; its one unparseable response in Run C
  (`g3-image-temp1`, `candidate_02479`, replicate 3) is the same text as
  replicate 1's, which failed at the same position.
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

Run C (§ 7a), twenty verifier legs on 2026-10-08: US$25.32 audited
(`scripts/audit_verifier_cost.py`, record
`outputs/modality-bridge-2026-10-07/stage2/checks/run-c-cost-audit.json`;
US$12.66 per replicate, against the US$12.69 of Run B's ten legs), within
D56's US$50. The analysis made no API call.

## Changelog

### 2026-10-08 — Run C: the verifier's re-invocation noise, measured

Run C (PI ruling D56; card `planning/run-c-verifier-reinvocation-2026-10-08.md`)
verified each of the ten Stage 2 legs twice more with byte-identical
requests (US$25.32). New § 7a: per-cell verifier SDs from three replicates,
flips, and § 7's floors with the measured verifier variance in quadrature
in place of the 0.001-per-contrast band (`scripts/modality_bridge_verifier_sd.py`,
results `verifier-sd/`; replicate 1 reproduced all 20 committed sets tile
for tile). New § 8 flag: the noise runs against three expectations. § 9
gains Run C's cost. § 4 item 5, § 7's reading and § 7 Limits point to § 7a;
§ 7 Limits' June range is clarified (it spans a 384-pixel and a 256-pixel
cell) and its "probably too small" is answered.

| Claim | Before | After |
|---|---|---|
| Verifier noise on this frame | Gemini 3: June's 0.0025–0.0072; 3.7: never measured | Gemini 3: 0.0011–0.0034 per cell (pooled 0.0022); 3.7: 0.0003–0.0021 (pooled 0.0011) |
| Primary gap changes, of floor | 1.24 and 1.28 (band) | 1.27 and 1.33 (measured verifier) |
| K = 5, T 1.0, fully matched gap changes | 1.66, 1.70; 1.49, 1.53; 1.87, 1.74 | 1.69, 1.78; 1.52, 1.59; 1.93, 1.81 |
| Gap changes' upper readings | 0.66 to 0.99 | 0.68 to 1.01 (one at 1.01) |
| Break-even per-cell verifier SD, primaries | "about 0.009" | 0.0087 and 0.0093 |

Unchanged: every cell, gap, gap change and p of §§ 2–6, and every number
of § 7 and `floors/`, which still report the banded floors. Commits: the
launcher's replicates `88103aef1`, the card `4b199a2ef`, the analysis
`a79cb4d40`, `cc9a21c68` and `65b73ab21`, the legs `6c1e82014` and
`9793307a5`, the results `494309a43` and `2283f2054`, the cost record
`f70cd09f3`.

### 2026-10-08 — The 55-map 3.7 result; the verifier's measured noise

§ 4 item 4 now gives the deployment-scale 3.7 result beside this frame's:
on the 55-map corpus, 3.7 image beats 3.7 text by +0.0351 F1 (BH
p < 0.0001), mostly recall, which this frame cannot resolve. PI ruling D53
adopts it for the paper. § 7 Limits corrected: the Gemini 3 verifier's
re-invocation noise was measured in June on a 487-tile gold-standard frame
(0.0025 to 0.0072 F1 per cell); the note and the audit had said it never
was. The sensitivity of the primary and fully matched ratios to a per-cell
verifier SD is added; Run C (D56) measures the 3.7 verifier's. No number
from `floors/` changed.

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
