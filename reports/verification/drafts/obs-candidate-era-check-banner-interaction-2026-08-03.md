# Obs candidate — the remedy resets the clock it feeds (era_check × banner policy)

**Status**: DRAFT for PI review (Session 126, 2026-08-03). Not an Obs
until approved; if approved, land via obs-writer with its blind
re-derivation pass per ruling 11.

**One-line**: The verification programme's own correction policy
(ruling-1 banners) rewrites a document's blob, which resets the era
that the era_check machinery (ruling 12/14) computes from that blob —
so the instrument that decides "faithful at its own era?" silently
loses the era the moment the document is bannered.

## The mechanism

`find_era_commit` (`scripts/recompute_c4_claims.py`) defines a
document's era as the newest commit still holding the extraction's
recorded blob. Ruling 1 prescribes append-only banners/riders on
exactly the dated-snapshot class where era matters most; every banner
rewrites the blob, so the computed era lands at the banner date, and
`era_check` degenerates into a restatement of the primary
current-tree comparison (`faithful: false` whenever the row
mismatches, regardless of what the document's true era held).

## Evidence (Session-126 wave 5; three independent blind passes)

- All 43 phase3a-audit rows resolved their "era" at `5d91c2a97a73`
  (2026-08-01, the banner commit) — the document's true eras are
  `adf95dbf9` (2026-05-03 body) and `d78601b62` (2026-05-06
  annotation). Manual re-resolution at the true eras: 42/43
  era-faithful, with the recovery-campaign closure exact (deltas sum
  to the audit's own 835).
- All batch-048/049 rows resolved at `a6f58d1b7604` (2026-08-02, the
  E72 banner commit) for claims authored 2026-03-26.
- Quantified corpus-wide by pass DE: 134 of 178 era_check rows report
  `actual_era` identical to `actual`, era commits clustering at
  2026-08-01/02. All 110 MISMATCH rows on the phase3a audit repo-wide
  carry the degenerate `faithful: false`, 67 of them in wave-3's
  batch 043.
- No adjudication is known to be contaminated: every triage wave has
  been blind-pass-driven, and the wave-5 passes re-resolved eras
  manually. The exposure is prospective (any consumer trusting the
  field), not retrospective.

## Why it generalises

A provenance instrument that keys era off *blob identity* inherits a
coupling to every policy that touches the file — including the
correction policy the instrument exists to support. Any repository
combining (a) append-only correction banners with (b)
blob-dated-snapshot semantics will reproduce this failure. The fix
family keys era off the *claim*, not the file: resolve over the
claim's own source lines (`git log -L`), select by verbatim-span
presence, or take the oldest commit holding the blob; and emit an
explicit `anchor-absent-at-era` status instead of `faithful: false`
when the era artefact never existed. The within-file multi-era case
(the phase3a audit's 2026-05-06 annotation vs its 2026-05-03 body)
falls out naturally under claim-level dating and is wrong under any
file-level scheme.

## Cross-references

- Wave-5 triage: `reports/verification/c4-triage/mismatch-triage-2026-08-03.json` (escalation W5-E1)
- Blind passes: `reports/verification/c4-triage/blind-passes/wave5-pass-{A,DE,FG}-2026-08-03.json`
- Ruling 12 (era_check, "provisional"), ruling 14 (two-axis rule), ruling 1 (banner policy): `reports/verification/phase3-rulings-2026-07-31.md`
- Kin observations: Obs 382 (machine decides the verdict), Obs 385 (measurement-method contamination) — same genus: the instrument's implicit frame (machine, measurement method, now the clock) doing undeclared work.
