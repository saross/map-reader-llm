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