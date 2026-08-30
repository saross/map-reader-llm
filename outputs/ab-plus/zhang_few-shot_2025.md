# AB+ — Few-shot learning with large foundation models for automated segmentation and accessibility analysis in architectural floor plans

| field | value |
|---|---|
| **citekey** | `zhang_few-shot_2025` |
| **full cite** | Zhang, Haolan & Zhang, Ruichuan (2025) *Few-shot learning with large foundation models for automated segmentation and accessibility analysis in architectural floor plans.* Journal of Infrastructure Intelligence and Resilience. DOI: 10.1016/j.iintel.2024.100137 |
| **register** | Borrowed (construction informatics / architectural drawing analysis — Journal of Infrastructure Intelligence and Resilience) |
| **primary gap** | Few-shot / annotation-budget — foundation-model extraction from a handful of annotated exemplars |
| **also touches** | Symbol-on-technical-drawing analogue — rooms and doors on raster architectural plans; Calibration transfer — decision rules derived from the reference set and carried to deployment; Metric hygiene — multiplier framing over collapsed baselines; stage-wise versus end-to-end evaluation; Ground-truth epistemics and evaluation-set realism; Difficulty ladder — area segmentation (rooms) versus small rectangular objects (doors) |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Zhang and Zhang segment rooms and doors on 2D raster architectural floor plans by wrapping the Segment Anything Model (SAM) in a five-exemplar few-shot loop. Their pipeline — GPT-integrated Multi-object Few-shot SAM (GMFS) — scores cosine similarity between SAM encoder features of the test plan and the masked regions of five reference plans, clusters the surviving points, prompts SAM with each cluster's best point, then has GPT-4 label the post-processed masks as public/private space or interior/entrance door. Validated on CubiCasa 5K (607 test plans) and Rent3D (210).

This is the cleanest statement available of the annotation-budget argument on a symbol-bearing technical drawing. Supervised prior art in the same domain annotates 4,800 to over 5,000 plans; GMFS reaches its operating point from five. It is not benchmarked against that prior art, though: Tables 2 and 3 pit it against DeepLabv3+ and DeepFloorplan, both listed in those tables at five reference samples, and the paper never says how they were trained. Two results transfer. First, which five exemplars you draw barely matters: three random reference sets give standard deviations within 0.04 (rooms) and 0.03 (doors) — but over only three draws, and the headline set sits at the top of that range (CubiCasa room F1 0.69 against draws of 0.68, 0.67, 0.66), so cite the range. Second, the budget dividend has a shape: one exemplar to five buys recall (+59% on doors) at little or no precision cost on doors (0.66 to 0.67, 0.61 to 0.60) and a small one on rooms (0.72 to 0.70, 0.74 to 0.66), while post-processing buys precision (over 100% on doors). The five exemplars come from corpora annotated exhaustively anyway: few-shot means few prompts, not a cheap ground truth.

Three cautions. (1) The absolutes are modest — room F1 0.69/0.62, door F1 0.70/0.58 — and the multiplier rhetoric (7.3 times, 13.1 times) is large only because the baselines collapse on the regional, IoU-matched metrics (DeepFloorplan room F1 0.05; DeepLabv3+ zero on every door metric). Cite the absolutes. (2) Two of the three SAM-mode multipliers do not reproduce: every DeepLabv3+ and DeepFloorplan figure recomputes exactly from Tables 2 and 3 as the mean of per-dataset ratios, but that convention gives 11.6 times precision and 6.5 times F1 against the stated 6.8 and 6.1 for rooms, and 3.7 against the stated 2.7 for door F1; the pixel- and mean-accuracy gains against the same SAM baseline do recompute exactly (+95.5%, +67%), ruling out a different convention. (3) The stages are never composed: GPT-4's classification F1 of 0.86 is measured on ground-truth masks, so no end-to-end number exists. Our consensus-plus-verifier pipeline faces the same temptation.

Transfer. The CubiCasa half of the evaluation runs on SVG-rendered plans converted to PNG — a standardised drawing style, not a degraded scan — and both corpora are filtered to at least three rooms. The authors name style divergence from the reference samples as a principal driver of false positives, the CubiCasa-to-Rent3D drop is that tax made visible. Our Soviet-era sheets sit outside that boundary.

## Positioning annotation (interpretive)

