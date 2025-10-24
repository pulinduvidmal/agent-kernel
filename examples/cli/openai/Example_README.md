# Overview

This example runs Agent Kernel in REST API mode, adds a small local RAG layer (searching over `.txt` files), and extends the `/run` endpoint to accept an optional context object.

## Capabilities

- List agents: `GET /agents`
- Run an agent: `POST /run` (optional `context`)
- Search local files: `GET /rag/search?q=...`
- Ask a question that combines RAG plus an agent: `POST /rag/ask` (returns answer and sources)

## File Layout

```
examples/cli/openai/
|-- local_agents.py       # Custom agents for the local-news flow (triage/analyst/summarizer/general)
|-- run_server_rag.py     # Starts FastAPI: AK REST + /rag/search + /rag/ask
|-- run_server.py         # Minimal AK REST only: /health, /agents, /run
|-- rag_service.py        # RAG: load, split, embed, index, and search .txt files
`-- local_data/           # Local text corpus
    |-- local_news_1.txt
    |-- local_news_2.txt
    |-- local_news_3.txt
    `-- local_news_4.txt
```

## Core Library Changes

- `ak-py/src/agentkernel/api/agent.py` adds `context` to `RunRequest` and forwards it to the service.
- `ak-py/src/agentkernel/core/service.py` updates `run(self, prompt, context=None)` to store context on the session and persist the session.


### Install Agent Kernel (editable) and RAG dependencies

```ps1
# From repo root:
cd ak-py
pip install -e .

# RAG + helpers
pip install faiss-cpu langchain langchain-community langchain-huggingface sentence-transformers requests
```

## Start the Server (REST + RAG)

```ps1
# From repo root:
cd examples/cli/openai
$env:PYTHONPATH = (Get-Location).Path
$env:OPENAI_API_KEY = "sk-..."

python .\run_server_rag.py
```

## Sample Run ( outputs)

1. Health check  
   ```ps1
   curl http://localhost:8000/health
   ```
   ```
   {"status":"ok"}
   ```

2. List agents  
   ```ps1
   curl http://localhost:8000/agents
   ```
   ```
   {"agents":["triage","analyst","summarizer","general"]}
   ```

3. RAG search (local files)  
   ```ps1
   curl "http://localhost:8000/rag/search?q=colombo"
   ```
   ```
   {"query":"colombo","results":[{"snippet":"This initiative aims to position Moratuwa as a center for \"Industry 4.0\" innovation, focusing on developing AI-driven solutions ...","source":"E:\\OneDrive - University of Moratuwa\\Vidmal\\github\\agent-kernel\\examples\\cli\\openai\\local_data\\local_news_2.txt"}, ... ]}
   ```

4. RAG plus agent (answer and sources, with context)  
   ```ps1
   $body = @{
       question = "Top local headlines?"
       agent    = "general"
       top_k    = 5
       context  = @{ region="LK"; city="Colombo" }
   } | ConvertTo-Json
   Invoke-RestMethod -Method POST -Uri "http://localhost:8000/rag/ask" -ContentType "application/json" -Body $body
   ```
   ```
   question   : Top local headlines?
   agent      : general
   answer     : Top local headlines include the announcement of the "Coastal Link" bridge, ... [1].
                Another major story is the restoration of a historic building ... [2][4].
                Lastly, the local robotics team SeabsBots ... [3][5].
   session_id : 57dc7237-33ef-4ac5-a845-4a204e70a764
   sources    : @{snippet=Mayor Anura Perera hailed the decision, ...; source=...local_news_1.txt},
                @{snippet=The restoration project will be helmed by renowned architect Vihan Mathews, ...; source=...local_news_3.txt},
                @{snippet="The final round was incredibly tense," said 17-year-old team captain, ...; source=...local_news_4.txt},
                @{snippet=Dr. Elena Ranasinghe, a local historian ...; source=...local_news_3.txt}, ...
   ```

5. `/run` with context (API accepts context)  
   ```ps1
   $body = @{
       agent   = "general"
       prompt  = "Use this context: region=LK, city=Colombo. Answer in one short line: which city is preferred?"
       context = @{ region="LK"; city="Colombo" }
   } | ConvertTo-Json
   Invoke-RestMethod -Method POST -Uri "http://localhost:8000/run" -ContentType "application/json" -Body $body
   ```
   ```
   result                                                                      session_id
   ------                                                                      ----------
   Based on the context provided (LK, Colombo), the preferred city is Colombo. 1361403d-5275-447f-8909-04eee93c53b2
   ```

6. OpenAPI shows context in the schema  
   ```ps1
   curl http://localhost:8000/openapi.json
   ```
   Look for `RunRequest`; it now includes `context`, and the API title shows `AK + Local RAG`.

## Endpoints

- `GET /health` - Server alive check
- `GET /agents` - Loaded agents (triage, analyst, summarizer, general)
- `POST /run` - Run an agent (body supports `context`)
- `GET /rag/search?q=...` - RAG search over local `.txt` files
- `POST /rag/ask` - RAG plus agent summary; returns answer, session, and sources

Example `/run` request body:

```json
{ "prompt": "...", "agent": "general", "session_id": null, "context": { "key": "value" } }
```

## Notes

- Place `.txt` files in `examples/cli/openai/local_data/` and restart the server after changes.
- `local_agents.py` defines agents and handoffs suitable for local news flows (triage, analyst, summarizer, general).

### Minimal Server (AK REST only)

If you only need `/health`, `/agents`, and `/run`, start the lightweight server:

```ps1
python .\run_server.py
```

For the RAG demo, keep using `run_server_rag.py`.

## Troubleshooting

- `ModuleNotFoundError: rag_service` - Ensure you are inside `examples/cli/openai`, set `PYTHONPATH`, and confirm `rag_service.py` exists.
- `404` on `/rag/ask` - Likely running `run_server.py` instead of `run_server_rag.py`.
- Embedding model download on first run is expected; it caches under the default Hugging Face directories.
- No RAG results - Confirm filenames end with `.txt`, the content is UTF-8, and search for a known keyword.
