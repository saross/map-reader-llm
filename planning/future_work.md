# Future Work & Maintenance

This document tracks long-term maintenance and methodological tasks for the Map Reader LLM project.

## Methodological Records
- [ ] **Log Retention Strategy**: `~/.gemini/antigravity/` logs are not purged effectively, but should be treated as research data.
    - Action: Review logs in `conversations/` and artifacts in `brain/`.
    - Action: Set up a cron job or script to copy relevant `*.pb` and `*.md` files into a dedicated `methodology/logs/` directory in this repository.

## Open Science Standards
- [ ] **FAIR4RS Compliance**: Upgrade the repository to fully meet FAIR (Findable, Accessible, Interoperable, Reusable) principles for Research Software.
    - [ ] Add `CITATION.cff`
    - [ ] Ensure comprehensive license coverage
    - [ ] Improve documentation for reusability (containerization, etc.)
