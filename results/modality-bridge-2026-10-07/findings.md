# Run B, the modality bridging pair: first findings

> **Last revised**: 2026-10-15 (restated with the rows re-verified on
> 2026-10-13 and the cluster-origin route, PI rulings D62 (1) and D65 (6);
> the floors and verifier-SD scripts moved onto the origin route; the
> 2026-10-09 re-run under the D50/D51 scorer recorded, D58 Q9; the cost total
> corrected). See [§ Changelog](#changelog) for revision history.

**Status: SCORED AND RESTATED, FOR THE PRINCIPAL INVESTIGATOR'S (PI'S)
REVIEW.** Point estimates and tile-swap p-values (§§ 2–3), the gap-change
interaction test (§ 5), the date component per cell (§ 6), and the D45/D46
replicate floors (§ 7), every run behind the six-cell anchor gate; § 7a adds
Run C, three verifier replicates of every leg, and the floors with the
verifier's measured noise. Not yet computed: Matthews correlation
coefficient (MCC) gaps. Every number is the 2026-10-15 restatement (D65 (2)
and (6)): the cells and gap tests from
`scripts/modality-bridge-2026-10-07-score.sh`, and §§ 5–7a from
`scripts/modality_bridge_floors.py` and
`scripts/modality_bridge_verifier_sd.py`, all at `02339bd98`,
on the D50/D51 scorer (pull request #26, merged as `fefb73f2b`) and the
D62 (1) cluster-origin route. They read the 162 rows of the ten legs that
were re-verified on 2026-10-13 (§ 1). The six-cell anchor gate still checks
the instrument against the six original cells as registered, on the legs as
run. The values this document carried until 2026-10-15 are in the
[changelog](#changelog).

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

**Rows re-verified on 2026-10-13 (D65 (6)).** Some candidates' verifier
crops had been cut from the neighbouring sheet's raster, so the verifier saw
no map and answered at most 0.05. On 2026-10-13 they were re-verified on
crops from their own sheet (PI ruling D62 (1) step 2; run record
`outputs/wrong-sheet-reverify-2026-10-13/record.json`, booked
2026-10-13T06:44Z) and booked in each leg's `_repaired/` copy: 162 rows of
the ten legs (Gemini 3 text 17, Gemini 3 image 34, 3.7 text 12 under each
verifier, 3.7 image 8 under each, the fifth leg 10 under each, T 1.0 text
16, T 1.0 image 35), US$0.127524. Every number below uses them, so those
rows carry a verification date of 2026-10-13, not 2026-10-07; the floors'
and verifier SD's `meta.reverification` records them per leg.

## 2. Cells (F1 at 20 m, 487-tile frame)

| Cell | Bridge F1 (point) | Original F1 | Bridge − original | MCC |
|---|---:|---:|---:|---:|
| Gemini 3 text, K = 10, Gemini 3 verifier | 0.8986 (0.15, k10) | 0.9017 | −0.0031 | 0.8048 |
| Gemini 3 image, K = 10, Gemini 3 verifier | 0.8386 (0.15, k9); best 0.8449 | 0.8458 | −0.0072 | 0.8072 |
| 3.7 text, K = 5, Gemini 3 verifier | 0.9241 (0.10, k5) | 0.9238 | +0.0004 | 0.8184 |
| 3.7 text, K = 5, 3.7 verifier | 0.9352 (0.80, k5) | 0.9364 | −0.0012 | 0.8230 |
| 3.7 image, K = 5, Gemini 3 verifier | 0.9259 (0.10, k5); best 0.9267 (0.05, k5) | 0.9353 | −0.0095 | 0.8300 |
| 3.7 image, K = 5, 3.7 verifier | 0.9375 (0.90, k5) | 0.9408 | −0.0033 | 0.8482 |
| 3.7 image **cached**, Gemini 3 verifier | 0.9404 (0.10, k5); best 0.9409 (0.05, k5) | — | — | 0.8300 |
| 3.7 image **cached**, 3.7 verifier | 0.9437 (0.90, k5); best 0.9448 | — | — | 0.8338 |
| Gemini 3 text, **T 1.0**, K = 5 | best 0.8908 (0.15, k5) | — | — | — |
| Gemini 3 image, **T 1.0**, K = 5 | best 0.8299 (0.15, k5) | — | — | — |

Source: `*/analysis.json` (`operating_point`, `image_best`). "Original" is
each original cell as it now scores, at its registered point, with its own
re-verified rows (`results/grid-2026-08-18/`, `results/image-b-gs-2026-08-28/`,
`results/gemini37-screen-2026-08-28/`, `results/gemini37-image-gs-2026-09-01/`
as restated on 2026-10-15); as registered on the legs as run they were
0.8961, 0.8412, 0.9139, 0.9265, 0.9254 and 0.9308. The 3.7 image original
under the Gemini 3 verifier now takes its best at (0.05, k5), 0.9381, above
its registered point. "Bridge − original" is the difference of the unrounded
F1s, date plus serving mode (batch against the originals' real-time tiers),
never date alone (Stage 1 card § 9 item 6); § 6 tests it.

Under both the inline and the cached 3.7 image arms the Gemini 3 verifier's
best point moved from (0.10, k5) to (0.05, k5): at 0.05 the re-verified rows
that the verifier now accepts enter with every other candidate, and the
verifier rejects almost nothing (§ 7a).

## 3. Gaps, text − image (tile-swap permutation, 10,000, 487 tiles)

| Pair | Bridge gap (p) | Original gap (p) |
|---|---:|---:|
| Gemini 3, K = 10 | **+0.0536 (0.0018)** | +0.0559 (0.0005) |
| Gemini 3, K = 5 (inherited rung) | +0.0624 (0.0001) | — |
| Gemini 3, **T 1.0**, K = 5 | **+0.0608 (< 0.0001)** | — |
| 3.7, Gemini 3 verifier | −0.0026 (0.77) | −0.0143 (0.16) |
| 3.7, 3.7 verifier | −0.0023 (0.75) | −0.0044 (0.68) |
| 3.7 text − **cached** image, Gemini 3 verifier | −0.0168 (0.093) | — |
| 3.7 text − **cached** image, 3.7 verifier | −0.0096 (0.25) | — |

Gap change against Gemini 3: −0.0562 (3.7, Gemini 3 verifier) and −0.0559
(all 3.7), interaction p 0.0060 and 0.0031 (§ 5). Sources: `gap_test.json`
(best points, as the originals), `k5/gap_test.json`,
`additions/gap_test.json`; each gap against its floor in § 7. The original
gaps are the restated originals' (`results/image-b-gs-2026-08-28/analysis.json`
`head_to_head_20m`; `results/gemini37-image-gs-2026-09-01/gap_test.json`);
as registered they were +0.0549 (0.0010), −0.0115 (0.25) and −0.0043 (0.68).
"< 0.0001" means no permutation of 10,000 reached the observed value (D42
default (d)).

## 4. What it says, against the floors

1. **The modality result replicates on one day, on one serving mode.**
   Gemini 3 keeps a text advantage of about +0.05 F1 (p 0.002), 1.7 times
   its floor (§ 7). Gemini 3.7 shows none, under either verifier. The change
   between the families, −0.056 and −0.056, is resolved (interaction
   p 0.006 and 0.003, § 5) and 1.4 times its own floor. Each bridge
   cell sits within 0.01 F1 of its original, at most 0.46 of its run-to-run
   floor (§ 6).
2. **Temperature does not explain it.** At T 1.0, the temperature 3.7
   actually samples at, the Gemini 3 text advantage is +0.061 (p < 0.0001,
   1.9 times its floor), as large as at T 0.7.
3. **Nor does the request shape.** Sent through the explicit cache, as
   Gemini 3 image is, 3.7 image still shows no text advantage. If anything,
   image leads, by −0.017 (p 0.093) and −0.010 (p 0.25), but neither is
   rejected and they sit at 0.66 and 0.42 of their floors: no resolved
   gap, and no image lead. The cached 3.7 image cells score a little above
   the inline ones at the operating points (0.9404 against 0.9259; 0.9437
   against 0.9375), differences of 0.71 and 0.32 of the floor of two
   independent 3.7 image cells (1.96 · √(SD² + SD²) + 0.001 from § 7's cell
   SDs at those points); not tested by permutation.
4. With temperature, request structure, tier, K and day matched, the family
   difference remains once only the model and its thinking level differ:
   the fully matched gap change is −0.078 and −0.070 (p < 0.0001), 1.9 and
   1.8 times its floor (§ 7). What remains is Gemini 3's text advantage
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
   0.0095 between its original date and Run B's (§ 2), well under the 55-map
   lead. The gold-standard frame cannot resolve a gap of that size, and the
   cached arm's −0.0168 points the same way. PI ruling D53 adopts the
   55-map result for the paper.
5. **Under D45 the family claim stands on these runs: every gap change
   clears its point floor. The earlier reading that every one sits inside
   its floor's upper bound fails for two.** All ten gap changes reject and
   clear their point floors (1.39 to 1.89 times), the floors re-derived from
   § 3 of the W2.7 report (1.44 to 1.86) and the direct-SD sensitivity (1.46
   to 1.89). The two K-matched gap changes also clear the upper bound of
   their floor (1.09 and 1.01); the other eight do not (0.75 to 0.94). The
   K = 10 contrast the claim was first made on is still the narrowest (1.41
   and 1.39); the K-matched and fully matched contrasts are clearer (1.75 to
   1.89). **With the verifier's noise measured (Run C, § 7a)** in place of
   the borrowed band, every point ratio rises (1.45 to 1.95; the primaries
   1.46 and 1.45), and the verdict stands; the two K-matched upper readings
   rise to 1.12 and 1.04.

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
| **Primary:** 3.7 (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0562 | [−0.0964, −0.0207] | 0.0060 | 0.0044 | 0.0060 |
| **Primary:** all-3.7 − Gemini 3 K = 10 | −0.0559 | [−0.0936, −0.0214] | 0.0031 | 0.0026 | 0.0034 |
| 3.7 (Gemini 3 verifier) − Gemini 3 K = 5 rung | −0.0649 | [−0.1049, −0.0279] | 0.0006 | 0.0005 | 0.0010 |
| all-3.7 − Gemini 3 K = 5 rung | −0.0647 | [−0.1020, −0.0290] | 0.0001 | < 0.0001 | 0.0003 |
| 3.7 (Gemini 3 verifier) − Gemini 3 T 1.0 | −0.0634 | [−0.1013, −0.0288] | 0.0005 | 0.0003 | 0.0010 |
| all-3.7 − Gemini 3 T 1.0 | −0.0632 | [−0.0974, −0.0322] | 0.0002 | 0.0002 | 0.0005 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0704 | [−0.1098, −0.0321] | 0.0007 | 0.0006 | 0.0010 |
| Fifth leg (3.7 verifier) − Gemini 3 K = 10 | −0.0633 | [−0.0996, −0.0279] | 0.0010 | 0.0009 | 0.0013 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 T 1.0, fully matched | −0.0776 | [−0.1121, −0.0431] | < 0.0001 | < 0.0001 | < 0.0001 |
| Fifth leg (3.7 verifier) − Gemini 3 T 1.0, fully matched | −0.0705 | [−0.1025, −0.0398] | < 0.0001 | < 0.0001 | < 0.0001 |

"Fifth leg" is 3.7 text − cached 3.7 image; "< 0.0001" means no permutation
of 10,000 reached the observed value (D42 default (d)). Every interval
excludes zero. This is the p the original claim could not compute across
campaigns. The primary under the Gemini 3 verifier grew (−0.0529 → −0.0562)
while its p rose (0.0047 → 0.0060): its interval widened as much.

## 6. The date component per cell (scoring plan item 6): date plus serving mode

Bridge minus original at the original's operating point and at the bridge's
oracle (its own sweep best). The original contributes its set at its
registered point to both rows: on the legs as run that point is its own
sweep best (gate 1), and on the re-verified rows it still is for five of the
six originals; for the 3.7 image original under the Gemini 3 verifier the
best moved to (0.05, k5), 0.9381 (§ 2), so its "oracle" row compares the
bridge's best with the original's registered set, not with the original's
best (against which the difference would be 0.9267 − 0.9381 = −0.0114,
arithmetic on the two F1s, not tested). Every difference combines date with
serving mode (batch against the originals' real-time flex or standard
tiers); none is a date effect alone, and on both sides the re-verified rows
carry the date 2026-10-13 (§ 1; the six originals read 93 such rows: Gemini
3 text 22, Gemini 3 image 31, 3.7 text 11 under each verifier, 3.7 image 9
under each). Tile-swap p (10,000, seed 42). Same-tile
flips on the 487 tiles: a tile is **discordant** when any of its TP, FP or
FN counts differ; it is **fixed** when it leaves error (FP + FN > 0) and
**broken** when it enters it. The within-execution yardstick is the
discordant-tile rate between disjoint subset rungs of the bridge arm,
K' = 5 for Gemini 3 (126 pairs) and K' = 2 for 3.7 (15 pairs): smaller rungs
flip more tiles than the K = 10 or K = 5 cells, so the yardstick is generous
in pass count. It holds the verifier fixed, though, while each bridge cell
was re-verified on a different date from its original, so verifier
re-invocation flips are in the comparison but not in the yardstick. Floor:
1.96 · √2 · SD + 0.001, the original's SD taken equal to the bridge's (§ 7).
Results `floors/date_component.json`.

| Cell | Point (bridge) | Bridge − original | p | Discordant tiles | Fixed / broken | Within execution, median (95th) | Of floor |
|---|---|---:|---:|---:|---:|---:|---:|
| Gemini 3 text | (0.15, k10), the oracle too | −0.0031 | 0.74 | 34 (7.0 %) | 12 / 14 | 4.7 % (5.3 %) | 0.19 |
| Gemini 3 image | original (0.15, k9) | −0.0072 | 0.57 | 63 (12.9 %) | 14 / 19 | 13.3 % (15.1 %) | 0.18 |
| Gemini 3 image | oracle (0.15, k10) | −0.0009 | 0.94 | 58 (11.9 %) | 17 / 14 | 13.3 % (15.1 %) | 0.02 |
| 3.7 text, Gemini 3 verifier | (0.10, k5), the oracle too | +0.0004 | 0.98 | 35 (7.2 %) | 13 / 9 | 8.2 % (8.4 %) | 0.01 |
| 3.7 text, 3.7 verifier | (0.80, k5); oracle (0.75, k5), same set | −0.0012 | 0.87 | 24 (4.9 %) | 8 / 9 | 6.0 % (6.2 %) | 0.05 |
| 3.7 image, Gemini 3 verifier | original (0.10, k5) | −0.0095 | 0.26 | 24 (4.9 %) | 4 / 9 | 7.0 % (8.1 %) | 0.46 |
| 3.7 image, Gemini 3 verifier | oracle (0.05, k5) | −0.0086 | 0.32 | 30 (6.2 %) | 6 / 14 | 8.0 % (9.4 %) | 0.46 |
| 3.7 image, 3.7 verifier | (0.90, k5); oracle (0.88, k5), same set | −0.0033 | 0.73 | 21 (4.3 %) | 5 / 7 | 6.0 % (7.2 %) | 0.16 |

Reading:

- **No date-plus-mode component is resolved in F1.** No p falls below 0.25,
  and every difference is at most 0.46 of its within-execution floor (and
  0.38 of the § 3 floor).
- **On five of six cells the bridge moves no more tiles than two disjoint
  rungs of one execution do** (five-pass rungs for Gemini 3, two-pass rungs
  for 3.7). Gemini 3 text is the exception: 7.0 % of tiles change against a
  95th percentile of 5.3 % between rungs half its size, balanced (12 fixed,
  14 broken), so its F1 hardly moves (flagged, § 8). Part or all of the
  excess may be verifier re-invocation, which the yardstick leaves out.
- Gemini 3 image at the original point gains 10 TP and 21 FP (its union is
  15 % smaller and its passes agree more, § 8); at its oracle the difference
  is −0.0009. The lower F1 at k9 is the operating point moving, not the
  cell.

## 7. Against the floors (scoring plan item 7; rulings D45, D46)

**Method** (W2.7 report § 6b, `reports/w27-replicate-floors-2026-10-06.md`,
and its `floors-v2/` scripts). Each arm's rung was rebuilt from every subset
of its passes (2,201 rungs: 1,023 per ten-pass arm, 31 per five-pass arm)
with the K = 5 ladder's own mechanism: re-cluster the subset keeping each
cluster's member tiles, book each cluster on the sheet its members were seen
on (the D62 (1) origin route), and inherit each candidate's verifier
probability from the arm's union verification within 10 m, so the verifier
is held fixed. Each rung was scored at 20 m on the 487-tile frame along the
cell's vote path (k' = round(k / K · K')). The run-to-run SD at K' passes is
√(V_sub · N / (N − K')) over all C(N, K') subsets. At K = N it is carried by
§ 6b's rules: for ten passes, the largest of a power-law fit, a hyperbola
fit (both on K' = 1..5) and the K' = 5 value; for five passes, the largest
of the fits and the direct K' = 3 and K' = 4 values. Upper bounds add 1.96
jackknife standard errors. Floors: two independent cells
1.96 · √(SD_x² + SD_y²) + 0.001; a gap change of four
1.96 · √ΣSD² + 0.002 (the verifier re-invocation band, 0.001 per contrast).
"Direct" replaces the ten-pass K = 10 carry by the largest direct estimate
from K' = 5 to 9, which only these arms have. "§ 3" is the W2.7 report's
committed 487-tile within-execution floor at the cell's (K, t): proposer-only
consensus, re-derived from its pairs file to four places, and read as a
per-cell SD where a contrast has more than two cells. Gates, all passed:
the six original cells and three gaps (as registered, on the legs as run);
every committed bridge set re-scored to its F1 within 1e-3; every committed
gap test reproduced exactly (both F1s, the difference and the p); each
all-pass rung equal to its arm's union on origin (count, votes, within 2
nanometres) and to every committed cell set tile for tile; the first-five
rungs equal to the committed K = 5 ladder sets. Until 2026-10-15 the script
read the unions with their stored nearest-carrier tiles and clustered the
rungs without their members; on the re-verified rows that refused (§ 8), and
on the legs as run the corrected script reproduces the 2026-10-08 floors
(changelog). Results `floors/floors.json`, `floors/summary.csv`,
`floors/gates.json` and `floors/subset_cells.csv`; 2,158 s on sapphire on one
worker (2026-10-08: 380 s on 20).
The floors read the rows re-verified on 2026-10-13 (§ 1): 255 rows, the
ten legs' 162 and the six originals' 93 (US$0.202353), recorded per leg
in `floors/floors.json` `meta.reverification`.

**Cell SDs** (the run-to-run SD of each cell at its point):

| Cell (point) | K | SD | Upper | Direct | § 3 floor |
|---|---:|---:|---:|---:|---:|
| Gemini 3 text (0.15, k10) | 10 | 0.0056 | 0.0079 | 0.0059 | 0.0253 |
| Gemini 3 image (0.15, k10) | 10 | 0.0145 | 0.0274 | 0.0128 | 0.0253 |
| Gemini 3 image (0.15, k9) | 10 | 0.0145 | 0.0274 | 0.0121 | 0.0191 |
| Gemini 3 text, K = 5 rung (0.15, k5) | 5 of 10 | 0.0056 | 0.0093 | — | 0.0295 |
| Gemini 3 image, K = 5 rung (0.15, k5) | 5 of 10 | 0.0121 | 0.0185 | — | 0.0295 |
| 3.7 text, Gemini 3 verifier (0.10, k5) | 5 | 0.0095 | 0.0181 | — | 0.0295 |
| 3.7 text, 3.7 verifier (0.75 / 0.80, k5) | 5 | 0.0095 / 0.0087 | 0.0194 / 0.0172 | — | 0.0295 |
| 3.7 image, Gemini 3 verifier (0.05 / 0.10, k5) | 5 | 0.0065 / 0.0071 | 0.0100 / 0.0137 | — | 0.0295 |
| 3.7 image, 3.7 verifier (0.88 / 0.90, k5) | 5 | 0.0072 / 0.0072 | 0.0137 / 0.0137 | — | 0.0295 |
| 3.7 image cached, Gemini 3 verifier (0.05 / 0.10, k5) | 5 | 0.0079 / 0.0070 | 0.0197 / 0.0197 | — | 0.0295 |
| 3.7 image cached, 3.7 verifier (0.95 / 0.90, k5) | 5 | 0.0061 / 0.0061 | 0.0172 / 0.0168 | — | 0.0295 |
| Gemini 3 text, T 1.0 (0.15, k5) | 5 | 0.0084 | 0.0183 | — | 0.0295 |
| Gemini 3 image, T 1.0 (0.15, k5) | 5 | 0.0132 | 0.0251 | — | 0.0295 |

**Gaps** (text − image; p from § 3):

| Gap | Estimate | p | Floor (upper) | Of floor (of upper) | Direct floor (of it) | § 3 floor (of it) |
|---|---:|---:|---:|---:|---:|---:|
| Gemini 3, K = 10 | +0.0536 | 0.0018 | 0.0314 (0.0570) | 1.71 (0.94) | 0.0287 (1.87) | 0.0253 (2.12) |
| Gemini 3, K = 5 rung | +0.0624 | 0.0001 | 0.0271 (0.0416) | 2.30 (1.50) | — | 0.0295 (2.11) |
| Gemini 3, T 1.0, K = 5 | +0.0608 | < 0.0001 | 0.0316 (0.0619) | 1.92 (0.98) | — | 0.0295 (2.06) |
| 3.7, Gemini 3 verifier | −0.0026 | 0.77 | 0.0235 (0.0415) | 0.11 (0.06) | — | 0.0295 (0.09) |
| 3.7, 3.7 verifier | −0.0023 | 0.75 | 0.0243 (0.0475) | 0.10 (0.05) | — | 0.0295 (0.08) |
| 3.7 text − cached image, Gemini 3 verifier | −0.0168 | 0.093 | 0.0252 (0.0534) | 0.66 (0.31) | — | 0.0295 (0.57) |
| 3.7 text − cached image, 3.7 verifier | −0.0096 | 0.25 | 0.0231 (0.0518) | 0.42 (0.19) | — | 0.0295 (0.33) |

**Gap changes** (p from § 5):

| Gap change | Estimate | p | Floor (upper) | Of floor (of upper) | Direct floor (of it) | § 3-derived floor (of it) |
|---|---:|---:|---:|---:|---:|---:|
| **Primary:** 3.7 (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0562 | 0.0060 | 0.0398 (0.0711) | 1.41 (0.79) | 0.0377 (1.49) | 0.0389 (1.44) |
| **Primary:** all-3.7 − Gemini 3 K = 10 | −0.0559 | 0.0031 | 0.0403 (0.0748) | 1.39 (0.75) | 0.0382 (1.46) | 0.0389 (1.44) |
| 3.7 (Gemini 3 verifier) − Gemini 3 K = 5 rung | −0.0649 | 0.0006 | 0.0364 (0.0593) | 1.78 (1.09) | — | 0.0417 (1.56) |
| all-3.7 − Gemini 3 K = 5 rung | −0.0647 | 0.0001 | 0.0370 (0.0637) | 1.75 (1.01) | — | 0.0417 (1.55) |
| 3.7 (Gemini 3 verifier) − Gemini 3 T 1.0 | −0.0634 | 0.0005 | 0.0400 (0.0752) | 1.58 (0.84) | — | 0.0417 (1.52) |
| all-3.7 − Gemini 3 T 1.0 | −0.0632 | 0.0002 | 0.0405 (0.0786) | 1.56 (0.80) | — | 0.0417 (1.51) |
| Fifth leg (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0704 | 0.0007 | 0.0409 (0.0787) | 1.72 (0.89) | 0.0388 (1.81) | 0.0389 (1.81) |
| Fifth leg (3.7 verifier) − Gemini 3 K = 10 | −0.0633 | 0.0010 | 0.0396 (0.0776) | 1.60 (0.82) | 0.0374 (1.69) | 0.0389 (1.63) |
| Fifth leg (Gemini 3 verifier) − Gemini 3 T 1.0, fully matched | −0.0776 | < 0.0001 | 0.0411 (0.0824) | 1.89 (0.94) | — | 0.0417 (1.86) |
| Fifth leg (3.7 verifier) − Gemini 3 T 1.0, fully matched | −0.0705 | < 0.0001 | 0.0398 (0.0813) | 1.77 (0.87) | — | 0.0417 (1.69) |

Reading (D45: a configuration claim needs the test to reject AND the
difference to exceed its floor):

- **The Gemini 3 text advantage is a configuration-level result** at K = 5
  (2.30 times the floor, 1.50 times its upper bound). At T 1.0 it clears the
  point floor (1.92) but, **unlike on 2026-10-08, no longer its upper bound
  (0.98)**; at K = 10 it clears the point floor (1.71, or 1.87 on direct SDs,
  2.12 on § 3) but not the upper bound (0.94), which the image arm's carried
  SD drives.
- **No 3.7 gap is resolved** (none rejected; 0.10 to 0.66 of its floor),
  the fifth leg's included. This is the absence of a resolved gap, not a
  demonstrated equivalence.
- **Every gap change rejects and clears its point floor** (1.39 to 1.89),
  on all three floor readings. **The 2026-10-08 reading "none clears its
  upper bound (0.66 to 0.99)" fails:** the two K-matched gap changes clear
  theirs (1.09 for 3.7 under the Gemini 3 verifier, 1.01 all-3.7), so on the
  K-matched contrasts the family claim is a configuration claim in the
  re-screen's stronger category, "clears the point floor and its upper
  bound" (W2.7 report § 6b). The other eight stay inside their upper bounds
  (0.75 to 0.94), in the category "clears the point floor; inside its upper
  bound", most narrowly the K = 10 contrast the claim was first made on.
  The upper bound is conservative: it adds each cell's upper SD in
  quadrature. The independent audit's delta-method 95 % upper for the
  primary floor (about 0.068, ratio 0.78, on the 2026-10-08 floors) was not
  re-derived.
  These floors carry the borrowed verifier band; § 7a replaces it with the
  verifier's measured noise, which raises every ratio slightly.

Limits:

- **The verifier band is borrowed; it was suspected too small for this
  frame, and the measurement does not bear that out** (Run C, § 7a,
  2026-10-08). The 0.001 per contrast was measured on the 55-map corpus
  (W2.7 report § 1). Each cell here holds 400 to 449 detections, so one
  verifier decision moves F1 by about 0.0011 to 0.0013, and the whole band
  is about one decision; the 2.4 % same-week re-invocation flip rate would
  be about ten. Scaled from the 55-map corpus (about 11 times as many
  detections), the band would be about 0.003 to 0.005 per contrast. At
  0.003 the primary gap changes are 1.28 and 1.26 times their floors; at
  0.005, 1.17 and 1.16. The floors are proposer-stage floors plus that
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
  follows: 0.0025 gives 1.44 and 1.41; 0.0072 gives 1.19 and 1.17; 0.010
  gives 1.03 and 1.02. The fully matched gap changes stay above 1 up to
  0.012 (1.27 and 1.17). So the family claim holds on the matched
  contrasts for any plausible verifier noise, and the original K = 10
  contrast clears its floor up to a per-cell verifier SD of about 0.010.
  Run C (PI ruling D56, `planning/pi-decisions-2026-09-20.md`) measured it
  by two further verifications of all ten legs (§ 7a): the 3.7 verifier's
  per-cell SD is 0.0003 to 0.0021 (pooled 0.0010) and the Gemini 3
  verifier's 0.0006 to 0.0034 (pooled 0.0017), well under the 0.0106 at
  which the primary would reach its floor; with them the primaries are
  1.46 and 1.45.
- **Gemini 3 image at (0.15, k9)** follows a unanimity vote path at every
  K' ≤ 5, so its carried SD is the k10 cell's (0.0145). This affects only
  that cell's date-component floor, in the conservative direction.
- **No floor at K = N is measured; each is carried.** The Gemini 3 image
  arm's SD rises with K (power exponent +0.23: unanimity rungs keep fewer,
  more borderline detections), so the power fit reads 0.0145 at K = 10
  against direct values of 0.0115 to 0.0128 at K' = 6 to 9; the rule is
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
booked (card § 9). Audited cost US$25.32. On 2026-10-13 the wrong-sheet rows
of all thirty legs were re-verified on crops from their own sheet (§ 1):
162 rows per replicate, 486 in all (US$0.383286), each replicate's rows sent
as separate requests, in one batch job per verifier (396 Gemini 3 rows,
90 Gemini 3.7 rows). So for those rows the three
replicates are three independent verifications made on one day,
2026-10-13; `meta.reverification` records them per leg and replicate beside
`meta.replicate_dates`.

**Method** (card § 7, fixed before the first lodge). Each committed set of
§§ 2, 5 and 7 is scored at its own point with each replicate's
probabilities, the union booked on its origin sheets as the cells were
scored; the K = 5 rungs re-inherit them within 10 m. Gate, passed:
replicate 1 reproduces all 20 committed sets tile for tile. Per cell: the SD
of the three F1s (two degrees of freedom) and its 95 % chi-square interval,
0.52 to 6.3 times the estimate. "Split" counts the candidates the cell's
vote gate admits whose accept/reject decision differs between replicates.
The floors are § 7's, with 1.96 · √(Σ proposer SD² + Σ verifier SD²) in
place of the 0.001-per-contrast band; the proposer SDs are § 7's, read from
`floors/floors.json`. Script `scripts/modality_bridge_verifier_sd.py`;
results `verifier-sd/verifier_sd.json`, `verifier-sd/floors_with_verifier.json`,
`verifier-sd/summary.csv` and `verifier-sd/gates.json`; 42 s on sapphire.

**Cells** (F1 at 20 m, 487-tile frame):

| Cell (point) | Verifier | F1, replicates 1 / 2 / 3 | SD (95 % interval) | Split |
|---|---|---|---:|---:|
| Gemini 3 text (0.15, k10) | Gemini 3 | 0.8986 / 0.8975 / 0.9014 | 0.0021 (0.0011–0.0129) | 20 of 942 |
| Gemini 3 image (0.15, k10) | Gemini 3 | 0.8449 / 0.8435 / 0.8449 | 0.0008 (0.0004–0.0051) | 14 of 580 |
| Gemini 3 image (0.15, k9) | Gemini 3 | 0.8386 / 0.8372 / 0.8395 | 0.0012 (0.0006–0.0073) | 15 of 680 |
| Gemini 3 text, K = 5 rung (0.15, k5) | Gemini 3 | 0.8918 / 0.8918 / 0.8949 | 0.0018 (0.0009–0.0113) | 24 of 1,086 |
| Gemini 3 image, K = 5 rung (0.15, k5) | Gemini 3 | 0.8294 / 0.8300 / 0.8324 | 0.0015 (0.0008–0.0097) | 17 of 670 |
| 3.7 text (0.10, k5) | Gemini 3 | 0.9241 / 0.9218 / 0.9185 | 0.0028 (0.0015–0.0179) | 7 of 466 |
| 3.7 text (0.75, k5) | Gemini 3.7 | 0.9352 / 0.9358 / 0.9371 | 0.0010 (0.0005–0.0060) | 10 of 466 |
| 3.7 text (0.80, k5) | Gemini 3.7 | 0.9352 / 0.9369 / 0.9382 | 0.0015 (0.0008–0.0094) | 11 of 466 |
| 3.7 image (0.05, k5) | Gemini 3 | 0.9267 / 0.9267 / 0.9257 | 0.0006 (0.0003–0.0038) | 1 of 460 |
| 3.7 image (0.10, k5) | Gemini 3 | 0.9259 / 0.9317 / 0.9257 | 0.0034 (0.0018–0.0213) | 10 of 460 |
| 3.7 image (0.88, k5) | Gemini 3.7 | 0.9375 / 0.9372 / 0.9369 | 0.0003 (0.0002–0.0018) | 15 of 460 |
| 3.7 image (0.90, k5) | Gemini 3.7 | 0.9375 / 0.9394 / 0.9380 | 0.0010 (0.0005–0.0062) | 16 of 460 |
| 3.7 image cached (0.05, k5) | Gemini 3 | 0.9409 / 0.9409 / 0.9398 | 0.0006 (0.0003–0.0039) | 4 of 455 |
| 3.7 image cached (0.10, k5) | Gemini 3 | 0.9404 / 0.9428 / 0.9393 | 0.0018 (0.0009–0.0113) | 4 of 455 |
| 3.7 image cached (0.95, k5) | Gemini 3.7 | 0.9448 / 0.9464 / 0.9479 | 0.0015 (0.0008–0.0095) | 17 of 455 |
| 3.7 image cached (0.90, k5) | Gemini 3.7 | 0.9437 / 0.9464 / 0.9480 | 0.0021 (0.0011–0.0134) | 15 of 455 |
| Gemini 3 text, T 1.0 (0.15, k5) | Gemini 3 | 0.8908 / 0.8897 / 0.8870 | 0.0019 (0.0010–0.0121) | 17 of 1,018 |
| Gemini 3 image, T 1.0 (0.15, k5) | Gemini 3 | 0.8299 / 0.8285 / 0.8267 | 0.0016 (0.0008–0.0102) | 12 of 588 |

Where a cell's operating point and best point coincide, one row serves both.

**By verifier:**

- **Gemini 3:** per-cell SDs 0.0006 to 0.0034. Pooled over the best sets of
  its seven legs, 0.0017 (14 degrees of freedom; 95 % 0.0012 to 0.0027).
  June's single-run SDs, from five verifications at T 0.0 (§ 7 Limits), were
  0.0025 to 0.0072: 0.0032 to 0.0072 over the five vote levels of its
  384-pixel cell and 0.0025 to 0.0048 over those of a 256-pixel cell
  (`results/verifier-robustness/robustness_summary_T0.0.json`). These are
  lower (flagged, § 8). The two smallest, 0.0006, are the 3.7 image cells'
  best sets at (0.05, k5), where the verifier rejects almost nothing (1 and
  4 split decisions).
- **Gemini 3.7:** per-cell SDs 0.0003 to 0.0021. Pooled over its three legs,
  0.0010 (6 degrees of freedom; 0.0007 to 0.0023).
- **Responses.** Between any two replicates, Gemini 3 returns byte-identical
  text for 48.0 to 52.5 % of candidates and changes 14 to 18 % of
  probabilities; Gemini 3.7 never returns identical text and changes 35 to
  44 % of probabilities. The text comparison reads each replicate's original
  batch responses, so for the re-verified rows it compares the wrong-sheet
  answers; the probability comparison reads the booked rows, re-verified
  ones included. At the cells' points Gemini 3.7 splits more decisions (2.1
  to 3.7 % of admitted candidates, against 0.2 to 2.5 %), yet its F1 SDs are
  the smaller (flagged, § 8).
- **Day.** Replicate 1 ran a day before 2 and 3, except for the re-verified
  rows, which all three replicates took on 2026-10-13. Replicate 1 minus the
  mean of 2 and 3 ranges from −0.0034 to +0.0040, with both signs on both
  verifiers: no day-to-day shift shows.

**Gaps** against floors with the measured verifier SD (point; the upper
reading uses each cell's upper proposer SD):

| Gap | Estimate | Floor, band (ratio) | Floor, measured (ratio) | Upper ratio, band → measured | Break-even verifier SD |
|---|---:|---:|---:|---:|---:|
| Gemini 3, K = 10 | +0.0536 | 0.0314 (1.71) | 0.0307 (1.75) | 0.94 → 0.95 | 0.0159 |
| Gemini 3, K = 5 rung | +0.0624 | 0.0271 (2.30) | 0.0265 (2.35) | 1.50 → 1.53 | 0.0204 |
| Gemini 3, T 1.0, K = 5 | +0.0608 | 0.0316 (1.92) | 0.0310 (1.96) | 0.98 → 1.00 | 0.0190 |
| 3.7, Gemini 3 verifier | −0.0026 | 0.0235 (0.11) | 0.0232 (0.11) | 0.06 → 0.06 | — |
| 3.7, 3.7 verifier | −0.0023 | 0.0243 (0.10) | 0.0234 (0.10) | 0.05 → 0.05 | — |
| 3.7 text − cached image, Gemini 3 verifier | −0.0168 | 0.0252 (0.66) | 0.0249 (0.67) | 0.31 → 0.32 | — |
| 3.7 text − cached image, 3.7 verifier | −0.0096 | 0.0231 (0.42) | 0.0223 (0.43) | 0.19 → 0.19 | — |

The Gemini 3 T 1.0 gap's measured upper ratio is 0.996, still inside its
upper bound.

**Gap changes:**

| Gap change | Estimate | Floor, band (ratio) | Floor, measured (ratio) | Upper ratio, band → measured | Direct, band → measured | § 3-derived, without → with verifier | Break-even verifier SD |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Primary:** 3.7 (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0562 | 0.0398 (1.41) | 0.0385 (1.46) | 0.79 → 0.81 | 1.49 → 1.54 | 1.44 → 1.42 | 0.0106 |
| **Primary:** all-3.7 − Gemini 3 K = 10 | −0.0559 | 0.0403 (1.39) | 0.0386 (1.45) | 0.75 → 0.77 | 1.46 → 1.53 | 1.44 → 1.43 | 0.0104 |
| 3.7 (Gemini 3 verifier) − Gemini 3 K = 5 rung | −0.0649 | 0.0364 (1.78) | 0.0352 (1.84) | 1.09 → 1.12 | — | 1.56 → 1.53 | 0.0140 |
| all-3.7 − Gemini 3 K = 5 rung | −0.0647 | 0.0370 (1.75) | 0.0354 (1.83) | 1.01 → 1.04 | — | 1.55 → 1.54 | 0.0139 |
| 3.7 (Gemini 3 verifier) − Gemini 3 T 1.0 | −0.0634 | 0.0400 (1.58) | 0.0388 (1.64) | 0.84 → 0.86 | — | 1.52 → 1.49 | 0.0130 |
| all-3.7 − Gemini 3 T 1.0 | −0.0632 | 0.0405 (1.56) | 0.0389 (1.62) | 0.80 → 0.82 | — | 1.51 → 1.50 | 0.0128 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 K = 10 | −0.0704 | 0.0409 (1.72) | 0.0396 (1.78) | 0.89 → 0.91 | 1.81 → 1.88 | 1.81 → 1.78 | 0.0150 |
| Fifth leg (3.7 verifier) − Gemini 3 K = 10 | −0.0633 | 0.0396 (1.60) | 0.0380 (1.67) | 0.82 → 0.83 | 1.69 → 1.76 | 1.63 → 1.61 | 0.0130 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 T 1.0, fully matched | −0.0776 | 0.0411 (1.89) | 0.0398 (1.95) | 0.94 → 0.96 | — | 1.86 → 1.83 | 0.0171 |
| Fifth leg (3.7 verifier) − Gemini 3 T 1.0, fully matched | −0.0705 | 0.0398 (1.77) | 0.0382 (1.84) | 0.87 → 0.89 | — | 1.69 → 1.67 | 0.0152 |

"Break-even" is the verifier SD that, on all four cells alike, brings the
point ratio to 1; "—" in that column means the gap is below its floor with
no verifier noise at all. § 3's committed floors carry no band, so adding
the verifier lowers those ratios slightly.

**Verifier sensitivities** on the gap changes' point ratios: the pooled SD
of each cell's verifier family, that SD at its 95 % upper bound (added after
the results), and each cell at its own upper bound (pre-specified):

| Gap change | Measured per cell | Pooled | Pooled, upper | Each cell at its upper |
|---|---:|---:|---:|---:|
| **Primary:** 3.7 (Gemini 3 verifier) − Gemini 3 K = 10 | 1.46 | 1.46 | 1.43 | 0.96 |
| **Primary:** all-3.7 − Gemini 3 K = 10 | 1.45 | 1.44 | 1.41 | 1.15 |
| 3.7 (Gemini 3 verifier) − Gemini 3 K = 5 rung | 1.84 | 1.85 | 1.80 | 1.13 |
| all-3.7 − Gemini 3 K = 5 rung | 1.83 | 1.83 | 1.78 | 1.37 |
| 3.7 (Gemini 3 verifier) − Gemini 3 T 1.0 | 1.64 | 1.64 | 1.61 | 1.04 |
| all-3.7 − Gemini 3 T 1.0 | 1.62 | 1.62 | 1.59 | 1.24 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 K = 10 | 1.78 | 1.78 | 1.75 | 1.18 |
| Fifth leg (3.7 verifier) − Gemini 3 K = 10 | 1.67 | 1.67 | 1.63 | 1.23 |
| Fifth leg (Gemini 3 verifier) − Gemini 3 T 1.0, fully matched | 1.95 | 1.96 | 1.92 | 1.26 |
| Fifth leg (3.7 verifier) − Gemini 3 T 1.0, fully matched | 1.84 | 1.85 | 1.81 | 1.31 |

Reading:

- **The verifier adds less than the band assumed.** Measured per cell and
  added in quadrature, it lowers every gap change's floor, so every point
  ratio rises: the primaries from 1.41 and 1.39 to 1.46 and 1.45, the
  K = 5 contrasts to 1.84 and 1.83, the T 1.0 ones to 1.64 and 1.62, and
  the fully matched ones to 1.95 and 1.84. The audit's suspicion that the
  0.001 band was too small (§ 7 Limits) is not borne out (flagged, § 8).
- **The K = 10 contrast clears its floor with the verifier measured.** It
  would need a per-cell verifier SD of 0.0106 (Gemini 3 verifier) or 0.0104
  (all-3.7) to reach its floor. The largest measured is 0.0034, and the
  pooled upper bounds are 0.0027 (Gemini 3) and 0.0023 (Gemini 3.7).
- **No contrast changes side of its point, upper, direct or § 3 floor when
  the measured noise replaces the band.** The two K-matched gap changes
  clear their upper floors on both readings (1.09 → 1.12 and 1.01 → 1.04);
  every other gap change stays inside its upper bound (0.77 to 0.96
  measured), and the Gemini 3 T 1.0 gap moves from 0.98 to 0.996 of its.
  The 2026-10-08 sentence that one upper reading reached 1.01 on the
  measured noise is superseded: on the band alone two now clear.
- **Three replicates bound one cell's SD loosely.** With every cell at its
  own two-degree-of-freedom upper bound at once (6.3 times its SD), one gap
  change falls below 1: the primary under the Gemini 3 verifier (0.96),
  because its 3.7 text cell's SD is among the largest measured (0.0028). On
  2026-10-08 three did (0.72, 0.87 and 0.80); the K-matched and T 1.0
  contrasts on the same cells now read 1.13 and 1.04, because the inline 3.7
  image cell's best set moved to (0.05, k5), where its verifier SD is 0.0006
  (it was 0.0034 at (0.10, k5)). Every other gap change stays above 1 (1.15
  to 1.37). Pooled within each verifier, the upper bounds leave every gap
  change at 1.41 or more.

Limits:

- Three replicates per cell. The per-cell SDs are rough; the pooled SDs
  assume one SD per verifier across its cells.
- The replicates measure re-invocation within a day and across one day, on
  the batch tier. They do not cover longer drift or the originals' real-time
  tiers (§ 6 compares those). For the re-verified rows all three replicates
  are one day's verifications (2026-10-13).
- Verifier noise is taken as independent of the proposer's and between
  cells, since each cell's leg is a separate invocation. The K = 5 rungs
  inherit probabilities from the K = 10 legs, so they share those legs'
  verifier draws; no contrast pairs a rung with its own K = 10 cell.
- Otherwise the floors are § 7's, with the same carried proposer SDs and
  normality assumption.

**Reproduction under the D50/D51 scorer (2026-10-09; PI ruling D58 Q9,
recorded 2026-10-15).** After pull request #26 merged, the ten cells, the
three gap tests, the floors and the verifier SD were re-run on 2026-10-09 in
a scratch clone on sapphire, scorer at `8988f3f17`, without rebuilding the
deduplicated passes. Of the 57 committed output files, 49 were byte-identical
(all 44 cell files; the floors' `subset_cells.csv`, `summary.csv`,
`gap_change.json` and `date_component.json`; the verifier SD's
`summary.csv`) and 8 differed only in metadata (run times, roots, the new
`floors_dir`, and the gap tests' scratch `pair_sources`). Under D58 Q9 that
was to be recorded here as a dated note, not as re-committed files; it was
not added at the time
(`reports/s163-agent-records/d57-4-rescore-s4-q4.md`, "Run B and Run C:
nothing moves"). The run overlapped sapphire's memory fault of that week;
the byte-identical files stand (same record).

## 8. Flags

- **Restated 2026-10-15 (D65 (2) and (6)); four readings changed.**
  - **The floors and verifier-SD scripts refused the re-verified rows until
    they were moved onto the origin route.** They read each union with its
    stored nearest-carrier tile and clustered their rungs without members,
    as the cells were scored before D62 (1); the rows they booked to the
    neighbouring sheet were exactly the 162 re-verified rows (17, 34, 12, 8,
    10, 16 and 35 per arm). With the old route, replicate 1 scored the 20
    committed sets 0.010 to 0.018 below their F1 and gate 1 refused. Both
    scripts now book every union row and rung cluster on its origin sheet,
    as `image_b_analysis.py` does; on the legs as run the corrected scripts
    reproduce the 2026-10-08 floors and verifier SD (changelog).
  - **§ 7's "none clears its upper bound (0.66 to 0.99)" fails**: the two
    K-matched gap changes clear theirs (1.09 and 1.01; 1.12 and 1.04 with
    the measured verifier noise).
  - **The Gemini 3 T 1.0 text advantage falls inside its upper bound**
    (1.03 → 0.98; 1.05 → 0.996 measured): "configuration-level at T 1.0"
    now holds on the point floor only.
  - **§ 7a's "each cell at its upper" reading**: one gap change below 1
    (0.96), not three; the inline 3.7 image cell's best moved to (0.05, k5),
    where its verifier SD is 0.0006.
  - **§ 6's "oracle" for the 3.7 image original under the Gemini 3 verifier
    is its registered point, not its new best** (0.9353 at (0.10, k5)
    against 0.9381 at (0.05, k5)).
  - Reading the bridge "as run" now needs the data before
    `0e8a1fa7a` (PR #43): 7 of the 10 replicate-1 legs and all 20 Run C legs
    are named by their `_repaired` copies, which PR #43 rewrote with the
    re-verified rows, so `MAP_READER_VERIFY_DIRS=fixed` reads those rows
    too.
- **Run C's verifier noise runs against three expectations** (§ 7a; raised
  as findings, not explained away):
  - **It is smaller than the band assumed.** The audit and § 7 Limits
    expected the 0.001-per-contrast band to understate it; measured, it
    lowers every gap-change floor and raises every ratio.
  - **The Gemini 3.7 verifier is the steadier in F1, not the noisier.** It
    samples at T 1.0 and never repeats a response, changes 35 to 44 % of
    probabilities between replicates (Gemini 3: 14 to 18 %) and splits more
    decisions at the cells' points (2.1 to 3.7 % against 0.2 to 2.5 %), yet
    its per-cell F1 SDs are the smaller (pooled 0.0010 against 0.0017).
  - **The Gemini 3 verifier's SDs (0.0006 to 0.0034) sit below June's**
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
  moved by −0.0072 only. Raised as a surprise; the chain that built it rebuilds
  the original unions byte for byte, so it is not a pipeline artefact.
- **Gemini 3 text changes more tiles between dates than within an
  execution, without changing F1** (§ 6): 34 of 487 tiles (7.0 %) differ
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
  records no change). Updated 2026-10-15: PR #43 (2026-10-13) committed
  `verify_g3_repaired/` for those three legs with their re-verified rows
  (17, 34 and 16), so they no longer equal `verify_g3/`; the scripts read
  them under the shared leg rule. The passes are still uncommitted; the
  restatement read sapphire's copies, whose SHA-256 equals the floors'
  record for all 45.
- T 1.0 text passes lost more tiles to flex-retry failures (31 across five
  passes against 11 across ten at T 0.7), all recovered in round 1.
- The original Gemini 3 image leg's six recovery tiles went inline (Stage 2
  card § 8); negligible here.
- Batch metas do not book thinking tokens separately; the audited costs
  carry them.

## 9. Cost (audited, batch)

Stage 1: Gemini 3 text US$8.39, Gemini 3 image US$19.52, 3.7 text US$8.64,
3.7 image US$18.93, fifth leg US$12.33, T 1.0 text US$4.26, T 1.0 image
US$9.76 (US$81.83). Stage 2, ten legs: US$12.69. In all, US$94.53, plus the
cache storage (shortened by deleting each cache once its pass landed,
D52). The 3.7 cache reads are priced at the rate card's US$0.0375/M. At the
US$0.075/M the September invoices show, add about US$9. §§ 5–7 made no
Application Programming Interface (API) call.

Run C (§ 7a), twenty verifier legs on 2026-10-08: US$25.32 audited
(`scripts/audit_verifier_cost.py`, record
`outputs/modality-bridge-2026-10-07/stage2/checks/run-c-cost-audit.json`;
US$12.66 per replicate, against the US$12.69 of Run B's ten legs), within
D56's US$50. The analysis made no API call.

The 2026-10-13 re-verification of the wrong-sheet rows (D62 (1) step 2) cost
US$0.383286 for these thirty legs' 486 rows (US$0.127524 for Run B's ten),
part of that run's US$0.821008 for 1,029 rows
(`outputs/wrong-sheet-reverify-2026-10-13/record.json`, `total_cost_usd`).

## Changelog

### 2026-10-15 — Restated with the re-verified rows; the floors on the origin route

Refresh trigger: PI rulings D62 (1) (the cluster-origin route, pull
requests #41 and #42; the 1,029 wrong-sheet rows re-verified on 2026-10-13
and booked by PR #43) and D65 (2) and (6) (one restatement pass; the
bridge's floors and verifier SD re-run with the re-verified rows, recording
their date). The cells and gap tests regenerate with
`scripts/modality-bridge-2026-10-07-score.sh` (the text-B anchor is the
dated 0.9017); `scripts/modality_bridge_floors.py` and
`scripts/modality_bridge_verifier_sd.py` were moved onto the origin route
first (they refused the re-verified rows, § 8) and given the
`meta.reverification` record. On the legs as run (data at `be252e57b`) the
corrected scripts reproduce the 2026-10-08 floors and verifier SD: four of
the six `floors/` files and the verifier SD's `summary.csv` byte for byte,
the rest apart from run metadata, the new `reverification` record (0 rows
there) and the provenance fields both scripts have written since `9c843b980`
(the D58 Q6 check, recorded in
`reports/s164-agent-records/restatement-pass.md`). § 9's total is corrected
from US$94.52 to US$94.53: the audited components sum to US$94.526842
(`reports/s164-agent-records/fault-window-rechecks-scripts/w1-8-w2-11/w1-8-cost-audit-summary.json`,
`totals.all`); the slip came from adding the rounded subtotals. The
2026-10-09 reproduction under the D50/D51 scorer, which D58 Q9 asked to be
recorded here, is added at the end of § 7a.

| Claim | Before | After |
|---|---|---|
| Gemini 3 text, K = 10 (bridge; original) | 0.8916; 0.8961 | 0.8986; 0.9017 |
| Gemini 3 image at (0.15, k9) (bridge; original) | 0.8331; 0.8412 | 0.8386; 0.8458 |
| 3.7 cells, bridge (text G3v, text 3.7v, image G3v, image 3.7v) | 0.9154, 0.9265, 0.9160, 0.9288 | 0.9241, 0.9352, 0.9259, 0.9375 |
| 3.7 originals at their points | 0.9139, 0.9265, 0.9254, 0.9308 | 0.9238, 0.9364, 0.9353, 0.9408 |
| Cached 3.7 image at the operating points | 0.9318, 0.9352 | 0.9404, 0.9437 |
| 3.7 image G3-verifier best points (inline; cached) | (0.10, k5) both | (0.05, k5) both: 0.9267; 0.9409 |
| Gemini 3 gap K = 10 (p); original | +0.0523 (0.0029); +0.0549 (0.0010) | +0.0536 (0.0018); +0.0559 (0.0005) |
| Gemini 3 gaps, K = 5 rung; T 1.0 | +0.0609; +0.0582 | +0.0624; +0.0608 |
| 3.7 gaps, G3v; 3.7v (p) | −0.0006 (0.95); −0.0023 (0.75) | −0.0026 (0.77); −0.0023 (0.75) |
| Fifth-leg gaps (p) | −0.0164 (0.074); −0.0098 (0.25) | −0.0168 (0.093); −0.0096 (0.25) |
| Primary gap changes (p) | −0.0529 (0.0047); −0.0547 (0.0040) | −0.0562 (0.0060); −0.0559 (0.0031) |
| Fully matched gap changes | −0.0746; −0.0680 | −0.0776; −0.0705 |
| Gap changes, of point floor | 1.24 to 1.87 | 1.39 to 1.89 |
| Gap changes, of upper floor | 0.66 to 0.99, none above 1 | 0.75 to 1.09, two above 1 (K-matched) |
| Gemini 3 T 1.0 gap, of upper floor (band; measured) | 1.03; 1.05 | 0.98; 0.996 |
| Primaries with the measured verifier SD | 1.27 and 1.33 | 1.46 and 1.45 |
| Break-even verifier SD, primaries | 0.0087 and 0.0093 | 0.0106 and 0.0104 |
| Verifier SD per cell, Gemini 3 (pooled) | 0.0011–0.0034 (0.0022) | 0.0006–0.0034 (0.0017) |
| Verifier SD per cell, 3.7 (pooled) | 0.0003–0.0021 (0.0011) | 0.0003–0.0021 (0.0010) |
| "Each cell at its upper", gap changes below 1 | three (0.72, 0.87, 0.80) | one (0.96) |
| Gemini 3 image arm's carried SD at K = 10 | 0.0164 (exponent +0.31) | 0.0145 (exponent +0.23) |
| Date components, largest share of floor | 0.46 | 0.46 |
| Total cost | US$94.52 | US$94.53 |

Not changed: § 1's run facts (passes, legs, dates, costs other than the
total); every verdict of §§ 4–7a except the two upper-bound readings and
§ 7a's "each cell at its upper" count above (the Gemini 3 text advantage is
resolved; no 3.7 gap is resolved; every gap change rejects and clears its
point floor; no date-plus-mode component is resolved; on five of six cells
the bridge flips no more tiles than an execution does, Gemini 3 text the
exception); Run C's three flags; the 55-map paragraph of § 4 item 4; the
W2.7 § 3 floors; the six-cell anchor gate, which still reads the originals
as registered. Commits: `02339bd98` (the origin-route fix and its tests)
and `OUTPUTS_COMMIT` (these outputs and this entry).

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
