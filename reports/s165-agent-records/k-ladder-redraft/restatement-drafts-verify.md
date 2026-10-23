# Verification of the 15 drafted register outcomes (PR #52, restatement pass)

- **Verifier**: Claude (Anthropic), Claude Code, model lane Opus 5.5 (`claude-opus-5-5`), read-only sub-agent.
- **Date**: 2026-10-17.
- **Reviewed**: `origin/restatement-pass-s164` at `4367cecc5`, in a disposable detached worktree.
  The texts checked were `reports/s164-agent-records/restatement-pass.md` § 4 and
  `reports/s164-agent-records/restatement-pass-scripts/records/register/drafted-outcomes-final.json`,
  against the register `results/run-analyses.json` (`analyses[].outcome`).
- **Method**: I made a token-level diff of each current `outcome` against its draft. I then
  looked up every changed number in the regenerated artefacts committed on the branch,
  spot-checked unchanged numbers, and read the predicted outcomes and lapse notes for the
  verdicts. I ran no model call and no heavy computation. Two values had no stored field, so I
  computed them from committed files (means over a `probabilities.json` file, and sweep-band
  minimum and maximum over a CSV). Each of those is marked "computed".
- **Pre-checks**:
  - All 15 fenced drafts in § 4 are identical, after whitespace normalisation, to `drafted-outcomes-final.json`.
  - On this branch every register `outcome` is unchanged from `718d0ee08` and from `origin/main`.
  - All 15 rows are `re-sign-pending`.

All paths below are relative to the repository root on that branch.

## Summary

