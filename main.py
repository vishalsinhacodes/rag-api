import asyncio

from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.responses import StreamingResponse

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
async def health():
    return {
        "status": "ok"
    }
    
@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    answer, sources, session_id = await asyncio.to_thread(
        rag.ask,
        request.question,
        request.session_id
    ) # type: ignore
    
    return AskResponse(
        answer=answer,
        sources=sources,
        session_id=session_id
    )

@app.post("/ask/stream")
async def ask_stream(request: AskRequest):
    return StreamingResponse(
        rag.ask_stream(request.question),
        media_type="text/plain"
    )

@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    count = await asyncio.to_thread(rag.ingest_documents, request.documents)
    return IngestResponse(
        ingested=count,
        message=f"Successfully ingested {count} docuements"
    )