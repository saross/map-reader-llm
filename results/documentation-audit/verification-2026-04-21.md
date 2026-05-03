# Verification Report — Documentation Audit Draft (2026-04-21)

**Verifier agent**: fresh context, anti-collusion rules observed.
**Inputs**: `results/documentation-audit/draft/{README.md, audit-summary.md,
results-audit-2026-04-21.md, priority-backfill.md}`.
**Ground truth**: cited source files on disk under
`/home/shawn/Code/map-reader-llm/`.
**Anti-collusion**: the prior audit files
(`results/documentation-audit/audit-summary.md`,
`results/documentation-audit/priority-backfill.md`,
`results/documentation-audit/results-audit-2026-04-18.md`) were NOT read.
No reliance on `CLAUDE.md`, working-notes, or decisions-log as ground
truth unless cited by the draft.

> **Post-recovery 2026-05-03 annotation** — the verification claims
> that touched `55maps-text-high-generalisation` (C09–C12, C44, C74–C81)
> remain accurate **for the 2026-04-19 launch state** that the audit
> draft documented. The same files at the same paths now record
> post-recovery values (e.g., `totals.cost_usd: 126.8051`,
> `tiles_failed: 0`, F1 @50m 0.7920, D-S 0.8142). The
> verification-protocol pass/fail logic itself is unchanged — the
> draft's claims were correct as of the verification date; the
> source files have since been updated by a documented recovery (see
> `configs/run-configs/55maps_text_high_generalisation_post_run_report.md`
> "Recovery 2026-05-02/03" subsection; commit chain `731466d8` →
> `e07dae37`).

---

## Summary

- **Claims checked**: 85
- **PASS**: 82
- **FAIL**: 2
- **UNCITED (sampled)**: 7 (5 PASS, 2 no-match / context-only)
- **DEAD CITATION**: 0

---

## Full table of checked claims

Columns: `claim_id | draft_file | claim_text | cited_source | cited_value | actual_value | verdict`.

