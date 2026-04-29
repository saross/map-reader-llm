# Daylight follow-up sweep — 165-cell N=10K standardisation plan

**Created**: 2026-04-29
**Author**: Claude Code (Opus 4.7, 1M context) — Plan agent
**Status**: DRAFT — awaits user review and explicit approval before any execution
**Related spec**: `planning/paper-writeup-continuity.md` lines 1372–1428
**Anchor observation**: Obs 303 (`docs/notes/reflections/working-notes.md` line ~15019)

---

## 1. Executive summary

**Verdict**: READY TO PLAN. All 165 deferred cells are recoverable. The cleanest implementation
is a one-shot **queue-CSV builder** (`scripts/build_bootstrap_10k_queue_followup.py`, new) that
parses the four heterogeneous metadata sources, emits a 165-row CSV in the same schema the
existing `scripts/run_bootstrap_10k.py` already consumes, and lets the existing runner do the
re-evaluation unchanged. No edits to `run_bootstrap_10k.py` or `evaluate_detections.py` are
required. The dry-run protocol is one cell per group (4 cells), validated by checking that
`evaluation.json._metadata.cli_args.bootstrap == 10000`.

**Approach in 200 words**: build a per-cell CSV queue offline; each row carries the absolute
detection paths (or detections-dir + glob), bounds path, ground-truth path, buffer list, label,
and MCC flag. The queue is built by four mechanisms — one per group — that each parse a
known-shape source: (a) the existing batch YAMLs `configs/n1-eval-{384px,384px-all-buffers,
512px-phase2}.yaml` and `configs/mcc-eval-384px.yaml` for paper-eval (143 of the 156 cells); (b)
`configs/tile-size-comparison.yaml` for pairwise tile-size-30m (5 cells); (c) the per-cell
`evaluation.metadata.json` sidecars for 55maps-cleaned-gt (3 cells); (d) the
`extended-buffer-report.md` §10 reproducibility command for gold-standard-extended-buffer-sweep
(1 cell). The remaining 13 paper-eval cells (`mcc/512px`, the three `single-pass-n1*/`, and
`pro-n10/`-adjacent) need bespoke rows but follow the same mappings.

**Compute estimate**: ~30–60 min wall on sapphire at `xargs -P 16`, dominated by the three
55maps-cleaned-gt cells against the 8,541-tile bounds.

**Commit strategy**: 4 commits, one per group, for diff legibility and rollback granularity.

---

## 2. Cell inventory (165 cells)

| Group | Subtree | Cells | Recovery source |
|---|---|---:|---|
| **paper-eval** | `results/paper-eval/n1/384px/` | 11 | `configs/n1-eval-384px.yaml` (9 conditions) + 2 cells (`pro-image-medium-t-0-0`, `pro-text-medium-t-0-0`) from `configs/n1-eval-384px-all-buffers.yaml` Pro-MEDIUM rows; **buffer set drawn from existing `evaluation.json.summary.buffers` (30m-only), not from the all-buffers YAML's `[20,30,40,50]`** |
| paper-eval | `results/paper-eval/n1/384px-all-buffers/` | 18 | `configs/n1-eval-384px-all-buffers.yaml` (18 conditions, exact match) |
| paper-eval | `results/paper-eval/n1/384px-outstanding/` | 7 | `configs/n1-eval-384px-all-buffers.yaml` (the 7 "outstanding" condition slugs: `flash-image-minimal-t-0-0-487-tiles`, `flash-image-minimal-t-0-3`, `flash-text-minimal-t-0-3`, `pro-image-high-t-0-0`, `pro-image-medium-t-0-7`, `pro-text-high-t-0-0`, `pro-text-medium-t-0-7`); same YAML row as the all-buffers cell, different `--output-dir` |
| paper-eval | `results/paper-eval/n1/512px/` | 33 | `configs/n1-eval-512px-phase2.yaml` (single buffer = 30 m subset) |
| paper-eval | `results/paper-eval/n1/512px-all-buffers/` | 33 | `configs/n1-eval-512px-phase2.yaml` (full buffers 20/30/40/50) |
| paper-eval | `results/paper-eval/mcc/384px/` | 18 | `configs/mcc-eval-384px.yaml` (`--mcc` flag) |
| paper-eval | `results/paper-eval/mcc/512px/` | 33 | `configs/n1-eval-512px-phase2.yaml` (`--mcc` flag) — same conditions, different output dir |
| paper-eval | `results/paper-eval/single-pass-n1/` | 1 | parent `.metadata.json` + condition catalogue (single condition: `outputs/retest/h11-single-pass-384-t0/brief-text-t0`) |
| paper-eval | `results/paper-eval/single-pass-n1-high/` | 1 | bespoke (HIGH thinking variant) |
| paper-eval | `results/paper-eval/single-pass-n1-t07/` | 1 | bespoke (T=0.7 variant) |
| paper-eval (subtotal) | | **156** | |
| **pairwise tile-size-30m** | `results/pairwise/tile-size-30m/512px-{image,text}-{t0,t07}/` | 4 | `configs/tile-size-comparison.yaml` `detections_512` per row |
| pairwise tile-size-30m | `results/pairwise/tile-size-30m/eval-512-on-384-image-t0/` | 1 | bespoke (re-eval of phase2b/track1-image/T0.0 against 384 bounds) |
| pairwise (subtotal) | | **5** | |
| **55maps-cleaned-gt** | `results/55maps-cleaned-gt-evaluation/{image,text-high,text-min}/` | 3 | per-cell `evaluation.metadata.json` `command_shape` + verified-detections paths under `outputs/55maps-{image,text-high,text-min}-generalisation/verified/` |
| 55maps (subtotal) | | **3** | |
| **gold-standard-extended-buffer-sweep** | `results/gold-standard-extended-buffer-sweep/evaluation.json` | 1 | `extended-buffer-report.md` §10 reproducibility step 2 (verbatim CLI) |
| gold-standard (subtotal) | | **1** | |
| **TOTAL** | | **165** | |

