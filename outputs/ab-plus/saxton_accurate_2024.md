# AB+ — Accurate Feature Extraction from Historical Geologic Maps Using Open-Set Segmentation and Detection

| field | value |
|---|---|
| **citekey** | `saxton_accurate_2024` |
| **full cite** | Saxton, Aaron et al. (2024) *Accurate Feature Extraction from Historical Geologic Maps Using Open-Set Segmentation and Detection.* Geosciences. DOI: 10.3390/geosciences14110305 |
| **register** | Borrowed (geoscience / historical-map digitisation) |
| **primary gap** | Historical-map extraction lineage — legend-prompted open-set detection |
| **also touches** | Generalisation gap between selection and deployment splits; Metric hygiene and reporting comparability; Difficulty ladder: area segmentation to point symbols; Rare-class / long-tail symbol failure; Annotation budgets and human-in-the-loop |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Saxton and colleagues extract polygon and point features from scanned USGS historical geologic maps by turning the legend into the prompt: a legend crop is concatenated channel-wise with the map patch to make a six-channel input, fed to a U-Net for areas and to a YOLOv8 variant with a binary head for point symbols. The corpus is the DARPA/USGS AI4CMA release (169 training maps, 82 validation, 32 test); the motivating problem is inconsistent symbology, one feature type drawn differently across sheets and eras. That is the closest problem-shape ancestor of our pipeline in the historical-map lineage, and the difficulty a burial-mound symbol poses across Soviet topographic series.

The abstract's headline is a median F1 of 0.91 for polygon segmentation and 0.73 for point detection, and both carry conditions. The 0.73 is qualified in the abstract's own sentence — 'when such features had abundant annotated data' — and the only point-detection figure it rounds to is Table 5's validation, common-legend cell, 72.59; the paper never names the split, so this is an inference from rounding. On the test split the same model scores 48.10 on common legends and zero F1, precision, and recall on rare ones. Our earlier reading carried 0.73 as this paper's point-detection result; the deployment counterpart is 48.10. That is a selection-split-to-deployment-split generalisation gap, which rhymes with our carried-versus-oracle diagnosis without being the same mechanism — the authors attribute the drop to unseen symbols, and the paper reports no threshold-transfer analysis for point detection.

Four metric-hygiene traps sit beneath the numbers. The polygon F1 is a median, legend-wise score over weighted pixels — those the colour-matching baseline already recovers count 0.3, the rest 0.7 — so 91.52 is a bespoke competition metric, and 'surpassing the state-of-the-art method by 13.12%' is a relative improvement over LOAM's 80.90, an absolute margin of 10.62 points. Table 4's columns do not compose either: LOAM's 89.10 precision and 91.50 recall imply an F1 of 90.28 against a reported 80.90, because each column is an independent legend-wise median, so cross-study work must read the F1 column rather than recompute it. The 0.91 is a test figure while the 0.73 is a validation one, so the pair does not come from one evaluation; that attribution holds under either rounding convention, since 91.52 truncates to 0.91 (it rounds to 0.92), the nearest test figure rounding to 0.91 is U-Net+P's 90.90, and every validation figure in Table 4 is 83.71 or lower. Point matches, finally, use a distance cutoff of 0.01 of the map diagonal, so across the stated 3000 x 3000 to 14,000 x 14,000 resolution range the tolerance runs from roughly 42 to 198 pixels (our arithmetic).

The paper's own remedy for the rare-symbol collapse — less data-hungry models, class-agnostic foundation-model priors, and a human-in-the-loop system the authors report as under development, which they say will cut annotation from a week to a few hours — names the family our approach belongs to, the strongest reason to cite it as lineage rather than benchmark.

## Positioning annotation (interpretive)

The historical-map extraction lineage's closest problem-shape ancestor to our pipeline: an open-set, legend-prompted detector built for the same task shape — one symbol family at a time, on scanned sheets whose symbology drifts between them — and the reference point for what exemplar-conditioned supervised methods reach on point symbols before a vision-language model enters. Its principal use to us is corrective rather than comparative: the 0.73 can only be Table 5's validation, common-legend cell (72.59) — it is the sole point-detection F1 in the paper that rounds to it, and the paper never states the split, so this is an inference — while the same model scores 48.10 on common symbols and 0 on rare ones on the test split, which makes this an attested selection-split-to-deployment-split generalisation gap rather than a bar we should be clearing. Its metrics also need restating before any cross-study comparison, since the polygon F1 is a weighted-pixel competition score and the point matcher uses a scale-dependent distance cutoff, so neither is a like-for-like target.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "our approach achieved a median F1 score of 0.91 for polygon feature segmentation and 0.73 for point feature detection when such features had abundant annotated data, outperforming current benchmarks"
- **Locator:** page_index 0 · p.1 · Abstract
- **Paraphrase:** The abstract's headline pair is a median F1 of 0.91 for polygon segmentation and 0.73 for point detection, with the point figure explicitly conditioned on the feature having abundant annotated data — the qualifier is in the headline sentence itself, not buried in the results. Note also that the abstract calls both figures 'median F1', yet Table 5, the only source of the point number, states no aggregation at all, so 'median' is unsubstantiated for the 0.73.
- **Relevance:** §2 related work — historical-map feature extraction · Historical-map extraction lineage — attested headline figures · **supports**

