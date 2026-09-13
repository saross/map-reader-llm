# Null-exemplar and tile-count errata (E86, E87) — claims with anchors

> **Last revised**: 2026-09-13 (original publication, with the two errata).
> See [§ Changelog](#changelog) for revision history.

**Scope**: what was verified, recomputed, corrected and deliberately not done
when the two errata drafted in `map-reader-bench`
`wiki/planning/parent-errata-drafts.md` were inserted into this repository's
register as **E86** and **E87**. Every checkable claim below carries the file,
command or commit it came from. No Application Programming Interface (API) call
was made and nothing heavier than a few seconds of local JavaScript Object
Notation (JSON) arithmetic was run.

**Read the errata, not this, for the dispositions**:
`docs/methodology/preregistration/protocol-errata.md` §§ E86, E87.

## 1. What the two errata are

| | E86 | E87 |
|---|---|---|
| Defect | The three null few-shot exemplars were selected from a training set that was superseded and never rebuilt, so they were never entered into the calibration exclusion geometry | The registration's per-tile mound counts came from a bounding-box approximation of each sheet's georeferencing that never reads the raster affine |
| Type | Provenance defect in a model-visible artefact; scope of the exclusion | Correction of documented counts |
| Reaches a measured value? | **No** — 0 of 569 reference symbols lie in a null window | **No** — no hypothesis, run, board or paper figure reads the counts |
| Reaches the paper? | Yes — the clean-holdout claim in Methods § M.9 needed a qualifier | Yes, but not via the counts: the corpus-size sentences had carried 361 forward without E64 (ii) |
| Register position | Entry 86 of 87 | Entry 87 of 87 |

Numbering was collision-checked: the register held 85 entries before this
session and holds 87 after (`### E<n>` headings in
`docs/methodology/preregistration/protocol-errata.md`).

## 2. The provenance chain, re-verified commit by commit

Each row was re-read in this session with `git show <commit>:<path>`; the
drafts' commit hashes are this repository's commits and all five resolve.

| Claim | Anchor | Verified |
|---|---|---|
| At `3f66fc3f8` (2025-12-23) the training set was `inputs/training_manifest.json`, 20 tiles | `git show 3f66fc3f8:inputs/training_manifest.json` | ✓ 20 entries |
| All three null tiles are members of that set | same | ✓ `K-35-078-1_Lesovo_x2240_y2688`, `K-35-053-3_Elenovo_x3584_y1344`, `K-35-052-4_32635_x896_y1792` all present |
| The null selection was made the same day | `a2ad75c98` "docs: Add null tiles selection for few-shot library", 2025-12-23 | ✓ |
| At `4d011a839` (2026-01-04) the set was re-selected and only 3 of the 20 survived | `git show 4d011a839:inputs/training_manifest.json` against the earlier one | ✓ intersection is exactly 3: `K-35-052-4_32635_x1344_y2240`, `K-35-062-2_Rakovski_x448_y2688`, `K-35-078-1_Lesovo_x1344_y0` |
| None of the three null tiles survived | same | ✓ |
| The committed calibration manifest is that 2026-01-04 content | `git hash-object inputs/tiles/calibration_manifest.json` = `0d61aa81a45a`; identical list to `4d011a839:inputs/training_manifest.json` | ✓ the later `cfc10c133` moved the path, not the content |
| The null manifest was moved unchanged | `a10ed8236` "chore: Reorganise inputs and archive preliminary results", 2026-01-08 | ✓ |
| The empty 384 px calibration manifest came from a bulk commit | `03a233da6`, 2026-03-17 | ✓ |
| The hard examples are unaffected | the 20 source tiles named in `inputs/examples/neutral-naming/MANIFEST.md`'s provenance tables, checked against `inputs/tiles/calibration_manifest.json` | ✓ **20 of 20 are committed calibration tiles** |

## 3. Exposure by frame — recomputed, not carried

Generator `scripts/audit_null_exemplar_overlap.py`; sidecar
`inputs/examples/null-tiles/null_overlap_by_frame.json` (carries every
overlapping tile id); tier-1 tests `tests/test_null_exemplar_overlap.py`.

Method: overlap in each sheet's own pixel space, from the offsets in the tile
filenames, half-open axis-aligned intersection. A frame tile counts when it
shares **any** pixel with a null exemplar's 512 px window. Era-1 frames are
512 px on a 448 px stride (so a null exemplar is itself a frame member and its
eight immediate neighbours overlap it; the next ring out, at 896 px, does not);
the 384 px frames step 336 px. No georeferencing is read.

| Frame | Manifest | Tile size | Tiles | Overlapping | Draft said |
|---|---|---:|---:|---:|---|
| Era-1 full evaluation | `inputs/tiles/full_evaluation_manifest.json` | 512 px | 340 | **25** | — (added this session) |
| Era-1 validation (registered holdout) | `inputs/tiles/validation_manifest.json` | 512 px | 60 | 3 | 3 of 60 ✓ |
| Era-1 verification | `inputs/tiles/verification_manifest.json` | 512 px | 5 | 0 | — |
| Era-2 full evaluation | `inputs/tiles_384/full_evaluation_manifest.json` | 384 px | 487 | 20 | 20 of 487 ✓ |
| Era-2 validation | `inputs/tiles_384/validation_manifest.json` | 384 px | 240 | 6 | 6 of 240 ✓ |
| Era-3 H10 test | `inputs/calibration/h10-384/test_manifest.json` | 384 px | 327 | 13 | 13 of 327 ✓ |
| Era-1 calibration (not scored) | `inputs/tiles/calibration_manifest.json` | 512 px | 20 | 2 | — (by design) |

All four counts the draft carried reproduce exactly. The frame totals also
match the benchmark's own inventory
(`map-reader-bench` `data/derived/provenance/inventory.json`: 340 / 487 / 240 /
327, `references/total` 569, `references_inside_visible_windows.null_tile_512`
0, and the null manifest's blob `efbc0004ece3ea093f31683f813accffec788e70`,
which matched this repository's `git hash-object` **before** the `_note_E86`
annotation was added — that annotation changes the blob, so the benchmark's
`tracked_input_blobs` entry for that file is now one revision behind by design).

**The Era-1 row is the sharpest form of the defect.** On the 340-tile frame the
three exemplars are not neighbours of shown tiles, they **are** shown tiles:
`K-35-078-1_Lesovo_x2240_y2688.png`,
`K-35-053-3_Elenovo_x3584_y1344.png` and
`K-35-052-4_32635_x896_y1792.png` are all members of
`inputs/tiles/full_evaluation_manifest.json`. The remaining 22 are their
stride-448 neighbours.

## 4. Model visibility, by configuration — a census, not an assertion

`scripts/4_detect_mounds_batch.py:885` reads
`config.get("include_example_images", True)`, so an **absent** key means the
example images were transmitted. Census over all `prompts/configs/*.json`:

| Class | Configs | Null pixels transmitted |
|---|---:|---|
| Image modality (key `true` or absent) **and** the three nulls in the example list | **37** | **yes** |
| Image modality, nulls **not** in the list — exactly the four `verify_*.json` verifier configs (library is examples 01–04, 09, 10) | 4 | no |
| Text modality (`include_example_images: false`) | 22 | no — labels only; 21 of the 22 list the nulls, `detect_brief-text_high-recall.json` carries 10 examples and none |
| No example library at all — `library_scale-{16,32}.json` (deferred, never executed) and the four text verifier configs | 6 | no |

So the exposure is **the image modality on the Gold Standard boards**: text
cells, every verifier stage, and all 55-map deployment cells are unaffected
(the 55-map corpus shares no sheet with the three tiles, which are on Lesovo,
Elenovo and K-35-052-4 of the four Gold Standard sheets).

The **direction** of the leak is conservative: what the model saw, labelled
"no mounds here", is ground it was later scored on, which can only suppress
detections on those tiles. The magnitude is the sibling session's re-score
(`results/null-exemplar-sensitivity-2026-09-13/`, checklist item 13a), not this
session's, and E86's Impact field names it as the quantification.

## 5. E87's corrected counts

Generator `scripts/recount_prereg_tile_mounds.py`; outputs
`docs/methodology/preregistration/osf/tile-mound-counts-recomputed-2026-09-13.{json,md}`;
tier-1 tests `tests/test_recount_prereg_tile_mounds.py`. The generator parses
the published counts **out of** the lodged tables rather than transcribing
them, reads each tile's window from `inputs/tiles/<sheet>/metadata.json` (the
affine-derived origins `scripts/generate_tile_bounds.py` uses for every bounds
file the evaluation pipeline scores against), and reproduces the superseded
approximation by importing `select_tiles_phase2`'s own `load_map_georef`,
`get_map_dimensions` and `count_mounds_in_tile`.

