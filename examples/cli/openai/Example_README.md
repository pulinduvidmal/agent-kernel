# AK + Local RAG Example

## Overview

This example runs Agent Kernel in REST mode, layers on a small local RAG service (searching `.txt` files), and extends the `/run` endpoint to accept an optional `context` object. The OpenAI runner now assembles a system preamble from each agent's instructions plus `session["context"]`, so we can pass context without repeating it in the user prompt.

## Capabilities

- List agents with `GET /agents`
- Run an agent via `POST /run` (supports `context`)
- Search indexed text files using `GET /rag/search?q=...`
- Combine RAG retrieval with an agent through `POST /rag/ask` (returns answer + sources)

## File Layout

```text
examples/cli/openai/
|-- local_agents.py       # Custom agents for the local news workflow (triage / analyst / summarizer / general)
|-- run_server_rag.py     # FastAPI app: AK REST + /rag/search + /rag/ask
|-- run_server.py         # Minimal AK REST only: /health, /agents, /run
|-- rag_service.py        # RAG loader: split, embed, index, and search .txt files
`-- local_data/           # Local text corpus
    |-- local_news_1.txt
    |-- local_news_2.txt
    |-- local_news_3.txt
    `-- local_news_4.txt
```

## Core Library Changes

| File | Update |
| --- | --- |
| `ak-py/src/agentkernel/api/agent.py` | Added the `context` field to `RunRequest` and passed it through to the service. |
| `ak-py/src/agentkernel/core/service.py` | `run(self, prompt, context=None)` now stores context on the session without injecting it into the prompt body. |
| `ak-py/src/agentkernel/core/prompting.py` | Added `build_preamble(agent_instructions, session)` to create the system-style preamble (instructions + context). |
| `ak-py/src/agentkernel/openai/openai.py` | `OpenAIRunner.run()` prepends the generated preamble before calling the model. |

]

## Installation

```ps1
# From repo root
cd ak-py
pip install -e .

# RAG + helpers
pip install faiss-cpu langchain langchain-community langchain-huggingface sentence-transformers requests
```

## Run the Server (REST + RAG)

```ps1
# From repo root
cd examples/cli/openai
$env:PYTHONPATH = (Get-Location).Path
$env:OPENAI_API_KEY = "sk-..."  # Supply your real key

python .\run_server_rag.py
```

Use `run_server.py` instead if you only need `/health`, `/agents`, and `/run` without the RAG endpoints.

## Sample Requests

1. **Health**
   ```ps1
   curl http://localhost:8000/health
   ```
   ```json
   {"status":"ok"}
   ```

2. **List Agents**
   ```ps1
   curl http://localhost:8000/agents
   ```
   ```json
   {"agents":["triage","analyst","summarizer","general"]}
   ```

3. **RAG Search**
   ```ps1
   curl "http://localhost:8000/rag/search?q=colombo"
   ```
   Returns the most relevant snippets and their source files from `local_data/`.

4. **/run With Context (triage hand-off)**
   ```ps1
   $body = @{
     agent   = "triage"
     prompt  = "Classify this issue for follow-up: community reactions to the Coastal Link bridge update."
     context = @{
       region  = "Western Province"
       topic   = "transport"
       urgency = "medium"
     }
   } | ConvertTo-Json -Depth 6

   Invoke-RestMethod -Method POST -Uri "http://localhost:8000/run" -ContentType "application/json" -Body $body
   ```
   ```text
   [analyst] This issue falls under the category of "Public Engagement & Feedback" related to regional transport infrastructure...
   ```

5. **RAG + Agent**
   ```ps1
   $body = @{
       question = "Top local headlines?"
       agent    = "general"
       top_k    = 5
       context  = @{ region = "LK"; city = "Colombo" }
   } | ConvertTo-Json

   Invoke-RestMethod -Method POST -Uri "http://localhost:8000/rag/ask" -ContentType "application/json" -Body $body
   ```
   Returns the answer, selected sources, and a `session_id`.

6. **OpenAPI**
   ```ps1
   curl http://localhost:8000/openapi.json
   ```
   `RunRequest` now documents the optional `context`, and the API title shows `AK + Local RAG`.

## REST Endpoints

- `GET /health` - Server alive check
- `GET /agents` - Loaded agents (triage, analyst, summarizer, general)
- `POST /run` - Run an agent (request body supports `context`)
- `GET /rag/search?q=...` - RAG search across local `.txt` files
- `POST /rag/ask` - RAG + agent answer; returns answer, session, and sources

Example `/run` payload:

```json
{
  "prompt": "...",
  "agent": "general",
  "session_id": null,
  "context": {
    "key": "value"
  }
}
```

## Notes

- Place `.txt` files in `examples/cli/openai/local_data/` and restart the server to rebuild embeddings.
- `local_agents.py` defines agents and handoffs tailored for local news triage, analysis, and summarization.

## Troubleshooting

- `ModuleNotFoundError: rag_service` - Ensure you are in `examples/cli/openai`, set `PYTHONPATH`, and confirm `rag_service.py` exists.
- `404` on `/rag/ask` - You are likely running `run_server.py` instead of `run_server_rag.py`.
- Slow first run - Embedding models download on first execution and cache under the default Hugging Face directories.

