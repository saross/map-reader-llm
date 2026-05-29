# Stage A Verifier-Temperature Failure-Rate Pilot — Report

> **Last revised**: 2026-05-29 (`gold-standard-v2` relocated to `outputs/gs/`). See [§ Changelog](#changelog) for revision history.

**Date:** 2026-04-27
**Author:** Claude Code (Opus 4.7) acting under Shawn's brief
**Compute:** sapphire (192.168.1.150)
**Status:** Pilot complete; outputs uncommitted; awaiting Shawn's decision on Stage B.

## 1. Pilot scope

This is the **Option 1 (re-dispatch)** Stage A pilot. It tests whether the
verifier failure rate observed at T=0.0 (10/607 = 1.65%) is reduced by raising
the verifier sampling temperature. The hypothesis under test is that the
T=0.0 failures are not sampling noise but reflect a deterministic dead-end in
which the verifier exhausts its thinking budget on the same hard candidates
under repeated retries (Observation 281).

Three conditions, all on the same 607 candidates from the canonical 4-of-5
consensus set:

- **T=0.0** — reused from the existing canonical run at
  `outputs/gs/gold-standard-v2/verified-v1/` (commit `a01858e5`,
  `run.meta.json` records git commit `d59798ac`).
- **T=0.5** — fresh run, single pass (k=1).
- **T=1.0** — fresh run, single pass (k=1).

All three use the canonical verifier config (`verify_adversarial-text.json`):
`gemini-3-flash`, `thinking_level: minimal`, no example images.

## 2. Pre-flight findings

| Check | Result |
|---|---|
| `prompts/configs/verify_adversarial-text.json` is canonical v1 | Confirmed: T=0.0, gemini-3-flash, thinking_level minimal, examples=[]. |
| `scripts/run_pv.py verify` accepts `--temperature` override | Confirmed at `scripts/run_pv.py:1078-1081`. |
| 4-of-5 consensus path exists with 607 candidates | Confirmed: `outputs/gs/gold-standard-v2/consensus/consensus-4of5.geojson`. |
| `outputs/gs/gold-standard-v2/crops/` PNGs present | **Re-extracted on sapphire** — directory previously held only `candidate_manifest.json` (PNGs gitignored). 607/607 successful from rasters. |

### Canonical config snapshot (verifier)

```json
{
  "version": "verify_adversarial-text",
  "model": "gemini-3-flash",
  "instruction_file": "verify_adversarial.md",
  "temperature": 0.0,
  "max_output_tokens": 8192,
  "thinking_level": "minimal",
  "examples": []
}
```

## 3. Per-T results

Failure-rate formula (Obs 281):

```text
n_failures = len(consensus_candidates) − len(probabilities['results'])
```

| T   | candidates | success | failures | rate    | Wilson 95% CI       | cost USD |
|-----|------------|---------|----------|---------|---------------------|----------|
| 0.0 |        607 |     597 |       10 | 1.6474% | [0.8973%, 3.0058%] |  $0.8393 |
| 0.5 |        607 |     607 |        0 | 0.0000% | [0.0000%, 0.6289%] |  $0.8518 |
| 1.0 |        607 |     607 |        0 | 0.0000% | [0.0000%, 0.6289%] |  $0.8549 |

The T=0.0 failures are candidate IDs `[253, 292, 302, 304, 321, 359, 397, 408,
435, 520]`. T=0.5 and T=1.0 produced complete result sets (zero missing).

### Cross-check against `finish_reason_counts.error` (the misleading counter)

| T   | success | finish_reason error | retries_total |
|-----|---------|---------------------|---------------|
| 0.0 |    597  | 154                 | (legacy run)  |
| 0.5 |    607  |  20                 | 0             |
| 1.0 |    607  |   7                 | 0             |

This confirms Obs 281: at all three temperatures the runtime sees transient
errors mid-pipeline, but only at T=0.0 does any candidate fail to recover.
T=0.5 had 20 transient errors and all 20 ultimately succeeded; T=1.0 had 7
transient errors and all 7 ultimately succeeded. The original "6%
verifier failure" misreading would have been derived from the `error`
counter, which captures recovered transients, not unrecovered failures.

## 4. Cost actual vs estimate

| Item | Estimated | Actual |
|------|-----------|--------|
| T=0.5 run | $0.84 | $0.8518 |
| T=1.0 run | $0.84 | $0.8549 |
| **Total fresh spend** | **$1.68** | **$1.7067** |

Within 1.6% of estimate; well under the $5 cap.

## 5. Decision-rule output

The brief specified three decision branches:

1. **All three CIs overlap → hypothesis NOT supported, close.**
2. **One T point > 2x another's rate → recommend Stage B (do NOT auto-launch).**
3. **Borderline (overlap but trend visible) → describe and recommend.**

**Result: branches (1) and (2) need re-interpretation because two of the
three rates are exactly zero**, which the >2x rule did not anticipate.

- **CI overlap test:** The T=0.0 Wilson CI is `[0.90%, 3.01%]`; the T=0.5 and
  T=1.0 CIs are `[0.00%, 0.63%]`. **They do not overlap** — the T=0.0 lower
  bound (0.90%) lies above both upper bounds (0.63%). This rules out branch
  (1) "hypothesis not supported".
- **>2x rule:** Strictly inapplicable when `min_rate = 0`; substantively the
  T=0.0 rate is "infinitely larger" than the T>0 rates. The spirit of the
  rule (a real, non-noise difference) is satisfied.

**Verdict: Hypothesis SUPPORTED. The T=0.0 failures are not sampling noise.
A non-zero verifier temperature eliminates the deterministic
thinking-budget-exhaustion failure mode within this 607-candidate pilot.**

## 6. Recommendation

The pilot's stated purpose was to decide whether to invest in Stage B (a
larger-N replication and/or analysis of which candidates fail at T=0.0).
Three options for Shawn:

1. **Close — adopt T>0 for the verifier going forward.** The simplest
   interpretation is that T=0.0 has a known, reproducible failure mode that a
   small temperature change cures. Adopting T=0.5 (or higher) costs essentially
   nothing per run and removes the need for cleanup passes on stragglers.
   Open question: **does T>0 affect verifier accuracy?** The pilot did not
   evaluate F1/MCC, only completion. Accuracy comparison would need ground-truth
   re-evaluation against the existing consensus labels.
2. **Run Stage B for accuracy verification.** Re-evaluate T=0.5 and T=1.0
   probabilities against the gold standard, comparing F1/MCC at the standard
   threshold sweep. This is analysis-only (no fresh API calls), low-cost, and
   is the natural follow-up if (1) is on the table.
3. **Re-design.** If the pilot result is suspicious, run T=0.0 fresh on the
   same crops to confirm the 10 failures replicate (and that they are the
   *same* candidate IDs). This costs ~$0.84.

**My recommendation: option (2)** — do the accuracy comparison, because the
operational decision (raise temperature) is only acceptable if accuracy holds.
Option (1) without accuracy verification would be a process improvement that
silently costs F1.

**Do not auto-launch.** Awaiting Shawn's direction.

## 7. Uncommitted artefacts

The brief specified leaving outputs and report uncommitted. The following
paths are uncommitted on amd-tower (and on sapphire for the run outputs):

- `outputs/verifier-t-pilot/T0.5/{probabilities.json, run.meta.json, run.log}` — sapphire + amd-tower
- `outputs/verifier-t-pilot/T1.0/{probabilities.json, run.meta.json, run.log}` — sapphire + amd-tower
- `outputs/gs/gold-standard-v2/crops/candidate_*.png` — sapphire only (gitignored; can be re-extracted)
- `results/verifier-t-pilot/stage-a-report.md` — amd-tower (this file)
- `results/verifier-t-pilot/per-t-stats.json` — amd-tower
- `scripts/analyse_verifier_t_pilot.py` — amd-tower

The T=0.0 baseline at `outputs/gs/gold-standard-v2/verified-v1/` was not
modified, moved, or overwritten.

## Changelog

### 2026-05-29 — gold-standard-v2 relocated to outputs/gs/

**Refresh trigger**: H11 reorganisation — the `gold-standard-v2` run was moved
out of `outputs/h11/` to the new `outputs/gs/` umbrella (relocation landed in
commit `c5983adb`). Its `run_id` slug is unchanged (`gold-standard-v2`);
only the directory path moved.

**What changed**: every `outputs/h11/gold-standard-v2/…` path reference in this
document was repointed to `outputs/gs/gold-standard-v2/…`.

**What did NOT change**: no numerical results, tables, rankings, or findings —
this is a pure path relocation.

### 2026-04-27 — Original publication

Document first authored on 2026-04-27; see git history for substantive content.
This banner and changelog were added on 2026-05-29 (the first Revision-Policy
stub for this document) as part of the H11 reorganisation.
