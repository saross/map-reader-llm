# Defect register — Session 136 (2026-08-18)

> **Last revised**: 2026-08-19 (D17 and D18 added and fixed, both found while
> filing E82; E82 filed). See [§ Changelog](#changelog).

**What this is.** A single tracked list of every defect surfaced during
Session 136, with status and the fix each one needs. The session produced
three errata and four analysis reports, and the defects ended up spread
across all of them plus conversation. This register is the working list;
the errata remain the canonical protocol-facing disclosures.

**What this is not.** A findings document. Each entry points at the
artefact that carries the evidence rather than restating it.

**Status vocabulary**: `RECORDED` — disclosed, no code change intended.
`OPEN` — needs a fix. `FIXED` — corrected, with the commit.
`CLEARED` — investigated and found not to be a defect.

## Protocol-facing (errata carry the canonical disclosure)

| # | Defect | Where | Status |
|---|---|---|---|
| D1 | Order-dependent tile assignment: `evaluate_detections.py` books a detection to the FIRST intersecting bounds tile, which depends on row order. ~0.01 F1 on 123 conditions. | E79 | RECORDED — fix is a PI decision |
| D2 | No within-pass deduplication in the scoring path, so two scoring paths coexist; 155 of 333 conditions affected. Preregistration-compliant, but cross-path comparisons are confounded. | E80 | RECORDED — correction campaign in `dedup-correction-worklist-2026-08-18.md` |
| D3 | Undefined tile-level MCC published as `0.0` (9 conditions), plus 4 more depressed by averaging an undefined pass into a mean. Originates in a mathematically false registered claim at `preregistration.md:392`. | E81 | RECORDED — correction OPEN, see D4/D5 |
| D19 | Bootstrap CIs depart from Decision 10 on **method** (BCa substituted for the registered percentile method in `2026999ad`, 2026-04-30, undisclosed) and on **iteration count** (1,583 evaluations at B=10,000 against 114 at B=1,000, inverting E54's recorded split). PI ruled 2026-08-19 to standardise on 10,000 and disclose. | E82 | RECORDED — re-emission proceeds by campaign; E54 carries a correction block pointing at E82 |

## Open code defects

| # | Defect | Location | Fix needed |
|---|---|---|---|
| **D15** | **CRITICAL — the BCa bootstrap wrapper transposes its axes**, computing `n` statistics of `B` draws each instead of `B` statistics of `n` draws. Every interval on the BCa path is too narrow by roughly `sqrt(B/n)`: measured **1.66×** at B=1,000 and **5.50×** at B=10,000 on a real published cell. 1,520 committed evaluations used B=10,000. Point estimates are unaffected; the `percentile_fallback` path, permutation tests, and this session's paired bootstraps are all unaffected. Because the registered significance rule is "the 95 % CI excludes zero", the error runs towards **false positives**. | `lib_advanced_metrics.py`, `_bca_ci_from_indices` (the `np.moveaxis` in the vectorised wrapper) | **FIXED and DISCLOSED 2026-08-19** — code fix `122104b8a`; disclosed as E82 disclosure 2. Corrected characterisation: width is rescaled by `sqrt(n/B)`, so intervals are too narrow only when `B > n` (69,663 intervals); **840 sit at `B < n` and are too WIDE**. **Zero published significance verdicts change** — Decision 10's rule is on *difference* CIs, and the defective wrapper is reachable only from single-condition ones. Re-emission of committed intervals remains OPEN, by campaign. Full working in `reports/bca-axis-defect-2026-08-18.md`. |
| D4 | `_safe_round` returns `0.0` for an undefined MCC; `aggregate_runs` averages those zeros into multi-run means. | `evaluate_detections.py:533-535`, `:752-788` | Emit `null`, and average over defined passes only. Re-emit the 13 affected conditions. |
| D5 | `bootstrap_tile_classification_ci` documents degenerate resamples as "treated as `NaN` and skipped" but returns `0.0`. Every tile-MCC CI lower bound of exactly `0.0000` on the affected cells is that substitution, not a percentile. | `lib_advanced_metrics.py:2034-2036` (docstring) vs `:2087-2091` (code) | Make code and docstring agree; skip degenerate resamples. |
| D6 | Two detection-file naming conventions coexist. Any `detections_*` glob silently under-reads a mixed pool. | `evaluate_detections.py`; `scoring_sensitivity_survey.py`; 24 further sites | **FIXED** — `scripts/lib_detection_paths.py` + 30 sites migrated (`6b1cb87af`, `4c44e3fd6`, `6fa658877`, `8e59c9555`). Repo guard green; tier-1 suite 1,479 passed. |
| D6a | **Found by the audit of D6's fix.** Adding a package-qualified import to `lib_consensus.py` — which previously had no project import at all — broke **8 scripts at import time**; `n1_baseline_leaderboard_tiering.py` was unrunnable as documented. Invisible to tests because `pytest.ini` sets `pythonpath = "."`. | `lib_consensus.py`, `n1_baseline_leaderboard_tiering.py` | **FIXED** — dual-mode import; all 9 scripts verified running. |
| D6b | **Found by the audit of D6's fix.** The exclusion filter was dead code: every filename reaching it had already matched the glob, so its stem was always `"detections"`. Meanwhile 24 real non-passes DO begin `detections_` — verifier threshold outputs and this session's `detections_dedup.geojson`, the latter inside `run_<N>` directories. | `lib_detection_paths.py` | **FIXED** — strict per-convention regexes, corpus-validated. |
| D6c | **Found by the audit of D6's fix.** The tests validated the resolver's interior and nothing the defect broke: reverting the migration at all four call sites left 1,489/1,489 tier-1 tests green, and the migrated functions were executed by no test. | `tests/test_lib_detection_paths.py` | **FIXED** — 7 caller-wiring tests; verified to fail under a reverted migration. |
| D7 | A parsed detection lacking a `box_2d` key is counted by the results tracker but silently skipped when features are built — no log, unlike the malformed-length branch immediately below it. Cost one detection in H13 arm B run_2 (meta 1,362 vs GeoJSON 1,361). | `4_detect_mounds_batch.py` | **FIXED** — the skip is now logged (`4_detect_mounds_batch.py:614-628`) and the tracker reconciled with the emitted feature count (`d0a709059`). Historical metadata still carries the discrepancy. |
| D8 | `pro-medium-image-baseline` provenance mismatch: the crop manifest cites 519 candidates from a raw pass that now holds 587 features. Three `gs-era2` rows depend on it. | `outputs/h11/pv-diag-384/pro-medium-image-baseline/` | **CLEARED** — the gap is recovery commit `c07c57766` (2026-06-03, E57/Obs 339) appending 68 detections to a pass whose crops were cut 2026-03-24. Append is prefix-preserving, the manifest aligns exactly, and all three `gs-era2` rows reproduce their accept counts. **Not** a D6 artefact: 587 is a single-file count; the three-pass total is 1,675. `provenance-d8-2026-08-18.md` |
| D12 | `execution_stats.parse_failures` reads `0` and `finish_reason_counts` records unbroken success on the six 2026-08-18 grid passes that each lost a tile to a JSON-parse failure. The counter was driven by whether the API *envelope* parsed, not the JSON body. `items_failed` and the `.tiles.json` `failed` array are the reliable record. | `lib_llm_metadata.py`; `4_detect_mounds_batch.py` | **FIXED** in the writer — `log_failure` now takes a category and attributes to the right counter (`d0a709059`). **RECORDED** for historical metadata, which still carries it: read `<pass>.tiles.json` `failed` and `execution_stats.items_failed`, never `parse_failures`, when auditing pre-`d0a709059` runs. |
| D13 | Recorded `cost_estimate` blocks are at **list price** and overstate actual billing by ~2×: Gemini real-time flex carries the same 50 % discount as the async Batch API, but only the batch path applied one. Metadata therefore disagreed with the audited `pareto_v2.json` model by exactly 2× with nothing in either artefact to say which was right. | `lib_llm_metadata.py:1079` (`FLEX_DISCOUNT`), `:1084` (`BATCH_API_DISCOUNT`) | **FIXED** in the writer — the discount is now a parameter of the cost model; `total_cost_usd` records the billed amount alongside `list_total_cost_usd` and an explicit `cost_basis` (`d0a709059`). **RECORDED** for historical metadata: absence of `cost_basis` marks the old list-price convention. All 46 `outputs/grid-2026-08-18/**/*.meta.json` blocks are on it — a recorded $37.06 is ≈ $18.53 billed. Never re-derive a spend figure from pre-`d0a709059` metadata without halving it. |
| D14 | Crop manifests record `source_geojson` as a bare mutable path with no content hash, commit, or timestamp, so a source regenerated after extraction leaves the manifest silently describing an artefact that no longer exists at that path. Three cells corpus-wide are affected: `pro-medium-image-baseline` (519→587), `pro-medium-text-baseline` (430→446, same commit `c07c57766`), and `flash-high-image-n5/image-t0.0/verified-v1-n10` (802→889, `f6116cba0`/`77bb342b4`). This is what made D8 look like corruption. | `extract_candidates.py:396-410` | Anchor the manifest to its source (content hash or git commit). Until then, annotate the affected cells' provenance. Sweep basis: 203 manifests, 104 exact, 91 k-of-N by design, 4 anomalies, 4 dangling — `provenance-d8-2026-08-18.md` § 6. |
| D17 | **FOUND AND FIXED 2026-08-19.** `_metrics_from_eval` took `n_iter: int = 10000` as a default and its only caller never overrode it, so every manifest condition was stamped with the project standard whatever its source ran. **49 of 333 conditions published `n_iter: 10000` where the source evaluation declared 1,000**, and 16 adapter-written cells with no bootstrap block were stamped too. Same class as the hard-coded `_metadata.bootstrap.method` literal D15 flagged: a recorded parameter that is not evidence of anything. Point estimates untouched. | `scripts/generate_post_run_report.py:677` (`_metrics_from_eval`), `:816` (caller) | **FIXED AND DISCHARGED 2026-08-19** — two parts. (a) Code: parameters now read from the source `_metadata.bootstrap`; undeclared parameters are omitted rather than filled. (b) Data: all 49 register-backing evaluations below 10,000 were replayed at 10,000 (`scripts/rerun_evals_at_10k.py`), and the 16 percentile cells that had always run at 10,000 now declare it via their adapters. **All 337 conditions declare `n_iter = 10 000`; zero point estimates moved** (gated at 1e-9). 46 intervals widened, 3 narrowed, ratios tracking `sqrt(B_old/n)`. Report: `results/bootstrap-10k-restandardisation.json`. Three tier-1 regression tests. |
| D18 | **FOUND AND FIXED 2026-08-19.** E81's corrections were hand-applied to the generated manifests and taught to neither the generator nor the schema. Two consequences. (a) The committed `results/conditions-manifest.json` **failed its own schema on 26 counts across 13 conditions** (`mcc_n_runs`, `mcc_n_runs_defined`, `mcc_undefined_reason`, `provenance.e81_correction` all forbidden by `additionalProperties: false`). (b) Regeneration silently **reverted** every one of them, including the `[REVISED … erratum E81]` outcome text in the analyses manifest, whose hand-authored source `run-analyses.json` never carried it. Nothing caught this because the generator reports ALL VALID over rows it has just built, never over the committed artefact. | `docs/manifest-schemas/{conditions-manifest,common-defs}.schema.json`; `scripts/generate_post_run_report.py`; `results/run-analyses.json` | **FIXED** — schema extended for the four fields; generator derives them from the source evaluation (the reason string names the marginal that actually vanished rather than assuming TN+FN); E81's outcome text ported into `run-analyses.json`. Regeneration is now idempotent and reproduces E81 exactly: 0 drift in tile-classification, provenance, and point estimates. Four tier-1 tests, including one that validates each **committed** manifest against its schema, closing the gap that hid this. |

## Open documentation and reporting defects

| # | Defect | Location | Fix needed |
|---|---|---|---|
| D9 | H13 cost-efficiency figures are reported on the UNDISCOUNTED basis. Gemini real-time flex carries a 50 % discount, so `$5.7488` total and the F1-per-dollar values (0.4069 / 0.2975 / 0.1007) are about 2× actual. Ratios and the "every additional dollar buys negative F1" conclusion are unaffected, because all arms share one basis. | `results/h13-overlap-2026-08-18/findings.md` § Analysis 2 | Halve the dollar figures, state the basis explicitly, add a changelog entry. |
| D16 | **WAS blocked by D15, now unblocked** (the code fix landed in `122104b8a`). Writing the row still needs per-cell evaluations generated at B=10,000 per the 2026-08-19 PI ruling. **D15 blocks the grid's register row.** `results/grid-2026-08-18/` has no per-cell `evaluation.json` (its metrics are computed directly in `grid_analysis.py`), so its four cells cannot be registered as conditions — and the analyses schema requires a non-empty `conditions_compared`. Generating those evaluations means running `evaluate_detections.py`, which always computes bootstrap CIs with no option to skip them, so it would write four fresh intervals already known to be 1.7-5.4x too narrow. Recording the row was attempted and reverted to keep the register valid. | `results/grid-2026-08-18/`, `results/run-analyses.json` | **FIXED 2026-08-19** — `scripts/grid_materialise_conditions.py` rebuilds each cell's published best-F1@20 m point at K=10, writes it with E79 tile assignment against the common carrier, and scores it at **B=10,000** per E82. All four reproduce their published sweep F1 to < 5e-4. Run `grid-2026-08-18` registered (33 runs), four conditions minted (337), analysis row `grid-tilesize-overlap-2026-08-18` recorded (37) — **ALL VALID, zero drift in any pre-existing condition**. The grid's paired contrasts were also re-run at 10,000: every delta identical, every verdict unchanged, CI widths 0.95–1.03x. The runs schema now permits a null `tile_size_px` for a run that varies tile size across its own conditions. |
| D11 | `results/scoring-sensitivity-2026-08-18/exposure-survey.json` was produced while the under-read was live, so `pv-diag-384::baseline-pro-{text,image}-medium-t-0-0` were scored on 1 pass of 3. Re-running now resolves 3 each. The exposure classifications are unchanged, but the recorded per-cell numbers for those two conditions are wrong. | `results/scoring-sensitivity-2026-08-18/` | **FIXED 2026-08-19** — survey re-run at $0 on sapphire against the D6-fixed resolver. Both conditions now read 3 artefacts: text 446 → 1,356 features, `duplicate_fraction` 0.2130 → **0.2279**; image 587 → 1,675, 0.2249 → **0.2185**. **Every exposure classification and summary count is unchanged** (155 dedup-exposed, 123 tie-break, 6 both, 0 unresolved), so the correction worklist is unaffected. Superseded survey archived to `archive/superseded-scoring-surveys/`. |
| D20 | **Tier 1 can understate the leader's tie set, and does on the paper's headline board.** `greedy_clique_tiers` walks conditions in F1-descending order and closes the tier at the FIRST BH-significant condition, so a marginal result immediately below the leader shuts Tier 1 before lower-ranked, non-separable conditions are considered. Its docstring promises `tiers[0]` IS "the leader's clique"; that promise fails. On `era1-leaderboard` the rank-2 cell is significant at **BH p = 0.048** and closes Tier 1 at one member, while **five** further cells are non-significant against the leader and mutually non-significant — the leader's true clique has **6** members, verified with 0 violating pairs. The register therefore publishes a **SOLE Tier-1 leader** (`tie_set` = 1) and the outcome text reads "proposer-verifier is the single best Era-1 architecture ... clear of the HIGH-consensus cluster (Tier 2)", when three independent instruments disagree: the artefact's own pairwise tests (5 non-separable), the true clique (6), and MCB at simultaneous 95 % (**15 of 82**). **3 of 11 tiering artefacts are affected, all of them the era1-leaderboard board**; the other 8 are unaffected because no marginal result sits at rank 2. | `scripts/n1_baseline_leaderboard_tiering.py:383` (`greedy_clique_tiers`); `results/era1-leaderboard/tiering_20m.json`; two `results/dedup-metric-impact-2026-08-18/tiering-era1-leaderboard-*.json`; register row `era1-leaderboard` | **RESOLVED 2026-08-19, PI-approved** — `tie_set` replaced by the Hsu MCB admissible set at simultaneous 95 % on **8 boards** (era1-leaderboard 1→10; era1-single-pass 20→15; h12-v2 3→6; pass-budget-pareto 5→3; -v2 7→6; min-vs-high-thinking-pv 6→5; flash35-model-roles 2→3; verifier-robustness 5→5). Direction is not uniform, which is why the instrument was replaced rather than patched. Tiers below the first are RETAINED as descriptive rank bands per PI direction. **6 boards not recomputable** (2 with cells lacking `detections`/`detections_dir`; 4 Track-2 55-map boards with composite ground truth) and remain on the superseded instrument, disclosed. MCC computed alongside F1, with the derivation verified against a committed `tile_classification` block and E81's 13 undefined conditions dropped rather than read as 0.0. Disclosed as **E83**; superseded `greedy_clique_tiers` retained so published boards stay reproducible as published. |
| D21 | **`uuid` is not a unique key in the 55-map student reference, and reads as one.** `inputs/vectors/references/student-mounds-55maps-reviewed.geojson` carries **4,746 records over 839 distinct `uuid` values**, one repeated **1,152** times; the standardised layer inherits it (4,731 over 836). Geometries are all distinct, so these are genuine separate features whose identifier simply does not identify them — any join, dedup, or provenance trace keyed on `uuid` silently collapses records. Not introduced by standardisation; upstream in the digitisation. | `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`; `results/deployment-oracle-2026-06-06/canonical-gt/standardised/student-mounds-55maps-standardised.geojson` | **RECORDED** — the new merged reference keys positionally (`gt_id`) and retains `uuid` as a non-key `source_id`. No published number is known to depend on a `uuid` join, but that has not been audited; audit before any future work keys on it. |
| D22 | **`cell_per_tile` could not reproduce any cell scored through `--batch`.** In batch mode `cli_args` records the BATCH-level invocation, so `detections` and `detections_dir` are both null and the per-cell input sits in `_metadata.input_files.detections` instead. 18 cells across `n1-baseline-matrix-384` and `diversity-dividend-384` were unreproducible from the committed record, which is why neither board could be re-tiered under E83 on the first attempt. | `scripts/era1_leaderboard_tiering.py` (`load_cells`) | **FIXED 2026-08-19** — additive fallback to `input_files.detections`, firing only where the loader would otherwise raise. All 18 cells now reproduce their committed eval F1 to \|gap\| <= 0.0005. Both boards re-tiered. |
| D23 | **Tile-level MCC has three silent traps and no explanatory documentation**, one of which produced a wrong-but-plausible value during E83 work (0.898 against a committed 0.790): detections are booked to one tile by nearest centroid while references are booked to every tile they intersect, so reference occupancy cannot be derived from the detection-level FN column. The other two: an undefined MCC is not a zero (E81), and MCC is not comparable across tilings because the carrier tiles ARE its classification units. | `docs/methodology/tile-mcc-explained.md`; `scripts/lib_advanced_metrics.py` (`calculate_tile_classification`) | **DOCUMENTED 2026-08-19** — `docs/methodology/tile-mcc-explained.md` written for reviewers and reusers. Code unchanged; the canonical function was always right. |
| D24 | **The MCB critical value is a tile-level bootstrap, not Dunnett's tabulated one**, and the substitution is unverified. Hsu's construction assumes normal homoscedastic means; micro-F1 and tile-MCC over correlated tiles are neither, so the table cannot be used directly and a bootstrap analogue was substituted. It is well-motivated but has not been checked for coverage, and it now sits under **ten** re-tiered register rows (E83). | `scripts/selection_aware_intervals.py` (`run`, the `w_upper` / `w_lower` quantiles) | **OPEN — follow-up before submission.** Needs either a coverage simulation under known truth or a statistician's review. The direction of any error is unknown; the two-sided band computed alongside is strictly more conservative and brackets it from above. |
| D10 | The grid runs' auto-written `experiment_intent.md` records hypothesis `H1` and "factor being varied: `include_example_images`", inherited from `detect_brief-text.json`. Wrong for a geometry grid, and it lands in provenance. | `outputs/grid-2026-08-18/**/experiment_intent.md` | Correct in the register row and post-run report rather than forking the config. |

## Near-misses

| # | Event | Outcome |
|---|---|---|
| N1 | `git stash -u` on sapphire swept the untracked `inputs/tiles_384_ov192` tile tree (5,284 files) — the input the grid's 384/50 % cell cannot be re-scored without. Untracked-by-design trees are invisible to the usual safety habits, and `git clean -fd` would do the same. | **RECOVERED** from `stash@{0}^3` during the session-close residue sweep; verified to reproduce the committed manifest exactly (1,398 of 1,760 tiles, identical set). **UPDATE 2026-08-19 (N1b)**: an inventory taken while running Phase 0.3 found the hazard had already fired twice more, unrecorded. `inputs/tiles_512_ov128` and `inputs/tiles_512_ov256` hold **zero PNGs** on sapphire — the directories survive carrying only manifests (3 files and 1 file respectively). Neither is needed for Phase 0, so nothing this session was affected, but **Phase 2 of the recall-levers programme cannot run until they are regenerated** ($0, deterministic, then checked against `inputs/grid-2026-08-18/grid_512_ov*_manifest.json`). Inventory and regeneration commands are in `planning/recall-levers-programme-2026-08-19.md` § Machine state. |

## Cleared — investigated, not defects

| # | Suspicion | Outcome |
|---|---|---|
| C1 | Calibration tiles leaking into the 512 px evaluation scope | **CLEARED.** Tile-level intersection is 0. The 38.8 % area sharing is the inherent overlap-band geometry of a 12.5 % tiling and sits below the 43.7 % median share an eval tile has with its own neighbours. `scoring-audit-notes-2026-08-18.md` |
| C2 | The naming split contaminating committed results | **CLEARED for committed results.** 156 glob-based evaluations audited, 0 under-reads. The hazard remains live for new code — see D6. |
| C3 | Six consensus conditions flagged as un-deduplicated | **CLEARED — a mislabel.** 0 of their 193 residual within-20 m pairs share a contributing pass, so deduplication demonstrably ran; the residual is cross-pass clustering drift. |

## See also

- **Preceding experiment(s)**: `results/h13-overlap-2026-08-18/findings.md` — the H13 scoring chain whose phase gate first surfaced D2.
- **Follow-up experiment(s)**: None yet — the tile-size × overlap grid is in flight and will inherit D6's resolver once fixed.
- **Run output directory**: `outputs/grid-2026-08-18/` (grid proposer passes, in flight).
- **Working-notes Observations**: None yet — an entry covering the scoring-path family is pending the correction campaign.
- **Investigation reports**: `reports/provenance-d8-2026-08-18.md` — D8's full working, and the corpus sweep behind D14.
- **Decisions / Errata**: E79, E80, E81 — the three protocol-facing disclosures from this session. E75 — H13's disposition, which carried D2's mechanism before E80 took it over. E57 — the 2026-06-03 resume-merge recovery that D8 turned out to be.

## Changelog

### 2026-08-19 (latest) — E82 filed and executed; D11, D15, D16, D17 fixed; D18, D19 added

**Trigger**: filing erratum E82 for the bootstrap deviations, which required an
independent recount of the committed corpus and surfaced two further defects in
the manifest generator.

| Row | Before | After |
|---|---|---|
| D15 | VERIFIED, NOT FIXED; "every BCa interval too narrow" | FIXED (`122104b8a`) and disclosed as E82; too narrow only where `B > n` (69,663), **too wide** where `B < n` (840); zero published verdicts change |
| D16 | blocked by D15 | **FIXED** — four cells materialised, scored at B = 10,000, and registered; register now 33 runs / 337 conditions / 37 analyses, all valid |
| D17 | not known | **FIXED AND DISCHARGED** — declaration bug fixed, then all 49 evaluations re-run at 10,000; all 337 conditions now declare it, zero point drift |
| D18 | not known | **FIXED** — committed conditions-manifest failed its own schema on 26 counts; regeneration reverted E81 |
| D19 | not known | RECORDED via E82 — BCa and 10,000 iterations both depart from Decision 10 |
| D11 | OPEN — $0 re-run | **FIXED** — survey re-run on the full pools; per-cell counts corrected, every exposure classification unchanged |
| D20 | not known | **RESOLVED** — 10 boards re-tiered to Hsu MCB and disclosed as E83; 4 (55-map) still pending a scorable reference |
| D21 | not known | **RECORDED** — `uuid` is not unique in the 55-map student reference (4,746 records / 839 uuids) |
| D22 | not known | **FIXED** — batch-mode cells were unreproducible; fallback added, 2 boards recovered |
| D23 | not known | **DOCUMENTED** — tile-MCC traps written up after one produced a wrong-but-plausible value |
| D24 | not known | **OPEN** — MCB bootstrap critical value unverified against Dunnett; flagged for follow-up |
| N1 | one tree swept, recovered | **N1b added** — two more untracked tile trees found empty on sapphire (`tiles_512_ov128`, `tiles_512_ov256`); blocks recall-levers Phase 2 until regenerated |

**What did NOT change**: no point estimate, no F1, precision, recall, or tile-MCC
value moved. Regeneration after the D17/D18 fixes reproduces every committed
tile-classification block and every provenance block exactly; only the 871 CI
parameter blocks D17 was mis-stamping differ.

**Commits**: E82 `2907713f3`; D17/D18 fixes in the following commit.

### 2026-08-18 — D8 cleared; D7 fixed; D12–D14 added

**D8 is CLEARED.** The 519-versus-587 gap on `pro-medium-image-baseline` is
the signature of recovery commit `c07c57766` (2026-06-03, disclosed at the
time as E57's completeness addendum and Obs 339), which appended 68
detections from 18 recovered tiles to a pass whose verifier crops had been
extracted on 2026-03-24. Nothing is corrupt or lost: the append is
prefix-preserving, the crop manifest's 519 centroids align exactly with the
pass, and all three dependent `gs-era2` rows reproduce their committed accept
counts (485 / 463 / 465) from committed probabilities. The D6 hypothesis was
tested first and falsified — 587 is a single-file count; the pool's three-pass
total is 1,675.

| Claim | Before | After |
|---|--:|--:|
| `pro-medium-image-baseline` crop-pipeline feed | 587 | **519** |
| … deduplicated | 520 | **465** |
| … crops never extracted | 67 (11.4 %) | **54 (10.4 %)** |
| … crops whose centre moves | 64 | **53** |
| Worklist § 3.4 cells resolved | 9 of 12 | **12 of 12** (at $0) |
| Worklist Tier C1 call count | 720 | **687** |

What did **not** change: the three `gs-era2` rows' published F1 and MCC, the
raw-pass condition `pv-diag-384::baseline-pro-image-medium-t-0-0` (already
scored post-recovery on all three passes, 2026-06-03T12:32:32Z), and the four
analyses that consume it. Full working in `provenance-d8-2026-08-18.md`.

D7 closed by `d0a709059`. D12 and D13 added and verified at source — both
fixed in the writer by the same commit, both still present in historical
metadata. D14 added: the crop-manifest schema weakness that made D8 look like
corruption, found by a 203-manifest corpus sweep and affecting three cells.

### 2026-08-18 (later) — D6 fixed; its own fix audited

D6 closed: `scripts/lib_detection_paths.py` plus 30 migrated sites, repo
guard green, tier-1 suite 1,479 passed.

The `/audit` gate then ran two orthogonal lenses over that fix and found
**three further defects in it** (D6a-D6c), one of which — an import-time
breakage of eight scripts — was live and invisible to the test suite. That
is the case for the gate: the fix for a silent-undercount defect itself
shipped a silent breakage, a dead guard, and a test suite that would have
stayed green if the whole migration were reverted. All three are fixed.

Two corrections to earlier claims in this register's own lineage: the
migration is **not** "strictly a superset" at pool level (6 files across 4
pools are no longer resolved — correctly, as they are aggregation
artefacts), and the corpus counts quoted in the resolver's docstrings were
measured against `outputs/` while a run was writing to it, so they were
unverifiable and have been removed rather than restated.

D11 added: the exposure survey is affected data and needs a $0 re-run.

### 2026-08-18 — Original publication

Session 136. Consolidates the defects surfaced across the H13 scoring
chain, the Tier-0 and tile-size analyses, and four investigation agents,
which had been spread across three errata, four reports, and
conversation. Ten defects (three protocol-facing and disclosed, seven
open) and three cleared suspicions.
