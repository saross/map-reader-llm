# Verifier-stage refresh on the recovered candidate sets — 2026-09-08 (S150)

> **Last revised**: 2026-09-08 (later still, S151 — run complete, US$8.73
> at list; § 5 after-run steps done). Controls one API-spending block; the
> PI approved a ceiling of **US$20** on 2026-09-08 ("set up the run to
> clear the uncited verifier stages, spend up to $20"). See
> [§ Changelog](#changelog).

## 1. What and why

The recovery-consistency audit
(`reports/recovery-consistency-audit-2026-09-08.md` § 3) found three
text-only adversarial verifier stages whose candidate sets were built
from passes the E71 recovery (`99ae28ec4`, 2026-07-30) later rewrote.
None is cited by a registered condition or analysis; two are inventory
rows in `verifier_passes`, one (e47) was never registered. (Corrected
S151: this card originally called the e47 stage "an abandoned attempt
(57 of 4,358 candidates verified, crops gone)". That misread a
cleanup-overwritten `run.meta.json`: the stage's `probabilities.json`
holds 4,358 of 4,358 candidates with a probability — verified 2026-04-09
(`52b0215a6`) with a 57-crop gap that the 2026-05-06 cleanup closed
(`6683952ac`), whose 57-crop meta overwrote the original. Only the crop
PNGs are absent locally, as for every stage.) This block re-runs all three on
the candidate sets rebuilt today from the recovered passes, into NEW
dated stage directories beside the originals (archive, never delete: the
originals stay as the pre-recovery record).

| stage (new directory) | candidates (rebuilt 2026-09-08) | n | old stage |
|---|---|---:|---|
| `outputs/h11/pv-diag-384/flash-high-image-n5/image-t0.0/verified-v1-n10-recovery-2026-09-08/` | `…/image-t0.0/consensus/consensus_t1.geojson` | 889 | `verified-v1-n10` (802 candidates, pre-recovery; `c6b5e6b10`) |
| `outputs/h11/pv-diag-384/flash-high-text-n5/text-t0.0/verified-v1-n3-recovery-2026-09-08/` | `…/text-t0.0/consensus/consensus_t1.geojson` | 1,319 | `verified-v1-n3` (1,256; `857d5f714`) |
| `outputs/h11/e47-propose-brief/verified/flash-high-text-1of5-recovery-2026-09-08/` | `…/consensus/flash-high-text-1of5-recovery-2026-09-08.geojson` (a copy of the pool's rebuilt `consensus_t1`) | 4,149 | `verified/flash-high-text-1of5` (4,358 verified, complete after the 2026-05-06 cleanup; never registered or swept — corrected S151, see § 1) |

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

## 6. Pre-launch audit (`/audit-config`, 2026-09-08)

```text
=== PRE-LAUNCH AUDIT: verifier-stage refresh (reproduction of three stages' configuration) ===

1. REQUIREMENTS (14; source = the originals' run.meta.json unless stated):
   1 config version verify_adversarial-text (HARD)  2 model gemini-3-flash-preview
   (HARD; pricing_used.model on all three originals)  3 thinking minimal (HARD)
   4 temperature 0.0 (HARD)  5 instruction verify_adversarial.md, sha256 2518d529…
   (HARD)  6 example_count 0, text-only labels (HARD)  7 max_output_tokens 8192
   8 one iteration per candidate (HARD)  9 crop padding 75, rasters inputs/rasters
   (HARD; candidate_manifest.json)  10 candidates = the pool's vote>=1 consensus on
   the recovered passes (HARD; the manipulated variable)  11 sweep on
   full_evaluation_bounds (487), buffers 20/30/40/50, GT mounds-reference (HARD)
   12 real-time, flex (cost-only)  13 new stage dirs, originals untouched (HARD;
   archive policy)  14 spend <= US$20 (HARD; PI 2026-09-08).
   Preregistration: H2 Condition B "crop candidate regions, verify with focused
   prompt" (osf/preregistration.md:451ff); E56 (verifier thresholds in-sample);
   E80 (merge_passes-built candidates are within-pass deduplicated).

2. CONFIG DIFF (3 stages): identical — verifier config, model pin, thinking, T,
   instruction, padding, bounds, buffers, workers, tier. Differ — candidate file,
   stage directory, expected count (all EXPECTED). Confounds: NONE.

3. TRANSMISSION: image flag n/a (text-only verifier; originals record
   include_example_images True / example_count 0, same code path) PASS; temperature
   shadowed — no CLI override, config 0.0 PASS; thinking — config minimal, no
   override PASS; model drift — pinned gemini-3-flash-preview on verify and cleanup
   PASS; tile size n/a; candidate set — dry-run 889/1,319/4,149, 0 failed PASS;
   instruction file — sha256 equals the recorded hash PASS; example paths — list
   empty PASS; example dimensions n/a; agent model n/a. Blockers: NONE.

4. ALIGNMENT: matches 14; deliberate deviations 0; undocumented deviations 0.

5. DRY-RUN: PASS (extract, all three). `verify --dry-run` exists for batch mode
   only — real-time cannot be dry-run (WARNING).

6. EVALUATION SCOPE: PASS — 487-tile era-2 frame, curator reference; no
   calibration/holdout split applies to these GS inventory stages.

7. COMPLETENESS: not verifiable before launch — the flex tier (not recorded in the
   originals' metas; cost-only), the sweep's vote-threshold default (inherits the
   script's default as the originals did).

BLOCKERS: NONE.   WARNINGS: real-time verify has no dry-run; flex tier unrecorded.
OVERALL: READY TO LAUNCH
```

## Changelog

### 2026-09-08 (later still, S151) — Run complete; § 5 after-run steps done

- **Run**: all three stages complete (889 / 1,319 / 4,149 candidates with a
  probability; 0 failed, 3 retries; verify calls 06:56–07:22 UTC), committed
  from sapphire at `43516df9a`. **Cost as recorded**: US$1.24 + US$1.82 +
  US$5.67 = **US$8.73** — `cost_basis: "list"` in each `run.meta.json`
  (11.39 M input / 1.01 M output tokens); the flex tier bills at half of
  list, so the invoice is expected at ≈ US$4.37. Against the § 3 estimate of
  ≈ US$8.9 and the US$20 ceiling.
- **§ 5.1** rows registered by `scripts/register_verifier_stage_refresh.py`
  (idempotent; tier-1 tests) — `34fc71b9f`; passes manifest 1,279 → 1,282,
  `verify_run_conditions` unchanged (22 pass / 19 partial / 0 fail).
- **§ 5.2** comparison in `reports/recovery-consistency-audit-2026-09-08.md`
  § 6.1 — `d79ab6957`. Text stage +0.027 F1 at 20 m, unchanged operating
  point. The image stage's committed April sweep turned out to be a
  342-of-802 partial-verification artefact (sweep older than its own
  probabilities; the 2026-05-06 cleanup never re-swept), so it was re-swept
  complete at $0 (sapphire; preserved under
  `results/recovery-reeval-2026-09-08/pv-diag-384/`): 0.6589 → 0.6872, a
  recovery effect of the text stage's size. e47: first usable PV cell,
  0.8735 at 20 m.
- **§ 5.3** E71 rider addendum (same commit).
- **Regenerated**: uplift supplement and plateau doc — `001a98c97` (the
  refreshed stages add no condition row; the rebuild swept up the S150-b
  image 3-of-3 row registered after the previous build, 437 → 438).
- **PR #12 merged** (`459556ba4`) with the analyses manifests regenerated
  from the merged sources (63 analyses) and the hypothesis-outcome table
  regenerated (H13 gains `student-baseline-r2` as related post-hoc).
- **Correction (S151, on the PI's question about the unregistered e47
  directories)**: § 1's "abandoned attempt (57 of 4,358 verified, crops
  gone)" was wrong — the April stage is complete at 4,358 (the 57 is the
  2026-05-06 cleanup whose meta overwrote the original); it was never
  swept or registered. Fixed in § 1, the audit § 6.1, the E71 addendum,
  and the register note. `verified/text-baseline` (the same verifier on
  the N=1 propose_brief pass, 1,180 candidates, 2026-04-08, `42f07bc3b`)
  is the other unregistered directory the generator's draft proposes.
- **PI rulings executed (S151, 2026-09-08)**: (1) both April e47 directories
  registered as inventory rows (`scripts/register_e47_april_verifier_stages.py`,
  `952f30a22`; passes manifest 1,282 → 1,284); (2) the sweep-staleness
  class surveyed corpus-wide (`reports/sweep-staleness-survey-2026-09-08.md`,
  `107f5d06c`: 5 stale of 265 stages, all the one May cleanup's pv-diag
  image stages, none cited) and the four small ones re-swept complete
  (`88232c536`; gap-11 stage 0.7460 → 0.7475 at 20 m, gap-1 stages
  identical); (3) the April e47 stage swept for the first time
  (`proposer_votes` → `vote_count`, exact): 0.7953 at 20 m against the
  refreshed 0.8735 — NOT a like-for-like (different candidate-set
  construction: 4,358 vs 4,149 clusters, more at every vote tier; the April
  e47 consensus is irreproducible at any vintage), so the refreshed stage
  remains the pool's only sweep on a reproducible candidate set. Audit
  § 6.1 carries all of it.

### 2026-09-08 (later) — Audit READY; launched on sapphire

`scripts/run_verifier_stage_refresh.sh` under `setsid -f`, log
`/tmp/vsr.log` on sapphire.

### 2026-09-08 — Original publication

Written after the PI's approval of the US$20 ceiling; dry-runs passed.
