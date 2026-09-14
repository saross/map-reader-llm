# Preregistration Materials: VLM-Based Burial Mound Detection

This registration contains three documents comprising the complete preregistration for a study evaluating vision-language model prompting strategies for cartographic symbol detection.

## Document Overview

| Document | Purpose |
|----------|---------|
| `preregistration.md` | **Primary document** — full study specification including hypotheses, analysis plan, data resources, and implementation details |
| `preregistration-appendix-prompts.md` | Complete prompt text for all experimental conditions, including system instructions, few-shot examples, and configuration parameters |
| `preregistration-coverage.md` | Factorial coverage matrix documenting which factor combinations are tested, explicit exclusions with rationale, and interaction coverage |

## Corrections — read this before citing any number from the primary document

The three documents above are the **lodged, immutable** registration, and the
copies here are byte-identical to what was registered. Where execution or a
later audit found a lodged statement to be wrong, the correction is recorded in
`../protocol-errata.md` and **never** written into the text above.

- [`errata-pointers.md`](errata-pointers.md) — the reverse index: from a passage
  of `preregistration.md` (with its line locator) to the erratum that corrects
  it. Start here if you are about to reuse a figure from the primary document.
- [`tile-mound-counts-recomputed-2026-09-13.md`](tile-mound-counts-recomputed-2026-09-13.md)
  — the affine-correct per-tile mound counts, published beside the lodged
  §§ 2.3–2.5 tables as a post-hoc correction (erratum E87). The lodged counts
  came from a superseded bounding-box approximation of each sheet's
  georeferencing; the "36 mounds" of § 2.3 is 50 and the "79 mounds" of § 2.4
  is 97.

## Reading Order

Readers should begin with `preregistration.md`, which provides the complete study specification. The two companion documents supply detailed implementation specifications referenced from the main document:

- Section 8 of the preregistration references prompt configurations documented in the appendix
- Section 8.7 references the coverage matrix for factorial design details

## Version Information

All documents are synchronised to preregistration version 4.7 (dated 2026-01-31).

## Code Repository

Analysis code and configuration files are available at:

- **Repository**: <https://github.com/saross/map-reader-llm>
- **Commit**: `f037a9d`

The repository contains tile selection manifests, detection configurations, and analysis scripts referenced in the preregistration.

## Contact

Shawn Ross  
Macquarie University, Sydney, Australia
