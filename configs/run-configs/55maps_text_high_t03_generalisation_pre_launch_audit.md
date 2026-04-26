# Pre-Launch Audit — 55-Map Text HIGH Generalisation Re-run at T=0.3

**Audit date**: 2026-04-26
**Auditor**: Claude Code via `/audit-config` skill
**Target run**: `configs/run-configs/55maps_text_high_t03_generalisation.yaml`
**Launcher**: `scripts/run_generalisation.py`
**Expected cost**: ~$70 at Gemini 3 Flash Flex tier (T=0.7 reference run was
$69.60; temperature change does not affect token counts; identical proposer
+ verifier configs)
**Reference run (must-match)**:
`configs/run-configs/55maps_text_high_generalisation.yaml` (2026-04-18,
$69.60)
**Source Era 2 cell**: `pv-high-text-t0.3-n5` (Tier 1 of per-architecture
leaderboard at 20m, F1 = 0.886; Tier 1 at 50m, F1 = 0.908)
**Purpose**: re-run the 55-map text-HIGH generalisation with T=0.3 instead
of T=0.7, after the Session 79 per-architecture leaderboard rebuild
identified the Era 2 cell `pv-high-text-t0.3-n5` as a higher-F1 alternative
to the T=0.7 cell originally chosen for the 2026-04-18 reference run.

## 1. Source-of-truth requirements

This is a **post-leaderboard re-run**, not a preregistered hypothesis test.
The source of truth is the existing 2026-04-18 text-HIGH config plus the
project's standing rule: *"only the target parameter may change between
experimental conditions; audit configs against originals before running."*

| # | Requirement | Source |
|---|---|---|
| 1 | Proposer config = `prompts/configs/detect_brief-text.json` | Reference YAML + Era 2 source `outputs/h11/.../text-t0.3/run_*` |
| 2 | Proposer thinking_level = `high` | Reference YAML + Era 2 cell label `pv-high-text-...` |
| 3 | Proposer K (passes) = 5 | Reference YAML + leaderboard cell `...-n5` |
| 4 | Proposer temperature = **0.3** (target factor) | Era 2 cell `text-t0.3` path |
| 5 | Consensus vote_threshold = 4 | Reference YAML + inventory `vote_t=4` |
| 6 | Verifier config = `prompts/configs/verify_adversarial-text.json` (canonical v1) | Reference YAML + Era 2 verifier `verified-v1-n5` |
| 7 | Verifier instruction file unchanged byte-wise | Reproducibility rule |
| 8 | Proposer instruction file unchanged byte-wise | Reproducibility rule |
| 9 | Evaluate prob_threshold = 0.15 | Reference YAML + inventory `prob_t=0.15` |
| 10 | Evaluate buffers = [20, 30, 40, 50] | Reference YAML |
| 11 | Bootstrap 1000 iterations, seed 42 | Reference YAML |
| 12 | Ground truth + bounds files match reference | Reference YAML |
| 13 | Service tier = flex | Reference YAML; user pre-approval |
| 14 | Tiles manifest count matches reference run (~8,500) | Reference run processed 8,516 tiles |

## 2. Config pairwise diff (new vs reference)

Substantive differences (excluding cosmetic comment-only changes):

| Field | Reference (T=0.7) | New (T=0.3) | Classification |
|-------|-------------------|-------------|----------------|
| `run_name` | `55maps-text-high-generalisation` | `55maps-text-high-t0.3-generalisation` | METADATA — expected |
| `proposer.temperature` | `0.7` | **`0.3`** | **MANIPULATED** — the target factor |
| (all other 23 substantive fields) | identical | identical | Controlled |

**Confounds**: NONE.

## 3. Transmission verification

