# Phase 3a Verifier Completeness — Recovery Runbook

**Purpose**: operationalise the recovery of the 30 gap-positive verifier cells
identified in `reports/phase3a-verifier-completeness-audit-2026-05-03.md`
(commit `adf95dbf`), restoring full verifier coverage on every paper-feeding
and legacy diagnostic cell across the four-map gold-standard (GS) corpus and
the broader Phase 3a leaderboard.

**Status**: PLAN ONLY (Session 85 prep, written 2026-05-03). Execution is
gated on the in-flight software fix landing first (see "Prerequisites").

**Out of scope**: the 8 unmatched cells from the audit (no traceable input
manifest) — see § "Unrecoverable cells" below.

---

## 0. Important up-front findings (read before sequencing)

Two findings from re-reading the audit and the cell schemata changed how the
campaign should be sized and sequenced. Both are surprising relative to the
audit's "30 cells, 19 paper-feeding" framing:

### 0.1 Eleven of the 30 "gap-positive" cells are derived, not verifier outputs

`probabilities.json` exists in two schema variants in this codebase:

- **Verifier output** (canonical): top-level keys
  `{version, mode, verifier_config, iterations, total_results, results}`,
  optionally `cleanup_history` after a `run_pv.py cleanup` pass.
- **Derived vote-threshold filter**: top-level keys
  `{source, derived_from, vote_threshold, results}` only — produced by
  `scripts/derive_vote_threshold_results.py` from a 1-of-N union verifier
  output by filtering on `vote_count >= x`.

A derived cell's `gap` is an **artefact of the source's gap propagated through
threshold filtering** — it is not an independent silent-drop. Cleaning the
source automatically cleans every derivative. Calling `run_pv.py cleanup` on
a derived cell would fail (it expects the canonical schema).

**The 11 derived cells in the audit are**:

| Derived cell | Gap | Source cell (run cleanup here instead) |
|---|---|---|
| `outputs/h11/e47-propose-brief/verified/flash-high-text-2of5` | 28 | `flash-high-text-1of5` |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-3of5` | 19 | `flash-high-text-1of5` |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-4of5` | 14 | `flash-high-text-1of5` |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-5of5` | 9 | `flash-high-text-1of5` |
| `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-1of5` | 8 | `pro-high-image-1of5-pro-verifier` |
| `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-2of5` | 3 | `pro-high-image-1of5-pro-verifier` |
| `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-3of5` | 3 | `pro-high-image-1of5-pro-verifier` |
| `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-4of5` | 3 | `pro-high-image-1of5-pro-verifier` |
| `outputs/h11/pv-diag-384/verified/pro-high-image-pro-vf-5of5` | 3 | `pro-high-image-1of5-pro-verifier` |
| `outputs/h11/pv-diag-384/verified/flash-high-text-medium-vf-1of5` | 1 | `flash-high-text-1of5-flash-medium-verifier` |
| (one e47 derivative `flash-high-text-1of5` IS the source — listed in tier 1) | | |

So the **30 cells reduce to 19 distinct verifier-output cells requiring API
spend**, plus a regeneration step (`derive_vote_threshold_results.py`) for the
11 derived cells once their sources are cleaned.

### 0.2 The largest gap (gap=460) is in a non-paper sweep cell

The audit's executive summary flags `flash-high-image-n5/image-t0.0/verified-v1-n10`
(gap=460, 57 % of pool) as "the largest single offender" and "most likely to
shift tier rankings". A repo-wide grep across `scripts/`, `results/`, `docs/`,
`planning/` finds **zero references** to this cell. The image-temperature
sweep leaderboard cells use `t=0.3`, `t=0.7`, `t=1.0` only; `t=0.0` was a
sweep point that did not survive into any leaderboard or analysis output.

Recommendation: still recover for transparency and to close the silent-drop
ledger, but de-prioritise it (Tier 2, not Tier 1). Movement risk to paper
claims is zero.

### 0.3 verified-v2 is a contamination-policy investigation cell

`outputs/55maps-generalisation/verified-v2` (gap=3) uses
`verify_adversarial-text_v2` (per `docs/methodology/v2-verifier-contamination-policy.md`).
Only one current consumer:
`results/55maps-generalisation/v2-threshold-sweep-50m/threshold_sweep.json`.
Not paper-citation-load-bearing in current state. Tier 2.

---

## 1. Scope and prerequisites

### 1.1 Cell inventory (after de-duplicating derived cells)

**19 verifier-output cells** + **11 downstream derived cells** to regenerate:

#### Tier 1 — paper-cited verifier outputs (8 cells; gap = 257 of 835)

| # | Cell | Gap | Verifier model / config | Downstream consumers |
|---|---|---|---|---|
| 1 | `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5` | **57** | flash, `verify_adversarial-text` | `compare_wbf_vs_greedy_production.py`; e47 leaderboard tiers (era2/consensus); `derive_vote_threshold_results.py` regenerates 4 derivatives (2of5, 3of5, 4of5, 5of5) |
| 2 | `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-adversarial-text` | **41** | flash, `verify_adversarial-text` | `materialise_session78_geojsons.py`; `session-78-text-adversarial-text-487tile.json` |
| 3 | `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-brief-text` | **27** | flash, `verify_brief-text` | `materialise_session78_geojsons.py`; `session-78-text-brief-text-487tile.json` |
| 4 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-adversarial-text` | **26** | flash, `verify_adversarial-text` | `materialise_session78_geojsons.py`; `session-78-image-adversarial-text-487tile.json` |
| 5 | `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.7/session-78-matrix/verified-checklist-text` | **21** | flash, `verify_checklist-text` | `materialise_session78_geojsons.py`; `session-78-text-checklist-text-487tile.json` |
| 6 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist-text` | **19** | flash, `verify_checklist-text` | `materialise_session78_geojsons.py`; `session-78-image-checklist-text-487tile.json` |
| 7 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-brief-text` | **19** | flash, `verify_brief-text` | `materialise_session78_geojsons.py`; `session-78-image-brief-text-487tile.json` |
| 8 | `outputs/h8-v2/wbf/scale-4/verified` | **15** | flash, `verify_adversarial-text` | `results/h8-v2/wbf/scale-4/evaluation.json`; `permutation-wbf-s4-vs-s8` paired test |

