# SUPERSEDED 2026-04-24

**Reason**: Run completed 2026-04-18; this configs/ copy is a duplicate of the outputs/ audit.

**See**: `configs/run-configs/55maps_image_generalisation_post_run_report.md` (primary) and the outputs/ sibling `outputs/55maps-image-generalisation/post_run_report.md`

This document is preserved for audit / historical reference. Its original content follows below.

---

## Pre-Launch Audit — 55-Map Image Generalisation Run

**Audit date**: 2026-04-18
**Auditor**: Claude Code via `/audit-config` skill (+ `/audit` for launcher code)
**Target run**: `configs/run-configs/55maps_image_generalisation.yaml`
**Launcher**: `scripts/run_generalisation.py` (v1.0.0)
**Expected cost**: ~$350 at Gemini 3 Flash Flex tier
**Purpose**: Final image-track generalisation run reported in the paper.

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
4. The filesystem — actual JSON / YAML / GeoJSON / PNG values override
   claims in `description` fields.

## 1. Preregistration requirements extracted (20)

| # | Requirement | Source | Stage |
|--:|---|---|---|
| 1 | Proposer library: `library_plus-hp.json` | Errata E51, E53 | proposer |
| 2 | Proposer thinking: HIGH | Errata E49, E51 (overrides pre-reg minimal) | proposer |
| 3 | Proposer temperature: 0.7 | Errata E49, E51 | proposer |
| 4 | K (consensus passes): 5 | Errata E51 (overrides pre-reg K=10) | proposer |
| 5 | Tile size: 384 px | Errata E51, E53 | proposer |
| 6 | Consensus algorithm: greedy-ball 20 m | Decision 26; pre-reg §8.5 | consensus |
| 7 | Vote threshold: 3 (of 5) | Decision 25 (analogy from 3-of-10) | consensus |
| 8 | Verifier: `verify_adversarial-text.json` v1 | Errata E37, E39 | verifier |
| 9 | Verifier thinking: minimal | Decision 24 | verifier |
| 10 | Verifier temperature: 0.0 | Decision 24 | verifier |
| 11 | Verifier iterations: N = 1 (single-pass) | Decision 24 | verifier |
| 12 | Verifier probability threshold: 0.15 | Phase 3d tuning / prior 55-map text run | verifier |
| 13 | Evaluation primary tolerance: 20 m | Pre-reg §4.1.1; E47 | evaluate |
| 14 | Evaluation buffers: 20 / 30 / 40 / 50 m | E7, E47 | evaluate |
| 15 | Bootstrap iterations: 1000 | Decision 10 | evaluate |
| 16 | Random seed: 42 | E52 | evaluate |
| 17 | Consensus dedup radius matches Hungarian buffer | Pre-reg §8.5 line 1898 | consensus |
| 18 | Crop padding: 75 px (→ 150×150 px crops) | Decision 23 | extract |
| 19 | 55-map scope disjoint from calibration (0 overlap) | Pre-reg §2 (holdout principle) | evaluate |
| 20 | Greedy-ball primary; WBF optional robustness | Decision 26 | consensus |

## 2. Configuration diff

Single-config carry-forward run (no sweep). Every parameter is
**Controlled**; no factor is manipulated. Paper reports a single
(library, thinking, T, K, vote_t, prob_t, buffer) operating point.

## 3. Transmission check

