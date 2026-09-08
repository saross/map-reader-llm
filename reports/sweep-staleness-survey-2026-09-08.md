# Sweep-staleness survey of verifier stages

> **Last revised**: 2026-09-08 (original publication). See [§ Changelog](#changelog) for revision history.
>
> **Surveyed**: 2026-09-08 against repository HEAD `8a67c8881` (working tree, branch `main`). Read-only: no repository file was created or modified.

## Method

Every directory under `outputs/` holding a `probabilities.json` whose `results` entries carry `mound_probability` was enumerated (265 stages, ~470 MB of JSON), and each was paired with any file in the same directory whose name starts with `sweep`. For each sweep the "all candidates" cell was taken as the maximum `n` over rows at the lowest `vote_t` with `prob_t == 0.0` (across every `buffer_m` and `config`), and compared with the count of candidates currently holding a non-null probability. Last-commit provenance for both artefacts came from a single `git log --name-only` traversal of `outputs/` and `results/`. Completeness was checked two ways, because the known failure hides entries rather than nulling them: null-valued entries, and entries absent relative to the stage's own `candidate_manifest.json`. Flagged stages were then cross-referenced against `results/run-conditions.json` (conditions' `detections`/`eval_path` and the per-run `verifier_passes` block, whose paths are run-relative), `results/run-analyses.json` (`output_path`), and a line-level grep of every Markdown file under `results/`, `reports/`, and `docs/`.

**Compute**: run on `sapphire` (`ssh sapphire`, repo at `~/Code/map-reader-llm`, venv `.venv`), per the project's compute-location rule. Script copied to `sapphire:/tmp/survey_sweep_staleness.py` and executed there; `survey.json` copied back. Wall time 3.9 s (the tree was in page cache), 2,524 Markdown files / 229,058 lines scanned.

## Summary counts

| Category | Count |
| --- | ---: |
| Verifier stages found (`probabilities.json` with `mound_probability`) | 265 |
| CONSISTENT (sweep n == candidates with a probability) | 28 |
| **STALE** (sweep n < candidates with a probability) | **5** |
| NO SWEEP (no `sweep*` file in the stage directory) | 232 |
| UNPARSED (sweep schema unreadable) | 0 |
| Sweep n exceeds probabilities (other mismatch) | 0 |
| INCOMPLETE (candidates missing or null-valued) | 0 |

Supporting counts, same run:

- Stages carrying a `cleanup_history`: **30**; of those, 5 have an in-directory sweep (all 5 are STALE) and 25 have none.
- Sweep files found in stage directories: 33, every one named `sweep_2d.json` and every one the documented top-level-list schema (`config, vote_t, prob_t, n, p, r, f1, buffer_m`). No other sweep filename or schema occurs inside a stage directory.
- Authoritative `candidate_manifest.json` available for 124 stages; the other 141 have no manifest, or only a shared sibling `crops/` manifest that cannot be attributed to the stage.
- Register linkage: 134 `verifier_passes` entries resolved to a stage directory, 18 unresolved.

## Detector validation against the known case

**PASS.** `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10` is flagged STALE. The detector reads its `sweep_2d.json` all-candidates cell (`vote_t=1`, `prob_t=0.0`, max over buffers [20, 30, 40, 50]) as **n = 342**, last committed `b8961e56f` (2026-04-17), against **802 candidates with a probability** in `probabilities.json`, last committed `c6b5e6b10` (2026-05-06, "data(p3a-recovery): cleanup Tier-2 cells (6 cells, 474 cands)"). The `cleanup_history` records `initial_missing=460`, `recovered=460`, `still_missing=0` at 2026-05-06T09:11:46.281421+00:00 — matching the brief's description exactly (342 swept, 460 later added, 802 total).

Two independent corroborations that the detector measures the intended quantity, not an artefact:

1. `reports/phase3a-verifier-completeness-audit-2026-05-03.md` (written before the cleanup) tabulates the same pre-cleanup counts this survey recovers from the sweeps — e.g. line 126 records `2190 | 2179 | 11` for `image-t0.3/verified-v1-n5`, and the stale sweep's all-candidates cell is 2179 against 2190 probabilities.
2. All 28 CONSISTENT stages match exactly (sweep n == probabilities n == results n) and in every case the sweep and the probabilities were committed in the *same* commit — the expected signature of a sweep run after its verification finished.

## STALE stages (full table)

All 5 share one history: swept during the April verification commits, then amended by the 2026-05-06 Tier-2 cleanup pass `c6b5e6b10` ("data(p3a-recovery): cleanup Tier-2 cells (6 cells, 474 cands)"), with no re-sweep afterwards. Their recovered counts sum to 474 candidates, which is that commit's 474.

