# Hypothesis Tracking Matrix

**Purpose**: Map preregistered hypotheses to their experimental conditions, configs, and status.

**Last updated**: 2026-03-15

---

## Confirmatory Hypotheses (H1-H8)

| ID | Hypothesis | Factor | Phase | Status | Date |
|----|------------|--------|-------|--------|------|
| H1 | Modality/Elaboration Level | M/E | 2a | Complete | 2026-02-06 |
| H2 | Two-Stage Pipelines | Architecture | 3c/3d | **Complete** | 2026-03-11 |
| H3 | Consensus Voting | N, threshold | 3a | Complete | 2026-03-07 |
| H4 | Example Ordering | Ordering | 2e | Complete | 2026-02-12 |
| H5 | Negative Text Treatment | Text level | 2d | Complete | 2026-02-12 |
| H6 | Flash→Pro Transfer | Model | 4 | Not started | — |
| H7 | Temperature | T | 2b | Complete | 2026-02-08 |
| H8 | Library Composition/Scaling | Library size | 2c | Complete | 2026-02-09 |

---

## Exploratory Hypotheses (H9-H15)

| ID | Hypothesis | Factor | Tier | Status | Date |
|----|------------|--------|------|--------|------|
| H9 | Diversity Mechanisms | Text/Image/Temp diversity | A | Complete (implicit) | 2026-03-07 |
| H10 | Training Pool Size | Pool size | B | Not started (HP pool exhausted) | — |
| H11 | Tile Size Effects | Tile dimensions | B | Complete (384 pathway closed) | 2026-03-15 |
| H12 | HP:HN Ratio | Hard example ratio | B | Deferred (post-H10; HP pool exhausted) | — |
| H13 | Overlap/Stride Effects | Tile overlap | B | Not started (low priority) | — |
| H14 | Cross-Model Consistency | Provider | C | Deferred to future work | — |
| H15 | Cross-Model Voting | Multi-provider voting | C | Deferred to future work | — |

---

## Detailed Condition Mapping

### H1: Modality/Elaboration Level (Phase 2a) — COMPLETE

Tests how text presence and detail level affect detection performance.

**Status (2026-02-08)**: Phase 2a complete. Optimal modality/elaboration level
identified and carried forward into subsequent phases.

| Condition | M/E Level | Text | Images | Config File | Instruction File |
|-----------|-----------|------|--------|-------------|------------------|
| H1-1 | Image-only | Minimal | Yes | `detect_image-only.json` | `detect_image-only.md` |
| H1-2 | Brief-text | Brief | No | `detect_brief-text.json` | `detect_brief-text.md` |
| H1-3 | Brief-text+image | Brief | Yes | `detect_brief-text-image.json` | `detect_brief-text-image.md` |
| H1-4 | Verbose-text | Verbose | No | `detect_verbose-text.json` | `detect_verbose-text.md` |
| H1-5 | Verbose-text+image | Verbose | Yes | `detect_verbose-text-image.json` | `detect_verbose-text-image.md` |

---

### H2: Two-Stage Pipelines (Phase 3c/3d) — COMPLETE

Tests whether two-stage architectures improve over single-stage detection.

**Status (2026-03-11)**: Complete. The preregistered null prediction (two-stage
will not improve) was **contradicted** with large effect size. Phase 3c pilot
exceeded the GO criterion (ΔF1 ≥ 0.05) by a 2× margin, achieving +0.09 to
+0.14 F1 improvement with proposer-verifier architecture.

Phase 3d triggered exploratory extensions were comprehensive:

- Phase 3c pilot (Session 43): 3 verifier strategies × 2 tracks
- Phase 3d Experiments A–D (Sessions 44–48): provenance preamble, visual
  examples, temperature sweeps, cascaded verification
- Phase 3d Experiment E (Session 48): text proposer ablation — negative result
  confirming baseline is near capability frontier
- H11 factorial (Session 50): 3 strategies × 2 tracks at 384 tiles

**Best result**: F1=0.796 (adversarial verifier, text-only, 512 tiles) — but
see Observation 163 regarding model drift and the corrected v2 result
(F1=0.732) obtained after config audit.

| Condition | Architecture | Verifier Strategy | Best F1 |
|-----------|--------------|-------------------|---------|
| Single-stage baseline | N/A | N/A | 0.660 |
| Proposer-verifier | Coarse-to-fine | Adversarial (text-only) | 0.732 (v2 corrected) |
| Proposer-verifier | Coarse-to-fine | Standard (text-only) | 0.768 (pre-correction) |
| Proposer-verifier | Coarse-to-fine | Checklist (text-only) | 0.782 (pre-correction) |

**Note**: Fine-to-coarse (H2-C) was not tested — the coarse-to-fine results
were strong enough that context expansion was deprioritised.

---

### H3: Consensus Voting (Phase 3a) — COMPLETE

Tests voting pool sizes and thresholds. No separate configs — voting is
post-hoc analysis.

