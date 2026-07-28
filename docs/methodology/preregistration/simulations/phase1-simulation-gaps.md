# Phase 1 Simulation Gap Analysis

> **NOT PART OF THE OSF LODGEMENT.** The registration comprises exactly three
> documents, all in `osf/` (`osf/README.md:3,9-11`); this file is not one of
> them. It is a working document: pre-lodgement content here fed into writing
> the registration but does not license a "the preregistration says" claim,
> and post-lodgement content is operational, not registered. Cite
> `osf/preregistration.md` for registered content. Banner added 2026-07-28
> (D17 audit, structural fix).

**Date**: 2026-01-20
**Purpose**: Identify missing components, script mismatches, and skill documentation issues before executing Phase 1.

---

## Executive Summary

Simulation of Phase 1 (Library Construction) revealed several categories of gaps:

1. **Critical**: Path mismatch preventing config loading
2. **Major**: Skill documentation doesn't match actual script interfaces
3. **Moderate**: Missing study YAML definitions
4. **Minor**: Missing automated pre-flight check script

---

## Critical Issues

### 1. Example Directory Path Mismatch

**Problem**: All configs reference `neutral/example_*.png` but the actual directory is `neutral-naming/`.

**Evidence**:

```text
# Configs use:
"path": "neutral/example_01.png"

# Actual directory:
inputs/examples/neutral-naming/example_01.png
```

**Impact**: Detection script will fail to load example images.

**Fix Required**: Create symlink `inputs/examples/neutral -> neutral-naming` OR rename directory.

---

## Major Issues

### 2. Skill Documentation vs Actual Script Interfaces

The skill documents command-line interfaces that don't exist.

#### `4_detect_mounds_batch.py`

| Documented | Actual | Status |
|------------|--------|--------|
| `--config` | `--config` | Matches |
| `--manifest` | `--manifest` | Matches |
| `--output-dir` | `--output` | Different (filename vs directory) |
| `--workers` | `--workers` | Matches |
| `--dry-run` | — | Missing |
| `--continue-from` | — | Missing |
| `--limit` | — | Missing |

#### `7_analyse_consensus.py`

| Documented | Actual | Status |
|------------|--------|--------|
| `--input-dir` | `--pred` | Different |
| `--output` | — | Missing |
| `--passes` | `--iterations` | Different |
| `--tolerance` | — | Missing |
| — | `--bounds` | Not documented |
| — | `--template` | Not documented |

**Note**: `7_analyse_consensus.py` is for two-stage pipeline analysis, NOT for merging multi-pass detection results. The skill incorrectly describes its purpose.

#### Hard Example Mining

| Documented Script | Actual Script | Interface |
|-------------------|---------------|-----------|
| `mine_hard_cases.py` | `analyse_fp_crops.py` | Different |

The skill documents `mine_hard_cases.py` with argparse flags, but that script uses positional arguments. The correct script for Phase 1 is `analyse_fp_crops.py`.

**`analyse_fp_crops.py` actual interface:**

```bash
python scripts/analyse_fp_crops.py \
    --input <detections.geojson> \
    --output_dir <output_path> \
    --mode fn|fp \
    --manifest <manifest.json>
```

---

## Moderate Issues

### 3. Missing Study YAML Definitions

The `studies/` directory only contains README.md. No actual YAML study definitions exist.

**Required for preregistration reference:**

- `studies/phase1-library.yaml` — Phase 1 library construction
- `studies/phase2a-strand1.yaml` — Verbosity × M/E cross

### 4. Missing Pass Merging Script

The skill documents merging multiple detection passes into consensus, but there's no dedicated script for this. The existing scripts are:

- `generate_union_candidates.py` — For two-stage pipeline candidate aggregation
- `7_analyse_consensus.py` — For two-stage threshold grid search

**Needed**: A script to merge K passes of single-stage detection results with vote counts.

---

## Minor Issues

### 5. No Automated Pre-Flight Check Script

Pre-flight checks are documented in markdown but must be run manually. An automated script would reduce errors.

### 6. Output Directory Conventions

The skill documents output directory conventions (`outputs/phase1-library/pass_01/`) but `4_detect_mounds_batch.py` doesn't support `--output-dir`. It uses `--output` for custom filename only.

---

## Files to Create/Modify

### New Files Needed

| File | Purpose | Priority |
|------|---------|----------|
| `inputs/examples/neutral` | Symlink to `neutral-naming/` | Critical |
| `scripts/merge_passes.py` | Merge K detection passes with vote counts | High |
| `scripts/preflight_check.py` | Automated pre-flight verification | Medium |
| `studies/phase1-library.yaml` | Phase 1 study definition | Medium |

### Skill Files to Update

| File | Changes Needed |
|------|----------------|
| `SKILL.md` | Fix script references and command examples |
| `references/workflow-overview.md` | Correct script interfaces |
| `references/preregistration-phases.md` | Update commands to match actual scripts |

### Script Updates Needed

| Script | Changes |
|--------|---------|
| `4_detect_mounds_batch.py` | Add `--output-dir`, `--dry-run`, `--limit` options |

---

## Verification Checklist for Complete Repository

Before committing for preregistration reference:

- [ ] `inputs/examples/neutral` symlink created
- [ ] All config paths resolve correctly
- [ ] `scripts/merge_passes.py` created and tested
- [ ] `studies/phase1-library.yaml` created
- [ ] Skill documentation matches actual scripts
- [ ] Pre-flight checks can run without errors (except API key)
- [ ] `--dry-run` option added to detection script

---

## Recommended Action Order

1. **Fix critical path issue** — Create `neutral` symlink
2. **Update 4_detect_mounds_batch.py** — Add missing CLI options
3. **Create merge_passes.py** — New script for pass aggregation
4. **Update skill documentation** — Align with actual interfaces
5. **Create phase1-library.yaml** — Study definition
6. **Create preflight_check.py** — Optional automation

---

*Report generated during Phase 1 simulation, 2026-01-20*