| # | Stage | Sweep n | Probs n (with prob / results) | Gap | Sweep commit | Probs commit | cleanup_history (recovered) |
| --: | --- | --: | --: | --: | --- | --- | --- |
| 1 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10` | 342 | 802 / 802 | **460** | `b8961e56f` 2026-04-17 | `c6b5e6b10` 2026-05-06 | yes (460) |
| 2 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5` | 2179 | 2190 / 2190 | **11** | `b8961e56f` 2026-04-17 | `c6b5e6b10` 2026-05-06 | yes (11) |
| 3 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5` | 2016 | 2017 / 2017 | **1** | `b8961e56f` 2026-04-17 | `c6b5e6b10` 2026-05-06 | yes (1) |
| 4 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5` | 2839 | 2840 / 2840 | **1** | `b8961e56f` 2026-04-17 | `c6b5e6b10` 2026-05-06 | yes (1) |
| 5 | `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10` | 3600 | 3601 / 3601 | **1** | `b8961e56f` 2026-04-17 | `c6b5e6b10` 2026-05-06 | yes (1) |

Per-stage detail, register cross-references, and citing documents:

### 1. `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10`

- **Sweep**: `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10/sweep_2d.json` — 240 rows, schema `list-of-rows`, configs ['high-t0.0-n10'], buffers [20, 30, 40, 50]; all-candidates cell at `vote_t=1` / `prob_t=0.0` gives **n = 342** (identical across all buffers: min 342, max 342). Last commit `b8961e56f` (2026-04-17) — "data(verifier): full-matrix text-only adversarial v1 verification".
- **Probabilities**: 802 results, 802 with a non-null `mound_probability`, `total_results` field = 802. Last commit `c6b5e6b10` (2026-05-06) — "data(p3a-recovery): cleanup Tier-2 cells (6 cells, 474 cands)".
  - Commit history: `c6b5e6b10` 2026-05-06; `b8961e56f` 2026-04-17
- **cleanup_history**: [{"timestamp": "2026-05-06T09:11:46.281421+00:00", "initial_missing": 460, "recovered": 460, "still_missing": 0}]
- **Crop manifest** (in-crops): 802 candidates, `total_detections`=802 — shortfall vs probabilities = 0 (stage is complete; only the sweep is behind).
- **Register**: `results/run-conditions.json` → `decomposition/pv-diag-384/verifier_passes/flash-high-image-n5-image-t0.0-verified-v1-n10` (`path` = `flash-high-image-n5/image-t0.0/verified-v1-n10`, modality image).
- **Register conditions** with `detections`/`eval_path` inside this stage: none.
- **Register analyses** with `output_path` inside this stage: none.
- **Cited in** (`results/`, `reports/`, `docs/`; first 3 hits):
  - `results/uplift-supplement/k1-gapfill-disclosure.md:148` — | `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1
  - `results/recovery-reeval-2026-09-08/pv-diag-384/image-t0.0-verified-v1-n10-april-complete-resweep/README.md:3` — The April stage `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10`
  - `reports/provenance-d8-2026-08-18.md:260` — | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10/crops/` | 802 | 889 | **Same class, different event.** `consensus_t1.geojson
- **Also cited in** (outside the specified grep scope): planning/phase3a-verifier-recovery-runbook.md:109 (cell 9, gap 460, "**NOT cited** in any leaderboard / script")
- **Also cited in** (outside the specified grep scope): planning/verifier-stage-refresh-2026-09-08.md:30

### 2. `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5`

- **Sweep**: `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5/sweep_2d.json` — 400 rows, schema `list-of-rows`, configs ['high-t0.3-n5'], buffers [20, 30, 40, 50]; all-candidates cell at `vote_t=1` / `prob_t=0.0` gives **n = 2179** (identical across all buffers: min 2179, max 2179). Last commit `b8961e56f` (2026-04-17) — "data(verifier): full-matrix text-only adversarial v1 verification".
- **Probabilities**: 2190 results, 2190 with a non-null `mound_probability`, `total_results` field = 2190. Last commit `c6b5e6b10` (2026-05-06) — "data(p3a-recovery): cleanup Tier-2 cells (6 cells, 474 cands)".
  - Commit history: `c6b5e6b10` 2026-05-06; `b8961e56f` 2026-04-17
- **cleanup_history**: [{"timestamp": "2026-05-06T09:03:42.528175+00:00", "initial_missing": 11, "recovered": 11, "still_missing": 0}]
- **Crop manifest** (in-crops): 2190 candidates, `total_detections`=2190 — shortfall vs probabilities = 0 (stage is complete; only the sweep is behind).
- **Register**: `results/run-conditions.json` → `decomposition/pv-diag-384/verifier_passes/flash-high-image-n5-image-t0.3-verified-v1-n5` (`path` = `flash-high-image-n5/image-t0.3/verified-v1-n5`, modality image).
- **Register conditions** with `detections`/`eval_path` inside this stage: none.
- **Register analyses** with `output_path` inside this stage: none.
- **Cited in** (`results/`, `reports/`, `docs/`; first 3 hits):
  - `results/uplift-supplement/k1-gapfill-disclosure.md:150` — | `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 |
  - `reports/phase3a-verifier-completeness-audit-2026-05-03.md:126` — | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5` | 2190 | 2179 | 11 | manifest-in-crops-subdir |
  - `reports/phase3a-verifier-completeness-audit-2026-05-03.md:434` — ### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5/probabilities.json` — gap 11
