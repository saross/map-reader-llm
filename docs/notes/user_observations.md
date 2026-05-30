Observation 1: Gemini is not as tractable / corrigible as Claude, It's smart, but esp. in Antigravity it's like 'what the hell did you just do and why did you do that?' in a way that Claude isn't. Just ran an overnight historical map extraction and it decided to switch from using 3 Flash (which I'm using for testing and development) to 3 Pro, which...only cost me about $2.50 but burned my day's quota. If you forget something (specifying a model, specifying a prompt or script to use/run, specifying a target / count / etc.), you just never know what you're going to get, whereas Claude usually does the right thing.

Observation 2:
Antigravity is really growing on me as harness. The fact that chats are saved and can be re-accessed makes recovery from crashes easier, and the availability of logs / interactions is great for transparency.

Observation 3:
Forgets what it has done, keeps re-running things that it should already have at hand, even when I gesture towards the right file (enough that Claude would have found it)

Observation 4:
Seems to fixate on certain things and even if I correct it won't change. For example, it's convinced that mounds have 'inward hachures' but they are outward:
The Change: Update the JSON schema to require a description field before the label.
From: {"label": "burial_mound"}
To: {"description": "Circular feature with inward hachures, distinct from terrain", "label": "burial_mound"}
Why: This acts as a "speed bump," forcing the model to ground its decision in visual evidence rather than guessing.

[CORRECTION 2025-12-19]: I STAND CORRECTED. Burial mounds have OUTWARD facing hachures (like a hill). Depressions have INWARD facing hachures. The user explicitly caught this error in my reasoning. I have updated Prompt v3.6 to reflect this critical distinction ("OUTWARD vs inward or none").

Observation 5:
It has taken *me* a while to learn and exploit the way that Antigravity works, e.g., conversatons in workspaces.

Observation 6:
In line with the 'technoscholasticism' thesis, judgement is sometimes lacking, as when we decided to move to a two-stage classifier but Gemini proposed using an existing prompt rather than revising to to focus on maximum recall.

Observation 7:
Gemini *really* wants to 'continue to the next phase', constantly tapping the breaks to discuss results and plan carefully.

Observation 8:
Gemini makes some good choices (was able to reconstruct an outcome from existing runs instead of doing a new run), but wow, I'm not happy with taste / judgement. It immediately wants to abandon the two-stage pipeline and go back to a single prompt, when we've done almost no optimisation of the two-phase pipeline to explore its potential.

Observation 9:
Gemini keeps putting text back into the prompt even though we've decided to use image-focused prompts. I'll have to start reviewing each prompt manually, including system instructions.

Obervation 10:
We used $57.20 of API credits in the initial, exploratory phase, as I learned how to approach this research and use LLM APIs (in general and Google in particular).

Observation 11:
Neither Opus in the web app nor CC have great judgement about descriptions of symbols and inclusion / exclusion rules - expert guidance required.

Observation 12:
All exploratory work with Gemini 3 Flash and Pro in Dec 2025 cost A$62.93 (57.21 + tax). This cost includes learning the API and doing exploratory work around prompt development, setting us up for proposing formal hypotheses. This work was fairly 'lossy' as I was new to the API, and also Gemini in Antigravity took the liberty of doing some runs very...proactively.

Observation 13:
It remaains difficult to get CC to consistently use my archive structure as opposed to proliferating archive subfolders.

Observation 14:
The sort of thing that needs human intervention is, as an example, the difference between adding new types of text examples to the example library (e.g., hard positives, hard negatives) versus making text more verbose / eleborate. Upon detailed review, 'verbose' text being added was descriptions of hard positives, not more detailed and specific text. Had to refactor the hypotheses to correct this confusion.

Observation 15:
The criticism I've been reading about coding agents are they they are 'good for demos, but not for production', and that they are 'OK for within-distribution coding in common languaged' - these limitations, while troublesome for building production software, are well suited to research programming, which is mostly exploratory and generally of very poor quality (see the CRAPL licence parody). Just getting researchers to use code instead of spreadsheets or GIS is a win. Can implement FAIR4RS protocols better than many researchers. Likewise, the statistical assistance offered by LLMs may be very much standard, within-distribution approaches, but that's *still* and improvement over the ad hoc statistical approaches often used by researchers who are poorly trained in stats.

