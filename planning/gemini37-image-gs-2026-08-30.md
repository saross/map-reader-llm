# Gemini 3.7 image-track screen: has the modality gap moved?

> **Last revised**: 2026-09-02 (COMPLETE — verdicts I1–I5 in;
> the modality gap is eliminated at 3.7; findings at
> `results/gemini37-image-gs-2026-09-01/findings.md`).
> See [§ Changelog](#changelog).

**Question**: did 3.7's vision change shift RELATIVE modality
performance? On Gemini 3, text examples beat image examples by
**+0.0549 @20 m (p = 0.001)** on exactly this geometry
(`results/image-b-gs-2026-08-28/analysis.json`). A gap that size is
more than twice the GS verified-set resolution (MDE80 ≈ 0.024), so
"has the gap narrowed?" is GS-resolvable outright — unlike the
absolute 3.7-vs-3 text question that needed the 55-map instrument.

**Design strength (recorded up front)**: the gap change is a
difference-in-differences — (text − image) within 3.7 vs (text −
image) within Gemini 3. Both 3.7 cells carry the same thinking
regime (low, ~276 t/tile) and both Gemini 3 cells carry none
(MINIMAL, 0 t/tile), so the model-vs-thinking confound that hangs
over every absolute cross-model comparison largely nets out of this
contrast.

## The cell

| Parameter | Value | Note |
|---|---|---|
| Config | `detect_brief-text-image` — byte-identical | the S143 image-B campaign config; 17 examples, `include_example_images: true` |
| Model | `gemini-3.7-flash` via `--model` CLI override | stamped in metas |
| Thinking | `low` via `--thinking-level` CLI override | the screen's two-override pattern |
| Geometry | B: 384 px / 50 % (stride 192), GS corpus | `inputs/grid-2026-08-18/grid_384_ov192_manifest.json`, 1,398 tiles |
| Passes | K = 5 (run_1..5), T = 0.7, real-time flex | mirrors the text screen |
| Verifiers | BOTH arms over the K=5 union: carried gemini-3-flash T0.0 MINIMAL n1, AND gemini-3.7-flash low T0.0 n1 | the swap-symmetric design, per the 55-map card § 4b |
| Anchors | G3 image MIN best @20 m **0.8412** (P 0.8741 / R 0.8107 / MCC 0.7985) at (0.15, k9); text anchor 0.8961; gap **+0.0549** p=0.001; 3.7-text screen 0.9139 / all-3.7 0.9265 | all committed |

Operating points come from this screen's own sweep (screening
protocol, as the text screen did); carry-forward discipline applies
only if a cell later transfers to deployment.

## Registered expectations (committed at PI go)

| # | Bet | Prediction | Grounding |
|---|---|---|---|
| I1 | Family gain on image | 3.7-image verified best ABOVE the G3 image anchor 0.8412 | the text screen's +0.018; PI's vision-change hypothesis |
| I2 | The gap | (text − image) within 3.7 NARROWER than 0.0549 by more than the resolution — i.e. gap < ~0.031 | the vision-change hypothesis; pre-named informative outcomes: gap unchanged (vision gain is modality-neutral) or WIDER (text benefited more) |
| I3 | Lattices | carried-verifier arm optimum at prob ∈ {0.10–0.20}, mid-to-high k; 3.7-verifier arm optimum at prob_t ≥ 0.6 (the calibration shift replicates on image candidates) | every prior lattice; the GS swap profile |
| I4 | Thinking at `low` on image prompts | nonzero, < 1,000 t/tile, ≈ the text screen's 276 | measured text profile; probe pins |
| I5 | Cost and caching | implicit caching engages as on G3 (cached fraction ≥ 90 % of input); all-in within § Cost envelope | G3 image profile: 18,923 of 20,033 t/tile cached (94.5 %) |

## Cost — flex + caching (both load-bearing, per the PI)

The image track is only cheap because ~94.5 % of its input tokens hit
the implicit context cache (the 17 example images). Per-call at the
G3-measured profile (in 20,033 of which cached 18,923; out 119;
thinking assumed ≈ 276 at 3.7-low):

