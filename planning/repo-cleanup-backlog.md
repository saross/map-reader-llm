# Repository Cleanup Backlog

**Status**: Active backlog for pre-publication repo cleanup.
**Purpose**: Centralised list of cleanup items accumulated during
intensive development. This repo will be published alongside the
paper and must be legible, internally consistent, and navigable by
external readers.

**Plan**: Tackle these in a dedicated cleanup session using a
repo-cleanup agent/skill (to be developed, will be reused across
repos). Do NOT address these ad-hoc — batch them for a focused pass.

---

## `results/` — Accumulated evaluation artefacts

The results directory has grown organically with several parallel
evaluation pipelines. Needs rationalisation.

### Duplicate / superseded evaluation results

- `results/h11-384-pv-diagnostic/` — older PV sweep results, partially
  superseded by `results/phase3a-image-matrix/`. Determine which are
  still referenced vs which are safe to archive.
- `results/paper-eval/` — has `pv/`, `consensus-sweep/`, etc. Some
  overlaps with newer results. Verify what's still current.
- `results/phase3a-consensus/` — contains `track1-image/`,
  `track2-text/`, `replication/` from earlier sessions. The new
  Phase 3a image matrix is in `results/phase3a-image-matrix/`.
  Relationship between the two needs clarification or consolidation.
- `results/retest/` — older retest evaluations. Much may be
  superseded by the new leaderboard outputs in `results/leaderboard/`.
- `results/cross-hypothesis-library/` — pairwise matrix from Obs 240.
  Keep but verify it's referenced from the paper.

### Old leaderboard

- `results/paper-tables/leaderboard_tiers_20m.md` — the original
  manually-constructed leaderboard. Will be superseded by the new
  `results/leaderboard/era{1,2,3}/` outputs. Archive once new
  leaderboards are validated.

> **Note 2026-05-01**: the per-architecture leaderboard tree at
> `results/leaderboard/per-architecture/` (built in Sessions 79-80,
> continuity doc §"Session 80 closure") is the canonical future
> leaderboard path. Old `results/paper-tables/leaderboard_tiers_20m.md`
> and similar single-buffer / single-architecture leaderboards should
> be archived in the dedicated cleanup session.

### Mixed naming conventions

- Some files use `leaderboard_tiers_20m.md`, others `sweep_2d.json`,
  others `evaluation.md`. Standardise filenames across eras.
- Directory slugs are inconsistent (e.g., `fh-text-n5` vs
  `flash-high-image-n5` vs `flash-minimal-text-n30-t07`).

## `outputs/` — Detection artefacts

### Archive / remove

- `outputs/h11/pv-diag-256/` — 256 px pilot directory flagged in
  session 70 as untracked but not committed. Verify contents, archive
  or delete.
- `outputs/h8-v2/*/crops/` — crop image directories that weren't part
  of the original commit. Verify these are regenerable and covered by
  `.gitignore`.
- `outputs/h10/evaluation-v2/pool_{020,160}_hp4hn4/crops/` — same as
  above.
- `outputs/retest/phase3a-high/track1-image/` — the empty
  run directories from the originally-planned 512 px experiment
  (E53). Now superseded. Archive with a README explaining the
  relationship to E53.

### Verifier crop directories

- Every condition's `verified-v1-*/crops/candidate_*.png` — large
  number of small PNG files. Verify the `.gitignore` excludes these
  and only the `candidate_manifest.json` is tracked.

### Consensus file naming

- H11 conditions use a mix of conventions:
  - `consensus/consensus_t1.geojson` (merge_passes standard)
  - Shared directory with `*-NofM.geojson` (H11 era)
  - `consensus-n5/consensus_t1.geojson` (Phase 3a N=5 sweep)
- Proposal: converge on `consensus/consensus_tN.geojson` everywhere
  and archive the NofM files to a documented legacy location.

## `scripts/` — Script audit

### One-off analysis scripts

Identify scripts that were one-off analyses and archive them.
Candidates:

- `scripts/summarise_phase3a_matrix.py` — bespoke for Phase 3a.
  Used once. Consider whether to keep or fold into
  `analyse_consensus_sweep.py`.
- `scripts/apply_fdr_h8v2.py`, `apply_fdr_h12v2.py` — hypothesis-
  specific wrappers. Are they still used, or superseded by
  `build_tiered_leaderboard.py`?