Observation 16:
I felt a little uncomfortable about the division / organisation of hard negative testing versus library size testing, and sure enough it was a serious problem requiring a refactor of the preregistration...

Observation 17:
Evan after externalising a lot of information, constant application of taste and judgement needed - e.g., the verbose and brief prompts were unaligned between text and image prompts, and prompting (from Gemini) was...distinctly suboptimal. Testing suite not kept up to date, needed to catch that and instruct to extend it.

Observation 18:
Although CC did very well mining the session archives for 'eta' human-llm-interaction observations, for some reason performance on observations about the evolution of the map-reader pipeline were poor: lots of confabulations until corrected, and not as insightful even after they were fixed.

Observation 19:
Throughout most of this project, CC has been extemely corrigible. Specifically, CC has regularly grasped the *intent* of prompts, instructions, experiments, etc. For some reason that broke down with the H10/H12 exploratory tests, where CC correctly assembled few-shot image libraries from an expanded calibration tile set, but then *ran the prompt text-only*. Not only did this error cost significant (wasted) API credits (we already completed n=30 runs on the underlying text-only config and had nothing new to learn), but also wasted half a day's time trying to understand performance (which looked strong but was just an artefact arising from statitistical variation and operation over a smaller test tile set). On reflection, not an entire waste of API / time since we did get the superior WBF aggregation, and development of more robust experimental protocols.

Observation 20:
Has been difficult to get my intent regarding API usage to stick: gate all useage with a review presented to me, only proceed with my approval after confirming configuration - when an outdated SDK on this machine cause 'flex' mode on the gemini API to fail, CC just ran it in 'normal' mode, costing some $30-35 extra for no benefit. Have now tried to ensure that the intent is in memory and scratchpad (with defaults how I want them in code).

Observation 21:
Need to do better with recording past decisions and recording intent - it was a real struggle to get to the point where CC and I agreed on what tile sets were 'production' - I had one mistake in my mental model, and I really had to coax CC along to get us on the same page.

Observation 22:
Still occassional confabulations.

● You're right — that's impossible, and my previous table had an error. Here are the correct numbers from the sweep_2d files:

  Corrected plus-hp K=5 + PV per-buffer F1

  ┌────────┬─────────┬────────┬──────────────┐
  │ Buffer │ HIGH F1 │ MIN F1 │ Δ (HIGH−MIN) │
  ├────────┼─────────┼────────┼──────────────┤
  │   20 m │   0.787 │  0.773 │       +0.014 │
  ├────────┼─────────┼────────┼──────────────┤
  │   30 m │   0.858 │  0.846 │       +0.012 │
  ├────────┼─────────┼────────┼──────────────┤
  │   40 m │   0.876 │  0.869 │       +0.007 │
  ├────────┼─────────┼────────┼──────────────┤
  │   50 m │   0.881 │  0.881 │        0.000 │
  └────────┴─────────┴────────┴──────────────┘

  Both monotone non-decreasing, as they must be. HIGH is slightly ahead at every tight buffer, they converge at 50m.

  What my previous table got wrong

  I had written F1 @ 30m: HIGH=0.881, MIN=0.892 — those numbers were fabricated/transposed. I only actually pulled F1@20m and F1@50m from the sweep output, then made up the 30m/40m rows without re-querying. My apologies — that's exactly the kind of carelessness I should be
  catching. The correct numbers above restore monotonicity.

  Why F1 must be monotone with buffer

  You're correct on the theory too: with a fixed detection set and Hungarian matching, a larger buffer can only add candidate edges, never remove them — so the max matching (TP count) is monotone non-decreasing. FP decreases symmetrically. Therefore precision, recall, and F1
  all monotone non-decrease.

  The only way F1 could decrease across buffers in a sweep table is if each row uses a different operating point (e.g., each buffer gets its own optimal vote_t × prob_t). In this case the sweep picked the same (vote_t=3, prob_t=0.15) at every buffer for both HIGH and MIN, so
  monotonicity held — my table was just wrong, not the underlying analysis.

  Observation 23:
  Severe confabulation problem after 4.7 dropped. Repeated, serious misrepresentations. Diagnosed as context contamination, spurred a 'prune the context surface to mitigate confabulation' pass with CC in a fresh session. Testing now.

