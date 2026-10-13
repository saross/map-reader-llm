# Wrong-sheet verifier crops: every verifier leg swept (2026-10-13)

Claude Opus 5.5 sub-agent, 2026-10-13. Read-only: no branch, commit, PR, or model call.
Data: sapphire checkout `8988f3f17`; its verifier files match local `main` `fd3a30df8`, where
lineage was read. Scratch: `sapphire:~/scratch/wrong-sheet-crops-2026-10-13/`.

## Hand-back summary

1. **Scope.** 483 `probabilities.json` files: 105 derived threshold views, 378 verifier legs.
   360 legs paired with the manifest of the crops they saw. The other 18: 9 pv-diag legs with
   several candidate manifests (all measure 0, so the legs are 0 either way) and 9 archive legs.
   In `outputs/`: 283 paired legs, 1,078,463 verified rows.
2. **Wrong-sheet.** 1,515 leg-rows in 95 `outputs/` legs, 28 crop sets, 275 distinct places.
   Every one is an Elenovo (`K-35-053-3`) point cut from `K-35-052-4`'s raster. 43 places lie
   within 20 m of a gold-standard mound. Highest probability 0.2; 7 rows reach 0.15. Also 1 in
   a `results/` human-review kit (no model) and 23 in 5 archive legs.
3. **Signals.** Wrong-sheet ⇒ dark: all 1,515 are at least 0.5 black (lowest 0.591). Dark does
   not imply wrong-sheet: 20,123 dark crops are map edges or off-map detections. All 936,205
   retained crop PNGs equal the re-cut pixel for pixel.
4. **PR #42 reproduced exactly.** Its 14 unions give identical id sets, counts, near-mound
   counts, and darkness.
5. **Exposed beyond PR #42.** Gemini 3.7 screen (11 to 14), Gemini 3.7 image GS (9 + 9),
   Image-B K3/K5 arms (20, 21), Run B and Run C bridge (60 legs, 8 to 35 per arm), and the
   temperature probe (3 in each of 8 legs).
6. **Clean.** K-ladder legs, every 55-map leg (D53 included), Era 1, pv-diag, h10, wbf,
   verifier-robustness, flash35, gs-v2, t-pilot, Gemini 3.7 screen K1/K3. h13 has no verifier
   legs.
7. **Re-verification.** 5 jobs, 1,029 calls, about US$0.78; Batch and flex cost the same. Every
   corrected crop comes from Elenovo: dark share median 0.0135, highest 0.574. Nothing has been
   re-verified on corrected crops yet; `_repaired` copies and Run C reps reuse the blind crops.
8. **SURPRISE: re-verification will matter.** The same places (≤ 5 m), verified on correct-sheet
   crops in K-ladder and Gemini 3.7 K1/K3 legs, scored up to 1.0. Seen again (at least 0.5):
   g384_ov192 18 of 22 (8), g384_ov048 9/14 (6), g512_ov064 4/25 (3), g512_ov256 6/29 (4),
   Gemini 3.7 screen K10 11/14 (6). Candidate 245 scored 0.00 here and 0.95 there.
9. **SURPRISE: the geometric fallback over-counts.** On the 55-map corpus, 14,938 points lie off
   the crop sheet's map but were seen only on that sheet's tiles: detections in black raster
   margins, not re-keys. They lie up to 2.4 km off the map, mostly 1 vote, rarely near a mound.
   Geometry alone gives 16,749.
