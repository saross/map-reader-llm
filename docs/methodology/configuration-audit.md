# Configuration Audit Report — 2026-03-15

**Scope**: All completed experiments (Phases 1, 2a-2e, 3a, 3c, 3d, H11,
Phase 3a replication, Flash-Lite pilot)
**Method**: Three parallel audit agents, each covering a phase group,
comparing Study YAML → Prompt config JSON → Metadata JSON for every
condition. Adapted from `/audit` anti-satisficing framework.
**Presupposition**: Errors exist; the job is to find them.

---

## Critical (must fix before publication)

### C1: H11 verifier config drift — RESOLVED

**Phase**: H11 proposer-verifier (384 and 512)
**Category**: Parameter fidelity, within-experiment isolation
**Description**: Verifier configs had silently diverged from the Phase 3d
baseline in three ways: text-only configs missing all 6 example labels,
image configs with 9 examples instead of 6 (modified labels + 3 extra
null examples), and study YAML referencing the wrong config (image
instead of text-only).
**Impact**: H11 PV results pre-correction are invalid. The verifier
received a fundamentally different prompt than Phase 3d.
**Resolution**: Fixed in commit `9b023ae` (2026-03-15). All configs
aligned to Phase 3d. H11 PV re-run with v2 configs completed. v2
results (512 F1=0.732, 384 F1=0.682) are the authoritative figures.
**Status**: RESOLVED. See Decision 19, Observation 163.

---

## Medium (should investigate)

### M1: Phase 3a metadata records wrong thinking_level — KNOWN

**Phase**: Phase 3a (`track2-text-high/`)
**Category**: Metadata accuracy
**Description**: All metadata files in `track2-text-high/` record
`thinking_level: minimal` when the actual API used HIGH thinking.
The metadata writer captured the config file's default value rather
than the runtime parameter.
**Impact**: Metadata cannot verify thinking level. The results are
correct (HIGH was used), but automated audit of metadata would flag
a false inconsistency.
**Resolution**: Documented in Observation 141 and hypothesis-tracking.md.
Phase 3a replication uses separate config files (`detect_brief-text.json`
vs `detect_brief-text-high.json`) to ensure correct metadata. The
`--thinking-level` CLI flag (added in commit `ead94aa`) now mutates the
config dict before metadata is written, preventing recurrence.
**Status**: KNOWN AND MITIGATED. Original metadata files preserved
unmodified per user decision.

---

## Low (documentation only)

### L1: detect_brief-text.json has temperature 1.0 (legacy)

**Phase**: N/A (no impact on any executed experiment)
**Category**: Configuration consistency
**Description**: `detect_brief-text.json` specifies `temperature: 1.0`
(from its Phase 2a origin) but Phase 2d and later use T=0.0 via CLI
override or symlinks to Phase 2b results.
**Impact**: Zero — the temperature is always overridden at runtime.
The file value is never used in its raw form for any post-Phase-2a
experiment.
**Status**: Not an error. The config's temperature (1.0) is correct
for its original purpose (Phase 2a H1 baseline). Subsequent phases
correctly override via `--temperature 0.0`. Changing the file would
make it inconsistent with Phase 2a's historical use.

### L2: Phase 2e config-default metadata lacks ordering_override field

**Phase**: Phase 2e, config-default condition
**Category**: Metadata completeness
**Description**: The config-default condition (symlinked from Phase 2c)
does not include an `ordering_override` field in metadata, since no
override was applied.
**Impact**: Zero — this is correct behaviour. Config-default used the
JSON file's original order without override.
**Status**: Working as designed. Not an error.

### L3: Phase 3a metadata thinking_level null vs "minimal"

**Phase**: Multiple (early runs before thinking_level was in configs)
**Category**: Metadata recording inconsistency
**Description**: Some metadata files record `thinking_level: null` at
the top level but correctly record `"minimal"` in the
`full_config_snapshot` section. The top-level field was not populated
when the config didn't include `thinking_level` as a key.
**Impact**: Zero for results. Minor inconvenience for automated
metadata queries that don't check `full_config_snapshot`.
**Status**: Already fixed. The `--thinking-level` CLI flag (commit
`ead94aa`) mutates `config["thinking_level"]` before the metadata
tracker reads it, so future runs will always populate this field.

