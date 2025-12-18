# Tasks

- [x] Assess repository state after crash
- [x] Archive legacy scripts and commit changes
- [x] Verify versioning strategy (Configs and Results)
- [x] Refactor system instructions to be explicitly versioned
- [x] 1. Rename instruction file to `v3.0_system_instruction.md`
- [x] 2. Update configs to reference it
- [x] 3. Update script to use dynamic loading and save metadata
- [x] Audit legacy archives (V1/V2)
- [x] Answer user questions on traceability and history <!-- id: 0 -->

# FAIR4RS Compliance & Documentation
- [x] Audit repository for FAIR4RS gaps (License, Citation, Readmes) <!-- id: 1 -->
- [x] Create/Update Licenses (Apache 2.0 & CC-BY 4.0) <!-- id: 2 -->
- [x] Create CITATION.cff <!-- id: 3 -->
- [x] Create Root README.md <!-- id: 4 -->
- [x] Create Directory READMEs (scripts, prompts, inputs, outputs, archive) <!-- id: 5 -->
- [x] Enhance Code Documentation (Docstrings & Headers) <!-- id: 6 -->
- [x] Create File Manifests where appropriate <!-- id: 7 -->

# Refactoring Archive Organization
- [x] Audit `archive/results/` contents <!-- id: 8 -->
- [x] Locate missing archival files (`Gemini25-flash`, `v3.2-partial`) <!-- id: 12 -->
- [x] Design new folder structure & naming convention <!-- id: 9 -->
- [x] Rename and move files <!-- id: 10 -->
- [x] Update `ARCHIVE_MANIFEST.md` with new paths <!-- id: 11 -->
- [x] Rationalize `archive/scripts/` naming <!-- id: 13 -->

# Updating Input Paths
- [x] Audit new `inputs/` structure <!-- id: 14 -->
- [x] Update `config.py` and dependent scripts <!-- id: 15 -->
- [x] Update `inputs/README.md` <!-- id: 16 -->

# Renaming Calibration Inputs
- [x] Audit `inputs/calibration-run/` <!-- id: 17 -->
- [x] Propose new directory name & file renames <!-- id: 18 -->
- [x] Execute `mv` commands <!-- id: 19 -->
- [x] Update Prompt Configs (`prompts/versions/*.json`) <!-- id: 20 -->

# Archiving Unused Prompt Examples
- [x] Verify zero references <!-- id: 21 -->
- [x] Move `inputs/prompt_examples/` to `archive/prompt_examples/` <!-- id: 22 -->
- [x] Update `inputs/README.md` & `ARCHIVE_MANIFEST.md` <!-- id: 23 -->

# Finalize Documentation & Cleanup
- [x] Update `planning/future_work.md` <!-- id: 27 -->
- [x] Update `README.md` (root) <!-- id: 28 -->
- [x] Update `scripts/README.md` <!-- id: 29 -->
- [x] Update `archive/README.md` <!-- id: 30 -->
- [x] Commit and Push <!-- id: 31 -->

# Phase 2: Calibration and Benchmarking
- [x] Standardize `target_tiles_manifest.json` (was `calibration_manifest.json`) <!-- id: 32 -->
- [x] Update `4_detect_mounds_batch.py` to support `--manifest` and save metadata <!-- id: 33 -->
- [x] Generate manifest from V3 baseline <!-- id: 24 -->
- [ ] Run benchmark on target set <!-- id: 25 -->
- [ ] Analyze results (FP/FN) <!-- id: 26 -->

# Refactor Input Directory Structure
- [x] Move `outputs/tiles/` to `inputs/tiles/` <!-- id: 34 -->
- [x] Move `references/` to `inputs/references/` <!-- id: 37 -->
- [x] Update `config.py` & `scripts/4_detect_mounds_batch.py` <!-- id: 35 -->
- [x] Update documentation <!-- id: 36 -->

# Refactor Outputs Directory
- [x] Audit `outputs/` contents <!-- id: 38 -->
- [x] Create detailed plan <!-- id: 39 -->
- [x] Move/Rename legacy result folders <!-- id: 40 -->
- [x] Clean up empty directories <!-- id: 41 -->

# Refactor Scripts Directory
- [x] Audit `scripts/` for legacy files <!-- id: 42 -->
- [x] Plan move and renaming <!-- id: 43 -->
- [x] Move files to `archive/scripts/` <!-- id: 44 -->
- [x] Update `ARCHIVE_MANIFEST.md` <!-- id: 45 -->

# Implement Methodological Records
- [ ] Inspect `~/.gemini` structure <!-- id: 46 -->
- [ ] Create `methodology/logs/` <!-- id: 47 -->
- [ ] Write `scripts/archive_methodology.py` <!-- id: 48 -->
- [ ] Verify archiving process <!-- id: 49 -->




