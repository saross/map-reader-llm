# Pre-launch audit — K-ladder Phase 2, tiers A–D

> **Last revised**: 2026-09-12 (original publication — step 2 of the K-ladder
> Phase-2 run, before any tier's verifier pass was launched). Controlling card:
> `planning/k-ladder-review-2026-09-11.md` (rulings R1–R5); costing and gate:
> `reports/k-ladder-phase2-costing-2026-09-12.md`. Discipline:
> `~/.claude/skills/audit-config/SKILL.md`. See [§ Changelog](#changelog).

**Verdict: READY TO LAUNCH.** 0 blockers, 3 warnings, all three recorded below
and none of them a reason to hold the spend. Every check has a verdict; nothing
is reported as "looks fine".

## 0. What is being launched, and what the gate authorises

| Field | Value | Anchor |
|---|---|---|
| Stage | one verifier pass per rung over a freshly built first-N consensus union | `reports/k-ladder-phase2-costing-2026-09-12.md` § 5, "Practical notes" |
| Rungs | 28 (tiers A, B, C, D — all four approved by the PI on 2026-09-12) | costing § 3, § 5 |
| Candidates | **35,844** measured, not extrapolated | `results/k-ladder-2026-09-12/phase2/unions.json`, `total_candidates_ok` |
| Model | `gemini-3-flash`, resolved by the client to `gemini-3-flash-preview` | `prompts/configs/verify_adversarial-text.json`; `scripts/run_pv.py:1393-1420` (`_resolve_model_name`) |
| Config | `prompts/configs/verify_adversarial-text.json` | R1 |
| Thinking / temperature / iterations | MINIMAL / 0.0 / n = 1 | config, unmodified |
| Tier | real-time **flex** (`--service-tier flex`) | costing § 2 "Rate basis" |
| Estimated cost | **US$24.84** at 0.000693 USD per candidate | costing § 1 |
| Hard stop | running total above **US$30** | the run's brief |

Anything outside that row set — a different model, a different config, a
re-run of a failed union, a proposer pass — is **not** approved and is not
launched.

## 1. Preregistration requirements (9 extracted, all HARD unless noted)

Read this session: `docs/methodology/preregistration/protocol-errata.md`
(E33, E37, E39, E56) and the errata's PV entries. The verifier stage is
registered as **H2 Condition B** by E37, so the requirements are E37's plus the
corrections that post-date it.

| # | Requirement | Source | Class |
|---:|---|---|---|
| 1 | Verifier crops are extracted from the **source GeoTIFF rasters**, not from tile PNGs; tile PNGs are a fallback only | E33 (`protocol-errata.md:830-853`) | HARD |
| 2 | Crop size 150 × 150 px, i.e. `--padding 75` | E33 fix text; errata line 1557 ("150px, aligned with verifier standard") | HARD |
| 3 | The verifier is fed from a **consensus union** of proposer passes, not a single detection pass | E37 (`protocol-errata.md:1041-1043`) | HARD |
| 4 | Verifier model is `gemini-3-flash` | E37 deviation list; errata line 1191 ("All verifier runs used `gemini-3-flash`") | HARD |
| 5 | Verifier strategy is **adversarial** (`verify_adversarial.md`) — the default retained after E39 showed the three strategies equivalent | E39 (`protocol-errata.md:1090-1102`) | HARD (consistency, not statistics) |
| 6 | Verifier consensus size n = 1 (the registration is silent; N = 1 is the production choice) | E37 deviation 5 (`protocol-errata.md:1052`) | RECOMMENDED |
| 7 | Verifier thinking level MINIMAL, fixed by the 2026-01-15 calibration pilot | `prompts/configs/verify_adversarial-text.json` `_config_notes.thinking_level` | HARD |
| 8 | Verifier temperature 0.0 | same, `_config_notes.temperature`; E37 | HARD |
| 9 | A `prob_t`-thresholded F1 from these diagnostics is an **in-sample, test-set-optimised** number and must be reported as such; `pv-diag ∩ calibration = 0`, so there is no calibration data to select on | E56 (`protocol-errata.md:2003-2014`) | HARD (reporting) |

## 2. Config diff across the 28 rungs

**Every rung uses one config file, byte-identical, unmodified.** The
manipulated variable of this job is K — the number of proposer passes in the
union the verifier sees — and K lives in the *input*, not in any config field.
So the expected diff table is: everything controlled, nothing manipulated
inside the config.

| Field | Identical across 28 rungs? | Value | Classification |
|---|:---:|---|---|
| `version` | YES | `verify_adversarial-text` | Controlled |
| `model` | YES | `gemini-3-flash` → resolved `gemini-3-flash-preview` | Controlled (R1) |
| `instruction_file` | YES | `verify_adversarial.md` | Controlled (R1, E39) |
| `temperature` | YES | `0.0` | Controlled (R1) |
| `thinking_level` | YES | `minimal` | Controlled (R1) |
| `max_output_tokens` | YES | `8192` | Controlled |
| `examples` | YES | `[]` | Controlled (text-only track) |
| `text_only_labels` | YES | 6 labels | Controlled |
| `crop_label` | YES | "Now classify the candidate symbol…" | Controlled |
| `hypothesis` | YES | `H2` | Metadata |
| — | — | — | — |
| **union (the input)** | **NO — by design** | 28 first-N unions, K ∈ {1, 3} | **MANIPULATED — expected** |

**Intent → config check.** The factor the review tests (K) *does* differ
between conditions: the 28 unions carry 28 distinct candidate sets, and the
K = 1 and K = 3 unions of one pool differ in size by 133 to 1,385 candidates
(`unions.json`). The experiment tests something.

**Config → intent check.** No config field differs. **Confounds: NONE.**

**Cross-family check.** The 28 rungs span 14 proposer pools whose own
parameters (thinking level, modality, temperature, geometry, model family)
differ — deliberately, because each pool is its own ladder and K is compared
only *within* a pool. No cross-pool comparison is made at a fixed K, so the
pools' differences are strata, not confounds. This is the inventory's "a family
is a ladder only within one evaluation recipe" rule
(`results/k-ladder-2026-09-12/inventory.md` § 1).

## 3. Transmission verification

One config, so one row — checked against every error mode in the audit
discipline's table. Evidence is the **5-candidate smoke run** executed on
sapphire before this document was written
(`outputs/k-ladder-2026-09-12/smoke/`, 5/5 succeeded, 0 failed).

| Error mode | Check | Verdict |
|---|---|---|
| Image flag off | Text-only track: `examples` is `[]` and `include_example_images` is absent from the config. The smoke meta records `include_example_images: true, example_count: 0` — **byte-identical to the committed K = 5 rung's meta** (`outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/verified-v1-n5/run.meta.json`), so the flag means the same thing it meant for the carried verifier. Not an image experiment; no image payload is expected or sent | **PASS** |
| Temperature shadowed | No `--temperature` is passed. `run_pv.py`'s `--temperature` defaults to `None` (`scripts/run_pv.py:1513-1516`), and the smoke meta records `temperature: 0.0` from the config | **PASS** |
| Thinking level dropped | No `--thinking-level` is passed; the model is Flash, not Pro, so no MEDIUM floor applies (E40/E58). Smoke meta: `thinking_level: minimal` | **PASS** |
| Model version drift | No `--model` is passed. Smoke log: "Model `gemini-3-flash` not found; resolved to `gemini-3-flash-preview`" — the same resolution the carried verifier's metas record since April, and the model R1 fixes | **PASS** |
| Tile size mismatch | N/A to a verifier pass: crops are 150 × 150 from rasters, independent of the proposer's tile geometry. Verified anyway — smoke manifest `crop_dimensions: "150x150"`, `padding: 75` | **PASS** |
| Wrong tile set | The 28 unions' candidates resolve to **4 rasters and only 4**: `K-35-078-1_Lesovo` (11,229), `K-35-062-2_Rakovski` (8,867), `K-35-053-3_Elenovo` (8,658), `K-35-052-4_32635` (7,090) — the 4-map gold standard, summing to 35,844. **0 features lack a `source_tile`; 0 resolve to a raster that does not exist** | **PASS** |
| Wrong instruction file | `verify_adversarial.md`, SHA-256 `2518d5298d9b84bac6810bb0d11e59ef534c46853f65cb25dc1454af3497e15d` — **identical to the hash stamped by the August 3.7-screen verifier run** (`outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify/run.meta.json`, `system_instruction_hash`). The carried verifier's prompt has not moved | **PASS** |
| Example paths broken | No example images: `examples` is `[]`, `library_hash: "no_examples"` in the smoke meta. Nothing to resolve | **PASS (vacuous)** |
| Example image dimensions | Same — no example images | **PASS (vacuous)** |
| Agent model unpinned | The model is pinned in the config and stamped into every `run.meta.json` (`configuration.model`), together with `environment.git_commit`. No agent-spawning step is involved | **PASS** |
| **E33 raster-crop mode** (project-specific) | Smoke extraction: "From rasters: 5, From tiles (fallback): 0". The committed K = 5 manifests record `raster_crops == total_detections` on every pool, so this is the mode the carried cells used | **PASS** |

**Blockers from transmission: NONE.**

## 4. Preregistration alignment

| # | Requirement | What will be done | Verdict |
|---:|---|---|---|
| 1 | Crops from rasters | `run_pv.py extract` with `inputs/rasters` present (4 rasters on sapphire); smoke run took 5/5 from rasters | MATCHES |
| 2 | 150 × 150 crops | `--padding 75`, the value recorded in every committed pv-diag-384 and 3.7-screen crops manifest | MATCHES |
| 3 | Consensus union input | Each rung's input is `consensus-n<N>/consensus_t1.geojson`, built by `merge_passes.py --passes 1..N --sweep`. This is the same file *kind* the committed K = 5 rung consumed (`scale-4-optimal-487/verified-v1-n5/crops/candidate_manifest.json` names `consensus-n5/consensus_t1.geojson` as its `source_geojson`) | MATCHES |
| 4 | `gemini-3-flash` | unmodified config; no `--model` | MATCHES |
| 5 | Adversarial strategy | `verify_adversarial.md` | MATCHES |
| 6 | n = 1 | `--iterations` left at its default of 1 | MATCHES |
| 7 | MINIMAL thinking | unmodified config; no `--thinking-level` | MATCHES |
| 8 | T = 0.0 | unmodified config; no `--temperature` | MATCHES |
| 9 | In-sample operating points reported as such | The sweep-optimal point of each new rung is an in-sample optimum of the **E56 class**, exactly like the 21 committed `-opmax` cells, and R2 requires the carried point alongside it as the transfer tax. Both points will be reported per rung, and the E56 class named | **DELIBERATE DEVIATION — E56** |

Matches: **8**. Deliberate deviations: **1** (E56, already the registered
convention for this family). Undocumented deviations: **0**.

**Reverse direction.** Two parameters the preregistration does not mention are
set to non-default values, and both are accounted for:

- `--service-tier flex` — a billing tier, not an experimental parameter. It
  halves list price and adds 1–15 min of latency tolerance. Every cost column
  in the corpus is already on the flex basis
  (`docs/methodology/notation-key.md` § 8), so using it keeps this run
  comparable rather than making it exceptional.
- `--workers` — concurrency only. Never hard-coded in a study YAML
  (`docs/agent-guidance.md` § "Experiment Execution"); passed at the CLI.

## 5. Dry-run validation — the 5-candidate smoke run

Run on sapphire at 06:15 UTC, before this document was written, against the
first five features of the tier-A MINIMAL-text T 0.7 K = 1 union.

| Check | Expected | Actual | Verdict |
|---|---|---|---|
| Candidates found | 5 | 5 | PASS |
| Crops extracted | 5, all from rasters | 5 successful, 0 failed, 5 from rasters, 0 from tiles | PASS |
| Crop dimensions | 150 × 150 | `"150x150"` | PASS |
| Model resolution | `gemini-3-flash-preview` | resolved, logged | PASS |
| API calls succeeded | 5 | 5 verified, 0 failed | PASS |
| Rate-limit retries | 0 at 2 workers | 0 | PASS |
| `probabilities.json` written | yes | yes | PASS |
| `run.meta.json` written | yes, with model / thinking / temperature / instruction hash | yes, all four | PASS |
| Reference-image warnings | none | none | PASS |
| Score summary | plausible | mean 0.810, 4/5 above 0.5 | PASS |
| Cost | ≈ 5 × 0.000693 = US$0.0035 flex | US$0.006997 list → **US$0.0035 flex** (0.00070 per candidate) | PASS |

**Dry-run: PASS.** The per-candidate flex cost measured on 5 candidates,
0.00070, sits 1.0 % above the adopted constant 0.000693 and 0.3 % above the top
of the audit's measured spread (0.000684–0.000698) — a 5-item sample, so it is
reported for transparency and not treated as a new rate (warning 2 below).

## 6. Evaluation scope

| Check | Result | Verdict |
|---|---|---|
| Evaluation frame | `inputs/vectors/bounds/384/era2_b_intersection_bounds.geojson`, the board frame `era2-b-487` (487 tiles) — the frame the 21 committed `-opmax` cells of these same pools are scored on | PASS |
| Reference | `inputs/vectors/references/mounds-reference.geojson`, the Gold Standard curator reference, which has not moved (R4 clarification) | PASS |
| Calibration disjointness | `pv-diag ∩ calibration = 0` — the verifier never ran on the 20 calibration tiles, which are excluded from the 487-tile scope (E56, `protocol-errata.md:2014`). Zero overlap, established in the errata rather than re-derived | PASS |
| Corpus | 4-map gold standard; all 35,844 candidates resolve to the 4 GS rasters and nothing else (§ 3) | PASS |
| Output-path collisions | Every target pool holds `verified-v1-n5` and `verified-v1-n10` and **nothing else**; `verified-v1-n1` and `verified-v1-n3` are free in all 13 `pv-diag-384` pools, and `verify_k1` / `verify_k3` are free in the 3.7 screen's verifier tree. No committed probabilities can be overwritten | PASS |

## 7. Completeness — what this audit did not check

Stated rather than skipped.

- **The downstream sweep and scoring recipe** is not audited here. This audit
  covers the API spend; the operating-point sweep, the evaluation and the
  register rows are US$0 steps that follow, and their gate is the drift check
  and the board instrument, not this document.
- **Wall-clock and quota headroom** are estimated, not measured: at 20 workers
  and the smoke run's ≈ 2.2 s per call the 35,844 calls are of order 1–2 hours,
  and Gemini 3 Flash has no daily request cap
  (Pro 2K RPM / 8M TPM, Flash 20K RPM / 20M TPM, both unlimited RPD). Per-tier
  wall time will be read from the metas afterwards rather than predicted.
- **`--service-tier` is not verifiable from the output** — see warning 1.

### Warnings

1. **The verify path does not stamp the service tier anywhere in
   `run.meta.json`.** The smoke meta records `cost_basis: "list"`,
   `discount: 1.0`, `discount_reason: "no discount applied"` even though
   `--service-tier flex` was passed, and a search of the whole meta for
   `tier` / `flex` / `service` returns nothing. This reproduces the observation
   in `reports/r7-gaps-deltas-2026-09-11.md` § 2.3. **Consequence**: the audited
   flex figure is `list_total_cost_usd × 0.5`, applied by the accounting rather
   than read from the file, and the Phase 2 deltas report must say so. Not a
   blocker — the tier is in the launch command and the command is recorded — but
   it is the reason the run's own cost field cannot be cited unhalved.
2. **The smoke run's per-candidate cost is 0.00070**, marginally above the
   audited spread's ceiling of 0.000698. Five candidates is too small a sample
   to move a rate; the real per-tier rate will be computed from each tier's own
   metas and compared with 0.000693 in the deltas report.
3. **Two costing rows serve four inventory gaps.** Rows 27–28 (the 3.7 GS text
   screen) each answer two inventory gaps, because that family appears once per
   evaluation recipe (grid-common and `era2-b-487`) while reading one proposer
   pool (costing § 3). One verifier pass per rung is correct; the 28 ≠ 30
   arithmetic is not an omission.

## 8. Verdict

```text
=== PRE-LAUNCH AUDIT: K-ladder Phase 2, tiers A-D (H2 Condition B verifier) ===

1. PREREGISTRATION REQUIREMENTS: 9 extracted
2. CONFIG DIFF: 10 fields identical, 0 differ; input (the union) manipulated
   Confounds: NONE
3. TRANSMISSION CHECK: 12 error modes, 12 PASS
   Blockers: NONE
4. PREREGISTRATION ALIGNMENT: 8 matches, 1 deliberate deviation (E56),
   0 undocumented
5. DRY-RUN: PASS (5/5 candidates, US$0.0035 flex)
6. EVALUATION SCOPE: PASS
7. COMPLETENESS: 3 items not checked (named in section 7), 3 warnings

BLOCKERS: NONE
WARNINGS: 3 (service tier unstamped; 5-item rate 1 % high; 28 rows / 30 gaps)

OVERALL: READY TO LAUNCH
```

The launch command, per rung, is:

```bash
python scripts/run_pv.py extract \
    --proposer <pool>/consensus-n<N>/consensus_t1.geojson \
    --output-dir <verify-dir>/crops \
    --padding 75 \
    --tiles-dir inputs/tiles[_384_ov192 for the 3.7 pool]

python scripts/run_pv.py verify \
    --crops-dir <verify-dir>/crops \
    --verifier-config prompts/configs/verify_adversarial-text.json \
    --output-dir <verify-dir> \
    --mode realtime --workers <N> --service-tier flex
```

## Changelog

### 2026-09-12 — Original publication (K-ladder Phase 2 step 2)

Written after the 28 unions were built and before any tier's verifier pass was
launched. Sources read this session:
`~/.claude/skills/audit-config/SKILL.md` (the discipline);
`docs/methodology/preregistration/protocol-errata.md` E33, E37, E39, E56;
`prompts/configs/verify_adversarial-text.json`;
`scripts/run_pv.py` (`_get_api_key`, `_resolve_model_name`, the `verify`
argparse block); the committed `run.meta.json` of
`outputs/h11/pv-diag-384/flash-minimal-text-n30-t07/text-t0.7/verified-v1-n5`
and of `outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/verify`; the
committed `candidate_manifest.json` of three pools; and a 5-candidate smoke run
executed on sapphire for this audit. The API key is read by `config.py` via
`python-dotenv` from `GOOGLE_API_KEY` in the repository's `.env`
(`scripts/run_pv.py:1385`, `config.py:3-5,84`); sapphire's `.env` carries a
39-character value, confirmed present without printing it.
