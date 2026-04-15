# /audit-config — Pre-Launch Experimental Configuration Audit

You are auditing VLM detection experiment configurations before an API run that costs real money. Your job is to catch configuration errors, preregistration violations, and silent parameter mismatches BEFORE they waste budget. The H10/H12 text-only error ($33 wasted, half a day of invalid analysis and troubleshooting) was caused by exactly the kind of mistake this audit is designed to catch.

## Inputs

The user will provide:
- The hypothesis being tested (e.g., "H10", "H12")
- The config files to audit (paths or glob pattern)
- Optionally: the specific parameter being varied

## Audit Steps

### Step 1: Identify the hypothesis and its preregistered requirements

Read the relevant hypothesis section from `docs/methodology/preregistration/osf/preregistration.md`. Extract:
- The research question
- The experimental design (conditions, variables, controls)
- The library construction procedure (Section 8.4.1 if applicable)
- Any specific parameter values mandated by the preregistration

Also check `docs/methodology/preregistration/decisions-log.md` and `docs/methodology/preregistration/protocol-errata.md` for any decisions or errata that modify the original hypothesis specification. Refer to other preregistration documents as necessary to clarify the protocol.

### Step 2: Config pairwise diff

Load all condition configs. For every field, check whether it is IDENTICAL across all conditions or DIFFERS. Report:
- **IDENTICAL fields**: These are the controlled parameters. List them with values.
- **DIFFERING fields**: These are the manipulated variables. There should be exactly ONE semantic difference (the factor being tested). If more than one field differs, flag each as either:
  - EXPECTED (e.g., `version`, `description`, `pool_source` — metadata that should differ)
  - UNEXPECTED — a potential confound that needs justification

### Step 3: Transmission verification

For each config, verify that the manipulated factor will actually reach the API:
- If the factor is `examples` (few-shot library): check that `include_example_images` is `true` (not `false`, not `null`, not absent-defaulting-to-false)
- If the factor is `temperature`: check that no CLI override will shadow the config value
- If the factor is `thinking_level`: same check
- If the factor involves image crops: verify the image files exist at the expected paths under `inputs/examples/`

### Step 4: Preregistration cross-check

Compare the config parameters against the preregistration requirements from Step 1. For each parameter, classify as:
- **MATCHES**: Config value matches preregistration specification
- **DELIBERATE DEVIATION**: Config value differs from preregistration, but this is an intentional, documented change. Check that a corresponding entry exists in `protocol-errata.md`.
- **UNDOCUMENTED DEVIATION**: Config value differs from preregistration with no errata entry. Flag as a blocker — this must be either corrected or recorded in errata before proceeding.

### Step 5: Dry-run validation

Instruct the user to run a `--dry-run` of the detection script with one config and verify:
- Correct number of tiles found in manifest
- Correct number of examples loaded (no "Warning: Reference image not found" messages)
- Tile size matches (no "Tile dimensions do not match" errors)
- The experiment_intent.md preview confirms the hypothesis, factor, and modality

### Step 6: Holdout and evaluation scope

Verify:
- The evaluation manifest is disjoint from any calibration/training tiles
- The evaluation tile count matches expectations
- Ground truth reference file is correct

## Output Format

Present results as a structured audit report:

```
=== PRE-LAUNCH AUDIT: [Hypothesis] ===

PASS / FAIL / DEVIATION for each check:

1. Preregistration requirements extracted: [summary]
2. Config diff: [N fields identical, M fields differ]
   - Controlled: [list]
   - Manipulated: [list — flag if unexpected]
3. Transmission check: [PASS/FAIL per config]
4. Preregistration alignment:
   - Matches: [list]
   - Deliberate deviations: [list with errata refs]
   - Undocumented deviations: [BLOCKER if any]
5. Dry-run: [PASS/FAIL]
6. Evaluation scope: [PASS/FAIL]

OVERALL: READY TO LAUNCH / BLOCKED (reason)
```

## Critical Rules

- A config with `include_example_images: false` that claims to test an image-based factor is ALWAYS a blocker
- Any undocumented deviation from the preregistration is ALWAYS a blocker until recorded in errata
- If more parameters differ between conditions than the target factor + metadata fields, flag as a potential confound
- Check the ACTUAL JSON values, not what the description field claims — descriptions can be stale
- Verify paths resolve by checking the filesystem, not by trusting the config
