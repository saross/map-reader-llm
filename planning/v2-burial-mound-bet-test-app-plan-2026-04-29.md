# Inspection-app plan — v2 burial-mound reclassification bet test

_Created 2026-04-29 — Claude Code (Opus 4.7) for Shawn Ross. Plan-only; no code yet._

## 1. Executive summary

Build a small Streamlit inspection app at `scripts/v2_burial_mound_bet_review.py` that walks
Shawn through the **177 false-positive (FP) candidates** that the v2 closed-list FP-classifier
reclassified into one of the four burial-mound categories
(`burial-mound`, `settlement-mound`, `triangulation-point-on-burial-mound`,
`benchmark-on-burial-mound`), so he can record a per-candidate verdict that resolves the
2026-04-29 bet over the true review-error rate.

The app mirrors the rendering pipeline of the existing review UI
(`scripts/review_candidates.py`), reusing live-raster crop rendering, the magenta concentric
tolerance rings, and the keyboard-driven verdict capture pattern. Verdicts persist to a CSV
under `results/55maps-fp-classification/v2-burial-mound-bet-test/verdicts.csv`; resume support
is keyed on `(run, candidate_id)` because `candidate_id` alone is non-unique across runs.

**Framework recommendation: Streamlit**, for parity with the reviewer's existing muscle memory
and zero net new tool surface. **Estimated build effort: ~250-350 lines of code, ~1-2 h to
implement and test.** **Estimated user wall time to review 177 crops: 60-90 minutes** at the
~20-30 s per crop pace observed in prior review sessions.

## 2. The bet

In the 2026-04-29 v2 FP-classification re-run (commit `ec21c8ef`), the v2 closed list
(with `burial-mound`, `settlement-mound`, `triangulation-point-on-burial-mound`,
`benchmark-on-burial-mound` added) reclassified **177 / 1,119 (15.8 %)** of FPs into the four
burial-mound categories — dominated by `settlement-mound` (117 = 10.5 % of all FPs).

Shawn argues his digitisation error rate is well below 2 %; the agent estimates the true
review-error rate at 1-3 %, with the bulk of the 15.8 % attributable to v2 prompt bias and
vocabulary leakage. The two parties have agreed to manual re-review of the 177 crops to
adjudicate.

- **If review-error rate < 2 %** (i.e., < ~3 of 177 reclassifications are genuine reviewer
  errors): the model owes Shawn a deep-dive analytical sweep on a topic of his choosing.
- **If ≥ 2 %**: Shawn owes the model a single-line tea-acknowledgement next session.

The app's job is to produce the data on which that 2 % gate is decided.

## 3. Inputs

### 3.1 Per-FP record source

`results/55maps-fp-classification/fp_classifications.json` — list of 1,119 dicts. Verified
schema (every key present in every row of the 177-record subset):

| Field | Type | Notes |
|---|---|---|
| `run` | str | One of `T0.3`, `T0.7`, `image`, `text-MIN` |
| `candidate_id` | str | Per-run identifier; non-unique across runs |
| `map_name` | str | e.g., `K-35-051-3` |
| `x`, `y` | float | UTM zone 35 N (EPSG:32635) centroid |
| `source_tile` | str | e.g., `K-35-051-3_x0_y1680.png` |
| `category` | str | v2 closed-list label — filter to mound categories |
| `raw_category` | str | Pre-normalisation model output |
| `confidence` | float | 0.0-1.0; mound-category records are 0.90-0.95 (mean 0.94-0.95) |
| `rationale` | str | Single-sentence model rationale; **always non-empty** for mound rows |
| `success` | bool | All 177 mound rows have `success: true` |
| `error` | str | Empty for mound rows |
| `input_tokens`, `output_tokens` | int | Cost-accounting only — not displayed |

**Subset filter for the bet test:**

```python
mound_cats = {
    "burial-mound", "benchmark-on-burial-mound",
    "triangulation-point-on-burial-mound", "settlement-mound",
}
candidates = [r for r in fp_classifications if r["category"] in mound_cats]
# yields exactly 177 records:
#   settlement-mound:                    117
#   triangulation-point-on-burial-mound:  37
#   burial-mound:                         23
#   benchmark-on-burial-mound:             0
```

### 3.2 Review-CSV cross-reference

