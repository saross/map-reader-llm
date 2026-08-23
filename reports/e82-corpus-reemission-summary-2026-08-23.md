# E82 corpus re-emission — campaign summary

> **Last revised**: 2026-08-23 (original publication; written at campaign
> close from the report JSON, after operator sign-off). See
> [§ Changelog](#changelog) for revision history.

**What happened.** Every Bias-Corrected and accelerated (BCa)-era committed
evaluation — 1,655 files selected by metadata vintage — was replayed at
B = 10,000 through the fixed bootstrap wrapper (`122104b8a`) and re-emitted
at metadata 1.3, correcting the D15 axis defect's interval widths corpus-wide
(erratum E82). Contract: `planning/e82-corpus-reemission-2026-08-20.md`.
Machine-readable record: `results/e82-corpus-reemission-2026-08-20.json`
(every number below cites it). Zero API spend; all scoring on sapphire.
**Operator sign-off: Principal Investigator, 2026-08-23.**

## The six legs

| Leg | Date | ok | failed | pinned | reagg | order | median |
|---|---|---|---|---|---|---|---|
| Pilot 1 (seeded + forced) | 2026-08-20 | 13 | 2 | (pre-counter) | — | — | 4.92 |
| Pilot 2 (post vintage-search) | 2026-08-20 | 14 | 0 | (pre-counter) | — | — | 5.31 |
| Full leg 1 (S138) | 2026-08-20/21 | 204 | 19 | 8 | — | — | 4.43 |
| Full leg 2 (S139, resumed) | 2026-08-21/22 | 588 | 7 | 21 | 18 | — | 4.66 |
| Full leg 3 (S140) | 2026-08-22/23 | 832 | 4 | 6 | 1 | 2 | 5.27 |
| Clearing leg (S140) | 2026-08-23 | 4 | 0 | 0 | 0 | 4 | 4.70 |

Final engine census: **selected = 0, done = 1,657** (the 1,655-file worklist
plus two pre-campaign 1.3 cells), other-vintage = 42 (out of scope by
construction), no-recipe skips = 13 (frozen and named in the report),
non-canonical basenames excluded = 12; 1,724 tracked evaluations — the
arithmetic is exact. Width-ratio medians per full leg all sit inside the
[1.05, 6] band and track `sqrt(B/n)` for the small-scope majority. Two
`no_ci` cells recorded (degenerate: one with zero detections; one with
n = 2 whose committed intervals all had width exactly 0).

## Failure accounting — 32 events, all attributed

- **2 × input-vintage drift (D40)**, pilot leg: cells scored against inputs
  committed minutes after scoring. Both re-emitted via the bounded
  adjacent-vintage search, pins recorded in `_metadata.e82_input_vintage`.
- **20 × D41 mis-aggregation** (19 first-pass + 1 rounding-boundary
  re-fail): summary tile points that had committed run 1's value instead of
  the defined-pass mean. All 19 re-emitted with corrected summaries;
  the corpus-wide signature scan confirmed the population is exactly 19
  (`reports/e82-d41-widening-inspection-2026-08-22.md`).
- **10 × pass-order replay infidelity** (6 + 4 re-fails): the original
  batch glob consumed passes lexicographically, the canonical resolver
  replays numerically, and at >= 10 runs the per-run blocks permute. The
  gate corrections (per-run comparison keyed by run label; the
  re-aggregation helper aligned to the writer's exact
  `round(float(np.mean), 4)`; buffer-table order artefacts forgiven only
  under strict reproduction conditions) loosened no measurement tolerance —
  PI ruling C1 + D (2026-08-22), buffer-mean extension ratified 2026-08-23.
  Full mechanism history: Obs 426.

Cumulative counters land exactly on the ruling's expected values:
**n_reaggregated = 19, n_order_normalised = 6.** Vintage-pinned
re-emissions: **35** recorded by the counter (the data commit `43ea31b26`
says 27 — a conflation with the 27 distinct ever-failed cells; 35 is
correct). Eight summary values moved by one 4 dp step (seven buffer points,
one tile MCC) as enumerated order artefacts; **no other point estimate moved
anywhere** (1e-9 gate on every accepted attempt).

## What changed for consumers

- **Interval widths**: corrected throughout — wider where `B > n` (the
  dominant regime), per the `sqrt(B/n)` model. No hypothesis verdict or
  tie-set membership depends on these per-cell intervals.
- **Reliability flags**: 1,134 buffer rows now carry `ci_unreliable = true`
  on *measured* `partial_coverage` where pre-campaign artefacts held an
  unmeasured "normal" default. All 1,134 trace to that single mechanism;
  no flag anywhere was lowered. Tables reading the flags will count fewer
  "reliable" cells.
- **Manifests**: regenerated, ALL VALID (33 runs / 338 conditions /
  1,138 passes / 38 analyses — the 338th being the genuine IM-k4 cell
  registered the same day, outside this campaign's scope).

## Emergent repairs and the new defect

1. **D42 (new)**: the writer does not emit `ci_flag_basis` /
   `ci_excludes_point`, so re-scoring regressed the 2026-08-20 measured-flag
   migration on 169 files (values untouched). Migration re-applied
   (`e46f13bba`); standing mitigation: re-run it after any re-score
   campaign until the writer stamps the fields natively.
2. **Recorded output_dir**: every replay recorded its temp workdir; engine
   now normalises to the cell's own directory and all 1,655 files were
   repaired one field each (`70c550177`), with a regression test.

## Verification state at close

Tier-1 1,895 and tier-2 27 green on the workstation; tier-1 1,892-equivalent
green on sapphire (its venv required two committed dependencies installed —
all three machines subsequently synced to `requirements.txt` in full). The
three campaign dry-runs report zero; the engine dry-run reads
selected = 0 / no_recipe = 13.

## Changelog

### 2026-08-23 — Original publication

Written at campaign close (Session 140) from
`results/e82-corpus-reemission-2026-08-20.json`, after operator sign-off.
Companion updates in the same block: the E82 corpus execution note
(`docs/methodology/preregistration/protocol-errata.md`), defect register
rows D15/D19/D41 closed and D42 opened, and the contract changelog closed
(`planning/e82-corpus-reemission-2026-08-20.md`).
