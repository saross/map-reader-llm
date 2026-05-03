# Corrected F1 / P / R on the 55-map image set — buffer-stratified

**Original analysis timestamp**: 2026-04-21T09:19:22.660216+00:00.
**Level-up**: 2026-04-24 (Session 76).
**Methodology**: Approach B — extended-GT-at-R Hungarian matching.
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling.
**Git commit of original data run**: `508f76989e0c8739469950bfca415719b6712c83`.

**Observation anchors**: Obs 267 (corrected-F1 headline), Obs 272 (attractor-pull scale ends at ~125 m), Obs 263 + Obs 268 (review-UI calibration). Direct input to meta-findings Theme T1.

**Companion auto-generated file**: `report_autogen.md` in this directory holds the script's raw output. This `report.md` is the paper-citation source; re-running the script does NOT overwrite it (script hardened 2026-04-24 Session 76; see §9 Reproducibility).

**Sibling single-buffer artefact**: `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md` is the analytic-adjustment variant using yesterday-only review (472 phantoms; F1 = 0.8295 at 50 m). This multi-buffer artefact re-runs Hungarian against extended GT at each R ∈ {50, 75, 100, 125, 150} m using yesterday + today review (474 phantoms at 50 m; F1 = 0.8317 at 50 m). Both round to the paper-citable ≥ 0.830 headline.

## 1. Executive summary

The 55-map image-generalisation corrected-F1 curve, computed via Approach B (extended-GT-at-R Hungarian re-matching with reviewer-promoted phantoms added at each buffer), traces from F1 = 0.8317 at 50 m up to F1 = 0.8551 at 150 m in five discrete buffer steps. **The practitioner-useful ceiling is F1 = 0.8538 at R = 125 m** — the largest buffer at which the attractor-pull contribution to recall is statistically distinguishable from within-tile random placement (Obs 272; p = 0.002 at the 100–125 m shell vs p = 0.381 at the 125–150 m shell).

**Headline numbers**:

