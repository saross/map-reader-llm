# MMMU-Pro Leaderboard (for cross-model comparison planning)

**Last updated**: 2026-03-15
**Source**: Multiple (see notes). Scores vary by evaluation conditions
(tools, CoT, vision-only). Some conflation between MMMU and MMMU-Pro
exists in secondary sources.

## Scores

| Model | MMMU-Pro | Notes |
|:------|--------:|:------|
| Gemini 3.1 Pro | 80.5–82% | Frontier; #1 on Artificial Analysis |
| Gemini 3 Flash | 81.2% | Our current model |
| GPT-5.4 | 81.2% | Without tools |
| Gemini 3 Pro | 81.0% | |
| GPT-5.2 | 79.5% | Without tools; 80.4% with |
| Claude Opus 4.6 | 77.3% | With tools; 73.9% without |
| Gemini 3.1 Flash-Lite | 76.8% | **Failed our task (F1=0.11)** |
| Claude Sonnet 4.6 | 74.5–75.6% | |
| Claude Sonnet 4.5 | ~70–72% (est.) | MMMU-Pro not confirmed |
| Claude Haiku 4.5 | ~60–65% (est.) | MMMU-Pro not confirmed |
| GPT-4o | 54.0% | Older model |

## Observations

- Flash-Lite at 76.8% catastrophically fails our mound detection task
- The capability threshold appears to sit between 76.8% and 81.2%
- Models at 81%+ (GPT-5.4, Gemini 3.1 Pro) would likely work but
  aren't cheaper than Flash
- Testing a model in the 77–80% range (Opus 4.6, GPT-5.2) would
  narrow the threshold estimate

## Sources

- [Artificial Analysis MMMU-Pro Leaderboard](https://artificialanalysis.ai/evaluations/mmmu-pro)
- [Google Gemini 3 Benchmarks (Vellum)](https://www.vellum.ai/blog/google-gemini-3-benchmarks)
- [Gemini 3.1 Pro Model Card](https://deepmind.google/models/model-cards/gemini-3-1-pro/)
- [OpenAI GPT-5.4 announcement](https://openai.com/index/introducing-gpt-5-4/)
- [Anthropic Claude Opus 4.6 System Card](https://www.anthropic.com/claude-opus-4-6-system-card)
- [Anthropic Claude Sonnet 4.6 System Card](https://anthropic.com/claude-sonnet-4-6-system-card)
- [MMMU-Pro paper (arXiv)](https://arxiv.org/html/2409.02813v3)
