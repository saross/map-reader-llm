# Defect register — Session 136 (2026-08-18)

> **Last revised**: 2026-08-18 (D6 fixed; three further defects found by the
> audit of that fix; two new items). See [§ Changelog](#changelog).

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
| D4 | `_safe_round` returns `0.0` for an undefined MCC; `aggregate_runs` averages those zeros into multi-run means. | `evaluate_detections.py:533-535`, `:752-788` | Emit `null`, and average over defined passes only. Re-emit the 13 affected conditions. |
| D5 | `bootstrap_tile_classification_ci` documents degenerate resamples as "treated as `NaN` and skipped" but returns `0.0`. Every tile-MCC CI lower bound of exactly `0.0000` on the affected cells is that substitution, not a percentile. | `lib_advanced_metrics.py:2034-2036` (docstring) vs `:2087-2091` (code) | Make code and docstring agree; skip degenerate resamples. |
| D6 | Two detection-file naming conventions coexist. Any `detections_*` glob silently under-reads a mixed pool. | `evaluate_detections.py`; `scoring_sensitivity_survey.py`; 24 further sites | **FIXED** — `scripts/lib_detection_paths.py` + 30 sites migrated (`6b1cb87af`, `4c44e3fd6`, `6fa658877`, `8e59c9555`). Repo guard green; tier-1 suite 1,479 passed. |
| D6a | **Found by the audit of D6's fix.** Adding a package-qualified import to `lib_consensus.py` — which previously had no project import at all — broke **8 scripts at import time**; `n1_baseline_leaderboard_tiering.py` was unrunnable as documented. Invisible to tests because `pytest.ini` sets `pythonpath = "."`. | `lib_consensus.py`, `n1_baseline_leaderboard_tiering.py` | **FIXED** — dual-mode import; all 9 scripts verified running. |
| D6b | **Found by the audit of D6's fix.** The exclusion filter was dead code: every filename reaching it had already matched the glob, so its stem was always `"detections"`. Meanwhile 24 real non-passes DO begin `detections_` — verifier threshold outputs and this session's `detections_dedup.geojson`, the latter inside `run_<N>` directories. | `lib_detection_paths.py` | **FIXED** — strict per-convention regexes, corpus-validated. |
| D6c | **Found by the audit of D6's fix.** The tests validated the resolver's interior and nothing the defect broke: reverting the migration at all four call sites left 1,489/1,489 tier-1 tests green, and the migrated functions were executed by no test. | `tests/test_lib_detection_paths.py` | **FIXED** — 7 caller-wiring tests; verified to fail under a reverted migration. |
| D7 | A parsed detection lacking a `box_2d` key is counted by the results tracker but silently skipped when features are built — no log, unlike the malformed-length branch immediately below it. Cost one detection in H13 arm B run_2 (meta 1,362 vs GeoJSON 1,361). | `4_detect_mounds_batch.py:606-607` | Log the skip, and reconcile the tracker count with the emitted feature count. |
| D8 | `pro-medium-image-baseline` provenance mismatch: the crop manifest cites 519 candidates from a raw pass that now holds 587 features. Three `gs-era2` rows depend on it. | `outputs/h11/pv-diag-384/pro-medium-image-baseline/` | Investigate which artefact moved and when; document or correct. |

## Open documentation and reporting defects

| # | Defect | Location | Fix needed |
|---|---|---|---|
| D9 | H13 cost-efficiency figures are reported on the UNDISCOUNTED basis. Gemini real-time flex carries a 50 % discount, so `$5.7488` total and the F1-per-dollar values (0.4069 / 0.2975 / 0.1007) are about 2× actual. Ratios and the "every additional dollar buys negative F1" conclusion are unaffected, because all arms share one basis. | `results/h13-overlap-2026-08-18/findings.md` § Analysis 2 | Halve the dollar figures, state the basis explicitly, add a changelog entry. |
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
- **Decisions / Errata**: E79, E80, E81 — the three protocol-facing disclosures from this session. E75 — H13's disposition, which carried D2's mechanism before E80 took it over.

## Changelog

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
