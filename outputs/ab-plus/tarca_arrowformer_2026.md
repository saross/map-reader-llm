# AB+ — ArrowFormer: detecting painted symbols using DEViT

| field | value |
|---|---|
| **citekey** | `tarca_arrowformer_2026` |
| **full cite** | Țarcă, Andrei-Ioan et al. (2026) *ArrowFormer: detecting painted symbols using DEViT.* Eighteenth International Conference on Machine Vision (ICMV 2025). DOI: 10.1117/12.3096237 |
| **register** | Borrowed (computer vision / intelligent transport) |
| **primary gap** | Closed-vocabulary supervised baseline for point-symbol detection |
| **also touches** | Metric hygiene and reporting comparability; Ground-truth completeness; Annotation budgets; Difficulty ladder and evaluation-set composition |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Tarca and colleagues present DEViT, a transformer-only detector for painted road symbols: DETR with its ResNet backbone and encoder replaced by a DINOv2-pretrained ViT-Small, trained on a private corpus of 30,000 driving images with 8,000 held out, then fine-tuned on CeyMo, a public benchmark of 2,887 images and 4,706 road-marking instances across 11 classes. The headline is a Macro F1 of 92.96%, against 90.18%, the best prior figure the authors are aware of.

For our study this is the closest analogue outside archaeology to the point-symbol rung of the difficulty ladder: a small closed vocabulary of stylised glyphs on a constrained surface. Three things matter more than the headline.

First, metric hygiene. The 92.96% is post-processed. Scored with CeyMo's own script on the best-mAP checkpoint the model reaches 91.66%; the authors then noticed duplicate boxes on single objects, applied non-maximum suppression at IoU 0.3, and the macro figure rose by 1.30 points. Only the higher number reaches the abstract, and the source never says what post-processing the 90.18% comparator used. Table 3 also reports an Overall F1 of 94.40% beside the Macro F1 of 92.96% on identical predictions - a 1.44-point gap between two aggregates of one prediction set, while the state-of-the-art column carries N/A for the overall figure (90.18% macro). The lesson does not transfer as macro-versus-micro over classes - with a single target class the two coincide - but as the choice of aggregation level across strata: pooled tiles against the mean of per-map or per-era scores. That is the distinction we have to name explicitly wherever we report a burial-mound F1.

Second, ground truth. Qualitative inspection turns up the model detecting small arrows the reference annotation does not contain; such detections would be scored as false positives. The paper offers no count - it is a single sentence beside a figure - but the condition is an analogue of our own gold standard's.

Third, closed vocabulary. Evaluated on CeyMo before any training there, the arrow-trained model absorbed the unseen Diamond class into Left and Right arrows, which the authors attribute - hedged as "mostly because" - to no such symbol appearing in the training images. An unseen symbol family was forced into the nearest trained class; that is the failure an open-vocabulary or prompt-driven detector is meant to avoid.

A quieter fourth lesson: the filtered run reports 65.1% validation mAP against 57.0% for the unfiltered run, but those are two separately trained models scored on two differently composed validation splits, so the gap cannot be assigned to evaluation-set composition alone; the source says only that the unfiltered result is lower because "the task is also more complex". The sharper caution is what happens next: transferred to CeyMo the ranking inverts, the unfiltered model scoring 50.6% mAP against the filtered model's 49.0% (Table 2). The easier evaluation set produced the better-looking number and the weaker model.

## Positioning annotation (interpretive)

A symbol-on-technical-drawing analogue, with a strong secondary claim as a methods/metrics exhibit. It is, for our purposes, the clearest non-archaeological demonstration of what a fully supervised, closed-vocabulary detector achieves on stylised point symbols once roughly 38,000 annotated images are available, and the detector is then fine-tuned on the target benchmark's own 2,089-image training split - the implicit baseline our prompt-driven pipeline is measured against, and the annotation budget it exists to avoid. Its second use is cautionary: the headline Macro F1 includes an NMS post-processing step absent from the benchmark-script figure, the paper reports two aggregates 1.44 points apart on one prediction set, and its zero-shot transfer illustrates the closed-vocabulary failure mode that motivates an open-vocabulary approach.

## Key points (salience-ranked to the citing paper)

### KP1
- **Quote (verbatim):** "we applied a NMS post-processing with IoU threshold of 0.3 on the outputs, obtaining the metrics detailed in 3, with a Macro F1 score of 92.96%"
- **Locator:** page_index 6 · p.7 · §4.6 Discussion
- **Paraphrase:** The 92.96% headline is a post-processed figure: having seen the model emit duplicate boxes for one object, the authors applied non-maximum suppression at an IoU threshold of 0.3 and report the resulting metrics in Table 3.
- **Relevance:** §5 discussion - reporting the full operating point · Metric hygiene and reporting comparability · **supports**

