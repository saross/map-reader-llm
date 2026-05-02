# Inspection-app plan — v2 burial-mound reclassification bet test

> **⚠️ SUPERSEDED 2026-05-01.** This planning document is preserved
> for historical reference. The work it describes was executed in
> Session 81 (bet-test app built and run end-to-end; final tally
> 0/177 review errors; Obs 312); see
> `planning/paper-writeup-continuity.md` §"Session 81 closure roll-up"
> (Item 13 row in the Items 1–16 status table) and Obs 312 in
> `docs/notes/reflections/working-notes.md` for the current state.
> Do not act on items in this file as if they are pending.

_Created 2026-04-29 — Claude Code (Opus 4.7) for Shawn Ross._
_Status: **APPROVED — ready for implementation** (open questions resolved 2026-04-29; see §10)._

## 1. Executive summary

Build a small Streamlit inspection app at `scripts/v2_burial_mound_bet_review.py` that walks
Shawn through the **177 false-positive (FP) candidates** that the v2 closed-list FP-classifier
reclassified into one of the four burial-mound categories
(`burial-mound`, `settlement-mound`, `triangulation-point-on-burial-mound`,
`benchmark-on-burial-mound`), so he can record a per-candidate verdict that resolves the
2026-04-29 bet over the true review-error rate.

The app mirrors the rendering pipeline of the existing review UI
(`scripts/review_candidates.py`), reusing live-raster crop rendering and the keyboard-driven
verdict capture pattern. The default crop view is the **exact 150 m / 768 px window the v2
classifier saw** (no rings), so the reviewer judges the same image the model judged; a sidebar
toggle exposes the richer 400 m ringed view from `review_candidates.py` when extra context
helps. Verdicts persist to a CSV under
`results/55maps-fp-classification/v2-burial-mound-bet-test/verdicts.csv`; resume support is
keyed on `(run, candidate_id)` because `candidate_id` alone is non-unique across runs.

**Bet adjudication denominator: 1,675** — the `not_mound` corpus the user actually reviewed
and the v2 classifier inspected (not the full 3,492-tile corpus, which would be too generous,
and not the 177 reclassifications alone, which would be too strict). The 2 % review-error
threshold thus equates to **34 errors among the 177 reclassifications (≈ 19 % of
reclassifications)** — the bet is settled by counting `real_mound_my_error` verdicts and
comparing to that threshold.

**Framework recommendation: Streamlit**, for parity with the reviewer's existing muscle memory
and zero net new tool surface. **Estimated build effort: ~305 lines of code (range
~280-330), ~1-2 h to implement and test.** **Estimated user wall time to review 177 crops:
60-90 minutes** at the ~20-30 s per crop pace observed in prior review sessions.

## 2. The bet

In the 2026-04-29 v2 FP-classification re-run (commit `ec21c8ef`), the v2 closed list
(with `burial-mound`, `settlement-mound`, `triangulation-point-on-burial-mound`,
`benchmark-on-burial-mound` added) reclassified **177 / 1,119 (15.8 %)** of FPs into the four
burial-mound categories — dominated by `settlement-mound` (117 = 10.5 % of all FPs).

Shawn argues his digitisation error rate is well below 2 %; the agent estimates the true
review-error rate at 1-3 %, with the bulk of the 15.8 % attributable to v2 prompt bias and
vocabulary leakage. The two parties have agreed to manual re-review of the 177 crops to
adjudicate.

The bet is settled against a denominator of **1,675** — the `not_mound`-labelled corpus the
user actually reviewed and the v2 classifier inspected (see §7.2 for why this denominator was
chosen over 3,492 or 177).

- **If review-error rate < 2 %** (i.e., **< 34 `real_mound_my_error` verdicts** among the 177
  reclassifications, which is < 19 % of reclassifications): the model owes Shawn a deep-dive
  analytical sweep on a topic of his choosing.
- **If ≥ 2 %** (≥ 34 `real_mound_my_error` verdicts): Shawn owes the model a single-line
  tea-acknowledgement next session.

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
for review work. **Decision** (resolved 2026-04-29; see §5 + §10): default to the **exact
150 m / 768 px crop the v2 classifier saw** (no rings) so the reviewer adjudicates the same
image the model adjudicated — this pins the bet to "what could the model see?" and removes
the "but the model did not see that" objection. Expose a sidebar toggle to switch to the
richer 400 m ringed view from `review_candidates.py` when extra spatial context aids a
borderline call.

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
│   │      [150 m crop, 768 px — exact classifier view]  │        │
│   │                  (no rings)                        │        │
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
│ Your verdict (press 1 / 2 / 3):                                 │
│                                                                 │
│  [1] real_mound_my_error      — I clicked not_mound by mistake  │
│  [2] v2_overclaim             — model is wrong, my call stands  │
│  [3] edge_case_ambiguous      — reasonable people disagree      │
│                                                                 │
│  Optional note: [_______________________________________]       │
│                                                                 │
│  [< Prev]            [Skip]            [Submit + Next >]        │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Sidebar controls

