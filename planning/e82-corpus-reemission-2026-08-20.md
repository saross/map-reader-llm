# E82 corpus re-emission — controlling document

> **Last revised**: 2026-08-20 (original publication; pre-run review conducted
> before launch). See [§ Changelog](#changelog).

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
- **Item B** moves ~300 files (tier JSONs/MDs, cells, rows, enrichment
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
- C: worklist processed = 1,668 with **skipped = 13 named files and failed =
  0**; every processed file passes the 1e-9 point gate; post-run
  `metadata_version` census over tracked non-archive evaluations shows 1.1
  and 1.2 counts of **zero** on the BCa population; the three campaign
  dry-runs all report zero (`migrate_ci_flag_basis`, `migrate_csv_mcc_point`,
  `backfill_tile_point_estimates`) — the corpus is single-vintage.
- D: manifest generator reports ALL VALID; a scripted manifest diff shows
  changes confined to `ci` blocks (plus `last_extracted_at`) on re-emitted
  sources; tier-1 (≥ 1,746), tier-2 (27), unmarked (103) all green on zbook.
- E: E82 carries the execution note; D15's "re-emission OPEN by campaign"
  text is closed; changelog entries landed.

Human sign-off sits AFTER item D's gates: the operator reviews the campaign
report before item E's erratum note is written.

## § 3 Stop states (tripwires)

1. **Any point estimate moves > 1e-9** on any file → that file is left
   untouched, logged as FAILED; **> 5 failures aborts the run** for
   diagnosis (a systematic failure, not per-file noise).
2. **Width ratios off-model**: pre-fix v1.1/v1.2 files must widen ≈ √(B/n)
   (n = 340–8,541 → ratios ≈ 1.08–5.4). A median outside [1.05, 6] or any
   ratio < 0.8 on a pre-fix file → stop, diagnose.
3. **Pilot gate**: the 10-file pilot must pass 10/10 with plausible ratios
   before the full run starts. Pilot runtime calibrates the wall-clock
   estimate; if the full-run projection exceeds 12 h at 10 workers, pause
   and report rather than run into the next day silently.
4. **Sapphire load/environment**: check `nproc` and current load before
   choosing workers (reserve ≥ 2 cores; the check-compute-hosts backstop);
   sapphire venv must import the project cleanly at campaign HEAD. Never
   fall back to zbook silently — that is a report-and-ask.
5. **Sequencing**: item C must not start until A and B are pushed and
   sapphire is at that HEAD (B changes the registry and test surface that
   D's gates rely on; A is what makes sapphire's tree current).
6. **No API spend of any kind** — this campaign is $0 by construction; any
   path that would call an API is a defect, full stop.
7. **Git hygiene on sapphire**: explicit pathspecs on commit; re-verify
   `0 behind` before push; **never `git stash -u`, `git clean`, or
   `git reset --hard`** (N1 — the untracked tile trees live there).

## § 4 Dependency structure

A → B → C → D → E is a chain, with one genuine parallelism: B (zbook) can
run while A's sapphire pull is in flight, since they touch disjoint trees —
but both must be pushed before C. Coherence orderings: (i) exactly one item
(B) rebuilds the generated-file registry this block — C and D do not touch
it; (ii) exactly one item (D) regenerates the manifests — C does not; (iii)
the campaign report file belongs to C alone; E only appends prose. The
13-file skip list is frozen at census time and named in the report, so C
cannot silently absorb a 14th.

## § 5 Partial-completion semantics

The replay is deterministic (seed 42, fixed B) and per-file atomic (temp dir,
gate, then sibling copy) — a killed run leaves each file either fully old or
fully new, never mixed WITHIN a file. Partial state across the corpus is
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

## Changelog

### 2026-08-20 — Original publication

Written during the `/pre-run-review` dialogue, Session 138, after the PI's
three scope rulings (whole BCa corpus; archive the legacy leaderboard family;
archive the sapphire stray). Census run same day: 1,668 selected, 13
unresolvable (named), ~1,655 runnable.
