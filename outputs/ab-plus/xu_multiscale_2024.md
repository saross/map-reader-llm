# AB+ — Multiscale object detection on complex architectural floor plans

| field | value |
|---|---|
| **citekey** | `xu_multiscale_2024` |
| **full cite** | Xu, Zhongguo et al. (2024) *Multiscale object detection on complex architectural floor plans.* Automation in Construction. DOI: 10.1016/j.autcon.2024.105486 |
| **register** | Borrowed (computer vision / construction automation — Automation in Construction) |
| **primary gap** | Symbol-on-technical-drawing analogue — closed-vocabulary symbol detection on line drawings |
| **also touches** | Metric hygiene and reporting comparability; Annotation budgets and ground-truth epistemics; Tiling and resolution trade-space; Difficulty ladder: area segmentation to point symbols; Cost, accessibility, and what the CNN route requires |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Xu, Jha, Mehadi, and Mandal present ArchNetv2, a YOLOv8-derived convolutional detector for thirteen fixture symbols — doors, windows, stairs, sinks, fridges, and the rest — on complex architectural type (CAT) floor plans, not the simple brochure type (SBT) plans most prior work uses. It is our task with the archaeology and the cartography stripped out: conventionalised line symbols from a fixed vocabulary, distributed across a large, cluttered, text-annotated drawing. The authors state the difficulty in our own terms: floor-plan objects are black-and-white lines and curves and so carry less contextual information than natural objects, which makes architectures designed for photographs sub-optimal on them — though with every model retrained on their plans, a stock YOLOv8l still reaches 87.80 per cent mAP0.5 against ArchNetv2's 93.50. Their answer is architectural surgery — a fourth, finer detection head plus a convolutional block attention module — for 5.7 points of aggregate at roughly 10 per cent more parameters, about 15 per cent slower, 62.5 ms per image.

Four things bear on us. First, the supervision budget: 54 real floor plans, hand-annotated, split 36/8/10 and expanded eightfold by rotation and flipping to 288/64/80. The test set is therefore 80 geometric derivatives of 10 drawings; the split precedes augmentation, so there is no leakage, but the evaluation items are not independent. The transfer question we actually ask — what a small gold standard buys at deployment scale — this design cannot pose.

Second, metric hygiene, twice over. The 93.50 per cent that will travel is an unweighted mean over thirteen classes, and Table 4 shows the spread it hides: fridge 67.90, shower 77.50, window 87.40 against toilet, firebox, and stove at 99.50. Windows — the class closest to our target — sit 6.1 points below the mean, and there the bespoke network loses to a stock YOLOv7 at 90.20: the aggregate winner is not the per-class winner where it matters to us. It also states its gains on inconsistent bases: §4.1's 'by 5.70% relative to YOLOv8l' is a percentage-point difference (93.50 − 87.80), while §5.2's 'by more than 6% and 19% mAP' holds only as relative increases (6.5 and 25.2 per cent). Any improvement figure lifted from it must carry its base.

Third, scale management. Tiling is the fix adopted by the one prior floor-plan work the authors cite for small symbols, on the simpler brochure-type SESYD set; ArchNetv2 itself downsamples 2200 by 3400 sheets to 640 by 640 and names the resulting loss of object visibility as a limitation, with a larger input conjectured to help but liable to exhaust memory — a trade-off listed as future work, not measured.

Fourth, symbol semantics. The worst class fails for a reason that flatters our approach: a fridge's identifying text label may sit outside its symbol, where an attention module confined to the target box cannot use it. Finally, walls are out of scope because bounding boxes are imprecise for complex geometries and belong to semantic segmentation — our ladder's area-versus-symbol boundary, drawn in a neighbouring literature.

## Positioning annotation (interpretive)

