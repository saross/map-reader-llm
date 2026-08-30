# AB+ — Cartographic reconstruction of building footprints from historical maps: A study on the Swiss Siegfried map

| field | value |
|---|---|
| **citekey** | `heitzler_cartographic_2020` |
| **full cite** | Heitzler, Magnus & Hurni, Lorenz (2020) *Cartographic reconstruction of building footprints from historical maps: A study on the Swiss Siegfried map.* Transactions in GIS. DOI: 10.1111/tgis.12610 |
| **register** | Borrowed (cartography / GIScience — Transactions in GIS) |
| **primary gap** | Historical-map extraction lineage — the segmentation-to-vectorisation rung |
| **also touches** | Annotation budgets and human-in-the-loop correction economics; Ground-truth epistemics — the single-operator reference polygon; Metric hygiene (accuracy under class imbalance; IoU size bias); Consensus aggregation over independent passes; Calibration transfer / carried vs oracle operating points; Difficulty ladder (area segmentation → point symbols); Symbol-family confusion as the dominant error mode |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Heitzler and Hurni document the production workflow behind the vectorised building layer of the Swiss Siegfried map (3,903 sheets of 7,000 × 4,800 pixels published 1872–1949; 3,098 at 1:25,000, 805 at 1:50,000). An ensemble of ten U-Net-derived fully convolutional networks segments building pixels from 200 × 200-pixel tiles with a 60-pixel context margin; a hand-built vectoriser then idealises those pixels into polygons (Canny contours, corner detection after Wall and Danielsson (1984), DBSCAN clustering of wall orientations, two artefact clean-up passes). Training used 26 manually digitised sheets accumulated across bootstrap iterations; the product is roughly six million footprints.

Four features make this the most useful comparator in the historical-map extraction lineage for our cost and calibration claims, area-feature target notwithstanding.

First, correction economics are measured, not asserted. Across ten held-out sheets, 90.77% of 15,658 predicted buildings needed no manual edit; correcting all ten took 414 minutes (about 41 per sheet, some 38 buildings per minute) against roughly 10 per minute from scratch — a fourfold human-in-the-loop speed-up. These are, they caution, “a matter of subjectivity”: operators differ in speed and in what counts as a flaw, and the from-scratch baseline used a 100-building sample per sheet. Projected to the full series at a conservative 45 minutes — rounded up from the measured 41.4 — that is 2,900 hours or 363 eight-hour working days, an upper bound stated on the express condition that no further improvement iterations are run: the aggregate arithmetic our annotation-budget section needs.

Second, transfer heterogeneity is visible per sheet. Table 4's per-sheet IoU measures how much the human corrector changed the pipeline's own polygons, not accuracy against an independent reference; it runs from 99.40 on sheet 6 (high print quality, simple geometries) to 52.83 on sheet 10 (mountainous, hachure-dense, one of the two sample sheets at 1:50,000), where correction stripped more than 44% of predicted area and 46% of vertices. That spread belongs to the whole pipeline, not the ensemble alone, and the 92.33% aggregate hides a near two-fold range driven by print quality, terrain, and scale — our carried-versus-oracle operating point in another guise.

Third, the dominant failure is symbol-family confusion, not noise: only 2.4% of pixels called building were wrong, but hachures alone contribute 1.6%, with labels, border symbols, height marks, roads, and railways supplying the rest. On a Soviet sheet where mounds are one symbol family among dozens, that is the expected shape of the error budget.

Fourth, the authors are candid about metrics and ground truth: accuracy is uninformative at roughly 1% positive pixels (models 9 and 10 scored 98.990% predicting no buildings), IoU is positively biased towards large features because seam width is scale-independent, and the reference is one operator's polygon among infinitely many defensible ones. They add, hedged, at the end of the §2.2 metrics discussion (p.447) — not in the conclusions — that “it might very well be worth exploring how these measures can be adapted” to historical-map segmentation and vectorisation, an opening our metric-hygiene framing can take up.

## Positioning annotation (interpretive)

The canonical cartographic-vectorisation rung of the historical-map extraction lineage: a pre-LLM, closed-vocabulary convolutional pipeline that industrialised one symbol family across one national series and then measured what the human correction pass actually costs. It supports three of the citing paper's structural commitments — aggregation over independently initialised models as the standard remedy (ten separately trained networks averaged once at inference, rather than repeated stochastic passes of one model), symbol-family confusion as the dominant error mode, and the single-operator reference polygon as an epistemically soft ground truth. It complicates any direct comparison of headline numbers, because its 88.2% IoU is building-class pixels on a held-out tile split while its 92.33% IoU is a polygon-area delta against a human-corrected version of the model's own output rather than an independent reference.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "pixels that might very well be part of another valid polygon might erroneously be classified as a false positive or false negative when checked against the one given polygon"
- **Locator:** page_index 5 · p.6 · §2.2 Performance assessment (cont., p.447)
- **Paraphrase:** Because the reference is a single polygon drawn by one GIS operator, a prediction that traces an equally defensible alternative outline is scored as error. The authors state that infinitely many polygons can legitimately represent the same map feature, so the measured false positives and false negatives partly index annotator choice rather than detection failure. They bound the effect themselves: “These issues mainly occur at the border pixels (the seam) of features”, and they judge a building sufficiently well detected when that seam is only a few pixels wide (up to about 3), with buildings above 80% IoU generally well represented — so annotator choice inflates the seam rather than swamping the error budget.
- **Relevance:** § ground-truth construction; § limitations of the gold standard · Ground-truth epistemics — the single-operator reference polygon · **complicates**

