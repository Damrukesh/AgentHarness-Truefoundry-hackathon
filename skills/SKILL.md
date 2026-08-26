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

## Turning an answer into a GitHub issue

If the user wants this turned into a GitHub issue (e.g. "file this as a bug" or
"can you raise an issue for this"), draft the issue title and body using the
retrieved KB content as grounding, then use the GitHub MCP tool to create it.
**Always show the drafted issue and wait for explicit user approval before
creating it** — never create the issue directly without confirmation, since this
is an irreversible action visible to others.