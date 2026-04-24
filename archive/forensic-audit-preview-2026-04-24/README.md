# Forensic-audit preview — gold-standard text-HIGH @ Era 2 (retracted)

**Archived**: 2026-04-24 (Session 78)
**Origin**: Session 77 forensic audit of the "250-feature anomaly" in the gold-standard-v2 text-HIGH extended-buffer sweep.

## What this is

The `gold-standard-text-high-extended-buffer-sweep-era2/` sub-directory
contains a Session 77 *preview* evaluation of the 250-feature Era-3-
bounds-filtered detection file against Era 2 bounds (487 tiles). The
headline numbers it reports are:

| Buffer | F1 | P | R | n_detections |
|---|---|---|---|---|
| 20 m | 0.677 [0.617, 0.732] | 0.928 | 0.533 | 250 |
| 50 m | 0.686 [0.625, 0.741] | 0.940 | 0.540 | 250 |

## Why it is archived (not in `results/`)

This is **not** the Era 2 companion of the gold-standard v2 text-HIGH
evaluation. It is a diagnostic artefact produced while investigating
the "250-feature anomaly" — a case where `score_leaderboard_cells.py`
had silently `tile_allowlist`-filtered the detection manifest to the
Era 3 327-tile pool, leaving the resulting GeoJSON with zero
detections in pool_160 (116 additional Era 2 GT mounds had no
corresponding detections, tanking recall by construction). The
0.677/0.686 F1 numbers therefore measure the 250-feature bounds-
mismatched set against a larger GT denominator — they are an artefact
of the silent-filter bug (Obs 276), not a real scope comparison.

The forensic audit extrapolated from this preview to predict F1 ≈
0.722 at 20 m / 0.736 at 50 m for the *unfiltered* 371-feature set at
Era 2, assuming the 121 pool_160 detections would contribute roughly
average precision. That prediction was superseded by the actual Q1
run in Session 78, which gave F1 = 0.854 [0.821, 0.883] at 20 m / F1 =
0.873 [0.844, 0.901] at 50 m. The prediction is retracted.

## Authoritative Era 2 companion

For the actual gold-standard v2 text-HIGH Era 2 evaluation, see:

- `results/gold-standard-extended-buffer-sweep-era2/` (371 detections;
  F1 = 0.854/0.873 @ 20/50 m; MCC = 0.778).

For the matched Era 3 (327-tile) sibling, intentionally preserved for
comparability with h8-v2 / h10-v2 / h12-v2 library-design artefacts:

- `results/gold-standard-extended-buffer-sweep/with-mcc/` (250
  detections; F1 = 0.8155/0.826 @ 20/50 m).

## References

- Obs 276 (silent `tile_allowlist` filter in
  `score_leaderboard_cells.py`) — `docs/notes/reflections/working-notes.md`.
- `planning/paper-writeup-continuity.md` §"Session 78 entry-point
  queue" → Q1 for the retraction note.
- Script-hygiene backlog entry in the same continuity doc (added
  Session 78).
