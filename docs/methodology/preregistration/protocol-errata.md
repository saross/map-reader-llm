# Protocol Errata

**Purpose**: Record of corrections, clarifications, and deviations from the preregistered protocol identified during execution. This document is maintained for transparency and reproducibility.

**Associated preregistration**: `preregistration.md` v4.7 (2026-01-31)

**See also**: `osf/execution-checklist.md` for execution tracking

---

## Classification

- **Correction**: Fix to implementation that brings it into alignment with the preregistered protocol (no protocol change)
- **Clarification**: Interpretation of an ambiguous point in the preregistration
- **Deviation**: Substantive change from the preregistered protocol (requires justification)

---

## Entries

### E1: Stale version/date in OSF companion README

| Field | Value |
|-------|-------|
| Date | 2026-01-31 |
| Type | Correction |
| Commit | `a9ed78b` |
| Impact | None (cosmetic) |

**Description**: The `osf/README.md` file contained a stale date (`2026-01-14`) that did not match the current preregistration version (v4.7, 2026-01-31). Updated to `2026-01-31` along with version alignment across all three OSF companion documents (`f037a9d`).

**Protocol impact**: None. These are companion metadata files, not the preregistration document itself.

---

### E2: Missing execution fields in Phase 1 config

| Field | Value |
|-------|-------|
| Date | 2026-02-01 |
| Type | Correction |
| File | `prompts/configs/library_pure-positive-canon.json` |
| Impact | Would have prevented execution or produced non-preregistered results |

**Description**: The library config file used by Phase 1 (`run_phase1.py`) was missing five execution fields required by the batch detection script (`4_detect_mounds_batch.py`):

| Field | Missing default | Preregistered value |
|-------|----------------|---------------------|
| `model` | `None` (crash) | `gemini-3-flash` |
| `temperature` | `0.1` (wrong) | `1.0` |
| `instruction_file` | `v3.0_system_instruction.md` (doesn't exist) | `detect_image-only.md` |
| `thinking_level` | omitted | `minimal` |
| `max_output_tokens` | `8192` | `8192` |

**Root cause**: The library config files (`library_*.json`) were designed as examples-only compositions for use with `run_study.py`, which supplies execution parameters from its own `defaults` section. However, `run_phase1.py` passes the config directly to the batch script, requiring it to be self-contained.

**Fix**: Added the five fields to `library_pure-positive-canon.json`, matching the values specified in the preregistration (Section 8.9) and the pattern established in other detection configs (e.g., `detect_image-only.json`).

**Protocol impact**: None. The preregistered parameters are unchanged; this corrects the implementation to match them. Without the fix, either the script would crash (`model=None`, missing instruction file) or silently use wrong parameters (`temperature=0.1` instead of `1.0`).

---

*End of errata. New entries should be appended above this line.*