Tier-1 sub-total: **205 candidates** (Session 78 matrix dominates: 153) +
e47 source 57 = **257 candidates**.

#### Tier 2 — sweep / smaller paper-cited / contamination-policy (5 cells; gap = 477)

| # | Cell | Gap | Notes |
|---|---|---|---|
| 9  | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10` | **460** | Sweep cell; **NOT cited** in any leaderboard / script (see § 0.2). Recover for ledger completeness. |
| 10 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5` | **11** | Image temperature sweep; feeds `flash-high-image-n5-t0.3-greedy-v1-487tile.json`. Likely <0.005 F1 movement. |
| 11 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist` | **1** | Image-side session-78. Trivial. |
| 12 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5` | **1** | Image-temperature sweep t=1.0; feeds `flash-high-image-n5-t1.0-greedy-v1-487tile.json`. |
| 13 | `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5` | **1** | Image-temperature sweep t=0.7; feeds `flash-high-image-n5-t0.7-greedy-v1-487tile.json`. |
| 14 | `outputs/h11/pv-diag-384/scale-4-optimal-487/verified-v1-n10` | **1** | Feeds `scale4-optimal-greedy-v1-487tile.json` leaderboard cell. |
| 15 | `outputs/55maps-generalisation/verified-v2` | **3** | v2 contamination policy investigation; only consumer is `v2-threshold-sweep-50m/threshold_sweep.json`. |

Tier-2 sub-total: **478 candidates** (gap=460 dominates).

#### Tier 3 — legacy `pv-diag-384/verified/` and proposer-verifier-384 (6 cells; gap = 40)

| # | Cell | Gap | Verifier model | Notes |
|---|---|---|---|---|
| 16 | `outputs/h11/pv-diag-384/verified/text-baseline-pro-verifier` | **21** | **gemini-3.1-pro-preview, thinking=medium** | Legacy cross-verifier exploratory; cited by `overnight-pro-verifier-all.sh`, `sapphire-final-sweeps.sh`, `sapphire-pro-verifier-analysis.sh`, `results/h11-384-pv-diagnostic/text-baseline-pro-verifier/threshold_sweep.json`. |
| 17 | `outputs/h11/pv-diag-384/verified/pro-medium-image-baseline-pro-verifier` | **10** | **gemini-3.1-pro-preview, thinking=medium** | Same family as #16. |
| 18 | `outputs/h11/pv-diag-384/verified/pro-high-image-1of5-pro-verifier` | **8** | **gemini-3.1-pro-preview, thinking=medium** | Source for the 5 derived `pro-high-image-pro-vf-Nof5` cells. Has `iterations=1, mode=batch` — original was 2026-Q1 batch run; cleanup runs in real-time mode (acceptable). |
| 19 | `outputs/h11/pv-diag-384/verified/flash-high-text-1of5-flash-medium-verifier` | **1** | flash, thinking=medium | Source for derived `flash-high-text-medium-vf-1of5`. |
| 20 | `outputs/h11/proposer-verifier-384/verified-adversarial-text-v1-prompt` | **1** | flash, `verify_adversarial-text` | Audit notes: "no current script or analysis output references this cell"; classified non-paper. Inputs at `outputs/h11/proposer-verifier-384/candidates/candidate_manifest.json` (572 expected). |

Tier-3 sub-total: **41 candidates**, but **3 of 5 cells use gemini-3.1-pro at
thinking=medium** — much more expensive per call than flash (see § 2).

**Grand total verifier-output cells: 19; cumulative API gap to recover: 776
candidates** (matches the audit's 773 + 1 of 1 of the proposer-verifier-384
gap to within rounding; the 11 derivative cells' 62 cumulative gap regenerates
for free from the cleaned sources).

### 1.2 Prerequisites

Recovery executes only after **all** of the following:

