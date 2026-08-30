# AB+ — Unleashing the power of old maps: Extracting symbology from nineteenth century maps using convolutional neural networks to quantify modern land use on historic wetlands

| field | value |
|---|---|
| **citekey** | `ohara_unleashing_2024` |
| **full cite** | O'Hara, Rob et al. (2024) *Unleashing the power of old maps: Extracting symbology from nineteenth century maps using convolutional neural networks to quantify modern land use on historic wetlands.* Ecological Indicators. DOI: 10.1016/j.ecolind.2023.111363 |
| **register** | Borrowed (remote sensing / land-cover ecology) |
| **primary gap** | Metric hygiene — majority-class vs minority-class F1 / undeclared positive class |
| **also touches** | Cross-study comparability of reported F1; Area-segmentation vs point-symbol difficulty ladder; Ground-truth epistemics on historical maps; Annotation budgets for supervised map extraction |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

O'Hara and colleagues train a U-Net convolutional neural network to segment wetland symbology from the first-edition six-inch Ordnance Survey of Ireland maps (1829-1846) across 103 sheets of the ~3025 km2 River Barrow catchment, then intersect the result with the 2018 Irish National Land Cover map. Supervision came from 600 hand-made 512 × 512-pixel image/mask pairs from ten sheets outside the study area, split 90:10, masks hand-digitised in a geographic information system; training ran 50 epochs, and one global threshold (tensor value >= 0.40) binarised the output. One pre-processing choice was corpus-specific and necessary — dropping the blue and green channels, which carried the scan discolouration — while further tuning attempts (wetland-only patches, artificial linework, threshold adjustment) yielded no reported improvement.

It is chiefly valuable to us as a metric-hygiene exemplar, to be cited with care. The headline — abstract, Table 2, and Discussion — is an F1 of 98.2 %; Table 1 shows why that is unsafe as a wetland-detection score. Of 567 validation areas, 470 were dryland and 97 wetland; all ten Table 2 rows reproduce to printed precision when dryland, the majority class, is positive: F1 = 2×466/(2×466+13+4) = 98.2 %. On wetland-positive the seven asymmetric rows all fail, so the reading is forced, not merely consistent. The minority (wetland) class F1 is 90.8 %, appearing once, in §3.1, in the same sentence as a 98.2 % that is the upper bound of the accuracy confidence interval. Neither figure is an aggregate: macro-F1 is 94.5 % and micro-F1 (= accuracy) 97.0 %. The class-symmetric statistics sit near the minority-class reading: balanced accuracy 92.9 % and Kappa 89 %, both the authors' own (Table 2), plus a Matthews correlation coefficient (MCC) of ≈0.89 we recompute from Table 1, the paper reporting none. The paper is also internally inconsistent: §3.1 states correctly that "Both overall accuracy and F1 scores are susceptible to class imbalance" and leans on balanced accuracy, whereas §4 promotes F1 back into the imbalance-robust set. §4 then benchmarks 98.2 % against Ståhl and Weimann's 88.6 %, a wetland-class figure. On matched classes the margin is 90.8 % against 88.6 %, not 98.2 % against 88.6 % — but that is class-matched, not like-for-like: O'Hara's number is polygon-level under a ≥50 % coverage rule, Ståhl and Weimann's pixel-level over a 10-fold cross-validation. The ~10-point headline gap disappears once the class base is matched; no protocol-matched comparison exists.

Evaluation is area-relative, not instance-level — a polygon counted as wetland when at least half its area was predicted wetland, a rule adopted to suppress false negatives, with no direct analogue in point-symbol detection. The authors are candid about ground truth: they cannot assess the source maps' accuracy, and surveyors could round boundaries to the nearest field and skip small enclosed patches. Their remedy for context-starved patches — running segmentation more than once, aggregating by maximum value — is a rough antecedent of multi-pass aggregation, not of consensus: maximum-value aggregation is a union, hence recall-maximising, where consensus filters by agreement.

## Positioning annotation (interpretive)

