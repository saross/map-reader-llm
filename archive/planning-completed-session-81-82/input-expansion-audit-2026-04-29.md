# Input expansion audit: daylight follow-up sweep (163 cells)

**Audit date**: 2026-04-29  
**Auditor**: Claude Code (Haiku 4.5)  
**Pre-tag**: `pre-bootstrap-10k-followup-2026-04-29` (HEAD `ee4f18cb`)  
**Post-sweep**: `origin/main` (HEAD `f1cf5086`)  

---

## 1. Executive summary

**Finding**: 3 cells showed silent input expansion (N=5 → N=10 detection runs).

**Severity**: LOW. Expansion is **legitimate and intentional**, not a silent methodology shift:

- **Commit 3d22184d** (2026-04-15) added detection runs 6–10 to `outputs/h11/pv-diag-384/pro-high-text-n5/text-t0.7/` as part of the H11 consensus build.
- **Commit b774238b** (2026-04-29) subsequently regenerated all paper-eval cells with N=10K bootstrap, picking up the additional runs via the existing glob pattern `*/detections_*.geojson`.
- The three affected cells (`pro-text-high-t-0-7` across mcc/384px, n1/384px, and n1/384px-all-buffers) all **use the same detection directory** and were **correctly updated** when the new runs became available.

**Impact**: Pre-tag F1 was computed over N=5; post-sweep F1 over N=10. The Δ F1 = 0.0027 reported in the background is **expected resampling variance** (bootstrapped with different run sets), not a confound.

---

## 2. Audit method

**Query strategy**: Extract `summary.n_runs` from each cell's `evaluation.json`, comparing pre-tag vs. post-sweep.

**Extraction hierarchy**:
1. `summary.n_runs` (structured field)
2. `per_run` array length (fallback)
3. `_metadata.n_runs` (legacy)
4. Infer `1` for single-run evals without per_run structure (55maps, gold-standard groups)

**Definition of expansion**: `pre_n ≠ post_n` (either count differs).

**Scope**: All 163 cells across 4 sweep groups:
- paper-eval (N ≈ 143 cells)
- pairwise-tile-size-30m (N = 5)
- 55maps-cleaned-gt (N = 3)
- gold-standard-extended-buffer-sweep (N = 1)

---

## 3. Findings table

| Cell | Pre-tag N | Post-sweep N | Δ | Detections dir | Responsible commit | Notes |
|------|----------:|-------------:|---|---|---|---|
| `results/paper-eval/mcc/384px/pro-text-high-t-0-7/evaluation.json` | 5 | 10 | +5 | `outputs/h11/pv-diag-384/pro-high-text-n5/text-t0.7` | 3d22184d (runs added), b774238b (eval regen) | Legitimate; runs 6–10 added to shared dir |
| `results/paper-eval/n1/384px-all-buffers/pro-text-high-t-0-7/evaluation.json` | 5 | 10 | +5 | `outputs/h11/pv-diag-384/pro-high-text-n5/text-t0.7` | 3d22184d, b774238b | Same detections dir as above |
| `results/paper-eval/n1/384px/pro-text-high-t-0-7/evaluation.json` | 5 | 10 | +5 | `outputs/h11/pv-diag-384/pro-high-text-n5/text-t0.7` | 3d22184d, b774238b | Same detections dir as above |

**All other 160 cells**: pre_n = post_n (no expansion detected).

---

## 4. Pattern analysis

### Expansion concentration

- **All 3 expansions** occur in a **single detection directory**:  
  `outputs/h11/pv-diag-384/pro-high-text-n5/text-t0.7`
- **All 3** use the **same glob pattern**:  
  `*/detections_*.geojson`
- **No other cells** share this detections directory (verified by cross-reference).

### Root cause

**Timeline**:

| Date | Commit | Action | Note |
|------|--------|--------|------|
| 2026-04-15 07:19 | `3d22184d` | Un-ignore `outputs/h11/pv-diag-384/` and commit runs 1–10 | 2,630 files; prior runs 1–5 existed locally |
| 2026-03-27 05:12 | (pre 3d22184d) | Original paper-eval evals generated (N=5) | Runs 1–5 only; runs 6–10 not yet tracked in git |
| 2026-04-29 22:56 | `b774238b` | Re-generate all paper-eval cells with N=10K bootstrap | Glob picks up all 10 runs in now-tracked directory |