| Component | Tokens/call | Rate (flex) | $/call |
|---|---:|---|---:|
| Non-cached input | 1,110 | $0.375/M | 0.000416 |
| Cached input | 18,923 | $0.075/M ASSUMED (G3's cached = 20 % of input rate; 3.7 cached rate unconfirmed) | 0.001419 |
| Output + thinking | ~395 | $1.875/M | 0.000741 |
| **Total** | | | **≈ $0.00258** |

- Proposer 6,990 calls ≈ **$18 token-basis / ~$12 billed-expected**
  (the 3.7 SKU has billed ~0.6× token-basis so far).
- Verifier arms on a ~700–1,000-candidate union ≈ **$1.5–2** both.
- **All-in expected ≈ $20 flex** (standard-tier fallback ≈ $40 if
  the flex queue is unusable).
- **Failure ceiling**: if caching does NOT engage on 3.7 (or bills at
  the full input rate), the proposer alone is ≈ $58. The probe gates
  this out (below).

## Probe first (gates the caching assumption)

5 tiles (~$0.02): verify meta stamps (model, thinking level); measure
thinking volume on image-example prompts; **measure the cached-token
fraction — abort if < 80 %** (caching is the cost model); pause if
the implied all-in exceeds **$30**.

## Execution and sequencing (the 3.7-SKU pipeline)

Runs on the 3.7 SKU are SEQUENTIAL (PI rule, 2026-08-30 — quota is
not the binder at RPM 20k / TPM 20M; flex-queue congestion is, and
concurrent 3.7 runs would inflate each other's 503 retries):

1. 55-map proposers (IN FLIGHT) →
2. 55-map arm-2 (3.7) verifier →
3. **this screen's proposers** (probe → `/audit-config` delta →
   K=5 driver, idempotent overnight pattern) →
4. this screen's 3.7-verifier arm.

Gemini-3-SKU work (the two carried-verifier arms) runs concurrently
with any of the above the moment its union exists. Analysis chain:
the text screen's exact machinery (`image_b_prepare_and_union.py`
→ `run_pv.py verify` ×2 → `image_b_analysis.py` with
`--union-name`/`--verify-dir`), then the I1–I5 verdicts and the
difference-in-differences gap test.

## Changelog

### 2026-09-02 — Screen complete; gap eliminated

All verdicts in (findings doc is canonical): I1 confirmed at ~5× the
text-side gain (0.9254/0.9308 vs the 0.8412 anchor); I2 overshot to
statistical parity (text−image −0.0115 p=0.25 / −0.0043 p=0.68 vs
G3's +0.0549 p=0.001); I3 exact; I4 lighter than predicted; I5
informative failure (79.5 % caching). No resolvable new F1 high —
the 55-map image-extension trigger is NOT met. Execution survived an
fd-ulimit failure mode (fixed in the committed driver) and the daily
flex-storm window (recovery driver, one clear-window round).

### 2026-09-01 — Probe gates run; PI approved launch at probed cost

Probe (5 tiles, $0.026): stamps PASS (gemini-3.7-flash / low),
thinking 189 t/call (I4 PASS). **Cache-fraction gate FAILED at face
value (16.3 %)**; a sequential 15-call re-probe ($0.077) showed
warm-up dynamics: 54.2 % aggregate, ~60–65 % estimated steady state —
caching engages but well short of G3's 94.5 %, so **I5 fails
informatively** (runs as the registered prediction). Implied all-in
~$34–36 token-basis (~$20–22 billed-expected at the SKU's ~0.6×
history), over this card's $30 pause line — PI ruled 2026-09-01:
"that cost is acceptable, please use caching". Launched 05:5x UTC:
`scripts/gemini37-image-gs-driver.sh`, K=5, WORKERS=400, flex,
byte-identical config (md5 9ff5e64d…), manifest = tree 1,398/0,
prefix warmed by the probes. /audit-config delta clean.

### 2026-08-31 — PI go given

PI: "After that, we can run the queued image-mode GS" (following the
fourth-cell commissioning). Queue position: after the fourth-cell
55-map verification + scoring harvest. Execution unchanged from this
card: probe (cache-fraction gate ≥ 80 %) → /audit-config delta →
K=5 driver at the WORKERS=400 standing default → union → BOTH
verifier arms → I1-I5 verdicts + the difference-in-differences gap
test. Anchors and costs as below.

### 2026-08-30 — Original publication

PI commissioned in-session ("draft the card now. Be sure to use
caching as well as flex") after the escalation results; queued on
the 3.7-SKU pipeline behind the 55-map campaign. Nothing runs before
PI go on this card.