**Status (2026-03-07)**: Complete. Consensus voting confirmed to improve over
single-run baseline for both tracks. N=30 at T=0.7 optimal. Detailed results
in `results/phase3a-consensus/`.

**Note (2026-03-15)**: The Phase 3a metadata files in `track2-text-high/`
incorrectly record `thinking_level: minimal` due to a metadata-recording bug
(the script captured the config file default rather than the actual API
parameter). The directory label "HIGH" is correct — the runs did use HIGH
thinking at the API level (see Observation 141). A clean replication
(2026-03-15) with properly controlled configs confirmed the direction:
HIGH F1=0.735 vs minimal F1=0.699 (+3.6 pp).

| Pool Size | Source | Thresholds Tested |
|-----------|--------|-------------------|
| N=5 | Runs 1-5 or 6-10 | 1, 2, 3, 4, 5 |
| N=10 | All 10 runs | 1, 2, ..., 10 |
| N=30 | Extended (20 additional runs) | 1, 2, ..., 30 |

---

### H4: Example Ordering (Phase 2e) — COMPLETE

Tests positioning of canonical vs hard examples.

**Status (2026-02-12)**: Complete. No significant ordering effect after FDR
correction. Config-default (canonical-first) ordering carried forward.

| Condition | ID | Canonical Position | Config Pattern |
|-----------|----|--------------------|----------------|
| Canonical-first | H4-A | First (positions 1-6) | `detect_*.json` (base configs) |
| Canonical-last | H4-B | Last (final positions) | `detect_*_canonical-last.json` |
| Random | H4-C | Shuffled | `detect_*_random-order.json` |

**Triggered exploratory (H4b)**: If H4 significant, test HP-first vs HN-first
ordering within hard block. **Not triggered** — H4 showed no significant
effect (2026-02-12).

---

### H5: Negative Text Treatment (Phase 2d) — COMPLETE

Tests whether exclusion guidance text in the system instruction reduces false
positives. Three levels tested at the carried-forward optimal M/E per track
(OFAT, not full factorial). See Decision 17 and Erratum E28.

**Status (2026-02-12)**: Complete. H5=minimal optimal for both tracks. Carried
forward to subsequent phases.

**Instruction text adaptation**: Terse and verbose instruction files were
modified to remove references to non-existent HN reference images (HN
excluded after Phase 2c). Exclusion *descriptions* (what not to detect)
retained as domain knowledge. Minimal instruction unchanged (serves as
baseline from prior phases).

| Condition | H5 Level | Exclusion Text | Track 1 Config (image) | Track 2 Config (text-only) |
|-----------|----------|----------------|------------------------|---------------------------|
| H5-A | Minimal | No exclusion text | `library_plus-hp.json` | `detect_brief-text.json` |
| H5-B | Terse | Brief "do not mark" list | `library_plus-hp_terse.json` | `detect_brief-text_terse.json` |
| H5-C | Verbose | Detailed per-type criteria | `library_plus-hp_verbose.json` | `detect_brief-text_verbose.json` |

**Dual-track OFAT design** (4 net new cells, 2 per track):

| Track | M/E Level | H5=Minimal | H5=Terse | H5=Verbose |
|-------|-----------|------------|----------|------------|
| Track 1 (image) | brief-text-image | Reuse Phase 2c | **New** | **New** |
| Track 2 (text) | brief-text | Reuse Phase 2b T=0.0 | **New** | **New** |

**Preregistered design was**: 3×3 factorial (3 image-using M/E × 3 H5).
Simplified to single-factor OFAT at carried-forward M/E per Decision 17.

---

### H6: Flash→Pro Transfer (Phase 4) — NOT STARTED

Tests whether Flash-optimal config transfers to Pro. OFAT sensitivity testing.
This is the only untested confirmatory hypothesis.

| Factor | Tests | Decision Rule |
|--------|-------|---------------|
| M/E | 2 adjacent levels | Adjust if Δ ≥ 0.03 F1 |
| H5 | 2 alternatives | Adjust if Δ ≥ 0.03 F1 |
| T | 2 adjacent temperatures | Adjust if Δ ≥ 0.03 F1 |
| O | 2 alternative orderings | Adjust if Δ ≥ 0.03 F1 |

---

### H7: Temperature (Phase 2b) — COMPLETE

Tests temperature effect on detection performance.

| Condition | Temperature | Rationale |
|-----------|-------------|-----------|
| H7-1 | 0.0 | Minimum (deterministic) |
| H7-2 | 0.3 | Low variance (evidence for visual detection) |
| H7-3 | 0.7 | Moderate variance |
| H7-4 | 1.0 | Vendor default |
| H7-5 | 1.3 | Above default |

**Temperature is a runtime parameter** — no separate config files needed.

**Result (2026-02-08)**: T=0.0 optimal for both tracks. FDR-significant pairwise
differences: 6/10 comparisons (Track 1), 4/10 comparisons (Track 2). T=0.0 carried
forward as the optimal temperature setting for subsequent phases.

---