The symbol-on-technical-drawing analogue in its purest form: a closed vocabulary of thirteen conventionalised line symbols detected on large, cluttered, text-annotated drawings, which is structurally our problem with the archaeology removed. Its use to us is threefold — it articulates why line-drawing symbols are harder for photograph-trained detectors than their size suggests, it supplies a clean instance of the aggregate-versus-per-class metric trap (93.50 per cent mAP over classes running from 67.90 to 99.50, with the class closest to our target won by a stock YOLOv7 rather than by the bespoke network), and it shows what the CNN route costs: a hand-annotated bespoke corpus, a retrained and re-architected network per domain, and a test set built by augmenting ten drawings. It also marks what the CNN route achieves on its own benchmark — a floor-plan mAP0.5 not directly commensurable with our tile-level F1 and MCC — and the two failure modes, symbol identity carried by adjacent text and area-shaped features needing segmentation rather than boxes, that a prompted vision-language model addresses differently rather than merely better.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "the objects in floor plans are typically created by lines or curves in purely black and white, and therefore the object features have less contextual information compared to natural objects, such as animals, cars and natural scenes. This makes object detection in floor plans a challenging task."
- **Locator:** page_index 1 · p.2 · §1 Introduction — why floor-plan detection is hard
- **Paraphrase:** Floor-plan objects are drawn as black-and-white lines and curves, so their features carry less contextual information than natural objects such as animals or cars; the authors name this informational poverty as what makes symbol detection on a technical drawing hard.
- **Relevance:** §2 related work — the substrate our task shares with technical drawings · Symbol-on-technical-drawing analogue — why line-drawing symbols are not natural objects · **supports**

### KP2
- **Quote (verbatim):** "Table 4 Performance comparison with existing technique. AP0.5(%) TOD [47] YOLOv3 [38] ArchNet [50] YOLOv7 [41] YOLOv8n [42] YOLOv8l [42] ArchNetv2 Door 82.19 89.98 90.48 96.20 90.60 96.30 98.10 Stairs 80.87 53.68 67.54 99.00 91.90 99.40 95.30 Sink 77.27 90.40 88.27 97.60 87.60 93.70 98.50 Toilet 80.41 90.09 92.75 98.60 85.30 93.70 99.50 Firebox 86.24 83.28 89.31 99.00 93.70 98.90 99.50 Fridge 52.58 43.66 49.67 52.60 64.10 78.10 67.90 Stove 95.79 66.67 66.67 99.00 85.40 99.50 99.50 Dishwasher 63.23 57.63 62.02 58.80 66.50 64.80 95.70 Bathtub 80.78 93.06 91.89 99.70 97.70 99.50 99.20 Shower 55.03 38.57 42.28 58.00 69.50 80.50 77.50 Dryer 49.78 72.50 64.45 43.20 65.50 80.20 98.70 Washer 65.62 80.00 81.52 77.40 73.00 86.90 98.70 Window 68.28 84.64 84.44 90.20 68.10 70.00 87.40 mAP0.5 72.16 72.62 74.71 82.40 79.90 87.80 93.50"
- **Locator:** page_index 8 · p.9 · §4.1 Experiments — Table 4
- **Paraphrase:** The headline mAP0.5 of 93.50 per cent is a mean over thirteen classes whose per-class average precisions run from 67.90 (fridge) and 77.50 (shower) up to 99.50 (toilet, firebox, stove). The window class — the closest analogue to a small, repeated point symbol — sits at 87.40, some 6.1 points below the mean. Windows are also where the bespoke architecture is not decisive: ArchNetv2's 87.40 improves on YOLOv8l's 70.00 but is beaten by plain YOLOv7's 90.20 in the same table, so on the class closest to our target the aggregate winner is not the per-class winner.
- **Relevance:** §5 discussion — class-relative versus aggregate reporting · Metric hygiene and reporting comparability · **complicates**

