# E72 board regeneration — 23-condition round-robin

> **Last revised**: 2026-10-30 (regenerated on the restated pairwise layout, PI ruling D69 Q15). Prior: 2026-08-02 (original publication — E72 remediation). See [§ Changelog](#changelog) for revision history.

**Purpose**: supplies the regenerated leaderboard the Principal Investigator's ruling on protocol erratum [E72](../../docs/methodology/preregistration/protocol-errata.md) calls for — the March 2026 round-robin boards with the three coverage-confounded `flash-min-text-t10` cells dropped, the Benjamini–Hochberg (BH) false-discovery-rate (FDR) family recomputed over the retained pairs, and the greedy-clique tiers re-run.

**Produced**: 2026-10-30, on zbook, from repository commit `27454299f` by `scripts/regen_e43_board.py`, over `results/pairwise/` as restated in place by the S164 pass (`08af04cf3`), reading today's run beside each of its 100 dated March records (`results/rescore-2026-10-15/pairwise/`). Zero application programming interface (API) calls; zero permutation tests re-run.

## 1. What was dropped, and why

The condition family `flash-min-text-t10` (five aliases across the repository; the underlying study is `outputs/h11/consensus-384-UNINTENDED-T1.0/`) covers **240 of the 487** evaluation tiles by design, but the 2026-03-26 bounds standardisation scored it against the full 487-tile bounds. Every mound in the 247 unprocessed tiles became an automatic false negative, understating that arm's F1 by roughly 0.17–0.19. Membership was derived from each test artefact's recorded `condition_*.source` provenance, never from labels — the condition carries five aliases across the repository, so label matching is unsafe. A provenance walk of `results/pairwise/` flags **148** test artefacts, matching the remediation report's inventory.

| Board | Conditions before | Dropped | Conditions after | Pairs before | Pairs dropped | Pairs after |
|---|--:|--:|--:|--:|--:|--:|
| `leaderboard-20m` | 26 | 3 | 23 | 325 | 72 | 253 |
| `leaderboard-30m` | 25 | 3 | 22 | 300 | 69 | 231 |

The dropped conditions are identical on both boards: `flash-min-text-t10 N=10 N=10, 9-of-10`, `flash-min-text-t10 N=30 N=30, 22-of-30`, `flash-min-text-t10 N=5 N=5, 5-of-5`.

The matched-scope replacements for these cells are filed as their own first-class analysis at `results/e43-matched-temperature/` and are deliberately **not** spliced into this board — the two analyses answer different questions and were run under different protocols.

## 2. Validation gates

All four gates passed before anything was written:

- **Gate A** — the per-pair JSONs reproduce each board's committed `run_manifest.json` exactly (same pair set, same raw p-values, same ΔF1), and each hypothesis family's raw p-values equal its per-test JSONs. Where a per-pair file is a dated March record (100 of them), today's run beside it is read in its place, after checking that the two name the same test and that the record is the older; a beside file with no record next to it is refused.
- **Gate B** — recomputing the FULL board (nothing dropped) reproduces each board's own run as its BH artefact (`fdr/pairwise_results_fdr.json`) records it: `leaderboard-20m` 265/325 significant, 9 tiers; `leaderboard-30m` 240/300 significant, 9 tiers, with every pair's adjusted value equal to the run's. The significance count is the run's own, as the PI specified (D69 Q15); the previous revision's 243 at `leaderboard-30m` came from the superseded March run; the tier count is the published snapshot's. This proves the BH and tiering reimplementation is faithful before its output is trusted for the reduced board.
- **Gate C** — every condition's F1, precision, recall and detection count agree across all tests it appears in. The dated March records are a different vintage and are not mixed in.
- **Gate D** — replaying the greedy clique under the *published* 20 m rank order reproduces the published tier sizes (1, 6, 3, 2, 4, 4, 1, 3, 2) exactly. See § 3.1 for why this gate exists.

## 3. Movement: which conditions changed tier

Movement is measured against the **recomputed** 26-condition board, so the comparison isolates the E72 effect: both boards use the same code, the same p-values and the same F1-descending processing order, and differ only in which cells are present.

### `leaderboard-20m` — 9 tiers → 8 tiers

| Condition | F1 | Tier (26-condition board) | Tier (regenerated board) | Movement |
|---|:---:|--:|--:|:---|
| flash-high-text-4-of-5--flash-min-vf (t=0.15) | 0.864 | 2 | 1 | 1 up |

**BH status changes among the 253 retained pairs**: 1. See the table below.

| Condition A | Condition B | p (raw) | q (old family) | q (new family) | Change |
|---|---|---:|---:|---:|:---|
| flash-high-text-16-of-30--flash-min-vf (t=0.2) | flash-high-text-4-of-5--flash-min-vf (t=0.15) | 0.0398 | 0.0490 | 0.0506 | significant → ns |

### `leaderboard-30m` — 9 tiers → 8 tiers

No retained condition changed tier number. The board loses the tier(s) the dropped cells occupied and nothing else moves.

**BH status changes among the 231 retained pairs**: 0. No retained pair changed significance verdict when the family shrank.

### 3.1 One difference from the published snapshot that is NOT E72

Greedy-clique tiering is order-dependent, and the published 20 m snapshot (`results/paper-tables/leaderboard_tiers_20m.md`) ranks one condition out of F1 order in a way that moves a tier: `flash-high-image-3-of-5--flash-min-vf (t=0.15)` (F1 0.778) sits at rank 10, ahead of two higher-F1 conditions. Processed there it joins the 0.814–0.816 clique; processed in strict F1 order it is reached only after `flash-high-text N=10` (F1 0.799) has already opened the next tier — and that boundary rests on a single borderline pair (`FH text 26/30` versus `FH text 9/10`, q = 0.044). The published order also places rank 8 (`text-baseline--flash-min-vf (t=0.15)`, F1 0.814) ahead of rank 9 (`flash-high-text N=30 N=30, 26-of-30`, F1 0.816) on these inputs, but the two share a tier under either order, so that swap moves nothing.

This script uses the documented F1-descending order throughout, so the following condition sits one tier lower here than in the March snapshot **for reasons unrelated to the coverage confound**:

| Condition | Tier (published snapshot) | Tier (F1-ordered recomputation) |
|---|--:|--:|
| flash-high-image-3-of-5--flash-min-vf (t=0.15) | 3 | 4 |

Gate D proves the attribution: replaying the clique under the published rank order reproduces the published tier sizes exactly, so the difference is processing order, not statistics.

## 4. The smaller BH families

The same confounded p-values also entered three smaller BH families. Memberships below are derived from the family manifests themselves, not assumed. In this project BH is applied **within** each declared family, so only families containing a confounded member are affected; the script asserts the others are clean rather than trusting that.

| Family artefact | Family | Members (published) | Dropped | Members (retained) | Significant (published, retained members) | Significant (recomputed) | Status changes |
|---|---|--:|--:|--:|--:|--:|--:|
| `results/pairwise/20m` | `confirmatory` | 26 | 3 | 23 | 17 | 17 | 0 |
| `results/pairwise/30m` | `confirmatory` | 26 | 3 | 23 | 15 | 15 | 0 |
| `results/factor-analysis/factor_analysis_results.json` | `temperature` | 6 | 4 | 2 | 1 | 1 | 0 |

Unaffected families (no confounded member; left untouched): `factor-analysis:architecture`, `factor-analysis:modality`, `factor-analysis:prompt_engineering`, `factor-analysis:thinking`, `pairwise-20m:exploratory`, `pairwise-30m:exploratory`.

## 5. What this does and does not change

- **Unchanged**: every retained condition's F1, precision, recall, detection count and tile-level MCC. Dropping whole cells removes rows; it does not rescore the survivors.
- **Unchanged**: every retained pair's observed ΔF1 and raw permutation p-value. No test was re-run.
- **Changed**: the BH family size, hence the adjusted q-values, hence (potentially) the tier clustering.
- **Not done here**: the matched-scope temperature evidence. That lives at `results/e43-matched-temperature/` and is cited, not merged.

## 6. Files in this directory

```text
leaderboard-20m/   leaderboard.{md,csv}, tiers.{md,csv},
                   pairwise_results_fdr.csv, run_manifest.json
leaderboard-30m/   (as above, at the 30 m buffer)
bh-families/       families_recomputed.{md,csv,json}
summary.md         this document
```

## Changelog

### 2026-10-30 — Regenerated on the restated pairwise layout (Session 166)

**Trigger**: the S164 restatement pass regenerated `results/pairwise/` in place on the consensus route of PI ruling D60 (3) (`08af04cf3`; PR #52, merged as `0d195cac8`). The per-pair files that read the two drifted single-pass arms stay at their paths as dated March records, with today's runs beside them under `results/rescore-2026-10-15/pairwise/` (D61 (2)); this revision reads those runs in place of the 100 records the boards and families use. The PI queued the regeneration as D69 Q15. No permutation test was re-run.

**Script changes** (the PI's specification, D69 Q15): Gates A and C read today's run beside each dated record, after checking that the two name the same test and that the record is the older; Gate B takes each board's significance count from the board's own run and also matches every pair's adjusted value; the renderers keep this revision trail; and § 3.1's figures are computed rather than quoted.

**Key figures**:

| Figure | 2026-08-02 | 2026-10-30 |
|---|--:|--:|
| `leaderboard-20m` full board: BH-significant | 265 of 325 | 265 of 325 |
| `leaderboard-20m` regenerated board: BH-significant | 199 of 253 | 198 of 253 |
| `leaderboard-20m` regenerated board: tiers | 8 | 8 |
| `leaderboard-20m`: retained pairs whose raw p moved | — | 64 of 253 |
| `leaderboard-20m`: retained conditions whose F1 or tier moved | — | 13 of 23 |
| `leaderboard-30m` full board: BH-significant | 243 of 300 | 240 of 300 |
| `leaderboard-30m` regenerated board: BH-significant | 181 of 231 | 178 of 231 |
| `leaderboard-30m` regenerated board: tiers | 8 | 8 |
| `leaderboard-30m`: retained pairs whose raw p moved | — | 58 of 231 |
| `leaderboard-30m`: retained conditions whose F1 or tier moved | — | 13 of 22 |
| `results/pairwise/20m` `confirmatory`: BH-significant (retained) | 16 of 23 | 17 of 23 |
| `results/pairwise/20m` `confirmatory`: members whose raw p moved | — | 9 of 23 |
| `results/pairwise/30m` `confirmatory`: BH-significant (retained) | 15 of 23 | 15 of 23 |
| `results/pairwise/30m` `confirmatory`: members whose raw p moved | — | 9 of 23 |
| `results/factor-analysis/factor_analysis_results.json` `temperature`: BH-significant (retained) | 1 of 2 | 1 of 2 |
| `results/factor-analysis/factor_analysis_results.json` `temperature`: members whose raw p moved | — | 0 of 2 |

**BH verdicts that changed** (the same retained pair or family member, 2026-08-02 → 2026-10-30): 5.

| Artefact | Condition A | Condition B | p (raw) | q | Verdict |
|---|---|---|---|---|---|
| `leaderboard-20m` | image-baseline--flash-min-vf (t=0.2) | flash-min-text-t07 N=30 N=30, 29-of-30 | 0.0383 → 0.0469 | 0.048693 → 0.059033 | significant → ns |
| `leaderboard-30m` | flash-high-image-3-of-5--flash-min-vf (t=0.15) | flash-high-text N=10 N=10, 9-of-10 | 0.0371 → 0.0506 | 0.047349 → 0.063525 | significant → ns |
| `leaderboard-30m` | pro-high-text-3-of-5--flash-min-vf (t=0.15) | flash-high-text N=30 N=30, 26-of-30 | 0.0315 → 0.0410 | 0.041110 → 0.052911 | significant → ns |
| `leaderboard-30m` | text-baseline--flash-min-vf (t=0.15) | flash-high-text N=5 N=5, 5-of-5 | 0.0371 → 0.0465 | 0.047349 → 0.059019 | significant → ns |
| `results/pairwise/20m` `confirmatory`, group 7 — N=30 vs N=10 (HIGH text) | Flash HIGH text 26-of-30 | Flash HIGH text 9-of-10 | 0.0375 → 0.0357 | 0.050735 → 0.048300 | ns → significant |

**Tier changes on the regenerated boards**: none; every retained condition keeps its tier number. The F1 moves are listed in each board's `leaderboard.md` changelog.

**Not changed**: the dropped conditions and every retained pair, condition and family member (the membership is checked, not assumed); the provenance walk's inventory of 148 confounded per-pair files under `results/pairwise/`; the method (BH within each declared family at q = 0.05; greedy clique in F1-descending order). The previous revision's outputs were read at `2f3ef020a`.

### 2026-08-02 — Original publication

Trigger: PI ruling on protocol erratum E72, option (a) — drop the confounded cells and regenerate rather than splice in the matched-scope replacements. Produced the regenerated 23-condition boards at both buffers, the recomputed BH families, and this summary. Nothing under `results/pairwise/` was modified; the superseded dated snapshots carry banners pointing here.