**Note on `with-mcc/` cell** at `results/gold-standard-extended-buffer-sweep/with-mcc/evaluation.json`
— already upgraded to N=10K by the overnight sweep (commit `76b6592f`), confirmed by
`_metadata.cli_args.bootstrap == 10000`. NOT in this plan's scope.

**Verification of cell counts**: re-counted by `find <dir> -name evaluation.json | wc -l`:
156 + 5 + 3 + 1 = 165, matching `planning/paper-writeup-continuity.md` line 1379–1384.

---

## 3. Metadata recovery design (per-pattern)

Four distinct metadata patterns; each gets its own helper function inside the new builder
script.

### 3.1 Pattern A — Parent batch-YAML lookup (143 cells)

**Source**: `configs/{n1-eval-384px,n1-eval-384px-all-buffers,n1-eval-512px-phase2,mcc-eval-384px}.yaml`.

**Schema sketch** (relevant fields):

```yaml
defaults:
  bounds: <path to bounds geojson>
  ground_truth: <path to GT geojson>
  buffers: [20, 30, 40, 50]    # or [30] only for single-buffer batches
  bootstrap: 1000               # → override to 10000 at runtime
  seed: 42
  glob: "*/detections_*.geojson"

conditions:
  - label: "<human-readable label>"
    detections_dir: <path to detection run directory>
    glob: <override glob if non-default>
```

**Recovery procedure**:

1. Load YAML; for each condition, merge `defaults` + condition overrides.
2. Compute the output cell directory by `slugify(label)` (the same slugifier
   `evaluate_detections.py` uses; mirrors `import slugify` from that module).
3. Pair each YAML config to its target output subtree:
   - `n1-eval-384px.yaml` → `results/paper-eval/n1/384px/`
   - `n1-eval-384px-all-buffers.yaml` → `results/paper-eval/n1/384px-all-buffers/`
   - `n1-eval-512px-phase2.yaml` → `results/paper-eval/n1/512px-all-buffers/` (full buffers)
     **and** `results/paper-eval/n1/512px/` (30-m-only subset)
   - `mcc-eval-384px.yaml` → `results/paper-eval/mcc/384px/` (`--mcc`)
   - `n1-eval-512px-phase2.yaml` → `results/paper-eval/mcc/512px/` (`--mcc`, 30-m-only buffers)
4. For 384px-outstanding (7 cells), the cells appear to be the subset of
   `n1-eval-384px-all-buffers.yaml` conditions with explicit non-default `glob` patterns; verify
   by name-matching during dry-run; fall back to bespoke rows if the slugified labels don't
   appear in the all-buffers config.

**Sample CSV row (paper-eval n1/384px Flash Text MINIMAL T=0.0)**:

```text
status,eval_path,output_dir,detections,detections_dir,glob,bounds,ground_truth,buffers,bootstrap,seed,label,mcc
queued,results/paper-eval/n1/384px/flash-text-minimal-t-0-0/evaluation.json,\
results/paper-eval/n1/384px/flash-text-minimal-t-0-0,,\
outputs/retest/h11-single-pass-384-t0/brief-text-t0,*/detections_*.geojson,\
inputs/vectors/bounds/384/full_evaluation_bounds.geojson,\
inputs/vectors/references/mounds-reference.geojson,20 30 40 50,1000,42,Flash Text MINIMAL T=0.0,0
```

(Note: the queue-CSV records `bootstrap: 1000` for traceability; the runner forces
`--bootstrap 10000` at the CLI per its existing line 80 hard-coding. This is the
overnight-runner contract; do not change it.)

