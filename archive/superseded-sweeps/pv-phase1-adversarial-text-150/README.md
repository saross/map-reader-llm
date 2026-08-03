# Superseded coarse-grid sweep — PV Phase 1, adversarial-text-150 (N=1, T=0.0)

> **Archived**: 2026-08-03 (E39 repo-side fix). Superseded by a step-0.05 /
> 1000-bootstrap regeneration written to the original path. Retained under the
> project's archive-never-delete policy.

## What these files are

`threshold_sweep.json` and `threshold_sweep.csv` as originally committed for the
Proposer-Verifier (PV) Phase 1 `adversarial-text-150 / text-n1-t0.0-minimal`
arm, in commit `9a1b9e1d5` (2026-03-21, "feat(pv): validate verifier strategy
choice + add phase-gate process").

Their original path was:

```text
results/pv/phase1/adversarial-text-150/text-n1-t0.0-minimal/
```

## Why they were superseded

This arm was swept on a **coarser threshold grid** than every one of its six
sibling arms in `results/pv/phase1/`:

| Setting | This (archived) sweep | All six sibling arms |
|---|---|---|
| `step` | 0.1 | 0.05 |
| `bootstrap_iterations` | 100 | 1000 |
| grid rows | 11 | 21 |
| 0.15 row present | no | yes |
| reported optimum | F1 0.7669 @ threshold 0.20 | mostly @ threshold 0.15 |

Because a 0.1 grid has no 0.15 row, this arm's reported optimum was pinned to
threshold 0.20. `results/pv/phase1/pv-phase1-analysis.md` then published that
0.7669 alongside two fine-grid sibling figures (checklist-text 0.7694,
brief-text 0.7523) as a like-for-like strategy comparison — an
incommensurable-grid defect, not an arithmetic one.

## The wave-4 finding

Triage family `w4-e39-superseded-sweep-instrument` (row `017#52[2]`) in
`reports/verification/c4-triage/mismatch-triage-2026-08-02-wave4.json`
diagnosed this. A blind re-sweep of the archived inputs at the siblings'
settings reproduced the figure published in erratum **E39**
(`docs/methodology/preregistration/protocol-errata.md`, entry dated 2026-03-21)
exactly: **F1 0.7701 at threshold 0.15** (P 0.7759, R 0.7644, n 531).

The disposition is therefore "erratum right, committed artefact and published
table wrong": E39's prose figure of 0.770 for the adversarial strategy was
correct all along; this sweep and the analysis table were the defective
artefacts.

Confirming that the sole difference is grid resolution and nothing else: the
regenerated fine-grid sweep's **threshold-0.20 row reproduces this archived
sweep's optimum exactly** — F1 0.7669, P 0.7771, R 0.7570, n 525.

## Replacement

Regenerated 2026-08-03 on sapphire (zero API calls) with the same generator,
`scripts/evaluate_pv_results.py`, at the sibling arms' settings:

```bash
python scripts/evaluate_pv_results.py sweep \
  --probabilities archive/outputs-experimental-pilot/pv/results/adversarial-text-150/text-n1-t0.0-minimal/probabilities.json \
  --manifest archive/outputs-experimental-pilot/pv/crops-150/text-n1-t0.0-minimal/candidate_manifest.json \
  --output-dir results/pv/phase1/adversarial-text-150/text-n1-t0.0-minimal \
  --step 0.05 --bootstrap 1000 --seed 42
```

Inputs resolved to 882 candidates, 569 reference mounds, and 340 evaluation
tiles at a 20 m matching tolerance — identical to the sibling arms. Note that
the regenerated file's `probabilities_file` and `manifest_file` fields point at
the `archive/outputs-experimental-pilot/pv/...` locations where those inputs now
live, whereas the sibling arms still record the pre-archive `outputs/pv/...`
paths.

### Confidence-interval caveat

The regenerated confidence intervals (CIs) use the **bias-corrected and
accelerated (BCa)** bootstrap. This archived sweep — and all six sibling arms —
use the older **percentile** method. `scripts/lib_advanced_metrics.py` switched
percentile→BCa at commit `2026999ad` (2026-04-30).

**Point estimates reproduce exactly; CIs do not and cannot.** Any future
verification wave comparing a pre-May-2026 sweep's CI against a regenerated one
should read the difference as this method change rather than as a defect.