| Error mode | Status | Evidence |
|---|:--:|---|
| **Image flag off** | ✅ **PASS** | `include_example_images: true` **explicit** in `library_plus-hp.json` (added during this audit; pre-fix it was absent and relied on a `config.get(..., True)` runtime default — the skill's H10/H12 rule treats absence as an always-blocker, so we fixed it) |
| Temperature shadowed | ✅ PASS | YAML `temperature: 0.7` overrides config default `0.0` via launcher CLI forwarding; Phase 3a runs confirmed this path works |
| Thinking level dropped | ✅ PASS | YAML `thinking_level: high` overrides config default `minimal`; CLI forwarding confirmed |
| Model version drift | ✅ PASS | Proposer and verifier both `gemini-3-flash` |
| Tile size mismatch | ✅ PASS | Config `tile_size: 384`; tiles under `inputs/tiles_384_55maps/` |
| Wrong tile set | ✅ PASS | `55maps_full_evaluation_manifest.json`, 8,541 tiles, 55 distinct maps |
| Wrong instruction file | ✅ PASS | Proposer: `detect_brief-text-image.md` (image-track); verifier: `verify_adversarial.md` |
| Example paths broken | ✅ PASS | All 13 `inputs/examples/neutral-naming/example_*.png` resolve |
| Verifier text-only | ✅ PASS | 0 examples in verifier config (intentional for text-only verifier) |

Blockers (pre-fix): 1 (image flag absence). **Blockers remaining: 0.**

## 4. Preregistration alignment

| # | Requirement | Config value | Verdict |
|--:|---|---|---|
| 1 | Library: plus-hp | `library_plus-hp.json` | MATCHES (E51/E53) |
| 2 | Thinking: HIGH | `high` | MATCHES (E49/E51) |
| 3 | Temperature: 0.7 | 0.7 | MATCHES |
| 4 | K = 5 | 5 | MATCHES (E51) |
| 5 | Tile size 384 | 384 | MATCHES (E51/E53) |
| 6 | Greedy 20 m | `dedup_radius_m: 20.0` | MATCHES (D26) |
| 7 | vote_t = 3 | 3 | MATCHES (D25) |
| 8 | Verifier v1 adv-text | `verify_adversarial-text.json` | MATCHES (E37/E39) |
| 9 | Verifier minimal | `minimal` | MATCHES (D24) |
| 10 | Verifier T = 0.0 | 0.0 | MATCHES (D24) |
| 11 | Verifier N = 1 | 1 (default) | MATCHES (D24) |
| 12 | prob_t = 0.15 | 0.15 | MATCHES |
| 13 | Primary tolerance 20 m | first buffer = 20 | MATCHES (§4.1.1, E47) |
| 14 | Buffers 20/30/40/50 | `[20, 30, 40, 50]` | MATCHES (E7, E47) |
| 15 | Bootstrap 1000 | 1000 | MATCHES (D10) |
| 16 | Seed 42 | 42 | MATCHES (E52) |
| 17 | Consensus radius = eval tolerance | 20.0 = 20 | MATCHES (§8.5) |
| 18 | Padding 75 px | 75 | MATCHES (D23) |
| 19 | Scope disjoint from calibration | 0 overlap with 487-tile Era 2 calibration manifest | MATCHES (§2) |
| 20 | Greedy primary | default pipeline | MATCHES (D26) |

- Matches: **20**
- Deliberate deviations: **0** (every deviation from the original
  preregistration is authorised by errata / decisions)
- **Undocumented deviations: 0**

## 5. Dry-run

Performed *after* this audit:
`python scripts/run_generalisation.py all --run-config configs/run-configs/55maps_image_generalisation.yaml --dry-run`.

Verifies the launcher parses its YAML, writes a valid `launch_manifest.json`
and `experiment_intent.md`, and plumbs subprocess arguments correctly.
Any deviation there aborts the launch before the first paid API call.

## 6. Evaluation scope

| Check | Status |
|---|:--:|
| Evaluation manifest exists | ✅ `inputs/tiles_384_55maps/full_evaluation_manifest.json` |
| Expected tile count: 8,541 | ✅ 8,541 |
| Expected map count: 55 | ✅ 55 |
| Disjoint from 487-tile Era 2 calibration | ✅ 0 overlap |
| Ground truth present and non-empty | ✅ `student-mounds-55maps.geojson`, 4,770 mounds, 2 MB |
| Evaluation bounds file matches scope | ✅ `55maps_evaluation_bounds.geojson`, 55 bounds |

## 7. Completeness

Checked:

- All 20 preregistration requirements against config values (Step 4)
- All transmission error modes against both configs (Step 3)
- Filesystem resolution of every referenced path (proposer config,
  verifier config, instruction files, example library, manifest, ground
  truth, bounds)
- Example-image path resolution: 13 / 13 resolve
- Disjointness of 55-map scope from calibration scope

Unverified (low risk, recorded for transparency):

- Example image *dimensions* — not verified per-file; known convention
  per Decision 23 is 150 × 150 for HP/HN and 384 × 384 for null tiles,
  but we did not open each PNG to confirm.
- Per-raster integrity on sapphire — 55 rasters confirmed by file
  count; checksums not computed.
- Runtime test of the launcher's `--dry-run` — performed after this
  audit (see Section 5).

## Code audit (`/audit`) findings

Separately from `/audit-config`, a line-by-line `/audit` of the
launcher and YAML was performed prior to this audit. Five Critical
issues were found and fixed before this `/audit-config` pass:

1. Token-key lookup bug — `thinking_tokens` was silently zeroed in the
   cost manifest (Gemini uses `total_thoughts_tokens`, not
   `total_thinking_tokens`). Fixed via explicit field-name mapping.
2. Cache-hit-rate denominator — double-counted cached tokens. Fixed.
3. `yaml.safe_dump` on `Path` objects — would raise on CLI-path
   overrides. Fixed by stringifying before dump.
4. Top-level `service_tier` in the YAML was a dead key. Now
   propagates to both proposer and verify sections with CLI precedence.
5. Git-dirty check false-flagged untracked output directories. Fixed
   to check only tracked-file modifications; untracked count recorded
   in the launch manifest for audit.

Plus three medium fixes (pass-index parser robustness, manifest-format
tolerance, README cost range corrected).

## Overall verdict

**READY TO LAUNCH.**

All 20 preregistration requirements match. All transmission error
modes pass. No undocumented deviations. Scope is disjoint from
calibration. One initial blocker (`include_example_images` absent) was
fixed during the audit by making the flag explicit.

The expected headline outcome is F1 @ 20 m ≈ 0.75 (image track),
F1 @ 50 m ≈ 0.85, based on Era 2 plus-hp image matrix results scaled
by the prior text 55-map attenuation (F1 Era 2 text 0.814 → F1 55-map
text 0.790 at 50 m ≈ −0.025 attenuation).

## Reproducing this audit

```bash
cd /home/shawn/Code/map-reader-llm
## code audit
claude /audit scripts/run_generalisation.py \
              configs/run-configs/55maps_image_generalisation.yaml \
              configs/run-configs/README.md

## pre-launch config audit
claude /audit-config "Hypothesis: 55-map image generalisation; \
                      config: configs/run-configs/55maps_image_generalisation.yaml"
```

The launcher records a reference to this audit file in
`launch_manifest.json` under `pre_launch_audit`. Replicators should
re-run both audits after any config change and verify zero BLOCKERs
before re-launching.
