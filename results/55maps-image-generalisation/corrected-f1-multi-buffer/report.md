# Corrected F1 / P / R on the 55-map image set — buffer-stratified

> **Last revised**: 2026-08-04 (W6-E9 resolved — coincidence de-dup landed in
> `build_extended_gt` and the artefact regenerated from the tracked HEAD
> student GT; every metric identical, channel accounting corrected). See
> [§ Changelog](#changelog) for revision history.

**Original analysis timestamp**: 2026-04-21T09:19:22.660216+00:00.
**Level-up**: 2026-04-24 (Session 76).
**Post-recovery refresh**: 2026-05-03 (image-recovery propagation —
commit `da84a3d2`).
**Cand-2397 re-run**: 2026-08-03T12:34:34Z (Session 126, W6-E8) — the § 2
table now genuinely includes the cand 2397 review entry (`c816d4bd4`).
**Methodology**: Approach B — extended-GT-at-R Hungarian matching.
**Bootstrap**: 10,000 iterations, seed 42, tile-level resampling.
**Git commit of original data run**: `508f76989e0c8739469950bfca415719b6712c83`.

> **Provenance banner (current state)** — the § 2 F1 curve and § 1
> headline numbers reflect the 2026-08-03 re-run at repo commit
> `a6a18b3c4`, which supersedes the 2026-05-03 post-recovery state.
> Two upstream changes stack into the current numbers:
>
> 1. **Image-generalisation recovery** (commits `2992056b..8699f456`)
>    added 1 new consensus candidate plus 18 pre-existing missing-from-
>    verifier candidates (+15 net to retained verified detections;
>    4,665 → 4,680). This lifted the 50 m headline from F1 = 0.8317
>    (pre-recovery) to F1 = 0.8332 — a **+0.0015** delta.
> 2. **Cand 2397 review entry** (`c816d4bd4`, 2026-05-03T04:13Z) landed
>    88 minutes *after* the post-recovery artefact was written at
>    `8699f456b` (02:45Z), so it was **absent** from that artefact
>    despite being claimed as included. The 2026-08-03 re-run adds it:
>    F1 = 0.8332 → **0.8333** at 50 m, a further **+0.0001**.
>
> Total movement across both: 0.8317 → 0.8333, **+0.0016**. On
> 2026-08-04 the artefact was regenerated through `build_extended_gt`'s
> coincidence de-duplication (`1de559119`) from the tracked HEAD student
> GT (`30a902f56`): **no metric moved**; the channel accounting now
> counts the cand-2397 rescue once, on the student side
> (`n_ref_student_only` 4,746, `n_reviewer_promoted_at_R` −1 at every R,
> `n_phantom_duplicates_dropped` = 1). The auto-regenerated sibling
> `report_autogen.md` is at the same state. Superseded artefacts are
> preserved as the `*.pre-dedup-rerun-20260804T000000.backup`,
> `*.pre-cand2397-rerun-20260803T123434.backup` (post-recovery,
> pre-2397), and `*.pre-recovery-20260503T023134.backup` (pre-recovery)
> siblings.

**Observation anchors**: Obs 267 (corrected-F1 headline), Obs 272 (attractor-pull scale ends at ~125 m), Obs 263 + Obs 268 (review-UI calibration). Direct input to meta-findings Theme T1.

**Companion auto-generated file**: `report_autogen.md` in this directory holds the script's raw output. This `report.md` is the paper-citation source; re-running the script does NOT overwrite it (script hardened 2026-04-24 Session 76; see §9 Reproducibility).

**Sibling single-buffer artefact**: `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.md` is the analytic-adjustment variant using yesterday-only review (472 phantoms; F1 = 0.8295 at 50 m). This multi-buffer artefact re-runs Hungarian against extended GT at each R ∈ {50, 75, 100, 125, 150} m using yesterday + today review (474 phantoms entering at 50 m post de-dup; F1 = 0.8333 at 50 m). Both round to the paper-citable ≥ 0.830 headline.

## 1. Executive summary

The 55-map image-generalisation corrected-F1 curve (2026-08-03 re-run), computed via Approach B (extended-GT-at-R Hungarian re-matching with reviewer-promoted phantoms added at each buffer), traces from F1 = 0.8333 at 50 m up to F1 = 0.8566 at 150 m in five discrete buffer steps. **The practitioner-useful ceiling is F1 = 0.8554 at R = 125 m** — the largest buffer at which the attractor-pull contribution to recall is statistically distinguishable from within-tile random placement (Obs 272; p = 0.002 at the 100–125 m shell vs p = 0.469 at the 125–150 m shell post-recovery).

**Headline numbers (2026-08-03 re-run)**:

- **F1 curve** (50 → 75 → 100 → 125 → 150 m): **0.8333 → 0.8492 → 0.8536 → 0.8554 → 0.8566** (was 0.8332 → 0.8491 → 0.8535 → 0.8552 → 0.8565 post-recovery-but-pre-2397; 0.8317 → 0.8477 → 0.8521 → 0.8538 → 0.8551 pre-recovery).
- **Practitioner-useful cap**: F1 = **0.8554** at R = 125 m (CI [0.8468, 0.8635]).
- **Paper lower-bound headline** at 50 m: F1 = **0.8333** [0.8241, 0.8422]; P = 0.8814, R = 0.7902.
- **Upper-bound-only 150 m row**: F1 = 0.8566 [0.8481, 0.8646] — **not practitioner-useful**, flagged because the 125–150 m shell admits mounds indistinguishable from random within-tile co-occurrences.
- **Sentinel exclusion**: 74 candidates at today's `> 150 m` shell (`buffer_metres = 200`) are excluded from the extended-GT build at every R; their detections contribute FP at every R ≤ 150 m (correct behaviour under the 125 m practitioner cap).
- **Reconciliation with `buffer-100m-diagnostics/report.md`**: this pipeline gives TP = 4,125 at 50 m after the cand-2397 re-run (4,124 post-recovery-but-pre-2397; 4,110 pre-recovery); the diagnostic was last refreshed at the pre-recovery state (its `total_matched_at_50m = 4,108` has never been re-run). The 2-pair gap noted at Session 76 (4,110 vs 4,108) widens to **17 pairs** (4,125 − 4,108 = 17, i.e. the original 2-pair methodological difference, plus the recovery's +14 TP increment, plus the +1 cand-2397 promotion) as neither the recovery nor the cand-2397 entry has propagated to the diagnostic; both are descriptively correct for their respective input states.

**One-line paper claim (2026-08-03 re-run)**: "The 55-map image-generalisation corrected F1 runs from 0.833 at 50 m to 0.857 at 150 m; the practitioner-useful ceiling, at the largest buffer where attractor-pull is statistically distinguishable from within-tile random placement (Obs 272), is **F1 = 0.855 at 125 m** [0.8468, 0.8635]."

## 2. F1 curve (current state — 2026-08-04 regeneration; metrics identical to the 2026-08-03 re-run)

| R (m) | TP | FP | FN | n_ref_student | n_promoted@R | n_ref_extended | P [95 % CI] | R [95 % CI] | F1 [95 % CI] |
|------:|---:|---:|---:|--------------:|-------------:|---------------:|:-----------:|:-----------:|:------------:|
| 50 | 4125 | 555 | 1095 | 4746 | 474 | 5220 | 0.8814 [0.8715, 0.8907] | 0.7902 [0.7776, 0.8025] | **0.8333** [0.8241, 0.8422] |
| 75 | 4255 | 425 | 1086 | 4746 | 595 | 5341 | 0.9092 [0.9002, 0.9175] | 0.7967 [0.7844, 0.8086] | **0.8492** [0.8405, 0.8575] |
| 100 | 4297 | 383 | 1091 | 4746 | 642 | 5388 | 0.9182 [0.9096, 0.9261] | 0.7975 [0.7854, 0.8093] | **0.8536** [0.8450, 0.8617] |
| 125 | 4314 | 366 | 1093 | 4746 | 661 | 5407 | 0.9218 [0.9133, 0.9297] | 0.7979 [0.7857, 0.8097] | **0.8554** [0.8468, 0.8635] |
| 150 | 4325 | 355 | 1093 | 4746 | 672 | 5418 | 0.9241 [0.9158, 0.9319] | 0.7983 [0.7861, 0.8101] | **0.8566** [0.8481, 0.8646] |

For the post-recovery-but-pre-2397 numbers (TP = 4,124 at 50 m; F1 = 0.8332 at
50 m to 0.8565 at 150 m) see the `*.pre-cand2397-rerun-20260803T123434.backup`
siblings; for the pre-recovery numbers (TP = 4,110 at 50 m; F1 = 0.8317 at 50 m
to 0.8551 at 150 m) see the `report.md.pre-recovery-20260503T023134.backup`
sibling. All are preserved at the same path.

## 3. How to read this table

- **TP / FP / FN**: Hungarian-matching counts against the extended GT at R. Every reviewer-promoted phantom within R is added to the GT before matching.
- **n_ref_student**: Student GT points scoped to the evaluation tile bounds (the denominator without any human-review correction).
- **n_promoted@R**: Number of reviewer-promoted phantoms that ENTER the extended GT at this R (post de-duplication — § 9 caveat 7). Yesterday's 472 mound labels appear at every R ≥ 50. Today's shell-stratified mound labels accumulate as R rises: +3 reviewed @ 50 m of which 1 (cand 2397) is de-duplicated against its curator twin, so +2 enter; +121 @ 75 m, +47 @ 100 m, +19 @ 125 m, +11 @ 150 m.
- **n_ref_extended**: Scoped extended-GT count at R (student GT scoped ∪ in-scope phantoms at R). This is the recall denominator.
- **F1 [95 % CI]**: Corrected F1 at R with tile-level bootstrap CI.

## 4. Comparison to yesterday's 50 m result

Yesterday's single-buffer correction (`compute_corrected_f1_human_reviewed.py`) produced **F1 = 0.8295** at R = 50 m via an analytic adjustment to measured counts (moved 472 FPs into TP and added them to the GT denominator, without re-running Hungarian). This script's R = 50 m row (**F1 = 0.8333** after the 2026-08-03 cand-2397 re-run; was 0.8332 post-recovery-but-pre-2397 and 0.8317 pre-recovery) re-runs Hungarian over extended GT including the 3 today-corrections at 50 m. Expected ΔF1 ≈ +0.003 versus yesterday's number. The two numbers are methodologically close but not identical — Approach B allows detections to rematch optimally against the extended GT, which can free a detection previously bound to a distant student-GT point to pair with a closer phantom.

Both round to the paper-citation **≥ 0.830** headline; the multi-buffer figure is the paper-preferred value because it uses the later multi-buffer re-review labels.

## 5. Obs 272 caveat — the 150 m row is an upper bound

Obs 272 in `docs/notes/reflections/working-notes.md` shows the attractor-pull effect (reviewer confirmations concentrating closer to the detection than a uniform within-tile null would predict) is statistically significant only through 125 m. At the (125, 150] shell the shell-specific mound-confirmation rate is indistinguishable from the within-tile random-placement null (p = 0.381), and the (150, 286] shell (the "200 m" sentinel in today's CSV) is completely indistinguishable (p = 0.433).

**Implication for interpretation**:

- **R ≤ 125 m**: corrected F1 / P / R are practitioner-meaningful. The reviewer-promoted phantoms in these shells are confirming detections genuinely spatially associated with visible mound symbols.
- **R = 150 m**: corrected F1 at 150 m is an **upper bound on achievable practitioner recall**, not a practitioner-useful operating point. Including the 11 mounds in the (125, 150] shell inflates recall in a way the attractor-pull null cannot distinguish from coincidental alignment.
- **R > 150 m (excluded from this analysis)**: the 74 candidates at the `> 150 m` sentinel (`buffer_metres = 200`) are visible mounds inside the 286 m corners-plus-5 px review circle but outside every review ring. They are **not** added as phantoms at any R in this analysis; their detections appear as FP at every R ≤ 150 m, which is the correct behaviour under the 150 m practitioner cap.

## 6. Practitioner-useful cap: F1 at R = 125 m

Recommended single-number summary for downstream quotation (2026-08-03 re-run): **F1 = 0.8554 at R = 125 m (95 % CI [0.8468, 0.8635])** — the largest R where the attractor-pull contribution to recall is statistically distinguishable from within-tile random placement. The 150 m row (0.8566) is a strict upper bound; the 50 m row (0.8333) is the conservative lower bound and matches the paper-citable ≥ 0.830 headline.

## 7. Sentinel exclusion

74 candidates at today's `> 150 m` shell (`buffer_metres = 200`) are excluded from every extended-GT build in this analysis. Their detections contribute FP at every R ≤ 150 m. Rationale: these detections sit inside the 286 m corners-plus-5 px review circle but outside every review ring, so no phantom promotion is warranted within the 150 m practitioner cap (Obs 272). See `buffer-band-lift/report.md` §7 for the full attractor-pull-cap derivation.

## 8. Reconciling with the buffer-100m diagnostic

The sibling `results/55maps-image-generalisation/buffer-100m-diagnostics/report.md` reports `total_matched_at_50m = 4,108`, while this pipeline reports TP = 4,125 at 50 m after the 2026-08-03 cand-2397 re-run. The 17-pair gap has three components: a **methodological difference in the ground-truth inputs** (the original 2 pairs), the **refresh-state difference** introduced by the 2026-05-03 image recovery (a further 14 pairs), and the **cand-2397 promotion** picked up by the 2026-08-03 re-run (1 more). None is a bug in either pipeline:

- **This corrected-F1 pipeline** uses both yesterday's single-buffer review (`human-review.csv`, 472 mounds at 50 m) and today's multi-buffer re-review (`human-review-multi-buffer.csv`, 3 additional mounds specifically confirmed at the 50 m shell — candidate IDs 5641 (map K-35-075-4), 5777 (map K-35-076-1), and 2397 (map K-35-062-4_Asenovgrad_4326, added at `c816d4bd4`)). Total: 475 phantoms at 50 m.
- **The diagnostic** uses only yesterday's review (472 phantoms at 50 m) with the same Hungarian one-to-one matching.

**This pipeline's 4,125 is the paper-citable count**; it underpins the canonical corrected-F1 headline of 0.833 at 50 m. The diagnostic's 4,108 is descriptive only, citable for the 50 → 100 m recall-gain decomposition (71 new matches admitted at 100 m, 0 lost) but not as a stand-alone TP headline. Step 6 backlog entry S6.1 was resolved 2026-04-24 with reconciliation notes added to both reports in commit `783f37c2`.

**Session-76 reconciliation, restated at the 2026-08-03 state**: the reconciliation those commit-`783f37c2` notes were written to explain compared 4,110 (this pipeline, pre-recovery) against 4,108 (the diagnostic) — a 2-pair gap wholly attributable to the two extra 50 m phantoms above. The 2026-05-03 image recovery lifted this pipeline's TP@50 to 4,124, and the 2026-08-03 cand-2397 re-run to 4,125, while the diagnostic's `total_matched_at_50m` stayed at 4,108 (single commit `da2681709`, 2026-04-21, never re-run), so the gap now reads 17 pairs: the same 2-pair methodological difference, plus 14 recovery-promoted TPs, plus 1 cand-2397 promotion. The Session-76 explanation is unchanged; only the arithmetic moved.

## 9. Caveats / risk register

1. **150 m row is NOT practitioner-useful** (§5). The 0.8566 F1 at R = 150 m (2026-08-03 re-run; was 0.8565 post-recovery-but-pre-2397 and 0.8551 pre-recovery) includes 11 mounds in the statistically-indistinguishable-from-random (125, 150] shell. Paper text must cite the 125 m row (0.8554) as the practitioner-useful cap; 150 m is reportable as an upper bound only.
2. **Lower-bound framing** (§4, §6): the 0.8333 at 50 m (2026-08-03 re-run; was 0.8332 post-recovery-but-pre-2397 and 0.8317 pre-recovery) is the paper-citable lower bound under the conservative reviewer policy (Obs 263 + Obs 268; 21.4 % one-directional flip rate confirming reviewer defaulting to not-mound). A more-permissive reviewer policy would raise the floor.
3. **Per-map F1 not reported**: this artefact is buffer-stratified only; no per-map breakdown (consistent with the single-buffer sibling). Sample size per map would be small and per-sheet CIs noisy.
4. **Bootstrap resamples tiles, not reviewer labels**: the 10,000-iteration bootstrap here resamples at the tile level (standard pipeline bootstrap), capturing matching variability across the 55-map corpus. The reviewer-label bootstrap variance is already baked into the phantoms via yesterday + today review; the two uncertainty sources are not commensurable (same caveat as the single-buffer sibling §4 Caveat 3).
5. **Extended-GT methodology is Approach B**: extended GT includes reviewer-promoted phantoms at each R. Approach A (analytic adjustment without re-running Hungarian) is the single-buffer sibling's methodology. Approach B's Hungarian re-matching is the preferred methodology at buffer > 50 m because it allows detections to rematch against closer phantoms.
6. **Level-up did not re-run the analysis**. All numbers in §2 were lifted verbatim from `report_autogen.md` (regenerated by the same script run, so the twin cannot drift).
7. **The extended-GT build does not de-duplicate phantoms against the student
   GT** — and at HEAD the cand-2397 mound is present in *both* channels. The
   curator added a GT point at exactly cand 2397's detection coordinates
   (326977.31391498476, 4658047.464190174) in
   `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` at commit
   `2e075eb99` (feature `uuid` `manual-2026-05-03-K35-062-4-001`, whose own
   `_added_2026-05-03` note describes it as a "phantom-FP rescue at image cand
   2397"), while the same rescue is also encoded as a `mound` row in
   `human-review-multi-buffer.csv` at `c816d4bd4`. `build_extended_gt` in
   `scripts/compute_corrected_f1_multi_buffer.py` concatenates student GT and
   phantoms with no coincidence check, so scoring against the HEAD student GT
   would place **two GT points 0.00 m apart**; Hungarian one-to-one matching
   then credits one and books the other as an unmatched FN. Measured cost of
   that double-count (re-run against the HEAD 4,746-feature GT, same seed and
   inputs otherwise): FN +1 at every R, and recall at 50 m *falling* to 0.7901
   against the § 2 table's 0.7902, despite a rescue that should only help.
   **RESOLVED 2026-08-04**: `build_extended_gt` now de-duplicates
   channel-coincident rescues (commit `1de559119` — any phantom within
   1 m of a same-map student-GT point is dropped and the student
   channel kept; the drop count is recorded as
   `n_phantom_duplicates_dropped`; the fix propagates to
   `paired_permutation_corrected_55maps` and
   `score_55maps_extended_gt_canonical` by import). The § 2 artefact
   was then regenerated from the **tracked HEAD student GT (4,746
   features)** through the fix (`30a902f56`): every metric and CI is
   identical to the pre-fix 4,745-blob run; only the channel
   accounting moves (`n_reviewer_promoted_at_R` −1 at every R,
   `n_ref_student_only` 4,745 → 4,746, `n_phantom_duplicates_dropped`
   = 1) — the rescue is counted once, on the student side. The
   companion exposure sweep of other GT-plus-CSV consumers is recorded
   in the Session-126 triage register.

## 10. Paper implications

### 10.1 Paper-citable headline numbers (per-buffer)

- **Conservative lower bound**: F1 = 0.8333 at 50 m (2026-08-03 re-run; within-band pull; 475 phantoms from yesterday + today review).
- **Practitioner-useful cap**: F1 = 0.8554 at 125 m (2026-08-03 re-run; largest buffer with significant attractor-pull signal; Obs 272).
- **Upper bound, caveated**: F1 = 0.8566 at 150 m (2026-08-03 re-run; admits statistically-indistinguishable-from-random shell mounds; use with explicit Obs 272 caveat).

All three cite this artefact. The Results section should lead with 0.8333 @ 50 m as the conservative headline, then state the 125 m practitioner cap, then optionally note the 150 m upper bound with caveat.

### 10.2 Precision monotonicity is a methodological finding

Precision rises monotonically from 0.8814 at 50 m to 0.9241 at 150 m (2026-08-03 re-run; was 0.8812 → 0.9239 post-recovery-but-pre-2397, and 0.8810 → 0.9239 pre-recovery) — a 4.3-percentage-point gain driven by the FP count dropping from 555 to 355 as the reviewer-promoted phantom pool expands. Recall is nearly flat (0.7902 → 0.7983). The F1 curve's rise is almost entirely precision-driven. This is a useful methodological data point: Approach B's phantom-promotion mostly converts existing FPs to TPs rather than adding new TPs via re-matching; the recall headroom is small.

### 10.3 Suggested paper text (Results — corrected-F1 multi-buffer)

> Applying a buffer-stratified corrected-F1 methodology (Approach B: extended-GT Hungarian re-matching with reviewer-promoted phantoms added at each R) to the 55-map image-generalisation corpus yields the F1 curve 0.8333 → 0.8492 → 0.8536 → 0.8554 → 0.8566 at R ∈ {50, 75, 100, 125, 150} m (2026-08-03 re-run; 95 % BCa bootstrap CIs in Table [multi-buffer]; 10,000 iterations, seed 42, tile-level resampling). The practitioner-useful cap is **F1 = 0.8554 at R = 125 m**, the largest buffer at which the attractor-pull contribution to recall is statistically distinguishable from within-tile random placement (Obs 272; shell permutation p = 0.002 at 100–125 m vs p = 0.469 at 125–150 m post-recovery). The 150 m row is reported as an upper bound under the Obs 272 caveat; the 50 m row is the conservative lower bound. Precision rises monotonically from 0.8814 at 50 m to 0.9241 at 150 m, primarily by converting existing FPs to TPs as the reviewer-promoted phantom pool expands; recall is nearly flat (0.7902 → 0.7983). 74 candidates at the `> 150 m` sentinel shell are excluded from the extended-GT build at every R and appear as FP throughout, consistent with the 125 m practitioner cap.

## 11. Files manifest

**Outputs (this directory)**:

- `report.md` — this report (hand-authored, paper-citation source).
- `report_autogen.md` — script-authored sibling (regenerated by the 2026-08-03 run).
- `corrected-f1.csv` — §2 table data.
- `summary.json` — machine-readable summary + full bootstrap CIs.
- `*.pre-cand2397-rerun-20260803T123434.backup` — the superseded
  post-recovery-but-pre-2397 artefacts (`summary.json`, `corrected-f1.csv`,
  `report_autogen.md`), preserved rather than discarded.
- `*.pre-recovery-20260503T023134.backup` — the superseded pre-recovery
  artefacts, preserved from the 2026-05-03 refresh.

**Inputs**:

- `outputs/55maps-image-generalisation/verified/verified_detections.geojson` — VLM detections post-verifier (**4,680 features** at HEAD; 4,665 pre-recovery).
- `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` — student GT, consumed at the **tracked HEAD state (4,746 mounds)**. The curator point added at image cand 2397 (`2e075eb99`) duplicates the phantom the review CSV supplies; `build_extended_gt`'s coincidence de-duplication (`1de559119`) counts the rescue once, on the student side — see § 9 caveat 7.
- `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` — 55-map evaluation bounds (8,541 tiles).
- `results/55maps-image-generalisation/human-review.csv` — yesterday's review (1,028 rows; 472 mounds, all at 50 m).
- `results/55maps-image-generalisation/human-review-multi-buffer.csv` — today's multi-buffer re-review (558 rows; **275 mounds** across shells, of which 74 sit at the excluded `buffer_metres = 200` sentinel).

## 12. Reproducibility

- **Script**: `scripts/compute_corrected_f1_multi_buffer.py`. Writes `corrected-f1.csv` + `summary.json` + `report_autogen.md` in the output directory.
- **Guardrail (Session 75 item 6 / Session 76 carry-over)**: script hardened 2026-04-24 to redirect Markdown output from `report.md` to `report_autogen.md`, protecting this hand-authored level-up against dry-run overwrite.
- **Bootstrap**: 10,000 iterations, seed 42, tile-level resampling (configurable via CLI).
- **Exact command that produced the current § 2 table** (run on `sapphire`,
  2026-08-04, repo at `1de559119`, wall-clock ~36 s). Every input is a
  tracked working-tree path — no git-blob materialisation step is needed
  since `build_extended_gt`'s coincidence de-duplication (§ 9 caveat 7):

    ```bash
    python scripts/compute_corrected_f1_multi_buffer.py \
        --verified-detections outputs/55maps-image-generalisation/verified/verified_detections.geojson \
        --student-gt inputs/vectors/references/student-mounds-55maps-reviewed.geojson \
        --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
        --review-yesterday results/55maps-image-generalisation/human-review.csv \
        --review-today results/55maps-image-generalisation/human-review-multi-buffer.csv \
        --output-dir results/55maps-image-generalisation/corrected-f1-multi-buffer \
        --buffers 50 75 100 125 150 \
        --n-bootstrap 10000 \
        --seed 42
    ```

  The 2026-08-03 predecessor run materialised the 4,745-feature GT blob
  to a temporary path to sidestep the then-unfixed double-count; its
  command is preserved in the changelog. Running the current script
  against the tracked GT reproduces the § 2 table exactly (verified
  field-by-field, `30a902f56`); the double-counted variant is no longer
  producible without setting `dedup_tolerance_m=0`.

- **Note on the previously recorded command**: the re-run block published here
  before 2026-08-03 used the flags `--detections` and `--out`, which the script
  does not accept — the correct names are `--verified-detections` and
  `--output-dir` (see `parse_args` in
  `scripts/compute_corrected_f1_multi_buffer.py`). The old block would have
  failed at argument parsing; it has been replaced above.
- **Git commit of original data run**: `508f7698` (shortened from `508f76989e0c8739469950bfca415719b6712c83`). Level-up commit: see this file's `git log` entry at 2026-04-24.
- **Toolchain**: Python ≥ 3.11, GeoPandas ≥ 0.14, NumPy, pandas, scipy (for Hungarian). Pinned versions in `requirements.txt`.

## Changelog

### 2026-08-04 — W6-E9 resolved: de-dup fix landed, artefact regenerated from tracked HEAD GT

**Trigger**: the durable fix for the two-channel cand-2397 rescue
(Session-126 escalation W6-E9, PI-approved). `build_extended_gt` gained
coincidence de-duplication (`1de559119`: phantoms within 1 m of a
same-map student-GT point are dropped, the student channel kept,
`n_phantom_duplicates_dropped` recorded; four tier-1 tests). The § 2
artefact was regenerated on sapphire through the fix from the tracked
HEAD student GT (`30a902f56`).

**What changed**: NO metric moved — TP/FP/FN, P/R/F1, and every CI are
identical to the 2026-08-03 state at all five R (verified
field-by-field). Channel accounting only: `n_reviewer_promoted_at_R`
−1 at every R (475→474 at 50 m …), `n_ref_student_only` 4,745 → 4,746,
new field `n_phantom_duplicates_dropped` = 1. § 9 caveat 7 rewritten
from open-hazard to resolved; the § 2 table's n_ref_student /
n_promoted@R columns, the § 3 accumulation note, and the sibling-
artefact note refreshed to the corrected accounting; § 11's input-diff
record annotated; § 12
now shows the tracked-path command (the 2026-08-03 predecessor
materialised the 4,745 blob to a temporary path:
`git cat-file -p 60adff7258b328eb93cee2340715a0a5b4e0e923 > /tmp/...`
then `--student-gt` that path — preserved here for the record).

**What did NOT change**: every headline and CI; the 17-pair gap
decomposition; all conclusions.

### 2026-08-03 (later) — W6-E8: analysis re-run against the current review CSVs

**Refresh trigger**: Session-126 wave-6 escalation W6-E8 (PI-approved). The
earlier wave-6 repair pass (entry below) established that `summary.json` was
written at `8699f456b` (2026-05-03T02:45Z), **88 minutes before** the cand-2397
review entry landed at `c816d4bd4` (04:13Z), and recorded that residue rather
than resolving it. This entry resolves it: the analysis was re-run against the
current review CSVs, so the banner's "cand 2397 now included" claim and § 11's
mound count are true of the artefact for the first time.

**Run**: `sapphire`, 2026-08-03T12:34:34Z, repo at `a6a18b3c4`, 35.9 s
wall-clock, 10,000-iteration tile-level bootstrap, seed 42, buffers
{50, 75, 100, 125, 150}. Exact command in § 12. `summary.json`,
`corrected-f1.csv`, and `report_autogen.md` were all regenerated by that single
run, so the generated twin cannot drift from the § 2 table. The superseded
artefacts are preserved as `*.pre-cand2397-rerun-20260803T123434.backup`.

**Input-change audit** (`8699f456b` → `a6a18b3c4`). Of the five declared
inputs, three are byte-identical (`verified_detections.geojson`,
`55maps_evaluation_bounds.geojson`, `human-review.csv`) and **two** changed:

1. `human-review-multi-buffer.csv` — one row **added** (cand 2397, `mound`,
   `trig_point_on_mound`, `buffer_metres = 50`, map
   `K-35-062-4_Asenovgrad_4326`). No row was removed and **no `human_label`,
   `x`, `y`, or `symbol_type` changed on any pre-existing row**. 493 rows differ
   in the `buffer_metres` *string form only* (`'200.0'` → `'200'`, and a blank →
   `'50'` fill on 283 rows, all of which are `not_mound`); none differs
   numerically, and `build_phantom_gdf` filters on `human_label == 'mound'`
   before reading `buffer_metres`, so the reformatting is inert. Mound counts:
   274 → **275**.
2. `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` —
   4,745 → 4,746 features. **This was not folded in.** The added feature is at
   exactly cand 2397's detection coordinates and duplicates the phantom the
   review CSV supplies; scoring against it double-counted at the time of
   that run. See § 9 caveat 7 for the measured cost. (Superseded
   2026-08-04: the de-dup fix `1de559119` now consumes the tracked HEAD
   GT safely; the § 2 artefact was regenerated through it, `30a902f56`,
   metrics unchanged.)

**Field-by-field movement** (`summary.json`, old → new). The pattern is
identical at every R: **TP +1, FP −1, FN unchanged**, `n_reviewer_promoted_at_R`
+1, `n_ref_extended` +1 — one false positive became a true positive, exactly as
a single phantom promotion should behave.

| R (m) | TP | FP | n_promoted@R | n_ref_extended | F1 (4 d.p.) | P (4 d.p.) | Recall (4 d.p.) |
|------:|:---|:---|:---|:---|:---|:---|:---|
| 50 | 4124 → **4125** | 556 → **555** | 474 → **475** | 5219 → **5220** | 0.8332 → **0.8333** | 0.8812 → **0.8814** | 0.7902 (unchanged) |
| 75 | 4254 → **4255** | 426 → **425** | 595 → **596** | 5340 → **5341** | 0.8491 → **0.8492** | 0.9090 → **0.9092** | 0.7966 → **0.7967** |
| 100 | 4296 → **4297** | 384 → **383** | 642 → **643** | 5387 → **5388** | 0.8535 → **0.8536** | 0.9179 → **0.9182** | 0.7975 (unchanged) |
| 125 | 4313 → **4314** | 367 → **366** | 661 → **662** | 5406 → **5407** | 0.8552 → **0.8554** | 0.9216 → **0.9218** | 0.7978 → **0.7979** |
| 150 | 4324 → **4325** | 356 → **355** | 672 → **673** | 5417 → **5418** | 0.8565 → **0.8566** | 0.9239 → **0.9241** | 0.7982 → **0.7983** |

FN (1095 / 1086 / 1091 / 1093 / 1093), `n_ref_student_only` (4745 at every R)
and the sentinel exclusion (74) are unchanged. Every CI bound moved by
< 0.0002; the largest single movement anywhere in the artefact is +0.00021
(precision at 50 m), well inside the ±0.002 tolerance the escalation set.

**Which rounded forms changed**:

- **4 d.p. F1**: all five moved (table above). Note the 50 m figure returns to
  **0.8333** — the value this document carried *before* the earlier wave-6 pass
  corrected it to 0.8332 against the then-stale artefact. That correction was
  right for the artefact it was checked against; the re-run has now moved the
  artefact.
- **3 d.p. F1**: two moved — **100 m 0.853 → 0.854** and **150 m 0.856 →
  0.857**. The 50 m (0.833), 75 m (0.849), and 125 m (0.855) forms are
  unchanged, so the paper-citable ≥ 0.830 headline and the 0.855 practitioner
  cap need no downstream chasing. (§ 1's one-line paper claim already read
  "0.857 at 150 m", which was a double-rounding slip against the old 0.8565 and
  is now simply correct.)
- **4 d.p. precision**: all five moved. **4 d.p. recall**: three moved
  (75 / 125 / 150 m); 50 m and 100 m are unchanged.
- **Counts**: TP / FP / n_promoted@R / n_ref_extended at every R, plus § 8's
  16-pair → **17-pair** reconciliation gap and § 11's 274 → **275** mound count.

**What did NOT change**:

- **No conclusion moves.** The shape of the F1 curve, the 125 m practitioner
  cap, the 150 m upper bound, the ≥ 0.830 paper-citable headline, the Obs 272
  attractor-pull caveat, and § 10.2's "4.3-percentage-point" precision gain
  (0.9241 − 0.8814 = 0.0427) all stand.
- **Recall is still nearly flat** across the curve (0.7902 → 0.7983).
- **`buffer-100m-diagnostics` was NOT regenerated** — see below.

**`buffer-100m-diagnostics` deliberately left alone**: its `summary.json` was
written once, at commit `da2681709` (2026-04-21), and records
`n_detections = 4665`, `n_student_gt = 4744`, `n_reviewer_phantoms = 472`. Those
are **pre-recovery** values (detections are 4,680 at HEAD), so the artefact is
stale for the whole 2026-05-03 image recovery, not merely for cand 2397.
Regenerating it would fold in the entire recovery and move
`total_matched_at_50m` away from 4,108 — the figure on which §§ 1 and 8 of this
report build their explicitly two-state reconciliation ("descriptively correct
for their respective input states"). That is a larger scope change than this
escalation authorises and would silently rewrite the reconciliation narrative,
so it was left as found and flagged for a separate decision.

**New caveat added**: § 9 caveat 7 documents the phantom/student-GT
double-counting hazard surfaced by this re-run.

**Commit**: not committed by the re-run agent; see this file's `git log` entry
at 2026-08-03 for the landing commit.

### 2026-08-03 — C4 wave-6 repair: 4th-decimal slip, § 10.2 residue, reconciliation figures

**Refresh trigger**: Session-126 wave-6 C4 triage (blind pass P2,
`reports/verification/c4-triage/blind-passes/wave6-pass-P2-2026-08-03.json`,
recommendation R3; families F14 / F15 / F16 / F4 / F1) adjudicated four defect
classes in this document. Repaired under Phase-3 ruling 17
(`reports/verification/phase3-rulings-2026-07-31.md` § 17: living documents in
`results/**.md` are refreshed in place, not marked), with ruling 16's / P2 R9's
coupling discipline applied to the downstream 3 d.p. forms.

**Authority for every replacement value**: the sibling machine artefacts in
this directory — `summary.json` and `corrected-f1.csv` (both at data-run commit
`da84a3d2`, script commit `8699f456b`) and the generated twin
`report_autogen.md` — plus, for the historical column, the preserved
`summary.json.pre-recovery-20260503T023134.backup`.

| Location | Quantity | Before | After | Source |
|:---|:---|---:|---:|:---|
| §§ 1, 4, 6, 9, 10.1, 10.3, banner, sibling note (11 spans) | Corrected F1 @ 50 m, 4 d.p. | 0.8333 | **0.8332** | `summary.json` `$.results[0].F1` = 0.8332154763107384; `report_autogen.md` renders 0.8332 |
| Post-recovery banner | Corrected F1 @ 50 m, pre-recovery | 0.8316 | **0.8317** | pre-recovery backup `$.results[0].F1` = 0.8317312557 |
| Post-recovery banner | ΔF1 across the recovery | +0.0017 | **+0.0015** | 0.8332154763 − 0.8317312557 = 0.0014842 |
| § 1 reconciliation bullet | Gap vs `buffer-100m-diagnostics` | ~14 pairs | **16 pairs** | 4,124 − 4,108; `buffer-100m-diagnostics/summary.json` `$.diagnostic_2_pair_drift.total_matched_at_50m` = 4108 |
| § 8 | This pipeline's TP @ 50 m | 4,110 | **4,124** | `summary.json` `$.results[0].TP` |
| § 8 | Gap framing | 2-pair gap | **16-pair gap (2 methodological + 14 recovery)** | as above |
| § 8 | Canonical corrected-F1 headline, 3 d.p. | 0.832 | **0.833** | 0.8332154763 → 0.833 |
| § 10.2 | Precision @ 50 m | 0.8810 | **0.8812** | `summary.json` `$.results[0].precision` = 0.8811965812 |
| § 10.2 | FP @ 50 m → FP @ 150 m | 555 → 355 | **556 → 356** | `$.results[0].FP`, `$.results[4].FP` |
| § 10.2 | Recall @ 50 m → @ 150 m | 0.7877 → 0.7958 | **0.7902 → 0.7982** | `$.results[0].recall` = 0.7901896915, `$.results[4].recall` = 0.7982278014 |
| § 11 | Student-GT layer count | 4,744 | **4,745** (+ note that HEAD is 4,746) | `git show da84a3d2:inputs/vectors/references/student-mounds-55maps-reviewed.geojson` → 4745 features; HEAD → 4746 |

**What did NOT change**:

- **The 3 d.p. headline is unaffected**: 0.8333 and 0.8332 both round to
  **0.833**, so no downstream document quoting the 3 d.p. form needs chasing
  for the F14 fix (P2 R9). The one 3 d.p. form that *did* move is § 8's
  pre-recovery `0.832` → `0.833`, which was stale for the recovery, not for the
  rounding.
- **No conclusion moves.** The F1 curve, the 125 m practitioner cap
  (F1 = 0.8552), the 150 m upper bound (0.8565), the ≥ 0.830 paper-citable
  headline, and the Obs 272 attractor-pull caveat all stand exactly as before.
- **§ 10.2's "4.3-percentage-point gain" is unchanged**: 0.9239 − 0.8812 =
  0.0427, the same 4.3 pp it was at 0.8810.
- **§ 2's table was already correct** — it has rendered 0.8332 since the
  2026-05-03 refresh; the eleven slips were confined to the prose.

**Known residue NOT repaired in this pass** (recorded for a later sweep; neither
was in the P2 R3 adjudication): § 11's "+274 mounds across shells" for
`human-review-multi-buffer.csv` and the banner's "cand 2397 review entry
`c816d4bd` now included" are both in tension with the § 2 table's provenance.
The CSV at HEAD carries 275 `mound` rows, but `summary.json` was written at
`8699f456b` (2026-05-03T02:45Z), 88 minutes *before* cand 2397 landed at
`c816d4bd4` (04:13Z), so `n_reviewer_promoted_at_R` = 474 at 50 m reflects the
274-mound state. Refreshing the counts without re-running the analysis would
create a new internal inconsistency, so both were left as found.

**Commit**: recorded by the Session-126 W6 doc-repair commit (see this file's
`git log` entry at 2026-08-03).

### 2026-04-21 — Original publication

Script-generated by `scripts/compute_corrected_f1_multi_buffer.py` at commit
`dee0ecf0d` (2026-04-21) as the raw multi-buffer corrected-F1 output;
hand-levelled into the paper-citation source at `e60aadb40` (2026-04-23,
Session 75 guardrail 6, which also hardened the script to write
`report_autogen.md` instead of overwriting this file), with the § 8
reconciliation notes added at `783f37c2a` and the post-recovery refresh applied
at `fc536a19c` (2026-05-03). This banner and changelog were added on 2026-08-03
as the first Revision-Policy stub for the document.
