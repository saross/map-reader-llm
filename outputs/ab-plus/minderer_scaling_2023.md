# AB+ — Scaling Open-Vocabulary Object Detection

| field | value |
|---|---|
| **citekey** | `minderer_scaling_2023` |
| **full cite** | Minderer, Matthias, Gritsenko, Alexey & Houlsby, Neil (2023) *Scaling Open-Vocabulary Object Detection.* DOI: 10.48550/arxiv.2306.09683 |
| **register** | Borrowed (computer vision / open-vocabulary detection) |
| **primary gap** | Open-vocabulary detection as the alternative to VLM prompting |
| **also touches** | Calibration transfer and operating-point selection; Annotation budgets and resource asymmetry; Metric hygiene; Domain shift: Web photographs to scanned map sheets |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Minderer, Gritsenko and Houlsby scale open-vocabulary detection by self-training rather than by architectural novelty. An existing detector (OWL-ViT CLIP L/14) pseudo-annotates the WebLI corpus of roughly 10B Web images using their alt-text; new OWLv2 detectors train on those pseudo-boxes, optionally followed by a brief fine-tune on human annotations. Two of the three decisions they isolate are resolved towards permissiveness: queries are every word N-gram up to length 10 drawn from an image's associated text, with no grammatical parsing, and filtering keeps everything above a moderate confidence threshold rather than the single best box per image. The third, training efficiency, is resolved the other way, towards aggressive throughput: half the image patches dropped by pixel variance, only top-ranked instances scored, images packed into mosaics. The reported figures need their stages kept straight: self-training alone on approximately 2B images takes an L/14 model to 34.9% zero-shot LVIS APval rare (Table 1 row 12); the headline 44.6% is that model after the optional third stage, fine-tuning on LVISbase (row 15), against 31.2% for the OWL-ViT L/14 that annotated the corpus; the 47.2% G/14 (row 16) is likewise post-fine-tuning, on a SigLIP rather than CLIP backbone. A human-curated label space of 2520 categories helps when the evaluation vocabulary is known in advance, but the authors state that this approach is not fully open-vocabulary.

For our study this is the reference point for the open-vocabulary-detection alternative — what a reviewer will ask why we did not simply use. Two features make the answer concrete. Provenance: the entire semantic supervision is Web alt-text attached to natural photographs, and no comparable supervision exists for Soviet-era topographic symbology, so the mechanism that makes OWLv2 open-vocabulary is precisely the one unavailable in our domain; the vocabulary is open towards Web-describable objects, not cartographic symbol families. Cost: the authors name compute and data as their principal limitation and note that cost likely increases faster than resources can realistically be grown in practice — the resource asymmetry that makes inference-time prompting of a general VLM attractive when the gold standard is a handful of annotated tiles, not billions of pseudo-labelled images.

Their fine-tuning analysis is the most transferable part. Fine-tuning on a target dataset buys in-distribution accuracy and spends out-of-distribution generalisation in proportion to its duration, with that generalisation operationalised as ODinW13 mean AP; weight-space ensembling improves the frontier without abolishing it. They add, as an unmeasured limitation rather than a result, that fine-tuned models may be poorly calibrated for out-of-distribution queries and may depend on the query's precise wording, immediately qualifying this as mitigable by weight ensembling. Carried with that hedge intact, it is an externally voiced worry about prompt sensitivity and threshold behaviour under shift, not evidence. Their metric commentary is usable as it stands: LVIS APrare measures only a narrow concept of open-vocabulary performance and conceals the generalisation loss the in-the-wild benchmark exposes — sharpened by the mechanism they give, that rare-class scores rise during fine-tuning because rare categories are semantically and visually close to frequent ones.

## Positioning annotation (interpretive)

