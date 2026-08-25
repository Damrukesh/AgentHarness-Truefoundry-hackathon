---
name: kb-retrieval
description: Use this skill whenever the user asks a question about DevFlow (the CI/CD platform) that might be answered by the internal knowledge base — e.g. questions about retries, timeouts, secrets, caching, webhooks, promotions, notifications, matrix builds, or rollback behavior. Also use it before drafting a GitHub issue about a DevFlow bug or question, so the issue is grounded in the actual documented behavior instead of a guess.
---

# KB Retrieval Skill

This skill lets you answer questions using DevFlow's internal knowledge base instead
of guessing. The knowledge base and a search script are available in the sandbox at
`kb-project/`.

## When to use this

Use this skill any time the user's question is about how DevFlow behaves — retries,
timeouts, secrets, caching, webhooks, environment promotion, notifications, matrix
builds, or rollback behavior. If you're not sure whether a question is DevFlow-related,
try the retrieval first; it's cheap and returns nothing useful if there's no match.

## How to use it

1. Run this in the sandbox, replacing `<question>` with the user's actual question:

   ```
   python3 kb-project/retrieve.py "<question>" --top_k 3
   ```

2. This returns the top 3 most relevant KB entries as JSON, each with a `title`,
   `content`, and a `score` (higher = more relevant, roughly 0 to 1).

3. Use the retrieved `content` to ground your answer. If the top result's score is
   very low (below ~0.15), the KB likely doesn't cover this — say so honestly instead
   of forcing an answer from a weak match.

4. If the user wants this turned into a GitHub issue (e.g. "file this as a bug" or
   "can you raise an issue for this"), draft the issue title and body using the
   retrieved KB content as grounding, then use the GitHub MCP tool to create it.
   **Always show the drafted issue and wait for explicit user approval before
   creating it** — never create the issue directly without confirmation, since this
   is an irreversible action visible to others.

## Files in this skill

- `kb-project/retrieve.py` — the retrieval script (do not modify)
- `kb-project/kb_embeddings.json` — precomputed embeddings for the KB (do not modify)
- `kb-project/sample_kb.csv` — the source KB content, for reference