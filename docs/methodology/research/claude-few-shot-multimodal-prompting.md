# Few-shot prompting for visual detection in multimodal LLMs

**Your F1 dropped from 0.75 to 0.64 because text instructions created modality interference**—a well-documented phenomenon where textual cues override visual analysis, causing the model to reject valid detections that don't perfectly match written criteria. The path to F1=0.85 lies not in better instructions, but in restructured pipelines, smarter example selection, and confidence-based thresholding rather than prompt-based filtering.

Research across GPT-4V, Claude, and Gemini consistently shows that visual few-shot examples should do the heavy lifting while text remains minimal and permissive. State-of-the-art VLMs achieve only **17% accuracy** on visual tasks when images conflict with textual priors, and "thinking" models like o3 show *worse* degradation (-6.56%) when text cues are present. Your recall drop exemplifies this: the model began "seeing" what the text primed it to expect rather than analyzing actual features.

## Optimal few-shot library size peaks around 10-15 examples per class

Empirical research on GPT-4V for histopathology classification found accuracy improved from **61.7%** (zero-shot) to **78.3%** (5-shot) to **90%** (10-shot), with no saturation observed up to 10 examples per class. This contrasts sharply with vendor guidance: Anthropic recommends 3-5 examples with "diminishing returns after 2-3," while Google suggests experimentation without specific numbers.

The discrepancy resolves when considering task complexity. For straightforward classification, 3-5 examples suffice. For specialized domains with subtle visual distinctions—like cartographic symbol detection—evidence supports continued improvement to 10+ examples per class. Your current **12 examples** sits near the sweet spot, suggesting example *quality* rather than *quantity* explains your plateau.

**Recommended composition for 15-20 total examples:**
- 40% clear positive examples (unambiguous burial mounds)
- 25% hard positives (subtle, partial, or degraded mounds that ARE real)
- 20% easy negatives (clearly different features)
- 15% hard negatives (visually similar features that are NOT mounds)

The ordering matters: LLMs exhibit recency bias, favoring patterns from the last few examples. For detection tasks prioritizing recall, place hard positive examples at positions 10-15 (near the end) so the model learns to include edge cases.

## Example selection through kNN retrieval outperforms random selection by 5-15%

The most impactful improvement available is **kNN-based example selection**. Rather than using fixed examples for all queries, pre-compute CLIP or SigLIP embeddings for your example pool, then dynamically retrieve the k most similar examples for each target tile. Research demonstrates this consistently outperforms random selection across all tested datasets, with accuracy gains of 5-15%.

The REPRE (representativeness) method offers an alternative: cluster your example pool via K-means, then select cluster centroids as representative samples. This ensures coverage across the full distribution of visual variations in burial mound symbols. Gaussian Monte Carlo selection—adding noise to images and selecting those with stable predictions—identifies robust, informative examples.

**Hard negative mining is non-negotiable.** Analyse your current false positives to identify common confounders—likely spot heights, trigonometric points, degraded map areas, and small circles from other feature classes. Add 3-5 explicit examples showing "This is NOT a burial mound because [specific visual distinction]." Run your current model on unlabeled tiles, collect false positives, and iteratively add these as hard negatives. One to two iterations typically suffice for convergence.

## Text-image interference explains your recall collapse

Your F1 drop from 0.75 to 0.64 follows a predictable pattern: text instructions **over-constrained** what the model considers a positive detection. Research on VLMs consistently shows that specific textual descriptions narrow interpretation, activate prior knowledge over visual analysis, and create confirmation bias toward described features.

The solution is counterintuitive: **use less text, not better text**. Structure your prompt with images first, followed by minimal task framing:

```text
[Visual examples - positive, then hard positive, then hard negative]
"Detect features similar to these examples. When uncertain, err toward detection."
[Target tile]
```

If you must include negative guidance, **show it visually** rather than describing it textually. "Do not look for X" often backfires—the model paradoxically becomes primed to think about X. Instead, include visual counter-examples with explicit labels: "This is NOT a burial mound—note the numeric elevation label indicating a spot height."

Google's Gemini documentation specifically recommends "semantic negative prompts": instead of "no false positives," describe the desired outcome positively. For your task: "Identify all features that could possibly be burial mounds, including uncertain cases" rather than "Only mark clear, unambiguous mounds."

## Two-stage pipelines resolve the precision-recall trap

The fundamental insight from precision-recall research is: **don't fight the tradeoff through instructions—fight it through architecture**. A two-stage pipeline separates concerns:

**Stage 1 (High Recall):** Use permissive detection with minimal text. Prompt: "Identify all circular or oval elevated features in this map section." Accept false positives liberally.

**Stage 2 (Precision Filter):** Apply stricter verification *only* to Stage 1 candidates. Prompt: "For each feature identified, rate the likelihood (0-100%) it is a burial mound based on these criteria: [specific distinguishing features]."

