# Temperature probe, 2026-10-07: does Gemini 3.7 Flash ignore `temperature`?

> **Last revised**: 2026-10-07 (original publication, Session 163). See
> [§ Changelog](#changelog) for revision history.

**Status: APPROVED by the PI (2026-10-07, "happy to let you test it, up to
$5"); written before launch.** Script:
`scripts/temperature_probe_2026_10_07.py` (tests:
`tests/test_temperature_probe.py`). Background:
`reports/google-temperature-notice-2026-10-07.md`.

## 1. Why

Google's notice of 2026-10-07 ("[Action Required] Update thinking_budget and
sampling parameters", read 2026-10-07) says: "Since Gemini 3.6 Flash,
sampling parameters have been set to default values, so custom values have
had no effect on model output. Soon with our upcoming models, requests that
include temperature, top_p, and top_k parameters will return an error." The
first sentence is about the past: if it holds, every Gemini 3.7 and 3.8 leg
logged at T 0.7 or T 0.0 ran at the model's default. This probe tests that on
the project's own requests, and reads each model's default, before Run B's
Stage 1 is lodged (its 3.7 arms send T 0.7).

## 2. Design

- **Candidates:** 300 drawn at random (seed 42) from the 791-candidate
  Gemini 3.7 text K = 5 union of the gold-standard screen
  (`outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/crops`), crops
  copied unchanged. The subset manifest records its draw (`probe_subset`); the
  union-provenance guard will flag it as disagreeing with its union, which is
  the point of a subset, so every leg passes `--allow-stale-manifest`.
- **Verifier:** `prompts/configs/verify_adversarial-text.json`, n = 1, on the
  Batch API — the path Run B will use, so the probe also shows whether 3.7
  still accepts a `temperature` field.
- **Legs**, all lodged together on one day (table below).

| Leg | Model | Thinking | Temperature |
|---|---|---|---|
| `g37-t0a`, `g37-t0b` | `gemini-3.7-flash` | low (as `verify_swap37`) | 0.0, twice |
| `g37-tmax` | `gemini-3.7-flash` | low | the model's `max_temperature` (expected 2.0) |
| `g3-t0a`, `g3-t0b` | `gemini-3-flash-preview` | minimal (config) | 0.0, twice |
| `g3-tmax` | `gemini-3-flash-preview` | minimal | its `max_temperature` |

Gemini 3 Flash predates 3.6, so it should honour temperature: it is the
positive control that shows the probe can see an effect.

- **Model defaults:** one `models.get` per model (`gemini-3-flash-preview`,
  `gemini-3.7-flash`, `gemini-3.8-flash`), saved to `models-get.json`. No
  tokens, no charge.

## 3. Prediction and decision rule (fixed before launch)

The statistic is the **agreement drop**: exact agreement of the two T 0.0
legs, minus the mean exact agreement of each T 0.0 leg with the T max leg,
with a paired bootstrap 95 % interval over candidates (10,000 resamples,
seed 42).

- **Control valid** if Gemini 3's drop has an interval excluding 0. If not,
  the probe cannot see temperature and says nothing about 3.7.
- **3.7 ignores temperature** (the notice holds for our requests) if, with the
  control valid, 3.7's interval includes 0 and its upper bound is below 0.10.
- **3.7 honours temperature** if its interval excludes 0 and its point drop is
  at least half of Gemini 3's.
- Anything else is **inconclusive** and goes back to the PI.
- A 400 error on any 3.7 leg is itself the answer to a different question:
  3.7 rejects the field, so Run B's 3.7 arms must omit it.

Expected, if the notice is right: 3.7 drop near 0; Gemini 3 drop large (the
project's single-pass Gemini 3 verifier at T 1.0 agreed with T 0.0 on 251 of
607 candidates, `reports/google-temperature-notice-2026-10-07.md` § 5).

## 4. Calls and cost

- 1,800 verifier calls (6 legs × 300) plus 3 `models.get` calls.
- Register rates on the same union: Gemini 3 US$0.56 for 791 candidates
  (US$0.00071 each), Gemini 3.7 about US$0.87 for 791 (US$0.0011 each)
  (`planning/modality-bridge-2026-10-07.md` § 5, Stage 2 table).
- Estimate: 900 × 0.00071 + 900 × 0.0011 = **about US$1.63**; doubled for
  longer outputs at T max, about US$3.3. **Cap US$5** (PI).

## 5. Commands (sapphire, repository root)

```bash
P=outputs/temperature-probe-2026-10-07
.venv/bin/python scripts/temperature_probe_2026_10_07.py prepare \
  --source-crops outputs/gemini37-screen-2026-08-28/verifier/g384_ov192_g37/crops \
  --out $P/crops --n 300 --seed 42
.venv/bin/python scripts/temperature_probe_2026_10_07.py models --out $P/models-get.json
# one detached launch per leg, e.g.:
.venv/bin/python scripts/run_pv.py verify --crops-dir $P/crops \
  --verifier-config prompts/configs/verify_adversarial-text.json \
  --output-dir $P/g37-t0a --mode batch --model gemini-3.7-flash \
  --thinking-level low --temperature 0.0 --allow-stale-manifest
.venv/bin/python scripts/temperature_probe_2026_10_07.py analyse \
  --root $P --out $P/analysis.json
```

Each leg is first built with `--dry-run` (the verifier's batch dry run
returns before any client is created, `scripts/run_pv.py:1102` against
`:1133`) and its request file checked for the intended temperature.

## 6. What it does not settle

- The probe tests the verifier seat at one prompt; the notice is about the
  model, so a null here is read as applying to 3.7 as a proposer too, by
  inference, not measurement.
- `models.get` gives the default's value, not proof that it was applied.
- It says nothing about 3.8 beyond its listed default.

## Changelog

### 2026-10-07 — Original publication (Session 163)

Written before launch, with the decision rule fixed in advance.
