# AB+ — Learning to Look at LiDAR: the use of R-CNN in the automated detection of archaeological objects

| field | value |
|---|---|
| **citekey** | `verschoof-vandervaartLearningLookLiDAR2019` |
| **full cite** | Verschoof-van der Vaart, Wouter Baernd & Lambers, Karsten (2019) *Learning to Look at LiDAR: the use of R-CNN in the automated detection of archaeological objects.* Journal of Computer Applications in Archaeology. DOI: 10.5334/jcaa.32 |
| **register** | Archaeology-native (computational archaeology / archaeological prospection) |
| **primary gap** | Archaeological prospection prior art — supervised CNN detection of burial mounds |
| **also touches** | Metric hygiene — class-relative vs aggregate F1; Ground-truth epistemics; Annotation budgets; Difficulty ladder — area features vs point-like mounds; Calibration transfer / carried vs oracle operating points; Cross-study comparability of reported F1 |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Verschoof-van der Vaart and Lambers report the first year of a Leiden PhD project: WODAN, a workflow that preprocesses about 440 km2 of LiDAR data acquired from the Veluwe — part of a circa 2,350 km2 forested research area in the central Netherlands — into Faster R-CNN inputs, and is designed to detect three classes of archaeological object. It is the earlier, R-CNN paper by the lead author of the later WODAN2.0 study, and our closest-object prior art: barrows are burial mounds, so this is the supervised baseline our pipeline is measured against.

First, annotation budget. No suitable datasets existed, so they were built: 365 training, 41 validation, and 73 testing sub-images out of 2,940 — 749 labelled barrows to train on, 78 in the test set. Charcoal kilns were never detected in any experiment, and the authors give their 119 training examples, against 749 and 904 for the others, as the most probable cause — a per-class cost a zero-shot prompt does not incur. The counterweight sits in the same table: with training data fixed, backbone and anchor choices move barrow F1 from 0.49 to 0.79, five runs detected nothing, and nine Resnet50 runs managed one class. Annotation binds at the low end; architecture dominates the variation above it.

Second, ground truth. Labelling turned up 745 previously unknown potential barrows; sub-images holding only these were dropped, but candidates sharing a sub-image with a known object were labelled as barrows — unvalidated candidates entered the ground truth as positives. Drift-sand zones went too, the dunes being 'indistinguishable from barrows, even for humans'. Those 754 exclusions are stated for training and validation, and the test-pool arithmetic (2,940 − 754 − 1,360 − 406 = 420) implies they preceded the draw of the 73 test images; but the authors also deliberately added difficult objects of confusion. A partial transfer tax, visible at corpus construction and partly offset on purpose.

Third, metric hygiene. The headline is a top MaF1 of 0.66 and an average of 0.49. MaF1 abbreviates a micro-averaged score despite reading like macro; reconstructing class counts from the per-class rates confirms it (0.658 for experiment 5, 0.450 for experiment 4). Recomputing, the 0.49 the paper calls the mean of 'all experiments' is the mean of the six tabulated values (0.485), not of the 20 conducted. The rankings then disagree: experiment 5 wins on MaF1 (0.66) with a barrow F1 of 0.59, while experiment 4 has the best barrow F1 (0.79) at MaF1 0.46 — third of six, inside the tight 0.43–0.47 band holding all but the winner. It is the class-relative 0.79 that the cross-study table carries, as 'our best performing model'. Anyone quoting this paper must say which figure, on which class.

Fourth, the difficulty ladder runs backwards: barrows beat Celtic fields — but on precision, not recall (Celtic-field recall reaches 0.97, above every barrow recall), and confounded by sub-image cutting that dissects extended features. Area features are not the easy rung, though their invisibility is not shown either.

## Positioning annotation (interpretive)

Archaeological prospection prior art, and the closest-object member of that lineage: the target class is burial mounds, detected by a supervised region-proposal CNN on LiDAR-derived relief. It sets a prior-art marker our §2 must address — barrow F1 0.79, bought with 749 hand-labelled examples of that one class and scored on 78 — though the paper's own table lists three mound studies above it (0.98, 0.86, 0.84) and calls the comparison rough, and though annotation count binds only at the low end here: the 119-example class never learned, while backbone and anchor choices swing barrow F1 from 0.49 to 0.79 on identical training data. Its second use is cautionary — the headline aggregate and the cross-study row are different numbers from different experiments, exactly the class-relative-versus-aggregate confusion our metric-hygiene passage exists to pre-empt.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "WODAN Machine Learning (R-CNN) 55 6 23 0.71 0.90 0.79"
- **Locator:** page_index 7 · p.8 · Table 3 — comparison with other barrow/mound detection research
- **Paraphrase:** The row this paper contributes to its own cross-study comparison table reports 55 true positives, 6 false positives, and 23 false negatives, giving recall 0.71, precision 0.90, and F1 0.79. These are barrow-class figures: the table covers 'barrows or equivalent mounds', and recomputing from the counts (55/78 = 0.705, 55/61 = 0.902, F1 = 0.791) reproduces the triple and matches the barrow column of experiment 4 in Table 2 — and no other row. The paper introduces this row as 'our best performing model', which is what makes its mismatch with the 0.66 MaF1 headline an internal inconsistency rather than two unrelated numbers.
- **Relevance:** §2 related work — prior-art floor for burial-mound detection · Archaeological prospection prior art — the barrow-detection figure a related-work section would quote · **supports**

