# v2-Verifier Contamination Quarantine

**Status**: quarantined, not deleted. These files are preserved for audit,
reproduction, and potential re-evaluation on an out-of-sample corpus.

## Why this directory exists

The verifier prompt `prompts/system-instructions/verify_adversarial_v2.md`
(created 2026-04-14) was written by inspecting false positives from the
four-map gold-standard (GS) set. Specifically, the v2 prompt added:

- A spot-height size criterion (about 5-7 px versus at least 12 px for
  mounds), derived after the QGIS sanity check on 2026-04-08 identified
  spot heights as the dominant addressable false-positive class on the GS
  set.
- A water-feature colour exclusion (blue circles or concentric rings are
  never mounds), derived from the same GS false-positive analysis.

Because the prompt was **calibrated on** the gold standard, any evaluation
that then uses v2 **on** the gold standard (or on a corpus that overlaps
it) is circular: the held-out set is no longer held out. Reported metrics
would be optimistically biased.

This is the classic "calibration on the test set" failure. The contamination
applies to any file produced by running the v2 verifier over the 4 GS maps
(K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1) or any superset of those
tiles.

## What is in here

Three sub-folders, all products of v2-on-GS evaluation:

- `leaderboard-cells/` — gold-standard v2 leaderboard cell files.
- `e47-v1-vs-v2/` — the entire prompt-development comparison study. Both v1
  and v2 halves are archived together because the v1 arm was the control
  for v2 and the two are methodologically entangled as a unit.
- `raw-outputs/` — raw probabilities, run metadata, and post-processed
  GeoJSON from every v2 verifier run on the GS corpus or a superset.

See `MANIFEST.md` for the complete inventory with original paths and
per-file contamination type.

## What is still valid

- **Paper headline F1 = 0.904** (condition
  `flash-high-text-16-of-30--flash-min-vf`, 30 m buffer) uses verifier
  **v1** (`verify_adversarial.md`). Confirmed via `run.meta.json` in
  `outputs/h11/pv-diag-384/verified/flash-high-text-1of30/` — the source of
  the 16-of-30 derived file. The headline is not contaminated.
- **55-map generalisation v2 raw data** at
  `outputs/55maps-generalisation/verified-v2/` remains in place. Its corpus
  (55 Soviet topographic sheets) is disjoint from the 4 GS maps, so it is
  a legitimate out-of-sample target for a v2 evaluation — pending student
  ground-truth labels.
- The v2 prompt file and its config (`prompts/system-instructions/verify_adversarial_v2.md`,
  `prompts/configs/verify_adversarial-text_v2.json`) remain in place.

## How to re-evaluate v2 honestly

To produce an unbiased v2 F1 estimate, re-run v2 verification on a corpus
that was **not** used to derive the prompt. Two options:

1. **55-map student corpus** — candidate set already exists at
   `outputs/55maps-generalisation/verified-v2/`. Blocker: student GT labels.
2. **Fresh out-of-sample maps** — identify new sheets not seen by the
   prompt author and re-run the full pipeline.

A legitimate v1-vs-v2 comparison requires both prompts evaluated on the
same held-out corpus, with the held-out corpus never inspected during
prompt authoring.

## Why quarantine rather than delete

- Reproducibility: the contaminated runs cost API calls and compute.
  Preserving them lets future analysts audit the contamination claim and
  compare v1-vs-v2 behaviour on GS (useful as a diagnostic of the
  calibration effect, even if invalid as a headline metric).
- Repository policy: `CLAUDE.md` mandates "archive, never delete" for any
  files removed from the active tree.
- Discovery opportunity: see `CLAUDE.md` section "Unexpected Data as
  Discovery Opportunities" — preserved unexpected data has repeatedly
  produced insight in this project.

## Cross-references

- Policy note: `docs/methodology/v2-verifier-contamination-policy.md`
- Inventory: entries marked `"status": "QUARANTINED"` in
  `planning/condition-inventory.json`
- v1 prompt (clean): `prompts/system-instructions/verify_adversarial.md`
- v2 prompt (contamination source): `prompts/system-instructions/verify_adversarial_v2.md`

## Contact

If you are a future researcher opening this directory, you can reconstruct
the history by reading:

1. `MANIFEST.md` in this directory (what was moved where, and why).
2. `docs/methodology/v2-verifier-contamination-policy.md` (policy statement).
3. `docs/notes/reflections/working-notes.md` (research log).
4. Git log for the commit that created this quarantine.
