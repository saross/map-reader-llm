# E72 board regeneration — 23-condition round-robin

> **Last revised**: 2026-08-02 (original publication — E72 remediation, Phase R3). See [§ Changelog](#changelog) for revision history.

**Purpose**: supplies the regenerated leaderboard the Principal Investigator's ruling on protocol erratum [E72](../../docs/methodology/preregistration/protocol-errata.md) calls for — the March 2026 round-robin boards with the three coverage-confounded `flash-min-text-t10` cells dropped, the Benjamini–Hochberg (BH) false-discovery-rate (FDR) family recomputed over the retained pairs, and the greedy-clique tiers re-run.

**Produced**: 2026-08-02, on sapphire, from repository commit `bc45133b4` by `scripts/regen_e43_board.py`. Zero application programming interface (API) calls; zero permutation tests re-run.

## 1. What was dropped, and why

The condition family `flash-min-text-t10` (five aliases across the repository; the underlying study is `outputs/h11/consensus-384-UNINTENDED-T1.0/`) covers **240 of the 487** evaluation tiles by design, but the 2026-03-26 bounds standardisation scored it against the full 487-tile bounds. Every mound in the 247 unprocessed tiles became an automatic false negative, understating that arm's F1 by roughly 0.17–0.19. Membership was derived from each test artefact's recorded `condition_*.source` provenance, never from labels — the condition carries five aliases across the repository, so label matching is unsafe. A provenance walk of `results/pairwise/` flags **148** test artefacts, matching the remediation report's inventory.

| Board | Conditions before | Dropped | Conditions after | Pairs before | Pairs dropped | Pairs after |
|---|--:|--:|--:|--:|--:|--:|
| `leaderboard-20m` | 26 | 3 | 23 | 325 | 72 | 253 |
| `leaderboard-30m` | 25 | 3 | 22 | 300 | 69 | 231 |

The dropped conditions are identical on both boards: `flash-min-text-t10 N=10 N=10, 9-of-10`, `flash-min-text-t10 N=30 N=30, 22-of-30`, `flash-min-text-t10 N=5 N=5, 5-of-5`.

The matched-scope replacements for these cells are filed as their own first-class analysis at `results/e43-matched-temperature/` and are deliberately **not** spliced into this board — the two analyses answer different questions and were run under different protocols.

## 2. Validation gates

All three gates passed before anything was written:

- **Gate A** — the per-pair JSONs reproduce each board's committed `run_manifest.json` exactly (same pair set, same raw p-values, same ΔF1).
- **Gate B** — recomputing the FULL board (nothing dropped) reproduces the published snapshot: `leaderboard-20m` 265/325 significant, 9 tiers; `leaderboard-30m` 243/300 significant, 9 tiers. This proves the BH and tiering reimplementation is faithful before its output is trusted for the reduced board.
- **Gate C** — every condition's F1, precision, recall and detection count agree across all tests it appears in.
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
| flash-high-text-16-of-30--flash-min-vf (t=0.2) | flash-high-text-4-of-5--flash-min-vf (t=0.15) | 0.0398 | 0.0488 | 0.0503 | significant → ns |

### `leaderboard-30m` — 9 tiers → 8 tiers

No retained condition changed tier number. The board loses the tier(s) the dropped cells occupied and nothing else moves.

**BH status changes among the 231 retained pairs**: 0. No retained pair changed significance verdict when the family shrank.

### 3.1 One difference from the published snapshot that is NOT E72

Greedy-clique tiering is order-dependent, and the published 20 m snapshot (`results/paper-tables/leaderboard_tiers_20m.md`) ranks one condition out of F1 order: `flash-high-image-3-of-5--flash-min-vf (t=0.15)` (F1 0.778) sits at rank 10, ahead of two higher-F1 conditions. Processed there it joins the 0.814 clique; processed in strict F1 order it is reached only after `flash-high-text N=10` (F1 0.797) has already opened the next tier — and that boundary rests on a single borderline pair (`FH text 26/30` versus `FH text 9/10`, q = 0.046).

This script uses the documented F1-descending order throughout, so the following condition sits one tier lower here than in the March snapshot **for reasons unrelated to the coverage confound**:

| Condition | Tier (published snapshot) | Tier (F1-ordered recomputation) |
|---|--:|--:|
| flash-high-image-3-of-5--flash-min-vf (t=0.15) | 3 | 4 |

Gate D proves the attribution: replaying the clique under the published rank order reproduces the published tier sizes exactly, so the difference is processing order, not statistics.

## 4. The smaller BH families

The same confounded p-values also entered three smaller BH families. Memberships below are derived from the family manifests themselves, not assumed. In this project BH is applied **within** each declared family, so only families containing a confounded member are affected; the script asserts the others are clean rather than trusting that.

| Family artefact | Family | Members (published) | Dropped | Members (retained) | Significant (published, retained members) | Significant (recomputed) | Status changes |
|---|---|--:|--:|--:|--:|--:|--:|
| `results/pairwise/20m` | `confirmatory` | 26 | 3 | 23 | 17 | 16 | 1 |
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

### 2026-08-02 — Original publication

Trigger: PI ruling on protocol erratum E72, option (a) — drop the confounded cells and regenerate rather than splice in the matched-scope replacements. Produced the regenerated 23-condition boards at both buffers, the recomputed BH families, and this summary. Nothing under `results/pairwise/` was modified; the superseded dated snapshots carry banners pointing here.
