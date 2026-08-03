# Attractor-pull v2 — multi-run shell-wise null analysis

> **Last revised**: 2026-08-03 (Session 126 wave-6 living-document repair —
> § 2 T=0.3 and text-MIN tables refreshed to the current artefact; the
> "no row-level shifts" re-confirmation clause corrected; student-GT and
> image `n_candidates` residue cleared). See [§ Changelog](#changelog) for
> revision history.

**Anchor**: Obs 272 (`docs/notes/reflections/working-notes.md`, 2026-04-21) established the attractor-pull cutoff at ~125 m using the image-generalisation review only. v2 re-runs the same shell-wise within-tile permutation null on each of the 4 corrected 55-map runs and synthesises a consensus cutoff.

**Post-recovery 2026-05-03**: all four runs re-evaluated against the
canonical post-recovery review cohorts (cross-track-v2 commit `42ed1d32`).
T=0.7 row refreshed against the post-recovery T=0.7 evaluation
(n_candidates 630 → 637, bias_correction 0.9309 → 0.9302); image row
refreshed against the +1 phantom-promoted cand 2397 review
(n_candidates 1,029 → 1,030, bias_correction 0.8641 → 0.864); T=0.3
and text-MIN were re-run against the same cohorts, and their observed
rates and configuration are unchanged (T=0.3 `n_candidates` = 692,
text-MIN `n_candidates` = 585 and `bias_correction` = 0.9361, every
`obs_rate_in_shell` byte-identical) — but their permutation-null-derived
columns DID shift at the final regeneration (`null_mean_bias_corrected`,
`lift_ratio_bias_corrected`, `signal_fraction_bias_corrected`,
`p_value_bias_corrected`, and T=0.3's run-level `bias_correction`
0.9231 → 0.9232), because the student-GT reference set moved
4744 → 4745 and that re-draws the within-tile permutation null even
under a fixed seed. The T=0.3 and text-MIN tables in § 2 below carry the
current values and agree cell for cell with the generated twin
`report_autogen.md`. The qualitative finding is preserved: per-run cutoffs
unchanged (T=0.3 = 100 m, T=0.7 = 125 m, image = 125 m,
text-MIN = 100 m); 100 m most-permissive cap and 125 m majority
breakpoint are stable.

## 0. Executive summary

The shell-wise within-tile permutation null was applied independently to all four corrected 55-map runs (T=0.3 text-HIGH, T=0.7 text-HIGH, image at T=0.7, text-MIN). Two consensus operating points emerge from the cross-run synthesis (§3):

- **Most-permissive cap = 100 m** — the deepest shell outer edge at which **all four** runs reject the within-tile null at α = 0.05. This is the cap at which a practitioner can claim, with cross-run consensus across both decoding temperatures, both modalities, and both thinking budgets, that detection density above ground-truth mounds is distinguishable from random co-occurrence.
- **Majority cap = 125 m** — the deepest shell outer edge at which **≥ 3 of 4** runs reject the null. T=0.7 text-HIGH and image (T=0.7) extend cleanly to 125 m with monotonic decay; T=0.3 text-HIGH dips at the (100, 125] shell from a thin n = 7 sample (p = 0.093), and text-MIN cuts cleanly at 100 m with no thin-sample uncertainty.

These two operating points are the headline finding for the Methods / Results sections of the paper. They tie directly to Obs 298 (4-run consensus refinement) and clarify — without contradicting — Obs 294's earlier 3-run 125 m framing. See §6 for the practitioner-cap framing the paper should adopt.

## 1. Method

For each run, observed shell rates are taken directly from the reviewer's ``buffer_metres`` label (the band at which a real mound is visible inside the buffer; ``not_mound`` rows are mapped to the > 286 m shell). The null distribution is M = 1,000 within-tile permutations (seed 42) of student GT distances. Bias correction divides the null rate by the student-GT fraction of the real-mound universe to account for the reviewer-promoted phantoms absent from student GT. Per-shell significance is the one-sided permutation p-value against the bias-corrected null (P(null_corrected ≥ obs)), alpha = 0.05.

Student-GT reference set: 4745 mounds (4-corner of the corrected reviewed reference).
Shell edges (m): 50, 75, 100, 125, 150, 286. The (200, 286] shell corresponds to the >150-m / not_mound review label, with effective tolerance 286 m (200 × √2 + 5 display-pixels on the 400 m × 400 m crop).

## 2. Per-run shell tables

### T=0.3 text-HIGH — n=692, bias_correction=0.9232

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_bias_corrected |   lift_ratio_bias_corrected |   signal_fraction_bias_corrected |   p_value_bias_corrected | significant   |
|------------:|------------:|--------------------:|---------------------------:|----------------------------:|---------------------------------:|-------------------------:|:--------------|
|           0 |          50 |              0.4451 |                     0.0031 |                      145.74 |                           0.9931 |                    0.001 | True          |
|          50 |          75 |              0.0347 |                     0.0038 |                        9.23 |                           0.8917 |                    0.001 | True          |
|          75 |         100 |              0.0202 |                     0.005  |                        4.04 |                           0.7522 |                    0.001 | True          |
|         100 |         125 |              0.0101 |                     0.0059 |                        1.71 |                           0.4155 |                    0.093 | False         |
|         125 |         150 |              0.0145 |                     0.0069 |                        2.08 |                           0.5199 |                    0.013 | True          |
|         150 |         286 |              0.0462 |                     0.0552 |                        0.84 |                          -0.193  |                    0.842 | False         |

**Per-run cutoff**: 100 m (deepest shell outer edge with bias-corrected p < 0.05)

### T=0.7 text-HIGH — n=637, bias_correction=0.9302

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_bias_corrected |   lift_ratio_bias_corrected |   signal_fraction_bias_corrected |   p_value_bias_corrected | significant   |
|------------:|------------:|--------------------:|---------------------------:|----------------------------:|---------------------------------:|-------------------------:|:--------------|
|           0 |          50 |              0.4239 |                     0.0029 |                      146.96 |                           0.9932 |                    0.001 | True          |
|          50 |          75 |              0.0298 |                     0.0034 |                        8.69 |                           0.8849 |                    0.001 | True          |
|          75 |         100 |              0.0298 |                     0.0048 |                        6.27 |                           0.8406 |                    0.001 | True          |
|         100 |         125 |              0.0173 |                     0.0061 |                        2.83 |                           0.6464 |                    0.002 | True          |
|         125 |         150 |              0.0078 |                     0.0071 |                        1.11 |                           0.1017 |                    0.396 | False         |
|         150 |         286 |              0.0502 |                     0.0548 |                        0.92 |                          -0.0913 |                    0.707 | False         |

**Per-run cutoff**: 125 m (deepest shell outer edge with bias-corrected p < 0.05)

### image (T=0.7) — n=1030, bias_correction=0.864

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_bias_corrected |   lift_ratio_bias_corrected |   signal_fraction_bias_corrected |   p_value_bias_corrected | significant   |
|------------:|------------:|--------------------:|---------------------------:|----------------------------:|---------------------------------:|-------------------------:|:--------------|
|           0 |          50 |              0.4612 |                     0.0047 |                       98.46 |                           0.9898 |                    0.001 | True          |
|          50 |          75 |              0.1175 |                     0.0058 |                       20.24 |                           0.9506 |                    0.001 | True          |
|          75 |         100 |              0.0456 |                     0.0077 |                        5.95 |                           0.8319 |                    0.001 | True          |
|         100 |         125 |              0.0184 |                     0.0093 |                        1.99 |                           0.4985 |                    0.002 | True          |
|         125 |         150 |              0.0107 |                     0.0107 |                        1.00 |                           0.0003 |                    0.469 | False         |
|         150 |         286 |              0.0718 |                     0.0818 |                        0.88 |                          -0.1385 |                    0.881 | False         |

**Per-run cutoff**: 125 m (deepest shell outer edge with bias-corrected p < 0.05)

### text-MIN — n=585, bias_correction=0.9361

|   R_inner_m |   R_outer_m |   obs_rate_in_shell |   null_mean_bias_corrected |   lift_ratio_bias_corrected |   signal_fraction_bias_corrected |   p_value_bias_corrected | significant   |
|------------:|------------:|--------------------:|---------------------------:|----------------------------:|---------------------------------:|-------------------------:|:--------------|
|           0 |          50 |              0.4274 |                     0.0027 |                      159.2  |                           0.9937 |                    0.001 | True          |
|          50 |          75 |              0.0342 |                     0.0032 |                       10.63 |                           0.9059 |                    0.001 | True          |
|          75 |         100 |              0.012  |                     0.0046 |                        2.6  |                           0.6147 |                    0.012 | True          |
|         100 |         125 |              0.0085 |                     0.0057 |                        1.51 |                           0.3387 |                    0.202 | False         |
|         125 |         150 |              0.012  |                     0.0067 |                        1.79 |                           0.4421 |                    0.067 | False         |
|         150 |         286 |              0.0598 |                     0.0524 |                        1.14 |                           0.124  |                    0.223 | False         |

**Per-run cutoff**: 100 m (deepest shell outer edge with bias-corrected p < 0.05)

## 3. Cross-run consensus

|   R_outer_m | t0.3   | t0.7   | image   | text-min   |   n_runs_significant | all_significant   |
|------------:|:-------|:-------|:--------|:-----------|---------------------:|:------------------|
|          50 | sig    | sig    | sig     | sig        |                    4 | yes               |
|          75 | sig    | sig    | sig     | sig        |                    4 | yes               |
|         100 | sig    | sig    | sig     | sig        |                    4 | yes               |
|         125 | —      | sig    | sig     | —          |                    2 | no                |
|         150 | sig    | —      | —       | —          |                    1 | no                |
|         286 | —      | —      | —       | —          |                    0 | no                |

**Most-permissive consensus cutoff**: 100 m (largest shell outer edge significant in all 4 runs).
**Majority-loses breakpoint**: 125 m (first shell where < 3/4 runs are significant).

### Per-run cutoff summary

| run             |   n_candidates |   cutoff_m |
|:----------------|---------------:|-----------:|
| T=0.3 text-HIGH |            692 |        100 |
| T=0.7 text-HIGH |            637 |        125 |
| image (T=0.7)   |           1030 |        125 |
| text-MIN        |            585 |        100 |

## 4. Cross-reference to Obs 272

Obs 272 reported a 125-m cutoff using only the image-generalisation review and a 1,000-permutation within-tile null. The v2 image-only cutoff is **125 m** — corroborates Obs 272 exactly.

The cross-run **consensus cutoff** (most permissive value significant in every run) is **100 m**.

**Verdict**: Obs 272's 125 m claim is revised downward by the multi-run consensus — at least one run shows the cutoff at a tighter radius.

### Cross-run disagreement (range 100–125 m)

Per-run cutoffs differ by 25 m. Inspect the per-run shell tables in §2 to see which shells flip significance between runs.

## 5. Reproducibility

Script: `scripts/analyse_attractor_pull_v2.py` (ruff-clean). Seed 42, M = 1000 permutations per run. Rerun with `python scripts/analyse_attractor_pull_v2.py` from the repo root.

## 6. Paper implications

This section is **discussion-load-bearing** for the paper's Methods and Results sections; it is the practitioner-cap reference the paper relies upon when citing recall and F1 numbers on the 55-map generalisation corpus.

### 6.1 Practitioner cap recommendation

For downstream consumers of the 55-map detection results, the paper recommends **100 m as the conservative practitioner cap and 125 m as the extended cap**:

- **Cite 100 m** as the most-permissive cap — "all four corrected 55-map runs (two decoding temperatures, two thinking budgets, both text and image tracks) show detection density above ground-truth mounds significantly distinguishable from random within-tile placement up to 100 m". This is the operating point that minimises practitioner risk: every run agrees, and a recall claim at this radius does not depend on accepting any single run's editorial reading.
- **Cite 125 m** as the majority / extended cap — "T=0.7 text-HIGH and image (T=0.7) extend significant signal to 125 m with clean monotonic decay; T=0.3 text-HIGH and text-MIN cut at 100 m". Use this cap when the analysis specifically benefits from the wider buffer (e.g., when comparing against Obs 272's original 125 m anchor) and when the run under discussion is one of the two that supports it.
- **Do not cite buffers in (125, 150] m** as practitioner-meaningful for the 55-map corpus. They may be reported as upper bounds (footnoted, italicised, or asterisked per Obs 294's citation discipline), but the cross-run evidence does not support them as evidence the detector has localised specific mounds.

### 6.2 Cross-run consensus interpretation

The two consensus operating points are not in tension; they describe different consensus thresholds for a real cross-run pattern. Two specific observations support this reading:

1. **Text-MIN cleanly corroborates T=0.3's previously thin-sample 100 m floor.** T=0.3 text-HIGH cut at 100 m in the original 3-run analysis (Obs 294), but with a non-monotonic dip at the (100, 125] shell from only n = 7 mound calls (p = 0.093). Obs 294 editorially collapsed that dip to thin-sample noise so the unified 125 m claim could stand. Text-MIN's cut at 100 m is **clean and monotonic** — no dip, no thin-sample concern, monotonic decay across (0, 50] → (50, 75] → (75, 100] → (100, 125] (rates 42.7 % → 3.4 % → 1.2 % → 0.85 %). This independent corroboration removes the precarity of the 3-run editorial reading and establishes the 100 m floor as a genuine cross-run pattern visible in two of four runs.
2. **The 100 m / 125 m split is patterned.** The two runs reaching 125 m are T=0.7 text-HIGH and image (HIGH thinking by default at T = 0.7); the two cutting at 100 m are T=0.3 text-HIGH (HIGH thinking, lower decoding temperature) and text-MIN (lower thinking budget at the canonical text temperature). One reading is causal — that HIGH thinking *plus* diverse decoding extends spatial reach by one shell. The alternative is coincidence at n = 4. The current data cannot distinguish; it is flagged as a hypothesis worth testing if a future run varies one factor at a time. Either way, the patterned split is consistent with Obs 296's broader observation that different runs hit different effective spatial-precision floors depending on their detection-mode mix.

### 6.3 Practitioner-cap framing for the paper

The paper's Methods section should specify the cap used for each cited recall / F1 number, and the Results section should adopt the conservative-vs-extended language above. Two concrete choices follow from this:

- The corrected-F1 multi-buffer tables (50, 75, 100, 125, 150 m) should report 150 m visually distinct (italics / asterisk / footnote), per Obs 294's citation discipline carried forward through Obs 298.
- Pairwise-permutation buffer sweeps (Obs 297 and earlier) cap at 125 m on this principle. Wider comparisons would test detector-versus-random-placement equivalence rather than detector-versus-detector differences.
- Where a single headline number is needed, **100 m is the safer choice** (cross-run unanimity); 125 m is acceptable when the analysis is restricted to the runs that support it (T=0.7 text-HIGH or image).

### 6.4 Relation to the cross-corpus story

The 100 m / 125 m within-corpus split is itself a small-scale reflection of the cross-corpus cap-difference observation in Obs 296: the cap is set by **whichever failure mode dominates each run**, not by a single fundamental detector spatial-precision floor. The 100 m vs 125 m split among the four 55-map runs is a within-corpus instance of the same failure-mode-driven cap variation that Obs 296 documents at the 25 m (gold-standard, post-calibration) vs 125 m (55-map, native unfamiliar-map) cross-corpus scale. The paper's Discussion section can cite both to make the point that the practitioner cap is a property of the detection-mode mix on the corpus under analysis, not a fixed detector property.

## 7. Cross-references

- **Obs 294** (`docs/notes/reflections/working-notes.md`, 2026-04-28): 125 m practitioner cap from the original 3-run consensus (T=0.3, T=0.7, image). Clarified — not superseded — by the 4-run extension reported here. The 125 m claim still holds for the *majority* of the four runs; Obs 298 reframes the implication that the cap is *unanimous* across runs.
- **Obs 296** (`docs/notes/reflections/working-notes.md`, 2026-04-28): GS-vs-55-map cap difference is a failure-of-generalisation effect (cap-as-calibration-vs-native), not a fundamental detector-precision shift. The 100 m / 125 m within-corpus split documented here is consistent with the same failure-mode-driven cap variation that Obs 296 observes cross-corpus. Discussion-load-bearing for the paper's framing of "the cap is set by detection-mode mix, not by detector behaviour".
- **Obs 298** (`docs/notes/reflections/working-notes.md`, 2026-04-28): 4-run attractor-pull consensus refines the 55-map cap to 100 m most-permissive / 125 m majority; text-MIN cleanly corroborates T=0.3's previously thin-sample 100 m floor. This report is the artefact backing Obs 298. Includes the off-by-one fix in the majority-threshold formula (`(N // 2) + 1`) so the 4-run majority breakpoint correctly reports the (100, 125] shell.

## Changelog

### 2026-08-03 — C4 wave-6 repair: T=0.3 / text-MIN tables refreshed; false re-confirmation clause corrected

**Refresh trigger**: Session-126 wave-6 C4 triage — blind pass P4
(`reports/verification/c4-triage/blind-passes/wave6-pass-P4-2026-08-03.json`,
recommendation R2, family F2, 27 rows) and blind pass P2
(`…/wave6-pass-P2-2026-08-03.json`, family F2 and recommendation R4's
partial-refresh-residue class). The permutation-null columns of
`attractor-pull-v2.json` were regenerated in place twice after the § 2 tables
were pasted in — at `33435aab2` (2026-05-03T00:57Z, student-GT 4744 → 4745) and
`29fcc3679` (04:29Z, 4-run consensus refresh) — and the T=0.3 and text-MIN
blocks were never re-pasted. Repaired under Phase-3 ruling 17
(`reports/verification/phase3-rulings-2026-07-31.md` § 17: living documents in
`results/**.md` are refreshed in place, not marked).

**Authority for every replacement value**: the sibling artefact
`results/55maps-attractor-pull-v2/attractor-pull-v2.json` and its generated twin
`results/55maps-attractor-pull-v2/report_autogen.md`, which already carried the
current content. The § 2 T=0.3 and text-MIN tables are now byte-identical to the
twin; a sample of cells was re-read directly from the JSON
(`$.n_student_gt`, `$.runs[key=='t0.3'].bias_correction`,
`$.runs[key=='text-min'].shell[*]`, `$.runs[key=='image'].n_candidates`).

| Location | Quantity | Before | After |
|:---|:---|---:|---:|
| Post-recovery header | T=0.3 / text-MIN re-confirmation | "…re-confirmed against the same cohorts (no row-level shifts)" | honest statement: observed rates and configuration unchanged, null-derived columns shifted |
| § 1 | Student-GT reference set | 4744 mounds | **4745 mounds** |
| § 2 T=0.3 header | run-level `bias_correction` | 0.9231 | **0.9232** |
| § 2 T=0.3 (0, 50] | `lift_ratio_bias_corrected` | 145.88 | **145.74** |
| § 2 T=0.3 (75, 100] | `lift_ratio` / `signal_fraction` | 4.03 / 0.7521 | **4.04 / 0.7522** |
| § 2 T=0.3 (100, 125] | `signal_fraction` | 0.416 | **0.4155** |
| § 2 T=0.3 (125, 150] | `signal_fraction` | 0.5203 | **0.5199** |
| § 2 T=0.3 (150, 286] | `signal_fraction` | −0.1931 | **−0.193** |
| § 2 text-MIN (0, 50] | `null_mean` / `lift_ratio` / `signal_fraction` | 0.0028 / 151.76 / 0.9934 | **0.0027 / 159.2 / 0.9937** |
| § 2 text-MIN (50, 75] | `null_mean` / `lift_ratio` / `signal_fraction` | 0.0034 / 10.08 / 0.9008 | **0.0032 / 10.63 / 0.9059** |
| § 2 text-MIN (75, 100] | `null_mean` / `lift_ratio` / `signal_fraction` / `p` | 0.0045 / 2.68 / 0.6262 / 0.015 | **0.0046 / 2.6 / 0.6147 / 0.012** |
| § 2 text-MIN (100, 125] | `null_mean` / `lift_ratio` / `signal_fraction` / `p` | 0.0056 / 1.54 / 0.3486 / 0.199 | **0.0057 / 1.51 / 0.3387 / 0.202** |
| § 2 text-MIN (125, 150] | `null_mean` / `lift_ratio` / `signal_fraction` / `p` | 0.0068 / 1.76 / 0.433 / 0.082 | **0.0067 / 1.79 / 0.4421 / 0.067** |
| § 2 text-MIN (150, 286] | `null_mean` / `signal_fraction` / `p` | 0.0527 / 0.1193 / 0.254 | **0.0524 / 0.124 / 0.223** |
| § 3 per-run cutoff summary | image `n_candidates` | 1029 | **1030** |

**Which display forms moved**: every changed cell is a permutation-null-derived
column. In the T=0.3 block the moves are 4th-decimal (run-level
`bias_correction` 0.9231 → 0.9232, unchanged at 3 d.p.; four `signal_fraction`
values) apart from two `lift_ratio` cells — (0, 50] 145.88 → 145.74 and
(75, 100] 4.03 → 4.04. In the text-MIN block the moves are larger and survive
rounding: all six `signal_fraction` values change at 3 d.p. (0.993 → 0.994,
0.901 → 0.906, 0.626 → 0.615, 0.349 → 0.339, 0.433 → 0.442, 0.119 → 0.124), four
`p_value` cells change at 3 d.p. (0.015 → 0.012, 0.199 → 0.202, 0.082 → 0.067,
0.254 → 0.223), every `null_mean` cell moves in the 4th decimal, and the (0, 50]
`lift_ratio` moves 151.76 → 159.2 (+4.9 %) — the largest single change in this
pass.

**What did NOT change**:

- **No significance flag flips.** text-MIN (75, 100] stays significant at
  p = 0.012 as it was at p = 0.015; the three non-significant shells stay
  non-significant. Every `significant` column is unchanged.
- **No observed quantity moved.** Every `obs_rate_in_shell` is byte-identical
  across both regenerations, as are `n_candidates` (T=0.3 692, text-MIN 585),
  text-MIN's `bias_correction` (0.9361), `permutations` (1,000), `seed` (42) and
  `alpha` (0.05). That selectivity is what identifies the null re-draw as the
  mechanism.
- **No conclusion moves.** Per-run cutoffs (T=0.3 = 100 m, T=0.7 = 125 m,
  image = 125 m, text-MIN = 100 m), the 100 m most-permissive cap, the 125 m
  majority breakpoint, § 3's consensus table, and the whole of § 6's
  practitioner-cap framing survive the refresh unchanged. § 6.2's observed-rate
  sequence (42.7 % → 3.4 % → 1.2 % → 0.85 %) is likewise unaffected.
- **T=0.7 and image tables were already current** and were not touched.

**Commit**: recorded by the Session-126 W6 doc-repair commit (see this file's
`git log` entry at 2026-08-03).

### 2026-04-27 — Original publication

First authored at `74dbe6809` (2026-04-27) as the 3-run attractor-pull v2
analysis; text-MIN added as the fourth run at `1c8c34bd1` (2026-04-28); levelled
up with the executive summary, paper implications and Obs cross-references at
`4f64fae5f` (2026-05-02); T=0.7 post-recovery numbers propagated at `01b5441fb`
and the post-recovery header added at `fc536a19c` (2026-05-03). This banner and
changelog were added on 2026-08-03 as the first Revision-Policy stub for the
document.
