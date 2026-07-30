# Empirical GS sub-phase mapping

> **Last revised**: 2026-07-30 (quoted "1 of 10" FDR-survivor figure flagged as a source misreport; correct figure 0 of 10). See [§ Changelog](#changelog) for revision history.

Empirical mapping of `results/gold-standard-*` and `results/gs-*` / `*-gs4`
sub-directories to their evaluation tile pools, with anchored evidence
from in-tree files and git history. Goal: reconcile the user's
"~60-tile" recollection with the project's canonical "Era 1 / 2 / 3"
taxonomy, and tag each subdirectory accordingly.

## 1. Tile pool definitions (canonical)

The authoritative reference is `results/evaluation-scopes.md` (commit
introducing it: `6d804934`, 2026-04-16). It defines three nested,
zero-tolerance-geographic test tile pools on the 4-map gold-standard
sub-corpus (K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1; UTM Zone
35N / EPSG:32635). Verified inline (`evaluation-scopes.md:30–34`):

| Label | Tile size | Test tiles | Area (sq km) | GT mounds | Bounds manifest |
|---|---|---:|---:|---:|---|
| **Era 1** (pre-H11, H1–H9 retest) | 512 px | **340** | 1,751 | 539 | `inputs/vectors/bounds/full_evaluation_bounds.geojson` |
| **Era 2** (H11, PV diagnostic, N-sweep) | 384 px | **487** | 1,416 | 435 | `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` |
| **Era 3** (post-H10 v2: H8/H10/H12 v2) | 384 px | **327** | 1,034 | 319 | `inputs/vectors/bounds/384/h10_test_bounds.geojson` |

Strict nesting: Era 3 ⊂ Era 2 ⊂ Era 1 at 100.000% area containment
(`evaluation-scopes.md:43–56`). Coverage: Era 2 = 80.8 % of Era 1;
Era 3 = 73.0 % of Era 2.

In **all three eras**, a calibration footprint is excluded from the
test pool. Era 1 excludes the original 20-tile calibration seed
(`evaluation-scopes.md:73–80`). Era 2 excludes the same geographic
footprint re-projected onto the 384-px grid
(`evaluation-scopes.md:82–90`). Era 3 additionally excludes the
160-tile `pool_160` hard-example-mining footprint
(`evaluation-scopes.md:92–104`).

### Reconciling the user's "~60-tile" recollection

The user's "~60 tiles" refers to an **earlier and distinct evaluation
pool** — pre-dating Era 1 — used in the exploratory Phase 2 work
(approximately Sessions 17–52, up to 2026-03-15). Anchor:
`working-notes.md:3383–3406` ("Transition to Production Runs (Session
52)"), which records the explicit shift from the "60-tile validation
holdout" to the **340-tile** corpus (= Era 1) on 2026-03-15, citing
"wide confidence intervals (F1 CI width ~0.22)" and "only 1 of 10
Phase 2a comparisons" surviving FDR correction (the quoted survivor
figure is a misreport in the source block — the correct figure is 0 of
10, `results/phase2a-analysis-report.json`; corrected 2026-07-30, see
Obs 372 and the E36 correction block). Prior obs entries in
`working-notes.md:1732, 1740, 1756, 2176, 2306` corroborate the
60-tile pool's identity: it was `validation_bounds.geojson` (legacy,
not the present-day 384/full_evaluation_bounds), 20-tile calibration
held out separately.

**None of the GS subdirectories in scope use the 60-tile pool.** All
nine post-date the 2026-03-15 transition. The methodological "earlier
phase / later phase" framing the user described therefore reduces, in
this set, to **Era 3 (327-tile, bounds-filtered for v2 library-design
comparability) vs Era 2 (487-tile, full scope)**, not 60-tile vs
larger. The `-era2` suffix is the explicit signal of the Era 2
(broader scope) re-evaluation.

The user-memory entry `feedback_384px_scope_preference` (referenced in
the briefing) is consistent: it states the preference for the 487-tile
Era 2 pool over the 327-tile Era 3 pool on the 4-map GS corpus
"unless the analysis specifically requires Era 3's pool_160 exclusion".

## 2. Per-subdirectory mapping

