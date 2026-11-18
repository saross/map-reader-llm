# Wave 1 stop: 55-map references across a sheet seam (first read as double printing)

> **Last revised**: 2026-11-19 (pixel-convention fix: §§ 1, 4, and 5 re-counted; § 5 retitled and revised, one 1/3-candidate in every file, the lineage to the import commit added; earlier the same day, own-sheet evidence added, seam counts corrected, and Wave 2 drafting moved). See
> [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, Opus lane, the S169 main
  session on amd-tower, 2026-11-18 at about 23:50 AEDT.
- **Stop condition**: specification § 5, "the 55-map GS check finding a
  cross-sheet contact on map content"
  (`planning/tile-join-wave-1-spec-2026-11-01.md`, W1.0 "The 55-map GS sheet
  check").
- **Evidence**: `dry-run.md` § 2 and § 2.1;
  `scripts/sheet_check_55map.py`; `scripts/out/sheet_check_55map.txt` and
  `scripts/out/sheet_check_55map_summary.json` (commits `c1a7a23fd`,
  `561ecd611`; re-measured with the corrected pixel convention on branch
  `tile-join-wave-1-seam2` at `768cb2a9b` and `7056bb857`, pre-fix
  outputs kept as `scripts/out/*-pre-pixel-fix.*`).
- **The PI was notified** by push notification at about 23:50 AEDT.

## 1. What was found

The check reads the 55-map frame
(`inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`, 8,541 tiles on
55 sheets) and the reference behind smoke cell 2,
`best-available-gt-55maps-r2.geojson` (5,018 points, sheet in `source_map`).
For every point–tile contact with another sheet's tile, it classifies the
point's pixels in that tile as padding, map content, or ambiguous.
**Revised 2026-11-19:** the shared pixel helper floored a centre-indexed
coordinate, half a pixel off (`dry-run.md` § 2, "Pixel convention";
found by Astra). The counts below are re-measured with the containing
pixel; the first version's are in brackets.

| Measure | Count |
|---|---:|
| Cross-sheet reference pairs within 50 / 100 / 200 / 500 m | 0 / 0 / 0 / 35 (closest 200.7 m) |
| Point–tile contacts with another sheet's tile | 814 (648 references) |
| On padding | 764 [764] |
| Ambiguous | 16 [18] |
| **On map content** | **34 (27 references)** [32 (26)] |

Of the 34 map-content contacts, 32 lie on nine seams involving the
reprojected `_4326` sheets: Granit/Chirpan, Granit/Tatarevo,
Chirpan/Sredets, Tatarevo/K-35-075-1, Skobelevo/Dimitrovgrad,
Skobelevo/K-35-075-2, Dimitrovgrad/Galabovo, Dimitrovgrad/K-35-076-1, and
Glavan/K-35-077-1. The other two are `student:04282`'s (sheet K-35-076-1,
in two K-35-076-2 tiles), which the pixel fix moved from ambiguous to map
content, with a window 48.8 % near-black against the rule's 50 % limit.
The other four tracked 55-map reference files show 34–37 map-content
contacts each (32–35 before the fix; `dry-run.md` § 2).

Three things are kept apart here (revised 2026-11-19 after Astra's
review):

- **Measured.** No other-sheet reference lies within 200 m of any of the
  27 references with a map-content contact, and none of the contacted
  sheet's references lies within 50 m (`dry-run.md` § 2.2). That is
  evidence that the contacted sheet carries no local annotation there,
  not proof of what is printed at each point: the pixel test detects map
  content, not mound symbols, and the seams are misregistered.
- **Visually confirmed.** In the inspected crops (§ 2, and `dry-run.md`
  § 2), the point lies on a printed burial-mound symbol on the
  neighbouring sheet.
- **Not adjudicated.** The remaining map-content contacts, and the 16
  ambiguous ones, are candidates. Whether each is a second printed copy
  of the same mound needs adjudication before any reference is changed.

What follows for scoring, where a contact is a second printed copy, also
has two separate parts:

- **Symbol level.** Under the existing D50 matcher, a correct detection
  of that copy, attributed to the sheet it was seen on, has no reference
  on that sheet and can be scored a false positive.
- **Tile level.** Under sheet-specific containment (D73 (2)), a tile
  changes only if it holds none of its own sheet's references; many
  contacted tiles are already positive from another mound. For the
  map-content contacts on r2 that is 11 tiles of the 28 contacted, not
  one per contact (`dry-run.md` § 2.2; 11 of 26 before the pixel fix).

On the GS (Era-2), by contrast, every cross-sheet contact was black
no-data padding (parent record § 2.6), and that is the case the
sheet-specific rule was ruled on. The 55-map check shows that the
padding-only rationale cannot be carried over to the 55-map corpus
unexamined.

## 2. Independent verification (main session)

I viewed two of the W1.0 agent's crops, copied from zbook
(`~/scratch/wave1/w10/sheet-check/crops/best-available-gt-55maps-r2/`):

- `student:01862` (sheet Granit) in `K-35-063-2_Chirpan_4326_x0_y672.png`:
  the point sits on a printed burial-mound symbol inside the Chirpan
  sheet's map face, with map content all around and the black margin well
  to the left.
- `student:02387` (sheet Tatarevo) in `K-35-075-1_x1344_y0.png`: the point
  sits on a printed burial-mound symbol labelled "2", on K-35-075-1's map
  content.

Both agree with the agent's pixel measurements. I did not view the other 30
contacts.

**Correction (2026-11-19).** These two checks looked only at the
*neighbouring* sheet. They established a printed symbol there, not a second
printed copy. Astra's paired panels
(`~/agent-mail/codex/reviews/seam-paired-views-2026-11-18/`, panels 008 and
020, which I viewed) show both recorded coordinates in black padding on
their **own** labelled sheets (Granit and Tatarevo). See § 5.

## 3. What is paused, and what continues

**Paused until the PI rules**: everything that would consume a seam ruling.
That is the W1.5 smoke run and every corrected score on the 55-map corpus.
Nothing is merged to `main`. (The Wave 2 specification and its cost
projection were first listed here; see the second bullet below.)

**Continuing, on branches only, because none of it depends on the ruling**:

- W1.1 and W1.2 code and tests. The sheet-specific joins stand for the GS
  under D73 (2) whatever the 55-map ruling, and every option below needs
  the same machinery.
- The remaining read-only W1.0 steps: field schema, census, worklist,
  pinning smoke cells 3–5 (GS frames), recipes, and legacy determinism
  replays under each artefact's recorded rules.
- A read-only measurement for the ruling, described in § 4.
- Astra's cross-model review of the sheet check.
- The Wave 2 specification and its cost projection, **drafted with the seam
  handling as an explicit open parameter** that the PI's ruling fills. The
  draft takes no position among options (a)–(d), and the projection uses
  legacy-replay timings only. Moved here from the paused list at about
  00:15 AEDT on 2026-11-19, so that Astra can review the draft overnight;
  the draft is text, and the ruling slots into it unchanged.

This reading of "stops the wave" is the main session's, made overnight. The
PI may stop everything instead; the continuing work is on branches and can
be discarded.

## 4. Decisions the PI is asked to make

1. **How sheet-specific scoring treats these seam contacts.** Read § 5
   first: it changes the question. The options first framed (for a mound
   printed on both sides of a seam but digitised once) were:
   - (a) Add the second copy as its own reference on the neighbouring
     sheet, in the style of the phantom references. The canonical r50
     file already carries 415 `phantom:*` references from a review, and in
     24 of its cross-sheet pairs within 50 m a student reference sits
     beside a phantom on the neighbouring sheet (W1.0 agent's lead, being
     measured; see below).
   - (b) A seam exception: on a seam's overlap, a detection matches a
     reference from either sheet.
   - (c) A frame-wide join for the 55-map corpus only.
   - (d) Exclude the contacted seam tiles from tile classification on
     both sheets, and report how many tiles that removes.

   The read-only measurement under way counts, for every map-content
   contact in each reference file, whether a reference on the contacted
   sheet already lies within 50 m. It also counts how many such tiles
   each option would change.

   **Measured (W1.0 agent, 2026-11-18; counts corrected 2026-11-19, and
   again after the pixel-convention fix; `dry-run.md` § 2.2).** On r2, no
   map-content or ambiguous contact has a reference on the contacted
   sheet within 50 m. The 34 map-content contacts are 27 distinct
   (reference, recipient sheet) pairs, since seven references each reach
   two overlapping tiles of the same sheet. On canonical r50, 29 of its
   35 map-content contacts already have a contacted-sheet reference
   within 50 m, every one a `phantom:*` reference (22 within 20 m), and
   all 24 of r50's student–phantom pairs within 50 m are map-content
   contacts: a useful lead that the r50 review already did (a) for all
   but five references, not confirmation of each feature's identity.
   Relative to sheet-specific containment on r2: (a) adds 27 references
   (40 with the ambiguous contacts) and turns 11 of the 28 contacted
   tiles positive (17 of 41); (b) turns the same 11 (17) positive; (d)
   removes 55 tiles (44 of them positive); (c) turns 333 tiles positive,
   of which 11 hold a map-content contact, 6 only ambiguous contacts, and
   316 only padding contacts (confirmed padding). On canonical r50, (a)
   adds 5 references and, like (b), moves no tile. (Before the pixel fix:
   32 contacts, 26 pairs, six references; r50 29 of 33, all but four;
   (a) 26 on r2 and 4 on r50; 11 of 26 tiles; (d) 52 (41).)

2. **Note A in `withheld-37.md`.** D51's searched-area difference is not
   treated as an exclusion in the as-evaluated K-ladder families. Confirm
   or overrule. Overruling makes rows 13–18 not eligible; no row becomes
   unresolved.
3. **The 16 ambiguous contacts** (points on the black edge of the map face;
   18 before the pixel fix): a rule, or a look at the crops.

## 5. Own-sheet evidence: reference attribution requires adjudication

Added 2026-11-19; **revised the same day** after Astra's review of the
own-sheet audit (`~/agent-mail/codex/outbox/claude/20261118T145509Z-astra-seam-pixel-convention-interim.md`,
`…T145706Z-astra-seam-own-sheet-review.md`). The first version rested on a
half-pixel error in the shared pixel helper and drew a categorical
conclusion from the ambiguous/map-content boundary; it said that no
contact had map content on both sheets and that double printing was ruled
out for every contact. Both claims are withdrawn.

The § 1 check measured each point only on the **other** sheet's tile.
Astra's review (`~/agent-mail/codex/outbox/claude/20261118T142910Z-astra-seam-attribution-evidence.md`,
`…T143422Z-astra-seam-padding-diagnostic.md`) and a follow-up measurement
(`dry-run.md` § 2.4; branch `tile-join-wave-1-seam2`, first at
`61c091dc2`, re-measured with the corrected pixel convention at
`7056bb857`) measured each point on its **own** labelled sheet as well.

