# AB+ — Exploring Robust Features for Few-Shot Object Detection in Satellite Imagery

| field | value |
|---|---|
| **citekey** | `bou_exploring_2024` |
| **full cite** | Bou, Xavier et al. (2024) *Exploring Robust Features for Few-Shot Object Detection in Satellite Imagery.* 2024 IEEE/CVF Conference on Computer Vision and Pattern Recognition Workshops (CVPRW). DOI: 10.1109/cvprw63382.2024.00048 |
| **register** | Borrowed (computer vision — few-shot object detection in remote sensing) |
| **primary gap** | Annotation budgets — the few-shot alternative |
| **also touches** | Open-vocabulary detection alternative; Calibration transfer / transfer taxes; Metric hygiene — class-relative vs aggregate reporting; The area-segmentation to point-symbol difficulty ladder; Cost/accuracy trade-space |
| **page index → printed page** | `page_index N` = printed p.(N+1) (best-effort) |

## Summary (Claude's synthesis — advisory, unverified)

Bou and colleagues (arXiv:2403.05381v1, 8 March 2024) build a few-shot detector for satellite imagery by keeping a two-stage architecture and replacing only the classification head. A Faster R-CNN trained on DOTA (403,318 annotated instances, 16 general classes) supplies class-agnostic proposals; a frozen backbone yields a feature map; each class becomes a prototype, the normalised mean of the patch embeddings under its annotated boxes; and proposals are labelled by cosine similarity, with K = 200 background prototypes clustered from object-free crops to suppress false alarms. Only the prototypes are trainable. Evaluation runs at N = {5, 10, 30} examples per class on SIMD and DIOR, reporting mAP50 on novel classes.

Three findings bear on us. First, the annotation-budget curve: at 5-shot on SIMD the detector reaches 35.44 mAP50 against a DOTA-pretrained YOLOv5's 16.60, holding the lead to 30-shot (41.21 against 29.48). This looks like the sharpest form of the "why not just fine-tune a few-shot detector?" objection to our pipeline: it needs a few dozen boxes and thereafter costs a forward pass, not a metered API call, but only on top of a proposal network trained on DOTA's 403,318 annotated instances, and only where that training set's object definition matches the target class. The paper's own DIOR collapse is what the method does when it does not, and its stated remedy is to find a better-aligned pre-training dataset — for which Soviet-era cartographic symbol families have no analogue. That cuts in our favour: the rival is a weaker objection to our cost argument than it first appears.

Second, cutting the other way: purely visual DINOv2 features beat every CLIP variant on novel classes, including the remote-sensing-tailored RemoteCLIP and GeoRSCLIP. The authors' explanation is a vocabulary argument — captions never name propeller-aircraft or stair-truck, so the text tower has nothing to align a rare fine-grained class to. Table 2 reverses across class bands: RemoteCLIP ViT-H/14 leads on base classes (0.482) and is near-worst on novel ones (0.117), against DINOv2 ViT-L/14's 0.416 and 0.306. Aggregating over both bands would compress the gap and hide the mechanism without reversing it: DINOv2 still leads RemoteCLIP ViT-H/14 on an unweighted band mean (0.361 against 0.300) and on a class-count-weighted mAP over SIMD's four base and ten novel classes (0.337 against 0.221). The split earns its keep by making the trade visible, not by changing who wins.

Third, the recall ceiling sits upstream. On DIOR the carried mAP50 collapses to 9.56-12.60 while the same prototypes, scored on ground-truth boxes, reach classification F-1 above SIMD's at 5-shot (59.58 against 57.96) and 30-shot (72.23 against 66.88), though below it at 10-shot (60.60 against 64.30) — a cross-metric contrast, not a matched delta. DOTA treats buildings and ground areas as background, so DIOR's area-like classes are never proposed. Difficulty here is at least partly architecture-relative rather than intrinsic to spatial extent: swapping in FSRW's proposals lifts DIOR 30-shot from 12.60 to 26.46, recovering roughly half the distance to SIMD's 41.40 and leaving the rest unexplained.

## Positioning annotation (interpretive)

The annotation-budget benchmark for our cost/accuracy argument, and the cluster's most direct rival: a prototype classifier over frozen DINOv2 features that, on SIMD, beats a supervised YOLOv5 at 5-30 boxes per class and thereafter runs for the price of a forward pass. The scoping matters: on DIOR, whose novel classes are unlike anything in the proposal network's DOTA pre-training, the same detector trails FSRW at every shot count and loses to YOLOv5 at 30-shot (12.60 against 16.99). It also supplies the cluster's strongest evidence against contrastive vision-language grounding in this domain — purely visual features win on novel classes even against remote-sensing-tailored CLIPs, because captions never name the fine-grained category — which supports our scepticism about open-vocabulary transfer while sitting uncomfortably close to our own VLM commitment. Cited in §2 to define the few-shot/annotation-budget alternative, in §6 for the cost floor, and in the architecture discussion for its cleanest lesson: the DIOR collapse shows a two-stage system's ceiling set by a proposal stage calibrated on a different object definition, diagnosed by the same move we use, substituting ground-truth boxes for the proposal stage, though the paper reports classification F-1 under the oracle against end-to-end mAP50 carried, so its version is a qualitative contrast rather than a matched delta.

## Key points (salience-ranked to Paper B)

### KP1
- **Quote (verbatim):** "Robust visual features largely outperform state-of-the-art supervised methods when annotated data is limited."
- **Locator:** page_index 0 · p.1 · Figure 1 caption
- **Paraphrase:** With few annotations per class, a detector built on frozen general-purpose visual features beats a supervised detector fine-tuned on the same examples — on SIMD, whose novel classes are fine-grained subtypes (aircraft and vehicle types) of categories the DOTA-trained proposal network already localises well. The paper's limitations section names this as the favourable regime. The figure plots mAP against 1, 5, 10, 20, 30 and 50 examples per class on SIMD; Table 1 gives the tabulated form (35.44 against YOLOv5's 16.60 at 5-shot, 41.21 against 29.48 at 30-shot).
- **Relevance:** §2 Related work — few-shot detection / §6 Discussion — cost/accuracy trade-space · Annotation budgets — the few-shot alternative · **complicates**

