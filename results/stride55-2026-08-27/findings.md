# The 55-map portfolio at deployment: the transfer tax collapses

> **Last revised**: 2026-08-27 (later: A-vs-B at the N = 5 carried
> points, lean deployment costs, uplift basis correction). See
> [§ Changelog](#changelog) for revision history.

**Classification**: post-hoc, E41-class deployment extension (card:
`planning/55map-portfolio-2026-08-25.md`; the measurement contract and
the P1–P8 predictions were committed before launch). All evaluation is
corrected-F1 at 50 m against the canonical adjudicated extended
Ground Truth (GT) on the two-reference 55-map protocol, tile-level
Matthews Correlation Coefficient (MCC) alongside.

## Headlines (the committed primary claims)

The two carried operating points, declared before launch and evaluated
once, whatever the sweep later showed:

| Run | Geometry (stride) | Carried point | corrected-F1@50 | Precision | Recall | MCC |
|---|---|---|---:|---:|---:|---:|
| A | 384 px / 33.3 % (256) | prob ≥ 0.15, k ≥ 8 of 10 | **0.8326** | 0.896 | 0.777 | 0.693 |
| B | 384 px / 50 % (192) | prob ≥ 0.15, k ≥ 10 of 10 | **0.8422** | 0.903 | 0.789 | 0.698 |

Both sit **above the carried incumbent** (text-HIGH T0.7 × 4-of-5,
0.8152) — at MINIMAL thinking, where the incumbent runs HIGH. B's
carried point lands within 0.006 of the old two-axis deployment oracle
(0.8476) and within 0.0002 of the incumbent's within-config
(threshold-only) oracle ≈ 0.842.

## The sweep: oracles and the transfer tax

Full (prob_t × k) sweep per run (200 points each, 20 achievable
verifier thresholds × k ∈ 1..10), same fixed extended GT
(5,160 references at 50 m). Replication gate: the sweep reproduces
each run's committed primary evaluation to 1e-6 (A 0.832590,
B 0.842214) — passed for both cells before anything was written.

| Run | Carried | Oracle | Oracle point | Transfer tax |
|---|---:|---:|---|---:|
| A | 0.8326 | 0.8362 | (0.15, k7) | **+0.0036** |
| B | 0.8422 | 0.8503 | (0.20, k9) | **+0.0081** |
| Incumbent (S104, for scale) | 0.8152 | 0.8476 | (T0.3 × 3-of-5) | **+0.0324** |

The Gold Standard (GS)-selected calibration essentially **sat on the
deployment plateau**: the tax the S104 incumbent paid (+0.032, joint;
~+0.027 on the threshold axis alone) is an order smaller for A and 4×
smaller for B. B's oracle 0.8503 **exceeds the old deployment oracle**
0.8476 — and B's is a one-config (prob_t, k) oracle where the old one
also optimised over configuration (temperature).

Why the tax collapsed (the sweep surface):

1. **The k-lattice is finer at K = 10.** A one-step k error near the
   top costs A −0.0036 (k7→k8) and B −0.0072 (k9→k10); at the
   incumbent's K = 5 the same one-step move cost +0.027 (4-of-5 →
   3-of-5). Vote resolution, not better guessing, is what shrank the
   price of a mis-carried threshold.
2. **The top is flat.** A's k5–k8 all lie within 0.008 of its oracle;
   B's k8–k10 within 0.008 likewise.
3. **The verifier dial transfers exactly.** Both prob-curves peak at
   0.15–0.20 (A: 0.15 is the argmax; B: 0.15 sits 0.0009 under the
   0.20 argmax); 0.10 collapses the board (−0.12) and ≥ 0.25 decays
   slowly. The GS-chosen 0.15 was never the risk.
4. **The portfolio froze the config axis by design** (one carrier
   config per run), so the temperature loss the incumbent paid
   (+0.021 marginal) had no analogue to pay.

## A versus B (pre-declared question 2 — the overlap choice)

Per-map paired sign-swap permutation (55 sheets, 10,000, seed 42),
convention delta = A − B:

| Comparison | ΔF1 | p (two-sided) |
|---|---:|---:|
| At the carried primaries | −0.0096 | 0.0147 |
| At the oracles | −0.0141 | 0.0001 |

**B (denser stride, the recall pole) wins at both.** P6 predicted a
tie from the GS board; this is one of the card's pre-named informative
failures (A ≠ B). It is also exactly the Obs 362 mechanism: a GS tie
is bounded ignorance at ±0.03 resolution, and a real ~0.01 effect sat
inside the bound.

**Added post-hoc at PI request (2026-08-27), clearly labelled as
outside the card's declared family**: paired A-vs-B at the **N = 5
carried points** — the rung the deployment recommendation lives on
(A 0.8322 at ~$60 vs B 0.8438 at ~$97). ΔF1 = −0.0116, p = 0.0042
(same instrument; gates reproduced both committed carried F1s to 1e-6
first). **B is significantly better at the recommendation rung too** —
the extra ~$37 buys a real ~0.012, at every rung tested.

**Benjamini–Hochberg across the test family** (q = 0.05; the declared
six tests plus the PI-requested seventh): all five non-tie results
survive — A-vs-B at oracles (p = 0.0001), B oracle-saturation
(0.0003), A-vs-B at N = 5 carried (0.0042), A oracle-saturation
(0.0131), A-vs-B at primaries (0.0147); the two carried-point
saturation ties stay non-significant. P6's failure is BH-robust.

## The N-ladder (P2 / P4 / P7)

First-N rungs (`stride55_ladder.py`), verifier probabilities inherited
from the committed K = 10 verification (inheritance p95 match distance
5.4–8.7 m against the 10 m radius; unmatched clusters 0.3–2.6 % per
rung, excluded from scoring, included in cost). Gates passed for both
cells: exact K = 10 union rebuild (count and votes identical, centroid
drift ≤ 0.069 m = manifest storage precision) and 1e-6 primary
reproduction through the ladder's own path.

| Run | N | Union | Rung oracle | Point | Carried (GS) | Est. all-in (flex) |
|---|---:|---:|---:|---|---:|---:|
| A | 1 | 18,631 | 0.8186 | (0.20, k1) | — | $20.53 |
| A | 3 | 26,245 | 0.8274 | (0.20, k2) | — | $41.22 |
| A | 5 | 30,713 | 0.8322 | (0.15, k4) | **0.8322** — carried IS the optimum | $59.75 |
| A | 10 | 38,713 | 0.8362 | (0.15, k7) | 0.8326 | $103.91 |
| B | 1 | 25,586 | 0.8004 | (0.20, k1) | — | $30.99 |
| B | 3 | 36,757 | 0.8449 | (0.20, k3) | — | $65.48 |
| B | 5 | 43,909 | 0.8450 | (0.20, k5) | 0.8438 | $97.22 |
| B | 10 | 57,482 | 0.8503 | (0.20, k9) | 0.8422 | $173.59 |

(N = 10 rows are the sweep's committed values; carried N = 3/N = 1
points were not registered, so those rungs are oracle-only. Costs are
proposer flex × N/10 + full-union verification at $0.000687/call.)

**P7 saturation** (per-map paired permutation, delta = N5 − N10):

| Run | At the carried points | At the oracles |
|---|---|---|
| A | −0.0004, p = 0.82 (tie) | −0.0040, p = 0.0131 (BH-sig) |
| B | **+0.0016**, p = 0.32 (tie — N5 carried ABOVE N10 carried) | −0.0053, p = 0.0003 (BH-sig) |

At the deployed (carried) points, half the passes cost nothing —
B's N = 5 carried point actually scores above its N = 10 carried
point. At the oracles a small real residue remains (−0.004 to
−0.005): pass-count saturation is real but not complete. B saturates
early — its N = 3 rung oracle (0.8449) already equals its N = 5
(0.8450) and exceeds the N = 10 carried headline (0.8422).

## The P1–P8 scorecard

