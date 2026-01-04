# Phase 0: Script Audit and Readiness Assessment

**Created**: 2025-12-31
**Status**: In Progress

---

## Environment Setup Required

The project venv (`/home/shawn/Code/map-reader-llm/.venv/`) appears incomplete. Before testing scripts:

```bash
cd /home/shawn/Code/map-reader-llm
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Required packages** (from `requirements.txt`):
- google-generativeai
- rasterio
- geopandas
- shapely
- Pillow
- geojson
- tqdm
- python-dotenv
- numpy
- pandas

---

## Hard Example Mining Scripts

### `analyze_fp_crops.py`

**Purpose**: Clusters FP/FN detections across multiple runs, ranks by recurrence, extracts image crops.

**Usage**:
```bash
python scripts/analyze_fp_crops.py \
    --input outputs/results/v4.2_temp_0_7_train/run_01_fn.geojson \
    --output_dir outputs/hard-examples \
    --mode fn \
    --manifest inputs/training_manifest.json
```

**Code Review Findings**:

| Aspect | Status | Notes |
|--------|--------|-------|
| Clustering algorithm | OK | Uses 20m centroid distance (matches F1 threshold) |
| Recurrence ranking | OK | Counts unique runs per cluster |
| Crop extraction | OK | 60px margin around detection |
| Error handling | Partial | Some exception handling, but silent failures |
| Path resolution | Fragile | Hardcoded `inputs/tiles/`, complex fallback logic |
| Manifest usage | Incomplete | Loaded but not actually used (see lines 147-152) |

**Issues to Address**:
1. Line 152: Manifest is loaded but never used for tile lookup
2. Line 154: Hardcoded `inputs/tiles` path should use `config.TILES_DIR`
3. Complex spatial lookup logic (lines 198-222) could be simplified

**Recommended Test**:
```bash
python scripts/analyze_fp_crops.py \
    --input outputs/results/v4.2_temp_0_7_train/run_01_fn.geojson \
    --output_dir outputs/test-hard-examples \
    --mode fn \
    --manifest inputs/training_manifest.json
```

---

### `mine_hard_cases.py`

**Purpose**: Simpler crop extraction - takes FP and FN GeoJSON files directly.

**Usage**:
```bash
python scripts/mine_hard_cases.py \
    outputs/results/v4.2_temp_0_7_train/run_01_fp.geojson \
    outputs/results/v4.2_temp_0_7_train/run_01_fn.geojson \
    outputs/hard-examples \
    outputs/results/v4.2_temp_0_7_train/run_01_bounds.geojson
```

**Code Review Findings**:

| Aspect | Status | Notes |
|--------|--------|-------|
| Crop extraction | OK | Uses rasterio Window for proper georeferenced crops |
| Context size | OK | 512×512 pixels (configurable) |
| Spatial fallback | OK | Uses bounds file for spatial lookup when source_tile missing |
| Config integration | OK | Uses `config.TILES_DIR` properly |
| Output structure | OK | Organises by label (`hard_negative_fp/`, `hard_positive_fn/`) |

**Issues to Address**:
1. No clustering - extracts every FP/FN individually (may produce duplicates)
2. No recurrence ranking - doesn't prioritise frequently-missed examples
3. Silent failures if tile not found

**Comparison**:

| Feature | analyze_fp_crops.py | mine_hard_cases.py |
|---------|---------------------|-------------------|
| Clustering | Yes (20m) | No |
| Recurrence ranking | Yes | No |
| Limit output | Top 10 | All |
| Georeferenced crops | Basic (Pillow) | Proper (rasterio) |
| Path handling | Fragile | Clean |

**Recommendation**: Use `analyze_fp_crops.py` for Phase 1 library construction (need recurrence ranking), but fix the manifest issue and hardcoded paths first.

---

## Statistical Analysis Script

**Status**: Missing

No script exists for:
- Factorial ANOVA
- FDR correction (Benjamini-Hochberg)
- Effect size calculations
- Bootstrap confidence intervals

**Options**:

1. **Jupyter notebook** (recommended for exploratory analysis)
   - Interactive visualisation
   - Easy to iterate on analysis
   - Can be version-controlled

2. **Python script** (for reproducible final analysis)
   - `statsmodels` for ANOVA
   - `scipy.stats` for hypothesis tests
   - `pingouin` for effect sizes

**Suggested structure for `scripts/analyze_factorial.py`**:
```python
# Phase 2 analysis pipeline
# 1. Load all condition results from outputs/phase2-factorial/
# 2. Compute F1 per condition (using lib_advanced_metrics.py)
# 3. Reshape to factorial structure (M × O × H × T)
# 4. Run 4-way ANOVA with interactions
# 5. Apply FDR correction
# 6. Generate summary tables and plots
```

---

## Multi-Provider Support

**Status**: Gemini only - no Claude or OpenAI scripts exist

### Current Implementation Analysis

`4_detect_mounds_batch.py` is tightly coupled to Gemini:

```python
# Gemini-specific imports
import google.generativeai as genai

