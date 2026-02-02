# Superseded Hard Negative Crops (512×512)

**Superseded**: 2026-02-02 (Session 8)

**Reason**: These were the original hard negative crops from commit `12898e9` (2026-02-01). The selections themselves remain correct (same 4 vote-5/5 hallucinations), but the crops were 512×512 extractions from detection tiles. They were re-extracted as 128×128 crops centred on the FP detection coordinate from full map GeoTIFFs, consistent with the hard positive extraction method (errata E8).

| File | Subtype | Map | Nearest Ref. | Status |
|------|---------|-----|-------------|--------|
| example_11_rakovski.png | burial_mound | Rakovski | 1896.0m | Re-extracted as 128×128 from GeoTIFF |
| example_12_lesovo.png | triangulation_mound | Lesovo | 1807.8m | Re-extracted as 128×128 from GeoTIFF |
| example_13_k-35-052-4.png | burial_mound | K-35-052-4 | 872.9m | Re-extracted as 128×128 from GeoTIFF |
| example_14_elenovo.png | burial_mound | Elenovo | 725.0m | Re-extracted as 128×128 from GeoTIFF |

See `inputs/examples/neutral-naming/MANIFEST.md` for current crop provenance.