1. **Software fix landed**: the in-flight verifier-completeness pipeline-level
   guard (assertion / improved retry handling / cardinality check at end of
   `run_pv.py verify`) is committed to `main`. The commit hash should be
   recorded by the operator at execution time. The runbook does not depend on
   the fix's specific surface — `run_pv.py cleanup` is independent of the
   verify-time guard — but executing recovery before the fix lands risks
   re-introducing identical silent-drop patterns in the same cells.

   **Sentinel check** (template script enforces): a sentinel file
   `.phase3a-recovery-fix-landed` exists at the repo root and contains the
   commit hash of the fix landing commit. Operator creates this manually after
   verifying the fix on `main` (`git log -1 --format=%H >
   .phase3a-recovery-fix-landed`). The template script aborts with a clear
   error if the sentinel is missing.

2. **Sapphire available** (per project compute-location policy):
   `ssh sapphire` succeeds; the repo on sapphire is at the same commit; venv
   activated.

3. **Working tree clean** (`git status` shows no modifications); current
   branch up to date with `origin/main`.

4. **Backup retention**: `outputs/**/*.pre-cleanup-*.backup` is gitignored
   (`.gitignore:122`); operator must `tar -cz` the soon-to-be-touched cells'
   pre-recovery state separately if a non-git rollback path is wanted (see
   § 9). The `cleanup_history` audit trail inside `probabilities.json` is the
   primary preserved record.

5. **Cost budget approved**: see § 2. Operator confirms the total budget
   before launching Tier 2 (image-t0.0 gap=460 dominates Tier 2 cost) and
   again before launching Tier 3 (Pro thinking=medium).

---

## 2. Cost estimate

### 2.1 Per-call cost evidence (from already-recovered cells)

Computed from `run.meta.json::cost_estimate` and `usage_stats` of the four
Session-83/84 cleanup passes:

| Cleanup pass | Cleaned candidates | Cost | Per-call cost | Model + thinking |
|---|---|---|---|---|
| T=0.7 verifier (74 cands) | 74 | $0.10168 | **$0.001374** | flash, minimal |
| Image (1 cand) | 1 | $0.00145 | **$0.001450** | flash, minimal |
| Text-MIN (39 cands) | 39 | $0.05285 | **$0.001355** | flash, minimal |
| GS-v2 (11 cands) | 11 | $0.01562 | **$0.001420** | flash, minimal |
| **Mean (flash, minimal, single-attempt success)** | | | **~$0.00140 per call** | |

All four runs succeeded on attempt 1 of 3 (`max_attempts=3` default), so the
empirical cost is one verifier call per missing candidate. Worst case is 3
attempts × first attempt's cost; allow a 3× headroom multiplier.

### 2.2 Pro thinking=medium per-call extrapolation

Three Tier-3 cells use `gemini-3.1-pro-preview` at `thinking=medium`. Pricing
(per `prompts/configs/verify_adversarial-text.json`-style snapshot in the
existing meta files): Pro has materially higher per-token cost than Flash and
medium thinking adds reasoning tokens. From the audit's prior context (no
direct pro-cleanup precedent in this repo), extrapolating from the flash
ratio + a conservative 5× multiplier for Pro-medium versus Flash-minimal:

- Estimated pro-medium per-call: **~$0.007 per call** (5× flash baseline; not
  empirically validated — first cleanup attempt will produce ground truth and
  the script logs actuals).

### 2.3 Tier sub-totals

| Tier | Cells | Candidates | Per-call | Best (1 attempt) | Expected (1.5×) | Worst (3×) |
|---|---|---|---|---|---|---|
| **Tier 1** (8 paper flash cells) | 8 | 205 | $0.00140 | **$0.29** | $0.43 | $0.86 |
| **Tier 2** (5 sweep + 1 v2 + 1 scale-4 = 7 cells, all flash) | 7 | 478 | $0.00140 | **$0.67** | $1.00 | $2.01 |
| **Tier 3a** (3 pro-medium cells: text-baseline + pro-medium-image + pro-high-image-1of5) | 3 | 39 | $0.007 | **$0.27** | $0.41 | $0.82 |
| **Tier 3b** (3 flash cells: flash-medium-verifier + adversarial-text-v1-prompt) | 2 | 2 | $0.00140 | **<$0.01** | <$0.01 | $0.01 |
| **Campaign** | **20** (incl Tier 3 split) | **724** | mixed | **~$1.23** | **~$1.84** | **~$3.70** |

**Headline budget for approval**: planned $2 (expected case, 1.5× empirical
single-attempt cost); cap $5 (explicit confirm threshold); hard stop $10
(abort if approached — see § 8).

> **Note**: this is verifier API cost only. Downstream propagation
> (re-evaluation, leaderboard rebuilds, paired permutation, attractor-pull,
> FP-classify) is CPU-only (zero API cost) and runs on sapphire; wall-clock
> dominated by paired-permutation N=100K bootstrap which has been previously
> measured at ~5–15 min per pair on sapphire.

### 2.4 Stop-and-confirm thresholds

The template script enforces:

- After Tier 1 completes: report cumulative actual cost. If > $1.00, halt and
  request operator confirmation before Tier 2.
- After Tier 2 completes: report cumulative cost. If > $3.00, halt and require
  explicit confirmation before Tier 3.
- Hard cap: $10 cumulative spend across all tiers — script aborts and
  prints diagnostic state.

---

## 3. Sequencing

