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