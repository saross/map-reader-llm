# TM verifier-date check: k3 against k4 under one verifier date

Read-only. Computed on sapphire (repository at 51b49deca); scratch in `/tmp/vdate/`. Scripts and results
are in this directory: `vdate_check.py`, `vdate_extra.py`, `vdate_ident.py`, `vdate-results.json`, and
`vdate-results-extra.json`. No API calls were made.

## Inputs, verified at source

| Set | Candidates | Verified | Source |
|---|---|---|---|
| TM k4 (votes ≥ 4 of 5) | 10,170 | 10,131 on 2026-04-18 (flex); 39 on 2026-05-03 | `outputs/55maps-text-min-generalisation/run.log` (lines 10865–32261); pre-cleanup backup |
| TM vote-3 shell | 2,220 | 2026-06-06 (flex) | `results/deployment-oracle-2026-06-06/vote3-verify/.../verified/run.meta.json` |
| UPL ≥ 3 of 10 | 16,482 | 2026-06-11 (flex), 16,482 fresh calls, 0 cached input tokens | `outputs/55maps-text-min-n10-uplift/verified-3of10/run.meta.json`; `post_run_report.md` |

All three runs have the same `gemini-3-flash-preview` model, system-instruction hash `2518d5298d9b…`, T = 0, `minimal`
thinking, no examples, and crop label. The request is the crop image plus fixed text
(`lib_verifier.build_candidate_content`), so a byte-identical crop means an identical request. "Carry-forward" in the UPL
log means the verifier configuration was carried forward, not the probabilities. No run.meta records the
served model version.

**Crops:** UPL crops are not on disk on either machine. Crops are deterministic: `extract_candidates.crop_region` uses
the floor pixel index on a 5.02 m/px raster, and the code has been unchanged since 2026-04-11. I regenerated them
in scratch. As validation, **all 12,390 regenerated TM crops matched the on-disk crops byte for byte.**

## 1. Matching (mutual nearest neighbour, EPSG:32635 centroids)

| Set | ≤ 1 m | ≤ 2 m | ≤ 5 m | Identical crops (1 / 2 / 5 m) | Passes 1–5 consistent |
|---|---|---|---|---|---|
| k4 (n = 10,170) | 4,387 (43.1 %) | 7,757 (76.3 %) | 9,964 (98.0 %) | 3,854 / 6,088 / 6,985 | 99.7–99.8 % |
| shell (n = 2,220) | 1,003 (45.2 %) | 1,484 (66.8 %) | 2,079 (93.6 %) | 955 / 1,255 / 1,460 | 99.7–100 % |

"Passes 1–5 consistent" means the UPL candidate's `contributing_passes` restricted to run_1..run_5 equals the TM
candidate's. So the matches are the same clusters, with centroids shifted by detections from passes 6–10. Median
offset is 1.15 m for k4 and 1.16 m for the shell. 70 % of the k4 pairs within 5 m are exact-request replicates.

## 2. Cross-date agreement (later minus earlier; the 39 May-3 k4 candidates are excluded)

| Pairs | n | Identical p | Mean / median abs(Δp) | Signed mean Δp | Flips @ 0.15 (up/down) | Flips @ 0.20 |
|---|---|---|---|---|---|---|
| k4 Apr→Jun, 1 m | 4,376 | 53.3 % | 0.068 / 0 | +0.016 | 3.68 % [3.16, 4.28] (80/81) | 3.82 % [3.29, 4.43] |
| k4 Apr→Jun, 2 m | 7,745 | 52.9 % | 0.073 / 0 | +0.017 | 3.80 % [3.39, 4.25] (148/146) | 4.03 % [3.61, 4.49] |
| k4 Apr→Jun, 5 m | 9,948 | 52.0 % | 0.077 / 0 | +0.018 | 4.13 % [3.76, 4.54] (207/204) | 4.33 % [3.95, 4.75] |
| k4 Apr→Jun, identical crop | 6,976 | 53.3 % | 0.071 / 0 | +0.017 | 3.84 % [3.42, 4.32] (134/134) | 4.06 % [3.62, 4.55] |
| shell Jun 6→11, 1 m | 1,003 | 60.1 % | 0.040 / 0 | +0.001 | 2.09 % [1.37, 3.18] (12/9) | 2.09 % [1.37, 3.18] |
| shell Jun 6→11, 2 m | 1,484 | 58.7 % | 0.041 / 0 | +0.001 | 2.36 % [1.70, 3.26] (18/17) | 2.43 % [1.76, 3.34] |
| shell Jun 6→11, 5 m | 2,079 | 57.4 % | 0.048 / 0 | +0.002 | 3.13 % [2.46, 3.97] (33/32) | 3.27 % [2.59, 4.13] |
| shell Jun 6→11, identical crop | 1,460 | 59.4 % | 0.042 / 0 | +0.002 | 2.53 % [1.84, 3.47] (21/16) | 2.47 % [1.79, 3.39] |

