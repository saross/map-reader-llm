# Optimal crop sizing for small feature detection in VLM few-shot prompting

For detecting **15-20 pixel burial mound symbols** on Soviet topographic maps via VLM few-shot prompting, the recommended crop size is **200-400 pixels** (approximately **12-25× the feature diameter**), with **300×300 pixels** as a strong practical default. Negative examples should use **identical crop dimensions** to positives. These recommendations synthesize constraints from VLM technical specifications, remote sensing literature, and few-shot learning research—though notably, no authoritative guidance exists specifically for VLM visual prompting crop ratios.

## VLM technical constraints drive minimum crop sizes

The most important finding for your use case is that VLM providers specify minimum image dimensions that exceed typical computer vision recommendations. **Claude requires images to be at least 200 pixels on any edge**—images below this threshold show degraded performance. GPT-4V processes images through internal **512×512 pixel tiles** in high-detail mode, meaning your target features need sufficient pixels to be visible within these processing units. Gemini upscales images smaller than **768×768 pixels**, which can introduce artifacts for small features.

For your 15-20 pixel symbols, a tight crop of 40-60 pixels (the 2-3× diameter recommended by few-shot metric learning literature) would fall dangerously below these thresholds. The practical minimum for VLM prompting is therefore **200×200 pixels**, with **300-400 pixels preferred** to ensure robust internal processing across all frontier models.

No official documentation from OpenAI, Google, or Anthropic provides explicit guidance on feature-to-crop ratios for few-shot visual examples. This represents a significant gap in practitioner literature—recommendations below are derived from combining VLM specifications with empirical findings from adjacent fields.

## Object detection research suggests tighter crops than VLMs allow

Traditional computer vision literature offers more specific ratio guidance, though calibrated for neural network training rather than VLM prompting:

| Object detection framework | Recommended crop sizing | Key principle |
|---------------------------|------------------------|---------------|
| **SAHI (sliced inference)** | 256-512px patches | Objects should occupy 1-5% of crop area |
| **YOLO practitioners** | Object >5% of frame height | Minimum 20× height for 15px targets |
| **MS COCO standard** | "Small" defined as <32×32 pixels | Your symbols qualify as "small objects" |
| **Faster R-CNN** | Add 32-64px anchors for small objects | Default anchors start at 128px |

The CVPR 2019 paper "The Power of Tiling" established that objects should occupy **at least 3-5% of patch dimensions** for reliable detection. For 20-pixel features, this implies patches of **400-660 pixels**—aligning well with VLM requirements. A critical finding from archaeological remote sensing: a Bulgaria burial mound study using fixed tile sizes achieved only **5-13% true positive rates**, demonstrating that tile size must adapt to object size.

SAHI framework research (IEEE ICIP 2022) showed that sliced inference with **256×256 patches and 25% overlap** improved average precision by **5-12%** for small objects compared to processing full images. While this applies to model inference rather than prompt engineering, it suggests that focused crops improve small object recognition broadly.

## Few-shot learning recommends 2-4× diameter plus context margin

Metric learning literature (Siamese networks, prototypical networks) provides the most relevant guidance for *exemplar* sizing, though oriented toward embedding networks rather than VLMs:

The CVPR 2020 few-shot object detection paper specifies cropping support images around targets with a **16-pixel context margin**, zero-padded and resized. For a 20-pixel feature, this yields a 52-pixel raw crop, typically resized to **84×84 or 127×127 pixels** for network input. SiamFC tracking uses **127×127 exemplar images** with context calculated to maintain fixed area around the bounding box.

Research on receptive fields in Siamese networks found that **optimal receptive field size is 60-70% of exemplar dimensions**—too much context makes features insensitive to spatial location, while too little loses discriminative structural information. This suggests including substantial context, but not overwhelming amounts.

For VLM prompting where you cannot control internal processing, **erring toward larger crops (3-4× diameter)** is safer than the 2× diameter typical in metric learning.

## Practical crop size recommendations for your use case

Synthesizing across domains and accounting for VLM constraints:

| Crop approach | Dimensions | Diameter ratio | Pros/cons |
|---------------|-----------|----------------|-----------|
| **Minimum viable** | 200×200 px | ~10-13× | Meets Claude minimum; may lose some context |
| **Recommended** | 300×300 px | ~15-20× | Balances context with focus; safe across VLMs |
| **Context-rich** | 400×400 px | ~20-27× | Maximum context; captures surrounding map features |
| **Full tile** | 512×512 px | ~26-34× | Only for showing null/empty examples |

The **300×300 pixel crop** represents the best balance for hard positive and hard negative exemplars: large enough to meet all VLM minimum requirements, small enough that the target feature remains visually prominent (occupying roughly **0.4-0.9%** of crop area), and sufficient to capture distinguishing context like adjacent symbols, labels, or terrain features that help differentiate true burial mounds from confusable patterns.

