# SUPERSEDED 2026-04-24

**Reason**: Run completed 2026-04-18; this configs/ copy is a duplicate.

**See**: `configs/run-configs/55maps_text_min_generalisation_post_run_report.md` (primary) and the outputs/ sibling

This document is preserved for audit / historical reference. Its original content follows below.

---

## Pre-Launch Audit — 55-Map Text MIN Generalisation Run

**Audit date**: 2026-04-18
**Auditor**: Claude Code via `/audit-config` skill (+ `/audit` for YAML + MD)
**Target run**: `configs/run-configs/55maps_text_min_generalisation.yaml`
**Launcher**: `scripts/run_generalisation.py` (v1.0.0)
**Expected cost**: ~$65 at Gemini 3 Flash Flex tier
**Purpose**: Paired MIN-vs-HIGH comparison on the 55-map text
pipeline. Tests whether HIGH thinking's ~$10 cost premium at K=5 + PV
is statistically significant — anchored on the 2026-04-10 HIGH text
run (F1 = 0.790 measured, 0.814 Dawid-Skene-corrected).

This file is a **pre-launch audit artefact** kept alongside the run
config so reviewers and replicators can see exactly which checks were
performed before committing API budget.

## Sources of truth consulted

1. `docs/methodology/preregistration/osf/preregistration.md` — canonical
   protocol.
2. `docs/methodology/preregistration/protocol-errata.md` — documented
   deviations (errata override preregistration).
3. `docs/methodology/preregistration/decisions-log.md` — decisions
   constraining generalisation-run protocol.
4. The filesystem — actual JSON / YAML / GeoJSON values override claims
   in `description` fields.
5. `configs/run-configs/55maps_text_generalisation_retrospective.yaml`
   — the HIGH baseline configuration this run is paired against.

## 1. Preregistration requirements extracted (13)

| # | Requirement | Source | Stage |
|--:|---|---|---|
| 1 | Proposer config: `detect_brief-text.json` (text-track carry-forward) | Decision 17 (text-track uses Scale-8 metadata); E51 text-track text library | proposer |
| 2 | Proposer `include_example_images`: false (text-only prompts) | Decision 17 | proposer |
| 3 | Proposer thinking: **minimal** (the factor under test; pre-reg Stage 1 baseline) | Preregistration §9.1; compared against HIGH per E49 production carry-forward | proposer |
| 4 | Proposer temperature: 0.7 | Errata E49, E51 | proposer |
| 5 | K (consensus passes): 5 | Errata E51 (overrides pre-reg K=10) | proposer |
| 6 | Tile size: 384 px | Errata E51, E53 | proposer |
| 7 | Consensus algorithm: greedy-ball 20 m | Decision 26; pre-reg §8.5 | consensus |
| 8 | Vote threshold: 4 (of 5) — text-track sweep optimum, distinct from image-track 3/5 | 2026-04-10 run consensus-4of5.geojson; text-track sweep | consensus |
| 9 | Verifier: `verify_adversarial-text.json` v1 | Errata E37, E39 | verifier |
| 10 | Verifier: minimal thinking / T=0.0 / N=1 single-pass | Decision 24 | verifier |
| 11 | Verifier probability threshold: 0.15 | Paired-with-HIGH operating point; v1 threshold sweep | verifier |
| 12 | Evaluation primary tolerance: 20 m primary; curve over 20/30/40/50 m | Preregistration §4.1.1; E7 added 40 m; E47 reverts primary to 20 m | evaluate |
| 13 | Evaluation: 1000-iter bootstrap, tile-level, seed 42 | Decision 10; E52 | evaluate |
| 14 | Evaluation scope disjoint from calibration (0 overlap) | Preregistration §2 (holdout principle) | evaluate |
| 15 | Crop padding 75 px (→ 150×150 crops) | Decision 23 | extract |

(15 items actually — added scope disjointness + crop padding to the
checklist compared to the initial 13-item summary in the main audit.)

## 2. Configuration pairwise diff (vs retrospective HIGH baseline)

Single-factor paired design. Every parameter that affects the API
payload is held identical to the retrospective
`55maps_text_generalisation_retrospective.yaml`; only `thinking_level`
is changed (plus one orchestration-only difference, flagged below).

