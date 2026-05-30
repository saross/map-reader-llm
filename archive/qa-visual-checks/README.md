# Archived QGIS visual QA spot-checks

Archived 2026-05-30 during the run-registry fan-out review (sub-step 1), once
confirmed they are not experimental runs and are referenced only by their own
export scripts and frozen historical records.

## Contents

| Dir | What it is | Export script (still live in `scripts/`) |
|-----|-----------|-------------------------------------------|
| `qgis-dedup-check/` | Visual QA of detection de-duplication | `scripts/export_dedup_visual_check.py` |
| `qgis-sanity-check/` | General QGIS sanity-check export | `scripts/export_qgis_sanity_check.py` |
| `qgis-wbf-check/` | Visual QA of WBF fusion output | `scripts/export_wbf_visual_check.py` |

## Why archived (not deleted)

These are one-off visual QA artefacts, not experimental runs — so they are
omitted from the run registry (`docs/manifest-schemas/run-registry.schema.json`
explicitly lists `qgis-*/` as non-runs). They were live under `outputs/` only as
incidental QA output. Per the project's "archive, never delete" policy they are
preserved here, browsable in the tree.

## Regenerating

The three `scripts/export_*_check.py` tools remain in place. Re-running any of
them recreates its check under `outputs/` (the scripts' default output path is
unchanged); the copy here is the historical snapshot from the QA pass.

## Referenced by (frozen historical records — intentionally not updated)

- `results/documentation-audit/results-audit-2026-04-21.md` (dated audit)
- `planning/nas-migration-baseline-*.txt` (dated NAS-migration file inventories)
