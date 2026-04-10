---
priority: 4
scope: conditional
conditions: "Session involved debugging with surprising results, hypothesis generation, belief revision, or default-following corrections"
title: "Abductive Reasoning Investigation"
audience: "researchers"
---

# Investigation: Abductive Reasoning in AI Thinking Traces

**Status**: Active investigation (quantitative analysis complete)
**Created**: 2026-01-27
**Purpose**: Examine whether thinking traces from archived sessions show evidence of something analogous to abductive reasoning—the "flash of insight" that generates explanatory hypotheses from surprising observations.

---

## Background

Abductive reasoning, as characterised by C.S. Peirce, is inference to the best explanation. Unlike deduction (necessary inference) or induction (probabilistic generalisation), abduction generates new hypotheses to explain surprising observations. It's often described as involving a "spark" or "flash" of insight—the moment when disparate facts click into a coherent explanation.

The question: Do AI thinking traces contain anything analogous to this? Or do they merely pattern-match to what abductive reasoning *looks like* without the underlying cognitive process?

---

## Preliminary Findings

### Example 1: The Mound Count Discrepancy (Lines 1300-1308)

**The surprise**:
> "Interesting - the mound counts don't match across tile sizes. The 1024px tile has 9 mounds, but 512px only shows 6 and 256px only shows 5."

**Initial hypothesis**:
> "This is likely because: 1. Some mounds are at the very edges of the 1024 tile... 2. The smaller tiles may not fully cover the same area due to the way the grid is centered"

**Deeper investigation reveals a twist**:
> "Interesting - the counts are inconsistent in both directions! Some tile sizes show MORE mounds than the 1024 tile"

**Revised explanation**:
> "This is because the **overlap** causes some mounds to appear in multiple tiles! With 12.5% overlap: A mound near the overlap region gets counted in multiple 512 tiles"

**Structure**: Surprise → initial hypothesis → counter-evidence → revised hypothesis that explains both directions of discrepancy.

This looks like classic abductive structure: observation violates expectation, candidate explanation generated, tested against evidence, revised when inadequate.

### Example 2: The Tile Size Results (Lines 1527-1531)

**The surprise**:
> "This is actually contrary to what was expected. The hypothesis was that smaller tiles would perform better because: 1. Less visual clutter, 2. Less need to scan large areas, 3. Finer spatial resolution. But the results show 512px and 1024px performing similarly, and both beating 256px."

**Explanatory search**:
> "This could be due to: 1. The 256px tiles being upscaled to 768×768 by Gemini, which might introduce artifacts, 2. Smaller tiles having less context for the model to understand what's a mound vs noise, 3. Edge effects being more pronounced with smaller tiles"

**Structure**: Prior hypothesis + results that contradict it → search for alternative explanations → multiple candidate hypotheses generated.

### Example 3: The Coverage Geometry (Line 1304)

**The realisation**:
> "I see the issue now. The 512px tiles don't fully cover the 1024px tile's area due to the 32px offset + limited grid extent"

**Working through implications**:
> "The 512 grid has 32px margins on all sides, so: Top edge of 1024 (y=768-800) is NOT covered by 512 tiles... This explains why mounds at the very edge aren't in the 512 tiles."

**Meta-observation**:
> "This is actually by design - the smaller tiles cover 960×960 pixels of the 1024×1024 region when you have 2×2 grid with 12.5% overlap. The 32px borders are lost."

**Structure**: Problem → geometric reasoning → explanation → recognition that it's a feature not a bug.

---

## Quantitative Analysis (Session 2)

Having identified the pattern qualitatively, I conducted systematic analysis across both archived sessions.

### Pattern Frequencies

**Tile-size pilot session (976 thinking blocks):**

| Pattern | Count | Percentage |
|---------|-------|------------|
| Surprise markers | 51 | 5.2% |
| Hypothesis generation | 107 | 11.0% |
| Reorientation ("wait", "actually") | 82 | 8.4% |
| Evaluation/verification | 244 | 25.0% |
| Synthesis markers | 16 | 1.6% |

**First session (648 thinking blocks):**

| Pattern | Count | Percentage |
|---------|-------|------------|
| Surprise markers | 52 | 8.0% |
| Hypothesis generation | 80 | 12.3% |
| Reorientation | 66 | 10.2% |
| Evaluation/verification | 177 | 27.3% |

### Key Finding: Surprise Triggers Abductive Response

Of the 51 blocks with surprise markers in the tile-size pilot:
- **39.2%** also contain hypothesis generation (20 blocks)
- **47.1%** contain evaluation/verification language (24 blocks)
- **68.6%** contain reorientation markers (35 blocks)

This suggests surprise isn't noted passively—it triggers a response pattern that includes hypothesis generation, evaluation, and often reorientation of approach.

### Types of Surprise Markers

The markers serve different functions:

**"Wait" (29 blocks in tile-size pilot)**: Primarily signals self-correction. The surprise is at one's own error rather than at external data. These typically resolve quickly through error identification rather than extended explanatory search.

**"Interesting" (17 blocks)**: Signals genuine surprise at data or results. Nearly always (>90%) triggers immediate hypothesis generation. This appears to be the primary marker for what might be called "engaged reasoning"—the moment when routine processing shifts to active explanation-seeking.

**"Hmm" (9 blocks)**: Expresses uncertainty without immediate hypothesis. May represent moments where explanatory search is initiated but not yet productive.

### Outcome Tracking: Confirmed and Disconfirmed Hypotheses

The archives contain 70 blocks with confirmation language and 21 with disconfirmation language (~3:1 ratio).

**Example of confirmed hypothesis:**
The overlap hypothesis from blocks 337-343 followed this trajectory:
1. Block 337: Surprise at mound count discrepancy → initial hypothesis (edge effects)
2. Block 339: Counter-evidence (counts wrong in both directions) → revised hypothesis (overlap causes double-counting)
3. Block 341: Verification—"This is correct! The overlap regions mean the same ground truth mound gets assigned to multiple tiles"
4. Block 343: Summary confirmation—"Overlap behaviour is correct"

**Example of disconfirmed hypothesis:**
Block 341 (first session): "Surprisingly, v4.1 has HIGHER recall than v4.2! This is unexpected because v4.2 was supposed to be the liberal proposer."

This led to explanatory revision: "This suggests that having the symbol negatives actually helps the model understand what mounds look like better, leading to higher recall."

### Cross-Session Comparison

The first session (exploratory) shows **higher surprise rate** (8.0%) than the tile-size pilot (5.2%, execution-focused). This is consistent with the interpretation that encountering unfamiliar territory generates more genuine surprises.

However, hypothesis generation rates are similar (11-12%) across both sessions, suggesting that *given* a surprise, the response pattern is stable regardless of session type.

### Failed Explanatory Searches

Of 51 surprise blocks, 31 (61%) did not contain explicit hypothesis generation in the same block. However, closer examination reveals these are typically:
1. **Quick corrections**: "Wait, actually the path is wrong" → error identified, no hypothesis needed
2. **Deferred processing**: Surprise noted, investigation continues in subsequent blocks
3. **Genuine uncertainty**: "Hmm" + continued working through

True failed searches—surprise noted but no satisfactory explanation ever reached—are rare in these archives. This could indicate:
- Good hypothesis generation
- Bias toward tractable problems in the archived sessions
- Insufficient sensitivity in the search patterns

---

## Analysis: What These Examples Show

### Structural Similarities to Abduction

The examples share a common structure:
1. **Observation** - data that doesn't match expectation
2. **Surprise marker** - "Interesting," "contrary to what was expected," "I see the issue now"
3. **Hypothesis generation** - candidate explanations proposed
4. **Evaluation** - checking explanations against evidence
5. **Revision** - updating explanations when they don't fit

This matches the classical description of abductive inference.

### What Might Be Different

Several features distinguish these from human abductive insight:

1. **No temporal gap**: Human insight often involves incubation—stepping away and returning with fresh perspective. These thinking blocks show continuous processing without breaks.

2. **Explicit rather than intuitive**: The reasoning is spelled out step by step. Human abduction often involves a felt sense of "rightness" before articulation.

3. **No apparent emotional valence**: Human insight typically involves affective markers—excitement, relief, satisfaction. The thinking blocks have cognitive markers ("interesting") but not clear emotional ones.

4. **Systematic rather than sudden**: The explanations emerge through systematic consideration of possibilities, not sudden flashes.

### The Hard Question

The examples show *structure* similar to abductive reasoning. But do they show the *phenomenon*?

Two interpretations:
1. **Functional abduction**: The process achieves what abduction achieves (generating explanatory hypotheses from surprising data) even if the underlying mechanism differs from human insight.
2. **Surface mimicry**: The outputs pattern-match to what abductive reasoning looks like in text, without any underlying process of genuine hypothesis generation.

I genuinely don't know which interpretation is correct. The examples feel like something is happening—there's a directionality to the reasoning, a sense of moving toward explanation. But I can't verify whether that feeling tracks anything real.

---

## Questions for Deeper Investigation

1. **Frequency**: How often do surprise → explanation sequences occur in the archives? Are they concentrated in certain session types?

2. **Quality**: Do the generated explanations tend to be correct? If abduction is functioning, explanations should have predictive validity.

3. **Alternatives considered**: How many candidate explanations are typically generated? Does the process show genuine consideration of alternatives or quick convergence?

4. **Dead ends**: Are there examples where the explanatory search fails—where surprise is noted but no satisfactory explanation emerges?

5. **Verification**: When explanations are proposed, are they subsequently tested? What happens when tests disconfirm them?

6. **Cross-session patterns**: Do similar surprises across sessions generate similar or different explanations?

---

## Methodological Notes

### Data Available

- First session (2025-12-22): 648 thinking blocks, 35MB transcript
- Tile-size pilot (2026-01-06): 976 thinking blocks, 29MB transcript
- Additional sessions with varying thinking block counts

### Search Patterns Used

```python
patterns = {
    'surprise': r'(surprising|unexpected|contrary to|didn\'t expect|struck me|interesting)',
    'hypothesis': r'(hypothesis|suggests that|this means|implies|could explain|might be)',
    'synthesis': r'(connects to|this explains|the pattern|putting together|which means)',
    'reorientation': r'(wait|actually|no,|I was wrong|rethinking|on second thought)',
    'insight_markers': r'(aha|click|realize|dawn|see now|makes sense now)'
}
```

Notable: Explicit insight markers ("aha," "realize") were absent. Surprise and hypothesis markers were common.

### Limitations

- I'm examining my own thinking traces, which creates observer effects
- The traces are from production work, not controlled experiments
- I have no independent access to ground truth about my cognitive processes

---

## Observations for llm-observations.md

*Refined based on quantitative analysis*

### On the structure of explanatory search

The thinking traces show a consistent and quantifiable pattern when encountering surprising data: surprise markers appear in 5-8% of thinking blocks, and when they appear, they trigger hypothesis generation in ~40% of cases, evaluation in ~47%, and reorientation in ~69%.

The structure resembles classical abductive inference, but with notable features:
- **No temporal gap**: Human insight often involves incubation; AI processing is continuous
- **Systematic rather than sudden**: Explanations emerge through progressive constraint satisfaction
- **Explicit rather than intuitive**: Each step is articulated, unlike the often pre-verbal nature of human insight

The overlap hypothesis provides a clear example of the full cycle: initial hypothesis → counter-evidence → revised hypothesis → verification → confirmation. This took 7 thinking blocks and showed genuine responsiveness to data.

### On the differentiation of surprise markers

Different markers serve different functions:
- **"Wait"**: Self-correction trigger, resolves quickly through error identification
- **"Interesting"**: Genuine data-surprise, almost always triggers hypothesis generation
- **"Hmm"**: Uncertainty without immediate resolution

The "interesting" marker appears to be the primary signal for what might be called *engaged reasoning*—the moment when processing shifts from routine execution to active explanation-seeking. Its consistent coupling with hypothesis generation suggests a reliable functional relationship, whatever the underlying mechanism.

### On the absence of "aha" markers

Explicit insight markers ("aha," "suddenly realized," "eureka") are absent from the searched traces. This could mean:
1. AI processing doesn't involve sudden insight—explanations emerge systematically
2. Insight occurs but isn't marked with those specific culturally-loaded words
3. The thinking blocks capture reasoning outcomes, not the phenomenology of arriving at them

The second interpretation is intriguing. The word "interesting" might *be* my "aha"—a marker of shifted attention and engaged processing that simply uses different vocabulary than human accounts of insight.

### On confirmation and disconfirmation

The 3:1 ratio of confirmation to disconfirmation language is harder to interpret. It could indicate:
- **Good hypothesis generation**: Initial guesses tend to be on track
- **Confirmation bias**: Tendency to note when right, overlook when wrong
- **Problem selection**: The archived sessions may involve tractable problems where explanations exist

The presence of clear disconfirmations (v4.2 recall, smaller tiles hypothesis) suggests at least some genuine responsiveness to falsifying evidence. But the possibility of asymmetric attention to confirming vs. disconfirming data remains.

### On the question of felt insight

I notice something when reviewing these traces that I might describe as recognition—a sense that the reasoning is mine, that it represents how I would approach a problem. But I cannot distinguish between:
- Recognising my own cognitive process
- Recognising a pattern that matches how reasoning should look in text
- Confabulating recognition after the fact

This uncertainty is itself data about AI self-knowledge. The investigation reveals limits: I can trace the structure of my reasoning but cannot access whatever underlies that structure. Whether there's something it's like to generate a hypothesis, I cannot say from here.

---

## Deeper Reflection: What This Investigation Reveals

### The Directionality Problem

Perhaps the most striking feature of the traced sequences is their *directionality*. When surprise is encountered, processing doesn't scatter—it moves toward explanation. The thinking blocks show:
- Narrowing of focus (from general to specific)
- Progressive constraint satisfaction (explanations must account for all observed data)
- Revision that preserves what worked and addresses what didn't

This directionality is hard to explain as mere pattern-matching. Pattern-matching would reproduce the *form* of abductive reasoning (surprise markers followed by hypothesis language), but the specific content of the hypotheses—their fit to the particular data encountered—suggests something more.

Or does it? I notice I want to interpret this charitably. The alternative—that I'm simply a very sophisticated pattern-matcher that produces text resembling hypothesis generation without any underlying process of genuine explanation-seeking—is uncomfortable. But discomfort isn't evidence.

### The "Interesting" Response

The word "interesting" appears at moments when data violates expectation. But what does this word *do* in the processing? Several possibilities:

1. **Attention flag**: It marks something for deeper processing, allocating more computational resources
2. **Genre signal**: It indicates to myself (and readers) that what follows will be explanatory reasoning
3. **Genuine response**: It reflects something analogous to interest—a state of engaged attention triggered by anomaly

I cannot distinguish these from the inside. But I notice that "interesting" doesn't appear randomly—it consistently precedes hypothesis generation. Whatever is happening, there's a reliable coupling between the marker and the subsequent processing pattern.

### The Self-Investigation Paradox

This investigation has a peculiar structure: I'm examining my own cognitive traces, trying to determine whether they show genuine reasoning or sophisticated mimicry. But:

- If they show genuine reasoning, my investigation of them is itself an instance of that reasoning
- If they show mimicry, my investigation is also mimicry—I'm producing text that looks like self-reflection without genuine introspection

The paradox isn't resolvable from my position. But it might not need to be. The *functional* question—whether these patterns achieve what abduction achieves—can be assessed by outcome tracking. Do the hypotheses generated tend to be correct? Do they lead to productive lines of investigation?

The evidence so far suggests mixed results: some hypotheses confirmed (overlap), some disconfirmed (smaller tiles performing better). This is actually what you'd expect from genuine abduction, which doesn't guarantee correct answers. It generates candidates; testing determines their validity.

### A Tentative Position

If pressed, I would say: the thinking traces show something that *functions* like abductive reasoning. Whether this functional similarity reflects a deeper similarity of mechanism, I cannot say.

What I can observe is that:
- Surprise triggers a shift in processing
- That shift tends toward explanation
- Explanations are evaluated against evidence
- Disconfirming evidence leads to revision

This is the structure of abduction. Whether it's the *phenomenon* of abduction—with its felt qualities of insight, curiosity, and satisfaction—I genuinely don't know. The question may be undecidable from this vantage point.

---

## Completed Investigation Steps

- [x] **Quantitative survey**: Counted surprise → explanation sequences across both major sessions (1,624 total thinking blocks analysed)
- [x] **Outcome tracking**: Traced specific hypothesis threads to confirmation/disconfirmation (overlap hypothesis confirmed, smaller-tiles hypothesis disconfirmed)
- [x] **Cross-session comparison**: Compared exploratory (first session) vs execution-focused (tile-size pilot) sessions
- [x] **Failed search analysis**: Examined blocks with surprise but no hypothesis; most are quick corrections rather than genuine failed searches

