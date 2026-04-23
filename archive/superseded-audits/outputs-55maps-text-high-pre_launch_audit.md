# Pre-Launch Audit — 55-Map Text HIGH Generalisation Re-run

**Audit date**: 2026-04-19
**Auditor**: Claude Code via `/audit-config` skill (+ `/audit` for YAML + MD)
**Target run**: `configs/run-configs/55maps_text_high_generalisation.yaml`
**Launcher**: `scripts/run_generalisation.py` (v1.0.0)
**Expected cost**: ~$75 at Gemini 3 Flash Flex tier (text MIN measured
$60.79; HIGH thinking adds ~19 % proposer thinking tokens).
**Purpose**: Re-run the 2026-04-10 text HIGH generalisation under the
publishable launcher so it sits alongside the text MIN (2026-04-18) and
image HIGH (2026-04-18) runs with equivalent documentation: pre-launch
audit, post-run report, launch_manifest, cost_manifest, per-map cost
attribution, and reproducibility artefacts. The 2026-04-10 run is
preserved intact at `outputs/55maps-generalisation/` with its
retrospective post-run report honestly labelling its limitations; this
re-run closes those gaps with measured values.

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
5. `configs/run-configs/55maps_text_min_generalisation.yaml` — the
   paired MIN configuration (structural template for this re-run).
6. `configs/run-configs/55maps_text_generalisation_retrospective.yaml`
   — the 2026-04-10 HIGH parameter baseline this re-run reproduces.
7. `configs/run-configs/55maps_text_min_generalisation_pre_launch_audit.md`
   — audit template mirrored here for documentation symmetry.

## 1. Preregistration requirements extracted (15)

| # | Requirement | Source | Stage |
|--:|---|---|---|
| 1 | Proposer config: `detect_brief-text.json` (text-track carry-forward) | Decision 17 (text-track uses Scale-8 metadata); E51 text-track text library | proposer |
| 2 | Proposer `include_example_images`: false (text-only prompts) | Decision 17 | proposer |
| 3 | Proposer thinking: **high** (2026-04-10 production carry-forward; operating point used for the headline text generalisation result) | Errata E49; 2026-04-10 text HIGH run (F1 = 0.790 measured, 0.814 D-S corrected) | proposer |
| 4 | Proposer temperature: 0.7 | Errata E49, E51 | proposer |
| 5 | K (consensus passes): 5 | Errata E51 (overrides pre-reg K=10) | proposer |
| 6 | Tile size: 384 px | Errata E51, E53 | proposer |
| 7 | Consensus algorithm: greedy-ball 20 m | Decision 26; pre-reg §8.5 | consensus |
| 8 | Vote threshold: 4 (of 5) — text-track sweep optimum, distinct from image-track 3/5 | 2026-04-10 run consensus-4of5.geojson; text-track sweep | consensus |
| 9 | Verifier: `verify_adversarial-text.json` v1 | Errata E37, E39 | verifier |
| 10 | Verifier: minimal thinking / T=0.0 / N=1 single-pass | Decision 24 | verifier |
| 11 | Verifier probability threshold: 0.15 | Paired-with-MIN operating point; v1 threshold sweep | verifier |
| 12 | Evaluation primary tolerance: 20 m primary; curve over 20/30/40/50 m | Preregistration §4.1.1; E7 added 40 m; E47 reverts primary to 20 m | evaluate |
| 13 | Evaluation: 1000-iter bootstrap, tile-level, seed 42 | Decision 10; E52 | evaluate |
| 14 | Evaluation scope disjoint from calibration (0 overlap) | Preregistration §2 (holdout principle) | evaluate |
| 15 | Crop padding 75 px (→ 150×150 crops) | Decision 23 | extract |

## 2. Configuration pairwise diff

Two-way check: this re-run is structurally mirrored from the text MIN
YAML (same launcher, same workers, same documentation template) and is
a parameter replica of the 2026-04-10 text HIGH retrospective YAML
(same thinking_level, same K, same vote_t, same prob_t, etc.).

### 2a. Diff vs text MIN YAML (paired comparison; MIN is this run's pair)

Single-factor paired design. Every parameter that affects the API
payload is held identical to `55maps_text_min_generalisation.yaml`;
only `thinking_level` differs.

