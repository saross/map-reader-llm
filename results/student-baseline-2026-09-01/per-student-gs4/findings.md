# The novice baseline decomposed: students and configs on identical ground

> **Last revised**: 2026-10-30 (restated against the S164-restated model
> cells, PI ruling D70: the model rows rise on the two Elenovo zones and in
> the pooled rows; Student A no longer edges the model at 20 m; no
> significance verdict changes). Prior: 2026-10-18 (a dated note that the
> model rows predated the restatement). 2026-09-01: original publication.
> See [§ Changelog](#changelog) for revision history.

**Classification**: Phase 0a/1a of the student-baseline programme
(`planning/student-baseline-2026-08-31.md`), run overnight on PI
authorisation (2026-08-31 "proceed through the analysis as far as
you can"). Significance via the board's tile-swap instrument —
§ Significance. All numbers: `analysis.json` / `per_student.csv` /
`significance.json` alongside this file.

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
values sit within 0.01 of its committed corpus-wide figures (0.9289
vs 0.9364 @20 swap; 0.9165 vs 0.9238 screen), validating the
instrument.

## Ranking on identical ground (footprint basis)

At **20 m** (the GS working radius), pooled over all five zones
(n_ref = 435):

| Rank | Contender | P | R | F1 |
|---|---|---:|---:|---:|
| 1 | **all-3.7 model** | 0.9268 | 0.9310 | **0.9289** |
| 2 | 3.7-text-screen model | 0.9002 | 0.9333 | 0.9165 |
| 3 | students (pooled) | 0.8678 | 0.8299 | 0.8484 |

At **50 m**:

| Rank | Contender | P | R | F1 |
|---|---|---:|---:|---:|
| 1 | **students (pooled)** | 0.9976 | 0.9540 | **0.9753** |
| 2 | all-3.7 model | 0.9405 | 0.9448 | 0.9427 |
| 3 | 3.7-text-screen model | 0.9135 | 0.9471 | 0.9300 |

Per zone at 20 m: the model wins Rakovski[C] decisively (0.9789 vs
0.7492) and loses Lesovo[D] decisively (0.7059 vs 0.8966; n_ref
only 15, and model precision collapses to 0.46–0.63 on that sparse
sheet); B edges the model narrowly on its zone (0.9462 vs 0.9239),
and on the two Elenovo zones the model now edges the students narrowly
(A's: 0.8889 vs 0.8718; C's: 0.9438 vs 0.9195), where both students
led before the restatement (the model then read 0.8646 and 0.9070);
none of the three differences is significant. At 50 m every student
except C beats
both models on their own zone; the model still beats C on Rakovski
(0.9849 vs 0.9587).

## Significance (tile-swap permutation + BH)

The board instrument (per-tile micro-F1 tile-swap permutation,
10,000 draws, seed 42; per-tile counts gate-exact against the zone
confusion counts) over a declared 14-test family, BH q = 0.05
(`significance.json`; diff = students − model, positive = humans
ahead):

- **20 m, pooled**: the model leads the cohort SIGNIFICANTLY — all-3.7
  −0.0805 (adj p < 0.0001), screen −0.0681 (adj p = 0.0053). Zone-wise
  only the Rakovski rout is significant (C: −0.2296, adj p < 0.0001);
  B, D, and the two Elenovo comparisons are ns at 20 m.
- **50 m, pooled**: the cohort leads SIGNIFICANTLY — +0.0327 vs
  all-3.7 (adj p = 0.0119), +0.0453 vs screen (adj p = 0.0014).
  Individually, A (+0.0769, adj p = 0.0053), B (+0.0546, adj
  p = 0.029), and D (+0.2008, adj p = 0.029) each significantly beat
  the model on their own ground; both C zones are ns — Student C is
  the only novice the model does not significantly lose to at 50 m.

The radius crossover is therefore statistical, not descriptive, in
both directions.

## The three findings

1. **The PI's bet lands: the model beats at least one student.**
   The all-3.7 stack beats Student C on his main sheet decisively at
   20 m (0.9789 vs 0.7492, BH-adj p < 0.0001); at 50 m its edge is
   not significant, but C is the only novice the model does not
   significantly lose to there. C is not a strawman: excluding his
   three digitised missed-swath polygons (coverage failure), his
   50 m performance is excellent (0.9916). The model's advantage
   over C is over his *coverage and localisation*, not his eye.
2. **The human–model comparison is radius-dependent, and the
   crossover is the finding — now statistically in both directions.**
   At 20 m the model beats the pooled cohort (+0.080, BH-adj
   p < 0.0001); at 50 m the cohort's near-perfect precision (0.9976)
   restores a clear human lead (+0.033, BH-adj p = 0.012). Novice error is
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

- Zone n_ref spans 15–164, so per-zone deltas are unequally
  reliable (Lesovo especially: its +0.19/+0.20 deltas reach
  significance only at 50 m on 15 reference mounds).
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

### 2026-10-30 — Restated against the restated model cells (PI ruling D70)

**Trigger.** The S164 restatement (PR #52, merged as `0d195cac8`) re-verified
the wrong-sheet candidates and moved both model cells this analysis scores.
`scripts/student_perstudent_gs4.py` and
`scripts/student_ranking_significance.py` were re-run on them (Session 166,
$0; the replication gate passed); the PI ruled to restate in place.

| Figure | Before | After |
|---|---|---|
| All-3.7 model, pooled F1 at 20 m / 50 m | 0.9190 / 0.9329 | 0.9289 / 0.9427 |
| 3.7-text-screen model, pooled F1 at 20 m / 50 m | 0.9066 / 0.9203 | 0.9165 / 0.9300 |
| Model on A's Elenovo zone at 20 m (both models) | 0.8646 | 0.8889 |
| Model (all-3.7) on C's Elenovo zone at 20 m | 0.9070 | 0.9438 |
| 20 m pooled, students − model (all-3.7; screen) | −0.0706, adj p 0.0017; −0.0582, 0.017 | −0.0805, < 0.0001; −0.0681, 0.0053 |
| 50 m pooled, students − model (all-3.7; screen) | +0.0425, adj p 0.0017; +0.0551, < 0.0001 | +0.0327, 0.0119; +0.0453, 0.0014 |
| A's zone at 20 m, A − all-3.7 | +0.0072 (p 0.85) | −0.0171 (p 0.67) |
| A's zone at 50 m, A − all-3.7 | +0.1006, adj p 0.0009 | +0.0769, adj p 0.0053 |

**What changed in reading**: Student A no longer edges the model at 20 m,
and on C's Elenovo zone the model now leads at 20 m; neither difference is
significant, before or after.

**What did NOT change**: every student value; zones B, Rakovski and Lesovo,
whose model values do not move; every significance verdict
of the 14-test family; the three findings and the radius crossover. The
significance paragraph's "three Elenovo comparisons" was corrected to two
(the family has two Elenovo zone tests per radius).

**Commit**: see `git log` for this entry's date.

### 2026-10-18 — Dated note: the model rows predate the restatement

A note under the banner records that the two model rows, and every
comparison and test that uses them, predate the S164 restatement
(PR #52), which lifted both model rows by about 0.01 at 20 m. Nothing else
changes; the re-score follows PR #52 (PI ruling D69, restatement record
§ 10 Q8). Commit: the one that applies this entry.

### 2026-09-01 — Original publication

Overnight Phase 0a/1a run (Session 145): per-student decomposition
(gate exact), footprint-basis ranking, the full-sheet model-scoring
catch, and the three findings above; significance added same day
(tile-swap instrument, two gate-caught scoping fixes recorded in the
script). Queued next: the A/C Elenovo-split note for
Table 3 reconciliation; the corrective observation on the GS-4
random-selection framing (card § 4b).