| Row | Numbers checked (changed + unchanged) | Mismatches | Verdicts OK? | Issues (most important first) |
|---|---|---|---|---|
| 4.1 grid-tilesize-overlap | 16 + 5 | 0 | Yes | p = 0.4033 is the D42 permutation p, but the text does not say the p instrument changed (minor) |
| 4.2 grid-postverifier | 29 + 6 | 0 | Yes; the 384 px failure is stated plainly | Kept sentence "The paired tile-bootstrap contrasts are the significance instrument" is stale: every quoted p is now a D42 permutation p. The RESTATED clause sets permutation p's beside the REVISED block's bootstrap p's without saying so. "at roughly HALF" now hangs off the failure clause |
| 4.3 stride-winner-ladder-exact | 4 + 1 (+ 1 p) | 0 | Yes | none |
| 4.4 image-b-modality | 8 + 2 | 0 | Yes | none |
| 4.5 image-b-thinking-pair | 3 + 3 | 0 | Yes (HP3's −0.0031 is inside ±0.02) | none |
| 4.6 gemini37-screen | 21 + 3 | 0 | Yes | Kept clause "registration pending materialisation" is stale: the 3.7 ladder rungs are registered. +0.0006 is correct on unrounded values, but the re-score record prints +0.0005 |
| 4.7 gemini37-image-gs | 15 + 2 | **2** | Yes; I3 FAILS stated plainly | **The all-3.7 gap is printed −0.0043 and the escalation margin +0.0043. Both should be −0.0044 / +0.0044.** The lapse note wrongly lists them as UNCHANGED. The restated findings doc says the draft prints −0.0044, which is false |
| 4.8 gemini37-fourth-cell | 10 + 3 | 0 | Yes | p = 0.0311 now crosses 0.05 with no comment (PI's choice) |
| 4.9 gemini38-screen-armv | 15 + 3 | 0 | Yes | none |
| 4.10 e45-bootstrap-pairings | 15 + 3 | 0 | Yes | Kept "the 2*min-tail p is convention-borrowed …" is stale since D42: the artefact's p is the permutation test's |
| 4.11 gs-era2-verified-board | 23 + 9 | 0 | Yes | none. The draft is byte-identical to the board builder's own `proposed_outcome` |
| 4.12 k-ladder | 38 + 10 | **3** | Mostly; see issues | **(a)** A kept sentence still cites "the US$1,100-to-US$43,000 per 0.001 F1 figures above", which contradicts the redrafted "about US$0.20 to US$27" and repeats the units slip. **(b)** "8 of the 15 interpretable ladders" should be **7 of 15**: tier E is counted in the numerator but is not among the 15. **(c)** "+0.0131" against the artefact's delta 0.013043 (+0.0130). **(d)** It keeps "the last step is the worst buy on every ladder" and "31 % to 64 %", which the PI-approved 2026-10-04 notes corrected (17 of 23; 31–62 %). **(e)** It mixes a clipped basis (15 ladders) with unclipped MCB counts (22 ladders) without saying so. **(f)** 60.3 % is the unclipped tier E reading; the clipped 48.8 % is not mentioned |
| 4.13 verifier-uplift-pairing | 13 + 5 | 0 | Yes | Name the new third F1 negative (3.7 image carried arm, −0.0017), which D65 (4) asked to be reported. "pending" means "not computable", not "scheduled" |
| 4.14 uplift-supplement-flatten | 4 + 2 | 0 | Yes | none (optional: say 66 of the 505 are conditions registered since 2026-09-12) |
| 4.15 null-exemplar-sensitivity | 12 + 6 | 0 | Yes | none |

**Rows fully OK as drafted**: 4.3, 4.4, 4.5, 4.9, 4.11, 4.14, 4.15. Rows 4.1, 4.8 and 4.13
have correct numbers and only wording suggestions.

Each section below lists the checks as `draft value | source file : key (or line) | found value | OK/MISMATCH`.

---

## 4.1 `grid-tilesize-overlap-2026-08-18`

Changed numbers. Unless another file is named, the source is `results/grid-2026-08-18/conditions/grid_conditions.json`.

| Draft value | Source | Found | Result |
|---|---|---|---|
| 512/12.5 F1 0.6845 [0.6336,0.7313] MCC 0.5431 | `cells[0]`: `rescored_f1_at_20m`, `f1_ci_lower`, `f1_ci_upper`, `tile_mcc` | 0.6845, 0.6336, 0.7313, 0.5431 | OK |
| 512/50 F1 0.7611 [0.7126,0.8023] MCC 0.5853 | `cells[1]` | 0.7611, 0.7126, 0.8023, 0.5853 | OK |
| 384/12.5 F1 0.6574 [0.6038,0.7056] MCC 0.3066 | `cells[2]` | 0.6574, 0.6038, 0.7056, 0.3066 | OK |
| 384/50 F1 0.7293 [0.6841,0.7686] | `cells[3]` | 0.7293, 0.6841, 0.7686 | OK |
| tile-size −0.0803 [−0.1236,−0.0394] | `results/grid-2026-08-18/grid_analysis.json`: `contrasts["tilesize_at_12.5pct (384 - 512)"]` delta, ci_lower, ci_upper | −0.080296, −0.123568, −0.039389 | OK |
| −0.0976 [−0.1206,−0.0752] | `grid_analysis.json`: `contrasts["tilesize_at_50pct (384 - 512)"]` | −0.097643, −0.120552, −0.075233 | OK |
| best-F1 gap 0.0926 | `grid_analysis.json`: `cost_efficiency.passes_versus_overlap.delta_best_f1` | −0.092574 | OK |
| (12.5 % − 50 %) +0.1207 at 512 px | `contrasts["overlap_at_512px (12.5% - 50%)"].delta` | 0.120719 | OK |
| +0.1381 at 384 px | `contrasts["overlap_at_384px (12.5% - 50%)"].delta` | 0.138066 | OK |
| "about 0.12-0.14" | derived from the two above | 0.1207–0.1381 | OK |
| interaction −0.0173 [−0.0580,+0.0248], p=0.4033 | `grid_analysis.json`: `interaction` difference_of_differences, ci_lower, ci_upper, p_two_sided | −0.017346, −0.058023, +0.024810, 0.4033 | OK |

Unchanged numbers spot-checked:

| Draft value | Source | Found | Result |
|---|---|---|---|
| 384/50 MCC 0.4909 | `grid_conditions.json`: `cells[3].tile_mcc` | 0.4909 | OK |
| 0.0304 union recall | `grid_analysis.json`: `passes_versus_overlap.delta_union_recall` | −0.030374 | OK |
| 30,130 calls, $18.53 billed | `grid_analysis.json`: `costs.total_calls`, `costs.total_flex_usd` | 30130, 18.5302 | OK |
| two of 228 swept cells undefined | `grid_analysis.json`: `len(sweep)`, `len(undefined_mcc_cells)` | 228, 2 | OK |
| 512 px wins at every overlap and every K | `cost_efficiency.frontier`: best_f1 by cell and K | 512 is higher at all 8 (overlap, K) pairs | OK |

Wording:

- **The p instrument changed silently (minor).** The signed p = 0.4902 was the bootstrap's.
  The PI-approved D42 note (2026-10-05, in `signature.attests`) records the permutation p as
  0.4681 at the branch point, and the draft's 0.4033 is the restated permutation p
  (`interaction.p_method`). A reader comparing old and new texts will put the whole 0.49 → 0.40
  move down to the restatement. Suggested fix: "… −0.0173 [−0.0580,+0.0248], p=0.4033 (paired
  permutation test, D42), spanning zero."

## 4.2 `grid-postverifier-2026-08-18`

Changed numbers. Unless another file is named, the source is `results/grid-2026-08-18/verifier_analysis.json`.

| Draft value | Source | Found | Result |
|---|---|---|---|
| 384/50 F1 0.9017 [0.8727,0.9244] MCC 0.8037 | `conditions[3]`: rescored_f1_at_20m, f1_ci_lower, f1_ci_upper, tile_mcc | 0.9017, 0.8727, 0.9244, 0.8037 | OK |
| 512/50 F1 0.8870 [0.8583,0.9118] MCC 0.8087 | `conditions[1]` | 0.887, 0.8583, 0.9118, 0.8087 | OK |
| 384/12.5 best p>=0.15 k>=7 F1 0.8761 MCC 0.7852 | `board_best.g384_ov048`: prob_t, min_votes, f1, mcc | 0.15, 7, 0.876095, 0.785181 | OK |
| registered p>=0.20 k>=7 F1 0.8752 [0.8424,0.9017] MCC 0.7852 | `conditions[2]`: prob_t, min_votes, rescored_f1_at_20m, CI, tile_mcc; `registered_point_is_best` | 0.2, 7, 0.8752, 0.8424/0.9017, 0.7852; False | OK (the two MCCs really are equal to 4 dp) |
| 512/12.5 F1 0.8368 [0.7995,0.8676] MCC 0.8011 | `conditions[0]` | 0.8368, 0.7995, 0.8676, 0.8011 | OK |
| (384−512) +0.0393 [+0.0052,+0.0741] p=0.0266 | `bootstrap_contrasts["tilesize_at_12.5pct (384 - 512)"]` | 0.039285, 0.005184, 0.074097, 0.0266 | OK |
| consensus-only −0.0803 | `grid_analysis.json`: `contrasts["tilesize_at_12.5pct (384 - 512)"].delta` | −0.080296 | OK |
| 50 %: [−0.0095,+0.0394] p=0.2454 | `bootstrap_contrasts["tilesize_at_50pct (384 - 512)"]` | −0.009458, 0.039447, 0.2454 | OK |
| ceilings 0.9112/0.9696 vs 0.8879/0.9603 | `grid_analysis.json`: `cost_efficiency.frontier`, K = 10, union_recall for g384_ov048 / g384_ov192 / g512_ov064 / g512_ov256 | 0.911215 / 0.969626 / 0.887850 / 0.960280 | OK |
| 512 px overlap −0.0502 [−0.0778,−0.0224] p=0.0003 | `bootstrap_contrasts["overlap_at_512px (12.5% - 50%)"]` | −0.050168, −0.077813, −0.022363, 0.0003 | OK |
| 384 px overlap −0.0256 [−0.0517,+0.0001] p=0.0541 | `bootstrap_contrasts["overlap_at_384px (12.5% - 50%)"]`; `excludes_zero` | −0.025584, −0.051707, +0.0000828, 0.0541; False | OK (the upper bound rounds to +0.0001) |
| interaction −0.0246 [−0.0613,+0.0114] p=0.1831 | `interaction` | −0.024585, −0.061345, +0.011354, 0.1831 | OK |
| pure-verifier top 0.8187 (384/12.5) | `board_pure_verifier_k1.g384_ov048.f1` (the maximum of the four) | 0.818687 | OK |
| trails by 0.057-0.207 | `board_best[c].f1 − board_pure_verifier_k1[c].f1` | 0.0574 (384/12.5) … 0.2074 (512/50) | OK |
| MCC 0.785-0.809 | `board_best[*].mcc` | 0.785181 … 0.808663 | OK |
| gain +0.126..+0.219 | `verifier_gain_over_consensus` | 0.1259 … 0.2187 | OK |
| RESTATED: single-pass −0.0803/−0.0976 | `grid_analysis.json`: `contrasts` tile size at 12.5 % / 50 % | −0.080296 / −0.097643 | OK |
| RESTATED: −0.0271 [−0.0809,+0.0254] p=0.3081 | `bootstrap_contrasts_consensus_k10_baseline["tilesize_at_12.5pct (384 - 512)"]` | −0.027066, −0.080946, +0.025406, 0.3081 | OK |
| RESTATED: −0.0319 [−0.0704,+0.0048] p=0.0862 | `…_k10_baseline["tilesize_at_50pct (384 - 512)"]` | −0.031866, −0.070447, +0.004813, 0.0862 | OK |
| RESTATED: +0.0393 p=0.0266 | as above | — | OK |
| RESTATED: overlap baseline −0.0766 p=0.0006 / −0.0718 p=0.0037 | `…_k10_baseline["overlap_at_512px…"]`, `["overlap_at_384px…"]` | −0.076632, 0.0006 / −0.071832, 0.0037 | OK |

Unchanged numbers spot-checked:

| Draft value | Source | Found | Result |
|---|---|---|---|
| 1,402/2,585/1,827/3,319 | `gates.union_counts_measured` | 1402/2585/1827/3319 | OK |
| 9,133 verified, zero failures | `verifier.candidates_verified`, `verifier.failures` | 9133, 0 | OK |
| $12.5428 list → $6.2714, $6.33, −$0.06 | `billing.total_list_usd`, `total_flex_usd`, `costed_estimate.total_usd`, `delta_usd` | 12.5428, 6.2714, 6.33, −0.0586 | OK |
| 580-row sweep | `results/grid-2026-08-18/verifier_sweep.csv` (581 lines including the header) | 580 | OK |
| k>=5..10 | `board_best[*].min_votes` | 5, 9, 7, 10 | OK |
| +0.0147 at 50 % | `bootstrap_contrasts["tilesize_at_50pct…"].delta` | 0.014701 | OK |

Verdicts: "SURVIVES … at 512 px but FAILS at 384 px" agrees with `excludes_zero` (True at 512 px,
False at 384 px) and the p values. The failure is stated plainly in (2) and again in the
RESTATED clause.

Wording:

1. **Stale sentence kept (should fix).** The draft keeps "The paired tile-bootstrap contrasts are
   the significance instrument (Decision 10 resampler, B=10,000 per E82, seed 42 …)". Every p
   the draft now quotes is the D42 paired tile-swap permutation p: every block's `p_method` in
   `verifier_analysis.json` says so. The signed text quoted bootstrap p's (0.034, 0.231, 0.0208,
   0.234), and the D42 note of 2026-10-05 deliberately left them alone. The draft therefore
   mixes a permutation p with a sentence naming the bootstrap as the instrument.
   - Suggested fix: "The paired tile bootstrap (Decision 10 resampler, B=10,000 per E82, seed
     42 …) gives the intervals; p values are the paired tile-swap permutation test's (D42;
     10,000 permutations, seed 42)".
   - In the RESTATED clause, add "(p values now the D42 permutation test's)". Otherwise 0.281 →
     0.3081, 0.089 → 0.0862, 0.0004 → 0.0006 and 0.0026 → 0.0037 read as pure restatement
     moves. Part of each move is the instrument change: at the branch point the permutation
     p's were 0.2975, 0.0939, 0.0008 and 0.0032 (D42 note in `signature.attests`).