For your specific workflow with three exemplar tiers (canonical legend symbols, hard positives/negatives, full null tiles), a middle-ground sizing of **256-320 pixels** for hard examples creates visual distinctiveness from tight canonical crops (~64-128px resized) while remaining clearly different from 512×512 null tiles.

## Negative examples must match positive dimensions exactly

The consensus across all research domains is unambiguous: **negative exemplars should use identical crop dimensions to positives**. This finding emerges from triplet loss, contrastive learning, and few-shot detection literature:

The "hardness" of negatives should come from **semantic/visual similarity**, not size differences. Using different sizes introduces confounding variables and biases the embedding space. FaceNet research found that "very hard" negatives (closer to anchor than positive) cause training instability, but this applies to neural network training rather than VLM prompting—for your few-shot prompts, including genuinely difficult confusable symbols is valuable.

For hard negative selection, research recommends a difficulty distribution: approximately **50% semi-hard negatives** (different but visually similar symbols), **30% easy negatives** (clearly different patterns), and **20% hard negatives** (highly confusable features). All should use the same crop dimensions as your hard positive examples.

**When the "target" is absent in a negative crop** (showing map area without the feature), center the crop on the most confusable element—the similar-looking symbol, contour line intersection, or text element that triggered the false positive. This maintains consistency with positive crops that center on the actual target.

## Remote sensing reveals performance thresholds for small objects

Archaeological and cartographic detection studies provide directly relevant benchmarks. MATLAB documentation establishes that objects with area **≥0.015% of image** achieve AP >0.9, while objects **≤0.0024% of image area** (roughly 100 square pixels in a 640×640 crop) show considerable performance degradation.

Your 15-20 pixel symbols (~225-315 square pixels) in a 300×300 crop occupy **0.25-0.35%** of area—comfortably above the degradation threshold and within the reliable detection range. In contrast, the same symbols in a 512×512 tile occupy only **0.08-0.12%**, explaining why direct tile-level detection struggles.

The map symbol detection literature remains sparse, but studies on historical map digitization consistently find that **point features require higher resolution relative to symbol size** than areal features, and benefit from object detection (bounding box) approaches rather than semantic segmentation.

## Context provides disambiguation value for map symbols

Beyond meeting technical minimums, including **16-24 pixels of surrounding context** serves several functions for burial mound detection:

Spatial grounding shows where on the map the symbol appears—burial mounds typically appear in specific landscape contexts (elevated terrain, near watercourses). Adjacent features like elevation labels, contour patterns, or other point symbols help disambiguate similar shapes. Surrounding map typography and symbology provide scale reference that pure tight crops lose.

The SimCLR contrastive learning insight that "random cropping creates global-to-local view prediction tasks" suggests that **varying crop scales during training improves robustness**. For VLM prompting, this implies that including a mix of crop sizes in your few-shot examples (e.g., 250px, 300px, 350px) may help the model generalize better than uniform sizing—though this remains untested in the VLM prompting context.

## Recommended implementation for burial mound detection

For hard positive examples (difficult real mounds mined from false negatives):
- **Crop size**: 300×300 pixels centered on the mound symbol
- **Context margin**: ~140-145 pixels around a 15-20px feature (~7× radius on each side)
- Include diverse backgrounds, degraded examples, and edge cases

For hard negative examples (confusable non-mound symbols mined from false positives):
- **Same 300×300 pixel crops** centered on the confusable feature
- Select genuinely difficult cases: symbols with radiating lines, circular patterns, or similar visual structure
- Include the false positive that triggered inclusion—the model needs to learn these specific confusions

For canonical/legend symbols (existing tight crops):
- Maintain current sizing (~64-128px) for clear, idealized examples
- These serve a different function: showing the platonic form of the symbol

For null/empty tiles (existing 512×512 tiles):
- Maintain full tile size to demonstrate absence at the inference scale
- Ensures the model understands what "no burial mound present" looks like at operational resolution

## Conclusion

The key ratio recommendation is **15-20× feature diameter** for VLM few-shot prompting—substantially larger than the 2-4× recommended by few-shot metric learning, driven by VLM minimum input requirements rather than pure recognition theory. **300×300 pixels** serves as a robust default for 15-20px features, satisfying all VLM technical constraints while maintaining visual prominence of the target. Negative examples should always match positive dimensions, with difficulty coming from visual similarity rather than sizing differences. These recommendations derive from synthesizing VLM documentation, object detection research, and metric learning literature—no direct studies on VLM visual prompting crop ratios exist, making empirical testing against your specific detection task essential for optimization.