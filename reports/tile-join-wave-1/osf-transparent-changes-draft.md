# OSF transparent-changes record: tile-level classification (draft)

> **Last revised**: 2026-11-18 (original publication: Wave 1 draft, W1.3). See [§ Changelog](#changelog) for revision history.

## Draft status (not part of the postable text)

> **DRAFT — not posted; posting requires the PI's approval of the exact
> text.**
>
> - **What this is**: the draft of a dated transparent-changes record for
>   the study's Open Science Framework (OSF) project, required by the
>   principal investigator's (PI's) ruling D73 (1)
>   (`planning/pi-decisions-2026-09-20.md`). It is the outside reader's
>   version of erratum E93
>   (`docs/methodology/preregistration/protocol-errata.md`, entry E93, also a
>   draft).
> - **Written by**: Claude (Anthropic), Claude Code, model lane Opus 5.5
>   (`claude-opus-5-5`), Wave 1 work item W1.3 of
>   `planning/tile-join-wave-1-spec-2026-11-01.md`, on branch
>   `tile-join-wave-1-w13` at base `e92d1c5d7`, 2026-11-18. Every number and
>   date in the postable text was read from the file named beside it in
>   erratum E93.
> - **Not final**: the section "What the change does to the reported
>   results" is a placeholder that Wave 2 fills; Wave 4 finalises the whole
>   text. Bracketed items marked **[TO FILL]** must be completed or removed
>   before posting.
> - **Decisions for the PI**: approve, amend, or hold the text (Wave 1
>   specification § 9, decision 3); and choose the OSF form (a registration
>   update, as for erratum E91, or a project file or wiki page).
> - **Posting** is an external action. Nothing here has been posted, and
>   nothing may be posted until the PI has approved the exact text.

---

<!-- POSTABLE TEXT BEGINS -->

## Transparent change: how tile-level classification is scored (erratum E93)

**Date of this record**: [TO FILL: date of posting]. **Decided**: 1 and 18
November 2026.

### What was registered

The registration's secondary outcome (§ 4.2) is tile-level discrimination,
measured by the Matthews correlation coefficient (MCC). Each map tile is
classified by two questions: does it hold a mound ("Has mounds"), and did
the model detect at least one mound in it ("Detected ≥1 mound")? Tile-level
sensitivity and specificity are reported beside it. Section 3.5 asks for
95 % bootstrapped confidence intervals. The registration does not say how a
detection is assigned to a tile when tiles overlap, when one detection
merges sightings from several tiles, or when neighbouring map sheets meet.
It does not name the resampling unit for the intervals either.

The registered text is unchanged. It is preserved verbatim in the
repository at `docs/methodology/preregistration/osf/preregistration.md`,
lines 379–394.

### What we found

Our evaluation frames tile each map with overlapping tiles. The scoring code
assigned each detection to the single tile recorded in its name field, and
each reference mound to every tile that contains it. For a merged detection
(several sightings of one mound combined into one point, as in every
consensus and verified condition), the name field holds the alphabetically
first of the tiles it was seen on. A mound seen on two tiles was therefore
credited to one of them, while its reference counted in both; the other
tile was scored as a miss that the pipeline did not make.

We tested this by scoring the reference mounds as their own detections. On
the 487-tile Era-2 frame, where 117 of 435 mounds (26.9 %) lie in two or
more tiles, a perfect merged detector scored tile-MCC 0.8711 under the
original rule (196 true positives, 33 false negatives), and 1.0 under rules
that assign by location. A rule that cannot give a perfect detector a
perfect score is not a valid measurement for merged output. It remains
correct for unmerged output, where each tile's own response is scored.

The same name rule distributed true and false positives over tiles in the
per-tile count tables from which the F1 bootstrap intervals and tile-swap
permutation tests are computed.

### What changed

After the change, both steps assign by location, within one map sheet:

- **Tile classification** (tile-MCC, tile-F1, sensitivity, specificity): a
  tile counts as holding a mound if a reference mound recorded on that
  tile's own sheet lies in it, and as detected if a detection attributed to
  that tile's own sheet lies in it.
- **Per-tile count tables** (behind the F1, precision, and recall intervals
  and permutation tests): each detection and each missed reference is
  counted once, in the tile of its own sheet whose centre is nearest, among
  the tiles of that sheet it falls in.

The original rule and two earlier location-based rules remain in the code
under their own names, so that previously published values can still be
reproduced exactly.

### Why this reading

Section 4.2's wording ("Has mounds", "Detected ≥1 mound") reads naturally
as containment, but it does not settle how merged detections map onto
overlapping tiles. This is one defensible reading, not the only one.

