# AB+ — Identifying wetland areas in historical maps using deep convolutional neural networks

| field | value |
|---|---|
| **citekey** | `stahl_identifying_2022` |
| **full cite** | Ståhl, Niclas & Weimann, Lisa (2022) *Identifying wetland areas in historical maps using deep convolutional neural networks.* Ecological Informatics. DOI: 10.1016/j.ecoinf.2022.101557 |
| **register** | Borrowed (ecological informatics / land-cover remote sensing) |
| **primary gap** | Metric provenance — what the 88.6 % benchmark actually measures |
| **also touches** | Cross-study comparability of reported F1; Area-segmentation vs point-symbol difficulty ladder; Annotation budgets for supervised map extraction; Calibration and operating-point transfer; Ground-truth epistemics on historical maps |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Ståhl and Weimann train a fully convolutional network — seven convolutional layers, no pooling — to segment wetland areas from Generalstabskartan, the roughly century-old Swedish national topographic series, supervised by wetland polygons Jönköping county had already hand-digitised. The county map is cut into 80 × 80-pixel tiles and assessed by a ten-fold spatial cross-validation; the same model is then run across the whole southern collection to publish an open GIS layer.

O'Hara et al. benchmark against this paper, so its numbers need attesting at source. The Results give an F1 measured over all folds of 0.886, precision 0.871, recall 0.901; O'Hara's transcription (88.6 %, 87.1 %, 90.1 %) is faithful. Two cautions. First, the Conclusions of this same paper give the ten-fold result as 0.87 — an unexplained disagreement, but a settleable one: the harmonic mean of the reported precision and recall is 0.8857, making 0.886 internally consistent and 0.87 the outlier. Second, the paper never names the unit of analysis for its F1, nor which class is positive. The network estimates per-pixel wetland probability, the prediction is thresholded per pixel, and Figure 4 maps false-positive and false-negative areas from a pixelwise comparison, so per-pixel is the strong inference; and because wetland is the minority class — the paper gives 1.805 × 10⁹ m² of wetland in Jönköping but no total area, so the base rate comes from outside it — a precision of 0.871 fits only the wetland class. The inference matters: 0.886 is a target-class score, O'Hara's 98.2 % headline a majority-class one. Matched on class the figures are 0.908 against 0.886, yet incommensurable in denominator: O'Hara's from 567 manually assessed validation areas scored wetland at ≥ 50 % areal coverage, Ståhl's from an inferred pixelwise comparison. No confusion matrix or class base rates are reported, so no class-symmetric statistic (Kappa, Matthews correlation coefficient) can be recomputed.

Three further contrasts bear on our design. On difficulty the authors offer a hedged aside, not a measurement: wetlands 'may be' on the easier end 'of nature types' to detect, given their simple texture — a remark made while explaining why no sensitivity study was run. It is also area segmentation, where the authors attribute residual error to small disagreements over where outlines should be drawn — a claim resting only on the 0.3 % macroscopic area agreement, and qualified by their warning about confusing wetland texture with hill texture. Either way the failure mode has no analogue in point-symbol detection. The annotation budget was 173,718 pre-existing wetland polygons from one region, and the authors concede in the very next sentence that no sensitivity study established how much was needed. The operating point is fixed by fiat — a 0.5 rounding step never treated as a decision boundary, plus a 1000 m² minimum-area filter the paper calls post-processing done 'primarily' for the southern-Sweden product — then carried into a deployment covering half of Sweden with no evaluation there: an uncosted calibration transfer of the kind we set out to price.

## Positioning annotation (interpretive)

Historical-map extraction lineage. This is the convolutional baseline that the closest comparator in our related work measures itself against, and therefore the load-bearing other half of that comparison: Ståhl and Weimann's 0.886 is, by inference from the model description rather than by the paper's own statement, a target-class (wetland) F1 from a ten-fold spatial cross-validation over one Swedish county, whereas O'Hara et al.'s 98.2 % is a majority-class figure, so on the same class the gap is roughly two points rather than ten — though the scores remain incommensurable in their denominator: O'Hara's derives from a confusion matrix over 567 manually assessed validation areas under a ≥ 50 % areal rule, Ståhl's from an inferred pixelwise comparison. The right formula is class-matched but protocol-incommensurable. O'Hara are themselves alive to the hazard, declining pixel-level comparison between their historic mask and the modern national land-cover map because it 'would suggest a comparable level of accuracy between the two maps which is not the case' — a caution about mismatched denominators they do not extend to their own benchmarking against this paper. Cite Ståhl as the pixel-level area-segmentation benchmark for wetland extraction, and cite its internal discrepancy — 0.886 in the abstract and Results, 0.87 in the Conclusions — as evidence that headline numbers in this literature must be reconciled across a paper's own sections rather than lifted from whichever one is read first; the citing paper here transcribed the Results figure faithfully.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "The presented method acquired a F1-score, measured over all folds, of 0.886 where the precision of the model is 0.871 and the recall is 0.901."
- **Locator:** page_index 3 · p.4 · §3 Results
- **Paraphrase:** The Results section gives a single headline F1 of 0.886 pooled over all ten cross-validation folds, with precision 0.871 and recall 0.901. These are exactly the three figures O'Hara et al. transcribe as 88.6 %, 87.1 % and 90.1 %, so their citation of this paper is accurate. The sentence does not state the unit of analysis or which class is positive; per-pixel evaluation on the wetland class is an inference from the model description, and the supporting step — that a majority-class precision could not be as low as 0.871 — rests on a base rate the paper never supplies and that must be imported from outside it.
- **Relevance:** §2 related work · Metric provenance — what the 88.6 % benchmark actually measures · **complicates**

