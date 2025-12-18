# Prompt Refinement and Validation Plan

The goal is to validate the V2.5 Mound Detection Prompt, which aims to reduce false positives (specifically "Label Confusion" and "Black Blobs") by refining the model's instructions.

## Proposed Changes

### [Detection Logic](file:///home/shawn/Code/map-reader-llm/scripts/2_detect_mounds.py)
#### [MODIFY] [2_detect_mounds.py](file:///home/shawn/Code/map-reader-llm/scripts/2_detect_mounds.py)
- Update `detect_mounds` function signature to accept `prompt_path` (optional).
- Start using `prompts/V2.5_mound_detection_prompt.md` as the default or passed argument.
- If `prompt_path` is provided, read the system instruction/prompt from the file instead of the hardcoded string.
- Update the system instruction loading to use the text from the file.

### [Test Script](file:///home/shawn/Code/map-reader-llm/scripts/test_detection_v2.py)
#### [MODIFY] [test_detection_v2.py](file:///home/shawn/Code/map-reader-llm/scripts/test_detection_v2.py)
- Update the call to `detect_mounds` to pass `prompt_path="prompts/V2.5_mound_detection_prompt.md"`.

## Verification Plan

### Automated Tests
- Run `python scripts/test_detection_v2.py`
    - This will process the specific problem tile: `K-35-062-2_Rakovski_x2688_y3136.png`.
    - Output: `test_v2.5_x2688_y3136.geojson`.

### Manual Verification
- Inspect `test_v2.5_x2688_y3136.geojson` (content) to see if "Label Confusion" (boxing numbers) has been reduced.
- Ideally, the number of detections should decrease if we are successfully filtering false positives, or remain stable but with better bounding boxes.