### 3.2 Pattern B — Pairwise-YAML lookup (5 cells)

**Source**: `configs/tile-size-comparison.yaml` lines 22–36 + bespoke 5th-cell rule.

**Schema sketch**:

```yaml
defaults:
  ground_truth: inputs/vectors/references/mounds-reference.geojson
  common_bounds: inputs/vectors/bounds/384/full_evaluation_bounds.geojson
  buffer_metres: 20

comparisons:
  - label: "<modality T-value label>"
    detections_512: <single-file path to 512px detection geojson>
    detections_384: <single-file path to 384px detection geojson>
```

**Recovery procedure**: only the `detections_512` path is in scope (the 4 cells named
`512px-image-t0`, `512px-image-t07`, `512px-text-t0`, `512px-text-t07`). Use the 340-tile
bounds (`inputs/vectors/bounds/full_evaluation_bounds.geojson`) — NOT the YAML's
`common_bounds` (which is 384/487-tile and used for the matched-pair comparison, not the per-
condition cell). Confirm this by re-reading
`results/pairwise/tile-size-30m/.metadata.json` line 25 (`command_shape`: `--bounds <buffer-30m
bounds>`) and the actual N rows in the per-cell CSV.

**Buffer set**: actual data shows `[20, 30]` for all 5 cells (verified in §4 reading); use
`--buffers 20 30`, NOT the YAML's `buffer_metres: 20`. Schema-drift caveat: the parent sidecar
text (`--buffers 30`) is approximate.

**Sample CSV row (pairwise 512px-image-t0)**:

```text
status,eval_path,output_dir,detections,detections_dir,glob,bounds,ground_truth,buffers,bootstrap,seed,label,mcc
queued,results/pairwise/tile-size-30m/512px-image-t0/evaluation.json,\
results/pairwise/tile-size-30m/512px-image-t0,\
outputs/retest/phase2b/track1-image/T0.0/run_1/detections_T0.0_run01.geojson,,,\
inputs/vectors/bounds/full_evaluation_bounds.geojson,\
inputs/vectors/references/mounds-reference.geojson,20 30,1000,42,512px-image-t0,0
```

**Fifth cell** (`eval-512-on-384-image-t0`, n_runs=3): use `--detections-dir
outputs/retest/phase2b/track1-image/T0.0/` with the default glob, against the 384/487-tile
bounds (label: `"512px Image T=0.0 (on 384px grid)"`).

### 3.3 Pattern C — Per-cell sidecar (3 cells)

**Source**: `results/55maps-cleaned-gt-evaluation/{image,text-high,text-min}/evaluation.metadata.json`.

**Schema sketch** (one of three):

```json
{
  "bootstrap": {"n_iterations": 1000, "seed": 42, ...},
  "invocation": {
    "command_shape": "python scripts/evaluate_detections.py --detections \
        <55maps-image detections> --buffers 20 30 40 50 --bootstrap 1000 --seed 42 \
        --ground-truth <cleaned-gt geojson> --bounds <55maps bounds>",
    ...
  },
  ...
}
```

**Recovery procedure**: parse the JSON; the `command_shape` is a template with three
placeholders that must be resolved:

- `<55maps-{image,text-high,text-min} detections>` →
  `outputs/55maps-{image,text-high,text-min}-generalisation/verified/verified_detections.geojson`
- `<cleaned-gt geojson>` → `inputs/vectors/references/student-mounds-55maps-reviewed.geojson`
  (per `dea1155f` commit which introduced this cleaned GT)
- `<55maps bounds>` → `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` (8,541 tiles)
- Label: `image-vs-cleaned-gt`, `text-high-vs-cleaned-gt`, `text-min-vs-cleaned-gt` (verbatim
  from existing evaluation.json `summary.label`)

**Sample CSV row (55maps image-vs-cleaned-gt)**:

```text
status,eval_path,output_dir,detections,detections_dir,glob,bounds,ground_truth,buffers,bootstrap,seed,label,mcc
queued,results/55maps-cleaned-gt-evaluation/image/evaluation.json,\
results/55maps-cleaned-gt-evaluation/image,\
outputs/55maps-image-generalisation/verified/verified_detections.geojson,,,\
inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson,\
inputs/vectors/references/student-mounds-55maps-reviewed.geojson,20 30 40 50,1000,42,image-vs-cleaned-gt,0
```

### 3.4 Pattern D — Report-MD inference (1 cell)

**Source**: `results/gold-standard-extended-buffer-sweep/extended-buffer-report.md` §10.

**Recovery procedure**: §10 step 2 contains the verbatim CLI, ready to use:

```bash
python scripts/evaluate_detections.py \
    --detections results/gold-standard-extended-buffer-sweep/verified_detections.geojson \
    --buffers 5 10 15 25 35 45 \
    --bootstrap 1000 --seed 42 \
    --ground-truth inputs/vectors/references/mounds-reference.geojson \
    --bounds inputs/vectors/bounds/384/h10_test_bounds.geojson \
    --output-dir results/gold-standard-extended-buffer-sweep \
    --label gold-standard-extended-buffer-sweep
```

Non-standard buffer list `5 10 15 25 35 45` (NOT 20/30/40/50). Verifier-detections file
`verified_detections.geojson` already exists in the cell directory (250 features filtered to
the 327-tile h10 allowlist at vote_t=4, prob_t=0.15).

**Sample CSV row**:

```text
status,eval_path,output_dir,detections,detections_dir,glob,bounds,ground_truth,buffers,bootstrap,seed,label,mcc
queued,results/gold-standard-extended-buffer-sweep/evaluation.json,\
results/gold-standard-extended-buffer-sweep,\
results/gold-standard-extended-buffer-sweep/verified_detections.geojson,,,\
inputs/vectors/bounds/384/h10_test_bounds.geojson,\
inputs/vectors/references/mounds-reference.geojson,5 10 15 25 35 45,1000,42,gold-standard-extended-buffer-sweep,0
```

---

## 4. Implementation choice — queue-build over runtime recovery

**Recommendation**: build the queue offline in a one-shot
`scripts/build_bootstrap_10k_queue_followup.py`; reuse the existing `scripts/run_bootstrap_10k.py`
unchanged.

### 4.1 Trade-off analysis

| Criterion | Queue-build | Runtime recovery |
|---|---|---|
| Code surface | new builder script (~250 LOC) + 0 changes to runner | 4 metadata-pattern parsers grafted onto runner (~150 LOC), runner gains heterogeneous CLI flags |
| Restart-ability | queue CSV is durable; rerun-by-index trivial | runner state-machine more complex; partial failures harder to resume |
| Audit trail | the CSV itself is the audit trail (committable artefact) | provenance is implicit in argv at run-time |
| Diff legibility | builder is read-only on configs/sidecars; review easy | runner becomes a swiss-army-knife; review harder |
| Schema-drift resilience | drift detected at queue-build (single failure mode); easy to inspect rows before launch | drift detected at run-time across 165 cells; could partially complete then fail |
| Failure-mode visibility | builder fails fast on missing path/file before any CPU is spent | runner discovers issues mid-sweep |

### 4.2 Concrete plan for the builder script

`scripts/build_bootstrap_10k_queue_followup.py` (NEW, ~250 LOC):

1. Header + docstring (purpose, usage, author, licence).
2. Constants: `REPO_ROOT`, group→config mappings, output queue path
   (`/tmp/bootstrap-10k-followup-jobs.csv`).
3. Function `build_paper_eval_rows()` → reads four batch YAMLs, slugifies labels, emits rows
   for the matching 143 cells; also emits the special 13 cells (`single-pass-n1*`,
   `pro-n10/`-adjacent if any, `n1/384px-outstanding/` overflow).
4. Function `build_pairwise_rows()` → reads `tile-size-comparison.yaml` + bespoke 5th cell.
5. Function `build_55maps_cleaned_gt_rows()` → reads three sidecar JSONs + resolves placeholders.
6. Function `build_gold_standard_rows()` → reads the report markdown §10 (regex-free; the CLI
   is fully literal — alternatively, hard-code the row).
7. `main()` — orchestrates, validates each row's input paths exist on disk, writes the CSV,
   prints a summary breakdown by group.
8. CLI flag `--validate-paths` (default ON) to check every detection / bounds / GT path
   resolves to a real file before writing the CSV.

The script is **read-only on configs and sidecars**; the only artefact it writes is the queue
CSV in `/tmp/`. No commits, no rollback risk during build.

### 4.3 What stays in `run_bootstrap_10k.py` (unchanged)

Lines 42–49 (CSV reader) and lines 62–86 (CLI builder) already handle the schema we need:
`detections | detections_dir + glob | batch`, `--ground-truth`, `--bounds`, `--buffers`,
`--seed`, `--label`, `--output-dir`, `--mcc`. Hard-coded `--bootstrap 10000` (line 80) is
exactly what we want. **No changes required.**

---

## 5. Dry-run protocol (4 cells)

Pick one cell from each group; the builder writes a 165-row CSV; we run only indices for these
4 cells with `--dry-run` first, then live with `xargs -P 1`.

### 5.1 Selected cells

