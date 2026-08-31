# Sobotkova et al. 2023 — targeted synopsis for the student-baseline programme

> Agent-produced synopsis (Opus subagent, Session 145, 2026-08-31),
> commissioned for `planning/student-baseline-2026-08-31.md`. Read
> against the local PDF in `docs/methodology/references/`; tables
> verified against rendered page images. The PI has flagged that a
> full first-hand read by the lead agent is queued for a later
> session — treat this as the working synopsis until then.

**Paper**: Sobotkova, Ross, Nassif-Haynes, and Ballsun-Stanton 2023,
*Applied Geography* 155: 102967 (open access CC BY, 13 pp.). Page
numbers are the article's own 1–13 pagination.

**Headline caution up front**: the paper contains no inter-annotator
agreement, no designed redundancy, no per-sheet results, no sheet
names, no spatial matching tolerance, and no positional-accuracy
assessment. Several numbers are internally inconsistent (§ 8).
Everything needed for a per-student re-analysis beyond Table 3 must
come from the raw exports.

## 1. Study design: recruitment, training, assignment

**Not open crowdsourcing.** Volunteers were undergraduates in the
TRAP field school, 2017 and 2018 seasons, Yambol region, Bulgaria.
Digitisation was "an ancillary activity" / "auxiliary activity
undertaken on a time-available basis, intentionally secondary to
pedestrian survey" (abstract p. 1; § 4 p. 9), often on rainy days.

**Cohort**: students "came from a range of academic backgrounds in
Arts and Humanities. Most had no training in archaeology,
cartography, or digital methods" (§ 2.2, p. 4). Field-school size
given incidentally as 12 students (§ 2.3, pp. 4–5). Nine distinct
student digitisers appear across Tables 1–2 (A–E in 2017; F–I in
2018), plus a staff "Tester" row in each year.

**Training**: essentially nil by design — "students to begin
digitising after only minutes of training" (§ 2.2, p. 4); "Training
and supervision of students took no more than half an hour of staff
time across the entire season" (§ 3.1, p. 7).

**Assignment**: maps were assigned per student ("participants failed
to digitise some assigned maps", § 3.5.2 p. 7; "three contiguous
sections of an assigned map", § 3.5.2 p. 9). **But the paper never
describes the assignment procedure, never gives a student→sheet
lookup, and never states whether assignment was exclusive.** Fig. 6
(p. 8) shows 2017 and 2018 coverage as largely disjoint blocks with
internal white holes (one ringed "DIGITISATION GAP"); some visible
interleaving near block boundaries is the only published hint any
zone was touched twice.

**Double-marking, redundancy, agreement — the critical finding**:

- The only double-marking reported is **within a single student**:
  "Six were double-marked (Student C digitised a section of a map
  twice)" (§ 3.5.2, p. 9).
- **No inter-annotator agreement statistic of any kind is reported.**
- Multi-volunteer redundancy appears **only as a recommendation for
  future work**: "Simple expedients, such as assigning multiple
  students to digitise the same map tiles independently or assigning
  one student to review work by another, would likely eliminate most
  errors" (§ 3.5.2, p. 9); echoed in the conclusion (§ 5, p. 11).

**Implication**: no consensus-comparable overlap was designed. Any
overlapping zone in the raw exports is accidental (boundary spill, a
redo, a gap-correction session) — a *finding worth reporting*, not a
documented design feature. The double-marking-as-consensus analysis
is exactly the experiment the paper proposes but did not run.

## 2. QA methodology behind ≈5.0 % FN / 0.1 % FP / "under 6 %"

**Design**: "a review by project staff of four randomly selected maps
(7 % of the total)" (§ 3.5.2, p. 7; 4 of 58 sheets = 6.9 %).

**Cost and method**: 6 staff-hours total, "including desktop GIS
setup, confirmation of feature digitisation, and tabulating errors
and error rates" (§ 3.1, p. 7) — the *entire* published description.