Historical-map extraction lineage. This is the closest area-segmentation analogue in our related work — symbology extraction from a scanned national topographic series — and the source whose headline number most needs handling: the 98.2 % F1 a reader meets in the abstract is the majority (dryland) class F1, while the minority wetland-class F1 is 90.8 %. It is not the closest analogue to our detection task: berganzo-besga_curriculum_2023 (curriculum-learning mound detection from historical maps) and garciamolsosa_potential_2021 (deep-learning extraction of archaeological features from a map series) are nearer neighbours on both feature class and task. Cite O'Hara as an area-segmentation baseline and as the concrete case motivating our policy of reporting MCC alongside F1, not as evidence that symbol extraction from historical maps is solved at 98 %.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "The predicted mask had very high overall accuracy of 97 % (95 % C.I. 95.2 %, 98.2 %) and an F1 score of 90.8 % reflecting a strong ability to separate wetlands from non-wetlands"
- **Locator:** page_index 5 · p.6 · §3.1 Predicted mask and thematic accuracy
- **Paraphrase:** The Results section gives an unlabelled F1 of 90.8 % — arithmetically the wetland (minority) class F1 — alongside an overall accuracy of 97 % whose confidence interval has an upper bound of 98.2 %, numerically the same figure the abstract reports as the paper's F1. The string 90.8 occurs nowhere else in the article. §3.1 is not itself a clean class-relative report: the next two sentences mislabel in the opposite direction, attributing 99.15 % and 97.29 % to the wetland class where Table 1 gives 86.6 % and 95.5 %.
- **Relevance:** §2 related work · Metric hygiene — majority-class vs minority-class F1 / undeclared positive class · **supports**

### KP2
- **Quote (verbatim):** "N = 567 Reference (Original map) Dryland Wetland User Accuracy Predicted (wetland mask) Dryland 466 13 97.3 % Wetland 4 84 95.5 % Producer Accuracy 99.2 % 86.6 % Table 2 Accuracy metrics: positive, N: negative, TP: true positive, TN: true negative, FP: false positive, FN: false negative. Metric Derivation Value Accuracy (TP + TN)/(P + N) 97.0 % (95 % C.I. 95.2, 98.2 %) Balanced Accuracy (TP/(TP + FN) + TN/(FP + TN))/2 92.9 % F1 2TP/(2TP + FP + FN) 98.2 %"
- **Locator:** page_index 5 · p.6 · Tables 1 and 2
- **Paraphrase:** The confusion matrix records 470 dryland and 97 wetland reference areas out of 567, so dryland is the majority class by roughly five to one. The stated derivation, 2TP/(2TP + FP + FN), returns 98.2 % only when dryland is positive (2×466 / (2×466 + 13 + 4)); on the wetland class the same formula gives 168/185 = 90.8 %. The positive class is never declared. The quoted balanced-accuracy derivation is also an arithmetic mean of sensitivity and specificity, which yields the printed 92.9 %, whereas the harmonic mean §3.1 calls it would give 92.4 %.
- **Relevance:** §2 related work · Metric hygiene — majority-class vs minority-class F1 / undeclared positive class · **supports**

### KP3
- **Quote (verbatim):** "The segmentation approach yielded high overall accuracy (97.0 %) and balanced accuracy (92.9 %) with an F1 score of 98.2 % (Table 2). Overall accuracy is sensitive to class imbalance, which occurs here, however the balanced accuracy and F1 score suggest the model is highly accurate in this case."
- **Locator:** page_index 6 · p.7 · §4 Discussion
- **Paraphrase:** The Discussion restates 98.2 % as the paper's F1, acknowledges the class imbalance, and then offers the F1 score — with balanced accuracy — as reassurance against it, treating a single-class statistic as imbalance-robust. This contradicts §3.1, which states that overall accuracy and F1 are both susceptible to imbalance and leans only on balanced accuracy. The paper gets the diagnosis right in Results and wrong in the Discussion.
- **Relevance:** §5 results — metric reporting · Metric hygiene — imbalance-sensitive reporting · **supports**

