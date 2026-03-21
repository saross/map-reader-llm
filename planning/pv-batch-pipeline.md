# Plan: Proposer-Verifier Pipeline (Dual-Mode)

## Context

The PV pipeline achieves F1=0.796 in the 60-tile pilot (adversarial verifier,
text-only track) — competitive with our best consensus result (F1=0.771). We
need to replicate on 340 tiles and optimise the verifier before scaling to all
21 proposer configurations. All proposer data exists — zero new proposer API
calls needed. Verifier cost is negligible (~$0.0001 per candidate).

**Dual-mode requirement (added 2026-03-20):** The pipeline must support both
Batch API and real-time API execution. Prompt construction is factored into a
shared intermediate representation (IR) with mode-specific serialisers, so the
same prompts are used regardless of execution mode. Published software must
offer both modes to end users.

## Architecture: 3 New Files

### `scripts/lib_verifier.py` — Core library (~450 lines)

Verifier library with shared prompt construction via an intermediate
representation (IR). Supports both Batch API and real-time API modes.

**IR types:** `TextItem` and `ImageItem` frozen dataclasses represent
mode-agnostic content. Two serialisers convert the IR:

- `content_items_to_batch_parts()` → JSONL-compatible dicts (base64 images)
- `content_items_to_sdk_parts()` → google-genai `types.Part` objects (binary)

**Shared prompt construction:**

- `build_reference_items()` — Reference examples as IR (text-only or image)
- `build_candidate_content()` — Full candidate prompt as IR
- `load_system_instruction()` — System instruction text from file
- `build_generation_config()` — Mode-agnostic config dict
- `gen_config_to_sdk()` — Converts config dict to SDK `GenerateContentConfig`

**Batch JSONL builders (use IR internally):**

- `build_verifier_jsonl()` — One JSONL line per candidate
- `build_verifier_jsonl_consensus()` — N copies per candidate for consensus
- `build_verifier_jsonl_multiscale()` — Two crops (75+150px) per JSONL line

**Real-time verification:**

- `verify_candidate_realtime()` — Verify one candidate via SDK (called per
  thread). Builds IR, serialises to SDK parts, calls API, parses response.
  Supports N iterations for consensus.

**Response parsing (unchanged):**

- `parse_verifier_results()` — Extracts `mound_probability` and `reasoning`
- `aggregate_consensus_votes()` — Groups by candidate ID, computes votes

### `scripts/run_pv.py` — Dual-mode orchestrator (~350 lines)

Two subcommands with `--mode batch|realtime` for the verify path:

**`extract`** — Crop extraction (direct call to `extract_candidates()`):

```text
python scripts/run_pv.py extract \
    --proposer outputs/retest/.../detections.geojson \
    --output-dir outputs/pv/crops-150/config-name \
    --padding 75
```

**`verify`** — Verification with mode selection:

```text
python scripts/run_pv.py verify \
    --crops-dir outputs/pv/crops-150/config-name \
    --verifier-config prompts/configs/verify_adversarial.json \
    --output-dir outputs/pv/results/adversarial-150/config-name \
    --mode batch|realtime \
    [--iterations 5] [--temperature 0.7] \
    [--workers 10] [--model gemini-3-flash] \
    [--multi-scale] [--dry-run]
```

For consensus: `--iterations 5 --temperature 0.7`
For multi-scale: `--multi-scale --crops-dir-75 ... --crops-dir-150 ...`

### `scripts/evaluate_pv_results.py` — Evaluation (~250 lines)

Threshold sweep and comparison:

```text
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
| `extract_candidates()` | `extract_candidates.py` (direct function call) |
| `upload_jsonl()`, `submit_batch_job()`, `poll_batch_job()`, etc. | `lib_batch_api.py` |
| `_encode_image_base64()`, `_mime_type_for()` | `lib_batch_api.py` |
| `LLMMetadataTracker`, `extract_gemini_metadata()`, `estimate_cost()` | `lib_llm_metadata.py` |
| `calculate_f1_internal()`, `bootstrap_ci()`, `bootstrap_effect_size_ci()` | `lib_advanced_metrics.py` |
| `apply_threshold()`, `cluster_across_passes()` | `merge_passes.py` |
| `consensus_to_gdf()` | `analyse_consensus_sweep.py` |

## New config files needed

- `prompts/system-instructions/verify_adversarial-multiscale.md` — Modified
  adversarial prompt referencing two scale views
- No new JSON configs needed — crop size and consensus are CLI parameters

## Implementation sequence

1. ~~`lib_batch_verifier.py` — JSONL builder + response parser (core)~~ [done 2026-03-19]
2. ~~Refactor → `lib_verifier.py` with shared IR layer and dual-mode
   serialisers (batch dicts + SDK `types.Part` objects)~~ [done 2026-03-20]
3. ~~Add `verify_candidate_realtime()` to `lib_verifier.py`~~ [done 2026-03-20]
4. ~~`run_pv.py extract` subcommand (calls `extract_candidates()` directly)~~ [done 2026-03-20]
5. ~~`run_pv.py verify --mode batch` — single variant, single iteration~~ [done 2026-03-20]
6. ~~`run_pv.py verify --mode realtime` — ThreadPoolExecutor path~~ [done 2026-03-20]
7. ~~Test on proposer #1 with adversarial-150 baseline → verify matches pilot~~ [done 2026-03-20]
   882 candidates, 340 tiles, F1=0.767 at threshold 0.2 (pilot: F1=0.796
   on 60 tiles — within CI). Full threshold sweep from 0.1–0.9 confirms
   expected precision/recall trade-off curve.
8. ~~Add `--iterations` and `--temperature` for consensus (both modes)~~ [done 2026-03-20]
   Built into both batch and realtime paths from the start.
9. ~~Add `--multi-scale` for dual-crop variant~~ [skipped — crop size insensitive,
   Obs 166. No benefit from multi-scale given 75–300px equivalence.]
10. ~~`evaluate_pv_results.py` — threshold sweep + comparison~~ [done 2026-03-20]
    Sweep + compare subcommands with bootstrap CIs. Verified on proposer #1:
    optimal T=0.15, F1=0.770 [0.726–0.811].
11. ~~Run Phase 1 verifier optimisation matrix~~ [done 2026-03-20]
    Crop size (4 sizes), consensus (N=1 vs N=5), verifier strategy (3 types).
    All parameters insensitive. See `results/pv/phase1/pv-phase1-analysis.md`.
12. ~~Analyse results, select optimal verifier~~ [done 2026-03-21]
    Optimal: adversarial-text, 150px, N=1, T=0.0. Decision 23–24.
13. ~~Run Phase 2 full evaluation~~ [done 2026-03-21]
    25 experiments + 6 top-performer additions. PV improves F1 in 25/25.
    New project best: F1=0.831 (text 5-of-10 + PV).
    See `results/pv/phase2/pv-phase2-analysis.md`.

## Verification

1. `ruff check` on all new files
2. Dry-run on proposer #1 to verify JSONL structure
3. Single batch submission → verify response parsing matches pilot format
4. Compare adversarial-150 baseline result against pilot (should be similar
   F1 range, adjusted for 340 vs 60 tiles)
5. Threshold sweep produces expected curve shape (precision up, recall down)