- **Also cited in** (outside the specified grep scope): planning/phase3a-verifier-recovery-runbook.md:110 (cell 10, gap 11, feeds `flash-high-image-n5-t0.3-greedy-v1-487tile.json`)

### 3. `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5`

- **Sweep**: `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5/sweep_2d.json` — 400 rows, schema `list-of-rows`, configs ['high-t0.7-n5'], buffers [20, 30, 40, 50]; all-candidates cell at `vote_t=1` / `prob_t=0.0` gives **n = 2016** (identical across all buffers: min 2016, max 2016). Last commit `b8961e56f` (2026-04-17) — "data(verifier): full-matrix text-only adversarial v1 verification".
- **Probabilities**: 2017 results, 2017 with a non-null `mound_probability`, `total_results` field = 2017. Last commit `c6b5e6b10` (2026-05-06) — "data(p3a-recovery): cleanup Tier-2 cells (6 cells, 474 cands)".
  - Commit history: `c6b5e6b10` 2026-05-06; `b8961e56f` 2026-04-17
- **cleanup_history**: [{"timestamp": "2026-05-06T09:01:49.952236+00:00", "initial_missing": 1, "recovered": 1, "still_missing": 0}]
- **Crop manifest** (in-crops): 2017 candidates, `total_detections`=2017 — shortfall vs probabilities = 0 (stage is complete; only the sweep is behind).
- **Register**: `results/run-conditions.json` → `decomposition/pv-diag-384/verifier_passes/flash-high-image-n5-image-t0.7-verified-v1-n5` (`path` = `flash-high-image-n5/image-t0.7/verified-v1-n5`, modality image).
- **Register conditions** with `detections`/`eval_path` inside this stage: none.
- **Register analyses** with `output_path` inside this stage: none.
- **Cited in** (`results/`, `reports/`, `docs/`; first 3 hits):
  - `results/uplift-supplement/k1-gapfill-disclosure.md:153` — | `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 |
  - `reports/phase3a-verifier-completeness-audit-2026-05-03.md:138` — | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5` | 2017 | 2016 | 1 | manifest-in-crops-subdir |
  - `reports/phase3a-verifier-completeness-audit-2026-05-03.md:505` — ### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5/probabilities.json` — gap 1
- **Also cited in** (outside the specified grep scope): planning/phase3a-verifier-recovery-runbook.md:113 (cell 13, gap 1, feeds `flash-high-image-n5-t0.7-greedy-v1-487tile.json`)

### 4. `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5`

- **Sweep**: `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5/sweep_2d.json` — 400 rows, schema `list-of-rows`, configs ['high-t1.0-n5'], buffers [20, 30, 40, 50]; all-candidates cell at `vote_t=1` / `prob_t=0.0` gives **n = 2839** (identical across all buffers: min 2839, max 2839). Last commit `b8961e56f` (2026-04-17) — "data(verifier): full-matrix text-only adversarial v1 verification".
- **Probabilities**: 2840 results, 2840 with a non-null `mound_probability`, `total_results` field = 2840. Last commit `c6b5e6b10` (2026-05-06) — "data(p3a-recovery): cleanup Tier-2 cells (6 cells, 474 cands)".
  - Commit history: `c6b5e6b10` 2026-05-06; `b8961e56f` 2026-04-17