2. **Dangling clause (minor).** "… but not at 384 px (−0.0256 …), at roughly HALF the
   consensus-only margin — … the surviving advantage tracks the recall-ceiling edge" now
   follows the failure clause, so "roughly HALF" seems to describe the 384 px result. Against
   the K = 10 baseline the ratios are 0.66 at 512 px (−0.0502 / −0.0766) and 0.36 at 384 px
   (−0.0256 / −0.0718). Suggested fix: "… the 512 px margin about two-thirds of the
   consensus-only one (−0.0502 against −0.0766) and the 384 px margin about a third (−0.0256
   against −0.0718) — the corroboration filter and the verifier are partially redundant …".
3. **Minor.** The 384/12.5 best point is the only per-cell figure without a CI, although the
   header says "BCa CI95 at B=10,000". It has none because `verified-best/` holds detections
   only. That is acceptable, but a few words would help: "(best point: no interval computed)".

## 4.3 `stride-winner-ladder-exact-2026-08-25`

| Draft value | Source | Found | Result |
|---|---|---|---|
| N=1 0.8737 | `results/stride-2026-08-25/plateau_analyses.json`: `winner_ladder_exact.N.1.best.f1` | 0.873672 | OK |
| N=3 0.8993 | `winner_ladder_exact.N.3.best.f1` | 0.899263 | OK |
| N=5 0.8937 | `winner_ladder_exact.N.5.best.f1` | 0.893720 | OK |
| K=10 0.9075 | `board_13cell.f1.g384_ov128` | 0.907543 | OK |
| (unchanged) ~$2.64 all-in | `winner_ladder_exact.N.3.all_in_flex_usd` | 2.64 | OK |
| (verdict) "N=3 within noise of K=10" | `results/k-ladder-2026-09-12/mcc-test/tiering/gs-stride-a/tiering_20m.json`, pair n3 against k10 (around line 144) | −0.008284, p 0.2275, BH 0.273, not significant | OK |

The row has no other unchanged numbers apart from "Obs 436". No wording issues.

## 4.4 `image-b-modality-2026-08-28`

The source is `results/image-b-gs-2026-08-28/analysis.json`.

| Draft value | Key | Found | Result |
|---|---|---|---|
| text +0.0559 @20m | `head_to_head_20m.observed_diff` | 0.055896 | OK |
| p=0.0005 | `head_to_head_20m.p_value` | 0.0005 | OK |
| gap 0.0559 → 0.0245 | `buffer_curves.text.75.f1 − buffer_curves.image.75.f1` | 0.911271 − 0.886747 = 0.024524 | OK |
| MCC 0.8139 (image) | `image_best.mcc` | 0.813866 | OK |
| vs 0.8037 (text) | `buffer_curves.text.20.mcc` | 0.803724 | OK |
| N3−N10 −0.0136 | `saturation_N3_vs_N10.observed_diff` | −0.013615 | OK |
| p=0.1189 | `saturation_N3_vs_N10.p_value` | 0.1189 | OK |
| Image N=1 0.6998 | `ladder.1.best.f1` | 0.699805 | OK |
| (unchanged) prob 0.15 | `image_best.prob_t` | 0.15 | OK |
| (unchanged) IP5 indeterminate | the p above is above 0.05; the effect is below `results/sensitivity-mde-2026-08-28/sensitivity.json` `mde_table[2].mde_50pc_power` | 0.0172 | OK |

No wording issues.

## 4.5 `image-b-thinking-pair-2026-08-28`

The source is `results/image-b-gs-2026-08-28/high/pair_verdicts.json`.

| Draft value | Key | Found | Result |
|---|---|---|---|
| HIGH −0.0068 | `hp1_high_vs_min_20m.observed_diff` | −0.006841 | OK |
| p=0.668 | `hp1_high_vs_min_20m.p_value` | 0.668 | OK |
| MCC −0.0031 | `hp3_mcc.delta` | −0.003106 | OK; inside HP3's registered ±0.02 (`predicted_outcome`) |
| (unchanged) union +126 % | `hp2_union.growth` | 1.2605 | OK |
| (unchanged) (0.20,k8) | `hp4_points.high` | [0.2, 8] | OK |
| (unchanged) 2.91x | `hp5_cost.ratio` | 2.9097 | OK |

No wording issues.

## 4.6 `gemini37-screen-2026-08-28`

The sources are under `results/gemini37-screen-2026-08-28/`.

