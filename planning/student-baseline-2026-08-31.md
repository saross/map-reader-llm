# The novice human baseline: hardening student F1/P/R before the paper claims proximity

> **Last revised**: 2026-09-05 (Phase 2 empty-tile audit CLOSED at 500
> tiles and adjudicated: 5 true double-misses, 1.06 % of empty tiles;
> Phase 2b cluster census starts). See [§ Changelog](#changelog).

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
him").

### 2b. Drive scout manifest (agent, 2026-08-31) — both verdicts CONFIRMED

The data spans three Drive locations, not one:
`2022-MapDigitisationModule` (shared drive; QA analysis +
manuscript), `Mound Digitisation from Maps project` (personal My
Drive; the FAIMS campaign exports), and `Publications` (final PDF
only).

- **Per-record attribution CONFIRMED**: every export carries
  `createdBy`/`createdAtGMT` plus a duplicating
  `FeatureAuthor`/`FeatureTimestamp` pair (the latter sometimes in
  local +03:00 rather than GMT — reconcile before analysis), and
  `modifiedBy`/`modifiedAtGMT` for partial edit history.
- **Assignment polygons CONFIRMED**: `Analysis-areas-by-student.shp`
  in `QGIS-work`, with an earlier same-named `.dbf` variant (typo
  filename, richer attribute table — diff both before choosing) and
  companions `Mound-count-by-student.shp` /
  `Error-count-by-student.shp` already spatially joined per student.
- **Pre-curation GS-4 per-student audit FOUND**: the "QA time on
  task" sheet holds a per-tile, per-student pre-cleaning error audit
  for exactly the four GS sheets — error rates 1.71 % (Elenovo),
  2.87 % (K-35-052-4), 7.44 % (Lesovo), **12.42 % (Rakovski)**.
  Early cross-validation for free: the ordering matches our GS-4
  per-sheet FN pattern (Rakovski was our 9.18 % outlier, Obs 316).
- **Raw daily FAIMS server exports** (`rawdata/Entity-YYYYMMDD.csv`
  + `MapDig_ALLfixedNE.csv`) survive alongside the merged "good"
  CSVs — genuine pre-cleaning granularity.
- **Session/time logs** (`RecordingProgress`: per-volunteer session
  start/end) enable time-on-task performance modelling.
- **Reusable pipeline**: `Original-data/README` points to a public R
  loader (github.com/adivea/MapMoundsDigitized, `MapMoundLoad.R`).

**Priority download list** (Drive IDs in the S145 scout report,
archived with the session): (1) `MapMounds17_18allgood.csv` — full
attributed export, 10,825 pts (cross-check headers/row-counts
against the `NEgood` and `withnas` variants before committing to
one); (2) the `rawdata/` daily exports; (3) the whole `QGIS-work`
shapefile set + `QA-workspace.qgz`; (4) "QA time on task" +
`MapDigitisation` assignment log + `RecordingProgress`;
(5) `Mapmounds.7z` (shapefile cross-check) and the four GS
GeoTIFFs if needed. Also inspect the small unopened
`QA-review-2023-02-18-export.7z`.

**Sensitivity**: the `Student-coding-sheet` is the code↔name
de-anonymisation key. Handle per the dormant teaching-data policy
instincts: analysis artefacts committed to this repo use student
CODES only; the key and any personal names stay OUT of the
repository and out of committed outputs.

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

## 4b. Design notes from the 2023 paper (S145 agent synopsis)

Full synopsis:
`docs/methodology/research/claude-sobotkova-2023-synopsis.md`.
Consequences for the phases above:

- **No designed redundancy existed** — the paper reports no
  inter-annotator agreement and proposes multi-student redundancy as
  FUTURE WORK (§ 3.5.2/§ 5). Any overlap the census finds is
  accidental; if usable, Phase 1b literally fulfils the paper's own
  recommendation (quotable framing for the write-up).
- **Paper-derived per-student F1s** (staff-recount truth, agent
  translation): A 0.993, B 0.985, C 0.945, D 0.962 — the ranking
  baseline expectation. The model's nearest target is Student C
  (0.945, the missed-swath case). All four must be RE-computed
  against the curator GT at matched radius before any ranking claim.
- **Sheet↔student alignment**: Table 3 is per-student with no sheet
  names; the Drive QA workbook's per-sheet rates (1.71/2.87/7.44/
  12.42 %) match Table 3's pattern, implying A↔Elenovo,
  B↔K-35-052-4, C↔Rakovski, D↔Lesovo — verify from export author
  fields (Phase 1a gate), never assume.