| Subdir | Tile pool | Evidence | Confidence |
|---|---|---|---|
| `gold-standard-attractor-pull/` | **Era 2 (487-tile)** | `attractor-pull-gs.json:17` — `"scope": "Era 2, 487-tile gold-standard 4-map evaluation"` | High |
| `gold-standard-extended-buffer-sweep/` | **Era 3 (327-tile)** | `evaluation.json:26` — `"n_tiles": 327` (all buffers); `extended-buffer-report.md:60` — `"inputs/vectors/bounds/384/h10_test_bounds.geojson (327 evaluation tiles, 4 maps; Era 3 scope)"`. `with-mcc/evaluation.json` also reports `n_tiles: 327` | High |
| `gold-standard-extended-buffer-sweep-era2/` | **Era 2 (487-tile)** | `evaluation.json:5,26` — `"label": "gold-standard-text-high-era2"`, `"n_tiles": 487`; commit `aa36b638` (2026-04-24) — "GS text-HIGH Era 2 companion + 487-tile leaderboard cell" | High |
| `gold-standard-image-extended-buffer-sweep/` | **Era 2 (487-tile)** | `evaluation.json:5,26` — `"label": "gold-standard-image-flash-high-t0.7-n10-t7-era2"`, `"n_tiles": 487` | High |
| `gold-standard-subtype-classification/` | **Era 2 (487-tile)** | `run_manifest.json:19` — `"bounds": "inputs/vectors/bounds/384/full_evaluation_bounds.geojson"`; `report.md:50,283` reiterates the same bounds path. Per `evaluation-scopes.md:33`, that bounds file defines Era 2 | High |
| `gs-125m-fp-side-6-crop-review/` | **Era 2 (487-tile), derivative** | `README.md:73` — cohort is filtered from `results/gs-fp-classification/fp_classifications.json` (six > 125 m FPs); upstream is Era 2 full-scope (see next row) | High |
| `gs-fp-classification/` | **Era 2 (487-tile), full-scope** | `report.md:14,30` — classifier applied to all 371 detections in `outputs/h11/gold-standard-v2/verified-v1/verified_detections_full-scope.geojson`; `category_distribution.json:3` — `"n_total_classified": 371`. Per `evaluation-scopes.md:134`, the 371-detection count is the pre-recovery Era 2 (487-tile) verifier output (post-recovery 380); the file suffix `_full-scope.geojson` matches the full Era 2 evaluation area, not the 327-tile h10 filter | High |
| `gt-duplicate-review-gs4/` | **4-map sheet area (not Era-tagged)** | `gt-duplicate-diff.md:5–7` — operates on raw student GT points (560 → 556 after merges) across the 4 GS sheets; no tile-pool restriction. Commit `a8b576d5` says "560 Hairy-filtered student features in the 4 GS map sheets". The output, `student-mounds-gs-4maps-reviewed.geojson`, is consumed by `student-gt-fn-rate-analysis-gs4/` (next row) | High |
| `student-gt-fn-rate-analysis-gs4/` | **4-map active-sheet area (trapezoidal graticule); not Era-tagged** | `report.md:78` — `"Bounds file: inputs/vectors/bounds/gs-4maps-active-area-bounds.geojson"`; this clips to the 4 sheets' cartographic neat-line, not a tile pool. Curator 569 GT + cleaned student 556 GT, with 539 retained after clipping | High |

### Note on the GT-comparator subdirectories

