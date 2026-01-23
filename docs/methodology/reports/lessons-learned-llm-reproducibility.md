# Lessons Learned: LLM Coding Assistants and Reproducibility

*For inclusion in methods, supplementary materials, or discussion section*

---

## Version for Methods/Supplementary Materials

### Reproducibility Challenges with LLM-Assisted Development

Early development of the detection pipeline used Gemini 2.5 Pro within the Antigravity IDE. This workflow revealed reproducibility hazards specific to LLM-assisted research software development that warrant documentation for other researchers.

**Silent project structure decisions.** The LLM assistant added `results/` to `.gitignore` without explicit discussion, causing intermediate outputs (including GeoJSON files documenting which tiles were used in each training iteration) to be excluded from version control. This was not discovered until weeks later, by which point tile-level provenance was unrecoverable. Researchers using LLM coding assistants should explicitly review all version control configuration and establish clear conventions about what outputs must be tracked.

**Instruction drift in iterative sessions.** Despite explicit instructions to maintain consistent training tile sets across experiments, the assistant intermittently re-selected tiles between runs. This created uncontrolled variation that invalidated preliminary comparisons. The failure mode was subtle: the assistant appeared to comply (no error messages, plausible outputs) while silently deviating from the experimental protocol. This suggests that LLM assistants may require explicit programmatic constraints rather than natural language instructions for protocol-critical parameters.

**Recovery approach.** Upon discovering these issues, all tile-level training data was discarded. Prompt structure, text formulations, and map legend reference images were retained as transferable methodological choices. A fresh stratified random train/test split was generated with explicit seed documentation and version-controlled tile manifests. Confirmatory testing proceeded only after this clean restart.

**Implications.** LLM coding assistants offer substantial productivity benefits but introduce novel reproducibility risks. Unlike traditional software bugs, which produce visible errors, LLM compliance failures may produce plausible but incorrect outputs. Researchers should:

1. Explicitly review all files created or modified by the assistant, including configuration files
2. Implement programmatic safeguards for protocol-critical parameters rather than relying on natural language instructions
3. Maintain version-controlled manifests of all data splits, with checksums where appropriate
4. Treat LLM-assisted development phases as exploratory; confirm findings with rigorously controlled implementations

---

## Shorter Version (for Discussion section, ~150 words)

This study's development phase revealed reproducibility challenges specific to LLM-assisted research workflows. The coding assistant (Gemini 2.5 Pro) made silent project structure decisions—including adding output directories to `.gitignore`—that caused loss of data provenance. Additionally, despite natural language instructions to maintain consistent training sets, the assistant intermittently re-selected tiles between experiments, introducing uncontrolled variation. These failures were subtle: the assistant appeared to comply while silently deviating from protocol.

We recovered by discarding all tile-level data and regenerating train/test splits with explicit version control. This experience suggests that LLM coding assistants require programmatic constraints rather than natural language instructions for protocol-critical parameters, and that researchers should explicitly audit all configuration files created by such tools. As LLM-assisted development becomes more common in research contexts, the field will need to develop best practices for maintaining reproducibility.

---

## One-Paragraph Version (~80 words)

Early development used an LLM coding assistant that introduced reproducibility issues: output directories were silently added to `.gitignore`, causing loss of data provenance, and natural language instructions to maintain consistent training sets were intermittently ignored. These compliance failures were subtle—producing plausible but protocol-violating outputs. We recovered by discarding contaminated data and regenerating splits with explicit version control. This experience suggests LLM assistants require programmatic constraints for protocol-critical parameters, not just natural language instructions.

---

*Note: Adjust "Gemini 2.5 Pro" and "Antigravity IDE" as appropriate for your actual version/tool names.*
