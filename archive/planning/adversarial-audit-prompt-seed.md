# Adversarial Results Audit: Prompt Seed for CC

## Framing

Our text-only VLM pipeline reports F1 > 0.9 for point symbol detection on degraded Soviet topographic maps, using Gemini 3 Flash with zero visual training examples. This result, if correct, substantially exceeds every published benchmark for point symbol detection on historical maps (best prior: F1 = 0.73, DARPA CriticalMAAS, using a trained U-Net with abundant annotated data). It also exceeds the best published result for any map symbol extraction task (U-Net wetland segmentation, F1 = 0.886).

**We assume this result contains an error.** Your task is to find it. The error may be small or large, subtle or obvious, in the data, code, pipeline, configuration, metric calculation, or evaluation methodology. Small errors can mask larger ones, so investigate every anomaly — not only those that would directly inflate F1.

## Audit Scope

Examine every layer of the pipeline, working from ground truth through to final metrics. For each layer, document what you checked, what you found, and your confidence that it is correct.

### Layer 1: Ground Truth Integrity

- Are ground truth annotations complete and consistent across all 4 maps?
- Are there duplicate annotations (same mound annotated twice)?
- Are there missing annotations (mounds visible on map but not in ground truth)?
- Do annotation coordinates correctly align with tile pixel coordinates after tiling?
- When tiles are generated at 384px vs 512px, does the ground truth correctly re-map to the new tile boundaries?
- Are edge-of-tile mounds handled consistently (included in one tile only, or counted in overlapping tiles)?
- How many ground truth symbols are in the production set? Is this number consistent across all reports?

### Layer 2: Tile Generation and Coverage

- Do the 384px and 512px tile sets cover exactly the same geographic area?
- Is the overlap/stride correctly implemented for both tile sizes?
- Are any ground truth symbols lost in the gaps between tiles?
- Are training/calibration tiles correctly excluded from the production evaluation set?
- Verify the exact tile counts: how many tiles at each size, how many excluded, how many evaluated?

### Layer 3: API Response Parsing

- Are raw API responses archived for spot-checking?
- Does the parser correctly extract all detections from every response?
- Are there edge cases where the model returns unexpected formats that the parser silently drops or mishandles?
- For the consensus proposer + adversarial verifier pipeline: are proposer and verifier responses correctly paired and reconciled?
- Are any tiles silently skipped (API timeout, rate limit, malformed response)?
- Check: does the number of tiles with parsed results exactly match the number of tiles submitted?

### Layer 4: Spatial Matching (Hungarian Algorithm)

- Is the spatial tolerance correctly calculated in metres (not pixels)?
- Verify the pixel-to-metre conversion factor for both 384px and 512px tiles.
- Is the Hungarian algorithm implementation correct? Test with known inputs.
- At 30m tolerance, what is the maximum pixel distance allowed? Is this correctly computed for both tile sizes?
- Are detections matched one-to-one (no double-counting)?
- What happens when a detection falls exactly on the tolerance boundary?
- **Critical check**: run the matching at 1m, 5m, 10m, 15m, 20m, 25m, 30m, 40m, 50m and plot the full spatial tolerance curve. Does the curve behave monotonically? Does it plateau where expected?

### Layer 5: Metric Calculation

- Verify F1, precision, and recall calculations from raw TP/FP/FN counts.
- Are TP + FN = total ground truth symbols? If not, why not?
- Are empty tiles (no ground truth, no detections) excluded from F1 calculation, or do they contribute?
- For consensus voting: is the voting threshold correctly applied before matching, not after?
- **Spot-check**: select 5 random tiles, manually verify the detections against ground truth, confirm TP/FP/FN counts match the pipeline output.

### Layer 6: Configuration and Pipeline Integrity

- Is the configuration that produced F1 > 0.9 exactly reproducible? Re-run it on a subset (e.g., 20 tiles) and confirm identical results.
- Are there any cached results, intermediate files, or stale outputs that could contaminate the evaluation?
- Verify that the text-only prompt files used contain no embedded images or image references.
- Confirm the model called is actually Gemini 3 Flash (check API response metadata for model version strings).
- Is the adversarial verifier using the same prompt as the proposer, or a different one? Document exactly what differs.

### Layer 7: Cross-Configuration Consistency

- Do worse-performing configurations (e.g., image-inclusive, single-pass) produce results consistent with expectations?
- If text-only F1 > 0.9 but text+image F1 = 0.6, that's suspicious — the image shouldn't hurt that much. Check for configuration contamination.
- Does single-pass (no voting) performance sit in a plausible range given the voted result?
- Are the 384px and 512px results internally consistent (384px better, as reported)?

### Layer 8: Statistical Validity

- How many independent runs contribute to the F1 > 0.9 figure?
- What are the bootstrap CIs? Are they computed correctly (check bootstrap implementation)?
- Is there any multiple-comparisons issue? How many configurations were tested in total?
- Does FDR correction (preregistered at q = 0.05) change which results are significant?

## Specific Failure Modes to Investigate

These are ways F1 could be artificially inflated. Check each one explicitly:

1. **Ground truth leakage**: Are any ground truth coordinates visible to the model (e.g., baked into tile filenames, embedded in metadata)?
2. **Tolerance inflation**: Is 30m / 6px actually correct, or has a unit conversion error made the tolerance larger than intended?
3. **Double-counting TPs**: Could a single detection match multiple ground truth points, or vice versa?
4. **Selective tile exclusion**: Are tiles where the model performs poorly being silently dropped (e.g., due to API errors that correlate with difficult tiles)?
5. **Contamination between proposer and verifier**: Does the verifier see the proposer's detections in a way that biases it toward confirmation rather than genuine adversarial rejection?
6. **Empty tile inflation**: If empty tiles (no mounds, no detections) are counted as perfect performance, this inflates F1. Verify how empty tiles are handled.
7. **Training tile inclusion**: Confirm — with tile IDs — that no calibration/training tiles are in the production evaluation set.
8. **Stale results**: Could the reported metrics come from a previous run with different parameters?

## Output Format

For each layer, report:
- **Status**: PASS (verified correct) / CONCERN (potential issue found) / FAIL (confirmed error)
- **Evidence**: What you checked and what you found
- **Impact on F1**: If a concern or failure, estimate the direction and magnitude of impact on the reported F1

Conclude with an overall assessment: given everything checked, what is your confidence that F1 > 0.9 is a genuine result?