`gt-duplicate-review-gs4/` and `student-gt-fn-rate-analysis-gs4/` are
**not detection-pipeline evaluations** — they are curator-vs-student
GT comparisons on the 4 GS sheets. They operate on the full sheet
active area rather than on a tiled evaluation pool, so the Era 1 / 2
/ 3 taxonomy does not apply to them. They are correctly tagged "4-map
gold-standard sub-corpus" but not to a specific Era. `evaluation-
scopes.md:131` confirms this orthogonality for the analogous
subtype-classification work: "a separate dedicated sub-corpus; document
this explicitly rather than shoehorn into an Era".

## 3. Chronology

Verified from git log and `working-notes.md`:

1. **Pre-2026-03-15 — 60-tile validation pool** (`validation_bounds.geojson`).
   Exploratory Phase 2 work. Anchors: `working-notes.md:1732, 1740, 1756`;
   commit `4d011a83` (`feat(preregistration): Expand holdout set from 20
   to 60 tiles`) and `496dde29` (`fix(inputs): Regenerate
   validation_bounds.geojson from correct manifest (E19)`).

2. **2026-03-15 — transition to Era 1 (340-tile, 512 px)**. Driven by
   the 60-tile pool's insufficient power. Anchor: `working-notes.md:3383–3406`
   ("Transition to Production Runs (Session 52)").

3. **Approx. 2026-03-21 → 2026-04-16 — Era 2 (487-tile, 384 px)
   established**. H11 tile-size study moved evaluation to 384 px; the
   487-tile clean set is the post-calibration test pool. Anchors:
   project-memory entries dated 2026-03-21 and 2026-03-26 (search
   `feedback_384px_scope_preference` and the bounds-reconciliation
   memory at `memories.jsonl:11791`: "consensus results (20m) evaluated
   on validation_bounds.geojson (240 tiles, 242 mounds) while PV
   results (20m) evaluated on full_evaluation_bounds.geojson (487 tiles,
   435 mounds)... re-evaluate all conditions on full 487-tile bounds").

4. **2026-04-16 — three-Era taxonomy formalised**. Commit `6d804934`
   introduces `results/evaluation-scopes.md` and the Obs 242 decision
   in `working-notes.md:10478–10554` ("Leaderboard Construction Strategy:
   Era-First Then Consolidated via Spatial Re-Tiling").

5. **2026-04-16 → 2026-04-30 — Era 3 (327-tile) bounds in active use**
   for H8 v2 / H10 v2 / H12 v2 closure and the original GS extended-
   buffer sweep. Most of `results/gold-standard-extended-buffer-sweep/`
   commits land in this window (e.g. `743e59a8` 2026-04-24, `76b6592f`
   2026-04-28, `85f11501` 2026-04-30; `git log --follow` output above).

6. **2026-04-24 → 2026-05-03 — Era 2 companions added**. Commit
   `aa36b638` (2026-04-24) creates the `-era2` companion for the
   extended-buffer sweep. The 2026-05-03 GS-v2 recovery (commits
   `90890ae9..c6023034`) lifts the Era 2 verifier count from 371 to
   380 detections and is propagated through both extended-buffer-sweep
   variants and the subtype-classification report. Anchors:
   `extended-buffer-report.md:14–23, 68`; `evaluation-scopes.md:134`.

So in the user's mental model, the "earlier (smaller subset)" phase
inside the GS programme corresponds to **Era 3 (327 tiles)** — the
v2-library-design comparator scope, which is genuinely a strict subset
of the later Era 2 (487 tiles) re-evaluations. The user's "~60 tiles"
recollection is a separate (pre-Era) phase that none of the listed
subdirectories share.

## 4. Anomalies and open questions

- **`gold-standard-image-extended-buffer-sweep/` lacks the `-era2`
  suffix but is Era 2 by content.** The internal label
  `"gold-standard-image-flash-high-t0.7-n10-t7-era2"` and `n_tiles:
  487` are unambiguous. The directory name is inconsistent with the
  sibling `gold-standard-extended-buffer-sweep-era2/`. If a uniform
  naming convention is desired this directory should probably be
  renamed (or its sibling un-suffixed). Flagging, not recommending — the
  user should decide.

- **`gold-standard-extended-buffer-sweep/with-mcc/`** is an Era 3
  re-run with MCC added; `n_tiles: 327` confirmed in
  `with-mcc/evaluation.json:26`. Same scope as parent. Not a separate
  pool.

- **`gs-fp-classification/` pre-dates the 2026-05-03 recovery**: it
  classifies 371 detections, the pre-recovery Era 2 count. After the
  recovery, the canonical Era 2 verifier output has 380 detections.
  The 9 extra detections have not been classified. Whether this
  matters depends on downstream use; flagging for the user.

- **The `validation_bounds.geojson` 60-tile pool** referenced in early
  obs entries is `archive/outputs-pre-retest-60-tile/preliminary-
  results/validation_bounds.geojson` (verified with `find ... -name
  '*bounds*geojson'`). It is correctly archived rather than deleted,
  per the project's preservation policy.

- **240-tile pool**: `memories.jsonl:11791` mentions a "240 tiles, 242
  mounds" pool used briefly during reconciliation. This is a third
  pre-Era pool not represented in any of the GS subdirectories in
  scope, and is not the same as the 60-tile or the 487-tile pools.
  Flagging for completeness; not relevant to any current artefact.

- **The `pool_160` exclusion**: Era 3 = Era 2 minus 160 calibration
  tiles (487 − 160 = 327). Verified at `evaluation-scopes.md:92–104`.
  This is the geographically-separate hard-example-mining footprint,
  not the same area as the original 20-tile calibration that all three
  Eras share.

## 5. References (anchors used)

- `/home/shawn/Code/map-reader-llm/results/evaluation-scopes.md` (whole file; canonical Era definitions)
- `/home/shawn/Code/map-reader-llm/docs/notes/reflections/working-notes.md` lines 1732, 1740, 1756, 2176, 2306, 3383–3406, 10478–10554
- `/home/shawn/Code/map-reader-llm/results/gold-standard-extended-buffer-sweep/extended-buffer-report.md` lines 14–23, 60–72
- `/home/shawn/Code/map-reader-llm/results/gold-standard-extended-buffer-sweep/evaluation.json` line 26
- `/home/shawn/Code/map-reader-llm/results/gold-standard-extended-buffer-sweep-era2/evaluation.json` lines 5, 26
- `/home/shawn/Code/map-reader-llm/results/gold-standard-image-extended-buffer-sweep/evaluation.json` lines 5, 26
- `/home/shawn/Code/map-reader-llm/results/gold-standard-subtype-classification/run_manifest.json` line 19
- `/home/shawn/Code/map-reader-llm/results/gold-standard-attractor-pull/attractor-pull-gs.json` line 17
- `/home/shawn/Code/map-reader-llm/results/gs-fp-classification/report.md` lines 14, 30; `category_distribution.json` line 3
- `/home/shawn/Code/map-reader-llm/results/gs-125m-fp-side-6-crop-review/README.md` line 73
- `/home/shawn/Code/map-reader-llm/results/student-gt-fn-rate-analysis-gs4/report.md` line 78
- `/home/shawn/Code/map-reader-llm/results/gt-duplicate-review-gs4/gt-duplicate-diff.md` lines 5–7; commit `a8b576d5`
- Git commits: `6d804934`, `aa36b638`, `4d011a83`, `496dde29`, `743e59a8`, `76b6592f`, `85f11501`, `90890ae9..c6023034`
- Project memory: `~/personal-assistant/memories/memories.jsonl` lines 10446, 10455, 11038, 11072, 11075, 11791, 11792, 11793

## Changelog

### 2026-07-30 — Quoted FDR-survivor figure flagged as source misreport (Session 121)

**Refresh trigger**: the Phase 1 verification campaign established that
the working-notes block this report quotes (§ 2's anchor,
`working-notes.md:3383–3406`) misreports the Phase 2a FDR outcome; PI
handling at `reports/verification/phase2-rulings-2026-07-30.md` § 1d.

| before | after |
| :--- | :--- |
| quoted "only 1 of 10 Phase 2a comparisons" surviving, unqualified | quotation retained, flagged as a source misreport; correct figure 0 of 10 (`results/phase2a-analysis-report.json`) |

What did NOT change: the tile-pool mapping itself, all nine subdir
assignments, and the Era taxonomy — the quoted figure was anchoring
evidence for the *timing* of the 60→340 shift, which stands. Companion
corrections: the E36 correction block, Obs 372, and
`reports/experimental-progression.md`.

### 2026-05-28 — Original publication

Initial empirical mapping of nine GS-related sub-directories under
`results/` to their evaluation tile pools, written to settle the
"earlier vs later" phase terminology question. Reconciled the user's
"~60 tile" recollection (a pre-Era exploratory pool, archived at
`archive/outputs-pre-retest-60-tile/`) against the project's canonical
Era 1 / Era 2 / Era 3 taxonomy formalised in
`results/evaluation-scopes.md` (commit `6d804934`). Of the nine
subdirs: 5 are Era 2 (487-tile), 1 is Era 3 (327-tile), 1 is an Era 3
extended report with an Era 2 companion (the bare and `-era2`
subdirs), and 2 are GT-comparator analyses on the 4-map sheet area
outside the Era taxonomy. No Era 1 subdirs in scope. No 60-tile
subdirs in scope. Commit hash for this addition: pending.