### KP4
- **Quote (verbatim):** "Ståhl and Weimann (2022) reported an F1 score of 88.6 % (Precision: 87.1 %, Recall: 90.1 %) when extracting wetland extents using CNN for a region of Sweden."
- **Locator:** page_index 6 · p.7 · §4 Discussion
- **Paraphrase:** The paper benchmarks its 98.2 % against a prior wetland-extraction F1 of 88.6 %. That comparator is a wetland-class figure — Ståhl and Weimann estimate per-pixel wetland probability, and the precision and recall quoted are the positive class — so a dryland-class score is being set against a wetland-class one. On matched classes the margin is 90.8 % against 88.6 % rather than 98.2 % against 88.6 %; even that is class-matched but protocol-different, because O'Hara's figure is polygon-level over 567 areas under a ≥50 % coverage rule while Ståhl and Weimann's is pixel-level over a 10-fold cross-validation. No protocol-matched comparison exists, and the comparator is unstable at its own source (their Conclusions give 0.87 against their Results' 0.886).
- **Relevance:** §2 related work · Cross-study comparability of reported F1 · **complicates**

### KP5
- **Quote (verbatim):** "If the wetland coverage within the area was greater than or equal to 50 %, the area was classified as wetland."
- **Locator:** page_index 5 · p.6 · §2.4 Accuracy assessment
- **Paraphrase:** Validation units were areas rather than symbol instances, and an area was scored as wetland when at least half of it was predicted wetland. Performance is therefore measured as regional coverage agreement, not as instance-level matching of discrete symbols.
- **Relevance:** §2 related work · Area-segmentation vs point-symbol difficulty ladder · **complicates**

### KP6
- **Quote (verbatim):** "An uncertainty in our approach for quantifying wetland loss is our assumption that the historical maps were correct, both thematically and geometrically. We cannot make any assessment of the accuracy of the source material."
- **Locator:** page_index 7 · p.8 · §4 Discussion
- **Paraphrase:** The authors state plainly that their results rest on assuming the nineteenth-century maps are thematically and geometrically correct, and that they have no way of assessing the accuracy of the source material itself. The same paragraph names two directional biases: surveyors could set boundaries at the nearest field and could ignore patches of 2 ha or less enclosed within large inaccessible areas, which the authors say could over-represent wetlands in mountainous ground and extensive bog.
- **Relevance:** §3 corpus and ground truth · Ground-truth epistemics on historical maps · **supports**

### KP7
- **Quote (verbatim):** "A total of 600 patches (image/mask pairs) were created for model training and validation. These were created from ten map sheets randomly selected from the national archive of maps (outside the study area). Each map sheet was subset into patches (512 × 512 pixels) and visually inspected to ensure it contained both wetland and non-wetland areas. Binary wetland/non-wetland masks were created as manually digitised polygons converted to 1-bit raster images in a GIS"
- **Locator:** page_index 5 · p.6 · §2.3.2 Model training and parameter tuning
- **Paraphrase:** Supervision cost 600 image/mask pairs cut from ten map sheets outside the study area, visually inspected to confirm both classes were present (a presence check, not a balance check), each mask hand-digitised as polygons in a geographic information system; the source's next sentence records a 90:10 train/validation split, so roughly 540 training patches. This is a citable supervision floor for a supervised segmentation baseline — but the authors present it as a cheap one-off amortised across 103 sheets and extensible to a national series without further annotation, not as a burden, and the citing paper should say so.
- **Relevance:** §2 related work · Annotation budgets for supervised map extraction · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "Our analysis achieved a very high F1 score of 98.2% and a Kappa of 89%."
- **Locator:** page_index 0 · p.1
- **Why:** The citational surface: the sentence a reader lifts from the abstract, and the trap. The 98.2 % is the majority (dryland) class F1 under an undeclared positive-class assignment. Read it beside the class-symmetric statistics — balanced accuracy 92.9 % and Kappa 89 %, both the paper's own, and MCC ≈0.892, our recomputation — which cluster close to the minority-class wetland F1 of 90.8 % and nowhere near 98.2 %. Kappa and F1 are on different scales, so the point is where each statistic sits, not the difference between them. A crisp epigraph for the argument that headline F1 in the historical-map extraction literature must be read class-relative, and for our practice of reporting MCC alongside F1.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
