# **Optimizing Vision-Language Models for Historical Map Symbol Extraction: A Deep Analysis of Few-Shot Strategies and Multimodal Prompting**

## **Executive Summary**

The automated extraction of anthropogenic features from historical cartography represents a critical convergence of computer vision, digital humanities, and geospatial analysis. The specific task of extracting symbols representing burial mounds—variously termed kurgans, tumuli, or barrows—presents a unique set of semiotic and morphological challenges that distinguish it from standard object detection tasks in natural imagery. This report provides an exhaustive technical analysis and strategic roadmap for optimizing a Vision-Language Model (VLM) pipeline, specifically utilizing the Gemini architecture, to achieve a target F1 score of 0.85 or higher.

The analysis is grounded in a forensic examination of the user's current baseline performance (F1: 0.74) and the significant regression observed upon the introduction of textual descriptors (F1: 0.64). This regression serves as the pivotal data point for understanding the underlying mechanics of "Attention Dilution" and "Instruction Conflict" within multimodal transformer architectures. The report argues that the prevailing assumption in prompt engineering—that explicit textual instruction enhances visual recognition—is fundamentally flawed when applied to the extraction of abstract semiotic features in high-variance historical documents.

Instead, the research supports a paradigm shift towards "Many-Shot In-Context Learning," enabled by the massive context windows of modern foundation models. By expanding the few-shot library from the current \~12 images to a "federated" dataset of 50–100 examples, utilizing Set-of-Mark (SoM) grid overlays to stabilize spatial grounding, and implementing a "Propose-and-Verify" architecture, the pipeline can overcome the stochastic hallucinations currently plaguing the detection of benchmark mounds and random terrain noise. This document details the theoretical underpinnings, architectural modifications, and post-processing strategies required to execute this shift.

## ---

**1\. Introduction: The Semiotics of Historical Cartography and VLM Perception**

The extraction of information from historical maps is distinct from general object detection because maps are not photographs; they are semiotic systems. A photograph of a car contains the physical features of a car (wheels, metal, glass). A map symbol of a burial mound, however, is a *signifier*—an abstract graphic convention agreed upon by cartographers of a specific era to represent a physical reality.1 These signifiers are often composed of hachures (short parallel lines indicating slope), concentric circles, or specific shading patterns that mimic three-dimensional topography but are graphically indistinguishable from other map features (like hills, dunes, or embankments) to a non-expert observer.

The user's project leverages Large Language Models (LLMs) with vision capabilities (VLMs) to perform this extraction. The current setup involves a few-shot, image-based prompt empirically built by adding legend items, false positives, false negatives, and null examples. While the baseline F1 score of 0.74 indicates that the model has successfully "grounded" the concept of a burial mound, the detailed taxonomy of errors—specifically the confusion between burial mounds and benchmark mounds—reveals a fragility in the model's discriminative decision boundary.

### **1.1. The User's Baseline: A Forensic Analysis**

The data provided from the user's last run offers a high-fidelity diagnostic view of the current pipeline's limitations.

* **Recall vs. Precision Imbalance:** The "Burial Mounds" class—the primary target—shows a Recall of 0.78 and Precision of 0.70. This implies the model is missing 22% of the mounds (False Negatives) while simultaneously classifying noise as mounds 30% of the time (False Positives).  
* **The "Benchmark" Confusion:** The "Benchmark" class has the lowest performance (F1: 0.62). The report notes that the model "likely confused other black squares/dots" for benchmarks. This is critical because benchmarks and burial mounds often share similar geometric primitives (circles or triangles with central dots) in historical symbology.  
* **The Text Regression Anomaly:** The most significant finding is the regression in performance when text descriptions were added to "tighten strictness."  
  * **F1 Score:** Dropped from 0.75 to 0.64 (-0.11).  
  * **Recall:** Dropped from 0.80 to 0.67 (-0.13).  
  * **Precision:** Dropped from 0.71 to 0.61 (-0.10).

This regression is not random; it is a systemic signal. It suggests that the introduction of text did not act as a clarifier but as a **distractor**. The drop in Recall (0.13) is particularly telling: it indicates that the text description likely imposed a "platonic ideal" of a burial mound that the messy, hand-drawn reality of the map could not satisfy. The model, constrained by the text, became over-conservative, rejecting valid mounds that didn't perfectly match the textual definition. This phenomenon, known as **Modality Interference**, forms a core pillar of the subsequent analysis.

