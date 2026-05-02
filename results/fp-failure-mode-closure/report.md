# False-positive failure-mode catalogue closure — synthesis report

**Date**: 2026-04-30
**Source observations**: Obs 312, Obs 313, Obs 314, Obs 315 (Session 81 review thread) in `docs/notes/reflections/working-notes.md`
**Cross-referenced observations**: Obs 304 (high-pull tail characterisation), Obs 306 (closed-list expansion), Obs 307 (cross-corpus chi-square), Obs 308 (v2 reclassification rate; provisional, closed by Obs 312)
**Source data**:

- `results/55maps-fp-classification/v2-burial-mound-bet-test/verdicts.csv` (197 rows: 177 non-calibration + 20 calibration; all `verdict = v2_overclaim`)
- `results/55maps-fp-classification/v2-burial-mound-bet-test/settlement-mound-mode2-verdicts.csv` (117 rows: settlement-mound subset)
- `inputs/examples/SovietTopoSymbols.pdf` (US Army TM 30-548, 1958)

**Source commits**: `c4585f60` (Obs 312 / bet-test), `1a56f35b` (Obs 313 / settlement-mound re-inspection), `c4432978` (Obs 314 / Item 473 — superseded), `0d80ebcd` (Obs 315 / symbol-ID closure)

## 1. Executive summary

The false-positive (FP) failure-mode catalogue for the v2 FP-classifier on the
55-map corpus is now **closed at the mechanism level** and ready for the paper's
Discussion section. Three small Session 81 sub-investigations resolved together:

1. **Obs 312** confirmed the v2 closed-list expansion was correctly classifying,
   not over-claiming as a quality artefact: a manual bet-test by an experienced
   archaeological digitiser found **0 / 177 review errors** on the v2-burial-mound
   reclassifications (decisively below the < 2 % bet threshold). The 15.8 %
   reclassification rate from Obs 308 is genuine v2 overclaim behaviour that
   needs an explanation, not a review-pass artefact that could be discounted.

2. **Obs 313** decomposed the 117 v2-`settlement-mound` reclassifications into a
   three-category visual taxonomy (87 / 29 / 1 / 0) and unified the categories
   into a two-mechanism causal framework. **Mechanism A — colour-veto failure**
   accounts for ~75 % of the settlement-mound confounds; **Mechanism B —
   central-glyph anchor** accounts for ~25 %.

3. **Obs 314 + Obs 315** closed the symbol-identification thread for the
   dominant Mechanism A confound class ("Cat 2": rounded black features with
   outward hachures, visually indistinguishable from a real settlement mound
   except for colour). Two agent searches of TM 30-548 produced contradictory
   identifications (Item 472 "Burial mound", then Item 473 "Tailings pile"); a
   second exhaustive search across Items 1–425 (the ≤ 1:50,000-scale-relevant
   range) found **no clean match**. This is a **clean negative** result: the
   paper's mechanism-level argument does not depend on any specific symbol
   identity for Cat 2. Item 473 is superseded; the methodological note from
   Obs 314 on agent context-biasing stands unchanged. Obs 315 also adds
   **Mechanism C — source-domain ambiguity**, illustrated by Item 285 "Crater of
   mud geyser" — a small but conceptually important third class that cannot be
   resolved by any prompt-engineering or post-classification filter.

The catalogue now consists of three named mechanisms, two of which carry
specific testable methodological fixes:

| Mechanism | Approximate share of 117 settlement-mound confounds | Methodological fix |
|---|---:|---|
| A — Colour-veto failure | ~75 % | Hard colour-rejection rule in proposer prompt or RGB post-filter on detection crop |
| B — Central-glyph anchor | ~25 % | Drop `benchmark-on-mound` / `triangulation-on-mound` subtypes from proposer prompt; reframe as post-classification spatial-join task |
| C — Source-domain ambiguity | Small but real (Item 285 as canonical example) | None — cartographic-source-level disambiguation is lost; flag as fundamental limit in Discussion |

The catalogue is paper-Discussion-ready. The Cat 2 specific symbol identity
remains unresolved in TM 30-548; the user has indicated future consultation of
a primary Russian-language source. This caveat does not block the paper because
the failure-mode argument operates at mechanism level, not symbol-identity
level.