Brackets are Wilson 95 % intervals. The 12 May-3 k4 candidates matched within 2 m had no flips.

**Drift estimate.** These are cross-date minus same-week flip rates. The raw excess with a Newcombe 95 % interval is
+1.44 pp [0.45, 2.23] at 0.15 (2 m) and +1.31 pp [0.28, 2.15] at 0.15 (identical crops). Most of that excess comes
from composition: the shell has more p = 0 candidates, and those rarely flip. Re-weighting by the earlier
probability value (direct standardisation, both directions) shrinks the excess:

| Basis | @ 0.15 | @ 0.20 |
|---|---|---|
| 2 m | +0.50 to +0.93 pp | +0.37 to +0.73 pp |
| identical crop | +0.44 to +0.68 pp | +0.40 to +0.62 pp |

So the cross-date flip rate is about 3.8–4.0 %, against 3.3–3.7 % for same-week pairs of the same composition.
The same-week control on its own, at 2.4–2.5 %, reproduces the brief's 2.4 % re-invocation figure.

**Does the later verifier accept more?** Not at the decision points: flips are balanced (148 up / 146 down at 0.15).
The +0.017 signed mean Δp comes from movement away from the thresholds. Earlier p in [0.15, 0.5] (n = 466) rose by
+0.285 on average, against +0.140 for the shell (n = 48). Earlier p ≥ 0.8 fell by −0.033 for k4 and −0.073 for the
shell. Mid-range values are unstable on both dates.

**The flips are not direction-neutral with respect to truth (surprising — flagged).** At 0.15, 56.1 % of k4
up-flips lie within 50 m of an r2 reference point, against 43.2 % of down-flips and 36.7 % of all matched k4 pairs.
In the same-week shell control the direction is reversed: 33 % of up-flips and 47 % of down-flips (n = 18 and 17).

## 3. TM family re-read under one verifier date (r2, 50 m, the board's own scorer)

Reproduction is exact. Built with `load_manifest_probs` and the vote gate, as in `build_families`, then scored with
`compute_per_tile_tp_fp_fn` and `micro_f1`. The committed probabilities give the `sweep_TM.csv` TP/FP/FN triples
**identically** at all four points: TM-k4 is 0.7826 (3476/389/1542) and TM-oracle is 0.8103 (3717/439/1301).

In the table, "kept" is the share of candidates (k4 / shell) that keep their original probability. The last two
columns are k3 − k4 at 0.15 and (0.20, k3) − (0.15, k4).

| Probabilities | Kept | (0.15,k3) | (0.15,k4) | (0.20,k3) | (0.20,k4) | k3 − k4 @ 0.15 | (0.20,k3) − (0.15,k4) |
|---|---|---|---|---|---|---|---|
| (a) committed, mixed date | — | 0.8102 | 0.7826 | 0.8103 | 0.7817 | **+0.0275** | **+0.0277** |
| (b) all-June, 2 m (specified) | 23.7 % / 33.2 % | 0.8131 | 0.7867 | 0.8122 | 0.7848 | **+0.0264** | **+0.0255** |
| (b) k4 only, 2 m (shell stays 6 June) | 23.7 % / 100 % | 0.8139 | 0.7867 | 0.8131 | 0.7848 | +0.0271 | +0.0264 |
| (b) identical crops only | 31.3 % / 34.2 % | 0.8121 | 0.7862 | 0.8112 | 0.7846 | +0.0259 | +0.0249 |
| (b) all-June, 5 m | 2.0 % / 6.4 % | 0.8156 | 0.7896 | 0.8145 | 0.7877 | +0.0261 | +0.0249 |

