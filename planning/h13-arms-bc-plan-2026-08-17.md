# H13 arms B + C — preparation plan and phase gate

> **Last revised**: 2026-08-17 (initial plan; phase gate run; API
> spend NOT yet approved). See [§ Changelog](#changelog).

**Ruling being executed**: S134 walk Group E — "H13: run arms B + C,
gated behind a re-pricing check." E75 discloses the registered
three-arm contrast as silently dropped; this plan prepares the run.
Gate chain: phase-gate (this document, § 2) → design rulings (PI) →
$0 validations → `/audit-config` → API-gate approval (model, mode,
call count, cost) → launch.

## 1. Registered specification (verified at source this session)

`docs/methodology/preregistration/osf/preregistration.md:1014-1048`:
three 512 px overlap arms — A = 64 px / stride 448 (12.5 %),
B = 128 px / 384 (25 %), C = 256 px / 256 (50 %); implementation
"uses optimal configuration from Stages 1-2", spatial deduplication
applied, GT matching robust to multi-tile detections; three
registered analyses — F1 as a function of overlap, cost-efficiency
per additional API dollar, edge-detection analysis. Registered cost
multipliers "~1.4× / ~2×".

## 2. Phase gate

| # | Assumption | Source | Status | Validation cost | If wrong… |
|---|---|---|---|---|---|
| 1 | Arm tile counts: B = 492, C = 1,015 over the Era-1 footprint (1.45× / **2.99×** — the registered "~2×" for C underestimated; overlap compounds in both axes) | Geometric count over `full_evaluation_bounds.geojson`, this session; the stride-448 grid reproduces the 340-tile corpus exactly | Validated (pinned exactly when the tiler runs, $0) | — | Cost estimate scales; caught pre-spend |
| 2 | "Optimal configuration from Stages 1-2" is identifiable | Era-1 single-pass board: Tier 1 is a **20-cell tie** (F1 0.583–0.631) — the GS instrument never resolved a single-pass optimum | **Under-powered as an identification**; non-load-bearing for the within-config overlap contrast if one config is held constant across arms | $0 — read the Stage-2 carry-forward record in the decisions log at audit | A different Tier-1 config might show different overlap sensitivity; result is framed "for the carried config", per the plateau rule (no peak-picking) |
| 3 | Arm A can be reused at $0 | Committed Era-1 passes at the chosen config | **Superseded by #5**: arm A must be **re-scored** (not reused) so one dedup rule covers all arms; committed *detections* are reused, committed *F1s* are not | $0 (re-score from committed geojsons) | — |
| 4 | Pricing: ~$0.00097/tile (512 px, MINIMAL, flex) — audited 384 px rate × (512/384)² pixel scaling | `pareto_v2.json` cost model ($0.266 / 487-tile MIN pass); Era-1 passes were free-tier so no historical 512 px costs exist | Under-powered (±50 % band) | **Smoke test, 5 tiles, cents** — pins per-item cost before launch | Overrun on a ~$5 run; trivial but the pin is ~free |
| 5 | Scoring handles overlapping tiles | `evaluate_detections.py` has **no dedup step**; Hungarian matching per map converts cross-tile duplicates into false positives | **Untested and load-bearing — caught at this gate.** Naive scoring would manufacture "overlap hurts precision" | $0 — route every arm's per-pass detections through the existing `merge_passes` within-pass 20 m dedup before scoring; verify on existing arm-A data | The headline H13 result would be an artefact of the scorer, not the data |
| 6 | The 512 px tiler still runs locally (tile trees are machine-local/regenerable) | S114 sync audit | Untested; $0 at tiling time | $0 | Fix locally; no spend at risk |
| 7 | Model pinned explicitly (`gemini-3-flash-preview`) in the study YAML and stamped in artefacts | 2026-07-24 provenance standard | Design requirement | — | Provenance mislabelling |
| 8 | Flex real-time ≈ batch pricing on Gemini 3 | pareto cost-model note | Validated (audited note) | — | Mode choice is cost-neutral; PI chooses mode |
| 9 | The three registered analyses are $0 post-hoc once detections exist | F1-per-arm (standard eval + dedup), cost-efficiency (audited costs), edge-detection (new distance-to-boundary script) | Validated by construction | — | — |

**Recommendation: validate first, then proceed.** All validations are
$0 plus a cents-level smoke test:

1. Dedup-uniformity check: re-score one existing arm-A pass with and
   without the `merge_passes` dedup step; confirm the pipeline and
   quantify the arm-A duplication baseline ($0, sapphire).
2. Resolve the Stage-2 carried configuration from the decisions log;
   confirm committed arm-A detections exist for it (n ≥ 3) with
   feature-count crosschecks ($0).
3. Generate arm B/C tilings locally; pin exact tile counts ($0).
4. Smoke test 5 tiles at the chosen config (cents) → pin per-item
   cost → final priced API gate.

## 3. Design decisions for the PI (pre-audit)

- **D-H13-1 — configuration**: recommend the Stage-2 carried
  configuration (registered intent; resolved from the decisions log),
  MINIMAL thinking, text track, held constant across arms. The
  result is then "overlap effect for the carried configuration".
- **D-H13-2 — replicates**: recommend n = 3 per arm (matches the
  Era-1 replicate convention; supports delta CIs). n = 1 halves cost
  but gives no within-arm variance.
- **D-H13-3 — execution mode**: recommend real-time flex on
  sapphire/zbook-class pacing (recent-practice default); Google
  async Batch API is the equal-cost alternative.
- **D-H13-4 — arm A**: re-scored from committed detections under the
  uniform dedup rule ($0); no arm-A API spend unless validation 2
  finds no suitable committed cell (contingency: +340 tiles × n).

## 4. Re-priced cost (to be pinned by the smoke test)

Basis: audited flex rates (token-load audit 2026-06-12, via
`pareto_v2.json`), 384 px → 512 px scaled by pixel ratio 1.778;
±50 % band until the smoke test.

| Scenario | Calls | Estimate | Band |
|---|---:|---:|---|
| **B + C, MINIMAL text, n = 3 (REC)** | (492 + 1,015) × 3 = 4,521 | **≈ $4.4** | $2.2–6.6 |
| B + C, n = 1 | 1,507 | ≈ $1.5 | $0.7–2.2 |
| Contingency: arm A re-run (only if validation 2 fails) | + 1,020 | + ≈ $1.0 | — |
| Smoke test | 5–15 | cents | — |

The E75-era "~$6–8" pre-lodgement figure is superseded by this
computation: arm C needs 3× tiles (not 2×), but MINIMAL flex pricing
is lower than the drafters assumed; the recommended scenario lands
at ≈ $4.4 within band.

## 5. Stop states

Per the S135 block conventions: reproduction/feature-count gate
failures halt before spend; the smoke test's per-item cost exceeding
2× the estimate halts for re-approval; any tiling anomaly (counts
off the pinned values) halts; no silent mode or model changes.

## Changelog

### 2026-08-17 — Initial plan (S135)

Phase gate run in-session with the PI present. Two real catches:
arm C's tile count is 2.99× (registered "~2×"), and the evaluation
path has no dedup step (naive scoring would manufacture an
overlap-hurts-precision artefact — dedup must be uniform across
arms, arm A re-scored). API spend not yet approved; design rulings
D-H13-1..4 pending.
