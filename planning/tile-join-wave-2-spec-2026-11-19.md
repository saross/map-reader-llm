# Tile-join Wave 2 — specification (the corpus re-score)

> **Last revised**: 2026-11-19 (seam-evidence refresh, Astra's patch adopted;
> technical review closed at `16354b73a`, with implementation notes in § 5.2).
> See [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), drafting for session S169 on amd-tower. Every path,
  count, line number, and timing below was read from the file named beside
  it, at these commits:
  - `main` at `92064b134` (first draft) and `d9f5d6096` and `3422ba329` (revisions):
    the decision record, the Wave 1 specification, D72 and D73, and
    `scripts/`;
  - branch `tile-join-wave-1-w10` at `89cab15ee` (W1.0's worklist and
    replay record) and `568a80689` (the corrected seam counts of
    `21cd6ef97`, and the GS-frame sheet check, `dry-run.md` § 2.3);
  - branch `tile-join-wave-1` at `a7989c47f` (first draft) and
    `f6f5ffe54` (this revision): the W1.1 code, still in progress. It is
    read for orientation and to verify review findings. This document
    specifies against the Wave 1 specification's contract, not against
    unfinished code.

  Astra's consumer audit was read at its audited base `e92d1c5d7`. New
  counts come from the read-only, standard-library planning script
  `planning/tile-join-wave-2-spec-2026-11-19-scripts/wave2_scope_and_cost.py`
  (output beside it as `wave2_scope_and_cost.txt`), run on amd-tower
  against the tracked evaluation files. Nothing was scored.
- **Parent**: `planning/tile-join-resolution-2026-11-01.md` (the decision
  record; this document specifies the Wave 2 row of its § 5). Sibling:
  `planning/tile-join-wave-1-spec-2026-11-01.md`, whose § 7 lists what must
  hold before Wave 2 may be called ready. Rulings: D72 and D73 in
  `planning/pi-decisions-2026-09-20.md`.
- **Status**: **DRAFT, revised after Astra's review
  (`~/agent-mail/codex/outbox/claude/20261118T133843Z-astra-wave2-spec-review.md`,
  "revise before launch approval"; round 2,
  `…/20261118T135814Z-astra-wave2-round2-review.md`, found W2-1, W2-3, and
  W2-4 addressed and asked for completion details on W2-2 and W2-5; round
  3, `…/20261118T140800Z-astra-wave2-round3-native-writers.md`, asked for
  three lifecycle cases and found the native-adapter writers;
  dispositions in § 13); not approved;
  Wave 1 stopped on the seam ruling (Wave 2 cannot launch until M1).** The
  55-map seam handling is an open parameter (§ 4), and this draft takes no
  position among the options.
- **Target**: all data and results settled, and the write-up begun, by
  **Sunday 2026-11-29** (PI, 2026-11-18).
- **Runs on**: zbook, unattended from launch to M2, stopping only on a
  problem (§ 6), as Wave 1 does under D73 (7), if the principal
  investigator (PI) extends that ruling to Wave 2 (open question P1).
  **Zero API calls.**

## 0. What Wave 2 does, in one paragraph

Wave 2 re-scores every committed evaluation whose tile classification or
interval arithmetic depends on a tile join, using the merged Wave 1 code.
Each file is first replayed under the rules it recorded, which must
reproduce its committed confusion and intervals (or its recorded refusal).
Every target field is then computed under the new rules: sheet-specific
containment for classification, and nearest-centre within the point's own
sheet for count tables. Only those fields, at structurally defined paths,
are spliced into the committed file. Every other field must stay identical,
and the file and its Markdown and comma-separated values (CSV) siblings
are checked and published as one bundle. Live files under `results/` are
re-scored in place. Files under `archive/` (and any other directory the PI
rules frozen) get labelled corrected counterparts elsewhere and are not
modified. Paper-cited files go first, then the rest, in the same run. The
gold-standard (GS) frames can run as soon as M1 allows. The 55-map files
wait for the PI's seam ruling and a complete seam-policy specification. A
new driver, written for this wave, does the work and records every file's
outcome, against its full computation identity, in a ledger that
reconciles to the W1.0 worklist.

## 1. Preconditions (launch is blocked until all hold)