**Truth source**: an expert staff re-read of the same sheet in a
desktop GIS ("True feature count" per row). NOT independent ground
truth. No statement of who reviewed, blinding, checking of the
recount, or — critically — **the spatial tolerance for matching a
student point to a symbol**. No buffer, CRS, or datum anywhere.

**Scope — narrower than the headline implies**: Table 3 covers
Students A–D — **four sheets, four students, 2017 only**. Student E
(2017) and the whole 2018 cohort (F–I, 2,463 features) were never
audited. The "error rate under 6 %" generalises this to all 10,827
features.

**Numbers** (Table 3, p. 8): 799 features identified; 834 true; 792
TP; 49 total errors → 5.87 %.

**Denominator conventions (reverse-engineered; never defined)**:
FN and total-error rates use the *true feature count* (42/834 =
5.04 %; 49/834 = 5.88 %); FP and double-marking rates use *features
identified* (1/799 = 0.13 %; 6/799 = 0.75 %).

**Precision/recall/F1 translation** (the synopsis agent's, not the
paper's). Cumulative TP = 792, FN = 42, FP = 1, double-marks = 6:

| Treatment of double-marks | Precision | Recall | F1 |
|---|---|---|---|
| As duplicate FPs | 0.9912 | 0.9496 | **0.970** |
| Excluded | 0.9987 | 0.9496 | **0.974** |

Per student (double-marks as FP): A P 1.000 / R 0.9870 / **F1
0.993**; B 1.000 / 0.9713 / **0.985**; C 0.9803 / 0.9116 /
**0.945**; D 0.9844 / 0.9403 / **0.962**.

## 3. Per-student variation

**Table 1 — 2017** (hours / features / s-per-feature / missing
lat-long / symbol omissions / omission rate): A 28 / 2302 / 44 / 0 /
1 / 0.04 %; B 22.3 / 1799 / 45 / 36 / 4 / 2.2 %; C 27.3 / 1615 / 61
/ 2 / 9 / 0.68 %; D 30.8 / 1526 / 73 / 136 / 2 / 9.04 %; E 17.1 /
1090 / 57 / 18 / 1 / 1.74 %; Tester 0.3 / 11 / 20; overall 125.8 h /
8,343 / 54 s / 192 / 17 / 2.51 %.

**Table 2 — 2018**: F 29.1 / 1305 / 80 / 3 / 0 / 0.23 %; G 25.8 /
810 / 115 / 10 / 1 / 1.36 %; H 8 / 335 / 86 / 0 / 0 / 0 %; I 0.4 /
13 / 103 / 0 / 0 / 0 %; Tester 0.3 / 21 / 60; overall 63.6 h /
2,484 / 92 s / 13 / 1 / 0.56 %.

**Table 3 — errors, 2017 audit only** (identified / FP /
double-marked / FN / classification / total / TP / true count →
rates): A 227/0/0/3/0/3/227/230 → FN 1.3 %; B 203/0/0/6/0/6/203/209
→ 2.9 %; C 305/0/6/29/0/35/299/328 → FN 8.7 %, total 10.6 %; D
64/1/0/4/0/5/63/67 → FN 5.9 %, total 7.4 %. Cumulative 799 / 1 / 6 /
42 / 0 / 49 / 792 / 834 → FP 0.1 %, DM 0.8 %, FN 5.0 %, total 5.9 %.

**Reported spread**: "Students' individual error rates ranged from
1.3 % to 10.6 %" (§ 3.5.2, p. 9) — an 8× spread across four novices.

**Speed–accuracy**: the *opposite* of a trade-off — "the two fastest
digitisers (Students A and B; 44 and 45 s per feature respectively)
also had the lowest error rates (1.3 and 2.9 %), while the two
slowest (Students C and D; 61 and 73 s) had the highest error rates
(10.6 and 7.4 %)" (§ 3.5.2, p. 9).

**The missed-swath case — Student C**: "35 of the 49 false negatives
were the result of Student C failing to digitise three contiguous
sections of an assigned map… excluding Student C would have cut the
cumulative error rate in half to 2.8 %" (§ 3.5.2, p. 9).
[Erratum: should read "35 of the 49 errors" — FN total is 42; 35 is
C's total errors (29 FN + 6 double-marks). The derived 2.8 % =
14/506 is nevertheless correct.]

**Experience/learning**: no within-student learning curve analysed.
2017 averaged 54 s/feature vs 2018's 92 s, attributed to work
pattern (concentrated vs sporadic), not skill (§ 3.2, p. 7).

## 4. Error taxonomy

FN (symbol missed) 42 = 85.7 % of the 49; double-marked 6 = 12.2 %
(all Student C, one contiguous section); FP 1; classification error
0 in the table but 1 in prose ("a similar symbol mistaken for a
benchmark" with "no outright false positives", § 3.5.2 p. 9 —
table and prose disagree on which column that single error occupies).
**Misplacement/positional error is not a category — no positional
accuracy was assessed at all.**

**Symbol vocabulary** (Fig. 2, p. 4), six classes, several with two
glyph variants: burial mound; settlement mound; triangulation point;
triangulation point on a burial mound; bench mark; bench mark (on a
burial mound). **Four of six are mound-bearing** — a mound-only
evaluation must re-map student labels. The bench-mark pair is the
obvious confusion locus for the one classification error.

**The structural claim that matters for a VLM comparison**: "the
pattern of errors — mostly false negatives and double-marked
features, mostly from contiguous map sections — made them relatively
easy to identify and correct" (§ 3.5.2, p. 9). Human error is
*spatially clustered coverage/attention failure at sub-tile scale*,
not per-symbol perception failure. A tiled VLM structurally cannot
exhibit this failure mode, so the raw 5.9 % is a misleading
like-for-like comparator unless swath omissions are handled
explicitly.

**Separate class — recoverable data omissions** (§ 3.5.1, p. 7):
form-completion failures, NOT detection errors. 223 across both
years (205 empty lat/long + 18 missing symbol); cause was the app
failing to populate coordinates when users moved too fast; 203 of
205 recovered by re-extraction, 2 unrecoverable; validation added
for 2018. **Do not conflate with FN/FP**: Student D's 9.04 %
"omission rate" (Table 1) is a form-speed artefact (detection error
7.4 %); Student C is the inverse (0.68 % omission, worst 10.6 %
detection error). The two rankings are nearly orthogonal.

## 5. The four audited sheets

**The paper does not name them** (no "K-35", "Elenovo", "Rakovski",
or "Lesovo" anywhere). Selection was "four randomly selected maps"
— random, post hoc, unstratified. Per-sheet results: none published
(Table 3 is per-student). **If** each audited student digitised
exactly one sheet — the natural but unstated reading — Table 3's
rows are also per-sheet with true counts 230, 209, 328, 67. The
alignment must be verified from the raw exports (author + sheet
fields), not assumed.

[Session-145 note, not from the paper: the Drive "QA time on task"
workbook gives per-sheet per-student error rates — Elenovo 1.71 %,
K-35-052-4 2.87 %, Lesovo 7.44 %, Rakovski 12.42 % — whose ordering
matches Table 3's A 1.3 / B 2.9 / D 7.4 / C 10.6 pattern, implying
A↔Elenovo, B↔K-35-052-4, C↔Rakovski, D↔Lesovo. To be confirmed from
the exports in Phase 1.]

## 6. Efficiency and economics — reusable numbers

**Totals**: 241 person-hours = 57 staff + 184 volunteer → 10,827
features → 44.9 features/person-hour (abstract p. 1; § 4.3 p. 10).
Staff detail: 44 h customisation/deployment (36 programmer ≈ AUD
$2,000 + setup) + 7 h in-field support + 6 h QA. Volunteer detail:
2017 125.8 h / 8,343 features / 42 maps / 54 s per feature; 2018
63.6 h / 2,484 / 16 maps / 92 s; 58 tiles ≈ 23,500 sq km.

**Rates** (§ 4.1.1): ~190 features/staff-hour (all staff); >500
(internal staff only); ~1,550 (in-field staff only); marginal cost
4.3 s staff support per feature; map prep 6 min/sheet; QA checking
≈ 139 features/staff-hour vs 60–75 to digitise from scratch.

**Comparators**: expert desktop GIS 60–75 features/staff-hour;
staff-supervised desktop volunteers 130–180 (from the failed 2010
ArcGIS attempt); the ML benchmark (Can et al. 2021) ≈ 1,300 h
preparation → the 60,000-feature threshold. Table 5 round
thresholds: 4,500 (vs staff GIS), 10,000 (vs desktop volunteers),
60,000 (vs ML); "most suitable for datasets numbering perhaps
10,000–60,000 records".

**Platform ceiling** (§ 3.4): coordinate auto-extraction degraded
past ~2,500 records/device; mitigated by fresh app instances —
**expect the raw exports to be split across multiple instances per
device**.

## 7. What the per-student re-analysis should know

- Cleaning applied pre-publication: lat/long re-extraction (203/205
  recovered), 2018 validation, multi-device export merging, "<2 h"
  post-collection processing (§ 5's figure; abstract says "a few
  hours").
- **The 10,827 vs 127 good/problem split is NOT in this paper** —
  downstream curation, likeliest Sobotkova & Weissova 2020
  (*Archaeological Prospection*, doi 10.1002/arp.1769) or the 2018
  TRAP report. 10,827 includes 32 staff-tester features; a strictly
  volunteer-only count is 10,795.
- **No datum/projection/EPSG named anywhere.** Records carry both
  Lat/Long and Northing/Easting, auto-populated (§ 3.5.1).
- Per-record provenance is native: creation time and author captured
  automatically; full server-side change history (§ 2.4).
- "Time per feature" excludes pauses between records and includes
  attribute transcription — not wall-clock, not detection latency.
- Fig. 6's white areas are real corpus holes (some assigned maps
  never digitised); Student C's swaths are sub-tile holes inside a
  nominally completed sheet — per-student recall that assumes full
  tile coverage will misattribute attention failure as perception
  failure. Use the assignment polygons.
- No dataset DOI or deposit; only the customisation code
  (github.com/FAIMS/map-digitisation, tag map-dig-2018).
- Comparability caveats for the VLM baseline: sheet-wide pan/zoom
  work vs fixed tiles; form-filling in the timing; six symbol
  classes needing re-mapping; swath-omission failure mode; Table 3's
  truth is one staff re-read at an unstated tolerance — recomputed
  per-student P/R/F1 against the curator GT will legitimately
  differ.

**Future work the re-analysis fulfils** (quotable): multi-student
redundancy/peer review (§ 3.5.2 p. 9; § 5 p. 11); "train and
error-check a ML model, to more systematically compare the results
of crowdsourcing versus machine learning" (§ 5); the call for
projects to publish time/error/type accounting (§ 5);
crowdsourcing-ML complementarity (§ 4.2); the authors' own "single
data point" caveat (§ 5).

## 8. Internal inconsistencies to cite carefully

1. Volunteer hours 184 (abstract, § 4.3, § 5) vs 189.4 (Tables 1–2 +
   Fig. 3); the 241-hour and 44.9/hour headlines use 184.
2. "35 of the 49 false negatives" should be "35 of the 49 errors".
3. "no outright false positives" contradicts Table 3's one FP.
4. Table 4's mid volunteer cell 3,000 is likely a typo for ~3,800.
5. Student C's published 8.7 %/10.6 % recompute to 8.84 %/10.67 %.
6. 2018 omission "0.52 %" is spatial-only; with attributes 0.56 %.
7. Rate denominators are never defined (FN/total on true count;
   FP/DM on identified).
8. Post-processing effort stated three ways; "<2 h" is the most
   specific.