Tiers execute strictly in order (1 → 2 → 3); within each tier, cells are
ordered to maximise downstream-propagation batching:

### Tier 1 (paper-cited; do first — highest information value)

**Group 1A: Session 78 matrix (6 cells; gap = 153)** — these all materialise
through `scripts/materialise_session78_geojsons.py` and feed the same
leaderboard tier rebuilt by `scripts/build_tiered_leaderboard.py`. Run all 6
cleanups before invoking the materialise step once, then rebuild the
leaderboard once.

Order within group (largest gap first to surface any failures early):

1. text-t0.7 / verified-adversarial-text (gap 41)
2. text-t0.7 / verified-brief-text (gap 27)
3. image-t0.7 / verified-adversarial-text (gap 26)
4. text-t0.7 / verified-checklist-text (gap 21)
5. image-t0.7 / verified-checklist-text (gap 19)
6. image-t0.7 / verified-brief-text (gap 19)

**Group 1B: e47-propose-brief (1 cell; gap = 57 + 4 derived cells regenerate)**

- (cell 7) `e47-propose-brief/verified/flash-high-text-1of5` (gap 57). Then
  run `scripts/derive_vote_threshold_results.py` to regenerate 2of5, 3of5,
  4of5, 5of5.

**Group 1C: h8-v2 WBF (1 cell; gap = 15)**

- (cell 8) `h8-v2/wbf/scale-4/verified` (gap 15).

### Tier 2 (smaller / sweep / contamination-policy)

Execute in roughly descending gap order, but the gap=460 cell at the start
allows the operator to confirm the cost-per-call scaling on a real workload
before committing to the rest:

- (cell 9) `pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10`
  (gap 460) — **stop-and-confirm point** even within Tier 2: if actual cost
  diverges from the estimate by > 2×, halt before continuing.
- (cell 10) `pv-diag-384/flash-high-image-n5/image-t0.3/verified-v1-n5`
  (gap 11)
- (cell 11) `55maps-generalisation/verified-v2` (gap 3)
- (cell 12) `pv-diag-384/flash-high-image-n5/image-t1.0/verified-v1-n5`
  (gap 1)
- (cell 13) `pv-diag-384/flash-high-image-n5/image-t0.7/verified-v1-n5`
  (gap 1)
- (cell 14) `pv-diag-384/flash-high-image-n5/image-t0.7/session-78-matrix/verified-checklist`
  (gap 1)
- (cell 15) `pv-diag-384/scale-4-optimal-487/verified-v1-n10` (gap 1)

### Tier 3 (legacy diagnostic; user-requested for completeness)

Pro-medium cells first (highest per-call cost; surface failures cheaply on a
small set):

- (cell 16) `pv-diag-384/verified/text-baseline-pro-verifier`
  (gap 21, **pro-medium**)
- (cell 17) `pv-diag-384/verified/pro-medium-image-baseline-pro-verifier`
  (gap 10, **pro-medium**)
- (cell 18) `pv-diag-384/verified/pro-high-image-1of5-pro-verifier`
  (gap 8, **pro-medium**) — then run `derive_vote_threshold_results.py` to
  regenerate 5 `pro-high-image-pro-vf-Nof5` derivatives.
- (cell 19) `pv-diag-384/verified/flash-high-text-1of5-flash-medium-verifier`
  (gap 1, flash-medium) — then regenerate `flash-high-text-medium-vf-1of5`.
- (cell 20) `proposer-verifier-384/verified-adversarial-text-v1-prompt`
  (gap 1, flash)

---

## 4. Per-cell recovery procedure

### 4.1 Canonical recipe (executed per cell)

```bash
# 1. cleanup the missing candidates (writes a .pre-cleanup-<ts>.backup
#    automatically; appends a cleanup_history audit entry).
python scripts/run_pv.py cleanup \
  --crops-dir <CROPS_DIR> \
  --verified-dir <VERIFIED_DIR> \
  --verifier-config <CONFIG_PATH> \
  --max-attempts 3 \
  --safe-mode-tokens 2048   # only on attempt 3 — prevents thinking-token exhaustion

# 2. (sources of derived cells only) regenerate downstream derivatives
python scripts/derive_vote_threshold_results.py \
  --consensus <CONSENSUS_GEOJSON> \
  --probabilities <CLEANED_PROBS_PATH> \
  --manifest <MANIFEST_PATH> \
  --pool-size 5 \
  --output-dir <PARENT_DIR_OF_DERIVATIVES> \
  --prefix <PREFIX>

# 3. re-evaluate against the cell's evaluation pipeline (see § 6 for the
#    artefact map per cell)

# 4. propagate downstream (leaderboard / matrix / paired-permutation /
#    attractor-pull / FP-classification — see § 6)

# 5. commit per cell or per group (see § 9)
```

### 4.2 Per-cell argument map

The template script `run-phase3a-recovery.sh.template` resolves the four
paths (`--crops-dir`, `--verified-dir`, `--verifier-config`, downstream
artefacts) per cell from a static lookup table. The table is populated from
the audit's "Gap-positive cells, expanded" section + `run.meta.json`'s
`configuration.instruction_file` cross-reference. For each cell, the
verifier config to pass to `--verifier-config` is the matching file under
`prompts/configs/`:

| Cell pattern | Config to use |
|---|---|
| `verified-adversarial-text` (image or text track) | `prompts/configs/verify_adversarial-text.json` |
| `verified-brief-text` | `prompts/configs/verify_brief-text.json` |
| `verified-checklist-text` | `prompts/configs/verify_checklist-text.json` |
| `verified-checklist` (no -text suffix; image-side) | `prompts/configs/verify_checklist.json` |
| `verified-v2` under `55maps-generalisation/` | `prompts/configs/verify_adversarial-text_v2.json` |
| `pv-diag-384/verified/*-pro-verifier` (Tier 3 pro-medium) | `prompts/configs/verify_adversarial-text.json` + `--model gemini-3.1-pro-preview --thinking-level medium` (model-and-thinking overrides) |
| `pv-diag-384/verified/*-flash-medium-verifier` (Tier 3 flash-medium) | `prompts/configs/verify_adversarial-text.json` + `--thinking-level medium` |

Operator MUST verify each config selection by reading the cell's
`run.meta.json::configuration.instruction_file` and `model` /
`thinking_level` fields before launching its cleanup. The template script
auto-extracts these and constructs the command, but the operator should
spot-check the first cell of each tier.

### 4.3 Special cases

- **`verified-v2` (gap=3)**: the `_v2` config is "contamination-policy"; the
  audit's `verify_adversarial-text_v2` is correct and exists at
  `prompts/configs/verify_adversarial-text_v2.json`. No deviation from the
  recipe.
- **`pro-high-image-1of5-pro-verifier`**: original ran in `mode=batch`
  (legacy 2026-Q1 batch API). Cleanup runs in real-time mode — fine for
  filling 8 candidates; no schema impact (both modes write the same
  `results` dict structure).
- **`proposer-verifier-384/verified-adversarial-text-v1-prompt`**: input
  manifest at `outputs/h11/proposer-verifier-384/candidates/candidate_manifest.json`
  (note `candidates/`, not `crops/`). Pass `--crops-dir
  outputs/h11/proposer-verifier-384/candidates`.

---

## 5. Sanity checks at each phase

### 5.1 Per-cell post-cleanup invariants

```python
# Equivalent of the audit's gap formula, post-cleanup:
gap_after = expected_input - len(probabilities['results'])
assert gap_after == 0, f"residual gap {gap_after} on {cell}"
```

The template script enforces this by running the audit script
(`/tmp/verifier_audit.py` from the original audit, copied into `scripts/` as
part of the campaign) on the affected cell post-cleanup and asserting
`gap == 0`. If non-zero, the cell halts and the campaign continues with the
next cell (the `cleanup_history` entry's `still_missing_ids` is recorded for
follow-up).

### 5.2 Per-cell post-evaluation invariants

For every re-evaluated cell:

- F1, MCC, and detection-count delta from pre-recovery state are logged.
- Sign of any tier-ranking-relevant comparison is documented (paper-feeding
  cells only).
- If the F1 shift is > 0.01, the operator is prompted to inspect manually
  (this magnitude was the GS-v2 +0.013 in Session 84; flagging it surfaces
  any anomalies for the user before propagating).

### 5.3 Per-tier post-rebuild invariants

For Tier 1: after the leaderboard rebuild, tier-membership of cells in the
canonical leaderboard tier is logged. Any tier-membership flip is highlighted
for the operator. (Expected: zero flips — gaps of 1–41 against pools of
2,000–4,000 historically produce <0.005 F1 shifts.)

### 5.4 Pre-commit invariants

- Tier-1 tests (`pytest -m tier1`) green.
- `ruff check` clean on any modified Python.
- `git status` shows only intended file changes.

---

## 6. Downstream propagation matrix

For each verifier-output cell, the artefacts that need refreshing. Items
marked **(auto)** are regenerated by an existing script; **(manual)** items
require operator edits to Markdown.

### 6.1 Tier 1 propagation

#### Session 78 matrix (6 cells, batched)

After all 6 Session-78 cells are clean:

1. `python scripts/materialise_session78_geojsons.py` **(auto)** — emits 6
   GeoJSONs under `results/leaderboard/era2/pv-materialised/`.
2. `python scripts/compute_session78_calibration_matrix.py` **(auto)** —
   refreshes `results/verifier-calibration-matrix/{text,image}-*/calibration.json`.
3. `python scripts/build_tiered_leaderboard.py` **(auto)** — rebuilds the 6
   `session-78-{image,text}-{adversarial,brief,checklist}-text-487tile.json`
   leaderboard cells under `results/leaderboard/cells/`.
4. `bash scripts/finalise_per_arch_leaderboard.sh` **(auto)** — regenerates
   `results/leaderboard/per-architecture/era2/consensus/leaderboard_tiers_*.{json,md}`.
5. `bash scripts/build_combined_leaderboard.sh` **(auto)** — combined
   architecture leaderboard.
6. `bash scripts/build_combined_tier_stability.sh` **(auto)** — tier
   stability tables.
7. **(manual)** Refresh paper-citation Markdown referencing session-78 tier
   numbers — locate via `grep -rl session-78 docs/ planning/`.

#### e47-propose-brief (1 cell + 4 derivatives)