For each candidate, the corresponding row in the run's `human-review-multi-buffer.csv` carries
the user's original review verdict. Header (verified):

```text
candidate_id, verifier_probability, human_label, symbol_type, source_tile,
map_name, x, y, buffer_metres, timestamp
```

Run-to-CSV map (paths verified to exist):

| run label | review-CSV path |
|---|---|
| `T0.3` | `results/55maps-text-high-t0.3-generalisation/human-review-multi-buffer.csv` |
| `T0.7` | `results/55maps-text-high-generalisation/human-review-multi-buffer.csv` |
| `image` | `results/55maps-image-generalisation/human-review-multi-buffer.csv` |
| `text-MIN` | `results/55maps-text-min-generalisation/human-review-multi-buffer.csv` |

For every mound-category candidate, expect `human_label == "not_mound"` in the matching CSV
row — this is the original verdict the v2 classifier is now disputing. Surfacing this cell in
the UI makes the contradiction explicit.

### 3.3 Rendering pipeline

`scripts/55maps-fp-classify.py:render_crop()` (lines 384-434) is the function the v2
classifier used. Verbatim contract:

- 150 m metric window, centred on `(x, y)`.
- `best_raster_for_point()` picks the source TIF from `inputs/rasters/Russian1981_32635/`,
  preferring the raster with most non-black content at the candidate location (handles
  trapezoidal sheet edges).
- LANCZOS-upscaled to 768 px display size for legibility at the ~5 m/px native resolution.
- `boundless=True` so edge-of-sheet candidates still render full-size.

The richer `render_candidate_context_crop()` in `scripts/review_candidates.py` (400 m crop,
600 px display, magenta concentric rings at 50/75/100/125/150 m) is what Shawn already uses
for review work. **Decision** (see §5): default to the richer 400 m / ringed crop because the
extra context helps a fresh-eyes review, but expose a sidebar toggle to switch to the exact
150 m / 768 px crop the v2 classifier saw — useful when adjudicating "is the model
hallucinating from a feature outside the FP-classifier's field of view?".

## 4. Architecture

### 4.1 Framework — Streamlit (recommended)

| Option | Pros | Cons |
|---|---|---|
| **Streamlit** | Reuses `review_candidates.py` rendering helpers; existing reviewer muscle memory; `st.cache_data` already wraps the crop-rendering function; image + buttons + sidebar are first-class primitives | Heavier than strictly needed; cold-start lag (~1-2 s) |
| Jupyter widget (ipywidgets) | Interactive in notebook context; integrates with downstream analysis cells | Reviewer would need to keep a notebook session live; resume after kernel restart is fragile |
| Plain HTML + local Flask | Light, no Streamlit dependency | Need to write the routing, form handling, asset serving — net new code with no existing parallel in this repo |
| CLI with image preview (e.g., `feh` / `kitty icat`) | Fastest keyboard input; no browser | Image pre-rendering required; viewing on remote workstations awkward; cannot easily display rationale + metadata alongside |

**Streamlit wins** on parity with the existing reviewer workflow. The `review_candidates.py`
rendering helpers (`_collect_raster_bounds`, `_best_raster_for_point`,
`render_candidate_context_crop`) can be imported as-is. Verdict capture via
`st.button` plus `st.session_state` for keyboard shortcuts.

### 4.2 Crop rendering — live, not pre-rendered

Live re-rendering on the fly per candidate, mirroring what the v2 classifier did:

- The existing `render_candidate_context_crop()` is `@st.cache_data` decorated, so a re-visit
  to a candidate is free.
- 177 candidates × ~0.5 s first render = ~90 s of cumulative render time — invisible to the
  reviewer because rendering happens between candidate selections, not at startup.
- Pre-rendering 177 PNGs would save ~0.5 s per first-visit but adds a build step, an
  archive directory of stale crops, and a divergence risk if the rendering function later
  changes. Not worth the complexity for 177 records.

### 4.3 File layout

```text
scripts/
  v2_burial_mound_bet_review.py       # NEW — the inspection app
results/55maps-fp-classification/
  v2-burial-mound-bet-test/           # NEW — created on first save
    verdicts.csv                      # NEW — per-candidate verdicts
    summary.md                        # NEW — auto-written on completion
```

