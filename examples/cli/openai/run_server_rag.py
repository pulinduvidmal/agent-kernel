import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn
import requests

import local_agents   
from agentkernel.api.agent import AgentRESTRequestHandler

from rag_service import RAGService
rag = RAGService(data_directory="local_data")

app = FastAPI(title="AK + Local RAG")
app.include_router(AgentRESTRequestHandler.get_router())


@app.get("/rag/search")
def rag_search(q: str = Query(..., description="search query"), top_k: int = 5):
    return {"query": q, "results": rag.query(q)[:top_k]}

# RAG + agent summarize endpoint 
class AskBody(BaseModel):
    question: str
    agent: str | None = "general"
    top_k: int = 5

@app.post("/rag/ask")
def rag_ask(body: AskBody):
    # search local data
    hits = rag.query(body.question)[: body.top_k]
    # build context for the agent
    if hits:
        lines = [f"[{i+1}] {h['snippet']} (source: {h['source']})" for i, h in enumerate(hits)]
        context_text = "\n".join(lines)
    else:
        context_text = "No local matches."

    prompt = (
        "Use the local snippets below to answer the user's question in 3-5 sentences. "
        "Answer ONLY from these snippets; if not found, say you couldn't find it locally. "
        "Cite sources as [1], [2], etc.\n\n"
        f"USER QUESTION: {body.question}\n\n"
        f"SNIPPETS:\n{context_text}"
    )

  
    resp = requests.post(
        "http://localhost:8000/run",
        json={"agent": body.agent, "prompt": prompt},
        timeout=60,
    )
    resp.raise_for_status()
    out = resp.json()

    return {
        "question": body.question,
        "agent": body.agent,
        "answer": out.get("result"),
        "session_id": out.get("session_id"),
        "sources": hits,
    }

if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8000)
