# SUPERSEDED 2026-04-24

**Reason**: Follow-up items resolved and consolidated.

**See**: `results/meta-findings-summary.md` (2026-04-23; folds Obs 262-273 into paper-Discussion shape, covering all post-run follow-up items)

This document is preserved for audit / historical reference. Its original content follows below.

---

## 55-Map Image Generalisation — Post-Run Follow-ups

**Status**: Open list. Created 2026-04-18 after the run completed at 05:10 UTC.
**Run artefacts**: `outputs/55maps-image-generalisation/` + `configs/run-configs/55maps_image_generalisation_*.md`

## Outstanding items

### 1. Debug missing bootstrap confidence intervals — **RESOLVED 2026-04-18**

False alarm. The bootstrap CIs were always present — I misread the
evaluation JSON. `evaluate_detections.py` writes CI fields flat at the
buffer level (`f1_ci_lower`, `f1_ci_upper`, same for P and R); my
post-run summary script looked for a nested `ci.f1.lower` structure
and silently returned 0 for every value.

**Actual results**:

| Buffer | F1 | 95% CI |
|-------:|---:|:------:|
| 20 m | 0.506 | [0.492, 0.520] |
| 30 m | 0.686 | [0.672, 0.697] |
| 40 m | 0.748 | [0.737, 0.760] |
| 50 m | 0.771 | [0.760, 0.782] |

Half-widths ~0.01; publication-quality. No re-run needed. Post-run
report updated with the real numbers.

### 2. Examine per-map breakdown for heterogeneity — **RESOLVED 2026-04-18**

Matched-configuration per-map F1 analysis completed for the 55 maps
plus the 4 Era 2 calibration maps as a baseline. Script
`scripts/analyse_55maps_heterogeneity.py`; artefacts under
`results/55maps-image-generalisation/`.

Key findings:

- Mean F1 @ 50 m drops from 0.887 (4-map) to 0.750 (55-map) = −0.137
- SD @ 50 m widens ~4.4× (0.021 → 0.094). Generalisation widens the
  distribution, not just shifts it.
- Best 55-map (F1 = 0.894) matches best 4-map (0.903) — pipeline can
  work as well out-of-sample on at least some maps.
- **K-35-075-3** is a persistent low-outlier (F1 = 0.286 across all
  buffers); buffer loosening does not help, indicating an FP problem
  rather than a spatial-precision problem. **Diagnosed as an
  under-annotation artefact** (see
  `results/55maps-image-generalisation/k35-075-3-diagnostic.md`):
  the student ground truth has only 2 mounds, vs 58–142 in the three
  adjacent same-row maps. Two of the 10 "FPs" are verifier-confirmed
  at p ≥ 0.95 and are almost certainly real mounds that annotators
  missed. Excluding this single map tightens SD @ 50 m from 0.093 to
  0.069 (−26%) and raises the minimum F1 from 0.286 to 0.587.
- Cost per map is uniform (r ≈ 0 with F1); cost cannot predict
  difficulty on a new map.
- Candidate count weakly predicts F1 (r = +0.16 to +0.30) — denser
  mound maps produce more true-positive matches.

### 3. Commit the outputs — **RESOLVED 2026-04-18**

