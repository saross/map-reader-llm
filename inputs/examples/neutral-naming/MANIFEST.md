# Neutral Filename Mapping

Symlinks with neutral names to prevent semantic leakage in image-only prompts.

| Neutral Name | Actual File | Type | Source |
|--------------|-------------|------|--------|
| example_01.png | legend-positive/burial_mound.png | Positive | Legend |
| example_02.png | legend-positive/settlement_mound.png | Positive | Legend |
| example_03.png | legend-positive/triangulation_mound.png | Positive | Legend |
| example_04.png | legend-positive/benchmark_mound.png | Positive | Legend |
| example_05.png | null-tiles/null_lesovo.png | Negative (null) | Training tile (empty) |
| example_06.png | null-tiles/null_elenovo.png | Negative (null) | Training tile (empty) |
| example_07.png | null-tiles/null_32635.png | Negative (null) | Training tile (empty) |
| example_08.png | legend-negative/standalone_triangulation.png | Negative (hard) | Legend |
| example_09.png | legend-negative/standalone_benchmark.png | Negative (hard) | Legend |

## Usage

- **Baseline** (`detect_image-only.json`): examples 01-07
- **Hard negatives** (`detect_image-only_hardneg.json`): examples 01-09

## Notes

Hard negatives (examples 08-09) are legend symbols that visually resemble mound
markers but represent standalone survey markers (triangulation point, bench mark)
without an associated mound.
