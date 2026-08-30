# AB+ — Convolutional neural networks for archaeological site detection – Finding “princely” tombs

| field | value |
|---|---|
| **citekey** | `caspari_convolutional_2019` |
| **full cite** | Caspari, Gino & Crespo, Pablo (2019) *Convolutional neural networks for archaeological site detection – Finding “princely” tombs.* Journal of Archaeological Science. DOI: 10.1016/j.jas.2019.104998 |
| **register** | Archaeological prospection (CNN site detection / Journal of Archaeological Science) |
| **primary gap** | Archaeological prospection prior art — CNN detection of burial mounds |
| **also touches** | Metric hygiene and reporting comparability; Ground-truth epistemics and gold-standard construction; Difficulty ladder: area segmentation to point symbols; Annotation budgets and human-in-the-loop; Cost, accessibility, and who can actually run the method |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Caspari and Crespo train a small convolutional neural network to recognise Early Iron Age "Saka" burial mounds in open-source Google Earth imagery over the Heiliutan Valley in northern Xinjiang, benchmarked against a biased random guess and two support-vector machine (SVM) baselines. Published in the Journal of Archaeological Science and predating Orengo's Cholistan study (external bibliography, not a claim of this source), it is — our judgement, not the paper's — the reference point for CNN mound detection in archaeology, and the closest object-level prior art to our task in a remote-sensing modality.

Three design features bear on us. The task is patch classification, not localisation: 100 x 100 pixel tiles labelled tomb-present or tomb-absent, 1,212 of them with 169 positives. There is no bounding box, no intersection-over-union, no matching step — it is our tile-level evaluation without our point-symbol layer, and it sits at the easy end of the difficulty ladder for a reason the paper states: the mounds' distinctive shape makes them separable from ordinary ground even at low resolution. Supervision is field-derived and narrow: 59 monuments mapped on the ground, the target class restricted to Saka funerary architecture for its relative homogeneity, many smaller Early Iron Age remains falling below what open-source imagery can resolve. The gold standard is built from easy positives. Augmentation is confined to training — 655 images from zoomed, sheared and flipped positives — with testing and validation on them explicitly ruled out.