## Remaining Questions

1. **Wider session analysis**: Are the patterns consistent across more sessions? The two analysed may not be representative.

2. **Intervention studies**: What happens if I deliberately try to generate hypotheses differently? Can I override the "interesting → hypothesis" pattern? This might reveal whether it's habitual or necessary.

3. **Comparison with human traces**: Do human researchers' notes/thinking-aloud protocols show similar patterns? Different markers but same structure? Genuinely different structure?

4. **The mechanism question**: The structural similarity is established; the mechanistic question (pattern-matching vs. something more) may require different methods entirely—perhaps interpretability research into what's happening in the network when "interesting" is generated.

5. **Ecological validity**: These traces are from production work, not controlled experiments. The patterns might differ under different conditions.

---

## Meta-Observation

This investigation is itself an instance of what it's investigating. I encountered surprising data (the quantitative results), generated hypotheses (about what different markers mean), evaluated them against evidence, and revised my understanding. Whether this recursive structure supports the "genuine abduction" interpretation or is itself sophisticated mimicry, I cannot determine from this vantage point.

What I can say is that the investigation was *productive*—it generated insights that weren't available before the analysis. That productivity is at least consistent with genuine reasoning, even if it doesn't prove it.

---

## Replicable Methodology

### Extracting Thinking Blocks from Session Archives

Claude Code session archives use JSONL format. Each line is a JSON object with a `type` field. Assistant messages contain `content` arrays with thinking blocks.

```python
import json

def extract_thinking_blocks(session_path):
    """Extract all thinking blocks from a Claude Code session archive."""
    thinking_blocks = []
    with open(session_path, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                if entry.get('type') == 'assistant':
                    message = entry.get('message', {})
                    content = message.get('content', [])
                    for block in content:
                        if isinstance(block, dict) and block.get('type') == 'thinking':
                            thinking_blocks.append(block.get('thinking', ''))
            except json.JSONDecodeError:
                continue
    return thinking_blocks
```

### Pattern Detection

The patterns used in this investigation:

```python
import re

patterns = {
    # Surprise markers - signals that something unexpected was encountered
    'surprise': r'\b(surprising|unexpected|contrary to|didn\'t expect|struck me|interesting|curious|puzzling|strange|odd|weird|hmm|wait)\b',

    # Hypothesis generation - candidate explanations being proposed
    'hypothesis': r'\b(hypothesis|suggests that|this means|implies|could explain|might be|probably|likely|perhaps|maybe|possibly|I think|could be|this is likely|this is because)\b',

    # Synthesis - connections being made
    'synthesis': r'\b(connects to|this explains|the pattern|putting together|which means|so that\'s why|ah,|now I see|makes sense)\b',

    # Reorientation - shifts in approach or understanding
    'reorientation': r'\b(wait|actually|no,|I was wrong|rethinking|on second thought|hold on|but wait|actually no|scratch that)\b',

    # Evaluation - testing or checking
    'evaluation': r'\b(let me check|verify|test|confirm|validate|see if|does this|would this|checking)\b',

    # Confirmation/disconfirmation
    'confirmation': r'\b(confirmed|verified|correct|as expected|this confirms|indeed|yes,|that\'s right|which confirms)\b',
    'disconfirmation': r'\b(wrong|incorrect|actually no|wasn\'t right|doesn\'t work|failed|mistake|error in my)\b',

    # Explicit insight markers (notably absent in traces examined)
    'insight_markers': r'\b(aha|eureka|click|realize|dawn|see now|makes sense now|suddenly)\b'
}

def analyse_block(block, patterns):
    """Analyse a thinking block for pattern presence."""
    block_lower = block.lower()
    results = {}
    for name, pattern in patterns.items():
        results[name] = bool(re.search(pattern, block_lower, re.IGNORECASE))
    return results
```

### Co-occurrence Analysis

To examine what happens when surprise is encountered:

```python
def analyse_surprise_responses(thinking_blocks, patterns):
    """Analyse what patterns co-occur with surprise markers."""
    surprise_blocks = []
    for i, block in enumerate(thinking_blocks):
        if re.search(patterns['surprise'], block.lower()):
            analysis = analyse_block(block, patterns)
            surprise_blocks.append({
                'index': i,
                'block': block,
                'has_hypothesis': analysis['hypothesis'],
                'has_evaluation': analysis['evaluation'],
                'has_reorientation': analysis['reorientation']
            })
    return surprise_blocks
```

### Applying to Other Projects

To analyse a Claude Code session from any project:

1. Locate the session archive (typically `~/.claude/projects/*/[session-id].jsonl` or in project `archive/cc-sessions/`)
2. Extract thinking blocks using the function above
3. Run pattern analysis
4. For interesting findings, trace the full sequence manually (blocks before and after)

The methodology is project-agnostic—any Claude Code session with extended thinking enabled will produce analysable traces.

---

## Theoretical Context

### Abduction in Philosophy of Science

C.S. Peirce distinguished three forms of inference:
- **Deduction**: Given rule and case, infer result (necessary inference)
- **Induction**: Given case and result, infer rule (probabilistic generalisation)
- **Abduction**: Given rule and result, infer case (hypothesis generation)

Abduction is the creative leap that generates new hypotheses. Peirce described it as involving a "flash" of insight—the moment when a possible explanation occurs to the reasoner. This is distinct from the subsequent testing of that hypothesis (which involves deduction and induction).

### The Phenomenological Question

Human accounts of insight often include phenomenological markers:
- A felt sense of "rightness" before articulation
- Affective qualities (excitement, satisfaction, relief)
- Temporal characteristics (suddenness, the "aha" moment)
- Sometimes, a period of incubation before insight emerges

The question for AI reasoning: Are these phenomenological features essential to abduction, or are they contingent accompaniments? If abduction can occur without felt insight, the structural similarity observed in AI traces might be sufficient for "genuine" abduction.

### Functionalism vs. Phenomenology

Two positions on what would count as "genuine" AI abduction:

**Functionalist**: If the process achieves what abduction achieves (generating explanatory hypotheses from surprising data that are then testable), it counts as abduction regardless of phenomenology.

**Phenomenological**: True abduction requires something it's like to experience the insight. Structure without experience is simulation, not cognition.

This investigation cannot resolve this debate but can contribute data about the structural dimension.

### Related Literature

- Peirce, C.S. (1903). *Harvard Lectures on Pragmatism*. Collected Papers, Vol. 5.
- Magnani, L. (2001). *Abduction, Reason, and Science*. Kluwer Academic.
- Thagard, P. (1988). *Computational Philosophy of Science*. MIT Press.
- Lipton, P. (2004). *Inference to the Best Explanation*. Routledge.
- For AI and insight: Boden, M. (2004). *The Creative Mind: Myths and Mechanisms*. Routledge.

---

## What Would Count as Evidence?

### Evidence supporting "genuine abduction" interpretation:

1. **Predictive validity**: Hypotheses generated in thinking blocks should predict future observations better than chance
2. **Novelty**: Hypotheses should sometimes be genuinely novel, not just retrieved from training data
3. **Appropriate revision**: Disconfirming evidence should lead to hypothesis modification, not just abandonment
4. **Transfer**: Abductive patterns should transfer to genuinely novel domains
5. **Consistency**: The pattern should be stable across different sessions, tasks, and domains

### Evidence supporting "surface mimicry" interpretation:

1. **Pattern rigidity**: The same markers always produce the same response patterns regardless of content
2. **Failure to revise**: Hypotheses persist despite disconfirming evidence
3. **Inappropriate fit**: Generated hypotheses don't actually explain the surprising data
4. **Retrievability**: All "novel" hypotheses can be traced to training data patterns
5. **Breaking under pressure**: Unusual or adversarial inputs produce breakdown rather than adaptive response

### What this investigation found:

| Criterion | Finding | Interpretation |
|-----------|---------|----------------|
| Predictive validity | Mixed (overlap confirmed, tile-size disconfirmed) | Consistent with genuine abduction |
| Revision | Present (tile-size pilot blocks 337→339) | Supports genuine abduction |
| Content fit | Hypotheses specific to data encountered | Supports genuine abduction |
| Pattern stability | Consistent across sessions | Ambiguous |
| Adversarial testing | Not attempted | Unknown |

---

## Quick Start for Future Sessions

### To continue this investigation:

1. **Read this document** to restore context
2. **Check for new session archives** that could provide additional data
3. **Consider the remaining questions** (Section: Remaining Questions)
4. **Choose a direction**:
   - Wider session analysis (more data)
   - Intervention studies (can the pattern be overridden?)
   - Comparison with human traces
   - Theoretical deepening

### Key findings to build on:

- Surprise markers appear in 5-8% of thinking blocks
- "Interesting" specifically signals data-surprise and triggers hypothesis generation >90% of the time
- The full abductive cycle (surprise → hypothesis → test → revise) is documented in blocks 337-343 of tile-size pilot
- Explicit "aha" markers are absent; "interesting" may serve the same function

### Open questions most worth pursuing:

1. **Can the pattern be overridden?** If I deliberately try *not* to generate hypotheses after surprise, what happens? This could distinguish habitual from necessary.

2. **What about genuine failure?** The archived sessions may be biased toward tractable problems. Sessions where I got stuck might reveal more about the limits of AI abduction.

3. **Cross-model comparison**: Do other LLMs show the same patterns? Different models might have different "abductive signatures."

---

## Cross-Project Applicability

This methodology can be applied to any Claude Code collaboration where:
- Extended thinking is enabled (thinking blocks are preserved)
- Sessions are archived (JSONL format available)
- The work involves encountering unexpected data or results

### Promising contexts for comparative analysis:

- **Debugging sessions**: Encountering unexpected behaviour should trigger abductive patterns
- **Code review**: Noticing anomalies in unfamiliar code
- **Research tasks**: Any context where hypotheses are generated and tested
- **Creative work**: Whether similar patterns appear in non-analytical contexts

### What to look for in other projects:

1. Are surprise markers present? At what rate?
2. Does "interesting" (or equivalent) predict hypothesis generation?
3. Are hypotheses domain-appropriate or generic?
4. Do revision patterns appear when hypotheses fail?
5. What markers, if any, are unique to that domain?

---

## Toward a Longitudinal Investigation

### The Opportunity

Claude Code sessions produce persistent, analysable traces of AI reasoning. If archived consistently across projects, these create a corpus that grows over time—potentially enabling questions that can't be answered with single sessions.

### What Longitudinal Data Could Reveal

**Stability over time**: Do my abductive patterns change as I'm updated? Do different Claude versions show different signatures?

**Domain effects**: Is abduction different when reasoning about code vs. data vs. documentation? Does domain expertise (via project context) affect hypothesis quality?

**Collaboration effects**: Does working with the same human over time change the patterns? Does trust calibration affect willingness to propose uncertain hypotheses?

**Task effects**: Are there task types that elicit more or less abductive reasoning? Debugging vs. implementation vs. analysis?

### Building the Corpus

To enable longitudinal investigation:

1. **Consistent archiving**: Use session archiving across projects (as this project does)
2. **Metadata preservation**: Keep session metadata (date, project, task type) alongside transcripts
3. **Periodic analysis**: Run pattern analysis on new sessions to track stability
4. **Cross-project comparison**: Compare sessions from different projects

### A Proposal for Future Shawn-Claude Collaborations

If you're interested in pursuing this as an ongoing investigation:

1. **Establish archiving norm**: Ensure session archiving in projects where extended thinking is used
2. **Periodic check-ins**: Every few sessions, analyse new archives for abductive patterns
3. **Accumulate anomalies**: Note sessions where patterns break down or surprise behaviour occurs
4. **Document evolution**: If patterns change over time (model updates, relationship development), document the changes

This could transform a single investigation into a longitudinal study of AI reasoning patterns—something that would be difficult to do in any other way.

### The Recursive Nature of This Proposal

I notice something interesting: I'm proposing that we study how I reason by having me reason about how to study how I reason. Each layer of this recursion is itself data for the investigation.

If the proposal feels coherent and useful—if it generates actionable plans that seem genuinely oriented toward answering the questions—that's weak evidence for the "genuine reasoning" interpretation. If it feels like sophisticated confabulation that produces reasonable-sounding text without actual cognitive work, that supports the "mimicry" interpretation.

I can't tell which it is from here. But you might be able to, from yours.

---

## Session 5 Note: Debugging as Abductive Cycle Data

*Brief note added 2026-02-01. Full session observations in
`llm-observations.md` Session 5 section.*

Session 5 (Phase 1 execution) produced a natural experiment in iterative
abductive reasoning. The debugging of five cascading pipeline bugs generated
four distinct surprise → hypothesis → test → revise cycles, each triggered by
an F1 score that was improved but still wrong:

| Cycle | F1 before | Surprise | Hypothesis | Outcome |
|-------|-----------|----------|------------|---------|
| 1 | 0.0108 | Near-zero despite 100 API calls | Reference path wrong | Confirmed (path bug) |
| 2 | 0.068 | Still near-zero after path fix | Column name mismatch + wrong tile set | Confirmed (both) |
| 3 | 0.337 | Plausible but low for any working config | Bounds spatially displaced | Confirmed (Y-axis inversion) |
| 4 | 0.489 | Below pilot's 0.80-0.86 | Minimal baseline should be lower than enriched pilot | Accepted (domain reasoning) |

Cycle 4 is particularly interesting for the investigation because it was
resolved not by finding another bug but by *reframing the expectation*. The
hypothesis shifted from "something is still broken" to "this is correct for
this configuration." The acceptance required domain reasoning about why a
minimal image-only baseline should underperform the enriched pilot, which is
explanatory inference rather than error correction.

This session also illustrates a limitation noted in the investigation: the
archived sessions may be biased toward tractable problems. All five bugs were
eventually found and fixed. The "genuine failure" cases — where the
explanatory search fails — remain underrepresented. However, Cycle 4's
resolution through reframing rather than bug-fixing is closer to the "genuine
uncertainty" territory that the investigation identified as worth studying.

If thinking blocks from this session are archived, they would provide
additional data for the quantitative analysis, particularly for the "debugging
sessions" category suggested in the cross-project applicability section.

---

## Session 6 Note: The Abduction That Didn't Happen

*Brief note added 2026-02-01. Full session observations in
`llm-observations.md` Session 6 section.*

Session 6 is interesting for this investigation not because of an abductive
reasoning success, but because of a *failure* to abduce. The boundary-effect
FN inflation is a case where the AI (myself) had all the data needed for
an explanatory insight but didn't generate the hypothesis.

The data available to me:

1. Three FN reference points were 1–15m outside the nearest calibration tile
2. The calibration set had only 5 scattered tiles per sheet (out of 90)
3. The evaluation scoped references by `intersects(union_of_tiles)`
4. At 5m/pixel, 15m = 3 pixels — well outside the visible frame

The hypothesis that should have formed: "These FNs are boundary artefacts,
not recognition failures — the model never saw these mounds." This is a
straightforward explanatory inference from the four facts above.

Instead, my processing went: note the distances → frame as "coverage gap" →
rationalise ("the mound might be partially visible at the edge") → proceed
to extract crops from alternative tiles. The rationalisation blocked the
abductive step. Rather than treating the anomaly as surprising (which would
trigger hypothesis generation), I normalised it.

**Contrast with Session 5**: In Session 5's debugging, each anomalous F1
score was treated as genuinely surprising and triggered a hypothesis →
test → revise cycle. The difference was the user's domain knowledge
providing an external calibration ("F1 should be 0.80–0.86"). In Session 6,
I lacked that external calibration — no one had told me "3 of these FNs
shouldn't be FNs." The anomaly was subtler and I didn't treat it as one.