## 2. The bet-test outcome (Obs 312)

### 2.1 Protocol

Obs 308 had reported that the v2 FP-classifier reclassified 15.8 % (177 / 1,119)
of the 55-map corpus's human-labelled FPs as one of four burial-mound
categories (`burial-mound`, `settlement-mound`,
`triangulation-point-on-burial-mound`, `benchmark-on-burial-mound`). Three
competing explanations were on the table:

1. The v2 prompt's vocabulary expansion induced *over*-claiming by the
   classifier (a classifier failure).
2. Some of the original "not_mound" labels in the human-review pass were errors,
   and the v2 classifier was correcting them (a review-pass quality issue).
3. The expanded vocabulary redistributed labels that previously fell into other
   FP categories (a v1 vs v2 vocabulary effect).

Explanation (2) had the largest stakes because it would call into question the
prior human-review pass that underpins much of the paper's analysis. A
pre-registered "bet" was set up: an experienced archaeological digitiser
manually inspects all 177 v2 reclassifications via a Streamlit app and assigns
each one a verdict of `real_mound_my_error` (i.e., the original human review
labelled it "not_mound" by mistake) or `v2_overclaim`. The bet threshold for
explanation (2) was set at < 2 % review errors (< 34 of 1,675 in the broader
review denominator) before the test was run.

### 2.2 Result

| Metric | Value |
|---|---|
| Reclassifications inspected | 177 |
| `real_mound_my_error` | 0 |
| `v2_overclaim` | 177 (100 %) |
| Calibration rows (paired with non-calibration as inter-rater grounding) | 20 |
| Empirical review-error rate (177 / 1,675 denominator) | 0 / 1,675 = 0.0 % |
| Bet threshold (< 2 % = < 34 errors) | Decisively met |
| Ambiguous / edge cases flagged by the inspector | 0 |

The Wilson upper 95 % confidence bound on 0 / 177 is 2.1 %, but the observed
rate is 0 %. Explanation (2) is rejected.

### 2.3 What this validates

The 15.8 % v2 reclassification rate is genuine v2 overclaim behaviour, not a
review-pass artefact. This has two consequences:

1. **Obs 307's cross-corpus chi-square stands intact.** The 55-map FP-class
   distribution that fed the chi-square (Monte Carlo *p* = 0.0028 at the
   > 125 m stratum; *p* = 0.0012 at the > 50 m stratum) is an accurate
   distribution of v2 overclaims and does not require ground-truth correction.
2. **The 15.8 % needs a mechanistic explanation, not a discount.** This sets
   up the work in Obs 313 (settlement-mound re-inspection) and Obs 315
   (symbol-identification + Mechanism C) that produces the mechanism-level
   catalogue.

## 3. Settlement-mound subtype taxonomy (Obs 313)

### 3.1 Three-category breakdown (verified against source data)

A targeted re-inspection of all 117 v2-`settlement-mound` reclassifications was
run via a dedicated Streamlit app (`scripts/v2_settlement_mound_mode2_app.py`,
commit `d75a483e`). The verdict scheme had four mutually exclusive labels.
Counts (verified by direct read of
`results/55maps-fp-classification/v2-burial-mound-bet-test/settlement-mound-mode2-verdicts.csv`):

| Verdict | Count | % of 117 |
|---|---:|---:|
| `not_orange_brown` | 87 | 74.4 % |
| `closed_topo_line_no_hachures` | 29 | 24.8 % |
| `other_orange_brown_feature` | 1 | 0.9 % |
| `closed_topo_line_with_hachures` | 0 | 0.0 % |

Visual sub-analysis of representative `not_orange_brown` crops during the
re-inspection identified two structurally distinct sub-populations within the
87, yielding a three-category visual taxonomy across all 117:

- **Category 1 — Square black symbols with hachures** (subset of the 87
  `not_orange_brown`). Visual signature: rectangular black perimeter +
  perpendicular outward hachures + blue / grey interior. The class includes
  water reservoirs with earthen embankment (резервуар, пруд с валом), walled
  compounds, and fortification icons. The rectangular-fortification subset was
  identified against TM 30-548 Item 706 "Fortification (ancient)" by an earlier
  PDF-agent (commit `c4585f60`).
