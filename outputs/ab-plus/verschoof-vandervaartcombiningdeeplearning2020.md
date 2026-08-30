# AB+ — Combining Deep Learning and Location-Based Ranking for Large-Scale Archaeological Prospection of LiDAR Data from The Netherlands

| field | value |
|---|---|
| **citekey** | `verschoof-vandervaartCombiningDeepLearning2020` |
| **full cite** | Verschoof-van der Vaart, Wouter B. et al. (2020) *Combining Deep Learning and Location-Based Ranking for Large-Scale Archaeological Prospection of LiDAR Data from The Netherlands.* ISPRS International Journal of Geo-Information. DOI: 10.3390/ijgi9050293 |
| **register** | Archaeology-native (LiDAR prospection / deep learning) |
| **primary gap** | Archaeological prospection prior art — evaluation-set realism and the transfer tax |
| **also touches** | Human baselines for detection tasks; Consensus aggregation over independent passes; Ground-truth epistemics and reference-standard construction; Operating-point selection and metric hygiene; Difficulty ladder: area features to point-like objects; Annotation budgets and precision-versus-recall by user role |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Verschoof-van der Vaart and colleagues present WODAN2.0, a Faster R-CNN workflow (VGG16 backbone, fifteen bagged models) detecting prehistoric barrows, Celtic fields, and (post)medieval charcoal kilns in airborne LiDAR from the Veluwe. This is the closest-object prior art in our corpus: barrows are burial mounds, the feature class our study reads off Soviet topographic sheets, in terrain relief rather than as a drawn symbol.

Its central contribution to us is the test-set design. The team replaced the small, non-random test set inherited from WODAN1.0 with a large, random one — 828 subtiles of which only 164 (19.8%) contain any archaeology — because the former did not represent the real-world scarcity of archaeological objects; that it had also flattered the model is what the new set then showed. Barrow F1 falls from 70.1 to 49.8; only that pair is like-for-like, since the Celtic-field fall (70.0 to 45.5) spans a change of counting convention — plots in the non-random set, demarcated areas in the random — and charcoal kilns (18.0) are scored on the random set only. The paper splits the drop in two, but only the precision half — prevalence and low object density — is asserted firmly; the recall attribution to variety in preservation state is explicitly hedged, and neither is ablated. Two caveats attend the prevalence figures: the printed 6.7:1 ratio for the non-random set does not reconcile with its Table 2 counts (63 positive, 10 negative), and the sets use different subtile sizes (1000 by 600 px against 600 by 600 px), so neither ratio is area-normalised.

Two threads are metric hygiene. The headline random-test barrow figure is chosen post hoc: the authors sweep confidence 80–91 against a detections-per-grid-cell threshold (1 to ≥10) and report the best cell. On our reading, 49.8 is the maximum of that 120-cell grid (Table 6, confidence 89 and ≥4 detections), and the grid's (80, ≥1) cell is exactly Table 7's 24.0 — so 'without thresholds' means the field-default confidence 80 with no cell-count threshold, a carried threshold rather than an absent one, which sharpens the oracle-versus-carried contrast. Also on our reading, the reported '17% and 35%' improvement is absolute F1 points on the random set alone (45.5 − 27.7 = 17.8; 49.8 − 15.3 = 34.5).

The human baseline is genuine: Heritage Quest ran a near-identical task on the same data and beat WODAN2.0 on all three classes (57.9, 80.1, and 45.5 F1), chiefly on precision — at Table 5's threshold-tuned operating points. Without thresholds (Table 7) its F1 falls below WODAN2.0's on barrows (14.8 against 24.0) and charcoal kilns (5.0 against 8.9), though its recall is higher on all three; the Conclusions assert non-attainment of human performance independently of operating point. The closest analogue to our consensus-over-passes design is WODAN2.0 itself — fifteen bootstrap resamples, fifteen models, detections aggregated into 20 by 20 m cells for barrows and 15 by 15 m for kilns, then thresholded on detections per cell — with Heritage Quest's fifteen classifications per snippet its human-side counterpart.

## Positioning annotation (interpretive)

