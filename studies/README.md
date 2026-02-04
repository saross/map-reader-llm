# Studies

YAML configuration files for study execution. Phase 1 uses `scripts/run_phase1.py` (single-condition repeated measures). Phases 2+ use `scripts/run_study.py` (sequential OFAT experiments).

## Completed Studies

| File | Phase | Script | Description |
|------|-------|--------|-------------|
| `phase1-library.yaml` | 1 | `run_phase1.py` | Library construction (5 passes) |

## Phase 2: Sequential Hypothesis Testing

| File | Phase | Hypothesis | Cells | Description |
|------|-------|------------|-------|-------------|
| `phase2a-h1-modality.yaml` | 2a | H1 | 5 | Modality/elaboration level |
| `phase2b-h7-temperature.yaml` | 2b | H7 | 5 | Temperature optimisation |
| `phase2c-h8-library.yaml` | 2c | H8 | 5 | Library composition (7 preregistered, 2 deferred per E11) |
| `phase2d-h5-negtext.yaml` | 2d | H5 | 6 | Negative text treatment (9 cells, 3 reused from 2a) |
| `phase2e-h4-ordering.yaml` | 2e | H4 | 3 | Example ordering (+2 triggered exploratory) |

## Phase 3+: Follow-up Experiments

| File | Phase | Hypothesis | Description |
|------|-------|------------|-------------|
| `phase3a-h3-voting.yaml` | 3a | H3 | Voting extension (N=30) |
| `phase3c-h9-diversity.yaml` | 3c | H9 | Diversity (exploratory) |
| `phase3d-h2-twostage.yaml` | 3d | H2 | Two-stage pipeline (exploratory) |
| `phase4-transfer.yaml` | 4 | H6 | Flash→Pro transfer |

## Usage

```bash
# Dry run (shows conditions without executing)
python scripts/run_study.py studies/phase2a-h1-modality.yaml --dry-run

# Execute study
python scripts/run_study.py studies/phase2a-h1-modality.yaml

# Resume interrupted study
python scripts/run_study.py studies/phase2a-h1-modality.yaml --resume
```

## See Also

- `docs/methodology/preregistration/execution-plan.md` — Detailed phase specifications
- `scripts/run_study.py` — Study runner script