| Draft value | Source | Found | Result |
|---|---|---|---|
| K=5 0.9238 at (0.10, k5) | `analysis.json`: `image_best.f1`, prob_t, min_votes | 0.923777, 0.1, 5 | OK |
| +0.0221, p = 0.0971 | `analysis.json`: `head_to_head_20m` (anchor − cell), p_value | −0.022098, 0.0971 | OK |
| null SD 0.0134 | `head_to_head_20m.null_std` | 0.013407 | OK |
| K=10 adds +0.0006 | `k10/analysis.json` `image_best.f1` − K=5 | 0.924331 − 0.923777 = 0.000554 | OK at 4 dp. `reports/s164-agent-records/rescore-repaired-gs.md` line 238 prints "+0.0005" (rounded endpoints); the two records disagree in the 4th decimal |
| (0.9243, p = 0.1231) | `k10/analysis.json`: `image_best.f1`, `head_to_head_20m.p_value` | 0.924331, 0.1231 | OK |
| N5−N10 −0.0013, p = 0.7921 | `k10/analysis.json`: `saturation_N5_vs_N10` | −0.001254, 0.7921 | OK |
| ladder 0.8652/0.9118/0.9231/0.9243 | `k10/analysis.json`: `ladder.{1,3,5}.best.f1` + `image_best.f1` | 0.865169/0.911765/0.923077/0.924331 | OK |
| swap 0.9364 at (0.80, k5) | `swap37/analysis.json`: `image_best` | 0.936416, 0.8, 5 | OK |
| P 0.9268 / R 0.9463 / MCC 0.8192 | `swap37/analysis.json`: `image_best` precision, recall, mcc | 0.926773 / 0.946262 / 0.819173 | OK |
| +0.0347, p = 0.0065 | `swap37/analysis.json`: `head_to_head_20m` | −0.034738, 0.0065 | OK |
| mean probability 0.699 (3.7) | computed: mean `results[*].mound_probability` in `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap37_repaired/probabilities.json` (791 rows) | 0.698761 | OK |
| 0.594 (carried) | computed: the same over `…/verify_repaired/probabilities.json` (791 rows) | 0.594058 | OK |
| 0.687 / 0.587 at `planning/gemini37-screen-2026-08-28.md:110` | that line | "mean prob 0.687 vs the carried 0.587" | OK |
| (unchanged) 791-candidate union | `analysis.json`: `verifier_probabilities.n_results` | 791 | OK |
| (unchanged) +0.0126 for the role swap | 0.936416 − 0.923777 | 0.012639 | OK |
| (unchanged) only cell beating the anchor on F1 and MCC | anchor MCC 0.8037 (`image-b…/analysis.json` `buffer_curves.text.20.mcc`); swap 0.8192; K=5 0.7914; K=10 0.7971 | holds | OK |

Wording:

- **Stale on arrival (pre-existing, should fix while re-signing).** "The ladder rungs are
  re-derived; registration pending materialisation." The `gemini37-screen-2026-08-28` entry of
  `results/run-conditions.json` (`decomposition`) now lists `g37-text-k1-verified-opmax`,
  `g37-text-k1-verified-carried-p0.10-k1` and `g37-text-k3-verified-opmax`. Suggested fix:
  "The ladder rungs are re-derived; the K = 1 and K = 3 rungs have since been registered (the
  K-ladder, k-ladder-2026-09-12)." The PI should confirm the exact set first.
- **Rounding (informational).** +0.0006 (unrounded) against the record's +0.0005 (rounded
  endpoints). The draft is right at 4 dp. Row 4.12 uses the other convention, as noted there.

## 4.7 `gemini37-image-gs-2026-09-01`

The sources are under `results/gemini37-image-gs-2026-09-01/`.

| Draft value | Source | Found | Result |
|---|---|---|---|
| G3 gap +0.0559, p = 0.0005 | `gap_test.json`: `g3_gap_committed` | 0.0559, 0.0005 | OK |
| carried pair −0.0143 (p = 0.158) | `gap_test.json`: `pairs.carried-verifier` observed_diff, p_value | −0.014296, 0.158 | OK |
| **all-3.7 pair −0.0043** (p = 0.6767), text unchanged | `gap_test.json`: `pairs.all-3.7.observed_diff` −0.00435. Unrounded from the arms: `results/gemini37-screen-2026-08-28/swap37/analysis.json` image_best.f1 0.9364161849710984 − `arm2/analysis.json` image_best.f1 0.9407665505226481 | **−0.0043504 → −0.0044** | **MISMATCH**. p 0.6767 is OK |
| gap change −0.060 to −0.070 | 0.0559 + 0.0044 = 0.0603; 0.0559 + 0.0143 = 0.0702 | — | OK |
| MDE80 ~0.025 | `results/sensitivity-mde-2026-08-28/sensitivity.json`: `mde_table[2].mde_80pc_power` | 0.024632 | OK |
| "about four times" | 0.0923 / 0.0221 = 4.18; 0.0950 / 0.0221 = 4.30 | — | OK |
| 0.9381, carried, at (0.05, k5) | `arm1/analysis.json`: `image_best` f1, prob_t, min_votes | 0.938073, 0.05, 5 | OK |
| 0.9353 at registered (0.10, k5) | `arm1/op-eval/evaluation.json`: `summary.buffers[buffer_metres=20].f1`; `summary.n_detections` | 0.9353; 438 | OK |
| 0.9408 (3.7 verifier) | `arm2/analysis.json`: `image_best.f1` | 0.940767 | OK |
| G3 image anchor 0.8458 | `results/image-b-gs-2026-08-28/analysis.json`: `image_best.f1` | 0.845783 | OK |
| gains +0.0923 / +0.0950 | 0.938073 − 0.845783; 0.940767 − 0.845783 | 0.092290 / 0.094984 | OK |
| text-side step +0.022 | 0.923777 − 0.901679 | 0.022098 | OK |
| 3.7 arm at (0.90, k5) | `arm2/analysis.json`: `image_best.prob_t`, `min_votes` | 0.9, 5 | OK |
| escalation 0.9408 against 0.9364 | as above | — | OK |
| **escalation +0.0043** at p = 0.677 | as the all-3.7 row | **+0.0044** | **MISMATCH**. p OK (0.6767 → 0.677) |
| (unchanged) I2 bar ~0.031 | `predicted_outcome` ("gap < ~0.031") | — | OK |
| (unchanged) "roughly 2.5x" | 0.060 / 0.025 = 2.4; 0.070 / 0.025 = 2.8 | — | OK |

The 88–157 t/call, 79.5 %, 16 % / 54 % and $22.50 / $32–36 figures are unchecked: the pass did not move them.

Verdicts:

- "I3 FAILS on the carried-verifier arm, whose optimum moved to (0.05, k5), below the predicted
  0.10-0.20" is correct. `predicted_outcome` gives I3 as "carried-verifier arm optimum at prob
  in {0.10-0.20}", and the failure is stated plainly. The 3.7-verifier limb holds (0.90 ≥ 0.6).
- I1, I2, parity, and the escalation trigger not being met are all consistent with the artefacts.

Issues:

