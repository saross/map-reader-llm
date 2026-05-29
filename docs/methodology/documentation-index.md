# Documentation Index and Cross-Reference

**Purpose**: Navigate between the project's documentation sources. Each
source captures a different dimension of the research; this index shows
where information lives and how sources relate.

**Last updated**: 2026-03-15

---

## Document Map

| Document | What it captures | Numbering | Current range |
|:---------|:-----------------|:----------|:--------------|
| [Working notes](../notes/working-notes.md) | Observations — findings, mechanisms, lessons | Obs N | 1–165 |
| [Decisions log](preregistration/decisions-log.md) | Methodology decisions with rationale | Decision N | 1–21 |
| [Protocol errata](preregistration/protocol-errata.md) | Deviations, corrections, clarifications | EN | E1–E34 |
| [Hypothesis tracking](preregistration/hypothesis-tracking.md) | Hypothesis status and condition mapping | H1–H15 | All updated |
| [Execution checklist](preregistration/execution-checklist.md) | Phase completion tracking | Phases | Through 3d |
| Results files (`results/`) | Statistical outputs per phase | Per-phase | 2a–H11 |
| Study YAMLs (`studies/`) | Experiment definitions | Per-study | 22 files |
| [Session log](../notes/reflections/session-log.md) | Session-level activity summaries | Session N | 1–50 (gaps) |

---

## Phase → Document Cross-Reference

| Phase | Hypothesis | Results | Study YAML | Key Decisions | Key Errata | Key Observations |
|:------|:-----------|:--------|:-----------|:--------------|:-----------|:-----------------|
| 1 | — | `phase1-library/` | `phase1-library.yaml` | D1, D2 | E1–E6 | Obs 21–31 |
| 2a | H1 | `phase2a-*.md` | `phase2a-h1-modality.yaml` | D16 | E7–E8 | Obs 66–70 |
| 2b | H7 | `phase2b-*.md` + `retest/phase2b/analysis_summary.md` (paper-citation source) | `phase2b-h7-temperature*.yaml` | — | — | Obs 71–75 |
| 2c | H8 | `phase2c-*.md` | `phase2c-h8-library*.yaml` | D8, D11 | E9–E14 | Obs 76–82 |
| 2d | H5 | `phase2d-*.md` | `phase2d-h5-negtext*.yaml` | D17 | E28 | Obs 103 |
| 2e | H4 | `phase2e-*.md` | `phase2e-h4-ordering.yaml` | D18 | E29–E30 | — |
| 3a | H3 | `phase3a-consensus/` | `phase3a-h3-voting-*.yaml` | D6 | E32 | Obs 128–145 |
| 3a-repl | H3, H5 | `phase3a-replication/` | `phase3a-replication.yaml` | D20 | E34 | Obs 140–141 |
| 3c | H9 | `phase3c-diversity/` | `phase3c-h9-diversity-*.yaml` | — | — | Obs 147–149 |
| 3d | H2 | `phase3d-*.md` | `phase3d-h2-twostage.yaml` | D3 | E33 | Obs 150–162 |
| H11 | H11 | `h11-tile-size-results.md` | `h11-384-*.yaml` | D19 | E33 | Obs 160–163 |
| FL pilot | — | — (failed) | — | D21 | — | Obs 164 |

---

## Decision → Evidence Cross-Reference

| Decision | Date | Topic | Observations | Errata |
|:---------|:-----|:------|:-------------|:-------|
| D1 | 2025-12-19 | Model selection (Gemini 3 Flash) | — | — |
| D2 | 2026-01-15 | Thinking level (minimal) | Obs 71 | — |
| D3 | 2026-01-20 | Two-stage pipeline (exploratory) | — | — |
| D4 | 2026-01-25 | Hard example selection criteria | Obs 76, 79, 80 | E8, E15 |
| D5 | 2026-01-26 | Temperature default (1.0) | — | — |
| D6 | 2026-01-27 | Consensus voting strategy | — | — |
| D7 | 2026-01-27 | Neutral filenames | — | — |
| D8 | 2026-01-28 | Scale-8 as default library | — | — |
| D9 | 2026-01-29 | Sequential OFAT design | — | — |
| D10 | 2026-01-30 | Bootstrap CIs with FDR | — | — |
| D11 | 2026-01-31 | 50 m threshold, HP pool exhaustion | Obs 78 | — |
| D12 | 2026-02-01 | Centre-pointing language | — | — |
| D13 | 2026-02-02 | VLM-calibrated prompt diagnostics | Obs 87 | E16 |
| D14 | 2026-02-03 | Visual appearance over identity | — | — |
| D16 | 2026-02-06 | Dual-track carry-forward | Obs 103 | E27 |
| D17 | 2026-02-11 | Phase 2d dual-track OFAT | — | E28 |
| D18 | 2026-02-12 | 4th ordering condition | — | E29, E30 |
| D19 | 2026-03-15 | Config v2 rerun | Obs 163, 165 | E33 |
| D20 | 2026-03-15 | Phase 3a replication | Obs 140, 141 | E34 |
| D21 | 2026-03-15 | Flash-Lite abandoned | Obs 164 | — |

---

## Observation Clusters (by theme)

### Model behaviour and capabilities

- Obs 28–31: Model grade impact, Flash vs Pro
- Obs 71: Thinking level calibration (single-pass)
- Obs 140–141: Thinking level under consensus (diversity dividend)
- Obs 164: Flash-Lite capability failure
- Obs 165: Model drift detection

### Consensus voting

- Obs 128–136: Determinism, pool sizing, threshold sensitivity
- Obs 160: Recall saturation at 384 tiles

### Proposer-verifier pipeline

- Obs 150–159: Two-stage verification, cross-modal union, experiment E
- Obs 162: Text-only vs image gap at different tile sizes

### Methodology and infrastructure

- Obs 76–82: Hard example curation, evaluation architecture
- Obs 87: VLM-calibrated diagnostics
- Obs 103: Dual-track design
- Obs 127: 429 status code unreliability
- Obs 163: Configuration drift as systematic risk

---

## Notes

- Decision 15 was skipped in the numbering (historical artefact)
- Observations are not strictly sequential by date — some were
  backfilled retroactively (Obs 102-145 written in Sessions 44-48
  covering work from Sessions 26-43)
- Session log has gaps at Sessions 6-26 and 45-47; information from
  these sessions is captured in results files and working notes
- **Phase 2b — split location is intentional, not a gap**: the
  carry-forward parameters live at
  `results/phase2b-carry-forward-parameters.md`, but the paper-citation
  analysis lives at `results/retest/phase2b/analysis_summary.md`
  (Session 75 closure, commit `e8c46809`). Phase 2b numbers also appear
  in `results/retest/retest-production-summary.md` § 4 for
  cross-reference. There is no top-level
  `results/phase2b-analysis-summary.md` — the analysis is under
  `retest/` rather than at the top level. Prior audits flagged this as
  "Phase 2b summary missing"; the file is not missing, it's at a
  non-obvious location.
- **Phase 3b — does not exist**: the original v2.0 stranded-factorial
  design had a Phase 3b (H9 Diversity, exploratory). The v2.9
  preregistration redesign absorbed Phase 3b into Phase 2e; H9
  Diversity work was subsequently redirected into the exploratory
  Phase 3c matrix at `results/phase3c-diversity/`. See
  `docs/methodology/preregistration/execution-plan.md` line 516
  ("Phase 3b: (Absorbed into Phase 2e)") and line 810 (v2.9 changelog).
  Prior audits flagged "Phase 3b absent"; the phase was retired, not
  forgotten.
