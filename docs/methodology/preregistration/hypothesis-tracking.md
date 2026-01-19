# Hypothesis Tracking Matrix

**Purpose**: Map preregistered hypotheses to their experimental conditions, configs, and status.

**Last updated**: 2026-01-18

---

## Confirmatory Hypotheses (H1-H8)

| ID | Hypothesis | Factor | # Conditions | Config Pattern | Phase | Status |
|----|------------|--------|--------------|----------------|-------|--------|
| H1 | Modality/Elaboration Level | M/E | 5 | `detect_{modality}.json` | 2a | Pending |
| H2 | Two-Stage Pipelines | Architecture | 3 | `propose_*.json`, `verify_*.json` | 3d | Pending (Exploratory) |
| H3 | Consensus Voting | N, threshold | Multiple | N/A (runtime) | 3a | Pending |
| H4 | Example Ordering | Ordering | 3 | `detect_*_canonical-last.json`, `detect_*_random-order.json` | 2e | Pending |
| H5 | Negative Text Treatment | Text level | 3 × 3 | `detect_*_terse.json`, `detect_*_verbose.json` | 2d | Pending |
| H6 | Flash→Pro Transfer | Model | OFAT | Same configs, different model | 4 | Pending |
| H7 | Temperature | T | 5 | N/A (runtime parameter) | 2b | Pending |
| H8 | Library Composition/Scaling | Library size | 7 | `library_*.json` | 2c | Pending |

---

## Exploratory Hypotheses (H9-H15)

| ID | Hypothesis | Factor | Tier | Trigger | Status |
|----|------------|--------|------|---------|--------|
| H9 | Diversity Mechanisms | Text/Image/Temp diversity | A | After Phase 2 | Pending |
| H10 | Training Pool Size | Pool size | B | Budget permits | Pending |
| H11 | Tile Size Effects | Tile dimensions | B | F1 < 0.85 or speed concerns | Pending |
| H12 | HP:HN Ratio | Hard example ratio | B | H8 shows library matters | Pending |
| H13 | Overlap/Stride Effects | Tile overlap | B | Edge errors observed | Pending |
| H14 | Cross-Model Consistency | Provider | C | Deferred to future work | Deferred |
| H15 | Cross-Model Voting | Multi-provider voting | C | Deferred to future work | Deferred |

---

## Detailed Condition Mapping

### H1: Modality/Elaboration Level (Phase 2a)

Tests how text presence and detail level affect detection performance.

| Condition | M/E Level | Text | Images | Config File | Instruction File |
|-----------|-----------|------|--------|-------------|------------------|
| H1-1 | Image-only | Minimal | Yes | `detect_image-only.json` | `detect_image-only.md` |
| H1-2 | Brief-text | Brief | No | `detect_brief-text.json` | `detect_brief-text.md` |
| H1-3 | Brief-text+image | Brief | Yes | `detect_brief-text-image.json` | `detect_brief-text-image.md` |
| H1-4 | Verbose-text | Verbose | No | `detect_verbose-text.json` | `detect_verbose-text.md` |
| H1-5 | Verbose-text+image | Verbose | Yes | `detect_verbose-text-image.json` | `detect_verbose-text-image.md` |

---

### H2: Two-Stage Pipelines (Phase 3d — Exploratory)

Tests whether two-stage architectures improve over single-stage detection.

| Condition | Architecture | Stage 1 | Stage 2 | Configs |
|-----------|--------------|---------|---------|---------|
| H2-A | Single-stage (baseline) | N/A | N/A | Optimal single-stage config |
| H2-B | Coarse-to-fine | `propose_brief.json` | `verify_brief.json` | Both configs |
| H2-C | Fine-to-coarse | Standard detection | Context-expanded re-query | TBD |

**Note**: H2 is now confirmatory but treated as exploratory in execution due to preliminary evidence suggesting no benefit.

---

### H3: Consensus Voting (Phase 3a)

Tests voting pool sizes and thresholds. No separate configs — voting is post-hoc analysis.

| Pool Size | Source | Thresholds Tested |
|-----------|--------|-------------------|
| N=5 | Runs 1-5 or 6-10 | 1, 2, 3, 4, 5 |
| N=10 | All 10 runs | 1, 2, ..., 10 |
| N=30 | Extended (20 additional runs) | 1, 2, ..., 30 |

---

### H4: Example Ordering (Phase 2e)

Tests positioning of canonical vs hard examples.

| Condition | ID | Canonical Position | Config Pattern |
|-----------|----|--------------------|----------------|
| Canonical-first | H4-A | First (positions 1-6) | `detect_*.json` (base configs) |
| Canonical-last | H4-B | Last (final positions) | `detect_*_canonical-last.json` |
| Random | H4-C | Shuffled | `detect_*_random-order.json` |

**Triggered exploratory (H4b)**: If H4 significant, test HP-first vs HN-first ordering within hard block.

---

### H5: Negative Text Treatment (Phase 2d)

Tests text elaboration for negative examples. Crossed with 3 image-using M/E levels.

| Condition | H5 Level | Exclusion Text | Config Pattern |
|-----------|----------|----------------|----------------|
| H5-A | Minimal | "Negative" label only | `detect_*.json` (base configs) |
| H5-B | Terse | Brief guidance | `detect_*_terse.json` |
| H5-C | Verbose | Detailed guidance | `detect_*_verbose.json` |