| # | Bet | Observed | Verdict |
|---|---|---|---|
| P1 | A optimum (0.15, k8); drift only DOWNWARD (6–7) | oracle (0.15, k7) | **PASS** — downward, inside the named window |
| P2 | A N = 5 optimum (0.15, k4) | rung oracle (0.15, k4) — the carried point IS the optimum | **PASS, exact** |
| P3 | B optimum (0.15, k10); most likely to break downward (8–9) | oracle (0.20, k9) | **PASS on k** — broke downward into the named 8–9 window; prob_t caveat under P8 |
| P4 | B N = 5 optimum (0.15, k5) | rung oracle (0.20, k5); (0.15, k5) at −0.0012 | **PASS on k**, exact; the recurring marginal prob_t drift under P8 |
| P5 | Headlines 0.80–0.85; neither significantly below 0.8152 | 0.8326 / 0.8422, both ABOVE the incumbent | **PASS**, with an overshoot worth explaining (next section) |
| P6 | A vs B statistical tie | B wins, p = 0.0147 primaries / 0.0001 oracles | **FAIL** — the pre-named informative failure; overlap matters at deployment |
| P7 | N = 5 within noise of N = 10, both runs | carried: tie both runs (p = 0.82 / 0.32); oracles: −0.004/−0.005, BH-sig | **PASS at the deployed points**; a small real oracle residue — saturation is real but not complete |
| P8 | prob_t 0.15 everywhere | A argmax 0.15; B argmax 0.20, with 0.15 at −0.0009 | **FAIL by the letter, PASS in substance** — 0.15 on-plateau in both runs; the B deviation is an order below every other effect in the family |

Pre-named informative failures triggered: **A ≠ B** (P6). Neither of
the other two (upward k drift; any headline below 0.80) occurred.

## The P5 overshoot, decomposed

The open question flagged at S142 close: why does the new geometry
transfer BETTER than the incumbent it was benchmarked against, when on
GS it was plateau-not-winner? The sweep gives an exact additive
decomposition of B's carried margin over the incumbent's carried point:

```text
B carried − incumbent carried   = 0.8422 − 0.8152 = +0.0270
  incumbent's transfer tax      = +0.0324   (it paid; B did not)
  oracle-to-oracle geometry gap = +0.0027   (0.8503 − 0.8476)
  B's own transfer tax          = −0.0081   (B paid)
                                  --------
                                  +0.0270  ✓
```

**The overshoot is not the geometry finding substantially more mounds**
(+0.0027 at oracle, against an old oracle that also optimised
temperature) — **it is the transfer tax collapsing** (mechanisms in
the sweep section: finer vote lattice, flat top, exactly-transferring
verifier threshold, frozen config axis). The practitioner-workflow
reading: "calibrate on 4 sheets, deploy" cost the K = 5 incumbent
0.032; at K = 10 with overlap geometry the same workflow cost
0.004–0.008. What GS could not see (P6's broken tie) was worth ~0.010;
what the calibration protected was worth ~0.03.

A second, cheaper reading of the same numbers: the incumbent's HIGH
thinking bought nothing here — both new runs are MINIMAL-thinking and
carried above the HIGH incumbent's carried point (and B's oracle above
its two-axis oracle) on the strength of geometry + K = 10 + verifier.

## The four pre-declared questions, answered

1. **Does the GS geometry plateau transfer?** Yes, and almost
   losslessly: both carried points landed above the incumbent with
   transfer taxes of +0.004/+0.008 against the incumbent's +0.032.
2. **Does the overlap/stride choice matter at deployment?** Yes —
   P6's tie broke. B (50 % overlap) beats A by ~0.010 at the
   primaries and ~0.014 at the oracles, BH-robust.