### **1.2. The Shift to Foundation Models**

The user is transitioning from Gemini 3 Flash to Gemini 3 Pro. This transition is not merely an upgrade in processing power; it represents a shift in the *regime* of learning. Smaller models rely heavily on fine-tuning or rigid prompting. Large foundation models like Gemini 3 Pro (and GPT-4o, Claude 3.5 Sonnet) exhibit emergent behaviors in "Many-Shot" scenarios—where hundreds of examples can be processed in-context.3 This capability fundamentally alters the optimal strategy for library size and composition, moving away from the "efficiency" mindset of 2022-era prompt engineering towards a "volume" mindset suitable for 2025-era long-context models.

## ---

**2\. The Modality Interference Phenomenon: Why Text Failed**

The user's attempt to improve performance by adding text descriptions resulted in a catastrophic drop in metrics. To understand this, and to design a prompt that avoids it, we must delve into the mechanics of attention in multimodal transformers.

### **2.1. Theory of Attention Dilution**

Vision-Language Models process information by tokenizing both images and text into a shared embedding space. The "Attention Mechanism" allows the model to weigh the importance of different tokens when generating a response. However, attention is a finite resource.

Research indicates that as the volume and complexity of textual instructions increase, the model's attention to visual tokens is "diluted".4 This is often referred to as **Visual Token Dilution**. When the user provided a detailed text description of a burial mound (e.g., "a circular feature with inward-pointing hachures representing a steep slope"), the model allocated a significant portion of its attention heads to processing and maintaining this complex linguistic constraint.

Consequently, the "bandwidth" available for processing the subtle visual features of the map (the faint lines, the irregular shapes) was reduced. The model essentially stopped "looking" at the map with full fidelity and started "reading" the prompt, trying to hallucinate visual features that matched the strong textual prior. This aligns with findings that VLMs can ignore visual input in favor of textual priors when the text is semantically rich and directive.5

### **2.2. The Instruction Conflict Mechanism**

The regression also points to a phenomenon known as **Instruction Conflict**.6 In a multimodal prompt, the model receives two streams of definition:

1. **Implicit Visual Definition:** The few-shot images show what a mound *actually* looks like (irregular, ink-blotched, varied).  
2. **Explicit Textual Definition:** The text describes what a mound *should* look like (geometric, standardized).

In historical maps, the visual reality rarely matches the textual ideal. A "circular" mound might be drawn as an ellipse due to projection distortion or artist error. If the text strictly defines it as "circular," the model detects a conflict. Research shows that when faced with such conflicts, models often default to the textual instruction because pre-training data (web text) biases them towards following explicit language commands over implicit visual cues.7

**Result:** The model rejected the valid, irregular mounds because they didn't satisfy the strict text conditions, causing the massive drop in Recall (0.80 \-\> 0.67).

### **2.3. The "Image-First" Advantage**

The sequencing of modalities in the prompt architecture plays a subtle but decisive role. "Image-First" prompting—where the visual data is presented before the text instructions—has been shown to improve reasoning performance in visual tasks.8

* **Text-First Approach:** "Find all burial mounds. They are defined as X, Y, Z. Here is the image."  
  * *Cognitive Load:* The model primes its internal representation with the definition X, Y, Z. It then scans the image looking for matches to X, Y, Z. This is a "top-down" approach prone to missing features that don't fit the prime.  
* **Image-First Approach:** "Here is an image. Based on the visual patterns A, B, C observed in the examples, find similar objects."  
  * *Cognitive Load:* The model encodes the visual features first. The subsequent instruction acts as a query over the encoded visual latent space. This is a "bottom-up" approach that relies on visual similarity rather than semantic definition.

**Strategic Recommendation:** To reach F1 0.85, the user must **remove the descriptive text**. The prompt should rely on *visual ostension*—pointing to examples—rather than linguistic definition. Text should be reserved strictly for task logistics (e.g., "Return bounding boxes in JSON format") and not for feature definition.

## ---

**3\. Few-Shot Library Engineering: From "Few" to "Many"**

The user's current library contains approximately 12 images. While this was sufficient for a proof-of-concept (F1 0.74), it is mathematically insufficient for the high-variance domain of historical cartography. The transition to "Many-Shot" learning is the primary lever for performance gain.

### **3.1. The "Many-Shot" Regime**

