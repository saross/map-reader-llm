# AB+ — Semantic Segmentation Deep Learning for Extracting Surface Mine Extents from Historic Topographic Maps

| field | value |
|---|---|
| **citekey** | `maxwell_semantic_2020` |
| **full cite** | Maxwell, Aaron et al. (2020) *Semantic Segmentation Deep Learning for Extracting Surface Mine Extents from Historic Topographic Maps.* Remote Sensing. DOI: 10.3390/rs12244145 |
| **register** | Borrowed (remote sensing / GIScience — Remote Sensing, MDPI) |
| **primary gap** | Historical-map extraction lineage — the area-segmentation rung |
| **also touches** | Difficulty ladder (area segmentation → point symbols); Calibration transfer / carried vs oracle operating points; Annotation budgets; Ground-truth epistemics; Metric hygiene (chip-level vs map-level protocol; accuracy under class imbalance) |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Maxwell and colleagues train a modified UNet to segment surface-mine disturbance from scanned, georeferenced United States Geological Survey (USGS) 1:24,000 topographic maps — 170 sheets across Kentucky, Ohio, and Virginia — supervised by manually digitised polygons from the USGS Geology, Geophysics, and Geochemistry Science Center (GGGSC) database. The abstract carries the map-level arm: Dice 0.902 on held-out Kentucky sheets (precision 0.891, recall 0.917), 0.837 in Ohio, 0.763 in Virginia. A second arm cuts training from 84 maps to 15 and reports only slight loss.

This is the historical-map extraction lineage's canonical area-segmentation result, and it is as useful for what it excludes as for what it achieves. The source database holds both point and polygon features; the authors take the polygons. The 0.902 is therefore our difficulty ladder's easy rung — area segmentation, and correspondingly the top of the performance range — with the point-symbol rung on those same sheets excluded at data selection.

The transfer degradation is asymmetric: map-level recall falls 0.917 to 0.811 to 0.686 as the model leaves Kentucky while map-level precision never drops below 0.890, and at chip level precision rises (0.954, 0.966, 0.971). That is consistent with a carried operating point — an in-domain decision rule travelling as a recall tax rather than a precision tax — but the paper reports no alternative operating point (the word "threshold" does not occur in it), so it cannot separate a stale decision rule from genuine loss of recognition on unfamiliar symbology — the authors' own hedged reading: "could potentially be attributed to differences in the representation or presentation of mine features in the new data" (§3.1).

The annotation-budget claim needs qualification. The subsets were not drawn uniformly — selection was random but probability-weighted by each map's mining land area — so low-budget models saw positive-rich sheets. The comparison is chip-level, although the paper calls whole-map assessment the more robust one, and the twenty subset models were never validated at map scale. The shortfall widens with distance (0.009, 0.019, 0.024), and below fifteen maps the curve falls away fast: at two maps, mean Kentucky-testing Dice never exceeded 0.800. The authors also disclaim exactly the transfer we want from them — their "findings associated with sample size and model generalization may not translate to other algorithms and/or classification problems" (§4).

Two hygiene notes. The paper runs two protocols in parallel, and 0.837 names both Virginia's chip-level Dice and Ohio's map-level Dice; no figure should be lifted from here without its protocol. Overall accuracy is uninformative throughout (0.942 to 0.999) because background pixels dominate — the authors say so and adopt Dice loss for that reason, the same imbalance argument that motivates reporting MCC beside F1 in our work, though this paper never mentions MCC and its remedy stops at Dice/F1. The ground truth also needed hand repair — the scan identifier could not be trusted to link features to sheets, so all 170 maps were inspected — though the pass was forced by linkage failure, not digitising error.

## Positioning annotation (interpretive)