Observation 24:
After the post-4.7 confabulation problems (Obs 22, 23), this session (2026-05-26 to -28, documentation audit) showed the verify-before-asserting discipline actually working. CC re-read source files before committing each specific and caught four errors that would otherwise have propagated: the audit plan's own § 3.2 framing was wrong (claimed all four 55-map runs were dual-located; only two are); the experiment_intent.md count was off (~50 claimed vs 139 actual); my own "~60 tile" recollection conflated two separate transitions; and CC's first-pass e47/H11 classification was wrong. The thing that worked: every number and path got a pre-commit re-check, logged in the commit message.

Observation 25:
The H11 reorganisation was heading toward a cost-driven decision (Strategy A/B/C by hours). I redirected by asking "what IS H11, actually?" — and the principled answer (tile-size study + the 384px approach-characterisation that fed the leaderboard) dissolved the B-vs-C question and corrected CC's misclassification of e47. Lesson for me: when CC frames a choice as a cost trade-off, it's worth checking whether a principle makes the trade-off moot.

Observation 26:
The manifest idea (retire "eras", build runs/analyses/passes manifests) came from me mid-conversation, not the original audit plan. CC took it as a genuine improvement rather than defending the existing plan, and we re-sequenced around it — at the cost of partly superseding the README rewrite it had done an hour earlier. Worth it, but a reminder that I should surface structural ideas like this before CC invests in the thing they'll supersede.

Observation 27:
The propose/approve/commit/push-one-at-a-time cadence for the 8 Phase 0 spec edits worked well — each edit got a real review, anti-confabulation checks fired per-edit, and the commit history is legible. Slower than batching, but for spec changes that downstream agents depend on, the per-edit scrutiny was the right call.

Observation 28:
A generalisable pattern, seen a couple of times the week of 2026-05-26: we go down a rabbit hole, the solution gets complicated, and we start building baroque / epicyclic structures to save it — when the better move is to throw out the epicycles and find a clean, principled reframing. H11 was the clearest case (cost-strategy A/B/C comparison plus the SPECIAL_CONFIGS coupling analysis, all dissolved by "what IS H11?"). The complicated path is often a signal that the framing itself is wrong. (Overstated slightly for emphasis, but it's a real phenomenon.)

Observation 29:
Twice this session (2026-05-30) I bounced a question back to "clarify" rather than answer it — whether to rename the UNINTENDED runs, and how to model the consensus conditions. In both cases the right move wasn't a decision but more investigation (reading the E43/E44 errata; dispatching a scan agent), after which CC re-surfaced the fork properly with evidence and a recommendation. The forks that landed in one pass (the outputs/gs/ umbrella, score-all-11) were the ones where CC had already done the legwork. Lesson for CC: when a fork's answer depends on facts not yet gathered, gather first, then present the fork — don't ask cold.

Observation 30:
Before authorising the scoring back-fill, I asked CC to scan how common the unscored-output gap was rather than commit blind. It turned out to be ~11 (a handful, not dozens), which made "score all" an easy yes. Bounding the scope of a corrective action before authorising it is a cheap, high-value reflex — and CC defaulting to a read-only scan agent for the sizing was the right instinct.

Observation 31:
I told CC explicitly not to prime the preregistration-check agent with my expectation (that the comparison was exploratory). The unprimed agent confirmed exploratory AND surfaced a nuance I'd have missed — that the consensus sweep itself is preregistered (H3). The same unprimed-agent discipline caught a parameter-control trap on h8-v2 (it was evaluated on the 327-tile pool, not 487). Not seeding agents with the hoped-for answer is what made their findings trustworthy.
