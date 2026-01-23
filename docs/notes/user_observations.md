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