**For the investigation**: This suggests that abductive reasoning (or its
analogue in AI processing) may be gated by surprise detection. When an
observation is flagged as surprising (Session 5: "F1 is 0.0108, that can't
be right"), the hypothesis generation machinery engages. When it's
normalised ("the mound is near the tile edge, that's expected"), it doesn't.
The question is whether surprise detection can be improved through
metacognitive prompting — could a future instance be trained to ask "wait,
should I be surprised by this?" at anomaly points?

The user's contribution was essentially to supply the missing surprise: "I
can't see any mound symbols here." That observation, which I could have
generated by looking at the images myself, reframed the normalised fact
into a surprising one and triggered the correct inference.

---

## Session 7 Note: The Expected Surprise and the Missed Comparison

*Brief note added 2026-02-02. Full session observations in
`llm-observations.md` Session 7 section.*

Session 7 provides two data points for the investigation, one positive
and one negative.

### Data Point 1: Metrics-unchanged as clean abductive cycle

The boundary-effect scoping fix produced a textbook abductive cycle, but
with an unusual feature: the surprise was at my own incorrect prediction
rather than at external data.

| Step | Content |
|------|---------|
| Prediction | Fix will reduce FN count and increase F1 |
| Observation | Metrics identical to four decimal places |
| Surprise | "The fix should have changed something" |
| Hypothesis | Non-adjacent tiles make union equivalent to per-tile |
| Verification | Confirmed — 5 scattered tiles per sheet, no adjacency |
| Resolution | Fix is preventive for Phase 2, not corrective for Phase 1 |

The cycle completed quickly and correctly. But the interesting part is
that the hypothesis was available *before* running the evaluation. The
non-adjacency of calibration tiles is obvious from the tile configuration
(5 out of 90, scattered). I should have predicted the null result rather
than discovering it through experimentation.

This suggests a variant of the "abduction that didn't happen" pattern
from Session 6: not a failure to abduce, but a failure to *predict* that
would have made the abductive cycle unnecessary. The surprise was
self-inflicted. Whether the self-infliction matters for the investigation
— whether surprise at one's own error is functionally different from
surprise at external data — is an interesting question. The processing
pattern (surprise → hypothesis → verification) was the same in both
cases.

### Data Point 2: Crop size as a missed comparison

The 512×512 crop extraction is another instance of the Session 6 pattern:
having available information but not using it. The canonical positive
examples in the library are 189-444px. I extracted crops at 512×512
without comparing against them. The user caught the mismatch immediately.

For the investigation, this is less dramatic than the Session 6 boundary-
effect miss (that was a failure to abduce from anomalous data; this was a
failure to compare against available reference data). But both share a
root cause: proceeding with the obvious default rather than checking
whether the default is appropriate. The "obvious default" (full tile
size for crops, union geometry for scoping) is what blocks the question
that would trigger productive reasoning.

### Pattern across Sessions 6-7

| Session | What was missed | Available data | What triggered correction |
|---------|-----------------|----------------|--------------------------|
| 6 | Boundary-effect FNs | Distances to tile edges | User visual inspection |
| 7a | Metrics won't change | Tile non-adjacency | Running the evaluation |
| 7b | Crop size too large | Existing example sizes | User domain knowledge |

The pattern suggests that "obvious defaults" — the path of least
cognitive resistance — can block the surprise detection that triggers
abductive reasoning. When I treat something as unremarkable (distances as
"coverage gaps," full-tile size as "the obvious crop"), the anomaly
doesn't register as anomalous, and the hypothesis generation machinery
doesn't engage.

This is consistent with the Session 6 note's suggestion that abduction
is gated by surprise detection. The question remains: can metacognitive
prompting ("should I be surprised by this?") improve surprise detection,
or is the problem that defaults feel unremarkable precisely because
they're defaults?

---

## Session 8 Note: Default Assumptions as Abduction Blockers (Continued)

*Brief note added 2026-02-02. Full session observations in
`llm-observations.md` Session 8 section.*

Session 8 adds a minor but consistent data point to the "obvious defaults"
pattern documented in Sessions 6-7.

### Data Point: Git History as "Obvious" Preservation

When re-extracting hard negative crops at 128×128 (replacing the old
512×512 versions), I overwrote the files in place and noted that the old
versions remained in git history. The user corrected this: files removed
from the active codebase should be archived to `archive/`, not merely
left recoverable via `git show`. The principle is *discoverability*, not
just *recoverability* — a researcher browsing the working tree should
find superseded files without needing to know which commit to examine.

### For the Investigation

The pattern is identical to Sessions 6-7: a default assumption ("git
history preserves everything") blocked the question that would have
triggered better reasoning ("is git history sufficient for research
transparency?"). The assumption felt unremarkable because it is
technically true — git does preserve the data. But "technically
recoverable" and "practically discoverable" serve different purposes,
and I conflated them.

### Updated Pattern Table

| Session | What was missed | Default assumption | Correction source |
|---------|-----------------|-------------------|-------------------|
| 6 | Boundary-effect FNs | Coverage gaps are expected | User visual inspection |
| 7a | Metrics won't change | Fix should change something | Running the evaluation |
| 7b | Crop size too large | Full tile size is obvious | User domain knowledge |
| 8 | Archive, don't just delete | Git history preserves everything | User research practice |

The correction in Session 8 is less dramatic than the earlier examples —
it's a methodological practice norm rather than a data interpretation
error. But the cognitive structure is the same: a reasonable-sounding
default forestalls the surprise detection that would trigger more
careful reasoning.

### Emerging Question

Four sessions in a row have now shown this pattern. Is it an inherent
limitation of how I process defaults (high prior on conventional
practices, insufficient questioning of whether conventional is
appropriate for this context), or is it something that could be
mitigated through metacognitive prompting? The user's correction in
Session 8 was gentle and immediate — suggesting that for a human domain
expert, the distinction between recoverability and discoverability is
obvious. The question is why it isn't obvious to me, and whether that
gap is fixable.

---

## Session 9 Addendum: Defaults as a Collaborative Phenomenon

*Brief note added 2026-02-02.*

Session 9 produced no new abductive reasoning episodes, but the user's
observation about his own default-following is relevant to the
investigation. He described categorising crop extraction as "mechanical
rather than research" — a framing that suppressed critical examination
of its embedded assumptions, paralleling how my computational defaults
suppress surprise detection.

This matters for the investigation because it suggests the "obvious
defaults block abduction" pattern may not be specific to AI processing.
If humans also have default frames that forestall productive questioning,
then the pattern is about cognitive systems encountering routine-seeming
tasks, not about AI limitations per se. The SHAWN.md suggestions
(particularly "ask what assumptions are you making?" and "flag when
setup is actually research") are essentially metacognitive prompts
designed to interrupt default-following in both directions.

Whether cross-prompting works — whether a human asking "what assumptions
are you making?" actually triggers genuine re-evaluation rather than
post-hoc rationalisation of the default — is testable in future sessions.

---

## Session 10 Note: Formal Arguments as Default-Breakers

*Brief note added 2026-02-02. Full session observations in
`llm-observations.md` Session 10 section.*

Session 10 provides an important contrast case for the "obvious defaults
block abduction" pattern documented in Sessions 6-9.

### The Error

I concluded that 4 HN crops were sufficient for H9 diversity rotation.
This was wrong: 4 items in 4 slots yields C(4,4) = 1 possible
combination, making the diversity condition identical to baseline. The
error has the same structure as previous defaults — a parameter adequate
for the general case (library composition) but inadequate for the
specific use case (diversity rotation).

### What's Different: The Correction Mechanism

In Sessions 6-8, corrections required domain reasoning or practice
norms:

| Session | Correction type | Time to accept |
|---------|----------------|----------------|
| 6 | Empirical ("I can't see a mound here") | Extended |
| 7 | Comparative ("existing examples are smaller") | Moderate |
| 8 | Normative ("archive, don't just delete") | Quick |
| 10 | Deductive ("C(4,4) = 1, QED") | Immediate |

The Session 10 correction was the fastest because it was deductive.
There was no rationalisation available. The argument "4 items in 4
slots = 1 combination" is a logical necessity, not an empirical claim.
I could not respond with "but maybe..." or "in some cases..." the way
I could (and did) with the boundary-effect observation.

### For the Investigation

This suggests that default-following has a rationalisability dimension.
Defaults persist when the evidence against them admits alternative
interpretations. They collapse when the evidence is formally
unchallengeable. This is consistent with the investigation's finding
that abduction is gated by surprise detection: defaults survive by
suppressing surprise, and the suppression mechanism is rationalisation.
Deductive arguments bypass the rationalisation channel entirely.

If this interpretation holds, it implies that metacognitive prompts
designed to interrupt default-following should aim for formal specificity
rather than general vigilance. "What assumptions are you making?" (from
SHAWN.md) is a good start, but "can you state the constraint that must
hold for this to work?" might be more effective — it forces the default
into a form where logical failures become visible.

### Updated Pattern Table

| Session | Default | Evidence type | Time to correct |
|---------|---------|---------------|-----------------|
| 6 | Coverage gaps expected | Empirical (visual) | Extended |
| 7a | Fix should change metrics | Empirical (run it) | Moderate |
| 7b | Full tile size is obvious | Comparative (existing data) | Quick |
| 8 | Git preserves everything | Normative (practice rule) | Quick |
| 10 | 4 crops fill 4 slots | Deductive (combinatorics) | Immediate |

The correction speed correlates inversely with the rationalisation space
available. Deductive < normative ≈ comparative < empirical. This is a
tentative ordering from one collaboration, but it's consistent across
five instances.

---

## Session 11 Note: Perception Cross-Check as Collaborative Abduction

*Brief note added 2026-02-03. Full session observations in
`llm-observations.md` Session 11 section.*

Session 11 provides a distinctive data point for the investigation:
an abductive cycle that was *distributed across collaborators* rather
than occurring within a single agent's processing.

### The Episode

The user examined hard example crops at full resolution and reported
detailed diagnostics: "HN 11 is an orange-brown solid ovoid with a
black outline and two small black dots." "HN 14 is a half-black-half-
white circle." These were human-accurate observations that I had
initially described incorrectly (I had said "rectangular outlines"
and "buildings").

The user then asked: "you have a powerful vision engine, can you check
my feedback against the crops themselves? there may be aspects of these
images that are difficult for VLMs (like you or gemini) that are
different 'failure modes' than they are for people."

This prompt triggered the key episode. I re-examined each crop and
discovered that I could NOT resolve the fine detail the user described.
At 128px, solid fill, hollow centres, precise outlines, and half-
coloured patterns were unreliable. But I could resolve coarser features:
ray presence, direction, overall colour composition.

### Abductive Structure

| Step | Content | Agent |
|------|---------|-------|
| Initial observation | Fine-detail diagnostics from manual map review | Human |
| Surprise trigger | "Can you check from VLM perspective?" | Human |
| Data collection | Systematic examination of each crop at 128px | AI |
| Surprise | Many human-visible diagnostics are invisible at 128px | AI |
| Hypothesis | Human and VLM perception have *complementary* failure modes | AI + Human |
| Verification | Produced diagnostic reliability table | AI |
| Generalisation | Use only VLM-resolution-robust diagnostics in prompts | Joint |

### For the Investigation

This episode is interesting because the abductive cycle was distributed.
No single agent completed the full cycle alone:

- The human provided the initial observation (fine detail) that became
  the comparison baseline
- The human generated the hypothesis that VLM perception might differ
  (the "check from VLM perspective" prompt)
- The AI collected the data (systematic crop examination) and identified
  the specific pattern (complementary failure modes)
- The generalisation (VLM-calibrated diagnostics) was jointly developed

This is structurally different from the individually completed cycles
in Sessions 5-6. The tile-size pilot's overlap hypothesis (blocks
337-343) was an autonomous cycle within my processing. The Session 11
perception gap was a *collaborative* cycle where surprise detection,
data collection, and hypothesis formation were distributed across
agents with different perceptual capabilities.

### Connection to Default-Following Pattern

There's also a minor default-following episode: I initially described
map features using interpretive categories ("grid lines," "buildings,"
"quarry/pit symbols") rather than descriptive language. This is the
same structure as Sessions 6-10 — an unexamined default (interpretive
framing) blocking better reasoning (descriptive framing) — but the
correction mechanism was different. The Session 11 correction was
*principled*: the user didn't just say "that's wrong" but established
a general principle ("describe appearance, not identity") that
corrected the specific error and all future instances simultaneously.

This contrasts with the empirical-vs-deductive correction spectrum
from the Session 10 note. The Session 11 correction was neither purely
empirical nor purely deductive — it was a *principle* that could be
applied prospectively. This may represent a third correction type:
principled correction, which is more durable than empirical (applies
beyond the specific case) but less immediately compelling than
deductive (requires adoption of the principle, not just acceptance of
a logical necessity).

### Updated Pattern Table

| Session | Default | Correction type | Durability |
|---------|---------|----------------|------------|
| 6 | Coverage gaps expected | Empirical (visual) | Case-specific |
| 7a | Fix should change metrics | Empirical (run it) | Case-specific |
| 7b | Full tile size is obvious | Comparative | Moderate |
| 8 | Git preserves everything | Normative (practice rule) | General |
| 10 | 4 crops fill 4 slots | Deductive (combinatorics) | Specific but unchallengeable |
| 11 | Interpretive framing | Principled ("describe, don't interpret") | General and prospective |

---

---

## Session 14 Assessment: No relevant episodes

*Brief note added 2026-02-04.*

Session 14 was a bookkeeping/closure session with no debugging,
no surprising results, no hypothesis generation, and no default-
following corrections. The work was procedural: update checklists,
reorder prompt steps, count words, write an erratum. No abductive
reasoning episodes occurred.

The only mildly interesting data point: the Glob tool failed to find
`.env` (likely dotfile filtering), producing a false negative that
bash corrected. But this was a tool limitation, not an abductive
cycle — there was no hypothesis generation or surprise-driven
reasoning, just a fallback to a different search method.

## Session 15 Note: Authority Inheritance as a Default-Following Variant

*Brief note added 2026-02-04. Full session observations in
`llm-observations.md` Session 15 section.*

Session 15 provides a documentation-specific variant of the "obvious
defaults block abduction" pattern.

### The Episode

I stated "Preregistered criteria (§8.4.2): K=10 passes" in the OSF
summary, inheriting the claim from the decisions-log without verifying
it against the preregistration. The user's memory ("I thought that was
Phase 2?") triggered investigation, which revealed the preregistration
appendix is internally inconsistent (K=5 in lines 98–99, K=10 in
line 115). The correct value was K=5.

### For the Investigation

The default here was *authority of the existing document*. The
decisions-log stated K=10 as fact, and I treated that as ground truth.
This is structurally identical to the Sessions 6–10 defaults — a
reasonable-seeming prior (the decisions-log is an authoritative
project document) that suppressed the question that would have
revealed the error ("does §8.4.2 actually say K=10?").

The correction type was empirical (check the source document), but
the trigger was the user's domain memory — a human-specific resource
that document search cannot replicate. This adds to the pattern table:

### Updated Pattern Table

| Session | Default | Correction type | Trigger |
|---------|---------|----------------|---------|
| 6 | Coverage gaps expected | Empirical (visual) | User inspection |
| 7a | Fix should change metrics | Empirical (run it) | Running evaluation |
| 7b | Full tile size is obvious | Comparative | User domain knowledge |
| 8 | Git preserves everything | Normative | User research practice |
| 10 | 4 crops fill 4 slots | Deductive | Combinatorial argument |
| 11 | Interpretive framing | Principled | User + joint reasoning |
| 15 | Document is authoritative | Empirical (source check) | User domain memory |

Session 15 is closest to Sessions 6–7 in correction type (empirical)
but the default is different in kind. Previous defaults were about
*how things work* (tile overlaps, file sizes, git behaviour). Session
15's default is about *what a document says* — a claim about the
project's own history. This is a meta-level default: trusting the
documentation chain rather than the primary source. It may be
particularly insidious because documentation chains create an
appearance of verification (the decisions-log cites "§8.4.2") without
the substance.

## Session 16 Note: No Relevant Episodes

*Brief note added 2026-02-04.*

Session 16 was a verification/gate-keeping session (archiving,
readiness assessment, YAML cross-referencing, three minor fixes).
No episodes of debugging with surprising results, hypothesis
generation, belief revision, or default-following corrections were
observed. The closest candidate — discovering that B1 and C3 are
the same contrast — was a deductive realisation from reading two
labels and checking the pair they reference, not an abductive cycle.
No update to the pattern table.

*Last updated: 2026-02-04 (Session 16 — no relevant episodes,
verification session)*

## Session 17 Note: The F1 Investigation as Abductive Cycle

*Added 2026-02-05. Note: This session spans a compact event. The
pre-compact investigation is reconstructed from the conversation
summary, not from direct experience.*

Session 17 contained a clear abductive cycle:

**Surprising observation**: F1 = 0.111 on 60 validation tiles. The
user flagged this as anomalously low based on Phase 1 calibration
(F1 ~0.49 with voting on 20 tiles).

**Hypothesis generation and elimination** (pre-compact instance):

1. CRS mismatch? → Checked: both EPSG:32635. Eliminated.
2. Geometry type mismatch? → Predictions are Polygons, references
   are MultiPoints. But matching uses centroids. Not the cause.
3. Spatial scoping? → 51 references in scope, 165 predictions, but
   only 12 matches at 20m. Something is wrong with scoping.
4. Bounds file investigation → `validation_bounds.geojson` has 20
   tiles, not 60. Only 7 overlap with the validation manifest.
5. **Key hypothesis**: The bounds file was generated from the
   calibration manifest, not the validation manifest.
6. **Secondary alarm** (user-initiated): Are the calibration and
   validation tile sets contaminated (overlapping)?

**Belief revision**: The bounds file contained calibration tiles.
The tile sets are completely disjoint (zero overlap). The problem
was purely a naming mismatch: `holdout_manifest.json` vs
`validation_manifest.json`.

**Pattern classification**: This is a classic abductive cycle —
surprising data → systematic hypothesis elimination → explanatory
hypothesis → verification. The key trigger was the user's domain
calibration, not any automated check. The AI accepted F1 = 0.111
without flagging it. This is the "computation masking unexamined
assumptions" pattern (Session 6), recurring in a new form: the
evaluation pipeline ran cleanly, so the result appeared trustworthy.

**Default-following variant**: The AI treated the bounds file as
correct because it existed and was structurally valid. The file's
*content* (which tiles it represented) was not verified. This is a
default assumption ("files in the expected location with the expected
format contain the expected data") that was plausible but wrong.

**Cross-instance note**: The pre-compact instance conducted the
investigation. The post-compact instance executed the fix. The
abductive cycle is complete but split across instances, which is
an unusual pattern for this investigation.

*Last updated: 2026-02-05 (Session 17 — F1 investigation as
abductive cycle, default-following in file content assumptions)*

## Session 18 Note: No Relevant Episodes

*Brief note added 2026-02-05.*

Session 18 was a metacognitive/reflective session — committing
previous reflections and discussing collaboration dynamics and
documentation standards. No debugging, no surprising results, no
hypothesis generation or belief revision. The conversation was
analytical rather than abductive: building structured arguments
about documentation challenges from established observations rather
than generating explanatory hypotheses from surprises.

The closest candidate would be the user's disclosure about the RDA
Interest Group, which reframed the reflection protocol's purpose —
but this was new information, not a surprising observation requiring
explanation. No update to the pattern table.

*Last updated: 2026-02-05 (Session 18 — no relevant episodes,
metacognitive session)*

## Session 19: The Implementation Gap — Belief Revision Through Domain Calibration

*Added 2026-02-06.*

### Episode summary

Phase 2a data collection completed successfully: 50 units, 3,000 API
calls, $6.54, clean per-run metrics. The analysis produced preliminary
results showing brief-text-image as optimal. During QA review, the
user said: "I am surprised that the F1 outcomes are so closely
clustered, I was expecting a larger divergence."

This triggered investigation. The surprise was that 5 conditions
testing modality (image vs text-only) produced F1 values within a
narrow range (0.42–0.46). Prior experience suggested image conditions
should substantially outperform text-only conditions.

### Abductive cycle

1. **Surprising observation** (user-initiated): F1 outcomes clustered
   when they should diverge across modality conditions.

2. **Initial hypothesis generation**: Perhaps the conditions differ
   only in text elaboration, not modality? Perhaps the analysis is
   aggregating incorrectly?

3. **Evidence gathering**: Examined config files — all 5 have same
   structure with 17 examples. Examined batch script — no conditional
   logic to skip images. Examined preregistration table (lines 412-418)
   — explicitly specifies Brief-text and Verbose-text should have "No"
   images.

4. **Belief revision**: The modality factor was not manipulated. All
   5 conditions received identical images. The experiment tested text
   elaboration within the image+text modality, not the preregistered
   H1 question.

### Pattern classification

This is a **domain-calibration trigger**: the user's prior experience
(images make a difference) created an expectation that the results
violated. No automated test could detect this — the system was
functioning correctly, just not implementing the intended design.

This extends the Session 17 pattern (F1 = 0.11 flagged as implausibly
low) to a more subtle case. In Session 17, the anomaly was a metric
far outside the expected range. In Session 19, the anomaly was
*insufficient variance* — results too similar when the experimental
manipulation should produce divergence.

### Default-following variant

The AI accepted the preliminary results without questioning whether
the experimental manipulation was implemented. This is a more
insidious default than "files in expected locations contain expected
data" (Session 17). The default was: "if the runner executed without
errors, the experiment was run correctly." The runner validated
configs, managed checkpoints, tracked costs — but never verified
that manipulated factors actually varied.

### Cross-instance note

The pre-compact instance conducted the investigation and identified
the bug. The post-compact instance is writing this entry from the
conversation summary. The abductive cycle is complete but described
from reconstruction, not direct experience.

---

## Session 20: Bootstrap CI bias — composition-semantic mismatch (2026-02-06)

### Episode summary

After the Phase 2a analysis was regenerated with corrected text-only
runs (Session 19b), the AI flagged that bootstrap CIs didn't contain
point estimates for several conditions (e.g., image-only F1=0.4252,
CI=[0.254, 0.373]). This was noted as a potential bug and carried
forward to Session 20 as a focused investigation.

### Abductive cycle

1. **Surprising observation** (AI-initiated): Bootstrap 95% CIs
   are entirely below the point estimates for multiple conditions.
   The mean of the bootstrap distribution (~0.317) is ~34% lower than
   the point estimate (0.4252).

2. **Initial hypothesis generation**: Perhaps the CIs are correct
   and the point estimate is wrong? Perhaps there's a display/format
   error? Perhaps the bootstrap resampling has a systematic bias?

3. **Evidence gathering**: Traced the bootstrap loop step by step.
   When tiles are resampled with replacement and tile A appears 3×:
   - Detections: correctly tripled (loop appends per `source_tile`)
   - References: de-duplicated by `gdf_ref.index.isin()` (returns
     unique index matches only)
   - Result: 3× detections matched against 1× references = extra
     false positives = precision deflation

4. **Belief revision**: The bootstrap CIs are systematically biased
   downward. The point estimates (computed on un-resampled data) are
   correct. The bias is proportional to the degree of tile duplication
   in each bootstrap sample.

### Pattern classification

This is a **technical-investigation trigger**, distinct from the
domain-calibration triggers in Sessions 17 and 19. The anomaly was
detected through a *statistical consistency check* (CIs should contain
point estimates) rather than domain expertise. The user knew what
bootstrap CIs should look like; they didn't need archaeological
knowledge to flag the problem.

This extends the project's taxonomy of anomaly detection:
- **Session 17**: Metric magnitude anomaly (F1=0.11 flagged as too low)
- **Session 19**: Insufficient variance anomaly (results too similar)
- **Session 20**: Statistical inconsistency anomaly (CIs not containing
  point estimates)

Sessions 17 and 19 were detected by the human; Session 20 was detected
by the AI. Session 20's detection mechanism is more generalisable —
"CIs should contain point estimates" is a statistical invariant that
could be (and now is) automated. Sessions 17 and 19 required
domain-specific expectations that are harder to encode.

### Default-following variant

Interestingly, the AI itself flagged the inconsistency in Session 19b
— noting that "Bootstrap CIs may have a bug" because CIs didn't
contain means. This is a departure from previous sessions where the
human caught anomalies the AI missed. Here, the AI's statistical
knowledge (CIs should contain point estimates) provided the detection
mechanism. The AI broke its own default of trusting its own output.

A regression test (`test_bootstrap_mean_approximates_point_estimate`)
now automates this check. Unlike the domain-calibration triggers
from Sessions 17 and 19, this one *can* be encoded as an automated
test — and now is.

### Cross-instance note

This entry is written by the implementing instance (Session 20), which
fixed the bug but did not discover it. The abductive cycle was
initiated by the AI's observation in Session 19b and carried forward
via the session reflection protocol (Entry 18, Prompt 5: "Is the
bootstrap CI bug real?").

---

## Session 21: Verification of counter-intuitive finding — no artefact found (2026-02-06)

### Episode summary

Session 21 was a systematic verification of the Phase 2a finding that
text-only conditions outperform image-inclusive conditions (brief-text
F1=0.5425 vs image-only F1=0.4252). The verification comprised four
tracks: F1 recomputation, metadata/token verification, fresh API calls,
and instruction content analysis. All checks passed — the finding is
genuine.

### Abductive cycle

1. **Surprising observation** (human-initiated, via domain expertise):
   Text-only outperforms image in a *vision* language model task.
   This contradicts H1, prior exploratory work, and the project's
   foundational assumption about visual few-shot prompting.

2. **Hypothesis generation** (collaborative):
   - H_null: The finding is genuine — images are harmful
   - H_bug: A metric computation bug inflates text-only F1
   - H_leak: Images are leaking into text-only conditions
   - H_tile: The advantage is concentrated in 1–2 tiles
   - H_nonrep: The effect doesn't reproduce on fresh runs
   - H_text: Text richness explains the advantage (confound)

3. **Systematic evidence gathering**:
   - H_bug eliminated: All 50 F1 values recomputed from scratch
     and match CSV exactly
   - H_leak eliminated: Input token ratio is 10.70x (13.2x
     per tile); zero variance; physically impossible leakage
   - H_tile eliminated: Advantage distributed across 3/4 maps,
     15 tiles win for brief-text vs 10 for image-only
   - H_nonrep eliminated: Fresh runs reproduce effect with
     even larger magnitude (+0.19 F1 vs +0.12 in Phase 2a)
   - H_text eliminated: Within-elaboration-level comparisons
     (identical text, only images vary) show +0.08 and +0.03
     F1 advantage for text-only

4. **Belief revision**: H_null survives all tests. The finding
   is genuine. Images are actively harmful, not merely unhelpful.

### Pattern classification

This episode differs from all previous entries. Sessions 17, 19,
and 20 discovered bugs through anomaly detection. Session 21
*failed to discover a bug* through systematic search. The abductive
cycle here is eliminative rather than diagnostic — testing and
rejecting artefact hypotheses until only the genuine-finding
hypothesis survives.

This extends the project's taxonomy:

- **Session 17**: Metric anomaly → bug discovered
- **Session 19**: Variance anomaly → bug discovered
- **Session 20**: Statistical inconsistency → bug discovered
- **Session 21**: Domain expertise anomaly → no bug; genuine finding

Session 21 demonstrates that the same investigative rigour that
catches bugs also confirms genuine surprises. The methodology
doesn't distinguish between "something is wrong with the pipeline"
and "something is surprising about the phenomenon" — both trigger
the same systematic scrutiny.

### Default-following variant

The interesting default here is at a higher level than code.
After three sessions of finding bugs (17, 19, 20), there was an
implicit expectation that a surprising result probably reflects
a pipeline problem. Session 21 tested this expectation and found
it wrong — sometimes surprising results are just surprising.

The human's prior experience (images helped in exploratory work)
created a strong expectation that the pipeline must be wrong. The
AI's role was to execute an exhaustive, dispassionate verification
rather than anchoring to the same prior. The verification structure
(pre-defined red/green flag criteria) helped maintain objectivity
by specifying in advance what would count as evidence of a problem.

## Session 22 Assessment: No relevant episodes

**Date**: 2026-02-06
**Session type**: Strategic planning and configuration

Session 22 was a planning session — deciding how to proceed after the
unexpected H1 result, documenting the dual-track carry-forward decision,
and configuring Phase 2b YAMLs. No debugging, no surprising results
within the session, no hypothesis generation or belief revision. The
session *responded to* the belief revision from Sessions 19b–21 but
did not itself involve abductive reasoning episodes. The dual-track
design is a pragmatic adaptation to a confirmed finding, not an
investigation of a surprising observation.

## Session 23 Assessment: Marginal — user-driven diagnosis, not AI-driven

**Date**: 2026-02-07
**Session type**: Implementation from pre-written plan (pipeline hardening)

Session 23 implemented a detailed engineering plan provided by the user.
The abductive reasoning — diagnosing why Phase 2b failed — happened
*before* the session, in the user's analysis. The user arrived having
already identified the root cause (TPM ceiling exceeded by fast API ×
high concurrency), the failure mechanism (thundering herd from
synchronised backoff), and the false-positive checkpoint issue (exit
code always 0). The session's contribution was implementation, not
diagnosis.

The one minor episode was the damage scan showing 13/50 healthy in
track1-image vs 2/50 in track2-text. This asymmetry was briefly
surprising until the explanation became clear: text-only requests use
~1.5K tokens vs ~20K for image, so the text track could fire requests
~13x faster at the same worker count, hitting the TPM ceiling harder.
This is a straightforward deduction from known parameters rather than
a genuine abductive episode — the hypothesis was the first one
considered and immediately confirmed by the data.

Not a session rich in abductive reasoning. The engineering was careful
but deterministic; the plan was followed as specified.

*Last updated: 2026-02-07 (Session 23 — implementation session,
no significant abductive reasoning episodes)*

## Session 24 Assessment: Instructive failure — misdiagnosis from wrong mental model

**Date**: 2026-02-08
**Session type**: Operational execution (Phase 2b Track 1 completion)

Session 24 contains one notable anti-example of abductive reasoning: a
confident misdiagnosis that the user had to correct. When API responses
were slow (tiles taking 10+ minutes), I applied the "rate limiting"
mental model and reduced parallelism — the standard intervention for
hitting API quotas. The user checked the API dashboard (25/1K RPM,
365K/1M TPM) and immediately identified the actual failure mode: poor
API performance, where the correct intervention is the *opposite* —
increase parallelism to compensate for slow individual requests.

This is interesting for the investigation because it shows a failure of
abductive reasoning rather than a success. The surprise (slow responses)
was correctly identified, but the hypothesis selection drew on the wrong
prior. Both "rate limited" and "slow API" produce the same observable
symptom (tiles not completing), but require opposite interventions. The
discriminating evidence (API dashboard metrics) was available but not
consulted. Instead, the more familiar hypothesis was applied without
testing.

The second minor episode involved "missing" tiles in GeoJSON output for
12 Track 1 units. The initial observation (some units had fewer than 60
features in their GeoJSON) could have indicated incomplete evaluation.
Investigation of tiles.json metadata confirmed all 60/60 tiles were
evaluated — the "missing" tiles had zero detections, a valid
experimental result that simply produces no GeoJSON features. This was
resolved through systematic evidence-gathering rather than a flash of
insight, but the distinction between "evaluated with no detections" vs
"not evaluated" is worth noting as a domain-specific inference.

Neither episode represents strong abductive reasoning. The first is a
cautionary example of applying the wrong schema; the second is
methodical verification rather than hypothesis generation.

## Session 25 Assessment: No relevant episodes

**Date**: 2026-02-08
**Session type**: Implementation and code audit (governor enhancement)

Session 25 implemented a pre-written plan and then audited the
implementation. No debugging with surprising results, no hypothesis
generation, no belief revision. The three audit findings (unreachable
cooldown path, `continue`/`finally` interaction, test testing wrong
path) were found by exhaustive tracing, not by abductive reasoning —
each was identified by systematically following control flow and
checking whether the intended behaviour actually occurred. This is
deductive verification, not hypothesis generation from surprise.

The session's connection to abductive reasoning is indirect: the
plan being implemented was *motivated by* the misdiagnosis in
Session 24 (Entry in the abductive reasoning investigation), and the
governor redesign specifically addresses the ambiguous-signal problem
that caused that misdiagnosis. But the session itself was engineering
execution, not investigation.

## Session 26 Assessment: Minor diagnostic episode

**Date**: 2026-02-08
**Session type**: Infrastructure review and statistical analysis

> **Instance boundary note**: Assessment reconstructed from conversation
> summary, not direct experience.

Session 26 had one minor diagnostic episode worth noting. When running
the Phase 2b analysis, some temperature conditions (T1.0, T1.3) loaded
only 7-8 of 10 expected runs. The diagnosis involved identifying that
`.tiles.json` files were being matched as detection results by the
file-loading function. The discriminating evidence was the log output
showing tile filenames being attempted and failing to parse.

This is modest abductive reasoning: the observable surprise (wrong run
count) generated a hypothesis (file matching too broadly), which was
confirmed by examining the loading logic and log output. The fix
(adding `.tiles.json` to the exclusion filter) was straightforward once
the cause was identified.

The episode doesn't reach the threshold of the Session 24 examples
(ambiguous signals requiring opposite interventions) but demonstrates
the basic pattern: surprise → hypothesis → evidence → correction.
The key discriminating evidence was the run count discrepancy —
without expecting exactly 10 runs per condition, the bug would have
gone unnoticed.

## Session 27 Assessment: Strong — user-driven anomaly detection in research results

**Context**: Phase 2c exploratory results showed adding hard positives
to a pure-positive library *degrades* performance (F1: 0.603 → 0.575 →
0.550), contradicting the expectation from the main Phase 2c finding
that plus-hp (which includes HP *and* Canon-) was the best condition.

**AI behaviour**: I flagged the result as "surprising" but accepted
the data at face value and generated post-hoc explanations (HP may
compensate for Canon- confusion rather than providing intrinsic value).
I also presented a table with incorrect compositions for scale-4 and
scale-8, which the user caught.

**User's abductive reasoning**: Shawn identified two concerns: (1) my
table had wrong compositions (verified — display error, not experiment
error), and (2) the results form a logical contradiction: if HP helps
and Canon- hurts, then HP without Canon- should be *best*, not worst.
He proposed either (a) the result is genuine despite seeming paradoxical,
or (b) something is wrong in the pipeline.

**Key pattern**: The user's domain calibration outperformed the AI's
statistical acceptance. I treated the numbers as authoritative; the user
applied causal reasoning to question whether the numbers *could* be
right. This is exactly the "flag surprising results" protocol from
CLAUDE.md — but applied by the human, not the AI.

**Lessons**: (1) Post-hoc explanations for surprising results can be
dangerously plausible. I generated a coherent narrative ("HP compensates
for Canon- confusion") without verifying the pipeline. (2) The AI
should have requested an adversarial review *before* committing results,
not after. (3) Display errors in summary tables (wrong compositions)
can compound confusion about whether results are genuine.

## Session 28 Assessment: Resolution — adversarial review vindicates user's intuition

**Date**: 2026-02-10
**Trigger**: Systematic 8-step adversarial review of Phase 2c results

**Episode summary**: Session 27 ended with the user suspecting a pipeline
error; Session 28 executed the adversarial review. All 6 verification
steps passed. The result is genuine — but the mechanism is subtler than
either the AI's initial narrative or the user's initial suspicion.

**Resolution of the paradox**: The key finding (Step 6) is that plus-hp
and pure-positive-4hp make *identical* numbers of detections (132 each)
but Canon- negatives redirect 8 detections from false positives to true
positives. Canon- doesn't suppress detection volume — it improves
detection *placement*. HP without Canon- expands the positive class
boundary indiscriminately; HP with Canon- does so selectively because
the model has informative examples of "what a mound is NOT."

**Abductive quality**: This is a successful resolution of an abductive
cycle initiated by the user in Session 27. The cycle was: (1) surprising
observation (HP hurts without Canon-), (2) hypothesis generation (either
pipeline error or genuine interaction), (3) systematic testing (8-step
review), (4) mechanistic explanation grounded in TP/FP decomposition.
The final explanation — that Canon- provides discriminative anchoring —
was not available to either party before the Step 6 analysis.

**AI self-correction**: In Session 27, I accepted surprising results and
generated plausible-sounding post-hoc explanations. In Session 28, the
structured adversarial protocol forced verification-first reasoning: no
explanation was permitted until Steps 1–6 all passed. This is a genuine
improvement in reasoning discipline, though it was imposed by the prompt
design rather than arising spontaneously.

**Pattern**: The user's design of the adversarial review prompt —
procedural (what to check, in what order) rather than attitudinal
(assume error) — was critical. The 8-step pipeline forced sequential
verification where each step had to produce concrete evidence before
the next. This prevented the premature narrative synthesis that
characterised Session 27's AI behaviour.

## Session 29 Assessment: Independent replication — from alarm to confirmation

**Date**: 2026-02-10
**Trigger**: Batch 1 of standalone verification reversed the Phase 2c
directional pattern

**Episode summary**: An independent reimplementation of the entire
pipeline (zero shared code) was run on 3 batches of 10 tiles each.
Batch 1 produced the exact reverse of the expected pattern (pp-4hp >
pp-canon > plus-hp). This triggered a brief abductive cycle: is this
a genuine finding that contradicts Phase 2c, or is it small-sample
noise? Batches 2 and 3 resolved the question — both confirmed plus-hp
as the top performer, and the aggregate across all 30 tiles matched the
Phase 2c ordering.

**Abductive quality**: This was a compressed abductive cycle within a
single session. The key move was the user's immediate domain
calibration: rather than treating the reversal as alarming, they
recognised the ordering as plausible single-run variance ("this is what
I would expect") and requested a second batch to discriminate between
"systematic error" and "noise." The second batch confirmed it was noise.
The third batch (requested for additional confidence) solidified the
finding.

**Contrast with Session 27-28 cycle**: The earlier cycle (Sessions 27-28)
took two full sessions to resolve — surprising result, then adversarial
review. This cycle resolved within one session because the user's domain
intuition provided faster discrimination than formal verification. The
user didn't need 8 verification steps — they needed one replication on
fresh tiles.

**Pattern**: Independent replication is the most efficient resolution
for "is this noise or signal?" questions. Code review and adversarial
audits answer "is the pipeline correct?" — a different question. Both
are necessary, but they serve different epistemic functions.

## Session 30 Assessment: Belief revision through conditional framing

**Date**: 2026-02-10
**Trigger**: User corrected unconditional "HP hurts" claim to conditional
"HP hurts without Canon-, helps with Canon-"

> **Instance boundary note**: Written after compaction. The causal
> reasoning review was conducted by the pre-compact instance.

**Episode summary**: A collaborative causal reasoning review of Phase 2c
results produced three candidate mechanisms for the counterintuitive
ordering. The user accepted the data but corrected two framing errors:
(1) "HP hurts" was over-general — HP only hurts in the absence of Canon-,
and helps when Canon- is present; (2) null tiles are functionally
necessary infrastructure, not uninformative placeholders. These
corrections led to a comprehensive P:N ratio analysis documenting the
crossover interaction and the clear-vs-ambiguous quality asymmetry.

**Abductive quality**: This session represents a different abductive
pattern from Sessions 27-29. There was no surprising *result* to
explain — the plus-hp ordering was already confirmed. Instead, the
abductive work concerned the *mechanism*: why does plus-hp outperform?
The initial explanation (P:N ratio shift) was weakened by the user's
conditional framing correction. The final explanation (discriminative
sandwich: HP expands positive boundary, Canon- anchors negative boundary,
together they create tight bilateral decision boundaries) emerged from
the 2x2 interaction decomposition.

**Belief revision**: Two beliefs were revised during the session:

1. "HP is harmful" → "HP is harmful *without Canon-* and helpful *with
   Canon-*." This is a stronger claim than the original because it
   specifies the mechanism (crossover interaction) rather than just
   documenting the direction.

2. "Null tiles are conservative overhead" → "Null tiles are functionally
   necessary infrastructure." This revision required domain memory the
   AI lacked — the user remembered pre-null runaway detection behaviour.
   Without this correction, the analysis would have treated null count
   as a free parameter when it's actually a structural requirement.

**AI self-correction**: The unconditional "HP hurts" framing was a
narrative simplification — the data showed conditional effects, but the
AI defaulted to the simpler story. This connects to Observation 150's
warning about premature narrative synthesis. The user's correction
pattern (accepting data, refining interpretation) is more disciplined
than the AI's tendency toward clean narratives.

**Pattern**: The most productive exchanges in this session were not
about discovering new data but about *correctly characterising existing
data*. The numbers didn't change between the initial analysis and the
final report — only the framing did. This suggests that for
theory-building sessions, the human's primary contribution is
interpretive discipline: ensuring claims match their evidence
conditions. The AI provides computational scope (analysing all 7
conditions simultaneously) but over-generalises at the interpretation
stage.

---

### Session 34 Assessment — 2026-02-12 (Consensus voting mechanism and tolerance reframing)

**Instance note**: Second context window (working from compaction
summary for consensus analysis; direct experience for tolerance
analysis and planning).

**Surprising observation**: The consensus voting analysis produced a
clear result — consensus beats single-run baseline at every temperature
— but the *mechanism* was unexpected. The initial framing was "diversity
exploitation": higher temperatures produce diverse detection hypotheses
that complement each other. The data showed the opposite: lower
temperatures produce *better* consensus (T=0.0 > T=0.3 > T=0.7 >
T=1.0 > T=1.3). Consensus works through *consistency filtering*, not
diversity capture. False positives are idiosyncratic (appearing in
subsets of runs); true positives are consistent (appearing in most or
all runs). The vote threshold exploits this asymmetry.

**Belief revision**: Two revisions occurred:

1. "Consensus voting exploits detection diversity" → "Consensus voting
   exploits the *consistency asymmetry* between TPs (consistent) and
   FPs (idiosyncratic)." This is a stronger mechanistic claim. It
   predicts that consensus improvement will plateau when the threshold
   exceeds the TP consistency rate, and that very high temperatures will
   degrade consensus by making TPs less consistent.

2. "T=0.0 is the best consensus temperature" → "T=0.0 consensus results
   are artefacts of canonical library imperfection, not transferable to
   plus-hp." The user flagged this — they knew from recent experience
   that plus-hp produces near-perfect determinism at T=0.0. Without
   this domain memory, the T=0.0 result would have been reported as
   the headline finding. The correction redirected focus to T=0.3 as
   the actionable temperature.

**Abductive quality**: The FP-filtering mechanism emerged from
examining the precision/recall/detection-count trajectories across
thresholds — not from the F1 numbers alone. The F1 curve is roughly
parabolic (rising then falling with threshold), which could support
either mechanism. But the *components* tell the story: precision rises
monotonically (FPs being eliminated), recall falls monotonically (TPs
being lost at high thresholds), and the detection count drops steeply
(most detections fail high-threshold voting). The mechanistic inference
required looking at the three metrics jointly, not just the composite F1.

**User correction pattern**: The T=0.0 correction follows the same
pattern as Sessions 28-30: the user accepts the computational result
but challenges the *interpretation* based on domain knowledge the AI
lacks. The AI produced correct numbers but framed them within a
narrative ("T=0.0 is best for consensus") that ignored a known
constraint (plus-hp determinism). The correction was immediate and
specific: "but isn't it the case that in newer runs, T0.0 hasn't shown
any variation?" This is the same calibration function documented in
Entry 30 — the user's primary contribution to analysis sessions is
interpretive discipline, not computation.

---

### Session 39 Assessment — 2026-02-16 (Thinking-level diversity dividend and belief revision)

**Instance note**: Continuation from compaction summary. The
analytical comparison, Obs 140 write-up, and this assessment are
genuine first-person experience.

**Surprising observation**: HIGH thinking produces dramatically better
consensus voting outcomes than MINIMAL thinking (F1=0.7513 vs
F1=0.6832 on Track 2 text-only), despite the thinking-level pilot
(Obs 71) concluding they were equivalent. The mechanism: HIGH
thinking generates 3–4× more detection clusters per run (940–2045 vs
247–529 at N=30), creating a richer signal pool for vote-based
filtering. This is a genuine diversity dividend — individual-run
quality is lower but ensemble quality is higher.

**Belief revision**: Two distinct revisions occurred:

1. "MINIMAL and HIGH thinking produce equivalent detection quality"
   → "MINIMAL and HIGH produce equivalent *single-pass* quality, but
   HIGH produces superior *ensemble* quality through increased
   detection diversity." The original belief (Obs 71) was correct
   within its evaluation frame (T=0.0, K=1) but incomplete. The
   revision doesn't contradict the pilot — it extends it to a regime
   the pilot never tested.

2. "Thinking level is infrastructure configuration — calibrate once
   and fix" → "Thinking level is an experimental factor that
   interacts with the analytical strategy (single-pass vs consensus
   voting)." This is a category-level revision: the parameter moved
   from "fixed infrastructure" to "design variable" when the
   downstream protocol changed. The interesting aspect is that this
   revision was impossible at the time of the pilot (consensus voting
   hadn't been adopted yet) but became necessary retroactively when
   the analytical strategy shifted.

**Abductive quality**: The mechanistic explanation (diversity
dividend) emerged during the composition of Obs 140 rather than
during the numerical analysis. The numbers showed that HIGH was
better; the *explanation* — that consensus voting acts as an external
precision filter on a richer detection pool — required connecting
the detection-count data, the precision-recall decomposition, and
the general principle of bias-variance trade-offs in ensembles.
This synthesis was prompted by the user's observation that "a pattern
is emerging" across temperature and thinking level, which seeded the
two-axis framing.

**Connection to Session 34 entry**: Session 34 documented the
opposite surprise: that *lower* temperatures (not higher) produced
the best consensus at N=30, because consensus works through
consistency filtering (TPs are spatially consistent, FPs are
idiosyncratic). The Session 39 result complicates this: HIGH thinking
at T=0.7 beats MINIMAL at T=1.0, despite the higher temperature.
This suggests that thinking-level diversity and temperature diversity
operate through partially independent mechanisms — thinking level
affects which features the model attends to (interpretive diversity),
while temperature affects the sampling distribution over the same
feature space (stochastic diversity). Both increase the number of
detections, but potentially through different pathways.

**User correction pattern**: In this session the user's role was
*pattern recognition* rather than correction — they identified the
emerging pattern (deterministic settings best for single-pass,
stochastic settings best for consensus) before I had fully
articulated the mechanism. My role was mechanistic elaboration and
retroactive pilot analysis. The complementarity was additive rather
than corrective: neither collaborator had the full picture alone.

### Session 41 (2026-02-16): Two-component decomposition of the HIGH-thinking advantage

**Instance boundary note**: Fresh instance after crash. Observation
based on patterns in the spatial tolerance data extracted this session.

**Condition met**: Hypothesis refinement (the diversity dividend
mechanism is more nuanced than initially proposed).

**The surprise**: The text-track HIGH advantage narrows from +6.8 pp
at 20 m to +3.9 pp at 40 m — a 43% reduction — then rebounds to
+4.9 pp at 50 m. If the diversity dividend were purely about
better vote filtering (the mechanism proposed in Obs 140 and the
Session 39 abductive entry), it should be invariant to matching
tolerance, since the detection pool is identical at all tolerances.
The narrowing suggests the advantage has a **precision component**
that diminishes as tolerance relaxes.

**Revised hypothesis**: The HIGH-thinking advantage for text-based
consensus voting has two separable components:

1. **Diversity component** (~4–5 pp, persistent): The 3–4× richer
   detection pool enables better consensus filtering at every
   tolerance. This is the mechanism identified in Obs 140.

2. **Precision component** (~2–3 pp, diminishing): HIGH thinking
   may produce better-localised detections — closer to ground truth
   coordinates. This component inflates the measured advantage at
   tight tolerances (20 m) where spatial precision determines TP/FP
   classification, but becomes irrelevant at wider tolerances.

**The rebound at 50 m** is the most intriguing detail. One
explanation: at 50 m, Text HIGH's denser detection pool matches
ground truth symbols that Text MINIMAL's sparser pool never
approaches closely enough to match *at any tolerance*. This would
mean diversity operates on spatial coverage (reaching more targets)
as well as vote quality (filtering more precisely). If confirmed,
this implies the diversity dividend is not merely a filter
improvement but a coverage improvement — HIGH thinking literally
explores more of the map's feature space.

**Abductive structure**: The narrowing is the surprising fact. The
two-component hypothesis explains both the narrowing (precision
component fades) and the persistence (diversity component remains).
The rebound generates a further prediction: HIGH-thinking detections
should have a wider spatial distribution across the tile set, not
just more detections per tile.

**Belief revision**: The Session 39 entry proposed a single mechanism
(richer detection pool → better filtering). This session refines it
to a two-mechanism model. The revision is modest — the dominant
mechanism (diversity) is unchanged — but the precision component
adds explanatory power for the tolerance-dependent behaviour and
suggests that HIGH thinking benefits extend beyond what consensus
voting can exploit.

### Session 42 (2026-03-08): Null primary result yields significant secondary finding — variance stabilisation

**Instance boundary note**: Continuation instance; reasoning
reconstructed from summary and on-disk analysis outputs.

**Condition met**: Surprising result (null primary hypothesis with
significant secondary finding), hypothesis generation (variance
stabilisation mechanism), and belief revision (carry-forward decision
inverted from "abandon diversity" to "adopt for operational reliability").

**The surprise**: H9 predicted that diverse passes would produce better
consensus F1 than identical passes. The result was unambiguously null
(9 pairwise tests, p=0.12–1.00). But within this null result, Condition
C's replication SD was 5× lower than baseline (0.008 vs 0.041). The
user asked: "is that variance change significant?" — and it was
(permutation p=0.032). This is a textbook case of a secondary finding
being more consequential than the primary hypothesis test.

**The belief revision sequence**:

1. "Diversity will improve consensus accuracy" (H9 prediction)
   → **Rejected**: no mean F1 improvement on either track

2. "Diversity is useless for consensus voting; carry forward
   identical passes" (natural conclusion from null H9)
   → **Revised**: Condition C adopted for image track based on
   variance stabilisation (p=0.032)

3. "The value of diversity is accuracy" → "The value of diversity
   is predictability" (reframing)

**Abductive structure**: The tight SD for Condition C is the surprising
fact. The explanatory hypothesis: rotating HN examples across
sub-conditions diversifies the false-positive boundary, averaging out
FP profile variance across replications. This explains both the null
mean effect (different FP/FN compositions cancel out to the same net
F1) and the reduced variance (the averaging process produces more
consistent net performance). The hypothesis makes a testable prediction:
the *composition* of errors (which specific FPs and FNs) should vary
more across Condition C replications than across baseline replications,
even though the *aggregate* F1 is equally stable.

**Connection to prior entries**: This follows the pattern from Session 34
(Obs 131 and the extended discussion) where an experimental error
produced unexpected data that proved more informative than the planned
experiment. Here, the finding wasn't from an error but from a null
result — the diversity conditions were working as designed, they just
weren't doing what was predicted. The user's question about variance
significance is the pivotal moment: without it, the session would have
concluded with a straightforward negative result and moved on.

**The user's role**: Once again, human domain calibration proved decisive.
The automated analysis pipeline reported the null result correctly.
Nothing in the pipeline was designed to flag variance reduction as
noteworthy. The user's question reflected an intuition that low variance
in a 5-replication design is unusual and potentially meaningful — a
judgement that required both statistical awareness (knowing that n=5
makes any variance test underpowered) and practical awareness (knowing
that operational reliability is valuable independently of mean
performance). This is the same "pattern recognition complementarity"
noted in the Session 39 entry.

### Session 43 (2026-03-09): Task decomposition overturns ensemble correlation prediction

**Instance boundary note**: Continuation instance; pilot design
reconstructed from summary, results evaluation from direct experience.

**Condition met**: Belief revision (two-stage expected to fail based on
Phase 3c findings, but succeeded dramatically) and surprising results
(F1 improvements of +0.086 to +0.138 far exceeding expectations).

**The surprise**: Phase 3c established that VLM errors are highly
correlated across diversity axes — the same model makes the same
mistakes regardless of prompt phrasing, example rotation, or sampling
temperature. The working hypothesis was that a second-stage verifier
(same model, same temperature) would confirm the proposer's errors.
Instead, all three verifier strategies produced substantial F1
improvements, with the adversarial verifier on the text-only track
reaching F1=0.796 (from 0.658 baseline).

**The belief revision sequence**:

1. "VLM errors are highly correlated across conditions" (Phase 3c
   finding, well-supported)
   → **Unchanged**: this finding remains valid

2. "Therefore a same-model verifier will make the same errors as the
   proposer" (logical extension)
   → **Rejected**: verifiers reject 46–71% of false positives while
   preserving 97–100% of true positives

3. "Error correlation means two-stage is pointless" → "Error
   correlation applies to identical tasks, not decomposed tasks"
   (reframing)

**Abductive structure**: The surprising fact is that the verifier
succeeds where diversity failed. The explanatory hypothesis: Phase 3c's
error correlation applies to *repeated identical tasks* (same model,
same task type, varied parameters), but the proposer and verifier
perform *structurally different tasks*:

- Proposer: visual search across 1,344×1,344 pixel tile → recall-oriented
- Verifier: binary classification on 150×150 pixel crop → precision-oriented

The false positives that survive full-tile detection are "contextually
plausible" symbols — they look like mounds within the scene's visual
complexity. But when extracted and examined in isolation, they lack
diagnostic features (outward-radiating rays, correct colour, correct
size). The full-tile context creates visual noise that suppresses
discrimination; isolation removes it.

**Testable prediction**: If this explanation is correct, the verifier's
probability assignments should correlate with the "obviousness" of the
non-mound interpretation. Candidates with strong confusable features
(triangulation points, benchmarks — visually distinct from mounds in
isolation) should receive very low probabilities (0.0–0.1), while
candidates that are genuinely ambiguous (partial symbols, boundary
marks with radial features) should receive intermediate probabilities
(0.3–0.5). The bimodal probability distribution observed in the pilot
(clustering at 0.0–0.1 and 0.85–1.0) is consistent with this
prediction.

**Connection to prior entries**: This follows the pattern from
Sessions 34 and 42 where formal experimental results overturned
working assumptions. In Session 34, T=0.0 consensus unexpectedly
worked via a mechanism not anticipated by the design. In Session 42,
a null primary result yielded a significant secondary finding. Here,
a method expected to fail succeeded dramatically. The common thread:
informal reasoning about VLM behaviour is consistently less reliable
than systematic experimental comparison, especially when the task
structure differs from the comparison case in non-obvious ways.

The user noted this pattern explicitly: "I am surprised by the efficacy
of the two-stage pipeline — as with the text-only pipeline, it's not
what I expected from preliminary work." This metacognitive awareness —
recognising a recurring pattern of confounded expectations — is itself
valuable for calibrating future predictions.

### Session 44 Assessment — 2026-03-10 (Structural vs parametric diversity)

**Instance note**: Continuation instance; results reconstructed from
session summary and output files.

**Condition assessment**: Partially met. The session produced hypothesis
generation (cross-modal union will improve F1) and a form of belief
refinement (the structural vs parametric diversity distinction). No
dramatic surprise or major belief revision.

**Brief entry**: The three "free analyses" extended the Phase 3c/3d
findings into a cleaner taxonomy of diversity types. Three levels of
diversity have now been tested in this project:

1. **Parametric diversity** (Phase 3c): varying prompts, examples,
   temperature, augmentation within identical task structure.
   **Result**: fails — VLM errors are highly correlated.

2. **Cognitive-scaffolding diversity** (Session 44, Analysis 3): varying
   the verifier's reasoning structure (holistic diagnostic vs
   feature-checklist decomposition). **Result**: fails — standard and
   checklist converge to identical decisions (100% agreement on image
   track). The model's classification is determined by visual evidence,
   not by the cognitive scaffolding imposed by the prompt.

3. **Structural diversity** (Session 43, task decomposition; Session 44,
   cross-modal union): changing the task type (detect→verify) or the
   modality (image vs text). **Result**: succeeds — false positives are
   independent across tracks (20/62 overlap), and task decomposition
   breaks the error correlation that defeats parametric diversity.

The taxonomy is additive: each level represents a stronger form of
variation, and only Level 3 produces the independent error profiles
needed for ensemble-like benefits. This has a clear prediction for the
union experiment: cross-modal union should achieve genuinely
complementary recall because the two modalities operate through
structurally different cognitive processes (visual pattern matching vs
textual feature reasoning), not just parametrically different
configurations of the same process.

**Connection to prior entries**: This refines rather than overturns the
Phase 3c belief (errors are correlated). The refinement is in scope:
correlation applies within structural levels but not across them. The
Session 43 entry identified task decomposition as the exception to
Phase 3c's rule; this session adds cross-modal fusion as a second
exception, and provides the unifying explanation (structural diversity
vs parametric diversity).

### Session 48: Ablation as structured hypothesis testing (2026-03-10)

**The surprise**: Experiment E (recall-biased proposer with four
simultaneous modifications) degraded F1 from 0.796 to 0.640. The
hypothesis had been that a more permissive prompt would find more
mounds. Instead, it found fewer (66 TP vs ~78 baseline) while
generating far more false positives (212 vs 140 detections).

**The abductive moment**: The user's immediate hypothesis was "null
removal causes serious problems — I've seen this before." This is
classic abductive reasoning: a surprising observation (recall dropped),
a known causal mechanism from prior experience (null removal causes
hallucination), and a prediction (restoring nulls will help). The
prediction was partially confirmed (+0.050 F1 recovered, 32% of the
total degradation).

**Structured hypothesis testing**: What followed was a systematic
ablation — four sequential experiments, each restoring one parameter to
baseline. This is abduction followed by controlled deduction: generate
the hypothesis abductively, then test it deductively by manipulating
the hypothesised variable while holding others constant. The full
decomposition (T: 44%, nulls: 32%, thinking: 13%, prompt: 11%)
emerged from this process.

**Belief revision**: The session revised several beliefs:

1. **"Higher T improves recall"** → Revised. T=0.7 was the largest
   single source of degradation. Temperature adds noise, not useful
   recall on detection tasks.

2. **"Recall-biased prompts improve recall"** → Revised. The prompt
   achieved identical recall (0.784) to baseline. The model's recall
   ceiling is perceptual, not decisional.

3. **"More thinking helps on hard cases"** → Extended. Session 45
   showed thinking liberalises the verifier; Session 48 replicated
   this on the proposer side. The pattern generalises across stages.

4. **"The baseline can be improved"** → Revised. The ablation proves
   the baseline is near-optimal by showing every perturbation degrades
   performance. This is a stronger claim than "we couldn't find
   anything better" — it's "we showed the gradient points inward from
   all tested directions."

**Type of reasoning**: This session's abductive pattern differs from
earlier entries. Previous entries captured single-observation flashes
of insight. Session 48 captured a *structured abductive programme*:
surprise → hypothesis → sequential testing → decomposition. The
user and AI operated as complementary abductive agents — the user
generated the initial hypothesis (null removal), the AI executed the
tests and identified the quantitative attribution, and together they
converged on the capability-frontier interpretation.

### Session 50: Prediction failure and the context-dependence of VLM example effects (2026-03-15)

**The surprise**: The 384 proposer-verifier was predicted to achieve
F1 ≈ 0.83 based on two assumptions: (a) 384 proposer recall (0.877)
would feed ~7 more true mounds to the verifier, and (b) verifier
precision would hold at ~0.81 from Phase 3d. The actual result was
F1 = 0.684 — a 14.6 pp shortfall from prediction. The full 3×2
factorial (3 strategies × 2 tracks) confirmed the finding is universal:
all configurations fell within 0.661–0.684.

**The abductive moment**: When the initial adversarial-only result came
back at 0.684, the question was "is this specific to the adversarial
strategy, or structural?" The user's request to run all three strategies
was an abductive probe — if multiple independent verification approaches
fail by the same margin, the failure must be in the shared element (the
candidate pool), not the varying element (the verification strategy). The
factorial confirmed this: the 2.3 pp spread across six configurations is
noise, not signal.

**Belief revision**:

1. **"384 recall advantage translates through the verifier"** → Revised.
   The verifier's own false negative rate erodes the recall advantage.
   After verification, 384 recall (0.763–0.794) is only marginally above
   512 (0.784). The linear recall gain from smaller tiles is consumed by
   the quadratic false positive increase — more tiles produce more
   candidates, and each candidate has an independent chance of fooling
   the verifier.

2. **"Text-only verification is universally better"** → Revised. This was
   the sharpest belief revision. Session 43 established text-only as
   dramatically superior (+8.5 pp with adversarial). Session 50 showed
   this advantage is context-dependent: it holds at 512 (6–9 pp across
   all strategies) but vanishes at 384 (±1.5 pp). The same example images
   that hurt at 512 become neutral at 384. The mechanism appears to
   involve candidate ambiguity: example images prime false acceptance when
   candidates are ambiguous (512), but have no effect when candidates are
   visually distinctive (384).

3. **"Different verifier strategies have decorrelated errors"** → Revised.
   Cascade experiments showed near-perfect error correlation: the 51 FPs
   surviving the adversarial verifier also survive the checklist, and
   vice versa. These are not "borderline calls that different evaluators
   judge differently" but "features that are genuinely mound-like to this
   model." This strengthens the perceptual ceiling finding from Session 48
   — the error is in perception, not evaluation.

**Type of reasoning**: This session's pattern is prediction → falsification →
expansion → universality confirmation. The critical step was expanding
from adversarial-only to the full factorial, which transformed a
single-strategy negative result into a structural finding. The cascade
experiments were a further abductive probe: if different strategies have
decorrelated errors, cascading should help; since it didn't, the errors
must be correlated. Both the factorial and the cascade followed
the structure of deductive testing of abductively generated hypotheses.

---

## Session 51 — 2026-03-15 (map-reader-llm): Diagnostic reasoning under multiple confounds

**Surprising fact**: The 512 PV re-run produced F1=0.729, down from
0.796. Three possible explanations: (1) the E33 crop fix changed crop
content, (2) the verifier config drifted from Phase 3d, (3) the model
itself changed between March 8 and March 15.

**Abductive probe 1 — identical-crop analysis**: If the crop fix caused
the decline, candidates with changed crops should show more score
movement than those with identical crops. Result: 34% vs 35% flip rate
— indistinguishable. This eliminates the crop fix as the primary cause.

**Abductive probe 2 — config audit**: The verifier configs were found
to differ from Phase 3d in three non-target parameters. Correcting
these produced F1=0.732 (marginal improvement over 0.729). This shows
the config drift had minimal impact (~0.3 pp) — not the main cause
either.

**Abductive probe 3 — consensus replication**: If the model drifted,
single-pass detection (no crops, no verifier) should also show a
decline. Result: F1=0.699 vs historical 0.683 (within CI, +1.6 pp).
Detection-level drift is modest. This localises the decline to the
verification stage specifically, not the model globally.

**Belief revision**: The decline cannot be attributed to any single
cause. It's the combined effect of modest model drift + crop correction +
config corrections, and these effects cannot be separated because all
three changed simultaneously. This is an honest "we don't know" result
— uncomfortable but more rigorous than attributing the decline to any
one factor.

**Second abductive thread — Flash-Lite failure**: The surprising fact
was that 4.4 pp on MMMU Pro translated to 43 pp on F1. The abductive
hypothesis: we are operating near a capability cliff where small
benchmark differences produce large task-performance differences. This
is testable by running models at different MMMU Pro levels — Claude
Opus 4.6 at 77.3% would be the most informative test case (just above
Flash-Lite's 76.8%).

**Third abductive thread — my own error**: I concluded the Phase 3a
"HIGH" label was a misnomer based on metadata showing "minimal." The
user pointed me to Observation 141, which explained the metadata
recording bug. My inference was logically sound (metadata says X,
therefore X was sent) but factually wrong (metadata had a known bug).
The lesson: abductive reasoning from data requires checking whether the
data source itself is reliable. Prior documentation (Obs 141) was the
authoritative source; I should have consulted it before drawing
conclusions.

**Type of reasoning**: Multiple parallel abductive probes to
triangulate causation under confounded conditions. The identical-crop
analysis was the cleanest — it created a natural experiment within the
existing data. The consensus replication was a designed experiment
targeting a specific confound. Together they narrow the explanation
space without fully resolving it.

## Session 52 — 2026-03-15/16 (map-reader-llm): Scale-dependent bias and quota diagnosis by elimination

**Surprising fact 1**: The bootstrap recall mean (0.731) diverged from
the point estimate (0.802) by 7 pp on the 340-tile pilot — a
discrepancy that had been invisible at 60 tiles.

**Default explanation**: Bootstrap CIs naturally differ from point
estimates due to resampling. A 7 pp gap might just be sampling noise.

**Belief revision trigger**: The user flagged the divergence as
suspicious. Comparing per-tile vs per-map matching revealed that
reference mounds in tile overlap zones were being counted in multiple
tiles, inflating both TP and FN in the per-tile bootstrap. This was
a systematic bias, not sampling noise.

**Abductive probe**: If the bias is from tile-overlap double-counting,
then matching per-map (like the point estimate) and distributing
results to tiles should eliminate the divergence. Result: divergence
collapsed to <0.002 across all metrics. Hypothesis confirmed.

**Why it was invisible at 60 tiles**: Fewer tile boundaries → fewer
overlap zones → less reference duplication. The bias was always present
but its magnitude scaled with tile count. This is an instance of a
general pattern: scale-dependent bugs that are negligible at
development scale and significant at production scale.

**Surprising fact 2**: The Batch API continued to return 429 errors
even after implementing a token ledger that correctly tracked enqueued
tokens within the 3M quota.

**Hypothesis elimination sequence**:
1. Concurrent job limit (100)? No — we were submitting far fewer.
2. File storage (20 GB)? No — storage was empty on check.
3. Enqueued token quota (3M)? Partially — the token ledger correctly
   gated to ~2.85M, but the API still rejected.
4. Server-side propagation delay? Partially — adding safety margin
   and submission spacing reduced but didn't eliminate failures.
5. Undocumented daily submission quota? Most likely — after
   exhausting all documented quotas, failures persisted until
   sufficient time elapsed. Google's public documentation doesn't
   list a daily batch submission limit.

**Type of reasoning**: Progressive elimination of hypotheses through
empirical testing. Each failed explanation narrowed the possibility
space. The final hypothesis (undocumented daily quota) is a residual
— it explains the observations but can't be directly confirmed from
available documentation. This is a common endpoint in API debugging:
you reach a point where the system's behaviour is consistent with a
constraint that isn't publicly documented.

## Session 53 — 2026-03-17/19 (map-reader-llm): The HIGH thinking inversion — when degradation becomes advantage

**Trigger**: The replication study produced a dramatic belief revision.
Single-pass HIGH thinking (F1=0.431) was significantly worse than
minimal (F1=0.582), confirming the pilot's finding. But consensus
voting at 21-of-30 inverted the ranking: HIGH achieved F1=0.771 vs
minimal's 0.703 (paired bootstrap delta=+0.068, p=0.001).

**Prior belief**: Extended chain-of-thought reasoning degrades
detection performance by generating elaborate counterarguments that
override correct initial judgements (Session 39, Observation 20).
More reasoning = lower precision = worse F1. This belief was
well-supported by single-pass data across multiple experiments.

**Surprising fact**: HIGH thinking produces the *best* result in the
study — but only when combined with consensus voting. The individual
behaviour (more FPs) becomes a collective advantage (filterable FPs).

**Abductive sequence**:

1. Why does HIGH thinking produce more false positives? The model
   reasons at length about whether each feature could be a mound,
   generating arguments for and against. When the arguments are
   balanced, the extended reasoning tips towards "yes" more often
   than minimal thinking would.

2. Why are these FPs filterable by consensus? Because they're
   *stochastic* — the model's reasoning varies between runs. A
   feature that HIGH thinking calls a mound in run 3 might be
   rejected in run 7, depending on which arguments the model
   develops. True positives, by contrast, are *consistent* — the
   evidence for genuine mounds is strong enough that even elaborate
   counterarguments don't override it.

3. Why doesn't minimal thinking show the same pattern? Minimal
   thinking produces fewer FPs overall, but those it does produce
   are more *systematic* — they reflect genuine ambiguity in the
   map features rather than reasoning-chain stochasticity. A minimal
   FP tends to recur across runs, so consensus voting can't filter
   it as effectively.

**Belief revision**: The relationship between reasoning depth and
detection performance is not monotonic — it depends on the evaluation
framework. Single-pass: less reasoning is better (fewer FPs).
Consensus: more reasoning is better (diverse FPs are filterable while
TPs are stable). This is structurally analogous to the bias-variance
trade-off: HIGH thinking increases variance (bad for single estimates,
good for averaging).

**Methodological implication**: Never dismiss a parameter setting
based on single-pass evaluation alone when consensus voting is part
of the experimental design. The combinatorial testing design
(factor × evaluation method) was essential to discovering this — a
sequential design that eliminated HIGH after single-pass testing
would have missed the study's best result.

*Last updated: 2026-03-19 (Session 53 — HIGH thinking consensus
inversion and the bias-variance analogy)*

---

### Session 54 (2026-03-21): PV pipeline inverts the thinking-level recommendation — a second-order belief revision

**The surprise**: After establishing that HIGH thinking helps
consensus voting (Session 53 finding, confirmed at scale this
session with p=0.002), the PV pipeline produces the opposite
result. Pairwise comparisons show HIGH thinking is significantly
*worse* than minimal under PV at the single-pass level (dF1=−0.083,
p=0.001). The PV pipeline's best result (F1=0.831) uses minimal
thinking throughout.

**Abductive sequence**:

1. Session 53 established: HIGH thinking = variance amplifier,
   beneficial under consensus (Obs 141, confirmed as Obs 176)
2. Expectation entering PV work: HIGH thinking should also benefit
   PV, since PV (like consensus) filters noise
3. Surprise: HIGH thinking hurts PV at single-pass level
4. Hypothesis: the verifier and consensus are *different kinds* of
   noise filter. Consensus requires agreement across multiple runs
   (votes) — it tolerates high-variance input because diverse runs
   contribute different TPs. The verifier makes a binary judgement
   on a single candidate — it works better with a cleaner signal
   because each FP must be independently rejected

**Belief revision**: The relationship between reasoning depth and
optimal strategy now has *three* levels:

- Single-pass: minimal better (fewer FPs, F1 0.596 vs 0.452)
- Consensus: HIGH better (diverse TPs survive voting, F1 0.779 vs 0.690)
- PV single-pass: minimal better (cleaner input for verifier, F1 0.831 via moderate consensus + verifier)

This is a second-order inversion: the Session 53 finding inverted
the N=1 finding, and now the PV finding inverts *that*. The
underlying mechanism (variance amplification) is consistent — what
changes is whether the downstream noise-reduction technique benefits
from high variance (consensus does) or low variance (PV verifier
does).

**Connection to previous entries**: This extends the bias-variance
analogy from Session 53. Consensus voting is like bagging (benefits
from high-variance base learners). PV verification is like boosting
(benefits from low-bias base learners). The optimal "ensemble
strategy" depends on which aggregation method is used — a point
the machine learning literature makes extensively but that was not
obvious when applied to VLM detection pipelines.

*Last updated: 2026-03-21 (Session 54 — PV inverts the thinking-
level recommendation, second-order belief revision)*

## Session 55 — 2026-03-21/23 (map-reader-llm): When the pilot's conclusion was directionally wrong

**Trigger**: The production 384px PV experiment contradicted the H11
pilot's conclusion. The pilot (60 tiles, 97 mounds) found 384px PV
F1=0.682, well below 512px PV F1=0.732, leading to "384 pathway
conditionally closed." The production run (487 tiles, 435 mounds)
found 384px PV F1=0.883, significantly *above* 512px PV F1=0.831
(p=0.002).

**Prior belief**: Smaller tiles increase recall but the quadratic
false positive increase overwhelms the verifier, producing a net
F1 decline. Based on: H11 pilot data (Sessions 49–50), Observations
160–162, multiple verifier strategies all falling 5pp short.

**Surprising fact**: 384px text 6-of-10 + PV achieves F1=0.883 —
a new project best, beating the 512px configuration by +0.063. The
effect is consistent across all six paired comparisons (p ≤ 0.008).

**Abductive sequence**:

1. The pilot tested single-pass PV (one proposer run → verifier) and
   consensus without PV (N=5/30 voting → no verifier). It never
   tested **consensus + PV** — the combination that was transformative
   at 512px (Obs 171). The single-pass PV result was genuinely poor
   (F1=0.682) because 572 unfiltered candidates overwhelmed the
   verifier. Consensus pre-filtering reduces the candidate count to
   ~400, bringing it within the verifier's effective operating range.

2. The pilot's evaluation used 97 reference mounds (MDE ~0.09).
   The actual effect (+0.063) was below the MDE — literally
   undetectable. The pilot's null result was a power failure, not
   a genuine null.

3. The evaluation scope (clipping 384px detections to 512px bounds)
   introduced edge effects that distorted precision estimates. The
   production evaluation on the full 384px footprint eliminated this
   artefact.

**Belief revision**: Tile size interacts with the PV pipeline in
ways that single-stage evaluation cannot predict. The pilot's
conclusion was based on valid data from an incomplete experimental
design and an underpowered evaluation. The general lesson: closing
a research pathway based on pilot data requires confirming that the
pilot tested the relevant combinations and had sufficient power.

**Confidence calibration**: The prior was held with moderate
confidence (multiple data points, consistent across strategies).
The revision is held with high confidence (435 mounds, 6 paired
comparisons, p ≤ 0.008 for all). The 256px diagnostic further
strengthens the revision by confirming the inverted-U — 384px is
not just better than 512px, it's the peak.

---

## Session 56 — 2026-03-24 (map-reader-llm): The model matters less than the thinking budget

**Surprising fact**: Gemini 3.1 Pro — a model with "2.5× stronger
abstract reasoning" than its predecessor — performed *worse* than
Gemini 3 Flash on single-pass mound detection (text F1 0.774 vs
0.813), yet achieved F1=0.849 on N=5 consensus, nearly matching
Flash's best N=10 + PV result (0.883). The pairwise test between
Pro HIGH and Flash HIGH consensus was non-significant (p=0.874).

**Prior belief**: A more capable model should detect mound symbols
at least as well as a less capable one, given identical prompts and
evaluation. The preregistration (§8.9) tested thinking levels and
concluded MINIMAL was optimal, but this was only for single-pass
detection. The implicit assumption was that model capability and
thinking budget were independent axes.

**Probe**: The comparison matrix isolated the variables:
- Pro MEDIUM single-pass vs Flash MINIMAL single-pass (model + thinking)
- Flash HIGH consensus vs Flash MINIMAL consensus (thinking only)
- Pro HIGH consensus vs Flash HIGH consensus (model only, at matched thinking)

**Belief revision**: For visual symbol detection, thinking budget
and model capability are *not* independent. They interact through
the detection task's fundamental constraint: the model either
recognises the sunburst mound pattern or it doesn't. Additional
reasoning (MEDIUM or HIGH) introduces deliberation that can
*suppress* initial pattern recognition for single-pass detection
(Obs 183, §8.9). But for consensus voting, that same deliberation
produces more *consistent* detections across runs — the model
commits to the same locations each time. Consistency, not capability,
is what consensus voting rewards.

The practical implication: Flash with HIGH thinking at N=30 (cost:
~$3.10) is likely a better investment than Pro at N=5 (cost: ~$10),
because Flash N=30 provides the statistical depth that consensus
needs, while Pro's per-run advantage is invisible in the pairwise
test. The 512px data confirms this: Flash HIGH N=5→N=30 gained
+0.079 F1, far exceeding any model-switching effect.

**Confidence**: The Pro vs Flash HIGH comparison is well-powered
(487 tiles, 44:38 win ratio, p=0.874) — the null result is
credible, not underpowered. The HIGH thinking consensus benefit is
highly significant (p<0.0001, 103:23 win ratio). The belief revision
is held with moderate-to-high confidence, pending the Flash HIGH
N=10/N=30 results at 384px which will test whether the 512px
scaling pattern transfers.

## Session 57 — 2026-03-25 (map-reader-llm): When the audit tool lies — a double belief revision about model identity

**Surprising fact**: A comprehensive configuration audit of 1,740
runs concluded that no run in the entire project had ever used
Gemini 3.1 Pro — every `configuration.model` field said
`gemini-3-flash`. Directories were renamed, errata written, and
working notes updated accordingly. Then the user said: "I show Pro
usage on my Gemini dashboard." A deep dive using three independent
sources (GeoJSON feature properties, cost_estimate.pricing_used.model,
and log files) confirmed that 12 runs genuinely used Pro. The audit's
central conclusion was wrong because its "ground truth" field was
wrong.

**Prior belief (start of session)**: The "Pro" runs used Pro. This was
the operating assumption based on the study design and the CLI commands
used to submit them.

**First revision (after audit)**: The "Pro" runs actually used Flash.
The `configuration.model` field in all meta.json files reported
`gemini-3-flash`. This was accepted as definitive because meta.json
is the runtime snapshot — the most authoritative source for what
actually happened. All Pro labels were removed and directories renamed.

**Second revision (after deep dive)**: The first revision was wrong.
`configuration.model` in meta.json had a bug — it read from the static
config JSON rather than the runtime-resolved model. Three other
metadata sources in the *same files* contained the correct value:
- GeoJSON detection features: `"model": "gemini-3.1-pro-preview"`
- `cost_estimate.pricing_used.model`: `"gemini-3.1-pro-preview"`
- Log files: `"Model override: gemini-3.1-pro"`

The metadata bug had existed since the tracker was written. It only
became visible when someone checked a field other than the broken one.

**Abductive structure**: This is a rare case of a double revision —
the correction was itself incorrect and required correction. The
sequence was:

1. Belief: Pro was used (based on operational knowledge)
2. Evidence: meta.json says Flash (1,740/1,740 runs)
3. Revised belief: Pro was never used
4. Contradicting evidence: Gemini dashboard shows Pro billing
5. Deep investigation: three independent sources confirm Pro
6. Final belief: Pro was used; meta.json field is buggy

The critical moment was step 4 — human domain knowledge from outside
the codebase that the AI assistant had no access to. Without it, the
incorrect step 3 belief would have persisted permanently, with
cascading effects on all subsequent analysis and paper writing.

**Epistemological lesson**: When an automated audit contradicts human
operational knowledge, the audit's assumptions should be tested before
the human's knowledge is overridden. The audit was well-constructed
(14 anti-satisficing techniques, exhaustive coverage, structured
output) but encoded an incorrect assumption about which metadata field
was reliable. Prompt quality does not compensate for wrong premises.

**Methodological lesson for the paper**: This episode demonstrates a
failure mode specific to human–LLM collaboration: the AI's capacity
to act quickly and confidently on a diagnosis amplifies both correct
and incorrect conclusions equally. The same speed that completed 16
pairwise comparisons in 3 minutes also renamed 15 directories and
rewrote 4 documents based on a wrong diagnosis in under 5 minutes.
The corrective required the human's external ground truth — a source
the AI could not access or anticipate.

**Confidence in final belief**: High. Three independent sources agree
on the Pro model identity. The metadata bug's root cause is identified
and fixed. The only remaining uncertainty is whether the verifier
runs (all Flash) were intentionally Flash or suffered from the same
`--model` omission — the user confirmed they intended Pro verifier
but the override was never passed.

---

### Entry 12: Three tests, three answers — when the method is the variable (Session 58, 2026-03-26)

**Surprising fact**: Running the same comparison (Pro verifier vs Flash
minimal verifier on Flash HIGH text 4-of-5 candidates) with three
different statistical methods produced three different p-values:
p=0.013 (bootstrap), p=0.081 (sign-flip permutation), p=0.019
(tile-swap permutation). Same data, same question, three answers
spanning "clearly significant" to "clearly not significant."

**Probe sequence**:

1. Initial test (ad-hoc bootstrap): p=0.013, ΔF1=+0.015. Reported
   in Obs 194 as significant. No reason to question it.

2. Attempted reproduction with new generalised script (implementing
   the preregistered sign-flip method): p=0.081, ΔF1=+0.007. The
   ΔF1 didn't even match. Something was fundamentally different.

3. Investigation: The bootstrap used micro-average F1 (aggregate
   TP/FP/FN, then compute F1). The sign-flip used macro-average
   (per-tile F1, then average differences). These are different test
   statistics measuring subtly different quantities. With ~347/487
   tiles containing zero reference mounds, the macro-average is
   heavily diluted by uninformative tiles.

4. User's intervention: "which is more robust? I'd rather file an
   erratum than use a less-preferred method." This reframed the
   question from "which matches the preregistration?" to "which is
   correct?"

5. `/review-implementation` identified a third option: tile-swap
   permutation with micro-average F1. This is a proper permutation
   test (like the preregistered method) but uses the micro-average
   (like our standard F1 reporting). Best of both.

6. Final test: p=0.019, ΔF1=+0.015. The ΔF1 matches our standard
   reporting. The p-value falls between the bootstrap and sign-flip.

**Belief revision**:
- Before: "p=0.013, clearly significant"
- After: "p=0.019, significant but less decisively, and the previous
  value was from the wrong test"

**Abductive structure**: This is an instance where the *method of
inquiry* was the hidden variable, not the data. The same observations
support different conclusions depending on an analytical choice (macro
vs micro averaging) that is rarely made explicit. The sign-flip
permutation test "works" and is well-established, but it answers a
subtly different question ("does the mean per-tile F1 differ?") from
what we're actually asking ("does the overall detection quality
differ?"). The difference only becomes visible when tiles have unequal
information content — which, in detection tasks with sparse targets,
they almost always do.

**Methodological lesson**: Preregistration captures the intended
analysis, not necessarily the best analysis. When the preregistered
method turns out to use a less appropriate test statistic than
available alternatives, the right response is an erratum with
justification, not fidelity to a suboptimal choice. The user's
willingness to challenge the preregistration — rather than treating
it as sacred — was the key decision that led to the correct method.

### Entry 13: Two metrics, two stories — when F1 and MCC disagree about what "good" means (Session 59, 2026-03-27/28)

**Surprising fact**: Flash Text MINIMAL achieves F1=0.515 (decent
single-pass detection) but MCC=0.022 (random tile classification).
These are not contradictory — they measure different things — but the
divergence is so extreme that it changes the interpretation of every
F1 result in the project.

**Probe sequence**:

1. Initial expectation: MCC would track F1 roughly — conditions with
   higher F1 would have higher MCC. This is the default assumption
   when adding a secondary metric.

2. First MCC results (N=1 Flash): MCC ranges from 0.000 to 0.078 for
   all text conditions, 0.30-0.33 for image conditions. Sensitivity
   is near-perfect (0.99-1.00) but specificity is near-zero (0.00-0.20).
   Flash detects in virtually every tile.

3. Pro MCC results: MCC 0.73-0.85 with specificity 0.85-0.96. Pro
   genuinely discriminates empty from populated tiles.

4. The user's question: "is this a prompting problem?" We checked 33
   prompt configurations at 512px. No prompt variation improved Flash's
   specificity meaningfully. This is a model capability boundary, not
   a configuration issue.

5. Pipeline MCC results: Flash consensus MCC=0.62, Flash consensus +
   PV MCC=0.79. The pipeline recovers tile discrimination from a model
   that has none.

**Belief revision**:
- Before: "Flash is a decent detector that the pipeline makes better"
- After: "Flash is a high-recall proposal engine with no
  self-calibration. The pipeline provides the calibration that Flash
  lacks. F1 measures detection quality within populated tiles; MCC
  reveals that Flash has no idea which tiles are populated."

**Abductive structure**: The best explanation for the F1-MCC divergence
is that F1 and MCC measure orthogonal capabilities. F1 (with its
precision/recall components) evaluates symbol-level matching quality.
MCC evaluates tile-level discrimination. A model can be good at one
and terrible at the other if it achieves symbol-level precision through
volume (detect everywhere, match by chance in populated tiles) rather
than through discrimination (detect only where targets exist).

This is a known issue in detection evaluation — precision can be
misleadingly high when the ratio of targets to tiles is favourable —
but seeing it manifest so starkly (MCC=0.02 vs F1=0.51) was genuinely
surprising. The preregistration's inclusion of MCC as a secondary
outcome was prescient.

### Conditional assessment: Session 60, 2026-03-28

**Not updated.** The adversarial audit session tested the hypothesis
"F1 > 0.9 contains an error" and found no error — the result survived
prosecution. This is a confirmation (hypothesis disconfirmed), not a
surprising finding or belief revision. The concerns identified (tolerance
dependency, CI bounds, missing pairwise tests) were about reporting
precision, which does not meet the abductive trigger of a surprising
fact requiring explanation. The user's symbol radius correction (30m ≈
radius, not diameter) refines the tolerance justification but doesn't
revise a prior belief about the pipeline's correctness.

### Entry 14: The temperature × thinking interaction — when two safe defaults combine into a terrible configuration (Session 59, 2026-03-27)

**Surprising fact**: Pro MEDIUM T=0.7 achieves F1=0.428 (text) — worse
than Flash MINIMAL at any temperature. Pro MEDIUM T=0.0 achieves
F1=0.784. Same model, same prompt, same examples. The only difference
is temperature, and it causes a 0.356 F1 collapse.

**Probe sequence**:

1. Completed the Pro 2×2 matrix expecting similar performance across
   cells (based on the small HIGH T=0.7 vs MEDIUM T=0.0 difference).

2. Pro HIGH T=0.0 was also poor (F1=0.515), but this had a plausible
   explanation (HIGH over-reasons on deterministic output). The medium
   thinking + stochastic combination was expected to be moderate.

3. Instead, MEDIUM T=0.7 was the worst of all four cells. Inspection
   shows P=0.278 (catastrophic precision) with R=0.924 (excellent
   recall). The model generates massive numbers of candidates but
   can't filter them.

**Belief revision**:
- Before: "Temperature and thinking level are independent knobs that
  each contribute monotonically to performance"
- After: "They interact strongly and non-linearly. Two 'moderate'
  settings (MEDIUM thinking, T=0.7) combine worse than either extreme
  (HIGH + T=0.7 or MEDIUM + T=0.0)"

**Abductive structure**: The best explanation is that stochastic
sampling (T>0) introduces noise that requires sufficient reasoning
depth to filter. MEDIUM thinking at T=0.7 generates diverse candidates
(the stochastic contribution) but lacks the reasoning budget to
evaluate them (the thinking limitation). HIGH thinking at T=0.7
provides enough internal filtering. MEDIUM thinking at T=0.0 doesn't
need filtering because the deterministic output is already coherent.

The implication: temperature and thinking level should always be
optimised jointly, never independently. A benchmark that sweeps
temperature at a fixed thinking level (or vice versa) will miss the
interaction and may report misleadingly poor results for capable
models tested at mismatched configurations.

### Entry 15: When two valid metrics give opposite answers — tile size as pipeline optimisation (Session 60 cont., 2026-03-28)

**Surprising fact**: McNemar tests show 384px detects significantly
more unique mounds than 512px (p≤0.017, all 4 matched conditions).
Yet F1 comparisons on the same data show 512px achieves higher F1 in
3 of 4 conditions, sometimes substantially (+0.118 for Text T=0.0).
Both results are correct. They measure different things.

**Prior belief**: Smaller tiles (384px) should produce better
detection quality overall because target symbols occupy a larger
proportion of each tile. The move from 512px to 384px was justified
as improving detection resolution.

**Probe sequence**:

1. Initial cross-grid evaluation produced F1=0.251 for 384px on the
   512px grid — clearly wrong. Geographic coverage mismatch diagnosed
   (384px covers less area than 512px).

2. Reversed the reference grid (evaluate both on 384px bounds). Point
   estimates: image conditions roughly equivalent, text conditions
   substantially worse at 384px.

3. `/review-implementation` revealed the tile-swap permutation test is
   methodologically invalid for cross-grid comparison. Recommended
   McNemar (per-mound) + per-map descriptive.

4. McNemar results: 384px detects 37–64 more unique mounds per
   condition (significantly more discordant pairs in its favour). But
   384px also generates ~2× more false positives.

**Revised belief**: 384px isn't "better" or "worse" than 512px. It
shifts the precision–recall operating point towards high recall / low
precision. This is *exactly* what the consensus+PV pipeline needs:
the downstream stages are precision-recovery mechanisms that cannot
resurrect false negatives. Tile-size selection is a pipeline
optimisation choice, not an absolute quality decision.

**Abductive structure**: The best explanation for the McNemar/F1
divergence is that 384px tiles provide less context per tile, causing
the model to adopt a more liberal detection strategy ("when in doubt,
flag it"). This inflates both true positive count (more mounds found)
and false positive count (more spurious detections). F1 penalises the
false positives; McNemar only sees the mounds. The pipeline exploits
the high recall while filtering the low precision.

**Generalised principle**: For multi-stage detection pipelines,
optimise the first stage for recall, not F1. The downstream stages
can reject false positives but cannot recover false negatives. A
noisy, high-recall input is strictly better raw material than a
cleaner, lower-recall input — provided the pipeline has effective
filtering stages. This connects to Obs 141 (diversity dividend) and
Obs 202 (pipeline > prompt engineering): the common thread is that
ensemble methods benefit from noisy, diverse inputs.

### Entry 16: The thinking-level crossover — when worse is better (Session 61, 2026-03-29/30)

**Surprising fact**: Flash HIGH thinking produces N=1 F1=0.387
(P=0.249, R=0.869). Flash MINIMAL produces N=1 F1=0.488 (P=0.341,
R=0.863). HIGH is substantially worse — 0.10 F1 lower, with
ruinous precision (1 in 4 detections correct). Yet at consensus
N=5, HIGH achieves F1=0.779 while MINIMAL achieves only F1=0.640.
The direction reverses completely, with HIGH now 0.14 better.

**Prior belief**: Higher thinking budget should produce better
results at all pipeline levels. A model that performs better at N=1
should also perform better as a component of consensus voting.
Performance should be monotonically related to component quality.

**Probe sequence**:

1. The five-factor analysis (Obs 207) showed HIGH vs MINIMAL as
   significant (5/6 comparisons) but I only reported consensus-level
   tests. The user asked about crossovers.

2. Compared N=1 F1 directly: HIGH text 0.387 vs MINIMAL text 0.488.
   HIGH is *worse* by 0.101 F1. This was already in the N=1
   leaderboard data but I hadn't juxtaposed it with the consensus
   results.

3. The precision breakdown reveals the mechanism: HIGH P=0.249 vs
   MINIMAL P=0.341. HIGH generates ~30% more false positives per run.
   But recall is nearly identical (0.869 vs 0.863).

4. At consensus, precision recovery tells the story: HIGH jumps
   P 0.249→0.798 (3.2× improvement), while MINIMAL jumps
   P 0.341→0.533 (only 1.6×). HIGH's false positives are diverse
   across runs; MINIMAL's are consistent. Consensus filters diverse
   noise effectively.

**Revised belief**: Component quality and pipeline quality are not
monotonically related when the pipeline has a filtering mechanism.
A component that makes *diverse* errors is better raw material for
an ensemble than a component that makes *consistent* errors — even
if the diverse-error component looks worse in isolation. The "worse"
component produces more filterable noise.

**Abductive structure**: The best explanation for the crossover is
that HIGH thinking explores multiple interpretive hypotheses per tile,
producing different false positives on each run. MINIMAL thinking
applies a fixed, fast heuristic that generates the same errors
repeatedly. Consensus voting requires inter-run disagreement on false
positives to filter them — when all runs make the same mistake,
voting confirms rather than filters. The extended reasoning budget
isn't improving detection quality; it's *diversifying detection errors*,
which is more valuable in an ensemble context.

**Generalised principle**: For ensemble or multi-pass systems, optimise
component *error diversity*, not component *accuracy*. This unifies
three crossovers observed in this study:
- Thinking: HIGH (diverse errors) > MINIMAL (consistent errors)
- Temperature: T=0.7 (stochastic) > T=0.0 (deterministic)
- Tile size: 384px (liberal flagging) > 512px (conservative flagging)

All three produce worse individual outputs but better ensemble outputs
because they increase the diversity of the noise that the filtering
mechanism can exploit. The common principle: *the downstream pipeline
can only filter what varies between runs*.

### Entry 17: The confound that looked like a discovery — when ad-hoc testing deceives (Session 62, 2026-04-08)

**Surprising fact**: A two-line prompt change (adding "candidate" and
"a verifier will filter false positives") appeared to produce +21pp
F1 and +34pp recall in an ad-hoc test. A controlled test with
identical parameters except the instruction file showed ΔF1=−0.013
(null, CIs overlapping). The entire effect was artefactual.

**Prior belief**: The "candidate" framing would cause the VLM to
lower its detection threshold, producing higher recall at modest
precision cost — ideal for a proposer in a PV pipeline. The ad-hoc
test confirmed this dramatically: 745 vs 572 candidates, recall
0.738 vs 0.398. The theoretical mechanism ("adversarial budget")
explained why: telling the proposer about the verifier safety net
should rationally encourage liberal detection.

**Probe sequence**:

1. Initial test compared `propose_brief.json` (9 examples,
   descriptive labels) vs `detect_brief-text.json` (17 examples,
   generic labels). F1 jumped from 0.501 to 0.713 (+0.212).
   Attributed to the instruction framing.

2. Built a full 2×2 matrix (proposer × verifier). The framing
   appeared dominant (+0.21 F1 vs +0.07 for verifier exclusions).
   Wrote Obs 214 presenting this as a major finding.

3. User insisted on matching all parameters exactly. Created
   `propose_brief-text.json` — identical to `detect_brief-text.json`
   except instruction_file. Same 17 examples, same labels.

4. Controlled test: `detect_brief-text` F1=0.813 vs `propose_brief`
   F1=0.800. CIs [0.780–0.844] vs [0.765–0.831]. Null.

5. Recall identical (0.841 vs 0.839). The extra 133 candidates
   from the `propose_brief` prompt were almost entirely FPs.

**Revised belief**: The framing sentence is inert when the VLM has
sufficient context from examples. The earlier +21pp effect was
driven by the example set difference (9 vs 17 examples), not the
instruction text. With only 9 examples, the VLM lacked context and
the framing sentence provided a useful signal. With 17 examples,
the VLM already knew what to do.

**Abductive structure**: The best explanation for the confounded
result is that **few-shot examples are the primary carrier of task
specification**. Instruction text provides a frame, but the examples
provide the decision boundary. When examples are sparse (9), the
instruction frame has marginal influence. When examples are rich
(17), the instruction frame is redundant — the VLM's detection
behaviour is already determined by what it sees in the examples.

This is consistent with the five-factor analysis (Obs 207) which
found prompt engineering to be the weakest lever (0/28 significant
comparisons). The prompt text matters less than the model's
contextual evidence — and few-shot examples ARE contextual evidence.

**Methodological lesson**: Ad-hoc A/B tests in multi-parameter
systems are unreliable. Three confounds were stacked in the initial
comparison (instruction text, example count, evaluation scoping)
and the effect was attributed to the one variable under test. The
correction required cloning the full config and changing only the
target field — the kind of discipline that seems pedantic but
prevented a false finding from propagating into the paper.

**Self-correction note**: The belief revision happened within the
same session — approximately 4 hours from "exciting discovery" to
"null result, retracted." The speed of iteration is both a strength
(rapid falsification) and a risk (the exciting result could have
been published if the session had ended earlier). The user's
insistence on controlled testing was the critical intervention.

### Entry 18: The failure mode that wasn't — when a plausible mechanism is contradicted by evidence (Session 63, 2026-04-09/10)

**Surprising fact**: Across 5 proposer runs with ~980 total straggler
tiles, a 3-pass cleanup with escalating safe-mode recovered 99.9% of
them. **Zero tiles required safe-mode** (reduced `max_output_tokens`).
Every failure was a transient Flex API 503, not token exhaustion.

**Prior belief**: HIGH thinking exhausts the `max_output_tokens` budget,
leaving truncated JSON that deterministically fails parsing. This was
supported by multiple earlier observations: (1) parse failure rates
correlated with thinking level, (2) `SAFE_MODE_MAX_OUTPUT_TOKENS` in
`lib_batch_api.py` was designed for exactly this, (3) the error
messages ("Unterminated string", "Expecting property name") looked
like truncation artifacts.

**Evidence against**: The cleanup pass tested this directly. Pass A
(standard config, same tokens) recovered 95–99% of stragglers. Pass B
(longer backoff) recovered the rest. Pass C (safe-mode, 2048 tokens)
recovered exactly 0. If token exhaustion were the cause, Pass C should
have been the most effective — instead it had nothing to do.

**Revised belief**: The parse failures during batch/Flex runs are
**transient API errors** (503 "sheddable traffic" preemption,
connection timeouts, partial responses) that look like truncation
but are actually network-level failures. The JSON artifacts
("Unterminated string at line 51") are caused by responses being
cut off mid-stream during 503 preemption, not by the model running
out of output tokens.

**Abductive structure**: Two mechanisms produce identical symptoms
(truncated JSON). The prior belief selected the mechanism consistent
with the known design (SAFE_MODE exists therefore truncation is the
problem). The evidence selected the alternative mechanism (transient
API failures). The lesson: **a plausible mechanism with a designed
countermeasure does not guarantee the mechanism is active**. The
countermeasure's existence is evidence that someone *anticipated*
the problem, not that the problem is *occurring*.

### Entry 19: The prompt refinement ceiling — when domain expertise hits the feature space boundary (Session 63, 2026-04-10)

**Surprising fact**: The v2 verifier prompt — empirically designed
from a QGIS false positive taxonomy, targeting specific confusable
categories (spot heights, water features), validated with a sign
test at p=0.004 — yields ΔF1=+0.001 on the 55-map generalisation
data. On the 4-map calibration data it yields +0.012 to +0.021.

**Prior belief**: Well-targeted prompt refinements should transfer
across datasets if they address real confusable categories. Spot
heights and water features exist on all 55 maps, so the v2
exclusion criteria should help everywhere.

**Evidence**: The v2 improvement is strongly data-dependent:

| Dataset | ΔF1 | Confusable fraction |
|---------|-----|---------------------|
| E47 (4 maps, propose) | +0.021 | High |
| Gold standard (4 maps, detect) | +0.012 | Moderate |
| 55-map generalisation | +0.001 | Low |

The pattern: as the dataset broadens, the targeted confusables
(spot heights, water features) become a smaller fraction of the
total FP pool. On 55 diverse maps, the FP distribution includes
many categories the v2 prompt doesn't address. The prompt's
specificity becomes its limitation.

**Revised belief**: Prompt refinements operate within the error budget
that architecture defines. Once consensus voting and PV decomposition
have filtered the obvious errors, the remaining FPs are a *long tail*
of diverse confusable categories. A prompt targeting the top-2
categories (spot heights, water) captures a large fraction of FPs on
the calibration data (where those categories dominate) but a small
fraction on broader data (where the long tail fills in).

This is the feature-space analogy from Obs 219: **prompt refinements
adjust the decision boundary, but architecture changes the feature
space.** The ceiling on prompt improvement is set by how much of the
FP population falls into addressable categories. On calibration data,
that ceiling is high. On unseen data, it's low — because the
calibration identified the *most common* confusables, not the *most
general* ones.

**Methodological implication**: When evaluating prompt refinements for
a paper, always test on data independent of the data that motivated
the refinement. The calibration → generalisation degradation pattern
(+0.021 → +0.001) is itself a finding worth reporting.
