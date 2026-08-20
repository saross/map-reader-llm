# Superseded leaderboard family

Archived 2026-08-20 (PI ruling, Session 138; E82 campaign item B). This is the
legacy `results/leaderboard/**` family — tier boards, per-architecture views,
cells, and enrichment rows generated around 2026-05-06 — retired in favour of
`results/metric-leaderboards/**` (the paper-facing family) and the register's
Hsu-MCB tie sets (erratum E83).

Archived with KNOWN DEFECTS, deliberately preserved as-is per the
archive-never-delete policy (Session 137 audit, findings F6/F10/F11; defect
register D30/D34/D35):

- The three `combined/*/leaderboard_tiers_mcc.json` boards are RANKED on the
  bootstrap-resample mean, not the observed MCC; re-ranking on the observed
  point changes 18/86, 9/87, and 2/14 position occupants respectively.
- 56 per-architecture `_mcc*` boards carry pre-migration CI columns.
- 18 interval blocks under `combined/era2/` predate the B = 10,000
  restandardisation.
- All tiering is the superseded greedy-clique instrument (pre-E83).
- The era2 buffer boards carry a declared hand-edit row
  (`gold-standard-v2-greedy-v1-487`), refreshed 2026-08-20 to current point
  estimates before archival.

Nothing in the paper, the conditions manifest, or the analyses register cites
this family (verified 2026-08-20). Everything here is regenerable from
committed data; regenerate fresh on current instruments rather than reviving
these artefacts.
