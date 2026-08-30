# AB+ — Curriculum learning-based strategy for low-density archaeological mound detection from historical maps in India and Pakistan

| field | value |
|---|---|
| **citekey** | `berganzo-besga_curriculum_2023` |
| **full cite** | Berganzo-Besga, Iban et al. (2023) *Curriculum learning-based strategy for low-density archaeological mound detection from historical maps in India and Pakistan.* Scientific Reports. DOI: 10.1038/s41598-023-38190-x |
| **register** | Archaeological prospection / computer vision (Scientific Reports) |
| **primary gap** | Archaeological prospection prior art — mound-symbol detection on historical maps |
| **also touches** | Metric hygiene and reporting comparability; Calibration and operating-point transfer; Annotation budgets and human-in-the-loop; Ground-truth epistemics and gold-standard construction; Difficulty ladder: area segmentation to point symbols; Historical-map extraction lineage; Cost/accuracy trade-space |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Berganzo-Besga and colleagues train two Mask R-CNN instance-segmentation models — one per depiction type, hachure and form-line — to find mound symbols on 645 georeferenced Survey of India sheets, then apply them across 470,500 km2 of the Indus basin, detecting 2802 hachure and 3145 form-line candidates that the authors flag as still requiring validation by remote sensing, archival work, and ground survey. Only 43 of the 645 maps carried known mounds: 286 hachure and 103 form-line symbols for training and validation, the training split alone being 22 maps with 168 hachure and just 26 form-line instances. Same object family, same substrate, same sparse target among dense cartography — the closest prior art we have.

Its central contribution is the low-density argument, which is really a metric-hygiene argument. On a high-density validation pool the first hachure model scores F1 78.73; on a low-density pool with identical true positives and false negatives — 87 and 21 in both rows — it scores 18.67, because false positives rise from 26 to 737. Density is manipulated purely through the negative pool, so sparse-detection F1 is a property of the evaluation tile set as much as of the model. Sharpest of all is what the finished system buys on each pool: the whole apparatus moves the high-density hachure model from 78.73 to 78.97, +0.24 points, against +57.6 (18.67 to 76.24) on the low-density pool.

That apparatus is supervision engineering, not architecture: random translation and rotation; a 'Doppelgänger' technique pasting a mound's interior outside the symbol as a hard negative; a refinement pass (DA4) combining harvested false positives with correct mounds redrawn as continuous-line circles, 88 form-line and 127 hachure elements multiplied to 8800 and 12,700 placements; then a curriculum learning 75 synthetic exemplars per class before fine-tuning on real ones. The low-density hachure chain reads 18.67, 69.31, 75.86, 76.24 — with four cautions. The 75.86 row (77 TP / 38 FN / 11 FP) reappears bit-identical as the filter table's Filter1+Filter2 row, so it already carries the area and blob filters and cannot be credited to curriculum learning alone. Intermediates are non-monotonic (65.14, 58.12, 64.45). The gain is entirely precision, 10.56 to 88.51, while recall falls 80.56 to 66.96 — a loss the authors concede. And no row-to-row comparison is fixed-target: positives wobble 108, 108, 110, 113, 112, 113, 115 across the augmentation tables and 312, 121, 115 across the filter table, so even the 18.67-to-76.24 span sets 108 positives against 115.

Transfer is measured rather than assumed. Binning test maps by background-RGB similarity, hachure F1 falls 72.44 to 64.19 across the full spread; form-line falls from 93.75 on a 16-instance closest bin to 70.55, and for a narrower target, since the form-line detector covers only the most common typology where the hachure detector covers all, and Table 10 excludes four off-typology detections from both TP and FP. The authors conclude that an adaptive algorithm, retrained per map, is needed — a transfer tax quantified in our own terms, with its denominators visible.

## Positioning annotation (interpretive)