Post-run artefacts committed at `4c147af6` ("data(55maps-image): final
image-track generalisation run — F1=0.771 @ 50 m"); observations
committed at `15eb9383` (Obs 256–257). Working tree clean.

### 4. Write the observation — **RESOLVED 2026-04-18**

Two observations added to `docs/notes/reflections/working-notes.md`:

- **Obs 256**: 55-Map Image Generalisation — F1 = 0.771 Measured
  (0.795 Dawid-Skene Corrected), Image Trails Text by 0.02
  Out-of-Sample. Includes the measured-vs-D-S-corrected comparison
  and cross-modality numbers.
- **Obs 257**: Generalisation Widens the F1 Distribution ~4× —
  Per-Map Heterogeneity on the 55-Map Image Run, Dominated by One
  Under-Annotated Outlier. Covers the 4-map-vs-55-map SD ratio, the
  K-35-075-3 diagnostic, cost/difficulty correlation nulls, and the
  sensitivity analysis.

### 5. Launcher robustness fixes — **RESOLVED 2026-04-18** (commit `b80cfc30`)

Three latent bugs surfaced during the run, all recovered operationally
without data loss. Applied to `scripts/run_generalisation.py`:

- **Task #15 (resolved)**: Pass-skip check now uses `*.meta.json`
  (proposer writes this only on successful completion), not
  `*.geojson` (partial during run).
- **Task #16 (resolved)**: SIGINT/SIGTERM handler propagates to the
  active subprocess via Popen + module-level `_active_subprocess`
  handle; launcher terminates child on signal before exiting
  128+signum.
- **Task #17 (resolved)**: Removed the `failed_passes >= 3` gate.
  Exit-code-2 is the proposer's documented "log and continue" signal.
  Partial-pass count is still logged for audit. Genuine escalation
  surfaces via `execution_stats.items_failed` in the cost manifest.

Audited via `/audit`: no Critical findings; one Medium (theoretical
microsecond Popen-assignment race — acceptable for publication).

## Priority order

All items resolved except (7) Human verification of VLM-only candidates —
urgent pre-publication task, in progress.

## Added 2026-04-18

### 6. Dawid-Skene corrected F1 — **RESOLVED 2026-04-18** (commit `[pending]`)

Ran `scripts/analyse_dawid_skene.py` against the image run's
consensus + verifier probabilities (newly added CLI path overrides
to the script so it can target any run, not just the legacy text
run). Results under
`results/55maps-image-generalisation/dawid-skene/`.

Headline:

| Method | F1 | P | R |
|--------|---:|--:|--:|
| Measured (vs student GT) | 0.771 | 0.780 | 0.763 |
| Simple FN correction (5%) | 0.790 | 0.821 | 0.762 |
| **Dawid-Skene posterior** | **0.795** | **0.821** | **0.772** |

+0.024 F1 correction vs measured — the same magnitude as the prior
text-run correction (0.790 → 0.814). Shared item set: 5,798 items
(3,637 matched, 1,133 student-only, 1,028 VLM-only). EM converged
in 11 iterations. Estimated VLM-only posterior P(true=1) = 0.186.

### 7. Human verification pass of VLM-only candidates — **URGENT, PENDING**

The D-S analysis (item 6) identifies 1,028 VLM-only candidates —
detections the pipeline produced that don't match any student
ground-truth mound. D-S's aggregate posterior estimates ~186 of
these are real mounds missed by annotators, but cannot discriminate
individual items (2-annotator identifiability limit).

Per-item discrimination requires human review. Use the existing
Streamlit app:

```bash
streamlit run scripts/review_candidates.py -- \
    --crops-dir outputs/55maps-image-generalisation/crops \
    --probabilities outputs/55maps-image-generalisation/verified/probabilities.json \
    --ground-truth inputs/vectors/references/student-mounds-55maps.geojson \
    --bounds inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson \
    --output results/55maps-image-generalisation/human-review.csv
```

Output: CSV with human classification (mound / not-mound / uncertain)
for each VLM-only candidate. Results feed back into the corrected
F1 calculation — replacing D-S's aggregate posterior with item-level
ground truth, which is identifiable and far more defensible.

This is an urgent pre-publication item: the paper's generalisation
F1 should be accompanied by a human-verified correction, not just
the D-S aggregate estimate.

## Related documents

- `configs/run-configs/55maps_image_generalisation.yaml`
- `configs/run-configs/55maps_image_generalisation_pre_launch_audit.md`
- `configs/run-configs/55maps_image_generalisation_post_run_report.md`
- `outputs/55maps-image-generalisation/cost_manifest.json`
- `outputs/55maps-image-generalisation/evaluation/evaluation.json`
