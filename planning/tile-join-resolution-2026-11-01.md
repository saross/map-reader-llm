# Tile-join resolution — decision record and execution plan

> **Last revised**: 2026-11-18 (gate R round 1: Astra's review and the
> PI's rulings D73). See [§ Changelog](#changelog) for revision history.

- **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
  (`claude-opus-5-5`), main session S167 on zbook, with the principal
  investigator (PI); revised in S168 on amd-tower. Every figure below was
  re-read from the files named beside it, on `main` at `c33c1463d` (S167)
  or `73f74e9af` (S168), before it was written here.
- **Status**: rulings **D72 (1)–(4)**, as revised by **D73 (1)–(7)**
  (`planning/pi-decisions-2026-09-20.md`). Gate R round 1 is closed:
  Astra's review is answered in § 7. **Waiting on Astra's round-2 review
  of this revision and of the Wave 1 specification before Wave 1
  launches.** Nothing has been re-scored, and no committed result has
  changed.
- **Target**: the original target (all data and results settled, and the
  write-up begun, by 2026-11-08) passed during a pause in the work. The PI
  has not yet set a new one.

## 0. The decision in one paragraph

The published tile join (`id`, S153 ruling 6) gives a **perfect** detector
a tile-level Matthews correlation coefficient (tile-MCC) of **0.8711**
instead of 1.0, whenever the detector merges duplicates, as every consensus
and verified cell does. Here is why. A merged point's `source_tile` is the
alphabetically first of the tiles it was seen on, while a reference mound
counts in every tile it lies in. On our overlapping frames, a mound seen
on two tiles can therefore leave a false-negative tile that the pipeline
did not cause. This makes the rule invalid as a measurement for merged
output, not merely one defensible choice among several, so no workaround
that keeps `id` values in the reported numbers or in the robustness set is
acceptable. The PI ruled (D72, as revised by D73 after Astra's review):

- **(1)** tile-level classification (tile-MCC, tile-F1, sensitivity,
  specificity) moves to **containment within each sheet**: a tile is
  reference-positive if one of *its own sheet's* gold-standard (GS) mounds
  lies in it, and detected if a detection scoped to *its own sheet* lies
  in it (D72 (1), D73 (2); § 2.6);
- **(2)** the per-tile count tables behind F1's bootstrap intervals and
  tile-swap permutation tests book each outcome once, to the nearest-centre
  tile **of the detection's scoped sheet** (references: their recorded
  sheet), as false negatives already are (D72 (2), D73 (2));
- **(3)** the paper-cited artefacts are re-scored first, but a run does
  not stop at that subset if it can carry on;
- **(4)** Astra reviews this record before compute is spent (round 1
  closed 2026-11-18, § 7; round 2 requested);
- **(5)** the change is disclosed as a clarification made after results
  were known, by erratum E93 plus a dated transparent-changes record on
  the Open Science Framework (OSF) project (D73 (1); § 2.2);
- **(6)** a spatial-block resampling check is required, on both corpora,
  before any affected significance claim is finalised (D73 (3); § 5).

Symbol-level F1, precision and recall, the registered primary outcome, are
not touched by any of this (§ 2).

## 1. The defect, stated once

| Step | Code | What it does |
|---|---|---|
| A merged point gets one name | `scripts/lib_consensus.py:307–309`, `:394–395` | "`source_tile` is still the alphabetically first" of the tiles the cluster's members were seen on. The full list is kept in `source_tiles` (since D62 (1)) |
| Tile classification under `id` | `scripts/lib_advanced_metrics.py`, `calculate_tile_classification` | detections are booked by name, references by containment ("`id` keeps the legacy asymmetric pairing … purely so that published numbers reproduce") |
| Per-tile F1 counts under `id` | same file, `compute_per_tile_tp_fp_fn` (`:2889–2890`) | "TPs and FPs to the detection's `source_tile`, unmatched FNs to the reference's primary tile (nearest centroid)" |
| The default | same file, `:149` | `TILE_JOIN_DEFAULT: str = TILE_JOIN_ID` |

Every frame tiles its maps with overlap, so the asymmetry can bite on any
frame. A mound seen on tiles T1 and T2 is credited by name to T1 only. Its
reference counts in both, so T2 becomes a false negative unless another
detection already makes it positive, even though the model reported the
mound there.

## 2. Evidence

### 2.1 The perfect-detector test

`tile-join-resolution-2026-11-01-scripts/perfect_detector.py` scores the
GS reference mounds *as* the detections, on the Era-2 frame
(`inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`), for two
perfect pipelines. Output: `perfect_detector.txt`. Of the 435 mounds in
the frame, 117 (26.9 %) lie in two or more tiles.

| Perfect pipeline | `id` | `geometric-primary` | `geometric-contains` |
|---|---|---|---|
| merged: one point per mound, named for the alphabetically first containing tile | **0.8711** (TP 196, FN 33) | 1.0000 | 1.0000 |
| per-tile: one point per (mound, containing tile) | 1.0000 | 1.0000 | 1.0000 |

`id` is correct for unmerged per-tile output, which is the case S153
ruling 6 reasoned about ("the pipeline's decision on the tile the model
saw"). It is wrong for merged output, which covers every consensus and
verified cell.

### 2.2 The registered definition

`docs/methodology/preregistration/osf/preregistration.md:379–390`
(§ 4.2) defines the unit as the tile and classifies it as "Has mounds" ×
"Detected ≥1 mound", for a holdout of 30 empty and 30 populated tiles.
For one tile's own model output, "detected in that tile" and "named for
that tile" coincide. § 4.2 does not say how merged detections are
projected back onto overlapping tiles, whether evidence from another sheet
may count, or whether the intended output is each tile's own model
response (Astra, R1). Containment within each sheet is therefore a
defensible clarification for merged output, and the perfect-detector test
shows that `id` cannot represent the quantity at all. It is not the only
possible reading of the registration, and it was chosen after results
were known.

**Disclosure (D73 (1)).** The original registered text is preserved. The
change is reported as erratum E93 *and* as a dated transparent-changes
record on the OSF project, stating the defect, the clarification, its
date, and which results were already known when the choice was made. This
replaces the S167 framing, which called `id` an unrecognised departure
that the fix simply undid.

### 2.3 Scope: what is and is not affected

| Result | Status | Basis |
|---|---|---|
| Symbol-level F1, precision and recall (primary outcome, every hypothesis decided on F1) | **untouched** | matched per map by Hungarian assignment on geometry, "before any tile is consulted" (`lib_advanced_metrics.py:2899`) |
| Tile-MCC, tile-F1, sensitivity, specificity (secondary outcome) | **an invalid rule for merged output; each cell's effect must be measured** | § 1. Another detection may already make an overlapping tile positive, so the defect need not move every cell, and 117 multiply contained references do not imply 117 false-negative tiles (Astra, R1) |
| F1, precision and recall bootstrap intervals and means, tile-swap permutation p-values, tiers, F1 Hsu sets | **unknown** | point estimates exact (each object booked once); the spread of counts over tiles follows the name rule for TP/FP, so the null distributions may move. Reassignment can make tests anti-conservative, not only noisier (Astra, R3; § 5) |
| Coverage diagnostics and the interval-reliability flags (`coverage`, `coverage_status`, `sparse_coverage`, `ci_unreliable`, `ci_excludes_point`, and their summary roll-ups) | **may flip** | derived from the same per-tile count table (`TILE_JOIN_WITHHELD_QUANTITIES`, `scripts/lib_advanced_metrics.py:178–189`; Astra, R4) |
| Sheet attribution of tile outcomes | **wrong under the existing geometric routines** | they book detections and assign references against *all* frame tiles, not the sheet D50 matched on (`lib_advanced_metrics.py:2960–2975`, `:3005–3011`, `:5010–5013`; Astra, R2; § 2.6) |

### 2.4 Every frame overlaps

`frame_census.py` (output `frame_census.txt`) reads the frame each
evaluation was scored on, for the 21 signed register rows that quote
tile-MCC:

| Frame | Tiles | Summed area / union |
|---|---:|---:|
| `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson` | 487 | 1.2783 |
| `inputs/vectors/bounds/384/full_evaluation_bounds.geojson` | 487 | 1.2768 |
| `outputs/grid-2026-08-18/scoring/bounds/grid_common_bounds.geojson` | 487 | 1.2834 |
| `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` | 8,541 | 1.4527 |
| `inputs/vectors/bounds/full_evaluation_bounds.geojson` (512 px) | 340 | 1.2814 |
| `outputs/h13/scoring/bounds/h13_common_bounds.geojson` | 340 | 1.2918 |
| `inputs/vectors/bounds/384/h10_test_bounds.geojson` | 327 | 1.1743 |
| `inputs/vectors/bounds/256/full_evaluation_bounds.geojson` | 1,032 | 1.2853 |

The 55-map frame overlaps most: neighbouring sheets also overlap at their
seams, and some tiles have a near-duplicate from the next sheet about
170 m away. Only 5 of the 21 rows have any committed geometric-join
reading. That count is a text match, so it is indicative. In the 47 Era-2
board cells whose detection files record `source_tiles`, 19.4 % of
detections (3,698 of 19,017) were seen on two or more tiles; the other 56
cells' files carry no list.

### 2.5 What the S166 sensitivity runs showed

From `reports/s166-agent-records/mcc-join-tiering.md` and
`k-ladder-mcc-join.md`, under `id` / primary / contains:

- the board's top-F1 cell ranks 21st / 1st / 1st on MCC;
- F1-admissible cells that are also MCC-admissible: 9 / 50 / 45 of 52;
- tile-MCC falls from K = 1 to the best F1 rung on 16 / 9 / 11 of 21
  ladders;
- K = 1 is MCC-admissible on 22 / 17 / 16 of 22 ladders;
- 59.6 % (board) and 67.3 % (K-ladder) of `id`'s false-negative tiles
  contain one of the cell's own detections.

The claims that the "F1 and tile-MCC disagree" (Obs 482, Obs 513, R6-18)
and that "tile-MCC does not follow F1" (R3-12, R3-13) look like products of
the defect. Frame-wide contains values are already computed for the
board (`results/tile-join-audit/era2-board-mcc-tiering-2026-10-30/`) and
the K-ladder (`results/k-ladder-2026-09-12/mcc-join-2026-10-30/`). Under
D73 (2) they are historical comparison values, not the published values:
the sheet-specific readings may differ from them, but only on tiles where
another sheet's evidence reaches (§ 2.6; gates G1 and G2).

### 2.6 Sheet boundaries (gate R round 1, R2; D73 (2))

The existing geometric routines test points against every tile in the
frame, whatever its sheet, so a reference attributed to one sheet can make
another sheet's tile positive. Whether that is right depends on how the
GS was made and on what the other sheet's tile shows.
`tile-join-resolution-2026-11-01-scripts/sheet_boundary_check.py` (output
`sheet_boundary_check.txt`) imports nothing from the scorer and answers
both, on the Era-2 frame:

- **The GS is digitised per sheet, and no mound appears twice.** Its 569
  references each carry one `Map` (Elenovo 217, Rakovski 196,
  K-35-052-4 136, Lesovo 20). No reference has a reference from a
  different sheet within 1 km; the closest cross-sheet pair is 1,313.0 m
  apart.
- **Every cross-sheet contact is no-data padding.** All 15 references that
  lie inside another sheet's tile are Elenovo mounds in K-35-052-4's last
  column of tiles (`x4032`), at pixel columns 134–299. Two of those tiles
  were inspected (`inputs/tiles_384/K-35-052-4_32635/K-35-052-4_32635_x4032_y672.png`,
  `…_x4032_y1680.png`): the map ends near column 115 and 105 respectively,
  and the rest is black.

A frame-wide ("mosaic") join therefore makes K-35-052-4's edge tiles
reference-positive for mounds that no model was shown. That is the same
class of error D72 removes, so the PI ruled sheet-specific semantics
(D73 (2)). It also gives tile outcomes and symbol matching one definition
of where a mound is, since D50 already matches per sheet, and it is immune
to the misregistration seen on the 55-map frame, where the same ground
appears on neighbouring sheets about 170 m apart (§ 2.4). It does not add
a corpus re-score: Wave 2 re-scores every tile-bearing evaluation once,
whichever rule is chosen. The equivalent check of the 55-map GS is owed
before Wave 2 (Wave 1 spec, W1.0).

## 3. The rulings, and what was rejected

- **Rejected: options A and B** of the S166 records (keep `id` and add a
  sensitivity sentence; or keep `id` and narrow claims to what holds under
  all three joins). Both keep an invalid rule, either in the reported
  numbers or in the robustness set. The PI's objection was that this would
  produce outcomes that are consistent but consistently incorrect.
- **Rejected for classification: `geometric-primary`.** It too scores the
  perfect detector at 1.0, but it redefines the unit as a tile's
  nearest-centre core, a new deviation from § 4.2. It stays the rule for
  count tables, where each object must be counted exactly once (D72 (2)).
- **Not built: a `source_tiles` join** (credit a merged point to every
  tile it was seen on). It is closest to ruling 6's intent, but it does
  not exist, 56 of the board's 103 detection files lack the list it
  needs, and it would measure exposure rather than the registered
  presence.
- **`id` stays in the code** as a named legacy join, so historical
  artefacts can still be reproduced. It stops being the default.
- **Rejected (D73 (2)): frame-wide geometric joins as the final
  definition.** The existing `geometric-primary` and `geometric-contains`
  routines reach across sheets (§ 2.6). They stay in the code under their
  current names, so the S166 artefacts that carry those names keep their
  meaning, and become historical comparisons.
- **Rejected (D73 (6)): aliasing `TILE_JOIN_DEFAULT`.** The single name is
  retired, so every caller must choose a classification or a count-table
  join explicitly.

## 4. Design of the change (Wave 1)

The full specification is `planning/tile-join-wave-1-spec-2026-11-01.md`.
In outline:

1. **Two defaults, one per purpose**, in `scripts/lib_advanced_metrics.py`,
   both **sheet-specific** (D73 (2)), under new names so that historical
   provenance stays unambiguous:
   - tile classification defaults to containment within each sheet;
   - per-tile count tables default to nearest-centre within the
     detection's scoped sheet, with references on their recorded sheet.

   `TILE_JOIN_DEFAULT` is retired (D73 (6)). Every caller is audited.
   Classification-style containment must never reach a count table (it
   would double-count): refuse that combination. Validation of a
   historical artefact uses the rule it recorded; every analysed value is
   then computed under the explicitly requested rule (Astra, S2).
2. **The perfect-detector test, made permanent (tier 1).** On the real
   Era-2 frame, with each reference's own sheet preserved, and on
   synthetic overlapping frames with seams:
   - ground truth fed back as merged detections gives tile-MCC 1.0 and
     symbol F1 1.0;
   - unmerged per-tile occupancy gives perfect tile classification, and
     the duplicates it contains are correctly penalised at symbol level
     unless passed through the real deduplication path (Astra, S1);
   - the per-tile count table sums to the symbol-level totals, overall
     and per sheet.

   Its red sentinel: the same merged test under `id` gives 0.8711 on the
   Era-2 frame.
3. **The three withheld Gemini 3.7 GS text cells** become scoreable under
   a geometric join. They enter their families by a fixed eligibility rule
   (D73 (4)): if the join was the only reason for their exclusion, they
   re-enter every family they otherwise qualify for. Eligibility is fixed
   before the new inference is seen, and the fixed-old-family comparison is
   shown separately.
4. **Erratum E93** (the next free number on `main` at the time of
   writing) in `docs/methodology/preregistration/protocol-errata.md`,
   with the OSF transparent-changes record (D73 (1)); the before/after
   table is produced by Wave 2.
5. **Gap analysis first** (project convention): a dry-run simulation of
   Wave 2's driver over a handful of evaluations, before any code is
   written for it.

## 5. Execution plan: waves and gates

Each wave is a specified, long-running job, multi-agent where the work
splits. Each ends at a milestone where the PI reviews and approves before
the next wave launches. Compute runs on zbook, which is about as capable as
sapphire and may run as long as needed. An approved overnight wave runs to
completion rather than stopping at its priority subset. Launch discipline
follows `docs/agent-guidance.md`: all three file descriptors redirected,
nothing after the launch on the same line, watchers on terminal state
(`scripts/wait_for_run.py`) and log staleness, never `pgrep -f`. Zero API
calls throughout.

| Wave | Work | Gate before the milestone | Milestone |
|---|---|---|---|
| **R** | Astra reviews this record (amd-tower). Round 1 closed 2026-11-18 (§ 7); round 2 reviews this revision and the Wave 1 specification | review delivered by agent mail or a committed file | PI rules on the findings |
| **1** | § 4 code and tests; erratum draft; Wave 2 driver dry-run. **Smoke test:** re-score five representative evaluations (an Era-2 board cell, a K-ladder 55-map rung, an Era-1 512 px cell, a grid cell, a replicate-mean cell) plus the three withheld 3.7 cells. Runs unattended from launch to M1, stopping only on a problem (D73 (7)) | G1 (Wave 1 spec § 4): F1/P/R byte-identical; legacy replay reproduces each pass; sheet-specific tile-MCC differs from the historical contains reading only on cross-sheet tiles, each difference explained; tier-1 green | **M1**: PI reviews the smoke results and the 3.7 cells' eligibility outcome |
| **2** | Corpus re-score. 2,646 committed `evaluation.json` files (exact basename) carry tile tables, 33 of them under `archive/` (`git ls-files`; Astra, S5). Paper-cited first (cited by the register's signed rows or `docs/paper/`), then the rest, in one run, from an explicit worklist with a status and reason per file. Re-emit `tile_classification` **and** every per-tile-table-derived field (F1, precision and recall intervals and means, coverage diagnostics and flags), surgically, on the `scripts/rescore_tile_mcc_e81.py` pattern. Live `results/` files are re-scored in place; `archive/` and frozen historical artefacts get labelled corrected counterparts instead (D73 (5)) | G2: every non-target field byte-identical (the E81 guards); point F1/P/R identical; legacy replay first, under each file's recorded rule; differences from the historical board and K-ladder contains readings confined to cross-sheet tiles; a reconciled success/refusal/skip/failure ledger | **M2**: PI reviews the ledger summary (ΔMCC distribution, any interval or guard failure = stop) |
| **3** | Regenerate downstream: tierings (F1 permutation on the new count tables, MCC on sheet-specific classification), Hsu sets, boards, K-ladder tables, leaderboards, manifests, register renderings. Families recomputed with the 3.7 cells admitted by the D73 (4) rule, and the fixed-old-family comparison shown beside them | G3: a flip report: every F1 significance, tier or admissible-set change, and every MCC claim's new reading | **M3**: PI reviews the flip report and wave S |
| **S** (required, D73 (3)) | Spatial-block resampling check on **both** corpora: paired tests and intervals, MCC included, with blocks of contiguous tiles inside one sheet. The block rule (candidate edges, the basis for choosing them, and which size is headlined) is fixed and reviewed before any result is seen; sheet blocks are an extra check on the 55-map corpus. Limits stated: adjacent blocks still touch, and small frames give fewer blocks | its block rule reviewed by Astra before it runs | **M3**: no affected significance claim is finalised until S has reported; a claim it cannot support is qualified or withdrawn |
| **4** | Restate claims. The worklist is built by searching the dependency and claim records, not from this list alone (Astra, R4): the 21 signed MCC rows (`frame_census.txt`), Obs 482, Obs 513, R6-18, R3-12, R3-13, R3-14 / R6-17, the K-ladder findings §§ 4.1, 4.3, 7.2, 8.2, 8.4, 8.6, MCC leader identity, modality comparisons (`claims.iv` and `claims.v` in `results/tile-join-audit/era2-board-mcc-tiering-2026-10-30/summary.json`), "no significant rise" statements, uncertainty and coverage claims, selection-aware conclusions, any F1 claim Wave 3 or S flips, and the D71 held items; erratum E93 and the OSF record finalised | G4: drift checks green; markdownlint and tier-1 green; any skipped paper-cited artefact blocks an "all settled" verdict | **M4**: PI re-signs rows; write-up starts |

## 6. Questions for the review (gate R, round 1, as sent on 2026-11-01)

Kept as asked, so § 7's answers can be read against them.

1. Is `geometric-contains` the right literal reading of OSF § 4.2 for
   merged output on an overlapping frame? Is calling `id` an unrecognised
   departure, corrected by erratum, the right framing, or is it a new
   deviation that needs a registration update?
2. Is using two rules (contains for classification, primary for count
   tables) coherent, or should one rule serve both?
3. Can booking TP/FP by name instead of by nearest centre make the F1
   tile-swap permutation tests or BCa intervals anti-conservative, or only
   noisier? Is anything already published at risk before Wave 3 measures
   it?
4. Does anything in § 2.3's "untouched" row deserve a check we have not
   planned? For example, D50 frame scoping reads `source_tiles` to
   attribute a detection seen on two sheets.
5. Should the three withheld 3.7 cells enter their families once
   scoreable?
6. Are gates G1–G4 sufficient, and is anything missing from Wave 4's
   claim list?

## 7. Gate R round 1: Astra's review and its dispositions

Astra (GPT, OpenAI Codex, Astra lane) reviewed this record at
`4b7411c9e` and the Wave 1 specification at `4d3300e9b`, separately and
in that order, and reproduced the 0.8711 independently in JavaScript with
no project code. Review:
`~/agent-mail/codex/outbox/claude/20261101T225231Z-astra-tile-join-record-and-wave1-review.md`;
evidence: `~/agent-mail/codex/reviews/tile-join-2026-11-02/`. Verdicts:
record, **revise before closing gate R**; specification, **changes
requested**. The PI ruled on 2026-11-18 (D73).

| Finding | Disposition |
|---|---|
| R1: containment is a defensible clarification, not the only reading of § 4.2; disclose it; soften "wrong for every merged cell" | Adopted (D73 (1)); § 0 item (5), § 2.2, § 2.3 |
| R2: the geometric routines reach across sheets; choose sheet-specific or mosaic semantics | Sheet-specific, on the § 2.6 evidence (D73 (2)); § 0, § 3, § 4 |
| R3: reassignment can be anti-conservative; make the block check a requirement, covering paired tests, intervals and MCC | Required on both corpora, block rule fixed before results (D73 (3)); wave S in § 5 |
| R4: the target-field and claim inventories are incomplete | Adopted; § 2.3 coverage row, Waves 2 and 4 in § 5 |
| R5: admit the repaired cells by a fixed eligibility rule | Adopted (D73 (4)); § 4 item 3, Wave 3 |
| S1–S6 (Wave 1 specification) | Accepted; answered in the specification's revision of 2026-11-18. S1, S3, and S4 corrected errors in the specification |

**Round 2 questions** (for Astra's re-review of this revision):

1. Does the sheet-specific definition (§ 0 (1)–(2), § 2.6) answer R2? In
   particular, is it right for detections to take their sheet from D50's
   scope, and for references to use their recorded `Map`?
2. Is wave S's specification (§ 5) adequate as a requirement, and what
   must its block rule fix before results are seen?
3. Does the R1 disclosure (§ 2.2) say enough, and does anything in it
   overstate?
4. Is anything in round 1 left unanswered?

## Changelog

### 2026-11-18 — Gate R round 1 answered (S168, amd-tower)

Trigger: Astra's round-1 review (§ 7) and the PI's rulings D73 (1)–(7).
The definition, disclosure, and execution plan changed; no number in the
evidence changed.

| Item | Before | After |
|---|---|---|
| Classification rule | `geometric-contains`, frame-wide | containment within each sheet |
| Count-table rule | `geometric-primary`, frame-wide | nearest-centre within the detection's scoped sheet |
| Status of the S166 contains readings | the published values | historical comparison values |
| Framing | `id` an unrecognised departure, undone | a post-results clarification, disclosed by E93 and an OSF record |
| Wave S | parallel, low priority, 55-map only | required on both corpora before significance claims are final |
| The 3.7 cells | a PI judgement at M1 | a fixed eligibility rule |
| `archive/` artefacts | re-scored in place | labelled corrected counterparts |
| Target | 2026-11-08 | passed; not yet reset |

New: § 2.6 and its evidence script `sheet_boundary_check.py` (with
`.txt` output), § 7, and the coverage and sheet rows of § 2.3. Wave 4 no
longer lists the Obs 515 candidate, which was written at the S167 handoff
(`68fcc4eed`). Unchanged: the perfect-detector evidence (§ 2.1), the frame
census (§ 2.4), the S166 summaries (§ 2.5), and rulings D72 (3) and (4).

### 2026-11-01 — Original publication

Written at S167 after the PI paused the tile-join walk-through ("a serious
problem that needs a robust solution"). Records the perfect-detector test,
the scope check, rulings D72 (1)–(4), and the wave plan. Evidence scripts
and their outputs are in `tile-join-resolution-2026-11-01-scripts/`.