### KP2
- **Quote (verbatim):** "The presented model achieves a F1 score of 0.87 when a 10 fold cross validation is performed on the data."
- **Locator:** page_index 4 · p.5 · §5 Conclusions
- **Paraphrase:** The Conclusions report the same ten-fold cross-validated result as an F1 of 0.87, which does not match the 0.886 stated in the abstract and in the Results. The paper offers no reconciliation, but the discrepancy is nonetheless settleable from the paper's own numbers: the harmonic mean of the reported precision and recall, 2(0.871)(0.901)/(0.871 + 0.901), is 0.8857, so 0.886 is the internally consistent figure and 0.87 is the outlier. A citing author who reads only the Conclusions will reproduce the wrong one.
- **Relevance:** §2 related work · Cross-study comparability of reported F1 · **complicates**

### KP3
- **Quote (verbatim):** "the agreement on a macroscopic level, where the agreement between the human annotator and the CNN is almost in unison. In this case, the total area estimated by the CNN differed less than 0.3% compared to the area that was marked by human annotators."
- **Locator:** page_index 4 · p.5 · §5 Conclusions
- **Paraphrase:** The authors defend the model by appealing to agreement at the macroscopic scale: the total wetland area the network estimates differs from the human-annotated total by less than 0.3 per cent — an overestimate, per the direction given in the Results. Aggregate area agreement is a far more forgiving statistic than the per-pixel F1 — over- and under-shoots at opposite boundaries cancel in a sum — and it has no analogue in instance-level symbol detection, where a detection either matches a ground-truth instance or does not.
- **Relevance:** §5 results — metric reporting · Ground-truth epistemics on historical maps · **complicates**

### KP4
- **Quote (verbatim):** "Wetlands may be on the easier end of nature types to detect, due to the simple texture, but, there is a risk to confuse the texture with the texture representing hills."
- **Locator:** page_index 3 · p.4 · §4 Discussion
- **Paraphrase:** The authors offer a hedged aside: wetlands 'may be' on the easier end 'of nature types' to detect — that is, among land-cover classes, not among map-extraction tasks in general — attributing that to the simplicity of the wetland texture, and immediately noting the one confusion they expect, the hill texture. The remark sits inside a paragraph explaining why no sensitivity study was run, so it is authorial intuition rather than a measurement. Even so, it is a prior-art author volunteering that their class is among the easier ones, which is the rung above the one our task occupies.
- **Relevance:** §2 related work · Area-segmentation vs point-symbol difficulty ladder · **supports**

### KP5
- **Quote (verbatim):** "the pixel predictions from the CNN are rounded, so all predictions with predicted value larger than 0.5 are considered as wetlands and all predictions below are non-wetlands"
- **Locator:** page_index 2 · p.3 · §2.5 Data post-processing
- **Paraphrase:** The probability surface is binarised at 0.5. The authors present this as a rounding step inside a post-processing chain and never treat it as a decision boundary open to calibration — reading it as an operating point is our frame, not theirs. No sweep, tuning, sensitivity analysis, or justification of the cut point appears anywhere: the word 'threshold' occurs nowhere in the paper.
- **Relevance:** §5 results — operating points · Calibration and operating-point transfer · **supports**

### KP6
- **Quote (verbatim):** "Besides this experiment, the model is also applied to historical maps covering the whole southern part of Sweden, with the aim of generating an overview of historical wetland areas."
- **Locator:** page_index 1 · p.2 · §1 Introduction
- **Paraphrase:** The model validated by cross-validation within a single county is then run over map sheets covering the entire southern half of Sweden, and the resulting layer is published as a research resource. No accuracy assessment is reported for that far larger deployment area. The paper does offer a qualitative check — the densest predicted wetlands fall where wetlands are known to be dense today, and the historical estimate of 1.96 × 10¹⁰ m² is set beside modern coverage of 7.82 × 10⁹ m² — but no validation data outside the county. The county-level score and the fixed 0.5 threshold are simply carried across.
- **Relevance:** §5 discussion — transfer · Calibration and operating-point transfer · **supports**

### KP7
- **Quote (verbatim):** "data from a single region, covering 173,718 separate wetlands, where the smallest wetland is 3527m2, is sufficient to get a model with acceptable performance"
- **Locator:** page_index 3 · p.4 · §4 Discussion
- **Paraphrase:** The supervised model was viable because 173,718 hand-delineated wetlands already existed for one county, with the smallest at 3527 m². The authors present this as the quantity that sufficed, while conceding in the very next sentence that no formal sensitivity study established how much less would have done — so it is an upper bound on the budget, not a measured requirement. They add that these wetlands were 'only selected due to their availability'.
- **Relevance:** §2 related work · Annotation budgets for supervised map extraction · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "The lack of pre-labelled material of high quality, which can be used in the training of supervised models, is a major bottleneck for full scale digitalisation of historical maps."
- **Locator:** page_index 3 · p.4
- **Why:** A clean statement of the constraint our approach is designed around, made by authors who escaped it only because a county agency had already digitised 173,718 wetlands for the region. It is the natural epigraph for the move from supervised segmentation to prompt-time symbol detection: the bottleneck is not model capacity but labelled material, and a method that needs a small gold standard rather than a regional cadastre of labels is answering the bottleneck this paper names.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
