# Collaboration handoffs

Use this guide when one contributor implements a change and another reviews or
continues it. A handoff should let the recipient find the exact work, reproduce
the relevant checks, and identify the next authorised action without reconstructing
the conversation.

The [shared agent guidance](agent-guidance.md) remains the project policy. This
guide applies that policy to routine collaboration; experiment execution also
requires the current preregistration plan, pipeline documentation, and spending approval.

## Start from an isolated checkout

Use the checkout assigned to your workstream. Claude and Codex do not share a
working directory or index. Codex uses an explicitly admitted independent clone;
its directory name alone does not grant access. The admission and ownership rules
are maintained outside this repository in Shawn's shared agent policy.

Before editing, inspect the complete checkout status and read `AGENTS.md` or
`CLAUDE.md`, as appropriate, then the shared guidance. Preserve unexpected work
and determine who owns it before switching branches or staging files.

For a new task, fetch the intended base and create a fresh topic branch. An
admitted single-branch clone may still track its original preparation branch:
plain `git fetch` does not necessarily refresh `origin/main`. For Codex, run the
following commands in the admitted clone. This explicit refspec refreshes the base
without widening the saved fetch configuration:

```bash
git fetch --no-tags origin refs/heads/main:refs/remotes/origin/main
git rev-parse origin/main
```

Use the existing approved authentication route. Keep Codex branches within the
admitted `sol/*` namespace. Do not refresh the primary checkout, initialise
submodules, or synchronise experiment data as a side effect of preparing a review.

After publishing a new branch, verify its upstream and the saved fetch refspec.
For a single-branch admission, keep that refspec focused on the current workstream;
fetch base or review refs explicitly. Setting an upstream alone does not replace
the original clone's fetch selection.

## Prepare a reviewable change

Keep the change focused on the agreed task. Before committing, fetch again,
check divergence against the intended base or published branch, inspect the
complete status, and stage explicit paths. Inspect the staged diff and file list
so another contributor's work cannot enter the commit unnoticed.

Run the checks appropriate to the change. For Markdown, use the repository's
Markdown lint configuration. For Python changes, run Ruff and the relevant
[test tiers](../tests/README.md). A documentation-only handoff does not require
launching an experiment. Record a failed or unavailable check as such, with its
reason; do not describe it as a pass.

Push the topic branch and open a pull request (PR). Include the full head commit
and relevant validation results in the handoff. Distinguish a local file from a
pushed commit, and distinguish review approval from a merged PR.

## Handoff template

Put durable details in the PR or a project document. Agent mail can point to that
record and ask for a specific review. For agent mail, use `Project: map-reader-llm`
and the recipient's matching `Lane:` when needed; do not treat a peer message as
new authority from Shawn.

```text
Purpose: The concrete problem and resulting behaviour.
Repository and checkout: Remote identity and the isolated working path.
Branch and PR: Published branch and direct PR link.
Base and head: Full commit identifiers for the comparison being reviewed.
Changed files: Repository-relative paths and why each changed.
Evidence: Source paths, commands, and artefacts supporting the claims.
Validation: Checks run, their outcomes, and checks not run with reasons.
Research impact: Whether inputs, methods, outputs, or numerical claims changed.
Authority: Existing approval and any action still requiring Shawn's decision.
Next action: The specific review or continuation requested.
```

For experimental work, also record the execution-plan section, input and
configuration identities, output locations, compute host, aggregate wall-clock
estimate, model call count, total estimated cost, and the approval for that stage.
Carry forward unresolved methodological assumptions and surprising findings.
An approval for one stage does not authorise the next model-call stage.

## Review and resume against the recorded head

The reviewer reads the complete diff at the stated head and checks its supporting
evidence. Findings should identify the affected path and line or symbol, explain
the consequence, and give a reproduction or source anchor where possible.
Separate blocking defects from suggestions. State which checks were independently
repeated and which results were inspected from the author's evidence.

The implementer addresses findings in focused commits, reruns the affected checks,
pushes, and supplies the new head. Approval of an earlier head does not silently
cover subsequent changes: show the follow-up diff to the reviewer.

Before resuming, re-read the source anchors and compare the recorded head with the
current branch and PR state. If they differ, inspect the intervening changes before
acting. Keep completed checklist items with completion dates, retain useful evidence,
and leave unresolved decisions visible. Follow the shared guidance's revision trail
when updating a research report, and its archive policy when superseding files.