10. **SURPRISE: g384_ov240.** 708 candidates sit 0.5 to 1.4 km off the map (10th to 90th
    percentile), from near-empty edge tiles (`K-35-052-4_32635_x0_y3744.png` starts 4 px above
    the raster's bottom edge). A separate issue.
11. **Integrity.** Every step ran twice with byte-identical output. Bad-page count 0 before and
    after. Not done: re-verification, any repo change, and 9 archive legs (4 bounded at 0).
12. **For the PI.** (a) Approve the jobs below. (b) Re-verify every leg, or only primary legs
    (dropping Run C reps 2–3 and probe replicates)? (c) Do the 55-map margin detections and the
    g384_ov240 edge tiles get their own look?

## Method (scripts in `scripts/`; outputs in `out/runA/` and `out/runB/`)

- **Pairing.** 6 explicit pairings, a `verify<k>` → `crops<k>` rule, the six `find_manifest`
  conventions, id-set matches, and 9 consensus rebuilds validated by PNG equality.
- **Sheet signal.** Recorded member sheets; otherwise the point lies more than 10 m outside the
  crop sheet's non-black footprint and inside another sheet, and no raw pass detection within
  40 m was seen on the crop's sheet. **Dark signal:** all-black share of the crop as verified.

## Affected crop sets (`outputs/`)

Key: W wrong-sheet; D dark crops; CD centre-dark; pmax highest probability on a W row;
≤20 m and v≥5 are W rows near a mound or with 5+ votes; fix = highest dark share once corrected.

| Crop set | Legs (models) | Rows | W | D | CD | pmax | ≤20 m | v≥5 | fix | Feeds |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| grid g384_ov048 | 1 (G3) | 1,827 | 14 | 33 | 14 | 0.10 | 8 | 10 | 0.36 | 4 signed; 4 claims |
| grid g384_ov192 | 2 (G3, G3.7) | 3,319 | 22 | 29 | 22 | 0.10 | 8 | 14 | 0.40 | 11 signed; 25 claims |
| grid g512_ov064 | 1 (G3) | 1,402 | 25 | 27 | 26 | 0.05 | 8 | 4 | 0.35 | 4 signed; 4 claims |
| grid g512_ov256 | 1 (G3) | 2,585 | 29 | 33 | 31 | 0.05 | 10 | 13 | 0.35 | 4 signed; 4 claims |
| stride g256_ov064 | 1 (G3) | 3,570 | 22 | 26 | 25 | 0.10 | 8 | 15 | 0.40 | 3 signed; R1b-15 |
| stride g384_ov128 K10 | 1 (G3) | 2,387 | 11 | 17 | 11 | 0.10 | 8 | 10 | 0.36 | 5 signed; 13 claims |
| winner N1 / N3 / N5 | 3 (G3) | 1,290 / 1,700 / 1,968 | 11 each | 12/15/16 | 11 | 0.10 | 8 | 0/0/9 | 0.36 | as K10 |
| stride g512_ov176 | 1 (G3) | 1,981 | 24 | 35 | 24 | 0.05 | 7 | 10 | 0.35 | 3 signed; R1b-15 |
| stride g512_ov320 | 1 (G3) | 3,778 | 38 | 46 | 40 | 0.10 | 8 | 9 | 0.39 | 3 signed; R1b-15 |
| stride g384_ov240 | 1 (G3) | 5,250 | 19 | 747 | 725 | 0.10 | 8 | 12 | 0.39 | 3 signed; R1b-15 |
| Image-B min K10 | 1 (G3) | 4,065 | 31 | 51 | 43 | 0.05 | 8 | 12 | 0.36 | 7 signed; 7 claims |
| Image-B min K3 / K5 | 2 + 2 (G3, G3.7) | 2,227 / 2,788 | 20 / 21 | 30/34 | 24/28 | 0.10 | 7/8 | 0/7 | 0.36 | as K10 |
| Image-B HIGH K10 | 1 (G3) | 9,189 | 64 | 136 | 100 | 0.15 | 12 | 9 | 0.57 | 5 signed; 4 claims |
| G3.7 screen K5 | 3 (G3, G3.7, G3.8) | 791 | 11 | 11 | 11 | 0.05 | 8 | 8 | 0.36 | 8 signed; 22 claims |
| G3.7 screen K10 | 1 (G3) | 913 | 14 | 14 | 14 | 0.05 | 8 | 10 | 0.36 | as K5 |
| G3.7 image GS K5 / K3 | 2 + 2 (G3, G3.7) | 674 / 622 | 9 / 9 | 9/9 | 9 | 0.05 | 8 | 8/0 | 0.36 | 5 signed; 7 claims |
| Run B g3-text / temp1 | 6 + 6 (G3) | 3,258 / 3,179 | 17 / 16 | 23/19 | 17/16 | 0.20 | 8 | 12/11 | 0.36 | unregistered |
| Run B g3-image / temp1 | 6 + 6 (G3) | 3,456 / 3,085 | 34 / 35 | 55/53 | 45/45 | 0.10 | 9 | 11/6 | 0.41 | unregistered |
| Run B g37 text / image / cache | 12 each (G3, G3.7) | 789 / 661 / 644 | 12/8/10 | = W | = W | 0.05 | 8 | 7/8/7 | 0.36 | unregistered |
| temperature probe | 8 (G3 ×3, G3.7 ×5) | 300 | 3 | 3 | 3 | 0.05 | 2 | 2 | 0.36 | unregistered |

**Configuration as run** (`run.meta.json`, `probabilities.json`; per leg in `out/runA/legs.json`):
all `verify_adversarial-text`, one iteration. G3 = `gemini-3-flash-preview` T 0.0 MINIMAL
(realtime flex for the Aug–Sep legs, batch for Run B and the probe); G3.7 = `gemini-3.7-flash` T 0.0 LOW;
G3.8 = `gemini-3.8-flash` T 0.0 LOW (standard tier); the probe's three `tmax` legs ran at T 2.0.

## Re-verification jobs (repaired copies once; human-review kit excluded)

| Model / prompt / T / thinking | Legs | Calls | Distinct crops | Batch = flex | Audited per call |
|---|---:|---:|---:|---:|---|
| gemini-3-flash-preview / verify_adversarial-text / 0.0 / minimal | 43 | 818 | 551 | US$0.562 | $0.00068–0.00071 |
| gemini-3.7-flash / verify_adversarial-text / 0.0 / low | 18 | 191 | 125 | US$0.191 | ≈ $0.0011 |
| gemini-3.8-flash / verify_adversarial-text / 0.0 / low | 1 | 11 | 11 | US$0.021 | $0.00107 (standard) |
| gemini-3.7-flash / same / 2.0 / low (probe) | 2 | 6 | 3 | US$0.007 | none recorded |
| gemini-3-flash-preview / same / 2.0 / minimal (probe) | 1 | 3 | 3 | US$0.002 | none recorded |

Estimate = calls × the leg's own billed tokens per call × the 2026-10-13 rate card, which prices
batch and flex the same. Audited sums are lower bounds: `verify_37`'s record is US$0.0024 for
3,319 calls, and Run B and the probe have no `cost_audit.json`.

## Corrected-crop check

Every candidate needs a re-crop from Elenovo, its origin sheet; all 1,515 corrected crops were
cut (dark median 0.0135, highest 0.574). 244 sample PNGs are in `out/run{A,B}/corrected-sample/`,
including g384_ov048's 185, 1648, and 115; viewed, the corrected 185 and 1648 show map symbols at
the centre. The probe's batch requests decode to wrong-sheet crops at least 0.644 dark.

## Lineage (per cell; `out/lineage.json`)

38 conditions on affected cells feed 14 signed analyses (grid post-verifier, stride plateau,
winner ladder, Image-B modality and thinking pair, Gemini 3.7 screen, fourth cell and image GS,
Gemini 3.8 arm V, Era 2 board, K-ladder via its K10 rung, null-exemplar, uplift flatten and
pairing) and at most 27 claim rows: R0-05; R1b-08, -12, -15, -17, -22; R3-10 to -15; R4-17, -18,
-28; R6-11, -14, -16 to -18; R7.3-01 to -03, -11, -12, -21, -29. Run B and Run C feed the
unregistered `results/modality-bridge-2026-10-07/` (the R7.3-22/23 bridge).