| Group | Cell path | Index in CSV (TBD by builder) | Why this cell |
|---|---|---|---|
| paper-eval | `results/paper-eval/n1/384px/flash-text-minimal-t-0-0/evaluation.json` | TBD | Smallest paper-eval cell (single buffer, single condition); fastest dry-run |
| pairwise | `results/pairwise/tile-size-30m/512px-image-t0/evaluation.json` | TBD | Single-file detection; tests the `--detections` (not `--detections-dir`) path |
| 55maps-cleaned-gt | `results/55maps-cleaned-gt-evaluation/text-min/evaluation.json` | TBD | Slowest cell (8,541-tile bounds); validates the heavy case won't time out |
| gold-standard | `results/gold-standard-extended-buffer-sweep/evaluation.json` | TBD | Tests the non-standard buffer list `5 10 15 25 35 45` |

### 5.2 Validation steps per dry-run cell

1. Run the cell via `run_bootstrap_10k.py --index N --dry-run`; verify the printed CLI matches
   the parent sidecar's `command_shape` (allowing for buffer-list expansion and N=10K).
2. Re-run the cell live (no `--dry-run`); verify exit code 0 and wall time < 60 s for
   paper-eval/pairwise, < 5 min for the 55maps-cleaned-gt cell.
3. After live run, inspect the output `evaluation.json`:
   - `_metadata.cli_args.bootstrap == 10000`
   - `_metadata.bootstrap.n_iterations == 10000`
   - `summary.buffers` list and per-buffer F1 point estimates within ±0.005 of pre-rerun
     values (CI bounds will shift by Monte Carlo noise per Obs 303; do not flag bound shifts
     of ±0.01; flag only if the point estimate F1 changes — that would indicate a bug).
4. Inspect the diff: `git diff results/<cell-path>/evaluation.json`. Expect bound shifts of
   ~1 in the 4th decimal place; expect identical detection counts and identical TP/FP/FN.
5. If all 4 cells pass: launch the full sweep. If any cell fails: stop, report, do not proceed.

### 5.3 Expected dry-run timing (sapphire)

- paper-eval n1/384px cell: ~3–8 s CPU
- pairwise 512px-image-t0: ~3–8 s CPU
- 55maps-cleaned-gt text-min: ~2–4 min CPU (8,541 tiles × 10K bootstrap)
- gold-standard: ~5–15 s CPU (327 tiles × 10K × 6 buffers)

Total dry-run wall: ~5 minutes.

---

## 6. Sweep workflow (post-approval)

### 6.1 Compute target — sapphire

Per `CLAUDE.md` "Compute Location" rule: SSH to sapphire, run there. amd-tower fallback only
if sapphire unreachable.

### 6.2 Pre-sweep tag

```bash
git tag pre-bootstrap-10k-followup-2026-04-29 HEAD
git push origin pre-bootstrap-10k-followup-2026-04-29
```

This is the rollback anchor.

### 6.3 Build the queue (sapphire)

```bash
ssh sapphire 'cd ~/Code/map-reader-llm && git pull --ff-only && \
  source .venv/bin/activate && \
  python3 scripts/build_bootstrap_10k_queue_followup.py --validate-paths'
```

Expect: `/tmp/bootstrap-10k-followup-jobs.csv` (165 rows), printed summary by group.

### 6.4 Dry-run (4 cells)

```bash
ssh sapphire 'cd ~/Code/map-reader-llm && source .venv/bin/activate && \
  for i in <idx_paper> <idx_pairwise> <idx_55maps> <idx_gs>; do
    python3 scripts/run_bootstrap_10k.py --index $i --dry-run
  done'
```

User reviews the printed CLIs against the parent sidecars; approves or rejects.

### 6.5 Live dry-run on the same 4 cells

```bash
ssh sapphire 'cd ~/Code/map-reader-llm && source .venv/bin/activate && \
  for i in <idx_paper> <idx_pairwise> <idx_55maps> <idx_gs>; do
    python3 scripts/run_bootstrap_10k.py --index $i
  done && \
  git status results/'
```

User reviews `git diff` on the 4 cells before approving the full sweep.

### 6.6 Full sweep (parallel)

```bash
ssh sapphire 'cd ~/Code/map-reader-llm && source .venv/bin/activate && \
  seq 0 164 | xargs -n 1 -P 16 -I{} python3 scripts/run_bootstrap_10k.py --index {} \
  > /tmp/bootstrap-10k-followup-progress.log 2>&1'
```

Or use `parallel --bar` for live progress display. Concurrency 16 matches the prior overnight
sweep; sapphire has 24 cores so headroom remains.

### 6.7 Error handling

The runner already returns non-zero for `error`, `verify_failed`, `timeout`, `exception`.
Capture failed indices via:

```bash
seq 0 164 | xargs -n 1 -P 16 -I{} bash -c \
  'python3 scripts/run_bootstrap_10k.py --index $1 || echo "FAIL $1" >> /tmp/bootstrap-10k-followup-failures.log' _ {}
```