| Error mode | Check | Verdict |
|---|---|---|
| Image flag off | `include_example_images: false` (text-only by design); matches reference (recorded `false` in T=0.7 `run.meta`) | **PASS** |
| Temperature shadowed | YAML `proposer.temperature: 0.3` → flows via `run_generalisation.py:544` (`--temperature str(p["temperature"])`) → reaches API | **PASS** |
| Thinking level dropped | YAML `thinking_level: high`; not Pro model so no MEDIUM-floor concern | **PASS** |
| Model version drift | Both reference and new resolve `gemini-3-flash` → `gemini-3-flash-preview` | **PASS** |
| Tile size mismatch | YAML `tile_size: 384` matches reference and Era 2 source | **PASS** |
| Wrong tile set | YAML manifest resolves on sapphire to **8,541 tiles** (reference processed 8,516; 25 failed = 0.3% — within normal range) | **PASS** |
| Wrong instruction file | Proposer config uses `detect_brief-text.json` (text-only) — matches reference | **PASS** |
| Example paths broken | Examples are text descriptions (`include_example_images: false`); no image paths | **N/A** |
| Prompt drift — proposer | `sha256sum prompts/system-instructions/detect_brief-text.md` = `e169b7237b853eeaad990fc2e54fbd7214afb435d85c8e444a4a784432200e12` ✓ matches T=0.7 run's recorded hash byte-for-byte | **PASS** |
| Prompt drift — verifier | `sha256sum prompts/system-instructions/verify_adversarial.md` = `2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25dc1454af3497e15d` ✓ matches T=0.7 run's recorded hash byte-for-byte | **PASS** |
| Example library drift | Current config has 17 examples; T=0.7 run recorded 17 examples | **PASS** |

**Blockers**: NONE.

## 4. Reference alignment table

All 14 requirements from §1 verified MATCHES against the reference YAML and
Era 2 source. Undocumented deviations: NONE.

## 5. Dry-run validation

Recommended pre-launch:

```bash
ssh sapphire 'cd /home/shawn/Code/map-reader-llm/ && .venv/bin/python scripts/run_generalisation.py proposer \
    --run-config configs/run-configs/55maps_text_high_t03_generalisation.yaml \
    --run-name 55maps-text-high-t0.3-generalisation \
    --dry-run'
```

Should report 8,541 tiles, 17 examples, temperature 0.3 reaching the API.

## 6. Evaluation scope check

| Check | Verdict |
|---|---|
| Bounds file is the 55-map evaluation scope | **PASS** — `inputs/vectors/bounds/384/55maps_evaluation_bounds.geojson` (same as reference) |
| Ground truth file matches reference | **PASS** — `inputs/vectors/references/student-mounds-55maps.geojson` |
| Disjoint from Era 2 487-tile scope | **PASS** — distinct tile naming conventions confirm distinct scopes |

## 7. Completeness check

- All 14 requirements verified ✓
- All 11 transmission error modes checked ✓
- 23+ non-target fields confirmed identical via diff ✓
- Prompt SHA256 checks performed for both proposer + verifier ✓

## BLOCKERS: NONE

## WARNINGS

1. **Must launch from sapphire** — `inputs/tiles_384_55maps/` is gitignored
   (line 75 of `.gitignore`) and only present on sapphire. Running from
   amd-tower would fail at the proposer stage.
2. **Dry-run not yet performed** — recommended before committing the API
   spend.

## OVERALL: READY TO LAUNCH

### Approval recorded

User approved API spend on 2026-04-26: ~$70 expected, $100 ceiling, Gemini
3 Flash Flex tier, realtime mode, 14-cell scope match per the inventory
entry `pv-high-text-t0.3-n5`.

### Metadata logged for paper reporting

`run_generalisation.py` produces:

- `launch_manifest.json` — git commit SHA, input file SHA256s, resolved
  configuration
- `cost_manifest.json` — per-stage cost breakdown, per-pass tokens, cache
  hit rate, per-map cost attribution
- `experiment_intent.md` — auto-generated narrative
- Per-pass `*.meta.json` — model, prompt hash, library hash, full
  configuration snapshot
- Verified detection geojson + probabilities.json
- Multi-buffer evaluation results (F1, P, R, MCC + 1000-iter bootstrap CIs
  at 20 / 30 / 40 / 50 m buffers)