We confined both steps to a single sheet because, on the Era-2 frame, all
15 reference mounds that fall inside another sheet's tile lie in the black
no-data padding at the edge of one sheet (K-35-052-4), on tiles that show
no map content at those points. A frame-wide rule would mark those tiles as
holding mounds that no model was shown. Each reference mound records one
sheet, and the same sheet attribution is already used to match detections
to references.

### When, and what was known

The choice of tile rule was made three times, each time after results were
available:

1. **12–13 September 2026.** A decision to assign by location was paused
   when an audit of 149 committed conditions showed that both
   location-based rules raised tile-MCC on 146 and 145 of the 146
   conditions it could score (mean +0.106 and +0.075). The original name-based rule was then confirmed as
   the published convention, with the location-based rules kept as a
   sensitivity option.
2. **1 November 2026.** After the perfect-detector test, the principal
   investigator (PI) ruled to
   replace the name-based rule with frame-wide location-based rules. That
   ruling described the change as restoring the registered definition.
3. **18 November 2026.** After an independent review by a second AI model
   (GPT, in OpenAI Codex), the PI re-described the change as a
   clarification made after results were known and confined both rules to
   one sheet.

When the November decisions were made, the following were already known:

- all symbol-level F1, precision, and recall results, and all published
  tile-MCC values under the name-based rule;
- the frame-wide location-based tile-MCC of 149 committed conditions,
  including three that the name-based rule could not score;
- sensitivity runs (30 October 2026) re-ranking tile-MCC under all three
  earlier rules, which showed that published statements that F1 and
  tile-MCC disagree rest largely on the name-based rule;
- the perfect-detector result.

Not known at either date: any sheet-confined tile-MCC for a real condition,
and any F1 interval or permutation test computed under a count table other
than the name-based one. The sheet-confined values can differ from the
already known frame-wide values only on tiles that a neighbouring sheet's
mounds or detections reach, so much of their effect could be anticipated
when the choice was made.

### What is and is not affected

- **Not affected**: the point estimates of symbol-level F1, precision, and
  recall, the registered primary outcome. Mounds are matched to references
  by location on each map before any tile is consulted.
- **Affected**: tile-MCC, tile-F1, sensitivity, and specificity (the
  secondary outcome), for every merged condition, by an amount that must be
  measured condition by condition.
- **Possibly affected**: F1, precision, and recall bootstrap intervals,
  tile-swap permutation p-values, the rankings and admissible sets built on
  them, and the diagnostics that flag an interval as unreliable. Any
  conclusion that rests on one of these is re-checked. Because reassigning
  outcomes to tiles can make tests over-confident as well as noisier, a
  spatial-block resampling check on both evaluation corpora is required
  before any affected significance claim is final.
- Three conditions withheld under the original rule become scoreable. They
  re-enter the comparisons they otherwise qualify for by a rule fixed before
  their sheet-confined scores were computed; the comparison without them is
  reported beside it.

### What the change does to the reported results

[TO FILL, Wave 2 and Wave 4: the number of evaluations re-scored, the
distribution of the change in tile-MCC, every significance, ranking, or
admissible-set change, the outcome of the spatial-block check, and the
claims restated or withdrawn, each with its repository path.]

### Limits

- The new rule was chosen after results were known, by the same team that
  reported them.
- It is one reading of § 4.2. Other readings remain possible, and the
  previously published values can be reproduced under the original rule.
- One recorded sheet per reference mound, with no two mounds from
  different sheets within 1 km of each other on the Era-2 frame, is
  consistent with digitising each sheet separately, but does not prove
  that no mound is printed on two sheets.
  The equivalent check on the larger 55-map corpus is part of the work and
  had not been run when this record was drafted. [TO FILL, Wave 4: its
  outcome.]

### Where the full record is

In the study's public repository (`saross/map-reader-llm` on GitHub):

- erratum E93: `docs/methodology/preregistration/protocol-errata.md`;
- the decision record, with the perfect-detector test and its scripts:
  `planning/tile-join-resolution-2026-11-01.md` and
  `planning/tile-join-resolution-2026-11-01-scripts/`;
- the rulings, D72 and D73: `planning/pi-decisions-2026-09-20.md`;
- the implementation specification: `planning/tile-join-wave-1-spec-2026-11-01.md`;
- the September 2026 audit: `reports/tile-mcc-geometric-join-2026-09-12.md`;
- the October 2026 sensitivity runs:
  `reports/s166-agent-records/mcc-join-tiering.md` and
  `reports/s166-agent-records/k-ladder-mcc-join.md`;
- the re-scoring ledger: [TO FILL, Wave 2: path].

<!-- POSTABLE TEXT ENDS -->

---

## Changelog

### 2026-11-18 — Original publication

First draft, written in Wave 1 (W1.3) beside the draft of erratum E93,
before any evaluation was re-scored. The section on the change's effect on
reported results, the posting date, the re-scoring ledger path, and the
55-map check outcome are placeholders. Not posted.