After the sweep, `cat /tmp/bootstrap-10k-followup-failures.log` lists indices for retry.

### 6.8 Push retry behaviour (lesson from overnight run)

Per `paper-writeup-continuity.md` line 1419: the overnight orchestrator stalled at the
rebase+push step on sapphire. The 4-commit-per-group strategy (§8) keeps each commit small,
which makes the rebase trivial. Retry policy:

- After each per-group commit, attempt `git pull --rebase origin main && git push origin main`.
- On rebase conflict: `git rebase --abort`, log the conflict, alert the user — do NOT
  auto-resolve; conflicts in evaluation.json bytes are subtle and risk silent corruption.
- If push fails for non-conflict reason (network, auth): retry up to 3 times with 30 s
  back-off; after 3 fails, alert user and stop.

---

## 7. Verification queries

After the full sweep, run these checks:

### 7.1 N=10K presence query

```bash
# All 165 cells must have _metadata.cli_args.bootstrap == 10000
python3 - <<'EOF'
import json
from pathlib import Path
import csv
queue = list(csv.DictReader(open('/tmp/bootstrap-10k-followup-jobs.csv')))
n_pass = n_fail = 0
fails = []
for row in queue:
    p = Path(row['eval_path'])
    try:
        with open(p) as f:
            d = json.load(f)
        cli = (d.get('_metadata') or {}).get('cli_args') or {}
        bs = cli.get('bootstrap')
        if bs == 10000:
            n_pass += 1
        else:
            n_fail += 1
            fails.append((str(p), bs))
    except FileNotFoundError:
        n_fail += 1
        fails.append((str(p), 'MISSING'))
print(f'PASS: {n_pass}/165 cells at N=10K')
print(f'FAIL: {n_fail}')
for f, bs in fails[:20]:
    print(f'  {f}: bootstrap={bs}')
EOF
```

Expected: `PASS: 165/165 cells at N=10K`, `FAIL: 0`.

### 7.2 Detection-count cross-check (sanity)

For each cell, the per-run detection counts in `evaluation.json.per_run[*].n_detections`
should be identical pre/post (we re-run the same detections). Spot-check 5 random cells:

```bash
python3 - <<'EOF'
import json, random, subprocess
from pathlib import Path
import csv
queue = list(csv.DictReader(open('/tmp/bootstrap-10k-followup-jobs.csv')))
sample = random.sample(queue, 5)
for row in sample:
    p = row['eval_path']
    # Compare current vs pre-tag
    cur = json.load(open(p))
    pre = json.loads(subprocess.check_output(
        ['git', 'show', f'pre-bootstrap-10k-followup-2026-04-29:{p}']).decode())
    cur_n = [r.get('n_detections') for r in cur.get('per_run', [])]
    pre_n = [r.get('n_detections') for r in pre.get('per_run', [])]
    print(f'{p}: pre={pre_n} cur={cur_n} match={cur_n == pre_n}')
EOF
```

Expected: every sampled cell shows `match=True`. Any False is a bug to investigate.

### 7.3 F1 point-estimate stability (Obs 303 sanity check)

Per Obs 303, F1 point estimates should be unchanged (bootstrap N affects CI MC-noise, not
point estimates). Spot-check 5 random cells; if a point estimate shifts > 1e-4, that's a bug:

```bash
python3 - <<'EOF'
import json, random, subprocess
import csv
queue = list(csv.DictReader(open('/tmp/bootstrap-10k-followup-jobs.csv')))
sample = random.sample(queue, 5)
for row in sample:
    p = row['eval_path']
    cur = json.load(open(p))
    pre = json.loads(subprocess.check_output(
        ['git', 'show', f'pre-bootstrap-10k-followup-2026-04-29:{p}']).decode())
    cur_b = (cur.get('summary') or {}).get('buffers') or []
    pre_b = (pre.get('summary') or {}).get('buffers') or []
    for cb, pb in zip(cur_b, pre_b):
        df1 = abs(cb['f1'] - pb['f1'])
        ok = df1 < 1e-4
        print(f'{p} @ {cb["buffer_metres"]}m: F1 pre={pb["f1"]:.4f} cur={cb["f1"]:.4f} Δ={df1:.5f} ok={ok}')
EOF
```

### 7.4 CI-width comparison (informational only — DO NOT use as pass/fail)

Per Obs 303, CI widths should be near-identical (ratio 0.96–1.02 in the prior overnight
spot-check). Compute for context, but do NOT use as a verification pass/fail criterion. The
pass criterion is §7.1 (N=10K presence); width comparison is for the paper write-up only.

---

## 8. Commit strategy — 4 commits, one per group

**Rationale**: per-group commits give:

- **Diff legibility**: each commit's diff is bounded to one results subtree; reviewers can
  scan one group at a time.
