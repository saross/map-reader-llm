# SUPERSEDED 2026-04-24

**Reason**: Run executed 2026-04-18.

**See**: `outputs/55maps-text-high-generalisation/post_run_report.md` (and the active cross-track summary `results/55maps-cross-track-comparison/report.md`)

This document is preserved for audit / historical reference. Its original content follows below.

---

## 55-Map Text HIGH Re-run — Plan

**Created**: 2026-04-18
**Purpose**: Re-execute the 2026-04-10 text HIGH generalisation run
under the publishable launcher (`scripts/run_generalisation.py`) so
it sits alongside the text MIN (2026-04-18) and image HIGH
(2026-04-18) runs with equivalent documentation: pre-launch audit,
post-run report, launch_manifest, cost_manifest, per-map cost
attribution, reproducibility artefacts.

The existing 2026-04-10 run at `outputs/55maps-generalisation/`
stays intact. Its retrospective post-run report in
`configs/run-configs/55maps_text_generalisation_retrospective_post_run_report.md`
labels its limitations honestly (proposer cost estimated, no per-map
attribution, no cache hit rate, etc.). This re-run closes those
limitations with measured values.

## Expected outcome

- **Measured F1 @ 50 m**: ≈ 0.790 (matches prior HIGH run; same
  config, same tiles, same GT)
- **D-S corrected F1 @ 50 m**: ≈ 0.814 (ΔF1 = +0.024, same magnitude
  as text MIN and image HIGH corrections)
- **Cost**: ~$75 (prior estimate; publishable launcher will measure
  precisely)
- **Runtime**: ~2-3 h at 250 workers on Flex tier

## Configuration — differences from reference configs

Two configs to mirror:

1. **2026-04-10 text HIGH parameter set** (retrospective YAML):
   `configs/run-configs/55maps_text_generalisation_retrospective.yaml`.
   Use as the parameter baseline.

2. **2026-04-18 text MIN launched config** (template YAML):
   `configs/run-configs/55maps_text_min_generalisation.yaml`.
   Use as the structural/format template.

### Required changes from the text MIN YAML

| Field | text MIN (existing) | text HIGH (new) |
|-------|---------------------|-----------------|
| `run_name` | `55maps-text-min-generalisation` | `55maps-text-high-generalisation` |
| `proposer.thinking_level` | `minimal` | `high` |
| Other proposer fields | unchanged | unchanged |
| Verifier / consensus / evaluate | unchanged | unchanged |

Everything else (workers=250, vote_threshold=4, prob_threshold=0.15,
buffers [20,30,40,50], bootstrap=1000, seed=42) stays identical.

## Work to do (in order)

1. **Write the YAML config** at
   `configs/run-configs/55maps_text_high_generalisation.yaml` by
   copying the text MIN YAML and flipping the two fields above.
   Comment header should describe: re-run for documentation symmetry;
   paired with 2026-04-10 run.

2. **Write the pre-launch audit** at
   `configs/run-configs/55maps_text_high_generalisation_pre_launch_audit.md`
   mirroring the text MIN audit structure. Key sections:
   - Sources of truth consulted
   - Preregistration requirements extracted (~15 items; same as MIN
     audit except thinking_level MATCHES production E49 not the
     MIN-under-test variant)
   - Configuration pairwise diff (vs text MIN YAML + vs retrospective
     text HIGH YAML — two-way check)
   - Transmission check (9 rows, all expected PASS)
   - Preregistration alignment (expect all MATCHES)
   - Dry-run record (to be filled after step 4)
   - Evaluation scope
   - Completeness
   - Code audit (`/audit`) findings
   - Overall verdict

3. **`/audit` the YAML + audit MD** — expect minimal findings (the
   configs are near-identical to already-audited text MIN). Fix any
   real issues, document acceptable ones.

4. **`/audit-config`** pre-launch — expect READY TO LAUNCH with no
   BLOCKERs. Dry-run on sapphire as part of this step.

5. **Commit the YAML + audit MD** to main (so the launch_manifest
   records the exact pre-launch state).

