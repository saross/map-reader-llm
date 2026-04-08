# Output Directory Standard

## Purpose

This document defines the standard structure for experimental outputs.
Every directory under `outputs/` must be immediately legible to someone
browsing the repository on GitHub — no tribal knowledge required.

## Status

- **Current state**: Organic growth from 10+ experimental phases; naming
  inconsistent across phases
- **Target**: Standardised layout with clear README, consistent naming,
  and explicit gitignore policy
- **Tracking gap**: `outputs/h11/pv-diag-384/` (top-tier F1=0.89 results)
  is gitignored and only exists on sapphire

## Artefact Types

Every pipeline in this project produces a subset of these artefact types:

| Artefact | Extension | Typical size | Track in git? | Description |
|----------|-----------|-------------|---------------|-------------|
| Detections | `.geojson` | 300–600 KB | **Yes** | GeoJSON FeatureCollection of detected symbols |
| Execution metadata | `.meta.json` | 450 KB–1 MB | **Yes** | Model, config, cost, usage stats, per-tile telemetry |
| Tile status | `.tiles.json` | 20 KB | **Yes** | Per-tile processing success/failure |
| Candidate manifest | `candidate_manifest.json` | ~290 KB | **Yes** | Maps candidate IDs to precise coordinates |
| Probabilities | `probabilities.json` | ~50 KB | **Yes** | Aggregated verification probabilities per candidate |
| Verified detections | `verified-*.geojson` | 500–600 KB | **Yes** | Detections enriched with verifier scores and reasoning |
| Threshold sweep | `threshold_sweep.json` | ~20 KB | **Yes** | Optimal threshold analysis with bootstrap CIs |
| Crop images | `crops/*.png` | ~24 MB total | **No** | Raster crops around candidates — regenerable |
| Batch working files | `batch_working/*.jsonl` | 50–80 MB/run | **No** | Raw API request/response payloads — regenerable |
| Logs | `*.log` | Varies | **No** | Runtime logs — ephemeral |

## Gitignore Policy

The following patterns must be gitignored globally (not per-directory):

```text
# Large regenerable artefacts
outputs/**/batch_working/
outputs/**/crops/
outputs/**/*.log
outputs/.active_files.*
```

Everything else under `outputs/` should be tracked. If a directory is
temporarily too large to commit, add a **specific** gitignore entry with
a comment explaining why, and create a TODO to resolve it.

## Proposed Directory Structure

```text
outputs/
├── README.md                              # This file (high-level map)
│
├── phase2a/                               # Phase 2a: calibration runs
│   ├── {condition}/                       # e.g., "brief-text", "image-only"
│   │   └── run_{N}/
│   │       ├── detections_*.geojson
│   │       ├── detections_*.meta.json
│   │       └── detections_*.tiles.json
│
├── h11/                                   # H11: tile size comparison + PV
│   ├── n1-outstanding-384/                # Single-pass proposer (N=1)
│   │   └── {condition}/run_{N}/           # e.g., "pro-text-high-t0"
│   │
│   ├── consensus-384/                     # 30-pass consensus proposer
│   │   └── 384/run_{N}/
│   │
│   ├── proposer-verifier-384/             # PV pipeline (N=1 proposer)
│   │   ├── proposer/                      # Raw proposer detections
│   │   ├── candidates/                    # Manifest + crops
│   │   │   ├── candidate_manifest.json
│   │   │   └── crops/                     # GITIGNORED
│   │   └── verified-{variant}.geojson     # Verifier outputs
│   │
│   └── pv-diag-384/                       # PV pipeline (consensus proposer)
│       └── verified/
│           └── {architecture}/            # e.g., "flash-high-text-4of5"
│               ├── candidate_manifest.json
│               ├── probabilities.json
│               └── crops/                 # GITIGNORED
│
├── production/                            # NEW: 55-map production run
│   ├── README.md                          # Describes run config and purpose
│   ├── proposer/
│   │   └── run_{N}/
│   │       ├── detections.geojson
│   │       ├── detections.meta.json
│   │       └── detections.tiles.json
│   ├── consensus/
│   │   └── voting-results.geojson
│   ├── verified/
│   │   ├── candidate_manifest.json
│   │   ├── probabilities.json
│   │   └── verified.geojson
│   └── evaluation/
│       ├── threshold_sweep.json
│       └── per-map-metrics.json
│
├── qgis-sanity-check/                     # QGIS inspection layers
│   ├── qgis_tp.geojson
│   ├── qgis_fp.geojson
│   ├── qgis_fn.geojson
│   └── sanity_check_summary.json
│
└── figures/                               # Generated figures
```

## Naming Conventions

- **Directories**: lowercase with hyphens (`proposer-verifier-384`,
  not `ProposerVerifier384`)
- **Run directories**: `run_{N}` with zero-padded numbers where
  practical (`run_01`, `run_02`)
- **Condition names**: `{model}-{thinking}-{modality}-{temperature}`
  (e.g., `flash-high-text-t0`, `pro-minimal-image-t07`)
- **Verified files**: `verified-{verifier-variant}.geojson`
  (e.g., `verified-adversarial-text.geojson`)

## Immediate TODOs

### 1. Track pv-diag-384 in git (requires sapphire access)

The top-tier results (F1=0.89) live in `outputs/h11/pv-diag-384/` on
sapphire. This directory is currently gitignored.

Steps:

1. Remove `outputs/h11/pv-diag-384/` from `.gitignore`
2. Ensure global patterns cover regenerable artefacts:

   ```text
   outputs/**/batch_working/
   outputs/**/crops/
   ```

3. Commit the lightweight outputs (verified GeoJSONs, probabilities,
   manifests, meta files)
4. Verify total committed size is reasonable (~5–15 MB expected)

### 2. Extract consensus-384 detections

The `outputs/h11/consensus-384/` directory has 30 runs of
`batch_working/` JSONL (2.3 GB) but no extracted detection GeoJSONs.
The extraction was done directly into `pv-diag-384/` on sapphire.

Either:

- Parse the JSONL files to extract GeoJSONs (preserves full provenance)
- Or accept that `pv-diag-384/` is the canonical processed output

### 3. Standardise gitignore

Replace the current per-directory gitignore entries with global
patterns. Current `.gitignore` has:

```text
outputs/h11/pv-diag-256/
outputs/h11/pv-diag-384/
outputs/pv/
outputs/retest/
```

These should become:

```text
# Large regenerable artefacts (global)
outputs/**/batch_working/
outputs/**/crops/
outputs/**/*.log
```

Plus any remaining specific entries with explanatory comments.

### 4. Production run output structure

Before running the 55-map production run, create the `outputs/production/`
directory with a README documenting the run configuration, cost, and
the ground truth filtering applied (hairy-only symbols from student data).
