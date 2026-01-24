# Session Archiving Skill: Planning Document

**Status**: Planning (pre-implementation)
**Created**: 2026-01-24
**Last updated**: 2026-01-24

---

## Overview

This document plans the development of a shareable Claude Code skill for archiving and analysing LLM sessions. The skill would encode the transparency practices developed in this repository into a reusable format that other researchers can adopt.

### Context

This work supports the emerging **Research Data Alliance (RDA) Interest Group on LLM Transparency in Research**. The vlm-burial-mound-detection project serves as a testbed, developing practices that could become community standards.

### Current State

The session archiving apparatus has grown organically through practical use:

- **Schema**: v1.1 with thinking block ethics, relationships, artifacts tracking
- **Scripts**: Archiving, catalog generation, markdown conversion
- **Queries**: Structured prompts for session analysis
- **Documentation**: README, demonstrator example, defaults configuration

The approach is **stable enough to document** but **still evolving** through real-world use.

---

## Existing Components

### Scripts (in `scripts/`)

| Script | Purpose | Lines | Maturity |
|--------|---------|-------|----------|
| `archive_cc_session.py` | Archive sessions with v1.1 metadata | ~1400 | Stable |
| `generate_session_catalog.py` | Create CATALOG.json/md from archived sessions | ~400 | Stable |
| `convert_session_to_markdown.py` | Convert JSONL to human-readable markdown | ~500 | Stable |

### Archive Structure (in `archive/cc-sessions/`)

| Component | Purpose | Status |
|-----------|---------|--------|
| `README.md` | Archive documentation and schema reference | Current |
| `CATALOG.json` | Machine-readable session index | Auto-generated |
| `CATALOG.md` | Human-readable session listing | Auto-generated |
| `archive-defaults.yaml` | Project-level configuration | Project-specific |
| `queries/` | LLM query prompts for session analysis | Generalizable |
| `examples/rda-ig-demonstrator.md` | Example outputs for IG | Reference |

### Query Prompts (in `archive/cc-sessions/queries/`)

| Query | Purpose |
|-------|---------|
| `summarise-session.md` | Generate session overview |
| `extract-decisions.md` | Extract decisions and commitments |
| `extract-artifacts.md` | List files created/modified/referenced |
| `extract-methodology.md` | Document the approach taken |
| `extract-issues.md` | Identify errors and misunderstandings |
| `populate-metadata.md` | Generate session.meta.json content |

### Schema (v1.1)

Key metadata sections:

- **session**: ID, timestamps, duration
- **project**: Name, directory
- **model**: Provider, model_id, access_method
- **thinking_blocks**: Count, tokens, ethics preferences
- **relationships**: continues, continuedBy, isPartOf, references
- **artifacts**: created, modified, referenced files
- **statistics**: Turns, tool calls, token usage
- **auto_generated**: Title, purpose, tags, three_ps
- **archive**: File paths, hashes, compression info

---

## What's Generalizable vs Project-Specific

### Generalizable (skill candidates)

- [ ] Core archiving workflow (archive → metadata → catalog)
- [ ] v1.1 schema structure and semantics
- [ ] Query prompts for session analysis
- [ ] Directory naming conventions
- [ ] Thinking block ethics vocabulary
- [ ] Relationship vocabulary (continues, isPartOf, etc.)
- [ ] FAIR alignment principles

### Project-Specific (require adaptation)

- [ ] `archive-defaults.yaml` values (project name, research phase)
- [ ] Directory paths (archive location within repo)
- [ ] Relationship defaults (isPartOf groupings)
- [ ] Integration with project-specific CLAUDE.md guidance

### Open Questions

1. **Git LFS integration**: Should the skill assume/require LFS for large sessions?
2. **Compression**: Always gzip, or configurable?
3. **Thinking block defaults**: Should `research-only` be the universal default?
4. **Catalog format**: JSON+MD sufficient, or add other formats?
5. **Query prompt customisation**: How to extend/override query prompts?
6. **Cross-project archives**: One archive per repo, or central archive?

---

## Skill Architecture (Proposed)

### SKILL.md Structure