| Set | § | Tiles | Published | Affine 512 px, distinct | Affine 512 px, summed | Affine 448 px core |
|---|---|---:|---:|---:|---:|---:|
| Training / calibration | 2.3 | 20 | **36** | **50** | 52 | **39** |
| Holdout / validation | 2.4 | 60 | **79** | **97** | 106 | **82** |

The draft's "50" is the **union** (distinct references); the sum of per-tile
counts is 52, because two references sit in the 64 px overlap between two
calibration tiles. The 448 px cores tile each sheet without overlap, so their
counts partition the reference layer — the generator asserts this as its
geometry self-check (**the cores of all 360 physical tiles account for the 569
references exactly once**), and that identity is what licenses the arithmetic.

**Mechanism.** The approximation reproduces **45 of the 80** published per-tile
counts exactly (10 of 20 calibration, 35 of 60 holdout); the affine-correct
512 px computation reproduces **31 of 80** (7 of 20, 24 of 60). The draft
quoted "45 of the 80 … against 7 of 20", which compares different
denominators; the like-for-like comparison is 45 against 31, and it still
identifies the approximation as the method that wrote the tables. It does not
reproduce all 80, so a second and smaller source of divergence remains; the
entry does not attribute it.

**New and not in the draft — the consequence that matters most.** Applying the
registered density rule (`empty` 0, `sparse` 1–2, `dense` 3+) to the corrected
counts moves **10 of the 20 training tiles and 27 of the 60 holdout tiles**
into a different stratum (8 and 23 over their 448 px cores), and **3 training
and 12 holdout tiles registered as `empty` are not empty**. The stratified
sample is unchanged — those were the strata the registered seeds drew from — so
§ 2.5 records *how the selection was made*, not the tiles' mound content, and
nothing downstream reads it (the executed evaluation scopes are frame-defined
and score against the reference layer directly).