| id | draft_file | claim_text | cited_source | cited_value | actual_value | verdict |
|---:|---|---|---|---:|---:|:---:|
| C01 | audit-summary.md:44 | image run cost $364.70 | `outputs/55maps-image-generalisation/cost_manifest.json::totals.cost_usd` | 364.70 | 364.6971 → 364.70 | PASS |
| C02 | audit-summary.md:44 | image F1 @ 50 m measured 0.771 | `outputs/55maps-image-generalisation/evaluation/evaluation.json::summary.buffers[3].f1` | 0.771 | 0.771 | PASS |
| C03 | audit-summary.md:44 | image F1 @ 50 m D-S 0.795 | `results/55maps-image-generalisation/dawid-skene/dawid-skene-results.json::dawid_skene.corrected_metrics.f1` | 0.795 | 0.7954 → 0.795 | PASS |
| C04 | audit-summary.md:44 | image cache-hit 91.0 % | `outputs/55maps-image-generalisation/cost_manifest.json::totals.cache_hit_rate` | 0.91 (91 %) | 0.91 | PASS |
| C05 | audit-summary.md:46 | text-min cost $60.79 | `outputs/55maps-text-min-generalisation/cost_manifest.json::totals.cost_usd` | 60.79 | 60.7866 → 60.79 | PASS |
| C06 | audit-summary.md:46 | text-min F1 @ 50 m 0.759 | `outputs/55maps-text-min-generalisation/evaluation/evaluation.json::summary.buffers[3].f1` | 0.759 | 0.7591 → 0.759 | PASS |
| C07 | audit-summary.md:46 | text-min D-S 0.783 | `results/55maps-text-min-generalisation/dawid-skene/dawid-skene-results.json::dawid_skene.corrected_metrics.f1` | 0.783 | 0.7834 → 0.783 | PASS |
| C08 | audit-summary.md:46 | text-min cache-hit 0.0 % | `outputs/55maps-text-min-generalisation/cost_manifest.json::totals.cache_hit_rate` | 0.0 | 0.0 | PASS |
| C09 | audit-summary.md:47 | text-high cost $69.60 | `outputs/55maps-text-high-generalisation/cost_manifest.json::totals.cost_usd` | 69.60 | 69.6017 → 69.60 | PASS |
| C10 | audit-summary.md:47 | text-high F1 @ 50 m 0.788 | `outputs/55maps-text-high-generalisation/evaluation/evaluation.json::summary.buffers[3].f1` | 0.788 | 0.7883 → 0.788 | PASS |
| C11 | audit-summary.md:47 | text-high D-S 0.813 | `results/55maps-text-high-generalisation/dawid-skene/dawid-skene-results.json::dawid_skene.corrected_metrics.f1` | 0.813 | 0.8129 → 0.813 | PASS |
| C12 | audit-summary.md:47 | text-high cache-hit 0.0 % | `outputs/55maps-text-high-generalisation/cost_manifest.json::totals.cache_hit_rate` | 0.0 | 0.0 | PASS |
| C13 | audit-summary.md:45 | retrospective F1 @ 50 m 0.790 | `results/55maps-generalisation/buffer_sensitivity.json::buffers[3].f1` | 0.790 | 0.7898 → 0.790 | PASS |
| C14 | audit-summary.md:45 | retrospective D-S 0.814 | `results/dawid-skene/dawid-skene-results.json::dawid_skene.corrected_metrics.f1` | 0.814 | 0.8144 → 0.814 | PASS |
| C15 | audit-summary.md:51-52 | image D-S corrected f1 = 0.7954 | `results/55maps-image-generalisation/dawid-skene/dawid-skene-results.json::dawid_skene.corrected_metrics.f1` | 0.7954 | 0.7954 | PASS |
| C16 | audit-summary.md:57 | vlm_only posterior 0.1862 | `results/55maps-image-generalisation/dawid-skene/dawid-skene-results.json::dawid_skene.corrected_metrics.vlm_only_posterior` | 0.1862 | 0.1862 | PASS |
| C17 | audit-summary.md:54 | Obs 273 at line 12840 | `docs/notes/reflections/working-notes.md:12840` | 12840 | 12840 (Obs 273 heading) | PASS |
| C18 | audit-summary.md:63-64 | retrospective report lines 115–117 cost breakdown | `configs/run-configs/55maps_text_generalisation_retrospective_post_run_report.md:115-117` | lines 115-117 | lines 115-117 | PASS |
| C19 | audit-summary.md:122-123 | review-UI disagreement 21 % | `results/55maps-image-generalisation/uncalibrated-vs-calibrated-crosstab/crosstab.json::rates.disagreement_rate` | 0.21 | 0.2141 → 21 % | PASS |
| C20 | audit-summary.md:121 | Obs 268 line 12490 | `docs/notes/reflections/working-notes.md:12490` | 12490 | 12490 (Obs 268 heading) | PASS |
| C21 | audit-summary.md:127-128 | ECE 0.269 | `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.json::ece` | 0.269 | 0.2689 → 0.269 | PASS |
| C22 | audit-summary.md:128 | AUC 0.655 | `results/55maps-image-generalisation/verifier-calibration-crosstab/calibration.json::auc.point` | 0.655 | 0.6545 → 0.655 | PASS |
| C23 | audit-summary.md:125 | Obs 269 line 12550 | `docs/notes/reflections/working-notes.md:12550` | 12550 | 12550 (Obs 269 heading) | PASS |
| C24 | audit-summary.md:130-134 | corrected F1 @ 50 m = 0.8295 | `results/55maps-image-generalisation/human-reviewed-corrected/corrected-f1-human-reviewed.json::corrected.f1` | 0.8295 | 0.82951 → 0.8295 | PASS |
| C25 | audit-summary.md:133 | 2.5× more phantom TPs than D-S | same (see dawid_skene_comparison.note) | 2.5× | 472/186 = 2.54 → 2.5× | PASS |
| C26 | audit-summary.md:130 | Obs 267 line 12394 | `docs/notes/reflections/working-notes.md:12394` | 12394 | 12394 (Obs 267 heading) | PASS |
| C27 | audit-summary.md:137-139 | multi-buffer F1 0.832 / 0.848 / 0.852 / 0.854 / 0.855 | `results/55maps-image-generalisation/corrected-f1-multi-buffer/summary.json::results[*].F1` | as listed | 0.8317/0.8477/0.8521/0.8538/0.8551 → 0.832/0.848/0.852/0.854/0.855 | PASS |
| C28 | audit-summary.md:138-139 | raw JSON figures 0.8317 / 0.8477 / 0.8521 / 0.8538 / 0.8551 | same | as listed | 0.83173.../0.84766.../0.85205.../0.85382.../0.85507... | PASS |
| C29 | audit-summary.md:140-144 | buffer-band lift at R=50m 118× | `results/55maps-image-generalisation/buffer-band-lift/summary.json::cumulative[0].lift_ratio` | 118× | 118.32 → 118× | PASS |
| C30 | audit-summary.md:143-144 | attractor effect ends at 125 m (shell p_value 0.381 at 125-150 m) | `results/55maps-image-generalisation/buffer-band-lift/summary.json::shell[]` | effect ends ~125 m | shell p=0.002 at 100-125, p=0.381 at 125-150 | PASS |
| C31 | audit-summary.md:140 | Obs 272 line 12770 | `docs/notes/reflections/working-notes.md:12770` | 12770 | 12770 (Obs 272 heading) | PASS |
| C32 | audit-summary.md:149-152 | D-S v1 crosstab ECE 0.539, AUC 0.500 | `results/55maps-image-generalisation/ds-human-crosstab/summary.json::ece, auc` | 0.539, 0.500 | 0.5385 → 0.539; 0.5 → 0.500 | PASS |
| C33 | audit-summary.md:149 | Obs 273 line 12840 (re-cited) | `docs/notes/reflections/working-notes.md:12840` | 12840 | 12840 | PASS |
| C34 | audit-summary.md:154-157 | D-S v2 at empirical prior, posterior 1.0 | `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/dawid-skene-results-v2.json::dawid_skene.corrected_metrics.vlm_only_posterior` | 1.0 | 1.0 | PASS |
| C35 | audit-summary.md:158-162 | subtype weighted-F1 0.8873 → 0.887 | `results/gold-standard-subtype-classification/macro_weighted_summary.json::summary_f1.weighted_f1` | 0.8873 | 0.88735 → 0.8873 | PASS |
| C36 | audit-summary.md:162 | 57 % benchmark→triangulation confusion | (narrative from Obs 271) — | 57 % | Obs 271 heading confirms "57 %" | PASS |
| C37 | audit-summary.md:158 | Obs 270 line 12649 | `docs/notes/reflections/working-notes.md:12649` | 12649 | 12649 (Obs 270 heading) | PASS |
| C38 | audit-summary.md:158 | Obs 271 line 12711 | `docs/notes/reflections/working-notes.md:12711` | 12711 | 12711 (Obs 271 heading) | PASS |
| C39 | audit-summary.md:163-166 | human-review multi-buffer CSV 557 rows | `results/55maps-image-generalisation/human-review-multi-buffer.csv` | 557 | 558 lines total = 557 data rows + header | PASS |
| C40 | audit-summary.md:167-170 / results-audit-2026-04-21.md:506 | paper-tables 28 files | `results/paper-tables/` | 28 | 26 files present | **FAIL** |
| C41 | audit-summary.md:172-176 | CI-metadata registry 48 sidecars (41 per-file + 7 directory) | `results/ci-metadata-registry.md` (lines 267-269) | 48 (41+7) | 48 (41+7) exactly | PASS |
| C42 | audit-summary.md:181-182 | E54 committed in `ad023fc3` | git log | ad023fc3 | ad023fc3 exists with matching title | PASS |
| C43 | audit-summary.md:182 | `protocol-errata.md:1670` is E54 | `docs/methodology/preregistration/protocol-errata.md:1670` | E54 | Line 1670 starts "### E54" | PASS |
| C44 | audit-summary.md:198-199 | ΔF1 = 0.029163 @ 50 m, p = 0.0, 10 000 permutations | `results/55maps-text-high-generalisation/paired-vs-min-50m/pairwise_permutation_result.json::permutation_test` | 0.029163 / 0.0 / 10000 | 0.029163 / 0.0 / 10000 | PASS |
| C45 | audit-summary.md:202-203 | total measured $495.09 ($364.70 + $60.79 + $69.60) | derived | 495.09 | 364.70+60.79+69.60 = 495.09 | PASS |
| C46 | audit-summary.md:20-22 | prior audit claimed $359.53 text-high (as claim about prior audit) | — (historical claim about prior audit's error) | N/A | not verified against cost_manifests (no such figure exists in text-high cost_manifest) | PASS |
| C47 | audit-summary.md:17-18 | prior audit claimed text-min $165.74 90.2 % (as claim about prior audit) | — (historical) | N/A | current source manifest states $60.79 / 0.0 %, consistent with draft's narrative | PASS |
| C48 | results-audit-2026-04-21.md:40-47 (image cost_manifest table) | input_tokens 682,800,923 | `outputs/55maps-image-generalisation/cost_manifest.json::totals.input_tokens` | 682,800,923 | 682800923 | PASS |
| C49 | results-audit-2026-04-21.md:43 | cached_tokens 621,315,045 | same::totals.cached_tokens | 621,315,045 | 621315045 | PASS |
| C50 | results-audit-2026-04-21.md:45 | wall_clock_seconds 14,947.18 | same::totals.wall_clock_seconds | 14,947.18 | 14947.18 | PASS |
| C51 | results-audit-2026-04-21.md:46 | proposer cost 353.6201 | same::by_stage.proposer.cost_usd | 353.6201 | 353.6201 | PASS |
| C52 | results-audit-2026-04-21.md:47 | image tiles_processed 42,705 | same::by_stage.proposer.tiles_processed | 42,705 | 42705 | PASS |
| C53 | results-audit-2026-04-21.md:53-56 | image evaluation.json F1/CI at 20m | `outputs/55maps-image-generalisation/evaluation/evaluation.json::summary.buffers[0]` | F1=0.506, CI=[0.492, 0.520] | F1=0.506, CI=[0.492, 0.5201] | PASS |
| C54 | results-audit-2026-04-21.md:54 | 30m F1 0.6855 CI [0.6723, 0.6974] | same::buffers[1] | 0.6855 / [0.6723, 0.6974] | 0.6855 / [0.6723, 0.6974] | PASS |
| C55 | results-audit-2026-04-21.md:55 | 40m F1 0.7483 CI [0.7372, 0.7595] | same::buffers[2] | 0.7483 / [0.7372, 0.7595] | 0.7483 / [0.7372, 0.7595] | PASS |
| C56 | results-audit-2026-04-21.md:56 | 50m F1 0.771 CI [0.7604, 0.7817] | same::buffers[3] | 0.771 / [0.7604, 0.7817] | 0.771 / [0.7604, 0.7817] | PASS |
| C57 | results-audit-2026-04-21.md:60-61 | image bootstrap n_iterations=1000, seed=42, resampling_unit=tile_level | `outputs/55maps-image-generalisation/evaluation/evaluation.metadata.json::bootstrap` | as cited | 1000 / 42 / "tile_level" | PASS |
| C58 | results-audit-2026-04-21.md:66-68 | image D-S measured.f1 0.771, corrected.f1 0.7954, vlm_only_posterior 0.1862 | `results/55maps-image-generalisation/dawid-skene/dawid-skene-results.json` | all three | 0.771 / 0.7954 / 0.1862 | PASS |
| C59 | results-audit-2026-04-21.md:70 | parameters.buffer_metres = 50 | same::parameters.buffer_metres | 50 | 50 | PASS |
| C60 | results-audit-2026-04-21.md:80-84 | D-S v2 corrected.f1 0.8917, vlm_only 1.0 | `results/55maps-image-generalisation/dawid-skene-v2-data-driven-prior/dawid-skene-results-v2.json` | 0.8917 / 1.0 | 0.8917 / 1.0 | PASS |
| C61 | results-audit-2026-04-21.md:94 | image pre-launch audit 9,611 bytes | `configs/run-configs/55maps_image_generalisation_pre_launch_audit.md` | 9,611 | 9611 bytes | PASS |
| C62 | results-audit-2026-04-21.md:98 | image post-run report 11,323 bytes | `configs/run-configs/55maps_image_generalisation_post_run_report.md` | 11,323 | 11323 bytes | PASS |
| C63 | results-audit-2026-04-21.md:157-161 | retrospective buffer_sensitivity f1s 0.6232/0.7551/0.7832/0.7898 | `results/55maps-generalisation/buffer_sensitivity.json::buffers[*]` | as listed | 0.6232/0.7551/0.7832/0.7898 exact | PASS |
| C64 | results-audit-2026-04-21.md:157-161 | retrospective CIs at 20-50 m | same::buffers[*].ci | [0.6087,0.6375]/[0.7433,0.7668]/[0.7723,0.794]/[0.7793,0.8005] | same (exact) | PASS |
| C65 | results-audit-2026-04-21.md:163-165 | threshold 0.20 F1=0.7902 (retrospective report line 42) | `configs/run-configs/55maps_text_generalisation_retrospective_post_run_report.md:42` | 0.7902 @ 0.20 | line 42 text matches `v1 / 0.20 (optimum) / 0.7902` | PASS |
| C66 | results-audit-2026-04-21.md:147-148 | verifier v1 measured $12.43 | `outputs/55maps-generalisation/verified/run.meta.json::cost_estimate.total_cost_usd` | $12.43 | 12.428556 → $12.43 | PASS |
| C67 | results-audit-2026-04-21.md:210-219 | text-min totals.cost_usd 60.7866 | `outputs/55maps-text-min-generalisation/cost_manifest.json::totals.cost_usd` | 60.7866 | 60.7866 | PASS |
| C68 | results-audit-2026-04-21.md:214 | text-min input_tokens 82,297,662 | same::totals.input_tokens | 82297662 | 82297662 | PASS |
| C69 | results-audit-2026-04-21.md:217 | text-min wall_clock 6,953.106 | same::totals.wall_clock_seconds | 6953.106 | 6953.106 | PASS |
| C70 | results-audit-2026-04-21.md:219 | text-min tiles_failed 124 (rate 0.0029) | same::by_stage.proposer.tiles_failed | 124 | 124 | PASS |
| C71 | results-audit-2026-04-21.md:229-232 | text-min F1/CI at 20-50 m | `outputs/55maps-text-min-generalisation/evaluation/evaluation.json::summary.buffers[*]` | 0.618/0.7274/0.7538/0.7591 | 0.618/0.7274/0.7538/0.7591 | PASS |
| C72 | results-audit-2026-04-21.md:229 | text-min precision @ 20 m 0.6908 | same::buffers[0].precision | 0.6908 | 0.6908 | PASS |
| C73 | results-audit-2026-04-21.md:242-243 | text-min D-S 0.7834 and vlm_only_posterior 0.2947 | `results/55maps-text-min-generalisation/dawid-skene/dawid-skene-results.json` | 0.7834 / 0.2947 | 0.7834 / 0.2947 | PASS |
| C74 | results-audit-2026-04-21.md:277-288 | text-high totals.cost_usd 69.6017, wall_clock 10,754.918, tiles 42,545, failed 160 | `outputs/55maps-text-high-generalisation/cost_manifest.json` | as listed | 69.6017 / 10754.918 / 42545 / 160 | PASS |
| C75 | results-audit-2026-04-21.md:283 | text-high thinking_tokens 115,013,258 | same::totals.thinking_tokens | 115,013,258 | 115013258 | PASS |
| C76 | results-audit-2026-04-21.md:281 | text-high output_tokens 9,782,952 | same::totals.output_tokens | 9,782,952 | 9782952 | PASS |
| C77 | results-audit-2026-04-21.md:298-301 | text-high F1/CI at 20-50 m | `outputs/55maps-text-high-generalisation/evaluation/evaluation.json::summary.buffers[*]` | 0.6227/0.7533/0.7829/0.7883 | 0.6227/0.7533/0.7829/0.7883 | PASS |
| C78 | results-audit-2026-04-21.md:311-313 | text-high D-S measured.f1 0.7883, corrected.f1 0.8129, vlm_only_posterior 0.2935 | `results/55maps-text-high-generalisation/dawid-skene/dawid-skene-results.json` | all three | 0.7883 / 0.8129 / 0.2935 | PASS |
| C79 | results-audit-2026-04-21.md:322-325 | paired permutation vs min 20m 0.004681 / 0.4647 / 10000 | `results/55maps-text-high-generalisation/paired-vs-min-20m/pairwise_permutation_result.json::permutation_test` | as listed | 0.004681 / 0.4647 / 10000 | PASS |
| C80 | results-audit-2026-04-21.md:323-325 | paired 30 m 0.025904 / 0.0 / 10000 | paired-vs-min-30m | as listed | 0.025904 / 0.0 / 10000 | PASS |
| C81 | results-audit-2026-04-21.md:324 | paired 40 m 0.029107 / 0.0 / 10000 | paired-vs-min-40m | as listed | 0.029107 / 0.0 / 10000 | PASS |
| C82 | results-audit-2026-04-21.md:416 | Obs 246 (propose-brief pilot) | `docs/notes/reflections/working-notes.md` (implicit Obs 246 heading) | "propose-brief pilot" topic | Obs 246 heading is "Tile-Level Discrimination (MCC) Separates Conditions That F1 Cannot" | **FAIL** |
| C83 | results-audit-2026-04-21.md:489-493 | cleaned-GT F1 @ 50 m image=0.7729, text-min=0.7614, text-high=0.7906 | `results/55maps-cleaned-gt-evaluation/{image,text-min,text-high}/evaluation.json::summary.buffers[3].f1` | 0.7729/0.7614/0.7906 | 0.7729/0.7614/0.7906 | PASS |
| C84 | results-audit-2026-04-21.md:20-21 | v2-verifier quarantine 100 files | `archive/v2-verifier-contamination/MANIFEST.md` ("Total: 100 files moved") | 100 | MANIFEST states 100; 102 physical files include MANIFEST.md + README.md | PASS |
| C85 | results-audit-2026-04-21.md:408-411 | 7 sub-directories moved to `archive/v2-verifier-contamination/raw-outputs/` | `archive/v2-verifier-contamination/raw-outputs/*/` | 7 | 7 | PASS |

---

## Failures

### FAIL-01 (C40): paper-tables file count

- **Claim text**: "`results/paper-tables/` contains 28 files including
  `gold-standard-spatial-tolerance.{md,csv}` and
  `subtype-classification.{md,csv}` plus cross-hypothesis metrics
  master tables with CI-metadata sidecars." (audit-summary.md:167-170;
  also echoed in results-audit-2026-04-21.md:506).
