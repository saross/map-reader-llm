# Superseded Hard Positive Crops (512×512)

**Superseded**: 2026-02-02 (Session 7)

**Reason**: These were the original hard positive crops from commit `12898e9` (2026-02-01). Three of four (examples 05–07) were boundary-effect artefacts — the reference mounds fell outside all calibration tile polygons, so the model never saw them. They were not genuine recognition failures.

**Replaced by**: 128×128 crops centred on confirmed in-tile recognition failures, extracted from full map GeoTIFFs (errata E8). The replacement files use different map sheet names for examples 06 and 07 (Elenovo and Rakovski replace Lesovo and K-35-052-4).

| File | fid | Map | Status | Reason |
|------|-----|-----|--------|--------|
| example_05_rakovski.png | 354 | Rakovski | Out of scope | Reference outside all calibration tiles |
| example_06_lesovo.png | 249 | Lesovo | Out of scope | Reference outside all calibration tiles |
| example_07_k-35-052-4.png | 556 | K-35-052-4 | Out of scope | Reference outside all calibration tiles |
| example_08_elenovo.png | 105 | Elenovo | Re-extracted | Confirmed in-tile, but re-extracted as 128×128 centred crop |

See `outputs/phase1-library/fp-fn-register.md` and `docs/methodology/preregistration/decisions-log.md` (Decision 4) for full rationale.
