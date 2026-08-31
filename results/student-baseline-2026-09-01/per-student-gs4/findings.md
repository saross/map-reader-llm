# The novice baseline decomposed: students and configs on identical ground

> **Last revised**: 2026-09-01 (original publication). See
> [§ Changelog](#changelog) for revision history.

**Classification**: Phase 0a/1a of the student-baseline programme
(`planning/student-baseline-2026-08-31.md`), run overnight on PI
authorisation (2026-08-31 "proceed through the analysis as far as
you can"). Descriptive — no significance tests yet (the per-sheet
paired instrument can be adapted next). All numbers:
`analysis.json` / `per_student.csv` alongside this file.

## What was computed

The committed pooled GS-4 student baseline (P 1.000 / R 0.9473 /
F1 0.9729 at 50 m) was decomposed per student within the 2023 QA
audit-area polygons, with a **replication gate**: the per-student
split sums exactly to the committed aggregate (TP 539 / FP 0 /
FN 30 at 50 m). Attribution came from the staged 2023 master layer
(nearest-neighbour join; unanimous per polygon). Students and two
model configurations (the 3.7 text screen best and the all-3.7 swap
best) were then re-scored on **identical ground**: audit polygon ∩
the 487-tile GS evaluation footprint, same curator reference, same
Hungarian matcher, radii 20/30/50 m.

**Method catch recorded**: the first pass scored the model against
full sheets — territory it never saw (the GS corpus is the 487-tile
footprint) — producing sheet-dependent recall (0.59–0.91) at healthy
precision, the partial-coverage signature. Those rows were invalid
and replaced by the footprint basis; on it, the model's pooled zone
values sit within 0.01 of its committed corpus-wide figures (0.9190
vs 0.9265 @20 swap; 0.9066 vs 0.9139 screen), validating the
instrument.

## Ranking on identical ground (footprint basis)

At **20 m** (the GS working radius), pooled over all five zones
(n_ref = 435):

| Rank | Contender | P | R | F1 |
|---|---|---:|---:|---:|
| 1 | **all-3.7 model** | 0.9254 | 0.9126 | **0.9190** |
| 2 | 3.7-text-screen model | 0.8984 | 0.9149 | 0.9066 |
| 3 | students (pooled) | 0.8678 | 0.8299 | 0.8484 |

At **50 m**:

| Rank | Contender | P | R | F1 |
|---|---|---:|---:|---:|
| 1 | **students (pooled)** | 0.9976 | 0.9540 | **0.9753** |
| 2 | all-3.7 model | 0.9394 | 0.9264 | 0.9329 |
| 3 | 3.7-text-screen model | 0.9120 | 0.9287 | 0.9203 |

Per zone at 20 m: the model wins Rakovski[C] decisively (0.9789 vs
0.7492) and loses Lesovo[D] decisively (0.7059 vs 0.8966; n_ref
only 15, and model precision collapses to 0.46–0.63 on that sparse
sheet); B and A edge the model narrowly on their zones (0.9462 vs
0.9239; 0.8718 vs 0.8646). At 50 m every student except C beats
both models on their own zone; the model still beats C on Rakovski
(0.9849 vs 0.9587).

## The three findings

1. **The PI's bet lands: the model beats at least one student.**
   The all-3.7 stack beats Student C on his main sheet at BOTH radii
   — and C is not a strawman: excluding his three digitised
   missed-swath polygons (coverage failure), his 50 m performance is
   excellent (0.9916). The model's win over C at 50 m is a win over
   his *coverage*, not his eye; at 20 m it is a win over both.
2. **The human–model comparison is radius-dependent, and the
   crossover is the finding.** At 20 m the model beats the pooled
   cohort (+0.071); at 50 m the cohort's near-perfect precision
   (0.9976) restores a clear human lead (+0.042). Novice error is
   **localisation-dominated** (loose clicks on true mounds); model
   error is **identification-dominated** (FPs and genuine misses
   that no radius forgives). This asymmetry is invisible in any
   single-radius comparison and belongs in the paper's
   human-baseline discussion.
3. **Model weakness concentrates where mounds are sparse.** Lesovo
   (15 reference mounds in-zone) is the only zone where both models
   lose at both radii, driven by precision collapse — consistent
   with the known FP structure: on sparse sheets a handful of FPs
   destroys precision, while novices stay near-silent on empty
   terrain. The empty-tile audit (card § 5) probes exactly this
   regime from the other side.

## Caveats

- Descriptive ranking; no significance tests yet. Zone n_ref spans
  15–164, so per-zone deltas are unequally reliable (Lesovo
  especially).
- The model cells are 20 m-optimised operating points; their 50 m
  rows slightly under-serve the model.
- The reviewed student layer carries a single cleaning pass
  (dedup/merge/collar-clip); Sobotkova 2023's published rates were
  rawer. 9 of 539 reviewed points join the staged master beyond
  10 m (max 2.3 km — merge/curation artefacts); attribution within
  polygons is nonetheless unanimous.
- Students digitised sheet-wide with pan/zoom; the model saw fixed
  tiles. The footprint basis equalises *territory*, not *task*.

## Changelog

### 2026-09-01 — Original publication

Overnight Phase 0a/1a run (Session 145): per-student decomposition
(gate exact), footprint-basis ranking, the full-sheet model-scoring
catch, and the three findings above. Queued next: paired
significance on the zone ranking; the A/C Elenovo-split note for
Table 3 reconciliation; the corrective observation on the GS-4
random-selection framing (card § 4b).