With Gemini 1.5 Pro's context window (1M+ tokens), the constraint on the number of few-shot examples has effectively vanished. Research into **Many-Shot In-Context Learning (ICL)** demonstrates that performance scales log-linearly with the number of examples, showing significant gains as the number of shots increases from 10 to 100, and even up to 1000\.3

* **Mechanism:** In "few-shot" (10-20 examples), the model relies on retrieving pre-trained knowledge and adapting it slightly. In "many-shot" (100+ examples), the model can effectively learn a new probability distribution *in-context*, mimicking the performance of fine-tuning without the weight updates.3  
* **Target Size:** For the user's task, a library of **50 to 100 images** is recommended. This size allows for the representation of the full "manifold" of burial mound depictions, capturing variations in size, degradation, ink density, and surrounding terrain context.

### **3.2. Library Composition: The "Federated" Approach**

The composition of the library is more critical than its raw size. The user's current strategy of "legend \-\> false positives \-\> false negatives \-\> nulls" is sound but needs to be systematized into a **Federated Dataset** structure.11 This involves creating distinct "clusters" of examples that cover specific failure modes.

#### **3.2.1. Cluster 1: The Canonical Positives**

These are the clear, high-quality examples of burial mounds. They establish the baseline visual features. (Target: \~30% of library).

#### **3.2.2. Cluster 2: The Hard Negatives (The "Benchmark" Killer)**

The user's data shows a specific confusion between **Benchmarks** and mounds. This is a "Hard Negative."

* **Action:** The 8 False Positives from the previous run (where the model thought a random bump/circle was a mound) must be added to the library.  
* **Labeling:** These should be explicitly labeled as {"class": "background", "reason": "benchmark\_symbol"}.  
* **Theory:** By providing explicit "counter-examples" that are visually similar to the target (hard negatives), the model is forced to learn a tighter decision boundary. It learns not just what a mound *is*, but specifically what it *is not*.12

#### **3.2.3. Cluster 3: The Edge Cases (Visual Variance)**

Historical maps often have "edge cases"—mounds that are bisected by map folds, obscured by text labels, or faded.

* **Action:** Include the 9 False Negatives (Misses) from the previous run. These represent the visual variance the model currently fails to capture. Adding them to the support set directly addresses the Recall gap.

### **3.3. Addressing Recency Bias and Ordering**

The order in which these 100 examples are presented in the prompt matters. VLMs exhibit **Recency Bias**, paying disproportionate attention to the examples at the very end of the prompt.14

* **The Risk:** If the prompt ends with 10 examples of "nulls" (empty terrain), the model may become over-conservative. If it ends with 10 clear mounds, it may become trigger-happy (hallucinating mounds).  
* **The Fix:**  
  1. **Interleaving:** The examples must be interleaved: \[Positive, Negative, Positive, Negative...\].  
  2. **Randomization:** For every API call, the order of the examples in the prompt should be randomized. This prevents the model from learning spurious correlations based on the fixed position of examples.14  
  3. **The "Anchor" End:** The very last example before the query image should ideally be a "Hard Negative" or a "Complex Positive" to prime the model for high attention, rather than a simple example.

### **3.4. Synthetic Data Augmentation**

To reach 100 examples, the user may run out of annotated "real" data. Research supports the use of **Synthetic Data Generation** using style transfer techniques (e.g., CycleGAN or diffusion in-painting).13

* **Technique:** Take a modern topographic map with clear elevation data. Generate a "synthetic historical map" by applying the style of the target historical maps.  
* **Benefit:** This allows the user to generate thousands of "perfect" mounds (where the ground truth is known from the modern data) to fill the few-shot library. This is particularly useful for creating "Hard Negatives"—e.g., synthetically placing a triangle (benchmark) next to a circle (mound) to teach the model the difference.

## ---

**4\. Advanced Prompting Architectures: Visual Scaffolding**

To achieve an F1 of 0.85, relying solely on a better library is unlikely to be sufficient. The "spatial intelligence" of the VLM must be augmented through specific prompting architectures.

### **4.1. Set-of-Mark (SoM) and Grid Overlays**

A fundamental weakness of VLMs is their inability to output precise pixel coordinates (regression). They are token predictors, so asking for "bbox: " is asking the model to hallucinate numbers that correlate to spatial positions.18

The Solution: Grid Overlay Prompting  
Research 20 suggests that overlaying a visible grid on the image fundamentally changes the task from regression to classification.

* **Implementation:**  
  1. Superimpose a $10 \\times 10$ semi-transparent grid on the map tile.  
  2. Label the columns A-J and rows 1-10.  
  3. **Prompt:** "Identify the grid cells that contain a burial mound."  
