# AB+ — Leveraging LLMs and attention-mechanism for automatic annotation of historical maps

| field | value |
|---|---|
| **citekey** | `yuan_leveraging_2025` |
| **full cite** | Yuan, Yunshuang & Sester, Monika (2025) *Leveraging LLMs and attention-mechanism for automatic annotation of historical maps.* DOI: 10.48550/arXiv.2504.11050 |
| **register** | Borrowed (cartography/GIScience — arXiv:2504.11050 [cs.CV]; conference-style short paper with BoK concepts) |
| **primary gap** | Historical-map extraction lineage — the LLM-as-labeller rung |
| **also touches** | Annotation budgets; Ground-truth epistemics; Difficulty ladder (area segmentation → point symbols); Calibration transfer / carried vs oracle operating points; Metric hygiene (protocol-dependent IoU/precision/recall) |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Yuan and Sester propose a knowledge-distillation pipeline in which a large language model acts as a cheap, coarse labeller for scanned topographic sheets and an attention mechanism does the localising. The LLM is shown a prompt image carrying exemplar symbols for two classes, Wood and Settlement, alongside a 384×384 pixel crop, and asked two independent yes/no questions with reasons; fig. 2's worked example is answered by ChatGPT-4o, but the paper never names the model used for the full labelling run. Those image-level binary labels — never coordinates — train a small convolutional encoder with random token dropping and a cross-attention head; the trained attention weights are then read out as a spatial map by an iterative take-the-maximum-then-drop-that-token procedure, giving 64×64 pixel annotations (36 tokens per crop). The data are four Lower Saxony mapping agency (LGLN) sheets, 1973–1975: 3821, 3822 and 3921, described as covering the Hameln area, for training, 3922 for evaluation, one binary model per class.

Three things make this both the closest lineage neighbour to our study and its clearest contrast. First, the division of labour: the LLM is a coarse presence detector and nothing more, with localisation delegated to a distilled model — precisely the step our detector asks the VLM to perform directly, on point symbols, at a far smaller scale. Second, both classes are area classes, and the paper's own hedged, unquantified explanation for Wood outscoring Settlement is coverage; the extension of that remark into our area-to-point difficulty ladder is ours, not theirs. Third, the paper reports the number this lineage usually leaves out: the LLM-generated labels were about 70% accurate, on two independent yes/no presence questions per crop, at 384×384 pixels, with exemplar symbols in the prompt image — an author-reported approximation in the conclusion, with no denominator, breakdown, or stated measurement basis.

Metric handling needs care. The attention maps are scored against pixel-wise ground truth under two resolution-harmonisation protocols, published side by side and measuring different capabilities rather than the same one twice, and the same class moves a long way between them: Settlement IoU is 0.720 down-sampled (Table 1) against 0.474 up-sampled (Table 2), a decline the authors attribute to coarse predictions failing to align with fine-grained ground truth. The abstract's precision figures, and Settlement's IoU, are Table 1's down-sampled values, while the unqualified "more than 90%" recall claim is true of both classes only under the up-sampled protocol — down-sampled Settlement recall is 0.880. Its Wood IoU, 84.2%, matches neither table (0.824 and 0.781), so it appears to be a transposition, though §3.2's swept Wood IoU "reaching 0.85" is a second possible origin. The threshold is a free parameter: both tables report an untuned σ = 0.5, while the quoted peak precisions (0.93 and 0.84, Wood only) are read off the evaluation sweep at σ = 0.9 — an oracle operating point in our vocabulary, with no carried counterpart. The "without fine-grained manual labels" claim is literally exact but easy to over-read: the coarse labels were human-corrected in a click-to-flip interface.

## Positioning annotation (interpretive)

The LLM-as-labeller rung of the historical-map extraction lineage, and the lineage's sharpest architectural contrast to our design: a general-purpose LLM sits upstream as a coarse yes/no presence detector on 384×384 crops and is never asked to localise, that job being delegated to a distilled attention model whose weight maps become the fine-grained annotation. Cite it for three things — the roughly 70% accuracy of LLM presence labels prompted with exemplar symbols on scanned topographic sheets, a hedged, unquantified coverage explanation for the Wood–Settlement gap that parallels our area-to-point difficulty ladder (the authors' own reading; the extension to point symbols as the limiting case of low coverage is ours), and the annotation-budget claim that fine-grained labels can be manufactured from coarse ones. It is a supportive comparator that must be handled with the protocol attached: the paper scores one set of attention maps under two resolution-harmonisation schemes and explains the gap between them, the abstract's precision figures track Table 1's down-sampled values while its blanket recall claim is class-dependent under that protocol, and the threshold that produces the quoted peaks (σ = 0.9) is not the untuned midpoint that produces the tables (σ = 0.5).

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "LLMs are employed to generate coarse classification labels for low-resolution historical image patches, while attention mechanisms are utilized to refine these labels to higher resolutions."
- **Locator:** page_index 0 · p.1 · Abstract
- **Paraphrase:** The architecture splits the task in two: the LLM supplies only coarse, image-level class labels for large low-resolution patches, and a separately trained attention mechanism does the spatial refinement to finer resolution. The LLM is never asked where anything is — only whether a class is present — which is the exact capability our detector puts on the VLM itself, and at point-symbol rather than land-cover scale.
- **Relevance:** §2 related work; §5 discussion — what we ask the VLM to do that this lineage does not · Historical-map extraction lineage — where the LLM sits in the pipeline · **complicates**