The closest-object prior art in the corpus and its cleanest external measurement of the transfer tax: barrows are burial mounds, and the same detector loses 20.3 F1 points (70.1 to 49.8) when moved from a small, purposively assembled test set to one randomly sampled within two extensively studied, object-rich areas of the Veluwe — so its 1:4 prevalence is a conservative floor on landscape realism, the paper claiming only that this set "could better represent the real-world situation". It sits on the CNN side of our related-work framing — supervised, single-sensor, a closed three-class ontology in a single model, trained on 1024 annotated subtiles — yet it anticipates three of our design commitments: consensus aggregation over independent passes (fifteen bagged models with spatial aggregation, and fifteen citizen classifications per tile), a confidence-tiered reference standard built out of inter-analyst disagreement rather than adjudicated away, and an explicit human benchmark the automated system does not beat. Cite it for the prevalence-shift mechanism and the human baseline; cite headline numbers on either side only with the qualifier that they are threshold-tuned, since without thresholds WODAN2.0 scores 24.0 F1 on barrows and the human baseline 14.8.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "Experiments show that WODAN2.0 has a performance of circa 70% for barrows and Celtic fields on the small, non-random testing dataset, while the performance on the large, random testing dataset is lower: circa 50% for barrows, circa 46% for Celtic fields, and circa 18% for charcoal kilns."
- **Locator:** page_index 0 · p.1 · Abstract
- **Paraphrase:** The abstract states the transfer drop in the authors' own headline: F1 of about 70% for barrows and Celtic fields on the small, non-random test set, falling to about 50% for barrows, 46% for Celtic fields, and 18% for charcoal kilns on the large, random one. The exact Table 5 values are 70.1 and 70.0 on the non-random set, and 49.8, 45.5, and 18.0 on the random set.
- **Relevance:** §2 related work — archaeological prospection prior art · Calibration transfer — small purposive gold standard to realistic deployment sample · **supports**

### KP2
- **Quote (verbatim):** "the proportion of positive and negative subtiles (i.e., subtiles with or without archaeological objects) varies greatly between the non-random (6.7:1, positive:negative) and the random (1:4, positive:negative) test dataset. This increased amount of negative subtiles in the latter results in more false positives."
- **Locator:** page_index 15 · p.16 · §6.1 Non-Random versus Random Test Dataset
- **Paraphrase:** The mechanism behind the drop is a prevalence shift: positive tiles outnumber negative ones 6.7:1 in the non-random set but are outnumbered 1:4 in the random one, and the extra negative area generates the additional false positives that depress precision. Two cautions on the printed ratios: 6.7:1 does not reconcile with the paper's own Table 2 counts for that set (63 positive, 10 negative) — quote it as printed rather than recomputing it — and the two sets use different subtile sizes (1000 by 600 px non-random, 600 by 600 px random), so the ratios are not area-normalised.
- **Relevance:** §5 discussion — why deployment performance falls below gold-standard performance · Prevalence shift as the mechanism of the transfer tax · **supports**

### KP3
- **Quote (verbatim):** "In this research, the confidence threshold was varied between 80 and 91, with intervals of 1, and the threshold for the number of detections per grid cell was varied between 1 and ≥10, with intervals of 1 (see Table 6). By finding the optimal trade-off between confidence and number of detections per grid cell, the highest F1-score is obtained."
- **Locator:** page_index 12 · p.13 · §5.1 Implementation Details — thresholds
- **Paraphrase:** The reported figures come from a two-dimensional threshold sweep — twelve confidence values crossed with ten detections-per-cell values — from which the highest-scoring combination is reported. The operating point is therefore selected on the evaluation data rather than carried in from elsewhere.
- **Relevance:** §3 methods — threshold selection and metric comparability · Operating-point selection — oracle versus carried thresholds · **complicates**