**Full factorial** (9 cells, 6 net new after H1 overlap):

| M/E Level | H5=Minimal | H5=Terse | H5=Verbose |
|-----------|------------|----------|------------|
| Image-only | `detect_image-only.json` | `detect_image-only_terse.json` | `detect_image-only_verbose.json` |
| Brief-text+image | `detect_brief-text-image.json` | `detect_brief-text-image_terse.json` | `detect_brief-text-image_verbose.json` |
| Verbose-text+image | `detect_verbose-text-image.json` | `detect_verbose-text-image_terse.json` | `detect_verbose-text-image_verbose.json` |

---

### H6: Flash→Pro Transfer (Phase 4)

Tests whether Flash-optimal config transfers to Pro. OFAT sensitivity testing.

| Factor | Tests | Decision Rule |
|--------|-------|---------------|
| M/E | 2 adjacent levels | Adjust if Δ ≥ 0.03 F1 |
| H5 | 2 alternatives | Adjust if Δ ≥ 0.03 F1 |
| T | 2 adjacent temperatures | Adjust if Δ ≥ 0.03 F1 |
| O | 2 alternative orderings | Adjust if Δ ≥ 0.03 F1 |

---

### H7: Temperature (Phase 2b)

Tests temperature effect on detection performance.

| Condition | Temperature | Rationale |
|-----------|-------------|-----------|
| H7-1 | 0.0 | Minimum (deterministic) |
| H7-2 | 0.3 | Low variance (evidence for visual detection) |
| H7-3 | 0.7 | Moderate variance |
| H7-4 | 1.0 | Vendor default |
| H7-5 | 1.3 | Above default |

**Temperature is a runtime parameter** — no separate config files needed.

---

### H8: Library Composition and Scaling (Phase 2c)

Tests library component effects and scaling.

| Condition | ID | Canon+ | Canon- | HP | HN | Null | Total | Config File |
|-----------|----|--------|--------|----|----|------|-------|-------------|
| Pure Positive Canon | H8-1 | 4 | 0 | 0 | 0 | 3 | 7 | `library_pure-positive-canon.json` |
| Canonical | H8-2 | 4 | 2 | 0 | 0 | 3 | 9 | `library_canonical.json` |
| +HP | H8-3 | 4 | 2 | 4 | 0 | 3 | 13 | `library_plus-hp.json` |
| Scale-4 | H8-4 | 4 | 2 | 2 | 2 | 3 | 13 | `library_scale-4.json` |
| Scale-8 | H8-5 | 4 | 2 | 4 | 4 | 3 | 17 | `library_scale-8.json` |
| Scale-16 | H8-6 | 4 | 2 | 8 | 8 | 3 | 25 | `library_scale-16.json` |
| Scale-32 | H8-7 | 4 | 2 | 16 | 16 | 3 | 41 | `library_scale-32.json` |

**Planned contrasts**:

- C1: Pure Positive Canon → Canonical (Canon- effect)
- C2: Canonical → +HP (HP effect)
- C3: +HP → Scale-8 (HN effect)
- S1: Scale-4 → Scale-8 (initial scaling)
- S2: Scale-8 → Scale-16 (mid scaling)
- S3: Scale-16 → Scale-32 (ceiling)
- B1: +HP vs Scale-4 (composition at matched size)

---

### H9: Diversity Mechanisms (Phase 3c — Exploratory)

Tests whether diversity in prompts, images, or temperature improves voting.

| Condition | Text | Images | Temperature | Description |
|-----------|------|--------|-------------|-------------|
| H9-A | Fixed | Fixed | Fixed | Baseline (identical passes) |
| H9-B | Varied | Fixed | Fixed | Text diversity only |
| H9-C | Fixed | Varied | Fixed | Image diversity only |
| H9-D | Fixed | Fixed | Varied | Temperature diversity only |
| H9-E | Varied | Varied | Varied | Full diversity |

---

## Execution Dependency Chain

```text
Phase 0: Preparation
    ↓
Phase 1: Library + Text Construction
    ↓
Phase 2a: H1 (M/E) → optimal M/E
    ↓
Phase 2b: H7 (Temperature) → optimal T
    ↓
Phase 2c: H8 (Library) → optimal library
    ↓
Phase 2d: H5 (Negative Text) → optimal text treatment
    ↓
Phase 2e: H4 (Ordering) → optimal ordering
    ↓
    ├── Phase 3a: H3 (Voting N=30)
    ├── Phase 3c: H9 (Diversity)
    └── Phase 3d: H2 (Two-Stage)
        ↓
Phase 4: H6 (Flash→Pro Transfer)
    ↓
Phase 5: Exploratory (H10-H15 as triggered)
```

---

## Status Key

| Status | Meaning |
|--------|---------|
| Pending | Not yet started |
| In Progress | Currently executing |
| Complete | Execution finished, analysis done |
| Deferred | Postponed to future work |

---

## Related Documents

- **Preregistration**: `preregistration.md` — Full hypothesis specifications
- **Execution plan**: `execution-plan.md` — Operational sequencing
- **Decisions log**: `decisions-log.md` — Rationale for key decisions
- **Config schema**: `prompts/README.md` — Configuration file documentation
