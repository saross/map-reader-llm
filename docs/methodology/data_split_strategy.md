# Formal Machine Learning Methodology (Remote Sensing)

**Objective**: Ensure statistical rigor for the final publication by separating "tuning" data from "reporting" data.

## 1. Dataset Overview
*   **Total Corpus**: 361 Tiled Images (1km x 1km approx).
*   **Source**: 4 Map Sheets (Rakovski, Lesovo, Elenovo, 32635).

## 2. The Three-Split Protocol
Standard ML practice is to divide data into three distinct buckets.

### A. Training & Development Set (The "Lab" Set)
*   **Size**: **20 Tiles** (The "Original 20").
*   **Composition**: A stratified sample representing ~5% of the corpus.
*   **Usage**: 
    1.  **Prompt Engineering**: All few-shot examples (the "teaching material") are cropped from these 20 tiles.
    2.  **Iterative Tuning**: We benchmark newly engineered prompts against *this same set* to measure improvement.
*   **Status**: **Biased/Burned**. Since the prompt is explicitly designed to solve *these* tiles, performance here will be higher than on unseen data. This is expected.

### B. Test / Holdout Set (The "Safety Check")
*   **Size**: **20 NEW Tiles** (~5%).
*   **Role**: **Intermediate Verification**.
*   **Why do we need this?** Before we commit to the full "Production Run" (which consumes time/quota and generates massive data), we run this small, unbiased set to confirm our prompt works on data it has never seen.
*   **Publication Usage**: We report these numbers as "Preliminary Validation" or "Pilot Performance".

### C. Production Run (The "Archaeological Result")
*   **Size**: **All Remaining Tiles** (~321 tiles).
*   **Role**: **Final Deployment**.
*   **Publication Usage**: 
    1.  **Global Metrics**: Since we have Ground Truth for the whole area, we can report the *true* accuracy of the method (n=321). This is the gold standard.
    2.  **Discovery**: We analyze the False Positives to see if we found *new* unmapped mounds (the archeological goal).
    3.  **Spatial Analysis**: We map the distribution of mounds across the landscape.

**Summary**: 
*   **Dev Set** = "Build the tool."
*   **Test Set** = "Verify the tool works."
*   **Production** = "Use the tool to do Science."

## 3. Revised Plan of Action
1.  **Restoration**: I have restored the full **20-tile Development Set** to `inputs/target_tiles_manifest.json`.
2.  **Tuning (Phase 3)**: We will continue optimizing the "Hybrid" prompt using this 20-tile set.
3.  **Future**: When we are happy with v3.x, we will define the 20-tile Test Set.

## 4. Scaling Strategy: The 80-Map Corpus
You noted that our 4 maps are a "Gold Standard" sample of a larger 80-map corpus with noisy (student) labels (6-7% error).

### The Challenge
We cannot benchmark against the 80 maps directly because the "Ground Truth" is unreliable. If the Model disagrees with a Student, the Student might be wrong.

### The Solution: "Disagreement Sampling"
1.  **Prove the Tool (The 4 Maps)**: We use our current "Gold Standard" dataset (361 tiles) to rigorously prove the model's Precision and Recall. This satisfies the "Methodology" section of the paper.
2.  **Apply the Tool (The 80 Maps)**: We run the proven model on the remaining 76 maps.
3.  **Audit the Students (The "Results" Section)**:
    *   **Student Error Profile**: Your review indicates students have extremely high Precision (very few False Positives) but suffer from **False Negatives** (missed mounds).
    *   **The AI Role**: This is the perfect complement. The AI (High Recall) acts as a "safety net" to catch what the students missed.
    *   **Disagreement Analysis**: We specifically target **Type A Disagreements** (Model says "Mound", Student says "Nothing"). Verification of these should yield a high number of "New Discoveries".

**Conclusion**: The AI complements the human annotators by solving their primary weakness (Recall/Fatigue), transforming the 80-map dataset into a verified archaeological resource.