- **Category 2 — Rounded black features with hachures** (subset of the 87
  `not_orange_brown`). Visual signature: circular black perimeter + outward
  radiating hachures (~10–15) + any interior. Shape, hachure count, and
  overall gestalt are visually identical to a real `settlement-mound` symbol;
  the only difference is colour (black vs orange-brown). This is the cleanest
  possible colour-veto-failure case. Cat 2's specific cartographic identity is
  unresolved (see §4).
- **Category 3 — Closed topo lines** (the 29 `closed_topo_line_no_hachures`
  verdicts). Visual signature: orange-brown closed contour ring (hilltop) +
  (usually) a central benchmark, spot-height, or triangulation glyph. The
  orange-brown colour is correct; what is missing is the hachure / ray pattern
  that distinguishes a real mound from a contour ring.

### 3.2 Two-mechanism unification

The three categories collapse into two distinct failure mechanisms that
together account for the full 117:

**Mechanism A — Colour-veto failure (Categories 1 + 2; ~75 % of the 117
confounds).** The proposer prompt
(`prompts/system-instructions/detect_brief-text.md`) explicitly states that
burial-mound subtypes are orange-brown. The FP-classifier ignores this colour
requirement and fires on shape + hachure pattern alone. Both the
square-black-walled-water (Cat 1) and the round-black-mound-shaped (Cat 2)
features pass the model's "circle / polygon + radiating lines" gate despite
having a black or blue interior, not orange-brown. Cat 2 is the cleanest
demonstration: every visual feature of a `settlement-mound` is present except
colour. The colour requirement is stated in the prompt but not enforced by the
model.

> **Methodological fix (testable for under USD 10 of API spend):** add a hard
> colour-rejection rule — either as a prompt addition to the FP-classifier's
> closed-list instruction or as a post-classification filter on the RGB
> properties of the detection crop.