| # | Precondition | How it is checked |
|---|---|---|
| P1 | **M1 passed** and the Wave 1 pull request (PR) merged, with gate G1 green (Wave 1 specification § 4, § 9). Today Wave 1 is stopped on the 55-map seam ruling (`reports/tile-join-wave-1/stop-2026-11-18-55map-seams.md`, on `tile-join-wave-1-w10`) | the PI's M1 decision; the merge commit on `main` |
| P2 | The Wave 1 specification's § 7 holds: a complete target and non-target schema (met: `dry-run.md` § 3); a small reference case checked independently of the scorer; an idempotent rerun; a reconciled worklist with every paper-cited file resolved (met: `dry-run.md` § 4.3, 0 paper-cited `unresolved-recipe`) | W1.5's smoke ledger; `worklist.json` |
| P3 | **W1.5 has re-measured the cost** with the new joins: wall-clock, CPU time, and peak resident set size (RSS) per smoke cell, replay and new-rule legs separately. § 7's projection uses legacy-replay timings only and is replaced by the re-measurement | `smoke-ledger.json` (Wave 1 § 8) |
| P4 | **Every GS frame in scope has had the sheet check. Met 2026-11-19.** `dry-run.md` § 2.3 (`tile-join-wave-1-w10` at `568a80689`; run at `cf15e9906`) checked all twelve GS frames that a tile-bearing evaluation uses. It found 243 cross-sheet contacts (237 padding, 0 ambiguous, 0 map content), and no cross-sheet reference pair within 500 m. The other 6 contacts are on H13 arm C tiles that are not on disk; the source scan puts those points 2,135.9–2,183.0 m beyond its right edge. 86 contacts on the H13 arms B and C were measured on substitute images of the same sheet, all padding. Every contact is the Era-2 pattern: Elenovo references in K-35-052-4's last column of tiles | `dry-run.md` § 2.3; `reports/tile-join-wave-1/scripts/out/sheet_check_gs_frames.txt` and `.json` |
| P5 | **The Wave 1 consumer-disposition record is committed** and reconciled with Astra's inventory (116 calls in 70 files outside the metrics library). It now exists on `tile-join-wave-1` at `f6f5ffe54`, as `reports/tile-join-wave-1/consumer-dispositions.md`. Its reconciliation with the inventory is part of Wave 1's review | the file on `main` after the Wave 1 merge; § 8 |
| P6 | **The PI has answered the open questions that the driver needs as inputs** (§ 12.1): the frozen-directory list (P5), the counterpart location (P6), and whether the stop rule is amended (P9) | the answers recorded in this document's changelog |
| P7 | **For phase B only (the 55-map files):** the seam ruling (§ 4) has been made, and its policy has been specified in full: the five components of § 4.2, and the schema amendment of § 4.3 if the ruling changes a reference or the frame. The ruling's parameters are written into the driver's configuration. Astra has reviewed the specification before any 55-map compute. Every option changes how a 55-map metric is computed, and the project requires cross-model review of such a change before compute (`docs/agent-guidance.md`, "Cross-model review of definition changes") | the ruling in `planning/pi-decisions-2026-09-20.md`; the policy specification; Astra's review by mail or committed file |
| P8 | zbook's `.venv` still matches the reference environment, and zbook's checkout is on `origin/main`, clean, 0 behind (as Wave 1's P3 and P4) | `uv pip freeze` against `requirements-lock.txt`; tier 1 at the post-merge count; `git status -sb` |
| P9 | **The missing-input list is enumerated and committed before launch**: the 13 files of § 5.3, after W2.0's search. Only these may be held for a missing input (§ 6) | `reports/tile-join-wave-2/missing-inputs.json` |

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
   rules (`wave2_scope_and_cost.txt` § 1b). All of them are in scope
   (§ 3.1). Astra recounted the 149, 21, and 5 independently and agreed
   (§ 13). Scoring a withheld file does not admit it to any inferential
   family: that stays with the fixed eligibility rule (D73 (4)).
2. **W1.0's determinism replays covered two schema strata out of several.**
   The eight smoke cells have `_metadata.metadata_version` 1.3 or 1.4
   (`wave2_scope_and_cost.txt` § 5). The files in scope also include
   versions 1.0 (5 files) and 1.1 (27). There are also 24 files with no
   version: the 55-map native-adapter files (§ 5.2). All 761
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
   ways. All 8 are native-adapter views of 55-map files (§ 5.2): three
   from `register_gemini37_author.py` and five from
   `register_pass1_adapt.py` (`wave2_scope_and_cost.txt` § 4). For the other 2,821 files,
   re-serialising the parsed document reproduces the file, so the
   structural splice of W2.1 changes only the text it is meant to change
   (W2-5; § 9 item 1).
4. **`write_outputs` overwrites two non-target fields.** It stamps
   `version` and `timestamp` afresh (`evaluate_detections.py:1882–1883`),
   and E81's re-emission went through it (`rescore_tile_mcc_e81.py:392–397`).
   `version` is non-target in W1.0's schema (`dry-run.md` § 3.3). A
   surgical re-emission must therefore keep the original `version` and
   `timestamp`. It must not call `write_outputs` on the whole document.
5. **The non-scorer files are adapted views of a different engine's
   output** (Astra's round-3 native-writer audit, verified here). The 24
   live files in scope that `evaluate_detections.py` did not write are
   all 55-map and all paper-cited. Every one records the adapter that
   wrote it, in `_metadata.adapter` or `_metadata.adapted_by`, even where
   `script_path` is absent. Every one also records its source, the
   corrected-F1 engine's native `summary.json` in the same directory:
   - `scripts/adapt_track2_evals_for_manifest.py`: 8, under
     `results/55maps-extended-gt-2026-06-07/`;
   - `scripts/register_standardised_gt_conditions.py`: 8, under
     `results/55maps-standardised-ref-2026-08-14/`;
   - `scripts/register_gemini37_author.py`: 3, under
     `results/gemini37-55map-2026-08-31/` (2) and
     `results/gemini37-fourth-cell/` (1);
   - `scripts/register_pass1_adapt.py`: 5, under
     `results/stride55-2026-08-27/`. These also record `script_path`
     `scripts/compute_corrected_f1_multi_buffer.py`.

   They are now a disposition of their own, `rescore-native` (§ 3.1,
   § 5.2). The first draft's "19 with no recorded writer" was wrong.
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
7. **The shared booking hook is not a seam policy** (Astra W2-1, verified
   at `f6f5ffe54`). `sheet_join_candidate_tiles`
   (`scripts/lib_advanced_metrics.py:3202`) takes no argument for purpose
   (classification or count table) or side (reference or detection). The
   classification path calls it for both sides (`:3429`, inside a loop over
   detections and references), and the count-table path calls it for both
   sides again (`:3843`, `:3846`). A change meant for reference-positive
   classification would therefore also move detection booking and the
   count tables. Widening the candidates can also book an outcome to
   another sheet's tile, against the per-sheet conservation check. The
   populations are fixed earlier, by `iter_sheet_scopes` (`:2723`), which
   scopes each sheet's points before the hook runs. The hook cannot
   restore a point that scoping excluded. Giving a retained point no
   candidate does not remove a tile from the classification denominator;
   it leaves the population unchanged and can trigger a booking shortfall.
   The hook's docstring at `f6f5ffe54` still says that a seam ruling "is a
   change here alone" (`:3216–3220`). The main session will have it
   corrected. This document makes no such claim (§ 4.2).

## 3. Scope and order

### 3.1 Disposition of every worklist entry

The W1.0 worklist (`reports/tile-join-wave-1/worklist.json`, 2,829
entries) gives each file a status. The driver maps status to disposition
by the rules in `wave2_scope_and_cost.py` `disposition()`:

| Disposition | GS | 55-map | No frame | Of which paper-cited | Basis |
|---|---:|---:|---:|---:|---|
| `rescore-in-place` | 2,184 | 285 | — | 737 (608 GS, 129 55-map) | `reproducible-legacy` with a tile block or intervals and no native adapter (2,420), plus all 49 `known-withheld` |
| `rescore-native` | — | 24 | — | 24 | `reproducible-legacy` files that record a native adapter: re-scored through the corrected-F1 engine and their adapter (§ 5.2), never through the scorer |
| `counterpart` | 43 | 11 | — | 0 | `historical-only` (`archive/`); all 54 carry intervals, and 33 also a tile block |
| `regenerate-then-rescore` | 232 | — | — | 0 | the null-exemplar `unresolved-recipe` cells (§ 5.1) |
| `hold:input-absent` | 1 | 12 | — | 0 | `unresolved-recipe`: detection input absent on zbook (§ 5.3) |
| `skip:no-recipe` | — | — | 36 | 0 | `unresolved-recipe`: `results/verifier-t-pilot/` 24 and `results/retest/` 12 record no recipe (§ 5.1) |
| `skip:not-tile-bearing` | 1 | — | — | 0 | `reproducible-legacy` with neither a tile block nor intervals |
| **Total** | 2,461 | 332 | 36 | 761 | 2,829 |

Source: `wave2_scope_and_cost.txt` § 1. The 2,779 files that the driver
re-scores or counterparts are 2,459 GS and 320 55-map files (§ 3 of the
same output).

### 3.2 Order

D72 (3): paper-cited first, then the rest, without stopping between them
if the run can carry on. The seam ruling splits the run into two phases:

| Phase | Files | Needs | Order inside |
|---|---|---|---|
| **A** (GS frames) | 2,459: 608 paper-cited, 1,851 not (including 43 counterparts and 232 regenerated null-exemplar cells) | P1–P6, P8, and P9 | paper-cited first; then the rest; counterparts last |
| **B** (55-map frame) | 320: 153 paper-cited, 167 not (including 11 counterparts) | P1–P9, so the seam ruling and its specification (P7) | the same |

Phase A's frames are the 384 px full frame (1,105 files), the 512 px full
frame (739), the Era-2 B intersection (254), the two null-exemplar reduced
frames (153 and 82), the grid common frame (64), the H10 test frame (40),
the 256 px full frame (16), and the H13 common frame and arms (6). Their
tile counts are 487, 340, 487, 467 and 315, 487, 327, 1,032, and 340 to
999. Every phase A file uses `inputs/vectors/references/mounds-reference.geojson`
(`wave2_scope_and_cost.txt` § 2). These are the twelve frames
`dry-run.md` § 2.3 checked (P4).

**Before the seam ruling, phase B computes nothing under the new rules.**
What it may do in the meantime, once M1 has passed, is the legacy-replay
leg alone. That leg replays each 55-map file under its recorded rules,
does not depend on the ruling, and computes no corrected score, so it is
outside the stop record's pause (§ 3 there). Each file is then ledgered
`skip`, `held:seam-ruling`, with its replay outcome, so replay failures
surface early. Under § 6 the first replay failure stops even this leg.
The replay is repeated when phase B runs, because the computation
identity then differs (§ 5.6). That costs 10.89 CPU-hours more, about
0.9 h at 12 workers (§ 7). This draft also proposes that no 55-map score
under any seam option be computed before the ruling, so that the ruling is
not made with its results in view (open question P3).

### 3.3 Merging

Wave 2 writes on branch `tile-join-wave-2`, in a zbook worktree, and
commits in batches (one commit per top-level results directory, each
carrying its ledger counts in the body). It pushes the branch and does
not merge it. This draft proposes that Wave 3 branch from
`tile-join-wave-2` and that both merge after M3. `main` would then never
hold re-scored evaluations beside downstream artefacts built from the old
ones (§ 8; open question P4).

## 4. The seam parameter (open; the PI rules)

### 4.1 What is measured, what has been seen, and what is not adjudicated

This section follows the corrected pixel-convention and own-sheet
measurements in `reports/tile-join-wave-1/dry-run.md` §§ 2–2.4 and
`reports/tile-join-wave-1/stop-2026-11-18-55map-seams.md` §§ 1–5, read at
`b0ca4983409bd63526cc15a6e6dc46619c03b1ff`. The earlier evidence summary
predated those corrections; the original counts and interpretations remain
in the source records' changelogs.

- **Measured: projections onto map content.** On the 55-map frame, some
  references recorded on one sheet project onto the map content of an
  adjacent sheet's tile. The pixel test is a padding or content
  diagnostic, not a mound detector. In `best-available-gt-55maps-r2.geojson`
  there are 34 such contacts, from 27 distinct (reference, recipient sheet)
  pairs. With the 16 ambiguous contacts, there are 50 contacts from 40
  pairs. Each of the other four tracked reference files shows 34–37
  map-content contacts. No reference on the recipient sheet lies within
  50 m of any r2 non-padding contact. That establishes the absence of a
  local annotation, not the identity of anything printed there.
- **Seen: recipient-sheet examples.** In the inspected crops of r2
  `student:01862` and `student:02387`, a printed mound symbol lies at
  the projected point on the recipient sheet. The paired views show both
  recorded points in padding on their own labelled sheets. The recipient
  crops therefore establish a printed symbol there, not a second copy
  across the seam (stop record § 2).
- **Measured: own-sheet attribution concern.** Of the 27 r2 references
  with recipient map content, 25 have padding at the recorded coordinate
  on their own labelled sheet, `student:02194` is ambiguous, and
  `student:04282` has weak map-content verdicts on both sheets. The
  corrected containing-pixel convention moves the latter's two recipient
  contacts from ambiguous to map content. Its own and recipient windows
  are just below the classifier's near-black threshold; neither verdict
  establishes a complete mound symbol or its identity (stop record § 5).
- **Not adjudicated: source and identity.** A wrong sheet label and a
  displaced counterpart needing its own sheet-specific centre remain
  distinct possibilities. Padding at the recorded point excludes a copy
  there, but does not exclude a displaced copy elsewhere. The attribution
  concern predates centre marking and traces back to the imported labels;
  the import's exact assignment method is not recovered. The canonical
  r50 file's `phantom:*` references lie within 50 m of 29 of its 35
  recipient map-content contacts. Proximity is a lead, not confirmation of
  identity. No candidate is adjudicated by these measurements alone.

**The scientific question now includes reference attribution.** Correcting
an erroneous sheet label, assigning a displaced counterpart its own centre,
and adding a genuine second printed copy are different interventions.
Adding a copy indiscriminately can retain a false instance in padding on
the wrong sheet. Any reference correction needs paired-image adjudication
and the separate correction leg in § 4.3.

A wrong attribution can already affect symbol matching under D50, whatever
the tile join: an own-sheet reference may be unmatched, and a correct
recipient-sheet detection may lack a reference. These are possible effects,
not measured false positives, false negatives, or F1 changes; the actual
result also depends on detections and the matching radius. At tile level,
the original addition counterfactual changes only a contacted tile that
holds none of its own sheet's references. It turns 11 of 28 contacted r2
tiles positive. It does not measure the effect of correcting labels or
centres (`dry-run.md` § 2.2; stop record §§ 1 and 5).

The stop record § 4 preserves the original four join/copy options, and § 5
explains how the own-sheet evidence changes their interpretation. **This
document takes no position among them and does not select a reference
correction.** Astra's original conditional preference for adding confirmed
copies was not a ruling or authority to retain incorrectly attributed
instances. The sections below state what an implementable policy must
specify (§ 4.2), what a reference or frame change adds (§ 4.3), and the
original counterfactual measurements (§ 4.4).

**The parameter is keyed by (frame, reference file),** because the
contacts are measured per reference file and differ between them. The
paper-cited 55-map files use four references: r2 104, the earlier
best-available file 28, the reviewed student file 13, and canonical r50 8.
The non-cited files also use the unreviewed student file
(`wave2_scope_and_cost.txt` § 2). The driver reads a committed
configuration, `reports/tile-join-wave-2/seam-policy.json`. Its default
for every 55-map key is `pending`, under which the driver holds the file
(§ 5.4: status `skip`, reason `held:seam-ruling`).

### 4.2 What a seam policy must specify (Astra W2-1)

A ruling is not implementable by changing the shared booking hook alone
(§ 2 item 7). Before phase B, the policy states each of these five
components on its own. It also states, for each one, whether it applies
to references, to detections, or to both:

1. **The symbol-matching population**: which references and detections
   each sheet's matcher sees (today, `iter_sheet_scopes`, the D50 scope).
2. **Reference-positive tiles**: which tiles a reference makes positive.
3. **Detection-positive tiles**: which tiles a detection makes positive.
4. **The classification denominator**: which tiles are classified at all.
5. **The count-table population and booking**: which outcomes enter the
   per-tile tables, and to which tile each is booked.

**Separation rules.** A policy that touches classification only (items
2–4) must not reach count-table booking (item 5). The implementation must
therefore pass purpose and side to whatever decides candidates, or use
separate functions. A tier 1 test shows that the count tables are
byte-identical to the unmodified sheet-join tables under such a policy.
A policy that excludes tiles or points from the count tables must also
state its consequences for coverage (`coverage.n_tiles` and the zero
fraction), for the matching scope, and for the per-sheet conservation
check (G2 item 5). Each of those then becomes a target field under the
schema amendment of § 4.3. The current D73 implementation does not
acquire any speculative exception in advance.

The table below describes the four originally framed options. A sheet-label
correction or a sheet-specific centre correction also needs all five
components specified; it must not inherit the addition counts or effects
from option (a). The ruling's specification fixes every cell, including
those marked "to state":

| Component | (a) second-copy references | (b) seam exception | (c) frame-wide on the 55-map frame | (d) seam-tile exclusion |
|---|---|---|---|---|
| 1. Matching population | changes: references gain the adjudicated copies (a new reference version, § 4.3) | matching reading: changes (a detection may match a reference from either sheet on the overlap); tile-only reading: unchanged | unchanged; it does not repair symbol-level matching of an unannotated copy (Astra) | unchanged, unless the mask also enters matching (to state) |
| 2. Reference-positive tiles | follow from the new references under `sheet-contains` | tile-only: the contacted tile is also positive for the listed contacts | frame-wide containment (`geometric-contains`) | the masked tiles are not classified |
| 3. Detection-positive tiles | unchanged rule | to state: whether a detection on the overlap also books to the other sheet's tile | frame-wide containment | the masked tiles are not classified |
| 4. Classification denominator | unchanged (8,541 tiles) | unchanged | unchanged | reduced by the mask |
| 5. Count-table population and booking | `sheet-primary` over the new references; per-sheet conservation holds | to state; a tile-only exception must not reach it | to state (frame-wide `geometric-primary` is the existing counterpart) | to state; if the mask enters, coverage, matching scope, and conservation consequences are stated |

### 4.3 A reference or frame change needs a schema amendment (Astra W2-3)

A sheet-label or centre correction, option (a), option (b) read as a
matching change, and option (d) if its mask enters matching or the count
tables change what the evaluation measures, not only how tiles are joined.
The policy then also states:

- **The affected targets.** Beyond W1.0's target set, these include
  everything that symbol matching determines: the point F1, precision, and
  recall; the reference counts; the per-sheet confusions; and anything
  derived from them. For (d), they also include the coverage fields that
  W1.0 classes as non-target (`dry-run.md` § 3.3).
- **The recorded inputs.** `_metadata.cli_args` (`ground_truth`, `bounds`,
  and any mask), `_metadata.input_files`, and `_metadata.input_git_state`
  describe the effective new inputs, with their hashes. The originals are
  kept in the re-emission history (§ 5.6).
- **The comparison baselines.** The two effects stay separate, as the
  accepted E93 draft requires:
  1. **The join-only effect.** The recorded references and frame are held
     fixed and only the joins change. This is the in-place re-emission of
     W2.1, and G2 applies to it unchanged, point estimates included.
  2. **The reference or frame correction.** This is a separate
     computation, whose baseline is the join-only result. It has its own
     timing, inputs, identity, ledger legs, and gate items. Its point
     estimates may move, and the gate states how each move is explained.
     It is written as a separate, labelled evaluation, beside the
     join-only one, never over it. The proposed location is
     `results/tile-join-wave-2/reference-corrected/<reference version>/<original path>`.
     Which of the two the paper cites is part of the ruling (open question
     P15).
- **An effective recipe that can be reconstructed from the new artefact.**
  Recipe recovery (`recover_recipe`) reads `_metadata.cli_args` and
  `input_files`. These are rewritten to the effective recipe: the actual
  reference, frame or mask, both joins, and input hashes. A later replay of
  the new artefact therefore uses its effective inputs, and never remaps
  the historical ones again. The ledger labels each leg's inputs
  separately (`replay_inputs`, `compute_inputs`; § 5.5).

### 4.4 Measured facts that bear on the options

| Option | Original counterfactual on r2, relative to sheet-specific containment (`dry-run.md` § 2.2 at `b0ca4983409bd63526cc15a6e6dc46619c03b1ff`) |
|---|---|
| (a) | 27 references would be added for the map-content contacts, turning 11 of 28 contacted tiles positive; 40 references and 17 tiles if the ambiguous contacts are included. Canonical r50 already carries a `phantom:*` reference within 50 m of 29 of its 35 map-content contacts, so this counterfactual would add 5 references and no tile would move |
| (b), tile-only | the same tiles as (a): 11, or 17 with the ambiguous contacts |
| (c) | 333 tiles turn positive: 11 hold map-content contacts, 6 hold only ambiguous contacts, and 316 hold only padding contacts, with no remainder |
| (d) | 55 tiles removed (44 positive, 11 negative), or 85 (68 and 17) with the ambiguous contacts |

These are measurements of the originally proposed hypothetical rules, not
approved reference additions. They are not predictions for correcting
sheet labels or centres: those interventions have not been adjudicated or
measured.

**Sub-parameter, whichever option is chosen:** whether the ambiguous
contacts (16 on r2, points on the black edge of the map face) count with
the map-content contacts (stop record § 4, item 3).

**Interim:** phase A runs, and phase B waits (§ 3.2). The driver refuses
to compute any 55-map file under the new rules while its key is
`pending`. A refused attempt is a § 6 stop, because it means the
configuration was bypassed.

## 5. Work items

### W2.0 Preconditions and the independent recount (read-only, first)

- Confirm P1–P9, and record the evidence in the run directory. The GS
  sheet check (P4) is done (`dry-run.md` § 2.3).
- **The independent reference recount** (as G1 item 4), once per (frame,
  reference) pair rather than once per file: the number of tiles holding
  at least one of their own sheet's references, computed without the
  scorer. Every re-scored file's reference-positive count must equal it
  (G2 item 6).
- **The missing-input search** of § 5.3, which ends in the committed list
  of P9.
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
`rewrite_cell`. At the audited base those call classification without a
join (`:310–314`, the dependence Astra's C2 names), guard on confusion
counts alone (`:317–328`), and rewrite through `write_outputs`
(`:392–397`). The Wave 1 code has since pinned E81 to each record's own
join. Wave 2 still does not depend on it, and E81 stays a historical tool.
Every library call the driver makes passes the classification join and the
count-table join explicitly. It reads no default, so a later change of
default cannot change its meaning.

**Inputs:**

- the W1.0 worklist (pinned by commit and SHA-256);
- `seam-policy.json` (§ 4), a frozen-prefix list (default `archive/`;
  open question P5), and `missing-inputs.json` (P9);
- the data root, zbook's main checkout, read-only, for gitignored inputs;
- the target worktree, the `tile-join-wave-2` checkout on zbook;
- a run directory in zbook scratch, `~/scratch/wave2/<run-id>/`.

**Per file, in order** (the Wave 1 specification's "two computations, in
order", W1.1):

1. **Identity.** Hash every member of the committed bundle (SHA-256 of
   `evaluation.json` and of each sibling present). Recover the recipe, hash
   every input, and compare each with any recorded git blob hash. Compute
   the file's computation identity (§ 5.6).
2. **Legacy replay.** Score under the file's recorded rules: the recorded
   classification join, else `id`; the recorded count-table join, else the
   legacy name rule. Compare every committed field, treating a key absent
   from an older file as "not recorded", not as drift (`dry-run.md` § 7).
   For a `known-withheld` file, the replay must end in its recorded
   refusal with its recorded counts.
3. **New-rule compute.** Compute every target field (`dry-run.md` § 3.2)
   under classification `sheet-contains` and count table `sheet-primary`,
   or under the frame's specified seam policy for phase B.
4. **Splice** (Astra W2-5). The driver edits a parsed copy of the
   committed document at **structural target paths** only. These are JSON
   Pointer patterns, committed before launch in
   `reports/tile-join-wave-2/target-paths.json`. They are generated from
   W1.0's target set (`dry-run.md` § 3.2) and the provenance paths below,
   and each writer adapter (§ 5.2) has its own set. Examples are
   `/summary/tile_classification`, `/summary/buffers/*/f1_ci_lower`,
   `/per_run/*/buffers/*/coverage/coverage_status`, and
   `/_metadata/metadata_version`. Everything else keeps its parsed value.
   `version` and `timestamp` are kept. A non-target key that the committed
   file lacks (for example `summary.detection_scope`) stays absent. Only the
   specified provenance and schema-migration fields are added (§ 13, A5).
   **Representation rule.** The edited document is serialised exactly as
   the scorer serialises: `json.dumps(document, indent=2)`, plus one
   trailing newline if and only if the committed file had one. New numbers
   therefore take Python's shortest round-trip `repr`, as every scorer
   output does. This rule applies only to the 2,821 files that round-trip
   (§ 2 item 3). For those files, re-serialising the unedited parse is
   byte-identical, so this is a token-preserving edit. The 8 files that do
   not round-trip are native-adapter views, which are regenerated by their
   migration adapter, with its serialisation pinned by the adapter-replay
   check (§ 5.2).
5. **Guards** (G2 items 1–6, per file) on the staged bundle, including the
   textual guard of G2 item 1.
6. **Siblings** (Astra W2-5; § 13, A2). The driver regenerates
   `evaluation.md` and `evaluation.csv` from the spliced document, but only
   where the committed directory has them; it creates no file that did not
   exist. It then compares old and new siblings for **scientific content**,
   cell by cell (Astra R2-3):
   - **Keyed cells.** Both siblings are parsed into canonical non-target
     cells, each keyed by its scientific identity: (section or table, row
     label, buffer, column, metric, unit). The CSV's columns come from its
     header; the Markdown's from each table's header row and its section
     heading. A cell's canonical value is its parsed number with its unit
     (so `0.8610` and `0.861` are equal; `86.1 %` and `0.861` are not),
     or its exact text if it is not a number. Target cells and target
     footnotes (`dry-run.md` § 3.2) are excluded by key. Every non-target
     key must exist in both siblings with an equal canonical value. A
     changed value, a missing or extra key (a changed population of rows,
     buffers, or results), or two values that trade keys is a guard
     failure, `guard:sibling-content`. A multiset of numbers is not used,
     because swapping two values would preserve it.
   - **Wording outside the cells.** Header lines, notes, and non-target
     footnotes are compared after normalising whitespace. Every changed
     passage must match a class on the **wording allowlist**,
     `reports/tile-join-wave-2/sibling-wording-allowlist.json`. Each entry
     holds a before pattern, an after pattern, the strata it was seen in,
     and who approved it. The pilot builds the list: it reviews every
     distinct wording change it meets and enters only those it approves.
     During the corpus run, a matching change is ledgered as
     `sibling-layout-drift`, with its diff. **An unseen wording change is
     never published automatically.** The bundle is not published, the file
     is ledgered `skip`, `held:sibling-review`, with its diff, and the run
     continues. Held files are reviewed before M2: an approved class joins
     the allowlist, and the file is reprocessed. A paper-cited file still
     held blocks G2 (item 8). Astra's example shows why: "includes" changed
     to "excludes" keeps every number and reverses an interval's
     interpretation.

   **The JSON and its siblings are one bundle**: they are checked,
   published, and recovered together (§ 5.6).
7. **Publish** the bundle through the staged manifest (§ 5.6), into the
   target worktree (in-place re-score) or the counterpart tree. Then
   append the ledger record.

**Provenance and schema migration written into each re-scored file.**

- The fields W1.1 defines: `tile_join` in every tile block,
  `count_table_join` on every block whose intervals or coverage come from
  a count table, and both in `_metadata` with the D72 and D73 pointer.
- `_metadata.cli_args` describes the effective recipe: `tile_join` (a
  W1.0 target field) and `count_table_join` updated; every other argument
  unchanged for a join-only re-emission, or amended under § 4.3. This
  avoids pairing old invocation metadata with new-rule blocks (Astra C2's
  concern).
- **`_metadata.metadata_version` migrates to `"1.5"`** (§ 13, A4). This is
  added to the authorised target schema. It is the version from which the
  Wave 1 writer records both rules (`evaluate_detections.py:820` at
  `f6f5ffe54`), and from which `recorded_tile_joins` demands both records
  (`lib_advanced_metrics.py:513–514`). The re-emission writes both. The
  migration claims nothing else: the history entry records the prior
  version and states that only tile-join provenance was migrated. Other
  legacy schema fields are not upgraded, and keys the file lacked stay
  absent.
- **The bootstrap-migration census** (Astra R2-4, A10). One other script
  reads the version. `rerun_bca_corpus.py` selects vintages `"1.1"` and
  `"1.2"` for its bootstrap re-emission. It treats `"1.3"` and `"1.4"` as
  done, because they "already carry a BCa-requested bootstrap"
  (`:106–110` at `f6f5ffe54`; read at `:146–150`). "Done" there means
  bootstrap completion. A file migrated to 1.5 by Wave 2 has only its
  tile-join provenance migrated, so 1.5 alone does not mean done. The
  census must not infer one from the other. Wave 2's code therefore
  classifies a 1.5 file by its **recorded prior vintage**: the
  `prior_metadata_version` of the first entry in
  `_metadata.tile_join_reemission`.
  - A prior vintage in the done set (`"1.3"`, `"1.4"`) counts as done, but
    only after the census also confirms that the file's
    `_metadata.bootstrap` records a BCa-requested bootstrap.
  - A prior vintage in the selected set (`"1.1"`, `"1.2"`) is still
    selected.
  - Anything else goes into its own census category,
    `join-migrated-other-vintage`, reported with its prior vintage. That
    covers 1.0, an unversioned file, or a 1.5 file with no history.
  - A 1.5 file written by the Wave 1 scorer itself (no re-emission
    history, both rules recorded) counts as done only after the same
    bootstrap-field check. This draft has not verified what that writer
    requests.

  Tests cover a prior-done file (1.3 → 1.5: done), a legacy file upgraded
  only for joins (1.0 → 1.5: not done, own category), a 1.1 file
  (→ 1.5: still selected), and a scorer-written 1.5 file. In live files
  this matters now for two 1.0 files that Wave 2 re-scores in place
  (`wave2_scope_and_cost.txt` § 5). The 1.0 and 1.1 counterparts are under
  `archive/`, which the census skips (`:139`). The 24 native-adapter
  files carry no version, and their percentile intervals are the native
  engine's intended estimator, not missing BCa metadata (§ 5.2). After
  migration they fall in `join-migrated-other-vintage`, and no generic
  writer may fill in a bootstrap method for them. Astra's cross-check found that the live 1.2 records are the
  pre-enumerated missing-input cases (§ 5.3), which Wave 2 does not
  migrate.
- **`_metadata.tile_join_reemission`**, the re-emission history. It holds
  a list of entries, one per distinct computation identity, in order. Each
  entry records:
  - the identity hash and its components (§ 5.6);
  - the driver path and commit, and the library commit;
  - the date of first publication;
  - the rulings, and for phase B the seam-policy key and value;
  - `original_bundle[]`: for every pre-migration bundle member, its path,
    the git commit and blob object it was read from, and its SHA-256
    (§ 5.6);
  - the prior `metadata_version`;
  - the replaced `cli_args`, `input_files`, and `input_git_state`;
  - the recorded rules it replayed under;
  - the D50 scope summary;
  - for a counterpart, `counterpart_of` (path and SHA-256);
  - for every entry after the first, `supersedes` (the previous identity
    hash) and a stated `reason`.

**Counterparts** (D73 (5)). The original stays byte-identical. The
corrected bundle is written at
`results/tile-join-wave-2/counterparts/<original path>`. This location is
a proposal (open question P6).

**Batch roll-ups.** Seven live directories carry a `batch_summary.json`:
`results/paper-eval/mcc/{384px,512px}/`,
`results/paper-eval/n1/384px-14buf-mcc/` and its `pro-rerun/`, and
`results/paper-eval/n1/{384px-all-buffers,512px-all-buffers,512px}/`.
Each one whose cells are re-scored is rebuilt from them afterwards, as
E81 did (`rebuild_batch_summary`, `rescore_tile_mcc_e81.py:400–434`). The
rebuild keeps the original `version` and `timestamp`, as in step 4, and is
published as its own bundle (`batch_summary.{json,csv,md}`). The two
roll-ups under `archive/` get counterparts.

### W2.2 Pilot (before the corpus run)

The W1.5 smoke run proves the code on eight cells. The pilot proves the
driver on the corpus's strata. It writes into a disposable copy of the
branch, not the branch itself. It takes at least one file from every
populated cell of frame × `metadata_version` × interval method ×
coverage block × replication × route × status (§ 2 item 2;
`wave2_scope_and_cost.txt` § 5). That includes the 1.0 and 1.1
counterparts, a 30-pass file, a `known-withheld` file, a regenerated
null-exemplar cell, and a batch root. The pilot:

- records each leg's timing and peak RSS **at the intended worker count**,
  so that concurrency is sized from memory measured under that load;
- runs the interruption tests of § 5.6 on real bundles;
- runs the full driver twice, forcing recomputation on the second run
  (§ 5.6), and shows byte-identical bundles and a reproduced ledger;
- reviews every distinct sibling wording change it meets, and enters the
  approved classes in the wording allowlist the corpus run uses (W2.1
  step 6).

It passes only if every G2 item holds on every pilot file. Its timings
replace § 7's projection before phase A launches.

### W2.3 Phase A (GS frames)

The driver runs over the phase A files in § 3.2's order, with the worker
count from § 7 (re-measured by the pilot), and writes into the zbook
`tile-join-wave-2` worktree. It commits per top-level directory and pushes
after each commit.

### W2.4 Phase B (55-map; after the seam ruling)

The same as W2.3, once P7 holds. It also covers the 24 `rescore-native`
files, through the native engine and their adapters (§ 5.2). If the ruling changes a reference or the
frame, the separate reference-corrected computation of § 4.3 runs after
the join-only one, under its own identity and gate items.

### W2.5 Reports

`reports/tile-join-wave-2/` (§ 10), all following the document revision
policy.

### 5.1 The 281 `unresolved-recipe` files

| Group | Files | Handling |
|---|---:|---|
| Null-exemplar sensitivity cells (`results/null-exemplar-sensitivity-2026-09-13/`) | 232 | **Regenerate, then re-score.** Run `analyse_null_exemplar_sensitivity.py --stage filter` in a disposable clone, because it also rewrites the committed `detections_manifest.json` (`:636`). Accept the regenerated inputs only if the regenerated manifest equals the committed one (every `n_features`, `n_dropped`, `n_kept`, and path), and if the legacy replay then reproduces each cell's committed confusion and intervals. A matching count is a tripwire, not proof (Wave 1 specification, W1.0). A mismatch is a replay-guard failure and stops the run (§ 6). None of these files is paper-cited |
| `results/verifier-t-pilot/` | 24 | `skip: no-recipe`. No references, bounds, or detection input recorded (`worklist.json` reasons). Left untouched and listed as not migrated (§ 8) |
| `results/retest/*-evaluation.json` | 12 | `skip: no-recipe`. No `_metadata` at all. They carry neither a tile block nor intervals. Left untouched and listed |
| `results/deployment-oracle-2026-06-06/preverifier-eval/` and `results/rescore-2026-05-31/` | 12 + 1 | § 5.3 |

### 5.2 The 60 files that `evaluate_detections.py` did not write, and the 24 native-adapter files (Astra round 3)

W1.0 counts 5 written by `compute_corrected_f1_multi_buffer.py` and 55
with no recorded writer (`dry-run.md` § 3.4). Of the 55, 36 are the
no-recipe files of § 5.1, which are skipped. The other 19, with the 5,
are the 24 native-adapter files of § 2 item 5. The disposition below was
verified at `f6f5ffe54` against Astra's evidence
(`~/agent-mail/codex/reviews/native-writer-audit-2026-11-18/native-writer-schema-audit.json`,
which reads git objects only).

**What these files are.** Each `evaluation.json` is a deterministic
transform of the corrected-F1 engine's native `summary.json` in the same
directory. The adapter at `register_gemini37_author.py:1128–1135` calls
itself "a pure deterministic transform of the engine's `summary.json`".
Astra's audit found three things for all 24:

- the point metrics and the F1 interval endpoints map exactly to the
  native summary;
- the adapted tile confusion maps to the native 50 m row;
- every adapted interval is percentile.

The engine is a different estimator from the scorer. In 16 of the native
summaries the reference count varies by buffer. For example,
`results/55maps-extended-gt-2026-06-07/IM-k3/summary.json` has 4,746
references at 5 m, 5,160 at 50 m, and 5,508 at 150 m. Its adapter records
`canonical-gt-55maps-r50.geojson` as the loadable reference but valid at
50 m only. Rows at other radii were scored against "the composite gated
at that radius" (`adapt_track2_evals_for_manifest.py:80–95`). The
extended-GT driver calls the engine with the student reference, the
bounds, and two review tables (`score_55maps_extended_gt_canonical.py:165–176`).
The standardised adapter takes a reference vintage, `standardised` or
`r2` (`register_standardised_gt_conditions.py:204–213`).

**Disposition.** Every one of the 24 is re-scored through **its native
engine and recipe, then its adapter**. The historical estimator (the
percentile interval) and the historical reference construction (the
per-buffer gating, the review tables, and the standardised vintage) are
preserved. **A matching key structure never selects the scorer.** The
first draft's rule that "the driver re-scores them if their key structure
matches" is withdrawn: the adapters produce that structure deliberately,
and `recover_recipe` would recover only the single `ground_truth` alias,
which does not reproduce the computation.

**The native recipe and identity.** The effective recipe, and the
identity's anchor (§ 5.6), capture what the engine actually used: the
detection layers; the student reference; the bounds; the review tables
(yesterday's and today's); the gating or standardised mode and the
reference vintage; the buffers; the bootstrap count; the seed; and
`compute_mcc`. They are read from the native summary's
`metadata.input_paths` and parameters, with the absolute-path prefix
resolved as P14 proposes, and each input is hashed. The seam-policy key
for these files (§ 4) is (frame, native reference construction), not the
`ground_truth` alias.

**The two computations, natively.**

1. **Legacy replay.** Run the engine under its recorded rules (the legacy
   joins, as the extended-GT driver passes them at `f6f5ffe54`). The
   native summary must reproduce the committed one. Then run the
   adapter on the committed native summary. It must reproduce the
   committed `evaluation.json` byte for byte, which pins the adapter's
   own serialisation. Either mismatch is a replay-guard failure (§ 6).
2. **New rules.** Run the engine under `sheet-contains` and
   `sheet-primary` (or the phase B seam policy), then run the **migration
   adapter**. This is a version of the adapter that also carries both join
   rules, the refusal state (the withheld form, if the engine refuses),
   the re-emission history, and the `metadata_version` migration. The
   existing adapters drop the new join provenance, so they cannot be used
   unchanged.

**Native output and adapted view are published together.** The native
`summary.json` stays the claimed current source of its `evaluation.json`.
The re-scored native outputs that carry join-dependent values
(`summary.json`, and any sibling such as `corrected-f1.csv` that holds
those values) and the adapted `evaluation.json` and its siblings form one
bundle under § 5.6. They are checked, published, and recovered together.
The native summary carries the same provenance as the adapted view: both
rules, the refusal state, and the history. A later run of a pure adapter
therefore regenerates the new values, not the old. The old summary is
never left in place as the source of a changed view. (The alternative, a
versioned replacement source that the view points to, is not taken. It
would leave two summaries in the directory, and a later adapter run could
read the wrong one.)

**Schema and guards.** Before phase B, each native writer's schema is
traced field by field, as W1.0 § 3 did for the scorer. The trace covers
the native `summary.json` and its siblings, and the adapted view. Its
output is a target and non-target schema with structural target paths for
both levels, committed in `reports/tile-join-wave-2/`. The join-only
invariant applies at both levels. Native point F1, true and false
positives and negatives per radius, reference counts per buffer, and
every other non-target field must be identical (G2 items 1–2). The
textual guard of G2 item 1 compares the committed and new
`evaluation.json`, both as serialised by the adapter, so the eight files
that do not round-trip (§ 2 item 3) are covered by the adapter-replay
check rather than by `json.dumps`. The A10 capability check stays in
force for these files (W2.1).

**Implementation notes from Astra's closing review** (`16354b73a`;
`~/agent-mail/codex/outbox/claude/20261118T141430Z-astra-wave2-spec-accepted.md`;
evidence `~/agent-mail/codex/reviews/native-writer-audit-2026-11-18/`
`native-input-git-anchors.json` and `native-dedup-default-anchors.json`).
These bind the native-schema trace; they do not change the design.

- **`dedup_tolerance_m` is recorded explicitly** in each native file's
  effective recipe. The engine accepts it
  (`scripts/compute_corrected_f1_multi_buffer.py:1296` at `f6f5ffe54`), the
  native summaries' metadata omit it, and every recorded source revision
  has a 5 m default; a default does not prove that no override was used, so
  the legacy replay and the native reference-count checks must establish
  the value actually selected.
- **Native refusal propagation is handled deliberately.** At `f6f5ffe54`,
  `compute_mcc_block` (`:683–705`) reads metric fields with `.get` from a
  library refusal and discards its reason and diagnostics, and
  `_result_to_dict` (from `:1025`) omits the tile block when both MCC and TP
  are absent. This predates the new joins. The migration adapter carries
  the refusal reason and diagnostics through, and a missing block is never
  read as "MCC not requested". A test drives a refusal from the engine
  through the adapter.
- **An older identity is verified against its own published bundle**, not
  a later superseding one, if older-entry verification is exposed.
- Astra checked the native inputs against Git trees: of 112 per-file input
  references, 100 have the same blob at the recorded source-code commit and
  at the reviewed head, and 12 were untracked at the source commit but are
  tracked now. This corroborates, but does not prove, clean original inputs.

### 5.3 The 13 files whose detection input is absent on zbook

Twelve are under `results/deployment-oracle-2026-06-06/preverifier-eval/`
(55-map) and one under `results/rescore-2026-05-31/` (GS). None is
paper-cited. W2.0 searches for each missing input: git history
(`git log --all -- <path>`), amd-tower's checkout, and the generating run's
output directory. An input that is found, and whose hash matches any
recorded hash, is used, and the file proceeds; its replay is the identity
check. The files still missing are committed as the pre-enumerated list of
P9, and each is ledgered `skip`, `held:input-absent`, left untouched, and
listed as not migrated (§ 8). A missing input that is not on the list is a
§ 6 stop. Sapphire is unreachable and is not searched (Wave 1
specification, changelog of 2026-11-18).

### 5.4 Statuses

Every file ends with exactly one file-level status and one reason. Each
leg's outcome is recorded separately (§ 5.5).

| Status | Reasons |
|---|---|
| **success** | `rescored-in-place`; `counterpart-written`; `withheld-now-scored` (a `known-withheld` file whose replay ended in its recorded refusal and which scores under the new rules); `rescored-superseding` (an intentional re-emission under a new identity, § 5.6) |
| **expected refusal** | `new-rule-refusal:<reason>`: the new-rule leg ends in a refusal the library names (`tile_join_unattributed_detection`, `no_tiles_in_bounds`, `detections_have_no_source_tile`, or the shortfall reasons), with its diagnostics. The file is re-emitted in the scorer's withheld form, a target-set shape (`dry-run.md` § 3.2). For a `known-withheld` file the reason is `still-withheld:<reason>` |
| **skip** | `not-tile-bearing`; `no-recipe`; `already-done` (§ 5.6: rebuilt identity equal, manifest `committed`, one terminal record, and every bundle member's hash equal to that record's `bundle_after`); `held:seam-ruling`; `held:input-absent` (pre-enumerated files only, P9); `held:foreign-schema` (a native writer whose schema trace is not complete, § 5.2); `held:sibling-review` (an unseen wording change, W2.1 step 6) |
| **failure** | `replay-mismatch:<fields>`; `interval-mismatch:<fields>`; `input-hash-mismatch`; `regeneration-mismatch`; `recipe-error:<message>`; `guard:<item>` (including `guard:sibling-content` and `guard:textual`); `unnamed-refusal`; `unexpected-content` (a bundle member's hash matches neither its before nor its staged hash); `identity-changed` (§ 5.6); `rolled-back` (a staged copy failed verification and the bundle was restored, § 5.6); `exception:<type>` |

A failed file is never published, and a `skip` changes nothing. Under the
current stop rule, almost every failure also stops the run (§ 6).

### 5.5 Ledger schema

The ledger is append-only JSON Lines (JSONL), at
`~/scratch/wave2/<run-id>/ledger.jsonl`. It holds one terminal record per
file per publication, plus `verification` records (§ 5.6), and only the
driver's main process writes it. It is copied to
`reports/tile-join-wave-2/ledger.jsonl` at each commit. Fields:

- **identity**: `ledger_version`, `record_kind` (`terminal` or
  `verification`), `run_id`, `host`, the file's `computation_identity`
  (its hash, its anchor, and its execution context, § 5.6), and the
  `publication_identity` (the computation identity plus the
  `bundle_after` hashes);
- **worklist facts**: `path`, `worklist_status`, `disposition`,
  `paper_cited`, `corpus`, `frame`, `reference`, `construction_route`,
  `passes`, `buffers`, `metadata_version`;
- **inputs, labelled by leg**: `replay_inputs[]` and `compute_inputs[]`,
  each with `role` (detections, reference, frame, mask), `path`,
  `sha256`, `git_blob`, `recorded_git_blob`, and `matches`;
- **bundle**: `bundle_before[]` and `bundle_after[]`, one entry per member
  (JSON, `.md`, `.csv`) with `path` and `sha256`, and the staged-manifest
  path;
- **legs**: `replay` (outcome `reproduced`, `reproduced-recorded-refusal`,
  `mismatch`, or `error`; `recorded_rules`; `differences[]`); `compute`
  (outcome `scored` or `refused`; `reason`; `diagnostics`); `guards` (each
  G2 item `pass`, `fail`, or `n/a`, with details); `siblings` (content
  check and any layout drift);
- **changes**: `targets_changed` (count by structural path), with the full
  per-field before and after in `diffs/<sha256 of path>.json`; `delta`
  (tile confusion and MCC before and after; flips of `coverage_status`,
  `ci_unreliable`, `ci_excludes_point`, and `sparse_coverage`; intervals
  before and after, per buffer); `cross_sheet_tiles[]` (G2 item 4);
- **result**: `status` and `reason`;
- **cost**: `started_utc`, `finished_utc`, `wall_s`, `cpu_s` and
  `max_rss_mb` per leg, and `worker`.

`ledger-summary.json` reconciles the ledger to the worklist: one terminal
record per worklist path, and counts by status and reason that sum to
2,829.

### 5.6 Computation identity, bundle publication, recovery, and idempotence (Astra W2-2, R2-1, R2-2)

**Computation identity.** Each file's identity is the SHA-256 of a
canonical JSON object with two parts.

The **anchor** is frozen when the file is first processed and recorded in
its first re-emission history entry. It holds:

- the pre-migration bundle: the SHA-256 of every member (JSON, `.md`,
  `.csv`) as committed before re-emission;
- the worklist: its commit and SHA-256;
- the original recipe: buffers, passes and their order, seed, and
  iteration count, and the recorded rules the replay uses;
- the replay leg's input hashes (the original inputs) and the compute
  leg's input hashes;
- the schema adapter: its identifier, version, and target-paths SHA-256;
- the seam policy: key, value, and the hashes of any mask and reference
  it introduces.

The **execution context** is the code (driver, library, and scorer
commits, each from a clean tree) and the environment (Python version, and
the SHA-256 of the `uv pip freeze` output).

**The identity is never derived from a re-emitted file's current bytes**
(Astra R2-2). After publication the file has new hashes and new effective
join arguments. On restart, a published file's identity is rebuilt from
two things: the anchor in its verified manifest (or, after commit, in its
history entry), and the current run's execution context. The current
bundle bytes are compared separately with the ledger's `bundle_after`.
An ordinary restart, with the same code, environment, and policy,
therefore rebuilds the same identity and does not report
`identity-changed`. A file not yet published has no history, and its
anchor is computed from its committed bytes.

**What is frozen, and what is checked afresh** (Astra round 3). The
anchor freezes the *original artefact*: the pre-migration bundle hashes
and the original recipe that the historical result was computed from. It
does not freeze the evidence used to detect a new request or drift. On
every resume, before a file can be reported `already-done`, the driver
**recomputes**:

- the hashes of every input the file's recipe references, read from disk
  now;
- the recipe, seam policy (with its mask and reference hashes), schema
  adapter, and worklist that the current run requests for that file.

It then compares each with the anchor's recorded value. A changed input
file, a changed requested policy or recipe, a different adapter, or a
different worklist entry is drift. Rebuilding the identity from the
stored anchor alone would hide it.

Resume compares the whole identity, not selected fields. If the anchor,
the freshly computed request and input hashes, or the execution context
differs, the file is not treated as done. The driver stops with
`identity-changed`, unless the operator has started an explicit new
computation (`--supersede <reason>`), which is recorded as below.

**Durable, atomic manifest writes** (Astra R2-1). Each file has a manifest
at `<run-dir>/staging/<sha256 of path>/manifest.json`. Every write of it,
whether creation or a state transition, goes the same way:

1. Write the full new manifest to a temporary file in the same directory.
2. `fsync` the temporary file.
3. `os.replace` it onto `manifest.json`.
4. `fsync` the directory.

A kill during any of these steps leaves the previous manifest whole. A
torn manifest therefore never erases the only record that recovery needs.
Stray temporary files are moved to `<run-dir>/abandoned/` at the next
start.

**Immutable recovery copies.** Staging holds two copies of every member:
the original (from the committed bundle) and the staged new version. Both
are written, `fsync`ed, and made read-only. Their hashes are recorded in
the manifest and verified before every use. Both are kept until the
bundle is `committed`, and after that in scratch until M2. **A staged copy
is never consumed by `os.replace`.** Publication copies it to a temporary
file in the target member's own directory, on the target file system,
`fsync`s that file, replaces the target with it, and `fsync`s the target
directory. Restoration uses the original copy in the same way.

**States and steps of publication:**

1. **`staged`**: write and `fsync` both copies of every member and the
   staging directory, then write the manifest.
2. **`publishing`**: replace the target members, siblings first and
   `evaluation.json` last, each as above.
3. **`published`**: the main process appends the ledger record and
   `fsync`s the ledger.
4. **`committed`**.

Rollback has two states of its own, **`rolling-back`** and
**`rolled-back`**, and each is a recoverable transition.

**One ledger writer.** Workers never write the ledger. They return each
result to the driver's main process, which alone appends records and makes
the `published` → `committed` transition. The main process holds an
exclusive `flock` on `<run-dir>/ledger.lock` for the whole run, so a second
driver on the same run directory refuses to start. Parallel workers
therefore cannot interleave JSON Lines records.

**Recovery**, at every start and before any new work. For each manifest
not in state `committed`:

- **No manifest, or only a stray temporary file**: nothing was published.
  Every target must hash to its committed original, and the file is
  reprocessed.
- **`staged`**: every target must still hash to its original. The staging
  directory is moved to `<run-dir>/abandoned/`, and the file is
  reprocessed.
- **`publishing`**: every member must hash either to its original or to
  its staged version.
  - If every staged copy verifies, the driver completes the publication
    and moves to `published`.
  - If a staged copy fails verification, the driver first verifies every
    original copy. If they all verify, it writes `rolling-back`, restores
    every member from its original, and writes `rolled-back`.
  - If an original copy also fails, nothing is written, and the run stops
    with `unexpected-content`.
- **`rolling-back`**: every member must hash to its original or its staged
  version. The driver finishes restoring from the verified originals,
  then writes `rolled-back`.
- **`rolled-back`**: the main process appends a `failure`, `rolled-back`
  record (unless an identical one is already durable), and the run stops
  (§ 6).
- **`published`**: verify every member against its staged hash. The
  ledger is then searched for a terminal record with the same
  **publication identity**: the computation identity plus the
  `bundle_after` hashes. If one exists, the driver writes `committed` and
  appends nothing. If none exists, it appends the record and then writes
  `committed`. Either way, there is exactly one terminal record.
- **Any member matching neither its original nor its staged hash**:
  `unexpected-content`, and the run stops.

**`already-done`** requires five things:

- the rebuilt identity is equal;
- the fresh input hashes and current request match the anchor (above);
- the manifest is `committed`;
- there is exactly one terminal record for the publication identity, and
  it is a published outcome: a **success** or an **expected refusal**
  (Astra round 3), since an expected refusal is published in the scorer's
  withheld form (§ 5.4);
- every bundle member's current hash equals that record's `bundle_after`.

So a published expected refusal is neither recomputed nor appended again
on restart. Checking `evaluation.json` alone is not enough.

**A truncated JSON Lines tail.** On start, the main process reads the
ledger line by line. A final line without its terminating newline, or one
that does not parse, is copied to `ledger.jsonl.torn-<UTC timestamp>`, and
the ledger is cut back to its last complete line. The bundle it described
is then recovered through its manifest, as above. A malformed line
anywhere but the end is corruption and stops the run.

**Durability claimed.** The design claims consistency after the process
is killed at any point, and the tests below show it. It also claims
durability after power loss to the extent that the `fsync` calls on files
and parent directories above provide it, on zbook's file system. Power
loss itself is not tested.

**Interruption tests** (tier 1, by a fault-injection hook that ends the
process at a named point). Each test asserts that recovery reaches the
same final bytes for every bundle member, exactly one terminal ledger
record per file, and intact recovery copies:

- **during a manifest write**, for every transition: after a partial
  temporary file, and after the temporary file's `fsync` but before its
  replace;
- **after staging**, before publishing;
- **during publication**: during the copy to a target temporary file, and
  after each sibling replace;
- after the JSON replace;
- **during the ledger append**, leaving a partial line;
- **after the durable ledger record**, before `committed`; recovery must
  append no second terminal record;
- **during rollback**, after the first restored member, with a staged copy
  deliberately corrupted to force the rollback;
- after `committed`.

A concurrency test runs several workers against one ledger and checks
that every line parses and that the record count equals the file count.

**The migration lifecycle test** (Astra R2-2) runs, in order:

1. a successful in-place migration;
2. a complete process exit;
3. an ordinary restart, which gives `already-done`, no `identity-changed`,
   and no new terminal record;
4. a forced recomputation.

After every step, the first history entry must be byte-identical to the
one written at step 1. Three more lifecycle tests:

- the same sequence for a file whose new-rule leg ends in an **expected
  refusal**, where step 3 must give `already-done`;
- **drift**: after step 2, change one referenced input file, and
  separately the requested seam policy; the restart must stop with
  `identity-changed`, not report `already-done`;
- **supersession** (Astra round 3): migration, then `--supersede`, then
  an ordinary restart, then a forced verification of the latest identity.
  The verification must take its original from the superseding entry's
  recorded anchor, not from the merge base. Every earlier history entry
  must stay byte-identical. The pilot repeats the sibling-replace,
partial-line, and lifecycle cases on real bundles.

**Idempotence: what a forced recomputation replays.** `--verify-idempotence`
ignores `already-done`. It replays the **anchor of the computation being
verified**, never the effective new artefact. By default that is the
latest history entry; an older one can be named. The entry must therefore
record exactly where its original came from: the git commit and blob
object of every pre-migration bundle member (`original_bundle[]`: path,
commit, blob, SHA-256). The first entry's originals are the committed
files the migration replaced. A superseding entry's originals are the
bundle it superseded, at the commit that published it. No entry assumes
the branch's merge base.

1. It takes the original bundle members from the recorded commit and blob
   objects (`git cat-file`) and verifies them against the entry's
   SHA-256s.
2. It takes the original recipe and inputs from the same entry (the
   replaced `cli_args`, `input_files`, and recorded rules, or for the
   native writers the native recipe of § 5.2), and verifies each input
   against the entry's hashes.
3. It runs both legs again under the anchor's rules and policy, into
   scratch, and compares the resulting bundle byte for byte with the
   committed one.

It writes no bundle, manifest, or history, and its ledger record has kind
`verification`, which never counts as a terminal record. Because the
history entry is part of the output, an unchanged rerun reuses it
verbatim: its first-publication date, its replaced `cli_args` and other
inputs, and its original-file hash. Fresh provenance would otherwise break
byte identity on its own.

**An intentional, different re-emission** (a new identity, such as a later
ruling or a corrected input) needs `--supersede <reason>`. Its anchor is
the current committed bundle, recorded by commit and blob in its own
history entry. It appends a new history entry carrying
`supersedes` and the reason, never rewrites an earlier entry, and is
ledgered `rescored-superseding`.

**The idempotence sample** during the corpus run (§ 13, A7): 5 % of each
stratum, rounded up, so every populated stratum has at least one file.
The strata are those of W2.2. The sample is drawn with a seed fixed and
recorded before launch. Together with the pilot's full double run it is a
regression check, not proof for every file. A full second pass is the PI's
choice and is costed (open question P8).

### 5.7 Launch discipline

The project's rules apply (`docs/agent-guidance.md`, "Compute Location"):

- The driver is launched detached on zbook as
  `ssh zbook 'cd <worktree>; nohup <python> scripts/tile_join_wave2_rescore.py ... > <run-dir>/run.log 2>&1 < /dev/null & echo $! > <run-dir>/run.pid'`,
  with all three descriptors redirected, setup separated by `;`, and
  nothing after the launch on the same line.
- The driver also writes its own pid file, and a heartbeat line to its log
  at least every 60 s, so that log staleness works during long files.
- It ends with exactly one of `^WAVE2 COMPLETE`, `^WAVE2 PARTIAL`, or
  `^WAVE2 STOPPED`, followed by the summary counts. The watcher is
  `scripts/wait_for_run.py --pidfile ... --marker success='^WAVE2 COMPLETE'
  --marker partial='^WAVE2 (PARTIAL|STOPPED)'`, which keys on terminal
  state and log staleness. A chain proceeds only on exit 0.
- Liveness is `kill -0 $(cat run.pid)` plus log age, never `pgrep -f` over
  `ssh`. Failure filters are case-insensitive
  (`grep -iE 'error|traceback|failed|partial|stopped'`).
- Worker processes are separate operating-system processes (the scorer is
  single-threaded: CPU time ≈ wall time, `dry-run.md` § 8). The 55-map
  phase admits a new job only while the free-memory estimate allows it
  (§ 7).

## 6. Running unattended, and what stops it (Astra W2-4)

The parent record's M2 rule is "any interval or guard failure = stop"
(`planning/tile-join-resolution-2026-11-01.md:312`). D72 (3) says an
overnight run "should just continue" past its priority subset, but that
means not stopping at the end of the subset. It does not mean tolerating
failures. Until the PI amends the rule (open question P9), **the first
of these stops the run**, in any file, cited or not:

- an interval or replay-guard failure: a `replay-mismatch`, an
  `interval-mismatch`, or a `regeneration-mismatch`, or a legacy replay
  that does not end in a `known-withheld` file's recorded refusal;
- an **input-hash mismatch** that was not explained and recorded before
  launch. A changed input never becomes a file-local exception;
- a missing input that is not on the pre-enumerated list (P9);
- a non-target field changed, or a point F1, precision, or recall moved
  (G2 items 1–2), including `guard:textual` and `guard:sibling-content`;
- a count-table sum mismatch, overall or per sheet (G2 item 5), or a
  reference-positive count that disagrees with the W2.0 recount (item 6);
- a sheet-specific difference from a historical contains reading on a tile
  that no other sheet's evidence reaches (item 4);
- an idempotence-sample mismatch (item 7);
- a `rolled-back` bundle (§ 5.6);
- `identity-changed` without `--supersede`, `unexpected-content`, a
  malformed ledger line that is not the last, an `unnamed-refusal`, or a
  write outside the target worktree, the counterpart and
  reference-corrected trees, `reports/tile-join-wave-2/`, or the run
  directory;
- any 55-map file reaching the new-rule leg while its seam key is
  `pending`;
- a worker killed for memory, or swap in use on zbook;
- any decision this specification does not cover.

**After a stop**, the failure is diagnosed, and its disposition is written
into the stop record before the run resumes. Resumption goes through
§ 5.6's recovery, so no completed bundle is redone.

Not stops, but ledgered and reported at M2: a pre-enumerated
`held:input-absent`; any other `skip`; an expected refusal; a
`sibling-layout-drift`.

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
phase memory binds: (31 − 6) GB ÷ 2.046 GB per job = 12.2, so
**12 workers** (about 24.6 GB). The 6 GB margin covers the operating
system, the driver, and the new joins' unmeasured extra memory. In the GS
phase cores bind, not memory: 30 jobs would need about 8.7 GB. The Wave 1
operating brief caps heavy jobs at **14 workers**, which this draft uses.
Raising it to 30 would cut phase A's wall-clock from 2.93 h to 1.37 h
(open question P10). These worker counts are provisional. The pilot sizes
concurrency from peak memory measured at the intended load (W2.2).

**Wall-clock**, idealised: CPU-hours ÷ workers, assuming even packing and
no contention. The longest single file is 28.5 CPU-minutes, a 30-pass
file, well inside each phase.

| Phase | CPU-h | Workers | Idealised wall-clock |
|---|---:|---:|---:|
| A, paper-cited only | 12.40 | 14 | 0.89 h |
| A, all | 41.05 | 14 | **2.93 h** (1.37 h at 30) |
| B, all | 22.79 | 12 | **1.90 h** |
| A + B | 63.84 | | **4.83 h** |
| A + B with a full idempotence pass instead of a sample | 61.59 + 34.69 = 96.28 | 14 / 12 | 4.40 + 2.89 = 7.29 h |

**Not costed, because unmeasured:**

- the null-exemplar regeneration (its filter stage reads and writes
  GeoJSON);
- the 24 `rescore-native` files through the corrected-F1 engine. They are
  included in the 55-map total at the scorer's rate as a placeholder only
  (1.77 CPU-h: 0.59, 0.59, 0.37, and 0.22 by adapter;
  `wave2_scope_and_cost.txt` § 3). The engine has not been timed;
- any reference-corrected computation under § 4.3;
- the bundle `fsync` calls;
- contention at 12–14 concurrent jobs (the timings were taken at 8).

The estimate leans high on three counts: the GS rate is the costliest
smoke cell's, short-buffer 55-map files are charged 14 buffers, and the
256 px frame is charged at the 55-map rate. It leans low on one count: the
new-rule leg may cost more than a replay. On this projection, compute
takes hours, not days. The schedule to 2026-11-29 is set by the rulings
and reviews, not by compute.

## 8. Downstream dispositions (Astra's C1–C4, as they bear on Wave 2)

Wave 2 changes evaluation files only. It regenerates no tiering, Hsu set,
board, ladder table, leaderboard, manifest, or register rendering: those
are Wave 3's (parent record § 5). Astra's audit
(`~/agent-mail/codex/outbox/claude/20261118T122600Z-astra-tile-join-consumer-audit.md`)
bears on Wave 2 as follows.

| Finding | What Wave 2 does | Wave 3 |
|---|---|---|
| **C1**: the public resampling helpers (`bootstrap_ci`, the effect-size, multi-run, and interaction bootstraps, and `generate_report`) reached the count table without a join option at the audited base | Wave 2 uses only the scorer's path (`bootstrap_ci`, and classification with its bootstrap), with both joins explicit. W1.1 threads all five helpers (`bf7186b71`) | The effect-size and interaction consumers Astra names (`analyse_phase2_results.py`, `analyse_study_effects.py`, `analyse_secondary_effects{,_text}.py`, `compute-pairwise-effect-sizes.py`, `evaluate_pv_results.py`, `evaluate_retest_all.py`) re-run in Wave 3 only where a cited artefact depends on them. They first pass the integration check Astra asks for: one single-run, one multi-run, and one interaction route under each rule |
| **C2**: the E81 driver could acquire the new semantics through a changed default | Not used to write (W2.1); only its pure `recover_recipe` is imported | E81 stays a historical tool, pinned to each record's own join on the Wave 1 branch |
| **C3**: `compute_corrected_f1_multi_buffer.py` and `score_detection_set` lose join provenance | The five stride55 files are re-scored through that engine, with both rules recorded in its native schema (§ 5.2) | `score_detection_set` sweep consumers: disposition per call in the consumer-disposition record (P5); re-run only where cited |
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
name it. That list comes from a text search of tracked files, so it is
indicative, as W1.0's searches were.

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
   consumer-disposition record must say, for each generator, whether it
   refuses that mix or labels its output as legacy. A generator that does
   neither is a P5 finding.
3. **No merge before M3** (§ 3.3, proposed). `main` never holds re-scored
   evaluations beside downstream artefacts built from the old ones.
4. **A not-migrated register.** `reports/tile-join-wave-2/not-migrated.json`
   lists every in-scope file that Wave 2 left on its legacy rules (skipped,
   held, or failed), with the reason. Wave 3 and Wave 4 check every cited
   path against it, and any hit blocks the "all settled" verdict (G4).
   Unmigrated files are not edited to carry a marker: they are not
   re-scored, so they are not touched.

## 9. Gate G2 (all must hold before M2)

From the parent record's § 5 Wave 2 row and Wave 1's G1.

1. **Non-target content identical** (Astra W2-5). In every re-scored or
   counterpart bundle:
   - every JSON field outside the structural target paths of
     `target-paths.json` is value-identical to the committed file after
     parsing;
   - **textual guard**: for the 2,821 files that round-trip (§ 2 item 3),
     every line that differs between the committed and the new text lies
     inside the text span of a target path, with one exception. The
     permitted delimiter change is a comma added to or removed from the
     last line of the preceding sibling member in the same object or
     array, when a key is inserted or removed after it. No other change is
     permitted, and unrestricted reformatting fails the guard. The trailing
     newline is unchanged, and `version` and `timestamp` are unchanged;
   - for the 8 that do not round-trip, the adapter's token-preserving edit
     changes only target spans (§ 5.2);
   - the siblings pass the scientific-content check of W2.1 step 6.
2. **Point F1, precision, and recall identical** in every buffer and every
   pass of every join-only re-emission. This is part of item 1, and is
   stated on its own because it is the registered primary outcome. A
   reference-corrected computation (§ 4.3) is gated by its own amended
   items, never by this one.
3. **Legacy replay first**, under each file's recorded rules, reproducing
   its committed confusion and intervals, or its recorded refusal, before
   any new value is published.
4. **Differences from the historical contains readings confined to
   cross-sheet tiles.** For every cell with a committed frame-wide contains
   reading (the board's 150 gates in
   `results/tile-join-audit/era2-board-mcc-tiering-2026-10-30/mcc-family-geometric-contains.json`,
   and the K-ladder's in `results/k-ladder-2026-09-12/mcc-join-2026-10-30/`),
   `sheet-contains` differs only on tiles that another sheet's evidence
   reaches. Every such tile is listed with its explanation. On the 55-map
   frame the expected differences depend on the seam policy, and the
   comparison is made under it.
5. **Count tables sum** to the symbol-level totals, overall and per sheet,
   for every buffer and every pass.
6. **Reference-positive tiles** equal W2.0's independent recount for the
   file's (frame, reference) pair.
7. **Idempotent**: the migration lifecycle test (§ 5.6), the
   forced-recomputation sample, and the pilot's
   full double run give byte-identical bundles, and every interruption
   test recovers to the same bytes. A resumed run reproduces the ledger.
8. **A reconciled ledger**: exactly one terminal record per worklist entry
   (2,829). Counts by status and reason sum to the worklist. Every file
   changed on `tile-join-wave-2` is a published member of a committed
   bundle, or a rebuilt roll-up (`git diff --name-only` against the merge
   base). Every paper-cited file in the phases M2 covers is a success or an
   expected refusal; a paper-cited skip or failure there blocks G2.
9. **Batch roll-ups** rebuilt, and equal to a rebuild from their cells.
10. **Tests and lint**: tier 1 green on zbook at the post-merge reference
    count, plus the driver's tests (interruption tests included); `ruff
    check` and `npx markdownlint-cli2` clean on touched files.
11. **Audit**: a fresh-context `/audit` of the driver, with every finding
    resolved or given a written disposition (as G1 item 9), and Astra's
    review of this specification and of the seam-policy specification
    (P7).

## 10. Outputs

- The driver and its tests on branch `tile-join-wave-2`, with the
  re-scored bundles and roll-ups on the same branch. Counterparts go under
  `results/tile-join-wave-2/counterparts/`, and any reference-corrected
  evaluations under `results/tile-join-wave-2/reference-corrected/` (both
  proposed).
- `reports/tile-join-wave-2/`, following the document revision policy:
  - `target-paths.json` (W2.1 step 4), `missing-inputs.json` (P9), and
    `seam-policy.json` with the policy specification it encodes (§ 4);
  - `pilot.md` and `pilot-ledger.jsonl` (W2.2), with the re-measured cost
    and the sibling wording allowlist with its approvals;
  - `ledger.jsonl`, `ledger-summary.json`, and `diffs/`;
  - `ledger-summary.md`, containing:
    - counts by status and reason;
    - the distribution of tile-MCC changes (ΔMCC) by frame, corpus,
      construction route, replication, and paper citation;
    - every interval, coverage-status, `ci_unreliable`,
      `ci_excludes_point`, and `sparse_coverage` flip;
    - every expected refusal;
    - the cross-sheet tile list of G2 item 4;
  - `not-migrated.json` and `downstream-inputs.json` (§ 8);
  - `native-writer-schemas.md`: the native and adapted schemas of the four adapters (§ 5.2);
  - `e93-before-after.json`: the paper-cited before and after values that
    erratum E93's table needs (parent record § 4 item 4), with the join-only
    and any reference-correction effects kept separate (§ 4.3). The
    erratum text itself remains Wave 4's, with the PI's approval.

## 11. Milestone M2: what the PI receives, and decides

M2 may be taken once, after both phases, or in two parts (M2-A after
phase A, M2-B after phase B), if the PI prefers to see the GS results while
the seam ruling is pending (open question P11).

The PI receives:

- the G2 checklist with the evidence for each item;
- `ledger-summary.md`: the ΔMCC distribution, every flip, every refusal,
  every skip and failure with its reason, and the not-migrated list;
- every stop record, with its diagnosis and disposition (§ 6);
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
- **P8.** Idempotence on a 5 % stratified sample with forced recomputation
  (proposed; Astra finds it a reasonable regression check, § 13), or a full
  second pass (+32.44 CPU-h, about +2.5 h idealised wall-clock, § 7)?
- **P9.** **An amendment to the stop rule, or not.** The parent record's
  M2 rule is "any interval or guard failure = stop" (§ 5 there). Under
  it, the first replay or interval failure in any file stops the run, as
  § 6 now specifies. The first draft proposed tolerating up to 10 replay
  mismatches on non-cited files before stopping. That is not an
  interpretation of the current rule. It would need your explicit
  amendment (Astra W2-4). Do you want such an amendment? If so, what
  threshold, and does an input-hash mismatch on a non-cited file count
  towards it? Without an amendment, Wave 2 stops on the first.
- **P10.** Raise phase A's worker count from the brief's 14 to 30? Memory
  allows it (§ 7). It would cut phase A's idealised wall-clock from
  2.93 h to 1.37 h.
- **P11.** M2 whole, or in two parts (§ 11)?
- **P12.** The 46 `known-withheld` files outside W1.4 (W1.0 open question
  5): Wave 2 re-scores all 49 in place either way, and scoring does not
  admit any of them to a family (§ 2 item 1). Is the D73 (4) eligibility
  rule applied to the 46 when Wave 3 rebuilds their families, or do they
  simply re-score? 29 of them are 55-map files under
  `results/uplift-supplement/` (`wave2_scope_and_cost.txt` § 1;
  `dry-run.md` § 4.3).
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
- **P15.** If the seam ruling changes a reference or the frame (§ 4.3),
  which evaluation does the paper cite for the 55-map results: the
  join-only re-emission with the recorded references, or the separate
  reference-corrected one? Both exist under this design, and E93 reports
  the two effects separately.

### 12.2 For Astra

None open. A1–A7 were closed in round 1 and A8–A10 in round 2 (§ 13).

## 13. Review dispositions

### 13.1 Round 1

Astra's review of the first draft (`f5f3824bb`):
`~/agent-mail/codex/outbox/claude/20261118T133843Z-astra-wave2-spec-review.md`.
Its verdict was "revise before launch approval". Each finding that cites
code was checked against `tile-join-wave-1` at `f6f5ffe54` before it was
adopted.

| Finding | Verified | Disposition |
|---|---|---|
| **W2-1**: the shared hook is not a seam policy | Yes: `sheet_join_candidate_tiles` (`lib_advanced_metrics.py:3202`) has no purpose or side argument, and is called for both sides in classification (`:3429`) and in count tables (`:3843`, `:3846`); `iter_sheet_scopes` (`:2723`) scopes populations first | Adopted. The "change here alone" claim is removed (§ 2 item 7, § 4.2; the docstring at `:3216–3220` is to be fixed on the code branch). § 4.2 requires the five components to be specified separately, forbids a classification-only policy from reaching count tables, and requires stated coverage, matching-scope, and conservation consequences for count-table exclusions |
| **W2-2**: resume, bundle, and idempotence | Yes: the first draft's resume compared `rule_set_id` and one file hash only | Adopted. § 5.6: the full computation identity; a durable staged manifest with `staged`, `publishing`, `published`, and `committed` states and whole-bundle recovery; truncated-tail handling; a durability claim matched by `fsync`; interruption tests at every step; forced-recomputation idempotence; provenance reused verbatim on an unchanged rerun; `--supersede` for an intentional new re-emission |
| **W2-3**: a reference or frame change needs a schema amendment | Yes | Adopted. § 4.3: the affected targets, the recorded inputs, the separate join-only and correction baselines, an effective recipe in `cli_args` and `input_files`, and inputs labelled by leg. § 4.1 now uses the accepted E93 distinctions: measured projections, confirmed examples, and candidates awaiting adjudication |
| **W2-4**: the replay threshold changes the stop rule | Yes: `planning/tile-join-resolution-2026-11-01.md:312`, "any interval or guard failure = stop" | Adopted. § 6 stops on the first interval or replay-guard failure, and on an unexplained input-hash mismatch. Only the pre-enumerated missing inputs may be held (P9 precondition). The tolerance is now a request for a PI amendment (open question P9) |
| **W2-5**: a precise surgical-write guard | Yes: inserting a key adds a comma to the previous line | Adopted. Structural target paths in `target-paths.json`; the representation rule; the textual guard with its one permitted delimiter change; a token-preserving adapter for the 8 non-round-tripping files; the siblings' scientific-content guard (`guard:sibling-content`), with layout and wording drift only ledgered; JSON and siblings as one bundle (W2.1 steps 4 and 6; G2 item 1) |
| **A1** additional scope | Astra recounted 149, 21, and 5 | Closed: in scope. Scoring a withheld file does not admit it to a family (§ 2 item 1, P12) |
| **A2** regenerated Markdown | — | Closed: acceptable with the scientific-content guard and the bundle checks (W2-5) |
| **A3** seam hook | — | Closed: not sufficient; see W2-1 |
| **A4** `metadata_version` | Writer and reader at `f6f5ffe54` (`evaluate_detections.py:820`; `lib_advanced_metrics.py:513–514`; `rerun_bca_corpus.py:106–110`) | Closed: a documented migration to 1.5, added to the target schema, with the prior version kept in the history and no claim that other fields were upgraded (W2.1). The `rerun_bca_corpus.py` consequence was A10, closed in § 13.2 |
| **A5** absent legacy keys | — | Closed: they stay absent; only the specified provenance, effective-recipe, and migration fields are added (W2.1 step 4) |
| **A6** stop list | — | Closed: see W2-4 |
| **A7** idempotence sample | — | Closed as Astra states: a reasonable regression check, not proof for every file, conditional on forced recomputation, the identity and bundle checks, and the interruption tests. Rounding is up, with at least one file per populated stratum (§ 5.6) |
| Seam counting correction (Astra, `20261118T130529Z`; W1.0 `21cd6ef97`) | Read in `dry-run.md` § 2.2 at `568a80689` | Adopted: on r2, 26 references (40 with the ambiguous contacts); option (c)'s 333 tiles split into 11 map content, 6 ambiguous, and 316 padding (§ 4.4) |

### 13.2 Round 2

Astra's review of the revision (`1883c9611`):
`~/agent-mail/codex/outbox/claude/20261118T135814Z-astra-wave2-round2-review.md`.
W2-1, W2-3, and W2-4 were found addressed at specification level, and W2-2
and W2-5 substantially improved, with the details below still needed. It
is a technical review, not approval to launch.

| Finding | Verified | Disposition |
|---|---|---|
| **R2-1 (A9)**: recovery complete at every transition | Yes, against § 5.6 as revised. The manifest was rewritten in place; `os.replace` of the staged copy would consume the only recovery copy; there was no rule for `published` with a durable record, and no rollback state; workers could write the ledger | Adopted (§ 5.6). Every manifest write goes to a temporary file, `fsync`, replace, directory `fsync`. Original and staged copies are immutable, hash-verified, and kept until commit, and publication copies through a temporary file on the target file system. `published` with a durable record finds it by publication identity and appends nothing. Rollback verifies the originals first and has its own `rolling-back` and `rolled-back` states. One main process owns the ledger, under a `flock`. New interruption points cover the manifest write, the target copy, and rollback; a concurrency test covers the ledger |
| **R2-2**: freeze the identity anchor | Yes: an identity hashed from current bundle bytes would change after publication, so every ordinary restart would report `identity-changed` | Adopted (§ 5.6). The identity is an anchor (pre-migration bundle, original recipe and inputs, adapter, policy), frozen in the first history entry, plus the execution context. On restart it is rebuilt from the manifest or history, never from current bytes. Current bytes are compared separately with `bundle_after`. `--verify-idempotence` replays the anchor (the original bundle from git at the merge base, and the history's original recipe and inputs), writes nothing, and records `verification`. A migration lifecycle test checks that the history entry stays verbatim through a restart and a forced recomputation |
| **R2-3 (A8)**: bind sibling values to their cells | Yes: a multiset of numbers survives two values trading places | Adopted (W2.1 step 6). Markdown and CSV are compared as canonical non-target cells keyed by (section or table, row, buffer, column, metric, unit). Wording outside the cells must match the pilot's approved allowlist. An unseen change holds the file (`held:sibling-review`) for review before publication. The JSON textual guard (G2 item 1) was accepted as specified |
| **R2-4 (A10)**: schema capability is not bootstrap completion | Yes: `rerun_bca_corpus.py:106–110` at `f6f5ffe54` defines done as "already carry a BCa-requested bootstrap" | Adopted (W2.1, provenance). A 1.5 file is classified by its recorded prior vintage, plus a check of its bootstrap fields. A legacy file upgraded only for joins gets its own census category. Four tests are specified. In live files this concerns two 1.0 files today |

### 13.3 Round 3

Astra's review of the round-2 revision (`6d2729b96`), with an independent
trace of the alternative writers:
`~/agent-mail/codex/outbox/claude/20261118T140800Z-astra-wave2-round3-native-writers.md`;
evidence `~/agent-mail/codex/reviews/native-writer-audit-2026-11-18/`. It
found that the round-2 requests were addressed in principle. Each item
below was checked against `6d2729b96` and, for the writers, against
`f6f5ffe54` and the evidence JSON.

| Finding | Verified | Disposition |
|---|---|---|
| **Fresh inputs and requests compared with the anchor** | Yes: § 5.6 rebuilt the identity from the stored anchor plus the execution context only, so a changed input file or requested policy would have passed | Adopted (§ 5.6). Before `already-done`, the driver hashes the referenced inputs afresh and compares the requested recipe, policy, adapter, and worklist with the anchor. Only the original artefact is frozen. A drift test is added |
| **A published expected refusal is done** | Yes: `already-done` required a terminal *success* record | Adopted (§ 5.6). Success or expected refusal, under the same identity and hash checks. A lifecycle test covers the refusal case |
| **Superseded computations have their own anchor source** | Yes: forced recomputation read the merge base and the first history entry, while `--supersede` anchors to the current bundle | Adopted (§ 5.6, W2.1). Each history entry records `original_bundle[]` (commit, blob, SHA-256). Verification replays the entry being verified (the latest by default), read by blob, and never assumes the merge base. A supersession lifecycle test is added |
| **The 24 alternative-writer files are native-adapter views** | Yes. Every file's `_metadata` names its adapter (`adapter` or `adapted_by`) and its source `summary.json`: 8 `adapt_track2_evals_for_manifest.py`, 8 `register_standardised_gt_conditions.py`, 3 `register_gemini37_author.py`, 5 `register_pass1_adapt.py`. The evidence JSON shows the point and F1-interval mappings and the 50 m confusion mapping equal for all 24, percentile intervals throughout, and reference counts varying by buffer in 16 (IM-k3: 4,746 at 5 m, 5,160 at 50 m, 5,508 at 150 m). The adapter source anchors were read at `f6f5ffe54` | Adopted (§ 2 item 5, § 3.1, § 5.2). A new disposition, `rescore-native` (24). Native engine and recipe replay, then the adapter, preserving the percentile estimator and the reference construction; a key match never selects the scorer. Native inputs, review tables, mode and vintage, seeds, and buffers are in the effective recipe and identity. The native outputs and the adapted view are one bundle, with the native summary staying the current source. Migration adapters carry both rules and the refusal state. The A10 capability check stays, and the percentile method is intentional. Scope: `rescore-in-place` 2,469, `rescore-native` 24 (totals unchanged). Cost: the 24 stay in the 55-map total at the scorer's rate as a 1.77 CPU-h placeholder; the engine is untimed (§ 7) |

**Closing review** (`16354b73a`;
`~/agent-mail/codex/outbox/claude/20261118T141430Z-astra-wave2-spec-accepted.md`):
the technical specification review is **closed** at this revision. That
accepts the design, not an implementation, G1 or G2 evidence, a scientific
ruling, or launch. Its three implementation notes are recorded in § 5.2.

## Changelog

### 2026-11-19 — Seam-evidence refresh (Astra's patch, adopted)

Prepared after reading the corrected seam and own-sheet records at
`b0ca4983409bd63526cc15a6e6dc46619c03b1ff`. §§ 4.1 and 4.4 use the
containing-pixel counts and distinguish recipient content, own-sheet
attribution, and unadjudicated symbol identity. §§ 4.2 and 4.3 explicitly
cover sheet-label and centre corrections as well as the original options.
The original addition/exclusion counterfactuals are retained as such; they
are not estimates for a reference correction. No corrected score is
computed, no option selected, and no launch gate or review verdict changed.
Drafted by Astra (GPT, OpenAI Codex) as a proposed patch; adopted by the
Claude main session after checking every count against `dry-run.md` at
`b0ca49834` (r2 34 / 27 / 28 / 11; (d) 55 (44 / 11); r50 29 of 35).

### 2026-11-19 — Astra's closing review recorded (S169, amd-tower)

Trigger: Astra closed the technical review at `16354b73a`. Its three
implementation notes (`dedup_tolerance_m`, native refusal propagation,
older-entry verification) and the input-anchor corroboration are recorded
in § 5.2; § 13.3 notes the closure. No design element changed.

### 2026-11-19 — Revised after Astra's round-3 review (S169, amd-tower)

Trigger: Astra's round-3 review and native-writer audit (§ 13.3), and the
main session's instructions on it. The planning script now reads each
file's recorded adapter, and its output is regenerated.

| Item | Before | After |
|---|---|---|
| `already-done` | rebuilt identity, `committed` manifest, one terminal success | also fresh input hashes and current request compared with the anchor; success **or** expected refusal |
| Forced verification | merge base and first history entry | the verified entry's `original_bundle[]` by commit and blob; latest entry by default |
| Lifecycle tests | migration, exit, restart, forced recomputation | adds expected refusal, drift, and supersession sequences |
| The 24 alternative-writer files | 5 engine-written plus 19 "unknown writers", re-scored by the scorer if the keys match | 24 native-adapter views, `rescore-native`: native engine and recipe, then a migration adapter; native outputs and view published as one bundle |
| § 3.1 | `rescore-in-place` 2,493 (761 paper-cited) | `rescore-in-place` 2,469 (737), `rescore-native` 24 (24) |
| § 7 | the 24 at the scorer rate, unremarked | the same 1.77 CPU-h, marked as a placeholder; the native engine untimed |

Unchanged: the totals (2,829 entries; 2,779 re-scored or counterparted),
phase membership, the seam parameter, the stop rule, and the cost totals.

### 2026-11-19 — Revised after Astra's round-2 review (S169, amd-tower)

Trigger: Astra's round-2 review (§ 13.2) and the main session's
instructions on it. Each finding was checked against this document at
`1883c9611` and, for A10, against `rerun_bca_corpus.py` at `f6f5ffe54`.

| Item | Before | After |
|---|---|---|
| Manifest writes | rewritten in place, with `fsync` | temporary file, `fsync`, atomic replace, directory `fsync`; kill tested during the write |
| Recovery copies | the staged copy consumed by `os.replace` | immutable original and staged copies, verified, kept until commit; publication through a target-side temporary file |
| `published` recovery | no ledger record only | also with a durable record: matched by publication identity, no second record |
| Rollback | inside `publishing` recovery | its own `rolling-back` and `rolled-back` states, originals verified first |
| Ledger writers | unspecified | one main process, under a `flock` |
| Identity | hashed from the bundle's current bytes | a frozen anchor plus the execution context, rebuilt from the manifest or history |
| Forced recomputation | from the effective recipe | replays the anchor; writes nothing |
| Markdown check | row labels plus a multiset of numbers | keyed canonical cells; a wording allowlist; `held:sibling-review` |
| `rerun_bca_corpus.py` | add `"1.5"` to the done vintages | classify by the recorded prior vintage, plus a bootstrap-field check, with a separate category |
| Open questions for Astra | A8–A10 | none open |

Unchanged: the scope, the order, the seam parameter, the stop rule, the
cost projection, and the downstream dispositions.

### 2026-11-19 — Revised after Astra's review (S169, amd-tower)

Trigger: Astra's review of the first draft (§ 13), the main session's
instructions on it, and W1.0's GS-frame sheet check and corrected seam
counts (`tile-join-wave-1-w10` at `568a80689`). Code findings were checked
against `tile-join-wave-1` at `f6f5ffe54`.

| Item | Before | After |
|---|---|---|
| P4 (GS sheet check) | owed | met: 12 frames, 243 contacts, 237 padding, 0 ambiguous, 0 map content, 6 unmeasurable (beyond the scan's edge) |
| Seam hook | "a change here alone" | not a policy; five components specified separately (§ 4.2) |
| Seam facts | (a) 32 references added on r2; (c)'s complement treated as padding | (a) 26 references (40 with ambiguous); (c) 11 map content, 6 ambiguous, 316 padding |
| § 4 framing | contacts treated as undigitised printed copies | measured projections, confirmed examples, and candidates awaiting adjudication |
| Reference or frame change | a G2 amendment only | a full schema amendment, separate join-only and correction effects, an effective recipe (§ 4.3) |
| Resume | `rule_set_id` plus one file hash | full computation identity; staged bundle manifest; recovery; interruption tests (§ 5.6) |
| Stop rule | 10 replay mismatches tolerated on non-cited files | stop on the first; tolerance only by PI amendment (P9) |
| Write guard | "text outside target lines byte-identical" | structural target paths; representation rule; one permitted delimiter change; sibling content guard |
| `metadata_version` | open (A4) | migrated to 1.5, documented, in the target schema |
| P5 record | not on any branch | on `tile-join-wave-1` at `f6f5ffe54` |
| Open questions | P1–P14, A1–A7 | P1–P15 (P9 reworded, P15 new), A8–A10; A1–A7 closed in § 13 |

Unchanged: the scope and its counts (§ 3.1), the order, the cost
projection and its basis (§ 7, now labelled idealised), the downstream
dispositions (§ 8), and the planning script and its output.

### 2026-11-19 — Original publication

First draft, written in S169 on amd-tower while Wave 1 is stopped on the
55-map seam ruling, from W1.0's census, worklist, replays, and timings
(`tile-join-wave-1-w10` at `89cab15ee`), Astra's consumer audit, and the
decision record and Wave 1 specification on `main` at `92064b134`. It
specified the corpus re-score with the seam handling as an open parameter
and no position among the options, and projected the cost from
legacy-replay timings only. The new counts come from
`tile-join-wave-2-spec-2026-11-19-scripts/wave2_scope_and_cost.py`. Not
approved. For Astra's review (commit `f5f3824bb`).
