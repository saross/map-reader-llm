# ci_unreliable migration to the measured rule

> **Last revised**: 2026-08-20 (original publication). See
> [§ Changelog](#changelog) for revision history.

**What this is.** The execution record for defect **D28** (Session 137 audit,
finding F4): Session 137 retired the sparse-coverage heuristic behind
`ci_unreliable` in code (`6f8e31f97`) but re-emitted no artefact, so the
register kept publishing 1,041 stale `true` flags — 91 of 337 conditions at the
20 m headline buffer, the paper's gold-standard cell included — for a pathology
the session's own measurement showed never occurs, with no vintage marker
anywhere. The Principal Investigator ruled on 2026-08-20 for full migration.
Machine-readable inventory: `reports/ci-flag-migration-2026-08-20.json`.

## What was done

`scripts/migrate_ci_flag_basis.py --write` recomputed the flag for every
git-tracked `*evaluation.json` outside `archive/**` (excluded to match erratum
E82's re-emission scope — archived artefacts are historical snapshots), from
each row's **own committed fields**: measured CI-excludes-point on
f1/precision/recall, or E72 partial coverage. Every row now carries
`ci_excludes_point`, `ci_flag_basis`, and (where coverage is recorded) the
descriptive `sparse_coverage`. All `ci_unreliable_any_buffer` rollups were
recomputed. The manifest generator now copies `ci_flag_basis` (schema
extended first, per the D18 lesson), and the two Track-2 adapters compute the
measured rule instead of writing a `False` literal. Manifests regenerated.

## The numbers

| Quantity | Value |
|---|---:|
| Tracked evaluations in scope | 1,723 (archive/** excluded: 30) |
| Files changed | 1,710 |
| Buffer rows touched | 25,438 |
| Flag flips (true → false) | 3,021 |
| Rows still flagged, and truthfully | 16 |
| Register flagged rows | 1,041 → **0** of 4,299 |
| Register flagged conditions at 20 m | 91 → **0** of 337 |
| Register rows carrying a basis | 4,299 of 4,299 (4,075 full rule, 224 exclusion-only) |

The migration is idempotent: a second `--dry-run` reports zero changes.

## The 16 rows that stay flagged — a finding, not residue

All 16 sit in `results/pairwise/tile-size-30m/**` (5 files), and each is a
**measured exclusion**: the committed CI genuinely excludes its own point
estimate — the exact D15 axis-defect signature (intervals rescaled by
`sqrt(n/B)`) surviving in committed artefacts that were never re-emitted.
The family is cited by **no** register condition and **no** analysis row
(verified by grep over both manifests), so no published claim rests on it.
Under the measured rule the flag on these rows is now *true and meaningful*:
any future use of this family will meet an honest warning and should trigger
re-emission at B = 10,000 first.

## Semantics after this migration

- `ci_unreliable: true` now means, everywhere outside `archive/**`: *the
  interval excludes its own point estimate, or coverage is partial (E72)*.
- `ci_flag_basis: "measured-exclusion-or-partial-coverage"` — both grounds
  were evaluable. `"measured-exclusion-only"` — the row carries no coverage
  status (adapter-written cells), so the E72 ground could not be evaluated.
- Sparseness is still visible (`sparse_coverage`, `coverage.zero_fraction`)
  as a fact for the reader, not a reliability verdict.
- `archive/**` evaluations keep the superseded flag and no basis key — absence
  of `ci_flag_basis` marks the old convention, as the code comment in
  `evaluate_detections.py` documents.

## Changelog

### 2026-08-20 — Original publication

Written with the migration itself (Session 138, audit remediation Phase 2,
$0 API, zbook). Tier-1 suite green after migration and regeneration.
