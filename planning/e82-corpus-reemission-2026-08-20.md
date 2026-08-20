# E82 corpus re-emission — controlling document

> **Last revised**: 2026-08-20 (amended after the fresh-context pre-launch
> audit: input-vintage rule added per the PI's B1 ruling; pilot redesigned;
> gate holes closed; finish states made measurable — see § Adjudication).
> Original publication earlier the same day. See [§ Changelog](#changelog).

**What this is.** The controlling document for the E82 corpus-wide re-emission
campaign: re-running every BCa-era committed evaluation at B = 10,000 through
the fixed bootstrap wrapper, on sapphire, per the PI's 2026-08-19 E82 ruling
("re-run everything that needs re-running") and the 2026-08-20 scope ruling
(whole BCa corpus, uniform end vintage). Produced by the `/pre-run-review`
protocol; the six sections below are the review's record and the run's
contract. Companion rulings executed in the same block: archive the legacy
`results/leaderboard/**` family; archive the stray unstamped selection-aware
artefact found untracked on sapphire.

**Why**: ~1,520 committed BCa intervals at B = 10,000 predate the `122104b8a`
axis fix and are too narrow by ≈ √(B/n) (D15/E82); a further tranche ran
pre-standardisation. No significance verdict depends on them (Decision 10's
rule is on difference CIs), but the register publishes them, and one
register-backing instance (the era2 GS cell) has already been shown ~4.6× too
narrow and corrected. The 2026-08-20 audit remediation made every recipe
loadable, which is what makes a corpus replay possible at all.

## Block items, in order

| # | Item | Where |
|---|---|---|
| A | Sapphire sync: archive the stray `55map-standardised-leaderboard-50m_m1.json` into `archive/superseded-selection-aware/`; fast-forward sapphire to HEAD; never touch `inputs/tiles_*` untracked trees (N1) | sapphire + zbook |
| B | Archive `results/leaderboard/**` → `archive/superseded-leaderboards/` with a defect-stating README; adjust tests/registry rules that reference the old path; rebuild the generated-file registry | zbook |
| C | E82 re-emission: extend the D17 replay engine to corpus scope (`scripts/rerun_bca_corpus.py`), pilot 10 files on sapphire, then full run with workers | sapphire |
| D | Post-run gates and manifest regeneration; commit from sapphire; pull and re-gate on zbook | both |
| E | Bookkeeping: E82 execution note, D15/D19 register updates, this document's changelog | zbook |

## § 1 Artefact inventory

- **Item A** produces one archived JSON + a README line; sapphire moves to
  campaign HEAD. No repo artefact changes beyond the archive addition.
- **Item B** moves 38,258 files (tier JSONs/MDs, cells, rows, enrichment
  summaries) under `archive/superseded-leaderboards/`, adds a README naming
  the known defects (mean-ranked MCC order on three combined boards;
  56 pre-migration CI columns; superseded greedy-clique tiering; the
  enrichment `mcc`-nulling hazard), updates registry rules, re-emits
  `reports/verification/generated-file-registry.json`. Phase-6 ownership
  tests that classify per-architecture paths keep working on path strings;
  any test reading committed board content is re-pointed at the archive path
  or the synthetic fixture, never deleted.
- **Item C** rewrites, in place, `evaluation.json` + `evaluation.csv` +
  `evaluation.md` for every worklist file (census 2026-08-20: **1,668
  BCa-era evaluations** = 572 at metadata v1.1 + 1,096 at v1.2, of which 13
  deployment-oracle cells have unresolvable recipe paths and are SKIPPED with
  a report row — uncited, documented in D33). Re-emitted files land at
  metadata v1.3 with `method_requested`/measured `method`, measured
  reliability flags with basis, observed-point MCC columns plus
  `*_boot_mean`, and corrected BCa intervals. Campaign report:
  `results/e82-corpus-reemission-2026-08-20.json` (per-file: B before/after,
  20 m width ratio, gate result) plus a short MD summary in `reports/`.
- **Item D** refreshes `results/conditions-manifest.{json,md}` (CI bounds
  move on every re-emitted register-backing cell; nothing else may move) and
  the analyses/passes manifests via the standard generator.
- **Cross-cutting**: defect register rows D15/D19; erratum E82 gains a dated
  execution note; this document's changelog.

## § 2 Finished states (countable)

- A: sapphire `git status --porcelain` shows exactly the N1 tile trees;
  `git rev-parse HEAD` equal on sapphire, zbook, origin.
- B: `git ls-files results/leaderboard/` returns 0; the archive README
  exists; registry `--check` and `--strict` exit 0; full tier-1 green.
- C: worklist processed = **1,655** with the **13 named skips recorded in
  the report** (`census` + `skips_no_recipe` fields) and **failed = 0**;
  every processed file passes the 1e-9 point gate on its accepted attempt
  (current-input or vintage-frozen, the latter counted in
  `n_frozen_vintage`); the post-run engine census reads **selected = 0 and
  no_recipe = 13**; the three campaign dry-runs all report zero
  (`migrate_ci_flag_basis`, `migrate_csv_mcc_point`,
  `backfill_tile_point_estimates`). "Single-vintage" is scoped to the BCa
  population: the 16 percentile adapter cells, the 36 pre-metadata
  percentile-era files, and the 2 v1.0 files are correctly outside scope and
  keep their vintages (audit M5).
- D: manifest generator reports ALL VALID; a scripted manifest diff shows
  changes confined to `ci` blocks (plus `last_extracted_at`) on re-emitted
  sources; tier-1 (≥ 1,746), tier-2 (27), unmarked (103) all green on zbook.
- E: E82 carries the execution note; D15's "re-emission OPEN by campaign"
  text is closed; changelog entries landed.

Human sign-off sits AFTER item D's gates: the operator reviews the campaign
report before item E's erratum note is written.

## § 3 Stop states (tripwires)

1. **Input-vintage rule (audit B1; PI ruling 2026-08-20).** ~324 cells were
   scored against inputs later changed in git (defect D40 carries the
   machine-readable list). Each cell is replayed against current inputs
   first; if the point gate fails, once more against the inputs AS OF its
   own `generated_at_utc`, materialised from git history, with the frozen
   commits recorded in `_metadata.e82_input_vintage` and the recorded input
   paths normalised back to repo-relative. Reference-vintage reconciliation
   is deliberately NOT bundled here (the E81/E82 lesson); the Track-3
   best-available-GT completeness sweep is queued as its own item.
2. **Any point estimate moves > 1e-9** on the accepted attempt → the file is
   left untouched, logged as FAILED with both attempts' diagnostics;
   **> 5 failures stops submission**, already-dispatched workers are drained
   and RECORDED, and the report is written before exit (audit M1/M2).
3. **Width tripwire, per file**: measured on the WIDEST buffer row carrying
   intervals in both vintages (91 cells have no 20 m row — audit M3); a
   ratio outside [0.8, 8], or a replay interval collapsing to zero/absent
   where the committed one existed, fails the file. Cells with no committed
   interval anywhere are recorded `no_ci`, never silently passed. Expected
   ratios: √(10000/n) for pre-fix files (1.08 at n = 8,541 up to 5.53 at
   n = 327); ≈ 1.0 for the ~49 already-corrected cells.
4. **Median guard**: once 200 ratio samples exist, a running median outside
   [1.05, 6] aborts mid-run; the band is re-checked at completion on full
   runs. Pilots make no median claim (audit M4/B2 — the band is a
   corpus-level statement).
5. **Pilot gate**: the pilot is a SEEDED random sample (seed 20260820) plus
   forced includes — the three cells the audit watched fail on current
   inputs, so the vintage-frozen path is exercised before the corpus run.
   It must pass with failed = 0 before the full run starts; runtime
   calibrates the projection, and a full-run projection over 12 h at the
   chosen workers pauses for the operator.
6. **Skip-census freeze**: the engine refuses to run unless the no-recipe
   census equals the expected 13 (`--expect-skips`), so a checkout that
   resolves different inputs — sapphire retaining untracked leftovers of the
   skipped cells' inputs, for instance — cannot silently widen the campaign
   (audit M7).
7. **Sapphire load/environment**: check `nproc` and current load before
   choosing workers (reserve ≥ 2 cores; the check-compute-hosts backstop);
   sapphire venv must import the project cleanly at campaign HEAD. Never
   fall back to zbook silently — that is a report-and-ask.
8. **Sequencing**: item C must not start until A and B are pushed and
   sapphire is at that HEAD (B changes the registry and test surface that
   D's gates rely on; A is what makes sapphire's tree current).
9. **No API spend of any kind** — this campaign is $0 by construction; any
   path that would call an API is a defect, full stop.
10. **Git hygiene on sapphire**: explicit pathspecs on commit; re-verify
   `0 behind` before push; **never `git stash -u`, `git clean`, or
   `git reset --hard`** (N1 — the untracked tile trees live there).

## § 4 Dependency structure

A → B → C → D → E is a chain, with one genuine parallelism: B (zbook) can
run while A's sapphire pull is in flight, since they touch disjoint trees —
but both must be pushed before C. Coherence orderings: (i) exactly one item
(B) rebuilds the generated-file registry this block — C and D do not touch
it; (ii) exactly one item (D) regenerates the manifests — C does not; (iii)
the campaign report file belongs to C alone; E only appends prose. The
13-file skip list (12 deployment-oracle cells + 1
`rescore-2026-05-31/e47-propose-brief` cell — audit M7 corrected the count
attribution) is enforced by the `--expect-skips` guard and named in the
report, so C cannot silently absorb a 14th.

## § 5 Partial-completion semantics

The replay is deterministic (seed 42, fixed B). Each sibling is staged in
its destination directory and `os.replace()`d — no committed file is ever
truncated — and the JSON, which carries the 1.3 vintage stamp that marks a
cell complete, lands LAST: a kill mid-cell can leave a cell's CSV newer than
its JSON for the seconds until resume, but the cell remains selected and the
next run rewrites all three siblings together (audit m1). Partial state across the corpus is
visible and resumable: selection keys on `metadata_version != "1.3"`, so a
restart processes exactly the remainder. The mixed-vintage window between a
partial C and item D is gated by § 2's zero-count census — D does not start
until the census reads zero. Commits: C lands as ONE data commit (the corpus
is one logical change; a review-sized split adds nothing when every file
passed the same gate), with the campaign report in the same commit; the E82
note and register rows land with their changelog entries in one commit each
(the one-commit-per-document rule).

## § 6 Verification stack

- **Layer 0**: the campaign report JSON is the machine-readable record;
  every number in the MD summary and the E82 note cites it.
- **Layer 1**: `rerun_bca_corpus.py` reuses the tested D17 replay path and
  the Phase-7 recipe recovery; new selection/worker logic gets tier-1 tests
  (selection by vintage, skip-list stability, resume-by-vintage) before the
  pilot.
- **Layer 2**: a fresh-context Opus agent audits the committed contract and
  the script BEFORE launch (the clean-context pass, this document as input),
  with fault-injection probes (empty worklist; a doctored point estimate must
  fail the gate; a broken recipe must land in skips, not failures) and a
  reported denominator. After the run, the same stance re-derives the
  campaign summary's headline numbers from the report JSON. Disagreement
  rule: a correction that conflicts triggers a third derivation, never
  auto-lands.
- **Layer 3**: the three zero-dry-runs; the manifest diff scope check; the
  metadata-vintage census; full suites on both machines.
- **Layer 4**: operator gates — the go/no-go below; sign-off on the campaign
  report before the E82 note lands.

## Hardenings recorded by this review

1. Pilot-first with a calibrated runtime projection and a 12 h pause line.
2. Abort at > 5 gate failures (systematic-failure tripwire).
3. Width-ratio plausibility band as a stop state, not a curiosity.
4. Selection by metadata vintage rather than declared method, so the 22
   method-silent register-backing cells are included without assuming their
   method (the D17 principle applied to selection).
5. Resume keyed on the artefact's own vintage stamp — no sidecar state to
   desynchronise.
6. Registry and manifest each owned by exactly one item (coherence).
7. The frozen 13-file skip list, named in the report.
8. B's test re-pointing rule: archive-affected tests are re-pointed, never
   deleted.

## Pre-launch audit adjudication (2026-08-20)

The codified clean-context pass (one fresh-context Opus agent, 13 live
probes, 23 claims checked, denominator reported) returned 2 blockers, 7
majors, 6 minors — recommendation FIX-THEN-LAUNCH. Dispositions:

| Finding | Disposition |
|---|---|
| B1 stale-input corpus (~324 cells; 3 live-replay failures confirmed) | PI ruling: vintage-frozen fallback (engine); reference-vintage question split out — D40 records the drift, and a Track-3 best-available-GT completeness sweep is queued separately |
| B2 pilot slice (alphabetical, one family, undetectable ratios) | Fixed: seeded random sample + forced includes of the three known-stale cells; pilots make no median claim |
| M1 unguarded worker result | Fixed: every exception becomes a failure row; report written in `finally` |
| M2 in-flight writes unrecorded on abort | Fixed: bounded submission window; abort stops submission and drains, recording every row |
| M3 width-tripwire holes (zero-collapse, no upper bound, 91 no-20 m cells) | Fixed: widest-common-buffer ratio, band [0.8, 8], collapse fails, `no_ci` recorded |
| M4 median band post-mortem | Fixed: running-median guard from 200 samples + completion check; contract wording corrected |
| M5 16 adapter cells outside scope | Accepted with rationale: they are percentile-method by construction, not D15-affected; § 2 C now says so |
| M6 unmeasurable finish states | Fixed: § 2 C rewritten with the engine's own countable outputs |
| M7 skip list not frozen or recorded | Fixed: `--expect-skips` guard; census + named skips in the report; count attribution corrected (12 + 1) |
| m1 atomicity claim | Fixed: staged `os.replace`, JSON last; § 5 rewritten |
| m2 `--pilot 0` | Fixed: rejected by argparse |
| m3 untested main()-level paths | Fixed in part: 13 tier-1 tests now encode the audit's fault injections (gate, width holes, worker exception, skip guard, pilot-zero, frozen fallback); the parallel drain path remains exercised by the pilot rather than unit tests, accepted |
| m4 item B "~300 files" | Fixed: 38,258 |
| m5 report fields / MD summary | Fixed: `bootstrap_after` recorded; the MD summary is item E's deliverable, written from the report JSON after operator sign-off |
| m6 non-canonical basenames | Fixed: canonical-basename filter in selection |

Clean probes worth keeping on record: the resume stamp is real
(`evaluate_detections.py` writes 1.3); detection-resolution fidelity
1,655/1,655 against recorded pass counts; the worklist is machine-portable
(1,655/1,655 tracked inputs); the D15 width model confirmed live (5.469×
measured vs 5.42× predicted; an already-corrected cell at exactly 1.0000×);
$0 API by import graph; runtime ≈ 16–38 CPU-h → 1.6–3.8 h at 10 workers.

## Changelog

### 2026-08-20 (later) — Audit adjudication amendments

All findings of the pre-launch audit adjudicated (table above); the engine
revised (vintage-frozen fallback, pilot redesign, gate-hole closures, abort
recording, skip freeze, atomic staging) with 13 tier-1 fault-injection
tests; §§ 2–5 corrected to measurable criteria. The B1 policy and the
Track-3 sweep split were PI rulings taken during adjudication.

### 2026-08-20 — Original publication

Written during the `/pre-run-review` dialogue, Session 138, after the PI's
three scope rulings (whole BCa corpus; archive the legacy leaderboard family;
archive the sapphire stray). Census run same day: 1,668 selected, 13
unresolvable (named), ~1,655 runnable.