### KP2
- **Quote (verbatim):** "These captions often lack the ability to describe all elements in the image, since a single satellite image can contain numerous instances and concepts. Thus, we argue that VLMs are limited by the granularity of image descriptions, which restricts their capabilities for FSOD on fine-grained, rare categories."
- **Locator:** page_index 5 · p.6 · §4.1 Ablation study — Visual vs. vision-language features
- **Paraphrase:** Image-text pre-training learns whatever the captions name, and a caption for a scene dense with instances names only some of them at a coarse granularity; the authors argue this is why vision-language models fail on fine-grained, rare categories in few-shot detection.
- **Relevance:** §2 Related work — open-vocabulary detection · Open-vocabulary detection alternative — vocabulary grounding limits · **supports**

### KP3
- **Quote (verbatim):** "Visual features show higher detection capabilities on novel classes cnovel, and they report strong performance in base classes cbase as well. DINOv2 largely outperforms RemoteCLIP on novel classes despite having fewer parameters."
- **Locator:** page_index 6 · p.7 · Table 2 caption — backbone comparison, 10-shot SIMD
- **Paraphrase:** Results are reported split by class band rather than aggregated, and the split is load-bearing: in Table 2 the ordering reverses between bands. Without fine-tuning, RemoteCLIP ViT-H/14 leads on base classes (0.482) but sits near the bottom on novel ones (0.117), while DINOv2 ViT-L/14 records 0.416 and 0.306. At this tier the domain-tailored remote-sensing CLIPs buy performance on common classes without buying it on rare ones — though at matched ViT-B/32 they edge general CLIP on novel classes too (GeoRSCLIP 0.132, RemoteCLIP 0.124 against CLIP 0.113), so the clean form of that claim rests on the L/14-H/14 tier.
- **Relevance:** §5 Results — metric hygiene / §6 Discussion — transfer taxes · Metric hygiene — class-relative vs aggregate reporting; transfer taxes · **extends**

### KP4
- **Quote (verbatim):** "Therefore, categories containing those elements in DIOR will be ignored as object candidates and consequently never detected."
- **Locator:** page_index 6 · p.7 · §4.1 Ablation study — Classification abilities of DINOv2 features
- **Paraphrase:** Because the region proposal network was pre-trained on DOTA, whose object definition treats buildings and ground areas as background, DIOR's area-like classes (airport, trainstation, dam, toll-station) are never proposed and so can never be detected, whatever the classifier's quality. The system's recall ceiling is set by a component calibrated on a different object definition.
- **Relevance:** §4 Architecture / §6 Discussion — where difficulty actually lives · The area-segmentation to point-symbol difficulty ladder · **extends**

### KP5
- **Quote (verbatim):** "we evaluate the classification abilities of the learned prototypes using their ground truth box annotations as region proposals"
- **Locator:** page_index 6 · p.7 · §4.1 Ablation study — Classification abilities of DINOv2 features
- **Paraphrase:** To locate the bottleneck, the authors substitute ground-truth boxes for the proposal stage and score classification alone — an oracle operating point. Table 3 shows the classifier is healthy on DIOR: F-1 above SIMD's at 5-shot (59.58 against 57.96) and 30-shot (72.23 against 66.88), though below it at 10-shot (60.60 against 64.30). Meanwhile the end-to-end DIOR mAP50 sits at 9.56-12.60, pointing at the proposal stage — though the two figures are different metrics rather than one metric under two operating points, and the paper's confirming evidence is the FSRW-as-RPN swap (DIOR 30-shot rising from 12.60 to 26.46), not the oracle scores alone.
- **Relevance:** §5 Results — carried vs oracle operating points · Carried vs oracle operating points · **extends**

### KP6
- **Quote (verbatim):** "satellite imagery contains a finite number of backgrounds, i.e. the different earth land cover types (water, pavement, urban, forest, etc.). For this reason, we propose to generate K background prototypes using object-free areas in available images."
- **Locator:** page_index 3 · p.4 · §3.1 Building prototypes — Background prototypes
- **Paraphrase:** Unlike natural photographs, satellite scenes draw their backgrounds from a small closed set of land-cover types, so the background itself can be modelled explicitly as K learned prototypes built from object-free crops — introduced to cut false alarms from invalid region proposals.
- **Relevance:** §4 Architecture — verifier and false-alarm control · Architecture — explicit false-alarm control · **extends**

## Optional framing hook (not counted in the salience cap)

- **Quote (verbatim):** "Results indicate that visual features are largely superior to vision-language models, as the latter lack the necessary domain-specific vocabulary."
- **Locator:** page_index 0 · p.1
- **Why:** A single sentence from inside the remote-sensing detection literature stating that the vision-language route fails for want of domain vocabulary — the cleanest pivot for the §2 move from the open-vocabulary cluster to our claim that Soviet-era cartographic symbol families are exactly such a missing vocabulary, and a warning we must answer for our own prompted VLM.

## Extraction / fidelity notes (auto-generated)

- Deterministic quote check: **7/7 passed**.
- Generated by: run 2026-08-30; pipeline rev `pre-bootstrap-10k-2026-04-28-1640-g00a94aae6`.

## Independent verifier (advisory — flags only)

- **paraphrase flags:** none
- **summary flags:** none
- **relevance flags:** none
- **overall:** PASS-WITH-EDITS
