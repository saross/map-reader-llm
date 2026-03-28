# Plan: Pairwise Permutation Test Orchestration + FDR Correction

## Context

All API experiments are complete. The paper needs statistical evidence for
its claims: that pipeline architecture (consensus, PV) matters more than
prompt engineering (temperature, thinking level), that text outperforms
image, and which top conditions are statistically distinguishable. We have
a mature permutation test script (`pairwise_permutation_test.py`) and a
complete 32-comparison YAML config, but no orchestration to run them as
a batch with FDR correction.

### Analytical goals driving the comparisons

| Goal | What it shows | Covered by |
|------|--------------|------------|
| (a) Architecture progression | N=1 → consensus → PV each improves F1 | Groups 1, 7 + new N=1-vs-consensus |
| (b) Prompt engineering limited | Temperature, thinking level changes ≈ ns | Groups 3, 4 |
| (c) Architecture > prompt eng | Effect sizes in Groups 1,7 >> Groups 3,4 | Summary table |
| (d) Text vs image | Text consistently outperforms | Group 2 |
| (e) Leaderboard tiers | Which top-25 are distinguishable | Group 6 expanded |

---

## Script 1: `scripts/run_pairwise_tests.py`

### Purpose

YAML-driven orchestrator that reads comparison definitions, builds
detection GeoDataFrames, runs permutation tests, and saves results.

### CLI interface

```text
python scripts/run_pairwise_tests.py \
    --config configs/pairwise-comparisons.yaml \
    --buffer-metres 30 \
    --output-dir results/pairwise/30m \
    [--filter-group 6]           # optional: run only one group
    [--n-permutations 10000]     # default: 10000
    [--seed 42]                  # default: 42
    [--quiet]                    # suppress per-tile output in JSONs
```

### Architecture

```
main()
  ├── load ground truth + bounds ONCE
  ├── load_comparisons_yaml(config_path)
  │     └── parse + validate + resolve paths
  ├── for each comparison:
  │     ├── load_condition_gdf(spec, cache) ← dispatches by type
  │     │     ├── type=pv → load_pv_detections(probs, manifest, threshold)
  │     │     ├── type=consensus → load_consensus_detections(study_dir, config, bounds)
  │     │     └── type=geojson → load_geojson_detections(path)
  │     ├── run_permutation_test(gdf_a, gdf_b, ref, bounds, buffer)
  │     └── write per-comparison JSON
  ├── write run_manifest.json (all comparisons, metadata)
  └── print console summary table
```

### Key design decisions

1. **Import, don't subprocess.** Import `run_permutation_test`,
   `load_pv_detections`, `load_consensus_detections`,
   `load_geojson_detections` directly from `pairwise_permutation_test.py`.
   Avoids reloading ground truth 32× and enables GDF caching.

2. **GeoDataFrame cache.** Many comparisons share conditions (e.g.,
   "Flash HIGH text 5-of-5" appears in Groups 2, 3, 7). Cache by
   `(type, source_key)` tuple. Consensus source_key = `(study_dir, config)`;
   PV source_key = `(probs_path, manifest_path, threshold)`.

3. **Per-comparison JSON output** in `output_dir/{group_N}/{slug}.json`,
   matching existing `pairwise_permutation_result.json` schema. Plus a
   `run_manifest.json` at the root with all results for FDR input.

4. **Path validation upfront.** Before running any tests, validate all
   paths in the YAML exist. Fail fast with a clear error listing all
   missing paths, rather than failing on comparison #27.

### Functions to IMPORT from existing code

| Function | Source file | Used for |
|----------|-----------|----------|
| `run_permutation_test()` | `pairwise_permutation_test.py:275` | Core test logic |
| `load_pv_detections()` | `pairwise_permutation_test.py:101` | PV GDF loading |
| `load_consensus_detections()` | `pairwise_permutation_test.py:130` | Consensus GDF loading |
| `load_geojson_detections()` | `pairwise_permutation_test.py:188` | GeoJSON GDF loading |
| `assign_source_tiles()` | `pairwise_permutation_test.py:221` | Tile assignment fallback |
| `_compute_f1()` | `pairwise_permutation_test.py:264` | F1 calculation |

### Functions to WRITE NEW