1. Run `scripts/derive_vote_threshold_results.py` with `--prefix flash-high-text`
   on the cleaned `flash-high-text-1of5` source **(auto)** — regenerates
   2of5, 3of5, 4of5, 5of5 with cleaned candidates.
2. `python scripts/compare_wbf_vs_greedy_production.py` **(auto)** —
   refreshes the WBF-vs-greedy comparison output.
3. `python scripts/build_tiered_leaderboard.py` **(auto)** for e47 cells.
4. `bash scripts/finalise_per_arch_leaderboard.sh` **(auto)** — re-rolls
   the per-arch consensus leaderboard cells (`leaderboard_tiers_*.{json,md}`
   under `era2/consensus/`).
5. **(manual)** Spot-check `results/leaderboard/per-architecture/mc-precision-flags.md`
   for any newly-flagged tests after the rebuild.

#### h8-v2 WBF scale-4 (1 cell)

1. `python scripts/evaluate_detections.py` for `outputs/h8-v2/wbf/scale-4/`
   **(auto)** — refreshes `results/h8-v2/wbf/scale-4/evaluation.json`.
2. `python scripts/paired_permutation_consensus.py` **(auto)** — refreshes
   `results/h8-v2/verifier-sweep/permutation-wbf-s4-vs-s8/pairwise_permutation_result.json`.
3. **(manual)** Update `docs/notes/reflections/working-notes.md` if the s4
   vs s8 comparison's significance status changes.

### 6.2 Tier 2 propagation

#### Image-temperature sweep (5 cells: t0.0/t0.3/t0.7/t1.0)

1. `python scripts/evaluate_detections.py` for each affected cell **(auto)**.
2. `python scripts/build_tiered_leaderboard.py` **(auto)** — rebuilds
   `flash-high-image-n5-t{0.3,0.7,1.0}-greedy-v1-487tile.json` (note: t0.0
   produces no leaderboard cell per § 0.2).
3. `bash scripts/finalise_per_arch_leaderboard.sh` **(auto)**.
4. `python scripts/analyse_secondary_effects.py`,
   `analyse_consensus_sd_shrinkage_v2.py`,
   `analyse_inter_pass_agreement.py`,
   `analyse_token_efficiency.py`,
   `analyse_proposer_vote_fraction.py` **(auto)** — these consume the image-n5
   sweep cells. Run together at end of Tier 2 to batch.

#### scale-4-optimal-487 (1 cell)

1. `evaluate_detections.py` **(auto)**.
2. `build_tiered_leaderboard.py` **(auto)** — rebuilds
   `scale4-optimal-greedy-v1-487tile.json`.
3. `finalise_per_arch_leaderboard.sh` **(auto)**.

#### verified-v2 (1 cell)

1. Refresh `results/55maps-generalisation/v2-threshold-sweep-50m/threshold_sweep.json`
   via the threshold-sweep script (locate via `grep -rl threshold_sweep
   scripts/`) **(auto)**.
2. **(manual)** Annotate `docs/methodology/v2-verifier-contamination-policy.md`
   with the post-recovery numbers if it cites the verified-v2 F1.

### 6.3 Tier 3 propagation

Tier-3 cells feed legacy `results/h11-384-pv-diagnostic/<cell-name>/threshold_sweep.json`
artefacts and the historical "pro-verifier" exploratory analysis. Reduced
propagation:

1. For the 3 pro-medium cells: rerun their threshold-sweep scripts (locate
   via `grep -rln threshold_sweep scripts/sapphire-pro-verifier-analysis.sh`)
   **(auto)**.
2. After cleaning `pro-high-image-1of5-pro-verifier`, regenerate the 5
   `pro-high-image-pro-vf-Nof5` derivatives via
   `derive_vote_threshold_results.py` **(auto)**.
3. After cleaning `flash-high-text-1of5-flash-medium-verifier`, regenerate
   `flash-high-text-medium-vf-1of5` derivative similarly.
4. The `proposer-verifier-384/verified-adversarial-text-v1-prompt` cell has
   no current consumer per the audit; cleanup is for ledger completeness only,
   no propagation needed.
5. **(manual)** Document the Tier-3 recovery in a new working-notes
   observation entry — see § 7.

### 6.4 Cross-track impact (post-Tier-1 / post-Tier-2)

If any Tier-1 paper-cited cell shows F1 movement > 0.005 absolute, the
following downstream artefacts MAY need refreshing (per the Session 84
post-recovery template):

- `results/55maps-pairwise-permutation-v2/summary.md` (cross-track paired
  permutation — only if image or text-HIGH track values shifted; **none of
  the Tier-1 cells map to these tracks**, so this should be unaffected).
- Cross-track FP-classify (`scripts/55maps-fp-classify.py`,
  `gs-fp-classify.py`) — same reasoning; unaffected.
- Cross-track attractor-pull v2 — same; unaffected.

The campaign therefore should NOT trigger a cross-track v2 grid rebuild
unless evaluation surfaces an unexpected magnitude movement (§ 5.2 ≥ 0.01
threshold).

---

## 7. Documentation updates required

After campaign completion (or per-tier checkpoint):

### 7.1 New observation entries (working-notes.md)

