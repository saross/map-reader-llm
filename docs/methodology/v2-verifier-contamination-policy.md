# v2-Verifier Contamination Policy

## What happened

The adversarial verifier prompt v2
(`prompts/system-instructions/verify_adversarial_v2.md`, 2026-04-14) was
written after inspecting false positives from the four-map gold-standard
(GS) set. The v2 revisions — a spot-height size criterion and a
water-feature colour exclusion — were derived directly from the QGIS
sanity-check of 2026-04-08, which itself operated on GS-set output.

Because the prompt was calibrated on the test set, any evaluation that
then uses v2 on the GS (or on a corpus that overlaps it) is circular.
Reported metrics would be optimistically biased. This is the standard
"calibration-on-test" failure mode, not a bug in any particular script.

## What is quarantined

Everything produced by running v2 over the 4 GS maps or a superset has
been moved to `archive/v2-verifier-contamination/`. The three sub-folders
are:

- `leaderboard-cells/` — 1 file (GS v2 greedy leaderboard cell)
- `e47-v1-vs-v2/` — 80 files (the whole prompt-development comparison
  directory; v1 and v2 halves are entangled as a unit)
- `raw-outputs/` — 19 files across 7 sub-directories of raw probabilities,
  run metadata, and post-processed GeoJSON

See `archive/v2-verifier-contamination/MANIFEST.md` for the full inventory
and `archive/v2-verifier-contamination/README.md` for a policy overview
written for future readers.

## What is still valid

- **Paper headline F1 = 0.904** uses verifier **v1**
  (`verify_adversarial.md`), confirmed via the run-metadata chain for the
  condition `flash-high-text-16-of-30--flash-min-vf`. The headline is not
  contaminated.
- **55-map generalisation v2 raw data** at
  `outputs/55maps-generalisation/verified-v2/` remains in place. The
  55-map student corpus is disjoint from the 4 GS maps, so v2 evaluation
  on it would be a legitimate out-of-sample test. Pending: student ground-
  truth labels.
- The v2 prompt file and config remain in place so the v2 pipeline can be
  re-run on an uncontaminated corpus without reconstruction.

## Future work

1. Obtain student GT labels for the 55-map corpus, then re-evaluate v2
   there. This will produce an honest out-of-sample v2 F1.
2. If a v1-vs-v2 comparison is still wanted for the paper, run both
   prompts on a fresh held-out set never inspected during prompt
   authoring. The archived e47-v1-vs-v2 comparison cannot serve this role.
3. Update `planning/condition-inventory.json`: the six `pv-*-v2` entries
   referring to `outputs/h11/proposer-verifier-384/verified-*-v2.geojson`
   are currently marked QUARANTINED but their underlying metadata shows
   v1 instruction files (the "v2" in the filename denotes a second
   verification pass, not the v2 prompt). Either re-label or verify
   contamination per case.

## Authorship

Contamination discovered during end-of-session review on 2026-04-20.
Quarantine action staged (not committed) on the same day pending human
review.
