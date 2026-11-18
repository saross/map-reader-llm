# Tile-join Wave 2 — specification (the corpus re-score)

> **Last revised**: 2026-11-19 (original publication: first draft, for
> Astra's review). See [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), drafting for session S169 on amd-tower. Every path,
  count, line number, and timing below was read from the file named beside
  it, at these commits: `main` at `92064b134` (the decision record, the
  Wave 1 specification, D72 and D73, `scripts/`); branch
  `tile-join-wave-1-w10` at `89cab15ee` (W1.0's reports, worklist, and
  replay record); branch `tile-join-wave-1` at `a7989c47f` (the W1.1 code,
  in progress: read for orientation only; this document specifies against
  the Wave 1 specification's contract, not against unfinished code).
  Astra's consumer audit was read at its audited base `e92d1c5d7`. New
  counts come from the read-only, standard-library planning script
  `planning/tile-join-wave-2-spec-2026-11-19-scripts/wave2_scope_and_cost.py`
  (output beside it as `wave2_scope_and_cost.txt`), run on amd-tower
  against the tracked evaluation files; nothing was scored.
- **Parent**: `planning/tile-join-resolution-2026-11-01.md` (the decision
  record; this document specifies the Wave 2 row of its § 5). Sibling:
  `planning/tile-join-wave-1-spec-2026-11-01.md`, whose § 7 lists what must
  hold before Wave 2 may be called ready. Rulings: D72 and D73 in
  `planning/pi-decisions-2026-09-20.md`.
- **Status**: **DRAFT, for Astra's review; not approved; Wave 1 stopped on
  the seam ruling (Wave 2 cannot launch until M1).** The 55-map seam
  handling is an open parameter (§ 4); this draft takes no position among
  the options.
- **Target**: all data and results settled, and the write-up begun, by
  **Sunday 2026-11-29** (PI, 2026-11-18).
- **Runs on**: zbook, unattended from launch to M2, stopping only on a
  problem (§ 6), as Wave 1 does under D73 (7) if the principal
  investigator (PI) extends that ruling to Wave 2 (open question P1).
  **Zero API calls.**

## 0. What Wave 2 does, in one paragraph

Wave 2 re-scores every committed evaluation whose tile classification or
interval arithmetic depends on a tile join, using the merged Wave 1 code.
Each file is first replayed under the rules it recorded, which must
reproduce its committed confusion and intervals (or its recorded refusal).
Every target field is then computed under the new rules: sheet-specific
containment for classification, and nearest-centre within the point's own
sheet for count tables. Only those fields are spliced into the committed
file, and every other field must stay identical. Live files under
`results/` are re-scored in place. Files under `archive/` (and any other
directory the PI rules frozen) get labelled corrected counterparts
elsewhere and are not modified. Paper-cited files go first, then the rest,
in the same run. The gold-standard (GS) frames can run as soon as M1
allows. The 55-map files wait for the PI's seam ruling, because that
ruling changes how the new rule treats their sheet seams. A new driver,
written for this wave, does the work and records every file's outcome in
a ledger that reconciles to the W1.0 worklist.

## 1. Preconditions (launch is blocked until all hold)

| # | Precondition | How it is checked |
|---|---|---|
| P1 | **M1 passed** and the Wave 1 pull request (PR) merged, with gate G1 green (Wave 1 specification § 4, § 9). Today Wave 1 is stopped on the 55-map seam ruling (`reports/tile-join-wave-1/stop-2026-11-18-55map-seams.md`, on `tile-join-wave-1-w10`) | the PI's M1 decision; the merge commit on `main` |
| P2 | The Wave 1 specification's § 7 holds: a complete target and non-target schema (met: `dry-run.md` § 3); a small reference case checked independently of the scorer; an idempotent rerun; a reconciled worklist with every paper-cited file resolved (met: `dry-run.md` § 4.3, 0 paper-cited `unresolved-recipe`) | W1.5's smoke ledger; `worklist.json` |
| P3 | **W1.5 has re-measured the cost** with the new joins: wall-clock, CPU time, and peak resident set size (RSS) per smoke cell, replay and new-rule legs separately. § 7's projection uses legacy-replay timings only and is replaced by the re-measurement | `smoke-ledger.json` (Wave 1 § 8) |
| P4 | **Every GS frame in scope has had the sheet check.** The parent record's § 2.6 check ran on the Era-2 frame only (`planning/tile-join-resolution-2026-11-01-scripts/sheet_boundary_check.py:43`). Phase A also scores six other GS frame families (§ 3.2). Each needs the same check, with the same stop rule: a cross-sheet contact on map content stops that frame's files, as it stopped Wave 1 (W2.0) | `reports/tile-join-wave-2/gs-sheet-check.md` |
| P5 | **The Wave 1 consumer-disposition record is committed** and reconciled with Astra's inventory (116 calls in 70 files outside the metrics library). Commit `e34a7e581` on `tile-join-wave-1` names `reports/tile-join-wave-1/consumer-dispositions.md` as its per-site record, but no branch carried that file when this draft was written | the file exists on `main` after the Wave 1 merge; § 8 |
| P6 | **The PI has answered the open questions that the driver needs as inputs** (§ 12.1): the counterpart location (P6), the frozen-directory list (P5), and the replay-mismatch threshold (P9) | the answers recorded in this document's changelog |
| P7 | **For phase B only (the 55-map files): the seam ruling** (§ 4) has been made, its parameter written into the driver's configuration, and Astra has reviewed it before any 55-map compute. Every option changes how a 55-map metric is computed, and the project requires cross-model review of such a change before compute (`docs/agent-guidance.md`, "Cross-model review of definition changes") | the ruling in `planning/pi-decisions-2026-09-20.md`; Astra's review by mail or committed file |
| P8 | zbook's `.venv` still matches the reference environment, and zbook's checkout is on `origin/main`, clean, 0 behind (as Wave 1's P3 and P4) | `uv pip freeze` against `requirements-lock.txt`; tier 1 at the post-merge count; `git status -sb` |

**The order of events matters.** Wave 2 cannot launch before M1, and M1
needs the W1.5 smoke run, which includes the 55-map smoke cell 2. The stop
record's § 3 pauses W1.5 until the seam ruling. So the GS-first plan of
§ 3 buys time only if the PI either rules on the seams soon or splits M1:
GS smoke cells 1 and 3–8 now, with cell 2 after the ruling (open question
P2).

## 2. What W1.0 and this draft's census found that shapes Wave 2

1. **The scope is wider than "files with a tile block".** The parent
   record's Wave 2 row counts 2,646 files that contain
   `tile_classification`. The count-table change (D72 (2)) also moves the
   F1, precision, and recall intervals and the coverage diagnostics of
   files that carry intervals but no tile block. From the worklist:
   149 live files have intervals and no tile block. 21 more are under
   `archive/`. Five `known-withheld` files carry neither, because the
   recorded refusal withheld both. They become scoreable under the new
   rules (`wave2_scope_and_cost.txt` § 1b). This draft puts all of them in
   scope (§ 3.1); open question A1 asks Astra to confirm.
2. **W1.0's determinism replays covered two schema strata out of several.**
   The eight smoke cells have `_metadata.metadata_version` 1.3 or 1.4
   (`wave2_scope_and_cost.txt` § 5). The files in scope also include
   versions 1.0 (5 files) and 1.1 (27). There are also 24 files with no
   version, which are the 55-map files not written by the scorer. All 761
   paper-cited files are version 1.3 (520), 1.4 (217), or unversioned
   (24). E81's header warns that a full replay "imports every unrelated
   change made to the scorer since the cell was written", such as the E72
   coverage machinery (`scripts/rescore_tile_mcc_e81.py:15–27`). A replay
   of an older stratum may therefore fail for reasons unrelated to the
   join. The pilot (W2.2) samples every stratum before the corpus run.
3. **Re-serialisation preserves the bytes of almost every file.**
   `write_outputs` writes `json.dump(output, f, indent=2)` with no trailing
   newline (`scripts/evaluate_detections.py:1893`). Of the 2,829 worklist
   files, 2,795 equal `json.dumps(json.loads(text), indent=2)` exactly. A
   further 26 differ only by one trailing newline, and 8 differ in other
   ways. All 8 are 55-map files not written by the scorer: three with no
   recorded writer and five written by
   `scripts/compute_corrected_f1_multi_buffer.py`
   (`wave2_scope_and_cost.txt` § 4). So for all but 8 files, a byte
   comparison of untouched lines is a meaningful guard.
4. **`write_outputs` overwrites two non-target fields.** It stamps
   `version` and `timestamp` afresh (`evaluate_detections.py:1882–1883`),
   and E81's re-emission went through it (`rescore_tile_mcc_e81.py:392–397`).
   `version` is non-target in W1.0's schema (`dry-run.md` § 3.3). A
   surgical re-emission must therefore keep the original `version` and
   `timestamp`. It must not call `write_outputs` on the whole document.
5. **The non-scorer writers are all 55-map and all paper-cited.** The 24
   live files in scope that `evaluate_detections.py` did not write are
   five under `results/stride55-2026-08-27/`
   (`compute_corrected_f1_multi_buffer.py`) and 19 with no recorded writer:
   `results/55maps-extended-gt-2026-06-07/` 8,
   `results/55maps-standardised-ref-2026-08-14/` 8,
   `results/gemini37-55map-2026-08-31/` 2, and
   `results/gemini37-fourth-cell/` 1. Every one is paper-cited
   (`wave2_scope_and_cost.txt` § 3, "non-scorer writers"). W1.0 did not
   trace their schemas (`dry-run.md` § 3.4). They fall in phase B, behind
   the seam ruling, which leaves time to trace them.
6. **The null-exemplar detections are filtered by the name rule.** The 232
   `unresolved-recipe` null-exemplar cells score leak-filtered copies of
   their detections. The filtered files are gitignored. The committed
   manifest calls them "a deterministic function of committed inputs and
   this script" (`results/null-exemplar-sensitivity-2026-09-13/detections_manifest.json`,
   `_README`). The filter drops every feature whose `source_tile` names an
   exposed tile, and it falls back to the first intersecting frame tile
   only when a file has no `source_tile`
   (`scripts/analyse_null_exemplar_sensitivity.py:500–551`). That is the
   legacy name rule applied at construction time. Wave 2 can regenerate and
   re-score those inputs as built. Whether the filter itself should change
   is a separate question (open question P7).
7. **The single seam hook exists in the Wave 1 code.** On
   `tile-join-wave-1` (`32ebe3762`), every sheet-join booking reads one
   function, `sheet_join_candidate_tiles`, whose docstring says a seam
   exception or exclusion "is a change here alone". This draft relies on
   that design (§ 4) and asks Astra to check it holds at merge (open
   question A3).

## 3. Scope and order

### 3.1 Disposition of every worklist entry

The W1.0 worklist (`reports/tile-join-wave-1/worklist.json`, 2,829
entries) gives each file a status. The driver maps status to disposition
by the rules in `wave2_scope_and_cost.py` `disposition()`:

| Disposition | GS | 55-map | No frame | Of which paper-cited | Basis |
|---|---:|---:|---:|---:|---|
| `rescore-in-place` | 2,184 | 309 | — | 761 (608 GS, 153 55-map) | `reproducible-legacy` with a tile block or intervals (2,444), plus all 49 `known-withheld` |
| `counterpart` | 43 | 11 | — | 0 | `historical-only` (`archive/`), all 54 carry intervals, 33 also a tile block |
| `regenerate-then-rescore` | 232 | — | — | 0 | the null-exemplar `unresolved-recipe` cells (§ 5.1) |
| `hold:input-absent` | 1 | 12 | — | 0 | `unresolved-recipe`: detection input absent on zbook (§ 5.3) |
| `skip:no-recipe` | — | — | 36 | 0 | `unresolved-recipe`: `results/verifier-t-pilot/` 24 and `results/retest/` 12 record no recipe (§ 5.1) |
| `skip:not-tile-bearing` | 1 | — | — | 0 | `reproducible-legacy` with neither a tile block nor intervals |
| **Total** | 2,461 | 332 | 36 | 761 | 2,829 |

Source: `wave2_scope_and_cost.txt` § 1. The 2,779 files that the driver
rescores or counterparts are 2,459 GS and 320 55-map files (§ 3 of the same
output).

### 3.2 Order

D72 (3): paper-cited first, then the rest, without stopping between them
if the run can carry on. The seam ruling splits the run into two phases:

| Phase | Files | Needs | Order inside |
|---|---|---|---|
| **A** (GS frames) | 2,459: 608 paper-cited, 1,851 not (including 43 counterparts and 232 regenerated null-exemplar cells) | P1–P6 and P8 | paper-cited first; then the rest; counterparts last |
| **B** (55-map frame) | 320: 153 paper-cited, 167 not (including 11 counterparts) | P1–P8, so the seam ruling (P7) | the same |

Phase A's frames are the 384 px full frame (1,105 files), the 512 px full
frame (739), the Era-2 B intersection (254), the two null-exemplar reduced
frames (153 and 82), the grid common frame (64), the H10 test frame (40),
the 256 px full frame (16), and the H13 common frame and arms (6). Their
tile counts are 487, 340, 487, 467 and 315, 487, 327, 1,032, and 340 to
999. Every phase A file uses `inputs/vectors/references/mounds-reference.geojson`
(`wave2_scope_and_cost.txt` § 2). P4's sheet check is therefore one check
per frame.

**Before the seam ruling, phase B computes nothing under the new rules.**
What it may do in the meantime, once M1 has passed, is the legacy-replay
leg alone. That leg replays each 55-map file under its recorded rules,
does not depend on the ruling, and computes no corrected score, so it is
outside the stop record's pause (§ 3 there). Each file is then ledgered
`skip`, `held:seam-ruling`, with its replay outcome, so replay mismatches
surface early. The replay is repeated when phase B runs, because the rule
set then differs. That costs 10.89 CPU-hours more, about 0.9 h at 12
workers (§ 7). This draft also proposes that no 55-map score under any
seam option be computed before the ruling, so that the ruling is not
made with its results in view (open question P3).

### 3.3 Merging

Wave 2 writes on branch `tile-join-wave-2`, in a zbook worktree, and
commits in batches (one commit per top-level results directory, each
carrying its ledger counts in the body). It pushes the branch and does
not merge it. This draft proposes that Wave 3 branch from
`tile-join-wave-2` and that both merge after M3. `main` would then never
hold re-scored evaluations beside downstream artefacts built from the old
ones (§ 8; open question P4).

## 4. The seam parameter (open; the PI rules)

On the 55-map frame, adjacent sheets print some mounds twice, and only one
copy was digitised. W1.0 found 32 contacts on map content (26 references)
in `best-available-gt-55maps-r2.geojson`, and 32–35 in each of the other
four tracked 55-map reference files (`dry-run.md` § 2). Sheet-specific
scoring would count a correct detection of the undigitised copy as a false
positive (stop record § 1). The stop record § 4 lists four options. **This
document takes no position among them.** It specifies how each would
enter the driver, and states facts that bear on them.

**The parameter is keyed by (frame, reference file),** because the
contacts are measured per reference file and differ between them. The
paper-cited 55-map files use four references: r2 104, the earlier
best-available file 28, the reviewed student file 13, and canonical r50 8.
The non-cited files also use the unreviewed student file
(`wave2_scope_and_cost.txt` § 2). The driver reads a committed
configuration file, `reports/tile-join-wave-2/seam-policy.json`. Its
default for every 55-map key is `pending`, under which the driver holds
the file (§ 5.4, status `skip`, reason `held:seam-ruling`).

| Option (stop record § 4) | How it enters the driver | Facts that bear on it |
|---|---|---|
| **(a)** add the second copy as a reference on the neighbouring sheet | **An input change, not a driver code path.** A new, versioned reference file per affected reference, committed with its construction recorded. The driver maps each recorded reference to it for the new-rule computation only; the legacy replay still uses the recorded file | It changes the symbol-level matching inputs, so point F1, precision, and recall can move on affected 55-map files. G2 item 2 (points identical) cannot hold for them without an amendment; the record says the point estimates are untouched (parent record § 0). On r2, 11 tiles turn positive (`dry-run.md` § 2.2). Astra found that § 2.2's "references added" column counts contacts, not distinct references: on r2 the 32 map-content contacts are 26 distinct reference and recipient-sheet combinations (`~/agent-mail/codex/outbox/claude/20261118T130529Z-astra-seam-measurement-counting-finding.md`). Canonical r50 already carries such a copy (`phantom:*`) for 29 of its 33 map-content contacts, and (a) moves no tile on it (`dry-run.md` § 2.2) |
| **(b)** a seam exception | Two readings, which enter differently. **Tile-only** (the contacted tile also counts as positive, as `dry-run.md` § 2.2 measured it): a rule inside `sheet_join_candidate_tiles` that adds the contacted neighbour tile for the listed contacts, read from a committed contact list per (frame, reference). **Matching** (the stop record's wording: "a detection matches a reference from either sheet"): a change to symbol matching, which Wave 1 does not change | The tile-only reading moves the same tiles as (a) on r2 (11; 17 with the ambiguous contacts) and changes no point estimate. The matching reading changes point estimates, with the same G2 consequence as (a), and needs code outside Wave 1's scope |
| **(c)** a frame-wide join for the 55-map corpus only | **A per-frame join choice, no new code.** The driver's configuration names classification `geometric-contains` and count table `geometric-primary` for the 55-map frame. Both are kept selectable (Wave 1 specification, W1.1) | It turns 333 tiles positive on r2 relative to sheet-specific containment. Only 11 of them are confirmed map-content contacts; the rest arise from references in other sheets' tiles (`dry-run.md` § 2.2). Astra notes that the complement of the 11 is not established as all padding, since 17 tiles change once ambiguous contacts are included (same message). The outputs would carry frame-wide join names, which the parent record keeps as historical comparisons (§ 3) |
| **(d)** exclude the contacted seam tiles from classification | A committed exclusion list per (frame, reference), applied in `sheet_join_candidate_tiles` and in the classification tile population | On r2 it removes 52 tiles, 41 of them positive (`dry-run.md` § 2.2). It is a sub-decision whether the excluded tiles also leave the count tables. If they do, `coverage.n_tiles` changes, and W1.0 classes that field as non-target (`dry-run.md` § 3.3), so G2 item 1 would need a stated exception |

**Sub-parameter, whichever option is chosen:** whether the 18 ambiguous
contacts on r2 (points on the black edge of the map face) count with the
map-content contacts (stop record § 4, item 3; `dry-run.md` § 10, question
3). Astra's pixel audit leaves the two contacts of `student:04282`
unresolved for manual judgement (same message).

**Interim:** phase A runs, and phase B waits (§ 3.2). The driver refuses
to compute any 55-map file under the new rules while its key is
`pending`. A refused attempt is a § 6 stop, because it means the
configuration was bypassed.

## 5. Work items

### W2.0 Preconditions and the GS sheet check (read-only, first)

- Confirm P1–P8, and record the evidence in the run directory.
- **The GS sheet check (P4).** Run the parent record's
  `sheet_boundary_check.py` method on every phase A frame other than
  Era-2: the 384 px, 512 px, and 256 px full frames, the grid common
  frame, the H10 frame, and the H13 common frame and its three arms. The
  two null-exemplar reduced frames (`era2-b-487_minus_null_overlap`,
  `era1-full-340_minus_null_overlap`) are named as full frames less their
  null-overlap tiles. W2.0 confirms that every tile in each, name and
  polygon, is in its parent frame. A confirmed subset inherits its
  parent's result; an unconfirmed one is checked in its own right. Report every cross-sheet tile
  contact with its pixel position and a padding, map-content, or
  ambiguous verdict, using W1.0's rule (`dry-run.md` § 2, "Method").
  **A contact on map content stops that frame's files** and goes to the
  PI, as the 55-map contacts did.
- **The independent reference recount** (as G1 item 4), once per (frame,
  reference) pair rather than once per file: the number of tiles holding
  at least one of their own sheet's references, computed without the
  scorer. Every re-scored file's reference-positive count must equal it
  (G2 item 6).
- Re-run `wave2_scope_and_cost.py` against the merged worklist, and stop
  if any count in § 3.1 has moved without an explanation.

### W2.1 The driver (code, tests)

A new script, proposed name `scripts/tile_join_wave2_rescore.py`, with
tier 1 tests in `tests/test_tile_join_wave2_rescore.py`, on branch
`tile-join-wave-2`.

**What it reuses, and what it must not inherit (Astra C2).** It imports
the pure recipe recovery `recover_recipe`
(`scripts/rescore_tile_mcc_e81.py:142–179`; it reads `_metadata` and
returns the recipe, with no join and no scoring), and the scorer's
`find_detection_files`. It must not call E81's `recompute_cell` or
`rewrite_cell`. Those call classification without a join at this base
(`:310–314`, the dependence Astra's C2 names), guard on confusion counts
alone (`:317–328`), and rewrite through `write_outputs` (`:392–397`). The
Wave 1 code has since pinned E81 to each record's own join. Wave 2 still
does not depend on it, and E81 stays a historical tool. Every library call
the driver makes passes the classification join and the count-table join
explicitly. It reads no default, so a later change of default cannot
change its meaning.

**Inputs:**

- the W1.0 worklist (pinned by commit and SHA-256);
- `seam-policy.json` (§ 4) and a frozen-prefix list (default `archive/`;
  open question P5);
- the data root, zbook's main checkout, read-only, for gitignored inputs;
- the target worktree, the `tile-join-wave-2` checkout on zbook;
- a run directory in zbook scratch, `~/scratch/wave2/<run-id>/`.

**Per file, in order** (the Wave 1 specification's "two computations, in
order", W1.1):

1. **Identity.** Hash the committed file (SHA-256). Recover the recipe.
   Hash every input and compare it with any recorded git blob hash. Record
   the run order of replicated passes, the seed, the iteration count, the
   buffers, and the environment.
2. **Legacy replay.** Score under the file's recorded rules: the recorded
   classification join, else `id`; the recorded count-table join, else the
   legacy name rule. Compare every committed field, treating a key absent
   from an older file as "not recorded", not as drift (`dry-run.md` § 7).
   For a `known-withheld` file, the replay must end in its recorded
   refusal with its recorded counts.
3. **New-rule compute.** Compute every target field (`dry-run.md` § 3.2)
   under classification `sheet-contains` and count table `sheet-primary`,
   or under the frame's seam policy for phase B.
4. **Splice.** Copy the committed document, replace only the target
   fields, and add the provenance below. Keep `version`, `timestamp`, and
   every non-target `_metadata` field. A non-target key that the committed
   file lacks (for example `summary.detection_scope` on older files) stays
   absent. The scope used is recorded in the re-emission block instead.
5. **Guards** (G2 items 1–6, per file), on the staged output.
6. **Siblings.** Regenerate `evaluation.md` and `evaluation.csv` from the
   spliced document, but only where the committed directory has them. The
   driver creates no file that did not exist. Compare the CSV's non-target
   columns (`dry-run.md` § 3.3) with the committed ones. Ledger any
   non-target difference in the Markdown as `sibling-renderer-drift`
   (open question A2).
7. **Write.** Write into the target worktree (rescore) or the counterpart
   tree, then append the ledger record.

**Provenance written into each re-scored file.** The fields W1.1 defines:
`tile_join` in every tile block, `count_table_join` on every block whose
intervals or coverage come from a count table, and both in `_metadata`
with the D72 and D73 pointer. `_metadata.cli_args.tile_join` is a target
field (`dry-run.md` § 3.2). It is updated to describe the values now in
the file, so the file no longer pairs old invocation metadata with
new-rule blocks (Astra C2's concern). The original `cli_args` is kept,
unchanged, as `_metadata.tile_join_reemission.original_cli_args`. One block records the re-emission:
`_metadata.tile_join_reemission`, holding the driver path and commit, the
library commit, the date, the rulings, the seam policy key and value (for
phase B), the SHA-256 of the committed file it replaced, the recorded
rules it replayed under, and the D50 scope summary. Whether a re-emitted
file also takes the new `metadata_version` (1.5 on the Wave 1 branch,
where it marks a writer that records both rules) is open question A4.

**Counterparts** (D73 (5)). The original stays byte-identical. The
corrected file is written at
`results/tile-join-wave-2/counterparts/<original path>`, with siblings,
and carries `_metadata.tile_join_reemission.counterpart_of` (path and
SHA-256). The location is a proposal (open question P6).

**Batch roll-ups.** Seven live directories carry a `batch_summary.json`:
`results/paper-eval/mcc/{384px,512px}/`,
`results/paper-eval/n1/384px-14buf-mcc/` and its `pro-rerun/`,
`results/paper-eval/n1/{384px-all-buffers,512px-all-buffers,512px}/`.
Each one whose cells are re-scored is rebuilt from them afterwards, as
E81 did (`rebuild_batch_summary`, `rescore_tile_mcc_e81.py:400–434`). The
rebuild keeps the original `version` and `timestamp`, as in step 4. The
two roll-ups under `archive/` get counterparts.

### W2.2 Pilot (before the corpus run)

The W1.5 smoke run proves the code on eight cells. The pilot proves the
driver on the corpus's strata. It writes into a disposable copy of the
branch, not the branch itself. It takes at least one file from every
populated cell of frame × `metadata_version` × interval method ×
coverage block × replication × route × status, from § 2 item 2 and
`wave2_scope_and_cost.txt` § 5. That includes the 1.0 and 1.1 counterparts,
a 30-pass file, a `known-withheld` file, a null-exemplar regenerated cell,
and a batch root. It records each leg's timing and peak RSS, and it runs
the full driver twice over the pilot to show idempotence and resumption
(kill the first run part-way). It passes only if every G2 item holds on
every pilot file. Its timings replace § 7's projection before phase A
launches.

### W2.3 Phase A (GS frames)

The driver runs over the phase A files in § 3.2's order, with the worker
count from § 7, and writes into the zbook `tile-join-wave-2` worktree. It
commits per top-level directory and pushes after each commit.

### W2.4 Phase B (55-map; after the seam ruling)

The same as W2.3, once P7 holds. It also covers the 24 files from
non-scorer writers (§ 5.2).

### W2.5 Reports

`reports/tile-join-wave-2/` (§ 10), all following the document revision
policy.

### 5.1 The 281 `unresolved-recipe` files

| Group | Files | Handling |
|---|---:|---|
| Null-exemplar sensitivity cells (`results/null-exemplar-sensitivity-2026-09-13/`) | 232 | **Regenerate, then re-score.** Run `analyse_null_exemplar_sensitivity.py --stage filter` in a disposable clone (it also rewrites the committed `detections_manifest.json`, `:636`). Accept the regenerated inputs only if the regenerated manifest equals the committed one (every `n_features`, `n_dropped`, `n_kept`, and path), and if the legacy replay then reproduces each cell's committed confusion and intervals. A matching count is a tripwire, not proof (Wave 1 specification, W1.0). Any cell that fails is ledgered `failure: regeneration-mismatch` and left untouched. None is paper-cited |
| `results/verifier-t-pilot/` | 24 | `skip: no-recipe`. No references, bounds, or detection input recorded (`worklist.json` reasons). Left untouched and listed as not migrated (§ 8) |
| `results/retest/*-evaluation.json` | 12 | `skip: no-recipe`. No `_metadata` at all. They carry neither a tile block nor intervals. Left untouched and listed |
| `results/deployment-oracle-2026-06-06/preverifier-eval/` and `results/rescore-2026-05-31/` | 12 + 1 | § 5.3 |

### 5.2 The 60 files that `evaluate_detections.py` did not write

W1.0 counts 5 written by `compute_corrected_f1_multi_buffer.py` and 55
with no recorded writer (`dry-run.md` § 3.4). Of the 55, 36 are the
no-recipe files of § 5.1, which are skipped. The other 19 and the 5 make
24 live, paper-cited, 55-map files (§ 2 item 5). Before phase B:

- **Trace each writer's schema** field by field, as W1.0 § 3 did for the
  scorer. The output is a target and non-target schema per writer, added
  to `reports/tile-join-wave-2/`.
- **The five `compute_corrected_f1_multi_buffer.py` files** are re-scored
  through that engine's own path. Astra's C3 found that the engine does
  not route through `evaluate_detections.py`. The Wave 1 branch threads
  both rules through it (`55737337a`). The same two computations and G2
  guards apply, on its native schema.
- **The 19 files with no recorded writer** are re-scored by the driver only
  if their key structure matches the scorer's schema. A file that does not
  match is ledgered `skip`, `held:foreign-schema`, and goes to the PI at
  M2.
- **The eight files that do not round-trip** (§ 2 item 3) get a textual
  diff check against their own formatting. A re-serialisation that would
  reformat untouched lines is ledgered and reported, never silently
  accepted.

### 5.3 The 13 files whose detection input is absent on zbook

Twelve under `results/deployment-oracle-2026-06-06/preverifier-eval/`
(55-map) and one under `results/rescore-2026-05-31/` (GS). None is
paper-cited. W2.0 searches for each missing input: git history
(`git log --all -- <path>`), amd-tower's checkout, and the generating run's
output directory. An input that is found, and whose hash matches any
recorded hash, is used, and the file proceeds. Its replay is the identity
check. Otherwise the file is ledgered `skip`, `held:input-absent`, left
untouched, and listed as not migrated (§ 8). Sapphire is unreachable and
is not searched (Wave 1 specification, changelog of 2026-11-18).

### 5.4 Statuses

Every file ends with exactly one file-level status and one reason. Each
leg's outcome is recorded separately (§ 5.5).

| Status | Reasons |
|---|---|
| **success** | `rescored-in-place`; `counterpart-written`; `withheld-now-scored` (a `known-withheld` file whose replay ended in its recorded refusal and which scores under the new rules) |
| **expected refusal** | `new-rule-refusal:<reason>`: the new-rule leg ends in a refusal the library names (`tile_join_unattributed_detection`, `no_tiles_in_bounds`, `detections_have_no_source_tile`, or the shortfall reasons), with its diagnostics. The file is re-emitted in the scorer's withheld form, a target-set shape (`dry-run.md` § 3.2). For a `known-withheld` file, the reason is `still-withheld:<reason>` |
| **skip** | `not-tile-bearing`; `no-recipe`; `already-done` (on resume: the file's current SHA-256 equals the ledger's `sha256_after` under the same rule set); `held:seam-ruling`; `held:input-absent`; `held:foreign-schema`; `held:frame-sheet-check` (P4 stopped its frame) |
| **failure** | `replay-mismatch:<fields>`; `input-hash-mismatch`; `regeneration-mismatch`; `recipe-error:<message>`; `guard:<item>`; `unnamed-refusal`; `unexpected-content` (the current SHA-256 matches neither `sha256_before` nor `sha256_after`); `exception:<type>` |

A failed file is never written. A `skip` changes nothing. Whether a failure
also stops the run is decided by § 6.

### 5.5 Ledger schema

The ledger is append-only JSON Lines (JSONL), one record per file per
attempt, at `~/scratch/wave2/<run-id>/ledger.jsonl`. Each line is written
with `fsync`. The ledger is copied to `reports/tile-join-wave-2/ledger.jsonl`
at each commit. Fields:

- **identity**: `ledger_version`, `run_id`, `host`, `driver_commit`,
  `library_commit`, `rule_set` (classification join, count-table join,
  seam policy key and value or `null`; its hash is the `rule_set_id`);
- **worklist facts**: `path`, `worklist_status`, `disposition`,
  `paper_cited`, `corpus`, `frame`, `reference`, `construction_route`,
  `passes`, `buffers`, `metadata_version`;
- **inputs**: `sha256_before`, and `inputs[]` with `path`, `sha256`,
  `git_blob`, `recorded_git_blob`, and `matches`;
- **legs**: `replay` (outcome `reproduced`, `reproduced-recorded-refusal`,
  `mismatch`, or `error`; `recorded_rules`; `differences[]`); `compute`
  (outcome `scored` or `refused`; `reason`; `diagnostics`); `guards` (each
  G2 item `pass`, `fail`, or `n/a`, with details); `siblings`;
- **changes**: `targets_changed` (count by field), with the full per-field
  before and after in `diffs/<sha256 of path>.json`; `delta` (tile
  confusion and MCC before and after; flips of `coverage_status`,
  `ci_unreliable`, `ci_excludes_point`, and `sparse_coverage`; intervals
  before and after per buffer); `cross_sheet_tiles[]` (G2 item 4);
- **result**: `outputs[]` (path and `sha256_after`), `status`, `reason`;
- **cost**: `started_utc`, `finished_utc`, `wall_s`, `cpu_s` and
  `max_rss_mb` per leg, and `worker`.

`ledger-summary.json` reconciles the ledger to the worklist: one terminal
record per worklist path, and counts by status and reason that sum to
2,829.

### 5.6 Idempotence and resumability

- **Staged writes.** Each file is computed and checked in
  `<run-dir>/staging/<sha256 of path>/`. The siblings are moved into place
  first and `evaluation.json` last, each by an atomic `os.replace`. Then
  the ledger line is appended. The staging directory is kept until the run
  ends.
- **Resume.** On start, the driver reads the ledger. A file with a
  terminal record under the current `rule_set_id`, whose current SHA-256
  equals the recorded `sha256_after`, is `skip: already-done`. A file
  whose SHA-256 equals `sha256_before` is processed. A crash between the
  replace and the ledger line leaves a file whose SHA-256 equals its staged
  output: that is completed and recorded as success. Anything else is
  `failure: unexpected-content`, and the run stops (§ 6).
- **Idempotence.** Re-running the new-rule leg on a re-scored file yields
  byte-identical output: the replay leg now reads the file's own sheet-join
  records, and the compute leg reproduces them. The pilot shows this on
  every stratum. During the corpus run it is checked on a stratified
  sample of at least 5 % of files per phase, chosen by a seeded draw fixed
  before launch. A full second pass costs about half as much again
  (§ 7) and is the PI's choice (open question P8).
- **Never twice.** A held file is re-evaluated when its condition changes:
  a ruling recorded, or an input found. A succeeded file is never
  re-written under the same `rule_set_id`.

### 5.7 Launch discipline

The project's rules apply (`docs/agent-guidance.md`, "Compute Location"):

- launched detached on zbook as
  `ssh zbook 'cd <worktree>; nohup <python> scripts/tile_join_wave2_rescore.py ... > <run-dir>/run.log 2>&1 < /dev/null & echo $! > <run-dir>/run.pid'`,
  with all three descriptors redirected, setup separated by `;`, and
  nothing after the launch on the same line;
- the driver writes its own pid file as well, and a heartbeat line to its
  log at least every 60 s, so that log staleness works during long files;
- it ends with exactly one of `^WAVE2 COMPLETE`, `^WAVE2 PARTIAL`, or
  `^WAVE2 STOPPED`, followed by the summary counts. The watcher is
  `scripts/wait_for_run.py --pidfile ... --marker success='^WAVE2 COMPLETE'
  --marker partial='^WAVE2 (PARTIAL|STOPPED)'`, which keys on terminal
  state and log staleness. A chain proceeds only on exit 0;
- liveness is `kill -0 $(cat run.pid)` plus log age, never `pgrep -f` over
  `ssh`. Failure filters are case-insensitive
  (`grep -iE 'error|traceback|failed|partial|stopped'`);
- worker processes are separate operating-system processes (the scorer is
  single-threaded: CPU time ≈ wall time, `dry-run.md` § 8). The 55-map
  phase admits a new job only while the free-memory estimate allows it
  (§ 7).

## 6. Running unattended, and what stops it

D72 (3) says an overnight run "should just continue" past its priority
subset. A problem in one file is therefore ledgered and the run moves on,
unless the problem points to the code or the configuration rather than to
the file. **These stop the run** (and send the PI a push notification and
a written stop record):

- a non-target field changed, or a point F1, precision, or recall moved
  (G2 items 1–2), in any file: this is a code defect, not a file defect;
- a count-table sum mismatch, overall or per sheet (G2 item 5), or a
  reference-positive count that disagrees with the W2.0 recount (item 6);
- a sheet-specific difference from a historical contains reading on a tile
  that no other sheet's evidence reaches (item 4);
- an idempotence-sample mismatch (item 7);
- `unexpected-content`, an `unnamed-refusal`, or a write outside the target
  worktree, the counterpart tree, `reports/tile-join-wave-2/`, or the run
  directory;
- any 55-map file reaching the new-rule leg while its seam key is
  `pending`;
- a `replay-mismatch` on a **paper-cited** file, or more than a threshold
  of replay mismatches on other files. This draft proposes 10 in total
  (open question P9), because a burst suggests drift in the environment
  rather than in the files;
- a worker killed for memory, or swap in use on zbook;
- a map-content contact in a W2.0 sheet check (that frame only; the other
  frames continue);
- any decision this specification does not cover.

Not stops, but ledgered and reported at M2: a replay mismatch on a
non-cited file under the threshold; `skip` of any kind; an expected
refusal; `sibling-renderer-drift`.

## 7. Cost (measured, not guessed)

**Basis.** The only measurements are W1.0's eight legacy replays on zbook
(`reports/tile-join-wave-1/scripts/out/smoke_replay.json`; `dry-run.md`
§ 8), run eight at a time on 32 cores. Rates (CPU seconds; from
`wave2_scope_and_cost.txt` § 3):

| Rate | Value | From |
|---|---:|---|
| GS, per pass per buffer | 2.0329 s | the largest of cells 1 (20.51 / 14), 3 (28.46 / 14), and 5 (57.86 / 42): cell 3, the 512 px frame |
| GS, floor per pass | 4.19 s | cell 4 (one buffer) |
| 55-map, per pass per buffer | 9.5614 s | cell 2 (133.86 / 14) |
| replay ending in a recorded refusal, per pass | 9.16 s | the slowest of cells 6–8 |
| peak RSS | GS 296 MB; 55-map 2,095 MB | cells 1–8 |

**Per file.** For a GS file, legacy replay costs
passes × max(buffers × 2.0329, 4.19) s. For a 55-map file it costs
passes × max(buffers, 14) × 9.5614 s: no 55-map file with fewer buffers
was timed, so they are charged the full 14-buffer cost. The 1,032-tile
256 px frame was not timed either, and is charged at the 55-map rate. A
`known-withheld` file's replay costs 9.16 s per pass.

**Stated assumption.** The new-rule computation costs about as much as a
legacy replay, so each file's work roughly doubles: replay plus compute.
This is not measured. The sheet joins add a D50 scoping and per-sheet
candidate searches that the `id` join does not need. P3 (W1.5) and the
W2.2 pilot re-measure it, and the re-measurement replaces this section
before launch.

**Per class** (largest classes shown; every class is in
`wave2_scope_and_cost.txt` § 3):

| Class (corpus, tiles, passes × buffers) | Files | Arithmetic (replay + compute) | CPU-h |
|---|---:|---|---:|
| GS 487, 1 × 14 | 941 | 941 × 28.46 s compute = 7.44 h, plus replay 7.41 h (refusal replays are cheaper) | 14.85 |
| GS 340, 1 × 14 | 566 | 2 × 566 × 28.46 s | 8.95 |
| GS 340, 5 × 14 | 45 | 2 × 45 × 5 × 28.46 s | 3.56 |
| GS 467 (null-exemplar Era-2), 1 × 14 | 153 | 2 × 153 × 28.46 s, less the cheaper refusal replays | 2.40 |
| GS 315 (null-exemplar Era-1), 1, 3, 5 × 14 | 82 | 0.885 + 0.806 + 0.712 | 2.40 |
| GS 487, 1 × 4 | 329 | 2 × 329 × 8.13 s | 1.49 |
| GS 1,032 (256 px), 1 × 14 | 16 | 2 × 16 × 14 × 9.5614 s | 1.19 |
| Other GS classes | 327 | per class in the output | 6.21 |
| **GS total (phase A)** | **2,459** | | **41.05** |
| 55-map, 1 × 14 | 293 | replay (264 × 133.86 + 29 × 9.16) s = 9.89 h; compute 293 × 133.86 s = 10.89 h | 20.79 |
| 55-map, 1 × 3, 4, 5 | 27 | charged as 14 buffers | 2.01 |
| **55-map total (phase B)** | **320** | | **22.79** |
| **Aggregate** | **2,779** | | **63.84** |

The "other GS classes" row is the GS total less the rows above it
(41.05 − 34.84 = 6.21 CPU-h; 2,459 − 2,132 = 327 files).

**Workers.** zbook has 32 cores, 2 kept free, and 31 GB. In the 55-map
phase memory binds: (31 − 6) GB headroom-adjusted ÷ 2.046 GB per job
= 12.2, so **12 workers** (about 24.6 GB). The 6 GB margin covers the
operating system, the driver, and the new joins' unmeasured extra memory.
In the GS phase cores bind, not memory: 30 jobs would need about 8.7 GB.
The Wave 1 operating brief caps heavy jobs at **14 workers**, which this
draft uses. Raising it to 30 would cut phase A's wall-clock from 2.93 h to
1.37 h (open question P10).

**Wall-clock** (CPU-hours ÷ workers, assuming even packing; the longest
single file is 28.5 CPU-minutes, a 30-pass file, well inside each
phase):

| Phase | CPU-h | Workers | Wall-clock |
|---|---:|---:|---:|
| A, paper-cited only | 12.40 | 14 | 0.89 h |
| A, all | 41.05 | 14 | **2.93 h** (1.37 h at 30) |
| B, all | 22.79 | 12 | **1.90 h** |
| A + B | 63.84 | | **4.83 h** |
| A + B with a full idempotence pass instead of a sample | 61.59 + 34.69 = 96.28 | 14 / 12 | 4.40 + 2.89 = 7.29 h |

Not costed, because unmeasured: the W2.0 sheet checks, the null-exemplar
regeneration (its filter stage reads and writes GeoJSON), the five
`compute_corrected_f1_multi_buffer.py` re-scores, and contention at 12–14
concurrent jobs (the timings were taken at 8). The estimate leans high on
three counts: the GS rate is the costliest smoke cell's, short-buffer
55-map files are charged 14 buffers, and the 256 px frame is charged at
the 55-map rate. It leans low on one count: the new-rule leg may cost more
than a replay. On this projection, compute is hours, not days. The
schedule to 2026-11-29 is set by the rulings and reviews, not by compute.

## 8. Downstream dispositions (Astra's C1–C4, as they bear on Wave 2)

Wave 2 changes evaluation files only. It regenerates no tiering, Hsu set,
board, ladder table, leaderboard, manifest, or register rendering: those
are Wave 3's (parent record § 5). Astra's audit
(`~/agent-mail/codex/outbox/claude/20261118T122600Z-astra-tile-join-consumer-audit.md`)
bears on Wave 2 as follows.

| Finding | What Wave 2 does | Wave 3 |
|---|---|---|
| **C1**: the public resampling helpers (`bootstrap_ci`, the effect-size, multi-run, and interaction bootstraps, and `generate_report`) reached the count table without a join option at the audited base | Wave 2 uses only the scorer's path (`bootstrap_ci`, classification and its bootstrap), with both joins explicit. W1.1 threads all five helpers (`bf7186b71`) | The effect-size and interaction consumers Astra names (`analyse_phase2_results.py`, `analyse_study_effects.py`, `analyse_secondary_effects{,_text}.py`, `compute-pairwise-effect-sizes.py`, `evaluate_pv_results.py`, `evaluate_retest_all.py`) re-run in Wave 3 only where a cited artefact depends on them, after the integration check Astra asks for (one single-run, one multi-run, and one interaction route under each rule) |
| **C2**: the E81 driver could acquire the new semantics through a changed default | Not used to write (W2.1); only its pure `recover_recipe` is imported | E81 stays a historical tool, pinned to each record's own join on the Wave 1 branch |
| **C3**: `compute_corrected_f1_multi_buffer.py` and `score_detection_set` lose join provenance | The five stride55 files are re-scored through that engine with both rules recorded in its native schema (§ 5.2) | `score_detection_set` sweep consumers: disposition per call in the consumer-disposition record (P5); re-run only where cited |
| **C4**: `paired_mcc_permutation.py`, `pairwise_permutation_test.py`, and `build_pareto_v2.py` compute classification arrays on the default, and committed-record gates read confusion without provenance | Nothing: these read evaluations Wave 2 writes | Each re-runs in Wave 3 under the two-computation contract, validating every record under its own recorded rule, which after Wave 2 is the sheet joins |

**Which generators re-run in Wave 3.** These do: the wrappers W1.1 names
(`evaluate_detections.py`, `era1_leaderboard_tiering.py`,
`selection_aware_intervals.py`, `k_ladder_mcb.py`, `k_ladder_mcc_test.py`,
`mcc_tiering_55map.py`, `k_ladder_clipped_cells.py`), the C4 scripts, and
every other consumer in Astra's inventory that the consumer-disposition
record marks as feeding a cited artefact. The rest stay pinned to the
legacy rules (`e34a7e581`) as historical tools. Wave 2 hands Wave 3 one
input for this: `reports/tile-join-wave-2/downstream-inputs.json`, which
lists every re-scored evaluation path beside the committed artefacts that
name it (a text search of tracked files, indicative, as W1.0's searches
were).

**What stops an un-migrated generator from publishing an apparently
migrated result before Wave 3 regenerates it.** Four mechanisms. The
first two are in the Wave 1 code; the last two are proposed here.

1. **Pinned legacy rules.** Every deferred consumer calls its leaf with an
   explicit legacy join (`e34a7e581`), so what it computes itself does not
   change silently. This does not cover a generator that copies committed
   values out of an evaluation instead of recomputing them: after Wave 2,
   those values are the new ones. Mechanism 2 has to catch that case.
2. **Recorded-rule validation.** A migrated generator validates each input
   under the rule the input records (`recorded_tile_joins` on the Wave 1
   branch). It rejects contradictory provenance, and it rejects a new
   output that lacks provenance. A legacy-pinned generator that reads a
   re-scored evaluation therefore sees a sheet-join record. The
   consumer-disposition record must say, per generator, whether it refuses
   that mix or labels its output as legacy. A generator that does neither
   is a P5 finding.
3. **No merge before M3** (§ 3.3, proposed). `main` never holds re-scored
   evaluations beside downstream artefacts built from the old ones.
4. **A not-migrated register.** `reports/tile-join-wave-2/not-migrated.json`
   lists every in-scope file Wave 2 left on its legacy rules (skipped,
   held, or failed), with the reason. Wave 3 and Wave 4 check every cited
   path against it, and any hit blocks the "all settled" verdict (G4).
   Unmigrated files are not edited to carry a marker: they are not
   re-scored, so they are not touched.

## 9. Gate G2 (all must hold before M2)

From the parent record's § 5 Wave 2 row and Wave 1's G1.

1. **Non-target fields identical.** In every re-scored or counterpart file,
   every field outside W1.0's target set (`dry-run.md` § 3.2) and the
   provenance of W2.1 is value-identical to the committed file after
   parsing. For the 2,821 files that round-trip (§ 2 item 3), the file's
   text outside target lines is also byte-identical, trailing newline
   included. `version` and `timestamp` are unchanged.
2. **Point F1, precision, and recall identical** in every buffer and every
   pass (this is part of item 1, and is stated on its own because it is
   the registered primary outcome).
3. **Legacy replay first**, under each file's recorded rules, reproducing
   its committed confusion and intervals, or its recorded refusal, before
   any new value is written. A file that does not reproduce is left
   untouched and ledgered.
4. **Differences from the historical contains readings confined to
   cross-sheet tiles.** For every cell with a committed frame-wide contains
   reading (the board's 150 gates in
   `results/tile-join-audit/era2-board-mcc-tiering-2026-10-30/mcc-family-geometric-contains.json`,
   and the K-ladder's in `results/k-ladder-2026-09-12/mcc-join-2026-10-30/`),
   `sheet-contains` differs only on tiles that another sheet's evidence
   reaches. Every such tile is listed with its explanation. On the 55-map
   frame the expected differences depend on the seam ruling, and the
   comparison is made under it.
5. **Count tables sum** to the symbol-level totals, overall and per sheet,
   for every buffer and every pass.
6. **Reference-positive tiles** equal W2.0's independent recount for the
   file's (frame, reference) pair.
7. **Idempotent**: the stratified sample (§ 5.6), and the pilot's full
   double run, give byte-identical output. A resumed run reproduces the
   ledger.
8. **A reconciled ledger**: exactly one terminal record per worklist entry
   (2,829). Counts by status and reason sum to the worklist. Every file
   changed on `tile-join-wave-2` is a ledgered success output or a rebuilt
   roll-up (`git diff --name-only` against the merge base). Every
   paper-cited file in the phases M2 covers is a success or an expected
   refusal. A paper-cited skip or failure there blocks G2.
9. **Batch roll-ups** rebuilt and equal to a rebuild from their cells.
10. **Tests and lint**: tier 1 green on zbook at the post-merge reference
    count plus the driver's tests; `ruff check` and `npx markdownlint-cli2`
    clean on touched files.
11. **Audit**: a fresh-context `/audit` of the driver, with every finding
    resolved or given a written disposition (as G1 item 9), and Astra's
    review of this specification.

## 10. Outputs

- The driver and its tests on branch `tile-join-wave-2`; the re-scored
  files, siblings, and roll-ups on the same branch; counterparts under
  `results/tile-join-wave-2/counterparts/` (proposed).
- `reports/tile-join-wave-2/`, following the document revision policy:
  - `gs-sheet-check.md` (W2.0);
  - `pilot.md` and `pilot-ledger.jsonl` (W2.2), with the re-measured cost;
  - `ledger.jsonl`, `ledger-summary.json`, and `diffs/`;
  - `ledger-summary.md`: counts by status and reason; the tile-MCC change
    (ΔMCC) distribution by frame, corpus, construction route,
    replication, and paper citation; every interval, coverage-status,
    `ci_unreliable`, `ci_excludes_point`, and `sparse_coverage` flip;
    every expected refusal; the cross-sheet tile list of G2 item 4;
  - `seam-policy.json` and, for phase B, the ruling it encodes;
  - `not-migrated.json` (§ 8) and `downstream-inputs.json` (§ 8);
  - `foreign-writer-schemas.md` (§ 5.2);
  - `e93-before-after.json`: the paper-cited before and after values that
    erratum E93's table needs (parent record § 4 item 4). The erratum text
    itself remains Wave 4's, with the PI's approval.

## 11. Milestone M2: what the PI receives, and decides

M2 may be taken once, after both phases, or in two parts (M2-A after
phase A, M2-B after phase B), if the PI prefers to see the GS results while
the seam ruling is pending (open question P11).

The PI receives:

- the G2 checklist with the evidence for each item;
- `ledger-summary.md`: the ΔMCC distribution, every flip, every refusal,
  every skip and failure with its reason, and the not-migrated list;
- the cross-sheet tile explanations (G2 item 4);
- the re-measured cost against § 7's projection;
- the E93 before-and-after data;
- the downstream input list for Wave 3.

The PI decides:

1. **Accept G2**, or stop on a named item.
2. **Each not-migrated file**: leave it (it is not cited), re-run its
   writer, or withdraw it.
3. **Coverage and interval flips**, under the M1 decision on coverage
   flips (Wave 1 specification § 9, decision 2).
4. **Launch Wave 3** on `tile-join-wave-2`, and the merge timing (§ 3.3).

## 12. Open questions

### 12.1 For the PI

- **P1.** Does D73 (7)'s unattended mode extend to Wave 2, with § 6 as its
  stop list?
- **P2.** Split M1 so that Wave 2's GS phase can start before the seam
  ruling (GS smoke cells 1 and 3–8 now, cell 2 later), or keep M1 whole?
- **P3.** Should the seam ruling be made before any 55-map score is
  computed under any option, as proposed in § 3.2, or would you rather see
  each option's scores first? Seeing them first would make the ruling
  results-informed, and it would then need to be disclosed as such
  (D73 (1)).
- **P4.** Merge Wave 2 only together with Wave 3, after M3 (proposed), or
  at M2?
- **P5.** Which live directories, besides `archive/`, count as frozen
  under D73 (5)? (W1.0 open question 6; `dry-run.md` § 4.3.) The driver
  takes the list as an input.
- **P6.** Where do counterparts go? (Proposed:
  `results/tile-join-wave-2/counterparts/<original path>`.)
- **P7.** The null-exemplar leak filter drops detections by `source_tile`
  name (§ 2 item 6). Wave 2 re-scores the inputs as built. Should Wave 3
  instead rebuild the filter under the sheet joins? The sensitivity
  analysis also read pre-D50 evaluations (`withheld-37.md` § 3.3), so
  Wave 3 revisits it in any case.
- **P8.** Idempotence on a 5 % stratified sample (proposed), or a full
  second pass (+32.44 CPU-h, about +2.5 h wall-clock, § 7)?
- **P9.** The replay-mismatch threshold for non-cited files: 10 in total
  (proposed), or another number?
- **P10.** Raise phase A's worker count from the brief's 14 to 30? Memory
  allows it (§ 7). It would cut phase A's wall-clock from 2.93 h to
  1.37 h.
- **P11.** M2 whole, or in two parts (§ 11)?
- **P12.** The 46 `known-withheld` files outside W1.4 (W1.0 open question
  5): Wave 2 re-scores all 49 in place either way. Is the D73 (4)
  eligibility rule applied to the 46 when Wave 3 rebuilds their families,
  or do they simply re-score? 29 of them are 55-map files under
  `results/uplift-supplement/` (`wave2_scope_and_cost.txt` § 1; `dry-run.md`
  § 4.3).
- **P13.** The construction route is unknown for 79 paper-cited files (54
  materialisations that carry only `source_tile`, and 25 Era-1
  proposer-verifier accepted sets; W1.0 open question 4). The route does
  not change what Wave 2 computes, since D72 applies one rule to every
  file. It does change how a ΔMCC is read: on unmerged output, `id` was a
  valid rule, so a change there is a change of definition, not a
  correction. `ledger-summary.md` reports the 79 as their own stratum.
  Should their builders be traced before M2, or before Wave 4 interprets
  the deltas?
- **P14.** One evaluation records its frame and its reference as absolute
  paths: `archive/55maps-superseded-gt-evals/per-run/55maps-text-high-generalisation/mcc/evaluation.json`
  (`wave2_scope_and_cost.txt` § 2; W1.0 open question 7). It is an
  `archive/` counterpart in phase B. Proposed: resolve the prefix
  `/home/shawn/Code/map-reader-llm/` to the repository root for reading
  only, record the normalisation in the ledger, and leave the original
  untouched. Agree?

### 12.2 For Astra

- **A1.** Scope (§ 2 item 1): is it right to include the 149 live and 21
  archived files that carry intervals but no tile block, and the 5
  withheld files that carry neither, beyond the parent record's 2,646?
- **A2.** Siblings (W2.1 step 6): is regenerating `evaluation.md` with the
  current renderer, ledgering non-target Markdown drift rather than
  stopping on it, acceptable? The alternative is to patch target cells in
  place, as hand edits.
- **A3.** Is `sheet_join_candidate_tiles` (`32ebe3762`) a sufficient
  single hook for seam options (b, tile-only) and (d)? Or would either also
  need changes to the count-table population or the D50 scope?
- **A4.** Should a re-emitted file take the new `metadata_version` (1.5 on
  the Wave 1 branch)? If it does, `recorded_tile_joins` reads it as a new
  output and demands both records, which the re-emission writes. If it
  does not, the version understates the provenance the file carries.
  `metadata_version` is non-target in W1.0's schema.
- **A5.** Non-target keys that an older file lacks (for example
  `summary.detection_scope`): is leaving them absent, and recording the
  scope in the re-emission block instead (W2.1 step 4), the right reading
  of "surgical"?
- **A6.** Do the stop list (§ 6) and its split between run-stopping
  defects and ledgered file problems meet the M2 rule "any interval or
  guard failure = stop" (parent record § 5)? This draft reads a guard
  failure as a stop, and a replay mismatch on an uncited file as a
  ledgered file problem below a threshold.
- **A7.** Is a 5 % stratified idempotence sample, plus the pilot's full
  double run, enough for G2 item 7?

## Changelog

### 2026-11-19 — Original publication

First draft, written in S169 on amd-tower while Wave 1 is stopped on the
55-map seam ruling, from W1.0's census, worklist, replays, and timings
(`tile-join-wave-1-w10` at `89cab15ee`), Astra's consumer audit, and the
decision record and Wave 1 specification on `main` at `92064b134`. It
specifies the corpus re-score with the seam handling as an open parameter
and no position among the options, and projects the cost from
legacy-replay timings only. The new counts come from
`tile-join-wave-2-spec-2026-11-19-scripts/wave2_scope_and_cost.py`. Not
approved. For Astra's review.