| Function | Purpose |
|----------|---------|
| `load_comparisons_yaml(path)` | Parse YAML, validate schema, resolve relative paths |
| `validate_paths(comparisons, defaults)` | Pre-flight check all referenced files exist |
| `build_cache_key(condition_spec)` | Generate hashable key for GDF caching |
| `load_condition_gdf(spec, bounds, cache)` | Dispatch to correct loader with caching |
| `sanitise_slug(label)` | Convert label to filesystem-safe dirname |
| `write_comparison_result(result, metadata, output_path)` | Write per-comparison JSON |
| `write_run_manifest(all_results, output_dir)` | Write consolidated manifest |
| `print_summary_table(all_results)` | Console summary with significance markers |

### Output structure

```
results/pairwise/30m/
├── run_manifest.json          # all results + metadata for FDR
├── group_1_architecture/
│   ├── pv-vs-consensus-flash-high-text-16of30.json
│   ├── pv-vs-consensus-flash-high-text-9of10.json
│   └── ...
├── group_2_modality/
│   └── ...
├── ...
└── group_7_pool_size/
    └── ...
```

---

## Script 2: `scripts/apply_fdr_correction.py`

### Purpose

Read permutation test results, apply Benjamini-Hochberg FDR correction
by family, output consolidated paper tables.

### CLI interface

```text
python scripts/apply_fdr_correction.py \
    --results-dir results/pairwise/30m \
    --output-dir results/paper-tables/pairwise \
    [--q 0.05]                   # FDR threshold, default 0.05
```

### Logic

1. Read `run_manifest.json` from results directory
2. Separate into FDR families:
   - Confirmatory (Groups 1-5, 7): 26 comparisons
   - Exploratory (Group 6): 6 comparisons
   - Leaderboard (if present): separate family
3. For each family: `scipy.stats.false_discovery_control(p_values, method='bh')`
4. Output:
   - `pairwise_results_fdr.json` — full results with adjusted p-values
   - `pairwise_results_fdr.csv` — paper table format
   - `pairwise_results_fdr.md` — Markdown summary

### Table columns

```
group | question | label_a | label_b | f1_a | f1_b | delta_f1 |
raw_p | adj_p | sig | family
```

Significance markers: `***` (p<0.001), `**` (p<0.01), `*` (p<0.05), `ns`

---

## Expanding to top-25 leaderboard (goal e)

The existing 6 Group-6 comparisons only compare the #1 PV condition against
runners-up. For the paper, we want to characterise **tiers of
indistinguishable performance** across the full leaderboard.

### Approach: top-25 round-robin

Generate all C(25,2) = 300 pairwise comparisons among the top 25
conditions at 30m. This is computationally trivial (~25 min on sapphire)
and the FDR correction handles the multiple comparisons burden.

### Implementation

Add a `--leaderboard` flag to `run_pairwise_tests.py`:

```text
python scripts/run_pairwise_tests.py \
    --leaderboard results/paper-tables/metrics_master.csv \
    --top-n 25 \
    --buffer-metres 30 \
    --output-dir results/pairwise/leaderboard-30m
```

This mode:
1. Reads metrics_master.csv, filters to 30m buffer, sorts by F1
2. Takes top-N unique conditions
3. Generates all-pairs comparisons programmatically
4. Needs a mapping from condition labels → detection sources (study dirs,
   PV files). This mapping can be embedded in the leaderboard YAML or
   derived from the existing condition configs.

**Complication:** metrics_master.csv doesn't store detection source paths.
Options:
- (A) Generate a `configs/pairwise-leaderboard.yaml` manually or with a
  helper script that maps labels → sources
- (B) Add a `conditions_registry.yaml` that maps every condition label to
  its detection source, then the leaderboard mode looks up conditions there

I recommend **(A)** — a small helper function that generates the YAML from
existing configs. The mapping is straightforward since all conditions
appear in the paper-eval configs which contain the source paths.

**Decision: top-25 round-robin confirmed.** Generate all C(25,2) = 300
comparisons. FDR-correct as a separate exploratory family. Output a
tier-clustering summary showing which conditions are statistically
indistinguishable.

---

## Additional comparisons for goal (a): architecture progression

The current YAML lacks explicit **N=1 vs consensus** comparisons (Group 1
compares PV vs consensus, not N=1 vs consensus). For the architecture
progression story (N=1 → consensus → PV), we need ~3 additional
comparisons:

| Comparison | Purpose |
|-----------|---------|
| Best N=1 Flash text vs best consensus Flash text | Consensus benefit |
| Best N=1 Flash image vs best consensus Flash image | Consensus benefit (image) |
| Best N=1 Pro text vs best consensus Pro text | Consensus benefit (Pro) |