### KP2
- **Quote (verbatim):** "Accuracy has limited expressiveness as it is more sensitive to imbalanced data (only about 1% of the pixels belong to a building), and also shows high values if all pixels are classified as non-building."
- **Locator:** page_index 4 · p.5 · §2.2 Performance assessment
- **Paraphrase:** With roughly one per cent of pixels positive, accuracy is inflated by the negative class and a degenerate all-negative predictor scores highly. The authors therefore treat accuracy as uninformative and report class-sensitive measures instead — the same reasoning that makes MCC rather than accuracy the right companion to F1 in our reporting.
- **Relevance:** § metrics; § why MCC accompanies F1 · Metric hygiene (accuracy under class imbalance) · **supports**

### KP3
- **Quote (verbatim):** "It is striking that the combined predictions performed best in every case except for recall, which is the reason that this ensemble approach was used to make the final predictions of the Siegfried map sheets."
- **Locator:** page_index 4 · p.5 · §2.2 Performance assessment
- **Paraphrase:** Averaging ten independently initialised models beat every individual model on all reported measures except recall, and that result is what motivated shipping the ensemble rather than a single network. Aggregating independent passes trades a little recall for gains elsewhere — structurally the same bargain our consensus-over-passes stage strikes.
- **Relevance:** § architecture — consensus over passes; § prior art for aggregation · Consensus aggregation over independent passes · **supports**

### KP4
- **Quote (verbatim):** "it also becomes apparent that IoU is positively biased toward larger features. As the width of the seam is independent of the feature area, smaller IoUs are calculated for smaller features"
- **Locator:** page_index 5 · p.6 · §2.2 Performance assessment (cont., p.447)
- **Paraphrase:** Disagreement concentrates in a boundary seam whose width does not scale with the object, so overlap-based scores fall as target size falls even when the detection is qualitatively correct. Small targets are therefore penalised by the metric itself, which motivates point-matching rather than overlap criteria at the point-symbol rung of the difficulty ladder — an extension we draw, since the source demonstrates the seam effect only on area features (its illustrative low-IoU cases are buildings at 75.56 and 80.21%) and proposes no alternative measure of its own.
- **Relevance:** § difficulty ladder; § matching criterion and metric choice · Difficulty ladder (area segmentation → point symbols); metric hygiene · **supports**

### KP5
- **Quote (verbatim):** "sheet 10, whose bad predictions were already discussed before, lost more than 44% in area and 46% of the generated vertices due to correction"
- **Locator:** page_index 13 · p.14 · §4 Results
- **Paraphrase:** One of the ten held-out sheets — mountainous, hachure-dense, and one of the two sample sheets at the coarser 1:50,000 scale, a difference the authors invoke on this same page — lost nearly half its predicted area and vertices at the correction stage, with a Table 4 IoU of 52.83 against 99.40 on the best sheet: figures that quantify the size of the human correction applied to the pipeline's own output, not accuracy against independent ground truth. A single frozen configuration therefore demands wildly unequal amounts of human repair across the deployment corpus — a property of the whole pipeline, segmentation ensemble plus vectoriser plus clean-up passes, rather than of the ensemble alone — which is what a transfer tax looks like when it is disaggregated by sheet.
- **Relevance:** § transfer taxes; § deployment heterogeneity · Calibration transfer / carried vs oracle operating points · **complicates**

### KP6
- **Quote (verbatim):** "of all pixels classified as buildings, only 2.4% have been falsely classified, with hachures making up the majority of 1.6%"
- **Locator:** page_index 7 · p.8 · §2 Segmentation — false-positive analysis (cont., p.449)
- **Paraphrase:** False positives are both rare and highly concentrated: two-thirds of them come from one competing cartographic sign, relief hachures, with labels, border symbols, height marks, roads, and railways accounting for the rest. Error on a topographic sheet is structured by the symbol vocabulary, not spread uniformly, which is the premise our adversarial verifier is built on. The concentration is spatial as well as symbolic: 117,344 of the 125,770 hachure false positives (93%) come from sheet 10 alone, where roughly 45% of all pixels called building were in fact something else — so the 2.4% aggregate averages one very bad sheet against nine good ones.
- **Relevance:** § error analysis; § adversarial verifier rationale · Symbol-family confusion as the dominant error mode · **supports**

### KP7
- **Quote (verbatim):** "it would take approximately 2,900 hr or 363 8-hr working days to manually correct all sheets, assuming a conservative correction time per sheet of 45 min"
- **Locator:** page_index 14 · p.15 · §5 Discussion
- **Paraphrase:** The authors carry a deliberately conservative 45 min/sheet — rounded up from the measured 41.4 min (414 min over 10 sheets), which the paper reports as “41 min/sheet” — to the full 3,903-sheet series, giving roughly 2,900 hours or 363 eight-hour days under the explicit antecedent “If no more iterations of this process were to be conducted”: a ceiling on the no-further-improvement scenario that they expect continued model improvement to lower, not a settled projection of what finishing the series will cost. Stating the corpus-scale total rather than the per-unit figure is what turns a plausible-sounding review cost into a budget decision.
- **Relevance:** § annotation budgets; § cost/accuracy trade-space · Annotation budgets and human-in-the-loop correction economics · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "these approaches are hardly able to distinguish between feature types of similar color (e.g., black buildings and labels) and show limited success in cases of color deterioration due to aging"
- **Locator:** page_index 1 · p.2
- **Why:** A one-line statement of why the pre-deep-learning colour-segmentation lineage stalled on scanned topographic sheets: same-coloured symbol families are not separable by colour, and print ageing degrades what separability there was. It frames the historical-map extraction paragraph exactly where our own problem sits — a black point symbol among dozens of other black marks on a deteriorated sheet.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
