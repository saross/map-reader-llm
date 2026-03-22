# Plan: Comprehensive Analysis Session

## Context

Multiple data streams are now complete or nearly complete. The code audit (commit `db7745f`) fixed the consensus.json key mismatch and deduplication algorithm divergence, meaning previous pairwise comparisons may have used incorrect data. All analyses need re-running with the corrected code, and new analyses are needed for Phase 3c Track 2 and the 384px diagnostic results.

**FDR correction is deferred** — requires all experimental factors complete (Phase 3c Track 1 image is at 41/125).

## Data available now

| Dataset | Status | Location |
|---------|--------|----------|
| Phase 3c Track 2 text | 98/100 (finishing imminently) | `outputs/retest/phase3c/track2-text/` |
| 384px Config A (text N=10) | 10/10 complete | `outputs/h11/pv-diag-384/text-n10/` |
| 384px Config B (image N=5) | 5/5 complete | `outputs/h11/pv-diag-384/image-n5/` |
| 384px Config C (text baseline) | 1/1 complete | `outputs/h11/pv-diag-384/text-baseline/` |
| 384px Config D (image baseline) | 1/1 complete | `outputs/h11/pv-diag-384/image-baseline/` |
| All previous phases | Patched (306 tiles recovered) | `outputs/retest/` |
| PV Phase 2 results | 25 configs evaluated | `outputs/pv/results/phase2/` |

---

## Analysis Tasks (in execution order)

### Task 1: Phase 3c Track 2 consensus diversity analysis

**Purpose**: Test whether diversity across consensus voting passes (H9) improves detection for the text track.

**Method**: Use `analyse_consensus_sweep.py` with the Phase 3c grouping:
- Condition A (baseline): 5 identical passes → consensus
- Condition B (text diversity): 5 instruction variants → consensus
- Condition D (temperature diversity): 5 temperatures → consensus
- Condition E (full diversity): text + temperature → consensus

Each condition has 5 replications (run_k from each sub-condition forms replication k).

**Command**:

```bash
python scripts/analyse_consensus_sweep.py \
    --study-yaml studies/retest/phase3c-h9-diversity-track2.yaml \
    --output-dir results/phase3c-diversity/track2-text \
    --bootstrap 1000 --seed 42
```

**Note**: Check whether the script supports the Phase 3c grouping structure or needs manual invocation with per-condition directories.

**Run on**: sapphire (bootstrap-intensive)

### Task 2: 384px PV pipeline (17 verification runs)

**Purpose**: Run the full PV pipeline on all 384px proposer outputs across all consensus thresholds.

#### 2a: Compute consensus GeoJSON for multi-run configs

Use `generate_consensus_gdf()` from `lib_consensus.py` to merge proposer runs into consensus GeoDataFrames at each vote threshold.

- **Config A** (text N=10): 10 thresholds (1-of-10 through 10-of-10)
- **Config B** (image N=5): 5 thresholds (1-of-5 through 5-of-5)
- **Configs C, D**: Single-pass, no consensus needed

Write each consensus GeoDataFrame as GeoJSON for crop extraction.

**Output**: 15 consensus GeoJSON files + 2 single-pass GeoJSON files = 17 total

#### 2b: Extract crops for each of the 17 GeoJSON files

```bash
# For each consensus/baseline GeoJSON:
python scripts/extract_candidates.py \
    --proposer <geojson> \
    --rasters-dir inputs/rasters \
    --output-dir outputs/h11/pv-diag-384/crops/<threshold_name> \
    --padding 75
```

**Check**: Verify 0 tile fallbacks in every extraction summary.

#### 2c: Run PV verifier on all 17 crop sets (Batch API)

```bash
# For each crop set:
python scripts/run_pv.py verify \
    --crops-dir outputs/h11/pv-diag-384/crops/<threshold_name> \
    --verifier-config prompts/configs/verify_adversarial-text.json \
    --output-dir outputs/h11/pv-diag-384/verified/<threshold_name> \
    --mode batch
```

**API review gate**: ~14,000 verification calls, Gemini 3 Flash, Batch API, ~$1.75. Approved — Batch API confirmed by user.

#### 2d: Evaluate all 17 verified outputs

```bash
# For each verified output:
python scripts/evaluate_pv_results.py sweep \
    --probabilities outputs/h11/pv-diag-384/verified/<threshold>/probabilities.json \
    --manifest outputs/h11/pv-diag-384/crops/<threshold>/candidate_manifest.json \
    --output-dir results/h11-384-pv-diagnostic/<threshold>
```

**Run on**: sapphire (bootstrap CIs for all 17 configs)

### Task 3: Re-run existing pairwise comparisons (52 comparisons)

**Purpose**: The audit commit fixed two bugs that may have affected previous results:
1. `consensus.json` key mismatch — scripts read `"results"` but producer writes `"consensus"`, making consensus override dead code
2. Deduplication algorithm divergence — O(N²) greedy vs cKDTree produced different cluster assignments

**Method**: Re-run `compute-pairwise-effect-sizes.py` with the corrected code.

```bash
# On sapphire:
python scripts/compute-pairwise-effect-sizes.py \
    --data-dir outputs/ \
    --pv-dir outputs/pv/ \
    --output results/pv/pairwise-effects/pairwise-effect-sizes-v2.json \
    --workers 20
```

**Output**: `pairwise-effect-sizes-v2.json` with corrected bootstrap CIs and p-values for all 52 comparisons. Compare to v1 results to quantify the impact of the bug fixes.

**Run on**: sapphire (CPU-intensive, ~1 min per comparison × 52 = ~1 hour with 20 workers)