### KP2
- **Quote (verbatim):** "In the current approach, the LLM-generated labels had an accuracy of approx. 70%. While a quick correction of those labels is possible due to the large patch-sizes, future work will also try to improve the labelling results."
- **Locator:** page_index 5 · p.6 · §4 Conclusion and future work
- **Paraphrase:** Reported only in the conclusion, and absent from the abstract: the raw LLM labels were right about 70% of the time. That is the performance of a general-purpose model (ChatGPT-4o in the worked example of fig. 2; the paper does not name the model used for the full labelling run) on two independent yes/no presence questions per crop (Wood, Settlement), at 384×384 pixels, with exemplar symbols supplied in a prompt image — and on land-cover classes far more spatially extensive than a point symbol. It is the most directly citable figure in the source for what an off-the-shelf model achieves on scanned topographic sheets without task-specific training. The paper gives no denominator, no per-class breakdown, and no measurement procedure for the figure — it is a single author-reported approximation in the conclusion, and should be cited as such.
- **Relevance:** §2 related work; §5 discussion — the baseline a purpose-built detector has to beat · Historical-map extraction lineage — LLM presence-label accuracy on scanned sheets · **supports**

### KP3
- **Quote (verbatim):** "The wood class outperforms settlement, likely due to its higher spatial coverage, which increases the likelihood of patches being classified as foreground."
- **Locator:** page_index 5 · p.6 · §3.2 Quantitative result
- **Paraphrase:** The authors offer higher spatial coverage as the likely explanation for the gap between their two classes: more patches carry Wood, so more are classified as foreground. No coverage statistics are reported for either class, and with two classes and no ablation the hypothesis is offered rather than tested. Both are area classes — the study never leaves that rung — and the mechanism named is the distilled patch classifier's base rate, not visual difficulty for the LLM. The extension to point symbols as the limiting case of low coverage is OURS, not theirs: cite the sentence as a suggestive parallel to our area-to-point difficulty ladder, never as evidence for it.
- **Relevance:** §2 related work; §5 discussion — why point symbols are the harder rung · Difficulty ladder (area segmentation → point symbols) · **supports**

### KP4
- **Quote (verbatim):** "Experimental results demonstrate that the refined labels achieve a high recall of more than 90%. Additionally, the intersection over union (IoU) scores—84.2% for Wood and 72.0% for Settlement—along with precision scores of 87.1% and 79.5%, respectively, indicate that most labels are well-aligned with ground-truth annotations."
- **Locator:** page_index 0 · p.1 · Abstract
- **Paraphrase:** Each of the abstract's headline figures needs its protocol attached, and one of them is class-dependent. The IoU and precision figures are the down-sampled, patch-level values of Table 1 (Settlement 0.720 and 0.795; Wood precision 0.871) at threshold σ = 0.5, while the unqualified "more than 90%" recall claim is true of both classes only under the up-sampled, pixel-level protocol of Table 2 (0.975 and 0.968); under Table 1 it holds for Wood (0.939) and for the two-class mean (0.910), but not for Settlement (0.880). That is class-dependence, not demonstrated protocol mixing — a class-unspecific or macro-averaged reading of Table 1 satisfies the sentence as written. The quoted Wood IoU of 84.2% matches neither table — Table 1 gives 0.824 and Table 2 gives 0.781 — so it appears to be a transposition, though §3.2 also reports Wood down-sampled IoU "reaching 0.85" in the threshold sweep, so an unlabelled sweep value is a second possible origin. Any comparison table we build must carry the protocol, and none of these figures should be moved without it.
- **Relevance:** §2 related work; results comparison table · Metric hygiene — protocol-dependent and class-dependent headline figures · **complicates**

