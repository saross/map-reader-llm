# Quarantine Manifest — v2-Verifier Contamination

Complete inventory of files moved into this quarantine. Moves performed with
`git mv` for tracked files. Directory structure preserved inside each
sub-folder.

## Summary

| Sub-folder | Original location | Files | Bytes (approx) |
|------------|-------------------|------:|---------------:|
| `leaderboard-cells/` | `results/leaderboard/cells/` | 1 | 47 KB |
| `e47-v1-vs-v2/` | `results/e47-v1-vs-v2/` | 80 | ~5 MB |
| `raw-outputs/` | `outputs/h11/...`, `outputs/qgis-sanity-check-v2-30m/` | 19 | ~3 MB |

Total: 100 files moved.

## Detailed Inventory

### `leaderboard-cells/`

| Original path | New path | Contamination type | Notes |
|---------------|----------|--------------------|-------|
| `results/leaderboard/cells/gold-standard-v2-greedy-v2-327tile.json` | `archive/v2-verifier-contamination/leaderboard-cells/gold-standard-v2-greedy-v2-327tile.json` | Calibration-on-test | Greedy consensus on 327 GS tiles, v2 verifier |

### `e47-v1-vs-v2/`

The entire `results/e47-v1-vs-v2/` directory was moved as a unit. It contains
the v1-vs-v2 verifier prompt-development comparison study across 80 files in
the sub-trees:

- `detect-single-pass/` (16 files) — single-pass threshold sweeps at 20-50 m buffers, v1 and v2
- `grid/` (20 files) — grid threshold sweeps, v1-1of5 through v2-5of5
- `grid-multibuffer/` (32 files) — grid sweeps at 20-50 m for 3of5 and 4of5 consensus
- `pairwise/` (4 files) — v1-vs-v2 pairwise permutation tests
- `v1/`, `v2/`, `v1-sweep/`, `v2-sweep/` (8 files) — per-prompt buffer sensitivity and sweep results

Contamination type for all 80 files: **entangled comparison**. The v1 halves
of this study are methodologically entangled with the v2 comparison — v2 was
the experimental arm, v1 the control. Quarantining the whole directory
preserves the integrity of the prompt-development record without cherry-
picking.

### `raw-outputs/`

| Original path | New path | Contamination type | Notes |
|---------------|----------|--------------------|-------|
| `outputs/h11/gold-standard-v2/verified-v2/` | `raw-outputs/gold-standard-v2--verified-v2/` | Calibration-on-test | GS-set detection, v2 verification |
| `outputs/h11/wbf/gold-standard-v2-detect/verified-v2/` | `raw-outputs/wbf-gold-standard-v2-detect--verified-v2/` | Calibration-on-test | WBF variant on GS, v2 verification |
| `outputs/h11/e47-propose-brief/verified-v2/` | `raw-outputs/e47-propose-brief--verified-v2/` | Prompt-dev entanglement | Part of the e47 v1-vs-v2 study |
| `outputs/h11/proposer-verifier-384/verified-adversarial-text-v2-prompt/` | `raw-outputs/proposer-verifier-384--verified-adversarial-text-v2-prompt/` | Partial (487-tile corpus overlaps GS) | 487-tile matrix with v2 verifier; 4 GS maps are a subset |
| `outputs/h11/v2-proposer-test/verified-adversarial-text-v2/` | `raw-outputs/v2-proposer-test--verified-adversarial-text-v2/` | Calibration-on-test | Corpus = 487 GS tiles (K-35-052-4, K-35-053-3, K-35-062-2, K-35-078-1); v2 verifier |
| `outputs/h11/propose-brief-v1-test/verified-adversarial-text-v2/` | `raw-outputs/propose-brief-v1-test--verified-adversarial-text-v2/` | Calibration-on-test | Same 4-map GS corpus; v2 verifier; sibling `verified-adversarial-text-v1/` NOT moved (clean) |
| `outputs/qgis-sanity-check-v2-30m/` | `raw-outputs/qgis-sanity-check-v2-30m/` | Calibration-on-test | GS-set QGIS sanity-check with v2 verifier |

## Files NOT Moved (Verified Clean or Out-of-Scope)

- `outputs/55maps-generalisation/verified-v2/` — 55-map student corpus, disjoint
  from the 4 GS maps. Valid out-of-sample v2 evaluation pending student
  ground-truth.
- `outputs/h11/proposer-verifier-384/verified-*-v2.geojson` (top-level, six
  files) — filename "v2" denotes a second verification pass, NOT the v2
  prompt. All use `verify_adversarial.md` / `verify_brief.md` /
  `verify_checklist.md` (v1 instruction files). See "Flag for manual review"
  below.
- `outputs/h11/propose-brief-v1-test/verified-adversarial-text-v1/` — v1
  verifier output, clean.
- `outputs/h11/v2-proposer-test/detections-propose_brief_v2-*` — proposer v2
  prompt output (separate experiment from the verifier v2 prompt).
- `prompts/system-instructions/verify_adversarial_v2.md` — prompt file itself.
- `prompts/configs/verify_adversarial-text_v2.json` — config file itself.
- `scripts/11maps-gold-standard-v2.sh`, `scripts/build_condition_inventory.py`
  — scripts; "v2" refers to corpus not verifier.
- `configs/run-configs/55maps_text_generalisation_retrospective.yaml` — config.
- Historical documentation in `docs/`, `planning/`, `reports/`.

## Flag for Manual Review

1. `planning/condition-inventory.json` entries 3303-3565 (six entries with
   `"id": "pv-*-v2"`) are marked `status: "QUARANTINED"` with the note "v2
   verifier — data leakage from test pool". However, their underlying
   `.meta.json` files show `instruction_file: "verify_adversarial.md"` (or
   `verify_brief.md`, `verify_checklist.md`) — that is, **v1 instruction
   files**. The filename suffix "-v2" here appears to mark a second
   verification pass, not the v2 prompt. The author should verify whether
   these six entries really are contaminated; if not, the inventory note is
   mis-labelled and the status should probably revert to `PV_READY`. This
   quarantine action has left the files in place and the inventory status
   unchanged.

2. `scripts/sapphire-paper-eval.sh` and `configs/pv-paper-conditions.yaml`
   reference `outputs/h11/pv-diag-384/verified/flash-high-text-16of30/` for
   the paper headline. Verifier version for that file is **v1**
   (`verify_adversarial.md`, hash `2518d5298...`); the headline F1 = 0.904 is
   clean. Documented here for audit clarity.