### KP2
- **Quote (verbatim):** "obtained a Macro F1 score of 91.66%, outperforming the current SOTA, which had 90.18% [25]."
- **Locator:** page_index 6 · p.7 · §4.5 Numerical Experiments on the CeyMo dataset
- **Paraphrase:** Scored with the benchmark's own evaluation script and without the later post-processing, the model's Macro F1 is 91.66%, and that is the figure which clears the 90.18% prior state of the art.
- **Relevance:** §5 discussion - reporting the full operating point · Metric hygiene and reporting comparability · **complicates**

### KP3
- **Quote (verbatim):** "There are cases where our model detects small arrows that are not annotated."
- **Locator:** page_index 6 · p.7 · §4.6 Discussion
- **Paraphrase:** Inspection of the qualitative results shows the detector finding small arrows that the reference annotation omits; such detections would be scored as false positives, though the paper gives no count.
- **Relevance:** §6 limitations - ground-truth epistemics · Ground-truth completeness · **supports**

### KP4
- **Quote (verbatim):** "we noticed some symbols (the Diamond class) that are misclassified by our models into Left or Right Arrows, mostly because in the training data there were no such symbols present in the images at all"
- **Locator:** page_index 5 · p.6 · §4.5 - Arrows on CeyMo Dataset
- **Paraphrase:** Applied to a new dataset, the arrow-trained model pushed an unseen symbol class (Diamond) into its Left and Right arrow classes, which the authors attribute - hedged as "mostly because" - to that symbol being absent from the training images.
- **Relevance:** §2 related work - why open-vocabulary or prompt-driven detection · Closed-vocabulary failure modes · **supports**

### KP5
- **Quote (verbatim):** "we will filter the bounding boxes smaller than 14px × 14px on both training and validation split"
- **Locator:** page_index 2 · p.3 · §4.1 Datasets - Private Dataset with arrows
- **Paraphrase:** Bounding boxes below 14 x 14 px are removed from the validation split as well as the training split, so the first round of reported metrics is computed on an evaluation set with the smallest and most faded instances taken out.
- **Relevance:** §3 methods - evaluation protocol and tile scale · Difficulty ladder and evaluation-set composition · **complicates**

### KP6
- **Quote (verbatim):** "Overall F1-Score 94.40% 90.62% N/A Macro F1-Score 92.96% 88.33% 90.18%"
- **Locator:** page_index 5 · p.6 · Table 3 - per-class and aggregate F1 on CeyMo
- **Paraphrase:** Two aggregates of the same prediction set are reported side by side - an Overall F1 of 94.40% and a Macro F1 of 92.96% - while the state-of-the-art column carries N/A for the overall figure (90.18% macro), so the like-for-like comparison exists in one aggregate alone.
- **Relevance:** §5 discussion - aggregation level across strata · Metric hygiene and reporting comparability · **supports**

### KP7
- **Quote (verbatim):** "The training data consists of 30.000 images, while validation is computed on 8.000 images."
- **Locator:** page_index 2 · p.3 · §4.1 Datasets - Private Dataset with arrows
- **Paraphrase:** The supervised pipeline is built on 30,000 annotated training images with a further 8,000 for validation.
- **Relevance:** §2 related work - supervised baselines and their cost · Annotation budgets · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "reaching a Macro F1-Score of 92.96%, outperforming the currently best approach that achieved 90.18%"
- **Locator:** page_index 0 · p.1
- **Why:** The abstract's headline pairing, quotable as the exhibit for a post-processed figure carried into a comparison without saying so: the body reveals that 92.96% is post-NMS and that the script-computed figure is 91.66%, so the margin over prior art is 2.78 points on the post-NMS figure and 1.48 points on the script-computed one. Which of the two is the like-for-like comparison cannot be settled from this paper, because it never says what post-processing the 90.18% comparator used - and that silence is the exhibit.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: model `claude-opus-5` requested (proposer + verifier); run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1721-gfbbfb0a4e-dirty`.

## Independent verifier (advisory — flags only)