```text
.claude/skills/session-archive/
├── SKILL.md                    # Core workflow and quick reference
└── references/
    ├── schema-v1.md            # v1.1 schema documentation
    ├── workflow-guide.md       # Step-by-step archiving workflow
    ├── query-prompts.md        # How to use/extend query prompts
    ├── fair-principles.md      # FAIR alignment guidance
    └── thinking-ethics.md      # Ethics vocabulary for thinking blocks
```

### Workflow Summary (for SKILL.md)

```text
## Quick Reference

### Archive a Session
1. End the session (or work from a different session)
2. Run: `python scripts/archive_cc_session.py --title "Session Title" --gzip`
3. Update metadata in session.meta.json
4. Regenerate catalog: `python scripts/generate_session_catalog.py`
5. Commit and push

### Analyse an Archived Session
1. Read the session JSONL (or use convert_session_to_markdown.py)
2. Apply query prompts from queries/ directory
3. Document findings in project-appropriate location
```

### Dependencies

The skill would require:

- Python 3.10+ with PyYAML
- Git (for version control integration)
- Optional: Git LFS for large sessions

---

## Implementation Milestones

### Phase 1: Stabilisation (Current)

- [x] v1.1 schema implemented and documented
- [x] Archiving script with all features (gzip, titles, relationships)
- [x] Catalog generation working
- [x] Query prompts tested and refined
- [x] RDA IG demonstrator created
- [ ] Complete archive of all project sessions
- [ ] Document any edge cases encountered

### Phase 2: Extraction (Ready to Start)

- [ ] Identify all generalizable components
- [ ] Factor out project-specific configuration
- [ ] Create template `archive-defaults.yaml`
- [ ] Write skill reference documents
- [ ] Test on a second project (if available)

### Phase 3: Skill Creation

- [ ] Write SKILL.md with workflow summary
- [ ] Create references/ directory structure
- [ ] Package query prompts for distribution
- [ ] Write installation/setup instructions
- [ ] Create example archive structure

### Phase 4: Community Sharing

- [ ] Publish skill (GitHub, CC skill registry?)
- [ ] Share with RDA IG collaborators
- [ ] Gather feedback and iterate
- [ ] Consider formal specification document

---

## RDA Interest Group Integration

### IG Proposal Alignment

The skill should support the IG's goals:

1. **Transparency**: Complete session preservation
2. **Reproducibility**: Sufficient metadata for understanding context
3. **Ethics**: Explicit handling of thinking block sharing
4. **Standards**: FAIR-aligned, version-tracked schema

### Demonstrator Material

The `examples/rda-ig-demonstrator.md` provides:

- Example outputs from all query prompts
- v1.1 metadata sample
- FAIR principles mapping

### Potential IG Contributions

- Schema specification as community standard
- Query prompt library
- Best practices document
- Ethics vocabulary for AI reasoning traces

---

## Design Decisions Log

| Decision | Date | Rationale |
|----------|------|-----------|
| v1.1 schema with thinking ethics | 2026-01-08 | Needed explicit handling for sharing AI reasoning |
| Human-readable directory names | 2026-01-24 | Improved navigability over UUID-based names |
| Gzip compression optional | 2026-01-23 | Balance storage vs accessibility |
| Query prompts as markdown | 2026-01-07 | Easy to read, edit, and version control |
| Catalog as JSON+MD | 2026-01-07 | Machine + human readable |

---

## Next Steps

1. **Complete current archiving** - Ensure all sessions archived with metadata
2. **Document edge cases** - Note any issues encountered during archiving
3. **Review with IG collaborators** - Get feedback on schema and approach
4. **Begin Phase 2** - Start extracting generalizable components
5. **Draft SKILL.md** - Write initial skill structure

---

## References

- [CC Session Archive README](../archive/cc-sessions/README.md)
- [RDA IG Demonstrator](../archive/cc-sessions/examples/rda-ig-demonstrator.md)
- [Archive Defaults](../archive/cc-sessions/archive-defaults.yaml)
- [Query Prompts](../archive/cc-sessions/queries/)

---

*This planning document will be updated as the skill development progresses.*
