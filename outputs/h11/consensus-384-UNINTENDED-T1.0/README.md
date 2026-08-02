# consensus-384-UNINTENDED-T1.0 — E43 deviation data (serendipitous T=1.0 data — 240-tile scope; see E72 for the coverage caveat on any 487-bounds comparison)

## Origin (protocol deviation)

This directory contains 30 consensus-pipeline runs at **240-tile scope**
(the 384 px re-projection of the Era-1 validation split — this README
previously said 487-tile, which was never true of the runs; corrected
2026-08-02 per E43's correction block and E72) that
were inadvertently executed at temperature T=1.0 when T=0.7 was intended.
The root cause was a config propagation failure: the `detect_brief-text.json`
prompt config has `"temperature": 1.0` hardcoded, and `run_phase2.py` used
the config's default instead of the YAML-specified `fixed.temperature: 0.7`.
Discovered during the comprehensive configuration audit (Session 57,
2026-03-25). Root cause and full disposition are documented in
`docs/methodology/preregistration/protocol-errata.md` §E43. The intended
T=0.7 baseline was re-run separately at
`outputs/retest/h11-single-pass-384-t0/` (and the corrected T=0.7
consensus baseline lives at `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/`).

## Status — retained for Era 2 / 487-tile-scope T=1.0 coverage

**Authoritative scientific evidence for the T=1.0 temperature finding is
`outputs/retest/phase2b/{track1-image,track2-text}/T1.0/` (Era 1, 340
tiles × 3 runs × 2 tracks, preregistered H7 temperature sweep).** This
directory must not be cited as primary evidence for the temperature
finding — the paper rests on the Phase 2b sweep.

This directory's legitimate use is 487-tile / Era 2-scope T=1.0 coverage
where Phase 2b does not extend — specifically the full-corpus leaderboard
rows in `results/paper-eval/` and pairwise tests in
`results/pairwise/leaderboard-20m/group_8/`. It is retained rather than
archived because (a) it fills a scope gap the preregistered design does
not cover, and (b) ~157 downstream artefacts already reference it for
this legitimate purpose.

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