1. **MISMATCH, should fix before approval.** The draft keeps −0.0043 and +0.0043. The record's
   own § 2.6 and § 3 table say the restated all-3.7 gap prints −0.0044 (unrounded −0.0043504).
   `results/gemini37-image-gs-2026-09-01/findings.md` lines 178–181, corrected in `94d5815b3`,
   say it "rounds to −0.0044, as the drafted register outcome prints it". **The drafted outcome
   does not print it.** `drafted-outcomes-final.json` and `drafted-outcomes-gs.json` both print
   −0.0043.
   - Suggested fix: "… and −0.0044 (p = 0.677) on the all-3.7 pair …" and "… all-3.7 text swap
     0.9364 is +0.0044 at p = 0.677 …". This also makes the p precision consistent: the draft
     currently prints 0.6767 in one place and 0.677 in the other.
   - The **lapse note** in `signature.attests` puts "the all-3.7 gap −0.0043, p 0.6767
     (gap_test.json −0.004345 → −0.00435, the same at four places) and so the escalation margin
     +0.0043" under UNCHANGED. It should move to CHANGED (−0.0043 → −0.0044; +0.0043 → +0.0044).
   - The findings doc's sentence will be true only once the draft is fixed.

## 4.8 `gemini37-fourth-cell-gs-leg-2026-08-31`

The source is `results/gemini37-fourth-cell/gs-leg/analysis.json`.

| Draft value | Key | Found | Result |
|---|---|---|---|
| 0.9220 at (0.98, k10) | `image_best` f1, prob_t, min_votes | 0.921951, 0.98, 10 | OK |
| P 0.9643 / R 0.8832 / MCC 0.8350 | `image_best` precision / recall / mcc | 0.964286 / 0.883178 / 0.835024 | OK |
| anchor 0.9017 | `anchor.registered` | 0.9017 | OK |
| +0.0203, p = 0.0311 | `head_to_head_20m` observed_diff, p_value | −0.020273, 0.0311 | OK |
| mean probability 0.214 | computed: mean `mound_probability` over `outputs/grid-2026-08-18/verifier/g384_ov192/verify_37_repaired/probabilities.json` (3,319 rows) | 0.213513 | OK |
| 0.699 on its own union | as 4.6 (swap37) | 0.698761 | OK |
| 0.209 / 0.687 at `planning/gemini37-55map-2026-08-29.md:200` | that line | "mean prob 0.209 vs 0.687 on its own union" | OK |
| (unchanged) :201 carried point (0.98, k10) | `planning/gemini37-55map-2026-08-29.md:201` | present | OK |
| (unchanged) 3,319 candidates | `verifier_probabilities.n_results` | 3319 | OK |
| (unchanged) 10,000 permutations, 487 tiles | `head_to_head_20m.n_permutations`, `n_tiles` | 10000, 487 | OK |

"~$3" is unchecked.

Wording (PI's choice, not an error): p = 0.0311 is now below 0.05, while the signed text read
0.0563. The text claims no significance either way (§ 3 says so), but a reader will see p = 0.03.
If the PI wants no implied claim, append "(a single sweep-selected comparison, no family
correction)". The board-frame argmax moved to (0.95, k10) (§ 2.2), but the GS-frame argmax this
row quotes did not. The draft is correct as written.

## 4.9 `gemini38-screen-armv-2026-09-04`

The sources are under `results/gemini38-screen-2026-09-04/armV/`.

| Draft value | Source | Found | Result |
|---|---|---|---|
| 0.9358 at (0.88, k5) | `analysis.json`: `image_best` | 0.935823, 0.88, 5 | OK |
| P 0.9347 / R 0.9369 / MCC 0.8331 / 429 det. | `analysis.json`: `image_best` | 0.934732 / 0.936916 / 0.833080 / 429 | OK |
| dF1 −0.0006, p = 0.7769 | `pair_test.json`: `pairs.all-3.7` | −0.000594, 0.7769 | OK |
| +0.0120, p = 0.0764 | `pair_test.json`: `pairs.carried-G3` | 0.012046, 0.0764 | OK |
| +0.0139 MCC (0.8331 vs 0.8192) | 0.833080 − 0.819173 (`swap37/analysis.json` `image_best.mcc`) | 0.013906 | OK |
| losing 0.0006 F1 | as dF1 | — | OK |
| 3.7 band 0.9343-0.9364 | computed: `results/gemini37-screen-2026-08-28/swap37/sweep_20m.csv`, min_votes 5, prob_t 0.20–0.92 | 0.934256–0.936416 | OK |
| carried band 0.8520-0.9021, spread 0.0502 | computed: `results/gemini37-screen-2026-08-28/sweep_20m.csv`, min_votes 5, prob_t 0.20–0.85 (its lattice has no 0.88 or 0.92) | 0.851995–0.902148, 0.050153 | OK |
| (unchanged) 3.8 within 0.0022 | computed: `sweep_20m.csv`, k5, 0.20–0.92 | 0.002179 | OK |
| (unchanged) 3.7 spread 0.0022 | as above | 0.002160 | OK |
| (unchanged) 791 union | `pair_test.json`: `union` | "791 candidates" | OK |

No wording issues.

## 4.10 `e45-bootstrap-pairings`

The source is `results/e45-bootstrap-pairings/e45_bootstrap_pairings.json`.

| Draft value | Key | Found | Result |
|---|---|---|---|
| H2 dF1 +0.073730 | `results.H2.bootstrap.registered_b1000.observed_delta` | 0.07373 | OK |
| B=1,000 [+0.049520, +0.101772] | `…registered_b1000.ci95` | 0.04952, 0.101772 | OK |
| B=10,000 [+0.048250, +0.101597] | `…e54_sensitivity_b10000.ci95` | 0.04825, 0.101597 | OK |
| H3 dF1 +0.429693 | `results.H3.bootstrap.registered_b1000.observed_delta` | 0.429693 | OK |
| [+0.392114, +0.470439] | `H3 …registered_b1000.ci95` | 0.392114, 0.470439 | OK |
| [+0.388060, +0.472072] | `H3 …e54_sensitivity_b10000.ci95` | 0.38806, 0.472072 | OK |
| (unchanged) gates 7/7 | `results.H2.reproduction_gate` (7 checks, all `pass`) | 7/7 | OK |
| (unchanged) gates 4/4 | `results.H3.reproduction_gate` (4 checks) | 4/4 | OK |
| (unchanged) seed 42; "AS PREDICTED", all CIs exclude zero | `ci_excludes_zero` True ×4 | — | OK |

Wording:

- **Stale since D42 (pre-existing, worth fixing at re-sign).** "the 2*min-tail p is
  convention-borrowed from the family H1 leg, not registered". The artefact's `method` now
  reads "p-value: paired tile-swap permutation test, 10,000 permutations, seed 42 (D42)", and
  the PI-approved D42 note (2026-10-05) says the bootstrap's 2 × min-tail p was retired.
  Suggested fix: "the p value is the paired tile-swap permutation test's (D42), not registered".
- The new dated clause about blind verification is clear and accurate.

## 4.11 `gs-era2-verified-board-2026-09-10`

