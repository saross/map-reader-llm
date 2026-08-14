# Session 133 analysis block — ink-colour adhesion test + D-S report refresh

> **Status**: APPROVED — PI go given in-session 2026-08-15 AEST after a
> `/pre-run-review` dialogue (the S131 protocol). US$0.00 API budget —
> any spend is a hard stop. This document is the block's controlling
> document per the pre-run-review exit requirements.

## Scope

Two independent, simultaneous-safe, $0 items:

1. **Obs 407 ink-colour adhesion test** — does displacement behaviour
   in the marking data sort by attractor ink colour?
   Input: `results/deployment-oracle-2026-06-06/canonical-gt/marked-centres.csv`
   (1,317 records; 1,276 with displacement).
2. **D-S report refresh** — move
   `results/55maps-ds-summary-v2/report.md` §§ 4.1/4.3/5.3/5.4 (and
   banner) from per-run-vintage corrected-F1 figures onto the
   standardised reference
   (`results/55maps-standardised-ref-2026-08-14/consolidated-standardised.csv`),
   re-examining the Obs 293 middle-pair swap. Discharges the S131
   carry-forward ("§§ 4.1/4.3/5.3/5.4 … then re-examine the
   middle-pair swap") and the stale banner flagged at S133 open.

## Hardenings recorded from the review dialogue

1. **Item 1 operationalisation (PI-approved)**: a symbol-class
   contrast, not a full vector-field attribution. Colour classes from
   `symbol_type`: black-element = {bench_mark_on_mound,
   trig_point_on_mound} (230 records); plain = {burial_mound,
   settlement_mound} (1,042). Per source layer (corrected_student 543
   / promoted_phantom 773), seeded permutation tests (10,000 perms,
   seed 42) on displacement magnitude; jitter_sample records (100)
   reported as the PI's marking-noise floor. Compute on sapphire.
2. **Named confound (item 1)**: compound-symbol mounds are surveyed
   geodetic points — plausibly larger and better-mapped, so smaller
   displacement for non-colour reasons. The finding is reported as
   exploratory, consistent-with (never proof-of) colour adhesion.
3. **Data-semantics gate (item 1)**: before computing, profile
   `item_type` semantics (jitter_sample, merge_site, student_pair,
   student_conflation) and record every inclusion/exclusion decision
   in the findings doc BEFORE looking at contrast outcomes
   (registration-before-compute). Excluded a priori: not_a_mound (45),
   extra_point (1), skipped records.
4. **Cell↔run mapping gate (item 2)**: the report's current figures
   (0.8437 / 0.8273 / 0.8333 / 0.7968) come from per-run
   `corrected-f1-multi-buffer/summary.json` files and match neither
   the legacy canonical board nor the standardised one — a two-step
   vintage jump the changelog must state explicitly. Before editing
   prose: read each run's summary provenance, confirm the operating
   point maps to board cells {T03-k4, TH7-k4, IM-k3, TM-k4}, and
   feature-count crosscheck per cell (the Session 77 lesson).
5. **One-commit rule (item 2)**: figures, ranking prose, banner, and
   changelog entry (with before→after table) move in a single commit.
6. **Verifier conditions (both items)**: blind fresh-context
   verification with (a) denominator reported (claims identified /
   re-derived / confirmed / corrections), (b) disagreement rule — a
   conflicting correction triggers a third derivation from the data,
   never verifier-wins, (c) answer-shaped questions asked cold (rank
   the four runs from the CSV; derive the contrast statistics from
   marked-centres.csv) and diffed against prose.
7. **Registry refresh at close**: item 1 mints new generated files;
   `build_generated_file_registry.py` re-runs in the block's closing
   commit so `--check` stays green.
8. **Expected-result band (item 2)**: on the standardised reference
   the corrected-F1@50m order becomes T=0.3 (0.8303) > T=0.7 (0.8169)
   > Image (0.8010) > text-MIN (0.7833) — the middle-pair swap
   dissolves (it is already absent on the legacy common reference, so
   it was a per-run-vintage artefact). Any movement beyond this
   grounded expectation is a stop-and-escalate surprise.

## Stop states

- Any API spend ($0 budget) — hard stop.
- Gate failure (mapping/crosscheck/semantics) — stop, never
  substitute a near-enough source.
- Surprising result outside § Hardenings 8 — verify pipeline, then
  escalate to the PI.
- sapphire unreachable — stop and report; no silent local fallback.

## Parked items (PI, 2026-08-15)

- **Vector-extension project**: the stronger directional test of
  colour adhesion — extract black-feature locations from the map
  sheets and test displacement *bearings* toward same-colour
  attractors. A future project, not this $0 analysis.
- **Higher-temperature road for MCC exploration** — considered, NOT
  now. Context: E60 closed the F1 escalation (curve declining), but
  tile-MCC rises monotonically through the highest tested rungs
  (Phase 2b characterised MCC through T=1.3, still rising — Obs 274;
  the E43 ladder replicates through T=1.0), so the MCC upper bound
  (T=1.6/2.0) is genuinely uncharacterised. Design cautions if ever
  revived: higher T raises zero-detection/malformed-JSON rates and
  recovery costs (Obs 319; session-log S1954 zero-detection
  concentration at T1.0/T1.3); GS-at-k3 lacks power for temperature
  questions (Obs 366) — design on consensus depth ≥5 or the 55-map
  corpus; frame as exploratory tile-triage (MCC), not a revisit of
  the settled F1 question. API-gated.

## Changelog

### 2026-08-15 — Original publication

Block plan authored from the S133 pre-run-review dialogue; PI go
recorded. Items not yet executed at time of writing.