These would be GeoJSON-mode comparisons (N=1 detections are plain
GeoJSON files). Add to Group 1 as confirmatory comparisons.

**Decision: add these.** Implement as consensus-mode comparisons using
N=1 pool size (i.e., `config: "text-t0.7,1,1"` which selects individual
runs). If the consensus loader can't handle N=1, fall back to GeoJSON
mode loading averaged N=1 GeoJSON from the evaluation outputs.
Add to Group 1 as confirmatory comparisons (3 additional).

---

## Execution plan

### Phase 1: Write `run_pairwise_tests.py` (~200 lines)

1. Skeleton: imports, constants, CLI argument parser
2. `load_comparisons_yaml()` with validation
3. `validate_paths()` for fail-fast checking
4. `load_condition_gdf()` with cache dispatch
5. Main orchestration loop
6. `write_run_manifest()` and `print_summary_table()`

### Phase 2: Write `apply_fdr_correction.py` (~120 lines)

1. Load `run_manifest.json`
2. BH correction per family via scipy
3. Output writers (JSON, CSV, Markdown)

### Phase 3: Run on sapphire

1. Copy scripts to sapphire (or git push + pull)
2. `run_pairwise_tests.py --buffer-metres 30` → ~3 min
3. `apply_fdr_correction.py` on 30m results
4. `run_pairwise_tests.py --buffer-metres 20` → ~3 min (sensitivity)
5. Verify: Group 4 (temperature) should be significant; Group 6 (top-N)
   should mostly be non-significant after FDR

### Phase 4: Leaderboard round-robin

1. Create `configs/condition-registry.yaml` — maps each of the 25
   leaderboard condition labels to detection source parameters (type,
   study_dir/config or probabilities/manifest/threshold). Built once
   from existing configs.
2. Add `--leaderboard` mode to `run_pairwise_tests.py` that:
   - Reads metrics_master.csv → top-N at specified buffer
   - Looks up each condition in the registry
   - Generates all C(N,2) pairwise comparisons
   - Runs them with `family: leaderboard` tag
3. Run at 30m on sapphire (~25 min for 300 comparisons)
4. FDR correct as separate leaderboard family
5. Cluster into tiers: conditions where all pairwise adj_p ≥ 0.05
   belong to the same tier

### Phase 5: N=1 vs consensus comparisons

1. Add 3 comparisons to `pairwise-comparisons.yaml` (Group 1 extended):
   - Best N=1 Flash text vs best consensus Flash text
   - Best N=1 Flash image vs best consensus Flash image
   - Best N=1 Pro text vs best consensus Pro text
2. These use GeoJSON mode (N=1 detections are plain GeoJSON files
   from `results/paper-eval/n1/` evaluation outputs)
3. Run with the main 32+3 = 35 comparison batch

---

## Comparison totals

| Family | Source | N comparisons |
|--------|--------|---------------|
| Confirmatory | Groups 1-5, 7 + 3 new N=1-vs-consensus | 29 |
| Exploratory (Group 6) | Top-N from YAML | 6 |
| Leaderboard | Top-25 round-robin | 300 |
| **Total** | | **335** |

All 335 run at 30m primary. The 35 hypothesis-driven also run at 20m
for sensitivity. Leaderboard at 20m is optional (same compute, separate
family).

## Verification

- [ ] Groups 3, 4 comparisons show small |ΔF1| — supports goal (b)
- [ ] Groups 1, 7 show larger |ΔF1| — supports goal (c)
- [ ] Group 2 shows text > image consistently — supports goal (d)
- [ ] Leaderboard produces clear tier clustering at top
- [ ] N=1 vs consensus comparisons are highly significant (large ΔF1)
- [ ] FDR-adjusted p-values are ≥ raw p-values
- [ ] Three FDR families corrected separately (confirmatory, exploratory, leaderboard)
- [ ] Results at 20m and 30m are directionally consistent
- [ ] All JSON outputs match the existing `pairwise_permutation_result.json` schema

## Critical files

- `scripts/pairwise_permutation_test.py` — import core functions
- `configs/pairwise-comparisons.yaml` — 32 comparison definitions
- `planning/pairwise-comparison-proposal.md` — authoritative spec
- `scripts/lib_advanced_metrics.py` — `compute_per_tile_tp_fp_fn()`
- `results/paper-tables/metrics_master.csv` — leaderboard source
