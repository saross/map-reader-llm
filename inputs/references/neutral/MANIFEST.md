# Neutral Filename Mapping

Symlinks with neutral names to prevent semantic leakage in image-only prompts.

| Neutral Name | Actual File | Type | Source |
|--------------|-------------|------|--------|
| example_01.png | burial_mound.png | Positive | Legend |
| example_02.png | settlement_mound.png | Positive | Legend |
| example_03.png | triangulation_mound.png | Positive | Legend |
| example_04.png | benchmark_mound.png | Positive | Legend |
| example_05.png | null_lesovo.png | Negative (null) | Training tile (empty) |
| example_06.png | null_elenovo.png | Negative (null) | Training tile (empty) |
| example_07.png | null_32635.png | Negative (null) | Training tile (empty) |
| example_08.png | ref_neg_benchmark.png | Negative (hard) | Legend |
| example_09.png | ref_neg_triangulation.png | Negative (hard) | Legend |

## Usage

- **Baseline** (`detect_image-only.json`): examples 01-07
- **Hard negatives** (`detect_image-only-hardneg.json`): examples 01-09
