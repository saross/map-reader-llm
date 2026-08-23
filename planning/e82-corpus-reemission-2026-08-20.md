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
   first; if the point gate fails, against a BOUNDED PLAN of committed input
   vintages adjacent to its own `generated_at_utc` — the all-before
   baseline, then single-input flips to the first-after commit, then
   all-after (cap 6) — because evaluations are sometimes scored against a
   working tree committed minutes later (measured on the pilot: a
   detections commit landed 2 minutes after its evals, "propagate +1
   candidate"). Pinned commits are recorded in
   `_metadata.e82_input_vintage` and the recorded input paths normalised
   back to repo-relative. Reference-vintage reconciliation
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

## Resume runbook (state as of 2026-08-21, zbook away from network)

**Where the campaign stands.** Two pilots passed (14/14 second pilot, the
adjacent-vintage search validated on the two known mixed-state cells). The
full run processed 223 of 1,628 before the D41 abort fired exactly as
designed: 204 ok (8 vintage-pinned) re-emitted, 19 failed on the
mis-aggregated summary tile points. The D41 gate exception is implemented,
tested (18 tier-1 tests), committed, and PUSHED; sapphire has NOT yet pulled
it. Sapphire's working tree holds ~231 re-emitted evaluation files plus the
campaign report, UNCOMMITTED. Nothing further runs until sapphire is back on
the network.

**To resume (one command each, from zbook, when home):**

```bash
ssh sapphire 'cd ~/Code/map-reader-llm && git pull --ff-only && \
  nohup .venv/bin/python scripts/rerun_bca_corpus.py --workers 10 \
  >> /tmp/e82-corpus-run.log 2>&1 < /dev/null & echo resumed'
```

The engine resumes by vintage stamp (1.3 = done): expect the census to show
roughly selected ≈ 1,424, done_1.3 ≈ 245, no_recipe = 13 (the `--expect-skips`
guard enforces the 13). The 19 D41 cells re-enter the worklist and should
re-emit with `summary_tile_point_reaggregated` flags; `n_reaggregated` in the
report must read 19 — more means the defect is wider than diagnosed (stop,
inspect), fewer means some failed again (inspect their attempts).

**Item D checklist (after the run exits 0):**

1. On sapphire: `git status` review; commit the corpus as ONE data commit
   (explicit pathspecs: `results/ outputs/` evaluation siblings + the report
   JSON), message citing this contract; verify `0 behind`, push.
2. On zbook: pull; run the three zero-dry-runs
   (`migrate_ci_flag_basis --dry-run`, `migrate_csv_mcc_point --dry-run`,
   `backfill_tile_point_estimates --dry-run` — each must report 0);
   `rerun_bca_corpus.py --dry-run` must show selected = 0 / no_recipe = 13.
3. Regenerate manifests (`generate_post_run_report.py --all --write`); the
   scripted manifest diff must confine changes to `ci` blocks (+
   `last_extracted_at`, and the 19 D41 cells' summary tile points); ALL
   VALID required.
4. Register the Track-3 gap cell minted 2026-08-21
   (`results/55maps-standardised-ref-2026-08-14/IM-k4/`, F1@50 0.801, MCC
   0.712) as a condition beside its adapter siblings.
5. Full tier-1 + tier-2 + unmarked suites on zbook; tier-1 on sapphire.

**Item E checklist (after operator sign-off on the campaign report):**

1. E82 gains a dated EXECUTION note (counts from the report JSON: n_ok,
   n_pinned_vintage, n_reaggregated, width-ratio median vs the √(B/n)
   model, the 13 named skips, the D40/D41 stories).
2. Defect register: D15's "re-emission OPEN by campaign" closed; D19 row
   annotated; D41 marked executed; changelog entry.
3. `reports/` MD summary written from the report JSON (the § 1 promise).
4. This contract's changelog closed with the final numbers; the audit
   report's changelog gains a completion line; republish the artifact.

## Resume attempt outcome (2026-08-21 evening → 2026-08-22, S139 overnight)

**Resumed per the runbook command, verbatim.** Pre-flight: sapphire 26
behind / 0 ahead, zero pull conflicts, engine idle; pull
fast-forwarded `9c82d3fa0..349cdd1b6`. Census exactly on contract:
`{selected: 1424, done_1.3: 233, other_vintage: 42, unparseable: 0,
no_recipe: 13}` — the `--expect-skips` guard held.

**ABORTED at > 5 failures (§ 3.1) at item ~595/1424.** Run record
(report JSON, `runs[-1]`): n_ok **588**, n_pinned_vintage **21**,
n_reaggregated **18**, n_no_ci 2, width_ratio_median 4.66 (inside the
[0.8, 8] band). Cumulative corpus progress ≈ 842 of 1,424 selected;
vintage stamps preserve it for the next resume.

**Diagnosis.** The D41 gate exception worked as designed for **18 of
the 19** diagnosed cells; one re-failed
(`results/paper-eval/mcc/384px/flash-image-minimal-t-0-7`). The other
**six failures are NEW same-symptom cells** ("point estimates moved")
in `results/paper-eval/n1/384px-14buf-mcc/` — a tree with zero
failures in the first run — sharing config lineages with the
diagnosed set (`flash-image-minimal-t-0-7`, `pro-text-high-t-0-7`,
`flash-image-high-t-0-7`, `flash-text-minimal-t-0-0`,
`flash-text-minimal-t-0-7`, `flash-text-high-t-0-7`). **The D41
mis-aggregation defect therefore extends beyond the diagnosed 19**,
and per this contract's own rule that is a STOP-AND-INSPECT state.
*[CORRECTED 2026-08-22 by the inspection
(`reports/e82-d41-widening-inspection-2026-08-22.md`, commit
a50638832): the wider-defect inference is FALSE. The six n1-tree
cells are NOT D41 — their summaries are correct; they fail on
pass-ORDER replay fidelity (lexicographic committed labels vs
numeric canonical-resolver replay, biting only at ≥ 10 runs on
batch-recovered cells). The one re-failed original-19 cell hit a
rounding-boundary bug in the exception helper (sum()/len() vs
np.mean at a 4 dp half-boundary). D41 population corpus-wide is
exactly the 19; ordering-defect population exactly 6, none
unreached; the contract's n_reaggregated = 19 stands as written.]*
No further action taken overnight: engine idle, sapphire working tree
untouched (re-emitted files still awaiting the single post-completion
data commit per Item D).

**PI RULING (2026-08-22): C1 + D adopted** — key per-run gate
comparisons by run label rather than index (order-permuted pools
pass with zero tolerance loss; changed pools still fail as
label-set mismatches), and fix `_reaggregated_mean` to
`round(float(np.mean(vals)), 4)` so the exception helper agrees
with the writer. Expected counts: `n_reaggregated` stays **19**;
new expected order-normalisations **6**. Two regression tests
required (a ≥ 10-run lexicographic-label pool; a per-run mean on a
4 dp half-boundary). Implement, test, and resume next session;
runbook command unchanged. Evidence:
`reports/e82-d41-widening-inspection-2026-08-22.md` (a50638832).

**Superseded next-session inspection plan** (executed 2026-08-22): (1) confirm the mechanism on one
n1-tree cell (does its summary tile point equal run 1's per-run tile
point?); (2) enumerate the full same-symptom population corpus-wide
with a cheap read-only scan, rather than discovering it five failures
at a time; (3) widen the D41 exception and the expected-reaggregation
set accordingly (PI ruling; contract changelog entry); (4) resume —
the runbook command is unchanged.

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

### 2026-08-23 (later) — SIGNED OFF; Item E executed; contract CLOSED

The Principal Investigator reviewed the campaign report and its briefing
(failure accounting 32/32 attributed; flag raises 1,134/1,134 traced to
measured partial coverage, zero lowered; census arithmetic exact at
1,724 = 1,657 + 42 + 13 + 12), **ratified the buffer-mean gate
extension**, and signed off on 2026-08-23. Item E landed in the same
block: the E82 corpus execution note (`db2e1ea4e`) — including the
correction of the data commit's pinned-vintage count (27 → 35) — the
defect-register closures D15/D19/D41 plus new row D42 (`8db04432e`),
and the campaign summary
`reports/e82-corpus-reemission-summary-2026-08-23.md` (`a110fd064`).
Final numbers: 1,655 re-emitted / failed 0 / n_reaggregated 19 /
n_order_normalised 6 / pinned 35 / medians 4.43–5.31. Post-contract
rider executed under the same sign-off conversation: the genuine IM-k4
cell (derivation, scoring, registration — register at 338 conditions),
replacing the mislabelled Item D step 4. **This contract is CLOSED**;
the one live residual it leaves is D42's standing mitigation.

### 2026-08-23 — CAMPAIGN COMPLETE; Item D executed (Session 140)

**Item C closed.** The clearing resume processed the four remaining
buffer-boundary cells: ok 4 / failed 0. Engine census reads
**selected = 0, done_1.3 = 1657, no_recipe = 13**; cumulative
counters exactly on ruling — **n_reaggregated = 19,
n_order_normalised = 6**; per-leg width-ratio medians all inside
[1.05, 6]. ONE data commit from sapphire (`43ea31b26`, 4,965 files,
report JSON included); N1 trees untouched throughout.

**Item D executed, with three findings:**

1. **ci-flag basis regression (169 files)** — the re-emission
   regressed the S138 measured-flag migration because the writer does
   not stamp `ci_flag_basis`/`ci_excludes_point`; zero flag VALUES
   moved. Migration re-applied idempotently (`e46f13bba`); its
   dry-run now reports 0. Writer gap to register at Item E.
2. **Recorded output_dir pollution (1,655 files)** — every replay
   recorded its temp workdir as `cli_args.output_dir`; caught by the
   migration-queue round-trip test. Engine fixed (`_accept` now
   normalises the output path) + one-field repair sweep + regression
   test (`70c550177`).
3. **Item D step 4 NOT executed — the "IM-k4 gap cell" is a
   mislabelled duplicate.** The image run's production consensus is
   3-of-5 (`consensus-3of5.geojson`; `resolved_config.yaml`
   `vote_threshold: 3`), so `verified/verified_detections.geojson` IS
   the k3 set already registered as
   `55maps-image-generalisation::verified-k3-standardised-gt`. The
   S138 cell at `results/55maps-standardised-ref-2026-08-14/IM-k4/`
   re-scored those same detections (identical n_det 4,680, F1@50
   0.801, MCC 0.712 = IM-k3's rounded values). Registering it would
   mint a duplicate condition under a false k4 label. The file stays
   on disk, uncited; a GENUINE IM-k4 needs a 4-of-5 re-vote of the
   image pool — a PI decision (likely $0: the k4 candidate set is a
   subset of k3's, whose verifier verdicts already exist).

**Manifests** regenerated, ALL VALID (33/337/1,138/38); scoped leaf
diff fully accounted: ci bounds (3,414 pairs — the campaign's
purpose), EXACTLY the eight enumerated order-artefact point values,
1,134 `ci_unreliable` False→True flips traced to measured
partial_coverage replacing unmeasured pre-campaign defaults (§ 1
scope, flagged for sign-off), `last_extracted_at`, and new writer
bookkeeping on 36 conditions. The three zero-dry-runs report 0.
Suites: tier-1 1,892 + tier-2 27 green locally; tier-1 on sapphire.

**Item E awaits operator sign-off of the campaign report** per § 2.

### 2026-08-22 (later) — Buffer-mean order artefacts: a third boundary layer

The C1 + D resume surfaced ONE further, previously masked layer of the
same mechanism: `evaluate_multi_run_mean` aggregates the summary BUFFER
table (f1/precision/recall per buffer) with the identical
order-sensitive `round(float(np.mean(vals)), 4)`, so an order-permuted
pool can flip a summary buffer value by one 4 dp step. Observed live
(leg of 2026-08-22, items 82 and 98: `n1/.../flash-image-minimal-t-0-7`
25 m precision + tile mcc; `n1/.../flash-text-minimal-t-0-0` 40/45/50 m
f1, raw mean exactly 0.52045); the corpus-wide enumeration finds
**eight shifted summary values across four of the six order-permuted
cells** and nowhere else (the widening inspection's § 1.5 sweep scanned
tile-metric blocks only, so this layer was outside its enumeration).
The gate now forgives a moved summary buffer point ONLY when the pool
is order-permuted, every labelled per-run buffer measurement reproduces
exactly, and both committed and replayed values equal the writer's
aggregation over their own run order — filed under
`per_run_order_normalised.summary_buffer_points`, never D41. Two
regression tests added (25 total green; tier-1 1,788). The 2026-08-22
leg therefore ends with those four cells failed (below the abort
threshold) and still at vintage 1.2; **one further resume via the
unchanged runbook command clears them**. Live validation from the same
leg: the 19th D41 cell (`mcc/384px/flash-image-minimal-t-0-7`)
re-emitted correctly under fix D (tile mcc 0.3295, stamped 1.3) —
cumulative `n_reaggregated` = 19 exactly as required. Expected final
order-normalisation count stays 6 (2 from the 2026-08-22 leg, 4 from
the clearing resume).

### 2026-08-22 — C1 + D implemented (Session 140)

The PI's C1 + D ruling is implemented in `scripts/rerun_bca_corpus.py`:
per-run gate comparisons are keyed by run LABEL (index fallback when
labels are absent or non-unique; a changed pool fails as a label-set
mismatch), and `_reaggregated_mean` mirrors the writer's
`round(float(np.mean(vals)), 4)` exactly. The pure order/rounding
artefact on the n1-tree boundary cell (committed and replayed summaries
BOTH correct writer means, split only by summation order at a 4 dp
half-boundary) is filed under a new `n_order_normalised` report counter,
never as a D41 re-aggregation, so `n_reaggregated = 19` stays exact as
written. Five regression tests added — the two the ruling required (a
>= 10-run lexicographic-label pool; a 4 dp half-boundary mean) plus
moved-measurement-in-permuted-pool, changed-pool label-set, and
order-artefact-classification cases. Tier-1 green at 1,786. Expected
resumed-leg counts: `n_reaggregated` = 1 (19 cumulative),
`n_order_normalised` = 6 — more of either is stop-and-inspect. Runbook
command unchanged.

### 2026-08-20 (later still) — Adjacent-vintage search after the first pilot

The first pilot (15 files, 4 workers) passed 13 and failed 2 — both 55-map
image cells whose consumed state mixed the before-vintage GT with a
detections state committed 2 minutes AFTER scoring. The frozen fallback
alone cannot reach mixed states, so § 3.1 now specifies the bounded
adjacent-vintage plan (implemented and unit-tested; 15 tier-1 tests). The
pilot re-runs before the corpus.

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