## 6. Three claims in the drafts that did not survive verification

Recorded because the drafts are otherwise accurate and these are the kind of
error that propagates if carried silently.

1. **"The verifier config carries no examples."** It carries **six**
   (`prompts/configs/verify_brief.json`: examples 01–04, 09, 10). The
   conclusion — the verifier never saw the null pixels — holds, and holds more
   strongly than the draft's reason: of the 41 image-modality configs the only
   four without nulls are the four verifier configs.
2. **The null-pool statement's location, given as § 8.4.1.** It is
   § 8.4.2 (the library-composition table's "Source: Training set",
   `osf/preregistration.md:1512`) and § 8.4.3 (the pool, seed and the three
   named tiles, `:1533-1541`).
3. **"361 tiles at preregistration line 78" as a live minor item.**
   **E64 (ii)** already catalogued that contradiction — 361 here against
   "~360" in § 8.6 — and adopted the 360 physical tiles as the operative
   reading on 2026-07-30. What was actually outstanding is that
   `docs/paper/methods-draft.md` carried 361 forward at `:21`, `:195` and
   `:439` without that reading. E87 records the distinction and the Methods
   commit fixes the draft; line 78 is not re-opened.

## 7. Three dispositions that departed from the drafts

### 7.1 The lodged registration copy cannot be annotated inline

E87 remediation 1 as drafted was to annotate `osf/preregistration.md`
§§ 2.3–2.5 and § 8.4.2 with erratum pointers. It was attempted, and it broke
the project's own integrity tripwire. `results/commitments.json` pins all three
lodged documents by git blob — `preregistration.md` at `fa221b30f395` — and
anchors **702 extracted commitments** to verbatim statements at specific line
ranges inside them; `scripts/validate_commitments.py` checks both (checks 2 and
5 of its docstring). The inserted blockquotes shifted every line number below
each insertion and produced **520 verbatim-locator failures** and two tier-1
failures in `tests/test_validate_commitments.py`.

The annotations were reverted — the file is back at blob `fa221b30f395` and the
ledger's tier-1 tests are green — and became
`docs/methodology/preregistration/osf/errata-pointers.md`, a 12-row reverse
index from a lodged passage (with its line locator) to the erratum that
corrects it, linked from the errata register's header and from
`osf/README.md`. It delivers the same reader-facing guarantee without touching
the pinned text.

