# Pre-patch retest detections, 2026-03-21 copies

> **Last revised**: 2026-10-05 (original publication, Session 161). See
> [§ Changelog](#changelog) for revision history.

**What this is.** 85 retest detection GeoJSONs as they stood on 2026-03-21,
when a bootstrap-CI working copy was made in `~/cc-scratch/bootstrap-cis/`
on sapphire (untracked, outside the repository). They differ from the
repository's versions of the same files under `outputs/retest/`, which git
first tracked on 2026-04-15 (`3d22184d6`); the scratch directory was the only
copy of these earlier versions. Archived at the PI's request, Session 161
(2026-10-05), during the D42 class B work.

**Why they matter.** Some committed March pairwise artefacts (the PV pairwise
file v1 and the Phase 3a HIGH-text pairwise file) were computed from this
working copy; their committed outputs are byte-identical to the outputs left
in it (`reports/d42-implementation-2026-10-05-scripts/moved-inputs.md`).
Re-testing them on the inputs they actually used needs these files.

**How they differ.** Every one has fewer detections than the repository
version: between 1 and 119 fewer per file, 464 in all. That is consistent with
detections added to the files after 2026-03-21 (for example by a recovery
pass), but the cause was not verified here.

**Layout.** Paths mirror `outputs/retest/` (for example
`phase3a/track1-image/T0.3/run_N/…`); file bytes and modification times are
preserved (`cp -p`). By phase: Phase 3a track 1 image 44, Phase 3a track 2
text 4, Phase 3a HIGH text 3, Phase 3a replication 1, Phase 3c text 4,
Phases 2a-2e 29.

**`scratch-inventory.md5`.** MD5 of every file in the scratch directory (570
files, excluding its virtual environment and bytecode cache) as of
2026-10-05, so the remaining contents (371 retest files identical to the
repository, the PV crops, results and sweeps, and the scripts and logs) are
recorded even though they stay outside the repository.

## Changelog

### 2026-10-05 — Original publication (Session 161)

Archived from `~/cc-scratch/bootstrap-cis/data/retest/` on sapphire; the
scratch directory itself is left in place.