### KP2
- **Quote (verbatim):** "Methods Common Legends Rare Legends F1 Precision Recall F1 Precision Recall Prompted YOLO (Validation) 72.59 82.12 70.59 39.21 32.58 69.46 Prompted YOLO (Testing) 48.10 53.84 80.16 0 0 0"
- **Locator:** page_index 12 · p.13 · Table 5 — point detection, common versus rare legend symbols
- **Paraphrase:** Table 5 splits point detection four ways. On validation the model reaches 72.59 F1 on common legend symbols and 39.21 on rare ones; on the test split it falls to 48.10 on common symbols and to zero on rare ones. The abstract's 0.73 corresponds, by rounding, to the validation common-legend cell, though the paper does not state the split. The common-legend drop is precision-driven — precision falls 82.12 to 53.84 while recall rises 70.59 to 80.16 — whereas the rare-legend cell is a total failure (0 F1, 0 precision, 0 recall) that no threshold choice could repair.
- **Relevance:** §5 discussion — selection-split to deployment-split degradation · Generalisation gap between selection and deployment splits · **complicates**

### KP3
- **Quote (verbatim):** "The performance discrepancy between the validation and testing datasets in Table 5 arose because the testing dataset includes a significantly higher number of unseen point symbols. While the model performed relatively well with sufficient training data, it struggled to generalize to these unfamiliar symbols."
- **Locator:** page_index 12 · p.13 · §4.3 Model Performance for Point Detection
- **Paraphrase:** The authors trace the validation-to-test drop to the test split containing far more point symbols the model had not seen in training: the method works where training data were sufficient and does not generalise to unfamiliar symbols, despite being framed as open-set.
- **Relevance:** §2 related work — why exemplar prompting alone does not deliver open-set behaviour · Rare-class / long-tail symbol failure · **supports**

### KP4
- **Quote (verbatim):** "Pixels correctly identified by the colormatching baseline model were labeled as "easy" and the rest as "hard". In this study, "hard" pixels were weighted at 0.7, while "easy" pixels carried a weight of 0.3."
- **Locator:** page_index 7 · p.8 · §3.6 Evaluation Metrics
- **Paraphrase:** The polygon score is computed over weighted pixels: those a colour-matching baseline already recovers are down-weighted to 0.3 and the remainder up-weighted to 0.7, so the reported F1 is a bespoke competition metric rather than a standard one. Table 4's columns are independent legend-wise medians and do not compose — LOAM's 89.10 precision and 91.50 recall imply an F1 of 90.28 against its reported 80.90 — so any cross-study comparison must read the F1 column directly rather than recompute it.
- **Relevance:** §3 methods — evaluation protocol and metric comparability · Metric hygiene and reporting comparability · **complicates**

### KP5
- **Quote (verbatim):** "The distances were normalized by the diagonal length of the map, with a value of 0 indicating perfectly overlapping pixels and a value of 1 representing pixels at opposite corners of the map. In this study, we used a cutoff distance of 0.01 to determine valid pairs"
- **Locator:** page_index 7 · p.8 · §3.6 Evaluation Metrics
- **Paraphrase:** Point detections are matched to ground truth by nearest-neighbour distance normalised against the map diagonal, with anything closer than 0.01 counted a valid pair — a match tolerance that scales with the sheet rather than with the symbol.
- **Relevance:** §3 methods — point-matching criterion · Metric hygiene and reporting comparability · **complicates**

### KP6
- **Quote (verbatim):** "The threshold for classifying symbols as common or rare was set at 1000 occurrences in the training dataset. For comparison, the baseline benchmark model, which utilized template matching [34], achieved an F1 score of 0.35 for all point symbols."
- **Locator:** page_index 12 · p.13 · §4.3 Model Performance for Point Detection
- **Paraphrase:** Symbols are called common above 1000 training occurrences and rare below it, and the challenge's template-matching benchmark reaches 0.35 F1 — scored over all point symbols pooled, so not like-for-like with the common/rare-split figures. Flag for citation: the paper cites '[34]' for that baseline, but [34] in its own reference list is Ronneberger et al.'s U-Net, so the benchmark method is not identifiable from the paper.
- **Relevance:** §2 related work — the template-matching benchmark on the same dataset · Difficulty ladder: area segmentation to point symbols · **supports**

### KP7
- **Quote (verbatim):** "one strategy is to explore alternative models that require less data, such as non-learning-based methods like template matching [38] and class-agnostic learning using foundation models as a prior [39,40]"
- **Locator:** page_index 13 · p.14 · §4.3 Model Performance for Point Detection — rare symbols
- **Paraphrase:** Facing the rare-symbol collapse, the authors nominate less data-hungry alternatives, specifically class-agnostic learning that uses a foundation model as a prior — the lineage naming, from inside, the family our move belongs to; their citations and the conclusion's SAM are vision-only detection foundation models, not vision-language models.
- **Relevance:** §2 related work — motivation for a vision-language-model approach · Historical-map extraction lineage — where the lineage points next · **extends**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "Notably, no studies have yet automated the extraction of all symbols from scanned geologic maps."
- **Locator:** page_index 3 · p.4
- **Why:** A one-line statement of the lineage's standing condition as of late 2024: extraction on scanned geologic maps is still done one symbol family at a time. It frames our own scope honestly — a burial-mound symbol is one family among dozens on a Soviet sheet — and it sets up the claim that the constraint is an annotation and vocabulary constraint rather than an imaging one.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