3. **Does pass-count saturation hold?** At the deployed points, yes —
   N = 5 is statistically indistinguishable from N = 10 in both runs
   (B's N = 5 carried point is nominally higher). At the oracles a
   small real residue (−0.004 to −0.005) remains.
4. **Where is the deployment Pareto frontier?** Below, with the
   incumbents folded in.

## Deployment Pareto and recommendation

Two cost bases, both flex, full 55-sheet corpus. **Full** = proposer ×
N/10 + verification of the entire vote ≥ 1 union (what this analysis
paid: it buys the sweep, the oracle, and the ladder inheritance).
**Lean deploy** = proposer × N/10 + verification of only the carried
vote-shell (vote ≥ k at the row's operating point) — what a
practitioner deploying the carried point actually needs. Incumbent
costs from the S113 token-load audit; incumbent lean adds the ~$2
S104-campaign shell share to the proposer cost (approximate — their
as-billed verifier lines vary in scope).

| Configuration | Full cost | Lean deploy | corrected-F1@50 | Basis |
|---|---:|---:|---:|---|
| A, N = 1 | $20.53 | $20.53 (shell = union at k1) | 0.8186 | rung oracle |
| text-min incumbent (K = 5) | ~$23.4 | ~$25 | 0.783 carried / 0.8127 post-hoc k3 | as-billed is proposer-only |
| B, N = 1 | $30.99 | $30.99 | 0.8004 | rung oracle; dominated by A N = 1 |
| A, N = 3 | $41.22 | $34.74 | 0.8274 | rung oracle |
| min11-uplift incumbent (10-pass min, std grid) | ~$58 | ~$47 + k5-shell (count not on disk; as-run band $11.27) | 0.8290 | **post-hoc best** (0.15, 5-of-10) — corrected from "committed cell" |
| A, N = 5 | $59.75 | $48.18 | 0.8322 | carried (= rung oracle) |
| B, N = 3 | $65.48 | $51.71 | 0.8449 | rung oracle |
| B, N = 5 | $97.22 | $77.28 | **0.8438 carried** / 0.8450 oracle | carried |
| B, N = 10 | $173.59 | $143.17 | 0.8422 carried / **0.8503 oracle** | carried / oracle |
| A, N = 10 | $103.91 | $86.18 | 0.8326 carried / 0.8362 oracle | dominated by B N = 3 |
| image incumbent (HIGH, K = 5) | ~$195.4 | ~$197 | 0.799 carried / 0.801 post-hoc k3 | dominated |
| TH7-k4 incumbent (HIGH, K = 5) | ~$207.4 | ~$203 | 0.8152 carried / 0.8425 post-hoc k3 | dominated from A N = 3 up |
| T03 incumbent (HIGH T0.3, K = 5) | ~$261.0 | ~$256 | 0.836 carried / 0.8476 post-hoc k3 (the old oracle) | dominated |

A matched-config aside the table makes visible: min11-uplift, A, and B
are all MINIMAL-text T = 0.7 at 10 passes with the same verifier —
the only axis moving is overlap. Post-hoc best against overlap:
**0.8290 (12.5 % / stride 336) → 0.8362 (33.3 %) → 0.8503 (50 %)** —
a clean monotone overlap gradient with everything else frozen.

**Practitioner recommendation (pre-declared question 4): Run B's
geometry (384 px / 50 % overlap) at N = 5 with the GS-carried
calibration (0.15, k5)** — an honestly-carried 0.8438 at ~$97 full /
**~$77 lean** for 55 sheets, above every other carried point on the
board including its own N = 10 (0.8422, $174/$143) and the
HIGH-thinking incumbent (0.8152, ~$207) — and the A-vs-B margin at
this rung is statistically real (−0.0116, p = 0.0042). Budget floor:
A at N = 3–5 ($35–48 lean) holds 0.827–0.832. Peak: B at N = 10 only
if the last ~0.005 matters and post-hoc calibration is acceptable
(its 0.8503 is an oracle).

Caveats: N < 10 costs are simulated from the audited per-call rates
(the passes were physically run inside the K = 10 campaign); N = 3
rungs are oracle-only (no carried point was registered there); all
costs are flex-tier estimates, not billing-console figures.

## Method

- Corpus: 55 sheets, full-extent overlapping tilings
  (`tiles_384_ov128_55maps` 14,160 tiles/pass; `tiles_384_ov192_55maps`
  24,561 tiles/pass), K = 10 passes, `detect_brief-text`,
  gemini-3-flash-preview, MINIMAL thinking, T = 0.7, real-time flex.
- Verifier: carry-forward `verify_adversarial-text`, T = 0.0, MINIMAL,
  n = 1, one call per K = 10 union candidate (38,713 A / 57,482 B;
  96,195/96,195 verified).
- Evaluation: corrected-F1 at 50 m vs the canonical adjudicated
  extended GT (4,746 student + 414 reviewer-promoted phantoms at 50 m,
  1 duplicate dropped → 5,160 references), detection-independent,
  built once and reused across the sweep; tile-MCC alongside where
  inputs support it.
- Instruments: full (prob_t × k) sweep (`stride55_sweep_oracle.py`);
  per-map paired sign-swap permutation, 10,000 draws, seed 42
  (the S104 instrument); first-N ladder with inherited verification
  (`stride55_ladder.py`); BH-FDR q = 0.05 across the declared family.
- Gates: sweep and ladder each reproduce the committed primary
  evaluations to 1e-6 before writing; the ladder additionally rebuilds
  the committed K = 10 unions exactly (count and votes identical;
  centroids within 0.2 m — the committed manifest's 4326 GeoJSON
  round-trip precision, observed max drift 0.069 m).

## Artefacts

- `sweep_oracle.json` — oracles, transfer gaps, paired A-vs-B.
- `<cell>/sweep_50m.csv` — the full 200-point surfaces.
- `<cell>/primary/` — the committed primary evaluations (S142).
- `ladder.json`, `<cell>/ladder_sweep_50m.csv` — the first-N rungs
  (360 further sweep points), inheritance diagnostics, saturation
  permutations, cost estimates.
- Card and registered predictions:
  `planning/55map-portfolio-2026-08-25.md` § 3b.

## See also

- `results/deployment-oracle-2026-06-06/deployment-oracle-findings.md`
  — the incumbent S104 oracle and canonical-GT construction.
- `results/stride-2026-08-25/findings.md` — the GS stride programme
  that selected these two geometries.

## Changelog

### 2026-08-27 (later) — A5-vs-B5, lean costs, uplift basis correction

Trigger: PI review session (interactive). (1) **A-vs-B at the N = 5
carried points** added at PI request, labelled post-hoc to the card's
declared family: ΔF1 −0.0116, p = 0.0042 (`a5_vs_b5.json`; gates
reproduced both committed carried F1s to 1e-6). BH re-run over the
seven-test family — all five non-tie results survive; conclusions
unchanged, strengthened at the recommendation rung. (2) **Lean-deploy
cost column** added to the Pareto (carried-shell verification only):
e.g. B N = 5 $97.22 → **$77.28**; A N = 5 $59.75 → $48.18; the
recommendation's prices updated. (3) **Correction**: min11-uplift's
0.8290 basis was listed as "committed cell"; its condition entry
(`run-conditions.json`) records it as the **best deployment operating
point (0.15, 5-of-10) — post-hoc**. Moved to the post-hoc column.
(4) The matched-config overlap gradient noted (uplift 0.8290 → A
0.8362 → B 0.8503, post-hoc, MINIMAL/K = 10/verifier frozen).
What did NOT change: headlines, scorecard verdicts, transfer taxes,
the P5 decomposition. Commit: this one.

### 2026-08-27 — Original publication

The complete secondary analysis (Session 143, sapphire, $0 API):
sweep oracles and transfer taxes, paired A-vs-B, the first-N ladder
with saturation tests, family-wide BH-FDR, the full P1–P8 scorecard
(P6 the sole informative failure; P8 fail-by-letter only), the
P5-overshoot decomposition, and the deployment Pareto with the
practitioner recommendation. Every derived number gated: sweep and
ladder each reproduce the committed S142 primary evaluations to 1e-6;
the ladder rebuilds the committed K = 10 unions exactly.
