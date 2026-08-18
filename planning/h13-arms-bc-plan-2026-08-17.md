# H13 arms B + C — preparation plan and phase gate

> **Last revised**: 2026-08-18 (cost-basis note added — all dollar
> figures here are list price; billed is half). See
> [§ Changelog](#changelog).

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

## 6. Validation results (2026-08-17, all four complete)

1. **Dedup uniformity (V1)**: on arm-A `retest-phase2a/brief-text`
   run_1 (340 tiles, 12.5 % overlap), within-pass 20 m dedup removes
   57/973 detections (54 multi-clusters) and moves F1@20 m
   0.5397 → 0.5595 (FP 565 → 509, TP 408 → 407). The duplication
   artefact is material even at arm A, confirming the uniform-dedup
   scoring rule; all three arms will be scored deduped, arm A
   re-scored from committed detections.
2. **Carried config (V2)**: resolved from
   `studies/phase3a-h3-voting-track2.yaml` `carried_forward` —
   `prompts/configs/detect_brief-text.json` ("brief-text"), Phase 2a
   best M/E, T = 0.0, MINIMAL, 512 px. Arm-A committed detections
   exist (3 runs). **Rider**: at T = 0.0 output is near-deterministic
   (E31 verified byte-identical replicates), so flat n = 3 buys
   little — a staged design (run 2 passes, complete n = 3 only if
   they differ) is proposed at the gate.
3. **Tilings (V3)**: trees generated on sapphire
   (`inputs/tiles_512_ov128`, `_ov256`); footprint-majority
   manifests committed — **arm B = 430 tiles, arm C = 999**
   (1,429/pass-set). The plan's geometric estimate (492/1,015)
   over-counted by anchoring at the footprint rather than the raster
   origin; the manifests from real tiles are the pinned figures.
4. **Smoke test (V4)**: 5 calls, `gemini-3-flash-preview`,
   brief-text, T = 0.0 MINIMAL, real-time flex — 5/5 ok, 7,948
   tokens, **$0.0051 = $0.00102/tile**, within 5 % of the scaled
   audited estimate (commit `11f20b2a0`).

**Final priced scenarios (pinned)**: n = 1 → **$1.46**; staged
n = 2(→3) → **$2.92 expected, $4.37 cap**; flat n = 3 → **$4.37**.
Model `gemini-3-flash-preview` pinned; real-time flex; sapphire.

## 7. Audit outcome and run record (2026-08-17/18)

**`/audit-config`: READY TO LAUNCH** (7/7 requirements matched; no
blockers). The transmission check **caught and corrected a
temperature mismatch**: the committed arm-A passes
(`retest-phase2a::brief-text`) all ran at **T = 1.0** (verified in
the passes manifest; the plan's T = 0.0 came from a stale
60-tile-era note in the phase3a YAML), so the run launched at
T = 1.0 to preserve arm comparability — which also made the flat
n = 3 ruling correct (replicates genuinely stochastic). One
WARNING, to disclose in the findings: arm A's passes are March
pipeline vintage, B/C today's (config and instruction file
identical; E66-class orchestration evolution).

**Run record** (PI-approved gate; commits `11f20b2a0` smoke,
`3b4ec3f38` main): 6 passes complete — arm B 1,353/1,362/1,380
detections, arm C 3,034/3,130/3,125; one tile failed (JSON parse,
armB run_1 `K-35-078-1_Lesovo_x2304_y1536`) and was recovered as an
additive pass (`run_1_recovery`, $0.0021); two transient 503s
retried. **Actual spend $5.74 vs the $4.37 gate figure (+31 %),
flagged to the PI, not absorbed** — both figures on the LIST-price basis
(see the basis note at the end of this section; billed was **$2.87 against
a $2.19 gate**, and the +31 % overrun is unaffected because gate and
actual share one basis): the smoke priced T = 0.0 output
volumes (~1.2 detections/tile) and the audit's correction to
T = 1.0 (~3.2/tile) inflated output tokens; per-item cost stayed
under the 2× halt threshold mid-run. **Lesson recorded: re-pin the
smoke after ANY audit-stage parameter change.**

## 8. Scoring chain — complete (2026-08-18, S136)

Executed on sapphire, $0 API. Sequence: per-arm bounds
(`generate_tile_bounds.py --manifest`, 340 / 430 / 999 tiles) →
uniform within-pass 20 m deduplication for ALL arms →
`evaluate_detections.py` at 20 m with `--mcc` on two scopes →
three registered analyses → independent verification.

**One hazard the plan missed, caught in scoring.** The plan assumed
the three arms cover the same ground. They do not: the
footprint-majority manifests give tile unions of 1751 / 1695 /
1847 km² and ground-truth-in-scope counts of 539 / 563 / 565, so
native scoring would have confounded overlap with tile inclusion.
Resolution: a **common A ∩ B ∩ C footprint** (1637.5 km², 538
mounds) carried on the arm-A grid, with detections clipped and
reassigned to it — which also supplies the shared resampling unit the
paired bootstrap needs. Native scoring is retained alongside; the two
agree to under 0.005 F1 (tile-level MCC does *not* survive the scope
change and carries no overlap claim).