- `scripts/run_h12_cross_analysis.sh` — one-shot cross-hypothesis
  sweep. Archive or document.
- `scripts/run_phase3a_image_analysis.sh`, `run_phase3a_overnight_sync.sh`,
  `run_phase3a_image_matrix.sh` — session-specific launchers.
- Any `11maps-*.sh`, `55maps-*.sh`, `overnight-*.sh`, `sapphire-*.sh`
  that were single-use.

### Name sprawl

- Multiple `build_*.py`, `analyse_*.py`, `run_*.py` prefixes —
  standardise naming conventions. Decide between `analyse`
  (UK/AU) and `analyze` (no, already UK).
- Some scripts are test scripts, some are CLI scripts. Separate
  tests under `tests/` cleanly.

### Deprecated / superseded logic

- `scripts/4_detect_mounds_batch.py` — numeric prefix from an older
  pipeline ordering convention. Remove prefix or keep for historical
  reference?
- `scripts/5_verify_crops.py` — similar.
- Several scripts load the condition inventory; standardise on a
  shared loader.

## `inputs/` — Input data

### Tile sets

- `inputs/tiles/` (512 px) and `inputs/tiles_384/` (384 px) —
  duplicated tile content at different resolutions. Document which
  experiments used which, confirm both are still needed.
- `inputs/tiles_256/` — pilot size, may be archivable.

### Bounds files

- `inputs/vectors/bounds/` has several files at different scopes.
  Document which is used for which era (Era 1 → 340 tiles, Era 2 →
  487, Era 3 → 327).

### Manifests

- Multiple manifest files per tile size. Verify that gitignored vs
  tracked manifests are internally consistent.

## `docs/` — Documentation

### Working notes

- `docs/notes/reflections/working-notes.md` is now ~10,700+ lines
  with 246+ observations. Still readable for context but needs an
  index or split by phase for the published repo.
- `docs/notes/reflections/session-log.md` — similar.
- Decide what's supplemental material for the paper vs internal
  research notes vs removable.

### Preregistration + errata

- Current structure is good but verify all errata (E1–E53) are
  properly cross-referenced and the preregistration still reflects
  the actual protocol.

### Methodology docs

- Several README-like files in `docs/methodology/`. Verify they're
  all current and eliminate duplication.

## Condition inventory schema

- `planning/condition-inventory.json` has 150 entries but the schema
  has accumulated fields. Some conditions have `consensus_files`,
  others don't. Some have `library` field, others don't. Define a
  canonical schema and migrate.
- Field naming is inconsistent (`K` vs `k`, `T` vs `temperature`,
  `consensus_built` vs would-be `has_consensus`).
- Consider a JSON Schema for validation.

## Git state

- Multiple untracked output directories (crops/, some consensus/).
  Confirm `.gitignore` is complete and clean up.
- Branch state is main-only. Verify no stale branches on remote.

## Tests

- `tests/` exists but may be thin. Confirm coverage of key scripts
  (`merge_passes.py`, `evaluate_detections.py`, the new
  `build_tiered_leaderboard.py`, `build_all_consensus.py`).

## README / publication readiness

- Top-level `README.md` — verify it reflects the current state of the
  repo (experiments completed, how to reproduce, where the paper is).
- `CITATION.cff` — check version is current and authors are correct.
- `pyproject.toml` / `requirements.txt` — pin versions consistently.

## Session-specific artefacts

### Session 70 (current session)

- The Phase 3a image matrix experiment should be clearly documented
  in session log and reflections.
- E53 should be cross-referenced from the Phase 3a results directory.
- Obs 243–248 (secondary effects + verifier reversal) — verify
  they're linked from the relevant results files.

---

## Meta

**Next steps for this backlog:**

1. **Define a repo-cleanup agent or skill** that can be reused across
   projects. Should accept a backlog like this and execute items
   systematically.
2. Tackle items in rough priority order: publication-blocking first
   (naming consistency, old leaderboard deletion, untracked files
   audit), then readability (working notes index, methodology docs),
   then nice-to-haves (tests, version pinning).
3. Before any deletion, verify files are archived (per the CLAUDE.md
   "archive, never delete" policy) unless they're definitively
   regenerable temp files.

**Last updated**: 2026-04-17 (Session 70)