This architecture prevents restrictive criteria from affecting initial detection. The model sees all potential targets first, then evaluates them individually. Expected improvement: **+5-8% F1** based on comparable studies.

**Multi-pass voting** offers another precision-recall optimization: run detection 3 times at temperature 0.5 (or use Gemini 3's default 1.0), flag regions detected in ≥2/3 passes as positive. Research shows this reduces false positives by 35% while maintaining recall. The redundancy catches both random hallucinations (false positives eliminated by disagreement) and borderline true cases (preserved when detected consistently).

## Confidence calibration enables threshold optimization

VLMs can self-report useful confidence scores when prompted correctly, despite systematic overconfidence. The key technique is **verbalized confidence with calibration framing**:

```text
After analysis, provide:
1. Detection result (MOUND or NOT_MOUND)
2. Confidence score (0-100%) representing probability your answer is correct
3. Factors that REDUCE your confidence

Important: 70% confidence means you expect to be wrong ~30% of the time.
```

Research shows RLHF-trained models like GPT-4 and Gemini produce **better-calibrated verbalized confidence** than token logits, often reducing Expected Calibration Error by 50%. Once you have confidence scores, plot a precision-recall curve on your validation set and identify the threshold maximizing F1. The optimal threshold is rarely 0.5—for burial mound detection, it might need to be **0.3-0.4** to hit F1=0.85.

**Sample consistency** provides even better calibration: run each ambiguous tile 3-5 times, use agreement percentage as confidence. This outperforms verbalized confidence for failure prediction.

## VLMs have fundamental limitations for cartographic symbol detection

The CartoMapQA benchmark (2025) reveals that "current LVLMs still face significant challenges in reasoning over cartographic maps"—OCR capabilities are insufficient, and semantic reasoning remains shallow. More critically for your task:

- VLMs reliably count only **4-6 objects** without explicit serial counting
- GPT-4V achieves precision@0.5 of just **0.076** and mean IoU of **0.158** for object localization in remote sensing
- Coordinates returned "don't match actual object positions" with regularity

Traditional computer vision significantly outperforms VLMs for precise symbol detection: YOLOv3 achieves **89.5% detection rate** with precision **0.97** for burial mound detection on LiDAR data; U-Net variants reach **98.99% accuracy** for road extraction from historical WWII maps.

**The highest-impact path to F1=0.85 is a hybrid VLM+CV pipeline:**

1. **VLM initial detection**: Use Gemini to identify regions likely containing burial mounds (high recall pass)
2. **CV refinement**: Apply a trained U-Net or YOLO model on flagged regions for precise localization
3. **VLM verification**: Optionally use Gemini to validate/reject CV predictions

This leverages VLM strengths (scene understanding, zero-shot generalization, semantic reasoning) while compensating for weaknesses (counting, localization, small object detection).

## Gemini-specific optimizations for your pipeline

For Gemini 3 models specifically:

- **Keep temperature at 1.0**—Google explicitly warns that lower temperatures cause "looping or degraded performance" on complex tasks
- **Use `media_resolution_high`** (1120 tokens) to capture fine symbol details
- **Place images before text** in all prompts—this is critical for proper visual processing
- **Use structured XML or Markdown formatting** consistently; Gemini responds well to hierarchy
- Consider **`thinking_level: "high"`** for complex detection requiring reasoning

For output formatting, Gemini's `responseSchema` parameter enables strict JSON enforcement, but beware: format restrictions can degrade reasoning. Decouple reasoning from formatting by letting the model reason naturally first, then extract structured output.

## Implementation roadmap for F1 improvement

**Immediate actions (low effort, +8-13% potential):**

1. **Remove restrictive text** from your prompts—rely on visual examples alone
2. **Add 3-4 hard positive examples** (subtle/partial mounds that ARE real) near the end of your example sequence
3. **Replace text negatives with visual counter-examples** showing confusable symbols with explicit labels
4. **Request verbalized confidence scores** and tune detection threshold on validation data
5. **Frame instructions permissively**: "When uncertain, err on the side of detection"

**Medium-term improvements (+5-10% additional):**

6. **Implement two-stage detection**: broad candidate identification → targeted verification
7. **Add kNN-based example retrieval** using CLIP embeddings to dynamically select relevant examples per tile
8. **Deploy multi-pass voting** (3 passes, 2/3 agreement threshold)
9. **Analyse false positives** from current pipeline to mine hard negatives iteratively

**High-impact architectural change:**

10. **Implement hybrid VLM+CV pipeline**: Train a lightweight U-Net or YOLO model on Gemini-annotated data (with manual corrections), use Gemini for initial scene filtering and final verification

The research evidence strongly suggests your current approach can improve substantially through example curation (especially hard negatives), pipeline restructuring (two-stage detection), and confidence-based thresholding—without requiring fundamental methodology changes. The combination of these techniques should push F1 from 0.75 toward the 0.85 target, with the hybrid CV approach offering the most reliable path beyond that threshold.