The few-shot/annotation-budget anchor from an adjacent symbol-bearing-drawing domain: a foundation-model pipeline reaching room F1 0.69/0.62 and door F1 0.70/0.58 across two corpora from five annotated exemplars, in a domain whose supervised prior art annotates thousands of plans. Cite it for the two transferable results — reference-set choice barely matters (standard deviations within 0.04), and extra exemplars buy recall while post-processing buys precision — and cite it against its own framing, since the eye-catching multipliers are artefacts of collapsed baselines run at the same five-sample budget rather than a win over the fully supervised prior art, and the segmentation and classification stages are never composed into an end-to-end figure. It supports our claim that a small gold standard can be enough to calibrate a prompted foundation model, while complicating any inference from its numbers to ours: its CubiCasa inputs are style-standardised vector renders rather than scans, and its targets are large room polygons and door rectangles rather than one point-symbol family among dozens.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "For instance, Seo et al. (2020) used 4800 annotated floor plans to train and test. Yang et al. (2023) used over 5000 floor plans for training. This requirement for extensive annotation poses a substantial barrier, particularly for accessibility analysis, where annotated data is often not available."
- **Locator:** page_index 2 · p.3 · §2.2 Automatic floor plan analysis
- **Paraphrase:** Supervised floor-plan analysis requires thousands of annotated drawings (4,800 used for training and testing in one cited study, over 5,000 for training in another), and the authors identify the annotation requirement rather than the architecture as the barrier in domains where labelled data is scarce. The counter-claim on the same page is that their pipeline works "with as few as five reference samples" — a roughly three-orders-of-magnitude reduction in annotation budget for the same class of task.
- **Relevance:** §2 related work — the annotation budget a prompted foundation-model pipeline avoids; §5 cost/accuracy trade-space · Few-shot / annotation-budget · **supports**

