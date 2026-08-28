# DevFlow KB Agent — Approval-Gated Support, Issue Filing & PR Review

Built for the [TrueForge Agent Harness Hackathon](https://www.wemakedevs.org/hackathons/trueforge) on [TrueForge](https://github.com/truefoundry/trueforge).

**Demo video:** _[link coming soon]_

## The problem

Support and platform teams answer the same handful of questions over and over
(*"why do my retries duplicate notifications?"*), and the answers live scattered
across docs, Slack threads, and tribal knowledge. When something's clearly wrong —
a bug worth filing, or a PR that violates a documented convention — someone still
has to notice, write it up, and act on it. This agent does the noticing and the
drafting, but never acts without a human saying yes first.

## What it does

One agent, one knowledge base, three capabilities:

1. **Answers questions** from an internal knowledge base (semantic search, not
   keyword matching), instead of guessing or hallucinating.
2. **Files GitHub issues** grounded in that knowledge base — checks for existing
   duplicates first, drafts the issue, and **waits for explicit approval** before
   creating it.
3. **Reviews pull requests** against the same knowledge base — flags changes that
   violate documented behavior (e.g. a new step missing a required safety flag),
   drafts a review comment, and **waits for explicit approval** before posting it.

Every action that touches the outside world (creating an issue, posting a PR
comment) stops for human approval first. Nothing gets written to GitHub without
someone explicitly saying yes.

## Why the approval gate matters

The agent is genuinely capable of being wrong — early in development it once
fabricated a plausible-sounding but entirely incorrect explanation of the
knowledge base's contents when a tool call failed silently, instead of admitting
it didn't have the information. The approval gate isn't a formality here: it's
the actual backstop for that failure mode. You see the draft. You catch a
wrong or overconfident answer before it becomes a real GitHub issue or a real PR
comment. See the demo video for a real example.

## Architecture

```
 User question
      │
      ▼
 TrueForge Agent (kb-approval-assistant)
      │
      ├── Skill: kb-retrieval
      │     └── Sandbox: fetches retrieve.py + kb_embeddings.json from this
      │         repo, runs local semantic search (fastembed, ONNX-based,
      │         no API key needed) against the DevFlow knowledge base
      │
      ├── MCP: GitHub
      │     ├── search/list issues (duplicate check)
      │     ├── create issue (with `from-kb-agent` label)
      │     ├── read PR diff
      │     └── post PR review comment
      │
      └── Approval gate
            └── Every GitHub write action pauses here first
```

## Tech stack

- **[TrueForge](https://github.com/truefoundry/trueforge)** — the agent harness:
  model + sandbox + MCP + skills + approval gate
- **Model** — OpenRouter (bring-your-own-key)
- **Retrieval** — [fastembed](https://github.com/qdrant/fastembed) (`BAAI/bge-small-en-v1.5`),
  ONNX-based local embeddings, no external API or secret required
- **MCP** — GitHub connector, for reading/writing issues and PR comments
- **Knowledge base** — a synthetic 10-entry FAQ for a fictional CI/CD tool
  ("DevFlow"), covering retries, timeouts, secrets, caching, and more

## Repo structure

```
skills/
├── SKILL.md              # instructions the agent follows for all 3 capabilities
├── kb.csv                 # the knowledge base source content
├── generate_embeddings.py # one-time script: builds kb_embeddings.json
├── kb_embeddings.json     # precomputed embeddings (committed, so the skill
│                           # doesn't need to regenerate them at runtime)
├── retrieve.py             # semantic search over the KB, called from the sandbox
└── requirements.txt        # fastembed, numpy — installed automatically by the skill
```

## Setup — how to run this yourself

1. **Run TrueForge locally**
   ```
   npx @truefoundry/trueforge
   ```

2. **Connect a model** in TrueForge's Initial Setup — any OpenAI-compatible
   provider works (OpenRouter, Anthropic, OpenAI, or a local Ollama endpoint).
   Use a model with solid tool-calling ability; small/free-tier models can be
   unreliable at multi-step tool use (see Design Decisions below).

3. **Connect the GitHub MCP server** with a personal access token scoped to a
   test repo you're comfortable with the agent writing to. You'll need:
   - `Issues: Read and write`
   - `Pull requests: Read and write`

4. **Import this skill**: in TrueForge's Skills tab → *Import from GitHub* →
   repository URL = this repo, folder = `skills`.

5. **Create an agent**, attach the GitHub connector and the imported skill, and
   give it instructions along these lines:
   > You are a support assistant for DevFlow, a CI/CD platform. Use the
   > kb-retrieval skill for any DevFlow question, issue filing, or PR review
   > request. Always create issues/comments in `<your-owner>/<your-test-repo>`.
   > Always show your draft and wait for explicit approval before creating or
   > posting anything.

6. **Try it**:
   - `why do my retries duplicate notifications in DevFlow?`
   - `file this as a GitHub issue in <owner>/<repo>`
   - `review PR #<number> on <owner>/<repo>`

No API key is needed for retrieval itself — the skill installs its own
lightweight dependencies and downloads a small (~130MB) local embedding model
the first time it runs in the sandbox.

## Design decisions & trade-offs

A few real engineering calls made along the way, kept here because the *why*
is more interesting than the *what*:

- **Semantic search, not keyword matching.** An earlier version used TF-IDF
  (scikit-learn) for retrieval, since it needs no model download at all. It
  works, but it's genuinely keyword-based: a query like *"why do my retries
  duplicate notifications"* ranked a tangentially-related "Notification
  Channels" entry above the actually-correct "Retry Behavior" entry, because
  the literal word "notifications" appears more often there. Semantic
  embeddings fixed this — but needed a lightweight-enough way to run them.

- **fastembed over sentence-transformers.** The natural first choice
  (`sentence-transformers`) pulls in PyTorch as a dependency — commonly
  1-2GB+ — which exceeded the sandbox's disk quota mid-run. `fastembed` uses
  ONNX Runtime instead: same model families, real semantic embeddings, ~55MB
  installed. This is what made local, secret-free semantic search actually
  fit.

- **No external embedding API.** A HuggingFace Inference API version was also
  tried and worked, but required an `HF_TOKEN` — and TrueForge's sandbox is
  intentionally isolated from the host machine's environment variables, with
  no built-in secrets manager for custom scripts. Rather than commit a live
  token to this public repo or re-type it into every chat session, retrieval
  was kept fully local instead.

- **Free-tier model routing is a real reliability risk.** Testing initially
  used OpenRouter's `openrouter/free` auto-router, which silently picks a
  different underlying free model per request. This produced inconsistent
  tool-calling behavior — including one run where the model tried to
  hand-write Python code to call MCP tools directly instead of using its
  normal tool-calling interface. Pinning to one fixed, known model resolved
  this. Lesson: for anything relying on multi-step tool use, model
  consistency matters more than which free tier is cheapest.

## Known limitations

- The knowledge base is a small synthetic dataset (10 entries) for demo
  purposes, not a production KB.
- Retrieval quality depends on the KB actually covering the topic; the agent
  is instructed to say so honestly when it doesn't, rather than guess.
- PR review currently checks changed config/pipeline-style content against the
  KB; it does not execute the PR's own code or test suite.

## License

MIT
