---
name: kb-retrieval

description: Use this skill whenever the user asks a question about DevFlow (the CI/CD platform) that might be answered by the internal knowledge base — e.g. questions about retries, timeouts, secrets, caching, webhooks, promotions, notifications, matrix builds, or rollback behavior. Also use it before drafting a GitHub issue about a DevFlow bug or question, so the issue is grounded in the actual documented behavior instead of a guess.
---

# KB Retrieval Skill

This skill lets you answer questions using DevFlow's internal knowledge base instead
of guessing. There is no separate "fetch_from_kb" tool — use your existing
sandbox / code execution capability to run the script below, exactly like you would
for any other Python script.

The retrieval script and precomputed embeddings sit in this same skill folder,
alongside this SKILL.md file: `retrieve.py`, `kb_embeddings.json`, and `requirements.txt`.

## When to use this

Use this skill any time the user's question is about how DevFlow behaves — retries,
timeouts, secrets, caching, webhooks, environment promotion, notifications, matrix
builds, or rollback behavior. If you're not sure whether a question is DevFlow-related,
try the retrieval first; it's cheap and returns nothing useful if there's no match.

Do NOT answer DevFlow questions from general knowledge or by guessing. Always run
the retrieval script first, even if you think you already know the answer.

## How to use it

1. The sandbox is a fresh environment each session and does NOT have the required
   Python libraries pre-installed. Before running retrieve.py for the first time,
   install dependencies using your sandbox/code execution tool:

   ```
   pip install -r requirements.txt --break-system-packages -q
   ```

   If retrieve.py fails with an import error (e.g. "No module named
   sentence_transformers"), run this install command and then retry — don't give
   up or fall back to guessing after one failed attempt.

2. Using your sandbox/code execution tool, run this command, replacing `<question>`
   with the user's actual question (keep the quotes):

   ```
   python3 retrieve.py "<question>" --top_k 3
   ```

   Run it from the same directory this SKILL.md file is in, since `retrieve.py`
   loads `kb_embeddings.json` from its own working directory.

3. This returns the top 3 most relevant KB entries as JSON, each with a `title`,
   `content`, and a `score` (higher = more relevant, roughly 0 to 1).

4. Use the retrieved `content` to ground your answer. If the top result's score is
   very low (below ~0.15), the KB likely doesn't cover this — say so honestly instead
   of forcing an answer from a weak match or from general knowledge.

5. If the user wants this turned into a GitHub issue (e.g. "file this as a bug" or
   "can you raise an issue for this"), draft the issue title and body using the
   retrieved KB content as grounding, then use the GitHub MCP tool to create it.
   **Always show the drafted issue and wait for explicit user approval before
   creating it** — never create the issue directly without confirmation, since this
   is an irreversible action visible to others.

## Files in this skill

- `retrieve.py` — the retrieval script (do not modify)
- `kb_embeddings.json` — precomputed embeddings for the KB (do not modify)
- `kb.csv` — the source KB content, for reference
- `requirements.txt` — Python dependencies needed to run retrieve.py