### KP2
- **Quote (verbatim):** "The results of the experiments (see Table 2) show a top performance of the Faster R-CNN model of 0.66 (MaF1) and an on average performance of 0.49 (average MaF1 score of all experiments)."
- **Locator:** page_index 6 · p.7 · §5 Initial Results
- **Paraphrase:** The paper's headline is an aggregate: a best micro-averaged F1 of 0.66 across the two detected classes, and a mean of 0.49. Neither figure is the 0.79 that reaches the cross-study table. The paper's own words are 'average MaF1 score of all experiments', but recomputing shows 0.49 to be the mean of the six tabulated values (0.485 exactly) rather than of the 20 conducted — five of which detected nothing at all.
- **Relevance:** §2 related work; §5 results — stating which number, on which class, a comparison quotes · Metric hygiene — class-relative vs aggregate F1 · **complicates**

### KP3
- **Quote (verbatim):** "F1-scores lie between 0.49 and 0.79 for barrows (on average 0.67) and between 0.29 and 0.68 for Celtic fields (on average 0.43). The latter shows that the model performs better at detecting barrows than Celtic fields."
- **Locator:** page_index 6 · p.7 · §5 Initial Results
- **Paraphrase:** Per-class F1 spans 0.49–0.79 for barrows and 0.29–0.68 for Celtic fields, and the authors read this as the model detecting compact mounds more reliably than the extended field systems. The advantage is precision-driven rather than a failure to see area features: Celtic-field recall reaches 0.97 and 0.92, above every barrow recall in the table, while its precision never exceeds 0.71. It is also confounded by the 500 × 298 m sub-image cutting, which dissects extended features far more than compact ones — a problem the authors flag and plan to address with overlapping sub-images.
- **Relevance:** §2 related work; §5 discussion — where mounds sit on the difficulty ladder · Difficulty ladder — area features vs point-like mounds · **complicates**

### KP4
- **Quote (verbatim):** "At the moment of writing 745 potential barrows have been discovered in the datasets."
- **Locator:** page_index 4 · p.5 · §4.1 Datasets
- **Paraphrase:** Labelling the imagery surfaced 745 candidate barrows absent from the existing inventories; because their status could not be settled, sub-images containing only such candidates were removed from the datasets. Potential barrows sharing a sub-image with a known object were, by contrast, labelled as barrows, so unvalidated candidates entered the ground truth as positives while candidate-only sub-images left the corpus.
- **Relevance:** §3 corpus and ground truth — incompleteness of the reference inventory · Ground-truth epistemics · **supports**

### KP5
- **Quote (verbatim):** "Sub-images containing large parts of this drift-sand were excluded as well, because the small dunes within these areas are indistinguishable from barrows, even for humans."
- **Locator:** page_index 4 · p.5 · §4.1 Datasets
- **Paraphrase:** Terrain whose natural landforms human experts cannot separate from the target class was removed — stated for the training and validation sets, and implied for the test-selection pool by the arithmetic (2,940 − 754 − 1,360 − 406 = 420 sub-images, from which the 73 test images were drawn). The authors nonetheless deliberately added sub-images containing difficult objects of confusion to the test set, so the curation is partial: the hardest confusion class is absent, other confusions were retained by design.
- **Relevance:** §3 corpus and ground truth; §5 discussion — transfer taxes from a curated test set to deployment · Ground-truth epistemics / evaluation-set composition · **complicates**

### KP6
- **Quote (verbatim):** "examples in the training set (119 versus 749 and 904 for the other classes; see Table 1)"
- **Locator:** page_index 6 · p.7 · §6 Discussion
- **Paraphrase:** The authors attribute the total failure to detect charcoal kilns to that class's training count — 119 labelled examples against 749 barrows and 904 Celtic fields — offered as the most probable cause, with size, complexity, and terrain interference judged to seem not to have been the main problem because objects of comparable size and complexity were detected.
- **Relevance:** §2 related work; §5 discussion — what a supervised route costs per symbol family · Annotation budgets — per-class example counts as a binding constraint at the low end · **supports**

### KP7
- **Quote (verbatim):** "The main complications are insufficient details on the number of true- and false positives (e.g. Cerrillo-Cuenca 2017)"
- **Locator:** page_index 6 · p.7 · §6 Discussion
- **Paraphrase:** Comparing detection results across archaeological studies is judged difficult because papers frequently omit the counts needed to recompute precision and recall, and because verification datasets differ — the authors instance Kramer (2015), whose ground truth included levelled barrows that could not be detected in LiDAR at all and so inflated the false negatives.
- **Relevance:** §2 related work — why headline F1 values across the prospection literature are not commensurable · Cross-study comparability of reported F1 · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "in archaeological prospection the focus lies not only on characterising objects (or classifying, the typical task of a CNN) but also on obtaining the exact position (or localising) of these objects in the wider landscape"
- **Locator:** page_index 2 · p.3
- **Why:** An archaeology-native statement of why the task is detection rather than classification — useful for framing the move from 'is there a mound symbol on this sheet' to 'where, exactly', which is what our tile-level and point-matched evaluation both assume.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