The script imports from `scripts/review_candidates.py` rather than duplicating the
rendering helpers (single source of truth; if `review_candidates.py` changes, the bet-test
app picks up the change — desirable here because we want visual parity with the reviewer's
existing tools).

## 5. UI design

### 5.1 Wireframe (text)

Mirrors the layout in `docs/streamlit-manual-correction-app.png`:

```text
┌─────────────────────────────────────────────────────────────────┐
│ v2 Burial-Mound Bet Test — Manual Re-review                     │
│ Progress: 23 / 177 reviewed   ●●●●●○○○○○○○○○○○○○ 13 %           │
├─────────────────────────────────────────────────────────────────┤
│ Candidate 24 of 177  •  run = T0.3  •  candidate_id = 281       │
│ map = K-35-051-3  •  source_tile = K-35-051-3_x0_y1680.png      │
│ centroid = (336503.2, 4697170.2)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌────────────────────────────────────────────────────┐        │
│   │                                                    │        │
│   │           [400 m crop with magenta rings]          │        │
│   │              50 / 75 / 100 / 125 / 150 m           │        │
│   │                                                    │        │
│   └────────────────────────────────────────────────────┘        │
│                                                                 │
│   v2 verdict:  settlement-mound  (confidence 0.95)              │
│   v2 rationale: "The central feature is a distinct black        │
│      square with a central dot and outer hachures, which is     │
│      the standard Soviet symbol for a settlement mound or       │
│      tell."                                                     │
│   Original review label:  not_mound  (the v2 model disputes)    │
├─────────────────────────────────────────────────────────────────┤
│ Your verdict (press 1 / 2 / 3 / 4):                             │
│                                                                 │
│  [1] real_mound_my_error      — I clicked not_mound by mistake  │
│  [2] v2_overclaim             — model is wrong, my call stands  │
│  [3] edge_case_ambiguous      — reasonable people disagree      │
│  [4] v2_correct_review_correct — both right; semantic distinct  │
│                                                                 │
│  Optional note: [_______________________________________]       │
│                                                                 │
│  [< Prev]            [Skip]            [Submit + Next >]        │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Sidebar controls

- **Toggle: 150 m / 768 px crop view** (off by default) — render the exact image the v2
  classifier saw, no rings. Useful for adjudicating prompt-bias arguments.
- **Toggle: Re-review already-judged candidates** (off by default) — when on, the queue
  iterates over verdicted rows so the reviewer can revise. Default off so the queue is the
  un-judged subset.
- **Filter by mound subtype** — `all / settlement-mound / burial-mound /
  triangulation-point-on-burial-mound / benchmark-on-burial-mound`. Useful for
  Shawn to batch-review the 117 settlement-mound rows in one sitting since
  the cognitive task is the same across that subgroup.
- **Show verdict tally** — running breakdown of verdicts so far (live, updates on each
  submit).
- **Optional: surface a random sample of agreed `not_mound` candidates** (see §5.4).

### 5.3 Verdict input scheme — keyboard shortcuts

Speed matters at 177 crops. Streamlit's native keyboard handling is limited but workable
via `st.button` plus an `st.text_input` "command bar":

- **Primary scheme**: numbered buttons `1 / 2 / 3 / 4` plus a "Submit" button. Each verdict
  button submits-and-advances in one click (no separate Submit press).
- **Optional power-user scheme**: a small `st.text_input` at top labelled "shortcut" — typing
  `1`, `2`, `3`, `4`, then Enter, advances. Saves the mouse round-trip if Shawn finds the
  click pattern slow.
- **Navigation**: `[< Prev]` re-displays the previous candidate (read-only — to revise, use
  the sidebar "Re-review" toggle and resubmit, which overwrites the existing row). `[Skip]`
  advances without writing — useful if Shawn wants to come back to a hard call.

The four verdict labels (verbatim per spec):

1. `real_mound_my_error` — user's review-pass label was wrong (real mound, clicked not_mound)
2. `v2_overclaim` — v2 is wrong; user's `not_mound` stands
3. `edge_case_ambiguous` — reasonable people could disagree
4. `v2_correct_review_correct` — both right; the v2 label is semantically a feature the user
   correctly declined to call a project burial mound (e.g., the model identified a
   `settlement-mound` / tell accurately _as_ a feature, but settlement-mounds are not in
   scope for the project's burial-mound corpus)

### 5.4 Optional: blinded calibration sample (sanity check)

A nice-to-have, off by default behind a sidebar toggle: surface a small random sample (~10)
of `human_label == "not_mound"` candidates that v2 _also_ classified as a non-mound category
(i.e., agreed cases) interleaved into the queue. The reviewer is told the queue contains a
calibration sample but not which rows. The verdict captured for those rows is logged but
held back from the headline 177-row review-error-rate computation, and used as an
inter-rater calibration signal: if Shawn flips on those, that's a noise estimate.

**Default: off.** Adds complexity and turns a 90-minute task into a 100-minute task. Worth
shipping the toggle in case Shawn wants the calibration data, but the bet itself is
adjudicated on the 177 mound-category records alone.

## 6. Resume + persistence

### 6.1 Verdicts CSV format

Path: `results/55maps-fp-classification/v2-burial-mound-bet-test/verdicts.csv`.

```text
run,candidate_id,verdict,note,timestamp
T0.3,281,v2_correct_review_correct,"settlement mound, not a burial mound — out of scope",2026-04-29T22:14:03+00:00
T0.3,233,v2_overclaim,"reads as a building cluster",2026-04-29T22:14:31+00:00
...
```

| Column | Type | Notes |
|---|---|---|
| `run` | str | From `fp_classifications.json` |
| `candidate_id` | str | From `fp_classifications.json` |
| `verdict` | str | One of the four spec labels (or `skipped` if Skip was clicked) |
| `note` | str | Optional free-text; quoted-CSV-safe |
| `timestamp` | str | ISO-8601 UTC, written at submit time |

### 6.2 Resume mechanism

1. On startup, load `verdicts.csv` if it exists into a `dict[(run, candidate_id) -> row]`.
2. The candidate queue iterates over the 177 mound-category records in the order
   `(run_alpha_order, descending_confidence, candidate_id)` so the queue order is stable
   across sessions.
3. Skip any candidate whose `(run, candidate_id)` is already keyed in the loaded dict
   **and** the recorded verdict is not `skipped`. Skipped candidates remain in the queue
   so Shawn cycles back to them.
4. The "current candidate" is the first un-judged-and-not-skipped candidate; the
   second pass picks up the skipped ones at the end.
5. Submit appends a row to `verdicts.csv` (open in append mode, fsync after each write so a
   crash mid-session loses at most the in-flight row).

### 6.3 Matching key — `(run, candidate_id)`, not `candidate_id` alone

Verified empirically: across the 177 mound-category subset, `candidate_id` alone happens to
be unique, but across the full 1,119 FP set it is **not**. The composite key `(run,
candidate_id)` is unique on both subsets and on the full FP table. Standardise on the
composite key so the script is correct on the full population if ever extended to the other
942 non-mound FPs.

## 7. Final-report scheme

A separate post-review summary, run on the verdicts CSV after the queue is empty
(the app calls this automatically once all 177 are judged; it can also be re-run
manually as `python scripts/v2_burial_mound_bet_review.py --summary`):

### 7.1 Verdict breakdown table

```text
Verdict                       count  share of 177
real_mound_my_error           ?      ? %
v2_overclaim                  ?      ? %
edge_case_ambiguous           ?      ? %
v2_correct_review_correct     ?      ? %
skipped                       ?      ? %
total                         177    100 %
```

### 7.2 Review-error rate computation

The headline metric on which the bet is settled:

```text
review_error_rate = real_mound_my_error / total_FPs_in_corpus
                  = real_mound_my_error / 1,119