- **cleanup_history**: [{"timestamp": "2026-05-06T09:01:27.374537+00:00", "initial_missing": 1, "recovered": 1, "still_missing": 0}]
- **Crop manifest** (in-crops): 2840 candidates, `total_detections`=2840 — shortfall vs probabilities = 0 (stage is complete; only the sweep is behind).
- **Register**: `results/run-conditions.json` → `decomposition/pv-diag-384/verifier_passes/flash-high-image-n5-image-t1.0-verified-v1-n5` (`path` = `flash-high-image-n5/image-t1.0/verified-v1-n5`, modality image).
- **Register conditions** with `detections`/`eval_path` inside this stage: none.
- **Register analyses** with `output_path` inside this stage: none.
- **Cited in** (`results/`, `reports/`, `docs/`; first 3 hits):
  - `results/uplift-supplement/k1-gapfill-disclosure.md:155` — | `pv-diag-384` | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 |
  - `reports/phase3a-verifier-completeness-audit-2026-05-03.md:140` — | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5` | 2840 | 2839 | 1 | manifest-in-crops-subdir |
  - `reports/phase3a-verifier-completeness-audit-2026-05-03.md:516` — ### `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5/probabilities.json` — gap 1
- **Also cited in** (outside the specified grep scope): planning/phase3a-verifier-recovery-runbook.md:112 (cell 12, gap 1, feeds `flash-high-image-n5-t1.0-greedy-v1-487tile.json`)

### 5. `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10`

- **Sweep**: `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10/sweep_2d.json` — 800 rows, schema `list-of-rows`, configs ['scale4-high-t0.7-n10'], buffers [20, 30, 40, 50]; all-candidates cell at `vote_t=1` / `prob_t=0.0` gives **n = 3600** (identical across all buffers: min 3600, max 3600). Last commit `b8961e56f` (2026-04-17) — "data(verifier): full-matrix text-only adversarial v1 verification".
- **Probabilities**: 3601 results, 3601 with a non-null `mound_probability`, `total_results` field = 3601. Last commit `c6b5e6b10` (2026-05-06) — "data(p3a-recovery): cleanup Tier-2 cells (6 cells, 474 cands)".
  - Commit history: `c6b5e6b10` 2026-05-06; `b8961e56f` 2026-04-17
- **cleanup_history**: [{"timestamp": "2026-05-06T09:03:02.873122+00:00", "initial_missing": 1, "recovered": 1, "still_missing": 0}]
- **Crop manifest** (in-crops): 3601 candidates, `total_detections`=3601 — shortfall vs probabilities = 0 (stage is complete; only the sweep is behind).
- **Register**: `results/run-conditions.json` → `decomposition/pv-diag-384/verifier_passes/scale-4-optimal-487-verified-v1-n10` (`path` = `scale-4-optimal-487/verified-v1-n10`, modality image).
- **Register conditions** with `detections`/`eval_path` inside this stage: none.
- **Register analyses** with `output_path` inside this stage: none.
- **Cited in** (`results/`, `reports/`, `docs/`; first 3 hits):
  - `results/uplift-supplement/k1-gapfill-disclosure.md:163` — | `pv-diag-384` | `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10/crops/candidate_manifest.json` | `consensus_t1.geojson` | 1 | 3601 |
  - `reports/phase3a-verifier-completeness-audit-2026-05-03.md:141` — | `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10` | 3601 | 3600 | 1 | manifest-in-crops-subdir |
  - `reports/phase3a-verifier-completeness-audit-2026-05-03.md:521` — ### `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10/probabilities.json` — gap 1
- **Also cited in** (outside the specified grep scope): planning/phase3a-verifier-recovery-runbook.md:114 (cell 14, gap 1, feeds `scale4-optimal-greedy-v1-487tile.json`)

## Remediation status of the five

Only the known case has been re-swept. `results/recovery-reeval-2026-09-08/pv-diag-384/image-t0.0-verified-v1-n10-april-complete-resweep/sweep_2d.json` (240 rows, all-candidates cell n = 802) is today's like-for-like re-sweep of the April stage's complete probabilities, and its README states the diagnosis this survey reproduces independently. The stage's own `sweep_2d.json` was deliberately left in place under the preserve-and-compare policy, so it still reads STALE by the counts and always will.

**The other four have no re-sweep anywhere in `results/`.** Their downstream exposure, as far as it can be traced:

- `planning/phase3a-verifier-recovery-runbook.md` records each as feeding a named leaderboard cell. All four of those cells now live only in `archive/superseded-leaderboards/leaderboard/cells/`, retired by `b69d8af4b` (2026-08-20, "chore(archive): retire the legacy results/leaderboard family") — no live leaderboard consumes them.
- Of those archived cells, `scale4-optimal-greedy-v1-487tile.json` records `n_candidates_loaded` = 3600, i.e. the **pre-cleanup** count for `scale-4-optimal-487/verified-v1-n10` (complete: 3601) — that cell was built on the partial set.
- The other three cells record `n_candidates_loaded` of 3412, 3211, and 4638, which are the counts of the *`verified-v1-n10`* siblings (all CONSISTENT), not of the STALE `verified-v1-n5` stages. The runbook's "feeds" mapping is therefore looser than it reads: those three cells do not appear to have been built on the stale sweeps.

Gaps of 11, 1, 1, and 1 candidate on pools of 2,190–3,601 are small — the runbook's own estimate for the largest (cell 10, gap 11) was "Likely <0.005 F1 movement" (`planning/phase3a-verifier-recovery-runbook.md:110`) — but each stage's in-directory sweep is nonetheless a partial-verification artefact, and nothing in the directory says so.

## INCOMPLETE stages

**None.** Across all 265 stages, every `probabilities.json` entry carries a non-null `mound_probability`, no `cleanup_history` reports `still_missing > 0`, and for the 124 stages with an attributable `candidate_manifest.json` the probability count equals the manifest candidate count exactly (shortfall 0 in every case). The five STALE stages are themselves complete — the gap is in the sweep, not the verification.

## Cleanup-touched stages with no in-directory sweep

These 25 stages were amended by a cleanup pass but carry no `sweep*` file, so the staleness class as defined cannot arise inside the directory. They are listed because the same hazard could exist in whatever *external* artefact consumed them.

| Stage | Recovered | Results | Probabilities last commit |
| --- | --: | --: | --- |
| `outputs/55maps-generalisation/verified-v2` | 3 | 8942 | `6683952ac` 2026-05-06 |
| `outputs/55maps-image-generalisation/verified` | 1 | 7878 | `8699f456b` 2026-05-03 |
| `outputs/55maps-text-high-generalisation/verified` | 74 | 9205 | `d7f85978d` 2026-05-02 |
| `outputs/55maps-text-high-t0.3-generalisation/verified` | 2 | 9910 | `548604d95` 2026-04-27 |
| `outputs/55maps-text-min-generalisation/verified` | 39 | 10170 | `c1ea6df3c` 2026-05-03 |
| `outputs/flash35-pv-2x2/verified-f3vf` | 1 | 1132 | `68c4f0e29` 2026-06-11 |
| `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap37` | 2 | 791 | `3039d3ac9` 2026-08-29 |
| `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap38` | 1 | 791 | `f04eb6f58` 2026-09-04 |
| `outputs/grid-2026-08-18/verifier/g384_ov192/verify_37` | 1 | 3319 | `bce396250` 2026-08-31 |
| `outputs/gs/gold-standard-v2/verified-v1` | 11 | 608 | `c5983adb6` 2026-05-29 |
| `outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt` | 1 | 572 | `6683952ac` 2026-05-06 |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial-text` | 26 | 2017 | `414ee8a4b` 2026-05-03 |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief-text` | 19 | 2017 | `414ee8a4b` 2026-05-03 |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist` | 1 | 2017 | `c6b5e6b10` 2026-05-06 |
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist-text` | 19 | 2017 | `414ee8a4b` 2026-05-03 |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial-text` | 41 | 3736 | `414ee8a4b` 2026-05-03 |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief-text` | 27 | 3736 | `414ee8a4b` 2026-05-03 |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist-text` | 21 | 3736 | `414ee8a4b` 2026-05-03 |
| `outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-medium-verifier` | 1 | 3736 | `b2bfc446e` 2026-05-06 |
| `outputs/h11/pv-diag-384/verified/pro-high-image-1of5-pro-verifier` | 8 | 841 | `49703010b` 2026-05-06 |
| `outputs/h11/pv-diag-384/verified/pro-medium-image-baseline-pro-verifier` | 10 | 519 | `49703010b` 2026-05-06 |
| `outputs/h11/pv-diag-384/verified/text-baseline-pro-verifier` | 21 | 1047 | `49703010b` 2026-05-06 |
| `outputs/h8-v2/wbf/scale-4/verified` | 15 | 1114 | `6f8bc7140` 2026-05-06 |
| `outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/verify` | 6 | 38713 | `c368c9db7` 2026-08-26 |
| `outputs/wbf/e47-propose-brief-n5/verified-v1` | 1 | 3890 | `118507e2c` 2026-05-29 |