Expect 1 observation entry covering the campaign as a whole, plus per-tier
addenda if any unexpected findings surface:

- **Obs N (campaign close-out)**: scope (30 → 19 + 11 cells), per-tier cost
  ledger (actuals), F1 / MCC / tier-rank deltas summary, software-fix commit
  hash referenced, links to the per-tier commits.

If Tier-1 surfaces a tier-ranking flip on any leaderboard, a separate Obs
should document it before propagating.

### 7.2 Continuity doc update

`planning/paper-writeup-continuity.md` — append a "Session 85 closure" arc
section (or equivalent), structured analogously to "Session 84 closure":

- Headline: total campaign cost, candidates recovered, F1/MCC deltas table,
  paper claims affected (expected: none).
- Per-cell outcome table.
- Bug discoveries section (likely empty if software fix is sound).
- "Things to NOT redo" list.
- Pending items rolled forward.

### 7.3 Paper-citation Markdown refresh

For each Tier-1 cell with > 0.001 F1 movement, find any Markdown that quotes
the cell's canonical numbers via:

```bash
grep -rln "<cell-name>\|<f1-value>" docs/ planning/ results/ | grep -v archive/
```

Refresh in place. Do NOT rewrite already-correct numbers (the e47-propose-brief
F1 is currently quoted in roughly a dozen leaderboard `.md` files; only update
if the new value differs).

### 7.4 Audit report annotation

Append a note to the bottom of
`reports/phase3a-verifier-completeness-audit-2026-05-03.md`:

```markdown
## Recovery status (annotated post-execution)

- Recovery campaign run: <date>, commits <range>.
- All 30 cells now gap=0 (re-audited with the same script).
- See `planning/phase3a-verifier-recovery-runbook.md` for the recovery procedure
  and outcome table.
```

---

## 8. Stopping conditions

### 8.1 Per-cell halt (campaign continues)

The script halts the affected cell's recovery and continues with the next
cell when:

- `cleanup` exits with non-zero (still-missing > 0 after max attempts).
- Post-cleanup `gap > 0` invariant fails.
- Post-evaluation F1 delta > 0.05 absolute (anomalous magnitude — the
  GS-v2 +0.013 in Session 84 was the largest observed; > 0.05 indicates
  something else is wrong).
- Re-evaluation script exits with non-zero.

### 8.2 Campaign halt (require operator confirmation to resume)

The script halts the entire campaign when:

- Cumulative cost > $5 (require explicit confirmation to continue).
- Cumulative cost > $10 (hard abort; no resume without re-approval).
- 3 consecutive cleanup invocations fail.
- Software-fix sentinel (`.phase3a-recovery-fix-landed`) is missing or empty.

### 8.3 Tier-boundary checkpoints

The script pauses for explicit operator confirmation at:

- End of Tier 1 → before starting Tier 2.
- End of Tier 2 → before starting Tier 3.
- After cell #9 (gap=460, the cost-validation cell) within Tier 2.

---

## 9. Commit / push policy

### 9.1 Commit boundaries

One commit per **logical group**, not per cell. The Session 84 template
worked at 5–8 commits per recovery arc; this campaign aims for ~12–15
commits total:

- Tier 1 — Session-78 matrix: 1 commit for the 6 cleanups (probabilities
  changes batched), then 1 commit per propagation step (materialise →
  calibration matrix → leaderboard rebuild → per-arch finalise → docs).
  ~6 commits for Tier 1 Group 1A.
- Tier 1 — e47: 1 commit for source cleanup + derivative regeneration; 1
  for compare_wbf_vs_greedy_production refresh; 1 for leaderboard rebuild.
  ~3 commits.
- Tier 1 — h8-v2 WBF: 1 commit for cleanup + evaluate; 1 for paired
  permutation. ~2 commits.
- Tier 2: 1 commit per cell-or-group + 1 for the bulk
  analyse_secondary_effects propagation. ~4 commits.
- Tier 3: 1 commit for the 3 pro-medium cleanups + threshold-sweep refresh;
  1 for the 2 flash legacy cleanups; 1 for derivative regeneration.
  ~3 commits.
- Closure: 1 docs commit (continuity update + audit annotation + new
  working-notes Obs).

Use conventional-commit format (`type(scope): subject`):

- `analysis(p3a-recovery): cleanup session-78 matrix verifier outputs (6 cells, 153 cands)`
- `analysis(p3a-recovery): rebuild session-78 leaderboard tiers post-cleanup`
- `docs(p3a-recovery): annotate audit report + Obs N + continuity update`

Include the co-author trailer:

