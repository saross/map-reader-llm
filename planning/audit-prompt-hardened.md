# Hardened Prompt: Comprehensive Run Configuration Audit

<!-- [#13 Task-type declaration] -->
**This is an exhaustive verification audit, not a spot-check or summary.**
The goal is to confirm — or disprove — that every production run's actual
configuration matches both its label and its intended design. You must
examine every run individually. Do not sample, generalise from a subset,
or declare groups of runs consistent without checking each one.

<!-- [#7 Ground truth declaration] -->
**Source of truth hierarchy** (when sources conflict, higher wins):

1. **Batch JSONL request** (`batch_working/*.jsonl` → `request.generation_config`) —
   what the API actually received. Highest authority for temperature and
   thinking level.
2. **Run meta.json** (`detections_*.meta.json` or `verified/*/run.meta.json`) —
   runtime snapshot of resolved configuration. Highest authority for model
   name (not in JSONL). Contains `configuration.model`,
   `configuration.temperature`, `configuration.thinking_level`,
   `configuration.system_instruction_hash`.
3. **Prompt config JSON** (`prompts/configs/*.json`) — static defaults.
   Overridable by study YAML and CLI flags.
4. **Study YAML** (`studies/*.yaml`) — intended design. Expresses what
   SHOULD have happened, not what DID happen.

When any source is missing for a run, flag it as `SOURCE_MISSING` with
the source name, record reduced confidence for that run, and proceed
with available sources. Do not skip the run.

<!-- [#9 Error mode anchoring] -->
**Known error modes — watch specifically for these patterns:**

1. **Config hardcoding defeats override intent.** The prompt config JSON
   hardcodes `"model": "gemini-3-flash"`. If the study YAML or run label
   implies Pro but no `--model` CLI override was passed, the run used
   Flash regardless. This exact error went undetected for 3 weeks across
   all "Pro" H11 runs (E42). Check EVERY run that claims to use Pro.
2. **Temperature override propagation failure.** The config JSON default
   `temperature: 1.0` should be overridden by the study YAML's
   `temperature: 0.7`, but the override depends on `extract_conditions()`
   propagating correctly. This failed silently for 30 consensus-384 text
   runs, which executed at T=1.0 instead of T=0.7. Check EVERY run where
   meta.json temperature ≠ config JSON temperature — is the difference
   an intentional override or a propagation failure?
3. **Thinking level silent downgrade.** Gemini 3.1 Pro rejects MINIMAL
   thinking (lowest supported is MEDIUM). If a run targeted Pro with
   MINIMAL thinking, it may have silently failed or downgraded. Check
   for `partial_failure_N_tiles` in checkpoints or empty results.
4. **Instruction drift between runs.** If runs within the same condition
   were executed across different git commits, the system instruction
   text may have changed. The `system_instruction_hash` in meta.json
   detects this. Check for hash consistency within every condition.

<!-- [#15 Scope fence] -->
## Scope

**IN SCOPE — audit every run under these directories:**

- `outputs/h11/pv-diag-384/` — H11 384px proposer runs (all conditions)
- `outputs/h11/pv-diag-256/` — H11 256px proposer runs (if present)
- `outputs/h11/consensus-384/` — H11 consensus baseline runs
- `outputs/retest/` — retest runs (all phases)
- `outputs/phase2b/` through `outputs/phase3c/` — earlier phase runs
- `outputs/h11/pv-diag-384/verified/` — all verifier runs

**OUT OF SCOPE (do not audit):**

- Pilot/exploratory runs under `outputs/pv/` (Phase 3d pilot data)
- Archived runs under `archive/`
- Analysis results under `results/` (these are derived; audit the inputs)
- The correctness of detection outputs (this audit is configuration only)

## Execution

<!-- [#1 Phase decomposition] -->
<!-- [#2 Claims inventory — enumerate before evaluate] -->

### Phase 1: Inventory (enumerate every run)

Before checking anything, build a complete inventory of every production
run. For each run, extract and record these fields. Do not assess
correctness during this phase.

**For every proposer run** (each `run_N` directory under each condition):

| Field | Source | Path |
|-------|--------|------|
| condition_label | Directory name | Parent directory of run_N |
| run_number | Directory name | `run_N` |
| study_yaml | File system | Matching `studies/*.yaml` by output_dir |
| yaml_model | Study YAML | `conditions[].model` or absent |
| yaml_temperature | Study YAML | `conditions[].temperature` |
| yaml_thinking | Study YAML | `conditions[].thinking_level` |
| config_file | Study YAML | `conditions[].config` path |
| config_model | Config JSON | `model` field |
| config_temperature | Config JSON | `temperature` field |
| config_thinking | Config JSON | `thinking_level` field |
| meta_model | meta.json | `configuration.model` |
| meta_temperature | meta.json | `configuration.temperature` |
| meta_thinking | meta.json | `configuration.thinking_level` |
| meta_instruction_hash | meta.json | `configuration.system_instruction_hash` |
| meta_example_count | meta.json | `configuration.example_count` |
| jsonl_temperature | Batch JSONL | `request.generation_config.temperature` (first line) |
| jsonl_thinking | Batch JSONL | `request.generation_config.thinking_config.thinking_level` (first line) |

**For every verifier run** (each directory under `verified/`):

Same fields but from `run.meta.json` instead of `detections_*.meta.json`.

<!-- [#6 Exhaustive quantifiers] -->
**Exhaustiveness requirement**: Every `run_N` directory that contains a
`detections_*.meta.json` or `run.meta.json` must appear in the inventory.
After building the inventory, report the total count of runs inventoried
per condition and the grand total.

### Phase 2: Check each run (6 checks per run)

For every run in the Phase 1 inventory, apply all 6 checks. Record the
result of each check as PASS, FAIL, or UNVERIFIABLE (with reason).

<!-- [#16 CoT scaffolding for Check 3] -->
**Check 1: Label ↔ Metadata.** Does the directory name match the
meta.json configuration?

- Label says "pro" → meta_model must contain "pro"
- Label says "high" → meta_thinking must be "high"
- Label says "minimal" → meta_thinking must be "minimal"
- Label says "medium" → meta_thinking must be "medium"
- Label contains "t07" or "t0.7" → meta_temperature must be 0.7
- Label contains "t10" or "t1.0" → meta_temperature must be 1.0

**Check 2: Intent ↔ Metadata.** Does the study YAML's intended
configuration match the meta.json?

- yaml_model (if present) must match meta_model
- yaml_temperature must match meta_temperature
- yaml_thinking must match meta_thinking

**Check 3: Config propagation chain.** Trace the resolution:

```text
For each parameter (model, temperature, thinking_level):
  1. What does the config JSON default to?
  2. Does the study YAML override it?
  3. Was a CLI flag used? (check logs if available)
  4. What did meta.json record?
  5. If meta.json ≠ study YAML intent → was the override applied?
     If not → this is a propagation failure (CRITICAL)
```

**Check 4: Metadata ↔ JSONL submission.** Where batch JSONL exists:

- jsonl_temperature must match meta_temperature
- jsonl_thinking (uppercase) must match meta_thinking (case-insensitive)

**Check 5: Cross-run consistency.** Within each condition, all runs must
share identical values for: meta_model, meta_temperature, meta_thinking,
meta_instruction_hash, meta_example_count. Flag ANY run that differs
from the majority within its condition.

<!-- [#3 Bidirectional verification] -->
**Check 6: Comparison pair validity.** For every pair of conditions that
were compared in pairwise statistical tests (check
`results/h11-384-pairwise-n5/*.json` for the list), verify:

- **Forward**: Only the intended target parameter differs between the two
  conditions' actual configurations
- **Reverse**: No unintended parameters also differ (confounds)

List every parameter that actually varies between each comparison pair.
Flag pairs where more than one parameter varies.

### Phase 3: Report

<!-- [#4 Structured output] -->
<!-- [#12 Output exemplar] -->

**Section 1: Run Inventory Summary**

```text
| Condition | Runs | Study YAML | Config JSON | Has meta.json | Has JSONL |
|-----------|------|------------|-------------|---------------|-----------|
| flash-high-text-n5 | 30 | h11-384-flash-high-text-n5.yaml | detect_brief-text.json | 30/30 | 28/30 |
| ... | ... | ... | ... | ... | ... |
| TOTAL | NNN | — | — | NNN/NNN | NNN/NNN |
```

**Section 2: Discrepancy Table**

Every check failure, one row per discrepancy:

```text
| Condition | Run | Check | Severity | Expected | Actual | Detail |
|-----------|-----|-------|----------|----------|--------|--------|
| flash-high-text-n5-b | run_1 | 1: Label↔Meta | CRITICAL | model=pro | model=gemini-3-flash | E42: Pro label, Flash model |
| consensus-384 | run_1 | 3: Propagation | CRITICAL | temp=0.7 | temp=1.0 | Config default T=1.0 not overridden |
```

Severity levels:

- **CRITICAL**: Wrong model or thinking level — invalidates the condition's
  scientific claims
- **HIGH**: Wrong temperature or instruction file — affects results but
  may be recoverable
- **WARNING**: Minor parameter mismatch (e.g., max_output_tokens) —
  unlikely to affect results
- **INFO**: Cosmetic (label convention, missing optional field)

**Section 3: Confound Matrix**

For every comparison pair from pairwise tests:

```text
| Comparison | Intended variable | Also varies | Confounded? |
|------------|------------------|-------------|-------------|
| flash-high-text vs flash-minimal-text | thinking_level | temperature (0.7 vs 1.0) | YES — T=1.0 bug |
```

**Section 4: Cross-Run Consistency Exceptions**

Any condition where runs are not internally consistent:

```text
| Condition | Parameter | Majority value | Outlier runs | Outlier value |
|-----------|-----------|----------------|--------------|---------------|
```

If no exceptions, state: "All conditions internally consistent — no
cross-run anomalies detected."

**Section 5: Recommendations**

For each CRITICAL or HIGH discrepancy:

1. Whether the run data is usable (with corrected label) or must be
   re-executed
2. Whether any published analysis results are affected
3. Specific re-execution commands if needed

<!-- [#10 Negative constraints] -->
## Prohibitions

- **DO NOT** declare a condition "consistent" after checking only run_1.
  Check every run.
- **DO NOT** assume that if runs 1-5 are correct, runs 6-30 are too.
  Configuration can change mid-condition if the study was resumed with
  different parameters.
- **DO NOT** skip verifier runs. The E42 error affected both proposer
  and verifier stages.
- **DO NOT** accept directory names as evidence of configuration. The
  entire point of this audit is that directory names can be wrong.
- **DO NOT** treat the absence of a discrepancy as proof of correctness
  when a source is missing. Flag it as UNVERIFIABLE.
- **DO NOT** group runs under summary verdicts like "all 30 runs passed."
  Report each run's check results individually in the inventory, then
  summarise.

<!-- [#14 Success criteria] -->
## Completion Criteria

This audit is complete when:

- [ ] Every `run_N` directory with a meta.json has been inventoried
- [ ] All 6 checks have been applied to every inventoried run
- [ ] Every check result is recorded as PASS, FAIL, or UNVERIFIABLE
- [ ] The discrepancy table includes every FAIL with severity
- [ ] The confound matrix covers every pairwise comparison
- [ ] The cross-run consistency check covers every condition
- [ ] A completeness count confirms: "Audited N/N runs across M conditions"

<!-- [#5 Completeness check] -->
## Final Completeness Check

After completing all checks, answer these questions:

1. How many total runs were inventoried? Does this match the expected
   count from checkpoint files?
2. How many runs had at least one UNVERIFIABLE check? List them.
3. Were any conditions entirely skipped? If so, why?
4. For Check 5 (cross-run consistency), how many conditions had more
   than 10 runs? Were ALL runs in those conditions checked individually?

<!-- [#11 Uncertainty flagging] -->
## Handling Uncertainty

If a data source is missing, ambiguous, or contradictory:

- **Missing meta.json**: Flag as `SOURCE_MISSING:meta`, mark all metadata
  checks as UNVERIFIABLE for that run
- **Missing JSONL**: Flag as `SOURCE_MISSING:jsonl`, mark Check 4 as
  UNVERIFIABLE, proceed with other checks
- **No matching study YAML**: Flag as `SOURCE_MISSING:yaml`, mark
  Check 2 and Check 3 as UNVERIFIABLE
- **Contradictory sources**: Report both values with the source, apply
  the truth hierarchy (JSONL > meta.json > config > YAML)

## Known Issues (verify fixes are complete)

- **E42**: All "Pro" H11 runs used gemini-3-flash. Directories renamed
  Session 57. Verify no mislabelled remnants exist.
- **T=1.0 temperature bug**: consensus-384 text runs used T=1.0 instead
  of T=0.7 (discovered Session 56). Verify the corrected re-run
  (`flash-minimal-text-n30-t07`) actually uses T=0.7.
- **E40**: Gemini 3.1 Pro rejects MINIMAL thinking. Verify no Pro runs
  attempted MINIMAL and silently failed.