| Field | HIGH (retrospective) | MIN (this run) | Classification |
|-------|:--------------------:|:--------------:|:--------------:|
| run_name | `55maps-text-generalisation` | `55maps-text-min-generalisation` | Output segregation (expected) |
| proposer.config | `detect_brief-text.json` | `detect_brief-text.json` | Controlled |
| proposer.model | `gemini-3-flash` | same | Controlled |
| proposer.instruction_file | `detect_brief-text.md` | same | Controlled |
| proposer.include_example_images | `false` | `false` | Controlled (text-only) |
| proposer.temperature | 0.7 | 0.7 | Controlled |
| **proposer.thinking_level** | **high** | **minimal** | **MANIPULATED — factor under test** |
| proposer.passes (K) | 5 | 5 | Controlled |
| proposer.manifest | 55-map | 55-map | Controlled |
| proposer.tile_size | 384 | 384 | Controlled |
| proposer.workers | 60 | 250 | Orchestration only (concurrency; no payload change) |
| consensus.vote_threshold | 4 | 4 | Controlled (text-track sweep optimum) |
| consensus.dedup_radius_m | 20.0 | 20.0 | Controlled |
| extract.padding | 75 | 75 | Controlled |
| extract.rasters_dir | `Russian1981_32635` | same | Controlled |
| verify.config | `verify_adversarial-text.json` | same | Controlled |
| verify.model | `gemini-3-flash` | same | Controlled |
| verify.thinking_level | minimal (config default) | same | Controlled |
| verify.temperature | 0.0 (config default) | same | Controlled |
| verify.iterations | 1 | 1 | Controlled |
| evaluate.prob_threshold | 0.15 | 0.15 | Controlled |
| evaluate.buffers | [20,30,40,50] | same | Controlled |
| evaluate.bootstrap | 1000 | 1000 | Controlled |
| evaluate.seed | 42 | 42 | Controlled |
| evaluate.ground_truth | student-55maps | same | Controlled |
| evaluate.bounds | 55maps bounds | same | Controlled |

**Confounds: NONE.** Every parameter affecting the API payload is
identical. `workers` differs (60 → 250) for wall-clock throughput
but is an orchestration parameter that does not affect per-call model
output or F1. Paired permutation test post-run will measure the
thinking-level effect cleanly.

## 3. Transmission check

| Error mode | Status | Evidence |
|---|:--:|---|
| **Image flag** | ✅ PASS | `detect_brief-text.json` explicitly sets `include_example_images: False` — CORRECT for text-only pipeline. Skill's "absent ⇒ blocker" rule applies to image tracks, not text. |
| Temperature shadowed | ✅ PASS | YAML T=0.7 overrides config default T=1.0 via launcher CLI forwarding; dry-run `resolved_config.yaml` confirms `temperature: 0.7` |
| Thinking level dropped | ✅ PASS | YAML `thinking_level: minimal` resolves to `minimal` in dry-run; matches config default; explicit CLI `--thinking-level minimal` forwarded |
| Model version drift | ✅ PASS | Proposer and verifier both `gemini-3-flash` (matches HIGH reference run) |
| Tile size mismatch | ✅ PASS | 384 px, manifest from `inputs/tiles_384_55maps/` (same tiles as 2026-04-10 HIGH run and as 2026-04-18 image run) |
| Wrong tile set | ✅ PASS | 55-map manifest, 8,541 tiles, 55 distinct maps |
| Wrong instruction | ✅ PASS | Proposer: `detect_brief-text.md` (text-only track); verifier: `verify_adversarial.md` |
| Example paths | ✅ N/A | Text-only pipeline sends no example images; the 17 text-only examples in `detect_brief-text.json` are text descriptions embedded in the system instruction |
| Verifier text-only | ✅ PASS | 0 examples in verifier config (intentional) |

**Blockers: 0.**

## 4. Preregistration alignment

| # | Requirement | Config value | Verdict |
|--:|---|---|---|
| 1 | `detect_brief-text.json` | `detect_brief-text.json` | MATCHES (D17) |
| 2 | `include_example_images = false` | `false` (explicit) | MATCHES (D17) |
| 3 | Thinking MIN (under test) | `minimal` | MATCHES (pre-reg Stage 1 baseline; manipulated factor) |
| 4 | Temperature 0.7 | 0.7 | MATCHES (E49/E51) |
| 5 | K = 5 | 5 | MATCHES (E51) |
| 6 | Tile size 384 | 384 | MATCHES (E51/E53) |
| 7 | Greedy 20 m consensus | `dedup_radius_m: 20.0` | MATCHES (D26) |
| 8 | vote_t = 4 (text-track) | 4 | MATCHES (text-track sweep) |
| 9 | Verifier v1 adv-text | `verify_adversarial-text.json` | MATCHES (E37/E39) |
| 10 | Verifier minimal / T=0 / N=1 | minimal / 0.0 / 1 | MATCHES (D24) |
| 11 | prob_t = 0.15 | 0.15 | MATCHES |
| 12 | Primary 20 m + curve to 50 m | first buffer = 20, last = 50 | MATCHES (§4.1.1, E47) |
| 13 | Bootstrap 1000, seed 42 | 1000 / 42 | MATCHES (D10, E52) |
| 14 | Scope disjoint from calibration | 0 overlap with 487-tile Era 2 calibration | MATCHES (§2) |
| 15 | Padding 75 px | 75 | MATCHES (D23) |

- Matches: **15**
- Deliberate deviations: **0**
- **Undocumented deviations: 0**

## 5. Dry-run

Executed on sapphire 2026-04-18 10:05 UTC with
`--run-name 55maps-text-min-generalisation-dryrun --dry-run
--allow-dirty`. Results:

- YAML parsed, CLI overrides applied, `ResolvedRunConfig` materialised
- `launch_manifest.json` written with git commit SHA + all 6 input
  SHA256s populated (manifest, ground_truth, bounds, proposer_config,
  verifier_config, rasters_dir_listing)
- `experiment_intent.md` + `resolved_config.yaml` + `pre_launch_audit.md`
  copied into output dir