- **⚠ Selection-bias caveat is unfounded — PI-CONFIRMED
  (2026-08-31)**: the four audited sheets were randomly selected
  from the complete corpus (PI: "randomly selected from the complete
  59-map corpus"; the paper's § 3.5.2 says 4 of 58 — reconcile the
  58-vs-59 sheet count from the export during Phase 1). The
  "chosen for fieldwork-grade reference quality → downward-biased
  FN" framing in the GS-4 report and Obs 316 was a session-side
  confabulation. Random selection STRENGTHENS the 4-sheet estimate.
  Actions queued with Phase 0: corrective observation (new Obs —
  Obs are immutable), and a changelog-attached correction to
  `results/student-gt-fn-rate-analysis-gs4/report.md` § Caveats.
  The 4-GS-vs-55-map FN divergence then needs a different
  explanation: n=4 sampling variance, corpus/era variation, and the
  VLM-mediated lower-bound methodology.
- **Analysis hygiene from the paper**: exclude (or separately report)
  the 32 staff-Tester features; re-map the six symbol classes (four
  are mound-bearing); reconcile the FeatureTimestamp local-time
  quirk; expect multi-instance exports per device; per-feature times
  include form-filling (not a detection-latency comparator);
  distinguish coverage failure (swaths — Student C's 2.8 %
  rate-if-excluded) from perception failure in all reporting.
- The paper assessed **no positional accuracy and no matching
  tolerance** — our matched-radius recomputation (Phase 0a/1a) is
  the first to put these students on a defined tolerance.

## 4c. Queued PI decision — non-Mound points in the canonical reference (found S145)

The Obs 443 verification established that the reviewed 55-map layer's
23 non-Mound entries (16 "Surface feature" — all Student B's own
conscientious typing — plus 5 "Other", 2 "NA"; 81/10,827 = 0.75 %
corpus-wide) are **not review demotions but the volunteers' own
original labels**. Follow-on check: `compute_corrected_f1_multi_buffer.py`
applies no FeatureType filter and the canonical GT carries none, so
these 23 points sit in the 5,160-reference canonical extended GT as
mound references (~0.45 % contamination). Impact is bounded and
symmetric across cells (paired comparisons largely immune; absolute
F1 shifts ≲ 0.003 if removed), but it is a reference-definition
question and therefore a **PI ruling**: filter non-Mound FeatureTypes
in a future GT revision (registered-analysis impact — every 55-map
evaluation would shift by a hair), or document-and-retain. No action
taken; queued for the next interactive register session.

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

### 5b. Mark adjudication protocol (adopted S145, after the first edge case)

Every mark is classified corpus-wide (nearest neighbour at 50 m
across ALL tiles) against: (a) the canonical GT, (b) the deployed
detection sets (arm 2 carried; B-N5 incumbent), (c) both raw unions
(3.7 K=5; G3 K=10, with the 3.7-verifier probability). Classes:
**true double-miss** (nothing anywhere near) / **known-in-GT**
(edge artefact of tile-based emptiness — the first flagged mark was
one: GT point 17.8 m away in the neighbour tile's strip, arm-2-found
at 5/5 votes, missed by every G3-era cell) / **proposed-but-
filtered** (in a union below the operating point) / **detected**.
Only true double-misses count toward the FN floor; the
proposed-but-filtered class separates proposer blindness from
verifier/threshold kills. First adjudication results: 3 marks in the
first ~150 tiles → 1 known-in-GT + 2 true double-misses (nearest
anything 340+ m) — 2/150 ≈ 1.3 % of empty tiles, dead centre of the
card's 1–3 % expectation and consistent with the GS-anchored ~0.9 %
double-miss rate.

