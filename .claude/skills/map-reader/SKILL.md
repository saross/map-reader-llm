# map-reader

Guide for running Vision Language Model (VLM) detection experiments on cartographic symbol recognition tasks using scanned topographic maps.

## When to Invoke

Invoke this skill when:

- Running detection experiments with `4_detect_mounds_batch.py`
- Evaluating detection results with `6_accuracy_report.py`
- Analysing multi-pass consensus with `7_analyse_consensus.py`
- Building or updating the few-shot example library
- Executing preregistered hypothesis testing phases

## Purpose

This skill provides operational guidance for VLM-based cartographic symbol detection experiments. It covers the detect-evaluate-analyse pipeline, configuration selection, and study-specific procedures for preregistered research.

The skill is designed for **map-based detection** from scanned topographic maps. Other input types (satellite imagery, LiDAR) would require different workflows.

---

## Core Workflow

The detection pipeline follows five stages:

### 1. Pre-Flight Verification

Before running detection, verify all required inputs are in place.

**Essential checks:**

```bash
# API key configured
echo $GOOGLE_API_KEY | head -c 10  # Should show AIza...

# Training/calibration tiles present
ls inputs/tiles/*/  # Should list map directories

# Ground truth exists
ls inputs/vectors/references/mounds-reference.geojson

# Region bounds exist
ls inputs/vectors/bounds/calibration_bounds.geojson

# Example library images present
ls inputs/examples/neutral-naming/example_*.png

# Selected config exists
ls prompts/configs/<your-config>.json
```

See [references/input-paths.md](references/input-paths.md) for complete path reference.

### 2. Detection

Run the batch detection script with your chosen configuration.

**Basic usage:**

```bash
python scripts/4_detect_mounds_batch.py \
    --config prompts/configs/<config>.json \
    --manifest inputs/tiles/<manifest>.json \
    --output-dir outputs/<experiment-name>/pass_01
```

**Key parameters:**

- `--config` — Prompt configuration (model, examples, system instruction)
- `--manifest` — Tile manifest specifying which tiles to process
- `--output-dir` — Where to write detection results
- `--workers` — Parallel API calls (default: 1, increase with caution)
- `--dry-run` — Validate config without API calls

**Outputs per tile:**

- `{tile_name}.geojson` — Detection results with coordinates and confidence
- `{tile_name}.meta.json` — API metadata (tokens, timing, model version)

See [references/workflow-overview.md](references/workflow-overview.md) for detailed parameters.

### 3. Evaluation

Compare detections against ground truth using the accuracy report.

```bash
python scripts/6_accuracy_report.py \
    --pred outputs/<experiment>/merged_detections.geojson \
    --bounds inputs/vectors/bounds/<bounds>.geojson \
    --template inputs/vectors/references/mounds-reference.geojson
```

**Metrics generated:**

- **Symbol-level**: Precision, Recall, F1 (with 95% CI via bootstrap)
- **Tile-level**: MCC, Sensitivity, Specificity
- Confusion matrix (TP, FP, FN, TN counts)

### 4. Analysis

For multi-pass experiments, analyse consensus across runs.

```bash
python scripts/7_analyse_consensus.py \
    --input-dir outputs/<experiment>/ \
    --output outputs/<experiment>/consensus_analysis.json \
    --passes 5
```

**Consensus analysis provides:**

- Vote counts per detection across passes
- Stability metrics (detections appearing in N/K passes)
- Identification of systematic FNs and FPs

For two-stage (proposer-verifier) workflows:

```bash
python scripts/8_analyse_proposer_consensus.py \
    --proposer-dir outputs/<experiment>/proposer/ \
    --verifier-dir outputs/<experiment>/verifier/ \
    --output outputs/<experiment>/two_stage_analysis.json
```

### 5. Iteration

Use analysis results to refine the example library or adjust configurations.

**Hard example extraction:**

```bash
# Extract hard positives (frequently missed mounds)
python scripts/mine_hard_cases.py \
    --input outputs/<experiment>/fn_analysis.geojson \
    --output-dir inputs/examples/hard-positives/ \
    --mode fn --limit 4

# Extract hard negatives (frequent false alarms)
python scripts/mine_hard_cases.py \
    --input outputs/<experiment>/fp_analysis.geojson \
    --output-dir inputs/examples/hard-negatives/ \
    --mode fp --limit 4
```

After extracting hard examples, update the relevant configs and symlinks in `inputs/examples/neutral-naming/`.

---

## Quick Reference

### Config Selection

| Purpose | Config | Notes |
|---------|--------|-------|
| Phase 1 baseline | `library_pure-positive-canon.json` | Canon+ and null only |
| H1 (image-only baseline) | `detect_image-only.json` | No text labels |
| H5 text levels | `detect_verbose-text-image_*.json` | Minimal/Terse/Verbose |
| H8 library scale | `library_scale-*.json` | Scale-4/8/16/32 |
| H2 two-stage | `propose_*.json` + `verify_*.json` | Proposer then verifier |

See [references/config-guide.md](references/config-guide.md) for complete config documentation.

### Key Paths

| Resource | Path |
|----------|------|
| Calibration manifest | `inputs/tiles/calibration_manifest.json` |
| Holdout manifest | `inputs/tiles/holdout_manifest.json` |
| Ground truth | `inputs/vectors/references/mounds-reference.geojson` |
| Calibration bounds | `inputs/vectors/bounds/calibration_bounds.geojson` |
| Example images | `inputs/examples/neutral-naming/example_*.png` |
| Configs | `prompts/configs/*.json` |
| System instructions | `prompts/system-instructions/*.md` |

See [references/input-paths.md](references/input-paths.md) for full path reference.

---

## Reference Files

Detailed procedures are documented in reference files:

- **[workflow-overview.md](references/workflow-overview.md)** — Generic detect-evaluate-analyse pipeline documentation
- **[preregistration-phases.md](references/preregistration-phases.md)** — Phase 1-4 execution procedures for the preregistered study
- **[config-guide.md](references/config-guide.md)** — Configuration selection and parameter documentation
- **[input-paths.md](references/input-paths.md)** — Complete path reference for all inputs
- **[troubleshooting.md](references/troubleshooting.md)** — Common issues and solutions

---

## Study-Specific Notes

This skill supports the preregistered VLM burial mound detection study. When executing preregistered phases:

- Use hypothesis references (H1, H2, ... H15) consistently
- Use phase references (Phase 1, Phase 2a, Phase 2b, etc.)
- Document all deviations in `docs/methodology/preregistration/decisions-log.md`
- Maintain the audit trail by not deleting completed checklist items

See [references/preregistration-phases.md](references/preregistration-phases.md) for phase-specific procedures.