| Field | text MIN | text HIGH (this run) | Classification |
|-------|:--------:|:--------------------:|:--------------:|
| run_name | `55maps-text-min-generalisation` | `55maps-text-high-generalisation` | Output segregation (expected) |
| proposer.config | `detect_brief-text.json` | same | Controlled |
| proposer.model | `gemini-3-flash` | same | Controlled |
| proposer.instruction_file | `detect_brief-text.md` | same | Controlled |
| proposer.include_example_images | `false` | same | Controlled (text-only) |
| proposer.temperature | 0.7 | 0.7 | Controlled |
| **proposer.thinking_level** | **minimal** | **high** | **MANIPULATED — factor under test** |
| proposer.passes (K) | 5 | 5 | Controlled |
| proposer.manifest | 55-map | 55-map | Controlled |
| proposer.tile_size | 384 | 384 | Controlled |
| proposer.workers | 250 | 250 | Controlled (orchestration; unchanged) |
| consensus.vote_threshold | 4 | 4 | Controlled (text-track sweep optimum) |
| consensus.dedup_radius_m | 20.0 | 20.0 | Controlled |
| extract.padding | 75 | 75 | Controlled |
| extract.rasters_dir | `Russian1981_32635` | same | Controlled |
| verify.config | `verify_adversarial-text.json` | same | Controlled |
| verify.model | `gemini-3-flash` | same | Controlled |
| verify.thinking_level | minimal | minimal | Controlled |
| verify.temperature | 0.0 | 0.0 | Controlled |
| verify.iterations | 1 | 1 | Controlled |
| evaluate.prob_threshold | 0.15 | 0.15 | Controlled |
| evaluate.buffers | [20,30,40,50] | same | Controlled |
| evaluate.bootstrap | 1000 | 1000 | Controlled |
| evaluate.seed | 42 | 42 | Controlled |
| evaluate.ground_truth | student-55maps | same | Controlled |
| evaluate.bounds | 55maps bounds | same | Controlled |

**Confounds vs text MIN: NONE.** Every parameter affecting the API
payload is identical except `thinking_level` (the factor under test).
Worker count is identical (both at 250). Paired permutation test
post-run will measure the thinking-level effect cleanly and should
reproduce the 2026-04-10 (HIGH) vs 2026-04-18 (MIN) pattern already
observed: significant at 30/40/50 m (p<0.0001), ns at 20 m (p≈0.4).

### 2b. Diff vs 2026-04-10 retrospective HIGH YAML (parameter replica)

Every API-payload parameter is identical. Only orchestration and
output-segregation parameters change.

| Field | HIGH 2026-04-10 (retrospective) | HIGH 2026-04-19 (this re-run) | Classification |
|-------|:-------------------------------:|:-----------------------------:|:--------------:|
| run_name | `55maps-text-generalisation` | `55maps-text-high-generalisation` | Output segregation (expected) |
| proposer.workers | 60 | 250 | Orchestration only (wall-clock; no payload change) |
| All other proposer fields | — | identical | Controlled |
| consensus / extract / verify / evaluate | — | identical | Controlled |

**Confounds vs 2026-04-10 HIGH: NONE.** API-payload parameters are
identical. Worker count changes (60 → 250) for wall-clock throughput —
orchestration only, no effect on per-call model output or F1.
Measured F1 should match the 2026-04-10 run within bootstrap CI
(temperature 0.7 introduces per-call stochasticity; seed 42 controls
aggregation but not per-call model sampling).

## 3. Transmission check

| Error mode | Status | Evidence |
|---|:--:|---|
| **Image flag** | ✅ PASS | `detect_brief-text.json` explicitly sets `include_example_images: False` — CORRECT for text-only pipeline. Skill's "absent ⇒ blocker" rule applies to image tracks, not text. |
| Temperature shadowed | ✅ PASS | YAML T=0.7 overrides config default T=1.0 via launcher CLI forwarding; resolved_config.yaml will show `temperature: 0.7` |
| Thinking level dropped | ✅ PASS | YAML `thinking_level: high` overrides config default `minimal` via launcher CLI forwarding; explicit CLI `--thinking-level high` forwarded |
| Model version drift | ✅ PASS | Proposer and verifier both `gemini-3-flash` (matches text MIN and retrospective HIGH reference runs) |
| Tile size mismatch | ✅ PASS | 384 px, manifest from `inputs/tiles_384_55maps/` (same tiles as text MIN and 2026-04-10 HIGH run) |
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
| 3 | Thinking HIGH (2026-04-10 production carry-forward) | `high` | MATCHES (E49) |
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

Executed on sapphire 2026-04-19 14:02 UTC via
`.venv/bin/python scripts/run_generalisation.py all
--run-config configs/run-configs/55maps_text_high_generalisation.yaml
--run-name 55maps-text-high-generalisation-dryrun --dry-run
--allow-dirty --yes`. Results:

- YAML parsed, CLI overrides applied, `ResolvedRunConfig` materialised
- `launch_manifest.json` written with git commit SHA
  (`ac4ba4e04474b9769c0d9d11c4e7bb6e14dc5c86`) + all 6 input SHA256s
  populated (manifest, ground_truth, bounds, proposer_config,
  verifier_config, rasters_dir_listing)
- `experiment_intent.md` + `resolved_config.yaml` + `pre_launch_audit.md`
  copied into output dir
- Resolved values match intent: `thinking_level: high`,
  `temperature: 0.7`, `workers: 250`, `passes: 5`, `vote_threshold: 4`,
  `prob_threshold: 0.15`, `seed: 42`, `buffers: [20,30,40,50]`,
  `bootstrap: 1000`