**Results** (common scope, 20 m, mean of 3 passes): F1 falls
monotonically with overlap — **A 0.5578, B 0.5198, C 0.4025**. All
three paired contrasts exclude zero at B = 1,000 and B = 10,000
(A−B +0.0380, CI95 [+0.0009, +0.0708] — marginal; A−C +0.1554;
B−C +0.1174). Recall rises (0.7379 → 0.7844 → 0.8717), precision
falls faster (0.4484 → 0.3887 → 0.2616). Deduplication removes
5.9–6.7 % / 15.7–17.9 % / 39.2–40.0 % of raw detections by arm, so
V1's finding generalises and the phase gate's catch was load-bearing;
but after removing every duplicate arm C still carries 1323.7 FPs per
pass against arm A's 488.3, so the precision collapse is a real
property of looking more often, not a scoring artefact. The
registered edge mechanism is confirmed and localised: recall on the
ten mounds arm A could only ever see within 100 m of a tile edge goes
0.2667 → 0.7667 → 0.9333. Cost-efficiency: every additional API
dollar buys negative F1.

**Verification**: `scripts/verify_h13_overlap.py` re-derives counts,
scope, per-arm P/R/F1, cost and the edge subgroup from raw artefacts
along a separate code path (no shared library imports) — **20/20
checks pass**; V1's arm-A gate (973 → 916) reproduces exactly.

**Artefacts**: `results/h13-overlap-2026-08-18/` (findings.md,
analysis JSON, per-arm evaluations on both scopes);
`outputs/h13/scoring/` (deduplicated sets, bounds, dedup summary);
scripts `prepare_h13_scoring.py`, `h13_overlap_analysis.py`,
`verify_h13_overlap.py`. Register: run `h13` with three conditions
and six proposer passes now in the manifests; analysis row
`h13-overlap-2026-08-18` PROPOSED `registered-exploratory` (this
plan's § 7 had proposed `post-hoc`; the disagreement is recorded in
the row for the PI). E75 disposition updated to REMEDIATED.

Note: sapphire holds the (untracked, regenerable) tile trees
`inputs/tiles_512_ov128/` and `_ov256/` — do not clean them.

**COST-BASIS NOTE (added 2026-08-18).** Every dollar figure in §§ 4, 6
and 7 above is **list price**, because that is what the run metadata
recorded: `estimate_cost` priced real-time traffic at full rates until
2026-08-18. Gemini real-time flex carries the same 50 % discount as the
async Batch API, so the amounts actually billed are **half** those quoted
— $5.74 → **$2.87** actual, $4.37 → **$2.19** gate, $1.46 → **$0.73**,
$2.92 → **$1.46**, the smoke $0.0051 → **$0.0026**, and $0.00102/tile →
**$0.00051/tile**.

Note the mixed basis this document carries: `$0.266` per 487-tile MINIMAL
pass, quoted from `pareto_v2.json` in § 4, is ALREADY discounted, so it
was never comparable with the § 6/§ 7 figures beside it. That mismatch is
what made the two internal cost sources appear to disagree by exactly 2×.

No ratio or decision in this plan changes: the +31 % overrun, the
scenario ranking, and the gate verdict all rest on comparisons within one
basis. The writer now records the billed amount with list price and an
explicit `cost_basis` field (defects D13, and D9 for the corresponding
correction to `results/h13-overlap-2026-08-18/findings.md`).

## Changelog

### 2026-08-18 (latest) — Cost-basis note

Every dollar figure in this plan is list price; Gemini real-time flex
bills at half. Actual spend was **$2.87** rather than $5.74, against a
gate of **$2.19**. The document also mixed bases: `pareto_v2.json`'s
$0.266 per pass was
already discounted while the run figures beside it were not — which is
why the two internal cost sources appeared to disagree by exactly 2×. No
ratio, ranking or decision changes.

### 2026-08-18 (later) — Scoring chain complete

Section 8 added. All three registered analyses reported under a
uniform dedup rule and a common evaluation footprint (a hazard the
plan had not anticipated, caught before it could confound the
result). F1 falls monotonically with overlap; the registered edge
mechanism is confirmed but too localised to pay for the precision it
costs. Independent verification 20/20. Register rows and the E75
disposition updated; classification proposed as
`registered-exploratory` rather than the § 7 `post-hoc`, for the PI.

### 2026-08-18 — Audit READY; run complete; overrun recorded

Section 7 added: audit outcome (temperature catch), run record
(6 passes + recovery, $5.74 actual vs $4.37 gate, +31 % flagged),
and the fully-specified $0 scoring chain for the next session.

### 2026-08-17 (later) — Validations complete; price pinned

All four validations executed ($0 + $0.0051 smoke). Pinned: B 430 /
C 999 tiles; $0.00102/tile. V1 grounds the uniform-dedup rule
empirically; V2 surfaces the T = 0.0 determinism rider on the n = 3
ruling. Awaiting the final API gate + `/audit-config`.

### 2026-08-17 — Initial plan (S135)

Phase gate run in-session with the PI present. Two real catches:
arm C's tile count is 2.99× (registered "~2×"), and the evaluation
path has no dedup step (naive scoring would manufacture an
overlap-hurts-precision artefact — dedup must be uniform across
arms, arm A re-scored). API spend not yet approved; design rulings
D-H13-1..4 pending.