- **Toggle: 400 m ringed context view** (off by default) — render the richer
  `render_candidate_context_crop()` view (400 m crop, 600 px, magenta concentric rings at
  50/75/100/125/150 m) from `review_candidates.py`. Off by default so the headline view stays
  pinned to the exact image the v2 classifier saw; flip on when extra spatial context aids a
  borderline call.
- **Toggle: Calibration sample** (on by default) — interleave a small random sample
  (~10) of `not_mound`-agreed candidates from the same review CSVs (rows the v2 classifier
  also called non-mound) into the queue as a blinded inter-rater calibration check. See §5.4.
- **Toggle: Re-review already-judged candidates** (off by default) — when on, the queue
  iterates over verdicted rows so the reviewer can revise. Default off so the queue is the
  un-judged subset.
- **Filter by mound subtype** — `all / settlement-mound / burial-mound /
  triangulation-point-on-burial-mound / benchmark-on-burial-mound`. Useful for
  Shawn to batch-review the 117 settlement-mound rows in one sitting since
  the cognitive task is the same across that subgroup.
- **Show verdict tally** — running breakdown of verdicts so far (live, updates on each
  submit).

### 5.3 Verdict input scheme — keyboard shortcuts

Speed matters at 177 crops. Streamlit's native keyboard handling is limited but workable
via `st.button` plus an `st.text_input` "command bar":

- **Primary scheme**: numbered buttons `1 / 2 / 3` plus a "Submit" button. Each verdict
  button submits-and-advances in one click (no separate Submit press).
- **Optional power-user scheme**: a small `st.text_input` at top labelled "shortcut" — typing
  `1`, `2`, `3`, then Enter, advances. Saves the mouse round-trip if Shawn finds the click
  pattern slow.
- **Navigation**: `[< Prev]` re-displays the previous candidate (read-only — to revise, use
  the sidebar "Re-review" toggle and resubmit, which overwrites the existing row). `[Skip]`
  advances without writing and re-queues the candidate to the end of the queue, so Shawn
  cycles back to it once the un-judged rows are exhausted (see §6.2).

The three substantive verdict labels plus `skip` (resolved 2026-04-29; see §10.2.3):

1. `real_mound_my_error` — user's review-pass label was wrong: this _is_ a real mound (any
   in-scope mound subtype, including `settlement-mound` — settlement-mounds are in scope for
   the project's extraction, since the original detection pass was asked to find them, so a
   v2 settlement-mound classification on a real settlement-mound is a reviewer error, not a
   "both correct" case)
2. `v2_overclaim` — v2 is wrong; user's `not_mound` stands
3. `edge_case_ambiguous` — reasonable people could disagree
4. `skip` — defer this candidate; re-queue it to the end of the un-judged queue (recorded as
   `skipped` in the verdicts CSV until the reviewer comes back to it)

### 5.4 Blinded calibration sample (sanity check) — default ON

Resolved 2026-04-29 (see §10): include the calibration sample, default ON. Surface a small
random sample (~10) of `human_label == "not_mound"` candidates that v2 _also_ classified as a
non-mound category (i.e., agreed cases) interleaved into the queue. The reviewer is told the
queue contains a calibration sample but not which rows. The verdict captured for those rows
is logged but held back from the headline 177-row review-error-rate computation, and used as
an inter-rater calibration signal: if Shawn flips on those, that is a noise estimate of how
often a fresh-eyes review of a settled `not_mound` row would dispute itself, which usefully
bounds the interpretation of `real_mound_my_error` rates on the 177 contested rows.

**Default: on.** Adds ~10 extra crops to the queue (turning a 90-minute task into a
~100-minute task) and provides a reusable noise-floor estimate. The toggle remains so the
reviewer can disable the sample if pressed for time; the bet itself is still adjudicated on
the 177 mound-category records alone.

## 6. Resume + persistence

### 6.1 Verdicts CSV format

Path: `results/55maps-fp-classification/v2-burial-mound-bet-test/verdicts.csv`.

```text
run,candidate_id,verdict,note,timestamp,is_calibration
T0.3,281,real_mound_my_error,"settlement mound — in scope, my not_mound was the error",2026-04-29T22:14:03+00:00,false
T0.3,233,v2_overclaim,"reads as a building cluster",2026-04-29T22:14:31+00:00,false
T0.7,012,v2_overclaim,"calibration row — agreed not_mound stands",2026-04-29T22:15:10+00:00,true
...
```