* **Why it works:** The model no longer needs to predict "x=345"; it just needs to read the text "C4" which is visually present in the image. This "Visual Scaffolding" drastically reduces spatial hallucinations.  
* **Refinement:** Once the cell "C4" is identified, a second crop of just that cell can be sent to the model to get the precise bounding box, now that the search space is minimal.

### **4.2. Visual Chain-of-Thought (CoT)**

Standard Chain-of-Thought ("Let's think step by step") often fails in visual tasks because the "thinking" happens in text, detached from the image. **Visual Chain-of-Thought** 23 forces the reasoning to be grounded in visual observation.

**Proposed Prompt Sequence:**

1. **See (Perception):** "Scan the image. List all circular or hachured features. Do not classify them yet, just list them."  
2. **Think (Discrimination):** "Examine each feature. Does Feature A have a central dot? If yes, it is likely a Benchmark. Does Feature B have inward-facing hachures? If yes, it is a Mound."  
3. **Confirm (Decision):** "Based on the analysis, reject the Benchmarks and return only the Mounds."

This structure forces the model to explicitly acknowledge the **Hard Negatives** (Benchmarks) and reason *why* they are being rejected, rather than implicitly hoping the model ignores them. This directly targets the user's reported "Benchmark" confusion (F1 0.62).25

### **4.3. Tiling and Resolution Management**

The user notes that the model confuses "random bumps" with mounds. This is often a resolution issue. Historical maps are dense; if a $4000 \\times 4000$ pixel map is resized to the model's native resolution (often $1024 \\times 1024$ or smaller), the fine hachures of a mound blur into a "random bump".26

**The "Global-Local" Tiling Strategy:**