- Resolved paths match intent: proposer
  `prompts/configs/detect_brief-text.json`, verifier
  `prompts/configs/verify_adversarial-text.json`, GT
  `student-mounds-55maps.geojson`, bounds
  `55maps_evaluation_bounds.geojson`
- `config_file_sha256: 6a3f3c9f…fb7e` and audit-MD sha256
  `66e82fc3…d9e1` both recorded
- No subprocess invocations (dry-run short-circuits correctly)

Cosmetic observation (same as text MIN run):
`launch_manifest.json` reports `expected_cost_usd: 355.18` from the
image-calibrated estimator. Actual text HIGH cost will be ~$75 — the
`_estimate_cost` helper uses a single per-tile rate calibrated on
image proposer payloads (GH issue #1). Does not affect the run.

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
- Pairwise parameter diff against text MIN YAML (Step 2a) and the
  retrospective 2026-04-10 HIGH YAML (Step 2b) — two-way check
- Disjointness of 55-map scope from calibration scope (Step 6)
- Dry-run confirmed via `/audit-config` on sapphire (Step 5)
- `/audit` run on YAML + audit MD pre-launch (Section below)

Unverified (low-risk, recorded for transparency):

- Single-tile live smoke test at 250 workers on text HIGH proposer —
  skipped because the text MIN run at 250 workers proved the
  concurrency envelope for text payloads; HIGH adds thinking tokens
  (reduces TPM headroom by ~19 %) but stays well within Tier 3 limits.
- Per-raster integrity — 55 rasters present by count on sapphire;
  individual file checksums not computed.

## Code audit (`/audit`) findings

`/audit` run on the YAML + this audit MD on 2026-04-19 found two
Medium issues (both fixed in place):

- **Preregistration overclaim**: Requirement 3 originally described
  HIGH as "the preregistered Stage-1 alternate operating point".
  HIGH thinking is established as the 2026-04-10 production
  carry-forward via Errata E49, not as a preregistered alternate. The
  claim has been softened to "operating point used for the headline
  text generalisation result".
- **Stale audit date**: Header originally stamped 2026-04-18 (plan
  creation date). Updated to 2026-04-19 (actual audit execution
  date).

Low-severity observation (left as-is):

- YAML inline comment `~1.7× faster than 60` on the `workers: 250`
  line is inherited from the text MIN template and refers to the
  orchestration change vs the 2026-04-10 retrospective baseline
  (60 workers). The text MIN YAML uses identical wording; header
  comments in both files disambiguate.

No Critical findings. Cross-file consistency check confirmed both
files cite the same `run_name`, `thinking_level`, worker count, and
reference paths. UK/AU spelling sweep returned no matches in either
file.

## Overall verdict

**READY TO LAUNCH.**

All 15 preregistration requirements match. All transmission error
modes pass. Configuration differs from the text MIN YAML by exactly
ONE payload parameter (`thinking_level: minimal → high`, the factor
under test); workers are unchanged. Configuration is a parameter
replica of the 2026-04-10 retrospective HIGH YAML with only
orchestration differences (`workers: 60 → 250`). Dry-run executed
end-to-end on sapphire (2026-04-19); all resolved values match
intent, all six input SHA256s populated, git commit SHA
`ac4ba4e0` recorded.

### Expected outcome

Budget ~$75 at Flex tier (text MIN measured $60.79; HIGH thinking
adds ~19 % for proposer thinking tokens). Runtime ~2–3 h at 250
workers.

Post-run, the paired permutation test
(`scripts/pairwise_permutation_test.py --mode geojson`, 10,000
iterations, seed 42) between the new HIGH `verified_detections.geojson`
and the text MIN `verified_detections.geojson` (already committed)
should reproduce the pattern observed on the 2026-04-10 vs 2026-04-18
MIN pairing:

- Significant at 30/40/50 m (p<0.0001) — HIGH's ~0.024 F1 advantage
  holds.
- Ns at 20 m (p≈0.4) — at the strictest localisation tolerance the
  thinking-level effect is absorbed by the tolerance noise floor.

Measured F1 @ 50 m should match the 2026-04-10 run within bootstrap
CI (expected ≈ 0.790 measured / 0.814 D-S corrected). A divergence
outside the bootstrap CI would be flagged as a surprising finding
(per CLAUDE.md research-calibration guidance) and investigated
before acceptance.

## Reproducing this audit

```bash
cd /home/shawn/Code/map-reader-llm
# Code audit (YAML + MD)
claude /audit \
    configs/run-configs/55maps_text_high_generalisation.yaml \
    configs/run-configs/55maps_text_high_generalisation_pre_launch_audit.md

# Pre-launch config audit (dry-run on sapphire)
claude /audit-config "Hypothesis: 55-map text HIGH thinking \
    generalisation re-run; config: configs/run-configs/\
    55maps_text_high_generalisation.yaml; factor: thinking_level"
```

The launcher records a reference to this audit file in
`launch_manifest.json` under `pre_launch_audit`. Replicators should
re-run both audits after any config change and verify zero BLOCKERs
before re-launching.