| Column | Type | Notes |
|---|---|---|
| `run` | str | From `fp_classifications.json` (or the source review CSV for calibration rows) |
| `candidate_id` | str | From `fp_classifications.json` (or the source review CSV for calibration rows) |
| `verdict` | str | One of `real_mound_my_error`, `v2_overclaim`, `edge_case_ambiguous`, or `skipped` |
| `note` | str | Optional free-text; quoted-CSV-safe |
| `timestamp` | str | ISO-8601 UTC, written at submit time |
| `is_calibration` | bool | `true` for calibration-sample rows (§5.4); excluded from the headline 177-row count in §7.2 |

### 6.2 Resume mechanism

Resolved 2026-04-29 (see §10): skipped candidates re-appear at the **end** of the queue.

1. On startup, load `verdicts.csv` if it exists into a `dict[(run, candidate_id) -> row]`.
2. The candidate queue iterates over the 177 mound-category records in the order
   `(run_alpha_order, descending_confidence, candidate_id)` so the queue order is stable
   across sessions.
3. Skip any candidate whose `(run, candidate_id)` is already keyed in the loaded dict
   **and** the recorded verdict is not `skipped`. Skipped candidates remain in the queue
   so Shawn cycles back to them.
4. The "current candidate" is the first un-judged-and-not-skipped candidate; once the
   un-judged pool is exhausted, the queue cycles to the skipped candidates at the end so
   Shawn adjudicates them on a second pass.
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
skipped                       ?      ? %
total                         177    100 %
```

The calibration-sample rows (§5.4), if used, are reported in a separate sub-table and
excluded from the 177-row total above.

### 7.2 Review-error rate computation

The headline metric on which the bet is settled — denominator resolved 2026-04-29 (see §10):

```text
review_error_rate = real_mound_my_error / not_mound_corpus_reviewed
                  = real_mound_my_error / 1,675