The sources are under `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/`. The draft
is byte-identical to `provenance.json` → `re_sign_pending.proposed_outcome`, the text the board
builder generates itself.

| Draft value | Source | Found | Result |
|---|---|---|---|
| withheld 0.8616 / 0.8747 / 0.9135 | `tiering_20m.json`: `withheld_cells[*].eval_f1` | 0.8616 / 0.8747 / 0.9135 | OK |
| 8075/11175 | `tiering_20m.json`: count of `pairwise[*].significant` | 8075 of 11175 | OK |
| 14 tiers; Tier 1 = 5 | `tiers` (len), `tie_set` (len) | 14, 5 | OK |
| MCB admissible 52 | `mcb/gs-era2-verified-board-2026-09-10_b20_m1.json`: `hsu_not_ruled_out` (len) | 52 | OK |
| top five 0.9332 / 0.9289 / 0.9282 / 0.9278 / 0.9169 with the five labels | `ranking[0..4]` eval_f1 and label | identical | OK |
| G6 max \|delta\| 0.0079 | `frame-deltas.md`, row `grid-2026-08-18::g384-ov192-k10-verified37-p0.98-k10` | −0.0079 (the largest) | OK |
| MCC family 3001/11175, 6 tiers | `mcc_permutation.n_significant`, `n_tiers` | 3001, 6 | OK |
| MCC Tier 1 = 34, "and 29 more" | `mcc_permutation.tie_set` (len) | 34 (34 − 5 = 29) | OK |
| MCC MCB 60 | `mcb/…_mcc_b20_m1.json`: `hsu_not_ruled_out` (len) | 60 | OK |
| (unchanged) 9 in both sets | intersection of the two `hsu_not_ruled_out` sets | 9 | OK |
| (unchanged) MCC leaders 0.8887/0.8848/0.8766/0.8726/0.8640 | `mcc_permutation.ranking[0..4].mcc` | identical | OK |
| (unchanged) G2 0, G3 0, G4 110/110 | `gates.json` | 0, 0, 110/110 | OK |
| (unchanged) 150 of 153 | `n_cells`, `n_cells_withheld` | 150, 3 | OK |

No wording issues beyond the row's existing jargon (MCB, G1–G6, "greedy clique"), which is
unchanged.

## 4.12 `k-ladder-2026-09-12`

The sources are under `results/k-ladder-2026-09-12/`. "P2" means `phase2/ladders.json` and "P1"
means `ladders.json`.

