# Superseded bootstrap confidence-interval stores (pre-repair, 2026-09-12)

> **Last revised**: 2026-09-12 (original publication). See [§ Changelog](#changelog) for revision history.

The two files here are the bootstrap confidence-interval (CI) stores exactly as
they stood before the 2026-09-12 path repair and re-run. They are kept because
this project archives rather than deletes, and because the repair rewrote
`source_file` on 472 of 496 entries and replaced the values of 85 — a reader who
wants the March 2026 numbers as first committed should read them here rather
than reconstruct them from `git log`.

| archived file | live path it came from | SHA-256 |
|---|---|---|
| `all-bootstrap-cis.json` | `results/all-bootstrap-cis.json` | `dc6b3ce5f969c348a66ae4015b18d5070b7a5d8e13d2a24d45e0e9def1836b6f` |
| `pv-all-bootstrap-cis.json` | `results/pv/all-bootstrap-cis.json` | `dc6b3ce5f969c348a66ae4015b18d5070b7a5d8e13d2a24d45e0e9def1836b6f` |

The two SHA-256 values are the same because the two live files were byte-identical
(verified 2026-09-12); the defect was duplicated across both copies. Archived at
worktree HEAD `1cd205856`.

## What was wrong with them

Established by `reports/name-keyed-cache-audit-2026-09-12.md` § 4 Finding 1 and
reproduced by `scripts/check_bootstrap_cis.py --check --remap`:

- **Every** one of the 496 `source_file` values named a `data/**` tree that has
  never existed in this repository. Applying the documented prefix remaps
  resolves 472 (456 to `outputs/retest/**`, 16 to
  `archive/outputs-experimental-pilot/pv/consensus-proposers/**`); the remaining
  24 are `consensus:<label>` pseudo-paths, never file paths at all.
- **85 of the 472** recorded an `n_detections` lower than their source file's
  feature count today, because the March 2026 out-of-band tile-recovery
  campaign disclosed as E70
  (`docs/methodology/preregistration/protocol-errata.md:3154-3199`) grew those
  pass files in place after the CIs were computed. 84 of the 85 carry a
  non-empty `patched` list in their `.tiles.json` sidecar.

## Reproducing the finding from these files

```bash
python scripts/check_bootstrap_cis.py --check --remap \
    archive/superseded-bootstrap-cis-2026-09-12/all-bootstrap-cis.json
```

Expected: 496 entries, 472 resolved, 24 unresolved, 387 match, 85 mismatch
(exit 1). The audit report quotes 456 / 40 / 371 / 85 because it applied only
the `data/retest/` remap; the extra 16 are the consensus-proposer files, all of
which still match their recorded counts.

## What replaced them

`reports/bootstrap-cis-repair-2026-09-12.md` records the repair in full. In
summary: paths rewritten to the files that exist today (originals preserved
per entry in `source_file_original`), and the 85 stale entries re-run on their
present source files with the estimator pinned to the March 2026 percentile
implementation, their superseded values preserved per entry in a `pre_e70`
sub-object.

## Changelog

### 2026-09-12 — Original publication

Archived the two pre-repair stores at worktree HEAD `1cd205856`, before
`scripts/repair_bootstrap_cis.py repair-paths` touched the live copies.