- **One reference has map content on both sheets in every one of the five
  55-map reference files, so it is a 1/3-candidate.** It is one feature:
  r2 and best-available `student:04282`, r50 `student:04296` (sheet
  K-35-076-1, at the K-35-076-2 seam, recorded `as_digitised` and never
  moved). Both windows are just under the rule's 50 % near-black limit
  (own sheet 0.471, recipient 0.488), so the verdict is weak, and a
  content verdict is not evidence of a printed symbol on either sheet.
  Astra's paired panel 038 shows the edge case; neither Astra nor this
  agent has adjudicated symbol identity there.
- **Every other recipient map-content reference in r2 lies in padding on
  its own sheet, except `student:02194`** (ambiguous: black at the point,
  a few pixels from the map edge). That is 25 distinct references (31
  contacts), the 2-candidates. For them, a separately printed instance
  **at the recorded coordinate** on the own sheet is excluded. That does
  not exclude double printing: a displaced counterpart (case 3) would
  also be a separately printed instance.
- **Comparison with Astra's independent diagnostic on the full-sheet
  scans.** The two use different classifiers (Astra: 9 × 9 and 31 × 31
  windows, every band ≤ 8; this check: a 17 × 17 window with content
  spans, every channel ≤ 20), so exact categorical agreement is not
  claimed. Under the stated correspondence (Astra's 9 × 9 window all
  near-black exactly when this check's own verdict is padding or
  outside), **39 of 40** r2 final coordinates and **37 of 39** traced
  original coordinates correspond. The exceptions (`student:02194`, final
  and original; `student:01879`, original) are compatible pixel evidence
  under different window rules: black at the point, padding within a
  few pixels of the map edge, where a 9 × 9 window is all black and a
  17 × 17 one reaches content. Astra's 9 × 9 window is entirely
  near-black on the labelled sheet for all 26 of the pre-fix recipient
  map-content pairs, at the final coordinate and at the original; for the
  27th, `student:04282`, it is 0.444.