| Draft value | Source | Found | Result |
|---|---|---|---|
| last step about US$0.20 | P1, GS stride A rungs K5 (`f1_headline` 0.8937, `cost.usd` 3.8056) → K10 (0.9075, 6.5445) | +0.0138 for US$2.7389, so US$0.198 per 0.001 | OK |
| … to US$27 | P1, 3.7 arm 1: K3 oracle (0.8705, 94.3107) → K5 oracle (0.8727, 153.1642) | +0.0022 for US$58.85, so US$26.75 per 0.001 | OK on oracle rows. On the carried K5 row (0.8551) the step loses F1 |
| 3.7 K5→K10 +0.0004 for US$8.68, about US$22 | P2, "Gemini 3.7 text, GS B geometry", rungs K5 / K10 `opmax.f1_20` and `all_in_flex_usd` | 0.9165 → 0.9169; 9.1454 → 17.8281 (8.6827); US$21.7 per 0.001 | OK |
| HIGH text +0.0955 (T 1.0) | P2 `summary[HIGH text T 1.0].gain` (clipped basis) | 0.0955 | OK |
| (unchanged) +0.0559 / +0.0735 | P2 `summary` | 0.0559 / 0.0735 | OK |
| (unchanged) image +0.0780 / +0.0959 / +0.1514 | P2 `summary` | 0.078 / 0.0959 / 0.1514 | OK |
| 15 interpretable, F1 rises on all 15, MCC falls on 10 | P2 `summary[*].mcc_verdict`: 7 not withheld (5 down, 1 up, 1 flat); P1 8 ladders, `mcc-test/summary.json` `mcc_direction_k1_to_best` negative on 5 | 7 + 8 = 15; 5 + 5 = 10 | OK |
| GS ladder +0.0131 | `mcc-test/gs-stride-a.json`: `pairs[0].mcc.delta`; `mcc-test/summary.json` `mcc_direction_k1_to_best` | **0.013043 → +0.0130** | **MISMATCH (rounding)**. +0.0131 is the difference of rounded endpoints (0.8079 − 0.7948), the same convention the signed +0.0135 used (the artefact's old delta was 0.013419) |
| BH p = 0.7633 | `pairs[0].mcc.p_bh` | 0.76332 | OK |
| "no raw value is now recorded" | P2 rungs: `tile_mcc` null; the lapse note says the same of `phase2/scores.json` | null | OK (see wording) |
| GS MINIMAL range +0.0139..+0.0600 | P2 `summary` gains of the six MINIMAL ladders; `tension/effect-sizes.json` rows | 0.0139 … 0.06 | OK |
| **K=1 highest tile-MCC on 8 of the 15** | the 15 = P1's 8 + P2's 7 not withheld; `mcb/summary.json` `ladders[*].mcc.best_K` = 1 on 37arm1, 37arm2, stride-b-g37vf, high-text-t0.3, high-image-t0.7, high-image-t1.0, scale-4 | **7 of 15** (8 only if tier E is counted, but tier E is not among the 15; P1/P2 own-frame MCCs give the same 7) | **MISMATCH** |
| geometry 2.2x | 0.1441 / 0.0660 = 2.18; 0.0947 / 0.0425 = 2.23 | — | OK |
| +0.1441 / +0.0660 / +0.0947 / +0.0425 | `results/grid-2026-08-18/grid_analysis.json` `cost_efficiency.frontier` best_f1 K10 − K1; `tension/grid-overlap.json` `cells[*].delta_f1_k1_to_k10` | 0.1441 / 0.065954 / 0.0947 / 0.042509 | OK |
| MCC rises +0.029..+0.132 | frontier `best_mcc` K10 − K1 | 0.0291 … 0.1321 | OK |
| "about 60 %" and 60.3 % | 1 − 0.0262 / 0.0660 (unrounded 1 − 0.026191 / 0.065954 = 0.6029) | 0.603 | OK |
| +0.0660, +0.0444 (consensus) | `tension/grid-overlap.json` `cells[0]` delta_f1 / delta_mcc | 0.065954 / 0.044361 | OK |
| 0.7293/0.4909 at K=10 | `cells[0].rungs.10` | 0.729258 / 0.490858 | OK |
| verified +0.0262, −0.0238; 0.8680/0.8211; 0.8942/0.7973 | `tier-e/ladder.json` `rungs[0]` and `rungs[3]` f1_20 / tile_mcc | 0.868 / 0.8211; 0.8942 / 0.7973 | OK |
| swing 0.0682 | 0.044361 + 0.0238 | 0.0682 | OK |
| MCC whole ladder 13 of 22 | `mcb/summary.json` `roll_up.ladders_whose_MCC_admissible_set_is_the_whole_ladder` | 13 | OK |
| six of twenty exclude K=10 on MCC | count of `ladders[*]` with 10 in `rungs` and not in `mcc.hsu_admissible_K` | 6 of 20 | OK |
| GS w_upper 0.0159-0.0326 | `ladders[*].f1.hsu_w_upper` (GS / tier E / Phase 2) | 0.015867 … 0.032625 | OK |
| (unchanged) 55-map 0.0047-0.0056 | as above (55-map) | 0.004681 … 0.005639 | OK |
| (unchanged) K=3 admissible 12 of 22; cheapest on 10 | `roll_up…contains_K3`; count min(adm) = 3 | 12; 10 | OK |
| (unchanged) no F1 set excludes K=10; twenty have K=10 | `roll_up…excludes_K10`; rung count | 0; 20 | OK |
| (unchanged) K=1 out on F1 on 20 of 22; in on MCC on 22 of 22; highest MCC on 13 | `ladders[*]` | 20; 22; 13 | OK (all on the unclipped MCB; 13 includes tier E and five clipped ladders) |
| (unchanged) {K = 1} alone on two ladders | `55map-stride-b-g37vf-r2`, `37arm2-r2` `mcc.hsu_admissible_K` | [1], [1] | OK |
| (unchanged) two single-tier MINIMAL ladders admissible whole | `roll_up…F1…whole_ladder`: min-text-t0.7, image-t0.3 | 2 | OK |
| (unchanged) "on nine ladders nothing below K = 5 is admissible" | count with min(F1 adm) ≥ 5 | **10** (also 10 at `718d0ee08`) | Could not reproduce. This is pre-existing and the pass did not move it. It may depend on a qualifier I could not reconstruct |
| (unchanged) significant falls −0.0099 / −0.0275 / −0.0112 | `mcc-test/summary.json` 37arm1 / 37arm2 / stride-b-g37vf | −0.009904 / −0.027536 / −0.011152 | OK |
| (unchanged) 37 % to 93 % | P2 `share_at_k3` 0.3718–0.9146; P1 arm 1 (0.8705 − 0.8413) / (0.8727 − 0.8413) = 0.93 | 37–93 % | OK |

Verdict checks:

- The "TILE-MCC DOES NOT FOLLOW F1" counts are right (15, 10).
- HIGH image T 1.0 is not clipped (P2 `score_basis` "as-evaluated"), so its significant fall can stand.
- § 8.6 (the verifier absorbs about 60 % and reverses the MCC sign) agrees with the unclipped tier E reading.

Issues, most important first:

1. **Internal contradiction (MISMATCH, must fix).** The MCB paragraph keeps "which is the formal
   counterpart of the US$1,100-to-US$43,000 per 0.001 F1 figures above". The figures above now
   read "about US$0.20 to US$27". The kept sentence also repeats the units slip that the
   PI-approved 2026-10-04 note recorded. Suggested fix: "… the formal counterpart of the
   per-0.001-F1 last-step prices above".
2. **"8 of the 15 interpretable ladders" (MISMATCH).** The lapse note derives 8 as mcb's 13
   minus the 5 clipped ladders. Mcb's 13 includes tier E, which is not one of the 15 (P1's 8 +
   P2's 7). The correct figure is **7 of the 15**, or "8 of the 16 including tier E". The
   signed "13 of the 21" had the same overcount and should have read 12.
3. **Known-false SHAPE clause carried forward (should fix; the PI already ruled on it).** The
   draft rewrites the prices in "while the last step is the worst buy on every ladder, at …"
   but keeps the claim itself. The PI-approved second note of 2026-10-04 (ruling D25, in
   `signature.attests`) says it holds on **17 of 23**. The same notes correct K = 3's cost share
   to **31–62 %**, while the draft keeps "31 % to 64 %". My recomputation agrees: Phase 2
   31.5–43.5 %; Phase 1 maximum 62.4 % (3.7 arm 2: 99.03 / 158.58). The US$0.20–27 range also
   silently covers only ladders whose last step gains F1. On the restated tables the last step
   loses F1 on MINIMAL text T 0.3 and T 0.7, HIGH text T 0.3, HIGH image T 0.7 and tier E.
   Suggested fix: "… while the last step is the dearest per 0.001 F1 on 17 of the 23 ladders,
   at about US$0.20 to US$27 per 0.001 F1 where it gains at all (on five it loses F1) …", with
   "31 % to 62 %". The PI should confirm the 17 of 23 count on the restated tables; I did not
   recount it.
4. **Two bases in one text, unexplained.** The 15 (from 21) drops six Gemini 3 ladders because
   the D51 clip-to-common-area build withholds their tile-MCC. "Interpretable" no longer names
   the reason. The MCB section's MCC counts ("22 of 22", "13 of them", "13 of 22 whole", "six
   of twenty") still include those six ladders on unclipped scores; the lapse note says so, the
   draft does not. Suggested insertion after "Across the 15 verified ladders": "(the six Gemini
   3 ladders the D51 clip reports clipped have their tile-MCC withheld and are left out here;
   the MCB counts below are on the unclipped scores and include them)".
5. **§ 8.6 basis (PI decision; worth one clause).** 60.3 % uses tier E unclipped. Record § 1.4
   and the restated `findings.md` (around line 1551) report the clipped reading at **48.8 %**,
   and D51's text says tier E "takes the same rule". The draft gives only 60.3 %. Suggested:
   "… absorbs about 60 % of K's F1 return (60.3 % unclipped; 48.8 % on the D51 clipped basis)".
6. **+0.0131 against the artefact's 0.013043.** Either print +0.0130 or keep +0.0131 as the
   difference of rounded endpoints (0.7948 → 0.8079). The convention differs from row 4.6's
   +0.0006, which uses unrounded values.
7. **Minor wording.** "no raw value is now recorded" is ambiguous. Suggested: "the regenerated
   tables no longer record a raw value".
8. **Lapse note (not the outcome) stale on the branch head.**
   - It says "(tension/effect-sizes.json is not rebuilt and still records 0.0629)". The file was
     regenerated in `62050794d` and now records 0.06 for MINIMAL image T 0.7.
   - It says "results/k-ladder-2026-09-12/findings.md is not yet restated at 376eb1d50". The
     findings were restated later in `de998a94d`.
   - Both should be updated before the PI approves the note.

## 4.13 `verifier-uplift-pairing`

The sources are `results/uplift-supplement/verifier-uplift.csv` (F1) and `verifier-uplift-mcc.csv` (MCC).

