# 55-Map Image Generalisation — Post-Run Follow-ups

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

### 2. Examine per-map breakdown for heterogeneity

- `cost_manifest.json` has per-map candidate counts that range 60–298
  (~5× spread). Evaluate F1 per map to see where the pipeline is
  working vs failing.
- Useful for the paper's transfer-learning narrative: does the pipeline
  generalise uniformly across the 55 maps, or are there systematic
  failure modes (e.g., heavy-forest maps with low mound density
  failing, sparse-feature maps OK)?
- Script: adapt `analyse_secondary_effects.py` per-map-sheet analysis
  (already exists for Era 2 4-map study) to the 55-map scope.

### 3. Commit the outputs

- Run artefacts not yet committed: `outputs/55maps-image-generalisation/`
  + the three `configs/run-configs/55maps_image_generalisation_*.md`
  and the edits to `prompts/configs/library_plus-hp.json`
  (already committed at `b84925d2` for the launcher pre-run, but needs
  a follow-up commit for the outputs).
- Recommended structure: one commit for the launcher pre-run
  (already done), one commit for the post-run artefacts.
- Command: `git add configs/run-configs/55maps_image_generalisation_post_run_report.md
  outputs/55maps-image-generalisation/` then commit.

### 4. Write the observation

- Add a new observation to `docs/notes/reflections/working-notes.md`
  (next after Obs 255, so Obs 256 or 257) documenting:
  - F1 = 0.771 @ 50 m image-track (vs 0.791 text-track → −0.020)
  - Cross-modality pattern consistent with Era 2: text outperforms
    image at generalisation scale
  - Cost $365 at Flex; per-tile $0.043, per-map $6.63, per-detection
    $0.078
  - Cache hit rate 91% (demonstrating caching ROI at scale)
  - 0.06% tile failure rate (operational reliability confirmed)

### 5. Launcher robustness fixes

Three latent bugs surfaced during the run, all recovered operationally
without data loss. Apply to `scripts/run_generalisation.py`:

- **Task #15**: Pass-skip check should use `*.meta.json` not
  `*.geojson`. `.geojson` is written incrementally; `.meta.json` is
  written at end-of-run only. Current check wrongly skips interrupted
  passes that have partial geojson.
- **Task #16**: SIGINT/SIGTERM handler should propagate to the active
  subprocess so killing the launcher also kills the in-flight proposer
  or verifier. Observed: 5-second orphan window during the worker
  switch, cleaned up manually.
- **Task #17**: Remove or relax the `failed_passes >= 3` gate.
  Exit-code-2 is the proposer's "log and continue" signal per its own
  contract, but my launcher counted every exit-code-2 pass toward the
  "aborted" threshold. Fired after all 5 proposer passes succeeded.
  Either drop the gate entirely (proposer manages tile-level failures
  itself) or gate on aggregate tile-failure rate (e.g., abort if
  overall rate > 1%).

## Priority order

1. (1) Debug CIs — blocks paper write-up
2. (3) Commit outputs — makes run artefacts citable
3. (4) Write observation — captures findings while fresh
4. (2) Per-map heterogeneity — feeds into paper discussion
5. (5) Launcher fixes — robustness for future runs, no urgency

## Related documents

- `configs/run-configs/55maps_image_generalisation.yaml`
- `configs/run-configs/55maps_image_generalisation_pre_launch_audit.md`
- `configs/run-configs/55maps_image_generalisation_post_run_report.md`
- `outputs/55maps-image-generalisation/cost_manifest.json`
- `outputs/55maps-image-generalisation/evaluation/evaluation.json`