- Resolved values match intent: `thinking_level: minimal`,
  `temperature: 0.7`, `workers: 250`, `passes: 5`, `vote_threshold: 4`,
  `prob_threshold: 0.15`, `seed: 42`
- No subprocess invocations (dry-run short-circuits correctly)

One cosmetic observation:
`launch_manifest.json` reports `expected_cost_usd: 355.18` (image-
calibrated estimator). Actual text cost will be ~$65 — the
`_estimate_cost` helper uses a single per-tile rate calibrated on
image proposer payloads. Logged as a follow-up launcher fix; does
not affect the run.

**Verdict: PASS.**

## 6. Evaluation scope

| Check | Status |
|---|:--:|
| Evaluation manifest exists | ✅ `inputs/tiles_384_55maps/full_evaluation_manifest.json` |
| Expected tile count (8,541) | ✅ 8,541 |
| Expected map count (55) | ✅ 55 distinct maps |
| Disjoint from 487-tile Era 2 calibration | ✅ 0 overlap |
| Ground truth present (4,770 mounds) | ✅ `student-mounds-55maps.geojson` |
| Bounds file matches scope (55 bounds) | ✅ `55maps_evaluation_bounds.geojson` |

## 7. Completeness

Checked:

- All 15 preregistration requirements against config values (Step 4)
- All transmission error modes (Step 3)
- Filesystem resolution of every referenced path (proposer config,
  verifier config, instruction files, manifest, ground truth, bounds,
  rasters dir)
- Pairwise parameter diff against the retrospective HIGH baseline
  (Step 2)
- Disjointness of 55-map scope from calibration scope (Step 6)
- Dry-run confirmed launcher plumbing end-to-end (Step 5)
- `/audit` run on YAML + audit MD pre-launch (Section below)

Unverified (low-risk, recorded for transparency):

- Single-tile live smoke test at 250 workers on text proposer —
  skipped because the image run proved 250 workers works on a
  larger-payload case; text payload is smaller (no image examples)
  so TPM/RPM headroom is higher. Failure mode is unlikely.
- Per-raster integrity — 55 rasters present by count on sapphire;
  individual file checksums not computed.

## Code audit (`/audit`) findings

`/audit` run on the YAML config and this audit MD pre-launch found
one Medium issue (now fixed):

- **Overstated equivalence claim**: YAML header and audit Section 2
  originally said *"the ONLY differences are thinking_level and
  run_name"*, which was technically inaccurate given
  `proposer.workers: 60 → 250`. Worker count is orchestration, not a
  per-call payload parameter, so it does not confound the comparison —
  but the claim as written was overstated. Fixed: both files now
  document the workers difference explicitly and classify it as
  orchestration-only.

Low-severity findings (cosmetic, left as-is):

- Runtime estimate tightened from "~1.5–2 h" → "~2–3 h" based on
  image-run per-pass timing at 250 workers.
- `workers: 250` has not been smoke-tested on text proposer
  specifically; inferred safe from the image-run precedent (smaller
  text payload → lower TPM per call).

No Critical findings.

## Overall verdict

**READY TO LAUNCH.**

All 15 preregistration requirements match. All transmission error
modes pass. Configuration differs from the retrospective HIGH
baseline by exactly ONE payload parameter (`thinking_level`, the
factor under test) plus one orchestration parameter
(`workers: 60 → 250` — wall-clock-only, no F1 effect). Dry-run plumbs
the launcher end-to-end on sapphire with all reproducibility
metadata populated.

### Expected outcome

Budget $65–80 at Flex tier; runtime ~2–3 h. Post-run, the paired
permutation test (`scripts/pairwise_permutation_test.py --mode
geojson`, 10,000 iterations, seed 42) between the new MIN
`verified_detections.geojson` and the 2026-04-10 HIGH
`consensus-4of5.geojson` filtered at prob_t=0.15 will determine:

- **p > 0.05**: MIN is statistically indistinguishable from HIGH.
  The ~13 % cost premium for HIGH thinking is not justified.
  MIN becomes the recommended cost-optimal text-track config.
- **p ≤ 0.05**: HIGH thinking's F1 advantage is statistically
  significant. HIGH remains the recommended config.

Per the user's heuristic ("where ≥10 % cost savings are available
with statistically indistinguishable results, prefer the cheaper
option"), a p > 0.05 outcome would support switching the paper's
cost-optimal text recommendation from HIGH to MIN.

## Reproducing this audit

```bash
cd /home/shawn/Code/map-reader-llm
## Code audit (YAML + MD)
claude /audit \
    configs/run-configs/55maps_text_min_generalisation.yaml \
    configs/run-configs/55maps_text_min_generalisation_pre_launch_audit.md

## Pre-launch config audit
claude /audit-config "Hypothesis: 55-map text MIN thinking \
    generalisation; config: configs/run-configs/\
    55maps_text_min_generalisation.yaml; factor: thinking_level"
```

The launcher records a reference to this audit file in
`launch_manifest.json` under `pre_launch_audit`. Replicators should
re-run both audits after any config change and verify zero BLOCKERs
before re-launching.