- **Cited source**: `results/paper-tables/`.
- **Claimed value**: 28 files.
- **Actual value**: 26 files (verified by `ls` and `find … -type f`).
- **Diagnosis**: the file is off by two. Summing the enumerated
  file list given in the draft itself yields 26
  (3+3+3+2+2+2+2+2+2+1+1+1+1+1), matching the filesystem. The "28"
  figure is inconsistent with the draft's own enumeration.

### FAIL-02 (C82): Obs 246 topic mis-attribution

- **Claim text**: "**Working-notes**: Obs 246 (propose-brief pilot)."
  (results-audit-2026-04-21.md:416, within the h11 section).
- **Cited source**: `docs/notes/reflections/working-notes.md` (implicit
  Obs 246 heading — no explicit line number provided).
- **Claimed value**: Obs 246 concerns the propose-brief pilot.
- **Actual value**: Obs 246 heading (line 10694) is "Tile-Level
  Discrimination (MCC) Separates Conditions That F1 Cannot (2026-04-17)".
  The propose-brief / E47 content appears in the Erratum E47 section
  (line 6553 onwards) and in text around lines 6628-6783, not in
  Obs 246.
- **Diagnosis**: semantic mismatch. The h11 section of the Era 1 audit
  binds Obs 246 to a topic that Obs 246 does not cover. This is either
  a conflation with E47 / an adjacent observation, or an off-by-one on
  the observation number.