For the cleanup-touched stages the register links 18 conditions whose `detections` lie inside the stage directory. Comparing each condition's `eval_path` last-commit date with the stage's probabilities last-commit date, **0 of 18 evaluations predate the cleanup** — every one was last committed after the probabilities were amended. See the caveat below on what that check can and cannot establish.

## NO SWEEP stages

232 stages hold no file whose name starts with `sweep`. The full list is in `survey.json`; paths follow.

- `outputs/55maps-generalisation/verified`
- `outputs/55maps-generalisation/verified-v2`
- `outputs/55maps-image-generalisation/verified`
- `outputs/55maps-text-high-generalisation/verified`
- `outputs/55maps-text-high-t0.3-generalisation/verified`
- `outputs/55maps-text-min-generalisation/verified`
- `outputs/55maps-text-min-n10-uplift/verified-3of10`
- `outputs/era1-pv-stage-d/256-consensus-text-5of5/pass_1/verified`
- `outputs/era1-pv-stage-d/512-consensus-image/pass_1/verified`
- `outputs/era1-pv-stage-d/512-consensus-text-high/pass_1/verified`
- `outputs/era1-pv-stage-d/512-single-image-t0.0/pass_1/verified`
- `outputs/era1-pv-stage-d/512-single-image-t0.0/pass_2/verified`
- `outputs/era1-pv-stage-d/512-single-image-t0.0/pass_3/verified`
- `outputs/era1-pv-stage-d/512-single-text-t0.0/pass_1/verified`
- `outputs/era1-pv-stage-d/512-single-text-t0.0/pass_2/verified`
- `outputs/era1-pv-stage-d/512-single-text-t0.0/pass_3/verified`
- `outputs/flash35-pv-2x2/min-f3-verified-f35vf`
- `outputs/flash35-pv-2x2/verified-f35vf`
- `outputs/flash35-pv-2x2/verified-f3vf`
- `outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/verify_arm1`
- `outputs/gemini37-55map-2026-08-29/verifier/g384_ov192_55map_g37/verify_arm2`
- `outputs/gemini37-image-gs-2026-09-01/verifier/g384_ov192_g37img/verify_arm1`
- `outputs/gemini37-image-gs-2026-09-01/verifier/g384_ov192_g37img/verify_arm2`
- `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify`
- `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_k10`
- `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap37`
- `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify_swap38`
- `outputs/grid-2026-08-18/verifier/g384_ov048/verify`
- `outputs/grid-2026-08-18/verifier/g384_ov192/verify`
- `outputs/grid-2026-08-18/verifier/g384_ov192/verify_37`
- `outputs/grid-2026-08-18/verifier/g512_ov064/verify`
- `outputs/grid-2026-08-18/verifier/g512_ov256/verify`
- `outputs/gs/gold-standard-v2/verified-v1`
- `outputs/h10/evaluation-v2/pool_020_hp4hn4/verified`
- `outputs/h10/evaluation-v2/pool_160_hp4hn4/verified`
- `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5`
- `outputs/h11/e47-propose-brief/verified/flash-high-text-2of5`
- `outputs/h11/e47-propose-brief/verified/flash-high-text-3of5`
- `outputs/h11/e47-propose-brief/verified/flash-high-text-4of5`
- `outputs/h11/e47-propose-brief/verified/flash-high-text-5of5`
- `outputs/h11/e47-propose-brief/verified/text-baseline`
- `outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt`
- `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial`
- `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial-text`
- `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief`
- `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief-text`
- `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist`
- `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist-text`
- `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-comparative`
- `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial`
- `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial-text`
- `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief`
- `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief-text`
- `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist`
- `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist-text`
- `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-comparative`
- `outputs/h11/pv-diag-384/verified/flash-high-image-1of5`
- `outputs/h11/pv-diag-384/verified/flash-high-image-2of5`
- `outputs/h11/pv-diag-384/verified/flash-high-image-3of5`
- `outputs/h11/pv-diag-384/verified/flash-high-image-4of5`
- `outputs/h11/pv-diag-384/verified/flash-high-image-5of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-10of10`
- `outputs/h11/pv-diag-384/verified/flash-high-text-10of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-11of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-12of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-13of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-14of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-15of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-16of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-17of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-18of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-19of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-1of10`
- `outputs/h11/pv-diag-384/verified/flash-high-text-1of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-1of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-high-verifier`
- `outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-medium-verifier`
- `outputs/h11/pv-diag-384/verified/flash-high-text-1of5-pro-verifier`
- `outputs/h11/pv-diag-384/verified/flash-high-text-20of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-21of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-22of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-23of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-24of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-25of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-26of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-27of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-28of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-29of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-2of10`
- `outputs/h11/pv-diag-384/verified/flash-high-text-2of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-2of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-30of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-3of10`
- `outputs/h11/pv-diag-384/verified/flash-high-text-3of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-3of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-4of10`
- `outputs/h11/pv-diag-384/verified/flash-high-text-4of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-4of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-5of10`
- `outputs/h11/pv-diag-384/verified/flash-high-text-5of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-5of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-6of10`
- `outputs/h11/pv-diag-384/verified/flash-high-text-6of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-7of10`
- `outputs/h11/pv-diag-384/verified/flash-high-text-7of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-8of10`
- `outputs/h11/pv-diag-384/verified/flash-high-text-8of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-9of10`
- `outputs/h11/pv-diag-384/verified/flash-high-text-9of30`
- `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-1of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-2of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-3of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-4of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-high-vf-5of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-1of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-2of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-3of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-4of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-5of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-1of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-2of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-3of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-4of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-pro-vf-5of5`
- `outputs/h11/pv-diag-384/verified/flash-high-text-t03-1of5`
- `outputs/h11/pv-diag-384/verified/flash-minimal-image-medium-verifier`
- `outputs/h11/pv-diag-384/verified/flash-minimal-text-medium-verifier`
- `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-1of5`
- `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-2of5`
- `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-3of5`
- `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-4of5`
- `outputs/h11/pv-diag-384/verified/flash-minimal-text-t07-5of5`
- `outputs/h11/pv-diag-384/verified/image-10of10`
- `outputs/h11/pv-diag-384/verified/image-1of10`
- `outputs/h11/pv-diag-384/verified/image-1of5`
- `outputs/h11/pv-diag-384/verified/image-2of10`
- `outputs/h11/pv-diag-384/verified/image-2of5`
- `outputs/h11/pv-diag-384/verified/image-3of10`
- `outputs/h11/pv-diag-384/verified/image-3of5`
- `outputs/h11/pv-diag-384/verified/image-4of10`
- `outputs/h11/pv-diag-384/verified/image-4of5`
- `outputs/h11/pv-diag-384/verified/image-5of10`
- `outputs/h11/pv-diag-384/verified/image-5of5`
- `outputs/h11/pv-diag-384/verified/image-6of10`
- `outputs/h11/pv-diag-384/verified/image-7of10`
- `outputs/h11/pv-diag-384/verified/image-8of10`
- `outputs/h11/pv-diag-384/verified/image-9of10`
- `outputs/h11/pv-diag-384/verified/image-baseline`
- `outputs/h11/pv-diag-384/verified/image-baseline-pro-verifier`
- `outputs/h11/pv-diag-384/verified/pro-high-image-1of5-pro-verifier`
- `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-1of5`
- `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-2of5`
- `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-3of5`
- `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-4of5`
- `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-5of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-1of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-1of5-flash-minimal-verifier`
- `outputs/h11/pv-diag-384/verified/pro-high-text-1of5-pro-verifier`
- `outputs/h11/pv-diag-384/verified/pro-high-text-2of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-3of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-4of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-5of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-1of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-2of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-3of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-4of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-flash-min-vf-5of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-1of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-2of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-3of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-4of5`
- `outputs/h11/pv-diag-384/verified/pro-high-text-pro-vf-5of5`
- `outputs/h11/pv-diag-384/verified/pro-image-medium-verifier`
- `outputs/h11/pv-diag-384/verified/pro-image-minimal-verifier`
- `outputs/h11/pv-diag-384/verified/pro-medium-image-baseline-pro-verifier`
- `outputs/h11/pv-diag-384/verified/pro-medium-text-baseline-pro-verifier`
- `outputs/h11/pv-diag-384/verified/pro-text-medium-verifier`
- `outputs/h11/pv-diag-384/verified/pro-text-minimal-verifier`
- `outputs/h11/pv-diag-384/verified/text-10of10`
- `outputs/h11/pv-diag-384/verified/text-1of10`
- `outputs/h11/pv-diag-384/verified/text-2of10`
- `outputs/h11/pv-diag-384/verified/text-2of5`
- `outputs/h11/pv-diag-384/verified/text-3of10`
- `outputs/h11/pv-diag-384/verified/text-3of5`
- `outputs/h11/pv-diag-384/verified/text-4of10`
- `outputs/h11/pv-diag-384/verified/text-4of5`
- `outputs/h11/pv-diag-384/verified/text-5of10`
- `outputs/h11/pv-diag-384/verified/text-5of5`
- `outputs/h11/pv-diag-384/verified/text-6of10`
- `outputs/h11/pv-diag-384/verified/text-7of10`
- `outputs/h11/pv-diag-384/verified/text-8of10`
- `outputs/h11/pv-diag-384/verified/text-9of10`
- `outputs/h11/pv-diag-384/verified/text-baseline`
- `outputs/h11/pv-diag-384/verified/text-baseline-pro-verifier`
- `outputs/h11/pv-diag-384/verified/text-min-t07-true-1of5`
- `outputs/h2c-probe-2026-08-24/verify`
- `outputs/h8-v2/scale-4/verified`
- `outputs/h8-v2/wbf/scale-4/verified`
- `outputs/h8-v2/wbf/scale-8/verified`
- `outputs/image-b-gs-2026-08-28/verifier/g384_ov192_image/verify`
- `outputs/image-b-gs-2026-08-28/verifier/g384_ov192_image_high/verify`
- `outputs/stride-55map-2026-08-25/verifier/g384_ov128_55map/verify`
- `outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/verify`
- `outputs/stride-55map-2026-08-25/verifier/g384_ov192_55map/verify_37`
- `outputs/stride-phaseb-2026-08-25/verifier/g256_ov064/verify`
- `outputs/stride-phaseb-2026-08-25/verifier/g384_ov128/verify`
- `outputs/stride-phaseb-2026-08-25/verifier/g384_ov128/verify_k1`
- `outputs/stride-phaseb-2026-08-25/verifier/g384_ov128/verify_k3`
- `outputs/stride-phaseb-2026-08-25/verifier/g384_ov128/verify_k5`
- `outputs/stride-phaseb-2026-08-25/verifier/g512_ov176/verify`
- `outputs/stride-phaseb-2026-08-25/verifier/g512_ov320/verify`
- `outputs/stride-phasec-2026-08-25/verifier/g384_ov240/verify`
- `outputs/verifier-robustness/256-text-1of5-union/T0.0/verified`
- `outputs/verifier-robustness/256-text-ge3of5/T0.3/verified`
- `outputs/verifier-robustness/384-flash-high-text-16of30/T0.3/verified`
- `outputs/verifier-robustness/384-flash-high-text-1of5-union/T0.0/verified`
- `outputs/verifier-robustness/384-flash-high-text-ge3of5/T0.3-high/verified`
- `outputs/verifier-robustness/384-flash-high-text-ge3of5/T0.3/verified`
- `outputs/verifier-robustness/384-flash-high-text-ge3of5/T0.7-high/verified`
- `outputs/verifier-robustness/384-flash-high-text-ge3of5/T0.7/verified`
- `outputs/verifier-robustness/_smoke/256-text-1of5-union/T0.0/verified`
- `outputs/verifier-robustness/_smoke/256-text-ge3of5/T0.3/verified`
- `outputs/verifier-robustness/_smoke/384-flash-high-text-1of5-union/T0.0/verified`
- `outputs/verifier-robustness/_smoke/384-flash-high-text-ge3of5/T0.3/verified`
- `outputs/verifier-robustness/_smoke/384-flash-high-text-ge3of5/T0.7-high/verified`
- `outputs/verifier-t-pilot/T0.5`
- `outputs/verifier-t-pilot/T1.0`
- `outputs/wbf/e47-propose-brief-n5/verified-v1`
- `outputs/wbf/e47-propose-brief-n5/verified-v2`
- `outputs/wbf/fh-text-n30/verified`
- `outputs/wbf/fh-text-n5/verified`
- `outputs/wbf/gold-standard-v2-detect/verified-v1`

