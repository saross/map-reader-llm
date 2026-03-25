# Seed Prompt: Comprehensive Run Configuration Audit

## Purpose

Audit every production run in this project to verify that:

1. **Label ↔ metadata match**: The condition label (directory name, study YAML) matches the configuration recorded in the run's meta.json at execution time
2. **Metadata ↔ submission match**: The meta.json configuration matches what was actually submitted to the API (generation_config in the JSONL request files)
3. **Intent ↔ execution match**: The study YAML's intended parameters (model, temperature, thinking level) were correctly propagated through the config resolution chain to the API call

## Scope

All production runs under:

- `outputs/h11/pv-diag-384/` — H11 384px proposer runs
- `outputs/h11/pv-diag-256/` — H11 256px proposer runs (if present)
- `outputs/h11/consensus-384/` — H11 consensus baseline runs
- `outputs/retest/` — retest runs (all phases)
- `outputs/phase2b/` through `outputs/phase3c/` — earlier phase runs
- `outputs/h11/pv-diag-384/verified/` — all verifier runs

## Data Sources (per run)

For each run, extract and cross-reference these fields from up to four sources:

### Source A: Study YAML (`studies/*.yaml`)

- `conditions[].name` — condition label
- `conditions[].config` — path to prompt config JSON
- `conditions[].temperature` — intended temperature
- `conditions[].thinking_level` — intended thinking level
- `conditions[].model` (if present) — intended model override
- CLI flags used at invocation (if recoverable from logs)

### Source B: Prompt Config JSON (`prompts/configs/*.json`)

- `model` — default model name
- `temperature` — default temperature
- `thinking_level` — default thinking level
- `instruction_file` — system instruction filename

### Source C: Run meta.json (runtime snapshot — **ground truth**)

For proposer runs: `outputs/**/run_*/detections_*.meta.json`
For verifier runs: `outputs/**/verified/*/run.meta.json`

- `configuration.model` — resolved model name
- `configuration.temperature` — resolved temperature
- `configuration.thinking_level` — resolved thinking level
- `configuration.version` — config version identifier
- `configuration.instruction_file` — instruction file used
- `configuration.system_instruction_hash` — SHA256 of instruction text
- `configuration.example_count` — number of examples included

### Source D: Batch JSONL request (`batch_working/*.jsonl`)

First line of the JSONL, extract from `request.generation_config`:

- `temperature` — submitted temperature
- `thinking_config.thinking_level` — submitted thinking level
- `max_output_tokens` — submitted token limit

Note: model name is not in the JSONL (set at batch job level). Cross-reference with meta.json.

## Audit Checks

For each run, perform these checks and flag any discrepancy:

### Check 1: Label vs Metadata

Compare the directory name / condition label against `configuration.model` and `configuration.thinking_level` in meta.json. Flag if:

- Directory says "pro" but model is "gemini-3-flash"
- Directory says "high" but thinking_level is "minimal" or "medium"
- Directory says "minimal" but thinking_level is "high" or "medium"
- Directory implies a specific temperature (e.g., "t07") but recorded temperature differs

### Check 2: Study YAML Intent vs Metadata

Compare the study YAML's intended parameters against meta.json. Flag if:

- YAML specifies `model: gemini-3.1-pro` but meta.json records `gemini-3-flash`
- YAML specifies `temperature: 0.7` but meta.json records a different value
- YAML specifies `thinking_level: high` but meta.json records differently
- YAML condition description mentions "Pro" but model is Flash

### Check 3: Config Default Propagation

Verify whether study YAML overrides were correctly applied over config defaults. Flag if:

- Config JSON has `temperature: 1.0` but study YAML specifies `0.7` and meta.json shows `1.0` (override failed)
- Config JSON has `model: gemini-3-flash` but study intended Pro and meta.json shows Flash (override not applied)
- Config JSON has `thinking_level: minimal` but study intended `high` and meta.json shows `minimal`

### Check 4: Meta.json vs JSONL Submission

Where batch JSONL files are available, verify the generation_config matches meta.json. Flag if:

- JSONL temperature differs from meta.json temperature
- JSONL thinking_level differs from meta.json thinking_level

### Check 5: Cross-Run Consistency

For runs within the same condition (e.g., run_1 through run_30 of flash-high-text-n5), verify all runs used identical configuration. Flag if:

- Model differs between runs in the same condition
- Temperature differs between runs
- Thinking level differs between runs
- System instruction hash differs between runs

### Check 6: Comparison Pair Validity

For any two conditions intended for pairwise comparison, verify only the target parameter differs. Flag confounds where multiple parameters changed simultaneously:

- Model AND thinking level differ (can't attribute effect to either)
- Temperature AND thinking level differ
- Any other multi-parameter variation

## Output Format

Produce a structured report with:

1. **Summary table**: One row per condition, columns for label, intended model/temp/thinking, actual model/temp/thinking, PASS/FAIL per check
2. **Discrepancy list**: Each discrepancy with severity (CRITICAL = wrong model or thinking level, WARNING = minor mismatch, INFO = cosmetic)
3. **Confound matrix**: For each intended comparison pair, list which parameters actually vary
4. **Recommendations**: Specific runs that need re-execution or relabelling

## Known Issues (discovered pre-audit)

These have already been identified and corrected — verify the fixes are complete:

- **E42**: All "Pro" H11 runs used gemini-3-flash (renamed Session 57)
- **T=1.0 temperature bug**: consensus-384 text runs used T=1.0 instead of T=0.7 (discovered Session 56)
- **Gemini 3.1 Pro MINIMAL rejection**: Pro doesn't support MINIMAL thinking; lowest is MEDIUM (E40)
