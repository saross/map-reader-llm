# C1 adjudication record — 2026-07-29

**Adjudicator**: Claude Fable 5 interactive session (per charter § 8
executor assignment). **Inputs**: eight fresh-context reconstruct-and-diff
verifier reports (Opus 5; recon written before ledger access, per charter
§ 5 rules 2 and 11). **Outcome**: ledger v1.0 (696 rows) → v1.1 (702
rows). **Verifier tally**: 5 missed obligations, 16 disputes; every
ruling below names its verifier (v1–v8).

## Misses — all five accepted, rows added

| New row | Source | Ruling |
|---|---|---|
| CMT-0697 | prereg 317–321 | § 3.8 non-circularity constraint: decision statistic for every hypothesis except H3 is the **unvoted** run distribution (v2). **GATE 1 FLAG**: in tension with the project's greedy-consensus primary aggregation practice (cf. E52) — PI adjudication required. |
| CMT-0698 | prereg 759 | H8 "Hard Examples = HP + HN combined" terminology row (v4); the unit the scaling arm is indexed on. |
| CMT-0699 | prereg 1156 | H5 Stage-2 advancement is a three-conjunct rule; the interaction-non-significance conjunct had no row (v6). Five-element trigger block added, with ABSENT markers for the unoperationalised recall-stability criterion. |
| CMT-0700 | prereg 1152 | H1 advancement admits "or interaction" as an alternative sufficient condition, absent from CMT-0110 (v6). |
| CMT-0701 | coverage 258 | The changelog's "bootstrap CI + FDR throughout" is the coverage document's only statement of CI method and multiplicity correction (v8). |

Plus CMT-0702 (prereg 410): H1 umbrella test row added for convention
consistency (v3 dispute D5, accepted as an addition).

## Disputes — rulings

**Accepted, applied**: CMT-0113, CMT-0525, CMT-0617 retyped
factor→condition (scoping/execution rules, not level definitions);
CMT-0203 and CMT-0257 retyped disclosure→trigger with five-element blocks
(quantitative conditionals creating obligations); CMT-0101, CMT-0167,
CMT-0264 obligations reworded to track the lodged text (0167 had *added*
a verbatim requirement the source never states; 0264 would have
false-flagged the registered H14/H15 deferrals); CMT-0626, CMT-0631
uncertainty fields corrected against coverage line 258; CMT-0152
committed-block note narrowed to 556–560; CMT-0503↔CMT-0307 mutual
adjudication flags (contradictory H11 trigger directions — a
lodged-document defect, both rows faithful); CMT-0530/0539 notes now
name the hard temporal gate on the OSF upload undertaking.

**Rejected**: v3 D4 (split CMT-0159 into per-contrast rows) — both
contrasts share source line 571; single-line bundling is within grain
rules. Asymmetry with H1's per-contrast rows noted on the row.

**Resolved as convention** (v7 D12, design-wide): pure phase-carry-forward
selection rules ("use the X-optimal from phase Y") are `condition` rows;
carry-forward rules with an outcome-conditional branch ("…or default if
no significant effect") are `trigger` rows. CMT-0586/0587 (conditional
fallbacks) correctly carry trigger blocks; CMT-0537/0563/0565/0569 (pure
carry-forwards) correctly do not. No retypes. Convention added to the
extraction instructions v1.1.

**Partial**: v7 D13 — the OSF pre-holdout upload undertaking stays
`analysis` (the schema's reporting-obligation reading) rather than
`disclosure`; the temporal gate is now explicit in notes.

## Source-document findings carried to GATE 1

These are properties of the lodged text, not extraction defects: the two
incompatible Stage-2 gate formulations (v2); two-tailed power calculation
vs one-tailed default (v2); contradictory H11 trigger directions
(v6/CMT-0503); two different blocks headed "Tier C" (v5); transposed
hard-example thresholds between prereg and appendix, and the ≥3/10
count impossible from a 5-pass baseline (v7, matching extraction notes);
CMT-0463's unexplained ×5 in the 3,000-calls-per-cell arithmetic
underlying the ~$286 budget (v6); the stale v4.6 header at line 2388
(v6 — independently rediscovering the queued erratum).

## Session process notes

Two commit messages this session carried unverified counts, both wrong,
both corrected in-thread (526edfda9: "295" for 213; 2f5a9ae2d:
"560/55/81" for 515/81/100). Committed artefacts are authoritative.
Lesson recorded in the project scratchpad: numbers in commit messages
are checkable claims — compute them in the writing turn or omit.
