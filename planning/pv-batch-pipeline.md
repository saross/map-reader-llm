# Plan: Proposer-Verifier Batch Pipeline

## Context

The PV pipeline achieves F1=0.796 in the 60-tile pilot (adversarial verifier,
text-only track) — competitive with our best consensus result (F1=0.771). We
need to replicate on 340 tiles and optimise the verifier before scaling to all
21 proposer configurations. All proposer data exists — zero new proposer API
calls needed. Verifier cost is negligible (~$0.0001 per candidate).

## Architecture: 3 New Files

### `scripts/lib_batch_verifier.py` — Core library (~200 lines)

Verifier-specific batch functions. Reuses `lib_batch_api.py` for upload/submit/
poll/retrieve lifecycle; implements verifier JSONL building and response parsing.

**Key functions:**

- `build_verifier_jsonl()` — One JSONL line per candidate: reference examples
  (text labels or images from config), crop image (base64), system instruction,
  generation config. Supports configurable temperature for consensus.
- `build_verifier_jsonl_consensus()` — Emits N copies per candidate with unique
  keys (`candidate_00042_iter3`) for consensus voting.
- `build_verifier_jsonl_multiscale()` — Two crops (75+150px) per JSONL line.
- `parse_verifier_results()` — Extracts `mound_probability` and `reasoning` from
  batch response lines (different schema from proposer's `box_2d` detections).
- `aggregate_consensus_votes()` — Groups by candidate ID, computes vote count
  and mean probability.

### `scripts/run_pv_batch.py` — Orchestrator (~300 lines)

Two subcommands:

**`extract`** — Crop extraction wrapper:
```
python scripts/run_pv_batch.py extract \
    --proposer outputs/retest/.../detections.geojson \
    --output-dir outputs/pv-batch/crops-150/config-name \
    --padding 75
```

**`verify`** — Full verifier batch lifecycle:
```
python scripts/run_pv_batch.py verify \
    --crops-dir outputs/pv-batch/crops-150/config-name \
    --verifier-config prompts/configs/verify_adversarial.json \
    --output-dir outputs/pv-batch/results/adversarial-150/config-name \
    [--iterations 5] [--temperature 0.3] [--multi-scale] [--dry-run]
```

For consensus: `--iterations 5 --temperature 0.7`
For multi-scale: `--multi-scale --crops-dir-75 ... --crops-dir-150 ...`

### `scripts/evaluate_pv_results.py` — Evaluation (~250 lines)

Threshold sweep and comparison:
```
python scripts/evaluate_pv_results.py \
    --probabilities outputs/pv-batch/results/.../probabilities.json \
    --manifest outputs/pv-batch/crops-150/.../candidate_manifest.json \
    --output-dir results/pv-batch/phase1/adversarial-150/config-name

python scripts/evaluate_pv_results.py --compare \
    --results-dirs results/pv-batch/phase1/*/config-name
```

Sweeps probability threshold 0.0–1.0 in 0.05 steps. At each threshold: filter
candidates, convert to GeoDataFrame, compute F1/P/R with bootstrap CIs via
`lib_advanced_metrics.calculate_f1_internal()`.

## Phase 1: Verifier Optimisation

### Proposer inputs (4 configs, all existing data)

| # | Proposer | Candidates | Recall | Rationale |
|---|---|---|---|---|
| 1 | Text N=1 T=0.0 minimal | ~913 | 0.798 | Matches pilot — direct comparison |
| 2 | Text N=1 T=0.7 HIGH | ~1,370 | 0.764 | Tests verifier under HIGH FP load |
| 3 | Text N=5 T0.7 1-of-5 | ~1,333 | 0.859 | Practical high-recall |
| 4 | Text N=30 HIGH 21-of-30 | ~520 | 0.757 | Our best F1 — can PV improve it? |

### Verifier variants to test

| Variant | Crop | Passes | Temp | Notes |
|---|---|---|---|---|
| adversarial-150 (baseline) | 150px | 1 | 0.0 | Pilot's best — reference |
| adversarial-75 | 75px | 1 | 0.0 | Tighter crop, better SNR? |
| adversarial-150-n5 | 150px | 5 | 0.3, 0.7, 1.0 | Consensus verification |
| adversarial-75-n5 | 75px | 5 | best T | If both 75px and N=5 help |
| std+adv ensemble | 150px | 1+1 | 0.0 | Cross-framing filter |
| multiscale | 75+150px | 1 | 0.0 | Both scales in one prompt |

Test on proposer #1 first. If 75px or N=5 improves, extend to all 4 proposers.
If both improve, test combined. If promising direction found, consider
extending (e.g., 50px crops).

Total Phase 1 cost: ~$10-15.

### Consensus temperature note

Test verifier consensus at T=0.3, T=0.7, T=1.0 (matching proposer temperature
sweep) on proposer #1 only. Use winning temperature for remaining proposers.

## Phase 2: Full Evaluation

Apply optimal verifier (from Phase 1) to all 21 proposer configs (16 ready
now, 5 pending HIGH image track). Includes both text and image tracks at N=1,
N=5, N=30 with best-F1 and highest-recall proposer strategies.

Total Phase 2 cost: ~$3-5 (21 configs × optimal verifier only).

## Existing code to reuse (no modification needed)

| Function | Source |
|---|---|
| `extract_candidates.py` | Crop extraction at any `--padding` |
| `upload_jsonl()`, `submit_batch_job()`, `poll_batch_job()`, etc. | `lib_batch_api.py` |
| `_encode_image_base64()` | `lib_batch_api.py` |
| `calculate_f1_internal()`, `bootstrap_ci()`, `bootstrap_effect_size_ci()` | `lib_advanced_metrics.py` |
| `apply_threshold()`, `cluster_across_passes()` | `merge_passes.py` |
| `consensus_to_gdf()` | `analyse_consensus_sweep.py` |

## New config files needed

- `prompts/system-instructions/verify_adversarial-multiscale.md` — Modified
  adversarial prompt referencing two scale views
- No new JSON configs needed — crop size and consensus are CLI parameters

## Implementation sequence

1. `lib_batch_verifier.py` — JSONL builder + response parser (core)
2. `run_pv_batch.py extract` subcommand (wraps extract_candidates.py)
3. `run_pv_batch.py verify` subcommand — single variant, single iteration
4. Test on proposer #1 with adversarial-150 baseline → verify matches pilot
5. Add `--iterations` and `--temperature` for consensus
6. Add `--multi-scale` for dual-crop variant
7. `evaluate_pv_results.py` — threshold sweep + comparison
8. Run Phase 1 verifier optimisation matrix
9. Analyse results, select optimal verifier
10. Run Phase 2 full evaluation

## Verification

1. `ruff check` on all new files
2. Dry-run on proposer #1 to verify JSONL structure
3. Single batch submission → verify response parsing matches pilot format
4. Compare adversarial-150 baseline result against pilot (should be similar
   F1 range, adjusted for 340 vs 60 tiles)
5. Threshold sweep produces expected curve shape (precision up, recall down)
