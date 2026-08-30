# Manuscript workspace (Quarto)

The ISPRS Journal of Photogrammetry and Remote Sensing (JPRS)
manuscript, one `.qmd` per section (S143 venue-tooling decision).

- **Render**: `quarto render` from this directory → `_output/`
  (gitignored). Drafting previews in HTML; the `elsarticle`
  extension is applied at final-files time.
- **Contract**: `docs/paper/journal-requirements-isprs.md` (8,500-word
  body; per-section budgets embedded in each stub's header comment).
- **Structure**: `docs/paper/manuscript-skeleton-isprs.md` — decisions
  D-1..D-5 gate conversion of the zero-drafts (`methods-draft.md`,
  `results-draft.md`, `discussion-seeds.md`) into these sections.
- **Symbols**: `docs/methodology/notation-key.md` governs all notation.
- **References**: export BibTeX from the Zotero collection
  `vlm-burial-mound-detection` into `references.bib`; never
  hand-author entries Zotero holds.
- **Register calibration**: every number cited in prose anchors to the
  analyses register / results artefacts; the revision-policy applies
  to generated supplement documents, not these sections (git is the
  history here).
