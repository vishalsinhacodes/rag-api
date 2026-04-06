from fastapi import FastAPI
from contextlib import asynccontextmanager

from models import AskRequest, AskResponse, IngestRequest, IngestResponse

import rag

@asynccontextmanager
async def lifespan(app: FastAPI):
    rag.ingest()
    print("Documents ingested.")
    yield
    
app = FastAPI(
    title="RAG API",
    description="A Retrieval Augmented Generation API built with FastAPI, ChromaDB, and Groq.",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
def health():
    return {
        "status": "ok"
    }
    
@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    answer, sources = rag.ask(request.question) # type: ignore
    return AskResponse(answer=answer, sources=sources)

@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):
    count = rag.ingest_documents(request.documents)
    return IngestResponse(
        ingested=count,
        message=f"Successfully ingested {count} docuements"
    )