The nearest prior art in the corpus on our own substrate — hand-drawn mound symbols on a heterogeneous colonial topographic map series, detected at landscape scale by a CNN — and therefore the position our approach is defined against. It reaches usable precision only through two class-specific detectors, a five-stage augmentation and curriculum stack, a hand-built geometric and topographic filter cascade, and an explicit call for per-map retraining, all on a few hundred annotated symbols; the two structural conditions it names, low feature density and scarce training data, are the authors' own words, but the inference that they motivate a zero-shot prompted detector-plus-verifier is ours alone, since the source never discusses foundation models, prompting, or detection without training. Its low-density analysis is the strongest methodological warning in this cluster, and the lesson cuts both ways: adopt its evaluation stance — force the empty tiles into the metric — but do not borrow its reporting practice, because the positive counts shift from row to row throughout the paper, through the augmentation tables as well as the filter cascade, so no reported comparison is strictly fixed-target, and nothing chance-corrected appears anywhere.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "The density of the features must be taken into account11,12 since good results in high-density areas may actually be hiding much worse results in low-density areas. The first results showed a number of FPs of up to twenty times more than the mound features present in the area (Tables 1 and 2)."
- **Locator:** page_index 9 · p.10 · Discussion — Low-density approach
- **Paraphrase:** Detection scores reported on a feature-dense evaluation pool can conceal far worse behaviour on a sparse one: their own first models produced up to twenty times more false positives than there were real mound features in the area (the 'up to' is the form-line model, 1366 false positives against 67 real features; the hachure model is nearer seven times). Density of the evaluation set is therefore a reporting parameter that has to be declared, not an incidental property of the test data.
- **Relevance:** §5 discussion — density-dependent metrics and evaluation-pool composition · Metric hygiene and reporting comparability · **supports**

### KP2
- **Quote (verbatim):** "The resulting algorithms have a recall value of 52.61% and a precision of 82.31% for the hachure mounds, and a recall value of 70.80% and a precision of 70.29% for the form-line mounds, which allowed the detection of nearly 6000 mound features over an area of 470,500 km2, the largest such approach to have ever been applied. If we restrict our focus to the maps most similar to those used in the algorithm training, we reach recall values greater than 60% and precision values greater than 90%."
- **Locator:** page_index 0 · p.1 · Abstract
- **Paraphrase:** The operating point across the full test-set similarity spread is recall 52.61% and precision 82.31% for hachure symbols and 70.80% / 70.29% for form-line, while restricting evaluation to the sheets most like the training maps lifts recall above 60% and precision above 90%. Scope matters: these are the |3σ| and |0.5σ| rows of Tables 9 and 10, measured on 21 hand-annotated test maps (230 hachure and 137 form-line features). Nothing was measured over the 645-sheet corpus or the 470,500 km2 deployment, whose nearly 6000 detections are unvalidated candidates. The gap between the two figures is the cost of deploying beyond the sheets the model was calibrated on, and it is reported rather than hidden — though the closest-bin hachure recall is 60.13%, clearing the abstract's 'greater than 60%' by 0.13 points.
- **Relevance:** §5 discussion — carried versus oracle operating points · Calibration and operating-point transfer · **supports**

### KP3
- **Quote (verbatim):** "Of the 645 maps used, only 43 contained known mound features, which have been used for training and validation: 286 hachure and 103 form-line mound features."
- **Locator:** page_index 3 · p.4 · Materials and methods — Deep learning model
- **Paraphrase:** Across a 645-sheet corpus, known mound features existed on only 43 maps, and the entire training and validation supervision amounts to 286 hachure and 103 form-line annotated symbols — of which the training split alone is 22 maps carrying 168 hachure and just 26 form-line instances. The annotation budget available to a supervised map-symbol detector in archaeology is a few hundred instances, and for one of the two detectors here a few dozen, not the tens of thousands computer-vision practice assumes.
- **Relevance:** §2 related work — annotation budgets in map-symbol detection · Annotation budgets and human-in-the-loop · **supports**