Every k3 − k4 contrast above has a paired tile-swap p < 0.0001 (0 of 10,000 permutations, seed 42), with a null SD
of 0.0027–0.0028 and about 390–470 discordant tiles. **Under one verifier date, k3 still beats k4 by +0.025 to +0.026.**
That is 9–10 null SDs, 30–50 times the measured re-invocation band, and 3.5–6.5 times the cross-date floor in § 4.
Mixing dates inflates the contrast by 0.0004–0.0028 F1.

## 4. Cross-date floor on the k4 set alone (TM-k4, same candidates, April against June)

| Replacement | (0.15, k4) June | April | Δ F1 | p (tile swap) | Null SD | TP / FP |
|---|---|---|---|---|---|---|
| 2 m (24 % kept April) | 0.7867 | 0.7826 | **+0.0041** | 0.038 | 0.0020 | 3495/372 (from 3476/389) |
| identical crops only (31 % kept) | 0.7862 | 0.7826 | +0.0036 | 0.050 | 0.0018 | 3492/373 |
| 5 m (2 % kept) | 0.7896 | 0.7826 | +0.0069 | 0.0026 | 0.0023 | 3508/360 |
| 2 m at (0.20, k4) | 0.7848 | 0.7817 | +0.0031 | 0.148 | 0.0021 | 3446/318 |

The same-week control, replacing the shell's 6 June probabilities with 11 June ones, moves (0.15, k3) by −0.0007
and (0.20, k3) by −0.0009. That is the same scale as the brief's 0.0005–0.0008 band. **The cross-date floor for this
family is +0.004 to +0.007 F1, 5–9 times the same-date band**, and it points one way: the 11 June verifier scores
TM-k4 higher. The shift survives restriction to byte-identical requests (+0.0036), so it is not an artefact of crop
centring. The p-values are not corrected for the several tests run.

## What this check settles, and what it does not

- **Settles for TM:** the TM k3 − k4 advantage is not a verifier-date artefact. Under a mostly single-date (11 June)
  reading it is +0.026 at 0.15 and +0.025 for oracle against carried, both p < 0.0001.
- **Does not settle the all-April counterfactual.** No April verification of the shell exists, so (b) reads the
  contrast at June's date only. By proportion (2,220 shell candidates against 10,170 k4 candidates, with the drift
  worth +0.004–0.007 on k4), an April-dated shell would plausibly move the contrast by about 0.001–0.002. That is
  an extrapolation, not a measurement.
- **TM only.** TH7 and T03 have no later re-verification of their k4 sets (per the brief; not re-checked here). Their
  k3 − k4 contrasts remain date-confounded. This check shows only that the confound is small for the sibling
  family with the same verifier configuration.
- **Near-replicates.** 24 % of k4 and 33 % of shell candidates keep their original date under (b). Non-identical
  crops are offset by at least one pixel (5 m), and the UPL centroids average passes 6–10. The identical-crop
  variants remove the offset but keep more originals.
- **Cause of the drift is unattributable.** It could be a server-side model update to the preview alias or something
  else; the served model version is not recorded. The 0.0005–0.0008 band and the 2.4 % flip figure are the brief's,
  and are not re-measured here.
- **Board-wide implication (flag).** The April-dated carried cells (TM-k4, TH7-k4, T03-k4) carry a verifier-vintage
  component of a few thousandths of F1. The relevant noise floor for cross-date contrasts on the board is about
  0.004–0.007, not the re-invocation band.
- **One discarded null.** A random-flip null matched on earlier probability gave a spurious mean of −0.021,
  because flip propensity is not independent of truth given p. It is not reported as evidence.
