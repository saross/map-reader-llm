# Enable browser automation / DOM inspection for Claude Code

**Created**: 2026-04-19
**Purpose**: Install Playwright MCP so a future Claude Code session
can inspect the live Streamlit app and diagnose GitHub issue #7
(keyboard-shortcut second-stage failure in
`scripts/review_gt_duplicates.py`).

## Recommended: Playwright MCP (Microsoft's official)

Best fit for this use case. Excels at DOM inspection, element-
state tracking, and step-by-step interaction — exactly what's
needed to diagnose focus loss after the first keystroke. Chrome
DevTools MCP is excellent for performance profiling but overkill
for the debugging task.

## Install (project-scoped, ~5 min)

### 1. Verify prerequisites

```bash
node --version  # Needs Node.js 18+
```

### 2. Edit `/home/shawn/Code/map-reader-llm/.claude/settings.json`

Add an `mcpServers` entry:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"],
      "timeout": 30,
      "type": "stdio"
    }
  }
}
```

If `settings.json` already has other keys (permissions, env, etc.),
merge the `mcpServers` object — don't replace the whole file.

### 3. Pre-install Chromium (optional, recommended)

Avoids a ~400 MB download on first tool use:

```bash
npx @playwright/mcp@latest install chromium
```

### 4. Restart Claude Code

The MCP server list is read at startup. Quit and relaunch.

### 5. Verify installation

In a fresh Claude Code session, ask:

> "Navigate to http://localhost:8501, take a screenshot, and
> report the title of the page."

(Have the Streamlit app running first — see below.)

If Claude executes browser automation commands and returns a
screenshot or title, it's working.

## Why project-scoped

Keeps Playwright isolated to `map-reader-llm`. No browser
automation bleeding into unrelated projects. If you later want it
globally, move the `mcpServers` entry to `~/.claude/settings.json`.

## Known gotchas

- **First run downloads ~400 MB** unless pre-installed (step 3).
- **Headed mode**: Playwright runs headless by default but can
  still inspect DOM and take screenshots without a display.
- **Streamlit iframes**: the review app wraps components in
  iframes. When asking Claude to query elements, tell it
  explicitly: *"use `page.frameLocator('iframe')` if direct
  element queries fail"*.
- **Port 8501**: Streamlit's default. If it clashes with another
  service, change `streamlit run --server.port NNNN`.

## Workflow for GH issue #7 (after install)

Issue: https://github.com/saross/map-reader-llm/issues/7
(keyboard-shortcut second-stage failure on subsequent clusters)

### 1. Launch Streamlit locally

```bash
cd /home/shawn/Code/map-reader-llm
.venv/bin/streamlit run scripts/review_gt_duplicates.py -- \
    --threshold-m 75
```

This gives you a page at `http://localhost:8501` with the review
UI live. Leave it running.

### 2. In a fresh Claude Code session, task Claude

Suggested prompt:

> Use Playwright to navigate to http://localhost:8501. Advance to
> the second cluster (by clicking either `k: Keep all` or
> `m: Merge` on the first, then either pressing the subtype or
> cancelling as appropriate). On the second cluster, press `m` to
> open the merge-subtype selector. IMMEDIATELY after the selector
> appears, inspect:
>
> 1. `document.activeElement` at the top level — report tag, id,
>    class, and the owner document (parent / iframe).
> 2. Enumerate all iframes on the page and report their src/id.
> 3. Check for shadow roots on the Streamlit body and any
>    component iframes (`element.shadowRoot` property).
> 4. Press `d` (the second-stage subtype key). Check `activeElement`
>    again. Report any changes.
> 5. Open the DevTools console. Report all `[gt-review]` log
>    entries chronologically.
>
> The bug: the `d` keystroke fails to trigger the subtype button
> on clusters after the first. I need to know where the keystroke
> is being trapped.

### 3. Expected output

Claude should produce a diagnostic report identifying the focused
element at the moment of the failing keystroke. The three likely
diagnoses are:

| Symptom | Root cause |
|---|---|
| `activeElement` is inside a shadow root | The multi-doc listener misses shadow-DOM boundaries |
| `activeElement` is in an iframe not in `docs` list | The iframe enumeration is incomplete |
| `activeElement` is on body but handler doesn't fire | Event preventDefault upstream blocks before the listener |

Once you know which, the fix in
`scripts/review_gt_duplicates.py:_inject_keyboard_shortcuts` is
targeted.

## Cascade to review_candidates.py

Commit `2120741b` ported the same keyboard-JS pattern to
`scripts/review_candidates.py`. If the root cause and fix apply
there too, the fix should be cascaded — note this in the
commit message when closing #7.

## References

- Playwright MCP: https://github.com/microsoft/playwright-mcp
- Playwright MCP docs: https://playwright.dev/docs/getting-started-mcp
- Claude Code MCP integration: https://code.claude.com/docs/en/mcp
- GitHub issue #7: https://github.com/saross/map-reader-llm/issues/7