- **The attribution concern predates centre marking.** In r2, every
  reference in padding on its own sheet at its final coordinate is in
  padding (25) or ambiguous (1, `student:01879`) there at its original
  reviewed coordinate; in r50 the coordinates were never moved. Marking
  does change some classifications at the padding/ambiguous boundary
  (`student:01879`; before the pixel fix, `student:02390` too).
- **The concern traces back to the original import.** Astra's backtrace
  (`~/agent-mail/codex/reviews/seam-paired-views-2026-11-18/original-import-backtrace.json`),
  re-checked by this agent against `git show 301b51128:inputs/vectors/references/student-mounds-55maps.geojson`:
  24 of r2's 26 pre-fix recipient map-content references match a unique
  feature exactly, with the same sheet label, in
  `inputs/vectors/references/student-mounds-55maps.geojson` at its import
  commit `301b51128`. The other two, `student:02391` and `student:02392`,
  sit at the merged centroids of documented merges
  (`results/gt-duplicate-review/gt-duplicate-decisions.csv:44–45` at
  `f6f5ffe54`: import features 4195 with 4205, and 4196 with 4207), whose
  parents all carry the same label, K-35-063-4_Skobelevo_4326. The
  1/3-candidate `student:04282` is import feature 4027, labelled
  K-35-076-1 as now. The import notes
  (`docs/notes/reflections/session-log.md:3528–3531` at `f6f5ffe54`)
  record a spatial join of the student records "against 332 available
  rasters". That is a historical note, not recovered import code: the
  bounding geometry and tie-breaking of that join are not established.
  None of this shows which sheet is correct or the physical identity of
  any symbol, and a retained `source_map` is not evidence of a printed
  instance on that sheet.
