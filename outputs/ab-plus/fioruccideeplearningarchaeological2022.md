# AB+ — Deep Learning for Archaeological Object Detection on LiDAR: New Evaluation Measures and Insights

| field | value |
|---|---|
| **citekey** | `fiorucciDeepLearningArchaeological2022` |
| **full cite** | Fiorucci, Marco et al. (2022) *Deep Learning for Archaeological Object Detection on LiDAR: New Evaluation Measures and Insights.* REMOTE SENSING. DOI: 10.3390/rs14071694 |
| **register** | Archaeological prospection (remote sensing / evaluation methodology) |
| **primary gap** | Metric hygiene and reporting comparability |
| **also touches** | Archaeological prospection prior art — machine-learning mound detection; Difficulty ladder: area segmentation to point symbols; Ground-truth epistemics and gold-standard construction; Annotation budgets and human-in-the-loop; Calibration and operating-point transfer |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Fiorucci and colleagues propose not a new detector but a new way of scoring one. On Actueel Hoogtebestand Nederland 2 (AHN2) LiDAR from the Veluwe they train nine Faster R-CNN variants on prehistoric barrows and Celtic fields. Barrows are burial mounds: our object in another modality. The pair was chosen for its up-to-date inventories and clear LiDAR visibility, but the design then rests on the distinction our difficulty ladder inherits — 'discrete' objects against 'landscape patterns', each given its own measure.

The contribution is two automatic measures, 'centroid-based' and 'pixel-based', replacing a semi-automatic GIS-based measure that needed QGIS in the loop. The centroid rule is what we inherit: a prediction is a true positive if its centroid falls inside a ground-truth box, with exclusive association. That is point-in-box matching, not Intersection over Union (IoU), justified because archaeology needs geographical position relative to the shapes containing objects, barrows being validated by hand coring at a coordinate. Validated empirically: centroid-based tracks GIS-based to within an average discrepancy of less than 1% on barrows, pixel-based less than 3% on Celtic fields.

Three cautions travel with it. First, exclusive association penalises duplicates, but the source's evidence is class-split: it reports the circumstance as sporadic for barrows, with best-match selection offering negligible gain — hence its arbitrary 'first-come, first-selected' rule — while showing the choice move the score materially for Celtic fields, where overlapping ground truths make it produce more false positives (p13). Sharper: the paper's own two measures disagree, the GIS-based one counting multiple detections in a grid cell individually (p3) where the centroid-based one credits just one. The accounting choice is ours, and for a consensus-over-passes pipeline — which manufactures the clustering the source rarely saw on discrete objects — so is the caution.

Second, F1 is reported per class and as an unweighted two-class mean (130 barrows against 997 Celtic field plots), computed separately under each measure; since the pixel-based measure counts pixels of 0.5 m and the GIS-based counts square metres, F1 is not commensurable between them, and the authors offer that scale difference only as a possible cause of pixel-based scoring higher. No absolute F1 appears in the running text — the values live in Figures 9 and 10 — so cite this for metric design, not benchmark comparison. Step (iii) compounds this, listing the counts as 'TP, FP and TN' where F1 requires FN, a slip both published algorithms contradict.

Third, 164 of 825 test subtiles (19.8%) contain any object; the authors call this 'about 1:5 (positive:negative)' defended as real archaeological scarcity, though 164:661 is 1:4.03 (our arithmetic). The prevalence rationale is citable; the Matthews Correlation Coefficient (MCC) recommendation is ours — MCC never appears in the source, which reports F1 only. Mechanically: MCC requires true negatives, and the centroid algorithm returns TP, FP and FN alone, so MCC is uncomputable inside the framework we borrow the rule from. It needs the negative pool the GIS-based construction defined (negative grid cells minus FP, p3), which our tile grid supplies.

## Positioning annotation (interpretive)

Archaeological prospection prior art, and the single most directly reusable piece of it: the sub-branch of that literature that stopped arguing about architectures and started arguing about what counts as a hit. Its centroid-based measure is the attested disciplinary precedent for our point-symbol matching rule — a detection is correct if it lands inside the ground-truth annotation, not if it overlaps it by some IoU threshold — and it arrives with an empirical demonstration that the rule reproduces what archaeologists were already doing by hand in GIS, albeit on LiDAR relief objects rather than drawn map symbols. It is a metric-design source, not a benchmark: it reports no absolute F1 in text, averages F1 across two classes of very different cardinality, and computes it separately under measures denominated in different units, so values are not commensurable between measures. Cite it for the shape of the evaluation, never for a number.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "a prediction is considered as a TP if the predicted object's centroid falls inside the area of (at least) one ground truth's bounding box; otherwise, the prediction is considered as an FP"
- **Locator:** page_index 5 · p.6 · §4.1 Centroid-Based Measure
- **Paraphrase:** The matching rule is point-in-box: a detection scores as a true positive when its centroid falls within at least one ground-truth bounding box, and as a false positive otherwise. The fraction of overlap plays no part; the ground truth's box extent still sets the acceptance region, and the prediction's box shape determines where its centroid falls.
- **Relevance:** §3 methods — the point-symbol matching rule · Metric hygiene and reporting comparability · **supports**