### KP4
- **Quote (verbatim):** "WODAN2.0 (R) recall 79.6 82.9 38.5 precision 14.1 13.3 5.1 F1-score 24.0 22.9 8.9"
- **Locator:** page_index 13 · p.14 · Table 7 — performance without thresholds
- **Paraphrase:** Without thresholds, the same workflow on the random test set reaches recall 79.6, precision 14.1, and F1 24.0 on barrows (22.9 on Celtic fields, 8.9 on charcoal kilns) — roughly half the tuned F1 in each class, with recall high and precision collapsing. On our reading this is not a zero-threshold run but the field-default confidence 80 with no cell-count threshold, since Table 6's (80, ≥1) cell is exactly 24.0: a genuinely carried threshold rather than the absence of one, which is a cleaner carried-versus-oracle contrast than the paper's own wording suggests.
- **Relevance:** §5 discussion — what an untuned operating point costs · Cost-accuracy trade-space — carried versus oracle operating points · **complicates**

### KP5
- **Quote (verbatim):** "Comparing the performance of WODAN2.0 and Heritage Quest shows that the former has not reached general human performance on the object detection task in the research area. Table 5 shows that the citizen researchers of Heritage Quest outperform WODAN2.0 on all archaeological classes. The main difference in performance is related to the precision (see Table 5)."
- **Locator:** page_index 15 · p.16 · §6.2 Computer and Human Performance
- **Paraphrase:** On the threshold-tuned results of Table 5, the automated workflow does not reach human performance on any of the three classes, and the shortfall is concentrated in precision rather than recall. The scope matters: at Table 7's untuned operating point the F1 ordering reverses on barrows (24.0 against 14.8) and charcoal kilns (8.9 against 5.0), with Heritage Quest ahead only on Celtic fields and on recall for all three. The Conclusions nonetheless assert non-attainment of general human performance without reference to an operating point, so the headline verdict stands.
- **Relevance:** §2 related work — human-baseline framing · Human baselines for detection tasks · **supports**

### KP6
- **Quote (verbatim):** "Every individual LiDAR snippet was classified by fifteen different users before it was retired, therefore providing possibilities to aggregate the classifications and to explore inter-analyst agreement [53]. This type of "consensus" [54] improves accuracy of the classifications and is an established method to produce reliable data by guaranteeing minimal inter-analyst variability [55]."
- **Locator:** page_index 5 · p.6 · §2.4 Heritage Quest Dataset
- **Paraphrase:** The human baseline is itself a consensus system: every image tile is independently classified fifteen times, and the classifications are aggregated, which the authors present as an established route to accuracy by suppressing inter-analyst variability. Note that the aggregation rule actually scored is a detections-per-grid-cell count swept for best F1, so the human baseline's consensus operating point is oracle-selected in the same way the model's is.
- **Relevance:** §3 methods — consensus-over-passes rationale · Consensus aggregation over independent passes · **supports**

### KP7
- **Quote (verbatim):** "Inter-analyst variability (also see [48]) was resolved by assigning different levels of confidence to individual classifications: objects that were marked by both researchers and/or extant archaeological objects on record in any of the national archaeological databases were given high confidence, while objects, marked by only one researcher, were given low confidence."
- **Locator:** page_index 5 · p.6 · §2.3 Test Datasets (continued)
- **Paraphrase:** The reference standard is built from two independent expert passes, with disagreement preserved as a confidence tier rather than adjudicated away: objects marked by both analysts or already on record are high confidence, objects marked by one are low. Two qualifications for a ground-truth-epistemics point: the two experts are the paper's own first and fourth authors, so the standard is not independent of the modelling team, and the paper never states whether low-confidence objects count as ground truth in the reported metrics (Table 1 splits the 137 barrows 65 low / 72 high).
- **Relevance:** §3 methods — gold-standard construction and its uncertainty · Ground-truth epistemics — a graded rather than binary gold standard · **extends**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "Barrows are round or oval-shaped earthen mounds that demarcate the burial place of a select group of people"
- **Locator:** page_index 2 · p.3
- **Why:** The one-line attestation that this prior art shares our target class rather than merely our task: barrows are burial mounds. It lets the related-work paragraph state that the leading published deep-learning prospection work on this object class reads it from terrain relief, and that our contribution moves the same object from a sensed landform to a drawn map symbol — a change of representation, not of subject.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
