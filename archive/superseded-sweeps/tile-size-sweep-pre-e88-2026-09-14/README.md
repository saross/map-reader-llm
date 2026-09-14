# Tile-size sweep — the published artefacts superseded by erratum E88

**Archived**: 2026-09-14, under ruling 2 of the PI's four rulings on the
modality-track audit (`reports/modality-track-audit-2026-09-14.md`).

These are `results/tile-size-sweep/tile_size_sweep.{json,md}` exactly as they
stood before that ruling — the 2026-06-09-vintage tabulation whose
`best_per_size.by_arch_modality` grid grouped cells by a modality assigned from
a substring of the condition label. Kept browsable in the working tree per the
project's archive-never-delete policy; the live artefacts at
`results/tile-size-sweep/` are the regenerated, derived-modality versions.

**What differs between these files and the live ones** — five classes, only the
first attributable to E88:

| # | Change | Cause |
|---|---|---|
| 1 | 512 px `single-pass/image` `retest-phase2d::image-terse` 0.6052 / 0.2239 → `retest-phase2e::canonical-last` 0.6314 / 0.2132, and 512 px `single-pass/text` `canonical-last` 0.6314 / 0.2132 → `retest-phase2c::text-scale-4` 0.6094 / undefined | **E88** — `canonical-last`'s pool carries neither modality token, so the retired substring test put an image-bearing cell in the text leg |
| 2 | A `384 proposer-verifier/image` leg appears (`pv-diag-384::verified-adv-image-min-6of10` 0.789 / 0.8032) | Register growth since the 2026-06-09 vintage; not an E88 effect |
| 3 | Two Pro proposer-verifier rows appear in the Pro note (`verified-adv-image-baseline-pro-vf` 0.7309 / 0.8887; `verified-adv-text-pro-vf-4of5` 0.8792 / 0.7947) | Register growth; not an E88 effect. "Pro single-pass ran only at 384" is still true |
| 4 | Two 512 px View-1 text cells' `mcc` `0.0` → `null` | **E81** — undefined tile MCC had been published as `0.0`; this artefact had not been regenerated since that correction |
| 5 | One 384 px View-1 image cell's `mcc` 0.3295 → 0.3296 | A re-read of the cell's own evaluation; no rendered figure quotes it |

Views 1 and 3 are otherwise identical, and no F1 in any view moves.
