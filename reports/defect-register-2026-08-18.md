# Defect register — Session 136 (2026-08-18)

> **Last revised**: 2026-08-18 (D8 cleared; D7 fixed; D12–D14 added). See
> [§ Changelog](#changelog).

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

## Open code defects

| # | Defect | Location | Fix needed |
|---|---|---|---|
| **D15** | **CRITICAL — the BCa bootstrap wrapper transposes its axes**, computing `n` statistics of `B` draws each instead of `B` statistics of `n` draws. Every interval on the BCa path is too narrow by roughly `sqrt(B/n)`: measured **1.66×** at B=1,000 and **5.50×** at B=10,000 on a real published cell. 1,520 committed evaluations used B=10,000. Point estimates are unaffected; the `percentile_fallback` path, permutation tests, and this session's paired bootstraps are all unaffected. Because the registered significance rule is "the 95 % CI excludes zero", the error runs towards **false positives**. | `lib_advanced_metrics.py`, `_bca_ci_from_indices` (the `np.moveaxis` in the vectorised wrapper) | VERIFIED, NOT FIXED — full working and remediation options in `reports/bca-axis-defect-2026-08-18.md`. Needs its own erratum and a PI decision on re-emission scope. |
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

## Open documentation and reporting defects

| # | Defect | Location | Fix needed |
|---|---|---|---|
| D9 | H13 cost-efficiency figures are reported on the UNDISCOUNTED basis. Gemini real-time flex carries a 50 % discount, so `$5.7488` total and the F1-per-dollar values (0.4069 / 0.2975 / 0.1007) are about 2× actual. Ratios and the "every additional dollar buys negative F1" conclusion are unaffected, because all arms share one basis. | `results/h13-overlap-2026-08-18/findings.md` § Analysis 2 | Halve the dollar figures, state the basis explicitly, add a changelog entry. |
| D16 | **WAS blocked by D15, now unblocked** (the code fix landed in `122104b8a`). Writing the row still needs per-cell evaluations generated at B=10,000 per the 2026-08-19 PI ruling. **D15 blocks the grid's register row.** `results/grid-2026-08-18/` has no per-cell `evaluation.json` (its metrics are computed directly in `grid_analysis.py`), so its four cells cannot be registered as conditions — and the analyses schema requires a non-empty `conditions_compared`. Generating those evaluations means running `evaluate_detections.py`, which always computes bootstrap CIs with no option to skip them, so it would write four fresh intervals already known to be 1.7-5.4x too narrow. Recording the row was attempted and reverted to keep the register valid. | `results/grid-2026-08-18/`, `results/run-analyses.json` | OPEN — unblocks the moment D15 is fixed; no other dependency |
| D11 | `results/scoring-sensitivity-2026-08-18/exposure-survey.json` was produced while the under-read was live, so `pv-diag-384::baseline-pro-{text,image}-medium-t-0-0` were scored on 1 pass of 3. Re-running now resolves 3 each. The exposure classifications are unchanged, but the recorded per-cell numbers for those two conditions are wrong. | `results/scoring-sensitivity-2026-08-18/` | OPEN — $0 re-run; feeds the dedup correction campaign |
| D10 | The grid runs' auto-written `experiment_intent.md` records hypothesis `H1` and "factor being varied: `include_example_images`", inherited from `detect_brief-text.json`. Wrong for a geometry grid, and it lands in provenance. | `outputs/grid-2026-08-18/**/experiment_intent.md` | Correct in the register row and post-run report rather than forking the config. |

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

### 2026-08-18 (latest) — D8 cleared; D7 fixed; D12–D14 added

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
