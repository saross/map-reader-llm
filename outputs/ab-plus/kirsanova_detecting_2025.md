# AB+ — Detecting Legend Items on Historical Maps Using GPT-4o with In-Context Learning

| field | value |
|---|---|
| **citekey** | `kirsanova_detecting_2025` |
| **full cite** | Kirsanova, Sofia, Duan, Weiwei & Chiang, YaoYi (2025) *Detecting Legend Items on Historical Maps Using GPT-4o with In-Context Learning.* Proceedings of the 4th ACM SIGSPATIAL International Workshop on Searching and Mining Large Collections of Geospatial Data. DOI: 10.1145/3764920.3770590 |
| **register** | Borrowed (GIS / document-layout AI) |
| **primary gap** | Strand 3 — historical-map extraction: legend parsing vs map-face symbol detection |
| **also touches** | Example-count/accuracy trade-off (token counts reported, no cost figures); Metric hygiene — class-relative vs aggregate reporting; Annotation budgets and training-free adaptation; Area-segmentation to point-symbol difficulty ladder; Architecture contrast — single deterministic pass vs consensus-plus-verifier |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Kirsanova, Chiang, and Duan present a four-page GeoSearch '25 workshop paper that bolts a large-multimodal-model stage onto the DIGMAPPER geological-map digitisation pipeline. The task is legend parsing. Given a scanned United States Geological Survey (USGS) sheet, a fine-tuned LayoutLMv3 (LARA) segments the map into content and legend regions; the legend is cropped out as an image; GPT-4o then receives that crop together with a structured JSON prompt carrying annotated legend-item and description bounding-box pairs, and returns coordinates for the item-description pairs on an unseen legend. Evaluation covers forty annotated maps from the DARPA-USGS dataset, scored by Intersection over Union (IoU) and an F1 computed at a fixed IoU threshold of 0.5.

For the citing paper this source is most valuable as a difficulty-ladder datum and least valuable as a headline benchmark. The model works only inside a pre-cropped legend: a bounded region in which each target symbol is paired with adjacent explanatory text, the segmentation stage having already discarded the rest of the sheet. Bounded is not tidy — the paper reports legend layouts varying in spacing, symbol shape, and column count, and names that layout sensitivity as its primary limitation. Conceding the heterogeneity sharpens the ladder rather than blunting it: a heterogeneous but text-anchored, already-cropped region is still an easier search than an open map face carrying one symbol family among dozens with no adjacent caption to key on, and the source's own failure analysis becomes our supporting evidence. Kirsanova et al. are a clean lower rung, not a competitor result.

Two cautions follow. First, on novelty: the paper's related work acknowledges existing work on symbol recognition on topographic maps, citing Huang et al. (2023, point symbol recognition via deep convolutional neural networks) and Miao et al. (2017, point symbols in scanned topographic maps) — hedged as "Some prior work has examined", inside a paragraph positioning that prior art as adjacent to, not overlapping with, the legend-item gap it claims. A separate sentence there — that most such techniques "focus on the map content itself" while the legend area is ignored — does a different job, its antecedent being road, intersection, and building-footprint extraction rather than point symbols. Unwelded, the two still constrain us jointly: any strand-3 claim that nobody detects point symbols on scanned topographic maps is contradicted by this source's own citations, and should be narrowed to the corpus, symbol family, and evaluation protocol at issue.

Second, on metrics. The abstract's headline pair is the legend-item column alone; the description column at the same setting scores higher on F1. There is no aggregate figure, confidence interval, or repeated run; the pipeline is deterministic at temperature zero, with no repeated sampling, consensus stage, or verifier described. The denominator moves as well as the class: Table 2 sets "the baseline of LayoutLMv3 alone for the whole task" against a GPT-4o treatment described as one step of a two-stage pipeline whose segmentation stage is never separately scored. Cited uncritically the 88% reads as system-level performance, which it is not.

## Positioning annotation (interpretive)

A historical-map extraction lineage anchor that sits one rung below the citing paper on the difficulty ladder: it applies a vision-language model to a pre-cropped, text-adjacent legend region rather than to the open map face, and so measures parsing within a bounded, caption-bearing region rather than open-field symbol search — bounded, though not tidy: the paper stresses that legend layouts vary in spacing, symbol shape, and column count, and names that heterogeneity as its primary failure mode. Its chief work for us is negative and calibrating — it names the point-symbol prior art that constrains a strand-3 novelty claim, and it models the class-relative headline-metric habit our own reporting is built to avoid.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "Some prior work has examined symbol recognition on topographic maps [10, 17], or linking text and features in historical map corpora [12, 13]."
- **Locator:** page_index 1 · p.2 · §2 Related Work
- **Paraphrase:** The authors explicitly acknowledge existing work on symbol recognition in topographic maps, citing two studies (their refs 10 and 17 are Huang et al. 2023 on point symbol recognition with deep convolutional networks, and Miao et al. 2017 on point symbols in scanned topographic maps).
- **Relevance:** §2 related work; §5 novelty claim · Strand 3 — historical-map extraction: legend parsing vs map-face symbol detection · **complicates**

