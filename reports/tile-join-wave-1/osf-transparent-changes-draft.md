# OSF transparent-changes record: tile-level classification (draft)

> **Last revised**: 2026-11-19 (the 55-map seam bullet made precise on
> Astra's second review). See [§ Changelog](#changelog) for revision
> history.

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
>   text. The PI's ruling on the 55-map seam stop (see Limits) is pending.
>   Bracketed items marked **[TO FILL]** must be completed or removed before
>   posting.
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
first of the tiles it was seen on. A mound seen on two tiles was credited to
one of them, while its reference counted in both. The other tile could
therefore be scored as a miss that the merged pipeline did not make, unless
another detection already made that tile positive.

We tested this by scoring the reference mounds as their own detections. On
the 487-tile Era-2 frame, where 117 of 435 mounds (26.9 %) lie in two or
more tiles, a perfect merged detector scored tile-MCC 0.8711 under the
original rule (196 true positives, 33 false negatives), and 1.0 under rules
that assign by location. A rule that cannot give a perfect detector a
perfect score is not a valid measurement for merged output. For unmerged
output it remains correct only as a measure of each tile's own response:
where the tile recorded for each detection is the tile the model was
actually shown, and the tiles used for scoring are the tiles the model saw.
Unmerged output alone is not enough to make it valid.

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
to references. This finding is specific to the Era-2 frame: on the larger
55-map corpus, at least some mounds are printed on both sides of a sheet
seam (see Limits).

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
when the choice was made. The 55-map seam contacts described under Limits
were found after the third decision, on 18 November 2026.

### What is and is not affected

- **Not affected by the change of tile rule**: the point estimates of
  symbol-level F1, precision, and recall, the registered primary outcome,
  with the reference mounds held fixed. Mounds are matched to references by
  location on each map before any tile is consulted. If the pending 55-map
  seam ruling (see Limits) corrects the reference, that correction's effect
  on these estimates is a separate change, disclosed with its own timing,
  and the results before and after it are both kept.
- **Affected**: tile-MCC, tile-F1, sensitivity, and specificity (the
  secondary outcome). The rule used for them is invalid for merged output.
  The numerical effect must be measured for each condition; a condition's
  reported value may remain unchanged.
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
- On the larger 55-map corpus, the equivalent check, run on 18 November
  2026 on revision r2 of the 55-map reference (erratum E84), found
  reference mounds whose positions fall on a neighbouring sheet's map
  content, rather than its black no-data padding, with no reference on
  that neighbouring sheet nearby: 32 such contacts (26 reference mounds),
  at nine sheet seams, none within 50 m of a reference on the contacted
  sheet. The check detects map content, not mound symbols, and neighbouring
  sheets are slightly misregistered at these seams. Visual inspection of
  two examples confirmed a printed mound symbol on the neighbouring sheet
  in both; the remaining candidates have not been adjudicated. This shows
  that the padding-only rationale given under "Why this reading" cannot be
  generalised to the 55-map corpus. The two outcomes are affected
  differently. At symbol level, a correct detection of a neighbouring
  sheet's printed copy has no reference on its own sheet to match and
  could count as a false positive. At tile level, a tile counts as a false
  positive only if it holds no reference of its own sheet at all: counting
  these contacts as references would change 11 tile labels, not one per
  contact. The work stopped. The remaining candidates and any reference
  correction need adjudication, and the PI's ruling is pending. [TO FILL:
  the ruling; any change it makes to the 55-map reference or to the
  estimand, and, for a reference change, its effect on symbol-level F1,
  precision, and recall as a separate component; and whether each was made
  before or after any sheet-specific 55-map result was computed.]

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
- the 55-map seam stop:
  `reports/tile-join-wave-1/stop-2026-11-18-55map-seams.md` [TO FILL:
  confirm the path once it reaches the main branch];
- the re-scoring ledger: [TO FILL, Wave 2: path].

<!-- POSTABLE TEXT ENDS -->

---

## Changelog

### 2026-11-19 — Seam bullet made precise, on Astra's second review

Trigger: Astra's review of `652786ae8..87d3dfc47`
(`~/agent-mail/codex/outbox/claude/20261118T130721Z-astra-e93-seam-paragraph-review.md`),
which found the earlier corrections addressed and the new seam text in
need of two distinctions. Checked against
`reports/tile-join-wave-1/dry-run.md` § 2.2 and the stop record § 2, on
branch `tile-join-wave-1-w10`.

| Passage | Before | After |
|---|---|---|
| Limits, 55-map check | the neighbouring copy "was not digitised" for all 32 contacts, and a correct detection "would count as a false positive" | measured proximity (none within 50 m), two examples confirmed by eye, the rest unadjudicated; symbol-level and tile-level effects stated separately (11 tile labels, not one per contact) |
| What is and is not affected | symbol-level point estimates "Not affected" | not affected by the change of tile rule, with the reference held fixed; a reference correction would be a separate, separately timed change, with both results kept |
| Why this reading | "some mounds are printed on both sides" | "at least some mounds are printed on both sides" |

Not changed: E1 to E3 of the first review, the registration excerpt, and
every other placeholder. Not posted. Commit: this entry's commit on
`tile-join-wave-1-w13`.

### 2026-11-18 — Revised on Astra's review; the 55-map seam stop added

Trigger: Astra's (GPT, OpenAI Codex) review of the draft at `652786ae8`
(`~/agent-mail/codex/outbox/claude/20261118T124335Z-astra-e93-osf-draft-review.md`;
verdict: accept the framing as a working draft, with three text
corrections), and the 55-map seam stop of the same day
(`reports/tile-join-wave-1/stop-2026-11-18-55map-seams.md`, on branch
`tile-join-wave-1-w10`).

| Passage | Before | After |
|---|---|---|
| What we found, merged detection | the other tile "was scored as a miss" | it "could therefore be scored as a miss … unless another detection already made that tile positive" |
| What we found, unmerged output | the rule "remains correct for unmerged output" | correct only where the recorded tile is the tile shown and the scoring tiles are the tiles the model saw (`reports/tile-mcc-geometric-join-2026-09-12.md:54–56`) |
| What is and is not affected | affected "for every merged condition" | invalid for merged output; measured for each condition; a value may remain unchanged |
| Limits, 55-map check | not yet run; [TO FILL] its outcome | 32 map-content contacts (26 references) at nine seams; the work stopped; [TO FILL] the PI's ruling, any reference or estimand change, and its timing relative to results |

Also: the Era-2 padding finding is marked as specific to that frame; the
seam finding's date is placed after the third decision; the original
publication entry below now dates the draft against the new joins. Not
changed: the registration excerpt, the three decisions and what was known
at each, the description of the new joins, and every placeholder other
than the 55-map one. Not posted. Commit: this entry's commit on
`tile-join-wave-1-w13`.

### 2026-11-18 — Original publication

First draft, written in Wave 1 (W1.3) beside the draft of erratum E93,
before any evaluation was re-scored under the new sheet-specific joins. The
section on the change's effect on reported results, the posting date, the
re-scoring ledger path, and the 55-map check outcome are placeholders. Not
posted.