```

Reported alongside the more conservative bound:

```text
review_error_rate_inclusive = (real_mound_my_error + edge_case_ambiguous) / 1,119
```

Both rates are computed against the **full 1,119 FP corpus**, not just the 177 reclassified
candidates, because the 177 are the only candidates flagged by v2 as plausibly mound — the
other 942 are accepted at face value as `not_mound` (with a small noise floor that the
agreed-cases calibration sample, if used, would estimate).

### 7.3 Bet adjudication

| Rate | Interpretation |
|---|---|
| `< 2 %` (< 23 of 1,119) | Shawn wins — agent owes a deep-dive analytical sweep |
| `≥ 2 %` (≥ 23 of 1,119) | Agent wins — Shawn owes a single-line tea acknowledgement |

23 of 177 reclassifications need to be `real_mound_my_error` for the rate to land at
exactly 2 %. The agent's prediction of 1-3 % corresponds to 11-34 such verdicts.

### 7.4 Per-subtype slice

Also report the breakdown by v2 subtype (settlement-mound / burial-mound /
triangulation-point-on-burial-mound) to surface whether one subtype dominates the
review-error pool — informative for the broader interpretation question even when the bet
itself is settled by the aggregate rate.

### 7.5 Output: `summary.md`

Auto-written to `results/55maps-fp-classification/v2-burial-mound-bet-test/summary.md`:

- The two tables above.
- A timestamp of the review session and the verdicts-CSV row count.
- A link back to the v2 `report.md` so future readers can trace from the headline 15.8 %
  finding through to the resolved review-error rate.

## 8. Implementation effort estimate

| Component | Estimated LOC |
|---|---:|
| Argparse + path setup + module imports | 30 |
| Load `fp_classifications.json` + filter to mound categories | 25 |
| Cross-reference loader (review-CSV row per candidate) | 40 |
| Streamlit UI assembly (sidebar + main pane + buttons) | 80 |
| Render-call wiring (import from `review_candidates.py`) | 20 |
| Verdict capture + CSV append + resume key handling | 40 |
| Final-summary writer (`summary.md`) | 30 |
| Header docstring + UK English comments + edge-case handling | 30 |
| **Total** | **~295 LOC** |

**Build wall time**: ~1-2 hours, including a small smoke test against the first 3-5
candidates and a markdownlint / ruff pass.

**User wall time**: ~60-90 minutes for 177 candidates at 20-30 s per call. The crop renders
are ~0.5 s on a warm cache; per-call cognitive load is similar to the existing review pass
(centre-feature identification on a familiar UI), so the throughput estimate is anchored on
session-77/78 review pace.

## 9. Pre-launch checklist

1. Confirm `streamlit` is in the active venv (it is — `review_candidates.py` requires it).
2. Smoke-test the rendering import: `from scripts.review_candidates import
   render_candidate_context_crop` resolves without error.
3. Confirm the four `human-review-multi-buffer.csv` paths exist (verified during
   plan-writing — all four present).
4. Confirm `inputs/rasters/Russian1981_32635/` is populated with the expected GeoTIFFs
   (verified — sample `K-35-042-3.tif`, `K-35-050-4.tif`, `K-35-051-3.tif` etc. present).
5. `mkdir -p results/55maps-fp-classification/v2-burial-mound-bet-test/` before first
   submit (the app creates this on demand, but pre-creating avoids the first-write race).

## 10. Open questions for Shawn

1. **Crop view default**: the plan recommends defaulting to the 400 m / ringed view
   (richer context, parity with `review_candidates.py`) with a sidebar toggle to flip to
   the 150 m / 768 px view the v2 classifier actually saw. **Confirm: is the 400 m view the
   right default for this task, or do you want the 150 m view as default?** A reasonable
   counter-argument for 150 m as default is that it pins the review to "what could the
   model see?", removing the "but the model didn't see that" objection from the verdict.
2. **Calibration sample (§5.4)**: ship the toggle, default off?
3. **`v2_correct_review_correct` semantics**: the plan reads this as "model labelled the
   feature accurately as something other than a project burial mound (e.g., a settlement
   mound / tell), and the user correctly declined to count it as a mound under the
   project scope". **Is that the intended interpretation, or did you have something
   narrower in mind?** A second reasonable reading is "the model picked a burial-mound
   subtype that _is_ a mound but not the project's target subtype" — under that reading,
   verdict (4) would only fire on `settlement-mound` rows, never on the other three
   subtypes. Worth clarifying before launch because the headline rate depends on the
   split between (1) and (4).
4. **Bet adjudication denominator**: §7.2 reports the rate against the full 1,119 FP corpus
   (the conservative read). **Confirm**: that's the denominator you want, vs. against the
   177 reclassifications alone (which would put the threshold at 4 of 177 ≈ 2 %)?
5. **Skipped candidates at end-of-queue**: the plan re-cycles skipped candidates after the
   first pass. **Confirm**: that's preferred to leaving them un-judged in the verdicts CSV
   and adjudicating without them?