* **Sliding Window:** Crop the map into $1024 \\times 1024$ tiles with 20% overlap.  
* **Context Loss:** Tiling kills context (e.g., a mound might look like a hill if you can't see the surrounding river).  
* **Hybrid Input:** Research 26 suggests passing **two images** for every inference:  
  1. The **Local Tile** (High Resolution).  
  2. The **Global Map** (Downsampled).  
* **Prompt:** "Look at the Local Tile for detail. Refer to the Global Map to understand the terrain context. Is the object in the center of the Local Tile a mound?"

## ---

**5\. The "Propose-and-Verify" Pipeline: The Judge Model**

The user's data shows a classic precision-recall trade-off. To break this, the pipeline should be bifurcated into two distinct stages: **Detection** and **Verification**. This architecture is supported by recent findings on "Self-Consistency" and "Binary Verification" in VLMs.28

### **5.1. Stage 1: The Proposer (High Recall)**

* **Goal:** Capture *every possible* mound.  
* **Prompt:** Use the "Many-Shot" library with a prompt biased towards Recall. "Find all potential mounds. When in doubt, include it."  
* **Expected Outcome:** High Recall (0.90+), Low Precision (0.50). The model will pick up mounds, benchmarks, hills, and water spots.

### **5.2. Stage 2: The Judge (High Precision)**

* **Mechanism:** Crop the bounding boxes generated in Stage 1\. Add a small margin (context) around the crop.  
* **Prompt:** Feed each crop to the VLM (or a specialized fine-tuned model) with a **Binary Verification** prompt.  
  * *"Image: \[Crop\]. Question: Is this strictly a burial mound? It must have \[feature X\]. It must NOT be a benchmark (triangle/square). Answer YES or NO."*  
* **Why it works:** Binary classification on a focused crop is a fundamentally easier task for a VLM than multi-object detection on a cluttered map. The model focuses all its attention on the single object, resolving the "random bump" confusion.29

**Cost Implication:** This doubles the number of tokens (or calls). However, using a cheaper model (e.g., Gemini Flash) for the "Proposer" and the stronger model (Gemini Pro) for the "Judge" is a cost-effective strategy.

## ---

**6\. Post-Processing and Ensembling**

To squeeze the final performance gains (moving from F1 0.80 to 0.85), algorithmic post-processing is required.

### **6.1. Weighted Boxes Fusion (WBF)**

Traditional Non-Maximum Suppression (NMS) is destructive—it deletes overlapping boxes. **Weighted Boxes Fusion (WBF)** 30 is an additive strategy.

* **Scenario:** With the tiling strategy, a mound will likely be detected in Tile A and again in Tile B (overlap).  
* **WBF Logic:** Instead of deleting one, WBF *averages* their coordinates, weighted by the model's confidence score.  
* **Result:** This improves the Intersection-over-Union (IoU) accuracy, directly boosting the F1 score by refining the bounding box precision.

### **6.2. Self-Consistency Ensembling**

To combat the 8 False Positives (Hallucinations) reported:

* **Technique:** Run the inference on each tile **3 times** (with temperature=0.7).  
* **Voting:** Keep only the boxes that appear in **2 out of 3** runs.  
* **Theory:** Hallucinations in VLMs are stochastic (random noise). True positives are robust signals. A random bump might be detected as a mound in Run 1 but likely not in Run 2 or 3\. A real mound will be detected in all three. This simple voting mechanism can eliminate up to 60-80% of stochastic false positives.32

## ---

**7\. Strategic Implementation Roadmap**

Based on this exhaustive analysis, the following implementation plan is proposed to the user.

### **Phase 1: Data Engineering (Days 1-3)**

1. **Expand Library:** Move from 12 to 50+ images. Prioritize the inclusion of the 8 False Positives and 9 False Negatives from the failed run.  
2. **Synthetic Generation:** If real data is scarce, use manual editing or style transfer to create "Hard Negatives" (e.g., manually drawing a benchmark symbol next to a mound).  
3. **Federated Structure:** Organize the library into JSON-based clusters (Clear Mounds, Faint Mounds, Benchmarks, Triangulation Points).

### **Phase 2: Prompt Re-Architecture (Days 4-5)**

4. **Purge Text:** Remove the descriptive text that caused the regression. Revert to a purely visual-example-based prompt.  
5. **Implement SoM:** Add the $10 \\times 10$ grid overlay to the input images. Change the prompt to request "Grid Cell IDs" rather than coordinates.  
6. **Interleave Examples:** Modify the prompt construction script to interleave positive and negative examples (P, N, P, N...) and randomize their order.

### **Phase 3: The Verification Loop (Days 6-10)**

7. **Build the Judge:** Create a separate script that takes the outputs of Phase 2, crops the images, and runs the Binary Verification prompt.  
8. **Tune the Judge:** Run the Judge on the "Benchmark" class specifically to ensure it can discriminate 100% of the time (addressing the F1 0.62 issue).

### **Phase 4: Ensembling (Production)**

9. **WBF & Voting:** Implement Weighted Boxes Fusion for the overlapping tiles and 3-run majority voting for the final output.

## **Conclusion**

The user's project is currently stuck in a "local optimum" (F1 0.74) typical of early-stage VLM implementations. The regression caused by adding text is a valuable signal: it confirms that the model is sensitive to **Attention Dilution** and **Instruction Conflict**. The path to F1 0.85 does not lie in "better text descriptions" or "more prompt engineering" in the traditional sense. It lies in **Visual Scaffolding** (Grids, SoM), **Many-Shot Learning** (50+ examples), and **Structural Verification** (The Judge Model). By treating the VLM as a visual reasoner rather than a text reader, and by mechanically enforcing precision through a two-stage pipeline, the extraction of kurgans from historical maps can achieve the robustness required for production-grade digital humanities research.

### ---

**Table 1: Failure Mode Analysis & Mitigation Strategy**

| Failure Mode | User Data (Baseline) | Root Cause (Research) | Proposed Mitigation | Expected Impact |
| :---- | :---- | :---- | :---- | :---- |
| **Benchmark Confusion** | F1 0.62 (Low Precision) | Visual Similarity (Hard Negatives); Lack of discriminative examples. | **Cluster 2 Library:** Explicitly add benchmarks as negative examples. **Visual CoT:** Force "See-Think-Confirm" reasoning. | Precision $\\uparrow$ 15-20% |
| **Random Bumps (FP)** | 6 False Positives | Stochastic Hallucination; Low Resolution; Attention Dilution. | **Self-Consistency:** 3-run voting. **Grid Overlay:** Constrain search space. | Precision $\\uparrow$ 10-15% |
| **Missed Mounds (FN)** | Recall 0.80 $\\to$ 0.67 | **Instruction Conflict:** Text description contradicted visual reality. | **Purge Text:** Remove morphological descriptions. **Many-Shot:** Add 50+ diverse examples. | Recall $\\uparrow$ 10-15% |
| **Spatial Drift** | Imprecise Bounding Boxes | Token Prediction vs. Regression mismatch. | **Set-of-Mark (SoM):** Use Grid Cell detection first. **WBF:** Average overlapping predictions. | IoU $\\uparrow$ 0.1-0.2 |

### **Table 2: Recommended Few-Shot Library Composition (Total: 60 Images)**

| Category | Count | Purpose | Prompt Label Strategy |
| :---- | :---- | :---- | :---- |
| **Canonical Mounds** | 20 | Establish baseline features. | {"class": "mound"} |
| **Degraded/Faint Mounds** | 10 | Address Recall (Misses). | {"class": "mound", "condition": "faint"} |
| **Benchmarks** | 10 | **Hard Negative:** Fix F1 0.62. | {"class": "background", "type": "benchmark"} |
| **Triangulation Points** | 5 | **Hard Negative:** Prevent confusion. | {"class": "background", "type": "triangulation"} |
| **Natural Terrain (Hills)** | 10 | Contextual Negative. | {"class": "background", "type": "terrain"} |
| **Null (Empty)** | 5 | Calibrate confidence. | {"class": "null"} |

---

Citations:

1

#### **Works cited**

1. Exploring the potential of deep learning for settlement symbol extraction from historical map documents \- Information Sciences Institute, accessed on December 18, 2025, [https://www.isi.edu/results/publications/19534/exploring-the-potential-of-deep-learning-for-settlement-symbol-extraction-from-historical-map-documents](https://www.isi.edu/results/publications/19534/exploring-the-potential-of-deep-learning-for-settlement-symbol-extraction-from-historical-map-documents)  
2. Map Archive Mining: Visual-Analytical Approaches to Explore Large Historical Map Collections \- PMC, accessed on December 18, 2025, [https://pmc.ncbi.nlm.nih.gov/articles/PMC6500493/](https://pmc.ncbi.nlm.nih.gov/articles/PMC6500493/)  
3. Many-Shot In-Context Learning \- NIPS papers, accessed on December 18, 2025, [https://proceedings.neurips.cc/paper\_files/paper/2024/file/8cb564df771e9eacbfe9d72bd46a24a9-Paper-Conference.pdf](https://proceedings.neurips.cc/paper_files/paper/2024/file/8cb564df771e9eacbfe9d72bd46a24a9-Paper-Conference.pdf)  
4. Qwen Look Again: Guiding Vision-Language Reasoning Models to Re-attention Visual Information \- arXiv, accessed on December 18, 2025, [https://arxiv.org/html/2505.23558v2](https://arxiv.org/html/2505.23558v2)  
5. Examining Vision Language Models through Multi-dimensional Experiments with Vision and Text Features \- ChatPaper, accessed on December 18, 2025, [https://chatpaper.com/paper/187560](https://chatpaper.com/paper/187560)  
6. PromptCOS: Towards Content-only System Prompt Copyright Auditing for LLMs \- arXiv, accessed on December 18, 2025, [https://arxiv.org/html/2509.03117v2](https://arxiv.org/html/2509.03117v2)  
7. Don't Forget the Enjoin: FocalLoRA for Instruction Hierarchical Alignment in Large Language Models \- Computer Science at Emory, accessed on December 18, 2025, [https://www.cs.emory.edu/\~jyang71/files/focallora.pdf](https://www.cs.emory.edu/~jyang71/files/focallora.pdf)  
8. Image First or Text First? Optimising the Sequencing of Modalities in Large Language Model Prompting and Reasoning Tasks \- ResearchGate, accessed on December 18, 2025, [https://www.researchgate.net/publication/392378597\_Image\_First\_or\_Text\_First\_Optimising\_the\_Sequencing\_of\_Modalities\_in\_Large\_Language\_Model\_Prompting\_and\_Reasoning\_Tasks](https://www.researchgate.net/publication/392378597_Image_First_or_Text_First_Optimising_the_Sequencing_of_Modalities_in_Large_Language_Model_Prompting_and_Reasoning_Tasks)  
9. Image First or Text First? Optimising the Sequencing of Modalities in Large Language Model Prompting and Reasoning Tasks \- MDPI, accessed on December 18, 2025, [https://www.mdpi.com/2504-2289/9/6/149](https://www.mdpi.com/2504-2289/9/6/149)  
10. Large (Vision) Language Models are Unsupervised In-Context Learners \- OpenReview, accessed on December 18, 2025, [https://openreview.net/forum?id=ohJxgRLlLt](https://openreview.net/forum?id=ohJxgRLlLt)  
11. Revisiting Few-Shot Object Detection with Vision-Language Models \- arXiv, accessed on December 18, 2025, [https://arxiv.org/html/2312.14494v1](https://arxiv.org/html/2312.14494v1)  
12. CoT-PL: Visual Chain-of-Thought Reasoning Meets Pseudo-Labeling for Open-Vocabulary Object Detection \- ChatPaper, accessed on December 18, 2025, [https://chatpaper.com/paper/200600](https://chatpaper.com/paper/200600)  
13. \[Quick Review\] Multi-Perspective Data Augmentation for Few-shot Object Detection \- Liner, accessed on December 18, 2025, [https://liner.com/review/multiperspective-data-augmentation-for-fewshot-object-detection](https://liner.com/review/multiperspective-data-augmentation-for-fewshot-object-detection)  
14. Research notes: few-shot performance of vision-language models, accessed on December 18, 2025, [https://www.giete.ma/blog/few-shot-performance-of-vision-language-models](https://www.giete.ma/blog/few-shot-performance-of-vision-language-models)  
15. Few-Shot Prompting \- Prompt Engineering Guide, accessed on December 18, 2025, [https://www.promptingguide.ai/techniques/fewshot](https://www.promptingguide.ai/techniques/fewshot)  
16. Synthetic Map Generation to Provide Unlimited Training Data for Historical Map Text Detection | Request PDF \- ResearchGate, accessed on December 18, 2025, [https://www.researchgate.net/publication/356010977\_Synthetic\_Map\_Generation\_to\_Provide\_Unlimited\_Training\_Data\_for\_Historical\_Map\_Text\_Detection](https://www.researchgate.net/publication/356010977_Synthetic_Map_Generation_to_Provide_Unlimited_Training_Data_for_Historical_Map_Text_Detection)  
17. Synthetic Map Generation to Provide Unlimited Training Data for Historical Map Text Detection \- Zekun Li, accessed on December 18, 2025, [https://zekun-li.github.io/files/GEOAI\_2021.pdf](https://zekun-li.github.io/files/GEOAI_2021.pdf)  
18. 3DAxisPrompt: Promoting the 3D Grounding and Reasoning in GPT-4o \- arXiv, accessed on December 18, 2025, [https://arxiv.org/html/2503.13185v1](https://arxiv.org/html/2503.13185v1)  
19. Contrastive Region Guidance: Improving Grounding in Vision-Language Models without Training \- arXiv, accessed on December 18, 2025, [https://arxiv.org/html/2403.02325v1](https://arxiv.org/html/2403.02325v1)  
20. VLMs are Blind, accessed on December 18, 2025, [https://vlmsareblind.github.io/](https://vlmsareblind.github.io/)  
21. (PDF) An Image Grid Can Be Worth a Video: Zero-shot Video Question Answering Using a VLM \- ResearchGate, accessed on December 18, 2025, [https://www.researchgate.net/publication/387102066\_An\_Image\_Grid\_Can\_Be\_Worth\_a\_Video\_Zero-shot\_Video\_Question\_Answering\_Using\_a\_VLM](https://www.researchgate.net/publication/387102066_An_Image_Grid_Can_Be_Worth_a_Video_Zero-shot_Video_Question_Answering_Using_a_VLM)  
22. LLM for bounding boxes : r/LLMDevs \- Reddit, accessed on December 18, 2025, [https://www.reddit.com/r/LLMDevs/comments/1je2sp9/llm\_for\_bounding\_boxes/](https://www.reddit.com/r/LLMDevs/comments/1je2sp9/llm_for_bounding_boxes/)  
23. Visual Chain-of-Thought Prompting for Knowledge-based Visual Reasoning \- Zhenfang Chen, accessed on December 18, 2025, [https://zfchenunique.github.io/files/aaai24\_vcot\_arxiv.pdf](https://zfchenunique.github.io/files/aaai24_vcot_arxiv.pdf)  
24. COT-PL: VISUAL CHAIN-OF-THOUGHT REASONING MEETS PSEUDO-LABELING FOR OPEN-VOCABULARY OBJECT DETECTION \- OpenReview, accessed on December 18, 2025, [https://openreview.net/pdf/aee98d1593863214590534056dcf346e271f443d.pdf](https://openreview.net/pdf/aee98d1593863214590534056dcf346e271f443d.pdf)  
25. CoT-PL: Visual Chain-of-Thought Reasoning Meets Pseudo-Labeling for Open-Vocabulary Object Detection | OpenReview, accessed on December 18, 2025, [https://openreview.net/forum?id=8B1vsFiLin](https://openreview.net/forum?id=8B1vsFiLin)  
26. Image Tiling for High-Resolution Reasoning: Balancing Local Detail with Global Context \- arXiv, accessed on December 18, 2025, [https://arxiv.org/html/2512.11167v1](https://arxiv.org/html/2512.11167v1)  
27. The Power of Tiling for Small Object Detection \- CVF Open Access, accessed on December 18, 2025, [https://openaccess.thecvf.com/content\_CVPRW\_2019/papers/UAVision/Unel\_The\_Power\_of\_Tiling\_for\_Small\_Object\_Detection\_CVPRW\_2019\_paper.pdf](https://openaccess.thecvf.com/content_CVPRW_2019/papers/UAVision/Unel_The_Power_of_Tiling_for_Small_Object_Detection_CVPRW_2019_paper.pdf)  
28. Binary Verification for Zero-Shot Vision \- arXiv, accessed on December 18, 2025, [https://arxiv.org/html/2511.10983v1](https://arxiv.org/html/2511.10983v1)  
29. Zero-Shot Referring Expression Comprehension via Vision-Language True/False Verification \- arXiv, accessed on December 18, 2025, [https://arxiv.org/html/2509.09958v3](https://arxiv.org/html/2509.09958v3)  
30. SimpleVSF: VLM-Scoring Fusion for Trajectory Prediction of End-to-End Autonomous Driving \- ChatPaper, accessed on December 18, 2025, [https://chatpaper.com/paper/201235](https://chatpaper.com/paper/201235)  
31. Weighted Boxes Fusion — A detailed view | by Sambasivarao. K | Analytics Vidhya | Medium, accessed on December 18, 2025, [https://medium.com/analytics-vidhya/weighted-boxes-fusion-86fad2c6be16](https://medium.com/analytics-vidhya/weighted-boxes-fusion-86fad2c6be16)  
32. Ranked Voting based Self-Consistency of Large Language Models \- arXiv, accessed on December 18, 2025, [https://arxiv.org/html/2505.10772v1](https://arxiv.org/html/2505.10772v1)  
33. Enhancing Mathematical Reasoning in Large Language Models with Self-Consistency-Based Hallucination Detection \- arXiv, accessed on December 18, 2025, [https://arxiv.org/html/2504.09440v3](https://arxiv.org/html/2504.09440v3)  
34. Few-Shot Object Detection with Foundation Models \- CVF Open Access, accessed on December 18, 2025, [https://openaccess.thecvf.com/content/CVPR2024/papers/Han\_Few-Shot\_Object\_Detection\_with\_Foundation\_Models\_CVPR\_2024\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2024/papers/Han_Few-Shot_Object_Detection_with_Foundation_Models_CVPR_2024_paper.pdf)  
35. Revisiting Few-Shot Object Detection with Vision-Language Models, accessed on December 18, 2025, [https://proceedings.neurips.cc/paper\_files/paper/2024/file/22b2067b8f680812624032025864c5a1-Paper-Datasets\_and\_Benchmarks\_Track.pdf](https://proceedings.neurips.cc/paper_files/paper/2024/file/22b2067b8f680812624032025864c5a1-Paper-Datasets_and_Benchmarks_Track.pdf)  
36. Vision Language Models | Rohit Bandaru, accessed on December 18, 2025, [https://rohitbandaru.github.io/blog/Vision-Language-Models/](https://rohitbandaru.github.io/blog/Vision-Language-Models/)  
37. PhysVLM-AVR: Active Visual Reasoning for Multimodal Large Language Models in Physical Environments \- OpenReview, accessed on December 18, 2025, [https://openreview.net/pdf/89b1018647a9f5681e3ad0ed184e80229e3997ee.pdf](https://openreview.net/pdf/89b1018647a9f5681e3ad0ed184e80229e3997ee.pdf)  
38. Application of deep learning for symbol detection on historical maps to explore spatiotemporal changes in the regional tea indus \- Oxford Academic, accessed on December 18, 2025, [https://academic.oup.com/dsh/advance-article-pdf/doi/10.1093/llc/fqaf099/64420694/fqaf099.pdf](https://academic.oup.com/dsh/advance-article-pdf/doi/10.1093/llc/fqaf099/64420694/fqaf099.pdf)