## Caveats

1. **Scope is the in-directory sweep.** Only files named `sweep*` inside the stage directory were treated as that stage's sweep. Sweeps and evaluations computed over a stage but written elsewhere (e.g. `results/h8-v2/verifier-sweep/*/sweep_2d_greedy_pv.json`, `results/rescore-2026-05-31/pv-diag-384/sweep/`, `results/verifier-robustness/sweep-sets/`) were not matched back to their source stage; a pre-cleanup sweep living in `results/` would not be caught by this survey.
2. **Commit dates are a coarse proxy.** The external-evaluation check compares git commit dates, not content. A file re-committed for an unrelated reason (a bulk move, a reformat) looks fresh — several rescore evaluations share the single commit `70c550177` (2026-08-23) — so "does not predate the cleanup" means the artefact was touched later, not that it was recomputed on the complete probabilities.
3. **`n` is a detection count, not a candidate count.** The sweep's `n` counts detections surviving the threshold pair, so its equality with the probability count at `vote_t`=min / `prob_t`=0.0 is an empirical property of this pipeline (it holds exactly in all 28 CONSISTENT stages), not a definitional identity. A sweep whose candidate pool legitimately differs from the stage's would read as STALE here.
4. **Manifest attribution.** Completeness could be checked against a crop manifest for only 124 of 265 stages. For the remaining 141 the only completeness evidence is null-valued entries and `cleanup_history`, which cannot detect candidates that were never written and never recorded as missing.
5. **Register coverage.** 18 `verifier_passes` entries could not be resolved to a stage directory (listed in `survey.json` under `summary.register_passes_unresolved_detail`), mostly `verifier-robustness` passes whose recorded path is the parent of the stage and `proposer-verifier-384` image passes with no matching directory. A stage reached only through one of those would show no register linkage here.
6. **Moving HEAD.** Another session committed to `main` during the survey (`de0fde55e` → `8a67c8881`, a documentation commit plus a one-line change to `results/run-conditions.json`). The reported run is entirely against `8a67c8881`; no file under `outputs/` changed between the two.
7. **Read-only compliance.** No repository file was created, modified, or committed; all writing went to the scratchpad and to `sapphire:/tmp/`. A local `git status` during the survey listed 16 files as modified (mostly under `archive/`); these are an artefact of the sandboxed shell failing to read some blobs — `git` reported "short read while indexing" on one, and that file (`results/h11-384-pv-diagnostic/flash-high-image-4of5/threshold_sweep.csv`) is byte-identical on sapphire (1,618 bytes, md5 `b2cdfdd2220593fc81cbb84e606ca9f8`) and clean in sapphire's `git status`. The survey itself read the tree on sapphire, so it is unaffected.

## Artefacts

- `reports/sweep-staleness-survey-2026-09-08.json` — raw per-stage records (all 265 stages: counts, `cleanup_history`, git provenance for probabilities and sweeps, sweep parse detail, manifest cross-check, register links, doc citations).
- `scripts/survey_sweep_staleness.py` — the survey script (run on sapphire).
- `scripts/render_sweep_staleness_report.py` — renders this report from the JSON.

## Changelog

### 2026-09-08 — Original publication

Survey commissioned in Session 151 after the image-stage finding (`reports/recovery-consistency-audit-2026-09-08.md` § 6.1); run on sapphire at HEAD `8a67c8881`; five stale stages, none cited by a registered condition or analysis.
