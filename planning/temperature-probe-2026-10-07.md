# Temperature probe, 2026-10-07: does Gemini 3.7 Flash ignore `temperature`?

> **Last revised**: 2026-10-07 (follow-up result, § 8.5). See
> [§ Changelog](#changelog) for revision history.

**Status: DONE (2026-10-07). Verdict under the fixed rule: Gemini 3.7
ignores temperature; control valid (§ 7). Follow-up (§ 8.5): no residual
effect under its own fixed rule. Approved by the PI ("happy to let
you test it, up to $5"); §§ 1–6 were written before launch.** Script:
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

## 7. Result (2026-10-07, after the run)

Data: `outputs/temperature-probe-2026-10-07/` (`a79e960f4`): six legs,
300 of 300 candidates each, no failed items; audited cost **US$1.62**.

**Model defaults** (`models-get.json`): `gemini-3-flash-preview`,
`gemini-3.7-flash` and `gemini-3.8-flash` all list temperature 1.0 (maximum
2.0), top_p 0.95, top_k 64.

| Statistic | Gemini 3 Flash | Gemini 3.7 Flash |
|---|---:|---:|
| Exact agreement, T 0.0 against T 0.0 | 0.797 | 0.637 |
| Exact agreement, T 0.0 against T 2.0 (mean of two) | 0.385 | 0.613 |
| **Agreement drop** (95 % CI) | **+0.412 (+0.350, +0.475)** | **+0.023 (−0.030, +0.078)** |
| Mean \|Δp\|, T 0.0 / T 0.0 → T 0.0 / T 2.0 | 0.047 → 0.134 | 0.014 → 0.031 |
| Moves above 0.5, T 0.0 / T 0.0 → T 0.0 / T 2.0 (of 300) | 12 → 36–37 | 2 → 9 |

**Verdict under § 3's rule:** the control is valid (Gemini 3's interval
excludes 0), and Gemini 3.7's interval includes 0 with an upper bound below
0.10: **Gemini 3.7 ignores temperature on these requests.** Its T 0.0 legs
already disagree with each other on 36 % of candidates, as the 55-map
replicate found (63.5 % exact agreement), which fits a model sampling at its
default whatever is sent. 3.7 accepted T 2.0 without error.

**Exploratory, outside the fixed rule (flagged as a surprise).** On the
continuous measure, Gemini 3.7's mean |Δp| rises by +0.017 (paired bootstrap
95 % CI +0.004 to +0.032) from T 0.0 / T 0.0 to T 0.0 / T 2.0, about a fifth
of Gemini 3's rise (+0.087); 8 of the 10 large movers are candidates both
T 0.0 legs agreed on. This is one of several secondary statistics, chosen
after seeing the data. Two readings remain: temperature has a small residual
effect on 3.7 (Google's "no effect" overstates it), or the T 2.0 batch job
differed for another reason. A second T 2.0 leg (about US$0.33) would
separate them. It does not change the reading for Run B: the 3.7 arms ran,
and will run, at or near the default 1.0.

## 8. Follow-up: does the § 7 residual replicate? (written before launch)

**Approved by the PI, 2026-10-07** ("Go ahead and run: 'A second T 2.0 leg
(about US$0.33) would settle it' — I approve the minor cost (up to $1)").

### 8.1 Design

Two new Gemini 3.7 legs on the same 300 candidates, configuration and path as
§ 2, **lodged together**:

| Leg | Temperature | Why |
|---|---|---|
| `g37-tmax2` | 2.0 | the second T max leg the PI approved |
| `g37-t0c` | 0.0 | a same-time T 0.0 partner for it |

The T 0.0 partner is an addition to what the PI approved, inside the US$1 cap.
Without it, `g37-tmax2` would be lodged hours after the three original legs.
Any extra disagreement it showed could then be the lodging time, not the
temperature. With it, the new pair matches the original `t0a`/`t0b` pair: two
legs lodged together.

### 8.2 Statistics and decision rule

The statistic is mean |Δp| (per-candidate absolute probability difference),
the measure on which § 7's residual appeared. Contrasts use a paired bootstrap
over candidates (10,000 resamples, seed 42). Within each family of leg pairs,
the mean is taken per candidate first.

- **Primary (same-time replication):** |Δp|(`t0c`, `tmax2`) − |Δp|(`t0a`,
  `t0b`). Each side is a pair lodged together.
- **Pooled:** the mean over the six T 0.0 × T max pairs (`t0a`, `t0b`, `t0c` ×
  `tmax`, `tmax2`), minus the mean over the three T 0.0 × T 0.0 pairs. Both
  families hold the same share of cross-time pairs (two in three).
- **Residual effect** if both 95 % intervals lie above 0.
- **No residual effect** if both intervals include 0. In that case § 7's +0.017
  is read as job-to-job variation, and Google's "no effect" stands for these
  requests.
- **Inconclusive** otherwise.

Reported but outside the rule: the same pooled contrast on exact disagreement,
and the T max × T max pair against the T 0.0 × T 0.0 pairs.

**Power, stated in advance:** a single new pair is noisier than § 7's average
of two. A true residual of +0.017 might well leave the primary interval
crossing 0, which gives "inconclusive", not "no effect". The probe is sized to
the cap, not to this effect.

### 8.3 Calls and cost

600 verifier calls on `gemini-3.7-flash`, Batch API, n = 1, thinking low.
§ 7's 3.7 legs cost US$0.329 to US$0.331 each (audited, `run.meta.json` →
`cost_estimate.total_cost_usd`). Estimate **US$0.66; cap US$1** (PI).

### 8.4 Commands (sapphire)

```bash
P=outputs/temperature-probe-2026-10-07
.venv/bin/python scripts/run_pv.py verify --crops-dir $P/crops \
  --verifier-config prompts/configs/verify_adversarial-text.json \
  --output-dir $P/g37-tmax2 --mode batch --model gemini-3.7-flash \
  --thinking-level low --temperature 2.0 --allow-stale-manifest
# and the same with --output-dir $P/g37-t0c --temperature 0.0
.venv/bin/python scripts/temperature_probe_2026_10_07.py followup \
  --root $P --out $P/followup.json
```

### 8.5 Result (2026-10-07, after the run)

Data: `outputs/temperature-probe-2026-10-07/` (`9f19110b0`): `g37-tmax2` and
`g37-t0c`, 300 of 300 candidates each, no failed items, no safety blocks;
audited US$0.331 and US$0.329 (US$0.66 of the US$1 cap). Analysis:
`followup.json`.

| Contrast (mean \|Δp\|) | Point | 95 % CI |
|---|---:|---|
| **Primary**: (`t0c`, `tmax2`) − (`t0a`, `t0b`) | +0.0068 | −0.0059 to +0.0205 |
| **Pooled**: six T 0.0 × T 2.0 pairs − three T 0.0 × T 0.0 pairs | +0.0083 | −0.0002 to +0.0190 |
| Pooled, on exact disagreement (outside the rule) | +0.0267 | −0.0083 to +0.0622 |
| (`tmax`, `tmax2`) − three T 0.0 × T 0.0 pairs (outside the rule) | +0.0058 | −0.0039 to +0.0169 |

**Verdict under § 8.2's rule: no residual effect** (both intervals include 0).
The pooled interval only just does (lower bound −0.0002), and both point
estimates are positive at about half of § 7's +0.017. So a residual of up to
about 0.02 in mean |Δp| is not excluded, and none is shown.

**Where § 7's residual came from.** Pair by pair (`followup.json` → `pairs`),
every pair that includes the first T 2.0 leg, `tmax`, has the largest mean
|Δp|: 0.0307, 0.0318 and 0.0248 against the three T 0.0 legs, and 0.0218
against `tmax2`. Every other pair falls between 0.0144 and 0.0212, and that
includes the new T 2.0 leg against each T 0.0 leg (0.0180, 0.0190, 0.0212).
Moves above 0.5 follow the same pattern: 9, 9, 6 and 5 of 300 for `tmax`'s
pairs, 2 to 5 for the rest. § 7's +0.017 is mostly that one batch job, not
T 2.0 as such. Google's "no effect" holds for these requests to within the
interval above.

## Changelog

### 2026-10-07 — Follow-up result added (Session 163)

§ 8.5 added after the follow-up legs ran; §§ 1–8.4 unchanged. Data commit
`9f19110b0`.

### 2026-10-07 — Follow-up design added (Session 163)

§ 8 added before the follow-up legs were lodged; §§ 1–7 unchanged.

### 2026-10-07 — Result added (Session 163)

§ 7 added after the run; §§ 1–6 unchanged. Data commit `a79e960f4`.

### 2026-10-07 — Original publication (Session 163)

Written before launch, with the decision rule fixed in advance.