**The generalisable finding**: a line-anchored, blob-pinned document cannot
carry its own errata. Any future erratum landing on the registration must
extend the companion index. This is also why the file had no prior
erratum-pointer convention for this session to follow — not an oversight, a
constraint.

### 7.2 `select_tiles_phase2.py` is frozen and annotated, not fixed and not archived

The draft offered two options and the brief's criterion was "keep the committed
selections reproducible". **Both offered options fail it:**

- **Correcting `load_map_georef` to read the raster affine** would change the
  counts, which feed `categorise_density`, which defines the strata the
  stratified sample draws from. Under the same registered seeds the script
  would then select different tiles — against § 8.6's "Re-running with same
  seeds produces identical selection".
- **Archiving the script** to `archive/deprecated-scripts/` would break a
  registration-cited reproduction path: § 8.6 (`:1948-1953`) names its output
  artefacts and `scripts/README.md` documents it as their producer. Moving it
  repeats a defect class this project has already recorded (a registration
  citing a document at a path the file has since left).

So the third disposition: the arithmetic is kept unchanged as the historical
record of how the committed selections were made, and the script carries a
FROZEN block in its module docstring plus DO-NOT-FIX warnings on
`load_map_georef` (`:205`) and `count_mounds_in_tile` (`:250`), each naming E87
and pointing at the affine route instead. **Open for the PI**: a rebuilt
selection under corrected geometry would be a new selection with a new seed
record and its own erratum, not a repair of this one.

One incidental fix while in the file: its docstring still advertised
`inputs/tiles/holdout_manifest.json` as an output, which E73 changed to
`validation_manifest.json` on 2026-08-02 (`:635`).

### 7.3 The empty 384 px calibration manifest is documented, not archived