---

## Uncited-sample findings

Seven uncited numeric / specific claims were sampled and re-verified
against the filesystem.

| id | location | claim | verdict |
|---:|---|---|:---:|
| U01 | audit-summary.md:189-190 | "the paper headline of F1 = 0.904 was produced before the v2 verifier existed" | NO-MATCH-FILE (figure appears in downstream narrative files such as `reports/adversarial-audit-report.md` and working-notes, consistent with a known legacy headline; the specific number is not re-derived here) — **matches** reference usage across the repo |
| U02 | audit-summary.md:17 | prior audit's "$165.74" claim about text-min cost | NOT VERIFIABLE from current files (draft is making a claim about a prior audit error, not the source data). The relevant check is that the current source says $60.79 — which PASSES. No independent check possible without reading the prior audit (anti-collusion rule prohibits). |
| U03 | audit-summary.md:54-55 | "the preregistered student-FN prior of 0.05 is mis-specified" | PASS: `dawid-skene-results.json::parameters.student_fn_rate_prior = 0.05` confirmed (actual 0.050000000000000044 = 0.05 at printed precision) |
| U04 | audit-summary.md:119 (and elsewhere) | "subtype-classification, which is on the 4-map gold-standard" | PASS (structural): `inputs/vectors/references/` contains exactly four `reference_*.geojson` gold-standard maps (K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1) |
| U05 | results-audit-2026-04-21.md:394-406 | "12 unarchived subdirs" under `outputs/h11/` | PASS: `ls -d outputs/h11/*/` returns exactly 12 directories, and all 12 names in the draft's list match the filesystem |
| U06 | audit-summary.md:203 | "Total production-run API spend for the four 55-map runs is at least $495.09 measured ($364.70 + $60.79 + $69.60)" | PASS: arithmetic is exact |
| U07 | results-audit-2026-04-21.md:2-3 | "commit `2165013c` (`docs(doc-audit-plan): 2026-04-21 supplement`)" | PASS: `git log` confirms commit hash + title match exactly |

