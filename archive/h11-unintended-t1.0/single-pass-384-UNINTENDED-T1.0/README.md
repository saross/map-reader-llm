# single-pass-384-UNINTENDED-T1.0 — E44 deviation data (serendipitous Era 2 T=1.0 coverage)

## Origin (protocol deviation)

This directory contains 10 single-pass runs at 384 px tile size
(`384/run_{1..10}/`, with re-clipping to 512 px bounds under
`384-clipped-to-512/run_{1..10}/`) that were inadvertently executed at
temperature T=1.0 when the T=0.0 deterministic baseline was intended.
The root cause was the same config propagation failure documented for
`consensus-384-UNINTENDED-T1.0/`: the `detect_brief-text.json` prompt
config has `"temperature": 1.0` hardcoded, and the YAML-specified
`fixed.temperature: 0.0` / `carried_forward.optimal_temperature: 0.0`
was not propagated to the API call. Discovered during the comprehensive
configuration audit (Session 57, 2026-03-25). Root cause and full
disposition are documented in `docs/methodology/preregistration/protocol-errata.md`
§E44. The corrected T=0.0 single-pass rerun (487 tiles, matching the
full evaluation area) is at `outputs/retest/h11-single-pass-384-t0/`.

## Status — retained for Era 2 / 487-tile-scope T=1.0 coverage

**Authoritative scientific evidence for the T=1.0 temperature finding is
`outputs/retest/phase2b/{track1-image,track2-text}/T1.0/` (Era 1, 340
tiles × 3 runs × 2 tracks, preregistered H7 temperature sweep).** This
directory must not be cited as primary evidence for the temperature
finding — the paper rests on the Phase 2b sweep.

This directory's legitimate use is 487-tile / Era 2-scope T=1.0
single-pass coverage where Phase 2b does not extend — specifically the
full-corpus leaderboard rows in `results/paper-eval/` and pairwise
tests in `results/pairwise/leaderboard-20m/group_8/` (the single-pass
companion to the consensus-384-UNINTENDED-T1.0 rows). It is retained
rather than archived because (a) it fills a scope gap the preregistered
design does not cover, and (b) downstream artefacts already reference
it for this legitimate purpose.

## Provenance signals in the filesystem

- Directory name retains the `-UNINTENDED-` label as a permanent
  origin-of-data signal; do not rename.
- `results/ci-metadata-registry.md` records the provenance line
  "UNINTENDED (protocol deviation); kept for provenance".
- Working-notes (`docs/notes/reflections/working-notes.md`) line 6069+
  distinguishes the preregistered Phase 2b T=1.0 narrative from this
  deviation data. Any paper text that cites this directory must maintain
  that distinction.
- Per project policy: archive, never delete. The data's dual-role
  retention (serendipitous Era 2 T=1.0 scope coverage) is precisely the
  "unexpected data as discovery" heuristic in `CLAUDE.md`.
