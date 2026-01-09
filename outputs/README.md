# Outputs

All generated research outputs reside here. This directory is structured to support the preregistered factorial experiment design.

## Directory Structure

```text
outputs/
├── phase1-library/           # Few-shot library development
│   ├── baseline-runs/        # Initial detection runs
│   └── hard-example-analysis/# Hard positive/negative analysis
├── phase2-factorial/         # Main factorial experiment (60 conditions)
│   ├── raw-responses/        # Per-condition detection outputs
│   │   └── {condition_id}/   # e.g., M1_E1_H5-1_T1
│   └── aggregated/           # Collated results and analyses
├── phase3-followup/          # Confirmatory follow-up experiments
│   ├── h2-twostage/          # Two-stage pipeline evaluation
│   ├── h3-voting/            # Consensus voting evaluation
│   ├── h4-ordering/          # Example ordering evaluation
│   └── h9-diversity/         # Diversity mechanisms (exploratory)
├── phase4-transfer/          # Cross-model transfer
│   └── pro-replication/      # Flash→Pro transfer (H6)
├── phase5-exploratory/       # Exploratory analyses
└── figures/                  # Generated visualisations
```

## Output File Conventions

- `detections-*.geojson` — Raw Vision Language Model (VLM) detection output
- `detections-*.meta.json` — Run metadata (config, tokens, timing, git commit)
- `candidates.geojson` — Proposer stage output (two-stage pipeline)
- `verified.geojson` — Verifier stage output (two-stage pipeline)
- `*-results.csv` — Aggregated metrics for statistical analysis

## Metadata Format

Each `.meta.json` file contains:

- **Run identification**: Unique identifier (UUID), timestamps, git commit
- **Configuration snapshot**: Full config including prompt hash
- **Execution stats**: Items processed, retries, failures
- **Token usage**: Input/output/cached tokens by provider
- **Cost estimate**: Calculated from current pricing

## Notes

- Subdirectories will be created as each phase executes
- Raw responses are preserved for reproducibility
- Aggregated results support the preregistered statistical analyses