| Draft value | Source | Found | Result |
|---|---|---|---|
| 167 of 170 on tile MCC; three pending | MCC CSV `status` | 167 computed, 3 pending | OK |
| one undefined twin MCC | MCC CSV row `pair::retest-phase2b::verified-adv-text-t0.0` | "unverified side has no score (already-registered; registered)" | OK |
| two 55-map stride A K=10 twins withhold tile MCC | MCC CSV rows `…g384-ov128-55map-n10-oracle-p0.15-k7-{r2,standardised}-gt`; `results/uplift-supplement/verifier-pairing/stride-55map-2026-08-25__g384-ov128-55map-n10-oracle-p0_15-k7-*/evaluation.json` `summary.buffers[*].ci_withheld_reason` | "tile_join_detection_shortfall" (D57 re-score `c2eb1e6bc`) | OK |
| F1 median +0.2562 | F1 CSV, median of `uplift` (170) | 0.256241 | OK |
| range −0.0366 to +0.5232, 3 negative | F1 CSV | −0.0366, 0.5232, 3 | OK |
| MCC median +0.4936 | MCC CSV (167) | 0.493592 | OK |
| MCC range −0.0038 to +0.8410, 1 negative | MCC CSV | −0.0038, 0.841, 1 | OK |
| 55maps-8541 86, +0.369 | F1 CSV `frame_id` median | 0.368534 | OK (the branch point was 0.368491 → 0.368, so the change is real) |
| grid-common-487 21, +0.193 | F1 CSV | 0.1927 | OK |
| (unchanged) era-2-487 51, +0.132 | F1 CSV | 0.1322 | OK |
| (unchanged) era-1-340 5, +0.037; era-3-327 4, +0.005; px256-1032 3, +0.398 | F1 CSV | 0.0366, 0.0047, 0.3983 | OK |
| (unchanged) 170 of 170 F1, 0 blocked | F1 CSV `status` | 170 computed | OK |

Wording:

- **Name the new negative.** The third F1 negative is
  `pair::gemini37-image-gs-2026-09-01::g37-image-k5-verified-carried-p0.10-k5` (−0.0017).
  § 2.5 notes that D65 (4) asked for it to be reported. Suggested: "… range −0.0366 to +0.5232,
  3 negative (the third the 3.7 image carried arm, −0.0017, at its registered point) …".
- "pending" is the CSV status, but here it means "not computable under the current tile join",
  not "scheduled". Optional fix: "three MCC pairs not computed".

## 4.14 `uplift-supplement-flatten`

| Draft value | Source | Found | Result |
|---|---|---|---|
| 505 registered conditions | `results/uplift-supplement/conditions.csv` rows; `build-report.md` line 15 | 505; 505 | OK |
| 505 carry a headline-buffer F1 | `build-report.md` line 18 | 505 | OK |
| 153 board-frame rows excluded | `build-report.md` line 22 | 153 | OK |
| (unchanged) 130 strata | `strata.csv` rows; `build-report.md` changelog "strata 130 -> 130" | 130 | OK |
| (unchanged) headline references r2 (55-map) and curator (GS) | `conditions.csv` (corpus, reference) counts; `build-report.md` changelog | r2 103 rows, curator 353 rows | OK |

Wording (optional): 441 → 505 is mostly membership, not restatement. It adds the 66 conditions
registered since 2026-09-12, and the signed 441 / 79 were already stale at the branch point
(439 / 153; record § 3). The pairing in 4.13 deliberately kept its 170-pair worklist. A
half-sentence would stop readers putting the jump down to re-scoring: "(66 of them registered
since 2026-09-12)".

## 4.15 `null-exemplar-sensitivity-2026-09-13`

| Draft value | Source | Found | Result |
|---|---|---|---|
| restated board 8075 F1 pairs, 14 tiers, Tier 1 of 5 | as 4.11 (`tiering_20m.json`) | 8075, 14, 5 | OK |
| 3001 MCC pairs, 6 MCC tiers, MCC Tier 1 of 34 | as 4.11 | 3001, 6, 34 | OK |
| Hsu MCB 52 (F1) and 60 (tile-MCC) | as 4.11 | 52, 60 | OK |
| 14 of 150 Era-2 cells re-scored (4 image-bearing, 10 text) | the board's `membership.json` `_restated.changed` (field `committed_f1_20`): 17 members, minus the 3 in `tiering_20m.json` `withheld_cells` | 14: 4 image (2 × g37-image, 2 × image-b), 10 text | OK |
| "except the pv-diag-384 restriction" | none of the 14 is pv-diag-384 | — | OK |
| (unchanged) 7961 → 7905 | `results/null-exemplar-sensitivity-2026-09-13/analysis.json`: `era2_tiering.n_pairs_significant_before/after` | 7961, 7905 | OK |
| (unchanged) 2982 → 3118 | `era2_mcc_family.n_significant_before/after` | 2982, 3118 | OK |
| (unchanged) F1 MCB 65 → 66, MCC 59 → 57 | `era2_mcb.f1/mcc.n_admissible_before/after` | 65/66, 59/57 | OK |
| (unchanged) Spearman 0.9989 | `era2_tiering.rank_stability.spearman` | 0.998852 | OK |
| (unchanged) difference −0.0881 | `leak_signature.boards[0].observed_image_minus_text` | −0.088143 | OK |
| (unchanged) 3.7 image cell keeps rank 1 | restated `tiering_20m.json` `ranking[0]` | g37-image swap37, 0.9332 | OK |

The draft qualifies the board figures rather than replacing them, as § 3 intends. No wording
issues beyond the long parenthetical in (3), which reads correctly.

---

## Cross-cutting notes

- **Rounding convention is not uniform across the drafts.** 4.6 uses unrounded differences
  (+0.0006), while 4.12 uses differences of rounded endpoints (+0.0131). The PI may want one
  convention; unrounded matches the artefacts' own `delta` fields.
- **Session jargon.** "S164 restatement pass" appears in 4.2, 4.10 and 4.15. It follows the
  register's existing "S153" convention, but a reader outside the project gets nothing from it.
  Optional: cite the record path once, `reports/s164-agent-records/restatement-pass.md`.
- **Lapse notes cite branch commit hashes** (for example `f6f10d605`, `08af04cf3`, `64382beea`).
  If the PR is squash-merged, those hashes will not resolve from `main`. The drafted outcomes
  themselves cite no branch hashes.
- **Staleness scan.** The drafts contain no "draft", "PR #", "branch", "not yet" or "will be".
  The only "pending" wording is the pre-existing 4.6 clause and the CSV status in 4.13, both
  covered above.

## Unchecked

- Unchanged figures that the pass did not touch and that are not recorded in the artefacts I
  read: 4.6's "~$5.4", "~$0.9" and "276 thinking tokens"; 4.7's I4 / I5 figures; 4.8's "~$3";
  4.9's token counts and spends; 4.12's "170 candidate rows, max abs delta 4.958e-05", the
  instrument cross-check (8 pairs, 0.0006, BH 0.0079 / 0.0655), the tension draws (197 / 200,
  39 / 200, ~0.0114) and the US$24.8065 / US$4.9595 spends.
- The 17-of-23 last-step count in 4.12 on the restated tables (I relied on the PI-approved D25
  note).
- The "nine ladders" clause in 4.12, which I could not reproduce (I count 10).