**Phase 2 CLOSED at 500 tiles (PI, 2026-09-05; the full 10 % tier plus
30 of the 20 % tier).** Adjudication by `scripts/empty_tile_adjudicate.py`
(protocol above; deployed sets = arm-2 carried 3.7 and the final board's
B-N5-carried; unions = 3.7 K=5 under both verifiers, G3 K=10 under both;
all four union↔probability joins gated) →
`results/empty-tile-audit/adjudication.{json,md}`: **9 marks → 4
known-in-GT (edge artefacts, all also arm-2-detected at 1.2–11 m) + 5
true double-misses (nearest anything 223–731 m)**; the
proposed-but-filtered class is EMPTY — no double-miss had a union
candidate within 50 m, so these are proposer blind spots, not verifier
or threshold kills. All five sit in the 10 % tier (a complete simple
random sample of the 4,676-tile empty frame): **5/470 = 1.06 % of empty
tiles (Clopper–Pearson 95 % 0.35–2.47 %) → ≈ 50 missed mounds in the
frame (16–115) ≈ 0.96 % of the 5,161-point GT (0.31–2.23 %)**. The
frame is the EMPTY stratum only; misses inside occupied tiles are the
cluster census's question (§ 5c). Regenerated 2026-09-06 against the
Ruling-21 standardised reference (§ 5c, reference switch): every class
unchanged (the four known-in-GT marks sit 2.4–30.6 m from a
standardised point), share of GT 0.99 % of 5,010.

### 5c. Phase 2b — the cluster audit (PI-commissioned 2026-09-01)

The empty-tile instrument sees only ISOLATED double-misses; Obs 361's
miss-correlation predicts FNs concentrate in mound groups. Follow-on
review of known-cluster neighbourhoods:

- **Cluster definition**: 2+ canonical-GT mounds single-linkage-
  chained at **≤ 125 m** — the project's own interaction scale
  (Obs 272 attractor-pull significant to 125 m; the FN analysis's
  marginal-tier boundary), sitting between the GT nearest-neighbour
  p10 (83 m) and p25 (164 m) so it captures genuine groups without
  chaining the background (median NN 453 m). Sensitivity framings
  computed S145: X=100 m → 348 clusters/601 tiles; X=150 m → 540
  clusters/839 tiles.
- **Frame at X=125 m**: 464 clusters, 1,006 mounds (19 % of GT),
  **739 evaluation tiles** intersecting the 50 m-buffered clusters —
  small enough for a full CENSUS (no sampling error in this
  stratum; ~1–1.5 h at the observed review pace).
- **Protocol**: the audit app extended with a KNOWN-MOUNDS OVERLAY
  (canonical GT drawn on the tile) so the reviewer marks only
  ADDITIONAL, unrecorded mounds; same adjudication protocol (§ 5b).
- **REFERENCE SWITCHED to the Ruling-21 standardised GT (PI,
  2026-09-06, S148, after 10 census tiles).** The first tile's overlay
  showed two known mounds 52 m apart for one symbol; the reviewer
  flagged the second (`phantom:745`) as a GT error. It was not a review
  error: the canonical review had accepted a real mound, and Ruling 21
  had already removed that phantom as a duplicate of `student:00001` —
  but the census sampler and § 5b drew from the canonical r50 file
  (5,161 points), not the standardised reference
  (`best-available-gt-55maps.geojson`, 4,731 + 279 = 5,010). Of the
  canonical file's 415 phantoms, 176 have no standardised counterpart
  within 15 m (71 of the 72 within 50 m of a same-map student point,
  all 27 at 50–60 m); 151 of the 241 phantoms drawn on the canonical
  census tiles were already-removed duplicates, on 308 of 739 tiles.
  Rebuilt on the standardised reference (`cluster_audit_sample.py
  --gt`, now the default): **334 clusters, 719 mounds, 478 census
  tiles** (465 with overlay) — 270 of the canonical build's 739 tiles
  dropped out and 9 entered (469 shared), the dropped ones
  predominantly "clusters" that existed only through a student point
  and its own duplicate (the frame lost 130 clusters and 287 mounds).
  The 308 figure was re-verified S148 two ways (tile bounds on the
  739 distinct tiles; overlay points mapped back to phantoms), after
  the Obs 449 source check reported 267. The
  canonical build is kept under
  `results/cluster-audit/superseded-canonical-r50-2026-09-01/`; 9 of
  the 10 reviewed tiles remain in the new frame (positions 1–9), the
  dropped tile carrying the phantom:745 flag. The app gained an `o`
  overlay toggle and a "Known (yellow) mound is NOT a mound — GT error"
  symbol, which `empty_tile_adjudicate.py` classes `gt-error-flag`
  (never a double-miss). § 5b's class (a) now reads the standardised
  reference by default; the empty-tile adjudication was regenerated
  against it (see § 5b and `results/empty-tile-audit/adjudication.md`).
- **Explicit scope boundary (PI, 2026-09-01)**: locations where one
  mound was marked but 2–3 truly exist AND no second known mound
  sits within X — singleton undercounts — are NOT discoverable by
  this design; they are covered only by the existing 1,000+
  candidate reviews. The estimand is additional mounds in
  known-cluster neighbourhoods.

