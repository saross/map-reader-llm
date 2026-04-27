# Detector confidence opt-in flag — scoping doc (DO NOT IMPLEMENT)

**Created**: 2026-04-27
**Status**: Scoping only — no code changes in this document
**Cross-references**:

- Companion: `planning/detector-confidence-calibration-pilot.md` (deliverable b — vote-fraction proxy validation pilot)
- Working notes: Obs 269 (verifier miscalibration motivates a numeric detector confidence; `docs/notes/reflections/working-notes.md` line 12578) and Obs 277 (verifier-prompt variation does not rescue image-track miscalibration; line 13215)
- Trigger: this document is reviewed only if the calibration pilot fails its decision rule (Spearman ρ < 0.5 or non-monotonic), or independently if the project decides per-detection confidence is required for downstream work irrespective of pilot outcome

## Goal

An **opt-in** flag (working name `--emit-confidence` on the CLI; mirror as `emit_confidence: true` in proposer config / run-config YAML) that elicits a numeric confidence score per detection from the VLM proposer, analogous to the verifier's `mound_probability`. The flag must default to OFF; existing run scripts must be byte-identical in their default behaviour.

## Backwards-compatibility constraints (mandatory)

1. **Default OFF**. Existing scripts run with no flag must reproduce current outputs unchanged. CI verifies this by re-running a known manifest and diffing the output geojson byte-for-byte.
2. **Schema isolation**. The new field, when emitted, lives in a sibling property (`detector_confidence`) on the GeoJSON `Feature`, never replacing or shadowing existing properties. The existing `confidence: "high"` literal (currently set on every detection in `_save_geojson` → feature build, `scripts/4_detect_mounds_batch.py` line ~629) is preserved untouched. The numeric field has a distinct name to avoid silent type widening of the existing string.
3. **Config schema preservation**. The proposer config JSON (`prompts/configs/detect_brief-text.json` and family) gains an optional top-level boolean `emit_confidence` that defaults to false. Existing configs that omit the key behave as if it were false. No key in any existing config is renamed or repurposed.
4. **Affected entry points** (must all preserve byte-identical default behaviour):
   - `scripts/run_generalisation.py`
   - `scripts/4_detect_mounds_batch.py` (real-time + batch paths)
   - `scripts/run_pv.py` (downstream consumer of detection geojsons — verify it tolerates the optional field)
5. **Downstream consumers**. `scripts/lib_consensus.py` (`cluster_across_passes`), `scripts/8_analyse_proposer_consensus.py`, the verifier crop extraction in `run_pv.py extract`, and the PV evaluation pipeline must continue to operate when the field is absent **and** must propagate the field when present (so the confidence is preserved through clustering — typically by averaging or taking the max within a cluster).

## Approach options

### Option A — Prompt augmentation

Extend the proposer schema in `prompts/system-instructions/propose_brief.md` (and `propose_brief_v2.md`) to request:

```text
{
    "box_2d": [ymin, xmin, ymax, xmax],
    "label": "mound",
    "subtype": "burial_mound" | ...,
    "confidence": <float in [0, 1]>
}
```

The VLM self-reports per-detection confidence in the same JSON output.

**Implementation surface**:

- New prompt files: `propose_brief_confidence.md`, `propose_brief_v2_confidence.md` — copies of the originals with the schema and a 3–4 line scoring guide added (model after the verifier's `verify_adversarial.md` scoring guide at lines 53–58).
- New configs: `detect_brief-text_confidence.json` etc., or extend existing configs with `emit_confidence: true` and select the matched `_confidence` instruction file via a small dispatcher in `4_detect_mounds_batch.py` (the existing `instruction_file` config key already supports this kind of selection).
- Feature-build code change in `4_detect_mounds_batch.py` lines 597–634 (the `for det in detections:` loop): when `emit_confidence` is true, read `det.get("confidence")` (renamed to avoid clashing with the existing string) — likely simplest to rename the new field `detector_confidence` in the schema itself to keep prompt and code unambiguous. Add a numeric validity check (must be float in [0,1]; reject otherwise, log warning, set `None`).
- Result: an extra optional `detector_confidence: float` property on each output `Feature`. Default-OFF preserves the current `confidence: "high"` literal exactly.

**Effort**: **Small** — 1–2 days. Prompt copy + config additions + ~30-line code change in feature build + tests.

**Risk**: **Medium**.

- Self-reported confidence from VLMs is well-known to be poorly calibrated; the verifier already exhibits ECE 0.18–0.27 with a much more elaborate prompt (Obs 269, Obs 277). Asking the proposer to self-confidence-rate is unlikely to yield better calibration without verifier-style anti-confirmation prompting.
- Heavy quantisation risk: per Obs 269, the verifier collapses to ~13 distinct values across 1,028 candidates. The proposer with a brief prompt may collapse even more aggressively (e.g., 0.95 or 1.0 on every detection).
- Output token count increases by ~15–25% per detection (one extra numeric field per `box_2d` block). With detection counts of 10–100 per tile, this is generally below the existing 8192 cap but worth flagging.

### Option B — SDK logprobs

Enable `response_logprobs` (Gemini equivalent — capability check required, not all Gemini 3 surfaces expose this) on the API call to capture per-token log-probabilities. Derive a confidence score by aggregating logprobs over the JSON tokens that constitute each detection (e.g., the tokens for `subtype`, the `box_2d` coordinates, or the closing `}` of each detection block).

**Implementation surface**:

- `scripts/4_detect_mounds_batch.py` `gen_config` build (lines ~864–887): add `response_logprobs=True` and `logprobs=top_K` conditional on `emit_confidence`.
- Lines 391–413 (`client.models.generate_content` and metadata capture): extract logprobs from the response object; `extract_gemini_metadata` in `scripts/lib_llm_metadata.py` would need a parallel field. Logprobs may not be available on cached content, batch, or flex tier — verify on a single call before scoping further.
- Feature-build code (lines 597–634): index from each detection back to the JSON tokens that produced it, average or marginalise the logprobs, apply softmax/exp to derive a pseudo-probability. This is fragile because the JSON token alignment is not guaranteed to be deterministic across model versions.

**Effort**: **Large** — 1–2 weeks. Capability check + token-alignment infrastructure + model-version regression risk + needing a calibration pilot of its own (logprob-derived scores are not probabilities, only proxies).

**Risk**: **High**.

- Capability uncertainty: Gemini 3 Flash's `response_logprobs` support is not confirmed in this codebase (no occurrences of `response_logprobs`, `logprobs`, or `top_logprobs` in `scripts/lib_verifier.py`, `scripts/4_detect_mounds_batch.py`, `scripts/lib_batch_api.py`).
- Batch API and context-cache compatibility uncertain.
- Token-to-detection alignment fragile and hard to maintain.
- Cost: logprobs typically increase response payload size 2–5×.

### Option C — Multi-pass within-call ensemble

K=N within a single API call (multi-sample at temperature) to derive agreement-rate within one call, returning per-detection consensus counts directly. Equivalent to deliverable (b)'s vote-fraction proxy but folded into a single API hit.

**Implementation surface**:

- Requires Gemini API support for `n` (number of candidate completions) at the per-call level. Current SDK call shape (`client.models.generate_content(...)` with single-completion return) does not appear to expose this.
- If supported, the prompt would need a deterministic clustering spec post-hoc to merge the N completions into a confidence signal — the existing across-pass clustering in `lib_consensus.py` would have to be reimplemented within a single response.

**Effort**: **Large** — model-support uncertain; even if supported, duplicates infrastructure already implemented for cross-call K passes.

**Risk**: **High** — capability uncertainty, output-token blowup (N× the current per-call output), no clear advantage over existing K-pass approach.

## Recommendation

**Defer all three options**. Rationale:

1. **Option C** has the worst effort/information-gain ratio: it replicates K-pass infrastructure that already exists, with capability uncertainty.
2. **Option B** is high-effort and high-risk; logprob-derived confidence is itself a behavioural proxy that would itself require its own calibration pilot. The verifier already shows ECE 0.18 even with elaborate adversarial prompting (Obs 277); logprob-derived signals are unlikely to be better-calibrated than vote-fraction without substantial calibration work.
3. **Option A** is the cheapest and most parallel to the verifier's `mound_probability` mechanism — but the same calibration concerns apply (Obs 269 verifier ECE 0.27 with a ten-paragraph adversarial scoring rubric; the proposer with three lines of guidance would likely calibrate worse). The information-gain relative to vote-fraction is unclear without empirical evidence.

The recommended path is:

- **First**: run the calibration pilot in `planning/detector-confidence-calibration-pilot.md` (deliverable b). It is zero-cost and produces decisive evidence on the soundness of vote-fraction as a proxy.
- **If the pilot passes**: report vote-fraction in the paper. Flag Option A as future work but do not implement.
- **If the pilot fails**: open Option A as the lowest-cost mitigation, with a tight calibration sub-pilot baked in (small K=5 calibration run on the 4-map gold-standard corpus comparing self-reported `detector_confidence` against ground truth, target Spearman ρ ≥ 0.7 against TP-rate). Total budget ≤ $20 at flex-tier text-mode rates (rates from `scripts/run_generalisation.py` `_MODE_RATES`).
- **Options B and C remain deferred** indefinitely until either Gemini SDK capability lands cleanly or another use case justifies the engineering cost.

## Cost implications (flag for cost-estimator)

The cost-estimator at `scripts/run_generalisation.py` `_estimate_cost` is now mode-aware (image vs text) per the recent refactor referenced in `_MODE_RATES`. Each option's flag-on cost multiplier should be added to that table when (if) implemented:

| Option | Output-token multiplier | Input-token impact | Notes |
|---|---|---|---|
| A — Prompt augmentation | ~1.15–1.25× | +20–40 input tokens (scoring guide) | Extra `detector_confidence` field per detection |
| B — SDK logprobs | ~2–5× response payload | Negligible input | Logprobs are returned alongside generated tokens; payload grows substantially |
| C — Within-call N-sample | ~N× output | 1× input | Effectively N× the output cost; equivalent to running K passes outside the call but in one bill |

When any option is implemented, the implementer must:

1. Add a new key to `_MODE_RATES` (e.g. `"text-confidence": {...}` or a multiplicative adjustment factor `confidence_multiplier`) so `_estimate_cost` continues to give an accurate pre-launch dollar figure.
2. Update `scripts/run_generalisation.py` `_detect_proposer_mode` to recognise the confidence-on variants.
3. Capture an empirical recalibration of the per-tile-pass rate on the first 50–100 tiles, mirroring the methodology used for the existing image and text rates.

## Affected files (read-only audit, no edits)

- `scripts/4_detect_mounds_batch.py` — feature-build loop (lines 597–634) for Option A field addition; `gen_config` build (lines 864–887) for Option B logprobs; both require an `emit_confidence` config check at config-load time (lines 706–745).
- `scripts/run_generalisation.py` — `_estimate_cost`, `_detect_proposer_mode`, plus run-config schema (`proposer:` block parsing) for any new opt-in flag; intent guard via `lib_experiment_intent.run_launch_checks` (lines 956–966) needs the new flag added to its diff scope.
- `scripts/run_pv.py` — extract / verify subcommands as downstream consumers of the detection geojsons; must tolerate optional `detector_confidence` and propagate it.
- `scripts/lib_consensus.py` — `cluster_across_passes` and `generate_consensus_gdf` (lines ~168–328) for confidence propagation through clustering (e.g., mean confidence per cluster, or the max).
- `prompts/system-instructions/propose_brief.md`, `propose_brief_v2.md` — prompt augmentation for Option A (sibling files, do not edit existing).
- `prompts/configs/detect_brief-text.json` and family — config schema additions (new optional key `emit_confidence`); existing configs untouched.
- `scripts/lib_llm_metadata.py` — `extract_gemini_metadata` and `estimate_cost` (cost-rate update for any chosen option).
- `tests/` — new regression test asserting flag-OFF byte-identity on a small fixture manifest.

## Implementation gates

If/when this work is undertaken:

1. **Gate 1 — capability check**. For Options B and C, prove SDK support on a single tile call before committing further effort.
2. **Gate 2 — backwards-compat regression test**. Flag-off run on a fixture manifest must produce a geojson byte-identical to the pre-change baseline. CI must enforce this.
3. **Gate 3 — calibration sub-pilot**. The chosen option must clear Spearman ρ ≥ 0.7 against TP rate on a 4-map gold-standard pilot before being promoted as a paper-reportable signal.
4. **Gate 4 — cost-estimator update**. The new flag-on rate must be captured empirically and added to `_MODE_RATES`. A pre-flight cost estimate that ignores the flag is unacceptable.