- For the 2-candidates, two readings remain, and pixels at the point
  cannot separate them: **(2) the reference's sheet label is wrong** (the
  mound is printed once, on the neighbouring sheet), or **(3) a displaced
  counterpart**: the labelled sheet prints the same mound elsewhere, and
  the reference needs a sheet-specific centre. A compact dark blob lies
  within about 240 m on the own sheet for 12 of r2's 25, and none for 13
  (a hint for where to look, not an adjudication).
- **Centre marking.** Astra traced `student:01862` through the
  standardised reference, `marked-centres.csv`, and the materialisers.
  `scripts/mark_mound_centres.py` chooses the display raster with
  `_best_raster_for_point` but saves the queue's `map_name`, not the
  raster shown, so a reviewed coordinate does not prove that the symbol
  was reviewed on the retained sheet.
- **Canonical r50:** 21 of its 25 2-candidates already have a
  `phantom:*` within 50 m on the neighbouring sheet, so the student
  reference sits in padding beside a digitised copy (20 of 24 before the
  pixel fix; the same four have none).
- **A possible pre-existing effect at symbol level, to be measured, not
  assumed.** D50 already matches symbols per sheet. On r2, 26 distinct
  references are placed on a sheet where the point is padding (25 with
  recipient map content, 1 with recipient ambiguous), and 2 where it is
  ambiguous. These are **exposure counts**. Padding at the coordinate
  does not establish that no detection can match the reference, since
  D50 matches within a non-zero radius. The attribution **can** leave
  such references unmatched (false negatives on their own sheet) and
  **can** leave correct detections on the recipient sheet without a
  reference (false positives), **in the published 55-map scores, under
  any tile join**; the actual effect depends on the reference set, where
  the detections fall, and the matching radius. No observed false
  negative or false positive count, and no F1 change, has been measured.
  A whole-file pass would find any other references in their own
  sheet's padding beyond these seam contacts.

