# H11 Reorganisation — Cost and Risk Estimate

> **Last revised**: 2026-05-28 (initial estimate). See [§ Changelog](#changelog) for revision history.

Read-only investigation. No repo changes made. The goal: estimate the workload and risk of moving the misplaced subdirectories out of `outputs/h11/` to better reflect what each one actually represents, ahead of a possible repo-publication pass.

## TL;DR

- **Five candidate subdirs were proposed for relocation**; the user also flagged `n1-outstanding-384/` as a possible move. After investigation, the candidate set shrinks to **four** subdirs to move and one to keep (`n1-outstanding-384/` is H11-proper). One further candidate (`e47-propose-brief/`) is ambiguous and is flagged as a decision question, not a confident move.
- **Aggregate workload** for the four confident moves: **6.5 – 11.5 hours** (high confidence on the upper bound for `gold-standard-v2`, lower confidence on `e47-propose-brief` if it stays in scope).
- **The dominant cost is documentation propagation, not code breakage.** Active code references (scripts, configs, YAML) total 26 lines across all candidates; markdown body lines total 96 in active docs (results/, reports/, docs/, planning/).
- **The single largest hidden gotcha is the leaderboard regeneration loop**: ~340 lines across tracked JSON files contain absolute paths derived from `planning/condition-inventory.json`. These are regenerable artefacts (script `scripts/build_combined_leaderboard.sh`), but each affected Era costs 30–60 minutes on sapphire. Inventory edits + leaderboard rebuild is mandatory for any path change that touches an inventory entry — currently only `e47-propose-brief` (2 entries) of the candidates.
- **Partial reorganisation gets ~80% of the benefit at ~30% of the cost.** Move the easy three (`propose-brief-v1-test`, `v2-proposer-test`, `wbf`) now; defer `gold-standard-v2` and `e47-propose-brief` to paper-writing prep.

## Recategorisation summary

| Candidate | User suggestion | My finding | Confidence |
|---|---|---|---|
| `e47-propose-brief/` | Move to `outputs/e47-propose-brief/` | **Inventory tags it `hypothesis=H11`** (2 entries). Methodologically it is a proposer-prompt swap experiment, not a tile-size axis. **Decision required** before moving. | Medium |
| `propose-brief-v1-test/` | Move alongside e47 | Confirmed orphan; tiny (6 files, 2 commits). Safe to move. | High |
| `gold-standard-v2/` | Move to `outputs/gold-standard-v2/` or `outputs/gs/` | Confirmed not H11-proper (no inventory entries), but is the canonical 4-map production pipeline cited as the paper headline result. Code-light, doc-heavy. | High |
| `v2-proposer-test/` | Move to `outputs/v2-proposer-test/` | Confirmed orphan; tiny (4 files, 2 commits). Safe to move. | High |
| `wbf/` | Move to `outputs/wbf/` | Confirmed methodology axis (aggregation), not tile-size. Safe to move, but `scripts/fuse_detections_wbf.py` carries 6 hardcoded `default_output_dir` strings. | High |
| `n1-outstanding-384/` | "Probably H11-proper" | **Confirmed H11-proper.** 8 inventory entries tagged `hypothesis=H11, era=2`. Configs `mcc-eval-384px.yaml` and `n1-eval-384px-all-buffers.yaml` interleave it with `pv-diag-384/` paths. **Do not move.** | High |

## Reference inventory by remediation cost

### Critical — active code that will break silently if not updated

| Subdir | Files | Where |
|---|---:|---|
| `gold-standard-v2/` | 9 .py, 5 .sh, 1 config (markdown-suffix) | `scripts/gs-fp-classify.py`, `scripts/analyse_inter_pass_agreement.py`, `scripts/analyse_subtype_classification.py`, `scripts/analyse_verifier_t_pilot.py`, `scripts/fuse_detections_wbf.py`, `scripts/gs-v2-t0.7-recovery.sh`, `scripts/lib_batch_api.py`, `scripts/run_verifier_t_stage_b.py`, `scripts/11maps-gold-standard-v2.sh`, `configs/run-configs/55maps_text_high_generalisation_post_run_report.md` |
| `e47-propose-brief/` | 1 .py | `scripts/fuse_detections_wbf.py` (5 hardcoded path strings in `SPECIAL_CONFIGS`) |
| `wbf/` | 2 .py | `scripts/fuse_detections_wbf.py` (3 `default_output_dir`), `scripts/compare_wbf_greedy_pv_permutation.py` |
| `propose-brief-v1-test/` | 0 | — |
| `v2-proposer-test/` | 0 | — |

Verbatim counts: `git grep -c` per extension produced py=17 sh=5 for gold-standard-v2; py=6 sh=6 for e47-propose-brief (sh count inflates because `gs-v2-t0.7-recovery.sh` mentions both subdirs — same file already counted under gold-standard-v2).

### Documentation — active docs that need updating

| Subdir | Active markdown body-line refs |
|---|---:|
| `gold-standard-v2/` | 49 lines across ~13 active markdown files |
| `e47-propose-brief/` | 34 lines |
| `wbf/` | 12 lines |
| `propose-brief-v1-test/` | 1 line |
| `v2-proposer-test/` | 0 lines |

Key paper-cited docs (must update under the Document Revision Policy if `gold-standard-v2/` moves):

- `results/meta-findings-summary.md` (3 refs)
- `results/paper-tables/gold-standard-spatial-tolerance.md` (1 ref)
- `results/gs-fp-classification/report.md`
- `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md`
- `results/gold-standard-subtype-classification/report.md`
- `results/temperature-failure-recovery-analysis/report.md`
- `results/verifier-t-pilot/stage-{a,b}-report.md`
- `reports/gs-tile-pool-mapping-2026-05-28.md`
- `reports/phase3a-verifier-completeness-audit-2026-05-03.md`

### Historical — leave as-is

| Subdir | Archive markdown body-line refs | Commits | Action |
|---|---:|---:|---|
| `e47-propose-brief/` | 36 | 7 | Leave; the archive subdirs (`archive/v2-verifier-contamination/`) are explicitly historical |
| `gold-standard-v2/` | 21 | 9 | Leave |
| `wbf/` | 3 | 7 | Leave |
| `propose-brief-v1-test/` | 2 | 2 | Leave |
| `v2-proposer-test/` | 3 | 2 | Leave |

## Hidden gotchas

### 1. Tracked JSON path embeddings (the leaderboard cache)

Counts of path-bearing JSON lines (verbatim from `git grep -c | awk` totals):

- `e47-propose-brief/`: **132 lines** across 85 JSON files
- `gold-standard-v2/`: **39 lines** across 29 JSON files
- `wbf/`: **5 lines** across 1 JSON file
- `propose-brief-v1-test/`: **2 lines** across 2 JSON files
- `v2-proposer-test/`: **2 lines** across 2 JSON files

The bulk of `e47-propose-brief/` JSON references (30 files, 30 lines) live under `results/leaderboard/combined/era2/` and store absolute paths like `/home/shawn/Code/map-reader-llm/outputs/h11/e47-propose-brief/.../consensus_t3.geojson`. Verified by reading `results/leaderboard/combined/era2/leaderboard_tiers_f1_100m.json`.

`scripts/augment_per_arch_with_mcc.py:152` reads `cond["geojson"]` from these tier JSONs and calls `gpd.read_file(geojson_path)` directly — so a stale path means a `FileNotFoundError`, not a silent miscalculation. But: the leaderboards are regenerable from `planning/condition-inventory.json` (which uses repo-relative paths) via `scripts/build_combined_leaderboard.sh`. Cost per Era: 30–60 minutes on sapphire (per the script header). Only `e47-propose-brief/` and `n1-outstanding-384/` appear in the inventory; the other candidates do not, so their JSON embeddings are likely in working/audit artefacts that won't be rerun.

A further 31 e47 references live under `archive/v2-verifier-contamination/`. Those are explicit historical records — leave as-is.

### 2. Hardcoded paths in `scripts/fuse_detections_wbf.py`

The `SPECIAL_CONFIGS` dictionary (lines 50–110+) carries verbatim path strings to detection files under `outputs/h11/e47-propose-brief/` and `outputs/h11/gold-standard-v2/` AND output paths to `outputs/h11/wbf/`. Moving any of the three breaks all three configs. **All three need updating together** if any single one of them moves.

### 3. `.gitignore` rules

6 active rules under `.gitignore` reference candidate paths:

- Line 114: `outputs/h11/gold-standard-v2/crops/crops/`
- Line 115: `outputs/h11/gold-standard-v2/*.log`
- Lines 118–120: `outputs/h11/e47-propose-brief/...`
- Line 122: `outputs/h11/v2-proposer-test-BAD-TILESIZE/` (a sibling dir, not the candidate — leave alone)
- Lines 126, 143: `outputs/h11/wbf/...`

These need updating in lockstep with any move. Easy to miss.

### 4. Configs that reference candidates

- `configs/mcc-eval-384px.yaml` and `configs/n1-eval-384px-all-buffers.yaml` reference `outputs/h11/n1-outstanding-384/...` extensively (16 YAML lines combined). **These confirm n1-outstanding-384 is H11-proper** — it sits next to `pv-diag-384/` paths in the H11 tile-size evaluation grid.
- `configs/run-configs/55maps_text_high_generalisation_post_run_report.md` references `gold-standard-v2/` (markdown body, not a code path).

### 5. Out-of-repo references (informational, not blocking)

`~/personal-assistant/data/scratchpads/map-reader-llm.md` mentions `outputs/h11/` paths. CC session transcripts under `~/.claude/projects/-home-shawn-Code-map-reader-llm/` contain many references — these are immutable historical records.

### 6. No symlinks

`find outputs/h11/ -maxdepth 3 -type l` returned no results.

## Workload estimate per subdir

| Subdir | Hours (low/high) | Critical refs | Doc refs (active) | High-risk items | Confidence |
|---|---|---:|---:|---|---|
| `propose-brief-v1-test/` | 0.25 / 0.5 | 0 | 1 | None | High |
| `v2-proposer-test/` | 0.25 / 0.5 | 0 | 0 | None | High |
| `wbf/` | 1.0 / 1.5 | 2 .py | 12 | `fuse_detections_wbf.py` SPECIAL_CONFIGS coupling with e47 + gs-v2 | High |
| `gold-standard-v2/` | 3.0 / 5.0 | 9 .py + 5 .sh + 1 config-doc | 49 | Heavy script coupling; `lib_batch_api.py` docstring mention; paper-cited docs need Document Revision Policy changelog stubs | High |
| `e47-propose-brief/` *(if moved)* | 2.0 / 4.0 | 1 .py (shared) | 34 | Inventory edit + leaderboard regen on Era 2 (30–60 min on sapphire); 132 lines of JSON regenerate as a side effect; archive refs are intentionally frozen | Medium |
| `n1-outstanding-384/` | **0 — do not move** | 7 .py + 1 .sh + 2 YAML | 2 | Confirmed H11-proper | High |

Each entry above includes ~15–30 minutes per subdir for **verification**: running `git grep` after the move to confirm no stragglers, smoke-testing one or two affected scripts (`python -c "import scripts.fuse_detections_wbf"` or running the script's `--help`), and visual diff of the inventory/leaderboard JSON if applicable.

## Aggregate estimate

**Confident-move set (4 subdirs, excluding `e47-propose-brief`)**: **4.5 – 7.5 hours**

| Subdir | Low | High |
|---|---:|---:|
| `propose-brief-v1-test/` | 0.25 | 0.5 |
| `v2-proposer-test/` | 0.25 | 0.5 |
| `wbf/` | 1.0 | 1.5 |
| `gold-standard-v2/` | 3.0 | 5.0 |
| **Total** | **4.5** | **7.5** |

**Full set (including `e47-propose-brief` if its move is decided)**: **6.5 – 11.5 hours**. Add Era-2 leaderboard regen wall-clock (30–60 min on sapphire, runs unattended).

## Alternative strategies

### Strategy A: Easy three now (recommended for low-risk progress)

Move `propose-brief-v1-test/`, `v2-proposer-test/`, `wbf/` in one focused 2-hour session. Defer `gold-standard-v2/` and `e47-propose-brief/` to paper-writing prep. Benefits:

- Removes 3 of the 5 misplaced subdirs (60% reduction in clutter for ~25% of the cost).
- No inventory edits, no leaderboard regen, no paper-cited doc revisions.
- `wbf/` is the only awkward one in this set because `fuse_detections_wbf.py` couples it to `e47-propose-brief/` and `gold-standard-v2/` — if those two don't move, the `wbf/` output path can be updated cleanly in `SPECIAL_CONFIGS` while leaving the input paths intact.

### Strategy B: Easy three + `gold-standard-v2/` (recommended for repo-publication push)

Adds `gold-standard-v2/` (the canonical 4-map pipeline). Highest doc-update cost but no leaderboard regen. ~6 hours total. The `gold-standard-v2/` cleanup is the most defensible from a publication perspective: it is the paper headline pipeline and its current location is least intuitive to an external reader.

### Strategy C: All five

Full reorganisation, requires the `e47-propose-brief` H11-or-not decision (see below) and a sapphire leaderboard regen for Era 2. ~9 hours active + ~1 hour wall-clock unattended.

### Strategy D: Move-without-rewrites (do not recommend)

Move the subdirs and leave references stale. Saves time but: (1) `fuse_detections_wbf.py` breaks immediately; (2) `gs-fp-classify.py` and friends break; (3) the inventory + leaderboard regen still needs running for `e47-propose-brief` because the inventory paths are wrong. This isn't really an option.

## Hidden questions worth surfacing before proceeding

1. **Is `e47-propose-brief/` H11 or not?** The inventory tags it `hypothesis=H11, era=2`, but methodologically it's a proposer-prompt-swap experiment (`propose_brief-text`, K=5) that happens to use 384px tiles. If you consider H11 = "tile-size axis", it doesn't belong. If you consider H11 = "the corpus partition where the 384px production pipeline lives", it does belong. The choice affects both whether to move it and whether the inventory's `hypothesis` field needs revisiting more broadly.

2. **Target for `gold-standard-v2/`**: `outputs/gold-standard-v2/` (flat) or `outputs/gs/gold-standard-v2/` (under a new `gs/` umbrella that could also hold future gold-standard variants)? The umbrella adds future-proofing at no extra cost during this move.

3. **Should `n1-outstanding-384/` be renamed in place?** It IS H11-proper, but its name reads like a one-off cleanup task ("n1 outstanding"). Renaming to `pv-diag-384-pro/` or similar would align it with its sibling `pv-diag-384/`. Not part of the move estimate but the same code paths would be affected; cheaper to fold in if doing a reorganisation pass anyway.

4. **Document Revision Policy compliance**: Per `CLAUDE.md`, any touched results/ or reports/ markdown needs a top banner + changelog entry. For `gold-standard-v2/`, that's ~13 docs to back-fill. I have factored this into the 3–5 hour estimate but called it "doc revisions"; if back-fill is a separate task, subtract ~1 hour from the gold-standard-v2 estimate and budget it separately.

5. **`raw-outputs/` mirror**: The audit report references `archive/v2-verifier-contamination/MANIFEST.md` mapping e47 paths to `raw-outputs/e47-propose-brief--verified-v2/`. Worth checking whether there's a parallel `raw-outputs/` tree mirroring `outputs/h11/` that would also need updating. I did not investigate `raw-outputs/` in this pass.

## Changelog

### 2026-05-28 — Original publication

Initial workload + risk estimate prepared at the user's request before deciding whether to proceed with reorganisation. Investigated 6 candidate subdirs (5 from the user's list + `n1-outstanding-384/`). Findings: `n1-outstanding-384/` is H11-proper; `e47-propose-brief/` is ambiguous (inventory tags as H11); the other 4 are confidently misplaced. Total estimated cost: 4.5–7.5 hours for the confident set, 6.5–11.5 hours including `e47-propose-brief`. Recommended path: Strategy A (easy three first) or Strategy B (easy three + `gold-standard-v2/`). No repo changes made.
