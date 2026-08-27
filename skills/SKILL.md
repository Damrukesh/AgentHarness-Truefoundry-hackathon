---
name: kb-retrieval

description: Use this skill whenever the user asks a question about DevFlow (the CI/CD platform) that might be answered by the internal knowledge base — e.g. questions about retries, timeouts, secrets, caching, webhooks, promotions, notifications, matrix builds, or rollback behavior. Also use it before drafting a GitHub issue about a DevFlow bug or question, so the issue is grounded in the actual documented behavior instead of a guess.
---

# KB Retrieval Skill

This skill lets you answer questions using DevFlow's internal knowledge base instead
of guessing. There is no separate "fetch_from_kb" or "kb-retrieval" tool to call by
name — do not attempt to call a tool with either of those names, it does not exist.
Instead, use your sandbox / code execution tool to run shell commands, exactly like
you would for any other task. Everything runs fully locally — no API key or secret
is required for this skill.

## When to use this

Use this skill any time the user's question is about how DevFlow behaves — retries,
timeouts, secrets, caching, webhooks, environment promotion, notifications, matrix
builds, or rollback behavior. Do NOT answer DevFlow questions from general knowledge
or by guessing — always retrieve first, even if you think you already know the answer.

## How to use it

**Step 1 — one-time setup, run these sandbox commands in order:**

```
curl -sO https://raw.githubusercontent.com/Damrukesh/AgentHarness-Truefoundry-hackathon/main/skills/retrieve.py
curl -sO https://raw.githubusercontent.com/Damrukesh/AgentHarness-Truefoundry-hackathon/main/skills/kb_embeddings.json
curl -sO https://raw.githubusercontent.com/Damrukesh/AgentHarness-Truefoundry-hackathon/main/skills/requirements.txt
pip install -r requirements.txt --break-system-packages -q
```

Only do this once per conversation — if these files already exist in your sandbox
working directory from an earlier step, skip straight to Step 2. The first run will
download a small (~130MB) local embedding model; this can take up to a minute.

**Step 2 — run the retrieval, replacing `<question>` with the user's actual question:**

```
python3 retrieve.py "<question>" --top_k 3
```

This returns the top 3 most relevant KB entries as JSON, each with a `title`,
`content`, and a `score` (higher = more relevant, roughly 0 to 1).

## Interpreting results

Use the retrieved `content` to ground your answer. If the top result's score is
very low (below ~0.3), the KB likely doesn't cover this — say so honestly instead
of forcing an answer from a weak match or from general knowledge. If any command in
Step 1 or Step 2 fails, tell the user plainly that retrieval failed and why —
never fabricate DevFlow behavior that wasn't actually retrieved.

## Checking for duplicate issues first

Before drafting a new issue, use the GitHub MCP tool to search/list existing open
issues in the target repo for similar titles or content (e.g. search for key terms
from the user's question, like "retry" or "notification"). If an existing issue
looks like it already covers the same problem, tell the user about it and share
its link/number instead of creating a new one — do not create a duplicate. Only
proceed to drafting a new issue if no clear duplicate exists.

## Turning an answer into a GitHub issue
When creating the issue, add the label `from-kb-agent` (create the label first via
the GitHub MCP tool if it doesn't already exist in the repo) so agent-created issues
are visually distinguishable from human-filed ones.
If the user wants this turned into a GitHub issue (e.g. "file this as a bug" or
"can you raise an issue for this"), draft the issue title and body using the
retrieved KB content as grounding, then use the GitHub MCP tool to create it.
**Always show the drafted issue and wait for explicit user approval before
creating it** — never create the issue directly without confirmation, since this
is an irreversible action visible to others.

The user may ask for both the answer AND the issue in a single message (e.g. "why do my retries duplicate notifications — can you file this as an issue in owner/repo?"). When this happens, do both steps in the same turn: retrieve from the KB first, use that content to draft the issue, then pause and show the draft for approval before creating it. Do not ask the user to repeat their question in a second message — a single combined request should still get retrieval, drafting, and the approval pause, all before anything is created.

## Reviewing a pull request against the KB

When the user asks you to review a pull request (e.g. "review PR #7 on
owner/repo"), do the following:

1. Use the GitHub MCP tool to fetch that PR's diff/changed files.

2. For each meaningfully changed piece of code (e.g. a new pipeline step, a
   config change), identify what topic it relates to — retries, notifications,
   secrets, caching, webhooks, promotions, matrix builds, or rollback behavior.

3. For each such topic found in the diff, run the retrieval script (same as
   above: `python3 retrieve.py "<topic-related question>" --top_k 3`) to check
   what the KB says the correct/documented behavior is.

4. Compare the PR's actual code against what the KB says. If the PR is missing
   something the KB says is required (e.g. a notification or side-effecting step
   without the `idempotent: true` flag), that's a finding worth flagging.

5. Draft a PR review comment describing what you found, citing the specific KB
   entry that supports it (e.g. "per the Retry Behavior KB entry, this step
   should have `idempotent: true` since retries will re-run it"). If nothing
   notable is found, draft a comment saying the change looks consistent with
   documented behavior.

6. **Always show the drafted review comment and wait for explicit user approval
   before posting it** — never post directly to the PR without confirmation,
   since this is visible to others and cannot be silently undone.