### KP2
- **Quote (verbatim):** "most of these techniques focus on the map content itself, while the legend area, which defines the semantic meaning of symbols, is often ignored"
- **Locator:** page_index 1 · p.2 · §2 Related Work
- **Paraphrase:** The gap this paper claims runs in the opposite direction to a map-face novelty claim: it treats work on the map content as the established body and the legend area as the neglected one.
- **Relevance:** §2 related work · Strand 3 — historical-map extraction: legend parsing vs map-face symbol detection · **complicates**

### KP3
- **Quote (verbatim):** "After segmentation, we crop the legend area as an image file."
- **Locator:** page_index 1 · p.2 · §3.1 Legend Area Segmentation
- **Paraphrase:** The vision-language model never sees the whole sheet: a prior segmentation stage reduces the search space to the legend region before any detection is attempted.
- **Relevance:** §2 related work; §4 task-difficulty framing · Area-segmentation to point-symbol difficulty ladder · **supports**

### KP4
- **Quote (verbatim):** "achieving 88% F-1 and 85% IoU"
- **Locator:** page_index 0 · p.1 · Abstract
- **Paraphrase:** The abstract's headline pair reports the legend-item class only; at the same 15-example setting the description class scores 0.92 F1 and 0.84 IoU in Tables 1 and 2, and no aggregate across the two classes is given.
- **Relevance:** §4 metrics; §6 comparison to prior art · Metric hygiene — class-relative vs aggregate reporting · **complicates**

### KP5
- **Quote (verbatim):** "The inference pipeline was deterministic, with fixed prompts and temperature = 0."
- **Locator:** page_index 2 · p.3 · §4 Experiments — Implementation Details
- **Paraphrase:** Results come from a single greedy pass per query, with no repeated sampling, no consensus across passes, and no verification stage.
- **Relevance:** §3 architecture contrast; §6 comparison to prior art · Architecture contrast — single deterministic pass vs consensus-plus-verifier · **supports**

### KP6
- **Quote (verbatim):** "When 20 examples are included, performance slightly declines; overly long prompts introduce noise and distract the model from the core task."
- **Locator:** page_index 2 · p.3 · §4 Experiments — Effect of In-Context Examples
- **Paraphrase:** The finding here is the source's disagreement with itself, and it should be cited as that. Table 1 puts the optimum at 15 examples and shows a slight decline at 20 — 0.02 on legend-item IoU (0.85 to 0.83) and 0.02 on legend-item F1 (0.88 to 0.86), 0.02 on description IoU (0.84 to 0.82) and 0.04 on description F1 (0.92 to 0.88) — from a single deterministic run over 40 maps, with no confidence intervals, no repeated runs, and no significance test. The paper's own Discussion ("Performance improves with more examples in the prompt") and §5 Conclusion ("accuracy improves as more in-context examples are provided") describe the improvement as monotone and never restate the dip; the mechanism this quote offers for it — that overly long prompts introduce noise — is asserted, never tested, since no ablation separates prompt length from example count. Suggestive that in-context example count has an optimum, and a clean instance of a source holding two incompatible readings of its own table — not evidence that the optimum exists.
- **Relevance:** §4 cost/accuracy trade-space · Example-count/accuracy trade-off (token counts reported, no cost figures) · **complicates**

### KP7
- **Quote (verbatim):** "the primary limitation of the current approach is layout sensitivity: tightly packed or multi-column legends remain challenging, as the model struggles to distinguish between neighboring entries"
- **Locator:** page_index 3 · p.4 · §4 Experiments — failure analysis (Figure 3)
- **Paraphrase:** The dominant failure mode is dense spatial packing: closely spaced neighbouring entries get merged into oversized boxes or paired incorrectly, an analogue of the crowded-cluster failure our own detector faces.
- **Relevance:** §5 failure modes · Area-segmentation to point-symbol difficulty ladder · **extends**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "Very few studies explicitly address the challenge of extracting legend items."
- **Locator:** page_index 1 · p.2
- **Why:** A compact illustration of how narrowly a historical-map extraction gap claim has to be scoped to survive: the absence is asserted for legend items specifically, immediately before the same paragraph concedes prior work on topographic-map symbol recognition. Useful as the pivot sentence when we scope our own novelty claim.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
