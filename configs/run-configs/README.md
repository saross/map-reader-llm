# Run-Config Directory

YAML configuration files consumed by `scripts/run_generalisation.py`.
Each file captures the full parameter set for a single generalisation
run so that runs are exactly reproducible from `run-config + launcher`.

## Usage

```bash
# Run every stage in order (default):
python scripts/run_generalisation.py all \
    --run-config configs/run-configs/<name>.yaml \
    --run-name <run-name>

# Run a single stage:
python scripts/run_generalisation.py verify \
    --run-config configs/run-configs/<name>.yaml \
    --run-name <run-name>

# Inspect help:
python scripts/run_generalisation.py --help
python scripts/run_generalisation.py all --help
```

Any CLI flag overrides the corresponding YAML value. Flags the YAML
does not supply must be passed on the command line.

## Schema

```yaml
run_name: <string>                 # default output subdir name under outputs/
output_root: <path>                # default: outputs/
service_tier: flex | standard      # applies to proposer + verify

proposer:
  config: <path>                   # prompts/configs/*.json
  manifest: <path>                 # tile manifest JSON (list of filenames)
  tiles_dir: <path>                # directory containing the tile images
  tile_size: <int>                 # tile pixel dimension (e.g. 384)
  temperature: <float>             # 0.0-2.0
  thinking_level: minimal | low | medium | high
  passes: <int>                    # K proposer passes
  mode: realtime | batch           # usually realtime
  workers: <int>                   # parallel requests (Tier 3: 60)
  max_retries: <int>
  use_cache: <bool>                # Gemini context caching

consensus:
  vote_threshold: <int>            # 1..passes
  dedup_radius_m: <float>          # 20.0 (preregistered)

extract:
  padding: <int>                   # px around detection centroid
  rasters_dir: <path>              # source rasters for cropping
  tiles_dir: <path>                # optional fallback

verify:
  config: <path>                   # prompts/configs/verify_*.json
  mode: realtime | batch
  workers: <int>

evaluate:
  prob_threshold: <float>          # 0.0-1.0
  buffers: [<int>, ...]            # metre values for Hungarian matching
  bootstrap: <int>                 # bootstrap iterations
  seed: <int>                      # RNG seed
  ground_truth: <path>             # reference GeoJSON
  bounds: <path>                   # evaluation bounds GeoJSON
```

All paths are resolved relative to the repository root (the launcher
sets `cwd` to the repo root when invoking subprocess scripts).

## Available configs

### `55maps_image_generalisation.yaml`

The headline image-track generalisation run reported in the paper:
plus-hp library, HIGH thinking, T=0.7, K=5 proposer passes; greedy
3-of-5 consensus at 20 m radius; text-only adversarial v1 verifier at
probability threshold 0.15; evaluation at 20/30/40/50 m buffers with
1000-iteration bootstrap. Expected scope: 8,541 tiles across 55 maps,
4,770 reference mounds. Expected cost: ~$350 at Flex (8,541 × 5 ×
~$0.0082 per tile-pass plus ~$5 verifier flat fee; see
`_estimate_cost` in `scripts/run_generalisation.py`). Prior-text
55-map run cost $12.4 verifier + ~$0.003/tile proposer; image costs
more because of the 13 in-context example images sent per call.

## Provenance

When a run executes, the launcher writes the following artefacts to
`outputs/<run-name>/`:

- `launch_manifest.json` — git commit SHA, input file SHA256s, resolved
  config (YAML + CLI merged), hostname, Python version, full CLI
  invocation. Everything a replicator needs to verify the run.
- `resolved_config.yaml` — the merged config actually used.
- `experiment_intent.md` — human-readable pipeline description.
- `cost_manifest.json` — totals, per-stage breakdown, per-map attribution,
  unit costs (cost_per_tile, cost_per_map, cost_per_detection,
  cost_per_reference_mound).
- `run.log` — tee'd stdout/stderr from every stage.
- Per-stage outputs under `proposer/`, `consensus/`, `crops/`,
  `verified/`, `evaluation/`.

## Reproducibility requirements

The launcher aborts with a clear error if the git working tree is
dirty (override with `--allow-dirty`, not recommended for the paper
run). SHA256 of every input file is recorded so replicators can
confirm they have the same data.

For the headline paper result, the recommended workflow is:

1. Clone the repo at the commit cited in the paper's code-availability
   section (or set `git checkout <commit_sha>`).
2. Install dependencies from `requirements-lock.txt` (or `uv sync`).
3. Place input rasters and tiles per the paths in the YAML.
4. Launch with `python scripts/run_generalisation.py all --run-config
   configs/run-configs/<name>.yaml`.
5. Confirm the interactive intent check, then wait for completion.
6. Compare `cost_manifest.json` and `evaluation/summary.md` with the
   published numbers (modulo Gemini API non-determinism at T=0.7).