6. **Launch on sapphire headless**:
   ```bash
   ssh sapphire "cd ~/Code/map-reader-llm && git pull --ff-only origin main && \
       nohup .venv/bin/python scripts/run_generalisation.py all \
           --run-config configs/run-configs/55maps_text_high_generalisation.yaml \
           --run-name 55maps-text-high-generalisation \
           --yes \
           > /tmp/55maps-text-high-generalisation.log 2>&1 &"
   ```
   Use `--yes` not `--allow-dirty`; git should be clean after pull.
   The `git pull` step ensures sapphire's recorded `git.commit_sha`
   matches the actual launcher content (closes the provenance
   caveat seen in the MIN run — see GH issue #5).

7. **Monitor** for `Run complete` / `Cost manifest` events.

8. **Post-run**: sync outputs from sapphire, run D-S correction on
   sapphire (new subagent), run paired permutation test vs text MIN
   (we already have text MIN's verified_detections.geojson committed,
   and the text HIGH run will produce its own), write the post-run
   report mirroring the text MIN post-run report.

9. **Commit** all run artefacts + post-run report + paired-test
   results. Push to main. Pull on amd-tower + zbook.

## Input files (all present on sapphire, verified 2026-04-18)

| File | Size |
|------|-----:|
| `inputs/tiles_384_55maps/` | 2.0 GB |
| `inputs/rasters/Russian1981_32635/` | 2.4 GB |
| `inputs/tiles_384_55maps/full_evaluation_manifest.json` | 8,541 entries |
| `inputs/vectors/references/student-mounds-55maps.geojson` | 2.0 MB |
| `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` | 3.0 MB |
| `prompts/configs/detect_brief-text.json` | 2.6 KB |
| `prompts/configs/verify_adversarial-text.json` | 1.4 KB |

## Environment state at plan creation

All three environments in sync at git `ac4ba4e0`:

- amd-tower (HEAD: `ac4ba4e0`, clean)
- sapphire (HEAD: `ac4ba4e0`, clean after reset + pull earlier today)
- zbook (HEAD: `ac4ba4e0`, clean)

## Reference artefacts (read before starting)

Pre-launch audit + post-run report templates to mirror:

- Pre-launch audits: `configs/run-configs/55maps_text_min_generalisation_pre_launch_audit.md`
  and `configs/run-configs/55maps_image_generalisation_pre_launch_audit.md`
- Post-run reports: `configs/run-configs/55maps_text_min_generalisation_post_run_report.md`
  and `configs/run-configs/55maps_image_generalisation_post_run_report.md`

Observation context (for narrative framing):

- `docs/notes/reflections/working-notes.md` — Obs 256, 257 (image
  run results and heterogeneity)

## Key scientific reference points (for post-run comparison)

The new text HIGH run will sit in a 3-way comparison:

| Run | Date | F1 @ 50 m (measured) | F1 @ 50 m (D-S) | Cost |
|-----|------|--------------------:|----------------:|-----:|
| Text HIGH (old) | 2026-04-10 | 0.790 | 0.814 | ~$75 est |
| Image HIGH | 2026-04-18 | 0.771 | 0.795 | $364.70 |
| Text MIN | 2026-04-18 | 0.759 | 0.783 | $60.79 |
| **Text HIGH (this run)** | **2026-04-19 (planned)** | **≈ 0.790 expected** | **≈ 0.814 expected** | **~$75 expected** |

The paired permutation test with text MIN should reproduce the
pattern observed on the 2026-04-10 vs 2026-04-18 MIN pairing:
significant at 30/40/50 m, ns at 20 m.

## Budget approval

The user pre-approved this re-run in session 2026-04-18. Budget
~$75. This plan formalises that for the new session.

## GH issues to be aware of (context only, NOT blockers)

- [#1](https://github.com/saross/map-reader-llm/issues/1) — `_estimate_cost()` image-biased; expected_cost_usd in launch_manifest will over-report
- [#2](https://github.com/saross/map-reader-llm/issues/2) — Popen-assignment race in signal handler (theoretical)
- [#3](https://github.com/saross/map-reader-llm/issues/3) — Pass-skip fragile to partial meta.json (rare)
- [#4](https://github.com/saross/map-reader-llm/issues/4) — heterogeneity script polish
- [#5](https://github.com/saross/map-reader-llm/issues/5) — launcher SHA256 in launch_manifest

None block the re-run.

## Memory references to preload in new session

The auto-memory system should load these via CLAUDE.md at session start:

- `feedback_compute_on_sapphire.md` — heavy compute goes to sapphire
- `feedback_audit_new_code.md` — /audit new/modified code
- `feedback_experimental_parameter_control.md` — careful parameter matching
- `project_k30_strategy.md` — K=5 not K=10

## Success criteria

- [ ] YAML, pre-launch audit, post-run report all committed before launch
- [ ] `/audit-config` returns READY TO LAUNCH with 0 BLOCKERs
- [ ] Dry-run passes on sapphire
- [ ] Full run completes in ~2-3 h at cost ~$75 ± 15 %
- [ ] F1 @ 50 m ≈ 0.790 (matches prior HIGH run within CI)
- [ ] Dawid-Skene correction ≈ +0.024 F1 (consistent with other 3 runs)
- [ ] Paired permutation test vs text MIN: significant at 30/40/50 m,
  ns at 20 m (reproduces the 2026-04-10 vs 2026-04-18 MIN pattern)
- [ ] All artefacts committed and pushed; sapphire + zbook pulled
- [ ] Brief observation added to working-notes.md if the pattern
  holds; flagged to user if it doesn't