```

Reported alongside the more conservative bound:

```text
review_error_rate_inclusive = (real_mound_my_error + edge_case_ambiguous) / 1,675
```

**Why 1,675 and not 3,492 or 177?** Three candidate denominators were considered:

- **3,492** — the full pre-review tile corpus. Too generous: it would inflate the denominator
  with rows the user never actually reviewed and the v2 classifier never inspected, making
  the 2 % gate trivially easy to clear.
- **177** — the reclassifications alone. Too strict: it would equate the bet with "no more
  than 4 of 177 reclassifications can be reviewer errors", ignoring the 1,498 rows where the
  user's `not_mound` label was not contested by v2 (and so should weigh into the
  reviewer-error denominator).
- **1,675** — the `not_mound` corpus the user reviewed and the v2 classifier inspected.
  Tightest defensible scope: the rows where the user's `not_mound` decision is at stake and
  v2 had a chance to challenge it. This is the agreed denominator.

The 1,498 v2-non-mound rows in this 1,675 (i.e., 1,675 − 177 reclassified) are accepted at
face value as `not_mound` with a small noise floor that the agreed-cases calibration sample
(§5.4, default ON) estimates.

### 7.3 Bet adjudication

The 2 % gate against the 1,675 denominator translates to a threshold of **34
`real_mound_my_error` verdicts** (rounded up from 1,675 × 0.02 = 33.5), which is **≈ 19 %
of the 177 reclassifications**:

| Rate (vs. 1,675) | `real_mound_my_error` count | Share of 177 | Interpretation |
|---|---|---|---|
| `< 2 %` | < 34 of 177 | < 19 % of 177 | Shawn wins — agent owes a deep-dive analytical sweep |
| `≥ 2 %` | ≥ 34 of 177 | ≥ 19 % of 177 | Agent wins — Shawn owes a single-line tea acknowledgement |

The agent's prior prediction of 1-3 % review-error rate corresponds to **17-50** such
verdicts (1,675 × 0.01 ≈ 17, × 0.03 ≈ 50), which straddles the 34-verdict threshold —
the bet is genuinely contested under that prior.

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
| Calibration-sample loader (~10 v2-agreed `not_mound` rows, §5.4) | 20 |
| Streamlit UI assembly (sidebar + main pane + buttons, 3 verdicts) | 70 |
| Render-call wiring (import from `review_candidates.py`; default = 150 m view) | 20 |
| Verdict capture + CSV append + resume key handling (incl. skip re-queue) | 40 |
| Final-summary writer (`summary.md`) | 30 |
| Header docstring + UK English comments + edge-case handling | 30 |
| **Total** | **~305 LOC** |

Net effect of the 2026-04-29 clarifications on LOC: dropping `v2_correct_review_correct`
shaves ~10 LOC from the verdict-handling and report-writer code; adding the
calibration-sample loader and the default-on toggle adds ~20 LOC; the headline shift to the
150 m crop is a one-line default change. Total moved from ~295 to ~305 LOC.

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

## 10. Resolved decisions (2026-04-29)

All five open questions from the original §10 (preserved verbatim in §10.2 below for
audit purposes) were resolved in conversation with Shawn on 2026-04-29. The plan body
above has been updated to reflect each resolution; this section consolidates them.

### 10.1 Resolutions

| # | Question | Resolution | Rationale |
|---|---|---|---|
| 1 | Default crop view | **Exact 150 m / 768 px classifier view**, no rings (was: 400 m ringed) | Pins the review to "what could the model see?", removing the "but the model did not see that" objection from the verdict. The 400 m ringed view remains available behind a sidebar toggle for borderline calls. |
| 2 | Calibration sample (§5.4) | **Ship and default ON** (was: ship, default off) | Provides a reusable noise-floor estimate for fresh-eyes review of agreed `not_mound` rows; ~10 extra crops adds only ~10 minutes to the session. |
| 3 | `v2_correct_review_correct` verdict | **Drop the verdict entirely**; settlement-mound rows where the model is correct are now `real_mound_my_error` (was: keep as 4th verdict) | Settlement-mounds are in scope for the project's extraction — the original detection pass was asked to find them. So a v2 settlement-mound classification on a real settlement-mound is a reviewer error, not a "both correct" case. The verdict scheme reduces to three substantive verdicts (`real_mound_my_error`, `v2_overclaim`, `edge_case_ambiguous`) plus `skip`. |
| 4 | Bet adjudication denominator | **1,675** (was: 1,119) | Tightest defensible scope: the `not_mound` corpus the user actually reviewed and the v2 classifier inspected. 3,492 (full pre-review tile corpus) is too generous; 177 (reclassifications alone) is too strict. The 2 % gate translates to **34 `real_mound_my_error` verdicts ≈ 19 % of 177 reclassifications**. |
| 5 | Skipped candidates re-queue | **Yes, re-appear at end of queue** (no change from plan default) | Confirms the plan's pre-existing behaviour. |

### 10.2 Original open questions (superseded 2026-04-29)

The verbatim text of the §10 questions before resolution, kept for auditability:

#### 10.2.1 Crop view default (superseded — see §10.1 row 1)

> The plan recommends defaulting to the 400 m / ringed view (richer context, parity with
> `review_candidates.py`) with a sidebar toggle to flip to the 150 m / 768 px view the v2
> classifier actually saw. **Confirm: is the 400 m view the right default for this task, or
> do you want the 150 m view as default?** A reasonable counter-argument for 150 m as
> default is that it pins the review to "what could the model see?", removing the "but the
> model didn't see that" objection from the verdict.

#### 10.2.2 Calibration sample (superseded — see §10.1 row 2)

> **Calibration sample (§5.4)**: ship the toggle, default off?

#### 10.2.3 `v2_correct_review_correct` semantics (superseded — see §10.1 row 3)

> The plan reads this as "model labelled the feature accurately as something other than a
> project burial mound (e.g., a settlement mound / tell), and the user correctly declined to
> count it as a mound under the project scope". **Is that the intended interpretation, or
> did you have something narrower in mind?** A second reasonable reading is "the model
> picked a burial-mound subtype that _is_ a mound but not the project's target subtype" —
> under that reading, verdict (4) would only fire on `settlement-mound` rows, never on the
> other three subtypes. Worth clarifying before launch because the headline rate depends on
> the split between (1) and (4).

#### 10.2.4 Bet adjudication denominator (superseded — see §10.1 row 4)

> §7.2 reports the rate against the full 1,119 FP corpus (the conservative read).
> **Confirm**: that's the denominator you want, vs. against the 177 reclassifications alone
> (which would put the threshold at 4 of 177 ≈ 2 %)?

#### 10.2.5 Skipped candidates at end-of-queue (superseded — see §10.1 row 5)

> The plan re-cycles skipped candidates after the first pass. **Confirm**: that's preferred
> to leaving them un-judged in the verdicts CSV and adjudicating without them?

## 11. Next step

Implementation can be dispatched as soon as Shawn gives the green light. The plan is now
fully resolved and the build envelope is ~305 LOC and ~1-2 h of build wall time. No further
design clarifications are pending.

A reasonable launch sequence:

1. Confirm verbal go-ahead from Shawn.
2. Build `scripts/v2_burial_mound_bet_review.py` per the spec above (single commit).
3. Smoke-test on the first 3-5 candidates from the queue.
4. `ruff check` + `npx markdownlint-cli2` pass.
5. Hand the app to Shawn for the 60-90 minute review session.
6. Generate `summary.md` automatically on queue completion; verify against the §7
   final-report scheme.