`inputs/tiles_384/calibration_manifest.json` is the literal `[]`. It is a
**required placeholder, not an omission**: the 384 px grid has no calibration
set of its own (the exclusion geometry derives from the 512 px calibration
tiles' footprint), but `scripts/generate_tile_bounds.py`'s default mode requires
the file in its `--tiles-dir` and exits if it is absent. Verified by running
`python scripts/generate_tile_bounds.py --tiles-dir inputs/tiles_384
--tile-size 384` in this session: it emits a zero-feature
`calibration_bounds.geojson` and a 240-feature `validation_bounds.geojson`.
Archiving it would break that command, so its role is documented in
`inputs/README.md` instead.

## 8. The provenance guard

`scripts/check_manifest_provenance.py` over
`inputs/provenance/manifest-dependencies.json`, extending the content-anchor
discipline of `reports/name-keyed-cache-audit-2026-09-12.md` and pull request
\#14 from **derived** artefacts (caches, unions, evaluations) to **input**
manifests and the example library — a class that audit's 27-row candidate table
did not cover.

Run output, 2026-09-13 (`python scripts/check_manifest_provenance.py`):

```text
ok null-tiles-from-calibration                       STALE     expected STALE  (documented: E86)
    source: inputs/tiles/calibration_manifest.json  [STALE]
            declared c5056693d505 (declaration-time, 2025-12-23) → on disk 0d61aa81a45a
ok hard-example-library-from-calibration             CURRENT   expected CURRENT
ok era1-full-evaluation-frame-from-calibration       CURRENT   expected CURRENT
ok era1-validation-from-reference                    CURRENT   expected CURRENT
ok era2-384-full-evaluation-from-calibration         CURRENT   expected CURRENT
ok era2-384-validation-from-bounds                   CURRENT   expected CURRENT
ok h10-384-pools-and-test-from-bounds-and-reference  CURRENT   expected CURRENT
ok era2-384-bounds-from-manifest                     CURRENT   expected CURRENT

8 dependencies: 7 current, 1 stale (0 not as declared).
```

`--check` exits **1**, naming `null-tiles-from-calibration` and nothing else —
which is what the brief asked of it: flag the null-tile manifest, pass
everything else. `--check-expected` exits **0**, and is the mode the tier-1
test runs, because E86's staleness is permanent by ruling and a permanently red
guard is an ignored guard; it turns red on any **new** re-selection under an
old declaration, and equally on a silent repair of a declared-stale row. A row
that expects staleness must name an erratum or the registry refuses to load.

Each anchor records its own strength: `declaration-time` (provable from the
repository's history — eight of the nine source anchors) or `registry-creation` (stamped now, so it
catches future drift only). One dependency was checked specifically because a
sibling bounds file *was* regenerated after its consumer's selection:
`inputs/tiles_384/validation_manifest.json` declares
`inputs/vectors/bounds/validation_bounds.geojson`, last changed 2026-02-05
(`496dde29b`, E19) — **before** the 2026-03-14 selection — while
`inputs/vectors/bounds/384/full_evaluation_bounds.geojson` was regenerated on
2026-03-22 (`8b52ab63b`). No second instance of the E86 class was found.

## 9. What did NOT change

- **No measured value.** No metric, evaluation, board cell, threshold, scope
  membership or hypothesis outcome was touched. Nothing under `results/` was
  modified by this session.
- **No experimental artefact.** No example image, no prompt configuration, no
  tile manifest membership, no detection or evaluation file.
- **The null exemplars themselves.** Deliberately frozen (E86 remediation 2
  recorded as an option, not taken): every committed run that used the library
  used these three tiles.
- **The lodged registration copy.** Byte-identical, at blob `fa221b30f395` —
  the pin `results/commitments.json` records.
- **`select_tiles_phase2.py`'s selection arithmetic.** Documentation only.
- **`inputs/tiles/tile_selection_metadata.json`'s data.** A `_note_E87` block
  was added; `parameters.tile_size` was **not** renamed, because other code
  reads the key by name, and the file was not regenerated, because that would
  rewrite the registered selection record.

## 10. Two pre-existing tier-1 failures, neither this session's

Reported rather than fixed, because both sit outside this work and one is
owned elsewhere.

- `tests/test_generate_run_reports.py::test_no_drift_in_committed_reports` —
  `scripts/generate_run_reports.py --check` reports
  `outputs/h10/post_run_report.md` stale, 1 of 39. That report is committed
  (`a7ab9c1c0`) and unmodified here, and the generator reads no path under
  `inputs/` (grep), so the drift is inherited from `main` at `e9bb1b03c`.
- `tests/test_build_generated_file_registry.py::test_committed_registry_matches_a_rebuild`
  — expected in kind: the registry enumerates the Markdown file tree, so its
  `--check` fails whenever a Markdown file is added, which checklist item
  **11d** already documents. This session adds one file the registry counts
  (this report; the two new `docs/methodology/preregistration/osf/` documents
  fall outside the paths it scans).

  **The rebuild was NOT done here, and item 11d needs amending.** Running
  `scripts/build_generated_file_registry.py` in this worktree produced 3,620
  files against the committed 3,619, but as **18 insertions and 938 deletions**:
  it dropped **93 `outputs/` entries** — `outputs/ab-plus/_work/*.overflow-notes.md`
  and siblings — that exist in the main checkout (526 files in that directory
  there) but are untracked working files a fresh worktree does not have. The
  rebuild was reverted. So item 11d's standing instruction ("rebuild it as the
  last step of every handoff") is **unsafe from a worktree**: the registry
  enumerates untracked `outputs/` content, so only the main checkout can
  rebuild it faithfully. Flagged for the PI as an amendment to that item; the
  rebuild for this session's one added file belongs to whoever merges this
  branch in the main checkout.

## Changelog

### 2026-09-13 — Original publication

Written with errata **E86** and **E87** as the claims-with-anchors record for
their insertion. Initial state: the provenance chain re-verified across five
commits; the per-frame exposure recomputed (25/340 at Era 1, new this session;
20/487, 6/240, 3/60 and 13/327 all reproducing the drafts exactly); the
configuration census (37 of 41 image-modality configs transmit the null
pixels); E87's corrected counts (36 → 50 distinct over the calibration windows,
79 → 97 over the holdout, with the 569-reference core-partition self-check);
the density-stratum consequence (10 of 20 and 27 of 60 tiles move, 3 + 12
"empty" tiles are not empty); three draft claims corrected; three dispositions
departed from the drafts, including the discovery that the blob-pinned,
line-anchored registration copy cannot carry inline errata pointers; and the
guard's run output. Anchored to commits `2a270af50`, `bcf936ad2` and
`92745b0c9`.