```text
Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

### 9.2 Push frequency

Push at **tier boundaries**: after Tier 1's last commit, after Tier 2's
last commit, after the closure commit. Per project policy ("commit AND
push agent-produced work BEFORE asking for review"), do not let multi-cell
work sit unpushed.

### 9.3 Commit hygiene

- Do NOT include `.pre-cleanup-*.backup` files (gitignored).
- Do NOT include `.claude/`, `.venv/`, untracked working files.
- DO include all cost manifest changes, all materialised geojsons, all
  evaluation jsons, all leaderboard cell jsons.

---

## 10. Rollback plan

If a recovery introduces an unexpected regression (e.g. a Tier-1 leaderboard
cell flips tiers in a way that contradicts a paper claim, or a re-evaluation
exposes a deeper data issue):

### 10.1 Soft rollback (preferred)

`git revert <commit-range>` for the affected commits. The
`.pre-cleanup-<timestamp>.backup` files alongside `probabilities.json`
preserve the pre-recovery state locally; the audit-trail
`cleanup_history` entry inside the new `probabilities.json` records what
was changed. Revert restores the pre-recovery state in the working tree.

### 10.2 Backup-driven rollback

If `git revert` is awkward (e.g. mid-tier failure crossing multiple
commits):

```bash
# Restore probabilities.json from the per-cell backup
cp <cell>/probabilities.json.pre-cleanup-<ts>.backup <cell>/probabilities.json
# Then re-run downstream propagation against the restored state
```

The backup files are written automatically by `run_pv.py cleanup`. They
are **gitignored** — preserve them to a side path
(`tar -cz` to `archive/phase3a-recovery-<date>/`) if the rollback may need
to span more than a few sessions.

### 10.3 Worst case: rebuild from canonical

If both the live `probabilities.json` and the local `.backup` are corrupted,
the canonical pre-recovery state is in commit `adf95dbf` (audit commit) — it
predates this campaign by definition. Restore via `git show
<adf95dbf>:<cell>/probabilities.json > <cell>/probabilities.json`.

### 10.4 Project archive policy

Per the project's "archive, never delete" convention, any superseded
artefacts produced during recovery (e.g. an intermediate evaluation JSON
that was wrong before being fixed in the next commit) must be moved to
`archive/phase3a-recovery-<date>/` rather than deleted.

---

## 11. Unrecoverable cells (out of scope)

The audit's "Unmatched cells" section lists 8 cells with no traceable input
manifest. They cannot be cleaned up by `run_pv.py cleanup` (which requires a
candidate manifest as input). They are listed below for transparency; the
campaign **does NOT attempt to recover them**:

| Cell | Reason unrecoverable |
|---|---|
| `outputs/verifier-t-pilot/T0.5/probabilities.json` | No candidate manifest — was a 2026-Q1 verifier-temperature pilot; inputs may exist but are not in the standard layout |
| `outputs/verifier-t-pilot/T1.0/probabilities.json` | Same as above |
| `outputs/h11/pv-diag-384/verified/pro-image-minimal-verifier/probabilities.json` | No located candidate manifest |
| `outputs/h11/pv-diag-384/verified/pro-text-medium-verifier/probabilities.json` | Same |
| `outputs/h11/pv-diag-384/verified/flash-minimal-image-medium-verifier/probabilities.json` | Same |
| `outputs/h11/pv-diag-384/verified/pro-text-minimal-verifier/probabilities.json` | Same |
| `outputs/h11/pv-diag-384/verified/flash-minimal-text-medium-verifier/probabilities.json` | Same |
| `outputs/h11/pv-diag-384/verified/pro-image-medium-verifier/probabilities.json` | Same |

The audit's note that "none feed the leaderboard or any paper analysis to my
knowledge" should be relied on; if a future analysis attempts to consume any
of these cells, the analyst should treat the cell as "completeness unknown"
and either locate the original candidate manifest or treat the cell as
unusable.

A separate research-hygiene task (NOT part of this campaign) could
investigate whether the verifier-t-pilot inputs can be recovered from
session archives or sapphire backups, allowing a future cleanup. Out of
scope here.

---

## 12. Linked artefacts

- Audit report (cell list, gaps, missing IDs, paths):
  `reports/phase3a-verifier-completeness-audit-2026-05-03.md` (commit
  `adf95dbf`).
- Run-time pattern reference: `planning/paper-writeup-continuity.md`
  § "Session 84 closure" (the four already-completed recoveries).
- Cleanup script: `scripts/run_pv.py` (subcommand `cleanup`, lines
  259–401; argparse spec lines 1116–1176).
- Cost-manifest backup-merge fix: commit `7f05f529`
  (`fix(aggregate-cost): merge pre-recovery verifier-meta backups`).
- Derivative regeneration: `scripts/derive_vote_threshold_results.py`.
- Audit annotation target: `reports/phase3a-verifier-completeness-audit-2026-05-03.md`
  bottom (per § 7.4).
- Template script (this campaign): `planning/run-phase3a-recovery.sh.template`.

---

## 13. Approval gate (before launch)

Before invoking the template script, the operator presents to the user:

- (1) the model(s) being called: `gemini-3-flash-preview` (Tier 1, 2, most
  of 3) + `gemini-3.1-pro-preview` (Tier 3a, 3 cells).
- (2) execution mode: real-time (Flash) — `run_pv.py cleanup` does not
  support batch mode.
- (3) total API calls in the campaign: ~776 verifier calls (one per missing
  candidate, expected single-attempt success per the four already-completed
  recoveries; up to ~2,300 worst case at 3× retry).
- (4) cost estimate: best $1.23 / expected $1.84 / worst $3.70 / hard cap $10.

Approval for Tier 1 does not imply approval for Tier 2 or 3 — the
tier-boundary checkpoints (§ 8.3) re-confirm.