# Gemini-specific configuration
genai.configure(api_key=GOOGLE_API_KEY)

# Gemini-specific model initialization
model = genai.GenerativeModel(
    model_name=model_name_cfg,
    generation_config=generation_config,
    system_instruction=v3_prompt_text,
    safety_settings=safety_settings
)

# Gemini-specific generation config
generation_config = {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "application/json",
}
```

### What Needs to Change for Multi-Provider

| Component | Gemini | Claude | OpenAI |
|-----------|--------|--------|--------|
| SDK | `google.generativeai` | `anthropic` | `openai` |
| Auth | `GOOGLE_API_KEY` | `ANTHROPIC_API_KEY` | `OPENAI_API_KEY` |
| Model init | `genai.GenerativeModel()` | `anthropic.Anthropic()` | `openai.OpenAI()` |
| Image encoding | PIL Image object | Base64 encoded | Base64 encoded |
| Response format | `response_mime_type: json` | Tool use or text | `response_format: json_object` |
| System prompt | `system_instruction` param | `system` message | `system` message |
| Thinking/reasoning | `thinking_level: high` | `extended_thinking` | `reasoning.effort` |

### Recommended Approach

**Option 1: Separate scripts** (recommended for study timeline)

Create parallel scripts with shared utilities:

```
scripts/
├── 4_detect_mounds_batch.py      # Gemini (existing)
├── 4_detect_mounds_claude.py     # Claude (new)
├── 4_detect_mounds_openai.py     # OpenAI (new)
└── lib_detection.py              # Shared utilities (new)
```

Shared utilities (`lib_detection.py`):
- Tile loading and processing
- Prompt construction from config
- Response parsing (JSON → GeoJSON features)
- Metadata tracking
- Output file management

**Option 2: Provider abstraction** (cleaner, more work)

```python
# lib_providers.py
class VLMProvider(ABC):
    @abstractmethod
    def detect(self, tile_image, few_shot_examples, prompt) -> list[Detection]:
        pass

class GeminiProvider(VLMProvider): ...
class ClaudeProvider(VLMProvider): ...
class OpenAIProvider(VLMProvider): ...
```

### Priority

- **H1-H7, H9**: Gemini only → existing script sufficient
- **H8**: Flash→Pro transfer → existing script sufficient
- **H12**: Cross-model consistency → requires Claude/OpenAI scripts
- **H13**: Cross-model voting → requires Claude/OpenAI scripts

**Recommendation**: Defer Claude/OpenAI scripts until after Phase 2 (Gemini factorial). If H12/H13 are to be run, create scripts during Phase 4-5.

---

## Config Files Needed for Phase 2

**Status**: ✅ Complete (2025-12-31)

All 48 factorial conditions now have valid config files. Verified with:

```bash
python3 scripts/run_study.py studies/phase2-factorial.yaml --list
# Output: Total conditions: 48, Valid configs: 48, Missing configs: 0
```

**Created configs**:
- `detect_image-only_canonical-last-hardneg.json`
- `detect_image-only_random-order-hardneg.json`
- `detect_text-image_canonical-last.json`
- `detect_text-image_canonical-last-hardneg.json`
- `detect_text-image_random-order.json`
- `detect_text-image_random-order-hardneg.json`

---

## Summary Checklist

### Environment
- [x] Rebuild `.venv` with all requirements (2025-12-31)
- [x] Verify geopandas, rasterio installed correctly (2025-12-31)

### Hard Example Mining
- [x] Fix `analyze_fp_crops.py` manifest usage (2025-12-31)
- [x] Replace hardcoded paths with config imports (2025-12-31)
- [x] Test on existing v4.2 results (2025-12-31)
- [x] Document expected output format (crops saved to output_dir as hard_positive/hard_negative_rank_tile.png)

### Statistical Analysis
- [x] Create Jupyter notebook: `notebooks/phase2-factorial-analysis.ipynb` (2025-12-31)
- [x] Include ANOVA, FDR, effect sizes, visualisations (2025-12-31)
    - Four-way factorial ANOVA with Type II sum of squares
    - Benjamini-Hochberg FDR correction at q=0.05
    - Partial eta-squared effect sizes
    - Hypothesis-specific tests (H1, H9)
    - Box plots for main effects, interaction plots

### Multi-Provider
- [ ] Create `scripts/detect_claude.py` — **Deferred to Phase 4-5**
- [ ] Create `scripts/detect_openai.py` — **Deferred to Phase 4-5**
- [ ] Or implement provider abstraction in `lib_detection.py` — **Deferred to Phase 4-5**

**Rationale**: Multi-provider support (H12, H13) is exploratory. Phase 2 focuses on Gemini Flash factorial. Claude/OpenAI scripts will be created during Phase 4-5 if H12/H13 are prioritised after confirmatory hypotheses are tested.

### Config Files
- [x] Create 6 missing config variants (2025-12-31)
- [x] Verify all 48 conditions pass `run_study.py --list` (2025-12-31)

---

*Document version: 1.0*
