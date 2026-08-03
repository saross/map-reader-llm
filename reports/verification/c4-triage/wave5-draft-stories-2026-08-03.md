# Wave-5 triage — pre-registered draft stories (2026-08-03, Session 126)

**Discipline**: ruling 11 (`phase3-rulings-2026-07-31.md` § 11) — these
stories are the author-side hypotheses, committed BEFORE the blind
verification passes run. The blind adjudicators do not see this file;
writer-vs-author disagreement is signal, not friction.

**Scope**: the 92 wave-5 MISMATCH rows of the post-wave-5 canonical
recompute (`3fdff7803`, sapphire; 9,588 rows total). The Obs 382
standing check on pre-wave rows ran CLEAN this wave — exactly 12 rows
moved, all attributed (ruling-15 phases 1–2: four 044 resolutions,
037#37[0] → MATCH, the 006#32/34 pair → honest MISMATCH abs_error 41;
S125 repairs: 009#30[1]/[3] and 012#48[3] → MATCH; the E39 sweep fix
`01c84b841`: 017#52[2] → MATCH at 0.7701; the e43-matched-temperature
analysis registration: 050#42[0] live count 20→21, stays MISMATCH).
Zero rows moved from the 0.7.1 passes-manifest fix (the beacon's
conditional prediction resolved to none).

**Instrument observation (for the wave record)**: `era_check` on
wave-5 rows is DEGENERATE — freshly-extracted documents carry today's
blob, so ruling 12's newest-commit-holding-the-blob heuristic resolves
at ~HEAD (e.g. 045 rows resolve at `5d91c2a97a73`, the 2026-08-01
banner commit, not the document's true 2026-05-03 era). Its
`faithful: false` merely repeats the primary mismatch. True-era
attestation for dated snapshots therefore falls to the blind passes
(manual git-era resolution at the document's own date).

## Family partition (92 rows)

| family | rows | members |
| :--- | ---: | :--- |
| A — phase3a audit era figures | 43 | all 27 MISMATCH rows of 045; all 16 of 046 |
| B — config-audit v2 at-era counts/F1 | 13 | 031#3,4,5,6,10,12[0],12[3],13,17[0],17[2],20,21,22[2] |
| C — config-audit v1 rows | 12 | 032#7,40[2],44[0],44[1],44[2],44[4],45[2],55[0],55[2],56[2],61[1],61[5] |
| D — pn-ratio rounding boundary | 6 | 041-phase2c-pn-ratio#25[3],29[2],30[0],44[0],45[1],51[3] |
| E — session-58 paired-comparison rows | 4 | 048#48[0],48[2],48[3],59[0] |
| F — session-58 appendix at-era optima | 11 | 049#2[1],13[0],25[0..2],26[0..2],30[0..2] |
| G — singletons | 3 | 051#1[0]; 056#41[0]; 058#38[0] |

## Draft stories (predictions, unseen by the blind passes)

**A (43 rows) — SNAPSHOT-DIVERGENCE, doc faithful at true era.** The
2026-05-03 completeness audit recorded verified-probabilities counts
and gap figures at audit time; the May–July recovery campaigns closed
the gaps (the document's own 2026-07-31 banner says the 35 gap figures
no longer reproduce, current gap 0, one post-audit regression per
Obs 377/ruling 6). Predicted mechanical signature: for count rows,
actual = quoted + closed-gap (e.g. 342+460=802, 3735+1=3736,
4301+57=4358, 8939+3=8942); for gap rows, actual = 0. Predicted
verdict: SNAPSHOT-DIVERGENCE for all 43; zero SNAPSHOT-DEFECT. The
document body must NOT be edited (historical record; the banner is
already the dated rider).

**B (13 rows) — SNAPSHOT-DIVERGENCE, run population grew.** The v2
configuration audit (2026-03-25) counted 12 Pro runs (5
pro-high-text-n5; 10 HIGH n5) at its era; later sessions added Pro
runs (17/10/15 now). The three F1 rows moved with later re-scoring.
The era-resolution failures ("0 candidates") reflect renamed/
restructured run directories, so manual era resolution at a
2026-03-25-adjacent commit is needed. Predicted: divergence, not
defect; possible extraction-side anchor-precision residue on the F1
rows (they may anchor to re-scored evals rather than era evals).

**C (12 rows) — MIXED; the interesting family.** v1 is the audit its
own v2 supersedes for a metadata bug. Sub-shapes: (i) temperature
rows (q=1.0, actual 0.0, five rows) — v1 may have asserted the
temperature the config JSON specified while the meta records the
executed default (or the anchor binds the wrong run generation);
(ii) count rows (6/60 vs 4/40; 2 vs 4; 119 vs 125; 611 vs 609) —
at-era population vs current. Predicted: a mix of
SNAPSHOT-DIVERGENCE and AT-ERA DOC-DEFECT (v1's known wrongness may
extend beyond the model-name bug); at least the temperature sub-shape
suspected DEFECT-at-era or wrong-anchor. No prediction is offered per
row — the blind pass must resolve each at the March era.

**D (6 rows) — COMPARER ROUNDING SEMANTICS, not doc defects.** Five
rows sit exactly on the round-half boundary (0.0525 quoted '0.053';
0.0585 quoted '+0.059'): the document rounded half-up; the harness's
match-at-quoted-precision uses banker's/half-even. Predicted:
FALSE-MISMATCH — instrument-tolerance family; recommend a
`lib_c4_compare` half-up acceptance (instrument change, PI-visible,
not silent). The sixth (0.662 vs 0.66145) is NOT half-boundary;
predicted genuine small at-era discrepancy needing era resolution
(possible recompute-input drift).

**E (4 rows) — ORIENTATION TRANSPOSITION + one boundary.** 048#48:
the document states Flash-vs-Pro; the anchored artefact stores the
pair in the opposite orientation — |ΔF1| 0.028 and the 66/44
wins/losses agree exactly under transposition. Predicted:
extraction-side anchor-orientation (or doc-artefact order mismatch),
not a value defect. 048#59 (+0.021 vs 0.020485) — rounding boundary
adjacent; predicted at-era value ≥0.0205 or half-up rounding; needs
era resolution.

**F (11 rows) — SNAPSHOT-DIVERGENCE mostly, one doc-internal
inconsistency.** The session-58 appendix quotes at-era operating
points; recovery re-scores and re-materialisations moved third
decimals and the vote-threshold optimum (5→10). 049#13[0] (572 vs
569) is predicted an AT-ERA DOC-DEFECT: the document's own preamble
says 569 reference mounds while the appendix table header asserts
"% of 572" (the extractor flagged the internal inconsistency; the
2026-08-02 banner already notes a separate internal ΔF1
inconsistency in this document).

**G (3 rows) — three distinct stories.**

- 051#1[0] ('one' tier vs 2): the S113 signoff asserted the
  verifier-robustness rungs shared ONE tier; later tiering machinery
  (BH/BCa revisions) now yields 2. Predicted SNAPSHOT-DIVERGENCE with
  the BCa caveat in force (the 2026-04-30 percentile→BCa switch
  `2026999ad` means no pre-May CI-derived quantity reproduces —
  never book a CI-derived mismatch as a doc defect).
- 056#41[0] ('4 954' vs 1032): magnitude gap suggests WRONG-ANCHOR
  binding (a different pool aggregation), i.e. extraction-side
  repair, not a doc or artefact defect.
- 058#38[0] (26 vs 32, FDR pairwise family row count): HIGH
  materiality if real — the registered family must not grow after
  registration. Predicted alternatives: (i) the anchor counts a
  broader table than the registered subset the document means, or
  (ii) the family genuinely changed post-registration → escalate to
  PI immediately. No adjudication without the blind pass.

## Non-mismatch dispositions (proposed)

- **APPROX (2)**: 053-token-load-audit#12[1] (~$207.4 vs 207.3382)
  and #14[1] (~$195.4 vs 195.3499) — ACCEPT; well within their
  approx markers.
- **UNRESOLVED (463)**: structural classes, routed per standing
  practice — non-JSON anchors docs/studies/scripts/archive/tests/
  inputs (~276) to triage-scope; path-resolution failures (~117) and
  unparseable quotes (52) + non-numeric source values (13) to the
  repair queue; era1-phase3c and confirmatory locator failures (6) to
  the comparer/locator queue.
- **SKIPPED (1,314)**: anchor-unknown 681; recompute-script without
  registered runner 504 (runner tranches 2–3 — queue item (c) — will
  spec these; NAMED lines for GATE 3 per ruling 7); historical 116;
  external 11; unverifiable-era 2.
