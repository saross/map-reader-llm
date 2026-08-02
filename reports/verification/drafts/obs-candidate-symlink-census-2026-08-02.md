# Obs candidate (S125, for PI review): Obs 383's latent-exposure table is contaminated by a follow-symlinks census — the four experiment_intent rows are repo-reproducible after all

**Status**: DRAFT — held for Shawn's approval per the working-notes
convention (corrections to a landed Obs land as a NEW Obs
cross-referencing the old; Obs 383 itself is never edited).

## The finding

Obs 383's sub-example — "`outputs/**/experiment_intent.md` (184 live
files, 174 tracked) ... the 10 untracked files, all under
`outputs/55maps-text-min-n10-uplift/proposer-all/run_{1..10}/`, happen
to be present on both machines" and the derived "agreed by luck"
classification of rows `006#23[0]`, `#23[1]`, `#33[1]`, `#38[1]` — does
not reproduce on either machine with a symlink-consistent census:

- `find outputs -name experiment_intent.md | wc -l` = **174** on
  amd-tower AND on sapphire (both re-measured 2026-08-02, sapphire over
  read-only ssh), equal to `git ls-files` = 174. Zero intent files under
  `proposer-all` by `find`.
- `outputs/55maps-text-min-n10-uplift/proposer-all/run_{1..10}` are
  **symlinks** (created 2026-07-15): `run_10` →
  `../proposer/run_10` (same tree, already counted), `run_{1..9}` →
  `outputs/55maps-text-min-generalisation/proposer/detect_brief-text/run_N`
  (their intent files counted at their real paths).
- `find -L outputs -name experiment_intent.md | wc -l` = **184** — the
  "184 live files" was a follow-symlinks measurement; the "10 untracked
  files" are re-counts of tracked files through the links, not distinct
  untracked artefacts.

Consequence for Obs 383's table "repo-reproducibility of the matched
set (23 fully tracked / 6 partially / 1 zero)": the experiment_intent
spec belongs in the fully-tracked class, and the remaining
"partially tracked" classifications each need re-measuring with a
symlink-consistent method before the GATE 3 scope decision consumes
the table. Obs 383's CORE mechanism is unaffected and re-verified the
same day: pv-diag-384 counts 48,707 (amd-tower) vs 127,281 (sapphire),
and the `037#37[0]` crops verdict-flip (6 local / 0 sapphire) both
reproduce.

## Instrument corollary (implemented S125, same session)

`Path.glob` on Python 3.13 TRAVERSES directory symlinks, so the
glob-count census primitive was itself susceptible to the same
double-count. `scripts/lib_c4_runners.py::glob_entries` now excludes
symlink entries and entries reachable only through a symlinked
directory (find-consistent), with a tier-1 regression test
(`tests/test_lib_c4_runners.py::test_glob_count_ignores_dir_symlinks`).
Glob-count report rows are now stamped `census_total` /
`census_tracked` / `machine_scope` (Obs 383 guard 1, flag-not-decide),
and the recompute report `_meta` carries a `host` stamp (guard 3).

## Anchors

- symlink targets: `ls -la outputs/55maps-text-min-n10-uplift/proposer-all/`
  (mtime 2026-07-15)
- counts: re-measured 2026-08-02 on both hosts (this session's log);
  `find` vs `find -L` vs `git ls-files` as above
- Obs 383: `docs/notes/working-notes.md` (Session 124, 2026-08-02)
- harness changes: `scripts/lib_c4_runners.py::glob_entries`,
  `scripts/recompute_c4_claims.py::_census_scope`, commits this date
- wave-3 triage: `reports/verification/c4-triage/mismatch-triage-2026-08-02.json`
  (instrument_findings → symlink-census-method)