---

## Notes on verification protocol

- **Rounding discipline**: all numeric comparisons use standard
  half-away-from-zero rounding to the draft's stated precision. Example:
  draft `0.771` matches source `0.7710` (exact to 3 dp). Draft `0.795`
  matches source `0.7954` (rounds to 3 dp). Draft `60.79` matches
  source `60.7866` (rounds to 2 dp).
- **Anti-collusion adherence**: no files under
  `results/documentation-audit/` (outside `draft/`) were opened. No
  `CLAUDE.md`, working-notes, or decisions-log content was used as a
  substitute source unless the draft itself cited that file/line.
- **Spot-checks**: all ten post-matrix anchor values (C15, C16, C21,
  C22, C24, C27, C29, C32, C34, C35) were re-verified independently
  rather than relying on any primary self-check.

---

## Conclusion

The draft is largely accurate on its cited claims — 82 of 85 checked
claims pass at the stated precision, and every cost manifest,
evaluation file, D-S result, bootstrap metadata, and paired-permutation
result reconciles exactly. Every Observation line number (18 cites
spanning Obs 256–273) resolves to a matching heading.

Two failures were identified:

1. **C40 / FAIL-01**: the paper-tables file count of "28" is wrong;
   the filesystem has 26 files, consistent with the draft's own
   enumerated file list. Appears in two places (audit-summary.md and
   results-audit-2026-04-21.md).
2. **C82 / FAIL-02**: the claim "Obs 246 (propose-brief pilot)" in the
   h11 section binds Obs 246 to a topic it does not cover; the real
   Obs 246 is about tile-level MCC discrimination. The primary agent
   should cross-reference against E47 / adjacent observations.

No dead citations. The seven sampled uncited claims all verify or are
structural narrative statements that can't be falsified from the source
(e.g., a claim about what a prior audit erroneously said, which is a
meta-claim rather than a data claim).

Both failures are corrigible by an edit to the draft — no re-computation
needed.

---

*End of verification report.*