### 5d-i. Instrument-design note (PI, 2026-09-01 — note only, do not build)

Empty-tile review proved highly fatiguing: sustained vigilance for
ABSENCE, "tile after tile where nothing is usually there", with
384 px frames forcing back-and-forth eye scanning — one sitting's
budget was ~253 tiles. The PI's design for a purpose-built audit
app: present **verifier-sized chunks assessable at a single glance**
instead of full tiles. Worth recording because it independently
recapitulates the pipeline's own architecture — the verifier's
small-crop-at-a-time primitive is what efficient assessment
converged on for the model too, and it reframes audit-app design as
reviewer ergonomics (single-fixation presence checks over
scanning). The census overlay (yellow anchors) is the interim
mitigation; the chunked app is future work if audits recur.
PI corollary (2026-09-01): the optimum is STAGE-ASYMMETRIC — the
consensus-P+V pipeline's P-R trade favours a LARGE proposal tile
(context boosts recall; consensus + verifier absorb the FP cost)
while assessment, human or machine, wants the small single-glance
window. The ideal human review size and the model's verifier crop
coincide; neither matches the proposal tile.

### 5d. FN image bank (PI-commissioned 2026-09-01)

Build a small image bank of every adjudicated true double-miss at
verifier resolution (the verifier-crop convention), for the paper or
supplement — the PI's reading of the first two is that both were
partly obscured / intersected by other map features, and the crops
are the evidence. Build after the audit closes (final FN set);
script cuts crops centred on the marked positions plus a context
frame, named by order_index and sheet.

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

### 2026-09-06 — Census reference switched to the Ruling-21 standardised GT

After 10 census tiles the reviewer flagged a duplicate known mound that
Ruling 21 had already removed; the census (and § 5b) had been drawing
from the canonical r50 file. Sampler regenerated with `--gt`
defaulting to `best-available-gt-55maps.geojson`: 464 → 334 clusters,
739 → 478 tiles, 2,866 → 1,857 overlay points; canonical artefacts kept
under `superseded-canonical-r50-2026-09-01/`; verdict indices migrated
(9/10 reviewed tiles retained). Adjudication script gained `--gt`
(default standardised) and a `gt-error-flag` class; the empty-tile
report was regenerated with a carried-forward changelog. § 5c text
extended in place with the counts.

### 2026-09-05 — Phase 2 closed at 500 tiles; adjudication run; census tiles staged

The PI closed the empty-tile review at 500 tiles (the full 10 % tier
plus 30 of the 20 % tier; verdicts committed `953b15c46`). New script
`scripts/empty_tile_adjudicate.py` (with tier-1 tests) implements § 5b
end to end and wrote `results/empty-tile-audit/adjudication.{json,md}`:
9 marks → 4 known-in-GT + 5 true double-misses, none
proposed-but-filtered; 5/470 = 1.06 % (95 % CI 0.35–2.47 %) → ≈ 50
missed mounds in the 4,676-tile empty frame (16–115), ≈ 0.96 % of GT.
§ 5b text updated in place. For Phase 2b the 739 census tiles were
fetched from sapphire's `inputs/tiles_384_55maps` tree into the
gitignored `inputs/cluster-audit-tiles/`; every manifest tile and
overlay key verified present.

### 2026-08-31 (later) — Drive scout manifest appended

Agent scout located the full data ecosystem across three Drive
locations; both PI-anticipated assets confirmed (per-record
attribution; assignment polygons), plus unanticipated finds: the
per-tile per-student pre-cleaning GS-4 QA audit (whose per-student
error ordering already matches Obs 316's per-sheet FN pattern), raw
daily FAIMS exports, session/time logs, and a public R loading
pipeline. § 2b carries the condensed manifest and the
priority download list; sensitivity note added for the
de-anonymisation key. Phase 1 is now gated only on downloading.

### 2026-08-31 — Original publication

Drafted at PI direction (S145 interactive) after the audit of both
existing assessments; shape approved in discussion. PI decisions
recorded: 10 % empty-tile sample as default (20 % feasible);
assignment polygons confirmed to exist in the 2023 export; Drive
scout agent dispatched for the export manifest. Phase 0 gated
behind the Gemini 3.7 fourth-cell harvest; Phase 1 gated on the
export; Phase 2 gated on tooling + PI availability.
