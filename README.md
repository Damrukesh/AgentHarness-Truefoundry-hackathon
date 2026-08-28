# DevFlow KB Agent (Approval Gated Support, Issue Filing and PR Review)

Built for the [TrueForge Agent Harness Hackathon](https://www.wemakedevs.org/hackathons/trueforge) on [TrueForge](https://github.com/truefoundry/trueforge).

**Demo video:** _[link coming soon]_

## The problem

Support and platform teams answer the same handful of questions over and over
e.g.(*"why do my retries duplicate notifications?"*), and the answers live scattered
across docs maintained in the team's archives. Whenever a bug is worth filing, or a PR that violates a documented convention ,someone still has to notice, write it up, and act on it. This agent does the noticing and the drafting, but never acts without a human saying yes first.

## What it does

One agent, one knowledge base, three capabilities:

1. **Answers questions** from an internal knowledge base (semantic search, not
   keyword matching), instead of guessing or hallucinating.
2. **Files GitHub issues** Being grounded to the knowledge base ,it checks for existing
   duplicates first, drafts the issue, and **waits for explicit approval** before
   creating it.
3. **Reviews pull requests** against the same knowledge base ,it flags changes that
   violate documented behavior (e.g. a new step missing a required safety flag),
   drafts a review comment, and **waits for explicit approval** before posting it.

Every action that touches the outside world (creating an issue, posting a PR
comment) stops for human approval first. Nothing gets written to GitHub without
someone explicitly saying yes.

## Why the approval gate matters

The agent is genuinely capable of being wrong and must admit it didn't have the information instead of incorrect commits. The approval gate isn't a formality here. It's
the actual backstop for that failure mode. You see the draft. You catch a
wrong or overconfident answer before it becomes a real GitHub issue or a real PR
comment.

## Architecture

```
 User question
      │
      ▼
 TrueForge Agent
      │
      ├── Skill: kb retrieval ( created inside Trueforge )
      │     └── Sandbox: fetches retrieve.py + kb_embeddings.json from this
      │         repo, runs local semantic search (fastembed),against the
      │         DevFlow knowledge base
      │
      ├── MCP: GitHub
      │     ├── search/list issues (duplicate check)
      │     ├── create issue (with "from-kb-agent" label)
      │     ├── read exisiting pull requests PR 
      │     └── post PR review comment
      │
      └── Approval gate
            └── Every GitHub write action pauses here first
```

## Tech stack

- **[TrueForge](https://github.com/truefoundry/trueforge)** — the agent harness:
  model + sandbox + MCP + skills + approval gate
- **Model** — OpenRouter (Cluade-3-5-Haiku)
- **Retrieval** — (`BAAI/bge-small-en-v1.5`),
  ONNX based local embeddings, no external API key required
- **MCP** — GitHub connector, for reading/writing issues and PR comments
- **Knowledge base** — a synthetic 10 entry FAQ for a fictional CI/CD tool Devflow scenario

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

## Small guide to setup this project yourself

1. **Run TrueForge locally**
   ```
   npx @truefoundry/trueforge
   ```

2. **Connect a model** in TrueForge's Initial Setup . Any provider works (OpenRouter,      
   Anthropic, OpenAI, or a local Ollama endpoint). Use a model with solid tool calling ability.
3. **Connect the GitHub MCP server** with a personal access token scoped to a
   test repo you're comfortable with the agent writing to. You'll need:
   - `Issues: Read and write`
   - `Pull requests: Read and write`

4. **Import this skill**: in TrueForge's Skills tab → *Import from GitHub* →
   repository URL = this repo, folder = `skills`.

5. **Create an agent**, attach the GitHub connector and the imported skill, and
   give some prompt instructions on how do you want the agent to execute.

6. **Try some queries like**:
   - `why do my retries duplicate notifications in DevFlow?`
   - `file this as a GitHub issue in <owner>/<repo>`
   - `review PR #5 on <owner>/<repo>`


## Design decisions and trade-offs

A few real engineering challenges hit me along the way which I would love to share so you could watch out for them.

- **Semantic search, not keyword matching.** An earlier version used TF IDF
  (scikit-learn) for retrieval, since it needs no model download at all. It
  works, but it's genuinely keyword based. Choose models that check semantic relationships.

- **fastembed over sentence-transformers.** The natural first choice
  (`sentence-transformers`) pulls in PyTorch as a dependency , commonly
  1.5 GB+ which exceeded the sandbox's disk quota mid run. `fastembed` uses
  ONNX Runtime instead. Free local setup and 55MB

- **No external embedding API.** A HuggingFace Inference API version was also
  tried and worked, but required an `HF_TOKEN` but TrueForge's sandbox is
  intentionally isolated from the host machine's environment variables. Rather than commit a live token to this public repo or re type it into every chat session, retrieval
  was kept fully local instead.

- **Choose the right models.** small models can be unreliable at 
   multi step tool use. If using a free tier toggle off "dynamic subagents" in the trueforge agent setup.

## Known limitations

- The knowledge base is a small synthetic dataset (10 entries) for demo
  purposes, not a production KB.
- Retrieval quality depends on the KB actually covering the topic
- The agent is instructed to say so honestly when it doesn't, rather than guess.

## License

MIT