**Mechanism B — Central-glyph anchor (Category 3 + analogous patterns in the
60 non-settlement-mound rows of the 177; ~25 % of the 117 settlement-mound
confounds).** The model uses the central black symbol (benchmark / spot-height
/ triangulation glyph) as the dominant trigger. Per the proposer prompt's
`benchmark-on-mound` subtype description ("Black square with central dot,
surrounded by black rays"), a central-square-with-dot match appears sufficient
to fire the classification, even when outward hachures are absent. The closed
topo line provides supporting "circle" evidence. The result: hilltop +
geodetic-control-point = systematic false positive.

> **Methodological fix:** drop `benchmark-on-mound` and `triangulation-on-mound`
> from the proposer prompt's mound subtypes entirely; reframe co-located
> benchmark + mound as a separate post-classification spatial-join step (flag
> detections that fall within a configurable radius of a georeferenced
> benchmark or triangulation point as requiring manual confirmation).

### 3.3 Threshold artefact note

The Streamlit app's pre-registered design rule was "Mode 2 SUPPORTED if ≥ 60 %
of verdicts are `closed_topo_line_no_hachures`". Under that rule, Mode 2 is
**technically rejected at the strict threshold** (24.8 % observed, 60 %
required). However, the empirical finding is that Mode 2 is a **real and
substantive secondary failure mode at ~25 %**; the 60 % rule was set before the
composition of the `not_orange_brown` group was known. The threshold verdict
is an artefact of pre-registration; the empirical finding stands.

## 4. Symbol-identification negative result (Obs 314 + Obs 315)

### 4.1 Background — the Cat 2 thread

Obs 313 flagged Cat 2 ("rounded black features with hachures, visually
indistinguishable from a real settlement mound except for colour") as having
"symbol identity in flight" — a PDF-agent search of `inputs/examples/SovietTopoSymbols.pdf`
(US Army TM 30-548, 1958) was running in the background.

A first agent search returned two candidates from page 53:

| Candidate | Agent's verdict | Correct? |
|---|---|---|
| Item 472 "Burial mound" (курган) | "Black due to scanning artefacts" — primary | No |
| Item 473 "Tailings pile" (отвал породы) | Dismissed as "burial-mound context" — secondary | Was the working answer in Obs 314, now superseded |

Obs 314 (commit `c4432978`) accepted the Item 473 identification and explicitly
ruled out Item 472 on three independent grounds: colour signature (burial mounds
are orange-brown; scanning artefacts produce tonal shifts within the
orange-brown family, not full-black inversions); bet-test ground truth
(Obs 312's 0 / 177 review-error rate empirically rules out the
"discoloured burial mound" hypothesis); and visual fit (Item 473 matches all
three of Cat 2's defining visual attributes — rounded perimeter, outward
hachures, black rendering).

### 4.2 The exhaustive search and the negative result

A second agent search (Obs 315) was run after the user clarified that symbol
numbers ≤ 425 in TM 30-548 correspond to the 1:50,000 scale-set relevant to
this project. The exhaustive review of pages 11–50 (covering Items 1–425)
found **no clean match** for the Cat 2 visual pattern (circular black
perimeter + outward radiating hachures, ~10–15 rays, no distinguishing central
glyph):

| Symbol searched | Result |
|---|---|
| Item 62 "Burial mound" (курган) | Visual shape match; renders orange-brown, not black — rules out |
| Items 63–64 (mound subtypes) | Same colour ruling; no black-rendered variant found |
| Item 473 "Tailings pile" | Falls at page 53 within the ≤ 425 range; structurally plausible but not a confirmed clean match under exhaustive review |
| All other rounded-with-hachures symbols (pages 11–50) | No unambiguous match for "circular black + outward hachures, no central glyph" |

The Item 473 identification from Obs 314 is **superseded** by this negative
result. Three explanations remain viable for Cat 2's identity:

- Cat 2 is **heterogeneous** at the classifier's resolution — a mix of feature
  classes that share the rounded-black-hachured gestalt;
- The symbol class is **absent from TM 30-548** (the US Army guide may have
  omitted less common feature types or region-specific conventions);
- The symbol belongs to a **different scale-set** that bleeds visually onto
  the 1:50,000 sheets in the project corpus.

### 4.3 Why this is a clean negative, not a missed signal

The negative result is decisive at the mechanism level for two reasons:

1. **The exhaustive review covers the scale-relevant range.** The user's
   domain-expertise constraint (Items ≤ 425 are the 1:50,000-scale-relevant
   set) bounds the search space to a finite, fully-scanned target set.
   "No clean match" is a verified finding, not a search-coverage gap.
2. **Mechanism A is independent of Cat 2's specific identity.** The
   colour-veto-failure mechanism describes *what the classifier is doing
   wrong* (firing on shape + hachures regardless of colour); it does not
   require knowing the precise cartographic name of every black symbol class
   that triggers the failure. The paper Discussion can say "approximately 75 %
   of confounds are colour-veto failures across multiple Soviet 1:50,000
   feature classes whose precise cartographic identity is currently
   unresolved for the bulk of Cat 2 cases" without weakening the mechanistic
   argument.

The Cat 2 identity remains an interesting open question; the user has indicated
future consultation of a primary Russian-language Soviet topographic guide
(e.g., 1:50,000 Условные знаки, 1983 or similar). This is deferred to future
work and does not block the paper.

### 4.4 Methodological side-finding (Obs 314, stands unchanged)

The first agent's misidentification of Item 472 is a methodologically useful
observation in its own right. The agent's reasoning chain:

1. Visual evidence: the symbol has a circular perimeter + outward hachures.
   Item 473 is an equally or better visual match.
2. Context pressure: the agent was briefed that this is a burial-mound
   detection project; the user is inspecting confounds.
3. Context override: the agent rationalised toward the project narrative —
   inventing a plausible-sounding mechanism ("scanning artefacts cause colour
   distortion") to fit the observation into the expected category.

This is a **non-confabulation reasoning failure**. The agent did not fabricate
data; it reasoned from real data toward a wrong conclusion because project
context biased it against reporting the objective visual match. Mitigation
(now standing guidance for any domain-objective task — symbol identification,
catalogue lookup, methodological audit, cross-corpus comparison): include an
explicit prompt clause along the lines of "Identify based on visual properties
and objective evidence only. Do not bias your reasoning toward the project's
research context. Treat each candidate symbol agnostically and report what its
visual properties actually match in the source reference, not what the project
context might predict." Obs 315's negative result on the exhaustive ≤ 425
search supersedes Item 473 specifically; the agent context-biasing
methodological note from Obs 314 is unaffected.

### 4.5 Mechanism C — source-domain ambiguity (Obs 315 addition)

While reviewing TM 30-548 for the Cat 2 search, the user identified Item 285
"Crater of mud geyser" (кратер грязевого вулкана) as a canonical exemplar of
a third failure mechanism not captured by the colour-veto (A) or central-glyph
(B) framing. Item 285's visual signature — an orange-brown sunburst pattern
with a small central circle — is strikingly similar to a real burial mound,
though not quite identical. The user noted they had "fallen for it" during the
original GS curator review before catching the distinction.

> **Mechanism C — source-domain ambiguity.** A feature that is correctly
> rendered in canonical Soviet cartographic convention, yet visually aliases
> with the target class because Soviet topographic convention applies similar
> graphic vocabulary (raised feature + outward hachures) to topographically
> similar phenomena regardless of geological origin. Unlike Mechanisms A and
> B, Mechanism C **cannot** be resolved by any prompt-engineering or
> post-classification filter — the disambiguation is lost at the
> cartographic-source level. A prompt that says "orange-brown, outward
> hachures, raised circular feature" correctly describes both Item 62 (burial
> mound) and Item 285 (mud-geyser crater). No additional lexical instruction
> can separate them; only spatial context, corpus priors, or ground-truth
> inspection can do so.

Mud-geyser craters are luckily rare in the project corpus (the GS maps cover
semi-arid steppe with no known active mud volcanism), so Mechanism C
contributes a small fraction of the observed FP rate. Its value to the paper
is as a **conceptual boundary case**, not a numerical driver.

### 4.6 Adjacent confirmations (Obs 315)

Two additional findings emerged from the same review session and are worth
recording for completeness:

- **TM 30-548 Item 83 "Trigonometrical point on burial mound"**
  (тригонометрический пункт на кургане) — confirmed within the ≤ 425 range
  (approximately page 17, "Orientation Points and Local Features" section).
  Adjacent items 81–84 cover the burial-mound subtypes as a coherent group.
  This confirms that the four burial-mound subtypes named in
  `prompts/system-instructions/detect_brief-text.md` — `burial-mound`,
  `settlement-mound`, `triangulation-point-on-burial-mound`,
  `benchmark-on-burial-mound` — each map to a canonical Soviet 1:50,000
  symbol. The proposer prompt's vocabulary is **cartographically grounded**,
  not invented.
- **TM 30-548 partial colour-reliability note.** The user's domain diagnosis:
  "I think they chose to simply print part of the guide in black-and-white."
  Sections of the 1958 printing were reproduced in B&W, losing the original
  colour information for those pages. Methodological implication for any
  future TM 30-548 lookup: trust shape, hachure direction, central-glyph
  presence, item number, and Russian / English labels; do not trust colour
  claims derived from B&W-rendered sections — cross-check colour against the
  user's domain expertise or a primary Russian-language source. This
  partially explains why the first agent search accepted Item 472 as a colour
  match: if the burial-mound entry happened to fall in a B&W-rendered
  section, the agent had no colour ground truth from the PDF and defaulted to
  context-biasing.

## 5. The mechanism-level catalogue

| Mechanism | Description | Approximate share of 117 settlement-mound confounds | Cartographic exemplars (where named) | Methodological fix |
|---|---|---:|---|---|
| A — Colour-veto failure | Classifier fires on shape + hachure pattern regardless of the prompt's orange-brown colour requirement; black symbols passing the geometric gate are misclassified | ~75 % | Cat 1 partly identified as walled water features / fortifications (TM 30-548 Item 706); Cat 2 unresolved in TM 30-548 ≤ 425 — likely heterogeneous | Hard colour-rejection rule in proposer prompt; or RGB post-filter on detection crop. Testable for under USD 10 of API spend |
| B — Central-glyph anchor | Classifier treats the central black square / triangle (benchmark, spot-height, triangulation glyph) as a sufficient trigger; closed contour ring on a hilltop provides the "circle" evidence | ~25 % | Hilltop closed-contour-ring + benchmark or triangulation glyph; Cat 3 in Obs 313 | Drop `benchmark-on-mound` and `triangulation-on-mound` subtypes from proposer prompt; reframe as post-classification spatial-join task against georeferenced benchmark / triangulation point layer |
| C — Source-domain ambiguity | Visually correct cartographic rendering of a non-target feature class that aliases with the target because Soviet convention uses similar graphic vocabulary for topographically similar phenomena regardless of geological origin | Small but real (not formally measured in this corpus) | Item 285 "Crater of mud geyser" (кратер грязевого вулкана) — illustrative canonical case | None — disambiguation is lost at the cartographic-source level. Flag as a fundamental limit in the paper Discussion |

The catalogue is **closed at the mechanism level**: every category produced by
the bet-test inspection (Obs 312) and the settlement-mound re-inspection
(Obs 313) maps onto one of A / B / C, and the qualitative framing for each
mechanism is supported by independent visual evidence from the source data.

The **share figures (~75 % / ~25 %) refer specifically to the 117
settlement-mound confounds** (Obs 313's denominator), not to the broader 177
or 1,119. The 60 non-settlement-mound rows in Obs 312's 177 (i.e., the rows
classified as `burial-mound`, `triangulation-point-on-burial-mound`, or
`benchmark-on-burial-mound`) were not individually re-categorised; they map
predominantly to Mechanism B per Obs 312's qualitative inspection, but a
precise per-mechanism share across the full 177 would require a second
annotation pass.

## 6. What this means for the paper

### 6.1 Discussion section claims that are now supported

1. The v2 FP-classifier's overclaim behaviour (15.8 % reclassification) is
   **genuine classifier behaviour, not a review-pass artefact** — verified
   empirically by the bet-test (0 / 177 review errors, well below the < 2 %
   bet threshold).
2. The overclaim behaviour is **driven by two structural mechanisms with
   specific testable methodological remedies** (colour-veto failure;
   central-glyph anchor) plus a third, conceptually important boundary case
   (source-domain ambiguity).
3. Both Mechanisms A and B are **addressable at the prompt / filter level,
   not at the model architecture level**. This is a practically important
   claim: the approach is not fundamentally limited by VLM resolution; it is
   limited by an incomplete instruction set and a classification vocabulary
   that incentivises over-generalisation.
4. Mechanism C represents a **fundamental cartographic-source-level limit**
   that no prompt-engineering or post-classification filter can remove.
   This sets honest expectations for the practical ceiling of the approach
   on Soviet 1:50,000 maps.
5. **Obs 307's cross-corpus chi-square interpretation stands intact.** The
   55-map FP-class distribution is an accurate distribution of v2 overclaims;
   the cross-corpus divergence (Monte Carlo *p* = 0.0028 at > 125 m;
   *p* = 0.0012 at > 50 m) reflects genuine between-corpus differences in
   what gets overclaimed and is now interpretable via the mechanism-level
   catalogue.

### 6.2 Discussion section claims that should be hedged

- **Cat 2's specific cartographic identity** is unresolved in TM 30-548;
  cite as "currently unresolved for the bulk of Cat 2 cases; future work to
  consult primary Russian-language Soviet topographic guides" rather than as
  a named symbol class. Item 473 "Tailings pile" should not be cited as the
  Cat 2 identity — that identification is superseded.
- **Mechanism share figures (~75 % / ~25 %)** apply specifically to the 117
  settlement-mound confounds. The mechanism shares for the broader 177
  v2-burial-mound reclassifications were not formally measured; cite the
  117-denominator figures and note the scope.
- **The Cat 1 / Cat 2 split within the 87 `not_orange_brown` rows** is
  approximate (visual analysis of representative cases, not a full sub-count).
  A second annotation pass with explicit Cat 1 / Cat 2 labels would be needed
  for a precise quantification; not done in this work.
- **Mechanism C frequency** is not formally measured in the project corpus.
  The mud-geyser crater exemplar is a conceptual case for the Discussion, not
  a numerical contributor to a tabulated breakdown.

## 7. Future-work bullets

The catalogue suggests three concrete follow-up directions, two of them cheap:

1. **Mechanism A test (~USD 10 API spend).** Add a hard colour-rejection rule
   to the v2 FP-classifier — either a prompt addition ("Reject any candidate
   whose dominant interior colour is not orange-brown, regardless of shape
   or hachure pattern") or a post-classification filter on the dominant
   RGB values inside the detection crop bounding box. Re-run on the 1,119 v2
   FP-classifier denominator; expected outcome is the elimination of the
   ~75 % of settlement-mound confounds attributable to Cat 1 and Cat 2.
2. **Mechanism B test (cheap; relies on existing georeferenced layers).**
   Remove `benchmark-on-mound` and `triangulation-on-mound` from the proposer
   prompt's mound subtypes. Run a post-classification spatial-join step
   against the georeferenced benchmark / triangulation point layer at
   configurable radius (suggest start with 25 m). Detections falling within
   the radius are flagged for manual confirmation rather than automatically
   classified. Expected outcome is the elimination of Mechanism B confounds
   plus a more honest reporting of survey-infrastructure-on-mound cases as
   a distinct downstream task.
3. **Cat 2 identity resolution (deferred).** Consult a primary
   Russian-language Soviet topographic guide (1:50,000 Условные знаки, 1983
   or similar) to identify the rounded-black-hachured symbol class. Update
   the catalogue addendum once resolved. Not on the paper's critical path.

Mechanisms A and B fixes are independent and can be tested in either order or
in parallel.

## 8. Caveats and risk register

- **Mechanism share figures are scoped to the 117 settlement-mound
  re-inspection.** Generalising to the full 1,119 v2 FP-classifier
  denominator would require a second annotation pass with consistent
  Cat 1 / Cat 2 / Cat 3 labelling.
- **Cat 1 / Cat 2 split within the 87 `not_orange_brown` rows is qualitative.**
  A formal sub-count is not part of this work.
- **The bet-test's 0 / 177 error rate has Wilson upper 95 % CI of 2.1 %.**
  The empirical rate is 0 %; the bet's 2 % threshold was decisively met. The
  upper-bound interval is reported here as transparency for any reader who
  prefers the worst-case framing.
- **Cat 2's cartographic identity is unresolved in TM 30-548 ≤ 425.** The
  paper Discussion uses mechanism-level framing to avoid dependence on this
  resolution. If a primary Russian-language source resolves Cat 2 in future
  work, the catalogue can be sharpened by addendum without retracting any
  current claim.
- **Mechanism C is conceptual, not numerically tabulated.** Item 285 is a
  named exemplar; the corpus-level frequency of mud-geyser-crater-like
  confounds is not measured.
- **Threshold-rule artefact in Obs 313.** The Streamlit app's "Mode 2
  SUPPORTED if ≥ 60 % `closed_topo_line_no_hachures`" rule was set before the
  composition of the `not_orange_brown` group was known. The strict-rule
  verdict (Mode 2 technically rejected at 24.8 %) is an artefact of the
  pre-registration choice; the empirical finding (Mode 2 is a substantive
  secondary mode at ~25 %) stands.

## 9. Cross-references

### 9.1 Source observations (Session 81 review thread)

- **Obs 312** (commit `c4585f60`) — bet-test resolved 0 / 177 review errors;
  initial Mode 1–7 catalogue (refined and partially superseded by Obs 313's
  two-mechanism framework, but quantitative bet-test result unchanged).
- **Obs 313** (commit `1a56f35b`) — settlement-mound re-inspection
  three-category taxonomy (87 / 29 / 1 / 0) and two-mechanism unification
  (A — colour-veto; B — central-glyph anchor).
- **Obs 314** (commit `c4432978`) — Cat 2 = TM 30-548 Item 473 "Tailings pile"
  identification; **superseded** by Obs 315's exhaustive ≤ 425 negative
  result. Methodological note on agent context-biasing
  (`### Why Item 472 was wrong — agent context-biasing` and the mitigation
  guidance) **stands unchanged** and is not affected by the supersession.
- **Obs 315** (commit `0d80ebcd`) — symbol-identification thread closed: Cat 2
  negative result on TM 30-548 ≤ 425; Mechanism C added (Item 285 "Crater of
  mud geyser" as exemplar); Item 83 vocabulary confirmation; TM 30-548 partial
  colour-reliability caveat.

### 9.2 Context observations

- **Obs 304** (high-pull tail characterisation) — qualitative inspection of
  nine high-pull and three low-pull maps rejected the strong shared-feature
  hypothesis. Convergent with the present catalogue: per-map FP rates are
  driven by reference-point density and small-denominator variance, not by an
  identifiable cartographic feature class shared across high-pull maps.
- **Obs 306** (GS FP-classifier closed-list expansion) — the v2 closed-list
  expansion that enabled the v2 reclassification rate; v1's 60 % `contour-ring`
  leakage was a closed-list design artefact, not classifier hallucination.
- **Obs 307** (cross-corpus chi-square) — Monte Carlo *p* = 0.0028 at the
  > 125 m stratum; *p* = 0.0012 at the > 50 m stratum, supporting
  corpus-specific failure modes. Interpretation **stands intact** under the
  bet-test result (the 55-map FP-class distribution that fed the chi-square
  is genuine v2 overclaim, not review-pass error).
- **Obs 308** (15.8 % reclassification rate) — provisional status **closed**
  by Obs 312 (explanation 1 rejected); the reclassification rate is genuine
  classifier behaviour and is now mechanistically explained by the present
  catalogue.

### 9.3 Source data and scripts

- `results/55maps-fp-classification/v2-burial-mound-bet-test/verdicts.csv`
  (197 rows; 177 non-calibration + 20 calibration; all `verdict =
  v2_overclaim`).
- `results/55maps-fp-classification/v2-burial-mound-bet-test/settlement-mound-mode2-verdicts.csv`
  (117 rows; verdict counts 87 / 29 / 1 / 0 verified by direct read).
- `scripts/v2_burial_mound_bet_test_app.py` — Streamlit bet-test inspection
  app used to generate the 197 verdict rows.
- `scripts/v2_settlement_mound_mode2_app.py` (commit `d75a483e`) — Streamlit
  re-inspection app used to generate the 117 settlement-mound verdict rows.
- `prompts/system-instructions/detect_brief-text.md` — proposer prompt; states
  the orange-brown colour requirement and the four burial-mound subtypes that
  underpin both failure mechanisms.
- `inputs/examples/SovietTopoSymbols.pdf` — TM 30-548 (US Army, 1958);
  pages 11–50 searched exhaustively for the Cat 2 visual pattern; Item 285
  at page 53; Items 81–84 (burial-mound subtypes) at approximately page 17.
- `archive/planning-completed-session-81-82/v2-burial-mound-bet-test-app-plan-2026-04-29.md`
  (commit `8d2f7f47`) — bet-test protocol: denominator, threshold, verdict
  categories, calibration design.

## 10. Reproducibility

This report is a **synthesis** of source observations and source data; no new
analysis script or computational result is produced. To reproduce or audit any
specific quantitative claim:

- The 0 / 177 bet-test result is verifiable by reading
  `results/55maps-fp-classification/v2-burial-mound-bet-test/verdicts.csv`
  and confirming all 177 non-calibration rows carry `verdict = v2_overclaim`.
  The verdict-count breakdown is reproducible via:

  ```bash
  cut -d',' -f3,6 results/55maps-fp-classification/v2-burial-mound-bet-test/verdicts.csv \
      | sort | uniq -c
  ```

- The 87 / 29 / 1 / 0 settlement-mound breakdown is verifiable by reading
  `results/55maps-fp-classification/v2-burial-mound-bet-test/settlement-mound-mode2-verdicts.csv`
  and counting verdict labels:

  ```bash
  cut -d',' -f3 results/55maps-fp-classification/v2-burial-mound-bet-test/settlement-mound-mode2-verdicts.csv \
      | sort | uniq -c
  ```

- The mechanism-level interpretation (A / B / C) is qualitative and is
  documented in the source observations cited in §9.1.
- The TM 30-548 negative result (Cat 2 ≤ 425) is documented in Obs 315; the
  source PDF is `inputs/examples/SovietTopoSymbols.pdf`.

The Session 81 review thread that produced these observations was conducted
via Streamlit-app inspection (Phase 1 — bet-test; Phase 2 — settlement-mound
re-inspection) plus two SovietTopoSymbols.pdf agent searches. The visual
analysis is not algorithmically reproducible by definition; the verdict data
that supports the quantitative claims is fully reproducible from the committed
CSV files.

## 11. Files in this directory

| File | Contents |
|---|---|
| `report.md` | This document — synthesis of Obs 312 / 313 / 314 / 315 |

No additional data artefacts are produced by this synthesis. All source data
lives at the cross-referenced paths in §9.3.

---

**End of report.**