### KP5
- **Quote (verbatim):** "Table 2. Up-sampled: pixel-wise classification results at attention weight threshold of 0.5. IoU Precision Recall Wood 0.781 0.796 0.975 Settlement 0.474 0.482 0.968"
- **Locator:** page_index 4 · p.5 · §3.2 Quantitative result — Table 2 (up-sampled, pixel-wise)
- **Paraphrase:** The same attention maps, scored against the same ground truth at pixel rather than 64×64 patch resolution, give Settlement an IoU of 0.474 and a precision of 0.482 on a recall of 0.968 — a detector that finds nearly everything and is right about half the time. Set against Table 1's down-sampled Settlement figures (IoU 0.720, precision 0.795, recall 0.880), the choice of resolution-harmonisation scheme, not the model, moves Settlement IoU by roughly 0.25. The authors give the reason themselves — "the coarse-grained predictions [fail] to align precisely with the fine-grained ground-truth labels, even after up-sampling" — and the two protocols measure different things rather than the same thing twice: down-sampling scores a 64×64 predictor against a permissive tile-level ground truth (foreground if it contains any foreground pixel), up-sampling demands pixel-precise delineation a 64×64 predictor cannot give. Both tables are published side by side, so this is not a case of a flattering ruler being selected. It remains a clean illustration that a headline number is a claim about a protocol.
- **Relevance:** §2 related work; §4 evaluation protocol — why we state matching rules explicitly · Metric hygiene — the same model under two evaluation protocols · **complicates**

### KP6
- **Quote (verbatim):** "Given that LLM-generated annotations may not be fully accurate, we visualized the labels in an interactive interface, allowing human annotators to efficiently correct errors by simply clicking to flip incorrect labels. As the majority of labels were accurate, this correction process was highly efficient, typically requiring less than one minute per map sheet."
- **Locator:** page_index 4 · p.5 · §2.4 Experimental settings — Dataset
- **Paraphrase:** The training labels are not raw LLM output: a human reviewed them in a click-to-flip interface, reportedly in under a minute per map sheet. This is the source's annotation-budget claim, and it is what makes the abstract's "without the use of fine-grained manual labels during training" literally true but easy to over-read — coarse manual labels were used, just cheaply. The claim also sits awkwardly beside the conclusion's approximately 70% label accuracy: roughly three labels in ten needing a click (each crop carries two independent class labels) is hard to reconcile with under a minute per sheet unless each sheet yields few crops, and the paper reports neither the number of crops per sheet nor the sheet dimensions from which it could be derived, and gives no measurement basis for the ~70%, so the two figures may not even describe the same label set. The tension is real but strictly unquantifiable from the source. Cite the interaction pattern; treat the minute as unverified.
- **Relevance:** §5 discussion — annotation budgets and what counts as a manual label · Annotation budgets / ground-truth epistemics · **complicates**

### KP7
- **Quote (verbatim):** "The results demonstrate that increasing the threshold improves IoU and precision, though it slightly reduces recall. This effect was less pronounced for the settlement class, where metrics stabilized at lower thresholds but achieved lower maximum values—IoU of 0.72 (down-sampled) and 0.47 (up-sampled), and precision of 0.80 (down-sampled) and 0.48 (up-sampled)."
- **Locator:** page_index 5 · p.6 · §3.2 Quantitative result — threshold sweep (figs. 6 and 7)
- **Paraphrase:** The attention threshold σ is a free parameter, and the paper sweeps it, reporting the maxima each class reaches; which sheet the sweep runs on is never stated, though the evaluation design makes sheet 3922 the safe reading. Both tables are quoted at σ = 0.5 while the best precision figures are quoted at σ = 0.9, so the numbers in circulation come from two different operating points: σ = 0.5 as an untuned default for the tables, and σ = 0.9 as a peak read off the evaluation sweep — and those peaks (0.93 down-sampled, 0.84 up-sampled) are reported for Wood only. In our terms the σ = 0.9 figures are an oracle operating point on a one-sheet evaluation set; nothing suggests σ = 0.5 was chosen on the evaluation data. There is no carried threshold and no transfer measurement here either, since the held-out sheet shares agency, series and 1973–1975 date range with the three training sheets (its adjacency is our inference from the German sheet-numbering grid, not a statement in the text).
- **Relevance:** §5 discussion — transfer taxes and why we report carried as well as oracle points · Calibration transfer / carried vs oracle operating points · **extends**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "these approaches require extensive training data and ground-truth annotations, which are particularly costly and labor-intensive to generate for historical maps"
- **Locator:** page_index 0 · p.1
- **Why:** The lineage's own statement of the problem that motivates putting a general-purpose model in the loop at all — a compact pivot for the §2 paragraph that moves from supervised segmentation to VLM-based extraction, in the words of an author who then went and used an LLM to solve it.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
