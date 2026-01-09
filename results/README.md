# Results

Statistical analysis outputs and final results from the preregistered VLM burial mound detection study.

## Directory Structure

```text
results/
├── phase1-library/           # Library construction analysis
│   ├── failure-analysis.csv  # FN/FP frequency rankings
│   └── library-selection.md  # Hard example selection rationale
├── phase2-factorial/         # Main factorial analysis
│   ├── strand1-verbosity/    # M/E × H5 ANOVA results
│   ├── strand2-h5-confirm/   # Full H5 3-level analysis
│   ├── strand3-library/      # Library size (H8) analysis
│   ├── strand4-interaction/  # M/E × Library interaction (if triggered)
│   └── optimal-config.json   # Final optimal configuration
├── phase3-followup/          # Follow-up experiment results
│   ├── h2-twostage/          # Two-stage pipeline comparison
│   ├── h3-voting/            # Voting threshold analysis
│   ├── h4-ordering/          # Example ordering effects
│   └── h9-diversity/         # Diversity mechanism analysis
├── phase4-transfer/          # Cross-model transfer results
│   └── h6-flash-pro/         # Flash→Pro OFAT analysis
├── phase5-exploratory/       # Exploratory hypothesis results
│   ├── h10-pool-size/        # Training pool size
│   ├── h14-cross-model/      # Cross-model consistency
│   └── h15-ensemble/         # Cross-model voting
├── figures/                  # Publication-ready figures
│   ├── factorial-heatmaps/   # Condition × metric heatmaps
│   ├── threshold-curves/     # Voting threshold sweeps
│   ├── interaction-plots/    # Factor interaction visualisations
│   └── transfer-plots/       # Cross-model comparison plots
├── tables/                   # Publication-ready tables
│   ├── anova-summaries/      # ANOVA result tables
│   ├── pairwise-comparisons/ # Post-hoc comparison tables
│   └── effect-sizes/         # Cohen's d and confidence intervals
└── final-report/             # Synthesis documents
    ├── analysis-notebook.ipynb  # Reproducible analysis
    ├── results-summary.md       # Plain-language summary
    └── deviations.md            # Preregistration deviations log
```

## File Conventions

### Analysis Outputs

- `*-anova.csv` — ANOVA summary tables (SS, df, F, p, partial η²)
- `*-posthoc.csv` — Post-hoc pairwise comparisons with FDR correction
- `*-effects.csv` — Effect sizes (Cohen's d) with 95% confidence intervals
- `*-summary.md` — Human-readable analysis narrative

### Metrics Files

- `metrics-*.csv` — Aggregated performance metrics per condition
  - Columns: `condition_id`, `mean_f1`, `sd_f1`, `ci_lower`, `ci_upper`, `n_runs`, `n_tiles`
- `voting-*.csv` — Voting analysis at multiple thresholds
  - Columns: `pool_size`, `threshold`, `f1`, `precision`, `recall`

### Figure Formats

- `.png` — Raster figures (300 DPI for publication)
- `.svg` — Vector figures (for editing)
- `.pdf` — Print-ready figures

## Analysis Pipeline

Results are generated from `outputs/` using scripts in `scripts/`:

1. **Aggregation**: `scripts/aggregate_results.py` — Collates raw outputs into metrics CSVs
2. **Statistical tests**: `scripts/run_anova.py` — Executes preregistered ANOVA designs
3. **Visualisation**: `scripts/generate_figures.py` — Creates publication figures
4. **Reporting**: `scripts/compile_report.py` — Generates summary documents

## Preregistration Alignment

Each analysis corresponds to a preregistered hypothesis:

| Hypothesis | Analysis Location | Primary Metric |
|------------|-------------------|----------------|
| H1 (Modality/Elaboration) | `phase2-factorial/strand1-verbosity/` | F1 |
| H2 (Two-stage pipeline) | `phase3-followup/h2-twostage/` | F1 delta |
| H3 (Voting threshold) | `phase3-followup/h3-voting/` | Optimal (N, T) |
| H4 (Example ordering) | `phase3-followup/h4-ordering/` | F1 by ordering |
| H5 (Hard negatives) | `phase2-factorial/strand2-h5-confirm/` | F1 by H5 level |
| H6 (Flash→Pro transfer) | `phase4-transfer/h6-flash-pro/` | Transfer success |
| H7 (Temperature) | `phase2-factorial/strand1-verbosity/` | F1 by temperature |
| H8 (Library size) | `phase2-factorial/strand3-library/` | F1 by library |
| H9 (Diversity) | `phase3-followup/h9-diversity/` | Diversity effect |

## Quality Control

Before finalising results:

- [ ] All statistical tests use preregistered analysis plans
- [ ] Multiple comparisons corrected with Benjamini-Hochberg FDR
- [ ] Effect sizes reported with confidence intervals
- [ ] Deviations from preregistration documented in `final-report/deviations.md`
- [ ] Analysis notebook reproduces all figures and tables

## Notes

- Subdirectories created as each phase completes
- Raw data remains in `outputs/`; this directory contains derived analyses only
- All analyses should be reproducible from the analysis notebook