### H8: Library Composition and Scaling (Phase 2c) — COMPLETE

Tests library component effects and scaling.

**Status (2026-02-09)**: Phase 2c complete (Track 1 image-using only; Track 2
text-only skipped because library composition is inherently visual). plus-hp
selected as optimal library (F1=0.609). No pairwise comparisons significant
after FDR correction, but consistent directional gradient: more positive
examples = better performance. Carried forward to Phase 2d.

| Condition | ID | Canon+ | Canon- | HP | HN | Null | Total | Config File |
|-----------|----|--------|--------|----|----|------|-------|-------------|
| Pure Positive Canon | H8-1 | 4 | 0 | 0 | 0 | 3 | 7 | `library_pure-positive-canon.json` |
| Canonical | H8-2 | 4 | 2 | 0 | 0 | 3 | 9 | `library_canonical.json` |
| +HP | H8-3 | 4 | 2 | 4 | 0 | 3 | 13 | `library_plus-hp.json` |
| Scale-4 | H8-4 | 4 | 2 | 2 | 2 | 3 | 13 | `library_scale-4.json` |
| Scale-8 | H8-5 | 4 | 2 | 4 | 4 | 3 | 17 | `library_scale-8.json` |
| Scale-16 | H8-6 | 4 | 2 | 8 | 8 | 3 | 25 | **DEFERRED** |
| Scale-32 | H8-7 | 4 | 2 | 16 | 16 | 3 | 41 | **DEFERRED** |

**Note (2026-02-02)**: Scale-16 and Scale-32 are deferred because the HP pool is
structurally exhausted at 4 recognition failures (>50m threshold). These conditions
collapse to Scale-8 under the 1:1 HP:HN constraint. Deferred to post-H10 when
calibration tile expansion may yield additional recognition failures. See Decision 11
in decisions-log.md.

**Planned contrasts**:

- C1: Pure Positive Canon → Canonical (Canon- effect)
- C2: Canonical → +HP (HP effect)
- C3: +HP → Scale-8 (HN effect)
- S1: Scale-4 → Scale-8 (initial scaling)
- ~~S2: Scale-8 → Scale-16 (mid scaling)~~ — deferred (post-H10)
- ~~S3: Scale-16 → Scale-32 (ceiling)~~ — deferred (post-H10)
- B1: +HP vs Scale-4 (composition at matched size)

---

### H9: Diversity Mechanisms (Phase 3c — Exploratory) — COMPLETE (implicit)

Tests whether diversity in prompts, images, or temperature improves voting.

**Status (2026-03-07)**: Implicitly tested via Phase 3a parameter variation.
Prompt/parameter diversity does not improve consensus — confirmed null result.
The formal H9-A through H9-E conditions were not run as separate experiments;
the finding emerged from Phase 3a's multi-temperature, multi-run design which
inherently tested temperature diversity (H9-D).

| Condition | Text | Images | Temperature | Description |
|-----------|------|--------|-------------|-------------|
| H9-A | Fixed | Fixed | Fixed | Baseline (identical passes) |
| H9-B | Varied | Fixed | Fixed | Text diversity only |
| H9-C | Fixed | Varied | Fixed | Image diversity only |
| H9-D | Fixed | Fixed | Varied | Temperature diversity only |
| H9-E | Varied | Varied | Varied | Full diversity |

**Note (2026-02-02)**: H9 runs as **HN-diversity-only** for image diversity (H9-C).
HP channel is frozen: 4 slots, 4 examples, every HP appears in every pass. Only HN
examples rotate across passes. HP diversity is untestable due to pool exhaustion (only
4 recognition failures exist). HN rotation is the more important diversity dimension
given that FPs outnumber FNs ~23:1. See Decision 11 in decisions-log.md.

---

## Execution Dependency Chain

```text
Phase 0: Preparation
    ↓
Phase 1: Library + Text Construction
    ↓
Phase 2a: H1 (M/E) → optimal M/E                    ✓ COMPLETE
    ↓
Phase 2b: H7 (Temperature) → optimal T               ✓ COMPLETE (T=0.0)
    ↓
Phase 2c: H8 (Library) → optimal library              ✓ COMPLETE (plus-hp)
    ↓
Phase 2d: H5 (Negative Text) → optimal text           ✓ COMPLETE (minimal)
    ↓
Phase 2e: H4 (Ordering) → optimal ordering             ✓ COMPLETE (no effect)
    ↓
    ├── Phase 3a: H3 (Voting N=30)                     ✓ COMPLETE
    ├── Phase 3c: H9 (Diversity — implicit)            ✓ COMPLETE
    └── Phase 3c/3d: H2 (Two-Stage)                    ✓ COMPLETE
    ↓
    └── H11 (Tile Size — exploratory)                  ✓ COMPLETE (384 closed)
    ↓
Phase 4: H6 (Flash→Pro Transfer)                       ○ NOT STARTED
    ↓
Phase 5: Exploratory (H10-H15 as triggered)            ○ H10-H13 not started
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