- **F1 curve** (50 → 75 → 100 → 125 → 150 m): **0.8317 → 0.8477 → 0.8521 → 0.8538 → 0.8551**.
- **Practitioner-useful cap**: F1 = **0.8538** at R = 125 m (CI [0.8453, 0.8620]).
- **Paper lower-bound headline** at 50 m: F1 = **0.8317** [0.8225, 0.8407]; P = 0.8810, R = 0.7877.
- **Upper-bound-only 150 m row**: F1 = 0.8551 [0.8466, 0.8632] — **not practitioner-useful**, flagged because the 125–150 m shell admits mounds indistinguishable from random within-tile co-occurrences.
- **Sentinel exclusion**: 74 candidates at today's `> 150 m` shell (`buffer_metres = 200`) are excluded from the extended-GT build at every R; their detections contribute FP at every R ≤ 150 m (correct behaviour under the 125 m practitioner cap).
- **Reconciliation with `buffer-100m-diagnostics/report.md`**: this pipeline gives TP = 4,110 at 50 m; the diagnostic gives 4,108. The 2-pair gap is a methodological GT-input difference (this pipeline adds 2 candidates from today's multi-buffer re-review), not a bug in either (Step 6 backlog entry S6.1 RESOLVED 2026-04-24).

**One-line paper claim**: "The 55-map image-generalisation corrected F1 runs from 0.832 at 50 m to 0.855 at 150 m; the practitioner-useful ceiling, at the largest buffer where attractor-pull is statistically distinguishable from within-tile random placement (Obs 272), is **F1 = 0.854 at 125 m** [0.8453, 0.8620]."

## 2. F1 curve

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 50 | 4110 | 555 | 1108 | 4744 | 474 | 5218 | 0.8810 [0.8710, 0.8904] | 0.7877 [0.7750, 0.8000] | **0.8317** [0.8225, 0.8407] |
| 75 | 4240 | 425 | 1099 | 4744 | 595 | 5339 | 0.9089 [0.8999, 0.9173] | 0.7942 [0.7818, 0.8060] | **0.8477** [0.8388, 0.8560] |
| 100 | 4282 | 383 | 1104 | 4744 | 642 | 5386 | 0.9179 [0.9093, 0.9259] | 0.7950 [0.7828, 0.8069] | **0.8521** [0.8434, 0.8602] |
| 125 | 4299 | 366 | 1106 | 4744 | 661 | 5405 | 0.9215 [0.9131, 0.9294] | 0.7954 [0.7832, 0.8073] | **0.8538** [0.8453, 0.8620] |
| 150 | 4310 | 355 | 1106 | 4744 | 672 | 5416 | 0.9239 [0.9155, 0.9317] | 0.7958 [0.7836, 0.8077] | **0.8551** [0.8466, 0.8632] |

## 3. How to read this table

- **TP / FP / FN**: Hungarian-matching counts against the extended GT at R. Every reviewer-promoted phantom within R is added to the GT before matching.
- **n_ref_student**: Student GT points scoped to the evaluation tile bounds (the denominator without any human-review correction).
- **n_promoted@R**: Number of reviewer-promoted phantoms included in the extended GT at this R. Yesterday's 472 mound labels appear at every R ≥ 50. Today's shell-stratified mound labels accumulate as R rises: +2 @ 50 m, +121 @ 75 m, +47 @ 100 m, +19 @ 125 m, +11 @ 150 m.
- **n_ref_extended**: Scoped extended-GT count at R (student GT scoped ∪ in-scope phantoms at R). This is the recall denominator.
- **F1 [95 % CI]**: Corrected F1 at R with tile-level bootstrap CI.

## 4. Comparison to yesterday's 50 m result

Yesterday's single-buffer correction (`compute_corrected_f1_human_reviewed.py`) produced **F1 = 0.8295** at R = 50 m via an analytic adjustment to measured counts (moved 472 FPs into TP and added them to the GT denominator, without re-running Hungarian). This script's R = 50 m row (**F1 = 0.8317**) re-runs Hungarian over extended GT including the 2 today-corrections at 50 m. Expected ΔF1 ≈ +0.003 versus yesterday's number. The two numbers are methodologically close but not identical — Approach B allows detections to rematch optimally against the extended GT, which can free a detection previously bound to a distant student-GT point to pair with a closer phantom.

Both round to the paper-citation **≥ 0.830** headline; the multi-buffer figure is the paper-preferred value because it uses the later multi-buffer re-review labels.

## 5. Obs 272 caveat — the 150 m row is an upper bound

Obs 272 in `docs/notes/reflections/working-notes.md` shows the attractor-pull effect (reviewer confirmations concentrating closer to the detection than a uniform within-tile null would predict) is statistically significant only through 125 m. At the (125, 150] shell the shell-specific mound-confirmation rate is indistinguishable from the within-tile random-placement null (p = 0.381), and the (150, 286] shell (the "200 m" sentinel in today's CSV) is completely indistinguishable (p = 0.433).

**Implication for interpretation**:

- **R ≤ 125 m**: corrected F1 / P / R are practitioner-meaningful. The reviewer-promoted phantoms in these shells are confirming detections genuinely spatially associated with visible mound symbols.
- **R = 150 m**: corrected F1 at 150 m is an **upper bound on achievable practitioner recall**, not a practitioner-useful operating point. Including the 11 mounds in the (125, 150] shell inflates recall in a way the attractor-pull null cannot distinguish from coincidental alignment.
- **R > 150 m (excluded from this analysis)**: the 74 candidates at the `> 150 m` sentinel (`buffer_metres = 200`) are visible mounds inside the 286 m corners-plus-5 px review circle but outside every review ring. They are **not** added as phantoms at any R in this analysis; their detections appear as FP at every R ≤ 150 m, which is the correct behaviour under the 150 m practitioner cap.

## 6. Practitioner-useful cap: F1 at R = 125 m

Recommended single-number summary for downstream quotation: **F1 = 0.8538 at R = 125 m (95 % CI [0.8453, 0.8620])** — the largest R where the attractor-pull contribution to recall is statistically distinguishable from within-tile random placement. The 150 m row (0.8551) is a strict upper bound; the 50 m row (0.8317) is the conservative lower bound and matches the paper-citable ≥ 0.830 headline.

## 7. Sentinel exclusion

74 candidates at today's `> 150 m` shell (`buffer_metres = 200`) are excluded from every extended-GT build in this analysis. Their detections contribute FP at every R ≤ 150 m. Rationale: these detections sit inside the 286 m corners-plus-5 px review circle but outside every review ring, so no phantom promotion is warranted within the 150 m practitioner cap (Obs 272). See `buffer-band-lift/report.md` §7 for the full attractor-pull-cap derivation.

## 8. Reconciling with the buffer-100m diagnostic

The sibling `results/55maps-image-generalisation/buffer-100m-diagnostics/report.md` reports `total_matched_at_50m = 4,108`, while this pipeline reports TP = 4,110 at 50 m. The 2-pair gap is a **methodological difference in the ground-truth inputs**, not a bug in either pipeline:

- **This corrected-F1 pipeline** uses both yesterday's single-buffer review (`human-review.csv`, 472 mounds at 50 m) and today's multi-buffer re-review (`human-review-multi-buffer.csv`, 2 additional mounds specifically confirmed at the 50 m shell during the staggered re-review — candidate IDs 5641 (map K-35-075-4) and 5777 (map K-35-076-1)). Total: 474 phantoms at 50 m.
- **The diagnostic** uses only yesterday's review (472 phantoms at 50 m) with the same Hungarian one-to-one matching.

**This pipeline's 4,110 is the paper-citable count**; it underpins the canonical corrected-F1 headline of 0.832 at 50 m. The diagnostic's 4,108 is descriptive only, citable for the 50 → 100 m recall-gain decomposition (71 new matches admitted at 100 m, 0 lost) but not as a stand-alone TP headline. Step 6 backlog entry S6.1 was resolved 2026-04-24 with reconciliation notes added to both reports in commit `783f37c2`.

## 9. Caveats / risk register

1. **150 m row is NOT practitioner-useful** (§5). The 0.8551 F1 at R = 150 m includes 11 mounds in the statistically-indistinguishable-from-random (125, 150] shell. Paper text must cite the 125 m row (0.8538) as the practitioner-useful cap; 150 m is reportable as an upper bound only.
2. **Lower-bound framing** (§4, §6): the 0.8317 at 50 m is the paper-citable lower bound under the conservative reviewer policy (Obs 263 + Obs 268; 21.4 % one-directional flip rate confirming reviewer defaulting to not-mound). A more-permissive reviewer policy would raise the floor.
3. **Per-map F1 not reported**: this artefact is buffer-stratified only; no per-map breakdown (consistent with the single-buffer sibling). Sample size per map would be small and per-sheet CIs noisy.
4. **Bootstrap resamples tiles, not reviewer labels**: the 10,000-iteration bootstrap here resamples at the tile level (standard pipeline bootstrap), capturing matching variability across the 55-map corpus. The reviewer-label bootstrap variance is already baked into the phantoms via yesterday + today review; the two uncertainty sources are not commensurable (same caveat as the single-buffer sibling §4 Caveat 3).
5. **Extended-GT methodology is Approach B**: extended GT includes reviewer-promoted phantoms at each R. Approach A (analytic adjustment without re-running Hungarian) is the single-buffer sibling's methodology. Approach B's Hungarian re-matching is the preferred methodology at buffer > 50 m because it allows detections to rematch against closer phantoms.
6. **Level-up did not re-run the analysis**. All numbers in §2 were lifted verbatim from `report_autogen.md`.

## 10. Paper implications

### 10.1 Paper-citable headline numbers (per-buffer)

- **Conservative lower bound**: F1 = 0.8317 at 50 m (within-band pull; 474 phantoms from yesterday + today review).
- **Practitioner-useful cap**: F1 = 0.8538 at 125 m (largest buffer with significant attractor-pull signal; Obs 272).
- **Upper bound, caveated**: F1 = 0.8551 at 150 m (admits statistically-indistinguishable-from-random shell mounds; use with explicit Obs 272 caveat).

All three cite this artefact. The Results section should lead with 0.8317 @ 50 m as the conservative headline, then state the 125 m practitioner cap, then optionally note the 150 m upper bound with caveat.

### 10.2 Precision monotonicity is a methodological finding

Precision rises monotonically from 0.8810 at 50 m to 0.9239 at 150 m — a 4.3-percentage-point gain driven by the FP count dropping from 555 to 355 as the reviewer-promoted phantom pool expands. Recall is nearly flat (0.7877 → 0.7958). The F1 curve's rise is almost entirely precision-driven. This is a useful methodological data point: Approach B's phantom-promotion mostly converts existing FPs to TPs rather than adding new TPs via re-matching; the recall headroom is small.

### 10.3 Suggested paper text (Results — corrected-F1 multi-buffer)

> Applying a buffer-stratified corrected-F1 methodology (Approach B: extended-GT Hungarian re-matching with reviewer-promoted phantoms added at each R) to the 55-map image-generalisation corpus yields the F1 curve 0.8317 → 0.8477 → 0.8521 → 0.8538 → 0.8551 at R ∈ {50, 75, 100, 125, 150} m (95 % bootstrap CIs in Table [multi-buffer]; 10,000 iterations, seed 42, tile-level resampling). The practitioner-useful cap is **F1 = 0.8538 at R = 125 m**, the largest buffer at which the attractor-pull contribution to recall is statistically distinguishable from within-tile random placement (Obs 272; shell permutation p = 0.002 at 100–125 m vs p = 0.381 at 125–150 m). The 150 m row is reported as an upper bound under the Obs 272 caveat; the 50 m row is the conservative lower bound. Precision rises monotonically from 0.8810 at 50 m to 0.9239 at 150 m, primarily by converting existing FPs to TPs as the reviewer-promoted phantom pool expands; recall is nearly flat (0.7877 → 0.7958). 74 candidates at the `> 150 m` sentinel shell are excluded from the extended-GT build at every R and appear as FP throughout, consistent with the 125 m practitioner cap.

## 11. Files manifest

**Outputs (this directory)**:

- `report.md` — this report (hand-authored, paper-citation source).
- `report_autogen.md` — script-authored sibling.
- `corrected-f1.csv` — §2 table data.
- `summary.json` — machine-readable summary + full bootstrap CIs.

**Inputs**:

- `outputs/55maps-image-generalisation/verified/verified_detections.geojson` — VLM detections post-verifier.
- `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` — student GT (4,744 mounds).
- `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` — 55-map evaluation bounds (8,541 tiles).
- `results/55maps-image-generalisation/human-review.csv` — yesterday's review (472 mounds at 50 m).
- `results/55maps-image-generalisation/human-review-multi-buffer.csv` — today's multi-buffer re-review (+274 mounds across shells).

## 12. Reproducibility

- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`. Writes `corrected-f1.csv` + `summary.json` + `report_autogen.md` in the output directory.
- **Guardrail (Session 75 item 6 / Session 76 carry-over)**: script hardened 2026-04-24 to redirect Markdown output from `report.md` to `report_autogen.md`, protecting this hand-authored level-up against dry-run overwrite.
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling (configurable via CLI).
- **Re-run command**:

    ```bash
    python scripts/compute_corrected_f1_multi_buffer.py \
        --detections outputs/55maps-image-generalisation/verified/verified_detections.geojson \
        --student-gt inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
        --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
        --review-yesterday results/55maps-image-generalisation/human-review.csv \
        --review-today results/55maps-image-generalisation/human-review-multi-buffer.csv \
        --out results/55maps-image-generalisation/corrected-f1-multi-buffer
    ```

- **Git commit of original data run**: `508f7698` (shortened from `508f76989e0c8739469950bfca415719b6712c83`). Level-up commit: see this file's `git log` entry at 2026-04-24.
- **Toolchain**: Python ≥ 3.11, GeoPandas ≥ 0.14, NumPy, pandas, scipy (for Hungarian). Pinned versions in `requirements.txt`.