### KP3
- **Quote (verbatim):** "The dataset is divided into a training dataset with 36 images, a validation dataset with 8 images, and a testing dataset with 10 images. Each floor plan image is annotated to generate a .txt file manually that contains the locations/sizes of all bounding boxes and the objects classes. Augmentation is used to expand the dataset in the manner that first rotates a floorplan image by 90◦, 180◦and 270◦, and the four rotated images are then flipped based on the horizontal center line. After augmentation, there are 288 floorplan images in the training dataset, 64 floorplan images in the validation dataset and 80 floorplan images in the testing dataset."
- **Locator:** page_index 3 · p.4 · §3.1 Dataset preprocessing
- **Paraphrase:** The whole supervision budget is 54 hand-annotated drawings split 36/8/10, then expanded eightfold by rotation and flipping to 288/64/80. The augmentation is applied to the test split as well, so the reported figures rest on 80 geometric derivatives of only 10 distinct floor plans.
- **Relevance:** §3 methods — supervision budgets and evaluation-item independence · Annotation budgets and ground-truth epistemics · **complicates**

### KP4
- **Quote (verbatim):** "In this method, a tiling strategy was used to improve the detection performance on small-size objects in large floor plan images (e.g., 5400 × 3600 pixels). The large floor plan image was first split into various tiles with certain size (e.g., 224 × 224 pixels) and then fed into the deep learning network."
- **Locator:** page_index 2 · p.3 · §2.2 Object detection in floor plan image — Rezvanifar et al.
- **Paraphrase:** The one prior work the authors cite for small symbols on a large drawing tiles it: a plan of the order of 5400 by 3600 pixels is cut into tiles of the order of 224 by 224 pixels before the detector sees it. The corpus is the simple-brochure-type SESYD set, materially easier than the complex architectural plans ArchNetv2 targets.
- **Relevance:** §3 methods — why the pipeline tiles the map sheet · Tiling and resolution trade-space · **supports**

### KP5
- **Quote (verbatim):** "resizing the input floor plan image to 640 × 640 for the proposed network would reduce the size of the objects. A large input image size might be beneficial for the performance of the network and it may lead to memory issues."
- **Locator:** page_index 11 · p.12 · §6 Conclusions — limitations
- **Paraphrase:** The authors name their own downsampling as a limitation: shrinking the sheet to 640 by 640 pixels reduces the size of the objects, while a larger input might improve performance but may exhaust memory — a conjecture the authors list as future work rather than a result they measured.
- **Relevance:** §5 discussion — the resolution/cost trade-off stated by a CNN pipeline · Tiling and resolution trade-space · **supports**

### KP6
- **Quote (verbatim):** "the fridge annotation can be outside or inside of the fridge (shown in Fig. 14), which makes the prediction challenging for the network."
- **Locator:** page_index 10 · p.11 · §5.2 Limitations — the fridge class
- **Paraphrase:** The worst-performing class fails because the text label that identifies a fridge may sit outside the symbol rather than inside it, which the network cannot exploit.
- **Relevance:** §4 architecture — what a language-capable detector can read that a box-bound CNN cannot · Symbol-on-technical-drawing analogue — symbol identity carried by adjacent text · **extends**

### KP7
- **Quote (verbatim):** "when the objects have complex geometries, such as the walls, it is not a precise way to detect objects using bounding boxes. Instead, wall detection is generally done using semantic segmentation techniques"
- **Locator:** page_index 11 · p.12 · §5.3 Future works — wall detection
- **Paraphrase:** Bounding boxes are treated as the wrong instrument for spatially extended features such as walls, which the authors route to semantic segmentation instead — an explicit split between area-shaped and symbol-shaped targets.
- **Relevance:** §2 related work — the ladder from area segmentation to point symbols · Difficulty ladder: area segmentation to point symbols · **supports**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "While prior works have directly used popular CNNs (which were primarily developed for natural image analysis) for floor plan analysis, our approach aims towards adaptation (and modification) of the CNNs to achieve superior performance for floor plan image analysis."
- **Locator:** page_index 11 · p.12
- **Why:** The CNN lineage's own statement of its strategy for domain shift: when a detector built for photographs meets a line drawing, you rebuild the detector. It sets up our contrast in a single sentence — we change the prompt, not the architecture, and pay in inference cost rather than in annotation and retraining.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **8/8 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