### KP4
- **Quote (verbatim):** "ML algorithms like Mask R-CNN typically evaluate their models on images that contain labelled objects and do not evaluate those without labels. Since our goal is to demonstrate the good performance of the model in low-density areas, we have created artificial mound labels on all those images without real mounds to force the analysis in them."
- **Locator:** page_index 3 · p.4 · Materials and methods — Deep learning model
- **Paraphrase:** Standard detection evaluation silently skips images with no labelled object, so empty tiles contribute no false positives to the score. They defeat this by planting 4 × 4 pixel dummy labels in every empty image, forcing the negative regions into the evaluation and exposing false-positive behaviour where features are absent. An edge-discard rule guarantees the dummies are never detected; how they are kept out of the false-negative count is not stated.
- **Relevance:** §3 methods — tile-pool construction and evaluation of negatives · Metric hygiene and reporting comparability · **extends**

### KP5
- **Quote (verbatim):** "Other studies with similar elements such as burial mounds4, have shown that despite having limited training data, features of interest are detectable due to the characteristic circular shape of the tumuli, which presented few variations. The archaeological elements of this study, despite being mound features like those of previous studies where we encountered a similar problem, are much more diverse. Since they are symbols drawn by human hands and not images of their actual form, whether aerial or satellite, the features are noticeably divergent in style from each other."
- **Locator:** page_index 2 · p.3 · Introduction — training data and feature diversity
- **Paraphrase:** Burial mounds imaged from the air are learnable from few examples because real tumuli are consistently circular; the same object rendered as a hand-drawn map symbol is not, because draughtsmen vary. Moving from the landform to its cartographic sign raises intra-class variability and therefore the supervision required, even though the target archaeology is identical — the authors' own explanation for why a small training set was not enough.
- **Relevance:** §1 introduction — the area-segmentation to point-symbol difficulty ladder · Difficulty ladder: area segmentation to point symbols · **supports**

### KP6
- **Quote (verbatim):** "they are not included in the automated detection given the low correspondence of this type of mound feature with archaeological sites, where 86.36% of the examples visited on the ground were found not to be archaeological sites"
- **Locator:** page_index 3 · p.4 · Materials and methods — Deep learning model
- **Paraphrase:** A whole symbol subtype, shaded-relief mounds, is excluded from detection because 86.36% of the examples visited on the ground were not archaeological sites. The figure is not this study's own fieldwork but prior ground-truthing (Green et al., the paper's reference 3), which the authors elsewhere describe as covering only a small number of well-preserved mounds. The mapped symbol and the archaeological site are separate objects, and which symbol classes are worth detecting is an archaeological judgement made on external, thin evidence before any model is trained.
- **Relevance:** §3 methods — what counts as a positive when the symbol is the ground truth · Ground-truth epistemics and gold-standard construction · **complicates**

### KP7
- **Quote (verbatim):** "We predicted that manually digitising all mound features from the 645 historical maps used in this research region would take an experienced professional more than 120 work hours based on the manually digitised mound features prepared as training data for the algorithm. The detection time, running each algorithm on a single NVIDIA A40 GPU, has been more than 6 computing hours."
- **Locator:** page_index 11 · p.12 · Discussion — Comparison to manual digitisation of mound features
- **Paraphrase:** Hand-digitising every mound symbol across the 645 sheets was estimated at more than 120 expert working hours, against more than 6 hours of GPU time per algorithm for the automated pass. This is the rare attested labour-versus-compute baseline in this literature, but it is not labour parity: the compute figure covers inference only, excluding the 756 features hand-digitised for the study and the five-stage augmentation and filter engineering. The authors justify automation by headroom to scale rather than by the saving on the present corpus.
- **Relevance:** §5 discussion — cost/accuracy trade-space and the labour baseline · Cost/accuracy trade-space · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "Our proposed approach addresses two of the most common issues in archaeological automated survey, the low-density of archaeological features to be detected, and the small amount of training data available."
- **Locator:** page_index 0 · p.1
- **Why:** The two structural conditions of archaeological detection stated by archaeologists in their own terms, and the cleanest setup for our §2 pivot: a supervised CNN answers both with augmentation, synthetic data, and curriculum learning, which is exactly the supervision a prompted vision-language model does without. The pivot is ours — the source names the conditions, not the alternative.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
