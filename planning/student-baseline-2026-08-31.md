# The novice human baseline: hardening student F1/P/R before the paper claims proximity

> **Last revised**: 2026-08-31 (original publication; PI-approved
> shape, Session 145). See [§ Changelog](#changelog).

**Question**: how good is the n=1 novice human baseline, exactly?
The model's corrected-F1@50 has drifted to 0.8763–0.8825 on the
55-map corpus (all-3.7 stack, `results/gemini37-55map-2026-08-31/`),
while the implied 55-map student baseline sits near ≈ 0.94 — a gap
of ~0.05 resting on estimates with known soft spots. Before the
paper claims proximity to (or parity with) novice performance, the
baseline needs solid numbers. PI (2026-08-31): "the n=1 novice human
baseline has become more important as our F1 has drifted upward".

## 1. What exists now (audited Session 145)

| Assessment | Numbers | Instrument |
|---|---|---|
| GS-4 direct (`results/student-gt-fn-rate-analysis-gs4/`, Obs 316) | Student P 1.000 / R 0.9473 / **F1 0.9729** at 50 m; FN 5.27 % (CI 2.9–8.8 %); radius-insensitive 50–150 m | reviewed student layer vs curator truth, Hungarian matcher, trapezoidal active-area clipping; replicates Sobotkova et al. 2023 (5.0 % / 0.1 %) |
| 55-map VLM-mediated (`results/student-gt-fn-rate-analysis/`, Obs 305) | FN headline 8.87 % (CI 6.9–11.4); recall-adjusted central **11.15 %** (8.6–14.5); precision assumed ≈ 1.0 | human review of VLM-flagged candidates; recall adjustment from the highest-recall corrected run |

### The five weaknesses (why the baseline is not yet claim-grade)

1. **Radius/footprint mismatch on GS** — the student baseline was
   never matched below 50 m; the model's GS headline is at 20 m on
   the tiled footprint. Novice localisation jitter at 20 m is
   unmeasured.
2. **Circularity on the 55 maps** — the canonical reference is 92 %
   the students' own layer (4,746 of 5,160); students scored against
   it are structurally flattered.
3. **Optimistic recall adjustment** — dividing by VLM recall assumes
   the model finds student-missed mounds at its average rate; Obs 361
   measured miss-correlation 1.5–1.7× on GS (double-misses cluster),
   so true 55-map FN is plausibly above 11.15 %.
4. **Cleaned vs raw** — the baseline uses the reviewed layer
   (commit `a8b576d5` lineage); Sobotkova 2023's figures were rawer.
5. **n=1, pooled** — no per-student attribution survives in the repo
   (checked all four GT files, S145); no between-student variance,
   no overlap structure.

## 2. Source data (Phase 1 input)

The 2023 campaign's FAIMS Mobile export (Sobotkova, Ross,
Nassif-Haynes, and Ballsun-Stanton 2023, *Applied Geography*,
10.1016/j.apgeog.2023.102967: 10,827 features, 241 person-hours)
contains, per the PI (2026-08-31): per-record creator attribution
**plus polygons designating each student's assigned area of
analysis** — one student is known to have missed a whole horizontal
swath, which the polygons make attributable ("should be held against
him"). Location: local download if present, else Google Drive under
publications → participatory GIS / crowdsourcing, ca. 2022–2023
(agent scout dispatched S145; manifest to be appended here).

## 3. Phase 0 — repo-only (no source data, $0 API)

- **0a. Matched-radius, matched-footprint GS baseline**: score the
  reviewed GS-4 student layer with the model evaluation machinery
  (same matcher, curated GT, model footprint) at 20/30/50 m →
  the first honest like-for-like model-vs-novice table. Expect the
  20 m row to drop (localisation jitter); that drop is itself a
  finding.
- **0b. Propagated implied-55-map student F1 interval**: combine the
  FN central estimate, an Obs 361-style miss-correlation correction,
  and a precision band (see 0d), with the circularity caveat stated
  in the artefact.
- **0c. `K-35-076-2` outlier check**: headline FN rate 0.5253 (52
  flagged vs 47 student mounds) — establish whether participatory
  coverage was incomplete on that sheet (assignment polygons, once
  retrieved, likely answer this directly).
- **0d. Review-derived precision bound**: formalise the measured
  demotion rate among reviewed student points (4,770 raw → 4,746
  kept; 23 of the kept reclassified off "Mound" ≈ 0.5 %, on a
  review biased TOWARD problem points) → "precision bounded
  ≥ ~0.995 by targeted review" replaces "assumed ≈ 1.0".
- **0e. FN error-profile mining**: the 462 confirmed student FNs in
  the review CSVs, by distance-to-nearest-student-point, per-map
  density, and symbol covariates where recorded → do novice misses
  cluster near mapped mounds (attention saturation) or in blank
  regions (scanning gaps)? Feeds Seed 11's "error profiles differ
  in kind".

**Sequencing**: Phase 0 starts after the Gemini 3.7 fourth-cell
harvest is complete (the standing results-write freeze for the grid
campaign governs until then).

## 4. Phase 1 — return to source (gated on the export)

- **1a. Per-student P/R/F1 within assignment polygons** on the GS-4
  sheets vs curator truth: recall denominator = truth within the
  student's polygon, so coverage failures (the horizontal swath)
  count against the responsible student. Produces a *distribution*
  of novice performance in place of the pooled point.
- **1b. Overlap census**: polygon intersections → wherever 2+
  students covered the same ground, novice k-of-n consensus curves —
  the human analogue of the model's consensus dividend. If no
  overlaps exist, between-student variance on disjoint areas is
  still reportable (polygon covariates partially control sheet
  difficulty).
- **1c. Raw-vs-cleaned delta**: pre-curation GS-4 student pass vs
  the repo's reviewed layer — how much did cleaning flatter the
  baseline?
- **1d. Lineage confirmation** for Seed 11's standing
  `[unverified]` flag (does the 55-map layer descend from the 2023
  campaign?).

## 5. Phase 2 — the empty-tile audit (PI-executed, ~40–80 min)

Estimates the double-miss floor: mounds missed by BOTH students and
model — the blind spot no existing instrument can see.

- **Frame**: the 8,541-tile evaluation grid. **Empty** = no
  canonical-GT point, no student point, no detection from arm-2
  carried or B-N5 carried → **4,676 tiles (54.7 %)** (computed
  S145 from `55maps_evaluation_bounds.geojson` +
  `canonical-gt-55maps-r50.geojson` + the two detection sets; the
  sampling script re-derives and gates this count).
- **Sample**: **10 % = 468 tiles** (PI: "easily"; 20 % = 935
  feasible as escalation), stratified by sheet with proportional
  allocation, seeded. ~40 min at a few seconds per tile (~80 min
  at 20 %).
- **Task**: presence/absence per tile; on presence, mark the mound
  location (adapt the existing Streamlit reviewer).
- **Escalation rule (pre-agreed)**: if positives exceed the GS-rate
  expectation (~1–3 % of tiles), extend to 20 %; if still
  non-trivial, revive the stratified fresh-curator-pass option
  (§ 6).
- **Estimand caveat (state in the artefact)**: this measures
  double-misses in UNFLAGGED terrain — isolated mounds. Obs 361's
  miss-correlation implies some double-misses hide inside dense
  clusters on occupied tiles; the audit does not see those, and the
  number must not be presented as the total double-miss rate.
- **Scope note**: FP characterisation is NOT part of this audit —
  the 55-map FP side is considered nailed down (PI, 2026-08-31;
  Obs 361 precision review-verified).

## 6. Held in reserve

A fresh curator pass over a stratified ~5-sheet sample of the 55
maps (direct, non-VLM-mediated student FN/FP measurement) — only if
Phase 2 finds a non-trivial double-miss rate.

## 7. Cost and effort envelope

$0 API throughout (all phases are local compute + PI review time).
Compute on sapphire per the standing rule. PI time: Phase 2 ~40–80
min; Phase 1 sign-offs interactive. Claude time: Phases 0–1
scriptable within existing machinery (Hungarian matcher,
bootstrap-by-sheet, Streamlit reviewer).

## Changelog

### 2026-08-31 — Original publication

Drafted at PI direction (S145 interactive) after the audit of both
existing assessments; shape approved in discussion. PI decisions
recorded: 10 % empty-tile sample as default (20 % feasible);
assignment polygons confirmed to exist in the 2023 export; Drive
scout agent dispatched for the export manifest. Phase 0 gated
behind the Gemini 3.7 fourth-cell harvest; Phase 1 gated on the
export; Phase 2 gated on tooling + PI availability.