### KP2
- **Quote (verbatim):** "Archaeological research, however, requires an evaluation measure based on the geographical position of the predicted bounding box in relation to the shapes or areas containing archaeological objects"
- **Locator:** page_index 1 · p.2 · §1 Introduction
- **Paraphrase:** The authors argue that archaeological evaluation must be grounded in where a prediction sits relative to the areas that hold the objects, which is a different question from how much a predicted box overlaps a reference box. The sentence is framed directly against the alternative it rejects, IoU with a threshold.
- **Relevance:** §2 related work — why IoU-thresholded detection metrics do not transfer · Metric hygiene and reporting comparability · **supports**

### KP3
- **Quote (verbatim):** "This guarantees that, if there are two or more distinct predictions, the centroids of which fall inside the same ground truth's bounding box, only one is considered as a TP, while the others are computed as FPs."
- **Locator:** page_index 5 · p.6 · §4.1 Centroid-Based Measure
- **Paraphrase:** Ground truths are consumed on first match, so where several predictions land inside the same annotation, exactly one is credited and the remainder are charged as false positives. The stated policy is 'first-come, first-selected' rather than best-match, so which duplicate is credited is arbitrary; the authors accept this because they observed the circumstance only sporadically, and for their discrete-object class judged best-match selection to offer negligible gain.
- **Relevance:** §4 architecture — duplicate accounting under consensus over passes (the source calls duplicates sporadic on barrows and demonstrates score movement only on Celtic fields; the caution for a multi-pass pipeline is ours) · Metric hygiene and reporting comparability · **complicates**

### KP4
- **Quote (verbatim):** "Barrows are examples of 'discrete' archaeological objects due to their convex, compact and localised shapes, while Celtic fields are examples of 'landscape patterns'"
- **Locator:** page_index 2 · p.3 · §2 Research Area and Archaeological Classes
- **Paraphrase:** The paper formalises a two-class typology of archaeological targets: compact, localised discrete objects such as barrows on one side, and spatially extended landscape patterns such as Celtic fields on the other. The typology drives the design of the two measures, though the authors' stated reason for selecting these classes was their up-to-date inventories and clear visibility in LiDAR.
- **Relevance:** §2 related work — the area-segmentation to point-symbol ladder · Difficulty ladder: area segmentation to point symbols · **extends**

### KP5
- **Quote (verbatim):** "The number of TP, FP and TN for each class (barrow and Celtic field) were obtained from each evaluation measure; iv Based on these values, F1-scores (for each class and a mean) were computed per model, for each evaluation measure."
- **Locator:** page_index 12 · p.13 · §6.1 Experimental Results, steps (iii)–(iv) — 'TN' in step (iii) is [sic]
- **Paraphrase:** Counts are tallied separately for each class and F1 is reported both per class and as an unweighted mean over the two classes, for every model and every measure — so the mean averages a discrete-object score against a landscape-pattern score. Note the source error carried in the quote: step (iii) says 'TP, FP and TN' [sic], but F1 requires FN, and Algorithm 1 (p5) and Algorithm 2 (p7) both declare their output as TP, FP and FN. The same slip recurs in the Figure 8 caption (p8), where Figure 7's caption (p7) has it right.
- **Relevance:** §5 results — per-class versus aggregate reporting · Metric hygiene and reporting comparability · **complicates**

### KP6
- **Quote (verbatim):** "The resulting ratio of positive and negative subtiles (i.e., with or without archaeological objects of interest respectively) of about 1:5 (positive:negative) in the test dataset accurately represents the real-world situation of scarce archaeological objects in different types of complex and dynamic terrain"
- **Locator:** page_index 10 · p.11 · §5.1.2 Test Dataset
- **Paraphrase:** The authors describe their test set as running at about 1:5 positive to negative and justify the imbalance as reflecting how sparse archaeological objects genuinely are across real terrain. Their own counts are 164 positive against 661 negative subtiles, i.e. 1:4.03 (our arithmetic), so the phrase is best read as 'one subtile in five is positive'.
- **Relevance:** §5 results — prevalence realism in the test set (the MCC-alongside-F1 step is ours; MCC does not appear in the source, and is uncomputable from the centroid measure's TP/FP/FN output) · Metric hygiene and reporting comparability · **complicates**

### KP7
- **Quote (verbatim):** "These will also enable us to overcome the need for a large amount of labelled training data, which is one of the main challenges in archaeological automated detection"
- **Locator:** page_index 14 · p.15 · §8 Conclusions
- **Paraphrase:** The authors name the appetite for large labelled training sets as one of the main challenges in archaeological automated detection — endorsing a challenge they credit to earlier work — and look to active-learning, human-in-the-loop approaches to reduce it.
- **Relevance:** §2 related work — the annotation budget a zero-shot VLM pipeline avoids · Annotation budgets and human-in-the-loop · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "not as straightforward as more general object detection tasks, such as finding people or household objects in photographs"
- **Locator:** page_index 14 · p.15
- **Why:** A one-line statement, from inside the archaeological prospection literature, that this detection task is not the task the mainstream benchmarks measure. It is the cleanest available warrant for our refusal to be scored against IoU-thresholded benchmark conventions, and it sets up the point our evaluation section then makes concretely: the measure, not just the model, has to be chosen for the object. Note that the authors report it as an established finding they are endorsing, citing Verschoof-van der Vaart, rather than as a fresh claim.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