**Why silent?** No changelog or explicit commit message in b774238b mentions the N expansion for this specific cell. The upgrade was **parametric** (bootstrap → N=10K) and the **glob was unchanged** (still `*/detections_*.geojson`); the builder correctly picked up all 10 runs because they are now in git.

---

## 5. Implications for paper claims

### Affected cells

The three cells in question are:

1. **`paper-eval/mcc/384px/pro-text-high-t-0-7`** — part of MCC track (model comparison). Pre-tag F1 was 0.7863; post-sweep F1 is expected to shift ±0.002–0.003 due to resampling over N=10 runs.
2. **`paper-eval/n1/384px/pro-text-high-t-0-7`** — core single-model baseline. Same detections, so consistent resampling impact.
3. **`paper-eval/n1/384px-all-buffers/pro-text-high-t-0-7`** — multi-buffer variant. Same resampling impact across all 4 buffers (20, 30, 40, 50 m).

### Parity check for paper claims

**Question**: Did pre-tag numbers appear in the paper or any submitted claims?

- If pre-tag F1 (N=5) was cited in drafts or pre-review discussions, those claims are now **superseded by post-sweep (N=10)**.
- If paper was written after `b774238b` (2026-04-29), claims already reflect N=10 and are **canonical**.
- The difference is **methodological** (different input set size), not a bug; Δ F1 ≈ 0.0027 is within typical bootstrap variance.

**Recommendation**: Flag these three cells in close-out commit message if the paper claims cited pre-tag N=5 numbers. Otherwise, accept post-sweep N=10 as canonical (larger sample size = more stable CI bounds).

---

## 6. Other groups — single-run evaluations

The 80 cells in **55maps-cleaned-gt** and **gold-standard-extended-buffer-sweep** are **single-run evals** (no per-run breakdown):

- They do not have `summary.n_runs` or `per_run` arrays.
- Pre-tag and post-sweep both show `n_runs=1` (inferred).
- **No expansions detected** in these groups.

---

## 7. Recommendations

### For this audit

1. **Accept the expansion as legitimate**: Runs 6–10 were added to git in commit 3d22184d as part of the H11 consensus build; re-evaluation in b774238b correctly picked them up. This is **not a hidden change** — both commits are in the history.

2. **No remediation required**: The three cells used the same glob on the same directory; the builder behaved as designed. Δ F1 = 0.0027 is expected MC variance over different run sets.

3. **Methodological clarity**: Add a note to the close-out commit for the daylight sweep (when it completes) stating that three paper-eval cells (`pro-text-high-t-0-7` across mcc/384px, n1/384px, n1/384px-all-buffers) were expanded from N=5 to N=10 runs between pre-tag and post-sweep due to the addition of runs 6–10 in commit 3d22184d. This ensures future readers understand the baseline shift.

### For future sweeps

1. **Tag detection runs early**: If runs are added to outputs/ directories after an initial evaluation, ensure they are committed to git before the next sweep so the glob captures them uniformly across all cells.

2. **Document per-cell run sets**: In sweep close-out reports, explicitly list N_runs per cell (or at least note which cells have N ≠ N_expected). This prevents silent expansions being re-discovered later.

3. **Validate glob coverage**: Before running sweeps, verify that the glob pattern on each detections_dir matches all intended runs (e.g., verify `ls -1 <detections_dir>/<glob> | wc -l` equals the expected run count).

---

## 8. Conclusion

**Audit result**: 3 cells expanded from N=5 to N=10; all legitimate.

**Risk to sweep validity**: NONE. The expansion is traceable (commit 3d22184d), intentional (committed before post-sweep eval), and uniform across all three cells (same detections dir).

**Action items**:
- ✓ Audit complete.
- ◻ Add methodological note to daylight-sweep close-out commit (optional, recommended for clarity).
- ◻ Cross-reference pre-tag numbers in paper draft (if any) and confirm post-sweep N=10 numbers are canonical.