Metric hygiene is the most transferable lesson. Results are reported class-conditionally in two tables and the numbers diverge sharply: on tomb-absent tiles the CNN scores precision 0.98, recall 1, F1 0.99; on tomb-present tiles precision 1, recall 0.84, F1 0.91. The linear-kernel SVM scores 0.94 on the negative class and 0.20 on the positive. A reader who quotes "F1 = 0.99" as burial-mound detection performance has quoted the empty tiles, and the labelling scheme inverts the usual convention, coding tomb-present as zero and tomb-absent as one, so any downstream reading of a class-indexed report has to check which class is which. Figure 10 then adds an Average/Total bar across both classes, which in a corpus with roughly one tomb image in seven is largely the negative class again. There are no confidence intervals, no Matthews correlation coefficient, and no repeated splits behind the reported metrics (five-fold cross-validation appears, but only for tuning the SVMs' hyperparameters). The validation-set size is never stated: the 25 per cent holdout covers testing and validation together, so on a proportional split the tomb-present row rests on at most about forty images — our arithmetic from 1,212 patches at 169 positives, not a figure the paper reports — and fewer again if testing and validation are separate subsets of that holdout.

The conclusion names two barriers to uptake: automatic detection demands computer-science collaborators and a bespoke training pipeline, and practitioners are often unaware the option exists. A prompted vision-language model answers the first, not the second; our cost and accuracy trade-space is the question that follows.

## Positioning annotation (interpretive)

Archaeological prospection prior art of the closest possible kind — the same object, burial mounds, detected automatically — but in optical satellite imagery and as tile-level presence/absence rather than symbol localisation, which places it at the easy end of our difficulty ladder in target distinctiveness while sitting alongside our own tile-level F1 and MCC reporting in evaluation granularity. Its principal use to us is twofold: as the attested picture of what a CNN mound detector costs and delivers, and as the cleanest available example of the class-relative versus aggregate metric trap, since the paper headlines no single number and the 0.99 F1 a casual reading would take as its result belongs to the tomb-absent class, while its detection-relevant figure is 0.91 on a positive set the paper never sizes, which proportional arithmetic on the 25 per cent holdout puts at roughly forty tiles or fewer. The paper's own closing complaint — that automatic detection remains inaccessible to practitioners without computer-science collaborators, and unrecognised as an option even where it is feasible — is the motivation our zero-training, prompt-driven approach answers in part, the collaborator half rather than the awareness half.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "Table 2 Classification metrics for validation data set pictures with tombs. Model Precision Recall F1 score Random Guessing 0.59 0.58 0.59 SVM with linear kernel 0.29 0.15 0.20 SVM with RBF kernel 0.76 0.67 0.71 CNN 1 0.84 0.91"
- **Locator:** page_index 6 · p.7 · §4.3 Benchmarks and results — Table 2
- **Paraphrase:** On the class that actually matters for detection — validation images that contain tombs — the CNN reaches precision 1, recall 0.84 and F1 0.91, not the 0.99 reported for tomb-absent images. The linear-kernel SVM collapses to F1 0.20 on the same class. Class-conditional reporting is what makes the gap visible.
- **Relevance:** §2 related work — what published mound-detection numbers actually measure · Metric hygiene and reporting comparability · **supports**

### KP2
- **Quote (verbatim):** "Fig. 10 summarizes both tables and includes a bar for Average/Total, which has a weighted average for both classes under the measure. Showing that overall the CNN is the better performing model."
- **Locator:** page_index 7 · p.8 · §4.3 Benchmarks and results — discussion of Fig. 10
- **Paraphrase:** The headline summary figure averages the two class-conditional tables across both classes. The source does not state the weighting basis; on the standard reading it is weighted by class support, in which case an 86:14 corpus makes the aggregate largely a restatement of the easy class, so the single 'overall' number understates how hard the positive class is. The conclusion holds on any plausible weighting given 169 positives in 1,212.
- **Relevance:** §5 discussion — class-relative versus aggregate reporting · Metric hygiene and reporting comparability · **complicates**

### KP3
- **Quote (verbatim):** "The dataset is composed of 1212 images with 169 including tombs."
- **Locator:** page_index 5 · p.6 · §4.1 Data preprocessing
- **Paraphrase:** The whole labelled corpus is 1,212 image patches of which 169 contain tombs — a small, heavily imbalanced supervision budget, with roughly one positive for every seven images.
- **Relevance:** §3 methods — supervision budgets in mound detection · Annotation budgets and human-in-the-loop · **supports**

### KP4
- **Quote (verbatim):** "the distinctive shape of the tombs makes them easily distinguishable from other patches of land even in low-resolution data"
- **Locator:** page_index 5 · p.6 · §4.1 Data preprocessing
- **Paraphrase:** The authors state that the target is visually distinctive enough to be separated from ordinary ground even at low resolution — the detection problem is easy by construction of the target class. Their own results complicate that claim, and we should carry the complication: the SVM baselines still failed badly on the positive class, which the authors themselves call surprising given that the tomb shapes are simple to the naked eye, and the CNN's positive-class recall is 0.84 rather than near-ceiling. 'Easy' is relative to the model, not a property of the target alone.
- **Relevance:** §2 related work — positioning our task on the difficulty ladder · Difficulty ladder: area segmentation to point symbols · **complicates**

### KP5
- **Quote (verbatim):** "There is a plethora of architectural remains from the Early Iron Age present in the survey area, but many of them are too small to be reliably detected in open source optical satellite data"
- **Locator:** page_index 2 · p.3 · §2 The field archaeological foundation
- **Paraphrase:** Many Early Iron Age structures in the survey area are below the resolving power of the imagery. The target class is Saka funerary architecture, chosen for its relative homogeneity and further bounded by what open-source optical data can resolve — large mounds with circular ditches.
- **Relevance:** §3 methods — what the substrate permits a gold standard to contain · Ground-truth epistemics and gold-standard construction · **supports**

### KP6
- **Quote (verbatim):** "This occurs because other images that might just simply be circular in shape are likely to be picked up by the SVM models as tombs. This has been an issue with other detection algorithms before"
- **Locator:** page_index 7 · p.8 · §4.3 Benchmarks and results — why the SVMs underperform
- **Paraphrase:** The SVM baselines fail on the positive class because anything roughly circular reads as a tomb; the authors note this as a recurring failure mode of earlier detection algorithms rather than a quirk of these models. The CNN did not share it here — its positive-class precision is 1 — which the authors credit to filters that pick up subtlety beyond the circular outline.
- **Relevance:** §4 architecture — the confusable-distractor failure mode a verifier stage targets · Archaeological prospection prior art — CNN detection of burial mounds · **supports**

### KP7
- **Quote (verbatim):** "Both the complexity of the method which often demands cooperation with computer science specialists, and the lack of awareness for the possibility play a role in the so far rare application of automatic detection algorithms by archaeological practitioners. The authors do not expect to see a widespread application unless intuitive tools are developed for feature selection, algorithm training and visualization of ready-to-use results."
- **Locator:** page_index 7 · p.8 · §5 Conclusions
- **Paraphrase:** The authors attribute the rarity of automated detection in archaeological practice to two causes jointly — methodological complexity requiring computer-science collaborators, and lack of awareness that the option exists — and expect no wider adoption until tools exist that handle feature selection, training and result visualisation for the practitioner.
- **Relevance:** §1 introduction — why a prompted VLM is worth testing at all · Cost, accessibility, and who can actually run the method · **extends**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "CNNs are a versatile solution to a plethora of problems in archaeology which works well when plenty of data is available. It comes at the cost of not being able to fully and analytically understand the process of solving the problem. The outcomes however can be qualitatively assessed and the solution is reproducible."
- **Locator:** page_index 1 · p.2
- **Why:** The CNN bargain stated by an archaeologist in 2019: data hunger in exchange for opacity. The hook is quoted through the authors' own qualification — outcomes remain qualitatively assessable and the solution reproducible — because that clause must travel with it: it cuts against us as much as for us, a trained network being deterministic where a sampled vision-language model is not. Used honestly the hook sets up a two-sided contrast: we need no training corpus and we return a natural-language rationale the verifier can interrogate, but the reproducibility Caspari and Crespo claim as a CNN virtue is precisely what our consensus-over-passes design has to buy back.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
