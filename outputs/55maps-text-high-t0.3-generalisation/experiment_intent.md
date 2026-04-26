# Experiment intent: 55maps-text-high-t0.3-generalisation

Generated: 2026-04-26T08:18:16Z
Script: `scripts/run_generalisation.py` v1.0.0

## Pipeline

1. **Proposer** (`prompts/configs/detect_brief-text.json`, thinking=high, T=0.3, K=5)
2. **Consensus** (greedy, 20.0 m radius, vote_t=4)
3. **Extract** (padding 75 px, rasters: inputs/rasters/Russian1981_32635)
4. **Verify** (`prompts/configs/verify_adversarial-text.json`, mode=realtime)
5. **Evaluate** (prob_t=0.15, buffers=[20, 30, 40, 50] m, bootstrap=1000)

## Data

- Tile manifest: `inputs/tiles_384_55maps/full_evaluation_manifest.json`
- Ground truth: `inputs/vectors/references/student-mounds-55maps.geojson`
- Evaluation bounds: `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson`

## Expected cost

- ~$355 (Flex tier estimate)

## Outputs

- `launch_manifest.json` — reproducibility metadata
- `cost_manifest.json` — full cost accounting
- `consensus/` — voted candidate GeoJSON
- `verified/` — verifier probabilities + final filtered GeoJSON
- `evaluation/` — per-buffer F1 / P / R with bootstrap CIs