- **KP1: SUPPORTED** — NMS at IoU 0.3 -> 92.96%. Quote and section (§4.6, p.6) are correct, and the paraphrase's causal ordering matches the source: the authors observed duplicate boxes for one object first ('we observed that our model sometimes predicted two bounding boxes for the same object. So we applied a NMS post-processing...'). Worth noting for the drafter, not against them: DETR is characterised in §2 of this same paper as detecting 'without anchor boxes or NMS', so the post-processing is a departure from the architecture's advertised behaviour - which strengthens the metric-hygiene point rather than weakening it.
- **KP2: SUPPORTED** — 91.66% via the CeyMo script on the highest-mAP checkpoint, against 90.18% prior art. Verbatim at the head of p.6, correctly attributed to the tail of §4.5. The paraphrase's 'without the later post-processing' is right: the NMS step is introduced afterwards in §4.6. One caveat the entry should not lose - the source nowhere says the 92.96% was computed by a *different* means; the difference is NMS applied to the outputs, not a different scorer. Phrasings that oppose 'the script-computed figure' to 'the post-processed figure' imply a scorer swap the paper does not report.
- **KP3: SUPPORTED** — 'There are cases where our model detects small arrows that are not annotated' is verbatim (§4.6, p.6). The paraphrase's consequence - that these are scored as false positives - is a sound inference (Figure 3 is captioned as predictions on the testing images) but is not stated by the source, and the source quantifies nothing: 'cases', observed in one qualitative figure. Recommend the conditional ('would be scored as') and an explicit acknowledgement that no count is given. See edit 3 for the summary sentence, which is firmer than this paraphrase and adds an equivalence claim.
- **KP4: SUPPORTED** — Diamond-into-arrows misclassification is verbatim (§4.5, p.5), and the paraphrase correctly (a) attributes the causal explanation to the authors rather than asserting it, and (b) states that no CeyMo training preceded the comparison, which §4.5 confirms ('For this comparison we did not train the models at all on CeyMo's images'). The summary's rendering drops the authors' 'mostly' hedge and generalises one observed class into a law; see edit 4. Also worth carrying: once Diamond entered the fine-tuning vocabulary the model scored 96.34% on it (Table 3), so the failure is specifically a property of the zero-shot condition, which the entry does say.
- **KP5: SUPPORTED** — The quote is verbatim (§4.1, p.2) and the paraphrase is accurate and appropriately narrow - the filter is applied to the validation split as well as the training split, so the first reported metrics are computed on a thinned evaluation set. The overreach attached to this quote lives in the summary, not here: see edit 1.
- **KP6: SUPPORTED** — Table 3 aggregates check out: Overall 94.40 / Macro 92.96 for DEViT, 90.62 / 88.33 for Mask R-CNN, N/A / 90.18 for Swin-APT; the 1.44-point gap is arithmetically right. One softening: the source shows 'N/A' in the Swin-APT overall cell, which is evidence about this table, not about what the Swin-APT paper published. 'Supplies only a macro figure' should become 'is entered as N/A for the overall figure' (edit 5).
- **KP7: SUPPORTED** — 30,000 training / 8,000 validation images is verbatim (§4.1, p.2). The paraphrase is exact. The aggregation into '~38,000' in the positioning is legitimate (the validation images are annotated too) but incomplete - see edit 7.
- **KP8: OVERREACH** — POSITIONING. Three sub-claims run ahead of the source. (i) 'once roughly 38,000 annotated images are available' omits that the 92.96% additionally required fine-tuning on CeyMo's own 2,089-image training split (§4.5, p.5) - the annotation budget for the headline is the private corpus plus in-domain target data, which is the stronger version of the point anyway. (ii) 'exposes exactly the closed-vocabulary failure mode' overstates a hedged, qualitative aside about one class ('mostly because'), offered by the authors to explain an anomaly in Left-class mAP, not as a finding about vocabulary closure. (iii) 'the best non-archaeological demonstration' is a curatorial judgement, not a sourced claim - defensible as positioning, but the entry should not lean on it as though the paper established it. The core positioning - closed-vocabulary supervised baseline plus metrics exhibit - is well founded.
- **KP9: OVERREACH** — FRAMING HOOK. The abstract quote is verbatim, and the observation that the abstract carries the post-NMS number without saying so is fair and well evidenced. But 'the margin over prior art shrinks from 2.78 to 1.48 points once the comparison is put on one footing' asserts that the no-NMS figure is the like-for-like one. The source gives no basis for that: it never characterises Swin-APT's post-processing - a point the entry's own summary concedes two paragraphs earlier ('a prior-art figure whose post-processing is not characterised'). If anything the inference cuts the other way, since NMS is standard for the Mask R-CNN and Swin comparators (§2, p.1, describes NMS as 'standard' outside DETR), so the post-NMS number may be the more comparable one. The arithmetic is right; the framing is not. See edit 2.
- **requested edits** (applied to the entry by the edit pass before render; kept quotes byte-identical):
  - EDIT 1 (most consequential; summary, final paragraph). Replace: 'A quieter fourth lesson: restricting boxes to those larger than 14 x 14 px lifts validation mAP from 57.0% to 65.1%. The metric moves with the evaluation set's composition, not the model's competence - a caution to carry into any tile-size or instance-size comparison of our own.' With: 'A quieter fourth lesson: the filtered run reports 65.1% validation mAP against 57.0% for the unfiltered run, but those are two separately trained models scored on two differently composed validation splits, so the gap cannot be assigned to evaluation-set composition alone; the source says only that the unfiltered result is lower because "the task is also more complex". The sharper caution is what happens next: transferred to CeyMo the ranking inverts, the unfiltered model scoring 50.6% mAP against the filtered model's 49.0% (Table 2). The easier evaluation set produced the better-looking number and the weaker model.' RATIONALE: §4.4 (p.4) trains the filtered model on filtered annotations and the unfiltered model on all annotations, from the same Epoch-29 checkpoint but to different best epochs (73 vs 85). Training set, evaluation set and model all differ, so 'the metric moves with the evaluation set's composition, not the model's competence' is an unsupported causal attribution to one of three confounded factors.
  - EDIT 2 (framing hook note). Replace: 'so the margin over prior art shrinks from 2.78 to 1.48 points once the comparison is put on one footing.' With: 'so the margin over prior art is 2.78 points on the post-NMS figure and 1.48 points on the script-computed one. Which of the two is the like-for-like comparison cannot be settled from this paper, because it never says what post-processing the 90.18% comparator used - and that silence is the exhibit.' RATIONALE: nothing in the source licenses 'one footing'; §2 (p.1) treats NMS as standard practice for the non-DETR comparators, so the pre-NMS number is not self-evidently the fairer one.
  - EDIT 3 (summary, second lesson). Replace: 'Qualitative inspection turns up the model detecting small arrows the reference annotation does not contain, so correct detections are being scored as false positives - the same epistemic condition our gold standard is in.' With: 'Qualitative inspection turns up the model detecting small arrows the reference annotation does not contain; such detections would be scored as false positives. The paper offers no count - it is a single sentence beside a figure - but the condition is an analogue of our own gold standard's.' RATIONALE: the false-positive consequence is inferred rather than stated, the observation is unquantified, and 'the same epistemic condition' asserts an equivalence with our gold standard that the source cannot underwrite.
  - EDIT 4 (summary, third lesson). Replace: 'the arrow-trained model absorbed the unseen Diamond class into Left and Right arrows because no such symbol existed in its training images. A symbol family outside the trained vocabulary is forced into the nearest trained class' With: 'the arrow-trained model absorbed the unseen Diamond class into Left and Right arrows, which the authors attribute - hedged as "mostly because" - to no such symbol appearing in the training images. An unseen symbol family was forced into the nearest trained class' RATIONALE: (a) hedged finding reported as firm; (b) one observed class generalised into a stated rule.
  - EDIT 5 (summary and key point 5 paraphrase). Replace 'the state-of-the-art comparator publishes only the macro figure' / 'the state-of-the-art comparator supplies only a macro figure (90.18%)' with 'the state-of-the-art column carries N/A for the overall figure (90.18% macro)'. RATIONALE: Table 3 evidences an empty cell in this paper's table, not the comparator's publishing practice.
  - EDIT 6 (summary, first lesson, final sentence). Replace: 'This is the class-relative versus aggregate distinction we have to state explicitly whenever we report a single-class burial-mound F1.' With: 'The lesson does not transfer as macro-versus-micro over classes - with a single target class the two coincide - but as the choice of aggregation level across strata: pooled tiles against the mean of per-map or per-era scores. That is the distinction we have to name explicitly wherever we report a burial-mound F1.' RATIONALE: salience drift. The 1.44-point gap in the source arises from averaging over eleven classes; a single-class F1 has no macro/overall distinction, so as written the bridge to our study does not hold. The corrected version keeps the real transferable lesson.
  - EDIT 7 (positioning). Replace: 'once roughly 38,000 annotated images are available' With: 'once roughly 38,000 annotated images are available, and the detector is then fine-tuned on the target benchmark's own 2,089-image training split'. RATIONALE: §4.5 (p.5) - the headline 92.96% is post-fine-tuning on CeyMo, not a transfer result from the private corpus alone.
  - EDIT 8 (positioning). Replace 'its zero-shot transfer exposes exactly the closed-vocabulary failure mode that motivates an open-vocabulary approach' with 'its zero-shot transfer illustrates the closed-vocabulary failure mode that motivates an open-vocabulary approach'. RATIONALE: 'exposes exactly' inflates a hedged single-class observation into a demonstration.
  - EDIT 9 (low priority; summary, opening paragraph). 'against 90.18% for the Swin-APT state of the art' - the source hedges this ('For our knowledge, the best performance is obtained with a Swin-APT', §2, p.1). Consider 'the best prior figure the authors are aware of'. Not blocking; the paper does treat 90.18% as SOTA throughout.
- **overall:** PASS-WITH-EDITS