- **Rollback granularity**: if any single group has a bug discovered later, revert that commit
  alone; don't lose the work for the other 3 groups.
- **Rebase friendliness**: small commits rebase cleanly onto fast-moving `main`; one big
  165-cell commit risks larger merge conflicts.

**Conventional-commit format** (matching the overnight sweep's commit style):

```text
data(paper-eval): upgrade bootstrap CIs to N=10K

Upgrade bootstrap-CI iteration count from N=1000 to N=10000 across the
156 paper-eval evaluation.json cells. Methodology preserved per cell:
same buffers, seed=42, MCC flag, ground truth, bounds, label. Only the
--bootstrap value changed. Computed on sapphire (24 cores, 60 GiB)
under tag pre-bootstrap-10k-followup-2026-04-29.

Cells in this commit:
- n1/384px (11), n1/384px-all-buffers (18), n1/384px-outstanding (7)
- n1/512px (33), n1/512px-all-buffers (33)
- mcc/384px (18), mcc/512px (33)
- single-pass-n1, single-pass-n1-high, single-pass-n1-t07 (3)

Per Obs 303, CI bounds shift only by Monte Carlo noise (~1-2 % in
spot-check); F1/P/R point estimates and TP/FP/FN unchanged.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

Repeat for `data(pairwise-tile-size-30m): ...` (5 cells), `data(55maps-cleaned-gt): ...` (3
cells), `data(gold-standard-extended-buffer-sweep): ...` (1 cell).

**Order of commits**: paper-eval first (largest diff, most representative), then pairwise,
55maps-cleaned-gt, gold-standard. Rebase-and-push between each commit so the working tree
returns to clean before the next commit.

**Counter-argument considered (single commit)**: a single 165-cell commit would make the
"completion of the standardisation across all 540 cells" milestone visually atomic in
`git log`. Counter-counter: per-group is preferred because (a) the milestone is already
documented in Obs 304 (or wherever Obs 303 is forward-pointed); (b) the per-group commits map
1:1 to the 4 metadata recovery patterns, providing self-documenting structure; (c) any later
audit reads diffs by group anyway.

---

## 9. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Sapphire push conflicts (per overnight lesson) | medium | medium | Per-group commits; abort on rebase conflict; manual escalation; 3-retry policy on non-conflict push fails |
| Schema drift in batch YAMLs vs filesystem (e.g. extra cell, renamed condition) | medium | medium | Builder script's `--validate-paths` flag fails fast; user reviews queue CSV before launch; bespoke fall-back rows for the ~13 special paper-eval cells |
| `slugify(label)` mismatch between YAML labels and existing output dirs | medium | low | Dry-run on one cell per group catches this before scaling; if mismatch found, fix the slug map in the builder before re-running |
| 8,541-tile 55maps cells time out (3,600 s ceiling in runner line 100) | low | high | Run sequentially (`-P 1`) for 55maps cells if `-P 16` causes thrashing; 8,541 × 10K bootstrap on tile-level resampling is well within memory; monitor wall time on dry-run |
| Per-cell `evaluation.json` schema drift (older vs newer `evaluate_detections.py`) | low | low | New writes use the current script; pre-tag captures the old shape for rollback; the verification query reads `_metadata.cli_args.bootstrap` which all current writes produce |
| `n1/384px-outstanding/` cells not all in a single config (some bespoke) | medium | low | Build rows for the 7 cells from the all-buffers config; for any cell that doesn't appear in a config, fall back to a bespoke per-cell rule sourced from its existing `evaluation.json.per_run[0].label` |
| `mcc/512px` driven by N1-eval YAML with `--mcc` flag despite no dedicated `mcc-eval-512px.yaml` | high | low | Confirmed: `mcc/512px` cells share the 33 conditions of `n1-eval-512px-phase2.yaml` with `--mcc`; flag this in the builder as a known shared-source case |
| Buffer-list mismatch between sidecar-claimed and actual data (e.g. pairwise sidecar says `--buffers 30`, actual data is `[20,30]`) | medium | low | Builder reads buffers from the existing `evaluation.json.summary.buffers` of each target cell, NOT from the sidecar text; this is authoritative |
| `gold-standard` non-standard buffer list dropped during runner CLI build | low | medium | The runner's line 79 is `cmd += ['--buffers'] + row['buffers'].split()`; verify dry-run prints `--buffers 5 10 15 25 35 45` for this cell |

---

## 10. Pre-launch checklist (user must confirm before approving execution)

- [ ] Plan document `planning/daylight-followup-sweep-plan-2026-04-29.md` reviewed and approved
- [ ] Builder script approach (`build_bootstrap_10k_queue_followup.py`) preferred over runtime
      recovery
- [ ] Per-group commit strategy (4 commits) preferred over single-commit
- [ ] Sapphire is accessible (`ssh sapphire echo OK` returns OK)
- [ ] Rollback tag `pre-bootstrap-10k-followup-2026-04-29` will be created on `main` HEAD
      before the sweep
- [ ] Dry-run on the 4 selected cells (one per group) is a hard prerequisite before the full
      sweep launches
- [ ] Sweep concurrency `xargs -P 16` is acceptable on sapphire (matches prior overnight
      sweep)
- [ ] Push-retry policy: abort on rebase conflict; do NOT auto-resolve evaluation.json byte
      conflicts
- [ ] Verification query §7.1 (N=10K presence on all 165 cells) is the binding pass/fail
      criterion; CI-width is informational only
- [ ] User explicitly approves the `data(<group>): upgrade bootstrap CIs to N=10K` commit
      message template

---

## 11. Estimated effort

### 11.1 Implementation effort (Implement agent, post-approval)

- Builder script (~250 LOC): ~30–45 minutes drafting + diff review
- Dry-run validation (4 cells, ~5 min): ~10 minutes including review
- Full sweep on sapphire (`xargs -P 16`): ~30–60 minutes wall, mostly on the 3 55maps-cleaned-gt
  cells (~10 min CPU each at the 8,541-tile bounds; the other 162 cells finish in ≪ 30 s
  each)
- Verification queries §7.1–7.3: ~5 minutes
- 4 per-group commits + rebase-and-push between each: ~15–20 minutes (allowing for any
  resolvable rebase if origin moves)
- Obs 304 update (or Obs 303 forward-pointer): ~10 minutes

**Total Implement-agent wall**: ~2–2.5 hours under user supervision; ~30–60 min of that is
actual sapphire CPU.

### 11.2 CPU-hours on sapphire

Estimated CPU at `xargs -P 16`:

- 156 paper-eval cells × ~5–10 s each ≈ 13–26 min single-thread; ~1–2 min wall at P=16
- 5 pairwise cells × ~5–10 s ≈ 1 min single-thread; trivial at P=16
- 3 55maps-cleaned-gt cells × ~10 min each (8,541 tiles is the dominant cost) ≈ 30 min
  single-thread; ~10 min wall at P=16 (capped by single-cell wall)
- 1 gold-standard cell ~5–15 s ≈ trivial

**Aggregate CPU-hours**: ~0.5–1.0 CPU-hours; **wall**: 30–60 minutes at P=16.

### 11.3 API spend

**Zero**. This is a re-evaluation of cached detection geojsons against ground truth; no VLM
API calls.

---

## 12. Open questions for the user

1. **`pro-n10/` cell**: this directory contains `pro_n10_consensus_results.csv` and
   `metadata.json`, but NO `evaluation.json`. The cell-inventory lists 156 paper-eval cells
   with `evaluation.json`; `pro-n10/` is NOT one of them. Confirm this is correctly excluded.
2. **`mcc/{consensus-pv,phase2b,remaining}/` subtrees**: these contain `mcc.json` (not
   `evaluation.json`); excluded from the 156-cell scope. Confirm exclusion.
3. **`n1/384px-outstanding/` cells (7)**: do they share a config with `n1/384px-all-buffers/`,
   or were they bespoke one-off invocations? The builder will detect this empirically; if the
   condition labels don't appear in any config, the builder will need bespoke rows. User: do
   you have prior knowledge that helps the builder author this fall-back?
4. **Single-commit alternative**: §8 recommends 4 commits per group. If you'd prefer a single
   `data(bootstrap-10k-followup): ...` commit covering all 165 cells, say so before launch;
   the trade-off is documented but reversible.
5. **Verification query: include MCC-cell mcc value stability check?** §7.3 spot-checks F1
   point estimates only. The 18 + 33 = 51 MCC-flag cells will also have `tile_classification.mcc`
   point estimates that should be unchanged. Add a §7.5 check for these? (~5 lines of Python.)

---

## 13. Cross-references

- Obs 303 (`docs/notes/reflections/working-notes.md` line ~15019): bootstrap-N controls Monte
  Carlo noise, not CI width. The "what N=10K buys" framing for the paper.
- `planning/paper-writeup-continuity.md` lines 1372–1428: the spec this plan implements.
- `scripts/run_bootstrap_10k.py` (lines 42–86): existing CSV-driven runner; reused unchanged.
- `scripts/evaluate_detections.py` (lines 884–984): CLI surface this plan must conform to;
  unchanged.
- Bootstrap-10K commit chain: `4b31aae0..51f438bd` (11 commits); rollback anchor
  `pre-bootstrap-10k-2026-04-28` → `5040f5b4`.
- This plan's rollback tag (proposed): `pre-bootstrap-10k-followup-2026-04-29` → current HEAD
  (`6d798e83` at plan-write time; verify on launch).