The scaling-side statement of the open-vocabulary-detection alternative, and the strongest zero-shot LVIS APrare reported at the time of its publication — therefore the source against which our decision to prompt a general VLM has to be justified rather than assumed. It supplies the strongest version of the counterfactual, a detector whose vocabulary is open because it inherited Web-scale image-text supervision, while documenting why that route does not reach scanned topographic symbology: the supervision is alt-text on photographs, the cost is billions of pseudo-labelled images, and adaptation to a narrow target dataset demonstrably degrades out-of-distribution accuracy (operationalised as ODinW13 mean AP), while the authors flag — as a limitation, without measuring it, and as mitigable by weight ensembling — that fine-tuned models may be poorly calibrated for out-of-distribution queries. Its fine-tuning-versus-generalisation frontier and its scepticism about the headline open-vocabulary metric are borrowable for our transfer-tax and metric-discipline arguments, provided the calibration half travels as their hedged speculation rather than as a result.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "For out-of-distribution queries, predictions of fine-tuned models may be poorly calibrated and may depend on the precise wording of the query."
- **Locator:** page_index 8 · p.9 · §5 Limitations
- **Paraphrase:** The authors caution that once a fine-tuned open-vocabulary detector is queried outside its adaptation distribution, its scores may be badly calibrated and its outputs sensitive to how the query is phrased. The double hedge is theirs and nothing here is measured — the paper reports no calibration analysis anywhere — and their next sentence adds that these issues can be mitigated with weight ensembling, while more research is needed to understand open-vocabulary robustness.
- **Relevance:** § discussion — calibration transfer and prompt sensitivity (cited as an author-flagged limitation, not a measured result) · Calibration transfer and operating-point selection · **supports**

### KP2
- **Quote (verbatim):** "Fine-tuning on a target dataset improves performance on that dataset, but reduces the open-world generalization ability in proportion to the finetuning duration"
- **Locator:** page_index 8 · p.9 · Figure 5 caption (§4.6)
- **Paraphrase:** Adapting the model to a specific target dataset raises accuracy on that dataset while lowering open-world generalisation, and the loss scales with how much fine-tuning is done. Open-world generalisation is operationalised solely as ODinW13 mean AP, and the figure shows B/16 models (the L/14 replication is Figure A1).
- **Relevance:** § discussion — transfer taxes, carried versus oracle operating points · Calibration transfer and operating-point selection · **complicates**

### KP3
- **Quote (verbatim):** "LVIS mAPrare therefore only measures a narrow concept of open-vocabulary performance, and does not reveal the fact that fine-tuning significantly reduces generalization to broader distribution shifts."
- **Locator:** page_index 8 · p.9 · §4.6 Effect of Fine-Tuning Open-Vocabulary Performance
- **Paraphrase:** The field's headline open-vocabulary metric captures only a restricted sense of generalisation and hides the fact that fine-tuning substantially damages performance under wider distribution shift. The authors' stated mechanism is that rare-class scores improve during fine-tuning because rare categories are semantically and visually close to frequent ones, so the metric can rise for reasons unrelated to open-vocabulary capability.
- **Relevance:** § methods and results — metric selection and reporting · Metric hygiene · **supports**

### KP4
- **Quote (verbatim):** "The dataset consist of approximately 10B images and associated alt-text strings, which can be thought of as noisy image captions."
- **Locator:** page_index 2 · p.3 · §3.1 Generating Web-Scale Open-Vocabulary Object Annotations
- **Paraphrase:** The weak supervision behind the method is roughly ten billion Web images paired with noisy alt-text captions.
- **Relevance:** § prior art — why open-vocabulary detection does not transfer to cartographic symbology · Domain shift: Web photographs to scanned map sheets · **complicates**

### KP5
- **Quote (verbatim):** "The main limitation of our method is the amount of compute and data needed for self-training."
- **Locator:** page_index 8 · p.9 · §5 Limitations
- **Paraphrase:** The authors identify the compute and data requirements of self-training as the method's principal limitation.
- **Relevance:** § prior art and § discussion — cost of the detector route versus inference-time prompting · Annotation budgets and resource asymmetry · **supports**

### KP6
- **Quote (verbatim):** "a human-curated label space can help if the target label space is known, but that strong in-the-wild generalization is driven by the weakly supervised machine-generated label space"
- **Locator:** page_index 6 · p.7 · §4.3 Pseudo-Annotation Label Space
- **Paraphrase:** Curating the label list in advance improves results when the target categories are known, whereas generalisation to unfamiliar settings comes from the diverse machine-generated queries. The benefit of curation is modest for the larger model (LVIS APval rare 44.6 to 45.9) and negative on the in-the-wild benchmark (ODinW13 50.1 to 48.7).
- **Relevance:** § prior art — what 'open vocabulary' buys for a single known symbol family · Open-vocabulary detection as the alternative to VLM prompting · **extends**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "we argue that we should "let the data do the work" and therefore apply little processing and filtering"
- **Locator:** page_index 1 · p.2
- **Why:** A one-line statement of the open-vocabulary-detection lineage's governing assumption, and the cleanest possible foil for our setting: where there is no Web-scale corpus of annotated cartographic symbols, the data cannot do the work, and the burden falls back on prompting, consensus, and verification.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **7/7 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