What this means for § 4, item 1. For case-2 references, adding a copy
(option a) would keep a phantom instance in padding on the wrong sheet; the
matching fix is to correct the sheet label. Case 3 needs a sheet-specific
centre. The 1/3-candidate needs both sheets viewed before any reading. Either is a **reference correction**, distinct from the join change
and disclosed separately with its own timing (E93's accepted wording). It
needs adjudication against both sheets' imagery. Astra's preference for (a)
was conditional on exactly that adjudication. The stop stands.

## Changelog

### 2026-11-19 — Pixel convention corrected; § 5 retitled and revised (seam audit agent)

Trigger: Astra's review of the own-sheet audit
(`~/agent-mail/codex/outbox/claude/20261118T145509Z-astra-seam-pixel-convention-interim.md`,
`…T145706Z-astra-seam-own-sheet-review.md`), relayed by the main session.
Each point was verified by this agent before editing: the world-file
convention (from the ESRI definition, the project's tiler, and the frame
polygons), the re-measurement on zbook (`768cb2a9b` fix, `7056bb857`
outputs; every changed verdict in `scripts/out/compare_pixel_fix.txt`),
and the import lineage (`301b51128`; the merge rows and import notes at
`f6f5ffe54`).

| Item | Before | After |
|---|---|---|
| § 1, r2 ambiguous / map content (references) | 18 / 32 (26) | 16 / 34 (27) |
| § 1, the other four files' map-content contacts | 32–35 | 34–37 |
| § 1, r2 contacted tiles (map content) | 26 | 28 (11 still move) |
| § 4 item 1, r2 pairs / (a) references / (d) tiles removed | 26 / 26 / 52 (41) | 27 / 27 / 55 (44) |
| § 4 item 1, r50 map-content contacts with a phantom; (a) references | 29 of 33; 4 | 29 of 35; 5 |
| § 5 heading | "the contacts are not double printings" | "reference attribution requires adjudication" |
| § 5, references with map content on both sheets | none in any file; case 1 "ruled out for every contact" | **one 1/3-candidate in every file** (`student:04282` in r2; windows 0.471 / 0.488) |
| § 5, r2 2-candidates | 25 | 25 |
| § 5, r50 2-candidates with a phantom | 20 of 24 | 21 of 25 |
| § 5, Astra comparison | "agrees on all 40 r2 pairs" | 39 of 40 final, 37 of 39 original, as a correspondence between different classifiers; exceptions named |
| § 5, centre marking | "the marking step did not cause it" | the attribution concern predates centre marking; marking moves some padding/ambiguous classes |
| § 5, symbol-level effect | "26 … placed on a sheet where the point is padding" read as false negatives and positives | 26 in padding and 2 ambiguous, as exposure counts; possible effects depend on references, detections, and the matching radius; none measured |
| § 5, lineage | marking step only | traced to the import commit: 24 of 26 exact, 2 via documented merges, same labels |

The 2026-11-19 own-sheet entry below is corrected in place where it said
§ 5 rules out double printing. Unchanged: the stop, § 2's crops, § 3,
and the decisions asked of the PI (item 3 now counts 16 ambiguous
contacts).

### 2026-11-19 — Own-sheet evidence added (§ 5); § 2 corrected (main session)

Trigger: Astra's paired panels and source-padding diagnostic, and the
own-sheet measurement (`dry-run.md` § 2.4). § 2's two "confirmed" examples
are corrected: they confirmed a symbol on the neighbouring sheet, and both
points lie in padding on their own sheet. New § 5 ruled out double printing
for every contact (withdrawn; see the correction at the end of this
entry), and set out the label-error and displaced-counterpart readings
and the possible pre-existing symbol-level effect. § 4 item 1 now
points to § 5. The title, which read "55-map mounds printed on both sides
of a sheet seam", now says the contacts were first read as double printing.
No measurement in §§ 1–4 changed. [Correction, 2026-11-19, entry above: § 5
no longer rules out double printing; that claim rested on a half-pixel
error and on reading the ambiguous/map-content boundary categorically, and
a displaced counterpart would itself be a printed instance.]

### 2026-11-19 — Seam counts corrected; § 1 made precise (W1.0 agent)

Trigger: two reviews by Astra (GPT, Codex, Astra lane):
`~/agent-mail/codex/outbox/claude/20261118T130529Z-astra-seam-measurement-counting-finding.md`
and `…/20261118T130721Z-astra-e93-seam-paragraph-review.md`, relayed by
the main session. Verified by this agent before editing.

| Item | Before | After |
|---|---|---|
| § 4 item 1, option (a) on r2 | "32 second copies" (contacts) | 26 references to add (40 with ambiguous); 32 (50) contacts kept as contacts |
| § 4 item 1, option (c) on r2 | 333 tiles: 11 map content, "the rest padding" | 333 tiles, disjoint: 11 map content, 6 ambiguous, 316 confirmed padding, 0 remainder |
| § 4 item 1, r50 phantoms | "the r50 review already did (a)" | a lead, not confirmation of identity |
| § 1, last paragraph | "the printed copy was not digitised"; a detection "would be scored a false positive" | measured proximity, visually confirmed examples, and unadjudicated candidates kept apart; symbol-level and tile-level effects stated separately (11 tiles on r2) |

Unchanged: every tile count, the stop, and the decisions asked of the PI.

### 2026-11-19 — Wave 2 drafting moved to the continuing list (main session)

Trigger: W1.0 finished its ruling-independent steps. The Wave 2
specification and cost projection moved from "paused" to "continuing",
drafted with the seam handling left open (§ 3). No decision or measurement
in this record changed.

### 2026-11-18 — The read-only measurement for the ruling added (W1.0 agent)

Trigger: the main session's request (§ 4, item 1). Added the measured
paragraph under § 4, item 1, from `dry-run.md` § 2.2
(`scripts/seam_second_copy.py`; outputs `scripts/out/seam_second_copy.txt`
and `.json`). No ruling, decision, or other text in this record changed.

### 2026-11-18 — Original publication

Written when the stop was raised, with the main session's verification of
two crops and its reading of what continues.
