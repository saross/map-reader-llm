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