---

## Cross-experiment issues

### Carry-forward chain verified

All carry-forward transitions checked and passed:

| Transition | Carried parameter | Verified |
|:-----------|:-----------------|:--------:|
| Phase 2a → 2b | Optimal M/E (brief-text-image Track 1, brief-text Track 2) | Yes |
| Phase 2b → 2c | Optimal T=0.0 | Yes |
| Phase 2c → 2d | Optimal library (plus-hp Track 1, brief-text Track 2) | Yes |
| Phase 2d → 2e | Optimal H5 (minimal) | Yes |
| Phase 2e → 3a | All optimal parameters | Yes |
| Phase 3a → 3d | Optimal config + consensus parameters | Yes |

No silent parameter changes detected in any carry-forward.

### Within-experiment isolation verified

All OFAT/factorial phases checked for target-parameter-only variation:

| Phase | Target parameter | All others constant? |
|:------|:----------------|:-------------------:|
| 2a | Modality/elaboration | Yes |
| 2b | Temperature | Yes |
| 2c | Library composition | Yes |
| 2d | Negative text treatment | Yes |
| 2e | Example ordering | Yes |
| 3a | Temperature (within tracks) | Yes |
| H11 | Tile size | Yes (after v2 correction) |

---

## Verified correct (explicitly checked and passed)

### Phase 1

- Temperature, thinking level, model, example count all match config
- System instruction hash consistent across 5 passes

### Phase 2a (H1 modality, 5 conditions)

- Only M/E and `include_example_images` vary; T, thinking, library constant
- All 5 conditions use 17 examples (Scale-8)
- System instruction hashes differ correctly per M/E level

### Phase 2b (H7 temperature, 10 conditions across 2 tracks)

- Only temperature varies; M/E, thinking, library constant per track
- CLI temperature override correctly recorded in metadata
- Track 1 and Track 2 use correct carried-forward M/E configs

### Phase 2c (H8 library, 5 conditions)

- Only library composition varies (7, 9, 13, 13, 17 examples)
- T=0.0 constant across all conditions
- Instruction file constant (detect_brief-text-image.md)

### Phase 2d (H5 negative text, 6 conditions across 2 tracks)

- Only exclusion guidance text varies (minimal, terse, verbose)
- T=0.0, library, and M/E constant per track
- Minimal baseline correctly symlinked to prior phase results

### Phase 2e (H4 ordering, 4 conditions)

- Only example ordering varies (config-default, canonical-first,
  canonical-last, random)
- Random seeds correctly incremented (42-51 across runs 1-10)
- Config-default correctly symlinked to Phase 2c plus-hp

### Phase 3a (H3 consensus, 4 tracks × 3 temperatures)

- Temperature correctly applied via CLI override
- System instruction hash consistent within each track
- Example counts consistent within each track

### Phase 3d (H2 two-stage pilot)

- Verifier examples match Phase 3d VERIFIER_EXAMPLES exactly
- crop_label text matches Phase 3d prompt
- Text-only labels match Phase 3d build_verifier_request()

### H11 (tile size, v2 corrected)

- Proposer config, temperature, thinking level all correct
- Verifier configs corrected to Phase 3d baseline
- Evaluation bounds uniform (512 scope for both tile sizes)
- 384 and 512 manifest files reference correct tile directories

### Phase 3a replication

- Minimal config: detect_brief-text.json (thinking=minimal)
- HIGH config: detect_brief-text-high.json (thinking=high)
- Only thinking_level differs between the two configs
- Temperature 0.7 applied from YAML `fixed` section

### Flash-Lite pilot

- Model override to gemini-3.1-flash-lite-preview confirmed in output
  filenames and metadata
- All other parameters match Flash baseline

---

## Audit statistics

| Metric | Count |
|:-------|------:|
| Phases audited | 12 |
| Conditions checked | ~45 |
| Metadata files sampled | ~80 |
| Parameters verified per condition | 6-8 |
| Total parameter checks | ~350 |
| Critical findings | 1 (resolved) |
| Medium findings | 1 (known, mitigated) |
| Low findings | 3 |
| False positives | 0 |