### Task 4: New pairwise comparisons — 384px diagnostic

**Purpose**: Formally compare 384px PV results against 512px benchmarks and each other.

**New comparison groups** (all use paired bootstrap on shared geographic area):

#### Group I: 384px tile size effect under PV (6 comparisons)

| # | Condition A | Condition B | Question |
|---|-------------|-------------|----------|
| I1 | 384px text 1-of-10 + PV | 512px text 1-of-10 + PV | Single diverse pass: tile size effect |
| I2 | 384px text 5-of-10 + PV | 512px text 5-of-10 + PV | **Headline**: Goldilocks zone at 384px vs 512px |
| I3 | 384px text 10-of-10 + PV | 512px text 5-of-10 + PV | Strict 384px consensus vs moderate 512px |
| I4 | 384px image 3-of-5 + PV | 512px image 3-of-10 + PV | Image track tile size effect |
| I5 | 384px text N=1 T=0.0 + PV | 512px text N=1 T=0.0 + PV | Deterministic baseline tile size effect |
| I6 | 384px image N=1 T=0.0 + PV | 512px image N=1 T=0.0 + PV | Image deterministic baseline |

#### Group J: 384px modality effect (4 comparisons)

| # | Condition A | Condition B | Question |
|---|-------------|-------------|----------|
| J1 | 384px text 5-of-10 + PV | 384px image 3-of-5 + PV | Text vs image at moderate consensus |
| J2 | 384px text 1-of-10 + PV | 384px image 1-of-5 + PV | Text vs image at loose consensus |
| J3 | 384px text N=1 T=0.0 + PV | 384px image N=1 T=0.0 + PV | Text vs image at single-pass |
| J4 | 384px text 10-of-10 + PV | 384px image 5-of-5 + PV | Text vs image at strict consensus |

#### Group K: 384px consensus threshold sweep (4 comparisons)

| # | Condition A | Condition B | Question |
|---|-------------|-------------|----------|
| K1 | 384px text 1-of-10 + PV | 384px text 5-of-10 + PV | Loose vs moderate (recall vs precision) |
| K2 | 384px text 5-of-10 + PV | 384px text 10-of-10 + PV | Moderate vs strict (Goldilocks test) |
| K3 | 384px text N=1 T=0.0 + PV | 384px text 5-of-10 + PV | Does consensus add value at 384px? |
| K4 | 384px text N=1 T=0.0 + PV | 384px text 1-of-10 + PV | T=0.0 vs T=0.7 single-pass |

#### Group L: Phase 3c diversity under PV (3 comparisons, if feasible)

| # | Condition A | Condition B | Question |
|---|-------------|-------------|----------|
| L1 | Phase 3c Cond A (baseline) + PV | Phase 3c Cond B (text diversity) + PV | Does text diversity help PV? |
| L2 | Phase 3c Cond A + PV | Phase 3c Cond E (full diversity) + PV | Does full diversity help PV? |
| L3 | Phase 3c Cond B + PV | Phase 3c Cond D (temp diversity) + PV | Text vs temperature diversity |

**Note**: Group L requires running PV on Phase 3c consensus outputs. Defer if PV verification costs are too high for Phase 3c scale.

**Total new comparisons**: 14–17 (Groups I-K definite, Group L conditional)

**Run on**: sapphire

### Task 5: Consolidated bootstrap CIs

**Purpose**: Compute bootstrap CIs for all new configs (384px threshold sweeps, Phase 3c conditions) and merge with existing `all-bootstrap-cis.json`.

**Run on**: sapphire

### Task 6: Summary and observation notes

After all analyses complete:
- Update `docs/notes/reflections/working-notes.md` with new observations
- Document any surprising findings (especially 384px PV results)
- Compare re-run pairwise results to originals — document any changes from bug fixes

---

## Execution order and dependencies

Phase 3c Track 2 is at 98/100 — start with other tasks to give it time to finish.

```text
Task 2a (384px consensus merge)  → START HERE, independent
Task 2b (crop extraction)        → depends on 2a
Task 2c (PV verification)        → depends on 2b, Batch API approved
Task 3 (re-run pairwise)         → independent, run on sapphire in parallel with 2a-2c
Task 2d (PV evaluation)          → depends on 2c
Task 4 (new pairwise)            → depends on 2d (needs 384px PV results)
Task 5 (bootstrap CIs)           → depends on 2d
Task 1 (Phase 3c consensus)      → LAST — wait until 100/100 confirmed
Task 6 (observations)            → depends on all above
```

**Parallelisation**: Tasks 2a and 3 can run concurrently on sapphire. Task 2c (PV verification) runs on this machine via Batch API. Task 1 deferred until Track 2 completes. Everything else is local compute.

---

## Files to modify/create

- Results in `results/phase3c-diversity/track2-text/`
- Results in `results/h11-384-pv-diagnostic/` (17 threshold sweep JSONs)
- `results/pv/pairwise-effects/pairwise-effect-sizes-v2.json`
- New pairwise comparison results in `results/h11-384-pv-diagnostic/pairwise/`
- Updated `results/all-bootstrap-cis.json`
- New observations in `docs/notes/reflections/working-notes.md`

## Verification

1. **Lint**: `ruff check` on any new/modified scripts
2. **Tests**: `pytest tests/ -m tier1`
3. **Code audit**: `/audit` on any new analysis scripts
4. **Cross-check**: Compare re-run pairwise v2 to v1 — document any differences exceeding 0.01 F1
5. **Sanity check**: 384px PV F1 should be in range 0.5–0.85 based on smoke test (raw proposer F1=0.520)
