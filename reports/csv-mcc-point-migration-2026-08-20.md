# Tile-metric migration: resample mean to observed point

> **Last revised**: 2026-08-20 (original publication). See
> [§ Changelog](#changelog) for revision history.

**What this is.** The execution record for defect **D30** (Session 137
audit, finding F6): the evaluation JSONs keep the observed tile statistic
(`point`) and the bootstrap resample mean (`mean`) apart, but the CSV and
Markdown writers in `scripts/evaluate_detections.py` published `mean`
under the bare column names `mcc`, `sensitivity`, and `specificity`. Every
committed `evaluation.csv`, `batch_summary.csv`, and `evaluation.md` in
the corpus therefore carried a resample artefact under a header naming the
statistic itself. The signature is in the record: in the D17 commit
(`60f83e571`) those three columns moved while F1, precision, and recall
held to the digit — a bootstrap mean is not invariant to iteration count
and an observed statistic is. The Principal Investigator ruled on
2026-08-20 for full migration. Machine-readable inventory:
`reports/csv-mcc-point-migration-2026-08-20.json`.

## What was done

`scripts/migrate_csv_mcc_point.py --write` rewrote the three metric cells
of every git-tracked `evaluation.csv`, `batch_summary.csv`, and
`evaluation.md` outside `archive/**` (excluded to match erratum E82's
re-emission scope, as in the Phase 2 `ci_unreliable` migration), taking
the value from each file's **own** committed evaluation JSON:
`tile_classification.<metric>.point` where the block carries a `point`
key, or — for the 47 evaluations whose blocks predate that key — the value
recomputed from that block's own committed `confusion` counts.

The replacement is surgical. No header was rewritten, no column added, no
other cell touched: each CSV is parsed and re-serialised through a
round-trip that must reproduce the original bytes before any edit is
applied, and each Markdown row is rebuilt from its own `split("|")` fields
so pipes and padding survive. An undefined metric stays an empty CSV cell
and the word `undefined` in Markdown — never `0` (erratum E81).

The writers were fixed first, so nothing regenerates the defect: the bare
names now carry the observed statistic, and three new columns
(`mcc_boot_mean`, `sensitivity_boot_mean`, `specificity_boot_mean`) carry
the resample means in **future** files. Existing files did not gain those
columns — adding one is not a value replacement, and the means remain in
the JSON.

## The numbers

| Quantity | Value |
|---|---:|
| Files scanned (CSV + MD, `archive/**` excluded) | 3,397 |
| Files changed | 2,165 |
| — `evaluation.csv` | 1,487 |
| — `evaluation.md` | 676 |
| — `batch_summary.csv` | 2 |
| Metric cells changed | 51,792 |
| Files with no tile-metric columns at all (no-ops) | 317 |
| Files skipped by the safety gate | 2 |
| Evaluations whose point was recomputed from `confusion` | 47 |
| Max abs(mean − point) across the corpus | 0.0467 |
| CSV cells where abs(mean − point) > 0.001 | 494 |

The largest single movement is specificity in
`results/paper-eval/mcc/512px/p2a-verbose-text-image/`: the committed
matrix is tp 204, tn 13, fp 123, fn 0, so the observed specificity is
13/136 = 0.0956 while the published resample mean was 0.1350. Its MCC
moved 0.2909 → 0.2442 by the same mechanism — a tiny negative class makes
the bootstrap distribution of a bounded ratio strongly biased relative to
the observed value.

The migration is idempotent: a second `--dry-run` reports zero changes.

## Verification

* **Corpus-wide byte check.** Every one of the 2,165 changed files was
  compared against its `HEAD` content field by field: 42,007 CSV cells and
  9,785 Markdown cells moved, all of them inside the three metric columns,
  and **zero** bytes moved anywhere else (headers, row counts, CI columns,
  coverage columns, line endings). Each migrated CSV also still
  re-serialises to itself under the `csv` module's default dialect.
* **The recompute fallback is validated against the corpus.** For every
  committed single-run evaluation that carries BOTH a `point` and a
  confusion matrix — 1,391 evaluations, each on all three metrics — the
  committed `point` equals the value recomputed from the counts to 4
  decimal places, with zero mismatches. The 47 point-less blocks are
  therefore recovered by a rule the rest of the corpus proves exact.
* **Nothing analytical read this layer.** No analysis script parses
  `evaluation.csv` or `batch_summary.csv`; the only other reference is
  `rerun_evals_at_10k.py`, which moves the files as siblings. The manifest
  and the `metric-leaderboards` family already read `point` from the JSON.
  The defect lived where humans read, not where numbers were computed.

## The two files the gate skipped — a finding, not residue

`results/paper-eval/mcc/384px/batch_summary.csv` and
`results/paper-eval/mcc/512px/batch_summary.csv` were left untouched. Their
metric cells match neither the current resample mean nor the current
observed point of the per-condition evaluations sitting in their own
sub-directories: those evaluations were re-emitted (BCa migration, then
B = 10,000) and the roll-up was never refreshed. For example the
`Pro Text HIGH T=0.7` row publishes MCC 0.7457 where its own condition
directory now holds mean 0.7467.

Migrating those cells would have imported a second correction — a newer
vintage's numbers — under cover of this one, next to F1 and CI columns
still at the old vintage. They are recorded in the inventory's
`files_skipped` and are **stale roll-ups**, a separate defect from D30.
Both should be regenerated from their conditions, not patched.

## What is still carrying the resample mean

The `batch_summary.json` and `batch_summary.md` siblings were outside this
migration's scope (which is the CSV layer plus `evaluation.md`), and six
of them still publish the resample mean under the MCC / Sens / Spec names:
`batch_summary.json` under `results/paper-eval/mcc/384px/`,
`.../mcc/512px/`, `.../n1/384px-14buf-mcc/`, and
`.../n1/384px-14buf-mcc/pro-rerun/`, plus `batch_summary.md` under the
last two. The last two directories are now internally inconsistent — their
`batch_summary.csv` carries the observed statistic and their `.md` / `.json`
siblings do not.

The recommended remedy is not another patch: those two batch summaries
should be **regenerated** by the fixed writer, which rewrites all three
files together and adds the `*_boot_mean` columns. The other two
directories need the stale-roll-up regeneration described above, which
resolves their JSON at the same time.

## A neighbouring finding the migration surfaced

Among the 47 evaluations whose point had to be recomputed, **12** now
publish an observed statistic that falls outside its own committed
bootstrap interval (5 MCC, 7 sensitivity, and 8 specificity cells across
those files, all under `results/paper-eval/mcc/384px/**` and
`.../512px/**`). This is the "interval excludes its own point estimate"
signature that Phase 2's measured `ci_unreliable` rule tests for — but
that rule covers F1, precision, and recall only, so nothing flags it on
the tile metrics.

No published claim rests on these: **zero** manifest conditions and zero
analyses source from `results/paper-eval/mcc/**` (verified by scanning the
`provenance.source_files` of all 337 conditions and the analyses manifest).
Among the 1,476 committed MCC blocks that carry a `point`, every interval
contains it. The recommendation is a register row, not a rescore.

## Semantics after this migration

- A column named `mcc`, `sensitivity`, or `specificity` in any CSV or
  Markdown table outside `archive/**` is the statistic computed on the
  observed tile confusion matrix.
- The resample mean lives in `tile_classification.<metric>.mean` in the
  JSON, and — in files written from now on — in the `*_boot_mean` CSV
  columns.
- `archive/**` artefacts keep the old convention, as they do for the D28
  flag migration.

## Companion: the D36 CI-method labelling fixes

Phase 5 also landed defect **D36** (finding F12), which has no separate
migration because only one committed data artefact carried the claim:

- **The two 55-map F1 boards** called their per-cell intervals BCa. They
  are the committed evaluations' `f1_ci_lower` / `f1_ci_upper`, which the
  Track-2 adapters compute by the percentile bootstrap and record as
  `"f1_ci_method": "percentile"`. The shared note is now built by
  `paired_ci_note(ci_method)`; the F1 boards say percentile and the two
  MCC boards keep BCa, which is true of them. Both boards were re-rendered
  through `build_55map_leaderboard.py --rebuild-md`, which rebuilds the
  markdown from the committed JSON without recomputation: the diff is
  **one line per board**, and no number moved.
- **`results/conditions-manifest.json`** asserted `ci.method = "BCa"` on
  every cell, including cells whose source evaluation declares no method.
  The generator now copies the method where the source records one and
  omits the key where it does not (the D17 principle), with `method` made
  optional in `docs/manifest-schemas/common-defs.schema.json` first.
  After regeneration, **619 per-buffer cells across 47 conditions** lost a
  method claim; nothing else in any manifest changed except the
  `last_extracted_at` stamp on those same 47 rows, plus one row carried in
  from a concurrently committed phase (see the note at the end of this
  section). The Session 137 audit
  brief put this at 308 cells across 22 conditions; that is the count for
  `results/paper-eval/n1/384px-14buf-mcc/**` alone, and even there this run
  measures 252 cells across 18 conditions. The 619 figure was measured
  twice — once by diffing the manifest cell by cell, once by re-reading
  every source evaluation independently — and the two agree exactly. The
  remaining families are `results/paper-eval/phase2/512px-14buf-mcc/**`
  (210 cells, 15 conditions), `results/rescore-2026-06-07/phase3c/**`
  (126 cells, 9 conditions), `results/era1-pv-stage-d/**` (28 cells, 2
  conditions), and `results/h13-overlap-2026-08-18/common/**` (3 cells, 3
  conditions).
- **`_metadata.bootstrap.method`** was a literal `"BCa"` written before
  any interval existed, contradicted inside 58 committed files by 162
  measured per-metric values. In future files the intent is recorded as
  `method_requested` and `write_outputs` adds a `method` derived from what
  the run actually measured (plus a `methods_measured` census), so the
  block can no longer contradict its own document. Committed historical
  values are left as the audit disclosed them. Metadata schema version
  1.2 → 1.3.

One further manifest row moved, and it is not this phase's: commit
`8dd028c92` (defect D33, a concurrent phase) re-emitted
`gold-standard-extended-buffer-sweep-era2` and deferred manifest
regeneration, so the regeneration this phase had to run picked it up.
The row is `gold-standard-v2::verified-v1`, where all ten per-buffer `ci`
bounds widen — the D15 axis-defect correction that commit documents — with
every point estimate and the whole tile block unchanged.

## Changelog

### 2026-08-20 — Original publication

Written with the migration itself (Session 138, audit remediation Phase 5,
$0 API, zbook). Companion writer fixes in `evaluate_detections.py`,
`build_tiered_leaderboard.py` (the MCC ranking key), and the D36 CI-method
labelling fixes landed in the same phase.