### KP2
- **Quote (verbatim):** "Specifically, when using five reference samples and post-processing, GMFS achieves average improvements of 4.0 times in precision, 9.6 times in recall, and 7.3 times in F1-score across two datasets compared to DeepLabv3+. Against DeepFloorplan, GMFS shows an average improvement of 22.7 times in precision, 4.5 times in recall, and 13.1 times in F1-score across both datasets."
- **Locator:** page_index 9 · p.10 · §4.3 Segmentation performance test
- **Paraphrase:** The headline gains are stated as multipliers over supervised baselines. Both figures reproduce exactly from Tables 2 and 3 as the mean of the two per-dataset ratios, but they are inflated by collapsed denominators rather than by high absolute performance: GMFS itself reaches room F1 0.69 on CubiCasa and 0.62 on Rent3D, while DeepFloorplan reaches 0.05 on both and DeepLabv3+ 0.12 and 0.07. A 13.1-times improvement over an F1 of 0.05 is a weak claim dressed as a strong one. The collapse is specific to the regional metrics computed under bipartite matching at an intersection-over-union threshold of 0.5 (§4.2); at pixel level the same baselines are not degenerate (DeepLabv3+ pixel accuracy 0.82 and 0.80 against GMFS's 0.87 and 0.87), which is precisely why an improvement factor from this literature is uninterpretable without its metric family attached.
- **Relevance:** §2 related work — why headline improvement factors across this literature are not comparable; §5 results — reporting absolute operating points · Metric hygiene — ratio framing over a degenerate baseline · **complicates**

### KP3
- **Quote (verbatim):** "We use floor plans with ground truth room or door masks with indexes to test the performance. GMFS achieves an average precision of 0.83 and recall of 0.91, resulting in an average F1 score of 0.86 for both rooms and doors."
- **Locator:** page_index 9 · p.10 · §4.4 Classification performance test
- **Paraphrase:** The GPT-4 classification arm is evaluated on ground-truth masks, not on the masks GMFS actually produces. The 0.86 classification F1 therefore sits on an oracle input and cannot be composed with the 0.69/0.62 room and 0.70/0.58 door segmentation F1s to give a pipeline-level score; the paper reports no end-to-end figure for the two stages run together. The authors nonetheless conclude from this test that "GPT-4 can effectively classify segmented masks generated from SAM" — the composition their own protocol rules out.
- **Relevance:** §4 architecture — detector plus adversarial verifier; §5 results — why stage metrics on oracle inputs must not be composed · Metric hygiene — stage-wise versus end-to-end evaluation in a multi-stage pipeline · **complicates**

### KP4
- **Quote (verbatim):** "we additionally tested GMFS on three different sets of reference floor plans randomly selected from the final set described in Section 4.1."
- **Locator:** page_index 9 · p.10 · §4.3 Segmentation performance test — sensitivity analysis
- **Paraphrase:** The authors repeat the segmentation evaluation — not the classification arm — with three independently drawn sets of five reference plans. The reported spread is small — standard deviations within 0.04 on every room metric (Tables 4 and 5) and within 0.03 on every door metric (Tables 8 and 9) — so performance is insensitive to which five exemplars happen to be drawn, at least within a style-homogeneous corpus.
- **Relevance:** §3 methods — gold-standard construction; §5 discussion — how much a small calibration set's composition matters · Few-shot / annotation-budget — robustness of a small exemplar set · **supports**

### KP5
- **Quote (verbatim):** "Specifically, recall improves by an average of 59% when increasing from one to five reference samples, while precision sees an average improvement of over 100% with the application of post-processing."
- **Locator:** page_index 9 · p.10 · §4.3 Segmentation performance test — door segmentation
- **Paraphrase:** The two ingredients of the pipeline act on different error types and are reported separately: additional annotated exemplars buy recall, and geometric post-processing buys precision. Tables 6 and 7 bear this out for doors (one exemplar with post-processing gives precision 0.66/0.61 and recall 0.42/0.38; five gives 0.67/0.60 and 0.72/0.56), and Tables 2 and 3 show the same trade for rooms, where the extra exemplars raise recall from 0.37 to 0.68 on CubiCasa while precision edges down from 0.72 to 0.70.
- **Relevance:** §5 cost/accuracy trade-space — decomposing what extra gold-standard items buy versus what the verifier stage buys · Few-shot / annotation-budget — what marginal annotation actually buys · **extends**

### KP6
- **Quote (verbatim):** "Given that doors typically exhibit a distinctive rectangular shape, we filter the rectangles by selecting those with an aspect ratio between 0.75 and 1.25. These threshold values are derived from reference samples by calculating the smallest and largest aspect ratios for doors, ensuring they are well-suited for door detection in floor plans."
- **Locator:** page_index 6 · p.7 · §3.4 Mask post-processing — door mask filtering based on aspect ratio
- **Paraphrase:** The only post-processing threshold read off the reference samples is a shape prior for the small object class — the minimum and maximum door aspect ratios observed there become a hard [0.75, 1.25] acceptance band applied unchanged to every test plan. This is a carried operating point calibrated on a five-item gold standard, and the paper reports no alternative band, so the cost of carrying it rather than tuning it in-domain cannot be recovered from the paper.
- **Relevance:** §5 discussion — transfer taxes and carried versus oracle operating points · Calibration transfer — carried versus oracle operating points · **complicates**

### KP7
- **Quote (verbatim):** "The SVG-format floor plans were first converted to PNG format, as required for input to SAM. We then filter the floor plans by removing entries with incomplete annotations and those with fewer than three rooms, resulting in a final set of 612 floor plans. Only plans with more than three rooms were included to prevent the model from generating overly large masks that might cover multiple rooms."
- **Locator:** page_index 7 · p.8 · §4.1 Datasets — CubiCasa 5K
- **Paraphrase:** The CubiCasa evaluation substrate is a vector drawing rendered to raster, not a scan: the same page notes that the SVG version supplies a standardised and consistent visual style across samples (line thickness, colour, symbols, text annotations). This is a CubiCasa fact only — §4.1 describes Rent3D merely as "a collection of 2D floor plans", with more non-rectangular room shapes, and it is where scores drop. Plans are then filtered by room count — the two sentences give slightly different cut-offs, fewer-than-three versus more-than-three — to suppress a known failure mode, though for Rent3D the filter removed nothing (210 test + 5 reference = the full 215 apartments). Both moves make the task easier than ours in the ways that matter most for us: no scan degradation, no cross-sheet style drift, and a screened evaluation pool.
- **Relevance:** §2 related work — why five-exemplar results on clean vector renders do not transfer directly to scanned sheets; §3 corpus and ground truth · Ground-truth epistemics and evaluation-set realism · **complicates**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "This dependence on large datasets limits the scalability of these methods and restricts their application in floor plan analysis, especially in contexts where annotated data is scarce"
- **Locator:** page_index 2 · p.3
- **Why:** A one-line statement of the annotation-budget problem in a neighbouring symbol-on-technical-drawing domain — useful as the pivot in §2 from supervised map-symbol detectors to prompted foundation models, since the same sentence would read true with 'floor plan analysis' replaced by 'historical-map symbol extraction'.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
