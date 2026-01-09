# Studies

YAML configuration files for `scripts/run_study.py`, which orchestrates factorial experiments.

## Status

Study definitions will be created when ready to execute the preregistered experiments. They will align with the stranded factorial design in `docs/methodology/preregistration/execution-plan.md`.

## Planned Files

| File | Phase | Description |
|------|-------|-------------|
| `phase2a-strand1.yaml` | 2a | Verbosity × H5 cross (40 cells) |
| `phase2b-h5-confirmatory.yaml` | 2b | Full 3-level H5 at optimal M/E |
| `phase2c-strand2-library.yaml` | 2c | Library size (H8) |
| `phase2d-interaction.yaml` | 2d | M/E × Library interaction (conditional) |
| `phase3a-voting.yaml` | 3a | H3 voting extension (N=30) |
| `phase3b-ordering.yaml` | 3b | H4 ordering effects |
| `phase3c-diversity.yaml` | 3c | H9 diversity (exploratory) |
| `phase3d-twostage.yaml` | 3d | H2 two-stage pipeline |
| `phase4-transfer.yaml` | 4 | H6 Flash→Pro transfer |

## Usage

```bash
# Dry run (shows conditions without executing)
python scripts/run_study.py studies/phase2a-strand1.yaml --dry-run

# Execute study
python scripts/run_study.py studies/phase2a-strand1.yaml

# Resume interrupted study
python scripts/run_study.py studies/phase2a-strand1.yaml --resume
```

## See Also

- `docs/methodology/preregistration/execution-plan.md` — Detailed phase specifications
- `scripts/run_study.py` — Study runner script
- `archive/preregistration/phase2-factorial.yaml` — Superseded draft configuration
