# Verifier-stage refresh on the recovered candidate sets — 2026-09-08 (S150)

> **Last revised**: 2026-09-08 (original publication). Controls one
> API-spending block; the PI approved a ceiling of **US$20** on
> 2026-09-08 ("set up the run to clear the uncited verifier stages, spend
> up to $20"). See [§ Changelog](#changelog).

## 1. What and why

The recovery-consistency audit
(`reports/recovery-consistency-audit-2026-09-08.md` § 3) found three
text-only adversarial verifier stages whose candidate sets were built
from passes the E71 recovery (`99ae28ec4`, 2026-07-30) later rewrote.
None is cited by a registered condition or analysis; two are inventory
rows in `verifier_passes`, one (e47) is an abandoned attempt (57 of
4,358 candidates verified, crops gone). This block re-runs all three on
the candidate sets rebuilt today from the recovered passes, into NEW
dated stage directories beside the originals (archive, never delete: the
originals stay as the pre-recovery record).

| stage (new directory) | candidates (rebuilt 2026-09-08) | n | old stage |
|---|---|---:|---|
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10-recovery-2026-09-08/` | `…/image-t0.0/consensus/consensus_t1.geojson` | 889 | `verified-v1-n10` (802 candidates, pre-recovery; `c6b5e6b10`) |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/verified-v1-n3-recovery-2026-09-08/` | `…/text-t0.0/consensus/consensus_t1.geojson` | 1,319 | `verified-v1-n3` (1,256; `857d5f714`) |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5-recovery-2026-09-08/` | `…/consensus/flash-high-text-1of5-recovery-2026-09-08.geojson` (a copy of the pool's rebuilt `consensus_t1`) | 4,149 | `verified/flash-high-text-1of5` (57 of 4,358 verified; abandoned) |

## 2. Recipe (= `scripts/run_verifier_matrix.sh`, the stages' original pipeline)

Driver: `scripts/run_verifier_stage_refresh.sh` (sapphire, `setsid -f`).
Per stage: `run_pv.py extract --padding 75` → `run_pv.py verify
--verifier-config prompts/configs/verify_adversarial-text.json --mode
realtime --workers 20 --service-tier flex` (Gemini 3 Flash, thinking
minimal, T 0.0, one iteration per candidate — the stages' recorded
configuration, `run.meta.json`; the model is pinned on the command line as
`gemini-3-flash-preview` because the config's `gemini-3-flash` alias is
resolved against the live model list) → completeness (every candidate carries
a probability; one `cleanup` pass if not) → `sweep_f1_greedy_pv.py`
at 20/30/40/50 m on `full_evaluation_bounds`.

## 3. Cost and calls (the API-call review gate)

- Model: `gemini-3-flash-preview`, real-time API, flex tier.
- Calls: 889 + 1,319 + 4,149 = **6,357** verifier calls (+ retries), one
  crop each; no proposer calls.
- Estimate: the two original stages cost US$0.649 / 460 and US$1.735 /
  1,267 crops = **US$0.0014 per crop** → **≈ US$8.9**; ceiling US$20
  enforced by the driver (cumulative `cost_estimate.total_cost_usd`).
- Wall clock: ≈ 6,400 calls at 20 workers, flex — of the order of an
  hour.

## 4. Gates and stop states

- `run_pv.py extract --dry-run` on all three candidate files: 889 /
  1,319 / 4,149, 0 failed (sapphire, 2026-09-08).
- `/audit-config` on this card + driver: recorded in § Changelog.
- Stop: a candidate count that disagrees with this card; extract or
  sweep failure; a stage still incomplete after one cleanup pass;
  cumulative cost > US$20. On any stop the finished stages stay on disk
  (each step is cached and resumable).

## 5. After the run ($0)

1. Register the three new stage directories as `verifier_passes`
   inventory rows beside the old ones (`results/run-conditions.json`;
   e47 gains its first), regenerate the manifests.
2. Compare each new `sweep_2d.json` to the old stage's (best F1 at 20 m
   and its operating point) in the audit report § 6; preserve and
   compare, do not swap.
3. E71 rider addendum: the three stages refreshed; costs as billed.

No registered condition or analysis cites these stages, so nothing in
the paper moves; the value is corpus consistency and a usable e47 PV
cell.

## Changelog

### 2026-09-08 — Original publication

Written after the PI's approval of the US$20 ceiling; dry-runs passed.