The area-segmentation baseline of the historical-map extraction lineage: a well-resourced CNN result on the same class of scanned national-survey sheets we work on, but on pattern-filled polygons that the authors explicitly separate from the point symbols carried on those same maps. Cite it for three things — the easy rung of our difficulty ladder, area segmentation, and correspondingly the top of the performance range (Dice 0.902 in-domain); a clean measurement of the transfer tax with its characteristic shape (precision holds, recall collapses at a fixed 0.5 rule — a shape consistent with, but not evidence for, a carried operating point, since no oracle threshold is reported); and the annotation-budget claim that 15 maps nearly match 84, which should never travel without at least its protocol qualifier, since that comparison is chip-level rather than the whole-map protocol the authors themselves call more robust. It is a supportive comparator whose numbers must never be quoted without their evaluation protocol attached, since the paper reports chip-level and map-level Dice side by side and 0.837 denotes a different quantity in each.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "This database contains manually digitized point and polygon features interpreted from mine symbols on historic topographic maps available in the HTMC. Examples of the historic topographic maps and mining features data are shown in Figure 4. We only used polygon features digitized from 1:24,000-scale maps in this study."
- **Locator:** page_index 6 · p.7 · §2.1 Study Areas and Input Data
- **Paraphrase:** The USGS source database holds both point and polygon features digitised from mine symbols, and this study takes only the polygons from 1:24,000-scale sheets: point symbols were excluded at the data-selection step, not merely left unaddressed. (§1.1 states the scope in the authors' own words — "Such areal, thematic features are the focus of this study" — while noting that the retained class is not purely generic pattern fill, since symbols for specific features such as tailings are kept.)
- **Relevance:** §2 related work; §5 discussion — why point symbols are the harder rung · Difficulty ladder — the rung this lineage actually measures · **supports**

### KP2
- **Quote (verbatim):** "When the model is applied to new topographic maps in Ohio and Virginia to assess generalization, model performance decreases; however, performance is still strong (Ohio Dice coefficient = 0.837 and Virginia Dice coefficient = 0.763)."
- **Locator:** page_index 0 · p.1 · Abstract
- **Paraphrase:** Applied to sheets in two states outside the training region, whole-map Dice falls from 0.902 in Kentucky to 0.837 in Ohio and 0.763 in Virginia; the authors read this as a real but tolerable generalisation cost. (These are the map-level figures of Table 5; the chip-level figures for the same transfers are higher — 0.894 and 0.837 in Table 4.)
- **Relevance:** §2 related work; §5 discussion — transfer taxes · Calibration transfer — the size of the transfer tax in a comparable task · **supports**

### KP3
- **Quote (verbatim):** "errors when generalizing to new data and geographic extents were dominated by omission error, as measured with recall, and precision remained above 0.890 for all datasets, even when the number of training topographic maps in the datasets were reduced to 15"
- **Locator:** page_index 17 · p.18 · §4 Discussion
- **Paraphrase:** Under transfer the error budget shifts one way only: recall falls while precision stays above 0.890 on every dataset, including the models trained on just fifteen maps, so generalising to new regions costs omissions rather than false positives.
- **Relevance:** §5 discussion — what a carried threshold costs, and on which side · Calibration transfer — carried vs oracle operating points · **extends**

### KP4
- **Quote (verbatim):** "the average Dice coefficients for the 15 topographic map models were 0.940, 0.875, and 0.813 for the KY, OH, and VA validation sets, respectively. For comparison, the model using all the training samples yielded Dice coefficients of 0.949, 0.894, 0.837 for the same validation sets."
- **Locator:** page_index 16 · p.17 · §3.3 Sample Size Comparisons
- **Paraphrase:** Cutting the training set from all available maps to fifteen costs 0.009 Dice in Kentucky, 0.019 in Ohio, and 0.024 in Virginia: the annotation saving is nearly free in-domain and progressively less so as the target region moves further away. (These are chip-level figures; the sample-size arm is not repeated at the whole-map level the paper elsewhere calls more robust.) Fifteen maps is the top of a curve that falls away quickly below it: with only two training maps, mean KY-Testing Dice across all five replicates and all epochs never rose above 0.800, and between-subset variability shrank only as the map count grew.
- **Relevance:** §5 cost/accuracy trade-space; §5 discussion — low-budget calibration under transfer · Annotation budgets — the budget-by-transfer interaction · **complicates**

### KP5
- **Quote (verbatim):** "the probability of selection was weighted by the relative land area of mining in each topographic map"
- **Locator:** page_index 10 · p.11 · §2.4 Sample Size Comparisons
- **Paraphrase:** The reduced-size training subsets were not sampled uniformly from the available maps — each map's chance of selection was weighted by how much mining it contained — so the small-budget models were trained on positive-rich sheets rather than a uniform random draw — the selection was random, but probability-weighted by mining land area.
- **Relevance:** §3 methods — gold-standard construction; §5 discussion — oracle assumptions in budget claims · Annotation budgets — what a low-budget result presupposes about sheet selection · **complicates**

### KP6
- **Quote (verbatim):** "all features that intersected the extent of the quadrangle were extracted and then manually inspected for all 170 maps. Features that were not present on the map were removed, and any missing features were added"
- **Locator:** page_index 6 · p.7 · §2.1 Study Areas and Input Data
- **Paraphrase:** Because the scan identifier could not be trusted to link digitised features to the correct sheet, the authors pulled every feature intersecting each quadrangle and inspected all 170 maps by hand, deleting features that were not on the map and adding ones that had been missed. The authors add that missing features were a rare occurrence because the database was very comprehensive; the hand pass was forced by unreliable SCANID linkage rather than by digitising error.
- **Relevance:** §3 methods — gold-standard construction; §5 discussion · Ground-truth epistemics — an authoritative database still needed hand repair · **complicates**

### KP7
- **Quote (verbatim):** "Visual inspection of these poorly classified maps suggest that they were obtained for maps with a small percentage or land area of surface mining where small proportions of omission or commission error had large weight and thus greatly impacted the reported metrics."
- **Locator:** page_index 14 · p.15 · §3.2 Topographic Map-Based Assessment
- **Paraphrase:** The worst-scoring sheets were those with very little mining on them: where the positive class is small, a handful of omissions or false positives moves the reported metric a long way, which is why per-map scores are volatile at the sparse end.
- **Relevance:** §4 results — per-tile metrics; §5 discussion — reporting MCC alongside F1 · Metric hygiene — sparse-positive volatility, and why accuracy alone misleads · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "automating the extraction of such features is complicated by inconsistencies between maps, differences in mine disturbance symbology, and overprinting with contour lines, text and labels, and other features"
- **Locator:** page_index 1 · p.2
- **Why:** Written about pattern-filled area symbols, the sentence names precisely the conditions our point-symbol task meets on Soviet-era sheets: symbology that drifts between sheets, and overprinting by contour lines, text, and neighbouring features. A crisp epigraph for the step from area segmentation to point symbols — the clutter that merely complicates a polygon boundary is the entire problem for a symbol a few pixels across.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
