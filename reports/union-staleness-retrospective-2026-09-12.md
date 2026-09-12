# Union-staleness retrospective — is any committed consensus union stale against its pool?

> **Last revised**: 2026-09-12 (later — the PI's rulings on § 3.3 and § 4.1
> executed: the five stale T = 1.0 unions relabelled N = 5 with an erratum, and
> the § 4.1 near-miss's two stale h10 siblings archived and rebuilt. Before that:
> original publication). See [§ Changelog](#changelog) for revision history.

**Verdict in one line.** Of the **106** consensus unions that a registered
condition reads, **64 REPRODUCE**, **36 are SUBPOOL-CONSISTENT**, **1 is
UNRESOLVED**, and **5 are STALE** — all five in
`outputs/h11/consensus-384-UNINTENDED-T1.0/voting/`, where the union reflects
the **first 5 of the pool's 30 passes** while the register describes the
conditions that read it as `consensus-1of30` … `consensus-5of30` with
`n_passes: 30`.

## 1. Why this check exists

Finding 4 of `reports/name-keyed-cache-audit-2026-09-12.md:261-292` established
that a consensus union written before 2026-09-12 records only `total_passes` in
its `voting_summary.json` — "no pass paths, no pass count per file, no hashes"
— and that `build_all_consensus.check_existing_consensus`
(`scripts/build_all_consensus.py:329-356`, with the skip at `:439-446`) returns
"exists" from a glob. A recovery or top-up that adds or rewrites a pass under
the pool therefore leaves the union serving under its own name, unrebuilt.

That audit's own attempted demonstration was **negative and inconclusive**: of
151 `outputs/**/voting_summary.json` surveyed, 37 disagreed with the number of
`run_*` directories in their pool, and all 37 were legitimate sub-pool unions
whose directory names declared the subset (`consensus-n5`, `consensus-n10`).
The finding's closing sentence names the only decisive test —
"re-deriving each union from its pool and comparing cluster sets … **needs
sapphire**" (`:290-292`) — and the Principal Investigator queued it on
2026-09-12. Pull request #14 fixed the defect **forward**
(`scripts/merge_passes.py:478-509` `build_pass_provenance`, schema
`consensus-pass-provenance/1`); this report settles it **backward**.

## 2. Method

**Scope — unions a registered condition reads.** `results/conditions-manifest.json`
(read 2026-09-12: `schema_version` present, 542 conditions) records for each
condition a `provenance.source_files` list. A condition reaches its detections
either directly (a `.geojson` in that list) or through the `evaluation.json`
that scored it (`_metadata.input_files.detections`, e.g.
`results/condition-scoring-backfill-2026-05-30/gs-v2-consensus-3of5/evaluation.json`).
Following both hops resolves **396 distinct detection files**. Of those, **106**
are `merge_passes.py` consensus unions under `outputs/`; they are read by **106**
of the 542 registered conditions. The remaining 290 were excluded, and the
census is:

| excluded class | n |
|---|---:|
| detections under `results/` (re-score trees, board cells) | 131 |
| single-pass / per-run detections under `outputs/` | 85 |
| detections under `archive/` (superseded leaderboards) | 34 |
| verifier-accepted or materialised proposer-verifier sets (`accepted_*`, `verified*`, `vote*_prob*`) | 22 |
| Weighted Box Fusion (WBF) outputs (`wbf_vote*.geojson`) | 10 |
| absolute paths into a vanished `~/cc-scratch/tmp/*/frozen` tree (all single-pass) | 7 |
| `outputs/h11/pv-diag-256/consensus/text-baseline.geojson` (single-pass) | 1 |
| **total excluded** | **290** |

No union-shaped filename (`consensus_t*`, `consensus-NofM`, `merged_t*`) occurs
outside `outputs/` in the manifest's reader set, so the scope rule is complete
for unions. WBF outputs are excluded because `scripts/fuse_detections_wbf.py`,
not `merge_passes.py`, writes them: they are a different aggregation with a
different staleness question.

**Re-derivation.** `scripts/check_union_provenance.py` (added by this work) calls
`merge_passes.py`'s own `load_pass_detections` → `deduplicate_within_pass` →
`cluster_across_passes` → `apply_threshold` — the same implementation that wrote
the committed files — so a difference in output is a difference in **inputs**,
not in algorithm. Every re-derived union was written to a scratch directory on
sapphire (`/tmp/union-check-all`); **no committed union, evaluation, or register
row was modified.**

**Parameters recovered per union.** The vote threshold comes from the filename
(`consensus_t22.geojson` → T=22; `consensus-3of5.geojson` → T=3). The pool is
the parent of the consensus directory, because
`build_all_consensus.build_merge_command` (`scripts/build_all_consensus.py:524-542`)
invokes `merge_passes.py --input-dir <cell> --output-dir <cell>/consensus --sweep`.
Eleven union directories predate that driver and carry an explicit override in
`scripts/check_union_provenance.py:POOL_OVERRIDES`, each with the anchor that
establishes it — `results/run-conditions.json` `decomposition.<run>.proposer_pools`
for the gold-standard-v2, consensus-384-t1-0, h8-v2, and h12-v2 cells, and for
`outputs/h12-v2/greedy/r2-balanced` (which has no pool of its own)
`results/run-facts.json` `facts.h12-v2._flags` ("r2-balanced reuses h10 pool")
together with `scripts/fuse_detections_wbf.py:136-142`, which names
`outputs/h10/evaluation-v2/pool_160_hp4hn4/run_{1..5}`. The re-derivation
confirms that mapping: `r2-balanced/consensus_t4.geojson` reproduces from that
pool exactly (236 = 236 features, zero unmatched, maximum matched offset 0.0 m).

**Declared sub-pools.** A `consensus-nN` directory means `--passes 1,..,N`, the
first-N rule — anchored at `scripts/build_phase3_subpool_consensus.py:23-28`
("restricts to `run_1..run_N` *by parsed run number* — i.e. the **first N
passes**") and at `scripts/run_phase3a_image_analysis.sh:105-117`, which passes
the literal `"1,2,3,4,5"`.

**Comparison.** Feature count, plus a bidirectional nearest-neighbour
coordinate match at **1 m** — every committed feature must have a re-derived
feature within 1 m and vice versa. Matching both ways catches a union that is a
strict subset or superset of the re-derivation as well as one whose centroids
have moved. Union features are WGS84 points; both sides are projected to
EPSG:32635 before measuring. One metre is two orders of magnitude below the
20 m clustering tolerance, so it separates "same output" from "same pool,
different clustering".

**Compute.** sapphire, 16 worker processes, 1 m 11 s wall for all 106 unions
(10 m 17 s CPU). Machine-readable output:
`results/union-staleness-retrospective-2026-09-12.json` (106 rows, one per
union, with the pool, the passes used, the passes not reflected, the unmatched
counts, and the maximum matched offset).

## 3. Finding: five STALE unions, all in one run

`outputs/h11/consensus-384-UNINTENDED-T1.0/voting/consensus_t1..t5.geojson`
each **reproduce exactly from the first 5 of the pool's 30 passes** — 974, 616,
484, 395, and 295 features respectively, zero unmatched in either direction,
maximum matched offset 0.066 m — and reproduce from **no declared selection**.
Nothing on disk declares the subset: the directory is `voting/`, not
`consensus-n5/`, and the pool
`outputs/h11/consensus-384-UNINTENDED-T1.0/384/` holds `run_1` … `run_30`.

Re-derived against the whole 30-pass pool the same files diverge grossly:

| union | committed | re-derived from first 5 | re-derived from all 30 | committed features with no 30-pass match |
|---|---:|---:|---:|---:|
| `consensus_t1.geojson` | 974 | **974** | 1,862 | 709 |
| `consensus_t2.geojson` | 616 | **616** | 1,186 | 480 |
| `consensus_t3.geojson` | 484 | **484** | 953 | 358 |
| `consensus_t4.geojson` | 395 | **395** | 828 | 281 |
| `consensus_t5.geojson` | 295 | **295** | 770 | 196 |

(An intermediate first-10 re-derivation also fails on all five — 1,246 / 784 /
643 / 556 / 502 features — so the reflected subset is 5, not some other prefix.)

**The mechanism, dated from the run's own artefacts.** The pass metadata puts
`run_1` … `run_5` at `2026-03-14T11:10:45` – `11:10:49` UTC and `run_6` …
`run_30` at `11:47:29` – `11:53:32` UTC (`detections_384_run{01,05,06,07,30}.meta.json`,
`timestamp.end`, read 2026-09-12). `study_manifest.json`, generated
`2026-03-14T11:30:13Z`, declares `"runs_per_condition": 30` and its
`execution_order` lists exactly the 25 runs `384/run_6` … `384/run_30` —
i.e. the first five were already done and the manifest scheduled the rest.
`checkpoint.json`, `last_updated` `2026-03-14T11:53:34Z`, lists all 30 as
`completed` with `run_1` … `run_5` first. The union in `voting/` was built
between those two moments and never rebuilt: its `voting_summary.json` is eight
lines reading `{"total_passes": 5, "thresholds": {...}}`, and every feature's
`contributing_passes` is a subset of `["run_1" … "run_5"]` with
`"total_passes": 5`. This is Finding 4's failure scenario, in the same
forty-minute window that produced the data.

### 3.1 The registered conditions, and what is at risk

Each union is read by exactly one registered condition, via its evaluation at
`outputs/h11/consensus-384-UNINTENDED-T1.0/voting/eval-t{1..5}/evaluation.json`:

| union | condition (`results/conditions-manifest.json`) | `n_passes` | `vote_threshold` | `n_detections` | F1 @ 20 m | P | R |
|---|---|---:|---:|---:|---:|---:|---:|
| `consensus_t1.geojson` | `consensus-384-t1-0::consensus-1of30` | 30 | 1 | 974 | 0.3038 | 0.2197 | 0.4920 |
| `consensus_t2.geojson` | `consensus-384-t1-0::consensus-2of30` | 30 | 2 | 616 | 0.3977 | 0.3393 | 0.4805 |
| `consensus_t3.geojson` | `consensus-384-t1-0::consensus-3of30` | 30 | 3 | 484 | 0.4331 | 0.4112 | 0.4575 |
| `consensus_t4.geojson` | `consensus-384-t1-0::consensus-4of30` | 30 | 4 | 395 | 0.4554 | 0.4785 | 0.4345 |
| `consensus_t5.geojson` | `consensus-384-t1-0::consensus-5of30` | 30 | 5 | 295 | 0.4712 | 0.5831 | 0.3954 |

**The metrics are not miscomputed — they are mislabelled, and the correct label
is already on the record elsewhere.** Each recorded `n_detections` equals the
committed union's feature count exactly, so each F1 was measured on the artefact
it names. What is wrong is the description: these are **5-pass unions at vote
thresholds 1–5** (confidence = votes/5, so `t5` is unanimity), registered as
**30-pass conditions at vote thresholds 1–5** (where `t5` would be a 1-in-6
minority).

The run's 30-pass sweep was in fact computed — as an *analysis*, never
materialised. `results/paper-eval/flash-min-text-t10-20m/consensus-analysis-report.json`
(`metadata.timestamp` 2026-03-26T12:46:10Z, `script_version` 2.0.0,
`study_dir` `outputs/h11/consensus-384-UNINTENDED-T1.0`,
`pool_selection` "first-N (preregistration Section 3.8)",
`pool_sizes: [5, 10, 30]`, `n_configurations` 45) holds all 45 sweep points in
memory-computed form. Its N=5 rows reproduce the five register conditions
exactly:

| T | analysis report F1 / `n_detections` | register condition F1 / `n_detections` |
|---:|---|---|
| 1 | 0.3038 / 974 | `consensus-1of30` 0.3038 / 974 |
| 2 | 0.3977 / 616 | `consensus-2of30` 0.3977 / 616 |
| 3 | 0.4331 / 484 | `consensus-3of30` 0.4331 / 484 |
| 4 | 0.4554 / 395 | `consensus-4of30` 0.4554 / 395 |
| 5 | 0.4712 / 295 | `consensus-5of30` 0.4712 / 295 |

So the committed `voting/` unions are the **N=5 slice of a first-N sweep**,
materialised on disk under a directory name (`voting/`) that does not say so,
while the N=10 and N=30 slices were never written out at all (the report's
per-pool optima are N=10 T=9, F1 0.4615, 319 detections; N=30 T=22, F1 0.4670,
383 detections). The register then minted five conditions from the N=5 slice and
labelled them `Nof30`.

**The same study's board cells label it correctly.** `results/e43-board-regen/summary.md`
(banner 2026-08-02; § 1) names the three cells the E72 remediation dropped from
`leaderboard-20m` / `leaderboard-30m` as "`flash-min-text-t10 N=10 N=10,
9-of-10`, `flash-min-text-t10 N=30 N=30, 22-of-30`, `flash-min-text-t10 N=5 N=5,
5-of-5`", and states that "the underlying study is
`outputs/h11/consensus-384-UNINTENDED-T1.0/`". Those are the three per-pool
optima above, and the N=5 cell — the same artefact as
`consensus-384-t1-0::consensus-5of30` — is labelled **5-of-5** there. The
register's `Nof30` is therefore not a defensible alternative convention; it
contradicts the board family derived from the same sweep.

**The numbers at risk.** Not the five F1 values in isolation, but every claim
that treats them as N=30 operating points — any vote-threshold or N-scaling
reading of this cell, and any comparison against the genuine 30-pass sweeps
(`outputs/retest/phase3a*/**/consensus/`, which all REPRODUCE here). Two
downstream artefacts carry the mislabel forward: `results/uplift-supplement/conditions.csv`
records `K=30, N=30` for all five rows (lines 43–47) with a `cost_basis` reading
"sum over N=30 proposer passes", which over-attributes the cost of a 5-pass
union by a factor of six; and `results/conditions-manifest.json` carries
`n_passes: 30` (the field this report's § 3.1 table quotes).

### 3.2 No board or paper artefact reads these unions — but the existing caveat has not propagated

**What reads them.** Searching the working tree outside `archive/`,
`consensus-384-UNINTENDED-T1.0` occurs in 272 files and `consensus-384-t1-0` in
95. Of those:

- **`docs/paper/` and `paper/`: zero hits for either string.** No paper text
  cites this run.
- **`results/leaderboard/`: one file**, and not a membership row —
  `results/leaderboard/era2/gs-era2-verified-board-2026-09-10/tiering-input/run-analyses.json`,
  where the five condition ids appear inside an `uplift-supplement-flatten`
  diagnostic's `conditions_compared` list. The live board's own
  `membership.json` has **zero** occurrences of `consensus-384` (verified
  directly), as do its `tiering_20m.md` and `README.md`. **No signed board row
  reads a stale union.**
- **`results/ci-metadata-registry.md`: no row names this run.** The one
  `UNINTENDED` row (`:100`) covers the *sibling* single-pass study
  `outputs/h11/single-pass-384-UNINTENDED-T1.0/analysis_report.json`, and
  `:302` confirms the singular ("the h11 UNINTENDED analysis report"). Contrast
  Finding 1 of the parent audit, where the registry's paper-citable designation
  was what made a defect LIVE: here it does not apply.

**Mitigation already on the record.** This cell is *already* fenced off for an
unrelated reason. Every one of the five register rows carries the note
"**E72 COVERAGE CONFOUND — do not cite this cell's 487-bounds figures**", which
records that the native data scope is the 240-tile validation pool while the
recorded evaluation scores against 487-tile Era-2 bounds, capping recall at
242/435 = 0.556 before any model behaviour is measured; it names
`results/e43-matched-temperature/` as the matched-scope replacement and the
preregistered Phase 2b sweep (`results/retest/phase2b/analysis_summary.md`) as
the paper's citable temperature evidence
(`results/run-conditions.json`, `decomposition.consensus-384-t1-0.conditions[*]._note`).
The run's own README says the same: "**must not be cited as primary evidence
for the temperature finding**" (`outputs/h11/consensus-384-UNINTENDED-T1.0/README.md`).
Erratum E72 (`docs/methodology/preregistration/protocol-errata.md:3410`) and the
2026-08-02 correction block of E43 (`:1248-1275`) carry the same disposition.
So the staleness compounds a cell already marked uncitable rather than
contaminating a live headline — and the `n_passes: 30` mislabel is a **separate**
defect from E72, not covered by that note.

**A propagation gap noticed in passing (not part of this audit's remit).**
That E72 note lives only in `results/run-conditions.json`. `results/conditions-manifest.json`
contains **zero** occurrences of "E72" and its condition schema has no note or
caveat field at all (the five rows' keys are `condition_id, run_id, label,
architecture, aggregation, proposer_pool, n_passes, vote_threshold,
prob_threshold, verifier_config, scope_override, metrics, n_detections,
n_candidates, n_reference_mounds, provenance`), and the `notes` column is empty
for all five rows of `results/uplift-supplement/conditions.csv` — the artefact
that feeds the current board's `tiering-input/`. E72's remediation item 4
(`protocol-errata.md:3448-3452`) lists "conditions-manifest coverage caveats set
for the derived conditions" among the hardening delivered. Whether that item was
satisfied by some other mechanism — the register note itself, or the deliberate
`scope_override: null` decision the register explains ("that mis-scoping IS the
defect, and overriding the field would misdescribe the recorded metrics") — is a
question for the PI, not something this report can settle. It is recorded here
because the five conditions' raw 487-bounds F1 figures travel into the board
pipeline with no caveat attached to them.

### 3.3 What was not changed, and the options

Per the brief, **no union, evaluation, or register row was touched.** The remedy
is a PI decision, and the options are now cleanly distinguishable:

1. **Relabel** the five conditions `consensus-1of5` … `consensus-5of5` with
   `n_passes: 5`, matching the label `results/e43-board-regen/summary.md`
   already uses for the same artefact, and correct `K`/`N` and `cost_basis` in
   `results/uplift-supplement/conditions.csv`. Zero compute, zero change to any
   measured value, and it makes every artefact describe what is on disk.
2. **Materialise the N=30 union and re-score.** The 30-pass sweep already
   exists as an analysis, so this adds no information — it would change five
   published F1 values in a cell already marked uncitable, and cost a
   re-derivation plus five evaluations.
3. **Rename the directory** `voting/` → `consensus-n5/`, which would make the
   sub-pool self-declaring and turn this cell SUBPOOL-CONSISTENT under the same
   rule that covers the 36 phase3a and pv-diag-384 sub-pools. Cheap, but it
   moves a path that 272 files reference.
4. **Record an erratum** beside E72 noting that the cell's five consensus
   conditions are N=5, not N=30.

Option 1 plus option 4 is the cheapest honest outcome and changes no number,
but the choice is not this report's to make.

## 4. What did NOT turn out stale

**64 unions REPRODUCE** from their whole pool and **36 are
SUBPOOL-CONSISTENT** — 100 of 106, across 83 union directories and 47 distinct
pools. In particular:

- **Every Era-1 phase3a consensus sweep is sound.** All 33 unions under
  `outputs/retest/phase3a/`, `outputs/retest/phase3a-high/`, and
  `outputs/retest/phase3a-replication/` reproduce: the 11 whole-pool unions at
  T = 18, 19, 21, 22×3, 23×3, 24, 25 over 30 passes, and the 22 `consensus-n5`
  / `consensus-n10` sub-pool unions built by
  `scripts/build_phase3_subpool_consensus.py`. These are the runs the audit's
  negative survey flagged as count-disagreements; the re-derivation confirms
  all of them are declared sub-pools, exactly as the audit suspected but could
  not show.
- **All 36 SUBPOOL-CONSISTENT unions reproduce at zero coordinate offset** from
  their declared first-N passes — 13 at N=5 of 30, 13 at N=10 of 30, and 10 at
  N=5 of 10. The first-N convention is therefore not merely documented but
  empirically the one that was used, in every instance.
- **The E57 / E70 recovery campaigns did not orphan a union.** Those campaigns
  are the mechanism behind Finding 1's 85 stale bootstrap entries and they
  rewrote passes in place under `outputs/retest/**`. No union that a registered
  condition reads is stale against a rewritten pass: 63 of the 64 REPRODUCES
  rows match at a maximum offset of exactly 0.0 m.
- **The h8-v2 / h12-v2 greedy cells and the h10 pool ladder all reproduce**,
  including the pool-reuse case (`r2-balanced` from `h10/pool_160_hp4hn4`) and
  the four gold-standard-v2 `consensus-NofM` unions, which use the older
  filename convention and carry no `voting_summary.json` at all.

### 4.1 One near-miss worth recording (not STALE, no condition affected)

`outputs/h10/evaluation-v2/pool_160_hp4hn4/consensus/consensus_t4.geojson` is
the single REPRODUCES row with a non-zero offset: 236 = 236 features, zero
unmatched, but one matched pair **0.444 m** apart. Probing the whole sweep
explains it. The same pool has two committed `voting_summary.json` records:

| threshold | pool's own `consensus/` | `h12-v2/greedy/r2-balanced/` | re-derived today |
|---|---:|---:|---:|
| T=1 | 1,454 | 1,474 | **1,474** |
| T=2 | 474 | 477 | **477** |
| T=3 | 313 | 313 | **313** |
| T=4 | 236 | 236 | **236** |
| T=5 | 163 | 163 | **163** |

The pool's own `consensus/` directory was built from a slightly **earlier** pool
state: its `consensus_t1.geojson` is short 20 clusters and 3 of its features have
no re-derived match within 1 m; `consensus_t2.geojson` is short 3. From T=3 up
the two agree, and the 0.444 m offset at T=4 is the residual trace of one
cluster's mean centroid shifting. **`consensus_t1` and `consensus_t2` in that
directory are stale**, but no registered condition reads them — the only reader
is `h10::greedy-pool-160`, which reads `consensus_t4.geojson`, and that union is
set-identical to the re-derivation. It is recorded here so that a future reader
of those two files knows, and so the near-miss is not mistaken for noise.

## 5. What was UNRESOLVED, and why

One union: `outputs/h11/pv-diag-256/consensus/text-5of5.geojson` (1,165
features), read by `pv-diag-256::text-consensus-5of5`.

It cannot be re-derived because **the pool does not exist**. The register says
so in terms: "Proposer passes were NOT materialised as `run_*` dirs (only
consensus + crops), so `proposer_pools` is empty and conditions reference the
pool by string (benign pool-unresolved; pv-384/512 precedent)"
(`results/run-conditions.json`, `decomposition.pv-diag-256._note`). Confirmed on
disk: `outputs/h11/pv-diag-256/` contains only `consensus/`, whose seven files
are `text-{1..5}of5.geojson`, `text-ge3of5.geojson`, and `text-baseline.geojson`
— no `run_*` or `pass_*` directory anywhere under it.

This is UNRESOLVED rather than STALE: with no pool, there is nothing the union
can be stale *against*, and no evidence either way. The condition is the 256 px
anchor of the tile-size comparison (F1 @ 20 m orders 256 < 512 < 384 = 0.46 /
0.69 / 0.79 per the register note), and it is also flagged there as an
"unregistered exploratory extension of the registered H11 two-level design
(E62)". If that anchor is ever cited in a way that depends on the union's
provenance, the passes would have to be recovered first — and they may not
exist anywhere.

`outputs/h11/pv-diag-256/consensus/text-baseline.geojson` was excluded from the
audit rather than marked UNRESOLVED: its condition `pv-diag-256::text-baseline`
has `architecture: single-pass`, `aggregation: none`, `n_passes: 1`, so it is
not a union.

## 6. Classification table

106 unions in 85 directories. Grouped by union directory; `T read` lists the
thresholds a registered condition actually reads (the sweep wrote every
threshold, but only these are in scope).

| union directory | unions | T read | pool passes | reflects | class |
|---|---:|---|---:|---|---|
| `outputs/gs/gold-standard-v2/consensus` | 3 | 3,4,5 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h10/evaluation-v2/pool_020_hp4hn4/consensus` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h10/evaluation-v2/pool_040_hp4hn4/consensus` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h10/evaluation-v2/pool_080_hp4hn4/consensus` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h10/evaluation-v2/pool_160_hp4hn4/consensus` | 1 | 4 | 5 | 5 of 5 | REPRODUCES (§ 4.1) |
| **`outputs/h11/consensus-384-UNINTENDED-T1.0/voting`** | **5** | **1,2,3,4,5** | **30** | **5 of 30** | **STALE** |
| `outputs/h11/e47-propose-brief/flash-high-text-n5/propose_brief-text/consensus` | 5 | 1,2,3,4,5 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h11/n1-outstanding-384/brief-text-t03/consensus` | 3 | 1,2,3 | 3 | 3 of 3 | REPRODUCES |
| `outputs/h11/n1-outstanding-384/image-t0/consensus` | 3 | 1,2,3 | 3 | 3 of 3 | REPRODUCES |
| `outputs/h11/n1-outstanding-384/image-t03/consensus` | 3 | 1,2,3 | 3 | 3 of 3 | REPRODUCES |
| `outputs/h11/n1-outstanding-384/pro-image-high-t0/consensus` | 3 | 1,2,3 | 3 | 3 of 3 | REPRODUCES |
| `outputs/h11/n1-outstanding-384/pro-text-high-t0/consensus` | 3 | 1,2,3 | 3 | 3 of 3 | REPRODUCES |
| `outputs/h11/pv-diag-256/consensus` | 1 | 5 | — | — | UNRESOLVED |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/consensus` | 2 | 1,3 | 3 | 3 of 3 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/consensus` | 1 | 9 | 10 | 10 of 10 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/consensus-n5` | 1 | 5 | 10 | 5 of 10 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/consensus` | 1 | 7 | 10 | 10 of 10 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/consensus-n5` | 1 | 3 | 10 | 5 of 10 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/consensus` | 1 | 6 | 10 | 10 of 10 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/consensus-n5` | 1 | 4 | 10 | 5 of 10 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/consensus` | 1 | 3 | 3 | 3 of 3 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3/consensus` | 1 | 10 | 10 | 10 of 10 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.3/consensus-n5` | 1 | 5 | 10 | 5 of 10 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/consensus` | 1 | 26 | 30 | 30 of 30 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/consensus-n10` | 1 | 9 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/consensus-n5` | 1 | 5 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0/consensus` | 1 | 9 | 10 | 10 of 10 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t1.0/consensus-n5` | 1 | 5 | 10 | 5 of 10 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.0/consensus` | 1 | 3 | 3 | 3 of 3 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3/consensus` | 1 | 10 | 10 | 10 of 10 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.3/consensus-n5` | 1 | 5 | 10 | 5 of 10 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/consensus` | 1 | 29 | 30 | 30 of 30 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/consensus-n10` | 1 | 10 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/consensus-n5` | 1 | 5 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0/consensus` | 1 | 9 | 10 | 10 of 10 | REPRODUCES |
| `outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t1.0/consensus-n5` | 1 | 5 | 10 | 5 of 10 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/image-n5/image-t0.3/consensus` | 1 | 10 | 10 | 10 of 10 | REPRODUCES |
| `outputs/h11/pv-diag-384/image-n5/image-t0.3/consensus-n5` | 1 | 5 | 10 | 5 of 10 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/image-n5/image-t0.7/consensus` | 1 | 8 | 10 | 10 of 10 | REPRODUCES |
| `outputs/h11/pv-diag-384/image-n5/image-t0.7/consensus-n5` | 1 | 4 | 10 | 5 of 10 | SUBPOOL-CONSISTENT |
| `outputs/h11/pv-diag-384/image-n5/image-t1.0/consensus` | 1 | 8 | 10 | 10 of 10 | REPRODUCES |
| `outputs/h11/pv-diag-384/image-n5/image-t1.0/consensus-n5` | 1 | 4 | 10 | 5 of 10 | SUBPOOL-CONSISTENT |
| `outputs/h12-v2/greedy/r1-hn-heavy` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h12-v2/greedy/r2-balanced` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h12-v2/greedy/r3-hp-heavy` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h8-v2/greedy/canonical` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h8-v2/greedy/plus-hp` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h8-v2/greedy/pure-positive-canon` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h8-v2/greedy/scale-4` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h8-v2/greedy/scale-8` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h8-v2/greedy/scale-16` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/h8-v2/greedy/scale-32` | 1 | 4 | 5 | 5 of 5 | REPRODUCES |
| `outputs/retest/phase3a-high/track2-text/T0.3/consensus` | 1 | 23 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a-high/track2-text/T0.3/consensus-n10` | 1 | 8 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a-high/track2-text/T0.3/consensus-n5` | 1 | 4 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a-high/track2-text/T0.7/consensus` | 1 | 22 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a-high/track2-text/T0.7/consensus-n10` | 1 | 7 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a-high/track2-text/T0.7/consensus-n5` | 1 | 4 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a-high/track2-text/T1.0/consensus` | 1 | 23 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a-high/track2-text/T1.0/consensus-n10` | 1 | 8 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a-high/track2-text/T1.0/consensus-n5` | 1 | 4 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a-replication/high/consensus` | 1 | 21 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a-replication/high/consensus-n10` | 1 | 8 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a-replication/high/consensus-n5` | 1 | 4 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a-replication/minimal/consensus` | 1 | 25 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a-replication/minimal/consensus-n10` | 1 | 8 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a-replication/minimal/consensus-n5` | 1 | 4 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track1-image/T0.3/consensus` | 1 | 22 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a/track1-image/T0.3/consensus-n10` | 1 | 8 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track1-image/T0.3/consensus-n5` | 1 | 4 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track1-image/T0.7/consensus` | 1 | 18 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a/track1-image/T0.7/consensus-n10` | 1 | 7 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track1-image/T0.7/consensus-n5` | 1 | 4 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track1-image/T1.0/consensus` | 1 | 19 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a/track1-image/T1.0/consensus-n10` | 1 | 7 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track1-image/T1.0/consensus-n5` | 1 | 4 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track2-text/T0.3/consensus` | 1 | 23 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a/track2-text/T0.3/consensus-n10` | 1 | 8 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track2-text/T0.3/consensus-n5` | 1 | 5 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track2-text/T0.7/consensus` | 1 | 24 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a/track2-text/T0.7/consensus-n10` | 1 | 8 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track2-text/T0.7/consensus-n5` | 1 | 4 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track2-text/T1.0/consensus` | 1 | 22 | 30 | 30 of 30 | REPRODUCES |
| `outputs/retest/phase3a/track2-text/T1.0/consensus-n10` | 1 | 7 | 30 | 10 of 30 | SUBPOOL-CONSISTENT |
| `outputs/retest/phase3a/track2-text/T1.0/consensus-n5` | 1 | 4 | 30 | 5 of 30 | SUBPOOL-CONSISTENT |

## 7. Limits of this check

- **Only unions a registered condition reads.** 868 union-named GeoJSONs
  (`consensus_t*`, `consensus-NofM`) sit directly under an
  `outputs/**/consensus/` directory and are git-tracked, out of 914 tracked
  `.geojson` files in those directories; 1,403 union-named files are tracked
  anywhere under `outputs/`. **106** are in scope here. A union that nothing in
  `results/conditions-manifest.json` reads was not checked, as the brief
  directs. Sibling thresholds inside a checked directory were not checked
  either — § 4.1 is the one case where a probe found stale siblings, and it
  suggests a full-directory sweep would find more.
- **Proposer-verifier conditions were reached only where the chain is
  recorded.** 273 of the 542 conditions are proposer-verifier; their candidate
  universe is a consensus union, but the artefacts record the verifier's
  accepted set, not the union behind it. Where a PV condition's evaluation
  named a union directly it is in scope; otherwise the union is upstream of the
  recorded chain and outside this check. Those unions are, however, largely the
  same `pv-diag-384` and `phase3a` unions checked here.
- **WBF and greedy-variant aggregations are out of scope** (10 `wbf_vote*`
  unions read by registered conditions), as is the `diversity-consensus` tree.
  They have the same structural exposure and a different builder.
- **The comparison is spatial, not property-level.** Two unions with identical
  point sets but different `confidence` or `contributing_passes` values would
  both pass. For the STALE cell that difference is material — a 5-pass `t5`
  carries `confidence: 1.0`, a 30-pass `t5` would carry 0.167 — and was checked
  by hand there, but it is not part of the automated verdict.

## 8. Reusable artefacts

- `scripts/check_union_provenance.py` — `--union PATH` for one union,
  `--all` for every union a registered condition reads; `--json-out` for the
  machine-readable result; exits 1 if any union is STALE, so it can gate a
  pipeline. Writes only to `--scratch-dir`.
- `tests/test_check_union_provenance.py` — 11 tier-1 tests on a synthetic
  pool, covering both failure modes: a pool that grew after the union was
  written, and a pass rewritten in place at an unchanged pass count (the case
  `total_passes` cannot see).
- `results/union-staleness-retrospective-2026-09-12.json` — the full 106-row
  result this report tabulates.

## Changelog

### 2026-09-12 (later) — the PI's rulings on § 3.3 and § 4.1 executed

**Trigger**: the PI ruled on this report's two open dispositions. For § 3.3, on
**option 1 plus option 4** — relabel the five conditions and record an erratum,
changing no measured value. For § 4.1's near-miss, **rebuild and archive**.

**What landed, § 4.1 (the h10 near-miss).** The two stale siblings
`outputs/h10/evaluation-v2/pool_160_hp4hn4/consensus/consensus_t{1,2}.geojson`
were archived to `archive/superseded-consensus-2026-09-12/h10-pool_160_hp4hn4/`
with a README recording the diagnosis, and rebuilt from the full five-pass pool
with the current `scripts/merge_passes.py`, which now writes a
`pass_provenance` block with a `git_blob_hash` per pass.

| union | committed (stale) | rebuilt | § 4.1's predicted re-derivation |
|---|---:|---:|---:|
| `consensus_t1.geojson` | 1,454 | **1,474** | 1,474 |
| `consensus_t2.geojson` | 474 | **477** | 477 |
| `voting_summary.json` | `{total_passes, thresholds}` | + `pass_provenance_schema`, `pass_ids`, `pass_provenance` | — |

The rebuild reproduces § 4.1's predicted counts exactly. **No registered
condition reads either file** — re-verified this session across
`results/run-conditions.json`, `results/conditions-manifest.json` and `results/`
generally — so no registered number moved.

**What did NOT change there, and why it is a question rather than an omission.**
`consensus_t3/t4/t5.geojson` were **not** rebuilt. They reproduce at identical
counts (313 / 236 / 163), so none is stale in the sense `t1` and `t2` were; but
`consensus_t4.geojson` is the detections file of the registered condition
`h10::greedy-pool-160`, and § 4.1 records that its re-derivation differs by one
matched pair **0.444 m** apart. Rewriting a registered condition's detections
file for a 0.444 m centroid shift is a PI decision, so it was left and is put
back. Consequence stated plainly: the installed `voting_summary.json` carries the
rebuild's provenance and truthful threshold counts, while `t3`–`t5` on disk are
the original build of the same five passes.

**What landed, § 3.3 (the five stale T = 1.0 unions).** Option 1 + option 4, as
ruled — the relabel, its propagation through the generated manifests and the
uplift supplement, and the erratum. The artefacts themselves are unchanged: no
union, evaluation, or measured value was touched. Details and the before→after
figures are in `reports/k-ladder-closeout-deltas-2026-09-12.md`.

### 2026-09-12 — Original publication

**Trigger**: the Principal Investigator's retrospective queued against
Finding 4 of `reports/name-keyed-cache-audit-2026-09-12.md:261-292`, whose
attempted demonstration was negative (37 of 151 count-disagreements, all
legitimate sub-pools) and which named re-derivation on sapphire as the only
decisive test. Pull request #14 having fixed the defect forward, this report
settles the existing corpus.

**Initial state**: 106 committed consensus unions read by 106 registered
conditions, re-derived on sapphire (1 m 11 s wall, 16 workers) and classified
64 REPRODUCES / 36 SUBPOOL-CONSISTENT / 5 STALE / 1 UNRESOLVED. The five STALE
unions are `outputs/h11/consensus-384-UNINTENDED-T1.0/voting/consensus_t1..t5.geojson`,
which reflect the first 5 of a 30-pass pool while their register rows declare
`n_passes: 30`; § 3.1 corroborates the N=5 reading against
`results/paper-eval/flash-min-text-t10-20m/consensus-analysis-report.json` and
the correct 5-of-5 label against `results/e43-board-regen/summary.md` § 1.
§ 3.2 records that no signed board row or paper text reads any of the five, and
notes in passing that the E72 caveat present in `results/run-conditions.json`
does not appear in `results/conditions-manifest.json` or
`results/uplift-supplement/conditions.csv`. One near-miss recorded at § 4.1
(`outputs/h10/evaluation-v2/pool_160_hp4hn4/consensus/`, stale `t1`/`t2`
siblings, read by nothing). No committed union, evaluation, or register row was
modified.

**Landed in**: `scripts/check_union_provenance.py` and
`tests/test_check_union_provenance.py` at commits `056a1ef78` and `55ebfe6db`;
this report and `results/union-staleness-retrospective-2026-09-12.json` at the
commit that adds them.
